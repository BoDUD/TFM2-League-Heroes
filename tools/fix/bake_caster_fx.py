#!/usr/bin/env python3
"""Move a hero's caster pictures with a front and a back into his own frames.

    python tools/fix/bake_caster_fx.py --hero riven [--name league_riven_q1_front ...] [--dry]
    python tools/art/import_native.py --hero riven

The client never mirrors a data effect picture (champion-data.md section 6: ViewEffect and CasterViewEffect are drawn
as stored whichever way the hero faces), but it mirrors the hero's own frames. This finds every CasterViewEffect
playing one of the pictures (by default the ones lint_mod.py flags: mirrored, more than half the opaque pixels land on
empty ones), works out when it plays - ticks from the action's start: start_timing + 1, the Delayed ticks over it, a
lob's travel_time and a penetrating LinearProjectile's flight to its range for their end_effects - and which animation
is on the hero then: the action's own, or the last CasterAnimation before it in the same effect list (or a Combine or
a Switch in it: a Switch whose branches start different ones, league_aatrox Q's skill_r in his R and skill out of it,
is followed down the branch the play is in, or the play is split the same way). Then:
- a play under no condition its animation was not started under (the same Switch fields and branch count as the same
  condition), in a tag started in one place only: the picture is drawn into that tag at that time
  (assets/source/native/<hero>_bake.json "into", "at_ms") and the CasterViewEffect goes - nothing the game runs changes;
- any other play: the CasterViewEffect becomes a CasterAnimation of a copy of the animation on him then, from that
  moment on, with the picture drawn in ("from", "slice_ms", "length_ms"), ending where that animation would have (a
  CasterAnimation keeps the unit from walking: never longer than the one it replaces, or than the action for its own
  animation) - so only that play shows it. Starting an animation still nudges the simulated AI by a tick now and then
  (league_aatrox Q2's slash, 2026-10-06), which is why the first way is taken whenever it fits;
- a play the hero's frames cannot carry (on a projectile's hit or flight, in an AddCasted / buff, after the animation
  ended, with no known animation, its picture running more than SPILL ms past the animation unless --cut names it) is
  left and listed - unless a CasterAnimation was started in the same callback
  before it (league_sivir's catch: the time from it is known). tools/fix/mirror_union_fx.py makes those symmetric.
A CasterAnimation held longer than its tag loops it (league_garen's spin), and so does the copy.
A picture with no play left loses its view_effects entry. --dry only lists. Then run import_native.py for the frames.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import lint_mod as L  # noqa: E402
import tfm2_ase  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
SLOTS = ("attack", "skill", "skill2", "ult")
LOB = "ParabolicProjectile"
FLIGHT = {"LinearProjectile", "TargetProjectile", "RangeProjectile", "RangePeriodProjectile", "ApplyInProjectile",
          "LineRangeProjectile", "BounceProjectile", "ReturnProjectile"}
LATER = {"AddCasted", "Periodic", "AddBuff", "AddCasterBuff", "AddBuffToCaster"}
SPILL = 150             # ms a picture may run past the animation it is drawn into (cut there)


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def ms(ticks):
    return int(round(ticks * 1000 / 60))


def ticks(ms_):
    return int(round(ms_ * 60 / 1000))


def fields_of(node):
    return json.dumps({a: b for a, b in node.items() if not isinstance(b, (dict, list))}, sort_keys=True)


class Tag:
    """An animation on the hero: tag name, held ticks (None: the action's own), start tick, the conditions it was
    started under, the callback region it was started in."""
    def __init__(self, name, held, start, conds, region):
        self.name, self.held, self.start, self.conds, self.region = name, held, start, conds, region


class Split:
    """A Switch whose branches leave different animations on him: its fields and {branch key: Tag or Split}."""
    def __init__(self, fields, branches):
        self.fields, self.branches = fields, branches


def set_anim(node, cur, ctx):
    """The animation a node leaves on the hero at once, given `cur` before it, or None if it starts none."""
    if not isinstance(node, dict):
        return None
    t = node.get("type")
    if t == "CasterAnimation":
        return Tag(node["name"], node.get("tick"), ctx["t"], ctx["conds"], ctx["why"])
    if t == "Combine":
        found = None
        for e in node.get("effects", []):
            found = set_anim(e, found or cur, ctx) or found
        return found
    if t and (t.startswith("Switch") or t.startswith("Random")):
        f = fields_of(node)
        keys = [k for k, v in node.items() if isinstance(v, (dict, list))]
        got = {k: set_anim(node[k], cur, dict(ctx, conds=ctx["conds"] | {(f, k)})) for k in keys}
        if not any(got.values()):
            return None
        return Split(f, {k: got[k] or cur for k in keys})
    return None


def resolve(spec, branches):
    """A Split narrowed by the branches the play is in."""
    while isinstance(spec, Split) and spec.fields in branches:
        spec = spec.branches.get(branches[spec.fields])
    return spec


def plays(kit, names):
    """Every CasterViewEffect of `names`: dict(node, holder, key, name, slot, t, anim, conds, why, branches)."""
    out = []

    def walk(node, holder, key, ctx):
        if isinstance(node, list):
            # everything in a list happens in the same tick: an animation started anywhere in it is the one on him
            # (league_garen's E pulses play the picture, then start the spin again)
            anim, last = ctx["anim"], -1
            for i, v in enumerate(node):
                a = set_anim(v, anim, ctx)
                if a is not None:
                    anim, last = a, i
                if isinstance(v, dict) and v.get("type") == "RemoveCasterAnimation" and isinstance(anim, Tag) and \
                        v.get("name") == anim.name:
                    anim = None
            for i, v in enumerate(node):
                walk(v, node, i, dict(ctx, anim=anim, last=last))
            return
        if not isinstance(node, dict):
            return
        t = node.get("type")
        if t == "CasterViewEffect" and node.get("name") in names:
            out.append(dict(node=node, holder=holder, key=key, name=node["name"], slot=ctx["slot"], t=ctx["t"],
                            anim=ctx["anim"], conds=ctx["conds"], why=ctx["why"], branches=ctx["branches"],
                            last=ctx.get("last", -1)))
        for k, v in node.items():
            if not isinstance(v, (dict, list)) or k == "buff_state":
                continue
            c = dict(ctx, last=-1)          # `last` is an index in the list holding this node, not in its own
            if t == "Delayed" and k == "effects":
                c["t"] = ctx["t"] + node.get("tick", 0)
            elif t and (t.startswith("Switch") or t.startswith("Random")):
                f = fields_of(node)
                c["conds"] = ctx["conds"] | {(f, k)}
                c["branches"] = dict(ctx["branches"], **{f: k})
            elif t == LOB and k == "end_effects":
                c["t"] = ctx["t"] + node.get("travel_time", 0)
            elif t == "LinearProjectile" and node.get("penetrate") and k == "end_effects" and node.get("speed"):
                # nothing stops it before its range (league_aatrox Q's hidden tips)
                c["t"] = ctx["t"] + max(0, -(-node.get("range", 0) // node["speed"]) - 1)
            elif t == LOB or t in FLIGHT or k in ("end_effects", "applied_effects"):
                c["why"] = ctx["why"] or (f"on a {t}'s {k}", id(node))
            elif t in LATER:
                c["why"] = ctx["why"] or (f"in a {t}", id(node))
            walk(v, node, k, c)

    for slot in SLOTS:
        a = kit.get(slot)
        if not isinstance(a, dict) or "effect" not in a:
            continue
        tag = a.get("action_name", slot)
        walk(a["effect"], a, "effect", dict(slot=slot, t=a.get("start_timing", 0) + 1, branches={},
                                            anim=Tag(tag, None, 0, frozenset(), None), conds=frozenset(),
                                            why=None))
    return out


def dump(cfg):
    """The bake table, one item a line."""
    items = ",\n".join("    " + json.dumps(i, ensure_ascii=False) for i in cfg["items"])
    return f'{{\n  "fx": {json.dumps(cfg["fx"])},\n  "items": [\n{items}\n  ]\n}}\n'


def anim_starts(kit):
    """{tag: number of places that start it}: CasterAnimation nodes and actions."""
    found = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "CasterAnimation":
                found[o.get("name")] = found.get(o.get("name"), 0) + 1
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for k, v in kit.items():
        if not k.startswith("view_"):
            walk(v)
    for s in SLOTS:
        if isinstance(kit.get(s), dict):
            n = kit[s].get("action_name", s)
            found[n] = found.get(n, 0) + 1
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--name", action="append", help="pictures to move (default: the ones lint_mod.py flags)")
    ap.add_argument("--cut", action="append", default=[],
                    help="a picture drawn in even where it runs past the animation, cut there (a dash trail)")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    hero = args.hero
    kit_path = os.path.join(MOD, "champion", f"league_{hero}.data_champion")
    raw = open(lp(kit_path), "rb").read().decode("utf-8")
    kit = json.loads(raw)
    views = {v["name"]: v for v in kit.get("view_effects", [])}
    if args.name:
        names = set(args.name)
    else:
        names = set()
        for n in L.caster_views({k: v for k, v in kit.items() if not k.startswith("view_")}):
            v = views.get(n)
            if not v:
                continue
            share = L.turned_off_share(os.path.join(MOD, v["anim"].split("asset/league/")[1]),
                                       [v[k] for k in ("tag", "loop_tag") if v.get(k)], mirror=True)
            if share is not None and share > 0.5:
                names.add(n)
    sp = tfm2_ase.load_sprite(os.path.join(MOD, "champions", f"league_{hero}#sheet.png"))
    lengths = {t["name"]: sum(sp.durations[t["frm"]:t["to"] + 1]) for t in sp.tags}
    bake_path = os.path.join(SRC, f"{hero}_bake.json")
    cfg = json.load(open(bake_path, encoding="utf-8")) if os.path.exists(bake_path) else {"items": []}
    starts = anim_starts(kit)
    made = {}                                         # (from, slice_ms, length_ms, fx tag, under) -> copy tag
    for it in cfg["items"]:
        if "from" in it:
            made[(it["from"], it["slice_ms"], it["length_ms"], it["tag"], it.get("under", False))] = it["into"]
            lengths[it["into"]] = it["length_ms"]

    fx_len = {}

    def fx_ms(sheet, tag):
        if (sheet, tag) not in fx_len:
            fsp = tfm2_ase.load_sprite(os.path.join(MOD, "effects", sheet + "#sheet.png"))
            fx_len[(sheet, tag)] = sum(fsp.durations[i] for i in fsp.tag_frames(tag))
        return fx_len[(sheet, tag)]

    def item_for(fx_tag, fx_sheet, under, **kw):
        item = dict(tag=fx_tag, **kw)
        if fx_sheet != cfg.get("fx"):
            item["fx"] = fx_sheet
        if under:
            item["under"] = True
        return item

    def build(spec, p, fx_tag, fx_sheet, under, duration):
        """(the node replacing the CasterViewEffect - None to drop it - , what was done)."""
        if isinstance(spec, Split):
            node = json.loads(spec.fields)
            said, drop = [], True
            for k, sub in spec.branches.items():
                if sub is None:
                    raise ValueError("no animation known on him in one branch")
                r, s_ = build(sub, p, fx_tag, fx_sheet, under, duration)
                node[k] = r or {"type": "Combine", "effects": []}
                drop = drop and r is None
                said.append(s_)
            return (None if drop else node), " / ".join(said)
        tag = spec.name
        if p["why"] != spec.region:
            raise ValueError(p["why"][0] if p["why"] else "the animation came from a callback")
        off = p["t"] - spec.start
        if tag not in lengths:
            raise ValueError(f"no tag {tag} in his sheet")
        # a copy must not hold him longer than he was held: a CasterAnimation keeps the unit from walking
        end = min(ticks(lengths[tag]), duration - spec.start) if spec.held is None else spec.held
        if off >= end:
            raise ValueError(f"after {tag} ended ({off} ticks in, {end} long)")
        over = fx_ms(fx_sheet, fx_tag) - ms(end - off)
        if over > SPILL and p["name"] not in args.cut:
            raise ValueError(f"the picture runs {over} ms past the end of {tag} (it played on while he walked)")
        if not (p["conds"] - spec.conds) and starts.get(tag, 0) == 1:
            kw = {}
            if spec.held is not None and ms(spec.held) > lengths[tag]:
                kw["length_ms"] = ms(spec.held)             # a held loop is drawn out to its whole hold first
            item = item_for(fx_tag, fx_sheet, under, into=tag, at_ms=ms(off), **kw)
            if item not in cfg["items"]:
                cfg["items"].append(item)
            return None, f"drawn into {tag} at {ms(off)} ms"
        key = (tag, ms(off), ms(end - off), fx_tag, under)
        new = made.get(key)
        if new is None:
            base = re.sub(r"_fx\d+$", "", tag)
            n = 1
            while f"{base}_fx{n}" in lengths:
                n += 1
            new = f"{base}_fx{n}"
            cfg["items"].append(item_for(fx_tag, fx_sheet, under, into=new, **{"from": tag}, slice_ms=ms(off),
                                         length_ms=ms(end - off), at_ms=0))
            made[key] = new
            lengths[new] = ms(end - off)
            starts[new] = 1
        return ({"type": "CasterAnimation", "name": new, "tick": end - off},
                f"{tag} from {ms(off)} ms played as {new} ({end - off} ticks)")

    left, moved = [], []
    while True:
        todo = [p for p in plays(kit, names) if id(p["node"]) not in {id(q["node"]) for q in left}]
        if not todo:
            break
        p = todo[0]
        v = views[p["name"]]
        fx_sheet = v["anim"].split("asset/league/effects/")[1]
        fx_tag = v.get("tag") or v.get("loop_tag")
        under = (v.get("z") or 0) < 0
        spec = resolve(p["anim"], p["branches"])
        try:
            if spec is None:
                raise ValueError(p["why"][0] if p["why"] else "no animation known on him then")
            repl, said = build(spec, p, fx_tag, fx_sheet, under, kit[p["slot"]]["duration"])
        except ValueError as e:
            left.append(dict(p, why=str(e)))
            continue
        moved.append(f"{p['name']}: {said}")
        h, k = p["holder"], p["key"]
        if isinstance(h, list) and repl is None:
            h.pop(k)
        elif isinstance(h, list) and p["last"] > k:
            h.insert(p["last"] + 1, repl)              # after the animation started later in the same tick
            h.pop(k)
        elif isinstance(h, list):
            h[k] = repl
        else:
            h[k] = repl or {"type": "Combine", "effects": []}
    # a copy is stopped wherever the tag it was copied from is (an interrupted spin, the end of a channel)
    copies = {}
    for it in cfg["items"]:
        if "from" in it:
            copies.setdefault(it["from"], []).append(it["into"])

    def stops(o):
        if isinstance(o, dict):
            for k, v in list(o.items()):
                if isinstance(v, dict) and v.get("type") == "RemoveCasterAnimation" and v.get("name") in copies:
                    o[k] = {"type": "Combine", "effects": [v]}
                stops(o[k])
        elif isinstance(o, list):
            i = 0
            while i < len(o):
                v = o[i]
                if isinstance(v, dict) and v.get("type") == "RemoveCasterAnimation" and v.get("name") in copies:
                    have = {x.get("name") for x in o if isinstance(x, dict) and x.get("type") == "RemoveCasterAnimation"}
                    todo = []
                    stack = [v["name"]]
                    while stack:
                        n = stack.pop()
                        for c in copies.get(n, []):
                            stack.append(c)
                            if c not in have:
                                todo.append({"type": "RemoveCasterAnimation", "name": c})
                    o[i + 1:i + 1] = todo
                    i += len(todo)
                else:
                    stops(v)
                i += 1
    stops({k: v for k, v in kit.items() if not k.startswith("view_")})
    if cfg.get("fx") is None:
        firsts = [i.get("fx") for i in cfg["items"] if i.get("fx")]
        cfg["fx"] = firsts[0] if firsts else f"league_{hero}_fx"
        for i in cfg["items"]:
            if i.get("fx") == cfg["fx"]:
                del i["fx"]
    body = {k: v for k, v in kit.items() if not k.startswith("view_")}
    still = L.caster_views(body)
    used_ve = set()

    def vwalk(o):
        if isinstance(o, dict):
            if o.get("type") == "ViewEffect" and o.get("name"):
                used_ve.add(o["name"])
            for x in o.values():
                vwalk(x)
        elif isinstance(o, list):
            for x in o:
                vwalk(x)
    vwalk(body)
    gone = sorted(n for n in names if n not in still and n not in used_ve)
    for line in moved:
        print("  " + line)
    for p in left:
        print(f"  LEFT {p['name']} ({p['slot']}, tick {p['t']}): {p['why']}")
    if args.dry:
        return
    kit["view_effects"] = [v for v in kit["view_effects"] if v["name"] not in gone]
    out = json.dumps(kit, ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(kit_path), "wb").write(out.encode("utf-8"))
    if cfg["items"]:
        with open(bake_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(dump(cfg))
    print(f"league_{hero}: {len(moved)} plays moved, {len(left)} left, {len(gone)} bindings removed")


if __name__ == "__main__":
    main()

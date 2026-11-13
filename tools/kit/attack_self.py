"""What an attack does to its own caster goes under a hidden projectile's hit, at packing (2026-11-13).

    python tools/kit/attack_self.py --check   # (CI) every champion file: the rewrite settles, undoes to the source,
                                              # survives slim.py; lists who is rewritten, kept and left, with why

Why. The game's AI (0.7.2) hardly ever orders an attack at a champion with a hero whose attack runs, when it is thrown,
an area effect on allies or on the caster himself - `RangeEffect` with target AllyOnlySelf / AllyChampion / AllyNotSelf,
the kits' "on me" (an automatic W or E, a count, the start of a kit's polling aura). league_ai_watch, the AI's own
attacks at champions per alive minute: marksmen 4.5-7, mages 2.3-3.3, and with such an attack Aurelion Sol 0.06 (168
games), Azir 0.07, Ahri 0.13, Draven 0.16, Swain 0.21 (357), Anivia 0.26, Kai'Sa 0.60, Sejuani 0.83 - they last-hit and
cast as usual. Three rounds in the game on 2026-11-13:
  1. Draven's automatic W moved from the attack's top Combine under his hidden twin projectile's hit: 0.16 -> 6.5.
  2. league.dll's `league:range` node added to 62 such attacks (the 7 heroes with both looked normal): nothing
     (Aurelion Sol 0.03, Azir 0.06, Ahri 0.10, Swain 0.13) - a coincidence, taken out again.
  3. the attack's top-level effect that holds the area wrapped, in place, in a hidden homing projectile at the attack's
     target, on seven heroes of different shapes: Kai'Sa 0.60 -> 5.51 (91 games), Azir 0.07 -> 1.91 (66), Sejuani 0.83
     -> 2.36 (11), Ahri 0.13 -> 2.61 (5), Anivia 0.26 -> 1.60 (3), Aurelion Sol 0.06 -> 1.08 (1); untouched heroes of
     the same pattern stayed where they were (Orianna 0.18 in 64 games, Xin Zhao 0.95 in 77), casts per minute too.
What the engine reads from the area was not found: the AI's own decision trace gives these attacks the right reach,
damage, picks and fight verdicts (docs/native_ai.md). Eleven heroes with such an area were never neglected.

What. `settle()` is round 3 for every league_ champion it is safe for; the packers (tools/package_mod.py,
addons/league_addons/assemble.py) pass every champion through it after slim.py, so the installed file has the wrap and
the repository's files and their 129 generators stay as they are. From the attack's effect down: an effect that holds
such an area at cast time and none of the attack's own damage becomes

    {"type": "TargetProjectile", "name": "<id>_a_self", "speed": 60000, "y_offset": <the attack's own bolt's>,
     "applied_target": "Enemy", "applied_effects": [{"casting_type": "Targeting", "effect": <that effect, unchanged>}]}

(no view of that name: it is not drawn; it lands a tick later); an effect that holds both is entered when it keeps an
enemy as the context's target (Combine, SwitchByBuff, Delayed, RandomTarget / RangeEffect on enemies). A hero is LEFT
as he is, and listed, when the move could change what his kit does:
  A  the block writes a buff in its own tick that another cast-time effect reads in that tick (after it) or within
     LATE ticks: that reader would not see it any more;
  B  the block reads in its own tick a buff that another cast-time effect writes then or within LATE ticks;
  C  an effect that holds both the area and the attack's damage does not hand its children an enemy;
  D  the attack's own damage can land before the hidden projectile does (a direct Attack at or before the block's
     tick, or a projectile fast or early enough: bodies are 20000 apart at the least) - a projectile at a dead target
     hits nothing, and the block would be lost on every killing blow.
KEEP lists the heroes measured as attacking normally with the area where it is: not touched.
The estimate stub of the generated attacks (AddCasterBuff x, SwitchByBuff x -> Attack, RemoveCasterBuff x) never runs
and is not counted as damage. Not done: tft_ champions (the watch does not measure them), skills.

The second carrier (2026-11-14), for a hero the first is not safe for: only the area itself - each cast-time
`RangeEffect` on allies / the caster, the outermost of nested ones - is replaced, in place, by

    {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": false, "effects": [
        {"type": "ParabolicProjectile", "name": "<id>_a_self", "travel_time": 1, "range": 400000,
         "shape": {"Circle": {"radius": 1000}}, "range_effect_name": "", "applied_target": "AllyOnlySelf",
         "applied_effects": [], "end_effects": [<the area, unchanged>]}]}

a hidden one-tick lob onto the caster himself (league_draven's q_drop and league_leesin's w_probe are such lobs). It
needs no enemy alive, so a killing blow loses nothing (league_tryndamere's fury on a kill sits in such an area), and
everything round the area - the buffs an automatic W writes and the rest of the attack reads in the same tick - stays
at the cast. Checked like the first on what the area itself writes and reads in its tick (A, B; a voice line's
cooldown flag `...vo_cd` is not counted), and not used when
  E  the area sits inside a cast-time AddCasted outside any area (a lob at every run of that aura);
  F  the area reads the projectile it is under (`from_projectile` at its own level);
  G  the area is not centred on the caster (`apply_type` other than AroundCaster: the lob lands on the caster).
HOLD lists heroes left as they are although no hazard is found, because the game showed something the classic engine
does not (league_kogmaw's death watch under the lob, 2026-11-14).
"""
import argparse
import copy
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slim  # noqa: E402  the packers run it first

DAMAGE = ("Attack", "ApAttack", "FixedAttack")
SPEED = 60000          # the hidden projectile: one tick over any attack range
LATE = 2               # ticks after its own tick by which the wrapped block has run
NEAR = 20000           # two bodies touching, centre to centre: the shortest flight of the attack's own projectile
# measured as attacking champions normally with the area at cast time (league_ai_watch, 2026-11-13): left alone
KEEP = {
    "league_belveth": "5.26 a minute in 119 games",
    "league_senna": "5.59 a minute in 10 games",
    # 2026-11-14, all launches together
    "league_zeri": "7.93 a minute in 125 games",
    "league_renekton": "5.15 a minute in 137 games",
    "league_wukong": "3.97 a minute in 137 games",
    "league_seraphine": "3.97 a minute in 135 games",
    "league_blitzcrank": "4.2 a minute in 51 games, a support",
}
# held out of both carriers although no hazard is found: what the move did to the kit in the game is not settled
HOLD = {
    # the first action of each life starts his death watch (Icathian Surprise) from the attack's "on me" area. With it
    # under the lob (installed 2026-11-14 01:18) the player saw no void form after his deaths: 「大嘴死了后的炸人怎么看不到了」.
    # The classic engine wakes the form on every death either way (the watch forced to start from the attack: lob 16
    # of 16, the area at the cast 21 of 21), and league.dll's draw log was spent before his second death in that
    # match - the cause is not found, so his attack stays as it was until the game shows which it is.
    "league_kogmaw": "the death watch: no void form seen in the game under the lob (2026-11-14), cause not found",
}


def name_of(champ_id):
    return f"{champ_id}_a_self"


def kids(e):
    """(key, index or None, child effect) for an effect's direct children; a projectile's `applied_effects` hold
    {"casting_type", "effect"} wrappers"""
    for k, v in e.items():
        if isinstance(v, dict) and "type" in v:
            yield k, None, v
        elif isinstance(v, list):
            for i, x in enumerate(v):
                if isinstance(x, dict) and "type" in x:
                    yield k, i, x
                elif isinstance(x, dict) and isinstance(x.get("effect"), dict):
                    yield k, i, x["effect"]


def nodes(e):
    yield e
    for _, _, c in kids(e):
        yield from nodes(c)


def is_proj(e):
    return str(e.get("type", "")).endswith("Projectile")


def is_area(e):
    return e.get("type") == "RangeEffect" and any(w in str(e.get("target", "")) for w in ("Ally", "Self"))


def area_at_cast(e):
    """an area on allies / the caster reached outside every projectile's hit"""
    if is_proj(e):
        return False
    return is_area(e) or any(area_at_cast(c) for _, _, c in kids(e))


def _stub(e):
    return e.get("type") == "SwitchByBuff" and str(e.get("buff_name", "")).endswith("_x")


def own_damage(e):
    """the attack's own damage reached at cast time: a damage effect, or a projectile whose hit holds one; not looked
    for inside an area on allies / the caster, an AddCasted (a kit's aura) or the estimate stub"""
    t = str(e.get("type", ""))
    if t in DAMAGE:
        return True
    if is_proj(e):
        return any(n.get("type") in DAMAGE for n in nodes(e))
    if is_area(e) or t == "AddCasted":
        return False
    if _stub(e):
        return any(own_damage(c) for k, _, c in kids(e) if k != "effect_none")
    return any(own_damage(c) for _, _, c in kids(e))


def enemy_context(e):
    t = e.get("type")
    if t in ("Combine", "SwitchByBuff", "Delayed"):
        return True
    if t == "RandomTarget":
        return "Enemy" in str(e.get("casting_target", ""))
    if t == "RangeEffect":
        return "Enemy" in str(e.get("target", ""))
    return False


def plan(e, blocks, bad, path=()):
    """e holds an area at cast time: the effects to wrap (`blocks`), or why not (`bad`)"""
    if not own_damage(e):
        blocks.append(e)
        return
    if not enemy_context(e):
        bad.append(f"C  {' > '.join(path) or 'top'}: {e.get('type')}[{e.get('casting_target') or e.get('target') or ''}] "
                   "holds the area and the attack's damage")
        return
    for k, i, c in kids(e):
        if area_at_cast(c):
            plan(c, blocks, bad, path + (f"{e.get('type')}.{k}" + (f"[{i}]" if i is not None else ""),))


def timeline(e, tick, acc, stubbed=False):
    """(effect, tick it runs at after the release or None for later / under a hit, order, inside the stub)"""
    acc.append((e, tick, len(acc), stubbed))
    for k, _, c in kids(e):
        if is_proj(e) or e.get("type") == "AddCasted":
            timeline(c, None, acc, stubbed)
        elif e.get("type") == "Delayed":
            timeline(c, None if tick is None else tick + int(e.get("tick", 0) or 0), acc, stubbed)
        else:
            timeline(c, tick, acc, stubbed or (_stub(e) and k == "effect_none"))


def _own_tick(blk):
    out = []

    def go(e):
        out.append(e)
        if e.get("type") in ("Delayed", "AddCasted") or is_proj(e):
            return
        for _, _, c in kids(e):
            go(c)
    go(blk)
    return out


def _writes(n):
    if n.get("type") in ("AddCasterBuff", "AddBuff"):
        return (n.get("buff_state") or {}).get("name")
    if n.get("type") in ("RemoveCasterBuff", "RemoveBuff"):
        return n.get("name")
    return None


def _hits_hard(n):
    return any(m.get("type") in DAMAGE and any((m.get("damage"), m.get("attack_ratio"), m.get("ap_ratio"))) for m in nodes(n))


def hazards(champ, eff, blocks):
    """the reasons (A, B, D of the module's text) not to wrap these blocks of this attack"""
    cid = champ.get("id", "")
    short = lambda s: str(s).replace(cid + "_", "")
    tl = []
    timeline(eff, 0, tl)
    info = {id(n): (tick, k) for n, tick, k, _ in tl}
    notes = set()
    for blk in blocks:
        bt, bk = info[id(blk)]
        if bt is None:
            notes.add("?  a block without a tick")
            continue
        inside = {id(n) for n in nodes(blk)}
        mine = _own_tick(blk)
        w = {_writes(n) for n in mine} - {None}
        r = {n.get("buff_name") for n in mine if n.get("type") == "SwitchByBuff"} - {None}
        for n, tick, k, stubbed in tl:
            if id(n) in inside or tick is None:
                continue
            near = (tick == bt and k > bk) or (bt < tick <= bt + LATE)
            if near and n.get("type") == "SwitchByBuff" and n.get("buff_name") in w:
                notes.add(f"A  {short(n['buff_name'])} written by the block at tick {bt} is read at tick {tick}")
            if near and _writes(n) in r:
                notes.add(f"B  {short(_writes(n))} read by the block at tick {bt} is written at tick {tick}")
            before = tick < bt or (tick == bt and k < bk)
            if before and not stubbed and n.get("type") in DAMAGE and any((n.get("damage"), n.get("attack_ratio"), n.get("ap_ratio"))):
                notes.add(f"D  a direct {n.get('type')} at tick {tick} before the block at tick {bt}")
            if is_proj(n) and "Enemy" in str(n.get("applied_target", "")) and n.get("speed") and _hits_hard(n):
                lands = tick + -(-NEAR // int(n["speed"]))
                if lands <= bt + 1:
                    notes.add(f"D  {short(n.get('name'))} (speed {n['speed']}, tick {tick}) can land at tick {lands}, "
                              f"the hidden projectile at {bt + 1}")
    return sorted(notes)


def areas(e, out, bad, casted=False):
    """the outermost cast-time areas on allies / the caster (the second carrier's blocks); E of the module's text"""
    if is_proj(e):
        return
    if is_area(e):
        if casted:
            bad.append("E  an area inside a cast-time AddCasted")
        out.append(e)
        return
    for _, _, c in kids(e):
        areas(c, out, bad, casted or e.get("type") == "AddCasted")


def _cosmetic(name):
    return str(name).endswith("vo_cd")      # a voice line's cooldown: two lines in one tick at the worst


def lob_hazards(champ, eff, blocks):
    """the reasons (A, B, F, G of the module's text) not to put these areas under a lob onto the caster"""
    cid = champ.get("id", "")
    short = lambda s: str(s).replace(cid + "_", "")
    tl = []
    timeline(eff, 0, tl)
    info = {id(n): (tick, k) for n, tick, k, _ in tl}
    notes = set()
    for blk in blocks:
        bt, bk = info[id(blk)]
        if bt is None:
            notes.add("?  an area without a tick")
            continue
        if blk.get("apply_type") != "AroundCaster":
            notes.add(f"G  an area with apply_type {blk.get('apply_type')}")
        inside = {id(n) for n in nodes(blk)}
        mine = _own_tick(blk)
        if any(n.get("from_projectile") is True for n in mine):
            notes.add("F  from_projectile at the area's own level")
        w = {_writes(n) for n in mine} - {None}
        r = {n.get("buff_name") for n in mine if n.get("type") == "SwitchByBuff"} - {None}
        for n, tick, k, _ in tl:
            if id(n) in inside or tick is None:
                continue
            near = (tick == bt and k > bk) or (bt < tick <= bt + LATE)
            if near and n.get("type") == "SwitchByBuff" and n.get("buff_name") in w and not _cosmetic(n["buff_name"]):
                notes.add(f"A  {short(n['buff_name'])} written by the area at tick {bt} is read at tick {tick}")
            if near and _writes(n) in r and not _cosmetic(_writes(n)):
                notes.add(f"B  {short(_writes(n))} read by the area at tick {bt} is written at tick {tick}")
    return sorted(notes)


def verdict(champ):
    """("wrap", blocks) | ("lob", areas) | ("keep", why) | ("left", [reasons]) | ("none", None) for a champion as
    slim.py leaves it: the first carrier where it is safe, else the second, else nothing"""
    cid = str(champ.get("id", ""))
    attack = champ.get("attack")
    eff = attack.get("effect") if isinstance(attack, dict) else None
    if not cid.startswith("league_") or not isinstance(eff, dict) or not area_at_cast(eff):
        return "none", None
    if cid in KEEP:
        return "keep", KEEP[cid]
    if cid in HOLD:
        return "left", ["held: " + HOLD[cid]]
    blocks, bad = [], []
    plan(eff, blocks, bad)
    why = bad + hazards(champ, eff, blocks)
    if blocks and not why:
        return "wrap", blocks
    found, bad2 = [], []
    areas(eff, found, bad2)
    why2 = bad2 + lob_hazards(champ, eff, found)
    if found and not why2:
        return "lob", found
    return "left", (why or ["nothing to wrap"]) + ["and the lob: " + w for w in (why2 or ["no area found"])]


def _own_bolt(eff, blocks):
    """the attack's own homing projectile at enemies (with an Attack in its hit), outside the blocks: its fields are
    the hidden projectile's (y_offset)"""
    skip = {id(b) for b in blocks}

    def go(e):
        if id(e) in skip:
            return None
        if e.get("type") == "TargetProjectile" and e.get("applied_target") == "Enemy" and any(
                n.get("type") == "Attack" for n in nodes(e) if n is not e):
            return e
        if is_proj(e):
            return None
        for _, _, c in kids(e):
            hit = go(c)
            if hit is not None:
                return hit
        return None
    return go(eff)


def _carrier(cid, block, like):
    c = {k: copy.deepcopy(v) for k, v in like.items() if k != "applied_effects"} if like else {"type": "TargetProjectile"}
    c["name"] = name_of(cid)
    c["speed"] = SPEED
    c.setdefault("y_offset", 0)
    c["applied_target"] = "Enemy"
    c["applied_effects"] = [{"casting_type": "Targeting", "effect": block}]
    return c


def _replace(e, table):
    """a copy of the tree with the effects in `table` (id -> replacement) swapped; everything else shared"""
    if id(e) in table:
        return table[id(e)]
    out, changed = {}, False
    for k, v in e.items():
        if isinstance(v, dict) and "type" in v:
            nv = _replace(v, table)
        elif isinstance(v, list):
            nv = []
            for x in v:
                if isinstance(x, dict) and "type" in x:
                    nv.append(_replace(x, table))
                elif isinstance(x, dict) and isinstance(x.get("effect"), dict):
                    ne = _replace(x["effect"], table)
                    nv.append(x if ne is x["effect"] else dict(x, effect=ne))
                else:
                    nv.append(x)
            if all(a is b for a, b in zip(nv, v)):
                nv = v
        else:
            nv = v
        changed = changed or nv is not v
        out[k] = nv
    return out if changed else e


def _lob(cid, area):
    """the second carrier: a one-tick hidden lob onto the caster himself, the area in its end effects"""
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False, "effects": [
        {"type": "ParabolicProjectile", "name": name_of(cid), "travel_time": 1, "range": 400000,
         "shape": {"Circle": {"radius": 1000}}, "range_effect_name": "", "applied_target": "AllyOnlySelf",
         "applied_effects": [], "end_effects": [area]}]}


def _is_lob(e, name):
    """a RandomTarget made by `_lob` for this champion"""
    if e.get("type") != "RandomTarget" or e.get("casting_target") != "AllyOnlySelf" or len(e.get("effects") or []) != 1:
        return False
    p = e["effects"][0]
    return (isinstance(p, dict) and p.get("type") == "ParabolicProjectile" and p.get("name") == name
            and not p.get("applied_effects") and len(p.get("end_effects") or []) == 1)


def settle(champ):
    """What the packers ship: the champion itself, or a copy whose attack has its blocks under hidden projectiles."""
    kind, blocks = verdict(champ)
    if kind not in ("wrap", "lob"):
        return champ
    cid, eff = champ["id"], champ["attack"]["effect"]
    if kind == "wrap":
        like = _own_bolt(eff, blocks)
        table = {id(b): _carrier(cid, b, like) for b in blocks}
    else:
        table = {id(b): _lob(cid, b) for b in blocks}
    return dict(champ, attack=dict(champ["attack"], effect=_replace(eff, table)))


def unwrap(champ):
    """`settle` undone: every hidden projectile (and a lob's pick of the caster) replaced by the effect it carries."""
    attack = champ.get("attack")
    if not isinstance(attack, dict) or not isinstance(attack.get("effect"), dict):
        return champ
    name = name_of(str(champ.get("id", "")))
    table = {}
    for n in nodes(attack["effect"]):
        if _is_lob(n, name):
            table[id(n)] = n["effects"][0]["end_effects"][0]
        elif n.get("type") == "TargetProjectile" and n.get("name") == name:
            table[id(n)] = n["applied_effects"][0]["effect"]
    if not table:
        return champ
    return dict(champ, attack=dict(attack, effect=_replace(attack["effect"], table)))


def load(path):
    return json.loads(open(path, "rb").read().decode("utf-8-sig"))


def check():
    # the main pack's files first: an add-on's copy of the same champion is the one installed, and comes after
    files = (sorted(glob.glob(os.path.join(ROOT, "league", "champion", "*.data_champion"))) +
             sorted(glob.glob(os.path.join(ROOT, "addons", "*", "override", "*.data_champion"))))
    bad, final = [], {}
    for path in files:
        rel = os.path.relpath(path, ROOT)
        src = slim.slim_champion(load(path))
        kind, what = verdict(src)
        out = settle(src)
        final[os.path.basename(path)] = (src.get("id"), kind, what)      # an add-on's copy comes after the main pack's
        if kind in ("wrap", "lob"):
            if out is src or unwrap(out) != src:
                bad.append(f"{rel}: the wrap does not undo to the source")
            if area_at_cast(out["attack"]["effect"]):
                bad.append(f"{rel}: an area is still at cast time after the wrap")
            if settle(out) is not out or slim.slim_champion(out) != out:
                bad.append(f"{rel}: the wrapped copy does not settle (settle / slim.py change it again)")
            if any(v.get("name") == name_of(src["id"]) for v in src.get("view_projectiles", [])):
                bad.append(f"{rel}: a view is bound to {name_of(src['id'])} - the hidden projectile would be drawn")
            if {k: v for k, v in out.items() if k != "attack"} != {k: v for k, v in src.items() if k != "attack"}:
                bad.append(f"{rel}: more than the attack changed")
        elif out is not src:
            bad.append(f"{rel}: changed although its verdict is {kind}")
    return bad, final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.check:
        ap.error("--check")
    bad, final = check()
    for b in bad:
        print(b)
    if bad:
        sys.exit(f"{len(bad)} problem(s)")
    short = lambda i: str(i)[len("league_"):]
    wrap = sorted(short(i) for i, k, _ in final.values() if k == "wrap")
    lob = sorted(short(i) for i, k, _ in final.values() if k == "lob")
    keep = sorted(f"{short(i)} ({w})" for i, k, w in final.values() if k == "keep")
    left = sorted((short(i), w) for i, k, w in final.values() if k == "left")
    print(f"attack_self: {len(wrap)} attacks get their caster's block under a hidden projectile at packing: " + ", ".join(wrap))
    print(f"and {len(lob)} get each area on the caster under a one-tick lob onto himself: " + ", ".join(lob))
    print(f"kept as they are ({len(keep)}, measured normal): " + ", ".join(keep))
    print(f"left as they are ({len(left)}, the move could change the kit):")
    for i, why in left:
        print(f"  {i}: " + "; ".join(w[:110] for w in why[:3]) + (f"; ... {len(why) - 3} more" if len(why) > 3 else ""))


if __name__ == "__main__":
    main()

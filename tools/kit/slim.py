#!/usr/bin/env python3
"""Exact rewrites of TFM2 effect trees: fewer nodes, the same game.

While a match is on screen the game copies every data champion's `skill` and `skill2` trees each tick
(docs/perf.md, "skill and skill2 are copied every tick"), so their node count is CPU. These rewrites keep what
runs, in what order and in which context, for every buff state - the play, the pictures and sounds, and the
branch the AI reads - and drop only the wrappers around it:

  flatten  a Combine inside an effect list -> its effects in its place (an empty one goes; so does an empty Delayed);
           in the lists of WithSelf and RangeEffect, which run for several units, only a Combine of one effect
  unwrap   a Combine of one effect where one effect is expected -> that effect
  same     SwitchByBuff / SwitchByLevel3 with two equal branches -> that branch (the check has no side effect)
  suffix   SwitchByBuff(b, [A.., S..], [B.., S..]) -> [SwitchByBuff(b, A, B), S..]
  prefix   SwitchByBuff(b, [P.., A..], [P.., B..]) -> [P.., SwitchByBuff(b, A, B)] when nothing in P adds or
           takes the buff b (so b reads the same after P as before)

An effect list here is one whose effects run one after the other in the same context (Combine, Delayed, WithSelf,
RandomTarget, RangeEffect, AddCasted, and the end_effects of dashes and of linear / lobbed / returning
projectiles); the applied effects of projectiles and a RangePeriodProjectile's end_effects are wrapped one by one
and are only rewritten inside.

tools/package_mod.py and addons/league_addons/assemble.py run it on every .data_champion they pack, so the
sources stay as their builders write them. Hero-specific rewrites that need a fact about the kit (a flag that is
never on in some state) live in the hero's own builder.

    python tools/kit/slim.py <file.data_champion> ...       # node counts per slot, before -> after
    python tools/kit/slim.py --all [--repo <repo>]          # every hero of league/ and the add-ons' copies
"""
import argparse
import glob
import json
import os

SEQ = {
    "Combine": ("effects",),
    "Delayed": ("effects",),
    "WithSelf": ("effects",),
    "RandomTarget": ("effects",),
    "RangeEffect": ("effects",),
    "AddCasted": ("effects",),
    "MoveTo": ("end_effects",),
    "MoveToTarget": ("end_effects",),
    "LinearProjectile": ("end_effects",),
    "ParabolicProjectile": ("end_effects",),
    "BackToCasterLinearProjectile": ("end_effects",),
}
# lists run for several units (WithSelf: the caster, then the action's target; RangeEffect: every unit in the shape):
# a Combine of two or more effects there stays whole - whether the engine runs the list unit by unit or effect by
# effect, it then runs the same way as before
MULTI = {"WithSelf", "RangeEffect"}
BRANCHES = {"SwitchByBuff": ("effect_buff", "effect_none"), "SwitchByLevel3": ("effect_start", "effect_level3")}
SLOTS = ("attack", "skill", "skill2", "ult")


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def count(x):
    """Effect nodes: dicts with a "type"."""
    if isinstance(x, dict):
        return (1 if "type" in x else 0) + sum(count(v) for v in x.values())
    if isinstance(x, list):
        return sum(count(v) for v in x)
    return 0


def _key(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)


def _buffs(x, acc):
    """Every buff name an effect adds or takes, anywhere inside it."""
    if isinstance(x, dict):
        if x.get("type") == "RemoveCasterBuff":
            acc.add(x.get("name"))
        state = x.get("buff_state")
        if isinstance(state, dict):
            acc.add(state.get("name"))
        for v in x.values():
            _buffs(v, acc)
    elif isinstance(x, list):
        for v in x:
            _buffs(v, acc)
    return acc


def _is_bare_combine(e):
    return isinstance(e, dict) and e.get("type") == "Combine" and set(e) == {"type", "effects"}


def _as_list(e):
    return list(e["effects"]) if _is_bare_combine(e) else [e]


def _from_list(items):
    if len(items) == 1:
        return items[0]
    return {"type": "Combine", "effects": items}


def _flat(items, multi=False):
    out = []
    for it in items:
        if _is_bare_combine(it) and (not multi or len(it["effects"]) <= 1):
            out.extend(_flat(it["effects"], multi))
        elif isinstance(it, dict) and it.get("type") == "Delayed" and not it.get("effects"):
            continue
        else:
            out.append(it)
    return out


def _one(e):
    """An effect slot that holds one effect: a bare Combine of one effect becomes that effect."""
    while _is_bare_combine(e) and len(e["effects"]) == 1:
        e = e["effects"][0]
    return e


def _rewrite(e):
    if isinstance(e, list):
        return [_rewrite(x) for x in e]
    if not isinstance(e, dict):
        return e
    e = {k: _rewrite(v) for k, v in e.items()}
    t = e.get("type")
    for k in SEQ.get(t, ()):
        if isinstance(e.get(k), list):
            e[k] = _flat(e[k], t in MULTI)
    if "type" not in e and isinstance(e.get("effect"), dict):        # an applied-effect wrapper
        e["effect"] = _one(e["effect"])
    if t in BRANCHES:
        yes, no = BRANCHES[t]
        e[yes], e[no] = _one(e[yes]), _one(e[no])
        if _key(e[yes]) == _key(e[no]):
            return e[yes]
    if t == "SwitchByBuff":
        a, b = _as_list(e["effect_buff"]), _as_list(e["effect_none"])
        s = 0
        while s < min(len(a), len(b)) and _key(a[-1 - s]) == _key(b[-1 - s]):
            s += 1
        p = 0
        while (p < min(len(a), len(b)) - s and _key(a[p]) == _key(b[p])
               and e["buff_name"] not in _buffs(a[p], set())):
            p += 1
        if s or p:
            inner = dict(e, effect_buff=_from_list(a[p:len(a) - s]), effect_none=_from_list(b[p:len(b) - s]))
            return {"type": "Combine", "effects": a[:p] + [inner] + a[len(a) - s:]}
    if _is_bare_combine(e) and len(e["effects"]) == 1:
        return e["effects"][0]
    return e


def slim_effect(effect):
    """The exact rewrites, repeated until nothing changes."""
    cur = effect
    while True:
        new = _rewrite(cur)
        if _key(new) == _key(cur):
            return new
        cur = new


def slim_champion(data):
    """A copy of a .data_champion's dict with every action's effect tree rewritten."""
    out = dict(data)
    for slot in SLOTS:
        action = out.get(slot)
        if isinstance(action, dict) and isinstance(action.get("effect"), dict):
            out[slot] = dict(action, effect=slim_effect(action["effect"]))
    return out


def _load(path):
    with open(lp(path), encoding="utf-8-sig") as f:
        return json.load(f)


def report(path):
    data = _load(path)
    new = slim_champion(data)
    cells = []
    for slot in SLOTS:
        if isinstance(data.get(slot), dict):
            cells.append(f"{slot} {count(data[slot])} -> {count(new[slot])}")
    print(f"{os.path.basename(path)}: " + ", ".join(cells))
    return sum(count(data[s]) for s in ("skill", "skill2") if data.get(s)), \
        sum(count(new[s]) for s in ("skill", "skill2") if new.get(s))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    a = ap.parse_args()
    files = list(a.files)
    if a.all:
        files += sorted(glob.glob(os.path.join(a.repo, "league", "champion", "*.data_champion")))
        files += sorted(glob.glob(os.path.join(a.repo, "addons", "*", "override", "*.data_champion")))
    before = after = 0
    for f in files:
        b, n = report(f)
        before, after = before + b, after + n
    if len(files) > 1:
        print(f"skill + skill2 of {len(files)} files: {before} -> {after} nodes ({100 * (before - after) / max(before, 1):.1f}% fewer)")


if __name__ == "__main__":
    main()

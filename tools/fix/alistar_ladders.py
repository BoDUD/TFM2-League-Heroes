#!/usr/bin/env python3
"""league_alistar: the Trample and Triumphant Roar ladders without their re-checks, and the E-ready picture without
its dead R branch (skill-tree slimming, 2026-10-18).

    python tools/fix/alistar_ladders.py [--check]

The game copies skill and skill2 every tick (docs/perf.md). Both ladders were built rung by rung as
`SwitchByBuff e_(k-1) (... SwitchByBuff e_k (up) (SwitchByBuff e_(k-1) (add e_k) ())) ...`: the inner test of
e_(k-1) (p1 in the roar ladder) sits in the branch of the outer test of the same flag, reached through SwitchByBuffs
only - nothing runs between the two reads, so the inner one always takes the branch the outer one took, for every buff
state, in a cast and in what units read through his buffs. Each such inner test is replaced by that branch (2 nodes
each: three in every Trample ladder, one in every roar ladder; tools/kit/build_alistar.py's e_count / p_stack emit the
same form now). The attack and the ult (not copied every tick) get the same rewrite, so the kit stays one form.

Q's first stomp played its E-ready picture (baked into his frames by tools/fix/bake_caster_fx.py) as
`SwitchByBuff r_armed (SwitchByBuff r_go (ult_fx1) (skill_fx1)) (skill_fx1)`. r_go (1 tick) is added only by the R
check that opens every action and pulse - `SwitchByBuff r_armed [-r_go, search +r_go, search +r_go, SwitchByBuff
r_go [-r_armed, ...]]` (attack, skill, skill2, ult; asserted below; no add-on names these flags) - which takes r_armed
off in the same run whenever it adds r_go; r_armed is added only by the ult's cast, which runs that check right after.
So r_armed and r_go are never on together after any run (and a dead caster's frozen buffs come from such a run): the
ult_fx1 branch can never run or be read, and the switch is skill_fx1 (4 nodes).

skill 155 -> 131 nodes (151 -> 127 packed), skill2 184 -> 162 (179 -> 157), attack 51 -> 49. Classic simulation (every
tick's events, support lane against the five base supports, three lineups, both sides, seeds 1-4): 120 of 120 games
identical. Idempotent: --check reports whether the file is already done.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_alistar.data_champion")
N = "league_alistar_"
LADDER = {N + f"e{k}" for k in range(1, 5)} | {N + "p1", N + "p2"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def is_sw(o, name=None):
    return isinstance(o, dict) and o.get("type") == "SwitchByBuff" and (name is None or o["buff_name"] == name)


def drop_rechecks(node, known):
    """node: an effect; known: {flag: on?} for the ladder flags read by SwitchByBuffs this node hangs under through
    SwitchByBuff branches only. Returns (new node, how many re-checks went)."""
    if not is_sw(node):
        return node, 0
    b = node["buff_name"]
    if b in known:
        branch = node["effect_buff"] if known[b] else node["effect_none"]
        new, k = drop_rechecks(branch, known)
        return new, k + 1
    total = 0
    for side, on in (("effect_buff", True), ("effect_none", False)):
        kn = dict(known, **{b: on}) if b in LADDER else known
        node[side], k = drop_rechecks(node[side], kn)
        total += k
    return node, total


def walk_effects(o, fn):
    """Call fn on every effect (dict with a type) reachable from o, parents first; fn may replace it (returns it)."""
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if isinstance(v, dict) and "type" in v:
                o[k] = fn(v)
                walk_effects(o[k], fn)
            elif isinstance(v, (dict, list)):
                walk_effects(v, fn)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, dict) and "type" in v:
                o[i] = fn(v)
                walk_effects(o[i], fn)
            elif isinstance(v, (dict, list)):
                walk_effects(v, fn)


def count_rechecks(d):
    n = [0]

    def fn(e):
        if is_sw(e) and e["buff_name"] in LADDER:
            _, k = drop_rechecks(json.loads(json.dumps(e)), {})
            n[0] += k
        return e
    for slot in ("attack", "skill", "skill2", "ult"):
        walk_effects(d[slot], fn)
    return n[0]


def dead_fx(o):
    return (is_sw(o, N + "r_armed") and is_sw(o["effect_buff"], N + "r_go")
            and o["effect_buff"]["effect_none"] == o["effect_none"]
            and o["effect_none"].get("type") == "CasterAnimation" and o["effect_none"]["name"] == "skill_fx1"
            and o["effect_buff"]["effect_buff"].get("type") == "CasterAnimation")


def r_go_only_in_checks(d):
    """Every AddCasterBuff r_go sits in a check [-r_go, search(+r_go), search(+r_go), SwitchByBuff r_go [-r_armed ..]]
    under SwitchByBuff r_armed; r_armed is added only in the ult, right before such a check."""
    adds, checks = 0, 0
    text = {s: json.dumps(d[s]) for s in ("attack", "skill", "skill2", "ult")}
    for s, t in text.items():
        adds += t.count(f'"name": "{N}r_go", "duration"')

    def fn(e):
        nonlocal checks
        if is_sw(e, N + "r_armed") and e["effect_buff"].get("type") == "Combine":
            items = e["effect_buff"]["effects"]
            if items and items[0] == {"type": "RemoveCasterBuff", "name": N + "r_go"}:
                assert len(items) == 4 and all(x["type"] == "RandomTarget" for x in items[1:3])
                for x in items[1:3]:
                    assert [y["buff_state"]["name"] for y in x["effects"]] == [N + "r_go"]
                    assert x["effects"][0]["buff_state"]["duration"] == {"Time": {"tick": 1}}
                fire = items[3]
                assert is_sw(fire, N + "r_go")
                assert fire["effect_buff"]["effects"][0] == {"type": "RemoveCasterBuff", "name": N + "r_armed"}
                checks += 2
        return e
    for s in text:
        walk_effects(d[s], fn)
    assert adds == checks, (adds, checks)
    assert all(f'"name": "{N}r_armed", "duration"' not in text[s] for s in ("attack", "skill", "skill2")), \
        "r_armed added outside the ult"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8-sig")
    d = json.loads(raw)
    fx = []
    walk_effects(d["skill"], lambda e: (fx.append(e), e)[1] if dead_fx(e) else e)
    left = count_rechecks(d)
    done = left == 0 and not fx
    if a.check:
        print("already done" if done else f"{left} re-checks, {len(fx)} dead R branches left")
        sys.exit(0 if done else 1)
    if done:
        print("already done")
        return
    r_go_only_in_checks(d)
    gone = [0]

    def fix(e):
        if is_sw(e) and e["buff_name"] in LADDER:
            e, k = drop_rechecks(e, {})
            gone[0] += k
        return e
    for slot in ("attack", "skill", "skill2", "ult"):
        walk_effects(d[slot], fix)
    walk_effects(d["skill"], lambda e: e["effect_none"] if dead_fx(e) else e)
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: {gone[0]} ladder re-checks and {len(fx)} dead R branch(es) gone")


if __name__ == "__main__":
    main()

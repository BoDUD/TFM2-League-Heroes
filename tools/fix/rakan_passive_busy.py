#!/usr/bin/env python3
"""league_rakan: the passive's "is the countdown still running" check as one chain (skill-tree slimming, 2026-10-18).

    python tools/fix/rakan_passive_busy.py [--check]

Fey Reflexes (异色羽裳) waits 12 s after its shield broke: twelve caster flags p_s1..p_s12 (60..720 ticks) laid together,
each hit on a champion taking the highest one off. Every action (attack, Q, W -> E, R) first checks the countdown: the
1-tick flag p_busy off, then twelve separate `SwitchByBuff p_s<k> -> AddCasterBuff p_busy` (one instance per flag still
on), then `SwitchByBuff p_busy` - off: the shield. The twelve checks become one chain from the top, p_s12 -> p_busy, else
p_s11 -> p_busy, ... else p_s1 -> p_busy: p_busy is on after it exactly when it was on before (one instance instead of one
per flag; `SwitchByBuff` only asks whether any is on, `RemoveCasterBuff` takes them all), so the same shield in the same
casts. p_busy is hidden (no view_buffs entry, no stat), laid and read only in these checks, and lasts the tick it was laid:
readers of a tree (the AI before a cast, enemies at any tick) see the same p_busy as before, so the same branch; the check
itself holds nothing they score. 36 nodes -> 25 in each of the four slots (the game copies skill and skill2 every tick,
docs/perf.md). The trace check needs TRACE_HIDE=league_rakan_p_busy (its instance count is in the buff list).

Idempotent: --check reports whether the file is already done.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_rakan.data_champion")
N = "league_rakan_"
STEPS = [f"p_s{k}" for k in range(1, 13)]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def busy():
    return {"type": "AddCasterBuff", "buff_state": {"name": N + "p_busy", "duration": {"Time": {"tick": 1}}},
            "only_to_enemy": False}


NONE = {"type": "Combine", "effects": []}


def old_check(k):
    return {"type": "SwitchByBuff", "buff_name": N + STEPS[k], "effect_buff": busy(), "effect_none": dict(NONE)}


def chain():
    out = dict(NONE)
    for name in STEPS:      # built from the bottom, read from the top: p_s12 first
        out = {"type": "SwitchByBuff", "buff_name": N + name, "effect_buff": busy(), "effect_none": out}
    return out


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in list(o.values()):
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def waits(d):
    """The p_wait branches of the passive block in every slot."""
    found = []
    for slot in ("attack", "skill", "skill2", "ult"):
        walk(d[slot]["effect"], lambda o: found.append(o) if o.get("type") == "SwitchByBuff"
             and o.get("buff_name") == N + "p_wait" else None)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8-sig")
    d = json.loads(raw)
    blocks = waits(d)
    if len(blocks) != 4:
        sys.exit(f"expected the passive's p_wait check in 4 slots, found {len(blocks)}: update this script")
    todo = []
    for b in blocks:
        items = b["effect_buff"]["effects"]
        assert items[0] == {"type": "RemoveCasterBuff", "name": N + "p_busy"}, items[0]
        assert items[-1].get("buff_name") == N + "p_busy" and len(items) in (3, 14), len(items)
        if len(items) == 14:
            assert items[1:13] == [old_check(k) for k in range(12)], "the twelve checks differ"
            todo.append(b)
        else:
            assert items[1] == chain(), "the chain differs"
    # 14 uses a slot either way (the removal, twelve lays, the read): none elsewhere
    assert json.dumps(d).count(f'"{N}p_busy"') == 4 * 14, "p_busy is used elsewhere"
    if a.check:
        print("already done" if not todo else f"{len(todo)} of 4 slots still check twelve times")
        sys.exit(1 if todo else 0)
    if not todo:
        print("already done")
        return
    for b in todo:
        items = b["effect_buff"]["effects"]
        b["effect_buff"]["effects"] = [items[0], chain(), items[-1]]
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: {len(todo)} countdown checks chained")


if __name__ == "__main__":
    main()

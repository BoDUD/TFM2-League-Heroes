#!/usr/bin/env python3
"""league_fiora: Grand Challenge's Vital ladder written once instead of four times (skill-tree slimming, 2026-10-18).

    python tools/fix/fiora_vital_ladder.py [--check]

Every hit of hers on a champion runs the Vital hook (the attack, Q's two dash strikes, W's two lines; all five the
same): while R is on (`r_on`) it strikes the top rung left of r_v4..r_v1, else the passive's Vital. The ladder was
four copies of the strike, one per rung (the damage, heal, move speed, pictures, sound and the flags R keeps: 78 nodes
in a hook, and Q and W each carry two hooks - the game copies skill and skill2 every tick, docs/perf.md). The rungs are
added together (R's two starts: all four, 480 ticks) and taken off from the top (each strike its own rung, the fourth
and the Victory Zone's cleanup all four), so whenever any rung is on, r_v1 is. The ladder becomes: with r_v1 on, the
strike, then the top rung off (r_v4, else r_v3, else r_v2, else r_v1), the 3-tick cooldown cap renewed, and then with
r_v1 still on the struck / owed flags (rungs left), without it R's end (the fourth Vital: the zone's flag, the heal
sound). The same effects in the same order for every state R can be in, also for the AI reading the branch; 34 nodes
instead of 78. The cleanup's removals of r_v1..r_v4 went: the ladder has just taken the last one.

addons/league_fiora_duel/make_override.py copies the hook from here (run it after this). Idempotent: --check reports
whether the file is already done.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_fiora.data_champion")
N = "league_fiora_"
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": N + buff, "effect_buff": yes, "effect_none": no or dict(NONE)}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": N + name}


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in list(o.values()):
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def is_hook(o):
    return (o.get("type") == "SwitchByBuff" and o.get("buff_name") == N + "r_on"
            and o.get("effect_buff", {}).get("type") == "SwitchByBuff"
            and o["effect_buff"].get("buff_name") in (N + "r_v4", N + "r_v1"))


def compact(ladder):
    """The four-rung ladder -> the one-strike form (checks every rung's strike is the same first)."""
    rungs, node = [], ladder
    for k in (4, 3, 2, 1):
        assert node.get("type") == "SwitchByBuff" and node["buff_name"] == N + f"r_v{k}", node.get("buff_name")
        rungs.append(node["effect_buff"]["effects"])
        node = node["effect_none"]
    assert node == NONE, node
    strike = rungs[0][:9]
    tail = rungs[0][10:]
    for k, items in zip((4, 3, 2), rungs[:3]):
        assert items[:9] == strike and items[9] == rm(f"r_v{k}") and items[10:] == tail, f"rung {k} differs"
    last = rungs[3]
    assert last[:9] == strike and last[9] == rm("r_v1") and last[10:12] == tail[:2] and len(last) == 13
    assert [e.get("type") for e in tail] == ["RemoveCasterBuff", "AddCasterBuff", "AddCasterBuff",
                                             "RemoveCasterBuff", "AddCasterBuff"]
    assert tail[0] == rm("r_cdr") and tail[2]["buff_state"]["name"] == N + "r_struck"
    end = last[12]
    assert end.get("type") == "Combine"
    end_items = [e for e in end["effects"] if e not in [rm(f"r_v{k}") for k in (1, 2, 3, 4)]]
    assert len(end_items) == len(end["effects"]) - 4
    top = sw("r_v4", rm("r_v4"), sw("r_v3", rm("r_v3"), sw("r_v2", rm("r_v2"), rm("r_v1"))))
    return sw("r_v1", {"type": "Combine", "effects": strike + [top] + tail[:2] + [
        sw("r_v1", {"type": "Combine", "effects": tail[2:]}, {"type": "Combine", "effects": end_items})]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8-sig")
    d = json.loads(raw)
    hooks = []
    for slot in ("attack", "skill", "skill2", "ult"):
        walk(d[slot]["effect"], lambda o: hooks.append(o) if is_hook(o) else None)
    if len(hooks) != 5:
        sys.exit(f"expected 5 Vital hooks, found {len(hooks)}: update this script")
    todo = [h for h in hooks if h["effect_buff"]["buff_name"] == N + "r_v4"]
    if a.check:
        print("already done" if not todo else f"{len(todo)} of 5 hooks still have the four-copy ladder")
        sys.exit(1 if todo else 0)
    if not todo:
        print("already done")
        return
    for h in todo:
        h["effect_buff"] = compact(h["effect_buff"])
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: {len(todo)} Vital hooks compacted")


if __name__ == "__main__":
    main()

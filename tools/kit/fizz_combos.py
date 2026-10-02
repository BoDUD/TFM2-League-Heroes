#!/usr/bin/env python3
"""Fizz's combos (the user, 2026-10-02: "小鱼人也顺便加一点连招", after Yasuo's and Yone's).

    python tools/kit/fizz_combos.py [--check]

Playful / Trickster (E) waits up to 1 s with an enemy champion near (it jumps when he is hit). Two windows make it
jump at once instead, like tools/kit/leesin_combos.py each combo played by the slot it spends, no slot held:
- Q -> E: Urchin Strike's dash through an enemy champion (a champion-only twin of its hit: q_on, 60 ticks);
- R -> E: Chum the Waters' fish stuck on an enemy champion (the kit's own r_stuck, 140 ticks: until the shark).
E cast in either skips the enemy check that would hold it, so he hops at once onto the nearest champion (the one Q
went through) and slams. The jump itself is untouched (written once, as before).
The kit file was hand-built; the script refuses to run twice (q_on marks a combo kit). --check only verifies.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_fizz.data_champion")
P = "league_fizz_"
WINDOW = 60                  # q_on: E this soon after Q went through a champion jumps at once


def n(x):
    return P + x


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or combine()}


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None


def build(k):
    q, e = k["skill"], k["skill2"]
    rush = find(q["effect"], lambda o: o.get("type") == "RushMoveToBack")
    top = e["effect"]["effects"]
    i = next(j for j, x in enumerate(top) if x.get("type") == "RandomTarget")
    check = top[i]
    assert check["casting_target"] == "EnemyChampion" and check["effects"][0]["buff_state"]["name"] == n("e_threat")
    assert n("r_stuck") in json.dumps(k["ult"])
    # ---- Q through a champion: the window (a champion-only twin of the dash's hit, no picture)
    rush["applied_effects"].append({          # a RushMoveToBack's applied_effects are plain effects
        "type": "TargetProjectile", "name": n("q_twin"), "speed": 20000, "y_offset": 0,
        "applied_target": "EnemyChampion",
        "applied_effects": [{"casting_type": "Targeting", "effect": flag("q_on", WINDOW)}]})
    # ---- E in either window: no enemy check, so no wait
    top[i] = sw("q_on", combine(), sw("r_stuck", combine(), check))
    return k


def has_combos(k):
    return n("q_on") in json.dumps(k)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    k = json.loads(raw)
    if args.check:
        ok = has_combos(k)
        print("league_fizz.data_champion:", "combos in" if ok else "NO combos")
        sys.exit(0 if ok else 1)
    if has_combos(k):
        sys.exit("league_fizz.data_champion already has the combos")
    out = json.dumps(build(k), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_fizz.data_champion with Q -> E and R -> E")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Alistar's Pulverize once per its cooldown, Q or W -> Q (the user, 2026-10-13: 「牛头EQ后 还能释放一次Q」「改」).

    python tools/fix/alistar_pulverize.py [--check]

His Q (E -> Q) slammed and his W carried a slam of its own on its own cooldown, so a Q and a W a moment apart threw
everyone up twice. In League W -> Q is the one Q: the slam waits for Q's cooldown. Here both slams share a caster flag,
league_alistar_pq_cd, set for q_cd ticks (600, Q's cooldown) when either slams: while it holds, Q only tramples and W
only headbutts (no landing slam, no slam animation). Edits league/champion/league_alistar.data_champion in place (the
shipped kit carries the red-side pass's changes, so it is not rebuilt from tools/kit/build_alistar.py, which has the
same gate). Idempotent; --check only says whether it is there.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT = os.path.join(ROOT, "league", "champion", "league_alistar.data_champion")
FLAG = "league_alistar_pq_cd"
TICKS = 600


def has_airborne(o):
    if isinstance(o, dict):
        if o.get("type") == "Airborne":
            return True
        return any(has_airborne(v) for v in o.values())
    if isinstance(o, list):
        return any(has_airborne(v) for v in o)
    return False


def gate(node):
    """node (one effect) played only with the flag off, the flag set as it plays."""
    return {"type": "SwitchByBuff", "buff_name": FLAG, "effect_buff": {"type": "Combine", "effects": []},
            "effect_none": {"type": "Combine", "effects": [
                {"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": TICKS}}},
                 "only_to_enemy": False},
                node]}}


def gated(o):
    return isinstance(o, dict) and o.get("type") == "SwitchByBuff" and o.get("buff_name") == FLAG


def wrap(o):
    """Top down: the first Delayed holding the knock-up on each path wrapped (nothing under it, nothing already
    wrapped). -> how many are wrapped now."""
    n = 0
    if isinstance(o, dict):
        for key, v in o.items():
            if gated(v):
                n += 1
            elif isinstance(v, dict) and v.get("type") == "Delayed" and has_airborne(v):
                o[key] = gate(v)
                n += 1
            else:
                n += wrap(v)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if gated(v):
                n += 1
            elif isinstance(v, dict) and v.get("type") == "Delayed" and has_airborne(v):
                o[i] = gate(v)
                n += 1
            else:
                n += wrap(v)
    return n


def count(o):
    if gated(o):
        return 1
    if isinstance(o, dict):
        return sum(count(v) for v in o.values())
    if isinstance(o, list):
        return sum(count(v) for v in o)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    raw = open(KIT, "rb").read().decode("utf-8-sig")
    k = json.loads(raw)
    if a.check:
        nq, nw = count(k["skill"]["effect"]), count(k["skill2"]["effect"])
        print(f"gated: Q {nq}, W {nw}")
        sys.exit(0 if nq and nw else 1)
    nq = wrap(k["skill"]["effect"])
    nw = wrap(k["skill2"]["effect"])
    assert nq >= 1 and nw >= 1, (nq, nw)
    text = json.dumps(k, ensure_ascii=False, indent=2).replace(chr(10), chr(13) + chr(10)) + chr(13) + chr(10)
    with open(KIT, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{KIT}: Q slams gated {nq}, W slams gated {nw}")


if __name__ == "__main__":
    main()

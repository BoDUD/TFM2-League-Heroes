#!/usr/bin/env python3
"""league_rakan R: the ult pose only while he dashes, so he runs on his own feet in between.

    python tools/fix/fix_rakan_r_walk.py [--check]

「洛开大后在原地跑」 (2026-10-07): the R held a CasterAnimation "ult" for its whole 240 ticks (re-issued at every
hop, 20 ticks apart, for what was left), and a CasterAnimation keeps a unit from walking. He moved only by the
hops' RushMoveToBack - a few ticks each, barely any way when the champion he passed was beside him, none with no
enemy within 50000 - and for the rest stood on the spot in the ult's running pose (restarted every 20 ticks, its first
four frames only). Every CasterAnimation "ult" in the R now lasts HOP ticks, about one dash, so between the hops he
walks and attacks with R's +75% move speed, the charm ring following him (League: he runs about freely). The user's
pick 「只在冲刺时播 ult」. Writes league/champion/league_rakan.data_champion in place (indent 2, CRLF).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT = os.path.join(ROOT, "league", "champion", "league_rakan.data_champion")
HOP = 12                     # ticks: a hop of 20000 at 1800 a tick (the R's slower dash) takes about 11


def shorten(o, n=0):
    if isinstance(o, dict):
        if o.get("type") == "CasterAnimation" and o.get("name") == "ult" and o["tick"] != HOP:
            o["tick"] = HOP
            n += 1
        for v in o.values():
            n = shorten(v, n)
    elif isinstance(o, list):
        for v in o:
            n = shorten(v, n)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    kit = json.load(open(KIT, encoding="utf-8"))
    n = shorten(kit["ult"]["effect"])
    if a.check:
        print(f"{n} ult animations still longer than {HOP} ticks")
        sys.exit(1 if n else 0)
    text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(KIT, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{n} ult animations set to {HOP} ticks")


if __name__ == "__main__":
    main()

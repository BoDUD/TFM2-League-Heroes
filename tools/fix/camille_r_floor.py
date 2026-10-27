#!/usr/bin/env python3
"""Camille's R arena picture for the whole 4 s: one 240-tick floor at the landing instead of seven clocked 30-tick pieces.

    python tools/fix/camille_r_floor.py [--check] [--path <data_champion>]

The user (2026-10-27): 「青钢影大招还是1秒消失」. The arena's rules held for 4 s (r_on, the add-on's ARENA lines), but its
picture did not: after r_field (the arena forming, 30 ticks) each 30-tick r_floor piece (r_zone's loop) was to start
from a clock - a penetrating `LinearProjectile` of speed 1 and range 30, 60 ... 210 that should stand on the landing and
end after `range` ticks. Its direction is (0, 0) (she lands on her target) and the engine removes such a projectile on
the tick it appears (SDK simulation trace, 2026-10-27: all seven clocks Removed and all seven pieces spawned on the
landing tick, 14 casts in 3 games), so the pieces all played at once and the picture was gone half a second after the
landing. Chaining the pieces does not work either: a zone's `end_effects` run on the units in it, and a zone started
there (straight or in a `Delayed`) never appeared; a zone started from a `Delayed` in the anchor's `end_effects` points
(1, 0) or (-1, 0) by the side she stood on, and r_zone is not the same turned round (59% of its pixels differ).

So r_floor is one `RangePeriodProjectile` of r_on's ticks started in the anchor's `end_effects` beside r_field (the
anchor's own zones point (-1, 0): upright), r_zone looping over it. It cannot end before its time: the add-on
league_camille_wall keeps her in the arena (the AI's walks out turned into attacks), so the picture and the rules end
together but when she leaves anyway - her low-health E escape (kept, the add-on's v4.2), a knock-back, her death - and the
picture stays to its 4 s. The floor also renews r_vis, the gate of the hold on her target, for the whole arena now (it
lapsed with the pieces after half a second). Idempotent; --check exits 1 when the file differs.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_camille.data_champion")
N = "league_camille_"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def find(o, pred, out):
    if isinstance(o, dict):
        if pred(o):
            out.append(o)
        for v in o.values():
            find(v, pred, out)
    elif isinstance(o, list):
        for v in o:
            find(v, pred, out)
    return out


def r_on_ticks(ult):
    on = find(ult, lambda o: o.get("type") == "AddCasterBuff" and o["buff_state"]["name"] == N + "r_on", [])
    ticks = {o["buff_state"]["duration"]["Time"]["tick"] for o in on}
    if len(ticks) != 1:
        sys.exit(f"r_on durations {ticks}: expected one")
    return ticks.pop()


def apply(d):
    ult = d["ult"]["effect"]
    land = find(ult, lambda o: o.get("type") == "MoveToTarget", [])[0]["end_effects"]
    anchor = next(e for e in land if e.get("name") == N + "r_anchor")
    field = next(e for e in anchor["end_effects"] if e.get("name") == N + "r_field")
    clocks = [e for e in land if e.get("name") == N + "r_clock"]
    floors = find(clocks, lambda o: o.get("name") == N + "r_floor", [])
    have = [e for e in anchor["end_effects"] if e.get("name") == N + "r_floor"]
    if not floors and have:
        return d                                    # done already
    floor = copy.deepcopy(floors[0])
    floor["tick"] = r_on_ticks(d["ult"])
    land[:] = [e for e in land if e.get("name") != N + "r_clock"]
    at = anchor["end_effects"].index(field) + 1
    anchor["end_effects"][at:at] = [floor]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    bom = "﻿" if raw.startswith("﻿") else ""
    text = bom + json.dumps(apply(json.loads(raw.lstrip("﻿"))), ensure_ascii=False, indent=2).replace("\n", nl) + nl
    if a.check:
        print("already done" if text == raw else "Camille's 4-s floor not applied")
        sys.exit(0 if text == raw else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: R's arena floor is one zone for the arena's whole life (the r_clock pieces gone)")


if __name__ == "__main__":
    main()

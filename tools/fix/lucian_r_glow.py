#!/usr/bin/env python3
"""league_lucian's R shows on him while it fires: his channel flag gets a picture.

    python tools/fix/lucian_r_glow.py [--check] [--path <data_champion>]

The user (2026-10-27): 「卢锡安的移动大招有问题吧？」「移动大招看不出来放大 只听得到音乐」. Since he walks while The Culling
fires (tools/kit/lucian_r_move.py, 2026-10-21) the 182-tick ult pose is gone and the shots alone show it: each
`r_bullet` reaches its target in 4-5 ticks at 12000 a tick, its first two frames blank or a dot - about 0.06 s of a
streak every 9 ticks, easy to miss on a walking Lucian. His channel flag `league_lucian_r_ch` (183 ticks from the cast,
taken away by crowd control as the shots stop) had no picture; it now plays his blue sparkle (`league_lucian_fx`
`hit`, 5 frames in 0.2 s, looped) on him for as long as the shots go on. Picture only: no damage or timing change.
league_sylas's copy of his ult and league_viego_soul's of his kit pick the view up from their make_override.py.
Idempotent; --check exits 1 when the file differs.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_lucian.data_champion")
VIEW = {"type": "Animated", "name": "league_lucian_r_ch", "anim": "asset/league/effects/league_lucian_fx", "tag": "hit",
        "z": 2}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def apply(d):
    if VIEW["name"] not in json.dumps(d["ult"]):
        sys.exit(f"{VIEW['name']} is no longer in his ult: nothing to show")
    d["view_buffs"] = [v for v in d["view_buffs"] if v["name"] != VIEW["name"]] + [dict(VIEW)]
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
        print("already done" if text == raw else "Lucian's R picture not applied")
        sys.exit(0 if text == raw else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: {VIEW['name']} shows {VIEW['tag']} on him while R fires")


if __name__ == "__main__":
    main()

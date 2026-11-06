#!/usr/bin/env python3
"""Leona's Sunlight on champions in sunglasses (the user's easter egg, 2026-11-05: 「太阳镜防晒」).

    python tools/kit/leona_shades.py [--check]

Leona's passive Sunlight deals 1 less to every champion wearing sunglasses. This pack's Sunlight is no detonation: her
Q, E, W and R hang league_leona_sunlight on each enemy they hit (damaged_amplify 10 for 90 ticks). Data cannot read who
the target is (and SwitchByBuff reads the caster, never the target), so the match add-on league_eggs does it: while a
wearer (Vayne, Locke, Heimerdinger, Ziggs, Twitch - sunglasses or goggles over the eyes in their art - and Lee Sin's
blindfold, the user's own example) carries n Sunlight it also carries n league_leona_shades (damaged_reduce 1 each):
+9% damage taken instead of +10%. This script only gives the shades a picture in Leona's kit: the view_buffs entry
league_leona_shades (a pair of sunglasses beside her sun mark, asset/league/effects/league_leona_shades,
tools/art/fx_leona_shades.py), bound like her sunlight mark. Nothing her kit does changes.
The kit file was hand-built; this script refuses to run twice. --check only verifies.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_leona.data_champion")
SUN = "league_leona_sunlight"
SHADES = {"type": "Animated", "name": "league_leona_shades", "anim": "asset/league/effects/league_leona_shades",
          "tag": "shades", "z": 2}


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def has_shades(k):
    return any(v["name"] == SHADES["name"] for v in k["view_buffs"])


def build(k):
    sun = [v for v in k["view_buffs"] if v["name"] == SUN]
    assert len(sun) == 1 and set(sun[0]) == set(SHADES), "the sunlight mark's binding changed: update this script"
    k["view_buffs"].append(dict(SHADES))
    return k


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    k = json.loads(raw)
    if args.check:
        ok = [v for v in k["view_buffs"] if v["name"] == SHADES["name"]] == [SHADES]
        print("league_leona.data_champion:", "shades in" if ok else "NO shades")
        sys.exit(0 if ok else 1)
    if has_shades(k):
        sys.exit("league_leona.data_champion already has the shades")
    out = json.dumps(build(k), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_leona.data_champion with the view league_leona_shades")


if __name__ == "__main__":
    main()

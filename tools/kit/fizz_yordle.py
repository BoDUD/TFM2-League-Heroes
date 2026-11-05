#!/usr/bin/env python3
"""Fizz's shark swallows small yordles (the user's easter egg, 2026-11-05: 「鲨鱼吃小矮子」).

    python tools/kit/fizz_yordle.py [--check]

When Chum the Waters kills a small yordle (Annie, Lulu, Tristana, ... - the user's list; Teemo and Heimerdinger keep their
bodies: too heavy, head too big) the shark swallows the body: none is left on the ground. Data cannot read a champion's
id, so the swallow is native - the match add-on (league_eggs) banishes the yordle's body a moment after the bite, with
this kit's picture league_fizz_r_gulp as the banish's lock picture (the pool closing, bubbles; then nothing). The kit
only tells the add-on who the shark killed:
  * every bite of the shark (league_fizz_r_bite1 / 2 / 3, and the big shark of a missed fish) first lays a 2-tick marker
    league_fizz_r_eat on each enemy it hits, before its damage: a unit the bite kills keeps it frozen on its body (a dead
    unit's buffs keep the state they had when it died), one that lives loses it 2 ticks later;
  * the view league_fizz_r_gulp (asset/league/effects/league_fizz_gulp, tools/art/fx_fizz_gulp.py).
The marker has no stats and no picture; nothing else changes (the ult is not one of the trees the game copies every tick).
The kit file was hand-built (tools/kit/fizz_combos.py patched it once); this script refuses to run twice. --check only
verifies.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_fizz.data_champion")
P = "league_fizz_"
EAT = P + "r_eat"
EAT_T = 2                    # ticks the marker stays on a unit the bite does not kill
BITES = (P + "r_bite1", P + "r_bite2", P + "r_bite3")
N_BITES = 4                  # the three sharks of a stuck fish and the big shark of a missed one
GULP = {"type": "Animation", "name": P + "r_gulp", "anim": "asset/league/effects/league_fizz_gulp", "tag": "gulp",
        "z": -1, "is_follow": True}


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def marker():
    return {"casting_type": "Targeting",
            "effect": {"type": "AddBuff", "buff_state": {"name": EAT, "duration": {"Time": {"tick": EAT_T}}}}}


def bites(o, out=None):
    """Every shark bite zone in the tree."""
    out = [] if out is None else out
    if isinstance(o, dict):
        if o.get("type") == "RangeProjectile" and o.get("name") in BITES:
            out.append(o)
        for v in o.values():
            bites(v, out)
    elif isinstance(o, list):
        for v in o:
            bites(v, out)
    return out


def marked(b):
    first = b["applied_effects"][0]["effect"]
    return first.get("type") == "AddBuff" and first["buff_state"]["name"] == EAT


def has_egg(k):
    return any(marked(b) for b in bites(k["ult"])) or any(v["name"] == GULP["name"] for v in k["view_effects"])


def build(k):
    found = bites(k["ult"])
    assert len(found) == N_BITES, f"{len(found)} shark bites in the ult, expected {N_BITES}: update this script"
    for b in found:
        assert b["applied_effects"][0]["effect"]["type"] == "ApAttack", f"{b['name']}: the damage is not first"
        b["applied_effects"].insert(0, marker())
    k["view_effects"].append(dict(GULP))
    return k


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    k = json.loads(raw)
    if args.check:
        found = bites(k["ult"])
        ok = (len(found) == N_BITES and all(marked(b) for b in found)
              and [v for v in k["view_effects"] if v["name"] == GULP["name"]] == [GULP])
        print("league_fizz.data_champion:", "yordle egg in" if ok else "NO yordle egg",
              f"({sum(marked(b) for b in found)} of {len(found)} bites marked)")
        sys.exit(0 if ok else 1)
    if has_egg(k):
        sys.exit("league_fizz.data_champion already has the yordle egg")
    out = json.dumps(build(k), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print(f"wrote league/champion/league_fizz.data_champion: {N_BITES} bites mark {EAT}, view {GULP['name']}")


if __name__ == "__main__":
    main()

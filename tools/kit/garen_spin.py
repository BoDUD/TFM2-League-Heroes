#!/usr/bin/env python3
"""Where Garen's Judgment (E) moves him while he spins (a player's feedback, 2026-10-03: 「盖伦的大风车有没有可能改一下ai设定，
自动吸附敌方英雄有点容易送了，而且清兵的时候不会动，也很呆」).

    python tools/kit/garen_spin.py [--check]

The spin's forced animation holds him, so each of the 7 pulses moves him with a dash. Each dash used to go at 1400 a
tick (faster than he walks) onto a random enemy champion within 60000 - often one behind the front, or one under its
tower - and, with no champion that close, nowhere: on a wave or a camp he spun on the spot. Now each pulse looks in
rings and dashes at his own move speed (1000) onto the first unit it finds:
  1. an enemy champion within CHAMP (one he is already on: he keeps to him, League's chase);
  2. else any enemy unit within NEAR (minions and monsters too: he spins through the wave or the camp);
  3. else any enemy unit within FAR (he walks up to the nearest group);
  4. else he spins where he is.
A ring that finds a unit sets a 1-tick caster flag (FLAG) that skips the outer ones (league_lucian R's rings). The
dash's end still deals the +25% on the unit he went for (League's bonus on the nearest enemy).
In the SDK simulation (Garen top against base fighter / knight / executioner, three lineups, both sides, 432 games of
10 minutes each): spins on waves and camps that moved him less than 10 px 73% -> 6%; spins ending with no ally within
40000 44% -> 40%; deaths a game 4.29 -> 4.25; kill difference -0.98 -> -1.47 (noise: about 0.35). A version that never
put champions first ended alone after 34% of spins but lost a kill a game (-2.08): his spin missed the champion he
fought. The kit file was hand-written; the script refuses to run twice (FLAG marks the new pulses). --check only says
whether the file has them.
"""
import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_garen.data_champion")
FLAG = "league_garen_e_found"
CHAMP, NEAR, FAR = 25000, 30000, 45000      # ring ranges: a champion he is on, the units round him, the next group
SPEED = 1000                                # his move speed: the dashes are no faster than his walk


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def flag():
    return {"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": 1}}}, "only_to_enemy": False}


def ring(rng, target, end, last):
    dash = {"type": "MoveToTarget", "speed": SPEED, "range": rng, "end_effects": end}
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": ([] if last else [flag()]) + [dash]}


def rings(end):
    spec = [(CHAMP, "EnemyChampion"), (NEAR, "EnemyWithoutTower"), (FAR, "EnemyWithoutTower")]
    node = None
    for i in range(len(spec) - 1, -1, -1):
        rng, target = spec[i]
        r = ring(rng, target, copy.deepcopy(end), last=node is None)
        node = r if node is None else {"type": "Combine", "effects": [
            r, {"type": "SwitchByBuff", "buff_name": FLAG, "effect_buff": {"type": "Combine", "effects": []},
                "effect_none": node}]}
    return node


def has_rings(kit):
    return FLAG in json.dumps(kit["skill2"])


def build(kit):
    n = 0
    for pulse in kit["skill2"]["effect"]["effects"]:
        if pulse.get("type") != "Delayed":
            continue
        for i, e in enumerate(pulse["effects"]):
            if e.get("type") == "RandomTarget" and e["effects"][0].get("type") == "MoveToTarget":
                pulse["effects"][i] = rings(e["effects"][0]["end_effects"])
                n += 1
    if n != 7:
        sys.exit(f"expected 7 spin pulses with a dash, found {n}")
    return kit


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    kit = json.loads(raw)
    if args.check:
        ok = has_rings(kit)
        print("league_garen.data_champion:", "E moves in rings" if ok else "E still dashes at random champions")
        sys.exit(0 if ok else 1)
    if has_rings(kit):
        sys.exit("league_garen.data_champion already has the rings")
    out = json.dumps(build(kit), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_garen.data_champion: E's 7 pulses move him in rings at his own speed")


if __name__ == "__main__":
    main()

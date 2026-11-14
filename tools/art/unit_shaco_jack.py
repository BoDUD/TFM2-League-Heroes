#!/usr/bin/env python3
"""Shaco's Jack in the Box as a unit: league/champions/league_shaco_jack#sheet.png + #anim.fanim.

    python tools/art/unit_shaco_jack.py [--check] [--preview <png>]

The add-on league_shaco_backstab gives the box W throws a body through the mod API's spawn_unit under this name (round 2
of "summons as real units", 2026-11-14): the unit can be targeted and killed, the add-on's native code fires its shots.
Every frame is the box's own picture (league/effects/league_shaco_big, tag w_box - its plain 1x frames: an effects-PPU
sheet the game draws at the 1x size, so the unit is the size the box has on screen today, no league.dll row), facing
right as it is drawn (the jester shoots right; the game mirrors a unit facing left). The picture: the closed box (0),
the jester springing out (1, 2), then out (3) and shooting (4), out and shooting by turns, the jester back in (47) and a
puff (48, 49). Every frame's lowest row is the box's base, put on the unit's ground row (checked):

  idle    the jester out, two of its frames (3, 5);
  run     the same (the body has move speed 1: it does not walk);
  attack  out, the shot (4) - where the add-on's harmless unit attack lands (league_shaco_backstab src/jack.rs: JACK_ACT /
          JACK_LANDS, checked by its make_override.py against this sheet's .fanim) - out;
  hit     out, a column back;
  dead    the jester back in (47), the puff (48, 49), gone.
Its spring is the main pack's landing picture, played while the body waits banished (src/jack.rs).
--check: exit 1 when the sheet in the repo is not what this writes. --preview: the frames at 8x on the ground line.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_frames as U  # noqa: E402

BIG = os.path.join(U.EFFECTS, "league_shaco_big")
OUT = os.path.join(U.CHAMPIONS, "league_shaco_jack")
OUT_A, OUT_B, SHOT, SHUT, PUFF = 3, 5, 4, 47, (48, 49)
IDLE_MS = 200
ATTACK_MS = (60, 150, 90)
HIT_MS = 100
DEAD_MS = (80, 80, 80, 60)


def build():
    raw = U.frames_of(BIG, "w_box")
    if len(raw) != 50:
        sys.exit("w_box is no longer 50 frames: read the picture again")
    base = U.lowest(raw[OUT_A][0])
    for k in (OUT_B, SHOT, SHUT):
        if U.lowest(raw[k][0]) != base:
            sys.exit(f"w_box {k}: the box's base is not on the same row as frame {OUT_A}: read the picture again")
    lift = U.FEET - base
    f = {k: U.shift(raw[k][0], 0, lift) for k in (OUT_A, OUT_B, SHOT, SHUT) + PUFF}
    return {
        "idle": [(f[OUT_A], IDLE_MS), (f[OUT_B], IDLE_MS)],
        "run": [(f[OUT_A], IDLE_MS), (f[OUT_B], IDLE_MS)],
        "attack": list(zip([f[OUT_A], f[SHOT], f[OUT_B]], ATTACK_MS)),
        "hit": [(U.shift(f[OUT_A], -1, 0), HIT_MS)],
        "dead": list(zip([f[SHUT], U.under_ground_cut(f[PUFF[0]]), U.under_ground_cut(f[PUFF[1]]), U.blank()], DEAD_MS)),
    }


def shot_lands():
    """the attack's ticks long and the tick the shot frame starts"""
    return round(sum(ATTACK_MS) * 60 / 1000), round(ATTACK_MS[0] * 60 / 1000)


if __name__ == "__main__":
    U.run("league_shaco_jack", OUT, build)

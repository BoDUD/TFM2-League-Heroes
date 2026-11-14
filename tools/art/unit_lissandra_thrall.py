#!/usr/bin/env python3
"""Lissandra's Frozen Thrall as a unit: league/champions/league_lissandra_thrall#sheet.png + #anim.fanim.

    python tools/art/unit_lissandra_thrall.py [--check] [--preview <png>]

The add-on league_lowhp raises each of her thralls as a unit through the mod API's spawn_unit under this name (round 2 of
"summons as real units", 2026-11-14): League's thrall walks after the nearby enemies until it shatters. Every frame is
the thrall's own picture (league/effects/league_lissandra_big, tag p_thrall - its plain 1x frames: an effects-PPU sheet
the game draws at the 1x size, so the unit is the size the thrall has on screen today, no league.dll row). The picture:
it rises out of the ice (0, 1), stands (2-5), cracks (6) and glows white before it shatters (7). Every frame's lowest
row is put on the unit's ground row:

  idle    its three standing frames at the picture's 250 ms;
  run     the standing frames by turns, quicker: a lurching walk;
  attack  standing, cracking, standing (it never strikes: the add-on shatters it);
  hit     standing, a column back;
  dead    cracking, the white glow, gone (the add-on's shatter picture bursts where it shatters).
--check: exit 1 when the sheet in the repo is not what this writes. --preview: the frames at 8x on the ground line.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_frames as U  # noqa: E402

BIG = os.path.join(U.EFFECTS, "league_lissandra_big")
OUT = os.path.join(U.CHAMPIONS, "league_lissandra_thrall")
STAND = (3, 4, 5)
CRACK, GLOW = 6, 7
IDLE_MS = 250
RUN_MS = 150
ATTACK_MS = (80, 120, 80)
HIT_MS = 100
DEAD_MS = (100, 100, 60)


def build():
    raw = U.frames_of(BIG, "p_thrall")
    if len(raw) != 8 or [raw[k][1] for k in STAND] != [IDLE_MS] * 3:
        sys.exit("p_thrall is no longer 8 frames standing at 250 ms: read the picture again")
    f = [U.to_feet(r[0]) for r in raw]
    return {
        "idle": [(f[k], IDLE_MS) for k in STAND],
        "run": [(f[k], RUN_MS) for k in (3, 4, 5, 4)],
        "attack": list(zip([f[4], f[CRACK], f[4]], ATTACK_MS)),
        "hit": [(U.shift(f[4], -1, 0), HIT_MS)],
        "dead": list(zip([f[CRACK], f[GLOW], U.blank()], DEAD_MS)),
    }


if __name__ == "__main__":
    U.run("league_lissandra_thrall", OUT, build)

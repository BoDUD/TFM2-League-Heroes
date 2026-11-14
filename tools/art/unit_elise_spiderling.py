#!/usr/bin/env python3
"""Elise's spiderling as a unit of its own: league/champions/league_elise_spiderling#sheet.png + #anim.fanim.

    python tools/art/unit_elise_spiderling.py [--check] [--preview <png>]

The add-on league_elise spawns the passive's spiderlings in Spider Form through the mod API's spawn_unit under this name
(round 2 of "summons as real units", 2026-11-14). Every frame is the crawling spiderling of Volatile Spiderling
(league/effects/league_elise_fx, tag w_spider: its plain 1x frames, the size that spiderling has on screen today - the
riding spiderlings of the main pack have no body, only claw marks on the target), seen from above as the shot is,
facing right (the way a sheet faces; the game mirrors a unit walking left). Its crawl is four poses (frames 1-4, then
the same four twice more); each frame's lowest row is put on the unit's ground row:

  idle    tucked (3) and the legs stretched (1), slowly;
  run     the crawl, frames 1-4 at the shot's own 90 ms;
  attack  a pounce: tucked, a column forward with the legs out, two forward with the marks showing - the bite, BITE_MS
          in - one back, and tucked where it stood;
  hit     tucked, a column back;
  dead    tucked, the legs flung out (1), gone.
The add-on's unit attack lands on the bite (league_elise src/lib.rs: SL_ACT / SL_LANDS, checked by its make_override.py
against this sheet's .fanim).
--check: exit 1 when the sheet in the repo is not what this writes. --preview: the frames at 8x on the ground line.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_frames as U  # noqa: E402

FX = os.path.join(U.EFFECTS, "league_elise_fx")
OUT = os.path.join(U.CHAMPIONS, "league_elise_spiderling")
IDLE_MS = (320, 140, 320, 140)
RUN_MS = 90
ATTACK_MS = (80, 60, 110, 80, 70)
BITE_MS = sum(ATTACK_MS[:2])
HIT_MS = 100
DEAD_MS = (90, 90, 60)


def build():
    raw = U.frames_of(FX, "w_spider")
    if len(raw) != 13 or any(raw[k][1] != RUN_MS for k in range(1, 12)):
        sys.exit("w_spider is no longer 13 frames crawling at 90 ms: read the picture again")
    crawl = [U.to_feet(f) for f, _ in raw]
    for k in range(1, 5):
        if not U.np.array_equal(raw[k][0], raw[k + 4][0]):
            sys.exit(f"w_spider {k}: the crawl no longer repeats every four frames: read the picture again")
    tucked, out_, marks, wide = crawl[3], crawl[1], crawl[2], crawl[4]
    return {
        "idle": list(zip([tucked, out_, tucked, out_], IDLE_MS)),
        "run": [(crawl[k], RUN_MS) for k in (1, 2, 3, 4)],
        "attack": list(zip([tucked, U.shift(out_, 1, 0), U.shift(wide, 2, 0), U.shift(marks, 1, 0), tucked], ATTACK_MS)),
        "hit": [(U.shift(tucked, -1, 0), HIT_MS)],
        "dead": list(zip([tucked, out_, U.blank()], DEAD_MS)),
    }


if __name__ == "__main__":
    U.run("league_elise_spiderling", OUT, build)

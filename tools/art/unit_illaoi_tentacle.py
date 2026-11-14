#!/usr/bin/env python3
"""Illaoi's tentacle as a unit: league/champions/league_illaoi_tentacle_body#sheet.png + #anim.fanim.

    python tools/art/unit_illaoi_tentacle.py [--check] [--preview <png>]

The add-on league_illaoi gives each tentacle it grows a body through the mod API's spawn_unit under this name (round 2 of
"summons as real units", 2026-11-14): the unit can be targeted and killed, the add-on's native code keeps striking (a
tentacle strikes only on her abilities' word, League's). Not the effect sheet's name (league_illaoi_tentacle):
league.dll finds dense frames by the resource's last name alone, and that one is a registered EFFECTS row.
Every frame is the tentacle the add-on draws today (league/effects/league_illaoi_tentacle, its hd_ tags: PPU 1.5, which
the game draws a square a game pixel - so these dense squares as plain 1x frames keep the tentacle the size and the look
it has on screen today, no league.dll row), every frame lifted alike so the swaying tentacle's base is on the unit's
ground row:

  idle    its sway, two frames at 600 ms (the add-on's sway picture);
  run     the same (the body has move speed 1: it does not walk);
  attack  a twitch, the sway's two frames quick (the body never strikes - its attack reaches nowhere - the add-on's lash
          picture slams the one it strikes);
  hit     the first sway frame, a column back;
  dead    it sinks (the sink frame), gone.
Its rise is the add-on's rise picture, played where it grows while the body waits banished (league_illaoi src/lib.rs).
--check: exit 1 when the sheet in the repo is not what this writes. --preview: the frames at 8x on the ground line.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_frames as U  # noqa: E402

FX = os.path.join(U.EFFECTS, "league_illaoi_tentacle")
OUT = os.path.join(U.CHAMPIONS, "league_illaoi_tentacle_body")
SWAY_MS = 600
TWITCH_MS = 100
HIT_MS = 100
SINK_MS = 300


def build():
    sway = U.frames_of(FX, "hd_sway")
    sink = U.frames_of(FX, "hd_sink")
    if len(sway) != 2 or any(ms != SWAY_MS for _, ms in sway) or len(sink) != 1:
        sys.exit("the tentacle's sway is no longer two frames of 600 ms and one sink frame: read the picture again")
    lift = U.FEET - U.lowest(sway[0][0])
    if U.lowest(sway[1][0]) != U.lowest(sway[0][0]):
        sys.exit("the sway's two frames stand on different rows: read the picture again")
    s0, s1 = (U.shift(f, 0, lift) for f, _ in sway)
    down = U.under_ground_cut(U.shift(sink[0][0], 0, lift))
    return {
        "idle": [(s0, SWAY_MS), (s1, SWAY_MS)],
        "run": [(s0, SWAY_MS), (s1, SWAY_MS)],
        "attack": [(s1, TWITCH_MS), (s0, TWITCH_MS)],
        "hit": [(U.shift(s0, -1, 0), HIT_MS)],
        "dead": [(down, SINK_MS), (U.blank(), 60)],
    }


if __name__ == "__main__":
    U.run("league_illaoi_tentacle_body", OUT, build)

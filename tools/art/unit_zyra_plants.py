#!/usr/bin/env python3
"""Zyra's plants as units: league/champions/league_zyra_spitter and league_zyra_lasher (#sheet.png + #anim.fanim).

    python tools/art/unit_zyra_plants.py [--check] [--preview <png>]      (both sheets; the preview gets _spitter / _lasher)

The add-on league_zyra gives each of its plants a body through the mod API's spawn_unit under these names (round 2 of
"summons as real units", 2026-11-14): the unit can be targeted and killed, the add-on's native code keeps striking. Every
frame is the plant's own life picture (league/effects/league_zyra_big, tags t_plant / v_plant: its plain 1x frames - the
sheet is an effects-PPU sheet the game draws at the 1x size, so the unit is the size the plants have on screen today,
no league.dll row), facing right (the game mirrors a unit facing left). The life is: the seed, the sprout, grown, then
four times the strike (the spit's glow / the lash) and four swaying frames, then the shake and the wither. The plant's
base is already on the 1x frames' row 11, a unit's ground row (checked):

  idle    the four swaying frames at the life's 212 ms;
  run     the same (the body has move speed 1: it does not walk);
  attack  grown upright, the strike (the spit's glow / the lash) - where the add-on's harmless unit attack lands
          (league_zyra src/lib.rs: TP_ACT / TP_LANDS, VP_ACT / VP_LANDS, checked by its make_override.py) - and the
          first sway frame;
  hit     the first sway frame, a column back;
  dead    the life's end: the shake, the wither, the stump, gone.
--check: exit 1 when a sheet in the repo is not what this writes. --preview: the frames at 8x on the ground line.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_frames as U  # noqa: E402

BIG = os.path.join(U.EFFECTS, "league_zyra_big")
PLANTS = {"league_zyra_spitter": "t_plant", "league_zyra_lasher": "v_plant"}
GROWN, STRIKE, SWAY, END = 2, 3, (4, 5, 6, 7), (24, 25, 26, 27, 28, 29)
SWAY_MS = 212
ATTACK_MS = (80, 150, 100)
HIT_MS = 100


def build_one(name):
    raw = U.frames_of(BIG, PLANTS[name])
    if len(raw) != 30 or [raw[k][1] for k in (STRIKE, 8, 13, 18, 23)] != [150] * 5 or any(raw[k][1] != SWAY_MS for k in SWAY):
        sys.exit(f"{PLANTS[name]}: the life is no longer 30 frames striking every fifth: read the picture again")
    for k in (GROWN, STRIKE) + SWAY + END[:4]:
        if U.lowest(raw[k][0]) != U.FEET:
            sys.exit(f"{PLANTS[name]} {k}: the plant's base is not on row {U.FEET}: read the picture again")
    f = [U.under_ground_cut(r[0]) for r in raw]
    return {
        "idle": [(f[k], SWAY_MS) for k in SWAY],
        "run": [(f[k], SWAY_MS) for k in SWAY],
        "attack": list(zip([f[GROWN], f[STRIKE], f[SWAY[0]]], ATTACK_MS)),
        "hit": [(U.shift(f[SWAY[0]], -1, 0), HIT_MS)],
        "dead": [(f[k], raw[k][1]) for k in END] + [(U.blank(), 60)],
    }


def strike_lands(name):
    """the attack's ticks long and the tick the strike frame starts"""
    ms = [m for _, m in build_one(name)["attack"]]
    return round(sum(ms) * 60 / 1000), round(ms[0] * 60 / 1000)


if __name__ == "__main__":
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
    code = 0
    for name in PLANTS:
        if preview:
            sys.argv[sys.argv.index("--preview") + 1] = preview.replace(".png", "_" + name.split("_")[-1] + ".png")
        try:
            U.run(name, os.path.join(U.CHAMPIONS, name), lambda n=name: build_one(n))
        except SystemExit as e:
            code = code or (e.code or 0)
    print("attacks", {n: strike_lands(n) for n in PLANTS})
    sys.exit(code)

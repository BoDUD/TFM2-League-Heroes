#!/usr/bin/env python3
"""Heimerdinger's turrets as units: league/champions/league_heimerdinger_h28g and league_heimerdinger_h28q (#sheet.png +
#anim.fanim).

    python tools/art/unit_heimerdinger_turrets.py [--check] [--preview <png>]       (both sheets; the preview gets _g / _q)

The add-on league_heimerdinger spawns a body for each turret Q puts down (H-28G Evolution Turret) and for the upgraded Q's
apex (H-28Q Apex Turret) through the mod API's spawn_unit under these names (round 2 of "summons as real units",
2026-11-14): the unit gives the turret a body that can be targeted and killed, the add-on's native code keeps firing its
shots. The names are not the effect sheets' (league_heimerdinger_turret / _apex): league.dll's dense frames are found by
the resource's last name alone, and those are registered EFFECTS rows.
Every frame is the side view the add-on's copy draws today (league/effects/league_heimerdinger_turret_r / apex_r, tag
hd_idle: the turret's whole life at PPU 1.75, which the game draws a square a game pixel - so these dense squares as plain
1x frames keep the turret the size and the look it has on screen today, no league.dll row), facing right (the game
mirrors a unit facing left); the base of each frame put on the unit's ground row:

  idle    standing (the life's held frame);
  run     standing (the body has move speed 1: it does not walk);
  attack  the shot: the life's three muzzle-flash frames and standing - the flash's widest frame where the add-on's
          harmless unit attack lands (league_heimerdinger src/lib.rs: TU_ACT / TU_LANDS, XU_ACT / XU_LANDS, checked by
          its make_override.py against these sheets' .fanim);
  hit     standing, a column back;
  dead    the life's last frames - sparks, smoke, sinking (cut at the ground row) - and gone.
The muzzle (where the add-on's shots leave, forward and up of the unit's spot in game px x 1000) is the flash's first
column at its middle row: muzzles() - make_override.py checks src/lib.rs's TU_MUZZLE / XU_MUZZLE against it.
--check: exit 1 when a sheet in the repo is not what this writes. --preview: the frames at 8x on the ground line.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_frames as U  # noqa: E402

np = U.np
# name, source, (rise frames, stand, flash frames, the stand after, the fold) of the life's hd_idle
TURRETS = {
    "league_heimerdinger_h28g": ("league_heimerdinger_turret_r", dict(stand=5, flash=(6, 7, 8), fold=(54, 55, 56, 57))),
    "league_heimerdinger_h28q": ("league_heimerdinger_apex_r", dict(stand=12, flash=(9, 10, 11), fold=(69, 70, 71, 72))),
}
IDLE_MS = 600
FLASH_MS = 50
AFTER_MS = 100
HIT_MS = 100
FOLD_MS = 80


def life(source):
    return U.frames_of(os.path.join(U.EFFECTS, source), "hd_idle")


def build_one(name):
    source, at = TURRETS[name]
    raw = life(source)
    stand = raw[at["stand"]][0]
    lift = U.FEET - U.lowest(stand)
    for k in at["flash"] + at["fold"][:-1]:
        if U.lowest(raw[k][0]) != U.lowest(stand):
            sys.exit(f"{source} {k}: its base is not the standing frame's: read the life again")
    put = lambda f: U.shift(f, 0, lift)      # noqa: E731 - every frame the same lift: the base on the ground row
    s = put(stand)
    flash = [put(raw[k][0]) for k in at["flash"]]
    return {
        "idle": [(s, IDLE_MS)],
        "run": [(s, IDLE_MS)],
        "attack": [(f, FLASH_MS) for f in flash] + [(s, AFTER_MS)],
        "hit": [(U.shift(s, -1, 0), HIT_MS)],
        "dead": [(U.under_ground_cut(put(raw[k][0])), FOLD_MS) for k in at["fold"]] + [(U.blank(), FOLD_MS)],
    }


def muzzles():
    """{name: (forward, up)} in game px x 1000 from the unit's spot: the first column of the widest flash frame's pixels
    the standing frame lacks, at their middle row (the unit's spot is the frame's pivot)."""
    out = {}
    for name in TURRETS:
        tags = build_one(name)
        s = tags["idle"][0][0]
        widest = max((f for f, _ in tags["attack"][:-1]), key=lambda f: int(np.nonzero(f[..., 3])[1].max()))
        new = (widest[..., 3] > 0) & (s[..., 3] == 0)
        ys, xs = np.nonzero(new)
        x0 = int(xs.min())
        row = int(round(float(ys[xs <= x0 + 1].mean())))
        out[name] = ((x0 - U.C) * 1000, (U.C - row) * 1000)
    return out


def flash_lands(name):
    """the attack's ticks long and the tick its widest flash frame starts"""
    tags = build_one(name)
    ms = [m for _, m in tags["attack"]]
    widest = max(range(len(ms) - 1), key=lambda k: int(np.nonzero(tags["attack"][k][0][..., 3])[1].max()))
    return round(sum(ms) * 60 / 1000), round(sum(ms[:widest]) * 60 / 1000)


if __name__ == "__main__":
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
    code = 0
    for name in TURRETS:
        if preview:
            sys.argv[sys.argv.index("--preview") + 1] = preview.replace(".png", "_" + name[-1] + ".png")
        try:
            U.run(name, os.path.join(U.CHAMPIONS, name), lambda n=name: build_one(n))
        except SystemExit as e:
            code = code or (e.code or 0)
    print("muzzles", muzzles(), "attacks", {n: flash_lands(n) for n in TURRETS})
    sys.exit(code)

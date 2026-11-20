#!/usr/bin/env python3
"""Thor's sheets (the ragnarok pack, ragnarok_thor) from Codex's delivery in assets/source/thor/codex_v01.

    python tools/art/import_thor.py [--check]
    python tools/art/ppu_hd.py --hero thor          # then the hd_ and lo_ tags
    python tools/art/hero_reels.py --hero thor      # then the idle and ban/pick reels (always in this order)

Codex drew him (2026-11-20, branch codex/ragnarok-thor-assets-v01, commit 6f4833f, art 0.1.2) in Lu Bu's cells: the
soles' point at (64, 116), 55 rows from his hair to his soles, 76 to the top of Mjolnir on his shoulder. At Lu Bu's
PPU 1.65 (the two the same pixel size) he stands 33 game px to his hair, 46 to the hammer. The engine is
tools/art/ragnarok_art.py (Lu Bu's import_lubu.py tells why each step is so).

- Baked into his frames (pictures with a front and a back): the hammer swing's arc on the attack from 0.34 s (played a
  little quicker, 35 ms a frame, so all of it fits the 0.6 s attack), the ground lightning on the slam from 0.62 s (its
  ground point at (64, 116), as Codex lays it; 60 ms a frame to end with the action), the ult's charge ring stretched
  over the 1.24 s gathering and its lightning-bolt slam from 1.24 s.
- skill2, the returning hammer: Codex's frames 3-6 are his empty hands. The action tag keeps the throw (frames 0-3),
  `skill2_wait` the empty hands (4-6: the kit holds it with a CasterAnimation while the hammer is away) and
  `skill2_catch` frame 7, which the kit plays only when the hammer really comes back (the BackToCasterLinearProjectile's
  end_effects, build_thor.py, as league_sivir's Q): never on a timer.
- On units: the thunder hit (every hammer blow), the ult's ground impact (its ground line under the pivot like the
  soles), the hammer's awakening (the red cracks, centred over his head - a view is never mirrored, Codex drew it 15 px
  behind him - and lifted to the hammer's height on his shoulder).
- The flying hammer: ragnarok/effects/ragnarok_thor_proj, at 1x (the boomerang's picture, turned with its flight; it
  spins, so it reads the same both ways).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "thor", "codex_v01")
ID = "ragnarok_thor"
HERO = "thor"
PPU = 1.65                  # tools/art/ppu_hd.py PPU and addons/ragnarok/src/hd.rs HEROES say the same
SOLE = (64, 116)
GROUND = (64, 116)          # Codex's origin of the ground pictures (ground_lightning, ult_impact)
# (action, effect, from seconds, anchor from the soles, seconds a frame or None, the effect's origin in its cell)
BAKE = [
    ("attack", "hammer_swing", 0.34, (24, -40), 0.035),
    ("skill", "ground_lightning", 0.62, (35, 0), 0.06, GROUND),
    ("ult", "ult_charge", 0.0, (-15, -72), 1.24 / 8),
    ("ult", "ult_slam", 1.24, (32, -38), None),
]
# the attack is a 36-tick action (build_thor atk_dur): the blow on frame 4 at 0.42 s as drawn, the recovery shortened
RETIME = {"attack": [0.12, 0.10, 0.12, 0.08, 0.05, 0.05, 0.04, 0.04]}
# skill2: frames 0-3 the throw (the action's own tag), 4-6 the empty hands while the hammer flies (skill2_wait, looped by
# the kit's CasterAnimation until the return), 7 the catch (skill2_catch, played by the return's end_effects)
SPLIT = {"skill2": [("skill2_wait", 4), ("skill2_catch", 7)]}
TARGET_FX = {
    "thunder_hit": (64, 64),
    "ult_impact": (64, 116 - A.FEET * PPU),
    "hammer_awakening": (64, 64 + round(72 - A.FEET * PPU)),
}
PROJ_FX = {"hammer_flight": (64, 59)}

THOR = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
        "TARGET_FX": TARGET_FX, "SPLIT": SPLIT, "PROJ_FX": PROJ_FX}

if __name__ == "__main__":
    A.main(THOR, __doc__)

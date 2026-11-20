#!/usr/bin/env python3
"""Lu Bu's sheets (the ragnarok pack, ragnarok_lubu) from Codex's delivery in assets/source/lubu/codex_v02.

    python tools/art/import_lubu.py [--check]
    python tools/art/ppu_hd.py --hero lubu          # then: the hd_ and lo_ tags from the dense strips written here

Codex drew him (2026-11-20, branch codex/ragnarok-lubu-assets-v02, commit 00d78f3) in 128 x 128 cells, the soles' point
at (64, 116): 66 rows from his hair to his soles, 73 to the plume's tip - dense frames already. At PPU 1.65 (PPU
below) he stands 40 game px to his hair, 44 to the plume, a little over the base heroes' 35 (Lu Bu is a giant).

- The swing pictures go into his own frames (BAKE): the client never mirrors an effect picture and does mirror his
  frames, so a crescent drawn pointing right would point right on the red side too (SKILL.md "Both sides"). Each
  effect frame is laid on the body frame showing at that moment, its cell's centre at the soles plus Codex's anchor
  (asset_manifest_v02.json effect_anchors_logical, the way his preview.html lays them); the body frames are cut where
  an effect frame starts or ends (import_native's way), the effect over the body. The ult's charge plays stretched over
  the whole 1.18 s gathering, as in the preview.
- The 1x frames: each dense frame brought to 1 / PPU squares by pixel_down.pixelate (the pack's way: the mean of each
  square snapped to the frame's own colours, near-black squares outline), on a grid one of whose squares has the pivot
  at its centre; the pivot 11.5 game px over the soles (every base and pack sheet), at the centre of an odd frame.
- The dense frames: assets/source/ppu/lubu_<tag>.png, each round(PPU x its 1x frame), the pivot at its centre, 1 px
  gaps - ppu_hd.py reads them as drawn strips (drawn_strip) and writes hd_<tag> and lo_<tag>.
- The effects the kit plays on a unit (hit_spark on every hit, ult_impact where the cut lands, shield_break when a
  shield really breaks): ragnarok/effects/ragnarok_lubu_fx, brought to 1x by pixel_down.scale_fx (no outline, light
  has none), centred on the unit's pivot - ult_impact by its ground line (Codex's cell row 116) 11.5 game px under it,
  shield_break lifted to the chest - each with its hd_ twin (Codex's frames as drawn), an empty idle / hd_idle pair
  for the PPU: addons/ragnarok/src/hd.rs lists the sheet in EFFECTS and DRAWN_EFFECTS (view effects only).
--check rebuilds everything in memory and compares it with the files.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "lubu", "codex_v02")
ID = "ragnarok_lubu"
HERO = "lubu"
# tools/art/ppu_hd.py PPU and addons/ragnarok/src/hd.rs HEROES say the same. 1.65 at first (40 game px to his hair); the
# user, 2026-11-20, beside Thor: 「吕布是不是有点大啊 缩小一点 比雷神高出来不少」 - 1.94 = 1.65 / 0.85: the same pixels drawn
# 85 % as big, 34 game px to his hair (Thor 33), 37.6 to the plume
PPU = 1.94
FX_PPU = 1.65               # his effect sheets keep Codex's size: hits and the wave go by game distance, not by his size
SOLE = (64, 116)            # Codex's cells: the soles' point (the bottom edge of the feet's last row)
# (action, effect, from seconds, anchor from the soles in Codex's px, seconds a frame or None for the effect's own)
BAKE = [
    ("attack", "attack_swipe", 0.26, (32, -30), None),
    ("skill", "sweep", 0.42, (28, -24), None),
    ("skill2", "thrust", 0.34, (40, -28), None),
    ("ult", "ult_charge", 0.0, (12, -76), 1.18 / 8),
    ("ult", "ult_release", 1.18, (35, -43), None),
]
# the attack is a 30-tick action (build_lubu atk_dur): the recovery frames shortened so the swing still ends inside it,
# the blow on frame 4 at 0.32 s as drawn
RETIME = {"attack": [0.08, 0.08, 0.10, 0.06, 0.06, 0.04, 0.04, 0.04]}
# effects played on a unit: Codex's tag, the cell's point that goes on the unit's pivot (x, y in Codex's px)
TARGET_FX = {
    "hit_spark": (64, 64),
    "shield_break": (64, 64 + 14),          # lifted ~8 game px: on his chest, not his belt
    "ult_impact": (64, 116 - A.FEET * FX_PPU),   # the burst's ground line under the pivot like the soles
}

# Codex's first redraw round (2026-11-20, branch codex/ragnarok-lubu-req1): the halberd whole again in attack 3-5 and
# skill 4-5 (codex_v02's sheet replaced, the other 59 frames byte for byte the same) and Sky Eater's wave along the cut
# (codex_req1/ragnarok_lubu_wave_native: 8 frames of 132 x 40, drawn pointing right, top and bottom alike) - the picture
# of the ult's view-only line (build_lubu.py r_wave), at 1x like every projectile picture, its centre the line's middle
EXTRA_FX = [os.path.join(ROOT, "assets", "source", "lubu", "codex_req1", f"{ID}_wave_native")]
PROJ_FX = {"ult_wave": (66, 20)}

LUBU = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME, "TARGET_FX": TARGET_FX,
        "EXTRA_FX": EXTRA_FX, "PROJ_FX": PROJ_FX}

if __name__ == "__main__":
    A.main(LUBU, __doc__)

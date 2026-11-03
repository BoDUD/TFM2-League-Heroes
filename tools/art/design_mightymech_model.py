#!/usr/bin/env python3
"""The Mighty Mech's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_mightymech_model.py   # writes assets/source/mightymech/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-03, the review's 「B-1 40 PPU 2.0」 cell): B-1 (hd/B-1.png, Codex's raw B read on its own 7 px
squares: 136 x 115, the Ultimate form crouched with the giant sword gripped in both hands, the blade forward to the
right) at 40 game px from the spike tips to its soles, PPU 2.0 -> 80 rows, brought down by pixel_down.pixelate exactly
as the size review showed it. Its face (FACE_BOX, shown at 12x): the red helmet, the silver V horn, the silver face
plate and the yellow visor; nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_mightymech_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "mightymech", "hd")
PPU = 2.0
GAME_PX = 40
PICKS = {"idle": "B-1"}   # out -> take
FACE_BOX = (34, 20, 50, 38)   # x0, y0, x1, y1 on idle.png: the helmet, the V horn, the face plate, the visor


def main():
    for out, take in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        k = PPU * GAME_PX / d.shape[0]
        im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        if FACE_BOX:
            x0, y0, x1, y1 = FACE_BOX
            Image.fromarray(np.repeat(np.repeat(im[y0:y1, x0:x1], 12, 0), 12, 1)).save(
                lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

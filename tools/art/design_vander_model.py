#!/usr/bin/env python3
"""Vander's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_vander_model.py   # writes assets/source/vander/hd/idle.png (+ _8x)

The user's pick (2026-10-27): B-2 (hd/B-2.png, Codex's picture read on one and a half of its ~7 px squares: 87 x 86,
the low fighting stance, both fists up) at 40 game px from the top of his hair to his soles, PPU 2.0 -> 80 rows, by
pixel_down.pixelate (the size review's own reduction, so the picture is the one the user saw).
The palette cut gave his forehead and two cheek squares the waistcoat's cream (f6e8c2 / f7f1de, the nearest light
colour to Codex's skin highlight): SKIN puts the skin's light tone back on them inside the face box (the eye's white
glint at (54, 13) stays; checked at 20x).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_vander_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "vander", "hd")
PPU = 2.0
PICKS = {"idle": ("B-2", 40)}   # out -> (take, game px)
SKIN = (0xF9, 0xC1, 0x90)
FACE_BOX = (53, 7, 62, 16)       # x0, y0, x1, y1 (exclusive): forehead, brow, eyes, cheeks
CREAM = {(0xF6, 0xE8, 0xC2), (0xF7, 0xF1, 0xDE)}
GLINT = {(54, 13)}


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        if out == "idle":
            x0, y0, x1, y1 = FACE_BOX
            for y in range(y0, y1):
                for x in range(x0, x1):
                    if im[y, x, 3] and tuple(im[y, x, :3]) in CREAM and (x, y) not in GLINT:
                        im[y, x, :3] = SKIN
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

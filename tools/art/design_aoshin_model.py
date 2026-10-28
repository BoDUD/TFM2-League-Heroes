#!/usr/bin/env python3
"""Ao Shin's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_aoshin_model.py   # writes assets/source/aoshin/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-28): A-1 (hd/A-1.png, Codex's picture read on its own ~10.5 px squares: 75 x 76, hovering
upright) at 38 game px from the tips of his horns to the lowest point of his tail, PPU 2.0 -> 76 rows, by
pixel_down.pixelate (the size review's own reduction, so the picture is the one the user saw: here 1:1). His face (the
gold mask, the eyes, the horns) sits at the top right (FACE_BOX, shown at 12x); FACE: squares redrawn after a look at 12x.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_aoshin_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "aoshin", "hd")
PPU = 2.0
PICKS = {"idle": ("A-1", 38)}   # out -> (take, game px)
FACE = {}   # (x, y) -> colour
FACE_BOX = (30, 0, 75, 40)   # x0, y0, x1, y1: the mask, the horns, the eyes, the beard


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        if out == "idle":
            for (x, y), c in FACE.items():
                assert im[y, x, 3] == 255
                im[y, x, :3] = c
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

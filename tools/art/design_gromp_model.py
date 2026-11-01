#!/usr/bin/env python3
"""Gromp's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_gromp_model.py   # writes assets/source/gromp/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-01): A-1 (hd/A-1.png, Codex's first A read on its own 12 px squares: 105 x 54, TFT's idle at
3/4, crouched, the big olive belly at the lower right, the flat orange head on top of it with the yellow-green eyes and
the pale tusks, the purple and blue mushrooms on its back) at 32 game px from the mushroom caps to its feet, PPU 1.69
-> A-1's own 54 rows, kept 1:1 (no reduction; 32.0 game px). Its face sits at the upper right (FACE_BOX, shown at
12x); nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_gromp_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "gromp", "hd")
PPU = 1.69
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (44, 0, 92, 30)   # x0, y0, x1, y1: the head, the blue mushroom to the tusks


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

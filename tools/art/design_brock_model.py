#!/usr/bin/env python3
"""Brock's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_brock_model.py   # writes assets/source/brock/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-02, 「A-1 44格 PPU1.16」): A-1 (hd/A-1.png, Codex's final picture A read on its own 14 px
squares: 69 x 51, TFT's idle at 3/4, the two huge fists hanging wide, the bonsai on his right shoulder, the little
hooded head between the shoulders) at 44 game px from the bonsai top to his soles, PPU 51 / 44 = 1.16 -> A-1's own 51
rows, kept 1:1 (no reduction). Its face (FACE_BOX, shown at 12x): the grey-blue hood round the orange face plate, the two
3x3 ring eyes design_brock_hd redrew at (37, 17) and (41, 17); nothing more is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_brock_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "brock", "hd")
PPU = 1.16
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (30, 8, 48, 26)   # x0, y0, x1, y1: the hood, the orange face plate, the two ring eyes


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

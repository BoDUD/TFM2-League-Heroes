#!/usr/bin/env python3
"""The Blue Sentinel's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_sentinel_model.py   # writes assets/source/sentinel/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-31): A-1 (hd/A-1.png, Codex's revised picture read on its own 8 px squares: 101 x 68, TFT's
idle at 3/4, hunched, the two huge fists hanging low, the little stone head between the shoulders) at 40 game px from
the shoulder boulders to its soles, PPU 1.7 -> A-1's own 68 rows, kept 1:1 (no reduction; 40.0 game px). Its face
sits at the upper right (FACE_BOX, shown at 12x): the pale stump head with the one cyan eye (4 x 4 squares round
(62, 22)) and the V of cyan below; nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_sentinel_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "sentinel", "hd")
PPU = 1.7
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (50, 10, 76, 36)   # x0, y0, x1, y1: the stump head, its dark notch and cyan eye, the V of cyan below


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

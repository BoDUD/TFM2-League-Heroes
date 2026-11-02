#!/usr/bin/env python3
"""Baron Nashor's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_baronnashor_model.py   # writes assets/source/baronnashor/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-03, 「A1 46」): A-1 (hd/A-1.png, Codex's picture A - the S-curved idle on the two legs the
user had it add - read on its own 11 px squares: 58 x 94) at 46 game px from the crest tips to its soles, PPU 94 / 46
= 2.04 -> A-1's own 94 rows, kept 1:1 (no reduction). Its face (FACE_BOX, shown at 12x): the blue head, the yellow
diamond eye and the side eyes, the red mouth, the ivory tusks; nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_baronnashor_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "baronnashor", "hd")
PPU = 2.04
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (14, 14, 46, 42)   # x0, y0, x1, y1: the blue head, the eyes, the red mouth, the tusks


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

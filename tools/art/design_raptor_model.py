#!/usr/bin/env python3
"""The Crimson Raptor's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_raptor_model.py   # writes assets/source/raptor/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-31): A-1 (hd/A-1.png, Codex's revised picture read on its own 11 px squares: 75 x 56, TFT's
idle at 3/4, crouched low, the red back and tail feathers behind, the purple ruff round the brown hooked-beak head) at
36 game px from the crest to its claws, PPU 1.56 -> A-1's own 56 rows, kept 1:1 (no reduction; 35.9 game px). Its
face sits at the right (FACE_BOX, shown at 12x): the bony brown head, the hooked beak, the two orange eyes and the
orange-lit mouth; nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_raptor_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "raptor", "hd")
PPU = 1.56
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (46, 18, 75, 50)   # x0, y0, x1, y1: the brown head, the hooked beak, the two orange eyes, the lit mouth


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""T-Hex's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_thex_model.py   # writes assets/source/thex/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-02, 「A-1 40px PPU1.9」): A-1 (hd/A-1.png, Codex's first picture A read on its own 10 px
squares: 101 x 76, TFT's idle at 3/4, crouched, the gatling held in front of the chest, the mouth open, the tail raised)
at 40 game px from the ear spikes to its soles, PPU 76 / 40 = 1.9 -> A-1's own 76 rows, kept 1:1 (no reduction). Its
face (FACE_BOX, shown at 12x): the copper helmet, the blue visor, the near eye (white, red rim), the jaw and teeth;
nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_thex_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "thex", "hd")
PPU = 1.9
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (58, 0, 101, 34)   # x0, y0, x1, y1: the helmet, the visor, the near eye, the jaw and teeth


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

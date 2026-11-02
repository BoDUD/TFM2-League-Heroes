#!/usr/bin/env python3
"""Murk Wolf's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_murkwolf_model.py   # writes assets/source/murkwolf/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-01): A-1 (hd/A-1.png, Codex's A read on its own 9 px squares: 83 x 60, TFT's idle at 3/4,
crouched low on four legs, the purple mane and green-black thorns on its back, the bushy tail up behind, the two heads
side by side at the right) at 36 game px from the tail tip to its claws, PPU 1.67 -> A-1's own 60 rows, kept 1:1 (no
reduction; 35.9 game px). Its faces sit at the right (FACE_BOX, shown at 12x): the pink-eared heads, the cyan eyes,
the open pink mouths with yellow fangs, the white ruffs; nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_murkwolf_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "murkwolf", "hd")
PPU = 1.67
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (38, 12, 83, 52)   # x0, y0, x1, y1: the two heads, ears to ruffs


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

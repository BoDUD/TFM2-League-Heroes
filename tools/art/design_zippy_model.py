#!/usr/bin/env python3
"""Zippy's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_zippy_model.py   # writes assets/source/zippy/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-31): A-1 (hd/A-1.png, Codex's picture read on its own 17 px squares: 52 x 83, TFT's idle at
3/4, upright on two legs, the purple bib down its front, the pink feathers at both sides of the neck, the saddle on its
back, the tail at the left) at 38 game px from the head spikes to its soles, PPU 2.2 -> A-1's own 83 rows, kept 1:1
(no reduction; 37.7 game px). Its face sits at the upper right (FACE_BOX, shown at 12x): Codex's eye already has the
heavy lid, the slit and the near-white light square step 0 asked for, so nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_zippy_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "zippy", "hd")
PPU = 2.2
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (20, 8, 52, 40)   # x0, y0, x1, y1: the head spikes' roots, the black shards, the eye, the mouth, the bib's top


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

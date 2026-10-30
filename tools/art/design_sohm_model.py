#!/usr/bin/env python3
"""Sohm's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_sohm_model.py   # writes assets/source/sohm/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-30): B-1 (hd/B-1.png, Codex's side-on picture read on its own 8 px squares: 58 x 72, floating
side-on facing right, the mane swept back, the body coiled under her, the kelp tail fin to the lower right) at 40 game
px from the antler tips to the bottom of her coil, PPU 1.8 -> 72 rows: B-1 1:1. Her head is at the top right
(FACE_BOX, shown at 12x); FACE: squares redrawn after a look at 12x.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_sohm_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "sohm", "hd")
PPU = 1.8
PICKS = {"idle": ("B-1", 40)}   # out -> (take, game px)
FACE = {(46, 30): (0x09, 0x76, 0xe1), (46, 31): (0x21, 0x41, 0x8c)}   # (x, y) -> colour: the near eye's blue iris
# (the read-back left two white squares between the lids, no iris: at 1x it read as a glint on the snout)
FACE_BOX = (24, 14, 58, 46)   # x0, y0, x1, y1: the antlers, the crown and gem, the ear, the eye, the snout


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        if rows == d.shape[0]:   # 1:1
            im = d.copy()
        else:
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

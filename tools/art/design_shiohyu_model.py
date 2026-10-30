#!/usr/bin/env python3
"""Shi Oh Yu's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_shiohyu_model.py   # writes assets/source/shiohyu/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-30): B-1 (hd/B-1.png, Codex's turned picture read on its own 8.2 px squares: 81 x 113, the idle
facing right, the two folded wings rising behind his back, the tail fluke to the lower left) at 42 game px from the
wing tips to his feet, PPU 2.46 -> 103 rows: brought down from B-1's 113 by pixel_down.pixelate (Codex's squares do
not regrid to 103 rows: every larger square reads 107). His face sits right under the gold horns (FACE_BOX, shown at
12x); FACE: squares redrawn after a look at 12x.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_shiohyu_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "shiohyu", "hd")
PPU = 2.46
PICKS = {"idle": ("B-1", 42)}   # out -> (take, game px)
# the near eye (51-55, 37-39) is orange round a pale yellow core under the teal brow: its top core square made near-white
# so it glows at game size
FACE = {(53, 38): (255, 253, 226)}   # (x, y) -> colour
FACE_BOX = (40, 24, 66, 48)   # x0, y0, x1, y1: the gold horn, the brow, the eye, the muzzle, the beard's top


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

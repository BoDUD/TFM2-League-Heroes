#!/usr/bin/env python3
"""Daeja's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_daeja_model.py   # writes assets/source/daeja/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-30): A-1 (hd/A-1.png, Codex's 3/4 picture read on its own ~10 px squares: 58 x 69, TFT's idle
facing front-right, the two wing fans rising behind his head, the tail fluke to the lower left) at 40 game px from the
wing tips to his feet, PPU 1.72 -> 69 rows: A-1's own rows, kept 1:1 (no reduction). His face sits in the middle under
the wings (FACE_BOX, shown at 12x); FACE: squares redrawn after a look at 12x.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_daeja_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "daeja", "hd")
PPU = 1.72
PICKS = {"idle": ("A-1", 40)}   # out -> (take, game px)
# the near eye (32-34, 27-28) is three flat magenta squares under the bronze mask: its middle top square made near-white
# so it glows (the far eye at 39, 27-28 stays magenta)
FACE = {(33, 27): (255, 226, 255)}   # (x, y) -> colour
FACE_BOX = (24, 16, 46, 36)   # x0, y0, x1, y1: the crests, the mask, the eyes, the mane


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

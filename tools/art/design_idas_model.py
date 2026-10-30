#!/usr/bin/env python3
"""Idas's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_idas_model.py   # writes assets/source/idas/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-30): B-1 (hd/B-1.png, Codex's side-on picture read on its own ~7 px squares: 127 x 98, TFT's
idle turned side-on facing right, the near wing-arm in front of her body, the tail reaching back to the left) at 40
game px from the top of the crest to her feet, PPU 2.45 -> 98 rows: B-1's own rows, kept 1:1 (no reduction). Her face
sits at the top right (FACE_BOX, shown at 12x); FACE: squares redrawn after a look at 12x.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_idas_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "idas", "hd")
PPU = 2.45
PICKS = {"idle": ("B-1", 40)}   # out -> (take, game px)
# the near eye (106-108, 22-24): cyan with a cyan-white glint; its middle square made near-white so it glows
FACE = {(107, 23): (232, 255, 255)}   # (x, y) -> colour
FACE_BOX = (77, 0, 127, 45)   # x0, y0, x1, y1: the crest, the eye, the horns, the snout


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

#!/usr/bin/env python3
"""Zaahen's game-size design: the user's pick of step 0 brought to its height, and the wings-spread pose on its scale.

    python tools/art/design_zaahen_model.py   # writes assets/source/zaahen/hd/{idle,wings}.png (+ _4x)

The user's pick (2026-10-26): A-2 (hd/A-2.png, Codex's selected take read on its own ~7.5 px squares: 81 x 77) at
48 game px from the tips of his horns to his soles, PPU 1.75 -> 84 rows: pixel_down.pixelate (the size review's own
step, so the picture is the one the user saw). B-2 (the wings spread, the glaive raised; made from A-2 on its squares)
by the same factor -> hd/wings.png, the design the R and revive poses take their wings from.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_zaahen_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "zaahen", "hd")
ROWS = 84   # 48 game px at PPU 1.75
# FACE (at 36x after the reduction): the face is cols 54-60, rows 21-30, the brow dark at (57-58, 23); only one red eye
# square came through (58, 24). The near eye made 2 x 1 (a dark red at 57), the far eye one square at 60 on the same row,
# a short mouth line at row 27 in the face's own shadow shade.
RED, DEEP, SHADE = (185, 6, 19), (122, 4, 14), (127, 149, 182)
FACE = {(57, 24): DEEP, (58, 24): RED, (60, 24): RED, (58, 27): SHADE, (59, 27): SHADE}   # (col, row) -> colour


def main():
    a = np.asarray(Image.open(lp(os.path.join(HD, "A-2.png"))).convert("RGBA"))
    k = ROWS / a.shape[0]
    for src, out in (("A-2", "idle"), ("B-2", "wings")):
        d = a if src == "A-2" else np.asarray(Image.open(lp(os.path.join(HD, f"{src}.png"))).convert("RGBA"))
        im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = np.asarray(Image.fromarray(im).crop(Image.fromarray(im).getbbox())).copy()
        if out == "idle":
            for (x, y), c in FACE.items():
                im[y, x] = c + (255,)
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 4, 0), 4, 1)).save(lp(os.path.join(HD, f"{out}_4x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

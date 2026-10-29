#!/usr/bin/env python3
"""Steb's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_steb_model.py   # writes assets/source/steb/hd/idle.png (+ _8x)

The user's pick (2026-10-29): A-1 (hd/A-1.png, Codex's picture read on its own ~8 px squares: 80 x 106, the idle, a
baton on his shoulder, the other pointing down) at 40 game px, PPU 2.6; A-1 has 106 rows quiff to soles (40.8 game px
at PPU 2.6), kept 1:1 - no resample, the picture the user saw. FACE redraws squares where a part came back thin.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_steb_hd import lp  # noqa: E402
from review_steb_size import hair_top  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "steb", "hd")
PPU = 2.6
PICKS = {"idle": ("A-1", 106 / 2.6)}   # out -> (take, game px from the top of his quiff to his soles: 1:1)
# (x, y) -> colour, on the idle: both eyes came back one row of white with a one-square iris; each iris made 2x2 (its
# own dark blue over cyan, the rows 18-19 of both eyes), the near eye's white beside it (checked at 12x, 2026-10-29)
FACE = {(52, 18): "decdd8", (52, 19): "decdd8", (53, 18): "275c8e", (54, 18): "275c8e", (53, 19): "1aa2c8",
        (54, 19): "1aa2c8",
        (58, 18): "decdd8", (59, 18): "275c8e", (60, 18): "275c8e", (59, 19): "1aa2c8", (60, 19): "1aa2c8"}


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        body = d.shape[0] - hair_top(d)
        im = d if body == rows else PD.pixelate(d, rows / body, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))[0]
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        for (x, y), c in FACE.items():
            im[y, x] = [int(c[i:i + 2], 16) for i in (0, 2, 4)] + [255]
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

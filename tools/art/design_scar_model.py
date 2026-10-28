#!/usr/bin/env python3
"""Scar's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_scar_model.py   # writes assets/source/scar/hd/idle.png (+ _8x)

The user's pick (2026-10-28): B-1 (hd/B-1.png, Codex's picture read on ~12.4 px squares: 91 x 82, the spear guard,
point forward) at 38 game px from the top of his mohawk to his soles, PPU 2.0 -> 76 rows, by pixel_down.pixelate (the
size review's own reduction, so the picture is the one the user saw). FACE redraws squares the reduction smeared.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_scar_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "scar", "hd")
PPU = 2.0
PICKS = {"idle": ("B-1", 38)}   # out -> (take, game px)
FACE = {}  # (x, y) -> colour, on the idle


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        for (x, y), c in FACE.items():
            im[y, x] = [int(c[i:i + 2], 16) for i in (0, 2, 4)] + [255]
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

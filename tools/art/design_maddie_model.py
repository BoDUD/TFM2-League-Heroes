#!/usr/bin/env python3
"""Maddie's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_silco_model.py   # writes assets/source/maddie/hd/idle.png (+ _8x)

The user's pick (2026-10-27): A-1 (hd/A-1.png, Codex's picture read on its own ~13.2 px squares: 45 x 59, the rifle on
her shoulder) at 38 game px from the top of her beret to her soles, PPU 1.5 -> 57 rows, by pixel_down.pixelate (the
size review's own reduction, so the picture is the one the user saw).
The reduction left her far eye (image right) a red and a brown square over two grey-blues and her mouth one grey
square: FACE redraws them on the near eye's pattern - the lash row near-black, under it a white and a blue - and the
mouth her lip red (checked at 20x).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_maddie_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "maddie", "hd")
PPU = 1.5
PICKS = {"idle": ("A-1", 38)}   # out -> (take, game px)
FACE = {(35, 10): (9, 2, 15), (36, 10): (9, 2, 15), (35, 11): (247, 247, 249), (36, 11): (24, 41, 125),
        (31, 15): (207, 57, 24)}   # (x, y) -> colour


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        if out == "idle":
            for (x, y), c in FACE.items():
                assert im[y, x, 3] == 255
                im[y, x, :3] = c
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

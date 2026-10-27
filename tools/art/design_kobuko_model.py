#!/usr/bin/env python3
"""Kobuko's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_kobuko_model.py   # writes assets/source/kobuko/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-27): A-1 (hd/A-1.png, Codex's picture read on its own ~9.75 px squares: 99 x 105, stroking
his beard) at 40 game px from the top of his topknot to his soles, PPU 2.0 -> 80 rows, by pixel_down.pixelate (the
size review's own reduction, so the picture is the one the user saw). FACE: squares redrawn after a look at 12x.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_kobuko_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "kobuko", "hd")
PPU = 2.0
PICKS = {"idle": ("A-1", 40)}   # out -> (take, game px)
FACE = {}   # (x, y) -> colour


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
        Image.fromarray(np.repeat(np.repeat(im[:34], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

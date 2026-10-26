#!/usr/bin/env python3
"""Norra's game-size design: the user's picks of step 0 brought to their heights.

    python tools/art/design_norra_model.py   # writes assets/source/norra/hd/idle.png and yuumi.png (+ _4x)

The user's picks (2026-10-26): Norra = A-1 (hd/A-1.png, Codex's first, fine take read on its own 10 px squares:
63 x 101) at 36 game px from the top of her hat to her soles, PPU 2.0 -> 72 rows; Yuumi on her book = B-1 (70 x 65)
at 17 game px, the same PPU -> 34 rows. Both by pixel_down.pixelate (the size review's own reduction, so the pictures
are the ones the user saw).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_norra_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "norra", "hd")
PPU = 2.0
PICKS = {"idle": ("A-1", 36), "yuumi": ("B-1", 17)}   # out -> (take, game px)


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

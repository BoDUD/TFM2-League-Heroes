#!/usr/bin/env python3
"""Loris's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_loris_model.py   # writes assets/source/loris/hd/idle.png (+ _8x)

The user's pick (2026-10-27): B-1 (hd/B-1.png, Codex's picture read on its own ~11.2 px squares: 50 x 85, the shield
upright at his side, a fist at his chest) at 42 game px from the top of his hair to his soles, PPU 2.0 -> 84 rows, by
pixel_down.pixelate (the size review's own reduction, so the picture is the one the user saw).
The reduction kept the near eye (lash row over a white and a dark square) but no far eye on the bridge of his nose:
FACE puts one in on the near eye's pattern, a near-black over a dark brown square, under the end of his brow
(checked at 12x).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_loris_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "loris", "hd")
PPU = 2.0
PICKS = {"idle": ("B-1", 42)}   # out -> (take, game px)
FACE = {(32, 11): (3, 2, 2), (32, 12): (61, 38, 39), (32, 9): (61, 38, 39)}   # (x, y) -> colour


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

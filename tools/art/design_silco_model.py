#!/usr/bin/env python3
"""Silco's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_silco_model.py   # writes assets/source/silco/hd/idle.png (+ _8x)

The user's picks (2026-10-27): A-1 (hd/A-1.png, Codex's picture read on its own ~9.8 px squares: 48 x 88, leaning on
the cane, a Shimmer vial raised) at 40 game px from the top of his hair to his soles, PPU 2.0 -> 80 rows, by
pixel_down.pixelate (the size review's own reduction, so the picture is the one the user saw).
The reduction lost his scarred far eye (image right, Codex's orange 2x2 under a dark red scar): SCAR puts it back -
the glowing eye beside the near one's row, the scar over and under it (checked at 20x).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_silco_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "silco", "hd")
PPU = 2.0
PICKS = {"idle": ("A-1", 40)}   # out -> (take, game px)
SCAR = {(26, 14): (255, 112, 32), (26, 13): (122, 30, 42), (26, 15): (107, 35, 64)}   # (x, y) -> colour


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        if out == "idle":
            for (x, y), c in SCAR.items():
                assert im[y, x, 3] == 255
                im[y, x, :3] = c
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

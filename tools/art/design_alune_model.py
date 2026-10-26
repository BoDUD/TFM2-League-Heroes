#!/usr/bin/env python3
"""Alune's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_alune_model.py   # writes assets/source/alune/hd/idle.png (+ _8x)

The user's picks (2026-10-26): A-1 (hd/A-1.png, Codex's picture read on its own ~8 px squares: 88 x 134, riding the
crescent glaive) at 46 game px from the top of her horns to the crescent's foot, PPU 2.0 -> 92 rows, by
pixel_down.pixelate (the size review's own reduction, so the picture is the one the user saw).
The big horn's tip came out as a bare outline trailing up three rows past its last violet square (rows 0-2): those
squares go, one outline square caps the tip (TIP_OFF / TIP_CAP, checked at 16x).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_alune_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "alune", "hd")
PPU = 2.0
PICKS = {"idle": ("A-1", 46)}   # out -> (take, game px)
TIP_OFF = [(37, 0), (38, 0), (38, 1), (39, 1), (38, 2), (39, 2)]
TIP_CAP = (40, 2)


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        if out == "idle":
            for x, y in TIP_OFF:
                im[y, x] = 0
            assert im[TIP_CAP[1], TIP_CAP[0], 3] == 255
            im = np.asarray(Image.fromarray(im).crop(Image.fromarray(im).getbbox())).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

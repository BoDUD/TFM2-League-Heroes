#!/usr/bin/env python3
"""Sevika's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_sevika_model.py   # writes assets/source/sevika/hd/idle.png (+ _8x)

The user's pick (2026-10-29): A-1 (hd/A-1.png, Codex's picture read on its own ~17.5 px squares: 53 x 70, the standing
guard, the arm hanging) at 38 game px, PPU 1.8; A-1 has 70 rows hair to soles (38.9 game px at PPU 1.8), kept 1:1 -
no resample, the picture the user saw (38 exactly would be 68 rows and smear the face). FACE redraws squares if one smears.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_sevika_hd import lp  # noqa: E402
from review_sevika_size import hair_top  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "sevika", "hd")
PPU = 1.8
PICKS = {"idle": ("A-1", 70 / 1.8)}   # out -> (take, game px from the top of her hair to her soles: 1:1)
# (x, y) -> colour, on the idle: the far eye came back one white column; drawn as the near eye is (white + grey
# iris, 2x2), its brow over it (checked at 24x, 2026-10-29)
FACE = {(28, 12): "fbfafa", (28, 13): "fbfafa", (29, 12): "343d42", (29, 13): "343d42", (28, 11): "14040d"}


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

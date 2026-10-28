#!/usr/bin/env python3
"""Violet's game-size design: the user's pick of step 0 brought to its height.

    python tools/art/design_violet_model.py   # writes assets/source/violet/hd/idle.png (+ _8x)

The user's pick (2026-10-28): B-1 (hd/B-1.png, Codex's picture read on its own ~5.5 px squares: 123 x 137, the
fighting stance, both gauntlets up) at 38 game px from the top of her hair to her soles, PPU 2.0 -> 76 rows, by
pixel_down.pixelate (the size review's own reduction, so the picture is the one the user saw).
The reduction left her eyes as a dark smear (the far one no white, the near one a grey and a slate square; checked at
28x): FACE draws them again on the grid, after the art spec - the far eye a sclera, a white glint and a dark pupil over
two squares of pale blue iris, the near one the same, a lash row of the outline over each and the dark brown brows
over them, the near brow's end tilted up.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_violet_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "violet", "hd")
PPU = 2.0
PICKS = {"idle": ("B-1", 38)}   # out -> (take, game px)
LASH, SCLERA, GLINT, PUPIL, IRIS = "0f0411", "afbcc2", "f0f4f8", "1f2a44", "5b86b8"
SKIN, BROW = "f5ddbf", "734639"
FACE = {  # (x, y) -> colour, on the 68 x 76 idle
    **{(x, 16): LASH for x in range(34, 38)}, **{(x, 16): LASH for x in range(41, 44)},
    (34, 17): SCLERA, (35, 17): GLINT, (36, 17): PUPIL, (37, 17): SKIN, (35, 18): IRIS, (36, 18): IRIS, (37, 18): SKIN,
    (41, 17): SCLERA, (42, 17): GLINT, (43, 17): PUPIL, (41, 18): SKIN, (42, 18): IRIS, (43, 18): IRIS,
    **{(x, 15): BROW for x in range(35, 39)}, (41, 15): BROW, (42, 15): BROW, (43, 14): BROW,
}


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

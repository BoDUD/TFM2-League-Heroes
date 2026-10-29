#!/usr/bin/env python3
"""Smeech's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_smeech_model.py   # writes assets/source/smeech/hd/idle.png (+ _8x)

The user's pick (2026-10-29): B-1 (hd/B-1.png, Codex's refined picture read on its own ~6 px squares: 128 x 87, the
ambush crouch, claws spread) at 36 game px from the top of his hat to his soles, PPU 2.4 -> 87 rows: the picture as it
is, one pixel a square (rows = its own height, no reduction). FACE redraws the eyes: the read left a pink-red pupil in
the near eye and the far one's on the rim; both now a near-black pupil on the same row (39) in pale yellow whites.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_smeech_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "smeech", "hd")
PPU = 2.4
PICKS = {"idle": ("B-1", None)}   # out -> (take, game px; None: as it is)
FACE = {  # (x, y) -> colour, on the idle
    (83, 38): "efdfa2", (83, 39): "07060a",                       # near eye: whites 82-84 / 81-85, pupil
    (96, 38): "efdfa2", (97, 38): "efdfa2", (98, 38): "3e2320",   # far eye: whites 96-97 / 95, 97, pupil 96
    (96, 39): "07060a",
}


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        if px is None:
            im = d.copy()
        else:
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

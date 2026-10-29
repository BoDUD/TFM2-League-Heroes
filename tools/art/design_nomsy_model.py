#!/usr/bin/env python3
"""Nomsy's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_nomsy_model.py   # writes assets/source/nomsy/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-29): A-1 (hd/A-1.png, Codex's picture read on its own ~7.5 px squares: 129 x 94, TFT's idle
at 3/4 on all fours, the near wing reaching back to the left, the far wing behind her head) at 36 game px from the top
of the far wing to her feet, PPU 2.6 -> 94 rows: A-1's own rows, kept 1:1 (no reduction). Her face sits at the top
right (FACE_BOX, shown at 12x); FACE: squares redrawn after a look at 12x.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_nomsy_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "nomsy", "hd")
PPU = 2.6
PICKS = {"idle": ("A-1", 36)}   # out -> (take, game px)
# the near pupil: Codex's ran into the lid line (x 91-94, row 30); a 2x2 black pupil inside the green iris, the
# highlight (88-89, 29) kept
FACE = {(89, 30): (13, 6, 30), (90, 30): (13, 6, 30), (89, 31): (13, 6, 30), (90, 31): (13, 6, 30)}   # (x, y) -> colour
FACE_BOX = (70, 0, 129, 50)   # x0, y0, x1, y1: the head spikes, the eyes, the tusks, the mouth


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        if rows == d.shape[0]:   # 1:1
            im = d.copy()
        else:
            im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
            im = Image.fromarray(im)
            im = np.asarray(im.crop(im.getbbox())).copy()
        if out == "idle":
            for (x, y), c in FACE.items():
                assert im[y, x, 3] == 255
                im[y, x, :3] = c
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

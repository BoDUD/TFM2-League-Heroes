#!/usr/bin/env python3
"""Terra's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_terra_model.py   # writes assets/source/terra/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-31): A-1 (hd/A-1.png, Codex's picture read on its own 14 px squares: 86 x 52, TFT's idle at
3/4, crouched on all fours, the wings folded back over her, the tail's stone fan at the far left) at 36 game px from
the wing-bone tips to her soles, PPU 1.45 -> 52 rows: A-1's own rows, kept 1:1 (no reduction). Her face sits at the
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
from design_terra_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "terra", "hd")
PPU = 1.45
PICKS = {"idle": ("A-1", 36)}   # out -> (take, game px)
# the near eye: Codex's 2x2 glowing yellow had no light square (step 0 asked one near-white square in it): the upper
# right one, toward her snout, pale
FACE = {(75, 28): (255, 255, 214)}   # (x, y) -> colour
FACE_BOX = (56, 12, 86, 48)   # x0, y0, x1, y1: the brow plates, the eye, the fangs, the jaw


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

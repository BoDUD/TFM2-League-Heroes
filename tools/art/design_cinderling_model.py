#!/usr/bin/env python3
"""The Cinderling's (绯红树怪) game-size design: the user's pick of step 0 at its height.

    python tools/art/design_cinderling_model.py   # writes assets/source/cinderling/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-02, 「A 30 PPU 2.33」): A-1 (hd/A-1.png, Codex's first raw A read on its own 8 px squares:
94 x 70, TFT's idle at 3/4, crouched on all fours, the wooden mask at the front between the front legs, the tall
leaf spines on the back) at 30 game px from the tallest leaf to the claws, PPU 2.33 -> 70 rows: A-1 itself, 1:1 (the
pixelate below changes nothing at k = 1; it stays for a later height). Its face (FACE_BOX, shown at 12x): the big
glowing eye on the mask's left, the G spiral on its right, the row of fangs below.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_cinderling_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "cinderling", "hd")
PPU = 2.33
HEIGHT = 30   # game px
PICKS = {"idle": "A-1"}   # out -> take
FACE_BOX = (40, 26, 80, 60)   # x0, y0, x1, y1: the mask, its eye, its spiral and its fangs


def main():
    for out, take in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        rows = round(HEIGHT * PPU)
        if rows == d.shape[0]:
            im = d
        else:
            im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
            ys, xs = np.nonzero(im[..., 3] > 0)
            im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

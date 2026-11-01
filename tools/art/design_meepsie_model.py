#!/usr/bin/env python3
"""Meepsie's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_meepsie_model.py   # writes assets/source/meepsie/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-01): A-1 (hd/A-1.png, Codex's original A read on its own 7 px squares: 137 x 115, the idle
stance at 3/4 facing right, the headless moon-rock golem with the leaf-and-mushroom cap, the huge cratered fists and the
crater cockpit where the green meep pilot sits) at 40 game px from the mushroom tops to its soles, PPU 2.875 -> A-1's
own 115 rows, kept 1:1 (no reduction). The pilot's face (FACE_BOX, shown at 12x) read back whole: two dark 5 x 6 eyes
with a white highlight each and a small dark smile, so nothing is redrawn. Specks (opaque bits of under SPECK pixels
apart from the body, left by the draft's soft edge) go.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_meepsie_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "meepsie", "hd")
PPU = 2.875
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (68, 22, 92, 50)   # x0, y0, x1, y1: the pilot's antenna, eyes, smile and hands
SPECK = 6


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        lab, n = ndimage.label(im[..., 3] > 0, structure=np.ones((3, 3)))
        sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
        for i, sz in enumerate(sizes, 1):
            if sz < SPECK:
                im[lab == i] = 0
        ys, xs = np.nonzero(im[..., 3] > 0)
        im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})", "specks", int((sizes < SPECK).sum()))


if __name__ == "__main__":
    main()

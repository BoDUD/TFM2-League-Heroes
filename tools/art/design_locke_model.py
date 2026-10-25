#!/usr/bin/env python3
"""Locke's game-size design: the user's pick of step 0 brought to its height, its face squares fixed.

    python tools/art/design_locke_model.py   # writes assets/source/locke/hd/idle.png (+ _4x)

The user's pick (2026-10-26): A-1 (hd/A-1.png, Codex's first, fine take read on its own 5.5 px squares: 98 x 164) at
44 game px from the top of his hair to his soles, PPU 2.0 -> 88 rows: pixel_down.pixelate (the size review's own
reduction, so the picture is the one the user saw), 54 x 88.
FACE: at 16x the near lens reads (cols 36-38, rows 13-16: the dark purple 5a1c5c rim over the magenta 8d056d / b60480),
the far one a dark blob (cols 42-43: one magenta square); its lower two rows take the near lens's magenta b60480 so
both read as round purple lenses at the same height. The grin (the white e4f1f2 teeth, row 20) stays as drawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_locke_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "locke", "hd")
ROWS = 88   # 44 game px at PPU 2.0
LENS = (182, 4, 128)   # b60480, the near lens's magenta
FACE = {(42, 15): LENS, (43, 15): LENS, (42, 16): LENS}   # (col, row) -> colour


def main():
    d = np.asarray(Image.open(lp(os.path.join(HD, "A-1.png"))).convert("RGBA"))
    im, _ = PD.pixelate(d, ROWS / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    im = np.asarray(Image.fromarray(im).crop(Image.fromarray(im).getbbox())).copy()
    for (x, y), c in FACE.items():
        im[y, x] = c + (255,)
    Image.fromarray(im).save(lp(os.path.join(HD, "idle.png")))
    Image.fromarray(np.repeat(np.repeat(im, 4, 0), 4, 1)).save(lp(os.path.join(HD, "idle_4x.png")))
    print("idle", im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

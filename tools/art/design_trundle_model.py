#!/usr/bin/env python3
"""Trundle's game-size design: the user's pick of step 0 taken as drawn, its face squares fixed.

    python tools/art/design_trundle_model.py   # writes assets/source/trundle/hd/idle.png (+ _4x)

The user's pick (2026-10-25): A-1 (hd/A-1.png, Codex's first, fine take read on its own 10.3 px squares: 104 x 85) as
drawn at PPU 2.0 -> 42.5 game px from the top of his mane to his feet / the club's lowest point; no step-1 redraw: it is
the design itself (Yorick's, Belveth's and Singed's way of registering a PPU from the design's own rows).
FACE: the eyes at 16x read as a 2 x 2 blue (near, cols 65-67 rows 31-32: the deep blue 0b7cd1 and the light 42d9f3 /
3ec0f9) and a 1 x 1 light blue (far, col 72 row 32, a dark socket blue at col 73); the far one is widened to 2 x 1
(col 73 in the near eye's deep blue) so both read as eyes.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_trundle_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "trundle", "hd")
DEEP = (11, 124, 209)   # the near eye's deep blue, as drawn
FACE = {(73, 32): DEEP}   # (col, row) -> colour


def main():
    d = np.asarray(Image.open(lp(os.path.join(HD, "A-1.png"))).convert("RGBA")).copy()
    for (x, y), c in FACE.items():
        d[y, x] = c + (255,)
    Image.fromarray(d).save(lp(os.path.join(HD, "idle.png")))
    Image.fromarray(np.repeat(np.repeat(d, 4, 0), 4, 1)).save(lp(os.path.join(HD, "idle_4x.png")))
    print("idle", d.shape[1], "x", d.shape[0])


if __name__ == "__main__":
    main()

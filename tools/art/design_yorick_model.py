#!/usr/bin/env python3
"""Yorick's game-size design: the user's pick of step 0 taken as drawn, its face squares fixed.

    python tools/art/design_yorick_model.py   # writes assets/source/yorick/hd/idle.png (+ _4x)

The user's pick (2026-10-25): A-2 (hd/A-2.png, Codex's coarser take read on its own 10.6 px squares: 74 x 83) at 48
game px from the shovel's tip to his boots, PPU 1.75 -> 84 rows; A-2 is 83 rows as drawn (PPU 1.73 at 48, 47.4 game
px at 1.75), so no step-1 redraw: it is the design itself (Belveth's and Singed's way of registering a PPU from the
design's own rows). The summons stay B-2 (hd/B-2.png) as the look for the effects pack.
FACE: the eyes at 14x read as one 2 x 1 cyan glow (near, cols 45-46) and one 1 x 1 (far, col 49) on row 29; the far
one is widened to 2 x 1 (cols 48-49) so both glow alike, the nose bridge (col 47, his skin's dark shade) between them.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_yorick_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "yorick", "hd")
GLOW, CORE = (71, 250, 253), (10, 226, 238)   # the eyes' two cyans, as drawn in the near eye
FACE = {(48, 29): CORE, (49, 29): GLOW}       # (col, row) -> colour


def main():
    d = np.asarray(Image.open(lp(os.path.join(HD, "A-2.png"))).convert("RGBA")).copy()
    for (x, y), c in FACE.items():
        d[y, x] = c + (255,)
    Image.fromarray(d).save(lp(os.path.join(HD, "idle.png")))
    Image.fromarray(np.repeat(np.repeat(d, 4, 0), 4, 1)).save(lp(os.path.join(HD, "idle_4x.png")))
    print("idle", d.shape[1], "x", d.shape[0])


if __name__ == "__main__":
    main()

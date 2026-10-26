#!/usr/bin/env python3
"""Skarner's game-size design: the user's pick of step 0 taken as drawn, its face squares fixed.

    python tools/art/design_skarner_model.py   # writes assets/source/skarner/hd/{idle,rock}.png (+ _4x)

The user's pick (2026-10-26): A (hd/A.png, Codex's picture read on its own 8.7 px squares: 80 x 59) as drawn at PPU 1.75
-> 33.7 game px from the top of his highest stinger to his feet, ~46 wide; no step-1 redraw: it is the design itself
(Yorick's and Trundle's way). B (hd/B.png, read on 9.7 px squares: 77 x 75) is the same design holding the boulder in
his tails - rock.png, the design of the boulder poses (Q's three empowered attacks, the throw).
FACE: under the silver hood the eyes read as a 2 x 1 cyan (near, A cols 52-53 row 49; B cols 50-51 row 64) and a 1 x 1
cyan (far, A col 57, B col 55); the far one is widened to 2 x 1 (A col 56, B col 54: the outline black between them) so
both read as eyes.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_skarner_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "skarner", "hd")
CYAN = (0x47, 0xDB, 0xE4)   # the eyes' cyan, as drawn
# out name -> (the step-0 readback, {(col, row): colour})
DESIGNS = {"idle": ("A", {(56, 49): CYAN}), "rock": ("B", {(54, 64): CYAN})}


def main():
    for out, (src, face) in DESIGNS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{src}.png"))).convert("RGBA")).copy()
        for (x, y), c in face.items():
            d[y, x] = c + (255,)
        Image.fromarray(d).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(d, 4, 0), 4, 1)).save(lp(os.path.join(HD, f"{out}_4x.png")))
        print(out, d.shape[1], "x", d.shape[0])


if __name__ == "__main__":
    main()

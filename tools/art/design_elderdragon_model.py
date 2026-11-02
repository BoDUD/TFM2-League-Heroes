#!/usr/bin/env python3
"""The Elder Dragon's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_elderdragon_model.py   # writes assets/source/elderdragon/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-01): A-1 (hd/A-1.png, Codex's initial A read on its own 7.5 px squares: 167 x 125, the idle
stance at 3/4, low on four legs, the wings half spread and raised, the tail curled up, the white crystal mane, the
blue horns and the glowing cyan mouth) at 44 game px from the highest wing tip to its claws, PPU 2.84 -> A-1's own 125
rows, kept 1:1 (no reduction; 44.0 game px). Its face sits at the right (FACE_BOX, shown at 12x): the dark beak-like
jaw, the two blue horns, the near eye and the glowing mouth. Read back, the eye came out one cyan square and the
mouth's dark fangs were lost: EYE redraws the near eye on the grid (2 x 3: cyan, one near-white highlight, a dark rim
over it and a dark line under it), FANGS puts the dark fangs back along the mouth's top and bottom edges (the draft's
own colours). Specks (opaque bits of under SPECK pixels apart from the body, left by the draft's soft edge) go.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_elderdragon_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "elderdragon", "hd")
PPU = 2.84
PICKS = {"idle": "A-1"}   # out -> take, 1:1
FACE_BOX = (100, 70, 152, 118)   # x0, y0, x1, y1: the jaw, the two horns, the cyan eyes, the glowing mouth
CYAN, GLOW, WHITE = (4, 243, 211), (4, 244, 246), (247, 247, 247)   # the draft's own mouth / eye colours
DARK, NAVY, FANG = (11, 3, 17), (27, 33, 58), (58, 37, 76)
EYE = {(124, 95): CYAN, (125, 95): WHITE, (126, 95): CYAN, (124, 96): GLOW, (125, 96): GLOW, (126, 96): CYAN,
       (125, 94): DARK, (126, 94): DARK, (124, 97): NAVY, (125, 97): NAVY, (126, 97): NAVY}
FANGS = {(125, 99): FANG, (127, 99): FANG, (129, 99): FANG, (130, 106): FANG, (132, 106): FANG}
SPECK = 6


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        lab, n = ndimage.label(im[..., 3] > 0, structure=np.ones((3, 3)))
        sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
        for i, sz in enumerate(sizes, 1):
            if sz < SPECK:
                im[lab == i] = 0
        for (x, y), c in {**EYE, **FANGS}.items():
            im[y, x] = (*c, 255)
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

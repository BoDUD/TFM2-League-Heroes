#!/usr/bin/env python3
"""The Rift Herald's (峡谷先锋) game-size design: the user's pick of step 0 at its height.

    python tools/art/design_riftherald_model.py   # writes assets/source/riftherald/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-02, 「A-1，44 像素，PPU 2.0」): A-1 (hd/A-1.png, Codex's first raw A read on its own 8 px
squares: 136 x 117, TFT's idle at 3/4, hunched under the domed shell, both pincers low, the tail curled behind) at 44 game
px from the shell's top to its soles, PPU 2.0 -> 88 rows, brought down by pixel_down.pixelate about the soles' middle.
Its face (FACE_BOX, shown at 12x): the magenta eyes under the shell's rim, the golden tusk curving up beside them. Brought
to 88 rows each eye was one or two magenta squares smeared into the face's blues (「脸部给我弄好看点」, the Codex face rule):
EYES redraws them on the design's own squares - the far eye 3 x 2, the near one 2 x 2 in its cyan bulb, each a magenta with
its brightest square up front, the face's dark lines round them kept.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_riftherald_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "riftherald", "hd")
PPU = 2.0
HEIGHT = 44   # game px
PICKS = {"idle": "A-1"}   # out -> take
FACE_BOX = (60, 18, 104, 56)   # x0, y0, x1, y1: the eyes, the fangs and the near tusk
MAG, LIT, DIM = (222, 58, 205), (255, 150, 242), (150, 34, 140)
EYES = {   # (x, y) -> colour, on the 88-row design
    (75, 39): DIM, (76, 39): LIT, (77, 39): MAG, (75, 40): DIM, (76, 40): MAG, (77, 40): MAG,   # the far eye
    (85, 39): MAG, (86, 39): LIT, (85, 40): DIM, (86, 40): MAG,                                 # the near eye
}


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
        for (x, y), c in EYES.items():
            im[y, x] = (*c, 255)
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

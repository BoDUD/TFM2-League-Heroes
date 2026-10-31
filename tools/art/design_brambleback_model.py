#!/usr/bin/env python3
"""The Crimson Brambleback's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_brambleback_model.py   # writes assets/source/brambleback/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-10-31): A-1 (hd/A-1.png, Codex's raw read on its own 6 px squares: 201 x 132, TFT's idle at 3/4,
crouched on all fours, the long arms and red claws in front, the leaf collar, the branches and the red core on the
back, the wedge head low at the front right) at 40 game px from the back branches to the claws, PPU 1.7 -> 68 rows:
A-1 brought down by pixel_down.pixelate (k = 68 / 132, about the soles' centre), as the size review showed it. Its
face sits at the right (FACE_BOX, shown at 12x): the wedge head, the two red eyes and the orange forehead spiral. The
reduction left the far eye a dull smear and the spiral a blob, so FACE redraws them square by square in the design's
own colours: the far eye a yellow-hot centre in a red ring like the near one, the spiral a clear curl of orange on the
pale bark of the forehead (the near eye kept as it came).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_brambleback_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "brambleback", "hd")
PPU = 1.7
HEIGHT = 40   # game px
PICKS = {"idle": "A-1"}   # out -> take
# the design's own colours (idle.png after the reduction)
BARK, BARK_D = (187, 129, 79), (155, 103, 65)
HOT, ORANGE, EMBER, RED, RED_D = (253, 200, 5), (250, 116, 3), (251, 141, 11), (235, 17, 1), (148, 2, 2)
# (x, y) -> colour, on idle.png's 104 x 68
FACE = {
    # the far eye: red ring, a hot centre
    (82, 30): RED, (83, 30): ORANGE, (82, 31): ORANGE, (83, 31): HOT, (84, 31): RED, (82, 32): RED_D, (83, 32): RED_D,
    # the forehead spiral (centre (77, 25)) on the pale bark
    **{(x, y): BARK for x in range(75, 80) for y in range(23, 28)},
    (76, 23): EMBER, (77, 23): EMBER, (78, 23): EMBER,
    (75, 24): ORANGE, (79, 24): ORANGE,
    (75, 25): ORANGE, (77, 25): EMBER, (79, 25): ORANGE,
    (75, 26): ORANGE, (77, 26): ORANGE, (78, 26): ORANGE,
    (76, 27): ORANGE, (77, 27): BARK_D,
}
FACE_BOX = (64, 18, 92, 44)   # x0, y0, x1, y1: the wedge head, its two red eyes and the forehead spiral


def main():
    for out, take in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        rows = round(HEIGHT * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        ys, xs = np.nonzero(im[..., 3] > 0)
        im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        for (x, y), c in FACE.items():
            im[y, x] = (*c, 255)
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(lp(os.path.join(HD, f"{out}_face12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()

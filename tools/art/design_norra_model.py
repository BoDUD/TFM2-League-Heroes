#!/usr/bin/env python3
"""Norra's game-size design: the user's picks of step 0 brought to their heights.

    python tools/art/design_norra_model.py   # writes assets/source/norra/hd/idle.png and yuumi.png (+ _4x)

The user's picks (2026-10-26): Norra = A-1 (hd/A-1.png, Codex's first, fine take read on its own 10 px squares:
63 x 101) at 36 game px from the top of her hat to her soles, PPU 2.0 -> 72 rows; Yuumi on her book = B-1 (70 x 65)
at 17 game px, the same PPU -> 34 rows. Both by pixel_down.pixelate (the size review's own reduction, so the pictures
are the ones the user saw).
THE RING (the user, 2026-10-26: 「加金环」 - the TFT unit holds a small gold portal ring in her left hand, the video refs):
drawn into the idle in her NEAR hand (image left, the hand at cols 14-17 rows 58-61: her far arm is the one that
points at the target, the near one would cross her face) as a 7 x 7 gold ring with a purple portal inside, its top-left
at RING_AT; the hand's skin squares are put back over its right edge (she grips it).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_norra_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "norra", "hd")
PPU = 2.0
PICKS = {"idle": ("A-1", 36), "yuumi": ("B-1", 17)}   # out -> (take, game px)
K, L, H, G, D, P, Q = ((14, 3, 15), (242, 194, 58), (255, 236, 150), (200, 150, 30), (138, 90, 18), (87, 50, 203),
                       (137, 109, 238))
RING = ["-KKKKK-",
        "KHLLLGK",
        "KLPPPGK",
        "KLPQPDK",
        "KLPPPDK",
        "KGGDDDK",
        "-KKKKK-"]
RING_AT = (8, 57)
SKIN = {(252, 218, 142), (243, 184, 114), (222, 204, 153)}
PAL = {"K": K, "L": L, "H": H, "G": G, "D": D, "P": P, "Q": Q}


def ring(im):
    """The gold ring in her near hand (the hand's own squares kept on top: she holds its edge)."""
    hand = {(x, y): tuple(im[y, x]) for x in (14, 15) for y in range(57, 63) if tuple(im[y, x][:3]) in SKIN}
    x0, y0 = RING_AT
    for dy, row in enumerate(RING):
        for dx, ch in enumerate(row):
            if ch != "-":
                im[y0 + dy, x0 + dx] = PAL[ch] + (255,)
    for (x, y), c in hand.items():
        im[y, x] = c
    return im


def main():
    for out, (take, px) in PICKS.items():
        d = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA"))
        rows = round(px * PPU)
        im, _ = PD.pixelate(d, rows / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        im = Image.fromarray(im)
        im = np.asarray(im.crop(im.getbbox())).copy()
        if out == "idle":
            im = ring(im)
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        print(out, im.shape[1], "x", im.shape[0])


if __name__ == "__main__":
    main()

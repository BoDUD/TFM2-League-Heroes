#!/usr/bin/env python3
"""Draven's dense design: the picture the user handed over on 2026-10-26 (「就用这个就行」 - his idle as it is in game,
both axes held low at his sides, drawn at PPU 2.2 on 11-px squares, 1536 x 1024, 22 colours, true alpha) read back
square for square: every 11-px square one colour, none mixed, so the read is exact (scaled back up it is the picture
pixel for pixel). 114 x 76 squares: 76 rows = 34.5 game pixels, his 1x sprite's 35.

    python tools/art/design_draven_hd.py        # hd/raw/draven-user.png -> hd/design.png (checks the round trip)
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "draven", "hd")
RAW = os.path.join(HD, "raw", "draven-user.png")
SQ = 11                         # px a square in the picture
PPU = 2.2


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read():
    a = np.asarray(Image.open(lp(RAW)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    x0, y0 = xs.min(), ys.min()
    W, H = round((xs.max() + 1 - x0) / SQ), round((ys.max() + 1 - y0) / SQ)
    d = np.zeros((H, W, 4), np.uint8)
    for r in range(H):
        for c in range(W):
            blk = a[y0 + r * SQ:y0 + (r + 1) * SQ, x0 + c * SQ:x0 + (c + 1) * SQ].reshape(-1, 4)
            u, n = np.unique(blk, axis=0, return_counts=True)
            d[r, c] = u[n.argmax()]
    up = np.repeat(np.repeat(d, SQ, 0), SQ, 1)
    if not (up == a[y0:y0 + H * SQ, x0:x0 + W * SQ]).all():
        sys.exit("the picture is not on one 11-px grid: some squares are mixed")
    return d


def main():
    d = read()
    Image.fromarray(d).save(lp(os.path.join(HD, "design.png")))
    print(f"design {d.shape[1]} x {d.shape[0]} squares ({d.shape[0] / PPU:.1f} game px tall), "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")


if __name__ == "__main__":
    main()

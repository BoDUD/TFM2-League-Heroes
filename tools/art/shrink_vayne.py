#!/usr/bin/env python3
"""Vayne's design at a smaller size: the approved 48-row design with whole rows and columns deleted, never the face.

    python tools/art/shrink_vayne.py [--height 40] [--out FILE] [--check]

The user saw her in game at 48 rows (the ponytail's top to the soles) standing a head over the others ("薇恩游戏里尺寸
太大了"; Garen 37, Ahri 38, Riven 40, Darius 42). The approved design (B at 48 rows, assets/source/native/
vayne_native48.png) is shrunk the way tools/art/design_riven.py's step 7 shrank Riven to 40: rows are cut into as
many groups as the target has, and in each group the rows most like their neighbour go until one is left (columns
the same, the width in proportion; three offsets of the grouping, the least loss kept) - never the face's rows and
columns (FACE: the glasses, the skin round them, the mouth and the chin), which stay square for square, so the
lenses keep their two reds and the pasted face of every strip frame stays the design's. Then the outline pass
(design_riven.one_outline: spurs off, the black just inside the outline turned into the material's own darkest
shade, lone specks taken by their area; the face kept) and the outline ring completed where a deleted line held
it. Written on the 128 canvas with the soles on row 99 and the middle of the feet where the 48-row design has them.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_riven as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")
BIG = os.path.join(SRC, "vayne_native48.png")
OUT = os.path.join(SRC, "vayne_native.png")
HEIGHT = 40
FACE_ROWS = range(10, 18)       # the 48-row design's glasses, cheeks, mouth and chin (rows from its top) ...
FACE_COLS = range(21, 30)       # ... and its columns from the ear to the profile
Z = 8


def load(path):
    a = np.asarray(Image.open(R.lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(), (xs.min(), ys.min())


def shrink(a, height):
    H, W = a.shape[:2]
    cols = sorted({tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full((H, W), -1, int)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        idx[y, x] = lut[tuple(int(v) for v in a[y, x, :3])]
    rows = R.keep_axis([idx[y] for y in range(H)], height, FACE_ROWS)
    sub = idx[rows]
    keep_cols = R.keep_axis([sub[:, x] for x in range(W)], round(W * height / H), FACE_COLS)
    small = idx[np.ix_(rows, keep_cols)]
    pal = np.array(cols, np.uint8)
    out = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    out[m, :3] = pal[small[m]]
    out[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in FACE_ROWS]
    fc = [keep_cols.index(c) for c in FACE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    return R.outline_rgba(R.one_outline(out, keep), feet=out.shape[0] - 1), rows, keep_cols


def canvas(fig, big_origin, big_shape):
    """On the 128 canvas: the soles on the 48-row design's sole row, the feet's middle on its column."""
    c = np.zeros((128, 128, 4), np.uint8)
    bx, by = big_origin
    sole = by + big_shape[0] - 1
    x0 = int(round(bx + big_shape[1] / 2 - fig.shape[1] / 2))
    c[sole - fig.shape[0] + 1:sole + 1, x0:x0 + fig.shape[1]] = fig
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--height", type=int, default=HEIGHT)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="compare with the committed design instead of writing")
    o = ap.parse_args()
    big, origin = load(BIG)
    fig, rows, cols = shrink(big, o.height)
    c = canvas(fig, origin, big.shape)
    img = Image.fromarray(np.repeat(np.repeat(c, Z, 0), Z, 1))
    n = len({tuple(int(v) for v in p[:3]) for p in fig[fig[..., 3] > 0]})
    print(f"{fig.shape[1]}x{fig.shape[0]}, {n} colours; rows kept {rows}; columns kept {cols}")
    if o.check:
        now = np.asarray(Image.open(R.lp(o.out)).convert("RGBA"))
        print("same as", o.out, (now == np.asarray(img)).all())
        return
    img.save(R.lp(o.out))
    print("written", o.out)


if __name__ == "__main__":
    main()

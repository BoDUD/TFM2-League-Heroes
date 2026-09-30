#!/usr/bin/env python3
"""Read an image model's "pixel art" back on its own grid: one output pixel per drawn square, no resampling.

    python regrid.py design.png out.png [--size 10.5] [--scale 8]

Image models (Codex's image_gen, GPT) draw a game-size sprite as coarse squares of about 10 px on a 1254 px
canvas, with soft edges, tens of thousands of colours and squares that are not all the same width, so no fixed
grid fits: a fixed-pitch sample cuts through squares and doubles an outline column where they run narrow. Here the
square boundaries are found from the colour changes themselves: for every column the number of figure rows whose
colour changes between it and the next, peaks at least 0.6 of a square apart are boundaries, gaps wider than 1.6
squares get evenly spaced ones (the rows the same way). Every square then takes the median colour of its middle 3x3,
and it is figure when most of that middle is (alpha >= 128). The square size is the commonest distance between
strong neighbouring peaks unless --size is given.

Writes out.png (1 px per square, cropped to the figure) and, with --scale, out_<scale>x.png. Nothing else changes:
no palette, no outline pass - do those on the result (art-spec "A design drawn at game size"). league_lucian's
redesign read back as 47x46 game pixels this way.
"""
import argparse
import os

import numpy as np
from PIL import Image


def profile(a, op, axis):
    """Colour changes between neighbouring columns (axis 1) or rows (axis 0), counted over the figure."""
    d = np.abs(np.diff(a[..., :3].astype(int), axis=axis)).max(axis=2) > 36
    if axis == 1:
        both = op[:, 1:] | op[:, :-1]
        return np.concatenate([[0], (d & both).sum(axis=0)]).astype(float)
    both = op[1:] | op[:-1]
    return np.concatenate([[0], (d & both).sum(axis=1)]).astype(float)


def boundaries(e, lo, hi, size):
    """Square boundaries in [lo, hi]: peaks of e at least 0.6 size apart; gaps over 1.6 size filled evenly."""
    cand = [x for x in range(lo + 1, hi) if e[x] > 0 and e[x] >= e[x - 1] and e[x] >= e[x + 1]]
    cand.sort(key=lambda x: -e[x])
    picked = []
    for x in cand:
        if all(abs(x - p) >= 0.6 * size for p in picked) and e[x] >= 0.15 * e.max():
            picked.append(x)
    picked = sorted(set(picked + [lo, hi + 1]))
    out = [picked[0]]
    for b in picked[1:]:
        gap = b - out[-1]
        n = int(round(gap / size))
        if n >= 2 and gap > 1.6 * size:
            start = out[-1]
            for k in range(1, n):
                out.append(int(round(start + gap * k / n)))
        out.append(b)
    return out


def square_size(e, lo, hi):
    pk = [x for x in range(lo + 1, hi) if e[x] > 0.3 * e.max() and e[x] >= e[x - 1] and e[x] >= e[x + 1]]
    d = np.diff(pk)
    d = d[(d >= 5) & (d <= 24)]
    return float(np.median(d)) if len(d) else 10.0


def regrid(a, size=None):
    """RGBA array -> (1 px per square RGBA array, square size, (column bounds, row bounds))."""
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    ex, ey = profile(a, op, 1), profile(a, op, 0)
    size = size or square_size(ex, x0, x1)
    bx = boundaries(ex, x0, x1, size)
    by = boundaries(ey, y0, y1, size)
    H, W = len(by) - 1, len(bx) - 1
    out = np.zeros((H, W, 4), np.uint8)
    for j in range(H):
        cy = (by[j] + by[j + 1]) // 2
        for i in range(W):
            cx = (bx[i] + bx[i + 1]) // 2
            win = a[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2].reshape(-1, 4)
            if (win[:, 3] >= 128).sum() * 2 > len(win):
                px = win[win[:, 3] >= 128][:, :3]
                out[j, i, :3] = np.median(px, axis=0).astype(np.uint8)
                out[j, i, 3] = 255
    ys2, xs2 = np.nonzero(out[..., 3] > 0)
    return out[ys2.min():ys2.max() + 1, xs2.min():xs2.max() + 1], size, (bx, by)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--size", type=float, help="square size in source px (default: measured)")
    ap.add_argument("--scale", type=int, default=0, help="also write the result enlarged this many times")
    o = ap.parse_args()
    a = np.asarray(Image.open(o.src).convert("RGBA"))
    one, size, (bx, by) = regrid(a, o.size)
    Image.fromarray(one).save(o.dst)
    if o.scale:
        root, ext = os.path.splitext(o.dst)
        Image.fromarray(one).resize((one.shape[1] * o.scale, one.shape[0] * o.scale), Image.NEAREST).save(
            f"{root}_{o.scale}x{ext}")
    n = len({tuple(c) for c in one[one[..., 3] > 0][:, :3]})
    wx, wy = np.diff(bx), np.diff(by)
    print(f"{o.src}: squares ~{size:.2f} px (x {wx.min()}-{wx.max()}, y {wy.min()}-{wy.max()}) -> "
          f"{one.shape[0]} rows x {one.shape[1]} cols, {n} colours")


if __name__ == "__main__":
    main()

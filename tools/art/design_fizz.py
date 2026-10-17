#!/usr/bin/env python3
"""Fizz's design: Codex's game-size draft A read back on its own grid (assets/source/fizz/codex_model/).

    python tools/art/design_fizz.py [--check]

The user picked, of Codex's two drafts and its later cell-by-cell 34-row redraw, "左：原稿读回的 A" - the draft read
back as it was drawn (3/4 view, the big near eye, three prongs to the right), 32 rows: the redraw had turned him to
the front with small eyes and a C-shaped trident head. Steps:
  1 the skill's regrid.py on fizz_design_A_raw.png (Codex's ~10-px squares on a 1254-px canvas): one pixel per drawn
    square, 32 x 55, about 770 colours (the image model's soft colours);
  2 the colours merged down to 24, closest pair first in Lab and weighted by how many pixels they cover, so a small
    distinct colour (the eyes' green: 7 pixels) survives where k-means folds it into the skin;
  3 one outline colour: the second near-black (#13132B) joins the first (#121122) - 23 colours;
  4 on the 128 x 128 canvas the pack heroes use: soles on row 99, the middle of the feet on column 64 (the standing
    point 64, 88);
  5 the eyes' green only in the eyes: the one square of it in the gem of the trident's butt ring takes the trident's
    teal (the strips pack names the green the eye-only colour).
Writes assets/source/native/fizz_native.png (8x). --check compares with the file there instead.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "fizz", "codex_model", "fizz_design_A_raw.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "fizz_native.png")
MAXC = 24
OUTLINE, OUTLINE2 = (0x12, 0x11, 0x22), (0x13, 0x13, 0x2B)
EYE, TEAL = (0x20, 0xAE, 0x56), (0x07, 0x8E, 0x76)
EYE_BOX = (55, 70, 80, 84)     # x0, y0, x1, y1 on the canvas: the face


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) else pre + p


def lab(rgb):
    c = rgb.astype(float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def merge_palette(cols, counts, k):
    """Merge the closest pair (Lab distance x the square root of the smaller count) until k colours are left; the
    label of every input colour and the k colours (count-weighted means)."""
    rgb = cols.astype(float)
    n = counts.astype(float)
    L = lab(cols)
    label = np.arange(len(cols))
    alive = list(range(len(cols)))
    while len(alive) > k:
        A = np.array(alive)
        d = np.sqrt(((L[A, None, :] - L[None, A, :]) ** 2).sum(2))
        cost = d * np.sqrt(np.minimum(n[A][:, None], n[A][None, :]))
        np.fill_diagonal(cost, np.inf)
        i, j = np.unravel_index(np.argmin(cost), cost.shape)
        a, b = A[i], A[j]
        rgb[a] = (rgb[a] * n[a] + rgb[b] * n[b]) / (n[a] + n[b])
        n[a] += n[b]
        L[a] = lab(np.round(rgb[a:a + 1]).astype(np.uint8))[0]
        label[label == b] = a
        alive.remove(b)
    return label, {a: np.round(rgb[a]).astype(np.uint8) for a in alive}


def design():
    one, size, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    on = one[..., 3] >= 128
    one[~on] = 0
    one[on, 3] = 255
    cols, inv, counts = np.unique(one[on][:, :3], axis=0, return_inverse=True, return_counts=True)
    label, rep = merge_palette(cols, counts, MAXC)
    one[on, :3] = np.array([rep[label[i]] for i in inv.ravel()])
    one[(one[..., :3] == OUTLINE2).all(-1) & on, :3] = OUTLINE
    ys, xs = np.nonzero(on)
    fig = one[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = fig.shape[:2]
    feet = np.nonzero(fig[h - 3:, :, 3].any(0))[0]
    x0 = int(round(64 - (feet.min() + feet.max()) / 2))
    can = np.zeros((128, 128, 4), np.uint8)
    can[99 - h + 1:100, x0:x0 + w] = fig
    eye = (can[..., :3] == EYE).all(-1) & (can[..., 3] > 0)
    yy, xx = np.mgrid[0:128, 0:128]
    bx0, by0, bx1, by1 = EYE_BOX
    can[eye & ~((yy >= by0) & (yy <= by1) & (xx >= bx0) & (xx <= bx1)), :3] = TEAL
    return can, size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    can, size = design()
    big = np.repeat(np.repeat(can, 8, 0), 8, 1)
    op = can[..., 3] > 0
    n = len(np.unique(can[op][:, :3], axis=0))
    ys, xs = np.nonzero(op)
    print(f"squares ~{size:.2f} px; {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {n} colours")
    if a.check:
        cur = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("same as", OUT, ":", bool((cur == big).all()))
        return
    Image.fromarray(big).save(lp(OUT))
    print(OUT)


if __name__ == "__main__":
    main()

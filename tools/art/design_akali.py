#!/usr/bin/env python3
"""Akali's design, the redo (the user's pick "A40", 2026-10-01): Codex's drawing A cut to 40 rows, byte for byte.

    python tools/art/design_akali.py [--out assets/source/native/akali_native.png] [--check]

The first design (Codex's 66-square draft cut to 47 rows, then to 40 rows; codex_model/design3_*) read as a dark
blob on the olive arena ground: near-black and dark olive, realistic proportions with a small head, the face hidden by
the mask. The user: "现在阿卡丽太丑了 重做一下吧", then Tristana's route: a picture first (the
user picked Codex's redraw 4 B, codex_model/redo7/akali_redraw4_B.png: slim, a tapered face, amber eyes, a teal mask
hugging the face, navy-blue hair with a lime bow, lilac tattoos, a red satchel, blue trousers), then the sprite. Codex's
image model cannot draw an exact 40-row grid; main's 18-redraw recipe ("干净，不要细节": at most 24 colours, 2-3 flat
shades a material, big solid areas, eyes at least 2 squares tall in an eye-only colour) gave
codex_model/redo7/akali_native_A.png: 44x48, 18 colours, a strict 8x grid, the amber #D46A0A only in the eyes.
1. codex_model/redo7/akali_native_A_1x.png as drawn, one pixel a square, alpha to 0/255;
2. the face - the eye squares' rows from 3 over them to 4 under, their columns 3 to either side - is never deleted;
3. whole rows and columns go down to 39 rows by dynamic programming (dp_keep: never two neighbours, a deleted line
   costing its weighted difference from the nearer neighbour - the eyes 12, steel 8, lime 3 - rows then columns or
   columns then rows, whichever loses less), the width in proportion: the thin kunai and kama stay whole;
4. one outline (design_riven.one_outline + outline_rgba), the face kept square for square - closing the ring over the
   top adds a row: 40;
5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_riven as R  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "akali", "codex_model", "redo7", "akali_native_A_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "akali_native.png")
HEIGHT = 40
KEEP = 39                         # rows the deletion keeps: closing the outline ring adds one row on top (40)
EYE = (0xD4, 0x6A, 0x0A)          # the amber of the eyes, used nowhere else (import_native steadies the frames on it)
WEIGHTS = {"eye": 12, "steel": 8, "lime": 3}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dp_keep(lines, weights, n_keep, hard=()):
    """Which n_keep lines stay: never two neighbours deleted, each deleted line costing its weighted difference from
    the nearer-looking neighbour, the hard lines kept. (kept indices, total cost)"""
    n, INF = len(lines), float("inf")

    def cost(j, k):
        return float(((lines[j] != lines[k]) * np.maximum(weights[j], weights[k])).sum())

    dp = np.full((n_keep + 1, n), INF)
    back = np.full((n_keep + 1, n), -1, int)
    dp[1][0] = 0.0
    if 0 not in hard:
        dp[1][1] = cost(0, 1)
    for t in range(2, n_keep + 1):
        for i in range(1, n):
            if dp[t - 1][i - 1] < dp[t][i]:
                dp[t][i], back[t][i] = dp[t - 1][i - 1], i - 1
            if i >= 2 and (i - 1) not in hard and dp[t - 1][i - 2] < INF:
                c = dp[t - 1][i - 2] + min(cost(i - 1, i - 2), cost(i - 1, i))
                if c < dp[t][i]:
                    dp[t][i], back[t][i] = c, i - 2
    ends = [(dp[n_keep][n - 1], n - 1)] + ([(dp[n_keep][n - 2] + cost(n - 1, n - 2), n - 2)] if (n - 1) not in hard else [])
    total, last = min(ends)
    keep = [last]
    for t in range(n_keep, 1, -1):
        keep.append(back[t][keep[-1]])
    return sorted(int(k) for k in keep), total


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (int(ys.min()), int(xs.min()))


def soles(a):
    return int(np.nonzero((a[..., 3] > 0).any(1))[0].max())


def weight(c):
    r, g, b = c
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if c == EYE or (r > 230 and 170 < g < 215 and b < 40):
        return WEIGHTS["eye"]
    if max(c) - min(c) < 40 and lum > 120:          # steel greys and whites: the blades
        return WEIGHTS["steel"]
    if g > 200 and r > 150 and b < 110:              # the lime bow, trims and wraps
        return WEIGHTS["lime"]
    return 1


def build():
    a = np.asarray(Image.open(lp(DRAFT)).convert("RGBA")).copy()
    a[a[..., 3] > 0, 3] = 255
    a, _ = crop(a)
    eye = np.all(a[..., :3] == np.array(EYE, np.uint8), -1) & (a[..., 3] > 0)
    ys, xs = np.nonzero(eye)
    face_rows, face_cols = range(ys.min() - 3, ys.max() + 5), range(xs.min() - 3, xs.max() + 4)
    H, W = a.shape[:2]
    cols = sorted({tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full((H, W), -1, int)
    w = np.ones((H, W), int)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        c = tuple(int(v) for v in a[y, x, :3])
        idx[y, x], w[y, x] = lut[c], weight(c)
    tw = round(W * KEEP / H)
    best = None
    for order in ("rc", "cr"):
        if order == "rc":
            r_, lr = dp_keep(list(idx), list(w), KEEP, set(face_rows))
            c_, lc = dp_keep(list(idx[r_].T), list(w[r_].T), tw, set(face_cols))
        else:
            c_, lc = dp_keep(list(idx.T), list(w.T), tw, set(face_cols))
            r_, lr = dp_keep(list(idx[:, c_]), list(w[:, c_]), KEEP, set(face_rows))
        if best is None or lr + lc < best[0]:
            best = (lr + lc, r_, c_)
    _, rows, kc = best
    small = np.pad(idx[np.ix_(rows, kc)], 1, constant_values=-1)
    pal = np.array(cols, np.uint8)
    out = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    out[m, :3] = pal[small[m]]
    out[m, 3] = 255
    fr = [rows.index(y) for y in face_rows if y in rows]
    fc = [kc.index(x) for x in face_cols if x in kc]
    keep = np.zeros(m.shape, bool)
    keep[min(fr) + 1:max(fr) + 2, min(fc) + 1:max(fc) + 2] = True
    fig, _ = crop(R.outline_rgba(R.one_outline(out, keep), feet=soles(out), keep=keep))
    feet = np.nonzero(fig[-1, :, 3] > 0)[0]
    x0 = int(round(64 - (feet.min() + feet.max() + 1) / 2))
    canvas = np.zeros((128, 128, 4), np.uint8)
    canvas[100 - fig.shape[0]:100, x0:x0 + fig.shape[1]] = fig
    return canvas, fig, rows, kc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="compare with the committed design instead of writing it")
    a = ap.parse_args()
    canvas, fig, rows, kc = build()
    big = Image.fromarray(np.repeat(np.repeat(canvas, 8, 0), 8, 1))
    if a.check:
        old = np.asarray(Image.open(lp(a.out)).convert("RGBA"))
        same = old.shape == np.asarray(big).shape and (old == np.asarray(big)).all()
        print("identical" if same else "DIFFERENT", a.out)
        sys.exit(0 if same else 1)
    big.save(lp(a.out))
    op = fig[..., 3] > 0
    print(f"{a.out}: {fig.shape[1]}x{fig.shape[0]}, {len(np.unique(fig[op][:, :3], axis=0))} colours, "
          f"{int(op.sum())} px; rows kept {rows}; columns kept {kc}")


if __name__ == "__main__":
    main()

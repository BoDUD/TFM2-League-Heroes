#!/usr/bin/env python3
"""Rebuild Akali's design (the user's pick "①", 2026-09-30) from Codex's drawing, byte for byte.

    python tools/art/design_akali.py [--out assets/source/native/akali_native.png] [--check] [--search]

Step 1 was redone at game size (assets/source/akali/MODEL_PROMPTS.md) after the user found the first design too
flat next to the heroes on main. Codex drew the user's picture as pixel art on its own grid of 13 px squares, 66
squares from the ponytail's tip to the soles (codex_model/design3_generated_A.png); its own 46-row copy took every
1.4th square and broke the clothes into specks. Here:
1. The drawing back on its own grid: square borders at the peaks of colour change (at least 0.6 of a square apart,
   wider gaps split evenly), every square the median of the 3x3 round its centre: 53x66.
2. Colours: each square to the nearest (Lab) colour of Codex's palette (codex_model/design3_palette.json); its eye
   white and iris only on the two eye rows, and no gold on the head (the hairline's skin/hair blends went to it).
3. Game size by deleting whole rows and columns, no pixel mixed: KEEP_ROWS / KEEP_COLS, found by dynamic
   programming (--search) on the palette mapping without the head rule - 46 of 66 rows and 37 of 53 columns, never
   two neighbours deleted, a deleted line costing its difference from the nearer-looking kept neighbour, eye squares
   weighing 12, steel 6, gold 4, the liner row, both eye rows and the eye columns kept (the near eye white, white,
   iris; one square of skin; the far eye white, iris). The soles' outline row, which the search dropped, is kept
   under the feet instead (47 rows, 43 from the crown).
4. The outline ring completed outside clear colours (luma >= 60), never under the soles.
The result sits on a 128x128 canvas at 8x with the soles on row 99 and the feet's middle on column 64.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CM = os.path.join(ROOT, "assets", "source", "akali", "codex_model")
SRC = os.path.join(CM, "design3_generated_A.png")
PALETTE = os.path.join(CM, "design3_palette.json")
OUT = os.path.join(ROOT, "assets", "source", "native", "akali_native.png")
SQUARE = 13.0                   # px per square in Codex's drawing (the commonest gap between colour-change peaks)
EYE_ROWS, LINER = (21, 22), 20  # on the 53x66 grid
EYE_X = (26, 34)
EYE_COLS = {27, 28, 31, 32, 33}  # the near eye's whites, the skin between, the far eye: one near iris column may go
HEAD_ROWS = 24                  # rows 0-23: the head (no gold there)
STEEL = ("#6E7A8C", "#ACB8C8", "#E7EEF2")
GOLD = ("#755225", "#B88835", "#E2B94B", "#FFE397")
WEIGHTS = {"eye": 12, "steel": 6, "gold": 4}
KEEP_ROWS = [1, 3, 5, 7, 9, 11, 13, 15, 16, 17, 18, 20, 21, 22, 24, 26, 27, 29, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42,
             43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 58, 60, 62, 64, 65]
KEEP_COLS = [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 21, 22, 23, 25, 27, 28, 30, 31, 32, 33, 35, 37, 38,
             40, 42, 44, 46, 48, 49, 50, 51, 52]


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


# ------------------------------------------------------------------------------------------------ 1 own grid
def profile(a, op, axis):
    d = np.abs(np.diff(a[..., :3].astype(int), axis=axis)).max(axis=2) > 36
    if axis == 1:
        return np.concatenate([[0], (d & (op[:, 1:] | op[:, :-1])).sum(axis=0)]).astype(float)
    return np.concatenate([[0], (d & (op[1:] | op[:-1])).sum(axis=1)]).astype(float)


def boundaries(e, lo, hi, size):
    cand = sorted([x for x in range(lo + 1, hi) if e[x] > 0 and e[x] >= e[x - 1] and e[x] >= e[x + 1]], key=lambda x: -e[x])
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
            out += [int(round(start + gap * k / n)) for k in range(1, n)]
        out.append(b)
    return out


def regrid(a):
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    bx = boundaries(profile(a, op, 1), xs.min(), xs.max(), SQUARE)
    by = boundaries(profile(a, op, 0), ys.min(), ys.max(), SQUARE)
    out = np.zeros((len(by) - 1, len(bx) - 1, 4), np.uint8)
    for j in range(len(by) - 1):
        cy = (by[j] + by[j + 1]) // 2
        for i in range(len(bx) - 1):
            cx = (bx[i] + bx[i + 1]) // 2
            win = a[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2].reshape(-1, 4)
            if (win[:, 3] >= 128).sum() * 2 > len(win):
                out[j, i, :3] = np.median(win[win[:, 3] >= 128][:, :3], axis=0).astype(np.uint8)
                out[j, i, 3] = 255
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


# ------------------------------------------------------------------------------------------------ 2 colours
def lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def rgb(h):
    return tuple(int(h[k:k + 2], 16) for k in (1, 3, 5))


def quantise(a, head_rows):
    """Palette colours (the eye-only pair last) and the index image (-1 empty)."""
    pj = json.load(open(PALETTE, encoding="utf-8"))
    body = [h for h in pj["colors"] if h not in pj["eye_only"]]
    cols = np.array([rgb(h) for h in body + pj["eye_only"]], np.uint8)
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    d = ((lab(a[ys, xs, :3])[:, None] - lab(np.array([rgb(h) for h in body]))[None]) ** 2).sum(-1)
    d[np.ix_(ys < head_rows, [k for k, h in enumerate(body) if h in GOLD])] = np.inf
    idx = np.full(a.shape[:2], -1, int)
    idx[ys, xs] = d.argmin(1)
    white, iris = len(body), len(body) + 1
    for y in EYE_ROWS:
        for x in range(EYE_X[0], EYE_X[1] + 1):
            r, g, b = (int(v) for v in a[y, x, :3])
            if 0.299 * r + 0.587 * g + 0.114 * b > 225:
                idx[y, x] = white
            elif 80 <= r <= 140 and 40 <= g <= 75 and b <= 50:
                idx[y, x] = iris
    return cols, idx


# ------------------------------------------------------------------------------------------------ 3 game size
def dp_keep(lines, weights, n_keep, hard=()):
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


def search(grid, rows=46):
    """KEEP_ROWS / KEEP_COLS again: rows then columns and columns then rows, the order losing less."""
    cols, idx = quantise(grid, 0)
    hexes = ["#%02X%02X%02X" % tuple(int(v) for v in c) for c in cols]
    w = np.ones(idx.shape, int)
    w[np.isin(idx, [k for k, h in enumerate(hexes) if h in STEEL])] = WEIGHTS["steel"]
    w[np.isin(idx, [k for k, h in enumerate(hexes) if h in GOLD])] = WEIGHTS["gold"]
    w[idx >= len(cols) - 2] = WEIGHTS["eye"]
    th, tw = rows, round(idx.shape[1] * rows / idx.shape[0])
    hard_r = set(EYE_ROWS) | {LINER}
    best = None
    for order in ("rc", "cr"):
        if order == "rc":
            r, lr = dp_keep(list(idx), list(w), th, hard_r)
            c, lc = dp_keep(list(idx[r].T), list(w[r].T), tw, EYE_COLS)
        else:
            c, lc = dp_keep(list(idx.T), list(w.T), tw, EYE_COLS)
            r, lr = dp_keep(list(idx[:, c]), list(w[:, c]), th, hard_r)
        if best is None or lr + lc < best[0]:
            best = (lr + lc, r, c)
    return best[1], best[2]


# ------------------------------------------------------------------------------------------------ 4 outline
def outline_colour(idx):
    H, W = idx.shape
    edge = [idx[y, x] for y in range(H) for x in range(W) if idx[y, x] >= 0 and any(
        not (0 <= yy < H and 0 <= xx < W) or idx[yy, xx] < 0 for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)))]
    return int(np.bincount(edge).argmax())


def outline_out(idx, cols, line, feet):
    H, W = idx.shape
    res = idx.copy()
    lum = cols.astype(float) @ np.array([0.299, 0.587, 0.114])
    for y in range(min(H, feet + 1)):
        for x in range(W):
            if idx[y, x] >= 0:
                continue
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < H and 0 <= xx < W and idx[yy, xx] >= 0 and idx[yy, xx] != line and lum[idx[yy, xx]] >= 60:
                    res[y, x] = line
                    break
    return res


def build():
    grid = regrid(np.asarray(Image.open(lp(SRC)).convert("RGBA")))
    cols, idx = quantise(grid, HEAD_ROWS)
    small = idx[np.ix_(KEEP_ROWS, KEEP_COLS)]
    small = outline_out(np.pad(small, 1, constant_values=-1), cols, outline_colour(idx), feet=small.shape[0])
    fig = np.zeros(small.shape + (4,), np.uint8)
    op = small >= 0
    fig[op, :3] = cols[small[op]]
    fig[op, 3] = 255
    ys, xs = np.nonzero(fig[..., 3] > 0)
    fig = fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    soles = np.nonzero(fig[-1, :, 3] > 0)[0]
    fx = (soles.min() + soles.max() + 1) // 2
    canvas = np.zeros((128, 128, 4), np.uint8)
    x0, y0 = 64 - fx, 100 - fig.shape[0]
    m = fig[..., 3] > 0
    canvas[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]][m] = fig[m]
    return canvas, fig, grid


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="compare with the committed design instead of writing it")
    ap.add_argument("--search", action="store_true", help="recompute the kept rows and columns")
    a = ap.parse_args()
    canvas, fig, grid = build()
    if a.search:
        r, c = search(grid)
        print("rows", r, "(then the soles' outline row", grid.shape[0] - 1, ")")
        print("cols", c)
        return
    big = Image.fromarray(np.repeat(np.repeat(canvas, 8, 0), 8, 1))
    if a.check:
        old = np.asarray(Image.open(lp(a.out)).convert("RGBA"))
        same = old.shape == np.asarray(big).shape and (old == np.asarray(big)).all()
        print("identical" if same else "DIFFERENT", a.out)
        sys.exit(0 if same else 1)
    big.save(lp(a.out))
    op = fig[..., 3] > 0
    print(f"{a.out}: {fig.shape[1]}x{fig.shape[0]}, {len(np.unique(fig[op][:, :3], axis=0))} colours, {int(op.sum())} px")


if __name__ == "__main__":
    main()

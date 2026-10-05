#!/usr/bin/env python3
"""Tryndamere's design (assets/source/native/tryndamere_native.png): Codex's generated draft A_retry read back on its own
grid and shrunk to 40 rows by whole rows and columns, every kept square the draft's own.

    python tools/art/design_tryndamere.py [--check]

How it came about (2026-10-05): the user picked Codex's picture A (codex_picture/tryndamere-model-A.png: League's idle, the
greatsword trailing in the back hand). Codex's step 1 came back too big (raw/A_retry.png: 10 px squares, 80 x 56 on its own
grid) and its own 40x42 A / B, cut by 17 whole columns, broke into specks. Area votes and a pasted bigger head with a
hand-drawn face were rejected (「眼睛都看不到」「这是做的什么啊」); the user: 「就那这个慢慢描边 降到40px 描到一模一样」, then
「40 行原样」 from an options sheet (40 as drawn / 40 with design_riven.one_outline / 42 / 44). Steps:
  1. raw/A_retry.png read back on its own grid (the skill's regrid.py, alpha >= 128): 80 x 56;
  2. every square one of 24 colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. to 40 rows the way tools/art/shrink_vayne.py took Vayne and design_riven step 7 took Riven to 40: the rows in as many
     groups as are kept, in each group the rows most like a neighbour go (design_riven.keep_axis: three offsets of the
     grouping, the least loss kept), then the columns the same, the width in proportion - never FACE_ROWS / FACE_COLS
     (the helmet's brim, the eye, the cheek, the beard and red mouth, the chin; the cheek guard's edge to the gem), which
     stay square for square, and never row 0 (the horn's tip): 57 x 40;
  4. strips.complete_outline where a deleted line held the outline (the face never touched);
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64.
--check compares the result with the committed tryndamere_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "tryndamere", "codex_model", "raw", "A_retry.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "tryndamere_native.png")
K, HEIGHT = 24, 40
FACE_ROWS = range(12, 19)          # on the 80 x 56 read-back: brim, eye, cheek, beard + mouth, chin, the beard's bottom
FACE_COLS = range(52, 59)          # the cheek guard's edge, the face, the eye, the mouth, the gem
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def build():
    raw = read_back()
    assert raw.shape[:2] == (56, 80), raw.shape
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    # the horn's tip (row 0) always stays; the rows under it go to HEIGHT - 1
    face = range(FACE_ROWS.start - 1, FACE_ROWS.stop - 1)
    rows = [0] + [r + 1 for r in R.keep_axis([idx[y] for y in range(1, H)], HEIGHT - 1, face)]
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], round(W * HEIGHT / H), FACE_COLS)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in FACE_ROWS]
    fc = [cols.index(c) for c in FACE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out, rows, cols, added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    can, rows, cols, added = build()
    ys, xs = np.nonzero(can[..., 3] > 0)
    info = (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}), "
            f"{len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours, outline +{added}; rows kept {rows}; columns kept {cols}")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", info)
        return
    Image.fromarray(can).save(lp(OUT))
    print(OUT, info)


if __name__ == "__main__":
    main()

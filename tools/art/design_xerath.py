#!/usr/bin/env python3
"""Xerath's design (assets/source/native/xerath_native.png): Codex's generated draft B read back on its own grid and
shrunk to 44 rows by whole rows and columns, every kept square the draft's own.

    python tools/art/design_xerath.py [--check]

How it came about (2026-10-06): the user picked Codex's picture A (codex_picture/xerath-model-A.png: League's idle,
floating, the arms hanging). Codex's step 1 (codex_model/) cut its own drafts to 40 rows by every other row and they
broke into specks; the user: 「泽拉斯尺寸可以做大一点」「可以44px？」. From an options sheet (draft A or B read back and cut
to 44 rows, narrow or wide, and B at 50) the user took 「B44 宽 31x44」. Steps:
  1. codex_model/raw/xerath_design_B_raw.png read back on its own grid (the skill's regrid.py, alpha >= 128): 78 x 39;
  2. every square one of 24 colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. to 44 rows as design_tryndamere took Tryndamere to 40: the rows in as many groups as are kept, in each group the
     rows most like a neighbour go (design_riven.keep_axis), never FACE_ROWS (the hood's rim, the eyes, the energy face)
     nor the first row (the top of the hood) or the last (the near leg's tip); then the columns to WIDTH the same way,
     never FACE_COLS;
  4. strips.complete_outline where a deleted line held the outline (the face never touched);
  5. on the 128x128 canvas at 8x: the near leg's tip on row 99, the point between the two leg tips on column 64. The far
     leg's tip ends two rows higher, as drawn (he floats; Codex's own 40-row cut had moved that leg down).
--check compares the result with the committed xerath_native.png instead of writing it.
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

RAW = os.path.join(ROOT, "assets", "source", "xerath", "codex_model", "raw", "xerath_design_B_raw.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "xerath_native.png")
K, HEIGHT, WIDTH = 24, 44, 30
FACE_ROWS = range(7, 17)           # on the 78 x 39 read-back: the hood's rim, the eyes, the energy face, the chin
FACE_COLS = range(17, 31)          # the hood's opening
TIP_ROW, MID_COL = 99, 64


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
    assert raw.shape[:2] == (78, 39), raw.shape
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    mid = R.keep_axis([idx[y] for y in range(1, H - 1)], HEIGHT - 2, range(FACE_ROWS.start - 1, FACE_ROWS.stop - 1))
    rows = [0] + [r + 1 for r in mid] + [H - 1]
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], WIDTH, FACE_COLS)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [i for i, r in enumerate(rows) if r in FACE_ROWS]
    fc = [i for i, c in enumerate(cols) if c in FACE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # the two leg tips: the lowest square of each leg (the lowest rows split into two runs)
    low = np.nonzero(fig[-1, :, 3] > 0)[0]
    near = (low.min() + low.max()) / 2
    far_rows = [r for r in range(fig.shape[0] - 1, fig.shape[0] - 6, -1)
                if (np.nonzero(fig[r, :, 3] > 0)[0] > low.max() + 2).any()]
    far_cols = np.nonzero(fig[far_rows[0], :, 3] > 0)[0]
    far = far_cols[far_cols > low.max() + 2]
    mid_x = (near + (far.min() + far.max()) / 2) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = TIP_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
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

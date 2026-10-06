#!/usr/bin/env python3
"""Samira's design (assets/source/native/samira_native.png): Codex's generated draft attempt1_A read back on its own grid
and shrunk to 40 rows by whole rows and columns, every kept square the draft's own (tools/art/design_tryndamere.py's way).

    python tools/art/design_samira.py [--check]

How it came about (2026-10-06): the user picked Codex's picture A (codex_picture/samira-model-A.png: League's idle, hands
on her hips, the greatsword slung across her back). Codex's step 1 (codex_model/) came back too big - its drafts 53-81
squares tall - and its own 40-row cut of a later draft had changed her look. My first cuts kept the whole face (16 rows)
and squeezed the body from 65 rows to 26: the clothes broke into specks. The user: 「那这个慢慢调整啊 用工具 之前蛮王
赵兴不都调整了吗？」 (draft 1 attached), then 「40 行原样」 from an options sheet (40 as drawn / 40 with one_outline / 42 / 44).
Steps:
  1. codex_model/raw/attempt1_A.png read back on its own grid (the skill's regrid.py, alpha >= 128): 81 x 44 (8 px
     squares);
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. to 40 rows: the rows in as many groups as are kept, in each group the rows most like a neighbour go
     (design_riven.keep_axis: three offsets of the grouping, the least loss kept), never the first or the last row nor
     EYE_ROWS (the eyepatch and the green eye); then the columns to WIDTH the same way, never EYE_COLS. Only the eyes
     are kept whole: head and body lose rows in proportion;
  4. strips.complete_outline where a deleted line held the outline (the eyes never touched);
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64.
--check compares the result with the committed samira_native.png instead of writing it.
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

RAW = os.path.join(ROOT, "assets", "source", "samira", "codex_model", "raw", "attempt1_A.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "samira_native.png")
K, HEIGHT, WIDTH = 28, 40, 27
EYE_ROWS = range(16, 21)           # on the 81 x 44 read-back: the eyepatch, the strap, the green eye
EYE_COLS = range(19, 28)
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
    assert raw.shape[:2] == (81, 44), raw.shape
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    mid = R.keep_axis([idx[y] for y in range(1, H - 1)], HEIGHT - 2, range(EYE_ROWS.start - 1, EYE_ROWS.stop - 1))
    rows = [0] + [r + 1 for r in mid] + [H - 1]
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], WIDTH, EYE_COLS)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in EYE_ROWS]
    fc = [cols.index(c) for c in EYE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid_x = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
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
    os.makedirs(os.path.dirname(lp(OUT)), exist_ok=True)
    Image.fromarray(can).save(lp(OUT))
    print(OUT, info)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Xin Zhao's design (assets/source/native/xinzhao_native.png): Codex's generated draft 03 read back on its own grid and
shrunk to HEIGHT rows by whole rows and columns, every kept square the draft's own (tools/art/design_tryndamere.py's way).

    python tools/art/design_xinzhao.py [--check] [--height N] [--out file]

How it came about (2026-10-05): the user picked Codex's picture A (codex_picture/xinzhao-model-A.png: League's idle, the
spear slanting behind his shoulders). Codex's step 1 came back as two 57 x 42 designs cut down by whole lines from its
drafts 03 / 04 (dark, the trousers grey). An area vote of draft 02 with three hand-drawn faces was rejected (「原稿2的脸要调
一下吧 太方正了吧」, then 「不能用这个 参考刚刚蛮王怎么借助工具弄的 还不会？」「用那个记住工具调整不就好了吗」 with draft 03 attached).
Steps:
  1. raw/03.png read back on its own grid (the skill's regrid.py, alpha >= 128): 95 x 62 (11.5 px squares);
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. to HEIGHT rows the way design_tryndamere.py took Tryndamere to 40: the rows in as many groups as are kept, in each
     group the rows most like a neighbour go (design_riven.keep_axis: three offsets of the grouping, the least loss kept),
     then the columns the same, the width in proportion - never FACE_ROWS / FACE_COLS (the silver fringe, the brows, the
     eyes, the cheek, the chin), which stay square for square, and never the topknot's top row;
  4. strips.complete_outline where a deleted line held the outline (the face never touched);
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64;
  6. SLIM (2026-10-06, the user on the run: 「体型也有点胖」 - the body from the gold pauldron to the front bracer stood
     22 columns wide, League's at game size 12-14): below the chin (from SLIM_ROW) the columns SLIM_COLS go, the ones
     most like their right neighbour in that band (the chest, the white undershirt, the belt, the front arm's side), and
     everything right of each moves in a column - the head, the topknot and the spear above SLIM_ROW stay; the user
     picked 4 of the options 2 / 3 / 4; the outline closed again, and an outline square the cut left with no colour
     round it (outlines run together) takes the colour round it. Varus's SLIM (design_varus.py) the same way.
--check compares the result with the committed xinzhao_native.png instead of writing it.
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

RAW = os.path.join(ROOT, "assets", "source", "xinzhao", "codex_model", "raw", "03.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "xinzhao_native.png")
K, HEIGHT = 26, 42
SLIM_ROW, SLIM_COLS = 75, (59, 64, 70, 72)


def slim_x(x, row):
    """Where a canvas column of the design before SLIM is after it (a deleted column: where its right neighbour went)."""
    return x if row < SLIM_ROW else x - sum(1 for c in SLIM_COLS if c < x)


def slim(can, outline):
    out = can.copy()
    for x in sorted(SLIM_COLS, reverse=True):
        out[SLIM_ROW:, x:-1] = out[SLIM_ROW:, x + 1:]
        out[SLIM_ROW:, -1] = 0
    out, added, _ = strips.complete_outline(out, color=outline, feet=SOLE_ROW)
    # the cut brought outlines together (the undershirt's, the belt's, the front hand's): an outline square below
    # SLIM_ROW with no colour among its 8 neighbours takes the commonest colour within two squares
    # (a pinhole the cut opened inside the figure - between the front hand and the undershirt - counts: the rig's finish
    # would fill it with black)
    ol = np.array(outline, np.uint8)
    op = out[..., 3] > 0
    for y, x in zip(*np.nonzero(~op)):
        if y >= SLIM_ROW and 0 < x < 127 and y < 127 and op[y - 1, x] and op[y + 1, x] and op[y, x - 1] and op[y, x + 1]:
            out[y, x] = (*outline, 255)
    ink = (out[..., 3] > 0) & (out[..., :3] == ol).all(-1)
    for y, x in zip(*np.nonzero(ink)):
        if y < SLIM_ROW or (out[y - 1:y + 2, x - 1:x + 2, 3] > 0).sum() < 9:
            continue
        near = [tuple(out[yy, xx, :3]) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2) if not ink[yy, xx]]
        if near:
            continue
        ring = [tuple(out[yy, xx, :3]) for yy in range(y - 2, y + 3) for xx in range(x - 2, x + 3)
                if out[yy, xx, 3] and not ink[yy, xx]]
        if ring:
            out[y, x, :3] = max(set(ring), key=ring.count)
    return out, added
FACE_ROWS = range(15, 27)          # on the read-back: the silver fringe, brows, eyes, cheek, mouth, chin
FACE_COLS = range(61, 73)          # the hair's edge in front of the ear to the face's front
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


def build(height=HEIGHT):
    raw = read_back()
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    top = int(np.nonzero((idx >= 0).any(1))[0][0])      # the topknot's top row always stays
    face = range(FACE_ROWS.start - top - 1, FACE_ROWS.stop - top - 1)
    rows = [top] + [r + top + 1 for r in R.keep_axis([idx[y] for y in range(top + 1, H)], height - 1, face)]
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], round(W * height / (H - top)), FACE_COLS)
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
    x0 = max(0, min(128 - fig.shape[1], x0))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    out, more = slim(out, outline)
    return out, rows, cols, added + more


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--height", type=int, default=HEIGHT)
    ap.add_argument("--out")
    a = ap.parse_args()
    can, rows, cols, added = build(a.height)
    ys, xs = np.nonzero(can[..., 3] > 0)
    info = (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}), "
            f"{len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours, outline +{added}")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", info)
        return
    out = a.out or OUT
    os.makedirs(os.path.dirname(lp(out)), exist_ok=True)
    Image.fromarray(can).save(lp(out))
    print(out, info)


if __name__ == "__main__":
    main()

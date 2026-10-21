#!/usr/bin/env python3
"""Orianna's chibi designs (Q版, 2026-10-22) from Codex's raw drafts (assets/source/orianna/codex_chibi/raw), the
Tryndamere way: each draft read back on its own grid, its own K colours, then whole rows and columns deleted down to
HEIGHT rows - never the face's - and the outline closed.

    python tools/art/design_orianna_chibi.py --out DIR [--height 84]

Codex's own 84-row cut (orianna-q*_1x.png) was a nearest-neighbour shrink of its drafts and read muddy; its drafts
read back on their own grids (the skill's regrid.py) as clean 117 / 107 / 127 / 137-row sprites. Steps per take:
  1. regrid (alpha >= 128 is figure, then opaque);
  2. K colours of its own (design_varus.kmeans);
  3. the face kept square for square: the rows from a little above the eyes (the cyan squares) to the chin's mouth,
     the columns over both eyes and the cheek around them; row 0 (the bun's top) kept;
  4. design_riven.keep_axis rows to HEIGHT, then the columns in proportion;
  5. strips.complete_outline where a deleted line held the outline (the face untouched), then enclosed clear specks
     of 1-2 squares filled from their neighbours;
  6. on the 128x128 canvas: the soles on row 117, the middle of the feet (the lowest three rows) on column 64.
Writes <out>/<take>.png (128x128), <out>/<take>_8x.png and <out>/<take>_native.png (the read-back before the cuts).
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
import rigkit  # noqa: E402
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "orianna", "codex_chibi", "raw")
TAKES = ["q1-front", "q1-side", "q2-front", "q2-side"]
K = 28
SOLE_ROW, MID_COL, FEET_ROWS = 117, 64, 3
# Q1 front's read-back (72 x 117): the head is rows above SPLIT except the wind-up key (columns left of KEY_X from row
# KEY_Y), the neck at (NECK_Y, NECK_X)
SPLIT, KEY_X, KEY_Y, NECK_Y, NECK_X = 56, 34, 49, 55, 45
# rebalanced Q1 front: (head, body) kept fractions of their native size
REBALANCE = {"r1": (0.66, 0.80, True), "r2": (0.66, 0.86, True), "r3": (0.62, 0.86, True)}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(path):
    raw, _, _ = regrid(np.asarray(Image.open(lp(path)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def face_box(raw):
    """(rows, columns) to keep whole: the cyan eye squares, 3 rows above them to 5 below (the mouth), 2 columns round."""
    r, g, b = (raw[..., i].astype(int) for i in range(3))
    eye = (raw[..., 3] > 0) & (b > 170) & (g > 140) & (b - r > 60)
    ys, xs = np.nonzero(eye)
    return range(max(1, ys.min() - 3), ys.max() + 6), range(max(0, xs.min() - 2), xs.max() + 3)


def build(raw, height):
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    fr, fc = face_box(raw)
    face = range(fr.start - 1, fr.stop - 1)
    rows = [0] + [r + 1 for r in R.keep_axis([idx[y] for y in range(1, H)], height - 1, face)]
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], round(W * height / H), fc)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    r0, r1 = rows.index(fr.start), rows.index(fr.stop - 1)
    c0, c1 = cols.index(fc.start), cols.index(fc.stop - 1)
    keep[r0:r1 + 1, c0:c1 + 1] = True
    ink = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=ink, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return fig, added


def cut(idx, rows_to, cols_to, protect_rows, protect_cols, keep_top=True):
    """Rows then columns of idx deleted down to rows_to x cols_to by keep_axis; row 0 kept when keep_top."""
    H, W = idx.shape
    if keep_top:
        pr = range(protect_rows.start - 1, protect_rows.stop - 1)
        rows = [0] + [r + 1 for r in R.keep_axis([idx[y] for y in range(1, H)], rows_to - 1, pr)]
    else:
        rows = R.keep_axis([idx[y] for y in range(H)], rows_to, protect_rows)
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], cols_to, protect_cols)
    return rows, cols


def rebalance(raw, head, body, eye_cols=True):
    """The user on Q1 front (2026-10-22): 「把头缩小点 身体放长点就完美了」. The head (bun to the hair tails, the wind-up
    key left with the body) and the body are cut apart, each by its own share of whole rows AND columns so neither is
    squashed - only the eyes kept square for square - and the head set back on the neck: head and body are the kept
    fractions of their native rows."""
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    op = idx >= 0
    yy, xx = np.mgrid[:H, :W]
    hmask = op & (yy < SPLIT) & ~((xx < KEY_X) & (yy >= KEY_Y))
    bmask = op & ~hmask
    r, g, b = (raw[..., i].astype(int) for i in range(3))
    eye = op & (b > 170) & (g > 140) & (b - r > 60)
    ey, ex = np.nonzero(eye)
    eyes_r, eyes_c = range(ey.min() - 1, ey.max() + 2), range(ex.min() - 1, ex.max() + 2)

    hy, hx = np.nonzero(hmask)
    hy0, hy1, hx0, hx1 = hy.min(), hy.max() + 1, hx.min(), hx.max() + 1
    hid = np.where(hmask, idx, -1)[hy0:hy1, hx0:hx1]
    mid = (eyes_c.start + eyes_c.stop) // 2 - hx0
    pc = range(eyes_c.start - hx0, eyes_c.stop - hx0) if eye_cols else range(mid, mid + 1)
    hr, hc = cut(hid, round(hid.shape[0] * head), round(hid.shape[1] * head),
                 range(eyes_r.start - hy0, eyes_r.stop - hy0), pc)
    hsm = hid[np.ix_(hr, hc)]

    by, bx = np.nonzero(bmask)
    by0, by1, bx0, bx1 = by.min(), by.max() + 1, bx.min(), bx.max() + 1
    bid = np.where(bmask, idx, -1)[by0:by1, bx0:bx1]
    br, bc = _cut_free(bid, body)
    bsm = bid[np.ix_(br, bc)]

    # the neck: native (NECK_Y, NECK_X) in both cuts lines the head up on the body
    def at(kept, v):
        return min(range(len(kept)), key=lambda i: abs(kept[i] - v))
    hny, hnx = at([hy0 + v for v in hr], NECK_Y), at([hx0 + v for v in hc], NECK_X)
    bny, bnx = at([by0 + v for v in br], NECK_Y), at([bx0 + v for v in bc], NECK_X)
    oy, ox = bny - hny, bnx - hnx                      # head origin in body coordinates
    top, left = min(0, oy), min(0, ox)
    Hc = max(bsm.shape[0], oy + hsm.shape[0]) - top
    Wc = max(bsm.shape[1], ox + hsm.shape[1]) - left
    can = np.full((Hc, Wc), -1, int)
    can[-top:-top + bsm.shape[0], -left:-left + bsm.shape[1]] = bsm
    hv = hsm >= 0
    reg = can[oy - top:oy - top + hsm.shape[0], ox - left:ox - left + hsm.shape[1]]
    reg[hv] = hsm[hv]
    fig = np.zeros(can.shape + (4,), np.uint8)
    m = can >= 0
    fig[m, :3] = pal[can[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    er = [i for i, v in enumerate(hr) if hy0 + v in eyes_r]
    ec = [i for i, v in enumerate(hc) if hx0 + v in eyes_c]
    keep[oy - top + er[0]:oy - top + er[-1] + 1, ox - left + ec[0]:ox - left + ec[-1] + 1] = True
    ink = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, added, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1], added


def _cut_free(idx, k):
    H, W = idx.shape
    rows = R.keep_axis([idx[y] for y in range(H)], round(H * k), range(H // 2, H // 2 + 1))
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], round(W * k), range(W // 2, W // 2 + 1))
    return rows, cols


def fill_specks(fig, most=2):
    """Enclosed clear specks of at most `most` squares (a soft draft's half-transparent squares, or a cut's seam) take
    the commonest colour round them; bigger enclosed gaps (between a hand and the skirt) are drawn and stay."""
    out = fig.copy()
    n = 0
    for hole in rigkit.holes(fig):
        if len(hole) > most:
            continue
        for y, x in hole:
            near = [tuple(fig[y + dy, x + dx]) for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0))
                    if 0 <= y + dy < fig.shape[0] and 0 <= x + dx < fig.shape[1] and fig[y + dy, x + dx, 3] > 0]
            out[y, x] = max(set(near), key=near.count)
            n += 1
    return out, n


def place(fig):
    if fig.shape[0] > SOLE_ROW + 1:
        raise ValueError(f"{fig.shape[0]} rows do not fit above the soles")
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - (feet.min() + feet.max()) / 2))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--height", type=int, default=84)
    ap.add_argument("--raw", default=RAW)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for t in TAKES:
        raw = read_back(os.path.join(a.raw, f"orianna-{t}.png"))
        Image.fromarray(raw).save(lp(os.path.join(a.out, f"{t}_native.png")))
        fig, added = build(raw, a.height)
        fig, filled = fill_specks(fig)
        can = place(fig)
        im = Image.fromarray(can)
        im.save(lp(os.path.join(a.out, f"{t}.png")))
        im.resize((1024, 1024), Image.NEAREST).save(lp(os.path.join(a.out, f"{t}_8x.png")))
        n = len({tuple(p[:3]) for p in fig[fig[..., 3] > 0]})
        print(f"{t}: read back {raw.shape[1]}x{raw.shape[0]} -> {fig.shape[1]}x{fig.shape[0]}, {n} colours, outline +{added}, specks filled {filled}, "
              f"gaps left {[len(h) for h in rigkit.holes(fig)]}")
    raw = read_back(os.path.join(a.raw, "orianna-q1-front.png"))
    for name, (head, body, ec) in REBALANCE.items():
        fig, added = rebalance(raw, head, body, ec)
        fig, filled = fill_specks(fig)
        im = Image.fromarray(place(fig))
        im.save(lp(os.path.join(a.out, f"q1-front-{name}.png")))
        print(f"q1-front-{name} head {head} body {body}: {fig.shape[1]}x{fig.shape[0]}, outline +{added}, specks {filled}, "
              f"gaps {[len(h) for h in rigkit.holes(fig)]}")


if __name__ == "__main__":
    main()

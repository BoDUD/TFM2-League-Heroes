#!/usr/bin/env python3
"""Zilean's design (the user's pick "A2_40", 2026-10-03): Codex's image-model draft A_draft_02 cut to 40 rows.

    python tools/art/design_zilean.py [--out assets/source/native/zilean_native.png] [--check]

The user picked picture A (assets/source/zilean/PICTURE_PROMPT.md: League's idle - floating, the palms up, the giant
golden clock on his back, no staff). Asked for a game-size sprite of 40 rows from the clock's roof to the lowest toe
(MODEL_PROMPTS.md), Codex delivered no 40-row result (codex_model/zilean_design_HANDOFF.md: its A read back 45x56, its
B 54x77, and it would not shrink them) plus its image-model drafts. Of seven cuts of three drafts shown beside the
pack's heroes (A_draft_03 at 40 / 43 / 46 rows, A_draft_02 at 40 / 44, the front-view B at 43 / 46), the user took
A_draft_02 cut to 40 rows (codex_model/raw/A_draft_02.png, the draft Codex's own A came from):
1. the draft read back on its own grid (the skill's regrid.py, squares of 9 px: one pixel per drawn square), 52x62,
   alpha 0/255;
2. its colours merged to 30 (design_kaisa.merge_palette: agglomerative in Lab, weighted by count, after rounding the
   soft-edge near-duplicates); the ten eye squares keep their own colours, the whites made one white and the pupils
   the outline's near-black;
3. whole rows, then columns (or the other way, whichever loses less) deleted by design_akali.dp_keep: never two
   neighbours, never the face (the eye rows 2 over to 2 under, the eye columns 2 to either side), the eyes 12, the
   clock's turquoise 4, the gold glints 3 as weights; 39 rows kept (closing the outline ring adds the 40th);
4. one outline (design_riven.one_outline + outline_rgba);
5. on the 128x128 canvas at 8x: the lowest toe on row 99, the middle of the feet on column 64.
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
from design_akali import dp_keep  # noqa: E402
from design_kaisa import merge_palette  # noqa: E402
from regrid import regrid  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "zilean", "codex_model", "raw", "A_draft_02.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "zilean_native.png")
SIZE = 9                 # the draft's square, px
MAXC = 30
ROWS = 40
# on the 52x62 read-back: the near eye (white over white over a cyan iris, a dark pupil beside), the far eye
EYES = [(27, 32), (27, 33), (28, 32), (28, 33), (29, 32), (29, 33), (27, 37), (27, 38), (28, 37), (28, 38)]
WHITE = (246, 249, 250)
PUPIL = (7, 5, 20)       # the outline's near-black


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def weight(c):
    r, g, b = (int(x) for x in c)
    if g > 170 and b > 170 and r < 140:           # the clock's turquoise numerals
        return 4
    if r > 220 and g > 170 and b < 120:           # gold glints
        return 3
    return 1


def read_back():
    """Steps 1-2: the draft on its own grid, 30 colours, the eye squares as drawn."""
    a, _, _ = regrid(np.asarray(Image.open(lp(DRAFT)).convert("RGBA")), SIZE)
    a = a.copy()
    on = a[..., 3] >= 128
    a[~on] = 0
    a[on, 3] = 255
    q = a.copy()
    q[on, :3] = (q[on, :3] // 4) * 4 + 2          # near-duplicates first (thousands of soft-edge colours)
    cols, inv, counts = np.unique(q[on][:, :3], axis=0, return_inverse=True, return_counts=True)
    label, rep = merge_palette(cols, counts, MAXC)
    out = a.copy()
    out[on, :3] = np.array([rep[label[i]] for i in inv.ravel()])
    for y, x in EYES:                             # the eye squares as drawn: one white, the pupils the outline's black
        c = a[y, x, :3].astype(int)
        out[y, x, :3] = WHITE if c.min() > 235 else PUPIL if c.max() < 40 else c
    return out


def keep_lines(lines, weights, n, hard):
    while True:
        k, c = dp_keep(lines, weights, n, hard)
        if c < float("inf") and min(k) >= 0:
            return k, c
        n += 1


def cut(a):
    """Steps 3-4."""
    H, Wd = a.shape[:2]
    cols = sorted({tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full((H, Wd), -1, int)
    w = np.ones((H, Wd), int)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        c = tuple(int(v) for v in a[y, x, :3])
        idx[y, x], w[y, x] = lut[c], weight(c)
    for y, x in EYES:
        w[y, x] = 12
    ys, xs = np.array([e[0] for e in EYES]), np.array([e[1] for e in EYES])
    face_rows, face_cols = set(range(ys.min() - 2, ys.max() + 3)), set(range(xs.min() - 2, xs.max() + 3))
    keep_n = ROWS - 1
    tw = round(Wd * keep_n / H)
    best = None
    for order in ("rc", "cr"):
        if order == "rc":
            r_, lr = keep_lines(list(idx), list(w), keep_n, face_rows)
            c_, lc = keep_lines(list(idx[r_].T), list(w[r_].T), tw, face_cols)
        else:
            c_, lc = keep_lines(list(idx.T), list(w.T), tw, face_cols)
            r_, lr = keep_lines(list(idx[:, c_]), list(w[:, c_]), keep_n, face_rows)
        if best is None or lr + lc < best[0]:
            best = (lr + lc, r_, c_)
    _, rows, kc = best
    out = np.pad(a[np.ix_(rows, kc)], ((1, 1), (1, 1), (0, 0)))
    fr = [rows.index(y) for y in sorted(face_rows) if y in rows]
    fc = [kc.index(x) for x in sorted(face_cols) if x in kc]
    keep = np.zeros(out.shape[:2], bool)
    keep[min(fr) + 1:max(fr) + 2, min(fc) + 1:max(fc) + 2] = True
    soles = int(np.nonzero((out[..., 3] > 0).any(1))[0].max())
    return crop(R.outline_rgba(R.one_outline(out, keep), feet=soles, keep=keep))


def build():
    fig = cut(read_back())
    feet = np.nonzero(fig[-1, :, 3] > 0)[0]
    x0 = int(round(64 - (feet.min() + feet.max() + 1) / 2))
    canvas = np.zeros((128, 128, 4), np.uint8)
    canvas[100 - fig.shape[0]:100, x0:x0 + fig.shape[1]] = fig
    return canvas, fig


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="compare with the committed design instead of writing it")
    a = ap.parse_args()
    canvas, fig = build()
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

#!/usr/bin/env python3
"""Vi's design (the user's pick "A40", 2026-10-02): Codex's simple draft A, the gauntlets hanging at the hips, cut to 40
rows.

    python tools/art/design_vi.py [--out assets/source/native/vi_native.png] [--check]

The user picked picture B (assets/source/vi/PICTURE_PROMPT.md: League's recall stance, both fists down at the hips).
Asked for a game-size sprite of 38 rows inside a size box (MODEL_PROMPTS.md), Codex delivered 38-row A/B resampled from
its image-generation drafts (codex_model/vi_design_A.png, _B.png, its HANDOFF: "not native") and the drafts themselves
(codex_model/raw). Read back on their own grids, cut to 40 and 42 rows and shown with the pack's heroes beside Codex's
38-row ones, the user took the simple A draft at 40 rows ("A40最好"):
1. the draft read back on its own grid (the skill's regrid.py: one pixel per drawn square, 17 px squares, 56 x 37),
   its flat black background keyed out (every square within 24 of the corner's colour), cropped (54 x 35);
2. its colours merged to 26 (agglomerative in Lab, weighted by count); the six eye squares (the near eye 2x2: a white
   highlight beside a blue iris over a dark lid row, the far eye one column) keep their own colours;
3. whole rows, then columns (or the other way, whichever loses less) deleted by design_akali.dp_keep: never two
   neighbours, never the face (the eye rows 3 over to 4 under, the eye columns 3 to either side), the blue of the eyes
   and the crystals 12, the gauntlets' gold 3, the scarf's red 2 as weights; 39 rows kept (closing the outline ring over
   the top adds the 40th), the columns in proportion;
4. one outline (design_riven.one_outline + outline_rgba);
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
from design_akali import dp_keep  # noqa: E402
from design_kaisa import crop, keep_lines, merge_palette  # noqa: E402
from regrid import regrid  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "vi", "codex_model", "raw", "simple_A.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "vi_native.png")
MAXC = 26
ROWS = 40
KEY = 24
EYES = [(13, 16), (13, 17), (14, 16), (14, 17), (13, 21), (14, 21)]   # on the keyed 54x35 read-back


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def is_blue(c):
    r, g, b = (int(x) for x in c)
    return b > 140 and b - r > 60                         # the eyes' and the crystals' blue


def weight(c):
    r, g, b = (int(x) for x in c)
    if is_blue(c):
        return 12
    if r > 170 and g > 120 and b < 130:                   # the gauntlets' gold
        return 3
    if r > 130 and g < 60 and b < 70:                     # the scarf's red
        return 2
    return 1


def read_back():
    """Steps 1-2."""
    one, _, _ = regrid(np.asarray(Image.open(lp(DRAFT)).convert("RGBA")))
    one = one.copy()
    bg = one[0, 0, :3].astype(int)
    one[np.abs(one[..., :3].astype(int) - bg).max(2) < KEY, 3] = 0
    a = crop(one).copy()
    on = a[..., 3] >= 128
    a[~on] = 0
    a[on, 3] = 255
    cols, inv, counts = np.unique(a[on][:, :3], axis=0, return_inverse=True, return_counts=True)
    label, rep = merge_palette(cols, counts, MAXC)
    out = a.copy()
    out[on, :3] = np.array([rep[label[i]] for i in inv.ravel()])
    for y, x in EYES:
        out[y, x] = a[y, x]
    return crop(out)


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
    face_rows, face_cols = set(range(ys.min() - 3, ys.max() + 5)), set(range(xs.min() - 3, xs.max() + 4))
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

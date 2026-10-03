#!/usr/bin/env python3
"""Kai'Sa's design (the user's pick "B44", 2026-10-02): Codex's chibi draft B, the wing-pods raised, cut to 44 rows.

    python tools/art/design_kaisa.py [--out assets/source/native/kaisa_native.png] [--check]

The user picked picture B (assets/source/kaisa/PICTURE_PROMPT.md: League's pods raised and half open, as in her run and
her ult's ready pose). Asked for a game-size sprite of about 36 rows crown to soles with the pods 2-5 higher
(MODEL_PROMPTS.md), Codex drew both drafts bigger, on a 1254 px canvas of about 10 px squares: A (long proportions) 79
rows, B (chibi) 64 (codex_model/kaisa_design_B.png, its HANDOFF and manifest beside it). Cut to 40, 42 and 44 rows and
shown beside the pack's heroes, the user took 44:
1. the draft read back on its own grid (the skill's regrid.py: one pixel per drawn square), alpha 0/255;
2. its 1342 colours merged to 26 (agglomerative in Lab, weighted by count); the eight eye squares (2x2 each: a white
   highlight and a purple iris under a dark top, the far eye mirrored) keep their own colours - two squares of iris
   purple would merge into the hair;
3. whole rows, then columns (or the other way, whichever loses less) deleted by design_akali.dp_keep: never two
   neighbours, never the face (the eye rows 3 over to 4 under, the eye columns 3 to either side), the eyes 12, the
   magenta glow 6, the gold trims 3 as weights; 43 rows kept (closing the outline ring over the top adds the 44th),
   the columns in proportion (raised until the cut is possible: a run of L free lines loses at most (L + 1) // 2);
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
from regrid import regrid  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "kaisa", "codex_model", "kaisa_design_B.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "kaisa_native.png")
MAXC = 26
ROWS = 44
KEEP_ROWS = set()             # more rows of the read-back the cut never takes out (design_kaisa_v2.py: the pods' tips)
EYES = [(19, 27), (19, 28), (20, 27), (20, 28), (19, 32), (19, 33), (20, 32), (20, 33)]   # on the 64x46 read-back


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def lab(rgb):
    c = rgb.astype(float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def merge_palette(cols, counts, k):
    """Merge the closest pair (Lab distance x a count weight) until k colours are left."""
    rgb = cols.astype(float)
    n = counts.astype(float)
    L = lab(cols)
    label = np.arange(len(cols))
    alive = list(range(len(cols)))
    while len(alive) > k:
        A = np.array(alive)
        d = np.sqrt(((L[A, None, :] - L[None, A, :]) ** 2).sum(2))
        w = np.sqrt(np.minimum(n[A][:, None], n[A][None, :]))
        cost = d * w
        np.fill_diagonal(cost, np.inf)
        i, j = np.unravel_index(np.argmin(cost), cost.shape)
        a, b = A[i], A[j]
        tot = n[a] + n[b]
        rgb[a] = (rgb[a] * n[a] + rgb[b] * n[b]) / tot
        n[a] = tot
        L[a] = lab(np.round(rgb[a:a + 1]).astype(np.uint8))[0]
        label[label == b] = a
        alive.remove(b)
    return label, {a: np.round(rgb[a]).astype(np.uint8) for a in alive}


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def weight(c):
    r, g, b = (int(x) for x in c)
    if r > 200 and b > 170 and g < 90:                    # magenta glow: the pods' eyes, the palms, the slits
        return 6
    if r > 170 and g > 120 and b < 130:                   # gold trims
        return 3
    return 1


def read_back():
    """Steps 1-2: the draft on its own grid, 26 colours, the eye squares as drawn."""
    a, _, _ = regrid(np.asarray(Image.open(lp(DRAFT)).convert("RGBA")))
    a = a.copy()
    on = a[..., 3] >= 128
    a[~on] = 0
    a[on, 3] = 255
    cols, inv, counts = np.unique(a[on][:, :3], axis=0, return_inverse=True, return_counts=True)
    label, rep = merge_palette(cols, counts, MAXC)
    out = a.copy()
    out[on, :3] = np.array([rep[label[i]] for i in inv.ravel()])
    for y, x in EYES:
        out[y, x] = a[y, x]
    return out


def keep_lines(lines, weights, n, hard):
    """dp_keep, n raised until the cut is possible."""
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
    face_rows, face_cols = set(range(ys.min() - 3, ys.max() + 5)), set(range(xs.min() - 3, xs.max() + 4))
    keep_n = ROWS - 1
    tw = round(Wd * keep_n / H)
    best = None
    for order in ("rc", "cr"):
        if order == "rc":
            r_, lr = keep_lines(list(idx), list(w), keep_n, face_rows | KEEP_ROWS)
            c_, lc = keep_lines(list(idx[r_].T), list(w[r_].T), tw, face_cols)
        else:
            c_, lc = keep_lines(list(idx.T), list(w.T), tw, face_cols)
            r_, lr = keep_lines(list(idx[:, c_]), list(w[:, c_]), keep_n, face_rows | KEEP_ROWS)
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

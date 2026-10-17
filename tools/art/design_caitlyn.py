#!/usr/bin/env python3
"""Caitlyn's design (the user's pick "B42", 2026-10-01, with the straight one-square barrel): Codex's chibi draft B cut to
the pack's 42-row height (41 rows crown to soles), byte for byte.

    python tools/art/design_caitlyn.py [--out assets/source/native/caitlyn_native.png] [--check]

Codex drew the step-1 drafts (assets/source/caitlyn/MODEL_PROMPTS.md) as 1254 px images, not on the asked 42-row grid:
A (the picture's long proportions) came back 124 squares tall, B (chibi) 58 (codex_model/caitlyn_design_B.png, its
HANDOFF and manifest beside it). The user picked B cut to 42 rows (41 with its outline):
1. the draft read back on its own grid (the skill's regrid.py: one pixel per drawn square, about 10 px), alpha 0/255;
2. its 901 colours merged to 24 (agglomerative in Lab, weighted by count, so the eyes' small blue survives);
3. rows cut per region with a quota (design_akali.dp_keep inside each: never two neighbours, the eyes 12, cyan 6,
   gold 3 as weights): the top hat 14 -> 10, the face 10 kept, the body 21 -> 13, the legs 13 -> 8 - one global cut
   took the hat's uniform crown first and flattened it; then the columns 49 -> 38 over the whole figure, the face's
   columns kept; one outline (design_riven.one_outline + outline_rgba);
4. the rifle's barrel cream -> gold right of the near hand (League's rifle is gold; Codex's HANDOFF: "B 的枪管过浅");
5. the barrel redrawn straight (the user: "B42的枪是歪的"): the cut left it rising at 45 degrees beyond the near hand
   while stock and body lie on a 1/3 slope; the old barrel (rows 12-20, columns 29 on) is cleared and a one-square gold
   line drawn along the body's slope, outlined above and below, with the muzzle's 2x2 tip (gold and cyan) at its end;
6. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
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

DRAFT = os.path.join(ROOT, "assets", "source", "caitlyn", "codex_model", "caitlyn_design_B.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "caitlyn_native.png")
MAXC = 24
# rows of the 58-row read-back: (first, end exclusive, rows kept)
REGIONS = [(0, 14, 10), (14, 24, 10), (24, 45, 13), (45, 58, 8)]   # hat, face (eyes on row 19), body, legs
COLUMNS = 37
CREAM_TO_GOLD = {(0xED, 0xDD, 0xB1): (0xD7, 0xAE, 0x50), (0xE3, 0xCB, 0x92): (0xB4, 0x88, 0x30)}
GOLD, GOLD_D, CYAN, CYAN_D = (0xD7, 0xAE, 0x50), (0xB4, 0x88, 0x30), (0x27, 0xCC, 0xE2), (0x41, 0xB6, 0xAE)
INK, INK2 = (0x0A, 0x02, 0x0E), (0x10, 0x02, 0x16)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


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


def is_eye(c):
    r, g, b = (int(x) for x in c)
    return b > 150 and b - r > 90 and b - g > 40          # the eyes' saturated blue (the cyan is greener, lighter)


def weight(c):
    r, g, b = (int(x) for x in c)
    if is_eye(c):
        return 12
    if g > 170 and b > 170 and r < 140:                   # cyan gem, lenses, energy line
        return 6
    if r > 170 and g > 120 and b < 90:                    # gold trims, stripes
        return 3
    return 1


def read_back():
    """Steps 1-2: the draft on its own grid, 24 colours."""
    a, _, _ = regrid(np.asarray(Image.open(lp(DRAFT)).convert("RGBA")))
    a = a.copy()
    on = a[..., 3] >= 128
    a[~on] = 0
    a[on, 3] = 255
    cols, inv, counts = np.unique(a[on][:, :3], axis=0, return_inverse=True, return_counts=True)
    label, rep = merge_palette(cols, counts, MAXC)
    a[on, :3] = np.array([rep[label[i]] for i in inv.ravel()])
    return crop(a)


def cut(a):
    """Step 3: rows per region, then columns, one outline."""
    H, Wd = a.shape[:2]
    cols = sorted({tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full((H, Wd), -1, int)
    w = np.ones((H, Wd), int)
    eye = np.zeros((H, Wd), bool)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        c = tuple(int(v) for v in a[y, x, :3])
        idx[y, x], w[y, x], eye[y, x] = lut[c], weight(c), is_eye(c)
    ys, xs = np.nonzero(eye)
    face_cols = set(range(xs.min() - 3, xs.max() + 4))
    rows = []
    for y0, y1, k in REGIONS:
        sub = list(range(y0, y1))
        kept, _ = dp_keep([idx[y] for y in sub], [w[y] for y in sub], k, {len(sub) - 1})
        rows += [sub[i] for i in kept]
    kc, _ = dp_keep(list(idx[rows].T), list(w[rows].T), COLUMNS, face_cols)
    out = np.pad(a[np.ix_(rows, kc)], ((1, 1), (1, 1), (0, 0)))
    fr = [rows.index(y) for y in range(ys.min() - 3, ys.max() + 5) if y in rows]
    fc = [kc.index(x) for x in sorted(face_cols) if x in kc]
    keep = np.zeros(out.shape[:2], bool)
    keep[min(fr) + 1:max(fr) + 2, min(fc) + 1:max(fc) + 2] = True
    soles = int(np.nonzero((out[..., 3] > 0).any(1))[0].max())
    return crop(R.outline_rgba(R.one_outline(out, keep), feet=soles, keep=keep))


def gold_barrel(a):
    """Step 4: the cream right of the near hand (from column 0.62 of the width) turns gold."""
    a = a.copy()
    H, Wd = a.shape[:2]
    for y in range(H):
        for x in range(int(Wd * 0.62), Wd):
            c = tuple(int(t) for t in a[y, x, :3])
            if a[y, x, 3] and c in CREAM_TO_GOLD:
                a[y, x, :3] = CREAM_TO_GOLD[c]
    return a


def straight_barrel(a, x0=29, y0=19, length=9, rise=3, clear=(12, 21, 29, 40)):
    """Step 5: the old barrel (rows clear[0]..clear[1]-1, columns clear[2] on: nothing else of her is there) cleared,
    a one-square gold line from (y0, x0) rising one row every `rise` columns, outlined, and the muzzle at its end."""
    H, Wd = a.shape[:2]
    out = np.zeros((H, Wd + 6, 4), np.uint8)
    out[:, :Wd] = a
    out[clear[0]:clear[1], clear[2]:clear[3]] = 0

    def put(y, x, c):
        out[y, x, :3] = c
        out[y, x, 3] = 255

    def ink(y, x, c=INK):
        if out[y, x, 3] == 0:
            put(y, x, c)

    for i in range(length):
        x, top = x0 + i, y0 - i // rise
        put(top, x, GOLD)
        ink(top - 1, x, INK2)
        ink(top + 1, x)
    xm, top = x0 + length, y0 - length // rise
    put(top - 1, xm, GOLD_D)
    put(top - 1, xm + 1, CYAN_D)
    put(top, xm, GOLD)
    put(top, xm + 1, CYAN)
    put(top + 1, xm, GOLD_D)
    for y, x in ((top - 2, xm), (top - 2, xm + 1), (top - 1, xm + 2), (top, xm + 2), (top + 1, xm + 1),
                 (top + 2, xm), (top - 1, xm - 1)):
        ink(y, x, INK2)
    return crop(out)


def build():
    fig = straight_barrel(gold_barrel(cut(read_back())))
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

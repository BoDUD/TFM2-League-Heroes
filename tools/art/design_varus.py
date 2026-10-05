#!/usr/bin/env python3
"""Varus's design (assets/source/native/varus_native.png): Codex's generated draft A read back on its own grid, mapped to
a 24-colour palette of itself and brought to 40 rows by an area vote.

    python tools/art/design_varus.py [--check]

How it came about (2026-10-05): the user picked Codex's picture A (codex_picture/varus-model-A.png: League's idle, the
bow hanging in the near hand, the red scarf, the medallion, the crimson-purple corrupted arms). For step 1 Codex's
generated drafts came back far too big (codex_model/varus_design_A_raw.png: 19 px squares, 73 rows for 40) and its own
40-row A / B, sampled row by row, broke into specks. Of the options sheet (Codex's A, the draft halved, cut to 42 / 44 by
whole lines, area-voted to 40) the user took 「5 原稿按面积缩40行 ... 这个最好 很不错」. Steps:
  1. the draft read back on its own grid (the skill's regrid.py, alpha >= 128): 52 x 73;
  2. every square one of 24 colours of the read-back's own (k-means in CIELAB, farthest-point start, seed 1, 30 rounds;
     the darkest = the outline);
  3. down to 40 rows by area: each new square (73/40 of a read-back square on a side) the colour covering most of it,
     background when the background covers most: 29 x 40;
  4. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64;
  5. strips.complete_outline (one outline square outside every light edge, nothing under the soles);
  6. CLEAN (the user, after the strips: 「有些杂乱的黑色素 不干净的地方也帮我清理一下」): an outline-coloured square
     inside the figure (all four neighbours drawn) with at most one outline square beside it - a loose black speck the
     area vote left on the chest, the forearms, the legs and the bow - takes the commonest colour of its other
     neighbours; two passes; the face (FACE) untouched; inner lines of two squares and more stay;
  7. FIX (the user: 「这里是什么啊 黑色一大块？」, beside the medallion): the chest harness strap, voted into the outline's
     black, in the picture's dark grey-brown leather with a lit top edge; the black and clear squares between the
     scarf's front tail and the belly in the belly's own skin and crimson; LEG_CLEAN (leg_clean) after CLEAN.
--check compares the result with the committed varus_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "varus", "codex_model", "varus_design_A_raw.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "varus_native.png")
SOLE_ROW, MID_COL = 99, 64
FEET_ROWS = 3
K = 24
ROWS = 40
FACE = (66, 73, 55, 68)
LEGS = (89, 99, 58, 75)          # rows / columns of the legs for leg_clean (the draw hand, cols 51-57, left out)
STRAP, STRAP_LIT = (0x3A, 0x34, 0x38), (0x6A, 0x62, 0x68)       # the harness leather (Codex's palette.json)
SKIN_SH, CRIMSON_D = (0xC1, 0x8D, 0x7D), (0x89, 0x08, 0x51)
THIGH, OUTLINE_RGB = (0x26, 0x14, 0x32), (0x0B, 0x04, 0x10)
FIX = {(80, 61): STRAP_LIT, (80, 62): STRAP_LIT, (81, 61): STRAP, (81, 62): STRAP,
       (83, 59): SKIN_SH, (83, 60): SKIN_SH, (84, 59): CRIMSON_D, (84, 60): SKIN_SH,
       (85, 58): CRIMSON_D, (85, 59): CRIMSON_D, (85, 60): CRIMSON_D,
       # the near thigh's left edge under the scarf's tail (rows 88-90) dented two squares in - 「腿部这里还少一块」:
       # filled in the thigh's dark purple, the outline one column out
       (88, 58): THIGH, (89, 58): THIGH, (89, 57): OUTLINE_RGB, (90, 57): OUTLINE_RGB}
# the far leg below the thigh (rows 91-99, columns 63-70: shin, knee, boot) one column in, so its outer edge comes onto
# the thigh's (the outline on column 67) - the user, about the casts: the dark legs stood out past the waist
# (「腰和腿要对齐」「不对 是把腿凸在外面」「对齐对齐对齐」); the outer outline then closed on that column (FAR_EDGE)
FAR_SHIFT = (91, 99, 63, 70)
FAR_EDGE = 67          # rows / columns on the canvas the clean-up leaves alone (the eyes, brows, mouth)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def srgb2lab(c):
    c = np.asarray(c, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def kmeans(raw, k, iters=30, seed=1):
    op = raw[..., 3] > 0
    px = raw[op][:, :3].astype(float)
    lab = srgb2lab(px)
    rng = np.random.default_rng(seed)
    cen = [lab[rng.integers(len(lab))]]
    for _ in range(k - 1):            # farthest-point start: small saturated areas (eyes, gem, gold) get a centre
        d = np.min([((lab - c) ** 2).sum(1) for c in cen], 0)
        cen.append(lab[d.argmax()])
    cen = np.array(cen)
    for _ in range(iters):
        lbl = ((lab[:, None] - cen[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            if (lbl == j).any():
                cen[j] = lab[lbl == j].mean(0)
    lbl = ((lab[:, None] - cen[None]) ** 2).sum(-1).argmin(1)
    pal = np.array([px[lbl == j].mean(0) if (lbl == j).any() else (0, 0, 0) for j in range(k)]).round().astype(np.uint8)
    idx = np.full(raw.shape[:2], -1)
    idx[op] = lbl
    return idx, pal


def down(idx, n, rows):
    """Area vote: each new square the palette index (or background) covering most of it."""
    H, W = idx.shape
    s = H / rows
    cols = int(round(W / s))
    out = np.full((rows, cols), -1)
    for r in range(rows):
        for c in range(cols):
            y0, y1, x0, x1 = r * s, (r + 1) * s, c * s, (c + 1) * s
            w = np.zeros(n + 1)
            for y in range(int(y0), min(H, int(np.ceil(y1)))):
                wy = min(y + 1, y1) - max(y, y0)
                for x in range(int(x0), min(W, int(np.ceil(x1)))):
                    wx = min(x + 1, x1) - max(x, x0)
                    w[idx[y, x] + 1] += wy * wx
            out[r, c] = -1 if w[0] > w[1:].max() else int(w[1:].argmax())
    return out


def clean(a, outline, passes=2):
    """Loose inner black specks take their neighbours' commonest colour (step 6)."""
    from collections import Counter
    for _ in range(passes):
        op = a[..., 3] > 0
        ink = op & (a[..., :3] == np.array(outline, np.uint8)).all(-1)
        new = a.copy()
        for y, x in zip(*np.nonzero(ink)):
            if FACE[0] <= y <= FACE[1] and FACE[2] <= x <= FACE[3]:
                continue
            nb4 = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if not all(op[q] for q in nb4) or sum(ink[q] for q in nb4) > 1:
                continue
            cols = Counter(tuple(int(v) for v in a[q]) for q in nb4 if not ink[q])
            new[y, x] = cols.most_common(1)[0][0]
        a = new
    return a


def leg_clean(a, outline):
    """LEG_CLEAN (「腿上没用的黑色素也要清一清」): on the legs (LEGS rows / columns, the hand beside them left out) every
    outline-coloured square inside the figure (all four neighbours drawn) takes the commonest colour of its drawn
    non-outline neighbours, inner lines included; the silhouette's outline stays."""
    from collections import Counter
    op = a[..., 3] > 0
    ink = op & (a[..., :3] == np.array(outline, np.uint8)).all(-1)
    out = a.copy()
    r0, r1, c0, c1 = LEGS
    for y in range(r0, r1 + 1):
        for x in range(c0, c1 + 1):
            if not ink[y, x]:
                continue
            nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if not all(op[q] for q in nb):
                continue
            cols = Counter(tuple(int(v) for v in a[q]) for q in nb if not ink[q])
            if cols:
                out[y, x] = cols.most_common(1)[0][0]
    return out


def far_leg_in(a, outline):
    """FAR_SHIFT's squares one column left (the near leg, columns 62 and less, untouched); then on every row from the
    thigh down the far leg's outer edge gets its outline on FAR_EDGE where a coloured square ends there."""
    r0, r1, c0, c1 = FAR_SHIFT
    out = a.copy()
    out[r0:r1 + 1, c0 - 1:c1 + 1] = 0
    out[r0:r1 + 1, c0 - 1:c1] = a[r0:r1 + 1, c0:c1 + 1]
    for y in range(89, 97):
        x = FAR_EDGE - 1
        if out[y, x, 3] and tuple(int(v) for v in out[y, x, :3]) != tuple(outline) and not out[y, FAR_EDGE, 3]:
            out[y, FAR_EDGE] = (*outline, 255)
    return out


def build():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    assert raw.shape[:2] == (73, 52), raw.shape
    idx, pal = kmeans(raw, K)
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    d = down(idx, K, ROWS)
    a = np.zeros(d.shape + (4,), np.uint8)
    m = d >= 0
    a[m, :3] = pal[d[m]]
    a[m, 3] = 255
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((a[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    can = np.zeros((128, 128, 4), np.uint8)
    y0 = SOLE_ROW + 1 - a.shape[0]
    x0 = int(round(MID_COL - mid))
    can[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    can, added, darkened = strips.complete_outline(can, color=outline, feet=SOLE_ROW)
    can = clean(can, outline)
    can = leg_clean(can, outline)
    can = far_leg_in(can, outline)
    for (y, x), c in FIX.items():
        can[y, x] = (*c, 255)
    return can, added, darkened


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    can, added, darkened = build()
    ys, xs = np.nonzero(can[..., 3] > 0)
    info = (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}), "
            f"{len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours, outline +{added} darkened {darkened}")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", info)
        return
    Image.fromarray(can).save(lp(OUT))
    print(OUT, info)


if __name__ == "__main__":
    main()

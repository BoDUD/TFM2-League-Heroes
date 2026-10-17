#!/usr/bin/env python3
"""Lissandra's design (assets/source/native/lissandra_native.png): Codex's skin-swap answer B read back by cell majority.

    python tools/art/design_lissandra.py [--check] [--review OUT.png]

How it came about (2026-10-05): the user picked Codex's picture A (codex_picture/lissandra-model-A.png: League's idle,
the masked face, the braid, the crystal shoulders, the gown to the ground - she has no legs). Codex's image tool could
not draw her at 40 rows: its script-built A / B were crude (codex_model/), its generated drafts came back 72-100 rows
and every shrink of them broke into noise. A square-by-square 40-row draft (work/lz/design_lz.py) gave the size and the
pose but not the finish, so it went back as the 骨架 with Codex's best draft (codex_model v2 attempt-02) as the 皮囊
(SKIN_PROMPT.md; the user's skeleton + skin rule); the user took 「B（42 行）」 of its three answers (codex_skin/). Steps:
  1. the green ground keyed out (g - max(r, b) > 80);
  2. every pixel the nearest of 24 colours of the picture's own (k-means in CIELAB, seeded; the darkest = the outline);
  3. Codex's squares vary round 19 px, so a centre sample lands on neighbours: the cells of the grid pitch 19.75 px,
     offset (16, 8) - the most uniform of pitches 18-20.5 (work/lz/grid_mode_lz.py) - each take their majority colour,
     background when most of the cell is green: 27 x 42;
  4. FIX: square-by-square fixes after the user's pick (the face, specks);
  5. a lone square unlike all four neighbours takes their colour when 3 or 4 agree (the lips kept);
  6. on the 128x128 canvas at 8x: the hem on row 99, the middle of the hem (the lowest three rows) on column 64;
  7. strips.complete_outline (one outline square outside every light edge, nothing under the hem).
--check compares the result with the committed lissandra_native.png instead of writing it.
"""
import argparse
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "lissandra", "codex_skin", "lissandra_skin_B.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "lissandra_native.png")
SOLE_ROW, MID_COL = 99, 64
HEM_ROWS = 3
K = 24
PITCH, OX, OY = 19.75, 16.0, 8.0
OUTLINE = (0x0B, 0x0A, 0x14)
# (row, col, (r, g, b) or None) on the 27 x 42 read-back (canvas row - 58, canvas column - 50). The face (canvas rows
# 66-71, columns 65-68) came back as a pale 4 x 3 block with no mouth: the mask's lit lower edge on row 68, skin on
# rows 69-70, ONE dark-blue lips square on the face's middle line (70, 67), the chin in the skin's shadow on row 71.
MASK_EDGE, SKIN, SHADE, LIPS = (0x33, 0x4B, 0xAF), (0xD2, 0xF2, 0xFD), (0x84, 0xA8, 0xED), (0x23, 0x27, 0x5C)
FIX = [(10, c, MASK_EDGE) for c in range(15, 19)] +       [(11, c, SKIN) for c in range(15, 19)] + [(12, c, SKIN) for c in range(15, 19)] + [(12, 17, LIPS)] +       [(13, c, SHADE) for c in range(15, 18)]
KEEP = {(12, 17)}


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


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def kmeans(px, k, iters=30):
    lab = srgb2lab(px)
    cen = lab[np.random.default_rng(0).choice(len(lab), k, replace=False)]
    for _ in range(iters):
        lbl = ((lab[:, None] - cen[None]) ** 2).sum(-1).argmin(1)
        for i in range(k):
            if (lbl == i).any():
                cen[i] = lab[lbl == i].mean(0)
    lbl = ((lab[:, None] - cen[None]) ** 2).sum(-1).argmin(1)
    return np.array([np.median(px[lbl == i], 0) if (lbl == i).any() else px[0] for i in range(k)]).astype(int)


def read():
    img = np.asarray(Image.open(lp(SRC)).convert("RGB")).astype(int)
    bg = img[..., 1] - np.maximum(img[..., 0], img[..., 2]) > 80
    px = img[~bg]
    sub = px[np.random.default_rng(0).choice(len(px), min(len(px), 20000), replace=False)]
    P = kmeans(sub, K)
    P[np.argmin([lum(c) for c in P])] = OUTLINE
    L = np.full(img.shape[:2], -1, int)
    L[~bg] = ((srgb2lab(px)[:, None] - srgb2lab(P)[None]) ** 2).sum(-1).argmin(1)
    H, W = L.shape
    rows, cols = int((H - OY) // PITCH), int((W - OX) // PITCH)
    out = np.full((rows, cols), -1, int)
    for r in range(rows):
        y0, y1 = int(round(OY + r * PITCH)), int(round(OY + (r + 1) * PITCH))
        for c in range(cols):
            x0, x1 = int(round(OX + c * PITCH)), int(round(OX + (c + 1) * PITCH))
            out[r, c] = np.bincount(L[y0:y1, x0:x1].ravel() + 1, minlength=K + 1).argmax() - 1
    ys, xs = np.nonzero(out >= 0)
    out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    a = np.zeros(out.shape + (4,), np.uint8)
    m = out >= 0
    a[m, :3] = P[out[m]]
    a[m, 3] = 255
    return a


def despeckle(a, keep=()):
    out = a.copy()
    H, W = a.shape[:2]
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if a[y, x, 3] == 0 or (y, x) in keep:
                continue
            c = tuple(int(v) for v in a[y, x, :3])
            nb = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                  if a[y + dy, x + dx, 3] > 0]
            if len(nb) == 4 and c not in nb:
                cnt = Counter(nb)
                top = max(cnt.values())
                if top >= 3:
                    out[y, x, :3] = [k for k, v in cnt.items() if v == top][0]
    return out


def build(keep=KEEP):
    a = read()
    for y, x, c in FIX:
        if c is None:
            a[y, x] = 0
        else:
            a[y, x, :3] = c
            a[y, x, 3] = 255
    a = despeckle(a, keep)
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hem = np.nonzero((a[-HEM_ROWS:, :, 3] > 0).any(0))[0]
    mid = (hem.min() + hem.max()) / 2
    can = np.zeros((128, 128, 4), np.uint8)
    y0 = SOLE_ROW + 1 - a.shape[0]
    x0 = int(round(MID_COL - mid))
    can[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    can, added, darkened = strips.complete_outline(can, color=OUTLINE, feet=SOLE_ROW)
    return can, added, darkened


def review(can, path):
    ys, xs = np.nonzero(can[..., 3] > 0)
    a = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    z = 16
    img = Image.new("RGBA", (a.shape[1] * z + 40, a.shape[0] * z + 40), (200, 200, 200, 255))
    img.alpha_composite(Image.fromarray(a).resize((a.shape[1] * z, a.shape[0] * z), Image.NEAREST), (30, 30))
    d = ImageDraw.Draw(img)
    for y in range(a.shape[0] + 1):
        d.line([(30, 30 + y * z), (30 + a.shape[1] * z, 30 + y * z)], fill=(255, 0, 0, 60))
    for x in range(a.shape[1] + 1):
        d.line([(30 + x * z, 30), (30 + x * z, 30 + a.shape[0] * z)], fill=(255, 0, 0, 60))
    for y in range(0, a.shape[0], 2):
        d.text((4, 30 + y * z + 3), str(y + ys.min()), fill=(0, 0, 0, 255))
    for x in range(0, a.shape[1], 2):
        d.text((30 + x * z + 3, 4), str(x + xs.min()), fill=(0, 0, 0, 255))
    img.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    can, added, darkened = build()
    ys, xs = np.nonzero(can[..., 3] > 0)
    print(f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1}, rows {ys.min()}-{ys.max()}, outline +{added} "
          f"darkened {darkened}, colours {len({tuple(p[:3]) for p in can[can[..., 3] > 0]})}")
    if a.review:
        review(can, a.review)
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT")
        return
    os.makedirs(os.path.dirname(lp(OUT)), exist_ok=True)
    Image.fromarray(can).save(lp(OUT))
    print(OUT)


if __name__ == "__main__":
    main()

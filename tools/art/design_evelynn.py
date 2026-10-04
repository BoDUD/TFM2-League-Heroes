#!/usr/bin/env python3
"""Evelynn's design (assets/source/native/evelynn_native.png): Codex's generated draft A read back on its own grid,
mapped to Codex's palette in CIELAB, cut to twice the target by whole rows and columns, halved by 2x2 blocks.

    python tools/art/design_evelynn.py [--check] [--review OUT.png] [--no-face]

How it came about (2026-10-04): the user picked Codex's picture A (codex_picture/evelynn-model-A.png: League's idle,
the near claw raised beside her chin, the two lashers curling behind her). For step 1 Codex delivered A / B built square
by square on a 34 x 40 grid by its own script (codex_model/evelynn_design_A_1x.png / _B_1x.png: crude) and two generated
drafts that came back twice the asked size (87 and 83 rows for 40). Cutting whole rows down to 40 kept the face and
crushed the body (a deletion pass never takes two neighbouring lines, so it spends them on the cheap legs and lashers);
the options sheet showed Codex's A / B and the drafts halved, and the user took 「3 原稿A减半 40行」. Steps:
  1. the draft codex_model/evelynn_generated_A.png (13 px squares on 1254 x 1254) read back on its own grid (the skill's
     regrid.py, alpha >= 128): 75 x 87;
  2. every square the nearest colour of Codex's 24-colour palette (codex_model/palette.json) in CIELAB;
  3. ROWS / COLS: the lines work/ev/half_ev.py's passes of design_akali.dp_keep kept (the eye lines and the two soles'
     rows never deleted): 72 x 80, twice the target;
  4. every 2x2 block one square: the eye colour if the block holds one; the outline when 2 of its 4 squares are
     outline on the silhouette's edge (3 inside the figure); else the majority of its other colours, ties the darker;
  5. a lone square unlike all four neighbours takes their colour when 3 or 4 of them agree (eyes and lips kept);
  6. FACE: the eyes on one row - the draft's near eye came out on rows 13-14 and the far one on row 14 - both 2 squares
     wide on the near eye's top row with a violet lid above each, skin below (--no-face leaves them as halved);
  7. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64;
  8. strips.complete_outline (one outline square outside every light edge, nothing under the soles).
--check compares the result with the committed evelynn_native.png instead of writing it.
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "evelynn", "codex_model")
RAW = os.path.join(SRC, "evelynn_generated_A.png")
PALETTE = os.path.join(SRC, "palette.json")
OUT = os.path.join(ROOT, "assets", "source", "native", "evelynn_native.png")
SOLE_ROW, MID_COL = 99, 64
FEET_ROWS = 3                     # the lowest rows hold the two feet: their middle goes on MID_COL
ROWS = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
        32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
        62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 80, 82, 84, 85, 86]
COLS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
        32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
        60, 61, 62, 63, 64, 65, 66, 67, 69, 70, 71, 72, 73, 74]
OUTLINE = (0x12, 0x0C, 0x1C)
EYE = (0xFF, 0xD2, 0x1E)
LID = (0x4A, 0x1C, 0x96)          # violet eye shadow above each eye (the draft's own)
SKIN = (0xCA, 0xCA, 0xEE)
LIPS = (0xC0, 0x30, 0x6A)


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


def palette():
    d = json.load(open(lp(PALETTE), encoding="utf-8"))
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in d.values()])


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def halve(a):
    H, W = a.shape[:2]
    out = np.zeros((H // 2, W // 2, 4), np.uint8)
    for y in range(H // 2):
        for x in range(W // 2):
            blk = a[2 * y:2 * y + 2, 2 * x:2 * x + 2].reshape(-1, 4)
            ops = [tuple(int(v) for v in p[:3]) for p in blk if p[3] > 0]
            if len(ops) < 2:
                continue
            cnt = Counter(ops)
            edge = len(ops) < 4
            inner = Counter({k: v for k, v in cnt.items() if k != OUTLINE})
            if EYE in cnt:
                c = EYE
            elif cnt.get(OUTLINE, 0) >= (2 if edge else 3) or not inner:
                c = OUTLINE
            else:
                top = max(inner.values())
                c = min([k for k, v in inner.items() if v == top], key=lum)
            out[y, x, :3] = c
            out[y, x, 3] = 255
    return out


def despeckle(a):
    out = a.copy()
    H, W = a.shape[:2]
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if a[y, x, 3] == 0:
                continue
            c = tuple(int(v) for v in a[y, x, :3])
            if c in (EYE, LIPS):
                continue
            nb = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                  if a[y + dy, x + dx, 3] > 0]
            if len(nb) == 4 and c not in nb:
                cnt = Counter(nb)
                top = max(cnt.values())
                if top >= 3:
                    out[y, x, :3] = [k for k, v in cnt.items() if v == top][0]
    return out


def face(a):
    """Both eyes 2 squares wide on the near eye's top row, a violet lid above each, the rest of the old eye squares skin."""
    eye = np.all(a[..., :3] == np.array(EYE, np.uint8), -1) & (a[..., 3] > 0)
    ys, xs = np.nonzero(eye)
    split = (xs.min() + xs.max()) / 2
    near = [(y, x) for y, x in zip(ys, xs) if x < split]
    far = [(y, x) for y, x in zip(ys, xs) if x >= split]
    row = min(y for y, _ in near)
    nx = min(x for _, x in near)
    fx = min(x for _, x in far)
    for y, x in zip(ys, xs):
        a[y, x, :3] = SKIN
    for x0 in (nx, fx):
        for x in (x0, x0 + 1):
            a[row, x, :3] = EYE
            a[row - 1, x, :3] = LID
            a[row, x, 3] = a[row - 1, x, 3] = 255
    return a, (row, nx, fx)


def build(with_face=True):
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    assert raw.shape[:2] == (87, 75), raw.shape
    P = palette()
    d = ((srgb2lab(raw[..., :3])[:, :, None, :] - srgb2lab(P)[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    op = raw[..., 3] >= 128
    a = np.zeros(raw.shape, np.uint8)
    a[op, :3] = P[idx[op]]
    a[op, 3] = 255
    a = despeckle(halve(a[np.ix_(ROWS, COLS)]))
    eyes = None
    if with_face:
        a, eyes = face(a)
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((a[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    can = np.zeros((128, 128, 4), np.uint8)
    y0 = SOLE_ROW + 1 - a.shape[0]
    x0 = int(round(MID_COL - mid))
    can[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    can, added, darkened = strips.complete_outline(can, color=OUTLINE, feet=SOLE_ROW)
    if eyes:
        eyes = (eyes[0] - ys.min() + y0, eyes[1] - xs.min() + x0, eyes[2] - xs.min() + x0)
    return can, added, darkened, eyes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a 6x review picture")
    ap.add_argument("--no-face", action="store_true")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    can, added, darkened, eyes = build(not a.no_face)
    big = Image.fromarray(can).resize((1024, 1024), Image.NEAREST)
    ys, xs = np.nonzero(can[..., 3] > 0)
    cols = len({tuple(c) for c in can[can[..., 3] > 0][:, :3]})
    print(f"evelynn_native: {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {cols} colours, "
          f"outline +{added} / darkened {darkened}, rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}, eyes {eyes}")
    if a.check:
        old = np.asarray(Image.open(lp(a.out)).convert("RGBA"))
        same = np.array_equal(old, np.asarray(big))
        print("same as the committed file" if same else "DIFFERS from the committed file")
        sys.exit(0 if same else 1)
    big.save(lp(a.out))
    if a.review:
        crop = can[ys.min() - 2:ys.max() + 3, xs.min() - 2:xs.max() + 3]
        im = Image.fromarray(crop).resize((crop.shape[1] * 6, crop.shape[0] * 6), Image.NEAREST)
        bg = Image.new("RGBA", im.size, (92, 98, 86, 255))
        bg.alpha_composite(im)
        ImageDraw.Draw(bg).text((4, 4), "evelynn_native", fill=(255, 255, 255))
        bg.convert("RGB").save(a.review)
    print(a.out)


if __name__ == "__main__":
    main()

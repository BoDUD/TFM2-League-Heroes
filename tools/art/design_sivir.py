#!/usr/bin/env python3
"""Sivir's design (assets/source/native/sivir_native.png): Codex's raw game-size draft read back on its own grid, mapped
to Codex's palette in CIELAB, cut to 40 rows by whole rows and columns.

    python tools/art/design_sivir.py [--check] [--review OUT.png]

How it came about (2026-10-04): the user picked Codex's picture A (codex_picture/sivir-model-A.png: League's idle, a low
wide crouch, the open crossblade at her back hip). Codex's first game-size draft came out 63 squares tall; its own
38-row A / B (resampled) and whole-line cuts of that draft to 38-46 rows were all 「太胖 太丑」 (big cuts keep the limbs'
widths and shorten them); the user took the draft's look (「用这张」) and Codex redrew it a size smaller. Of its five
tries, the second (codex_model/sivir_design_raw.png, 1254 px on black) reads back 49 x 62 squares, the draft's look and
proportions; the user asked for it smaller (「继续缩小点吧 和别的ADC站一起太大了吧」) and picked 40 rows, then 「腿上鞋子模型丢失
修一修」: the boots' rows are kept. Steps:
  1. the black background keyed from the borders (only pure black: the outline is near-black), the ring's hole too;
  2. the raw read back on its own grid (the skill's regrid.py): 49 x 62;
  3. every square the nearest colour of Codex's 24-colour palette (codex_model/sivir_palette.hex) in CIELAB, the two
     eye squares (the raw's teal at (12, 35) and (12, 39)) the eye mint #4FE6D2, which nothing else uses;
  4. the rows and columns kept by work/sv/cut_sivir.py's DP (the head 16 -> 13 rows with the body by the same share,
     the brows, eyes and mouth rows, the knees, shins and boots (rows 39-48) and the eyes' columns never deleted;
     rows 1, 2, 5, 16, 24, 26, 32, 33, 38 go): 40 x 51;
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64;
  6. strips.complete_outline (one outline square outside every light edge, nothing under the soles).
--check compares the result with the committed sivir_native.png instead of writing it.
"""
import argparse
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sivir", "codex_model")
RAW = os.path.join(SRC, "sivir_design_raw.png")
PALETTE = os.path.join(SRC, "sivir_palette.hex")
OUT = os.path.join(ROOT, "assets", "source", "native", "sivir_native.png")
OUTLINE = (0x14, 0x10, 0x1A)
EYE = "#4FE6D2"
EYES = [(12, 35), (12, 39)]       # the eye squares on the raw's grid
SOLE_ROW, MID_COL = 99, 64
ROWS = [0, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 25, 27, 28, 29, 30, 31, 34, 35, 36, 37,
        39, 40, 41, 42, 43, 44, 45, 46, 47, 48]
COLS = [0, 2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 29, 30, 31, 32, 33,
        34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 48, 50, 51, 52, 53, 54, 55, 56, 57, 59, 61]
FEET_ROWS = 3                     # the lowest rows hold the two feet: their middle goes on MID_COL


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def key_black(a):
    """Pure black (max channel <= 4) reached from the borders goes clear, and the enclosed pure black (the ring's hole)."""
    a = a.copy()
    H, W = a.shape[:2]
    bg = a[..., :3].max(2) <= 4
    seen = np.zeros((H, W), bool)
    q = deque()
    for y in range(H):
        for x in range(W):
            if (y in (0, H - 1) or x in (0, W - 1)) and bg[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and bg[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    a[bg, 3] = 0
    return a


def srgb2lab(c):
    c = np.asarray(c, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def palette_map(raw, pal):
    P = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in pal])
    eye = pal.index(EYE)
    cand = [i for i in range(len(pal)) if i != eye]
    d = ((srgb2lab(raw[..., :3])[:, :, None, :] - srgb2lab(P)[None, None, cand]) ** 2).sum(-1)
    idx = np.array(cand)[d.argmin(-1)]
    op = raw[..., 3] > 0
    out = np.zeros_like(raw)
    out[op, :3] = P[idx[op]]
    out[op, 3] = 255
    for y, x in EYES:
        out[y, x, :3] = P[eye]
    return out


def build():
    raw, _, _ = regrid(key_black(np.asarray(Image.open(lp(RAW)).convert("RGBA"))))
    assert raw.shape[:2] == (49, 62), raw.shape
    pal = [line.strip() for line in open(lp(PALETTE)) if line.strip()]
    a = palette_map(raw, pal)[np.ix_(ROWS, COLS)].copy()
    a[a[..., 3] == 0] = 0
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((a[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    can = np.zeros((128, 128, 4), np.uint8)
    y0 = SOLE_ROW + 1 - a.shape[0]
    x0 = int(round(MID_COL - mid))
    can[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    can, added, darkened = strips.complete_outline(can, color=OUTLINE, feet=SOLE_ROW)
    return can, added, darkened


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a 6x review picture")
    a = ap.parse_args()
    can, added, darkened = build()
    big = Image.fromarray(can).resize((1024, 1024), Image.NEAREST)
    ys, xs = np.nonzero(can[..., 3] > 0)
    cols = len({tuple(c) for c in can[can[..., 3] > 0][:, :3]})
    print(f"sivir_native: {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {cols} colours, "
          f"outline +{added} / darkened {darkened}, rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        same = np.array_equal(old, np.asarray(big))
        print("same as the committed file" if same else "DIFFERS from the committed file")
        sys.exit(0 if same else 1)
    big.save(lp(OUT))
    if a.review:
        crop = can[ys.min() - 2:ys.max() + 3, xs.min() - 2:xs.max() + 3]
        im = Image.fromarray(crop).resize((crop.shape[1] * 6, crop.shape[0] * 6), Image.NEAREST)
        bg = Image.new("RGBA", im.size, (92, 98, 86, 255))
        bg.alpha_composite(im)
        ImageDraw.Draw(bg).text((4, 4), "sivir_native", fill=(255, 255, 255))
        bg.convert("RGB").save(a.review)
    print(OUT)


if __name__ == "__main__":
    main()

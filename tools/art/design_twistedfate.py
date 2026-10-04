#!/usr/bin/env python3
"""Twisted Fate's design (assets/source/native/twistedfate_native.png): Codex's generated game-size draft read back on
its own grid, mapped to Codex's palette in CIELAB, cut to 40 rows by whole rows and columns.

    python tools/art/design_twistedfate.py [--check] [--review OUT.png]

How it came about (2026-10-04): the user picked Codex's picture A (codex_picture/twistedfate-model-A.png: League's idle,
the fan of blue, red and gold cards at his near hip). For step 1 Codex delivered A / B built square by square on a 26 x 40
grid by its own script (codex_model/twistedfate_design_A_1x.png / _B_1x.png; the user had their faces redone) and three
generated drafts; the options sheet showed A, B and the drafts cut to 44 and 40 rows, and the user took
「4 原稿删到40行」 - the draft codex_model/generation_selected.png (23 px squares on 1239 x 1269) cut to 40 rows. Steps:
  1. the draft read back on its own grid (the skill's regrid.py): 32 x 59;
  2. every square the nearest colour of Codex's 25-colour palette (codex_model/palette.hex) in CIELAB;
  3. the rows and columns kept by work/tw/cut_gen_tw.py's DP (design_akali.dp_keep, rows first: the face's rows and
     columns round the cyan eye, the eye weighted 12, and the three soles' rows never deleted): 22 x 40;
  4. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64;
  5. strips.complete_outline (one outline square outside every light edge, nothing under the soles).
--check compares the result with the committed twistedfate_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "twistedfate", "codex_model")
RAW = os.path.join(SRC, "generation_selected.png")
PALETTE = os.path.join(SRC, "palette.hex")
OUT = os.path.join(ROOT, "assets", "source", "native", "twistedfate_native.png")
SOLE_ROW, MID_COL = 99, 64
FEET_ROWS = 3                     # the lowest rows hold the two feet: their middle goes on MID_COL
ROWS = [1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 35, 36, 37, 39, 41,
        43, 45, 47, 49, 51, 53, 54, 56, 57, 58]
COLS = [1, 3, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 26, 28, 30]


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
    out = []
    for line in open(lp(PALETTE), encoding="utf-8"):
        t = line.strip().lstrip("#")
        if len(t) >= 6:
            out.append(tuple(int(t[i:i + 2], 16) for i in (0, 2, 4)))
    return np.array(out)


def build():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    assert raw.shape[:2] == (59, 32), raw.shape
    P = palette()
    d = ((srgb2lab(raw[..., :3])[:, :, None, :] - srgb2lab(P)[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    op = raw[..., 3] >= 128
    a = np.zeros(raw.shape, np.uint8)
    a[op, :3] = P[idx[op]]
    a[op, 3] = 255
    a = a[np.ix_(ROWS, COLS)]
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((a[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    can = np.zeros((128, 128, 4), np.uint8)
    y0 = SOLE_ROW + 1 - a.shape[0]
    x0 = int(round(MID_COL - mid))
    can[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    outline = tuple(int(v) for v in P[np.argmin((P * [0.299, 0.587, 0.114]).sum(1))])
    can, added, darkened = strips.complete_outline(can, color=outline, feet=SOLE_ROW)
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
    print(f"twistedfate_native: {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {cols} colours, "
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
        ImageDraw.Draw(bg).text((4, 4), "twistedfate_native", fill=(255, 255, 255))
        bg.convert("RGB").save(a.review)
    print(OUT)


if __name__ == "__main__":
    main()

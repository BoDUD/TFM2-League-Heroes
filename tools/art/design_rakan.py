#!/usr/bin/env python3
"""Rakan's design (assets/source/native/rakan_native.png): Codex's raw game-size draft read back on its own grid, mapped
to Codex's palette in CIELAB, cut to 40 rows by whole rows and columns.

    python tools/art/design_rakan.py [--check] [--review OUT.png]

How it came about (2026-10-04): the user picked Codex's picture A (codex_picture/rakan-model-A.png: League's idle,
the golden feather at his chin, the feather cloak trailing on the ground behind him). For the game-size step Codex
drew a draft (codex_model/generation-original.png, ~24 px squares on 1086 x 1448) that reads back 52 x 39 squares;
its own 40-row versions 1 / 2 (codex_model/rakan_design_*_sprite.png) deleted 12 rows and 9 columns through the face
and the cloak (squeezed eyes, a short cloak). The user picked a cut of the draft itself at 40 rows (「40 行（我删
的）」 among 40 / 44 / 48 and Codex's) and kept its face as it is (「原样」 over three small face edits). Steps:
  1. the draft read back on its own grid (the skill's regrid.py): 52 x 39;
  2. every square the nearest colour of Codex's 23-colour palette (codex_model/palette.json) in CIELAB;
  3. the rows and columns kept by work/rk/cut_rakan.py's DP (the crest 7 -> 4 rows, the head from the white hair's
     top to the chin 13 -> 12, the torso and the legs by their length; the brows', eyes' and mouth's rows 14-18 and
     the face's columns 24-32 never deleted): 40 x 32;
  4. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64;
  5. strips.complete_outline (one outline square outside every light edge, nothing under the soles).
--check compares the result with the committed rakan_native.png instead of writing it.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rakan", "codex_model")
RAW = os.path.join(SRC, "generation-original.png")
PALETTE = os.path.join(SRC, "palette.json")
OUT = os.path.join(ROOT, "assets", "source", "native", "rakan_native.png")
OUTLINE = (0x16, 0x0A, 0x0E)
SOLE_ROW, MID_COL = 99, 64
ROWS = [0, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 21, 23, 24, 25, 27, 28, 29, 30, 31, 33, 35, 37, 38, 40,
        41, 42, 43, 44, 46, 47, 48, 49, 50, 51]
COLS = [0, 4, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
        35, 36, 38]
FEET_ROWS = 3                     # the lowest rows hold the two feet (the cloak's tips end higher): their middle on MID_COL


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


def palette_map(raw, pal):
    P = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in pal])
    d = ((srgb2lab(raw[..., :3])[:, :, None, :] - srgb2lab(P)[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    op = raw[..., 3] > 0
    out = np.zeros_like(raw)
    out[op, :3] = P[idx[op]]
    out[op, 3] = 255
    return out


def feet_mid(a):
    """The middle of the two feet on the lowest FEET_ROWS rows, the cloak's tips left out (they reach the soles' line
    at the far left)."""
    low = a[-FEET_ROWS:, :, 3] > 0
    cols = np.nonzero(low.any(0))[0]
    runs, start = [], cols[0]
    for c0, c1 in zip(cols, cols[1:]):
        if c1 != c0 + 1:
            runs.append((start, c0))
            start = c1
    runs.append((start, cols[-1]))
    feet = runs[-2:] if len(runs) >= 2 else runs
    return (feet[0][0] + feet[-1][1]) / 2


def build():
    raw, size, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    assert raw.shape[:2] == (52, 39), raw.shape
    pal = json.load(open(lp(PALETTE), encoding="utf-8"))["colors"]
    a = palette_map(raw, pal)[np.ix_(ROWS, COLS)].copy()
    a[a[..., 3] == 0] = 0
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    can = np.zeros((128, 128, 4), np.uint8)
    y0 = SOLE_ROW + 1 - a.shape[0]
    x0 = int(round(MID_COL - feet_mid(a)))
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
    print(f"rakan_native: {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {cols} colours, "
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
        ImageDraw.Draw(bg).text((4, 4), "rakan_native", fill=(255, 255, 255))
        bg.convert("RGB").save(a.review)
    print(OUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Jhin's design (assets/source/native/jhin_native.png): Codex's raw game-size draft read back on its own grid, mapped
to Codex's palette in CIELAB, cut to 41 rows by whole rows and columns.

    python tools/art/design_jhin.py [--check] [--review OUT.png]

How it came about (2026-10-03): the user picked Codex's picture A (codex_picture/jhin-model-A.png: League's idle, the
gold hand on the cane-rifle at his far hip, Whisper hanging in the near hand). Asked for a game-size sprite 41 squares
from the hood's top to the soles with a 13-row head (MODEL_PROMPTS.md), Codex's image generator drew 62 x 44 squares
of about 10 px (codex_model/jhin_design_A_raw.png); Codex cut its own A (head 13) and B (head 11) to 41 rows
(codex_model/jhin_design_*_1x.png, HANDOFF.md), which turned the bare near arm purple and broke Whisper up. Shown
those two next to three cuts of the raw made here (41 rows head 13 / 41 head 11 / 46 head 15), the user picked
「1 新41 头13」. Steps:
  1. the raw read back on its own grid (the skill's regrid.py): 62 x 44;
  2. every square the nearest colour of Codex's 24-colour palette (codex_model/jhin_palette.hex) in CIELAB - in RGB
     the cape's tan swirls (about #C9AC73) went to the skin colour - and the two eye squares (the raw's magenta at
     (9, 23) and (9, 28)) the eye pink #FF6EB4, which nothing else uses;
  3. the rows and columns kept by work/jh/cut_jhin.py (cut_kennen.py's DP: about 12% a step, the cheapest lines first,
     never two neighbours in one step, a line whose deletion splits the figure charged; the head down to 13 rows, the
     torso and the legs giving up the rest by length; the brows, eyes and mouth rows, the cane's columns, the eyes'
     columns and Whisper's columns never deleted): 41 x 28, 23 colours;
  4. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64;
  5. strips.complete_outline (one outline square outside every light edge, nothing under the soles).
--check compares the result with the committed jhin_native.png instead of writing it.
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

SRC = os.path.join(ROOT, "assets", "source", "jhin", "codex_model")
RAW = os.path.join(SRC, "jhin_design_A_raw.png")
PALETTE = os.path.join(SRC, "jhin_palette.hex")
OUT = os.path.join(ROOT, "assets", "source", "native", "jhin_native.png")
OUTLINE = (0x0E, 0x08, 0x14)
EYE = "#FF6EB4"
EYES = [(9, 23), (9, 28)]          # the eye squares on the raw's grid
SOLE_ROW, MID_COL = 99, 64
# the raw's lines kept for 41 rows (work/jh/cut_jhin.py <out> --heads 13 --cols 29)
ROWS = [0, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 25, 26, 27, 28, 29, 30, 32, 33, 34, 36, 38, 40, 41, 42,
        44, 45, 46, 47, 48, 50, 52, 54, 56, 57, 58, 61]
COLS = [0, 7, 8, 9, 10, 11, 13, 14, 17, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 33, 34, 35, 36, 37, 38, 39, 40, 41, 43]
FEET_ROWS = 3                     # the lowest rows hold the two feet: their middle goes on MID_COL
# The right (near) hand, traced from League's idle (2026-10-03, the user: 「右手的模型看起来有点不自然」): the cut left a
# 4-row skin stub ending in outline over Whisper's grip - no cuff, no hand. League's arm: the bare forearm, a purple
# cuff, a hand round the ivory grip's top. Canvas (x, y) of the first character, then rows: a palette character of
# jhin_palette.hex (0-9 a-n), "." clear, " " kept.
CH = "0123456789abcdefghijklmn"
HAND = (64, 80, ["4",         # his dark side under the cape, where the cut left a slit of ground (10 squares between
                 "4065",      # the arm and the body); the cuff (light and dark purple) where the stub narrowed
                 " 40ii",     # the hand round the grip's top, skin over shadow, outlined against his side; the
                 " 40hi",     # gold pommel at (69, 83) kept
                 "  00h"])    # a finger on the grip


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
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    assert raw.shape[:2] == (62, 44), raw.shape
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
    hx, hy, rows = HAND
    for dy, row in enumerate(rows):
        for dx, c in enumerate(row):
            if c != " ":
                rgb = [int(pal[CH.index(c)][i:i + 2], 16) for i in (1, 3, 5)] if c != "." else None
                can[hy + dy, hx + dx] = (0, 0, 0, 0) if c == "." else (*rgb, 255)
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
    print(f"jhin_native: {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {cols} colours, "
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
        ImageDraw.Draw(bg).text((4, 4), "jhin_native", fill=(255, 255, 255))
        bg.convert("RGB").save(a.review)
    print(OUT)


if __name__ == "__main__":
    main()

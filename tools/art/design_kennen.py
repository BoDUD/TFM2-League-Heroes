#!/usr/bin/env python3
"""Kennen's design (assets/source/native/kennen_native.png): Codex's design A cut to a yordle's size by whole rows and
columns, Codex's own face kept.

    python tools/art/design_kennen.py [--check] [--review OUT.png]

How it came about (2026-10-02): the user picked Codex's picture A (codex_picture/kennen-model-A.png: League's idle,
both clawed hands forward, the big gold shuriken on his back). Asked for a game-size sprite with the hood 32 rows over
the soles (MODEL_PROMPTS.md), Codex drew A 48 rows from the shuriken's top to the soles (the hood about 40) x 34 and
B 43 x 29 (codex_model/HANDOFF.md). Shown A and B cut to 44 / 41 / 38 and 40 / 38 / 36 rows, the user picked A38, then
kept Codex's own eyes ("凯南眼睛用codex原稿") and asked for about 37 rows, giving up pixels elsewhere ("用这个 缩小到37左右
可以牺牲点别的地方的像素 ... 约德尔人体型不能太大"). Steps, on Codex's own squares (no square redrawn):
  1. codex_model/kennen_design_A_1x.png (21 colours, one outline colour, soles on row 99);
  2. the rows and columns kept by work/kn/cut_kennen.py (league_leblanc's cut: about 10% a step, the cheapest lines
     first - those that differ least from a neighbour - never two neighbours in one step, a line whose deletion splits
     the figure charged; rows by region: over the hood 1.4, the hood 0.9, the robe 1.0, the legs 0.5; columns: left of
     the face 1.3, the face 0.6, right of it 1.0), never deleting Codex's face (rows 71-77, columns 63-75): 37 x 27,
     the hood 31 rows over the soles (Teemo is 38 with his hat, Tristana 34);
  3. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64;
  4. strips.complete_outline (one outline square outside every light edge, nothing under the soles).
The hands stay as Codex drew them (a redraw was shown and the user kept Codex's: "凯南的手就用调整前codex的").
--check compares the result with the committed kennen_native.png instead of writing it.
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

DRAFT = os.path.join(ROOT, "assets", "source", "kennen", "codex_model", "kennen_design_A_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "kennen_native.png")
OUTLINE = (0x0B, 0x06, 0x0E)
SOLE_ROW, MID_COL = 99, 64
# Codex's canvas lines kept for 37 rows (work/kn/cut_kennen.py A <out> --total 37)
ROWS = [52, 54, 56, 57, 58, 59, 61, 62, 63, 64, 67, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 85, 86, 87,
        88, 89, 90, 93, 94, 95, 96, 97, 98, 99]
COLS = [47, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 80]
FEET_ROWS = 4                     # the lowest rows hold the two shoes: their middle goes on MID_COL


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def build():
    raw = np.asarray(Image.open(lp(DRAFT)).convert("RGBA"))
    a = raw[np.ix_(ROWS, COLS)].copy()
    a[a[..., 3] == 0] = 0
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
    print(f"kennen_native: {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {cols} colours, "
          f"outline +{added} / darkened {darkened}, soles row {ys.max()}")
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
        ImageDraw.Draw(bg).text((4, 4), "kennen_native", fill=(255, 255, 255))
        bg.convert("RGB").save(a.review)
    print(OUT)


if __name__ == "__main__":
    main()

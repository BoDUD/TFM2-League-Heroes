#!/usr/bin/env python3
"""Shaco's design (assets/source/native/shaco_native.png): Codex's 46-row redraw v4, version A, as drawn.

    python tools/art/design_shaco.py [--check]

How it came about (2026-10-01): Codex's picture A (assets/source/shaco/PICTURE_PROMPT.md, the red jacket front) was the
user's pick. Codex's game-size drawings at 40 rows were "太模糊了" (gold specks, one-square eyes), then too stubby
(a script-placed chibi). The user liked Codex's clean big-block picture at 76 squares and asked for "稍微放大" - a
straight cut to 40-48 rows broke its checks and mask into specks - so Codex drew it square by square at 46 rows
(assets/source/shaco/MODEL_PROMPTS_46.md -> codex_model/v4: 37x46, 17 colours, a strict 8x grid, the outline closed,
two 2x2 eyes in #03A7E9 with a #B8FAFF core). My redrawn faces were turned down ("用codex版本", "你做的两版本都不行"):
version A goes in unchanged except for its place and the ruff:
  1. codex_model/v4/shaco_native46_A_1x.png as drawn (alpha 0/255);
  2. moved 4 columns left so the middle of the feet (row 99) sits on column 64 like the other heroes;
  3. the ruff closed under the chin (RUFF, 19 squares in rows 71-75): Codex joined the gold ruff to the neck while
     drawing the strips (codex_strips/HANDOFF.md, "neck / ruff junction", the user approved it there); every
     strip frame carries it, the head is untouched;
  4. shown at 8x on the 128x128 canvas (soles on row 99).
--check compares the result with the committed shaco_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DRAFT = os.path.join(ROOT, "assets", "source", "shaco", "codex_model", "v4", "shaco_native46_A_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "shaco_native.png")
SHIFT = -4
EYE = (0x03, 0xA7, 0xE9)          # the eyes' cyan, used nowhere else (import_native steadies the loops on it)
# (row, column, colour) on the shifted canvas: the ruff's gold and shadow carried across the neck, the jacket's navy
# under it (codex_strips/neck_validation.json: box x 62-72, y 71-76)
RUFF = [(71, 69, "F3BF27"), (71, 70, "8A5D25"), (71, 71, "0F0419"), (72, 62, "F3BF27"), (72, 68, "F3BF27"),
        (72, 69, "F3BF27"), (72, 70, "8A5D25"), (73, 65, "F3BF27"), (73, 66, "F3BF27"), (73, 67, "8A5D25"),
        (73, 68, "F3BF27"), (73, 69, "8A5D25"), (74, 64, "F3BF27"), (74, 65, "F3BF27"), (74, 66, "8A5D25"),
        (74, 67, "1D264A"), (74, 68, "1D264A"), (75, 67, "1D264A"), (75, 68, "1D264A")]


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def build():
    a = np.asarray(Image.open(lp(DRAFT)).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    out = np.roll(a, SHIFT, axis=1)
    for y, x, c in RUFF:
        out[y, x] = [int(c[i:i + 2], 16) for i in (0, 2, 4)] + [255]
    ys, xs = np.nonzero(out[..., 3])
    assert ys.max() == 99 and ys.min() == 54, (ys.min(), ys.max())
    feet = np.nonzero(out[99, :, 3])[0]
    assert abs((feet.min() + feet.max()) / 2 - 64) <= 1, feet
    eye = np.all(out[..., :3] == np.array(EYE, np.uint8), -1) & (out[..., 3] > 0)
    assert eye.sum() == 4, eye.sum()          # two cyan squares an eye, a #B8FAFF core and a dark corner
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = build()
    big = np.repeat(np.repeat(out, 8, 0), 8, 1)
    if a.check:
        cur = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(cur, big) else "DIFFERENT")
        return
    Image.fromarray(big).save(lp(OUT))
    ys, xs = np.nonzero(out[..., 3])
    print(OUT, f"{xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}",
          len({tuple(c) for c in out[out[..., 3] > 0][:, :3].tolist()}), "colours")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Sona's design (assets/source/native/sona_native.png): Codex's game-size design B as drawn, one hair square recoloured.

    python tools/art/design_sona.py [--check]

How it came about (2026-10-02): Codex drew the picture (assets/source/sona/PICTURE_PROMPT.md; A = League's idle, the
Etwahl level at her hips, both hands on the strings, taken for the user, who asked to go on whenever Codex finished),
then the 40-row game-size sprite in two versions (MODEL_PROMPTS.md; codex_model/HANDOFF.md: A a 10-square head, B a
12-square one, both 40 x 34 squares, 23 colours, alpha 0/255). B was taken - the bigger face reads at game size, as
Nocturne's, Kai'Sa's and LeBlanc's B did. Steps:
  1. codex_model/sona_design_B_1x.png as drawn (one 8-connected piece, 908 squares: Janna 902, Taric 907, Thresh 890);
  2. the eye colours kept to the eyes: the pupil's dark teal also sat in one square of the near twin tail (row 71,
     column 53) - it takes the tail's dark blue-teal, so import_native can find the eyes by colour;
  3. already on the standing point: the hem's lowest row on row 99, its middle on column 64, the standing point (64, 88)
     11 rows above it as for the other heroes' soles;
  4. shown at 8x on the 128x128 canvas.
--check compares the result with the committed sona_native.png instead of writing it.
"""
import argparse
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DRAFT = os.path.join(ROOT, "assets", "source", "sona", "codex_model", "sona_design_B_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "sona_native.png")
SOLE_ROW, MID_COL = 99, 64
PUPIL = (0x0C, 0x77, 0x7A)       # the eyes' dark teal pupils (row 74), used nowhere else after step 2
IRIS = (0x22, 0xC9, 0xB8)        # the irises (row 75)
SHINE = (0xFF, 0xFF, 0xFF)       # the highlights (row 74)
FIX = {(71, 53): (0x09, 0x56, 0x7C)}     # (row, column): colour - the tail's dark blue-teal


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def build():
    a = np.asarray(Image.open(lp(DRAFT)).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    a[a[..., 3] == 0] = 0
    for (y, x), c in FIX.items():
        assert tuple(a[y, x, :3]) == PUPIL, (y, x, a[y, x])
        a[y, x, :3] = c
    ys, xs = np.nonzero(a[..., 3])
    low = np.nonzero(a[ys.max(), :, 3])[0]
    assert ys.max() == SOLE_ROW and int(round((low.min() + low.max()) / 2)) == MID_COL, (ys.max(), low)
    assert (ys.max() - ys.min() + 1, xs.max() - xs.min() + 1) == (40, 34)
    for col, n in ((PUPIL, 2), (IRIS, 4), (SHINE, 2)):
        m = np.all(a[..., :3] == np.array(col, np.uint8), -1) & (a[..., 3] > 0)
        assert m.sum() == n and set(np.nonzero(m)[0].tolist()) <= {74, 75}, (col, m.sum())
    return a


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
    print(OUT, f"{xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}", f"rows {ys.min()}-{ys.max()}",
          len({tuple(c) for c in out[out[..., 3] > 0][:, :3].tolist()}), "colours", int((out[..., 3] > 0).sum()), "squares")


if __name__ == "__main__":
    main()

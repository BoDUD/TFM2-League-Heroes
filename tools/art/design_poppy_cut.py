#!/usr/bin/env python3
"""Poppy's design: a step-1 take (hd/model<take>.png, design_poppy_model.py) brought to HAIR rows from the pigtail top
to the soles (36 game px x PPU 1.3 = 47, the user's pick 2026-10-18) by design_rell_cut.even_cut: whole rows /
columns dropped one per equal window, never the face's lines (FACE), the haft's columns (HAFT) nor two neighbours.

    python tools/art/design_poppy_cut.py [--take B2] [--hair 47]    # writes hd/model<take>_cut.png (+ _8x)

B-2 reads 46 x 60 (51 rows pigtail top to soles, hair top row 9); B-1 54 x 66 (55 rows).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_rell_cut as RC  # noqa: E402
from design_poppy_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "poppy", "hd")
HAIR_TOP = {"B1": 11, "B2": 9}
FACE = {"B1": (28, 42, 24, 52), "B2": (23, 37, 17, 45)}   # rows / cols of the brows, eyes, ears, mouth
HAFT = {"B1": (9, 16), "B2": (6, 13)}                      # columns of the haft with its outline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", default="B2")
    ap.add_argument("--hair", type=int, default=47)
    a = ap.parse_args()
    d = np.asarray(Image.open(lp(os.path.join(HD, f"model{a.take}.png"))).convert("RGBA"))
    k = a.hair / (d.shape[0] - HAIR_TOP[a.take])
    rows, cols = round(d.shape[0] * k), round(d.shape[1] * k)
    r0, r1, c0, c1 = FACE[a.take]
    h0, h1 = HAFT[a.take]
    keep_c = list(range(c0, c1 + 1)) + list(range(h0, h1 + 1))
    cut = RC.even_cut(d, rows, cols, (list(range(r0, r1 + 1)), keep_c))
    Image.fromarray(cut).save(lp(os.path.join(HD, f"model{a.take}_cut.png")))
    Image.fromarray(np.repeat(np.repeat(cut, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"model{a.take}_cut_8x.png")))
    print(a.take, d.shape[1], "x", d.shape[0], "->", cut.shape[1], "x", cut.shape[0])


if __name__ == "__main__":
    main()

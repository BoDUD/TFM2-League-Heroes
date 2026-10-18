#!/usr/bin/env python3
"""Poppy's step-1 game-size designs read back on their own grid, one palette for both.

    python tools/art/design_poppy_model.py [--size B1 B2]   # writes assets/source/poppy/hd/model{B1,B2}.png (+ _8x)

Step 1 (assets/source/poppy/codex_model, 2026-10-18, Codex new-chat-11): two takes of design B (the hammer upright)
on 1254 squares, asked 21 px squares and 47 rows from the pigtail top to the soles. The outline steps at 6x measure
~17 px (B-1; regrid's own guess 17) and ~20 px (B-2; regrid 20). The final files equal their raw/ originals (B-1's
first raw touched the bottom edge and was redrawn). regrid.py reads each one pixel per drawn square; the colours of
both are cut together by k-means in Lab (design_varus.kmeans), alpha 0/255.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402
from design_poppy_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "poppy", "codex_model")
OUT = os.path.join(ROOT, "assets", "source", "poppy", "hd")
COLOURS = 40
SIZES = (17.0, 20.0)


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"poppy-model-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", nargs=2, type=float, default=SIZES, help="square sizes of B-1 and B-2 in px")
    a = ap.parse_args()
    A, B = read("B-1", a.size[0]), read("B-2", a.size[1])
    h = max(A.shape[0], B.shape[0])
    both = np.zeros((h, A.shape[1] + B.shape[1], 4), np.uint8)
    both[:A.shape[0], :A.shape[1]] = A
    both[:B.shape[0], A.shape[1]:] = B
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    for name, part in (("modelB1", out[:A.shape[0], :A.shape[1]]), ("modelB2", out[:B.shape[0], A.shape[1]:])):
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 8, 0), 8, 1)).save(lp(os.path.join(OUT, f"{name}_8x.png")))
        print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()

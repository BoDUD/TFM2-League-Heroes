#!/usr/bin/env python3
"""Sejuani's step-0 pictures read back on their own grid, A and B on one palette.

    python tools/art/design_sejuani_hd.py [--a 5.6] [--b 5.6]   # writes assets/source/sejuani/hd/{A,B}.png (+ _4x)

Step 0 (assets/source/sejuani/codex_picture/sejuani-picture, 2026-10-24, Codex 2026-10-24/new-chat-4): A her idle on
Bristle 3/4 front, B Arctic Assault's charge, raw on 1254 squares (asked 1536 and 11 px squares; soft alpha, no exact
grid, far finer than asked). Codex's squares: the outline's steps at 6x about 4.5-5 px, the colour edges' period (FFT
of the edge counts per column / row) 5.1-5.7 across and noisy down; regrid is given a little above (it splits rows
below the real square).
Every picture is read on SIZE px squares, one pixel per drawn square; the colours of the two cut to COLOURS together by
k-means in Lab (design_varus.kmeans), alpha 0/255.
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


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "sejuani", "codex_picture", "sejuani-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "sejuani", "hd")
GROUPS = ((("A", "B"), 36),)   # pictures sharing one palette, and its colours
FILES = {"A": "sejuani-A-original.png", "B": "sejuani-B-original.png"}
SIZES = {"A": 5.6, "B": 5.6}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, FILES[name]))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=float, default=SIZES["A"])
    ap.add_argument("--b", type=float, default=SIZES["B"])
    a = ap.parse_args()
    SIZES.update(A=a.a, B=a.b)
    os.makedirs(lp(OUT), exist_ok=True)
    for names, colours in GROUPS:
        parts = [read(n, SIZES[n]) for n in names]
        h = max(p.shape[0] for p in parts)
        both = np.zeros((h, sum(p.shape[1] for p in parts), 4), np.uint8)
        x = 0
        for p in parts:
            both[:p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1]
        op = both[..., 3] > 0
        idx, pal = V.kmeans(both, colours)
        out = np.zeros_like(both)
        out[op, :3] = pal[idx[op]]
        out[op, 3] = 255
        x = 0
        for name, p in zip(names, parts):
            part = out[:p.shape[0], x:x + p.shape[1]]
            x += p.shape[1]
            part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
            Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
            Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
            print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Singed's step-0 pictures read back on their own grid, A and SA on one palette.

    python tools/art/design_singed_hd.py [--a 8.2] [--sa 8.6]   # writes assets/source/singed/hd/{A,SA}.png (+ _4x)

Step 0 (assets/source/singed/codex_picture/singed-picture, 2026-10-23, Codex 2026-10-23/new-chat-6): A his idle 3/4
front, SA his side (still a little 3/4, Codex's HANDOFF says so), raw on 1254 squares (asked 1536 and 11 px squares; soft
alpha, no exact grid; raw/singed-A-initial.png is Codex's first try, bigger, kept as its reference). Codex's squares by
the period of the colour edges (FFT of the edge counts per column / row): A about 8.0 x 7.4, SA 7.2 x 8.0; regrid is
given a little above (it splits rows below the real square). Every picture is read on SIZE px squares, one pixel per
drawn square; the colours of the two cut to COLOURS together by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "singed", "codex_picture", "singed-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "singed", "hd")
GROUPS = ((("A", "SA"), 36),)   # pictures sharing one palette, and its colours
FILES = {"A": "singed-A-generated.png", "SA": "singed-SA-generated.png"}
SIZES = {"A": 8.2, "SA": 8.6}


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
    ap.add_argument("--sa", type=float, default=SIZES["SA"])
    a = ap.parse_args()
    SIZES.update(A=a.a, SA=a.sa)
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

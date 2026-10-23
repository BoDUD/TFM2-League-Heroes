#!/usr/bin/env python3
"""Zac's step-0 pictures read back on their own grid, A and SA on one palette.

    python tools/art/design_zac_hd.py   # writes assets/source/zac/hd/{A,SA}.png (+ _4x)

Step 0 (assets/source/zac/codex_picture/zac-picture, 2026-10-23, Codex 2026-10-23/new-chat-5): A his idle 3/4 front,
SA his side, raw on 1254 squares (asked 1536 and 11 px squares; soft alpha, no exact grid; raw/zac-A-first-draft-rejected
is Codex's dropped try). Codex's squares by the period of the colour edges (FFT of the edge counts per column / row):
A about 10.5 x 11.1, SA 10.4 x 10.3; regrid is given a little above each (it splits rows below the real square).
Codex's own zac-A.png / zac-SA.png are cut to 58 rows by nearest samples (muddier) - not used. Every picture is read on
SIZE px squares, one pixel per drawn square (the RAW drafts); the colours of the two cut to COLOURS together by k-means
in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "zac", "codex_picture", "zac-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "zac", "hd")
GROUPS = ((("A", "SA"), 32),)   # pictures sharing one palette, and its colours
FILES = {"A": "zac-A-raw.png", "SA": "zac-SA-raw.png"}
SIZES = {"A": 11.5, "SA": 11.0}


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
    ap.parse_args()
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

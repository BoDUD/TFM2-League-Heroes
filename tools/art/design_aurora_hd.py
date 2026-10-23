#!/usr/bin/env python3
"""Aurora's step-0 pictures read back on their own grid, one palette for both.

    python tools/art/design_aurora_hd.py   # writes assets/source/aurora/hd/{A,SA}.png (+ _4x)

Step 0 (assets/source/aurora/codex_picture/aurora-picture, 2026-10-23, Codex 2026-10-23/new-chat-2): A her idle 3/4
front (Codex's third try, raw/aurora-A-final.png; raw/aurora-A-initial.png the dropped first), SA her side, raw on 1254
squares (asked 1536 and 11 px squares; soft alpha, no exact grid). Codex's squares, counted on the outline's steps at
4x: A about 10 px, SA drawn finer, about 7. regrid's peak spacing has to be given a little above the real square, or it
splits rows (A at 10: 9.3 px columns but 8.7 px rows, 126 rows, the figure 7% taller): A read on 11 (columns 9.8, rows
9.95 - square), SA on 7.5 (7.3 / 7.3). Both come back about 110-116 rows ear tip to soles against the 66 asked. Every
picture is read on
SIZE px squares, one pixel per drawn square (the RAW drafts, not Codex's own cut); the painted colours of the two cut
to COLOURS together by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "aurora", "codex_picture", "aurora-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "aurora", "hd")
GROUPS = ((("A", "SA"), 40),)   # pictures sharing one palette, and its colours
FILES = {"A": "aurora-A-final.png", "SA": "aurora-SA.png"}
SIZES = {"A": 11.0, "SA": 7.5}


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

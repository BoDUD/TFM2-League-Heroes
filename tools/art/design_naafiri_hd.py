#!/usr/bin/env python3
"""Naafiri's step-0 pictures read back on their own grid, one palette for all four.

    python tools/art/design_naafiri_hd.py   # writes assets/source/naafiri/hd/{A,SA,P,SP}.png (+ _4x)

Step 0 (assets/source/naafiri/codex_picture, 2026-10-21, Codex new-chat-3): A her idle 3/4 front, SA her side-on, P a
packmate 3/4 front, SP a packmate side-on. Codex scaled its 1254 px drawings onto the asked 1536 layout by nearest
neighbour (uneven squares), so the raw drawings (codex_picture/raw) are read. regrid.py's squares: A 8, SA 10, P 9,
SP 10 px - so A reads 88 squares tall, SA 59, P 67, SP 48 (asked 36 and 20: each on its own scale). Each is read one
pixel per drawn square; the painted colours of the four are cut to COLOURS together by k-means in Lab
(design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "naafiri", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "naafiri", "hd")
COLOURS = 48
NAMES = ("A", "SA", "P", "SP")
SIZES = {"A": 8.0, "SA": 10.0, "P": 9.0, "SP": 10.0}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"naafiri-{name}-raw.png"))).convert("RGBA")).copy()
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
    parts = [read(n, SIZES[n]) for n in NAMES]
    h = max(p.shape[0] for p in parts)
    both = np.zeros((h, sum(p.shape[1] for p in parts), 4), np.uint8)
    x = 0
    for p in parts:
        both[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    x = 0
    for name, p in zip(NAMES, parts):
        part = out[:p.shape[0], x:x + p.shape[1]]
        x += p.shape[1]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()

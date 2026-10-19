#!/usr/bin/env python3
"""Quinn's step-0 pictures read back on their own grid, one palette for all four.

    python tools/art/design_quinn_hd.py [--size A B V R]   # writes assets/source/quinn/hd/{A,B,V,R}.png (+ _4x)

Step 0 (assets/source/quinn/codex_picture/quinn-picture, 2026-10-19, Codex new-chat-4): A (League's idle, the
crossbow raised), B (standing, the arms hanging down), V (Valor gliding, side view) and R (Quinn riding Valor) on 1254
squares (asked 1536 and 11 px squares; every picture came at its own square size). regrid's own guesses, checked at
4-6x against the outline steps: A 11 px (85 x 100 squares), B 6 px (67 x 136), V 10.5 (119 x 101), R 7.5 (155 x 119).
Its HANDOFF: soft edges, a semi-transparent rim. regrid.py reads each one pixel per drawn square; the painted colours
of all four are cut to COLOURS together by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "quinn", "codex_picture", "quinn-picture")
OUT = os.path.join(ROOT, "assets", "source", "quinn", "hd")
COLOURS = 48
SIZES = (11.0, 6.0, 10.5, 7.5)
FILES = {"A": "quinn-A.png", "B": "quinn-B.png", "V": "valor-V.png", "R": "quinn-R.png"}


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
    ap.add_argument("--size", nargs=4, type=float, default=SIZES, help="square sizes of A, B, V and R in px")
    a = ap.parse_args()
    if not os.path.exists(lp(OUT)):
        os.mkdir(lp(OUT))
    parts = {k: read(k, sz) for k, sz in zip("ABVR", a.size)}
    h = max(p.shape[0] for p in parts.values())
    both = np.zeros((h, sum(p.shape[1] for p in parts.values()), 4), np.uint8)
    x = 0
    for p in parts.values():
        both[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    x = 0
    for name, p in parts.items():
        part = out[:p.shape[0], x:x + p.shape[1]]
        x += p.shape[1]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()

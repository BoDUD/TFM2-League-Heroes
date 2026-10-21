#!/usr/bin/env python3
"""Ornn's step-0 pictures read back on a fine grid, one palette for both.

    python tools/art/design_ornn_hd.py [--size 6]   # writes assets/source/ornn/hd/{A,B}.png (+ _4x)

Step 0 (assets/source/ornn/codex_picture, 2026-10-21, Codex new-chat): A (3/4, League's wide horns and both hammers),
B (3/4, the horns curled tight, smaller hammers, the molten fist clearer) on 1254 squares (asked 1536 and 11 px
squares; its HANDOFF says no even grid and half-transparent edges), so the raws are read at --size px, finer than any drawn square: this
readback only feeds the size review (review_ornn_size.py brings it down to the game's squares); the game-size design is
step 1 (Codex on the grid). The painted colours of both are cut to COLOURS together by k-means in Lab
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


SRC = os.path.join(ROOT, "assets", "source", "ornn", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "ornn", "hd")
COLOURS = 40
NAMES = ("A", "B")


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"ornn-{name}-raw.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=float, default=6.0, help="square size the raws are read at, px")
    a = ap.parse_args()
    if not os.path.exists(lp(OUT)):
        os.mkdir(lp(OUT))
    parts = {k: read(k, a.size) for k in NAMES}
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

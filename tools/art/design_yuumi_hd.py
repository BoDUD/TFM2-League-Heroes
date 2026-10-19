#!/usr/bin/env python3
"""Yuumi's step-0 pictures read back on their own grid, one palette for all three.

    python tools/art/design_yuumi_hd.py [--size A B C]   # writes assets/source/yuumi/hd/{A,B,C}.png (+ _4x)

Step 0 (assets/source/yuumi/codex_picture, 2026-10-19, Codex new-chat-5): A (League's idle in the open book, 3/4 front),
B (lying on the open book laid flat: the attached look) and C (the closed book) on 1254 squares (asked 1536 and 11 px
squares), each filling its canvas (not one scale). regrid's own square guesses: A 9, B 8, C 9 (the outline steps at 4x
agree; the eyes are drawn finer). Its HANDOFF: soft edges, semi-transparent rim.
regrid.py reads each one pixel per drawn square; the painted colours of all three are cut to COLOURS together by k-means
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


SRC = os.path.join(ROOT, "assets", "source", "yuumi", "codex_picture", "yuumi-picture")
OUT = os.path.join(ROOT, "assets", "source", "yuumi", "hd")
COLOURS = 40
SIZES = (9.0, 8.0, 9.0)
BODY_TOP = {"A": 0, "B": 0, "C": 0}    # first row of the figure counted in its height (the antenna's orb)


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"yuumi-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", nargs=3, type=float, default=SIZES, help="square sizes of A, B and C in px")
    a = ap.parse_args()
    if not os.path.exists(lp(OUT)):
        os.mkdir(lp(OUT))
    parts = {n: read(n, sz) for n, sz in zip("ABC", a.size)}
    h = max(p.shape[0] for p in parts.values())
    both = np.zeros((h, sum(p.shape[1] for p in parts.values()), 4), np.uint8)
    x, at = 0, {}
    for n, p in parts.items():
        both[:p.shape[0], x:x + p.shape[1]] = p
        at[n] = x
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    for n, p in parts.items():
        part = out[:p.shape[0], at[n]:at[n] + p.shape[1]]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{n}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{n}_4x.png")))
        print(n, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()

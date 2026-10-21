#!/usr/bin/env python3
"""Shyvana's step-0 pictures read back on their own grid, one palette for all four.

    python tools/art/design_shyvana_hd.py   # writes assets/source/shyvana/hd/{A,SA,D,SD}.png (+ _4x)

Step 0 (assets/source/shyvana/codex_picture, 2026-10-21, Codex new-chat-2): A her idle 3/4 front, SA her side-on, D the
dragon 3/4 front, SD the dragon side-on, on 1254 squares (asked 1536 and 11 px squares; its HANDOFF: soft edges, the four
not on one scale, the side views still a little 3/4). regrid.py's squares: A 8, SA 6, D 10, SD 6 px (the outline steps
at 4x agree) - so A reads 67 squares tall, SA 81, D 57, SD 92. The user has not yet said whether the side views are
wanted (Warwick, Mel and Vel'Koz were 3/4 only), so all four are read. Each is read one pixel per drawn square; the
painted colours of the four are cut to COLOURS together by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "shyvana", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "shyvana", "hd")
COLOURS = 48
NAMES = ("A", "SA", "D", "SD")
SIZES = {"A": 8.0, "SA": 6.0, "D": 10.0, "SD": 6.0}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"shyvana-{name}.png"))).convert("RGBA")).copy()
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

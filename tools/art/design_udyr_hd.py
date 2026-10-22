#!/usr/bin/env python3
"""Udyr's step-0 pictures read back on their own grid, one palette for all five.

    python tools/art/design_udyr_hd.py   # writes assets/source/udyr/hd/{A,SA,Q,E,R}.png (+ _4x)

Step 0 (assets/source/udyr/codex_picture, 2026-10-22, Codex 2026-10-22/new-chat-2): A the plain guard idle 3/4 front,
SA its side (Codex's own HANDOFF: still near 3/4, drawn smaller), Q the bear stance, E the ram stance, R the phoenix
stance, raw on 1254 squares (asked 1536 and 11 px squares; soft alpha, no exact grid). Codex's squares are about 8 px
(regrid's own measure: A, Q, R 8.0; E 7.0 and SA 10.0 there, but the outline steps at 8x count 8 on both): every
picture is read on SIZE px squares, one pixel per drawn square; the painted colours of the five are cut to COLOURS
together by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "udyr", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "udyr", "hd")
COLOURS = 48
NAMES = ("A", "SA", "Q", "E", "R")
SIZES = {"A": 8.0, "SA": 8.0, "Q": 8.0, "E": 8.0, "R": 8.0}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"udyr-{name}.png"))).convert("RGBA")).copy()
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

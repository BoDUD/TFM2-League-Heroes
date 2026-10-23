#!/usr/bin/env python3
"""Azir's step-0 pictures read back on their own grid: Azir (A, SA) on one palette, the soldier and the guard (T, U,
US) on another, the Sun Disc (D) on its own.

    python tools/art/design_azir_hd.py   # writes assets/source/azir/hd/{A,SA,T,U,US,D}.png (+ _4x)

Step 0 (assets/source/azir/codex_picture/azir-picture, 2026-10-23, Codex 2026-10-23/new-chat-4): A his idle 3/4 front,
SA his side, T the sand soldier, U / US the Imperial Guard front / side, D the Sun Disc; raw on 1254 squares (asked
1536 and 11 px squares; soft alpha, no exact grid; raw/rejected_* are Codex's dropped tries). Codex's squares by the
period of the colour edges (FFT of the edge counts per column / row): A about 11, SA 9.8, T 15, U 14, US 13.9, D 12.2;
regrid is given a little above each (it splits rows below the real square). Codex's own logical/ cut is resized
(A 61x93 brought to 55x84) - not used. Every picture is read on SIZE px squares, one pixel per drawn square (the RAW
drafts); the painted colours of a group cut to COLOURS together by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "azir", "codex_picture", "azir-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "azir", "hd")
GROUPS = ((("A", "SA"), 40), (("T", "U", "US"), 28), (("D",), 20))   # pictures sharing one palette, and its colours
FILES = {k: f"{k}.png" for k in ("A", "SA", "T", "U", "US", "D")}
SIZES = {"A": 11.5, "SA": 10.5, "T": 15.5, "U": 14.5, "US": 14.5, "D": 12.5}


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

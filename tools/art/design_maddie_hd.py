#!/usr/bin/env python3
"""Maddie's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_maddie_hd.py   # writes assets/source/maddie/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/maddie/codex_picture, 2026-10-27, Codex 2026-10-27/new-chat-2): asked 1536 and 11 px squares,
delivered 1254 canvases with soft alpha and ~13.2 px squares (the colour edges' autocorrelation peaks at 13 / 26-27 /
39-40 / 52), so the figures came out coarser than asked: ~60 squares tall (asked 56; A 800 px, B 781 px). The
delivered PNGs are the raws A-coarse / B-coarse byte for byte; the raws are read (A-initial was Codex's finer first
try, not pixel art). A = the rifle on her shoulder, muzzle back; B = the rifle level at her hip. -1 = read on Codex's
own ~13.2 px squares (every detail), -2 = on one and a half of them (~19.8 px: a coarser ~40-row figure).
Every picture is read on SIZE px squares, one pixel per drawn square; its colours cut to COLOURS by k-means in Lab
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


SRC = os.path.join(ROOT, "assets", "source", "maddie", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "maddie", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "maddie-A-coarse.png", "A-2": "maddie-A-coarse.png", "B-1": "maddie-B-coarse.png",
         "B-2": "maddie-B-coarse.png"}
SIZES = {"A-1": 13.2, "A-2": 19.8, "B-1": 13.2, "B-2": 19.8}


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
    ap.add_argument("--size", nargs="*", default=[], metavar="NAME=PX", help="another square for a picture")
    a = ap.parse_args()
    SIZES.update({k: float(v) for k, v in (x.split("=") for x in a.size)})
    os.makedirs(lp(OUT), exist_ok=True)
    for name in FILES:
        d = read(name, SIZES[name])
        op = d[..., 3] > 0
        idx, pal = V.kmeans(d, COLOURS[name])
        out = np.zeros_like(d)
        out[op, :3] = pal[idx[op]]
        out[op, 3] = 255
        Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(out, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()

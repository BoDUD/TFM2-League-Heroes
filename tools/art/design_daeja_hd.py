#!/usr/bin/env python3
"""Daeja's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_daeja_hd.py   # writes assets/source/daeja/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/daeja/codex_picture, 2026-10-30, Codex 2026-10-30/new-chat, delivered as daeja_picture_done.zip):
asked 1536 and 11 px squares, delivered daeja-A.png (= raw/daeja-A-revised.png, 1254, figure 538 x 686) and
daeja-B.png (= raw/daeja-B-generated.png, 1254, figure 498 x 758), soft alpha; raw/daeja-A-initial.png (bigger, cut at
the bottom edge) was redone by Codex itself. regrid's own square: A ~10 px, B ~8 px.
A-1 / B-1 = each on its own squares (the most detail), A-2 / B-2 = on 12 / 10 px (a smaller figure).
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


SRC = os.path.join(ROOT, "assets", "source", "daeja", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "daeja", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "raw/daeja-A-revised.png", "A-2": "raw/daeja-A-revised.png", "B-1": "raw/daeja-B-generated.png",
         "B-2": "raw/daeja-B-generated.png"}
SIZES = {"A-1": 10.0, "A-2": 12.0, "B-1": 8.0, "B-2": 10.0}


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

#!/usr/bin/env python3
"""Smeech's step-0 pictures read back on bigger squares, each on its own palette.

    python tools/art/design_smeech_hd.py   # writes assets/source/smeech/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/smeech/codex_picture, 2026-10-29, Codex 2026-10-29/new-chat-3, smeech_picture_done.zip): asked
1536 and 11 px squares, delivered 1254 canvases with soft alpha, two rounds a picture (raw/*-initial big, raw/*-refined
small and coarser, Codex's own pick). Squares read by eye at 5x: A-refined ~7.5 px (669 px hat to soles), B-refined
~6 px (504 px), A-initial ~5 px (1166 px), B-initial ~9 px (899 px). A = TFT's idle, upright on his stilts, the near
claw raised; B = the ambush crouch, claws spread. -1 = the refined picture on its own squares (~89 / ~84 rows), -2 = the
initial one read on bigger squares to ~85 / ~80 rows (more of its detail kept).
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


SRC = os.path.join(ROOT, "assets", "source", "smeech", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "smeech", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "smeech-A-refined.png", "A-2": "smeech-A-initial.png", "B-1": "smeech-B-refined.png",
         "B-2": "smeech-B-initial.png"}
SIZES = {"A-1": 7.5, "A-2": 13.7, "B-1": 6.0, "B-2": 11.2}


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

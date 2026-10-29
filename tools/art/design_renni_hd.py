#!/usr/bin/env python3
"""Renni's step-0 pictures read back on bigger squares, each on its own palette.

    python tools/art/design_renni_hd.py   # writes assets/source/renni/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/renni/codex_picture, 2026-10-29, Codex 2026-10-29/new-chat-2, renni_picture.zip): asked 1536
and 11 px squares, delivered 1254 canvases with soft alpha and squares of ~10 px (A: hair to soles 976 px, ~98
squares) and ~7 px (B: 734 px, ~105 squares) - regrid's measure. A = TFT's idle, the saw upright on her shoulder
(its bars rise above her hair); B = the stance, the saw level forward. Both too tall on their own squares, so -1 is
read on squares that make her hair-to-soles ~76 rows (PPU 2.0 at 38 game px, Scar's, Violet's and Krug's), -2 on
squares for ~84 rows (more of the face kept). regrid follows the drawn edges, so A's rows jump (13.2 -> 88,
13.6-14.8 -> 80-81, 15.2 -> 69): A-1 takes 80, A-2 88; B-1 76, B-2 84.
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


SRC = os.path.join(ROOT, "assets", "source", "renni", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "renni", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "renni-A-original.png", "A-2": "renni-A-original.png", "B-1": "renni-B-original.png",
         "B-2": "renni-B-original.png"}
SIZES = {"A-1": 14.0, "A-2": 13.2, "B-1": 10.3, "B-2": 9.9}


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

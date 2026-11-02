#!/usr/bin/env python3
"""Murk Wolf's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_murkwolf_hd.py   # writes assets/source/murkwolf/hd/{A-1,A-2,A-3,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/murkwolf/codex_picture/murkwolf-picture, 2026-11-01, Codex 2026-11-01/new-chat-2,
murkwolf_picture_review.zip): asked 1536 and 11 px squares, delivered murkwolf-A.png (1254, = its
raw/murkwolf-A-normalization-attempt.png, the sprite smaller on the canvas), raw/murkwolf-A-generated.png (1470 x 1070,
its first A: the feet on the bottom edge, a bigger body) and murkwolf-B.png (1254, = raw/murkwolf-B-generated.png), soft
alpha, squares not on one grid (its HANDOFF says so). Squares by regrid's edge phase: A 9 px (83 x 60; on 11 it reads
75 x 51), the first A 11 px (99 x 66), B 11 px (110 x 68; on 12 it reads 100 x 59).
A-1 = A on 9, A-2 = A on 11, A-3 = the first A on 11, B-1 = B on 11, B-2 = B on 12 (one pixel per drawn square).
Every picture is read on SIZE px squares; its colours cut to COLOURS by k-means in Lab (design_varus.kmeans),
alpha 0/255.
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
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "murkwolf", "codex_picture", "murkwolf-picture")
OUT = os.path.join(ROOT, "assets", "source", "murkwolf", "hd")
COLOURS = {"A-1": 32, "A-2": 32, "A-3": 32, "B-1": 32, "B-2": 32}
FILES = {"A-1": "murkwolf-A.png", "A-2": "murkwolf-A.png", "A-3": "raw/murkwolf-A-generated.png",
         "B-1": "murkwolf-B.png", "B-2": "murkwolf-B.png"}
SIZES = {"A-1": 9.0, "A-2": 11.0, "A-3": 11.0, "B-1": 11.0, "B-2": 12.0}
SHRINK = {}


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
        if name in SHRINK:
            d, _ = PD.pixelate(d, SHRINK[name], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
            op_ = d[..., 3] > 0
            ys, xs = np.nonzero(op_)
            d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
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

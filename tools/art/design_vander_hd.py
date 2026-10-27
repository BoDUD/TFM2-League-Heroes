#!/usr/bin/env python3
"""Vander's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_vander_hd.py   # writes assets/source/vander/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/vander/codex_picture, 2026-10-27, Codex 2026-10-27/new-chat-5, delivered as
vander_picture_review.zip): asked 1536 and 11 px squares, delivered 1254 canvases with soft alpha and ~7 px squares
(regrid's measure; the face's steps count the same at 4x), the figures drawn far bigger than asked: A 882 px (~126
squares, asked 58), B 810 px. Codex's vander-A.png / vander-B.png are the raws byte for byte (its own HANDOFF says so);
raw/vander-A-grid-attempt-not-selected.png was a coarser retry that lost the face. A = standing easy, the gauntlet
hanging at his far side; B = the low fighting stance, both fists up. -1 = read on Codex's own ~7 px squares (every
detail, ~126 rows: too tall for any PPU the pack uses), -2 = on one and a half of them (~10.5 px: ~84 rows, PPU 2.0 at
42 game px).
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


SRC = os.path.join(ROOT, "assets", "source", "vander", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "vander", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "vander-A-original.png", "A-2": "vander-A-original.png", "B-1": "vander-B-original.png",
         "B-2": "vander-B-original.png"}
SIZES = {"A-1": 7.0, "A-2": 10.5, "B-1": 7.0, "B-2": 10.5}


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

#!/usr/bin/env python3
"""Loris's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_loris_hd.py   # writes assets/source/loris/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/loris/codex_picture, 2026-10-27, Codex 2026-10-27/new-chat-3): asked 1536 and 11 px squares,
delivered 1254 canvases with soft alpha and ~11.2 px squares (the colour edges' autocorrelation peaks at 11 / 22 / 33 /
44 down the rows, 11-12 / 35 / 47 across), the figures drawn bigger than asked: ~75 squares tall (asked 58; A 837 px,
B 861 px). Codex's own loris-A.png / loris-B.png are those raws brought down to 58 rows by nearest sampling (muddy):
the raws are read (raw/loris-*-refined.png; *-initial were earlier tries, B-placement-rejected held the shield on the
wrong side). A = the shield planted in front, arms crossed on its top; B = the shield upright at his side, a fist at
his chest. -1 = read on Codex's own ~11.2 px squares (every detail), -2 = on one and a half of them (~16.8 px: a
coarser ~50-row figure).
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


SRC = os.path.join(ROOT, "assets", "source", "loris", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "loris", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "loris-A-refined.png", "A-2": "loris-A-refined.png", "B-1": "loris-B-refined.png",
         "B-2": "loris-B-refined.png"}
SIZES = {"A-1": 11.2, "A-2": 16.8, "B-1": 11.2, "B-2": 16.8}


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

#!/usr/bin/env python3
"""Meepsie's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_meepsie_hd.py   # writes assets/source/meepsie/hd/{A-1,A-2,A-3,B-1,B-2,B-3}.png (+ _4x)

Step 0 (assets/source/meepsie/codex_picture/meepsie-picture, 2026-11-01, Codex 2026-11-01/new-chat-3,
meepsie_picture_done.zip): asked 1536 and 11 px squares, delivered four 1254 drafts with soft alpha:
raw/meepsie-A-original.png (its first A: fine squares, the clearest pilot face), raw/meepsie-A-coarse-revision.png
(its second A), raw/meepsie-B-original.png (side view) and raw/meepsie-B-coarse-revision.png (its second B), plus its own
50x40 / 26x40 readings of the coarse ones (meepsie-A-pixels.png, meepsie-B-pixels.png; its motion pack is drawn on that A).
The squares measured by regrid's own edge phase: A original 7 px, A coarse 9, B original 6, B coarse 17.
A-1 = the original A, A-2 = the coarse A, A-3 = Codex's 50x40; B-1 = the original B, B-2 = the coarse B, B-3 = Codex's 26x40.
Every picture is read on SIZE px squares; its colours cut to COLOURS by k-means in Lab (design_varus.kmeans),
alpha 0/255. The *-pixels files are taken as they are.
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


SRC = os.path.join(ROOT, "assets", "source", "meepsie", "codex_picture", "meepsie-picture")
OUT = os.path.join(ROOT, "assets", "source", "meepsie", "hd")
COLOURS = {"A-1": 32, "A-2": 32, "B-1": 32, "B-2": 32}
FILES = {"A-1": "raw/meepsie-A-original.png", "A-2": "raw/meepsie-A-coarse-revision.png", "A-3": "meepsie-A-pixels.png",
         "B-1": "raw/meepsie-B-original.png", "B-2": "raw/meepsie-B-coarse-revision.png", "B-3": "meepsie-B-pixels.png"}
SIZES = {"A-1": 7.0, "A-2": 9.0, "B-1": 6.0, "B-2": 17.0}
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
        if name not in SIZES:
            out = np.asarray(Image.open(lp(os.path.join(SRC, FILES[name]))).convert("RGBA")).copy()
            Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
            Image.fromarray(np.repeat(np.repeat(out, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
            print(name, out.shape[1], "x", out.shape[0], "(as delivered)")
            continue
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

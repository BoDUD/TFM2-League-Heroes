#!/usr/bin/env python3
"""Rumble's step-0 picture read back on its own grid.

    python tools/art/design_rumble_hd.py [--a 5.0]   # writes assets/source/rumble/hd/A.png (+ _4x)

Step 0 (assets/source/rumble/codex_picture/rumble-1.png, delivered 2026-10-25 as one 1254 px webp, saved as png): his
idle 3/4 front facing right; drawn without League's references (the pack went out without refs 1-9: the container could
not reach raw.communitydragon.org), so Codex drew Rumble from its own knowledge - blue fur and a blue mohawk, the goggles
pushed up, yellow eyes, a grin; the mech brass-olive and rusty, a long flamethrower cannon forward (image right), a
harpoon spike on its chest, a SPIKED MACE BALL on the back arm (asked: a claw), two red-capped rocket pods on its back,
thin jointed legs on red disc feet. Asked 1536 and 11 px squares: the squares run 4-5 px (soft, no exact grid, lossy
alpha 224-254 inside); regrid is given a little above (it splits rows below the real square), as for Kled.
Read on SIZE px squares, one pixel per drawn square; the colours cut to COLOURS by k-means in Lab (design_varus.kmeans),
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
import regrid as RG  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "rumble", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "rumble", "hd")
FILES = {"A": "rumble-1.png"}
COLOURS = 40


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
    ap.add_argument("--a", type=float, default=5.0)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    d = read("A", a.a)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    Image.fromarray(out).save(lp(os.path.join(a.out, "A.png")))
    Image.fromarray(np.repeat(np.repeat(out, 4, 0), 4, 1)).save(lp(os.path.join(a.out, "A_4x.png")))
    print("A", out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()

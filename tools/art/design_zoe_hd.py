#!/usr/bin/env python3
"""Zoe's step-0 pictures read back on their own grid, one palette for both.

    python tools/art/design_zoe_hd.py [--size A B]   # writes assets/source/zoe/hd/{A,B}.png (+ _4x)

Step 0 (assets/source/zoe/codex_picture, 2026-10-19, Codex new-chat-3): A (League's idle, 3/4 front, arms a little out,
the hair streaming back) and B (standing straight, arms hanging) on 1254 squares (asked 1536 and 11 px squares). The
silhouette's outline steps are 8-9 px in both (regrid's own guesses 8 / 7.5 for A, 7 / 9 for B; the face is drawn finer),
so both are read at 8.5 px. Its HANDOFF: soft edges, semi-transparent rim.
regrid.py reads each one pixel per drawn square; the painted colours of both are cut to COLOURS together by k-means in
Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "zoe", "codex_picture", "zoe-picture")
OUT = os.path.join(ROOT, "assets", "source", "zoe", "hd")
COLOURS = 40
SIZES = (8.5, 8.5)
BODY_TOP = {"A": 0, "B": 0}    # first row of the figure counted in its height (the hair on her crown)


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"zoe-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", nargs=2, type=float, default=SIZES, help="square sizes of A and B in px")
    a = ap.parse_args()
    if not os.path.exists(lp(OUT)):
        os.mkdir(lp(OUT))
    A, B = read("A", a.size[0]), read("B", a.size[1])
    h = max(A.shape[0], B.shape[0])
    both = np.zeros((h, A.shape[1] + B.shape[1], 4), np.uint8)
    both[:A.shape[0], :A.shape[1]] = A
    both[:B.shape[0], A.shape[1]:] = B
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    for name, part in (("A", out[:A.shape[0], :A.shape[1]]), ("B", out[:B.shape[0], A.shape[1]:])):
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()

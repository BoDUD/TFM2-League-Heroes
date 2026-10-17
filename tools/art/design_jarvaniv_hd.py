#!/usr/bin/env python3
"""Jarvan IV's step-0 pictures read back on their own grid, one palette for both.

    python tools/art/design_jarvaniv_hd.py [--size A B]   # writes assets/source/jarvaniv/hd/{A,B}.png (+ _4x)

Step 0 (assets/source/jarvaniv/codex_picture, 2026-10-17, Codex new-chat-6): A (League's idle, the lance upright) and
B (the low diagonal ready stance) on 1254 squares (asked 1536 and 11 px squares). regrid measured 7 px squares for both:
A 169 rows (the lance tip at row 0, the helmet's spikes at BODY_TOP 36, soles 168: 133 body rows), B 150 rows (helmet at
0: 150 body rows - drawn bigger than A). Its HANDOFF: not on one exact grid, soft edges. regrid.py reads each one pixel
per drawn square; the painted colours of both are cut to COLOURS together by k-means in Lab (design_varus.kmeans),
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


SRC = os.path.join(ROOT, "assets", "source", "jarvaniv", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "jarvaniv", "hd")
COLOURS = 40
SIZES = (7.0, 7.0)
BODY_TOP = {"A": 36, "B": 0}   # first row of the helmet (the lance left out) in the read-back


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"jarvaniv-{name}.png"))).convert("RGBA")).copy()
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

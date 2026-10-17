#!/usr/bin/env python3
"""Tahm Kench's dense (PPU) designs: Codex's step-0 pictures read back on their own grid, one palette for both.

    python tools/art/design_tahmkench_hd.py [--size 8]   # writes assets/source/tahmkench/hd/{A,B}.png (+ _4x previews)

Step 0 (assets/source/tahmkench/codex_picture, 2026-10-15, Codex new-chat-6): A (League's idle, the smug grin) and B
(the aggro idle, mouth wide open, arms out) on 1536x1024. Asked for 76 squares of 11 px, Codex drew about 125 squares
of 8 px hat to soles (its HANDOFF: "not on the 11-px grid", figure ~985 px). regrid.py reads each one pixel per drawn
square at SIZE; the painted colours of both are cut to COLOURS together by k-means in Lab (design_varus.kmeans, the
Nidalee / Elise way), alpha 0/255 (Codex's soft edge of alpha < 128 dropped). The game shows it at the PPU the user
picks (1.8 -> 1.5 -> 1.2, compared side by side at game size).
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


SRC = os.path.join(ROOT, "assets", "source", "tahmkench", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "tahmkench", "hd")
COLOURS = 40


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"tahmkench-{name}.png"))).convert("RGBA")).copy()
    d = RG.regrid(a, size)[0]
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=float, default=8.0)
    a = ap.parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    A, B = read("A", a.size), read("B", a.size)
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
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()

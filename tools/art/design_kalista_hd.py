#!/usr/bin/env python3
"""Kalista's dense (PPU) designs: Codex's step-0 pictures read back on their own grid, one palette for both.

    python tools/art/design_kalista_hd.py      # writes assets/source/kalista/hd/{A,B}.png (+ _4x previews)

Step 0 (assets/source/kalista/codex_picture, 2026-10-15): A = League's idle (low lunge, the spear low behind her),
B = the upright stance. Codex's own 1536 px exports are nearest-neighbour samples of its pictures on a 128-square
canvas (it said so in HANDOFF.md) - fewer squares than it drew, so they are not used: its raw 1254 px pictures are
read back here one pixel per drawn square (regrid.py, about 10 px a square, its own measure): A about 122 x 98, B about
103 x 104, B's helm top to soles about 82 squares (2.05 squares a game pixel at 40 game rows). The painted colours of
both cut to COLOURS together by k-means in Lab (design_varus.kmeans), alpha 0/255.
"""
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


SRC = os.path.join(ROOT, "assets", "source", "kalista", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "kalista", "hd")
COLOURS = 40
SQ = None     # regrid's own measure (10 px)


def read(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"kalista-{name}-original.png"))).convert("RGBA")).copy()
    d, size, _ = RG.regrid(a, SQ)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d, size


def main():
    os.makedirs(lp(OUT), exist_ok=True)
    (a, sa), (b, sb) = read("A"), read("B")
    h = max(a.shape[0], b.shape[0])
    both = np.zeros((h, a.shape[1] + b.shape[1], 4), np.uint8)
    both[:a.shape[0], :a.shape[1]] = a
    both[:b.shape[0], a.shape[1]:] = b
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    for name, part, size in (("A", out[:a.shape[0], :a.shape[1]], sa), ("B", out[:b.shape[0], a.shape[1]:], sb)):
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        n = len(np.unique(part[part[..., 3] > 0][:, :3], axis=0))
        print(f"{name} {part.shape[1]}x{part.shape[0]} squares ({size:.1f} px each), {n} colours")


if __name__ == "__main__":
    main()

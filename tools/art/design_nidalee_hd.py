#!/usr/bin/env python3
"""Nidalee's dense (PPU) designs: Codex's step-0 pictures read back on their own grids, one palette for both forms.

    python tools/art/design_nidalee_hd.py      # writes assets/source/nidalee/hd/{human,cougar}.png (+ _4x previews)

Step 0 (assets/source/nidalee/codex_picture, 2026-10-13): the user picked human A (3/4 front, the javelin upright at
her far side) and cougar A (side-on facing right, standing) and "Codex's proportions" between them. regrid.py reads
each picture one pixel per drawn square (human about 6.0 px a square: 101 x 168 from the javelin's tip, the ponytail's
top at row 9; cougar about 7.0 px: 197 x 97). One sheet needs one density, so the cougar is brought to the human's
square size by 7/6 (the user's pick 「我把美洲狮按 7/6 放大」 over a Codex redraw: every sixth column and row doubled,
nearest neighbour): 230 x 113. The 9000-odd painted colours of both cut to COLOURS together by k-means in Lab
(design_varus.kmeans, the Corki way), alpha 0/255 (Codex left a soft halo of alpha < 128: dropped). PPU about 3.83:
159 dense rows ponytail to soles = 41.5 game rows; the cougar about 29.5.
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

SRC = os.path.join(ROOT, "assets", "source", "nidalee", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "nidalee", "hd")
COLOURS = 56
HUMAN_SQ, COUGAR_SQ = 6.0, 7.0


def read(name, size):
    a = np.asarray(Image.open(os.path.join(SRC, f"nidalee-{name}.png")).convert("RGBA")).copy()
    d = RG.regrid(a, size)[0] if size else RG.regrid(a)[0]
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def stretch(d, k):
    """Nearest-neighbour enlargement by k (> 1): output square i shows source square floor(i / k)."""
    h, w = d.shape[:2]
    rows = np.minimum((np.arange(round(h * k)) / k).astype(int), h - 1)
    cols = np.minimum((np.arange(round(w * k)) / k).astype(int), w - 1)
    return d[rows][:, cols]


def main():
    os.makedirs(OUT, exist_ok=True)
    human = read("human-A", HUMAN_SQ)
    cougar = stretch(read("cougar-A", COUGAR_SQ), COUGAR_SQ / HUMAN_SQ)
    # one palette for both: k-means over the two pictures side by side
    h = max(human.shape[0], cougar.shape[0])
    both = np.zeros((h, human.shape[1] + cougar.shape[1], 4), np.uint8)
    both[:human.shape[0], :human.shape[1]] = human
    both[:cougar.shape[0], human.shape[1]:] = cougar
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    for name, part in (("human", out[:human.shape[0], :human.shape[1]]),
                       ("cougar", out[:cougar.shape[0], human.shape[1]:])):
        Image.fromarray(part).save(os.path.join(OUT, f"{name}.png"))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(os.path.join(OUT, f"{name}_4x.png"))
        n = len(np.unique(part[part[..., 3] > 0][:, :3], axis=0))
        print(f"{name} {part.shape[1]}x{part.shape[0]} squares, {n} colours")


if __name__ == "__main__":
    main()

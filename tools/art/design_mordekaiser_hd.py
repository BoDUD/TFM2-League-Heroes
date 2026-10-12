#!/usr/bin/env python3
"""Mordekaiser's dense (PPU) design: Codex's raw picture A read back on its own grid, its own colours.

    python tools/art/design_mordekaiser_hd.py      # writes assets/source/mordekaiser/hd/front.png (+ front_4x.png)

Step 0 (assets/source/mordekaiser/codex_picture, 2026-10-12): the user picked A (3/4 front, the mace on the shoulder).
Codex's own 8-px copy (mordekaiser-model-A.png, 14 colours) is a shrink of its raw picture by 0.86 with merged
colours, so the raw (raw/mordekaiser-model-A.png, about 6 px a square, a soft halo of alpha < 128 round it) is read
back one pixel per drawn square instead (regrid.py: 166 x 246 squares from the mace's top spike to the soles) and its
8000-odd painted colours cut to COLOURS by k-means in Lab with a farthest-point start (design_varus.kmeans, the Corki
way: the teal glow, the eyes and the maroon cloth keep colours of their own). Alpha 0/255. That is the dense 3/4-front
design: the idle and the ban/pick card. PPU 5 in league.dll: 246 dense rows = 49 game rows (league_darius 42,
league_nautilus 51).
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

PICTURE = os.path.join(ROOT, "assets", "source", "mordekaiser", "codex_picture", "raw", "mordekaiser-model-A.png")
OUT = os.path.join(ROOT, "assets", "source", "mordekaiser", "hd")
COLOURS = 48


def front():
    a = np.asarray(Image.open(PICTURE).convert("RGBA")).copy()
    d = RG.regrid(a)[0]
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    op = op[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    d[..., 3] = np.where(op, 255, 0)
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    f = front()
    Image.fromarray(f).save(os.path.join(OUT, "front.png"))
    Image.fromarray(np.repeat(np.repeat(f, 4, 0), 4, 1)).save(os.path.join(OUT, "front_4x.png"))
    n = len(np.unique(f[f[..., 3] > 0][:, :3], axis=0))
    print(f"front {f.shape[1]}x{f.shape[0]} squares, {n} colours -> {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Braum's dense (PPU) design: Codex's picture A read back on its own grid, its own colours (Corki's way).

    python tools/art/design_braum_hd.py            # writes assets/source/braum/hd/front.png (+ front_6x.png)

The user picked picture A (2026-10-12: the shield planted in front of him on the image right, his far hand on its top
bar) and, shown the read-back, 「这个可以用」「不用太高清」: no redraw. Codex's own 6-px copy (braum-model-A.png) is the
raw brought to a 6-px grid by resampling; its raw drawing (codex_picture/raw/braum-A-generated.png, about 10 px a
square, the glow behind it half-transparent) is read back one pixel per drawn square (regrid.py: 134 x 121 squares from
the crown to the soles), its painted colours cut to COLOURS by k-means in Lab with a farthest-point start
(design_varus.kmeans: small bright parts - the cyan gem and eyes, the teal pendant - keep a colour of their own),
alpha 0/255 (>= 200 kept: the glow is gone), then only strips.complete_outline. That is the 3/4-front design: the
idle, the ban/pick card and the base every action is posed from (all front, the user's pick).
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
import strips as ST  # noqa: E402

PICTURE = os.path.join(ROOT, "assets", "source", "braum", "codex_picture", "raw", "braum-A-generated.png")
OUT = os.path.join(ROOT, "assets", "source", "braum", "hd")
COLOURS = 48


def front():
    a = np.asarray(Image.open(PICTURE).convert("RGBA")).copy()
    d = RG.regrid(a)[0]
    op = d[..., 3] >= 200
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    op = op[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    d[..., 3] = np.where(op, 255, 0)
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    out, added, darkened = ST.complete_outline(out)
    print(f"outline: {added} added, {darkened} darkened")
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    f = front()
    Image.fromarray(f).save(os.path.join(OUT, "front.png"))
    Image.fromarray(np.repeat(np.repeat(f, 6, 0), 6, 1)).save(os.path.join(OUT, "front_6x.png"))
    n = len(np.unique(f[f[..., 3] > 0][:, :3], axis=0))
    print(f"front {f.shape[1]}x{f.shape[0]} squares, {n} colours -> {OUT}")


if __name__ == "__main__":
    main()

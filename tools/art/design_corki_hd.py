#!/usr/bin/env python3
"""Corki's dense (PPU) design: the user's picture 2 read back on its own grid, its own 48 colours.

    python tools/art/design_corki_hd.py            # writes assets/source/corki/hd/front.png (+ front_4x.png)

The user, 2026-10-12: 「直接用PPU做吧」 - no game-size redraw: the picture they picked (assets/source/corki/user_picture/
corki-picture-2.png, 1536x1024, about 7.5 px a square) is read back one pixel per drawn square (regrid.py: 146 x 125
squares from the propellers to the bombs) and its 8000-odd painted colours cut to 48 by k-means in Lab with a
farthest-point start (tools/art/design_varus.py's way: the small bright parts - the yellow lenses, the pink nose, the
gold lamps, the green suit - keep a colour of their own; a median cut merged them into the browns). Alpha 0/255.
That is the dense 3/4-front design: the idle and the ban/pick card. PPU 4 in league.dll: 125 dense rows = 31 game rows.
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

PICTURE = os.path.join(ROOT, "assets", "source", "corki", "user_picture", "corki-picture-2.png")
OUT = os.path.join(ROOT, "assets", "source", "corki", "hd")
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

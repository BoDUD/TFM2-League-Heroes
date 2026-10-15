#!/usr/bin/env python3
"""Elise's dense (PPU) designs: Codex's step-0 pictures read back on their own grid, one palette for both forms.

    python tools/art/design_elise_hd.py      # writes assets/source/elise/hd/{human,spider}.png (+ _4x previews)

Step 0 (assets/source/elise/codex_picture, 2026-10-15): the user picked human B (3/4 front, one clawed hand raised, the
six spider legs high behind her) and spider A (3/4 view facing right). Both are on Codex's 12-px grid (the least
within-square spread at 12: spider 14, human 37 against 39-40 at 11 / 11.5 / 12.5 - the human's edges are softer, not
off-grid). regrid.py reads each one pixel per drawn square: human about 85 x 123, the crown on row 25 and the toes on
row 125 of the full picture (100 squares crown to toes: 2.63 squares a game pixel for 38 game rows); spider about
114 x 72 at the same density (27 game rows). The painted colours of both cut to COLOURS together by k-means in Lab
(design_varus.kmeans, the Nidalee way), alpha 0/255 (Codex left a dark-red haze of alpha < 128 round the outline:
dropped). The game shows it at PPU 1.5 (ppu_restyle / ppu_hd after the actions).
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

SRC = os.path.join(ROOT, "assets", "source", "elise", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "elise", "hd")
COLOURS = 40
SQ = 12.0


def read(name):
    a = np.asarray(Image.open(os.path.join(SRC, f"elise-{name}.png")).convert("RGBA")).copy()
    d = RG.regrid(a, SQ)[0]
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    os.makedirs(OUT, exist_ok=True)
    human = read("human-B")
    spider = read("spider-A")
    h = max(human.shape[0], spider.shape[0])
    both = np.zeros((h, human.shape[1] + spider.shape[1], 4), np.uint8)
    both[:human.shape[0], :human.shape[1]] = human
    both[:spider.shape[0], human.shape[1]:] = spider
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    for name, part in (("human", out[:human.shape[0], :human.shape[1]]),
                       ("spider", out[:spider.shape[0], human.shape[1]:])):
        Image.fromarray(part).save(os.path.join(OUT, f"{name}.png"))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(os.path.join(OUT, f"{name}_4x.png"))
        n = len(np.unique(part[part[..., 3] > 0][:, :3], axis=0))
        print(f"{name} {part.shape[1]}x{part.shape[0]} squares, {n} colours")


if __name__ == "__main__":
    main()

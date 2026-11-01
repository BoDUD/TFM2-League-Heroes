#!/usr/bin/env python3
"""Meepsie's step-0 designs at game size: A (the idle stance at 3/4: A-1 Codex's original A on its 7 px squares, A-2 its
coarse A on 9 px, A-3 its own 50x40 reading) and B (the same stance side-on: B-1 on 6 px, B-2 on 17, B-3 its 26x40),
at several heights, next to the pack's golems and set neighbours (tft_sentinel, tft_krug, tft_terra, tft_idas, Ivern,
Galio) as the game shows them, the lowest points on one line, for the user's pick.

    python tools/art/review_meepsie_size.py --out DIR [--h 36,40,44] [--scale 3]

The height is the whole figure in game pixels, the mushroom tops to its soles. One row of cells per height, the
neighbours on every row. Every design is shown 1:1 (one design square a game square, PPU = its rows / the height), so
nothing is resampled; `scale` screen pixels a game pixel. Each cell is labelled with its PPU and its width and height in
game pixels. Writes <out>/meepsie_size_review.png.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import review_elderdragon_size as R  # noqa: E402

SRC = os.path.join(R.ROOT, "assets", "source", "meepsie", "hd")
TAKES = ["A-1", "A-2", "A-3", "B-1", "B-2", "B-3"]
NEIGHBOURS = ["tft:sentinel", "tft:krug", "tft:terra", "tft:idas", "ivern", "galio"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--h", default="36,40,44")
    ap.add_argument("--scale", type=int, default=3)
    a = ap.parse_args()
    D = {k: Image.open(R.lp(os.path.join(SRC, f"{k}.png"))).convert("RGBA") for k in TAKES}
    rows = []
    for h in [int(x) for x in a.h.split(",")]:
        cells = []
        for key in TAKES:
            im = D[key].crop(D[key].getbbox())
            ppu = im.height / h
            cells.append((f"{key} {h} PPU {ppu:.2f}", f"{im.width / ppu:.0f}x{h}", R.shown(im, ppu, a.scale)))
        for hero in NEIGHBOURS:
            im, p = R.frame0(hero)
            cells.append((hero.replace("tft:", "tft_"), f"{im.width / p:.0f}x{im.height / p:.0f}", R.shown(im, p, a.scale)))
        rows.append(cells)
    gap, top = 16, 34
    W = max(sum(c[2].width for c in cells) + gap * (len(cells) + 1) for cells in rows)
    Hs = [max(c[2].height for c in cells) + top + gap for cells in rows]
    can = Image.new("RGBA", (W, sum(Hs)), R.BG)
    dr = ImageDraw.Draw(can)
    y0 = 0
    for cells, H in zip(rows, Hs):
        x = gap
        for label, size, im in cells:
            can.alpha_composite(im, (x, y0 + H - gap - im.height))
            dr.text((x, y0 + 4), label, fill=(30, 30, 30, 255))
            dr.text((x, y0 + 18), size, fill=(30, 30, 30, 255))
            x += im.width + gap
        dr.line([(0, y0 + H - gap), (W, y0 + H - gap)], fill=(120, 120, 120, 255))
        y0 += H
    os.makedirs(R.lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "meepsie_size_review.png")
    can.convert("RGB").save(R.lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

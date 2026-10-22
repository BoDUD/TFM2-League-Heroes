#!/usr/bin/env python3
"""Illaoi's step-1 takes for the user's pick: the read-backs at 4x, the two faces at 12x, and every take as the game
draws it (PPU 1.5, the tentacle too) beside the pack's top laners, feet on one line.

    python tools/art/design_illaoi_model.py --options C:/t/il_work/model_opts
    python tools/art/review_illaoi_model.py --opts C:/t/il_work/model_opts --out dist/illaoi_packs

Writes <out>/illaoi_model_review.png.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from review_illaoi_size import NEIGHBOURS, frame0, lp, shown  # noqa: E402

TAKES = {"A-1": 1.5, "A-2": 1.5, "T": 1.5}   # take -> the PPU it is shown at
FACES = {"A-1": (22, 4, 46, 30), "A-2": (20, 4, 46, 30)}    # the bun to the chin, on the read-back
BG = (196, 200, 190, 255)


def on_bg(im):
    bg = Image.new("RGBA", im.size, BG)
    bg.alpha_composite(im)
    return bg


def row(cells, gap=16, top=34):
    W = sum(c[2].width for c in cells) + gap * (len(cells) + 1)
    H = max(c[2].height for c in cells) + top + gap
    can = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(can)
    x = gap
    for label, size, im in cells:
        can.alpha_composite(im, (x, H - gap - im.height))
        dr.text((x, 4), label, fill=(30, 30, 30, 255))
        dr.text((x, 18), size, fill=(30, 30, 30, 255))
        x += im.width + gap
    dr.line([(0, H - gap), (W, H - gap)], fill=(120, 120, 120, 255))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    im = {t: Image.open(lp(os.path.join(a.opts, f"opt_{t}.png"))).convert("RGBA") for t in TAKES}
    big = row([(t, f"{im[t].width}x{im[t].height} squares", im[t].resize((im[t].width * 4, im[t].height * 4),
                                                                          Image.NEAREST)) for t in TAKES])
    faces = row([(f"{t} face 12x", "", on_bg(im[t].crop(b)).resize(((b[2] - b[0]) * 12, (b[3] - b[1]) * 12),
                                                                 Image.NEAREST)) for t, b in FACES.items()])
    game = [(f"{t} PPU {p}", f"{im[t].width / p:.0f}x{im[t].height / p:.0f}", shown(im[t], p, 4))
            for t, p in TAKES.items()]
    for hero in NEIGHBOURS:
        f, p = frame0(hero)
        game.append((hero, f"{f.width / p:.0f}x{f.height / p:.0f}", shown(f, p, 4)))
    game = row(game)
    parts = [big, faces, game]
    can = Image.new("RGBA", (max(p.width for p in parts), sum(p.height for p in parts)), BG)
    y = 0
    for p in parts:
        can.alpha_composite(p, (0, y))
        y += p.height
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "illaoi_model_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

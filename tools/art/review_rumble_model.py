#!/usr/bin/env python3
"""Rumble's step-1 pick sheet: the takes read back at their counts (design_rumble_model.py --options), each at 4x on the
arena grey, below them his face at 12x (both eyes, the nose, the grin), and at the bottom both as the game draws them
(PPU 1.75) next to the pack's yordles and machines (review_rumble_size.NEIGHBOURS' frames).

    python tools/art/design_rumble_model.py --options DIR
    python tools/art/review_rumble_model.py --opts DIR --out outputs

Writes <out>/rumble_model_pick.png.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import review_rumble_size as RS  # noqa: E402

BG = (196, 200, 190, 255)
TAKES = ("B-1", "B-2")
FACE = (4, 30, 34, 66)   # rows / cols of the face on each read-back (the goggles to the chin, the near ear's root to the far cheek)
PPU = 1.75
NEIGHBOURS = ("kled", "blitzcrank", "urgot", "heimerdinger", "ziggs")


def big(a, k):
    im = Image.fromarray(np.repeat(np.repeat(a, k, 0), k, 1))
    bg = Image.new("RGBA", im.size, BG)
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    r0, r1, c0, c1 = FACE
    cells, row = [], []
    for t in TAKES:
        d = np.asarray(Image.open(os.path.join(a.opts, f"opt_{t}.png")).convert("RGBA"))
        cells.append((t, big(d, 4), big(d[r0:r1, c0:c1], 12)))
        im = Image.fromarray(d)
        row.append((f"{t} {round(im.width / PPU)}x{round(im.height / PPU)}", RS.shown(im, PPU, 3)))
    for h in NEIGHBOURS:
        im, p = RS.frame0(h)
        row.append((f"{h} {round(im.width / p)}x{round(im.height / p)}", RS.shown(im, p, 3)))
    W = max(sum(c[1].width for c in cells) + 60, sum(c[1].width for c in row) + 20 * len(row) + 20)
    H1, H2, H3 = (max(c[1].height for c in cells), max(c[2].height for c in cells), max(c[1].height for c in row))
    can = Image.new("RGBA", (W, H1 + H2 + H3 + 110), BG)
    dr = ImageDraw.Draw(can)
    x = 20
    for t, b, f in cells:
        dr.text((x, 4), t, fill=(30, 30, 30, 255))
        can.alpha_composite(b, (x, 20))
        can.alpha_composite(f, (x, 30 + H1))
        x += b.width + 20
    x, y0 = 20, H1 + H2 + 60
    for lab, im in row:
        dr.text((x, y0), lab, fill=(30, 30, 30, 255))
        can.alpha_composite(im, (x, y0 + 16 + H3 - im.height))
        x += im.width + 20
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "rumble_model_pick.png")
    can.convert("RGB").save(path)
    print(path, can.size)


if __name__ == "__main__":
    main()

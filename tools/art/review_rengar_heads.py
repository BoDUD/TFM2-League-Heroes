#!/usr/bin/env python3
"""Rengar's head check (the redo's rule: the head the design's size in every frame): every frame casts_rengar_hd places,
the design's head (casts_rengar_hd.HEAD_MASK) fitted on it at scales 0.80-1.20 and its outline drawn over the frame -
the scale printed (1.00 = the design's size) with the match's colour distance.

    python tools/art/review_rengar_heads.py --out DIR [--tag run]
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_rengar_hd as CS  # noqa: E402

Z = 6


def fit(pic, turned):
    best = None
    for turn in ((0, 1) if turned else (0,)):
        for sc in np.arange(0.80, 1.201, 0.04):
            rgb, m = CS.head_tpl(sc, turn)
            e, y, x = CS.match(pic, rgb, m, 2)
            e, y, x = CS.match(pic, rgb, m, 1, (y, x))
            if best is None or e < best[0]:
                best = (e, sc, turn, y - m.shape[0], x - m.shape[1], m)
    return best


def tile(pic, best):
    e, sc, turn, y, x, m = best
    bg = Image.new("RGBA", (pic.shape[1], pic.shape[0]), (150, 165, 150, 255))
    bg.alpha_composite(Image.fromarray(pic))
    im = bg.convert("RGB").resize((pic.shape[1] * Z, pic.shape[0] * Z), Image.NEAREST)
    edge = m & ~ndimage.binary_erosion(m)
    d = ImageDraw.Draw(im)
    for yy, xx in zip(*np.nonzero(edge)):
        d.rectangle([(x + xx) * Z + 2, (y + yy) * Z + 2, (x + xx) * Z + Z - 3, (y + yy) * Z + Z - 3], fill=(255, 0, 255))
    d.text((4, 4), f"head x{sc:.2f}  err {e:.0f}", fill=(0, 0, 0))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fr = CS.placed()
    for t in CS.TAGS:
        if a.tag and t != a.tag:
            continue
        names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
        tiles = [("design", tile(CS.D0, fit(CS.D0, False)))]
        for n in names:
            best = fit(fr[n][0], t in CS.TURNED)
            print(n, f"head x{best[1]:.2f} err {best[0]:.0f}", flush=True)
            tiles.append((n, tile(fr[n][0], best)))
        W, H = sum(i.width + 6 for _, i in tiles), max(i.height for _, i in tiles)
        can = Image.new("RGB", (W, H), (40, 40, 40))
        x = 0
        for _, i in tiles:
            can.paste(i, (x, H - i.height))
            x += i.width + 6
        can.save(os.path.join(a.out, f"heads_{t}.png"))


if __name__ == "__main__":
    main()

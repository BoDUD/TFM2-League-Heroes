#!/usr/bin/env python3
"""Kled's step-1 pick sheet: the four takes read back at their counts (design_kled_model.py --options), each at 5x on
the arena grey, and below them his face at 12x (both eyes, the scar and the grin; Skaarl's eye in A), for the user's
pick of one mounted take (A) and one on foot (B).

    python tools/art/design_kled_model.py --options C:/t/kl_work/opts
    python tools/art/review_kled_model.py --opts C:/t/kl_work/opts --out dist/kled_packs

Writes <out>/kled_model_pick.png.
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw

BG = (196, 200, 190, 255)
TAKES = ("A-1", "A-2", "B-1", "B-2")
# rows / cols of the face on each read-back (the brim's lower edge to the beard, the near ear's root to the far cheek)
FACES = {"A-1": (12, 40, 12, 46), "A-2": (12, 40, 10, 44), "B-1": (10, 36, 4, 34), "B-2": (12, 38, 4, 36)}
EYES = {"A-1": (33, 52, 32, 52), "A-2": (33, 52, 30, 52)}   # Skaarl's head (rows / cols)


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
    figs = {t: np.asarray(Image.open(os.path.join(a.opts, f"opt_{t}.png")).convert("RGBA")) for t in TAKES}
    tops, bottoms = [], []
    for t in TAKES:
        f = figs[t]
        r0, r1, c0, c1 = FACES[t]
        cells = [big(f[r0:r1, c0:c1], 12)]
        if t in EYES:
            r0, r1, c0, c1 = EYES[t]
            cells.append(big(f[r0:r1, c0:c1], 8))
        tops.append(big(f, 5))
        bottoms.append(cells)
    gap = 24
    W = max(sum(i.width for i in tops), max(sum(c.width for c in cs) for cs in bottoms) * 2) + gap * 6
    H1 = max(i.height for i in tops) + 40
    H2 = max(max(c.height for c in cs) for cs in bottoms) + 40
    can = Image.new("RGBA", (W, H1 + H2 * 2), (240, 240, 240, 255))
    dr = ImageDraw.Draw(can)
    x = gap
    for t, im in zip(TAKES, tops):
        can.alpha_composite(im, (x, H1 - im.height - 10))
        dr.text((x, 8), f"{t}  {figs[t].shape[1]}x{figs[t].shape[0]}", fill=(20, 20, 20, 255))
        x += im.width + gap
    for k, (t, cells) in enumerate(zip(TAKES, bottoms)):
        x = gap + (k % 2) * (W // 2)
        y = H1 + (k // 2) * H2
        dr.text((x, y + 6), f"{t} face 12x" + (" / Skaarl 8x" if len(cells) > 1 else ""), fill=(20, 20, 20, 255))
        for c in cells:
            can.alpha_composite(c, (x, y + 28))
            x += c.width + gap
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "kled_model_pick.png")
    can.convert("RGB").save(path)
    print(path, can.size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""K'Sante's step-1 takes for the user's pick: each take cut to the count (design_ksante_model.py --options) at 4x, and
the same takes as the game shows them at PPU 1.5 next to the pack's big tanks, feet on one line.

    python tools/art/review_ksante_model.py --opts C:/t/ks_work/model_opts --out dist/ksante_packs [--scale 4]

Reads <opts>/opt_{A-1,A-2,O-1,O-2}.png; writes <out>/ksante_model_review.png.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from review_ksante_size import BG, NEIGHBOURS, frame0, lp, shown  # noqa: E402

TAKES = ("A-1", "A-2", "O-1", "O-2")
PPU = 1.5


def row(cells, gap=16, top=34):
    W = sum(im.width for _, _, im in cells) + gap * (len(cells) + 1)
    H = max(im.height for _, _, im in cells) + top + gap
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
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    takes = {t: Image.open(lp(os.path.join(a.opts, f"opt_{t}.png"))).convert("RGBA") for t in TAKES}
    big = [(t, f"{im.width}x{im.height} squares", im.resize((im.width * 4, im.height * 4), Image.NEAREST))
           for t, im in takes.items()]
    game = [(f"{t} at PPU {PPU}", f"{im.width / PPU:.0f}x{im.height / PPU:.0f}", shown(im, PPU, a.scale))
            for t, im in takes.items()]
    for hero in NEIGHBOURS:
        im, p = frame0(hero)
        game.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", shown(im, p, a.scale)))
    r1, r2 = row(big), row(game)
    can = Image.new("RGBA", (max(r1.width, r2.width), r1.height + r2.height), BG)
    can.alpha_composite(r1, (0, 0))
    can.alpha_composite(r2, (0, r1.height))
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "ksante_model_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pantheon's design at game size: every (height, PPU) pair next to the pack's top laners as the game shows them, for the
user's pick (PPU 1.5 is the user's, 2026-10-16; the height is left to pick).

    python tools/art/review_pantheon_ppu.py --out DIR [--design A] [--heights 40,42,44] [--ppus 1.5] [--scale 4]

The design (assets/source/pantheon/hd/<design>.png, sized by A's helmet top to soles) is brought to PPU x height
squares by pixel_down.pixelate (the squares the game would draw), then every square shown 1 / PPU game pixels, the whole
picture `scale` screen pixels a game pixel. The neighbours: their battlefield frames (hd_idle / PPU, or the 1x idle),
the same scale, feet on one line. Writes <out>/pantheon_size_ppu_<design>.png.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
import ppu_hd  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "pantheon", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
NEIGHBOURS = ["garen", "darius", "jax", "shen", "galio"]
BG = (196, 200, 190, 255)
# A stands 136 squares from the helmet's top (row 26, the crest above it not counted) to the soles; B is drawn at the
# same figure size with 6.8-px squares against A's 6.7
STAND_A = 136
SQUARE = {"A": 6.7, "B": 6.8}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def frame0(hero):
    stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    ppu = ppu_hd.PPU.get(hero)
    tag = "hd_idle" if ppu and "hd_idle" in anims else "idle"
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    return im.crop(im.getbbox()), (ppu if tag == "hd_idle" else 1.0)


def shown(im, ppu, scale):
    """`im` drawn at `ppu` squares a game pixel -> screen pixels at `scale` a game pixel (nearest)."""
    k = scale / ppu
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--design", default="A")
    ap.add_argument("--heights", default="40,42,44")
    ap.add_argument("--ppus", default="1.5")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    d = np.asarray(Image.open(lp(os.path.join(SRC, f"{a.design}.png"))).convert("RGBA"))
    outline = PD.edge_colour(d)
    cells = []
    for h in [int(x) for x in a.heights.split(",")]:
        for p in [float(x) for x in a.ppus.split(",")]:
            k = p * h / STAND_A * SQUARE[a.design] / SQUARE["A"]
            im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), outline)
            im = Image.fromarray(im)
            cells.append((f"{h} rows  PPU {p}", shown(im.crop(im.getbbox()), p, a.scale)))
    for hero in NEIGHBOURS:
        im, p = frame0(hero)
        cells.append((hero + (f" (PPU {p})" if p != 1 else ""), shown(im, p, a.scale)))
    gap, top = 16, 22
    W = sum(c[1].width for c in cells) + gap * (len(cells) + 1)
    H = max(c[1].height for c in cells) + top + gap
    can = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(can)
    x = gap
    for label, im in cells:
        can.alpha_composite(im, (x, H - gap - im.height))
        dr.text((x, 4), label, fill=(30, 30, 30, 255))
        x += im.width + gap
    dr.line([(0, H - gap), (W, H - gap)], fill=(120, 120, 120, 255))
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, f"pantheon_size_ppu_{a.design}.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

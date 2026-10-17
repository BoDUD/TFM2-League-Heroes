#!/usr/bin/env python3
"""Nasus's step-0 designs at game size: A (his idle) at several heights at PPU 1.2, each with B (Fury of the Sands) GROW
times as tall, next to the pack's tops as the game shows them, feet on one line, for the user's pick.

    python tools/art/review_nasus_size.py --out DIR [--a 40,42,44] [--ppu 1.2] [--grow 1.35] [--scale 4]

A's height = ear tips to soles in game pixels; B (Codex drew it on its own grid, only 1.12x A) is brought to GROW x that
height (League's R: +30-40% size). The design (assets/source/rell/hd/{A,B}.png) is
brought to PPU x height squares by pixel_down.pixelate (the squares the game would draw), then every square shown 1 / PPU
game pixels, `scale` screen pixels a game pixel. The neighbours: their battlefield frames (hd_idle / PPU, or the 1x idle).
Each cell is labelled with its width and height in game pixels. Writes <out>/nasus_size_review.png.
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

SRC = os.path.join(ROOT, "assets", "source", "nasus", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
NEIGHBOURS = ["darius", "garen", "sett", "renekton", "tahmkench", "urgot", "swain"]
BG = (196, 200, 190, 255)


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
    k = scale / ppu
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--a", default="40,42,44")
    ap.add_argument("--ppu", type=float, default=1.2)
    ap.add_argument("--grow", type=float, default=1.35)
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    cells = []
    A = np.asarray(Image.open(lp(os.path.join(SRC, "A.png"))).convert("RGBA"))
    B = np.asarray(Image.open(lp(os.path.join(SRC, "B.png"))).convert("RGBA"))
    for h in [int(x) for x in a.a.split(",")]:
        for name, d, hh in (("A", A, h), ("B", B, h * a.grow)):
            k = a.ppu * hh / d.shape[0]
            im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
            im = Image.fromarray(im)
            im = im.crop(im.getbbox())
            cells.append((f"{name} at {h}", f"{im.width / a.ppu:.0f}x{im.height / a.ppu:.0f}", shown(im, a.ppu, a.scale)))
    for hero in NEIGHBOURS:
        im, p = frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", shown(im, p, a.scale)))
    gap, top = 16, 34
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
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "nasus_size_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Cassiopeia's step-0 designs at game size and at several densities, for the user's pick of the picture, the height and
the PPU at once (Maokai's lesson, 2026-10-18: the PPU was settled only on the PR - show it early).

    python tools/art/review_cassiopeia_size.py --out DIR [--heights 36,38,40] [--ppus 1.2,1.3,1.5] [--scale 4]

One row per PPU: A at each height and B at the middle one, then the pack's mages and Nami (a tail too) as the battlefield draws them
(hd_idle / PPU, or the 1x idle), feet on one line. The height is crest top to the ground in game pixels (BODY_TOP 0). The design (assets/source/cassiopeia/hd/{A,B}.png) is brought to the squares the game
would draw by pixel_down.pixelate, every square shown 1 / PPU game pixels, `scale` screen pixels a game pixel. Each cell
is labelled with its width and height in game pixels. Writes <out>/cassiopeia_size_review.png and
<out>/cassiopeia_ppu_closeup.png (A at the middle height, each PPU at 6 screen pixels a square: how coarse each grid is).
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

SRC = os.path.join(ROOT, "assets", "source", "cassiopeia", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
NEIGHBOURS = ["nami", "syndra", "morgana", "elise", "orianna", "swain", "anivia", "lux"]
BODY_TOP = {"A": 0, "B": 0}   # crest top to ground: nothing rises above her crest
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


def down(d, name, h, ppu):
    k = ppu * h / (d.shape[0] - BODY_TOP[name])
    im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    im = Image.fromarray(im)
    return im.crop(im.getbbox())


def strip(cells, gap=16, top=34):
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
    ap.add_argument("--out", required=True)
    ap.add_argument("--heights", default="40,44,48")
    ap.add_argument("--ppus", default="1.2,1.3,1.5")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    A = np.asarray(Image.open(lp(os.path.join(SRC, "A.png"))).convert("RGBA"))
    B = np.asarray(Image.open(lp(os.path.join(SRC, "B.png"))).convert("RGBA"))
    hs = [int(x) for x in a.heights.split(",")]
    mid = hs[len(hs) // 2]
    neighbours = []
    for hero in NEIGHBOURS:
        im, p = frame0(hero)
        neighbours.append((f"{hero} ({p:g})", f"{im.width / p:.0f}x{im.height / p:.0f}", shown(im, p, a.scale)))
    rows, close = [], []
    for ppu in [float(x) for x in a.ppus.split(",")]:
        cells = []
        for h in hs:
            im = down(A, "A", h, ppu)
            cells.append((f"A {h} PPU {ppu:g}", f"{im.width / ppu:.0f}x{im.height / ppu:.0f}", shown(im, ppu, a.scale)))
        im = down(B, "B", mid, ppu)
        cells.append((f"B {mid} PPU {ppu:g}", f"{im.width / ppu:.0f}x{im.height / ppu:.0f}", shown(im, ppu, a.scale)))
        rows.append(strip(cells + neighbours))
        im = down(A, "A", mid, ppu)
        close.append((f"A {mid} PPU {ppu:g}", f"{im.width}x{im.height} squares", im.resize((im.width * 6, im.height * 6),
                                                                                         Image.NEAREST)))
    W = max(r.width for r in rows)
    can = Image.new("RGBA", (W, sum(r.height for r in rows)), BG)
    y = 0
    for r in rows:
        can.alpha_composite(r, (0, y))
        y += r.height
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "cassiopeia_size_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)
    path = os.path.join(a.out, "cassiopeia_ppu_closeup.png")
    strip(close).convert("RGB").save(lp(path))
    print(path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Azir's step-0 designs at game size: his idle (A) at several heights and PPUs, his side (SA) and his summons (the
soldier T, the guard U / US, the Sun Disc D), next to the pack's mid mages as the game shows them, feet on one line, for
the user's pick.

    python tools/art/review_azir_size.py --out DIR [--a 38,42,46] [--ppu 1.2,1.35,1.5] [--scale 4]

The height is his helmet's CREST top to his soles in game pixels; the sceptre rises above it (A: crest at row CREST["A"]
of 81, SA: row CREST["SA"] of 96, read from the column tops of assets/source/azir/hd). SA is shown at the middle height
only, its crest-to-soles matched to A's. The summons are shown at the middle height times SUMMON (their whole picture,
top to bottom, against his crest-to-soles): a draft to pick from.
One row of cells per PPU, the neighbours on every row. The design (assets/source/azir/hd/*.png) is brought to the
squares the game would draw by pixel_down.pixelate, every square shown 1 / PPU game pixels, `scale` screen pixels a game
pixel (a height and PPU above the drawing's own rows upscales it: step 1 redraws at the picked size anyway). The
neighbours: their battlefield frames (hd_idle / PPU, or the 1x idle). Each cell is labelled with its width and height
in game pixels. Writes <out>/azir_size_review.png.
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

SRC = os.path.join(ROOT, "assets", "source", "azir", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
NEIGHBOURS = ["xerath", "aurora", "hwei", "orianna", "syndra", "viktor"]
HAT = {"A": 23, "SA": 36}
SUMMON = {"T": 0.85, "U": 0.9, "US": 0.75, "D": 1.15}
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
    ap.add_argument("--a", default="38,42,46")
    ap.add_argument("--ppu", default="1.2,1.35,1.5")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    D = {k: np.asarray(Image.open(lp(os.path.join(SRC, f"{k}.png"))).convert("RGBA")) for k in ("A", "SA", *SUMMON)}
    hs = [int(x) for x in a.a.split(",")]
    rows = []
    for ppu in [float(x) for x in a.ppu.split(",")]:
        cells = []
        for key, heights in (("A", hs), ("SA", hs[len(hs) // 2:len(hs) // 2 + 1])):
            d = D[key]
            body = d.shape[0] - HAT[key]   # crest to soles
            for h in heights:
                k = ppu * h / body
                im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
                im = Image.fromarray(im)
                im = im.crop(im.getbbox())
                cells.append((f"{key} {h} PPU {ppu}", f"{im.width / ppu:.0f}x{im.height / ppu:.0f}",
                              shown(im, ppu, a.scale)))
        mid = hs[len(hs) // 2]
        for key, f in SUMMON.items():
            d = D[key]
            k = ppu * mid * f / d.shape[0]
            im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
            im = Image.fromarray(im)
            im = im.crop(im.getbbox())
            cells.append((f"{key} {mid * f:.0f}", f"{im.width / ppu:.0f}x{im.height / ppu:.0f}", shown(im, ppu, a.scale)))
        for hero in NEIGHBOURS:
            im, p = frame0(hero)
            cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", shown(im, p, a.scale)))
        rows.append(cells)
    gap, top = 16, 34
    W = max(sum(c[2].width for c in cells) + gap * (len(cells) + 1) for cells in rows)
    Hs = [max(c[2].height for c in cells) + top + gap for cells in rows]
    can = Image.new("RGBA", (W, sum(Hs)), BG)
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
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "azir_size_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

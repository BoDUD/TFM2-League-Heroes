#!/usr/bin/env python3
"""Cho'Gath's step-0 designs at game size: A (League's idle, the scythes raised), B (the scythes folded, the tail
curled) and I (Codex's first A draft, finer squares) at several heights and PPUs, next to the pack's big beasts and
tanks as the game shows them, feet on one line, for the user's pick.

    python tools/art/review_chogath_size.py --out DIR [--h 44,50] [--ppu 1.2,1.3,1.5] [--scale 3]

The height is A's top (the raised scythe tip) to soles in game pixels; B is drawn at the same body scale (its
picture 660 px tall where A's is 792 on Codex's canvas, so B_SCALE of the height). One row of cells per PPU, the neighbours on every row.
The design (assets/source/chogath/hd/{A,B,I}.png, design_chogath_hd.py) is brought to the squares the game would
draw by pixel_down.pixelate, every square shown 1 / PPU game pixels, `scale` screen pixels a game pixel. The
neighbours: their battlefield frames (hd_idle / PPU, or the 1x idle). Each cell is labelled with its width and height
in game pixels. Writes <out>/chogath_size_review.png.
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

SRC = os.path.join(ROOT, "assets", "source", "chogath", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
NEIGHBOURS = ["volibear", "reksai", "nasus", "galio", "braum", "darius"]
B_SCALE = 660 / 792
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
    ap.add_argument("--h", default="44,50")
    ap.add_argument("--ppu", default="1.2,1.3,1.5")
    ap.add_argument("--scale", type=int, default=3)
    a = ap.parse_args()
    designs = {k: np.asarray(Image.open(lp(os.path.join(SRC, f"{k}.png"))).convert("RGBA")) for k in "ABI"}
    rows = []
    for ppu in [float(x) for x in a.ppu.split(",")]:
        cells = []
        for h in [int(x) for x in a.h.split(",")]:
            for name, d in designs.items():
                k = ppu * h * (B_SCALE if name == "B" else 1) / d.shape[0]
                im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
                im = Image.fromarray(im)
                im = im.crop(im.getbbox())
                cells.append((f"{name} {h} PPU {ppu}", f"{im.width / ppu:.0f}x{im.height / ppu:.0f}",
                              shown(im, ppu, a.scale)))
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
    path = os.path.join(a.out, "chogath_size_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

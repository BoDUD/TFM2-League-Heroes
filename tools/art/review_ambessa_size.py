#!/usr/bin/env python3
"""Ambessa's step-0 designs at game size: her idle (A) at several heights and PPUs and her side (SA) on A's scale,
next to the pack's top laners (Illaoi, K'Sante, Darius, Riven, Yorick, Garen) as the game shows them, the lowest points
on one line, for the user's pick.

    python tools/art/review_ambessa_size.py --out DIR [--a 44,48,52] [--ppu 1.5,1.75,2.0] [--scale 4] [--share 0.32]

The height is the top of her hair to her soles in game pixels (the whole figure: the blades hang lower than her
knees, never above her head). SA is shown at the middle height only, as tall as A (Codex drew it a tenth smaller),
its lowest point on the line. --share: both made chibi first (pack_ambessa_model.chibi: the head that share of the
height), as the step-1 targets; <out>/ambessa_size_review_chibi.png. One row of cells per PPU, the neighbours on every row.
The design (assets/source/ambessa/hd/{A,SA}.png) is brought to the squares the game would draw by pixel_down.pixelate,
every square shown 1 / PPU game pixels, `scale` screen pixels a game pixel. The neighbours: their battlefield frames
(hd_idle / PPU, or the 1x idle). Each cell is labelled with its width and height in game pixels. Writes
<out>/ambessa_size_review.png.
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
import pack_ambessa_model as PM  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ambessa", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
NEIGHBOURS = ["illaoi", "ksante", "darius", "riven", "yorick", "garen"]
TOP = {"A": 0}   # the hair's outline row
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
    ap.add_argument("--a", default="44,48,52")
    ap.add_argument("--ppu", default="1.5,1.75,2.0")
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--share", type=float, help="the head's share of the height (chibi, as the step-1 targets)")
    a = ap.parse_args()
    D = {k: np.asarray(Image.open(lp(os.path.join(SRC, f"{k}.png"))).convert("RGBA")) for k in ("A", "SA")}
    if a.share:
        D = {k: PM.chibi(d, PM.HEAD[k][0], a.share)[0] for k, d in D.items()}
    hs = [int(x) for x in a.a.split(",")]
    rows = []
    for ppu in [float(x) for x in a.ppu.split(",")]:
        cells = []
        for key, heights in (("A", hs), ("SA", hs[len(hs) // 2:len(hs) // 2 + 1])):
            d = D[key]
            for h in heights:
                k = ppu * h / (d.shape[0] - TOP["A"])   # SA as tall as A
                im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
                im = Image.fromarray(im)
                im = im.crop(im.getbbox())
                cells.append((f"{key} {h} PPU {ppu}", f"{im.width / ppu:.0f}x{im.height / ppu:.0f}",
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
    path = os.path.join(a.out, "ambessa_size_review_chibi.png" if a.share else "ambessa_size_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

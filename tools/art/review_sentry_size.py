#!/usr/bin/env python3
"""The Sentry's step-0 designs at game size: A (TFT's idle at a slight 3/4: A-1 Codex's raw A on its 9 px squares, A-3
the same on 12) and B (the same idle more side-on: B-1 the raw B on 9), at several heights and PPUs, next to its camp's
golem, the set's monsters and the floating heroes (tft_sentinel, tft_gromp, tft_krug, Xerath, Vel'Koz) as the game
shows them, the lowest points on one line, for the user's pick.

    python tools/art/review_sentry_size.py --out DIR [--a 30,34] [--b 30,34] [--ppu 1.53,1.7] [--scale 4]

The height is the whole figure in game pixels, the left shard's tip to the bottom points (it floats in the game; the
hover comes later). One row of cells per PPU, the neighbours on every row. The design (assets/source/sentry/hd/
<take>.png) is brought to the squares the game would draw by pixel_down.pixelate, every square shown 1 / PPU game
pixels, `scale` screen pixels a game pixel. The neighbours: their battlefield frames (hd_idle / PPU, or the 1x idle).
Each cell is labelled with its width and height in game pixels. Writes <out>/sentry_size_review.png.
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

SRC = os.path.join(ROOT, "assets", "source", "sentry", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
NEIGHBOURS = ["tft:sentinel", "tft:gromp", "tft:krug", "xerath", "velkoz"]
EFFECTS = os.path.join(ROOT, "league", "effects")
TFT = os.path.join(ROOT, "tft", "champions")
B_RATIO = 1.0
BG = (196, 200, 190, 255)
TAKES = ("A-1", "A-3", "B-1")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def frame0(hero):
    """("tft:powder" = the tft pack's sheet; "fx:yuumi_ride" = league_yuumi's ride picture, PPU 1.5)"""
    if hero.startswith("tft:"):
        stem, hero = os.path.join(TFT, f"tft_{hero[4:]}"), hero[4:]
    elif hero.startswith("fx:"):
        stem = os.path.join(EFFECTS, f"league_{hero[3:]}")
    else:
        stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    ppu = 1.5 if hero.startswith("fx:") else ppu_hd.PPU.get(hero)
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
    ap.add_argument("--a", default="30,34")
    ap.add_argument("--b", default="30,34")
    ap.add_argument("--ppu", default="1.53,1.7")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    D = {k: np.asarray(Image.open(lp(os.path.join(SRC, f"{k}.png"))).convert("RGBA")) for k in TAKES}
    ppus = [float(x) for x in a.ppu.split(",")]
    rows = []
    for ppu in ppus:
        cells = []
        ha, hb = [int(x) for x in a.a.split(",")], [int(x) for x in a.b.split(",")]
        plan, near = [(k, ha if k[0] == "A" else hb) for k in TAKES], NEIGHBOURS
        for key, heights in plan:
            d = D[key]
            for h in heights:
                h_ = h
                k = ppu * h_ / d.shape[0]
                im, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
                im = Image.fromarray(im)
                im = im.crop(im.getbbox())
                cells.append((f"{key} {h_:.0f} PPU {ppu}", f"{im.width / ppu:.0f}x{im.height / ppu:.0f}",
                              shown(im, ppu, a.scale)))
        for hero in near:
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
    path = os.path.join(a.out, "sentry_size_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()

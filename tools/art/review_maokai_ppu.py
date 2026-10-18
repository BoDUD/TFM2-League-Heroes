#!/usr/bin/env python3
"""Maokai at several densities (the user, 2026-10-18, on the PR: 「太高清了 降低点像素」 - after 1.2 cut from Codex's design
was 「太模糊了」): his posed frames (assets/source/ppu/orig, PPU
1.5) brought to each PPU by ppu_restyle.restyle (pixel_down.pixelate, nothing written), shown at one game size next to the
pack's big tanks and 1.2 / 1.5 heroes as the battlefield draws them.

    python tools/art/review_maokai_ppu.py --out DIR [--ppus 1.5,1.4,1.3,1.2] [--scale 4]

Writes <out>/maokai_ppu_choices.png: per PPU the idle's first frame and the slam (attack frame 2), then Tahm Kench,
Nasus, Ziggs (1.2), Malphite, Rell, Jarvan IV (1.5), feet on one line; and <out>/maokai_ppu_closeup.png: the same idle frames at 3x
their own pixels next to each other (how coarse each grid is).
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
import ppu_hd  # noqa: E402
import ppu_restyle as R  # noqa: E402

CHAMPS = os.path.join(ROOT, "league", "champions")
PEERS = ["tahmkench", "nasus", "ziggs", "malphite", "rell", "jarvaniv"]
BG = (96, 112, 96)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def frame0(hero, tag="idle"):
    stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    ppu = ppu_hd.PPU.get(hero)
    t = f"hd_{tag}" if ppu and f"hd_{tag}" in anims else tag
    f = anims[t]["frames"][0]["data"]
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    return im, (ppu if t.startswith("hd_") else 1.0)


def shown(im, ppu, scale):
    k = scale / ppu
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ppus", default="1.5,1.4,1.3,1.2")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    cells, close = [], []
    for p in [float(x) for x in a.ppus.split(",")]:
        spec = dict(R.RESTYLE["maokai"], ppu=p)
        out = R.restyle("maokai", spec, write=False)[0]
        for tag, k, lab in (("idle", 0, "idle"), ("attack", 1, "slam")):
            im = Image.fromarray(out[tag][k][0])
            cells.append((f"PPU {p} {lab}", shown(im, p, a.scale), im))
        close.append((f"PPU {p}", Image.fromarray(out["idle"][0][0])))
    for h in PEERS:
        im, p = frame0(h)
        cells.append((f"{h} (PPU {p})", shown(im, p, a.scale), im))
    gap, top = 18, 22
    W = sum(c[1].width for c in cells) + gap * (len(cells) + 1)
    H = max(c[1].height for c in cells) + top + gap
    can = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(can)
    x = gap
    for lab, im, _ in cells:
        # frames are centred on the pivot: line their centres up (the feet then share a row)
        can.paste(im, (x, top + (H - top - gap - im.height) // 2), im)
        d.text((x, 4), lab, fill=(240, 240, 240))
        x += im.width + gap
    os.makedirs(a.out, exist_ok=True)
    can.save(os.path.join(a.out, "maokai_ppu_choices.png"))
    Z = 3
    W = sum(im.width * Z + gap for _, im in close) + gap
    H = max(im.height * Z for _, im in close) + top + gap
    can = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(can)
    x = gap
    for lab, im in close:
        big = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
        can.paste(big, (x, top), big)
        d.text((x, 4), lab, fill=(240, 240, 240))
        x += big.width + gap
    can.save(os.path.join(a.out, "maokai_ppu_closeup.png"))
    print("written", a.out)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Rek'Sai at several densities (the user, 2026-10-17: 「雷克赛像素太高 需要降低」): her posed frames (assets/source/ppu/orig, PPU
1.58) brought to each PPU by ppu_restyle.restyle (pixel_down.pixelate, nothing written), shown at one game size next to the
pack's big heroes as the battlefield draws them.

    python tools/art/review_reksai_ppu.py --out DIR [--ppus 1.58,1.4,1.3,1.2,1.0] [--scale 4]

Writes <out>/reksai_ppu_choices.png: per PPU the idle's first frame, a bite and the burrowed body, then Kog'Maw,
Kha'Zix, Darius (1.0), Tahm Kench (1.2), Mundo (1.5), feet on one line; and <out>/reksai_ppu_closeup.png: the same
idle frames at 3x their own pixels next to each other (how coarse each grid is).
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
PEERS = ["kogmaw", "khazix", "darius", "tahmkench", "drmundo"]
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
    ap.add_argument("--ppus", default="1.58,1.4,1.3,1.2,1.0")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    ppus = [float(x) for x in a.ppus.split(",")]
    rows, close = {"idle": [], "bite": [], "burrowed": []}, []
    for p in ppus:
        spec = dict(R.RESTYLE["reksai"], ppu=p)
        out = R.restyle("reksai", spec, write=False)[0]
        for tag, k, lab in (("idle", 0, "idle"), ("attack", 2, "bite"), ("b_idle", 0, "burrowed")):
            rows[lab].append((f"PPU {p} {lab}", shown(Image.fromarray(out[tag][k][0]), p, a.scale)))
        close.append((f"PPU {p}", Image.fromarray(out["idle"][0][0])))
    peers = []
    for h in PEERS:
        im, p = frame0(h)
        peers.append((f"{h} (PPU {p})", shown(im, p, a.scale)))
    # one row per action (a column per PPU), then the peers; every frame is centred on its pivot, so lining the
    # centres up puts the feet on one row
    gap, top = 18, 22
    lines = list(rows.values()) + [peers]
    cw = max(im.width for line in lines for _, im in line)
    rh = [max(im.height for _, im in line) for line in lines]
    W = max(len(line) for line in lines) * (cw + gap) + gap
    H = sum(h + top + gap for h in rh) + gap
    can = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(can)
    y = gap
    for line, h in zip(lines, rh):
        for j, (lab, im) in enumerate(line):
            x = gap + j * (cw + gap)
            can.paste(im, (x + (cw - im.width) // 2, y + top + (h - im.height) // 2), im)
            d.text((x, y), lab, fill=(240, 240, 240))
        y += h + top + gap
    os.makedirs(a.out, exist_ok=True)
    can.save(os.path.join(a.out, "reksai_ppu_choices.png"))
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
    can.save(os.path.join(a.out, "reksai_ppu_closeup.png"))
    print("written", a.out)


if __name__ == "__main__":
    main()

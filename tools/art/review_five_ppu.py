#!/usr/bin/env python3
"""Gangplank, Wukong, Akshan, Poppy and Cassiopeia at lower densities (the user, 2026-10-18: 「船长猴子阿克尚波比蛇女像素太高需要
降低 船长猴子局内太大」): each hero's posed frames (assets/source/ppu/orig) brought to each PPU, and for Gangplank and Wukong
also to a smaller size (RESTYLE grow), by ppu_restyle.restyle (pixel_down.pixelate, nothing written), shown at one game
size next to peers as the battlefield draws them.

    python tools/art/review_five_ppu.py --out DIR [--scale 4]

Writes <out>/<hero>_ppu_choices.png per hero (idle first frame per choice, then the peers, frame centres on one line).
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_restyle as R  # noqa: E402
from review_urgot_ppu import BG, frame0, shown  # noqa: E402

# hero -> [(label, ppu, grow)]
CHOICES = {
    "gangplank": [("now 1.5", 1.5, 1), ("1.2", 1.2, 1), ("1.0", 1.0, 1), ("1.2 size 90%", 1.2, 0.9), ("1.0 size 90%", 1.0, 0.9), ("1.0 size 85%", 1.0, 0.85)],
    "wukong": [("now 1.5", 1.5, 1), ("1.2", 1.2, 1), ("1.0", 1.0, 1), ("1.2 size 90%", 1.2, 0.9), ("1.0 size 90%", 1.0, 0.9), ("1.0 size 85%", 1.0, 0.85)],
    "akshan": [("now 1.5", 1.5, 1), ("1.3", 1.3, 1), ("1.2", 1.2, 1), ("1.0", 1.0, 1)],
    "poppy": [("now 1.3", 1.3, 1), ("1.2", 1.2, 1), ("1.1", 1.1, 1), ("1.0", 1.0, 1)],
    "cassiopeia": [("now 1.3", 1.3, 1), ("1.2", 1.2, 1), ("1.1", 1.1, 1), ("1.0", 1.0, 1)],
}
PEERS = ["tahmkench", "darius", "garen", "lucian", "jinx"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--only")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    peers = [(f"{h} (PPU {p})", shown(im, p, a.scale)) for h in PEERS for im, p in [frame0(h)]]
    for hero, choices in CHOICES.items():
        if a.only and hero != a.only:
            continue
        cells = []
        for lab, p, g in choices:
            spec = dict(R.RESTYLE[hero], ppu=p)
            if g != 1:
                spec["grow"] = g * spec.get("grow", 1)
            out = R.restyle(hero, spec, write=False)[0]
            im = Image.fromarray(out["idle"][0][0])
            cells.append((f"{hero} {lab}", shown(im, p, a.scale)))
        cells += peers
        gap, top = 18, 22
        W = sum(c[1].width for c in cells) + gap * (len(cells) + 1)
        H = max(c[1].height for c in cells) + top + gap
        can = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(can)
        x = gap
        for lab, im in cells:
            can.paste(im, (x, top + (H - top - gap - im.height) // 2), im)
            d.text((x, 4), lab, fill=(240, 240, 240))
            x += im.width + gap
        can.save(os.path.join(a.out, f"{hero}_ppu_choices.png"))
        print("written", hero)


if __name__ == "__main__":
    main()

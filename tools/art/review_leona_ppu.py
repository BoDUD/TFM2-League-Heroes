#!/usr/bin/env python3
"""Leona at several densities (the user, 2026-10-31, on the PPU 1.76 redo: 「另外蕾欧娜的模型太高清了 降低点像素」, Lucian's
way - tools/art/review_lucian_ppu.py): her frames (assets/source/ppu/orig, PPU 1.756) brought to each PPU by
ppu_restyle.restyle (nothing written), shown at one game size - her size (hd.rs SIZES) - next to heroes of other
densities as the battlefield draws them (their SIZES too).

    python tools/art/review_leona_ppu.py --out DIR [--ppus 1.756,1.5,1.35,1.2] [--scale 4]

Writes <out>/leona_ppu_choices.png: per PPU the idle's first frame, a swing and a run frame, then Lucian, Lee Sin,
Garen, Jax and Sona, feet on one line; and <out>/leona_ppu_closeup.png: the idle frames at 3x their own pixels next
to each other (how coarse each grid is).
"""
import argparse
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_restyle as R  # noqa: E402
from preview_dense import SIZES  # noqa: E402
from review_reksai_ppu import frame0, shown  # noqa: E402

PEERS = ["lucian", "leesin", "garen", "jax", "sona"]
BG = (96, 112, 96)
FONT = "C:/Windows/Fonts/msyh.ttc"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ppus", default="1.756,1.5,1.35,1.2")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    ppus = [float(x) for x in a.ppus.split(",")]
    font = ImageFont.truetype(FONT, 16) if os.path.exists(FONT) else None
    before = set(glob.glob(os.path.join(R.ORIG, "leona_*")))
    size = SIZES.get("leona", 1.0)
    rows, close = {"待机": [], "普攻": [], "跑步": []}, []
    for p in ppus:
        spec = dict(R.RESTYLE["leona"], ppu=p)
        out = R.restyle("leona", spec, write=False, only=["idle", "attack", "run"])[0]
        now = "（现在）" if p == R.RESTYLE["leona"]["ppu"] else ""
        for tag, k, lab in (("idle", 0, "待机"), ("attack", 2, "普攻"), ("run", 2, "跑步")):
            rows[lab].append((f"PPU {p}{now}", shown(Image.fromarray(out[tag][k][0]), p / size, a.scale)))
        close.append((f"PPU {p}{now}", Image.fromarray(out["idle"][0][0])))
    for f in set(glob.glob(os.path.join(R.ORIG, "leona_*"))) - before:      # (read_orig saves tags it lacks: not ours)
        os.remove(f)
    peers = []
    for h in PEERS:
        im, p = frame0(h)
        peers.append((f"{h}（PPU {p}）", shown(im, p / SIZES.get(h, 1.0), a.scale)))
    gap, top = 18, 26
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
            can.paste(im, (x + (cw - im.width) // 2, y + top + (h - im.height)), im)
            d.text((x, y), lab, fill=(240, 240, 240), font=font)
        y += h + top + gap
    os.makedirs(a.out, exist_ok=True)
    can.save(os.path.join(a.out, "leona_ppu_choices.png"))
    Z = 3
    W = sum(im.width * Z + gap for _, im in close) + gap
    H = max(im.height * Z for _, im in close) + top + gap
    can = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(can)
    x = gap
    for lab, im in close:
        big = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
        can.paste(big, (x, top), big)
        d.text((x, 4), lab, fill=(240, 240, 240), font=font)
        x += big.width + gap
    can.save(os.path.join(a.out, "leona_ppu_closeup.png"))
    print("written", a.out)


if __name__ == "__main__":
    main()

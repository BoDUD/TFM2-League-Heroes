#!/usr/bin/env python3
"""Samira at several densities (the user, 2026-10-25, on the PPU 2.84 redo in game: 「我怎么感觉身体有点细啊 和原版画风不符」,
then 「不不不 你方向错了 感觉降低像素就行了」「泽丽之前也一样 但是后面调整好了」 - the 2026-10-13 restyle that brought the
PPU heroes to Zeri's look at about 2.2): her frames (assets/source/ppu/orig, PPU 2.84) brought to each PPU by
ppu_restyle.restyle (nothing written), shown at one game size next to the heroes restyled then, as the battlefield
draws them.

    python tools/art/review_samira_ppu.py --out DIR [--ppus 2.84,2.2,1.8,1.5] [--scale 4]

Writes <out>/samira_ppu_choices.png: per PPU the idle's first frame, a shot and a run frame, then Zeri, Jinx, Gwen,
Vladimir and Caitlyn, feet on one line; and <out>/samira_ppu_closeup.png: the idle frames at 3x their own pixels next
to each other (how coarse each grid is).
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_restyle as R  # noqa: E402
from review_reksai_ppu import frame0, shown  # noqa: E402

PEERS = ["zeri", "jinx", "gwen", "vladimir", "caitlyn"]
BG = (96, 112, 96)
FONT = "C:/Windows/Fonts/msyh.ttc"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ppus", default="2.84,2.2,1.8,1.5")
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    ppus = [float(x) for x in a.ppus.split(",")]
    font = ImageFont.truetype(FONT, 16) if os.path.exists(FONT) else None
    rows, close = {"待机": [], "开枪": [], "跑步": []}, []
    for p in ppus:
        spec = dict(R.RESTYLE["samira"], ppu=p)
        out = R.restyle("samira", spec, write=False, only=["idle", "attack", "run"])[0]
        now = "（画的密度）" if p == R.ORIG_PPU["samira"] else "（选用）" if p == R.RESTYLE["samira"]["ppu"] else ""
        for tag, k, lab in (("idle", 0, "待机"), ("attack", 3, "开枪"), ("run", 2, "跑步")):
            rows[lab].append((f"PPU {p}{now}", shown(Image.fromarray(out[tag][k][0]), p, a.scale)))
        close.append((f"PPU {p}{now}", Image.fromarray(out["idle"][0][0])))
    peers = []
    for h in PEERS:
        im, p = frame0(h)
        peers.append((f"{h}（PPU {p}）", shown(im, p, a.scale)))
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
            can.paste(im, (x + (cw - im.width) // 2, y + top + (h - im.height) // 2), im)
            d.text((x, y), lab, fill=(240, 240, 240), font=font)
        y += h + top + gap
    os.makedirs(a.out, exist_ok=True)
    can.save(os.path.join(a.out, "samira_ppu_choices.png"))
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
    can.save(os.path.join(a.out, "samira_ppu_closeup.png"))
    print("written", a.out)


if __name__ == "__main__":
    main()

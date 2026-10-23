#!/usr/bin/env python3
"""Nunu & Willump's imported effects for the user's review: every tag of league_nunu_fx / league_nunu_big played on the
arena colour over their idle at game size (the design at PPU 1.37), the pivot where the game puts it (the soles 11
under it), as one looping GIF, 3x.

    python tools/art/review_nunu_fx.py --out dist/nunu_packs/nunu_fx_review.gif

The sheets' frames are cells centred on the pivot (import_nunu_fx.py places each picture there); every tag loops on its
own timing over the GIF's 1.5 s.
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
import pack_nunu_fx as PF  # noqa: E402

FX = os.path.join(ROOT, "league", "effects")
ARENA = (104, 112, 72, 255)
CW, CH, COLS, Z = 130, 92, 5, 3
FEET = 11
STEP, LENGTH = 50, 1500     # ms a GIF frame, ms the GIF


def tags():
    out = []
    for sheet in ("league_nunu_fx", "league_nunu_big"):
        stem = os.path.join(FX, sheet)
        anims = json.load(open(PF.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
        im = Image.open(PF.lp(stem + "#sheet.png")).convert("RGBA")
        for tag, a in anims.items():
            frames = [(im.crop((int(f["data"]["x"]), int(f["data"]["y"]), int(f["data"]["x"] + f["data"]["w"]),
                                int(f["data"]["y"] + f["data"]["h"]))), f["duration"] * 1000) for f in a["frames"]]
            out.append((tag, frames))
    return out


def at(frames, t):
    total = sum(ms for _, ms in frames)
    t %= total
    for im, ms in frames:
        if t < ms:
            return im
        t -= ms
    return frames[-1][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fig = Image.fromarray(PF.design_1x())
    ts = tags()
    rows = (len(ts) + COLS - 1) // COLS
    gif = []
    for t in range(0, LENGTH, STEP):
        can = Image.new("RGBA", (CW * COLS, CH * rows), ARENA)
        d = ImageDraw.Draw(can)
        for k, (tag, frames) in enumerate(ts):
            ox, oy = (k % COLS) * CW, (k // COLS) * CH
            px, py = ox + CW // 2, oy + CH - 6 - FEET          # the pivot: the soles 11 under it, 6 above the cell's foot
            can.alpha_composite(fig, (px - fig.width // 2, py + FEET - fig.height))
            f = at(frames, t)
            can.alpha_composite(f, (px - f.width // 2, py - f.height // 2))
            d.text((ox + 2, oy + 1), tag, fill=(255, 255, 255, 255))
            d.rectangle([ox, oy, ox + CW - 1, oy + CH - 1], outline=(80, 86, 56, 255))
        gif.append(can.resize((can.width * Z, can.height * Z), Image.NEAREST).convert("RGB"))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    gif[0].save(a.out, save_all=True, append_images=gif[1:], duration=STEP, loop=0)
    print(a.out, gif[0].size, len(gif), "frames")


if __name__ == "__main__":
    main()

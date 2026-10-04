#!/usr/bin/env python3
"""Sett's step 3 pack for Codex: the pictures that go with assets/source/sett/PROMPTS_FX.md.

    python tools/art/pack_sett_fx.py --out <folder> [--zip]

Into <folder>:
  PROMPTS_FX.md               the prompts
  design/sett_design.png      the approved design at 8x (assets/source/native/sett_native.png)
  design/sett_size.png        the design at 4x on its soles line (red), 10-square ticks; W's reach (an orange arrow
                              50 squares from his standing point) and R's slam (an orange ellipse 52 x 26 at his feet)
  design/sett_shots.png       the frames the effects sit on, at 4x, a cyan cross on each spot: the idle's fists
                              (Knuckle Down's glow), E's clap (skill 6), W's punch (skill2 5: the fist, and his
                              standing point where the fist picture starts), R's slam (ult_slam 2: his soles)
  style/vi_effects.png        league_vi's effects (docs/preview), a brawler's approved effects: style and brightness
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from native_refs import layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sett")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "sett_native.png")
PIVOT = (64, 88)                 # on the design canvas; the soles' row is 99
W_LENGTH, R_RADIUS = 50, 26      # squares (tools/kit/sett_kit.py: W_LENGTH 50000, R_RADIUS 26000)
BG = (96, 104, 88, 255)
CYAN = (40, 230, 255, 255)
ORANGE = (245, 154, 30, 255)
# (tag, frame, label, spots from the pivot in squares: x right, y down)
SHOTS = [("idle", 0, "idle: Q glow on both fists", [(-10, -5), (10, -5)]),
         ("skill", 5, "E frame 6: the clap", [(7, -11)]),
         ("skill2", 4, "W frame 5: the punch (the fist picture starts at the pivot)", [(24, -14), (0, 0)]),
         ("ult_slam", 1, "R slam frame 2: the crater at his soles", [(0, 11)])]


def frame(tag, k):
    with open(os.path.join(NATIVE, "sett_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    rows = cells["tags"][tag]
    cw, ch = cells["cell"]
    a = np.asarray(Image.open(os.path.join(NATIVE, f"sett_{tag}.png")).convert("RGBA"))[::8, ::8]
    cols, _ = layout(len(rows))
    return a[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw], rows[k]["pivot"]


def cross(d, x, y, r=10):
    d.line((x - r, y, x + r, y), fill=CYAN, width=3)
    d.line((x, y - r, x, y + r), fill=CYAN, width=3)


def size_sheet(z=4):
    a = np.asarray(Image.open(DESIGN).convert("RGBA"))[::8, ::8]
    x0, x1, y0, y1 = 24, 128, 50, 122
    img = Image.new("RGBA", ((x1 - x0) * z, (y1 - y0) * z), BG)
    img.alpha_composite(Image.fromarray(np.ascontiguousarray(a[y0:min(y1, 128), x0:x1])).resize(
        ((x1 - x0) * z, (min(y1, 128) - y0) * z), Image.NEAREST))
    d = ImageDraw.Draw(img)
    px, py, soles = (PIVOT[0] - x0) * z, (PIVOT[1] - y0) * z, (100 - y0) * z
    cx, cy = px, soles - z
    d.ellipse((cx - R_RADIUS * z, cy - R_RADIUS // 2 * z, cx + R_RADIUS * z, cy + R_RADIUS // 2 * z), outline=ORANGE,
              width=2)
    d.line((0, soles, img.width, soles), fill=(230, 30, 30, 255), width=2)
    d.line((px, py, px + W_LENGTH * z, py), fill=ORANGE, width=3)
    tip = px + W_LENGTH * z
    d.polygon([(tip, py), (tip - 12, py - 7), (tip - 12, py + 7)], fill=ORANGE)
    for k in range(0, (x1 - x0) // 10 + 1):
        x = px - 40 * z + k * 10 * z
        if 0 <= x < img.width:
            d.line((x, soles, x, soles + 10), fill=(255, 255, 255, 255), width=2)
    for k in range(0, 6):
        y = soles - k * 10 * z
        d.line((4, y, 18, y), fill=(255, 255, 255, 255), width=2)
        d.text((22, y - 6), str(k * 10), fill=(255, 255, 255, 255))
    d.text((px + 8, py - 18), f"W reach {W_LENGTH}", fill=ORANGE)
    d.text((cx + R_RADIUS * z - 70, cy + R_RADIUS // 2 * z + 4), f"R slam {2 * R_RADIUS} x {R_RADIUS}", fill=ORANGE)
    return img


def shots_sheet(z=4):
    tiles = []
    for tag, k, label, spots in SHOTS:
        f, (px, py) = frame(tag, k)
        x0, x1, y0, y1 = px - 32, px + 36, py - 38, py + 14
        sub = np.ascontiguousarray(f[max(0, y0):y1, max(0, x0):x1])
        img = Image.new("RGBA", ((x1 - x0) * z, (y1 - y0) * z + 24), BG)
        img.alpha_composite(Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(img)
        d.text((6, 6), label, fill=(255, 255, 255, 255))
        for sx, sy in spots:
            cross(d, (px - x0 + sx) * z + z // 2, (py - y0 + sy) * z + z // 2 + 24)
        tiles.append(img)
    W = sum(t.width + 8 for t in tiles)
    out = Image.new("RGBA", (W, max(t.height for t in tiles)), (40, 40, 40, 255))
    x = 0
    for t in tiles:
        out.alpha_composite(t, (x, 0))
        x += t.width + 8
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--zip", action="store_true", help="also write <out>.zip")
    args = ap.parse_args()
    for sub in ("design", "style"):
        os.makedirs(os.path.join(args.out, sub), exist_ok=True)
    shutil.copy(os.path.join(SRC, "PROMPTS_FX.md"), os.path.join(args.out, "PROMPTS_FX.md"))
    shutil.copy(DESIGN, os.path.join(args.out, "design", "sett_design.png"))
    size_sheet().convert("RGB").save(os.path.join(args.out, "design", "sett_size.png"))
    shots_sheet().convert("RGB").save(os.path.join(args.out, "design", "sett_shots.png"))
    shutil.copy(os.path.join(ROOT, "docs", "preview", "league_vi_effects.png"),
                os.path.join(args.out, "style", "vi_effects.png"))
    print("wrote", ", ".join(sorted(os.path.relpath(os.path.join(r, f), args.out)
                                   for r, _, fs in os.walk(args.out) for f in fs)))
    if args.zip:
        print("wrote", shutil.make_archive(os.path.abspath(args.out), "zip", os.path.dirname(os.path.abspath(args.out)),
                                           os.path.basename(os.path.abspath(args.out))))


if __name__ == "__main__":
    main()

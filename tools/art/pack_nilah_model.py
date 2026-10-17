#!/usr/bin/env python3
"""Nilah's step-1 pack for Codex (assets/source/nilah/MODEL_PROMPTS.md): the side-on design on the front's fixed grid.

    python tools/art/pack_nilah_model.py --out dist/nilah_packs/nilah_model_pack

The user's picks (2026-10-13): picture A (the folded whip-blade raised upright beside her shoulder), kept square for
square as the dense design (regrid.py at 12-px squares: 64 x 106, the blade tip row 0, the hair's top row 5, the soles
row 105, the standing point - between the feet - column 34), shown at PPU 2.5 (99 squares head to soles = about 40 game
rows). The front needs no change, so Codex only draws the SIDE-ON view (facing right) on the same grid with the same
squares, height, head and details (memory side-view-design; one face: the head stays the front's 3/4 head, memory
one-face-all-frames). The pack lays the read-back on a 12-px grid of 85 x 128 squares (1020 x 1536 inside the
1024 x 1536 canvas): the blade tip on row TOP, the hair's top on row CROWN, the soles on row SOLE, the standing point
on column MID.
  1_front_grid.png      picture A read back, on the grid with rows / columns numbered: her look, square for square
  2_picture.png         picture A itself on light grey
  3_league_side.png     League's model turned to the side facing right (idle, two run frames; local render, never
                        committed): tools/lol/pose_ref.py --champ Nilah --hq --bg 225,225,225 --no-labels --size 800
                        --fit 0.75 --ground 0.92 --width 1.0 --yaw 70 --mirror --frame Idle1@0 --frame Run@0 --frame Run@700
  4_league_head.png     League's head (pack_nilah_picture.py's refs/3)
  5_style.png           the restyled PPU heroes (Zeri, Nidalee, Karma hd_idle at 4x): the one look to keep
  6_empty_grid.png      the same grid empty with the rows and the middle column marked: the canvas for the side view
"""
import argparse
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "nilah")
PICTURE = os.path.join(SRC, "codex_picture", "nilah-model-A.png")
PACK0 = os.path.join(ROOT, "dist", "nilah_packs", "nilah_pack0", "refs")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "nl_work", "side")
SQ = 12                          # one square of Codex's drawing = one dense pixel
COLS, ROWS = 85, 128             # 1020 x 1536
TOP, CROWN, SOLE = 10, 15, 115   # the blade tip, the hair's top, the soles' lowest row (101 rows hair to soles)
MID = 42                         # the standing point (between the feet)
# the read-back: rows 0..105 (blade tip row 0, the hair row 5, the soles row 105), the standing point column 34
RB_TOP, RB_MID = 0, 34


def readback():
    out = os.path.join(WORK, "rg_A.png")
    subprocess.run([sys.executable, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts", "regrid.py"),
                    PICTURE, out, "--size", str(SQ)], check=True, capture_output=True)
    a = np.array(Image.open(out).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    return a


def place(rb):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    dy, dx = TOP - RB_TOP, MID - RB_MID
    h, w = rb.shape[:2]
    can[dy:dy + h, dx:dx + w] = rb
    return can


def big(can):
    img = Image.new("RGBA", (1024, 1536), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can).resize((COLS * SQ, ROWS * SQ), Image.NEAREST))
    d = ImageDraw.Draw(img)
    for c in range(COLS + 1):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(170, 170, 185, 255), width=1)
    for r in range(ROWS + 1):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(170, 170, 185, 255), width=1)
    for r in range(0, ROWS, 10):
        d.text((2, r * SQ + 1), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 10):
        d.text((c * SQ + 2, 2), str(c), fill=(0, 0, 200, 255))
    d.line([(0, (SOLE + 1) * SQ), (COLS * SQ, (SOLE + 1) * SQ)], fill=(230, 30, 30, 255), width=3)
    d.line([(0, CROWN * SQ), (COLS * SQ, CROWN * SQ)], fill=(30, 170, 60, 255), width=3)
    d.line([(0, TOP * SQ), (COLS * SQ, TOP * SQ)], fill=(160, 60, 200, 255), width=2)
    d.line([((MID + 0.5) * SQ, 0), ((MID + 0.5) * SQ, ROWS * SQ)], fill=(40, 90, 230, 255), width=3)
    return img


def on_grey(im, k=1):
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.resize((im.width * k, im.height * k), Image.NEAREST)


def style():
    shots = [Image.open(os.path.join(SRC, "style_ref", f"{h}_hd_idle_x8.png")).convert("RGBA")
             for h in ("zeri", "nidalee", "karma")]
    shots = [s.resize((s.width // 2, s.height // 2), Image.NEAREST) for s in shots]
    pad = 24
    tall = max(s.height for s in shots)
    img = Image.new("RGBA", (sum(s.width + pad for s in shots) + pad, tall + 2 * pad), (225, 225, 225, 255))
    x = pad
    for s in shots:
        img.alpha_composite(s, (x, pad + tall - s.height))
        x += s.width + pad
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, "nilah")
    os.makedirs(out, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    rb = readback()
    big(place(rb)).convert("RGB").save(os.path.join(out, "1_front_grid.png"))
    pic = Image.open(PICTURE).convert("RGBA")
    al = np.array(pic)
    al[..., 3] = np.where(al[..., 3] > 200, 255, 0)
    pic = Image.fromarray(al)
    box = pic.getbbox()
    on_grey(pic.crop((box[0] - 20, box[1] - 20, box[2] + 20, box[3] + 20))).convert("RGB").save(
        os.path.join(out, "2_picture.png"))
    shutil.copyfile(os.path.join(WORK, "league_side.png"), os.path.join(out, "3_league_side.png"))
    Image.open(os.path.join(PACK0, "3_nilah_league_head.png")).convert("RGB").save(os.path.join(out, "4_league_head.png"))
    style().convert("RGB").save(os.path.join(out, "5_style.png"))
    big(np.zeros((ROWS, COLS, 4), np.uint8)).convert("RGB").save(os.path.join(out, "6_empty_grid.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(a.out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

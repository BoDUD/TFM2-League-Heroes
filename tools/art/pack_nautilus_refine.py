#!/usr/bin/env python3
"""Nautilus's step 1b pack for Codex: the pictures that go with assets/source/nautilus/REFINE_PROMPTS.md.

    python tools/art/pack_nautilus_refine.py --out <folder>

The user picked p35 (tools/art/design_nautilus.py: Codex's raw/A_simple.png cut to 39 x 48, the anchor 11 rows above the
helmet), then: 「头适当的小一点 学这张图」, pointing at Codex's first draft raw/A_first.png (the helmet narrower than the
shoulders, the chest plates showing). Cut to game size that draft blurs (the eyes and the anchor), so Codex redraws the
design at game size: p35's size, pose, anchor and colours, the helmet at A_first's proportions.
p35's helmet (the hood's top to the jaw guard's seam) is HEAD_NOW rows x HEAD_NOW_W columns of the 37 rows helmet to
soles (legs 13 rows, shoulders 34 columns); A_first's is half the height and 0.42 of the shoulders' width - the target
HEAD rows x HEAD_W columns.
  1_current.png / _1x.png   p35 on the 128 x 128 canvas (8x / 1x) with the lines of 5_target
  2_head_reference.png      A_first read back on its own grid (71 x 78 squares) at 8x - the proportions to learn
  3_picture.png             the approved picture A (codex_picture/nautilus-model-A.png) on white, cropped
  4_quality_bar.png         league_alistar, league_blitzcrank, league_leona, league_shen, league_viego at 8x
  5_target.png              p35 faded on the canvas: red = the soles' row (99), blue = the middle column (64), green =
                            the helmet's top (row TOP), cyan = the lowest the jaw guard may reach (row TOP + HEAD - 1),
                            orange = the anchor's highest row, purple = the widest the sprite may be
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_nautilus as D  # noqa: E402
import pack_nautilus_model as M  # noqa: E402

Z = 8
SOLES, MID = 99, 64
TOP = 63                      # p35's helmet top (the hood) on the canvas
ANCHOR_TOP = 52               # p35's anchor top
HEAD_NOW, HEAD_NOW_W = 23, 21
HEAD, HEAD_W = 18, 14         # the target helmet: rows (hood top to the jaw guard's seam) x columns (hood included)
MAX_W = 40
COL0 = MID - MAX_W // 2


def lines(img):
    d = ImageDraw.Draw(img)
    d.line([(0, (SOLES + 1) * Z), (1023, (SOLES + 1) * Z)], fill=(230, 30, 30, 255), width=2)
    d.line([(MID * Z, 0), (MID * Z, 1023)], fill=(40, 90, 230, 255), width=2)
    d.line([(0, TOP * Z), (1023, TOP * Z)], fill=(30, 170, 60, 255), width=2)
    d.line([(0, (TOP + HEAD) * Z), (1023, (TOP + HEAD) * Z)], fill=(20, 200, 210, 255), width=2)
    d.line([(0, ANCHOR_TOP * Z), (1023, ANCHOR_TOP * Z)], fill=(245, 140, 20, 255), width=2)
    for x in (COL0 * Z, (COL0 + MAX_W) * Z):
        d.line([(x, 0), (x, 1023)], fill=(150, 60, 200, 255), width=2)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cur = np.asarray(Image.open(D.lp(D.OUT)).convert("RGBA"))
    Image.fromarray(cur).save(os.path.join(a.out, "1_current_1x.png"))
    white = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
    white.alpha_composite(Image.fromarray(cur))
    lines(white.resize((1024, 1024), Image.NEAREST)).convert("RGB").save(os.path.join(a.out, "1_current.png"))
    first = D.read_back("first")
    bg = Image.new("RGBA", (first.shape[1], first.shape[0]), (255, 255, 255, 255))
    bg.alpha_composite(Image.fromarray(first))
    bg.resize((first.shape[1] * Z, first.shape[0] * Z), Image.NEAREST).convert("RGB").save(
        os.path.join(a.out, "2_head_reference.png"))
    pic = M.shortened(Image.open(M.PICTURE).convert("RGBA"))
    box = pic.getchannel("A").getbbox()
    sheet = Image.new("RGBA", pic.size, (255, 255, 255, 255))
    sheet.alpha_composite(pic)
    sheet.crop((box[0] - 30, box[1] - 30, box[2] + 30, box[3] + 20)).convert("RGB").save(
        os.path.join(a.out, "3_picture.png"))
    M.quality_bar().convert("RGB").save(os.path.join(a.out, "4_quality_bar.png"))
    faded = cur.copy()
    faded[..., 3] = np.where(cur[..., 3] > 0, 70, 0)
    white = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
    white.alpha_composite(Image.fromarray(faded))
    lines(white.resize((1024, 1024), Image.NEAREST)).convert("RGB").save(os.path.join(a.out, "5_target.png"))
    print("wrote", ", ".join(sorted(os.listdir(a.out))))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Galio's step-1 pack for Codex (assets/source/galio/MODEL_PROMPTS.md): the dense design, front and side, on a fixed grid.

    python tools/art/pack_galio_model.py --out dist/galio_packs/galio_model_pack

The user's picks (2026-10-13): picture A (wings raised high), shown at 2.0 squares a game pixel (one square of the
design = one dense pixel, PPU 2.0: the body 76 squares crown to soles = 38 game rows, 51 with the wings), the fists
made CLENCHED stone fists (picture A drew both as curled spirals - League's own left hand is a half-open claw). Picture A
read back on its own grid (regrid.py, 12-px squares, 102 x 83) is already the front design square for square: the pack
lays it on a 12-px grid of 85 x 128 squares (1020 x 1536 inside the 1024 x 1536 canvas) - wing tips on row TOP, the
crown on row CROWN, the soles on row SOLE, the standing point on column MID - and asks Codex to keep every square but
the two fists, and to draw the SIDE-ON view (facing right) on the same grid with the same squares, height, head and
details (memory side-view-design; one face: the head stays the front's 3/4 head, memory one-face-all-frames).
  1_front_grid.png      picture A read back, on the grid with rows / columns numbered: the front to keep 1:1
  2_picture.png         picture A itself on light grey (the look)
  3_league_fists.png    League's model, his two hands (the right one clenched: both fists like it)
  4_league_side.png     League's model turned to the side facing right (idle, two run frames; yaw -70 mirrored, each
                        cell flipped: local render, never committed)
  5_league_head.png     League's head (pack_galio_picture.py's refs/3)
  6_style.png           the restyled PPU heroes (Mordekaiser, Braum, Zeri hd_idle at 4x): the one look to keep
  7_empty_grid.png      the same grid empty with the rows and the middle column marked: the canvas for the side view
The League renders: tools/lol/pose_ref.py --champ Galio --hq --bg 225,225,225 --no-labels --size 800 --fit 0.75 --ground
0.92 --width 1.25 --yaw -70 --mirror --frame galio_idle01@0 --frame galio_run@0 --frame galio_run@480 (side), and --size
2400 --fit 0.8 --ground 0.94 --width 1.0 --yaw 30 --mirror --frame galio_idle01@0 cropped round the hands (fists).
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
SRC = os.path.join(ROOT, "assets", "source", "galio")
PICTURE = os.path.join(SRC, "codex_picture", "galio-model-A.png")
PACK0 = os.path.join(ROOT, "dist", "galio_packs", "galio_pack0", "refs")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "gl_work", "side")
SQ = 12                         # one square of Codex's drawing = one dense pixel
COLS, ROWS = 85, 128            # 1020 x 1536
TOP, CROWN, SOLE = 14, 40, 115  # wing tips, the crown spike's top, the soles' lowest row (76 rows crown to soles)
MID = 49                        # the standing point (between the feet)
# the read-back: rows 0..101 (wing tips row 0, the crown row 26, the soles row 101), the standing point column 48
RB_TOP, RB_MID = 0, 48


def readback():
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    out = os.path.join(WORK, "rg_A.png")
    subprocess.run([sys.executable, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts", "regrid.py"),
                    PICTURE, out], check=True, capture_output=True)
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
             for h in ("mordekaiser", "braum", "zeri")]
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
    out = os.path.join(a.out, "galio")
    os.makedirs(out, exist_ok=True)
    rb = readback()
    big(place(rb)).convert("RGB").save(os.path.join(out, "1_front_grid.png"))
    pic = Image.open(PICTURE).convert("RGBA")
    al = np.array(pic)
    al[..., 3] = np.where(al[..., 3] > 200, 255, 0)
    pic = Image.fromarray(al)
    box = pic.getbbox()
    on_grey(pic.crop((box[0] - 20, box[1] - 20, box[2] + 20, box[3] + 20))).convert("RGB").save(
        os.path.join(out, "2_picture.png"))
    shutil.copyfile(os.path.join(WORK, "league_fists.png"), os.path.join(out, "3_league_fists.png"))
    shutil.copyfile(os.path.join(WORK, "league_side.png"), os.path.join(out, "4_league_side.png"))
    Image.open(os.path.join(PACK0, "3_galio_league_head.png")).convert("RGB").save(os.path.join(out, "5_league_head.png"))
    style().convert("RGB").save(os.path.join(out, "6_style.png"))
    big(np.zeros((ROWS, COLS, 4), np.uint8)).convert("RGB").save(os.path.join(out, "7_empty_grid.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(a.out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

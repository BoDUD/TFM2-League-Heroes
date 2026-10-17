#!/usr/bin/env python3
"""Bard's step-1 pack for Codex (assets/source/bard/MODEL_PROMPTS.md): picture A redrawn at 85 % + a side view, one grid.

    python tools/art/pack_bard_model.py --out dist/bard_packs/bard_model_pack

The user's picks (2026-10-13): picture A (the instrument on his near shoulder), but "A 模型太大了 缩小一点" -> 85 %, made
by an on-grid redraw (memory muddy-design-grid-redraw: Codex's own final had come down from its 8-10 px drafts and the
shoulder / horn read muddy), PPU 1.5 kept. Codex's final A is 60 squares mane-top to soles on a 12-px grid whose
origin is x = 2 (1024 = 2 + 85 x 12 + 2); the redraw is 51 squares (85 %), the antenna and the raised hand above that.
So Codex draws on one grid of 85 x 128 squares of 12 px (origin x 2, y 0):
  bard-front.png   the 3/4 front (idle and the ban/pick card): picture A again, smaller and clean
  bard-side-A.png  SIDE-ON facing right (every action's base, memory side-view-design), full profile body
  bard-side-B.png  the same, the body three-quarter side
with the mane top on row CROWN, the soles' lowest row SOLE, the standing point (between the feet) on column MID, and
the SAME head (the round mane with the bronze mask showing both eye holes, memory one-face-all-frames) in all three.
Pack files:
  1_front_now_grid.png   picture A read back (60 squares) on the grid, soles on SOLE, with the 85 % outline to draw in
  2_picture_A.png        Codex's own final A (the look)
  3_draft_A01.png,       Codex's two raw A drafts (8 / 12 px squares): how the shoulder, the bell-mouth, the horn and
  4_draft_A02.png        the bells were meant to read
  5_league_side.png      League's model turned to the side facing right (idle, two run frames; local render, never
                         committed): pose_ref.py --champ Bard --hq --yaw 70 --mirror Bard_Idle01@0 Bard_Run01@0 @717
  6_league_head.png,     League's head and instrument close-ups (pack_bard_picture.py refs/3 and refs/8)
  7_league_instrument.png
  8_style.png            the PPU-1.5 heroes (galio hd, braum / zeri / nidalee lo at 4x): the look to keep
  9_empty_grid.png       the grid empty with CROWN / SOLE / MID marked: the canvas for each picture
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
SRC = os.path.join(ROOT, "assets", "source", "bard")
PICTURE = os.path.join(SRC, "codex_picture", "bard-model-A.png")
DRAFTS = [os.path.join(SRC, "codex_picture", "raw", f) for f in ("A-01.png", "A-02.png")]
PACK0 = os.path.join(ROOT, "dist", "bard_packs", "bard_pack0", "refs")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ba_work", "side")
SQ, X0 = 12, 2                   # one square of Codex's drawing = one dense pixel; the grid starts at x = 2
COLS, ROWS = 85, 128
CROWN, SOLE = 55, 105            # mane top, the soles' lowest row: 51 rows = 85 % of picture A's 60
MID = 42                         # the standing point (between the feet)
SCALE = 0.85
# picture A read back: mane top row 36, soles row 93, the feet's middle column 47
RB_SOLE, RB_MID = 93, 47


def readback():
    a = np.array(Image.open(PICTURE).convert("RGBA"))
    g = a[SQ // 2::SQ, X0 + SQ // 2::SQ][:ROWS, :COLS].copy()
    g[..., 3] = np.where(g[..., 3] > 0, 255, 0)
    return g


def place(rb, dy, dx):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    h, w = rb.shape[:2]
    ys, xs = slice(max(0, dy), min(ROWS, dy + h)), slice(max(0, dx), min(COLS, dx + w))
    can[ys, xs] = rb[ys.start - dy:ys.stop - dy, xs.start - dx:xs.stop - dx]
    return can


def ghost(rb):
    """The 85 % silhouette's edge, soles on SOLE and feet on MID: the size to draw (a mask only)."""
    m = Image.fromarray(((rb[..., 3] > 0) * 255).astype(np.uint8))
    bb = m.getbbox()
    m = m.crop(bb)
    s = m.resize((round(m.width * SCALE), round(m.height * SCALE)), Image.NEAREST)
    a = np.array(s) > 0
    edge = a & ~(np.pad(a, 1)[2:, 1:-1] & np.pad(a, 1)[:-2, 1:-1] & np.pad(a, 1)[1:-1, 2:] & np.pad(a, 1)[1:-1, :-2])
    out = np.zeros((ROWS, COLS), bool)
    dy = SOLE + 1 - a.shape[0]
    dx = MID - round((RB_MID - bb[0]) * SCALE)
    out[dy:dy + a.shape[0], dx:dx + a.shape[1]] = edge
    return out


def big(can, mark=None):
    img = Image.new("RGBA", (1024, 1536), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can).resize((COLS * SQ, ROWS * SQ), Image.NEAREST), (X0, 0))
    d = ImageDraw.Draw(img)
    if mark is not None:
        for r, c in zip(*np.where(mark)):
            d.rectangle([X0 + c * SQ + 3, r * SQ + 3, X0 + c * SQ + SQ - 4, r * SQ + SQ - 4], outline=(255, 0, 200, 255), width=2)
    for c in range(COLS + 1):
        d.line([(X0 + c * SQ, 0), (X0 + c * SQ, ROWS * SQ)], fill=(170, 170, 185, 255), width=1)
    for r in range(ROWS + 1):
        d.line([(X0, r * SQ), (X0 + COLS * SQ, r * SQ)], fill=(170, 170, 185, 255), width=1)
    for r in range(0, ROWS, 10):
        d.text((X0 + 2, r * SQ + 1), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 10):
        d.text((X0 + c * SQ + 2, 2), str(c), fill=(0, 0, 200, 255))
    d.line([(X0, (SOLE + 1) * SQ), (X0 + COLS * SQ, (SOLE + 1) * SQ)], fill=(230, 30, 30, 255), width=3)
    d.line([(X0, CROWN * SQ), (X0 + COLS * SQ, CROWN * SQ)], fill=(30, 170, 60, 255), width=3)
    d.line([(X0 + (MID + 0.5) * SQ, 0), (X0 + (MID + 0.5) * SQ, ROWS * SQ)], fill=(40, 90, 230, 255), width=3)
    return img


def on_grey(im, k=1):
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.resize((im.width * k, im.height * k), Image.NEAREST)


def style():
    names = ["galio_hd_idle_x8", "braum_lo_idle_x8", "zeri_lo_idle_x8", "nidalee_lo_idle_x8"]
    shots = [Image.open(os.path.join(SRC, "style_ref", f"{h}.png")).convert("RGBA") for h in names]
    shots = [s.resize((s.width // 2, s.height // 2), Image.NEAREST) for s in shots]
    pad = 24
    tall = max(s.height for s in shots)
    img = Image.new("RGBA", (sum(s.width + pad for s in shots) + pad, tall + 2 * pad), (225, 225, 225, 255))
    x = pad
    for s in shots:
        img.alpha_composite(s, (x, pad + tall - s.height))
        x += s.width + pad
    return img


def league_side():
    path = os.path.join(WORK, "league_side.png")
    if not os.path.exists(path):
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--champ", "Bard", "--hq",
                        "--bg", "225,225,225", "--no-labels", "--size", "800", "--fit", "0.75", "--ground", "0.92",
                        "--width", "1.0", "--yaw", "70", "--mirror", "--frame", "Bard_Idle01@0", "--frame",
                        "Bard_Run01@0", "--frame", "Bard_Run01@717", "--name", "league_side", "--out", WORK], check=True)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, "bard")
    os.makedirs(out, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    rb = readback()
    big(place(rb, SOLE - RB_SOLE, MID - RB_MID), ghost(rb)).convert("RGB").save(os.path.join(out, "1_front_now_grid.png"))
    pic = Image.open(PICTURE).convert("RGBA")
    box = pic.getbbox()
    on_grey(pic.crop((box[0] - 20, box[1] - 20, box[2] + 20, box[3] + 20))).convert("RGB").save(
        os.path.join(out, "2_picture_A.png"))
    for k, f in enumerate(DRAFTS):
        on_grey(Image.open(f).convert("RGBA")).convert("RGB").save(os.path.join(out, f"{3 + k}_draft_A0{1 + k}.png"))
    shutil.copyfile(league_side(), os.path.join(out, "5_league_side.png"))
    Image.open(os.path.join(PACK0, "3_bard_league_head.png")).convert("RGB").save(os.path.join(out, "6_league_head.png"))
    Image.open(os.path.join(PACK0, "8_bard_league_instrument.png")).convert("RGB").save(
        os.path.join(out, "7_league_instrument.png"))
    style().convert("RGB").save(os.path.join(out, "8_style.png"))
    big(np.zeros((ROWS, COLS, 4), np.uint8)).convert("RGB").save(os.path.join(out, "9_empty_grid.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(a.out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

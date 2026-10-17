#!/usr/bin/env python3
"""Milio's step-1 pack for Codex (assets/source/milio/MODEL_PROMPTS.md): the front redrawn on its game grid + side-on.

    python tools/art/pack_milio_model.py --out dist/milio_packs/milio_model_pack [--no-render]

The user's picks (2026-10-15): picture B (the boy + the round fire spirit behind his shoulder), 32 game rows hair top
to soles at about 2.2 squares a game pixel = 70 squares (tools/art/design_milio_cut.py -> assets/source/milio/hd/
cut_front.png, 48 x 70, standing point column 32). Cut from Codex's ~11-px picture the face reads muddy, so Codex
redraws the FRONT square for square on the grid (memory muddy-design-grid-redraw) and draws the SIDE-ON views facing
right (memory side-view-design; every action is side-on): A full profile, B three quarters to the side, the boy only.
One face (memory one-face-all-frames): the side views keep the front's 3/4 head.
The grid: SQ-px squares, COLS x ROWS on a 1024 x 1536 portrait canvas: hair top on row HAIR, soles on row SOLE, the
standing point (between the sandals) on column MID.
  1_front_grid.png     the cut on the grid (rows / columns numbered): size, position, colours - muddy, to be redrawn
  2_picture_B.png      Codex's own picture B (step 0): the look to keep, crisp
  3_league_side.png    League's Milio facing right at yaw 80 / 90 (idle) and a run frame (local render, never committed)
  4_style.png          the restyled PPU heroes (Zeri, Kindred, Nilah hd_idle at 4x): the one look
  5_empty_grid.png     the same grid empty, the lines marked: the canvas
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
SRC = os.path.join(ROOT, "assets", "source", "milio")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "mi_work", "side")
SQ = 12                          # one square of Codex's drawing = one dense pixel
COLS, ROWS = 85, 128             # 1020 x 1536
HAIR, SOLE = 30, 99              # hair top, the sandals' lowest row (70 rows)
MID = 48                         # the standing point (between the sandals)
DESIGN_MID = 32                  # ... in hd/cut_front.png
GREY = (225, 225, 225, 255)
IDLE = "spell4_idle_in@600"


def place(a):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    h, w = a.shape[:2]
    dy, dx = HAIR, MID - DESIGN_MID
    can[dy:dy + h, dx:dx + w] = a
    return can


def big(can, bg=(255, 255, 255, 255)):
    img = Image.new("RGBA", (1024, 1536), bg)
    img.alpha_composite(Image.fromarray(can).resize((COLS * SQ, ROWS * SQ), Image.NEAREST))
    d = ImageDraw.Draw(img)
    for c in range(0, COLS + 1, 2):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(200, 200, 212, 255), width=1)
    for r in range(0, ROWS + 1, 2):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(200, 200, 212, 255), width=1)
    for r in range(0, ROWS, 10):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(150, 150, 170, 255), width=1)
        d.text((2, r * SQ + 1), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 10):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(150, 150, 170, 255), width=1)
        d.text((c * SQ + 2, 2), str(c), fill=(0, 0, 200, 255))
    d.line([(0, (SOLE + 1) * SQ), (COLS * SQ, (SOLE + 1) * SQ)], fill=(230, 30, 30, 255), width=3)
    d.line([(0, HAIR * SQ), (COLS * SQ, HAIR * SQ)], fill=(30, 170, 60, 255), width=3)
    d.line([((MID + 0.5) * SQ, 0), ((MID + 0.5) * SQ, ROWS * SQ)], fill=(40, 90, 230, 255), width=3)
    return img


def render():
    os.makedirs(WORK, exist_ok=True)
    pr = os.path.join(ROOT, "tools", "lol", "pose_ref.py")
    for yaw, frames, name in ((80, [IDLE], "side80"), (90, [IDLE, "run_alt_2@0"], "side90")):
        cmd = [sys.executable, pr, "--champ", "Milio", "--hq", "--hide-submeshes", "--bg", "225,225,225",
               "--no-labels", "--size", "800", "--fit", "0.75", "--ground", "0.92", "--width", "0.8", "--yaw", str(yaw),
               "--name", name, "--out", WORK]
        for f in frames:
            cmd += ["--frame", f]
        subprocess.run(cmd, check=True, capture_output=True)
    a, b = Image.open(os.path.join(WORK, "side80.png")), Image.open(os.path.join(WORK, "side90.png"))
    img = Image.new("RGB", (a.width + b.width, max(a.height, b.height)), GREY[:3])
    img.paste(a, (0, 0))
    img.paste(b, (a.width, 0))
    img.save(os.path.join(WORK, "league_side.png"))


def style():
    shots = [Image.open(os.path.join(SRC, "style_ref", f"{h}_hd_idle_x8.png")).convert("RGBA")
             for h in ("zeri", "kindred", "nilah")]
    shots = [s.resize((s.width // 2, s.height // 2), Image.NEAREST) for s in shots]
    pad = 24
    tall = max(s.height for s in shots)
    img = Image.new("RGBA", (sum(s.width + pad for s in shots) + pad, tall + 2 * pad), GREY)
    x = pad
    for s in shots:
        img.alpha_composite(s, (x, pad + tall - s.height))
        x += s.width + pad
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    if not a.no_render:
        render()
    front = place(np.array(Image.open(os.path.join(SRC, "hd", "cut_front.png"))))
    big(front).convert("RGB").save(os.path.join(out, "1_front_grid.png"))
    pic = Image.open(os.path.join(SRC, "codex_picture", "milio-model-B.png")).convert("RGBA")
    can = Image.new("RGBA", pic.size, GREY)
    can.alpha_composite(pic)
    can.convert("RGB").save(os.path.join(out, "2_picture_B.png"))
    shutil.copyfile(os.path.join(WORK, "league_side.png"), os.path.join(out, "3_league_side.png"))
    style().convert("RGB").save(os.path.join(out, "4_style.png"))
    big(np.zeros((ROWS, COLS, 4), np.uint8)).convert("RGB").save(os.path.join(out, "5_empty_grid.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

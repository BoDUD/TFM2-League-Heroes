#!/usr/bin/env python3
"""Kindred's step-1 pack for Codex (assets/source/kindred/MODEL_PROMPTS.md): side-on Lamb and Wolf on the front's grid.

    python tools/art/pack_kindred_model.py --out dist/kindred_packs/kindred_model_pack [--no-render]

The user's picks (2026-10-14): picture B read back square for square (tools/art/design_kindred_hd.py ->
assets/source/kindred/hd/front.png, 227 x 166: the bow tip row 0, the mask's ear tips row 12, the hooves' lowest row 165,
Lamb's standing point - between the hooves - column 162; the Wolf at 55 % of Codex's, behind her hips). The front needs
no change, so Codex only draws the SIDE-ON views facing right (memory side-view-design; every action is side-on), each
figure on its own: Lamb A (full profile) and B (three quarters to the side), and the Wolf in profile, on the same
squares, height and details. One face (memory one-face-all-frames): Lamb keeps the front's mask head.
The pack lays the design on a SQ-px grid of COLS x ROWS squares (1536 x 1020 inside 1536 x 1024): the bow tip on row
TOP, the ear tips on row EARS, the hooves on row SOLE, Lamb's standing point on column MID.
  1_front_grid.png     the approved design on the grid, rows / columns numbered: their look, square for square
  2_front_layers.png   the same design as two layers (Lamb / Wolf) on the grid
  3_league_lamb.png    League's Lamb at yaw 70 facing right (idle, two run frames; local render, never committed)
  4_league_wolf.png    League's Wolf in profile facing right (two idle moments; local render)
  5_style.png          the restyled PPU heroes (Zeri, Nilah, Nidalee hd_idle at 4x): the one look to keep
  6_empty_grid.png     the same grid empty with the rows and the middle column marked: the canvas for the side views
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
SRC = os.path.join(ROOT, "assets", "source", "kindred")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "kn_work", "side")
SQ = 6                           # one square of Codex's drawing = one dense pixel
COLS, ROWS = 256, 170            # 1536 x 1020
TOP, EARS, SOLE = 2, 14, 167     # bow tip, mask ear tips, the hooves' lowest row (153 rows ears to hooves)
MID = 170                        # Lamb's standing point (between the hooves)
DESIGN_MID = 162                 # ... in hd/front.png (hooves at columns 126-148 and 178-198)
GREY = (225, 225, 225, 255)


def place(a):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    dy, dx = TOP, MID - DESIGN_MID
    h, w = a.shape[:2]
    can[dy:dy + h, dx:dx + w] = a
    return can


def big(can, bg=(255, 255, 255, 255)):
    img = Image.new("RGBA", (COLS * SQ, 1024), bg)
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
    d.line([(0, EARS * SQ), (COLS * SQ, EARS * SQ)], fill=(30, 170, 60, 255), width=3)
    d.line([(0, TOP * SQ), (COLS * SQ, TOP * SQ)], fill=(160, 60, 200, 255), width=2)
    d.line([((MID + 0.5) * SQ, 0), ((MID + 0.5) * SQ, ROWS * SQ)], fill=(40, 90, 230, 255), width=3)
    return img


def layers():
    lamb = place(np.array(Image.open(os.path.join(SRC, "hd", "front_lamb.png"))))
    wolf = place(np.array(Image.open(os.path.join(SRC, "hd", "front_wolf.png"))))
    # side by side on one grid: the wolf moved left of Lamb's box so both read whole
    ys, xs = np.nonzero(wolf[..., 3])
    shift = xs.min() - 2
    w2 = np.zeros_like(wolf)
    w2[:, :COLS - shift] = wolf[:, shift:]
    ly, lx = np.nonzero(lamb[..., 3])
    both = lamb.copy()
    m = w2[..., 3] > 0
    both[m] = w2[m]
    return both


def render():
    os.makedirs(WORK, exist_ok=True)
    pr = os.path.join(ROOT, "tools", "lol", "pose_ref.py")
    subprocess.run([sys.executable, pr, "--champ", "Kindred", "--hq", "--hide-submeshes", "--bg", "225,225,225",
                    "--no-labels", "--size", "800", "--fit", "0.75", "--ground", "0.92", "--width", "1.0", "--yaw", "70",
                    "--frame", "Lamb_Idle_loop@0", "--frame", "Lamb_run@0", "--frame", "Lamb_run@300",
                    "--name", "league_lamb", "--out", WORK], check=True, capture_output=True)
    subprocess.run([sys.executable, pr, "--champ", "KindredWolf", "--wad", "Kindred", "--hq", "--hide-submeshes",
                    "--bg", "225,225,225", "--no-labels", "--size", "700", "--fit", "0.55", "--ground", "0.85",
                    "--width", "1.4", "--yaw", "95", "--frame", "Wolf_Idle_base_movement@0",
                    "--frame", "Wolf_Idle_base_movement@1000", "--name", "league_wolf", "--out", WORK],
                   check=True, capture_output=True)


def style():
    shots = [Image.open(os.path.join(SRC, "style_ref", f"{h}_hd_idle_x8.png")).convert("RGBA")
             for h in ("zeri", "nilah", "nidalee")]
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
    out = os.path.join(a.out, "kindred")
    os.makedirs(out, exist_ok=True)
    if not a.no_render:
        render()
    front = place(np.array(Image.open(os.path.join(SRC, "hd", "front.png"))))
    big(front).convert("RGB").save(os.path.join(out, "1_front_grid.png"))
    big(layers()).convert("RGB").save(os.path.join(out, "2_front_layers.png"))
    shutil.copyfile(os.path.join(WORK, "league_lamb.png"), os.path.join(out, "3_league_lamb.png"))
    shutil.copyfile(os.path.join(WORK, "league_wolf.png"), os.path.join(out, "4_league_wolf.png"))
    style().convert("RGB").save(os.path.join(out, "5_style.png"))
    big(np.zeros((ROWS, COLS, 4), np.uint8)).convert("RGB").save(os.path.join(out, "6_empty_grid.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(a.out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

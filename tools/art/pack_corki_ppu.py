#!/usr/bin/env python3
"""Corki's PPU pack for Codex (assets/source/corki/PPU_PROMPTS.md): the side view, the key poses and the moving parts,
drawn on the dense design's own grid.

    python tools/art/pack_corki_ppu.py --out dist/corki_packs/corki_ppu_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-12: 「直接用PPU做吧」. The dense front design is the picture they picked read back on its own grid
(tools/art/design_corki_hd.py -> assets/source/corki/hd/front.png, 146 x 125 squares, 48 colours; PPU 4 in league.dll).
He is a rigid craft, so every action is posed by moving whole drawings (tools/art/rig_corki_hd.py: whole-craft moves,
the hover's bob, the rotors and the gun barrels swapped through their turn states) - what translation cannot give is
drawn here once: the craft turned side-on (every action but the idle), nose down (flying forward, the dash), nose up
(the recoil), the death's fall and crash, and the rotors' and the barrels' turn states. Every drawing on the same
SQ-px grid as the design (one drawn square = one dense pixel).
  design/corki_front.png        the dense design at SQ px a square (transparent); _1x one pixel a square
  design/corki_palette.png      its 48 colours
  design/corki_front_grid.png   the design on the grid canvas with the lines the side view keeps (top, bombs' bottom)
  design/empty_grid.png         the empty grid canvas, the same lines
  refs/1_picture.png            the user's picture 2 (the look)
  refs/2_league_side.png        League's model side-on facing right: idle + two flying frames (local render)
  refs/3_league_lean.png        League's flying frames 3/4 (nose down as he moves; local render)
  refs/4_league_death.png       League's death: the craft flips and drops nose first (local render)
  refs/5_league_actions.png     attack, Q bomb, E gatling, R missile, W dash moments (local render)
Renders are Riot's models: local only, never committed.
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
SRC = os.path.join(ROOT, "assets", "source", "corki")
FRONT = os.path.join(SRC, "hd", "front.png")
PICTURE = os.path.join(SRC, "user_picture", "corki-picture-2.png")
SQ = 8                           # pixels a square in the pack (1536 x 1024 = 192 x 128 squares)
COLS, ROWS = 192, 128
TOP = 1                          # the propellers' top row (the design is 125 rows: rows 1-125)
BOT = 125                        # the bombs' bottom row
X0 = 23                          # the design's left column on the grid canvas (146 wide: columns 23-168)


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def canvas(design=None):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    if design is not None:
        h, w = design.shape[:2]
        can[TOP:TOP + h, X0:X0 + w] = design
    img = Image.new("RGBA", (COLS * SQ, ROWS * SQ), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(up(can, SQ)))
    d = ImageDraw.Draw(img)
    for c in range(0, COLS + 1, 10):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(240, 210, 60, 255), width=1)
        if c < COLS:
            d.text((c * SQ + 2, 2), str(c), fill=(0, 0, 200, 255))
    for r in range(0, ROWS + 1, 10):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(240, 210, 60, 255), width=1)
        if r < ROWS:
            d.text((2, r * SQ + 2), str(r), fill=(200, 0, 0, 255))
    d.line([(0, TOP * SQ), (COLS * SQ, TOP * SQ)], fill=(30, 170, 60, 255), width=2)
    d.line([(0, (BOT + 1) * SQ), (COLS * SQ, (BOT + 1) * SQ)], fill=(230, 30, 30, 255), width=2)
    return img


def league(lol, out, name, frames, yaw, size, fit=0.62, width=1.4):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Corki", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", "0.92", "--width",
           str(width), "--yaw", str(yaw), "--mirror", "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    if os.path.isdir(a.out):
        shutil.rmtree(a.out)
    des, refs = os.path.join(a.out, "design"), os.path.join(a.out, "refs")
    os.makedirs(des)
    os.makedirs(refs)
    front = np.asarray(Image.open(FRONT).convert("RGBA"))
    assert front.shape[0] == BOT - TOP + 1, front.shape
    Image.fromarray(up(front, SQ)).save(os.path.join(des, "corki_front.png"))
    Image.fromarray(front).save(os.path.join(des, "corki_front_1x.png"))
    cols = np.unique(front[front[..., 3] > 0][:, :3], axis=0)
    cols = cols[np.argsort(cols.sum(axis=1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(des, "corki_palette.png"))
    canvas(front).convert("RGB").save(os.path.join(des, "corki_front_grid.png"))
    canvas().convert("RGB").save(os.path.join(des, "empty_grid.png"))
    pic = Image.open(PICTURE).convert("RGBA")
    bg = Image.new("RGBA", pic.size, (225, 225, 225, 255))
    bg.alpha_composite(pic)
    bg.convert("RGB").save(os.path.join(refs, "1_picture.png"))
    league(a.lol, refs, "2_league_side", ["corki_idle1@0", "corki_run@0", "corki_run@500"], 80, 800)
    league(a.lol, refs, "3_league_lean", ["corki_run@0", "corki_run@250", "corki_run@500"], 30, 800)
    league(a.lol, refs, "4_league_death", ["corki_death@0", "corki_death@250", "corki_death@500", "corki_death@800",
                                           "corki_death@1300"], 75, 700, fit=0.34, width=1.6)
    league(a.lol, refs, "5_league_actions", ["corki_attack1@300", "corki_spell1@330", "corki_spell3@300",
                                             "corki_spell4@200", "corki_spell2@300"], 75, 700, fit=0.5, width=1.6)
    shutil.copyfile(os.path.join(SRC, "PPU_PROMPTS.md"), os.path.join(a.out, "PPU_PROMPTS.md"))
    print(f"design {front.shape[1]}x{front.shape[0]} squares, {len(cols)} colours")
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()

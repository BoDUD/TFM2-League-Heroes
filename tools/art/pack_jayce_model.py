#!/usr/bin/env python3
"""Jayce's step-1 pack for Codex (assets/source/jayce/MODEL_PROMPTS.md): both forms' fronts redrawn on their game grid
+ side-on views.

    python tools/art/pack_jayce_model.py --out dist/jayce_packs/jayce_model_pack [--no-render]

The user's picks (2026-10-15): hammer A2 and cannon B2, crown to soles 38 game rows at 1.5 squares a game pixel = 57
squares (the cannon stance 54: knees bent), tools/art/design_jayce_cut.py -> assets/source/jayce/hd/cut_hammer-A2.png
(51 x 71, standing col 31) and cut_cannon-B2.png (68 x 54, standing col 30). Cut from Codex's ~8-11 px takes the face
reads muddy, so Codex redraws each FRONT square for square on the grid (memory muddy-design-grid-redraw) and draws the
SIDE-ON views facing right (memory side-view-design; every action is side-on), A full profile and B three quarters to
the side. One face (memory one-face-all-frames): the side views keep the front's 3/4 head.
The grids (SQ-px squares): hammer COLS x ROWS on a 1024 x 1536 portrait, the cannon on a 1536 x 1024 landscape; per form
the crown row, the soles row and the standing column below (FORMS).
  1_hammer_grid.png / 2_cannon_grid.png   the cuts on their grids (numbered lines): size, position, colours - muddy
  3_hammer_A2.png / 4_cannon_B2.png       Codex's own step-0 takes: the look to keep, crisp
  5_league_side.png                        League's Jayce facing right: hammer and cannon idles at yaw 80 / 90 and a run
                                           frame of each (local render, never committed)
  6_style.png                              this pack's heroes at the same density (1.5): Galio hd_idle, Braum / Zeri /
                                           Nidalee lo_idle at 4x
  7_hammer_empty.png / 8_cannon_empty.png  the same grids empty: the canvases
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
SRC = os.path.join(ROOT, "assets", "source", "jayce")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "jy_work", "side")
SQ = 12                          # one square of Codex's drawing = one dense pixel
GREY = (225, 225, 225, 255)
# form -> (cut, canvas px, crown row, soles row (the lowest drawn row), standing column, the cut's standing column)
FORMS = {
    "hammer": ("cut_hammer-A2.png", (1024, 1536), 44, 100, 48, 31),
    "cannon": ("cut_cannon-B2.png", (1536, 1024), 17, 70, 54, 30),
}
HAMMER, CANNON = "jayce_melee_idle1@0", "jayce_ranged_idle1@0"


def grid(form):
    _, (w, h), *_ = FORMS[form]
    return w // SQ, h // SQ


def place(form):
    cut, _, crown, sole, mid, cmid = FORMS[form]
    a = np.array(Image.open(os.path.join(SRC, "hd", cut)).convert("RGBA"))
    cols, rows = grid(form)
    can = np.zeros((rows, cols, 4), np.uint8)
    h, w = a.shape[:2]
    dy, dx = sole + 1 - h, mid - cmid
    can[dy:dy + h, dx:dx + w] = a
    return can


def big(form, can, bg=(255, 255, 255, 255)):
    _, size, crown, sole, mid, _ = FORMS[form]
    cols, rows = grid(form)
    img = Image.new("RGBA", size, bg)
    img.alpha_composite(Image.fromarray(can).resize((cols * SQ, rows * SQ), Image.NEAREST))
    d = ImageDraw.Draw(img)
    for c in range(0, cols + 1, 2):
        d.line([(c * SQ, 0), (c * SQ, rows * SQ)], fill=(200, 200, 212, 255), width=1)
    for r in range(0, rows + 1, 2):
        d.line([(0, r * SQ), (cols * SQ, r * SQ)], fill=(200, 200, 212, 255), width=1)
    for r in range(0, rows, 10):
        d.line([(0, r * SQ), (cols * SQ, r * SQ)], fill=(150, 150, 170, 255), width=1)
        d.text((2, r * SQ + 1), str(r), fill=(200, 0, 0, 255))
    for c in range(0, cols, 10):
        d.line([(c * SQ, 0), (c * SQ, rows * SQ)], fill=(150, 150, 170, 255), width=1)
        d.text((c * SQ + 2, 2), str(c), fill=(0, 0, 200, 255))
    d.line([(0, (sole + 1) * SQ), (cols * SQ, (sole + 1) * SQ)], fill=(230, 30, 30, 255), width=3)
    d.line([(0, crown * SQ), (cols * SQ, crown * SQ)], fill=(30, 170, 60, 255), width=3)
    d.line([((mid + 0.5) * SQ, 0), ((mid + 0.5) * SQ, rows * SQ)], fill=(40, 90, 230, 255), width=3)
    return img


def render():
    os.makedirs(WORK, exist_ok=True)
    pr = os.path.join(ROOT, "tools", "lol", "pose_ref.py")
    for yaw, frames, name in ((80, [HAMMER, CANNON], "side80"),
                              (90, [HAMMER, "jayce_melee_run1@0", CANNON, "jayce_ranged_run1@0"], "side90")):
        cmd = [sys.executable, pr, "--champ", "Jayce", "--hq", "--bg", "225,225,225", "--no-labels",
               "--size", "800", "--fit", "0.62", "--ground", "0.92", "--width", "1.2", "--yaw", str(yaw),
               "--name", name, "--out", WORK]
        for f in frames:
            cmd += ["--frame", f]
        subprocess.run(cmd, check=True, capture_output=True)
    a, b = Image.open(os.path.join(WORK, "side80.png")), Image.open(os.path.join(WORK, "side90.png"))
    img = Image.new("RGB", (max(a.width, b.width), a.height + b.height), GREY[:3])
    img.paste(a, (0, 0))
    img.paste(b, (0, a.height))
    img.save(os.path.join(WORK, "league_side.png"))


def style():
    names = ["galio_hd_idle_x8", "braum_lo_idle_x8", "zeri_lo_idle_x8", "nidalee_lo_idle_x8"]
    shots = [Image.open(os.path.join(ROOT, "assets", "source", "bard", "style_ref", f"{n}.png")).convert("RGBA")
             for n in names]
    shots = [s.resize((s.width // 2, s.height // 2), Image.NEAREST) for s in shots]
    pad = 24
    tall = max(s.height for s in shots)
    img = Image.new("RGBA", (sum(s.width + pad for s in shots) + pad, tall + 2 * pad), GREY)
    x = pad
    for s in shots:
        img.alpha_composite(s, (x, pad + tall - s.height))
        x += s.width + pad
    return img


def take(name):
    pic = Image.open(os.path.join(SRC, "codex_picture", f"jayce-{name}.png")).convert("RGBA")
    can = Image.new("RGBA", pic.size, GREY)
    can.alpha_composite(pic)
    return can.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    if not a.no_render:
        render()
    big("hammer", place("hammer")).convert("RGB").save(os.path.join(out, "1_hammer_grid.png"))
    big("cannon", place("cannon")).convert("RGB").save(os.path.join(out, "2_cannon_grid.png"))
    take("hammer-A2").save(os.path.join(out, "3_hammer_A2.png"))
    take("cannon-B2").save(os.path.join(out, "4_cannon_B2.png"))
    shutil.copyfile(os.path.join(WORK, "league_side.png"), os.path.join(out, "5_league_side.png"))
    style().convert("RGB").save(os.path.join(out, "6_style.png"))
    for i, form in ((7, "hammer"), (8, "cannon")):
        cols, rows = grid(form)
        big(form, np.zeros((rows, cols, 4), np.uint8)).convert("RGB").save(os.path.join(out, f"{i}_{form}_empty.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

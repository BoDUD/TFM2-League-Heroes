#!/usr/bin/env python3
"""Graves's run pack for Codex (assets/source/graves/RUN_PROMPT.md): his 8 run frames with the legs crossing.

    python tools/art/pack_graves_run.py [--out C:/t/gv_work/graves_run_pack]

The first review drew his move as league_braum's / league_nautilus's heavy walk (the design's legs lifted in turn under
him); the user, 2026-10-20: 「男枪应该是跑步吧？而且要确保跑步时腿部不变形 你利用工具好好做啊」. Legs built from the design's
parts read as deformed on every hero so far (memory run-legs-caitlyn-way), so Codex redraws the legs only, along a line
per leg - league_jayce's and league_milio's approved runs (tools/art/pack_jayce_run.py, pack_milio_run.py):
  now/graves_run_<n>.png    the side design's upper body (head, scarf, pauldron, arms, the shotgun - kept square for
                            square) with its legs taken away under the belt, bobbing a row as a foot lands
  guide/graves_run_<n>.png  the same with the legs to draw as lines: red = the near leg (in front, full tone), blue =
                            the far leg (a shade darker), hip - knee - ankle - toe, the ground line, the standing point
  ref/                      the side design (his legs: khaki trousers over dark grey, bunched over brown boots, khaki
                            knee pads), league_jayce's and league_caitlyn's runs (cross-step runs the user approved)
The near leg goes through 8 phases (planted ahead, under the body, the far leg swinging past it = the cross step,
pushing off behind, lifted, kicked up, swung through, reaching) and the far leg the same 4 frames on, so the legs swap
between frames 1-4 and 5-8 and cross in frames 3 and 7. The grid of the step-1 redraw and the poses: 16 px a design
square on a 1254 canvas, the soles on y 1168. The bones are the design's own (measured on hd/side.png): hips under the
belt, thigh THIGH and shin SHIN squares, the boot FOOT.
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
import rigkit as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "graves")
DOC = os.path.join(SRC, "RUN_PROMPT.md")
PX, CANVAS = 16, 1254
DX, DY = 2, 16                   # the side design's (0, 0) on the canvas grid: its soles on row 72 (y 1168)
SOLE = 56 + DY                   # the soles' row on the canvas grid
PIV = 33 + DX                    # the standing point's column (rig_graves.STAND)
RED, BLUE = (255, 40, 40), (40, 110, 255)
CUT = 42                         # design rows from here down are the legs (rig_graves.LEG_BAND + 1)
# the legs' bones in design squares (hd/side.png: the belt's lowest row 41, the knee pads' middle row 47, the boots'
# tops row 52, the soles row 56): hips under the belt, the near (front) hip image right, the far (back) one image left
HIP_Y = 41.5
NEAR_HIP, FAR_HIP = 38.0, 29.0
THIGH, SHIN = 7.0, 7.0
FOOT = (6, 3)                    # the toe from the ankle: forward, down (the boot)
ANKLE_UP = 4                     # the ankle over the ground with the boot flat
# the near leg's 8 phases from its hip: the ankle's x (forward +) and its height over the ground (rows); the far leg
# four on (league_jayce's PHASES brought to his 14-square legs: x 0.42, the lift x 0.45 over the flat ankle's 4)
PHASES = [(6.0, 4), (2.5, 4), (-1.0, 4), (-5.0, 5), (-7.0, 7), (-5.0, 10), (1.0, 9), (5.5, 6)]
BOB = [0, 1, 1, 0, 0, 1, 1, 0]   # the upper body a row down as a foot takes his weight (frames 2-3, 6-7)
TAG = "run"


def upper():
    """The side design without its legs (rows from CUT down)."""
    d = np.asarray(Image.open(os.path.join(SRC, "hd", "side.png")).convert("RGBA")).copy()
    d[CUT:] = 0
    return d


def big(a, dy=0, bg=None):
    can = Image.new("RGBA", (CANVAS, CANVAS), bg or (0, 0, 0, 0))
    im = Image.fromarray(a).resize((a.shape[1] * PX, a.shape[0] * PX), Image.NEAREST)
    can.alpha_composite(im, (DX * PX, (DY + dy) * PX))
    return can


def leg_points(hip, k):
    hx, hy = hip
    ax, ah = PHASES[k]
    ankle = (hx + ax, SOLE + 1 - ah)
    knee, ankle = K.elbow((hx, hy), ankle, THIGH, SHIN, bend=1)
    if not forward(knee, (hx, hy), ankle):            # knees point forward (image right) of the hip-ankle line
        knee, ankle = K.elbow((hx, hy), ankle, THIGH, SHIN, bend=-1)
    toe = (ankle[0] + FOOT[0], ankle[1] + FOOT[1])
    if ah > ANKLE_UP:                                 # a lifted foot hangs: the toe down and back a little
        toe = (ankle[0] + FOOT[0] * 0.7, ankle[1] + FOOT[1] * 1.6)
    return [(hx, hy), knee, ankle, toe]


def forward(knee, hip, ankle):
    """The knee on the forward side of the hip -> ankle line (a leg bends back at the knee; a leg kicked up behind has
    its thigh down and its shin back, never its thigh lying back level)."""
    vx, vy = ankle[0] - hip[0], ankle[1] - hip[1]
    nx, ny = vy, -vx                                   # the line turned a quarter: for a leg pointing down, image right
    if nx < 0 or (nx == 0 and ny > 0):
        nx, ny = -nx, -ny
    return (knee[0] - hip[0]) * nx + (knee[1] - hip[1]) * ny >= 0


def draw_guide(img, legs):
    d = ImageDraw.Draw(img)
    gy = (SOLE + 1) * PX
    d.line([(0, gy), (CANVAS, gy)], fill=RED, width=3)
    px = (PIV + 0.5) * PX
    d.line([(px - 14, gy - 14), (px + 14, gy + 14)], fill=BLUE, width=3)
    d.line([(px - 14, gy + 14), (px + 14, gy - 14)], fill=BLUE, width=3)
    for pts, col in legs:
        P = [((x + 0.5) * PX, (y + 0.5) * PX) for x, y in pts]
        d.line(P, fill=col, width=8, joint="curve")
        for x, y in P[:3]:
            d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=col, width=4)
        x, y = P[-1]
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=col)
    return img


def sheet_run(hero, z, tag="hd_run"):
    """A hero's run frames from its sheet, side by side at z (each frame's own box on one row)."""
    stem = os.path.join(ROOT, "league", "champions", f"league_{hero}")
    anims = json.load(open(stem + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    sh = Image.open(stem + "#sheet.png").convert("RGBA")
    fs = []
    for f in anims[tag]["frames"]:
        r = f["data"]
        fs.append(sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"]))))
    w = max(f.width for f in fs)
    h = max(f.height for f in fs)
    strip = Image.new("RGBA", (len(fs) * (w + 2) * z, h * z), (255, 255, 255, 255))
    for i, f in enumerate(fs):
        strip.alpha_composite(f.resize((f.width * z, f.height * z), Image.NEAREST), (i * (w + 2) * z, (h - f.height) * z))
    return strip


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="C:/t/gv_work/graves_run_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    for sub in ("now", "guide", "ref"):
        os.makedirs(os.path.join(out, sub))
    up = upper()
    plan = {}
    for k in range(8):
        dy = BOB[k]
        name = f"graves_{TAG}_{k + 1}.png"
        big(up, dy).save(os.path.join(out, "now", name))
        hy = DY + dy + HIP_Y
        legs = [(leg_points((DX + FAR_HIP, hy), (k + 4) % 8), BLUE), (leg_points((DX + NEAR_HIP, hy), k), RED)]
        g = big(up, dy, (255, 255, 255, 255))
        draw_guide(g, legs).convert("RGB").save(os.path.join(out, "guide", name))
        plan[name] = {"bob": dy, "legs": {"far": [[round(x, 1), round(y, 1)] for x, y in legs[0][0]],
                                          "near": [[round(x, 1), round(y, 1)] for x, y in legs[1][0]]}}
    side = np.asarray(Image.open(os.path.join(SRC, "hd", "side.png")).convert("RGBA"))
    big(side, 0, (255, 255, 255, 255)).convert("RGB").save(os.path.join(out, "ref", "graves_side_design.png"))
    sheet_run("jayce", 6).save(os.path.join(out, "ref", "jayce_run_reference.png"))
    sheet_run("caitlyn", 6, "run").save(os.path.join(out, "ref", "caitlyn_run_reference.png"))
    with open(os.path.join(out, "legs.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(plan, fh, indent=1)
    shutil.copy(DOC, os.path.join(out, "RUN_PROMPT.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{zp}: now/ guide/ x8, ref/ 3")


if __name__ == "__main__":
    main()

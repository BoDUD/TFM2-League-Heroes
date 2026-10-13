#!/usr/bin/env python3
"""Galio's run redo pack for Codex (assets/source/galio/RUN_PROMPT.md): the 8 run frames with the legs alternating.

    python tools/art/pack_galio_run.py [--out dist/galio_packs/galio_run_pack]

Codex's step-2 run (assets/source/galio/codex_strips/galio_run_*) kept the light leg forward and the dark one back in all
8 frames (the user: 「走路没有交叉步」); legs built from the idle's standing legs read as deformed three times over (bone
lines, pasted parts, row shear, whole legs slid: 「腿部变形？」「还是变形啊」「不还是变形？」「看不到这里变形吗」). So
Codex redraws the legs only, in a running pose, alternating:
  now/galio_run_<n>.png    the current frame with its legs taken away (upper body, fists, wings, tail: keep them)
  guide/galio_run_<n>.png  the same with the legs to draw as lines: red = the light near leg, blue = the dark far leg
                           (hip - knee - hock - toe, a dot on the toe), the ground row, the standing point
  ref/                     Codex's own near leg from its run (the leg to draw, both legs), the design, Alistar's run
                           (league_alistar: the approved beast-leg run in the pack, legs alternating)
Writes <out>/ and <out>.zip.
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_galio as R  # noqa: E402
import rigkit as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "galio")
DOC = os.path.join(SRC, "RUN_PROMPT.md")
PX = 7                           # pixels a square, the step-2 pack's grid (219 x 146 squares in 1536 x 1024)
NEAR_HIP = (-4.5, -3.0)          # game px from the pivot (rig_galio.py's run): the near hip, the far one 7 right, a row up
FAR_HIP = (2.5, -3.5)
THIGH, SHIN = 11.0, 11.0         # squares, hip - knee - hock (the hock is the beast leg's back-bent joint)
# the near leg's 8 phases in squares from its hip: the toe's x, the toe's lift off the ground, the hock from the toe.
# planted ahead and sliding back (1-4), pushing off (5), lifted behind (6), swung through (7), reaching (8); the far
# leg four phases on
PLANT, PUSH, LIFT, TUCK = (-6, -9), (-3, -10), (-2, -8), (-5, -7)
PHASES = [(11, 0, PLANT), (6, 0, PLANT), (1, 0, PLANT), (-4, 0, PLANT),
          (-9, 1, PUSH), (-9, 7, LIFT), (1, 6, TUCK), (9, 3, PLANT)]
RED, BLUE = (255, 40, 40), (40, 110, 255)


def can_xy(x, y):
    """Game px from the pivot -> canvas squares (rig_galio.to_can)."""
    return R.to_can(x, y)


def leg_points(hip_gp, k):
    hx, hy = can_xy(*hip_gp)
    toe_dx, lift, (hdx, hdy) = PHASES[k]
    toe = (hx + toe_dx, R.SOLE + 0.5 - lift + (hy - can_xy(*NEAR_HIP)[1]))
    hock = (toe[0] + hdx, toe[1] + hdy)
    knee, hock = K.elbow((hx, hy), hock, THIGH, SHIN, bend=-1)
    if knee[0] < min(hx, hock[0]):
        knee, hock = K.elbow((hx, hy), hock, THIGH, SHIN, bend=1)
    return [(hx, hy), knee, hock, toe]


def upper_only(can):
    """The run canvas without its legs (rig_galio.run_legs's cut: the fists and the tail kept)."""
    H, W = can.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    x0, y0 = R.to_can(0, 0)
    rx, ry = np.floor((xx + 0.5 - x0) / R.PPU), np.floor((yy + 0.5 - y0) / R.PPU)
    fx, fy, bx, by = R.RUN_KEEP
    keep = (rx >= fx) & (ry <= fy) | (rx <= bx) & (ry <= by) | (rx < R.RUN_TAILX)
    out = can.copy()
    out[(ry >= R.RUN_CUT) & ~keep] = 0
    return out


def big(a, bg=None):
    im = Image.fromarray(a).resize((a.shape[1] * PX, a.shape[0] * PX), Image.NEAREST)
    canvas = Image.new("RGBA", (1536, 1024), bg or (0, 0, 0, 0))
    canvas.alpha_composite(im, (0, 0))
    return canvas


def draw_guide(img, legs):
    d = ImageDraw.Draw(img)
    gy = (R.SOLE + 1) * PX
    d.line([(0, gy), (1536, gy)], fill=RED, width=2)
    px = (R.PIV_X + 0.5) * PX
    d.line([(px - 12, gy - 12), (px + 12, gy + 12)], fill=BLUE, width=2)
    d.line([(px - 12, gy + 12), (px + 12, gy - 12)], fill=BLUE, width=2)
    for pts, col in legs:
        P = [(x * PX, y * PX) for x, y in pts]
        d.line(P, fill=col, width=5, joint="curve")
        for x, y in P:
            d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=col, width=3)
        x, y = P[-1]
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "galio_packs", "galio_run_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    for sub in ("now", "guide", "ref"):
        os.makedirs(os.path.join(out, sub))
    table, pal = R.lut()
    cells = json.load(open(os.path.join(R.CODEX, "cells.json"), encoding="utf-8"))
    runs = sorted([f for f in cells["frames"] if f["tag"] == "run"], key=lambda f: f["index"])
    for k, f in enumerate(runs):
        can = R.frame("run", f["index"] + 1, table, pal)
        up = upper_only(can)
        big(up).save(os.path.join(out, "now", f"galio_run_{k + 1}.png"))
        legs = [(leg_points(FAR_HIP, (k + 4) % 8), BLUE), (leg_points(NEAR_HIP, k), RED)]
        g = big(up, (255, 255, 255, 255))
        draw_guide(g, legs).convert("RGB").save(os.path.join(out, "guide", f"galio_run_{k + 1}.png"))
    # the leg to draw: Codex's own near leg in its run frame 1 (the light leg, planted ahead), boxed on the whole frame
    can = R.frame("run", runs[0]["index"] + 1, table, pal)
    ref = big(can, (255, 255, 255, 255))
    x0, y0 = R.to_can(0, 0)
    box = [(x0 + R.PPU * -3) * PX, (y0 + R.PPU * -7) * PX, (x0 + R.PPU * 14) * PX, (R.SOLE + 2) * PX]
    ImageDraw.Draw(ref).rectangle(box, outline=RED, width=4)
    ref.crop((int(box[0]) - 280, int(box[1]) - 420, int(box[2]) + 140, int(box[3]) + 14)).convert("RGB").save(
        os.path.join(out, "ref", "galio_leg_from_codex_run.png"))
    d = R.design()
    Image.fromarray(d).resize((d.shape[1] * PX, d.shape[0] * PX), Image.NEAREST).save(
        os.path.join(out, "ref", "galio_design.png"))
    # Alistar's run (1x frames, 6x), the approved beast-leg run: legs alternating, hooves stepping
    sys.path.insert(0, HERE)
    from preview_garen import frames_of, load
    sp = load(os.path.join(ROOT, "league", "champions", "league_alistar"))
    fs = [f for f, _ in frames_of(sp, "run")]
    bb = None
    for f in fs:
        b = f.getbbox()
        bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    fs = [f.crop(bb) for f in fs]
    w, h = fs[0].size
    strip = Image.new("RGBA", (len(fs) * (w + 2) * 6, h * 6), (255, 255, 255, 255))
    for i, f in enumerate(fs):
        strip.alpha_composite(f.resize((w * 6, h * 6), Image.NEAREST), (i * (w + 2) * 6, 0))
    strip.save(os.path.join(out, "ref", "alistar_run_reference.png"))
    shutil.copy(DOC, os.path.join(out, "RUN_PROMPT.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{zp}: now/ guide/ x{len(runs)}, ref/ 3")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Elise's run redo pack for Codex (assets/source/elise/RUN_PROMPT.md): the huntress's 8 run frames with the legs
crossing, the legs only drawn by Codex (league_jayce's way, tools/art/pack_jayce_run.py).

    python tools/art/pack_elise_run.py [--out %TEMP%/el_work/elise_run_pack]   (the zip is copied to dist/elise_packs)

Codex's step-2 run kept the same leg in front in all 8 frames (the user: 「交叉步都没 腿不换步的？」); my rebuild from the
design's legs sheared her diagonal A-stance legs straight (「腿变形你问我可以吗？」), and legs built from a design's parts
read as deformed on every hero so far - so Codex redraws the legs only, along a line per leg (the user's pick A):
  now/elise_run_<n>.png    the design's upper body (the idle's, memory run-crossing-root-causes: the upper body = the
                           idle) without its two legs (tools/art/run_elise.py's masks: below HIP, the back legs' claws
                           kept), sunk SINK rows over the legs like a bob, on step 2's grid (7 px a design square, the
                           design at (52, 15), the soles on row SOLE)
  guide/elise_run_<n>.png  the same with the legs to draw as lines: red = the near leg (in front, full tone), blue = the
                           far leg (a shade darker), hip - knee - ankle - toe, the ground row, the standing point
  ref/                     the design (her legs: black-purple thigh-high boots with red stripes, pointed high heels),
                           its legs at 10x, league_caitlyn's approved cross-step run at 6x, the step-2 run (step2/)
The near leg goes through 8 phases (planted ahead, under the body, passing, pushing off behind, kicked up, swung
through, reaching), the far leg the same 4 frames on, so the legs swap between frames 1-4 and 5-8 and cross in
frames 3 and 7 (league_jayce's PHASES scaled to her legs).
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
import import_elise_strips as I  # noqa: E402
import rigkit as K  # noqa: E402
import run_elise as RE  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "elise")
DOC = os.path.join(SRC, "RUN_PROMPT.md")
PX = 7
SOLE = I.SOLE
PIV_X = I.FORMS["human"]["piv"]
RED, BLUE = (255, 40, 40), (40, 110, 255)
X0, Y0 = I.FORMS["human"]["at"]
HIPS = (42, 56)                  # design columns of the near / far hip (row RE.HIP)
THIGH, SHIN = 17.0, 17.0         # design squares (hip row 84 to the knee about row 100, to the ankle about row 114)
FOOT = (5, 7)                    # the toe from the ankle: forward, down (the pointed high-heeled boot)
ANKLE_UP = 8                     # the ankle over the ground with the boot planted (the heel lifts it)
SINK = RE.SINK
# the near leg's 8 phases from its hip: the ankle's x (forward +) and its height over the ground; the far leg four on
# (league_jayce's x 0.87 for her shorter legs, the heights + 3 for the heels)
PHASES = [(12, 8), (5, 8), (-2, 8), (-10, 10), (-14, 14), (-9, 22), (3, 18), (11, 12)]


def upper(k):
    """The design without its legs on the step-2 canvas, sunk SINK[k] rows."""
    d = I.design("human")
    near, far, body = RE.masks(d)
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    ys, xs = np.nonzero(body)
    can[ys + Y0 + SINK[k], xs + X0] = d[ys, xs]
    return can


def big(a, bg=None):
    im = Image.fromarray(a).resize((a.shape[1] * PX, a.shape[0] * PX), Image.NEAREST)
    canvas = Image.new("RGBA", (1536, 1024), bg or (0, 0, 0, 0))
    canvas.alpha_composite(im, (0, 0))
    return canvas


def leg_points(hip, k):
    hx, hy = hip
    ax, ah = PHASES[k]
    ankle = (hx + ax, SOLE + 1 - ah)
    # the knee always points forward (image right): of the two solutions the one further right (a back-bent knee in
    # frame 5 of the first pack)
    sols = [K.elbow((hx, hy), ankle, THIGH, SHIN, bend=b) for b in (1, -1)]
    knee, ankle = max(sols, key=lambda kv: kv[0][0])
    toe = (ankle[0] + FOOT[0], ankle[1] + FOOT[1])
    if ah > ANKLE_UP:                                 # a lifted foot hangs: the toe down and back a little
        toe = (ankle[0] + FOOT[0] * 0.7, ankle[1] + FOOT[1] * 1.2)
    return [(hx, hy), knee, ankle, toe]


def draw_guide(img, legs):
    d = ImageDraw.Draw(img)
    gy = (SOLE + 1) * PX
    d.line([(0, gy), (1536, gy)], fill=RED, width=2)
    px = (PIV_X + 0.5) * PX
    d.line([(px - 12, gy - 12), (px + 12, gy + 12)], fill=BLUE, width=2)
    d.line([(px - 12, gy + 12), (px + 12, gy - 12)], fill=BLUE, width=2)
    for pts, col in legs:
        P = [((x + 0.5) * PX, (y + 0.5) * PX) for x, y in pts]
        d.line(P, fill=col, width=6, joint="curve")
        for x, y in P[:3]:
            d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=col, width=3)
        x, y = P[-1]
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=col)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(os.environ["LOCALAPPDATA"], "Temp", "el_work", "elise_run_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    for sub in ("now", "guide", "ref", "step2"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    plan = {}
    for k in range(8):
        up = upper(k)
        name = f"elise_run_{k + 1}.png"
        big(up).save(os.path.join(out, "now", name))
        hy = Y0 + RE.HIP + SINK[k]
        legs = [(leg_points((X0 + HIPS[1], hy), (k + 4) % 8), BLUE), (leg_points((X0 + HIPS[0], hy), k), RED)]
        g = big(up, (255, 255, 255, 255))
        draw_guide(g, legs).convert("RGB").save(os.path.join(out, "guide", name))
        step2 = I.rgba(os.path.join(I.CODEX, f"elise_run_{k + 1}_1x.png"))
        big(step2, (255, 255, 255, 255)).convert("RGB").save(os.path.join(out, "step2", name))
        plan[name] = {"sink": SINK[k], "legs": {"far": [[round(x, 1), round(y, 1)] for x, y in legs[0][0]],
                                                "near": [[round(x, 1), round(y, 1)] for x, y in legs[1][0]]}}
    d = I.design("human")
    Image.fromarray(d).resize((d.shape[1] * PX, d.shape[0] * PX), Image.NEAREST).save(
        os.path.join(out, "ref", "elise_human_design.png"))
    legs = d[RE.HIP - 6:, :]
    Image.fromarray(legs).resize((legs.shape[1] * 10, legs.shape[0] * 10), Image.NEAREST).save(
        os.path.join(out, "ref", "elise_legs_design.png"))
    from preview_garen import frames_of, load
    sp = load(os.path.join(ROOT, "league", "champions", "league_caitlyn"))
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
    strip.save(os.path.join(out, "ref", "caitlyn_run_reference.png"))
    with open(os.path.join(out, "legs.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(plan, fh, indent=1)
    shutil.copy(I.lp(DOC), os.path.join(out, "RUN_PROMPT.md"))
    zp = shutil.make_archive(out, "zip", out)
    dst = os.path.join(ROOT, "dist", "elise_packs", "elise_run_pack.zip")
    shutil.copy(zp, I.lp(dst))
    print(f"{dst}: now/ guide/ step2/ x8, ref/ 3")


if __name__ == "__main__":
    main()

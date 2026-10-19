#!/usr/bin/env python3
"""LeBlanc's run legs pack (assets/source/leblanc/LEG_PROMPTS.md): Codex draws her legs and the gown below the waist
along a skeleton per frame for the eight-frame run, every leg segment as long as the design's own.

    python tools/art/pack_leblanc_legs.py [--out C:/t/lb_legs] [--lol D:/WeGameApps/lol]

The user, 2026-10-19, on the PPU actions (tools/art/rig_leblanc_hd.py): 「走路腿部不动的？」 - the rig only moves the
whole figure with League's pelvis: her legs are under the gown. The route the user accepts for dense designs (memory
run-legs-caitlyn-way, codex-legs-need-skeletons; tools/art/pack_quinn_legs2.py): Codex redraws only the legs, per frame,
along red / blue skeleton lines (hip - knee - ankle - toe) whose thigh and shin are the design's own lengths, and here
the gown below the waist, parted by the stride; everything above the waist, the staff arm and the cape hanging at her
back (left of CAPE_X) stay the design's squares. The staff is left out (the rig holds it level behind her in the run).
Round 2 (--prompts LEG_PROMPTS_2.md): round 1 came back with sheer brown stockings and brown heels, long and thin -
not her standing legs (「腿有点变形啊 待机的腿和走路的腿不一样？」; round 1's prompt itself said "stockings"): the
legs drawn as the idle's, bare pale thighs with the strap and navy gold-trimmed knee boots, the gown slit only in front.
Writes <out>/ (and <out>.zip): the prompts; 1_run_body.png / 1_run_guide.png (eight cells: the body with the gown's
lower part and the legs taken away, and the same with the skeletons), 2_lower_sample.png (the design's gown and legs
below the waist, 8x: the drawing to repeat), 3_run_lol.png (League's run, Riot's model, kept local).
"""
import argparse
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_leblanc_hd as L  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "leblanc")
PX = 6                            # pixels a square on the sheets
CW, CH = 70, 96                   # a cell in squares
STAND = (30, 92)                  # the cell square the design's standing point (column 21.5) and ground (row 86) go on
STAND_COL, GROUND = 21, 86
HIP_ROW = 56                      # the gold belt's lowest row: the gown and the legs below it are drawn by Codex
CAPE_X = 9                        # left of it the cape hanging at her back stays
# the design's legs (8x ruler on hd/design.png): near (image left: the thigh in the gown's slit, the boot at the hem)
# hip (19, 57), knee (19, 69), ankle (14.5, 79); far (image right, the dark stocking with its gold edge) hip (25, 57),
# knee (25.5, 69), ankle (26, 80)
THIGH, SHIN, FOOT = 12.0, 11.0, 3.0
NEAR_HIP, FAR_HIP = (19.0, 57.0), (25.0, 57.0)
ANKLE_Y = 81.5                    # an ankle on the ground (the sole four rows under it)
RED, BLUE = (255, 40, 40), (40, 110, 255)
KEY = (0, 255, 0)
# the run: league_quinn's scissor stride at her leg length (x 1.84): the near leg's ankle from its hip (ahead +), its
# lift, 8 phases; the far leg four phases on; the body down two rows as a foot lands
RUN = [(10.0, 0), (5.5, 0), (0.0, 0), (-5.5, 0), (-10.0, 3.0), (-6.5, 7.0), (1.0, 8.0), (8.0, 3.5)]
RUN_BOB = [2, 0, 0, 0, 2, 0, 0, 0]


def run_leg(hip, ax, lift):
    Lg = THIGH + SHIN
    if lift == 0:
        dy = math.sqrt(max(0.0, Lg * Lg - ax * ax))
        knee = (hip[0] + ax * THIGH / Lg, hip[1] + dy * THIGH / Lg)
        ankle = (hip[0] + ax, hip[1] + dy)
    else:   # a lifted leg bends at the knee: the knee forward of the hip-ankle line
        ay = ANKLE_Y - lift
        d = min(math.hypot(ax, ay - hip[1]), Lg - 0.01)
        mid = (hip[0] + ax / 2, (hip[1] + ay) / 2)
        h = math.sqrt(max(0.0, THIGH * THIGH - (d / 2) ** 2))
        ux, uy = ax / d, (ay - hip[1]) / d
        knee = (mid[0] + uy * h, mid[1] - ux * h)
        if knee[0] < mid[0]:
            knee = (mid[0] - uy * h, mid[1] + ux * h)
        ankle = (hip[0] + ax, ay)
    return [hip, knee, ankle, (ankle[0] + FOOT, ankle[1] + 1.5)]


def run_frames():
    out = []
    for k in range(8):
        bob = RUN_BOB[k]
        nax, nl = RUN[k]
        fax, fl = RUN[(k + 4) % 8]
        nh = (NEAR_HIP[0], NEAR_HIP[1] + bob)
        fh = (FAR_HIP[0], FAR_HIP[1] + bob)
        out.append((bob, run_leg(nh, nax, nl), run_leg(fh, fax, fl)))
    return out


def rest_body():
    """The design without its staff (the rig's upper body and staff arm at rest; the body the staff hid filled in)."""
    rig = L.make_rig(L.design())
    can = R.compose(rig, [("upper", dict()), ("arm", dict(angle=0, about=L.SHOULDER))])
    D = rig.D
    return can[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W].copy()


def body(d):
    b = d.copy()
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    b[(yy > HIP_ROW) & (xx >= CAPE_X)] = 0
    return b


def cell(b, drop, legs=None):
    img = Image.new("RGBA", (CW * PX, CH * PX), KEY + (255,))
    ox, oy = STAND[0] - STAND_COL, STAND[1] - GROUND
    lay = np.zeros((CH, CW, 4), np.uint8)
    y0 = oy + int(round(drop))
    h = min(b.shape[0], CH - y0)
    lay[y0:y0 + h, ox:ox + b.shape[1]] = b[:h]
    img.alpha_composite(Image.fromarray(np.repeat(np.repeat(lay, PX, 0), PX, 1)))
    dr = ImageDraw.Draw(img)
    dr.line([(0, STAND[1] * PX), (CW * PX, STAND[1] * PX)], fill=(0, 150, 0, 255), width=1)
    if legs:
        for pts, c in ((legs[1], BLUE), (legs[0], RED)):
            q = [((x + ox + 0.5) * PX, (y + oy + 0.5) * PX) for x, y in pts]
            dr.line(q, fill=c + (255,), width=4)
            for x, y in q[:3]:
                dr.ellipse([x - 5, y - 5, x + 5, y + 5], fill=c + (255,))
    return img


def sheet(cells, cols):
    rows = (len(cells) + cols - 1) // cols
    out = Image.new("RGB", (cols * CW * PX, rows * CH * PX), KEY)
    for i, c in enumerate(cells):
        out.paste(c.convert("RGB"), ((i % cols) * CW * PX, (i // cols) * CH * PX))
    dr = ImageDraw.Draw(out)
    for i in range(1, cols):
        dr.line([(i * CW * PX, 0), (i * CW * PX, out.height)], fill=(0, 120, 0), width=2)
    for j in range(1, rows):
        dr.line([(0, j * CH * PX), (out.width, j * CH * PX)], fill=(0, 120, 0), width=2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/lb_legs")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--prompts", default="LEG_PROMPTS.md", help="LEG_PROMPTS_2.md: round 2, the legs as the idle's")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    d = rest_body()
    b = body(d)
    Rf = run_frames()
    sheet([cell(b, bob) for bob, _, _ in Rf], 4).save(os.path.join(out, "1_run_body.png"))
    sheet([cell(b, bob, (n, f)) for bob, n, f in Rf], 4).save(os.path.join(out, "1_run_guide.png"))
    full = np.asarray(Image.open(R.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA"))
    low = full[HIP_ROW + 1:, CAPE_X:36]
    smp = Image.new("RGBA", (low.shape[1] * 8, low.shape[0] * 8), (225, 225, 225, 255))
    smp.alpha_composite(Image.fromarray(np.repeat(np.repeat(low, 8, 0), 8, 1)))
    smp.convert("RGB").save(os.path.join(out, "2_lower_sample.png"))
    work = out + "_work"
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", a.lol, "--champ", "Leblanc",
           "--anim", "Run1", "--frames", "8", "--t1", "1.1", "--head", "2.3", "--legs", "0.8",
           "--submesh-texture", "Weapon=Weapon_TX", "--yaw", "60", "--pitch", "15", "--size", "400", "--no-labels",
           "--out", work]
    subprocess.run(cmd, check=True, capture_output=True)
    png = [f for f in os.listdir(work) if f.lower().endswith(".png")][0]
    shutil.copyfile(os.path.join(work, png), os.path.join(out, "3_run_lol.png"))
    shutil.copyfile(R.lp(os.path.join(SRC, a.prompts)), os.path.join(out, a.prompts))
    print(shutil.make_archive(out, "zip", out))
    for k, (bob, n, f) in enumerate(Rf):
        print(k, "bob", bob, "near", [tuple(round(v, 1) for v in p) for p in n], "far", [tuple(round(v, 1) for v in p) for p in f])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Jarvan IV's run legs pack for Codex (assets/source/jarvaniv/RUN_LEGS.md): only the legs of the 8 run frames drawn on
League's run, everything above the skirt's hem kept as my rig poses it (league_pantheon's run redo, the way the user
took for him: tools/art/pack_pantheon_run.py).

    python tools/lol/pose_joints.py assets/source/jarvaniv/poses.json --tag run \
        --joints L_Thigh,L_Knee,L_Foot,L_Toe,R_Thigh,R_Knee,R_Foot,R_Toe --json %TEMP%/jv_work/run_joints.json
    python tools/art/pack_jarvaniv_run.py [--out %TEMP%/jv_work/jarvaniv_run_pack]

Why Codex: re-posing the design's legs losslessly cannot make a walk - only whole moves and quarter turns are allowed,
so the legs stay straight and vertical. Five walks built that way were turned down on 2026-10-17 (legs sliding apart,
one leg laid over the other, stepping in place, legs parting, knee guards shrinking behind the hem: 「这两个都不对 也不
自然」「膝盖那里怎么会缩进去啊」「感觉还是变形啊 这个问题其他英雄肯定碰到过啊 你看他们怎么解决的」) - and every merged
humanoid in a skirt or tabard walks on drawn legs (league_pantheon: Codex legs on League's joints; league_swain and
league_renata: Codex skin swaps).
The pack: now/ (my run frames: the upper body, arms and the lance carried on the shoulder as League carries it, the
body's bob, the skirt; the legs as the rig had them), guide/ (each frame with everything under the skirt's hem faded and
League's leg skeleton drawn over it: near leg red, far leg blue, from tools/lol/pose_joints.py, scaled LEG to the
design's legs), design/ (the design 10x + 1x), refs/ (League's run as a contact sheet), legs.json (the feet per frame).
Every frame is drawn PX px a square on a CW square canvas, the design's squares on the same grid.
"""
import argparse
import json
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
import rig_jarvaniv as J  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jarvaniv")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "jv_work")
PX = 12                         # pixels a square on the canvas
CW = 1536
DENS = 1.5                      # squares a game pixel (PPU)
LEG = 0.95                      # League's legs (run joints at a 40-px body) to the design's
HEM = 53                        # the skirt's bottom edge row in the design (the legs start under it)
NEAR, FAR = (230, 30, 30, 255), (30, 90, 240, 255)
JOINTS = ("Thigh", "Knee", "Foot", "Toe")


def lp(path):
    return R.lp(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "jarvaniv_run_pack"))
    ap.add_argument("--joints", default=os.path.join(TMP, "run_joints.json"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub))
    F = J.form()
    r = F.rig
    D = F.D
    Image.fromarray(np.repeat(np.repeat(D.d, 10, 0), 10, 1)).save(os.path.join(out, "design", "jarvaniv_design.png"))
    Image.fromarray(D.d).save(os.path.join(out, "design", "jarvaniv_design_1x.png"))
    js = json.load(open(a.joints, encoding="utf-8"))
    frames = J.walk(F)
    # the canvas window: the frame's squares with the soles' row 12 squares above the bottom edge, the pivot centred
    cells = CW // PX
    sole_row = cells - 12                       # the canvas square row the soles stand on
    ox = cells // 2 - r.CX                      # canvas square = rig square + (ox, oy)
    oy = sole_row - (r.GY - 1)
    table = []
    for k, can in enumerate(frames):
        name = f"jarvaniv_run_{k + 1}"
        f = r.finish(can)
        sq = np.zeros((cells, cells, 4), np.uint8)
        ys, xs = np.nonzero(f[..., 3] > 0)
        sq[ys + oy, xs + ox] = f[ys, xs]
        big = Image.fromarray(np.repeat(np.repeat(sq, PX, 0), PX, 1))
        big.save(os.path.join(out, "now", name + ".png"))
        bob = J.WALK_STEP["bob"][k]
        hem = r.oy + HEM + oy                  # the hem's canvas row (the skirt does not bob)
        j = js[k]["joints"] if isinstance(js[k], dict) and "joints" in js[k] else js[k]
        hip_x = (j["L_Thigh"][0] + j["R_Thigh"][0]) / 2.0
        pivot_x = r.CX + ox
        pts = {}
        for side in ("L", "R"):
            for part in JOINTS:
                x, y = j[f"{side}_{part}"][0], j[f"{side}_{part}"][1]
                X = pivot_x + 0.5 + (x - hip_x) * DENS * LEG + 1.5          # the hips under the skirt's middle
                Y = (sole_row + 1) - (11 - y) * DENS * LEG
                pts[(side, part)] = (X, Y)
        g = Image.new("RGBA", (CW, CW), (255, 255, 255, 255))
        g.alpha_composite(big)
        fade = Image.new("RGBA", (CW, CW), (0, 0, 0, 0))
        ImageDraw.Draw(fade).rectangle([0, (hem + 1) * PX, CW, CW], fill=(255, 255, 255, 200))
        g.alpha_composite(fade)
        dr = ImageDraw.Draw(g)
        for side, col in (("R", FAR), ("L", NEAR)):
            xy = [(pts[(side, p)][0] * PX, pts[(side, p)][1] * PX) for p in JOINTS]
            dr.line(xy, fill=col, width=8)
            for x, y in xy:
                dr.ellipse([x - 10, y - 10, x + 10, y + 10], fill=col)
        dr.line([(0, (sole_row + 1) * PX), (CW, (sole_row + 1) * PX)], fill=(255, 0, 0, 255), width=3)
        dr.line([(0, (hem + 1) * PX), (CW, (hem + 1) * PX)], fill=(0, 170, 0, 255), width=2)
        dr.text((20, 20), f"run {k + 1}: red = NEAR leg, blue = FAR leg; green line = the skirt's hem (keep everything "
                          f"above it), red line = ground", fill=(0, 0, 0, 255))
        g.convert("RGB").save(os.path.join(out, "guide", name + ".png"))
        table.append({"frame": k + 1, "bob": int(bob), "hem_row": int(hem), "sole_row": int(sole_row),
                      "near_foot": [round(v, 1) for v in pts[("L", "Foot")]],
                      "far_foot": [round(v, 1) for v in pts[("R", "Foot")]]})
    # League's run as a contact sheet (Riot's model: local only, never committed)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", a.lol, "--champ",
                    "JarvanIV", "--anim", "jarvanIV_run", "--frames", "8", "--size", "300", "--width", "1.4",
                    "--out", os.path.join(out, "refs")], check=True, capture_output=True)
    with open(os.path.join(out, "legs.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    shutil.copyfile(lp(os.path.join(SRC, "RUN_LEGS.md")), os.path.join(out, "RUN_LEGS.md"))
    zp = shutil.make_archive(out, "zip", out)
    for t in table:
        print(t)
    print(zp)


if __name__ == "__main__":
    main()

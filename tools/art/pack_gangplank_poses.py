#!/usr/bin/env python3
"""Gangplank's gun-hand pose pack for Codex (assets/source/gangplank/POSE_PROMPTS.md): the approved design with only the
near arm and the hand cannon drawn again, in League's Q (Parrrley: the arm out, the cannon aimed forward at the chest)
and R (Cannon Barrage: the arm straight up, the cannon to the sky).

    python tools/art/pack_gangplank_poses.py [--out %TEMP%/gp_work/gangplank_pose_pack]

Why (2026-10-18): the design holds the cannon on the near shoulder, the hand at the face; no arm in it reaches forward
or up. Five rounds of posing that arm from the design's own squares (moved, mirrored, quarter turns, the sleeve laid
across the chest, the coat grown into the bare side) all read wrong to the user: 「左手攻击导致身体看起来非常非常奇怪」
(Q: a jumble of red and gold on the chest; R: the sleeve apart from the shoulder). A body shape the design does not have
is the image model's job (memory proportions-go-to-codex). Everything else stays the design's squares.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md, 1_design.png (the design at PX px a square on the 1254 canvas), 2_grid.png
(the same with a grid every 5 squares, the hat-top and ground lines), 3_arm_closeup.png (the near arm and cannon at 10x),
4_lol_idle.png / 5_lol_q_aim.png / 6_lol_r_up.png (League's model: Riot's, kept local, never committed), 7_not_q.png /
8_not_r.png (the rejected posings, at PX).
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_gangplank_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gangplank")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "gp_work")
LOL = "C:/t/gp_dl/poses"
PX = 17
CANVAS = 1254
X0, Y0 = 142, 160        # the design's (0, 0) on the canvas: 57 x 62 squares -> 969 x 1054 px, room above the hat for
                         # R's raised cannon


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def on_canvas(d):
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(d, PX)), (X0, Y0))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "gangplank_pose_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA"))
    H, W = d.shape[:2]
    on_canvas(d).save(os.path.join(out, "1_design.png"))
    grid = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    grid.alpha_composite(on_canvas(d))
    dr = ImageDraw.Draw(grid)
    for c in range(0, W + 1, 5):
        dr.line([(X0 + c * PX, 0), (X0 + c * PX, CANVAS)], fill=(205, 205, 205, 255))
    for r in range(0, H + 1, 5):
        dr.line([(0, Y0 + r * PX), (CANVAS, Y0 + r * PX)], fill=(205, 205, 205, 255))
    dr.line([(0, Y0), (CANVAS, Y0)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, Y0 + H * PX), (CANVAS, Y0 + H * PX)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, CANVAS - 24), f"one square = {PX} px, {W} x {H} squares; green = hat top y {Y0}, red = ground y "
                               f"{Y0 + H * PX}", fill=(40, 40, 40, 255))
    grid.convert("RGB").save(os.path.join(out, "2_grid.png"))
    arm = d[4:34, 0:24]
    bg = Image.new("RGBA", (arm.shape[1], arm.shape[0]), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(arm))
    bg.convert("RGB").resize((arm.shape[1] * 10, arm.shape[0] * 10), Image.NEAREST).save(
        os.path.join(out, "3_arm_closeup.png"))
    for src, name in (("lol_idle", "4_lol_idle.png"), ("lol_q_aim", "5_lol_q_aim.png"), ("lol_r_up", "6_lol_r_up.png")):
        shutil.copyfile(os.path.join(LOL, src + ".png"), os.path.join(out, name))
    import rig_gangplank as G
    F = G.form()
    rig = F.rig
    acts = G.frames(F)
    for tag, i, name in (("skill", 1, "7_not_q.png"), ("ult", 2, "8_not_r.png")):
        f = rig.finish(acts[tag][i][0])
        sub = f[rig.oy - 6:rig.oy + H + 2, rig.ox - 8:rig.ox + W + 8]
        im = Image.new("RGBA", (sub.shape[1], sub.shape[0]), (225, 225, 225, 255))
        im.alpha_composite(Image.fromarray(sub))
        im.convert("RGB").resize((sub.shape[1] * 8, sub.shape[0] * 8), Image.NEAREST).save(os.path.join(out, name))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Akshan's gun-arm pose pack for Codex (assets/source/akshan/POSE_PROMPTS.md): the approved design with only the near
(image-left) arm and the relic pistol drawn again, held out forward and level the way League's attack holds it.

    python tools/art/pack_akshan_poses.py [--out C:/t/ak_work/akshan_pose_pack]

Why (2026-10-18): the design raises the gun beside his head; no arm in it reaches forward. Turning the forearm and the
gun level from the design's own squares put the gun over the chest (a jumble of crimson and gold on the orange sash);
hiding the upper arm so the forearm could reach across left it starting in the middle of his chest - the user: 「手都断了？」.
Gangplank's lesson (memory gangplank-session): a limb pose the design lacks -> one Codex "same design, only this arm"
picture on the design's exact grid, then only the changed squares are stamped (tools/art/design_akshan_poses.py).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md, 1_design.png (the design at PX px a square on the 1254 canvas, room on
the right for the gun held out), 2_grid.png (the same with a grid every 5 squares, the hair-top and ground lines),
3_arm_closeup.png (the gun arm at 10x), 4_lol_idle.png / 5_lol_aim.png (League's model: Riot's, kept local, never
committed), 6_not_like_this.png (the rejected posings at 8x).
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
import rig_akshan as A  # noqa: E402

lp = A.lp
SRC = os.path.join(ROOT, "assets", "source", "akshan")
LOL = "C:/t/ak_work/akshan_pack0/refs"
PX = 15
CANVAS = 1254
X0, Y0 = 90, 165         # the design's (0, 0) on the canvas: 46 x 69 squares -> 690 x 1035 px, soles on y 1200, room on
                         # the right for the gun held out (to about x 1100)


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def on_canvas(d):
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(d, PX)), (X0, Y0))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/ak_work/akshan_pose_pack")
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
    for c in range(0, (CANVAS - X0) // PX + 1, 5):
        dr.line([(X0 + c * PX, 0), (X0 + c * PX, CANVAS)], fill=(205, 205, 205, 255))
    for r in range(-(Y0 // PX), H + 1, 5):
        dr.line([(0, Y0 + r * PX), (CANVAS, Y0 + r * PX)], fill=(205, 205, 205, 255))
    hair = Y0 + 12 * PX
    dr.line([(0, hair), (CANVAS, hair)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, Y0 + H * PX), (CANVAS, Y0 + H * PX)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, CANVAS - 24), f"one square = {PX} px, {W} x {H} squares from x {X0}; green = top of the hair y {hair}, "
                               f"red = ground y {Y0 + H * PX}", fill=(40, 40, 40, 255))
    grid.convert("RGB").save(os.path.join(out, "2_grid.png"))
    arm = d[0:42, 0:20]
    bg = Image.new("RGBA", (arm.shape[1], arm.shape[0]), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(arm))
    bg.convert("RGB").resize((arm.shape[1] * 10, arm.shape[0] * 10), Image.NEAREST).save(
        os.path.join(out, "3_arm_closeup.png"))
    for src, name in (("1_akshan_idle", "4_lol_idle.png"), ("6_akshan_attack", "5_lol_aim.png")):
        shutil.copyfile(os.path.join(LOL, src + ".png"), os.path.join(out, name))
    # the two rejected posings: the forearm turned level over the chest, and the forearm reaching across with the upper
    # arm hidden (「手都断了？」)
    F = A.form()
    rig = F.rig
    bad = [rig.finish(F.pose(**A.AIM)), rig.finish(F.pose(gun=(17, -6), reach=True, **A.AIM))]
    tiles = []
    for f in bad:
        sub = f[rig.oy - 4:rig.oy + H + 2, rig.ox - 4:rig.ox + W + 18]
        im = Image.new("RGBA", (sub.shape[1], sub.shape[0]), (225, 225, 225, 255))
        im.alpha_composite(Image.fromarray(sub))
        tiles.append(im.convert("RGB").resize((sub.shape[1] * 8, sub.shape[0] * 8), Image.NEAREST))
    sheet = Image.new("RGB", (sum(t.width for t in tiles) + 24, tiles[0].height), (255, 255, 255))
    sheet.paste(tiles[0], (0, 0))
    sheet.paste(tiles[1], (tiles[0].width + 24, 0))
    sheet.save(os.path.join(out, "6_not_like_this.png"))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()

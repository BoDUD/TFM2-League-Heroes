#!/usr/bin/env python3
"""Graves's pose pack for Codex (assets/source/graves/POSE_PROMPTS.md): the poses his actions need that the side design
cannot give by whole-square moves - League tips the shotgun up after every shot (the pump), lunges low in Q and E, hefts
the gun to the shoulder for R and hops back from its recoil, and drops the gun to fall on his face in the death.

    python tools/art/pack_graves_poses.py [--out C:/t/gv_work/graves_pose_pack] [--lol D:/WeGameApps/lol]

Every pose is ONE 1254 picture at 16 px a square, soles on y 1168 - the grid of the step-1 redraw. Writes <out>/ (and
<out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the approved side design on that grid with its own skeleton drawn
over it: what each line stands for); 1_idle_head.png (the idle's head, 8x: every pose wears it); 2_side_design.png (the
side design on the grid, clean); per pose
<k>_<name>_skeleton.png (the grid, the ground, the skeleton at the design's own segment lengths and a grey box where
the head goes) and <k>_<name>_league.png (League's frame for it, side-on: the pose to copy; Riot's, kept local).
Skeleton colours: green = the spine (pelvis to neck), RED = the FRONT leg (image right), BLUE = the BACK leg, ORANGE =
the arm on the gun's back grip, PURPLE = the arm on the fore-grip, thick GOLD line = the shotgun (stock end, drum,
muzzle - one STRAIGHT gun), magenta = the scarf's tail; grey box = the head (idle head, never redrawn). Death poses
have no gun line: he has dropped it (the design's own gun is laid on the ground by the rig).
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
from design_graves_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "graves")
PX, CANVAS, SOLE_Y = 16, 1254, 1168
GREY = (225, 225, 225)
GROUND = SOLE_Y // PX - 1          # the soles' row on the canvas grid (72)
DX, DY = 2, GROUND - 56            # the side design's (0, 0) on the canvas grid (its soles on row 56)
COL = {"spine": (0, 170, 60), "front": (230, 30, 30), "back": (40, 90, 230), "grip": (255, 140, 0),
       "fore": (150, 60, 200), "gun": (215, 170, 0), "cape": (230, 0, 200)}
HEAD = (0, 18, 18, 39)             # rows / columns of the head in hd/idle.png (hair top to the beard's tip)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 21 x 18 squares


def d2c(pts):
    return [(x + DX, y + DY) for x, y in pts]


# the side design's skeleton, measured on hd/side.png (74 x 57), moved onto the canvas grid
REST = {
    "spine": d2c([(34, 39), (36, 18)]),
    "grip": d2c([(27, 22), (24, 30), (26, 34)]),
    "fore": d2c([(37, 22), (41, 30), (48, 35)]),
    "gun": d2c([(10, 35), (29, 31), (73, 30)]),
    "back": d2c([(31, 40), (26, 46), (21, 53), (25, 55)]),
    "front": d2c([(38, 40), (44, 46), (46, 53), (53, 55)]),
    "cape": d2c([(27, 20), (12, 27), (1, 30)]),
    "head": (37.5 + DX, 9 + DY),
}


def gun_at(hand, deg, behind=16, drum=3, ahead=47):
    """The shotgun's three points (stock end, drum, muzzle) held at `hand` (the back grip) and tipped `deg` up."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    hx, hy = hand
    return [(hx - ux * behind, hy - uy * behind), (hx + ux * drum, hy + uy * drum), (hx + ux * ahead, hy + uy * ahead)]


def along(hand, deg, k):
    a = math.radians(deg)
    return (hand[0] + math.cos(a) * k, hand[1] - math.sin(a) * k)


# the poses, canvas squares (soles on row 72); League's frame for each (clip, ms) and what it is for
TILT_HAND = (28, 50)
HOP_HAND = (30, 44)
POSES = {
    "tilt": (dict(spine=[(36, 55), (37, 34)], head=(38.5, 25),
                  grip=[(29, 38), (25, 45), TILT_HAND], fore=[(38, 38), (44, 43), along(TILT_HAND, 30, 22)],
                  gun=gun_at(TILT_HAND, 30), back=REST["back"], front=REST["front"], cape=REST["cape"]),
             ("graves_attack1", 300), "枪口往上翘：开枪后的后坐力和拉枪栓，枪管往上斜约 30°，腿和定稿一样"),
    "lunge": (dict(spine=[(31, 59), (37, 39)], head=(38.5, 30),
                   grip=[(31, 43), (27, 50), (28, 54)], fore=[(39, 43), (44, 50), (50, 55)],
                   gun=[(12, 56), (31, 52), (75, 51)],
                   back=[(29, 60), (21, 64), (13, 69), (16, 71)], front=[(35, 60), (44, 63), (46, 70), (53, 71)],
                   cape=[(30, 41), (16, 44), (4, 43)]),
              ("graves_spell1", 183), "低身前冲：前腿弓步、后腿往后蹬直，身子前倾压低，枪平端在腰间朝前"),
    "shoulder": (dict(spine=[(34, 55), (33, 34)], head=(34.5, 25),
                      grip=[(27, 38), (23, 41), (28, 41)], fore=[(36, 38), (43, 42), (50, 41)],
                      gun=[(12, 43), (31, 40), (75, 39)],
                      back=[(31, 56), (24, 62), (17, 69), (21, 71)], front=[(37, 56), (45, 62), (50, 69), (57, 71)],
                      cape=[(27, 36), (13, 40), (2, 41)]),
                 ("graves_spell4", 233), "端到肩高：两腿前后叉开站稳，身子微微后仰，两只手把枪举到胸口 / 肩膀的高度，枪管水平朝前"),
    "hop": (dict(spine=[(36, 48), (35, 28)], head=(36, 19),
                 grip=[(30, 31), (26, 38), HOP_HAND], fore=[(37, 31), (42, 32), along(HOP_HAND, 55, 22)],
                 gun=gun_at(HOP_HAND, 55), back=[(33, 49), (28, 56), (24, 63), (28, 65)],
                 front=[(39, 49), (46, 54), (43, 61), (49, 63)], cape=[(30, 30), (18, 24), (6, 22)]),
            ("graves_spell4_BACK", 213), "被后坐力震得往后跳：两脚离地、膝盖弯起，身子后仰，枪口朝上斜约 55°，围巾往上飘"),
    "stagger": (dict(spine=[(36, 55), (32, 35)], head=(32.5, 26),
                     grip=[(28, 38), (22, 42), (17, 46)], fore=[(36, 38), (42, 40), (47, 37)],
                     back=[(33, 56), (29, 63), (26, 70), (30, 71)], front=[(40, 56), (47, 62), (51, 69), (58, 71)],
                     cape=[(28, 37), (16, 46), (8, 52)]),
                ("graves_death", 358), "中枪后仰：枪已经脱手（不画枪），身子往后仰，两只手甩开，一只脚往前踏"),
    "kneel": (dict(spine=[(34, 62), (37, 42)], head=(38.5, 33),
                   grip=[(32, 45), (31, 52), (33, 58)], fore=[(41, 45), (43, 52), (41, 57)],
                   back=[(33, 63), (37, 70), (28, 71), (25, 71)], front=[(38, 63), (43, 70), (35, 71), (32, 71)],
                   cape=[(32, 43), (22, 52), (14, 60)]),
              ("graves_death", 1433), "跪倒：两个膝盖着地、小腿平贴地面往后，上身直着、头微微低下，两只手垂在身前（不画枪）"),
    "lie": (dict(spine=[(28, 68), (48, 67)], head=(58, 63),
                 grip=[(46, 66), (52, 70), (57, 71)], fore=[(40, 67), (34, 70), (28, 71)],
                 back=[(27, 68), (17, 69), (7, 70), (4, 71)], front=[(29, 69), (19, 70), (9, 71), (6, 71)],
                 cape=[(46, 64), (36, 63), (26, 64)]),
            ("graves_death", 2508), "趴倒：整个人脸朝下趴在地上（头在右边、下巴贴地），两腿伸直往左，一只手往前伸（不画枪）"),
}


def canvas_grid():
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(215, 215, 215, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(215, 215, 215, 255))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    return can


def c(p):
    """A square's middle on the canvas in px."""
    return ((p[0] + 0.5) * PX, (p[1] + 0.5) * PX)


def skeleton(can, sk, label, alpha=255):
    dr = ImageDraw.Draw(can, "RGBA")
    hx, hy = sk["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    order = [("cape", "cape", 5), ("back", "back", 7), ("spine", "spine", 7), ("front", "front", 7),
             ("grip", "grip", 7), ("gun", "gun", 14), ("fore", "fore", 7)]
    for name, key, w in order:
        if name not in sk:
            continue
        pts = [c(p) for p in sk[name]]
        dr.line(pts, fill=COL[key] + (alpha,), width=w, joint="curve")
        for p in pts:
            r = 9 if name == "gun" else 7
            dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=COL[key] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def gun_part(side):
    """The shotgun alone, cut from the side design by its colours (the gold and the black steel round the gun's rows)."""
    rgb = side[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    gold = (r > 150) & (g > 100) & (b < 90)
    steel = (np.abs(r - b) < 25) & (r < 110) & (side[..., 3] > 0)
    yy, xx = np.mgrid[0:side.shape[0], 0:side.shape[1]]
    box = (yy >= 26) & (yy <= 39) & (xx >= 9)
    m = (gold | steel) & box
    out = np.zeros_like(side)
    out[m] = side[m]
    ys, xs = np.nonzero(m)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def lol_frame(lol, clip, ms, work):
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Graves",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900", "--fit", "0.4",
           "--ground", "0.8", "--width", "2.0", "--yaw", "75", "--name", "f", "--out", work,
           "--frame", f"{clip}@{ms}"]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "f.png")).convert("RGB")
    a = np.asarray(im).astype(int)
    fg = np.abs(a - GREY).sum(2) > 12
    ys, xs = np.nonzero(fg)
    m = 40
    return im.crop((max(0, xs.min() - m), max(0, ys.min() - m), min(im.width, xs.max() + m), min(im.height, ys.max() + m)))


def big(a, z=8):
    im = Image.fromarray(up(a, z))
    bg = Image.new("RGBA", im.size, GREY + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/gv_work/graves_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    side = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "side.png"))).convert("RGBA"))
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    base = canvas_grid()
    base.alpha_composite(on_grid(side, DX, DY))
    clean = base.copy()
    skeleton(base, REST, "0: the approved side design with its own skeleton (what each coloured line stands for)", 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_side_design.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_idle_head.png"))
    for k, (name, (sk, (clip, ms), what)) in enumerate(POSES.items(), 3):
        can = canvas_grid()
        skeleton(can, sk, f"{k}: {name} - skeleton on the 16 px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, clip, ms, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, clip, ms)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Warwick's pose pack for Codex (assets/source/warwick/POSE_PROMPTS.md): the whole-body poses League's clips go through
that the hunched 3/4 design cannot give by moving its own parts (the user, 2026-10-20, on the first rig: 「怎么看起来只有
挥手的动作啊？和英雄联盟狼人那么多动作一样吗」, then picked 「Codex 照骨架画关键姿势」).

    python tools/art/pack_warwick_poses.py [--out C:/t/ww_work/warwick_pose_pack] [--lol D:/WeGameApps/lol]

Every pose is ONE 1254 picture at 12 px a square, soles on y 1176 - the grid of the step-1 redraw (the design A-1 sits at
squares (5, 29) on it). Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the approved design on
that grid with its own skeleton drawn over it: what each line stands for); 1_head.png (the design's head with its mane,
8x: every pose wears it); 2_design.png (the design on the grid, clean); per pose <k>_<name>_skeleton.png (the grid, the
ground, the skeleton at the design's own segment lengths and a grey box where the head goes) and <k>_<name>_league.png
(League's frame for it, 3/4 facing right: the pose to copy; Riot's, kept local).
Skeleton colours: green = the spine (pelvis to the hump of his back), RED = the NEAR leg (image left, in front),
BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left: the gauntlet with the green vials), PURPLE = the FAR
arm (image right), thick GOLD line = the back rig (the green vial's base to the copper spike's tip), magenta = the tail;
grey box = the head (the design's head and mane, never redrawn). The run stays league_braum's walk on the design.
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
sys.path.insert(0, HERE)
from design_warwick_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "warwick")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
GREY = (225, 225, 225)
DX, DY = 5, 29                     # the design's (0, 0) on the canvas grid (its soles on row 68 -> 97)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "rig": (215, 170, 0), "tail": (230, 0, 200)}
HEAD = (9, 44, 42, 80)             # rows / columns of the head with its ears and mane in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 38 x 35 squares


def d2c(pts):
    return [(x + DX, y + DY) for x, y in pts]


def sk(head, spine, rig, near_arm, far_arm, near_leg, far_leg, tail):
    """A skeleton in design squares (the design's own ground row 68), moved onto the canvas grid."""
    return {"head": (head[0] + DX, head[1] + DY), "spine": d2c(spine), "rig": d2c(rig), "near_arm": d2c(near_arm),
            "far_arm": d2c(far_arm), "near_leg": d2c(near_leg), "far_leg": d2c(far_leg), "tail": d2c(tail)}


# the design's own skeleton, measured on hd/idle.png (94 x 69): shoulder, elbow, wrist, claw tips; hip, knee, hock, toes
REST = sk(head=(61, 26.5), spine=[(53, 49), (48, 30)], rig=[(52, 16), (52, 0)],
          near_arm=[(42, 25), (33, 36), (32, 50), (31, 60)], far_arm=[(76, 29), (81, 37), (87, 46), (88, 60)],
          near_leg=[(44, 50), (39, 56), (34, 61), (30, 68)], far_leg=[(63, 50), (69, 55), (66, 61), (77, 68)],
          tail=[(33, 47), (17, 35), (4, 18)])

# the poses (design squares, ground row 68); League's frame for each (clip, ms) and what it is for
POSES = {
    "crouch": (sk(head=(66, 37), spine=[(52, 56), (50, 40)], rig=[(52, 27), (54, 11)],
                  near_arm=[(44, 36), (32, 44), (24, 52), (18, 58)], far_arm=[(84, 46), (89, 52), (92, 58), (94, 66)],
                  near_leg=[(45, 57), (36, 60), (31, 64), (26, 68)], far_leg=[(61, 57), (72, 60), (70, 64), (80, 68)],
                  tail=[(37, 55), (20, 46), (6, 34)]),
               ("warwick_attack1", 120), "蹲伏：压得很低、身子前倾、头往前探，两条胳膊张开到身体两侧，爪子低低地张着，两腿深蹲（普攻和大招的蓄力）"),
    "rear": (sk(head=(60, 18), spine=[(50, 48), (50, 26)], rig=[(44, 14), (42, -2)],
                near_arm=[(42, 28), (36, 38), (42, 44), (48, 38)], far_arm=[(78, 30), (84, 38), (86, 30), (86, 22)],
                near_leg=[(44, 50), (40, 56), (36, 62), (32, 68)], far_leg=[(58, 50), (64, 56), (62, 62), (70, 68)],
                tail=[(36, 48), (22, 52), (8, 48)]),
             ("warwick_spell1", 0), "后仰张嘴：身子直起来往后仰、胸口挺出，两只爪子抬到胸前，张开大嘴（Q 起手、E）"),
    "leap": (sk(head=(66, 20), spine=[(46, 46), (56, 30)], rig=[(50, 18), (48, 2)],
                near_arm=[(48, 26), (42, 14), (46, 4), (52, -2)], far_arm=[(84, 30), (90, 20), (94, 12), (97, 6)],
                near_leg=[(42, 48), (36, 52), (30, 56), (24, 58)], far_leg=[(52, 48), (58, 54), (52, 58), (60, 60)],
                tail=[(36, 44), (20, 38), (4, 36)]),
             ("warwick_spell4dash", 300), "空中飞扑：整个人腾空（脚离地约 8 格），身子斜着往前上方，两条胳膊张开举起、爪子张开，两腿收在身下往后，尾巴往后飘（Q、R）"),
    "bite": (sk(head=(68, 38), spine=[(50, 54), (48, 38)], rig=[(50, 26), (52, 10)],
                near_arm=[(42, 36), (30, 42), (22, 50), (18, 60)], far_arm=[(86, 46), (90, 54), (91, 60), (92, 67)],
                near_leg=[(44, 56), (34, 58), (30, 63), (24, 68)], far_leg=[(60, 56), (70, 58), (68, 63), (78, 68)],
                tail=[(36, 52), (20, 44), (6, 30)]),
             ("warwick_spell1", 330), "落地撕咬：落地后压成很宽的深蹲，头低低地往前咬下去，两条胳膊往两边撑开、爪子朝下（Q 落地）"),
    "howl": (sk(head=(58, 14), spine=[(52, 46), (54, 24)], rig=[(46, 10), (44, -6)],
                near_arm=[(40, 28), (36, 38), (36, 48), (36, 54)], far_arm=[(76, 30), (78, 40), (78, 48), (78, 54)],
                near_leg=[(46, 48), (42, 56), (40, 62), (36, 68)], far_leg=[(60, 48), (64, 56), (62, 62), (68, 68)],
                tail=[(40, 46), (26, 40), (12, 30)]),
             ("warwick_spell3_howl", 475), "直立嚎叫：整个人站直、站高，胸口挺出，两条胳膊垂在身体两侧、拳头握紧，头抬得很高（E 的嚎叫）"),
    "strike": (sk(head=(72, 36), spine=[(48, 52), (56, 38)], rig=[(56, 28), (54, 12)],
                  near_arm=[(54, 42), (62, 52), (70, 58), (78, 64)], far_arm=[(88, 40), (94, 48), (96, 56), (97, 64)],
                  near_leg=[(44, 54), (36, 58), (30, 63), (24, 68)], far_leg=[(56, 54), (64, 58), (62, 63), (72, 68)],
                  tail=[(38, 50), (22, 42), (6, 36)]),
               ("warwick_spell4hit", 227), "扑下连抓：身子往前压低扑下去，头在前面低处，两只爪子一起往前下方抓下去，后腿往后蹬（普攻出手、R 压住时抓下去）"),
    "raise": (sk(head=(60, 20), spine=[(52, 48), (52, 28)], rig=[(46, 12), (44, -4)],
                 near_arm=[(42, 30), (32, 32), (24, 36), (18, 34)], far_arm=[(78, 30), (86, 18), (88, 8), (88, -2)],
                 near_leg=[(46, 50), (40, 56), (36, 62), (32, 68)], far_leg=[(60, 50), (66, 56), (64, 62), (72, 68)],
                 tail=[(38, 48), (24, 46), (10, 40)]),
              ("warwick_spell4hit", 0), "举爪：身子立起来，远侧那只手臂高高举过头顶、爪子朝上，近侧手臂往外甩开，张嘴（R 压住时抬爪、普攻蓄力）"),
    "stagger": (sk(head=(54, 18), spine=[(50, 48), (46, 28)], rig=[(40, 14), (36, -2)],
                   near_arm=[(38, 26), (28, 30), (20, 36), (14, 40)], far_arm=[(72, 32), (80, 26), (88, 28), (94, 32)],
                   near_leg=[(46, 50), (42, 56), (38, 62), (34, 68)], far_leg=[(58, 50), (66, 56), (68, 62), (76, 68)],
                   tail=[(38, 48), (24, 54), (10, 58)]),
                ("warwick_death", 320), "中招后仰：身子往后仰，两条胳膊往两边甩开，一只脚往前踏稳（死亡第一下）"),
    "lie": (sk(head=(74, 50.5), spine=[(36, 62), (58, 58)], rig=[(48, 54), (44, 42)],
               near_arm=[(52, 56), (58, 62), (54, 66), (60, 68)], far_arm=[(50, 60), (56, 66), (64, 68), (70, 68)],
               near_leg=[(36, 64), (28, 62), (20, 64), (14, 68)], far_leg=[(38, 60), (30, 56), (22, 58), (16, 62)],
               tail=[(30, 62), (16, 66), (2, 68)]),
            ("warwick_death", 2900), "侧躺倒地：整个人侧躺在地上，头在画面右边、下巴贴地，身子和两腿往左伸，两只手软软地搭在身前地上，尾巴平放在身后地上（死亡）"),
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


def skeleton(can, s, label, alpha=255):
    dr = ImageDraw.Draw(can, "RGBA")
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    order = [("tail", 6), ("far_leg", 7), ("far_arm", 7), ("spine", 7), ("rig", 12), ("near_leg", 7), ("near_arm", 7)]
    for name, w in order:
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=w, joint="curve")
        for p in pts:
            r = 8 if name == "rig" else 6
            dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, clip, ms, work):
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Warwick",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900", "--fit", "0.4",
           "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work,
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
    ap.add_argument("--out", default="C:/t/ww_work/warwick_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    base = canvas_grid()
    base.alpha_composite(on_grid(idle, DX, DY))
    clean = base.copy()
    skeleton(base, REST, "0: the approved design with its own skeleton (what each coloured line stands for)", 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, (clip, ms), what)) in enumerate(POSES.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the 12 px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, clip, ms, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, clip, ms)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

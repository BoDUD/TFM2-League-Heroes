#!/usr/bin/env python3
"""Sylas's pose pack for Codex (assets/source/sylas/POSE_PROMPTS.md): the whole-body poses League's clips go through that
the 3/4 design cannot give by moving its own parts (the user, 2026-10-20, picked 「Codex 照骨架画关键姿势」 for the
actions, Warwick's way).

    python tools/art/pack_sylas_poses.py [--out C:/t/sy_work/sylas_pose_pack] [--lol D:/WeGameApps/lol]

Every pose is ONE 1254 picture at 16 px a square, soles on y 1168 - the grid of the step-1 redraw (the design A-1 sits at
squares (6, 27) on it). Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the approved design on
that grid with its own skeleton drawn over it: what each line stands for); 1_head.png (the design's head with its hair
and scarf, 8x: every pose wears it); 2_design.png (the design on the grid, clean); per pose <k>_<name>_skeleton.png (the
grid, the ground, the skeleton at the design's own segment lengths and a grey box where the head goes) and
<k>_<name>_league.png (League's frame for it, 3/4 facing right: the pose to copy; Riot's, kept local).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left) to its manacled fist, PURPLE = the FAR arm (image right), YELLOW = the
near chain, OLIVE = the far chain (each from its manacle); grey box = the head (the design's head, never redrawn).
The run is in the pack too (four frames: League's Sylas_Run), legs on skeletons (codex-legs-need-skeletons).
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
from design_sylas_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_sylas_picture import SUBTEX  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sylas")
PX, CANVAS, SOLE_Y = 16, 1254, 1168
GREY = (225, 225, 225)
DX, DY = 6, 27                     # the design's (0, 0) on the canvas grid (its soles on row 45 -> 72)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "near_chain": (240, 210, 0), "far_chain": (150, 140, 20)}
HEAD = (0, 14, 29, 46)             # rows / columns of the head with its hair and scarf in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 17 x 14 squares


def d2c(pts):
    return [(x + DX, y + DY) for x, y in pts]


def sk(head, spine, near_arm, far_arm, near_leg, far_leg, near_chain, far_chain):
    """A skeleton in design squares (the design's own ground row 45), moved onto the canvas grid."""
    return {"head": (head[0] + DX, head[1] + DY), "spine": d2c(spine), "near_arm": d2c(near_arm),
            "far_arm": d2c(far_arm), "near_leg": d2c(near_leg), "far_leg": d2c(far_leg),
            "near_chain": d2c(near_chain), "far_chain": d2c(far_chain)}


# the design's own skeleton, measured on hd/idle.png (65 x 46): shoulder, elbow, wrist, fist; hip, knee, ankle, toes;
# each chain from its manacle to its end
REST = sk(head=(37.5, 7), spine=[(37, 27), (37, 15)],
          near_arm=[(28, 16), (25, 22), (24, 29), (24, 33)], far_arm=[(46, 16), (48, 22), (50, 29), (50, 33)],
          near_leg=[(33, 28), (31, 36), (29, 43), (27, 45)], far_leg=[(41, 28), (43, 36), (45, 42), (48, 45)],
          near_chain=[(21, 30), (17, 38), (14, 42), (2, 42)], far_chain=[(55, 32), (57, 38), (60, 42), (64, 42)])

# the poses (design squares, ground row 45); League's frame for each (clip, ms) and what it is for
POSES = {
    "wind": (sk(head=(33, 8), spine=[(35, 28), (33, 15)],
                near_arm=[(25, 16), (19, 15), (13, 15), (9, 16)], far_arm=[(42, 16), (38, 19), (32, 20), (28, 20)],
                near_leg=[(31, 29), (25, 35), (21, 41), (18, 45)], far_leg=[(39, 29), (45, 35), (47, 41), (51, 45)],
                near_chain=[(7, 17), (4, 26), (3, 36), (0, 44)], far_chain=[(26, 21), (24, 30), (26, 38), (28, 44)]),
             ("sylas_attack_01", 0), "蓄力：身子往后仰，近侧手臂甩到身后、远侧拳头收在胸前，两腿前后分开（普攻起手）"),
    "lash": (sk(head=(41, 10), spine=[(37, 29), (40, 17)],
                near_arm=[(31, 18), (26, 22), (22, 27), (20, 30)], far_arm=[(49, 18), (55, 17), (61, 16), (64, 16)],
                near_leg=[(34, 30), (28, 36), (22, 41), (18, 45)], far_leg=[(41, 30), (47, 35), (48, 41), (52, 45)],
                near_chain=[(19, 31), (16, 38), (12, 42), (4, 44)], far_chain=[(65, 16), (69, 18), (71, 22), (72, 26)]),
             ("sylas_attack_01", 229), "甩链：身子前冲，远侧手臂往前甩直、锁链跟着往前抽出去，近侧手臂在身后，前腿弓、后腿蹬（普攻出手）"),
    "spin": (sk(head=(38, 9), spine=[(37, 28), (38, 15)],
                near_arm=[(29, 17), (26, 23), (29, 27), (33, 27)], far_arm=[(47, 17), (50, 22), (47, 26), (43, 27)],
                near_leg=[(33, 29), (27, 34), (23, 40), (20, 45)], far_leg=[(42, 29), (48, 34), (51, 40), (54, 45)],
                near_chain=[(31, 29), (20, 33), (8, 34), (2, 30)], far_chain=[(45, 29), (56, 33), (66, 34), (72, 30)]),
             ("sylas_attack_passive", 1050), "挥链横扫：两腿大开蹲低，两只镣铐收到肚子前面，两条锁链往两边横着甩开（被动的横扫）"),
    "leap": (sk(head=(38, 4), spine=[(37, 22), (38, 10)],
                near_arm=[(30, 10), (28, 4), (30, -2), (32, -6)], far_arm=[(46, 10), (49, 4), (48, -2), (46, -6)],
                near_leg=[(34, 23), (30, 29), (31, 35), (28, 37)], far_leg=[(41, 23), (46, 27), (44, 33), (47, 36)],
                near_chain=[(32, -7), (24, -6), (18, 0), (14, 8)], far_chain=[(46, -7), (54, -4), (60, 2), (62, 10)]),
             ("sylas_spell2", 75), "跃起：整个人腾空（脚离地约 8 格），两只镣铐高举过头，两腿收起，锁链在头顶两边甩开（W 起跳、Q 起手）"),
    "stab": (sk(head=(43, 12), spine=[(36, 30), (42, 19)],
                near_arm=[(36, 20), (43, 24), (50, 26), (54, 27)], far_arm=[(50, 20), (56, 23), (61, 25), (64, 26)],
                near_leg=[(33, 31), (27, 37), (21, 42), (16, 45)], far_leg=[(40, 31), (47, 36), (49, 41), (53, 45)],
                near_chain=[(55, 28), (50, 34), (46, 40), (40, 44)], far_chain=[(65, 27), (66, 34), (66, 40), (70, 44)]),
             ("sylas_spell2", 263), "突刺：落地往前扑，身子压低，两只镣铐一起往前捅出去（在腰的高度），后腿往后蹬直（W 弑君突刺）"),
    "slam": (sk(head=(42, 15), spine=[(36, 34), (41, 22)],
                near_arm=[(36, 23), (42, 29), (46, 35), (48, 40)], far_arm=[(48, 23), (53, 29), (56, 35), (58, 40)],
                near_leg=[(33, 35), (28, 40), (22, 44), (16, 45)], far_leg=[(40, 35), (47, 36), (48, 42), (51, 45)],
                near_chain=[(49, 42), (56, 44), (64, 44), (72, 44)], far_chain=[(59, 42), (64, 43), (70, 42), (76, 43)]),
             ("sylas_spell1_cast", 325), "单膝砸地：后腿跪地、前腿弓起，身子前倾，两只镣铐砸在身前地上，锁链往前平铺在地上（Q 锁链鞭击）"),
    "dash": (sk(head=(44, 13), spine=[(35, 30), (42, 19)],
                near_arm=[(36, 20), (30, 22), (24, 22), (20, 22)], far_arm=[(48, 20), (44, 24), (38, 26), (34, 26)],
                near_leg=[(33, 31), (26, 34), (20, 38), (14, 40)], far_leg=[(39, 31), (46, 35), (46, 41), (50, 45)],
                near_chain=[(19, 23), (12, 24), (6, 26), (0, 28)], far_chain=[(33, 27), (26, 30), (18, 32), (10, 33)]),
             ("sylas_spell3_dash", 133), "冲刺：身子压低往前冲，两只手臂往身后甩，锁链拖在身后飘起来，后腿离地往后蹬（E 潜掠）"),
    "throw": (sk(head=(38, 8), spine=[(36, 28), (37, 15)],
                 near_arm=[(28, 17), (22, 19), (16, 20), (12, 21)], far_arm=[(46, 16), (53, 16), (60, 16), (64, 16)],
                 near_leg=[(32, 29), (25, 35), (20, 41), (16, 45)], far_leg=[(40, 29), (46, 35), (48, 41), (52, 45)],
                 near_chain=[(10, 22), (7, 30), (6, 38), (2, 44)], far_chain=[(65, 17), (68, 22), (68, 30), (70, 38)]),
              ("sylas_spell4_cast", 108), "甩出锁链：两腿大开站稳，远侧手臂朝前伸直、和肩一样高，近侧手臂拉到身后（E 强掳、R 偷大招出手）"),
    "pull": (sk(head=(52, 16), spine=[(32, 26), (46, 21)],
                near_arm=[(44, 22), (50, 26), (56, 27), (59, 27)], far_arm=[(52, 21), (58, 21), (64, 20), (68, 20)],
                near_leg=[(30, 27), (22, 32), (14, 36), (10, 37)], far_leg=[(33, 28), (26, 34), (18, 40), (14, 42)],
                near_chain=[(60, 28), (62, 34), (62, 40), (60, 44)], far_chain=[(69, 20), (72, 21), (74, 22), (76, 23)]),
             ("sylas_spell3_bhit_cast", 325), "被锁链拉过去：整个人往前横着飞，远侧手臂朝前伸直，两腿在身后拖直（E 强掳把自己拉过去）"),
    "stagger": (sk(head=(35, 5), spine=[(37, 27), (36, 14)],
                   near_arm=[(28, 16), (24, 22), (22, 28), (21, 32)], far_arm=[(45, 16), (49, 21), (52, 26), (54, 29)],
                   near_leg=[(33, 28), (31, 36), (30, 43), (28, 45)], far_leg=[(41, 28), (44, 36), (47, 42), (50, 45)],
                   near_chain=[(19, 33), (16, 39), (12, 44), (4, 44)], far_chain=[(56, 30), (58, 37), (60, 43), (66, 44)]),
                ("sylas_death", 625), "中招后仰：站直往后仰、头往后甩，两只手臂垂在身体两边（死亡第一下）"),
    "kneel": (sk(head=(40, 16), spine=[(36, 34), (39, 22)],
                 near_arm=[(31, 23), (30, 30), (32, 36), (33, 40)], far_arm=[(46, 23), (48, 30), (48, 36), (49, 40)],
                 near_leg=[(33, 35), (30, 41), (24, 44), (19, 45)], far_leg=[(40, 35), (38, 41), (32, 44), (27, 45)],
                 near_chain=[(32, 42), (24, 44), (14, 44), (6, 44)], far_chain=[(50, 42), (57, 44), (64, 44), (70, 44)]),
              ("sylas_death", 1250), "跪倒：双膝跪地，身子往前塌，两只镣铐撑在身前地上（死亡第二下）"),
    "lie": (sk(head=(58, 38), spine=[(30, 41), (50, 40)],
               near_arm=[(46, 41), (46, 44), (52, 44), (56, 44)], far_arm=[(48, 38), (54, 36), (62, 38), (66, 42)],
               near_leg=[(30, 42), (22, 42), (14, 43), (10, 44)], far_leg=[(31, 40), (23, 39), (15, 40), (11, 41)],
               near_chain=[(57, 45), (64, 45), (70, 45), (74, 45)], far_chain=[(67, 43), (70, 45), (74, 45), (76, 45)]),
            ("sylas_death", 3750), "趴倒：整个人趴在地上，头在画面右边，两腿往左伸，两只镣铐落在身前地上，锁链散在地上（死亡）"),
    "run1": (sk(head=(39, 8), spine=[(37, 28), (38, 15)],
                near_arm=[(29, 17), (25, 22), (22, 26), (20, 28)], far_arm=[(46, 17), (50, 21), (54, 23), (57, 22)],
                near_leg=[(34, 28), (39, 35), (40, 41), (44, 45)], far_leg=[(40, 28), (36, 35), (31, 40), (28, 44)],
                near_chain=[(19, 29), (13, 34), (7, 38), (1, 40)], far_chain=[(56, 24), (52, 30), (46, 34), (40, 36)]),
             ("sylas_run", 0), "跑步 1（近侧腿在前着地）：身子微微前倾，远侧手臂往前摆、近侧手臂往后摆，锁链拖在身后"),
    "run2": (sk(head=(38, 7), spine=[(37, 27), (38, 14)],
                near_arm=[(29, 16), (27, 22), (26, 27), (26, 30)], far_arm=[(46, 16), (48, 22), (49, 27), (50, 29)],
                near_leg=[(35, 27), (35, 35), (35, 42), (38, 45)], far_leg=[(40, 27), (46, 31), (44, 37), (47, 39)],
                near_chain=[(24, 31), (18, 36), (11, 39), (3, 41)], far_chain=[(50, 31), (46, 36), (40, 39), (34, 41)]),
             ("sylas_run", 250), "跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两只手臂在身侧"),
    "run3": (sk(head=(39, 8), spine=[(37, 28), (38, 15)],
                near_arm=[(29, 17), (33, 22), (37, 25), (40, 25)], far_arm=[(46, 17), (43, 22), (41, 27), (40, 29)],
                near_leg=[(34, 28), (29, 35), (25, 40), (21, 44)], far_leg=[(40, 28), (46, 35), (48, 41), (52, 45)],
                near_chain=[(41, 26), (34, 31), (26, 35), (18, 38)], far_chain=[(39, 30), (32, 35), (24, 38), (16, 40)]),
             ("sylas_run", 500), "跑步 3（远侧腿在前着地）：近侧手臂往前摆到身前（在下巴下面，不挡脸）、远侧手臂往后摆"),
    "run4": (sk(head=(38, 7), spine=[(37, 27), (38, 14)],
                near_arm=[(29, 16), (27, 22), (26, 27), (26, 30)], far_arm=[(46, 16), (48, 22), (49, 27), (50, 29)],
                near_leg=[(34, 27), (39, 31), (37, 37), (40, 39)], far_leg=[(40, 27), (41, 35), (41, 42), (44, 45)],
                near_chain=[(24, 31), (18, 36), (11, 39), (3, 41)], far_chain=[(50, 31), (46, 36), (40, 39), (34, 41)]),
             ("sylas_run", 750), "跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两只手臂在身侧"),
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
    order = [("far_chain", 6), ("far_leg", 7), ("far_arm", 7), ("spine", 7), ("near_leg", 7), ("near_chain", 6), ("near_arm", 7)]
    for name, w in order:
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=w, joint="curve")
        for p in pts:
            r = 6
            dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, clip, ms, work):
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Sylas",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900", "--fit", "0.4",
           "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work,
           "--frame", f"{clip}@{ms}"] + [x for t in SUBTEX for x in ("--submesh-texture", t)] + [
           "--hide-submesh", "Sylas_Base_ChainLock_Mat"]
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
    ap.add_argument("--out", default="C:/t/sy_work/sylas_pose_pack")
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
        skeleton(can, s, f"{k}: {name} - skeleton on the 16 px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, clip, ms, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, clip, ms)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

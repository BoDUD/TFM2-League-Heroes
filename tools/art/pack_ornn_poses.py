#!/usr/bin/env python3
"""Ornn's pose pack for Codex (assets/source/ornn/POSE_PROMPTS.md): the whole-body poses League's clips go through that
the 3/4 design cannot give by moving its own parts (the user, 2026-10-21, picked 「Codex 照骨架画关键姿势」, Sylas's way).

    python tools/art/pack_ornn_poses.py [--out C:/t/on_work/ornn_pose_pack] [--lol D:/WeGameApps/lol]

Every pose is ONE 1254 picture at 16 px a square, soles on y 1248 - the design (hd/idle.png, 71 x 66, A-3) sits at
squares (DX, DY) so a hammer raised over the horns still fits. Writes <out>/ (and <out>.zip): POSE_PROMPTS.md;
0_design_skeleton.png (the approved design on that grid with its own skeleton drawn over it: what each line stands for);
1_head.png (the design's head with its horns, mane and beard, 8x: every pose wears it); 2_design.png (the design on the
grid, clean); per pose <k>_<name>_skeleton.png (the grid, the ground, the skeleton at the design's own segment lengths
and a grey box where the head goes) and <k>_<name>_league.png (League's frame for it, 3/4 facing right: the pose to copy;
Riot's, kept local; his skin's forge props hidden).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left) to its fist, PURPLE = the FAR (molten) arm (image right) to its fist,
YELLOW = the big hammer (butt -> the near fist -> its head), OLIVE = the small hammer (the far fist -> its head); grey box
= the head with its horns (the design's own, never redrawn).
The combos get their own poses: Q -> E is q_raise / q_slam then charge / impact; R1 -> R2 is summon / call then
butt_wind / headbutt.
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
from design_ornn_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ornn")
PX, CANVAS, SOLE_Y = 16, 1254, 1248
GREY = (225, 225, 225)
DX, DY = 3, 12                     # the design's (0, 0) on the canvas grid (its soles on row 65 -> 77)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "big_hammer": (240, 210, 0), "small_hammer": (150, 140, 20)}
HEAD = (0, 41, 7, 69)              # rows / columns of the head with its horns, mane and beard in hd/idle.png (ends excl.)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 62 x 41 squares
HC = ((HEAD[2] + HEAD[3]) / 2, (HEAD[0] + HEAD[1]) / 2)


def d2c(pts):
    return [(x + DX, y + DY) for x, y in pts]


def sk(head, spine, near_arm, far_arm, near_leg, far_leg, big_hammer, small_hammer):
    """A skeleton in design squares (the design's own ground row 65), moved onto the canvas grid."""
    return {"head": (head[0] + DX, head[1] + DY), "spine": d2c(spine), "near_arm": d2c(near_arm),
            "far_arm": d2c(far_arm), "near_leg": d2c(near_leg), "far_leg": d2c(far_leg),
            "big_hammer": d2c(big_hammer), "small_hammer": d2c(small_hammer)}


LEGS = dict(near_leg=[(41, 53), (37, 58), (34, 62), (30, 65)], far_leg=[(51, 53), (53, 58), (55, 62), (59, 65)])
WIDE = dict(near_leg=[(40, 54), (33, 58), (28, 62), (24, 65)], far_leg=[(50, 54), (55, 57), (58, 62), (62, 65)])

# the design's own skeleton, measured on hd/idle.png (71 x 66): shoulder, elbow, wrist, fist; hip, knee, ankle, toes;
# the big hammer butt -> fist -> head, the small one fist -> head
REST = sk(head=HC, spine=[(46, 52), (46, 34)],
          near_arm=[(24, 33), (17, 40), (12, 46), (10, 49)], far_arm=[(57, 35), (61, 42), (63, 48), (64, 51)],
          big_hammer=[(1, 46), (10, 49), (21, 57)], small_hammer=[(64, 51), (67, 56)], **LEGS)

# the poses (design squares, ground row 65); League's frame for each (clip, ms) and what it is for
POSES = {
    "raise": (sk(head=(36, 19), spine=[(45, 52), (43, 34)],
                 near_arm=[(24, 33), (20, 24), (22, 15), (24, 11)], far_arm=[(55, 35), (58, 42), (57, 48), (56, 51)],
                 big_hammer=[(26, 18), (24, 11), (20, -3)], small_hammer=[(56, 51), (59, 57)],
                 near_leg=[(40, 53), (35, 58), (31, 62), (27, 65)], far_leg=[(50, 53), (54, 58), (57, 62), (61, 65)]),
              ("ornn_attack1", 0), "举锤：身子稍往后仰，近侧手把大锤举过头顶（锤头朝上、在头后面），远侧熔岩手握小锤垂在身侧，两腿分开（普攻起手）"),
    "smash": (sk(head=(43, 25), spine=[(44, 53), (50, 37)],
                 near_arm=[(34, 36), (44, 42), (54, 46), (58, 48)], far_arm=[(60, 38), (64, 44), (66, 50), (66, 53)],
                 big_hammer=[(52, 44), (58, 48), (68, 59)], small_hammer=[(66, 53), (70, 58)], **WIDE),
              ("ornn_attack1", 356), "抡锤砸下：身子前倾，近侧手把大锤砸到身前右边的地上（锤头着地），两腿大开（普攻出手）"),
    "q_raise": (sk(head=(37, 17), spine=[(46, 52), (45, 32)],
                   near_arm=[(25, 32), (18, 39), (13, 45), (11, 48)], far_arm=[(55, 34), (56, 24), (54, 15), (53, 10)],
                   big_hammer=[(2, 45), (11, 48), (22, 56)], small_hammer=[(53, 10), (56, 3)], **LEGS),
                ("ornn_spell1", 200), "举起熔岩拳：站直挺胸，远侧熔岩手握着小锤高高举过头顶，近侧手的大锤垂在身侧（Q 起手）"),
    "q_slam": (sk(head=(43, 28), spine=[(44, 55), (50, 40)],
                  near_arm=[(36, 40), (30, 47), (26, 53), (24, 56)], far_arm=[(58, 41), (63, 49), (66, 57), (67, 62)],
                  big_hammer=[(30, 52), (24, 56), (14, 61)], small_hammer=[(67, 62), (71, 64)],
                  near_leg=[(41, 56), (34, 59), (30, 63), (26, 65)], far_leg=[(51, 56), (57, 58), (59, 62), (63, 65)]),
               ("ornn_spell1", 300), "熔岩拳砸地：蹲低前扑，远侧熔岩拳（握小锤）砸在身前右边的地上，近侧大锤拖在身后（Q 火山裂隙）"),
    "breath": (sk(head=(44, 24), spine=[(44, 53), (52, 38)],
                  near_arm=[(36, 37), (30, 44), (26, 50), (23, 53)], far_arm=[(60, 40), (62, 47), (62, 53), (61, 56)],
                  big_hammer=[(15, 50), (23, 53), (28, 60)], small_hammer=[(61, 56), (65, 61)],
                  near_leg=[(40, 54), (34, 58), (31, 62), (27, 65)], far_leg=[(50, 54), (55, 58), (58, 62), (62, 65)]),
               ("ornn_spell2", 311), "喷火：身子前倾，头往前伸、张嘴（不画火），两只手和锤子压低在身侧，两腿大开站稳（W 风箱烈息）"),
    "charge": (sk(head=(46, 30), spine=[(40, 54), (50, 44)],
                  near_arm=[(34, 44), (26, 46), (18, 47), (13, 48)], far_arm=[(56, 46), (52, 52), (46, 55), (42, 56)],
                  big_hammer=[(6, 44), (13, 48), (10, 57)], small_hammer=[(42, 56), (38, 60)],
                  near_leg=[(38, 55), (32, 58), (26, 61), (21, 62)], far_leg=[(46, 56), (52, 59), (52, 63), (56, 65)]),
               ("ornn_spell3_dash", 144), "低头冲撞：身子压得很低往前冲，羊角朝前像公羊顶人，两只手臂甩在身后，后腿离地往后蹬（E 灼热冲撞）"),
    "impact": (sk(head=(35, 18), spine=[(45, 52), (44, 33)],
                  near_arm=[(25, 33), (17, 36), (10, 38), (6, 40)], far_arm=[(55, 34), (62, 36), (67, 38), (69, 40)],
                  big_hammer=[(0, 36), (6, 40), (8, 50)], small_hammer=[(69, 40), (70, 47)], **WIDE),
               ("ornn_spell3_hit", 167), "撞上后挺起：撞上之后身子往后一挺、挺胸抬头，两只手臂往两边张开，两腿大开站稳（E 撞柱 / 撞墙）"),
    "summon": (sk(head=(37, 18), spine=[(46, 52), (45, 33)],
                  near_arm=[(25, 32), (24, 22), (28, 13), (32, 9)], far_arm=[(56, 35), (61, 36), (66, 36), (69, 36)],
                  big_hammer=[(36, 14), (32, 9), (24, -2)], small_hammer=[(69, 36), (72, 32)], **LEGS),
               ("ornn_spell4_windup", 300), "召唤：近侧手把大锤高高举过头顶，远侧熔岩拳朝前伸直（召唤公羊），两腿站稳（R 第一段起手；英雄联盟这一帧只看熔岩拳）"),
    "call": (sk(head=(43, 24), spine=[(44, 53), (50, 37)],
                near_arm=[(34, 36), (42, 43), (50, 48), (54, 50)], far_arm=[(60, 38), (64, 32), (67, 27), (69, 24)],
                big_hammer=[(48, 46), (54, 50), (62, 60)], small_hammer=[(69, 24), (72, 20)], **WIDE),
             ("ornn_attack1", 356), "砸锤召唤：大锤砸在身前地上，远侧熔岩拳朝前上方举起，身子前倾（R 第一段：公羊从远处冲过来）"),
    "butt_wind": (sk(head=(31, 22), spine=[(43, 53), (40, 36)],
                     near_arm=[(22, 36), (18, 42), (17, 48), (17, 51)], far_arm=[(52, 38), (56, 44), (56, 50), (55, 53)],
                     big_hammer=[(9, 48), (17, 51), (22, 59)], small_hammer=[(55, 53), (58, 58)],
                     near_leg=[(39, 54), (35, 58), (32, 62), (28, 65)], far_leg=[(48, 54), (53, 58), (56, 62), (60, 65)]),
                  ("ornn_spell4_hit", 0), "蓄力头槌：身子往后缩、头往后仰、羊角往后收，两只手垂在身侧，准备往前顶（R 第二段起手：公羊冲到身边）"),
    "headbutt": (sk(head=(48, 30), spine=[(40, 55), (51, 42)],
                    near_arm=[(36, 43), (28, 45), (20, 46), (15, 47)], far_arm=[(58, 45), (60, 51), (59, 56), (57, 58)],
                    big_hammer=[(8, 44), (15, 47), (12, 56)], small_hammer=[(57, 58), (61, 62)],
                    near_leg=[(38, 56), (31, 59), (25, 63), (20, 65)], far_leg=[(47, 56), (54, 58), (56, 63), (60, 65)]),
                 ("ornn_spell4_hit", 133), "头槌：往前猛扑，头压低、羊角朝前顶出去，近侧手臂和大锤甩在身后，前腿弓、后腿蹬（R 第二段：把公羊顶回去）"),
    "stagger": (sk(head=(33, 17), spine=[(47, 52), (43, 33)],
                   near_arm=[(24, 33), (21, 40), (20, 47), (20, 50)], far_arm=[(53, 34), (57, 41), (59, 47), (60, 50)],
                   big_hammer=[(12, 47), (20, 50), (24, 58)], small_hammer=[(60, 50), (63, 55)],
                   near_leg=[(42, 53), (39, 58), (36, 62), (32, 65)], far_leg=[(51, 53), (53, 58), (56, 62), (60, 65)]),
                ("ornn_death", 717), "中招后仰：站直往后仰、头往后甩，两只手臂垂在身体两边（死亡第一下）"),
    "kneel": (sk(head=(42, 30), spine=[(43, 57), (48, 43)],
                 near_arm=[(34, 44), (34, 51), (36, 58), (37, 62)], far_arm=[(57, 45), (60, 52), (61, 58), (62, 62)],
                 big_hammer=[(37, 62), (28, 64), (16, 61)], small_hammer=[(62, 62), (67, 64)],
                 near_leg=[(40, 58), (37, 64), (30, 65), (26, 65)], far_leg=[(49, 58), (47, 64), (40, 65), (36, 65)]),
              ("ornn_death", 1433), "跪倒：双膝跪地，身子往前塌，两只拳头撑在身前地上，大锤掉在身边地上（死亡第二下）"),
    "lie": (sk(head=(44, 45), spine=[(14, 61), (36, 59)],
               near_arm=[(34, 58), (40, 62), (46, 64), (50, 64)], far_arm=[(38, 55), (44, 52), (50, 54), (53, 57)],
               big_hammer=[(50, 64), (55, 65), (62, 64)], small_hammer=[(53, 57), (57, 61)],
               near_leg=[(14, 62), (8, 63), (3, 64), (0, 65)], far_leg=[(15, 60), (9, 60), (4, 61), (1, 62)]),
            ("ornn_death", 3583), "趴倒：整个人趴在地上，头和羊角在画面右边，两腿往左伸，锤子落在身前地上（死亡）"),
    "run1": (sk(head=(40, 19), spine=[(45, 51), (48, 34)],
                near_arm=[(27, 34), (21, 40), (16, 45), (13, 47)], far_arm=[(57, 36), (62, 41), (65, 46), (66, 49)],
                big_hammer=[(6, 44), (13, 47), (15, 56)], small_hammer=[(66, 49), (70, 53)],
                near_leg=[(42, 52), (46, 57), (47, 61), (51, 65)], far_leg=[(49, 52), (44, 57), (38, 60), (35, 62)]),
             ("ornn_run", 0), "跑步 1（近侧腿在前着地）：身子前倾，远侧熔岩手往前摆、近侧手（大锤）往后摆"),
    "run2": (sk(head=(39, 18), spine=[(45, 50), (47, 33)],
                near_arm=[(26, 33), (20, 39), (15, 45), (12, 48)], far_arm=[(57, 35), (61, 41), (63, 47), (63, 50)],
                big_hammer=[(5, 45), (12, 48), (16, 57)], small_hammer=[(63, 50), (66, 55)],
                near_leg=[(42, 51), (41, 57), (41, 62), (44, 65)], far_leg=[(49, 51), (55, 55), (54, 60), (57, 61)]),
             ("ornn_run", 258), "跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两只手在身侧"),
    "run3": (sk(head=(40, 19), spine=[(45, 51), (48, 34)],
                near_arm=[(27, 34), (28, 41), (31, 46), (33, 49)], far_arm=[(57, 36), (55, 43), (52, 48), (50, 50)],
                big_hammer=[(26, 46), (33, 49), (37, 57)], small_hammer=[(50, 50), (53, 55)],
                near_leg=[(42, 52), (37, 57), (32, 60), (28, 62)], far_leg=[(49, 52), (53, 57), (55, 61), (59, 65)]),
             ("ornn_run", 517), "跑步 3（远侧腿在前着地）：近侧手（大锤）往前摆到身前低处（不挡脸）、远侧熔岩手往后摆"),
    "run4": (sk(head=(39, 18), spine=[(45, 50), (47, 33)],
                near_arm=[(26, 33), (20, 39), (15, 45), (12, 48)], far_arm=[(57, 35), (61, 41), (63, 47), (63, 50)],
                big_hammer=[(5, 45), (12, 48), (16, 57)], small_hammer=[(63, 50), (66, 55)],
                near_leg=[(42, 51), (47, 55), (46, 60), (49, 61)], far_leg=[(49, 51), (50, 57), (51, 62), (54, 65)]),
             ("ornn_run", 775), "跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两只手在身侧"),
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
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))   # a light box on its own layer: the body shows through
    ImageDraw.Draw(lay).rectangle(box, fill=(120, 120, 120, 70), outline=(90, 90, 90, alpha), width=4)
    can.alpha_composite(lay)
    dr = ImageDraw.Draw(can, "RGBA")
    order = [("small_hammer", 9), ("far_leg", 7), ("far_arm", 7), ("spine", 7), ("near_leg", 7), ("big_hammer", 11),
             ("near_arm", 7)]
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
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Ornn",
           "--hide-submeshes", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900",
           "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work,
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
    ap.add_argument("--out", default="C:/t/on_work/ornn_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-league", action="store_true", help="skeletons only (for a look at them)")
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
        if not a.no_league:
            lol_frame(a.lol, clip, ms, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, clip, ms)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

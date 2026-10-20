#!/usr/bin/env python3
"""Gnar's pose pack for Codex (assets/source/gnar/POSE_PROMPTS.md): the key poses his rigged actions lack, which the
designs cannot give by whole-square moves (league_chogath's / league_graves's way; 2026-10-20 the user, after the rigged
actions: 「感觉大小纳尔少了点动作帧啊 要不要codex补啊」) - Mega Gnar crouches, lifts a fist, rears up with both fists over
his head and smashes them down (the punch, Wallop), heaves the boulder over his head, lunges in GNAR! and leaps in
Crunch; Mini Gnar winds up and flings the boomerang, hops and lands. The deaths stay rigged (approved).

    python tools/art/pack_gnar_poses.py [--out C:/t/gn_work/gnar_pose_pack] [--lol D:/WeGameApps/lol]

Mega poses are drawn on the approved SIDE design's grid (hd/m_side.png, 109 x 66: 10 px a square, soles on y 1180),
Mini poses on the approved 3/4 design's (hd/idle.png, 46 x 48: 20 px a square, soles on y 1180; the user: Mini only
3/4). Every pose is ONE 1254 picture. Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; per form
0_<form>_design_skeleton.png (the approved design on its grid with its own skeleton over it: what each line stands
for), 1_<form>_head.png (its head, 8x: every pose wears it), 2_<form>_design.png (the design on the grid, clean),
3_<form>_design_8x.png (the design at 8x: the thickness to keep); per pose <k>_<name>_skeleton.png (the grid, the
ground, the skeleton at the design's own segment lengths, a grey box where the head goes) and <k>_<name>_league.png
(League's frame for it: the pose to copy; Riot's, kept local).
Skeleton colours: green = spine and tail, RED = the NEAR legs (in front, full tone), BLUE = the FAR legs (behind,
darker), ORANGE = the NEAR arm, PURPLE = the FAR arm, GOLD = Mini's boomerang / Mega's boulder (a box), grey box = the
head (the design's head, never redrawn).
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
from design_gnar_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gnar")
CANVAS, SOLE_Y = 1254, 1180
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "near": (230, 30, 30), "far": (40, 90, 230), "near_a": (255, 140, 0),
       "far_a": (150, 60, 200), "prop": (215, 170, 0)}

# per form: design file, px a square, the design's (0, 0) on the canvas grid, head box (rows, cols) on the design,
# League's champion and camera
FORMS = {
    "mega": dict(design="m_side.png", px=10, dx=8, head=(12, 48, 78, 108), champ="GnarBig", yaw=80, width=2.2),
    "mini": dict(design="idle.png", px=20, dx=8, head=(0, 27, 6, 46), champ="Gnar", yaw=35, width=1.6),
}
for f in FORMS.values():
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f["design"]))).convert("RGBA"))
    f["W"], f["H"] = d.shape[1], d.shape[0]
    f["ground"] = SOLE_Y // f["px"]                     # the first row under the soles on the canvas grid
    f["dy"] = f["ground"] - f["H"]

# skeletons in DESIGN squares (x right, y down; the design's soles' bottom edge = its height): measured on the designs
REST = {
    "mega": dict(spine=[(30, 38), (68, 30)], tail=[(28, 36), (12, 30), (3, 19)],
                 near_hind=[(25, 40), (22, 50), (19, 58), (14, 60)], far_hind=[(35, 42), (37, 50), (41, 55), (47, 57)],
                 near_a=[(63, 28), (63, 45), (63, 62)], far_a=[(78, 40), (82, 50), (88, 59)], head=(93, 30)),
    "mini": dict(spine=[(28, 38), (28, 26)], tail=[(23, 37), (11, 31), (5, 21)],
                 near_leg=[(24, 39), (23, 43), (22, 47)], far_leg=[(33, 39), (34, 43), (35, 47)],
                 near_a=[(22, 30), (19, 35), (17, 39)], far_a=[(35, 30), (37, 35), (38, 39)],
                 prop=[(17, 39), (9, 43), (3, 45)], head=(26, 14)),
}
# the poses: (form, skeleton in design squares (soles' ground = the design's height), League's frame (clip, ms), what)
POSES = {
    "m_crouch": ("mega", dict(spine=[(32, 47), (70, 40)], tail=[(30, 46), (14, 44), (2, 36)],
                              near_hind=[(30, 48), (22, 55), (27, 62), (22, 65)],
                              far_hind=[(36, 49), (29, 57), (35, 63), (41, 65)],
                              near_a=[(66, 38), (60, 54), (75, 62)], far_a=[(72, 40), (80, 54), (94, 61)],
                              head=(90, 42)),
                ("gnarbig_spell3", 0), "蓄力：整个身子往下压、头缩回来贴近地面、两只大拳头收在胸前撑地、后腿弯着准备蹬（猛踏起跳前）"),
    "m_swing": ("mega", dict(spine=[(36, 46), (64, 20)], tail=[(33, 46), (17, 49), (4, 44)],
                             near_hind=[(34, 47), (28, 55), (30, 63), (25, 65)],
                             far_hind=[(40, 47), (43, 56), (41, 64), (47, 65)],
                             near_a=[(62, 22), (56, 6), (60, -11)], far_a=[(68, 24), (75, 40), (89, 48)],
                             head=(78, 22)),
               ("gnarbig_attack1", 200), "挥拳：上半身抬起一半、近侧的大拳头从头的后面高高举起准备往前砸、远侧的拳头从头下面往前伸（普攻）"),
    "m_rear": ("mega", dict(spine=[(42, 46), (46, 8)], tail=[(39, 48), (23, 54), (10, 61)],
                            near_hind=[(40, 47), (35, 56), (37, 64), (32, 65)],
                            far_hind=[(46, 47), (51, 56), (49, 64), (55, 65)],
                            near_a=[(46, 10), (49, -7), (55, -23)], far_a=[(44, 12), (37, -4), (39, -21)],
                            head=(63, 8)),
              ("gnarbig_spell2", 350), "直立：只用两条后腿站起来、身子竖直、头在胸口前面、两只大拳头从头的后面高高举过头顶（痛殴前一刻）、尾巴拖在地上"),
    "m_slam": ("mega", dict(spine=[(28, 36), (66, 32)], tail=[(25, 36), (12, 27), (4, 15)],
                            near_hind=[(26, 38), (17, 44), (9, 48), (4, 50)],
                            far_hind=[(32, 39), (24, 46), (17, 51), (12, 54)], near_a=[(64, 28), (66, 45), (68, 61)],
                            far_a=[(70, 32), (76, 47), (84, 61)], head=(86, 40)),
              ("gnarbig_spell2", 600), "下砸：整个身子往前压平、两只大拳头伸直一起砸在头下面的地上、后腿离地往后蹬、尾巴翘起（痛殴、普攻砸中）"),
    "m_lunge": ("mega", dict(spine=[(36, 46), (70, 24)], tail=[(33, 45), (17, 42), (4, 36)],
                             near_hind=[(34, 47), (26, 53), (19, 58), (14, 63)],
                             far_hind=[(40, 48), (34, 55), (28, 61), (24, 65)], near_a=[(66, 20), (72, 4), (88, -3)],
                             far_a=[(72, 28), (82, 42), (95, 53)], head=(86, 30)),
               ("gnarbig_spell4", 300), "前扑横扫：身子往前上方伸长、近侧的拳头从头顶上方往前挥出去、远侧的拳头从头下面往前伸、后腿蹬地、尾巴往后甩（呐啊！）"),
    "m_leap": ("mega", dict(spine=[(32, 24), (70, 18)], tail=[(29, 24), (14, 22), (3, 14)],
                            near_hind=[(30, 26), (37, 33), (31, 39), (36, 42)],
                            far_hind=[(36, 27), (43, 34), (37, 40), (43, 43)], near_a=[(66, 16), (64, 32), (74, 44)],
                            far_a=[(72, 20), (80, 34), (92, 44)], head=(88, 22)),
              ("gnarbig_spell3", 300), "跳在半空：整个身子离地很高（脚离地约 20 格）、后腿收在肚子下面、两只拳头从头下面往前下方准备砸地（猛踏的跳跃）"),
    "m_lift": ("mega", dict(spine=[(42, 46), (46, 8)], tail=[(39, 48), (23, 54), (10, 61)],
                            near_hind=[(40, 47), (35, 56), (37, 64), (32, 65)],
                            far_hind=[(46, 47), (51, 56), (49, 64), (55, 65)],
                            near_a=[(46, 10), (50, -7), (54, -23)], far_a=[(44, 12), (38, -4), (43, -21)],
                            head=(63, 8), prop=((49, -32), 22, 16)),
              ("gnarbig_spell1", 200), "举石：两条后腿站直、头在胸口前面、两只大拳头从头的后面举上去，一起把一块大石头（灰色，比他的头还小一点）举过头顶（投掷顽石）"),
    "a_windup": ("mini", dict(spine=[(28, 38), (26, 26)], tail=[(23, 37), (11, 32), (5, 22)],
                              near_leg=[(24, 39), (22, 43), (21, 47)], far_leg=[(32, 39), (34, 43), (36, 47)],
                              near_a=[(22, 30), (16, 32), (12, 30)], far_a=[(34, 30), (39, 33), (43, 35)],
                              prop=[(12, 30), (5, 26), (0, 20)], head=(24, 14)),
                ("gnar_attack1", 250), "蓄力：近侧的手（拿回力标那只）往后拉到身体后面（画面左边、头的下面），回力标往后上方翘在左耳旁边，身子微微后仰"),
    "a_throw": ("mini", dict(spine=[(29, 38), (31, 26)], tail=[(24, 37), (12, 34), (4, 28)],
                             near_leg=[(25, 39), (22, 42), (19, 46)], far_leg=[(33, 39), (36, 43), (38, 47)],
                             near_a=[(26, 29), (32, 30), (37, 31)], far_a=[(36, 30), (38, 35), (37, 39)],
                             head=(30, 14)),
               ("gnar_attack1", 450), "扔出：近侧的手往前（画面右边）甩直、手里空了（回力标已经扔出去）、身子往前倾、后腿蹬地"),
    "a_hop": ("mini", dict(spine=[(28, 29), (28, 17)], tail=[(23, 29), (12, 25), (5, 15)],
                           near_leg=[(24, 30), (27, 33), (24, 36)], far_leg=[(33, 30), (37, 32), (34, 35)],
                           near_a=[(22, 21), (16, 22), (11, 20)], far_a=[(34, 21), (39, 22), (43, 20)],
                           prop=[(11, 20), (3, 17), (-2, 13)], head=(27, 6)),
             ("gnar_spell3_jump", 300), "跳起：整个人离地（脚离地约 9 格）、膝盖收到肚子前、两只手往两边张开、尾巴翘起、回力标还在近侧的手里（轻跳）"),
    "a_crouch": ("mini", dict(spine=[(28, 41), (28, 29)], tail=[(23, 40), (11, 37), (4, 30)],
                              near_leg=[(24, 42), (19, 44), (21, 47)], far_leg=[(33, 42), (38, 44), (36, 47)],
                              near_a=[(22, 32), (16, 35), (12, 38)], far_a=[(34, 32), (39, 35), (43, 37)],
                              prop=[(12, 38), (4, 41), (-1, 42)], head=(26, 17)),
                ("gnar_spell1_catch", 300), "落地蹲下：膝盖弯着蹲低（身子比站着低 3 格）、两只手张开撑着平衡、回力标还在手里（落地、接回力标）"),
}


def canvas_grid(form):
    f = FORMS[form]
    px = f["px"]
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, px * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(215, 215, 215, 255))
    for y in range(0, CANVAS, px * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(215, 215, 215, 255))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    return can


def skeleton(can, form, sk, label, alpha=255):
    f = FORMS[form]
    px, dx, dy = f["px"], f["dx"], f["dy"]

    def c(p):
        return ((p[0] + dx) * px, (p[1] + dy) * px)
    dr = ImageDraw.Draw(can, "RGBA")
    r0, r1, c0, c1 = f["head"]
    hw, hh = c1 - c0, r1 - r0
    hx, hy = sk["head"]
    box = [c((hx - hw / 2, hy - hh / 2)), c((hx + hw / 2, hy + hh / 2))]
    dr.rectangle([box[0][0], box[0][1], box[1][0], box[1][1]], fill=(150, 150, 150, 70 if alpha < 255 else 120),
                 outline=(90, 90, 90, alpha), width=3)
    w = max(4, px // 2 + 2)
    legs = ("far_hind", "near_hind") if form == "mega" else ("far_leg", "near_leg")
    order = [("far_a", "far_a"), (legs[0], "far"), ("tail", "spine"), ("spine", "spine"), (legs[1], "near"),
             ("near_a", "near_a")]
    for name, key in order:
        pts = [c(p) for p in sk[name]]
        dr.line(pts, fill=COL[key] + (alpha,), width=w, joint="curve")
        for p in pts:
            dr.ellipse([p[0] - w, p[1] - w, p[0] + w, p[1] + w], fill=COL[key] + (alpha,))
    if "prop" in sk:
        if form == "mini":                               # the boomerang: a bent bone from the hand
            pts = [c(p) for p in sk["prop"]]
            dr.line(pts, fill=COL["prop"] + (alpha,), width=w + 2, joint="curve")
        else:                                            # the boulder: a box (centre, width, height)
            (bx, by), bw, bh = sk["prop"]
            a_, b_ = c((bx - bw / 2, by - bh / 2)), c((bx + bw / 2, by + bh / 2))
            dr.rectangle([a_[0], a_[1], b_[0], b_[1]], fill=COL["prop"] + (90,), outline=COL["prop"] + (alpha,),
                         width=4)
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    return can


def on_grid(form, d):
    f = FORMS[form]
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, f["px"])), (f["dx"] * f["px"], f["dy"] * f["px"]))
    return lay


def lol_frame(lol, form, clip, ms, work):
    f = FORMS[form]
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", f["champ"],
           "--wad", "Gnar", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900",
           "--fit", "0.3", "--ground", "0.8", "--width", str(f["width"]), "--yaw", str(f["yaw"]), "--name", "f",
           "--out", work, "--frame", f"{clip}@{ms}"]
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
    ap.add_argument("--out", default="C:/t/gn_work/gnar_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-league", action="store_true", help="skeletons only (no League renders)")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for form, f in FORMS.items():
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f["design"]))).convert("RGBA"))
        base = canvas_grid(form)
        base.alpha_composite(on_grid(form, d))
        clean = base.copy()
        skeleton(base, form, REST[form], f"0: the approved {form} design with its own skeleton (what each line stands for)",
                 200)
        base.convert("RGB").save(os.path.join(out, f"0_{form}_design_skeleton.png"))
        clean.convert("RGB").save(os.path.join(out, f"2_{form}_design.png"))
        r0, r1, c0, c1 = f["head"]
        big(d[r0:r1, c0:c1]).save(os.path.join(out, f"1_{form}_head.png"))
        big(d).save(os.path.join(out, f"3_{form}_design_8x.png"))
    for k, (name, (form, sk, (clip, ms), what)) in enumerate(POSES.items(), 4):
        can = canvas_grid(form)
        px = FORMS[form]["px"]
        skeleton(can, form, sk, f"{k}: {name} ({form}) - skeleton on the {px} px grid, red line = the ground "
                                f"(soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        if not a.no_league:
            lol_frame(a.lol, form, clip, ms, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(k, name, form, clip, ms)
    shutil.rmtree(out + "_work", ignore_errors=True)
    if os.path.isfile(lp(os.path.join(SRC, "POSE_PROMPTS.md"))):
        shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Gnar's pose pack for Codex (assets/source/gnar/POSE_PROMPTS.md): the poses his actions need that the designs cannot
give by whole-square moves (league_chogath's / league_graves's way) - Mega Gnar rears up on his hind legs and smashes
down in Wallop, heaves the boulder over his head, lunges in GNAR!, leaps in Crunch and collapses in the death; Mini Gnar
winds up and flings the boomerang, hops, lands and falls over.

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
    "m_crouch": ("mega", dict(spine=[(30, 44), (64, 38)], tail=[(28, 42), (14, 40), (4, 32)],
                              near_hind=[(25, 46), (19, 54), (18, 62), (13, 64)],
                              far_hind=[(35, 47), (35, 55), (39, 61), (45, 64)],
                              near_a=[(58, 36), (55, 50), (58, 64)], far_a=[(72, 44), (76, 54), (82, 64)], head=(86, 42)),
                 ("gnarbig_spell3", 100), "蓄力：整个身子往下压、头缩回来贴近地面、两只大拳头收在胸前撑地、后腿弯着准备蹬"),
    "m_swing": ("mega", dict(spine=[(34, 44), (60, 22)], tail=[(31, 44), (16, 48), (4, 44)],
                             near_hind=[(32, 46), (28, 55), (28, 63), (23, 66)],
                             far_hind=[(38, 46), (42, 55), (41, 63), (47, 66)],
                             near_a=[(58, 22), (56, 8), (62, -4)], far_a=[(66, 28), (78, 34), (88, 40)], head=(80, 24)),
                ("gnarbig_attack1", 200), "挥拳：上半身抬起一半、近侧的大拳头高高举起准备往前砸、远侧的拳头伸在前面（普攻）"),
    "m_rear": ("mega", dict(spine=[(40, 46), (48, 12)], tail=[(37, 48), (22, 56), (6, 62)],
                            near_hind=[(38, 47), (33, 56), (34, 63), (30, 66)],
                            far_hind=[(44, 47), (50, 56), (48, 63), (54, 66)],
                            near_a=[(50, 14), (60, 4), (66, -8)], far_a=[(45, 16), (36, 6), (32, -6)], head=(58, 6)),
               ("gnarbig_spell2", 350), "直立：只用两条后腿站起来、身子竖直、两只大拳头高高举过头顶（痛殴前一刻）、尾巴拖在地上"),
    "m_slam": ("mega", dict(spine=[(28, 36), (66, 46)], tail=[(25, 34), (14, 24), (5, 11)],
                            near_hind=[(26, 38), (20, 48), (14, 58), (8, 62)],
                            far_hind=[(31, 40), (27, 50), (23, 59), (17, 63)],
                            near_a=[(66, 42), (77, 54), (86, 64)], far_a=[(71, 44), (83, 56), (94, 64)], head=(84, 54)),
               ("gnarbig_spell2", 600), "下砸：整个身子往前扑下去、两只大拳头一起砸在前面的地上、头低到拳头后面、后腿往后蹬直、尾巴翘起"),
    "m_lunge": ("mega", dict(spine=[(26, 40), (70, 32)], tail=[(23, 38), (11, 33), (1, 26)],
                             near_hind=[(24, 42), (15, 52), (8, 60), (3, 63)],
                             far_hind=[(32, 43), (29, 52), (27, 60), (22, 64)],
                             near_a=[(70, 28), (86, 22), (102, 17)], far_a=[(77, 36), (91, 42), (104, 46)], head=(94, 30)),
                ("gnarbig_spell4", 300), "前扑横扫：身子往前伸长、两只大拳头往前上方挥出去、后腿蹬地伸直、尾巴往后甩（呐啊！把敌人掀飞）"),
    "m_leap": ("mega", dict(spine=[(30, 24), (68, 16)], tail=[(27, 22), (13, 21), (3, 12)],
                            near_hind=[(26, 26), (33, 34), (28, 40), (34, 43)],
                            far_hind=[(35, 28), (42, 36), (37, 42), (43, 45)],
                            near_a=[(64, 18), (72, 28), (80, 34)], far_a=[(76, 24), (84, 32), (92, 37)], head=(91, 18)),
               ("gnarbig_spell3", 300), "跳在半空：整个身子离地很高（脚离地约 20 格）、四肢收在身下、拳头往前下方准备砸地、尾巴往后（猛踏的跳跃）"),
    "m_lift": ("mega", dict(spine=[(40, 46), (46, 14)], tail=[(37, 48), (22, 56), (6, 62)],
                            near_hind=[(38, 47), (33, 56), (34, 63), (30, 66)],
                            far_hind=[(44, 47), (50, 56), (48, 63), (54, 66)],
                            near_a=[(48, 16), (54, 4), (52, -10)], far_a=[(44, 18), (40, 6), (42, -10)], head=(57, 8),
                            prop=((47, -19), 22, 16)),
               ("gnarbig_spell1", 200), "举石：两条后腿站直、两只大拳头一起把一块大石头（灰色，比他的头还大）举过头顶，准备往前扔"),
    "m_fall": ("mega", dict(spine=[(30, 52), (66, 52)], tail=[(27, 52), (14, 58), (2, 62)],
                            near_hind=[(26, 54), (20, 60), (14, 63), (9, 64)],
                            far_hind=[(34, 54), (38, 60), (44, 63), (49, 64)],
                            near_a=[(62, 50), (68, 58), (76, 64)], far_a=[(72, 54), (80, 60), (88, 64)], head=(86, 56)),
               ("gnarbig_death", 150), "瘫倒：四条腿都软下去、肚子贴在地上、头垂到地上、拳头往前摊开"),
    "m_lie": ("mega", dict(spine=[(26, 58), (70, 58)], tail=[(23, 58), (11, 62), (0, 64)],
                           near_hind=[(26, 60), (30, 52), (36, 48), (40, 46)],
                           far_hind=[(32, 58), (38, 54), (44, 52), (48, 50)],
                           near_a=[(66, 60), (72, 52), (80, 48)], far_a=[(70, 58), (78, 54), (86, 52)], head=(92, 56)),
              ("gnarbig_death", 260), "侧躺：整个身子侧着躺在地上（肚子朝外）、四条腿软软地朝外伸出来、尾巴平放在地上"),
    "a_windup": ("mini", dict(spine=[(27, 38), (25, 26)], tail=[(22, 37), (11, 32), (5, 22)],
                              near_leg=[(24, 39), (22, 43), (21, 47)], far_leg=[(32, 39), (34, 43), (36, 47)],
                              near_a=[(21, 29), (16, 24), (13, 18)], far_a=[(34, 30), (38, 33), (41, 35)],
                              prop=[(13, 18), (8, 12), (2, 10)], head=(24, 14)),
                 ("gnar_attack1", 250), "蓄力：近侧的手（拿回力标那只）往后上方举到头后面，回力标在头后面，身子微微后仰"),
    "a_throw": ("mini", dict(spine=[(29, 38), (31, 26)], tail=[(24, 37), (12, 34), (4, 28)],
                             near_leg=[(25, 39), (22, 43), (19, 47)], far_leg=[(33, 39), (36, 43), (39, 47)],
                             near_a=[(26, 29), (33, 31), (41, 32)], far_a=[(37, 30), (35, 35), (33, 38)], head=(30, 14)),
                ("gnar_attack1", 450), "扔出：近侧的手往前（画面右边）甩直、手里空了（回力标已经扔出去）、身子往前倾、后腿蹬地"),
    "a_hop": ("mini", dict(spine=[(28, 30), (28, 18)], tail=[(23, 29), (12, 26), (5, 16)],
                           near_leg=[(24, 31), (28, 35), (24, 38)], far_leg=[(33, 31), (37, 34), (34, 37)],
                           near_a=[(22, 22), (16, 18), (12, 14)], far_a=[(35, 22), (40, 18), (43, 14)],
                           prop=[(12, 14), (8, 8), (3, 6)], head=(27, 6)),
              ("gnar_spell3_jump", 300), "跳起：整个人离地（脚离地约 9 格）、膝盖收到肚子前、两只手张开往上、尾巴翘起（轻跳）"),
    "a_crouch": ("mini", dict(spine=[(28, 41), (28, 30)], tail=[(23, 40), (11, 37), (4, 30)],
                              near_leg=[(24, 42), (19, 45), (21, 47)], far_leg=[(33, 42), (38, 45), (36, 47)],
                              near_a=[(22, 33), (17, 37), (15, 41)], far_a=[(35, 33), (40, 37), (42, 41)],
                              prop=[(15, 41), (8, 44), (2, 45)], head=(26, 18)),
                 ("gnar_spell1_catch", 300), "落地蹲下：膝盖弯着蹲低（身子比站着低 3 格）、两只手张开撑着平衡（落地、接回力标）"),
    "a_fall": ("mini", dict(spine=[(24, 44), (19, 34)], tail=[(20, 44), (10, 46), (2, 44)],
                            near_leg=[(26, 44), (31, 41), (35, 37)], far_leg=[(30, 45), (35, 43), (40, 41)],
                            near_a=[(18, 36), (12, 40), (8, 44)], far_a=[(22, 35), (28, 38), (32, 41)], head=(16, 24)),
               ("gnar_death", 400), "往后倒：一屁股坐倒、身子往后仰、两条腿抬起来、两只手往后撑、回力标脱手"),
    "a_lie": ("mini", dict(spine=[(30, 45), (18, 45)], tail=[(32, 45), (40, 44), (46, 41)],
                           near_leg=[(30, 46), (35, 46), (40, 47)], far_leg=[(31, 45), (36, 44), (41, 45)],
                           near_a=[(19, 46), (14, 47), (10, 47)], far_a=[(21, 45), (25, 46), (28, 47)], head=(10, 37)),
              ("gnar_death", 1200), "趴倒：整个人趴在地上（肚子贴地）、头在画面左边侧着贴地、两条腿和尾巴往右平放在地上、两只手摊在地上"),
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

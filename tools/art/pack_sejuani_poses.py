#!/usr/bin/env python3
"""Sejuani's pose pack for Codex (assets/source/sejuani/POSE_PROMPTS.md): the whole-body poses her League clips go
through (the user, 2026-10-24: 「Codex 照骨架画」, pack_nunu_poses.py's way).

    python tools/art/pack_sejuani_poses.py [--out C:/t/se_work/sejuani_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, the lowest hoof on y SOLE_Y - the design hd/idle.png (the redraw's
A-2, 82 x 72, PPU 2.0) sits at squares (DX + shift, DY) on it. Two bodies, one figure (Nunu & Willump's way):
  * BRISTLE (the boar): his spine (the hip to the shoulder), four legs (hip / knee / ankle / hoof tip), his HEAD BOX (the
    head, the mane's front, the tusks) pasted on the shoulder, never turned;
  * SEJUANI: her spine (the hips in the saddle to the base of the neck) riding on Bristle's back (the saddle point is
    turned with his spine), her HEAD BOX (the helm, the ice horns, the face, the blonde locks) on her neck, her two arms
    (shoulder / elbow / wrist / fist), the FLAIL (a prop like Nunu's snowball: the chain from her near fist in three
    links, the ice head a disc at its end).
The skeletons are set by hand after League's frames (tools/lol/pose_ref.py at the 3/4 camera): every bone at the
design's OWN length (measured on hd/idle.png at 12x: REST), only its direction set per pose (POSES), the lowest hoof on
the ground unless the pose lifts it. The run poses are ridden like the run design hd/run.png (the redraw's B-1).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_heads.png (her head box and Bristle's, 8x: every pose wears them); 2_design.png and 2_run_design.png (the two designs
on the grid); per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's,
kept local).
--check DIR: each skeleton beside League's frame (nothing else written).
Skeleton colours: GREEN = Bristle's spine, RED = his NEAR legs (image left: the near hind and near front), BLUE = his FAR
legs, TEAL = Sejuani's spine, ORANGE = her NEAR arm (the flail arm, image left in the design), PURPLE = her FAR arm,
BROWN = the flail's chain, a light blue disc = its ice head; grey boxes = the two head boxes (hers small, his big).
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
from design_sejuani_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_nunu_poses import along, ang, bend, turned  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sejuani")
PX, CANVAS, SOLE_Y = 11, 1254, 1188
GREY = (225, 225, 225)
GROUND = 72                          # the design's hooves' bottom edge (rows)
DX, DY = 16, SOLE_Y // PX - GROUND    # the design's (0, 0) on the canvas grid (its hooves on row 108)
COL = {"b_spine": (0, 170, 60), "near_hind": (230, 30, 30), "near_front": (230, 30, 30), "far_hind": (40, 90, 230),
       "far_front": (40, 90, 230), "r_spine": (0, 160, 170), "near_arm": (255, 140, 0), "far_arm": (150, 60, 200),
       "chain": (120, 75, 35)}
ICE = (150, 210, 255)
R_HEAD = (1, 25, 31, 63)       # rows / columns of her head box in hd/idle.png: the helm, both ice horns, the face, the locks
B_HEAD = (38, 72, 56, 82)      # rows / columns of Bristle's head box: the ear, the eye, the snout, the tusks, the mane's front
R_FACE = (43, 55, 14, 24)      # her face (eyes to mouth): x0, x1, y0, y1
ICE_R = 6.0                    # the flail's ice head, as a disc

# the design's own skeleton, measured on hd/idle.png (82 x 72, square edges)
REST = {
    "b_spine": [(20.0, 52.0), (55.0, 51.0)],
    "near_hind": [(18.0, 54.0), (15.0, 60.0), (16.0, 66.0), (18.0, 70.0)],
    "far_hind": [(26.0, 55.0), (28.0, 61.0), (26.0, 66.0), (25.0, 70.0)],
    "near_front": [(40.0, 55.0), (37.0, 61.0), (36.0, 66.0), (38.0, 70.0)],
    "far_front": [(48.0, 55.0), (49.0, 61.0), (46.0, 66.0), (43.0, 70.0)],
    "r_spine": [(43.0, 37.0), (48.0, 25.0)],
    "near_arm": [(38.0, 27.0), (27.0, 27.0), (17.0, 27.0), (14.0, 28.0)],
    "far_arm": [(57.0, 28.0), (61.0, 32.0), (63.0, 36.0), (62.0, 38.0)],
    "chain": [(14.0, 28.0), (10.0, 36.0), (9.0, 43.0), (7.0, 49.0)],
}
REST_HEADS = {"r_head": ((R_HEAD[2] + R_HEAD[3]) / 2, (R_HEAD[0] + R_HEAD[1]) / 2),
              "b_head": ((B_HEAD[2] + B_HEAD[3]) / 2, (B_HEAD[0] + B_HEAD[1]) / 2)}
RHW, RHH = R_HEAD[3] - R_HEAD[2], R_HEAD[1] - R_HEAD[0]
BHW, BHH = B_HEAD[3] - B_HEAD[2], B_HEAD[1] - B_HEAD[0]
LEGS = ("near_hind", "far_hind", "near_front", "far_front")

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton).
# The skeleton: "hip" (Bristle's hip, design squares), "b_spine" (his spine's direction: 0 straight down, 90 to the image
# right, 180 up, -90 to the image left), each leg "rest", three angles, or (target, side, last angle) - the ankle at the
# target with the knee solved (side -1 bends a downward limb's knee to the image right, +1 to the image left), then the
# hoof at the last angle; "r_spine" (her spine's direction), "rider" (her hips at a design point instead of the saddle:
# thrown off), "near_arm" / "far_arm" "rest" or three angles, "chain" three angles (the ice head follows the last);
# "b_head" / "r_head" (squares the head box is moved from where the neck puts it); "lift" (rows the lowest point is off
# the ground; None: on it); "shift" (squares the whole figure is moved on the canvas).
STAND = dict(hip=(20.0, 52.0), b_spine=ang(*REST["b_spine"]), near_hind="rest", far_hind="rest", near_front="rest",
             far_front="rest", lift=None, shift=0)
POSES = {
    "a_wind": ("sejuani_2013_attack1@300",
               "甩到身后：钢鬃站稳不动；瑟庄妮身子往后仰，近侧（画面左边）的手臂往左后方抡开，链枷被甩到钢鬃屁股后面、冰锤头低低地拖在左后方（普攻起手）",
               "WIND-UP - the boar standing still; the woman leaning back, her NEAR arm (image left) swung out back to the "
               "image left, the flail flung behind the boar's rump, its ice head low at the back on the image left.",
               dict(STAND, r_spine=178, near_arm=(-95, -110, -120), far_arm="rest", chain=(-40, -25, -10))),
    "a_smash": ("sejuani_2013_attack1@457",
                "抽出：瑟庄妮身子往前（画面右边）压，近侧手臂往前伸，**链枷从身后抡上来往前抽直**，冰锤头甩到钢鬃头的右前上方、比她肩膀稍高（普攻打中）",
                "LASH - the woman lunging forward to the image right, her NEAR arm reaching forward, the flail whipped up "
                "from behind and LASHED STRAIGHT OUT forward, its ice head far in front of and above the boar's head, a "
                "little higher than her shoulder.",
                dict(STAND, r_spine=140, near_arm=(105, 100, 98), far_arm="rest", chain=(105, 112, 118), shift=-8)),
    "q_toss": ("sejuani_2013_spell1_hit@300",
               "撞飞上挑：钢鬃冲到头猛地抬头，**獠牙往上一挑**（头框往上抬），前腿离地收起，后腿蹬地；瑟庄妮压低身子抓紧，链枷甩在身后（极寒突袭：撞上把敌人挑飞）",
               "TUSK TOSS - the boar at the end of its charge throwing its head UP, the TUSKS flicking upward, its front legs "
               "off the ground and tucked, the hind legs pushing; the woman crouched low holding on, the flail flying behind.",
               dict(STAND, hip=(18.0, 52.0), b_spine=100, near_front=(110, 10, 80), far_front=(105, 5, 75),
                    near_hind=((14.0, 70.0), 1, -60), far_hind=((22.0, 70.0), 1, -60), b_head=(4, -3),
                    r_spine=140, near_arm=(-120, -135, -150), far_arm="rest", chain=(-110, -95, -80))),
    "w_sweep": ("sejuani_spell2_a_0@248",
                "横扫：瑟庄妮身子扭向右边，近侧手臂往前伸平，**链枷拉直往右横着扫出去**（冰锤头在钢鬃头的右前方、和她肩膀差不多高）（凛冬之怒：第一下）",
                "SWEEP - the woman twisting to the image right, her NEAR arm stretched straight forward, the flail pulled "
                "STRAIGHT OUT to the right in a level sweep, its ice head far in front of the boar's head at about her "
                "shoulder height.",
                dict(STAND, r_spine=120, near_arm=(95, 92, 90), far_arm="rest", chain=(92, 95, 98), shift=-10)),
    "w_raise": ("sejuani_spell2_b_0@200",
                "举高：瑟庄妮挺直身子，近侧手臂高高举过头顶，**链枷甩到头顶上方往后弯**，冰锤头在她头的左上方（凛冬之怒：第二下抡起）",
                "RAISE - the woman sitting up straight, her NEAR arm raised high above her head, the flail swung up OVER her "
                "head and curling back, its ice head above her on the upper left.",
                dict(STAND, r_spine=170, near_arm=(170, 175, 180), far_arm="rest", chain=(-160, -130, -110))),
    "w_slam": ("sejuani_spell2_b_0@250",
               "猛砸：瑟庄妮整个身子往前扑，近侧手臂往前下方砸到底，**链枷甩直、冰锤头重重砸在钢鬃前方很远的地上**（凛冬之怒：往前砸一条线）",
               "SLAM - the woman throwing her whole body forward, her NEAR arm swung all the way down and forward, the flail "
               "stretched straight, its ice head crashing onto the ground FAR in front of the boar.",
               dict(STAND, r_spine=125, near_arm=(80, 65, 55), far_arm="rest", chain=(60, 50, 40))),
    "r_wind": ("sejuani_2013_spell4@125",
               "举起套索：瑟庄妮挺身，近侧手臂举到头顶，**链枷在头顶上方抡圈**（冰锤头在她头的右上方）（极冰寒狱：甩之前）",
               "WIND THE BOLA - the woman sitting up, her NEAR arm raised above her head, whirling the flail in a circle "
               "OVER her head, its ice head up on the upper right.",
               dict(STAND, r_spine=165, near_arm=(165, 150, 135), far_arm="rest", chain=(120, 100, 80))),
    "r_throw": ("sejuani_2013_spell4@330",
                "甩出：瑟庄妮身子往前送，**近侧手臂往前（画面右边）伸直，刚把套索甩出去**（手张开），链枷垂在手下面晃（极冰寒狱：扔出）",
                "THROW - the woman leaning forward, her NEAR arm thrust straight forward to the image right, the hand open "
                "having just flung the bola; the flail hanging down from her hand, swinging.",
                dict(STAND, r_spine=130, near_arm=(95, 90, 88), far_arm="rest", chain=(15, 5, -5))),
    "run1": ("sejuani_2013_run@0",
             "跑 1（伸展）：钢鬃往前奔，**两条前腿往前伸、两条后腿往后蹬**，身子拉长、离地 1 格；瑟庄妮压低身子，链枷扬在身后（和跑步定稿 `2_run_design.png` 一样骑法）",
             "RUN 1 (STRETCHED) - the boar galloping to the image right, BOTH FRONT LEGS reaching forward and BOTH HIND "
             "LEGS kicking back, its body long and one square off the ground; the woman crouched low, the flail raised "
             "behind her (ridden like the run design).",
             dict(STAND, b_spine=95, near_front=(55, 40, 60), far_front=(48, 35, 55), near_hind=(-55, -40, -60),
                  far_hind=(-48, -35, -55), lift=1, r_spine=140, near_arm=(-150, -165, -175), far_arm="rest",
                  chain=(-120, -100, -85))),
    "run2": ("sejuani_2013_run@490",
             "跑 2（前脚着地）：前腿落地撑住，后腿往前收到身子下面，身子往前倾一点；瑟庄妮随着往前压",
             "RUN 2 (FRONT LANDING) - the front legs landing and bracing under the chest, the hind legs swinging forward "
             "under the body, leaning forward a little; the woman pressing forward with it.",
             dict(STAND, b_spine=100, near_front=((40.0, 70.0), -1, 60), far_front=((46.0, 70.0), -1, 60),
                  near_hind=(25, 10, 30), far_hind=(20, 5, 30), r_spine=138, near_arm=(-150, -165, -175),
                  far_arm="rest", chain=(-125, -105, -90))),
    "run3": ("sejuani_2013_run@980",
             "跑 3（收拢）：四条腿都收在身子下面，后腿着地、前腿抬起，身子弓起来高 1 格；瑟庄妮微微抬身",
             "RUN 3 (GATHERED) - all four legs gathered under the body, the hind legs on the ground, the front legs "
             "lifted and tucked, the back arched one square higher; the woman rising a little.",
             dict(STAND, b_spine=85, near_front=(100, 10, 80), far_front=(95, 5, 75), near_hind=((26.0, 70.0), -1, 50),
                  far_hind=((30.0, 70.0), -1, 50), r_spine=145, near_arm=(-150, -165, -175), far_arm="rest",
                  chain=(-115, -95, -80))),
    "run4": ("sejuani_2013_run@1475",
             "跑 4（后腿蹬地）：后腿用力往后蹬，前腿往前伸准备落地，身子前倾；瑟庄妮压低",
             "RUN 4 (PUSH-OFF) - the hind legs pushing hard back, the front legs reaching forward to land, the body "
             "tilted forward; the woman crouched low.",
             dict(STAND, b_spine=100, near_front=(60, 45, 50), far_front=(55, 40, 45), near_hind=((12.0, 70.0), 1, -70),
                  far_hind=((18.0, 70.0), 1, -70), r_spine=138, near_arm=(-150, -165, -175), far_arm="rest",
                  chain=(-125, -105, -90))),
    "d_rear": ("sejuani_2013_death@424",
               "人立：钢鬃痛得**后腿站起来、前腿在空中乱蹬**，头往上仰；瑟庄妮被甩得往后（画面左边）仰倒、快从背上掉下去，链枷脱手往后飞（死亡第一下）",
               "REARING - the boar rearing up on its HIND LEGS in pain, the front legs pawing the air, its head thrown "
               "up; the woman thrown back to the image left, falling off its back, the flail slipping from her hand.",
               dict(STAND, hip=(24.0, 56.0), b_spine=150, near_hind=((20.0, 70.0), 1, -20), far_hind=((27.0, 70.0), -1, 20),
                    near_front=(150, 120, 100), far_front=(160, 130, 110), b_head=(0, -3),
                    r_spine=-150, near_arm=(-160, -170, -175), far_arm=(150, 160, 170), chain=(-60, -40, -20))),
    "d_down": ("sejuani_2013_death@2960",
               "倒地：钢鬃**侧身倒在地上**（肚子朝画面外，四条腿往画面右边伸着），眼睛闭上（画成一道线）；瑟庄妮摔在钢鬃左边的地上，链枷落在她身边（死亡）",
               "DOWN - the boar lying on its side on the ground, its four legs stretched out to the image right, its eye "
               "closed (drawn as a line); the woman fallen on the ground on its left, the flail lying beside her.",
               dict(STAND, hip=(32.0, 64.0), b_spine=90, near_hind=(75, 80, 85), far_hind=(70, 75, 80),
                    near_front=(80, 85, 90), far_front=(75, 80, 85), b_head=(2, 6),
                    rider=(24.0, 68.0), r_spine=-95, near_arm=(-20, -10, 0), far_arm=(20, 10, 0),
                    chain=(120, 100, 90), shift=2)),
}


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def limb(base, base_rest, name, sp, turn):
    """A limb from where the turned rest puts its root: "rest", three angles, or (target, side, last)."""
    if sp == "rest":
        return [(base[0] + o[0], base[1] + o[1]) for o in
                (turned((x - base_rest[0], y - base_rest[1]), turn) for x, y in REST[name])]
    off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn)
    pts = [(base[0] + off[0], base[1] + off[1])]
    ls = lengths(name)
    if len(sp) == 3 and isinstance(sp[0], tuple):
        target, side, last = sp
        M, A = bend(pts[0], target, ls[0], ls[1], side)
        return pts + [M, A, along(A, last, ls[2])]
    for a_, l_ in zip(sp, ls):
        pts.append(along(pts[-1], a_, l_))
    return pts


def build(spec):
    """A skeleton from a pose spec (design squares): Bristle from his hip, Sejuani from the saddle point on his back (or
    `rider`), the head boxes upright on the necks, the flail from her near fist; then the lowest point on the ground
    (or `lift` rows over it)."""
    bs = REST["b_spine"]
    bturn = (spec["b_spine"] - ang(bs[0], bs[1]) + 180.0) % 360.0 - 180.0
    hip = spec["hip"]
    shoulder = along(hip, spec["b_spine"], lengths("b_spine")[0])
    sk = {"b_spine": [hip, shoulder]}
    for name in LEGS:
        root, rroot = (hip, bs[0]) if "hind" in name else (shoulder, bs[1])
        sk[name] = limb(root, rroot, name, spec[name], bturn)
    bh = REST_HEADS["b_head"]
    boff = turned((bh[0] - bs[1][0], bh[1] - bs[1][1]), bturn * 0.5)
    db = spec.get("b_head", (0, 0))
    sk["b_head"] = (shoulder[0] + boff[0] + db[0], shoulder[1] + boff[1] + db[1])
    rs = REST["r_spine"]
    if "rider" in spec:
        seat = spec["rider"]
    else:
        so = turned((rs[0][0] - bs[0][0], rs[0][1] - bs[0][1]), bturn)
        seat = (hip[0] + so[0], hip[1] + so[1])
    rturn = (spec["r_spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    neck = along(seat, spec["r_spine"], lengths("r_spine")[0])
    sk["r_spine"] = [seat, neck]
    for name in ("near_arm", "far_arm"):
        sk[name] = limb(neck, rs[1], name, spec[name], rturn)
    rh = REST_HEADS["r_head"]
    dr = spec.get("r_head", (0, 0))
    sk["r_head"] = (neck[0] + rh[0] - rs[1][0] + dr[0], neck[1] + rh[1] - rs[1][1] + dr[1])
    fist = sk["near_arm"][-1]
    chain = [fist]
    for a_, l_ in zip(spec["chain"], lengths("chain")):
        chain.append(along(chain[-1], a_, l_))
    sk["chain"] = chain
    sk["ice"] = along(chain[-1], spec["chain"][-1], ICE_R)
    # the lowest point: a hoof, the ice head's bottom or Bristle's head box (his tusks reach the ground in the design)
    low = max([y for k in LEGS + ("b_spine", "r_spine", "near_arm", "far_arm", "chain") for _, y in sk[k]]
              + [sk["ice"][1] + ICE_R, sk["b_head"][1] + BHH / 2])
    dy = GROUND - (spec["lift"] or 0) - low
    return {k: ((v[0], v[1] + dy) if k in ("r_head", "b_head", "ice") else [(x, y + dy) for x, y in v])
            for k, v in sk.items()}


def to_canvas(sk, shift=0):
    return {k: ((v[0] + DX + shift, v[1] + DY) if k in ("r_head", "b_head", "ice")
                else [(x + DX + shift, y + DY) for x, y in v]) for k, v in sk.items()}


def canvas_grid():
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(215, 215, 215, 255))
    for y in range(SOLE_Y % (PX * 5), CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(215, 215, 215, 255))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    return can


def c(p):
    return (p[0] * PX, p[1] * PX)


def skeleton(can, s, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    for key, w, h in (("b_head", BHW, BHH), ("r_head", RHW, RHH)):
        hx, hy = s[key]
        dr.rectangle([(hx - w / 2) * PX, (hy - h / 2) * PX, (hx + w / 2) * PX, (hy + h / 2) * PX],
                     fill=(150, 150, 150, 70 if alpha < 255 else 90), outline=(90, 90, 90, alpha), width=3)
    ix, iy = s["ice"]
    dr.ellipse([(ix - ICE_R) * PX, (iy - ICE_R) * PX, (ix + ICE_R) * PX, (iy + ICE_R) * PX],
               fill=ICE + (150,), outline=(60, 120, 200, alpha), width=4)
    for name in ("far_hind", "far_front", "b_spine", "near_hind", "near_front", "far_arm", "r_spine", "chain",
                 "near_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=5 if name == "chain" else 7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == 3 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work, yaw=35):
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Sejuani",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--fit-all",
           "--size", "900", "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", str(yaw), "--name", "f",
           "--out", work, "--frame", frame]
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


def poses_built():
    return {name: (to_canvas(build(spec), spec.get("shift", 0)), frame, zh, en)
            for name, (frame, zh, en, spec) in POSES.items()}


def problems(name, s):
    """Every bone, both head boxes and the ice head on the canvas; no fist or ice head over her face."""
    out = []
    pts = [p for k in LEGS + ("b_spine", "r_spine", "near_arm", "far_arm", "chain") for p in s[k]] + [s["ice"]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    for key, w, h in (("r_head", RHW, RHH), ("b_head", BHW, BHH)):
        hx, hy = s[key]
        if hy - h / 2 < 1 or hx - w / 2 < 0 or hx + w / 2 > CANVAS / PX:
            out.append(f"{key} off the canvas")
    hx, hy = s["r_head"]
    ox, oy = hx - RHW / 2 - R_HEAD[2], hy - RHH / 2 - R_HEAD[0]
    fx0, fx1, fy0, fy1 = R_FACE[0] + ox, R_FACE[1] + ox, R_FACE[2] + oy, R_FACE[3] + oy
    over = [p for p in s["near_arm"][2:] + s["far_arm"][2:] + [s["ice"]] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if over:
        out.append(f"over her face at {[(round(x), round(y)) for x, y in over[:3]]}")
    return out


def tile_sheet(tiles, path, cols=3):
    W = max(t.width for t in tiles)
    H = max(t.height for t in tiles)
    rows_ = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows_), (255, 255, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * W, (k // cols) * H))
    sheet.save(path)


def paste_heads(can, s, idle):
    r0, r1, c0, c1 = R_HEAD
    b0, b1, d0, d1 = B_HEAD
    for key, (y0, y1, x0, x1), w, h in (("b_head", (b0, b1, d0, d1), BHW, BHH), ("r_head", (r0, r1, c0, c1), RHW, RHH)):
        hx, hy = s[key]
        can.alpha_composite(Image.fromarray(up(idle[y0:y1, x0:x1], PX)),
                            (round((hx - w / 2) * PX), round((hy - h / 2) * PX)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/se_work/sejuani_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    run = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "run.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(STAND, r_spine=ang(*REST["r_spine"]), near_arm="rest", far_arm="rest",
                                chain=[ang(REST["chain"][i], REST["chain"][i + 1]) for i in range(3)])))
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        base = canvas_grid()
        base.alpha_composite(on_grid(idle, DX, DY))
        skeleton(base, rest, "the design's own skeleton (REST)", 200)
        base.convert("RGB").save(os.path.join(a.check, "rest_check.png"))
        names = a.only.split(",") if a.only else list(poses)
        cache = os.path.join(a.check, "_league")
        os.makedirs(cache, exist_ok=True)
        tiles = []
        for name in names:
            s, frame, zh, en = poses[name]
            can = canvas_grid()
            paste_heads(can, s, idle)
            skeleton(can, s, name)
            fpath = os.path.join(cache, name + ".png")
            if not os.path.isfile(fpath):
                lol_frame(a.lol, frame, os.path.join(a.check, "_work")).save(fpath)
            lf = Image.open(fpath).convert("RGB")
            sk = can.convert("RGB").resize((CANVAS * 2 // 5, CANVAS * 2 // 5))
            lf = lf.resize((round(lf.width * sk.height / lf.height), sk.height))
            t = Image.new("RGB", (sk.width + lf.width, sk.height), (255, 255, 255))
            t.paste(sk, (0, 0))
            t.paste(lf, (sk.width, 0))
            tiles.append(t)
        tile_sheet(tiles, os.path.join(a.check, "poses_check.png"))
        shutil.rmtree(os.path.join(a.check, "_work"), ignore_errors=True)
        return
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    base = canvas_grid()
    base.alpha_composite(on_grid(idle, DX, DY))
    clean = base.copy()
    skeleton(base, rest, "0: the approved design with its own skeleton (what each coloured line stands for)", 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    rcan = canvas_grid()
    rcan.alpha_composite(on_grid(run, DX, SOLE_Y // PX - run.shape[0]))
    rcan.convert("RGB").save(os.path.join(out, "2_run_design.png"))
    r0, r1, c0, c1 = R_HEAD
    b0, b1, d0, d1 = B_HEAD
    rh, bh = big(idle[r0:r1, c0:c1]), big(idle[b0:b1, d0:d1])
    heads = Image.new("RGB", (rh.width + bh.width + 40, max(rh.height, bh.height)), (255, 255, 255))
    heads.paste(rh, (0, 0))
    heads.paste(bh, (rh.width + 40, 0))
    heads.save(os.path.join(out, "1_heads.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (lowest hoof on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

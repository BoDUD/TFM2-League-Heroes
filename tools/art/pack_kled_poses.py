#!/usr/bin/env python3
"""Kled's pose pack for Codex (assets/source/kled/POSE_PROMPTS.md): the whole-body poses his League clips go through,
mounted on Skaarl and on foot (the user, 2026-10-24: 「Codex 照骨架画」, pack_sejuani_poses.py's way).

    python tools/art/pack_kled_poses.py [--out C:/t/kl_work/kled_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, the lowest point on y SOLE_Y. Two designs, one scale (PPU 2.0):
  * MOUNTED on hd/idle.png (A-1, 63 x 80): SKAARL - his spine (the hip to the base of the neck; he walks upright), two
    legs (hip / knee / ankle / toe), the tail (four points), his HEAD BOX (the spines, the big eye, the mouth) on the neck,
    never turned; KLED - his spine (the seat in the saddle to the base of the neck) riding on Skaarl's back (the seat
    turns with Skaarl's spine), his HEAD BOX (the hat and spike, both ears, the face, the beard) on his neck, two arms
    (shoulder / elbow / wrist / fist), the hand AXE in his near fist (a line to its blade, a disc), the ROPE from his far
    fist (three links) with the BEAR TRAP (a disc) at its end;
  * ON FOOT on hd/foot.png (B-1 under A-1's head, 58 x 60): KLED alone - his spine (hips to neck), two legs, two arms,
    the same HEAD BOX, the big two-handed AXE from his near fist (a line to its blades, a disc).
The skeletons are set by hand after League's frames (tools/lol/pose_ref.py at the 3/4 camera; the mounted model Kled,
the on-foot one KledRider in the same WAD): every bone at the design's OWN length (measured on the designs at 11x:
REST_M / REST_F), only its direction set per pose (POSES), the lowest point on the ground unless the pose lifts it.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_mounted_skeleton.png / 0_foot_skeleton.png (each design on the grid
with its own skeleton); 1_heads.png (Kled's head box and Skaarl's, 8x: every pose wears them); 2_design.png /
2_foot_design.png (the two designs on the grid); per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's
frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton (with the heads pasted) beside League's frame (nothing else written).
Skeleton colours: GREEN = Skaarl's spine, RED = his NEAR leg (image left), BLUE = his FAR leg, YELLOW = his tail, TEAL =
Kled's spine, ORANGE = Kled's NEAR arm (the axe arm, image left in the designs), PURPLE = his FAR arm, GREY-BLUE = the
axe's haft and a steel disc its blade, BROWN = the rope and a dark disc the bear trap; on foot DARK RED = his near leg,
NAVY = his far leg; grey boxes = the head boxes (Kled's, Skaarl's).
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
from design_kled_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_nunu_poses import along, ang, bend, turned  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kled")
PX, CANVAS, SOLE_Y = 11, 1254, 1188
GREY = (225, 225, 225)
COL = {"s_spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "tail": (235, 190, 0),
       "k_spine": (0, 160, 170), "near_arm": (255, 140, 0), "far_arm": (150, 60, 200), "axe": (110, 130, 160),
       "rope": (120, 75, 35), "f_near_leg": (150, 20, 40), "f_far_leg": (30, 40, 120)}
STEEL, TRAP = (200, 210, 225), (70, 70, 80)

# ---------------------------------------------------------------------- the mounted design (hd/idle.png, 63 x 80)
GROUND_M = 80
DX_M = 22
K_HEAD_M = (0, 39, 3, 43)      # rows / columns of Kled's head box in hd/idle.png: spike, hat, both ears, face, beard
S_HEAD = (40, 59, 28, 52)      # Skaarl's head box: the teal spines, the big eye, the mouth
K_FACE_M = (24, 40, 20, 34)    # Kled's face (both eyes to the grin): x0, x1, y0, y1
AXE_R, AXE_R_F, TRAP_R = 5.0, 9.0, 4.0
REST_M = {
    "s_spine": [(30.0, 65.0), (37.0, 51.0)],
    "near_leg": [(22.0, 65.0), (16.0, 70.0), (15.0, 74.0), (13.0, 79.0)],
    "far_leg": [(37.0, 66.0), (36.0, 70.0), (37.0, 74.0), (41.0, 79.0)],
    "tail": [(24.0, 63.0), (16.0, 63.0), (10.0, 62.0), (4.0, 59.0)],
    "k_spine": [(25.0, 47.0), (30.0, 38.0)],
    "near_arm": [(23.0, 40.0), (18.0, 41.0), (13.0, 40.0), (11.0, 39.0)],
    "far_arm": [(37.0, 38.0), (42.0, 35.0), (46.0, 32.0), (47.0, 30.0)],
    "axe": [(11.0, 39.0), (6.0, 41.0)],
    "rope": [(47.0, 31.0), (51.0, 40.0), (53.0, 46.0), (55.0, 51.0)],
}
# ---------------------------------------------------------------------- the on-foot design (hd/foot.png, 58 x 60)
GROUND_F = 60
DX_F = 30
K_HEAD_F = (0, 38, 0, 40)      # the same head (A-1's, pasted), on hd/foot.png
K_FACE_F = (16, 32, 18, 32)
REST_F = {
    "f_spine": [(22.0, 48.0), (23.0, 38.0)],
    "f_near_leg": [(19.0, 48.0), (16.0, 52.0), (13.0, 57.0), (11.0, 60.0)],
    "f_far_leg": [(27.0, 48.0), (29.0, 53.0), (30.0, 57.0), (33.0, 60.0)],
    "f_near_arm": [(15.0, 39.0), (13.0, 43.0), (16.0, 45.0), (18.0, 45.0)],
    "f_far_arm": [(29.0, 39.0), (31.0, 42.0), (33.0, 42.0), (34.0, 41.0)],
    "f_axe": [(18.0, 45.0), (46.0, 40.0)],
}


def lengths(rest, name):
    pts = rest[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def angles(rest, name):
    pts = rest[name]
    return tuple(ang(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def limb(rest, base, base_rest, name, sp, turn):
    """A limb from where the turned rest puts its root: "rest", angles, or (target, side, last)."""
    if sp == "rest":
        return [(base[0] + o[0], base[1] + o[1]) for o in
                (turned((x - base_rest[0], y - base_rest[1]), turn) for x, y in rest[name])]
    off = turned((rest[name][0][0] - base_rest[0], rest[name][0][1] - base_rest[1]), turn)
    pts = [(base[0] + off[0], base[1] + off[1])]
    ls = lengths(rest, name)
    if len(sp) == 3 and isinstance(sp[0], tuple):
        target, side, last = sp
        M, A = bend(pts[0], target, ls[0], ls[1], side)
        return pts + [M, A, along(A, last, ls[2])]
    for a_, l_ in zip(sp, ls):
        pts.append(along(pts[-1], a_, l_))
    return pts


def chain(start, angs, ls):
    pts = [start]
    for a_, l_ in zip(angs, ls):
        pts.append(along(pts[-1], a_, l_))
    return pts


def box_centre(b):
    return ((b[2] + b[3]) / 2, (b[0] + b[1]) / 2)


def build_m(spec):
    """Mounted: Skaarl from his hip, Kled from the seat on Skaarl's back, the heads upright on the necks, the axe and the
    rope from Kled's fists; then the lowest point on the ground (or `lift` rows over it)."""
    R = REST_M
    ss = R["s_spine"]
    sturn = (spec["s_spine"] - ang(ss[0], ss[1]) + 180.0) % 360.0 - 180.0
    hip = spec["hip"]
    neck = along(hip, spec["s_spine"], lengths(R, "s_spine")[0])
    sk = {"s_spine": [hip, neck]}
    for name in ("near_leg", "far_leg", "tail"):
        sk[name] = limb(R, hip, ss[0], name, spec[name], sturn)
    sh = box_centre(S_HEAD)
    off = turned((sh[0] - ss[1][0], sh[1] - ss[1][1]), sturn * 0.5)
    ds = spec.get("s_head", (0, 0))
    sk["s_head"] = (neck[0] + off[0] + ds[0], neck[1] + off[1] + ds[1])
    ks = R["k_spine"]
    if "rider" in spec:
        seat = spec["rider"]
    else:
        so = turned((ks[0][0] - ss[0][0], ks[0][1] - ss[0][1]), sturn)
        seat = (hip[0] + so[0], hip[1] + so[1])
    kturn = (spec["k_spine"] - ang(ks[0], ks[1]) + 180.0) % 360.0 - 180.0
    kneck = along(seat, spec["k_spine"], lengths(R, "k_spine")[0])
    sk["k_spine"] = [seat, kneck]
    for name in ("near_arm", "far_arm"):
        sk[name] = limb(R, kneck, ks[1], name, spec[name], kturn)
    kh = box_centre(K_HEAD_M)
    dk = spec.get("k_head", (0, 0))
    sk["k_head"] = (kneck[0] + kh[0] - ks[1][0] + dk[0], kneck[1] + kh[1] - ks[1][1] + dk[1])
    sk["axe"] = chain(sk["near_arm"][-1], (spec["axe"],), lengths(R, "axe"))
    sk["blade"] = along(sk["axe"][-1], spec["axe"], AXE_R * 0.4)
    sk["rope"] = chain(sk["far_arm"][-1], spec["rope"], lengths(R, "rope"))
    sk["trap"] = along(sk["rope"][-1], spec["rope"][-1], TRAP_R)
    lines = ("s_spine", "near_leg", "far_leg", "tail", "k_spine", "near_arm", "far_arm", "axe", "rope")
    low = max([y for k in lines for _, y in sk[k]] + [sk["trap"][1] + TRAP_R, sk["blade"][1] + AXE_R])
    dy = GROUND_M - (spec["lift"] or 0) - low
    return shift_y(sk, dy)


def build_f(spec):
    """On foot: Kled from his hips, the head upright on the neck, the axe from his near fist."""
    R = REST_F
    fs = R["f_spine"]
    turn = (spec["f_spine"] - ang(fs[0], fs[1]) + 180.0) % 360.0 - 180.0
    hips = spec["hip"]
    neck = along(hips, spec["f_spine"], lengths(R, "f_spine")[0])
    sk = {"f_spine": [hips, neck]}
    for name in ("f_near_leg", "f_far_leg"):
        sk[name] = limb(R, hips, fs[0], name, spec[name], turn)
    for name in ("f_near_arm", "f_far_arm"):
        sk[name] = limb(R, neck, fs[1], name, spec[name], turn)
    kh = box_centre(K_HEAD_F)
    dk = spec.get("k_head", (0, 0))
    sk["k_head"] = (neck[0] + kh[0] - fs[1][0] + dk[0], neck[1] + kh[1] - fs[1][1] + dk[1])
    sk["f_axe"] = chain(sk["f_near_arm"][-1], (spec["f_axe"],), lengths(R, "f_axe"))
    sk["blade"] = along(sk["f_axe"][-1], spec["f_axe"], AXE_R_F * 0.3)
    lines = ("f_spine", "f_near_leg", "f_far_leg", "f_near_arm", "f_far_arm", "f_axe")
    low = max([y for k in lines for _, y in sk[k]] + [sk["blade"][1] + AXE_R_F * 0.6])
    if spec.get("feet_only"):
        low = max(y for k in ("f_near_leg", "f_far_leg") for _, y in sk[k])
    dy = GROUND_F - (spec["lift"] or 0) - low
    return shift_y(sk, dy)


POINTS = ("s_head", "k_head", "blade", "trap")


def shift_y(sk, dy):
    return {k: ((v[0], v[1] + dy) if k in POINTS else [(x, y + dy) for x, y in v]) for k, v in sk.items()}


A = lambda name: angles(REST_M, name)   # noqa: E731
AF = lambda name: angles(REST_F, name)  # noqa: E731
STAND_M = dict(hip=(30.0, 65.0), s_spine=ang(*REST_M["s_spine"]), near_leg="rest", far_leg="rest", tail="rest",
               k_spine=ang(*REST_M["k_spine"]), near_arm="rest", far_arm="rest", axe=A("axe")[0], rope=A("rope"),
               lift=None, shift=0)
STAND_F = dict(hip=(22.0, 48.0), f_spine=ang(*REST_F["f_spine"]), f_near_leg="rest", f_far_leg="rest",
               f_near_arm="rest", f_far_arm="rest", f_axe=AF("f_axe")[0], lift=None, shift=0)

# the poses: name -> (figure "m" / "f", League's frame (champ:clip@ms), what it is for (Chinese), the pose line
# (English), the skeleton spec). Angles: 0 straight down, 90 to the image right, 180 up, -90 to the image left; a limb is
# "rest", its angles, or (target, side, last) - the ankle at the target with the knee solved (side -1 bends a downward
# limb's knee to the image right, +1 to the image left), then the toe at the last angle.
POSES = {
    "a_wind": ("m", "Kled:kled_attack1@233",
               "举斧：斯嘎尔站稳；克烈在鞍上**站起来往上一窜**（上身挺直、整个人比待机高 2 格），近侧（画面左边）的手把**小斧头高高举过头顶往后**，远侧的手拎着捕熊夹的绳子（普攻起手）",
               "AXE UP - the lizard standing still; the rider RISING UP out of the saddle (upper body straight, the whole "
               "rider two squares higher), his NEAR arm (image left) swinging the small AXE HIGH above and behind his head, "
               "the far hand still holding the bear trap's rope.",
               dict(STAND_M, k_spine=170, rider=(25.0, 45.0), near_arm=(-150, -175, 175), axe=-140)),
    "a_chop": ("m", "Kled:kled_attack1@467",
               "砍下：克烈往前（画面右边）扑，近侧的手把**斧头从头顶劈到斯嘎尔头的右前方**（斧刃朝下、比斯嘎尔的头低一点），身子压低；斯嘎尔脖子往前伸（普攻打中）",
               "CHOP - the rider lunging forward to the image right, his NEAR arm bringing the AXE DOWN from over his head "
               "to in front of the lizard's head (the blade down, a little lower than the lizard's head), his body low; "
               "the lizard stretching its neck forward.",
               dict(STAND_M, s_spine=150, k_spine=125, near_arm=(110, 100, 95), axe=150, shift=-4)),
    "q_throw": ("m", "Kled:kled_spell1@122",
                "扔夹子：克烈身子往前送，**远侧的手往前（画面右边）伸直，刚把拴绳的捕熊夹扔出去**（绳子拉直往右、夹子飞在最前面）；斧头垂在身侧（飞索捕熊器：扔出）",
                "THROW THE TRAP - the rider leaning forward, his FAR arm thrust straight forward to the image right having "
                "just flung the BEAR TRAP on its rope: the rope STRAIGHT out to the right, the trap flying at its end; "
                "the axe hanging at his side.",
                dict(STAND_M, k_spine=140, far_arm=(100, 95, 92), rope=(92, 90, 88), near_arm=(-30, -15, 0), axe=-10)),
    "q_yank": ("m", "Kled:kled_spell1_2@142",
               "拽回来：克烈往后（画面左边）仰，**远侧的手攥着绳子往怀里猛拽**（拳头拉到胸前），绳子绷直往右前方；斯嘎尔也往后仰（飞索捕熊器：把敌人拽过来）",
               "YANK - the rider leaning back to the image left, his FAR fist YANKING the rope back to his chest, the rope "
               "taut and straight out to the front-right; the lizard leaning back too.",
               dict(STAND_M, s_spine=165, k_spine=-170, far_arm=(60, -20, -40), rope=(95, 98, 100),
                    near_arm=(-60, -80, -90), axe=-60)),
    "e_lunge": ("m", "Kled:kled_spell3@317",
                "冲刺：斯嘎尔**往前猛冲**，身子往前倾、脖子伸直、嘴张开，**近腿往后蹬直、远腿往前迈**；克烈伏低，斧头往前顶（比武：冲过去）",
                "JOUST - the lizard DASHING forward, body tilted forward, neck stretched, mouth open, its NEAR leg kicked "
                "straight back, the FAR leg striding forward; the rider crouched low, the axe thrust forward.",
                dict(STAND_M, hip=(28.0, 64.0), s_spine=130, near_leg=(-50, -40, -60), far_leg=(40, 10, 60),
                     tail=(-80, -85, -95), k_spine=120, near_arm=(95, 90, 90), axe=100, lift=1, s_head=(2, 1))),
    "e_slash": ("m", "Kled:kled_spell3@475",
                "回身一砍：斯嘎尔刚冲过去、两腿着地刹住；克烈在鞍上**扭身把斧头往后（画面左边）横着抡**，身子侧扭（比武：第二下冲回来）",
                "BACK-SLASH - the lizard landing from the dash with both feet braced; the rider TWISTING in the saddle and "
                "swinging the axe BACK to the image left in a wide level slash.",
                dict(STAND_M, s_spine=165, near_leg=((18.0, 74.0), 1, -70), far_leg=((40.0, 74.0), -1, 70),
                     k_spine=-170, near_arm=(-80, -88, -90), axe=-95)),
    "r_charge": ("m", "Kled:kled_run2_fast@300",
                 "冲锋：斯嘎尔**压低身子往前狂奔**（身子几乎平着、脖子往前伸直、嘴张大），一条腿往前一条腿往后；克烈**站在鞍上往前探身大吼**，斧头往前指（冲啊——！！）",
                 "CHARGE - the lizard SPRINTING forward, body almost level, neck stretched straight out, mouth wide open, "
                 "one leg reaching forward and one kicked back; the rider STANDING UP in the saddle leaning forward and "
                 "yelling, the axe pointed forward.",
                 dict(STAND_M, hip=(26.0, 64.0), s_spine=115, near_leg=(-60, -45, -70), far_leg=(50, 25, 70),
                      tail=(-85, -90, -95), k_spine=125, near_arm=(110, 105, 100), axe=105,
                      far_arm=(150, 160, 170), rope=(-40, -20, 0), lift=2, s_head=(3, 2))),
    "run1": ("m", "Kled:kled_run1_base@0",
             "跑 1：斯嘎尔往前跑（像鸟一样两条腿），**近腿往前迈、远腿往后蹬**，身子稍往前倾；克烈随着颠一下",
             "RUN 1 - the lizard running forward on its two bird-like legs, the NEAR leg striding forward, the FAR leg "
             "pushing back, the body leaning a little forward; the rider bobbing with it.",
             dict(STAND_M, s_spine=150, near_leg=(35, 15, 60), far_leg=(-40, -25, -60), k_spine=145)),
    "run2": ("m", "Kled:kled_run1_base@233",
             "跑 2：近腿落地撑住，远腿往前收到身子下面，身子抬高 1 格",
             "RUN 2 - the near leg landing and bracing under the body, the far leg swinging forward under it, the body "
             "one square higher.",
             dict(STAND_M, s_spine=155, near_leg=((24.0, 74.0), -1, 60), far_leg=(20, -10, 40), k_spine=150, lift=1)),
    "run3": ("m", "Kled:kled_run1_base@467",
             "跑 3：和跑 1 反过来：**远腿往前迈、近腿往后蹬**",
             "RUN 3 - the opposite of run 1: the FAR leg striding forward, the NEAR leg pushing back.",
             dict(STAND_M, s_spine=150, near_leg=(-40, -25, -60), far_leg=(35, 15, 60), k_spine=145)),
    "run4": ("m", "Kled:kled_run1_base@700",
             "跑 4：远腿落地撑住，近腿往前收到身子下面，身子抬高 1 格",
             "RUN 4 - the far leg landing and bracing, the near leg swinging forward under the body, the body one square "
             "higher.",
             dict(STAND_M, s_spine=155, near_leg=(20, -10, 40), far_leg=((34.0, 74.0), 1, 60), k_spine=150, lift=1)),
    "f_wind": ("f", "KledRider:rider_attack1@200",
               "（步行）抡斧：克烈身子往后（画面左边）仰，**双手把大斧往后下方抡开**（斧刃在他身后左下方、离地不远），重心在后脚（下马后的普攻起手）",
               "(ON FOOT) SWING BACK - the rider leaning back to the image left, swinging the BIG AXE back and down "
               "in both hands (the blades behind him on the lower left, near the ground), his weight on the back foot.",
               dict(STAND_F, f_spine=-172, f_near_arm=(-60, -80, -90), f_far_arm=(-40, -60, -75), f_axe=-115,
                    f_near_leg=((12.0, 60.0), 1, -40), feet_only=True)),
    "f_chop": ("f", "KledRider:rider_attack1@350",
               "（步行）横扫：克烈**压低身子往前（画面右边）弓步**，双手把大斧**从后面往前横着扫过去**，斧刃在他右前方、膝盖那么高",
               "(ON FOOT) SWEEP - the rider crouching low in a lunge to the image right, sweeping the BIG AXE in both hands "
               "from behind to the FRONT in a low level arc, the blades out in front of him on the right at knee height.",
               dict(STAND_F, f_spine=148, f_near_arm=(55, 75, 85), f_far_arm=(65, 85, 90), f_axe=97,
                    f_near_leg=((9.0, 60.0), 1, -60), f_far_leg=((34.0, 60.0), -1, 70), feet_only=True)),
    "f_aim": ("f", "KledRider:rider_spell1_1@208",
              "（步行）掏枪：克烈**远侧的手掏出一把短粗的火枪往前（画面右边）平举**，枪口朝右；近侧的手把大斧拖在身后（随身手枪：瞄准）",
              "(ON FOOT) AIM - the rider pulling out a short, stubby BLUNDERBUSS PISTOL in his FAR hand and pointing it "
              "straight forward to the image right; his near hand dragging the big axe behind him.",
              dict(STAND_F, f_far_arm=(95, 92, 90), f_near_arm=(-20, -30, -40), f_axe=-100, feet_only=True)),
    "f_recoil": ("f", "KledRider:rider_spell1_1@313",
                 "（步行）后坐：开枪的后坐力把克烈**往后（画面左边）掀飞**，身子往后仰、两脚离地，举枪的手被震得往上翘（随身手枪：开火后弹开）",
                 "(ON FOOT) RECOIL - the shot's recoil BLOWING the rider BACK to the image left, leaning far back, both "
                 "feet off the ground, the pistol hand kicked up.",
                 dict(STAND_F, f_spine=-150, f_far_arm=(140, 150, 160), f_near_arm=(-40, -60, -70), f_axe=-110,
                      f_near_leg=(40, 60, 80), f_far_leg=(70, 90, 100), lift=3)),
    "f_run1": ("f", "KledRider:rider_run1@0",
               "（步行）跑 1：克烈往前跑，**近腿往前迈、远腿往后蹬**，大斧扛在身侧斜着",
               "(ON FOOT) RUN 1 - the rider running forward, the NEAR leg striding forward, the FAR leg pushing back, the "
               "big axe carried slanted at his side.",
               dict(STAND_F, f_spine=165, f_near_leg=(40, 20, 70), f_far_leg=(-40, -20, -70), feet_only=True)),
    "f_run2": ("f", "KledRider:rider_run1@433",
               "（步行）跑 2：两腿交叉到身子下面、身子抬高 1 格",
               "(ON FOOT) RUN 2 - the legs passing under the body, the body one square higher.",
               dict(STAND_F, f_spine=170, f_near_leg=(10, -15, 40), f_far_leg=(-10, 20, 60), lift=1, feet_only=True)),
    "f_run3": ("f", "KledRider:rider_run1@650",
               "（步行）跑 3：和跑 1 反过来：**远腿往前、近腿往后**",
               "(ON FOOT) RUN 3 - the opposite of run 1: the FAR leg forward, the NEAR leg back.",
               dict(STAND_F, f_spine=165, f_near_leg=(-40, -20, -70), f_far_leg=(40, 20, 70), feet_only=True)),
    "d_fall": ("f", "KledRider:rider_death@320",
               "（死亡）挨了一下：克烈被打得**往后（画面左边）仰**，一条腿往前踢起来，手一松，**大斧脱手往右上方飞出去**",
               "(DEATH) HIT - the rider knocked back to the image left, one leg kicked up in front, his hands letting go, "
               "the BIG AXE flying out of them up to the right.",
               dict(STAND_F, f_spine=-155, f_near_arm=(-120, -150, -170), f_far_arm=(160, 140, 130), f_axe=95,
                    f_far_leg=(110, 100, 90), feet_only=True)),
    "d_down": ("f", "KledRider:rider_death@2400",
               "（死亡）瘫倒：克烈**跪坐着瘫在地上**，身子往前趴、头耷拉下来，眼睛闭上（画成一道线），两只手垂在地上；大斧掉在他右边的地上",
               "(DEATH) COLLAPSED - the rider slumped on his knees on the ground, his body folded forward, his head "
               "drooping, his eyes closed (drawn as lines), his hands hanging to the ground; the big axe lying on the "
               "ground on his right.",
               dict(STAND_F, f_spine=140, f_near_leg=(-80, 40, 90), f_far_leg=(-70, 30, 90), f_near_arm=(20, 10, 0),
                    f_far_arm=(10, 0, -10), f_axe=90, k_head=(1, 3), feet_only=True)),
}


def to_canvas(sk, fig, shift=0):
    dx = (DX_M if fig == "m" else DX_F) + shift
    dy = SOLE_Y // PX - (GROUND_M if fig == "m" else GROUND_F)
    return {k: ((v[0] + dx, v[1] + dy) if k in POINTS else [(x + dx, y + dy) for x, y in v]) for k, v in sk.items()}


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


def head_boxes(fig):
    if fig == "m":
        return (("s_head", S_HEAD), ("k_head", K_HEAD_M))
    return (("k_head", K_HEAD_F),)


def skeleton(can, s, fig, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    for key, b in head_boxes(fig):
        hx, hy = s[key]
        w, h = b[3] - b[2], b[1] - b[0]
        dr.rectangle([(hx - w / 2) * PX, (hy - h / 2) * PX, (hx + w / 2) * PX, (hy + h / 2) * PX],
                     fill=(150, 150, 150, 70 if alpha < 255 else 90), outline=(90, 90, 90, alpha), width=3)
    bx, by = s["blade"]
    r = AXE_R if fig == "m" else AXE_R_F
    dr.ellipse([(bx - r) * PX, (by - r) * PX, (bx + r) * PX, (by + r) * PX], fill=STEEL + (150,),
               outline=(90, 100, 130, alpha), width=4)
    if fig == "m":
        tx, ty = s["trap"]
        dr.ellipse([(tx - TRAP_R) * PX, (ty - TRAP_R) * PX, (tx + TRAP_R) * PX, (ty + TRAP_R) * PX],
                   fill=TRAP + (150,), outline=(30, 30, 30, alpha), width=4)
        order = ("tail", "far_leg", "s_spine", "near_leg", "far_arm", "rope", "k_spine", "axe", "near_arm")
    else:
        order = ("f_far_leg", "f_far_arm", "f_spine", "f_near_leg", "f_axe", "f_near_arm")
    for name in order:
        col = COL[name]
        pts = [c(p) for p in s[name]]
        thin = name in ("rope", "axe", "f_axe")
        dr.line(pts, fill=col + (alpha,), width=5 if thin else 7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == 3 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=col + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


for _k, _v in (("f_spine", "k_spine"), ("f_near_arm", "near_arm"), ("f_far_arm", "far_arm"), ("f_axe", "axe")):
    COL[_k] = COL[_v]


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


SKIN = {"Kled": ["--submesh-texture", "KledRider_base_mat=KledRider_Base", "--submesh-texture",
                 "KledMount_Base_Mat=KledMount_base", "--hide-submesh", "KledRider_base_fish_mat", "--hide-submesh",
                 "KledRider_base_fish_cut_mat"],
        "KledRider": []}


def lol_frame(lol, spec, work, yaw=35):
    champ, frame = spec.split(":", 1)
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ, "--wad",
           "Kled", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--fit-all",
           "--size", "900", "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", str(yaw), "--name", "f",
           "--out", work, "--frame", frame] + SKIN[champ]
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


def build(fig, spec):
    return build_m(spec) if fig == "m" else build_f(spec)


def poses_built():
    return {name: (to_canvas(build(fig, spec), fig, spec.get("shift", 0)), fig, frame, zh, en)
            for name, (fig, frame, zh, en, spec) in POSES.items()}


def rest_m():
    return to_canvas(build_m(dict(STAND_M)), "m")


def rest_f():
    return to_canvas(build_f(dict(STAND_F)), "f")


def problems(name, s, fig):
    """Every bone and box on the canvas; no fist, blade or trap over Kled's face."""
    out = []
    keys = [k for k in s if k not in POINTS]
    pts = [p for k in keys for p in s[k]] + [s["blade"]] + ([s["trap"]] if fig == "m" else [])
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    for key, b in head_boxes(fig):
        hx, hy = s[key]
        w, h = b[3] - b[2], b[1] - b[0]
        if hy - h / 2 < 1 or hx - w / 2 < 0 or hx + w / 2 > CANVAS / PX:
            out.append(f"{key} off the canvas")
    hb, face = (K_HEAD_M, K_FACE_M) if fig == "m" else (K_HEAD_F, K_FACE_F)
    hx, hy = s["k_head"]
    ox, oy = hx - (hb[3] - hb[2]) / 2 - hb[2], hy - (hb[1] - hb[0]) / 2 - hb[0]
    fx0, fx1, fy0, fy1 = face[0] + ox, face[1] + ox, face[2] + oy, face[3] + oy
    arms = ("near_arm", "far_arm") if fig == "m" else ("f_near_arm", "f_far_arm")
    over = [p for p in s[arms[0]][2:] + s[arms[1]][2:] + [s["blade"]] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if over:
        out.append(f"over his face at {[(round(x), round(y)) for x, y in over[:3]]}")
    return out


def tile_sheet(tiles, path, cols=4):
    W = max(t.width for t in tiles)
    H = max(t.height for t in tiles)
    rows_ = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows_), (255, 255, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * W, (k // cols) * H))
    sheet.save(path)


def paste_heads(can, s, fig, designs):
    d = designs[fig]
    for key, (y0, y1, x0, x1) in head_boxes(fig):
        hx, hy = s[key]
        w, h = x1 - x0, y1 - y0
        can.alpha_composite(Image.fromarray(up(d[y0:y1, x0:x1], PX)),
                            (round((hx - w / 2) * PX), round((hy - h / 2) * PX)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/kl_work/kled_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    designs = {"m": np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")),
               "f": np.asarray(Image.open(lp(os.path.join(SRC, "hd", "foot.png"))).convert("RGBA"))}
    dy_m, dy_f = SOLE_Y // PX - GROUND_M, SOLE_Y // PX - GROUND_F
    poses = poses_built()
    for name, (s, fig, *_) in poses.items():
        for p in problems(name, s, fig):
            print("PROBLEM", name, p)
    rests = (("m", rest_m(), DX_M, dy_m, "0_mounted_skeleton.png", "2_design.png"),
             ("f", rest_f(), DX_F, dy_f, "0_foot_skeleton.png", "2_foot_design.png"))
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        for fig, rest, dx, dy, sk_name, _ in rests:
            base = canvas_grid()
            base.alpha_composite(on_grid(designs[fig], dx, dy))
            skeleton(base, rest, fig, "the design's own skeleton (REST)", 200)
            base.convert("RGB").save(os.path.join(a.check, "rest_" + sk_name))
        names = a.only.split(",") if a.only else list(poses)
        cache = os.path.join(a.check, "_league")
        os.makedirs(cache, exist_ok=True)
        tiles = []
        for name in names:
            s, fig, frame, zh, en = poses[name]
            can = canvas_grid()
            paste_heads(can, s, fig, designs)
            skeleton(can, s, fig, name)
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
    for fig, rest, dx, dy, sk_name, design_name in rests:
        base = canvas_grid()
        base.alpha_composite(on_grid(designs[fig], dx, dy))
        clean = base.copy()
        skeleton(base, rest, fig, "0: the approved design with its own skeleton (what each coloured line stands for)", 200)
        base.convert("RGB").save(os.path.join(out, sk_name))
        clean.convert("RGB").save(os.path.join(out, design_name))
    r0, r1, c0, c1 = K_HEAD_M
    b0, b1, d0, d1 = S_HEAD
    kh, sh = big(designs["m"][r0:r1, c0:c1]), big(designs["m"][b0:b1, d0:d1])
    heads = Image.new("RGB", (kh.width + sh.width + 40, max(kh.height, sh.height)), (255, 255, 255))
    heads.paste(kh, (0, 0))
    heads.paste(sh, (kh.width + 40, 0))
    heads.save(os.path.join(out, "1_heads.png"))
    for k, (name, (s, fig, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, fig, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

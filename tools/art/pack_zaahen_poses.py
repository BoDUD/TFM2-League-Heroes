#!/usr/bin/env python3
"""Zaahen's pose pack for Codex (assets/source/zaahen/POSE_PROMPTS.md): the whole-body poses his League clips go through
(the user, 2026-10-26: sprites by Codex from written prompts - pack_locke_poses.py's way).

    python tools/art/pack_zaahen_poses.py [--out C:/t/za_work/zaahen_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (step 0's A-2 at 48 game
px, PPU 1.75: 88 x 84) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames
(tools/lol/pose_ref.py at the 3/4 camera, his skin's own maps: pack_zaahen_picture.LOOK): every bone at the design's
OWN length (measured on hd/idle.png at 10-20x: REST), only its direction set per pose (POSES), the lowest foot on the
ground unless the pose lifts it.
TWO PROPS. His GLAIVE (longer than he is: G_BLADE squares from the near hand to the tip of its curved golden blade,
G_SPEAR from the near hand to its golden spear point) sits in the NEAR hand; `glaive` = the direction from that hand to
the blade's tip (degrees, ang()'s way: 0 down, 90 to the image right, 180 up, -90 to the image left), or ("loose",
centre, dir) for one no hand holds; the far hand may grip the shaft: far_arm = ("shaft", s, side, last) puts its wrist
s squares from the near hand toward the spear point (negative: toward the blade). Drawn as a dark line with the blade
part wide and gold. His WINGS: "folded" (the design's: one sheet from his back down to his calves, turned with his
spine), "back" (swept back behind him), "half" and "spread" (both wings open up and out - B, hd/wings.png); drawn as
translucent navy shapes from his shoulder blades.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head - horns, circlet, hair, face - 8x: every pose wears it); 2_design.png (the design on the
grid); 2b_wings.png (B, the wings-spread design, 8x: the open wings every spread pose copies); per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), PURPLE = the NEAR arm (the glaive hand), ORANGE = the FAR arm; grey box = the head (never redrawn); dark
line with a gold end = the glaive (gold = the blade); navy shapes = the wings.
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
from design_zaahen_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_illaoi_poses import ang, along, turned, bend, canvas_grid as _grid, tile_sheet  # noqa: E402
import pack_illaoi_poses as IP  # noqa: E402
import pack_zaahen_picture as ZP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zaahen")
PX, CANVAS, SOLE_Y = 9, 1254, 1188
GREY = (225, 225, 225)
GROUND = 84                        # the design's soles' bottom edge (rows)
DX, DY = 25, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 132)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (150, 60, 200),
       "far_arm": (255, 140, 0)}
HEAD = (0, 33, 42, 64)             # rows / columns of the horns, circlet, hair and face in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 22 x 33 squares
FACE = (50, 62, 18, 31)            # the face (circlet's gem, eyes, mouth): x0, x1, y0, y1 in design squares
G_BLADE, G_SPEAR = 52, 64          # the glaive: near hand to the blade's tip / to the spear point (squares; a pose's
                                   # "grip" moves the hand along the shaft: squares from the blade's tip)
BLADE = 34                         # the blade's length from its tip (the gold part)
SHAFT_RGB, BLADE_RGB = (30, 35, 70), (240, 180, 60)
WING_RGB = (30, 40, 110)

# the design's own skeleton, measured on hd/idle.png (88 x 84, square edges): the head box's middle; the spine pelvis
# (the gold belt) -> the base of the neck (under the chin); the near arm shoulder, elbow, wrist, fingers (its hand on the
# shaft by his chest, upper left of his body); the far arm down to its hand on the shaft at his far hip; each leg hip,
# knee, ankle, toes (he stands tall, the feet apart); the folded wings from his shoulder blades down to the calves; the
# glaive along its shaft from the blade's tip (2, 3) to the spear point (87, 82)
REST = {
    "head": (53.0, 16.5),
    "spine": [(55.0, 53.0), (55.0, 33.0)],
    "near_arm": [(49.0, 36.0), (46.0, 46.0), (40.0, 38.0), (38.0, 36.0)],
    "far_arm": [(61.0, 36.0), (65.0, 46.0), (66.0, 57.0), (68.0, 59.0)],
    "near_leg": [(52.0, 55.0), (50.0, 66.0), (46.0, 77.0), (43.0, 82.0)],
    "far_leg": [(58.0, 55.0), (60.0, 66.0), (61.0, 77.0), (66.0, 82.0)],
    "wing": (44.0, 30.0),          # the wings' root on his back
    "glaive": -132.6,
}
# wing shapes: mode -> [(direction, length)] one per wing, near first (its far wing a step darker)
WINGS = {"folded": [(-37.0, 62.0)], "back": [(-72.0, 56.0)], "half": [(-112.0, 46.0), (125.0, 34.0)],
         "spread": [(-140.0, 44.0), (140.0, 38.0)]}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest", three angles,
# (target, side, last angle) - the wrist / ankle at the target with the elbow / knee solved (side -1 bends a downward
# limb's middle joint to the image right, +1 to the image left) - or, for the far arm, ("shaft", s, side, last).
# "glaive": the blade's direction from the near hand, or ("loose", centre, dir); "wings": a WINGS mode.
POSES = {
    "a_wind": ("Attack_02@100",
               "普攻起手：两腿站开、膝盖微弯，双手把长刀高高举到头的左后上方（刀刃一头朝上、朝后，不挡脸），翅膀收在身后（横扫前的蓄力）",
               "WIND-UP - feet apart, knees a little bent, BOTH hands raising the glaive high behind the upper left of "
               "his head (the blade end up and back, never over the face), the wings folded behind him.",
               dict(pelvis=(55.0, 55.0), lift=None, shift=4, spine=-176, wings="folded", glaive=-150.0,
                    near_arm=(-140, -160, -165), far_arm=("shaft", 12, 1, 170),
                    near_leg=((46.0, 84.0), 1, -60), far_leg=((64.0, 83.0), -1, 80))),
    "a_sweep": ("Attack_02@500",
                "普攻横扫：弓步往前，双手把长刀往前下方（画面右边）横扫出去，刀刃一头在身前低处、朝右，矛头一头甩到身后，翅膀收在身后（横扫打中）",
                "SWEEP - lunging forward, BOTH hands sweeping the glaive out low to the front (the image right), the "
                "blade end out in front low down, the spear end swung behind him, the wings folded.",
                dict(pelvis=(55.0, 57.0), lift=None, shift=-12, spine=160, wings="folded", glaive=72.0,
                     near_arm=(60, 85, 95), far_arm=("shaft", 10, -1, 80),
                     near_leg=((40.0, 84.0), 1, -60), far_leg=((70.0, 83.0), -1, 80))),
    "q_cut1": ("Spell1_AA1@100",
               "第一斩：身子往前压，双手握刀从左往右横着斩出（刀刃一头平平地伸在身前胸口高、朝右），翅膀收在身后（暗裔长刀：第一下）",
               "FIRST CUT - leaning in, BOTH hands slashing the glaive across from left to right, the blade end out "
               "level in front at chest height (the image right), the wings folded.",
               dict(pelvis=(55.0, 56.0), lift=None, shift=-14, spine=165, wings="folded", glaive=90.0,
                    near_arm=(70, 90, 92), far_arm=("shaft", 12, -1, 90),
                    near_leg=((44.0, 84.0), 1, -60), far_leg=((68.0, 83.0), -1, 80))),
    "q_cut2": ("Spell1_AA1@450",
               "第二斩：身子一转，双手把长刀从下往右上方斜着挑斩（刀刃一头指向右上方高处），翅膀半张开（暗裔长刀：第二下）",
               "SECOND CUT - turning through, BOTH hands slashing the glaive up and across to the upper right (the "
               "blade end high at the upper right), the wings half open.",
               dict(pelvis=(55.0, 55.0), lift=None, shift=-4, spine=178, wings="half", glaive=145.0,
                    near_arm=(110, 130, 140), far_arm=("shaft", 12, -1, 140),
                    near_leg=((46.0, 84.0), 1, -60), far_leg=((66.0, 83.0), -1, 80))),
    "q_crouch": ("Spell1_AA2@150",
                 "下蹲蓄力：深深地蹲下、身子前倾，双手把长刀压低在身前（刀刃一头朝右下方、快碰到地面），翅膀收在身后（暗裔长刀第二段：挑飞前）",
                 "CROUCH - squatting deep, leaning forward, BOTH hands holding the glaive low in front of him (the "
                 "blade end down to the lower right, almost touching the ground), the wings folded.",
                 dict(pelvis=(55.0, 66.0), lift=None, shift=-2, spine=150, wings="folded", glaive=60.0,
                      near_arm=(40, 60, 65), far_arm=("shaft", 12, -1, 60),
                      near_leg=((42.0, 84.0), 1, -70), far_leg=((70.0, 83.0), -1, 80))),
    "q_up": ("Spell1_AA2@400",
             "上挑：猛地站直、往上一跃（脚离地约 2 格），双手把长刀往上挑（刀刃一头竖直朝上、在头的右前上方，不挡脸），翅膀半张开（暗裔长刀第二段：挑飞）",
             "UPPERCUT - springing up straight (the feet about 2 squares off the ground), BOTH hands thrusting the "
             "glaive up (the blade end straight up beside the front of his head, never over the face), the wings half "
             "open.",
             dict(pelvis=(55.0, 53.0), lift=2, shift=-4, spine=178, wings="half", glaive=172.0, grip=80,
                  near_arm=(100, 120, 130), far_arm=("shaft", 12, -1, 170),
                  near_leg=(10, 0, 70), far_leg=(-5, 5, 80))),
    "w_thrust": ("Spell2@250",
                 "直刺：大弓步往前冲，近侧的手把长刀直直地往前（画面右边）刺出去、手臂伸直，刀刃一头朝前平伸，远侧的手在后面握着刀杆，翅膀收在身后（厄影回锋：刺出）",
                 "THRUST - a long lunge forward, the NEAR arm stabbing the glaive straight out to the front (the image "
                 "right), the arm straight, the blade end level in front, the far hand behind it on the shaft, the "
                 "wings folded.",
                 dict(pelvis=(55.0, 58.0), lift=None, shift=-14, spine=150, wings="folded", glaive=92.0,
                      near_arm=(80, 88, 90), far_arm=("shaft", 14, -1, 90),
                      near_leg=((36.0, 84.0), 1, -70), far_leg=((74.0, 83.0), -1, 80))),
    "w_pull": ("Spell2_hit_Nomove@150",
               "回拽：身子往后仰、重心落在后脚，双手把长刀往怀里拽回来（刀刃一头在身前、略朝下），翅膀半张开（厄影回锋：把人拽回来）",
               "PULL - leaning back, the weight on the back foot, BOTH hands yanking the glaive back toward his chest "
               "(the blade end in front of him, a little down), the wings half open.",
               dict(pelvis=(55.0, 56.0), lift=None, shift=0, spine=-168, wings="half", glaive=80.0,
                    near_arm=(30, 100, 95), far_arm=("shaft", 10, 1, 80),
                    near_leg=((42.0, 84.0), 1, -70), far_leg=((66.0, 83.0), -1, 80))),
    "e_dash": ("Spell3_Dash@100",
               "冲刺：身子压得很低、几乎平着往前（画面右边）冲（脚离地约 3 格），双手把长刀拖在身前右下方（刀刃一头朝右下），翅膀往后掠（赤金突袭：冲刺）",
               "DASH - very low, rushing forward almost flat (to the image right, about 3 squares off the ground), "
               "BOTH hands trailing the glaive low in front (the blade end down to the lower right), the wings swept "
               "back.",
               dict(pelvis=(55.0, 60.0), lift=3, shift=-14, spine=128, wings="back", glaive=-92.0,
                    near_arm=(-20, -40, -60), far_arm=("shaft", 10, -1, 80),
                    near_leg=(-70, -60, -40), far_leg=(-30, 20, 80))),
    "e_spin": ("Spell1_AA1@650",
               "绕身斩：身子转了大半圈，双手把长刀在身后横着抡开（刀刃一头甩到画面左边、平平的），翅膀半张开（赤金突袭：绕身一斩）",
               "SPIN - turned most of the way round, BOTH hands swinging the glaive out level behind him (the blade "
               "end out to the image left, level), the wings half open.",
               dict(pelvis=(55.0, 57.0), lift=None, shift=14, spine=-172, wings="half", glaive=-92.0,
                    near_arm=(-60, -85, -90), far_arm=("shaft", -12, 1, -90),
                    near_leg=((44.0, 84.0), 1, -70), far_leg=((68.0, 83.0), -1, 80))),
    "r_crouch": ("Spell4_Intro@120",
                 "起跳下蹲：深深地蹲下，两只翅膀在身后向两边大大张开（照附图 2b 的翅膀），双手把长刀压在身侧（刀刃一头朝左下），抬头（大赦：升空前）",
                 "CROUCH TO LEAP - squatting deep, BOTH WINGS spread wide behind him (the wings of image 2b), BOTH "
                 "hands holding the glaive low at his side (the blade end down to the lower left), the chin up.",
                 dict(pelvis=(55.0, 67.0), lift=None, shift=0, spine=165, wings="spread", glaive=-80.0, grip=44,
                      near_arm=(-20, -40, -45), far_arm=("shaft", -10, 1, -50),
                      near_leg=((42.0, 84.0), 1, -70), far_leg=((70.0, 83.0), -1, 80))),
    "r_rise": ("Spell4_Intro@700",
               "升空：飞在空中（脚离地约 14 格），两只翅膀向上、向两边张开，双手在胸前反握长刀、刀刃一头竖直朝下（准备往下插），两腿并拢垂着（大赦：升空）",
               "RISEN - flying in the air (the feet about 14 squares off the ground), BOTH WINGS spread up and out, "
               "BOTH hands at his chest holding the glaive reversed, the blade end straight DOWN (ready to stab down), "
               "the legs together hanging.",
               dict(pelvis=(55.0, 53.0), lift=14, shift=0, spine=180, wings="spread", glaive=4.0, grip=60,
                    near_arm=(90, 110, 120), far_arm=("shaft", -14, -1, 170),
                    near_leg=(5, 0, 60), far_leg=(-5, 0, 70))),
    "r_stab": ("Spell4_Finish@600",
               "落地插刀：单膝跪地落下（近侧膝盖着地），双手把长刀狠狠插进身前的地里（刀刃一头竖直朝下、插在右前方地上），翅膀半张开（大赦：向下戳刺）",
               "LANDING STAB - landed on one knee (the near knee on the ground), BOTH hands driving the glaive down "
               "into the ground in front of him (the blade end straight down into the ground at the front right), the "
               "wings half open.",
               dict(pelvis=(55.0, 70.0), lift=None, shift=-6, spine=158, wings="half", glaive=-5.0, grip=34,
                    near_arm=(70, 110, 100), far_arm=("shaft", -14, -1, 10),
                    near_leg=(15, -85, -90), far_leg=(85, 0, 80))),
    "run1": ("Runfast@0",
             "跑 1（远侧腿往前迈大步着地，近侧腿往后蹬）：身子往前倾，近侧的手把长刀拖在身后（刀刃一头朝左下、离地），另一只手往前摆，翅膀往后掠",
             "RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg pushing off "
             "behind, the body leaning forward, the near hand trailing the glaive behind him (the blade end down to "
             "the lower left, clear of the ground), the far arm swinging forward, the wings swept back.",
             dict(pelvis=(55.0, 56.0), lift=None, shift=0, spine=160, wings="back", glaive=-60.0,
                  near_arm=(-30, -10, -5), far_arm=(40, 70, 80),
                  near_leg=((42.0, 82.0), 1, -60), far_leg=((70.0, 83.0), -1, 80))),
    "run2": ("Runfast@200",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两只手摆到身边，长刀还拖在身后",
             "RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square "
             "higher, both arms passing close to his sides, the glaive still trailing behind.",
             dict(pelvis=(55.0, 55.0), lift=1, shift=0, spine=163, wings="back", glaive=-62.0,
                  near_arm=(-10, 10, 10), far_arm=(10, 30, 40),
                  near_leg=((54.0, 84.0), 1, 70), far_leg=((66.0, 72.0), -1, 70))),
    "run3": ("Runfast@420",
             "跑 3（近侧腿往前迈大步着地，远侧腿往后蹬）：身子往前倾，近侧拿刀的手往前摆（长刀斜在身侧），另一只手往后摆",
             "RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg pushing off "
             "behind, the body leaning forward, the near (glaive) hand swinging forward (the glaive slanting at his "
             "side), the far arm back.",
             dict(pelvis=(55.0, 56.0), lift=None, shift=0, spine=160, wings="back", glaive=-50.0,
                  near_arm=(30, 60, 70), far_arm=(-30, -10, 0),
                  near_leg=((68.0, 84.0), -1, 80), far_leg=((44.0, 80.0), 1, -60))),
    "run4": ("Runfast@620",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两只手摆到身边",
             "RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square "
             "higher, both arms passing close to his sides.",
             dict(pelvis=(55.0, 55.0), lift=1, shift=0, spine=163, wings="back", glaive=-55.0,
                  near_arm=(10, 30, 40), far_arm=(-10, 10, 10),
                  near_leg=((62.0, 72.0), -1, 70), far_leg=((58.0, 84.0), -1, 80))),
    "d_fall": ("Death@300",
               "被打倒：被打得往后（画面左边）仰倒、膝盖发软，两只手臂往上甩开，长刀从手里飞出去（手里空），翅膀松松地张开（死亡第一下）",
               "KNOCKED BACK - thrown back toward the image left, the knees giving way, both arms flung up, the "
               "glaive flying out of his hands (the hands empty), the wings loosely open.",
               dict(pelvis=(56.0, 58.0), lift=None, shift=8, spine=-150, wings="half",
                    glaive=("loose", (45.0, -8.0), -100.0),
                    near_arm=(-140, -160, -170), far_arm=(115, 135, 145),
                    near_leg=((48.0, 84.0), 1, 60), far_leg=((66.0, 83.0), -1, 80))),
    "d_down": ("Death@3200",
               "跪倒：双膝跪在地上，身子往前垂、两只手撑在膝盖前的地上，翅膀垂下来盖在背上，长刀横躺在他身前的地上（死亡：倒地）",
               "COLLAPSED - down on both knees, the body slumped forward, both hands propped on the ground in front of "
               "the knees, the wings hanging down over his back, the glaive lying flat on the ground in front of him.",
               dict(pelvis=(52.0, 74.0), lift=None, shift=4, spine=135, wings="folded",
                    glaive=("loose", (50.0, 83.0), 90.0),
                    near_arm=(20, 5, 0), far_arm=(35, 10, 5),
                    near_leg=(10, -88, -90), far_leg=(20, -85, -90))),
    "rv_kneel": ("Passive_Revive@1800",
                 "复活跪起：单膝跪地（近侧膝盖着地），近侧的手把长刀竖直拄在身旁的地上（刀刃一头朝上），另一只手按在膝盖上，翅膀收拢裹在身后，抬头看向右前方（被动复活：重新站起之前；站起来之后就是 B 的样子）",
                 "RISING AGAIN - kneeling on one knee (the near knee on the ground), the near hand planting the "
                 "glaive upright on the ground beside him (the blade end up), the far hand on his knee, the wings "
                 "folded round behind him, looking up to the front-right (after it he stands as B).",
                 dict(pelvis=(55.0, 70.0), lift=None, shift=0, spine=172, wings="folded", glaive=178.0, grip=84,
                      near_arm=(-60, -10, -5), far_arm=(60, 20, 30),
                      near_leg=(15, -85, -90), far_leg=(85, 0, 80))),
}


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned); the glaive from the near hand (the far hand on its shaft), or loose; the wings from the back.
    The lowest foot or knee on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    g = spec["glaive"]
    for name, base, base_rest, k in (("near_arm", neck, rs[1], 1.0), ("near_leg", pel, rs[0], 0.5),
                                     ("far_leg", pel, rs[0], 0.5), ("far_arm", neck, rs[1], 1.0)):
        sp = spec[name]
        if sp == "rest":
            sk[name] = [(base[0] + o[0], base[1] + o[1]) for o in
                        (turned((x - base_rest[0], y - base_rest[1]), turn * k) for x, y in REST[name])]
            continue
        off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        ls = lengths(name)
        if sp[0] == "shaft":   # the far hand on the glaive's shaft, s squares from the near hand toward the spear point
            _, s, side, last = sp
            target = along(sk["near_arm"][2], g + 180.0, s)
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        elif len(sp) == 3 and isinstance(sp[0], tuple):
            target, side, last = sp
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    root_off = turned((REST["wing"][0] - rs[1][0], REST["wing"][1] - rs[1][1]), turn)
    sk["wing"] = [(neck[0] + root_off[0], neck[1] + root_off[1])]
    if isinstance(g, tuple):   # loose: (centre, dir) - the blade's tip toward dir
        _, (cx, cy), d = g
        half = (G_BLADE + G_SPEAR) / 2
        sk["glaive"] = [along((cx, cy), d, half), along((cx, cy), d + 180.0, half)]
    else:
        hand = sk["near_arm"][2]
        grip = spec.get("grip", G_BLADE)   # where the near hand holds the shaft: squares from the blade's tip
        sk["glaive"] = [along(hand, g, grip), along(hand, g + 180.0, G_BLADE + G_SPEAR - grip)]
    low = max(y for leg in ("near_leg", "far_leg", "spine") for _, y in sk[leg])
    dy = GROUND - (spec["lift"] or 0) - low
    out = {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}
    if isinstance(g, tuple):   # a glaive on the ground stays where it was put
        out["glaive"] = sk["glaive"]
    wturn = turn if spec["wings"] == "folded" else 0.0
    out["wings"] = (spec["wings"], wturn)
    return out


def to_canvas(sk, shift=0):
    return {k: (v if k == "wings" else (v[0] + DX + shift, v[1] + DY) if k == "head"
                else [(x + DX + shift, y + DY) for x, y in v]) for k, v in sk.items()}


def c(p):
    return (p[0] * PX, p[1] * PX)


def wing_shapes(s):
    """The wings as polygons from their root: (points, darker) per wing, the far one last."""
    mode, turn = s["wings"]
    root = s["wing"][0]
    out = []
    for k, (d, length) in enumerate(WINGS[mode]):
        d = d + turn
        tip = along(root, d, length)
        a1 = along(root, d - 22.0, length * 0.55)
        a2 = along(root, d + 18.0, length * 0.8)
        out.append(([root, a1, tip, a2], k == 1))
    return out


def skeleton(can, s, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    for pts, far in reversed(wing_shapes(s)):
        rgb = tuple(v // 2 for v in WING_RGB) if far else WING_RGB
        dr.polygon([c(p) for p in pts], fill=rgb + (70,), outline=rgb + (alpha,))
    blade_tip, spear = s["glaive"]
    dr.line([c(blade_tip), c(spear)], fill=SHAFT_RGB + (alpha,), width=5)
    d = ang(blade_tip, spear)
    dr.line([c(blade_tip), c(along(blade_tip, d, BLADE))], fill=BLADE_RGB + (alpha,), width=13)
    dr.line([c(along(spear, d + 180.0, 10)), c(spear)], fill=BLADE_RGB + (alpha,), width=7)
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("far_leg", "far_arm", "spine", "near_leg", "near_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 10 if name.endswith("arm") and k == 2 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def canvas_grid():
    IP.PX, IP.CANVAS, IP.SOLE_Y = PX, CANVAS, SOLE_Y
    return _grid()


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work):
    """League's frame, Zaahen at the 3/4 camera in his own maps."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Zaahen",
           "--fit-all", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", "900", "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f",
           "--out", work, "--frame", frame, "--mirror"] + ZP.LOOK
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


def fitted(spec):
    """build() with the glaive's held ends kept between the canvas top and the ground (the near hand slides along the
    shaft: the grip changes, never the direction), then the whole figure shifted the least from the pose's own `shift`
    that keeps every point on the canvas."""
    s = build(spec)
    if not isinstance(spec["glaive"], tuple):
        grip = spec.get("grip", G_BLADE)
        (bx, by), (sx, sy) = s["glaive"]
        top, ground = 1 - DY, GROUND
        for _ in range(2):
            if by > ground or by < top:     # the blade's end out: shorten that side
                k = ((ground if by > ground else top) - s["near_arm"][2][1]) / (by - s["near_arm"][2][1])
                grip *= max(0.2, k)
            if sy > ground or sy < top:     # the spear's end out: shorten the other side
                rest = G_BLADE + G_SPEAR - grip
                k = ((ground if sy > ground else top) - s["near_arm"][2][1]) / (sy - s["near_arm"][2][1])
                grip = G_BLADE + G_SPEAR - rest * max(0.2, k)
            s = build(dict(spec, grip=grip))
            (bx, by), (sx, sy) = s["glaive"]
    xs = [p[0] for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg", "glaive") for p in s[k]] +          [s["head"][0] - HW / 2, s["head"][0] + HW / 2]
    lo, hi = 2 - DX - min(xs), CANVAS / PX - 2 - DX - max(xs)
    shift = min(max(spec.get("shift", 0), lo), hi)
    return to_canvas(s, round(shift))


def poses_built():
    return {name: (fitted(spec), frame, zh, en) for name, (frame, zh, en, spec) in POSES.items()}


def problems(name, s):
    """Every bone, the head box and the glaive on the canvas, nothing below the ground; no hand or blade on the face."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg", "glaive") for p in s[k]]
    bad = [(round(x), round(y)) for x, y in pts if x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6]
    if bad:
        out.append(f"off the canvas / below the ground at {bad[:3]}")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"hand over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    (x0, y0), (x1, y1) = s["glaive"]
    for k in range(81):
        x, y = x0 + (x1 - x0) * k / 80, y0 + (y1 - y0) * k / 80
        if fx0 <= x <= fx1 and fy0 <= y <= fy1:
            out.append("glaive over the face")
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/za_work/zaahen_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    wings = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "wings.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), wings="folded",
                                glaive=REST["glaive"], near_arm="rest", far_arm="rest", near_leg="rest",
                                far_leg="rest")))
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
    r0, r1, c0, c1 = HEAD
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
            hx, hy = s["head"]
            can.alpha_composite(Image.fromarray(up(idle[r0:r1, c0:c1], PX)),
                                (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
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
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    big(wings).save(os.path.join(out, "2b_wings.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

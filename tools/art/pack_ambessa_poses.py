#!/usr/bin/env python3
"""Ambessa's pose pack for Codex (assets/source/ambessa/POSE_PROMPTS.md): the whole-body poses her League clips go
through (pack_yorick_poses.py's way).

    python tools/art/pack_ambessa_poses.py [--out C:/t/am_work/ambessa_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]
    python tools/art/pack_ambessa_poses.py --no-lol ...   # without the League client (a cloud session)

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (step 1's A-1 with its head
cut to 27%, 117 x 96, PPU 2.0; the user: 「用这个」) sits at squares (DX + shift, DY) on it. The skeletons are set by
hand after League's Ambessa (her clips as known: the alternating blade attacks, Cunning Sweep's half-circle sweep and
Sundering Slam's leaping slam, Repudiation's crossed-blade brace and slam, Lacerate's chain lash, Public Execution's
grab and slam, Drakehound's Step's lunging dash), drafted in a session without the League client. With the client
(the default; the user: 「重新参考英雄联盟的 重新整理了给我」) each pose also carries League's own frame,
<k>_<name>_league.png (tools/lol/pose_ref.py at the 3/4 camera, Riot's, kept local): the clip found in her animation
bin at run time by its role (LEAGUE: the clip, the moment in ms; the names it picked go to
assets/source/ambessa/lol_names.txt with pack_ambessa_picture.py's), and --check DIR shows every skeleton beside it so
the skeletons can be set after League's frames before the pack goes out. --no-lol: no League frames, the prompt's words
only. Every bone at the design's
OWN length (measured on hd/idle.png at 8x: REST), only its direction set per pose (POSES), the lowest foot on the ground
unless the pose lifts it. The prompt gives the legs' and arms' lengths in squares and asks Codex to count them.
HER BLADES are big props, each held in one fist: a hooked crescent BLADE_L squares from the handle to its far tip and
BLADE_W across at its widest. Each pose sets each blade's direction (`dir`, the fist -> the far tip, degrees: 0 straight
down, 90 to the image right, 180 up, -90 to the image left) and the side its crescent bulges to (`side` +1: to the
left of that direction, -1: to the right); `loose` = (centre, dir, side) is a blade flung out on its chain (Lacerate),
the chain drawn from the fist to its handle. Drawn on the skeleton as a translucent crescent.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head, 8x: every pose wears it); 2_design.png (the design on the grid); per pose
<k>_<name>_skeleton.png. --check DIR: every skeleton with the design's head pasted in one sheet, and the design's own
skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), PURPLE = the NEAR arm (image left in the design), ORANGE = the FAR arm (image right in the design); the
big dot on each arm = the fist; grey box = the head (hair and face, never redrawn); TEAL crescent = the near arm's blade,
LIGHT BLUE crescent = the far arm's blade; dark grey line = a chain to a flung blade.
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_ambessa_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_illaoi_poses import ang, along, turned, bend, canvas_grid as _grid, tile_sheet  # noqa: E402
import pack_illaoi_poses as IP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ambessa")
PX, CANVAS, SOLE_Y = 8, 1254, 1200
GREY = (225, 225, 225)
GROUND = 96                         # the design's soles' bottom edge (rows)
DX, DY = 19, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 150, 54 rows above her)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (150, 60, 200),
       "far_arm": (255, 140, 0)}
BLADE_COL = {"near_arm": (40, 170, 170), "far_arm": (110, 170, 240)}
HEAD = (0, 27, 49, 81)             # rows / columns of the hair and face in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 32 x 27 squares
FACE = (56, 78, 9, 25)             # the brows, eyes and lips: x0, x1, y0, y1 in design squares
BLADE_L, BLADE_W = 34, 18          # a blade: the fist to the far tip, and across (squares)

# the design's own skeleton, measured on hd/idle.png (117 x 96, square edges): the head box's middle; the spine pelvis
# (the belt) -> the base of the neck; each arm shoulder, elbow, wrist, the fist (both hanging, a blade in each fist);
# each leg hip, knee, ankle, toes
REST = {
    "head": (65.0, 13.5),
    "spine": [(64.0, 52.0), (66.0, 28.0)],
    "near_arm": [(46.0, 32.0), (40.0, 44.0), (32.0, 57.0), (28.0, 61.0)],
    "far_arm": [(78.0, 32.0), (80.0, 42.0), (84.0, 58.0), (86.0, 63.0)],
    "near_leg": [(58.0, 52.0), (51.0, 71.0), (45.0, 88.0), (39.0, 95.0)],
    "far_leg": [(70.0, 52.0), (74.0, 71.0), (76.0, 88.0), (84.0, 95.0)],
    "blades": dict(near_arm=dict(dir=-30.0, side=1), far_arm=dict(dir=40.0, side=-1)),
}

# the poses: name -> (what it is for (Chinese), the pose line (English), the skeleton: the pelvis (design squares), "lift"
# (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole figure is moved on the canvas), the
# spine's direction and every limb (degrees as above) - each bone at the design's own length (REST). A limb is "rest",
# three angles, or (target, side, last angle) - the wrist / ankle at the target with the elbow / knee solved (side -1
# bends a downward limb's middle joint to the image right, +1 to the image left). "blades": per arm dir / side, or
# loose=((x, y), dir, side).
POSES = {
    "a1_wind": ("普攻一起手：身子往左后方扭，近侧（画面左边）那只手把刀高高抡到左肩后上方（刀尖朝左上，不挡脸），远侧那只手的刀垂在身侧，两腿分开站稳",
                "ATTACK 1 WIND-UP - twisting back toward the image left, the NEAR fist raised behind her near shoulder "
                "with its blade swung up to the upper left (never over the face), the far blade hanging at her side, feet "
                "planted apart.",
                dict(pelvis=(64.0, 52.0), lift=None, shift=6, spine=-174, near_arm=(-120, -160, -165),
                     far_arm=(10, 5, 10), near_leg=((42.0, 95.0), 1, -60), far_leg=((82.0, 95.0), -1, 60),
                     blades=dict(near_arm=dict(dir=-135.0, side=1), far_arm=dict(dir=50.0, side=-1)))),
    "a1_slash": ("普攻一砍下：身子往前压、弓步，近侧那只手的刀从左上方斜着砍到身前右下方（刀尖朝右下），远侧那只手往后收",
                 "ATTACK 1 SLASH - pressing forward in a lunge, the NEAR blade cut down from the upper left to the lower "
                 "right in front of her belly (its tip low on the image right), the far arm pulled back.",
                 dict(pelvis=(64.0, 55.0), lift=None, shift=-6, spine=165, near_arm=((66.0, 56.0), 1, 80),
                      far_arm=(-20, -35, -40), near_leg=((44.0, 95.0), -1, -60), far_leg=((88.0, 95.0), -1, 60),
                      blades=dict(near_arm=dict(dir=60.0, side=1), far_arm=dict(dir=-55.0, side=1)))),
    "a2_wind": ("普攻二起手：身子往右前方扭，远侧（画面右边）那只手把刀举到右肩上方（刀尖朝上，在头的右上方，不挡脸），近侧那只手的刀垂在身前",
                "ATTACK 2 WIND-UP - twisting toward the image right, the FAR fist raised above her far shoulder with its "
                "blade pointing up (above her head on the right, never over the face), the near blade hanging in front "
                "of her.",
                dict(pelvis=(64.0, 52.0), lift=None, shift=-4, spine=178, near_arm=(15, 20, 15),
                     far_arm=(150, 165, 170), near_leg=((46.0, 95.0), 1, -60), far_leg=((82.0, 95.0), -1, 60),
                     blades=dict(near_arm=dict(dir=-45.0, side=1), far_arm=dict(dir=165.0, side=-1)))),
    "a2_slash": ("普攻二横扫：远侧那只手的刀从右上方往前横扫到身前（刀尖朝右、略朝下），身子往前压，近侧的刀往后摆",
                 "ATTACK 2 SWEEP - the FAR blade swept across in front of her from the upper right (its tip pointing to "
                 "the image right and a little down), the body pressing forward, the near blade swung back.",
                 dict(pelvis=(64.0, 54.0), lift=None, shift=-8, spine=168, near_arm=(-40, -50, -50),
                      far_arm=((100.0, 48.0), -1, 95), near_leg=((46.0, 95.0), -1, -60), far_leg=((86.0, 95.0), -1, 60),
                      blades=dict(near_arm=dict(dir=-45.0, side=1), far_arm=dict(dir=80.0, side=-1)))),
    "q_wind": ("狡诈横扫起手：深深蹲下，两只手臂往两边张开、压低，两把刀在身体两侧齐膝高往外甩开（刀尖朝外、略朝上），铁链跟着甩起来",
               "CUNNING SWEEP WIND-UP - squatting deep and low, BOTH arms spread out low to the sides, the two blades "
               "swung out at knee height on either side of her (their tips pointing outward and a little up), the chains "
               "swinging with them.",
               dict(pelvis=(64.0, 60.0), lift=None, shift=-3, spine=172, near_arm=(-45, -55, -60),
                    far_arm=(40, 50, 55), near_leg=((38.0, 95.0), 1, -70), far_leg=((88.0, 95.0), -1, 70),
                    blades=dict(near_arm=dict(dir=-110.0, side=-1), far_arm=dict(dir=110.0, side=1)))),
    "q_sweep": ("狡诈横扫：身子挺直、踮起脚，两只手臂往两边伸直齐肩高，两把刀在两边往外上方横扫出去（近侧的刀尖朝左上、远侧的刀尖朝右上），远侧的腿往前迈",
                "CUNNING SWEEP - standing tall on her toes, BOTH arms flung straight out to the sides at shoulder height, "
                "the two blades sweeping out and up on either side (the near blade's tip to the upper left, the far "
                "blade's to the upper right), the far leg stepping forward.",
                dict(pelvis=(64.0, 50.0), lift=2, shift=-2, spine=176, near_arm=(-100, -95, -95),
                     far_arm=(100, 95, 95), near_leg=((48.0, 95.0), 1, -50), far_leg=((80.0, 93.0), -1, 50),
                     blades=dict(near_arm=dict(dir=-125.0, side=-1), far_arm=dict(dir=125.0, side=1)))),
    "q2_leap": ("裂地重击起跳：双脚离地跳起（脚离地约 10 格），两只手把两把刀一起高高举过头顶（刀尖朝左后上方，不挡脸），膝盖收起",
                "SUNDERING SLAM LEAP - jumping (the feet about 10 squares off the ground), BOTH blades raised high over "
                "her head together (their tips up and back to the upper left, never over the face), knees drawn up.",
                dict(pelvis=(64.0, 52.0), lift=10, shift=6, spine=-176, near_arm=(-165, -175, -180),
                     far_arm=(-175, 175, 180), near_leg=((52.0, 84.0), -1, -40), far_leg=((78.0, 86.0), -1, 50),
                     blades=dict(near_arm=dict(dir=-140.0, side=1), far_arm=dict(dir=-155.0, side=1)))),
    "q2_slam": ("裂地重击砸下：落地深蹲，两只手把两把刀一起往身前（画面右边）的地上狠狠砸下（刀尖砸在地面线上），身子往前扑",
                "SUNDERING SLAM - landing in a deep crouch, BOTH blades slammed down together onto the ground in front "
                "of her (on the image right, their tips on the ground line), the body thrown forward.",
                dict(pelvis=(62.0, 64.0), lift=None, shift=-14, spine=145, near_arm=((84.0, 60.0), -1, 100),
                     far_arm=((92.0, 62.0), -1, 110), near_leg=((42.0, 95.0), -1, -80), far_leg=((82.0, 95.0), -1, 60),
                     blades=dict(near_arm=dict(dir=40.0, side=1), far_arm=dict(dir=35.0, side=1)))),
    "w_guard": ("拒斥格挡：远侧那只手把刀举过头顶横着挡住（刀身横在头的上方、刀尖朝左，不挡脸），近侧那只手的刀护在身前，弓着背、膝盖弯、站稳",
                "REPUDIATION BRACE - the FAR fist raised over her head holding its blade across above her head as a "
                "guard (the blade lying flat over the head, its tip to the image left, never over the face), the NEAR "
                "blade held across in front of her belly, hunched, knees bent, braced.",
                dict(pelvis=(64.0, 56.0), lift=None, shift=0, spine=172, near_arm=((70.0, 54.0), 1, 80),
                     far_arm=(170, 178, 180), near_leg=((44.0, 95.0), -1, -60), far_leg=((84.0, 95.0), -1, 60),
                     blades=dict(near_arm=dict(dir=70.0, side=1), far_arm=dict(dir=-110.0, side=1)))),
    "w_slam": ("拒斥砸地：深深蹲下，两只手把两把刀往两边的地上砸下去（近侧的刀在画面左下、远侧的刀在画面右下，刀尖着地）",
               "REPUDIATION SLAM - squatting deep, BOTH blades slammed down onto the ground on either side of her (the "
               "near one low on the image left, the far one low on the image right, their tips on the ground).",
               dict(pelvis=(64.0, 63.0), lift=None, shift=0, spine=175, near_arm=((36.0, 60.0), 1, -60),
                    far_arm=((94.0, 60.0), -1, 60), near_leg=((40.0, 95.0), 1, -70), far_leg=((88.0, 95.0), -1, 70),
                    blades=dict(near_arm=dict(dir=-15.0, side=1), far_arm=dict(dir=15.0, side=-1)))),
    "e_lash1": ("割裂一：两只手臂往两边张开，两把刀被铁链甩出去、飞在身体两侧（近侧的刀在画面左边齐腰高、远侧的刀在画面右边齐肩高），铁链从拳头拉直连到刀柄，身子微微往右转",
                "LACERATE 1 - both arms flung out to the sides, the two blades WHIRLED OUT ON THEIR CHAINS and flying at "
                "her sides (the near blade out on the image left at waist height, the far blade out on the image right "
                "at shoulder height), each chain pulled straight from the fist to the blade's handle, turning a little "
                "to the right.",
                dict(pelvis=(64.0, 54.0), lift=None, shift=0, spine=176, near_arm=(-100, -95, -90),
                     far_arm=(110, 100, 95), near_leg=((46.0, 95.0), 1, -60), far_leg=((82.0, 95.0), -1, 60),
                     blades=dict(near_arm=dict(loose=((6.0, 56.0), -100.0, 1)),
                                 far_arm=dict(loose=((114.0, 34.0), 80.0, 1))))),
    "e_lash2": ("割裂二：转了半圈，手臂换个方向，两把刀被铁链甩到另一边（近侧的刀在画面右下、远侧的刀在画面左上方、高过头，不挡脸），铁链拉直",
                "LACERATE 2 - half a turn on, the arms swapped over, the blades whirled round on their chains to the "
                "other side (the near blade low on the image right, the far blade high on the image left above her "
                "head, never over the face), the chains pulled straight.",
                dict(pelvis=(64.0, 54.0), lift=None, shift=0, spine=-178, near_arm=((78.0, 56.0), 1, 80),
                     far_arm=(-150, -140, -135), near_leg=((46.0, 95.0), 1, -60), far_leg=((82.0, 95.0), -1, 60),
                     blades=dict(near_arm=dict(loose=((118.0, 72.0), 80.0, -1)),
                                 far_arm=dict(loose=((24.0, -16.0), -120.0, 1))))),
    "step": ("龙犬之步：往前（画面右边）冲刺的一步，身子往前倾得很厉害，前腿弓、后腿蹬直，两把刀都拖在身后（刀尖朝左下、离地）",
             "DRAKEHOUND'S STEP - a dashing lunge forward to the image right, the body leaning far forward, the front "
             "leg bent, the back leg pushing straight, both blades trailing behind her (their tips low on the image left, "
             "off the ground).",
             dict(pelvis=(62.0, 57.0), lift=None, shift=4, spine=150, near_arm=(-70, -75, -80),
                  far_arm=(-45, -60, -70), near_leg=((34.0, 95.0), 1, -80), far_leg=((86.0, 95.0), -1, 60),
                  blades=dict(near_arm=dict(dir=-95.0, side=1), far_arm=dict(dir=-80.0, side=1)))),
    "r_grab": ("公开处决抓人：远侧那只手高高举过头顶（把抓住的敌人提起来，刀柄在拳头里、刀尖朝上），近侧那只手的刀垂在身侧，身子挺直、踮起脚",
               "PUBLIC EXECUTION GRAB - the FAR fist thrust high over her head, hoisting her victim (its blade in the "
               "fist, tip up), the NEAR blade hanging at her side, standing tall on her toes.",
               dict(pelvis=(64.0, 50.0), lift=2, shift=0, spine=178, near_arm=(-20, -15, -15),
                    far_arm=(170, 175, 180), near_leg=((52.0, 95.0), 1, -50), far_leg=((78.0, 95.0), -1, 50),
                    blades=dict(near_arm=dict(dir=-35.0, side=1), far_arm=dict(dir=175.0, side=-1)))),
    "r_slam": ("公开处决砸下：几乎单膝跪地的深蹲，远侧那只手往前下方猛按（把敌人按进画面右边的地里），近侧那只手的刀从上往下砍到身前地面（刀尖着地）",
               "PUBLIC EXECUTION SLAM - dropping into a deep crouch, almost kneeling, the FAR hand driven down in front "
               "of her (pinning her victim into the ground on the image right), the NEAR blade hewn down onto the ground "
               "in front of her (its tip on the ground).",
               dict(pelvis=(62.0, 66.0), lift=None, shift=-12, spine=145, near_arm=((78.0, 66.0), -1, 90),
                    far_arm=((96.0, 80.0), -1, 100), near_leg=((40.0, 95.0), -1, -90), far_leg=((80.0, 95.0), -1, 50),
                    blades=dict(near_arm=dict(dir=45.0, side=1), far_arm=dict(dir=-60.0, side=1)))),
    "run1": ("跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子前倾，两把刀拖在身后两侧（刀尖朝左下、离地），手臂往后摆",
             "RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back, "
             "leaning forward, both blades trailing behind at her sides (tips low on the image left, off the ground).",
             dict(pelvis=(64.0, 54.0), lift=None, shift=0, spine=168, near_arm=(-40, -55, -60),
                  far_arm=(-15, -30, -40), near_leg=((40.0, 95.0), 1, -70), far_leg=((86.0, 95.0), -1, 60),
                  blades=dict(near_arm=dict(dir=-70.0, side=1), far_arm=dict(dir=-60.0, side=1)))),
    "run2": ("跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两把刀还拖在身后",
             "RUN 2 - the near leg under the body carrying her, the FAR knee lifted forward, the body one square "
             "higher, both blades still trailing behind.",
             dict(pelvis=(64.0, 52.0), lift=1, shift=0, spine=170, near_arm=(-30, -45, -50),
                  far_arm=(-10, -25, -35), near_leg=((60.0, 95.0), -1, -40), far_leg=((84.0, 80.0), -1, 60),
                  blades=dict(near_arm=dict(dir=-65.0, side=1), far_arm=dict(dir=-55.0, side=1)))),
    "run3": ("跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：身子前倾，两把刀拖在身后",
             "RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back, "
             "leaning forward, both blades trailing behind.",
             dict(pelvis=(64.0, 54.0), lift=None, shift=0, spine=168, near_arm=(-20, -35, -45),
                  far_arm=(-35, -50, -60), near_leg=((84.0, 95.0), -1, 60), far_leg=((44.0, 95.0), 1, -70),
                  blades=dict(near_arm=dict(dir=-60.0, side=1), far_arm=dict(dir=-70.0, side=1)))),
    "run4": ("跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两把刀拖在身后",
             "RUN 4 - the far leg under the body carrying her, the NEAR knee lifted forward, the body one square "
             "higher, both blades trailing behind.",
             dict(pelvis=(64.0, 52.0), lift=1, shift=0, spine=170, near_arm=(-15, -30, -40),
                  far_arm=(-30, -45, -50), near_leg=((80.0, 80.0), -1, 60), far_leg=((66.0, 95.0), -1, 40),
                  blades=dict(near_arm=dict(dir=-55.0, side=1), far_arm=dict(dir=-65.0, side=1)))),
    "d_kneel": ("倒下一：被打得跪倒，双膝着地（小腿平贴地面、往后伸），身子往后仰，两只手松开垂着，两把刀掉在身体两侧的地上（平躺）",
                "COLLAPSE - struck down onto both knees (the shins flat on the ground behind), the body sagging back, "
                "both hands opening and hanging, the two blades dropped flat on the ground at her sides.",
                dict(pelvis=(64.0, 70.0), lift=None, shift=0, spine=-172, near_arm=(-30, -15, -10),
                     far_arm=(25, 15, 10), near_leg=(15, -90, -90), far_leg=(25, -90, -90),
                     blades=dict(near_arm=dict(loose=((20.0, 90.0), -90.0, 1)),
                                 far_arm=dict(loose=((112.0, 90.0), 90.0, -1))))),
    "d_slump": ("倒下二：跪着往前瘫下去，身子前弓，头低下（头不转），两只手臂软软垂到地上，两把刀平躺在地上",
                "SLUMP - still kneeling, slumping forward, the body bent over, the head low (never turned), both arms "
                "hanging limp to the ground, the two blades lying flat on the ground.",
                dict(pelvis=(62.0, 72.0), lift=None, shift=-4, spine=150, near_arm=(-15, -5, 0),
                     far_arm=(30, 40, 60), near_leg=(20, -90, -90), far_leg=(30, -90, -90),
                     blades=dict(near_arm=dict(loose=((20.0, 90.0), -90.0, 1)),
                                 far_arm=dict(loose=((114.0, 90.0), 90.0, -1))))),
}


# pose -> (clip role, the moment in ms into that clip): League's frame each skeleton follows, picked on strips of her
# clips (tools/lol/pose_ref.py). The roles are looked up in her animation bin by these patterns (stems in lower case),
# the first pattern with a hit wins and among its hits the shortest stem: her PassiveDash_Spell* clips (each ability
# cast out of Drakehound's Step) and Joke_Intro_Run match the looser patterns too. A role with no clip falls back to
# the next one listed (Sundering Slam to the Q clip, the Step to the run).
ROLES = {
    "a1": [r"^attack_?1$", r"(^|_)attack_?1"],
    "a2": [r"^attack_?2$", r"(^|_)attack_?2"],
    "q": [r"^spell1_?a?$", r"(^|_)spell1(_?a)?$", r"(^|_)spell1"],
    "q2": [r"^spell1_?b$", r"(^|_)spell1_?b$", r"(^|_)spell1_?2$", r"(^|_)spell1_?recast", r"(^|_)spell1_?slam"],
    "w": [r"^spell2_?a?$", r"(^|_)spell2(_?a)?$", r"(^|_)spell2"],
    "e": [r"^spell3_?a?$", r"(^|_)spell3(_?a)?$", r"(^|_)spell3"],
    "r": [r"^spell4_?hit$", r"^spell4_?a?$", r"(^|_)spell4"],
    "step": [r"^passivedash_spell1_?a$", r"(^|_)passivedash", r"(^|_)dash", r"(^|_)step"],
    "run": [r"^run(_?base)?$", r"^run\d*$", r"(^|_)run"],
    "death": [r"^death$", r"(^|_)death"],
}
FALLBACK = {"q2": ("q", 600), "step": ("run", None)}
LEAGUE = {
    "a1_wind": ("a1", 125), "a1_slash": ("a1", 250), "a2_wind": ("a2", 125), "a2_slash": ("a2", 250),
    "q_wind": ("q", 88), "q_sweep": ("q", 350), "q2_leap": ("q2", 150), "q2_slam": ("q2", 300),
    "w_guard": ("w", 250), "w_slam": ("w", 500), "e_lash1": ("e", 175), "e_lash2": ("e", 350),
    "step": ("step", 150), "r_grab": ("r", 488), "r_slam": ("r", 838),
    "run1": ("run", 0), "run2": ("run", 267), "run3": ("run", 533), "run4": ("run", 800),
    "d_kneel": ("death", 900), "d_slump": ("death", 2250),
}


def league_clips(lol):
    """{pose: "clip@ms"} for League's frames, from her animation bin (pack_ambessa_picture.names), and the roles
    picked (written to assets/source/ambessa/lol_names.txt next to the picture pack's)."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
    import pack_ambessa_picture as PP
    from riot import Wad
    wad = os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "Ambessa.wad.client")
    if not os.path.isfile(wad):
        sys.exit(f"League client not found: {wad} - pass --lol <League folder>, or --no-lol for a pack without League's frames")
    clips = PP.names(Wad(wad))[0]
    pick = {}
    for role, pats in ROLES.items():
        for pat in pats:
            hit = sorted((st for st, (_, d) in clips.items() if d and re.search(pat, st)), key=lambda st: (len(st), st))
            if hit:
                pick[role] = hit[0]
                break
    out = {}
    for pose, (role, ms) in LEAGUE.items():
        r, at = role, ms
        if r not in pick and r in FALLBACK:
            r, f = FALLBACK[r]
            at = f if f is not None else ms
        if r not in pick:
            print("no League clip for", pose, "(role", role + ")")
            continue
        out[pose] = f"{pick[r]}@{min(at, round(clips[pick[r]][1] * 1000))}"
    path = os.path.join(SRC, "lol_names.txt")
    old = open(path, encoding="utf-8").read() if os.path.isfile(path) else ""
    old = old.split("\n## poses")[0].rstrip("\n")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(old + "\n\n## poses (tools/art/pack_ambessa_poses.py)\n"
                + "\n".join(f"{k} {v}" for k, v in out.items()) + "\n")
    print("League roles", pick)
    return out


def lol_frame(lol, frame, work):
    """League's frame, Ambessa at the 3/4 camera facing right (all her submeshes: the blades and chains)."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Ambessa",
           "--fit-all", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900", "--fit", "0.4",
           "--ground", "0.8", "--width", "2.2", "--yaw", "35", "--name", "f", "--out", work, "--frame", frame, "--mirror"]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "f.png")).convert("RGB")
    a = np.asarray(im).astype(int)
    fg = np.abs(a - GREY).sum(2) > 12
    ys, xs = np.nonzero(fg)
    m = 40
    return im.crop((max(0, xs.min() - m), max(0, ys.min() - m), min(im.width, xs.max() + m), min(im.height, ys.max() + m)))


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned). The lowest foot or knee on the ground, or `lift` rows over it. Loose blades stay where put."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    for name, base, base_rest, k in (("near_arm", neck, rs[1], 1.0), ("far_arm", neck, rs[1], 1.0),
                                     ("near_leg", pel, rs[0], 0.5), ("far_leg", pel, rs[0], 0.5)):
        sp = spec[name]
        if sp == "rest":
            sk[name] = [(base[0] + o[0], base[1] + o[1]) for o in
                        (turned((x - base_rest[0], y - base_rest[1]), turn * k) for x, y in REST[name])]
            continue
        off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        ls = lengths(name)
        if len(sp) == 3 and isinstance(sp[0], tuple):
            target, side, last = sp
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    low = max(y for leg in ("near_leg", "far_leg", "spine") for _, y in sk[leg])
    dy = GROUND - (spec["lift"] or 0) - low
    out = {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}
    out["blades"] = {}
    for arm, b in spec["blades"].items():
        if "loose" in b:
            (cx, cy), d, side = b["loose"]
            hilt = along((cx, cy), d + 180.0, BLADE_L / 2)
            out["blades"][arm] = dict(hilt=hilt, dir=d, side=side, chain=out[arm][-1])
        else:
            out["blades"][arm] = dict(hilt=out[arm][-1], dir=b["dir"], side=b["side"], chain=None)
    return out


def shift_pt(p, dx, dy):
    return (p[0] + dx, p[1] + dy)


def to_canvas(sk, shift=0):
    dx, dy = DX + shift, DY
    out = {k: (shift_pt(v, dx, dy) if k == "head" else [shift_pt(p, dx, dy) for p in v])
           for k, v in sk.items() if k != "blades"}
    out["blades"] = {arm: dict(b, hilt=shift_pt(b["hilt"], dx, dy),
                               chain=None if b["chain"] is None else shift_pt(b["chain"], dx, dy))
                     for arm, b in sk["blades"].items()}
    return out


def c(p):
    return (p[0] * PX, p[1] * PX)


def crescent(b):
    """The blade's outline points (design squares): a crescent from the hilt along `dir`, bulging to `side`, a hook at
    the far tip."""
    d, side = b["dir"], b["side"]
    nx, ny = turned((1.0, 0.0), d)
    nx, ny = -nx * side, -ny * side
    outer, inner = [], []
    for k in range(13):
        t = k / 12
        p = along(b["hilt"], d, BLADE_L * t)
        w = BLADE_W * math.sin(math.pi * min(1.0, t * 1.1))
        outer.append((p[0] + nx * w, p[1] + ny * w))
        inner.append((p[0] + nx * w * 0.35, p[1] + ny * w * 0.35))
    tip = along(b["hilt"], d, BLADE_L)
    hook = (tip[0] - nx * BLADE_W * 0.3, tip[1] - ny * BLADE_W * 0.3)
    return outer + [hook] + inner[::-1]


def skeleton(can, s, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    for arm in ("far_arm",):
        b = s["blades"][arm]
        dr.polygon([c(p) for p in crescent(b)], fill=BLADE_COL[arm] + (70,), outline=BLADE_COL[arm] + (alpha,))
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("far_leg", "far_arm", "spine", "near_leg", "near_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == len(pts) - 1 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    b = s["blades"]["near_arm"]
    dr.polygon([c(p) for p in crescent(b)], fill=BLADE_COL["near_arm"] + (70,), outline=BLADE_COL["near_arm"] + (alpha,))
    for arm, b in s["blades"].items():
        dr.ellipse([c(b["hilt"])[0] - 8, c(b["hilt"])[1] - 8, c(b["hilt"])[0] + 8, c(b["hilt"])[1] + 8],
                   outline=BLADE_COL[arm] + (alpha,), width=3)
        if b["chain"] is not None:
            dr.line([c(b["chain"]), c(b["hilt"])], fill=(70, 70, 70, alpha), width=5)
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


def big(a, z=8):
    im = Image.fromarray(up(a, z))
    bg = Image.new("RGBA", im.size, GREY + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def poses_built():
    return {name: (to_canvas(build(spec), spec.get("shift", 0)), zh, en) for name, (zh, en, spec) in POSES.items()}


def rest_built():
    return to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), near_arm="rest",
                                far_arm="rest", near_leg="rest", far_leg="rest", blades=REST["blades"])))


def problems(s):
    """Every bone, the head box and the blades on the canvas; no fist and no blade over the face."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    lim = lambda x, y: x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6
    if any(lim(x, y) for x, y in pts):
        out.append(f"off the canvas / below the ground at {[(round(x), round(y)) for x, y in pts if lim(x, y)][:2]}")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    for arm, b in s["blades"].items():
        poly = crescent(b)
        bad = [(round(x), round(y)) for x, y in poly if x < 0.5 or x > CANVAS / PX - 0.5 or y < 0.5 or y > SOLE_Y / PX + 1.5]
        if bad:
            out.append(f"{arm}'s blade off the canvas / below the ground at {bad[:2]}")
        if any(fx0 <= x <= fx1 and fy0 <= y <= fy1 for x, y in poly):
            out.append(f"{arm}'s blade over the face")
        fist = s[arm][-1]
        if fx0 <= fist[0] <= fx1 and fy0 <= fist[1] <= fy1:
            out.append(f"{arm}'s fist over the face")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.environ.get("TMP", "/tmp"), "ambessa_pose_pack"))
    ap.add_argument("--check")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-lol", action="store_true", help="no League client: the skeletons and the words only")
    a = ap.parse_args()
    frames = {} if a.no_lol else league_clips(a.lol)
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = rest_built()
    bad = 0
    for name, (s, *_) in poses.items():
        for p in problems(s):
            print("PROBLEM", name, p)
            bad += 1
    r0, r1, c0, c1 = HEAD
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        base = canvas_grid()
        base.alpha_composite(on_grid(idle, DX, DY))
        skeleton(base, rest, "the design's own skeleton (REST)", 200)
        base.convert("RGB").save(os.path.join(a.check, "rest_check.png"))
        tiles = []
        for name, (s, zh, en) in poses.items():
            can = canvas_grid()
            hx, hy = s["head"]
            can.alpha_composite(Image.fromarray(up(idle[r0:r1, c0:c1], PX)),
                                (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
            skeleton(can, s, name)
            sk = can.convert("RGB").resize((CANVAS * 2 // 5, CANVAS * 2 // 5))
            if name in frames:   # League's frame beside it (cached)
                cache = os.path.join(a.check, "_league", name + ".png")
                if not os.path.isfile(cache):
                    os.makedirs(os.path.dirname(cache), exist_ok=True)
                    lol_frame(a.lol, frames[name], os.path.join(a.check, "_work")).save(cache)
                lf = Image.open(cache).convert("RGB")
                lf = lf.resize((round(lf.width * sk.height / lf.height), sk.height))
                t = Image.new("RGB", (sk.width + lf.width, sk.height), (255, 255, 255))
                t.paste(sk, (0, 0))
                t.paste(lf, (sk.width, 0))
                sk = t
            tiles.append(sk)
        tile_sheet(tiles, os.path.join(a.check, "poses_check.png"), cols=3 if frames else 5)
        shutil.rmtree(os.path.join(a.check, "_work"), ignore_errors=True)
        print("problems", bad)
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
    for k, (name, (s, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        if name in frames:
            lol_frame(a.lol, frames[name], out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
            print(name, frames[name])
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Hwei's pose pack for Codex (assets/source/hwei/POSE_PROMPTS.md): the whole-body poses his League clips go through,
each with the big paintbrush held somewhere else - the 3/4 design cannot give them by moving its own parts (quarter
turns only: the brush would swing stiffly; the user, 2026-10-22: 「动作帧让 Codex 照骨架画姿势（奇亚娜、乌迪尔那样）」,
pack_qiyana_poses.py's way).

    python tools/art/pack_hwei_poses.py [--out C:/t/hw_work/hwei_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-1, 62 x
76) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames (tools/lol/pose_ref.py
at the 3/4 camera): every bone at the design's OWN length (measured on hd/idle.png at 12x: REST), only its direction set
per pose (POSES), the lowest foot on the ground unless the pose lifts it. Qiyana's poses (2026-10-22) came back with
adult-long legs: the prompt gives the legs' and arms' lengths in squares and asks Codex to count them.
THE BRUSH (his weapon) is a rigid prop: in the design a straight brush BRUSH_L squares long from the butt of the shaft to
the wooden point, held GRIP of the way from the butt, the red-and-navy head from HEAD0 to POINT0 of its length. A pose
gives where the hand holds it ("at") and its direction (deg, butt -> point); the holding arm's wrist goes to the grip.
A dropped brush (hand None) lies where "at" puts its grip.
THE CRESCENT of paint behind him is rigid too: the design's own crescent squares (CRESCENT) moved with his neck, never
turned - drawn translucent on the skeletons.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head with its hair, 8x: every pose wears it); 2_design.png (the design on the grid);
per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right), YELLOW = the brush's shaft,
MAGENTA = its red-and-navy head, CYAN = its wooden point; grey box = the head (the design's head, never redrawn);
the pale blue shape = the crescent.
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
from design_hwei_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "hwei")
PX, CANVAS, SOLE_Y = 12, 1254, 1200
GREY = (225, 225, 225)
GROUND = 76                        # the design's soles' bottom edge (rows)
DX, DY = 21, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 100)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "shaft": (235, 200, 0), "bhead": (230, 40, 200), "point": (0, 200, 220)}
HEAD = (14, 38, 17, 46)            # rows / columns of the head with its hair in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 29 x 24 squares
BRUSH_L = 33.0                     # butt of the shaft to the wooden point (squares)
GRIP, HEAD0, POINT0 = 0.25, 0.42, 0.84
REST_BRUSH = dict(at=(43.5, 54.0), deg=42.5, hand="far_arm")


def crescent_mask(d):
    """The crescent of paint and its drops in hd/idle.png: everything above the hair (rows < 14) and the arc down the
    image left (columns < 15 above row 36, < 12 to row 47)."""
    h, w = d.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    m = (yy < 14) | ((xx < 15) & (yy < 36)) | ((xx < 12) & (yy < 47))
    return m & (d[..., 3] > 0)


# the design's own skeleton, measured on hd/idle.png (62 x 76, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (the near hand by his coat pocket, the far
# hand holding the brush); each leg hip, knee, ankle, toes
REST = {
    "head": (31.5, 26.0),
    "spine": [(27.0, 57.0), (29.0, 37.0)],
    "near_arm": [(19.0, 39.0), (16.0, 47.0), (19.0, 53.0), (21.0, 55.0)],
    "far_arm": [(37.0, 40.0), (39.0, 47.0), (43.5, 54.0), (45.5, 56.0)],
    "near_leg": [(23.0, 57.0), (22.0, 65.0), (22.0, 71.0), (26.5, 75.0)],
    "far_leg": [(31.0, 57.0), (31.0, 65.0), (30.5, 71.0), (35.0, 75.0)],
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest" (the design's own,
# turned with the spine), three angles, or (target, side, last angle): the wrist / ankle at the target with the elbow /
# knee solved at the design's lengths (side -1 bends a downward limb's middle joint to the image right, +1 to the image
# left), then the hand / foot at the last angle; target "grip" = the brush's grip. The brush: "at" where the hand holds
# it, "deg" its direction from the butt to the point, "hand" the arm holding it (None: lying on the ground).
POSES = {
    "a_wind": ("attack01@300",
               "甩笔蓄势：身子往左拧，远侧手臂把画笔横着收到身前左边（笔尖朝画面左边、腰的高度），近侧手臂往左后方垂着，两腿分开站（普攻起手）",
               "WIND-UP - the body twisting to the image left, the FAR arm drawing the brush across in front of his "
               "waist so it lies level with its point to the image left, the near arm hanging back to the left, the "
               "feet apart.",
               dict(pelvis=(27.0, 57.0), lift=None, shift=4, spine=-178, far_arm=("grip", 1, -90),
                    near_arm=(-40, -20, -10), near_leg=((19.0, 71.0), 1, 60), far_leg=((33.0, 71.0), -1, 60),
                    brush=dict(at=(29.0, 51.0), deg=-95, hand="far_arm"))),
    "a_flick": ("attack01@450",
                "甩笔：身子往前倾，远侧手臂往前平伸，画笔往右前方甩出去（笔尖朝右、略往上，肩的高度），近侧手臂往后甩，前腿（远侧）屈膝（普攻出手）",
                "FLICK - leaning forward, the FAR arm stretched forward level, the brush flicked out to the image right "
                "(the point to the right and a little up, at shoulder height), the near arm flung back, the front (far) "
                "knee bent.",
                dict(pelvis=(27.0, 58.0), lift=None, shift=-2, spine=168, far_arm=("grip", -1, 100),
                     near_arm=(-60, -40, -30), near_leg=((17.0, 72.0), 1, 70), far_leg=((37.0, 71.0), -1, 70),
                     brush=dict(at=(50.0, 40.0), deg=100, hand="far_arm"))),
    "q_wind": ("spell1q@175",
               "举笔蓄势：身子微微后仰，远侧手臂把画笔高高举到远侧肩膀上方（笔尖朝上、略往右，不挡脸），近侧手臂往前伸开，近侧腿在前（灾·没骨火起手）",
               "RAISE - leaning back a little, the FAR arm lifting the brush high above his far shoulder (the point up "
               "and a little to the right, never over the face), the near arm reaching forward, the near leg in front.",
               dict(pelvis=(27.0, 57.0), lift=None, shift=0, spine=-176, far_arm=("grip", -1, 170),
                    near_arm=(-20, 40, 80), near_leg=((24.0, 72.0), 1, 70), far_leg=((32.0, 71.0), -1, 60),
                    brush=dict(at=(47.0, 30.0), deg=170, hand="far_arm"))),
    "q_throw": ("spell1q@700",
                "甩笔掷出：大步往前，身子前倾，远侧手臂把画笔从上往前下方甩下来（笔尖朝右下方），近侧手臂往后张开，后腿（近侧）往后伸（灾·没骨火打出）",
                "THROW - a big step forward, leaning forward, the FAR arm swinging the brush down forward (the point to "
                "the lower right), the near arm flung back, the back (near) leg stretched out behind.",
                dict(pelvis=(27.0, 59.0), lift=None, shift=-4, spine=160, far_arm=("grip", -1, 80),
                     near_arm=(-80, -60, -50), near_leg=((14.0, 73.0), 1, 60), far_leg=((38.0, 71.0), -1, 70),
                     brush=dict(at=(50.0, 47.0), deg=60, hand="far_arm"))),
    "qw_raise": ("spell1w@0",
                 "引雷：踮起脚跳起来（脚离地约 4 格），两膝弯着，远侧手臂把画笔笔直举过头顶（笔尖朝上），近侧手臂往左上方张开（灾·攒聚雷起手）",
                 "CALL THE BOLT - hopping up on his toes (the feet about 4 squares up), the knees bent, the FAR arm "
                 "holding the brush straight up above his head (the point up), the near arm flung up and out to the "
                 "upper left.",
                 dict(pelvis=(27.0, 56.0), lift=4, shift=0, spine=180, far_arm=("grip", -1, 175),
                      near_arm=(-130, -140, -150), near_leg=((22.0, 70.0), 1, 30), far_leg=((33.0, 69.0), -1, 50),
                      brush=dict(at=(45.0, 27.0), deg=176, hand="far_arm"))),
    "qw_point": ("spell1w@700",
                 "指地落雷：低低的大弓步，身子前倾，远侧手臂把画笔往右前方指向地面（笔尖朝右下方、快碰到地），近侧手臂往后伸，后腿（近侧）往后伸直（灾·攒聚雷落下）",
                 "POINT DOWN - a deep low lunge, leaning forward, the FAR arm pointing the brush forward and down at the "
                 "ground (the point to the lower right, nearly touching the ground), the near arm stretched back, the "
                 "back (near) leg straight out behind.",
                 dict(pelvis=(26.0, 62.0), lift=None, shift=-4, spine=150, far_arm=("grip", -1, 60),
                      near_arm=(-80, -70, -60), near_leg=((10.0, 74.0), 1, -70), far_leg=((38.0, 72.0), -1, 70),
                      brush=dict(at=(48.0, 52.0), deg=58, hand="far_arm"))),
    "qe_raise": ("spell1e@350",
                 "跃起竖笔：跳起来（脚离地约 6 格），两膝收起，远侧手把画笔竖着握在身前右边（笔尖朝下），近侧手臂往左张开（灾·连皴山起跳）",
                 "LEAP WITH THE BRUSH - leaping up (the feet about 6 squares up), both knees tucked, the FAR hand "
                 "holding the brush upright in front of him on the image right (the point DOWN), the near arm flung out "
                 "to the left.",
                 dict(pelvis=(27.0, 56.0), lift=6, shift=0, spine=178, far_arm=("grip", -1, 20),
                      near_arm=(-110, -100, -90), near_leg=((25.0, 64.0), 1, 70), far_leg=((34.0, 64.0), -1, 70),
                      brush=dict(at=(45.0, 41.0), deg=4, hand="far_arm"))),
    "qe_slam": ("spell1e@1050",
                "落地插笔：深深蹲下（低弓步），远侧手把画笔往前下方插进地里（笔尖碰到右前方的地面），近侧手臂往左后方张开（灾·连皴山落地）",
                "STAB DOWN - landed in a deep low crouch, the FAR hand driving the brush down in front of him, its "
                "point touching the ground at the image right, the near arm flung back to the left.",
                dict(pelvis=(26.0, 63.0), lift=None, shift=-2, spine=158, far_arm=("grip", -1, 30),
                     near_arm=(-90, -80, -70), near_leg=((12.0, 74.0), 1, -60), far_leg=((36.0, 72.0), -1, 70),
                     brush=dict(at=(45.0, 50.0), deg=22, hand="far_arm"))),
    "ew_low": ("spell3w@150",
               "低扫：两腿大开站低，身子前倾，远侧手臂把画笔往左下方扫到身后（笔尖朝左下、贴近地面），近侧手臂往左张开（悚·滞涩幽瞳起手）",
               "LOW SWEEP - a wide low stance, leaning forward, the FAR arm sweeping the brush down to the lower left "
               "behind him (the point to the lower left, near the ground), the near arm flung out to the left.",
               dict(pelvis=(28.0, 60.0), lift=None, shift=6, spine=168, far_arm=("grip", 1, -60),
                    near_arm=(-110, -90, -80), near_leg=((14.0, 74.0), 1, -40), far_leg=((40.0, 73.0), -1, 60),
                    brush=dict(at=(30.0, 55.0), deg=-62, hand="far_arm"))),
    "ew_high": ("spell3w@600",
                "高举：站直，远侧手臂把画笔往右上方高高举起（笔尖朝右上方，不挡脸），近侧手臂垂在身边，近侧腿在前（悚·滞涩幽瞳睁眼）",
                "HIGH POINT - standing tall, the FAR arm raising the brush high to the upper right (the point to the "
                "upper right, never over the face), the near arm hanging at his side, the near leg in front.",
                dict(pelvis=(27.0, 57.0), lift=None, shift=-2, spine=178, far_arm=("grip", -1, 150),
                     near_arm="rest", near_leg=((20.0, 72.0), 1, 60), far_leg=((33.0, 71.0), -1, 60),
                     brush=dict(at=(48.0, 31.0), deg=148, hand="far_arm"))),
    "ee_wind": ("spell3e@0",
                "横笔蓄势：弓步，身子往左拧，远侧手臂把画笔横着拉到身后左边（笔尖朝画面左边，胸口的高度，不挡脸），近侧手臂往左后方张开（悚·双钩血喉起手）",
                "DRAW BACK - in a lunge, twisting to the image left, the FAR arm pulling the brush back level behind him "
                "to the image left (the point to the left, at chest height, below the face), the near arm flung back "
                "to the left.",
                dict(pelvis=(28.0, 59.0), lift=None, shift=6, spine=-174, far_arm=("grip", 1, -90),
                     near_arm=(-100, -110, -120), near_leg=((16.0, 73.0), 1, -30), far_leg=((38.0, 72.0), -1, 60),
                     brush=dict(at=(26.0, 43.0), deg=-92, hand="far_arm"))),
    "ee_swing": ("spell3e@350",
                 "下劈：往前压低，远侧手臂把画笔从左往右前下方劈下来（笔尖朝右下方），近侧手臂往后甩，前腿（远侧）屈膝（悚·双钩血喉咬合）",
                 "CHOP - pressing forward low, the FAR arm chopping the brush down forward (the point to the lower "
                 "right), the near arm flung back, the front (far) knee bent.",
                 dict(pelvis=(27.0, 60.0), lift=None, shift=-4, spine=156, far_arm=("grip", -1, 60),
                      near_arm=(-70, -60, -50), near_leg=((14.0, 74.0), 1, -50), far_leg=((38.0, 72.0), -1, 70),
                      brush=dict(at=(49.0, 50.0), deg=48, hand="far_arm"))),
    "r_open": ("spell4_alex@200",
               "张开双臂：站直，两只手臂往两边张开，远侧手把画笔平平地伸向右边（笔尖朝右），近侧手掌朝上张在左边（大招起手）",
               "ARMS WIDE - standing tall, both arms spread wide, the FAR hand holding the brush out level to the image "
               "right (the point to the right), the near hand open, palm up, out to the left.",
               dict(pelvis=(27.0, 57.0), lift=None, shift=-2, spine=178, far_arm=("grip", -1, 100),
                    near_arm=(-120, -100, -100), near_leg=((20.0, 72.0), 1, 60), far_leg=((35.0, 71.0), -1, 70),
                    brush=dict(at=(51.0, 42.0), deg=92, hand="far_arm"))),
    "r_fling": ("spell4_alex@400",
                "甩出画卷：身子前倾，远侧手臂把画笔往前用力甩出去（笔尖朝右、略往下），近侧手臂往后张开，大步往前（大招打出）",
                "FLING - leaning forward, the FAR arm flinging the brush forward hard (the point to the right and a "
                "little down), the near arm flung back, a big step forward.",
                dict(pelvis=(27.0, 59.0), lift=None, shift=-4, spine=162, far_arm=("grip", -1, 90),
                     near_arm=(-90, -80, -70), near_leg=((14.0, 73.0), 1, 60), far_leg=((39.0, 71.0), -1, 70),
                     brush=dict(at=(52.0, 44.0), deg=80, hand="far_arm"))),
    "r_hop": ("spell4_alex@800",
              "跃起：轻轻跳起（脚离地约 6 格），两膝收起，远侧手臂把画笔横着收到身后左边（笔尖朝画面左边、腰的高度），近侧手臂收在胸前（大招收尾）",
              "HOP - a light hop (the feet about 6 squares up), both knees tucked, the FAR arm drawing the brush back "
              "level behind him at his waist (the point to the image left), the near arm bent before his chest.",
              dict(pelvis=(27.0, 56.0), lift=6, shift=2, spine=176, far_arm=("grip", 1, -90),
                   near_arm=(-20, 60, 80), near_leg=((24.0, 64.0), 1, 80), far_leg=((33.0, 64.0), -1, 80),
                   brush=dict(at=(30.0, 49.0), deg=-100, hand="far_arm"))),
    "run1": ("runslow@0", "跑 1（远侧腿在前着地，近侧腿往后抬起）：身子微微前倾，远侧手握着画笔斜拖在右下方（和定稿一样），近侧手臂往后摆",
             "RUN 1 - the FAR leg forward with its foot landing, the NEAR leg kicked up behind him, leaning forward a "
             "little, the FAR hand trailing the brush down to the lower right as in the design, the near arm swinging "
             "back.",
             dict(pelvis=(27.0, 57.0), lift=None, shift=0, spine=172, far_arm=("grip", -1, 50),
                  near_arm=(-30, -10, 10), near_leg=((16.0, 69.0), 1, -60), far_leg=((35.0, 71.0), -1, 60),
                  brush=dict(at=(44.0, 52.0), deg=48, hand="far_arm"))),
    "run2": ("runslow@242", "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，画笔一样斜拖着",
             "RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square "
             "higher, the brush trailing to the lower right as before, the near arm swinging down.",
             dict(pelvis=(27.0, 56.0), lift=1, shift=0, spine=174, far_arm=("grip", -1, 50),
                  near_arm=(-10, 0, 10), near_leg=((25.0, 71.0), 1, 60), far_leg=((36.0, 64.0), -1, 70),
                  brush=dict(at=(44.0, 51.0), deg=46, hand="far_arm"))),
    "run3": ("runslow@483", "跑 3（近侧腿在前着地，远侧腿往后抬起）",
             "RUN 3 - the NEAR leg forward with its foot landing, the FAR leg kicked up behind him, leaning forward a "
             "little, the brush trailing to the lower right, the near arm swinging forward.",
             dict(pelvis=(27.0, 57.0), lift=None, shift=0, spine=172, far_arm=("grip", -1, 50),
                  near_arm=(10, 40, 60), near_leg=((34.0, 71.0), 1, 70), far_leg=((22.0, 68.0), 1, -60),
                  brush=dict(at=(44.0, 52.0), deg=48, hand="far_arm"))),
    "run4": ("runslow@725", "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格",
             "RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square "
             "higher, the brush trailing to the lower right, the near arm swinging down.",
             dict(pelvis=(27.0, 56.0), lift=1, shift=0, spine=174, far_arm=("grip", -1, 50),
                  near_arm=(0, 10, 20), near_leg=((30.0, 64.0), -1, 80), far_leg=((30.0, 71.0), -1, 60),
                  brush=dict(at=(44.0, 51.0), deg=46, hand="far_arm"))),
    "d_stagger": ("death@675",
                  "踉跄：身子往左后方倒，膝盖弯下去，近侧手捂着胸口，远侧手臂垂下张开，画笔从手里掉落、平躺在他右前方的地上（死亡第一下）",
                  "STAGGER - reeling back toward the image left, the knees buckling, the near hand clutching his chest, "
                  "the far arm hanging open, the brush dropped from his hand and lying flat on the ground in front of "
                  "him on the image right.",
                  dict(pelvis=(28.0, 59.0), lift=None, shift=0, spine=-164, far_arm=(20, 10, 0),
                       near_arm=((30.0, 43.0), 1, 60), near_leg=((20.0, 73.0), 1, 40), far_leg=((34.0, 72.0), -1, 50),
                       brush=dict(at=(46.0, 74.5), deg=90, hand=None))),
    "d_kneel": ("death@2025",
                "跪倒：近侧膝盖跪在地上，远侧腿立着膝盖，身子往前弯，近侧手撑在地上，远侧手搭在膝盖上，头低着；画笔平躺在他右前方的地上（死亡）",
                "DOWN - kneeling on the near knee, the far knee raised, bent forward, the near hand propped on the "
                "ground, the far hand on the raised knee, the head low; the brush lying flat on the ground in front of "
                "him on the image right.",
                dict(pelvis=(26.0, 64.0), lift=None, shift=0, spine=160, far_arm=((38.0, 62.0), -1, 40),
                     near_arm=((26.0, 74.0), 1, 20), near_leg=((22.0, 75.0), 1, -90), far_leg=((36.0, 74.0), -1, 60),
                     brush=dict(at=(46.0, 74.5), deg=90, hand=None))),
}


def ang(a, b):
    """The direction a -> b in degrees (0 = straight down, 90 = to the image right; y down)."""
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))


def along(p, deg, length):
    r = math.radians(deg)
    return (p[0] + length * math.sin(r), p[1] + length * math.cos(r))


def turned(v, deg):
    """A vector turned the way ang() counts: +deg turns straight down towards the image right."""
    r = math.radians(deg)
    x, y = v
    return (x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r))


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def brush_point(b, f):
    """The point `f` of the way from the brush's butt (0) to its point (1)."""
    return along(b["at"], b["deg"], (f - GRIP) * BRUSH_L)


def bend(H, A, l1, l2, side):
    """The middle joint of a two-bone limb from H towards A (A pulled in or pushed out to what the bones reach): side +1
    puts it to the image left of a limb pointing down, -1 to the image right (pack_shyvana_poses.bend)."""
    vx, vy = A[0] - H[0], A[1] - H[1]
    d = math.hypot(vx, vy) or 1e-9
    d2 = max(abs(l1 - l2) + 0.3, min(l1 + l2 - 0.05, d))
    ux, uy = vx / d, vy / d
    a = (l1 * l1 - l2 * l2 + d2 * d2) / (2 * d2)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    px, py = -uy, ux
    if side < 0:
        px, py = -px, -py
    M = (H[0] + ux * a + px * h, H[1] + uy * a + py * h)
    return M, (H[0] + ux * d2, H[1] + uy * d2)


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned), the crescent with it. The lowest foot or knee on the ground, or `lift` rows over it; a held
    brush moves with him, a dropped one stays where it lies."""
    brush = spec["brush"]
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1]),
          "neck_shift": (neck[0] - rs[1][0], neck[1] - rs[1][1])}
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
        if len(sp) == 3 and (sp[0] == "grip" or isinstance(sp[0], tuple)):
            target, side, last = sp
            M, A = bend(pts[0], brush["at"] if target == "grip" else target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    low = max(y for leg in ("near_leg", "far_leg") for _, y in sk[leg])
    dy = REST["near_leg"][-1][1] - (spec["lift"] or 0) - low
    moved = {}
    for k, v in sk.items():
        if k in ("head",):
            moved[k] = (v[0], v[1] + dy)
        elif k == "neck_shift":
            moved[k] = (v[0], v[1] + dy)
        else:
            moved[k] = [(x, y + dy) for x, y in v]
    held = brush.get("hand") is not None
    moved["brush"] = dict(brush, at=(brush["at"][0], brush["at"][1] + (dy if held else 0.0)))
    return moved


def to_canvas(sk, shift=0):
    out = {}
    for k, v in sk.items():
        if k == "head":
            out[k] = (v[0] + DX + shift, v[1] + DY)
        elif k == "neck_shift":
            out[k] = v
        elif k == "brush":
            out[k] = dict(v, at=(v["at"][0] + DX + shift, v["at"][1] + DY))
        else:
            out[k] = [(x + DX + shift, y + DY) for x, y in v]
    out["origin"] = (DX + shift + out["neck_shift"][0], DY + out["neck_shift"][1])
    return out


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
    """A point in design square edges, already on the canvas grid, in canvas px."""
    return (p[0] * PX, p[1] * PX)


def crescent_layer(idle, origin, alpha):
    """The design's crescent squares, moved with the neck (origin: the design's (0, 0) on the canvas grid)."""
    m = crescent_mask(idle)
    lay = np.zeros(idle.shape[:2] + (4,), np.uint8)
    lay[m] = (150, 200, 245, alpha)
    im = Image.fromarray(up(lay, PX))
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    out.paste(im, (round(origin[0] * PX), round(origin[1] * PX)))
    return out


def skeleton(can, s, label, idle, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    can.alpha_composite(crescent_layer(idle, s["origin"], 110 if alpha == 255 else 70))
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    b = s["brush"]
    dr.line([c(brush_point(b, 0)), c(brush_point(b, HEAD0))], fill=COL["shaft"] + (alpha,), width=7)
    dr.line([c(brush_point(b, HEAD0)), c(brush_point(b, POINT0))], fill=COL["bhead"] + (alpha,), width=15)
    dr.line([c(brush_point(b, POINT0)), c(brush_point(b, 1))], fill=COL["point"] + (alpha,), width=9)
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    order = [("far_leg", 7), ("spine", 7), ("near_leg", 7), ("near_arm", 7), ("far_arm", 7)]
    for name, w in order:
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=w, joint="curve")
        for p in pts:
            rr = 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work):
    """League's frame at the 3/4 camera."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Hwei",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900",
           "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work,
           "--frame", frame]
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
    """Every bone, brush point and head box on the canvas; the holding wrist on the grip; no hand or brush over the
    face; a held brush's point not below the ground."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    b = s["brush"]
    bpts = [brush_point(b, f / 20) for f in range(21)]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts + bpts):
        out.append("off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1:
        out.append("head off the top")
    if b.get("hand"):
        w = s[b["hand"]][2]
        if math.hypot(b["at"][0] - w[0], b["at"][1] - w[1]) > 0.6:
            sh = s[b["hand"]][0]
            out.append(f"the {b['hand']} cannot reach the grip ({math.hypot(b['at'][0] - sh[0], b['at'][1] - sh[1]):.1f}"
                       f" squares from the shoulder)")
    fx0, fx1, fy0, fy1 = hx - 4, hx + 7, hy - 1, hy + 8      # the face: eyes to mouth
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] + bpts if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/hw_work/hwei_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(dict(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), far_arm="rest",
                                     near_arm="rest", near_leg="rest", far_leg="rest", brush=REST_BRUSH))))
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        base = canvas_grid()
        base.alpha_composite(on_grid(idle, DX, DY))
        skeleton(base, rest, "the design's own skeleton (REST)", idle, 200)
        base.convert("RGB").save(os.path.join(a.check, "rest_check.png"))
        names = a.only.split(",") if a.only else list(poses)
        cache = os.path.join(a.check, "_league")
        os.makedirs(cache, exist_ok=True)
        tiles = []
        for name in names:
            s, frame, zh, en = poses[name]
            can = canvas_grid()
            hx, hy = s["head"]                       # the design's head in its box, to judge the chibi proportions
            r0, r1, c0, c1 = HEAD
            can.alpha_composite(Image.fromarray(up(idle[r0:r1, c0:c1], PX)),
                                (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
            skeleton(can, s, name, idle)
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
        W = max(t.width for t in tiles)
        cols = 3
        rows_ = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (W * cols, tiles[0].height * rows_), (255, 255, 255))
        for k, t in enumerate(tiles):
            sheet.paste(t, ((k % cols) * W, (k // cols) * t.height))
        sheet.save(os.path.join(a.check, "poses_check.png"))
        shutil.rmtree(os.path.join(a.check, "_work"), ignore_errors=True)
        return
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    base = canvas_grid()
    base.alpha_composite(on_grid(idle, DX, DY))
    clean = base.copy()
    skeleton(base, rest, "0: the approved design with its own skeleton (what each coloured line stands for)", idle, 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})", idle)
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

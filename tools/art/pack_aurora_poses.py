#!/usr/bin/env python3
"""Aurora's pose pack for Codex (assets/source/aurora/POSE_PROMPTS.md): the whole-body poses her League clips go through,
each with her long wand held somewhere else (the user, 2026-10-23: 「Codex 照骨架画姿势」, pack_hwei_poses.py's way).

    python tools/art/pack_aurora_poses.py [--out C:/t/au_work/aurora_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-2 read at
PPU 2.25, 53 x 104) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames
(tools/lol/pose_ref.py at the 3/4 camera): every bone at the design's OWN length (measured on hd/idle.png at 16x: REST),
only its direction set per pose (POSES), the lowest foot on the ground unless the pose lifts it. The prompt gives the
legs' and arms' lengths in squares and asks Codex to count them (Qiyana's adult-long legs, 2026-10-22).
HER HEAD is most of her: the hat, the hair, the glasses and the two long ears are rows 0-55 of 104 (HEAD) - pasted on
every pose upright, never turned; her chibi arms (about 23 squares to the fingertips) cannot lift anything over it, so the wand goes up
beside the head, never over it.
THE WAND is a rigid prop: in the design a straight wand WAND_L squares long from its red butt to its blue tip, held GRIP
of the way from the butt (the far hand, resting it on her shoulder pointing up and back), the blue glow from TIP0. A pose
gives where the hand holds it ("at") and its direction (deg, butt -> tip); the holding arm's wrist goes to the grip.
A dropped wand (hand None) lies where "at" puts its grip.
THE TAIL (the fluffy orange tail behind her) is rigid too: the design's own tail squares (tail_mask) moved with her
pelvis, never turned - drawn translucent on the skeletons.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head with its hat and ears, 8x: every pose wears it); 2_design.png (the design on the grid);
per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left, the hand hanging at her side), PURPLE = the FAR arm (image right, holding
the wand), YELLOW = the wand's shaft, CYAN = its blue glowing tip; grey box = the head (the design's head, never redrawn);
the translucent orange shape = the tail.
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
from design_aurora_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aurora")
PX, CANVAS, SOLE_Y = 9, 1254, 1197
GREY = (225, 225, 225)
GROUND = 104                       # the design's soles' bottom edge (rows)
DX, DY = 30, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 133)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "shaft": (235, 200, 0), "point": (0, 200, 220)}
HEAD = (0, 56, 3, 51)              # rows / columns of the head with the hat and the ears in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 48 x 56 squares
FACE = (24, 40, 38, 53)            # the face (the glasses, the eyes, the mouth): x0, x1, y0, y1 in design squares
WAND_L = 62.0                      # the red butt to the blue tip (squares): (51, 62) -> (2, 24) in the design
GRIP, TIP0 = 0.126, 0.95
REST_WAND = dict(at=(45.0, 57.0), deg=-127.8, hand="far_arm", behind=True)


def tail_mask(d):
    """The tail in hd/idle.png: its orange and red fur left of the coat (columns < 21, rows 62-84)."""
    h, w = d.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    c = d[..., :3].astype(int)
    fur = (c[..., 0] > 150) & (c[..., 1] < 140) & (c[..., 2] < 90)
    return (xx < 21) & (yy >= 62) & (yy <= 84) & fur & (d[..., 3] > 0)


# the design's own skeleton, measured on hd/idle.png (53 x 104, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (the near hand hanging at her side, the far
# hand on the wand at her shoulder); each leg hip, knee, ankle, toes
REST = {
    "head": (27.0, 28.0),
    "spine": [(31.0, 78.0), (31.0, 57.0)],
    "near_arm": [(22.0, 58.0), (18.0, 68.0), (15.0, 76.0), (13.0, 79.0)],
    "far_arm": [(39.0, 58.0), (43.0, 65.0), (45.0, 58.0), (46.0, 55.0)],
    "near_leg": [(27.0, 78.0), (26.0, 88.0), (26.0, 96.0), (31.0, 102.0)],
    "far_leg": [(35.0, 78.0), (36.0, 88.0), (36.0, 96.0), (42.0, 101.0)],
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest" (the design's own,
# turned with the spine), three angles, or (target, side, last angle): the wrist / ankle at the target with the elbow /
# knee solved at the design's lengths (side -1 bends a downward limb's middle joint to the image right, +1 to the image
# left), then the hand / foot at the last angle; target "grip" = the wand's grip. The wand: "at" where the hand holds
# it, "deg" its direction from the butt to the tip, "hand" the arm holding it (None: lying on the ground).
SHOULDER = dict(at=(45.0, 57.0), deg=-127.8, hand="far_arm", behind=True)   # on her shoulder BEHIND her head, as in the design
POSES = {
    "a_wind": ("attack6@0",
               "举杖：站直，远侧手把魔杖举到头的右边（杖头朝右上方，不挡脸），近侧手臂往左边张开（普攻起手）",
               "RAISE - standing tall, the FAR hand lifting the wand up beside her head on the image right (the tip to "
               "the upper right, never over the face), the near arm opened out to the left.",
               dict(pelvis=(31.0, 78.0), lift=None, shift=0, spine=180, far_arm=("grip", -1, 160),
                    near_arm=(-60, -40, -30), near_leg=((25.0, 96.0), 1, 60), far_leg=((37.0, 96.0), -1, 70),
                    wand=dict(at=(46.0, 50.0), deg=150, hand="far_arm"))),
    "a_point": ("attack6@329",
                "点出：身子往前倾，远侧手臂往前平伸，魔杖往右前方点出去（杖头朝右、略往上，肩的高度），近侧手臂往后甩，两腿分开（普攻出手）",
                "POINT - leaning forward, the FAR arm stretched forward level, the wand thrust out to the image right "
                "(the tip to the right and a little up, at shoulder height), the near arm flung back, the feet apart.",
                dict(pelvis=(31.0, 78.0), lift=None, shift=-6, spine=172, far_arm=("grip", -1, 100),
                     near_arm=(-70, -55, -45), near_leg=((23.0, 96.0), 1, 50), far_leg=((39.0, 96.0), -1, 70),
                     wand=dict(at=(51.0, 60.0), deg=100, hand="far_arm"))),
    "q_wind": ("spell1@158",
               "蓄力：轻轻跳起（脚离地约 3 格），身子往后仰，远侧手把魔杖竖着举在头的右边（杖头朝上，不挡脸），近侧手臂往左上方扬起（飞去来咒起手）",
               "WIND-UP - a small hop (the feet about 3 squares up), leaning back, the FAR hand holding the wand upright "
               "beside her head on the image right (the tip UP, never over the face), the near arm flung up to the "
               "upper left.",
               dict(pelvis=(31.0, 78.0), lift=3, shift=0, spine=-176, far_arm=("grip", -1, 175),
                    near_arm=(-140, -150, -160), near_leg=((26.0, 94.0), 1, 40), far_leg=((36.0, 95.0), -1, 50),
                    wand=dict(at=(46.0, 47.0), deg=176, hand="far_arm"))),
    "q_cast": ("spell1@317",
               "甩出：大步往前，身子前倾，远侧手臂把魔杖往右前下方甩出去（杖头朝右下方），近侧手臂往左张开，两腿大大分开（飞去来咒放出）",
               "CAST - a big step forward, leaning forward, the FAR arm sweeping the wand out to the lower right (the "
               "tip to the lower right), the near arm flung out to the left, the legs wide apart.",
               dict(pelvis=(31.0, 79.0), lift=None, shift=-4, spine=166, far_arm=("grip", -1, 70),
                    near_arm=(-100, -90, -80), near_leg=((20.0, 96.0), 1, -60), far_leg=((41.0, 96.0), -1, 70),
                    wand=dict(at=(51.0, 64.0), deg=58, hand="far_arm"))),
    "q_catch": ("spell1_recast@1050",
                "收回：踮脚站高（脚离地约 2 格），远侧手把魔杖笔直举在身子右边（杖头朝上，不挡脸），近侧手臂往左张开、手掌朝上，像在接住飞回来的东西（飞去来咒收回）",
                "RECALL - up on her toes (the feet about 2 squares up), the FAR hand holding the wand straight up at "
                "her side on the image right (the tip UP, never over the face), the near arm open to the left, palm "
                "up, as if catching something flying back.",
                dict(pelvis=(31.0, 78.0), lift=2, shift=0, spine=178, far_arm=("grip", -1, 178),
                     near_arm=(-110, -100, -90), near_leg=((28.0, 96.0), 1, 30), far_leg=((35.0, 96.0), -1, 40),
                     wand=dict(at=(47.0, 52.0), deg=179, hand="far_arm"))),
    "e_push": ("spell3_reblock3@225",
               "蹲下推出：两膝往外分开深深蹲下，身子前倾，两只手一起握着魔杖往右前下方推出去（杖头朝右下方），尾巴翘在身后（怪奇喷涌放出）",
               "BLAST - squatting deep with the knees spread apart, leaning forward, BOTH hands holding the wand and "
               "thrusting it out to the lower right (the tip to the lower right), the tail up behind her.",
               dict(pelvis=(31.0, 85.0), lift=None, shift=-2, spine=160, far_arm=("grip", -1, 60),
                    near_arm=("grip", -1, 60), near_leg=((21.0, 96.0), 1, -40), far_leg=((41.0, 96.0), -1, 60),
                    wand=dict(at=(47.0, 70.0), deg=55, hand="far_arm"))),
    "e_hop": ("spell3_reblock3@563",
              "向后跳：往后（画面左边）跳起（脚离地约 10 格），两膝收起，身子往后仰，远侧手把魔杖扛回肩上（和定稿一样），近侧手臂往前伸（怪奇喷涌后跳）",
              "HOP BACK - jumping back toward the image left (the feet about 10 squares up), both knees tucked, leaning "
              "back, the FAR hand resting the wand on her shoulder again as in the design, the near arm reaching "
              "forward.",
              dict(pelvis=(31.0, 78.0), lift=10, shift=6, spine=-170, far_arm=("grip", -1, 170),
                   near_arm=(40, 60, 70), near_leg=((25.0, 90.0), 1, 30), far_leg=((37.0, 92.0), -1, 40),
                   wand=dict(at=(44.0, 55.0), deg=-125, hand="far_arm", behind=True))),
    "r_reach": ("spell4_e@0",
                "踮脚张开：踮起脚站得高高的，近侧手臂往左边平平张开，远侧手把魔杖往右下方斜指（杖头朝右下方），像要往前一跃（双界合一起手）",
                "REACH - standing tall on her toes, the near arm spread out level to the left, the FAR hand pointing the "
                "wand down to the lower right (the tip to the lower right), about to leap.",
                dict(pelvis=(31.0, 78.0), lift=2, shift=0, spine=176, far_arm=("grip", -1, 50),
                     near_arm=(-100, -95, -90), near_leg=((29.0, 96.0), 1, 20), far_leg=((34.0, 96.0), -1, 30),
                     wand=dict(at=(49.0, 64.0), deg=45, hand="far_arm"))),
    "r_leap": ("spell4_e@267",
               "高高跃起：往右上方跳得很高（脚离地约 12 格），两膝收在身下，远侧手把魔杖扛在肩上（和定稿一样），近侧手臂往左后方张开（双界合一跳起）",
               "LEAP - jumping high to the upper right (the feet about 12 squares up), both knees tucked under her, the "
               "FAR hand resting the wand on her shoulder as in the design, the near arm flung back to the left.",
               dict(pelvis=(31.0, 78.0), lift=12, shift=-2, spine=172, far_arm=("grip", -1, 170),
                    near_arm=(-80, -100, -110), near_leg=((25.0, 88.0), 1, 20), far_leg=((37.0, 90.0), -1, 30),
                    wand=dict(at=(45.0, 56.0), deg=-122, hand="far_arm", behind=True))),
    "r_land": ("spell1_recast@700",
               "落地：两膝并拢蹲下落地，身子前倾，远侧手把魔杖往右前下方指向地面（杖头快碰到地），近侧手臂往左张开保持平衡（双界合一落地、冲击波）",
               "LAND - landing in a crouch with the knees together, leaning forward, the FAR hand pointing the wand "
               "down at the ground to the lower right (the tip nearly touching the ground), the near arm out to the "
               "left for balance.",
               dict(pelvis=(31.0, 84.0), lift=None, shift=-2, spine=165, far_arm=("grip", -1, 60),
                    near_arm=(-90, -80, -70), near_leg=((26.0, 96.0), 1, -20), far_leg=((36.0, 96.0), -1, 40),
                    wand=dict(at=(48.0, 68.0), deg=50, hand="far_arm"))),
    "w_hop": ("spell2@233",
              "翻身后跳：往后（画面左边）高高跳起（脚离地约 10 格），整个人缩成一团，两膝收到胸前，远侧手把魔杖抱在肩上，近侧手臂抱住膝盖，尾巴甩在身后（灵纱洞开）",
              "VEIL HOP - leaping high back toward the image left (the feet about 10 squares up), curled up in a ball, "
              "both knees pulled up to the chest, the FAR hand holding the wand on her shoulder, the near arm hugging "
              "the knees, the tail flung out behind her.",
              dict(pelvis=(31.0, 80.0), lift=10, shift=6, spine=-168, far_arm=("grip", -1, 170),
                   near_arm=(20, 70, 80), near_leg=((33.0, 86.0), -1, 60), far_leg=((39.0, 88.0), -1, 60),
                   wand=dict(at=(44.0, 56.0), deg=-130, hand="far_arm", behind=True))),
    "run1": ("run_new_4@0",
             "跑 1（远侧腿往前迈出着地，近侧腿往后伸）：身子微微前倾，魔杖扛在肩上（和定稿一样），近侧手臂往后摆",
             "RUN 1 - a stride: the FAR leg forward with its foot landing, the NEAR leg stretched back, leaning forward "
             "a little, the wand resting on her shoulder as in the design, the near arm swinging back.",
             dict(pelvis=(31.0, 78.0), lift=None, shift=0, spine=174, far_arm=("grip", -1, 170),
                  near_arm=(-30, -10, 0), near_leg=((20.0, 94.0), 1, -60), far_leg=((40.0, 96.0), -1, 60),
                  wand=SHOULDER)),
    "run2": ("run_new_4@217",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，魔杖一样扛在肩上",
             "RUN 2 - the near leg under the body carrying her, the FAR knee lifted forward, the body one square "
             "higher, the wand on her shoulder as before, the near arm swinging down.",
             dict(pelvis=(31.0, 77.0), lift=1, shift=0, spine=176, far_arm=("grip", -1, 170),
                  near_arm=(-10, 0, 10), near_leg=((28.0, 96.0), 1, 60), far_leg=((40.0, 89.0), -1, 70),
                  wand=SHOULDER)),
    "run3": ("run_new_4@433",
             "跑 3（近侧腿往前迈出着地，远侧腿往后伸）",
             "RUN 3 - the NEAR leg forward with its foot landing, the FAR leg stretched back, leaning forward a little, "
             "the wand on her shoulder, the near arm swinging forward.",
             dict(pelvis=(31.0, 78.0), lift=None, shift=0, spine=174, far_arm=("grip", -1, 170),
                  near_arm=(20, 40, 50), near_leg=((38.0, 96.0), -1, 70), far_leg=((24.0, 94.0), 1, -60),
                  wand=SHOULDER)),
    "run4": ("run_new_4@650",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格",
             "RUN 4 - the far leg under the body carrying her, the NEAR knee lifted forward, the body one square higher, "
             "the wand on her shoulder, the near arm swinging down.",
             dict(pelvis=(31.0, 77.0), lift=1, shift=0, spine=176, far_arm=("grip", -1, 170),
                  near_arm=(0, 10, 20), near_leg=((34.0, 89.0), -1, 80), far_leg=((34.0, 96.0), -1, 60),
                  wand=SHOULDER)),
    "d_stagger": ("death@517",
                  "踉跄：身子往左后方倒，膝盖弯下去，两只手臂往两边张开，魔杖从手里松开、斜斜地往右下方垂着（死亡第一下）",
                  "STAGGER - reeling back toward the image left, the knees buckling, both arms flung out to the sides, "
                  "the wand slipping in the far hand, hanging down to the lower right.",
                  dict(pelvis=(31.0, 80.0), lift=None, shift=0, spine=-166, far_arm=("grip", -1, 30),
                       near_arm=(-110, -120, -130), near_leg=((24.0, 96.0), 1, 40), far_leg=((37.0, 96.0), -1, 50),
                       wand=dict(at=(46.0, 66.0), deg=60, hand="far_arm"))),
    "d_slump": ("death@1292",
                "坐倒：一屁股坐在地上，两腿往前（画面右边）伸，膝盖微微弯，身子往后仰，近侧手撑在身后的地上，远侧手搭在腿上；魔杖平躺在她身下的地上，杖头朝左（死亡）",
                "DOWN - sitting down on the ground, both legs stretched forward to the image right with the knees a "
                "little bent, leaning back, the near hand propped on the ground behind her, the far hand resting on "
                "her leg; the wand lying flat on the ground under her, its tip to the image left.",
                dict(pelvis=(31.0, 99.0), lift=None, shift=-6, spine=-170, far_arm=((46.0, 96.0), -1, 90),
                     near_arm=((20.0, 103.0), 1, -60), near_leg=((44.0, 101.0), -1, 90), far_leg=((50.0, 100.0), -1, 90),
                     wand=dict(at=(58.0, 103.0), deg=-90, hand=None))),
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


def wand_point(b, f):
    """The point `f` of the way from the wand's butt (0) to its point (1)."""
    return along(b["at"], b["deg"], (f - GRIP) * WAND_L)


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
    pasted, never turned), the tail with the pelvis. The lowest foot or knee on the ground, or `lift` rows over it; a held
    wand moves with him, a dropped one stays where it lies."""
    wand = spec["wand"]
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1]),
          "neck_shift": (neck[0] - rs[1][0], neck[1] - rs[1][1]), "pelvis_shift": (pel[0] - rs[0][0], pel[1] - rs[0][1])}
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
            M, A = bend(pts[0], wand["at"] if target == "grip" else target, ls[0], ls[1], side)
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
        elif k in ("neck_shift", "pelvis_shift"):
            moved[k] = (v[0], v[1] + dy)
        else:
            moved[k] = [(x, y + dy) for x, y in v]
    held = wand.get("hand") is not None
    moved["wand"] = dict(wand, at=(wand["at"][0], wand["at"][1] + (dy if held else 0.0)))
    return moved


def to_canvas(sk, shift=0):
    out = {}
    for k, v in sk.items():
        if k == "head":
            out[k] = (v[0] + DX + shift, v[1] + DY)
        elif k in ("neck_shift", "pelvis_shift"):
            out[k] = v
        elif k == "wand":
            out[k] = dict(v, at=(v["at"][0] + DX + shift, v["at"][1] + DY))
        else:
            out[k] = [(x + DX + shift, y + DY) for x, y in v]
    out["origin"] = (DX + shift + out["neck_shift"][0], DY + out["neck_shift"][1])
    out["tail_origin"] = (DX + shift + out["pelvis_shift"][0], DY + out["pelvis_shift"][1])
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


def tail_layer(idle, origin, alpha):
    """The design's tail squares, moved with the pelvis (origin: the design's (0, 0) on the canvas grid)."""
    m = tail_mask(idle)
    lay = np.zeros(idle.shape[:2] + (4,), np.uint8)
    lay[m] = (255, 150, 60, alpha)
    im = Image.fromarray(up(lay, PX))
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    out.paste(im, (round(origin[0] * PX), round(origin[1] * PX)))
    return out


def skeleton(can, s, label, idle, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    can.alpha_composite(tail_layer(idle, s["tail_origin"], 110 if alpha == 255 else 70))
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    b = s["wand"]
    dr.line([c(wand_point(b, 0)), c(wand_point(b, TIP0))], fill=COL["shaft"] + (alpha,), width=6)
    dr.line([c(wand_point(b, TIP0)), c(wand_point(b, 1))], fill=COL["point"] + (alpha,), width=10)
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
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Aurora",
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
    """Every bone, wand point and head box on the canvas; the holding wrist on the grip; no hand or wand over the
    face; a held wand's point not below the ground."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    b = s["wand"]
    bpts = [wand_point(b, f / 20) for f in range(21)]
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
    fx0, fx1 = hx + FACE[0] - REST["head"][0], hx + FACE[1] - REST["head"][0]   # the face: glasses to mouth
    fy0, fy1 = hy + FACE[2] - REST["head"][1], hy + FACE[3] - REST["head"][1]
    over = [] if b.get("behind") else bpts   # a wand resting on her shoulder runs BEHIND the head, as in the design
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] + over if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/au_work/aurora_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(dict(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), far_arm="rest",
                                     near_arm="rest", near_leg="rest", far_leg="rest", wand=REST_WAND))))
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

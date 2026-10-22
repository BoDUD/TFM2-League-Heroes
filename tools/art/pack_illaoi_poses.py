#!/usr/bin/env python3
"""Illaoi's pose pack for Codex (assets/source/illaoi/POSE_PROMPTS.md): the whole-body poses her League clips go through,
and the tentacle's front-view poses (the user, 2026-10-23: 「动作帧让 Codex 照骨架画姿势（像艾翁、彗那样）」,
pack_ivern_poses.py's way).

    python tools/art/pack_illaoi_poses.py [--out C:/t/il_work/illaoi_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-2, 52 x
68) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames (tools/lol/pose_ref.py
at the 3/4 camera): every bone at the design's OWN length (measured on hd/idle.png at 14x: REST), only its direction set
per pose (POSES), the lowest foot on the ground unless the pose lifts it. The prompt gives the legs' and arms' lengths
in squares and asks Codex to count them (Qiyana's adult-long legs, 2026-10-22).
HER IDOL is a big prop (a gold disc IDOL_R squares round, its fan of ridges on its right side): it stays in the FAR hand
(the image left in the design, resting on her shoulder) and both hands hold it where the pose says; each pose places its
centre (`idol`: squares from the far wrist), drawn on the skeleton as a translucent gold disc.
THE TENTACLE (her passive, W, R) is drawn from the front (an effect picture, never mirrored) on its own design
hd/tentacle.png (33 x 66, PPU 1.5) at the same PX: no skeleton (one bending body), League's front frame and a line of text
for each (TENTACLE).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head with its bun, 8x: every pose wears it); 2_design.png (the design on the grid); per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local); T0_tentacle.png
(its design on the grid) and per tentacle pose T<k>_<name>_league.png (its front frame).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image right in the design, the fist on her hip, the bracer), PURPLE = the FAR arm
(image left in the design, under the idol); grey box = the head (the design's head with its bun, never redrawn); gold
disc = the idol.
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
from design_illaoi_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "illaoi")
PX, CANVAS, SOLE_Y = 12, 1254, 1200
GREY = (225, 225, 225)
GROUND = 68                        # the design's soles' bottom edge (rows)
DX, DY = 28, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 100)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200)}
HEAD = (5, 25, 20, 44)             # rows / columns of the bun, the hair and the face in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 24 x 20 squares
FACE = (27, 41, 14, 23)            # the face (brows, eyes, nose ring, mouth): x0, x1, y0, y1 in design squares
IDOL_R = 10.5                      # the idol's disc, squares (hd/idle.png: cols 0-22, rows 0-30 with its fan)
IDOL_GOLD = (230, 180, 40)

# the design's own skeleton, measured on hd/idle.png (52 x 68, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (the far hand up under the idol, the near
# fist on her hip); each leg hip, knee, ankle, toes (her boots point out to the sides)
REST = {
    "head": (32.0, 15.0),
    "spine": [(29.0, 45.0), (29.0, 25.0)],
    "far_arm": [(22.5, 28.0), (16.5, 32.0), (18.5, 26.0), (18.5, 23.0)],
    "near_arm": [(39.5, 27.5), (46.5, 33.0), (45.0, 40.0), (43.5, 43.0)],
    "near_leg": [(24.0, 46.0), (20.5, 53.0), (17.5, 61.0), (11.5, 67.0)],
    "far_leg": [(34.0, 46.0), (38.5, 53.0), (41.5, 61.0), (48.5, 67.0)],
    "idol": (-7.5, -11.0),          # the idol's centre from the far wrist
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest" (the design's own,
# turned with the spine), three angles, or (target, side, last angle): the wrist / ankle at the target with the elbow /
# knee solved at the design's lengths (side -1 bends a downward limb's middle joint to the image right, +1 to the image
# left), then the hand / foot at the last angle. "idol": its centre from the far wrist (squares).
POSES = {
    "a_raise": ("illaoi_attack2@267",
                "抡起神像：身子往左后方仰，远侧手臂把神像高高抡到头顶后上方（神像在头的左上方，不挡脸），近侧手臂往前伸着保持平衡，前腿（远侧）往前迈一步（普攻起手）",
                "WIND-UP - leaning back toward the image left, the FAR arm swinging the big gold idol up high behind and "
                "above her head (the idol over the image left, never over the face), the near arm reaching forward for "
                "balance, the front (far) leg stepping forward.",
                dict(pelvis=(29.0, 46.0), lift=None, shift=2, spine=-172, far_arm=(-150, -165, 180), idol=(-3.0, -9.0),
                     near_arm=(70, 85, 95), near_leg=((20.0, 62.0), 1, -50), far_leg=((42.0, 64.0), -1, 60))),
    "a_slam": ("illaoi_attack1@500",
               "砸下神像：身子往前压，两腿大大分开蹲下，两只手一起把神像砸在身前（画面右边）的地上，神像底边贴着地面线（普攻 / 灵魂试炼砸下）",
               "SMASH - pressing forward and down, the legs wide apart in a deep squat, BOTH hands smashing the idol "
               "into the ground in front of her (on the image right), the idol's lower edge on the ground line.",
               dict(pelvis=(27.0, 57.0), lift=None, shift=-6, spine=145, idol_at=(43.0, 57.5), far_arm=("grip", None, 1, None),
                    near_arm=("grip", 170, -1, None), near_leg=((16.0, 62.0), 1, -50), far_leg=((38.0, 62.0), -1, 50))),
    "w_jump": ("illaoi_spell2@125",
               "跃起：往前上方跳起（脚离地约 12 格），两膝收起，身子前倾，两只手一起抱着神像举在胸前右边（准备砸下，神像不挡脸）（严酷训诫跳起）",
               "LEAP - jumping up and forward (the feet about 12 squares off the ground), both knees tucked, leaning "
               "forward, BOTH hands holding the idol up in front of her chest on the image right, ready to smash (never "
               "over the face).",
               dict(pelvis=(28.0, 44.0), lift=12, shift=-2, spine=170, idol_at=(47.0, 24.0), far_arm=("grip", None, 1, None),
                    near_arm=("grip", None, -1, None), near_leg=((22.0, 56.0), 1, -30), far_leg=((37.0, 58.0), -1, 40))),
    "w_land": ("illaoi_spell2@375",
               "落地压住：深深蹲下，身子往前趴，两只手臂往前伸直，把神像按在身前（画面右边）的地上（严酷训诫落地）",
               "LAND - crouching very low, the body bent far forward, both arms stretched straight forward pressing the "
               "idol down on the ground in front of her (on the image right).",
               dict(pelvis=(27.0, 58.0), lift=None, shift=-8, spine=140, idol_at=(45.0, 57.5), far_arm=("grip", None, 1, None),
                    near_arm=("grip", None, -1, None), near_leg=((15.0, 63.0), 1, -40), far_leg=((37.0, 62.0), -1, 50))),
    "e_thrust": ("illaoi_spell3_a@600",
                 "推出神像：弓步往前，两只手臂往前（画面右边）伸直，把神像举在胸前的高度推出去，神像正面的绿色螺旋眼朝着敌人；后腿（近侧）伸直，前腿（远侧）屈膝（灵魂试炼：扯出灵魂）",
                 "THRUST - a lunge forward, BOTH arms stretched straight out to the image right holding the idol out at "
                 "chest height, its green spiral eye facing the enemy; the back (near) leg straight, the front (far) knee "
                 "bent.",
                 dict(pelvis=(27.0, 48.0), lift=None, shift=-8, spine=165, idol_at=(47.0, 38.0), far_arm=("grip", None, 1, None),
                      near_arm=("grip", None, -1, None), near_leg=((12.0, 64.0), 1, -60), far_leg=((43.0, 64.0), -1, 60))),
    "e_yank": ("illaoi_spell3_b_medium@225",
               "往回拽：身子往左后方仰，两只手把神像往胸前拽回来（手肘弯着，神像在胸口右前方），近侧腿往前撑住，像在把什么东西从敌人身上扯出来（灵魂试炼：拽出灵魂）",
               "YANK - leaning back toward the image left, both hands pulling the idol back toward her chest (elbows "
               "bent, the idol just in front of her chest on the image right), the near leg braced forward, as if "
               "tearing something out of the enemy.",
               dict(pelvis=(30.0, 47.0), lift=None, shift=-2, spine=-172, idol_at=(44.0, 38.0), far_arm=("grip", None, 1, None),
                    near_arm=("grip", None, -1, None), near_leg=((39.0, 64.0), -1, 60), far_leg=((19.0, 62.0), 1, -50))),
    "r_crouch": ("illaoi_attack2@800",
                 "蹲下蓄力：深深蹲下，两膝往外分开，身子往前弓，托神像的手把神像放低在身子左边（画面左边）靠近地面，另一只手臂垂在膝盖边，抬眼往前看（过界信仰起手）",
                 "CROUCH - squatting deep, the knees spread apart, hunched forward, the IDOL hand holding the idol low "
                 "at her side on the image left near the ground, the other arm hanging by her knee, looking ahead.",
                 dict(pelvis=(30.0, 55.0), lift=None, shift=6, spine=170, idol_at=(20.0, 55.0), far_arm=("grip", None, 1, None),
                      near_arm=(20, 10, 0), near_leg=((17.0, 62.0), 1, -50), far_leg=((43.0, 62.0), -1, 50))),
    "r_leap": ("illaoi_spell4@480",
               "高高跃起：往上跳得很高（脚离地约 16 格），两腿屈膝收在身下，身子微微后仰，托神像的手把神像高高举在头的左边（画面左边，不挡脸），另一只手臂往右上方扬起（过界信仰跳起）",
               "HIGH LEAP - jumping very high (the feet about 16 squares off the ground), both knees tucked under her, "
               "the body leaning back a little, the IDOL hand raising the idol high beside her head on the image left "
               "(never over the face), the other arm flung up to the upper right.",
               dict(pelvis=(30.0, 44.0), lift=16, shift=4, spine=-175, idol_at=(11.0, 14.0), far_arm=("grip", None, 1, None),
                    near_arm=(150, 160, 170), near_leg=((23.0, 56.0), 1, -40), far_leg=((37.0, 58.0), -1, 40))),
    "r_slam": ("illaoi_spell4@560",
               "跪地砸下：近侧膝盖跪在地上，远侧腿屈膝撑地，身子往前扑，两只手把神像狠狠砸进身前（画面右边）的地里（过界信仰落地）",
               "KNEELING SLAM - the near knee down on the ground, the far leg bent with its foot planted, the body "
               "lunging forward, BOTH hands slamming the idol hard into the ground in front of her (on the image right).",
               dict(pelvis=(27.0, 59.0), lift=None, shift=-8, spine=140, idol_at=(46.0, 57.5), far_arm=("grip", None, 1, None),
                    near_arm=("grip", None, -1, None), near_leg=((20.0, 66.0), 1, -90), far_leg=((38.0, 64.0), -1, 60))),
    "run1": ("illaoi_run1@0",
             "跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子微微前倾，远侧手拎着神像垂在身子左后方（画面左边、腰的高度），近侧手臂往后摆",
             "RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back "
             "behind, leaning forward a little, the far hand carrying the idol low at her side behind her (image left, "
             "at hip height), the near arm swinging back.",
             dict(pelvis=(29.0, 47.0), lift=None, shift=0, spine=172, far_arm=(-20, -10, 0), idol=(-6.0, 6.0),
                  near_arm=(-30, -20, -10), near_leg=((16.0, 66.0), 1, -70), far_leg=((42.0, 67.0), -1, 60))),
    "run2": ("illaoi_run1@250",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，神像还拎在身侧，近侧手臂垂在身边",
             "RUN 2 - the near leg under the body carrying her, the FAR knee lifted forward, the body one square higher, "
             "the idol still carried low at her side, the near arm hanging close.",
             dict(pelvis=(29.0, 45.0), lift=1, shift=0, spine=174, far_arm=(-10, 0, 0), idol=(-6.0, 6.0),
                  near_arm=(10, 0, 0), near_leg=((27.0, 67.0), 1, -40), far_leg=((38.0, 58.0), -1, 70))),
    "run3": ("illaoi_run1@500",
             "跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：身子微微前倾，神像拎在身侧，近侧手臂往前摆",
             "RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back "
             "behind, leaning forward a little, the idol carried low at her side, the near arm swinging forward.",
             dict(pelvis=(29.0, 47.0), lift=None, shift=0, spine=172, far_arm=(-10, 0, 0), idol=(-6.0, 6.0),
                  near_arm=(40, 60, 70), near_leg=((40.0, 67.0), -1, 60), far_leg=((18.0, 65.0), 1, -70))),
    "run4": ("illaoi_run1@750",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，神像拎在身侧",
             "RUN 4 - the far leg under the body carrying her, the NEAR knee lifted forward, the body one square higher, "
             "the idol carried low at her side.",
             dict(pelvis=(29.0, 45.0), lift=1, shift=0, spine=174, far_arm=(-20, -10, 0), idol=(-6.0, 6.0),
                  near_arm=(0, 10, 20), near_leg=((36.0, 58.0), -1, 70), far_leg=((32.0, 67.0), -1, 60))),
    "d_stagger": ("illaoi_death@325",
                  "踉跄：被打得往左后方倒，膝盖发软，两只手臂往两边甩开，神像从手里脱出去，飞在她左上方（画面左边，不挡脸）（死亡第一下）",
                  "STAGGER - knocked back toward the image left, the knees giving way, both arms flung out, the idol "
                  "flying out of her hands up to the upper left (the image left, never over the face).",
                  dict(pelvis=(30.0, 49.0), lift=None, shift=4, spine=-158, far_arm=(-120, -140, -150), idol=(-9.0, -6.0),
                       near_arm=(110, 120, 130), near_leg=((22.0, 67.0), 1, -50), far_leg=((38.0, 67.0), -1, 60))),
    # League's death ends lying flat; the head is pasted upright in every pose, so ours slumps sitting instead
    "d_slump": ("illaoi_death@975",
                "瘫坐：一屁股坐在地上，两条腿往画面右边平伸在地上，身子往前趴下去，头低下来，两只手臂软软垂到地上；神像倒在她身后（画面左边）的地上（死亡）",
                "SLUMPED - sitting down hard on the ground, both legs stretched out flat to the image right along the "
                "ground, the body slumped forward, the head low, both arms hanging limp to the ground; the idol lying on "
                "the ground behind her on the image left.",
                dict(pelvis=(27.0, 64.0), lift=None, shift=4, spine=150, idol_at=(8.0, 57.5), far_arm=(-40, -20, 0),
                     near_arm=(70, 60, 70), near_leg=(95, 90, 95), far_leg=(85, 92, 95))),
}

# the tentacle's poses, front view: name -> (League's frame, Chinese, English)
TENTACLE = {
    "tn_rise": ("illaoiminion_spawn@513",
                "钻出地面：只露出下面一小截（约 25 格高），直直地往上顶，尖端还没卷，根部的石块往两边炸开（触手出现第一下）",
                "RISING - only its lower part out of the ground (about 25 squares tall), pushing straight up, the tip "
                "not curled yet, the root stones bursting out to both sides."),
    "tn_grow": ("illaoiminion_spawn@1283",
                "长高：长到约 50 格高，身子微微往一边弯，尖端开始卷（触手出现第二下）",
                "GROWING - about 50 squares tall, its body bending a little to one side, the tip starting to curl."),
    "tn_sway": ("illaoiminion_idleangry@3000",
                "待机摇摆：和定稿一样高，但整条往另一边（画面右边）弯，卷钩朝画面右边卷（待机第二帧，和定稿来回摆）",
                "SWAY - as tall as the design but the whole body bent the other way (to the image right), the hook "
                "curling to the image right (the idle's second frame, swinging with the design)."),
    "tn_rear": ("illaoiminion_attack1@533",
                "高高扬起：伸得又高又直（约 80 格高，比定稿高一截，粗细不变），尖端只微微弯，准备往下砸（触手抽打起手）",
                "REARING - stretched up very tall and straight (about 80 squares, taller than the design, the same "
                "thickness), the tip only a little bent, about to strike down."),
    "tn_slam": ("illaoiminion_attack1@1067",
                "朝前砸下：整条触手朝着看画的人砸下来——从正面看变成很矮很粗的一团（约 22 格高、比定稿宽一倍），尖端拍扁在身前的地上，根部石块被震起来（触手抽打：砸中）",
                "SLAMMED DOWN - the whole tentacle smashed down toward the viewer: seen from the front it is a short, "
                "thick mass (about 22 squares tall, twice the design's width), its tip flattened on the ground in front, "
                "the root stones jolted up."),
    "tn_recoil": ("illaoiminion_attack1@1600",
                  "弹回：从地上弹起来一半（约 40 格高），身子歪着，尖端卷起来（触手抽打收回）",
                  "RECOIL - springing halfway back up (about 40 squares tall), the body leaning, the tip curling up again."),
    "tn_sink": ("illaoiminion_death@1000",
                "缩回地里：往下沉，只剩约 18 格露在地面上，尖端缩成一团，根部石块往里塌（触手消失）",
                "SINKING - sinking back into the ground, only about 18 squares left above it, the tip curled tight, "
                "the root stones caving in."),
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
    """build_raw with `idol_at` read on the finished skeleton (after the drop onto the ground): the legs and the spine
    alone set the drop, so a first pass finds it and the second places the idol (and the hands on it) there."""
    if "idol_at" not in spec:
        return build_raw(spec)
    first = build_raw(spec)
    dy = first["spine"][0][1] - spec["pelvis"][1]
    ix, iy = spec["idol_at"]
    return build_raw(dict(spec, idol_at=(ix, iy - dy)))


def build_raw(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned); the idol from the far wrist. The lowest foot or knee on the ground, or `lift` rows over it."""
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
        if sp[0] == "grip":         # the hand on the idol's rim at that angle (from the idol's centre)
            _, at, side, last = sp
            if at is None:            # the rim point nearest the shoulder
                at = ang(spec["idol_at"], pts[0])
            target = along(spec["idol_at"], at, IDOL_R)
            if last is None:          # the fingers over the rim, toward the idol's middle
                last = at + 180.0
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
            sk.setdefault("reach", {})[name] = math.hypot(A[0] - target[0], A[1] - target[1])
        elif len(sp) == 3 and isinstance(sp[0], tuple):
            target, side, last = sp
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    if "idol_at" in spec:
        sk["idol"] = spec["idol_at"]
    else:
        io = spec.get("idol", REST["idol"])
        w = sk["far_arm"][2]
        sk["idol"] = (w[0] + io[0], w[1] + io[1])
    reach = sk.pop("reach", {})
    low = max(y for leg in ("near_leg", "far_leg", "spine") for _, y in sk[leg])
    dy = GROUND - (spec["lift"] or 0) - low
    out = {k: ((v[0], v[1] + dy) if k in ("head", "idol") else [(x, y + dy) for x, y in v]) for k, v in sk.items()}
    out["reach"] = reach
    return out


def to_canvas(sk, shift=0):
    return {k: (v if k == "reach" else (v[0] + DX + shift, v[1] + DY) if k in ("head", "idol")
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
    """A point in design square edges, already on the canvas grid, in canvas px."""
    return (p[0] * PX, p[1] * PX)


def skeleton(can, s, label, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it);
    a bigger dot on each hand; the idol a translucent gold disc behind the limbs."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    ix, iy = s["idol"]
    dr.ellipse([(ix - IDOL_R) * PX, (iy - IDOL_R) * PX, (ix + IDOL_R) * PX, (iy + IDOL_R) * PX],
               fill=IDOL_GOLD + (90,), outline=(170, 120, 0, alpha), width=4)
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("far_leg", "far_arm", "spine", "near_leg", "near_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == 2 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work, champ="Illaoi", yaw=35):
    """League's frame (Illaoi at the 3/4 camera, the tentacle from the front). Never --hide-submeshes: it hides her."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Illaoi", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", "900", "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", str(yaw), "--name", "f",
           "--out", work, "--frame", frame]
    if champ == "Illaoi":
        cmd.append("--mirror")
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
    """Every bone, the head box and the idol on the canvas; no hand and no idol over the face."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    ix, iy = s["idol"]
    if iy - IDOL_R < 1 or ix - IDOL_R < 1 or ix + IDOL_R > CANVAS / PX - 1 or iy + IDOL_R > SOLE_Y / PX + 0.6:
        out.append(f"idol off the canvas / below the ground ({ix:.0f}, {iy:.0f})")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]   # the design's (0, 0) as the head box has it
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"hand over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    for arm, gap in s.get("reach", {}).items():
        if gap > 1.0:
            out.append(f"{arm} {gap:.1f} squares short of the idol's rim")
    nx, ny = min(max(ix, fx0), fx1), min(max(iy, fy0), fy1)
    if math.hypot(ix - nx, iy - ny) < IDOL_R - 0.5:
        out.append(f"idol over the face (centre {ix:.0f}, {iy:.0f})")
    return out


def tile_sheet(tiles, path, cols=3):
    W = max(t.width for t in tiles)
    H = max(t.height for t in tiles)
    rows_ = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows_), (255, 255, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * W, (k // cols) * H))
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/il_work/illaoi_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    tent = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "tentacle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), far_arm="rest",
                                near_arm="rest", near_leg="rest", far_leg="rest")))
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
            hx, hy = s["head"]                       # the design's head in its box, to judge the chibi proportions
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
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    tz = canvas_grid()
    tz.alpha_composite(on_grid(tent, (CANVAS // PX - tent.shape[1]) // 2, SOLE_Y // PX - tent.shape[0]))
    tz.convert("RGB").save(os.path.join(out, "T0_tentacle.png"))
    for k, (name, (frame, zh, en)) in enumerate(TENTACLE.items(), 1):
        lol_frame(a.lol, frame, out + "_work", "IllaoiMinion", 0).save(os.path.join(out, f"T{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

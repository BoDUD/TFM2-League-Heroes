#!/usr/bin/env python3
"""Neeko's pose pack for Codex (assets/source/neeko/POSE_PROMPTS.md): the whole-body poses her League clips go through
that the 3/4 design cannot give by moving its own parts - the fighting stance and the lunge of her attack, the kick and
the pounce of her third attack, Blooming Burst's somersault (one tucked ball, turned by quarter turns in the frames) and
throw, Tangle-Barbs' spin with the tail round her and its fling, Pop Blossom's crouched charge, its leap and landing,
the run, the twirl and the fall of her death (the user, 2026-10-21, shown League's clips: 「Codex 画关键姿势」; Shyvana's
skeleton way).

    python tools/art/pack_neeko_poses.py [--out C:/t/nk_work/neeko_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at 10 px a square, soles on y 1180 - the design hd/idle.png (Codex's step-1 A-1, 49 x
100) sits at squares (DX, DY) on it. The skeletons are set by hand after League's frames (tools/lol/pose_ref.py at the
3/4 camera): every bone at the design's OWN length (measured on hd/idle.png: REST; the far arm, foreshortened in the
design, takes the near arm's lengths), only its direction set per pose (POSES), the lowest foot on the ground unless the
pose lifts it.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head with its quills and hair, 8x: every pose wears it); 2_design.png (the design on the grid);
per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left) to its violet fingers, PURPLE = the FAR arm (image right), YELLOW = the
tail (from its root behind the hips to its violet tip); grey box = the head (the design's head, never redrawn).
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
from design_neeko_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "neeko")
PX, CANVAS, SOLE_Y = 10, 1254, 1180
GREY = (225, 225, 225)
GROUND = 100                       # the design's soles' bottom edge (rows)
DX, DY = 38, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 118)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "tail": (240, 210, 0)}
HEAD = (0, 41, 4, 49)              # rows / columns of the head with its quills and hair in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 45 x 41 squares

# the design's own skeleton, measured on hd/idle.png (49 x 100, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (both hands held together before her chest);
# each leg hip, knee, ankle, toes; the tail from its root behind the near hip round its curl to its violet tip
REST = {
    "head": (26.5, 20.5),
    "spine": [(28.0, 64.0), (29.5, 44.0)],
    "near_arm": [(23.5, 46.0), (19.5, 56.5), (30.0, 53.0), (33.0, 52.0)],
    "far_arm": [(35.5, 47.0), (38.0, 57.5), (34.0, 53.5), (31.5, 52.5)],
    "near_leg": [(24.5, 66.0), (22.5, 80.0), (23.5, 92.5), (28.5, 98.5)],
    "far_leg": [(32.0, 66.0), (33.0, 80.0), (33.5, 92.0), (37.0, 97.5)],
    "tail": [(20.0, 73.0), (15.0, 82.0), (9.0, 86.0), (4.0, 82.0), (3.0, 75.0), (6.0, 68.0), (10.0, 64.0)],
}
# the far arm is foreshortened in the design (its forearm points at the viewer): the poses give it the near arm's bones
SAME_AS = {"far_arm": "near_arm"}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), the spine's direction and every
# limb (degrees: 0 straight down, 90 to the image right, 180 up, -90 to the image left) - each bone at the design's own
# length (REST). A limb is "rest" (the design's own, turned with the spine), three angles, or (target, side, last
# angle): the wrist / ankle at the target with the elbow / knee solved at the design's lengths (side -1 bends a
# downward limb's middle joint to the image right, +1 to the image left), then the hand / foot at the last angle.
POSES = {
    "stance": ("Neeko_Attack1@0", "低身架势：两腿大开压低，前倾，近侧手臂朝前伸、手掌张开，远侧手臂弯在身前，尾巴贴地伸在身后、尾尖卷起（普攻、Q 的起手）",
               "STANCE - a wide low fighting stance, both knees bent, the body leaning forward, the NEAR arm reaching "
               "forward with the hand open, the far arm bent before her, the tail stretched low behind her along the "
               "ground with its tip curling up.",
               dict(pelvis=(26.0, 72.0), lift=None, spine=150, near_arm=((44.0, 54.0), 1, 95), far_arm=((40.0, 60.0), 1, 100),
                    near_leg=((12.0, 92.0), -1, 50), far_leg=((41.0, 92.0), -1, 55),
                    tail=(-55, -80, -92, -100, -150, 170))),
    "thrust": ("Neeko_Attack1@338", "扑出出手：离地往前扑（脚离地约 6 格），身子大幅前倾，近侧手臂朝前伸直（和肩一样高，手掌张开对着前方），远侧手臂往身后甩开，近侧腿屈膝在前、远侧腿往后收，尾巴在身后低低地卷着（普攻出手）",
               "THRUST - springing forward off the ground (the feet about 6 squares up), the body leaning far forward, "
               "the NEAR arm thrust straight forward at shoulder height with the palm open toward the target, the far "
               "arm flung back behind her, the near knee bent forward, the far leg folded back, the tail low behind her "
               "curling at its end.",
               dict(pelvis=(26.0, 66.0), lift=6, spine=125, near_arm=((52.0, 52.0), 1, 90), far_arm=((6.0, 50.0), 1, -100),
                    near_leg=((32.0, 86.0), -1, 35), far_leg=((12.0, 84.0), -1, -40),
                    tail=(-70, -88, -95, -110, -150, 170))),
    "kick": ("Neeko_Passive_attack@250", "旋身踢腿：远侧腿踮脚站直，近侧腿往后高高抬起（屈膝，脚到腰的高度），身子挺直微微后仰，两只手臂往两边平伸保持平衡，尾巴从身后往上甩成一道大弧（第三下强化普攻）",
             "KICK - standing tall on the tiptoe of the FAR leg, the NEAR leg kicked up high behind her (the knee bent, "
             "the foot at waist height), the body upright and leaning back a little, both arms stretched out level to "
             "both sides for balance, the tail swung up behind her in a big arc.",
             dict(pelvis=(28.0, 62.0), lift=None, spine=-176, near_arm=((2.0, 52.0), 1, -95), far_arm=((55.0, 52.0), -1, 95),
                  near_leg=((7.0, 66.0), -1, -120), far_leg=((31.0, 89.0), -1, 10),
                  tail=(-80, -115, -150, -175, 165, 140))),
    "pounce": ("Neeko_Passive_attack@375", "低身扑击：身子压得很低往前扑（几乎和地面平行），头在右前方，两只手往前伸到地面，前面的腿（远侧）屈膝，后面的腿（近侧）往后蹬直，尾巴在身后竖起来（第三下强化普攻打中）",
               "POUNCE - lunging forward very low, the body almost level with the ground, the head at the front (image "
               "right), both hands reaching forward to the ground, the front (far) leg bent, the back (near) leg pushed "
               "straight out behind, the tail standing up high behind her.",
               dict(pelvis=(20.0, 76.0), lift=None, spine=105, near_arm=((52.0, 92.0), 1, 100), far_arm=((56.0, 89.0), 1, 100),
                    near_leg=((0.0, 93.0), -1, -40), far_leg=((36.0, 93.0), -1, 55),
                    tail=(-150, -172, 180, 176, 170, 160))),
    "tuck": ("Neeko_Spell3_0@100", "空中抱团：在空中蜷成一团（脚离地约 12 格），两膝收到胸前，两只手抱住小腿，头往前低，尾巴绕着身子卷一圈（Q 的空翻：我会把这一张整张转 90°、180°、270° 做成翻跟头；英雄联盟的参考图是 E 起手时在空中蹲着的那一帧，这一张要蜷得更紧、手抱小腿）",
             "TUCK - curled up into a ball in mid-air (the feet about 12 squares up), both knees pulled up to the "
             "chest, both hands holding the shins, the head bent forward, the tail wrapped once round her body.",
             dict(pelvis=(28.0, 70.0), lift=12, spine=160, near_arm=((36.0, 66.0), 1, 60), far_arm=((40.0, 64.0), 1, 60),
                  near_leg=((34.0, 72.0), -1, 70), far_leg=((38.0, 71.0), -1, 70),
                  tail=(40, 85, 120, 175, -140, -95))),
    "throw_air": ("Neeko_Spell1@496", "空中掷出：在空中挺直（脚离地约 14 格），两只手臂往上甩开：近侧手臂往左上方、远侧手臂往右上方（手掌张开，种子从这只手飞出），都不挡脸，近侧腿屈膝抬起、远侧腿垂着，尾巴在身下卷着（Q 扔出种子）",
                  "THROW IN THE AIR - upright in mid-air (the feet about 14 squares up), both arms flung up and out: "
                  "the NEAR arm up to the upper left, the FAR arm up to the upper right with the palm open (the seed "
                  "leaves it), neither over the face, the near knee lifted, the far leg hanging, the tail curled below "
                  "her.",
                  dict(pelvis=(28.0, 64.0), lift=14, spine=176, near_arm=((6.0, 36.0), 1, -150), far_arm=((52.0, 34.0), -1, 150),
                       near_leg=((32.0, 84.0), -1, 25), far_leg=((33.0, 92.0), -1, 15),
                       tail=(-30, -60, -100, -150, 165, 120))),
    "coil": ("Neeko_Spell3_0@100", "旋身绕尾：在空中蹲着旋转（脚离地约 8 格），尾巴在腰上绕成一个大圈，近侧手臂往左边伸开，远侧手臂往右前方伸，两腿收起（E 的起手）",
             "COIL - spinning crouched in mid-air (the feet about 8 squares up), the tail looped round her waist in a "
             "big ring, the NEAR arm stretched out to the image left, the far arm reaching to the front right, both "
             "legs tucked.",
             dict(pelvis=(28.0, 66.0), lift=8, spine=172, near_arm=((5.0, 50.0), 1, -100), far_arm=((53.0, 52.0), 1, 95),
                  near_leg=((24.0, 84.0), -1, 25), far_leg=((35.0, 84.0), -1, 25),
                  tail=(55, 90, 105, 160, -150, -105))),
    "fling": ("Neeko_Spell3_0@400", "甩出倒刺：站定，近侧手臂往身后左边平平甩开，远侧手臂朝前伸（手掌张开），尾巴从身后往前猛甩、在她身前（画面右边）伸得又平又长（E 甩出倒刺）",
              "FLING - standing firm, the NEAR arm flung back level to the image left, the far arm reaching forward "
              "with the palm open, the tail whipped round from behind her and stretched out long and level in front of "
              "her to the image right.",
              dict(pelvis=(28.0, 64.0), lift=None, spine=172, near_arm=((2.0, 46.0), 1, -95), far_arm=((48.0, 52.0), 1, 90),
                   near_leg=((24.0, 92.0), -1, 40), far_leg=((38.0, 92.0), -1, 45),
                   tail=(70, 86, 90, 90, 92, 95))),
    "hunch": ("Neeko_channel_wndup@633", "蓄力下蹲：蹲得很低往前探（弓步），头低在前面，两只手垂在两膝之间，后面的腿（近侧）往后伸，前面的腿（远侧）屈膝，尾巴在身后卷成一个大螺旋竖起来（R 蓄力）",
              "HUNCH - crouched very low and leaning forward in a lunge, the head low at the front, both hands hanging "
              "between the knees, the back (near) leg stretched behind, the front (far) leg bent, the tail rolled up "
              "behind her into a big upright spiral.",
              dict(pelvis=(22.0, 78.0), lift=None, spine=125, near_arm=((34.0, 88.0), 1, 30), far_arm=((40.0, 87.0), 1, 30),
                   near_leg=((4.0, 93.0), -1, -40), far_leg=((38.0, 93.0), -1, 60),
                   tail=(-140, -170, 165, 120, 60, 10))),
    "soar": ("Neeko_Spell4@0", "腾空跃起：整个人笔直地跳起来（脚离地约 20 格），身子挺直、头仰起，两只手臂垂在身侧，近侧腿伸直往下、远侧腿屈膝，尾巴在身后往上卷（R 跳起）",
             "SOAR - leaping straight up into the air (the feet about 20 squares up), the body stretched tall, the "
             "head up, both arms down at her sides, the near leg straight down, the far knee bent, the tail curling up "
             "behind her.",
             dict(pelvis=(28.0, 62.0), lift=20, spine=178, near_arm=((18.0, 66.0), 1, 0), far_arm=((40.0, 66.0), -1, 0),
                  near_leg=((24.0, 92.0), -1, 10), far_leg=((36.0, 86.0), -1, 30),
                  tail=(-150, 180, 150, 110, 60, 20))),
    "land": ("Neeko_Spell4@788", "落地半蹲：屈膝落地、身子前倾，近侧手撑在身前右边的地上，远侧手臂往后扬，尾巴在身后高高竖起（R 落地）",
             "LAND - landed in a crouch, the knees bent, the body leaning forward, the NEAR hand pressed on the ground "
             "in front of her (image right), the far arm swept back, the tail raised high up behind her.",
             dict(pelvis=(24.0, 74.0), lift=None, spine=130, near_arm=((48.0, 96.0), 1, 90), far_arm=((18.0, 60.0), -1, -60),
                  near_leg=((10.0, 93.0), -1, -10), far_leg=((34.0, 93.0), -1, 60),
                  tail=(-160, 180, 175, 170, 175, 180))),
    "run1": ("Neeko_Run@0", "跑步 1（远侧腿在前着地，近侧腿往后抬起）：身子前倾一点，两只手收在胸前，尾巴在身后卷成螺旋",
             "RUN 1 - bounding along: the FAR leg forward with its foot landing, the NEAR leg kicked up behind her, "
             "the body leaning forward a little, both hands held before her chest, the tail curled into a spiral "
             "behind her.",
             dict(pelvis=(28.0, 64.0), lift=None, spine=168, near_arm="rest", far_arm="rest",
                  near_leg=((10.0, 84.0), -1, -60), far_leg=((40.0, 92.0), -1, 45),
                  tail=(-45, -60, -100, -150, 170, 120))),
    "run2": ("Neeko_Run@225", "跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格",
             "RUN 2 - bounding along: the near leg under the body carrying her, the FAR knee lifted forward, the body "
             "one square higher, both hands before her chest, the tail curled into a spiral behind her.",
             dict(pelvis=(28.0, 63.0), lift=1, spine=170, near_arm="rest", far_arm="rest",
                  near_leg=((26.0, 92.0), -1, 30), far_leg=((38.0, 80.0), -1, 60),
                  tail=(-45, -60, -100, -150, 170, 120))),
    "run3": ("Neeko_Run@450", "跑步 3（近侧腿在前着地，远侧腿往后抬起）",
             "RUN 3 - bounding along: the NEAR leg forward with its foot landing, the FAR leg kicked up behind her, "
             "the body leaning forward a little, both hands before her chest, the tail curled into a spiral behind her.",
             dict(pelvis=(28.0, 64.0), lift=None, spine=168, near_arm="rest", far_arm="rest",
                  near_leg=((40.0, 92.0), -1, 45), far_leg=((14.0, 82.0), -1, -60),
                  tail=(-45, -60, -100, -150, 170, 120))),
    "run4": ("Neeko_Run@675", "跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格",
             "RUN 4 - bounding along: the far leg under the body carrying her, the NEAR knee lifted forward, the body "
             "one square higher, both hands before her chest, the tail curled into a spiral behind her.",
             dict(pelvis=(28.0, 63.0), lift=1, spine=170, near_arm="rest", far_arm="rest",
                  near_leg=((36.0, 80.0), -1, 60), far_leg=((30.0, 92.0), -1, 30),
                  tail=(-45, -60, -100, -150, 170, 120))),
    "twirl": ("Neeko_Death@250", "旋转踉跄：远侧腿踮脚站着，近侧腿屈膝抬起（脚贴在远侧膝盖旁），两只手臂往两边平伸，尾巴往右前方低低地甩出去（死亡第一下）",
              "TWIRL - spinning on the tiptoe of the FAR leg, the NEAR knee lifted with its foot by the far knee, both "
              "arms stretched out level to both sides, the tail swung out low to the front right.",
              dict(pelvis=(28.0, 64.0), lift=None, spine=178, near_arm=((2.0, 48.0), 1, -90), far_arm=((56.0, 48.0), -1, 90),
                   near_leg=((32.0, 79.0), -1, 70), far_leg=((31.0, 92.0), -1, 10),
                   tail=(60, 90, 100, 120, 160, -160))),
    "sit": ("Neeko_Death@1500", "跪坐倒地：坐到地上，近侧腿跪着折在身下，远侧腿立起膝盖，近侧手撑在身边的地上，远侧手搭在膝盖上，身子微微往后靠，尾巴在身前的地上卷着（死亡）",
            "SIT - sunk down sitting on the ground, the near leg folded under her with its knee on the ground, the far "
            "knee raised, the near hand propped on the ground beside her, the far hand resting on the raised knee, the "
            "body leaning back a little, the tail curled on the ground in front of her.",
            dict(pelvis=(28.0, 86.0), lift=None, spine=-176, near_arm=((14.0, 96.0), 1, 0), far_arm=((44.0, 80.0), -1, 60),
                 near_leg=((22.0, 98.0), 1, -90), far_leg=((42.0, 97.0), -1, 60),
                 tail=(60, 85, 90, 95, 120, 170))),
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
    pts = REST[SAME_AS.get(name, name)]
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
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips and the tail's root turned half as much; the head box upright over the
    neck (the head is pasted, never turned). The lowest foot or knee on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    for name, base, base_rest, k in (("near_arm", neck, rs[1], 1.0), ("far_arm", neck, rs[1], 1.0),
                                     ("near_leg", pel, rs[0], 0.5), ("far_leg", pel, rs[0], 0.5),
                                     ("tail", pel, rs[0], 0.5)):
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
    low = max(y for leg in ("near_leg", "far_leg") for _, y in sk[leg])
    dy = REST["near_leg"][-1][1] - (spec["lift"] or 0) - low
    return {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}


def to_canvas(sk):
    return {k: ((v[0] + DX, v[1] + DY) if k == "head" else [(x + DX, y + DY) for x, y in v]) for k, v in sk.items()}


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
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    order = [("tail", 7), ("far_leg", 7), ("far_arm", 7), ("spine", 7), ("near_leg", 7), ("near_arm", 7)]
    for name, w in order:
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=w, joint="curve")
        for p in pts:
            r = 6
            dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work):
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Neeko",
           "--hide-submeshes", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900",
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
    return {name: (to_canvas(build(spec)), frame, zh, en) for name, (frame, zh, en, spec) in POSES.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/nk_work/neeko_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(REST)
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
            r0, r1, c0, c1 = HEAD
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
        W = max(t.width for t in tiles)
        cols = 2
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
    skeleton(base, rest, "0: the approved design with its own skeleton (what each coloured line stands for)", 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
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

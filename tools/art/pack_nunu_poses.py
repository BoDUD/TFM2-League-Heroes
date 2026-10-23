#!/usr/bin/env python3
"""Nunu & Willump's pose pack for Codex (assets/source/nunu/POSE_PROMPTS.md): the whole-body poses their League clips go
through (the user, 2026-10-23: 「Codex 照骨架画姿势」, pack_illaoi_poses.py's way).

    python tools/art/pack_nunu_poses.py [--out C:/t/nu_work/nunu_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-2, 51 x
63) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames (tools/lol/pose_ref.py
at the 3/4 camera, with pack_nunu_picture.SKIN): every bone at the design's OWN length (measured on hd/idle.png at 14x:
REST), only its direction set per pose (POSES), the lowest foot on the ground unless the pose lifts it. The prompt gives
the legs' and arms' lengths in squares and asks Codex to count them.
The skeleton is WILLUMP's: his spine, his two long arms, his two short legs. THE HEAD BOX is the pasted top of the
figure - Willump's head with his antlers and Nunu riding on it - moved with the neck, never turned (Nunu's arms move by
the pose's text: he throws the snowballs). THE SNOWBALL (W) is a prop like Illaoi's idol: a white disc of `ball_r`
squares at `ball_at`, the hands on its rim (`grip`).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head box - Nunu, the antlers, Willump's face - 8x: every pose wears it); 2_design.png (the
design on the grid); per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right:
Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left in the design), PURPLE = the FAR arm (image right); grey box = the head
box; white disc = the snowball.
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
from design_nunu_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_nunu_picture import SKIN  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nunu")
PX, CANVAS, SOLE_Y = 12, 1254, 1200
GREY = (225, 225, 225)
GROUND = 63                        # the design's soles' bottom edge (rows)
DX, DY = 26, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 100)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200)}
HEAD = (0, 46, 5, 48)              # rows / columns of the head box in hd/idle.png: Nunu, the antlers, Willump's head
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # 43 x 46 squares
FACES = [(23, 33, 9, 17), (26, 44, 34, 46)]     # Nunu's face, Willump's face (eyes to grin): x0, x1, y0, y1
BALL = (235, 245, 255)

# the design's own skeleton, measured on hd/idle.png (51 x 63, square edges): the head box's middle; the spine pelvis ->
# the base of Willump's neck; each arm shoulder, elbow, wrist, the claws' tips; each leg hip, knee, ankle, toes
REST = {
    "head": (26.5, 23.0),
    "spine": [(29.0, 52.0), (29.0, 40.0)],
    "near_arm": [(18.0, 40.0), (13.0, 46.0), (13.0, 52.0), (15.0, 55.0)],
    "far_arm": [(41.0, 42.0), (46.0, 47.0), (47.0, 52.0), (48.0, 56.0)],
    "near_leg": [(24.0, 52.0), (20.0, 56.0), (16.0, 60.0), (11.0, 63.0)],
    "far_leg": [(35.0, 52.0), (37.0, 56.0), (37.0, 60.0), (41.0, 63.0)],
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest" (the design's own,
# turned with the spine), three angles, or (target, side, last angle): the wrist / ankle at the target with the elbow /
# knee solved at the design's lengths (side -1 bends a downward limb's middle joint to the image right, +1 to the image
# left), then the hand / foot at the last angle; ("grip", at, side, last) puts the hand on the snowball's rim.
POSES = {
    "a_wind": ("nunu_attack01@412",
               "抬爪：威朗普身子往左后方仰，远侧（画面右边）的手臂高高举过头顶、爪子张开准备拍下去，近侧手臂垂在身边；努努扶着鹿角往后仰（普攻起手）",
               "WIND-UP - the yeti leaning back toward the image left, his FAR arm (image right) raised high above his head with "
               "the claws spread, ready to swipe down, the near arm hanging at his side; the boy holding on to the antlers, "
               "leaning back.",
               dict(pelvis=(29.0, 52.0), lift=None, shift=0, spine=-174, far_arm=(165, 175, 180), near_arm="rest",
                    near_leg=((18.0, 63.0), 1, -50), far_leg=((39.0, 63.0), -1, 50))),
    "a_swipe": ("nunu_attack01@825",
                "拍下：身子往前（画面右边）压，远侧手臂往右下方狠狠拍下去、爪子在身前下方，近侧手臂往后甩；前腿（远侧）往前跨一步（普攻拍中）",
                "SWIPE - pressing forward to the image right, the FAR arm swiping hard down and forward, its claws low in front "
                "of him, the near arm swinging back; the front (far) leg stepping forward.",
                dict(pelvis=(29.0, 52.0), lift=None, shift=-2, spine=162, far_arm=(85, 60, 40), near_arm=(-40, -20, -10),
                     near_leg=((17.0, 63.0), 1, -70), far_leg=((42.0, 63.0), -1, 60))),
    "b_open": ("nunu_spell1@150",
               "张大嘴扑过去：威朗普往前（画面右边）扑，**嘴张得特别大**（上下牙分开，嘴里深红），两只手臂往前张开，后腿蹬地；努努抱紧鹿角（吞噬：咬之前）",
               "LUNGE, JAWS WIDE - the yeti lunging forward to the image right with his MOUTH OPEN VERY WIDE (the upper and "
               "lower teeth far apart, dark red inside), both arms reaching forward and apart, the back leg pushing off; "
               "the boy hugging the antlers.",
               dict(pelvis=(28.0, 52.0), lift=None, shift=-6, spine=148, near_arm=(110, 100, 90), far_arm=(100, 85, 75),
                    near_leg=((14.0, 63.0), 1, -70), far_leg=((41.0, 63.0), -1, 60))),
    "b_bite": ("nunu_spell1@250",
               "咬下：威朗普的头压低往前，**嘴猛地合上咬住**（牙齿咬紧），身子往前趴，两只手臂垂在身下、爪子撑地；努努被甩得往前倾（吞噬：咬中）",
               "BITE - the yeti's head thrust low and forward, his JAWS SNAPPED SHUT (teeth clenched), the body bent far "
               "forward, both arms hanging down under him, the claws on the ground; the boy thrown forward, holding on.",
               dict(pelvis=(27.0, 55.0), lift=None, shift=-8, spine=125, near_arm=(20, 10, 0),
                    far_arm=(30, 15, 0), near_leg=((16.0, 63.0), 1, -70), far_leg=((36.0, 63.0), -1, 60))),
    "w_pack": ("nunu_spell2_in@208",
               "搓雪球：威朗普弯腰蹲下，远侧（画面右边）的手在身前地上拍一个**小雪球**（白色圆盘的位置和大小），近侧的手撑在膝盖上；努努探头往下看（史上最大雪球：起手）",
               "PACKING THE SNOWBALL - the yeti bent down in a crouch, his FAR hand patting a SMALL SNOWBALL on the ground in "
               "front of him (image right; the white disc's place and size), the near hand on his knee; the boy leaning over "
               "to look.",
               dict(pelvis=(29.0, 55.0), lift=None, shift=-8, spine=155, ball_at=(56.0, 58.0), ball_r=5.0,
                    near_arm=(10, 30, 60), far_arm=("grip", None, -1, None),
                    near_leg=((18.0, 63.0), 1, -60), far_leg=((38.0, 63.0), -1, 60))),
    "w_push1": ("nunu_spell2_in@1458",
                "推雪球 1（远侧腿在前）：身子往前倾，远侧（画面右边）的手臂伸直推着身前一个**大雪球**（白色圆盘），近侧手臂往后摆，近侧腿往后蹬直，远侧腿在身下；努努抱着鹿角大笑（史上最大雪球：滚动）",
                "PUSHING THE SNOWBALL 1 - leaning forward, the FAR arm stretched out pushing a BIG SNOWBALL rolling in front "
                "of him (image right; the white disc), the near arm swinging back, the near leg pushing back straight, the "
                "far leg under the body; the boy holding the antlers, laughing.",
                dict(pelvis=(25.0, 52.0), lift=None, shift=-14, spine=150, ball_at=(57.0, 52.0), ball_r=11.0,
                     near_arm=(-40, -25, -10), far_arm=("grip", None, -1, None),
                     near_leg=((10.0, 63.0), 1, -80), far_leg=((30.0, 63.0), -1, 50))),
    "w_push2": ("nunu_spell2_in@1250",
                "推雪球 2（近侧腿在前）：和推雪球 1 一样推着大雪球，两条腿换过来——近侧腿在身下，远侧腿往后蹬，近侧手臂往前摆（滚动的另一帧）",
                "PUSHING THE SNOWBALL 2 - the same push of the big snowball with the far arm, the legs the other way: the "
                "NEAR leg under the body, the FAR leg pushing back straight, the near arm swinging forward.",
                dict(pelvis=(25.0, 51.0), lift=1, shift=-14, spine=152, ball_at=(57.0, 52.0), ball_r=11.0,
                     near_arm=(20, 40, 60), far_arm=("grip", None, -1, None),
                     near_leg=((26.0, 63.0), 1, -40), far_leg=((12.0, 63.0), 1, -80))),
    "w_hit": ("nunu_spell2_release@275",
              "撞上：雪球撞碎了（不画雪球），威朗普被震得往左后方仰，两只手臂往两边甩开，嘴张着；努努往后仰（史上最大雪球：撞上）",
              "IMPACT - the snowball has burst (no snowball drawn), the yeti thrown back toward the image left by the crash, "
              "both arms flung out wide, his mouth open; the boy leaning back.",
              dict(pelvis=(30.0, 52.0), lift=None, shift=2, spine=-165, near_arm=(-140, -155, -165),
                   far_arm=(140, 155, 165), near_leg=((22.0, 63.0), 1, -50), far_leg=((40.0, 63.0), -1, 50))),
    "e_throw1": ("nunu_spell3@92",
                 "扔雪球 1：威朗普站稳（两脚分开，手臂微微张开），**努努在他头上用近侧的手臂往前（画面右边）扔出一个雪球**——手臂伸直在前，手里刚飞出一个白色小雪球（3 格大），另一只手扶着鹿角（雪球飞射）",
                 "THROW 1 - the yeti standing firm (feet apart, arms a little out), and ON HIS HEAD THE BOY throwing a "
                 "snowball forward with one arm - that arm stretched out to the image right, a small white snowball (3 "
                 "squares) just leaving his hand - the other hand on an antler.",
                 dict(pelvis=(29.0, 52.0), lift=None, shift=0, spine=176, near_arm=(-20, -5, 10), far_arm=(40, 25, 15),
                      near_leg=((18.0, 63.0), 1, -50), far_leg=((40.0, 63.0), -1, 50))),
    "e_throw2": ("nunu_spell3@275",
                 "扔雪球 2：威朗普同样站稳，身子往另一边晃一点；**努努换另一只手**：这只手举到脑后拿着一个雪球准备扔，刚扔完的手臂往前收回来（雪球飞射的另一帧）",
                 "THROW 2 - the yeti standing firm, swaying a little the other way; THE BOY switching hands: his other arm "
                 "cocked back behind his head holding a snowball ready to throw, the first arm following through forward.",
                 dict(pelvis=(29.0, 52.0), lift=None, shift=0, spine=-176, near_arm=(-30, -15, 0), far_arm=(30, 15, 5),
                      near_leg=((18.0, 63.0), 1, -50), far_leg=((40.0, 63.0), -1, 50))),
    "r_raise": ("nunu_spell4@1150",
                "举手召唤暴风雪：两腿大大分开站稳，**两只手臂高高举起往两边张开**，嘴张大像在吼；努努也两只手举过头顶（绝对零度：引导）",
                "CALLING THE BLIZZARD - the legs planted wide apart, BOTH ARMS RAISED HIGH and spread to the sides, his mouth "
                "wide open as if roaring; the boy also raising both arms above his head.",
                dict(pelvis=(29.0, 53.0), lift=None, shift=0, spine=180, near_arm=(-140, -155, -165),
                     far_arm=(140, 155, 165), near_leg=((15.0, 63.0), 1, -60), far_leg=((43.0, 63.0), -1, 60))),
    "r_slam": ("nunu_spell4@2683",
               "砸地爆发：深深蹲下，身子往前弓，**两只拳头一起砸在身前的地上**；努努往前探身（绝对零度：结束爆发）",
               "SLAM - squatting deep, hunched forward, BOTH FISTS smashing the ground in front of him together; the boy "
               "leaning forward.",
               dict(pelvis=(29.0, 56.0), lift=None, shift=-4, spine=148, near_arm=((39.0, 63.0), -1, 90),
                    far_arm=((47.0, 63.0), -1, 90), near_leg=((17.0, 63.0), 1, -60), far_leg=((37.0, 63.0), -1, 60))),
    "run1": ("nunu_run01@0",
             "跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子微微前倾，近侧手臂往前摆，远侧手臂往后摆",
             "RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back behind, "
             "leaning forward a little, the near arm swinging forward, the far arm back.",
             dict(pelvis=(29.0, 52.0), lift=None, shift=0, spine=172, near_arm=(40, 55, 65), far_arm=(-25, -15, -5),
                  near_leg=((16.0, 63.0), 1, -70), far_leg=((41.0, 63.0), -1, 60))),
    "run2": ("nunu_run01@292",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两只手臂垂在身边",
             "RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, "
             "both arms hanging close.",
             dict(pelvis=(29.0, 51.0), lift=1, shift=0, spine=174, near_arm=(5, 0, 0), far_arm=(5, 0, 0),
                  near_leg=((27.0, 63.0), 1, -40), far_leg=((37.0, 57.0), -1, 70))),
    "run3": ("nunu_run01@583",
             "跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：身子微微前倾，远侧手臂往前摆，近侧手臂往后摆",
             "RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back behind, "
             "leaning forward a little, the far arm swinging forward, the near arm back.",
             dict(pelvis=(29.0, 52.0), lift=None, shift=0, spine=172, near_arm=(-30, -20, -10), far_arm=(45, 60, 70),
                  near_leg=((39.0, 63.0), -1, 60), far_leg=((17.0, 63.0), 1, -70))),
    "run4": ("nunu_run01@875",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两只手臂垂在身边",
             "RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, "
             "both arms hanging close.",
             dict(pelvis=(29.0, 51.0), lift=1, shift=0, spine=174, near_arm=(0, 5, 5), far_arm=(0, 5, 5),
                  near_leg=((34.0, 57.0), -1, 70), far_leg=((31.0, 63.0), -1, 40))),
    "d_fall": ("nunu_death01@600",
               "往前倒：威朗普膝盖一软往前扑倒，两只手臂垂在身下，头往下垂；努努从他头上往前翻下来（死亡第一下）",
               "COLLAPSING - the yeti's knees giving way, falling forward, both arms hanging down under him, "
               "his head drooping; the boy tumbling forward off his head.",
               dict(pelvis=(26.0, 55.0), lift=None, shift=-6, spine=118, near_arm=(15, 5, 0),
                    far_arm=(25, 10, 0), near_leg=((16.0, 63.0), 1, -80), far_leg=((33.0, 63.0), -1, 60))),
    # League's death ends on his belly; the head box is pasted upright, so ours lies with the head resting on the ground
    "d_lie": ("nunu_death01@2988",
              "趴倒：威朗普**趴在地上**（肚子贴地，身子横着朝画面右边），两只手臂往前平伸在地上，腿往后伸平，眼睛闭上（画成 X 或一道线），"
              "头搁在地上；努努坐在他头前面的地上晕乎乎的（死亡）",
              "LYING FLAT - the yeti lying on his belly on the ground, the body stretched out toward the image right, both "
              "arms flat on the ground in front, the legs stretched out flat behind, his eyes closed (drawn as X or a line), "
              "his head resting on the ground; the boy sitting dazed on the ground in front of his head.",
              dict(pelvis=(16.0, 59.0), lift=None, shift=-6, spine=95, near_arm=(95, 92, 90), far_arm=(92, 90, 90),
                   near_leg=(-95, -92, -90), far_leg=(-92, -90, -90))),
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
    """build_raw with `ball_at` read on the finished skeleton (after the drop onto the ground): the legs and the spine
    alone set the drop, so a first pass finds it and the second places the ball (and the hands on it) there."""
    if "ball_at" not in spec:
        return build_raw(spec)
    first = build_raw(spec)
    dy = first["spine"][0][1] - spec["pelvis"][1]
    bx, by = spec["ball_at"]
    return build_raw(dict(spec, ball_at=(bx, by - dy)))


def build_raw(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (pasted, never
    turned); the snowball where the pose puts it. The lowest foot, knee or hand on the ground, or `lift` rows over it."""
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
        if sp[0] == "grip":         # the hand on the snowball's rim at that angle (from the ball's centre)
            _, at, side, last = sp
            if at is None:            # the rim point nearest the shoulder
                at = ang(spec["ball_at"], pts[0])
            target = along(spec["ball_at"], at, spec["ball_r"])
            if last is None:          # the claws over the rim, toward the ball's middle
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
    if "ball_at" in spec:
        sk["ball"] = spec["ball_at"]
    reach = sk.pop("reach", {})
    low = max(y for limb in ("near_leg", "far_leg", "spine", "near_arm", "far_arm") for _, y in sk[limb])
    dy = GROUND - (spec["lift"] or 0) - low
    out = {k: ((v[0], v[1] + dy) if k in ("head", "ball") else [(x, y + dy) for x, y in v]) for k, v in sk.items()}
    out["reach"] = reach
    out["ball_r"] = spec.get("ball_r")
    return out


def to_canvas(sk, shift=0):
    return {k: (v if k in ("reach", "ball_r") else (v[0] + DX + shift, v[1] + DY) if k in ("head", "ball")
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
    a bigger dot on each hand; the snowball a white disc behind the limbs."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    if "ball" in s:
        bx, by = s["ball"]
        r = s["ball_r"]
        dr.ellipse([(bx - r) * PX, (by - r) * PX, (bx + r) * PX, (by + r) * PX],
                   fill=BALL + (150,), outline=(110, 150, 200, alpha), width=4)
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 90), outline=(90, 90, 90, alpha), width=3)
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


def lol_frame(lol, frame, work, yaw=35):
    """League's frame (Nunu & Willump at the 3/4 camera, the skin's own submeshes and Willump's map: SKIN)."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Nunu",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", "900", "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", str(yaw), "--name", "f",
           "--out", work, "--frame", frame] + SKIN
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
    """Every bone, the head box and the snowball on the canvas; no hand over a face, the hands on the snowball."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    if "ball" in s:
        bx, by = s["ball"]
        r = s["ball_r"]
        if bx - r < 1 or bx + r > CANVAS / PX - 1 or by + r > SOLE_Y / PX + 0.6:
            out.append(f"snowball off the canvas / below the ground ({bx:.0f}, {by:.0f})")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]   # the design's (0, 0) as the head box has it
    for fx0, fx1, fy0, fy1 in FACES:
        fx0, fx1, fy0, fy1 = fx0 + ox, fx1 + ox, fy0 + oy, fy1 + oy
        face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
        if face:
            out.append(f"hand over a face at {[(round(x), round(y)) for x, y in face[:3]]}")
    for arm, gap in s.get("reach", {}).items():
        if gap > 1.0:
            out.append(f"{arm} {gap:.1f} squares short of the snowball's rim")
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
    ap.add_argument("--out", default="C:/t/nu_work/nunu_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
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
            hx, hy = s["head"]                       # the design's head box, to judge the proportions
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
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

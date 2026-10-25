#!/usr/bin/env python3
"""Yorick's pose pack for Codex (assets/source/yorick/POSE_PROMPTS.md): the whole-body poses his League clips go
through (the user, 2026-10-25: 「动作帧用 Codex 骨架姿势包」, pack_illaoi_poses.py's way).

    python tools/art/pack_yorick_poses.py [--out C:/t/yo_work/yorick_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (step 0's A-2 as drawn, 74
x 83) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames (tools/lol/pose_ref.py
at the 3/4 camera, his cloth cape hidden): every bone at the design's OWN length (measured on hd/idle.png at 12x: REST),
only its direction set per pose (POSES), the lowest foot on the ground unless the pose lifts it. The prompt gives the
legs' and arms' lengths in squares and asks Codex to count them.
HIS SHOVEL is a big prop, as long as he is tall (SHOVEL_L squares: the spear point on top, the shield-shaped spade at the
bottom; in the design upright on the image left, its spade on the ground): each pose places it by the point the
SHOVEL hand holds (`grip`, at `frac` of its length from the point) and its direction (`dir`, the point -> the spade,
degrees: 0 the spade straight down, 90 to the image right, 180 up, -90 to the image left); `free` puts the other hand on
it too (at that fraction), `main: "free"` lets the FREE hand hold it instead; `loose` (centre, dir) is a shovel no hand
holds. Drawn on the skeleton as a translucent haft with the spade and the point. Overhead and level swings are tilted
so the whole shovel stays on the canvas (League swings it level; 83 squares do not fit across).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head in the hood, 8x: every pose wears it); 2_design.png (the design on the grid); per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), PURPLE = the SHOVEL arm (image left in the design, its hand on the haft), ORANGE = the FREE arm (image right
in the design, hanging); grey box = the head (the hood and face, never redrawn); teal = the shovel.
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
from design_yorick_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_illaoi_poses import ang, along, turned, bend, canvas_grid as _grid, tile_sheet  # noqa: E402
import pack_illaoi_poses as IP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yorick")
PX, CANVAS, SOLE_Y = 11, 1254, 1188
GREY = (225, 225, 225)
GROUND = 82                        # the design's soles' bottom edge (rows)
DX, DY = 22, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 108)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "shovel_arm": (150, 60, 200),
       "free_arm": (255, 140, 0)}
HEAD = (19, 43, 34, 54)            # rows / columns of the hood and face in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 20 x 24 squares
FACE = (43, 52, 27, 40)            # the face (eyes, nose, goatee): x0, x1, y0, y1 in design squares
SHOVEL_L = 83                      # the point's tip to the spade's tip (hd/idle.png col ~10, rows 0-83)
SPADE = (24, 16)                   # the spade: length along the haft, width (squares)
POINT = (11, 8)                    # the spear point with its tassels
TEAL = (60, 170, 190)

# the design's own skeleton, measured on hd/idle.png (74 x 83, square edges): the head box's middle; the spine pelvis
# (the belt buckle) -> the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (the shovel hand up on
# the haft, its forearm raised; the free fist hanging by the thigh); each leg hip, knee, ankle, toes
REST = {
    "head": (44.0, 31.0),
    "spine": [(42.0, 58.0), (44.0, 41.0)],
    "shovel_arm": [(27.0, 37.0), (19.0, 45.0), (12.5, 33.0), (10.0, 30.0)],
    "free_arm": [(58.0, 41.0), (63.0, 52.0), (66.0, 63.0), (67.0, 69.0)],
    "near_leg": [(36.0, 60.0), (33.0, 69.0), (31.0, 77.0), (25.0, 81.0)],
    "far_leg": [(49.0, 60.0), (50.0, 69.0), (53.0, 77.0), (60.0, 81.0)],
    "shovel": dict(grip=(10.5, 32.0), frac=0.39, dir=0.0),
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees as above) - each bone at the design's own
# length (REST). A limb is "rest", three angles, (target, side, last angle) - the wrist / ankle at the target with the
# elbow / knee solved (side -1 bends a downward limb's middle joint to the image right, +1 to the image left) - or
# "haft" (the hand on the shovel). "shovel": grip / frac / dir (and free / main), or loose=(centre, dir).
H = "haft"
POSES = {
    "a_wind": ("yorick_attack1@183",
               "抡铲起手：身子往左后方仰，两只手握着铲柄上段，把铲子往左上方高高抡到身后（铲头在画面左上方，不挡脸），两腿分开站稳（普攻起手）",
               "WIND-UP - leaning back toward the image left, BOTH hands on the upper haft swinging the shovel up "
               "behind him to the upper left (the spade high on the image left, never over the face), feet planted "
               "wide apart.",
               dict(pelvis=(42.0, 58.0), lift=None, shift=13, spine=-172,
                    shovel=dict(grip=(20.0, 32.0), frac=0.1, dir=-137.0),
                    shovel_arm=H, free_arm=(45, 135, 160), sides=dict(shovel_arm=-1), near_leg=((29.0, 81.0), 1, -60), far_leg=((56.0, 81.0), -1, 60))),
    "a_smash": ("yorick_attack1@367",
                "砸下：身子往前压，弓步蹲低，两只手握着铲柄中段，把铲头狠狠砸在身前（画面右边）的地上，铲柄从左上方斜下来（普攻砸中）",
                "SMASH - pressing forward and down in a deep lunge, BOTH hands on the middle of the haft driving the "
                "spade into the ground in front of him (on the image right), the haft slanting down from the upper left.",
                dict(pelvis=(40.0, 63.0), lift=None, shift=-4, spine=145,
                     shovel=dict(grip=(47.0, 56.0), frac=0.5, dir=60.0, free=0.38),
                     shovel_arm=H, free_arm=H, near_leg=((23.0, 81.0), 1, -60), far_leg=((54.0, 81.0), -1, 60))),
    "q_raise": ("yorick_spell1@183",
                "高举铲子：身子挺直往后仰，两只手把铲子高高举过头顶，铲头甩到左后上方（画面左上，不挡脸），近侧腿往前迈一步（临终仪式起手）",
                "BIG RAISE - straight and leaning back, BOTH hands lifting the shovel high over his head, the spade flung "
                "up behind him to the upper left (never over the face), the near leg stepping forward.",
                dict(pelvis=(42.0, 57.0), lift=None, shift=15, spine=-170,
                     shovel=dict(grip=(24.0, 18.0), frac=0.12, dir=-126.0, behind=True),
                     shovel_arm=H, free_arm=(150, 160, 170), near_leg=((46.0, 81.0), -1, 60), far_leg=((30.0, 81.0), 1, -60))),
    "q_slam": ("yorick_spell1@367",
               "重重砸地：弓步蹲得更低，身子往前扑，两只手握在铲柄下段，把铲头整个砸进身前（画面右边）的地里（临终仪式砸中）",
               "HEAVY SLAM - an even deeper lunge, the body thrown forward, BOTH hands low on the haft slamming the whole "
               "spade into the ground in front of him (on the image right).",
               dict(pelvis=(40.0, 65.0), lift=None, shift=-8, spine=138,
                    shovel=dict(grip=(49.0, 60.0), frac=0.55, dir=62.0, free=0.43),
                    shovel_arm=H, free_arm=H, near_leg=((21.0, 81.0), 1, -70), far_leg=((55.0, 81.0), -1, 60))),
    "w_raise": ("yorick_spell2@240",
                "竖举铲子：站直，两只手一上一下握住铲柄，把铲子竖着高高举在身前（铲头朝上、高过头顶，尖头朝下），准备往地上插（暗灵缠身 / 唤醒起手）",
                "RAISE UPRIGHT - standing straight, BOTH hands one above the other on the haft holding the shovel "
                "upright high in front of him (the spade up above his head, the point down), ready to drive it down.",
                dict(pelvis=(42.0, 58.0), lift=None, shift=4, spine=178,
                     shovel=dict(grip=(60.0, 34.0), frac=0.55, dir=180.0, main="free"),
                     shovel_arm=(70, 90, 100), free_arm=H, near_leg=((33.0, 81.0), 1, -60), far_leg=((52.0, 81.0), -1, 60))),
    "w_slam": ("yorick_spell2@360",
               "插地蹲下：深深蹲下，两只手握着铲柄把铲头往下插进身前的地里（铲子竖直，铲头贴着地面线），头低一点往前看（暗灵缠身 / 唤醒）",
               "DRIVE DOWN - squatting deep, BOTH hands on the haft driving the spade straight down into the ground in "
               "front of him (the shovel upright, the spade on the ground line), the head a little lower, looking ahead.",
               dict(pelvis=(42.0, 66.0), lift=None, shift=0, spine=165,
                    shovel=dict(grip=(62.0, 55.0), frac=0.68, dir=2.0, main="free"),
                    shovel_arm=(60, 75, 85), free_arm=H, near_leg=((30.0, 81.0), 1, -50), far_leg=((55.0, 81.0), -1, 50))),
    "k_call": ("yorick_spell1_cast@480",
               "召唤：空着的那只手高高举起、五指张开（召唤雾行者），握铲的手把铲子斜着垂在身后左下方（铲头在画面左下），身子挺直（唤醒雾行者）",
               "SUMMON - the FREE hand raised high with the fingers spread (calling the dead up), the shovel hand holding "
               "the shovel slanting down behind him (the spade low on the image left), standing straight.",
               dict(pelvis=(42.0, 58.0), lift=None, shift=4, spine=-176,
                    shovel=dict(grip=(12.0, 36.0), frac=0.45, dir=0.0),
                    shovel_arm=H, free_arm=(160, 175, 180), near_leg=((32.0, 81.0), 1, -60),
                    far_leg=((54.0, 81.0), -1, 60))),
    "e_wind": ("yorick_spell3@133",
               "扔雾起手：身子往左后方扭，空着的那只手往后下方甩（准备扔出黑雾），握铲的手把铲子斜举在身后左上方，两腿分开（哀伤之雾起手）",
               "THROW WIND-UP - twisting back toward the image left, the FREE hand swung back and down behind him (about "
               "to throw), the shovel hand holding the shovel slanted up behind him to the upper left, feet apart.",
               dict(pelvis=(42.0, 59.0), lift=None, shift=12, spine=-168,
                    shovel=dict(grip=(18.0, 38.0), frac=0.45, dir=-160.0),
                    shovel_arm=H, free_arm=(-40, -60, -70), near_leg=((30.0, 81.0), 1, -60),
                    far_leg=((55.0, 81.0), -1, 60))),
    "e_throw": ("yorick_spell3@267",
                "扔出黑雾：身子往前压，空着的那只手往前（画面右边）甩出去、手臂伸直、手掌张开，握铲的手把铲子斜在身后，后腿蹬直（哀伤之雾扔出）",
                "THROW - pressing forward, the FREE arm flung straight out to the image right, the hand open (throwing), "
                "the shovel hand keeping the shovel slanted behind him, the back leg pushing straight.",
                dict(pelvis=(42.0, 60.0), lift=None, shift=-6, spine=158,
                     shovel=dict(grip=(26.0, 44.0), frac=0.45, dir=-150.0),
                     shovel_arm=H, free_arm=(95, 92, 90), near_leg=((26.0, 81.0), 1, -70),
                     far_leg=((54.0, 81.0), -1, 60))),
    "r_raise": ("yorick_spell4@200",
                "高举召唤：踮起脚、身子往上挺，两只手把铲子高高举过头顶（铲头朝左上、斜着），仰头（海屿悼词起手）",
                "RAISE TO THE SKY - up on his toes, the body stretched up, BOTH hands holding the shovel high above his "
                "head (the spade slanting up to the upper left), the head held high.",
                dict(pelvis=(42.0, 56.0), lift=3, shift=10, spine=-178,
                     shovel=dict(grip=(20.0, 24.0), frac=0.55, dir=180.0),
                     shovel_arm=H, free_arm=(150, 165, 175), near_leg=(5, 0, -20), far_leg=(-5, 5, 30))),
    "r_plant": ("yorick_spell4@400",
                "立铲：站得笔直，空着的那只手握住铲柄，把铲子竖着立在身前右边（铲头着地），另一只手臂垂在身边（海屿悼词：室女升起）",
                "PLANT - standing tall, the FREE hand gripping the haft, holding the shovel upright on his front right "
                "(the spade on the ground), the other arm hanging at his side.",
                dict(pelvis=(42.0, 58.0), lift=None, shift=-6, spine=180,
                     shovel=dict(grip=(66.0, 40.0), frac=0.5, dir=0.0, main="free"),
                     shovel_arm=(10, 0, 5), free_arm=H, near_leg=((33.0, 81.0), 1, -60), far_leg=((52.0, 81.0), -1, 60))),
    "run1": ("yorick_run@0",
             "跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子微微前倾，握铲的手拎着铲子斜在身侧（铲头在画面左下、离地），空着的手臂往后摆",
             "RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back, "
             "leaning forward a little, the shovel hand carrying the shovel slanted at his side (the spade low on the "
             "image left, off the ground), the free arm swinging back.",
             dict(pelvis=(42.0, 59.0), lift=None, shift=6, spine=172,
                  shovel=dict(grip=(18.0, 40.0), frac=0.45, dir=-25.0),
                  shovel_arm=H, free_arm=(-30, -20, -10), near_leg=((28.0, 81.0), 1, -70), far_leg=((55.0, 81.0), -1, 60))),
    "run2": ("yorick_run@300",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，铲子还斜拎在身侧，空着的手臂垂在身边",
             "RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, "
             "the shovel still carried slanted at his side, the free arm hanging close.",
             dict(pelvis=(42.0, 57.0), lift=1, shift=6, spine=174,
                  shovel=dict(grip=(18.0, 39.0), frac=0.45, dir=-22.0),
                  shovel_arm=H, free_arm=(10, 0, 0), near_leg=((39.0, 81.0), 1, -40), far_leg=((52.0, 70.0), -1, 70))),
    "run3": ("yorick_run@600",
             "跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：身子微微前倾，铲子斜拎在身侧，空着的手臂往前摆",
             "RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back, "
             "leaning forward a little, the shovel carried slanted at his side, the free arm swinging forward.",
             dict(pelvis=(42.0, 59.0), lift=None, shift=6, spine=172,
                  shovel=dict(grip=(18.0, 40.0), frac=0.45, dir=-25.0),
                  shovel_arm=H, free_arm=(40, 60, 70), near_leg=((52.0, 81.0), -1, 60), far_leg=((30.0, 81.0), 1, -70))),
    "run4": ("yorick_run@900",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，铲子斜拎在身侧",
             "RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, "
             "the shovel carried slanted at his side.",
             dict(pelvis=(42.0, 57.0), lift=1, shift=6, spine=174,
                  shovel=dict(grip=(18.0, 39.0), frac=0.45, dir=-22.0),
                  shovel_arm=H, free_arm=(0, 10, 20), near_leg=((48.0, 70.0), -1, 70), far_leg=((45.0, 81.0), -1, 60))),
    "d_drop": ("yorick_death@567",
               "倒下：被打得往左后方倒，膝盖发软，两只手臂往两边甩开，铲子从手里脱出去往左边倒（不挡脸）（死亡第一下）",
               "COLLAPSE - knocked back toward the image left, the knees giving way, both arms flung out, the shovel "
               "slipping out of his hand and falling away to the image left (never over the face).",
               dict(pelvis=(43.0, 62.0), lift=None, shift=10, spine=-160,
                    shovel=dict(loose=((10.0, 44.0), -35.0)),
                    shovel_arm=(-120, -140, -150), free_arm=(110, 120, 130), near_leg=((33.0, 81.0), 1, -50),
                    far_leg=((52.0, 81.0), -1, 60))),
    # League's death floats his body up as a spirit; the head is pasted upright, so ours hangs upright in the air
    "d_float": ("yorick_death@2267",
                "飘起：身体离地飘在空中（脚离地约 12 格），身子微微往前弓，头低下，两只手臂软软垂着，两腿垂下、膝盖微弯；铲子平躺在他下方的地上（死亡：灵魂飘起）",
                "FLOATING UP - his body lifted off the ground (the feet about 12 squares up), slightly hunched, the head "
                "low, both arms hanging limp, the legs dangling with the knees a little bent; the shovel lying flat on "
                "the ground under him.",
                dict(pelvis=(42.0, 58.0), lift=12, shift=8, spine=172,
                     shovel=dict(loose=((40.0, 80.5), -90.0)),
                     shovel_arm=(-10, 0, 5), free_arm=(10, 5, 0), near_leg=(10, -5, -40), far_leg=(5, -10, 40))),
}


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def ends(sh):
    """The shovel's point and spade tips from its spec."""
    if "loose" in sh:
        (cx, cy), d = sh["loose"]
        return along((cx, cy), d + 180.0, SHOVEL_L / 2), along((cx, cy), d, SHOVEL_L / 2)
    g, f, d = sh["grip"], sh["frac"], sh["dir"]
    return along(g, d + 180.0, f * SHOVEL_L), along(g, d, (1 - f) * SHOVEL_L)


def build(spec):
    """build_raw with the shovel read on the finished skeleton (after the drop onto the ground): the legs and the spine
    alone set the drop, so a first pass finds it and the second places the shovel (and the hands on it) there."""
    first = build_raw(spec)
    dy = first["spine"][0][1] - spec["pelvis"][1]
    sh = dict(spec["shovel"])
    if "loose" in sh:
        return first
    sh["grip"] = (sh["grip"][0], sh["grip"][1] - dy)
    return build_raw(dict(spec, shovel=sh))


def build_raw(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned); the hands on the haft. The lowest foot or knee on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    sh = spec["shovel"]
    top, bot = ends(sh)
    on_haft = lambda f: (top[0] + (bot[0] - top[0]) * f, top[1] + (bot[1] - top[1]) * f)
    main = sh.get("main", "shovel")
    reach = {}
    for name, base, base_rest, k in (("shovel_arm", neck, rs[1], 1.0), ("free_arm", neck, rs[1], 1.0),
                                     ("near_leg", pel, rs[0], 0.5), ("far_leg", pel, rs[0], 0.5)):
        sp = spec[name]
        if sp == "rest":
            sk[name] = [(base[0] + o[0], base[1] + o[1]) for o in
                        (turned((x - base_rest[0], y - base_rest[1]), turn * k) for x, y in REST[name])]
            continue
        off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        ls = lengths(name)
        if sp == H:
            f = sh["frac"] if name.startswith(main) else sh["free"]
            target = on_haft(f)
            side = spec.get("sides", {}).get(name, 1 if name == "shovel_arm" else -1)
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, ang(M, A), ls[2])]
            reach[name] = math.hypot(A[0] - target[0], A[1] - target[1])
        elif len(sp) == 3 and isinstance(sp[0], tuple):
            target, side, last = sp
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    sk["shovel"] = [top, bot]
    low = max(y for leg in ("near_leg", "far_leg", "spine") for _, y in sk[leg])
    dy = GROUND - (spec["lift"] or 0) - low
    out = {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}
    if "loose" in sh:   # a dropped shovel stays where it was put (on the ground: not lifted with him)
        out["shovel"] = [top, bot]
    out["reach"] = reach
    out["behind"] = bool(sh.get("behind"))
    return out


def to_canvas(sk, shift=0):
    return {k: (v if k in ("reach", "behind") else (v[0] + DX + shift, v[1] + DY) if k == "head"
                else [(x + DX + shift, y + DY) for x, y in v]) for k, v in sk.items()}


def c(p):
    return (p[0] * PX, p[1] * PX)


def shovel_shape(dr, top, bot, alpha):
    """The haft, the spade (a shield 16 wide, 24 long, at the bottom end) and the point (8 wide, 11 long, at the top)."""
    d = ang(top, bot)
    nx, ny = turned((1.0, 0.0), d)   # across the haft
    dr.line([c(top), c(bot)], fill=(120, 80, 50, alpha), width=round(1.6 * PX))

    def blade(tip, back, length, width):
        b0 = along(tip, back, length)
        mid = along(tip, back, length * 0.45)
        pts = [tip, (mid[0] + nx * width / 2, mid[1] + ny * width / 2), (b0[0] + nx * width / 3, b0[1] + ny * width / 3),
               (b0[0] - nx * width / 3, b0[1] - ny * width / 3), (mid[0] - nx * width / 2, mid[1] - ny * width / 2)]
        dr.polygon([c(p) for p in pts], fill=TEAL + (90,), outline=(20, 110, 130, alpha))
    blade(bot, d + 180.0, *SPADE)
    blade(top, d, *POINT)


def skeleton(can, s, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("far_leg", "shovel_arm", "spine", "near_leg"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == 2 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    shovel_shape(dr, *s["shovel"], alpha)
    for name in ("free_arm",):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if k == 2 else 6
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
    """League's frame, Yorick at the 3/4 camera, his cloth cape hidden (unsimulated it lies flat on the ground)."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Yorick",
           "--hide-submesh", "Yorick_Cape", "--fit-all", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", "900", "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f",
           "--out", work, "--frame", frame, "--mirror"]
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
    """Every bone, the head box and the shovel on the canvas; no hand and no shovel over the face; hands on the haft."""
    out = []
    pts = [p for k in ("spine", "shovel_arm", "free_arm", "near_leg", "far_leg") for p in s[k]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    for x, y in s["shovel"]:
        if x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6:
            out.append(f"shovel end off the canvas / below the ground ({x:.0f}, {y:.0f})")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    face = [p for p in s["shovel_arm"][2:] + s["free_arm"][2:] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"hand over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    (x0, y0), (x1, y1) = s["shovel"]
    for k in ([] if s.get("behind") else range(41)):
        x, y = x0 + (x1 - x0) * k / 40, y0 + (y1 - y0) * k / 40
        if fx0 <= x <= fx1 and fy0 <= y <= fy1:
            out.append("shovel over the face")
            break
    for arm, gap in s.get("reach", {}).items():
        if gap > 1.0:
            out.append(f"{arm} {gap:.1f} squares short of the haft")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/yo_work/yorick_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), shovel=REST["shovel"],
                                shovel_arm="rest", free_arm="rest", near_leg="rest", far_leg="rest")))
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

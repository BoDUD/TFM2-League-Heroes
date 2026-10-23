#!/usr/bin/env python3
"""Azir's pose pack for Codex (assets/source/azir/POSE_PROMPTS.md): the whole-body poses his League clips go through, each
with his long sceptre held somewhere else (the user, 2026-10-23: 「Codex 照骨架画姿势」, pack_aurora_poses.py's way).

    python tools/art/pack_azir_poses.py [--out C:/t/az_work/azir_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-2 at PPU 1.5,
50 x 73, the sceptre straightened) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's
frames (tools/lol/pose_ref.py at the 3/4 camera): every bone at the design's OWN length (measured on hd/idle.png at 14x:
REST), only its direction set per pose (POSES), the lowest foot on the ground unless the pose lifts it.
HIS HEAD is the falcon helmet (rows 16-35 of 73, HEAD) - pasted on every pose upright, never turned; his chibi arms (about
15 squares on the near side) cannot lift anything over it, so the sceptre goes up beside the head, never over it.
THE SCEPTRE is a rigid prop: in the design a straight bar WAND_L squares long from its foot to the tip of its forked head,
held GRIP of the way from the foot by the NEAR hand (image left), its gold head from TIP0. A pose gives where the hand holds
it ("at") and its direction (deg, foot -> tip); the holding arm's wrist goes to the grip. A dropped sceptre (hand None)
lies where "at" puts its grip.
THE CAPE RIBBONS (the purple ribbons hanging behind him on the image left) are rigid too: the design's own ribbon squares
(tail_mask) moved with his pelvis, never turned - drawn translucent on the skeletons.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's helmet, 8x: every pose wears it); 2_design.png (the design on the grid); per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local); 30_soldier.png,
31_guard.png (the summons' approved designs, 8x: their own poses are drawn from them, no skeleton).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left, holding the sceptre), PURPLE = the FAR arm (image right, the clawed
hand), YELLOW = the sceptre's shaft, CYAN = its gold forked head; grey box = the head (the design's helmet, never
redrawn); the translucent orange shape = the cape ribbons.
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
from design_azir_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "azir")
PX, CANVAS, SOLE_Y = 13, 1254, 1196
GREY = (225, 225, 225)
GROUND = 73                        # the design's soles' bottom edge (rows)
DX, DY = 23, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 92)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "shaft": (235, 200, 0), "point": (0, 200, 220)}
HEAD = (16, 36, 21, 43)            # rows / columns of the helmet (crest, beak, cheek wings) in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 22 x 20 squares
FACE = (33, 42, 24, 34)            # the beak and the glowing eye: x0, x1, y0, y1 in design squares
WAND_L = 71.0                      # the sceptre's foot (12.5, 72) to its tip (8.5, 1) in the design
GRIP, TIP0 = 0.41, 0.63            # the near hand at row 43; the gold forked head from row 27 up
REST_WAND = dict(at=(11.5, 43.0), deg=-176.8, hand="near_arm")


def tail_mask(d):
    """The cape ribbons in hd/idle.png: the purple squares left of the sceptre (columns < 11, rows 47-67)."""
    h, w = d.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    c = d[..., :3].astype(int)
    purple = (c[..., 0] > 80) & (c[..., 1] < 70) & (c[..., 2] > 40)
    return (xx < 11) & (yy >= 47) & (yy <= 67) & purple & (d[..., 3] > 0)


# the design's own skeleton, measured on hd/idle.png (50 x 73, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (the near hand gripping the sceptre, the far
# clawed hand hanging at his side); each leg hip, knee, ankle, toes
REST = {
    "head": (32.0, 26.0),
    "spine": [(30.0, 58.0), (30.0, 34.0)],
    "near_arm": [(22.0, 37.0), (17.0, 43.0), (13.0, 43.0), (10.0, 43.0)],
    "far_arm": [(42.0, 38.0), (44.0, 47.0), (45.0, 54.0), (47.0, 60.0)],
    "near_leg": [(26.0, 58.0), (25.0, 64.0), (24.0, 69.0), (29.0, 72.0)],
    "far_leg": [(35.0, 58.0), (38.0, 64.0), (39.0, 69.0), (46.0, 71.0)],
}

UP = dict(at=(11.5, 43.0), deg=-176.8, hand="near_arm")   # upright in his near hand, as in the design
# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest" (the design's own,
# turned with the spine), three angles, or (target, side, last angle): the wrist / ankle at the target with the elbow /
# knee solved at the design's lengths (side -1 bends a downward limb's middle joint to the image right, +1 to the image
# left), then the hand / foot at the last angle; target "grip" = the sceptre's grip. The sceptre: "at" where the hand
# holds it, "deg" its direction from the foot to the tip, "hand" the arm holding it (None: lying on the ground).
POSES = {
    "c_wind": ("azir_attack_command@150",
               "举手：站直，近侧手握着权杖竖在身旁（和定稿一样），远侧手臂抬起到头的右边、爪子朝上（普攻起手：号令沙兵）",
               "RAISE - standing tall, the sceptre upright in his NEAR hand at his side as in the design, the FAR arm "
               "lifted up beside his head on the image right, the claws up (never over the face).",
               dict(pelvis=(30.0, 58.0), lift=None, shift=0, spine=180, near_arm=("grip", 1, -90),
                    far_arm=(150, 175, 180), near_leg="rest", far_leg="rest", wand=UP)),
    "c_point": ("azir_attack_command@450",
                "指出：身子微微前倾，远侧手臂往右前方平平伸出、爪子指向前方，权杖仍然竖在近侧手里，两腿分开（普攻出手：沙兵代他刺）",
                "COMMAND - leaning forward a little, the FAR arm stretched out level to the image right, the claws "
                "pointing forward, the sceptre still upright in his near hand, the feet apart.",
                dict(pelvis=(30.0, 58.0), lift=None, shift=-2, spine=174, near_arm=("grip", 1, -90),
                     far_arm=(95, 90, 90), near_leg=((22.0, 69.0), 1, 60), far_leg=((41.0, 69.0), -1, 75),
                     wand=dict(at=(14.5, 42.0), deg=-178.0, hand="near_arm"))),
    "q_wind": ("azir_attack1@250",
               "蓄势：微微下蹲、身子往后仰，近侧手把权杖往左后上方斜斜举起（杖头朝左上，不挡脸），远侧手臂往前伸（狂沙猛攻起手）",
               "WIND-UP - crouching a little and leaning back, the NEAR hand cocking the sceptre back slanting to the "
               "upper left (the forked head to the upper left, never over the face), the far arm reaching forward.",
               dict(pelvis=(30.0, 60.0), lift=None, shift=0, spine=-174, near_arm=("grip", 1, -120),
                    far_arm=(110, 120, 120), near_leg=((22.0, 69.0), 1, 50), far_leg=((38.0, 69.0), -1, 75),
                    wand=dict(at=(15.0, 45.0), deg=-145.0, hand="near_arm"))),
    "q_thrust": ("azir_attack1@500",
                 "刺出：大步往前弓步，身子前倾，近侧手把权杖往右前方平平刺出去（杖头朝右，在胸口高度），远侧手臂垂在身侧，两腿大大分开（狂沙猛攻：沙兵冲锋）",
                 "THRUST - a big lunge forward, leaning forward, the NEAR hand thrusting the sceptre out level to the "
                 "image right (the forked head to the right, at chest height), the far arm hanging at his side, the legs "
                 "wide apart.",
                 dict(pelvis=(30.0, 61.0), lift=None, shift=-10, spine=162, near_arm=("grip", -1, 90),
                      far_arm=(10, 0, -10), near_leg=((19.0, 69.0), 1, 30), far_leg=((42.0, 69.0), -1, 80),
                      wand=dict(at=(30.0, 46.0), deg=93.0, hand="near_arm"))),
    "e_dash": ("azir_spell3_dash@300",
               "化沙冲刺：整个人往右前方飞扑（脚离地约 5 格），身子大大前倾，两腿往后拖，近侧手把权杖在头下面往前平平举着（杖头朝右），远侧手臂垂下（流沙移形冲刺）",
               "DASH - flying forward to the image right (the feet about 5 squares up), leaning far forward, both "
               "legs trailing back, the NEAR hand holding the sceptre out ahead of him nearly level, under his head (the "
               "forked head to the right), the far arm hanging down.",
               dict(pelvis=(30.0, 58.0), lift=5, shift=-6, spine=150, near_arm=("grip", -1, 100),
                    far_arm=(10, 0, -10), near_leg=((20.0, 66.0), 1, -40), far_leg=((25.0, 68.0), 1, -30),
                    wand=dict(at=(31.0, 47.0), deg=100.0, hand="near_arm"))),
    "e_land": ("azir_spell3_dash_exit@300",
               "落地：两膝弯下蹲住落地，身子前倾，近侧手把权杖往右前上方斜指（杖头朝右上），远侧手臂往后张开保持平衡（流沙移形落地）",
               "LAND - landing in a crouch with both knees bent, leaning forward, the NEAR hand pointing the sceptre "
               "slanting up ahead (the forked head to the upper right), the far arm out behind for balance.",
               dict(pelvis=(30.0, 62.0), lift=None, shift=-6, spine=166, near_arm=("grip", -1, 120),
                    far_arm=(-20, 0, 10), near_leg=((21.0, 69.0), 1, 30), far_leg=((40.0, 69.0), -1, 75),
                    wand=dict(at=(27.0, 49.0), deg=112.0, hand="near_arm"))),
    "r_raise": ("azir_spell4@112",
                "展臂：站直，权杖竖在近侧手里，远侧手臂往右边大大张开、爪子张开（禁军之墙起手）",
                "SUMMON - standing tall, the sceptre upright in his near hand, the FAR arm spread wide out to the image "
                "right, the claws open.",
                dict(pelvis=(30.0, 58.0), lift=None, shift=-2, spine=-178, near_arm=("grip", 1, -90),
                     far_arm=(110, 120, 125), near_leg=((23.0, 69.0), 1, 55), far_leg=((40.0, 69.0), -1, 75),
                     wand=UP)),
    "r_lift": ("azir_spell4@450",
               "高举：踮脚站高（脚离地约 2 格），近侧手把权杖笔直往上举高（杖头比定稿高约 10 格，在头的左边，不挡脸），远侧手臂往右下方甩（禁军之墙蓄力）",
               "LIFT - up on his toes (the feet about 2 squares up), the NEAR hand lifting the sceptre straight up "
               "high (its head about 10 squares higher than in the design, beside his head on the image left, never "
               "over the face), the far arm flung down to the lower right.",
               dict(pelvis=(30.0, 58.0), lift=2, shift=0, spine=180, near_arm=("grip", 1, 180),
                    far_arm=(60, 40, 30), near_leg=((26.0, 69.0), 1, 40), far_leg=((36.0, 69.0), -1, 60),
                    wand=dict(at=(14.0, 33.0), deg=-177.0, hand="near_arm"))),
    "r_sweep": ("azir_spell4@787",
                "挥杖：身子前倾，近侧手把权杖往右前下方挥出去（杖头朝右下方），远侧手臂往右前方推出、爪子张开，两腿分开（禁军之墙：号令冲锋）",
                "SWEEP - leaning forward, the NEAR hand sweeping the sceptre out to the lower right (the forked head "
                "to the lower right), the far arm pushing forward to the image right with the claws open, the feet "
                "apart.",
                dict(pelvis=(30.0, 59.0), lift=None, shift=-10, spine=166, near_arm=("grip", -1, 70),
                     far_arm=(100, 95, 90), near_leg=((20.0, 69.0), 1, 30), far_leg=((41.0, 69.0), -1, 75),
                     wand=dict(at=(30.0, 48.0), deg=60.0, hand="near_arm"))),
    "run1": ("azir_run_slow@0",
             "跑 1（远侧腿往前迈出着地，近侧腿往后伸）：身子微微前倾，权杖竖着握在近侧手里、杖头微微往前斜，远侧手臂往后摆",
             "RUN 1 - a stride: the FAR leg forward with its foot landing, the NEAR leg stretched back, leaning "
             "forward a little, the sceptre upright in his near hand, its head tilted a little forward, the far arm "
             "swinging back.",
             dict(pelvis=(30.0, 58.0), lift=None, shift=0, spine=174, near_arm=("grip", 1, -90),
                  far_arm=(-20, -10, 0), near_leg=((19.0, 67.0), 1, -50), far_leg=((40.0, 69.0), -1, 70),
                  wand=dict(at=(15.5, 41.0), deg=174.0, hand="near_arm"))),
    "run2": ("azir_run_slow@533",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，权杖一样竖着",
             "RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square "
             "higher, the sceptre upright as before, the far arm swinging down.",
             dict(pelvis=(30.0, 57.0), lift=1, shift=0, spine=176, near_arm=("grip", 1, -90),
                  far_arm=(0, 10, 20), near_leg=((27.0, 69.0), 1, 60), far_leg=((39.0, 63.0), -1, 80),
                  wand=dict(at=(15.5, 40.0), deg=174.0, hand="near_arm"))),
    "run3": ("azir_run_slow@1067",
             "跑 3（近侧腿往前迈出着地，远侧腿往后伸）",
             "RUN 3 - the NEAR leg forward with its foot landing, the FAR leg stretched back, leaning forward a little, "
             "the sceptre upright in his near hand, the far arm swinging forward.",
             dict(pelvis=(30.0, 58.0), lift=None, shift=0, spine=174, near_arm=("grip", 1, -90),
                  far_arm=(30, 50, 60), near_leg=((37.0, 69.0), -1, 70), far_leg=((22.0, 67.0), 1, -50),
                  wand=dict(at=(15.5, 41.0), deg=174.0, hand="near_arm"))),
    "run4": ("azir_run_slow@1600",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格",
             "RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square "
             "higher, the sceptre upright, the far arm swinging down.",
             dict(pelvis=(30.0, 57.0), lift=1, shift=0, spine=176, near_arm=("grip", 1, -90),
                  far_arm=(10, 20, 30), near_leg=((33.0, 63.0), -1, 80), far_leg=((34.0, 69.0), -1, 70),
                  wand=dict(at=(15.5, 40.0), deg=174.0, hand="near_arm"))),
    "d_stagger": ("azir_death@312",
                  "踉跄：身子往左后方倒，膝盖弯下去，远侧手臂往右边甩开，近侧手里的权杖往左歪倒（死亡第一下）",
                  "STAGGER - reeling back toward the image left, the knees buckling, the far arm flung out to the "
                  "right, the sceptre in his near hand tipping over to the left.",
                  dict(pelvis=(30.0, 60.0), lift=None, shift=4, spine=-164, near_arm=("grip", 1, -120),
                       far_arm=(120, 140, 150), near_leg=((24.0, 69.0), 1, 40), far_leg=((37.0, 69.0), -1, 60),
                       wand=dict(at=(15.0, 47.0), deg=-150.0, hand="near_arm"))),
    "d_kneel": ("azir_death@1250",
                "跪倒：单膝跪在地上（近侧膝盖着地），身子往前垂，远侧手撑在膝上，近侧手臂垂下撑地；权杖平躺在他身前的地上，杖头朝右（死亡）",
                "DOWN - kneeling on one knee (the near knee on the ground), slumped forward, the far hand on his knee, "
                "the near arm hanging down to the ground; the sceptre lying flat on the ground in front of him, its "
                "forked head to the image right.",
                dict(pelvis=(30.0, 64.0), lift=None, shift=-12, spine=160, near_arm=(10, 0, 0),
                     far_arm=((41.0, 63.0), -1, 30), near_leg=(5, -85, -90), far_leg=((42.0, 70.0), -1, 80),
                     wand=dict(at=(30.0, 72.0), deg=90.0, hand=None))),
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
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Azir",
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
    over = [] if b.get("behind") else bpts
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] + over if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/az_work/azir_pose_pack")
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
    for k, name in ((30, "soldier"), (31, "guard")):
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
        big(d).save(os.path.join(out, f"{k}_{name}.png"))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Taliyah's pose pack for Codex (assets/source/taliyah/POSE_PROMPTS.md): the whole-body poses her League clips go through
(pack_singed_poses.py's way, without a held prop; the surf poses stand her on her boulder).

    python tools/art/pack_taliyah_poses.py [--out C:/t/ta_work/taliyah_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-2, 33 x 70,
PPU 1.75) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames
(tools/lol/pose_ref.py at the 3/4 camera; ours keep the face to the front-right): every bone at the design's OWN length
(measured on hd/idle.png at 12x: REST), only its direction set per pose (POSES), the lowest foot on the ground unless the
pose lifts it. Her move is the rock surf (the passive; League's Run_Passive): she crouches on her boulder, so the surf
poses lift the feet ROCK_H rows and the boulder (a rigid prop, ROCK_W x ROCK_H squares, brown) stands under them.
THE HEAD (hd/idle.png rows 0-30, columns 2-31: the piled hair, the ornament, the face down to the chin - a chibi head, 40%
of her) is pasted on every pose upright, never turned. Her two red coat panels with their stones are cloth: they swing
with each pose (told in words, not on the skeleton).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png; 1_head.png (8x); 2_design.png; per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right); grey box = the head; the brown
box = the boulder.
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
from design_taliyah_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "taliyah")
PX, CANVAS, SOLE_Y = 11, 1254, 1188
GREY = (225, 225, 225)
GROUND = 70                        # the design's soles' bottom edge (rows)
DX, DY = 40, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 108)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "rock": (140, 90, 50)}
HEAD = (0, 30, 2, 31)              # rows / columns of the head in hd/idle.png (ends exclusive): hair top to the chin
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 29 x 30 squares
FACE = (14, 28, 19, 28)            # the face (the brows, the eyes, the mouth): x0, x1, y0, y1 in design squares
ROCK_W, ROCK_H = 44.0, 24.0        # the surf boulder (B's at the design's scale: 72 x 42 of 110 rows -> about 46 x 27)

# the design's own skeleton, measured on hd/idle.png (33 x 70, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips; each leg hip, knee, ankle, toes
REST = {
    "head": (16.5, 15.0),
    "spine": [(19.0, 52.0), (19.0, 31.0)],
    "near_arm": [(12.0, 36.0), (10.0, 42.0), (8.0, 47.0), (5.0, 50.0)],
    "far_arm": [(26.0, 36.0), (28.0, 42.0), (29.0, 47.0), (32.0, 50.0)],
    "near_leg": [(15.0, 53.0), (13.0, 60.0), (12.0, 66.0), (15.0, 69.5)],
    "far_leg": [(22.0, 53.0), (23.0, 60.0), (23.0, 66.0), (26.0, 69.5)],
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "rock" (True: the boulder under
# her feet, lift = ROCK_H), "shift" (squares the whole figure is moved on the canvas), the spine's direction and every
# limb (degrees: 0 straight down, 90 to the image right, 180 up, -90 to the image left) - each bone at the design's own
# length (REST). A limb is "rest", three angles, or (target, side, last angle): the wrist / ankle at the target with the
# elbow / knee solved (side -1 bends a downward limb's middle joint to the image right, +1 to the image left), then the
# hand / foot at the last angle.
SURF_LEGS = dict(near_leg=((13.0, 69.0), -1, 80), far_leg=((25.0, 69.0), -1, 85))
POSES = {
    "a_wind": ("taliyah_attack1@450",
               "召石：身子微微后仰，远侧手臂高高举到头的右上方、手掌朝上（一块小石头浮在手上方），近侧手臂往后下方摆，两腿站稳，红垂带往后飘（普攻起手）",
               "SUMMON - leaning back a little, the FAR arm raised high above the head on the image right, palm up (a small "
               "stone floating over the hand), the NEAR arm swung back and down, the legs planted, the red panels "
               "swinging back.",
               dict(pelvis=(19.0, 52.0), lift=None, shift=0, spine=-176, far_arm=(140, 150, 160),
                    near_arm=(-30, -20, -10), near_leg=((12.0, 66.0), 1, 70), far_leg=((25.0, 66.0), -1, 80))),
    "a_throw": ("taliyah_attack1@650",
                "甩出：身子往前（画面右边）压，远侧手臂往右前方甩出、手张开（石头刚扔出去），近侧手臂往后摆，远侧腿往前一步（普攻打出）",
                "THE FLICK - leaning forward to the image right, the FAR arm flung forward to the right with the hand open "
                "(the stone just thrown), the NEAR arm swung back, the far leg a step forward.",
                dict(pelvis=(19.0, 53.0), lift=None, shift=-2, spine=172, far_arm=(105, 95, 90),
                     near_arm=(-40, -30, -20), near_leg=((11.0, 66.0), 1, 60), far_leg=((28.0, 66.0), -1, 85))),
    "q_raise": ("taliyah_spell1_0@300",
                "举手召石：身子挺直、微微踮脚，远侧手臂往右上方伸直、手指张开（一串石头从地上升起），近侧手臂往左下方甩开（石穿：起手）",
                "THE CALL - standing tall on her toes, the FAR arm stretched up to the upper right with the fingers spread "
                "(a string of rocks rising from the ground), the NEAR arm flung out to the lower left.",
                dict(pelvis=(19.0, 51.0), lift=1, shift=0, spine=178, far_arm=(140, 145, 150),
                     near_arm=(-60, -50, -45), near_leg=((14.0, 65.0), 1, 30), far_leg=((24.0, 65.0), -1, 40))),
    "q_cast": ("taliyah_spell1_0@600",
               "推出石串：身子往前（画面右边）压低，远侧手臂往正前方推直、手掌朝前（石头一颗颗射出去），近侧手臂往后伸开保持平衡，弓步（石穿：射出）",
               "THE VOLLEY - leaning forward and low to the image right, the FAR arm pushed straight forward, palm out (the "
               "rocks shooting out one after another), the NEAR arm stretched back for balance; a lunge.",
               dict(pelvis=(18.0, 54.0), lift=None, shift=-2, spine=165, far_arm=(95, 90, 90),
                    near_arm=(-70, -75, -80), near_leg=((9.0, 66.0), 1, 60), far_leg=((29.0, 66.0), -1, 85))),
    "e_raise": ("taliyah_spell3@400",
                "双手举石：两只手臂一起往左上、右上方高高举起成 V 字（手在头发两边的外面，不挡脸），手指张开托着一片碎石，身子挺直（撒石阵：起手）",
                "BOTH HANDS UP - both arms raised high in a V to the upper left and upper right (the hands outside the hair "
                "on either side, never over the face), the fingers spread holding up a spray of pebbles, standing tall.",
                dict(pelvis=(19.0, 52.0), lift=None, shift=0, spine=180, far_arm=(140, 150, 160),
                     near_arm=(-140, -150, -160), near_leg=((14.0, 66.0), 1, 50), far_leg=((24.0, 66.0), -1, 70))),
    "e_sweep": ("taliyah_spell3@900",
                "撒雷：身子往前弯、半蹲，两只手臂一起从上往前下方扫出去、手张开（一片石雷撒到身前地上），两腿分开（撒石阵：撒出）",
                "THE SCATTER - bent forward in a half crouch, both arms swept down and forward, the hands open (a spray of "
                "mines thrown onto the ground in front of her), the legs apart.",
                dict(pelvis=(18.0, 56.0), lift=None, shift=-2, spine=150, far_arm=(60, 50, 45),
                     near_arm=(40, 30, 30), near_leg=((10.0, 66.0), 1, 50), far_leg=((28.0, 66.0), -1, 70))),
    "w_crouch": ("taliyah_spell2_0@0",
                 "按地：蹲下来，远侧手掌按在身前的地上（地面要隆起），近侧手臂往后上方扬起，膝盖弯着（岩突：按地）",
                 "PRESSING THE GROUND - crouched down, the FAR palm pressed on the ground in front of her (the ground about "
                 "to erupt), the NEAR arm thrown up and back, the knees bent.",
                 dict(pelvis=(18.0, 60.0), lift=None, shift=-2, spine=155, far_arm=((32.0, 68.0), -1, 90),
                      near_arm=(-130, -140, -150), near_leg=((11.0, 66.0), 1, 30), far_leg=((27.0, 66.0), -1, 90))),
    "w_push": ("taliyah_spell2_0@450",
               "横推：站起来，身子转向右前方，远侧手臂往右边横着一推、手掌朝外（把敌人掀飞），近侧手臂收在胸前，两腿站稳（岩突：推开）",
               "THE SHOVE - risen, turned to the front-right, the FAR arm thrust out sideways to the image right, palm out "
               "(throwing the enemies), the NEAR arm drawn in before the chest, the legs planted.",
               dict(pelvis=(19.0, 52.0), lift=None, shift=0, spine=176, far_arm=(110, 100, 95),
                    near_arm=(40, 120, 110), near_leg=((13.0, 66.0), 1, 50), far_leg=((26.0, 66.0), -1, 80))),
    "r_call": ("taliyah_spell4@800",
               "唤墙：挺直站着，远侧手臂笔直举向天空、手掌张开（石墙从地里升起），近侧手臂往身侧张开，红垂带往上飘（墙幔：起手）",
               "THE WALL - standing straight, the FAR arm raised straight up to the sky, the palm open (the wall rising "
               "from the ground), the NEAR arm opened out at her side, the red panels flying up.",
               dict(pelvis=(19.0, 52.0), lift=None, shift=0, spine=180, far_arm=(150, 165, 175),
                    near_arm=(-55, -60, -60), near_leg=((14.0, 66.0), 1, 40), far_leg=((24.0, 66.0), -1, 70))),
    "surf1": ("taliyah_run_passive@0",
              "冲浪 1：半蹲在一块大石头上（石头裹着红布，见附图 B），远侧手臂往前（画面右边）伸开，近侧手臂往后下方摆着保持平衡，两只脚踩在石头顶上、膝盖朝前，外套往后飘（移动）",
              "SURF 1 - crouching on her big boulder (wrapped in red cloth, like picture B), the FAR arm reaching forward "
              "to the image right, the NEAR arm swung back and down for balance, both feet on the boulder's top with the knees forward, the coat flying "
              "back.",
              dict(pelvis=(17.0, 60.0), lift=ROCK_H, rock=True, shift=0, spine=160, far_arm=(100, 95, 90),
                   near_arm=(-40, -30, -20), **SURF_LEGS)),
    "surf2": ("taliyah_run_passive@600",
              "冲浪 2：和冲浪 1 一样蹲在石头上，身子再低一点往前压，远侧手臂往前下方，外套和垂带飘得更高（移动）",
              "SURF 2 - as surf 1 on the boulder, lower and leaning further forward, the FAR arm forward and down, the coat "
              "and panels flying higher.",
              dict(pelvis=(17.0, 61.0), lift=ROCK_H, rock=True, shift=0, spine=150, far_arm=(80, 75, 70),
                   near_arm=(-60, -50, -45), **SURF_LEGS)),
    "surf3": ("taliyah_run_passive@1200",
              "冲浪 3：蹲在石头上身子稍微抬起，远侧手臂往右上方张开，近侧手臂往后伸（移动）",
              "SURF 3 - on the boulder, the body a little higher, the FAR arm opened to the upper right, the NEAR arm "
              "stretched back.",
              dict(pelvis=(17.0, 59.0), lift=ROCK_H, rock=True, shift=0, spine=168, far_arm=(120, 115, 110),
                   near_arm=(-80, -85, -90), **SURF_LEGS)),
    # the run on her feet (2026-10-26, the user: 「塔利亚怎么是飞着走路的 不对吧」 - League runs her on foot in a fight
    # and surfs only out of it): one stride of League's Run1 (a 1 s cycle, two steps), leaning forward, both arms
    # thrown out back and down, the coat streaming behind. One foot on the ground in each (the contact frames plant it
    # under her, the passing frames push off it).
    "run1": ("taliyah_run1@250",
             "跑步 1（远侧脚着地）：身子明显往前（画面右边）倾，远侧腿在身子下面踩地、膝盖微弯，近侧腿往后上方踢起、小腿收到身后，"
             "两只手臂往身体两侧后下方张开，红外套和垂带往后飘（用脚跑）",
             "RUN 1 (far foot down) - leaning well forward to the image right, the FAR leg planted under her with the knee a "
             "little bent, the NEAR leg kicked up behind her with the shin folded back, both arms thrown out back and down at "
             "her sides, the red coat and panels streaming behind.",
             dict(pelvis=(19.0, 53.0), lift=None, shift=0, spine=160, far_arm=(70, 60, 55),
                  near_arm=(-50, -40, -35), near_leg=((12.0, 59.0), -1, -100), far_leg=((21.5, 67.0), -1, 85))),
    "run2": ("taliyah_run1@500",
             "跑步 2（交错）：身子往前倾，远侧腿往后蹬地（脚尖还踩着地），近侧腿往前提起、膝盖朝前弯，两只手臂往两侧后方张开，外套往后飘（用脚跑）",
             "RUN 2 (passing) - leaning forward, the FAR leg pushing off behind her (its toes still on the ground), the NEAR "
             "leg swinging forward with the knee raised and bent forward, both arms out back at her sides, the coat "
             "streaming behind.",
             dict(pelvis=(19.0, 52.0), lift=None, shift=0, spine=162, far_arm=(80, 70, 65),
                  near_arm=(-60, -50, -45), near_leg=((21.0, 61.0), -1, 70), far_leg=((15.0, 66.0), -1, 60))),
    "run3": ("taliyah_run1@750",
             "跑步 3（近侧脚着地）：身子明显往前倾，近侧腿在身子下面踩地、膝盖微弯，远侧腿往后上方踢起、小腿收到身后，"
             "两只手臂往身体两侧后下方张开，外套往后飘（用脚跑）",
             "RUN 3 (near foot down) - leaning well forward, the NEAR leg planted under her with the knee a little bent, the "
             "FAR leg kicked up behind her with the shin folded back, both arms thrown out back and down at her sides, the "
             "coat streaming behind.",
             dict(pelvis=(19.0, 53.0), lift=None, shift=0, spine=160, far_arm=(95, 85, 80),
                  near_arm=(-40, -30, -25), near_leg=((18.5, 67.0), -1, 85), far_leg=((16.0, 59.0), -1, -100))),
    "run4": ("taliyah_run1@0",
             "跑步 4（交错）：身子往前倾，近侧腿往后蹬地（脚尖还踩着地），远侧腿往前提起、膝盖朝前弯，两只手臂往两侧后方张开，外套往后飘（用脚跑）",
             "RUN 4 (passing) - leaning forward, the NEAR leg pushing off behind her (its toes still on the ground), the FAR "
             "leg swinging forward with the knee raised and bent forward, both arms out back at her sides, the coat "
             "streaming behind.",
             dict(pelvis=(19.0, 52.0), lift=None, shift=0, spine=162, far_arm=(85, 75, 70),
                  near_arm=(-55, -45, -40), near_leg=((12.0, 66.0), -1, 60), far_leg=((26.0, 61.0), -1, 70))),
    "d_stagger": ("taliyah_death@300",
                  "踉跄：身子往后（画面左边）倒，膝盖弯下去，两只手臂往两边甩开（死亡第一下）",
                  "STAGGER - reeling back to the image left, the knees buckling, both arms flung out to the sides.",
                  dict(pelvis=(20.0, 56.0), lift=None, shift=2, spine=-165, far_arm=(120, 130, 140),
                       near_arm=(-100, -110, -120), near_leg=((14.0, 66.0), 1, 40), far_leg=((25.0, 66.0), -1, 50))),
    "d_down": ("taliyah_death@1000",
               "坐倒：一屁股坐在地上，两腿往前（画面右边）伸，身子往后仰，两只手撑在身后的地上，红垂带摊在地上（死亡）",
               "DOWN - sitting on the ground, both legs stretched forward to the image right, leaning back, both hands "
               "propped on the ground behind her, the red panels spread on the ground.",
               dict(pelvis=(18.0, 67.0), lift=None, shift=4, spine=-165, far_arm=((22.0, 69.0), 1, -60),
                    near_arm=((10.0, 69.0), 1, -60), near_leg=((32.0, 68.0), -1, 90), far_leg=((36.0, 67.0), -1, 90))),
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
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned). The lowest foot on the ground, or `lift` rows over it (the boulder's top in a surf pose)."""
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
    moved = {}
    for k, v in sk.items():
        if k in ("head",):
            moved[k] = (v[0], v[1] + dy)
        elif k in ("neck_shift", "pelvis_shift"):
            moved[k] = (v[0], v[1] + dy)
        else:
            moved[k] = [(x, y + dy) for x, y in v]
    if spec.get("rock"):   # the boulder under her feet: its top where the soles stand, centred under them
        feet = [moved[leg][-2][0] for leg in ("near_leg", "far_leg")]
        moved["rock"] = ((min(feet) + max(feet)) / 2, float(GROUND))
    return moved


def to_canvas(sk, shift=0):
    out = {}
    for k, v in sk.items():
        if k == "head":
            out[k] = (v[0] + DX + shift, v[1] + DY)
        elif k in ("neck_shift", "pelvis_shift"):
            out[k] = v
        elif k == "rock":
            out[k] = (v[0] + DX + shift, v[1] + DY)
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


def skeleton(can, s, label, idle, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    if "rock" in s:   # the boulder: ROCK_W x ROCK_H squares on the ground under her feet
        rx, ry = s["rock"]
        dr.rounded_rectangle([c((rx - ROCK_W / 2, ry - ROCK_H)), c((rx + ROCK_W / 2, ry))], radius=6 * PX,
                             fill=COL["rock"] + (120,), outline=COL["rock"] + (alpha,), width=4)
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
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Taliyah",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900",
           "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work,
           "--frame", frame] + (["--hide-submesh", "TauntRock", "--hide-submesh", "RecallRock"]
                                if "run_passive" in frame else ["--hide-submeshes"])
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
    """Every bone and head box on the canvas; no hand over the face."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1:
        out.append("head off the top")
    fx0, fx1 = hx + FACE[0] - REST["head"][0], hx + FACE[1] - REST["head"][0]
    fy0, fy1 = hy + FACE[2] - REST["head"][1], hy + FACE[3] - REST["head"][1]
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/ta_work/taliyah_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses: with --check the ones checked, else the ones packed")
    ap.add_argument("--prompts", default="POSE_PROMPTS.md", help="the prompt file in assets/source/taliyah/ the pack carries")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(dict(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), far_arm="rest",
                                     near_arm="rest", near_leg="rest", far_leg="rest"))))
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
    packed = [n for n in poses if not a.only or n in a.only.split(",")]
    if any(POSES[n][3].get("rock") for n in packed):   # step 0's B: the boulder she surfs on (surf poses only)
        surf = Image.open(lp(os.path.join(SRC, "codex_picture", "taliyah-picture", "raw", "taliyah-B-raw.png"))).convert("RGBA")
        pic = Image.new("RGBA", surf.size, GREY + (255,))
        pic.alpha_composite(surf)
        pic.convert("RGB").save(os.path.join(out, "2b_surf_picture.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(((n, poses[n]) for n in packed), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})", idle)
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, a.prompts)), os.path.join(out, a.prompts))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

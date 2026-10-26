#!/usr/bin/env python3
"""Locke's pose pack for Codex (assets/source/locke/POSE_PROMPTS.md): the whole-body poses his League clips go through
(the user, 2026-10-26: actions by Codex on skeletons - pack_trundle_poses.py's way).

    python tools/art/pack_locke_poses.py [--out C:/t/lk_work/locke_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (step 0's A-1 at 44 game
px, PPU 2.0: 54 x 88) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames
(tools/lol/pose_ref.py at the 3/4 camera, his skin's own maps: pack_locke_picture.maps): every bone at the design's OWN
length (measured on hd/idle.png at 12x: REST), only its direction set per pose (POSES), the lowest foot on the ground
unless the pose lifts it. The prompt gives the legs' and arms' lengths in squares and asks Codex to count them.
TWO PROPS. His CASE (the black coffin-like binding artifact, CASE_L long, CASE_W wide) is slung on his back in the
design: `back` keeps it there, turned with his spine; `strap` = (centre, direction) puts it in the air on its strap,
a hand holding the strap (the pose's `strap` arm, the free one by default: R swings and throws it); `loose` = (centre, direction) a case no hand holds. Drawn as a
translucent dark box (the direction runs from its top end to its bottom end: 0 = top up, bottom down... as ang()).
His NAIL (a long silver soul nail, NAIL_L squares) sits in the NAIL hand in a reverse grip; `nail` = its direction from
the hand to its point (degrees, ang()'s way); drawn as a light grey line.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head - hair, glasses, face - 8x: every pose wears it); 2_design.png (the design on the grid);
per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), PURPLE = the NAIL arm (the near arm: its hand in front of his body, the nail pointing down), ORANGE = the
FREE arm (the far arm, on the image right by the belt pouches); grey box = the head (never redrawn); dark box = the
case; light grey line = the nail.
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
from design_locke_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_illaoi_poses import ang, along, turned, bend, canvas_grid as _grid, tile_sheet  # noqa: E402
import pack_illaoi_poses as IP  # noqa: E402
import pack_locke_picture as LP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "locke")
PX, CANVAS, SOLE_Y = 11, 1254, 1188
GREY = (225, 225, 225)
GROUND = 88                        # the design's soles' bottom edge (rows)
DX, DY = 30, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 108)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "nail_arm": (150, 60, 200),
       "free_arm": (255, 140, 0)}
HEAD = (0, 25, 19, 46)             # rows / columns of the hair, the glasses and the face in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 27 x 25 squares
FACE = (30, 46, 9, 22)             # the face (glasses, nose, grin): x0, x1, y0, y1 in design squares
CASE_L, CASE_W = 38, 11            # the case: top end to bottom end, width (squares)
NAIL_L = 12                        # the nail in his hand: the grip to the point
CASE_RGB = (40, 30, 45)
NAIL_RGB = (190, 200, 210)

# the design's own skeleton, measured on hd/idle.png (54 x 88, square edges, at 12x): the head box's middle; the spine
# pelvis (the belt buckle) -> the base of the neck (under the high collar); each arm shoulder, elbow, wrist, the
# fingers' tips (the nail hand in front of his belly, the nail pointing down to the image right; the free hand by the
# pouches on the far hip); each leg hip, knee, ankle, toes (he stands loose, the weight on the back foot); the case on
# his back from its top end over his near shoulder to its bottom end at his near hip
REST = {
    "head": (32.5, 12.5),
    "spine": [(33.0, 58.0), (35.0, 26.0)],
    "nail_arm": [(27.0, 30.0), (28.0, 41.0), (31.0, 49.0), (32.0, 53.0)],
    "free_arm": [(45.0, 29.0), (48.0, 38.0), (47.0, 46.0), (47.0, 50.0)],
    "near_leg": [(28.0, 60.0), (27.0, 72.0), (25.0, 82.0), (29.0, 87.0)],
    "far_leg": [(38.0, 60.0), (41.0, 71.0), (41.0, 81.0), (51.0, 86.0)],
    "case": [(13.0, 23.0), (22.0, 60.0)],
    "nail": 150.0,
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest", three angles, or
# (target, side, last angle) - the wrist / ankle at the target with the elbow / knee solved (side -1 bends a downward
# limb's middle joint to the image right, +1 to the image left). "case": "back", ("strap", centre, dir) or ("loose",
# centre, dir); "nail": the nail's direction from the hand (None: no nail in the hand - it flew).
POSES = {
    "a_wind": ("Attack_02_L@166",
               "普攻起手：膝盖弯、身子往前压低，拿钉子的手往后上方收到肩膀旁边（钉尖朝前），另一只手往前伸、五指张开，棺匣背在背上（普攻第一下的蓄力）",
               "WIND-UP - knees bent, the body crouched and leaning forward, the NAIL hand pulled back up by his "
               "shoulder (the nail's point aimed forward), the free hand reaching forward with the fingers spread, the "
               "case on his back.",
               dict(pelvis=(33.0, 62.0), lift=None, shift=0, spine=158, case="back", nail=180.0,
                    nail_arm=(-100, -160, -170), free_arm=(60, 75, 85),
                    near_leg=((22.0, 87.0), 1, 70), far_leg=((46.0, 86.0), -1, 80))),
    "a_stab": ("Attack_01_R@278",
               "普攻捅：弓步往前冲，拿钉子的手往前（画面右边）伸直、钉子往前下方捅出去，另一只手收到身后，棺匣背在背上（普攻捅中）",
               "STAB - lunging forward, the NAIL hand thrust straight out to the image right, the nail stabbing "
               "forward and down, the free arm swept back behind him, the case on his back.",
               dict(pelvis=(33.0, 63.0), lift=None, shift=-6, spine=150, case="back", nail=100.0,
                    nail_arm=(70, 82, 88), free_arm=(-40, -60, -60),
                    near_leg=((18.0, 87.0), 1, 70), far_leg=((50.0, 86.0), -1, 80))),
    "q_raise": ("Spell1_L@100",
                "举钉：身子往后仰，拿钉子的手从头后面往左上方高高举起（三颗钉子握在手里，钉尖朝上，手在头的左后方，不挡脸），另一只手放在胸前，两腿站开（伏魔三钉起手）",
                "RAISE - leaning back, the NAIL hand raised high behind his head to the upper left (three nails in the "
                "fist, points up, the hand beyond the back of his head, never over the face), the free hand at his chest, the feet apart.",
                dict(pelvis=(33.0, 58.0), lift=None, shift=4, spine=-174, case="back", nail=175.0,
                     nail_arm=(-120, -160, 180), free_arm=(-20, -60, -80),
                     near_leg=((25.0, 87.0), 1, 70), far_leg=((44.0, 86.0), -1, 80))),
    "q_throw": ("Spell1_L@275",
                "甩钉：弓步往前，拿钉子的手从头顶往前（画面右边）甩下去、手臂伸直，手张开（钉子飞出去了，手里空），另一只手往后摆（伏魔三钉甩出）",
                "THROW - lunging forward, the NAIL arm whipped down from over his head to the front (the image right), "
                "straight, the hand open (the nails have flown: the hand is empty), the free arm swinging back.",
                dict(pelvis=(33.0, 62.0), lift=None, shift=-4, spine=155, case="back", nail=None,
                     nail_arm=(70, 80, 85), free_arm=(-30, -50, -50),
                     near_leg=((20.0, 87.0), 1, 70), far_leg=((48.0, 86.0), -1, 80))),
    "w_hunch": ("Spell2@60",
                "缩身：膝盖弯、身子往前缩，两只手握着钉子收在胸前（钉尖朝下，像要刺进自己的心口），头低一点（灵焰仪式起手：点燃灵魂）",
                "HUNCH - knees bent, the body hunched forward, BOTH hands gripping the nail at his chest (its point "
                "down, as if driving it into his own heart), the case on his back.",
                dict(pelvis=(33.0, 64.0), lift=None, shift=0, spine=165, case="back", nail=0.0,
                     nail_arm=(50, 140, 150), free_arm=(-10, -120, -140),
                     near_leg=((26.0, 87.0), 1, 60), far_leg=((42.0, 86.0), -1, 70))),
    "w_spread": ("Spell2@265",
                 "展开：身子挺直、往上浮起（脚离地约 3 格），两只手臂向两边张开伸直（近侧手里拿着钉子），下巴抬起（灵焰仪式：灵魂点燃）",
                 "SPREAD - standing tall and rising off the ground (the feet about 3 squares up), BOTH arms spread wide "
                 "out to the sides, straight (the nail in the near hand), the chin up, the case on his back.",
                 dict(pelvis=(33.0, 58.0), lift=3, shift=0, spine=180, case="back", nail=-120.0,
                      nail_arm=(-100, -95, -95), free_arm=(100, 95, 95),
                      near_leg=(5, 0, 60), far_leg=(-5, 0, 80))),
    "e_blink": ("Spell3_Blink@0",
                "闪现落地：低低地蹲着、身子往前探，拿钉子的手往后甩在身后（钉子朝后），另一只手撑在身前（灰猎无影：瞬移出现）",
                "BLINK LANDING - crouched very low, leaning forward, the NAIL arm flung back behind him (the nail "
                "pointing back), the free hand braced in front of him, the case on his back.",
                dict(pelvis=(33.0, 70.0), lift=None, shift=4, spine=140, case="back", nail=-100.0,
                     nail_arm=(-60, -80, -90), free_arm=(30, 10, 0),
                     near_leg=((22.0, 87.0), 1, 80), far_leg=((48.0, 86.0), -1, 85))),
    "e_dash": ("Spell3_Dash@187",
               "冲刺：整个人几乎平着往前（画面右边）飞扑出去（离地约 6 格），拿钉子的手伸在最前面、钉尖朝前，另一只手收在身侧，两腿往后蹬（灰猎无影：冲向目标）",
               "DASH - flying forward almost flat (to the image right, about 6 squares off the ground), the NAIL hand "
               "out in front with the point forward, the free arm tucked at his side, both legs kicked out behind.",
               dict(pelvis=(30.0, 62.0), lift=6, shift=-6, spine=110, case="back", nail=95.0,
                    nail_arm=(70, 85, 90), free_arm=(20, 40, 50),
                    near_leg=(-80, -70, -60), far_leg=(-60, -50, -40))),
    "r_swing": ("Spell4@111",
                "抡棺匣：身子扭向画面左边，近侧那只手（平时拿钉子的手，这时钉子插回腰上）抓住背带往左上方甩，棺匣离开背、飞在头的左上方（不挡脸），另一只手往前伸，两腿站稳（万魔狱起手）",
                "SWING - twisting toward the image left, the NEAR hand (the nail hand; the nail tucked back in his belt) "
                "gripping the case's strap and swinging it up to the upper left, the case off his back in the air over "
                "the upper left of his head (never over the face), the free hand reaching forward, the feet planted.",
                dict(pelvis=(33.0, 59.0), lift=None, shift=14, spine=-170, case=("strap", (0.0, 4.0), -120.0), strap="nail_arm",
                     nail=None, nail_arm=(-110, -150, -160), free_arm=(70, 90, 95),
                     near_leg=((24.0, 87.0), 1, 70), far_leg=((44.0, 86.0), -1, 80))),
    "r_throw": ("Spell4@278",
                "扔棺匣：另一只手（远侧那只）高高甩向前上方（画面右上），背带拉直，棺匣横着飞在他头的右边上方（不挡脸），近侧的手垂在身侧（万魔狱：扔出法器）",
                "THROW - the FREE (far) arm flung high to the upper right, the strap pulled straight, the case flying "
                "crosswise above and to the right of his head (never over the face), the near hand down at his side.",
                dict(pelvis=(33.0, 58.0), lift=None, shift=-10, spine=175, case=("strap", (70.0, 0.0), 90.0),
                     nail=None, nail_arm=(-10, 10, 20), free_arm=(150, 140, 135),
                     near_leg=((24.0, 87.0), 1, 70), far_leg=((44.0, 86.0), -1, 80))),
    "run1": ("Run_Fast@0",
             "跑 1（远侧腿往前迈大步着地，近侧腿往后蹬）：身子往前倾，拿钉子的手往后摆，另一只手往前摆，棺匣背在背上，飘带往后飞",
             "RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg pushing off "
             "behind, the body leaning forward, the nail arm swinging back, the free arm forward, the case on his "
             "back, the coat ribbons flying behind.",
             dict(pelvis=(33.0, 60.0), lift=None, shift=0, spine=165, case="back", nail=170.0,
                  nail_arm=(-30, -10, 0), free_arm=(40, 70, 80),
                  near_leg=((18.0, 85.0), 1, -60), far_leg=((46.0, 86.0), -1, 80))),
    "run2": ("Run_Fast@317",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两只手摆到身边",
             "RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square "
             "higher, both arms passing close to his sides.",
             dict(pelvis=(33.0, 59.0), lift=1, shift=0, spine=167, case="back", nail=170.0,
                  nail_arm=(-10, 10, 10), free_arm=(10, 30, 40),
                  near_leg=((32.0, 87.0), 1, 70), far_leg=((44.0, 76.0), -1, 70))),
    "run3": ("Run_Fast@633",
             "跑 3（近侧腿往前迈大步着地，远侧腿往后蹬）：身子往前倾，拿钉子的手往前摆，另一只手往后摆",
             "RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg pushing off "
             "behind, the body leaning forward, the nail arm swinging forward, the free arm back.",
             dict(pelvis=(33.0, 60.0), lift=None, shift=0, spine=165, case="back", nail=120.0,
                  nail_arm=(40, 70, 80), free_arm=(-30, -10, 0),
                  near_leg=((44.0, 87.0), -1, 80), far_leg=((22.0, 84.0), 1, -60))),
    "run4": ("Run_Fast@950",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两只手摆到身边",
             "RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square "
             "higher, both arms passing close to his sides.",
             dict(pelvis=(33.0, 59.0), lift=1, shift=0, spine=167, case="back", nail=150.0,
                  nail_arm=(10, 30, 40), free_arm=(-10, 10, 10),
                  near_leg=((38.0, 77.0), -1, 70), far_leg=((36.0, 86.0), -1, 80))),
    "d_fall": ("Death@312",
               "被打倒：被打得往后（画面左边）仰倒、膝盖发软，两只手臂往上甩开，钉子从手里飞出去（手里空），棺匣还背在背上（死亡第一下）",
               "KNOCKED BACK - thrown back toward the image left, the knees giving way, both arms flung up, the nail "
               "flying out of his hand (the hand empty), the case still on his back.",
               dict(pelvis=(34.0, 62.0), lift=None, shift=6, spine=-150, case="back", nail=None,
                    nail_arm=(-140, -160, -170), free_arm=(115, 135, 145),
                    near_leg=((26.0, 87.0), 1, 60), far_leg=((44.0, 86.0), -1, 80))),
    # League's death sits him against the case on the ground; the head is pasted upright, so ours sits slumped
    "d_down": ("Death@1562",
               "靠坐在地：一屁股坐在地上，背靠着竖在身后的棺匣，膝盖弯起来，两只手臂软软地搭在膝盖上，头微微垂下，钉子掉在他身前的地上（死亡：倒地）",
               "SITTING SLUMPED - sat down on the ground leaning back against the case standing upright behind him, "
               "the knees drawn up, both arms resting limp on the knees, the head hanging a little, the nail lying on "
               "the ground in front of him.",
               dict(pelvis=(30.0, 82.0), lift=None, shift=4, spine=-178, case=("loose", (16.0, 66.0), 180.0),
                    nail=None, nail_arm=(60, 80, 90), free_arm=(50, 70, 80),
                    near_leg=((42.0, 86.0), -1, 80), far_leg=((48.0, 86.0), -1, 85))),
}


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned); the case on his back turned with the spine, or on its strap from the free hand, or loose.
    The lowest foot or knee on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    for name, base, base_rest, k in (("nail_arm", neck, rs[1], 1.0), ("free_arm", neck, rs[1], 1.0),
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
    case = spec["case"]
    if case == "back":
        sk["case"] = [(neck[0] + o[0], neck[1] + o[1]) for o in
                      (turned((x - rs[1][0], y - rs[1][1]), turn) for x, y in REST["case"])]
    else:
        _, (cx, cy), d = case
        sk["case"] = [along((cx, cy), d + 180.0, CASE_L / 2), along((cx, cy), d, CASE_L / 2)]
    hand = sk["nail_arm"][2]
    sk["nail"] = [] if spec["nail"] is None else [hand, along(hand, spec["nail"], NAIL_L)]
    low = max(y for leg in ("near_leg", "far_leg", "spine") for _, y in sk[leg])
    dy = GROUND - (spec["lift"] or 0) - low
    out = {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}
    if case != "back" and case[0] == "loose":   # a case standing on the ground stays where it was put
        out["case"] = sk["case"]
    out["strap"] = spec.get("strap", "free_arm") if case != "back" and case[0] == "strap" else None
    return out


def to_canvas(sk, shift=0):
    return {k: (v if k == "strap" else (v[0] + DX + shift, v[1] + DY) if k == "head"
                else [(x + DX + shift, y + DY) for x, y in v]) for k, v in sk.items()}


def c(p):
    return (p[0] * PX, p[1] * PX)


def case_shape(dr, top, bot, alpha):
    """The case: a long hexagonal box from its top end to its bottom end, CASE_W wide."""
    d = ang(top, bot)
    nx, ny = turned((1.0, 0.0), d)   # across the case
    hw = CASE_W / 2
    a1, a2 = along(top, d, 3), along(bot, d + 180.0, 3)
    pts = [top, (a1[0] + nx * hw, a1[1] + ny * hw), (a2[0] + nx * hw, a2[1] + ny * hw), bot,
           (a2[0] - nx * hw, a2[1] - ny * hw), (a1[0] - nx * hw, a1[1] - ny * hw)]
    dr.polygon([c(p) for p in pts], fill=CASE_RGB + (90,), outline=(20, 10, 25, alpha))


def skeleton(can, s, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    case_shape(dr, *s["case"], alpha)
    if s["strap"]:   # the strap from the hand holding it to the case's nearer end
        hand = s[s["strap"]][2]
        end = min(s["case"], key=lambda p: math.hypot(p[0] - hand[0], p[1] - hand[1]))
        dr.line([c(hand), c(end)], fill=(60, 40, 60, alpha), width=4)
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("far_leg", "free_arm", "spine", "near_leg", "nail_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == 2 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    if s["nail"]:
        dr.line([c(p) for p in s["nail"]], fill=NAIL_RGB + (alpha,), width=6)
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
    """League's frame, Locke at the 3/4 camera in his own maps."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Locke",
           "--fit-all", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", "900", "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f",
           "--out", work, "--frame", frame, "--mirror"] + LP.LOOK
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
    """Every bone, the head box, the case and the nail on the canvas; no hand, nail or case over the face."""
    out = []
    pts = [p for k in ("spine", "nail_arm", "free_arm", "near_leg", "far_leg", "nail") for p in s[k]]
    bad = [(round(x), round(y)) for x, y in pts if x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6]
    if bad:
        out.append(f"off the canvas / below the ground at {bad[:3]}")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    for x, y in s["case"]:
        if x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6:
            out.append(f"case end off the canvas / below the ground ({x:.0f}, {y:.0f})")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    face = [p for p in s["nail_arm"][2:] + s["free_arm"][2:] + s["nail"] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"hand / nail over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    (x0, y0), (x1, y1) = s["case"]
    for k in range(41):
        x, y = x0 + (x1 - x0) * k / 40, y0 + (y1 - y0) * k / 40
        if fx0 <= x <= fx1 and fy0 <= y <= fy1:
            out.append("case over the face")
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/lk_work/locke_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), case="back",
                                nail=REST["nail"], nail_arm="rest", free_arm="rest", near_leg="rest", far_leg="rest")))
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

#!/usr/bin/env python3
"""Trundle's pose pack for Codex (assets/source/trundle/POSE_PROMPTS.md): the whole-body poses his League clips go
through (the user, 2026-10-25: 「都交给 Codex」 - pack_yorick_poses.py's way).

    python tools/art/pack_trundle_poses.py [--out C:/t/tr_work/trundle_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (step 0's A-1 as drawn, 104
x 85) sits at squares (DX + shift, DY) on it. 9 px squares (Yorick's 11 leave no room: the design is 104 wide and his
club 62 long). The skeletons are set by hand after League's frames (tools/lol/pose_ref.py at the 3/4 camera): every
bone at the design's OWN length (measured on hd/idle.png at 10x: REST), only its direction set per pose (POSES), the
lowest foot on the ground unless the pose lifts it. The prompt gives the legs' and arms' lengths in squares and asks
Codex to count them.
HIS CLUB (Boneshiver, a club of ice as long as his legs and body) is a big prop: in the design it hangs from his raised
hand on the image left, its ice head on the ground. Each pose places it by the point the CLUB hand holds (`grip`, at
`frac` of its length from the handle's end) and its direction (`dir`, the handle -> the head, degrees: 0 the head straight
down, 90 to the image right, 180 up, -90 to the image left); `free` puts the other hand on it too (at that fraction);
`loose` (centre, dir) is a club no hand holds. Drawn on the skeleton as a translucent shaft widening to the ice head.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head - mane, face, beard - 8x: every pose wears it); 2_design.png (the design on the grid); per
pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), PURPLE = the CLUB arm (image left in the design, raised, its hand on the handle), ORANGE = the FREE arm
(image right in the design, its fist by his knee); grey box = the head (the mane, face and beard, never redrawn); light
blue = the club.
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
from design_trundle_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_illaoi_poses import ang, along, turned, bend, canvas_grid as _grid, tile_sheet  # noqa: E402
import pack_illaoi_poses as IP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "trundle")
PX, CANVAS, SOLE_Y = 9, 1254, 1188
GREY = (225, 225, 225)
GROUND = 85                        # the design's soles' bottom edge (rows)
DX, DY = 17, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 132)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "club_arm": (150, 60, 200),
       "free_arm": (255, 140, 0)}
HEAD = (12, 49, 51, 84)            # rows / columns of the mane, the face and the beard in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 33 x 37 squares
FACE = (62, 79, 26, 41)            # the face (brows, eyes, nose, tusks): x0, x1, y0, y1 in design squares
CLUB_L = 62                        # the handle's end to the ice head's tip (hd/idle.png: the hand at row ~23, the tip row 85)
CLUB_HEAD = (32, 28)               # the ice head: length along the club, width (squares)
ICE = (90, 200, 240)

# the design's own skeleton, measured on hd/idle.png (104 x 85, square edges, over the design at 9 px): the head box's
# middle; the spine pelvis (the belt's gem buckle) -> the base of the neck (behind the head: he is hunched, the head
# hangs forward between the high shoulders); each arm shoulder (the big pauldron's middle), elbow, wrist, the fingers'
# tips (the club hand just under its pauldron, gripping the handle; the free fist hanging by the far knee); each leg
# hip, knee (the teal knee guard), ankle, toes
REST = {
    "head": (67.5, 30.5),
    "spine": [(58.0, 58.0), (56.0, 32.0)],
    "club_arm": [(38.0, 20.0), (26.0, 14.0), (20.0, 23.0), (19.0, 27.0)],
    "free_arm": [(88.0, 32.0), (93.0, 42.0), (95.0, 52.0), (96.0, 57.0)],
    "near_leg": [(46.0, 55.0), (40.0, 62.0), (38.0, 76.0), (30.0, 83.0)],
    "far_leg": [(68.0, 56.0), (76.0, 60.0), (81.0, 76.0), (96.0, 83.0)],
    "club": dict(grip=(20.0, 24.0), frac=0.04, dir=-3.0),
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees as above) - each bone at the design's own
# length (REST). A limb is "rest", three angles, (target, side, last angle) - the wrist / ankle at the target with the
# elbow / knee solved (side -1 bends a downward limb's middle joint to the image right, +1 to the image left) - or
# "shaft" (the hand on the club). "club": grip / frac / dir (and free; land=True turns it until its head is on the
# ground), or loose=(centre, dir).
H = "shaft"
POSES = {
    "a_wind": ("trundle_2013_attack1@200",
               "抡棒起手：身子挺起来往后仰，握棒的手把冰棒高高举过头顶、往左后上方甩（冰疙瘩在画面左上方，不挡脸），另一只拳头收在胸前，两腿分开站稳（普攻起手）",
               "WIND-UP - rearing up and leaning back, the CLUB hand swinging the ice club high over his head to the "
               "upper left (the ice head high on the image left, never over the face), the free fist pulled in at his "
               "chest, feet planted wide apart.",
               dict(pelvis=(58.0, 54.0), lift=None, shift=14, spine=-172,
                    club=dict(frac=0.04, dir=-122.0),
                    club_arm=(175, -170, -160), free_arm=(40, 150, 170), near_leg=((40.0, 84.0), 1, -60), far_leg=((80.0, 84.0), -1, 60))),
    "a_smash": ("trundle_2013_attack1@300",
                "砸下：身子往前压、弓步蹲低，握棒的手把冰棒从头顶抡下来，冰疙瘩重重砸在身前（画面右边）的地上，另一只手臂垂在身侧（普攻砸中）",
                "SMASH - pressing forward and down in a deep lunge, the CLUB hand swinging the ice club down from over "
                "his head, the ice head crashing on the ground in front of him (on the image right), the free arm hanging at his side.",
                dict(pelvis=(55.0, 62.0), lift=None, shift=-16, spine=135,
                     club=dict(frac=0.04, dir=70.0, land=True),
                     club_arm=(0, 10, 20), free_arm=(30, 20, 10), near_leg=((30.0, 84.0), 1, -70), far_leg=((82.0, 84.0), -1, 60))),
    "q_rear": ("trundle_2013_bite@200",
               "仰头张嘴：身子往上挺、头往后仰，张开大嘴（准备咬），握棒的手把冰棒垂在身侧（冰疙瘩着地、在画面左边），另一只手臂张开（利齿撕咬起手）",
               "REAR UP - the body straightening up, the head thrown back with the jaws open wide (about to bite), the "
               "club hand letting the club hang at his side (the ice head on the ground on the image left), the free "
               "arm spread out.",
               dict(pelvis=(58.0, 55.0), lift=None, shift=8, spine=-160,
                    club=dict(frac=0.04, dir=-10.0),
                    club_arm=(-30, -10, 0), free_arm=(100, 120, 130), near_leg=((42.0, 84.0), 1, -60), far_leg=((78.0, 84.0), -1, 60))),
    "q_chomp": ("trundle_2013_bite@300",
                "扑咬：整个身子往前扑、压得很低，头往前伸到最前面（画面右边）一口咬下去，握棒的手把冰棒拖在身后（冰疙瘩在画面左下着地），另一只手往前抓（利齿撕咬咬中）",
                "CHOMP - lunging forward low, the head thrust out in front (to the image right) snapping its jaws shut, "
                "the club hand dragging the club behind him (the ice head on the ground on the image left), the free "
                "hand clawing forward.",
                dict(pelvis=(56.0, 62.0), lift=None, shift=-4, spine=118,
                     club=dict(frac=0.04, dir=-70.0),
                     club_arm=(-80, -70, -60), free_arm=(20, 40, 60), near_leg=((32.0, 84.0), 1, -70), far_leg=((78.0, 84.0), -1, 60))),
    "w_crouch": ("trundle_2013_cast_hop@120",
                 "蹲下蓄力：深深蹲下、膝盖弯到底，两只手把冰棒横着抱在身前低处（冰疙瘩在画面左边），头低着往前看（冰封领域起手：要往上跳）",
                 "CROUCH - squatting deep, the knees fully bent, BOTH hands holding the club across in front of him low "
                 "(the ice head on the image left), the head low, looking ahead (about to leap up).",
                 dict(pelvis=(58.0, 68.0), lift=None, shift=8, spine=165,
                      club=dict(frac=0.04, dir=-85.0),
                      club_arm=(30, 20, 10), free_arm=(40, 30, 20), near_leg=((44.0, 84.0), 1, -40), far_leg=((76.0, 84.0), -1, 40))),
    "w_roar": ("trundle_2013_cast_hop@400",
               "跳起怒吼：整个人跳离地面（脚离地约 6 格），身子挺直，另一只拳头高高举起，张嘴吼，握棒的手把冰棒往左后方甩开（冰疙瘩在画面左边）（冰封领域：落下冻住地面）",
               "LEAP AND ROAR - jumped off the ground (the feet about 6 squares up), the body straight, the free fist "
               "thrust high in the air, roaring, the club hand flinging the club out behind him to the left (the ice "
               "head on the image left).",
               dict(pelvis=(58.0, 55.0), lift=6, shift=22, spine=-174,
                    club=dict(frac=0.04, dir=-125.0),
                    club_arm=(-110, -120, -125), free_arm=(150, 165, 175), near_leg=(10, -5, -40), far_leg=(-10, 5, 40))),
    "e_swing": ("trundle_2013_cast_wave@62",
                "挥棒起手：身子扭向画面左边，握棒的手把冰棒横着抡到身前左边（冰疙瘩在画面左边、齐腰高），另一只拳头往前（寒冰之柱起手）",
                "SWING - twisting toward the image left, the CLUB hand swinging the club across in front of him to the "
                "left (the ice head at waist height on the image left), the free fist pushed forward.",
                dict(pelvis=(58.0, 56.0), lift=None, shift=22, spine=-176,
                     club=dict(frac=0.04, dir=-60.0),
                     club_arm=(-70, -90, -95), free_arm=(10, 20, 30), near_leg=((40.0, 84.0), 1, -60), far_leg=((80.0, 84.0), -1, 60))),
    "e_raise": ("trundle_2013_cast_wave@250",
                "高举冰棒：站直了，握棒的手把冰棒高高举起、冰疙瘩朝左上方（不挡脸），另一只拳头往前伸，张嘴吼（寒冰之柱：冰柱冒出来）",
                "RAISE - standing tall, the CLUB hand holding the club up high (the ice head to the upper left, never "
                "over the face), the free fist pushed out forward, roaring.",
                dict(pelvis=(58.0, 54.0), lift=None, shift=8, spine=-178,
                     club=dict(frac=0.04, dir=-125.0),
                     club_arm=(170, 180, -175), free_arm=(30, 60, 80), near_leg=((40.0, 84.0), 1, -60), far_leg=((80.0, 84.0), -1, 60))),
    "r_rise": ("trundle_2013_spell4@150",
               "起身拽：从驼背站起来一半，另一只手往前伸、像要抓住对手，握棒的手把冰棒拖在身侧（冰疙瘩在画面左下着地）（强权至上起手）",
               "RISING GRAB - half straightening up from his hunch, the free hand reaching forward as if to seize the "
               "enemy, the club hand dragging the club at his side (the ice head on the ground on the image left).",
               dict(pelvis=(58.0, 56.0), lift=None, shift=6, spine=-176,
                    club=dict(frac=0.04, dir=-45.0),
                    club_arm=(-40, -30, -20), free_arm=(80, 90, 95), near_leg=((40.0, 84.0), 1, -60), far_leg=((80.0, 84.0), -1, 60))),
    "r_reach": ("trundle_2013_spell4@375",
                "伸手吸取：站得笔直、挺胸，另一只手臂往前（画面右边）伸直、手掌张开（把对手的力量吸过来），握棒的手把冰棒斜拖在身后（冰疙瘩在画面左下着地）（强权至上）",
                "DRAIN - standing up straight, chest out, the free arm stretched out straight to the image right with "
                "the palm open (pulling the enemy's strength in), the club hand dragging the club slanted behind him "
                "(the ice head on the ground on the image left).",
                dict(pelvis=(58.0, 54.0), lift=None, shift=2, spine=180,
                     club=dict(frac=0.04, dir=-40.0),
                     club_arm=(-50, -40, -30), free_arm=(95, 92, 90), near_leg=((42.0, 84.0), 1, -60), far_leg=((76.0, 84.0), -1, 60))),
    "run1": ("trundle_2013_run@0",
             "跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：驼着背往前冲，握棒的手把冰棒扛着往后平拖（冰疙瘩在画面左边、离地），另一只手臂往后摆",
             "RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back, "
             "charging hunched forward, the club hand carrying the club trailing out behind him (the ice head on the "
             "image left, off the ground), the free arm swinging back.",
             dict(pelvis=(58.0, 57.0), lift=None, shift=14, spine=160,
                  club=dict(frac=0.04, dir=-105.0),
                  club_arm=(-90, -100, -100), free_arm=(-20, -10, 0), near_leg=((36.0, 84.0), 1, -70), far_leg=((80.0, 84.0), -1, 60))),
    "run2": ("trundle_2013_run@232",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，冰棒还往后拖着，另一只手臂垂在身边",
             "RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, "
             "the club still trailing behind, the free arm hanging close.",
             dict(pelvis=(58.0, 55.0), lift=1, shift=20, spine=162,
                  club=dict(frac=0.04, dir=-102.0),
                  club_arm=(-85, -95, -100), free_arm=(10, 0, 0), near_leg=((52.0, 84.0), 1, -40), far_leg=((72.0, 72.0), -1, 70))),
    "run3": ("trundle_2013_run@465",
             "跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：驼着背往前冲，冰棒往后拖，另一只手臂往前摆",
             "RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back, "
             "charging hunched forward, the club trailing behind, the free arm swinging forward.",
             dict(pelvis=(58.0, 57.0), lift=None, shift=18, spine=160,
                  club=dict(frac=0.04, dir=-105.0),
                  club_arm=(-90, -100, -100), free_arm=(0, 10, 20), near_leg=((76.0, 84.0), -1, 60), far_leg=((42.0, 84.0), 1, -70))),
    "run4": ("trundle_2013_run@698",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，冰棒往后拖",
             "RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, "
             "the club trailing behind.",
             dict(pelvis=(58.0, 55.0), lift=1, shift=20, spine=162,
                  club=dict(frac=0.04, dir=-102.0),
                  club_arm=(-85, -95, -100), free_arm=(0, 10, 20), near_leg=((64.0, 75.0), -1, 50), far_leg=((62.0, 84.0), -1, 60))),
    "d_fall": ("trundle_2013_death@312",
               "被打倒：被打得往左后方仰倒，膝盖发软，两只手臂往两边甩开，冰棒从手里脱出去往左上方飞（不挡脸）（死亡第一下）",
               "KNOCKED DOWN - thrown back toward the image left, the knees giving way, both arms flung out, the ice "
               "club flying out of his hand to the upper left (never over the face).",
               dict(pelvis=(60.0, 60.0), lift=None, shift=14, spine=-155,
                    club=dict(loose=((20.0, 20.0), -140.0)),
                    club_arm=(-130, -150, -160), free_arm=(110, 130, 140), near_leg=((46.0, 84.0), 1, -50),
                    far_leg=((76.0, 84.0), -1, 60))),
    # League's death lays him flat on his back; the head is pasted upright, so ours slumps down sitting (Kled's d_down)
    "d_down": ("trundle_2013_death@1562",
               "瘫坐在地：一屁股坐倒在地上，身子往前耷拉，头垂下，两只手臂软软垂在地上，两腿往前伸着、膝盖微弯；冰棒平躺在他身边左边的地上（死亡：倒地）",
               "SLUMPED DOWN - sat down hard on the ground, the body sagging forward, the head hanging, both arms limp "
               "on the ground, the legs stretched forward with the knees a little bent; the ice club lying flat on the "
               "ground beside him on the image left.",
               dict(pelvis=(58.0, 78.0), lift=None, shift=2, spine=170,
                    club=dict(loose=((14.0, 80.0), -90.0)),
                    club_arm=(-10, 0, 10), free_arm=(10, 0, -10), near_leg=(80, 70, 60), far_leg=(100, 90, 80))),
}


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def ends(sh):
    """The club's point and spade tips from its spec."""
    if "loose" in sh:
        (cx, cy), d = sh["loose"]
        return along((cx, cy), d + 180.0, CLUB_L / 2), along((cx, cy), d, CLUB_L / 2)
    g, f, d = sh["grip"], sh["frac"], sh["dir"]
    return along(g, d + 180.0, f * CLUB_L), along(g, d, (1 - f) * CLUB_L)


def build(spec):
    """build_raw with the club read on the finished skeleton (after the drop onto the ground): the legs and the spine
    alone set the drop, so a first pass finds it and the second places the club there. A club with no `grip` hangs from
    the CLUB hand of an arm set by angles (Trundle's chibi arm reaches 15 squares: the hand sets the grip, not the other
    way round)."""
    sh = dict(spec["club"])
    if "loose" in sh:
        return build_raw(spec)
    first = build_raw(dict(spec, club=dict(sh, grip=sh.get("grip", (0.0, 0.0)))))
    dy = first["spine"][0][1] - spec["pelvis"][1]
    if "grip" not in sh:
        w = first["club_arm"][2]
        sh["grip"] = (w[0], w[1] - dy)
    else:
        sh["grip"] = (sh["grip"][0], sh["grip"][1] - dy)
    # the ice head rests on the ground, never in it: a club pointing down is turned up until its tip is on the ground
    gy = sh["grip"][1] + dy
    reach = (1 - sh["frac"]) * CLUB_L
    if sh.get("land") or gy + reach * math.cos(math.radians(sh["dir"])) > GROUND:   # `land`: the head on the ground
        k = max(-1.0, min(1.0, (GROUND - gy) / reach))
        sh["dir"] = math.copysign(math.degrees(math.acos(k)), sh["dir"] or 1.0)
    return build_raw(dict(spec, club=sh))


def build_raw(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned); the hands on the shaft. The lowest foot or knee on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    sh = spec["club"]
    top, bot = ends(sh)
    on_shaft = lambda f: (top[0] + (bot[0] - top[0]) * f, top[1] + (bot[1] - top[1]) * f)
    main = sh.get("main", "club")
    reach = {}
    # the big pauldrons sit far out from his spine: they turn half as much as it does (whole, a forward lean flung the
    # club shoulder over his head)
    for name, base, base_rest, k in (("club_arm", neck, rs[1], 0.5), ("free_arm", neck, rs[1], 0.5),
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
            target = on_shaft(f)
            side = spec.get("sides", {}).get(name, 1 if name == "club_arm" else -1)
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
    sk["club"] = [top, bot]
    low = max(y for leg in ("near_leg", "far_leg", "spine") for _, y in sk[leg])
    dy = GROUND - (spec["lift"] or 0) - low
    out = {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}
    if "loose" in sh:   # a dropped club stays where it was put (on the ground: not lifted with him)
        out["club"] = [top, bot]
    out["reach"] = reach
    out["behind"] = bool(sh.get("behind"))
    return out


def to_canvas(sk, shift=0):
    return {k: (v if k in ("reach", "behind") else (v[0] + DX + shift, v[1] + DY) if k == "head"
                else [(x + DX + shift, y + DY) for x, y in v]) for k, v in sk.items()}


def c(p):
    return (p[0] * PX, p[1] * PX)


def club_shape(dr, top, bot, alpha):
    """The handle at the top end (a shaft of ice chunks, widening) and the ice head (a faceted block CLUB_HEAD long and
    wide) at the bottom end."""
    d = ang(top, bot)
    nx, ny = turned((1.0, 0.0), d)   # across the club
    hl, hw = CLUB_HEAD
    neck = along(bot, d + 180.0, hl)
    dr.polygon([c(p) for p in (
        (top[0] + nx * 1.5, top[1] + ny * 1.5), (neck[0] + nx * hw / 4, neck[1] + ny * hw / 4),
        (neck[0] - nx * hw / 4, neck[1] - ny * hw / 4), (top[0] - nx * 1.5, top[1] - ny * 1.5))],
        fill=ICE + (70,), outline=(40, 120, 170, alpha))
    m1 = along(bot, d + 180.0, hl * 0.75)
    m2 = along(bot, d + 180.0, hl * 0.3)
    dr.polygon([c(p) for p in (
        (neck[0] + nx * hw / 4, neck[1] + ny * hw / 4), (m1[0] + nx * hw / 2, m1[1] + ny * hw / 2),
        (m2[0] + nx * hw / 2, m2[1] + ny * hw / 2), bot, (m2[0] - nx * hw / 2, m2[1] - ny * hw / 2),
        (m1[0] - nx * hw / 2, m1[1] - ny * hw / 2), (neck[0] - nx * hw / 4, neck[1] - ny * hw / 4))],
        fill=ICE + (110,), outline=(40, 120, 170, alpha))


def skeleton(can, s, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("far_leg", "club_arm", "spine", "near_leg"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == 2 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    club_shape(dr, *s["club"], alpha)
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
    """League's frame, Trundle at the 3/4 camera."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Trundle",
           "--fit-all", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
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
    """Every bone, the head box and the club on the canvas; no hand and no club over the face; hands on the shaft."""
    out = []
    pts = [p for k in ("spine", "club_arm", "free_arm", "near_leg", "far_leg") for p in s[k]]
    bad = [(round(x), round(y)) for x, y in pts if x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6]
    if bad:
        out.append(f"off the canvas / below the ground at {bad[:3]}")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    for x, y in s["club"]:
        if x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6:
            out.append(f"club end off the canvas / below the ground ({x:.0f}, {y:.0f})")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    face = [p for p in s["club_arm"][2:] + s["free_arm"][2:] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"hand over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    (x0, y0), (x1, y1) = s["club"]
    for k in ([] if s.get("behind") else range(41)):
        x, y = x0 + (x1 - x0) * k / 40, y0 + (y1 - y0) * k / 40
        if fx0 <= x <= fx1 and fy0 <= y <= fy1:
            out.append("club over the face")
            break
    for arm, gap in s.get("reach", {}).items():
        if gap > 1.0:
            out.append(f"{arm} {gap:.1f} squares short of the shaft")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/tr_work/trundle_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), club=REST["club"],
                                club_arm="rest", free_arm="rest", near_leg="rest", far_leg="rest")))
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

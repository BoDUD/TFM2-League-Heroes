#!/usr/bin/env python3
"""Zac's pose pack for Codex (assets/source/zac/POSE_PROMPTS.md): the whole-body poses his League clips go through (the
user, 2026-10-23: 「不行你做不出的地方让codex帮忙 做的太奇怪了」, then 「不用参照oppi 参照英雄联盟」; pack_nunu_poses.py's way).

    python tools/art/pack_zac_poses.py [--out C:/t/za_work/zac_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-1 cut to
66 rows, 87 x 66) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames
(tools/lol/pose_ref.py at the 3/4 camera, --hide-submeshes: the skin hides a puddle and a bloblet): every bone at the
design's OWN length (measured on hd/idle.png at 12x: REST) - times the pose's `k` for an arm League stretches like
rubber (Stretching Strikes, Elastic Slingshot) - only its direction set per pose (POSES), the lowest foot on the ground
unless the pose lifts it. The prompt gives the legs' and arms' lengths in squares and asks Codex to count them.
THE HEAD BOX is the head with the tendril (hd/idle.png rows 0-41, columns 46-69): pasted, moved with the neck, never
turned (one face in all frames). Where League squashes or melts him (r_splat, d_melt, d_puddle) no skeleton can say it -
turned that far the shoulders, far off his spine, fly up - so those poses get a BOX instead (spec "box": the squares his
whole body fills, its bottom on the ground) and the pose line says what goes in it.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head box 8x: every pose wears it); 2_design.png (the design on the grid); per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the head), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left in the design), PURPLE = the FAR arm (image right); grey box = the head
box.
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
from design_zac_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zac")
PX, CANVAS, SOLE_Y = 9, 1254, 1197
GREY = (225, 225, 225)
GROUND = 66                        # the design's soles' bottom edge (rows)
DX, DY = 26, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 133)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200)}
HEAD = (0, 42, 46, 70)             # rows / columns of the head box in hd/idle.png: the tendril, the head, the grin
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # 24 x 42 squares
FACES = [(52, 69, 21, 39)]         # his face (the eyes to the grin): x0, x1, y0, y1
BALL = (235, 245, 255)

# the design's own skeleton, measured on hd/idle.png (87 x 66, square edges): the head box's middle; the spine pelvis ->
# the base of the head; each arm shoulder, elbow, wrist, the fingers' tips; each leg hip, knee, ankle, toes
REST = {
    "head": (58.0, 21.0),
    "spine": [(44.0, 46.0), (55.0, 18.0)],
    "near_arm": [(24.0, 22.0), (11.0, 36.0), (10.0, 50.0), (12.0, 63.0)],
    "far_arm": [(70.0, 17.0), (77.0, 32.0), (78.0, 46.0), (80.0, 57.0)],
    "near_leg": [(34.0, 46.0), (31.0, 55.0), (30.0, 61.0), (24.0, 65.0)],
    "far_leg": [(53.0, 46.0), (58.0, 55.0), (62.0, 61.0), (72.0, 65.0)],
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), "k" (an arm's bones times k: stretched like rubber), the spine's direction and every
# limb (degrees: 0 straight down, 90 to the image right, 180 up, -90 to the image left) - each bone at the design's own
# length (REST). A limb is "rest" (the design's own, turned with the spine), three angles, or (target, side, last
# angle): the wrist / ankle at the target with the elbow / knee solved at the design's lengths (side -1 bends a
# downward limb's middle joint to the image right, +1 to the image left), then the hand / foot at the last angle.
POSES = {
    "a_wind": ("zac_attack1@196",
               "抡臂：身子扭着往后仰，近侧（画面左边）的手臂往后平甩到肩膀高度、拳头往下垂，远侧手臂垂在身前，弓步：近侧腿往后蹬直、远侧腿在前弯着（普攻起手）",
               "WIND-UP - his body twisted back, the NEAR arm (image left) swung back level with the shoulder, its fist hanging "
               "down, the FAR arm hanging in front of him; a lunge: the near leg pushed back straight, the far leg bent in "
               "front.",
               dict(pelvis=(44.0, 46.0), lift=None, shift=4, spine=166, near_arm=(-100, -95, -15), far_arm=(30, 5, 10),
                    near_leg=((22.0, 66.0), 1, -60), far_leg=((62.0, 66.0), -1, 60))),
    "a_punch": ("zac_attack1@392",
                "出拳：身子往前（画面右边）压低扑出去，远侧的手臂像橡皮一样**伸长一点**往前平平打出去（拳头在最前面，和肩膀一样高），"
                "近侧手臂甩到身后，弓步：近侧腿往后蹬直、远侧腿往前弯（普攻打中）",
                "PUNCH - lunging forward and low to the image right, the FAR arm STRETCHING a little like rubber and punching "
                "straight forward (the fist out in front at shoulder height), the near arm swung behind him; a lunge: the near "
                "leg pushed back straight, the far leg bent forward.",
                dict(pelvis=(44.0, 47.0), lift=None, shift=-14, spine=142, k={"far_arm": 1.15}, far_arm=(88, 90, 90),
                     near_arm=(-35, -20, -10), near_leg=((18.0, 66.0), 1, -80), far_leg=((66.0, 66.0), -1, 60))),
    "q_wind": ("zac_spell1_max@163",
               "甩手蓄力：身子挺高往后仰，近侧（画面左边）的手臂**拉长三成**高高甩到头顶后上方，远侧手臂垂在身前，两腿站稳（延伸打击：起手）",
               "WIND-UP - standing tall and leaning back, his NEAR arm (image left) STRETCHED a third longer and swung high up "
               "and back over his head, the far arm hanging in front, the legs planted.",
               dict(pelvis=(44.0, 45.0), lift=None, shift=4, spine=172, k={"near_arm": 1.3}, near_arm=(-160, -170, -178),
                    far_arm="rest", near_leg=((29.0, 66.0), 1, -50), far_leg=((61.0, 66.0), -1, 55))),
    "q_reach": ("zac_spell1_max@488",
                "长臂抓出：身子压低前倾，远侧手臂像橡皮一样**拉长三成**，贴着地面往前（画面右边）伸出去，张开的大手在最前面抓东西；"
                "近侧手臂垂在身后，两腿弯着（延伸打击：伸手）",
                "THE LONG GRAB - crouched low and leaning forward, his FAR arm STRETCHED a third longer like rubber, reaching "
                "forward low along the ground to the image right, the big open hand at its end grabbing; the near arm hanging "
                "behind him, the legs bent.",
                dict(pelvis=(42.0, 50.0), lift=None, shift=-22, spine=140, k={"far_arm": 1.3}, far_arm=(100, 95, 92),
                     near_arm=(-25, -15, -5), near_leg=((22.0, 66.0), 1, -70), far_leg=((60.0, 66.0), -1, 65))),
    "q_lift": ("zac_spell1_slam@250",
               "举起：挺直站高，**两只手臂一起高高举过头顶**（像举着一个人准备往下砸），两腿大大分开站稳（延伸打击：甩人）",
               "LIFTING - standing up tall, BOTH ARMS RAISED HIGH above his head together (as if holding someone up to slam "
               "him down), the legs planted wide apart.",
               dict(pelvis=(44.0, 45.0), lift=None, shift=0, spine=178, near_arm=(175, 178, 180), far_arm=(-175, -178, 180),
                    near_leg=((24.0, 66.0), 1, -60), far_leg=((64.0, 66.0), -1, 60))),
    "q_slam": ("zac_spell1_slam@500",
               "砸地：深深蹲成大马步，身子往前弓，**两只大拳头一起砸在身前两边的地上**（延伸打击：砸中）",
               "SLAM - squatting deep in a wide stance, hunched forward, BOTH BIG FISTS smashing the ground in front of him on "
               "either side.",
               dict(pelvis=(44.0, 53.0), lift=None, shift=0, spine=140, near_arm=((38.0, 66.0), -1, 0),
                    far_arm=((78.0, 66.0), -1, 0), near_leg=((24.0, 66.0), 1, -75), far_leg=((64.0, 66.0), -1, 75))),
    "e_plant": ("zac_spell3_windup@563",
                "按地：弯腰往前，**两只手臂一起往前伸到地上按住**（两只大手撑在身前的地上，手臂比平时长一点），近侧腿往后撤一步、两腿弯着（橡筋弹弓：起手）",
                "PLANTING THE ARMS - bending forward, BOTH ARMS reaching forward to the ground and pressing on it (both big "
                "hands flat on the ground in front of him, the arms a little longer than usual), the near leg stepped back, "
                "the legs bent.",
                dict(pelvis=(40.0, 49.0), lift=None, shift=-4, spine=125, k={"near_arm": 1.15, "far_arm": 1.15},
                     near_arm=((48.0, 66.0), -1, 90), far_arm=((88.0, 66.0), -1, 90),
                     near_leg=((22.0, 66.0), 1, -70), far_leg=((58.0, 66.0), -1, 50))),
    "e_pull": ("zac_spell3_windup@1688",
               "拉弹弓：身子使劲往后（画面左边）拉、弓着背，两只手还按在前面的地上，**两只手臂被拉得很长**（比平时长一半，像拉开的橡皮筋），两腿弯着蓄力（橡筋弹弓：蓄力）",
               "PULLING THE SLINGSHOT - his body pulled far back to the image left, hunched, both hands still planted on the "
               "ground in front, BOTH ARMS STRETCHED LONG between them (half as long again, like a drawn rubber band), the "
               "legs bent, ready to spring.",
               dict(pelvis=(30.0, 48.0), lift=None, shift=-6, spine=150, k={"near_arm": 1.5, "far_arm": 1.5},
                    near_arm=((70.0, 66.0), -1, 90), far_arm=((96.0, 66.0), -1, 90),
                    near_leg=((14.0, 66.0), 1, -75), far_leg=((42.0, 66.0), -1, 50))),
    "e_fly": ("zac_spell3_flying@217",
              "飞出去：整个人**横着飞在空中**（身子朝画面右边伸直、比平时拉长一点），两只手臂往前伸，两条腿往后拖，头照样朝右前方（橡筋弹弓：飞行）",
              "FLYING - his whole body FLYING THROUGH THE AIR stretched out toward the image right (a little longer than "
              "usual), both arms reaching forward, both legs trailing behind, the head facing the front-right as always.",
              dict(pelvis=(40.0, 40.0), lift=16, shift=-12, spine=105, near_arm=(95, 90, 85), far_arm=(80, 85, 90),
                   near_leg=(-100, -95, -90), far_leg=(-80, -90, -95))),
    "e_land": ("zac_spell3_back@1000",
               "落地：重重落下蹲成大马步，**两只手臂往两边张开**（肩膀高、手掌张开），两腿大大分开（橡筋弹弓：落地）",
               "LANDING - crashing down into a deep wide crouch, BOTH ARMS FLUNG OUT to the sides (at shoulder height, the "
               "hands open), the legs wide apart.",
               dict(pelvis=(44.0, 54.0), lift=None, shift=0, spine=165, near_arm=(-95, -125, -160),
                    far_arm=(95, 125, 160), near_leg=((22.0, 66.0), 1, -80), far_leg=((66.0, 66.0), -1, 80))),
    "r_crouch": ("zac_revert_spell4@0",
                 "下蹲蓄力：身子缩起来深深蹲下、背弓着，两只手臂垂到脚边的地上，准备往上弹（动感弹球：起跳前）",
                 "CROUCH - curling down into a deep squat, hunched, both arms hanging down to the ground by his feet, ready to "
                 "bounce up.",
                 dict(pelvis=(44.0, 55.0), lift=None, shift=0, spine=145, near_arm=((34.0, 66.0), 1, 0),
                      far_arm=((72.0, 66.0), -1, 0), near_leg=((28.0, 66.0), 1, -60), far_leg=((60.0, 66.0), -1, 60))),
    "r_jump": ("zac_spell4_snapcastrun@363",
               "跳在空中：整个人在空中（脚离地），**两只手臂往两边张开**、手垂着，两条腿弯着悬在身下（动感弹球：弹起）",
               "IN THE AIR - his whole body up in the air (the feet off the ground), BOTH ARMS SPREAD OUT to the sides with the "
               "hands hanging, both legs bent, dangling under him.",
               dict(pelvis=(44.0, 46.0), lift=16, shift=2, spine=178, near_arm=(-110, -95, -20), far_arm=(110, 95, 20),
                    near_leg=(-20, 30, -60), far_leg=(30, 10, 70))),
    "r_ball": ("zac_revert_spell4@363",
               "团成球：在空中把自己**缩成一个圆球**——两膝抱到胸前，两只手臂抱住小腿，脸照样朝右前方露在最上面（动感弹球：最高点）",
               "BALLED UP - high in the air, CURLED INTO A ROUND BALL: both knees pulled up to his chest, both arms wrapped round "
               "the shins, the face still showing on top to the front-right.",
               dict(pelvis=(44.0, 44.0), lift=20, shift=0, spine=178, near_arm=(30, 80, 100), far_arm=(20, 60, 90),
                    near_leg=(150, 20, 100), far_leg=(140, 15, 95))),
    "r_splat": ("zac_spell4_3@875",
                "压扁落地：砸在地上**整个身子被压扁**——又矮又宽（高度只有平时一半多，宽度宽两成），手臂和腿往四周摊开贴着地，"
                "头也被压低但两只眼睛和咧开的嘴照样露在上面（动感弹球：落地）",
                "SPLAT - landing with his WHOLE BODY SQUASHED: short and wide (a little over half his usual height, a fifth "
                "wider), the arms and legs sprawled out flat on the ground, the head pressed down low with both eyes and the "
                "grin still showing on top.",
                dict(box=(-6.0, 28.0, 93.0, 66.0), shift=0, cam_ground=0.55)),
    "d_stagger": ("zac_death2@1125",
                  "摇晃：身子直起来摇摇晃晃，远侧手臂往前伸着、手掌张开像要抓什么，近侧手臂往前下方垂着，腿开始发软（死亡第一下）",
                  "STAGGERING - standing up swaying, the far arm reaching forward with the hand open as if clutching at "
                  "something, the near arm hanging forward and down, the legs starting to give way.",
                  dict(pelvis=(44.0, 46.0), lift=None, shift=0, spine=175, near_arm=(25, 15, 5), far_arm=(75, 85, 95),
                       near_leg=((32.0, 66.0), 1, -40), far_leg=((58.0, 66.0), -1, 40))),
    "d_melt": ("zac_death2@2813",
               "融化：身子**软塌下去开始融化**，变成一大团往下淌的黏液，腿弯折陷进去，手臂软软地垂到地上，头往前耷拉（眼睛半闭）（死亡）",
               "MELTING - his body SAGGING AND MELTING into a big heap of dripping slime, the legs buckled and sinking into it, "
               "the arms hanging limp to the ground, the head drooping forward (the eyes half closed).",
               dict(box=(4.0, 24.0, 86.0, 66.0), shift=0)),
    "d_puddle": ("zac_death2@3375",
                 "化成一滩：完全化成**地上扁扁的一大滩绿色黏液**（只有十几格高），触须软软地倒在上面，两只眼睛闭着（画成一道线）露在黏液上（死亡）",
                 "A PUDDLE - fully melted into a FLAT POOL OF GREEN SLIME on the ground (only a dozen squares tall), the tendril "
                 "lying limp on it, his two eyes closed (drawn as lines) showing on the puddle.",
                 dict(box=(-8.0, 52.0, 96.0, 66.0), shift=0)),
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


def lengths(name, k=1.0):
    pts = REST[name]
    return [k * math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


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
    """build_raw (pack_nunu_poses.build: `ball_at` read on the finished skeleton - no prop for Zac)."""
    if "ball_at" not in spec:
        return build_raw(spec)
    first = build_raw(spec)
    dy = first["spine"][0][1] - spec["pelvis"][1]
    bx, by = spec["ball_at"]
    return build_raw(dict(spec, ball_at=(bx, by - dy)))


def build_raw(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (pasted, never
    turned). The lowest foot, knee or hand on the ground, or `lift` rows over it."""
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
        ls = lengths(name, spec.get("k", {}).get(name, 1.0))
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
    a bigger dot on each hand."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    if "box" in s:                               # a squashed / melted pose: his whole body inside the box
        x0, y0, x1, y1 = s["box"]
        dr.rectangle([x0 * PX, y0 * PX, x1 * PX, y1 * PX], fill=(0, 170, 60, 60), outline=(0, 120, 40, alpha), width=5)
        dr.text((12, 12), label, fill=(30, 30, 30, 255))
        can.alpha_composite(lay)
        return can
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


def lol_frame(lol, frame, work, yaw=35, ground=0.92):
    """League's frame (Zac at the 3/4 camera, the skin's hidden puddle and bloblet left out)."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Zac",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", "1100", "--fit", "0.22", "--ground", str(ground), "--width", "2.6", "--yaw", str(yaw), "--name", "f",
           "--out", work, "--frame", frame, "--hide-submeshes"]
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


def boxed(spec):
    """A box pose on the canvas grid: {"box": (x0, y0, x1, y1)} in canvas squares, its bottom on the ground."""
    x0, y0, x1, y1 = spec["box"]
    sh = spec.get("shift", 0)
    return {"box": (x0 + DX + sh, y0 + DY, x1 + DX + sh, y1 + DY)}


def poses_built():
    return {name: (boxed(spec) if "box" in spec else to_canvas(build(spec), spec.get("shift", 0)), frame, zh, en)
            for name, (frame, zh, en, spec) in POSES.items()}


def problems(name, s):
    """Every bone and the head box on the canvas; no hand over the face."""
    out = []
    if "box" in s:
        x0, y0, x1, y1 = s["box"]
        if x0 < 1 or x1 > CANVAS / PX - 1 or y0 < 1 or y1 > SOLE_Y / PX + 0.6:
            out.append("box off the canvas")
        return out
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
    ap.add_argument("--out", default="C:/t/za_work/zac_pose_pack")
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
            if "head" in s:                          # the design's head box, to judge the proportions
                hx, hy = s["head"]
                can.alpha_composite(Image.fromarray(up(idle[r0:r1, c0:c1], PX)),
                                    (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
            skeleton(can, s, name)
            fpath = os.path.join(cache, name + ".png")
            if not os.path.isfile(fpath):
                lol_frame(a.lol, frame, os.path.join(a.check, "_work"),
                          ground=POSES[name][3].get("cam_ground", 0.92)).save(fpath)
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
        lol_frame(a.lol, frame, out + "_work", ground=POSES[name][3].get("cam_ground", 0.92)).save(
            os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()

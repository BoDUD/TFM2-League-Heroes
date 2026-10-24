#!/usr/bin/env python3
"""Singed's pose pack for Codex (assets/source/singed/POSE_PROMPTS.md): the whole-body poses his League clips go through,
the big shield plate on his near arm swung somewhere else in each (pack_aurora_poses.py's way: her wand is his plate).

    python tools/art/pack_singed_poses.py [--out C:/t/si_work/singed_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-2 as drawn,
45 x 62, PPU 1.39) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames
(tools/lol/pose_ref.py at the 3/4 camera; League turns his back in the run, the attack's end and R - ours keep the face to
the front-right): every bone at the design's OWN length (measured on hd/idle.png at 16x: REST), only its direction set per
pose (POSES), the lowest foot on the ground unless the pose lifts it. No run here: League's run shows his back (the plate
over him), so the walk is rigged from the design (rig_singed.py, league_zac's way).
THE HEAD (hd/idle.png rows 13-24, columns 21-32: the bald head, the eyes, the mask) is pasted on every pose upright,
never turned. THE TANK on his back (the green tank and its cap above and behind the head) is rigid: the design's own tank
squares (tank_mask) moved with the neck, never turned - drawn translucent on the skeletons.
THE SHIELD PLATE is a rigid prop on his near arm: in the design a tall plate PLATE_L squares from its bottom end to its top
end on its middle line, PLATE_W wide, held GRIP of the way up (the near hand, behind it). A pose gives where the hand holds
it ("at") and its direction (deg, bottom -> top); the holding arm's wrist goes to the grip. A dropped plate (hand None)
lies where "at" puts its grip.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png; 1_head.png (8x); 2_design.png; per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left, holding the plate), PURPLE = the FAR arm (image right, the flask hand),
the wide YELLOW band = the shield plate, its CYAN end = the plate's top (the spiked end), a dark ring = where the hand grips
it; grey box = the head; the translucent green shape = the tank.
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
from design_singed_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "singed")
PX, CANVAS, SOLE_Y = 12, 1254, 1188
GREY = (225, 225, 225)
GROUND = 62                        # the design's soles' bottom edge (rows)
DX, DY = 34, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 99)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "shaft": (235, 200, 0), "point": (0, 200, 220)}
HEAD = (13, 25, 21, 33)            # rows / columns of the head in hd/idle.png (ends exclusive): scalp to the mask
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 12 x 12 squares
FACE = (23, 32, 17, 25)            # the face (the eyes, the mask): x0, x1, y0, y1 in design squares
PLATE_L, PLATE_W = 46.0, 8.0       # the plate's middle line (9, 56) -> (11, 10) in the design, about 8 squares wide
GRIP, TIP0 = 0.35, 0.85            # the hand a third of the way up; the top 15% (the spiked end) marked
REST_PLATE = dict(at=(9.7, 40.0), deg=177.5, hand="near_arm", behind=True)


def tank_mask(d):
    """The tank in hd/idle.png: the squares above the head's top and right of the plate (rows < 16, columns 17-35), the
    green glass, its rivets and its cap - everything there but the head's own scalp."""
    h, w = d.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    c = d[..., :3].astype(int)
    skin = (c[..., 0] > 190) & (c[..., 0] - c[..., 2] > 40) & (c[..., 1] > 110)
    return (yy < 16) & (xx >= 17) & (xx <= 35) & (d[..., 3] > 0) & ~skin


# the design's own skeleton, measured on hd/idle.png (45 x 62, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (the near hand behind the plate, the far hand
# round the flask); each leg hip, knee, ankle, toes
REST = {
    "head": (27.0, 19.0),
    "spine": [(24.0, 41.0), (26.0, 24.0)],
    "near_arm": [(19.0, 22.0), (16.0, 31.0), (16.0, 39.0), (16.0, 44.0)],
    "far_arm": [(33.0, 22.0), (35.0, 30.0), (38.0, 36.0), (40.0, 41.0)],
    "near_leg": [(21.0, 42.0), (19.0, 50.0), (16.0, 56.0), (19.0, 61.0)],
    "far_leg": [(28.0, 42.0), (31.0, 50.0), (32.0, 56.0), (40.0, 61.0)],
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest", three angles, or
# (target, side, last angle): the wrist / ankle at the target with the elbow / knee solved (side -1 bends a downward
# limb's middle joint to the image right, +1 to the image left), then the hand / foot at the last angle; target "grip" =
# the plate's grip. The plate: "at" where the near hand holds it, "deg" its direction from the bottom to the top (the
# spiked end), "hand" the arm holding it (None: lying on the ground).
SIDE = dict(at=(13.0, 40.0), deg=178.0, hand="near_arm")   # hanging at his near side, as in the design
POSES = {
    "a_wind": ("singed_attack1@200",
               "抡盾：身子往后（画面左边）仰，近侧手臂把盾板高高举起竖在头的左边（尖刺那头朝上、高过头顶，不挡脸），远侧手拿着药瓶往前伸，弓步（普攻起手）",
               "WIND-UP - leaning back to the image left, the NEAR arm lifting the shield plate high over his head to the "
               "upper left (the plate raised up beside the head on the image left, its spiked end high above, never over the face), the far "
               "hand with the flask reaching forward; a lunge.",
               dict(pelvis=(24.0, 41.0), lift=None, shift=2, spine=-172, near_arm=("grip", 1, -170),
                    far_arm=(70, 80, 90), near_leg=((14.0, 57.0), 1, 60), far_leg=((34.0, 57.0), -1, 80),
                    plate=dict(at=(11.0, 18.0), deg=-165, hand="near_arm"))),
    "a_smash": ("singed_attack1@500",
                "砸下：身子往前（画面右边）扑、压低，近侧手臂把盾板从上往下砸到身前右下方（盾板斜着横在身前，尖刺那头朝右下），远侧手臂甩到身后，弓步：远侧腿在前弯着（普攻打中）",
                "SMASH - lunging forward and low to the image right, the NEAR arm bringing the shield plate down in front of "
                "him to the lower right (the plate slanted, its spiked end to the lower right), the far arm swung back; a "
                "lunge with the far leg bent in front.",
                dict(pelvis=(24.0, 44.0), lift=None, shift=-6, spine=150, near_arm=("grip", -1, 100),
                     far_arm=(-40, -20, -10), near_leg=((12.0, 57.0), 1, -70), far_leg=((36.0, 57.0), -1, 70),
                     plate=dict(at=(34.0, 36.0), deg=70, hand="near_arm"))),
    "e_grab": ("singed_spell3@300",
               "抓人：身子前倾，远侧手臂往前（画面右边）伸到胸口高度、手张开抓住敌人，近侧手臂把盾板往后收在身体左边，两腿弯着（过肩摔：抓住）",
               "THE GRAB - leaning forward, the FAR arm reaching forward to the image right at chest height, the hand open "
               "grabbing, the NEAR arm pulling the shield plate back at his left side, the legs bent.",
               dict(pelvis=(24.0, 42.0), lift=None, shift=-4, spine=160, far_arm=(100, 95, 90),
                    near_arm=("grip", 1, -20), near_leg=((15.0, 57.0), 1, -60), far_leg=((33.0, 57.0), -1, 70),
                    plate=dict(at=(16.0, 36.0), deg=-170, hand="near_arm"))),
    "e_heave": ("singed_spell3@600",
                "举过肩：身子使劲往后（画面左边）仰，两只手臂一起高高举到头顶左后方（像把一个人从肩膀上扔到身后），盾板跟着举到头的左上方斜着（尖刺朝左上，不挡脸），两腿撑开（过肩摔：甩过去）",
                "THE HEAVE - leaning far back to the image left, BOTH ARMS raised high up and back over his near shoulder (as "
                "if hurling someone over his shoulder to behind him), the shield plate lifted with them, slanted up "
                "beside the head on the image left (its spiked end to the upper left, never over the face), the legs braced "
                "wide.",
                dict(pelvis=(25.0, 42.0), lift=None, shift=4, spine=-160, near_arm=("grip", 1, -150),
                     far_arm=(-170, -160, -150), near_leg=((14.0, 57.0), 1, 60), far_leg=((36.0, 57.0), -1, 60),
                     plate=dict(at=(9.0, 17.0), deg=-145, hand="near_arm"))),
    "e_throw": ("singed_spell3@900",
                "甩完：身子弯向左后方，两只手臂一起甩到左下方身后（刚把人扔出去），盾板斜在身体左下方，尖刺朝左，两腿弯着（过肩摔：扔出）",
                "THE FOLLOW-THROUGH - bent toward the back left, both arms swung down and back to the lower left (the enemy "
                "just thrown), the shield plate slanted at his lower left, its spiked end to the left, the legs bent.",
                dict(pelvis=(26.0, 44.0), lift=None, shift=4, spine=-150, near_arm=("grip", 1, -60),
                     far_arm=(-60, -50, -40), near_leg=((15.0, 57.0), 1, 50), far_leg=((36.0, 57.0), -1, 60),
                     plate=dict(at=(8.0, 42.0), deg=-125, hand="near_arm"))),
    "w_wind": ("singed_spell2@250",
               "扬手：身子往后仰，远侧手把药瓶举到头的右后上方（准备往前扔，手在头的右上方，不挡脸），近侧手臂挂着盾板垂在身边，两腿站稳（强力粘胶：起手）",
               "WIND-UP - leaning back, the FAR hand lifting the flask up behind and above the head on the image right "
               "(ready to throw, the hand above the head on the right, never over the face), the NEAR arm with the shield "
               "plate hanging at his side, the legs planted.",
               dict(pelvis=(24.0, 41.0), lift=None, shift=0, spine=-175, far_arm=(170, -170, 180),
                    near_arm=("grip", 1, 0), near_leg=((17.0, 57.0), 1, 40), far_leg=((32.0, 57.0), -1, 60),
                    plate=SIDE)),
    "w_throw": ("singed_spell2@450",
                "扔出：身子往前（画面右边）压，远侧手臂往前上方甩出去、手张开（药瓶刚扔出去，手里空了），近侧手臂挂着盾板往后摆，远侧腿往前迈（强力粘胶：扔出）",
                "THE THROW - leaning forward to the image right, the FAR arm flung forward and up with the hand open (the "
                "flask just thrown, the hand empty), the NEAR arm with the shield plate swinging back, the far leg stepping "
                "forward.",
                dict(pelvis=(24.0, 42.0), lift=None, shift=-4, spine=158, far_arm=(120, 110, 105),
                     near_arm=("grip", 1, -30), near_leg=((14.0, 57.0), 1, -60), far_leg=((36.0, 57.0), -1, 70),
                     plate=dict(at=(16.0, 37.0), deg=-165, hand="near_arm"))),
    "r_drink": ("singed_spell4@200",
                "举起药剂：挺直站高、微微后仰，远侧手把一大瓶亮绿药剂高高举在头的右上方（不挡脸），近侧手臂挂着盾板垂在身边（疯狂药剂：喝之前）",
                "THE POTION - standing tall and leaning back a little, the FAR hand holding a big bright green potion bottle "
                "high up above the head on the image right (never over the face), the NEAR arm with the shield plate hanging "
                "at his side.",
                dict(pelvis=(24.0, 41.0), lift=None, shift=0, spine=-178, far_arm=(175, 178, 180),
                     near_arm=("grip", 1, 0), near_leg=((18.0, 57.0), 1, 40), far_leg=((31.0, 57.0), -1, 60),
                     plate=SIDE)),
    "r_rage": ("singed_spell4@650",
               "发狂：喝完了，身子往前弓、微蹲，两只手臂往两边张开攥紧拳头（像全身充满力量在发抖），盾板在左边斜着，两腿大大分开（疯狂药剂：生效）",
               "THE RUSH - the potion drunk, hunched forward in a half crouch, BOTH ARMS spread out to the sides with the "
               "fists clenched (shaking with power), the shield plate slanted at his left, the legs wide apart.",
               dict(pelvis=(24.0, 44.0), lift=None, shift=0, spine=165, far_arm=(80, 60, 40),
                    near_arm=("grip", 1, -40), near_leg=((13.0, 57.0), 1, -40), far_leg=((36.0, 57.0), -1, 60),
                    plate=dict(at=(8.0, 36.0), deg=-150, hand="near_arm"))),
    "d_stagger": ("singed_death@400",
                  "踉跄：身子往后（画面左边）倒，膝盖弯下去，远侧手臂往右上方甩开、药瓶从手里掉下去，近侧手臂和盾板往左下方垂（死亡第一下）",
                  "STAGGER - reeling back to the image left, the knees buckling, the FAR arm flung out to the upper right, the "
                  "flask dropping from the hand, the NEAR arm and the shield plate sagging to the lower left.",
                  dict(pelvis=(26.0, 43.0), lift=None, shift=2, spine=-160, far_arm=(120, 140, 150),
                       near_arm=("grip", 1, -40), near_leg=((17.0, 57.0), 1, 40), far_leg=((33.0, 57.0), -1, 50),
                       plate=dict(at=(9.0, 44.0), deg=-140, hand="near_arm"))),
    "d_down": ("singed_death@1700",
               "坐倒：一屁股坐在地上，两腿往前（画面右边）伸，身子往后仰，远侧手撑在身后的地上，近侧手松开，盾板平躺在他左边的地上（死亡）",
               "DOWN - sitting down on the ground, both legs stretched forward to the image right, leaning back, the far "
               "hand propped on the ground behind him, the near hand let go; the shield plate lying flat on the ground at "
               "his left.",
               dict(pelvis=(24.0, 58.0), lift=None, shift=4, spine=-160, far_arm=((18.0, 61.0), 1, -60),
                    near_arm=((14.0, 52.0), 1, -30), near_leg=((40.0, 59.0), -1, 90), far_leg=((44.0, 58.0), -1, 90),
                    plate=dict(at=(0.0, 60.0), deg=-90, hand=None))),
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


def plate_point(b, f):
    """The point `f` of the way from the plate's bottom end (0) to its top end (1), on its middle line."""
    return along(b["at"], b["deg"], (f - GRIP) * PLATE_L)


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
    pasted, never turned), the tank with the neck. The lowest foot on the ground, or `lift` rows over it; a held plate
    moves with him, a dropped one stays where it lies."""
    wand = spec["plate"]   # the plate (the name kept from pack_aurora_poses)
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
    moved["plate"] = dict(wand, at=(wand["at"][0], wand["at"][1] + (dy if held else 0.0)))
    return moved


def to_canvas(sk, shift=0):
    out = {}
    for k, v in sk.items():
        if k == "head":
            out[k] = (v[0] + DX + shift, v[1] + DY)
        elif k in ("neck_shift", "pelvis_shift"):
            out[k] = v
        elif k == "plate":
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


def tank_layer(idle, origin, alpha):
    """The design's tank squares, moved with the neck (origin: the design's (0, 0) on the canvas grid)."""
    m = tank_mask(idle)
    lay = np.zeros(idle.shape[:2] + (4,), np.uint8)
    lay[m] = (120, 230, 40, alpha)
    im = Image.fromarray(up(lay, PX))
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    out.paste(im, (round(origin[0] * PX), round(origin[1] * PX)))
    return out


def skeleton(can, s, label, idle, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    can.alpha_composite(tank_layer(idle, s["origin"], 110 if alpha == 255 else 70))
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    b = s["plate"]
    dr.line([c(plate_point(b, 0)), c(plate_point(b, 1))], fill=COL["shaft"] + (150 if alpha == 255 else 90,),
            width=round(PLATE_W * PX))
    dr.line([c(plate_point(b, TIP0)), c(plate_point(b, 1))], fill=COL["point"] + (alpha,), width=round(PLATE_W * PX))
    g = c(b["at"])
    dr.ellipse([g[0] - 9, g[1] - 9, g[0] + 9, g[1] + 9], outline=(60, 60, 60, alpha), width=3)
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
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Singed",
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
    """Every bone, plate point and head box on the canvas; the holding wrist on the grip; no hand or plate over the
    face."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    b = s["plate"]
    bpts = [plate_point(b, f / 20) for f in range(21)]
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
    over = [] if b.get("behind") else bpts   # the design's own plate (behind) never counts
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] + over if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/si_work/singed_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(dict(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), far_arm="rest",
                                     near_arm="rest", near_leg="rest", far_leg="rest", plate=REST_PLATE))))
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

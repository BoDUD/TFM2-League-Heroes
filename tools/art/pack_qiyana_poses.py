#!/usr/bin/env python3
"""Qiyana's pose pack for Codex (assets/source/qiyana/POSE_PROMPTS.md): the whole-body poses her League clips go through,
each with the ring blade swung somewhere else - the 3/4 design cannot give them by moving its own parts (quarter turns
only: the ring would swing stiffly; the user, 2026-10-22: 「Codex 照骨架画姿势」, pack_neeko_poses.py's way).

    python tools/art/pack_qiyana_poses.py [--out C:/t/qy_work/qiyana_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-1, 52 x
60) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames (tools/lol/pose_ref.py
at the 3/4 camera): every bone at the design's OWN length (measured on hd/idle.png: REST; the far arm, foreshortened in
the design, takes the near arm's lengths), only its direction set per pose (POSES), the lowest foot on the ground unless
the pose lifts it.
THE RING (her weapon) is a rigid prop: in the design an upright ring of radius RING_R squares with two crystal heads
opposite each other, held at its rim. A pose gives the ring's middle, how it is seen (ry: RING_R upright and facing the
viewer, small when it is flat or edge-on), its tilt and where the heads and the grip are on it; the holding arm's wrist
goes to the grip.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head with its crest and hair, 8x: every pose wears it); 2_design.png (the design on the grid);
per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right), YELLOW ellipse = the RING (its
CYAN marks = the two crystal heads); grey box = the head (the design's head, never redrawn).
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
from design_qiyana_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "qiyana")
PX, CANVAS, SOLE_Y = 13, 1254, 1196
GREY = (225, 225, 225)
GROUND = 60                        # the design's soles' bottom edge (rows)
DX, DY = 24, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 92)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "ring": (235, 200, 0), "heads": (0, 200, 220)}
HEAD = (0, 31, 20, 48)             # rows / columns of the head with its crest and hair in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 28 x 31 squares
RING_R = 12.0                      # the ring's radius (squares, to the middle of its blade)
HEAD_OUT = 6.0                     # how far a crystal head sticks out of the ring

# the design's own skeleton, measured on hd/idle.png (52 x 60, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (the near hand up at the ring's rim, the far
# hand on her hip); each leg hip, knee, ankle, toes; the ring upright on the image left, held at its upper right
REST = {
    "head": (34.0, 15.5),
    "spine": [(33.0, 41.0), (33.5, 29.0)],
    "near_arm": [(26.0, 30.0), (21.0, 36.0), (18.0, 28.0), (16.5, 25.0)],
    "far_arm": [(41.0, 30.0), (45.0, 35.0), (41.0, 38.0), (38.5, 39.0)],
    "near_leg": [(29.0, 42.0), (25.0, 50.0), (26.0, 56.0), (29.0, 59.0)],
    "far_leg": [(37.0, 42.0), (41.0, 50.0), (45.0, 56.0), (49.0, 59.0)],
}
REST_RING = dict(c=(12.0, 39.0), ry=12.0, tilt=0, heads=-80, grip=-55, hand="near_arm")
# the far arm is foreshortened in the design (its forearm points at the viewer): the poses give it the near arm's bones
SAME_AS = {"far_arm": "near_arm"}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest" (the design's own,
# turned with the spine), three angles, or (target, side, last angle): the wrist / ankle at the target with the elbow /
# knee solved at the design's lengths (side -1 bends a downward limb's middle joint to the image right, +1 to the image
# left), then the hand / foot at the last angle; target "grip" = the ring's grip. The ring: its middle c (or "at": where
# the hand holds it, the middle following), ry (how wide
# it looks across its tilt: RING_R upright facing us, ~3 flat), tilt (degrees the ring's long axis turns from level,
# clockwise), heads (where the first crystal head sits on it, degrees: 0 the right end, 90 the bottom), grip (where the
# hand holds it, same degrees), hand (which arm holds it).
POSES = {
    "a_wind": ("qiyana_base_attack1@0",
               "挥环蓄势：远侧腿站直，近侧腿屈膝往前抬起，身子微微后仰，近侧手臂往左后方把圆环抡到身后（圆环几乎放平、在她身后左边，"
               "和肩一样高），远侧手臂往前平伸（普攻起手）",
               "WIND-UP - standing on the FAR leg, the NEAR knee lifted forward, the body leaning back a little, the NEAR "
               "arm swinging the ring back behind her to the image left (the ring almost flat, at shoulder height behind "
               "her), the far arm stretched forward level.",
               dict(pelvis=(33.0, 41.0), lift=None, shift=4, spine=-174, near_arm=("grip", 1, -100),
                    far_arm=((50.0, 31.0), -1, 95), near_leg=((36.0, 50.0), -1, 70), far_leg=((38.0, 56.0), -1, 50),
                    ring=dict(at=(12.0, 30.0), ry=4.0, tilt=-8, heads=180, grip=-10, hand="near_arm"))),
    "a_strike": ("qiyana_base_attack1@133",
                 "挥环砍出：往前跃起（脚离地约 3 格），身子前倾，近侧手臂把圆环往前抡到她身前右边（圆环斜着、下沿在她腰的高度），"
                 "远侧手臂往后甩开，近侧腿屈膝在前、远侧腿往后伸（普攻出手）",
                 "STRIKE - springing forward (the feet about 3 squares up), the body leaning forward, the NEAR arm sweeping "
                 "the ring round to the front at the image right (the ring tilted, its lower edge at her waist), the far arm "
                 "flung back, the near knee bent forward, the far leg stretched back.",
                 dict(pelvis=(30.0, 42.0), lift=3, shift=-2, spine=165, near_arm=("grip", -1, 90),
                      far_arm=((20.0, 40.0), 1, -100), near_leg=((36.0, 54.0), -1, 50), far_leg=((22.0, 56.0), -1, -60),
                      ring=dict(at=(40.0, 36.0), ry=6.0, tilt=20, heads=0, grip=180, hand="near_arm"))),
    "q_wind": ("qiyana_base_spell1@117",
               "横扫蓄势：弓步压低，前腿（远侧）屈膝、后腿（近侧）往后伸，身子前倾，近侧手臂往后把圆环拖在身后左边（圆环放平、"
               "贴近地面），远侧手臂弯在身前（Q 起手）",
               "SWEEP WIND-UP - a deep low lunge, the front (far) knee bent, the back (near) leg stretched out behind, "
               "the body leaning forward, the NEAR arm dragging the ring low behind her to the image left (the ring flat, "
               "close to the ground), the far arm bent before her.",
               dict(pelvis=(32.0, 46.0), lift=None, shift=8, spine=160, near_arm=("grip", 1, -80),
                    far_arm=((44.0, 40.0), 1, 100), near_leg=((18.0, 57.0), -1, -40), far_leg=((42.0, 56.0), -1, 60),
                    ring=dict(at=(15.0, 40.0), ry=4.0, tilt=0, heads=180, grip=0, hand="near_arm"))),
    "q_sweep": ("qiyana_base_spell1@350",
                "横扫：身子往前一拧，近侧手臂把圆环从身后抡到她身前右边（圆环竖起来正对着我们、在她身前右边），远侧手臂往左后方甩开，"
                "两腿大开（Q 打出）",
                "SWEEP - twisting forward, the NEAR arm sweeping the ring from behind round to the front at the image "
                "right (the ring upright and facing us, beside her on the image right), the far arm flung back to the "
                "upper left, the legs wide apart.",
                dict(pelvis=(30.0, 44.0), lift=None, shift=-4, spine=168, near_arm=("grip", -1, 60),
                     far_arm=((18.0, 38.0), 1, -110), near_leg=((20.0, 57.0), -1, -30), far_leg=((40.0, 56.0), -1, 60),
                     ring=dict(at=(39.0, 38.0), ry=11.0, tilt=0, heads=-60, grip=180, hand="near_arm"))),
    "q_end": ("qiyana_base_spell1@583",
              "收势：站直，近侧手臂把圆环平平地举在身前右边（圆环侧过来看成一条斜的长扁环，和肩一样高），远侧手臂往右上方张开，"
              "远侧腿屈膝抬起（Q 收尾）",
              "FOLLOW-THROUGH - standing tall, the NEAR arm holding the ring out level in front at the image right (the "
              "ring seen edge-on as a long flat oval at shoulder height), the far arm flung up and out to the upper right, "
              "the far knee lifted.",
              dict(pelvis=(33.0, 41.0), lift=None, shift=-6, spine=178, near_arm=("grip", -1, 90),
                   far_arm=((54.0, 24.0), -1, 140), near_leg=((32.0, 56.0), -1, 30), far_leg=((42.0, 50.0), -1, 60),
                   ring=dict(at=(40.0, 31.0), ry=3.0, tilt=-10, heads=0, grip=180, hand="near_arm"))),
    "e_dash": ("qiyana_base_spell3@250",
               "突进：身子压得很低往前冲（几乎和地面平行，头在右前方），近侧手臂把圆环平平地拖在身后（侧过来看成一条斜的长扁环），"
               "前腿（远侧）屈膝、后腿（近侧）往后蹬直（E 突进）",
               "DASH - dashing forward very low, the body almost level, the head at the front (image right), the NEAR arm "
               "trailing the ring flat behind her (seen edge-on as a long flat oval), the front (far) knee bent, the back "
               "(near) leg pushed straight out behind.",
               dict(pelvis=(28.0, 48.0), lift=2, shift=6, spine=125, near_arm=("grip", 1, -90),
                    far_arm=((48.0, 44.0), 1, 100), near_leg=((10.0, 56.0), -1, -80), far_leg=((42.0, 57.0), -1, 70),
                    ring=dict(at=(18.0, 40.0), ry=3.0, tilt=10, heads=180, grip=0, hand="near_arm"))),
    "e_hit": ("qiyana_base_spell3_hit@156",
              "落地斩：低低的大弓步落地，近侧手臂把圆环往前平平地砍出去（圆环放平、在她身前右边，腰的高度），远侧手臂往后甩，"
              "后腿（近侧）往后伸直（E 砍中）",
              "LANDING SLASH - landed in a low wide lunge, the NEAR arm slashing the ring forward flat (the ring flat in "
              "front at the image right, at waist height), the far arm flung back, the back (near) leg stretched out.",
              dict(pelvis=(30.0, 47.0), lift=None, shift=-4, spine=150, near_arm=("grip", -1, 90),
                   far_arm=((18.0, 34.0), 1, -100), near_leg=((12.0, 57.0), -1, -60), far_leg=((42.0, 56.0), -1, 60),
                   ring=dict(at=(43.0, 42.0), ry=4.0, tilt=0, heads=0, grip=180, hand="near_arm"))),
    "r_leap": ("qiyana_base_spell4@156",
               "跃起举环：笔直地跳起来（脚离地约 10 格），两腿屈膝收起，近侧手臂把圆环举到身后上方（圆环竖着、在她头后面偏左，"
               "环的下沿在肩膀的高度，不挡脸），远侧手臂往右上方张开（R 起跳）",
               "LEAP - leaping straight up (the feet about 10 squares up), both knees tucked up, the NEAR arm raising the "
               "ring up behind her (upright, behind her head toward the image left, its lower edge at her shoulders, "
               "never over the face), the far arm flung up and out to the upper right.",
               dict(pelvis=(33.0, 40.0), lift=10, shift=6, spine=176, near_arm=("grip", 1, -170),
                    far_arm=((50.0, 22.0), -1, 150), near_leg=((32.0, 50.0), -1, 60), far_leg=((40.0, 50.0), -1, 60),
                    ring=dict(c=(14.0, 14.0), ry=10.0, tilt=0, heads=-90, grip=60, hand="near_arm"))),
    "r_slam": ("qiyana_base_spell4@467",
               "砸环：落地前倾，近侧手臂把圆环从上往前下方狠狠砸出去（圆环斜着、在她身前右边，下沿碰到地面），远侧手臂往左后方甩开，"
               "前腿（远侧）屈膝、后腿（近侧）往后伸（R 砸出冲击波）",
               "SLAM - landing and leaning forward, the NEAR arm smashing the ring down forward (tilted, in front at the "
               "image right, its lower edge touching the ground), the far arm flung back to the upper left, the front "
               "(far) knee bent, the back (near) leg stretched out.",
               dict(pelvis=(30.0, 45.0), lift=None, shift=-6, spine=150, near_arm=("grip", -1, 100),
                    far_arm=((18.0, 26.0), 1, -130), near_leg=((14.0, 57.0), -1, -60), far_leg=((42.0, 56.0), -1, 60),
                    ring=dict(at=(43.0, 41.0), ry=7.0, tilt=20, heads=-120, grip=200, hand="near_arm"))),
    "run1": ("qiyana_base_run@0", "跑步 1（远侧腿在前着地，近侧腿往后抬起）：身子前倾，近侧手把圆环斜扛在背后（从左上到右下的一条斜扁环），远侧手臂在身前摆",
             "RUN 1 - running: the FAR leg forward with its foot landing, the NEAR leg kicked up behind her, the body "
             "leaning forward, the NEAR hand carrying the ring slung diagonally across her back (a flat oval from the "
             "upper left to the lower right behind her), the far arm swinging before her.",
             dict(pelvis=(32.0, 41.0), lift=None, shift=4, spine=165, near_arm=("grip", 1, -40),
                  far_arm=((44.0, 38.0), 1, 80), near_leg=((20.0, 52.0), -1, -70), far_leg=((42.0, 56.0), -1, 50),
                  ring=dict(c=(24.0, 32.0), ry=4.0, tilt=40, heads=0, grip=200, hand="near_arm"))),
    "run2": ("qiyana_base_run@233", "跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，圆环同样斜扛在背后",
             "RUN 2 - running: the near leg under the body carrying her, the FAR knee lifted forward, the body one square "
             "higher, the ring slung diagonally across her back as before, the far arm swinging back.",
             dict(pelvis=(32.0, 40.0), lift=1, shift=4, spine=167, near_arm=("grip", 1, -40),
                  far_arm=((40.0, 40.0), 1, 20), near_leg=((32.0, 56.0), -1, 30), far_leg=((42.0, 47.0), -1, 70),
                  ring=dict(c=(24.0, 31.0), ry=4.0, tilt=40, heads=0, grip=200, hand="near_arm"))),
    "run3": ("qiyana_base_run@467", "跑步 3（近侧腿在前着地，远侧腿往后抬起）",
             "RUN 3 - running: the NEAR leg forward with its foot landing, the FAR leg kicked up behind her, the body "
             "leaning forward, the ring slung diagonally across her back, the far arm swinging back.",
             dict(pelvis=(32.0, 41.0), lift=None, shift=4, spine=165, near_arm=("grip", 1, -40),
                  far_arm=((38.0, 40.0), 1, -20), near_leg=((40.0, 56.0), -1, 50), far_leg=((22.0, 52.0), -1, -70),
                  ring=dict(c=(24.0, 32.0), ry=4.0, tilt=40, heads=0, grip=200, hand="near_arm"))),
    "run4": ("qiyana_base_run@700", "跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格",
             "RUN 4 - running: the far leg under the body carrying her, the NEAR knee lifted forward, the body one square "
             "higher, the ring slung diagonally across her back, the far arm swinging before her.",
             dict(pelvis=(32.0, 40.0), lift=1, shift=4, spine=167, near_arm=("grip", 1, -40),
                  far_arm=((44.0, 37.0), 1, 80), near_leg=((38.0, 48.0), -1, 70), far_leg=((36.0, 56.0), -1, 30),
                  ring=dict(c=(24.0, 31.0), ry=4.0, tilt=40, heads=0, grip=200, hand="near_arm"))),
    "d_fall": ("qiyana_base_death@583",
               "踉跄倒下：身子往左后方倒，膝盖弯下去，近侧手臂垂下、圆环从手里滑落到她身后左边的地上（圆环斜着、下沿碰地），"
               "远侧手捂着胸口（死亡第一下）",
               "STAGGER - falling back toward the image left, the knees buckling, the NEAR arm hanging with the ring "
               "slipping from her hand onto the ground behind her on the image left (tilted, its lower edge on the "
               "ground), the far hand clutching her chest.",
               dict(pelvis=(32.0, 45.0), lift=None, shift=6, spine=-160, near_arm=("grip", 1, -30),
                    far_arm=((36.0, 34.0), -1, -60), near_leg=((24.0, 57.0), -1, -20), far_leg=((40.0, 56.0), -1, 40),
                    ring=dict(c=(6.0, 50.0), ry=7.0, tilt=-20, heads=150, grip=-30, hand="near_arm"))),
    "d_lie": ("qiyana_base_death@2917",
              "跪坐倒地：坐到地上，近侧腿跪着折在身下，远侧腿立起膝盖，近侧手撑在身边的地上，远侧手搭在膝盖上，头低着；圆环平躺在她身后"
              "左边的地上（侧过来看成一条贴地的扁环）（死亡）",
              "DOWN - sunk down sitting on the ground, the near leg folded under her with its knee on the ground, the far "
              "knee raised, the near hand propped on the ground beside her, the far hand resting on the raised knee; the "
              "ring lying flat on the ground behind her on the image left (seen as a flat oval on the ground).",
              dict(pelvis=(32.0, 52.0), lift=None, shift=8, spine=-176, near_arm=((22.0, 58.0), 1, 0),
                   far_arm=((42.0, 46.0), -1, 60), near_leg=((26.0, 59.0), 1, -90), far_leg=((44.0, 58.0), -1, 60),
                   ring=dict(c=(4.0, 57.0), ry=2.5, tilt=0, heads=180, grip=0, hand=None))),
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


def ring_point(r, deg, out=0.0):
    """A point on the ring at `deg` (0 = its right end, 90 = its bottom before the tilt), `out` squares outside it."""
    t = math.radians(deg)
    x, y = (RING_R + out) * math.cos(t), (r["ry"] + out * r["ry"] / RING_R) * math.sin(t)
    k = math.radians(r["tilt"])
    return (r["c"][0] + x * math.cos(k) - y * math.sin(k), r["c"][1] + x * math.sin(k) + y * math.cos(k))


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


def build(spec, ring):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned). The lowest foot or knee on the ground, or `lift` rows over it; the ring moves with it."""
    if "at" in ring:                     # placed by its grip: the ring's middle follows from where the hand holds it
        g = ring_point(dict(ring, c=(0.0, 0.0)), ring["grip"])
        ring = dict(ring, c=(ring["at"][0] - g[0], ring["at"][1] - g[1]))
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    grip = ring_point(ring, ring["grip"])
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
            M, A = bend(pts[0], grip if target == "grip" else target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    low = max(y for leg in ("near_leg", "far_leg") for _, y in sk[leg])
    dy = REST["near_leg"][-1][1] - (spec["lift"] or 0) - low
    sk = {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}
    held = ring.get("hand") is not None     # a ring lying on the ground stays where it lies
    sk["ring"] = dict(ring, c=(ring["c"][0], ring["c"][1] + (dy if held else 0.0)))
    return sk


def to_canvas(sk, shift=0):
    out = {}
    for k, v in sk.items():
        if k == "head":
            out[k] = (v[0] + DX + shift, v[1] + DY)
        elif k == "ring":
            out[k] = dict(v, c=(v["c"][0] + DX + shift, v["c"][1] + DY))
        else:
            out[k] = [(x + DX + shift, y + DY) for x, y in v]
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


def skeleton(can, s, label, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    r = s["ring"]
    rim = [c(ring_point(r, d)) for d in range(0, 361, 6)]
    dr.line(rim, fill=COL["ring"] + (alpha,), width=9, joint="curve")
    for d in (r["heads"], r["heads"] + 180):
        a0, a1 = c(ring_point(r, d)), c(ring_point(r, d, HEAD_OUT))
        dr.line([a0, a1], fill=COL["heads"] + (alpha,), width=11)
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    order = [("far_leg", 7), ("far_arm", 7), ("spine", 7), ("near_leg", 7), ("near_arm", 7)]
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
    """League's frame at the 3/4 camera, the ring blade shown (her skin hides it: no --hide-submeshes)."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Qiyana",
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
    return {name: (to_canvas(build(spec, spec["ring"]), spec.get("shift", 0)), frame, zh, en)
            for name, (frame, zh, en, spec) in POSES.items()}


def problems(name, s):
    """Every bone, ring point and head box on the canvas; no hand or ring part over the face."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    pts += [ring_point(s["ring"], d) for d in range(0, 360, 10)]
    pts += [ring_point(s["ring"], d, HEAD_OUT) for d in (s["ring"]["heads"], s["ring"]["heads"] + 180)]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.01 for x, y in pts):
        out.append("off the canvas")
    hx, hy = s["head"]
    if hy - HH / 2 < 1:
        out.append("head off the top")
    hand = s["ring"].get("hand")
    if hand:                             # the holding wrist reaches the grip (else bend() fell short)
        g = ring_point(s["ring"], s["ring"]["grip"])
        w = s[hand][2]
        if math.hypot(g[0] - w[0], g[1] - w[1]) > 0.6:
            out.append(f"the {hand} cannot reach the grip ({math.hypot(g[0] - s[hand][0][0], g[1] - s[hand][0][1]):.1f}"
                       f" squares from the shoulder)")
    # the face: the middle of the head box (eyes to mouth)
    fx0, fx1, fy0, fy1 = hx - 6, hx + 9, hy - 2, hy + 12
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] + [ring_point(s["ring"], d) for d in range(0, 360, 5)]
            if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/qy_work/qiyana_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(dict(REST, ring=REST_RING))
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
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

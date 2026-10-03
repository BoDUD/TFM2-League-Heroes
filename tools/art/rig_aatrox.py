#!/usr/bin/env python3
"""Aatrox's action strips put together from the approved design's own parts (2026-10-03).

    python tools/art/rig_aatrox.py [--check]

Codex's strips (assets/source/aatrox/codex_strips/, its animation_source.py) cut the design into layers and moved them:
the body kept only a 4-square column under the chest (the hips and thighs cut away), was shifted 1-2 squares off the
legs, the arms were drawn as tubes and the ult's wings as flat polygons. The user: 「腿变形还有上下身体脱节 开大时大招
翅膀极度奇怪」. Here every frame keeps the design whole and moves only what the action moves:
- BODY: the design without the blade, the near arm and its fist (NEAR_ARM) - the near hip painted where the fist and
  the grip covered it (NEAR_HIP) - and, where the far red arm moves (W, the ult, the run), without it (FAR_ARM, the
  waist painted: WAIST). Head, wings, chest, hips and both legs stay square for square on the idle's place (the
  user's rule: every standing pose on the idle's own legs); Q3's leap lifts the whole figure, the hit pushes it back.
- the near arm: shoulder -> elbow -> fist, three squares thick in the gauntlet's steel (lit edge, core, shadow) with
  one outline ring, the fist a 3 x 3 block; a fist out of reach stops at the arm's length (REACH), never a stretched
  stick. The far red arm the same in its reds, with the claw open for the throw.
- the greatsword: the design's own blade turned whole by RotSprite about its grip, its grip in the fist. Angles and
  fists follow Codex's pose plans (POSES), the fists pulled into reach.
- the ult's wings: the design's own wings turned out about the shoulders by RotSprite, a second copy turned further
  behind each for the spread membrane (WINGS).
- the death: the whole design turned by RotSprite (staggering back), then a quarter (lying on his back, face up), the
  blade on the ground beside him.
- the run: the idle's own two legs, every square as drawn, turned about the hips by RotSprite - the planted one from
  ahead to behind, the swinging one lifted and bent at the knee on its way forward - the hips in under the waist so the
  near leg passes in front of the far one; the body a row lower when the planted leg slants.
--check compares the strips with assets/source/native/.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_aatrox as D  # noqa: E402
from rig_nocturne import rotsprite  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "native")
CELLS = os.path.join(OUT, "aatrox_cells.json")
TAGS = ["idle", "run", "attack", "attack_p", "skill", "q2", "q3", "skill2", "ult", "hit", "dead"]
# drawn by Codex since 2026-10-04 (League's full-body Q casts, the transformation with League's wings):
# tools/art/import_redo_aatrox.py writes them
CODEX = {"skill", "q2", "q3", "ult"}
Z = 8
PIVOT = (64, 88)
# canvas row -> (first col, last col) cleared
NEAR_ARM = {77: (53, 58), 78: (53, 58), 79: (54, 58), 80: (54, 58), 81: (56, 58), 82: (57, 59), 83: (57, 60),
            84: (58, 61), 85: (57, 60), 86: (57, 60)}
FAR_ARM = {77: (68, 70), 78: (68, 71), 79: (68, 72), 80: (67, 71), 81: (67, 71), 82: (65, 70), 83: (65, 68),
           84: (65, 67)}
NEAR_HIP = {(84, 59): "o", (84, 60): "0", (84, 61): "e", (85, 58): "o", (85, 59): "0", (85, 60): "e",
            (86, 57): "o", (86, 58): "0", (86, 59): "0", (86, 60): "e"}
WAIST = {(82, 64): "a", (82, 65): "o", (83, 65): "o", (84, 65): "e", (84, 66): "e", (84, 67): "o"}
NEAR_SHOULDER = (57.0, 77.0)
FAR_SHOULDER = (68.0, 77.0)
REACH = 10.5                         # shoulder to fist, the design's arm (77, 55) -> (84, 60) plus the fist
GRIP = (57.5, 85.5)                  # the blade's grip on the design (under the near fist)
BASE = math.degrees(math.atan2(8, -20))   # the blade's direction on the design (screen degrees, y down)
STEEL = ("3", "2", "1")              # the gauntlet arm: lit edge, core, shadow
RED = ("8", "6", "5")                # the red arm
FIST = ["e23", "123", "ee1"]
CLAW = ["7o7o", "8888", "7o7o"]      # the far claw open (rows over and under the wrist), drawn rightwards
# Codex's pose plans (codex_strips/animation_source.py): per frame (blade angle, fist x, y) on the canvas, None = the
# design's own hold
POSES = {
    "attack": [None, (175, (57, 84)), (45, (68, 78)), (0, (72, 84)), (12, (72, 85)), None],
    "attack_p": [(-125, (59, 79)), (177, (56, 86)), (165, (55, 85)), (0, (75, 84)), (0, (75, 84)), None],
    "skill": [None, (-130, (53, 70)), (-100, (53, 62)), (0, (68, 74)), (65, (67, 78)), (65, (67, 78)), None],
    "q2": [None, (-150, (53, 72)), (-115, (53, 64)), (-30, (69, 78)), (0, (75, 84)), (12, (75, 84)), None],
    "q3": [(-130, (54, 73)), (-110, (53, 62)), (-100, (53, 60)), (-15, (67, 70)), (65, (67, 78)), (65, (67, 78)), None],
}
LIFT = {"q3": [0, 2, 3, 1, 0, 0, 0]}
# W: the far arm's elbow and fist per frame (Codex's throws), claw open in 2-5
THROW = [None, ((72, 74), (68, 71)), ((73, 73), (70, 70)), ((75, 76), (82, 76)), ((75, 76), (82, 76)), None]
# the ult: wings turned out (degrees) per frame, the blade held out to the near side, the far claw out
ULT_SPREAD = [None, 0.25, 0.55, 1.0, 1.0, None]
# the ult's arms per frame: the blade's angle and the near fist, the far elbow and claw (frame 2 opening, 3-5 out)
ULT_ARMS = [None, (165, (53, 83), (72, 79), (75, 80)), (150, (49, 81), (73, 78), (78, 77)),
            (150, (49, 81), (73, 78), (78, 77)), (150, (49, 81), (73, 78), (78, 77)), None]
FAR_ROOT = (69, 75)                  # where the drawn wings join the back (behind the shoulders)
NEAR_ROOT = (58, 75)
# the run (8 frames, 2026-10-04): every leg I drew was turned down - the whole-leg shear slid the knee plate off the shin
# as it played (「是膝盖那和下面的小腿 走路的时候感觉脱节的」), legs from close hips read as a skirt under the wide waist
# (「怎么看起来剑魔像穿了裙子？？」), two-bone legs on League's joints were 「不自然」, Codex's redraw lost to them; then
# 「你把待机的腿用到走路啊」, and the idle's legs slid whole on the ground were 「你觉得对吗？ 不自然啊」 (no swing, no
# knee). Now each of the idle's legs, every square as drawn, is TURNED about its hip by RotSprite (RUN: degrees, + = the
# foot ahead - a forward leg lands heel first, a back one leaves on the toe) and lifted RUN rows off the ground while it
# swings, bent at the knee when lifted 2+ rows (RUN_BEND: the thigh and the shin + boot turned apart, cut at KNEE_ROW);
# the hips come RUN_HIP_IN in under the waist so the feet cross (the near leg in front of the far one in an X in frames 8
# and 1; spread at most ~12 squares in 4-5); the near boot is mirrored about its knee so its toe points forward like the
# far one's; the body drops a row when the planted leg's slant shortens it.
RUN = [[24, 0, -32, 1], [12, 0, -22, 3], [-4, 0, 6, 3], [-14, 0, 18, 1],    # [near deg, near lift, far deg, far lift]
       [-22, 1, 16, 0], [-12, 3, 6, 0], [8, 3, -8, 0], [24, 1, -24, 0]]
RUN_HIP_IN = 3
RUN_BEND = (10, 25)
LEG_TOP = 88                         # the legs below this row move; the hips and the skirt above stay
KNEE_ROW = 94                        # the shin + boot from this row down
# the idle's legs (canvas squares): their columns, hips and knees; the lit (near) one's boot is mirrored about its knee
NEAR_LEG = {"cols": (52, 64), "hip": (59.0, 88.0), "knee": (58.0, 93.5)}
FAR_LEG = {"cols": (64, 76), "hip": (69.0, 88.0), "knee": (69.0, 93.5)}
DEAD = [(0, 0), (0.15, 0), (0.4, 1), ("rot", 0), ("rot", 0), ("rot", 0), ("rot", 0), ("rot", 0)]


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) or os.name != "nt" else pre + p


def rgba(k):
    return np.array(list(D.COL[k]) + [255], np.uint8)


def design():
    return D.load(D.OUT)[4::8, 4::8].copy()


def sword_mask(des):
    g = D.letters(des)
    part = D.blade(D.load(D.FIRST))
    keys = list(part)
    r0, c0 = min(r for r, _ in keys), min(c for _, c in keys)
    for dy in range(-r0, 128 - r0):
        for dx in range(-c0, 128 - c0):
            if all(0 <= r + dy < 128 and 0 <= c + dx < 128 and g[r + dy][c + dx] == part[(r, c)] for r, c in keys):
                m = np.zeros((128, 128), bool)
                for r, c in keys:
                    m[r + dy, c + dx] = True
                return m
    raise SystemExit("blade not found")


def loose_outline(a):
    """Outline squares with no coloured square round them go (the blade's outer ring left on the body)."""
    ink = (a[..., 3] > 0) & (a[..., :3] == D.COL["o"]).all(-1)
    col = (a[..., 3] > 0) & ~ink
    near = np.zeros_like(col)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near |= np.roll(np.roll(col, dy, 0), dx, 1)
    a[ink & ~near] = 0
    return a


def body(des, sm, far_arm=False):
    a = des.copy()
    a[sm] = 0
    for r, (c0, c1) in NEAR_ARM.items():
        a[r, c0:c1 + 1] = 0
    for (r, c), k in NEAR_HIP.items():
        a[r, c] = rgba(k)
    if far_arm:
        for r, (c0, c1) in FAR_ARM.items():
            a[r, c0:c1 + 1] = 0
        for (r, c), k in WAIST.items():
            a[r, c] = rgba(k)
    return loose_outline(a)


def sword_sprite(des, sm):
    s = np.zeros_like(des)
    s[sm] = des[sm]
    return s


def over(dst, src, dx=0, dy=0):
    """src laid over dst, moved (dx, dy)."""
    h, w = src.shape[:2]
    H, W = dst.shape[:2]
    y0, x0 = max(0, dy), max(0, dx)
    y1, x1 = min(H, dy + h), min(W, dx + w)
    if y1 <= y0 or x1 <= x0:
        return dst
    s = src[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    m = s[..., 3] > 0
    dst[y0:y1, x0:x1][m] = s[m]
    return dst


def turned(sprite, joint, deg, to):
    """sprite turned deg (counter-clockwise on screen) about joint, the joint put on `to` of a 128 canvas."""
    r, (jx, jy) = rotsprite(sprite, joint, deg)
    out = np.zeros((128, 128, 4), np.uint8)
    return over(out, r, int(round(to[0] - jx)), int(round(to[1] - jy)))


def blade(des, sm, fist, angle):
    """The design's blade turned to `angle` (screen degrees) with its grip in the fist."""
    return turned(sword_sprite(des, sm), GRIP, -(angle - BASE), fist)


def reach(shoulder, fist):
    sx, sy = shoulder
    fx, fy = fist
    d = math.hypot(fx - sx, fy - sy)
    if d <= REACH:
        return fist
    return (sx + (fx - sx) * REACH / d, sy + (fy - sy) * REACH / d)


def elbow(shoulder, fist, out=1.0):
    """The elbow of a two-bone arm (two halves of REACH), bent away from the body (down and out)."""
    sx, sy = shoulder
    fx, fy = fist
    d = max(1e-6, math.hypot(fx - sx, fy - sy))
    half = REACH / 2
    h = math.sqrt(max(0.0, half * half - (d / 2) ** 2))
    mx, my = (sx + fx) / 2, (sy + fy) / 2
    nx, ny = -(fy - sy) / d, (fx - sx) / d          # a normal; the elbow takes the one pointing down / outward
    if ny < 0 or (abs(ny) < 1e-6 and nx * out < 0):
        nx, ny = -nx, -ny
    return (mx + nx * h, my + ny * h)


def limb(a, points, mats):
    """A three-square limb along the polyline: lit edge on the side toward the top-left, core, shadow; one ring."""
    H, W = a.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    px, py = xs + 0.5, ys + 0.5
    best = np.full((H, W), 1e9)
    side = np.zeros((H, W))
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        x0, y0, x1, y1 = x0 + 0.5, y0 + 0.5, x1 + 0.5, y1 + 0.5
        vx, vy = x1 - x0, y1 - y0
        L2 = max(1e-6, vx * vx + vy * vy)
        t = np.clip(((px - x0) * vx + (py - y0) * vy) / L2, 0, 1)
        dx, dy = px - (x0 + t * vx), py - (y0 + t * vy)
        dist = np.hypot(dx, dy)
        nx, ny = -vy / math.sqrt(L2), vx / math.sqrt(L2)
        if nx + ny > 0:                                 # the normal toward the top-left (light)
            nx, ny = -nx, -ny
        s = dx * nx + dy * ny
        closer = dist < best
        best = np.where(closer, dist, best)
        side = np.where(closer, s, side)
    core = best <= 1.6
    ring = (best <= 2.6) & ~core & (a[..., 3] == 0)
    a[ring] = rgba("o")
    lit, mid, dark = mats
    a[core & (side > 0.55)] = rgba(lit)
    a[core & (np.abs(side) <= 0.55)] = rgba(mid)
    a[core & (side < -0.55)] = rgba(dark)
    return a


def stamp(a, rows, at, ring=True):
    """Letter rows centred on `at` (x, y), with an outline ring where clear."""
    h, w = len(rows), len(rows[0])
    x0, y0 = int(round(at[0] - w // 2)), int(round(at[1] - h // 2))
    if ring:
        for r in range(-1, h + 1):
            for c in range(-1, w + 1):
                y, x = y0 + r, x0 + c
                if 0 <= y < 128 and 0 <= x < 128 and a[y, x, 3] == 0:
                    a[y, x] = rgba("o")
    for r, row in enumerate(rows):
        for c, k in enumerate(row):
            if k != ".":
                a[y0 + r, x0 + c] = rgba(k)
    return a


def near_arm(a, fist):
    fist = reach(NEAR_SHOULDER, fist)
    el = elbow(NEAR_SHOULDER, fist, out=-1)
    limb(a, [NEAR_SHOULDER, el, fist], STEEL)
    return stamp(a, FIST, fist)


def far_arm(a, el, fist, claw=False):
    limb(a, [FAR_SHOULDER, el, fist], RED)
    if claw:
        return stamp(a, CLAW, (fist[0] + 2, fist[1]))
    return stamp(a, ["66", "56"], fist)


def wings(des, deg):
    """The design's wings turned out about the shoulders, a second copy turned further for the spread membrane."""
    near = np.zeros_like(des)
    far = np.zeros_like(des)
    hm = head_mask(des)
    for r in range(56, 84):
        for c in range(0, 128):
            if not des[r, c, 3] or hm[r, c]:
                continue
            if c <= (58 if r <= 72 else 55 if r <= 76 else 52):
                near[r, c] = des[r, c]
            elif c >= (70 if r <= 76 else 72):
                far[r, c] = des[r, c]
    out = np.zeros_like(des)
    for part, joint, sign in ((near, (57, 73), 1), (far, (70, 73), -1)):
        for k, extra in ((1, 1.6), (0, 1.0)):            # the far copy first, behind
            over(out, turned(part, joint, sign * deg * extra, joint))
    return out, near, far


def seg_dist(px, py, a, b):
    (x0, y0), (x1, y1) = a, b
    vx, vy = x1 - x0, y1 - y0
    L2 = max(1e-9, vx * vx + vy * vy)
    t = np.clip(((px - x0) * vx + (py - y0) * vy) / L2, 0, 1)
    return np.hypot(px - (x0 + t * vx), py - (y0 + t * vy))


def spread_wing(spread=1.0, size=1.0, bowk=0.22):
    """The right (far) wing, root at the returned joint; x right, y down. spread 0 = folded up, 1 = open."""
    S = size
    W = (8 * S, -13 * S)                                     # the wrist
    tips = [(17 * S, -20 * S), (20 * S, -9 * S), (13 * S, 0 * S)]
    folded = [(10 * S, -22 * S), (11 * S, -16 * S), (10 * S, -9 * S)]
    tips = [(f[0] + (t[0] - f[0]) * spread, f[1] + (t[1] - f[1]) * spread) for t, f in zip(tips, folded)]

    def bow(a, b, k=bowk):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        return (mx + (W[0] - mx) * k, my + (W[1] - my) * k)
    root = (0.0, 0.0)
    trail = [tips[0], bow(tips[0], tips[1]), tips[1], bow(tips[1], tips[2]), tips[2], bow(tips[2], root, 0.15)]
    poly = [root, W] + trail
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    x0, y0 = int(math.floor(min(xs))) - 3, int(math.floor(min(ys))) - 3
    w, h = int(math.ceil(max(xs))) - x0 + 4, int(math.ceil(max(ys))) - y0 + 4
    im = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(im).polygon([((x - x0) * 4, (y - y0) * 4) for x, y in poly], fill=255)
    mem = np.asarray(im.resize((w, h), Image.BOX)) >= 128
    yy, xx = np.mgrid[0:h, 0:w]
    px, py = xx + x0 + 0.5, yy + y0 + 0.5
    arm = seg_dist(px, py, root, W) <= 0.7
    fingers = np.zeros_like(arm)
    for t in tips:
        fingers |= seg_dist(px, py, W, t) <= 0.5
    folds = np.zeros_like(arm)                                # dark folds from the wrist to each scallop
    for a_, b_ in ((tips[0], tips[1]), (tips[1], tips[2])):
        folds |= seg_dist(px, py, W, bow(a_, b_, 0.0)) <= 0.45
    edge = np.zeros_like(mem)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        edge |= mem & ~np.roll(np.roll(mem, dy, 0), dx, 1)
    lead = np.minimum(seg_dist(px, py, root, W), seg_dist(px, py, W, tips[0])) <= 1.2
    a = np.zeros((h, w, 4), np.uint8)
    a[mem] = rgba("a")
    a[mem & folds] = rgba("9")
    a[edge & mem] = rgba("6")                                 # the crimson trailing rim
    a[edge & mem & lead] = rgba("8")                          # the lit leading edge
    a[fingers & mem] = rgba("0")
    a[arm] = rgba("0")
    a[arm & lead & edge] = rgba("2")
    for t in tips:
        ty, tx = int(round(t[1] - y0 - 0.5)), int(round(t[0] - x0 - 0.5))
        if 0 <= ty < h and 0 <= tx < w and a[ty, tx, 3]:
            a[ty, tx] = rgba("7")
    wy, wx = int(round(W[1] - y0 - 0.5)), int(round(W[0] - x0 - 0.5))
    for dy, dx, k in ((-1, -1, "2"), (-2, -1, "3"), (-3, 0, "3")):
        if 0 <= wy + dy < h and 0 <= wx + dx < w:
            a[wy + dy, wx + dx] = rgba(k)
    op = a[..., 3] > 0
    ring = np.zeros_like(op)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ring |= np.roll(np.roll(op, dy, 0), dx, 1)
    a[ring & ~op] = rgba("o")
    return a, (-x0, -y0)


HEAD = None


def head_mask(des):
    """The head's squares on the design (design_aatrox step 6: the first design's head mirrored)."""
    global HEAD
    if HEAD is None:
        HEAD = np.zeros((128, 128), bool)
        for r, c in D.head_squares(des, D.load(D.FIRST), mirrored=True):
            HEAD[r, c] = True
    return HEAD


def frame(tag, i, des, sm):
    """One frame on the 128 canvas, the standing point at PIVOT."""
    if tag == "idle":                                    # the design itself (import_native breathes it: BOB)
        return des.copy()
    if tag == "dead":
        return dead(i, des, sm)
    if tag == "run":
        return run(i, des, sm)
    if tag in POSES:
        pose = POSES[tag][i]
        if pose is None:
            return des.copy()
        angle, fist = pose
        a = body(des, sm)
        fist = reach(NEAR_SHOULDER, fist)
        a = over(a, blade(des, sm, fist, angle))
        a = near_arm(a, fist)
        lift = LIFT.get(tag, [0] * 9)[i]
        if lift:
            a = np.roll(a, -lift, 0)
        return a
    if tag == "skill2":
        t = THROW[i]
        if t is None:
            return des.copy()
        a = body(des, sm, far_arm=True)
        a = over(a, blade(des, sm, (57.5, 85.5), BASE))
        a = near_arm(a, (58, 84))
        f = reach(FAR_SHOULDER, t[1])
        return far_arm(a, elbow(FAR_SHOULDER, f, out=1), f, claw=True)
    if tag == "ult":
        spread = ULT_SPREAD[i]
        if spread is None:
            return des.copy()
        _, near, far = wings(des, 0)
        b = body(des, sm, far_arm=True)
        b[(near[..., 3] > 0) | (far[..., 3] > 0)] = 0
        b = loose_outline(b)
        out = np.zeros_like(des)
        r, (jx, jy) = spread_wing(spread)
        over(out, r, int(FAR_ROOT[0] - jx), int(FAR_ROOT[1] - jy))
        l = r[:, ::-1]
        over(out, l, int(NEAR_ROOT[0] - (l.shape[1] - 1 - jx)), int(NEAR_ROOT[1] - jy))
        out = over(out, b)
        angle, fist, _, claw = ULT_ARMS[i]
        fist = reach(NEAR_SHOULDER, fist)
        out = over(out, blade(des, sm, fist, angle))
        out = near_arm(out, fist)
        f = reach(FAR_SHOULDER, claw)
        return far_arm(out, elbow(FAR_SHOULDER, f, out=1), f, claw=True)
    if tag == "hit":                                     # jolted back: a slight lean, every row's squares kept
        return sheared(des, 0.08) if i == 0 else des.copy()
    raise ValueError(tag)


def turn(sprite, joint, deg):
    """RotSprite about joint (+ = counter-clockwise on screen: a hanging part swings ahead): (sprite, joint in it)."""
    if abs(deg) < 0.5:
        return sprite, joint
    r, (jx, jy) = rotsprite(sprite, joint, deg)
    return r, (jx + (joint[0] - round(joint[0])), jy + (joint[1] - round(joint[1])))


def leg_pieces(des, sm, L, mirror=False):
    """One of the idle's legs cut at the knee: (thigh, shin + boot, whole leg), the blade's squares left out; the shin +
    boot mirrored about the knee's column when `mirror` (the toe forward)."""
    c0, c1 = L["cols"]
    thigh, shin = np.zeros_like(des), np.zeros_like(des)
    thigh[LEG_TOP:KNEE_ROW, c0:c1] = des[LEG_TOP:KNEE_ROW, c0:c1]
    shin[KNEE_ROW:, c0:c1] = des[KNEE_ROW:, c0:c1]
    thigh[sm] = 0
    shin[sm] = 0
    if mirror:
        ys, xs = np.nonzero(shin[..., 3])
        m = np.zeros_like(shin)
        m[ys, np.round(2 * L["knee"][0] - xs).astype(int)] = shin[ys, xs]
        shin = m
    return thigh, shin, over(thigh.copy(), shin)


def run_leg(pieces, L, deg, lift, hip_at):
    """A leg turned deg about its hip, bent RUN_BEND at the knee when lifted 2+ rows."""
    thigh, shin, whole = pieces
    out = np.zeros((128, 128, 4), np.uint8)
    if lift >= 2:
        th, sh = deg + RUN_BEND[0], deg - RUN_BEND[1]
        t = math.radians(th)
        vx, vy = L["knee"][0] - L["hip"][0], L["knee"][1] - L["hip"][1]
        knee = (hip_at[0] + vx * math.cos(t) + vy * math.sin(t), hip_at[1] - vx * math.sin(t) + vy * math.cos(t))
        parts = ((shin, L["knee"], sh, knee), (thigh, L["hip"], th, hip_at))
    else:
        parts = ((whole, L["hip"], deg, hip_at),)
    for piece, joint, d, at in parts:
        s, j = turn(piece, joint, d)
        over(out, s, int(round(at[0] - j[0])), int(round(at[1] - j[1])))
    return out


def run(i, des, sm):
    """The idle's legs turned about the hips (RUN), each with its lowest square `lift` rows over the soles' row; the
    upper body - head, wings, arms, the blade - the design's own, a row lower when a planted leg's slant shortens it."""
    upper = des.copy()
    upper[LEG_TOP:, NEAR_LEG["cols"][0]:FAR_LEG["cols"][1]] = 0
    upper[sm] = des[sm]                                   # the blade hangs below the hips with the fist
    na, nl, fa, fl = RUN[i]
    legs, drop = [], 0
    for L, deg, lift, near in ((FAR_LEG, fa, fl, False), (NEAR_LEG, na, nl, True)):
        hip = (L["hip"][0] + (RUN_HIP_IN if near else -RUN_HIP_IN), L["hip"][1])
        a = run_leg(leg_pieces(des, sm, L, mirror=near), L, deg, lift, hip)
        low = int(np.nonzero(a[..., 3].any(1))[0].max())
        if not lift:
            drop = max(drop, min(1, 99 - low))
        legs.append(np.roll(a, 99 - lift - low, 0))
    out = np.zeros_like(des)
    for a in legs:                                        # the near leg over the far one
        over(out, a)
    return over(out, upper, 0, drop)


def sheared(a, k, sink=0):
    """Every row over the soles moved left by k x its height over them (a lean back, each row's squares unchanged),
    the whole lowered `sink` rows."""
    out = np.zeros_like(a)
    for y in range(a.shape[0]):
        dx = -int(round(k * (99 - y)))
        row = a[y]
        yy = y + sink
        if not 0 <= yy < a.shape[0]:
            continue
        if dx < 0:
            out[yy, :dx] = np.where(row[-dx:, 3:4] > 0, row[-dx:], out[yy, :dx])
        else:
            out[yy] = np.where(row[:, 3:4] > 0, row, out[yy])
    return out


def dead(i, des, sm):
    """Staggering back (rows sheared, no rotation noise), then on his back (a quarter turn: every square exact), the
    blade dropped flat on the ground in front of him."""
    lean, sink = DEAD[i]
    if lean == 0 and sink == 0:
        return des.copy()
    figure = des.copy()
    figure[sm] = 0
    figure = loose_outline(figure)
    if lean == "rot":
        r = np.rot90(figure)                                  # on his back, the head to the left
        ys, xs = np.nonzero(r[..., 3])
        out = np.zeros_like(des)
        over(out, r[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 64 - (xs.max() - xs.min() + 1) // 2 - 4,
             99 - (ys.max() - ys.min()))
    else:
        out = sheared(figure, lean, sink)
    s = blade(des, sm, (78, 97), 180)
    ys = np.nonzero(s[..., 3].any(1))[0]
    s = np.roll(s, 99 - ys.max(), 0)
    return over(out, s)


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def build():
    with open(lp(CELLS), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    des = design()
    sm = sword_mask(des)
    out = {}
    for tag in TAGS:
        if tag in CODEX:
            continue
        frs = cells["tags"][tag]
        cols, rows = layout(len(frs))
        sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
        for i, fr in enumerate(frs):
            a = frame(tag, i, des, sm)
            px, py = fr["pivot"]
            X, Y = (i % cols) * cw, (i // cols) * ch
            cell = np.zeros((ch, cw, 4), np.uint8)
            over(cell, a, px - PIVOT[0], py - PIVOT[1])
            sheet[Y:Y + ch, X:X + cw] = cell
        out[tag] = sheet
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    same = True
    for tag, a in build().items():
        big = np.repeat(np.repeat(a, Z, 0), Z, 1)
        path = os.path.join(OUT, f"aatrox_{tag}.png")
        if args.check:
            same &= np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")), big)
        else:
            Image.fromarray(big).save(lp(path))
        print(tag, a.shape)
    if args.check:
        print("same" if same else "DIFFERS")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()

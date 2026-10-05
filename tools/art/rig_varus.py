#!/usr/bin/env python3
"""Varus's action strips posed from the approved design's own parts (2026-10-05): the casting body = the idle's.

    python tools/art/rig_varus.py [--check] [--review DIR]

Codex's step-2 delivery (assets/source/varus/codex_strips/) rearranged the design's parts by script: the shooting arm
a pale skin plank to the bow, loose specks left under the bow, the bow in E turned into a broken stick of specks and
lying in the death as a dotted line, the Q bow no different from the attack's, stick legs in the run, the R crouch
and the kneel. The user: 「codex交付了 有奇怪的地方你帮我修复好」. Here every frame is the design
(tools/art/design_varus.py) with only what the action moves moved, the way league_twistedfate's, league_lissandra's and
league_ryze's arms were posed (tools/art/rig_twistedfate.py):
- the parts (work/vr/parts_vr.py shows them): BOW (the crescent right of the body), BOW_ARM (image right, the far arm:
  its crimson forearm and the hand on the grip) and DRAW_ARM (image left, the near arm: its crimson forearm and purple
  clawed hand under the tattooed shoulder, which stays on the body) are taken off the design; the legs (NEAR_LEG image
  left, FAR_LEG image right) stay on it except in the run, the R lunge and the kneel.
- the arms are posed as two bones (rig_twistedfate.place_bone: within 45 degrees of straight down a bone keeps its rows
  and shifts each by its slope, pointing across it is quarter-turned, near 45 degrees a square wider) from strips in the
  design's own colours: UPPER the pale arm (2 squares), FORE the crimson forearm and the purple clawed hand with its
  violet glint; the bow arm lies behind the body, the draw arm in front.
- the bow moves whole with the bow hand (its grip on the hand), turned by RotSprite only in E (45 degrees up) and in the
  death (falling, then lying: a quarter turn); a 1-square string (the bow's darkest purple) runs from its tips to the
  draw hand while he draws, straight between the tips otherwise; in the Q's charge the bow glows (each purple one shade
  lighter, GLOW, two steps).
- attack / Q / E stand on the design's legs; the whole figure (legs included) steps a column back on the full draw and
  forward at the release (league_sivir's attack: never the upper body alone over the legs).
- the run (League's run, 1.07 s, 8 frames): the legs sheared about the hip like league_twistedfate's walk (the lead foot
  changes each half cycle), the upper body a row lower at each contact, the draw arm swinging, the bow carried low.
- R (League's crouch and throw): the legs spread into a lunge (the near one back, the far one forward, sheared about the
  hip) with the body a row or two lower, the bow arm swept back then thrust forward to the right at chest height.
- the death (League's: the darkin bow leaves him): struck back a column, the draw hand to his chest, the bow falls from
  the bow hand and lies flat in front of him, he sinks to his knees (the thighs' rows taken out, everything above
  lowered with them) and the head bows a row.
Every built frame is finished alike (rig_twistedfate.finish): pinholes filled, the outline closed round the moved edges,
stray crumbs dropped. Writes assets/source/native/varus_<tag>.png (8x, 128x96 cells) and varus_cells.json; then
tools/art/import_native.py. --check compares instead of writing; --review writes review sheets.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rig_twistedfate as T  # noqa: E402

NATIVE = T.NATIVE
DESIGN = os.path.join(NATIVE, "varus_native.png")
Z = 8
PIVOT = (64, 88)
SOLES = 99
OUT = (0x0B, 0x04, 0x10)
CELL = (128, 96)
CELL_PIVOT = (64, 70)            # the soles on cell row 81 (the references' feet line)
TAGS = ["idle", "run", "attack", "skill", "skill_quick", "skill2", "ult", "hit", "dead"]
MS = {"idle": [200] * 6, "run": [133] * 8, "attack": [70, 80, 80, 70, 60, 40],
      "skill": [100, 150, 250, 300, 300, 80, 87], "skill_quick": [100, 150, 150, 80, 87],
      "skill2": [80, 87, 80, 80, 73], "ult": [120, 130, 90, 80, 80], "hit": [100, 100],
      "dead": [100, 110, 110, 120, 130, 150, 200, 300]}

RGB = {"o": OUT, "k": (0xE6, 0xB9, 0x9A), "h": (0xC1, 0x8D, 0x7D), "m": (0xFC, 0xDB, 0xB2), "c": (0xD3, 0x20, 0x87),
       "6": (0x89, 0x08, 0x51), "9": (0xA1, 0x12, 0xF7), "3": (0x3B, 0x18, 0x5F), "d": (0xCA, 0x2B, 0xFB),
       "8": (0x65, 0x24, 0x93), "1": (0x26, 0x14, 0x32)}
RED = {(0x64, 0x00, 0x05), (0x9D, 0x04, 0x0A), (0xF0, 0x1A, 0x1A)}   # the scarf's reds (not the draw arm)
STRING = RGB["1"]
ARROW, ARROW_TIP = (0xE8, 0x38, 0xF3), (0xE5, 0xE7, 0xFB)   # the nocked arrow: magenta shaft, white-lilac head
# the arm strips, (along, across) -> letter: along the bone from its joint, across + to the image-right side
UPPER = {(a, c): k for a in range(4) for c, k in ((-1, "o"), (0, "k"), (1, "h"), (2, "o"))}
FORE = {**{(a, c): k for a in range(3) for c, k in ((-1, "o"), (0, "c"), (1, "6"), (2, "o"))},
        (3, -1): "o", (3, 0): "9", (3, 1): "3", (3, 2): "o",
        (4, -1): "o", (4, 0): "d", (4, 1): "8", (4, 2): "3", (4, 3): "o",
        (5, 0): "o", (5, 1): "9", (5, 2): "o", (6, 1): "o"}
DRAW_SH = (55, 80)               # the draw arm's shoulder (under the tattooed deltoid, which stays on the body)
BOW_SH = (66, 78)                # the bow arm's shoulder: the torso's upper right corner under the scarf (at row 80 the
                                 # arm grew out of the medallion - the user: 「手臂连接处看起来做的也不好 很怪」)
GRIP = (70, 85)                  # where the bow hand holds the bow, on the design canvas
GLOW = {(0x3B, 0x18, 0x5F): (0x65, 0x24, 0x93), (0x65, 0x24, 0x93): (0xA1, 0x12, 0xF7),
        (0xA1, 0x12, 0xF7): (0xCA, 0x2B, 0xFB), (0xCA, 0x2B, 0xFB): (0xE8, 0x38, 0xF3),
        (0x52, 0x04, 0xBA): (0xA1, 0x12, 0xF7), (0x26, 0x14, 0x32): (0x3B, 0x18, 0x5F)}
HIP, ANKLE = 88, 96
# the hip's right side under the bow arm was two squares narrower than the far leg below it: a notch the raised
# arm left open (the user: 「腰和腿的这里 要不要补像素块」) - filled in the hip's dark purple, inside the idle's outline
# (the waist row above it in the belly's crimson - 「腰这里少一块？」 - and a column of outline outside, which the
# completion does not add beside such dark squares)
HIP_FILL = {(85, 65): (0x89, 0x08, 0x51), (85, 66): (0x89, 0x08, 0x51),
            (86, 65): (0x26, 0x14, 0x32), (86, 66): (0x26, 0x14, 0x32), (87, 65): (0x26, 0x14, 0x32),
            (87, 66): (0x26, 0x14, 0x32), (88, 65): (0x26, 0x14, 0x32), (88, 66): (0x26, 0x14, 0x32),
            (85, 67): OUT, (86, 67): OUT, (87, 67): OUT, (88, 67): OUT}
NEAR_ANKLE, FAR_ANKLE = 58.5, 67.0
BOOTS = 95
HEAD_ROWS = (60, 73)

# standing actions per frame: dict(bow=(up, fore) | None, draw=(up, fore) | None, string="draw"|"rest"|None,
# dx=whole-figure columns, glow=0..2, rot=bow degrees counter-clockwise (+ = top toward the left), lunge=(near, far,
# drop) leg shear, None = the design)
A_LEVEL = (80, 90)
D_REACH, D_FULL, D_LOOSE, D_FOLLOW, D_DOWN = (-15, 70), (-135, 65), (-125, -150), (-95, -125), (-25, -15)
POSES = {
    # League / oppi's Varus: the bow lights up while he draws and a glowing arrow lies on the string (oppi draws it in the
    # sprite); the release frame shows the string straight and the arrow gone
    "attack": [dict(bow=A_LEVEL, draw=D_REACH, string="rest", glow=1),
               dict(bow=A_LEVEL, draw=D_FULL, string="draw", dx=-1, glow=1, arrow=True),
               dict(bow=A_LEVEL, draw=D_LOOSE, string="rest", dx=1, glow=2),
               dict(bow=A_LEVEL, draw=D_FOLLOW, string="rest", dx=1, glow=1),
               dict(bow=(55, 75), draw=D_DOWN, string="rest"),
               None],
    # Q: League's (and oppi's) charge is a low wide archer's stance - the legs spread into a lunge while he draws and holds
    "skill": [dict(bow=A_LEVEL, draw=D_REACH, string="rest", lunge=(-2, 2, 1)),
              dict(bow=A_LEVEL, draw=D_FULL, string="draw", lunge=(-3, 3, 1), glow=1, arrow=True),
              dict(bow=A_LEVEL, draw=D_FULL, string="draw", lunge=(-3, 3, 1), glow=2, arrow=True),
              dict(bow=A_LEVEL, draw=D_FULL, string="draw", lunge=(-3, 3, 1), glow=1, arrow=True),
              dict(bow=A_LEVEL, draw=D_FULL, string="draw", lunge=(-3, 3, 1), glow=2, arrow=True),
              dict(bow=A_LEVEL, draw=D_LOOSE, string="rest", lunge=(-3, 3, 1), dx=1, glow=2),
              dict(bow=(55, 75), draw=D_DOWN, string="rest", lunge=(-1, 1, 0))],
    "skill2": [dict(bow=(105, 120), draw=(-30, 100), string="rest", rot=-30, glow=1),
               dict(bow=(120, 135), draw=(-115, 95), string="draw", dx=-1, rot=-45, glow=1, arrow=True),
               dict(bow=(120, 135), draw=(-130, -160), string="rest", dx=1, rot=-45, glow=2),
               dict(bow=(110, 125), draw=(-100, -130), string="rest", rot=-40),
               None],
    "ult": [dict(bow=(30, 55), draw=(-40, -60), lunge=(-3, 2, 1), rot=15),
            dict(bow=(60, 75), draw=(-50, -70), lunge=(-4, 3, 2), dx=1),
            dict(bow=(85, 90), draw=(-60, -80), lunge=(-5, 4, 2), dx=2),
            dict(bow=(85, 90), draw=(-55, -75), lunge=(-5, 4, 2), dx=2),
            None],
    "hit": [dict(dx=-1, keep_arms=True), None],
}
POSES["skill_quick"] = [POSES["skill"][i] for i in (0, 1, 2, 5, 6)]
# the run: leg swing (the near ankle's offset; the far one opposite), lifted boots, the drop, the draw arm
SWING = [4.0, 2.0, 0.0, -2.0, -4.0, -2.0, 0.0, 2.0]
NEAR_LIFT = [0, 0, 0, 0, 0, 1, 2, 1]
FAR_LIFT = [0, 1, 2, 1, 0, 0, 0, 0]
DROP = [1, 1, 0, 0, 1, 1, 0, 0]
RUN_DRAW = [(-25, -15), (-18, -10), (-8, -4), (2, 6), (12, 18), (2, 6), (-8, -4), (-18, -10)]
# the death: (dx, draw arm, bow: "hand" | ("fall", degrees, (x, y)) | ("lie", (x, y)), kneel rows, head dip)
DEAD = [(-1, (-15, -25), "hand", 0, 0),
        (-1, (10, 120), "hand", 0, 0),
        (-1, (10, 120), ("fall", -50, (78, 86)), 0, 0),
        (0, (10, 120), ("lie", (80, 99)), 2, 0),
        (0, (5, 110), ("lie", (80, 99)), 4, 0),
        (0, (0, 100), ("lie", (80, 99)), 6, 1),
        (0, (0, 100), ("lie", (80, 99)), 6, 1),
        (0, (0, 100), ("lie", (80, 99)), 6, 1)]


def lp(p):
    return T.lp(p)


def design():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        op = d[..., 3] > 0
        R, C = np.mgrid[0:128, 0:128]
        self.bow_m = op & (R >= 64) & (((C >= 70) & (R <= 92)) | ((C >= 71) & (R > 92)))
        self.bow_arm_m = op & (R >= 81) & (R <= 87) & (C >= 66) & (C <= 69)
        draw = np.zeros_like(op)
        for y in range(81, 93):
            # from row 88 down only the hand (cols 51-56): column 57 there is the near thigh's outline (design_varus FIX)
            for x in (range(52, 58) if y < 88 else range(51, 57)):
                if op[y, x] and tuple(int(v) for v in d[y, x, :3]) not in RED:
                    draw[y, x] = True
        self.draw_m = draw
        self.near_leg = op & (R >= 89) & (C >= 56) & (C <= 62)
        self.far_leg = op & (R >= 89) & (C >= 63) & (C <= 70) & ~self.bow_m
        self.bow = np.zeros_like(d)
        self.bow[self.bow_m] = d[self.bow_m]
        ys, xs = np.nonzero(self.bow_m)
        top, bot = ys.min(), ys.max()
        self.tips = ((float(xs[ys == top].mean()), float(top)), (float(xs[ys == bot].mean()), float(bot)))
        self.body = d.copy()
        self.body[self.bow_m | self.bow_arm_m | self.draw_m] = 0
        for (y, x), rgb in HIP_FILL.items():         # the hip under the bow arm, flush with the far leg below it
            self.body[y, x] = (*rgb, 255)
        self.body_bow_arm = d.copy()                 # the design without the bow and its hand (the death's empty hand)
        self.body_bow_arm[self.bow_m] = 0
        self.trunk = self.body.copy()
        self.trunk[self.near_leg | self.far_leg] = 0


def arm(shoulder, up, fore):
    """({(x, y): letter}, hand point) of an arm: UPPER `up`, FORE `fore` degrees from the hang (+ toward image right)."""
    cu, end = T.place_bone(UPPER, up)
    sx, sy = shoulder
    out = {(sx + x, sy + y): k for (x, y), k in cu.items()}
    st = T.step_of(fore)
    ex, ey = sx + end[0] + st[0], sy + end[1] + st[1]
    cf, fend = T.place_bone(FORE, fore)
    for (x, y), k in cf.items():
        out[(ex + x, ey + y)] = k
    hand = (ex + int(round(fend[0] * 0.8)), ey + int(round(fend[1] * 0.8)))
    return T.close_gaps(out), hand


def paint(c, cells):
    for (x, y), k in cells.items():
        if 0 <= y < 128 and 0 <= x < 128:
            c[y, x] = (*RGB[k], 255)
    return c


def glowed(s, n):
    s = s.copy()
    for _ in range(n):
        out = s.copy()
        for src, dst in GLOW.items():
            m = (s[..., 3] > 0) & (s[..., :3] == np.array(src, np.uint8)).all(-1)
            out[m, :3] = dst
        s = out
    return s


def rotate_pt(p, j, deg):
    t = math.radians(deg)
    x, y = p[0] - j[0], p[1] - j[1]
    return (j[0] + x * math.cos(t) + y * math.sin(t), j[1] - x * math.sin(t) + y * math.cos(t))


def place_bow(c, P, hand, rot=0, glow=0):
    """The bow with its grip on the hand (turned `rot` degrees counter-clockwise about the grip); its tips."""
    s = glowed(P.bow, glow) if glow else P.bow
    j = (GRIP[0] + 0.5, GRIP[1] + 0.5)
    target = (hand[0] + 1.5, hand[1] + 0.5)
    s2, j2 = T.turned(s, j, rot)
    T.place(c, s2, j2, target)
    return [(t[0] - j[0] + target[0], t[1] - j[1] + target[1]) for t in
            (rotate_pt((x + 0.5, y + 0.5), j, rot) for x, y in P.tips)]


def line(c, p0, p1, rgb, under=True):
    x0, y0 = int(math.floor(p0[0])), int(math.floor(p0[1]))
    x1, y1 = int(math.floor(p1[0])), int(math.floor(p1[1]))
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = int(round(x0 + (x1 - x0) * i / n))
        y = int(round(y0 + (y1 - y0) * i / n))
        if 0 <= x < 128 and 0 <= y < 128 and (not under or not c[y, x, 3]):
            c[y, x] = (*rgb, 255)


def leg_sprite(P, m, dx, drop, lift):
    """The leg sheared about HIP (each row above ANKLE moved in proportion, dropped with the body), the boot from ANKLE
    down moved dx whole and lifted `lift` rows (league_twistedfate's walk)."""
    shin = np.zeros((128, 128, 4), np.uint8)
    boot = np.zeros((128, 128, 4), np.uint8)
    for r, c in zip(*np.nonzero(m)):
        if r < ANKLE:
            sh = int(math.floor(dx * (r - HIP) / (ANKLE - HIP) + 0.5))
            rr, tgt = r + drop, shin
        else:
            sh = int(math.floor(dx + 0.5))
            rr, tgt = r - lift, boot
        if 0 <= rr < 128 and 0 <= c + sh < 128:
            tgt[rr, c + sh] = P.design[r, c]
    return T.put(shin, boot, 0, 0)


def seams(c, shoulder):
    """Outline squares at a shoulder (3 columns either side, 2 rows above to 3 below) lying between two drawn colours
    (left and right, or above and below) take the lighter of them: the arm joins the body without a black seam."""
    sx, sy = shoulder
    op = c[..., 3] > 0
    ink = op & (c[..., :3] == np.array(OUT, np.uint8)).all(-1)
    fix = []
    for y in range(sy - 2, sy + 4):
        for x in range(sx - 3, sx + 4):
            if not ink[y, x]:
                continue
            for (y1, x1), (y2, x2) in (((y, x - 1), (y, x + 1)), ((y - 1, x), (y + 1, x))):
                if op[y1, x1] and op[y2, x2] and not ink[y1, x1] and not ink[y2, x2]:
                    a1, a2 = c[y1, x1], c[y2, x2]
                    lum = lambda q: 0.299 * int(q[0]) + 0.587 * int(q[1]) + 0.114 * int(q[2])
                    fix.append((y, x, a1 if lum(a1) >= lum(a2) else a2))
                    break
    for y, x, col in fix:
        c[y, x] = col
    return c


def standing(P, pose):
    if pose is None:
        return P.design.copy()
    if pose.get("keep_arms"):
        return T.shifted(P.design, pose.get("dx", 0), 0)
    c = np.zeros((128, 128, 4), np.uint8)
    drop = 0
    if pose.get("lunge"):
        near, far, drop = pose["lunge"]
        T.put(c, leg_sprite(P, P.far_leg, far, drop, 0), 0, 0)
        body = T.shifted(P.trunk, 0, drop)
    else:
        body = P.body
    bsh = (BOW_SH[0], BOW_SH[1] + drop)
    dsh = (DRAW_SH[0], DRAW_SH[1] + drop)
    bcells, bhand = arm(bsh, *pose["bow"])
    paint(c, bcells)                                     # the bow arm behind the body
    T.put(c, body, 0, 0)
    if pose.get("lunge"):
        T.put(c, leg_sprite(P, P.near_leg, near, drop, 0), 0, 0)
    tips = place_bow(c, P, bhand, pose.get("rot", 0), pose.get("glow", 0))
    dcells, dhand = arm(dsh, *pose["draw"])
    if pose.get("string") == "draw":
        line(c, tips[0], (dhand[0] + 0.5, dhand[1] + 0.5), STRING)
        line(c, (dhand[0] + 0.5, dhand[1] + 0.5), tips[1], STRING)
    if pose.get("arrow"):
        # from the draw hand through the grip, 4 squares past it: the shaft magenta, the last 2 squares the head
        hx, hy = dhand[0] + 0.5, dhand[1] + 0.5
        gx, gy = bhand[0] + 1.5, bhand[1] + 0.5
        L = math.hypot(gx - hx, gy - hy) or 1.0
        ex, ey = gx + (gx - hx) / L * 4, gy + (gy - hy) / L * 4
        line(c, (hx, hy), (ex, ey), ARROW, under=False)
        line(c, (ex - (gx - hx) / L * 1.2, ey - (gy - hy) / L * 1.2), (ex, ey), ARROW_TIP, under=False)
    elif pose.get("string") == "rest":
        line(c, tips[0], tips[1], STRING)
    paint(c, dcells)                                     # the draw arm in front
    seams(c, bsh)
    seams(c, dsh)
    dx = pose.get("dx", 0)
    return T.shifted(c, dx, 0) if dx else c


def run(P, k):
    s = SWING[k]
    drop = DROP[k]
    c = np.zeros((128, 128, 4), np.uint8)
    T.put(c, leg_sprite(P, P.far_leg, -s * 0.8, drop, FAR_LIFT[k]), 0, 0)
    bcells, bhand = arm((BOW_SH[0], BOW_SH[1] + drop), 20, 75)
    paint(c, bcells)
    T.put(c, T.shifted(P.trunk, 0, drop), 0, 0)
    T.put(c, leg_sprite(P, P.near_leg, s, drop, NEAR_LIFT[k]), 0, 0)
    place_bow(c, P, bhand, 0)
    dcells, _ = arm((DRAW_SH[0], DRAW_SH[1] + drop), *RUN_DRAW[k])
    paint(c, dcells)
    return c


def kneeled(a, n, dip):
    """Everything above the thighs `n` rows lower, the thighs' rows (from HIP+1) taken out; the head `dip` more."""
    if not n and not dip:
        return a
    out = np.zeros_like(a)
    out[HIP + 1 + n:] = a[HIP + 1 + n:]          # the knees, shins and boots stay
    top = a[:HIP + 1].copy()
    if dip:
        head = np.zeros_like(top)
        head[HEAD_ROWS[0]:HEAD_ROWS[1] + 1] = top[HEAD_ROWS[0]:HEAD_ROWS[1] + 1]
        top[HEAD_ROWS[0]:HEAD_ROWS[1] + 1] = 0
        T.put(top, head, 0, dip)
    return T.put(out, top, 0, n)


def dead(P, k):
    dx, draw, bow, kneel, dip = DEAD[k]
    c = np.zeros((128, 128, 4), np.uint8)
    if bow == "hand":
        T.put(c, P.body_bow_arm, 0, 0)
        place_bow(c, P, (GRIP[0] - 1, GRIP[1]))
        c[P.draw_m] = 0
    else:
        T.put(c, P.body, 0, 0)
        bcells, _ = arm(BOW_SH, 25, 35)
        paint(c, bcells)
    dcells, _ = arm(DRAW_SH, *draw)
    paint(c, dcells)
    c = kneeled(c, kneel, dip)
    if isinstance(bow, tuple):
        s = P.bow
        j = (GRIP[0] + 0.5, GRIP[1] + 0.5)
        if bow[0] == "fall":
            s2, j2 = T.turned(s, j, bow[1])
            T.place(c, s2, j2, bow[2], under=True)
        else:
            s2, j2 = T.turned(s, j, -90)
            ys = np.nonzero(s2[..., 3].any(1))[0]
            low = ys.max() + 0.5 - j2[1]
            T.place(c, s2, j2, (bow[1][0], bow[1][1] + 0.5 - low), under=True)
    return T.shifted(c, dx, 0) if dx else c


def thin_outline(a):
    """Outline squares on the silhouette (a clear square beside them) whose drawn 4-neighbours are all outline go: the
    outer layer of a double ring, where an arm taken off left its own outline beside the body's (the hip under the
    bow arm read as a black slab - the user: 「这里又是黑的啊」). The completion then closes one ring again."""
    a = a.copy()
    op = a[..., 3] > 0
    ink = op & (a[..., :3] == np.array(OUT, np.uint8)).all(-1)
    gone = []
    for y, x in zip(*np.nonzero(ink)):
        nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if all(op[q] for q in nb):
            continue
        drawn = [q for q in nb if op[q]]
        if drawn and all(ink[q] for q in drawn):
            gone.append((y, x))
    for q in gone:
        a[q] = 0
    return a


def finish(a):
    T.OUT = OUT
    T.SOLES = SOLES
    return T.finish(thin_outline(a))


def frames(P, tag):
    if tag == "idle":
        return [P.design.copy() for _ in MS[tag]]
    if tag == "run":
        return [finish(run(P, k)) for k in range(len(MS[tag]))]
    if tag == "dead":
        return [finish(dead(P, k)) for k in range(len(MS[tag]))]
    return [finish(standing(P, p)) if p is not None else P.design.copy() for p in POSES[tag]]


def sheet(frs):
    T.CELL, T.PIVOT, T.CELL_PIVOT = CELL, PIVOT, CELL_PIVOT
    return T.sheet(frs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write review sheets to this folder")
    ap.add_argument("--out", default=NATIVE)
    a = ap.parse_args()
    P = Parts()
    built = {tag: frames(P, tag) for tag in TAGS}
    bad = 0
    for tag in TAGS:
        big = Image.fromarray(np.repeat(np.repeat(sheet(built[tag]), Z, 0), Z, 1))
        path = os.path.join(a.out, f"varus_{tag}.png")
        if a.check:
            same = os.path.exists(lp(path)) and np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")),
                                                                np.asarray(big))
            print(tag, "same" if same else "DIFFERS")
            bad += not same
        else:
            big.save(lp(path))
        print(f"{tag}: {len(built[tag])} frames, pieces {[len(T.pieces(f)) for f in built[tag]]}")
    cells = {"cell": list(CELL), "scale": Z,
             "tags": {tag: [{"pivot": list(CELL_PIVOT), "ms": ms} for ms in MS[tag]] for tag in TAGS}}
    cpath = os.path.join(a.out, "varus_cells.json")
    text = json.dumps(cells, indent=1) + "\n"
    if a.check:
        same = os.path.exists(lp(cpath)) and open(lp(cpath), encoding="utf-8").read() == text
        print("cells", "same" if same else "DIFFERS")
        bad += not same
    else:
        with open(lp(cpath), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    if a.review:
        T.DESIGN = DESIGN
        T.SOLES = SOLES
        T.review(P, built, a.review)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

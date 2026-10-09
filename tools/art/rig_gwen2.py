#!/usr/bin/env python3
"""Gwen's action strips posed from design 2 (the scissors carried on her shoulder, design_gwen2.py).

    python tools/art/rig_gwen2.py [--check] [--review DIR] [--tags attack,skill]

rig_gwen.py's way on the new design: the body is the design with the scissors lifted off (the blade over her
shoulder, the pivot screw, the handle) wherever she holds them out; the far arm (image right) leaves its shoulder as
a straight two-square arm in the design's skin and glove, the scissors in that hand drawn by code at any angle (a
long cyan blade from the screw, the screw, the shaft forking to two upright heart loops with see-through holes);
the free near arm (image left, akimbo in the idle) swings for R's needles. The run is League's skip (crouch, one
foot kicked up behind, the feet taking turns: 「左右脚来回切换单脚蹦跶着走」), the death league_sivir's (struck, knocked,
turned about the feet, lying on her back, the scissors on the ground). Hole marker Z (#ff00ff) rides through as a
colour; clean_gwen.py clears it after the import's outline pass.
Writes assets/source/native/gwen_<tag>.png (8x, 128x96 cells) and gwen_cells.json; then tools/art/import_native.py.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_gwen2 as DG  # noqa: E402
import rig_nocturne as RN  # noqa: E402
import rigkit as K  # noqa: E402
import strips  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
HERO = "gwen"
PIVOT = (64, 88)
CELL, CELL_PIVOT = (128, 96), (64, 70)
SOLES = 99
MS = {"idle": [200] * 6, "run": [150] * 8, "attack": [60, 60, 70, 70, 80, 100],
      "skill": [50, 60, 60, 60, 60, 70, 80, 100], "skill2": [40, 40, 40, 60, 80, 80, 80, 100],
      "ult": [50, 60, 60, 70, 80, 100], "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}
TAGS = list(MS)

# ------------------------------------------------------------------------------------------------ the design's parts
# letters: design_gwen2's palette (A outline, O/L/I/F the hair's and the blade's blues, V/Y/X the blade's light,
# W/T skin, R blush, E/K/C the gloves and sleeves, X/U the screw, Z the hole marker)
SKIN_LIT, SKIN_SHADE, GLOVE_LIT, GLOVE_SHADE = "W", "T", "K", "E"
HAIR = "OLIF"
BLADE_ROWS = {y: (0, 58) for y in range(50, 62)}      # the blade on her shoulder: (first, last column) per row
BLADE_ROWS.update({62: (54, 56), 63: (54, 56), 64: (55, 55)})
BLADE_FILL = {(57, 62): "A"}                          # the head's outline where the blade covered it
SCREW = (72, 75, 71, 73)                              # rows, columns of the pivot screw
HANDLE_ROWS = (75, 91)                                # the handle: these rows, columns >= HANDLE_COL
HANDLE_COL = 70
SHAFT = [(76, 72), (76, 73)]                          # (row, column) of the shaft squares left of HANDLE_COL
FAR_OFF = {75: (69, 70), 76: (67, 73), 77: (63, 73), 78: (63, 73), 79: (66, 73)}   # the far arm, the glove, the shaft, and the
# ringlet's tail on the shoulder (hidden by the handle in the idle; alone over the moved arm it hung oddly: 「头发这里要好好处理」)
FAR_FILL = {77: (63, "CC"), 78: (63, "C")}            # the bodice's edge under it
FAR_SH = (65, 77)                                     # the far arm's first square (top-left of its cross-section)
NEAR_OFF = {80: (56, 60), 81: (56, 60), 82: (56, 60), 83: (56, 60), 84: (56, 60)}   # the akimbo arm
NEAR_FILL = {80: (61, "C"), 81: (61, "C"), 82: (61, "C"), 83: (61, "C")}
NEAR_SH = (59, 79)
ARM_STEPS, GLOVE_STEPS = 4, 2
HAIR_ROWS = (56, 89)
BOWS = ((65, 70, 52, 55), (64, 71, 70, 73))          # rows, cols: the bows count as hair (the raised blade over them)
DRILL_L = (72, 89, 48, 57)                            # the left ringlet's box (the run's trailing curl)
DRILL_R = (72, 77, 66, 70)                            # the right ringlet's box (in front of the far shoulder)
LEG_TOP, LEG_SPLIT = 90, 64
KNEE_ROW, BOOT_ROW, FOOT_ROW = 93, 95, 97
SC_LEN, SC_OPEN = 25, 44
FACE_BOX = (70, 77, 60, 70)                           # rows, cols kept by the inner-ink softening


class Parts:
    def __init__(self):
        D = K.Design(DG.OUT)
        self.D = D
        can, pal = DG.read()
        if not np.array_equal(can, D.a):
            raise SystemExit("gwen_native.png differs from design_gwen2: run tools/art/design_gwen2.py first")
        self.L = pal
        self.rgba = {k: np.array(tuple(c) + (255,), np.uint8) for k, c in pal.items()}
        inv = {tuple(v): k for k, v in pal.items()}
        self.let = np.full(can.shape[:2], ".", dtype="<U1")
        for y, x in zip(*np.nonzero(can[..., 3] > 0)):
            self.let[y, x] = inv.get(tuple(int(v) for v in can[y, x, :3]), "?")
        sc = np.zeros(can.shape[:2], bool)
        for y, (x0, x1) in BLADE_ROWS.items():
            sc[y, x0:x1 + 1] = True
        r0, r1, c0, c1 = SCREW
        sc[r0:r1 + 1, c0:c1 + 1] = True
        sc[HANDLE_ROWS[0]:HANDLE_ROWS[1] + 1, HANDLE_COL:] = True
        for y, x in SHAFT:
            sc[y, x] = True
        sc &= can[..., 3] > 0
        self.sc = sc
        self.scissors = np.zeros_like(can)
        self.scissors[sc] = can[sc]
        body = can.copy()
        body[sc] = 0
        for (x, y), ch in BLADE_FILL.items():
            body[y, x] = self.rgba[ch]
        self.body = body
        self.hair = np.zeros(can.shape[:2], bool)
        for y, x in zip(*np.nonzero(body[..., 3] > 0)):
            if HAIR_ROWS[0] <= y <= HAIR_ROWS[1] and self.let[y, x] in HAIR:
                self.hair[y, x] = True
        for r0, r1, c0, c1 in BOWS:
            self.hair[r0:r1 + 1, c0:c1 + 1] |= body[r0:r1 + 1, c0:c1 + 1, 3] > 0
        self.drill_l = np.zeros_like(self.hair)
        r0, r1, c0, c1 = DRILL_L
        self.drill_l[r0:r1 + 1, c0:c1 + 1] = (body[r0:r1 + 1, c0:c1 + 1, 3] > 0)
        self.drill_r = np.zeros_like(self.hair)
        r0, r1, c0, c1 = DRILL_R
        self.drill_r[r0:r1 + 1, c0:c1 + 1] = self.hair[r0:r1 + 1, c0:c1 + 1]
        self.hair &= ~self.drill_r                      # the right ringlet hangs in front of the far shoulder
        self.keep = None
        dh = np.zeros(can.shape[:2], bool)              # the design's enclosed clear squares, a row up and down too
        for comp in K.holes(can):                       # (the breathing idle sinks the top a row)
            for y, x in comp:
                dh[max(y - 1, 0):y + 2, x] = True
        self.design_hole = dh


# ------------------------------------------------------------------------------------------------ the scissors
def blade(layer, p0, p1, w0, P):
    """A blade from p0 to p1, w0 wide at p0 tapering to a point: light edge, mid, blue lower third."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    n = np.linalg.norm(d)
    u = d / n
    v = np.array([-u[1], u[0]])
    if v[1] > 0:
        v = -v
    for y in range(layer.shape[0]):
        for x in range(layer.shape[1]):
            q = np.array([x + 0.5, y + 0.5]) - p0
            t, s = q @ u / n, q @ v
            if not 0 <= t <= 1:
                continue
            half = max(0.5, w0 / 2 * (1 - t) + 0.5 * t)
            if abs(s) <= half:
                layer[y, x] = P.rgba["O" if s > half * 0.35 else ("L" if s > -half * 0.35 else "I")]


LOOP = [".AA.AA.", "AOOAOLA", "AOZOZLA", "AOZZZLA", ".ALZLA.", "..ALA..", "...A..."]
SCREW_SPR = ["AAA", "AXU", "AUU", "AAA"]


def handle_frame(deg):
    t = math.radians(deg)
    u = np.array([math.cos(t), math.sin(t)])
    h = -u
    n = np.array([-h[1], h[0]])
    if n[1] < 0 or (abs(n[1]) < 1e-9 and n[0] < 0):
        n = -n
    return u, h, n


def scissors_unit(P, deg, length=SC_LEN, opening=0):
    """The scissors as a part with its joint on the hand (the shaft just under the screw): the blade along `deg`
    (0 right, 90 down) from the screw, or two blades opening/2 either side; the screw; the shaft back to a fork and
    an arm to each heart loop, the loops upright at any angle (hearts), their holes the marker."""
    N = 2 * length + 40
    c = np.zeros((N, N, 4), np.uint8)
    u, h, n = handle_frame(deg)
    pv = np.array([N / 2, N / 2])
    hand = pv + 8.0 * h                       # the hand between the two loops (fingers in them)
    if opening:
        for sgn in (1, -1):
            a = math.radians(deg) + sgn * math.radians(opening / 2)
            w = np.array([math.cos(a), math.sin(a)])
            blade(c, tuple(pv + 1.5 * w), tuple(pv + length * w), 2.8, P)
    else:
        blade(c, tuple(pv + 1.5 * u), tuple(pv + length * u), 3.4, P)
    fork = pv + 5.0 * h
    blade(c, tuple(pv), tuple(fork), 2.0, P)
    for sgn in (1, -1):
        rc = fork + 3.0 * h + sgn * 3.5 * n
        blade(c, tuple(fork), tuple(rc), 1.6, P)
        x0, y0 = int(math.floor(rc[0] - 3.5 + 0.5)), int(math.floor(rc[1] - 3.5 + 0.5))
        for j, row in enumerate(LOOP):
            for i, ch in enumerate(row):
                if ch != ".":
                    c[y0 + j, x0 + i] = P.rgba[ch]
    sx, sy = int(math.floor(pv[0] - 1.5 + 0.5)), int(math.floor(pv[1] - 2 + 0.5))
    for j, row in enumerate(SCREW_SPR):
        for i, ch in enumerate(row):
            c[sy + j, sx + i] = P.rgba[ch]
    can, _, _ = strips.complete_outline(np.pad(c, ((1, 1), (1, 1), (0, 0))), color=tuple(P.L["A"]), feet=N + 2)
    c = can[1:-1, 1:-1]
    ys, xs = np.nonzero(c[..., 3] > 0)
    s = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    return K.Part(s, (hand[0] - xs.min(), hand[1] - ys.min()))


# ------------------------------------------------------------------------------------------------ drawing
def arm_cells(P, sh, deg, steps=ARM_STEPS, glove=GLOVE_STEPS):
    """A straight arm from the shoulder square `sh`, `deg` from hanging (+90 image right, -90 left, 180 up), two
    squares across (lit, shade), the glove's last steps; its outline ring, its colour squares and the hand."""
    t = math.radians(deg)
    dx, dy = math.sin(t), math.cos(t)
    horiz = abs(dx) > abs(dy) + 1e-9
    cells = {}
    for i in range(steps + glove):
        if horiz:
            x = sh[0] + i * (1 if dx > 0 else -1)
            y = int(math.floor(sh[1] + i * dy / abs(dx) + 0.5))
            sq = [(x, y), (x, y + 1)]
        else:
            y = sh[1] + i * (1 if dy > 0 else -1)
            x = int(math.floor(sh[0] + i * dx / abs(dy) + 0.5))
            sq = [(x, y), (x + 1, y)]
        g = i >= steps
        for k, q in enumerate(sq):
            cells[q] = (GLOVE_LIT if k == 0 else GLOVE_SHADE) if g else (SKIN_LIT if k == 0 else SKIN_SHADE)
        hand = (sq[0][0] + sq[1][0]) / 2 + 0.5, (sq[0][1] + sq[1][1]) / 2 + 0.5
    add = {}
    for (x, y), ch in cells.items():
        for ox, oy in K.N4:
            q, q2 = (x + ox, y + oy), (x + 2 * ox, y + 2 * oy)
            if q not in cells and q not in add and cells.get(q2) == ch:
                add[q] = ch
    cells.update(add)
    ring = {}
    for (x, y) in cells:
        for ox, oy in K.N4:
            q = (x + ox, y + oy)
            if q not in cells:
                ring[q] = P.rgba["A"]
    return ring, {q: P.rgba[ch] for q, ch in cells.items()}, hand


def part_cells(part, at):
    ox = int(math.floor(at[0] - part.j[0] + 1e-9))
    oy = int(math.floor(at[1] - part.j[1] + 1e-9))
    ys, xs = np.nonzero(part.s[..., 3])
    return {(int(x) + ox, int(y) + oy): part.s[y, x].copy() for y, x in zip(ys, xs)}


def put_cells(c, cells, ok=None):
    for (x, y), v in cells.items():
        if 0 <= y <= SOLES and 0 <= x < c.shape[1] and (ok is None or ok(x, y)):
            c[y, x] = v


def fill(P, a, spec):
    for y, (x0, s) in spec.items():
        for i, ch in enumerate(s):
            a[y, x0 + i] = P.rgba[ch]


def clear(a, spec):
    for y, (x0, x1) in spec.items():
        a[y, x0:x1 + 1] = 0


def shifted(a, dx, dy):
    return K.shifted(a, dx, dy) if (dx or dy) else a


NEEDLE = "XXUUUUQ"
FAN = (-35, 0, 35)
LOOSE = (-12, 0, 12)


def needles(P, hand, held):
    hx, hy = hand[0] - 0.5, hand[1] - 0.5
    if held == "fan":
        dirs, d0 = [(math.sin(math.radians(a)), -math.cos(math.radians(a))) for a in FAN], 1
    else:
        dirs, d0 = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in LOOSE], 3
    cells = {}
    for dx, dy in dirs:
        for i, ch in enumerate(reversed(NEEDLE)):
            d = d0 + i
            q = (int(math.floor(hx + d * dx + 0.5)), int(math.floor(hy + d * dy + 0.5)))
            if q not in cells or ch in "XU":
                cells[q] = P.rgba[ch]
    ring = {}
    for (x, y) in cells:
        for ox, oy in K.N4:
            q = (x + ox, y + oy)
            if q not in cells:
                ring[q] = P.rgba["A"]
    ring.update(cells)
    return ring


# ------------------------------------------------------------------------------------------------ standing actions
# per frame: "far": (arm degrees, scissors degrees, opening) - the scissors in the far hand, off her shoulder;
# "near": (arm degrees, "fan" / "loose" / None) - the free near arm; "move": (dx, dy); "leap": the run frame
STAND = {
    "attack": [{"move": (-1, 0)}, {"far": (35, 160, 0), "move": (-1, 0)}, {"far": (45, 20, 0)},
               {"far": (60, 0, 0), "move": (2, 0)}, {"far": (50, 10, 0), "move": (1, 0)}, {}],
    "skill": [{"far": (45, 25, 0)}, {"far": (60, 0, SC_OPEN)}, {"far": (60, 0, 0)}, {"far": (60, 0, SC_OPEN)},
              {"far": (60, 0, 0)}, {"far": (60, 0, 70), "move": (2, 0)}, {"far": (60, 0, 0), "move": (1, 0)}, {}],
    "skill2": [{"leap": 0, "move": (1, 0)}, {"leap": 6, "move": (3, -2)}, {"leap": 7, "move": (2, 0)}, {},
               {"far": (45, -45, 0)}, {"far": (60, -70, 0)}, {"far": (45, -45, 0)}, {}],
    "ult": [{"near": (-30, None), "move": (-1, 0)}, {"near": (-150, "fan"), "move": (-2, 0)},
            {"near": (-160, "fan"), "move": (-2, 0)}, {"near": (100, None), "move": (2, 0)},
            {"near": (70, None), "move": (1, 0)}, {}],
    "hit": [{"move": (-2, 0)}, {"move": (-1, 0)}],
}


def stand(P, pose):
    far, near = pose.get("far"), pose.get("near")
    a = P.body.copy()
    if far is None:
        K.put(a, P.scissors, 0, 0)                                 # the scissors on her shoulder as drawn
    else:
        clear(a, FAR_OFF)
        fill(P, a, FAR_FILL)
    if near is not None:
        clear(a, NEAR_OFF)
        fill(P, a, NEAR_FILL)
    body = a[..., 3] > 0
    ink = (a[..., :3] == P.rgba["A"][:3]).all(-1) & body
    hair = P.hair
    under = lambda x, y: not body[y, x] or hair[y, x]              # noqa: E731
    clear_ok = lambda x, y: not body[y, x] or ink[y, x] or hair[y, x]   # noqa: E731  (the near arm's ring: over
    #                                                                  the hair too, never over the body's colours)
    c = a.copy()
    keep = np.zeros(a.shape[:2], bool)
    if far is None:
        keep |= P.sc
    else:
        deg, sdeg, opening = far
        ring, col, hand = arm_cells(P, FAR_SH, deg)
        sc = part_cells(scissors_unit(P, sdeg, opening=opening), hand)
        forward = -90 < sdeg < 90                                  # pointing away from her: the pair in front of her
        sc_ok = (lambda x, y: True) if forward else under
        put_cells(c, ring, under)
        put_cells(c, sc, sc_ok)
        for (x, y) in sc:
            if 0 <= y < 128 and 0 <= x < 128 and sc_ok(x, y):
                keep[y, x] = True
        put_cells(c, col, under)
        glove = {q: v for q, v in col.items() if (v[:3] == P.rgba[GLOVE_LIT][:3]).all()
                 or (v[:3] == P.rgba[GLOVE_SHADE][:3]).all()}
        put_cells(c, glove, lambda x, y: not P.drill_r[y, x])
    if near is not None:
        deg, held = near
        ring, col, hand = arm_cells(P, NEAR_SH, deg)
        put_cells(c, ring, clear_ok)
        put_cells(c, col)
        if held:
            nd = needles(P, hand, held)
            put_cells(c, nd)
            for (x, y) in nd:
                if 0 <= y < 128 and 0 <= x < 128:
                    keep[y, x] = True
    c[SOLES + 1:] = 0
    dx, dy = pose.get("move", (0, 0))
    k4 = np.zeros(a.shape, np.uint8)
    k4[keep] = 255
    P.keep = shifted(k4, dx, dy)[..., 3] > 0
    return shifted(c, dx, dy)


# ------------------------------------------------------------------------------------------------ the run (a skip)
# one leg's 8 phases (knee columns, ankle columns from the hip, rows lifted), League's run: kicked up behind,
# landing ahead, planted, crouch, supporting, planted, planted, crouch; the other leg half a cycle later
CYCLE = [(0, -3, 4), (1, 2, 0), (0, 1, 0), (1, 1, 0), (0, 0, 0), (0, -1, 0), (0, -1, 0), (1, 0, 0)]
CYCLE_FAR = list(CYCLE)
CYCLE_FAR[0] = (0, -1, 5)                   # the far leg's kick beside the near leg (kicked straight back it hid)
BOB = [0, 0, 0, 2, 0, 0, 0, 2]              # the body two rows down at the two crouches
HOP = [0] * 8                               # (V4 would lift the figure a row at the kicks)
HIP_IN = {"near": 1, "far": -1}
SWAY = [0, -1, -1, 0, 0, -1, -1, 0]


def bent(leg, knee, ankle, lift, hip_in=0):
    out = np.zeros_like(leg)
    for y in range(LEG_TOP, SOLES + 1):
        inward = hip_in * min(1.0, (y - LEG_TOP) / (KNEE_ROW - LEG_TOP))
        if y <= KNEE_ROW:
            dx = knee * (y - LEG_TOP) / (KNEE_ROW - LEG_TOP)
        elif y < BOOT_ROW:
            dx = knee + (ankle - knee) * (y - KNEE_ROW) / (BOOT_ROW - KNEE_ROW)
        else:
            dx = ankle
        dx += inward
        dx = int(math.floor(dx + 0.5))
        row = leg[y]
        ty = y - lift
        if dx >= 0:
            out[ty, dx:] = np.maximum(out[ty, dx:], row[:row.shape[0] - dx]) if dx else row
        else:
            out[ty, :dx] = row[-dx:]
    return out


def run_parts(P):
    full = P.body.copy()
    K.put(full, P.scissors, 0, 0)
    upper = full.copy()
    upper[LEG_TOP:] = 0
    legs = P.body.copy()
    legs[:LEG_TOP] = 0
    near, far = legs.copy(), legs.copy()
    near[:, LEG_SPLIT + 1:] = 0
    far[:, :LEG_SPLIT] = 0
    return upper, near, far


def run_frame(P, k, hold=None):
    upper, near, far = run_parts(P)
    top = upper if hold is None else stand(P, hold)
    if hold is not None:
        top = top.copy()
        top[LEG_TOP:] = 0
    P.keep = None
    drill = P.drill_l & (top == P.body).all(-1)
    tails = np.zeros_like(top)
    tails[drill] = top[drill]
    top[drill] = 0
    c = np.zeros((128, 128, 4), np.uint8)
    for leg, ph, side, cyc in ((far, (k + 4) % 8, "far", CYCLE_FAR), (near, k, "near", CYCLE)):
        K.put(c, bent(leg, *cyc[ph], hip_in=HIP_IN[side]), 0, 0)
    dy = BOB[k]
    K.put(c, shifted(top, 0, dy), 0, 0)
    K.put(c, shifted(tails, SWAY[k], dy), 0, 0, under=True)
    K.put(c, shifted(tails, 0, dy), 0, 0, under=True)
    c[SOLES + 1:] = 0
    s4 = shifted(P.scissors, 0, dy)
    P.keep = (s4[..., 3] > 0) & (c == s4).all(-1)
    if HOP[k]:
        c = shifted(c, 0, -HOP[k])
        k4 = np.zeros(c.shape, np.uint8)
        k4[P.keep] = 255
        P.keep = shifted(k4, 0, -HOP[k])[..., 3] > 0
    return c


def posed(P, pose):
    if "leap" in pose:
        c = shifted(run_frame(P, pose["leap"]), *pose.get("move", (0, 0)))
        k4 = np.zeros(c.shape, np.uint8)
        k4[P.keep] = 255
        P.keep = shifted(k4, *pose.get("move", (0, 0)))[..., 3] > 0
        c[SOLES + 1:] = 0
        return c
    return stand(P, pose)


# ------------------------------------------------------------------------------------------------ the death
def turned(a, deg, joint):
    ys, xs = np.nonzero(a[..., 3] > 0)
    x0, y0 = xs.min(), ys.min()
    s = a[y0:ys.max() + 1, x0:xs.max() + 1]
    jx, jy = joint[0] - x0 - 0.5, joint[1] - y0 - 0.5
    if deg % 90 == 0:
        r, (rx, ry) = RN.op(s, (jx, jy), ("rot", int(deg // 90) % 4))
    else:
        r, (rx, ry) = RN.rotsprite(s, (jx, jy), deg)
    out = np.zeros_like(a)
    K.put(out, r, int(math.floor(joint[0] - 0.5 - rx + 0.5)), int(math.floor(joint[1] - 0.5 - ry + 0.5)))
    return out


def laid_out(P):
    """The figure ready to fall: the scissors gone (they fell), the arms as drawn."""
    a = P.body.copy()
    clear(a, FAR_OFF)
    fill(P, a, FAR_FILL)
    ring, col, _ = arm_cells(P, FAR_SH, 20)            # the far arm hanging by her side
    body = a[..., 3] > 0
    put_cells(a, ring, lambda x, y: not body[y, x])
    put_cells(a, col, lambda x, y: not body[y, x])
    a[SOLES + 1:] = 0
    return finish(P, a)


def lying(P):
    a = laid_out(P)
    ys, xs = np.nonzero(a[..., 3] > 0)
    rot = np.rot90(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 1).copy()
    out = np.zeros_like(a)
    h, w = rot.shape[:2]
    x0 = 64 - w // 2 + 2
    out[SOLES + 1 - h:SOLES + 1, x0:x0 + w] = rot
    return out


def scissors_on_ground(P, x_grip=86):
    part = scissors_unit(P, 0)
    c = np.zeros((128, 128, 4), np.uint8)
    cells = part_cells(part, (x_grip, 0))
    lo = max(y for _, y in cells)
    put_cells(c, {(x, y + SOLES - lo): v for (x, y), v in cells.items()})
    return c


DEAD = ["hit", "knocked", (20, -1, 0), (45, -3, 2), (70, -4, 1), (90, -5, 1), (90, -5, 0), (90, -5, 0)]
FEET = (60.0, 99.0)
GRIP = (71.0, 76.5)                                   # the far hand on the shaft in the idle


def about_feet(q, deg):
    t = math.radians(deg)
    rx, ry = q[0] - FEET[0], q[1] - FEET[1]
    return FEET[0] + rx * math.cos(t) + ry * math.sin(t), FEET[1] - rx * math.sin(t) + ry * math.cos(t)


def dead_frame(P, i):
    what = DEAD[i]
    if what == "hit":
        return stand(P, {"move": (-1, 0)})
    if what == "knocked":
        return stand(P, {"move": (-2, -1)})
    deg, dx, up = what
    out = np.zeros((128, 128, 4), np.uint8)
    t = turned(laid_out(P), deg, FEET)
    ys, _ = np.nonzero(t[..., 3] > 0)
    sy = SOLES - int(ys.max()) - up
    K.put(out, shifted(t, dx, sy), 0, 0)
    if deg == 20:
        gx, gy = about_feet(GRIP, deg)
        mx, my = int(round(gx - GRIP[0])) + dx, int(round(gy - GRIP[1])) + sy
        s4 = shifted(P.scissors, mx, my)
    else:
        s4 = scissors_on_ground(P, 76)
    K.put(out, s4, 0, 0, under=True)
    P.keep = (s4[..., 3] > 0) & (out == s4).all(-1)                 # the scissors' outline stays as drawn
    return out


# ------------------------------------------------------------------------------------------------ build
def finish(P, raw):
    """rigkit.finish, then the open gaps the raw frame has (2+ squares) cleared again where the finish filled them."""
    f = K.finish(raw, P.D.outline, SOLES, pinholes=1)
    ink = np.array(P.D.outline, np.uint8)
    for comp in K.holes(raw):
        own = own_hole(P, raw, comp)                                  # the design's own pinholes (between the boots, by
        if len(comp) < 2 and not own:                                 # the loop) stay open: filled in some frames they
            continue                                                  # blinked
        for y, x in comp:
            if f[y, x, 3] and (own or not (f[y, x, :3] == ink).all()):
                f[y, x] = 0
    while True:
        gone = K.orphan_outline(f, P.D.outline)
        if not gone.any():
            break
        f[gone] = 0
    keep = getattr(P, "keep", None)
    P.keep = None
    soften_inner_ink(P, f, keep)
    f = K.fill_pinholes(f, 1, P.D.outline)
    for _ in range(4):                                            # a lone outline square inside the figure (the
        gone = K.orphan_outline(f, P.D.outline)                   # run's swung ringlet): its neighbours' colour
        gone &= ~(keep if keep is not None else np.zeros_like(gone))
        if not gone.any():
            break
        ink8 = np.array(P.D.outline, np.uint8)
        for y, x in zip(*np.nonzero(gone)):
            n8 = [tuple(int(v) for v in f[y + dy, x + dx, :3]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                  if (dy or dx) and f[y + dy, x + dx, 3] and not (f[y + dy, x + dx, :3] == ink8).all()]
            op4 = sum(1 for dy, dx in K.N4 if f[y + dy, x + dx, 3])
            if n8:
                f[y, x, :3] = max(set(n8), key=n8.count)
            elif op4 < 4:
                f[y, x] = 0                                       # (inside a black corner it stays black)
    for comp in K.holes(raw):                                     # the design's own pinholes, open again after the
        if own_hole(P, raw, comp):                                # last fill
            for y, x in comp:
                if f[y, x, 3] and not raw[y, x, 3]:
                    f[y, x] = 0
    return f


def own_hole(P, raw, comp):
    """A hole of the raw frame that is the design's own: the design (as is, or sunk a row) has the same squares in
    the 3 x 3 round every square of it (a pinhole between moved boots is not one: filled in some frames and open in
    others it blinked)."""
    D = P.D.a
    for dy in (0, 1, 2):                                            # (the top sinks a row breathing, two at a crouch)
        s = K.shifted(D, 0, dy) if dy else D
        if all(np.array_equal(s[y - 1:y + 2, x - 1:x + 2], raw[y - 1:y + 2, x - 1:x + 2]) for y, x in comp):
            return True
    return False


def soften_inner_ink(P, f, keep=None):
    """Outline squares a pose puts inside the figure (an arm's ring over the hair, a leg's over the other leg) - not
    in the idle there, every 4-neighbour opaque, two or more coloured - take the darkest colour beside them."""
    ink = np.array(P.D.outline, np.uint8)
    idle = P.D.a
    best = None
    for dx in range(-5, 6):
        for dy in range(-3, 4):
            s = K.shifted(idle, dx, dy) if (dx or dy) else idle
            cost = int((s[58:78, 50:80, :3] != f[58:78, 50:80, :3]).any(-1).sum())
            if best is None or cost < best[0]:
                best = (cost, s, dx, dy)
    s = best[1]
    face = np.zeros(f.shape[:2], bool)
    r0, r1, c0, c1 = FACE_BOX
    face[r0 + best[3]:r1 + best[3], c0 + best[2]:c1 + best[2]] = True
    was = (s[..., 3] > 0) & (s[..., :3] == ink).all(-1)
    was |= (idle[..., 3] > 0) & (idle[..., :3] == ink).all(-1)       # the legs stay where they are when the top sinks
    op = f[..., 3] > 0
    isk = op & (f[..., :3] == ink).all(-1)
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]  # noqa: E731
    change = {}
    for y, x in zip(*np.nonzero(isk & ~was)):
        if y >= SOLES or (keep is not None and keep[y, x]):
            continue
        n4 = [(y + dy, x + dx) for dy, dx in K.N4]
        if not all(0 <= yy < f.shape[0] and 0 <= xx < f.shape[1] and op[yy, xx] for yy, xx in n4):
            continue
        cols = [tuple(int(v) for v in f[yy, xx, :3]) for yy, xx in n4 if not isk[yy, xx]]
        if len(cols) >= 2:
            change[(y, x)] = min(cols, key=lum)
    for (y, x), c in change.items():
        f[y, x, :3] = c
    off = face | was | (keep if keep is not None else np.zeros_like(face))   # the design's own lone dots stay
    isk = op & (f[..., :3] == ink).all(-1)                                      # (seven of them went in every frame:
    for y, x in zip(*np.nonzero(isk & ~off)):                                   # 「脸上还有一些黑的像素丢失」)
        if y >= SOLES:
            continue
        n4 = [(y + dy, x + dx) for dy, dx in K.N4]
        if not all(0 <= yy < f.shape[0] and 0 <= xx < f.shape[1] and op[yy, xx] for yy, xx in n4):
            continue
        if sum(isk[yy, xx] for yy, xx in n4) > 1:
            continue
        cols = [tuple(int(v) for v in f[yy, xx, :3]) for yy, xx in n4 if not isk[yy, xx]]
        f[y, x, :3] = max(set(cols), key=cols.count)


BREATH = [0, 0, 1, 1, 0, 0]
BREATH_ROW = 89


def breathe(P, d):
    """The idle with everything above BREATH_ROW (the body and the scissors on her shoulder) sunk d rows."""
    if not d:
        return P.D.a.copy()
    a = P.D.a.copy()
    top = a.copy()
    top[BREATH_ROW + 1:] = 0
    a[:BREATH_ROW + 1] = 0
    K.put(a, shifted(top, 0, d), 0, 0)
    P.keep = shifted(np.where(P.sc[..., None], P.D.a, 0).astype(np.uint8), 0, d)[..., 3] > 0
    return finish(P, a)


def frames(P, tag):
    n = len(MS[tag])
    fin = lambda a: finish(P, a)  # noqa: E731
    if tag == "run":
        return [fin(run_frame(P, k)) for k in range(n)]
    if tag == "dead":
        return [fin(dead_frame(P, k)) for k in range(n)]
    if tag in STAND:
        return [fin(posed(P, p)) for p in STAND[tag]]
    if tag == "idle":
        return [breathe(P, d) for d in BREATH]
    return [P.D.a.copy() for _ in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write review sheets to this folder")
    ap.add_argument("--tags", help="comma-separated tags to build (review only)")
    a = ap.parse_args()
    P = Parts()
    tags = a.tags.split(",") if a.tags else TAGS
    built = {t: frames(P, t) for t in tags}
    for t in tags:
        rows = K.audit(built[t], P.D.a, P.D.outline, SOLES)
        print(t, " ".join(f"[{r['pieces']}p {r['holes']}h {r['orphans']}o {r['area']}]" for r in rows))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, [P.D.a] + built[t]) for t in tags], os.path.join(a.review, "rig_sheet.png"), z=4,
                       soles=SOLES)
        return
    bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differ:", bad or "none")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

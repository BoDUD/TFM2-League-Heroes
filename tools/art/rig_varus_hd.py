#!/usr/bin/env python3
"""league_varus redone at PPU 1.5 (the user, 2026-10-23: 「设计通过，用 PPU 1.5（和现在一样高）」) from the approved design
(tools/art/design_varus_hd.py, 58 x 59), every action posed here from the design's own squares - no Codex (the user:
「动作帧你可以参考隔壁oppi 这样就不要依赖codex了」), after oppi's archer (cf_ashe.aseprite: the bow held up at arm's
length, the string drawn back, the body bracing as it looses) and League's clips (the sheet's frames and the kit's
release ticks; tools/lol/league_joints.py's varus joints for the run and the death).

    python tools/art/rig_varus_hd.py --parts DIR         # the parts tinted and the key poses at 8x
    python tools/art/rig_varus_hd.py --review DIR        # every tag at 3x + GIFs
    python tools/art/rig_varus_hd.py                     # orig strips + the 1x sheet
    python tools/art/hero_reels.py --hero varus          # then: the idle / ban-pick reels from idle_base

No square is redrawn or resampled (the user: 「各种变形 请你改到完美」 on a first rig that drew its arms as bands twice
the design's width): the parts are cut square by square (BOW_ROWS, NEAR_ROWS, the legs below LEG_TOP) and placed only by
whole squares, quarter turns and mirrors; standing, the parts rebuild the design exactly (check()).

- The bow, the far claw round its grip and the far forearm are one rigid piece. Drawing, it is lifted (UP) so the arrow
  flies level with his lower chest (League holds the bow there) and the near arm is the design's own arm turned level
  (a transpose: its lit side up), the forearm sliding back along the upper arm as the string comes to the chest. The
  string runs from the bow's tips to the near claw behind his head (the head is drawn over it - League pulls past the
  ear); the arrow is a level shaft in the hair's silvers with the glow's magenta head.
- The run: the upper body as drawn, leaning 2 columns ahead of the hips and bobbing with League's pelvis; the legs on
  League's run angles, each drawn square by square from the design's own leg - the thigh and the shin take, along
  their bones, the design leg's row at that length and its square at that side - and the design's boot stamped whole at
  the ankle (the near one mirrored once: both toes forward); the near arm swings opposite the near leg by whole-row
  shifts, the bow rides a row with the hand.
- The death (League: he rears up, then sinks to his knees): staggered back and lifted, the bow raised; then he lets it
  fall (the bow and claw lying on the ground, tips down; his far arm hangs - a copy of the near arm's squares) and
  kneels on both knees on legs drawn the same way, the boots behind turned a quarter (toes tucked).
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
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "varus"
PPU = 1.5
DESIGN_ROWS = 59
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
JOINTS = os.path.join(HD, "varus_joints.json")

# ------------------------------------------------------------------------------------------------ the parts
# the bow, the far claw round its grip and the far forearm: every opaque square from these columns on (rows y0-y1)
BOW_ROWS = [(0, 30, 43), (31, 31, 35), (32, 34, 34), (35, 37, 35), (38, 38, 36), (39, 41, 37), (42, 52, 39), (53, 58, 44)]
FOREARM = (31, 41, 41)          # the far forearm in that piece: rows 31-41, columns up to 41
# the near arm hanging at his side: row -> (first column, last column)
NEAR_ROWS = {30: (13, 17), 31: (13, 18), 32: (13, 18), 33: (12, 18), 34: (12, 18), 35: (12, 18), 36: (12, 17),
             37: (13, 16), 38: (13, 16), 39: (13, 17), 40: (12, 18), 41: (12, 18), 42: (11, 18), 43: (11, 18),
             44: (12, 17), 45: (12, 16), 46: (15, 16)}
ARM_TOP, ARM_X0 = 30, 11        # the near arm's first row and its leftmost column
ELBOW = 34                      # its corrupted red ends here, the purple forearm and the claw follow
LEG_TOP = 41                    # the trousers below the hip plates: the legs
LOIN = (26, 30, 41, 50)         # columns, rows of the dark-red loincloth (its reds stay with the body)
SCARF_X = 11                    # the scarf's tail: columns up to here from ARM_TOP down
HEAD_ROW = 30                   # the head and the scarf round his neck: rows up to here (drawn over the bow string)
# the legs' bones (design squares, square edges): hip on LEG_TOP, knee, ankle on the boot's top row
BONES = {"near": dict(hip=(24.0, 41.0), knee=(20.5, 47.0), ankle=(19.0, 53.0)),
         "far": dict(hip=(33.0, 41.0), knee=(35.5, 47.0), ankle=(37.0, 53.0))}
BOOT_ROW = 53

# the bow piece and the near arm when he draws
UP = (3, -4)                    # the bow piece lifted: its grip from row 39 to the arrow's row
ARROW_ROW = 35                  # the arrow's shaft (the lower chest)
ARM_ROW0 = 30                   # the turned near arm's top row (its column ARM_X0 -> this row)
TIP_TOP, TIP_BOT = (44.5, 1.5), (46.5, 56.0)     # the bow's tips (design squares, as drawn)
ARROW_LEN = 29                  # squares from the nock to the head's point
NOCK_X = 32                     # the claw's fingertips, arm straight (the design's arm 17 squares from the shoulder)
FULL_X = 26                     # at full draw (by his chest)
LOOSE_X = 24                    # the hand flicked back past the chest as he looses
O = (10, 0, 14)
SHAFT = [(222, 223, 250), (172, 172, 216)]      # the hair's silvers
HEADC = [(214, 23, 250), (182, 32, 222)]        # the glow's magentas
STRING = (154, 53, 203)                          # the trousers' lit violet
PAD = 24


def lp(path):
    return R.lp(path)


def design_pic():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


def masks(d):
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:H, 0:W]
    start = np.full(H, W)
    for y0, y1, x0 in BOW_ROWS:
        start[y0:y1 + 1] = x0
    unit = op & (xx >= start[:, None])
    fa = unit & (yy >= FOREARM[0]) & (yy <= FOREARM[1]) & (xx <= FOREARM[2])
    near = np.zeros_like(op)
    for y, (a, b) in NEAR_ROWS.items():
        near[y, a:b + 1] = op[y, a:b + 1]
    red = (d[..., 0] > 50) & (d[..., 1] < 30) & (d[..., 2] < 30)
    x0, x1, y0, y1 = LOIN
    loin = op & red & (yy >= y0) & (yy <= y1) & (xx >= x0) & (xx <= x1)
    scarf = op & ~unit & ~near & (yy >= ARM_TOP) & (xx <= SCARF_X)
    legs = op & (yy >= LEG_TOP) & ~unit & ~near & ~loin & ~scarf
    leg_near, leg_far = legs & (xx <= 27), legs & (xx >= 28)
    body = op & ~unit & ~near & ~scarf & ~legs
    return dict(unit=unit, forearm=fa, near=near, scarf=scarf, leg_near=leg_near, leg_far=leg_far, body=body,
                head=body & (yy <= HEAD_ROW))


def piece(d, m):
    """The squares of mask m cut out on their bounding box, and the box's top-left (x, y)."""
    ys, xs = np.nonzero(m)
    sub = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    sub[~m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]] = 0
    return sub, (int(xs.min()), int(ys.min()))


# ------------------------------------------------------------------------------------------------ drawing
class Frame:
    """A frame being composed in design squares (PAD squares round the design)."""

    def __init__(self, d):
        self.d = d
        self.a = np.zeros((d.shape[0] + 2 * PAD, d.shape[1] + 2 * PAD, 4), np.uint8)

    def put(self, mask, dx=0, dy=0, src=None, keep=None):
        """The design's squares of mask, moved; keep: a mask of the frame (PAD coordinates) not to draw over."""
        src = self.d if src is None else src
        ys, xs = np.nonzero(mask)
        Y, X = ys + dy + PAD, xs + dx + PAD
        ok = (Y >= 0) & (Y < self.a.shape[0]) & (X >= 0) & (X < self.a.shape[1])
        Y, X, ys, xs = Y[ok], X[ok], ys[ok], xs[ok]
        if keep is not None:
            free = ~keep[Y, X]
            Y, X, ys, xs = Y[free], X[free], ys[free], xs[free]
        self.a[Y, X] = src[ys, xs]

    def stamp(self, img, x0, y0, keep=None):
        ys, xs = np.nonzero(img[..., 3] > 0)
        Y, X = ys + y0 + PAD, xs + x0 + PAD
        ok = (Y >= 0) & (Y < self.a.shape[0]) & (X >= 0) & (X < self.a.shape[1])
        Y, X, ys, xs = Y[ok], X[ok], ys[ok], xs[ok]
        if keep is not None:
            free = ~keep[Y, X]
            Y, X, ys, xs = Y[free], X[free], ys[free], xs[free]
        self.a[Y, X] = img[ys, xs]

    def paint(self, cells):
        for (x, y), c in cells.items():
            Y, X = y + PAD, x + PAD
            if 0 <= Y < self.a.shape[0] and 0 <= X < self.a.shape[1]:
                self.a[Y, X, :3] = c[:3]
                self.a[Y, X, 3] = 255

    def opaque(self):
        return self.a[..., 3] > 0


def line(cells, A, B, c):
    """A 1-square line A -> B (square edges), every square it passes."""
    A, B = np.array(A, float), np.array(B, float)
    n = int(max(abs(B - A)) * 2) + 1
    for k in range(n + 1):
        p = A + (B - A) * k / n
        cells[(int(math.floor(p[0])), int(math.floor(p[1])))] = c


def sheared(img, k, pivot_row=0):
    """Rows of img shifted by round(k * (row - pivot_row) / rows): an arm swinging about its top (whole rows kept)."""
    h, w = img.shape[:2]
    pad = int(abs(k)) + 1
    out = np.zeros((h, w + 2 * pad, 4), np.uint8)
    for y in range(h):
        s = int(round(k * (y - pivot_row) / max(1, h - 1 - pivot_row))) if y > pivot_row else 0
        out[y, pad + s:pad + s + w] = img[y]
    return out, pad


# ------------------------------------------------------------------------------------------------ the legs
# drawn again, the far leg's lights a step down the design's own purple ramps so the crossing reads (league_xinzhao's
# run, league_taric's): the armour l > p > w > u > v, the glow m / N > M > p; its base q stays (one more step is the
# near-black x: the leg went black)
SHADE = {(154, 53, 203): (129, 39, 159), (129, 39, 159): (100, 28, 134), (100, 28, 134): (77, 28, 115),
         (77, 28, 115): (62, 24, 97), (214, 23, 250): (154, 14, 250), (182, 32, 222): (154, 14, 250),
         (154, 14, 250): (129, 39, 159)}


def shaded(cols):
    out = cols.copy()
    for i, c in enumerate(cols):
        t = SHADE.get(tuple(int(v) for v in c[:3]))
        if t is not None:
            out[i, :3] = t
    return out


class Legs:
    """The design's legs as row slices along their bones, drawn again on other bones (the run, the kneel)."""

    def __init__(self, d, M):
        self.d = d
        self.slices, self.boots = {}, {}
        for key in ("near", "far"):
            m = M["leg_" + key]
            sl = {}
            for y in range(LEG_TOP, BOOT_ROW):
                xs = np.nonzero(m[y])[0]
                a, b = int(xs.min()), int(xs.max())
                a += tuple(d[y, a, :3]) == O                        # less the silhouette's outline square each
                b -= tuple(d[y, b, :3]) == O                        # side: fold draws it round the turned leg
                sl[y] = (a, b, shaded(d[y, a:b + 1]) if key == "far" else d[y, a:b + 1].copy())
            self.slices[key] = sl
            ys, xs = np.nonzero(m & (np.arange(d.shape[0])[:, None] >= BOOT_ROW))
            ax, ay = BONES[key]["ankle"]
            self.boots[key] = (xs - ax, ys - ay, shaded(d[ys, xs]) if key == "far" else d[ys, xs])

    def segment(self, cells, key, P0, P1, r0, r1, top=0.0):
        """Squares within the slice's half width of P0 -> P1 take the slice of design row r0 .. r1 at that length
        (top: squares more before P0, the first slice again - a thigh reaching up under the hip plates)."""
        P0, P1 = np.asarray(P0, float), np.asarray(P1, float)
        v = P1 - P0
        L = max(1e-6, float(np.hypot(*v)))
        u = v / L
        n = np.array((u[1], -u[0]))                     # down -> +x: the slice's left side stays on the left
        sl = self.slices[key]
        for y in range(int(math.floor(min(P0[1], P1[1]))) - 5, int(math.ceil(max(P0[1], P1[1]))) + 5):
            for x in range(int(math.floor(min(P0[0], P1[0]))) - 5, int(math.ceil(max(P0[0], P1[0]))) + 5):
                p = np.array((x + 0.5, y + 0.5)) - P0
                t, s = float(p @ u), float(p @ n)
                if t < -0.5 - top or t > L + 0.5:
                    continue
                r = int(round(r0 + min(1.0, max(0.0, t / L)) * (r1 - r0 - 1)))
                xl, xr, cols = sl[r]
                c = (xl + xr + 1) / 2
                xi = int(math.floor(c + s))
                if xl <= xi <= xr:
                    cells[(x, y)] = cols[xi - xl]

    def leg(self, key, H, K, A, boot="as drawn"):
        """{(x, y): rgba} the leg on bones hip H, knee K, ankle A (square edges): the shin, the thigh over it, the boot
        ("as drawn", "mirror": toe turned the other way, "tucked": a quarter turn, toes down, sole back)."""
        cells = {}
        self.segment(cells, key, K, A, 47, BOOT_ROW)
        self.segment(cells, key, H, K, LEG_TOP, 47, top=2.0)
        bx, by, cols = self.boots[key]
        if boot == "mirror":
            bx = -bx
        elif boot == "tucked":                          # a quarter turn clockwise: the toe down, the sole back
            bx, by = -by, bx
        elif boot == "tucked_m":                        # mirrored (toe forward), then that turn
            bx, by = -by, -bx
        for x, y, c in zip(bx, by, cols):
            cells[(int(math.floor(A[0] + x)), int(math.floor(A[1] + y)))] = c
        return cells


def fold(leg_cells, outline=O):
    """A drawn leg's squares with the outline ring closed round them (the slices carry their own edges; the ring
    covers what a turned slice leaves open)."""
    out = dict(leg_cells)
    for (x, y) in list(leg_cells):
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ddx, y + ddy)
            if q not in leg_cells:
                out.setdefault(q, np.array((*outline, 255), np.uint8))
    return out


# ------------------------------------------------------------------------------------------------ poses
# A pose: dx, dy (the whole figure); bow: "low" (as drawn), "up" (lifted to draw), "drop" (lying on the ground);
# bow_d: (dx, dy) more for the bow piece; hand: the turned near arm's fingertips' column (None: hanging); arm_k: the
# hanging arm's swing (columns at the claw); arrow / string: drawn; scarf: the tail's sway (columns at its end);
# legs: None (as drawn) or {"near" | "far": (hip, knee, ankle, boot)} with "lean" / "sink" for the body over them.
def arm_rows(d, M, r0, r1):
    """The near arm's design rows r0..r1 cut out (its own columns), and that piece's left column."""
    arm, (ax, ay) = piece(d, M["near"])
    return arm[r0 - ay:r1 - ay + 1].copy(), ax


def arm_turned(f, d, M, h, ya, bx, by):
    """The whole arm turned level (a transpose, its lit side up), the forearm sliding back along the upper arm."""
    arm, (ax, ay) = piece(d, M["near"])
    T = arm.transpose(1, 0, 2)                          # rows = the arm's columns (lit side up), columns = its rows
    e = ELBOW - ARM_TOP
    upper, fore = T[:, :e], T[:, e:]
    row0 = ARM_ROW0 + (ax - ARM_X0) + by
    fx0 = int(h) - fore.shape[1] + 1                    # the forearm's elbow end
    shoulder = 13 + bx
    if fx0 >= shoulder + upper.shape[1]:
        f.stamp(T, fx0 - upper.shape[1], row0)          # the arm straight out
    else:
        if fx0 >= shoulder:
            f.stamp(upper, shoulder, row0)
        else:
            f.stamp(upper[:, ::-1], fx0 - upper.shape[1] + 1, row0)     # the elbow back past the shoulder
        f.stamp(fore, fx0, row0)


def arm_drop(f, d, M, h, ya, bx, by):
    """The upper arm as drawn, hanging from the shoulder; the forearm and claw (rows ELBOW_DROP on) turned level from
    the elbow to the string (a transpose: the claw's fingers forward)."""
    up, ax = arm_rows(d, M, ARM_TOP, ELBOW_DROP - 1)
    f.stamp(up, ax + bx, ARM_TOP + by)
    fore, _ = arm_rows(d, M, ELBOW_DROP, 46)
    T = fore.transpose(1, 0, 2)
    f.stamp(T, int(h) - T.shape[1] + 1, ya - (14 - ax))


def arm_hang(f, d, M, h, ya, bx, by):
    """The upper arm as drawn; the wrist turned level from the elbow; the claw as drawn (fingers down) at its end, on
    the string."""
    up, ax = arm_rows(d, M, ARM_TOP, ELBOW_DROP - 1)
    f.stamp(up, ax + bx, ARM_TOP + by)
    wrist, _ = arm_rows(d, M, ELBOW_DROP, 39)
    claw, _ = arm_rows(d, M, 40, 46)
    W = wrist.transpose(1, 0, 2)
    cx0 = int(h) - claw.shape[1] + 1
    f.stamp(W, cx0 - W.shape[1] + 2, ya - (14 - ax))
    f.stamp(claw, cx0, ya - 2)


def arm_bent(f, d, M, h, ya, bx, by):
    """The upper arm as drawn (rows ARM_TOP..ELBOW-1) hanging from the shoulder, its foot sheared forward to the elbow
    when the hand reaches past it; the forearm and claw (ELBOW on) turned level (a transpose, the lit side up) from the
    elbow to the string."""
    up, ax = arm_rows(d, M, ARM_TOP, ELBOW - 1)
    fore, _ = arm_rows(d, M, ELBOW, 46)
    T = fore.transpose(1, 0, 2)
    fx0 = int(h) - T.shape[1] + 1                       # the forearm's elbow end
    k = max(0, fx0 - (ax + 3) - bx)                      # the elbow ahead of where the upper arm hangs
    img, pad = sheared(up, k, pivot_row=0)
    f.stamp(img, ax - pad + bx, ARM_TOP + by)
    f.stamp(T, fx0, ya - (14 - ax))


ELBOW_DROP = 36                 # arm_drop / arm_hang: the near arm's rows above hang as drawn, the rest turns level
ARMS = {"turned": arm_turned, "drop": arm_drop, "hang": arm_hang, "bent": arm_bent}
ARM = "bent"                    # the drawing arm (the user: 「左手拉弓箭有点变形」 on "turned": a bar across his belly, the elbow a pink lump)


def compose(d, M, legs_lib, pose):
    f = Frame(d)
    dx, dy = pose.get("dx", 0), pose.get("dy", 0)
    bow = pose.get("bow", "low")
    bd = pose.get("bow_d", (0, 0))
    legs = pose.get("legs")
    lean, sink = pose.get("lean", 0), pose.get("sink", 0)
    bx, by = dx + lean, dy + sink                       # the upper body's move (over the legs, which stay)
    if bow in ("low", "up"):
        ux, uy = (UP if bow == "up" else (0, 0))
        f.put(M["unit"], bx + ux + bd[0], by + uy + bd[1])
    elif not pose.get("nofar"):                         # dropped: the far arm hangs (the near arm's own squares)
        arm, (ax, ay) = piece(d, M["near"])
        f.stamp(arm, ax + 21 + bx, ay + 1 + by)
    drawn = {}
    if legs:
        for key in ("far", "near"):
            H, K, A, boot = legs[key]
            sh = np.array((dx, dy))
            drawn[key] = fold(legs_lib.leg(key, np.add(H, sh), np.add(K, sh), np.add(A, sh), boot))
        f.paint(drawn["far"])
        f.paint(drawn["near"])                          # the hip plates and the loincloth hang over both
    else:
        f.put(M["leg_far"], dx, dy)
        f.put(M["leg_near"], dx, dy)
    f.put(M["body"], bx, by)
    k = pose.get("scarf", 0)
    if k:
        sc, (sx, sy) = piece(d, M["scarf"])
        img, pad = sheared(sc, k)
        f.stamp(img, sx - pad + bx, sy + by)
    else:
        f.put(M["scarf"], bx, by)
    if bow == "drop":
        f.stamp(pose["_lying"], *pose["_lying_at"])
    hand = pose.get("hand")
    if hand is None:
        kk = pose.get("arm_k", 0)
        if kk:
            arm, (ax, ay) = piece(d, M["near"])
            img, pad = sheared(arm, kk, pivot_row=2)
            f.stamp(img, ax - pad + bx, ay + by)
        else:
            f.put(M["near"], bx, by)
        return f.a, {}, {}
    # drawing: the string and the arrow (effect layers, never outlined: under - the top string, hidden behind his head;
    # over - the bottom string in front of his legs and the arrow, both stopping at the claw), the near arm turned level
    ux, uy = UP[0] + bd[0] + bx, UP[1] + bd[1] + by
    h = hand + bx
    ya = ARROW_ROW + by
    over, under = {}, {}
    if pose.get("string"):
        line(under, (TIP_TOP[0] + ux, TIP_TOP[1] + uy), (h - 1.5, ya + 0.5), STRING)
        line(over, (TIP_BOT[0] + ux, TIP_BOT[1] + uy), (h - 1.5, ya + 0.5), STRING)
    if pose.get("arrow"):
        x0, x1 = int(h) - 3, int(h) + ARROW_LEN - 4
        for x in range(x0, x1 + 1):
            over[(x, ya)] = SHAFT[0]
            over[(x, ya + 1)] = SHAFT[1]
        for i, (top, bot) in enumerate(((-1, 2), (-1, 2), (0, 1))):
            for y in range(ya + top, ya + bot + 1):
                over[(x1 + 1 + i, y)] = HEADC[0] if top <= y - ya < bot else HEADC[1]
    was = f.a.copy()
    ARMS[pose.get("arm", ARM)](f, d, M, h, ya, bx, by)
    ys, xs = np.nonzero((f.a != was).any(-1))
    arm_sq = set(zip((xs - PAD).tolist(), (ys - PAD).tolist()))
    over = {q: c for q, c in over.items() if q not in arm_sq}
    return f.a, over, under


LOW = dict(bow="low")
NOCK = dict(bow="up", hand=NOCK_X, arrow=True, string=True)


def drawn(k, **kw):
    """The string pulled k of the way from the nock to his chest."""
    p = dict(bow="up", hand=int(round(NOCK_X + (FULL_X - NOCK_X) * k)), arrow=True, string=True)
    p.update(kw)
    return p


LOOSE = dict(bow="up", hand=LOOSE_X)
FOLLOW = dict(bow="up", hand=NOCK_X - 2)
# the tags: one pose per sheet frame (the sheet's count and timing; the release on the kit's tick)
POSES = {
    # loosed on the kit's tick: attack 167 ms (4th frame), Q 1100 ms (6th) / 400 ms (6th), E 183 ms (4th), R 267 ms (4th)
    "attack": [NOCK, drawn(0.5), drawn(1.0), dict(LOOSE, dx=-1, scarf=-1), dict(LOOSE, dx=-1, scarf=-1), LOOSE,
               LOOSE, FOLLOW, LOW, LOW],
    # Q's charge held braced (the upper body a row down over the legs), the scarf stirring
    "skill": [NOCK, drawn(0.5), drawn(1.0, sink=1), drawn(1.0, sink=1, scarf=-1), drawn(1.0, sink=1),
              dict(LOOSE, dx=-1, scarf=-2), dict(LOOSE, scarf=-1)],
    "skill_quick": [NOCK, drawn(0.5), drawn(1.0, sink=1), drawn(1.0, sink=1, scarf=-1), drawn(1.0, sink=1),
                    dict(LOOSE, dx=-1, scarf=-2), dict(LOOSE, scarf=-1), LOOSE, FOLLOW, LOW],
    "skill2": [NOCK, drawn(0.5), drawn(1.0), dict(LOOSE, dx=-1, scarf=-1), dict(LOOSE, dx=-1, scarf=-1), LOOSE,
               LOOSE, FOLLOW, LOW, LOW],
    "ult": [NOCK, drawn(0.5), drawn(1.0, sink=1), dict(LOOSE, dx=-1, scarf=-2), dict(LOOSE, dx=-1, scarf=-2),
            dict(LOOSE, scarf=-1), LOOSE, LOOSE, FOLLOW, LOW],
}


# ------------------------------------------------------------------------------------------------ the run
RUN_LEAN = 3                    # the upper body ahead of the hips (League's run leans 25-30 degrees)
RUN_HIP = 0.0                   # the hips' columns either side of the pelvis: one behind the other (3/4), so a step reads as a V either way
PELVIS_X = 28.5                 # between the design's hips, over the loincloth
RUN_K = 0.78                    # League units -> squares (his planted leg: League 16.9 from the pelvis, ours 13)
RUN_SHIFT = 3.0                 # League units the feet come forward: League's run leans 25-30 degrees, ours stands
BOOT_H = 6                      # the boot's rows under the ankle


def knee_of(H, A, lt, ls, forward=True):
    """The knee between hip H and ankle A on bones lt, ls (bent forward or back)."""
    H, A = np.asarray(H, float), np.asarray(A, float)
    v = A - H
    dist = float(np.hypot(*v))
    if dist >= lt + ls:
        return H + v / dist * lt
    a = math.acos(max(-1.0, min(1.0, (lt * lt + dist * dist - ls * ls) / (2 * lt * dist))))
    base = math.atan2(v[0], v[1])
    ang = base + (a if forward else -a)
    return H + lt * np.array((math.sin(ang), math.cos(ang)))


def bone_len(key):
    b = BONES[key]
    return float(np.hypot(*np.subtract(b["knee"], b["hip"]))), float(np.hypot(*np.subtract(b["ankle"], b["knee"])))


# the run's 8 frames on League's rhythm (near foot planted in 0-1, both up in 2-3, far planted in 4-5, both up in 6-7):
# each ankle's column from its own hip and its rows over the ground, the body's rows down (contact low, flight high)
RUN_KEYS = [((7, 0), (-7, 6), 1), ((3, 0), (-4, 8), 1), ((-2, 0), (2, 7), 0), ((-7, 3), (6, 2), -1),
            ((-7, 6), (6, 0), 1), ((-4, 8), (3, 0), 1), ((2, 7), (-2, 0), 0), ((6, 2), (-7, 3), -1)]
RUN_BOW = -2                    # the bow carried two rows higher while he runs (League's runs it up in front)


def run_poses(rows):
    """The run's poses: RUN_KEYS's ankles, the knees bent forward on the design's bone lengths (tools/lol's League
    run joints gave the rhythm: a foot planted two frames, then both up), the near arm swinging opposite the near leg
    (League's hand), the bow riding a row with the far hand."""
    hand = [r["j"]["r_hand"][0] - r["j"]["r_shoulder"][0] for r in rows]
    h0 = float(np.mean(hand))
    bow = [r["j"]["l_hand"][1] - r["j"]["chest"][1] for r in rows]
    b0 = float(np.mean(bow))
    out = []
    for i, (nk, fk, dy) in enumerate(RUN_KEYS):
        legs = {}
        for key, (ax, lift) in (("near", nk), ("far", fk)):
            lt, ls = bone_len(key)
            H = np.array((PELVIS_X + (-RUN_HIP if key == "near" else RUN_HIP), float(LEG_TOP)))
            A = np.array((H[0] + ax, float(BOOT_ROW - lift - dy)))
            v = A - H
            if np.hypot(*v) > lt + ls:
                sys.exit(f"run {i}: the {key} ankle out of reach ({np.hypot(*v):.1f} > {lt + ls:.1f})")
            K = knee_of(H, A, lt, ls, forward=True)
            legs[key] = (H, np.round(K * 2) / 2, A, "mirror" if key == "near" else "as drawn")
        out.append(dict(LOW, dy=dy, legs=legs, lean=RUN_LEAN,
                        arm_k=int(round((hand[i] - h0) * RUN_K * 1.5)),
                        bow_d=(0, RUN_BOW + int(round(max(-1, min(1, (bow[i] - b0) * RUN_K))))),
                        scarf=-1 - (i % 2)))
    return out


# ------------------------------------------------------------------------------------------------ the death
KNEEL = 9                       # rows the body sinks kneeling: the knees on the ground, the thighs upright


KNEEL_ANG = 30                  # kneeling: the thighs forward of straight down (degrees), the knees on the ground
CLUTCH_X = 30                   # the near claw clutching his chest (the turned arm's fingertips' column)
BOW_FALL = 39                   # the dropped bow's left end column: at his front foot (one piece with him)


def kneel_legs(sink, full):
    """{"near" | "far": (hip, knee, ankle, boot)}: full - both knees on the ground KNEEL_ANG forward, the shins back to
    the boots tucked behind (toes down); halfway - the knees bent forward over the boots standing as drawn."""
    out = {}
    for key in ("near", "far"):
        lt, ls = bone_len(key)
        b = BONES[key]
        H = np.array((b["hip"][0], b["hip"][1] + sink))
        if full:
            a = math.radians(KNEEL_ANG)
            K = H + lt * np.array((math.sin(a), math.cos(a)))
            ay = DESIGN_ROWS - BOOT_H
            A = np.array((K[0] - math.sqrt(max(0.0, ls * ls - (ay - K[1]) ** 2)), ay))
            out[key] = (H, K, A, "tucked_m" if key == "near" else "tucked")
        else:
            A = np.array(b["ankle"])
            out[key] = (H, knee_of(H, A, lt, ls, forward=True), A, "as drawn")
    return out


def lying_bow(d, M):
    """The bow and the far claw (the forearm left on the arm) lying on the ground in front of him: the tips down, the
    top forward - (x, y) -> (-y, -x), lossless."""
    sub, _ = piece(d, M["unit"] & ~M["forearm"])
    return sub.transpose(1, 0, 2)[::-1, ::-1].copy()


# League's death: he jerks back and rears up (lifted), throws the bow away, clutches his chest and sinks to his knees
DEAD = [dict(LOW, dx=-1), dict(LOW, dx=-1, dy=-1, bow_d=(0, -2), scarf=1), dict(LOW, dx=-2, dy=-2, bow_d=(0, -3), scarf=2),
        dict(bow="drop", dx=-2, dy=-1, hand=CLUTCH_X, nofar=True, scarf=1),
        dict(bow="drop", dx=-1, hand=CLUTCH_X, nofar=True),
        dict(bow="drop", legs="half", hand=CLUTCH_X, nofar=True),
        dict(bow="drop", legs="full", hand=CLUTCH_X, nofar=True),
        dict(bow="drop", legs="full", hand=CLUTCH_X, nofar=True)]


# ------------------------------------------------------------------------------------------------ the effects
# varus_bake.json's pictures were drawn round the old 1x sprite's arrow (its tip 9.5 px over the pivot, 14.5 ahead);
# this arrow flies 4.2 px over it, its head 15 ahead: each effect moved by (dx, dy) 1x px (e_cast left the old bow's
# raised tip: its streak now rises from the arrowhead)
FX_AT = {"a_flash": (0, 5), "q_charge": (0, 4), "q_charge_s": (0, 4), "w_glow": (0, 4), "q_fire": (0, 5),
         "e_cast": (5, 12), "r_cast": (1, 5)}


# ------------------------------------------------------------------------------------------------ the rig
def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(HD, "picture.png")))


def design():
    d = design_pic()
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.d0 = D.d.copy()
    return D


def on_rig(rig, a):
    """A composed frame (design squares + PAD) on the rig's canvas (the design's (0, 0) at ox, oy)."""
    can = rig.canvas()
    ys, xs = np.nonzero(a[..., 3] > 0)
    Y, X = ys - PAD + rig.oy, xs - PAD + rig.ox
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    can[Y[ok], X[ok]] = a[ys[ok], xs[ok]]
    can[rig.GY:] = 0
    return can


class Poser:
    def __init__(self, d):
        self.d = d
        self.M = masks(d)
        self.legs = Legs(d, self.M)
        self.lying = lying_bow(d, self.M)

    def check(self):
        """Standing, the parts rebuild the design square for square; the parts cover it once."""
        M, d = self.M, self.d
        op = d[..., 3] > 0
        n = sum(M[k].astype(int) for k in ("unit", "near", "scarf", "leg_near", "leg_far", "body"))
        if (n[op] != 1).any() or (n[~op] != 0).any():
            sys.exit(f"parts: {int((n[op] != 1).sum())} squares not in exactly one part")
        a = self.frame(LOW)[0]
        got = a[PAD:PAD + d.shape[0], PAD:PAD + d.shape[1]]
        if (got != d).any() or int(a[..., 3].astype(int).sum()) != int(d[..., 3].astype(int).sum()):
            sys.exit("the standing pose does not rebuild the design")

    def frame(self, pose):
        p = dict(pose)
        if p.get("legs") in ("half", "full"):
            full = p["legs"] == "full"
            sink = KNEEL if full else KNEEL // 2
            p.update(legs=kneel_legs(sink, full), sink=sink)
        if p.get("bow") == "drop":
            h, w = self.lying.shape[:2]
            p["_lying"] = self.lying
            p["_lying_at"] = (BOW_FALL, DESIGN_ROWS - h)        # on the ground, where it fell
        return compose(self.d, self.M, self.legs, p)


def layer(rig, cells):
    """{(x, y): colour} in design squares -> a canvas of the rig (None when empty)."""
    if not cells:
        return None
    can = rig.canvas()
    for (x, y), c in cells.items():
        Y, X = y + rig.oy, x + rig.ox
        if 0 <= Y < rig.GY and 0 <= X < can.shape[1]:
            can[Y, X, :3] = c[:3]
            can[Y, X, 3] = 255
    return can


def on_layers(rig, composed):
    """Poser.frame's (body, over cells, under cells) -> the rig's canvases."""
    a, ov, un = composed
    return on_rig(rig, a), layer(rig, ov), layer(rig, un)


def flat(rig, body, over=None, under=None):
    """The finished body with its effect layers on (the review's way): under where the body is clear, over on top."""
    full = rig.finish(body)
    for fx_, top in ((under, False), (over, True)):
        if fx_ is not None:
            m = fx_[..., 3] > 0
            if not top:
                m &= full[..., 3] == 0
            full[m] = fx_[m]
    return full


LINES = {}                      # id(a frame's body canvas) -> (over, under): its string and arrow


def with_lines(acts):
    """The string and arrow layers put under each baked frame's effects (bake splits frames; the pieces keep their
    body canvas, so the id finds them)."""
    for fr in acts.values():
        for lay, _ in fr:
            got = LINES.get(id(lay["body"]))
            if got is None:
                continue
            for key, ln in zip(("over", "under"), got):
                if ln is None:
                    continue
                new = ln.copy()
                if lay.get(key) is not None:
                    m = lay[key][..., 3] > 0
                    new[m] = lay[key][m]
                lay[key] = new
    return acts


def frames(rig):
    d = rig.D.d0
    ps = Poser(d)
    ps.check()
    sheet = R.sheet_of(HERO)
    with open(lp(JOINTS), encoding="utf-8") as f:
        joints = json.load(f)
    with open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8") as f:
        bake = json.load(f)
    for e in bake["items"]:                             # the old sprite's arrow -> this one's (FX_AT)
        ddx, ddy = FX_AT.get(e["tag"], (0, 0))
        e["dx"], e["dy"] = e.get("dx", 0) + ddx, e.get("dy", 0) + ddy
    baked = {e["into"] for e in bake["items"] if "from" in e}
    out = {}
    for tag in sheet:
        if tag in baked or tag in ("idle", "bp"):
            continue
        ms = [m for _, m in sheet[tag]]
        n = len(ms)
        if tag in POSES:
            poses = POSES[tag]
        elif tag == "run":
            poses = run_poses(joints["tags"]["run"])
        elif tag == "idle_base":
            poses = [LOW] * n
        elif tag == "hit":
            poses = [dict(LOW, dx=-1, scarf=1), LOW]
        elif tag == "dead":
            poses = DEAD
        else:
            sys.exit(f"{tag}: no poses")
        if len(poses) != n:
            sys.exit(f"{tag}: {len(poses)} poses for {n} frames")
        fr = []
        for p in poses:
            a, ov, un = ps.frame(p)
            can = on_rig(rig, a)
            if ov or un:
                LINES[id(can)] = (layer(rig, ov), layer(rig, un))
            fr.append(can)
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        out[tag] = list(zip(fr, ms))
    out["idle"] = [(fr_, m) for fr_, m in out["idle_base"]]
    acts = with_lines(rig.bake(out, cfg=bake))
    return {t: acts[t] for t in sheet if t in acts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    rig = R.Rig(D, pad=(90, 90, 90, 30))
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        ps = Poser(D.d0)
        ps.check()
        import design_fiora_hd as FD
        with open(lp(JOINTS), encoding="utf-8") as f:
            run = run_poses(json.load(f)["tags"]["run"])
        cells = []
        for name, p in (("low", LOW), ("nock", NOCK), ("half", drawn(0.5)), ("full", drawn(1.0)), ("loose", LOOSE),
                        ("run 0", run[0]), ("run 2", run[2]), ("run 4", run[4]), ("run 6", run[6]),
                        ("dead 2", DEAD[2]), ("dead 5", DEAD[5]), ("dead 7", DEAD[7])):
            a, ov, un = ps.frame(p)
            can = flat(rig, on_rig(rig, a), layer(rig, ov), layer(rig, un))
            ys, xs = np.nonzero(can[..., 3] > 0)
            cells.append((name, FD.shown(Image.fromarray(can[ys.min() - 2:ys.max() + 3, xs.min() - 2:xs.max() + 3]), 1, 6)))
        FD.strip(cells).convert("RGB").save(os.path.join(a.parts, "varus_poses.png"))
        return
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()

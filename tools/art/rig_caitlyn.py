#!/usr/bin/env python3
"""Caitlyn's second design posed for every action after the first design's approved strips (2026-10-03).

    python tools/art/rig_caitlyn.py --cells assets/source/native/caitlyn_cells.json --out assets/source/native
    python tools/art/rig_caitlyn.py --cells ... --out ... --check            # compare with the files in --out
    python tools/art/rig_caitlyn.py --cells ... --out DIR --review DIR --v1 <main's assets/source/native>

Codex's v2 strips (outputs/caitlyn-strips-v2, 13:33) drew new bodies round the design's pasted head: the user found
「头和脖子失去模型 头发失去模型 死亡是动作特别奇怪」 and 「各种模型丢失 模型异常问题」 - and 「你来修复吧 codex太笨了」.
Here every frame is put together from the approved design's own parts (assets/source/caitlyn/design_v2, 45 rows):
- the head (hat, face, the hair beside it: rows -33..-18) and the long back hair, as drawn;
- the torso and the skirt as drawn, the squares the carried rifle and the hands covered painted in the bodice's and
  the skirt's own colours (TORSO, SKIRT);
- the rifle drawn level square by square, traced from oppi's Caitlyn at design A's length (RIFLE_ROWS; the user:
  「枪的细节太差了」, 「枪的元素太少 实在改不好的话就抄oppi的拿回来手描」) and turned whole by RotSprite; the arms along
  shoulder -> elbow -> hand (ARM: the navy sleeve with its brown leather, the gold band, the cream cuff, the brown
  glove; every square within 1 of the line takes the colour at that length and side; a hand out of reach stops at
  the arm's length, never a stretched stick); the legs as oppi draws them (「除了移动的时候 其他时候腿部完全不对」):
  standing, straight down like the idle's and at most SPREAD out under the skirt's corners (slanting legs stepped and
  broke their bands: 「这里腿各种脱节」), two squares thick with the design's garter, knee pad, boot top and buckle
  whole, a near foot moved out turning its toe out; oppi's kneel drawn square by square (KNEEL); the hop back with both legs straight
  down and together off the ground; one outline ring each;
- the idle and the carrying frames: the design's hold (the butt by the near hip, the barrel up past the far
  shoulder) with the traced rifle - the user picked it over the design's own rifle so that the rifle is the same in
  every action (「B」); standing straight on the design's own legs;
- the death's end as oppi's: slumping on her knees, then down on her front (LYING: the head upright with its chin on
  the ground, the body and legs flat behind it, the rifle under her).
The poses follow the first design's strips the user approved (assets/source/native/caitlyn_<tag>.png on main before
this design): aiming from the shoulder, the shots from the hip (the muzzle 7-8 squares over the pivot, so a bullet
flies at the target's pivot nearly level), the kneeling shots, the rifle raised or stood upright, the hop back, the
fall. The frames are drawn in display order on the cells table's standing points (the run: fix_caitlyn_run_v2.py).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

DESIGN = os.path.join(ROOT, "assets", "source", "caitlyn", "design_v2", "caitlyn_design_v2_1x.png")
PIVOT = (64, 88)
Z = 8

PAL = {
    "a": "0A0011", "b": "0C0011", "c": "0A020E", "d": "0D0012", "e": "0F0115", "f": "100216", "g": "110717",
    "h": "23102D", "i": "211930", "j": "1D1C34", "k": "341340", "l": "301A28", "m": "272A50", "n": "451B59",
    "o": "402835", "p": "2F3158", "q": "522063", "r": "30345C", "s": "5C2576", "t": "683934", "u": "1454A9",
    "v": "7A4429", "w": "915526", "x": "CB516B", "y": "27CCE2", "z": "D7AE50", "A": "E1A58E", "B": "FCBE2E",
    "C": "FDC429", "D": "E3CB92", "E": "FAD3BA", "F": "EAE0A8", "G": "EDDDB1", "H": "FEEEA3", "I": "F9F8F9",
    # the rifle's dark wood, old gold, blue lens and pale gleams, traced from oppi's Caitlyn (the user: 「枪的元素太少
    # 实在改不好的话就抄oppi的拿回来手描」)
    "K": "503714", "O": "B2863E", "L": "4C83C6", "M": "F9FA9D", "P": "704C1E", "Q": "DFAE54", "S": "A1A3B8",
}
RING = "d"


def rgba(ch):
    h = PAL[ch]
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255], np.uint8)


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) else pre + p


# ---------------------------------------------------------------------------------------------------------------
# the design's parts, squares relative to the standing point

def design():
    return np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))


def grab(d, x0, x1, y0, y1, keep=None):
    out = {}
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = d[PIVOT[1] + y, PIVOT[0] + x]
            if c[3] and (keep is None or keep(x, y)):
                out[(x, y)] = c.copy()
    return out


# the torso (rows -17..-8) with the near arm, the far hand and the carried rifle taken off, rows of characters from
# x = -6 ("." empty): the design's collar, bodice and leather as drawn, the squares under the rifle and the hands in
# the bodice's purple, a gold waist band and the belt
TORSO_X0 = -6
TORSO = [
    # -6-5-4-3-2-1 0 1 2 3
    "..dpFdCd..",     # -17
    ".dwpaFCCd.",     # -16
    ".dowdFFsd.",     # -15
    ".dotdsssd.",     # -14
    ".ddoqqqqd.",     # -13
    ".diioqqqd.",     # -12
    "..doqqqsd.",     # -11
    "..doqqssd.",     # -10
    "..doqqqqd.",     # -9
    "..dvwCwvd.",     # -8: the belt and its buckle
]
# the skirt (rows -7..-2) without the rifle's butt and the near glove: the right half as drawn, mirrored to the left
SKIRT_X0 = -6
SKIRT = [
    # -6-5-4-3-2-1 0 1 2 3 4 5
    ".dsssCqsssd.",   # -7
    "dsCssCqssCsd",   # -6
    "dsCssCCssCsd",   # -5
    "dFFFFFCsCHFd",   # -4
    "ddtgpFFHge..",   # -3
    "dCtCvedovCd.",   # -2
]


def grid(rows, x0, y0):
    out = {}
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch != ".":
                out[(x0 + j, y0 + i)] = rgba(ch)
    return out


def parts(d):
    return {
        "head": grab(d, -13, 5, -33, -18),                                    # hat, face, the hair beside it
        "hair": grab(d, -13, -8, -17, -11, lambda x, y: x <= -9 or y == -17),  # the long hair under it
        "torso": grid(TORSO, TORSO_X0, -17),
        "skirt": grid(SKIRT, SKIRT_X0, -7),
        "legs": grab(d, -13, 14, -1, 11),                                     # standing straight: as drawn
    }


# ---------------------------------------------------------------------------------------------------------------
# parts drawn along a line

def seg(p, a, b):
    """(distance, t along a -> b, side: + right of the direction) of point p to segment a -> b."""
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    n = math.hypot(vx, vy) or 1e-9
    ux, uy = vx / n, vy / n
    t = max(0.0, min(n, (p[0] - ax) * ux + (p[1] - ay) * uy))
    qx, qy = ax + ux * t, ay + uy * t
    side = (p[0] - qx) * uy - (p[1] - qy) * ux
    return math.hypot(p[0] - qx, p[1] - qy), t, side


def chain(points, half, colour):
    """Squares within half(t) of the polyline; colour(t, side) -> rgba. t runs along the whole polyline."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    lens = [math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]) for i in range(len(points) - 1)]
    out = {}
    for y in range(int(math.floor(min(ys))) - 3, int(math.ceil(max(ys))) + 4):
        for x in range(int(math.floor(min(xs))) - 3, int(math.ceil(max(xs))) + 4):
            best = None
            acc = 0.0
            for i in range(len(points) - 1):
                dist, t, side = seg((x, y), points[i], points[i + 1])
                if best is None or dist < best[0] - 1e-9:
                    best = (dist, acc + t, side)
                acc += lens[i]
            if best[0] <= half(best[1]):
                out[(x, y)] = colour(best[1], best[2])
    return out


def ring(cells):
    r = set()
    for x, y in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells:
                r.add(q)
    return r


def knee(hip, ankle, lt, ls, forward=1):
    hx, hy = hip
    ax, ay = ankle
    dx, dy = ax - hx, ay - hy
    dist = math.hypot(dx, dy)
    if dist >= lt + ls - 1e-6:
        return hx + dx * lt / (lt + ls), hy + dy * lt / (lt + ls)
    a = (lt * lt - ls * ls + dist * dist) / (2 * dist)
    h = math.sqrt(max(0.0, lt * lt - a * a))
    mx, my = hx + dx * a / dist, hy + dy * a / dist
    nx, ny = -dy / dist, dx / dist
    if nx * forward < 0:
        nx, ny = -nx, -ny
    return mx + nx * h, my + ny * h


# the rifle drawn level square by square, traced from oppi's Caitlyn and fitted to design A's length (the user: 「枪的
#细节太差了」, then 「枪的元素太少 实在改不好的话就抄oppi的拿回来手描」): rows from the top, columns from the butt;
# RIFLE_AT is the body's top row at the butt (the point a pose gives). The round gold butt knob with its white gleam,
# the dark wooden wrist (the near hand), the gold receiver with white gleams, a blue stone and the trigger, the gold
# scope over the chamber (blue lens, white under it), the barrel of dark wood bound in gold with pale gleams, the gold
# muzzle. Turned whole by RotSprite (quarter turns exactly; pointing back it is turned over first); one outline ring.
RIFLE_ROWS = [
    ".OO.......OQO......OQMQO.........",
    "OQHPKKPv.OCIIQKQ..KQLLQK.........",
    "PIIQKPvwOQCQLQKPQKKOQQOKQMQPQMQPC",
    "KQOPKKPKKOQKKPKKQPKSIIIKPKKPKKPKC",
    ".KP.......PC.....................",
]
RIFLE_AT = (0, 2)
RIFLE_LEN = 32.0                                  # the anchor to the muzzle's last square
GRIP, FORE = 6.0, 17.0                            # where the near hand (the wrist) and the far hand (the chamber) hold it


def rifle(butt, deg):
    """The rifle's squares: its barrel's top row at the butt on butt, pointing deg (counter-clockwise from right);
    pointing back (over 90 degrees) it is turned over first, so its grip and trigger still face down."""
    import rig_nocturne as RN
    h, w = len(RIFLE_ROWS), len(RIFLE_ROWS[0])
    a = np.zeros((h, w, 4), np.uint8)
    for y, row in enumerate(RIFLE_ROWS):
        for x, ch in enumerate(row):
            if ch != ".":
                a[y, x] = rgba(ch)
    jx, jy = RIFLE_AT
    deg = deg % 360
    if 90 < deg < 270:
        a = a[::-1].copy()
        jy = h - 1 - jy
    if deg % 90 == 0:
        for _ in range(int(deg // 90)):
            a = np.rot90(a).copy()
            jx, jy = jy, a.shape[0] - 1 - jx
        r, (rx, ry) = a, (jx, jy)
    else:
        r, (rx, ry) = RN.rotsprite(a, (jx, jy), deg)
    bx, by = int(round(butt[0])), int(round(butt[1]))
    return {(bx + xx - rx, by + yy - ry): r[yy, xx].copy() for yy, xx in zip(*np.nonzero(r[..., 3]))}


def rifle_point(butt, deg, t, down=0.5):
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)
    nx, ny = -uy, ux
    if ny < 0:
        nx, ny = -nx, -ny
    return butt[0] + ux * t + nx * down, butt[1] + uy * t + ny * down


# the arm from the shoulder: (length, the two fill columns' colours, left / right of the arm going down)
ARM = [(1.0, "rr"), (3.0, "rw"), (1.0, "CC"), (2.5, "rr"), (1.0, "FF"), (1.5, "wv")]
ARM_HALF = 1.0
ARM_UP, ARM_LOW = 4.5, 4.5                     # shoulder -> elbow, elbow -> the glove's middle


def arm(shoulder, hand, out_dir=-1):
    """The arm's squares from shoulder to hand (the glove), the elbow bent toward out_dir (-1 back/left, +1 forward)."""
    dx, dy = hand[0] - shoulder[0], hand[1] - shoulder[1]
    reach = math.hypot(dx, dy)
    if reach > ARM_UP + ARM_LOW:                 # never a stretched stick arm: the glove stops at the arm's reach
        k = (ARM_UP + ARM_LOW) / reach
        hand = (shoulder[0] + dx * k, shoulder[1] + dy * k)
    e = knee(shoulder, hand, ARM_UP, ARM_LOW, forward=out_dir)

    def colour(t, side):
        acc = 0.0
        for n, cols in ARM:
            if t <= acc + n:
                return rgba(cols[0 if side < 0 else 1])
            acc += n
        return rgba(ARM[-1][1][0 if side < 0 else 1])
    return chain([shoulder, e, hand], lambda t: ARM_HALF, colour)


# the leg: hip at row -2, knee in the knee pad's row, ankle between the foot's rows (the design's left leg)
HIP_Y, KNEE_Y, ANKLE_Y, TOE = -2.0, 2.0, 9.5, 1.0
LT, LS = KNEE_Y - HIP_Y, ANKLE_Y - KNEE_Y
# the design leg's two fill columns, row by row: the thigh (navy, the garter, the knee pad) and the shin (navy, the
# boot top, the boot, the buckle); a bone drawn shorter keeps its bands whole and drops navy rows first. Bone lines
# coloured square by square scattered the bands into gold specks on every slanted leg (「腿有点变形」)
THIGH_END = ["Ct", "vw"]
SHIN_END = ["CC", "vv", "vw", "vC"]
FOOT = ["vvw", "tvw"]                            # the foot's two rows under a standing shin, the toe forward
FOOT_OUT = ["wvv", "wvt"]                        # a near foot planted wide: the toe out to the left, as oppi's
SPREAD = 2.0                                     # how far a standing leg moves out from its hip (the skirt's corners)
FOOT_FLAT = ["vt", "wv"]                         # at the end of a level shin: two columns, top and bottom


def leg_materials(d):
    return None                                  # the leg's colours are the design's, spelled out above


def bands(n, end, fill="rr"):
    if n <= 0:
        return []
    if n > len(end):
        return [fill] * (n - len(end)) + end
    return {1: [end[-1]], 2: [end[0], end[-1]], 3: [end[0], end[-2], end[-1]]}.get(n, end[len(end) - n:])


def steep(a, b):
    return abs(b[1] - a[1]) >= abs(b[0] - a[0])


def by_rows(a, b, rows, end, out):
    """The bone a -> b on the given rows, two squares wide round the line, its bands from a to b; returns the last
    row's first column."""
    mats = bands(len(rows), end)
    c0 = int(math.floor(a[0] - 0.5))
    for i, y in enumerate(rows):
        t = (y - a[1]) / (b[1] - a[1]) if b[1] != a[1] else 1.0
        x = a[0] + (b[0] - a[0]) * min(1.0, max(0.0, t))
        c0 = int(math.floor(x - 0.5))
        for j, ch in enumerate(mats[i]):
            out[(c0 + j, y)] = rgba(ch)
    return c0


def by_cols(a, b, cols, end, out):
    """The bone a -> b on the given columns, two squares tall round the line, its bands from a to b."""
    mats = bands(len(cols), end)
    for i, x in enumerate(cols):
        t = (x - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 1.0
        y = a[1] + (b[1] - a[1]) * min(1.0, max(0.0, t))
        r0 = int(math.floor(y - 0.5))
        for j, ch in enumerate(mats[i]):
            out[(x, r0 + j)] = rgba(ch)


def span(p0, p1):
    s = 1 if p1 >= p0 else -1
    return list(range(p0, p1 + s, s))


def leg(hip, ankle, mats=None, kneel=None, out_dir=None):
    """One leg drawn as pixel art: the thigh hip -> knee and the shin knee -> ankle two squares thick, row by row (or
    column by column where a bone lies flatter than 45 degrees), the design's bands whole, the foot toe forward under
    a standing shin or at the end of a level one. The knee bends forward (out_dir +1) unless told otherwise, or sits
    where kneel puts it."""
    out = False
    if kneel is not None:
        k = kneel
    else:
        # standing: the leg straight down like the idle's, at most SPREAD squares out from the hip so its top stays
        # under the skirt's hem; a slanting leg stepped a square every few rows and every band broke at the steps
        # (the user: 「这里腿各种脱节」)
        x = min(max(ankle[0], hip[0] - SPREAD), hip[0] + SPREAD)
        out = x < hip[0] - 0.75                   # a near leg moved out to the left turns its toe out, as oppi's
        hip, ankle = (x, hip[1]), (x, ankle[1])
        f = LT / (LT + LS)
        k = (hip[0] + (ankle[0] - hip[0]) * f, hip[1] + (ankle[1] - hip[1]) * f)
    cells = {}
    kr = int(math.floor(k[1] + 0.5))              # the knee pad's row
    kc = int(math.floor(k[0]))                    # ... and column
    if steep(hip, k):
        by_rows(hip, k, span(int(math.floor(hip[1])) + 1, kr), THIGH_END, cells)
    else:
        by_cols(hip, k, span(int(math.floor(hip[0])), kc), THIGH_END, cells)
    if steep(k, ankle):
        ar = int(math.floor(ankle[1]))            # the foot's first row
        c0 = by_rows(k, ankle, span(kr + 1, ar - 1), SHIN_END, cells)
        # the foot right under the shin's last row, its toe out to the left on a near leg moved out (as oppi's): a toe
        # turned in under it read as a broken ankle
        if out:
            foot, c0 = FOOT_OUT, c0 - 1
        else:
            foot = FOOT
        for i, row in enumerate(foot):
            for j, ch in enumerate(row):
                cells[(c0 + j, ar + i)] = rgba(ch)
    else:
        s = 1 if ankle[0] > k[0] else -1
        first = int(math.floor(k[0] - 0.5)) + (2 if s > 0 else -1)
        last = int(math.floor(ankle[0]))
        cols = span(first, last)
        by_cols(k, ankle, cols, SHIN_END, cells)
        r0 = int(math.floor(ankle[1] - 0.5))
        for i, col in enumerate(FOOT_FLAT):
            for j, ch in enumerate(col):
                cells[(cols[-1] + s * (i + 1), r0 + j)] = rgba(ch)
    return cells


# legs drawn square by square (oppi's kneel: the near knee on the ground and its shin flat behind, the far shin
# upright under a level thigh), rows from KNEEL_Y, columns from X0; the far one first
X0 = -12
KNEEL_Y = 4
KNEEL = {
    "far": ["..............rrrCvw..",
            "..............rrrtvw..",
            "..................rr..",
            "..................CC..",
            "..................vw..",
            "..................vvw.",
            "..................tvw."],
    "near": [".........rr...........",
             ".........rr...........",
             ".........rr...........",
             ".........rr...........",
             ".........Ct...........",
             "..vvvCrrrvw...........",
             "..tvwCrrrvw..........."],
}


# lying on her front as oppi's Caitlyn lies at the end of her death: the head upright with its chin on the ground,
# the jacket, the skirt and the legs flat behind it to the left, the rifle on the ground under her; the death's lying
# frames turned the whole upper body a quarter turn instead and laid the face on its side (the user: 「还是看了怪」)
LYING_X0, LYING_Y0 = -25, 4
LYING = {
    "far": ["......................",
            "......................",
            "......................",
            "..tvvCrrvCtrr.........",
            "..vvwCrrwCtrr.........",
            "......................",
            "......................"],
    "near": ["......................",
             "......................",
             "......................",
             "......................",
             "......................",
             "tvvwCrrrvCtrr.........",
             "vvwwCrrrwCtrr........."],
    "body": [".............mmmmmm....",
             "...........dqsssqmmmm..",
             "..........CsssssqqFdm..",
             ".........CsCsssqoqFFw..",
             ".........FsCssqqoqFwo..",
             "........FCssssqqoqqwo..",
             "........FCCCCCqqoqqqo.."],
}
LYING_HEAD = (7, 28)                # the head's move from standing: its chin on the ground in front of the body


def grid_cells(rows, y0, dx=0, dy=0):
    out = {}
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch != ".":
                out[(X0 + j + dx, y0 + i + dy)] = rgba(ch)
    return out


def run_leg(phase, dx=0, dy=0):
    """A leg of the approved run (tools/art/fix_caitlyn_run_v2.py LEG, its near hip on columns -3/-2)."""
    import fix_caitlyn_run_v2 as RUN
    return grid_cells(RUN.LEG[phase], RUN.Y0, dx, dy)


# ---------------------------------------------------------------------------------------------------------------
# a frame

class Canvas:
    def __init__(self, w, h, pivot):
        self.a = np.zeros((h, w, 4), np.uint8)
        self.p = pivot

    def put(self, cells, dx=0, dy=0, outline=True, behind=False):
        if outline:
            for x, y in ring(cells):
                self._set(x + dx, y + dy, rgba(RING), behind)
        for (x, y), c in cells.items():
            self._set(x + dx, y + dy, c, behind)

    def _set(self, x, y, c, behind):
        tx, ty = self.p[0] + int(round(x)), self.p[1] + int(round(y))
        if 0 <= tx < self.a.shape[1] and 0 <= ty < self.a.shape[0]:
            if behind and self.a[ty, tx, 3]:
                return
            self.a[ty, tx] = c


def shift(cells, dx, dy):
    return {(x + dx, y + dy): c for (x, y), c in cells.items()}


SHOULDER = {"near": (-5.0, -15.5), "far": (1.5, -15.5)}
HIPS = {"near": -3.5, "far": 2.5}               # the design's legs, straight down
STAND = {"near": (-3.5, 0), "far": (2.5, 0)}


def place_rotated(dst, layer, about, deg):
    """RotSprite the layer (an RGBA canvas) about the point about (canvas squares) and lay it over dst."""
    import rig_nocturne as RN
    ys, xs = np.nonzero(layer[..., 3])
    if not len(ys):
        return
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = layer[y0:y1, x0:x1]
    j = (about[0] - x0, about[1] - y0)
    r, (jx, jy) = RN.rotsprite(crop, j, deg)
    ox, oy = int(round(about[0] - jx)), int(round(about[1] - jy))
    for yy, xx in zip(*np.nonzero(r[..., 3])):
        ty, tx = oy + yy, ox + xx
        if 0 <= ty < dst.shape[0] and 0 <= tx < dst.shape[1]:
            dst[ty, tx] = r[yy, xx]


def compose_lying(P, pose, cell, pivot):
    """The lying frames: the rifle under her, the far leg, the near leg, the body, the head upright on top."""
    cv = Canvas(cell[0], cell[1], pivot)
    hx, hy = pose.get("head", (0, 0))
    cv.put(rifle(pose.get("rifle_at", (-15.0, 8.0)), 0))
    for part in ("far", "near", "body"):
        cells = {}
        for i, row in enumerate(LYING[part]):
            for j, ch in enumerate(row):
                if ch != ".":
                    cells[(LYING_X0 + j, LYING_Y0 + i)] = rgba(ch)
        cv.put(cells)
    cv.put(shift(P["head"], LYING_HEAD[0] + hx, LYING_HEAD[1] + hy), outline=False)
    cv.a[pivot[1] + 12:] = 0
    return cv.a


def compose(P, mats, pose, cell, pivot):
    """One frame of a pose:
    body (dx, dy): the upper parts, the shoulders and the hips; head (dx, dy) more;
    rifle (butt x, y, degrees: its body's top row at the butt) with the hands near / far: t along the rifle (the
      near glove at the wrist, the far one under the scope) or (x, y);
    legs: near / far as (ankle x, lift) or {"ankle": (x, y), "knee": (x, y)} (the knee placed);
    rifle_z: "front" (over the near arm too), "behind" (behind the head and the torso) or default (over the head);
    rot (degrees, (x, y)): the upper body turned about that point (+ counter-clockwise), the legs not;
    loose_rifle (x, y, degrees): a rifle not in her hands (drawn last, not turned)."""
    if pose.get("lying"):
        return compose_lying(P, pose, cell, pivot)
    cv = Canvas(cell[0], cell[1], pivot)
    if "loose_rifle" in pose and pose.get("loose_back"):     # lying on the ground behind her legs
        lx, ly, ld = pose["loose_rifle"]
        cv.put(rifle((lx, ly), ld))
    bx, by = pose.get("body", (0, 0))
    hx, hy = pose.get("head", (0, 0))
    hips = pose.get("hips", HIPS)
    legs = pose.get("legs", STAND)
    if legs == STAND and hips == HIPS and by == 0:
        cv.put(shift(P["legs"], bx, 0), outline=False)        # the design's own legs, square for square
        legs = {}
    for name in [n for n in ("far", "near") if n in legs]:
        spec = legs[name]
        hip = (hips[name] + bx, HIP_Y + by)
        if isinstance(spec, dict) and "kneel" in spec:           # oppi's kneel, drawn square by square
            cells = grid_cells(KNEEL[name], KNEEL_Y, spec.get("dx", 0))
        elif isinstance(spec, dict) and "run" in spec:           # a leg of the approved run
            cells = run_leg(spec["run"], spec.get("dx", 0), spec.get("dy", 0))
        elif isinstance(spec, dict):
            cells = leg(hip, spec["ankle"], mats, kneel=spec.get("knee"))
        else:
            cells = leg(hip, (spec[0], ANKLE_Y - spec[1]), mats)
        cv.put(cells)
    up = Canvas(cell[0], cell[1], pivot)
    sh = {k: (x + bx, y + by) for k, (x, y) in SHOULDER.items()}
    rz = pose.get("rifle_z", "")
    gun = None
    rx = ry = deg = 0
    if "rifle" in pose:
        rx, ry, deg = pose["rifle"]
        gun = rifle((rx, ry), deg)

    def hand(spec, down):
        if isinstance(spec, tuple):
            return spec
        return rifle_point((rx, ry), deg, spec, down=down)

    up.put(shift(P["hair"], bx + hx, by + hy), outline=False)
    if gun is not None and rz == "behind":
        up.put(gun)
    if "far" in pose:
        up.put(arm(sh["far"], hand(pose["far"], pose.get("far_down", 1.5)), pose.get("far_elbow", -1)))
    up.put(shift(P["skirt"], bx, by), outline=False)
    up.put(shift(P["torso"], bx, by), outline=False)
    up.put(shift(P["head"], bx + hx, by + hy), outline=False)
    if gun is not None and rz == "":
        up.put(gun)
    if "near" in pose:
        up.put(arm(sh["near"], hand(pose["near"], pose.get("near_down", 2.0)), pose.get("near_elbow", -1)))
    if gun is not None and rz == "front":
        up.put(gun)
    if "rot" in pose:
        deg_r, (ax, ay) = pose["rot"]
        lay = np.zeros_like(cv.a)
        place_rotated(lay, up.a, (pivot[0] + ax, pivot[1] + ay), deg_r)
        if pose.get("ground"):                   # lying: the turned body's lowest square on the feet line
            ys = np.nonzero(lay[..., 3].any(1))[0]
            move = pivot[1] + 11 - ys.max()
            if pose["ground"] != "lift" or move < 0:  # "lift": only out of the ground, never down onto it
                lay = np.roll(lay, move, 0)
        m = lay[..., 3] > 0
        cv.a[m] = lay[m]
    else:
        m = up.a[..., 3] > 0
        cv.a[m] = up.a[m]
    if "loose_rifle" in pose and not pose.get("loose_back"):
        lx, ly, ld = pose["loose_rifle"]
        cv.put(rifle((lx, ly), ld))
    cv.a[pivot[1] + 12:] = 0
    return cv.a


# ---------------------------------------------------------------------------------------------------------------
# the poses, after the first design's strips (main's assets/source/native/caitlyn_<tag>.png); this design's chin is 4
# rows higher than the first one's, so the rifle heights are taken 4 rows up; its legs (thigh 4, shin and boot 7.5)
# kneel 6 rows down: the near knee on the ground (its thigh drawn a little longer), the far shin upright

def wide(n=-6.5, f=5.5, ln=0, lf=0):
    return {"near": (n, ln), "far": (f, lf)}


def kneel_legs(dx=0):
    return {"near": {"kneel": True, "dx": dx}, "far": {"kneel": True, "dx": dx}}


BUTT = (-8.5, -14.0)                 # the aimed rifle's butt at the near shoulder


def aim(deg=0.0, up=0.0, dy=1, dx=0, legs=None, near=GRIP, far=FORE, head=(0, 0), **kw):
    """Aiming from the near shoulder: the butt at the shoulder, the near glove at the grip under the stock, the far one
    under the barrel; up raises the rifle, dy lowers the whole upper body (a crouch)."""
    p = {"rifle": (BUTT[0] + dx, BUTT[1] - up + dy, deg), "near": near, "far": far, "near_down": 2.5,
         "rifle_z": "front", "body": (dx, dy), "head": head, "legs": legs or wide()}
    p.update(kw)
    return p


def kneel(deg=0.0, up=0.0, dy=6, **kw):
    kw.setdefault("legs", kneel_legs())
    return aim(deg=deg, up=up, dy=dy, **kw)


CARRY = (-10.0, -5.0, 38)            # the idle's hold: the butt at the near hip, the barrel up past the far shoulder


def carry(dy=0, dx=0, legs=None, head=(0, 0), **kw):
    """The idle's hold with the traced rifle (the user picked it over the design's own rifle: 「B」), as the design
    holds hers: the butt by the near hip, the near glove at the wrist, the far one under the scope."""
    p = {"rifle": (CARRY[0] + dx, CARRY[1] + dy, CARRY[2]), "near": GRIP, "far": FORE, "near_down": 2.0,
         "rifle_z": "front", "body": (dx, dy), "head": head, "legs": legs or STAND}
    p.update(kw)
    return p


def staff(dy=0, dx=0, legs=None, head=(0, 0), far=None, **kw):
    """The rifle stood upright at her near side like a staff, the near glove round it; far: the far hand's point."""
    p = {"rifle": (-10.0 + dx, 1.0 + dy, 90), "near": 11.0, "near_down": -0.5, "rifle_z": "",
         "body": (dx, dy), "head": head, "legs": legs or STAND}
    if far is not None:
        p["far"] = far
    p.update(kw)
    return p


# the hop back: both legs straight down and together, off the ground (the run's legs there, one swung forward and one
# tucked back, made a big crossing stride in the middle of a skill: 「放技能时怎么大交叉步啊 看的这么有违和感」)
HOP = {"near": (-4.5, 2), "far": (1.5, 2)}
HOP2 = {"near": (-4.5, 1), "far": (1.5, 1)}

POSES = {
    # main's attack, shown in display order (import_native's ORDER for the first design is gone): aimed at the chest,
    # lowering, the shot from the hip held two slots (3-4: the barrel 7 squares over the pivot, so the bullet flies to
    # the target's pivot nearly level - "平A出去的子弹看起来是歪的"), the recoil, back to the idle's hold; the legs straight
    # and apart as oppi's
    "attack": [
        aim(deg=2),
        aim(deg=0, up=-3),
        aim(deg=0, up=-6),
        aim(deg=0, up=-6),
        aim(deg=5, up=-5),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's passive (the Headshot): aimed, down into a wider stance (2-3), the shot from the hip held two slots (4-5),
    # back to the idle's hold
    "passive": [
        aim(deg=2),
        aim(deg=0, dy=2, legs=wide(-8.5, 7.5)),
        aim(deg=0, up=-1, dy=2, legs=wide(-8.5, 7.5)),
        aim(deg=0, up=-4, dy=2, legs=wide(-8.0, 7.0)),
        aim(deg=0, up=-4, dy=2, legs=wide(-8.0, 7.0)),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's Q: the rifle swung up behind the head, brought round across the body, then down on one knee aiming level
    # (3-6, oppi's kneel), the shot (7), up again
    "skill": [
        {"rifle": (6.0, -15.0, 150), "near": 4.0, "far": 10.0, "near_down": 1.5, "rifle_z": "behind",
         "legs": wide(-5.5, 4.5), "body": (0, 1)},
        {"rifle": (-7.5, -9.0, 28), "near": GRIP, "far": FORE, "near_down": 2.0, "rifle_z": "front",
         "legs": wide(-6.5, 5.5), "body": (0, 1)},
        kneel(dy=5),
        kneel(),
        kneel(),
        kneel(up=0.5),
        kneel(dx=-1),                     # 7: the shot, the recoil a square back
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's W: the rifle stood at her side, she bends a little and the far hand throws the trap forward (4), up again
    "skill2": [
        staff(far=(4.0, -9.0)),
        staff(dy=1, dx=1, head=(1, 0), legs=wide(-5.0, 4.0), far=(6.0, -8.0)),
        staff(dy=2, dx=1, head=(1, 1), legs=wide(-6.5, 5.5), far=(7.0, -6.0)),
        staff(dy=2, dx=2, head=(1, 1), legs=wide(-7.5, 6.5), far=(14.0, -3.0)),
        staff(dy=1, dx=1, head=(1, 0), legs=wide(-6.0, 5.0), far=(8.0, -6.0)),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's E: aimed, lower, the net's shot (3), the hop back - off the ground, legs together (4-5), landing (6-7),
    # back to the idle's hold
    "e": [
        aim(deg=2),
        aim(deg=1, dy=2, legs=wide(-7.5, 6.5)),
        aim(deg=0, dy=2, legs=wide(-7.5, 6.5)),   # 3: the net's shot
        aim(deg=6, up=0.5, dx=-1, dy=-2, legs=HOP),
        aim(deg=3, dx=-1, dy=-1, legs=HOP2),
        aim(deg=0, dy=2, legs=wide(-8.0, 7.0)),
        aim(deg=1, dy=2, legs=wide(-7.5, 6.5)),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's R: the rifle raised high, down on one knee with it, aiming level (3-6), the shot (7), lower (8), up again
    "ult": [
        {"rifle": (-4.0, -11.0, 58), "near": GRIP, "far": 14.0, "near_down": 2.0, "rifle_z": "front",
         "legs": wide(-5.0, 4.0), "body": (0, 0)},
        {"rifle": (-7.0, -6.0, 38), "near": GRIP, "far": FORE, "near_down": 2.0, "rifle_z": "front",
         "legs": kneel_legs(), "body": (0, 5)},
        kneel(),
        kneel(),
        kneel(up=0.5),
        kneel(),
        kneel(dx=-1),                     # 7: the shot, a square of recoil
        kneel(dy=7),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's hit: thrown back while aiming, then back in the idle's hold a square behind
    "hit": [
        aim(deg=-4, dx=-1, up=-1, head=(-1, 0)),
        carry(dx=-1, legs=wide(-5.5, 4.5)),
    ],
}


def death():
    """main's death: struck, down on one knee leaning on the upright rifle (2), sinking lower (3-4), falling forward
    - the upper body turned about the hips while the rifle tips away (5-6) - lying on the ground (7-8)."""
    out = [
        aim(deg=12, up=1, dx=-1, head=(-1, 0)),
        staff(dy=6, legs=kneel_legs(), head=(1, 1), far=(4.0, -2.0)),
        staff(dy=7, legs=kneel_legs(), head=(1, 2), far=(4.0, -1.0)),
        staff(dy=7, legs=kneel_legs(), head=(1, 2), far=(4.0, -1.0)),
    ]
    # slumping on her knees, then down on her front as oppi's (the head upright, the body flat behind it): a turned
    # upper body with its face on its side read as strange (「还是看了怪」)
    out.append({"body": (0, 8), "head": (1, 2), "legs": kneel_legs(), "near": (-6.0, 1.0), "far": (4.0, 0.0),
                "loose_rifle": (-11.0, 9.0, 70), "loose_back": True})
    out.append({"lying": True, "head": (0, -2)})
    out.append({"lying": True})
    out.append({"lying": True})
    return out


POSES["dead"] = death()
POSES["idle"] = [carry() for _ in range(6)]       # the design's hold, the traced rifle; import_native's BOB breathes it


def build(tag, P, mats, cells):
    cell = cells["cell"][:2]
    return [compose(P, mats, POSES[tag][k], cell, fr["pivot"]) for k, fr in enumerate(cells["tags"][tag])]


def strip(frames, cell, cols):
    rows = (len(frames) + cols - 1) // cols
    a = np.zeros((rows * cell[1], cols * cell[0], 4), np.uint8)
    for k, c in enumerate(frames):
        a[(k // cols) * cell[1]:(k // cols + 1) * cell[1], (k % cols) * cell[0]:(k % cols + 1) * cell[0]] = c
    return a


def review(tag, frames, cells, v1_png, v1_cells, out, z=5):
    """The first design's frames (top) over this design's (bottom), a grid every 5 squares round the standing point."""
    from PIL import ImageDraw
    X0, X1, Y0, Y1 = -24, 34, -42, 13
    cw, ch = v1_cells["cell"][:2]
    a = np.asarray(Image.open(lp(v1_png)).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    cols = a.shape[1] // cw

    def tile(c, pivot):
        px, py = pivot
        cc = np.pad(c, ((70, 70), (70, 70), (0, 0)))[py + 70 + Y0:py + 70 + Y1 + 1, px + 70 + X0:px + 70 + X1 + 1]
        im = Image.new("RGBA", (cc.shape[1], cc.shape[0]), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(cc)))
        im = im.resize((cc.shape[1] * z, cc.shape[0] * z), Image.NEAREST).convert("RGB")
        dr = ImageDraw.Draw(im)
        for x in range(X0, X1 + 1):
            if x % 5 == 0:
                dr.line([((x - X0) * z, 0), ((x - X0) * z, im.size[1])], fill=(255, 80, 80) if x == 0 else (120, 130, 95))
        for y in range(Y0, Y1 + 1):
            if y % 5 == 0:
                dr.line([(0, (y - Y0) * z), (im.size[0], (y - Y0) * z)], fill=(255, 80, 80) if y == 0 else (120, 130, 95))
        return im
    v1 = v1_cells["tags"][tag]
    tops = [tile(a[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw], v1[k]["pivot"])
            for k in range(len(v1))]
    bots = [tile(c, fr["pivot"]) for c, fr in zip(frames, cells["tags"][tag])]
    w, h = tops[0].size
    img = Image.new("RGB", (len(tops) * (w + 4), 2 * h + 8), (30, 30, 30))
    for k in range(len(tops)):
        img.paste(tops[k], (k * (w + 4), 0))
        img.paste(bots[k], (k * (w + 4), h + 8))
    img.save(lp(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", required=True, help="the strips' cells table (frame counts, ms, standing points)")
    ap.add_argument("--out", required=True, help="directory for caitlyn_<tag>.png (8x)")
    ap.add_argument("--only", default="")
    ap.add_argument("--review", default="", help="directory for review_<tag>.png against the first design")
    ap.add_argument("--v1", default="", help="the first design's assets/source/native (for --review)")
    ap.add_argument("--check", action="store_true", help="compare with the strips in --out instead of writing them")
    a = ap.parse_args()
    cells = json.load(open(lp(a.cells), encoding="utf-8"))
    d = design()
    P = parts(d)
    mats = leg_materials(d)
    tags = a.only.split(",") if a.only else list(POSES)
    os.makedirs(lp(a.out), exist_ok=True)
    v1_cells = json.load(open(lp(os.path.join(a.v1, "caitlyn_cells.json")), encoding="utf-8")) if a.v1 else None
    for tag in tags:
        frames = build(tag, P, mats, cells)
        n = len(frames)
        cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
        s1 = np.repeat(np.repeat(strip(frames, cells["cell"][:2], cols), Z, 0), Z, 1)
        path = os.path.join(a.out, "caitlyn_%s.png" % tag)
        if a.check:
            same = np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")), s1)
            print(tag, "same" if same else "DIFFERENT")
            continue
        Image.fromarray(s1).save(lp(path))
        if a.review:
            os.makedirs(lp(a.review), exist_ok=True)
            review(tag, frames, cells, os.path.join(a.v1, "caitlyn_%s.png" % tag), v1_cells,
                   os.path.join(a.review, "review_%s.png" % tag))
        print(tag, n, "frames")


if __name__ == "__main__":
    main()

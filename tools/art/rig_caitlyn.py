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
- the rifle drawn along its line from the butt (RIFLE: the gold butt plate, the ivory stock, the brown grip, the gold
  receiver and the long one-square gold barrel, 29.5 squares as design A's), the arms along shoulder -> elbow -> hand
  (ARM: the navy sleeve with its brown leather, the gold band, the cream cuff, the brown glove; a hand out of reach
  stops at the arm's length, never a stretched stick) and the legs along hip -> knee -> ankle -> toe (the design's
  leg, as tools/art/fix_caitlyn_run_v2.py) - every square within the part's half width of its line takes the
  design's colour at that length and side, then one outline ring;
- in the carrying frames (the idle's pose) the design's whole upper body as drawn;
- the death's fall and the lying frames: the upper body turned about the hips (RotSprite, tools/art/rig_nocturne.py)
  and laid on the feet line, the rifle loose beside her.
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
        "upper": grab(d, -13, 14, -33, -2),                                   # the carrying frames: as drawn
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


# the rifle, from the butt: (length, colours of its rows from the top line down); the top line is straight, the stock
# hangs deeper under it
RIFLE = [
    (1.5, "CCC"),      # the butt plate
    (3.0, "FFD"),      # the ivory stock, deep at the butt
    (2.5, "FD"),       # ... narrowing to the wrist
    (2.0, "wv"),       # the grip (the near hand)
    (4.0, "CH"),       # the receiver
    (15.0, "C"),       # the barrel
    (1.5, "B"),        # the muzzle
]
RIFLE_LEN = sum(n for n, _ in RIFLE)


def rifle(butt, deg):
    """The rifle's squares: the butt's top corner at butt, pointing deg (counter-clockwise from right)."""
    a = math.radians(deg)
    ux, uy = math.cos(a), -math.sin(a)         # along the rifle
    nx, ny = -uy, ux                             # down from its top line (right of the direction)
    if ny < 0:
        nx, ny = -nx, -ny
    out = {}
    bx, by = butt
    for y in range(int(by) - 34, int(by) + 34):
        for x in range(int(bx) - 34, int(bx) + 34):
            u = (x - bx) * ux + (y - by) * uy
            v = (x - bx) * nx + (y - by) * ny
            if u < -0.5 or u > RIFLE_LEN + 0.5:
                continue
            acc = 0.0
            for n, rows in RIFLE:
                if u <= acc + n or (n, rows) == RIFLE[-1]:
                    k = int(math.floor(v + 0.5))
                    if 0 <= k < len(rows):
                        out[(x, y)] = rgba(rows[k])
                    break
                acc += n
    return out


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


# the leg (tools/art/fix_caitlyn_run_v2.py): hip at row -2, knee in the knee pad's row, ankle between the foot's rows
HIP_Y, KNEE_Y, ANKLE_Y, TOE = -2.0, 2.0, 9.5, 1.0
LT, LS = KNEE_Y - HIP_Y, ANKLE_Y - KNEE_Y


def leg_materials(d):
    rows = {r: (d[PIVOT[1] + r, PIVOT[0] - 4].copy(), d[PIVOT[1] + r, PIVOT[0] - 3].copy()) for r in range(-1, 9)}
    foot = {(r, i): d[PIVOT[1] + r, PIVOT[0] + c].copy() for r in (9, 10) for i, c in enumerate((-4, -3, -2))}
    return rows, foot


def leg(hip, ankle, mats, kneel=None):
    """One leg's squares: hip -> knee -> ankle -> toe, the knee forward (or at kneel: the knee on the ground)."""
    rows, foot = mats
    k = kneel if kneel is not None else knee(hip, ankle, LT, LS)
    sx, sy = ankle[0] - k[0], ankle[1] - k[1]
    n = math.hypot(sx, sy) or 1e-9
    sx, sy = sx / n, sy / n
    ux, uy = sy, -sx
    toe = (ankle[0] + ux * TOE, ankle[1] + uy * TOE)
    lt = math.hypot(k[0] - hip[0], k[1] - hip[1])
    out = {}
    xs = (hip[0], k[0], ankle[0], toe[0])
    ys = (hip[1], k[1], ankle[1], toe[1])
    for y in range(int(math.floor(min(ys))) - 2, int(math.ceil(max(ys))) + 3):
        for x in range(int(math.floor(min(xs))) - 2, int(math.ceil(max(xs))) + 3):
            p = (float(x), float(y))
            d1, t1, s1 = seg(p, hip, k)
            d2, t2, s2 = seg(p, k, ankle)
            d3, _, _ = seg(p, ankle, toe)
            if min(d1, d2, d3) > 1.0:
                continue
            lu = (x - ankle[0]) * ux + (y - ankle[1]) * uy
            lv = (x - ankle[0]) * sx + (y - ankle[1]) * sy
            if lv > -1.0 and (d3 < min(d1, d2) or lv > -0.5):
                i = int(np.argmin([abs(lu - c) for c in (-0.5, 0.5, 1.5)]))
                out[(x, y)] = foot[(9 if lv < 0 else 10, i)]
                continue
            if d1 <= d2:
                along, side = t1 * LT / max(lt, 1e-9), s1
            else:
                along, side = LT + t2 * LS / max(n, 1e-9), s2
            r = int(min(8, max(-1, round(HIP_Y + along))))
            out[(x, y)] = rows[r][0 if side < 0 else 1]
    return out


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


def compose(P, mats, pose, cell, pivot):
    """One frame of a pose:
    body (dx, dy): the upper parts, the shoulders and the hips; head (dx, dy) more;
    carry: the design's upper body as drawn, or rifle (butt x, y, degrees: its top line's end at the butt) with the
      hands near / far: t along the rifle (the near glove at the grip, the far one under the barrel) or (x, y);
    legs: near / far as (ankle x, lift) or {"ankle": (x, y), "knee": (x, y)} (the knee placed);
    rifle_z: "front" (over the near arm too), "behind" (behind the head and the torso) or default (over the head);
    rot (degrees, (x, y)): the upper body turned about that point (+ counter-clockwise), the legs not;
    loose_rifle (x, y, degrees): a rifle not in her hands (drawn last, not turned)."""
    cv = Canvas(cell[0], cell[1], pivot)
    bx, by = pose.get("body", (0, 0))
    hx, hy = pose.get("head", (0, 0))
    hips = pose.get("hips", HIPS)
    legs = pose.get("legs", STAND)
    for name in ("far", "near"):
        spec = legs[name]
        hip = (hips[name] + bx, HIP_Y + by)
        if isinstance(spec, dict):
            cells = leg(hip, spec["ankle"], mats, kneel=spec.get("knee"))
        else:
            cells = leg(hip, (spec[0], ANKLE_Y - spec[1]), mats)
        cv.put(cells)
    up = Canvas(cell[0], cell[1], pivot)
    if pose.get("carry"):
        up.put(shift(P["hair"], bx + hx, by + hy), outline=False)
        up.put(shift(P["upper"], bx, by), outline=False)
        up.put(shift(P["head"], bx + hx, by + hy), outline=False)
    else:
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
    if "loose_rifle" in pose:
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


def kneel_legs(nk=-1.0, na=-8.5, fa=7.0):
    return {"near": {"ankle": (na, 9.5), "knee": (nk, 10.0)}, "far": (fa, 0)}


BUTT = (-8.5, -14.0)                 # the aimed rifle's butt at the near shoulder


def aim(deg=0.0, up=0.0, dy=1, dx=0, legs=None, near=8.0, far=15.0, head=(0, 0), **kw):
    """Aiming from the near shoulder: the butt at the shoulder, the near glove at the grip under the stock, the far one
    under the barrel; up raises the rifle, dy lowers the whole upper body (a crouch)."""
    p = {"rifle": (BUTT[0] + dx, BUTT[1] - up + dy, deg), "near": near, "far": far, "near_down": 2.5,
         "rifle_z": "front", "body": (dx, dy), "head": head, "legs": legs or wide()}
    p.update(kw)
    return p


def kneel(deg=0.0, up=0.0, dy=6, **kw):
    kw.setdefault("legs", kneel_legs())
    return aim(deg=deg, up=up, dy=dy, **kw)


def carry(dy=0, dx=0, legs=None, head=(0, 0), **kw):
    p = {"carry": True, "body": (dx, dy), "head": head, "legs": legs or STAND}
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


POSES = {
    # main's attack, shown in display order (import_native's ORDER for the first design is gone): aimed at the chest,
    # lowering, the shot from the hip held two slots (3-4: the barrel 8 squares over the pivot, so the bullet flies to
    # the target's pivot nearly level - "平A出去的子弹看起来是歪的"), the recoil, back to the idle's hold
    "attack": [
        aim(deg=2),
        aim(deg=0, up=-3),
        aim(deg=0, up=-6),
        aim(deg=0, up=-6),
        aim(deg=5, up=-5),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's passive (the Headshot): aimed, down into a wide crouch (2-3), the shot from the hip held two slots (4-5),
    # back to the idle's hold
    "passive": [
        aim(deg=2),
        aim(deg=0, dy=4, legs=wide(-8.5, 7.5)),
        aim(deg=0, up=-1, dy=4, legs=wide(-8.5, 7.5)),
        aim(deg=0, up=-3, dy=3, legs=wide(-8.0, 7.0)),
        aim(deg=0, up=-3, dy=3, legs=wide(-8.0, 7.0)),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's Q: the rifle swung up behind the head, brought round across the body, then down on one knee aiming level
    # (3-6), the shot (7), up again
    "skill": [
        {"rifle": (6.0, -15.0, 150), "near": 8.0, "far": 13.0, "near_down": 1.5, "rifle_z": "behind",
         "legs": wide(-5.5, 4.5), "body": (0, 1)},
        {"rifle": (-6.5, -9.0, 28), "near": 8.0, "far": 14.0, "near_down": 2.0, "rifle_z": "front",
         "legs": wide(-6.5, 5.5), "body": (0, 1)},
        kneel(dy=5),
        kneel(),
        kneel(),
        kneel(up=0.5),
        kneel(dx=-1),                     # 7: the shot (the muzzle 7.5 squares up), the recoil a square back
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's W: the rifle stood at her side, she bends down and the far hand throws the trap forward (4), up again
    "skill2": [
        staff(far=(4.0, -9.0)),
        staff(dy=1, dx=1, head=(1, 0), legs=wide(-5.0, 4.0), far=(6.0, -8.0)),
        staff(dy=3, dx=1, head=(1, 1), legs=wide(-6.5, 5.5), far=(7.0, -6.0)),
        staff(dy=5, dx=2, head=(1, 1), legs=wide(-7.5, 6.5), far=(14.0, -1.0)),
        staff(dy=2, dx=1, head=(1, 0), legs=wide(-6.0, 5.0), far=(8.0, -5.0)),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's E: aimed, crouched, the net's shot (3), the hop back - airborne, legs tucked forward (4-5), landing in a
    # crouch (6-7), back to the idle's hold
    "e": [
        aim(deg=2),
        aim(deg=1, dy=3, legs=wide(-7.5, 6.5)),
        aim(deg=0, dy=3, legs=wide(-7.5, 6.5)),   # 3: the net's shot, the muzzle 11 squares up
        aim(deg=6, up=0.5, dx=-1, dy=-2, legs={"near": (2.0, 6), "far": (6.0, 5)}),
        aim(deg=3, dx=-1, dy=0, legs={"near": (1.0, 4), "far": (5.5, 3)}),
        aim(deg=0, dy=4, legs=wide(-8.0, 7.0)),
        aim(deg=1, dy=3, legs=wide(-7.5, 6.5)),
        carry(legs=wide(-5.5, 4.5)),
    ],
    # main's R: the rifle raised high, sinking down with it, on one knee aiming level (3-6), the shot (7), lower (8),
    # up again
    "ult": [
        {"rifle": (-3.0, -11.0, 58), "near": 7.5, "far": 13.0, "near_down": 2.0, "rifle_z": "front",
         "legs": wide(-5.0, 4.0), "body": (0, 0)},
        {"rifle": (-5.0, -7.0, 38), "near": 8.0, "far": 14.0, "near_down": 2.0, "rifle_z": "front",
         "legs": kneel_legs(nk=-1.0, na=-7.5, fa=6.5), "body": (0, 4)},
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
    hipk = (0.0, 4.0)                                   # the hips' middle when kneeling 6 down
    k6 = kneel_legs(fa=6.0)
    out = [
        aim(deg=12, up=1, dx=-1, head=(-1, 0)),
        staff(dy=6, legs=k6, head=(1, 1), far=(4.0, -2.0)),
        staff(dy=7, legs=kneel_legs(fa=6.0), head=(1, 2), far=(4.0, -1.0)),
        staff(dy=7, legs=kneel_legs(fa=6.0), head=(1, 2), far=(4.0, -1.0)),
    ]
    lying_legs = {"near": {"ankle": (-17.0, 9.5), "knee": (-10.0, 9.0)}, "far": {"ankle": (-16.0, 8.5), "knee": (-9.0, 8.0)}}
    # falling forward: the upper body turned about the hips, the hips going forward and down onto both knees
    out.append({"legs": kneel_legs(fa=5.0), "body": (1, 7), "head": (1, 1), "near": (3.0, -4.0), "far": (7.0, -3.0),
                "rot": (-30, (0.5, 5.0)), "ground": "lift", "loose_rifle": (-11.0, 9.0, 70)})
    out.append({"legs": {"near": {"ankle": (-6.0, 9.5), "knee": (1.0, 10.0)}, "far": {"ankle": (-3.0, 9.5), "knee": (4.0, 10.0)}},
                "body": (3, 9), "head": (1, 1), "near": (5.0, -2.0), "far": (9.0, -1.0),
                "rot": (-70, (2.5, 7.0)), "ground": "lift", "loose_rifle": (-13.0, 9.5, 35)})
    lie = {"legs": lying_legs, "body": (0, 7), "head": (0, 0), "near": (-1.0, -6.0), "far": (3.0, -6.0),
           "rot": (-90, (-2.0, 7.0)), "ground": True, "loose_rifle": (-14.0, 9.5, 0)}
    out.append(lie)
    out.append(dict(lie))
    return out


POSES["dead"] = death()
POSES["idle"] = [carry() for _ in range(6)]       # the design; import_native's BOB breathes it


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

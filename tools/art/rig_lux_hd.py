#!/usr/bin/env python3
"""league_lux redone at PPU 2.2 from Codex's picture (tools/art/design_lux_hd.py; the user, 2026-10-23: 「下一个英雄重做
拉克丝」, then 「动作帧你做到完美后喊我review吧」), every action posed here from the design's own squares
(rig_jinx_hd.py's way), after oppi's Lux (LoL Reborn champions/lux.aseprite: the staff swung from behind her to the
front for every cast) and League's clips.

    python tools/art/rig_lux_hd.py --parts DIR         # the parts tinted
    python tools/art/rig_lux_hd.py --review DIR        # every tag at 3x + GIFs
    python tools/art/rig_lux_hd.py                     # orig strips + the 1x sheet
    python tools/art/hero_reels.py --hero lux          # then: the idle / ban-pick reels from idle_base

Idle, run, hit and death: no square is redrawn - the parts are cut square by square and placed only by whole squares,
quarter turns and whole-row shifts, the run's and the death's thighs the design's own legging rows laid along the bone
(Legs); standing, the parts rebuild the design exactly (Poser.check). The four casts (attack, skill, skill2, ult) are
Codex's whole-frame redraw mended onto the design by tools/art/casts_lux_hd.py (the user on the first, rigged casts -
the staff only turned half round about her hand: 「手和法杖一点动作都没有的 不奇怪？」, then 「Codex 重画施法动作」).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_lux_hd as CL  # noqa: E402
import design_lux_hd as DL  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "lux"
PPU = DL.PPU
DESIGN_ROWS = 81
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
PAD = 40
PIVOT_COL = 34                  # between the soles (her left boot 19-27, her right 40-50)
O = DL.OUTLINE

# ------------------------------------------------------------------------------------------------ the parts
# the long hair falling behind her near arm: rows -> (first column, last column), the outline between it and the arm
# left to the arm
HAIR = {30: (11, 23), 31: (11, 22), 32: (13, 21), 33: (13, 21), 34: (13, 20), 35: (14, 20), 36: (14, 20),
        37: (14, 18), 38: (15, 20), 39: (14, 20), 40: (13, 18), 41: (13, 18), 42: (13, 17), 43: (14, 17),
        44: (14, 17)}
LEG_TOP = 58                    # the legs from this row down (the skirt's hem above)
LEG_SPLIT = 33                  # her left leg west of this column, her right one from it
PARTS = ["hair", "leg_l", "leg_r", "upper", "staff", "glove"]       # back to front
Z = {name: i for i, name in enumerate(PARTS)}


def lp(path):
    return R.lp(path)


def hexes(d):
    return np.array([["%02X%02X%02X" % tuple(d[y, x, :3]) for x in range(d.shape[1])] for y in range(d.shape[0])])


def masks(d):
    op = d[..., 3] > 0
    H, W = op.shape
    yy, xx = np.mgrid[0:H, 0:W]
    band, head, end = DL.staff_masks(d)
    glove = np.zeros_like(op)
    for x, y in DL.GLOVE:
        glove[y, x] = True
    staff = (band | head | end) & op & ~glove
    hair = np.zeros_like(op)
    for r, (x0, x1) in HAIR.items():
        hair[r, x0:x1 + 1] = True
    hair &= op & ~staff
    legs = op & (yy >= LEG_TOP) & ~staff
    out = {"staff": staff, "glove": glove & op, "hair": hair, "leg_l": legs & (xx < LEG_SPLIT),
           "leg_r": legs & (xx >= LEG_SPLIT)}
    taken = np.zeros_like(op)
    for m in out.values():
        taken |= m
    out["upper"] = op & ~taken
    return {name: out[name] for name in PARTS}


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

    def stamp(self, img, x0, y0):
        ys, xs = np.nonzero(img[..., 3] > 0)
        Y, X = ys + y0 + PAD, xs + x0 + PAD
        ok = (Y >= 0) & (Y < self.a.shape[0]) & (X >= 0) & (X < self.a.shape[1])
        self.a[Y[ok], X[ok]] = img[ys[ok], xs[ok]]


def transformed(img, x0, y0, t):
    """A part's picture (top-left x0, y0 in design squares) moved by its transform t: "shear" (whole rows shifted, k
    columns at the bottom row growing from 0 at row `pivot` - hair swinging), "rot" (quarter turns counter-clockwise
    about t["about"]), then (dx, dy). Returns (picture, x, y)."""
    out, x, y = img, x0, y0
    k = t.get("shear", 0)
    if k:
        h, w = out.shape[:2]
        p = t.get("pivot", 0)
        prof = t.get("profile")
        s = [0 if r <= p else int(round(k * (prof((r - p) / max(1, h - 1 - p)) if prof else (r - p) / max(1, h - 1 - p))))
             for r in range(h)]
        lo, hi = min(s), max(s)
        sh = np.zeros((h, w + hi - lo, 4), np.uint8)
        for r in range(h):
            sh[r, s[r] - lo:s[r] - lo + w] = out[r]
        out, x = sh, x + lo
    if t.get("rot"):
        ax, ay = t["about"]
        ys, xs = np.nonzero(out[..., 3] > 0)
        fx, fy = xs + x + 0.5, ys + y + 0.5
        for _ in range(t["rot"] % 4):
            fx, fy = ax + (fy - ay), ay - (fx - ax)
        tx, ty = np.floor(fx).astype(int), np.floor(fy).astype(int)
        nx, ny = tx.min(), ty.min()
        new = np.zeros((ty.max() - ny + 1, tx.max() - nx + 1, 4), np.uint8)
        new[ty - ny, tx - nx] = out[ys, xs]
        out, x, y = new, nx, ny
    return out, x + t.get("dx", 0), y + t.get("dy", 0)


# ------------------------------------------------------------------------------------------------ the legs
# The run's and the death's legs are the idle's own (league_jinx: 「走路时和待机时 左腿不一样了？」), on two bones each: the
# thigh is the design's legging rows (THIGH_ROWS) laid along hip -> knee, its top under the skirt; the shin the
# design's knee guard and shin rows (SHIN_ROWS) along knee -> ankle - a square near the bone takes the row at that
# length and its square at that side (each row less the outline square at each end; one outline ring round each
# bone), so the stance's splay (her V) does not ride into the stride; below the ankle the design's whole boot hangs as
# drawn, never turned standing (「脚变形」).
GROUND = 81.0                   # the soles' bottom edge
THIGH_ROWS = {"l": (58, 62), "r": (58, 63)}
SHIN_ROWS = {"l": (63, 72), "r": (64, 73)}
HIP = {"l": (28.5, 52.0), "r": (39.5, 51.8)}      # the hip joints, under the skirt: both legs 29.6 long with the boot
KNEE = {"l": (25.5, 63.0), "r": (41.5, 64.0)}
ANKLE = {"l": (23.5, 73.0), "r": (43.5, 74.0)}    # where the boot's top meets the shin


class Legs:
    def __init__(self, d, M):
        hx = hexes(d)
        out_hex = "%02X%02X%02X" % O
        self.slices, self.boot = {}, {}
        for key in ("l", "r"):
            m = M["leg_" + key]
            for seg, (r0, r1) in (("thigh", THIGH_ROWS[key]), ("shin", SHIN_ROWS[key])):
                rows = []
                for y in range(r0, r1 + 1):
                    xs = np.nonzero(m[y] & (hx[y] != out_hex))[0]
                    rows.append(d[y, xs.min():xs.max() + 1].copy())
                self.slices[(key, seg)] = rows
            yy = np.arange(d.shape[0])[:, None]
            self.boot[key] = piece(d, m & (yy >= int(ANKLE[key][1])))
        self.lt = {k: float(np.hypot(*np.subtract(KNEE[k], HIP[k]))) for k in KNEE}
        self.ls = {k: float(np.hypot(*np.subtract(ANKLE[k], KNEE[k]))) for k in KNEE}
        self.bh = {k: GROUND - ANKLE[k][1] for k in KNEE}

    def bone(self, rows, A, B):
        """{(x, y): rgba} the rows laid along A -> B (square edges)."""
        A, B = np.asarray(A, float), np.asarray(B, float)
        v = B - A
        L = max(1e-6, float(np.hypot(*v)))
        u = v / L
        n = np.array((u[1], -u[0]))                     # down -> +x: a row's left stays on the left
        cells = {}
        for y in range(int(math.floor(min(A[1], B[1]))) - 6, int(math.ceil(max(A[1], B[1]))) + 6):
            for x in range(int(math.floor(min(A[0], B[0]))) - 6, int(math.ceil(max(A[0], B[0]))) + 6):
                p = np.array((x + 0.5, y + 0.5)) - A
                t, s_ = float(p @ u), float(p @ n)
                if t < -0.5 or t > L + 0.5:
                    continue
                row = rows[int(round(min(1.0, max(0.0, t / L)) * (len(rows) - 1)))]
                xi = int(math.floor(len(row) / 2 + s_))
                if 0 <= xi < len(row) and row[xi][3]:
                    cells[(x, y)] = row[xi]
        return cells

    def items(self, key, hip, knee, ankle, turn=0):
        """Items (z, name, picture, x, y) of one leg: its thigh hip -> knee, its shin knee -> ankle (over the thigh)
        and its whole boot at the ankle (turned `turn` quarter turns counter-clockwise about it: lying)."""
        z = Z["leg_" + key]
        out = []
        for i, (seg, A, B) in enumerate((("thigh", hip, knee), ("shin", knee, ankle))):
            img, x0, y0 = cells_img(fold(self.bone(self.slices[(key, seg)], A, B)))
            out.append((z + 0.01 * i, seg + "_" + key, img, x0, y0))
        bimg, (bx, by) = self.boot[key]
        ax, ay = ANKLE[key]
        if turn:
            bimg, bx, by = transformed(bimg, bx, by, dict(rot=turn, about=(ax, ay)))
        out.append((z + 0.05, "boot_" + key, bimg, int(round(bx + ankle[0] - ax)), int(round(by + ankle[1] - ay))))
        return out


def fold(cells, outline=O):
    """A thigh's squares with the outline ring closed round them (the slices carry no edge squares of their own)."""
    out = dict(cells)
    for (x, y) in list(cells):
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ddx, y + ddy)
            if q not in cells:
                out.setdefault(q, np.array((*outline, 255), np.uint8))
    return out


def cells_img(cells):
    """{(x, y): rgba} -> (picture, x0, y0)."""
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    x0, y0 = min(xs), min(ys)
    img = np.zeros((max(ys) - y0 + 1, max(xs) - x0 + 1, 4), np.uint8)
    for (x, y), c in cells.items():
        img[y - y0, x - x0, :3] = np.asarray(c)[:3]
        img[y - y0, x - x0, 3] = 255
    return img, x0, y0


# ------------------------------------------------------------------------------------------------ composing
UNITS = {"upper": ["hair", "upper", "staff", "glove"]}
FLIP = dict(rot=2, about=DL.M)  # the staff's half turn: the same squares, the crescent head forward


def compose(d, pieces, pose, legs=None):
    """pose: {"dx", "dy": the whole figure; "upper": the upper body over the drawn legs (dx, dy); a part's name: its
    transform (dx, dy, shear, rot, about); "flip": the staff turned head forward; "legs": {"l" / "r": (hip, knee, ankle)}
    the run's legs (Legs.items); "prone": the death on her back (prone_items)}."""
    f = Frame(d)
    gdx, gdy = pose.get("dx", 0), pose.get("dy", 0)
    pose = dict(pose)
    if pose.get("flip"):
        pose["staff"] = dict(FLIP, **pose.get("staff", {}))
    items = []
    hide = set()
    lg = pose.get("legs")
    if lg:
        hide |= {"leg_l", "leg_r"}
        for key in ("l", "r"):
            items += legs.items(key, *lg[key])
    for name in PARTS:
        if name in hide:
            continue
        img, (x0, y0) = pieces[name]
        items.append((Z[name], name, img, x0, y0))
    if pose.get("prone"):
        items = prone_items(pieces, pose["prone"], legs, pose)
    for _, name, img, x0, y0 in sorted(items, key=lambda t: t[0]):
        out, x, y = transformed(img, x0, y0, dict(pose.get(name, {})))
        for unit, members in UNITS.items():
            if name in members and unit in pose:
                out, x, y = transformed(out, x, y, pose[unit])
        f.stamp(out, x + gdx, y + gdy)
    return f.a


# ------------------------------------------------------------------------------------------------ the death
# League's death and her old sheet's: knocked over backwards onto her back. Her upper body turns a quarter
# counter-clockwise about her hips (lossless: no square redrawn), the long hair first gathered in behind her back (its
# rows shifted toward it, HAIR_GATHER) so she is not propped on it, and lies on the ground; her right leg is drawn the
# run's way from the turned hip (the left one lies behind it) - thrown up as she lands, then lying along the ground -
# with the design's whole lower leg turned (DEAD_TURN). The staff leaves her hand (turned with her it stood up from her
# like a pole): it flies up behind her, then lies on the ground behind her as drawn (seen from above a staff lying
# across the ground slants like that) - her body under the shaft is under_shaft's.
PRONE_PIVOT = (34.0, 52.0)
HAIR_GATHER = 6                 # columns the hair's tips move toward her back before the turn
# the knee from the turned hip and the ankle from the knee (dx, dy in squares)
DEAD_LEGS = {"up": ((0, -12), (2, -10)), "flat": ((12, 0), (10, 1))}
DEAD_TURN = {"up": 2, "flat": 1}                  # the lower leg: upside down (soles to the sky), or lying toes-up
STAFF_DOWN = (-6, 7, False, False)                # the staff lying behind her: its crescent head on the ground


def prone_items(pieces, pr, legs, pose):
    """Items of the body on its back: pr = {"lift": rows off the ground, "dx": columns on, "legs": "up" | "flat",
    "staff": (dx, dy, turned head forward, in front) of the dropped staff from where she held it standing}."""
    group = []
    for name in ("hair", "upper", "glove"):
        img, (x0, y0) = pieces[name]
        t = dict(shear=HAIR_GATHER, pivot=3, profile=lambda t: t ** 1.2) if name == "hair" else {}
        img, x0, y0 = transformed(img, x0, y0, t)
        group.append((Z[name], name, img, x0, y0))
    px, py = PRONE_PIVOT
    turned = [(z, n) + transformed(img, x, y, dict(rot=1, about=(px, py))) for z, n, img, x, y in group]
    bottom = max(y + img.shape[0] for _, n, img, x, y in turned if n == "upper")
    sy = int(round(GROUND - bottom)) - pr.get("lift", 0)
    sx = pr.get("dx", 0)
    items = [(z, n, img, x + sx, y + sy) for z, n, img, x, y in turned]
    hx, hy = px + sx, py + sy                           # the turned hip
    mode = pr.get("legs", "flat")
    (kdx, kdy), (adx, ady) = DEAD_LEGS[mode]
    items += legs.items("r", (hx, hy), (hx + kdx, hy + kdy), (hx + kdx + adx, hy + kdy + ady), turn=DEAD_TURN[mode])
    sdx, sdy, flip, front = pr["staff"]
    img, (x0, y0) = pieces["staff"]
    img, x0, y0 = transformed(img, x0, y0, FLIP if flip else {})
    items.append((Z["glove"] + 1 if front else Z["hair"] - 1, "staff_dropped", img, x0 + sdx, y0 + sdy))
    return items


# ------------------------------------------------------------------------------------------------ poses
STAND = {}


def hair(k):
    """The long hair swinging: its tips k columns (right +) from where they hang, its top still (it lags a beat behind
    the body: back when she lunges forward, forward when she is knocked back)."""
    return {"hair": dict(shear=k, pivot=4, profile=lambda t: t ** 1.5)}


def P(dx=0, flip=False, **kw):
    """A pose: the whole figure moved dx columns (legs and all), the staff turned head forward (flip), the hair's swing
    and any part's transform in kw."""
    out = dict(kw)
    if dx:
        out["dx"] = dx
    if flip:
        out["flip"] = True
    return out


# The run (8 frames of 100 ms), the legs half a cycle apart through RUN_PHASE: (thigh, shin) degrees from straight down
# (+ = forward) and the rows the whole leg is lifted (its top sliding up under the skirt). The planted leg lands
# ahead, straightens and sweeps back under her (+25 to -14), pushes off; the free leg kicks its foot up behind, then
# swings its knee forward and reaches - so the feet cross every half cycle; the planted boot stands on the ground and
# its leg holds the hips (the body bobbing with the steps). The hips close together (RUN_HIP_X) as in a side-on run,
# the upper body RUN_LEAN columns ahead, the hair streaming back.
RUN_HIP_X = {"l": 33.0, "r": 35.0}
RUN_HIP_Y = 51.9                # the hips' row with a leg straight: the upper body as drawn
RUN_LEAN = 1
RUN_PHASE = [(25, 8, 0), (12, 0, 0), (0, -6, 0), (-14, -16, 0), (-24, -40, 1), (-8, -62, 4), (16, -28, 3), (28, 2, 1)]
HAIR_RUN = [-3, -4, -3, -2, -3, -4, -3, -2]


def run_poses():
    lt = {k: float(np.hypot(*np.subtract(KNEE[k], HIP[k]))) for k in KNEE}
    ls = {k: float(np.hypot(*np.subtract(ANKLE[k], KNEE[k]))) for k in KNEE}
    bh = {k: GROUND - ANKLE[k][1] for k in KNEE}
    out = []
    for i in range(len(RUN_PHASE)):
        spec = {"l": RUN_PHASE[i], "r": RUN_PHASE[(i + 4) % len(RUN_PHASE)]}
        rad = {k: (math.radians(v[0]), math.radians(v[1])) for k, v in spec.items()}
        plant = [k for k in spec if spec[k][2] == 0]
        hy = max(GROUND - bh[k] - lt[k] * math.cos(rad[k][0]) - ls[k] * math.cos(rad[k][1]) for k in plant)
        legs = {}
        for key in ("l", "r"):
            th, sh = rad[key]
            hip = np.array((RUN_HIP_X[key], hy - spec[key][2]))
            knee = hip + lt[key] * np.array((math.sin(th), math.cos(th)))
            ankle = knee + ls[key] * np.array((math.sin(sh), math.cos(sh)))
            legs[key] = (tuple(hip), tuple(knee), tuple(ankle))
        out.append(dict(upper=dict(dx=RUN_LEAN, dy=int(round(hy - RUN_HIP_Y))), legs=legs, **hair(HAIR_RUN[i])))
    return out


POSES = {
    # knocked back two columns, the hair flung forward; then halfway back
    "hit": [P(-2, **hair(3)), P(-1, **hair(1))],
    # struck: knocked back, she reels, topples over backwards (a leg thrown up as she lands), bounces and lies still
    "dead": [P(-2, **hair(3)), P(-4, **hair(4)),
             dict(prone=dict(lift=8, dx=-10, legs="up", staff=(-8, -18, True, True))),
             dict(prone=dict(lift=1, dx=-12, legs="up", staff=(-6, 0, False, False))),
             dict(prone=dict(lift=0, dx=-12, legs="flat", staff=STAFF_DOWN)),
             dict(prone=dict(lift=1, dx=-12, legs="flat", staff=STAFF_DOWN)),
             dict(prone=dict(lift=0, dx=-12, legs="flat", staff=STAFF_DOWN))],
}


# ------------------------------------------------------------------------------------------------ the rig
def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(HD, "picture.png")))


def design():
    d = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.px = PIVOT_COL
    D.d0 = D.d.copy()
    return D


def drop_stray_outline(can):
    """Outline squares with no coloured square within two (a swung part's corner) taken out, until none is left."""
    out = can.copy()
    while True:
        op = out[..., 3] > 0
        isout = op & (np.abs(out[..., :3].astype(int) - np.array(O)).sum(-1) < 30)
        near = ndimage.binary_dilation(op & ~isout, structure=np.ones((5, 5), bool))
        stray = isout & ~near
        if not stray.any():
            return out
        out[stray] = 0


class LuxRig(R.Rig):
    def finish(self, can):
        return drop_stray_outline(super().finish(can))


def on_rig(rig, a):
    """A composed frame (design squares + PAD) on the rig's canvas (the design's (0, 0) at ox, oy)."""
    can = rig.canvas()
    ys, xs = np.nonzero(a[..., 3] > 0)
    Y, X = ys - PAD + rig.oy, xs - PAD + rig.ox
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    can[Y[ok], X[ok]] = a[ys[ok], xs[ok]]
    can[rig.GY:] = 0
    return can


def under_shaft(d, M):
    """{(x, y): rgba} her body under the shaft where it crosses her (never drawn: the death drops the staff): each
    column's band squares take the body square just above them (the upper half) or just below (the lower half), where
    the body lies on both sides within UNDER_REACH rows - the belt, the skirt's top and the far forearm closed over."""
    band, _, _ = DL.staff_masks(d)
    body = (d[..., 3] > 0) & ~M["staff"]
    out = {}
    for x in range(d.shape[1]):
        ys = [y for y in range(d.shape[0]) if band[y, x] and not M["glove"][y, x]]
        if not ys:
            continue
        top, bot = min(ys), max(ys)
        up = next((y for y in range(top - 1, max(-1, top - 1 - UNDER_REACH), -1) if body[y, x]), None)
        dn = next((y for y in range(bot + 1, min(d.shape[0], bot + 1 + UNDER_REACH)) if body[y, x]), None)
        if up is None or dn is None:
            continue
        for y in ys:
            out[(x, y)] = d[up if y - up <= dn - y else dn, x].copy()
    return out


UNDER_REACH = 3


class Poser:
    def __init__(self, d):
        self.d = d
        self.M = masks(d)
        self.pieces = {n: piece(d, m) for n, m in self.M.items()}
        up = d.copy()
        up[~self.M["upper"]] = 0
        for (x, y), c in under_shaft(d, self.M).items():
            up[y, x] = c
        self.pieces["upper"] = piece(up, up[..., 3] > 0)
        st = d.copy()                                   # the staff whole: its shaft under her glove too (turned
        st[~self.M["staff"]] = 0                        # or dropped, those squares show)
        for (x, y), c in DL.shaft(d.shape).items():
            if (x, y) in DL.GLOVE:
                st[y, x, :3] = c
                st[y, x, 3] = 255
        self.pieces["staff"] = piece(st, st[..., 3] > 0)
        self.legs = Legs(d, self.M)

    def check(self):
        """Standing, the parts rebuild the design square for square; the parts cover it once."""
        d = self.d
        op = d[..., 3] > 0
        n = sum(m.astype(int) for m in self.M.values())
        if (n[op] != 1).any() or (n[~op] != 0).any():
            sys.exit(f"parts: {int((n[op] != 1).sum())} squares not in exactly one part")
        a = self.frame(STAND)
        got = a[PAD:PAD + d.shape[0], PAD:PAD + d.shape[1]]
        if (got != d).any() or int((a[..., 3] > 0).sum()) != int(op.sum()):
            sys.exit("the standing pose does not rebuild the design")

    def frame(self, pose):
        return compose(self.d, self.pieces, pose, self.legs)


def frames(rig):
    d = rig.D.d0
    ps = Poser(d)
    ps.check()
    sheet = R.sheet_of(HERO)
    casts, _ = CL.placed(rig)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        n = len(sheet[tag])
        if tag in CL.TAGS:
            fr = [casts[f"{tag}_{k + 1}"] for k in range(n)]
            out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
            continue
        if tag in POSES:
            poses = POSES[tag]
        elif tag == "run":
            poses = run_poses()
        else:
            poses = [STAND] * n
        if len(poses) != n:
            sys.exit(f"{tag}: {len(poses)} poses for {n} frames")
        fr = [on_rig(rig, ps.frame(p)) for p in poses]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
    out["idle"] = [(fr_, m) for fr_, m in out["idle_base"]]
    return {t: out[t] for t in sheet if t in out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    rig = LuxRig(D, pad=(110, 130, 110, 30))
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        ps = Poser(D.d0)
        ps.check()
        tint = {"hair": (0, 220, 255), "leg_l": (255, 0, 0), "leg_r": (140, 70, 20), "upper": (60, 200, 60),
                "staff": (170, 0, 255), "glove": (255, 230, 0)}
        d = D.d0
        img = np.zeros(d.shape[:2] + (3,), np.uint8) + 200
        for name, m in ps.M.items():
            img[m] = (d[m, :3] * 0.45 + np.array(tint[name]) * 0.55).astype(np.uint8)
        Image.fromarray(img).resize((d.shape[1] * 8, d.shape[0] * 8), Image.NEAREST).save(
            os.path.join(a.parts, "lux_parts.png"))
        return
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()

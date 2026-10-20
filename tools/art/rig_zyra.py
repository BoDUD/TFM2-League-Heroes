#!/usr/bin/env python3
"""league_zyra's action frames, posed on the approved 3/4 design after League's own clips frame by frame (the user,
2026-10-20: 「动作帧不是你自己做吗 其他英雄都是照着英雄联盟慢慢走出来的啊」「做出来」「动作帧要全啊别少 慢慢做好了 做完美了喊我
review」; on the side design: 「侧面太奇怪了 而且难做 就用四分之三面来做啊」).

    python tools/lol/league_joints.py assets/source/zyra/poses.json --out <dir>    # League's joints at the 3/4 camera
    python tools/art/rig_zyra.py --parts DIR                                       # the cut, tinted, at 11x
    python tools/art/rig_zyra.py --joints <dir>/zyra_joints.json --review DIR      # every tag at 3x + GIFs
    python tools/art/rig_zyra.py --joints <dir>/zyra_joints.json                   # orig strips + the 1x sheet
    python tools/art/review_zyra_actions.py --joints <dir>/zyra_joints.json --out DIR   # League left / ours right

The design (tools/art/design_zyra_model.py, Codex's A-1 at PPU 1.7: 75 x 74 squares, hair top to soles, Codex's own
face): League's idle seen 3/4 from the front-right - both arms held out to her sides with a whip-vine curling down from
each hand, legs apart. League's joints are exported at the same camera (poses.json: yaw 35 mirrored, as pose_ref
renders her): her right side (the throwing arm, the image-left one) is the near one.
  * her ARMS are the design's own squares (each from its shoulder piece to its claws), turned only losslessly about the
    shoulder (ARM_OPS: up, down, mirrored across her front) - every square kept;
  * the WHIPS are the design's own squares while their arm is as drawn; when the arm moves the whip is drawn along a
    curve from the hand's root (ACTS), two squares wide in the design's crimsons, the design's own spade pasted at its
    end turned by quarter turns;
  * the LEGS are the design's own in the standing actions; where League's legs kneel, run or fall they are drawn at
    the design's own lengths and widths in its leg colours with its pink thorns on the outer side and the design's own
    clawed feet pasted whole and flat - their angles the design's own plus League's change from its idle (the run:
    league_caitlyn's hand-placed phases);
  * the BODY (head, mane, torso, leaf skirt) is the design's own squares, moved whole and leaning on an even shear above
    the hips (the head one block, never cut).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "zyra"
PPU = 1.7
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
SPEC_HEIGHT = 44                             # assets/source/zyra/poses.json "height" (League game px)
S = 74 / SPEC_HEIGHT                         # design squares per League game px

# ------------------------------------------------------------------------------------------------- the 3/4 design
INK = (4, 1, 3)
PUR1, PUR2, PUR3 = (80, 39, 93), (53, 23, 63), (44, 22, 51)
VIOLET = (146, 42, 153)
THORN, THORN2 = (250, 44, 167), (249, 24, 137)
WHIP1, WHIP2 = (244, 4, 91), (193, 1, 67)
CRIMSONS = [(96, 1, 36), (151, 1, 51), (244, 4, 91), (75, 2, 31), (193, 1, 67)]

# the boxes (x0, y0, x1, y1, exclusive) the pieces are cut from, by colour inside them
NEAR_ARM_BOX = (13, 30, 32, 43)              # her right arm, held out to the image-left: shoulder piece to claws
FAR_ARM_BOX = (45, 32, 65, 48)               # her left arm, out to the image-right
NEAR_WHIP_BOX = (0, 37, 18, 54)
FAR_WHIP_BOX = (55, 45, 75, 63)
NEAR_SHOULDER = (31.0, 33.5)                 # square edges: what the arms turn about
FAR_SHOULDER = (46.0, 34.0)
NEAR_ROOT = (16.0, 41.0)                     # where each whip leaves its hand (square edges)
FAR_ROOT = (57.5, 47.0)
LEAN_TOP = 25                                # rows above this lean as one block (the head)
HIP_ROW = 50                                 # the shear's foot (the leaf skirt's hem)
# the legs as drawn (square edges): hip, knee, ankle; the near leg the image-left one
LEG_POINTS = {"near": ((33.5, 48.0), (29.5, 58.0), (26.5, 67.5)), "far": ((44.5, 48.5), (47.0, 59.0), (50.5, 68.5))}
LEG_ROW = 50                                 # drawn legs replace the design's legs from this row down
LEG_X = 39                                   # the near leg left of this column, the far one right
FOOT = {"near": ((21, 68, 32, 74), (26.5, 67.5)), "far": ((46, 68, 59, 74), (50.5, 68.5))}
LEG_PROFILE = {
    "near": {"thigh": [(0.0, 0.5, [PUR3, VIOLET, PUR1, PUR2, PUR3]), (0.5, 1.0, [PUR3, PUR1, PUR2, PUR3])],
             "shin": [(0.0, 0.5, [VIOLET, PUR1, PUR3]), (0.5, 1.0, [PUR1, PUR2])]},
    "far": {"thigh": [(0.0, 0.5, [PUR3, PUR2, PUR1, PUR2]), (0.5, 1.0, [PUR2, PUR2, PUR1])],
            "shin": [(0.0, 0.5, [PUR2, PUR2, PUR1]), (0.5, 1.0, [PUR2, PUR1])]},
}
# her leaf-blade thorns as drawn: (bone, place along it, length); side -1 the image-left, +1 the image-right edge
THORNS = {"near": (-1, [("thigh", 0.05, 3), ("thigh", 0.5, 4), ("shin", 0.05, 3), ("shin", 0.55, 3)]),
          "far": (1, [("thigh", 0.45, 4), ("shin", 0.1, 3), ("shin", 0.55, 2)])}
# the pink leaf strands running down inside each leg: (bone, from, to, squares across from the bone)
STRANDS = {"near": [("thigh", 0.35, 0.75, 0.6), ("shin", 0.2, 0.5, -0.4)],
           "far": [("thigh", 0.2, 0.55, 0.5), ("shin", 0.3, 0.6, 0.0)]}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(HD, name))).convert("RGBA")).copy()


def of(d, cols, tol=24):
    rgb = d[..., :3].astype(int)
    m = np.zeros(d.shape[:2], bool)
    for c in cols:
        m |= np.abs(rgb - np.array(c)).sum(-1) <= tol
    return m & (d[..., 3] > 0)


def box(d, b):
    m = np.zeros(d.shape[:2], bool)
    x0, y0, x1, y1 = b
    m[y0:y1, x0:x1] = True
    return m & (d[..., 3] > 0)


def leg_angles(pts):
    (h, k, a) = pts
    return (math.degrees(math.atan2(k[0] - h[0], k[1] - h[1])), math.degrees(math.atan2(a[0] - k[0], a[1] - k[1])))


HIPS = {k: v[0] for k, v in LEG_POINTS.items()}
THIGH = {k: math.hypot(v[1][0] - v[0][0], v[1][1] - v[0][1]) for k, v in LEG_POINTS.items()}
SHIN = {k: math.hypot(v[2][0] - v[1][0], v[2][1] - v[1][1]) for k, v in LEG_POINTS.items()}
LEG_REST = {k: leg_angles(v) for k, v in LEG_POINTS.items()}


class Design:
    """The 3/4 design cut into the body, the two arms, the two whips and the legs."""

    def __init__(self):
        d = load("idle.png")
        self.d0 = d
        self.H, self.W = d.shape[:2]
        self.hero, self.ppu = HERO, PPU
        self.outline = INK
        ys, xs = np.nonzero(d[..., 3] > 0)
        self.ground = ys.max() + 1
        low = d[ys.max() - 2:ys.max() + 1, :, 3].any(0)
        fx = np.nonzero(low)[0]
        self.px = int(round((fx.min() + fx.max() + 1) / 2))
        op = d[..., 3] > 0
        hair = of(d, CRIMSONS)
        spikes = [THORN, THORN2]
        nwhip = box(d, NEAR_WHIP_BOX) & of(d, CRIMSONS + spikes)
        fwhip = box(d, FAR_WHIP_BOX) & of(d, CRIMSONS + spikes)
        narm = box(d, NEAR_ARM_BOX) & ~hair & ~nwhip
        farm = box(d, FAR_ARM_BOX) & ~hair & ~fwhip
        legs = np.zeros(op.shape, bool)
        legs[LEG_ROW:] = True
        legs &= op
        rest = op & ~narm & ~farm & ~nwhip & ~fwhip
        # loose bits inside an arm's box that its cut left apart from the body (dark thorns) go with that arm
        lbl, n = ndimage.label(rest, structure=np.ones((3, 3)))
        main = 1 + int(np.argmax(ndimage.sum(rest, lbl, range(1, n + 1)))) if n else 0
        for k_ in range(1, n + 1):
            if k_ == main:
                continue
            m = lbl == k_
            if (m & box(d, NEAR_ARM_BOX)).sum() == m.sum():
                narm |= m
            elif (m & box(d, FAR_ARM_BOX)).sum() == m.sum():
                farm |= m
        # each piece's own outline: the near-black squares touching it and no coloured square of anything else
        ink = op & (np.abs(d[..., :3].astype(int) - np.array(INK)).sum(-1) <= 12)
        coloured = op & ~ink
        pieces = {"near_arm": narm, "far_arm": farm, "near_whip": nwhip, "far_whip": fwhip}
        for name in list(pieces):
            m = pieces[name] & coloured
            others = coloured & ~m
            for other in pieces.values():
                others &= ~(other & coloured) if other is not pieces[name] else others
            touch = ndimage.binary_dilation(m, structure=np.ones((3, 3)))
            near_other = ndimage.binary_dilation(others & ~m, structure=np.ones((3, 3)))
            pieces[name] = pieces[name] | (ink & touch & ~near_other)
        narm, farm, nwhip, fwhip = pieces["near_arm"], pieces["far_arm"], pieces["near_whip"], pieces["far_whip"]
        nwhip &= ~narm
        fwhip &= ~farm
        self.parts = {"near_arm": narm, "far_arm": farm, "near_whip": nwhip, "far_whip": fwhip}
        xx = np.arange(self.W)[None, :] * np.ones((self.H, 1), int)
        free = ~narm & ~farm & ~nwhip & ~fwhip
        self.parts["near_leg"] = legs & (xx < LEG_X) & free
        self.parts["far_leg"] = legs & (xx >= LEG_X) & free
        body = op.copy()
        for m in self.parts.values():
            body &= ~m
        self.layers = {k: np.where(m[..., None], d, 0).astype(np.uint8) for k, m in self.parts.items()}
        self.layers["body"] = np.where(body[..., None], d, 0).astype(np.uint8)
        self.feet = {k: self.piece(b, a) for k, (b, a) in FOOT.items()}
        self.spade = self.piece((0, 44, 6, 53), (2.5, 44.0))      # the near whip's spade (pointing down)

    def piece(self, b, anchor):
        x0, y0, x1, y1 = b
        sub = self.d0[y0:y1, x0:x1]
        ys, xs = np.nonzero(sub[..., 3] > 0)
        return np.stack([xs + x0 + 0.5 - anchor[0], ys + y0 + 0.5 - anchor[1]], 1), sub[ys, xs]


# ------------------------------------------------------------------------------------------------- lossless moves
def turn(off, k, flip=False):
    """Offsets mirrored (flip) then k quarter turns counter-clockwise on screen (y down)."""
    x, y = off[:, 0].copy(), off[:, 1].copy()
    if flip:
        x = -x
    for _ in range(k % 4):
        x, y = y, -x
    return np.stack([x, y], 1)


def quarter(v):
    """The quarter turns (counter-clockwise) taking straight down (0, 1) nearest to direction v."""
    a = math.degrees(math.atan2(v[0], v[1]))
    return int(round(a / 90.0)) % 4


# the arms' moves: name -> (flip, quarter turns counter-clockwise), per arm (the near one points left, the far right)
ARM_OPS = {"near": {"rest": (False, 0), "up": (False, 3), "down": (False, 1), "across": (True, 0)},
           "far": {"rest": (False, 0), "up": (False, 1), "down": (False, 3), "across": (True, 0)}}


def stamp(can, layer, at, op=(False, 0), about=(0.0, 0.0)):
    """A design-sized layer's squares onto the canvas: mirrored / turned about `about` (square edges), the design's
    (0, 0) at canvas `at`."""
    ys, xs = np.nonzero(layer[..., 3] > 0)
    if not len(ys):
        return can
    off = np.stack([xs + 0.5 - about[0], ys + 0.5 - about[1]], 1)
    o = turn(off, op[1], op[0])
    tx = np.floor(about[0] + o[:, 0] + at[0]).astype(int)
    ty = np.floor(about[1] + o[:, 1] + at[1]).astype(int)
    ok = (tx >= 0) & (tx < can.shape[1]) & (ty >= 0) & (ty < can.shape[0])
    can[ty[ok], tx[ok]] = layer[ys[ok], xs[ok]]
    return can


def moved(pt, op, about):
    o = turn(np.array([[pt[0] - about[0], pt[1] - about[1]]]), op[1], op[0])[0]
    return (about[0] + o[0], about[1] + o[1])


# ------------------------------------------------------------------------------------------------- drawing
class Layer:
    """Cells {(x, y): rgba} on the canvas, with an outline ring of their own."""

    def __init__(self):
        self.cells = {}
        self.fixed = {}

    def band(self, A, B, profile, t0=0.0, t1=1.0):
        n_ = len(profile)
        hw = n_ / 2.0 - 0.01
        vx, vy = B[0] - A[0], B[1] - A[1]
        n = math.hypot(vx, vy) or 1e-9
        lo, hi = t0 * n - (0.6 if t0 == 0 else 0.0), t1 * n + (0.6 if t1 == 1 else 0.0)
        for y in range(int(math.floor(min(A[1], B[1]))) - n_ - 1, int(math.ceil(max(A[1], B[1]))) + n_ + 1):
            for x in range(int(math.floor(min(A[0], B[0]))) - n_ - 1, int(math.ceil(max(A[0], B[0]))) + n_ + 1):
                px, py = x + 0.5, y + 0.5
                t = ((px - A[0]) * vx + (py - A[1]) * vy) / n
                if t < lo or t > hi:
                    continue
                sd = -((px - A[0]) * (vy / n) - (py - A[1]) * (vx / n))
                if abs(sd) <= hw:
                    i = int(math.floor(sd + n_ / 2.0))
                    self.cells[(x, y)] = tuple(profile[max(0, min(n_ - 1, i))]) + (255,)

    def bone(self, A, B, stretches):
        for t0, t1, prof in stretches:
            self.band(A, B, prof, t0, t1)

    def thorn(self, A, B, t, length, side, width, cols=(THORN, THORN2)):
        """One of the design's leaf-blade thorns: from the bone's edge at t on `side` (+1 the front / right of a bone
        pointing down) it runs `length` squares down the limb, leaning out to a point - two squares wide at its root."""
        vx, vy = B[0] - A[0], B[1] - A[1]
        n = math.hypot(vx, vy) or 1e-9
        ux, uy = vx / n, vy / n
        nx, ny = uy * side, -ux * side
        edge = width / 2.0
        for k in range(length):
            a_ = t * n + k * 0.95
            o_ = edge + 0.4 + 0.9 * k / max(1, length - 1)
            for w_ in ((0.0, -0.9) if k < length - 1 else (0.0,)):
                x, y = A[0] + ux * a_ + nx * (o_ + w_), A[1] + uy * a_ + ny * (o_ + w_)
                c = cols[0] if k < length - 1 else cols[-1]
                self.cells[(int(math.floor(x)), int(math.floor(y)))] = tuple(c) + (255,)

    def strand(self, A, B, t0, t1, off, col=THORN):
        """A pink leaf strand inside the limb: squares along the bone from t0 to t1, `off` squares across."""
        vx, vy = B[0] - A[0], B[1] - A[1]
        n = math.hypot(vx, vy) or 1e-9
        ux, uy = vx / n, vy / n
        nx, ny = uy, -ux
        for a_ in np.arange(t0 * n, t1 * n, 0.9):
            x, y = A[0] + ux * a_ + nx * off, A[1] + uy * a_ + ny * off
            self.cells[(int(math.floor(x)), int(math.floor(y)))] = tuple(col) + (255,)

    def paste(self, piece, at, k=0, flip=False, shade=None):
        off, cols = piece
        o = turn(off, k, flip)
        for (dx, dy), c in zip(o, cols):
            c = tuple(int(v) for v in c)
            if shade is not None and c[3] > 0 and sum(c[:3]) > 30:
                c = shade(c[:3]) + (255,)
            self.fixed[(int(math.floor(at[0] + dx)), int(math.floor(at[1] + dy)))] = c

    def curve(self, pts, widths=(WHIP1, WHIP2)):
        P = [np.array(p, float) for p in pts]
        P = [P[0]] + P + [P[-1]]
        samples = []
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            for t in np.linspace(0, 1, 12, endpoint=False):
                t2, t3 = t * t, t * t * t
                samples.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                                      (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
        samples.append(P[-2])
        for a, b in zip(samples, samples[1:]):
            self.band(tuple(a), tuple(b), widths)
        return samples

    def draw(self, can, outline=INK):
        line = tuple(outline) + (255,)
        H, W = can.shape[:2]
        ring = {}
        for (x, y) in self.cells:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in self.cells and q not in self.fixed:
                    ring[q] = line
        for cells in (ring, self.cells, self.fixed):
            for (x, y), c in cells.items():
                if 0 <= y < H and 0 <= x < W and c[3] > 0:
                    can[y, x] = c
        return can


def along(p, deg, length):
    r = math.radians(deg)
    return (p[0] + length * math.sin(r), p[1] + length * math.cos(r))


def knee(H, A, l1, l2, forward=1):
    vx, vy = A[0] - H[0], A[1] - H[1]
    d = math.hypot(vx, vy) or 1e-9
    d2 = max(abs(l1 - l2) + 0.3, min(l1 + l2 - 0.15, d))
    ux, uy = vx / d, vy / d
    A = (H[0] + ux * d2, H[1] + uy * d2)
    a = (l1 * l1 - l2 * l2 + d2 * d2) / (2 * d2)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    px, py = -uy, ux
    if px * forward < 0:
        px, py = -px, -py
    return (H[0] + ux * a + px * h, H[1] + uy * a + py * h), A


def darker(c, k=0.78):
    return tuple(int(v * k) for v in c[:3])


# ------------------------------------------------------------------------------------------------- the pose
class Pose:
    """One frame: arms {side: op name}, whips {side: "rest" | points from the root | "ground" | None}, legs None (the
    design's own) or {side: (thigh, shin) degrees} / ankles {side: (dx, dy) from the hip}, dx, dy (the whole figure),
    lean (columns at the head), lift (rows off the ground), flash."""

    def __init__(self, arms=None, whips=None, legs=None, ankles=None, dx=0, dy=0, lean=0, lift=0, flash=False,
                 far_leg_shade=False):
        self.arms = {"near": "rest", "far": "rest", **(arms or {})}
        self.whips = {"near": "rest", "far": "rest", **(whips or {})}
        self.legs, self.ankles = legs, ankles
        self.dx, self.dy, self.lean, self.lift, self.flash = dx, dy, lean, lift, flash
        self.far_leg_shade = far_leg_shade


def leg_geo(p):
    geo = {}
    for side in ("near", "far"):
        H = HIPS[side]
        if p.ankles is not None:
            ax, ay = p.ankles[side]
            K, A = knee(H, (H[0] + ax, H[1] + ay), THIGH[side], SHIN[side])
        else:
            th, sh = p.legs[side]
            K = along(H, th, THIGH[side])
            A = along(K, sh, SHIN[side])
        geo[side] = (H, K, A)
    return geo


def compose(rig, D, p):
    ox, oy = rig.ox, rig.oy
    drawn = p.legs is not None or p.ankles is not None
    geo = leg_geo(p) if drawn else None
    if drawn:
        low = []
        for side, (H, K, A) in geo.items():
            off, _ = D.feet[side]
            low.append(A[1] + off[:, 1].max())
            low.append(K[1] + 1.5)
        base_dy = int(round(D.ground - max(low)))
    else:
        base_dy = 0
    dy = base_dy - p.lift + p.dy
    dx = int(round(p.dx))
    at = (ox + dx, oy + dy)
    can = rig.canvas()

    def lean_at(y):
        if not p.lean:
            return 0
        if y <= LEAN_TOP:
            return p.lean
        if y >= HIP_ROW:
            return 0
        return int(round(p.lean * (HIP_ROW - y) / (HIP_ROW - LEAN_TOP)))

    def leaning(layer):
        """A design-sized layer sheared above the hips (whole rows moved, the head one block)."""
        if not p.lean:
            return layer
        out = np.zeros_like(layer)
        for y in range(layer.shape[0]):
            s = lean_at(y)
            if s > 0:
                out[y, s:] = layer[y, :-s]
            elif s < 0:
                out[y, :s] = layer[y, -s:]
            else:
                out[y] = layer[y]
        return out

    def place(side):
        """(op, the shoulder in design squares after the lean, the arm's canvas origin)."""
        sh0 = NEAR_SHOULDER if side == "near" else FAR_SHOULDER
        op = ARM_OPS[side][p.arms[side]]
        shift = lean_at(sh0[1])
        return op, sh0, (at[0] + shift, at[1])

    def whip_layer(side):
        w = p.whips[side]
        if w is None or w == "rest":
            return None
        op, sh0, origin = place(side)
        root0 = NEAR_ROOT if side == "near" else FAR_ROOT
        root = moved(root0, op, sh0)
        start = (origin[0] + root[0], origin[1] + root[1])
        if w == "ground":
            # down into the ground ahead (League's E: the vine dives in front of her)
            gy = rig.GY - 1.5
            fall = gy - start[1]
            pts = [start, (start[0] + 3, start[1] + fall * 0.5), (start[0] + 8, start[1] + fall * 0.9),
                   (start[0] + 13, gy), (start[0] + 18, gy)]
        else:
            pts = [start] + [(start[0] + x, start[1] + y) for x, y in w]
        lay = Layer()
        smp = lay.curve(pts)
        end, before = smp[-1], smp[-5]
        lay.paste(D.spade, tuple(end), quarter((end[0] - before[0], end[1] - before[1])))
        return lay

    def arm(side):
        op, sh0, origin = place(side)
        stamp(can, D.layers[f"{side}_arm"], origin, op, sh0)
        if p.whips[side] == "rest" and op == (False, 0):
            stamp(can, D.layers[f"{side}_whip"], origin)

    def leg(side):
        if not drawn:
            stamp(can, D.layers[f"{side}_leg"], at)
            return
        H, K, A = ((at[0] + v[0], at[1] + v[1]) for v in geo[side])
        lay = Layer()
        sh_ = (lambda c: darker(c)) if (side == "far" and p.far_leg_shade) else None
        prof = {k: [(a, b, [sh_(c) if sh_ else c for c in pr]) for a, b, pr in v] for k, v in LEG_PROFILE[side].items()}
        lay.bone(H, K, prof["thigh"])
        lay.bone(K, A, prof["shin"])
        tside, thorns = THORNS[side]
        for bone_, t, length in thorns:
            a, b = (H, K) if bone_ == "thigh" else (K, A)
            w = (len(prof[bone_][0][2]) + len(prof[bone_][-1][2])) / 2.0
            lay.thorn(a, b, t, length, tside, w, (THORN, THORN2) if sh_ is None else (sh_(THORN), sh_(THORN2)))
        for bone_, t0, t1, off in STRANDS[side]:
            a, b = (H, K) if bone_ == "thigh" else (K, A)
            lay.strand(a, b, t0, t1, off, THORN if sh_ is None else sh_(THORN))
        lay.paste(D.feet[side], A, shade=sh_)
        lay.draw(can)

    # back to front: the far arm and its whip, the far leg, the body, the near leg, the near whip, the near arm
    far_whip = whip_layer("far")
    arm("far")
    if far_whip is not None:
        far_whip.draw(can)
    leg("far")
    body = leaning(D.layers["body"])
    if drawn:
        body = body.copy()
        body[LEG_ROW:] = 0                     # the drawn legs replace the design's below the skirt
    stamp(can, body, at)
    leg("near")
    near_whip = whip_layer("near")
    if near_whip is not None:
        near_whip.draw(can)
    arm("near")
    can[rig.GY:] = 0
    return R.flash(can) if p.flash else can


# ------------------------------------------------------------------------------------------------- League's frames
def ang(a, b):
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))


def league_legs(j, d0):
    """The design's own leg angles plus League's change from its idle (League's right leg is the near one here)."""
    out = {}
    for side, sd in (("near", "r"), ("far", "l")):
        th = ang(j[f"{sd}_hip"], j[f"{sd}_knee"]) - ang(d0[f"{sd}_hip"], d0[f"{sd}_knee"])
        sh = ang(j[f"{sd}_knee"], j[f"{sd}_foot"]) - ang(d0[f"{sd}_knee"], d0[f"{sd}_foot"])
        out[side] = (LEG_REST[side][0] + th, LEG_REST[side][1] + sh)
    return out


def league_body(j, d0, lunge=0.5):
    dx = (j["pelvis"][0] - d0["pelvis"][0]) * S * lunge
    lean = ((j["chest"][0] - j["pelvis"][0]) - (d0["chest"][0] - d0["pelvis"][0])) * S * 0.6
    return dx, int(round(max(-2, min(3, lean))))


# whip shapes (points from the hand's root, design squares; x right, y down) after League's renders
LASH_R = [(5.0, -0.5), (10.0, -1.0), (15.0, -0.5), (20.0, 0.5)]
LASH_L = [(-5.0, -0.5), (-10.0, -1.0), (-15.0, -0.5), (-20.0, 0.5)]
DROOP_R = [(4.0, 1.5), (8.0, 3.5), (11.0, 6.5), (13.0, 10.0)]
HANG_L = [(-1.0, 4.0), (-2.5, 8.0), (-2.0, 12.0)]
HANG_R = [(1.0, 4.0), (2.5, 8.0), (2.0, 12.0)]
TRAIL_UP = [(-3.0, 3.0), (-7.0, 5.0), (-11.0, 5.0), (-14.0, 3.0)]
RISE_L = [(-2.0, -3.0), (-4.0, -8.0), (-3.0, -13.0), (0.0, -16.0)]
RISE_R = [(2.0, -3.0), (4.0, -8.0), (3.0, -13.0), (0.0, -16.0)]
RISE_L2 = [(-2.0, -3.0), (-3.0, -8.0), (-1.0, -13.0), (2.5, -15.5)]
RISE_R2 = [(2.0, -3.0), (3.0, -8.0), (1.0, -13.0), (-2.5, -15.5)]
BACK_LIFT = [(-4.0, -1.5), (-8.0, -4.0), (-12.0, -5.0), (-16.0, -3.5)]
RUN_FAR_WHIP = [[(1.0, 4.0), (-1.0, 8.5), (-4.0, 12.0)], [(1.0, 4.0), (-1.5, 8.5), (-3.5, 12.5)]]
RUN_TRAIL = [[(-4.0, 2.0), (-8.0, 4.5), (-12.0, 4.0), (-16.0, 6.0)], [(-4.0, 2.0), (-8.0, 3.5), (-12.0, 5.5), (-16.0, 4.5)]]
# per tag, per frame: arms, whips, drawn legs (League's), lean / dx, flash, lie - after League's renders
ACTS = {
    # League's Attack1: her right hand (the near one) swung up over her head, then flung across in front of her toward
    # the target - the seed leaves it; the whip lashes after it
    "attack": [dict(),
               dict(whips={"near": BACK_LIFT}),
               dict(arms={"near": "across", "far": "across"}, whips={"near": LASH_R, "far": HANG_L}),
               dict(arms={"near": "across", "far": "across"}, whips={"near": DROOP_R, "far": HANG_L}),
               dict()],
    # League's Spell2 (Q): both hands drawn in and down, then flung out wide (the spines burst)
    "skill": [dict(),
              dict(arms={"near": "down", "far": "down"}, whips={"near": HANG_L, "far": HANG_R}),
              dict(whips={"near": LASH_L, "far": LASH_R}),
              dict(whips={"near": LASH_L, "far": LASH_R}),
              dict(),
              dict()],
    # League's Spell3 (E): her right hand raised, then slammed down as she drops to one knee, the vine diving into the
    # ground ahead
    "skill2": [dict(),
               dict(arms={"near": "up"}, whips={"near": TRAIL_UP}),
               dict(arms={"near": "down", "far": "up"}, whips={"near": "ground", "far": HANG_R}, drawn=True),
               dict(arms={"near": "down", "far": "up"}, whips={"near": "ground", "far": HANG_R}, drawn=True),
               dict(arms={"near": "down"}, whips={"near": "ground"}, drawn=True),
               dict()],
    # League's Spell4 (R): a crouch with the hands low, then up on her toes, the arms out to her sides with the palms
    # up and the head thrown back - the vines rising from her hands (raised straight up her arms vanished in the mane)
    "ult": [dict(),
            dict(arms={"near": "down", "far": "down"}, whips={"near": HANG_L, "far": HANG_R}, drawn=True),
            dict(whips={"near": RISE_L, "far": RISE_R}, lean=-1, lift=1),
            dict(whips={"near": RISE_L2, "far": RISE_R2}, lean=-1, lift=1),
            dict(whips={"near": RISE_L, "far": RISE_R}, lean=-1, lift=1),
            dict()],
    "hit": [dict(dx=-2, flash=True), dict(dx=-1)],
    "dead": [dict(dx=-1),
             dict(arms={"near": "up", "far": "up"}, whips={"near": HANG_L, "far": HANG_R}, lean=-1),
             dict(arms={"near": "down", "far": "down"}, whips={"near": HANG_L, "far": HANG_R}, drawn=True),
             dict(arms={"near": "down", "far": "down"}, whips={"near": HANG_L, "far": HANG_R}, drawn=True)]
    + [dict(lie=True)] * 4,
}
# the run (league_caitlyn's way): one leg's ankle in eight phases from its hip (squares forward, down), the far leg
# four phases on
RUN_PHASES = [(8.0, 18.0), (4.0, 18.5), (-1.0, 19.0), (-5.0, 18.3), (-8.0, 15.5), (-6.0, 12.5), (1.0, 13.0),
              (6.0, 15.5)]
RUN_LIFT = [0, 0, 0, 2, 0, 0, 0, 2]
RUN_LEAN = 3
DEAD_SINK = 6


def idle_frames(rig, D, n):
    """The design breathing: everything but the legs (the body, both arms and their whips) sets down a row onto them."""
    sinks = [0, 0, 1, 1, 1, 1, 0, 0]
    d = D.d0
    legs = D.parts["near_leg"] | D.parts["far_leg"]
    still = np.where(legs[..., None], d, 0).astype(np.uint8)
    moving = np.where(legs[..., None], 0, d).astype(np.uint8)
    out = []
    for i in range(n):
        can = rig.canvas()
        stamp(can, still, (rig.ox, rig.oy))
        stamp(can, moving, (rig.ox, rig.oy + sinks[i % 8]))
        out.append(can)
    return out


def make_rig(D):
    return R.Rig(D, pad=(60, 60, 50, 30))


def tag_poses(tag, rows, d0):
    out = []
    for i, r in enumerate(rows):
        j = r["j"]
        dx, lean = league_body(j, d0)
        if tag == "run":
            ph = i % 8
            tr = RUN_TRAIL[i % 2]
            # her arms held out as drawn (hanging by her sides they lay over her torso), the near whip trailing behind
            p = Pose(whips={"near": tr, "far": RUN_FAR_WHIP[i % 2]},
                     ankles={"near": RUN_PHASES[ph], "far": RUN_PHASES[(ph + 4) % 8]}, lean=RUN_LEAN,
                     lift=RUN_LIFT[ph], far_leg_shade=True)
            p.lie = False
            out.append(p)
            continue
        a = ACTS[tag][i]
        legs = league_legs(j, d0) if a.get("drawn") else None
        p = Pose(arms=a.get("arms"), whips=a.get("whips"), legs=legs, dx=a.get("dx", dx), lean=a.get("lean", lean),
                 lift=a.get("lift", 0), flash=a.get("flash", False))
        p.lie = a.get("lie", False)
        out.append(p)
    return out


def frames(rig, joints):
    D = rig.D
    d0 = joints["design"]
    out = {}
    for tag, rows in joints["tags"].items():
        ms = [r["ms"] for r in rows]
        if tag == "idle":
            out[tag] = list(zip(idle_frames(rig, D, len(ms)), ms))
            continue
        poses = tag_poses(tag, rows, d0)
        fr = [compose(rig, D, p) for p in poses if not p.lie]
        if tag == "dead":
            # lying, head to the image-left (League's fall), the arms along her body: the figure with its arms down a
            # quarter turn counter-clockwise, its far side DEAD_SINK rows under the ground (lying flat, not a heap)
            flat = compose(rig, D, Pose(arms={"near": "down", "far": "down"}, whips={"near": None, "far": None},
                                        legs={"near": (14.0, 10.0), "far": (-14.0, -10.0)}))   # the legs together
            lie = R.lie(rig, flat, k=1, dx=-4, sink=DEAD_SINK)
            bounce = R.lie(rig, flat, k=1, dx=-4, sink=DEAD_SINK - 2)
            fr = fr[:4] + [bounce, lie, lie.copy(), lie.copy()]
        out[tag] = list(zip(fr, ms))
    return out


TINT = {"near_arm": (0, 128, 255), "far_arm": (255, 255, 0), "near_whip": (0, 255, 128), "far_whip": (0, 200, 200),
        "near_leg": (255, 0, 255), "far_leg": (255, 128, 0)}


def parts_png(D, path, z=11):
    img = D.d0.astype(float).copy()
    for n, c in TINT.items():
        m = D.parts[n]
        img[m, :3] = img[m, :3] * 0.45 + np.array(c) * 0.55
    big = Image.fromarray(np.repeat(np.repeat(img.astype(np.uint8), z, 0), z, 1))
    bg = Image.new("RGBA", big.size, (210, 210, 210, 255))
    bg.alpha_composite(big)
    body = Image.fromarray(np.repeat(np.repeat(D.layers["body"], z, 0), z, 1))
    bg2 = Image.new("RGBA", body.size, (210, 210, 210, 255))
    bg2.alpha_composite(body)
    can = Image.new("RGB", (bg.width * 2 + 20, bg.height), (255, 255, 255))
    can.paste(bg.convert("RGB"), (0, 0))
    can.paste(bg2.convert("RGB"), (bg.width + 20, 0))
    can.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = Design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        parts_png(D, os.path.join(a.parts, f"{HERO}_parts.png"))
        rig = make_rig(D)
        rest = rig.finish(compose(rig, D, Pose()))
        ref = rig.canvas()
        stamp(ref, D.d0, (rig.ox, rig.oy))
        print({k: int(v.sum()) for k, v in D.parts.items()}, "rest frame differs in",
              int((rest != rig.finish(ref)).any(-1).sum()), "squares")
        return
    if not a.joints:
        sys.exit("--joints is needed")
    with open(a.joints, encoding="utf-8") as f:
        joints = json.load(f)
    rig = make_rig(D)
    acts = frames(rig, joints)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()

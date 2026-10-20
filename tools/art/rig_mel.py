#!/usr/bin/env python3
"""league_mel's action frames, posed on the approved 3/4 design after League's own clips frame by frame (the user,
2026-10-20: actions 「我自己照英雄联盟摆」, 3/4 only; 「直接做动作帧吧」).

    python tools/lol/league_joints.py assets/source/mel/poses.json --out <dir>    # League's joints at the 3/4 camera
    python tools/art/rig_mel.py --parts DIR                                       # the cut, tinted, at 11x
    python tools/art/rig_mel.py --joints <dir>/mel_joints.json --review DIR      # every tag at 3x + GIFs
    python tools/art/rig_mel.py --joints <dir>/mel_joints.json                   # orig strips + the 1x sheet

The design (tools/art/design_mel_model.py, Codex's A-3 at PPU 1.5: 58 x 65 squares, bun top to soles, Codex's own
face): League's idle seen 3/4 from the front-right - her near hand on her hip, her far arm reaching forward palm up,
both wide crimson bell sleeves hanging, the robe open in front over two thin teal legs and lying behind her as a train.
League's joints are exported at the same camera (poses.json: yaw 35 mirrored): her right side (the hand on the hip,
the image-left one) is the near one.
  * the HANDS are the design's own squares: the far hand with its gold cuff turned only losslessly about its elbow
    (up, down: quarter turns); the near hand on the hip as drawn, or the far hand mirrored and turned onto the near
    side when that arm goes up or down;
  * the SLEEVES are the design's own squares, never turned: they hang from the wrists, so a sleeve goes up and out
    with its hand thrown up (moved by whole squares);
  * the ROBE (the two front panels, the train and the flare on the ground) is the design's own squares; it follows the
    hips by losing whole rows from its middle (a crouch: the waist comes down, the hem stays on the ground), its lowest
    rows fly back by whole columns and the train's tip lifts (run, casts);
  * the LEGS are the design's own when she stands; where League's legs lunge, kneel, run or fall they are drawn at the
    design's own widths in its teal shades with the silver knee plate, the design's own silver heels pasted whole -
    their angles the design's own plus League's change from its idle (the run: hand-placed phases, Caitlyn's way);
  * the UPPER body (bun, face, collar, shoulders, bodysuit) is the design's own squares, moved whole and leaning on an
    even shear above the hips (the head one block, never cut).
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
import rig_zyra as Z  # noqa: E402  (the lossless stamps, quarter turns and drawn bands)

HERO = "mel"
PPU = 1.5
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
SPEC_HEIGHT = 43                             # assets/source/mel/poses.json "height" (League game px)

# ------------------------------------------------------------------------------------------------- the 3/4 design
INK = (5, 0, 12)
TEAL1, TEAL2, TEAL3 = (18, 104, 115), (12, 73, 86), (9, 59, 71)          # the bodysuit's teals, light to dark
SILVER2, SILVER3 = (147, 156, 170), (103, 112, 125)
# the robe's colours (the reds, its gold trim and lining, the navy hem): inside LEGS these are the robe behind the legs
ROBE_REDS = [(111, 0, 31), (166, 1, 44), (227, 8, 55), (70, 2, 25), (133, 1, 37), (196, 113, 38), (252, 184, 71),
             (251, 171, 60), (209, 120, 30), (232, 136, 26), (22, 33, 71)]
GROUND = 64                                  # the soles' bottom edge (row 63 is the heels' outline)
STAND = 40                                   # the pivot: between her two heels (columns 35-43)

# the parts' polygons (x, y in square edges), each cut by its squares' centres
FAR_HAND = [(48.5, 29.0), (58.0, 29.0), (58.0, 35.0), (48.5, 35.0)]
FAR_SLEEVE = [(42.0, 30.5), (48.5, 30.5), (48.5, 33.5), (53.0, 33.5), (53.0, 49.0), (50.5, 53.5), (46.5, 53.5),
              (45.5, 51.0), (47.0, 47.0), (44.5, 40.0), (42.5, 34.5)]
NEAR_SLEEVE = [(22.5, 29.5), (30.5, 29.5), (30.5, 34.5), (28.5, 34.5), (28.5, 37.5), (30.5, 41.0), (29.5, 47.0),
               (29.5, 52.5), (24.0, 52.5), (22.5, 47.0)]
NEAR_HAND = [(28.0, 33.5), (34.0, 33.5), (34.0, 37.5), (28.0, 37.5)]
LEGS = [(33.5, 44.5), (41.5, 44.5), (41.5, 58.5), (44.5, 58.5), (44.5, 64.0), (33.5, 64.0)]
ROBE_TOP = 37                                # the robe's rows: from here down, outside the legs and the sleeves
ELBOW = (48.5, 32.0)                         # the far hand turns about this point (its cuff's inner end, square edges)
NEAR_SHOULDER = (27.5, 30.0)                 # where a near hand thrown up puts its cuff
NEAR_UP_X = 25.0                             # a near hand thrown up: its cuff over the sleeve's outer side (clear of
                                             # the bun: over the hair the hand's skin reads as hair)
NEAR_BACK = (24.5, 32.0)                     # where a near hand reaching back puts its cuff (the sleeve's top corner)
# the legs as drawn (square edges): hip, knee, ankle; the near leg the image-left one; the heels pasted whole (box,
# anchor = the ankle)
LEG_POINTS = {"near": ((35.5, 45.5), (35.6, 53.0), (36.5, 59.0)), "far": ((39.5, 46.5), (39.8, 53.5), (40.5, 59.0))}
FOOT = {"near": ((34, 59, 39, 64), (36.5, 59.0)), "far": ((38, 59, 45, 64), (40.5, 59.0))}
LEG_PROFILE = {
    "near": {"thigh": [(0.0, 1.0, [TEAL2, TEAL1, TEAL1])],
             "shin": [(0.0, 0.45, [SILVER2, TEAL2]), (0.45, 1.0, [TEAL1])]},
    "far": {"thigh": [(0.0, 1.0, [TEAL3, TEAL2, TEAL2])],
            "shin": [(0.0, 0.45, [SILVER3, TEAL3]), (0.45, 1.0, [TEAL2])]},
}
BREATH_ROW = 38                              # the idle's breathing: the rows above the waist settle onto it
HIP_ROW = 45                                 # the lean's foot: rows above it lean (the head the most)
LEAN_TOP = 27
# a sleeve thrown up with its hand: (columns, rows) it moves - up and out to its own side; "top" the peak of a throw
# (League's Q and R hold the sleeves high over her head)
SLEEVE_HIGH = {"high": {"near": (-3, -8), "far": (1, -8)}, "top": {"near": (-4, -14), "far": (0, -15)}}
# (never further out: a raised sleeve keeps overlapping its shoulder - the arm inside it - or it floats free)
ANKLE_Y = 59.0                               # an ankle on the ground (its heel's soles on GROUND)
K_LEG = 18.5 / 27.6                          # rows a League game px of pelvis height (her hips 18.5 rows over the
                                             # ground, League's chibi pelvis 27.6 px)


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(HD, name))).convert("RGBA")).copy()


def poly_mask(shape, pts):
    """Squares whose centres lie inside the polygon (square edges)."""
    H, W = shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    px, py = xx + 0.5, yy + 0.5
    inside = np.zeros((H, W), bool)
    n = len(pts)
    for i in range(n):                                   # even-odd ray casting
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if y0 == y1:
            continue
        cross = ((y0 > py) != (y1 > py)) & (px < x0 + (py - y0) * (x1 - x0) / (y1 - y0))
        inside ^= cross
    return inside


def of(d, cols, tol=24):
    rgb = d[..., :3].astype(int)
    m = np.zeros(d.shape[:2], bool)
    for c in cols:
        m |= np.abs(rgb - np.array(c)).sum(-1) <= tol
    return m & (d[..., 3] > 0)


class Design:
    """The 3/4 design cut into the upper body, the far hand, the two sleeves, the near hand, the robe and the legs."""

    def __init__(self):
        d = load("idle.png")
        self.d0 = d
        self.H, self.W = d.shape[:2]
        self.hero, self.ppu = HERO, PPU
        self.outline = INK
        self.ground = GROUND
        self.px = STAND
        op = d[..., 3] > 0
        parts = {}
        parts["far_hand"] = poly_mask(d.shape, FAR_HAND) & op
        parts["far_sleeve"] = poly_mask(d.shape, FAR_SLEEVE) & op & ~parts["far_hand"]
        parts["near_sleeve"] = poly_mask(d.shape, NEAR_SLEEVE) & op
        parts["near_hand"] = poly_mask(d.shape, NEAR_HAND) & op & ~parts["near_sleeve"]
        # the legs: the teal / silver squares and the outline inside LEGS; the robe's reds between them stay the robe's
        parts["legs"] = poly_mask(d.shape, LEGS) & op & ~of(d, ROBE_REDS, tol=30)
        yy = np.arange(self.H)[:, None] + np.zeros((1, self.W), int)
        taken = np.zeros(op.shape, bool)
        for m in parts.values():
            taken |= m
        suit = np.zeros(op.shape, bool)
        suit[ROBE_TOP:45, 33:41] = True                  # the bodysuit and its plates above the legs: the body's
        robe = op & (yy >= ROBE_TOP) & ~taken & ~suit
        xx = np.arange(self.W)[None, :] + np.zeros((self.H, 1), int)
        # the robe's reds between the two legs (only with the design's own legs), the train and the flare on the ground
        # (they stay there), and the two front panels hanging from the waist (they follow the hips)
        parts["slit"] = robe & poly_mask(d.shape, LEGS)
        hem = robe & ~parts["slit"] & ((yy >= 58) | ((xx <= 28) & (yy >= 52)) | ((xx >= 46) & (yy >= 55)))
        parts["flare"] = hem & (xx >= 44)                # the far side's hem flaring out on the ground (only streams back)
        parts["train"] = hem & ~parts["flare"]
        parts["panels"] = robe & ~parts["slit"] & ~hem
        taken |= robe
        parts["upper"] = op & ~taken
        self.parts = parts
        self.layers = {k: np.where(m[..., None], d, 0).astype(np.uint8) for k, m in parts.items()}
        self.feet = {k: self.piece(b, a) for k, (b, a) in FOOT.items()}

    def piece(self, b, anchor):
        """The legs' squares in box b (x0, y0, x1, y1) as offsets from anchor + colours (a heel)."""
        x0, y0, x1, y1 = b
        sub = np.where(self.parts["legs"][y0:y1, x0:x1, None], self.d0[y0:y1, x0:x1], 0)
        ys, xs = np.nonzero(sub[..., 3] > 0)
        return np.stack([xs + x0 + 0.5 - anchor[0], ys + y0 + 0.5 - anchor[1]], 1), sub[ys, xs]


def leg_angles(pts):
    (h, k, a) = pts
    return (math.degrees(math.atan2(k[0] - h[0], k[1] - h[1])), math.degrees(math.atan2(a[0] - k[0], a[1] - k[1])))


HIPS = {k: v[0] for k, v in LEG_POINTS.items()}
THIGH = {k: math.hypot(v[1][0] - v[0][0], v[1][1] - v[0][1]) for k, v in LEG_POINTS.items()}
SHIN = {k: math.hypot(v[2][0] - v[1][0], v[2][1] - v[1][1]) for k, v in LEG_POINTS.items()}
LEG_REST = {k: leg_angles(v) for k, v in LEG_POINTS.items()}


# ------------------------------------------------------------------------------------------------- whole-square moves
def squash(layer, y0, y1, n):
    """n whole rows dropped evenly from rows [y0, y1) of a design-sized layer, the rows above coming down by the rows
    dropped under them (the waist lowered, the hem where it was)."""
    if n <= 0:
        return layer
    n = min(n, y1 - y0 - 1)
    drop = set(min(y1 - 1, int(y0 + (k + 0.5) * (y1 - y0) / n)) for k in range(n))
    keep = [y for y in range(y1) if y not in drop]
    out = np.zeros_like(layer)
    out[y1:] = layer[y1:]
    for i, y in enumerate(reversed(keep)):
        out[y1 - 1 - i] = layer[y]
    return out


def stream(layer, y0, y1, k):
    """Rows from y0 down moved back (to the image-left) by whole columns, 0 at y0 and k from y1 on (the robe flying
    back)."""
    if not k:
        return layer
    out = layer.copy()
    for y in range(y0, layer.shape[0]):
        s_ = int(round(k * min(1.0, (y - y0) / max(1, y1 - y0))))
        if s_ > 0:
            out[y] = 0
            out[y, :-s_] = layer[y, s_:]
    return out


def sheared(layer, lean):
    """A design-sized layer leaning forward above the hips: whole rows moved, the head (rows over LEAN_TOP) one block."""
    if not lean:
        return layer
    out = np.zeros_like(layer)
    for y in range(layer.shape[0]):
        s_ = lean if y <= LEAN_TOP else (0 if y >= HIP_ROW else int(round(lean * (HIP_ROW - y) / (HIP_ROW - LEAN_TOP))))
        if s_ > 0:
            out[y, s_:] = layer[y, :-s_]
        elif s_ < 0:
            out[y, :s_] = layer[y, -s_:]
        else:
            out[y] = layer[y]
    return out


def lean_at(y, lean):
    if not lean:
        return 0
    return lean if y <= LEAN_TOP else (0 if y >= HIP_ROW else int(round(lean * (HIP_ROW - y) / (HIP_ROW - LEAN_TOP))))


def shifted(layer, dx, dy):
    """A design-sized layer moved by whole squares."""
    out = np.zeros_like(layer)
    H, W = layer.shape[:2]
    ys, xs = np.nonzero(layer[..., 3] > 0)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < H) & (tx >= 0) & (tx < W)
    out[ty[ok], tx[ok]] = layer[ys[ok], xs[ok]]
    return out


# ------------------------------------------------------------------------------------------------- the pose
class Pose:
    """One frame. far: the far hand - "rest" (reaching forward palm up, as drawn), "up" (pointing up at its cuff),
    "down", "high" (the sleeve thrown up and out with the hand up from its top); near: the near hand - "hip" (as
    drawn), "high" (the far hand mirrored up over its raised sleeve), "back" (the far hand mirrored, reaching back at
    shoulder height over the hanging sleeve); legs None (the design's) or {side: (thigh, shin) degrees}; ankles {side: (dx, dy) from the hip}; drop (rows
    the hips come down; None: from the drawn legs' feet on the ground); dx, dy (the whole figure), lift (rows off the
    ground), lean (columns at the head), up (the upper body over the hips), stream (columns the robe's hem flies back),
    train (rows the train's tip lifts), train_up (rows the whole train lifts off the ground: flying back in the run),
    breath (rows the body above the waist - head, bust, shoulders, sleeves, hands - settles onto its own waist: the
    idle's breathing; the waist, the legs and the robe stay), flash, lie."""

    def __init__(self, far="rest", near="hip", legs=None, ankles=None, dx=0, dy=0, lift=0, lean=0, up=(0, 0), stream=0,
                 train=0, flash=False, far_leg_shade=False, lie=False, drop=None, train_up=0, breath=0):
        self.far, self.near, self.legs, self.ankles = far, near, legs, ankles
        self.train_up, self.breath = train_up, breath
        self.dx, self.dy, self.lift, self.lean, self.up = dx, dy, lift, lean, up
        self.stream, self.train, self.flash, self.far_leg_shade, self.lie = stream, train, flash, far_leg_shade, lie
        self.drop = drop


def leg_geo(p):
    geo = {}
    for side in ("near", "far"):
        H = HIPS[side]
        if p.ankles is not None:
            ax, ay, *fwd = p.ankles[side]
            K, A = Z.knee(H, (H[0] + ax, H[1] + ay), THIGH[side], SHIN[side], fwd[0] if fwd else 1)
        else:
            th, sh = p.legs[side]
            K = Z.along(H, th, THIGH[side])
            A = Z.along(K, sh, SHIN[side])
        geo[side] = (H, K, A)
    return geo


def hips_drop(D, p, geo):
    """Rows the hips come down so the lowest drawn heel (or knee) stands on the ground."""
    low = []
    for side, (H, K, A) in geo.items():
        off, _ = D.feet[side]
        low.append(A[1] + off[:, 1].max())
        low.append(K[1] + 1.5)
    return int(round(D.ground - max(low)))


def compose(rig, D, p, robe=True):
    """The frame of pose p on the rig's canvas (robe False: without the robe - a body to lay down)."""
    drawn = p.legs is not None or p.ankles is not None
    geo = leg_geo(p) if drawn else None
    drop = p.drop if p.drop is not None else (hips_drop(D, p, geo) if drawn else 0)
    ox, oy = rig.ox + int(round(p.dx)), rig.oy + p.dy - p.lift
    body = (ox + p.up[0], oy + drop + p.up[1])               # the upper body, the hands and the sleeves
    limbs = (body[0], body[1] + p.breath)                    # the sleeves and the hands (they hang from the shoulders)
    can = rig.canvas()
    L = D.layers

    # the robe: the train and the flare stay on the ground (in the run and the casts the train's tip lifts and its
    # hem flies back); the front panels hang from the waist and come down with the hips, sinking into the ground as
    # she crouches (the robe pooling), their hems flying back with the train
    if robe:
        t = stream(L["train"], 50, 63, p.stream)
        if p.train_up:
            t = shifted(t, 0, -p.train_up)
        if p.train:
            t = R.sway(t, 0, 27, p.train, "right")
        Z.stamp(can, t, (ox, oy))
        Z.stamp(can, stream(L["flare"], 50, 63, p.stream), (ox, oy))
        # the slit (the robe's dark inside between the legs) goes with the panels, behind whatever legs she stands on
        pn = np.where(L["slit"][..., 3:] > 0, L["slit"], L["panels"]).astype(np.uint8)
        pn = stream(pn, 46, 57, p.stream)
        pn = sheared(pn, p.lean)
        under = rig.canvas()
        Z.stamp(under, pn, (ox, oy + drop))
        under[rig.GY:] = 0
        m = under[..., 3] > 0
        can[m] = under[m]

    # the far sleeve and hand (behind the body): a hand thrown up takes its sleeve up and out
    sx, sy = SLEEVE_HIGH[p.far]["far"] if p.far in SLEEVE_HIGH else (0, 0)
    Z.stamp(can, sheared(L["far_sleeve"], p.lean), (limbs[0] + sx, limbs[1] + sy))
    op = {"rest": (False, 0), "up": (False, 1), "high": (False, 1), "top": (False, 1), "down": (False, 3)}[p.far]
    hand = sheared(L["far_hand"], p.lean)
    elbow = (ELBOW[0] + lean_at(int(ELBOW[1]), p.lean), ELBOW[1])
    Z.stamp(can, hand, (limbs[0] + sx, limbs[1] + sy), op, elbow)

    # the legs
    if drawn:
        for side in ("far", "near"):
            H, K, A = ((ox + v[0], oy + v[1] + drop) for v in geo[side])
            lay = Z.Layer()
            shade = (lambda c: Z.darker(c)) if (side == "far" and p.far_leg_shade) else None
            prof = {k: [(a, b, [shade(c) if shade else c for c in pr]) for a, b, pr in v]
                    for k, v in LEG_PROFILE[side].items()}
            lay.bone(H, K, prof["thigh"])
            lay.bone(K, A, prof["shin"])
            lay.paste(D.feet[side], A, shade=shade)
            lay.draw(can, INK)
    else:
        Z.stamp(can, L["legs"], (ox, oy))

    # the upper body, then the near sleeve and hand (in front)
    up_l = sheared(L["upper"], p.lean)
    if p.breath:
        # the waist and below where they are, the rows above it settled onto it (whole rows, the legs untouched: the
        # whole upper body sinking onto the legs read as squashed legs - the user: 「上下摆动导致腿部变形」)
        low = up_l.copy()
        low[:BREATH_ROW] = 0
        Z.stamp(can, low, body)
        high = up_l.copy()
        high[BREATH_ROW:] = 0
        Z.stamp(can, high, (body[0], body[1] + p.breath))
    else:
        Z.stamp(can, up_l, body)
    nx, ny = SLEEVE_HIGH[p.near]["near"] if p.near in SLEEVE_HIGH else (0, 0)
    Z.stamp(can, sheared(L["near_sleeve"], p.lean), (limbs[0] + nx, limbs[1] + ny))
    if p.near == "hip":
        Z.stamp(can, sheared(L["near_hand"], p.lean), limbs)
    else:
        # the far hand mirrored onto the near side: pointing up from the raised sleeve's top (high), or reaching back
        # at shoulder height out of the sleeve's top corner, the sleeve hanging under it as the far one does (back)
        lean = lean_at(int(NEAR_SHOULDER[1]), p.lean)
        up = ((NEAR_UP_X + nx, NEAR_SHOULDER[1] + ny), (True, 3))
        cuff, op = ({"high": up, "top": up, "back": (NEAR_BACK, (True, 0))})[p.near]
        at = (limbs[0] + cuff[0] + lean - ELBOW[0], limbs[1] + cuff[1] - ELBOW[1])
        Z.stamp(can, L["far_hand"], at, op, ELBOW)
    return R.flash(can) if p.flash else can


# ------------------------------------------------------------------------------------------------- League's frames
def ang(a, b):
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))


def league_legs(j, d0, k=1.0):
    """The design's own leg angles plus League's change from its idle (League's right leg is the near one here)."""
    out = {}
    for side, sd in (("near", "r"), ("far", "l")):
        th = ang(j[f"{sd}_hip"], j[f"{sd}_knee"]) - ang(d0[f"{sd}_hip"], d0[f"{sd}_knee"])
        sh = ang(j[f"{sd}_knee"], j[f"{sd}_foot"]) - ang(d0[f"{sd}_knee"], d0[f"{sd}_foot"])
        out[side] = (LEG_REST[side][0] + th * k, LEG_REST[side][1] + sh * k)
    return out


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def league_feet(j, d0):
    """(rows the hips come down, {side: (ankle dx, dy from its hip, the knee's side)}) from League's frame: the pelvis
    height's change (K_LEG rows a League px) and each foot where League has it from its hip, scaled to her leg's
    length, never under the ground; the knee bent to League's side of the hip-foot line."""
    drop = (j["pelvis"][1] - d0["pelvis"][1]) * K_LEG
    out = {}
    for side, sd in (("near", "r"), ("far", "l")):
        h, k, f = j[f"{sd}_hip"], j[f"{sd}_knee"], j[f"{sd}_foot"]
        l0 = dist(d0[f"{sd}_hip"], d0[f"{sd}_knee"]) + dist(d0[f"{sd}_knee"], d0[f"{sd}_foot"])
        sc = (THIGH[side] + SHIN[side]) / l0
        vx, vy = (f[0] - h[0]) * sc, (f[1] - h[1]) * sc
        vy = min(vy, ANKLE_Y - HIPS[side][1] - max(0.0, drop))
        cross = (f[0] - h[0]) * (k[1] - h[1]) - (f[1] - h[1]) * (k[0] - h[0])
        out[side] = (vx, vy, 1 if cross <= 0 else -1)
    return drop, out


# Q's lunge: the near (back) leg stretched out behind, the far (front) knee bent over its foot
LUNGE = {"near": (-8.0, None, 1), "far": (6.0, None, 1)}

# per tag, per frame (after League's renders): hands, drawn legs (League's), lean, robe, lift
ACTS = {
    # League's Attack2: from her stance the near arm sweeps out back and up over her shoulder (the bolt leaves her far
    # hand at the target), the robe swirling up behind her, then back down
    "attack": [dict(train=1),
               dict(near="back", lean=-1, train=2, stream=1),
               dict(near="high", lean=-1, train=3, stream=2),
               dict(near="high", train=2, stream=1),
               dict(train=1)],
    # League's Spell1 (Q): both arms thrown up, the sleeves held high over her head; then down into a wide low lunge,
    # the far hand thrust at the target and the near one back, the robe flying back at hip height
    "skill": [dict(far="high", near="high", lean=-1, train=1),
              dict(far="top", near="top", lean=-1, train=2),
              dict(far="rest", near="back", drawn=True, drop=4, feet=LUNGE, lean=2, stream=3, train=3, train_up=3),
              dict(far="rest", near="back", drawn=True, drop=5, feet=LUNGE, lean=3, stream=4, train=4, train_up=5),
              dict(far="rest", near="back", drawn=True, drop=5, feet=LUNGE, lean=3, stream=4, train=3, train_up=5),
              dict(train=1)],
    # League's Spell3 (E): a spin down into a deep crouch, a hand to the ground in front and the other arm back - the
    # orb thrown along the ground - the robe draped back over her
    "skill2": [dict(far="up", drawn=True, lean=1, train=1),
               dict(far="down", near="back", drawn=True, lean=3, stream=2, train=3, train_up=3),
               dict(far="down", near="back", drawn=True, lean=4, stream=3, train=4, train_up=6),
               dict(far="down", near="back", drawn=True, lean=4, stream=3, train=4, train_up=6),
               dict(far="rest", near="back", drawn=True, lean=3, stream=2, train=3, train_up=3),
               dict(drawn=True, lean=1)],
    # League's Spell4 (R): arms spread, she rises high with the sleeves over her head and the robe flung out like wings,
    # then slams down into a deep crouch, the robe thrown up behind her (the near hand back on her hip: reaching back
    # it lay over the thrown robe)
    "ult": [dict(far="rest", near="back", train=2),
            dict(far="top", near="top", drawn=True, train=4, stream=2),
            dict(far="top", near="top", drawn=True, train=5, stream=3),
            dict(far="down", drawn=True, lean=3, stream=3, train=5, train_up=13),
            dict(far="down", drawn=True, lean=3, stream=3, train=4, train_up=10),
            dict(drawn=True, train=1)],
    "hit": [dict(dx=-2, flash=True), dict(dx=-1)],
    # League's Death: a stagger back hunched in the robe, down to her knees, a fall forward onto her face
    "dead": [dict(dx=-1, drawn=True),
             dict(dx=-2, far="down", near="back", drawn=True, lean=-2),
             dict(dx=-2, far="down", drawn=True, lean=2),
             dict(dx=-1, far="down", drawn=True, lean=3)]
    + [dict(lie=True)] * 4,
}
# the run (league_caitlyn's way, scaled to her short legs): one leg's ankle in eight phases from its hip (squares
# forward, down), the far leg four phases on
RUN_PHASES = [(7.0, 12.3), (3.5, 13.0), (-0.8, 13.4), (-4.5, 12.6), (-7.0, 10.6), (-5.2, 8.6), (0.8, 9.0), (5.2, 10.8)]
RUN_LIFT = [0, 0, 0, 1, 0, 0, 0, 1]
RUN_LEAN = 2
RUN_STREAM = [3, 4, 5, 4, 3, 4, 5, 4]
RUN_TRAIN = [3, 4, 5, 4, 3, 4, 5, 4]
RUN_TRAIN_UP = [6, 6, 5, 5, 6, 6, 5, 5]                # League's robe streams behind at hip height, off the ground
DEAD_SINK = 4
DEAD_FALL = 4                                # rows over the ground the falling body still is


def idle_frames(rig, D, n):
    """The design breathing: the body above the waist (head, bust, shoulders, the sleeves and the hands) settles a row
    onto the waist; the waist, the legs and the robe stay where they are."""
    sinks = [0, 0, 1, 1, 1, 1, 0, 0]
    sway = [0, 0, 0, 1, 1, 1, 0, 0]                        # the train's tip stirring
    return [compose(rig, D, Pose(breath=sinks[i % 8], train=sway[i % 8])) for i in range(n)]


def make_rig(D):
    rig = R.Rig(D, pad=(60, 60, 50, 30))
    # the cracks a move opens between the legs, the robe's panels and its train closed with the outline (gap-check):
    # holes of at most CRACK squares, no wider than CRACK_W from their middle, in the robe's rows, the idle without them
    rig.fill_rows = (ROBE_TOP + 3, GROUND)
    rig.CRACK, rig.CRACK_W = 14, 1.5
    rig.idle_canvas = compose(rig, D, Pose())
    return rig


def tag_poses(tag, rows, d0):
    out = []
    for i, r in enumerate(rows):
        j = r["j"]
        if tag == "run":
            ph = i % 8
            # her arms as drawn (League's run carries them low out from her sides; held out at shoulder height they read
            # as a T): the near hand on her hip, the far one forward palm up
            p = Pose(ankles={"near": RUN_PHASES[ph], "far": RUN_PHASES[(ph + 4) % 8]}, lean=RUN_LEAN,
                     lift=RUN_LIFT[ph], stream=RUN_STREAM[ph], train=RUN_TRAIN[ph], train_up=RUN_TRAIN_UP[ph],
                     far_leg_shade=True)
            out.append(p)
            continue
        a = ACTS[tag][i]
        ankles, drop, lift = None, None, a.get("lift", 0)
        if a.get("drawn"):
            dr, ankles = league_feet(j, d0)
            drop = int(round(dr)) if a.get("drop") is None else a["drop"]
            if drop < 0:                                       # League's pelvis over its idle height: she rises
                lift, drop = lift - drop, 0
            # feet set by hand where League's on her short chibi legs fold into one block: (dx from the hip, dy or
            # None for standing on the ground, the knee's side)
            for side, (fx, fy, fw) in (a.get("feet") or {}).items():
                ankles[side] = (fx, ANKLE_Y - HIPS[side][1] - drop if fy is None else fy, fw)
        p = Pose(far=a.get("far", "rest"), near=a.get("near", "hip"), ankles=ankles, drop=drop, dx=a.get("dx", 0),
                 lean=a.get("lean", 0), lift=lift, up=a.get("up", (0, 0)), stream=a.get("stream", 0),
                 train=a.get("train", 0), train_up=a.get("train_up", 0), flash=a.get("flash", False),
                 lie=a.get("lie", False), far_leg_shade=bool(a.get("drawn")))
        out.append(p)
    return out


def lying(rig, D, sink=None):
    """Face down, head to the image-right (League's fall forward): the body without its robe a quarter turn clockwise,
    sunk into the ground, the robe's train laid flat behind her feet."""
    sink = DEAD_SINK if sink is None else sink
    flat = compose(rig, D, Pose(far="down"), robe=False)
    body = R.lie(rig, flat, k=3, dx=3, sink=sink)
    train = np.where(D.layers["flare"][..., 3:] > 0, D.layers["flare"], D.layers["train"]).astype(np.uint8)
    ys, xs = np.nonzero(body[..., 3] > 0)
    under = rig.canvas()
    feet_x = xs.min()                                      # her soles are now at the left end
    Z.stamp(under, train, (feet_x + 4 - 30, rig.oy + sink - 1))
    m = (body[..., 3] == 0) & (under[..., 3] > 0)
    body[m] = under[m]
    return body


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
            # the fall forward (League's 1500 ms: diving onto her face): the lying body still DEAD_FALL rows up, then
            # on the ground, a row's bounce, lying
            fall = lying(rig, D, sink=DEAD_SINK - DEAD_FALL)
            bounce = lying(rig, D, sink=DEAD_SINK - 1)
            lie = lying(rig, D)
            fr = fr[:4] + [fall, lie, bounce, lie.copy()]
        out[tag] = list(zip(fr, ms))
    return out


TINT = {"far_hand": (255, 255, 0), "far_sleeve": (0, 200, 255), "near_sleeve": (0, 255, 128), "near_hand": (255, 0, 255),
        "legs": (255, 128, 0), "panels": (128, 0, 255), "train": (255, 0, 0), "flare": (255, 160, 160), "slit": (0, 0, 0)}


def parts_png(D, path, z=11):
    img = D.d0.astype(float).copy()
    for n, c in TINT.items():
        m = D.parts[n]
        img[m, :3] = img[m, :3] * 0.45 + np.array(c) * 0.55
    big = Image.fromarray(np.repeat(np.repeat(img.astype(np.uint8), z, 0), z, 1))
    bg = Image.new("RGBA", big.size, (210, 210, 210, 255))
    bg.alpha_composite(big)
    up = Image.fromarray(np.repeat(np.repeat(D.layers["upper"], z, 0), z, 1))
    bg2 = Image.new("RGBA", up.size, (210, 210, 210, 255))
    bg2.alpha_composite(up)
    can = Image.new("RGB", (bg.width * 2 + 20, bg.height), (255, 255, 255))
    can.paste(bg.convert("RGB"), (0, 0))
    can.paste(bg2.convert("RGB"), (bg.width + 20, 0))
    can.save(path)


def audit(rig, acts, out_dir, z=6):
    """Per frame: the pieces it falls into besides the biggest (tinted red) and the holes the idle does not have
    (magenta), every tag at z x in out_dir; returns the flagged frames."""
    import ppu_rig_audit as A
    _, _, idle_holes = A.holes(rig.finish(acts["idle"][0][0]))
    report = []
    os.makedirs(out_dir, exist_ok=True)
    for tag, fr in acts.items():
        tiles = []
        for i, (c, _) in enumerate(fr):
            a = rig.finish(c)
            lbl, ps = A.pieces(a)
            hm, hn, ha = A.holes(a)
            flag = []
            if len(ps) > 1:
                flag.append(f"pieces {[s_ for s_, _ in ps[1:]]}")
            if ha > idle_holes + 2:
                flag.append(f"holes {ha} (idle {idle_holes})")
            if flag:
                report.append(f"{tag}[{i}]: " + "; ".join(flag))
            t = a.copy()
            for _, k in ps[1:]:
                t[lbl == k] = (255, 0, 0, 255)
            t[hm] = (255, 0, 255, 255)
            tiles.append(t)
        allc = np.max([t[..., 3] for t in tiles], 0)
        ys, xs = np.nonzero(allc)
        y0, y1, x0, x1 = ys.min() - 1, max(ys.max() + 2, rig.GY + 1), xs.min() - 1, xs.max() + 2
        w, h = (x1 - x0) * z, (y1 - y0) * z
        img = Image.new("RGB", (len(tiles) * (w + 8), h), (60, 60, 60))
        for j, t in enumerate(tiles):
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(t[y0:y1, x0:x1]))
            img.paste(bg.convert("RGB").resize((w, h), Image.NEAREST), (j * (w + 8), 0))
        img.save(os.path.join(out_dir, f"{HERO}_{tag}.png"))
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    D = Design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        parts_png(D, os.path.join(a.parts, f"{HERO}_parts.png"))
        rig = make_rig(D)
        rest = rig.finish(compose(rig, D, Pose()))
        ref = rig.canvas()
        Z.stamp(ref, D.d0, (rig.ox, rig.oy))
        print({k: int(v.sum()) for k, v in D.parts.items()}, "rest frame differs in",
              int((rest != rig.finish(ref)).any(-1).sum()), "squares")
        return
    if not a.joints:
        sys.exit("--joints is needed")
    with open(a.joints, encoding="utf-8") as f:
        joints = json.load(f)
    rig = make_rig(D)
    acts = frames(rig, joints)
    if a.audit:
        rep = audit(rig, acts, a.audit)
        print(len(rep), "frames flagged")
        for line in rep:
            print("  " + line)
        return
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()

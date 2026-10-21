#!/usr/bin/env python3
"""league_zoe's action frames, posed by hand after League's own clips, frame by frame, on the approved designs (the user,
2026-10-22: 「佐伊只需要 完善动作帧 我觉得动作帧是不全的」 - the design stays; the first rig, 2026-10-19, moved her legs
only whole, so the run hardly moved, and a somersault or the fall jumped across in one or two frames).

    python tools/art/rig_zoe.py --parts DIR       # the side design's parts tinted, at 12x
    python tools/art/rig_zoe.py --review DIR      # every tag next to League's clip at 3x + one GIF
    python tools/art/rig_zoe.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero zoe && python tools/art/ppu_hd.py --hero zoe

The designs (tools/art/design_zoe_model.py, the user's picks 2026-10-19; 35 game px at PPU 1.5, one palette):
  hd/side.png   side-on facing right with the 3/4 face, 48 x 53: every action
  hd/idle.png   3/4 front, arms out, 59 x 53: the idle, and the front-facing beats of a spin (W, the death)
How a frame is made (league_orianna's chibi rig, tools/art/rig_orianna.py):
  * the head with its whole mane is one block, moved by whole squares (a lean carries it by the neck's amount); the
    mane's tail may sway a row or two (whole columns, nothing at the head);
  * the scarf, the top and the skirt are the side design's own squares moved whole, a lean an even shear of whole rows
    above the hips;
  * the limbs are drawn: arms and legs as bands in the design's own skin shades (lit on the left, one outline), the
    design's own bangle and hand pasted at the wrist (in its eight lossless orientations) and its own boots at the
    ankles; a limb at rest is the design's own squares;
  * a somersault or a fall turns the whole figure by quarter turns (lossless: a RotSprite turn breaks a face), a spin
    shows the 3/4 design and the mirrored side between the side frames;
  * every tag keeps the kit's length, its release on the same frame start (tools/kit/build_zoe.py: a_rel, q_rel, e_rel,
    r_rel, w_rel and w_gap).
The frames go out through ppu_rig.Rig (the old rig's canvas and standing point, so the effects keep their places).
"""
import argparse
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import rigkit as RK  # noqa: E402
import ppu_rig as R  # noqa: E402
from rig_orianna import along, best_hand, dist, hand_variants, heading, ik, stamp, zoom  # noqa: E402
from rig_wukong import CutDesign as _Cut  # noqa: E402

HERO = "zoe"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "zoe", "hd")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "zo_q")
OUTLINE = (10, 3, 22)
PAD = (60, 60, 70, 20)              # the old rig's canvas round the side design (left, right, top, bottom)


def lp(path):
    return R.lp(path)


def load(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def stand_col(d, rows=3):
    """The middle of the lowest `rows` rows' squares: where the design stands (an edge between two columns)."""
    op = d[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys.max() - rows + 1:ys.max() + 1].any(0))[0]
    return int(round((xs.min() + xs.max() + 1) / 2))


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def spans(shape, table):
    """{row: (first col, last col)} -> mask (design coordinates)."""
    m = np.zeros(shape[:2], bool)
    for y, (x0, x1) in table.items():
        m[y, x0:x1 + 1] = True
    return m


# ------------------------------------------------------------------------------------------------- the side's parts
# read square by square off hd/side.png (x a column, y a row; a square's middle at +0.5)
ARM_SPANS = {28: (32, 36), 29: (32, 36), 30: (32, 35), 31: (32, 35), 32: (31, 34), 33: (31, 34), 34: (30, 34),
             35: (30, 33)}                    # the near upper arm and forearm, hanging by her side
HAND_SPANS = {36: (30, 34), 37: (29, 34), 38: (28, 34), 39: (29, 34), 40: (28, 33), 41: (28, 32), 42: (29, 31)}
SHOULDER, WRIST, HAND_TIP = (34.5, 28.5), (31.5, 36.0), (30.5, 42.0)
ELBOW = (33.0, 32.5)
F_SHOULDER = (39.5, 28.5)                     # the far shoulder, behind the scarf (that arm is hidden in the design)
UP_LEN, FORE_LEN = dist(SHOULDER, ELBOW), dist(ELBOW, WRIST)
HEAD_ROW = 24                                 # the head: rows to the chin's shadow; the scarf from row 25
LOCK = (25, 26, 45, 47)                       # the front lock of hair hanging over the scarf (rows, columns)
MANE_COL = 31                                 # the mane: columns to here below the head
NECK = (38.5, 25.0)
LEG_TOP = 41                                  # the legs: rows from here, under the skirt's hem
RIBBON = (41, 45, 45, 47)                     # the skirt's ribbon hanging over the far thigh (rows, columns): the torso's
NEAR_LEG_SPANS = {**{y: (33, 39) for y in range(41, 51)}, 51: (32, 41), 52: (33, 41)}
N_HIP, N_KNEE, N_ANKLE = (36.5, 40.5), (36.5, 44.0), (36.0, 47.0)
F_HIP, F_KNEE, F_ANKLE = (41.5, 40.5), (41.5, 44.0), (41.5, 47.0)
LEG_L1, LEG_L2 = dist(N_HIP, N_KNEE), dist(N_KNEE, N_ANKLE)
KICK_ROOT = (37.5, 42.5)                      # where a kicking leg comes out from under the skirt's hem
BOOT_ROWS = (47, 52)                          # each boot: these rows of its leg (the far one with its last shin row)
GROUND = 47.0                                 # an ankle's row with the boot standing on the ground
HIP_ROW = 41                                  # a lean shears the rows above
SKIN = {"v": (253, 200, 162), "s": (251, 150, 119), "o": (222, 99, 84), "l": (156, 94, 88)}
NEAR_LEG, FAR_LEG = "svvvs", "ossso"          # across a leg, lit side first (side.png rows 43-46)
NEAR_ARM, FAR_ARM = "vvs", "sso"              # across an arm (side.png rows 29-35)
LIGHT = (-0.6, -0.8)                          # towards the light (upper left)


class Piece:
    """A sprite cut from a design with its joint (design coordinates)."""

    def __init__(self, a, mask, joint):
        m = mask & (a[..., 3] > 0)
        ys, xs = np.nonzero(m)
        self.y0, self.x0 = ys.min(), xs.min()
        s = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
        sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        mm = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        s[mm] = sub[mm]
        self.s, self.mask = s, m
        self.j = (joint[0] - self.x0, joint[1] - self.y0)


def darker(a):
    """The skin a shade darker (the far limbs' boots and hands keep their own colours otherwise)."""
    order = [SKIN["v"], SKIN["s"], SKIN["o"], SKIN["l"]]
    out = a.copy()
    for i, c in enumerate(order[:-1]):
        m = (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - c).sum(-1) == 0)
        out[m, :3] = order[i + 1]
    return out


class Kit:
    """The designs and their parts, cut once."""

    def __init__(self):
        self.side, self.front = load("side.png"), load("idle.png")
        S = self.side
        H, W = S.shape[:2]
        yy, xx = np.mgrid[:H, :W]
        op = S[..., 3] > 0
        arm = spans(S.shape, ARM_SPANS) & op
        hand = spans(S.shape, HAND_SPANS) & op
        legs = op & (yy >= LEG_TOP) & (xx >= 32) & ~hand
        r0, r1, c0, c1 = RIBBON
        legs &= ~((yy >= r0) & (yy <= r1) & (xx >= c0) & (xx <= c1))
        near = legs & spans(S.shape, NEAR_LEG_SPANS)
        far = legs & ~near
        l0, l1, k0, k1 = LOCK
        head = op & ((yy <= HEAD_ROW) | ((yy >= l0) & (yy <= l1) & (xx >= k0) & (xx <= k1)))
        mane = op & (yy > HEAD_ROW) & (xx <= MANE_COL) & ~arm & ~hand & ~head
        torso = op & ~(arm | hand | legs | head | mane)
        self.masks = dict(head=head, mane=mane, torso=torso, arm=arm, hand=hand, near_leg=near, far_leg=far)
        self.layer = {k: np.where(m[..., None], S, 0).astype(np.uint8) for k, m in self.masks.items()}
        self.hand = Piece(S, hand, WRIST)
        self.hands = hand_variants(self.hand.s, self.hand.j, HAND_TIP)
        self.hands_dark = hand_variants(darker(self.hand.s), self.hand.j, HAND_TIP)
        b0, b1 = BOOT_ROWS
        boot_rows = (yy >= b0) & (yy <= b1)
        self.n_boot = Piece(S, near & boot_rows, N_ANKLE)
        self.f_boot = Piece(S, far & boot_rows, F_ANKLE)
        # the canvas: the old rig's (ppu_rig.Rig round the side design, its standing point)
        self.D = CutDesign(S, px=stand_col(S))
        self.rig = R.Rig(self.D, pad=PAD)
        self.ox, self.oy = self.rig.ox, self.rig.oy
        self.CX, self.GY = self.rig.CX, self.rig.GY
        self.front_at = (self.CX - stand_col(self.front), self.GY - self.front.shape[0])

    def canvas(self):
        return self.rig.canvas()

    def put(self, can, a, at):
        """A design-sized layer onto can with its (0, 0) at canvas (x, y) (whole squares), over what is there."""
        x, y = at
        h, w = a.shape[:2]
        y0, x0 = max(0, y), max(0, x)
        y1, x1 = min(can.shape[0], y + h), min(can.shape[1], x + w)
        if y1 <= y0 or x1 <= x0:
            return
        src = a[y0 - y:y1 - y, x0 - x:x1 - x]
        m = src[..., 3] > 0
        can[y0:y1, x0:x1][m] = src[m]


def tint(kit, z=12):
    colours = dict(head=(255, 0, 0), mane=(255, 160, 0), torso=(0, 200, 255), arm=(255, 0, 255), hand=(128, 0, 255),
                   near_leg=(0, 255, 0), far_leg=(255, 255, 0))
    out = kit.side.copy()
    for name, c in colours.items():
        m = kit.masks[name] & ~(np.abs(out[..., :3].astype(int) - OUTLINE).sum(-1) < 12)
        out[m, :3] = (out[m, :3] * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    return zoom(np.pad(out, ((1, 1), (1, 1), (0, 0))), z, 0, 0, out.shape[1] + 2, out.shape[0] + 2)


# ------------------------------------------------------------------------------------------------- drawing limbs
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def band(layer, p0, p1, prof, ext0=0.0, ext1=0.0):
    """A limb from p0 to p1 (canvas, continuous) into layer: every square whose middle lies within the band (as wide as
    prof has letters) coloured by where it lies across it, the lit side first (prof's first letter towards LIGHT), with
    an outline ring where the layer is clear; ext0 / ext1 lengthen it past its ends (into the joints)."""
    vx, vy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(vx, vy) or 1e-6
    ux, uy = vx / L, vy / L
    nx, ny = -uy, ux
    lit = 1.0 if nx * LIGHT[0] + ny * LIGHT[1] >= 0 else -1.0
    hw = len(prof) / 2.0
    r = hw + max(ext0, ext1) + 2
    fill = np.zeros(layer.shape[:2], bool)
    col = np.zeros(layer.shape[:2] + (3,), np.uint8)
    for y in range(max(0, int(min(p0[1], p1[1]) - r)), min(layer.shape[0], int(max(p0[1], p1[1]) + r) + 1)):
        for x in range(max(0, int(min(p0[0], p1[0]) - r)), min(layer.shape[1], int(max(p0[0], p1[0]) + r) + 1)):
            cx, cy = x + 0.5 - p0[0], y + 0.5 - p0[1]
            t = cx * ux + cy * uy
            if t < -ext0 or t > L + ext1:
                continue
            d = (cx * nx + cy * ny) * lit             # + towards the light
            if abs(d) > hw:
                continue
            i = int((hw - d) / (2 * hw) * len(prof))
            fill[y, x] = True
            col[y, x] = SKIN[prof[min(len(prof) - 1, max(0, i))]]
    ring = ndimage.binary_dilation(fill, structure=CROSS) & ~fill & (layer[..., 3] == 0)
    layer[ring, :3] = OUTLINE
    layer[ring, 3] = 255
    layer[fill, :3] = col[fill]
    layer[fill, 3] = 255


def turned(piece, deg):
    """(sprite, joint) of a piece turned deg counter-clockwise on screen about its joint (quarter turns exact)."""
    if abs(deg) < 1.0:
        return piece.s, piece.j
    p = RK.turn(RK.Part(piece.s, piece.j), deg)
    return p.s, p.j


def sway(a, k, attach=MANE_COL):
    """Columns left of `attach` moved down k rows at the free end (up when k < 0), in proportion, whole columns
    (nothing at the head): the mane's tail."""
    if not k:
        return a
    out = np.zeros_like(a)
    for x in range(a.shape[1]):
        s = int(round(k * max(0, attach - x) / attach))
        if s > 0:
            out[s:, x] = a[:-s, x]
        elif s < 0:
            out[:s, x] = a[-s:, x]
        else:
            out[:, x] = a[:, x]
    return out


def sheared(a, k, row0):
    """Rows above canvas row row0 moved floor(k x rows above) columns (whole rows): the upper body's lean."""
    if not k:
        return a
    out = np.zeros_like(a)
    for y in range(a.shape[0]):
        dx = int(math.floor(k * (row0 - y))) if y < row0 else 0
        if dx == 0:
            out[y] = a[y]
        elif dx > 0:
            out[y, dx:] = a[y, :-dx]
        else:
            out[y, :dx] = a[y, -dx:]
    return out


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    dx, dy = int(dx), int(dy)
    out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = \
        a[max(0, -dy):H + min(0, -dy), max(0, -dx):W + min(0, -dx)]
    return out


# ------------------------------------------------------------------------------------------------- a frame
class Pose(dict):
    """A frame's pose; every key optional (the side design's own stance when absent):
    wx, lift           the whole figure moved forward / up (squares)
    dx, dy             the hips against the feet (dy > 0: down - a crouch with the feet planted)
    lean               columns the upper body moves forward per row above the hips (an even shear)
    head               (dx, dy) the head with its mane moved further than the neck
    mane               rows the mane's tail sways (+ down)
    n_arm, f_arm       None (near: the design's arm; far: hidden) or (upper arm heading, forearm heading[, hand
                       heading]) in screen degrees counter-clockwise from +x
    n_leg, f_leg       None (the design's leg), ("ang", thigh, shin[, boot degrees]) or ("ik", ankle x, ankle y[, boot])
                       - the ankle in design coordinates on the ground (moved by wx and lift, not by dx / dy)
    flip               k: the whole figure turned k quarter turns clockwise (a forward somersault), its middle
                       `at` = (dx) from the standing point, its lowest row (dy) rows above the ground
    lie                k: turned k quarter turns clockwise, lying with its lowest row on the ground (+ sink), its
                       middle `at` dx from the standing point; what reaches under the ground is not drawn
    mirror             facing left (a spin)
    """


def compose(kit, p):
    can = kit.canvas()
    wx, lift = p.get("wx", 0), p.get("lift", 0)
    dx, dy = p.get("dx", 0), p.get("dy", 0)
    k = p.get("lean", 0.0)
    ox, oy = kit.ox, kit.oy

    def body_pt(pt):
        sx = math.floor(k * (HIP_ROW - pt[1])) if pt[1] < HIP_ROW else 0
        return (pt[0] + sx + wx + dx + ox, pt[1] + dy - lift + oy)

    def hip_pt(pt):
        return (pt[0] + wx + dx + ox, pt[1] + dy - lift + oy)

    def ground_pt(pt):
        return (pt[0] + wx + ox, pt[1] - lift + oy)

    layers = []                                   # (z, canvas-sized RGBA)

    def limb_arm(z, shoulder, ang, prof, hands):
        up, fore = ang[0], ang[1]
        hand_ang = ang[2] if len(ang) > 2 else fore
        lay = kit.canvas()
        elbow = along(shoulder, up, UP_LEN)
        wrist = along(elbow, fore, FORE_LEN)
        band(lay, shoulder, elbow, prof, ext0=1.0, ext1=0.6)
        band(lay, elbow, wrist, prof, ext0=0.6, ext1=0.0)
        _, s, j = best_hand(hands, hand_ang)
        stamp(lay, s, j, wrist)
        layers.append((z, lay))

    # the far arm, behind everything
    if p.get("f_arm"):
        limb_arm(10, body_pt(F_SHOULDER), p["f_arm"], FAR_ARM, kit.hands_dark)
    # the head with its mane (behind the scarf), carried by the neck
    hx, hy = p.get("head", (0, 0))
    nk = body_pt(NECK)
    at = (int(round(nk[0] - NECK[0])) + hx, int(round(nk[1] - NECK[1])) + hy)
    head = kit.canvas()
    kit.put(head, sway(kit.layer["mane"], p.get("mane", 0)), at)
    kit.put(head, kit.layer["head"], at)
    layers.append((15, head))
    # the legs, under the skirt
    for side, z in (("f", 20), ("n", 22)):
        spec = p.get(side + "_leg")
        lay = kit.canvas()
        if spec is None:
            kit.put(lay, kit.layer["near_leg" if side == "n" else "far_leg"], (wx + ox, oy - lift))
            layers.append((z, lay))
            continue
        hip = hip_pt(N_HIP if side == "n" else F_HIP)
        if spec[0] == "kick":
            # ("kick", heading, reach[, boot]): one straight band from under the skirt's hem, `reach` squares - longer
            # than the leg, so the shot-out leg clears the skirt (league_zoe's first kick, 2026-10-19)
            root = hip_pt(KICK_ROOT)
            ank = along(root, spec[1], spec[2])
            prof = NEAR_LEG if side == "n" else FAR_LEG
            band(lay, root, ank, prof[1:], ext0=1.0, ext1=0.6)
            s, j = turned(kit.n_boot if side == "n" else kit.f_boot, spec[3] if len(spec) > 3 else 0.0)
            stamp(lay, s, j, ank)
            layers.append((z, lay))                 # under the skirt: the hem and the ribbon over its root
            continue
        if spec[0] == "ang":
            th, sh = spec[1], spec[2]
        else:
            ank = ground_pt((spec[1], spec[2]))
            kn = ik(hip, ank, LEG_L1, LEG_L2, bend=1)
            th, sh = heading(hip, kn), heading(kn, ank)
        boot_deg = spec[3] if len(spec) > 3 else 0.0
        knee = along(hip, th, LEG_L1)
        ank = along(knee, sh, LEG_L2)
        prof = NEAR_LEG if side == "n" else FAR_LEG
        band(lay, hip, knee, prof, ext0=2.0, ext1=0.8)
        band(lay, knee, ank, prof, ext0=0.8, ext1=0.6)
        s, j = turned(kit.n_boot if side == "n" else kit.f_boot, boot_deg)
        stamp(lay, s, j, ank)
        layers.append((z, lay))
    # the scarf, the top and the skirt, leant
    tor = kit.canvas()
    kit.put(tor, kit.layer["torso"], (ox, oy))
    tor = sheared(tor, k, HIP_ROW + oy)
    layers.append((30, shift(tor, wx + dx, dy - lift)))
    # the near arm
    if p.get("n_arm"):
        limb_arm(50, body_pt(SHOULDER), p["n_arm"], NEAR_ARM, kit.hands)
    else:
        lay = kit.canvas()
        sh_ = body_pt(SHOULDER)
        at = (int(round(sh_[0] - SHOULDER[0])), int(round(sh_[1] - SHOULDER[1])))
        kit.put(lay, kit.layer["arm"], at)
        kit.put(lay, kit.layer["hand"], at)
        layers.append((50, lay))
    for z, lay in sorted(layers, key=lambda t: t[0]):
        m = lay[..., 3] > 0
        can[m] = lay[m]
    if not p.get("lift"):
        can[kit.GY:] = 0                          # nothing under the ground (a planted boot rounded down)
    can = neck_gaps(can)
    return place(kit, finish(can), p)


def place(kit, can, p):
    """The whole-figure moves: a mirror, a quarter-turned somersault, lying."""
    if p.get("mirror"):
        can = mirrored(kit, can)
    for key in ("flip", "lie"):
        if p.get(key) is None:
            continue
        ys, xs = np.nonzero(can[..., 3] > 0)
        fig = np.rot90(can[ys.min():ys.max() + 1, xs.min():xs.max() + 1], -(p[key] % 4)).copy()
        out = kit.canvas()
        ax, ay = p.get("at", (0, 0))
        h, w = fig.shape[:2]
        x0 = int(round(kit.CX + ax - w / 2))
        y0 = kit.GY - ay - h if key == "flip" else kit.GY + p.get("sink", 0) - h
        kit.put(out, fig, (x0, y0))
        if key == "lie":
            out[kit.GY:] = 0
        can = out
    return can


def mirrored(kit, can):
    """Facing left: column x to 2 CX - 1 - x (the standing point, an edge, stays)."""
    out = kit.canvas()
    W = can.shape[1]
    src = can[:, ::-1]
    s = 2 * kit.CX - W
    if s >= 0:
        out[:, s:] = src[:, :W - s]
    else:
        out[:, :W + s] = src[:, -s:]
    return out


def neck_gaps(can, most=30, crack=20):
    """Enclosed gaps (the stance has none; memory gap-check) filled: thin cracks (at most two squares across) with the
    outline, the others - the room a moved arm leaves between her back and the mane, a stride's space under the
    skirt - with the hair's dark navy (the mane hangs behind her back; in the design the arm covered that spot, so
    nothing is drawn there)."""
    op = can[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for i in range(1, n + 1):
        m = lbl == i
        if m.sum() > most:
            continue
        thin = m.sum() <= crack and ndimage.distance_transform_edt(m).max() <= 1.0
        out[m, :3] = OUTLINE if thin else (26, 40, 79)
        out[m, 3] = 255
    return out


def finish(can):
    """The outline closed round moved edges, pinholes of up to 2 squares filled from their neighbours, specks under 6
    squares apart from the figure gone."""
    out = G.complete_outline(can, color=OUTLINE)[0]
    op = out[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for i in range(1, n + 1):
        m = lbl == i
        if m.sum() > 2:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool)) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for i in range(1, n + 1):
            if sz[i - 1] < 6:
                out[lbl == i] = 0
    return out


# ------------------------------------------------------------------------------------------------- the 3/4 design
FRONT_SKIRT = (35, 38, 37, 51)                # idle.png: the skirt (rows, columns) and everything from row 39 on (the
FRONT_LEGS = 39                               # legs; the hands hang to row 38) stay while she breathes


def front(kit, sink=0, wx=0, lift=0, mane=0, flash=False, mirror=False):
    """The 3/4 design: above the waist (the head, the bust, both arms) set down `sink` rows onto the skirt and the
    legs, which stay; the mane's tail swayed."""
    F = kit.front
    yy, xx = np.mgrid[:F.shape[0], :F.shape[1]]
    op = F[..., 3] > 0
    r0, r1, c0, c1 = FRONT_SKIRT
    low = op & (((yy >= r0) & (yy <= r1) & (xx >= c0) & (xx <= c1)) | (yy >= FRONT_LEGS))
    up = np.where((op & ~low)[..., None], F, 0).astype(np.uint8)
    up = np.roll(sway(up, mane, attach=30), sink, 0)
    can = kit.canvas()
    x0, y0 = kit.front_at
    kit.put(can, np.where(low[..., None], F, 0).astype(np.uint8), (x0 + wx, y0 - lift))
    kit.put(can, up, (x0 + wx, y0 - lift))
    can = finish(can)
    if mirror:
        can = mirrored(kit, can)
    return R.flash(can) if flash else can


# ------------------------------------------------------------------------------------------------- the actions
def stand(**kw):
    """The side stance with both feet planted on their design spots (IK when the hips move)."""
    p = Pose(n_leg=("ik", N_ANKLE[0], GROUND), f_leg=("ik", F_ANKLE[0], GROUND))
    p.update(kw)
    return p


def air(**kw):
    """Both feet off the ground: the legs hanging (thigh, shin headings), the toes pointed a little."""
    p = Pose(n_leg=("ang", -92, -100, -20), f_leg=("ang", -88, -96, -20))
    p.update(kw)
    return p


STRAIGHT = dict(n_leg=("ang", -92, -95, -30), f_leg=("ang", -88, -92, -30), n_arm=(-100, -95),
                f_arm=(-80, -85))             # a somersault laid out straight, the arms along her (League's E)
BACK_SINK = 20                                # lying on her back: rows of her (the mane under her) the ground hides
TUCK = dict(n_leg=("ang", 25, -95), f_leg=("ang", 15, -105), n_arm=(-20, -70), f_arm=(-10, -60), lean=0.25,
            head=(1, 1))                      # knees to the chest, the arms round them: the somersault's ball


def frames_of(rows, ms):
    if isinstance(ms, int):
        ms = [ms] * len(rows)
    assert len(rows) == len(ms), (len(rows), len(ms))
    return [(p, m) for p, m in zip(rows, ms)]


# ms per frame: each tag's length and release frame are the kit's (tools/kit/build_zoe.py P, 60 ticks a second)
RUN_PHASES = [(3.5, GROUND), (1.0, GROUND), (-2.0, GROUND), (-4.0, GROUND - 1.5), (-3.5, GROUND - 3.5),
              (0.0, GROUND - 4.0), (3.0, GROUND - 3.5), (4.0, GROUND - 1.5)]
RUN_DY = [1, 2, 1, 0, 1, 2, 1, 0]
RUN_LIFT = [0, 0, 1, 2, 0, 0, 1, 2]
RUN_MANE = [0, 1, 1, 0, 0, 1, 1, 0]


def run_poses():
    """League's Zoe_Run1, a bouncy skipping run (league_caitlyn's way): each leg's ankle in eight phases from its hip,
    the knee solved, the far leg four phases on; the body a row down as a foot lands and off the ground as one foot
    leaves and the other has not landed (the skip); leaning a little; the arms swinging against the legs; the mane's
    tail bouncing a beat behind."""
    out = []
    for i in range(8):
        sw = math.cos(2 * math.pi * i / 8)
        p = Pose(dy=RUN_DY[i], lift=RUN_LIFT[i], lean=0.15, mane=RUN_MANE[i])
        for side, ph, hip in (("n", i, N_HIP), ("f", (i + 4) % 8, F_HIP)):
            ax, ay = RUN_PHASES[ph]
            p[side + "_leg"] = ("ik", hip[0] + ax, ay, -15 if ay < GROUND else 0)
        p["n_arm"] = (-112 - 35 * sw, -95 - 35 * sw)
        p["f_arm"] = (-75 + 35 * sw, -60 + 35 * sw)
        out.append(p)
    return frames_of(out, 100)


def attack_poses():
    """League's Zoe_attack1: a crouch, a spring up with the near arm drawn back, the flick that sends the star (frame 4,
    the kit's a_rel 10 = 167 ms), a forward somersault (quarter turns), landing."""
    rows = [
        stand(dy=2, lean=0.15, n_arm=(-150, -140), f_arm=(-60, -40)),
        air(lift=3, lean=-0.05, n_arm=(165, 150), f_arm=(-70, -50)),
        air(lift=5, lean=-0.1, head=(-1, 0), n_arm=(140, 175), f_arm=(-60, -30)),
        air(lift=6, lean=0.2, n_arm=(5, 0), f_arm=(-110, -120), head=(1, 0)),
        Pose(TUCK, flip=1, at=(4, 9)),
        Pose(TUCK, flip=2, at=(5, 10)),
        Pose(TUCK, flip=3, at=(5, 6)),
        stand(dy=2, lean=0.2, n_arm=(-160, -170), f_arm=(-20, -10)),
    ]
    return frames_of(rows, [55, 55, 57, 60, 55, 55, 55, 58])


def idle_poses():
    """League's Zoe_Idle1: she stands bobbing lightly, her mane waving: the 3/4 design's body above the waist sets down
    a row onto its skirt and legs (which stay: memory rig-deformation-checks), the mane's tail rising and falling."""
    sink = [0, 0, 1, 1, 1, 1, 0, 0]
    mane = [0, -1, -1, 0, 1, 1, 1, 0]
    return [(lambda kit, s=s, m=m: front(kit, sink=s, mane=m), 150) for s, m in zip(sink, mane)]


def attack_p_poses():
    """More Sparkles! (League's Zoe_Empowered_Attack), played from the attack's tick 9 when the star leaves: up high
    with both arms flung up in a V (the throw), spreading them, coming down, landing in a crouch, up again."""
    rows = [
        air(lift=8, lean=-0.1, head=(-1, -1), n_arm=(165, 155), f_arm=(25, 30)),
        air(lift=9, lean=-0.1, head=(-1, -1), n_arm=(170, 160), f_arm=(20, 25)),
        air(lift=8, n_arm=(170, 175), f_arm=(10, 5)),
        air(lift=6, lean=0.1, n_arm=(-155, -150), f_arm=(-25, -30), n_leg=("ang", -60, -110, -20)),
        air(lift=3, lean=0.15, n_arm=(-140, -130), f_arm=(-40, -50)),
        stand(dy=3, lean=0.25, head=(1, 1), n_arm=(-150, -140), f_arm=(-30, -40)),
        stand(dy=2, lean=0.15, n_arm=(-130, -125), f_arm=(-55, -60)),
        stand(),
    ]
    return frames_of(rows, [55, 55, 55, 55, 55, 60, 60, 55])


def skill_poses():
    """Q Paddle Star (League's Spell1_base): she floats up straight, arms down, the near arm swinging back, throws
    (frame 4, the kit's q_rel 13 = 217 ms), tucks and turns a forward somersault, lands."""
    rows = [
        air(lift=2, n_arm=(-115, -110), f_arm=(-70, -75)),
        air(lift=5, n_arm=(-140, -150), f_arm=(-60, -60)),
        air(lift=7, lean=-0.1, head=(-1, 0), n_arm=(160, 175), f_arm=(-50, -40)),
        air(lift=8, lean=0.2, head=(1, 0), n_arm=(10, 5), f_arm=(-120, -130)),
        Pose(TUCK, flip=1, at=(4, 10)),
        Pose(TUCK, flip=2, at=(5, 10)),
        Pose(TUCK, flip=3, at=(5, 6)),
        stand(dy=2, lean=0.2, n_arm=(-160, -170), f_arm=(-20, -10)),
    ]
    return frames_of(rows, [70, 70, 77, 55, 55, 55, 55, 63])


KICK = dict(lean=-0.25, head=(-1, 0), n_leg=("kick", 8, 10.5, 90), f_leg=("ang", -110, -170), n_arm=(172, 165),
            f_arm=(20, 10))                   # the flying kick: the near leg shot out forward, the sole to the bubble


def skill2_poses():
    """E Sleepy Trouble Bubble (League's Zoe_Spell3): a crouch, up straight, a quick somersault, the flying kick that
    sends the bubble (frame 6, the kit's e_rel 13 = 217 ms), the kick held as she comes down, landing."""
    rows = [
        stand(dy=2, lean=0.1, n_arm=(-140, -135), f_arm=(-50, -60)),
        air(lift=5, n_arm=(-120, -115), f_arm=(-65, -70)),
        Pose(STRAIGHT, flip=1, at=(2, 10)),
        Pose(STRAIGHT, flip=2, at=(3, 10)),
        Pose(STRAIGHT, flip=3, at=(4, 10)),
        Pose(KICK, lift=8, wx=2),
        Pose(KICK, lift=6, wx=2),
        stand(dy=3, wx=1, lean=-0.1, n_arm=(-150, -150), f_arm=(-40, -30)),
        stand(dy=1),
    ]
    return frames_of(rows, [50, 50, 40, 40, 37, 60, 60, 60, 53])


def ult_poses():
    """R Portal Jump (League's Zoe_spell4_enter): a crouch, the spring with the arms up, the leap (frame 3, the kit's
    r_rel 8 = 133 ms: the portal opens and she is away), diving head first into it, then out at the far end: down,
    landing, standing."""
    reach = dict(n_arm=(-95, -95), f_arm=(-85, -85))
    rows = [
        stand(dy=3, lean=0.2, n_arm=(-150, -150), f_arm=(-40, -40)),
        air(lift=8, lean=-0.05, **reach),
        air(lift=18, n_leg=("ang", -95, -98, -40), f_leg=("ang", -92, -95, -40), **reach),
        Pose(air(**reach), flip=1, at=(6, 16)),
        Pose(air(**reach), flip=2, at=(8, 6)),
        air(lift=10, n_arm=(170, 160), f_arm=(15, 20)),
        stand(dy=3, lean=0.2, n_arm=(-160, -160), f_arm=(-20, -20)),
        stand(dy=1, n_arm=(-150, -150), f_arm=(-40, -40)),
    ]
    return frames_of(rows, [66, 67, 55, 55, 55, 52, 50, 50])


def skill_w_poses():
    """W Spell Thief's missiles (League's Zoe_spell2_missile): a quick spin - the side, the 3/4 front, the mirrored side,
    the front - and out of it the arms flung wide as the three missiles leave (frames 3, 5 and 7 start at the kit's
    w_rel 4 and w_gap 5: 67, 150 and 233 ms)."""
    wide = dict(n_arm=(165, 170), f_arm=(15, 10))
    rows = [
        stand(dy=1, n_arm=(-100, -80), f_arm=(-80, -60)),
        lambda kit: front(kit, lift=2, mane=-1),
        Pose(air(lift=3, n_arm=(-100, -80)), mirror=True),
        lambda kit: front(kit, lift=3, mane=1, mirror=True),
        air(lift=4, **wide),
        air(lift=5, mane=1, **wide),
        air(lift=4, mane=1, **wide),
    ]
    return frames_of(rows, [35, 32, 40, 43, 40, 43, 84])


def ult_exit_poses():
    """Leaving the far end (League's Zoe_Spell4_Exit): a crouch, and straight up out of sight."""
    up = dict(n_arm=(-95, -95), f_arm=(-85, -85), n_leg=("ang", -95, -98, -40), f_leg=("ang", -92, -95, -40))
    rows = [stand(dy=3, lean=0.15, n_arm=(-150, -150), f_arm=(-40, -40)), Pose(up, lift=8), Pose(up, lift=18),
            Pose(up, lift=30)]
    return frames_of(rows, [50, 50, 50, 50])


def ult_back_poses():
    """Back through the portal (League's Zoe_Spell4_B): dropping in from above, landing in a crouch, standing."""
    down = dict(n_arm=(170, 160), f_arm=(15, 20))
    rows = [air(lift=20, **down), air(lift=10, **down), air(lift=3, **down),
            stand(dy=3, lean=0.2, n_arm=(-160, -160), f_arm=(-20, -20)), stand(dy=1),
            lambda kit: front(kit)]
    return frames_of(rows, [50, 50, 50, 50, 50, 50])


def hit_poses():
    return [(lambda kit: R.flash(compose(kit, Pose(wx=-2))), 100), (Pose(wx=-1), 100)]


def dead_poses():
    """The death (League's Zoe_Death): hit, a spin (the 3/4 front, the mirrored side, the front), the arms flung out,
    stumbling back, falling on her back, legs up, then lying still."""
    rows = [
        stand(dy=2, lean=0.25, head=(1, 1), n_arm=(-80, -60), f_arm=(-100, -80)),
        lambda kit: front(kit, mane=-1),
        Pose(stand(n_arm=(-150, -140)), mirror=True),
        lambda kit: front(kit, mane=1, mirror=True),
        stand(wx=-1, lean=-0.15, head=(-1, -1), n_arm=(150, 160), f_arm=(40, 30)),
        stand(wx=-2, dy=1, lean=-0.3, head=(-2, 0), n_arm=(130, 140), f_arm=(60, 50)),
        Pose(n_leg=("ang", -60, -80), f_leg=("ang", -50, -70), n_arm=(-160, -150), f_arm=(-20, -10), lie=3,
             sink=BACK_SINK - 6, at=(-6, 0)),
        Pose(n_leg=("ang", 10, 40), f_leg=("ang", 20, 50), n_arm=(-170, -160), f_arm=(-10, 0), lie=3, sink=BACK_SINK,
             at=(-8, 0)),
        Pose(n_leg=("ang", -60, -40), f_leg=("ang", -50, -30), n_arm=(-160, -170), f_arm=(-20, -10), lie=3,
             sink=BACK_SINK, at=(-8, 0)),
        Pose(n_leg=("ang", -85, -85), f_leg=("ang", -80, -80), n_arm=(-150, -160), f_arm=(-30, -20), lie=3,
             sink=BACK_SINK, at=(-8, 0)),
    ]
    return frames_of(rows, [100, 100, 100, 100, 110, 110, 110, 110, 120, 240])


TAGS = ["idle", "run", "attack", "attack_p", "skill", "skill2", "ult", "skill_w", "ult_exit", "ult_back", "hit", "dead"]


def build(kit, tags=None):
    """{tag: [(canvas, ms)]} for the tags written so far."""
    out = {}
    for tag in tags or TAGS:
        fn = globals().get(tag + "_poses")
        if fn is None:
            continue
        out[tag] = [(compose(kit, p) if isinstance(p, Pose) else p(kit), ms) for p, ms in fn()]
    return out


# ------------------------------------------------------------------------------------------------- review
# tag -> (League's clip, its ms for each of our frames) - the beat each frame stands for
LOL = {
    "run": ("Zoe_Run1", [0, 83, 167, 250, 333, 417, 500, 583]),
    "attack": ("Zoe_attack1", [0, 67, 133, 233, 300, 350, 420, 750]),
    "idle": ("Zoe_Idle1", [0, 550, 1100, 1650, 2200, 2750, 3300, 3850]),
    "attack_p": ("Zoe_Empowered_Attack", [150, 225, 300, 375, 450, 525, 600, 750]),
    "skill": ("Spell1_base", [60, 120, 190, 250, 317, 380, 440, 700]),
    "skill2": ("Zoe_Spell3", [0, 175, 260, 292, 350, 467, 560, 640, 690]),
    "ult": ("Zoe_spell4_enter", [0, 69, 138, 346, 415, 484, 560, 700]),
    "skill_w": ("Zoe_spell2_missile", [0, 42, 83, 125, 208, 300, 417]),
    "ult_exit": ("Zoe_Spell4_Exit", [0, 50, 100, 150]),
    "ult_back": ("Zoe_Spell4_B", [67, 133, 200, 300, 500, 760]),
    "dead": ("Zoe_Death", [0, 200, 400, 600, 1000, 1200, 1400, 1600, 1900, 2300]),
}
LOL_ARGS = ["--champ", "Zoe", "--mirror", "--yaw", "15", "--head", "2.0", "--legs", "0.8", "--hair", "0.6",
            "--hide-submesh", "Zoe_Base_Jumprope_Mat", "--hide-submesh", "Zoe_Base_TennisRac_Mat",
            "--hide-submesh", "Zoe_Base_Yoyo_Mat", "--hide-submesh", "Zoe_Base_IceCream_Mat"]


def lol_strip(tag, size=220):
    """League's frames for a tag (pose_ref.py at those times; Riot's model: local only), cached in TMP."""
    clip, times = LOL[tag]
    out = os.path.join(TMP, "lol_at")
    name = f"{tag}_{'_'.join(map(str, times))}"
    path = os.path.join(out, name + ".png")
    if not os.path.isfile(path):
        os.makedirs(out, exist_ok=True)
        cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), *LOL_ARGS, "--anim", clip,
               "--times", ",".join(map(str, times)), "--size", str(size), "--no-labels", "--bg", "232,232,232",
               "--out", out]
        subprocess.run(cmd, check=True, capture_output=True)
        os.replace(os.path.join(out, clip + ".png"), path)
    strip = Image.open(path).convert("RGB")
    w = strip.width // len(times)
    return [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(len(times))]


def tile(kit, can, z, box=(-45, -88, 45, 4), bg=(92, 98, 86)):
    """The canvas round the standing point: box = (left, top, right, bottom) squares from the point / the ground row."""
    x0, y0, x1, y1 = box
    c = can[kit.GY + y0:kit.GY + y1, kit.CX + x0:kit.CX + x1]
    out = np.zeros(c.shape, np.uint8)
    out[...] = (*bg, 255)
    m = c[..., 3] > 0
    out[m] = c[m]
    return Image.fromarray(out).resize((c.shape[1] * z, c.shape[0] * z), Image.NEAREST).convert("RGB")


def compare(kit, acts, tag, path, z=3):
    """League's frames over ours, one column a frame."""
    ours = [tile(kit, c, z) for c, _ in acts[tag]]
    w, h = ours[0].size
    lol = lol_strip(tag) if tag in LOL else []
    lol = [im.resize((int(im.width * h / im.height), h)) for im in lol]
    lw = lol[0].width if lol else 0
    sheet = Image.new("RGB", (len(ours) * (max(w, lw) + 4), 2 * h + 4), (34, 34, 34))
    for i, im in enumerate(ours):
        if lol:
            sheet.paste(lol[i], (i * (max(w, lw) + 4), 0))
        sheet.paste(im, (i * (max(w, lw) + 4), h + 4))
    sheet.save(lp(path))


NAMES = {"idle": "待机", "run": "跑步", "attack": "普攻", "attack_p": "普攻（烟火四射！强化）", "skill": "Q 飞星乱入",
         "skill2": "E 催眠气泡", "ult": "R 折返跃迁", "skill_w": "W 窃法巧手（飞弹）", "ult_exit": "R 从远端跳走",
         "ult_back": "R 回到原地", "hit": "受击", "dead": "死亡"}


def review(kit, acts, out_dir, z=3):
    """Every tag next to League's clip (League left, ours right; hit ours only), played twice with its name over it,
    in one GIF (memory one-gif-review); and one PNG sheet per tag (League over ours)."""
    os.makedirs(out_dir, exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
    frames, durs = [], []
    for tag, frs in acts.items():
        compare(kit, acts, tag, os.path.join(out_dir, f"zoe_{tag}.png"), z=z)
        ours = [tile(kit, c, z) for c, _ in frs]
        w, h = ours[0].size
        lol = lol_strip(tag) if tag in LOL else None
        if lol:
            lol = [im.resize((int(im.width * h / im.height), h)) for im in lol]
        lw = lol[0].width if lol else w
        for rep in range(2):
            for i, (im, (_, ms)) in enumerate(zip(ours, frs)):
                f = Image.new("RGB", (lw + w + 8, h + 30), (34, 34, 34))
                if lol:
                    f.paste(lol[i], (0, 30))
                f.paste(im, (lw + 8, 30))
                d = ImageDraw.Draw(f)
                d.text((8, 4), f"{NAMES.get(tag, tag)}  {i + 1}/{len(frs)}", fill=(255, 240, 160), font=font)
                frames.append(f.quantize(255, dither=Image.Dither.NONE))
                durs.append(max(20, int(ms)))
    frames[0].save(os.path.join(out_dir, "zoe_actions_vs_lol.gif"), save_all=True, append_images=frames[1:],
                   duration=durs, loop=0)
    print("review ->", out_dir)


def audit(kit, acts):
    """Per frame: pieces, enclosed gaps (sizes), squares under the ground, area against the stance."""
    base = (compose(kit, Pose())[..., 3] > 0).sum()
    rows = []
    for tag, frs in acts.items():
        for i, (can, _) in enumerate(frs):
            op = can[..., 3] > 0
            _, n = ndimage.label(op, structure=np.ones((3, 3), bool))
            gaps = [len(h) for h in RK.holes(can)]
            rows.append(f"{tag:9s} {i + 1:2d} pieces {n} gaps {gaps} under {int(op[kit.GY:].sum())} "
                        f"area {op.sum() / base:.2f}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", help="the side design's parts tinted at 12x, here")
    ap.add_argument("--review", help="the comparison GIF and sheets here (nothing written to the repo)")
    ap.add_argument("--audit", action="store_true")
    a = ap.parse_args()
    kit = Kit()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        tint(kit).save(os.path.join(a.parts, "zoe_parts.png"))
        return
    acts = build(kit)
    if a.audit:
        print("\n".join(audit(kit, acts)))
        return
    if a.review:
        review(kit, acts, a.review)
        return
    kit.rig.export(acts)


def form():
    """The kit (the old rig's name, for tools/art/review_zoe_actions.py and preview_zoe.py)."""
    return Kit()


def frames(kit):
    return build(kit)


if __name__ == "__main__":
    main()

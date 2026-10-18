#!/usr/bin/env python3
"""league_wukong's action frames posed from the approved design's own squares (the user, 2026-10-18: 「动作帧你按照塔姆
那种方式做吧 做到完美了喊我review 你还要自我review后确定没问题」).

    python tools/art/rig_wukong.py --parts DIR       # the design with its parts tinted + pose tries (12x)
    python tools/art/rig_wukong.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_wukong.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_wukong.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design: Codex's step-1 take A-1 read back on its own 11.5 px grid and brought to 57 rows hair tip to soles by whole
rows / columns (tools/art/design_wukong_cut.py; the user: 「太模糊了 起码PPU1.5」 -> PPU 1.5, 38 game rows), 77 x 69
squares: the tail's tip row 0, the hair tip row 12, the soles row 68; the eyes put back by hand (EYES: the cut kept one
green square of each). Every pose is lossless (memory no-deformation-lossless-poses): parts cut square by square from
the design and only moved by whole squares, quarter turns about half-integer pivots and mirror images; nothing is drawn
again at another angle.
Parts (a material map of the design first, Maokai's lesson): the staff (a straight 3-square diagonal from its top cap at
row 17 to its foot at row 68, behind the near hand), the near arm (the gold-and-red guard and the furry hand gripping the
staff, image left), the far arm (its guard with the monkey-head ornament and the open furry hand, image right), the tail
(rising behind him), the near lower leg (the brown shin and the purple shoe, under the robe's flap) and the far lower leg
(the steel knee guard, the shin and the shoe); the rest is the body (the head, the scarf, the chest plate, the tabard and
the robe skirt).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "wukong"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "wukong", "hd")
P = 60                                          # padding round a design-sized layer


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign:
    """What ppu_rig.Rig needs of a design: the squares, the standing point, the outline colour."""
    TURN_PAD = P

    def __init__(self, d, px):
        self.hero, self.ppu = HERO, PPU
        self.d = d
        self.d0 = d.copy()
        self.H, self.W = d.shape[:2]
        ys, xs = np.nonzero(d[..., 3])
        self.ground = ys.max() + 1
        self.px = px
        self.outline = PD.edge_colour(d)
        self.parts, self.order, self.props = {}, [], set()

    def box(self, y0, y1, x0, x1):
        m = np.zeros((self.H, self.W), bool)
        m[max(0, y0):y1 + 1, max(0, x0):min(self.W, x1 + 1)] = True
        return m & (self.d[..., 3] > 0)

    def rows(self, spans):
        m = np.zeros((self.H, self.W), bool)
        for y, (x0, x1) in spans.items():
            m[y, max(0, x0):min(self.W, x1 + 1)] = True
        return m & (self.d[..., 3] > 0)

    def part(self, name, m):
        for k in self.parts:
            self.parts[k] &= ~m
        self.parts[name] = m.copy()
        if name not in self.order:
            self.order.append(name)

    def rest(self):
        m = self.d[..., 3] > 0
        for v in self.parts.values():
            m &= ~v
        return m

    def layer(self, name, m=None):
        m = (self.parts[name] if name != "rest" else self.rest()) if m is None else m
        out = np.zeros_like(self.d)
        out[m] = self.d[m]
        return out


def pad(a):
    out = np.zeros((a.shape[0] + 2 * P, a.shape[1] + 2 * P, 4), np.uint8)
    out[P:P + a.shape[0], P:P + a.shape[1]] = a
    return out


def spans(table):
    out = {}
    for rows, cols in table:
        for y in rows:
            out[y] = cols
    return out


# ------------------------------------------------------------------------------------------------- the design's parts
# the eyes (the cut kept one green square of each): League's green eyes, two squares each with the white highlight beside
EYES = {(28, 41): (58, 192, 5), (28, 42): (58, 192, 5)}
FUR = [(106, 41, 29), (148, 62, 46), (74, 26, 15), (175, 77, 52), (102, 40, 10), (129, 57, 8), (156, 79, 9),
       (200, 104, 58), (62, 41, 20)]
STAFF_TOP, STAFF_FOOT = (12.5, 17.0), (2.5, 68.0)     # (x, y) of the staff's axis ends
GRIP = (7.5, 44.5)                                    # the near hand's middle: the staff turns about it
NEAR_SHOULDER = (27.5, 33.5)
FAR_SHOULDER = (55.5, 27.5)
STAND = 44                                            # the column between the shoes: the standing point
STEEL = [(189, 201, 216), (135, 144, 164), (90, 98, 120), (54, 54, 70)]
ROBE = [(69, 10, 42), (106, 22, 64), (36, 6, 15)]
RED = [(244, 31, 15), (108, 3, 10), (187, 8, 13), (137, 7, 10)]
TAIL_HINGE = 16                                       # the tail swings above this row (its root stays behind him)
# The staff's steel middle (rows STEEL_ROWS) as the cut left it was 3-5 squares wide row to row and hidden under the hand
# (rows 39-45): turned level and slid out of the hand it showed a broken, ragged shaft (the user: 「武器有点变形吧」).
# It is laid again from the cut's own cleanest steel row (row 37: outline, dark, mid, light, dark, outline) along the
# shaft's line - its left outline from column 6 at row 31 to column 3 at row 50 - the gold-banded ends kept as drawn.
STEEL_ROWS = (31, 50)
STEEL_X = (6, 3)                                      # left outline column at the first / last steel row
STEEL_PAT = [None, (90, 98, 120), (135, 144, 164), (189, 201, 216), (90, 98, 120), None]   # None = the outline


def classes(d, cols):
    m = np.zeros(d.shape[:2], bool)
    for c in cols:
        m |= np.all(d[..., :3] == c, axis=-1)
    return m & (d[..., 3] > 0)


def staff_mask(D):
    """The staff: the squares within 4.2 of its axis left of column 17 (its gold bands and outline stick out of the
    3-square shaft), not the near hand's fur (rows 38-49) nor the outline squares touching it (the hand keeps its outline), not the
    near bracer beside it (rows 32-47 right of the shaft)."""
    (x0, y0), (x1, y1) = STAFF_TOP, STAFF_FOOT
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    t = np.clip(((xx + .5 - x0) * (x1 - x0) + (yy + .5 - y0) * (y1 - y0)) / ((x1 - x0) ** 2 + (y1 - y0) ** 2), 0, 1)
    dist = np.hypot(xx + .5 - (x0 + t * (x1 - x0)), yy + .5 - (y0 + t * (y1 - y0)))
    fur = classes(D.d, FUR) & D.box(38, 49, 0, 13)       # the hand (the staff's bands share its browns)
    dark = classes(D.d, [tuple(D.outline)])
    hand_rim = dark & ndimage.binary_dilation(fur, structure=R.CROSS)
    bracer = D.box(34, 47, 11, 16) | D.box(32, 33, 13, 16)
    return D.box(15, D.H - 1, 0, 16) & (dist <= 4.2) & ~fur & ~hand_rim & ~bracer


def design():
    d = load("design.png")
    for (y, x), rgb in EYES.items():
        d[y, x] = (*rgb, 255)
    D = CutDesign(d, px=STAND)
    D.part("tail", D.box(0, 16, 17, 29) | D.box(17, 28, 17, 26))
    D.part("staff", staff_mask(D))
    D.part("near_arm", D.box(29, 49, 0, 27) & ~D.parts["staff"])
    D.part("far_arm", D.box(21, 40, 54, 76) | D.box(41, 49, 60, 76))
    # the lower legs from a material map of rows 44-68 (2026-10-18; the first cut left the near knee guard on the body,
    # so the shin moved away from its own knee: 「腿部也有变形的」): near - the fur above the knee, the steel knee guard
    # with its gold rim (rows 52-60, columns 26-33), the shin going down-left and the purple shoe; far - the knee guard
    # (rows 46-51), the fur under it, the shin going down-right and the shoe. The robe's purple and red stay on the body
    near = D.rows(spans([((52,), (26, 32)), ((53, 54), (26, 33)), ((55,), (22, 33)), ((56, 57), (20, 33)),
                         ((58,), (16, 33)), ((59, 60), (15, 32)), (range(61, 69), (12, 27))]))
    robe = classes(d, ROBE + RED) & D.box(52, 55, 0, D.W - 1)
    D.part("near_leg", near & ~robe)
    D.part("far_leg", D.rows(spans([((46,), (55, 59)), ((47,), (55, 60)), (range(48, 52), (54, 61)), ((52,), (55, 61)),
                                    ((53, 54), (54, 61)), ((55,), (55, 61)), ((56,), (57, 62)), ((57,), (58, 64)),
                                    ((58, 59), (59, 65)), ((60,), (58, 65)), (range(61, 69), (57, 76))])))
    D.part("body", D.rest())
    return D


TINT = {"tail": (255, 0, 255), "staff": (255, 60, 60), "near_arm": (60, 120, 255), "far_arm": (0, 220, 120),
        "near_leg": (255, 220, 0), "far_leg": (0, 220, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def vflip(layer, row):
    """A padded layer mirrored top to bottom about design row `row`."""
    y = P + row
    out = np.zeros_like(layer)
    for i in range(layer.shape[0]):
        j = 2 * y - i
        if 0 <= j < layer.shape[0]:
            out[j] = layer[i]
    return out


def mirror(rig, can, col=None):
    """The whole frame mirrored left to right about the standing point (his back to the front: a spin's half turn)."""
    x = rig.CX if col is None else col
    out = np.zeros_like(can)
    for i in range(can.shape[1]):
        j = 2 * x - i
        if 0 <= j < can.shape[1]:
            out[:, j] = can[:, i]
    return out


class Form:
    """The design's layers; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self._staff = {}
        self.ref_holes = None

    def pose(self, crouch=0, whole=(0, 0), near=(0, 0), near_rot=0, staff=None, staff_rot=0, ext=0, far=(0, 0),
             far_rot=0, tail=(0, 0), sway=0, legs=None, leg_layers=None, no_staff=False, fill=True):
        """crouch: rows the body (with the arms, the staff and the tail) sets down onto the lower legs; whole: the whole
        figure; near: the near arm moved (dx, dy), near_rot quarter turns counter-clockwise about NEAR_SHOULDER; staff:
        the staff moved (default = near), staff_rot quarter turns counter-clockwise about GRIP (3: its top points
        forward); far: the far arm moved, far_rot quarter turns about FAR_SHOULDER; tail: the tail moved; legs:
        ((near dx, dy), (far dx, dy)); ext: steel squares added to the staff's middle in front of the hand (its magic
        lengthening, League's Crushing Blow and Cyclone; flat staffs only); sway: columns the tail's tip swings."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        staff = near if staff is None else staff
        legs_l = leg_layers if leg_layers is not None else [(L["far_leg"], dict(dx=wx + flx, dy=wy + fly)),
                                                             (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly))]
        staff_l = self.staff(staff_rot, ext)
        layers = [(self.tail(sway), dict(dx=ux + tail[0], dy=uy + tail[1])),
                  (L["far_arm"], dict(dx=ux + far[0], dy=uy + far[1], rot=far_rot, about=FAR_SHOULDER)),
                  *legs_l, (L["body"], dict(dx=ux, dy=uy)),
                  *([] if no_staff else [(staff_l, dict(dx=ux + staff[0], dy=uy + staff[1]))]),
                  (L["near_arm"], dict(dx=ux + near[0], dy=uy + near[1], rot=near_rot, about=NEAR_SHOULDER))]
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    def staff(self, rot, ext=0):
        """The staff layer (its drawn ends and the steel middle laid square by square, STEEL_*), ext steel rows longer
        above the hand (the top end moved out along the shaft's line: League's extending staff), then turned rot
        quarter turns counter-clockwise about GRIP (lossless; 3: the top points forward)."""
        key = (rot % 4, ext)
        if key in self._staff:
            return self._staff[key]
        D = self.D
        (r0, r1), (x0, x1) = STEEL_ROWS, STEEL_X
        xl = lambda y: int(round(x0 + (x1 - x0) * (y - r0) / (r1 - r0)))
        src = np.zeros_like(self.L["staff"])
        keep = D.parts["staff"].copy()
        keep[r0:r1 + 1] = False
        top, bot = keep.copy(), keep.copy()
        top[r0:] = False
        bot[:r1 + 1] = False
        dx_top = xl(r0 - ext) - xl(r0)
        for m, dy, dx in ((top, -ext, dx_top), (bot, 0, 0)):
            ys, xs = np.nonzero(m)
            src[ys + P + dy, xs + P + dx] = D.d[ys, xs]
        outline = (*D.outline, 255)
        for y in range(r0 - ext, r1 + 1):
            for i, c in enumerate(STEEL_PAT):
                src[y + P, xl(y) + i + P] = outline if c is None else (*c, 255)
        lay = np.zeros_like(src)
        R.put(lay, src, rot=rot, about=(GRIP[0] + P, GRIP[1] + P))
        self._staff[key] = lay
        return lay

    def tail(self, k):
        """The tail with its upper rows moved whole: the tip (row 0) k columns, nothing from row TAIL_HINGE down."""
        if not k:
            return self.L["tail"]
        out = np.zeros_like(self.L["tail"])
        for y in range(out.shape[0]):
            d = int(round(k * max(0, TAIL_HINGE - (y - P)) / TAIL_HINGE))
            row = self.L["tail"][y]
            if d > 0:
                out[y, d:] = row[:-d]
            elif d < 0:
                out[y, :d] = row[-d:]
            else:
                out[y] = row
        return out

    MOST = 10

    def close_holes(self, can):
        """Small enclosed holes the idle does not have filled from the squares round them (rig_jarvaniv's way)."""
        if self.ref_holes is None:
            idle = self.pose(fill=False)
            op = idle[..., 3] > 0
            self.ref_holes = ndimage.binary_dilation(ndimage.binary_fill_holes(op) & ~op, iterations=2)
        op = can[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op & ~self.ref_holes
        lbl, n = ndimage.label(holes)
        fill = np.zeros_like(holes)
        for k in range(1, n + 1):
            m = lbl == k
            if m.sum() <= self.MOST:
                fill |= m
        if not fill.any():
            return can
        out = R.fill_under(can, fill)
        left = fill & (out[..., 3] == 0)
        if left.any():
            src = (out[..., 3] > 0) & (out[..., :3].astype(int).sum(-1) >= 70)
            _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
            out[left] = out[iy[left], ix[left]]
        return out


def form():
    return Form(design(), rig_pad=(40, 50, 40, 20))


def sheet(cans, path, z=4):
    allc = np.stack(cans)
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
    tiles = []
    for c in cans:
        bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
        bg.alpha_composite(Image.fromarray(c[y0:y1, x0:x1]))
        tiles.append(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
    out = Image.new("RGB", (sum(t.width + 6 for t in tiles), tiles[0].height), (40, 40, 40))
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + 6
    out.save(lp(path))


def tries(F):
    p = F.pose
    return [p(), p(**flat()), p(**flat(ext=12)), p(staff_rot=1), p(staff_rot=2),
            p(near=(0, -4)), p(sway=2), mirror(F.rig, p(**flat(ext=8)))]


# ------------------------------------------------------------------------------------------------- the actions
# A flat staff (staff_rot 3: its top points forward) slid along itself so the hand holds its foot end and it reaches
# out in front of him (turned about the hand alone, its longer half went into the body and its foot out behind him)
FWD = 20


def flat(dx=FWD, dy=0, ext=0):
    return dict(staff_rot=3, staff=(dx, dy), ext=ext)


# ms per frame; the kit's ticks (tools/kit/build_wukong.py) come from these
MS = {"idle": [150] * 8, "run": [100] * 8, "attack": [80, 90, 100, 110, 80], "q_attack": [80, 90, 110, 100, 60],
      "skill": [60, 80, 80, 80], "skill2": [60, 70, 70], "spin": [60, 60, 60, 60], "ult": [50],
      "hit": [100, 100], "dead": [100, 110, 120, 150, 200, 500]}


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    # idle: the body sets down a row onto the lower legs and rises, the tail's tip swinging a column after it
    out["idle"] = [p(crouch=c, sway=k) for c, k in zip([0, 0, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 0, -1, -1, -1])]
    # auto attack (League's MonkeyKing_attack1: the staff raised high, then swung down to lie level in front of him):
    # the near arm raised 4 rows with the staff slid up in the hand; the swing - the staff level across his front (frame
    # 3, the hit), stepping in a column and low; held; back
    up = dict(near=(0, -4), staff=(0, -10))
    out["attack"] = [p(whole=(-1, 0), **up), p(near=(0, -3), **flat(dy=-3, ext=14)),
                     p(crouch=1, whole=(2, 0), near=(0, -1), **flat(dy=-1, ext=22)),
                     p(crouch=1, whole=(2, 0), near=(0, -1), **flat(dy=-1, ext=18)), p()]
    # Q Crushing Blow (League's monkeyking_spell1: the staff thrust straight out at chest height, longer): drawn back
    # level at the chest (the near arm up 5 rows), the thrust (frame 3) - the whole figure three columns in, the staff
    # lengthened 30 squares; held; back
    chest = dict(near=(0, -5))
    out["q_attack"] = [p(crouch=1, **chest, **flat(dx=8, dy=-5)),
                       p(crouch=1, whole=(1, 0), **chest, **flat(dy=-5, ext=10)),
                       p(crouch=1, whole=(3, 0), **chest, **flat(dy=-5, ext=30)),
                       p(crouch=1, whole=(3, 0), **chest, **flat(dy=-5, ext=26)), p()]
    # E Nimbus Strike (League's monkeyking_spell3: a leap at the target): crouched, up and forward with the staff
    # level in front (the cloud is the effect e_cloud), on, landing low
    out["skill"] = [p(crouch=2), p(whole=(2, -6), legs=((1, -2), (1, -2)), **flat(ext=6)),
                    p(whole=(4, -3), legs=((1, -1), (1, -1)), **flat(ext=6)), p(crouch=2, whole=(1, 0))]
    # W Warrior Trickster (League's monkeyking_spell2: he vanishes with a dash - the poof is the effect w_poof): down,
    # the dash's start low and forward, up
    out["skill2"] = [p(crouch=1), p(crouch=2, whole=(2, 0)), p(crouch=1, whole=(1, 0))]
    # R Cyclone's spin (League's monkeyking_spell4: the lengthened staff whirled level round him): the front and the
    # back (the frame mirrored about where he stands), the staff long, then short (end on to the eye), in turn
    a = p(crouch=1, **flat(dx=6, ext=30))
    b = p(crouch=1, **flat(dx=14))
    out["spin"] = [a, b, mirror(rig, a), mirror(rig, b)]
    # the ult's arming (3 ticks): the staff raised
    out["ult"] = [p(**up)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's MonkeyKing_death: a little hop and down to sit on the ground): staggering back, low, a hop,
    # then sitting - the body set down 9 rows over the lower legs, which draw in under him, the staff still in his hand
    # (its foot in the ground: nothing under the ground line). League drops the staff to lie level beside him; turned
    # level it keeps its 1:5 slant (one end up in the air), and laid flat it would have to be sheared - so he keeps it.
    def ground(can):
        out_ = can.copy()
        out_[rig.GY:] = 0
        return out_
    sit = ground(p(crouch=9, whole=(-2, 0), legs=((5, 0), (-5, 0))))
    out["dead"] = [p(whole=(-1, 0)), p(crouch=2, whole=(-2, 0)), p(whole=(-2, -3), legs=((2, -1), (-2, -1))),
                   ground(p(crouch=6, whole=(-2, 0), legs=((4, 0), (-4, 0)))), sit, sit.copy()]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# The design's own lower legs moved whole (memory codex-legs-deform) under the robe that stays on the body: each shin
# and shoe steps on its own side, planted and sliding back, then lifted and carried forward, the far one half a cycle
# later; the body set down a row on each contact and the whole figure a row up as the legs pass (league_ziggs's D walk);
# the arms never move against the body; the tail's tip swings against the step.
def _steps(stride, lifts):
    near = [round(stride * (1 - k / 4) + 1e-9) for k in range(5)]
    swing = [1, stride - 1 - (stride > 4), stride]
    dx = [v - stride // 2 for v in near + swing]
    up = [0] * 5 + list(lifts)
    return dict(near=list(zip(dx, up)), far=[(dx[(i + 4) % 8], up[(i + 4) % 8]) for i in range(8)],
                bob=[1, 0, 0, 0, 1, 0, 0, 0])


# stride 2 (the shins never more than a column off where they stand): a knee guard slid 2 columns opened a see-through
# slit between the robe's flap and the tabard
WALK_STEP = dict(_steps(2, (1, 2, 1)), rise=[0, 0, 1, 0, 0, 0, 1, 0], sway=[1, 1, 0, -1, -1, -1, 0, 1])


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    L = F.L
    for (ndx, nup), (fdx, fup), bob, up, k in zip(st["near"], st["far"], st["bob"], st["rise"], st["sway"]):
        legs = [(L["far_leg"], dict(dx=fdx, dy=-fup - up)), (L["near_leg"], dict(dx=ndx, dy=-nup - up))]
        out.append(F.pose(whole=(0, bob - up), leg_layers=legs, sway=k))
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": walk(F), **{k: v for k, v in a.items() if k != "idle"}}
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def audit(F, acts, out_dir):
    """Every frame after ppu_rig's finish(): its pieces (8-connected), new enclosed holes, colours in no design,
    outline squares with no colour beside them (rig_jarvaniv.audit); each tag at 6x."""
    from PIL import ImageDraw
    os.makedirs(lp(out_dir), exist_ok=True)
    rig = F.rig
    allowed = {tuple(c) for c in F.D.d[F.D.d[..., 3] > 0][:, :3].tolist()} | {tuple(F.D.outline)}
    idle = rig.finish(acts["idle"][0][0])
    iop = idle[..., 3] > 0
    idark = iop & (np.abs(idle[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
    base_orphan = int((idark & ~ndimage.binary_dilation(iop & ~idark, structure=R.CROSS)).sum())
    idle_holes = ndimage.binary_fill_holes(iop) & ~iop
    bad = 0
    for tag, fr in acts.items():
        tiles = []
        for i, (c, _) in enumerate(fr):
            f = rig.finish(c)
            op = f[..., 3] > 0
            lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
            sz = sorted(ndimage.sum(op, lbl, range(1, n + 1)).astype(int).tolist(), reverse=True) if n else []
            holes = ndimage.binary_fill_holes(op) & ~op
            new = holes & ~ndimage.binary_dilation(idle_holes, iterations=3)
            odd = {tuple(v) for v in f[op][:, :3].tolist()} - allowed
            dk = op & (np.abs(f[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
            orphan = dk & ~ndimage.binary_dilation(op & ~dk, structure=R.CROSS)
            pieces_ok = len(sz) == 1 or (tag == "dead" and len(sz) <= 2)
            flag = (not pieces_ok) or new.sum() or (odd and "hit" not in tag) or orphan.sum() > base_orphan
            bad += bool(flag)
            print(f"{tag:10s} {i + 1}: pieces {sz[:4]} new holes {int(new.sum())} odd colours {len(odd)} "
                  f"orphan outline {int(orphan.sum())}{'  <--' if flag else ''}")
            show = f.copy()
            if n > 1:
                big = 1 + int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1))))
                show[(lbl > 0) & (lbl != big)] = (255, 0, 0, 255)
            show[new] = (255, 0, 255, 255)
            show[orphan] = (255, 128, 0, 255)
            tiles.append(show)
        allc = np.stack(tiles)
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
        z = 6
        sheet_ = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 8), (y1 - y0) * z + 16), (40, 40, 40))
        dr = ImageDraw.Draw(sheet_)
        for i, t in enumerate(tiles):
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(t[y0:y1, x0:x1]))
            sheet_.paste(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST),
                         (i * ((x1 - x0) * z + 8), 16))
            dr.text((i * ((x1 - x0) * z + 8) + 2, 2), str(i + 1), fill=(255, 255, 0))
        sheet_.save(lp(os.path.join(out_dir, f"{HERO}_{tag}_6x.png")))
    print("frames flagged:", bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    if not (a.audit or a.review or a.parts):
        F = form()
        F.rig.export(frames(F))
        return
    if a.audit or a.review:
        F = form()
        acts = frames(F)
        if a.audit:
            audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in D.parts.items()})
    F = form()
    idle = F.pose()
    ref = F.rig.canvas()
    ref[F.rig.oy:F.rig.oy + D.H, F.rig.ox:F.rig.ox + D.W] = D.d
    print("idle vs design: squares differing", int((np.abs(idle.astype(int) - ref.astype(int)).sum(-1) > 0).sum()))
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()

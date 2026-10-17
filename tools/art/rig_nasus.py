#!/usr/bin/env python3
"""league_nasus's action frames posed from the approved designs' own squares (the user, 2026-10-17: 「动作帧按照塔姆那样
做吧 做到完美了喊我review」).

    python tools/art/rig_nasus.py --parts DIR       # the designs with their parts tinted (8x)
    python tools/art/rig_nasus.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_nasus.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_nasus.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_nasus_cut.py: Codex's step-1 takes A-1 and B-1 brought to 53 and 71 rows, PPU 1.2, by
whole rows / columns dropped, never the face's): A his normal body (72 x 53 squares, ear tips row 0, soles row 52), B
Fury of the Sands (86 x 71). Every pose is lossless (memory no-deformation-lossless-poses): parts cut square by square
from the design and only moved by whole squares, quarter turns about half-integer pivots (square centres stay
centres) and mirror images; nothing is drawn again from a picture at another angle (league_swain's arm, 「右手臂移动时候
有点变形」).
Parts (each form its own squares): the staff (spike, shaft, socket and crescent blade; the shaft's squares the near
fist, the gold front strip and the far hand hide are filled once along its line from its own visible columns, so it
is whole wherever it goes), the near arm (the gold gauntlet and the fist, from under the pauldron), the far arm (the
striped forearm and the hand at the socket, from under the collar), the upper body (head, pauldrons, chest, belt) and
the lower body (loincloth and legs). The staff turns as a whole in the eight lossless ways (as drawn: blade forward
and low; mirrored top to bottom: blade forward and high; half a turn: blade back and high; quarter turns: upright),
the arms in quarter turns about their shoulders; a crouch sets the upper body down over the loincloth (never lifted
off it). The walk is Codex's skin swap over oppi's Sion run (tools/art/pack_nasus_run.py), read back here.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "nasus"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "nasus", "hd")
P = 60                                          # padding round a design-sized layer
BROWN = {(114, 45, 28), (146, 59, 34)}          # the shaft's wood (A's palette)


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

    def mask(self, rule):
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        return rule(yy, xx) & (self.d[..., 3] > 0)

    def rows(self, spans):
        """{row: (x0, x1)} inclusive spans -> mask."""
        m = np.zeros((self.H, self.W), bool)
        for y, (x0, x1) in spans.items():
            m[y, x0:x1 + 1] = True
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

    def layer(self, name, src=None):
        m = self.parts[name] if name != "rest" else self.rest()
        out = np.zeros_like(self.d)
        out[m] = (self.d if src is None else src)[m]
        return out


def pad(a):
    """A design-sized layer padded P squares on every side (compose() reads the padding from the size)."""
    out = np.zeros((a.shape[0] + 2 * P, a.shape[1] + 2 * P, 4), np.uint8)
    out[P:P + a.shape[0], P:P + a.shape[1]] = a
    return out


# ------------------------------------------------------------------------------------------------- design A
# the near arm (gauntlet + fist) row by row, and the far arm (striped forearm + hand at the socket)
NEAR_A = {19: (34, 37), 20: (32, 39), 21: (30, 38), 22: (29, 38), 23: (28, 38), 24: (28, 36), 25: (28, 36),
          26: (29, 36), 27: (30, 35), 28: (30, 35), 29: (30, 36), 30: (30, 36), 31: (29, 36), 32: (29, 36),
          33: (30, 37), 34: (29, 36), 35: (30, 36), 36: (32, 34)}
FAR_A = {23: (51, 53), 24: (50, 54), 25: (49, 54), 26: (50, 55), 27: (50, 56), 28: (50, 57), 29: (51, 58),
         30: (51, 58), 31: (52, 57), 32: (53, 57), 33: (54, 57), 34: (55, 58), 35: (55, 58), 36: (55, 58),
         37: (55, 59), 38: (55, 57), 39: (56, 57), 40: (56, 57)}
NEAR_PIVOT_A = (35.5, 20.5)                     # the near shoulder under the pauldron
FAR_PIVOT_A = (52.5, 23.5)
UPPER_END_A = 31                                # head, pauldrons, chest and belt: rows 0..31


def design_a():
    d = load("design_A.png")
    D = CutDesign(d, px=44)
    rgb = d[..., :3].astype(int)
    brown = np.zeros(d.shape[:2], bool)
    for c in BROWN:
        brown |= (rgb == c).all(-1)
    dark = rgb.sum(-1) < 40
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    # the staff: the spike and the shaft left of the body, the wood across the body (and its outline), the socket and
    # the blade right of the far hand
    left = ((xx <= 28) | ((xx == 29) & (yy == 33))) & (yy >= 23) & (yy <= 34)
    by, bx = np.nonzero(brown & (xx >= 36) & (xx <= 54))
    k, c0 = np.polyfit(bx, by, 1)
    near_line = np.abs(yy - (k * xx + c0)) <= 2.0
    wood = brown & near_line & (xx >= 36) & (xx <= 54)
    from scipy import ndimage
    rim = dark & near_line & ndimage.binary_dilation(wood, structure=R.CROSS) & (xx >= 36) & (xx <= 54)
    right = ((xx >= 59) & (yy >= 30)) | ((xx == 58) & (yy >= 38))
    D.part("staff", D.mask(lambda y, x: left | wood | rim | right))
    D.line = (k, c0)
    D.part("near_arm", D.rows(NEAR_A))
    D.part("far_arm", D.rows(FAR_A))
    D.part("upper", D.mask(lambda y, x: y <= UPPER_END_A) & D.rest())
    D.part("lower", D.rest())
    return D


# ------------------------------------------------------------------------------------------------- design B
NEAR_B = {21: (41, 45), 22: (41, 47), 23: (40, 47), 24: (39, 48), 25: (39, 49), 26: (39, 45), 27: (39, 47),
          28: (39, 48), 29: (36, 47), 30: (35, 46), 31: (33, 45), 32: (33, 45), 33: (33, 44), 34: (35, 45),
          35: (35, 45), 36: (35, 44), 37: (35, 44), 38: (36, 43), 39: (37, 43), 40: (37, 43), 41: (37, 43),
          42: (37, 45), 43: (36, 44), 44: (37, 44), 45: (37, 45), 46: (37, 46), 47: (37, 45), 48: (37, 44),
          49: (41, 43)}
FAR_B = {31: (65, 67), 32: (61, 67), 33: (61, 67), 34: (61, 67), 35: (61, 68), 36: (61, 70), 37: (62, 70),
         38: (62, 71), 39: (62, 72), 40: (62, 72), 41: (63, 72), 42: (64, 72), 43: (64, 71), 44: (66, 71),
         45: (67, 71), 46: (67, 71), 47: (67, 71), 48: (68, 71), 49: (68, 71), 50: (70, 72), 51: (67, 72),
         52: (66, 71)}
NEAR_PIVOT_B = (44.5, 21.5)
FAR_PIVOT_B = (64.5, 31.5)
UPPER_END_B = 41
BROWN_B = {(115, 40, 31), (145, 61, 44)}


def design_b():
    d = load("design_B.png")
    D = CutDesign(d, px=53)
    rgb = d[..., :3].astype(int)
    brown = np.zeros(d.shape[:2], bool)
    for c in BROWN_B:
        brown |= (rgb == c).all(-1)
    dark = rgb.sum(-1) < 40
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    left = (((xx <= 32) & (yy >= 33) & (yy <= 47)) | ((xx >= 33) & (xx <= 35) & (yy >= 43) & (yy <= 47)))
    by, bx = np.nonzero(brown & (xx >= 31) & (xx <= 67) & (yy >= 40))
    k, c0 = np.polyfit(bx, by, 1)
    near_line = np.abs(yy - (k * xx + c0)) <= 2.0
    wood = brown & near_line & (xx >= 44) & (xx <= 67)
    from scipy import ndimage
    rim = dark & near_line & ndimage.binary_dilation(wood, structure=R.CROSS) & (xx >= 44) & (xx <= 67)
    right = (xx >= 72) & (yy >= 47)
    D.part("staff", D.mask(lambda y, x: left | wood | rim | right))
    D.line = (k, c0)
    D.part("near_arm", D.rows(NEAR_B))
    D.part("far_arm", D.rows(FAR_B))
    D.part("upper", D.mask(lambda y, x: y <= UPPER_END_B) & D.rest())
    D.part("lower", D.rest())
    return D


def whole_staff(D, gaps):
    """The staff layer with its hidden shaft filled: each square column x in `gaps` (hidden behind the fist, the front
    strip, the far hand) copies the staff squares of the visible wood column whose line height has the nearest
    fraction, moved by the line's height difference (the shaft's own stair pattern carried on). -> design-sized RGBA."""
    st = D.layer("staff")
    k, c0 = D.line
    line = lambda x: k * x + c0
    m = D.parts["staff"]
    seen = [x for x in range(36, 55) if m[:, x].any() and x not in gaps]
    out = st.copy()
    for x in gaps:
        fx = line(x) % 1
        src = min(seen, key=lambda s: (min(abs(line(s) % 1 - fx), 1 - abs(line(s) % 1 - fx)), abs(s - x)))
        dy = int(round(line(x) - line(src)))
        ys = np.nonzero(m[:, src])[0]
        for y in ys:
            ty = y + dy
            if 0 <= ty < D.H and abs(ty - line(x)) <= 2.0 and not out[ty, x, 3]:
                out[ty, x] = st[y, src]
    return out


def ring(D, st, x0, x1):
    """st with a 1-square outline round the shaft's squares between columns x0..x1 where it has none (a moved staff
    lies over other parts or the ground, so its shaft carries its own outline). The spike and the blade keep theirs."""
    out = st.copy()
    op = st[..., 3] > 0
    dark = st[..., :3].astype(int).sum(-1) < 40
    for y, x in zip(*np.nonzero(op & ~dark)):
        if not x0 <= x <= x1:
            continue
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < D.H and 0 <= xx < D.W and not op[yy, xx]:
                out[yy, xx] = (*D.outline, 255)
    return out


def patched_lower(D):
    """The lower body with the staff's squares that lay across it (the shaft over the loincloth, between loincloth
    squares above and below) filled from the loincloth round them - the lower body a moved staff leaves."""
    lo = D.layer("lower")
    st = D.parts["staff"]
    body = D.parts["lower"]
    hole = np.zeros_like(st)
    for y, x in zip(*np.nonzero(st)):
        above = body[max(0, y - 4):y, x].any()
        below = body[y + 1:y + 5, x].any()
        if above and below:
            hole[y, x] = True
    return R.fill_under(lo, hole)


def turn_pt(p, about, k):
    """A point turned k quarter turns counter-clockwise on screen (y down) about `about` (ppu_rig.put's way)."""
    x, y = p
    ax, ay = about
    for _ in range(k % 4):
        x, y = ax + (y - ay), ay - (x - ax)
    return x, y


# the staff's lossless orientations: (flip left-right, quarter turns counter-clockwise), applied about the grip
STAFF_WAYS = {"S0": (False, 0),            # as drawn: blade forward and low
              "VF": (True, 2),             # mirrored top to bottom: blade forward and high
              "R180": (False, 2),          # half a turn: blade back and high
              "FL": (True, 0),             # mirrored: blade back and low
              "UP": (False, 1),            # a quarter turn: blade up (the shaft nearly upright)
              "DOWN": (False, 3),          # blade down
              "UPB": (True, 3),            # mirrored and turned: blade up, leaning back
              "DOWNB": (True, 1)}          # blade down, leaning back


class Form:
    """One form's design, its layers and pivots; pose() -> canvas."""

    def __init__(self, D, near_pivot, far_pivot, grip_near, grip_far, hand_row, gaps, head_rows, head_x, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.ref_holes = None
        self.near_pivot, self.far_pivot = near_pivot, far_pivot
        self.grip_near, self.grip_far = grip_near, grip_far
        exact = whole_staff(D, gaps)
        self.staff_exact = pad(exact)
        self.staff_ring = pad(ring(D, exact, 10, D.W - 14))
        far = D.layer("far_arm")
        fore, hand = far.copy(), far.copy()
        fore[hand_row:] = 0
        hand[:hand_row] = 0
        self.far_fore, self.far_hand = pad(fore), pad(hand)
        self.near = pad(D.layer("near_arm"))
        self.upper = pad(D.layer("upper"))
        self.lower = pad(D.layer("lower"))
        self.lower_open = pad(patched_lower(D))
        # the body's squares that lie over the shaft's hidden stretch (the gold front strip, the outline by the far
        # hand): drawn again over the staff, so the staff in its place shows exactly the design
        over = (exact[..., 3] > 0) & ~D.parts["staff"]
        front = np.zeros_like(D.d)
        for name in ("lower", "upper"):
            m = over & D.parts[name]
            front[m] = D.d[m]
        self.strip_front = pad(front)
        # the head (ears to the jaw): drawn over a staff held overhead, which passes behind it
        head = D.parts["upper"] & D.mask(lambda y, x: (y <= head_rows) & (x >= head_x))
        h = np.zeros_like(D.d)
        h[head] = D.d[head]
        self.head = pad(h)

    def pose(self, crouch=0, whole=(0, 0), near=0, far=0, near_reach=(0, 0), far_reach=(0, 0), staff="S0",
             staff_shift=(0, 0), grip="near", far_off=False, behind=False, fill=True):
        """crouch: rows the upper body (with both arms and the staff) sets down over the loincloth (never up);
        whole: the whole figure; near / far: quarter turns of an arm counter-clockwise about its shoulder (1 forward, 2
        up); *_reach: whole squares an arm moves after turning; staff: one of STAFF_WAYS, turned about the grip and
        set into the near hand (grip="far": the far hand), then moved staff_shift; far_off: the far arm left out;
        behind: "head" - the staff passes behind the head (held up), "upper" - behind the whole upper body (over the
        shoulder)."""
        if crouch < 0:
            raise ValueError("the upper body never lifts off the loincloth")
        wx, wy = whole
        U = (wx, wy + crouch)
        hand = turn_pt(self.grip_near, self.near_pivot, near)
        hand = (hand[0] + U[0] + near_reach[0], hand[1] + U[1] + near_reach[1])
        fhand = turn_pt(self.grip_far, self.far_pivot, far)
        fhand = (fhand[0] + U[0] + far_reach[0], fhand[1] + U[1] + far_reach[1])
        flip, rot = STAFF_WAYS[staff or "S0"]
        g = self.grip_near if grip == "near" else self.grip_far
        at = hand if grip == "near" else fhand
        sdx, sdy = int(round(at[0] - g[0])) + staff_shift[0], int(round(at[1] - g[1])) + staff_shift[1]
        in_place = staff == "S0" and (sdx, sdy) == U
        st = self.staff_exact if in_place else self.staff_ring
        layers = []
        if not far_off:
            layers.append((self.far_fore, dict(dx=U[0] + far_reach[0], dy=U[1] + far_reach[1], rot=far,
                                               about=self.far_pivot)))
        at_lower = staff == "S0" and (sdx, sdy) == (wx, wy)
        layers += [(self.lower if at_lower else self.lower_open, dict(dx=wx, dy=wy)), (self.upper, dict(dx=U[0], dy=U[1]))]
        if staff:
            layers += [(st, dict(dx=sdx, dy=sdy, rot=rot, flip=flip, about=g)), (self.strip_front, dict(dx=wx, dy=wy))]
        if behind == "head":
            layers.append((self.head, dict(dx=U[0], dy=U[1])))
        elif behind == "upper":
            layers.append((self.upper, dict(dx=U[0], dy=U[1])))
        if not far_off:
            layers.append((self.far_hand, dict(dx=U[0] + far_reach[0], dy=U[1] + far_reach[1], rot=far,
                                               about=self.far_pivot)))
        layers.append((self.near, dict(dx=U[0] + near_reach[0], dy=U[1] + near_reach[1], rot=near,
                                       about=self.near_pivot)))
        fills = [("staff", (wx, wy)), ("near_arm", U), ("far_arm", U)] if fill else []
        can = R.compose(self.rig, layers, fill=fills)
        return self.close_holes(can) if fill else can

    MOST = 16

    def close_holes(self, can):
        """Small enclosed holes this form's idle does not have (the shoulder joint a turned arm leaves, the slit between
        an arm and the body a crouch closes at the bottom) filled from the squares round them."""
        from scipy import ndimage
        if self.ref_holes is None:
            idle = R.compose(self.rig, [(self.far_fore, {}), (self.lower, {}), (self.upper, {}), (self.staff_exact, {}),
                                        (self.strip_front, {}), (self.far_hand, {}), (self.near, {})])
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
        return R.fill_under(can, fill) if fill.any() else can


def form_a():
    D = design_a()
    return Form(D, NEAR_PIVOT_A, FAR_PIVOT_A, grip_near=(33.5, 33.5), grip_far=(56.5, 38.5), hand_row=36,
                gaps=list(range(29, 37)) + list(range(44, 48)) + list(range(54, 58)), head_rows=17, head_x=41,
                rig_pad=(90, 90, 140, 30))


MS = {"idle": [140] * 8, "run": [85] * 9, "b_run": [85] * 9, "attack": [70, 70, 60, 90, 80, 63], "skill": [60, 60, 40, 80, 90, 70],
      "skill2": [70, 80, 80, 90, 80], "skill_w": [60, 60, 100, 80], "ult": [60, 70, 70, 100, 100, 100],
      "hit": [100, 100], "dead": [100, 100, 120, 120, 120, 150, 150, 500]}


def form_b(fa=None):
    """B on a canvas of A's size with its standing point on A's (one sheet, one pivot for both forms)."""
    D = design_b()
    fa = fa or form_a()
    ra = fa.rig
    left, top = ra.CX - D.px, ra.GY - D.ground
    pad_ = (left, ra.CW - left - D.W, top, ra.CH - top - D.H)
    k, c0 = D.line
    return Form(D, NEAR_PIVOT_B, FAR_PIVOT_B, grip_near=(40.5, float(int(k * 40.5 + c0)) + 0.5),
                grip_far=(69.5, float(int(k * 69.5 + c0)) + 0.5), hand_row=47,
                gaps=list(range(36, 45)) + list(range(54, 60)) + list(range(67, 72)), head_rows=24, head_x=53,
                rig_pad=pad_)


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


def staff_on_ground(F, way="S0", dx=0):
    """The staff alone lying on the ground (a 3/4 view: one end nearer, lower on the screen), its lowest square on the
    soles' row, dx squares from where it was drawn. -> canvas."""
    can = R.compose(F.rig, [(F.staff_ring, dict(rot=STAFF_WAYS[way][1], flip=STAFF_WAYS[way][0], about=F.grip_near))])
    ys = np.nonzero(can[..., 3].any(1))[0]
    out = F.rig.canvas()
    sh = F.rig.GY - 1 - ys.max()
    src = can[max(0, -sh):can.shape[0] - max(0, sh)]
    out[max(0, sh):max(0, sh) + src.shape[0]] = src
    return np.roll(out, dx, axis=1)


def frames_a(F):
    p = F.pose
    out = {}
    out["idle"] = [p(crouch=b) for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    # the staff raised forward, the blade high (both arms a quarter turn forward, the far hand on the shaft by the
    # blade); "back" pulls it back along its own line (League's wind-ups), the strikes push it on along the drawn line
    raised = dict(near=1, far=1, staff="VF")
    # auto attack (League's nasus_attack1, an overhead chop): raised and drawn back, then down so the blade strikes the
    # ground ahead (frame 3 from tick 8.4, the blow on tick 9), held, and back
    out["attack"] = [p(whole=(-1, 0), **raised), p(whole=(-2, 0), staff_shift=(-4, 1), **raised),
                     p(crouch=1, whole=(1, 0), staff_shift=(4, 0)), p(crouch=1, whole=(1, 0), staff_shift=(4, 0)),
                     p(crouch=1), p()]
    # Q Siphoning Strike (Nasus_Spell1): raised and drawn far back, over, and slammed down far ahead with the body
    # thrown forward (frame 4 from tick 9.6, the blow on tick 10)
    out["skill"] = [p(whole=(-2, 0), staff_shift=(-4, 1), **raised), p(whole=(-3, 0), staff_shift=(-8, 2), **raised),
                    p(**raised), p(crouch=2, whole=(2, 0), staff_shift=(7, 0)), p(crouch=2, whole=(2, 0), staff_shift=(7, 0)),
                    p(crouch=1, whole=(1, 0), staff_shift=(3, 0))]
    # E Spirit Fire (Nasus_Base_Spell3_Full): gathers, raises the staff and thrusts it at the spot (frame 3 on tick 9)
    out["skill2"] = [p(crouch=1), p(**raised), p(whole=(1, 0), staff_shift=(4, -1), **raised),
                     p(whole=(1, 0), staff_shift=(4, -1), **raised), p(crouch=1)]
    # W Wither (Nasus_Base_Spell2_Full): the far hand thrust out at the champion, the staff kept in the near hand
    out["skill_w"] = [p(far=1, far_reach=(-2, 0)), p(far=1, whole=(1, 0)), p(far=1, whole=(1, 0)),
                      p(far=1, far_reach=(-2, 0))]
    # R Fury of the Sands (Nasus_Base_Spell4_Full): crouch, then up with the staff raised upright beside his head (the
    # big body from frame 4 - the kit's r_on_at; frames 4-6 are B's, set by frames())
    up = dict(near=2, near_reach=(-4, 0), staff="UP", staff_shift=(3, -14), behind="head")
    out["ult"] = [p(crouch=1), p(crouch=2), p(**up)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (Nasus_Base_Death): staggers back, sinks, falls on his back, the staff dropped on the ground beside him
    body = p(crouch=2, whole=(-3, 0), staff=None)
    lying = R.lie(F.rig, body, k=1, dx=-6)
    ground = staff_on_ground(F, dx=6)
    m = lying[..., 3] > 0
    ly = ground.copy()
    ly[m] = lying[m]
    out["dead"] = [p(whole=(-1, 0)), p(crouch=1, whole=(-2, 0)), p(crouch=2, whole=(-3, 0)), ly] + [ly.copy() for _ in range(4)]
    return out


def frames_b(F):
    """The big body's tags (the add-on's whole-body swap: b_idle, b_hit; the main pack's casts while R lasts:
    b_attack, b_skill, b_skill2, b_skill_w) and R's frames 4-6 - A's poses with B's own parts, the moves ~1.35x."""
    p = F.pose
    out = {}
    out["b_idle"] = [p(crouch=b) for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    raised = dict(near=1, far=1, staff="VF")
    out["b_attack"] = [p(whole=(-1, 0), **raised), p(whole=(-3, 0), staff_shift=(-5, 1), **raised),
                       p(crouch=1, whole=(1, 0), staff_shift=(5, 0)), p(crouch=1, whole=(1, 0), staff_shift=(5, 0)),
                       p(crouch=1), p()]
    out["b_skill"] = [p(whole=(-3, 0), staff_shift=(-5, 1), **raised), p(whole=(-4, 0), staff_shift=(-10, 2), **raised),
                      p(**raised), p(crouch=3, whole=(3, 0), staff_shift=(9, 0)),
                      p(crouch=3, whole=(3, 0), staff_shift=(9, 0)), p(crouch=1, whole=(1, 0), staff_shift=(4, 0))]
    out["b_skill2"] = [p(crouch=1), p(**raised), p(whole=(1, 0), staff_shift=(5, -1), **raised),
                       p(whole=(1, 0), staff_shift=(5, -1), **raised), p(crouch=1)]
    out["b_skill_w"] = [p(far=1, far_reach=(-3, 0)), p(far=1, whole=(1, 0)), p(far=1, whole=(1, 0)),
                        p(far=1, far_reach=(-3, 0))]
    out["b_hit"] = [R.flash(p(whole=(-3, 0))), p(whole=(-1, 0))]
    up = dict(near=2, near_reach=(-5, 0), staff="UP", staff_shift=(4, -19), behind="head")
    out["ult_b"] = [p(**up), p(**up), p(crouch=1, **up)]
    return out


MS.update({"b_idle": MS["idle"], "b_attack": MS["attack"], "b_skill": MS["skill"], "b_skill2": MS["skill2"],
           "b_skill_w": MS["skill_w"], "b_hit": MS["hit"]})


RUN_DIR = os.path.join(R.ROOT, "assets", "source", "nasus", "codex_run")


def runs(fa, fb):
    """The walk of each form: Codex's skin swap over oppi's Sion run (read_run); until it is delivered, the idle's
    first frame nine times (a placeholder that keeps the sheet whole)."""
    out = {}
    for tag, F in (("run", fa), ("b_run", fb)):
        path = os.path.join(RUN_DIR, f"nasus_run_{'A' if F is fa else 'B'}.png")
        out[tag] = read_run(F, path) if os.path.exists(lp(path)) else [F.pose() for _ in range(9)]
    return out


def read_run(F, path):
    raise NotImplementedError("written when Codex's walk is delivered")


def frames(fa, fb):
    """{tag: [(canvas, ms)]} in the sheet's order; R's strip = A's three frames + B's three."""
    a, b = frames_a(fa), frames_b(fb)
    a["ult"] = a["ult"] + b.pop("ult_b")
    rn = runs(fa, fb)
    a = {"idle": a["idle"], "run": rn["run"], **{k: v for k, v in a.items() if k != "idle"}}
    b = {"b_idle": b["b_idle"], "b_run": rn["b_run"], **{k: v for k, v in b.items() if k != "b_idle"}}
    out = {}
    for tag, cans in list(a.items()) + list(b.items()):
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def audit(F, acts, out_dir, allowed_extra=(), big=None):
    """Every frame after ppu_rig's finish(): its pieces (8-connected), the holes it closes in that the idle does not,
    colours in no design, outline squares with no colour beside them; each tag at 6x with every piece but the biggest
    red and every new hole magenta (rig_swain.audit)."""
    from scipy import ndimage
    from PIL import ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    rig = F.rig
    allowed = {tuple(c) for c in F.D.d[F.D.d[..., 3] > 0][:, :3].tolist()} | {tuple(F.D.outline)}
    allowed |= set(allowed_extra)
    def baseline(tag):
        idle = rig.finish(acts[tag][0][0])
        iop = idle[..., 3] > 0
        idark = iop & (np.abs(idle[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
        return (int((idark & ~ndimage.binary_dilation(iop & ~idark, structure=R.CROSS)).sum()),
                ndimage.binary_fill_holes(iop) & ~iop)
    bases = {"A": baseline("idle"), "B": baseline("b_idle") if "b_idle" in acts else None}
    bad = 0
    for tag, fr in acts.items():
        tiles = []
        for i, (c, _) in enumerate(fr):
            form = "B" if tag.startswith("b_") or (big and (tag, i) in big) else "A"
            base_orphan, idle_holes = bases[form]
            f = rig.finish(c)
            op = f[..., 3] > 0
            lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
            sz = sorted(ndimage.sum(op, lbl, range(1, n + 1)).astype(int).tolist(), reverse=True) if n else []
            holes = ndimage.binary_fill_holes(op) & ~op
            new = holes & ~ndimage.binary_dilation(idle_holes, iterations=3)
            odd = {tuple(v) for v in f[op][:, :3].tolist()} - allowed
            dark = op & (np.abs(f[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
            orphan = dark & ~ndimage.binary_dilation(op & ~dark, structure=R.CROSS)
            flag = len(sz) > 1 or new.sum() or (odd and "hit" not in tag) or orphan.sum() > base_orphan
            bad += bool(flag)
            print(f"{tag:9s} {i + 1}: pieces {sz[:4]} new holes {int(new.sum())} odd colours {len(odd)} "
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
        fa = form_a()
        fb = form_b(fa)
        fa.rig.export(frames(fa, fb))
        return
    if a.audit or a.review:
        fa = form_a()
        fb = form_b(fa)
        acts = frames(fa, fb)
        if a.audit:
            db = fb.D.d
            audit(fa, acts, a.audit, allowed_extra={tuple(c) for c in db[db[..., 3] > 0][:, :3].tolist()},
                  big={("ult", 3), ("ult", 4), ("ult", 5)})
        else:
            fa.rig.review(acts, a.review)
        return
    D = design_a()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        R.Design.ruler(D, os.path.join(a.parts, f"{HERO}_A_parts.png"), z=12)
        print("staff line y = %.3f x + %.2f" % D.line)
        full = whole_staff(D, list(range(29, 37)) + list(range(44, 48)) + list(range(54, 58)))
        Image.fromarray(np.repeat(np.repeat(full, 12, 0), 12, 1)).save(lp(os.path.join(a.parts, f"{HERO}_A_staff.png")))
        DB = design_b()
        R.Design.ruler(DB, os.path.join(a.parts, f"{HERO}_B_parts.png"), z=12)
        print("B staff line y = %.3f x + %.2f" % DB.line)
        FB = form_b()
        idleb = FB.pose()
        refb = FB.rig.canvas()
        refb[FB.rig.oy:FB.rig.oy + DB.H, FB.rig.ox:FB.rig.ox + DB.W] = DB.d
        print("B idle vs design: squares differing", int((np.abs(idleb.astype(int) - refb.astype(int)).sum(-1) > 0).sum()))
        Image.fromarray(np.repeat(np.repeat(FB.staff_ring, 6, 0), 6, 1)).save(lp(os.path.join(a.parts, f"{HERO}_B_staff.png")))
        F = form_a()
        idle = F.pose()
        ref = F.rig.canvas()
        ref[F.rig.oy:F.rig.oy + D.H, F.rig.ox:F.rig.ox + D.W] = D.d
        diff = int((np.abs(idle.astype(int) - ref.astype(int)).sum(-1) > 0).sum())
        print("idle vs design: squares differing", diff)
        tries = [F.pose(), F.pose(crouch=2), F.pose(near=1, far=1, staff="VF"), F.pose(near=2, far=2, staff="VF"),
                 F.pose(near=2, far=2, staff="R180", behind=True), F.pose(near=2, far=2, staff="VF", behind=True), F.pose(crouch=3, whole=(2, 0), staff="S0", staff_shift=(2, 2)),
                 F.pose(near=2, staff="UP", far=0), F.pose(far=1, far_reach=(0, 0))]
        sheet([F.rig.finish(c) for c in tries], os.path.join(a.parts, f"{HERO}_A_tries.png"))
        return


if __name__ == "__main__":
    main()

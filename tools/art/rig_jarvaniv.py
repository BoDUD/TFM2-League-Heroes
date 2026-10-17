#!/usr/bin/env python3
"""league_jarvaniv's action frames posed from the approved design's own squares (the user, 2026-10-17: 「用 A2 cut，动作帧
按照塔姆那样做吧 做到完美了喊我review」).

    python tools/art/rig_jarvaniv.py --parts DIR       # the design with its parts tinted + pose tries (8-12x)
    python tools/art/rig_jarvaniv.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_jarvaniv.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_jarvaniv.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design (tools/art/design_jarvaniv_cut.py: Codex's step-1 take A-2 brought to 60 body rows, PPU 1.5, by whole rows /
columns dropped, never the face's nor the lance's shaft): 34 x 73 squares, the lance's tip row 0, the helmet's top row
13, the soles row 72. Every pose is lossless (memory no-deformation-lossless-poses): parts cut square by square from the
design and only moved by whole squares, quarter turns about half-integer pivots (square centres stay centres) and mirror
images; nothing is drawn again at another angle (league_swain's arm, 「右手臂移动时候有点变形」).
Parts: the lance (spearhead, guard, shaft and butt; the shaft's squares the far fist hides are filled once from its own
column below the fist, so it is whole wherever it goes), the far arm (the sleeve, the gauntlet and the fist on the
shaft), the near arm (the elbow, the gauntlet and the hand hanging under the near pauldron), the upper body (head,
pauldrons, breastplate, belt), the skirt and the two legs. The lance turns as a whole in the lossless ways about the
fist (upright as drawn; a quarter turn clockwise: level, the spearhead forward - League's thrusts; counter-clockwise:
level, the spearhead back - carried; half a turn: point down - Cataclysm's landing); the arms turn in quarter turns about
their shoulders; a crouch sets the upper body down over the skirt (never lifted off it). The walk moves each leg whole
under the skirt (the stance is too wide to cross the legs - memory nasus-session's walk).
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

HERO = "jarvaniv"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "jarvaniv", "hd")
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

    def rows(self, spans):
        """{row: (x0, x1)} inclusive spans -> mask."""
        m = np.zeros((self.H, self.W), bool)
        for y, (x0, x1) in spans.items():
            m[y, max(0, x0):min(self.W, x1 + 1)] = True
        return m & (self.d[..., 3] > 0)

    def box(self, y0, y1, x0, x1):
        return self.rows({y: (x0, x1) for y in range(y0, y1 + 1)})

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


# ------------------------------------------------------------------------------------------------- the design's parts
FIST = (40, 45, 27, 32)                         # rows y0..y1, columns x0..x1: the far fist round the shaft
FAR_ARM = {38: (19, 22), 39: (19, 23), 40: (19, 24), 41: (19, 26), 42: (22, 26), 43: (21, 26), 44: (21, 26),
           45: (21, 26), 46: (22, 24)}          # the far sleeve and gauntlet down to the fist
NEAR_ARM = {38: (4, 8), 39: (2, 8), 40: (2, 7), 41: (2, 7), 42: (1, 8), 43: (1, 8), 44: (1, 8), 45: (2, 7),
            46: (2, 7), 47: (2, 7), 48: (3, 7), 49: (3, 7), 50: (4, 7), 51: (3, 7), 52: (5, 7)}
NEAR_PIVOT = (6.5, 38.5)                        # the near shoulder under the pauldron
FAR_PIVOT = (20.5, 38.5)                        # the far shoulder
GRIP = (29.5, 42.5)                             # the middle of the far fist, on the shaft's line (column 29)
UPPER_END = 46                                  # head, pauldrons, breastplate and belt: rows 0..46
SHAFT = 29                                      # the lance's middle column
# the legs from the knee guards down (the skirt's hem stays with the body)
NEAR_LEG = {y: (0, 12) for y in range(54, 73)}
FAR_LEG = {54: (20, 27), 55: (20, 27), 56: (20, 27), 57: (20, 27), **{y: (17, 27) for y in (58,)},
           **{y: (14, 27) for y in range(59, 73)}}


def navy(d):
    """The skirt's cloth (dark navy-violet), not the knee guards' blue gems."""
    r, g, b = (d[..., i].astype(int) for i in range(3))
    gem = (b > 150) & (r < 90)
    return (d[..., 3] > 0) & (b > r + 10) & (b > g + 10) & ~gem


def design():
    d = load("design.png")
    D = CutDesign(d, px=14)
    fist = D.box(*FIST)
    lance = D.rows({y: (26, 33) for y in range(D.H)}) & ~fist
    D.part("lance", lance)
    D.part("far_arm", D.rows(FAR_ARM) | fist)
    D.part("near_arm", D.rows(NEAR_ARM))
    D.part("upper", D.rows({y: (0, 33) for y in range(UPPER_END + 1)}) & D.rest())
    # each leg its own gold / brown / blue squares and outline - never the skirt's navy cloth hanging between them
    # (the first cut carried a square or two of it, so the skirt's hem moved with the legs)
    cloth = navy(d)
    D.part("near_leg", D.rows(NEAR_LEG) & D.rest() & ~cloth)
    D.part("far_leg", D.rows(FAR_LEG) & D.rest() & ~cloth)
    D.part("skirt", D.rest())
    return D


def leg_layer(D, name):
    """A leg with its own whole outline: the outline squares it shares with the skirt (the knee guard's top edge is the
    skirt's hem line) copied into it, so moved it keeps its edge; the skirt keeps them too (at home they coincide)."""
    leg = D.parts[name]
    dark = (D.d[..., :3].astype(int).sum(-1) < 70) & (D.d[..., 3] > 0)
    near = ndimage.binary_dilation(leg & ~dark, structure=R.CROSS)
    shared = near & dark & D.parts["skirt"]
    out = np.zeros_like(D.d)
    m = leg | shared
    out[m] = D.d[m]
    return out


def whole_lance(D):
    """The lance layer with the shaft the fist hides (rows FIST) filled from its own column under the fist: each hidden
    row copies the row ROWS_BELOW rows down (the shaft below the fist is a plain gold stripe between two outline columns
    there, rows 47-51). -> design-sized RGBA."""
    out = D.layer("lance")
    y0, y1 = FIST[0], FIST[1]
    src = list(range(47, 52))
    for i, y in enumerate(range(y0, y1 + 1)):
        sy = src[i % len(src)]
        for x in (SHAFT - 1, SHAFT, SHAFT + 1):
            out[y, x] = D.d[sy, x]
    return out


def turn_pt(p, about, k):
    """A point turned k quarter turns counter-clockwise on screen (y down) about `about` (ppu_rig.put's way)."""
    x, y = p
    ax, ay = about
    for _ in range(k % 4):
        x, y = ax + (y - ay), ay - (x - ax)
    return x, y


# the lance's lossless orientations: quarter turns counter-clockwise about the grip
LANCE = {"UP": 0,          # as drawn: upright, the spearhead up
         "FWD": 3,         # level, the spearhead forward (a quarter turn clockwise)
         "BACK": 1,        # level, the spearhead back
         "DOWN": 2}        # upright, the spearhead down (planted)


class Form:
    """The design's layers and pivots; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.lance = pad(whole_lance(D))
        self.lance_drawn = pad(D.layer("lance"))
        self.far = pad(D.layer("far_arm"))
        self.near = pad(D.layer("near_arm"))
        self.upper = pad(D.layer("upper"))
        self.skirt = pad(D.layer("skirt"))
        self.near_leg = pad(leg_layer(D, "near_leg"))
        self.far_leg = pad(leg_layer(D, "far_leg"))
        self.ref_holes = None

    def grip_at(self, far=0, far_reach=(0, 0), U=(0, 0)):
        g = turn_pt(GRIP, FAR_PIVOT, far)
        return g[0] + U[0] + far_reach[0], g[1] + U[1] + far_reach[1]

    def pose(self, crouch=0, whole=(0, 0), near=0, far=0, near_reach=(0, 0), far_reach=(0, 0), lance="UP",
             slide=0, lance_shift=(0, 0), legs=None, behind=False, fill=True, lance_front=False):
        """crouch: rows the upper body (with both arms and the lance) sets down over the skirt (never up); whole: the
        whole figure; near / far: quarter turns of an arm counter-clockwise about its shoulder; *_reach: whole squares
        an arm moves after turning; lance: one of LANCE, turned about the grip and set into the far fist, slid `slide`
        squares along its own line (+ toward the spearhead), then moved lance_shift; legs: ((near dx, dy), (far dx,
        dy)) moves of the legs; lance_front: the lance over the body (else behind it, the fist over it)."""
        if crouch < 0:
            raise ValueError("the upper body never lifts off the skirt")
        wx, wy = whole
        U = (wx, wy + crouch)
        gx, gy = self.grip_at(far, far_reach, U)
        k = LANCE[lance] if lance else 0
        # the slide along the line: the spearhead's direction after the turn
        sx, sy = turn_pt((0, -1), (0, 0), k)
        ldx = int(round(gx - GRIP[0])) + int(round(sx * slide)) + lance_shift[0]
        ldy = int(round(gy - GRIP[1])) + int(round(sy * slide)) + lance_shift[1]
        in_place = lance == "UP" and (ldx, ldy) == (0, 0) and not slide
        st = self.lance_drawn if in_place else self.lance
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        far_l = (self.far, dict(dx=U[0] + far_reach[0], dy=U[1] + far_reach[1], rot=far, about=FAR_PIVOT))
        lance_l = (st, dict(dx=ldx, dy=ldy, rot=k, about=GRIP)) if lance else None
        layers = []
        if lance_l and not lance_front:
            layers.append(lance_l)
        layers += [far_l,
                   (self.far_leg, dict(dx=wx + flx, dy=wy + fly)), (self.skirt, dict(dx=wx, dy=wy)),
                   # the near leg in front of the skirt's hem: lifted or stepping in, its knee guard stays whole
                   (self.near_leg, dict(dx=wx + nlx, dy=wy + nly)), (self.upper, dict(dx=U[0], dy=U[1]))]
        if lance_l and lance_front:
            layers += [lance_l, (self.fist_only(), far_l[1])]
        layers.append((self.near, dict(dx=U[0] + near_reach[0], dy=U[1] + near_reach[1], rot=near, about=NEAR_PIVOT)))
        fills = [("near_arm", U), ("far_arm", U)] if fill else []
        can = R.compose(self.rig, layers, fill=fills)
        return self.close_holes(can) if fill else can

    def fist_only(self):
        m = np.zeros((self.D.H, self.D.W), bool)
        y0, y1, x0, x1 = FIST
        m[y0:y1 + 1, x0:x1 + 1] = True
        out = np.zeros_like(self.D.d)
        sel = m & self.D.parts["far_arm"]
        out[sel] = self.D.d[sel]
        return pad(out)

    MOST = 12

    def close_holes(self, can):
        """Small enclosed holes the idle does not have (the shoulder joint a turned arm leaves) filled from the squares
        round them."""
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
    return Form(design(), rig_pad=(60, 70, 30, 20))


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


def lance_on_ground(F, dx=0):
    """The lance alone lying level on the ground (the spearhead forward), its lowest square on the soles' row, dx squares
    from where the fist held it. -> canvas."""
    can = R.compose(F.rig, [(F.lance, dict(rot=LANCE["FWD"], about=GRIP))])
    ys = np.nonzero(can[..., 3].any(1))[0]
    out = F.rig.canvas()
    sh = F.rig.GY - 1 - ys.max()
    src = can[max(0, -sh):can.shape[0] - max(0, sh)]
    out[max(0, sh):max(0, sh) + src.shape[0]] = src
    return np.roll(out, dx, axis=1)


MS = {"idle": [140] * 8, "run": [125] * 8, "attack": [70, 70, 60, 90, 80, 63], "skill": [60, 70, 70, 90, 100, 177],
      "skill_dash": [100, 100], "skill_land": [80, 90], "skill2": [60, 70, 50, 100, 90, 63], "skill_w": [60, 60, 100, 80],
      "ult": [60, 70, 70, 100, 100, 100], "hit": [100, 100], "dead": [100, 100, 120, 120, 120, 150, 150, 500]}


def frames_all(F):
    p = F.pose
    out = {}
    # idle: the upper body sinks a row over the skirt and rises (League's idle breath); the lance stays planted, the fist
    # sliding a row down its shaft
    out["idle"] = [p(crouch=b, lance_shift=(0, -b)) for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    # auto attack (League's jarvanIV_attack1: the lance brought down level, drawn back and thrust): level and drawn back,
    # further back with the body, the thrust (frame 3 from tick 8.4, the hit on tick 9), held, back, upright again
    fwd = dict(lance="FWD")
    out["attack"] = [p(whole=(-1, 0), slide=-6, **fwd), p(crouch=1, whole=(-2, 0), slide=-10, **fwd),
                     p(crouch=1, whole=(2, 0), slide=4, **fwd), p(crouch=1, whole=(2, 0), slide=4, **fwd),
                     p(whole=(1, 0), slide=-2, **fwd), p()]
    # E -> Q (League's jarvanIV_spell3 throw, then the drag): the near arm up and back, the banner thrown forward (frame 3
    # from tick 7.8, the throw on tick 8), the arm held out while the banner flies, then the lance levelled for the drag
    out["skill"] = [p(near=2), p(near=2, whole=(-1, 0), crouch=1), p(near=1, whole=(1, 0)), p(near=1, whole=(1, 0)),
                    p(near=1, slide=-4, **fwd), p(slide=-6, crouch=1, **fwd)]
    # the drag: leaning after the lance, both feet off the ground behind him
    out["skill_dash"] = [p(whole=(1, -2), slide=6, legs=((-2, -1), (-3, 0)), **fwd),
                         p(whole=(1, -3), slide=6, legs=((-3, 0), (-2, -1)), **fwd)]
    # landing at the banner: down on the knees a moment, the lance level
    out["skill_land"] = [p(crouch=2, slide=2, **fwd), p(crouch=1, **fwd)]
    # Q Dragon Strike alone (League's jarvanIV_spell1: a deep lunge thrust): level and drawn far back, the body low, the
    # thrust far ahead (frame 4 from tick 10.8, the lance flies on tick 11), held, back
    out["skill2"] = [p(slide=-6, **fwd), p(crouch=1, whole=(-2, 0), slide=-12, **fwd),
                     p(crouch=2, whole=(-2, 0), slide=-12, **fwd), p(crouch=2, whole=(3, 0), slide=8, **fwd),
                     p(crouch=1, whole=(2, 0), slide=6, **fwd), p(slide=-2, **fwd)]
    # W Golden Aegis (League's jarvanIV_spell2: the lance raised over the head, a roar)
    up = dict(far=1)
    out["skill_w"] = [p(**up), p(crouch=1, **up), p(crouch=1, near=2, **up), p(**up)]
    # R Cataclysm (League's jarvanIV_spell4): down, up in the air with the lance level over the head, down on the spot,
    # the lance driven point first into the ground in front of him, held
    out["ult"] = [p(crouch=2, **fwd), p(whole=(0, -8), far=1, **fwd), p(whole=(1, -10), far=1, **fwd),
                  p(crouch=2, lance="DOWN", lance_shift=(1, -15)), p(crouch=2, lance="DOWN", lance_shift=(1, -15)),
                  p(crouch=1, lance="DOWN", lance_shift=(1, -14))]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's jarvanIV_death: down on his knees, the lance dropped, falls forward): staggers, sinks letting
    # the lance fall level, the lance on the ground and the empty hand down, then face down behind the lance
    ground = lance_on_ground(F, dx=6)
    sink = p(crouch=2, whole=(-1, 0), far=3, lance=None)
    kg = ground.copy()
    kg[sink[..., 3] > 0] = sink[sink[..., 3] > 0]
    lying = R.lie(F.rig, p(crouch=2, lance=None), k=3, dx=-8)
    ly = ground.copy()
    ly[lying[..., 3] > 0] = lying[lying[..., 3] > 0]
    out["dead"] = [p(whole=(-1, 0)), p(crouch=1, whole=(-1, 0), lance="FWD", slide=-4),
                   kg, kg.copy(), ly] + [ly.copy() for _ in range(3)]
    return out


# ------------------------------------------------------------------------------------------------- the walk
def _steps(stride, lifts, far_lifts=None):
    """rig_nasus._steps: each leg planted five frames sliding back, then lifted and swung forward in three, the far leg
    four frames after the near one; the body a row down as each foot lands. Each foot keeps to the inner side of its own
    place (the near one between home and stride columns forward, the far one between stride columns back and home):
    outward a leg would leave the skirt's hanging middle flap alone between the knees with no edge - the user's
    「走路时腿部有点变形啊」 on the first walk (feet 3 columns out each way). far_lifts: the far leg's own lifts (lifted it
    slides up behind the skirt, so lifted as high as the near one its knee guard would vanish under the hem)."""
    near = [round(stride * (1 - k / 4) + 1e-9) for k in range(5)]
    swing = [1, stride - 1 - (stride > 4), stride]
    dx = near + swing
    up = [0] * 5 + list(lifts)
    fup = [0] * 5 + list(far_lifts or lifts)
    return dict(near=list(zip(dx, up)), far=[(dx[(i + 4) % 8] - stride, fup[(i + 4) % 8]) for i in range(8)],
                bob=[1, 0, 0, 0, 1, 0, 0, 0])


def _own_sides(stride, lifts):
    """Each foot steps on its own side (oppi's front-ish runs: the feet never cross, they open and close): planted ahead
    at +stride/2 and sliding back to -stride/2 in five frames, lifted and carried forward in three, the far foot half a
    cycle later - so the feet are close (the near one forward, the far one back) and wide apart in turn."""
    a = stride / 2
    planted = [int(round(a - stride * k / 4)) for k in range(5)]
    swing = [int(round(-a + stride * k / 4)) for k in (1, 2, 3)]
    dx = planted + swing
    up = [0] * 5 + list(lifts)
    return dict(near=list(zip(dx, up)), far=[(dx[(i + 4) % 8], up[(i + 4) % 8]) for i in range(8)],
                bob=[1, 0, 0, 0, 1, 0, 0, 0])


WALK_STEP = _steps(4, (2, 3, 2), far_lifts=(1, 2, 1))
# League's run carries the lance level on the shoulder, the spearhead back (jarvanIV_run): the far arm a quarter turn up,
# the lance turned counter-clockwise about the fist and slid toward the spearhead so the fist holds it near its middle
CARRY = dict(far=1, lance="BACK", slide=4)


def walk(F, steps=None, carry=None):
    """The walk: a frame per WALK_STEP entry, every square the design's, only moved: each leg whole (planted and sliding
    back, lifted and carried forward), the body a row down as each foot lands, the near arm swinging a column against
    the near leg, the lance carried (CARRY). -> canvases."""
    st = steps or WALK_STEP
    back = min(dx for dx, _ in st["near"])
    out = []
    for (ndx, nup), (fdx, fup), bob in zip(st["near"], st["far"], st["bob"]):
        # the near arm swings forward (over the body) while the near foot is back; it never moves back off the body
        # (that would open a slot between the arm and the breastplate)
        arm = 1 if ndx <= back + 1 and not nup else 0
        out.append(F.pose(crouch=bob, legs=((ndx, -nup), (fdx, -fup)), near_reach=(arm, 0), **(carry or CARRY)))
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
    """Every frame after ppu_rig's finish(): its pieces (8-connected), the holes it closes in that the idle does not,
    colours in no design, outline squares with no colour beside them; each tag at 6x with every piece but the biggest
    red, every new hole magenta and every orphan outline square orange (rig_nasus.audit)."""
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
            dark = op & (np.abs(f[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
            orphan = dark & ~ndimage.binary_dilation(op & ~dark, structure=R.CROSS)
            flag = len(sz) > 1 or new.sum() or (odd and "hit" not in tag) or orphan.sum() > base_orphan
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
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        D = design()
        R.Design.ruler(D, os.path.join(a.parts, f"{HERO}_parts.png"), z=12)
        F = form()
        idle = F.pose()
        ref = F.rig.canvas()
        ref[F.rig.oy:F.rig.oy + D.H, F.rig.ox:F.rig.ox + D.W] = D.d
        print("idle vs design: squares differing", int((np.abs(idle.astype(int) - ref.astype(int)).sum(-1) > 0).sum()))
        Image.fromarray(np.repeat(np.repeat(whole_lance(D), 12, 0), 12, 1)).save(lp(os.path.join(a.parts, f"{HERO}_lance.png")))
        tries = [F.pose(), F.pose(crouch=1), F.pose(lance="FWD"), F.pose(lance="FWD", slide=-8),
                 F.pose(lance="BACK"), F.pose(lance="DOWN"), F.pose(far=1, lance="FWD"), F.pose(near=3),
                 F.pose(near=2), F.pose(near=1)]
        sheet([F.rig.finish(c) for c in tries], os.path.join(a.parts, f"{HERO}_tries.png"))


if __name__ == "__main__":
    main()

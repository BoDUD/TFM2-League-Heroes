#!/usr/bin/env python3
"""league_gnar's action frames, posed by hand after League's own clips frame by frame on the approved designs (the
user, 2026-10-20: 「你自己做不了吗动作帧？」 - no Codex poses; Zyra / Karthus / Vex way).

    python tools/art/rig_gnar.py --parts DIR      # each design cut into its parts, tinted, at 10x
    python tools/art/rig_gnar.py --review DIR     # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_gnar.py                  # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (the user's picks 2026-10-20, one palette, PPU 1.5; tools/art/design_gnar_model.py):
  hd/idle.png    Mini Gnar, 3/4 front, 46 x 48 (32 game px): every Mini tag (the user: Mini only 3/4).
  hd/m_idle.png  Mega Gnar, 3/4 front, 92 x 65: Mega's idle and hit (and the transform's last frames).
  hd/m_side.png  Mega Gnar side-on facing right, 109 x 66 (44 game px): every Mega action (the user: 「大纳尔可以做完全侧面的」).
How the poses are made:
  * Mini: the design's own squares moved by whole squares - the head one block, never turned; the near arm with its
    boomerang turned only by quarter turns about the shoulder; the legs stepping whole (league_braum's walk).
  * Mega: the head is always the design's own squares, upright, carried to where the neck goes. The upper body (torso,
    crests, near arm, tail root) is turned about the hips by drawing it again from Codex's own full-size drawing
    (codex_model/raw/gnar-model-SM-2.png) turned at that angle and brought back to the design's grid and colours (the
    PPU redo's Design.turned: nothing is turned on the coarse grid), so League's rear-ups, slams and lunges keep every
    proportion; the near arm swings the same way about its shoulder, the chest behind it filled with the torso's own
    fur when it leaves; the hind legs stand as drawn; the run steps the four limbs below the belly whole (league_chogath).
  * Mega's death: League swaps in Mini's body when Mega dies (GnarBig_Death is a 0.27 s near-still clip): Mega slumps,
    flashes and Mini's death plays on.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "gnar"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "gnar")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "hd", name))).convert("RGBA")).copy()


def poly(pts, shape):
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=1, outline=1)
    return np.asarray(img, bool)


def is_fur(a):
    """Mega's crimson fur (red well over green and blue) - what the chest behind the near arm is painted from."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (a[..., 3] > 0) & (r > g + 50) & (r > b + 25)


def is_crest(a):
    """Mega's electric-blue crests."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (a[..., 3] > 0) & (b > r + 60) & (b > 120)


def turn_pt(p, c, deg):
    """Point p turned deg degrees counter-clockwise on screen (y down) about c."""
    t = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(t) + y * math.sin(t), c[1] - x * math.sin(t) + y * math.cos(t))


# ------------------------------------------------------------------------------------------------- the forms
class Form:
    """A design cut into named parts (masks over its squares); `stand` = the column the unit stands on (the frame's
    centre: the game centres his health bar and every effect on him there)."""

    def __init__(self, name, file, stand, parts):
        self.name = name
        self.d = load(file)
        self.H, self.W = self.d.shape[:2]
        self.stand = stand
        op = self.d[..., 3] > 0
        self.masks = {}
        taken = np.zeros(op.shape, bool)
        for pname, spec in parts:
            m = (spec(self) if callable(spec) else poly(spec, op.shape)) & op & ~taken
            self.masks[pname] = m
            taken |= m
        self.masks["body"] = op & ~taken

    def layer(self, *names, mask=None):
        m = np.zeros((self.H, self.W), bool) if mask is None else mask.copy()
        for n in names:
            m |= self.masks[n]
        out = np.zeros_like(self.d)
        out[m] = self.d[m]
        return out


def cols_mask(f, x0, x1):
    m = np.zeros((f.H, f.W), bool)
    m[:, max(0, x0):x1 + 1] = True
    return m


def rows_mask(f, y0, y1, x0=0, x1=None):
    m = np.zeros((f.H, f.W), bool)
    m[max(0, y0):y1 + 1, max(0, x0):(f.W if x1 is None else x1 + 1)] = True
    return m


# Mini Gnar (hd/idle.png, 46 x 48): the head with its ears and skull cap is rows 0-26; the tail curls out behind (image
# left) at rows 27-40 with its blue tip on the left edge; the near arm (the image-left one, his right) hangs from the
# shoulder at row 33 and its hand (rows 37-41) holds the boomerang, which runs down-left to the ground (rows 39-47);
# the far arm hangs at the right side (cols 34-40); the legs stand under the loincloth from row 40.
MINI_PARTS = [
    ("head", lambda f: rows_mask(f, 0, 26)),
    ("near_arm", [(16, 32), (24, 32), (24, 37), (23, 41), (17, 42), (15, 37)]),
    ("boomerang", [(1, 39), (15, 38), (21, 40), (19, 43), (13, 45), (7, 48), (1, 48)]),
    ("tail", [(0, 27), (18, 27), (18, 33), (17, 40), (13, 41), (6, 41), (0, 35)]),
    ("far_arm", [(34, 32), (42, 32), (42, 42), (36, 42), (34, 38)]),
    ("near_leg", [(18, 40), (26, 40), (27, 48), (18, 48)]),
    ("far_leg", [(32, 39), (38, 39), (38, 48), (27, 48), (27, 43), (32, 43)]),
]
MINI_SHOULDER = (20.0, 33.0)
MINI_GRIP = (20.0, 41.0)        # the hand's middle on the boomerang (square edges)
MINI_FACE = (252, 149, 26)      # the face's orange round the eyes
# each eye's box with its dark ring (rows, cols) and its shut lid: a line curving down across the eye's middle
MINI_EYES = [((15, 21, 20, 27), [(17, 20), (18, 21), (19, 22), (19, 23), (19, 24), (19, 25), (18, 26), (17, 27)]),
             ((15, 20, 32, 37), [(17, 32), (18, 33), (19, 34), (19, 35), (18, 36), (17, 37)])]
# Mega Gnar 3/4 (hd/m_idle.png, 92 x 65): the fists and feet stand on rows 56 down while he breathes
MEGA34_PARTS = [("feet", lambda f: rows_mask(f, 56, f.H - 1))]
# Mega Gnar side (hd/m_side.png, 109 x 66): the head (with its crests, skull, eye, tusk and jaw) at the front right;
# the near front arm a big pillar in the middle from the shoulder (row ~25) to the fist on the ground; the far front
# arm under the jaw; the hind legs at the back; the spiky tail out to the image left.
MEGA_PARTS = [
    ("head", [(74, 4), (99, 3), (109, 18), (109, 47), (99, 49), (86, 49), (78, 42), (72, 30), (71, 11)]),
    ("near_arm", [(46, 31), (52, 25), (70, 24), (76, 29), (77, 40), (76, 58), (74, 66), (51, 66), (50, 50), (48, 40)]),
    ("far_arm", [(73, 39), (84, 35), (96, 45), (97, 60), (77, 60), (73, 50)]),
    ("near_hind", [(16, 39), (31, 37), (37, 44), (36, 55), (28, 63), (11, 63), (11, 53), (16, 46)]),
    ("far_hind", [(32, 45), (46, 45), (50, 48), (50, 59), (37, 59), (32, 51)]),
    ("tail", [(0, 13), (11, 13), (27, 29), (27, 41), (15, 45), (0, 36)]),
]
HIP = (33.0, 45.0)              # the upper body turns about this point (above the hind legs)
SHOULDER = (62.0, 28.0)         # the near arm's
ELBOW = (63.0, 45.0)            # where it bends (the upper arm with its crests above, the forearm and fist below)
ELBOW_LAP = 3                   # rows each half reaches past the elbow (they overlap there: no gap at the joint)
NECK = (77.0, 30.0)             # where the head sits on the torso
RUMP = (26.0, 36.0)             # where the tail grows
BELLY = 45                      # rows above this, behind the near arm, are chest (filled when the arm leaves)
FORE_ROW = {"near_fore": 48, "far_fore": 50}   # the run steps each front limb from this row down (forearm and fist)
HIND_CUT = {"near_hind": 49, "far_hind": 51}   # and each hind leg from its knee down (shin and paw)
SHIN_COLS = {"near_hind": 26, "far_hind": 99}  # the near shin is the violet leg left of this column (the haunch's red
KNEE_BAND = 4                                  # lower edge and its back edge stay put); its top rows fill the knee
FUR_STEP = 19                   # the chest fill copies the torso's fur this many columns to its left
NECK_BAND = 84                  # head fur and crest squares up to this column (behind the eye) go with the body too


# ------------------------------------------------------------------------------------------------- Codex's drawing
class Turner:
    """Mega's side design drawn again from Codex's own picture at any angle: the design square (x, y) is the read-back's
    (cols[x], rows[y]) (design_gnar_model's cut: rows 12 / 44 / 60 and five columns dropped), the read-back's squares
    are the picture's cells (regrid's edges)."""

    def __init__(self, form):
        import design_gnar_model as G
        import regrid as RG
        self.f = form
        col = G.joint(list(G.PICKS.values()))
        fig, self.rows, self.cols = G.cut("SM-2", col["SM-2"])
        if fig.shape != form.d.shape or not (fig == form.d).all():
            sys.exit("hd/m_side.png is not design_gnar_model's cut of SM-2 any more")
        pic = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", "raw", "gnar-model-SM-2.png"))).convert("RGBA"))
        rb, self.sq, (self.bx, self.by) = RG.regrid(pic.copy(), 11.0)
        self.pic = pic.copy()
        self.pic[..., 3] = np.where(self.pic[..., 3] >= 128, 255, 0)
        self.pic[self.pic[..., 3] == 0] = 0
        self.pal = np.unique(form.d[form.d[..., 3] > 0][:, :3], axis=0).astype(float)
        self.outline = PD.edge_colour(form.d)
        # the design is the read-back less 3 of 69 rows and 5 of 114 columns: turned parts are brought to its own size
        self.k = (len(self.rows) / (max(self.rows) + 1) + len(self.cols) / (max(self.cols) + 1)) / 2 / self.sq
        self._cache = {}
        self.filled = self.chest_filled()

    def d2p(self, x, y):
        def axis(v, kept, edges):
            i = max(0, min(len(kept) - 1, int(math.floor(v))))
            f = v - math.floor(v) if 0 <= v < len(kept) else (v - i)
            a, b = edges[kept[i]], edges[min(kept[i] + 1, len(edges) - 1)]
            return a + f * (b - a)
        return axis(x, self.cols, self.bx), axis(y, self.rows, self.by)

    def pmask(self, dmask):
        Hr, Wr = len(self.by) - 1, len(self.bx) - 1
        rm = np.zeros((Hr, Wr), bool)
        rm[np.ix_(self.rows, self.cols)] = dmask
        kr, kc = set(self.rows), set(self.cols)
        for r in range(1, Hr):
            if r not in kr:
                rm[r] |= rm[r - 1]
        for c in range(1, Wr):
            if c not in kc:
                rm[:, c] |= rm[:, c - 1]
        m = np.zeros(self.pic.shape[:2], bool)
        for r in range(Hr):
            y0, y1 = int(round(self.by[r])), int(round(self.by[r + 1]))
            for c in np.nonzero(rm[r])[0]:
                m[y0:y1, int(round(self.bx[c])):int(round(self.bx[c + 1]))] = True
        return m

    def chest_filled(self):
        """The picture with the chest behind the near arm painted from the torso's own fur FUR_STEP columns to its
        left (twice that where the first copy falls in the arm too)."""
        f = self.f
        hole = f.masks["near_arm"] & rows_mask(f, 0, BELLY - 1)
        hp = self.pmask(hole)
        body = self.pmask(f.masks["body"]) & (self.pic[..., 3] > 0)
        out = self.pic.copy()
        step = int(round(FUR_STEP * self.sq))
        ys, xs = np.nonzero(hp)
        fur = body & is_fur(self.pic)
        for k in (1, 2, 3, 4):
            sx = xs - k * step
            ok = (sx >= 0) & fur[ys, np.clip(sx, 0, None)]
            out[ys[ok], xs[ok]] = self.pic[ys[ok], sx[ok]]
            keep = ~ok
            ys, xs = ys[keep], xs[keep]
            if not len(ys):
                break
        return out

    def turned(self, dmask, angle, about, filled=False):
        """The part (design-square mask) turned `angle` degrees counter-clockwise about design point `about`, drawn
        from the picture and brought to the design's grid and colours -> (squares, the grid index of `about`)."""
        key = (dmask.tobytes(), round(angle, 2), about, filled)
        if key in self._cache:
            return self._cache[key]
        src_pic = self.filled if filled else self.pic
        if filled:                                       # the painted chest goes with the part
            dmask = dmask | (self.f.masks["near_arm"] & rows_mask(self.f, 0, BELLY - 1))
        m = self.pmask(dmask) & (src_pic[..., 3] > 0)
        src = np.zeros_like(src_pic)
        src[m] = src_pic[m]
        P = 700
        big = np.pad(src, ((P, P), (P, P), (0, 0)))
        ax, ay = self.d2p(*about)
        rot = np.asarray(Image.fromarray(big).rotate(angle, resample=Image.BICUBIC, center=(ax + P, ay + P))).copy()
        rot[..., 3] = np.where(rot[..., 3] >= 128, 255, 0)
        rot[rot[..., 3] == 0] = 0
        g, n0 = PD.pixelate(rot, self.k, (ax + P, ay + P), self.outline, self.pal)
        g = R.snap(g, self.pal)
        g[..., 3] = np.where(g[..., 3] > 0, 255, 0)
        self._cache[key] = (g, n0)
        return g, n0


# ------------------------------------------------------------------------------------------------- the canvas
class Canvas:
    """Every frame of both forms on one canvas: the pivot column CX, the ground row GY (ppu_rig.Rig's)."""

    def __init__(self):
        self.mini = Form("mini", "idle.png", 28, MINI_PARTS)
        self.m34 = Form("m34", "m_idle.png", 46, MEGA34_PARTS)
        self.mega = Form("mega", "m_side.png", 55, MEGA_PARTS)
        self.T = Turner(self.mega)
        base = R.Rig.__new__(R.Rig)
        side = self.mega

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, side.d
            H, W, px, ground = side.H, side.W, side.stand, side.H
            outline = PD.edge_colour(side.d)
        self.rig = R.Rig(D, pad=(40, 40, 70, 12))
        self.outline = D.outline

    def blank(self):
        return self.rig.canvas()

    def origin(self, f):
        """Canvas square of design (0, 0) for a form standing on the pivot."""
        return self.rig.CX - f.stand, self.rig.GY - f.H

    def stamp(self, can, f, lay, dx=0, dy=0, rot=0, flip=False, about=None, under=False):
        ox, oy = self.origin(f)
        ab = None if about is None else (about[0] + ox, about[1] + oy)
        big = np.zeros(can.shape, np.uint8)
        big[oy:oy + f.H, ox:ox + f.W] = lay
        R.put(can, big, dx=dx, dy=dy, rot=rot, flip=flip, about=ab, under=under)
        return can

    def paste_grid(self, can, f, g, n0, at, dx=0, dy=0):
        """A turned part (squares g, its pivot cell corner n0) with that corner on design point `at` of form f."""
        ox, oy = self.origin(f)
        ys, xs = np.nonzero(g[..., 3] > 0)
        tx = xs - n0[0] + int(round(at[0] + ox)) + dx
        ty = ys - n0[1] + int(round(at[1] + oy)) + dy
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        can[ty[ok], tx[ok]] = g[ys[ok], xs[ok]]
        return can

    def finish(self, can):
        out = can.copy()
        out[self.rig.GY:] = 0
        return out


# ------------------------------------------------------------------------------------------------- Mini's poses
def closed_eyes(head):
    """The head with both eyes shut: each eye's squares painted over with the face's own orange and a near-black lid
    line curving down across its middle (League's death and hurt frames shut them)."""
    out = head.copy()
    for (r0, r1, c0, c1), lid in MINI_EYES:
        out[r0:r1 + 1, c0:c1 + 1, :3] = MINI_FACE
        out[r0:r1 + 1, c0:c1 + 1, 3] = 255
        for y, x in lid:
            out[y, x, :3] = (3, 1, 3)
    return out


def mini(C, arm="rest", lift=0, dx=0, lean=0, legs=None, sink=0, tail_dy=0, boomerang=True, flash=False,
         eyes_closed=False):
    """Mini Gnar: arm = the near arm with its boomerang - "rest" (as drawn: the boomerang trailing behind him), "swing"
    (the boomerang swung round low across his front: mirrored about the hand), "front" (the arm a quarter turn
    counter-clockwise about the shoulder: flung out in front, the hand empty - his head hides anything raised behind
    it, so League's wind-up over the shoulder is a lean back); lift = rows off the ground; lean = the upper body's columns ahead of the legs; legs
    = {leg: (dx, dy)} each leg moved whole (dy < 0 lifts it; its top hides under the loincloth); sink = the upper body
    set down onto the legs (breathing); boomerang False: the hand empty in every arm pose."""
    f = C.mini
    can = C.blank()
    legs = legs or {}
    up = -lift
    ux, uy = dx + lean, up + sink
    # back to front: the far leg, the far arm, the tail, the body, the head, the near leg, the near arm
    lx, ly = legs.get("far_leg", (0, 0))
    C.stamp(can, f, f.layer("far_leg"), dx + lx, up + ly)
    C.stamp(can, f, f.layer("far_arm"), ux, uy)
    C.stamp(can, f, f.layer("tail"), ux, uy + tail_dy)
    C.stamp(can, f, f.layer("body"), ux, uy)
    lx, ly = legs.get("near_leg", (0, 0))
    C.stamp(can, f, f.layer("near_leg"), dx + lx, up + ly)
    if arm == "rest":
        if boomerang:                                     # always with the hand that holds it
            C.stamp(can, f, f.layer("boomerang"), ux, uy)
        C.stamp(can, f, f.layer("near_arm"), ux, uy)
    elif arm == "swing":
        # the boomerang swung round to the front, low across his legs: mirrored about the hand's middle
        C.stamp(can, f, f.layer("near_arm"), ux, uy)
        if boomerang:
            C.stamp(can, f, f.layer("boomerang"), ux, uy, flip=True, about=MINI_GRIP)
    elif arm == "front":
        C.stamp(can, f, f.layer("near_arm"), ux, uy, rot=1, about=MINI_SHOULDER)
    head = f.layer("head")
    C.stamp(can, f, closed_eyes(head) if eyes_closed else head, ux, uy)
    can = seal(C.finish(can), C.outline)
    return R.flash(can) if flash else can


def mini_lying(C, sink=2, bounce=0):
    """Mini lying on his back, head to the image left (the whole figure a quarter turn counter-clockwise), his eyes shut
    (League's death closes them), the boomerang dropped flat on the ground in front of him."""
    stand = mini(C, boomerang=False, eyes_closed=True)
    lie = R.lie(C.rig, stand, k=1, dx=-2, sink=sink - bounce)
    f = C.mini
    boom = f.layer("boomerang")
    ys, xs = np.nonzero(boom[..., 3] > 0)
    sub = boom[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    flat = np.fliplr(sub)                                # lying the other way, its head forward
    h, w = flat.shape[:2]
    y0 = C.rig.GY - h + 1
    x0 = C.rig.CX + 12
    region = lie[y0:y0 + h, x0:x0 + w]
    m = (flat[..., 3] > 0) & (region[..., 3] == 0)
    region[m] = flat[m]
    return C.finish(lie)


def mini_heap(C, sink=0, bounce=0):
    """Mini collapsed (League's death ends with him flat on the ground): his head, eyes shut and upright, down on the
    ground with the body sunk out of sight behind it; the tail flat behind him, the legs out in front of him, the
    boomerang dropped beside them."""
    f = C.mini
    can = C.blank()
    head = closed_eyes(f.layer("head"))
    down = f.H - 27 + sink - bounce                     # the chin (row 26) onto the ground row
    C.stamp(can, f, f.layer("tail"), -6, f.H - 41 - bounce)
    # the legs out in front, flat on the ground: each a quarter turn counter-clockwise (the feet point forward)
    for leg, x in (("far_leg", 15), ("near_leg", 12)):
        lay = f.layer(leg)
        ys, xs = np.nonzero(lay[..., 3] > 0)
        piece = lay[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        flat = np.rot90(piece, 1)
        h, w = flat.shape[:2]
        y0, x0 = C.rig.GY - h, C.rig.CX + x
        region = can[y0:y0 + h, x0:x0 + w]
        m = flat[..., 3] > 0
        region[m] = flat[m]
    C.stamp(can, f, f.layer("body"), 0, down + 2)
    C.stamp(can, f, head, 0, down)
    boom = f.layer("boomerang")
    ys, xs = np.nonzero(boom[..., 3] > 0)
    flat = np.fliplr(boom[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    h, w = flat.shape[:2]
    y0, x0 = C.rig.GY - h, C.rig.CX + 22
    region = can[y0:y0 + h, x0:x0 + w]
    m = (flat[..., 3] > 0) & (region[..., 3] == 0)
    region[m] = flat[m]
    return seal(C.finish(can), C.outline)


# ------------------------------------------------------------------------------------------------- Mega's poses
def mega(C, theta=0.0, arm=None, dx=0, lift=0, tail_dy=0, legs=None, flash=False, boulder=None):
    """Mega Gnar side-on: theta = the upper body turned that many degrees counter-clockwise about the hips (> 0 rears
    up, < 0 pitches the head down); arm = the near arm's own turns on top of theta - (upper, fore): the upper arm about
    the shoulder, the forearm with the fist a further turn about the elbow (a number: straight) - or None (it goes with
    the body as drawn); dx / lift = the whole figure moved; legs = {limb: (dx, dy)} for the run (each limb below the
    belly moved whole)."""
    f, T = C.mega, C.T
    can = C.blank()
    up = -lift
    legs = legs or {}
    m = f.masks
    upper = m["body"] | m["far_arm"] | (m["near_arm"] if arm is None else np.zeros_like(m["body"]))
    # the body reaches under the back of the head (its crests and mane behind the ear): the head pasted over it hides
    # the joint at every angle - cut at the head's own edge, the turned body showed a dark edge and a gap there
    upper = upper | (m["head"] & cols_mask(f, 0, NECK_BAND) & (is_fur(f.d) | is_crest(f.d)))
    neck = turn_pt(NECK, HIP, theta)
    rump = turn_pt(RUMP, HIP, theta)
    sh = turn_pt(SHOULDER, HIP, theta)
    # back to front: the far hind leg, the tail, the upper body (torso, crests, far arm[, near arm]), the near hind
    # leg, the head, the near arm
    fore = {k: legs[k] for k in ("near_fore", "far_fore") if k in legs}
    cut = {"near_fore": m["near_arm"] & rows_mask(f, FORE_ROW["near_fore"], f.H - 1),
           "far_fore": m["far_arm"] & rows_mask(f, FORE_ROW["far_fore"], f.H - 1)}
    for k in fore:
        upper = upper & ~cut[k]
    def fore_limb(k):
        # the forearm stepped: its top KNEE_BAND rows laid on every square between the arm and where it steps, so a
        # forearm planted on the ground while the body bobs up never leaves a gap at the elbow (the knee's way)
        lx, ly = fore[k]
        band = cut[k] & rows_mask(f, FORE_ROW[k], FORE_ROW[k] + KNEE_BAND - 1)
        steps = max(abs(lx), abs(ly))
        for t in range(steps):
            C.stamp(can, f, f.layer(mask=band), dx + int(round(lx * t / steps)), up + int(round(ly * t / steps)))
        C.stamp(can, f, f.layer(mask=cut[k]), dx + lx, up + ly)

    hind(C, can, f, "far_hind", legs, dx, up)
    if "far_fore" in fore:
        fore_limb("far_fore")
    C.stamp(can, f, f.layer("tail"), dx + int(round(rump[0] - RUMP[0])), up + int(round(rump[1] - RUMP[1])) + tail_dy)
    if theta == 0 and arm is None:
        C.stamp(can, f, f.layer(mask=upper), dx, up)
    elif theta == 0:
        lay = f.layer(mask=upper)
        lay = chest_fill(f, lay)
        C.stamp(can, f, lay, dx, up)
    else:
        g, n0 = T.turned(upper, theta, HIP, filled=arm is not None)
        C.paste_grid(can, f, g, n0, HIP, dx, up)
    hind(C, can, f, "near_hind", legs, dx, up)
    head = m["head"]
    nx, ny = dx + int(round(neck[0] - NECK[0])), up + int(round(neck[1] - NECK[1]))
    if theta:                                          # the head's back edge (the red fur in its first three squares of
        edge = np.zeros_like(head)                     # each row, where it met the body's) is left to the turned body:
        for r in np.nonzero(head.any(1))[0]:           # laid over it, a red strip stood in the turned crests; seal
            c0 = int(np.argmax(head[r]))               # fills a gap it leaves from its neighbours
            edge[r, c0:c0 + 3] = head[r, c0:c0 + 3]
        head = head & ~(edge & is_fur(f.d))
    C.stamp(can, f, f.layer(mask=head), nx, ny)
    if arm is not None:
        a1, a2 = (arm, 0) if not isinstance(arm, tuple) else arm
        p1 = theta + a1                                  # the upper arm's direction (0 down, > 0 forward)
        p2 = p1 + a2                                     # the forearm's
        el = turn_pt(ELBOW, SHOULDER, p1)
        el = (el[0] + sh[0] - SHOULDER[0], el[1] + sh[1] - SHOULDER[1])
        upper_arm = m["near_arm"] & rows_mask(f, 0, int(ELBOW[1]) + ELBOW_LAP - 1)
        fore_arm = m["near_arm"] & rows_mask(f, int(ELBOW[1]) - ELBOW_LAP, f.H - 1)
        g, n0 = T.turned(upper_arm, p1, SHOULDER)
        C.paste_grid(can, f, g, n0, sh, dx, up)
        g, n0 = T.turned(fore_arm, p2, ELBOW)
        C.paste_grid(can, f, g, n0, el, dx, up)
    if "near_fore" in fore:
        fore_limb("near_fore")
    can = seal(C.finish(can), C.outline)
    if not lift and not legs:                          # the run keeps the design's own ground (its paws' perspective)
        can = grounded(C, can)
    return R.flash(can) if flash else can


def shin(f, name):
    """The part of a hind leg the run steps: from HIND_CUT down, the near leg's violet shin, ivory claws and the outline
    round them (left of SHIN_COLS) - cut by rows alone, the red haunch's lower edge went with it and left a strip of
    haunch hanging and a seam across it (the user's crop, 「看到这里了没」); the far leg is violet all through."""
    m = f.masks[name] & rows_mask(f, HIND_CUT[name], f.H - 1) & cols_mask(f, 0, SHIN_COLS[name])
    if name == "far_hind":
        return m
    r, g, b = (f.d[..., i].astype(int) for i in range(3))
    core = m & (((b > r) & (b > g)) | ((r > 150) & (g > 120)))
    dark = (r + g + b) < 90
    return core | (m & dark & ndimage.binary_dilation(core, iterations=1))


def hind(C, can, f, name, legs, dx, up):
    """A hind leg: as drawn, or in the run its shin and paw stepped under the thigh, which stays on the hip and is
    drawn over the shin's top (lifted, the shin tucks in under it: league_braum's walk); the shin's top KNEE_BAND rows
    are laid on every square between where it was drawn and where it steps, so the knee shows the shin, never a hole -
    the whole leg stepping slid the thigh against the hip (「大纳尔走路的时候后腿有点变形」)."""
    m = f.masks[name]
    if name not in legs:
        C.stamp(can, f, f.layer(name), dx, up)
        return
    lx, ly = legs[name]
    low = shin(f, name)
    top = int(np.nonzero(low.any(1))[0].min())
    knee = low & rows_mask(f, top, top + KNEE_BAND - 1)
    steps = max(abs(lx), abs(ly))
    for t in range(steps):
        C.stamp(can, f, f.layer(mask=knee), dx + int(round(lx * t / steps)), up + int(round(ly * t / steps)))
    C.stamp(can, f, f.layer(mask=low), dx + lx, up + ly)
    C.stamp(can, f, f.layer(mask=m & ~low), dx, up)


def grounded(C, can):
    """The frame moved up or down so its lowest square stands on the ground row: the side design draws the hind paws a
    few rows above the fist (they are farther back), so a rear-up lifting the fist off the ground left him hovering,
    and a slam pushing it lower went into the ground."""
    ys = np.nonzero((can[..., 3] > 0).any(1))[0]
    d = (C.rig.GY - 1) - int(ys.max())
    if d == 0:
        return can
    out = np.zeros_like(can)
    if d > 0:
        out[d:] = can[:-d]
    else:
        out[:d] = can[-d:]
    return out


POSES = os.path.join(SRC, "poses")
_POSE = {}


def pose(C, name, lift=0, dx=0, flash=False):
    """One of Codex's key poses (tools/art/read_gnar_poses.py: on the design's squares, its head the design's) as a
    frame: the lowest square on the ground row (lift rows over it); across, Mega by the drawing's middle of mass on the
    side design's (the body stays over his standing point), Mini by his head on the design's (one face in all frames)."""
    if name not in _POSE:
        a = np.asarray(Image.open(lp(os.path.join(POSES, f"{name}.png"))).convert("RGBA")).copy()
        _POSE[name] = a
    a = _POSE[name]
    f = C.mega if name.startswith("m_") else C.mini
    ox, oy = C.origin(f)
    if f is C.mini:                                          # Mini: the head where the design's is (his tail and the
        if "fit" not in _POSE:                               # boomerang reach far out behind him in the poses)
            with open(lp(os.path.join(POSES, "pose_fit.json")), encoding="utf-8") as fh:
                _POSE["fit"] = json.load(fh)
        x0 = ox + 6 - _POSE["fit"][name]["head_at"][0] + dx  # the 3/4 head's box starts at the design's column 6
    else:
        fx = np.nonzero(f.d[..., 3] > 0)[1].mean() + ox        # Mega: the design's middle of mass on the canvas
        px = np.nonzero(a[..., 3] > 0)[1].mean()
        x0 = int(round(fx - px)) + dx
    y0 = C.rig.GY - a.shape[0] - lift
    can = C.blank()
    big = np.zeros(can.shape, np.uint8)
    big[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    R.put(can, big)
    can = seal(C.finish(can), C.outline)
    return R.flash(can) if flash else can


def seal(can, outline, speck=8):
    """Cracks a turned part leaves against the untouched ones closed: a clear square with drawn squares on both sides
    of it (left and right, or above and below, within 2) inside the figure takes its neighbours' colour (not the
    outline's); enclosed holes up to 12 squares likewise; loose specks under `speck` squares dropped."""
    out = can.copy()
    for _ in range(2):
        op = out[..., 3] > 0
        hole = np.zeros(op.shape, bool)
        crack1 = np.zeros(op.shape, bool)
        for d in (1, 2):
            l, r = np.roll(op, d, 1), np.roll(op, -d, 1)
            u, dn = np.roll(op, d, 0), np.roll(op, -d, 0)
            hole |= (l & r) | (u & dn)
            if d == 1:
                crack1 = ((l & r) & (u | dn)) | ((u & dn) & (l | r))
        hole &= ~op
        crack1 &= ~op
        filled = ndimage.binary_fill_holes(op)
        lbl, n = ndimage.label(filled & ~op)
        small = np.zeros(op.shape, bool)
        for j in range(1, n + 1):
            mj = lbl == j
            if mj.sum() <= 12:
                small |= mj
        todo = (hole & ndimage.binary_dilation(op, iterations=1) & filled) | small | crack1
        if not todo.any():
            break
        out = R.fill_under(out, todo)
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for j in range(1, n + 1):
            if sz[j - 1] < speck:
                out[lbl == j] = 0
    return out


def chest_fill(f, lay):
    """The chest behind the near arm (gone from its place) painted from the torso's own fur FUR_STEP columns left."""
    hole = f.masks["near_arm"] & rows_mask(f, 0, BELLY - 1)
    out = lay.copy()
    body = f.masks["body"] & is_fur(f.d)
    ys, xs = np.nonzero(hole)
    for k in (1, 2, 3, 4):
        sx = xs - k * FUR_STEP
        ok = (sx >= 0) & body[ys, np.clip(sx, 0, None)]
        out[ys[ok], xs[ok]] = f.d[ys[ok], sx[ok]]
        ys, xs = ys[~ok], xs[~ok]
        if not len(ys):
            break
    return out


def m34(C, sink=0, dx=0, flash=False):
    """Mega Gnar 3/4 (the idle): everything but the fists and feet set down `sink` rows."""
    f = C.m34
    can = C.blank()
    C.stamp(can, f, f.layer("feet"), dx, 0)
    C.stamp(can, f, f.layer("body"), dx, sink)
    can = C.finish(can)
    return R.flash(can) if flash else can


# ------------------------------------------------------------------------------------------------- the tags
# ms per frame (the kit's ticks come from these)
MS = {
    "idle": [150] * 8, "run": [90] * 8,
    "attack": [70, 80, 80, 80, 90], "skill": [70, 80, 80, 80, 80, 80, 100], "skill2": [60, 60, 70, 80, 70, 60, 60, 60],
    "hit": [100, 100], "dead": [100, 120, 150, 60, 500],
    "transform": [60, 60, 60, 70, 80, 120], "revert": [70, 80, 80, 80, 120],
    "m_idle": [150] * 8, "m_run": [100] * 8, "m_hit": [100, 100], "m_dead": [100, 100, 100, 150, 60, 500],
    "m_attack": [70, 80, 90, 90, 80, 90], "m_skill": [90, 90, 100, 90, 80, 100],
    "m_skill2": [70, 70, 80, 80, 70, 80, 70, 60], "m_wallop": [80, 90, 100, 90, 90, 100], "ult": [80, 80, 90, 90, 90, 80],
}
SINK = [0, 0, 1, 1, 1, 1, 0, 0]
# Mini breathes up: everything above the legs rises a row (set down, the boomerang's tip went into the ground and the
# hand slid along it - 「小纳尔的上下摆动导致武器变形了」)
MINI_SINK = [0, 0, -1, -1, -1, -1, 0, 0]
# Mini's step (league_braum's walk, small): each leg's column offset and lift round the cycle, the body's bob
M_STRIDE = [2, 1, 0, -1, -2, -1, 0, 1]
M_LIFT = [0, 0, 0, 0, 1, 3, 3, 1]
M_HOP = [0, 1, 2, 1, 0, 1, 2, 1]
M_TAIL = [0, 0, -1, -1, 0, 0, -1, -1]
# Mega's gallop (league_chogath's walk): the fists' steps; the hind shins' under the thighs. The first strides (1-3
# squares, no bob) read stiff in game (the user: 「大纳尔的后腿走路有点问题吧 和僵尸一样」「走路的时候 僵硬无比」): twice
# as long, the body bobbing G_BOB squares (two bounces a cycle, up as the pairs push off) over legs that stay on the
# ground while planted (each limb's lift minus the bob)
G_STRIDE = [4, 2, -2, -6, -4, 0, 4, 6]
G_LIFT = [0, 0, 0, 0, 3, 5, 4, 2]
G_SURGE = [0, 0, 1, 1, 0, 0, 1, 1]
H_STRIDE = [2, 2, 0, -2, -4, -2, 0, 2]
H_LIFT = [0, 0, 0, 0, 2, 4, 3, 1]
G_BOB = [0, 1, 2, 1, 0, 1, 2, 1]


def frames_all(C):
    out = {}
    out["idle"] = [mini(C, sink=s) for s in MINI_SINK]
    # the run (League's Gnar_Run1: a bouncing scamper - two hops a cycle, a leg stepping with each, the tail bobbing)
    run = []
    for i in range(8):
        j = (i + 4) % 8
        run.append(mini(C, legs={"near_leg": (M_STRIDE[i], -M_LIFT[i]), "far_leg": (M_STRIDE[j], -M_LIFT[j])},
                        lift=M_HOP[i], lean=1, tail_dy=M_TAIL[i]))
    out["run"] = run
    # attack (League's Gnar_Attack1: the boomerang held across him, drawn back behind as he gathers, flung with a little
    # hop - it leaves on frame 3 - and he lands)
    # Codex's key poses (POSE_PROMPTS.md, the user: 「感觉大小纳尔少了点动作帧啊 要不要codex补啊」): the wind-up behind
    # him, the fling with the hand empty (frame 3, the boomerang's release)
    out["attack"] = [mini(C), pose(C, "a_windup"), pose(C, "a_throw", lift=2), pose(C, "a_throw"), mini(C)]
    # Q Boomerang Throw (League's Gnar_Spell1: across him, drawn back deep, the throw on frame 4 and a hop after it)
    out["skill"] = [mini(C, arm="swing"), pose(C, "a_windup"), pose(C, "a_windup", dx=-1), pose(C, "a_throw", lift=3),
                    pose(C, "a_throw", lift=6), mini(C, lift=3, boomerang=False), mini(C)]
    # Hop: a crouch, tucked up in the air, the landing crouch
    out["skill2"] = [pose(C, "a_crouch"), pose(C, "a_hop", lift=4), pose(C, "a_hop", lift=9), pose(C, "a_hop", lift=11),
                     pose(C, "a_hop", lift=9), pose(C, "a_hop", lift=4), pose(C, "a_crouch"), mini(C)]
    out["hit"] = [mini(C, dx=-2, flash=True), mini(C, dx=-1)]
    # dead (League's Gnar_Death: hit, eyes shut, the boomerang flies off, he drops flat on the ground)
    out["dead"] = [mini(C, dx=-1, eyes_closed=True), mini(C, dx=-2, lift=2, boomerang=False, eyes_closed=True),
                   mini_heap(C, bounce=2), mini_heap(C, bounce=1), mini_heap(C)]
    # the transform (League's Gnar_IdleRage then GnarBig_Rage_stop): Mini shakes with rage, flashes, Mega stands there
    out["transform"] = [mini(C), mini(C, dx=1), mini(C, dx=-1), mini(C, flash=True), m34(C, flash=True), m34(C)]
    # back to Mini (League's Gnar_Revert): Mega flashes, Mini pops out and lands
    out["revert"] = [m34(C), m34(C, flash=True), mini(C, lift=3, flash=True), mini(C, lift=1), mini(C)]

    out["m_idle"] = [m34(C, sink=s) for s in SINK]
    mrun = []
    for i in range(8):
        j = (i + 4) % 8
        bob = G_BOB[i]
        a, b = (G_STRIDE[i], bob - G_LIFT[i]), (G_STRIDE[j], bob - G_LIFT[j])
        ha, hb = (H_STRIDE[i], bob - H_LIFT[i]), (H_STRIDE[j], bob - H_LIFT[j])
        mrun.append(mega(C, dx=G_SURGE[i], lift=bob,
                         legs={"near_hind": ha, "far_fore": a, "far_hind": hb, "near_fore": b}))
    out["m_run"] = mrun
    out["m_hit"] = [m34(C, dx=-2, flash=True), m34(C, dx=-1)]
    out["m_dead"] = [mega(C, theta=-6), mega(C, theta=-8, flash=True), mini(C, flash=True)] + out["dead"][2:]
    # theta turns the whole upper body - torso, crests and both front arms as Codex drew them - counter-clockwise about
    # the hips (> 0 rears up, the near fist coming up and forward in front of his chest; < 0 pitches him down onto it).
    # The arms are never turned against the body: a raised arm cut from it left a seam at the shoulder and met his head
    # (the user: 「手臂有点不自然啊 身体还断开」「这手臂都绑在头上了？」「这里还是断开 修不好吗」); rearing up and coming down
    # onto all fours swings the fist up and down by itself.
    # attack (League's GnarBig_Attack1: up on the hind legs, claws high - then down onto all fours, the fist slamming
    # the ground ahead on frame 4)
    # Codex's key poses take the moves the body turn alone could not (the arms): the fist lifted behind the head, the
    # slam onto both fists, the boulder overhead, the leap, the rear-up, the lunge
    out["m_attack"] = [mega(C, theta=10), pose(C, "m_swing"), pose(C, "m_swing", dx=1), pose(C, "m_slam"),
                       pose(C, "m_slam"), mega(C, theta=-2, dx=1)]
    # Q Boulder Toss (League's GnarBig_Spell1: down to scoop the boulder, up on the hind legs with it held high, hurled
    # down and forward as he drops onto all fours on frame 4)
    out["m_skill"] = [pose(C, "m_crouch"), pose(C, "m_lift"), pose(C, "m_lift", dx=-1), pose(C, "m_lunge"),
                      mega(C, theta=3, dx=1), mega(C)]
    # E Crunch (League's GnarBig_Spell3: a crouch, a leap high up - nose up rising, level at the top, nose down falling -
    # and the landing slam on frame 6)
    out["m_skill2"] = [pose(C, "m_crouch"), pose(C, "m_leap", lift=12), pose(C, "m_leap", lift=26),
                       pose(C, "m_leap", lift=32), pose(C, "m_leap", lift=16), pose(C, "m_slam"), pose(C, "m_slam"),
                       mega(C)]
    # W Wallop (League's GnarBig_Spell2: right up on the hind legs, then the whole body thrown forward and down, the
    # fist smashing the ground ahead on frame 4)
    out["m_wallop"] = [mega(C, theta=20), pose(C, "m_rear"), pose(C, "m_rear"), pose(C, "m_slam", dx=2),
                       pose(C, "m_slam", dx=2), mega(C, theta=-2, dx=1)]
    # R GNAR! (League's GnarBig_Spell4: a crouch, a low lunge, then up on the hind legs flinging everything away - the
    # throw on frame 3)
    out["ult"] = [pose(C, "m_crouch", dx=-2), pose(C, "m_rear", dx=2), pose(C, "m_lunge", dx=4),
                  pose(C, "m_lunge", dx=5), mega(C, theta=12, dx=3), mega(C, dx=1)]
    return out


def frames(C):
    a = frames_all(C)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


TINT = {"head": (255, 255, 0), "near_arm": (0, 255, 120), "far_arm": (0, 160, 255), "near_hind": (255, 60, 60),
        "far_hind": (180, 60, 255), "tail": (255, 150, 0), "boomerang": (255, 0, 200), "near_leg": (255, 60, 60),
        "far_leg": (180, 60, 255), "feet": (0, 200, 255), "body": (128, 128, 128)}


def tinted(f, z=10):
    out = f.d.astype(float).copy()
    for n, c in TINT.items():
        if n in f.masks:
            m = f.masks[n]
            out[m, :3] = out[m, :3] * 0.45 + np.array(c) * 0.55
    big = np.repeat(np.repeat(out.astype(np.uint8), z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    C = Canvas()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        for f in (C.mini, C.m34, C.mega):
            tinted(f).save(os.path.join(a.parts, f"gnar_parts_{f.name}.png"))
            print(f.name, {k: int(v.sum()) for k, v in f.masks.items()})
        return
    acts = frames(C)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()

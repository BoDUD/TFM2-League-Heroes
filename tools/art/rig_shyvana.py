#!/usr/bin/env python3
"""league_shyvana's action frames, posed on the approved 3/4 designs after League's own clips, frame by frame (the
user, 2026-10-21: 「人形用 A-2，龙形用 D-1，龙就按画的大小，只做四分之三侧面」「做到完美后喊我review 如果有动作实在做不出
就让codex帮忙」).

    python tools/art/rig_shyvana.py --parts DIR       # each design cut into its parts, tinted, at 10x
    python tools/art/rig_shyvana.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_shyvana.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (the user's picks 2026-10-21, one palette, PPU 1.5; tools/art/design_shyvana_model.py):
  hd/idle.png    her, 3/4 front, 40 x 63 (42 game px): the idle, the hit, and the frames between Codex's key poses
                 (assets/source/shyvana/POSE_PROMPTS.md: the jumps, the flip, the throw, the leap, the fall, the run).
  hd/d_idle.png  the dragon, 3/4 front, 107 x 64 (43 game px, kept as Codex drew it): every dragon tag.
How the dragon's poses are made (rig_gnar's Mega way):
  * the head with its flame mane, the body and the legs are the design's own squares moved by whole squares; a leg that
    steps loses its top rows (league_braum's walk) or is set down whole;
  * the wings, the tail, the neck and the jaw held at another angle are drawn again from Codex's own full-size drawing
    (codex_model/raw/shyvana-model-D-1.png, 11 px squares; the design is its read-back square for square) turned at that
    angle and brought back to the design's grid and colours (Turner) - nothing is turned on the coarse grid;
  * the tail sweep (League's Spell1_Tail spins the dragon round) mirrors the whole figure for its middle frames.
"""
import argparse
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

HERO = "shyvana"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "shyvana")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "hd", name))).convert("RGBA")).copy()


def poly(pts, shape):
    """Squares whose middles lie inside the polygon (square edges)."""
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


def box(f, x0, y0, x1, y1):
    """Squares in columns x0..x1 and rows y0..y1 (inclusive)."""
    m = np.zeros((f.H, f.W), bool)
    m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
    return m


def is_flame(a):
    """The dragon's flame mane: orange and yellow (red well over blue, green over 60)."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (a[..., 3] > 0) & (r > 200) & (g > 60) & (b < 60) & (g < 200)


class Form:
    """A design cut into named parts (masks over its squares, each square in one part); `stand` = the column the unit
    stands on (the frame's centre: the game centres his health bar and every effect on him there)."""

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


# ------------------------------------------------------------------------------------------------- the dragon's parts
# hd/d_idle.png, 107 x 64 (square edges): low on four legs, facing right. The far wing (dark violet membrane, crimson
# bones, gold claw tips) sweeps up-left from its root behind the near wing to its tip at the top left; the near wing
# stands up over the shoulders (crimson membrane, gold claws at its corners); the flame mane runs over the neck to the
# head at the right (the yellow eye at 84, 42; the open jaw with its violet mouth and fangs under it); the long tail
# trails to the left with its golden fin; the near fore leg reaches down-right to the claws at the bottom right; the far
# fore leg stands under the teal chest plate; the near hind leg under the haunch, the far one behind it to the left.
D_STAND = 58                   # the standing point: between the hind and the fore legs, under the body's middle
FAR_WING = [(12.0, 7.0), (38.0, 7.0), (46.0, 12.0), (57.0, 18.0), (60.0, 24.0), (59.0, 31.0), (52.0, 34.0),
            (46.0, 33.0), (41.0, 31.0), (38.0, 24.0), (28.0, 22.0), (25.0, 22.0), (25.0, 16.0), (30.0, 14.0),
            (12.0, 11.0)]
NEAR_WING = [(57.0, 11.0), (65.0, 0.0), (76.0, 0.0), (82.0, 4.0), (86.0, 0.0), (93.0, 0.0), (93.0, 11.0),
             (96.0, 18.0), (97.0, 23.0), (93.0, 30.0), (85.0, 30.0), (80.0, 28.0), (72.0, 27.0), (66.0, 29.0),
             (60.0, 30.0), (57.0, 22.0)]
HEAD = [(64.0, 26.0), (84.0, 26.0), (86.0, 28.5), (93.0, 29.0), (99.0, 33.0), (99.0, 39.0), (94.5, 43.0),
        (93.5, 49.5), (86.0, 49.5), (80.0, 47.5), (76.0, 44.0), (70.0, 41.0), (64.0, 39.0)]
JAW = [(83.0, 46.5), (92.0, 45.5), (93.5, 49.5), (85.0, 49.5)]
TAIL = [(0.0, 44.0), (16.0, 43.0), (30.0, 39.0), (40.0, 36.0), (44.0, 40.0), (43.0, 47.0), (36.0, 50.0),
        (24.0, 51.0), (17.0, 57.0), (0.0, 58.0)]
NEAR_FORE = [(84.0, 47.0), (93.0, 49.0), (100.0, 53.0), (107.0, 57.0), (107.0, 64.0), (92.0, 64.0), (88.0, 56.0),
             (82.0, 51.0)]
FAR_FORE = [(60.0, 48.0), (73.0, 48.0), (74.0, 60.0), (60.0, 60.0)]
NEAR_HIND = [(41.0, 46.0), (56.0, 46.0), (57.0, 64.0), (41.0, 64.0)]
FAR_HIND = [(22.0, 50.0), (38.0, 49.0), (38.0, 62.0), (22.0, 62.0)]
DRAGON_PARTS = [
    ("jaw", JAW),
    ("head", lambda f: poly(HEAD, (f.H, f.W)) & ~poly(NEAR_FORE, (f.H, f.W))),
    ("near_wing", lambda f: poly(NEAR_WING, (f.H, f.W)) & ~is_flame(f.d)),
    ("far_wing", FAR_WING),
    ("tail", TAIL),                # before the legs: the tail's own underside outline goes with it when it lifts (cut
                                   # by the far hind leg's box, it stayed behind as a bar over the leg)
    ("near_fore", NEAR_FORE),
    ("far_fore", FAR_FORE),
    ("near_hind", NEAR_HIND),
    ("far_hind", FAR_HIND),
]
MOUTH = (47, 37, 94)           # the inside of the open jaws (the design's darkest violet)
D_ROOTS = {"far_wing": (55.0, 30.0), "near_wing": (74.0, 29.0), "tail": (42.0, 42.0), "head": (68.0, 38.0),
           "jaw": (82.0, 46.0)}

# ------------------------------------------------------------------------------------------------- her parts
H_STAND = 24                   # the standing point: between her feet
# hd/idle.png, 40 x 63: the horn crown and face over the hair (rows 0-20), the breastplate, both arms hanging with the
# claws at the hips (rows 38-41), the two legs from the belt (row 41) to the clawed feet, the tail curling down-left
# from behind the near hip to its golden tip at the bottom left
H_TAIL = [(0.0, 44.0), (8.0, 38.5), (14.5, 37.5), (14.5, 42.0), (11.0, 46.0), (9.0, 52.0), (13.0, 55.0),
          (13.0, 59.5), (0.0, 59.5)]
H_NEAR_LEG = [(11.5, 42.5), (22.5, 42.5), (22.5, 48.0), (19.5, 56.0), (18.5, 63.0), (11.0, 63.0), (12.0, 55.0)]
H_FAR_LEG = [(25.5, 41.5), (35.5, 41.5), (37.5, 50.0), (40.0, 57.0), (40.0, 63.0), (29.0, 63.0), (28.5, 52.0),
             (25.5, 47.0)]
HUMAN_PARTS = [("tail", H_TAIL), ("near_leg", H_NEAR_LEG), ("far_leg", H_FAR_LEG)]


def dragon_form():
    return Form("dragon", "d_idle.png", D_STAND, DRAGON_PARTS)


def human_form():
    return Form("human", "idle.png", H_STAND, HUMAN_PARTS)


# ------------------------------------------------------------------------------------------------- Codex's drawing
def regrid_full(a, size):
    """regrid.regrid's read-back NOT cropped to the figure, with its cell bounds: the read-back cell (i, j) spans
    bx[i]..bx[i + 1] x by[j]..by[j + 1] of the picture (regrid crops its result but returns the uncropped bounds)."""
    import regrid as RG
    out, sq, (bx, by) = RG.regrid(a.copy(), size)
    full_h, full_w = len(by) - 1, len(bx) - 1
    # where the crop started: the first cell row / column the uncropped read-back has a square in
    op = a[..., 3] >= 128
    oy = ox = None
    for j in range(full_h):
        cy = (by[j] + by[j + 1]) // 2
        row = [(op[max(0, cy - 1):cy + 2, max(0, (bx[i] + bx[i + 1]) // 2 - 1):(bx[i] + bx[i + 1]) // 2 + 2].sum() * 2 >
                9 if True else 0) for i in range(full_w)]
        if any(row):
            oy = j
            break
    for i in range(full_w):
        cx = (bx[i] + bx[i + 1]) // 2
        col = [op[max(0, (by[j] + by[j + 1]) // 2 - 1):(by[j] + by[j + 1]) // 2 + 2, max(0, cx - 1):cx + 2].sum() * 2 > 9
               for j in range(full_h)]
        if any(col):
            ox = i
            break
    return out, sq, bx, by, ox, oy


class Turner:
    """A design drawn again from Codex's own full-size picture at any angle: the design square (x, y) is the read-back's
    cell (x + ox, y + oy) (the design is the read-back square for square: design_shyvana_model keeps D-1 as drawn)."""

    def __init__(self, form, raw, size):
        pic = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", "raw", raw))).convert("RGBA")).copy()
        rb, self.sq, self.bx, self.by, self.ox, self.oy = regrid_full(pic, size)
        if rb.shape[:2] != form.d.shape[:2] or ((rb[..., 3] > 0) != (form.d[..., 3] > 0)).sum() > 0:
            sys.exit(f"{raw}: its read-back is not {form.name}'s design square for square any more")
        pic[..., 3] = np.where(pic[..., 3] >= 128, 255, 0)
        pic[pic[..., 3] == 0] = 0
        self.f, self.pic = form, pic
        self.pal = np.unique(form.d[form.d[..., 3] > 0][:, :3], axis=0).astype(float)
        self.outline = PD.edge_colour(form.d)
        self.k = 1.0 / ((self.bx[-1] - self.bx[0]) / (len(self.bx) - 1))   # design squares a picture px
        self._cache = {}

    def d2p(self, x, y):
        """A design point (square edges) on the picture (px)."""
        def axis(v, edges, off):
            i = int(math.floor(v)) + off
            i = max(0, min(len(edges) - 2, i))
            f = v - math.floor(v)
            return edges[i] + f * (edges[i + 1] - edges[i])
        return axis(x, self.bx, self.ox), axis(y, self.by, self.oy)

    def pmask(self, dmask):
        """A design-square mask as picture pixels (each square's cell)."""
        m = np.zeros(self.pic.shape[:2], bool)
        for r, c in zip(*np.nonzero(dmask)):
            y0, y1 = self.by[r + self.oy], self.by[r + self.oy + 1]
            x0, x1 = self.bx[c + self.ox], self.bx[c + self.ox + 1]
            m[y0:y1, x0:x1] = True
        return m

    def turned(self, dmask, angle, about):
        """The part (design-square mask) turned `angle` degrees counter-clockwise on screen about design point `about`,
        drawn from the picture and brought to the design's grid and colours -> (squares, the grid index of `about`)."""
        key = (dmask.tobytes(), round(angle, 2), about)
        if key in self._cache:
            return self._cache[key]
        m = self.pmask(dmask) & (self.pic[..., 3] > 0)
        src = np.zeros_like(self.pic)
        src[m] = self.pic[m]
        P_ = 700
        big = np.pad(src, ((P_, P_), (P_, P_), (0, 0)))
        ax, ay = self.d2p(*about)
        rot = np.asarray(Image.fromarray(big).rotate(angle, resample=Image.BICUBIC, center=(ax + P_, ay + P_))).copy()
        rot[..., 3] = np.where(rot[..., 3] >= 128, 255, 0)
        rot[rot[..., 3] == 0] = 0
        g, n0 = PD.pixelate(rot, self.k, (ax + P_, ay + P_), self.outline, self.pal)
        g = R.snap(g, self.pal)
        g[..., 3] = np.where(g[..., 3] > 0, 255, 0)
        self._cache[key] = (g, n0)
        return g, n0


def paste_grid(can, g, n0, at, origin):
    """Turned squares g (n0: the grid index of their pivot) with the pivot on design point `at`, the design's (0, 0) on
    canvas square `origin`."""
    ys, xs = np.nonzero(g[..., 3] > 0)
    tx = xs - n0[0] + int(round(at[0] + origin[0]))
    ty = ys - n0[1] + int(round(at[1] + origin[1]))
    ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
    can[ty[ok], tx[ok]] = g[ys[ok], xs[ok]]
    return can


# ------------------------------------------------------------------------------------------------- the canvas
def turn_pt(p, c, deg):
    """Point p turned deg degrees counter-clockwise on screen (y down) about c."""
    t = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(t) + y * math.sin(t), c[1] - x * math.sin(t) + y * math.cos(t))


class Canvas:
    """Every frame of both forms on one canvas: the pivot column CX, the ground row GY (ppu_rig.Rig's), each form
    standing with its own standing column on the pivot."""

    def __init__(self):
        self.dragon = dragon_form()
        self.human = human_form()
        self.T = Turner(self.dragon, "shyvana-model-D-1.png", 11.0)
        side = self.dragon

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, side.d
            H, W, px, ground = side.H, side.W, side.stand, side.H
            outline = PD.edge_colour(side.d)
        self.rig = R.Rig(D, pad=(40, 40, 60, 12))
        self.outline = D.outline

    def blank(self):
        return self.rig.canvas()

    def origin(self, f):
        """Canvas square of design (0, 0) for a form standing on the pivot."""
        return self.rig.CX - f.stand, self.rig.GY - f.H

    def stamp(self, can, f, lay, dx=0, dy=0):
        ox, oy = self.origin(f)
        ys, xs = np.nonzero(lay[..., 3] > 0)
        ty, tx = ys + oy + dy, xs + ox + dx
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        can[ty[ok], tx[ok]] = lay[ys[ok], xs[ok]]
        return can

    def smear(self, can, f, lay, frm, to):
        """The layer stamped at every whole step from offset `frm` to `to` (the last on top): a part that moved off the
        one it hangs from drags its edge after it (no seam opens)."""
        steps = max(abs(to[0] - frm[0]), abs(to[1] - frm[1]))
        for t in range(steps + 1):
            k = t / steps if steps else 1.0
            self.stamp(can, f, lay, int(round(frm[0] + (to[0] - frm[0]) * k)), int(round(frm[1] + (to[1] - frm[1]) * k)))
        return can

    def turned(self, can, f, mask, angle, about, at, dx=0, dy=0):
        """The parts in `mask` drawn from Codex's picture turned `angle` degrees (counter-clockwise) about design point
        `about`, that point put on design point `at` moved (dx, dy)."""
        g, n0 = self.T.turned(mask, angle, about)
        ox, oy = self.origin(f)
        return paste_grid(can, g, n0, at, (ox + dx, oy + dy))


def mirrored(C, can):
    """The frame mirrored about the pivot column (the dragon turned round)."""
    out = np.zeros_like(can)
    cx = C.rig.CX
    ys, xs = np.nonzero(can[..., 3] > 0)
    tx = 2 * cx - xs
    ok = (tx >= 0) & (tx < can.shape[1])
    out[ys[ok], tx[ok]] = can[ys[ok], xs[ok]]
    return out


HIP = (46.0, 44.0)             # the front rears up and comes down about this point (over the near hind leg)
SHOULDER = (86.0, 49.0)        # the near fore leg swings about this point (where it leaves the chest)
LEG_BAND = 3                   # rows of a leg's top dragged after it when the body above moves off it


def leg_top(f, name):
    m = f.masks[name]
    rows = np.nonzero(m.any(1))[0]
    band = np.zeros_like(m)
    band[rows.min():rows.min() + LEG_BAND] = True
    return m & band


def dragon(C, dx=0, dy=0, lift=0, body_dy=0, rear=0.0, near_wing=0.0, far_wing=0.0, wing_dy=0, near_front=False,
           tail=0.0, tail_dy=0, head=(0, 0), jaw=0, legs=None, swipe=0.0, mirror=False, flash=False):
    """The dragon: (dx, dy) the whole figure, `lift` rows off the ground; body_dy the body over its legs (negative: up);
    rear degrees the front (body, head, fore legs, wings) rears up about HIP; near_wing / far_wing degrees each wing
    turns about its root on top (positive: counter-clockwise - the far wing's tip down, the near wing tipped back),
    wing_dy rows both wings rise; near_front: the near wing drawn over the head (a slap forward); tail degrees about
    its root (positive: the tip down), tail_dy rows; head (dx, dy) the head with its mane and jaw on the body; jaw rows
    the jaw drops; legs {leg: (dx, dy)} each leg stepped (dy < 0: lifted); swipe degrees the near fore leg turns about
    its shoulder (negative: raised forward); mirror: turned round; flash: hit white."""
    f, T = C.dragon, C.T
    m = f.masks
    legs = legs or {}
    can = C.blank()
    gy = dy - lift
    by = gy + body_dy                                    # the body's rows

    def root(name):
        """Where a part's root lies after the rear (design point)."""
        return turn_pt(D_ROOTS[name], HIP, rear) if rear else D_ROOTS[name]

    def wing(name, deg):
        a = rear + deg
        if a == 0 and not rear:
            C.stamp(can, f, f.layer(name), dx, by + wing_dy)
        else:
            C.turned(can, f, m[name], a, D_ROOTS[name], root(name), dx, by + wing_dy)

    def leg(name):
        lx, ly = legs.get(name, (0, 0))
        to = (dx + lx, gy + ly)
        if by < to[1]:                                   # the body above it rose off it: its top dragged up to the body
            C.smear(can, f, f.layer(mask=leg_top(f, name)), to, (to[0], by))
        C.stamp(can, f, f.layer(name), *to)

    wing("far_wing", far_wing)
    if tail:
        C.turned(can, f, m["tail"], tail, D_ROOTS["tail"], D_ROOTS["tail"], dx, by + tail_dy)
    else:
        C.stamp(can, f, f.layer("tail"), dx, by + tail_dy)
    leg("far_hind")
    if rear:
        front = m["body"] | m["far_fore"] | m["near_fore"]
        C.turned(can, f, front, rear, HIP, HIP, dx, by)
    else:
        leg("far_fore")
        C.stamp(can, f, f.layer("body"), dx, by)
    leg("near_hind")
    if not near_front:
        wing("near_wing", near_wing)
    hx, hy = head
    if rear:
        C.turned(can, f, m["head"] | m["jaw"], rear, HIP, HIP, dx + hx, by + hy)
    else:
        # the head with its mane moved whole (a step or two: seal() closes the seam at the neck); the jaw dropped
        # `jaw` rows, the rows it leaves under the upper jaw the mouth's dark inside
        C.stamp(can, f, f.layer("head"), dx + hx, by + hy)
        if jaw:
            gap = np.zeros_like(f.d)
            jm = m["jaw"]
            for k in range(jaw):
                sh = np.zeros_like(jm)
                sh[k:] = jm[:jm.shape[0] - k]
                gap[sh & ~m["head"]] = (*MOUTH, 255)
            inner = ndimage.binary_erosion(jm | m["head"], iterations=1)
            gap[~ndimage.binary_dilation(inner, iterations=1)] = 0
            C.stamp(can, f, gap, dx + hx, by + hy)
        C.stamp(can, f, f.layer("jaw"), dx + hx, by + hy + jaw)
    if near_front:
        wing("near_wing", near_wing)
    if not rear:
        if swipe:
            C.turned(can, f, m["near_fore"], swipe, SHOULDER, SHOULDER, dx, by)
        else:
            leg("near_fore")
    if tail or tail_dy:
        # under a tail that lifted: the strip it leaves between itself and the far hind thigh is the thigh (else the
        # thigh's top outline stands alone as a bar under the tail)
        ox, oy = C.origin(f)
        region = np.zeros(can.shape[:2], bool)
        ys, xs = np.nonzero(ndimage.binary_dilation(m["tail"], iterations=3))
        ty, tx = ys + oy + by, xs + ox + dx
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        region[ty[ok], tx[ok]] = True
        can = bridge(can, region)
    can = seal(can, C.outline)
    if mirror:
        can = mirrored(C, can)
    can[C.rig.GY:] = 0
    return R.flash(can) if flash else can


def bridge(can, region, maxgap=2):
    """Clear squares in `region` with drawn squares above and below them in the same column, at most `maxgap` rows
    apart, filled from the squares round them that are not outline (R.fill_under): a strip a moved part opened."""
    op = can[..., 3] > 0
    gap = np.zeros(op.shape, bool)
    for up in range(1, maxgap + 1):
        for dn in range(1, maxgap + 2 - up):
            above = np.roll(op, up, 0)
            below = np.roll(op, -dn, 0)
            gap |= above & below
    gap &= ~op & region
    return R.fill_under(can, gap) if gap.any() else can


def seal(can, outline, speck=8):
    """rig_gnar.seal: cracks a moved or turned part leaves closed from their neighbours, enclosed holes up to 12 squares
    filled, loose specks under `speck` squares dropped."""
    import rig_gnar
    return rig_gnar.seal(can, outline, speck)


def human(C, dx=0, dy=0, flash=False, breath=0):
    """Her design standing; the idle's breathing: everything but the legs and the tail (head, hair, breastplate, both
    arms with their claws) set down `breath` rows onto the legs (the user's rule for Mel: legs untouched)."""
    f = C.human
    can = C.blank()
    still = f.layer("tail", "near_leg", "far_leg")
    C.stamp(can, f, still, dx, dy)
    C.stamp(can, f, f.layer("body"), dx, dy + breath)
    can[C.rig.GY:] = 0
    return R.flash(can) if flash else can


# ------------------------------------------------------------------------------------------------- the dragon's actions
# ms per frame; the kit's ticks (tools/kit/build_shyvana.py) come from these (a frame's start in ticks = ms x 0.06)
MS = {"idle": [150] * 8, "hit": [100, 100],
      "d_idle": [150] * 8, "d_run": [100] * 8,
      "d_attack": [60, 80, 90, 90, 90, 90],
      "d_skill": [60, 80, 90, 90, 80, 70],
      "d_skill_b": [60, 60, 60, 70, 90, 80, 80],
      "d_bite": [70, 90, 80, 90, 100, 100],
      "d_skill2": [70, 90, 90, 90, 70, 60],
      "d_hit": [100, 100],
      "d_fly": [90, 90, 90, 90],
      "d_dead": [100, 110, 120, 140, 160, 600]}


def dragon_frames(C):
    p = lambda **k: dragon(C, **k)
    out = {}
    # idle (League's ShyvanaDragon idle2: a slow breath, the wings lifting and settling, the head bobbing, the tail
    # swaying): the wings a row up and tipped up a little, the head a row up, the tail swinging a few degrees - body
    # and legs as drawn (the legs never move in an idle)
    wings = [0, -2, -3, -4, -4, -3, -2, 0]
    up = [0, 0, -1, -1, -1, -1, 0, 0]
    head = [0, 0, 0, -1, -1, 0, 0, 0]
    tail = [0, -2, -3, -4, -3, -2, 0, 1]
    out["d_idle"] = [p(far_wing=w, near_wing=-w * 0.6, wing_dy=u, head=(0, h), tail=t)
                     for w, u, h, t in zip(wings, up, head, tail)]
    # run (League's run1: a bounding gallop, the wings beating, the tail swinging): the diagonal pairs of legs stepping
    # in turn (league_braum's walk on four legs: a leg lifted steps forward, the one on the ground draws back), the body
    # rising as the legs push, the wings beating, the head bobbing, the tail swinging
    gait = [  # near_fore, far_hind | far_fore, near_hind: (dx, dy) - a lifted leg goes up into the body (no seam)
        ((2, -2), (2, -2), (-1, 0), (-1, 0)),
        ((3, -1), (3, -1), (-2, 0), (-2, 0)),
        ((2, 0), (2, 0), (-2, -1), (-2, -1)),
        ((0, 0), (0, 0), (0, -2), (0, -2)),
        ((-1, 0), (-1, 0), (2, -2), (2, -2)),
        ((-2, 0), (-2, 0), (3, -1), (3, -1)),
        ((-2, -1), (-2, -1), (2, 0), (2, 0)),
        ((0, -2), (0, -2), (0, 0), (0, 0)),
    ]
    lift = [0, 1, 0, 0, 0, 1, 0, 0]              # the suspension of the gallop: the whole dragon off the ground
    beat = [-6, -12, -6, 4, 8, 4, -2, -4]
    tail = [-3, -5, -3, 0, 3, 5, 3, 0]
    head = [(1, 0), (1, -1), (1, 0), (1, 1), (1, 0), (1, -1), (1, 0), (1, 1)]
    out["d_run"] = [p(lift=lf, far_wing=b, near_wing=-b * 0.5, tail=t, head=h,
                      legs={"near_fore": nf, "far_hind": fh, "far_fore": ff, "near_hind": nh})
                    for (nf, fh, ff, nh), lf, b, t, h in zip(gait, lift, beat, tail, head)]
    # auto attack (League's Attack1: drawn back low, the head and the near fore claw thrown forward, the claw raking
    # down; the hit at ~230 ms = tick 14): drawn back, the claw raised, thrown forward, the rake (frame 4, the hit),
    # held, back
    out["d_attack"] = [p(dx=-1, head=(-1, 1), swipe=25, tail=-3),
                       p(dx=-1, head=(0, -1), swipe=55, far_wing=-6, near_wing=4, tail=-6),
                       p(dx=2, head=(1, 0), swipe=40, jaw=1, far_wing=-8, near_wing=6, tail=-4),
                       p(dx=3, head=(2, 1), swipe=-12, jaw=1, tail=2),
                       p(dx=2, head=(1, 1), swipe=-6, tail=2),
                       p(dx=1, head=(1, 0))]
    # Q's first strike as the dragon, the wing (League's Spell1_Wing: both wings spread wide and up, then the near wing
    # sweeps forward and down across the front; the hit at ~230 ms): spread, wider, swept forward, slapped down in front
    # (frame 4, the hit), back up, back - the near wing stays behind the head (in front of it, it hid the face; turned
    # past -45 degrees its upper-left claw came off the wing)
    out["d_skill"] = [p(body_dy=1, near_wing=20, far_wing=-12, tail=-3),
                      p(dx=-1, body_dy=1, near_wing=32, far_wing=-22, head=(-1, 0), tail=-6),
                      p(dx=2, near_wing=-25, far_wing=-8, head=(1, 0), tail=-2),
                      p(dx=3, near_wing=-45, far_wing=6, head=(2, 1), tail=2),
                      p(dx=2, near_wing=-25, far_wing=2, head=(1, 1), tail=1),
                      p(dx=1, near_wing=-6)]
    # Q's second strike as the dragon, the tail (League's Spell1_Tail: the dragon spins round, its tail sweeping through
    # the front; the hit at ~250 ms): crouched with the tail raised, turned round (mirrored) with the tail swung high,
    # the tail sweeping low through the front, the sweep (frame 5, the hit), turned back, settling
    out["d_skill_b"] = [p(body_dy=1, tail=-20, far_wing=-6),
                        p(body_dy=1, tail=-40, far_wing=-10, near_wing=8),
                        p(tail=-35, far_wing=-8, near_wing=6, mirror=True),
                        p(tail=-10, far_wing=-4, mirror=True),
                        p(dx=1, tail=12, mirror=True, near_wing=-4),
                        p(dx=1, tail=6, far_wing=-4),
                        p(tail=2)]
    # Q's third strike, the bite (League's Spell1_Bite: rearing up high on the hind legs, then the head plunging down
    # and forward with the jaws open; the hit at ~270 ms): rearing, high, coming down, the bite (frame 4), back
    out["d_bite"] = [p(rear=14, far_wing=-8, near_wing=8, tail=6),
                     p(rear=24, far_wing=-14, near_wing=12, tail=10),
                     p(dx=2, rear=4, far_wing=-6, tail=-6),
                     p(dx=4, head=(2, 2), jaw=2, far_wing=4, near_wing=-6, tail=-10),
                     p(dx=3, head=(2, 1), jaw=1, tail=-5),
                     p(dx=1, head=(1, 0))]
    # E Molten Burst as the dragon (League's Spell3: the head reared back and up, then thrust forward low with the jaws
    # wide as the fireball leaves; the release at ~250 ms): head up and back, wings spread; thrust forward, jaws open
    # (frame 4, the release), held, back
    out["d_skill2"] = [p(head=(-1, -1), far_wing=-8, near_wing=10, tail=-3),
                       p(dx=-1, head=(-1, -2), far_wing=-14, near_wing=16, tail=-5),
                       p(dx=1, head=(1, 0), jaw=1, far_wing=-6, near_wing=6, tail=-2),
                       p(dx=2, head=(2, 1), jaw=2, far_wing=-4, near_wing=4),
                       p(dx=1, head=(1, 1), jaw=1),
                       p(head=(1, 0))]
    out["d_hit"] = [p(dx=-2, flash=True, head=(-1, 0)), p(dx=-1)]
    # R's flight and landing (League's Spell4_Intro / Spell4: the dragon in the air, both wings beating wide, the claws
    # reaching forward, then coming down onto the target with the wings spread): two beats in the air, the touch-down,
    # landed (the ult tag puts them after her leap; the add-on's whole-body dragon can use them alone)
    out["d_fly"] = [p(lift=9, far_wing=-28, near_wing=14, swipe=30, tail=-10, head=(1, -1)),
                    p(lift=11, far_wing=-6, near_wing=-8, swipe=36, tail=-6, head=(1, 0)),
                    p(lift=4, far_wing=-22, near_wing=12, swipe=20, tail=-8, head=(2, 0)),
                    p(dx=1, far_wing=-12, near_wing=8, swipe=-6, tail=-3, head=(1, 1))]
    # the death (League's Death: struck back, the legs giving way, the body sinking flat, the wings falling open on the
    # ground, the head down): struck, sinking, down, flat, the wings fallen
    out["d_dead"] = [p(dx=-1, head=(-1, -1), far_wing=-6, near_wing=6),
                     p(dx=-1, body_dy=2, head=(0, 1), far_wing=4, near_wing=14, tail=4),
                     p(dx=-1, body_dy=4, head=(0, 2), far_wing=12, near_wing=24, tail=8),
                     p(dx=-1, body_dy=5, head=(0, 2), far_wing=18, near_wing=32, tail=10),
                     p(dx=-1, body_dy=6, head=(0, 2), far_wing=22, near_wing=38, tail=12),
                     p(dx=-1, body_dy=6, head=(0, 2), far_wing=22, near_wing=38, tail=12)]
    return out


def human_frames(C):
    h = lambda **k: human(C, **k)
    out = {}
    # idle (League's Idle1: she stands breathing, the tail swaying a little): the rows above the waist settle a row and
    # rise again (legs and tail untouched: Mel's rule, 「上下摆动导致腿部变形」)
    out["idle"] = [h(breath=b) for b in (0, 0, 1, 1, 1, 1, 0, 0)]
    out["hit"] = [h(dx=-2, flash=True), h(dx=-1)]
    return out


def frames(C, tags=None):
    a = {**human_frames(C), **dragon_frames(C)}
    out = {}
    for tag, cans in a.items():
        if tags and tag not in tags:
            continue
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = [(c, m) for c, m in zip(cans, ms)]
    return out


TINT = {"near_leg": (255, 0, 255), "far_leg": (255, 120, 0), "far_wing": (60, 200, 255), "near_wing": (255, 220, 0), "head": (0, 255, 120), "jaw": (255, 0, 255),
        "tail": (255, 120, 0), "near_fore": (120, 120, 255), "far_fore": (0, 140, 140), "near_hind": (200, 60, 255),
        "far_hind": (140, 90, 40)}


def tinted(f, z=10):
    out = f.d.copy()
    for name, c in TINT.items():
        if name in f.masks:
            m = f.masks[name]
            out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    dr = ImageDraw.Draw(bg)
    for name, (x, y) in D_ROOTS.items() if f.name == "dragon" else ():
        dr.ellipse([x * z - 6, y * z - 6, x * z + 6, y * z + 6], outline=(0, 0, 0, 255), width=3)
    return bg.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        for f in (dragon_form(), human_form()):
            tinted(f).save(os.path.join(a.parts, f"shyvana_parts_{f.name}.png"))
            print(f.name, {k: int(v.sum()) for k, v in f.masks.items()})
        return
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        return


if __name__ == "__main__":
    main()

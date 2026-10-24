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
        self.rig = R.Rig(D, pad=(50, 70, 60, 12))      # room for the dragon's wing gust ahead (bake)
        self.outline = D.outline
        self.poses = {n: load(f"pose_{n}.png") for n in POSE_NAMES}
        self.pose_head = {}
        for n in POSE_NAMES:
            with open(lp(os.path.join(SRC, "hd", f"pose_{n}.json")), encoding="utf-8") as fh:
                self.pose_head[n] = json.load(fh)["head_at"]

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
    return hit_white(can) if flash else can


def hit_white(can, k=0.45):
    """ppu_rig.flash keeping the outline dark: the squares strips.complete_outline counts as dark (luminance under 70)
    stay, the rest go k of the way to white. Flashed whole, the frame's edge was all light and the export's finish drew
    a new outline round it - a square fatter, the gap between her tail and her foot closed into a hole."""
    import strips
    out = can.copy()
    m = (out[..., 3] > 0) & (strips.lum(out[..., :3]) >= 70)
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


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
    return hit_white(can) if flash else can


# ------------------------------------------------------------------------------------------------- her key poses
# Codex's whole-body poses (assets/source/shyvana/codex_poses, read back by tools/art/design_shyvana_poses.py at the
# design's build with the design's head: hd/pose_<name>.png + .json, where the head box went). Each is placed with its
# head's middle where the pose's skeleton put it from her standing point (tools/art/pack_shyvana_poses.py: every bone
# the design's length, the stance's middle on the design's H_STAND) and its lowest square on the ground, or `lift` rows
# over it. Placed by the feet instead, the body jumped back and forth: a run step's back foot is on its toes, the sweep's
# tail lies on the ground in front, the run's torso swung 16 squares a step.
POSE_NAMES = ["crouch", "rise", "slash", "flip", "sweep", "throw", "leap", "stagger", "kneel", "collapse",
              "run1", "run2", "run3", "run4"]
HEAD_MID = 13.5                # the head box's middle column from its left (27 squares: design_shyvana_poses.HEAD)


def plan_head(name):
    """Where the pose's skeleton put the head box's middle, squares right of her standing point."""
    import pack_shyvana_poses as PK
    return PK.build(PK.POSES[name][3])["head"][0] - H_STAND


def pose(C, name, dx=0, lift=0, flash=False):
    """Codex's key pose standing on the pivot (moved dx), its lowest square on the ground or `lift` rows over it."""
    a = C.poses[name]
    stand = C.pose_head[name][0] + HEAD_MID - plan_head(name)
    can = C.blank()
    ox = int(round(C.rig.CX - stand)) + dx
    oy = C.rig.GY - a.shape[0] - lift
    ys, xs = np.nonzero(a[..., 3] > 0)
    ty, tx = ys + oy, xs + ox
    ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
    can[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
    can[C.rig.GY:] = 0
    return hit_white(can) if flash else can


# ------------------------------------------------------------------------------------------------- the dragon's actions
# ms per frame; the kit's ticks (tools/kit/build_shyvana.py) come from these (a frame's start in ticks = ms x 0.06)
MS = {"idle": [150] * 8, "hit": [100, 100], "run": [120] * 4,
      "attack": [70, 70, 100, 80, 113], "skill": [60, 100, 120, 100, 87], "skill_b": [70, 110, 140, 90, 90],
      "skill2": [100, 130, 100, 137], "ult": [60, 90, 60, 90, 90, 90, 120], "revert": [90, 60, 80, 100, 103],
      "dead": [120, 160, 220, 600],
      "d_idle": [150] * 8, "d_run": [100] * 8,
      "d_attack": [60, 80, 90, 90, 90, 90],
      "d_skill": [60, 80, 90, 90, 80, 70],
      "d_skill_b": [60, 60, 60, 70, 90, 80, 80],
      "d_bite": [70, 90, 80, 90, 100, 100],
      "d_skill2": [70, 90, 90, 90, 70, 60],
      "d_hit": [100, 100],
      "d_fly": [90, 90, 90, 90],
      "d_dead": [100, 80, 100, 160, 220, 600]}


# ------------------------------------------------------------------------------------------------- the dragon's run
# The run's legs (the user, 2026-10-24, after the whole-body dragon add-on: 「这走路腿都不动的？」 - the old run moved
# each leg 2-3 squares as a block; moved 5-7 the blocks tore off the body: 「走路时腿部变形了 你应该能改好 不用依赖codex」).
# League_hecarim's way (fix_hecarim_strips.py, the user's 「四个脚都要有明显错开并且自然」): the body as drawn goes over the
# legs untouched and the legs step under it in a four-beat gait. Here each paw is the design's own squares moved whole -
# RUN_GROUND frames on the ground sliding back from RUN_REACH ahead to as far behind, then forward through the air on
# RUN_LIFT - and the leg above it is turned about its root (hip / shoulder, inside the body) to reach the paw's ankle,
# drawn again from Codex's picture at that angle (Turner, as the wings and the tail). The near fore stays one straight
# piece too, steeper as its paw comes back, the length it has over hidden behind the paw (bent at an elbow it folded into
# an L: 「右前脚有略微变形」). A leg's piece takes RUN_BAND rows of the body over its top along (drawn under the body: no
# seam opens however it turns) and is cut two rows into its paw (its end never shows between the claws).
# Every other dragon action keeps DRAGON_PARTS' legs.
RUN_LEGS = {   # cut: the leg's squares (taken out of the body); paw: its rows from paw_y (and columns from paw_x), with
               # wrist: also every square past the line through the ankle square to the leg (the wrist moves with the paw)
    "far_hind": dict(cut=[(25, 51), (33, 51), (33, 55), (35, 55), (35, 61), (22, 61), (22, 55), (25, 55)],
                     root=(30, 47), ankle=(29, 56), paw_y=56),
    "near_hind": dict(cut=[(41, 50), (54, 50), (54, 51), (56, 51), (56, 58), (57, 58), (57, 64), (41, 64)],
                      root=(48, 48), ankle=(48, 58), paw_y=58),
    "far_fore": dict(cut=[(59, 51), (67, 51), (67, 55), (72, 55), (72, 60), (59, 60)],
                     root=(63, 48), ankle=(63, 55), paw_y=55),
    "near_fore": dict(cut=[(79, 50), (87, 50), (87, 48), (95, 48), (97, 51), (108, 57), (108, 63), (92, 63),
                           (88, 56), (79, 51)],
                      root=(84, 50), ankle=(96, 56), paw_y=57, paw_x=93, wrist=True),
}
RUN_BAND = 3
RUN_GROUND = 5                 # frames a paw is on the ground (of 8)
RUN_LIFT = [2, 3, 2]           # rows a paw is up in the air frames
RUN_OFFSET = {"near_hind": 0, "far_hind": 2, "far_fore": 4, "near_fore": 6}    # the four beats, a quarter cycle apart
RUN_REACH = {"near_hind": 4, "far_hind": 3, "far_fore": 3, "near_fore": 3}
RUN_CENTRE = {"near_hind": 0, "far_hind": 0, "far_fore": 0, "near_fore": -3}  # the near fore reaches as drawn at most
RUN_BOB = [0, 0, -1, 0, 0, 0, -1, 0]   # the body rows up (the legs reach after it)


def _ang(v):
    """Screen angle of a vector (y down), counter-clockwise, radians."""
    return math.atan2(-v[1], v[0])


def _wrap(deg):
    return (deg + 180) % 360 - 180


class RunLegs:
    """The dragon design's legs for the run: each leg's cut and its two pieces (the leg, the paw)."""

    def __init__(self, f):
        self.f = f
        op = f.d[..., 3] > 0
        yy, xx = np.mgrid[0:f.H, 0:f.W]
        self.cuts = {n: poly(L["cut"], (f.H, f.W)) & op for n, L in RUN_LEGS.items()}
        self.allcut = np.zeros((f.H, f.W), bool)
        for m in self.cuts.values():
            self.allcut |= m
        self.pieces = {}
        for name, L in RUN_LEGS.items():
            cut = self.cuts[name]
            paw = cut & (yy >= L["paw_y"]) & (xx >= L.get("paw_x", 0))
            if L.get("wrist"):
                (rx, ry), (ax, ay) = L["root"], L["ankle"]
                n = math.hypot(ax - rx, ay - ry)
                paw |= cut & (((xx + 0.5 - rx) * (ax - rx) + (yy + 0.5 - ry) * (ay - ry)) / n >= n)
            leg = cut & ~paw
            top = leg.any(1).nonzero()[0].min()
            # the band: inner squares only (an outline square turned with it stood out alone past the jaw)
            band = (ndimage.binary_dilation(leg, iterations=RUN_BAND) & ndimage.binary_erosion(op) & ~self.allcut
                    & (yy <= top) & (yy >= top - RUN_BAND))
            self.pieces[name] = {"leg": leg | band, "paw": paw}

    def layer(self, mask):
        out = np.zeros_like(self.f.d)
        out[mask] = self.f.d[mask]
        return out


def run_paw(name, t):
    """Frame t of the run: the paw's columns from where it is drawn and its rows up."""
    p = (t - RUN_OFFSET[name]) % 8
    r, c = RUN_REACH[name], RUN_CENTRE[name]
    if p < RUN_GROUND:
        return c + r - 2 * r * p / (RUN_GROUND - 1), 0
    j = p - RUN_GROUND
    return c - r + 2 * r * (j + 1) / (8 - RUN_GROUND + 1), RUN_LIFT[j]


def run_leg(C, can, RL, name, gx, lift, by):
    """One leg of the run: the paw moved (gx, -lift) whole, the leg turned about its root (moved `by` rows with the
    body) to point at the paw's ankle."""
    L, P, f = RUN_LEGS[name], RL.pieces[name], RL.f
    gx = int(round(gx))
    (rx, ry), (ax, ay) = L["root"], L["ankle"]
    deg = _wrap(math.degrees(_ang((ax + gx - rx, ay - lift - ry - by)) - _ang((ax - rx, ay - ry))))
    legs = C.blank()
    if abs(deg) < 0.5:
        C.stamp(legs, f, RL.layer(P["leg"]), 0, by)
    else:
        C.turned(legs, f, P["leg"], deg, (rx, ry), (rx, ry + by))
    legs[C.origin(f)[1] + L["paw_y"] - lift + 2:] = 0
    m = legs[..., 3] > 0
    can[m] = legs[m]
    C.stamp(can, f, RL.layer(P["paw"]), gx, -lift)


def dragon_run(C, RL, t, far_wing=0.0, near_wing=0.0, tail=0.0, head=(0, 0)):
    """Frame t of the run: the legs (far, then near) under everything else as dragon() draws it standing - the wings
    and the tail turned about their roots, the head moved - with the body RUN_BOB rows up."""
    f, m = C.dragon, C.dragon.masks
    can = C.blank()
    by = RUN_BOB[t]
    for name in ("far_hind", "far_fore", "near_hind", "near_fore"):
        gx, lift = run_paw(name, t)
        run_leg(C, can, RL, name, gx, lift, by)

    def part(name, deg):
        pm = m[name] & ~RL.allcut
        if deg:
            C.turned(can, f, pm, deg, D_ROOTS[name], D_ROOTS[name], 0, by)
        else:
            C.stamp(can, f, RL.layer(pm), 0, by)

    part("far_wing", far_wing)
    part("tail", tail)
    body = m["body"] | m["far_fore"] | m["near_fore"] | m["near_hind"] | m["far_hind"]
    C.stamp(can, f, RL.layer(body & ~RL.allcut), 0, by)
    part("near_wing", near_wing)
    C.stamp(can, f, RL.layer((m["head"] | m["jaw"]) & ~RL.allcut), head[0], by + head[1])
    can = seal(can, C.outline)
    can[C.rig.GY:] = 0
    return can


def dragon_fly(C):
    """R's flight and landing (League's Spell4_Intro / Spell4: the dragon in the air, both wings beating wide, the claws
    reaching forward, then coming down onto the target with the wings spread): two beats in the air, the touch-down,
    landed (the ult puts them after her leap; the add-on's whole-body dragon can use them alone)."""
    p = lambda **k: dragon(C, **k)
    return [p(lift=9, far_wing=-28, near_wing=14, swipe=30, tail=-10, head=(1, -1)),
            p(lift=11, far_wing=-6, near_wing=-8, swipe=36, tail=-6, head=(1, 0)),
            p(lift=4, far_wing=-22, near_wing=12, swipe=20, tail=-8, head=(2, 0)),
            p(dx=1, far_wing=-12, near_wing=8, swipe=-6, tail=-3, head=(1, 1))]


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
    # run (League's run1: a bounding gallop, the wings beating, the tail swinging): the legs stepping under the body in
    # four beats (RunLegs, dragon_run), the body bobbing a row, the wings beating, the head bobbing, the tail swinging
    RL = RunLegs(C.dragon)
    beat = [-6, -12, -6, 4, 8, 4, -2, -4]
    tail = [-3, -5, -3, 0, 3, 5, 3, 0]
    head = [(1, 0), (1, -1), (1, 0), (1, 1), (1, 0), (1, -1), (1, 0), (1, 1)]
    out["d_run"] = [dragon_run(C, RL, k, far_wing=b, near_wing=-b * 0.5, tail=t, head=h)
                    for k, (b, t, h) in enumerate(zip(beat, tail, head))]
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
    out["d_fly"] = dragon_fly(C)
    # the death: struck back with the head thrown up, the fire taking the dragon (a flash), and she falls as herself
    # (her death's stagger, kneel and collapse) - the dragon's own sinking squashed its legs into the body
    q = lambda name, **k: pose(C, name, **k)
    out["d_dead"] = [p(dx=-2, head=(-1, -1), far_wing=-6, near_wing=6, flash=True),
                     p(dx=-1, far_wing=6, near_wing=10, flash=True),
                     q("stagger", flash=True), q("kneel"), q("collapse"), q("collapse")]
    return out


def human_frames(C):
    h = lambda **k: human(C, **k)
    q = lambda name, **k: pose(C, name, **k)
    d = lambda **k: dragon(C, **k)
    out = {}
    # idle (League's Idle1: she stands breathing, the tail swaying a little): the rows above the waist settle a row and
    # rise again (legs and tail untouched: Mel's rule, 「上下摆动导致腿部变形」)
    out["idle"] = [h(breath=b) for b in (0, 0, 1, 1, 1, 1, 0, 0)]
    out["hit"] = [h(dx=-2, flash=True), h(dx=-1)]
    # run (League's Run: the near foot landing, carried by it with the far knee up, the far foot landing, carried by it)
    out["run"] = [q("run1"), q("run2"), q("run3"), q("run4")]
    # auto attack (League's Attack1: sunk low, rising with the far claw raised over her head, the claw slashed down in
    # front - the hit - and back to standing)
    out["attack"] = [q("crouch"), q("rise"), q("slash", dx=1), q("slash"), h()]
    # Q's first strike (League's Spell1 Attack1: the same rise and slash, longer, lunging further; the fire slash is
    # drawn in at the slash)
    out["skill"] = [q("crouch"), q("rise"), q("slash", dx=2), q("slash", dx=1), h()]
    # Q's second strike (League's Spell1 Attack2: a somersault forward with the tail swinging over her head, landing
    # low with the tail swept round the front - the ring of fire - then up)
    out["skill_b"] = [q("crouch"), q("flip", lift=8), q("sweep"), q("sweep"), h()]
    # E Molten Burst (League's Spell3: sunk, then lunging with the far arm thrust out as the fireball leaves)
    out["skill2"] = [q("crouch"), q("throw"), q("throw", dx=-1), h()]
    # R Dragon's Descent (League's Spell4 Cast: she crouches and leaps, the fire wraps her - a flash - and the dragon
    # flies on to the target and lands; the dragon's flight is d_fly's)
    fly = dragon_fly(C)
    out["ult"] = [q("crouch"), q("leap", lift=6), q("leap", lift=10, flash=True)] + fly
    # the dragon running out (League's ShyvanaDragon Spell4 out: the wings folding, the fire, her crouching out of it)
    out["revert"] = [d(far_wing=10, near_wing=12), d(far_wing=16, near_wing=20, flash=True), q("crouch", flash=True),
                     q("crouch"), h()]
    # death (League's Death: struck back, sinking to her knees, fallen forward on her hands)
    out["dead"] = [q("stagger"), q("kneel"), q("collapse"), q("collapse")]
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


BAKED = {"skill", "d_skill"}    # the tags shyvana_bake.json draws into


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
        C.rig.review(C.rig.bake(acts) if BAKED <= set(acts) else acts, a.review)
        return
    # Q's slashes drawn into her frames and the dragon's (assets/source/native/shyvana_bake.json; import_shyvana_fx.py
    # first): they turn with her, the red side included
    C.rig.export(C.rig.bake(acts))


if __name__ == "__main__":
    main()

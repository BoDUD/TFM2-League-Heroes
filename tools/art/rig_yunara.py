#!/usr/bin/env python3
"""league_yunara's action frames posed from the approved design's own squares (no Codex strips: the user, 2026-10-17,
「codex交付了 动作帧你参考塔姆怎么做的吧 做到完美后喊我review」; league_tahmkench's and league_aphelios's way).

    python tools/art/rig_yunara.py --review DIR      # every tag on the canvas, 4x / 2x sheets + a GIF per tag + checks
    python tools/art/rig_yunara.py                   # the PPU frames -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero yunara && python tools/art/ppu_hd.py --hero yunara

The design (assets/source/yunara/hd/design.png, 33 x 60 squares at the final PPU 1.5: Codex's step-1 take 2 with its
beads taken off and whole rows / columns deleted, tools/art/design_yunara.py) is posed without rescaling; her six bronze
beads are one 6 x 6 bead (hd/bead.png) turned by quarter turns, floating where hd/beads.json puts them. Its parts are
told by fixed square ranges on the design (the colour-class map in design_yunara's notes): the violet dragon-head bead
with its streamers (it floats below her far hand), the far forearm (bracer and glove, hanging from the elbow), the two
trouser legs (split at the crease, column 12) with their sandals, and the body (head, ornaments, top, the near arm with
its hand on the belt, the belt and its front panel). Moves are lossless (memory no-deformation-lossless-poses):
whole-part translation, exact quarter turns and flips, whole-row shifts (a trouser leg swinging about the hip),
layering (the body sinking over the legs).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


SRC = os.path.join(ROOT, "assets", "source", "yunara")
STEM = os.path.join(ROOT, "league", "champions", "league_yunara")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
PPU = 1.5
FEET = 11                         # 1x rows from the pivot down to the ground row
DESIGN = load(os.path.join(SRC, "hd", "design.png"))
BEAD = load(os.path.join(SRC, "hd", "bead.png"))
BEADS = json.load(open(lp(os.path.join(SRC, "hd", "beads.json")), encoding="utf-8"))
DH, DW = DESIGN.shape[:2]         # 60 x 33
OUTLINE = (8, 2, 14)

# ------------------------------------------------------------------------------------------------- the canvas
CW, CH = 150, 120
SOLE = 100                        # the canvas row of the design's last row (the soles)
TORSO_X = 11                      # the design column over the pivot: her torso's and feet's middle
PIV_X = 66                        # the pivot column on the canvas
OX, OY = PIV_X - TORSO_X, SOLE - (DH - 1)   # where the design's (0, 0) goes standing
CORNER = (PIV_X + 0.5, SOLE + 1)  # the pivot column and the ground line, in squares

# ------------------------------------------------------------------------------------------------- parts
BODY, DRAGON, FORE, LEG_N, LEG_F = range(5)
WAIST = 35                        # the trousers start under the belt and its front panel
SPLIT = 12                        # the crease between the trouser legs (the near leg keeps it as its edge)
ELBOW = (26, 20)                  # where the far forearm hangs from the upper arm (design row, column)


def labels():
    op = DESIGN[..., 3] > 0
    R, C = np.mgrid[0:DH, 0:DW]
    lab = np.full((DH, DW), -1)
    lab[op] = BODY
    lab[op & (R >= 35) & (C >= 22)] = DRAGON                       # the streamers and the dragon head
    lab[op & (R >= 26) & (R <= 34) & (C >= 20) & ~((R >= 35) & (C >= 22))] = FORE
    panel = (R <= 42) & (C <= 11)                                  # the belt's front panel and the spiral hang over
    legs = op & (R >= WAIST + 1) & ~panel & (C <= 21)
    lab[legs & (C <= SPLIT)] = LEG_N
    lab[legs & (C > SPLIT)] = LEG_F
    lab[op & (R >= 55) & (C <= 11)] = LEG_N                       # the near sandal
    lab[op & (R >= 55) & (C >= 12)] = LEG_F                       # the far sandal
    return lab


LAB = labels()


def part(*ks):
    return np.isin(LAB, ks)


def leg_rows(k):
    ys = np.nonzero((LAB == k).any(1))[0]
    return int(ys.min()), int(ys.max())


# ------------------------------------------------------------------------------------------------- composing
def blank():
    return np.zeros((CH, CW, 4), np.uint8)


def put(dst, src, mask, dx, dy, under=False):
    """src's squares under mask, moved (dx, dy), onto dst (under: only where dst is empty)."""
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
    if under:
        free = dst[ty, tx, 3] == 0
        ys, xs, ty, tx = ys[free], xs[free], ty[free], tx[free]
    dst[ty, tx] = src[ys, xs]


def stamp(can, img, x, y, under=False):
    """img's opaque squares with its top-left on canvas (x, y)."""
    put(can, img, img[..., 3] > 0, x, y, under)


KNEE = 0.45                            # the knee's place down the trouser leg (hip 0, sole 1)
UNDERLAY = 3                           # rows of each leg's top kept standing under the swung legs


def knee_row(k):
    top, bot = leg_rows(k)
    return top + int(round((bot - top) * KNEE))


SANDAL = 55                            # the first sandal row: the sandal moves whole (flat), never slanted


def swung(k, knee=0, foot=0, lift=0):
    """Leg k as (squares, mask, pad) on the design grid, two bones and lossless: the thigh (hip to KNEE of the leg) by
    whole-row shifts growing from 0 at the hip to `knee` columns at the knee, the shin (knee to the hem) shifted from
    `knee` to `foot` columns at the hem and lifted `lift` rows (it rides over the thigh where they meet), the sandal
    under it moved whole by (foot, -lift)."""
    top, bot = leg_rows(k)
    kr = knee_row(k)
    m = LAB == k
    P = 24
    out = np.zeros((DH + 2 * P, DW + 2 * P, 4), np.uint8)
    om = np.zeros(out.shape[:2], bool)
    for r in range(top, kr):
        dx = int(round(knee * (r - top) / max(1, kr - top)))
        xs = np.nonzero(m[r])[0]
        out[r + P, xs + dx + P] = DESIGN[r, xs]
        om[r + P, xs + dx + P] = True
    hem = SANDAL - 1
    for r in range(kr, bot + 1):
        dx = foot if r >= SANDAL else int(round(knee + (foot - knee) * (r - kr) / max(1, hem - kr)))
        xs = np.nonzero(m[r])[0]
        out[r - lift + P, xs + dx + P] = DESIGN[r, xs]
        om[r - lift + P, xs + dx + P] = True
    return out, om, P


def bead_img(turn):
    return np.rot90(BEAD, turn % 4).copy()


def beads_at(spots, front=()):
    """A drawing callable: bead k (BEADS order) at spots[k] = (row, col, turn) on the design grid (its centre), drawn
    behind the figure unless k is in `front`."""
    def draw(can, x0, y0, behind=True):
        for k, (r, c, t) in enumerate(spots):
            if (k in front) == behind:
                continue
            img = bead_img(t)
            h, w = img.shape[:2]
            stamp(can, img, x0 + int(round(c - (w - 1) / 2)), y0 + int(round(r - (h - 1) / 2)), under=behind)
    return draw


# where the beads float in the idle (design rows, columns of a bead's centre): hd/beads.json's spots moved clear of her
# (by the tassel, the glove and the streamers the beads touched her, and the 1-square gaps read as specks), three on
# each side as in the picked design
IDLE_BEADS = [(15, -4), (28, -8), (42, -4), (18, 26), (27, 31), (46, 37)]


def idle_spots(t=0.0, lift=0.0):
    """The beads round her, bobbing (t: 0..1 of the idle's cycle) and turning a quarter every quarter cycle, each a step
    behind the one before."""
    out = []
    for k, (r, c) in enumerate(IDLE_BEADS):
        ph = 2 * np.pi * (t + k / len(IDLE_BEADS))
        dy = int(round(1.4 * np.sin(ph))) - int(round(lift))
        turn = BEADS[k]["turn"] + int(np.floor(4 * t + k / 2.0)) * (1 if k % 2 else -1)
        out.append((r + dy, c, turn))
    return out


class Frame:
    """A posed figure (the canvas without the beads: they are finished pictures and stay out of the tidying - its
    hole filling would close the gaps between a bead and the body) and where its beads float: spots in design squares
    from the origin (x0, y0) on the canvas, the ones in `front` drawn over the figure."""

    def __init__(self, can, spots, x0, y0, front=()):
        self.can, self.spots, self.x0, self.y0, self.front = can, spots, x0, y0, front

    def done(self, base):
        """The figure finished, then its beads laid on one at a time (behind first): a bead that would leave a small
        gap (a 1-4 square hole between it and her or another bead, or a stray outline square) is nudged to the
        nearest place within NUDGE squares that leaves none."""
        out = finish(self.can, base)
        order = [k for k in range(len(self.spots)) if k not in self.front] + list(self.front)
        for k in order:
            r, c, t = self.spots[k]
            img = bead_img(t)
            h, w = img.shape[:2]
            behind = k not in self.front
            h0, o0 = small_holes(out), int(orphans(out).sum())
            best = None
            for dy, dx in NUDGES:
                trial = out.copy()
                stamp(trial, img, self.x0 + int(round(c - (w - 1) / 2)) + dx, self.y0 + int(round(r - (h - 1) / 2)) + dy,
                      under=behind)
                if small_holes(trial) <= h0 and int(orphans(trial).sum()) <= o0:
                    best = trial
                    break
            out = best if best is not None else trial_at(out, img, self.x0, self.y0, r, c, behind)
        out[SOLE + 1:] = 0
        return out


NUDGES = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 2), (0, -2), (2, 0),
          (-2, 0)]


def trial_at(can, img, x0, y0, r, c, behind):
    out = can.copy()
    h, w = img.shape[:2]
    stamp(out, img, x0 + int(round(c - (w - 1) / 2)), y0 + int(round(r - (h - 1) / 2)), under=behind)
    return out


def pose(bob=0, dx=0, legs=((0, 0, 0), (0, 0, 0)), fore=None, dragon=(0, 0, 0), beads=None, front=(), lift=0,
         hide=(), extra=()):
    """One frame (a Frame): the body (all but the legs) bob rows down over the legs and dx columns on, the whole
    figure lift rows up; the near / far leg (knee columns, foot columns, lift rows: see swung); fore: None (as drawn) or
    a callable drawing the far forearm (gets the canvas and the body's origin); dragon: (dx, dy, quarter turns) of the
    dragon bead; beads: bead spots (idle_spots by default) and the ones in front; parts in `hide` left out; extra:
    callables run last."""
    can = blank()
    x0, y0 = OX + dx, OY - lift
    spots = idle_spots() if beads is None else beads
    # the legs' tops as they stand, under everything (nothing opens between the belt and a swinging leg)
    for k in (LEG_F, LEG_N):
        if k in hide:
            continue
        top = leg_rows(k)[0]
        put(can, DESIGN, (LAB == k) & (np.arange(DH)[:, None] < top + UNDERLAY), x0, y0)
    for k, spec in ((LEG_F, legs[1]), (LEG_N, legs[0])):
        if k in hide:
            continue
        src, m, P = swung(k, *spec)
        put(can, src, m, x0 - P, y0 - P)
    body = part(BODY) & ~part(*hide)
    put(can, DESIGN, body, x0, y0 + bob)
    if FORE not in hide:
        if fore is None:
            put(can, DESIGN, LAB == FORE, x0, y0 + bob)
        else:
            fore(can, x0, y0 + bob)
    if DRAGON not in hide:
        ddx, ddy, dt = dragon
        if dt % 4 == 0:
            put(can, DESIGN, LAB == DRAGON, x0 + ddx, y0 + bob + ddy)
        else:
            img, (r0, c0) = turned(LAB == DRAGON, dt)
            stamp(can, img, x0 + c0 + ddx, y0 + bob + r0 + ddy)
    for f in extra:
        f(can, x0, y0 + bob)
    return Frame(can, spots, x0, y0 + bob, front)


def turned(mask, k):
    """The design's squares under mask, cut to their box and turned k quarter turns counter-clockwise (exact)."""
    ys, xs = np.nonzero(mask)
    sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    sub[ys - ys.min(), xs - xs.min()] = DESIGN[ys, xs]
    return np.rot90(sub, k).copy(), (int(ys.min()), int(xs.min()))


def cut_ground(fr):
    fr.can[SOLE + 1:] = 0
    return fr


def flash(can, k=0.55):
    out = can.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------------- tidying
def cracks(a):
    out = a.copy()
    for _ in range(2):
        op = out[..., 3] > 0
        lr = np.zeros_like(op)
        lr[:, 1:-1] = op[:, :-2] & op[:, 2:]
        ud = np.zeros_like(op)
        ud[1:-1] = op[:-2] & op[2:]
        dark = op & np.all(out[..., :3] == OUTLINE, -1)
        coloured = ndimage.convolve((op & ~dark).astype(int), np.ones((3, 3), int), mode="constant") > 0
        m = (lr | ud) & ~op & coloured
        if not m.any():
            break
        out[m, :3] = OUTLINE
        out[m, 3] = 255
    return out


def tidy(a, hole=10, speck=4):
    """The outline closed round moved edges (strips.complete_outline), 1-square slits closed, small enclosed holes
    filled with their commonest neighbour, loose specks off, nothing under the soles."""
    out = G.complete_outline(cracks(a), color=OUTLINE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > hole:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < speck:
                out[lbl == k] = 0
    out[SOLE + 1:] = 0
    return out


def orphans(can):
    op = can[..., 3] > 0
    dark = op & np.all(can[..., :3] == OUTLINE, -1)
    nb = ndimage.convolve((op & ~dark).astype(int), np.ones((3, 3), int), mode="constant")
    return dark & (nb == 0)


def deorphan(can, base, reach=4):
    out = can.copy()
    near = ndimage.binary_dilation(orphans(base), structure=np.ones((2 * reach + 1, 2 * reach + 1)))
    pieces = lambda a: ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))[1]
    n0 = pieces(out)
    for y, x in np.argwhere(orphans(out) & ~near):
        keep = out[y, x].copy()
        out[y, x] = 0
        if pieces(out) > n0:
            out[y, x] = keep
    return out


def unblot(can, base, reach=4):
    out = can.copy()
    near = ndimage.binary_dilation(orphans(base), structure=np.ones((2 * reach + 1, 2 * reach + 1)))
    for _ in range(4):
        op = out[..., 3] > 0
        dark = op & np.all(out[..., :3] == OUTLINE, -1)
        four = np.zeros_like(op)
        four[1:-1, 1:-1] = op[:-2, 1:-1] & op[2:, 1:-1] & op[1:-1, :-2] & op[1:-1, 2:]
        lump = orphans(out) & four & ~near
        if not lump.any():
            break
        col = op & ~dark
        for y, x in np.argwhere(lump):
            win = out[max(0, y - 2):y + 3, max(0, x - 2):x + 3]
            m = col[max(0, y - 2):y + 3, max(0, x - 2):x + 3]
            if m.any():
                vals, cnt = np.unique(win[m][:, :3], axis=0, return_counts=True)
                out[y, x, :3] = vals[cnt.argmax()]
    return out


def finish(can, base):
    a = tidy(can)
    for _ in range(4):
        b = tidy(deorphan(unblot(a, base), base))
        if (b == a).all():
            break
        a = b
    return a


# ------------------------------------------------------------------------------------------------- idle, hit, run
BREATH = [0, 0, 1, 1, 2, 2, 1, 1]     # rows the body above the waist rises (the BP idle rule: >= 2 rows)
IDLE_MS = 150


def breathe(k, t, **kw):
    """The design standing (pose(**kw)), everything above the waist (the far forearm and the dragon bead carried
    whole) k rows up; the squares left open over the waist take the square under them. t: the beads' phase."""
    fr = pose(beads=[], **kw)
    can = fr.can
    out = can.copy()
    if k:
        up = np.zeros(can.shape[:2], bool)
        up[:OY + WAIST] = can[:OY + WAIST, :, 3] > 0
        carried = np.zeros(can.shape[:2], bool)
        for p_ in (FORE, DRAGON):
            ys, xs = np.nonzero(LAB == p_)
            carried[ys + OY, xs + OX] = True
        up |= carried
        ys, xs = np.nonzero(up)
        out[ys, xs] = 0
        out[ys - k, xs] = can[ys, xs]
        hole = (out[..., 3] == 0) & up & ~carried
        for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
            for x in np.nonzero(hole[y])[0]:
                if out[y + 1, x, 3] > 0:
                    out[y, x] = out[y + 1, x]
    return Frame(out, idle_spots(t, lift=k), OX, OY)


RUN_MS = 125                           # League's run_base: 1.0 s a cycle (run@1000 = run@0, tools/lol/anim_graph.py)
# League's run at game size (tools/lol/pose_joints.py assets/source/yunara/poses.json --tag run, game px from the
# pivot): per frame the root's y and, per leg, the foot's x from its hip and its height off the ground (L = her near
# leg). League's numbers are game px (1.5 squares each); her trouser legs are each 10 squares wide and side by side, so
# the far leg shows behind the near one only when the feet part by more than a leg's width: the columns at LEG_K squares
# a game px (0.55 and 0.95 hid the far leg in frames 4-6), the lift by LIFT_K, the bob by BOB_K; the upper body one
# column ahead of the legs (a lean by translation, no shear).
LEAGUE_RUN = [  # (root y, (near foot dx, lift), (far foot dx, lift)), game px
    (-12.2, (-6.6, 12.7), (5.0, 0.0)),
    (-8.4, (-3.6, 8.7), (0.7, 0.6)),
    (-9.8, (1.4, 3.6), (-3.9, 0.8)),
    (-10.1, (6.3, 1.6), (-7.8, 1.0)),
    (-15.3, (7.9, 5.5), (-9.4, 11.2)),
    (-12.3, (6.5, 0.0), (-9.2, 12.4)),
    (-8.4, (2.9, 0.6), (-4.2, 7.9)),
    (-9.6, (-1.1, 0.6), (1.5, 4.4)),
]
LEG_K, LIFT_K, BOB_K = 1.3, 0.6, 0.45


TRAIL = [(9, -3), (6, -9), (5, -15), (7, -21), (11, -26), (16, -29)]   # behind her head, curving down (League's
                                                                       # run: the beads stream behind her at head height)


def trail_spots(i, n=8):
    """The beads streaming behind her as she runs: a wave runs down the trail, each bead spinning."""
    out = []
    for k, (y, x) in enumerate(TRAIL):
        dy = int(round(1.5 * np.sin(2 * np.pi * (i / n) - k * 0.8)))
        out.append((y + dy, x, BEADS[k]["turn"] + (i // 2) * (1 if k % 2 else -1)))
    return out


def run_frames(**kw):
    tops = [h for h, _, _ in LEAGUE_RUN]
    top = min(tops)
    out = []
    for i, (hy, n, f) in enumerate(LEAGUE_RUN):
        leg = lambda t: (int(round(t[0] * LEG_K * 0.5)), int(round(t[0] * LEG_K)), int(round(t[1] * LIFT_K)))
        bob = int(round((hy - top) * BOB_K))
        swing = int(round(np.clip(-f[0] * LEG_K / 5.0, -2, 2)))
        out.append((pose(bob=bob, dx=1, legs=(leg(n), leg(f)), beads=trail_spots(i), dragon=(swing, 0, 0), **kw),
                    RUN_MS))
    return out


# ------------------------------------------------------------------------------------------------- arms, beads, poses
def fore_fwd(dx=0, dy=0):
    """The far forearm (bracer and glove, hanging from the elbow in the design) turned a quarter counter-clockwise about
    the elbow: pointing forward, the hand at its front, the lit side up; its elbow end on ELBOW (+dx, dy)."""
    img, (r0, c0) = turned(LAB == FORE, 1)

    def draw(can, x0, y0):
        # the turned piece's bottom-left corner is the old elbow; seat it on the elbow, three rows down (the forearm
        # centred on the elbow's row, not standing on it)
        h = img.shape[0]
        stamp(can, img, x0 + ELBOW[1] + dx, y0 + ELBOW[0] - h + 3 + dy)
    return draw


def fore_up(dx=0, dy=0):
    """The far forearm flipped up about the elbow (top to bottom: exact, the lit side kept): the hand over the elbow."""
    ys, xs = np.nonzero(LAB == FORE)
    sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    sub[ys - ys.min(), xs - xs.min()] = DESIGN[ys, xs]
    img = sub[::-1].copy()

    def draw(can, x0, y0):
        stamp(can, img, x0 + int(xs.min()) + dx, y0 + ELBOW[0] + 2 - img.shape[0] + dy)
    return draw


FWD_HAND = (-6, 5)                     # how far the hand moves (rows, columns) when the forearm turns forward


def lerp_spots(a, b, t):
    return [(int(round(ra + (rb - ra) * t)), int(round(ca + (cb - ca) * t)), ta if t < 0.5 else tb)
            for (ra, ca, ta), (rb, cb, tb) in zip(a, b)]


ARC = [(4, -8), (-3, -3), (-7, 4), (-8, 12), (-6, 20), (-1, 26)]     # the beads over her head (League's attack arc)


def arc_spots(shift=0, turn=0, lift=0):
    return [(r - lift, c + shift, BEADS[k]["turn"] + turn + k) for k, (r, c) in enumerate(ARC)]


def ring_spots(angle, radius=1.0, cy=24, cx=11, rx=21, ry=24, turn=0):
    """The beads on an ellipse round her (centre cy, cx in design squares), spread evenly from `angle` (radians)."""
    out = []
    for k in range(len(BEADS)):
        a = angle + 2 * np.pi * k / len(BEADS)
        out.append((int(round(cy + ry * radius * np.sin(a))), int(round(cx + rx * radius * np.cos(a))),
                    BEADS[k]["turn"] + turn + k))
    return out


def orbit(angle, cy=33, cx=11, rx=24, ry=7, turn=0):
    """The beads on a flat ring round her (centre cy, cx; radii rx, ry in squares), spread evenly from `angle`: (spots,
    the ones on the near half, drawn in front of her)."""
    spots, front = [], []
    for k in range(len(BEADS)):
        a = angle + 2 * np.pi * k / len(BEADS)
        spots.append((int(round(cy + ry * np.sin(a))), int(round(cx + rx * np.cos(a))), BEADS[k]["turn"] + turn + k))
        if np.sin(a) > 0.2:
            front.append(k)
    return spots, tuple(front)


def ground_spots(dx=0):
    """The beads fallen round her on the ground line (their bottoms on the soles' row)."""
    xs = [-14, -6, 30, 38, 22, -20]
    return [(DH - 1 - 3, x + dx, BEADS[k]["turn"] + k) for k, x in enumerate(xs)]


STANCE = ((-3, -7, 0), (3, 7, 0))      # the wide horse stance: the near leg back, the far leg forward, straight out


def lying(fr, cw=True, dx=0):
    """The figure turned a quarter (clockwise: she falls forward on her front, the head ahead), laid on the ground
    line (a canvas; the caller gives the beads)."""
    can = fr.can
    ys, xs = np.nonzero(can[..., 3] > 0)
    sub = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    t = np.rot90(sub, -1 if cw else 1).copy()
    out = blank()
    h, w = t.shape[:2]
    stamp(out, t, PIV_X - w // 2 + dx, SOLE + 1 - h)
    return out


def flipped(fr, k, lift=0, dx=0):
    """The figure turned k quarter turns counter-clockwise about its middle, its middle `lift` rows over its standing
    middle (the R dash's flip)."""
    can = fr.can
    ys, xs = np.nonzero(can[..., 3] > 0)
    cy, cx = (ys.min() + ys.max()) / 2.0, (xs.min() + xs.max()) / 2.0
    sub = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    t = np.rot90(sub, k).copy()
    out = blank()
    h, w = t.shape[:2]
    stamp(out, t, int(round(cx - (w - 1) / 2.0)) + dx, int(round(cy - (h - 1) / 2.0)) - lift)
    return out


def attack_frames():
    """Every cast strip: (Frame, ms). Release ticks (tools/kit/build_yunara.py): the attack's bead leaves on tick 8
    (133 ms, the start of frame 3), W's bead on tick 15 (250 ms, frame 5), the laser hits on tick 34 (567 ms)."""
    out = {}
    idle0 = idle_spots()
    hand = dict(dragon=(FWD_HAND[1] + 1, FWD_HAND[0] + 1, 0))
    # attack: the beads rise into an arc over her head, the palm pushed forward (League's attack1 / attack2)
    out["attack"] = [(pose(dx=-1, beads=lerp_spots(idle0, arc_spots(-2), 0.5)), 67),
                     (pose(dx=-1, beads=arc_spots(-2, 1)), 66),
                     (pose(dx=1, fore=fore_fwd(1), beads=arc_spots(2, 2), **hand), 100),
                     (pose(dx=1, fore=fore_fwd(1), beads=arc_spots(3, 3), **hand), 84),
                     (pose(beads=lerp_spots(arc_spots(1, 4), idle0, 0.5)), 83)]
    # W: crouch with the beads whirling, a hop, the wide stance and the palm thrust (the bead leaves at 250 ms)
    def orb(a, **k):
        sp, fr = orbit(a, **k)
        return dict(beads=sp, front=fr)
    out["skill"] = [(pose(bob=2, **orb(0.3, cy=34, rx=20)), 67),
                    (pose(lift=4, legs=((0, 0, 2), (0, 0, 2)), **orb(1.1, cy=30, rx=22)), 67),
                    (pose(bob=3, legs=STANCE, **orb(1.9, cy=35)), 66),
                    (pose(bob=3, dx=1, legs=STANCE, fore=fore_fwd(1), **hand, **orb(2.5, cy=35)), 50),
                    (pose(bob=3, dx=1, legs=STANCE, fore=fore_fwd(2), **hand, **orb(3.0, cy=35)), 100),
                    (pose(bob=1, legs=((-1, -3, 0), (1, 3, 0)), beads=lerp_spots(orbit(3.4, cy=35)[0], idle0, 0.5)),
                     100)]
    # R's W, the laser: crouch, the dragon raised over her head while the beads ring it, the stance and the thrust
    over = dict(dragon=(-14, -56, 0), fore=fore_up())

    def halo(a):
        return orbit(a, cy=-14, cx=11, rx=24, ry=8)[0]
    out["skill_r"] = [(pose(bob=2, beads=lerp_spots(idle0, halo(0.0), 0.5)), 100),
                      (pose(lift=1, beads=halo(0.6), **over), 100),
                      (pose(lift=1, beads=halo(1.2), **over), 100),
                      (pose(lift=1, beads=halo(1.8), **over), 100),
                      (pose(bob=3, dx=1, legs=STANCE, fore=fore_fwd(2), beads=arc_spots(3, 1), **hand), 100),
                      (pose(bob=3, dx=1, legs=STANCE, fore=fore_fwd(2), beads=arc_spots(4, 2), **hand), 100),
                      (pose(bob=1, legs=((-1, -3, 0), (1, 3, 0)), beads=lerp_spots(arc_spots(2, 3), idle0, 0.5)), 67)]
    # E: a quick stride forward, the beads streaming behind
    out["skill2"] = [(pose(dx=2, legs=((-2, -5, 2), (2, 5, 0)), beads=trail_spots(0)), 100),
                     (pose(dx=3, legs=((2, 4, 0), (-2, -5, 2)), beads=trail_spots(4)), 100)]
    # R's E: a back flip (whole quarter turns: exact), the beads streaming where she was
    crouch = pose(bob=2, beads=[])
    # (in place: the game moves her - MoveBack - so a sprite that also travelled would cover the distance twice)
    out["skill2_r"] = [(Frame(crouch.can, trail_spots(0), crouch.x0, crouch.y0), 53),
                       (Frame(flipped(pose(beads=[]), 1, lift=8), trail_spots(1), OX, OY), 53),
                       (Frame(flipped(pose(beads=[]), 2, lift=12), trail_spots(3), OX, OY), 53),
                       (Frame(flipped(pose(beads=[]), 3, lift=8), trail_spots(5), OX, OY), 53),
                       (pose(bob=2, beads=trail_spots(7)), 55)]
    # R: the palm forward, then the beads spread into a wide ring round her, rising a row
    out["ult"] = [(pose(fore=fore_fwd(1), beads=lerp_spots(idle0, orbit(0.0, cy=30, rx=20)[0], 0.5), **hand), 100),
                  (pose(fore=fore_up(), **orb(0.5, cy=26, rx=22, ry=8)), 100),
                  (pose(lift=1, fore=fore_up(), **orb(1.0, cy=20, rx=24, ry=9)), 100),
                  (pose(lift=1, fore=fore_up(), **orb(1.5, cy=14, rx=25, ry=9)), 100),
                  (pose(**orb(2.0, cy=24, rx=24, ry=9)), 100)]
    # death: the blow, a stagger, down on her knees (sunk into the ground line), falling forward on her front, still

    def drop(k):
        return [(r + k, c, t) for r, c, t in idle_spots()]
    kneel = cut_ground(pose(lift=-12, beads=drop(8), hide=(DRAGON,)))
    dimg, _ = turned(LAB == DRAGON, -1)                # the dragon bead fallen on its side beside her
    stamp(kneel.can, dimg, PIV_X + 16, SOLE + 1 - dimg.shape[0], under=True)
    flat = lying(pose(beads=[], hide=(DRAGON,)))
    stamp(flat, dimg, PIV_X + 22, SOLE + 1 - dimg.shape[0], under=True)
    out["dead"] = [(pose(dx=-2, beads=drop(1)), 100), (pose(dx=-2, bob=4, beads=drop(4)), 120), (kneel, 150),
                   (Frame(flat, ground_spots(), OX, OY), 150), (Frame(flat.copy(), ground_spots(), OX, OY), 400)]
    return out


GLOW = (248, 194, 68)                  # the design's light gold
HALO = (10, 11, 16, 16)                # the halo's centre (design row, column) and radii (rows, columns): a ring round
                                       # her head and shoulders, wider than the ornaments so it shows


def r_form(can, x0=None, y0=None):
    """A finished frame in the R form: one square of light gold round the whole silhouette, and a thin ring (the halo)
    behind her head; x0 / y0: where the design's origin is on this canvas (the halo follows the head)."""
    out = can.copy()
    op = out[..., 3] > 0
    rim = ndimage.binary_dilation(op, structure=np.ones((3, 3))) & ~op
    out[rim] = (*GLOW, 255)
    if x0 is not None:
        cy, cx, ry, rx = HALO
        Y, X = np.mgrid[0:out.shape[0], 0:out.shape[1]]
        d = ((Y - (y0 + cy)) / ry) ** 2 + ((X - (x0 + cx)) / rx) ** 2
        ring = (d >= 0.82) & (d <= 1.18) & (out[..., 3] == 0)
        out[ring] = (*GLOW, 255)
    # the rim closed small gaps between a bead and her: they glow too
    op = out[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for k in range(1, n + 1):
        if (lbl == k).sum() <= 4:
            out[lbl == k] = (*GLOW, 255)
    out[SOLE + 1:] = 0
    return out


def actions():
    acts = {"idle": [(breathe(b, i / len(BREATH)), IDLE_MS) for i, b in enumerate(BREATH)], "run": run_frames()}
    base = tidy(pose(beads=[]).can)
    acts["hit"] = [(pose(dx=-3), 90), (pose(dx=-1), 120)]
    acts.update(attack_frames())
    origin = {t: [(f.x0, f.y0) for f, _ in fr] for t, fr in acts.items()}
    acts = {t: [(f.done(base), ms) for f, ms in fr] for t, fr in acts.items()}
    # the add-on's R form (addons/league_yunara view.rs: idle / run -> r_idle / r_run while the R buff lasts)
    for t in ("idle", "run"):
        acts["r_" + t] = [(r_form(can, *origin[t][j]), ms) for j, (can, ms) in enumerate(acts[t])]
    acts["hit"][0] = (flash(acts["hit"][0][0]), acts["hit"][0][1])
    return acts, base


# ------------------------------------------------------------------------------------------------- checks and review
def stats(can):
    op = can[..., 3] > 0
    n = ndimage.label(op, structure=np.ones((3, 3)))[1]
    holes = int((ndimage.binary_fill_holes(op) & ~op).sum())
    return n, holes, int(orphans(can).sum()), int(op.sum())


def small_holes(can, most=4):
    """Enclosed gaps of up to `most` squares (a missing square in the body, not the gap between a bead and her)."""
    op = can[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    sz = ndimage.sum(np.ones(lbl.shape), lbl, range(1, n + 1)) if n else []
    return int(sum(s_ for s_ in sz if s_ <= most))


def new_orphans(can, base, reach=4):
    o = orphans(can)
    near = ndimage.binary_dilation(orphans(base), structure=np.ones((2 * reach + 1, 2 * reach + 1)))
    return int((o & ~near).sum())


def checks(acts, base):
    """Per frame: pieces (8-connected; the beads float apart, so 1 + their count is right), enclosed holes and orphan
    outline squares beyond the design's own, colours outside the design's and the bead's palette (the hit flash aside),
    squares under the soles, opaque area against the design's."""
    pal = {tuple(int(v) for v in c) for c in DESIGN[DESIGN[..., 3] > 0][:, :3]}
    pal |= {tuple(int(v) for v in c) for c in BEAD[BEAD[..., 3] > 0][:, :3]}
    _, _, bo, ba = stats(base)
    for tag, fr in acts.items():
        rep = []
        for j, (can, _) in enumerate(fr):
            op = can[..., 3] > 0
            n, _, _, area = stats(can)
            holes = small_holes(can)
            orphan = new_orphans(can, base)
            extra = len({tuple(int(v) for v in c) for c in can[op][:, :3]} - pal)
            under = int(op[SOLE + 1:].sum())
            bad = holes or orphan or under or (extra and tag != "hit")
            rep.append(f"{j + 1}:{'!' if bad else ''}p{n} h{holes} o{orphan} c{extra} a{100 * area // ba}%")
        print(f"{tag:9s} " + "  ".join(rep))


def review(acts, out_dir, z=4):
    os.makedirs(out_dir, exist_ok=True)
    for tag, fr in acts.items():
        allc = np.stack([f for f, _ in fr])
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = ys.min() - 2, SOLE + 3, xs.min() - 2, xs.max() + 3
        tiles = []
        for f, _ in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
            tiles.append(bg.convert("RGB"))
        for scale, suffix in ((z, ""), (2, "_2x")):
            big = [t.resize((t.width * scale, t.height * scale), Image.NEAREST) for t in tiles]
            sheet = Image.new("RGB", (len(big) * (big[0].width + 6), big[0].height), (60, 60, 60))
            for i, t in enumerate(big):
                sheet.paste(t, (i * (t.width + 6), 0))
            sheet.save(os.path.join(out_dir, f"yunara_{tag}{suffix}.png"))
        small = [t.resize((t.width * 3, t.height * 3), Image.NEAREST) for t in tiles]
        pal_src = Image.new("RGB", (small[0].width, small[0].height * len(small)))
        for i, t in enumerate(small):
            pal_src.paste(t, (0, i * t.height))
        pal = pal_src.quantize(255, dither=Image.Dither.NONE)
        q = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in small]
        q[0].save(os.path.join(out_dir, f"yunara_{tag}.gif"), save_all=True, append_images=q[1:],
                  duration=[ms for _, ms in fr], loop=0, optimize=False)
    print("review ->", out_dir)


# ------------------------------------------------------------------------------------------------- the game's frames
ORDER = ["idle", "run", "attack", "skill", "skill_r", "skill2", "skill2_r", "ult", "hit", "dead", "r_idle", "r_run"]


def one_of(can, px, py, hw, hh, need=0.5):
    """The 1x frame: each game pixel the commonest colour of the PPU squares under it (half of them drawn or more)."""
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_hd(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


def down(can):
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot). The pivot: the pivot
    column, FEET 1x rows above the ground line."""
    px, py = CORNER[0], CORNER[1] - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh), color=OUTLINE)[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    return one, crop_hd(can, px, py, W, H)


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def export(acts):
    sheet = {}
    os.makedirs(lp(ORIG), exist_ok=True)
    for tag in ORDER:
        ones, hds = [], []
        for can, t in acts[tag]:
            one, hd = down(can)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"yunara_{tag}.png")))
        with open(lp(os.path.join(ORIG, f"yunara_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_yunara#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="the frames at 4x / 2x and a GIF per tag here (nothing written to the repo)")
    a = ap.parse_args()
    acts, base = actions()
    checks(acts, base)
    if a.review:
        review(acts, a.review)
        return
    export(acts)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Nilah's run legs, drawn on League's run the way league_shen's accepted run draws his (tools/art/fix_shen_strips.py
draw_leg / stride_frame; art-spec "Strips posed from the design's own parts": legs drawn on joints in the design's own
colours, the same drawing in every frame, the feet whole). What the reviews of the drawn versions (2026-10-14) asked
for, and how this draws it:
  * each bone is ONE drawing in its own frame (u along the bone, v across it, v > 0 its front): the leg's outline and
    every colour band are fixed in that frame, so a leg is the same drawing in every frame, only turned with its bone.
    The widths and bands are read off the side design's own legs row by row (the pack's 56 x 106 crop, the bones in
    DESIGN): NEAR is her left leg - the red sash down the thigh, the plum balloon bulging forward over the knee and back
    over the calf (18 squares at its widest), the teal strap down its front, two red cords curving round it where it
    gathers, a teal anklet, the bare ankle; FAR is her right leg - the red thigh with a fold, the bright teal knee
    guard (a cap, a dark wrap, a lower lip, its folds only part way round), the balloon behind with two red cords at its
    top, the teal wrap down its front, the teal shin, the bare ankle (the costume is not symmetric - the front design
    shows the same). The skirt panel and its border stay with the body (tools/art/run_nilah.py). Drawn on the design's
    own bones it gives the design's legs back (--review shows both);
  * clean edges: the silhouette from SUB x SUB samples a square, spurs and notches taken out, ONE outline square round
    it by 4-neighbours (one square thick on a slant, never two); shading bands are the leg's own edge rings; the cords,
    the strap's and the guard's lines are the 4-boundary of a region in the bone's frame (no chequer);
  * a balloon hangs: past SAG[0] degrees of a shin kicked back its bulk goes over to the bone's lower side (all of it
    by SAG[1]) - kept rigid, the calf's bulge rode on top of a level shin like a hump (「a purple log against gravity」);
  * the feet: a planted foot is the design's own slipper flat on the ground; a foot in the air under a shin kicked back
    more than TRAIL degrees points its toe back and down along the shin, TOE_OFF degrees nearer the vertical, its sole
    up (the slipper drawn at that turn from its own outline and colour bands, under the ankle) - League's trailing feet
    point 108-136 degrees; flat or tipped forward they folded the ankle at 116-130 degrees; other feet in the air flat;
  * the hips 0.7 squares apart, League's (the design's stance had them 6.5 apart: the far foot landed 6 squares behind
    the near one and the far leg disappeared under the near balloon in the second leap); the seat behind them is the
    design's own (run_nilah RUMP), so the far thigh swinging forward leaves no corner;
  * the far leg one step darker on the design's ramps all over, its rim the darkest, its knee guard as bright as drawn;
  * the leap: League's run bounds (its hips rise 40-50 squares between contacts); the body rises RISE of it (league_
    zeri's accepted run rises 17 dense rows), a foot League has on the ground stands on the ground row.

    python tools/art/nilah_stride.py --review DIR     # the design | its legs drawn on its own bones | the 8 frames
"""
import argparse
import functools
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

OUTLINE = (10, 1, 20)
C = {"R": (186, 44, 43), "r": (147, 32, 37), "m": (107, 29, 54),
     "P": (94, 42, 108), "p": (67, 26, 80), "q": (37, 27, 62),
     "T": (101, 215, 233), "t": (64, 144, 179), "u": (47, 103, 139), "w": (84, 184, 213),
     "S": (214, 120, 63), "s": (165, 83, 43), "k": (130, 66, 41), "n": (66, 52, 69), "O": OUTLINE}
SHADE = {"R": "r", "r": "m", "m": "m", "P": "p", "p": "q", "q": "q", "T": "t", "t": "u", "u": "u", "w": "t",
         "S": "s", "s": "k", "k": "k", "n": "q", "O": "O"}      # one step darker on the design's own ramps
FAR = SHADE                         # the far leg one step darker (not its knee guard)
LT, LS = 15.6, 24.0                 # hip -> knee, knee -> ankle (the ankle: the top of the slipper)
HIPS = {"near": (34.0, 60.5), "far": (33.3, 60.5)}
DESIGN = {"near": ((34.0, 60.5), (36.55, 76.3), (40.5, 100.0)),       # the design's own bones (hip, knee, ankle)
          "far": ((26.0, 61.5), (22.0, 76.6), (15.0, 100.0))}
ANKLE_Y = 100.0                     # a planted ankle's y: the slipper's top row is the design's row 100, soles 104
SOLE_ROW = 104                      # the design's lowest coloured row (105 is the soles' outline)
CLEAR = {"near": 9, "far": 11}      # a swinging foot over a standing one keeps its soles this many rows above its top,
TUCK = {"near": 0.0, "far": 1.1}    # lifted up and back (columns a row). The near leg, in front, straight up; the far
                                    # one, behind the standing leg, kicked up and back so its shin shows (straight up it
                                    # shoved its knee out in front of the skirt, a teal ball; a small lift left a foot
                                    # sticking out of the calf with no leg to it)
RISE = 0.3                          # of League's leap the body rises
PLANT_TOE = 7.5                     # a League toe this low (squares under its pivot) stands on the ground
NEAR_TOP = 4.5                      # the near thigh red all across down to here (the seat's red), then only the sash
TRAIL, TOE_OFF, TOE_TURN = -30, 25, (95, 140)   # a trailing foot: shin back past TRAIL deg, toe TOE_OFF off its line
LEAD_THIGH, LEAD_TIP = 20, 35       # a thigh this far forward leads: its foot tipped toe-down forward this far -
LEAD_SHIN = -50                     # while its shin is back less than this (a heel kick's foot turns back along it)
SAG = (30, 60)                      # degrees of a shin kicked back over which a balloon's bulk goes to its lower side
ANKLE_R = 8                         # the ponytail test looks at the slipper and the leg this close to the ankle
SUB = 4
# (u, back, front): half-widths behind and in front of the bone (fill, no outline), read off the design row by row
PROFILE = {
    "near": {"thigh": [(-2.0, 3.6, 4.6), (0.0, 3.6, 4.6), (8.0, 4.2, 5.4), (15.6, 4.4, 7.0)],
             "lower": [(-3.9, 4.8, 7.0), (-1.8, 4.2, 8.6), (0.2, 3.6, 9.3), (2.2, 3.9, 9.9), (4.3, 5.2, 9.6),
                       (6.3, 6.5, 9.3), (8.3, 7.8, 9.0), (10.3, 9.1, 8.6), (12.4, 8.5, 8.3), (13.4, 7.6, 4.2),
                       (14.4, 7.6, 4.0), (15.4, 7.0, 2.9), (16.4, 6.2, 2.4), (17.4, 5.0, 0.9), (18.5, 3.2, 0.0),
                       (19.5, 1.7, 1.2), (20.5, 1.7, 1.4), (24.0, 1.6, 1.6)]},
    "far": {"thigh": [(-2.0, 3.6, 4.6), (0.0, 3.6, 4.6), (15.6, 4.2, 5.0)],
            "lower": [(-4.3, 3.9, 6.6), (-1.1, 3.4, 6.4), (0.9, 4.6, 5.4), (3.0, 5.0, 5.6), (5.1, 5.4, 5.2),
                      (7.2, 6.6, 5.6), (9.3, 6.3, 5.3), (11.3, 4.8, 3.9), (13.4, 2.4, 2.5), (15.5, 1.9, 2.0),
                      (17.6, 1.8, 1.4), (24.0, 1.8, 1.4)]},
}
SLIPPERS = {"near": (100, 106, 35, 53, 40.5), "far": (100, 106, 9, 27, 15.5)}   # rows, columns, the ankle's column
# the slipper's own shape (near design slipper, ankle at (0, 0), x toward the toe, y toward the sole; square edges)
SLIP_POLY = [(-2.5, 0.0), (3.5, 0.0), (4.6, 1.3), (5.8, 2.6), (9.6, 3.4), (11.6, 4.3), (11.6, 5.0), (-4.5, 5.0),
             (-4.5, 4.2), (-3.6, 2.0), (-2.5, 0.0)]


@functools.lru_cache(maxsize=None)
def table_fns(key):
    which, seg = key
    table = PROFILE[which][seg]
    us = np.array([r[0] for r in table])
    return (us[0], us[-1], PchipInterpolator(us, [r[1] for r in table], extrapolate=False),
            PchipInterpolator(us, [r[2] for r in table], extrapolate=False))


def widths(key, u, sag):
    """Half-widths (back, front) at u; sag 0..1 moves the bulk to the front side (the lower one on a kicked-back shin)."""
    u0, u1, fb, ff = table_fns(key)
    uc = np.clip(u, u0, u1)
    b, f = fb(uc), ff(uc)
    if sag > 0:
        b, f = (1 - sag) * b + sag * 0.9 * np.minimum(b, f), (1 - sag) * f + sag * np.maximum(b, f)
    return b, f


def frame_of(p0, p1):
    a = np.array(p1, float) - np.array(p0, float)
    L = float(np.hypot(*a))
    a /= max(L, 1e-9)
    return a, np.array((a[1], -a[0])), L                  # along, across (front = +x for a bone pointing down)


def local(px, py, p0, a, n):
    dx, dy = px - p0[0], py - p0[1]
    return dx * a[0] + dy * a[1], dx * n[0] + dy * n[1]


def inside(key, L, u, v, sag=0.0):
    """Points (u, v) inside a bone drawn from its table's first u to L (its own length), both ends round."""
    u0, u1, _, _ = table_fns(key)
    back, front = widths(key, np.clip(u, u0, min(L, u1)), sag)
    body = (u >= u0) & (u <= L) & (v >= -back) & (v <= front)
    for ue in (u0, L):                                    # round ends: a disc on each end's own width
        b, f = (float(x) for x in widths(key, np.array(min(ue, u1)), sag))
        r = (b + f) / 2.0
        body |= (u - ue) ** 2 + (v - (f - b) / 2.0) ** 2 <= r * r
    return body


def coverage(shape, fn):
    """Squares at least half covered by fn(px, py) (SUB x SUB samples a square)."""
    H, W = shape
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    acc = np.zeros(shape, float)
    for i in range(SUB):
        for j in range(SUB):
            acc += fn(xs + (j + 0.5) / SUB, ys + (i + 0.5) / SUB)
    return acc >= SUB * SUB / 2.0


def tidy(m):
    """Spurs (a square with one 4-neighbour or none) out, notches (a gap with three or four) in, until it settles."""
    m = m.copy()
    k = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    for _ in range(8):
        nb = ndimage.convolve(m.astype(int), k, mode="constant")
        new = (m & (nb >= 2)) | (~m & (nb >= 3))
        if (new == m).all():
            break
        m = new
    return m


CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def ring4(m):
    """The squares outside m sharing a side with it."""
    return ndimage.binary_dilation(m, CROSS) & ~m


def edge4(region, other):
    """The squares of `region` sharing a side with a square of `other` (outside region)."""
    return region & ndimage.binary_dilation(other & ~region, CROSS)


def slip_label(x, y):
    """The slipper's colour at foot point (x, y): the instep's skin, the sole, the side (the design's own bands)."""
    lab = np.full(np.shape(x), "n", dtype=object)
    skin = ((y < 3.0) & (x > -3.5 + 2.0 * y) & (x < 5.6)) | ((y >= 3.0) & (y < 4.0) & (x > 4.5) & (x < 6.6))
    sole = ((y >= 4.0) & (x < 4.5)) | ((y >= 3.0) & (y < 4.0) & (x > -0.5) & (x < 1.5))
    lab[skin] = "S"
    lab[sole] = "q"
    return lab


def contains(poly, x, y):
    ins = np.zeros(np.shape(x), bool)
    for i in range(len(poly) - 1):
        (x1, y1), (x2, y2) = poly[i], poly[i + 1]
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / ((y2 - y1) + 1e-12) + x1)
        ins ^= c
    return ins


@functools.lru_cache(maxsize=None)
def turned_slipper(deg):
    """The near slipper drawn turned `deg` degrees clockwise about its ankle (its toe toward deg: 0 forward, 90 down,
    120 down and back) from its own outline and colour bands: RGBA and the ankle point."""
    th = math.radians(deg)
    H = W = 32
    ox, oy = 16.0, 16.0
    cs, sn = math.cos(th), math.sin(th)

    def to_foot(X, Y):
        x, y = X - ox, Y - oy
        return x * cs + y * sn, -x * sn + y * cs

    m = tidy(coverage((H, W), lambda X, Y: contains(SLIP_POLY, *to_foot(X, Y))))
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    lab = slip_label(*to_foot(xs + 0.5, ys + 0.5))
    g = np.zeros((H, W, 4), np.uint8)
    for k in ("n", "S", "q"):
        g[m & (lab == k)] = (*C[k], 255)
    g[ring4(m)] = (*OUTLINE, 255)
    yy, xx = np.nonzero(g[..., 3] > 0)
    y0, x0 = yy.min(), xx.min()
    return g[y0:yy.max() + 1, x0:xx.max() + 1].copy(), (ox - x0, oy - y0)


def slipper(d, which, turn):
    """The slipper as a rigkit Part with its joint on the ankle point: the design's own (turn 0, flat) or drawn turned."""
    if turn:
        s, j = turned_slipper(int(turn))
        s = s.copy()
    else:
        r0, r1, c0, c1, ax = SLIPPERS[which]
        s, j = d[r0:r1, c0:c1].copy(), (ax - c0, 0.0)
    if which == "far":
        orig = s.copy()
        for k, f in FAR.items():
            if k in ("O", "n"):                 # the side kept: darkened it is the hair's shadow colour exactly
                continue
            msk = (orig[..., :3] == np.array(C[k])).all(-1) & (orig[..., 3] > 0)
            s[msk, :3] = C[f]
    return K.Part(s, j)


def foot_turn(leg):
    """The foot's turn: flat on the ground and under a near-vertical shin; under a shin kicked back, along it (toe back
    and down) when the thigh is back too, tipped toe-down forward LEAD_TIP degrees when the thigh leads (the knee up
    in front: two feet both pointing down side by side hung like talons)."""
    if leg["planted"]:
        return 0
    a = K.bone_angle(leg["knee"], leg["ank"])
    if a >= TRAIL:
        return 0
    if K.bone_angle(leg["hip"], leg["knee"]) > LEAD_THIGH and a > LEAD_SHIN:
        return LEAD_TIP
    return int(round(np.clip(90 - a - TOE_OFF, *TOE_TURN) / 5.0) * 5)


def paint(which, thigh, lower, u1, v1, u2, v2):
    """The leg's colour letters before shading, the squares drawn as lines (outline colour), the cords (red lines) and
    the squares that never darken (the far knee guard)."""
    lab = np.full(thigh.shape, "", dtype=object)
    lines = np.zeros(thigh.shape, bool)
    keep = np.zeros(thigh.shape, bool)
    cords = []
    if which == "near":
        lab[thigh] = "P"
        lab[thigh & (u1 < NEAR_TOP)] = "R"                                  # red across the top (the body's last rows
        lab[thigh & (v1 >= -1.0) & (v1 <= 2.6) & (u1 < 10.5)] = "R"          # are red there), then the sash down its middle
        lab[lower] = "P"
        c1 = 12.6 - 0.91 * v2 - 0.07 * v2 ** 2
        lab[lower & (u2 > c1)] = "p"                                         # under the first cord: the gather's dark
        mid_v = 1.9 + 0.17 * u2 + 0.7 * np.sin(u2 / 2.6)                     # the strap wanders down the front
        strap = lower & (u2 >= -2.0) & (u2 <= 11.5) & (np.abs(v2 - mid_v) <= 1.0)
        lab[strap] = "t"
        lab[strap & (v2 < mid_v - 0.2) & (u2 < 6.0)] = "T"
        lines |= edge4(lower & ~strap, strap)                                # the strap's own outline both sides
        lab[lower & (u2 >= 18.8)] = "T"                                      # the anklet
        lab[lower & (u2 >= 19.8)] = "S"
        band = lower & (u2 < 18.8) & (v2 >= -9.0) & (v2 <= 3.0) & ~strap
        red = lower & (u2 > c1 - 1.9) & (u2 <= c1 + 2.7) & band                # two cords, two squares thick, from one
        gap = edge4(lower & (u2 <= c1 + 0.7), lower) & red                   # band split by a clean line (no specks)
        cords.append(red & ~gap)
    else:
        lab[thigh] = "R"
        fold = thigh & (u1 > 1.5) & (u1 < 9.0)
        lab[edge4(fold & (v1 < 0.6), fold)] = "P"                            # the thigh's fold
        g = 2.6 + 0.35 * v2                                                  # the guard's lower edge (lower in front)
        guard = lower & (u2 < g)
        f1, f2 = g - 4.0, g - 2.0
        cap, wrap_, lip = guard & (u2 < f1), guard & (u2 >= f1) & (u2 < f2), guard & (u2 >= f2)
        lab[guard] = "t"                                                     # mostly the mid teal, as drawn
        lab[cap & (v2 > 0.5) & (v2 < 3.5)] = "T"                             # light on the cap's and the lip's front
        lab[wrap_ & (v2 < 2.0)] = "u"                                        # the dark wrap between them
        lab[lip & (v2 > 1.5)] = "T"
        lines |= edge4(wrap_, cap) & (v2 < 2.0)                              # the folds only part way round
        lines |= edge4(lip, wrap_) & (v2 < 3.0)
        lines |= edge4(guard, thigh)                                         # its own top edge over the thigh
        lines |= edge4(lower & ~guard, guard)                                # and its lower edge
        keep |= guard
        mid = lower & ~guard & (u2 < 12.5)
        back = mid & (v2 < 0.6)
        wrap = mid & (v2 >= 0.6)
        shin = lower & (u2 >= 12.5) & (u2 < 19.7)
        lab[back] = "P"
        lab[wrap] = "T"
        lab[wrap & (v2 > 2.4)] = "t"
        lab[shin] = "T"
        lab[shin & (v2 < -0.6)] = "k"
        lab[lower & (u2 >= 19.7)] = "S"
        lines |= edge4(wrap, back)
        lines |= edge4(back, shin)
        for c in (1.4, 3.2):
            cords.append(edge4(back & (u2 <= g + c), back) & (v2 < 0.0))
    return lab, lines, cords, keep


def draw_leg(shape, which, hip, knee, ank, foot, sag=0.0):
    """One leg on a canvas of `shape` (RGBA, its own outline in) and its fill; foot: a slipper Part on the ankle (a flat
    one over the leg, a turned one under it)."""
    ys, xs = np.mgrid[0:shape[0], 0:shape[1]].astype(float)
    pcx, pcy = xs + 0.5, ys + 0.5
    a1, n1, L1 = frame_of(hip, knee)
    a2, n2, L2 = frame_of(knee, ank)
    thigh = coverage(shape, lambda X, Y: inside((which, "thigh"), L1, *local(X, Y, hip, a1, n1)))
    lower = coverage(shape, lambda X, Y: inside((which, "lower"), L2, *local(X, Y, knee, a2, n2), sag))
    leg = tidy(thigh | lower)
    lower &= leg
    thigh &= leg & ~lower
    u1, v1 = local(pcx, pcy, hip, a1, n1)
    u2, v2 = local(pcx, pcy, knee, a2, n2)
    lab, lines, cords, keep = paint(which, thigh, lower, u1, v1, u2, v2)
    side = np.where(lower, v2, v1)
    foot_rgba = np.zeros((*shape, 4), np.uint8)
    flat = True
    if foot is not None:
        K.place(foot_rgba, foot, ank)
        flat = foot.s.shape[1] > foot.s.shape[0] + 4
    fop = foot_rgba[..., 3] > 0
    fink = fop & (foot_rgba[..., :3] == np.array(OUTLINE)).all(-1)
    fill_foot = fop & ~fink
    union = leg | fill_foot
    d4 = ndimage.distance_transform_cdt(np.pad(union, 1), metric="taxicab")[1:-1, 1:-1]
    back = leg & (side < 0)
    front = leg & (side >= 0)
    out = lab.copy()
    if which == "near":
        shade = (back & (d4 <= 2)) | (front & (d4 <= 1))
        for key in ("R", "P", "T", "t"):
            out[(lab == key) & shade] = SHADE[key]
        out[(lab == "S") & back & (d4 <= 1)] = "s"                           # the bare ankle stays bright
        out[(lab == "R") & back & (d4 <= 1)] = "m"
        out[(lab == "T") & (u2 >= 18.8) & (u2 < 19.8) & lower] = "T"         # the anklet bright
    else:
        rim = d4 <= 1                                                        # the far leg: its rim the darkest
        for key in ("R", "P", "T", "t", "S", "k"):
            out[(lab == key) & rim & ~keep] = SHADE[key]
        out[(lab == "T") & keep & back & rim] = "t"
    for line in cords:
        out[line & leg] = "R"
        if which == "near":
            out[line & leg & back & (d4 <= 2)] = "r"
    g = np.zeros((*shape, 4), np.uint8)
    for key, col in C.items():
        m = (out == key) & leg
        g[m] = (*col, 255)
        if which == "far":
            g[m & ~keep] = (*C[FAR[key]], 255)
    g[lines & leg] = (*OUTLINE, 255)
    if flat:
        g[fill_foot] = foot_rgba[fill_foot]
    else:
        g[fill_foot & ~leg] = foot_rgba[fill_foot & ~leg]
    g[ring4(union)] = (*OUTLINE, 255)
    g[fink & ~union] = (*OUTLINE, 255)
    return g, union


def ik(hip, ank, lt, ls):
    """The knee for an ankle at `ank` (pulled into reach), bent forward (the knee in front of hip -> ankle)."""
    best = None
    for bend in (1, -1):
        kn, an = K.elbow(hip, ank, lt, ls, bend=bend)
        z = (an[0] - hip[0]) * (kn[1] - hip[1]) - (an[1] - hip[1]) * (kn[0] - hip[0])
        if best is None or z < 0:
            best = (kn, an)
        if z < 0:
            break
    return best


def pose(J, k, origin=(0, 0)):
    """Frame k: the body's rows (negative = up) and per leg its hip, knee, ankle, whether it stands."""
    hy = [(fr["joints"]["L_Hip"][1] + fr["joints"]["R_Hip"][1]) / 2 for fr in J]
    low = max(hy)
    j = J[k]["joints"]
    want = {}
    for which, side in (("near", "R"), ("far", "L")):
        H, Kn, Fo, To = (j[f"{side}_{n}"][:2] for n in ("Hip", "KneeLower", "Foot", "Toe"))
        want[which] = (K.bone_angle(H, Kn), K.bone_angle(Kn, Fo), To[1] >= PLANT_TOE)
    ground = ANKLE_Y + origin[1]
    bob = int(round(RISE * (hy[k] - low)))
    for _ in range(40):                                     # a planted foot out of reach brings the body down
        legs, ok = {}, True
        for which, (th, sh, planted) in want.items():
            hip = (HIPS[which][0] + origin[0], HIPS[which][1] + origin[1] + bob)
            ax = hip[0] + LT * math.sin(math.radians(th)) + LS * math.sin(math.radians(sh))
            ay = hip[1] + LT * math.cos(math.radians(th)) + LS * math.cos(math.radians(sh))
            stands = planted or ay > ground
            if stands:
                ay = ground
                if math.hypot(ax - hip[0], ay - hip[1]) > LT + LS - 0.3:
                    ok = False
            knee, ank = ik(hip, (ax, ay), LT, LS)
            legs[which] = dict(hip=hip, knee=knee, ank=ank, planted=stands)
        if ok:
            break
        bob += 1
    for leg in legs.values():
        leg["turn"] = foot_turn(leg)
    return bob, legs


def lowest_row(d, which, leg):
    part = slipper(d, which, leg["turn"])
    top = math.floor(leg["ank"][1] - part.j[1] + 1e-9)
    return top + int(np.nonzero(part.s[..., 3].any(1))[0].max()), part


def lifted(leg, rows, back=0.0):
    ank = (leg["ank"][0] - back * rows, leg["ank"][1] - rows)
    knee, ank = ik(leg["hip"], ank, LT, LS)
    leg = dict(leg, knee=knee, ank=ank)
    leg["turn"] = foot_turn(leg)
    return leg


def keep_off_ground(d, which, leg, ground_row):
    """A foot in the air whose toe would reach under the soles' row: the ankle lifted so it touches it."""
    if leg["planted"]:
        return leg
    for _ in range(3):
        lowest, _ = lowest_row(d, which, leg)
        if lowest <= ground_row + 1:
            break
        leg = lifted(leg, lowest - ground_row - 1)
    return leg


def clear_of(d, which, leg, other, ground_row):
    """A swinging foot over the standing foot (the two slippers' columns overlapping): lifted so its lowest square is
    CLEAR rows above the standing slipper's top - two slippers stacked read as one leg with two feet."""
    if leg["planted"] or not other["planted"]:
        return leg
    for _ in range(3):
        lowest, part = lowest_row(d, which, leg)
        mine = math.floor(leg["ank"][0] - part.j[0] + 1e-9), part.s.shape[1]
        op = slipper(d, "near" if which == "far" else "far", 0)
        theirs = math.floor(other["ank"][0] - op.j[0] + 1e-9), op.s.shape[1]
        if mine[0] + mine[1] <= theirs[0] or theirs[0] + theirs[1] <= mine[0]:
            break
        want = math.floor(other["ank"][1]) - CLEAR[which]
        if lowest <= want:
            break
        leg = lifted(leg, lowest - want, TUCK[which])
    return leg


def sag_of(leg):
    """How far a balloon hangs to its lower side (0..1) under this shin."""
    a = -K.bone_angle(leg["knee"], leg["ank"])
    return float(np.clip((a - SAG[0]) / (SAG[1] - SAG[0]), 0, 1))


def foot_mask(d, which, leg, shape):
    m = np.zeros((*shape, 4), np.uint8)
    K.place(m, slipper(d, which, leg["turn"]), leg["ank"])
    return m[..., 3] > 0


def away_from(d, which, leg, avoid, shape, ground_row):
    """A foot in the air whose drawing (the slipper, and the leg within ANKLE_R squares of the ankle, outline in) comes
    within a square of `avoid` (the ponytail's squares): moved a few squares so one square of ground parts them - the
    slipper's dark ran into the hair's dark as one mass. The rest of the leg is not tested (its thigh touches the hair at
    the hip in most frames: moving the foot for that bent the leaps out of League's pose)."""
    if leg["planted"] or avoid is None:
        return leg
    zone = ndimage.binary_dilation(avoid, np.ones((3, 3), bool))
    ys, xs = np.mgrid[0:shape[0], 0:shape[1]]

    def touches(lg):
        g, _ = draw_leg(shape, which, lg["hip"], lg["knee"], lg["ank"], slipper(d, which, lg["turn"]), sag_of(lg))
        near_ankle = (xs + 0.5 - lg["ank"][0]) ** 2 + (ys + 0.5 - lg["ank"][1]) ** 2 <= ANKLE_R ** 2
        return bool(((g[..., 3] > 0) & (near_ankle | foot_mask(d, which, lg, shape)) & zone).any())

    if not touches(leg):
        return leg
    moves = sorted(((dx, dy) for dx in range(-6, 7, 2) for dy in range(-6, 7) if (dx, dy) != (0, 0)),
                   key=lambda m: (abs(m[0]) + abs(m[1]), abs(m[0])))
    for dx, dy in moves:
        cand = dict(leg)
        knee, ank = ik(leg["hip"], (leg["ank"][0] + dx, leg["ank"][1] + dy), LT, LS)
        cand.update(knee=knee, ank=ank)
        cand["turn"] = foot_turn(cand)
        if lowest_row(d, which, cand)[0] > ground_row + 1:
            continue
        if not touches(cand):
            return cand
    return leg


def stride(J, k, d, shape, origin=(0, 0), avoid=None):
    """Frame k's two legs (RGBA layers: far, near), the body's rows and the geometry. avoid(bob): squares a foot in the
    air keeps a square away from (the ponytail)."""
    bob, legs = pose(J, k, origin)
    keep_clear = avoid(bob) if avoid is not None else None
    layers = {}
    for which in ("far", "near"):
        other = legs["near" if which == "far" else "far"]
        leg = keep_off_ground(d, which, legs[which], SOLE_ROW + origin[1])
        leg = clear_of(d, which, leg, other, SOLE_ROW + origin[1])
        leg = away_from(d, which, leg, keep_clear, shape, SOLE_ROW + origin[1])
        legs[which] = leg
        g, _ = draw_leg(shape, which, leg["hip"], leg["knee"], leg["ank"], slipper(d, which, leg["turn"]), sag_of(leg))
        layers[which] = g
    return layers["far"], layers["near"], bob, legs


def design_legs(d, shape, origin=(0, 0)):
    """Both legs drawn on the design's own bones (the check that the drawing is the design's leg)."""
    can = np.zeros((*shape, 4), np.uint8)
    for which in ("far", "near"):
        h, kn, a = [(p[0] + origin[0], p[1] + origin[1]) for p in DESIGN[which]]
        g, _ = draw_leg(shape, which, h, kn, a, slipper(d, which, 0))
        m = g[..., 3] > 0
        can[m] = g[m]
    return can


def main():
    import import_nilah_strips as I
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True)
    ap.add_argument("--joints", default=os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "source", "nilah",
                                                     "run", "run_joints.json"))
    ap.add_argument("--z", type=int, default=5)
    a = ap.parse_args()
    J = json.load(open(a.joints, encoding="utf-8"))
    d = I.design()
    shape = (112, 72)
    origin = (8, 0)
    top, bot = 40, 108
    dl = np.zeros((*shape, 4), np.uint8)
    yy, xx = np.nonzero(d[..., 3] > 0)
    dl[yy + origin[1], xx + origin[0]] = d[yy, xx]
    dl[:58] = 0
    tiles = [("design", dl), ("drawn on its bones", design_legs(d, shape, origin))]
    for k in range(8):
        far, near, bob, legs = stride(J, k, d, shape, origin)
        can = np.zeros((*shape, 4), np.uint8)
        for g in (far, near):
            m = g[..., 3] > 0
            can[m] = g[m]
        tiles.append((f"frame {k + 1}", can))
        print(k + 1, "bob", bob, {w: (tuple(round(v, 1) for v in l["ank"]), l["planted"], l["turn"], round(sag_of(l), 2))
                                  for w, l in legs.items()})
    from PIL import ImageDraw
    z = a.z
    W, H = shape[1], bot - top
    cols = 5
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (W * z + 6), rows * (H * z + 14)), (40, 40, 40, 255))
    dr = ImageDraw.Draw(sheet)
    for i, (name, t) in enumerate(tiles):
        x0, y0 = (i % cols) * (W * z + 6), (i // cols) * (H * z + 14)
        bg = Image.new("RGBA", (W * z, H * z), (110, 120, 108, 255))
        bg.alpha_composite(Image.fromarray(np.ascontiguousarray(t[top:bot])).resize((W * z, H * z), Image.NEAREST))
        sheet.alpha_composite(bg, (x0, y0 + 14))
        dr.text((x0 + 2, y0 + 1), name, fill=(255, 255, 255, 255))
    os.makedirs(a.review, exist_ok=True)
    sheet.convert("RGB").save(os.path.join(a.review, "nilah_stride.png"))
    print("written")


if __name__ == "__main__":
    main()

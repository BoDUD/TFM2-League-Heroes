#!/usr/bin/env python3
"""Ryze's arms drawn as pixel art from three joints (2026-10-04): the idle's arm in any pose.

The arms Codex drew on the casting frames were thicker than the idle's, and turning the idle's own arm pixels
(RotSprite) left them straight and stiff - 「瑞兹的手臂感觉还是很奇怪真的」「像个僵尸一样」「不自然」. Here an arm is
drawn square by square from its joints (the shoulder S, the elbow E, the wrist W, the hand's middle H), as the idle's
arm is built (tools/art/rig_ryze.py parts, assets/source/ryze/design_v2):
- the bare upper arm from S to E, about three squares wide, lit on its outer side, dark on its inner side;
- the forearm from E to W, the brown leather bracer, a little wider, a gold band at each end;
- the hand round H: a fist (three by three) or an open palm (longer, the fingers a shade lighter);
each square coloured by where it lies across its bone (lit / middle / dark), then one outline round the whole arm.
The bones keep the idle's lengths whatever the joints say (only their directions are used), so an arm never grows.
"""
import math

import numpy as np

# the idle's lengths (squares): shoulder -> elbow, elbow -> wrist (the bracer), wrist -> the hand's middle
UPPER, FORE, HAND = 7.0, 4.5, 1.8
R_UPPER, R_FORE, R_FIST = 1.05, 1.45, 1.5
# the idle's colours by letter (rig_ryze.PAL): (lit, middle, dark) of each material
MAT = {
    "skin": ("f", "e", "d"),
    "bracer": ("h", "j", "u"),
    "band": ("y", "x", "h"),
    "hand": ("f", "e", "d"),
}


def _seg(p, a, b):
    """Distance of point p from segment a-b, the parameter along it (0..1) and the signed distance across it."""
    ax, ay = a
    vx, vy = b[0] - ax, b[1] - ay
    ln2 = vx * vx + vy * vy or 1e-9
    t = max(0.0, min(1.0, ((p[0] - ax) * vx + (p[1] - ay) * vy) / ln2))
    cx, cy = ax + vx * t, ay + vy * t
    dx, dy = p[0] - cx, p[1] - cy
    ln = math.sqrt(ln2)
    across = (dx * -vy + dy * vx) / ln            # + = to the left of a->b on screen (y down: counter-clockwise)
    return math.hypot(dx, dy), t, across


def joints(S, E, W, H):
    """The joints with the idle's bone lengths: the directions of S->E, E->W and W->H kept."""
    def step(a, b, n):
        vx, vy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(vx, vy) or 1.0
        return (a[0] + vx / ln * n, a[1] + vy / ln * n)
    E2 = step(S, E, UPPER)
    W2 = step(E2, (E2[0] + W[0] - E[0], E2[1] + W[1] - E[1]), FORE)
    H2 = step(W2, (W2[0] + H[0] - W[0], W2[1] + H[1] - W[1]), HAND)
    return S, E2, W2, H2


def lit_sign(a, b, side):
    """+1 if the lit side of bone a->b is its left (counter-clockwise) side on screen, else -1: the side away from
    the body (the far arm's left, the near arm's right), or the top when the bone runs more across than down."""
    vx, vy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(vx, vy) or 1.0
    nx, ny = vy / ln, -vx / ln                     # the left normal (y down)
    if abs(ny) >= 0.6:
        return 1 if ny < 0 else -1                 # light from above
    out = -1 if side == "far" else 1
    return 1 if nx * out > 0 else -1


def draw(S, E, W, H, side, shape="fist", rgba=None, ink=(0x0F, 0x02, 0x13, 255)):
    """{(x, y): rgba} of one arm (with its outline) from its joints; side "far" or "near"."""
    S, E, W, H = joints(S, E, W, H)
    xs = [p[0] for p in (S, E, W, H)]
    ys = [p[1] for p in (S, E, W, H)]
    cells = {}
    su, sf = lit_sign(S, E, side), lit_sign(E, W, side)
    sh = lit_sign(W, H, side)
    palm = shape in ("open_palm", "pointing")
    for y in range(int(math.floor(min(ys))) - 3, int(math.ceil(max(ys))) + 4):
        for x in range(int(math.floor(min(xs))) - 3, int(math.ceil(max(xs))) + 4):
            p = (x + 0.5, y + 0.5)
            best = None
            # the hand: a fist round H, or a palm from W past H
            if palm:
                tip = (H[0] + (H[0] - W[0]) * 0.8, H[1] + (H[1] - W[1]) * 0.8)
                d, t, ac = _seg(p, W, tip)
                if d <= 1.25:
                    best = ("hand", ac * sh / 1.25, t)
            else:
                d = math.hypot(p[0] - H[0] - 0.0, p[1] - H[1])
                if d <= R_FIST:
                    _, t, ac = _seg(p, W, H)
                    best = ("hand", ac * sh / R_FIST, 1.0)
            if best is None:
                d, t, ac = _seg(p, E, W)
                if d <= R_FORE:
                    along = t * FORE
                    part = "band" if along < 1.0 or along > FORE - 1.0 else "bracer"
                    best = (part, ac * sf / R_FORE, t)
            if best is None:
                d, t, ac = _seg(p, S, E)
                if d <= R_UPPER and t > 0.0:
                    best = ("skin", ac * su / R_UPPER, t)
            if best is None:
                continue
            part, c, _ = best
            lit, mid, dark = MAT[part]
            ch = lit if c > 0.34 else dark if c < -0.34 else mid
            cells[(x, y)] = rgba(ch) if rgba else ch
    if rgba is None:
        return cells
    ring = {}
    for (x, y) in cells:
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ox, y + oy)
            if q not in cells:
                ring[q] = np.array(ink, np.uint8)
    ring.update(cells)
    return ring


# ---- the idle's own arm squares, sheared and quarter-turned (no resampling) ------------------------------------
# Each bone of the idle's arm is a strip of rows hanging from its joint (the upper arm from the shoulder, the forearm
# with the bracer and the hand from the elbow). A bone pointing anywhere within 45 degrees of straight down keeps its
# rows and shifts each by its slope (one square per row at 45 degrees: a clean pixel diagonal, the same width all
# along); one pointing sideways is the strip quarter-turned (its lit outer side to the top) and shifted column by
# column; one pointing up is the strip upside down. Every square keeps the idle's colour, so the arm stays the idle's
# arm - only bent and swung.

def strip(cells, jx):
    """The bone's squares as (along, across) from its joint (its top row, column jx): along down the strip, across
    + to the right."""
    jy = min(y for _, y in cells)
    return {(y - jy, x - jx): c for (x, y), c in cells.items()}


def place(bone, theta, side, drop=()):
    """The bone's squares on screen relative to its joint, pointing theta degrees from straight down (+ toward the
    right of the screen, 180 = up); drop: rows (along) taken out (a bone foreshortened toward the camera)."""
    rows = sorted({a for a, _ in bone})
    keep = [a for a in rows if a not in drop]
    remap = {a: i for i, a in enumerate(keep)}
    t = math.radians(theta)
    sx, cy = math.sin(t), math.cos(t)
    out = {}
    far = side == "far"
    slope = min(abs(sx), abs(cy)) / max(abs(sx), abs(cy))
    if slope > WIDEN:
        # a bone near 45 degrees: rows shifted a square each are thinner across the bone than the idle's - each row
        # gets one more square in its middle (the middle colour), its outer half moved out by one
        wide = {}
        for a in rows:
            row = {c: col for (a_, c), col in bone.items() if a_ == a}
            inner = sorted(c for c, col in row.items() if tuple(int(v) for v in col[:3]) not in OUTLINE)
            if len(inner) < 2:
                wide.update({(a, c): col for c, col in row.items()})
                continue
            mid = inner[len(inner) // 2]
            for c, col in row.items():
                wide[(a, c + 1 if c > mid else c)] = col
            wide[(a, mid + 1)] = row[mid]
        bone = wide
    for (a, c), col in bone.items():
        if a not in remap:
            continue
        a2 = remap[a]
        if abs(theta) <= 45:                       # down: rows shifted
            X, Y = c + int(math.floor(a2 * sx / cy + 0.5)), a2
        elif abs(theta) >= 135:                    # up: upside down, rows shifted
            X, Y = c + int(math.floor(a2 * sx / -cy + 0.5)), -a2
        elif theta > 0:                            # right: the lit outer side to the top
            Y0 = c if far else -c
            X, Y = a2, Y0 + int(math.floor(a2 * cy / sx + 0.5))
        else:                                      # left: the lit outer side to the top as well
            Y0 = c if far else -c
            X, Y = -a2, Y0 + int(math.floor(a2 * cy / -sx + 0.5))
        out[(X, Y)] = col
    end_a = len(keep) - 1
    if abs(theta) <= 45:
        end = (int(math.floor(end_a * sx / cy + 0.5)), end_a)
    elif abs(theta) >= 135:
        end = (int(math.floor(end_a * sx / -cy + 0.5)), -end_a)
    elif theta > 0:
        end = (end_a, int(math.floor(end_a * cy / sx + 0.5)))
    else:
        end = (-end_a, int(math.floor(end_a * cy / -sx + 0.5)))
    return out, end


WIDEN = 0.45                                       # bones steeper than this slope off an axis get a square wider
OUTLINE = {(0x0F, 0x02, 0x13), (0x10, 0x04, 0x1C)}


def close_gaps(cells, outline=OUTLINE):
    """Empty squares between two arm squares (left and right, or above and below) - the elbow's corner, a row's step -
    filled with the colour of the arm square beside them; twice."""
    for _ in range(2):
        add = {}
        for (x, y), c in cells.items():
            for ox, oy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                q = (x + ox, y + oy)
                if q in cells or q in add:
                    continue
                opp = (q[0] + ox, q[1] + oy)
                if opp in cells and tuple(int(v) for v in cells[opp][:3]) not in outline                         and tuple(int(v) for v in c[:3]) not in outline:
                    add[q] = c
        cells.update(add)
    return cells


# a bone reaching sideways points into the picture as much as across it (the 3/4 view): rows taken out of its middle,
# up to these many at a right angle to the body (a straight arm thrown forward read as a stick, a zombie's arm:
# 「像个僵尸一样」); {bone: (rows that may go, in the order they go)}
FORESHORTEN_UP = [3, 5, 2]                      # the upper arm's rows (from the shoulder) that go first
FORESHORTEN_FORE = [2]                          # the bracer's middle row


def foreshorten(bone, theta, order):
    s = abs(math.sin(math.radians(theta)))
    n = int(math.floor(len(order) * max(0.0, s - 0.35) / 0.65 + 0.5))
    return tuple(order[:n])


def step_of(theta):
    t = math.radians(theta)
    sx, cy = math.sin(t), math.cos(t)
    if abs(sx) <= abs(cy):
        return (int(math.floor(sx / abs(cy) + 0.5)), 1 if cy > 0 else -1)
    return (1 if sx > 0 else -1, int(math.floor(cy / abs(sx) + 0.5)))


# the joints' columns on the idle (the upper arm's axis under the shoulder, the forearm's under the elbow) and the
# shoulder squares (the upper arm's top row, on its axis)
AXIS = {"far": (-7, -8), "near": (6, 6)}
SHOULDER = {"far": (-7, -14), "near": (6, -13)}


def pose(arms, side, up_deg, fore_deg, shoulder=None, drop_up=(), drop_fore=()):
    """{(x, y): colour} of the idle's arm (arms: rig_ryze.parts()["arms"]; side "far"/"near") with its shoulder on
    `shoulder` (default the idle's), the upper arm up_deg and the forearm fore_deg from straight down (+ toward the
    right of the screen, 180 = up)."""
    key = "back" if side == "far" else "front"
    up = strip(arms[(key, "upper")], AXIS[side][0])
    fo = strip(arms[(key, "fore")], AXIS[side][0])   # (across from the upper arm's axis: the bracer sits a square in)
    if not drop_up:
        drop_up = foreshorten(up, up_deg, FORESHORTEN_UP)
    if not drop_fore:
        drop_fore = foreshorten(fo, fore_deg, FORESHORTEN_FORE)
    cu, end = place(up, up_deg, side, drop_up)
    sx, sy = shoulder or SHOULDER[side]
    out = {(sx + x, sy + y): c for (x, y), c in cu.items()}
    st = step_of(fore_deg)
    ex, ey = sx + end[0] + st[0], sy + end[1] + st[1]
    cf, _ = place(fo, fore_deg, side, drop_fore)
    for (x, y), c in cf.items():
        out[(ex + x, ey + y)] = c
    return close_gaps(out)

#!/usr/bin/env python3
"""Twisted Fate's action strips posed from the approved design's own parts (2026-10-04): the casting body = the idle's.

    python tools/art/rig_twistedfate.py [--check] [--review DIR]

Codex's step-2 delivery (assets/source/twistedfate/codex_strips/, its build_tf_strips.py) pasted the design's head,
torso box and lower legs and drew everything that moves as 3-px lines: a plank of an arm across the chest in the
attack and Q, a tube arm with a block of a hand in W, the hit, the ult and the Gate, stick legs in the walk, the Q's
crouch, the Gate and the fall. The user: 「奇怪的地方你帮我修复 不再让codex返工了 codex太笨了」. Here every frame is
the design (tools/art/design_twistedfate.py) with only what the action moves moved:
- FAR_ARM: the image-right arm is taken off the design and posed from its own squares, as Ryze's arms were
  (tools/art/ryze_arms.py: the idle's arm sheared and quarter-turned, no resampling): two bones - UPPER, the thin navy
  sleeve, hanging from the shoulder under the gold epaulette, and FORE, the flared gold cuff, the white cuff and the
  small hand, hanging from the elbow - each a strip of the design's rows; a bone within 45 degrees of straight down
  keeps its rows and shifts each by its slope, one pointing across is quarter-turned (its outer side up), one near 45
  degrees gets a square wider, a sleeve pointing across loses a row (it points into the picture as much as across);
  every square keeps the design's colour, and the arm lies BEHIND the body, as the far arm does. (A 4-wide straight
  redraw read as a thick stick with a pointed hand - 「走路时右手这里有点奇怪」, 「放技能的时候右手臂应该也不对 要改全都改了」 -
  and the design's whole arm turned by RotSprite bent out of shape - 「怎么后面释放技能手臂变形了啊」.) Where an action
  leaves the arm at rest (the wind-ups, the Gate, the hit) it stays as drawn.
  The attack and Q lean back a column, then fling the arm forward at the release (tick 12, the start of frame 4);
  League's TF throws with that hand. The fan of cards stays in the other hand at the hip in every frame (the thrown
  card is an effect).
- the walk (League's walk at his base speed: one cycle in 868 ms, 8 frames): NEAR_LEG and FAR_LEG, the design's own
  trouser, knee-band and boot pixels, each sheared about its hip (row HIP) so its ankle moves; the ankles swing about
  their places in a 3/4 view (the far one a few columns right of the near one), the lead foot changes each half
  cycle, the swinging foot lifted 1-2 rows below the knee; layers: the far leg, the body, the near leg; where a leg
  leaves the coat's opening the coat's red lining shows (LINING); the upper body a row lower at each contact; the far
  arm - the design's own thin arm, a few degrees either way - swinging against the far leg.
- Q hops a row in frames 2-3; the Gate and the landing bow the head (DIP: the head and hat rows a row or two lower,
  over the collar); the hit leans everything above the boots a column back.
- the death: the whole design turned back about the near heel (RotSprite), then on its back (a quarter turn), the
  lowest square always on the soles row.
Every built frame is finished alike (finish): pinholes take the colour round them, the outline closes round the moved
edges (strips.complete_outline), loose crumbs go.
Writes assets/source/native/twistedfate_<tag>.png (8x, 128x96 cells, layout like native_refs) and twistedfate_cells.json;
then tools/art/import_native.py --hero twistedfate. --check compares instead of writing; --review writes review sheets.
"""
import argparse
import json
import math
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips  # noqa: E402
import rig_nocturne as RN  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "twistedfate_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point on its 128 canvas (the near sole on row 99)
SOLES = 99
OUT = (0x0D, 0x0B, 0x12)
CELL = (128, 96)
CELL_PIVOT = (64, 70)            # where the canvas pivot goes in each cell
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "ult_gate", "ult_land", "hit", "dead"]
# frame times (ms): League's clips sampled by tools/lol poses (assets/source/twistedfate/poses.json); the walk is one
# cycle of League's walk (868 ms) in 8 frames (sampled every 217 ms it was two cycles of 4 poses)
MS = {"idle": [200] * 6, "run": [108, 109, 108, 109, 108, 109, 108, 109], "attack": [60, 70, 70, 70, 80, 83],
      "skill": [60, 70, 70, 70, 70, 60], "skill2": [80, 87], "ult": [100, 130, 130, 140], "ult_gate": [250] * 6,
      "ult_land": [110, 110, 113], "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}

# the far arm on the design canvas (row: columns), with the outline squares it owns; the gold epaulette over it
# (rows 78-81) stays on the body
FAR_ARM = {82: [66, 67, 68], 83: [66, 67, 68], 84: [67, 68, 69], 85: [67, 68, 69, 70], 86: [66, 67, 68, 69, 70],
           87: [67, 68, 69, 70, 71], 88: [68, 69, 70, 71], 89: [68, 69, 70, 71], 90: [70, 71], 91: [70]}
SHOULDER = (67, 82)              # the sleeve's top square under the epaulette: the upper bone's joint
# the arm's bones as strips, (along, across) -> letter: along down the bone from its joint, across + to the outer
# (image-right) side of the column the sleeve starts in; the design's own squares (rows 82-85 and 86-91), with the
# outline squares that ring them (the inner ones the coat's edge shares)
UPPER = {(0, -1): "o", (0, 0): "4", (0, 1): "o",
         (1, -1): "o", (1, 0): "4", (1, 1): "4",
         (2, 0): "o", (2, 1): "4", (2, 2): "o",
         (3, 0): "o", (3, 1): "1", (3, 2): "h", (3, 3): "o"}
FORE = {(0, -1): "o", (0, 0): "h", (0, 1): "f", (0, 2): "8", (0, 3): "o",
        (1, -1): "o", (1, 0): "h", (1, 1): "5", (1, 2): "8", (1, 3): "h", (1, 4): "o",
        (2, 2): "o", (2, 3): "l", (2, 4): "o",
        (3, 2): "o", (3, 3): "g", (3, 4): "o",
        (4, 2): "o", (4, 3): "d", (4, 4): "o",
        (5, 3): "o"}
ARM_RGB = {"o": OUT, "1": (0x17, 0x19, 0x25), "4": (0x26, 0x2A, 0x3A), "5": (0x6B, 0x3B, 0x26),
           "8": (0x7A, 0x4A, 0x0E), "d": (0xA8, 0x64, 0x3E), "f": (0xC0, 0x8A, 0x1C), "g": (0xD5, 0x8C, 0x5C),
           "h": (0xF2, 0xC2, 0x3A), "l": (0xF2, 0xF2, 0xF6)}
WIDEN = 0.45                     # bones steeper than this slope off an axis get a square wider (ryze_arms)
FORESHORTEN_UP = [1]             # the sleeve's row that goes first when it points across (its two-square row)

# the legs (row: columns): the near one from the coat's opening (row 89) to its sole, the far one from its gold knee
# band (row 93; above it the coat's front flap hides it) to its sole
NEAR_LEG = {89: [59, 60, 61, 62], 90: [58, 59, 60, 61, 62], 91: [58, 59, 60, 61], 92: [57, 58, 59, 60],
            93: [57, 58, 59, 60], 94: [57, 58, 59, 60], 95: [56, 57, 58, 59], 96: [56, 57, 58, 59],
            97: [56, 57, 58, 59, 60], 98: [56, 57, 58, 59, 60], 99: [56, 57, 58, 59, 60]}
FAR_LEG = {93: [65, 66, 67, 68, 69], 94: [65, 66, 67, 68], 95: [66, 67, 68, 69], 96: [65, 66, 67, 68, 69, 70],
           97: [65, 66, 67, 68, 69, 70, 71], 98: [65, 66, 68, 69, 70]}
HIP = 88                         # the legs turn about this row (a straight leg: each row moved in proportion)
ANKLE = 96                       # from this row down a leg moves whole (the boot)
NEAR_ANKLE, FAR_ANKLE = 58.0, 66.5      # the ankles' middles in the stance
# the walk, per frame: the ankles' middles - the near one's swing s about NEAR_AT, the far one's -s about FAR_AT (the
# stance's tracks drawn 2.5 columns together, or the feet would be 16 apart when the far one leads: the 3/4 view
# adds its depth to that stride and takes it from the other), the lifted boot (rows), the upper body's drop (rows: a
# row lower at each contact) and the far arm (upper, fore: degrees from the design's own hang, + forward; forward
# when the far leg is back, the forearm trailing a little)
NEAR_AT, FAR_AT = 61.5, 63.5
SWING = [4.5, 2.5, 0.0, -2.5, -4.5, -2.5, 0.0, 2.5]
NEAR_LIFT = [0, 0, 0, 0, 0, 1, 2, 1]
FAR_LIFT = [0, 1, 2, 1, 0, 0, 0, 0]
DROP = [1, 1, 0, 0, 1, 1, 0, 0]
WALK_ARM = [(8, 14), (6, 11), (3, 6), (0, 0), (-3, -4), (0, 0), (3, 6), (6, 11)]
# the coat's red lining shows where the near thigh leaves the opening (row: (first, last column), squares left clear)
LINING = {89: (58, 63), 90: (58, 63), 91: (57, 63), 92: (57, 63)}
LINING_RGB = (0xA3, 0x14, 0x1E)
HEAD_ROWS = (59, 76)             # the head and the hat (and the hair falling behind the neck)
BOOTS = 95                       # the boots' first row: a crouch lowers everything above it

# the standing actions, per frame: (far arm (upper, forearm degrees from the design's hang, + forward) or None = the
# design's own arm, lift rows, lean columns, crouch rows, head dip rows); None = the design
POSES = {
    # release on tick 12 = 200 ms = the start of frame 4: he leans back a column in 2-3 (the arm hanging, both arms in
    # sight - drawn back behind the coat it vanished), then the arm flings forward-up with the body a column forward
    "attack": [None, (None, 0, -1, 0, 0), (None, 0, -1, 0, 0), ((112, 122), 0, 1, 0, 0), ((98, 104), 0, 0, 0, 0),
               ((48, 60), 0, 0, 0, 0)],
    # Q: the same throw, level (the band flies level), a hop in frames 2-3
    "skill": [None, (None, 1, -1, 0, 0), (None, 1, -1, 0, 0), ((84, 90), 0, 1, 0, 0), ((78, 84), 0, 0, 0, 0),
              ((38, 52), 0, 0, 0, 0)],
    # W: a flick of the hand as the cards start to turn over his head
    "skill2": [((32, 52), 0, 0, 0, 0), ((60, 80), 0, 0, 0, 0)],
    # Destiny: League barely moves; the free hand rises a little
    "ult": [((14, 26), 0, 0, 0, 0), ((28, 46), 0, 0, 0, 0), ((34, 54), 0, 0, 0, 0), ((22, 38), 0, 0, 0, 0)],
    # the Gate: League crouches under the hat while the gate turns round him - the coat comes down over the boots
    # (CROUCH: everything above them lower) and the head bows a row more
    "ult_gate": [(None, 0, 0, 1, 0), (None, 0, 0, 2, 1), (None, 0, 0, 2, 1), (None, 0, 0, 2, 1), (None, 0, 0, 2, 1),
                 (None, 0, 0, 2, 1)],
    # landing: out of the crouch
    "ult_land": [(None, 0, 0, 2, 1), (None, 0, 0, 1, 0), None],
    "hit": [(None, 0, -1, 0, 0), None],
}
# the death: degrees the whole design turns back (counter-clockwise) about the near heel, and rows it still rides
# over the ground (the bounce); frame 1 is the hit
HEEL = (56.0, 100.0)             # the near sole's back corner, continuous
DEAD = [None, (10, 0), (22, 0), (38, 0), (56, 0), (74, 0), (90, 1), (90, 0)]
LIE_X = 15                       # columns the falling body slides forward by the time it lies (the hips land near the
                                 # heels, not a whole body length behind them)


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if os.name != "nt" or p.startswith(pre) else pre + p


def design():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def mask_of(spec):
    m = np.zeros((128, 128), bool)
    for r, cols in spec.items():
        m[r, cols] = True
    return m


def put(dst, src, ox, oy, under=False):
    """src's opaque squares onto dst with src's top-left at (ox, oy); under=True only where dst is clear."""
    ys, xs = np.nonzero(src[..., 3])
    cy, cx = ys + oy, xs + ox
    ok = (cy >= 0) & (cy < dst.shape[0]) & (cx >= 0) & (cx < dst.shape[1])
    ys, xs, cy, cx = ys[ok], xs[ok], cy[ok], cx[ok]
    if under:
        free = dst[cy, cx, 3] == 0
        ys, xs, cy, cx = ys[free], xs[free], cy[free], cx[free]
    dst[cy, cx] = src[ys, xs]
    return dst


def turned(s, j, deg):
    """(sprite, joint) turned deg counter-clockwise on screen about the joint (pixel-centre coordinates)."""
    if abs(deg) < 1e-9:
        return s, j
    if abs(deg) % 90 < 1e-9:
        return RN.op(s, j, ("rot", int(round(deg / 90)) % 4))
    return RN.rotsprite(s, j, deg)


def place(dst, s, j, target, under=False):
    """Sprite s with its joint j (pixel-centre) on the continuous canvas point target."""
    return put(dst, s, int(math.floor(target[0] - j[0])), int(math.floor(target[1] - j[1])), under)


def place_bone(bone, theta, drop=()):
    """The bone's squares relative to its joint, pointing theta degrees from its hang (+ forward, toward the right of
    the screen; 180 = up), and the offset of its last row: rows within 45 degrees of straight down shifted by the
    slope, across the screen a quarter turn with the outer side up, up the strip upside down (ryze_arms.place)."""
    rows = sorted({a for a, _ in bone})
    keep = [a for a in rows if a not in drop]
    remap = {a: i for i, a in enumerate(keep)}
    t = math.radians(theta)
    sx, cy = math.sin(t), math.cos(t)
    slope = min(abs(sx), abs(cy)) / max(abs(sx), abs(cy))
    if slope > WIDEN:
        # near 45 degrees rows shifted a square each are thinner across than the hanging bone: each row one more
        # square in its middle
        wide = {}
        for a in rows:
            row = {c: k for (a_, c), k in bone.items() if a_ == a}
            inner = sorted(c for c, k in row.items() if k != "o")
            if len(inner) < 2:
                wide.update({(a, c): k for c, k in row.items()})
                continue
            mid = inner[len(inner) // 2]
            for c, k in row.items():
                wide[(a, c + 1 if c > mid else c)] = k
            wide[(a, mid + 1)] = row[mid]
        bone = wide
    out = {}
    for (a, c), k in bone.items():
        if a not in remap:
            continue
        a2 = remap[a]
        if abs(theta) <= 45:
            X, Y = c + int(math.floor(a2 * sx / cy + 0.5)), a2
        elif abs(theta) >= 135:
            X, Y = c + int(math.floor(a2 * sx / -cy + 0.5)), -a2
        elif theta > 0:
            X, Y = a2, -c + int(math.floor(a2 * cy / sx + 0.5))
        else:
            X, Y = -a2, -c + int(math.floor(a2 * cy / -sx + 0.5))
        out[(X, Y)] = k
    n = len(keep) - 1
    if abs(theta) <= 45:
        end = (int(math.floor(n * sx / cy + 0.5)), n)
    elif abs(theta) >= 135:
        end = (int(math.floor(n * sx / -cy + 0.5)), -n)
    elif theta > 0:
        end = (n, int(math.floor(n * cy / sx + 0.5)))
    else:
        end = (-n, int(math.floor(n * cy / -sx + 0.5)))
    return out, end


def step_of(theta):
    t = math.radians(theta)
    sx, cy = math.sin(t), math.cos(t)
    if abs(sx) <= abs(cy):
        return (int(math.floor(sx / abs(cy) + 0.5)), 1 if cy > 0 else -1)
    return (1 if sx > 0 else -1, int(math.floor(cy / abs(sx) + 0.5)))


def close_gaps(cells):
    """Empty squares between two coloured arm squares (the elbow's corner, a row's step) take the colour beside them;
    twice (ryze_arms.close_gaps)."""
    for _ in range(2):
        add = {}
        for (x, y), k in cells.items():
            for ox, oy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                q = (x + ox, y + oy)
                if q in cells or q in add:
                    continue
                opp = (q[0] + ox, q[1] + oy)
                if opp in cells and cells[opp] != "o" and k != "o":
                    add[q] = k
        cells.update(add)
    return cells


def far_arm(up, fore, shoulder=SHOULDER):
    """{(x, y): letter} of the design's far arm with its sleeve `up` and its forearm `fore` degrees from their hang
    (+ forward), the sleeve's top square on `shoulder`."""
    s = abs(math.sin(math.radians(up)))
    n = int(math.floor(len(FORESHORTEN_UP) * max(0.0, s - 0.35) / 0.65 + 0.5))
    cu, end = place_bone(UPPER, up, tuple(FORESHORTEN_UP[:n]))
    sx, sy = shoulder
    out = {(sx + x, sy + y): k for (x, y), k in cu.items()}
    st = step_of(fore)
    ex, ey = sx + end[0] + st[0], sy + end[1] + st[1]
    cf, _ = place_bone(FORE, fore)
    for (x, y), k in cf.items():
        out[(ex + x, ey + y)] = k
    return close_gaps(out)


def paint(c, cells):
    for (x, y), k in cells.items():
        if 0 <= y < 128 and 0 <= x < 128:
            c[y, x] = (*ARM_RGB[k], 255)
    return c


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        arm = mask_of(FAR_ARM)
        self.body = d.copy()
        self.body[arm] = 0
        self.near_leg = mask_of(NEAR_LEG)
        self.far_leg = mask_of(FAR_LEG)
        self.trunk = self.body.copy()                      # the body without the legs (the walk)
        self.trunk[self.near_leg | self.far_leg] = 0


def shifted(a, dx, dy):
    out = np.zeros_like(a)
    put(out, a, dx, dy)
    return out


def dipped(body, n):
    """The head and hat `n` rows lower, laid over the collar."""
    if not n:
        return body
    out = body.copy()
    head = np.zeros_like(body)
    head[HEAD_ROWS[0]:HEAD_ROWS[1] + 1] = body[HEAD_ROWS[0]:HEAD_ROWS[1] + 1]
    out[HEAD_ROWS[0]:HEAD_ROWS[1] + 1] = 0
    return put(out, head, 0, n)


def crouched(body, n):
    """Everything above the boots (row BOOTS) `n` rows lower, laid over them: a crouch under the long coat."""
    if not n:
        return body
    out = body.copy()
    top = np.zeros_like(body)
    top[:BOOTS] = body[:BOOTS]
    out[:BOOTS] = 0
    return put(out, top, 0, n)


def leaned(body, n):
    """Everything above the boots `n` columns over (the boots stay)."""
    if not n:
        return body
    out = body.copy()
    top = np.zeros_like(body)
    top[:95] = body[:95]
    out[:95] = 0
    return put(out, top, n, 0)


def standing(P, pose):
    if pose is None:
        return P.design.copy()
    arm, lift, lean, crouch, dip = pose
    body = leaned(crouched(dipped(P.body if arm is not None else P.design, dip), crouch), lean)
    c = np.zeros((128, 128, 4), np.uint8)
    if arm is not None:
        paint(c, far_arm(*arm, shoulder=(SHOULDER[0] + lean, SHOULDER[1] + crouch)))
    put(c, body, 0, 0)                   # the body over the far arm
    return shifted(c, 0, -lift) if lift else c


def leg_sprite(P, m, dx, drop, lift):
    """The leg's squares as a straight leg turned about HIP: each row above ANKLE moved in proportion (and dropped
    with the body), the boot from ANKLE down moved `dx` columns whole and lifted `lift` rows, over the shin."""
    shin = np.zeros((128, 128, 4), np.uint8)
    boot = np.zeros((128, 128, 4), np.uint8)
    for r, c in zip(*np.nonzero(m)):
        if r < ANKLE:
            sh = int(math.floor(dx * (r - HIP) / (ANKLE - HIP) + 0.5))
            rr, tgt = r + drop, shin
        else:
            sh = int(math.floor(dx + 0.5))
            rr, tgt = r - lift, boot
        if 0 <= rr < 128 and 0 <= c + sh < 128:
            tgt[rr, c + sh] = P.design[r, c]
    return put(shin, boot, 0, 0)


def walk(P, k):
    s = SWING[k]
    ndx = NEAR_AT + s - NEAR_ANKLE
    fdx = FAR_AT - s - FAR_ANKLE
    drop = DROP[k]
    c = np.zeros((128, 128, 4), np.uint8)
    put(c, leg_sprite(P, P.far_leg, fdx, drop, FAR_LIFT[k]), 0, 0)
    paint(c, far_arm(*WALK_ARM[k], shoulder=(SHOULDER[0], SHOULDER[1] + drop)))
    put(c, shifted(P.trunk, 0, drop), 0, 0)
    for r, (c0, c1) in LINING.items():          # the lining where the near thigh left the opening
        for x in range(c0, c1 + 1):
            if not c[r + drop, x, 3]:
                c[r + drop, x] = (*LINING_RGB, 255)
    put(c, leg_sprite(P, P.near_leg, ndx, drop, NEAR_LIFT[k]), 0, 0)
    return c


def grounded(a):
    """The figure moved up so its lowest square is on the soles row (a fall turns the back of the coat under it)."""
    ys = np.nonzero(a[..., 3].any(1))[0]
    low = ys.max()
    return shifted(a, 0, SOLES - low) if low != SOLES else a


def dead(P, k):
    if DEAD[k] is None:
        return standing(P, POSES["hit"][0])
    deg, up = DEAD[k]
    s, j = turned(P.design, (HEEL[0] - 0.5, HEEL[1] - 0.5), deg)
    c = np.zeros((128, 128, 4), np.uint8)
    place(c, s, j, (HEEL[0] + LIE_X * deg / 90, HEEL[1]))
    c = grounded(c)
    return shifted(c, 0, -up) if up else c


def holes(a):
    """Enclosed clear components (4-connected) as lists of (y, x)."""
    op = a[..., 3] > 0
    H, W = op.shape
    seen = np.zeros((H, W), bool)
    st = [(y, x) for y in range(H) for x in (0, W - 1)] + [(y, x) for x in range(W) for y in (0, H - 1)]
    st = [(y, x) for y, x in st if not op[y, x]]
    for y, x in st:
        seen[y, x] = True
    while st:
        y, x = st.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                st.append((ny, nx))
    hole = ~op & ~seen
    out, lab = [], np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero(hole)):
        if lab[y, x]:
            continue
        comp, st = [], [(y, x)]
        lab[y, x] = True
        while st:
            cy, cx = st.pop()
            comp.append((cy, cx))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if hole[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = True
                    st.append((ny, nx))
        out.append(comp)
    return out


def pieces(a):
    """8-connected opaque components, largest first."""
    op = a[..., 3] > 0
    H, W = op.shape
    lab = np.zeros((H, W), bool)
    comps = []
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        comp, st = [], [(y, x)]
        lab[y, x] = True
        while st:
            cy, cx = st.pop()
            comp.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = True
                        st.append((ny, nx))
        comps.append(comp)
    return sorted(comps, key=len, reverse=True)


def fill_pinholes(a, most):
    """Enclosed gaps of up to `most` squares take the commonest colour round them that is not the outline (the
    outline when nothing else is round them)."""
    for comp in holes(a):
        if len(comp) > most:
            continue
        cs = set(comp)
        nb = Counter()
        for y, x in comp:
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (y + dy, x + dx)
                if q not in cs and a[q][3] and tuple(int(v) for v in a[q][:3]) != OUT:
                    nb[tuple(int(v) for v in a[q])] += 1
        col = np.array(nb.most_common(1)[0][0] if nb else OUT + (255,), np.uint8)
        for y, x in comp:
            a[y, x] = col
    return a


def drop_strays(a):
    """Outline squares with no coloured square among their 8 neighbours go (RotSprite's and the completion's
    doubled corners), until none is left; the design has none."""
    while True:
        op = a[..., 3] > 0
        ink = op & (a[..., :3] == np.array(OUT, np.uint8)).all(-1)
        col = np.pad(op & ~ink, 1)
        H, W = op.shape
        near = np.zeros((H, W), bool)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    near |= col[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
        gone = ink & ~near
        if not gone.any():
            return a
        a[gone] = 0


def finish(a):
    """Pinholes (enclosed gaps up to 3 squares) take the colour round them; the outline closes round the moved edges
    (strips.complete_outline); stray outline squares and crumbs of under 3 squares go; pinholes the completion shut
    (up to 2 squares) are filled."""
    a = fill_pinholes(a.copy(), 3)
    low = int(np.nonzero(a[..., 3].any(1))[0].max())
    a, _, _ = strips.complete_outline(a, color=OUT, feet=max(SOLES, low))
    a = drop_strays(a)
    for comp in pieces(a)[1:]:
        if len(comp) < 3:
            for y, x in comp:
                a[y, x] = 0
    return fill_pinholes(a, 2)


def frames(P, tag):
    n = len(MS[tag])
    if tag == "idle":
        return [P.design.copy() for _ in range(n)]
    if tag == "run":
        return [finish(walk(P, k)) for k in range(n)]
    if tag == "dead":
        return [finish(dead(P, k)) for k in range(n)]
    return [finish(standing(P, p)) if p is not None else P.design.copy() for p in POSES[tag]]


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def sheet(frs):
    cw, ch = CELL
    cols, rows = layout(len(frs))
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for i, f in enumerate(frs):
        X, Y = (i % cols) * cw, (i // cols) * ch
        y0 = PIVOT[1] - CELL_PIVOT[1]
        x0 = PIVOT[0] - CELL_PIVOT[0]
        sub = f[y0:y0 + ch, x0:x0 + cw]
        if f[..., 3].sum() != sub[..., 3].sum():
            raise SystemExit(f"frame {i}: part of it falls outside the {cw}x{ch} cell")
        out[Y:Y + ch, X:X + cw] = sub
    return out


def review(P, built, out_dir, z=6):
    """One picture per strip: the design, then each frame, at z x on a grey ground, with the soles line."""
    os.makedirs(out_dir, exist_ok=True)
    for tag, frs in built.items():
        tiles = [("design", P.design)] + [(f"{tag} {i + 1}", f) for i, f in enumerate(frs)]
        x0, x1, y0, y1 = 12, 116, 52, 104
        W = (x1 - x0) * z
        img = Image.new("RGB", (len(tiles) * (W + 6), (y1 - y0) * z + 18), (40, 40, 40))
        for i, (name, f) in enumerate(tiles):
            sub = f[y0:y1, x0:x1]
            bg = Image.new("RGBA", (W, (y1 - y0) * z), (110, 120, 108, 255))
            bg.alpha_composite(Image.fromarray(sub).resize((W, (y1 - y0) * z), Image.NEAREST))
            d = ImageDraw.Draw(bg)
            yl = (SOLES + 1 - y0) * z
            d.line([(0, yl), (W, yl)], fill=(60, 60, 200, 255))
            img.paste(bg.convert("RGB"), (i * (W + 6), 18))
            ImageDraw.Draw(img).text((i * (W + 6) + 4, 3), name, fill=(255, 255, 255))
        img.save(os.path.join(out_dir, f"rig_{tag}.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write review sheets to this folder")
    ap.add_argument("--out", default=NATIVE)
    a = ap.parse_args()
    P = Parts()
    built = {tag: frames(P, tag) for tag in TAGS}
    bad = 0
    for tag in TAGS:
        big = Image.fromarray(np.repeat(np.repeat(sheet(built[tag]), Z, 0), Z, 1))
        path = os.path.join(a.out, f"twistedfate_{tag}.png")
        if a.check:
            same = os.path.exists(lp(path)) and np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")),
                                                                np.asarray(big))
            print(tag, "same" if same else "DIFFERS")
            bad += not same
        else:
            big.save(lp(path))
        n = [len(pieces(f)) for f in built[tag]]
        print(f"{tag}: {len(built[tag])} frames, pieces {n}")
    cells = {"cell": list(CELL), "scale": Z,
             "tags": {tag: [{"pivot": list(CELL_PIVOT), "ms": ms} for ms in MS[tag]] for tag in TAGS}}
    cpath = os.path.join(a.out, "twistedfate_cells.json")
    text = json.dumps(cells, indent=1) + "\n"
    if a.check:
        same = os.path.exists(lp(cpath)) and open(lp(cpath), encoding="utf-8").read() == text
        print("cells", "same" if same else "DIFFERS")
        bad += not same
    else:
        with open(lp(cpath), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    if a.review:
        review(P, built, a.review)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

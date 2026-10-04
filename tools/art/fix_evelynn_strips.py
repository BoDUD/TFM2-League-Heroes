#!/usr/bin/env python3
"""Evelynn's strips: Codex's delivery (assets/source/evelynn/codex_strips/evelynn_<tag>_1x.png) with the frames that
read wrong rebuilt from the design's own pixels, written as the 8x strips tools/art/import_native.py reads
(assets/source/native/evelynn_<tag>.png).

    python tools/art/fix_evelynn_strips.py [--review DIR]

Codex built every action from the design's parts (the head pasted unchanged, torso and legs moved by region, arms and
lashers drawn on the 1x grid). Most frames read as League's poses; these did not (2026-10-05, the user: 「有奇怪的地方你
直接修复 codex太笨了」):
  - run: both arms held out like a scarecrow, the two legs one dark tangle, the lashers two thick straight bars along the
    ground. Rebuilt: the design's upper body (head, torso, both arms, the crotch) upright, dipping a row when both feet
    are down (League's head is lowest at the footfalls); the legs on tools/art/evelynn_legs.py's rig - the design's own
    near leg (pink thigh from the belt, knee, shin, foot) for both, bent at hip and knee - on League's 8-frame step
    measured on the game-size render (each foot planted ahead, sweeping back, lifted and swung forward, half a cycle
    apart, each under its own hip); the two lashers trailing behind like League's run, one up, one low: each a tapering
    band from her back hip ending in the design's own blade (the idle's back-lasher tip, unrotated), following the bob
    a frame late. (A first pass drew thin 3-square legs that crossed in an X: 「走路时腿有点怪吧？」.)
  - attack 3-5, attack_e 4-5, attack_e2 1-5, skill 2, ult 1 and 3-5: Codex's lunges and crouches stood on the
    design's shins shifted row by row into thin stair-stepped sticks, without the thighs, the back foot out in a split
    (「放技能时腿也有点怪吧？」). Their legs come out (RELEG), the rest is raised back to the standing height, and they
    stand on the rig's legs in the idle's stance (the rule since Caitlyn: casting frames stand on the idle's legs); the
    lunge stays as the body's step forward. Codex's own hips go too (hips_cleared; left in, its pink thigh tops stuck out
    beside the rig's: 「这里凸出来的是什么」, ult 4); the legs are set under Codex's belt (hip_shift). Dead 2 holds dead 1.
  - dead 5-8: the kneeling body turned 35, 65 and 90 degrees whole, ending head-down with the front lasher standing up
    in the air. League's death clip buckles her to her knees and keeps her slumped low (the game fades her out; she
    never lies down), which Codex's 1-4 already follow. 5-8 are frame 4 with the upper body sinking 1-2 rows over the
    knees. (Laid down instead - turned whole like Twisted Fate's fall - her wide hair stood up as a block and the
    lashers splayed like crab legs.)
  - hit 1-2, skill2 1, dead 1: the back lasher a straight bar with a black rim (Codex's own drawing): put back as the
    design's curled back lasher, nothing else touched.
Every frame then gets the outline the import closes and its pinholes plugged with the neighbours' colour (plugged()).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "evelynn", "codex_strips")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
TAGS = ["idle", "run", "attack", "attack_e", "attack_e2", "skill", "skill2", "ult", "hit", "dead"]
Z = 8
SOLE, MID = 99, 64            # the design canvas (128 x 128): soles row, feet middle column
CELL_DY = -18                 # design row 99 -> cell row 81 (pivot row 70 + 11)

C = {k: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for k, h in {
    "0": "#120C1C", "1": "#1E1646", "2": "#2A0E5C", "3": "#2E2470", "4": "#463C9E", "5": "#4A1C96", "6": "#6A62C8",
    "7": "#9C9CCC", "8": "#B070FF", "9": "#B81E6A", "a": "#CACAEE", "b": "#ECECFF", "c": "#EE3C8C", "d": "#F05AA0",
    "e": "#F4F4FF", "f": "#FF86BC", "g": "#FFC0DC", "h": "#FFD21E"}.items()}


def layout(n):
    return {1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (4, 1), 5: (3, 2), 6: (3, 2), 7: (4, 2), 8: (4, 2)}[n]


def design():
    a = np.asarray(Image.open(G.lp(os.path.join(NATIVE, "evelynn_native.png"))).convert("RGBA"))[4::8, 4::8]
    return a.copy()


def put(can, x, y, col):
    if 0 <= y < can.shape[0] and 0 <= x < can.shape[1]:
        can[y, x, :3] = C[col] if isinstance(col, str) else col
        can[y, x, 3] = 255


def paste(can, part, dx=0, dy=0):
    ys, xs = np.nonzero(part[..., 3] > 0)
    for y, x in zip(ys, xs):
        put(can, x + dx, y + dy, tuple(int(v) for v in part[y, x, :3]))


def region(d, keep):
    """The design's pixels where keep(x, y) holds."""
    out = np.zeros_like(d)
    ys, xs = np.nonzero(d[..., 3] > 0)
    for y, x in zip(ys, xs):
        if keep(x, y):
            out[y, x] = d[y, x]
    return out


# ------------------------------------------------------------------ the design's parts (design canvas coordinates)
def is_back_lasher(x, y):
    """The idle's back lasher: everything left of the hips from row 86 down (its blade at columns 38-43), not the
    near hand's claw (rows 85-86, columns 49-52)."""
    if y >= 86 and x <= 53:
        return not (y == 86 and 49 <= x <= 52)
    return y >= 91 and x <= 54


def blade(d):
    """The back lasher's tip (columns 37-45, rows 85-92): the curved lilac blade, pointing up. Anchor: its foot
    (41, 93), where the lasher's body joins it in the idle."""
    return region(d, lambda x, y: x <= 45 and 85 <= y <= 92), (41, 93)


def back_lasher(d):
    return region(d, is_back_lasher)


# ------------------------------------------------------------------ drawing in the design's materials
def bezier(p0, p1, p2, n=60):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


def band(can, pts, r0, r1):
    """A tapering lasher body along pts (radius r0 at the root to r1 at the end): dark violet '2' inside, indigo '1'
    rim (the idle lasher's two colours), drawn over what is there."""
    body = {}
    for i, (x, y) in enumerate(pts):
        r = r0 + (r1 - r0) * i / (len(pts) - 1)
        for yy in range(int(y - r - 1), int(y + r + 2)):
            for xx in range(int(x - r - 1), int(x + r + 2)):
                dd = math.hypot(xx - x, yy - y)
                if dd <= r:
                    body[(xx, yy)] = min(body.get((xx, yy), 9), dd - r)
    for (x, y), m in body.items():
        rim = any((x + ex, y + ey) not in body for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        put(can, x, y, "1" if rim else "2")


def lasher(can, bl, root, ctrl, end, r0=1.5, r1=1.0):
    """A trailing lasher: a band from her hip to `end`, the blade's foot set on `end`."""
    sprite, (bx, by) = bl
    band(can, bezier(root, ctrl, (end[0] + 0.5, end[1] - 0.5)), r0, r1)
    paste(can, sprite, end[0] - bx, end[1] - by)


# ------------------------------------------------------------------ run
# League's run on the game-size render (8 x 125 ms), on the rig's legs (tools/art/evelynn_legs.py): each ankle's
# offset from its own standing place and its lift, the far leg half a cycle behind. A planted foot sweeps from 3.5
# ahead to 2.5 behind, lifts off behind, swings forward 2.5 rows up and lands ahead; each leg stays under its own hip
# (no X across the knees), the near foot a little ahead of the far one while it leads. The body dips a row when both
# feet are down (League's head is lowest at the footfalls).
RUN_STEP = [(3.5, 0), (1.5, 0), (-0.5, 0), (-2.5, 0), (-3.5, 1), (-1.5, 2.5), (1.0, 2.5), (3.0, 1)]
RUN_BOB = [1, 0, 0, 0, 1, 0, 0, 0]
FAR_STAND = 1.0                  # the far ankle's place in the run: a square right of its hip (the idle's 3 is a stance)
# the lashers (root, control, blade foot) trailing behind, the upper one raised, the lower one low; their roots ride
# with her hips, the rest follows the bob a frame late (a lash trailing), never more than a row a frame
RUN_LASH = [((54, 87), (46, 95), (40, 88)), ((55, 89), (44, 100), (32, 95))]


def run_frame(d, k):
    import evelynn_legs as LG
    can = np.zeros_like(d)
    bl = blade(d)
    bob = RUN_BOB[k]
    late = RUN_BOB[k - 1]
    for root, ctrl, end in RUN_LASH:
        lasher(can, bl, (root[0], root[1] + bob), (ctrl[0], ctrl[1] + late), (end[0], end[1] + late))
    tex, ft = LG.texture(d), LG.foot(d)
    near_dx, near_up = RUN_STEP[k]
    far_dx, far_up = RUN_STEP[(k + 4) % 8]
    hip_far = (LG.HIP_FAR[0], LG.HIP_FAR[1] + bob)
    LG.draw(can, tex, ft, hip_far, (hip_far[0] + FAR_STAND + far_dx, LG.FOOT_Y - far_up))
    paste(can, LG.body(d, is_back_lasher), 0, bob)
    hip_near = (LG.HIP_NEAR[0], LG.HIP_NEAR[1] + bob)
    LG.draw(can, tex, ft, hip_near, (hip_near[0] + near_dx, LG.FOOT_Y - near_up))
    return can


# ------------------------------------------------------------------ action frames: Codex's legs replaced by the rig's
# Codex built the lunges and crouches from the design's shins shifted row by row: thin stair-stepped sticks, longer than
# the idle's legs, without the pink thighs, the back foot out in a split (the user: 「放技能时腿也有点怪吧？」). In these
# frames everything under the waist that is leg - the legs' colours, and pink on the thighs' track - goes; Codex's
# lashers (within reach of its own lasher_paths in manifest.json), claws and sleeves stay. The rig's legs go in from
# the hips (where Codex's upper body put the design's hips: its head_translation) to Codex's own feet, pulled in when
# they are out of a leg's reach: the near leg to the back foot, the far one to the front foot, so they never cross.
RELEG = {"attack": [2, 3, 4], "attack_e": [3, 4], "attack_e2": [0, 1, 2, 3, 4], "skill": [1], "ult": [0, 2, 3, 4]}
LEGISH = {C[k] for k in "01236"}
LILAC = {C[k] for k in "78"}
PINKS = {C[k] for k in "c9"}
GROUND_Y = 81                    # the soles' cell row (pivot row 70 + 11)


def seg_dist(px_, py_, a, b):
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if not L2 else max(0.0, min(1.0, ((px_ - ax) * vx + (py_ - ay) * vy) / L2))
    return math.hypot(px_ - ax - t * vx, py_ - ay - t * vy)


def releg(d, frame, info):
    """Codex's legs out (see RELEG); the rest of the frame - head, torso, arms, claws, lashers - raised back to the
    standing height (League's lunge kept as the whole body's step forward, Codex's head_translation x), on the rig's
    legs in the idle's stance, set under Codex's own belt (hip_shift)."""
    import evelynn_legs as LG
    tx, ty = info["head"]["head_translation"]
    paths = info["head"]["lasher_paths"]
    waist = LG.HIP_Y + ty
    out = frame.copy()
    H, W = frame.shape[:2]
    claw = claws(frame)
    for y in range(waist, H):
        for x in range(W):
            if not frame[y, x, 3]:
                continue
            col = tuple(int(v) for v in frame[y, x, :3])
            if on_lasher(x + 0.5, y + 0.5, col, paths):
                continue
            # the legs' colours, pink that is no claw (Codex's thighs and knees, wherever it moved them) and lilac off
            # the lashers (the idle's front-lasher curl Codex left on the far leg it moved)
            if col in LEGISH or (col in PINKS and not claw[y, x]) or col in LILAC:
                out[y, x] = 0
    up = ty - CELL_DY                                  # rows Codex lowered the body
    raised = np.zeros_like(out)
    paste(raised, out, 0, -up)
    sx, sy = hip_shift(d, raised, tx)
    if sy:
        moved = np.zeros_like(raised)
        paste(moved, raised, 0, -sy)
        raised = moved
    can = np.zeros_like(frame)
    tex, ft = LG.texture(d), LG.foot(d)
    hx = tx + sx
    hip_n = (LG.HIP_NEAR[0] + hx, LG.HIP_NEAR[1] + CELL_DY)
    hip_f = (LG.HIP_FAR[0] + hx, LG.HIP_FAR[1] + CELL_DY)
    LG.draw(can, tex, ft, hip_f, (LG.STAND_FAR[0] + hx, LG.STAND_FAR[1] + CELL_DY))
    crotch = region(d, lambda x, y: LG.HIP_Y <= y <= LG.HIP_Y + 2 and 59 <= x <= 62)
    paste(can, crotch, hx, CELL_DY)
    LG.draw(can, tex, ft, hip_n, (LG.STAND_NEAR[0] + hx, LG.STAND_NEAR[1] + CELL_DY))
    paste(can, hips_cleared(raised, hip_n, hip_f, paths, up + sy), 0, 0)
    return crumbs_off(can)


LASH_COL = {C[k] for k in "0125678"}


def on_lasher(cx, cy, col, paths):
    """A square of Codex's lashers: a lasher colour within reach of a lasher path past its first 4 squares (the paths
    start inside the hips, where the hip block's own squares would pass), or near the path's end (the blade)."""
    if col not in LASH_COL:
        return False
    for p in paths:
        cut = trim(p, 4.0)
        if any(seg_dist(cx, cy, a, b) <= 2.5 for a, b in zip(cut, cut[1:])):
            return True
        if math.hypot(cx - p[-1][0] - 0.5, cy - p[-1][1] - 0.5) <= 4.5:
            return True
    return False


def trim(path, n):
    """The polyline without its first n squares of length."""
    out, left = [], n
    for a, b in zip(path, path[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if not out and left >= L:
            left -= L
            continue
        if not out:
            t = left / L if L else 0
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        out.append(b)
    return out if len(out) >= 2 else list(path[-2:])


def hip_shift(d, raised, tx):
    """Where Codex left the design's lower torso (rows 81-84, columns 55-64: the belt and the rows over it) in the raised
    frame, from where its head went: the (dx, dy) with the most squares of the same colour - Codex moved its torso apart
    from the head in some lunges (ult 4: three columns left)."""
    tpl = [(x, y, tuple(int(v) for v in d[y, x, :3])) for y in range(81, 85) for x in range(55, 65) if d[y, x, 3]]
    best = (-1, 0, 0)
    for dy in range(-2, 3):
        for dx in range(-6, 7):
            hit = 0
            for x, y, c in tpl:
                X, Y = x + tx + dx, y + CELL_DY + dy
                if 0 <= X < raised.shape[1] and 0 <= Y < raised.shape[0] and raised[Y, X, 3] and \
                        tuple(int(v) for v in raised[Y, X, :3]) == c:
                    hit += 1
            if hit > best[0] or (hit == best[0] and abs(dx) + abs(dy) < abs(best[1]) + abs(best[2])):
                best = (hit, dx, dy)
    return (best[1], best[2]) if best[0] >= len(tpl) * 0.35 else (0, 0)


CLAW_TIP = {C[k] for k in "gf"}


def claws(f):
    """Squares of the claws: pink pieces (c, 9, g, f; 4-connected) that hold a claw tip (g, f) - thighs and knees have
    none."""
    H, W = f.shape[:2]
    pink = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if f[y, x, 3] and tuple(int(v) for v in f[y, x, :3]) in (PINKS | CLAW_TIP):
                pink[y, x] = True
    lab, n = G.label(pink)
    out = np.zeros((H, W), bool)
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if any(tuple(int(v) for v in f[y, x, :3]) in CLAW_TIP for y, x in zip(ys, xs)):
            out[lab == i] = True
    return out
KEEP_HUE = {C[k] for k in "4578"}                  # sleeves, violet, lilac: never leg or hip material


def hips_cleared(raised, hip_n, hip_f, paths, up):
    """Codex's own hips and thigh tops off the raised frame, where the rig's hips and thighs now are (left in, its pink
    thigh tops stuck out beside the rig's: the user, 「这里凸出来的是什么」, ult 4). In a box round the rig's hips from
    three rows over the belt down, a square stays when it is on Codex's lashers, a sleeve or violet colour, or on a
    claw - a pink piece that has a claw tip (g, f) - or touches one; under the belt every other square goes, over it
    only pink without a tip."""
    import evelynn_legs as LG
    out = raised.copy()
    H, W = out.shape[:2]
    belt = LG.HIP_Y + CELL_DY
    x0, x1 = int(min(hip_n[0], hip_f[0])) - 7, int(max(hip_n[0], hip_f[0])) + 10
    y0 = belt - 3
    pink = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if out[y, x, 3] and tuple(int(v) for v in out[y, x, :3]) in (PINKS | CLAW_TIP):
                pink[y, x] = True
    claw = claws(out)
    near_claw = claw.copy()
    near_claw[1:] |= claw[:-1]
    near_claw[:-1] |= claw[1:]
    near_claw[:, 1:] |= claw[:, :-1]
    near_claw[:, :-1] |= claw[:, 1:]
    for y in range(max(0, y0), H):
        for x in range(max(0, x0), min(W, x1)):
            if not out[y, x, 3]:
                continue
            col = tuple(int(v) for v in out[y, x, :3])
            if on_lasher(x + 0.5, y + 0.5 + up, col, paths) or col in KEEP_HUE or near_claw[y, x]:
                continue
            if y < belt and not (pink[y, x] and not claw[y, x]):
                continue                                   # over the belt only the thigh tops go
            out[y, x] = 0
    return out


def crumbs_off(f, keep=12):
    """Pieces under `keep` squares off: a lasher tip Codex hung on a leg it drew (attack 3, skill 2, ult 5)."""
    op = f[..., 3] > 0
    lab, n = G.label(op)
    if n <= 1:
        return f
    sizes = np.bincount(lab.ravel())
    out = f.copy()
    for i in range(1, n + 1):
        if sizes[i] < keep:
            out[lab == i] = 0
    return out


# ------------------------------------------------------------------ dead 5-8: the slump held
# League's death clip: she buckles to her knees and stays slumped low while the game fades her out (it never lies her
# down). Codex's 1-4 follow it (a stagger, the knees, the slump with both lashers flat on the ground); 5-8 turned that
# kneeling figure 35-90 degrees whole, ending head-down with a lasher standing in the air. Now 5-8 are frame 4 with the
# upper body (cell rows over SLUMP_ROW) sinking 1, 2, 2, 2 rows over the knees and the lashers on the ground - nothing
# turned, nothing below the soles.
SLUMP_ROW = 76                   # the cell row of frame 4 above which the body sinks (its knees and lashers stay)
SLUMP = {4: 1, 5: 2, 6: 2, 7: 2}


def slumped(f4, rows, py):
    out = np.zeros_like(f4)
    low = f4.copy()
    low[:SLUMP_ROW + 1] = 0
    high = f4.copy()
    high[SLUMP_ROW + 1:] = 0
    out[:] = low
    ys, xs = np.nonzero(high[..., 3] > 0)
    for y, x in zip(ys, xs):
        if y + rows <= py + 11:
            out[y + rows, x] = high[y, x]
    return out


# ------------------------------------------------------------------ hit 1-2, skill2 1: the back lasher put back
BAR = {("hit", 0), ("hit", 1), ("skill2", 0), ("dead", 0)}
CLAW = {C[k] for k in "c9gf"}


def restore_back_lasher(d, frame, px):
    """Codex's straight bar (and its blade) left of the hand cleared, the design's curled back lasher laid under what
    stays. Design columns <= 51 from row 83 down, and the bar's rows 89-92 beside the hand (columns 52-56, the hips
    begin at 57) but for the claw's own pinks."""
    out = frame.copy()
    dx = px - MID
    for y in range(83 + CELL_DY, 96 + CELL_DY):
        for x in range(0, 57 + dx):
            dxx, dyy = x - dx, y - CELL_DY
            if dxx <= 51 or (89 <= dyy <= 92 and tuple(int(v) for v in out[y, x, :3]) not in CLAW):
                out[y, x] = 0
    lash = back_lasher(d)
    # the near thigh's left edge (columns 55-57 of rows 91-92), which Codex trimmed: it joins the lasher's curve to the leg
    for x, y in ((55, 91), (56, 91), (57, 91), (55, 92), (56, 92)):
        lash[y, x] = d[y, x]
    ys, xs = np.nonzero(lash[..., 3] > 0)
    for y, x in zip(ys, xs):
        X, Y = x + dx, y + CELL_DY
        if out[Y, X, 3] == 0:
            out[Y, X] = lash[y, x]
    return out


# ------------------------------------------------------------------ every frame: outline closed, pinholes plugged
OUTLINE = C["0"]


def plugged(f, py):
    """The outline the import closes (strips.complete_outline, nothing under the soles), then every pinhole - a clear
    square whose four neighbours are opaque - takes the colour most of those neighbours have: Codex's leaning chest in
    attack_e2 2 and 5 came as a checkerboard of 9-14 holes, the crossing legs leave one, and the design has three of
    its own (hair, chest, the back lasher's loop)."""
    from collections import Counter
    f = f.copy()
    for _ in range(4):                       # the closing can make a new pinhole, the plug a new edge: till both rest
        f, added, _ = G.complete_outline(f, color=OUTLINE, feet=py + 11)
        op = f[..., 3] > 0
        H, W = op.shape
        holes = [(y, x) for y in range(1, H - 1) for x in range(1, W - 1)
                 if not op[y, x] and op[y - 1, x] and op[y + 1, x] and op[y, x - 1] and op[y, x + 1]]
        for y, x in holes:
            cnt = Counter(tuple(int(v) for v in f[y + dy, x + dx, :3]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            top = max(cnt.values())
            f[y, x, :3] = max((c for c, v in cnt.items() if v == top), key=lambda c: sum(c))
            f[y, x, 3] = 255
        if not added and not holes:
            break
    return f


# ------------------------------------------------------------------ the strips
def load(tag):
    with open(G.lp(os.path.join(NATIVE, "evelynn_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"evelynn_{tag}_1x.png"))).convert("RGBA")).copy()
    return a, cells


def frames_of(a, n, cw, ch):
    cols, _ = layout(n)
    return [a[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw].copy() for k in range(n)]


def sheet_of(frs, cw, ch):
    cols, rows = layout(len(frs))
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k, f in enumerate(frs):
        out[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw] = f
    return out


def to_cell(can, px, cw, ch):
    """A design-canvas drawing into a cell whose pivot column is px (the design's feet middle on it, soles row 81)."""
    out = np.zeros((ch, cw, 4), np.uint8)
    ys, xs = np.nonzero(can[..., 3] > 0)
    for y, x in zip(ys, xs):
        X, Y = x + px - MID, y + CELL_DY
        if 0 <= X < cw and 0 <= Y < ch:
            out[Y, X] = can[y, x]
    return out


def build():
    d = design()
    out = {}
    for tag in TAGS:
        a, cells = load(tag)
        cw, ch = cells["cell"]
        rows = cells["tags"][tag]
        frs = frames_of(a, len(rows), cw, ch)
        if tag == "run":
            frs = [to_cell(run_frame(d, k), rows[k]["pivot"][0], cw, ch) for k in range(len(rows))]
        if tag == "dead":
            # frame 4 moved with each later pivot, so the slumped body stays where it knelt
            f4, p4 = frs[3], rows[3]["pivot"][0]
            frs = [slumped(np.roll(f4, rows[k]["pivot"][0] - p4, axis=1), SLUMP[k], rows[k]["pivot"][1]) if k in SLUMP
                   else f for k, f in enumerate(frs)]
        if tag in RELEG:
            man = json.load(open(G.lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
            frs = [releg(d, f, man["animations"][tag]["frames"][k]) if k in RELEG[tag] else f for k, f in enumerate(frs)]
        if tag in ("hit", "skill2", "dead"):
            frs = [restore_back_lasher(d, f, rows[k]["pivot"][0]) if (tag, k) in BAR else f for k, f in enumerate(frs)]
        if tag == "dead":
            # 2 holds 1's stagger: Codex's 2 stood on a stick leg, and on the rig's legs its hanging claw ran into the
            # thigh as one pink lump
            frs[1] = np.roll(frs[0], rows[1]["pivot"][0] - rows[0]["pivot"][0], axis=1)
        frs = [plugged(f, rows[k]["pivot"][1]) for k, f in enumerate(frs)]
        out[tag] = sheet_of(frs, cw, ch)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write <tag>_fix.png at 6x here instead of the strips")
    a = ap.parse_args()
    out = build()
    for tag, sheet in out.items():
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            im = Image.new("RGBA", (sheet.shape[1], sheet.shape[0]), (104, 112, 72, 255))
            im.alpha_composite(Image.fromarray(sheet))
            im.resize((sheet.shape[1] * 6, sheet.shape[0] * 6), Image.NEAREST).convert("RGB").save(
                os.path.join(a.review, f"{tag}_fix.png"))
            continue
        big = Image.fromarray(sheet).resize((sheet.shape[1] * Z, sheet.shape[0] * Z), Image.NEAREST)
        big.save(G.lp(os.path.join(NATIVE, f"evelynn_{tag}.png")))
    print("written" if not a.review else a.review)


if __name__ == "__main__":
    main()

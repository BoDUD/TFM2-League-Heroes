#!/usr/bin/env python3
"""Ryze's second design: Codex's strips (2026-10-03) finished for the game.

    python tools/art/fix_ryze_strips_v2.py [--check]

Codex drew every action again on the second design after the rig's frames read as strange to the user ("改不好就让gpt
重画吧", assets/source/ryze/codex_strips_v2: MODEL_STRIPS_V2.md's brief, its HANDOFF.md). It pasted the design's head into
every frame and the idle's legs under the standing ones. What is mended here (the user: 「有奇怪的地方你帮忙修正」):
- the waist (WAIST): where the pasted legs meet the generated body a row of ground opened under the belt in the standing
  frames ("腿部和身体分离" again; closed by the importer it became a dark line across the belt); those squares take the
  design's own squares at the same place (the belt and the hips stand where the idle's do), or else the commonest
  colour round them - first on the frame as drawn, then on the outline-closed copy;
- the neck: pockets of ground walled in next to the pasted head (the scroll's strap and the shoulder) take the design's
  squares at the same place from the head;
- small pockets elsewhere (at most POCKET squares: an arm and the body, the legs in the run; or a slit at most SLIT[1]
  squares wide between an arm and the body) the commonest colour round them.
The standing frames (IDLE_BODY: on the idle's own legs) then get the idle's own upper body. Codex drew the casting
bodies wider than the idle's, in a brown vest instead of the idle's navy shirt, with arms five or six squares thick and
fists of five (the idle's arms and hands are three); the user on the combo redrawn at a medium build: 「手臂待机和释放
技能时尺寸还是不一样」「上半身也是 释放技能上半身衣服变了」「体型也变了」. So in those frames:
- the body is the design's, square for square: the upper body without the arms (tools/art/rig_ryze.py's parts: the
  head, the scroll, the beard, the shirt and the strap, the shoulder pads, the belt, the teal flap) leaning as Codex's
  pasted head leans (a row shear over the hips, the head one block, at most 4 squares in the casts, LEAN_MAX in the
  recoils), over the idle's legs (the hips drawn in the design since: design_ryze_v2.py HIPS);
- the arms are Codex's own (its poses and hands): the squares outside that body (and the skin squares in front of it)
  in pieces holding skin, thinned where they are THICK or more squares deep from their edge (the outer layer taken
  off, the squares left on the new edge take the lit or dark colour of the one taken off beside them; a pointing
  finger in POINT kept), the near one moved in ARM_IN squares to the idle's shoulder; the far arm behind the body (in
  front of the scroll when raised across it: OVER_SCROLL), the near one in front of it, each with one outline;
then the pockets as above, those up to BODY_POCKET squares (between a thinned arm and the idle's narrower body)
from the design's squares there. After the review: the run's arms are the idle's turned to League's rhythm (RUN_POSE,
Codex's broke into pieces), the passing legs get their boots back (FEET), crumbs apart from the figure go (CRUMB), the
far arm Codex folded into a lump while shooting and the recoveries' short arms are the idle's own (IDLE_ARMS), and R's
channel stands (REUSE).
Writes assets/source/native/ryze_<tag>.png on the cells of assets/source/native/ryze_cells.json (the idle: the design
itself on all six pivots, with the same pocket fill); then run tools/art/import_native.py --hero ryze.
"""
import argparse
import json
import math
import os
import sys
from collections import Counter, deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402
import rig_ryze as R  # noqa: E402
import ryze_death as RD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ryze", "codex_strips_v2")
NAT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(ROOT, "assets", "source", "ryze", "design_v2", "ryze_design_v2_1x.png")
Z = 8
PIVOT = (64, 88)
INK = (0x0F, 0x02, 0x13)
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "ult_land", "hit", "dead"]
HEAD = (-7, 7, -29, -18)                         # the pasted head on the design (x0, x1, y0, y1 from the standing point)
WAIST = (-8, -2)                                 # rows from the standing point where the body meets the pasted legs
POCKET = 10
SLIT = (16, 2)                                   # a slit of ground (squares, widest row) between an arm and the body
# the frames on the idle's legs (every square of the shins and boots the idle's): the idle's upper body, Codex's arms
IDLE_BODY = {"attack": "all", "skill": "all", "skill2": "all", "ult": "all",
             "ult_land": [2, 3, 4], "hit": [1, 2], "dead": [1, 2]}
LEAN_MAX = {"hit": 8, "dead": 8}                 # squares at the neck (Codex's head stands up to 8 off the idle's):
                                                 # the recoils as far as Codex threw them; the casts none
BODY_POCKET = 30                                 # a pocket between a thinned arm and the idle's narrower body takes
                                                 # the design's squares there (the far upper arm under its pad)
ARM_IN = {"back": 0, "front": 2}                 # Codex's near shoulder stands 2 squares outside the idle's (its far
                                                 # arm already hangs under the idle's shoulder pad)
THICK = 3                                        # an arm 5+ squares thick: a square this deep within 2 of its edge
POINT = {("skill2", 2): "front", ("skill2", 9): "front", ("skill2", 10): "front"}   # the pointing finger kept
SHOULDER = {"back": (-7.0, -14.0), "front": (6.0, -13.5)}
SKIN = {tuple(int(R.PAL[k][i:i + 2], 16) for i in (0, 2, 4)) for k in "defgim"}
DARK = {tuple(int(R.PAL[k][i:i + 2], 16) for i in (0, 2, 4)) for k in "ab"}
# the arm's own colours: the skin, the bracer's leathers and golds (not the shirt's navy: Codex's wider body beside a
# far arm is no arm)
ARM_COLOURS = {tuple(int(R.PAL[k][i:i + 2], 16) for i in (0, 2, 4)) for k in "defgimhjqxyuD"}
BELT_ROW = -4                                    # the belt's last row (from the pivot): OWN_LEGS frames take Codex's legs under it
# the frames on Codex's own legs (the run's strides, W's kneel): the idle's upper body to its belt dropped to Codex's
# head over Codex's legs, Codex's arms drawn again
OWN_LEGS = {("run", k) for k in range(1, 9)}
# the crouches (Codex's kneel / squat, its head 6-15 rows down, its hips 2-8): CROUCH - none since the combo's
# Overload stands too (the user's rule since Caitlyn: the casts stand on the idle's own legs; Codex's kneel there was
# a dark heap of legs under a huge cloth flap)
CROUCH = set()
# the frames Codex drew alone (the landing's impact, the fall): its own head's crown cleared over the pasted head
# (HEAD_TOP), the lying ones lifted onto the soles' row (RAISE)
HEAD_TOP = {("ult_land", 1)}
RAISE = {}
# the death from frame 3 on the idle's own body (tools/art/ryze_death.py): Codex drew another, smeared body there under
# the pasted head (a bigger scroll, the coat and legs one dark mass)
DEATH = {3: ("kneel", 7), 4: ("kneel", 8), 5: ("slump", 10), 6: ("lying", 0), 7: ("lying", 0), 8: ("lying", 0)}
CUT_ROWS = range(-12, -5)                        # the torso's rows (from the pivot) a crouch may lose
MAX_CUT = 3
FLAP_TOP = -4                                    # the teal flap's top row on the design (from the pivot)
EYE_AT = (-1, -23)                               # the near eye's top-left white square on the design
ARM_STEPS = 16                                   # an arm's line at most this long (the idle's: shoulder to fingertips)
# the run's legs in the idle's materials (Codex shaded the back leg darker: 「左腿变色」), Codex's legs pushed down to the
# idle's hips with rows taken out of the shins
LEG_REMAP = {"u": "j", "q": "h", "r": "j", "l": "o"}
TROUSERS = set("ozw")
# the run's arms: Codex's broke into pieces over the body (the review: "arm fragments"), lines of the idle's arm
# colours swung as pendulums read as strange (「瑞兹走路时手还是有点不自然」), and League's run joints laid on the screen
# as League's camera sees them threw the far arm out level from the shoulder (「你觉得对吗 我的天 都变形了」). So the
# idle's own two arms, square for square (tools/art/rig_ryze.py's parts: the upper arm, the forearm with the bracer and
# the hand), turned a little (RotSprite): the upper arm about the shoulder, the forearm about the elbow a little more
# forward; {frame: {side: (upper arm degrees, forearm's more)}}, + forward. The rhythm is League's Ryze_Run_Fast (a
# frame later: Codex's legs run a frame behind it) - the near arm forward with the far leg (frames 6-8, 1), back with
# the near leg (2-4) - the far arm the other way; the near arm over the body, the far one behind it
RUN_POSE = {
    1: {"front": (8, 12), "back": (-8, 4)},
    2: {"front": (-3, 6), "back": (4, 10)},
    3: {"front": (-8, 4), "back": (8, 14)},
    4: {"front": (-10, 4), "back": (10, 16)},
    5: {"front": (-3, 8), "back": (4, 10)},
    6: {"front": (6, 12), "back": (-6, 4)},
    7: {"front": (10, 14), "back": (-10, 4)},
    8: {"front": (10, 14), "back": (-10, 4)},
}
# the boots of the legs swinging through in the run's passing frames (run_legs took rows out of the shins: the leg
# ended at the knee band); {row from the pivot: (first column, squares)} in the idle's boot materials
FEET = {("run", 2): {7: (0, "Dxx"), 8: (0, "rjhh")}, ("run", 6): {6: (-1, "Dxx"), 7: (-1, "rjhh")}}
# the frames whose arm (side) is the idle's own: Codex folded the far arm into a lump at the hip while the near one
# shoots (attack 3-4: "a black blob"; a flat bar across the chest in 1, an L by the scroll in 2, 5 and Q 3, 5), and its
# arms hung short of the idle's in the recoveries (attack 6, Q 1, 5 and 6)
# (the same where Codex left the far arm folded into an L at the shoulder, its fist hanging by the scroll, while the
# near one acts: the combo 7-8 and 11, the hit's recoil, the landing; and the combo's last frame, back to the idle)
IDLE_ARMS = {("attack", 1): ("back",), ("attack", 2): ("back",), ("attack", 3): ("back",), ("attack", 4): ("back",),
             ("attack", 5): ("back",), ("attack", 6): ("back", "front"),
             ("skill", 1): ("back", "front"), ("skill", 3): ("back",), ("skill", 4): ("back",),
             ("skill", 5): ("back", "front"),
             ("skill", 6): ("back", "front"),
             ("skill2", 2): ("back",), ("skill2", 6): ("back",), ("skill2", 7): ("back",), ("skill2", 8): ("back",),
             ("skill2", 9): ("back",), ("skill2", 10): ("back",), ("skill2", 11): ("back",),
             ("skill2", 12): ("back", "front"), ("hit", 1): ("back", "front"), ("hit", 2): ("back", "front"),
             ("dead", 1): ("back", "front"), ("dead", 2): ("back", "front"), ("ult_land", 2): ("back",),
             ("ult_land", 3): ("back", "front")}
CRUMB = 12                                       # pieces of fewer squares apart from the figure go
# R's channel stands (Codex knelt in 2-4 and landed in that kneel: 「瑞兹放大时候别跪下来啊」): its first frame, both
# arms spread over the portal, held through 2-4 (the user left A / B to me: 「你选一个吧」 - B); the landing comes out of
# the channel's last frame, both arms up
REUSE = {("ult", 2): ("ult", 1), ("ult", 3): ("ult", 1), ("ult", 4): ("ult", 1), ("ult_land", 1): ("ult", 8)}
SHIFT_X = {}
BRACER = 4                                       # squares from an arm's skin its bracer reaches (5 long in Codex's)
RAISED = -17                                     # rows over the shoulder pads (from the pivot, before the head's move)
# the frames whose far arm is raised across the scroll on his back (or thrown back over the shoulder pad in the hit):
# Codex's squares over the shoulder pads that are not the design's there are that arm's (else its fist floats over
# the scroll), and it lies in front of the scroll
OVER_SCROLL = {("skill", 1), ("skill", 2), ("skill2", 4), ("skill2", 5), ("ult", 5), ("ult", 6), ("hit", 1)}
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def lp(p):
    return G.lp(p)


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def cells_of(path, n, cell):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    cols, _ = layout(n)
    cw, ch = cell
    return [a[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw].copy() for k in range(n)]


def sheet_of(frames, cell):
    cols, rows = layout(len(frames))
    cw, ch = cell
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k, f in enumerate(frames):
        out[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw] = f
    return np.repeat(np.repeat(out, Z, 0), Z, 1)


def design():
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    return {(int(x) - PIVOT[0], int(y) - PIVOT[1]): d[y, x].copy() for y, x in zip(*np.nonzero(d[..., 3]))}


def find_head(frame, pivot, head):
    best = (0, 0, 0)
    for dy in range(-16, 12):
        for dx in range(-14, 14):
            s = 0
            for (x, y), c in head.items():
                yy, xx = pivot[1] + y + dy, pivot[0] + x + dx
                if 0 <= yy < frame.shape[0] and 0 <= xx < frame.shape[1] and (frame[yy, xx] == c).all():
                    s += 1
            if s > best[0]:
                best = (s, dx, dy)
    return best[1], best[2], best[0] / len(head)


def pockets(a, feet):
    b = G.complete_outline(a, color=INK, feet=feet)[0]
    op = b[..., 3] > 0
    h, w = op.shape
    seen = np.zeros(op.shape, bool)
    out = []
    for y0, x0 in zip(*np.nonzero(~op)):
        if seen[y0, x0]:
            continue
        comp, q, edge = [], deque([(y0, x0)]), False
        seen[y0, x0] = True
        while q:
            y, x = q.popleft()
            comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if not (0 <= yy < h and 0 <= xx < w):
                    edge = True
                elif not op[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    q.append((yy, xx))
        if not edge:
            out.append(comp)
    return out, b


def wall_colour(b, comp):
    walls = Counter()
    inside = set(comp)
    for y, x in comp:
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (y + dy, x + dx)
            if q in inside:
                continue
            c = b[q]
            if c[3] and tuple(int(v) for v in c[:3]) != INK:
                walls[tuple(int(v) for v in c)] += 1
    return np.array(walls.most_common(1)[0][0], np.uint8) if walls else np.array(INK + (255,), np.uint8)


def raw_holes(a):
    """Clear squares walled in by the frame as drawn (before any outline is closed): lists of (y, x)."""
    op = a[..., 3] > 0
    h, w = op.shape
    seen = np.zeros(op.shape, bool)
    out = []
    for y0, x0 in zip(*np.nonzero(~op)):
        if seen[y0, x0]:
            continue
        comp, q, edge = [], deque([(y0, x0)]), False
        seen[y0, x0] = True
        while q:
            y, x = q.popleft()
            comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if not (0 <= yy < h and 0 <= xx < w):
                    edge = True
                elif not op[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    q.append((yy, xx))
        if not edge:
            out.append(comp)
    return out


def mend(frame, pivot, des, head, body_lean=None):
    a = frame.copy()
    px, py = pivot
    # the waist's gap first, as drawn: closed by the importer it would turn into a dark line across the belt
    for comp in raw_holes(a):
        if all(WAIST[0] <= y - py <= WAIST[1] for y, _ in comp):
            for (y, x) in comp:
                c = des.get((x - px, y - py))
                if c is not None and tuple(int(v) for v in c[:3]) != INK:
                    a[y, x] = c
    dx, dy, share = find_head(a, pivot, head)
    found = share > 0.9
    placed = {(x + dx, y + dy) for (x, y) in head} if found else set()
    comps, closed = pockets(a, py + 11)
    fixed = Counter()
    for comp in comps:
        ys = [y - py for y, _ in comp]
        xs = [x - px for _, x in comp]
        by_head = found and any(abs(x - hx) <= 2 and abs(y - hy) <= 2 for y, x in zip(ys, xs) for (hx, hy) in placed)
        at_waist = all(WAIST[0] <= y <= WAIST[1] for y in ys)
        if by_head or at_waist:
            ox, oy = (dx, dy) if by_head else (0, 0)
            for (y, x) in comp:
                c = des.get((x - px - ox, y - py - oy))
                a[y, x] = c if c is not None and tuple(int(v) for v in c[:3]) != INK else wall_colour(closed, comp)
            fixed["head" if by_head else "waist"] += len(comp)
        elif body_lean is not None and len(comp) <= BODY_POCKET:
            # the idle's body leaning body_lean squares a row: the design's own square at the place
            for (y, x) in comp:
                c = des.get((x - px - R.lean_x(body_lean, y - py), y - py))
                a[y, x] = c if c is not None and tuple(int(v) for v in c[:3]) != INK else wall_colour(closed, comp)
            fixed["body"] += len(comp)
        elif len(comp) <= POCKET or (len(comp) <= SLIT[0] and max(Counter(y for y, _ in comp).values()) <= SLIT[1]):
            col = wall_colour(closed, comp)
            for (y, x) in comp:
                a[y, x] = col
            fixed["pocket"] += len(comp)
        else:
            fixed["left"] += len(comp)
    return a, (dx, dy, share), fixed


def grow(m):
    g = m.copy()
    g[1:] |= m[:-1]
    g[:-1] |= m[1:]
    g[:, 1:] |= m[:, :-1]
    g[:, :-1] |= m[:, 1:]
    g[1:, 1:] |= m[:-1, :-1]
    g[1:, :-1] |= m[:-1, 1:]
    g[:-1, 1:] |= m[1:, :-1]
    g[:-1, :-1] |= m[1:, 1:]
    return g


def pieces(mask):
    """The 8-connected pieces of a mask: lists of (y, x)."""
    h, w = mask.shape
    seen = np.zeros(mask.shape, bool)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        comp, q = [], deque([(y0, x0)])
        seen[y0, x0] = True
        while q:
            y, x = q.popleft()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        q.append((yy, xx))
        out.append(comp)
    return out


def thin(pix, keep=(), inner=None):
    """An arm (x, y) -> colour without its outline, thinned: the squares at depth 1 (next to the outside) go where a
    square within 2 of them lies THICK deep; the squares left on the new edge take the colour of the one taken off
    beside them (the lit edge, the dark edge); keep: squares never taken off; inner: Codex's dark lines inside the arm
    (a crease, the fist's knuckles) (x, y) -> colour - part of the arm's body for the depths, kept where they lie
    deep."""
    pix = dict(pix)
    pix.update(inner or {})
    P = set(pix)
    d, q = {}, deque()
    for p in P:
        if any((p[0] + ox, p[1] + oy) not in P for ox, oy in N4):
            d[p] = 1
            q.append(p)
    while q:
        p = q.popleft()
        for ox, oy in N4:
            n = (p[0] + ox, p[1] + oy)
            if n in P and n not in d:
                d[n] = d[p] + 1
                q.append(n)
    gone = {p for p, v in d.items() if v == 1 and p not in keep
            and max(d.get((p[0] + ox, p[1] + oy), 0) for ox in range(-2, 3) for oy in range(-2, 3)) >= THICK}
    out = {p: c for p, c in pix.items() if p not in gone}
    for p in list(out):
        for ox, oy in N4:
            n = (p[0] + ox, p[1] + oy)
            if n in gone:
                out[p] = pix[n]
                break
    return out, len(gone)


def trim_hand(arm, shoulder, body_x):
    """The hand at the arm's far end (the skin squares within 3 steps of the farthest one from the shoulder) cut to
    the idle's three squares where Codex drew it four or more both ways: the end row and the end column it points
    to (sideways: the outer one) go, their colours moved one square in. arm (x, y) -> colour; returns the new arm."""
    a0 = min(arm, key=lambda p: (p[0] - shoulder[0]) ** 2 + (p[1] - shoulder[1]) ** 2)
    dist, q = {a0: 0}, deque([a0])
    while q:
        p = q.popleft()
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                n = (p[0] + ox, p[1] + oy)
                if n in arm and n not in dist:
                    dist[n] = dist[p] + 1
                    q.append(n)
    far = max(dist.values())
    hand = [p for p, v in dist.items() if v >= far - 3 and tuple(int(c) for c in arm[p][:3]) in SKIN]
    wrist = [p for p, v in dist.items() if far - 6 <= v <= far - 4]
    if len(hand) < 9 or not wrist:
        return arm
    xs, ys = [x for x, _ in hand], [y for _, y in hand]
    if max(xs) - min(xs) < 3 or max(ys) - min(ys) < 3:
        return arm
    cx, cy = np.mean(xs), np.mean(ys)
    ux, uy = cx - np.mean([x for x, _ in wrist]), cy - np.mean([y for _, y in wrist])
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux / n, uy / n
    sx = (1 if ux > 0 else -1) if abs(ux) >= 0.3 else (1 if cx > body_x else -1)
    sy = (1 if uy > 0 else -1) if abs(uy) >= 0.3 else 0
    hs = set(hand)
    gone = {p for p in hs if p[0] == (max(xs) if sx > 0 else min(xs))}
    if sy:
        gone |= {p for p in hs if p[1] == (max(ys) if sy > 0 else min(ys))}
    out = {p: c for p, c in arm.items() if p not in gone}
    for p in list(out):
        if p not in hs:
            continue
        for ox, oy in N4:
            m = (p[0] + ox, p[1] + oy)
            if m in gone:
                out[p] = arm[m]
                break
    return out


def finger(pix, side, dx, dy):
    """The arm's last 3 steps from the square nearest its shoulder (a pointing finger)."""
    sh = SHOULDER[side]
    a0 = min(pix, key=lambda p: (p[0] - sh[0] - dx) ** 2 + (p[1] - sh[1] - dy) ** 2)
    dist, q = {a0: 0}, deque([a0])
    while q:
        p = q.popleft()
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                n = (p[0] + ox, p[1] + oy)
                if n in pix and n not in dist:
                    dist[n] = dist[p] + 1
                    q.append(n)
    far = max(dist.values())
    return {p for p, v in dist.items() if v >= far - 2}


def arm_mask(a, pivot, hd, P, over_scroll=False, legs=None, upper=None):
    """Codex's arms in a standing frame: the squares (mask) and the frame's skin and outline squares; legs / upper:
    the body's legs and upper body when not the idle's (OWN_LEGS: Codex's legs, the upper body to the belt)."""
    px, py = pivot
    dx, dy = hd
    h, w = a.shape[:2]
    # Codex's body where its head stands: what lies outside it (or is skin over its clothes) is an arm
    body = {}
    if legs is None:
        for side in ("back", "front"):
            body.update(P["legs"][side])
    else:
        body.update(legs)
    for (x, y), c in (upper if upper is not None else P["upper"]).items():
        body[(x + dx, y + dy)] = c
    inside = np.zeros((h, w), bool)
    bskin = np.zeros((h, w), bool)
    other = np.zeros((h, w), bool)                  # over the shoulder pads: not the design's square there
    for (x, y), c in body.items():
        inside[py + y, px + x] = True
        bskin[py + y, px + x] = tuple(int(v) for v in c[:3]) in SKIN
        other[py + y, px + x] = over_scroll and y - dy <= RAISED and not (a[py + y, px + x] == c).all()
    col = [[tuple(int(v) for v in a[y, x, :3]) for x in range(w)] for y in range(h)]
    skin = np.array([[c in SKIN for c in row] for row in col])
    dark = np.array([[c in DARK for c in row] for row in col])
    armc = np.array([[c in ARM_COLOURS for c in row] for row in col])
    # his body shows no skin under the head: every skin square there is an arm's (a hand, a bare upper arm), wherever
    # it lies; the bracers' leathers and golds are an arm's within BRACER squares of that skin, unless they lie in the
    # design's own torso (its shirt, strap and belt) or the legs
    headsq = np.zeros((h, w), bool)
    for (x, y), c in P["upper"].items():
        if y <= HEAD[3] and tuple(int(v) for v in c[:3]) in SKIN:
            headsq[py + y + dy, px + x + dx] = True
    headsq = grow(grow(headsq))
    core = np.zeros((h, w), bool)
    for (x, y) in body:
        core[py + y, px + x] = True
    arm = (a[..., 3] > 0) & skin & ~headsq & (~core | ~bskin)
    reach = arm.copy()
    for _ in range(BRACER):
        reach = grow(reach)
    arm |= (a[..., 3] > 0) & armc & ~skin & reach & (~core | other) & ~headsq
    arm |= (a[..., 3] > 0) & armc & ~grow(inside) & reach
    infront = (a[..., 3] > 0) & skin & core & ~bskin           # skin over his clothes: an arm in front of the body
    return arm, skin, dark, infront


# the arms drawn again along Codex's own (the user: 「手臂待机和释放技能时尺寸还是不一样」; the internal review found
# Codex's arms thinned in place came out as sticks, oversized fists and black smears): the arm's middle line (its
# skeleton, from the shoulder to the farthest tip) carries a band three squares wide in the idle's arm materials, lit
# on the upper / outer side - the bare upper arm, the bracer (where Codex drew it: its leathers and golds along the
# line), the hand the last squares
ARM_MAT = {"upper": ("f", "e", "i"), "band": ("x", "x", "q"), "bracer": ("h", "j", "j"), "hand": ("f", "e", "i"),
           "tip": ("e", "d", "g")}
BRACER_COLOURS = {tuple(int(R.PAL[k][i:i + 2], 16) for i in (0, 2, 4)) for k in "hjqxyuD"}
HAND_LEN = 3                                     # the hand's squares at the end of the line (the idle's: 3 rows)
BRACER_LEN = 4                                   # the bracer's squares at least (the idle's: 4 rows)


def skeleton(cells):
    """Zhang-Suen thinning of a set of squares: the middle line's squares."""
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    x0, y0 = min(xs) - 1, min(ys) - 1
    m = np.zeros((max(ys) - y0 + 2, max(xs) - x0 + 2), bool)
    for (x, y) in cells:
        m[y - y0, x - x0] = True
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            drop = []
            for y, x in zip(*np.nonzero(m)):
                if y == 0 or x == 0 or y == m.shape[0] - 1 or x == m.shape[1] - 1:
                    continue
                n = [m[y - 1, x], m[y - 1, x + 1], m[y, x + 1], m[y + 1, x + 1], m[y + 1, x], m[y + 1, x - 1],
                     m[y, x - 1], m[y - 1, x - 1]]
                b = sum(n)
                a_ = sum((not n[i]) and n[(i + 1) % 8] for i in range(8))
                if not (2 <= b <= 6 and a_ == 1):
                    continue
                if step == 0 and not (n[0] and n[2] and n[4]) and not (n[2] and n[4] and n[6]):
                    drop.append((y, x))
                if step == 1 and not (n[0] and n[2] and n[6]) and not (n[0] and n[4] and n[6]):
                    drop.append((y, x))
            for y, x in drop:
                m[y, x] = False
            changed = changed or bool(drop)
    return {(int(x) + x0, int(y) + y0) for y, x in zip(*np.nonzero(m))}


def arm_line(cells, anchor):
    """The arm's middle line from the square nearest the shoulder anchor to the farthest end: (x, y) in order."""
    sk = skeleton(cells) or set(cells)
    # the skeleton of an arm Codex's outline cut in pieces is in pieces too: the nearest pieces (8 squares or less
    # apart) joined by straight steps
    while True:
        parts_ = []
        left = set(sk)
        while left:
            s0 = left.pop()
            comp, q = {s0}, deque([s0])
            while q:
                p = q.popleft()
                for ox in (-1, 0, 1):
                    for oy in (-1, 0, 1):
                        nb = (p[0] + ox, p[1] + oy)
                        if nb in left:
                            left.discard(nb)
                            comp.add(nb)
                            q.append(nb)
            parts_.append(comp)
        if len(parts_) < 2:
            break
        best = None
        for i in range(len(parts_)):
            for j in range(i + 1, len(parts_)):
                for pa in parts_[i]:
                    for pb in parts_[j]:
                        dd = max(abs(pa[0] - pb[0]), abs(pa[1] - pb[1]))
                        if best is None or dd < best[0]:
                            best = (dd, pa, pb)
        if best is None or best[0] > 8:
            break
        _, pa, pb = best
        steps = best[0]
        for k in range(1, steps):
            sk.add((int(round(pa[0] + (pb[0] - pa[0]) * k / steps)), int(round(pa[1] + (pb[1] - pa[1]) * k / steps))))
    start = min(sk, key=lambda p: (p[0] - anchor[0]) ** 2 + (p[1] - anchor[1]) ** 2)
    par, dist, q = {start: None}, {start: 0}, deque([start])
    while q:
        p = q.popleft()
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                n = (p[0] + ox, p[1] + oy)
                if n in sk and n not in par:
                    par[n], dist[n] = p, dist[p] + 1
                    q.append(n)
    end = max(dist, key=dist.get)
    line = []
    while end is not None:
        line.append(end)
        end = par[end]
    line.reverse()
    # a piece away from the shoulder (the upper arm hidden by the body, a fist out on its own) hangs from it: the
    # line starts at the shoulder
    ax, ay = int(round(anchor[0])), int(round(anchor[1]))
    lead = []
    x, y = ax, ay
    while max(abs(line[0][0] - x), abs(line[0][1] - y)) > 1:
        lead.append((x, y))
        x += int(np.sign(line[0][0] - x)) if abs(line[0][0] - x) >= abs(line[0][1] - y) / 2 else 0
        y += int(np.sign(line[0][1] - y)) if abs(line[0][1] - y) >= abs(line[0][0] - x) / 2 else 0
    line = lead + line
    # carried on along its last direction while still on the arm (the skeleton stops a square inside the tip)
    if len(line) >= 3:
        sx, sy = int(np.sign(line[-1][0] - line[-3][0])), int(np.sign(line[-1][1] - line[-3][1]))
        for _ in range(2):
            q = (line[-1][0] + sx, line[-1][1] + sy)
            if q not in cells:
                break
            line.append(q)
    return line


def draw_arm(line, colours, side, finger=False, mats=None, bracer=None, skin=None, rgba=None):
    """The arm along its line, three squares wide: (x, y) -> rgba. colours: Codex's squares of the arm (to find the
    bracer on the line); mats / bracer / skin / rgba: another hero's materials, bracer and skin colours, codes."""
    mats = mats or ARM_MAT
    bracer = bracer or BRACER_COLOURS
    skin = skin or SKIN
    rgba = rgba or R.rgba
    n = len(line)
    if n < 2:
        return {}
    kinds = []
    for (x, y) in line:
        br = sk = 0
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                c = colours.get((x + ox, y + oy))
                if c is None:
                    continue
                c = tuple(int(v) for v in c[:3])
                br += c in bracer
                sk += c in skin
        kinds.append("bracer" if br > sk else "skin")
    # the parts in order: the upper arm, the bracer (Codex's longest run of it), the hand (the last HAND_LEN)
    hand0 = max(2, n - HAND_LEN)
    runs, cur = [], None
    for i, k in enumerate(kinds[:hand0]):
        if k == "bracer":
            cur = [i, i] if cur is None else [cur[0], i]
        elif cur is not None:
            runs.append(cur)
            cur = None
    if cur is not None:
        runs.append(cur)
    if runs:
        b0, b1 = max(runs, key=lambda r: r[1] - r[0])
        b0 = max(b0, 1)
        b1 = hand0 - 1 if hand0 - 1 - b1 <= 2 else b1
    else:
        b0, b1 = max(1, int(n * 0.5)), hand0 - 1
    if b1 - b0 < BRACER_LEN - 1:                 # the idle's bracer: four rows before the hand
        b1 = hand0 - 1
        b0 = max(1, b1 - BRACER_LEN + 1)
    part = []
    for i in range(n):
        if i >= hand0:
            part.append("tip" if i == n - 1 else "hand")
        elif b0 <= i <= b1:
            part.append("band" if i in (b0, b1) else "bracer")
        else:
            part.append("upper")
    out = {}
    out_x = -1 if side == "back" else 1
    for i, (x, y) in enumerate(line):
        a = line[max(0, i - 2)]
        b = line[min(n - 1, i + 2)]
        vx, vy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / ln, vx / ln
        if abs(ny) >= 0.35:
            if ny > 0:
                nx, ny = -nx, -ny                    # the lit side up
        elif nx * out_x < 0:
            nx, ny = -nx, -ny                        # a hanging arm: lit on its outer side
        lit, mid, dark = (rgba(ch) for ch in mats[part[i]])
        out[(int(round(x - nx)), int(round(y - ny)))] = dark
        out[(int(round(x + nx)), int(round(y + ny)))] = lit
        out[(x, y)] = mid
    # one-square gaps left between the bands of a turning line: the commonest colour round them
    for _ in range(2):
        for (x, y) in list(out):
            for ox, oy in N4:
                q = (x + ox, y + oy)
                if q in out:
                    continue
                round_ = [out[(q[0] + ex, q[1] + ey)] for ex, ey in N4 if (q[0] + ex, q[1] + ey) in out]
                if len(round_) >= 3:
                    out[q] = round_[0]
    if finger:                                   # the pointing finger: two squares on from the tip
        (ax, ay), (bx, by) = line[max(0, n - 3)], line[-1]
        ln = math.hypot(bx - ax, by - ay) or 1.0
        for k in (1, 2):
            out[(int(round(bx + (bx - ax) / ln * k)), int(round(by + (by - ay) / ln * k)))] = rgba("e")
    return out


# the body under the hanging arms: the idle's torso is nine squares between its arms, its hips eleven - with the arms
# moved the narrow waist sat on the wide trousers and the legs read as stuck on (「瑞兹这腿和身体感觉是分割的」, the
# review's main finding). In the standing frames the torso's rows are drawn out to the hips' width (SIDE_X), each
# row's edge colour carried outward (the back edge a shade darker), the belt with them
SIDE_ROWS = range(-13, -3)
SIDE_X = (-5, 5)
SHADE = {"o": "l", "z": "l", "w": "o", "h": "j", "j": "u", "x": "h", "y": "x", "r": "u", "u": "r", "q": "u"}


def unspur(cells):
    """Outline squares a turn left outlining nothing (fingertip spurs) go."""
    for _ in range(2):
        for (x, y) in [q for q, c in cells.items() if tuple(int(v) for v in c[:3]) in DARK]:
            if not any((x + ox, y + oy) in cells and tuple(int(v) for v in cells[(x + ox, y + oy)][:3]) not in DARK
                       for ox in (-1, 0, 1) for oy in (-1, 0, 1) if ox or oy):
                del cells[(x, y)]
    return cells


def pose_arm(P, side, S, H, near_elbow):
    """The idle's own arm (rig_ryze's parts: the upper arm, the forearm with the bracer and the hand) turned so its
    shoulder is on S and the hand's middle on H (out of reach: as far as the arm goes), the elbow bent the way that
    lies nearer near_elbow (Codex's): RotSprite of each part about its joint."""
    sp = R.ARMS[side]
    S0, E0, H0 = sp["S"], sp["E"], sp["H"]
    lu = math.hypot(E0[0] - S0[0], E0[1] - S0[1])
    lf = math.hypot(H0[0] - E0[0], H0[1] - E0[1])
    dx, dy = H[0] - S[0], H[1] - S[1]
    reach = math.hypot(dx, dy) or 1e-9
    if reach > lu + lf - 0.05:
        k = (lu + lf - 0.05) / reach
        H = (S[0] + dx * k, S[1] + dy * k)
    e = min((R.knee(S, H, lu, lf, forward=f) for f in (1, -1)),
            key=lambda q: (q[0] - near_elbow[0]) ** 2 + (q[1] - near_elbow[1]) ** 2)
    d1 = R.angle((E0[0] - S0[0], E0[1] - S0[1])) - R.angle((e[0] - S[0], e[1] - S[1]))
    d2 = R.angle((H0[0] - E0[0], H0[1] - E0[1])) - R.angle((H[0] - e[0], H[1] - e[1]))
    cells = {}
    for (x, y), c in R.turn_cells(P["arms"][(side, "upper")], S0, d1).items():
        cells[(math.floor(S[0] + x + 0.5), math.floor(S[1] + y + 0.5))] = c
    for (x, y), c in R.turn_cells(P["arms"][(side, "fore")], E0, d2).items():
        cells[(math.floor(e[0] + x + 0.5), math.floor(e[1] + y + 0.5))] = c
    return unspur(cells)


def run_arms(k, P):
    """Run frame k (0-based): {side: squares} - the idle's arm turned as RUN_POSE says."""
    out = {}
    for side, (up, more) in RUN_POSE[k + 1].items():
        sp = R.ARMS[side]
        S0, E0 = sp["S"], sp["E"]
        th = math.radians(up)                    # + counter-clockwise on screen (y down): forward from hanging
        vx, vy = E0[0] - S0[0], E0[1] - S0[1]
        ex, ey = S0[0] + vx * math.cos(th) + vy * math.sin(th), S0[1] - vx * math.sin(th) + vy * math.cos(th)
        cells = {}
        for (x, y), c in R.turn_cells(P["arms"][(side, "upper")], S0, up).items():
            cells[(math.floor(S0[0] + x + 0.5), math.floor(S0[1] + y + 0.5))] = c     # (round() halves to even)
        for (x, y), c in R.turn_cells(P["arms"][(side, "fore")], E0, up + more).items():
            cells[(math.floor(ex + x + 0.5), math.floor(ey + y + 0.5))] = c
        for _ in range(2):                       # outline squares the turn left outlining nothing (fingertip spurs)
            for (x, y) in [q for q, c in cells.items() if tuple(int(v) for v in c[:3]) in DARK]:
                if not any((x + ox, y + oy) in cells and tuple(int(v) for v in cells[(x + ox, y + oy)][:3]) not in DARK
                           for ox in (-1, 0, 1) for oy in (-1, 0, 1) if ox or oy):
                    del cells[(x, y)]
        out[side] = cells
    return out


def torso_sides(upper):
    out = {}
    for y in SIDE_ROWS:
        xs = sorted(x for (x, yy), c in upper.items() if yy == y and tuple(int(v) for v in c[:3]) not in DARK)
        if not xs:
            continue
        cl, cr = R.code(upper[(xs[0], y)]), R.code(upper[(xs[-1], y)])
        for x in range(SIDE_X[0], xs[0]):
            out[(x, y)] = R.rgba(SHADE.get(cl, cl) if x == SIDE_X[0] else cl)
        for x in range(xs[-1] + 1, SIDE_X[1] + 1):
            out[(x, y)] = R.rgba(cr)
    out[(SIDE_X[1], -4)] = R.rgba("o")           # the trousers' top under the widened waist
    return out


def eye_offset(a, pivot):
    """The pasted head's move by its near eye's white (2 x 2; the design's top-left one at EYE_AT)."""
    px, py = pivot
    ys, xs = np.nonzero((a[..., :3] == (0xFB, 0xFB, 0xFD)).all(-1) & (a[..., 3] > 0))
    pts = sorted(zip((xs - px).tolist(), (ys - py).tolist()), key=lambda p: (p[1], p[0]))
    return (pts[0][0] - EYE_AT[0], pts[0][1] - EYE_AT[1]) if pts else (0, 0)


def flap_top(a, pivot):
    """The teal flap's top row in Codex's frame (from the pivot), within 4 columns of the pivot."""
    px, py = pivot
    teal = {tuple(int(R.PAL[k][i:i + 2], 16) for i in (0, 2, 4)) for k in "ABC"}
    rows = [y - py for y in range(a.shape[0]) for x in range(px - 4, px + 5)
            if a[y, x, 3] and tuple(int(v) for v in a[y, x, :3]) in teal]
    return min(rows) if rows else FLAP_TOP


def ring_close(a, py):
    """One outline square on every open edge (4-neighbours) of the figure, over the soles' row nothing."""
    h, w = a.shape[:2]
    op = a[..., 3] > 0
    darkm = np.zeros((h, w), bool)
    for y, x in zip(*np.nonzero(op)):
        darkm[y, x] = tuple(int(v) for v in a[y, x, :3]) in DARK
    lit = op & ~darkm
    need = np.zeros((h, w), bool)
    need[1:] |= lit[:-1]
    need[:-1] |= lit[1:]
    need[:, 1:] |= lit[:, :-1]
    need[:, :-1] |= lit[:, 1:]
    need &= ~op
    need[py + 12:] = False
    a[need] = INK + (255,)
    return int(need.sum())


def run_legs(a, pivot, codex_flap, dy):
    """The run's legs: Codex's from under its belt, pushed down to the idle's hips (rows taken out of the shins),
    in the idle's leg materials, the trousers lit on their back edge as the idle's."""
    px, py = pivot
    h, w = a.shape[:2]
    top = codex_flap + 1                         # Codex's legs start under its flap's top row
    want = BELT_ROW + 1 + dy
    rows = {}
    for y in range(top, 12):
        rows[y] = {x - px: a[py + y, x].copy() for x in range(w) if a[py + y, x, 3]}
    d = max(0, want - top)
    if d:
        cand = list(range(top + 6, 9))
        cost = {r: sum(1 for x in set(rows[r]) | set(rows.get(r + 1, {}))
                       if (x in rows[r]) != (x in rows.get(r + 1, {})) or (x in rows[r] and tuple(rows[r][x][:3])
                                                                            != tuple(rows[r + 1][x][:3])))
                for r in cand}
        gone = []
        for r in sorted(cost, key=lambda r: (cost[r], r)):
            if len(gone) < d and all(abs(r - q) > 1 for q in gone):
                gone.append(r)
        keep = [y for y in sorted(rows) if y not in gone]
        new = {}
        for i, y in enumerate(keep):
            new[11 - (len(keep) - 1 - i)] = rows[y]
        rows = new
    out = {}
    for y, row in rows.items():
        if y < want:
            continue
        for x, c in row.items():
            ch = R.code(c)
            if ch in LEG_REMAP:
                c = R.rgba(LEG_REMAP[ch])
            out[(x, y)] = c
    for y in {yy for _, yy in out}:              # the trousers' lit back edge
        for x in sorted(x for x, yy in out if yy == y):
            if R.code(out[(x, y)]) in TROUSERS and R.code(out.get((x - 1, y), np.zeros(4, np.uint8))) in ("a", "?") \
                    and R.code(out.get((x + 1, y), np.zeros(4, np.uint8))) in TROUSERS:
                out[(x, y)] = R.rgba("w")
    return out


def own_legs(a, pivot, dy):
    """Codex's own legs (the run's strides, R's kneel) under the idle's belt dropped dy rows: its squares from the row
    under the belt down, not skin nor a bracer's leather within 2 squares of skin (a hand on the ground)."""
    px, py = pivot
    h, w = a.shape[:2]
    col = [[tuple(int(v) for v in a[y, x, :3]) for x in range(w)] for y in range(h)]
    skin = np.array([[c in SKIN for c in row] for row in col])
    near = grow(grow(skin))
    out = {}
    for y in range(py + BELT_ROW + 1 + dy, h):
        for x in range(w):
            if a[y, x, 3] and not skin[y, x] and not (near[y, x] and col[y][x] in BRACER_COLOURS):
                out[(x - px, y - py)] = a[y, x].copy()
    for _ in range(3):                           # outline with nothing left to outline (round a hand that went)
        for (x, y) in list(out):
            if tuple(int(v) for v in out[(x, y)][:3]) in DARK and not any(
                    (x + ox, y + oy) in out and tuple(int(v) for v in out[(x + ox, y + oy)][:3]) not in DARK
                    for ox in (-1, 0, 1) for oy in (-1, 0, 1) if ox or oy):
                del out[(x, y)]
    return out


def cut_rows(full, n):
    """n rows of the torso (CUT_ROWS, never two neighbours) whose loss changes it least: the most like the row
    under them."""
    xs = [x for x, _ in full]
    cost = {}
    for r in CUT_ROWS:
        c = 0
        for x in range(min(xs), max(xs) + 1):
            a_, b_ = full.get((x, r)), full.get((x, r + 1))
            if (a_ is None) != (b_ is None) or (a_ is not None and tuple(a_[:3]) != tuple(b_[:3])):
                c += 1
        cost[r] = c
    out = []
    for r in sorted(cost, key=lambda r: (cost[r], r)):
        if len(out) < n and all(abs(r - q) > 1 for q in out):
            out.append(r)
    return sorted(out)


def idle_body(a, pivot, hd, P, tag, point=(), over_scroll=False, legs_own=False, crouch_hip=None, swing=None,
              idle_arms=()):
    """A standing frame on the idle's own upper body with Codex's arms drawn again (the module's docstring); legs_own:
    the idle's upper body down to its belt, dropped to Codex's head, over Codex's own legs (OWN_LEGS); crouch_hip: in a
    crouch (CROUCH) the belt drops to Codex's hips instead, the torso losing up to MAX_CUT rows to reach Codex's head
    (the head higher than Codex's by what is left), Codex's arms kept where they reach (the hands on the ground)."""
    px, py = pivot
    dx, dy = hd
    h, w = a.shape[:2]
    most = LEAN_MAX.get(tag, 0)                  # (the casts: no lean - the sheared torso stepped a square at the
                                                 # hips: 「释放技能时身体有点变形」)
    lean = max(-most, min(most, dx)) / (R.HIP_Y - R.NECK_Y)

    def lx(y):                                   # the lean's shift of row y: none under the hips (the flap stays)
        return R.lean_x(lean, y) if y < R.HIP_Y else 0
    legs = upper = placed = None
    drop = 0
    if legs_own:
        lean = 0.0
        hip = dy if crouch_hip is None else crouch_hip
        cut = min(MAX_CUT, max(0, dy - hip))
        drop = hip + cut                         # the head's drop
        legs = own_legs(a, pivot, hip) if crouch_hip is not None else run_legs(a, pivot, flap_top(a, pivot), dy)
        full = {xy: c for xy, c in P["upper"].items() if xy[1] <= BELT_ROW}
        full.update({xy: c for xy, c in torso_sides(P["upper"]).items() if xy[1] <= BELT_ROW and xy not in full})
        rows = cut_rows(full, cut)
        placed = {(x, y + drop - sum(r < y for r in rows)): c for (x, y), c in full.items() if y not in rows}
        upper = {(x - dx, y - dy): c for (x, y), c in placed.items()}
    keep = crouch_hip is not None
    arm, skin, dark, infront = arm_mask(a, pivot, hd, P, over_scroll, legs, upper)
    arms, thinned = {"back": {}, "over": {}, "front": {}}, 0
    # an arm is the pieces holding skin; Codex rings a fist or a bracer with its own outline, so the pieces next to
    # one of those (2 squares: across that outline) belong to it
    found = pieces(arm)
    groups = [set(c) for c in found if len(c) >= 6 and any(skin[y, x] for y, x in c)]
    rest = [set(c) for c in found if not (len(c) >= 6 and any(skin[y, x] for y, x in c))]
    grown = True
    while grown:
        grown = False
        for c in list(rest):
            for g in groups:
                if any(abs(y - yy) <= 2 and abs(x - xx) <= 2 for y, x in c for yy, xx in g):
                    g |= c
                    rest.remove(c)
                    grown = True
                    break
    # pieces of one arm split by Codex's own outline (a fist ringed apart from its forearm): one arm, one line
    def side_of(g):
        return "back" if np.mean([x - px for _, x in g]) < dx else "front"

    # (all the pieces on one side: the arm drawn again along its longest line, a stray stub of it not twice)
    by_side = {}
    for g in groups:
        by_side.setdefault(side_of(g), set()).update(g)
    groups = list(by_side.values())
    groups = [g for g in groups if side_of(g) not in idle_arms]
    if swing is not None:                        # the run: the idle's arms turned (run_arms), not Codex's
        groups = []
    posed = {"back": {}, "over": {}, "front": {}}

    def layer_of(side, comp):
        # a far arm brought across the front of the body (its skin over his clothes: a fist before the belly) lies
        # in front of it, as the near arm does
        bare = [p for p in comp if skin[p]]
        if side == "back" and (over_scroll or sum(infront[p] for p in bare) >= 0.3 * max(1, len(bare))):
            return "over"
        return side

    for comp in groups:
        pix = {(x - px, y - py): a[y, x].copy() for y, x in comp}
        # the dark squares walled in by the arm on 3 or 4 sides (twice: a 2-square crease)
        inner = {}
        for _ in range(2):
            for (x, y) in list(pix) + list(inner):
                for ox, oy in N4:
                    n_ = (x + ox, y + oy)
                    if n_ in pix or n_ in inner or not (0 <= py + n_[1] < h and 0 <= px + n_[0] < w):
                        continue
                    if not dark[py + n_[1], px + n_[0]]:
                        continue
                    walls = sum((n_[0] + ex, n_[1] + ey) in pix or (n_[0] + ex, n_[1] + ey) in inner for ex, ey in N4)
                    if walls >= 3:
                        inner[n_] = a[py + n_[1], px + n_[0]].copy()
        side = "back" if np.mean([x for x, _ in pix]) < dx else "front"
        sh = SHOULDER[side]
        cells = set(pix) | set(inner)
        mv = (ARM_IN[side] if side == "back" else -ARM_IN[side]) + R.lean_x(lean, -14) - int(round(0.7 * dx))
        # the line from the shoulder: Codex's (moved with its head) or, in a crouch, this body's own
        anchor = (sh[0] - mv, sh[1] + drop) if keep else (sh[0] + dx, sh[1] + dy)
        line = arm_line(cells, anchor)[:ARM_STEPS]
        # Codex's arm (its line moved onto this body) -> the idle's own arm turned to it (POSED): the shoulder on the
        # body's, the hand's middle 1.5 squares short of Codex's fingertips, the elbow on Codex's side
        to_body = (lambda q: (q[0] + mv, q[1] if keep else q[1] - dy + drop))
        S = (R.ARMS[side]["S"][0] + R.lean_x(lean, -14), R.ARMS[side]["S"][1] + drop)
        if len(line) >= 3:
            tip, before = to_body(line[-1]), to_body(line[max(0, len(line) - 3)])
            ln = math.hypot(tip[0] - before[0], tip[1] - before[1]) or 1.0
            H = (tip[0] - 1.5 * (tip[0] - before[0]) / ln, tip[1] - 1.5 * (tip[1] - before[1]) / ln)
            el = to_body(line[min(len(line) - 1, 7)])
            posed[layer_of(side, comp)].update(pose_arm(P, side, S, H, el))
            continue
        t = draw_arm(line, pix, side, side in point)
        thinned += len(cells) - len(t)
        # a far arm brought across the front of the body (its skin over his clothes: a fist before the belly) lies
        # in front of it, as the near arm does
        bare = [p for p in comp if skin[p]]
        layer = side
        if side == "back" and (over_scroll or sum(infront[p] for p in bare) >= 0.3 * max(1, len(bare))):
            layer = "over"
        for (x, y), c in t.items():
            arms[layer][(x + mv, y if keep else y - dy + drop)] = c
    out = np.zeros_like(a)
    # the head (with its own outline): no arm drawn over it, nor an arm's outline - a hand by the face stops at it
    face = {(py + y + drop, px + x + lx(y)) for (x, y), c in P["upper"].items()
            if y <= HEAD[3] and HEAD[0] - 1 <= x <= HEAD[1] + 1}

    def lay(cells, over_body, shoulder):
        m = np.zeros((h, w), bool)
        for (x, y) in cells:
            if 0 <= py + y < h and 0 <= px + x < w:
                m[py + y, px + x] = True
        sx, sy = shoulder[0] + R.lean_x(lean, -14), shoulder[1] + drop
        for (y, x) in face:
            if 0 <= y < h and 0 <= x < w:
                m[y, x] = False
        for y, x in zip(*np.nonzero(grow(m) & ~m)):
            # one outline round the arm; over the body only for the near arm, never at its shoulder nor on the face
            if out[y, x, 3] and (not over_body or (abs(x - px - sx) <= 2.5 and abs(y - py - sy) <= 3.5)
                                 or (y, x) in face):
                continue
            out[y, x] = INK + (255,)
        for (x, y), c in cells.items():
            if 0 <= py + y < h and 0 <= px + x < w and (py + y, px + x) not in face:
                out[py + y, px + x] = c

    # the far arm behind the body, unless raised across the scroll on his back (OVER_SCROLL) or brought before the
    # body: then in front of it
    lay(arms["back"], False, SHOULDER["back"])
    for (x, y), c in posed["back"].items():
        if 0 <= py + y < h and 0 <= px + x < w:
            out[py + y, px + x] = c
    if legs is None:
        for side in ("back", "front"):
            for (x, y), c in P["legs"][side].items():
                out[py + y, px + x] = c
    else:
        for (x, y), c in legs.items():
            # (the run: no skin in the legs - Codex's hands by its hips went with its arms)
            if 0 <= py + y < h and not arm[py + y, px + x] and not (
                    swing is not None and tuple(int(v) for v in c[:3]) in SKIN):
                out[py + y, px + x] = c
    if swing is not None:                        # the run's far arm behind the body, its hand over the legs
        for (x, y), c in swing["back"].items():
            out[py + y + drop, px + x] = c
    if placed is not None:
        for (x, y), c in placed.items():
            if 0 <= py + y < h:
                out[py + y, px + x] = c
    else:
        for (x, y), c in list(P["upper"].items()) + list(torso_sides(P["upper"]).items()):
            out[py + y, px + x + lx(y)] = c
    if swing is not None:                        # the run's near arm over the body
        for (x, y), c in swing["front"].items():
            out[py + y + drop, px + x] = c
    for side in idle_arms:                       # IDLE_ARMS: the idle's own arm, square for square
        for part in ("upper", "fore"):
            for (x, y), c in P["arms"][(side, part)].items():
                out[py + y + drop, px + x + lx(y)] = c
    for layer in ("over", "front"):
        for (x, y), c in posed[layer].items():
            if 0 <= py + y < h and 0 <= px + x < w and (py + y, px + x) not in face:
                out[py + y, px + x] = c
    lay(arms["over"], True, SHOULDER["back"])
    lay(arms["front"], True, SHOULDER["front"])
    return out, thinned, int(round(lean * (R.HIP_Y - R.NECK_Y)))


def build():
    with open(lp(os.path.join(NAT, "ryze_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    cell = cells["cell"][:2]
    des = design()
    x0, x1, y0, y1 = HEAD
    head = {(x, y): c for (x, y), c in des.items() if x0 <= x <= x1 and y0 <= y <= y1}
    P = R.parts(R.design())
    out, log = {}, []
    for tag in TAGS:
        frs = cells["tags"][tag]
        frames = cells_of(os.path.join(SRC, f"ryze_{tag}.png"), len(frs), cell)
        if tag == "idle":                       # the design itself on every pivot (the pack's idle is the design
            frames = []                         # before its hips: design_ryze_v2.py HIPS)
            for fr in frs:
                f = np.zeros((cell[1], cell[0], 4), np.uint8)
                for (x, y), c in des.items():
                    f[fr["pivot"][1] + y, fr["pivot"][0] + x] = c
                frames.append(f)
        done = []
        for k, (f, fr) in enumerate(zip(frames, frs)):
            a, hd, fixed = mend(f, fr["pivot"], des, head)
            note = ""
            if tag == "dead" and k + 1 in DEATH:   # drawn on the idle's body (ryze_death.py), not Codex's
                kind, ddy = DEATH[k + 1]
                a = RD.frame(kind, des, fr["pivot"], a.shape, R.rgba, np.array(INK + (255,), np.uint8), ddy)
                note = f" | death drawn on the idle: {kind} {ddy}"
            crouch = (tag, k + 1) in CROUCH
            own = (tag, k + 1) in OWN_LEGS or crouch
            if IDLE_BODY.get(tag) == "all" or (k + 1) in IDLE_BODY.get(tag, []) or own:
                point = [s for (t, n), s in POINT.items() if t == tag and n == k + 1]
                if hd[2] < 0.9:                  # the pasted head partly covered: its place by the eyes
                    hd = eye_offset(a, fr["pivot"]) + (1.0,)
                hip = flap_top(a, fr["pivot"]) - FLAP_TOP if crouch else None
                a, thinned, lean = idle_body(a, fr["pivot"], (hd[0], max(0, hd[1])), P, tag, point,
                                             (tag, k + 1) in OVER_SCROLL, own, hip, run_arms(k, P) if tag == "run" else None,
                                             IDLE_ARMS.get((tag, k + 1), ()))
                a, _, fixed = mend(a, fr["pivot"], des, head, lean / (R.HIP_Y - R.NECK_Y))
                note = f" | idle body, lean {lean:+d}, arms thinned by {thinned}"
            if (tag, k + 1) in HEAD_TOP:
                # Codex's own drawn head behind the pasted one: its crown showed over the pasted head's top
                # outline as a band (the death's 3 and 5) or a second outline (6-8)
                ex, ey = eye_offset(a, fr["pivot"])
                px, py = fr["pivot"]
                for y in range(-32, -29):
                    for x in range(-5, 7):
                        a[py + y + ey, px + x + ex] = 0
                note += " | crown band cleared"
            if (tag, k + 1) in FEET:            # hand-drawn: the boot of a leg swinging through (its rows cut off)
                px, py = fr["pivot"]
                for row, (x0, s) in FEET[(tag, k + 1)].items():
                    for j, ch in enumerate(s):
                        a[py + row, px + x0 + j] = R.rgba(ch)
                note += " | boot drawn"
            if tag != "idle":                    # crumbs apart from the figure (a hand of Codex's left by the legs)
                ps = pieces(a[..., 3] > 0)
                big = max(len(p_) for p_ in ps)
                for p_ in ps:
                    if len(p_) < CRUMB and len(p_) < big:
                        for (y, x) in p_:
                            a[y, x] = 0
                        note += f" | crumb {len(p_)}"
            if (tag, k + 1) in SHIFT_X:
                s_ = SHIFT_X[(tag, k + 1)]
                a = np.concatenate([a[:, -s_:], np.zeros_like(a[:, :-s_])], axis=1) if s_ < 0 else a
                note += f" | x {s_:+d}"
            if (tag, k + 1) in RAISE:
                r_ = RAISE[(tag, k + 1)]
                a = np.concatenate([a[r_:], np.zeros_like(a[:r_])])
                note += f" | up {r_}"
            if tag != "idle":
                note += f" | ring {ring_close(a, fr['pivot'][1])}"
                for comp in raw_holes(a):        # a slit the ring walled in (between an arm and the body): outline
                    if len(comp) <= POCKET:
                        for (y, x) in comp:
                            a[y, x] = INK + (255,)
            done.append(a)
            log.append(f"{tag} {k + 1}: head {hd[0]:+d},{hd[1]:+d} ({hd[2]:.0%}) " +
                       " ".join(f"{k_} {v}" for k_, v in sorted(fixed.items())) + note)
        out[tag] = done
    # frames taken from another (REUSE): Codex's landing crouch was its old bulky body under the head (the review:
    # "the idle's body gone apart from the head") - the landing lands in R's own kneel
    for (tag, k), (stag, sk) in REUSE.items():
        src = out[stag][sk - 1]
        (sx, sy), (tx, ty) = cells["tags"][stag][sk - 1]["pivot"], cells["tags"][tag][k - 1]["pivot"]
        dst = np.zeros_like(src)
        h, w = src.shape[:2]
        for y, x in zip(*np.nonzero(src[..., 3])):
            Y, X = y - sy + ty, x - sx + tx
            if 0 <= Y < h and 0 <= X < w:
                dst[Y, X] = src[y, x]
        out[tag][k - 1] = dst
        log.append(f"{tag} {k}: = {stag} {sk}")
    return out, cells, log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out, cells, log = build()
    for line in log:
        print(line)
    cell = cells["cell"][:2]
    bad = 0
    for tag, frames in out.items():
        s = sheet_of(frames, cell)
        path = os.path.join(NAT, f"ryze_{tag}.png")
        if a.check:
            same = np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")), s)
            print(tag, "same" if same else "DIFFERENT")
            bad += not same
            continue
        Image.fromarray(s).save(lp(path))
        print("wrote", os.path.relpath(path, ROOT))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

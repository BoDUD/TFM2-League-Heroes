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
- small pockets elsewhere (at most POCKET squares: an arm and the body; or a slit at most SLIT[1]
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
from the design's squares there. After the review: R's channel is drawn from joints (DRAWN, Codex's broke into
pieces), crumbs apart from the figure go (CRUMB), the far arm Codex folded into a lump while shooting and the
recoveries' short arms are the idle's own (IDLE_ARMS), and R's channel stands (REUSE). The run is not Codex's any more:
League's Ryze_Run_Fast frame for frame on the design's own body (run_frame, 2026-10-05).
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
import ryze_arms as RA  # noqa: E402

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
BELT_ROW = -4                                    # the belt's last row (from the pivot): a crouch (CROUCH) takes Codex's legs under it
# the run's pelvis (the user, 2026-10-05: 「腿和腰脱节的问题你没解决啊」「跑步的时候」「瑞兹走路时候这里少一块就像脱节一样」):
# Codex's thighs met the belt narrower than it and 2-5 squares to its left in five of the eight frames, so ground showed
# under the belt's front end. The design's two rows under the belt (the trousers' seat and the flap's top: pivot rows
# PELVIS, columns PELVIS_X) go with the upper body; the run's legs hang under them (run_frame: League's since)
PELVIS = (-3, -2)
PELVIS_X = (-6, 6)
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
# the run's arms: Codex's broke into pieces over the body (the review: "arm fragments"), lines of the idle's arm
# colours swung as pendulums read as strange (「瑞兹走路时手还是有点不自然」), and League's run joints laid on the screen
# as League's camera sees them threw the far arm out level from the shoulder (「你觉得对吗 我的天 都变形了」); then the
# idle's arms posed on the first version's joints (V1_ARMS, below). Those squares sheared and quarter-turned (ryze_arms.pose)
# came apart where a forearm turned past 45 degrees (the run's fists, R's hands), the far forearm laid across the chest
# drew outlines through the body, and R 7-8's near arm went up as one long sheared line (the user, 2026-10-04: 「第一张
# 图这里是像素丢失 一条黑线？ 第二张图这里手臂严重变形？ 右手臂和蛇精一样的？你看像官方瑞兹啊 好好修复吧」). So the run and
# R's channel are drawn from joints (ryze_arms.draw: shaded capsules in the idle's materials and widths, the bones the
# idle's lengths); {(tag, frame): {side: (upper arm degrees, forearm degrees, layer)}} from straight down, + forward.
# (The run's arms are League's since: run_frame.) R 5-8: League's joints (lol_joints_v2.json, the game camera): the far arm
# raised by the head and the near one held out low (5-7), both raised (8; the landing's first frame is R's last, REUSE)
DRAWN = {
    ("ult", 5): {"far": (-106, 177, "over"), "near": (28, 64, "front")},
    ("ult", 6): {"far": (-117, -155, "over"), "near": (45, 63, "front")},
    ("ult", 7): {"far": (-110, -149, "over"), "near": (50, 63, "front")},
    ("ult", 8): {"far": (-144, 179, "over"), "near": (140, -173, "front")},
}
DRAW_S = {"far": (-7.0, -13.5), "near": (6.5, -13.0)}    # the shoulders for ryze_arms.draw (square centres at +0.5)
# the arms of every standing frame posed as the first version's (the user-approved strips before the slimming): their
# joints (shoulder, elbow, wrist, hand) read off each frame (V1_ARMS), the idle's own arm turned to the same directions
# (tools/art/ryze_arms.py) - Codex's v2 arms and the idle's arm turned at a guess read as stiff (「瑞兹的手臂感觉还是很
# 奇怪真的」「像个僵尸一样」「不自然」)
V1_ARMS = os.path.join(ROOT, "assets", "source", "ryze", "v1_arm_joints.json")
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
REUSE = {("ult_land", 1): ("ult", 8)}
# ... and kneels again (2026-10-05, shown League's crouch beside the standing channel: 「瑞兹放大招时要下跪吧」, then the
# kneel picked over standing): frames 2-4 are the death's one-knee kneel on the idle's own body (ryze_death.py KNEEL,
# the upper body down dy rows) with the arms drawn from joints (DRAWN's way) where League's spell4 puts the hands: the
# near hand down to the ground beside the knee (2), both hands down before the knees (3), rising with the hands by the
# hips (4); {frame: (dy, {side: (upper arm degrees, forearm degrees, layer)})}
R_KNEEL = {2: (7, {"far": (34, 42, "back"), "near": (14, 6, "front")}),
           3: (8, {"far": (25, 40, "over"), "near": (-10, -20, "front")}),
           4: (7, {"far": (-10, 20, "back"), "near": (10, 40, "front")})}
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
    the body's legs and upper body when not the idle's (a crouch: Codex's legs, the upper body to the belt)."""
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


def arm_poses():
    """{(tag, frame): {side: (upper arm degrees, forearm degrees, layer)}} from the first version's arms
    (V1_ARMS: their joints read off the user-approved first strips), the angles from straight down, + forward."""
    if not os.path.exists(lp(V1_ARMS)):
        return {}
    with open(lp(V1_ARMS), encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for strip_ in data:
        for fr in strip_["frames"]:
            pose = {}
            for side in ("far", "near"):
                j = fr[side]
                if j.get("hidden") or not all(j.get(k) for k in ("shoulder", "elbow", "hand")):
                    pose[side] = (0.0, 0.0, "back" if side == "far" else "front")
                    continue
                S, E, H = j["shoulder"], j["elbow"], j["hand"]
                up = math.degrees(math.atan2(E[0] - S[0], E[1] - S[1]))
                fore = math.degrees(math.atan2(H[0] - E[0], H[1] - E[1]))
                lay_ = j.get("layer", "")
                if side == "far":
                    layer = "over" if lay_ == "in_front_of_body" else "back"
                else:
                    layer = "back" if lay_ == "behind_body" else "front"
                pose[side] = (up, fore, layer)
            out[(strip_["tag"], fr["frame"])] = pose
    return out


def drawn_arms(pose, P):
    """{layer: squares} of both arms posed (ryze_arms.pose: the idle's arm squares sheared and turned)."""
    out = {"back": {}, "over": {}, "front": {}}
    for side, (up, fore, layer) in pose.items():
        out[layer].update(RA.pose(P["arms"], side, up, fore))
    return out


def joint_arms(pose):
    """{layer: squares} of both arms drawn from their angles (DRAWN; ryze_arms.draw with the idle's bone lengths, the
    upper arm's from rig_ryze's joints), without an outline (ring_layer draws one round each layer)."""
    out = {"back": {}, "over": {}, "front": {}}
    for side, (up, fore, layer) in pose.items():
        sp = R.ARMS["back" if side == "far" else "front"]
        upper = math.hypot(sp["E"][0] - sp["S"][0], sp["E"][1] - sp["S"][1])
        S = DRAW_S[side]
        u, f = math.radians(up), math.radians(fore)
        E = (S[0] + upper * math.sin(u), S[1] + upper * math.cos(u))
        W = (E[0] + RA.FORE * math.sin(f), E[1] + RA.FORE * math.cos(f))
        H = (W[0] + RA.HAND * math.sin(f), W[1] + RA.HAND * math.cos(f))
        out[layer].update({q: R.rgba(ch) for q, ch in RA.draw(S, E, W, H, side, "fist", upper=upper).items()})
    return out


def kneel_frame(pivot, shape, P, dy, pose):
    """R_KNEEL: the death's one-knee kneel (ryze_death.py KNEEL legs) under the idle's upper body without its arms
    (dropped dy rows, the flap hanging from the belt) and both arms drawn from joints (joint_arms), each with one
    outline: the far arm behind the body unless over it, the near one in front; nothing on the face."""
    px, py = pivot
    out = np.zeros(shape, np.uint8)
    ink = np.array(INK + (255,), np.uint8)
    arms = {layer: {(x, y + dy): c for (x, y), c in cells.items()} for layer, cells in joint_arms(pose).items()}
    face = {(py + y + dy, px + x) for (x, y), c in P["upper"].items()
            if y <= HEAD[3] and HEAD[0] - 1 <= x <= HEAD[1] + 1}
    ring_layer(out, arms["back"], py, px, face=set(), over=False)
    for name in ("far", "near"):
        RD.put(out, pivot, RD.cells_of(RD.KNEEL[name], R.rgba), ink)
    body = dict(P["upper"])
    body.update({xy: c for xy, c in torso_sides(P["upper"]).items() if xy[1] <= BELT_ROW and xy not in body})
    RD.put(out, pivot, {(x, y + dy): c for (x, y), c in body.items() if y + dy <= 10}, ink, outline=False)
    for layer in ("over", "front"):
        ring_layer(out, arms[layer], py, px, face=face, over=True)
    return out


# ---- the run (2026-10-05): League's Ryze_Run_Fast frame for frame on the design's own body ---------------------------
# The user on the run built from Codex's strides and the first version's arm joints: 「感觉不对啊 和英雄联盟不一样」
# 「瑞兹走路也没那味」「手臂做的很不好」 - the legs split 29 squares wide in 4 and 8, the arms swung with the legs on
# the same side, the near forearm stuck out level. League's run (the clip `Run` plays: Ryze_Run_Fast, see
# tools/lol/anim_graph.py) at game size: short bouncing strides, the heel kicked up behind, the knee lifted, the body
# leaning and bobbing, both fists pumping at the waist. So:
# - the legs: League's angles seen from the side (RUN_PROFILE, tools/lol/pose_joints.py with poses_run_profile.json =
#   poses_v2.json at yaw 90: the stride reads across the screen) on bones of the design's lengths (the thigh to the knee
#   band, the shin to the ankle band, the foot level under a standing shin or along League's foot kicked up), drawn row
#   by row (column by column where a bone lies flat) in the design's leg materials (rig_ryze.limb), the screen-left leg
#   (League's R) lit and in front, each with one outline; the body as high as the lowest sole lets it stand, lifted in
#   League's two airborne frames;
# - the upper body: the design's without its arms, with its pelvis rows (PELVIS), RUN_LEAN of a square per row forward
#   over the hips (the head as one block), bobbing with League's head in the design's camera (lol_joints_v2.json);
# - the arms: the design's own arm squares (the upper arm, the bracer, the hand) posed whole from the shoulder by
#   ryze_arms.pose (each bone's rows shifted within 45 degrees of hanging, a quarter turn past it, rows dropped where it
#   points at the camera - nothing resampled), three held poses each on League's timing (RUN_POSES), the elbows bent;
#   the far arm behind the body, across the belly when forward; the near one before the body, behind it when swung
#   back. Drawn as capsules (ryze_arms.draw) they were tubes of their own: eased every frame they crawled
#   (「右手臂还是奇怪看起来 在那晃动和个虫一样」), the near one drawn against the body cut its outline into the shirt
#   (「右手臂是贴着身体的 还导致身体变形了」), with only its forearm swinging it read stiff (「只有前臂晃动」);
# - the hands are fists: the design's hand without its fingertip row (RUN_FIST_ROW) - the round fist drawn before was
#   a lilac dot (「手的形状也没有」), the design's open hand with its fingertip an odd finger (「手指头做的是什么啊
#   你不然就做成拳头形状啊」);
# - ground walled in by the figure (between the far arm and the body: 「瑞兹这里有点色素丢失」) takes the colour beside it
#   that is neither the outline nor an arm's (fill_pockets); a crack one square wide takes the outline (fill_cracks).
RUN_PROFILE = os.path.join(ROOT, "assets", "source", "ryze", "lol_run_profile.json")
RUN_SIDE = {"near": "R", "far": "L"}                     # the run's legs: the screen-left one is League's R
RUN_HIP = {"near": (-4.0, -1.0), "far": (3.0, -1.0)}     # the hip joints (from the pivot)
RUN_BONES = (4.0, 6.0, 3.0)                              # the thigh, the shin, a raised foot
RUN_SOLE = 10                                            # the soles' row (the outline under them on 11)
RUN_THIGH = {"near": ["wow", "woz", "wwo", "wwz", "xxo"], "far": ["ozo", "ozl", "oow", "ozl", "hxo"]}
RUN_SHIN = {"near": ["hhhj", "jxjj", "jj", "hj", "hj", "xj"], "far": ["jhhj", "jjxj", "jj", "jh", "jh", "jx"]}
RUN_FOOT = {"near": ("jDhj", "jjjj"), "far": ("rjjh", "jjjj")}
RUN_KICK = 50                                            # a shin further than this from hanging: the foot raised
RUN_LEAN = 0.12
RUN_BOB = 0.6                                            # of League's head's bob (game px in the design's camera)
# each arm in three held poses, as a sprite's run swings its arms (one shape held through the frames of a swing):
# F at the front of the swing, M passing, B at the back; {side: {pose: (upper arm, forearm degrees from hanging
# (+ forward), layer)}}. The near arm goes behind the body only at the back of its swing. The far one swings back from
# the shoulder only a little, the whole arm leaning back as one: swung further it parted from the body in a narrow wedge,
# a crack of ground or, filled, a dark lump (「你不觉得奇怪吗？」), and a forearm turned further back is a stair of bracer;
# its forearm hangs back, as League's does (hanging forward, its hand met the hip and walled in ground with the body)
# The near arm swings as the far one does (「左手做的很好 右手不能按左手那样做吗」): at the front its upper arm hangs and
# the forearm lies level, a quarter turn of the bracer clean as the far arm's across the belly (sheared down at 50
# degrees it was a stair of bracer); passing it hangs nearly as the idle's (bent 25 degrees its forearm reached down
# the thigh); at the back it is behind the body.
RUN_POSES = {"near": {"F": (-5, 80, "front"), "M": (0, 8, "front"), "B": (-25, 0, "back")},
             "far": {"F": (-5, 80, "over"), "M": (-6, 18, "back"), "B": (-14, -14, "back")}}
# the poses frame by frame on League's timing (each hand's lead over its shoulder in the design's camera,
# lol_joints_v2.json: the near hand ahead in 7-2, back in 4-5; the far one ahead in 3-5, back in 8-1 - in 7 it passes,
# its hand clear of the near leg kicked up behind, which walled in ground with it)
RUN_ARM_FRAMES = {"near": "FFMBBMFF", "far": "BMFFFMMB"}
RUN_FIST_ROW = -2                                        # the design's hands down to this row: the fingertips left out
CRACK_ROWS = 6                                           # one-square cracks closed down to this row (from the pivot)
def run_arms(P):
    """The design's arm squares without their outline (ring_layer draws one round each layer), the hands fists."""
    return {(key, part): {q: c for q, c in cells.items() if tuple(int(v) for v in c[:3]) not in DARK
                          and not (part == "fore" and q[1] > RUN_FIST_ROW)}
            for (key, part), cells in P["arms"].items()}


def run_tables():
    """League's run: the profile joints (legs) and the body's bob per frame."""
    with open(lp(RUN_PROFILE), encoding="utf-8") as f:
        prof = json.load(f)
    head = [f["joints"]["Head"][1] for f in R.lol_table()["run"]]
    return prof, [int(round(RUN_BOB * (y - min(head)))) for y in head]


def run_leg(side, hip, thigh, shin, foot):
    """({(x, y): colour}, lowest row) of one run leg from its hip along League's angles (radians from hanging)."""
    lt, ls, lf = RUN_BONES
    knee = (hip[0] + lt * math.sin(thigh), hip[1] + lt * math.cos(thigh))
    ank = (knee[0] + ls * math.sin(shin), knee[1] + ls * math.cos(shin))
    cells = {}
    R.limb(hip, knee, RUN_THIGH[side], -1, cells)
    R.limb(knee, ank, RUN_SHIN[side], -1, cells, first=False)
    ax, ay = int(math.floor(ank[0] + 0.5)), int(math.floor(ank[1] + 0.5))
    if abs(math.degrees(shin)) <= RUN_KICK:     # standing or reaching: the foot level, the toe forward
        for row, s in enumerate(RUN_FOOT[side]):
            for j, ch in enumerate(s):
                cells[(ax - 1 + j, ay + 1 + row)] = R.rgba(ch)
    else:                                       # kicked up behind: the boot's foot along League's
        R.limb(ank, (ank[0] + lf * math.sin(foot), ank[1] + lf * math.cos(foot)), ["jj", "Dj", "jr"], -1, cells,
               first=False)
    return cells, max(y for _, y in cells)


def fill_pockets(a):
    """Ground walled in by the figure takes the commonest colour beside it that is neither the outline nor an arm's
    (ARM_COLOURS: the torso's side next to an arm), else the outline's; filled from its edge in."""
    h, w = a.shape[:2]
    op = a[..., 3] > 0
    outside = np.zeros((h, w), bool)
    todo = deque([(y, x) for y in range(h) for x in (0, w - 1) if not op[y, x]] +
                 [(y, x) for x in range(w) for y in (0, h - 1) if not op[y, x]])
    for y, x in todo:
        outside[y, x] = True
    while todo:
        y, x = todo.popleft()
        for oy, ox in N4:
            Y, X = y + oy, x + ox
            if 0 <= Y < h and 0 <= X < w and not op[Y, X] and not outside[Y, X]:
                outside[Y, X] = True
                todo.append((Y, X))
    left = set(zip(*np.nonzero(~op & ~outside)))
    while left:
        done = {}
        for y, x in left:
            near = [tuple(int(v) for v in a[y + oy, x + ox]) for oy in (-1, 0, 1) for ox in (-1, 0, 1)
                    if (oy or ox) and a[y + oy, x + ox, 3]]
            if not near:
                continue
            body = [c for c in near if c[:3] not in DARK and c[:3] not in ARM_COLOURS]
            done[(y, x)] = Counter(body).most_common(1)[0][0] if body else INK + (255,)
        if not done:
            break
        for (y, x), c in done.items():
            a[y, x] = c
        left -= set(done)
    return a


def fill_cracks(a, py):
    """A crack of ground one square wide - the figure on both sides of it in its row and above it (between a limb and
    the body, between two legs touching under the flap) - takes the outline: two outlines meeting read as one line, as
    the design draws them (「这里也补补吧」). Wider gaps stay open: a gap filled with the body's colour beside it read as
    a dark lump (「你不觉得奇怪吗？」)."""
    h, w = a.shape[:2]
    op = a[..., 3] > 0
    found = [(y, x) for y in range(1, min(h - 1, py + CRACK_ROWS + 1)) for x in range(1, w - 1)
             if not op[y, x] and op[y, x - 1] and op[y, x + 1] and op[y - 1, x]]
    for y, x in found:
        a[y, x] = INK + (255,)
    return a


def run_frame(k, pivot, shape, P, tables):
    """Run frame k (0-7) on the design's own body from League's joints (see RUN_PROFILE above)."""
    prof, bob = tables
    j, air = prof[k]["joints"], prof[k]["air"]

    def ang(a_, b_):
        return math.atan2(b_[0] - a_[0], b_[1] - a_[1])
    legs = {side: (ang(j[s + "_Hip"], j[s + "_KneeLower"]), ang(j[s + "_KneeLower"], j[s + "_Foot"]),
                   ang(j[s + "_Foot"], j[s + "_Toe"])) for side, s in RUN_SIDE.items()}
    dy = RUN_SOLE - max(run_leg(side, RUN_HIP[side], *legs[side])[1] for side in legs) - air
    b = bob[k]
    px, py = pivot
    out = np.zeros(shape, np.uint8)
    ink = np.array(INK + (255,), np.uint8)
    for side in ("far", "near"):
        RD.put(out, pivot, run_leg(side, (RUN_HIP[side][0], RUN_HIP[side][1] + dy), *legs[side])[0], ink)
    arms = {"back": {}, "over": {}, "front": {}}
    squares = run_arms(P)
    for side in ("far", "near"):
        up, fore, layer = RUN_POSES[side][RUN_ARM_FRAMES[side][k]]
        arms[layer].update({(x + R.lean_x(RUN_LEAN, -14), y + dy + b): c
                            for (x, y), c in RA.pose(squares, side, up, fore).items()})
    face = {(py + y + dy + b, px + x + R.lean_x(RUN_LEAN, y)) for (x, y), c in P["upper"].items()
            if y <= HEAD[3] and HEAD[0] - 1 <= x <= HEAD[1] + 1}
    ring_layer(out, arms["back"], py, px, face=set(), over=False)
    body = dict(P["upper"])
    body.update({xy: c for xy, c in torso_sides(P["upper"]).items() if xy[1] <= BELT_ROW and xy not in body})
    body.update({(x, y): c for (x, y), c in P["full"].items()
                 if PELVIS[0] <= y <= PELVIS[1] and PELVIS_X[0] <= x <= PELVIS_X[1]})
    for (x, y), c in body.items():
        X, Y = px + x + (R.lean_x(RUN_LEAN, y) if y < R.HIP_Y else 0), py + y + dy + b
        if 0 <= Y < shape[0] and 0 <= X < shape[1]:
            out[Y, X] = c
    for layer in ("over", "front"):
        ring_layer(out, arms[layer], py, px, face=face, over=True)
    for _ in range(6):                           # closing the outline can make a notch of what was open: again
        before = out.copy()
        ring_close(out, py)
        fill_pockets(fill_cracks(out, py))
        if (out == before).all():
            break
    return out


def ring_layer(out, cells, py, px, face, over):
    """Arm squares (x, y from the pivot) onto the frame with one outline round them: over the body too when over, never
    on the face (a hand by the face stops at it)."""
    h, w = out.shape[:2]
    pts = {(py + y, px + x): c for (x, y), c in cells.items() if 0 <= py + y < h and 0 <= px + x < w
           and (py + y, px + x) not in face}
    for (y, x) in pts:
        for oy, ox in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (y + oy, x + ox)
            if q in pts or q in face or not (0 <= q[0] < h and 0 <= q[1] < w):
                continue
            if over or not out[q][3]:
                out[q] = INK + (255,)
    for q, c in pts.items():
        out[q] = c


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


def own_legs(a, pivot, dy):
    """Codex's own legs (a crouch) under the idle's belt dropped dy rows: its squares from the row
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
              idle_arms=(), drawn=None):
    """A standing frame on the idle's own upper body with Codex's arms drawn again (the module's docstring); legs_own:
    the idle's upper body down to its belt, dropped to Codex's head, over Codex's own legs (a crouch); crouch_hip: in a
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
        legs = own_legs(a, pivot, hip)
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
    if drawn is not None:                        # ARM_POSES: the idle's arms posed as the first version's (ryze_arms)
        groups, swing, idle_arms = [], None, ()
        for layer, cells in drawn.items():
            posed[layer].update({(x + R.lean_x(lean, -14), y + drop): c for (x, y), c in cells.items()})

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
    if legs is None:
        for side in ("back", "front"):
            for (x, y), c in P["legs"][side].items():
                out[py + y, px + x] = c
    else:
        for (x, y), c in legs.items():
            if 0 <= py + y < h and not arm[py + y, px + x] and not (
                    swing is not None and tuple(int(v) for v in c[:3]) in SKIN) and 0 <= px + x < w:
                out[py + y, px + x] = c
    if swing is not None:                        # the run's far arm behind the body, its hand over the legs
        for (x, y), c in swing["back"].items():
            out[py + y + drop, px + x] = c
    # the far arm behind the body (over the legs: its hand hangs beside the hips), with its outline
    lay(arms["back"], False, SHOULDER["back"])
    ring_layer(out, posed["back"], py, px, face=set(), over=False)
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
        ring_layer(out, posed[layer], py, px, face=face, over=True)
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
    poses = arm_poses()
    run_tabs = run_tables()
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
            kneel = tag == "ult" and k + 1 in R_KNEEL
            if kneel:                            # R's channel kneeling on the idle's body (R_KNEEL)
                kdy, pose_ = R_KNEEL[k + 1]
                a = kneel_frame(fr["pivot"], a.shape, P, kdy, pose_)
                note = f" | kneel drawn on the idle: {kdy}"
            if tag == "run":                     # League's run on the design's own body (run_frame), not Codex's
                a = run_frame(k, fr["pivot"], a.shape, P, run_tabs)
                note = " | run drawn from League's joints"
            crouch = (tag, k + 1) in CROUCH
            own = crouch
            if (IDLE_BODY.get(tag) == "all" or (k + 1) in IDLE_BODY.get(tag, []) or own) and not kneel:
                point = [s for (t, n), s in POINT.items() if t == tag and n == k + 1]
                if hd[2] < 0.9:                  # the pasted head partly covered: its place by the eyes
                    hd = eye_offset(a, fr["pivot"]) + (1.0,)
                hip = flap_top(a, fr["pivot"]) - FLAP_TOP if crouch else None
                a, thinned, lean = idle_body(a, fr["pivot"], (hd[0], max(0, hd[1])), P, tag, point,
                                             (tag, k + 1) in OVER_SCROLL, own, hip, None,
                                             IDLE_ARMS.get((tag, k + 1), ()),
                                             joint_arms(DRAWN[(tag, k + 1)]) if (tag, k + 1) in DRAWN else
                                             drawn_arms(poses[(tag, k + 1)], P) if (tag, k + 1) in poses else None)
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

#!/usr/bin/env python3
"""Kai'Sa's second design: Codex's strips (2026-10-03, on the 42-row design) finished for the game.

    python tools/art/fix_kaisa_strips_v2.py [--check]

Codex drew every action again on the 42-row design (assets/source/kaisa/codex_strips_v2: its HANDOFF.md, the brief
assets/source/kaisa/MODEL_STRIPS_V2.md); its HANDOFF says it itself: the head is not the design's square for square
and the standing legs only follow the idle's. The user: 「卡莎的也好了 有奇怪的地方请帮忙给codex擦屁股」, and on Ryze's
casts 「手臂待机和释放技能时尺寸还是不一样」「上半身也是 释放技能上半身衣服变了」「体型也变了」 - the casting body must be the
idle's. So:
- the standing frames (IDLE_BODY: the casts, the hit, the landing's last two, the death's first two) are the idle's
  own body square for square - the head, the pods, the long hair, the suit and its gold plates, the far arm hanging
  as in the idle, the legs - and only what Codex moved is Codex's: the near arm (NEAR_ARM on the design, wherever
  Codex put it: the shot, the W cannon), Q's opened pods (OPEN_PODS: the design's closed pods go, Codex's wings stay);
  that is, Codex's squares outside the idle's body on the near side (and over the head with the pods open), moved with
  the head Codex drew (its near eye on the design's), thinned where 5+ squares thick (the outer layer off, its colours
  moved in), the near arm in front of the body and the wings behind it, each with one outline;
- the upright frames that are not standing (the run, the landing's rise: HEAD_LOCK) get the design's face (the hair
  and the face of the pack's head) on Codex's near eye;
- R's launch and dash, the landing's crouch, the death's fall are Codex's as drawn (its lying frames 7-8 raised
  RAISE rows onto the soles' line);
- then the pockets of ground walled in (closed as the importer closes the outline): up to POCKET squares the
  commonest colour round them, in the standing frames up to BODY_POCKET the design's own squares there;
- R's strip (4 frames: the launch 1-3, the dash 4) is split into kaisa_ult.png and kaisa_ult_dash.png.
The idle is the design on its six pivots (with its crown: tools/art/design_kaisa_v2.py).
Writes assets/source/native/kaisa_<tag>.png on the cells of assets/source/native/kaisa_cells.json; then run
tools/art/import_native.py --hero kaisa.
"""
import argparse
import json
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
import fix_ryze_strips_v2 as FR  # noqa: E402
import kaisa_death as KD  # noqa: E402
import design_kaisa_v2 as V  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kaisa", "codex_strips_v2")
NAT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(ROOT, "assets", "source", "kaisa", "design_v2", "kaisa_design_v2_1x.png")
Z = 8
PIVOT = (64, 88)                                # the design's standing point on its canvas (soles on +11)
INK = (0x14, 0x01, 0x1B)
DARK = {(0x14, 0x01, 0x1B), (0x17, 0x01, 0x1E), (0x0F, 0x07, 0x15)}   # the outline and its near-blacks
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "ult_land", "hit", "dead"]
IDLE_BODY = {"attack": "all", "skill": "all", "skill2": "all", "hit": "all", "ult_land": [3, 4], "dead": [1, 2]}
HEAD_LOCK = {"run": "all", "ult": [1, 2, 3], "ult_land": [1, 2]}
OPEN_PODS = {"skill": [3, 4]}                  # Q's wings open in 3-4; in 2 and 5 Codex's half-open ones were loose
                                                # strips beside the pods moved apart (design_kaisa_v2.py PODS_OUT): closed
POD = {(0xF7, 0xCA, 0x4E), (0xFB, 0x2C, 0xFB), (0x8F, 0x10, 0x89), (0xB5, 0x0E, 0xB1)}
EYE_WHITE, EYE_AT = (0xFD, 0xFC, 0xFC), (-1, -19)    # the near eye's top white square on the design
POCKET = 10
BODY_POCKET = 30
RAISE = {}   # lying 2 rows under the soles' line: up onto the ground
THICK = 3
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def near_arm(x, y):
    """The near arm on the design (x, y from the pivot): the gauntlet under the shoulder plate, the gold bracer, the
    magenta forearm and the claws hanging by the near hip; the torso's own edge (column 4) stays."""
    return (x >= 5 and -8 <= y <= -3) or (x >= 6 and -2 <= y <= 3)


# her palette by letter (work/ks2 charts) and her arm drawn again along Codex's (the review: sticks, a '+' hand, a
# double outline at the hip): three squares wide, the dark suit of the upper arm lit on top, the gold band, the
# magenta forearm, the claws with their pale highlight
KPAL = {"a": "14011B", "b": "F7CA4E", "c": "17011E", "d": "8F1089", "e": "FB2CFB", "f": "651A68", "g": "342C62",
        "h": "B50EB1", "i": "561F67", "j": "4B3675", "k": "271A43", "l": "FCDDCD", "n": "440F52", "r": "2F2952",
        "x": "A97F3C", "y": "0F0715", "z": "5A6299", "A": "8C8A95", "B": "484D78", "C": "D69732", "D": "9D346A",
        "E": "722A8C", "F": "FCD685", "v": "EE777C", "t": "FDDBCD", "w": "FBBCA5"}


def krgba(ch):
    h = KPAL[ch]
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255], np.uint8)


def kcol(ch):
    return tuple(int(KPAL[ch][i:i + 2], 16) for i in (0, 2, 4))


KMAT = {"upper": ("B", "r", "k"), "band": ("F", "b", "x"), "bracer": ("e", "d", "n"), "hand": ("F", "e", "d"),
        "tip": ("e", "d", "n")}
K_BRACER = {kcol(c) for c in "bxFC"}
K_SKIN = {kcol(c) for c in "rBkg"}
SHOULDER_K = (5, -9)                             # the near arm's top under the shoulder plate
CANNON = {"skill2": [2, 3, 4, 5]}               # W's cannon: Codex's as drawn, the upper arm drawn to it


def pod_squares(des):
    """The pods on the design: the gold, magenta and dark plum regions over the shoulders connected to the gold rims,
    their own outline, not the crown drawn between them (design_kaisa_v2.py CROWN)."""
    podc = POD | {kcol("f"), kcol("i"), kcol("D")}
    cand = {(x, y) for (x, y), c in des.items() if y <= -17 and rgb(c) in podc}
    out = set()
    seeds = [p for p in cand if rgb(des[p]) == kcol("b") and p[1] <= -22]
    q = list(seeds)
    out.update(seeds)
    while q:
        x, y = q.pop()
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                n = (x + ox, y + oy)
                if n in cand and n not in out:
                    out.add(n)
                    q.append(n)
    for (x, y), c in des.items():
        if y <= -17 and rgb(c) in DARK:
            around = [(x + ox, y + oy) for ox in (-1, 0, 1) for oy in (-1, 0, 1) if ox or oy]
            if any(q_ in out for q_ in around) and all(q_ in out or q_ not in des or rgb(des[q_]) in DARK
                                                       for q_ in around):
                out.add((x, y))
    return out - NOTCH


NOTCH = {(x0 + j, y) for y, (x0, s) in V.CROWN.items() for j, ch in enumerate(s) if ch not in " ."}
# the crown drawn between the pods (design_kaisa_v2.CROWN): the head's, not a pod's


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


def rgb(c):
    return tuple(int(v) for v in c[:3])


def head_squares(des):
    """The pack's head (work/ks2/kaisa_strips_v2_pack.py): the hair and the face down to the chin, not the pods; with
    the top-right squares the design filled since (design_kaisa_v2.py CROWN)."""
    out = {}
    for (x, y), c in des.items():
        right = 0 if y <= -25 else 2 if y <= -23 else 3 if y == -22 else 6 if y <= -14 else 2
        if (-27 <= y <= -12 and -5 <= x <= right and rgb(c) not in POD) or (y == -11 and rgb(c) == (0xFC, 0xDD, 0xCD)):
            out[(x, y)] = c
    return out


DASH_SHIFT = 2
# the death from frame 3 on the idle's own body (tools/art/kaisa_death.py): Codex drew an older model there (the user:
# 「死亡时候的脸也不对 身体还是原版的？」)
DEATH = {3: ("kneel", 6), 4: ("kneel", 7), 5: ("slump", 9), 6: ("lying", 0), 7: ("lying", 0), 8: ("lying", 0)}
IDLE_ARM = {"hit": "all", "dead": [1, 2]}       # Codex's arm there hangs as the idle's: the idle's own
WING_CUT = {("skill", 5): lambda x, y: y > -19 and x >= 6}


def ring_close(a, py):
    """One outline square on every open edge (4-neighbours) of the figure, none under the soles' row."""
    h, w = a.shape[:2]
    op = a[..., 3] > 0
    lit = op.copy()
    for y, x in zip(*np.nonzero(op)):
        if rgb(a[y, x]) in DARK:
            lit[y, x] = False
    need = np.zeros((h, w), bool)
    need[1:] |= lit[:-1]
    need[:-1] |= lit[1:]
    need[:, 1:] |= lit[:, :-1]
    need[:, :-1] |= lit[:, 1:]
    need &= ~op
    need[py + 12:] = False
    a[need] = INK + (255,)
    return int(need.sum())


def pieces_holes(a):
    """Clear squares walled in by the figure: lists of (y, x)."""
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
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if not (0 <= yy < h and 0 <= xx < w):
                    edge = True
                elif not op[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    q.append((yy, xx))
        if not edge:
            out.append(comp)
    return out
# the run's lifted back foot drawn by hand (Codex ended the back shin in a point, a peg leg in the review): a boot
# with its gold sole, as the idle's; {row from the pivot: (first column, squares)}
FEET = {("run", 3): {8: (-7, "affa"), 9: (-7, "aCba"), 10: (-6, "aa")},
        ("run", 6): {9: (-9, "affa"), 10: (-10, "aCbba"), 11: (-10, "aaaaa")},
        ("run", 7): {6: (-8, "afCa"), 7: (-8, "abba"), 8: (-7, "aa")}}
SKIN_K = {kcol(c) for c in "ltw"} | {(0xFE, 0xE4, 0xD3), (0xFD, 0xDF, 0xD2)}


def specks(a):
    """Codex's specks: loose crumbs (pieces under 12 squares: a pod's edge left by the head), the mouth's coral on the claws (no skin round it: the
    claws' magenta), grey on the face (skin round it: the skin)."""
    op = a[..., 3] > 0
    ps = pieces(op)
    big = max(len(p) for p in ps) if ps else 0
    n = 0
    for p in ps:
        if len(p) < 12 and len(p) < big:
            for y, x in p:
                a[y, x] = 0
            n += len(p)
    h, w = op.shape
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        c = rgb(a[y, x])
        near = [rgb(a[y + oy, x + ox]) for ox in (-1, 0, 1) for oy in (-1, 0, 1)
                if (ox or oy) and 0 <= y + oy < h and 0 <= x + ox < w and a[y + oy, x + ox, 3]]
        if c == kcol("v") and not any(q in SKIN_K for q in near):
            a[y, x] = krgba("e")
            n += 1
        elif c == kcol("A") and sum(q in SKIN_K for q in near) >= 2:
            a[y, x, :3] = Counter(q for q in near if q in SKIN_K).most_common(1)[0][0]
            n += 1
    return f", specks {n}" if n else ""


def eye_any(a, pivot):
    """The head's move by the near eye's white wherever the head went (a crouch, a fall): the topmost white square
    within 3 columns of the design's eye."""
    px, py = pivot
    ys, xs = np.nonzero((a[..., :3] == EYE_WHITE).all(-1) & (a[..., 3] > 0))
    cand = [(x - px, y - py) for y, x in zip(ys, xs) if abs(x - px - EYE_AT[0]) <= 3]
    if not cand:
        return None
    x, y = min(cand, key=lambda p: (p[1], p[0]))
    return int(x - EYE_AT[0]), int(y - EYE_AT[1])


def eye_offset(a, pivot):
    """Codex's head move from the design's: its near eye's top white square against the design's (EYE_AT)."""
    px, py = pivot
    ys, xs = np.nonzero((a[..., :3] == EYE_WHITE).all(-1) & (a[..., 3] > 0))
    cand = [(x - px, y - py) for y, x in zip(ys, xs) if abs(x - px - EYE_AT[0]) <= 3 and abs(y - py - EYE_AT[1]) <= 6]
    if not cand:
        return None
    x, y = min(cand, key=lambda p: (p[1], p[0]))
    return x - EYE_AT[0], y - EYE_AT[1]


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


def thin(pix):
    """Squares (x, y) -> colour thinned where 5+ thick: the layer next to the outside goes where a square within 2 of
    it lies THICK deep; the squares left on the new edge take the colour of the one taken off beside them."""
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
    gone = {p for p, v in d.items() if v == 1
            and max(d.get((p[0] + ox, p[1] + oy), 0) for ox in range(-2, 3) for oy in range(-2, 3)) >= THICK}
    out = {p: c for p, c in pix.items() if p not in gone}
    for p in list(out):
        for ox, oy in N4:
            n = (p[0] + ox, p[1] + oy)
            if n in gone:
                out[p] = pix[n]
                break
    return out


def idle_body(a, pivot, off, des, open_pods, cannon=False, idle_arm=False, wing_cut=None):
    """A standing frame: the idle's body (without its near arm; without its pods when Codex opened them) and Codex's
    squares outside it on the near side (and over the head with the pods open), moved back with Codex's head; the
    near arm drawn again along Codex's (its cannon in W kept as drawn, the upper arm drawn to it)."""
    px, py = pivot
    dx, dy = off
    h, w = a.shape[:2]
    pods = pod_squares(des) if open_pods else set()
    body = {(x, y): c for (x, y), c in des.items() if (idle_arm or not near_arm(x, y)) and (x, y) not in pods}
    if open_pods:                                # outline left with nothing to outline (the crown's, by the pods)
        for _ in range(2):
            for (x, y), c in list(body.items()):
                if y > -17 or rgb(c) not in DARK:
                    continue
                lit = any((x + ox, y + oy) in body and rgb(body[(x + ox, y + oy)]) not in DARK
                          for ox in (-1, 0, 1) for oy in (-1, 0, 1) if ox or oy)
                n4 = sum((x + ox, y + oy) in body for ox, oy in N4)
                if not lit or n4 <= 1:           # an orphan, or a 1-square spike
                    del body[(x, y)]
    seen = np.zeros((h, w), bool)
    for (x, y) in body:
        if 0 <= py + y + dy < h and 0 <= px + x + dx < w:
            seen[py + y + dy, px + x + dx] = True
    dark = np.array([[rgb(a[y, x]) in DARK for x in range(w)] for y in range(h)])
    # Codex shades her gauntlets with the near-blacks too: every square outside the idle's body counts, and only the
    # dark ring round it (Codex's own outline, drawn again below) goes
    extra = (a[..., 3] > 0) & ~grow(seen)
    rim = extra & dark & grow(~extra & ~seen | (a[..., 3] == 0))
    extra &= ~rim
    keep = np.zeros((h, w), bool)
    for y in range(h):
        for x in range(w):
            if extra[y, x] and (x - px > dx + 1 or (open_pods and y - py <= -12 + dy)):
                keep[y, x] = True
    arm, wings, limb = {}, {}, {}
    for comp in pieces(keep):
        # a piece mostly of near-blacks is a leftover of Codex's own outline (the opened pods' base), not a limb
        if len(comp) < 4 or sum(dark[p] for p in comp) > 0.7 * len(comp):
            continue
        pix = {(x - px - dx, y - py - dy): a[y, x].copy() for y, x in comp}
        top = min(y for _, y in pix)
        if open_pods and top <= -16:
            wings.update(pix)                   # the opened pods: Codex's shapes as drawn
        elif not idle_arm:
            limb.update(pix)
    if limb:
        if cannon:
            arm.update(limb)
            near = min(limb, key=lambda p: (p[0] - SHOULDER_K[0]) ** 2 + (p[1] - SHOULDER_K[1]) ** 2)
            steps = max(abs(near[0] - SHOULDER_K[0]), abs(near[1] - SHOULDER_K[1]))
            if steps > 1:
                lead = [(int(round(SHOULDER_K[0] + (near[0] - SHOULDER_K[0]) * k / steps)),
                         int(round(SHOULDER_K[1] + (near[1] - SHOULDER_K[1]) * k / steps))) for k in range(steps + 1)]
                for (x, y), c in FR.draw_arm(lead, {}, "front", mats={k: KMAT["upper"] for k in KMAT},
                                             bracer=K_BRACER, skin=K_SKIN, rgba=krgba).items():
                    arm.setdefault((x, y), c)
        else:
            line = FR.arm_line(set(limb), SHOULDER_K)
            arm.update(FR.draw_arm(line, limb, "front", mats=KMAT, bracer=K_BRACER, skin=K_SKIN, rgba=krgba))
    # where the pods were, Codex's wing roots (the head joined to its wings)
    # (only squares joined to a wing, grown from it; the crown under the near pod goes with the pod: no spike)
    grew = True
    while grew:
        grew = False
        for (x, y) in pods - NOTCH:
            if (x, y) in wings or not (0 <= py + y + dy < h and 0 <= px + x + dx < w):
                continue
            c = a[py + y + dy, px + x + dx]
            if c[3] and rgb(c) not in DARK and any((x + ox, y + oy) in wings for ox in (-1, 0, 1) for oy in (-1, 0, 1)):
                wings[(x, y)] = c.copy()
                grew = True
    if wing_cut is not None:                    # a closing pod's loose strip hanging by the face (Q 5)
        wings = {xy: c for xy, c in wings.items() if not wing_cut(*xy)}
    out = np.zeros_like(a)

    def lay(cells, over):
        m = np.zeros((h, w), bool)
        for (x, y) in cells:
            if 0 <= py + y < h and 0 <= px + x < w:
                m[py + y, px + x] = True
        for y, x in zip(*np.nonzero(grow(m) & ~m)):
            if not out[y, x, 3] or over:
                out[y, x] = INK + (255,)
        for (x, y), c in cells.items():
            if 0 <= py + y < h and 0 <= px + x < w:
                out[py + y, px + x] = c

    lay(wings, False)
    for (x, y), c in body.items():
        out[py + y, px + x] = c
    lay(arm, True)
    return out


def pockets(a, feet):
    """The pockets of ground walled in once the outline is closed as the importer closes it: lists of (y, x)."""
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
        for dy, dx in N4:
            q = (y + dy, x + dx)
            if q in inside:
                continue
            c = b[q]
            if c[3] and rgb(c) != INK:
                walls[tuple(int(v) for v in c)] += 1
    return np.array(walls.most_common(1)[0][0], np.uint8) if walls else np.array(INK + (255,), np.uint8)


def fill_pockets(a, pivot, des, standing):
    px, py = pivot
    comps, closed = pockets(a, py + 11)
    n = 0
    for comp in comps:
        if standing and len(comp) <= BODY_POCKET:
            for (y, x) in comp:
                c = des.get((x - px, y - py))
                a[y, x] = c if c is not None and rgb(c) != INK else wall_colour(closed, comp)
            n += len(comp)
        elif len(comp) <= POCKET:
            col = wall_colour(closed, comp)
            for (y, x) in comp:
                a[y, x] = col
            n += len(comp)
    return n


def chosen(table, tag, k):
    v = table.get(tag)
    return v == "all" or (v is not None and k + 1 in v)


def build():
    with open(lp(os.path.join(SRC, "kaisa_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)                    # Codex's table: R as one 4-frame strip
    with open(lp(os.path.join(NAT, "kaisa_cells.json")), encoding="utf-8") as f:
        game = json.load(f)                     # the game's: ult 1-3, ult_dash 1
    cell = cells["cell"][:2]
    des = design()
    head = head_squares(des)
    out, log = {}, []
    for tag in TAGS:
        frs = cells["tags"][tag]
        frames = cells_of(os.path.join(SRC, f"kaisa_{tag}.png"), len(frs), cell)
        if tag == "idle":                       # the design itself on every pivot (the pack's idle is the design
            frames = []                         # before its crown)
            for fr in frs:
                f = np.zeros((cell[1], cell[0], 4), np.uint8)
                for (x, y), c in des.items():
                    f[fr["pivot"][1] + y, fr["pivot"][0] + x] = c
                frames.append(f)
        done = []
        for k, (f, fr) in enumerate(zip(frames, frs)):
            piv = fr["pivot"]
            a = f.copy()
            off = eye_offset(a, piv) if tag != "idle" else (0, 0)
            note = "as drawn"
            if tag == "idle":
                note = "design"
            elif tag == "dead" and k + 1 in DEATH:
                kind, ddy = DEATH[k + 1]
                a = KD.frame(kind, des, piv, a.shape, krgba, np.array(INK + (255,), np.uint8), head,
                             pod_squares(des), ddy)
                note = f"death drawn on the idle: {kind} {ddy}"
            elif chosen(IDLE_BODY, tag, k):
                a = idle_body(a, piv, off or (0, 0), des, chosen(OPEN_PODS, tag, k), chosen(CANNON, tag, k),
                              chosen(IDLE_ARM, tag, k), WING_CUT.get((tag, k + 1)))
                note = f"idle body (Codex's head {off})"
            elif chosen(HEAD_LOCK, tag, k) and eye_any(a, piv) is not None:
                # the idle's head as it is - the pods, the crown, the hair over the shoulders, the face - over
                # Codex's (its own pods sat further back and higher, its fringe stuck out, grey specks in the faces)
                off = eye_any(a, piv)
                px, py = piv
                if True:
                    top = {xy: c for xy, c in des.items() if xy[1] <= -17}
                    top.update(head)
                    txs = [x for x, _ in top]
                    for y in range(-36, -16):    # Codex's head over the shoulders row by row, its pods' tips above
                        yy = py + y + off[1]
                        xs_ = txs
                        if 0 <= yy < a.shape[0]:
                            a[yy, max(0, px + min(xs_) - 1 + off[0]):px + max(xs_) + 2 + off[0]] = 0
                if tag == "run":
                    # the long hair down her back as the idle's too: Codex's swung out further and darker (the user:
                    # 「卡莎的发型怪异」); its hair and outline left of the body go, the design's hair takes their place
                    hairc = {kcol(ch) for ch in "jgkc"} | DARK
                    for y in range(-17, 3):
                        for x in range(-20, -5):
                            yy, xx = py + y + off[1], px + x + off[0]
                            if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and a[yy, xx, 3] \
                                    and rgb(a[yy, xx]) in hairc:
                                a[yy, xx] = 0
                    top.update({(x, y): c for (x, y), c in des.items()
                                if -17 <= y <= 2 and x <= -6 and rgb(c) in hairc})
                for (x, y), c in top.items():
                    a[py + y + off[1], px + x + off[0]] = c
                note = f"design head at {off}"
            if (tag, k + 1) in RAISE:
                r = RAISE[(tag, k + 1)]
                a = np.concatenate([a[r:], np.zeros_like(a[:r])])
                note += f", up {r}"
            if (tag, k + 1) in FEET:                # hand-drawn: the lifted back foot Codex ended in a point
                px, py = piv
                for row, (x0, s) in FEET[(tag, k + 1)].items():
                    for j, ch in enumerate(s):
                        if ch != ".":
                            a[py + row, px + x0 + j] = krgba(ch)
                note += ", foot drawn"
            if tag != "idle":
                note += specks(a)
                note += f", ring {ring_close(a, piv[1])}"
                for comp in pieces_holes(a):    # a slit the ring walled in: outline
                    if len(comp) <= POCKET:
                        for (y, x) in comp:
                            a[y, x] = INK + (255,)
            n = fill_pockets(a, piv, des, chosen(IDLE_BODY, tag, k) or tag == "idle")
            done.append(a)
            log.append(f"{tag} {k + 1}: {note}, pockets {n}")
        out[tag] = done
    out["ult_dash"] = out["ult"][3:]
    out["ult"] = out["ult"][:3]
    # the dash reached the frame's edge (no room for its outline behind the feet): two squares forward
    out["ult_dash"][0] = np.concatenate([np.zeros_like(out["ult_dash"][0][:, :DASH_SHIFT]),
                                         out["ult_dash"][0][:, :-DASH_SHIFT]], axis=1)
    for tag in out:
        assert len(out[tag]) == len(game["tags"][tag]), tag
        for k, fr in enumerate(game["tags"][tag]):
            src = cells["tags"]["ult"][k + (3 if tag == "ult_dash" else 0)] if tag in ("ult", "ult_dash") \
                else cells["tags"][tag][k]
            assert src["pivot"] == fr["pivot"], (tag, k)
    return out, game, log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out, game, log = build()
    for line in log:
        print(line)
    cell = game["cell"][:2]
    bad = 0
    for tag, frames in out.items():
        s = sheet_of(frames, cell)
        path = os.path.join(NAT, f"kaisa_{tag}.png")
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

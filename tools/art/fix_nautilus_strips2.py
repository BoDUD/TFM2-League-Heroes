#!/usr/bin/env python3
"""Nautilus's action strips from Codex's side-on redraw (step 2 again: tools/art/pack_nautilus_strips2.py,
MODEL_STRIPS2.md; delivered 2026-10-11 as nautilus_strips_pack_done.zip, kept in assets/source/nautilus/codex_strips2:
the 1x strips, nautilus_cells.json, manifest, HANDOFF; the raw generations stay in the user's Codex outputs).

    python tools/art/fix_nautilus_strips2.py [--check]

The user: 「完成泰坦吧 有问题的地方你帮我修复 做到完美版了再喊我review」. Codex's strips are side-on like the pack's other
heroes and oppi's sprites (the body and the helmet turned to the right, a crossing run, the anchor carried and swung
whole); what is fixed here:
  1. attack and skill: the bronze one step brighter than every other strip (#FDCC31 light, #F94102 mid-dark): yellow ->
     #FAAC2A, orange-red -> #A84217, #A84217 -> #8C3815, except the eyes (red #E4221F and what touches it);
  2. skill: single red squares Codex left on the body (knee guards, shoulders, boots) - a red square touching the bronze
     and no anchor grey, not one of the eyes - become #A84217;
  3. ult 3 (Codex's body curled into a ball) is skill 3 (the anchor drawn back behind his head); ult 5-6 (shrunk into
     a ball, the anchor flattened under him) are the attack's lunge (attack 4: the anchor out in front at knee height);
     ult 7 (the anchor overlapping his body) is the attack's recovery (attack 5) - each with its own standing point;
  4. dead 2-8: Codex drew another anchor (a ring on top, a thin stock, small flukes) standing beside him; it goes
     (every square left of a per-row boundary, B) and the anchor he carries everywhere else (attack 5's, cut above the
     fist) stands on its crown in its place, behind him, the outline closed (rigkit.finish).
  5. the anchor carried on his back: Codex's bent one out, the design's straight anchor unit in, held in the near fist
     (CARRY); frames whose anchor cannot take it (the attack's first and last, Q's landing, R's first, the hit's first)
     are the mended stance (GRIP_FROM).
  6. the run trades legs every half cycle: Codex's hips and legs of frames 1-3 whole, the 4th passing (frame 4's
     straight leg and the other one lifted behind it), then the same with the other leg near (the far leg one step
     darker, on whole patches).
  7. the run's body is frame 1's in every frame, its belt on each frame's own belt: Codex's redrawn bodies shook.
  8. the idle (side-on too, the user: 「待机图也改成侧面的吧 不然太奇怪了」) stands upright like oppi's Nautilus: the run's
     body and hip (its size) on frame 4's straight leg and a darker copy of it behind, standing still.
  9. the carried anchor is Codex's own straight one, attack 4's turned crown up (「钩子画的过大了 适当缩小」
     「武器给我画直了啊」).
Writes assets/source/native/nautilus_<tag>.png (8x) and nautilus_cells.json; then
python tools/art/import_native.py --hero nautilus.
"""
import argparse
import json
import math
import os
import sys
from collections import deque

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import rig_nautilus as RN  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nautilus", "codex_strips2")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
TAGS = ["idle", "run", "attack", "skill", "skill_pull", "skill2", "ult", "hit", "dead"]
Z = 8
D = K.Design(RN.DESIGN)
L = D.letters()
INV = {c: k for k, c in L.items()}
OUT = tuple(int(v) for v in D.outline)
BRONZE, GREY = set("tpkjhmuo"), set("nsv")


def cols_of(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def cell(k, n, cw, ch):
    c = cols_of(n)
    return slice((k // c) * ch, (k // c + 1) * ch), slice((k % c) * cw, (k % c + 1) * cw)


def is_(a, ch):
    return np.all(a[..., :3] == L[ch], -1) & (a[..., 3] > 0)


def near(m):
    out = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def bronze_down(a):
    """1: u -> t, m -> k, k -> j outside the eyes (red squares and what touches them)."""
    eyes = near(is_(a, "l"))
    u, m, k = is_(a, "u") & ~eyes, is_(a, "m") & ~eyes, is_(a, "k")
    a[k, :3] = L["j"]
    a[m, :3] = L["k"]
    a[u, :3] = L["t"]


def red_specks(f):
    """2: red squares on the body (touching bronze, no grey) that are not the eyes -> k. The eyes: the biggest red
    piece in the face rows (60-82) and a piece beside it on the right (the far eye) within 8 columns."""
    lm = is_(f, "l")
    lab, n = ndimage.label(lm, np.ones((3, 3)))
    face = [(int((lab == i).sum()), i) for i in range(1, n + 1) if 60 <= np.nonzero(lab == i)[0].min() <= 82]
    keep = set()
    if face:
        eye = max(face)[1]
        ey, ex = np.nonzero(lab == eye)
        keep.add(eye)
        for i in range(1, n + 1):
            ys, xs = np.nonzero(lab == i)
            if abs(ys.min() - ey.min()) <= 2 and 0 < xs.min() - ex.max() <= 8:
                keep.add(i)
    for y, x in zip(*np.nonzero(lm)):
        if lab[y, x] in keep:
            continue
        nb = {INV.get(tuple(int(v) for v in f[yy, xx, :3])) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
              if (yy, xx) != (y, x) and f[yy, xx, 3]}
        if nb & BRONZE and not nb & GREY:
            f[y, x, :3] = L["k"]


FOUR = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
WARM = "utpomkjhecl"                                            # the bronze ramp and the red


def darkened(part):
    step = {"v": "s", "s": "n", "n": "i", "i": "f"}
    u = part.s.copy()
    for y, x in zip(*np.nonzero(u[..., 3])):
        ch = INV.get(tuple(int(v) for v in u[y, x, :3]))
        if ch in step:
            u[y, x, :3] = L[step[ch]]
    return K.Part(u, part.j)


def straight_anchor(f4):
    """9: the anchor he carries - Codex's own, straight and even (attack frame 4 holds it level before him, the crown
    the same above and below the shank), from its red band to the crown (ANCHOR4), turned a quarter (crown up); the
    shank run on straight down to the design's near fist (darkened), the crown as high over the fist as the design's
    was."""
    r0, r1, c0, c1 = ANCHOR4
    head = np.rot90(f4[r0:r1, c0:c1], 1).copy()
    fist = darkened(RN.Parts().unit).s[FIST_ROWS[0]:FIST_ROWS[1]]
    H, W = FIST_AT + fist.shape[0], head.shape[1]
    u = np.zeros((H, W, 4), np.uint8)
    u[:head.shape[0]] = head
    shank = head[SHANK_ROW:SHANK_ROW + 1].copy()
    shank[0, :SHANK_COLS[0]] = 0
    shank[0, SHANK_COLS[1] + 1:] = 0
    for r in range(head.shape[0] - 1, FIST_AT + 1):
        K.put(u, shank, 0, r)
    K.put(u, fist, FIST_DX, FIST_AT)
    return K.Part(u, (8.0 + FIST_DX, 31.5 - FIST_ROWS[0] + FIST_AT))


def helmet_top(f):
    """The helmet: the biggest piece of light bronze; its top row and its leftmost square there."""
    br = is_(f, "t") | is_(f, "p") | is_(f, "k") | is_(f, "o") | is_(f, "u")
    lab, n = ndimage.label(br, np.ones((3, 3)))
    sizes = ndimage.sum(br, lab, range(1, n + 1))
    ys, xs = np.nonzero(lab == 1 + int(np.argmax(sizes)))
    top = ys.min()
    return top, xs[ys == top].min()


def carry(f, B, F, unit, old=None):
    """5: Codex's carried anchor out, the design's anchor unit in (see CARRY); `old`: a box (rows, columns) where Codex's
    old shank still runs beside the new one, cleared outside the unit (OLD_SHANK)."""
    op = f[..., 3] > 0
    outl = is_(f, "0")
    bronze = np.zeros_like(op)
    for c in "tpkouhje":
        bronze |= is_(f, c)
    red = is_(f, "l") | is_(f, "m")
    top, hl = helmet_top(f)
    lab, n = ndimage.label(op & ~outl & ~bronze & ~red, FOUR)
    gone = np.zeros_like(op)
    br = is_(f, "t") | is_(f, "p") | is_(f, "k") | is_(f, "o") | is_(f, "u")
    bl, bn = ndimage.label(br, np.ones((3, 3)))
    helm = bl == 1 + int(np.argmax(ndimage.sum(br, bl, range(1, bn + 1))))
    touch = ndimage.binary_dilation(helm, np.ones((3, 3)), iterations=2)   # the hood touches the helmet's bronze
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        # the crown's pieces: wholly over the helmet's top, or reaching down beside it without touching its bronze -
        # never the dark hood at the back of the helmet (taken with them once: 「头部有模型失去像素啊」)
        if ys.min() < top and (ys.max() < top + 2 or not (touch & (lab == i)).any()):
            gone |= lab == i
    by, bx = int(round(B[0])), int(round(B[1]))
    rl, _ = ndimage.label(red, np.ones((3, 3)))
    if rl[by, bx]:
        gone |= rl == rl[by, bx]
    for dy in range(1, 6):                                # the shank's piece under the band
        for dx in range(-2, 4):
            i = lab[by + dy, bx + dx]
            if i and not gone[by + dy, bx + dx]:
                ys, xs = np.nonzero(lab == i)
                if ys.max() <= top + 12 and xs.max() <= hl + 6:
                    gone |= lab == i
    rows, cols = np.mgrid[0:128, 0:128]
    gone |= op & ~outl & ~bronze & (rows < top - 1) & (cols < hl - 2)   # the crown's rope above the helmet
    g = f.copy()
    g[gone] = 0
    solid = (g[..., 3] > 0) & ~is_(g, "0")
    near_solid = ndimage.convolve(solid.astype(int), np.ones((3, 3), int), mode="constant") > 0
    # only the old anchor's own outline: squares next to what went (a visor's dark squares border only dark too)
    g[outl & ~near_solid & ndimage.binary_dilation(gone, np.ones((3, 3)))] = 0
    g = mend_gaps(g, top, hl)
    if old is not None:
        r0, r1, c0, c1 = old
        g[r0:r1 + 1, c0:c1 + 1] = 0
    # the anchor over his shoulder: behind the body (only where nothing is drawn), the fist round its shank on top;
    # over the helmet nothing of Codex's stays where the new anchor goes (his rope's last squares showed through)
    where = np.zeros_like(g)
    K.place(where, unit, (F[1], F[0]))
    g[(where[..., 3] > 0) & (np.arange(g.shape[0]) < top)[:, None]] = 0
    K.place(g, unit, (F[1], F[0]), under=True)
    fist = unit.s.copy()
    fist[:FIST_AT] = 0
    K.place(g, K.Part(fist, unit.j), (F[1], F[0]))
    # Codex's old flukes and the rope's knot left warm squares (bronze, red) by the new anchor's left fluke
    # (「还有多余的像素没清理」): small warm pieces outside the unit, left of its shank and above the fist, touching it
    # and hanging out of the figure (the air at most 2 squares off) go, with the outline that bordered only them
    foot = np.zeros_like(g)
    K.place(foot, unit, (F[1], F[0]))
    fm = foot[..., 3] > 0
    warm = np.zeros_like(fm)
    for c in WARM:
        warm |= is_(g, c)
    warm &= ~fm
    near_unit = ndimage.binary_dilation(fm, np.ones((5, 5), bool))
    air = ndimage.binary_dilation(g[..., 3] == 0, FOUR, iterations=2)
    lab, n = ndimage.label(warm, FOUR)
    stray = np.zeros_like(fm)
    for i in range(1, n + 1):
        piece = lab == i
        ys, xs = np.nonzero(piece)
        if (piece.sum() <= 12 and (piece & near_unit).any() and (piece & air).any() and xs.max() < round(F[1])
                and ys.max() < F[0] - 3):
            stray |= piece
    g[stray] = 0
    colour = ndimage.binary_dilation((g[..., 3] > 0) & ~is_(g, "0"), np.ones((3, 3), bool))
    g[is_(g, "0") & ~colour & ndimage.binary_dilation(stray, np.ones((3, 3), bool))] = 0
    lab2, n2 = ndimage.label(g[..., 3] > 0, np.ones((3, 3)))
    if n2 > 1:
        sizes = ndimage.sum(g[..., 3] > 0, lab2, range(1, n2 + 1))
        g[(lab2 != 1 + int(np.argmax(sizes))) & (lab2 > 0)] = 0
    return tidy(g)


def tidy(c):
    """The outline closed round the silhouette (strips.complete_outline) and crumbs under 3 squares dropped - nothing
    inside repainted: rigkit.finish took the visor's dark squares for orphan outline and filled them grey."""
    out, _, _ = K.strips.complete_outline(c, color=OUT, dark=70, feet=RN.PIVOT[1] + 11)
    out[RN.PIVOT[1] + 12:] = 0
    for comp in K.pieces(out)[1:]:
        if len(comp) < 3:
            for y, x in comp:
                out[y, x] = 0
    # a coloured square touching the figure only by a corner (the rope Codex tied to the old anchor's crown left two
    # such orange squares beside the new one: 「还有多余的像素没清理」)
    op = out[..., 3] > 0
    p = np.pad(op, 1)
    sides = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
    out[op & (sides == 0) & ~is_(out, "0")] = 0
    return out


def mend_gaps(g, top, hl):
    """Squares the old shank left clear at the back of the helmet (open notches between the hood and the shank): the
    body's mask closed (5x5) in a box round the helmet's back, each new square the commonest colour of its
    neighbours, from the edge in."""
    box = np.zeros(g.shape[:2], bool)
    box[max(top - 3, 0):top + 16, max(hl - 8, 0):hl + 10] = True
    op = g[..., 3] > 0
    closed = ndimage.binary_closing(op, np.ones((5, 5)), iterations=1) & box & ~op
    for _ in range(8):
        if not closed.any():
            break
        for y, x in zip(*np.nonzero(closed)):
            nb = [tuple(int(v) for v in g[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if g[yy, xx, 3] and not np.array_equal(g[yy, xx, :3], OUT)]
            if len(nb) >= 2:
                g[y, x] = max(set(nb), key=nb.count)
                closed[y, x] = False
    return g


def lower(f, belt):
    """6: Codex's hips and legs, every row under the belt; and apart, the pieces there that never reach the feet (the
    near fist's lowest squares)."""
    part = f.copy()
    part[:belt + 1] = 0
    lab, m = ndimage.label(part[..., 3] > 0, FOUR)
    bits = np.zeros(part.shape[:2], bool)
    for i in range(1, m + 1):
        if np.nonzero(lab == i)[0].max() < SEP_ROW:
            bits |= lab == i
    rest = part.copy()
    rest[~bits] = 0
    part[bits] = 0
    return part, rest


def solid_of(p):
    return (p[..., 3] > 0) & ~is_(p, "0")


def legs_of(part):
    """6: the back leg's and the front leg's squares from TONE_ROW down: the two biggest pieces standing apart from
    SEP_ROW down, grown up through the thighs (each square to the nearer one, stepping through coloured squares)."""
    low = solid_of(part)
    low[:SEP_ROW] = False
    lab, m = ndimage.label(low, FOUR)
    big = sorted(range(1, m + 1), key=lambda i: (lab == i).sum())[-2:]
    big.sort(key=lambda i: np.nonzero(lab == i)[1].mean())
    sol = solid_of(part)
    sol[:TONE_ROW] = False
    owner = np.zeros(sol.shape, int)
    queue = deque()
    for who, i in ((1, big[0]), (2, big[1])):
        for y, x in zip(*np.nonzero((lab == i) & sol)):
            owner[y, x] = who
            queue.append((y, x))
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if sol[y + dy, x + dx] and not owner[y + dy, x + dx]:
                owner[y + dy, x + dx] = owner[y, x]
                queue.append((y + dy, x + dx))
    return owner == 1, owner == 2, lab == big[0], lab == big[1]


def toned(p, mask):
    out = p.copy()
    for y, x in zip(*np.nonzero(mask)):
        ch = INV.get(tuple(int(v) for v in p[y, x, :3]))
        if ch in FAR:
            out[y, x, :3] = L[FAR[ch]]
    return out


def far_patches(p, far, near):
    """6: the far leg's tone goes on whole patches of one colour family (a knee guard, a boot, a highlight) lying
    mostly in the far leg - never half a knee guard."""
    letters = np.full(p.shape[:2], "", dtype=object)
    for y, x in zip(*np.nonzero(p[..., 3])):
        letters[y, x] = INV.get(tuple(int(v) for v in p[y, x, :3]), "?")
    mask = np.zeros(p.shape[:2], bool)
    for fam in FAMILIES:
        lab, m = ndimage.label(np.isin(letters, list(fam)), FOUR)
        for i in range(1, m + 1):
            patch = lab == i
            if (patch & far).sum() > (patch & near).sum():
                mask |= patch
    return mask


def leg_unit(part, mask):
    """The leg's squares and the outline squares touching them."""
    outline = (part[..., 3] > 0) & is_(part, "0")
    m = mask | (outline & ndimage.binary_dilation(mask, np.ones((3, 3), bool)))
    u = np.zeros_like(part)
    u[m] = part[m]
    return u


def stance(leg, hip, near, lift):
    """8 (and the run's passing frames): Codex's straight leg `leg` (frame 4's front one, in frame 1's place) and the
    same leg IDLE_FEET columns behind it, one step darker; the swing leg (the one behind) lifted `lift` rows, tucked
    under the hip; `near` "front" (the straight one near) or "back" (the swing one near, in Codex's colours, over the
    other); frame 1's hip on top."""
    swing = K.shifted(leg, -IDLE_FEET, -lift)
    swing[:HIP_END + 1] = 0
    far, nr = (swing, leg) if near == "front" else (leg, swing)
    out = np.zeros_like(leg)
    K.put(out, toned(far, solid_of(far)), 0, 0)
    K.put(out, nr, 0, 0)
    K.put(out, hip, 0, 0)
    return out


def leg_units(f, belt, pivot_x, ref_x):
    """8: one of Codex's run frames cut into its two whole legs ({"B": back, "F": front}): its squares under the belt
    (lower), told apart where they stand apart and grown up through the thighs (legs_of), each with the outline squares
    touching it; moved under frame 1's belt (its own belt to BELT[0], its standing point to ref_x)."""
    part, _ = lower(f, belt)
    back_m, front_m = legs_of(part)[2:]
    solid = solid_of(part)
    lab, _ = ndimage.label(solid, FOUR)
    out = {}
    for name, seed in (("B", back_m), ("F", front_m)):
        whole = np.isin(lab, np.unique(lab[seed & solid]))
        out[name] = K.shifted(leg_unit(part, whole), int(ref_x - pivot_x), BELT[0] - belt)
    return out


def on_ground(u, dx):
    """A leg unit moved dx columns, its lowest square on the soles' row."""
    ys = np.nonzero(u[..., 3])[0]
    return K.shifted(u, dx, RN.PIVOT[1] + 11 - ys.max())


def bounds(spec):
    return {r: c for r0, r1, c in spec for r in range(r0, r1 + 1)}


# 4: per death frame, the columns left of which every square is Codex's other anchor (rows: first, last, column)
DEAD_B = {2: bounds([(0, 68, 51), (69, 70, 53), (71, 71, 55), (72, 72, 54), (73, 127, 53)]),
          3: bounds([(0, 81, 59), (82, 127, 60)]),
          4: bounds([(0, 127, 60)]),
          5: bounds([(0, 73, 70), (74, 77, 69), (78, 92, 66), (93, 127, 73)]),
          6: bounds([(0, 73, 68), (74, 88, 65), (89, 92, 66), (93, 93, 70), (94, 94, 71), (95, 95, 72),
                     (96, 97, 73), (98, 127, 74)]),
          7: bounds([(0, 74, 59), (75, 79, 56), (80, 80, 57), (81, 88, 56), (89, 92, 57), (93, 94, 59), (95, 95, 61),
                     (96, 96, 62), (97, 127, 63)])}
DEAD_B[8] = DEAD_B[7]
DEAD_LEFT = {2: 23, 3: 34, 4: 28, 5: 49, 6: 47, 7: 42, 8: 42}   # the new anchor's left column (its crown on the soles)
ANCHOR_BOX = (40, 58, 28, 60)                                   # attack 5: rows, columns of the anchor above the fist
# 3: ult frames taken from other strips (ult frame <- (tag, frame)), 1-based
# 5: the anchor carried on his back looked stuck in his helmet and, drawn on, crooked (the user: 「武器没拿在手里 看起来像是插在
# 脑袋里了？」「武器别歪啊」「还是歪的吧」): Codex's carried anchor bends (a slanted crown, a shank curving into the back of
# the helmet), so it is taken out square by square - the crown's pieces, the red band at B and the shank's piece under it,
# outline squares left bordering only air; the helmet untouched - and the design's own anchor unit goes in (anchor + near
# fist, rigid, upright: the crown over his head, the straight shank down into the fist, as p35 carries it), one step
# darker to Codex's anchor greys, its fist on Codex's near fist F (rows, columns).
CARRY = {("run", 1): ((59, 51), (80, 57.1)), ("run", 2): ((58.5, 50.5), (79.5, 55.8)),
         ("run", 3): ((59.5, 51.5), (80, 55.5)), ("run", 4): ((59.2, 52.5), (80.2, 58.0)),
         ("run", 5): ((60.5, 52.5), (81.2, 58.4)), ("run", 6): ((58.9, 54.7), (79.2, 58.2)),
         ("run", 7): ((59.5, 49.5), (77.9, 55.1)), ("run", 8): ((56.5, 53.5), (77.2, 58.2)),
         ("skill2", 1): ((63, 52), (82, 58.9)), ("skill2", 5): ((63, 52), (82, 60.4)),
         ("skill2", 6): ((60, 50), (82, 58.6)), ("hit", 2): ((56, 49.3), (80, 58.6)), ("ult", 8): ((62.1, 54.3), (78.4, 61.2))}
# 9: the carried anchor was too big (「钩子画的过大了 适当缩小」), then crooked (「武器给我画直了啊」: the design's crown
# leans to the right of its shank). It is Codex's own anchor now, the one he swings (straight_anchor): attack 4's,
# rows/columns ANCHOR4 (red band to crown tip), turned a quarter; its shank's cross-section (row SHANK_ROW of the turned
# piece, columns SHANK_COLS) run down to the design's near fist (its rows FIST_ROWS) set FIST_DX columns over at row
# FIST_AT.
ANCHOR4 = (63, 96, 91, 108)
SHANK_ROW = 12
SHANK_COLS = (13, 19)
FIST_ROWS = (29, 34)
FIST_DX = 7
FIST_AT = 31
# W+E's last frame: Codex's old shank ran on down beside the new one to the fist, a light grey bar left of it (rows,
# columns, both ends in); cleared before the unit goes in
OLD_SHANK = {("skill2", 6): (64, 73, 52, 58)}
# (tag, frame) <- the mended W+E stance (the idle's), or the mended hit 2 a column back
GRIP_FROM = {("attack", 1): ("skill2", 1, 0), ("attack", 6): ("skill2", 1, 0), ("skill_pull", 4): ("skill2", 1, 0),
             ("ult", 1): ("skill2", 1, 0), ("hit", 1): ("hit", 2, -1)}
# 6: the run never changed legs (「走路压根看不出换腿」): Codex drew one stride and kept the same leg in front in all 8
# frames - 1 the stride, 2 the back foot down behind, 3-4 the front leg straight under him and the back one lifted
# behind. Frames 5-8 as 1-4 with only the legs' tones swapped made the back leg jump to the front in one frame,
# glaring yellow over a black one (「这交叉步看着好怪啊」); cutting the legs apart along columns then broke the thighs
# and left squares behind (「走路时下半身有点变形 还有多余的像素没清理」). The cycle now: 1-3 Codex's own hips and legs,
# whole, under frame 1's body (7), the far leg one step darker (FAR, on whole patches: far_patches); 4 frame 4's
# straight leg and the other leg passing behind it, lifted PASS_LIFT rows (stance()); 5-8 the same with the other leg
# near. Each leg goes forward, under him, behind, lifted, passing, forward again. The legs are told apart where they
# stand apart (from SEP_ROW down) and grown up through the thighs to TONE_ROW; the hips above stay as drawn.
SEP_ROW = 93
TONE_ROW = 90
PASS_LIFT = 2
FAR = {"u": "t", "t": "p", "p": "k", "o": "k", "m": "k", "k": "j", "j": "h", "h": "e", "e": "c", "c": "b",
       "v": "s", "s": "n", "n": "i", "i": "f"}
FAMILIES = (set("utpomkjhec"), set("vsni"))
# 7: the run shook (「走路时模型抖动太厉害」): Codex redrew the upper body in every frame (the helmet 3 columns and 2 rows
# apart) and the carried anchor rode the fist. Every frame wears frame 1's body (every row down to its belt - the teal
# light - and the near fist's lowest squares), its belt on the frame's own belt (BELT, Codex's run frames 1-4): the
# body bobs a row with Codex's hips and nothing is cut through them.
BELT = [85, 84, 84, 84]
# 8: the idle (「待机时上下浮动模型还变形 我的意思是待机时腿不要岔开啊 直立站那不就行了 你看oppi的泰坦啊」「现在明显待机和走路时
# 模型尺寸都不一样了」, then 「待机一样的问题」): like oppi's Nautilus, upright on two straight legs and still - frame 1's
# body and its hip (rows to HIP_END), frame 4's straight front leg from its thigh (THIGH4) down a row lower (the sole
# on the ground row), the far leg the same IDLE_FEET columns behind (its thigh under the back of the hip), one step
# darker. The run's size: the run's own body.
HIP_END = 87
THIGH4 = 87
IDLE_FEET = 7
# the idle's legs (「只是待机动作腿有问题」「你把待机动作的腿改好就行了啊」「大哥待机动作的腿弄直了啊」): run frame 4's
# front leg, the straight part from the thigh down, vertical, twice - the near one as drawn, the far one a step darker
# STAND_BACK columns behind (far enough for both boots to show) - both feet flat, side by side, not astride.
STAND_BACK = -8
ULT_FROM = {3: ("skill", 3), 5: ("attack", 4), 6: ("attack", 4), 7: ("attack", 5)}


def build():
    with open(os.path.join(SRC, "nautilus_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    strips = {t: np.asarray(Image.open(os.path.join(SRC, f"nautilus_{t}_1x.png")).convert("RGBA")).copy()
              for t in TAGS if t != "idle"}
    n = {t: len(cells["tags"][t]) for t in TAGS}
    for t in ("attack", "skill"):
        bronze_down(strips[t])
    for k in range(n["skill"]):
        red_specks(strips["skill"][cell(k, n["skill"], cw, ch)])
    for dst, (tag, src) in ULT_FROM.items():
        strips["ult"][cell(dst - 1, n["ult"], cw, ch)] = strips[tag][cell(src - 1, n[tag], cw, ch)]
        cells["tags"]["ult"][dst - 1]["pivot"] = list(cells["tags"][tag][src - 1]["pivot"])
    f5 = strips["attack"][cell(4, n["attack"], cw, ch)]
    r0, r1, c0, c1 = ANCHOR_BOX
    piece = np.zeros_like(f5)
    piece[r0:r1, c0:c1] = f5[r0:r1, c0:c1]
    ys, xs = np.nonzero(piece[..., 3] > 0)
    anchor = piece[ys.min():ys.max() + 1, xs.min():xs.max() + 1][::-1].copy()     # on its crown
    unit = straight_anchor(strips["attack"][cell(3, n["attack"], cw, ch)])
    for (tag, k), (B, F) in CARRY.items():
        sl = cell(k - 1, n[tag], cw, ch)
        strips[tag][sl] = carry(strips[tag][sl], B, F, unit, OLD_SHANK.get((tag, k)))
    # 6-7: the run - frame 1's body over each frame's own hips and legs, frames 4 and 8 passing (stance())
    first = [strips["run"][cell(k, n["run"], cw, ch)].copy() for k in range(4)]
    pivs = [list(cells["tags"]["run"][k]["pivot"]) for k in range(4)]
    if pivs[3][0] != pivs[0][0]:
        sys.exit("run frames 1 and 4 stand on different columns: stance() puts frame 4's leg under frame 1's body")
    fist = lower(first[0], BELT[0])[1]
    top = first[0].copy()
    top[BELT[0] + 1:] = 0
    K.put(top, fist, 0, 0)
    hip = first[0].copy()
    hip[:BELT[0] + 1] = 0
    hip[HIP_END + 1:] = 0
    hip[fist[..., 3] > 0] = 0
    parts = [lower(first[k], BELT[k])[0] for k in range(4)]
    legs = [legs_of(p) for p in parts]
    back_seed, front_seed = legs[3][2], legs[3][3]
    lab, _ = ndimage.label(solid_of(parts[3]), FOUR)
    whole = lab == lab[tuple(np.argwhere(front_seed)[0])]
    if (whole & back_seed).any():
        sys.exit("run frame 4's legs touch: stance() needs its front leg whole")
    leg = leg_unit(parts[3], whole)
    leg[:THIGH4] = 0
    leg = K.shifted(leg, 0, 1)                      # in frame 1's place (frame 4 floats a row: its belt on row 84)
    for k in range(8):
        j = k % 4
        if j == 3:
            f = stance(leg, hip, "front" if k < 4 else "back", PASS_LIFT)
            K.put(f, top, 0, 0)
            f = K.shifted(f, 0, BELT[3] - BELT[0])
        else:
            back, front = legs[j][:2]
            far, near = (back, front) if k < 4 else (front, back)
            f = toned(parts[j], far_patches(parts[j], far, near))
            K.put(f, top, pivs[j][0] - pivs[0][0], BELT[j] - BELT[0])
        strips["run"][cell(k, n["run"], cw, ch)] = tidy(f)
        cells["tags"]["run"][k]["pivot"] = list(pivs[j])
    for (tag, k), (src, j, dx) in GRIP_FROM.items():
        piece = strips[src][cell(j - 1, n[src], cw, ch)]
        strips[tag][cell(k - 1, n[tag], cw, ch)] = K.shifted(piece, dx, 0)
        cells["tags"][tag][k - 1]["pivot"] = list(cells["tags"][src][j - 1]["pivot"])
    dead = strips["dead"]
    for k in range(2, 9):
        sl = cell(k - 1, n["dead"], cw, ch)
        f = dead[sl].copy()
        for r in range(ch):
            f[r, :DEAD_B[k].get(r, 0)] = 0
        c = np.zeros_like(f)
        K.put(c, anchor, DEAD_LEFT[k], RN.PIVOT[1] + 11 - anchor.shape[0])
        K.put(c, f, 0, 0)
        c[RN.PIVOT[1] + 12:] = 0
        dead[sl] = tidy(c)
    # the idle: side-on like every action (the user: 「待机图也改成侧面的吧 不然太奇怪了」), standing still (8)
    for t in cells["tags"].values():
        for fr in t:
            fr.pop("head", None)
    near = leg_units(first[3], BELT[3], pivs[3][0], pivs[0][0])["F"]
    near[:THIGH4] = 0                               # the straight part of run frame 4's front leg, from the thigh down
    far = near
    stand = np.zeros_like(first[0])
    K.put(stand, toned(on_ground(far, STAND_BACK), solid_of(on_ground(far, STAND_BACK))), 0, 0)
    K.put(stand, on_ground(near, 0), 0, 0)
    K.put(stand, hip, 0, 0)
    K.put(stand, top, 0, 0)
    stand = tidy(stand)
    cells["tags"]["idle"] = [{"pivot": list(pivs[0]), "ms": m} for m in RN.MS["idle"]]
    cols, rows = K.layout(len(RN.MS["idle"]))
    sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k in range(len(RN.MS["idle"])):
        sheet[cell(k, len(RN.MS["idle"]), cw, ch)] = stand
    strips["idle"] = sheet
    return strips, cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare with the files instead of writing them")
    a = ap.parse_args()
    strips, cells = build()
    bad = []
    for t in TAGS:
        big = np.repeat(np.repeat(strips[t], Z, 0), Z, 1)
        path = os.path.join(NATIVE, f"nautilus_{t}.png")
        if a.check:
            if not np.array_equal(np.asarray(Image.open(path).convert("RGBA")), big):
                bad.append(t)
        else:
            Image.fromarray(big).save(path)
    path = os.path.join(NATIVE, "nautilus_cells.json")
    text = json.dumps(cells, indent=1) + "\n"
    if a.check:
        with open(path, encoding="utf-8") as f:
            if f.read() != text:
                bad.append("cells")
        print("differs:", bad or "nothing")
        sys.exit(1 if bad else 0)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote", ", ".join(TAGS))


if __name__ == "__main__":
    main()

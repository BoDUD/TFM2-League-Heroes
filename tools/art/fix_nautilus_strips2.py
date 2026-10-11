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
  6. the run trades legs every half cycle: frames 5-8 are frames 1-4 with the legs' tones swapped (the front one darker).
  9. the carried anchor cut to 0.72 by whole rows and columns (「钩子画的过大了 适当缩小」).
  7. the run's upper body is frame 1's in every frame (bobbing a row): Codex's redrawn upper bodies shook.
The idle is side-on too (the user: 「待机图也改成侧面的吧 不然太奇怪了」, after the front-on design idle beside the side-on
actions): W+E's first frame (8: its legs moved whole closer together, oppi's shoulder-wide stance - 「待机动作 不应该岔开腿」), breathing (the body above the hip band sinks a row over the legs). Writes assets/source/native/nautilus_<tag>.png (8x) and nautilus_cells.json; then
python tools/art/import_native.py --hero nautilus.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import rig_nautilus as RN  # noqa: E402
import design_riven as R  # noqa: E402

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


def darkened(part):
    step = {"v": "s", "s": "n", "n": "i", "i": "f"}
    u = part.s.copy()
    for y, x in zip(*np.nonzero(u[..., 3])):
        ch = INV.get(tuple(int(v) for v in u[y, x, :3]))
        if ch in step:
            u[y, x, :3] = L[step[ch]]
    return K.Part(u, part.j)


def smaller(part, scale):
    """9: the anchor above the fist (rows over FIST_ROW) made smaller by whole rows and columns dropped (design_riven's
    keep_axis: in each group the line most like its neighbour goes, nothing resampled, no square repainted), the
    shank's columns (SHANK_COLS) and its foot (rows FIST_ROW - 4 to - 2) kept whole; the crown as high over his head as
    before, the straight shank run on down to the fist; the fist as it is."""
    s = part.s
    top = s[:FIST_ROW]
    cols = sorted({tuple(int(v) for v in p[:3]) for p in top[top[..., 3] > 0]})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full(top.shape[:2], -1, int)
    for y, x in zip(*np.nonzero(top[..., 3])):
        idx[y, x] = lut[tuple(int(v) for v in top[y, x, :3])]
    H, W = idx.shape
    rows = R.keep_axis([idx[y] for y in range(H)], round(H * scale), range(H - 4, H - 1))
    keep = R.keep_axis([idx[rows][:, x] for x in range(W)], round(W * scale), SHANK_COLS)
    small = top[np.ix_(rows, keep)]
    dx = SHANK_COLS[0] - keep.index(SHANK_COLS[0])          # the shank over the same columns as before
    canvas = np.zeros_like(s)
    canvas[FIST_ROW:] = s[FIST_ROW:]
    K.put(canvas, small, dx, 0)
    shank = small[-1:]
    for r in range(len(rows), FIST_ROW):
        K.put(canvas, shank, dx, r)
    return K.Part(canvas, part.j)


def helmet_top(f):
    """The helmet: the biggest piece of light bronze; its top row and its leftmost square there."""
    br = is_(f, "t") | is_(f, "p") | is_(f, "k") | is_(f, "o") | is_(f, "u")
    lab, n = ndimage.label(br, np.ones((3, 3)))
    sizes = ndimage.sum(br, lab, range(1, n + 1))
    ys, xs = np.nonzero(lab == 1 + int(np.argmax(sizes)))
    top = ys.min()
    return top, xs[ys == top].min()


def carry(f, B, F, unit):
    """5: Codex's carried anchor out, the design's anchor unit in (see CARRY)."""
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
    K.place(g, unit, (F[1], F[0]))
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


def legs_swapped(f, pivot_x):
    """6: the frame with its back (left) leg lighter and its front (right) leg darker."""
    out = f.copy()
    for y in range(LEG_ROW, f.shape[0]):
        xs = np.nonzero((f[y, :, 3] > 0) & ~is_(f[y:y + 1], "0")[0])[0]
        if not len(xs):
            continue
        gaps = np.diff(xs)
        split = xs[int(np.argmax(gaps))] + 1 if gaps.size and gaps.max() > 1 else pivot_x
        for x in xs:
            ch = INV.get(tuple(int(v) for v in f[y, x, :3]))
            table = LIGHTER if x < split else DARKER
            if ch in table:
                out[y, x, :3] = L[table[ch]]
    return out


def legs_closer(stand, pivot_x):
    """8: the stance's two legs (every row from HIP_ROW, split at the crotch, CROTCH columns from the standing point)
    each moved whole NARROW columns toward the other - no square redrawn, the front leg over the back one."""
    split = int(pivot_x) + CROTCH
    back, front = np.zeros_like(stand), np.zeros_like(stand)
    back[HIP_ROW:, :split] = stand[HIP_ROW:, :split]
    front[HIP_ROW:, split:] = stand[HIP_ROW:, split:]
    out = stand.copy()
    out[HIP_ROW:] = 0
    K.put(out, back, NARROW, 0, under=True)
    K.put(out, front, -NARROW, 0)
    return tidy(out)


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
# 9: the carried anchor was too big (「钩子画的过大了 适当缩小」: the design's unit, 36 squares across, wider than his
# body; the anchors he swings are about 25): above the fist it loses whole rows and columns to ANCHOR_SCALE (smaller()).
FIST_ROW = 27
ANCHOR_SCALE = 0.72
SHANK_COLS = range(8, 12)                                       # the unit's shank above the fist
# (tag, frame) <- the mended W+E stance (the idle's), or the mended hit 2 a column back
GRIP_FROM = {("attack", 1): ("skill2", 1, 0), ("attack", 6): ("skill2", 1, 0), ("skill_pull", 4): ("skill2", 1, 0),
             ("ult", 1): ("skill2", 1, 0), ("hit", 1): ("hit", 2, -1)}
# 6: the run never changed legs (「走路压根看不出换腿」): Codex kept the same leg in front in all 8 frames. Frames 5-8 are
# frames 1-4 again with the legs' tones swapped - the leg in front darker (the far one), the one behind brighter (the near
# one) - so the legs trade places every half cycle; the shapes square for square. Below LEG_ROW each row's pixels split
# into the left leg and the right leg at the widest gap (or the standing point where they touch).
LEG_ROW = 88
DARKER = {"u": "p", "t": "k", "p": "j", "o": "k", "m": "j", "k": "h", "j": "e", "h": "e", "n": "i", "s": "n", "i": "f",
          "f": "a", "c": "e", "b": "a"}
LIGHTER = {"k": "t", "j": "p", "h": "k", "e": "j", "m": "p", "p": "t", "o": "t", "c": "j", "a": "f", "f": "i", "i": "n",
           "b": "f"}
# 7: the run shook (「走路时模型抖动太厉害」): Codex redrew the upper body in every frame (the helmet 3 columns and 2 rows
# apart) and the carried anchor rode the fist. The run's upper body (every row above LEG_ROW: the helmet, the shoulders,
# the fists, the anchor) is frame 1's in all 8 frames, at the same place from the standing point, bobbing RUN_BOB rows;
# only the legs change.
RUN_BOB = [0, -1, -1, 0, 0, -1, -1, 0]
# 8: the idle stood astride (「待机动作 不应该岔开腿」「待机动作你看oppi怎么画的啊 还有模型别变形啊」): oppi's idles stand
# with the feet about shoulder-wide; W+E's braced stance keeps every square, its two legs each moved whole NARROW
# columns in under the hips.
HIP_ROW = 89
CROTCH = -3
NARROW = 4
IDLE_BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
IDLE_CUT = 86                                                   # the last row that sinks (the hip band's)
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
    unit = smaller(darkened(RN.Parts().unit), ANCHOR_SCALE)
    for (tag, k), (B, F) in CARRY.items():
        sl = cell(k - 1, n[tag], cw, ch)
        strips[tag][sl] = carry(strips[tag][sl], B, F, unit)
    for k in range(4, 8):
        src = strips["run"][cell(k - 4, n["run"], cw, ch)]
        piv = cells["tags"]["run"][k - 4]["pivot"]
        strips["run"][cell(k, n["run"], cw, ch)] = legs_swapped(src, piv[0])
        cells["tags"]["run"][k]["pivot"] = list(piv)
    top = strips["run"][cell(0, n["run"], cw, ch)].copy()
    top[LEG_ROW:] = 0
    piv0 = cells["tags"]["run"][0]["pivot"][0]
    for k in range(8):
        sl = cell(k, n["run"], cw, ch)
        f = strips["run"][sl].copy()
        dy = RUN_BOB[k]
        f[:LEG_ROW + dy] = 0
        K.put(f, top, cells["tags"]["run"][k]["pivot"][0] - piv0, dy)
        strips["run"][sl] = tidy(f)
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
    # the idle: side-on like every action (the user: 「待机图也改成侧面的吧 不然太奇怪了」) - W+E's first frame (Codex's
    # braced stance, both boots flat, the anchor on his back), breathing: everything above the crotch (rows to
    # IDLE_CUT) sinks a row over the legs in frames 3-6
    for t in cells["tags"].values():
        for fr in t:
            fr.pop("head", None)
    pivot = list(cells["tags"]["skill2"][0]["pivot"])
    stand = legs_closer(strips["skill2"][cell(0, n["skill2"], cw, ch)], pivot[0])
    cells["tags"]["idle"] = [{"pivot": pivot, "ms": m} for m in RN.MS["idle"]]
    cols, rows = K.layout(len(IDLE_BREATH))
    sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k, b in enumerate(IDLE_BREATH):
        fr = stand.copy()
        if b:
            up = np.zeros_like(stand)
            up[:IDLE_CUT + 1] = stand[:IDLE_CUT + 1]
            fr[:IDLE_CUT + 1] = 0
            K.put(fr, up, 0, b)
            fr = tidy(fr)
        sheet[cell(k, len(IDLE_BREATH), cw, ch)] = fr
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

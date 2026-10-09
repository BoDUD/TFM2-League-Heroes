#!/usr/bin/env python3
"""Karma's action strips from Codex's whole-figure redraw (2026-10-09, assets/source/karma/codex_strips_v2).

    python tools/art/fix_karma_strips.py [--check] [--review DIR] [--no-write] [--heads]

The user on the rig's strips (rig_karma.py, only the arms moving over the idle): 「你好好修吧 这像英雄联盟里面的吗」,
and before that on a head pasted over a body drawn under it: 「头和身体移动时还是脱节的啊 合并在一起了」. The pick: Codex
redraws every action from League's own poses with the whole figure drawn at once (MODEL_STRIPS_v2.md). Its heads differ
from frame to frame (the ring's shape, the hair, the eyes), so every upright frame gets the approved design's head
piece at the place Codex drew its head - the head stays where the body puts it:
1. Codex's frame on the 128 canvas, its pivot on the design's standing point (64, 88);
2. the head's place: the design's bob and face (rows 63-75) slid over the frame, the offset with the most squares of
   the same colour (HEAD_AT overrides it);
3. Codex's own head goes: in a box round the design's head piece, every piece of Codex's squares outside the design's
   head that is not an arm (fewer than ARM skin squares) is cleared;
4. the design's ring and the head's prongs go behind (onto empty squares only: a raised hand stays in front), the bob
   and the face (the C2 eyes) over;
5. finished only round what changed (rig_karma.finish_near), stray outline squares dropped.
The idle is rig_karma's (the design with the ring and the prongs bobbing).
Her size (the user 10-09: 「卡尔玛体型可以变小一点」, then 「缩小模型后有点奇怪了啊整体」): the first 90% took four rows and two to
six columns out of the finished frames with the face kept - every cut fell under the chin (the boots, the waist, the
shoulders, a different line in each action) and the head kept its size: a big head on a squat body. Now the head is
made smaller here, the same in every frame (HEAD_CUT: one row of the ring, one of the forehead, one column of the bob's
left curtain, taken out of the design before anything is built), and import_native.py takes only two body rows (SHRINK
0.95, the head and the boots kept) - head and body both about 90%.
Writes assets/source/native/karma_<tag>.png
(8x, 96x80 cells, soles on cell row 65) and karma_cells.json; then tools/art/import_native.py.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import rig_karma as RK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "karma", "codex_strips_v2")
NATIVE = RK.NATIVE
L = RK.L
OUT = RK.OUT
PIVOT = RK.PIVOT
SOLES = RK.SOLES
CELL = RK.CELL
CELL_PIVOT = RK.CELL_PIVOT
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill_e", "ult", "hit", "dead"]
CODEX_TAGS = TAGS[1:]
FACE_ROWS = (64, 75)              # the (cut) design's bob, circlet and face: what the head's place is matched on
# the head made smaller in the design itself: rows of the head band (<= BAND) out, what lies over them moving down (the
# chin stays on the neck); columns of the head band out, what lies left of them moving right. Row 61: the ring's lower
# band (its hole keeps a row, the gem and the highlight stay); row 68: the forehead (the circlet, the eyes and the
# left prong's outline stay); column 56: the inside of the bob's left curtain (the right side carries the eye's corner,
# the earring, the prong: any column there breaks one)
HEAD_CUT = {"rows": (61, 68), "cols": (56,), "band": 75}
RING_LAST = 63                     # the ring's bottom row after the cut (58-62 before)
HEAD_PIECE = RK.RUN_HEAD           # the ring, the bob with its sides, the face, the earrings, the head's prongs
ARM = 5                            # a piece outside the design's head with this many skin squares is an arm, it stays
SKIN = ("s", "S", "z")
SEARCH = (22, 16)
# frames whose head stays Codex's own: the death's doubled-over and hanging heads (2-3) and the lying one
# (8) - an upright design head there would undo League's motion
KEEP_HEAD = {("dead", 2), ("dead", 3), ("dead", 8)}
# the death from its frame 2 on: the ring and the prongs have broken away (Codex drew them flying and on the ground),
# so only the bob and the face are the design's
NO_RING = {("dead", k) for k in range(2, 9)}
HEAD_AT = {}                       # (tag, frame): (dx, dy) of the design's head on the canvas, where the match misses
# Q's front leg: Codex drew League's dark stocking on it (navy and hair-dark squares from the thigh to the boot's gold
# trim); the design's leg in the slit is bare - those squares become skin ((row0, row1, col0, col1) on the canvas: the
# leftmost of each row's run the shade S, the rest s, an end against the background the outline)
LEG_SKIN = {("skill", 2): [(87, 93, 68, 73)], ("skill", 4): [(91, 94, 71, 76)], ("skill", 5): [(91, 94, 72, 75)],
            ("skill", 6): [(87, 94, 67, 70)]}
DARK = ("b", "h", "k", "H")
# an arm raised past the head (attack 5, E 2-3): Codex drew it in front of the hair's right side; the design's head
# pasted over it left only the hand floating by the ring - Codex's squares in these boxes (row0, row1, col0, col1 on
# the canvas: the hand, the bracer and the forearm) go back on top
ARM_OVER = {("attack", 5): [(60, 67, 66, 70)], ("skill_e", 2): [(60, 70, 67, 71)], ("skill_e", 3): [(60, 69, 62, 67)]}
# the death: the ring rolls 2-3 columns between Codex's frames once it lies (4: 32-41, 5-8: 29-38) - frame 5's ring in
# 4-8; the prong Codex left standing in the air beside the skirt in 5-8 (columns 40-46, rows 87-94) goes
RING_FROM = ("dead", 5)
RING_LOCK = [("dead", k) for k in range(4, 9)]
FLOATER = {("dead", k): (40, 46, 87, 94) for k in range(5, 9)}
JADE = ("m", "J", "j", "l", "n", "e")
# the run: Codex kept the planted foot on the pivot in every frame and swung the whole body round it - the head wandered
# 12 columns (League's 1.5), so in game she would wobble back and forth. Every run frame moves whole so its head (the
# pasted design head) follows League's head (the pack's cells "head" against the pivot, from League's idle head = the
# design's): the body steady and where the idle has it, the feet stepping under it (planted ahead, sliding back)
STEADY = {"run"}


def layout(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def codex(tag):
    """Codex's frames of a tag on 128 canvases (pivot on PIVOT) and their durations."""
    with open(K.lp(os.path.join(SRC, "karma_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    frs = cells["tags"][tag]
    strip = np.asarray(Image.open(K.lp(os.path.join(SRC, "native", f"karma_{tag}_1x.png"))).convert("RGBA"))
    cols = layout(len(frs))
    out = []
    for i, fr in enumerate(frs):
        X, Y = (i % cols) * CELL[0], (i // cols) * CELL[1]
        cell = strip[Y:Y + CELL[1], X:X + CELL[0]].copy()
        cell[cell[..., 3] < 128] = 0
        c = np.zeros((128, 128, 4), np.uint8)
        K.put(c, cell, PIVOT[0] - fr["pivot"][0], PIVOT[1] - fr["pivot"][1])
        out.append(c)
    return out, [fr["ms"] for fr in frs]


def head_place(c, des, face):
    """(dx, dy, score): where the design's bob and face sit best in c."""
    ys, xs = np.nonzero(face)
    cols = des[ys, xs, :3].astype(int)
    fr = c.astype(int)
    best = (-9.0, 0, 0)
    for dy in range(-SEARCH[1], SEARCH[1] + 1):
        for dx in range(-SEARCH[0], SEARCH[0] + 1):
            f = fr[ys + dy, xs + dx]
            op = f[:, 3] > 0
            d = np.abs(f[:, :3] - cols).sum(-1)
            s = (((d == 0) & op).sum() + 0.5 * ((d > 0) & (d < 90) & op).sum() - 0.5 * (~op).sum()) / len(ys)
            if s > best[0]:
                best = (float(s), dx, dy)
    return best


def colour_is(c, keys):
    m = np.zeros(c.shape[:2], bool)
    for k in keys:
        m |= (c[..., :3] == np.array(L[k], np.uint8)).all(-1) & (c[..., 3] > 0)
    return m


def with_head(P, c, at, ring=True):
    """c with Codex's head swapped for the design's head piece at offset `at` (without the ring and the head's prongs
    when ring is False)."""
    des = P.design
    dx, dy = at
    hp = RK.head_mask(des, HEAD_PIECE)
    rings = hp & (np.arange(128)[:, None] <= RING_LAST)
    behind = rings | (hp & ~RK.head_mask(des))         # the ring and the head's prongs
    if not ring:
        hp &= ~behind
        behind = np.zeros_like(behind)
    front = hp & ~behind
    put = K.shifted(np.where(hp[..., None], des, 0).astype(np.uint8), dx, dy)[..., 3] > 0
    ys, xs = np.nonzero(hp)
    y0, y1 = ys.min() + dy - 4, ys.max() + dy
    x0, x1 = xs.min() + dx - 4, xs.max() + dx + 4
    zone = np.zeros((128, 128), bool)
    zone[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
    rest = c.copy()
    rest[~(zone & ~put)] = 0
    skin = colour_is(c, SKIN)
    limb = colour_is(c, SKIN + ("b", "0"))
    out = c.copy()
    arm = np.zeros((128, 128), bool)
    for comp in K.pieces(rest):
        n = sum(1 for y, x in comp if skin[y, x])
        for y, x in comp:
            if n < ARM:
                out[y, x] = 0
            else:
                arm[y, x] = True
    # an arm reaching over the ring or a prong (a hand raised above the head) stays in front of them: its skin, bracer
    # and outline squares under the ring/prongs joined to the arm's squares outside
    back = K.shifted(np.where(behind[..., None], des, 0).astype(np.uint8), dx, dy)[..., 3] > 0
    grow = arm.copy()
    while True:
        g = grow.copy()
        for a_, b_ in RK.N4:
            g |= np.roll(np.roll(grow, a_, 0), b_, 1)
        g &= (grow | (back & limb))
        if (g == grow).all():
            break
        grow = g
    out[put & ~grow] = 0                                 # Codex's own hair, face and ring under the design's head
    K.put(out, K.shifted(np.where(behind[..., None], des, 0).astype(np.uint8), dx, dy), 0, 0, under=True)
    fm = K.shifted(np.where(front[..., None], des, 0).astype(np.uint8), dx, dy)
    m = fm[..., 3] > 0
    out[m] = fm[m]
    return out


def skin_leg(c, boxes):
    dark = colour_is(c, DARK)
    for r0, r1, c0, c1 in boxes:
        for y in range(r0, r1 + 1):
            run = [x for x in range(c0, c1 + 1) if dark[y, x]]
            for j, x in enumerate(run):
                if not c[y, x - 1, 3] or not c[y, x + 1, 3]:
                    c[y, x] = (*L["0"], 255)
                else:
                    c[y, x] = (*L["S" if j == 0 or not dark[y, x - 1] else "s"], 255)
    return c


def ground_ring(c):
    """The jade ring lying on the ground: the detached piece of jade squares under row 90."""
    m = np.zeros((128, 128), bool)
    jade = colour_is(c, JADE)
    for comp in K.pieces(c)[1:]:
        if min(y for y, x in comp) >= 90 and sum(1 for y, x in comp if jade[y, x]) > len(comp) // 2:
            for y, x in comp:
                m[y, x] = True
    return m


def cut_head(a):
    """HEAD_CUT applied to a design-canvas image or mask (rows and columns of the head band only)."""
    out = a.copy()
    band = out[:HEAD_CUT["band"] + 1].copy()
    for r in sorted(HEAD_CUT["rows"], reverse=True):
        band[1:r + 1] = band[0:r].copy()
        band[0] = 0
    for c in sorted(HEAD_CUT["cols"]):
        band[:, 1:c + 1] = band[:, 0:c].copy()
        band[:, 0] = 0
    out[:HEAD_CUT["band"] + 1] = band
    return out


def small_head(P):
    """rig_karma's parts with the design's head cut (HEAD_CUT): the design, every part's mask and the body under them
    (the arms' units start under the head band and stay as they are)."""
    P.design = cut_head(P.design)
    P.ink = cut_head(P.ink)
    for k in P.masks:
        P.masks[k] = cut_head(P.masks[k])
    P.body = P.design.copy()
    for m in P.masks.values():
        P.body[m] = 0
    return P


def build(P, tag, report=None):
    frames, ms = codex(tag)
    for i, c in enumerate(frames):
        if (tag, i + 1) in LEG_SKIN:
            skin_leg(c, LEG_SKIN[(tag, i + 1)])
        if (tag, i + 1) in FLOATER:
            x0, x1, y0, y1 = FLOATER[(tag, i + 1)]
            for comp in K.pieces(c)[1:]:
                if all(x0 <= x <= x1 and y0 <= y <= y1 for y, x in comp):
                    for y, x in comp:
                        c[y, x] = 0
    if tag == RING_FROM[0]:
        src = frames[RING_FROM[1] - 1]
        ring = np.where(ground_ring(src)[..., None], src, 0).astype(np.uint8)
        for t, k in RING_LOCK:
            c = frames[k - 1]
            c[ground_ring(c)] = 0
            K.put(c, ring, 0, 0, under=True)
    des = P.design
    face = RK.head_mask(des) & (np.arange(128)[:, None] >= FACE_ROWS[0]) & (np.arange(128)[:, None] <= FACE_ROWS[1])
    if tag in STEADY:
        with open(K.lp(os.path.join(SRC, "karma_cells.json")), encoding="utf-8-sig") as fh:
            tags = json.load(fh)["tags"]
        idle = tags["idle"][0]["head"][0] - tags["idle"][0]["pivot"][0]   # the design's head = League's idle head
        lol = [fr["head"][0] - fr["pivot"][0] - idle for fr in tags[tag]]
        at = [head_place(c, des, face)[1] for c in frames]
        frames = [K.shifted(c, int(round(lol[i])) - at[i], 0) for i, c in enumerate(frames)]
    out = []
    for i, c in enumerate(frames):
        k = i + 1
        if (tag, k) in KEEP_HEAD:
            out.append(tidy(c))
            continue
        if (tag, k) in HEAD_AT:
            dx, dy = HEAD_AT[(tag, k)]
            s = None
        else:
            s, dx, dy = head_place(c, des, face)
        if report is not None:
            report.append((tag, k, dx, dy, s))
        f = with_head(P, c, (dx, dy), ring=(tag, k) not in NO_RING)
        for r0, r1, c0, c1 in ARM_OVER.get((tag, k), []):
            box = np.zeros((128, 128), bool)
            box[r0:r1 + 1, c0:c1 + 1] = True
            box &= c[..., 3] > 0
            f[box] = c[box]
        f = RK.drop_orphans(RK.finish_near(f, c), c)
        out.append(tidy(f))
    return out, ms


def tidy(f):
    """Codex's own crumbs: one-square see-through pinholes inside the figure filled (the colour round them, or the
    outline between two outlines) and stray outline squares with no colour round them dropped."""
    f = K.fill_pinholes(f.copy(), 1, OUT)
    return RK.drop_orphans(f, np.zeros_like(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--heads", action="store_true", help="print where each frame's head went")
    a = ap.parse_args()
    P = small_head(RK.Parts())
    built = {"idle": RK.idle_frames(P)}
    ms = {"idle": RK.MS["idle"]}
    report = []
    for tag in CODEX_TAGS:
        built[tag], ms[tag] = build(P, tag, report)
    if a.heads:
        for r in report:
            print(r)
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}" for r in rows))
    if not a.no_write:
        bad = K.write_strips("karma", built, ms, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "karma_fix_review.png"), z=4, soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], ms, os.path.join(a.review, "karma_fix_review.gif"), z=4)
    return built


if __name__ == "__main__":
    main()

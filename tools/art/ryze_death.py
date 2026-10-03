#!/usr/bin/env python3
"""Ryze's death drawn on the idle's own body (2026-10-04), as Kai'Sa's (tools/art/kaisa_death.py) and Caitlyn's:
struck and swaying on the idle (Codex's frames 1-2, finished by tools/art/fix_ryze_strips_v2.py), down on one knee
with a hand on the other (3-4), slumped on both knees with the hands on the ground (5), lying on his front with the
scroll on his back and the head upright, the beard on the ground (6-8).

Codex's own frames from 3 on drew another body under the pasted head (a bigger scroll, a dark smeared mass for the
coat and the legs; the review after 「错误的地方太多了」). Here every frame is the design's own squares: the upper body
down to the belt with both arms hanging (the hands rest on the near knee / on the ground) moved down onto legs drawn
square by square in his leg materials (KNEEL: the navy trousers, the gold cuffs, the brown boots with their band), and
for the lying frames his body drawn flat behind the head (LYING). Imported by fix_ryze_strips_v2.py (DEATH).
"""
# rows from the standing point (the soles on 10, the ground under them on 11); {row: (first column, squares)}; one
# outline round each leg after
KNEEL = {
    # the far leg: the thigh level forward to the knee, the boot upright, the foot planted
    "far": {1: (-2, "ozwwwz"), 2: (-2, "ozzwwwwzo"), 3: (0, "oozzzzwo"), 4: (4, "zxxj"), 5: (5, "jxx"),
            6: (5, "jhjx"), 7: (5, "jhh"), 8: (5, "jhh"), 9: (5, "Dxx"), 10: (5, "rjjhh")},
    # the near leg: the thigh down to the knee on the ground, the boot flat behind it, its sole up at the far end
    "near": {1: (-5, "owwz"), 2: (-5, "owwz"), 3: (-5, "ozwz"), 4: (-4, "ozwz"), 5: (-4, "ozwwz"), 6: (-3, "ozwwz"),
             7: (-3, "ozwwz"), 8: (-2, "ozwwz"), 9: (-11, "rjhhjhhhxxozwz"), 10: (-11, "rjjhhjhDxxozzo")},
    # both knees down (the slump): the far thigh straight down, its boot flat behind higher up
    "far2": {1: (-1, "ozwwz"), 2: (0, "ozwwz"), 3: (0, "ozwwz"), 4: (0, "ozwwz"), 5: (0, "ozwwz"), 6: (1, "ozwwz"),
             7: (1, "ozwwz"), 8: (-7, "rjhhjhxxozwwz"), 9: (-7, "rjjhDxxozwzo")},
}
# lying on his front: the boots (soles up at the far end), the trousers, the belt, the coat with the strap and the
# near arm along it (the shoulder by the head, the hand back by the belt), the scroll lying on his back; the head (the design's, upright) in front, the beard on the ground
LYING = {3: (-15, "hkknnnnkkh"), 4: (-15, "hknnnnnnkh"), 5: (-16, "ahkkkkkkkkha"),
         6: (-29, "rjhxowwwwwwwojhozzhzzzzzo"),
         7: (-29, "rjhxozwwwwwzohxozzzhzzzzo"),
         8: (-29, "rjhxozzzzzzzohyozzzzhzzzo"),
         9: (-29, "rDxxoozzzzzoojhefxhhxeeff"),
         10: (-29, "rjjxooozzzoooj.idxjjxiddi")}
# the head to the beard's top (the beard under it lies on the ground), not the scroll left of it nor the strap and the
# shoulder beside the beard: {first row, last row: first column}; with them and the whole beard the head stood up
# diagonally, its beard trailing down to the left (the user: 「这死了头是歪的？」)
HEAD_PART = {(-29, -21): -6, (-20, -18): -5}
LYING_HEAD = (3, 28)             # the head's move from standing: the beard's top row (-18) on row 10


def cells_of(spec, rgba):
    out = {}
    for y, (x0, s) in spec.items():
        for j, ch in enumerate(s):
            if ch != ".":
                out[(x0 + j, y)] = rgba(ch)
    return out


def ring_of(cells):
    out = set()
    for (x, y) in cells:
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ox, y + oy)
            if q not in cells:
                out.add(q)
    return out


def put(canvas, pivot, cells, ink, outline=True):
    """cells (x, y) -> rgba onto the canvas at the pivot, with one outline round them; nothing under the ground row."""
    px, py = pivot
    h, w = canvas.shape[:2]
    if outline:
        for (x, y) in ring_of(cells):
            if 0 <= py + y < h and 0 <= px + x < w and y <= 11:
                canvas[py + y, px + x] = ink
    for (x, y), c in cells.items():
        if 0 <= py + y < h and 0 <= px + x < w and y <= 10:
            canvas[py + y, px + x] = c


def frame(kind, des, pivot, shape, rgba, ink, dy=5):
    """One death frame on the design: kind "kneel" (one knee), "slump" (both knees) or "lying"."""
    import numpy as np
    out = np.zeros(shape, np.uint8)
    if kind == "lying":
        put(out, pivot, cells_of(LYING, rgba), ink)
        hx, hy = LYING_HEAD
        head = {(x + hx, y + hy): c for (x, y), c in des.items()
                if any(y0 <= y <= y1 and x >= x0 for (y0, y1), x0 in HEAD_PART.items())}
        put(out, pivot, head, ink)
        return out
    for name in (("far", "near") if kind == "kneel" else ("far2", "near")):
        put(out, pivot, cells_of(KNEEL[name], rgba), ink)
    # the upper body to the belt, the teal flap hanging from it, both arms hanging to the hands (the far one left, the
    # near one right of the hips)
    upper = {(x, y + dy): c for (x, y), c in des.items()
             if (y <= -4 or (x <= -6 and y <= 1) or (x >= 6 and y <= 1) or (-2 <= x <= 3 and y <= 1)) and y + dy <= 10}
    put(out, pivot, upper, ink, outline=False)
    return out

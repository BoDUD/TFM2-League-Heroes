#!/usr/bin/env python3
"""Kai'Sa's death drawn on the idle's own body (2026-10-03), as Caitlyn's merged death (tools/art/rig_caitlyn.py on main):
struck and swaying on the idle (Codex's frames 1-2, mended by tools/art/fix_kaisa_strips_v2.py), down on one knee
(3-4), slumping on both knees with the claws on the ground (5), lying on her front with the head upright, its chin on
the ground (6-8).

Codex's own death drew another, older model from frame 3 on (a narrower torso, no near shoulder plate, a sliver of a
pod, plum hair; the user: 「死亡时候的脸也不对 身体还是原版的？」). Here every frame is the design's own squares: the upper
body (rows over the hips: the head, the pods, the long hair, the suit, both arms) moved down onto legs drawn square by
square in her leg materials (KNEEL, the violet thigh plates, the gold bands, the gold-soled boots), and for the lying
frames her body drawn flat behind the head (LYING). Imported by fix_kaisa_strips_v2.py (DEATH_FROM = 3).
"""
import numpy as np

# rows from the standing point (the soles on 11), columns from X0; "." empty; one outline round each leg after
X0 = -12
KNEEL_Y = 3
KNEEL = {
    # the far leg: the thigh level forward, the shin upright, the boot planted
    "far": ["..........EEEEbEEa....",
            "..........fffffbfff...",
            "................fbf...",
            "................ffb...",
            "................fbf...",
            "................fff...",
            "...............fbbCb..",
            "......................"],
    # the near leg: the thigh down to the knee on the ground, the shin flat behind it, the boot's sole up
    "near": ["......ffffEEEbE.......",
             "......fifffEbEE.......",
             "......ffiffEEff.......",
             ".......fffffbff.......",
             "..........fffbf.......",
             "..........ffbff.......",
             "..CbbffffbffffE.......",
             "..CbfffbfffffE........"],
    # both knees down (the slump): the far shin flat behind too, higher up
    "far2": ["..........EEEbE.......",
             "..........EEbEE.......",
             "..........ffEff.......",
             "..........fbfff.......",
             "..........fffbf.......",
             "....CbfffbfffEf.......",
             "....Cbfffffbfff.......",
             "......................"],
}

# lying on her front: the long hair over her back, the shoulder plate, the slate suit, the violet hips, the legs flat
# behind to the left with the gold-soled boots; the head (the design's, upright) in front with its chin on the ground
LYING_X0, LYING_Y0 = -27, 4
LYING = ["...............kjjjggjjk....",
         "............kjjjggggjjjgjk..",
         "..........kjggjjbbbjjgggjjk.",
         ".....EEbEErrBBrbbebbrrBBrrr.",
         "CbffffbffEEEbrrrBBrrrBBrrrd.",
         "CbffbfffffEEfirrrrBBrrrrrde.",
         "..........................e."]
LYING_HEAD = (6, 21)                 # the head's move from standing: its chin (row -11) on the ground row 10


def cells_of(rows, x0, y0, rgba):
    out = {}
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch != ".":
                out[(x0 + j, y0 + i)] = rgba(ch)
    return out


def ring_of(cells):
    out = set()
    for (x, y) in cells:
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                q = (x + ox, y + oy)
                if q not in cells and (ox == 0 or oy == 0):
                    out.add(q)
    return out


def put(canvas, pivot, cells, ink, outline=True, over=True):
    """cells (x, y) -> rgba onto the canvas at the pivot, with one outline round them (over what is there if over)."""
    px, py = pivot
    h, w = canvas.shape[:2]
    if outline:
        for (x, y) in ring_of(cells):
            if 0 <= py + y < h and 0 <= px + x < w and (over or not canvas[py + y, px + x, 3]):
                canvas[py + y, px + x] = ink
    for (x, y), c in cells.items():
        if 0 <= py + y < h and 0 <= px + x < w:
            canvas[py + y, px + x] = c


def frame(kind, des, pivot, shape, rgba, ink, head_squares, pods, dy=6, dx=0):
    """One death frame on the design: kind "kneel" (one knee), "slump" (both knees) or "lying"."""
    out = np.zeros(shape, np.uint8)
    if kind == "lying":
        put(out, pivot, cells_of(LYING, LYING_X0, LYING_Y0, rgba), ink)
        hx, hy = LYING_HEAD
        head = {(x + hx, y + hy): c for (x, y), c in des.items() if (x, y) in head_squares or (x, y) in pods
                or (y <= -17 and -9 <= x <= 9)}
        put(out, pivot, head, ink, outline=False)
        return out
    legs = ("far", "near") if kind == "kneel" else ("far2", "near")
    for name in legs:
        put(out, pivot, cells_of(KNEEL[name], X0, KNEEL_Y, rgba), ink)
    # the upper body over the hips and both arms hanging (the far claws left, the near ones right of the hips)
    upper = {(x + dx, y + dy): c for (x, y), c in des.items()
             if (y <= -3 or (x <= -8 and y <= 4) or (x >= 6 and -2 <= y <= 3)) and y + dy <= 10}   # claws on the ground
    put(out, pivot, upper, ink, outline=False)
    return out

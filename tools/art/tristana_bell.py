#!/usr/bin/env python3
"""Tristana's cannon bell symmetric (the user: "还有小炮的枪口有点歪？").

Cutting the design to 34 rows took four columns out of the bell's inside and left it leaning: its upper half a column
narrower than the lower, the mouth's dark line and the rim a row apart. BELL is the bell drawn again at the same size
(7 x 11 squares, the barrel's axis through its middle row): the outline the lower half's, mirrored up, the dark mouth,
the navy inside and the grey rim centred on the axis, the light from the top left as before.

A library: shrink_tristana.py gives every frame that holds the idle's bell (found square for square: the idle, the
attack and the frames that end on the idle) the new one, and the hit's first frame (its own taller drawing on a
thicker barrel) the new one on its barrel's axis; fix_tristana_run.py the run's (Codex's own smaller, slanted bell, the
same drawing in all eight frames, moved with the bob). Frames with the cannon turned (Q, W, R, the death) keep theirs.
"""
import numpy as np

OUTLINE = (0x19, 0x14, 0x21)
PAL = {'A': OUTLINE, 'F': (0xB9, 0xDD, 0xED), 'G': (0x73, 0x97, 0xC3), 'H': (0x44, 0x5E, 0x80),
       'I': (0xBF, 0xCC, 0xD8), 'M': (0x7E, 0x87, 0x9E), 'N': (0x28, 0x34, 0x47)}
STEEL = {c for k, c in PAL.items() if k != 'A'}
# on the idle's first frame: rows 67-77, columns 63-70 (column 63 is the barrel's end: only the outline over the
# barrel is new there); '.' leaves the square as it is
BELL = """\
. . A A A A . .
. A A F G A . .
. A F I G G A .
A G I G A M A A
. F F M A N M A
. H G M A N M A
. H H G A N M A
. H H G A M A A
. A H H G H A .
. A A M H A . .
. . A A A A . ."""
AT = (63, 67)                    # the grid's corner on the idle
OLD = (64, 67, 70, 77)           # the old bell on the idle (x0, y0, x1, y1 inclusive): what the frames are searched for
HIT1 = (0, -2)                   # the hit's 1st: the grid moved this much from the idle's (its barrel is rows 68-72)
RUN = (-1, -2)                   # the run's 1st (barrel rows 68-72, ending a column further left)
RUN_OLD = (62, 66, 69, 76)       # the run's old bell on its 1st frame


def col(a, y, x):
    return tuple(int(v) for v in a[y, x, :3])


def find(frame, ref, box):
    """(dx, dy, share): where the steel squares of ref's box sit in the frame, square for square."""
    x0, y0, x1, y1 = box
    tpl = ref[y0:y1 + 1, x0:x1 + 1]
    m = np.zeros(tpl.shape[:2], bool)
    for y, x in zip(*np.nonzero(tpl[..., 3])):
        m[y, x] = col(tpl, y, x) in STEEL
    th, tw = m.shape
    n = m.sum()
    best = (0, 0, 0.0)
    for y in range(frame.shape[0] - th + 1):
        for x in range(frame.shape[1] - tw + 1):
            s = ((frame[y:y + th, x:x + tw] == tpl).all(-1) & m).sum() / n
            if s > best[2]:
                best = (x - x0, y - y0, s)
    return best


def same_bell(a, dx, dy, barrel_end=True):
    """The frame with the bell in the grid's place moved dx, dy from the idle's: the steel squares there go with the
    outline squares that edge nothing else, the grid goes on (its first column only where barrel_end: the idle's
    barrel meets the bell a row lower than the rest of the grid's outline), and every empty square beside a steel one
    gets the outline."""
    b = a.copy()
    rows = BELL.splitlines()
    gx, gy = AT[0] + dx, AT[1] + dy
    h, w = len(rows), len(rows[0].split())
    y0, y1, x0, x1 = gy - 1, gy + h, gx, gx + w
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if b[y, x, 3] and col(b, y, x) in STEEL:
                b[y, x] = 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if b[y, x, 3] and col(b, y, x) == OUTLINE and not any(
                    b[y + j, x + i, 3] and col(b, y + j, x + i) != OUTLINE
                    for j in (-1, 0, 1) for i in (-1, 0, 1) if (j or i)):
                b[y, x] = 0
    for r, line in enumerate(rows):
        for c, ch in enumerate(line.split()):
            if ch == '.' or (c == 0 and not barrel_end):
                continue
            b[gy + r, gx + c, :3] = PAL[ch]
            b[gy + r, gx + c, 3] = 255
    add = []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 2):
            if b[y, x, 3] == 0 and any(b[y + j, x + i, 3] and col(b, y + j, x + i) in STEEL
                                       for j, i in ((0, 1), (0, -1), (1, 0), (-1, 0))):
                add.append((y, x))
    for y, x in add:
        b[y, x, :3] = OUTLINE
        b[y, x, 3] = 255
    return b


def fix(tag, k, a, idle):
    """Frame k (1-based) of a shrink_tristana tag with the new bell; idle: the idle's first frame before. (frame, how)"""
    dx, dy, share = find(a, idle, OLD)
    if share == 1:
        return same_bell(a, dx, dy), f"idle's bell at {dx:+d},{dy:+d}"
    if (tag, k) == ("hit", 1):
        return same_bell(a, *HIT1, barrel_end=False), "its own bell"
    return a, None


def fix_run(a, run1):
    """A run frame with the new bell; run1: the run's first frame before."""
    dx, dy, share = find(a, run1, RUN_OLD)
    if share < 1:
        raise ValueError(f"the run's bell is not in this frame ({share:.0%})")
    return same_bell(a, RUN[0] + dx, RUN[1] + dy, barrel_end=False)

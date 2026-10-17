#!/usr/bin/env python3
"""Tristana's two ears the same: the far (right) ear erased and the near (left) one mirrored onto that side.

The user: "小炮也有这问题左右耳朵做的不一样" - the design's right ear was a smaller, plainer one (no dark rose
inside). Of A (both the left ear) and B (both the right one) on the idle's first frame the user picked A.

A library: shrink_tristana.py runs fix on every frame it wrote, last (the turned frames and the attack are still made
from the frames as they were, so their bodies stay as approved), fix_tristana_run.py on the run (Codex's own head
drawing: one row taller between the goggles and the face, the face and the ears the design's). Frames turned as a
whole keep their body: quarter turns are undone and done again,
the others (W's 5th and the death's 5th at 45 degrees, R's 5th and the death's 4th that Codex turned about 22) get the
idle's new ear turned with RotSprite like their head (a mirror about the leaning line came out jagged).

The ears are found by colour: the ear's pink, the dark rose inside and the lilac edge (the face's lilac is the same
colour, so only the biggest piece in the box counts), and the outline squares round it - the tan strap square under the
left ear turns outline on the right, closing the lobe. The old ear and its outer outline go (outline squares that also
hold another part's edge stay), the mirror goes on squares that are empty, the old ear's or outline, never over the
hair, the face, a hand or the cannon (a single square it goes round takes the ear's colour), and every empty square
beside the new ear's colours gets the outline.
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rig_nocturne import rotsprite  # noqa: E402

OUTLINE = (0x19, 0x14, 0x21)
STRAP = (0xCE, 0x95, 0x60)
EAR = {(0xF6, 0x99, 0xB4), (0xC3, 0x5C, 0x80), (0xDF, 0xB4, 0xEB)}    # pink, dark rose, lilac edge
AMBER = (246, 186, 48)
# on the idle's first frame (96x96 cell): the mirror line (x' = AXIS - x, the goggles' and the hair's middle), the ears'
# boxes (x0, y0, x1, y1 inclusive), and the head's middle used to find it in other frames: the hair and the face
# between the ears, from under the goggles to the chin, the eyes' rows left out (shut in the hit)
AXIS = 87
LEFT = (25, 52, 34, 62)
RIGHT = (49, 52, 62, 62)
FIND = (35, 53, 51, 63)
FIND_SKIP_ROWS = range(58, 62)
FOUND = 0.9                      # share of the middle that must match
JOINT = (52, 56)                 # where the right ear meets the hair
MIDDLE = (43.5, 55.5)            # the head's middle, on the mirror line
# frames turned as a whole after they were drawn (shrink_tristana.py: TURNED, DEAD_PLAN; FACE_AT for Codex's own):
# quarter turns (np.rot90 k, + counter-clockwise) are undone, given the ears like an upright frame and done again; the
# rest (degrees clockwise) keep their body and get the idle's new ear turned with RotSprite where their head's is
QUARTER = {("skill2", 4): -1, ("dead", 6): 1, ("dead", 7): 1, ("dead", 8): 1}
TURNED = {("skill2", 5): 45, ("dead", 5): -45, ("ult", 5): 22, ("dead", 4): 22}
CORE = (30, 46, 58, 66)          # the head's middle box for turned frames: x0, y0, x1, y1 exclusive, centred on MIDDLE


def col(a, y, x):
    return tuple(int(v) for v in a[y, x, :3])


def inside(a, y, x):
    return 0 <= y < a.shape[0] and 0 <= x < a.shape[1]


def find(frame, idle):
    """(dx, dy, share): where the idle's head middle sits in the frame, relative to the idle."""
    x0, y0, x1, y1 = FIND
    tpl = idle[y0:y1 + 1, x0:x1 + 1]
    m = tpl[..., 3] > 0
    for r in FIND_SKIP_ROWS:
        m[r - y0] = False
    th, tw = tpl.shape[:2]
    n = m.sum()
    best = (0.0, 0, 0)
    for y in range(frame.shape[0] - th + 1):
        for x in range(frame.shape[1] - tw + 1):
            s = ((frame[y:y + th, x:x + tw] == tpl).all(-1) & m).sum() / n
            if s > best[0]:
                best = (s, x - x0, y - y0)
    return best[1], best[2], best[0]


def ear(a, box):
    """The ear in the box: its colour squares (the biggest 8-connected piece) and the outline (or strap) squares round
    them."""
    x0, y0, x1, y1 = box
    m = np.zeros(a.shape[:2], bool)
    for y in range(max(y0, 0), min(y1, a.shape[0] - 1) + 1):
        for x in range(max(x0, 0), min(x1, a.shape[1] - 1) + 1):
            if a[y, x, 3] and col(a, y, x) in EAR:
                m[y, x] = True
    seen = np.zeros_like(m)
    best = []
    for y, x in zip(*np.nonzero(m)):
        if seen[y, x]:
            continue
        q, comp = deque([(y, x)]), []
        seen[y, x] = True
        while q:
            cy, cx = q.popleft()
            comp.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if inside(m, ny, nx) and m[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
        if len(comp) > len(best):
            best = comp
    m[:] = False
    for y, x in best:
        m[y, x] = True
    ring = np.zeros_like(m)
    for y, x in best:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = y + dy, x + dx
                if inside(a, ny, nx) and a[ny, nx, 3] and col(a, ny, nx) in (OUTLINE, STRAP) and not m[ny, nx]:
                    ring[ny, nx] = True
    return m, ring


def erase(a, m, ring):
    """The ear's squares go, and its outline squares that hold no other part's edge."""
    b = a.copy()
    rest = (a[..., 3] > 0) & ~m & ~ring
    b[m] = 0
    for y, x in zip(*np.nonzero(ring)):
        if not any(inside(a, y + dy, x + dx) and rest[y + dy, x + dx] and col(a, y + dy, x + dx) != OUTLINE
                   for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
            b[y, x] = 0
    return b


def paintable(a, b, y, x, old):
    """A square the new ear may cover: empty now, the old ear's, or an outline square."""
    return inside(b, y, x) and (b[y, x, 3] == 0 or old[y, x] or col(b, y, x) == OUTLINE)


def close(b, box):
    """Every empty square 4-beside an ear colour in the box (and a square round it) gets the outline."""
    x0, y0, x1, y1 = box
    add = []
    for y in range(y0 - 1, y1 + 2):
        for x in range(x0 - 1, x1 + 2):
            if inside(b, y, x) and b[y, x, 3] == 0 and any(
                    inside(b, y + dy, x + dx) and b[y + dy, x + dx, 3] and col(b, y + dy, x + dx) in EAR
                    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0))):
                add.append((y, x))
    for y, x in add:
        b[y, x, :3] = OUTLINE
        b[y, x, 3] = 255
    return b


def specks(b, box):
    """A square of another colour with the ear's colours on all four sides (a pixel the new ear went round) takes the
    colour most of them have."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not inside(b, y, x) or not b[y, x, 3] or col(b, y, x) in EAR:
                continue
            nb = [col(b, y + dy, x + dx) for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0))
                  if inside(b, y + dy, x + dx) and b[y + dy, x + dx, 3]]
            if len(nb) == 4 and all(c in EAR for c in nb):
                b[y, x, :3] = max(set(nb), key=nb.count)
    return b


def shift(box, dx, dy):
    x0, y0, x1, y1 = box
    return x0 + dx, y0 + dy, x1 + dx, y1 + dy


def same_ears(a, dx=0, dy=0):
    """The frame with its right ear replaced by its left one mirrored; the head dx, dy from the idle's."""
    left, right, axis = shift(LEFT, dx, dy), shift(RIGHT, dx, dy), AXIS + 2 * dx
    ml, rl = ear(a, left)
    mr, rr = ear(a, right)
    old = mr | rr
    b = erase(a, mr, rr)
    lo, hi = axis - left[2], axis - left[0]
    for y, x in zip(*np.nonzero(ml | rl)):
        nx = axis - x
        if paintable(a, b, y, nx, old) and (ml[y, x] or b[y, nx, 3] == 0):
            b[y, nx] = a[y, x]
            if rl[y, x]:
                b[y, nx, :3] = OUTLINE
                b[y, nx, 3] = 255
    box = (min(lo, right[0]), right[1], max(hi, right[2]), right[3])
    return close(specks(b, box), box)


def ear_sprite(idle):
    """The new right ear of the (already fixed) idle as a sprite, and where it meets the hair in it."""
    m, ring = ear(idle, RIGHT)
    ys, xs = np.nonzero(m | ring)
    y0, x0 = ys.min(), xs.min()
    s = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1, 4), np.uint8)
    sub = (m | ring)[y0:, x0:][:s.shape[0], :s.shape[1]]
    s[sub] = idle[y0:y0 + s.shape[0], x0:x0 + s.shape[1]][sub]
    return s, (JOINT[0] - x0, JOINT[1] - y0)


def locate(a, idle, angle):
    """Where the idle head's MIDDLE is in a frame turned `angle` degrees clockwise: the head between the ears (no
    ears, no eyes), turned the same way nearest-neighbour, matched square for square."""
    x0, y0, x1, y1 = CORE
    core = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    fx0, fy0, fx1, fy1 = FIND
    core[fy0 - y0:fy1 + 1 - y0, fx0 - x0:fx1 + 1 - x0] = idle[fy0:fy1 + 1, fx0:fx1 + 1]
    for r in FIND_SKIP_ROWS:
        core[r - y0] = 0
    t = np.asarray(Image.fromarray(core).rotate(-angle, resample=Image.NEAREST, expand=True))
    m = t[..., 3] > 0
    th, tw = m.shape
    best = (-1, 0, 0)
    for y in range(a.shape[0] - th + 1):
        for x in range(a.shape[1] - tw + 1):
            s = ((a[y:y + th, x:x + tw] == t).all(-1) & m).sum()
            if s > best[0]:
                best = (s, x, y)
    s, x, y = best
    return (x + (tw - 1) / 2, y + (th - 1) / 2), s / m.sum()


def turned(angle, centre, p):
    """The idle's point p in a frame turned `angle` degrees clockwise about `centre` (the idle's MIDDLE there)."""
    t = np.radians(angle)
    return np.array(centre) + np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]) @         (np.array(p, float) - np.array(MIDDLE))


def same_ears_turned(a, idle, new_idle, angle):
    """same_ears for a frame turned `angle` degrees clockwise: the old right ear (in the idle's RIGHT box turned
    there) goes, the new idle's right ear is turned with RotSprite and put where the turned head's ear meets the hair."""
    centre, share = locate(a, idle, angle)
    x0, y0, x1, y1 = RIGHT
    corners = np.array([turned(angle, centre, p) for p in ((x0, y0), (x1, y0), (x0, y1), (x1, y1))])
    right = (int(np.floor(corners[:, 0].min())) - 1, int(np.floor(corners[:, 1].min())) - 1,
             int(np.ceil(corners[:, 0].max())) + 1, int(np.ceil(corners[:, 1].max())) + 1)
    s, j = ear_sprite(new_idle)
    r, (rx, ry) = rotsprite(s, j, -angle)
    at = turned(angle, centre, JOINT)
    mr, rr = ear(a, right)
    old = mr | rr
    b = erase(a, mr, rr)
    for y, x in zip(*np.nonzero(r[..., 3] > 0)):
        Y, X = int(round(at[1] + y - ry)), int(round(at[0] + x - rx))
        if paintable(a, b, Y, X, old) and (tuple(int(v) for v in r[y, x, :3]) != OUTLINE or b[Y, X, 3] == 0):
            b[Y, X] = r[y, x]
    box = (right[0] - 4, right[1] - 4, right[2] + 4, right[3] + 4)
    return close(specks(b, box), box), share


def fix(tag, k, a, idle, new_idle):
    """Frame k (1-based) of a tag with the same ears; idle: the idle's first frame before, new_idle: after."""
    if (tag, k) in QUARTER:
        q = QUARTER[(tag, k)]
        up = np.rot90(a, -q).copy()
        dx, dy, share = find(up, idle)
        return np.rot90(same_ears(up, dx, dy), q).copy(), share
    if (tag, k) in TURNED:
        return same_ears_turned(a, idle, new_idle, TURNED[(tag, k)])
    dx, dy, share = find(a, idle)
    return same_ears(a, dx, dy), share


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    idle = np.asarray(Image.open(os.path.join(here, "..", "..", "assets", "source", "native", "tristana_idle.png"))
                      .convert("RGBA"))[4::8, 4::8][0:96, 0:96].copy()
    print(find(idle, idle))
    sys.exit(0)

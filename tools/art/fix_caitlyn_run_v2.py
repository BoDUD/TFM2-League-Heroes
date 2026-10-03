#!/usr/bin/env python3
"""Caitlyn's run on the second design: the design's upper body on legs posed frame by frame, crossing (2026-10-03).

    python tools/art/fix_caitlyn_run_v2.py --cells JSON --out PNG

Codex's v2 run kept one leg kicked up behind in all 8 frames (no crossing step), and its legs-only redo shrank the legs
back into short shuffling steps - the players' complaint. The user: 「你来修复吧 codex太笨了」. As the first design's run
(tools/art/fix_caitlyn_run.py, approved: 「挺不错的」), each frame is
- the design (assets/source/caitlyn/design_v2) from the top down to its skirt's lining (2 rows over the standing
  point): head, hat, hair, the rifle carried as in the idle, the skirt - lowered by STEP (League's pelvis);
- two legs as long as the design's: a hip -> knee -> ankle -> toe bone line (the knee from the hip and the ankle, two
  bones, always forward; the foot square to the shin), every square within 1 of it filled with the design's leg at
  the same length along the leg (navy tights, the gold garter, the brown knee pad, the gold boot top, the boot, the
  buckle; the foot's 3 x 2 squares turned with the shin) and the side of the bone (the two fill columns), then one
  outline ring round each leg. Turning the 4-square-wide design leg with RotSprite gave broken doubled outlines;
- the ankles after CYCLE (League's jog, as the first run): the planted leg nearly upright under her, sliding back
  and pushing off; the other heel kicked up behind, swung through past it and landed in front; the legs swap every
  half cycle (the near foot passes the far one between frames 2 and 3, and back between 6 and 7). The far leg is
  drawn first, the near one with its ring over it, the upper body over both.
Writes the 4 x 2 strip of 96 x 96 cells at 8x (the cells and pivots of the run in the cells table).
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

DESIGN = os.path.join(ROOT, "assets", "source", "caitlyn", "design_v2", "caitlyn_design_v2_1x.png")
PIVOT = (64, 88)                 # the design's standing point on its canvas
Z = 8
CUT = -2                         # the upper body: rows to 2 over the standing point (the skirt's lining)
FILL = (-4, -3)                  # the design's left leg: its two fill columns (outline -5 and -2)
FOOT = (-4, -3, -2)              # its foot's columns in rows 9 and 10 (the sole's outline in row 11)
# the design leg's bone, squares from the standing point: hip at row -2, knee in the knee pad's row, ankle between
# the foot's two rows; the toe one square on
HIP_Y, KNEE_Y, ANKLE_Y, TOE = -2.0, 2.0, 9.5, 1.0
LT, LS = KNEE_Y - HIP_Y, ANKLE_Y - KNEE_Y
R = 1.0                          # squares within R of the bone are the leg (two squares wide upright)
HIPS = {"near": -2.5, "far": 0.5}  # the hips' x: 3 apart as the first run's, between the design's legs
STEP = [0, 1, 2, 1, 0, 1, 2, 1]  # the upper body's rows down per frame (League's pelvis)
# one leg's cycle: (ankle x from its hip, rows lifted); the near leg at phase k in frame k + 1, the far one 4 phases on
CYCLE = [(1.0, 0), (0.0, 0), (-1.0, 0), (-3.0, 1),   # planted under her sliding back, pushing off
         (-4.5, 4), (-4.5, 7), (3.0, 4), (3.5, 1)]    # heel up behind, kicked high, swung through, landing


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) else pre + p


def design():
    return np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))


def materials(d):
    px, py = PIVOT
    rows = {r: (d[py + r, px + FILL[0]].copy(), d[py + r, px + FILL[1]].copy()) for r in range(-1, 9)}
    foot = {(r, i): d[py + r, px + c].copy() for r in (9, 10) for i, c in enumerate(FOOT)}
    ring = d[py + 11, px + FILL[0]].copy()
    upper = d.copy()
    upper[py + CUT + 1:] = 0
    return rows, foot, ring, upper


def knee(hip, ankle):
    hx, hy = hip
    ax, ay = ankle
    dx, dy = ax - hx, ay - hy
    dist = math.hypot(dx, dy)
    if dist >= LT + LS - 1e-6:
        return hx + dx * LT / (LT + LS), hy + dy * LT / (LT + LS)
    a = (LT * LT - LS * LS + dist * dist) / (2 * dist)
    h = math.sqrt(max(0.0, LT * LT - a * a))
    mx, my = hx + dx * a / dist, hy + dy * a / dist
    nx, ny = -dy / dist, dx / dist
    if nx < 0:                                      # the knee forward (to the right)
        nx, ny = -nx, -ny
    return mx + nx * h, my + ny * h


def seg(p, a, b):
    """(distance, t along a -> b in squares, side: + right of the direction) of point p to segment a -> b."""
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    n = math.hypot(vx, vy)
    ux, uy = vx / n, vy / n
    t = max(0.0, min(n, (p[0] - ax) * ux + (p[1] - ay) * uy))
    qx, qy = ax + ux * t, ay + uy * t
    side = (p[0] - qx) * uy - (p[1] - qy) * ux     # (u_y, -u_x): right of a downward bone
    return math.hypot(p[0] - qx, p[1] - qy), t, side


def leg_pixels(hip, ankle, mats):
    """{(x, y): colour} of one leg's fill, squares relative to the standing point."""
    rows, foot, _, _ = mats
    k = knee(hip, ankle)
    sx, sy = ankle[0] - k[0], ankle[1] - k[1]
    n = math.hypot(sx, sy)
    sx, sy = sx / n, sy / n
    ux, uy = sy, -sx                                 # the foot: square to the shin, forward
    toe = (ankle[0] + ux * TOE, ankle[1] + uy * TOE)
    xs = (hip[0], k[0], ankle[0], toe[0])
    ys = (hip[1], k[1], ankle[1], toe[1])
    out = {}
    for y in range(int(math.floor(min(ys))) - 2, int(math.ceil(max(ys))) + 3):
        for x in range(int(math.floor(min(xs))) - 2, int(math.ceil(max(xs))) + 3):
            p = (float(x), float(y))
            d1, t1, s1 = seg(p, hip, k)
            d2, t2, s2 = seg(p, k, ankle)
            d3, _, _ = seg(p, ankle, toe)
            if min(d1, d2, d3) > R:
                continue
            # the foot: past the ankle's row along the shin, or nearest the foot
            lu = (x - ankle[0]) * ux + (y - ankle[1]) * uy
            lv = (x - ankle[0]) * sx + (y - ankle[1]) * sy
            if lv > -1.0 and (d3 < min(d1, d2) or lv > -0.5):
                i = int(np.argmin([abs(lu - c) for c in (-0.5, 0.5, 1.5)]))
                out[(x, y)] = foot[(9 if lv < 0 else 10, i)]
                continue
            if d1 <= d2:
                along, side = t1, s1
            else:
                along, side = LT + t2, s2
            r = int(min(8, max(-1, round(HIP_Y + along))))
            out[(x, y)] = rows[r][0 if side < 0 else 1]
    return out


def ring_of(cells):
    ring = set()
    for x, y in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells:
                ring.add(q)
    return ring


def frame(mats, k, pivot, cell):
    _, _, ringc, upper = mats
    c = np.zeros((cell[1], cell[0], 4), np.uint8)
    dy = STEP[k]

    def put(x, y, col):
        tx, ty = pivot[0] + x, pivot[1] + y
        if 0 <= tx < cell[0] and 0 <= ty < cell[1]:
            c[ty, tx] = col

    for name, phase in (("far", (k + 4) % 8), ("near", k)):
        ax, lift = CYCLE[phase]
        hip = (HIPS[name], HIP_Y + dy)
        ankle = (HIPS[name] + ax, ANKLE_Y - lift)
        px = leg_pixels(hip, ankle, mats)
        for q in ring_of(px):
            put(q[0], q[1], ringc)
        for (x, y), col in px.items():
            put(x, y, col)
    ys, xs = np.nonzero(upper[..., 3])
    for y, x in zip(ys, xs):
        put(x - PIVOT[0], y - PIVOT[1] + dy, upper[y, x])
    c[pivot[1] + 12:] = 0                            # nothing under the soles' row
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cells = json.load(open(lp(a.cells), encoding="utf-8"))
    cell = cells["cell"][:2]
    run = cells["tags"]["run"]
    mats = materials(design())
    strip = np.zeros((2 * cell[1], 4 * cell[0], 4), np.uint8)
    for k, fr in enumerate(run):
        strip[(k // 4) * cell[1]:(k // 4 + 1) * cell[1], (k % 4) * cell[0]:(k % 4 + 1) * cell[0]] = frame(mats, k, fr["pivot"], cell)
    Image.fromarray(np.repeat(np.repeat(strip, Z, 0), Z, 1)).save(lp(a.out))
    print("wrote", a.out)


if __name__ == "__main__":
    main()

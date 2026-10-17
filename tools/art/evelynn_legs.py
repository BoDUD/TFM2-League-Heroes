"""Evelynn's legs as a two-bone rig on the design's own near leg (tools/art/fix_evelynn_strips.py uses it).

The design's legs begin under the belt (row 84): the pink panels are the thighs (rows 85-91), the knee is row 92, the
shin rows 93-97 (one dark-blue square inside an indigo ring) and the foot rows 98-99. One leg - the near one, centred
on column 58 - serves for both, so they are always alike (Kai'Sa's run: 「左腿细右腿粗？」). A posed leg is drawn
along its bones, never resampled as a picture: each square within the limb takes the design's fill colour at the same
length down the bone and the same offset across it (the thigh's rows for the thigh, the shin's for the shin), then one
indigo ring goes round it (RotSprite on parts this thin broke Caitlyn's outlines), and the foot is the design's own,
flat on the ground under the ankle.
"""
import math

import numpy as np

LEG_X = 58                       # the near leg's centre column in the design
HIP_Y, KNEE_Y, FOOT_Y = 85, 92, 98
THIGH, SHIN = KNEE_Y - HIP_Y, FOOT_Y - KNEE_Y          # 7 and 6 squares
RING = (0x1E, 0x16, 0x46)        # the legs' outline colour in the design
DARK = {(0x12, 0x0C, 0x1C), (0x1E, 0x16, 0x46)}        # outline colours: not part of the fill texture


def texture(d):
    """{row: {dx: rgb}} - the near leg's fill (outline squares left out), rows 85-97, columns 56-60."""
    tex = {}
    for y in range(HIP_Y, FOOT_Y):
        row = {}
        for x in range(LEG_X - 2, LEG_X + 3):
            if d[y, x, 3] and tuple(int(v) for v in d[y, x, :3]) not in DARK:
                row[x - LEG_X] = tuple(int(v) for v in d[y, x, :3])
        tex[y] = row
    # the crotch's lilac and dark blue reach into the thigh's right side on rows 85 and 87: the thigh is pink there
    tex[HIP_Y] = {dx: c for dx, c in tex[HIP_Y].items() if dx <= 0}
    tex[HIP_Y + 1] = {dx: c for dx, c in tex[HIP_Y + 1].items() if dx <= 1}
    tex[HIP_Y + 2] = {dx: c for dx, c in tex[HIP_Y + 2].items() if dx <= 1}
    return tex


def foot(d):
    """The design's near foot (rows 98-99, columns 56-61) with its ankle point (58.5, 98.0)."""
    out = {}
    for y in (FOOT_Y, FOOT_Y + 1):
        for x in range(LEG_X - 2, LEG_X + 4):
            if d[y, x, 3]:
                out[(x - LEG_X, y - FOOT_Y)] = tuple(int(v) for v in d[y, x, :3])
    return out


def solve(hip, ankle):
    """Knee and ankle for a hip and a wanted ankle (continuous canvas coordinates), the knee bent forward (+x); an
    ankle out of reach is pulled in along the line."""
    hx, hy = hip
    vx, vy = ankle[0] - hx, ankle[1] - hy
    dist = math.hypot(vx, vy)
    ux, uy = vx / dist, vy / dist
    if dist >= THIGH + SHIN - 1e-6:
        knee = (hx + ux * THIGH, hy + uy * THIGH)
        return knee, (hx + ux * (THIGH + SHIN), hy + uy * (THIGH + SHIN))
    cos_a = (THIGH ** 2 + dist ** 2 - SHIN ** 2) / (2 * THIGH * dist)
    a = math.acos(max(-1.0, min(1.0, cos_a)))
    px, py = uy, -ux                                   # perpendicular: forward (+x) when the bone points down
    if px < 0:
        px, py = -px, -py
    knee = (hx + THIGH * (math.cos(a) * ux + math.sin(a) * px), hy + THIGH * (math.cos(a) * uy + math.sin(a) * py))
    return knee, ankle


def draw(can, tex, ft, hip, ankle):
    """One leg on the canvas: thigh hip -> knee, shin knee -> ankle, skinned with the texture, ringed, the foot under
    the ankle. Returns the ankle used."""
    knee, ankle = solve(hip, ankle)
    fill = {}
    for (j0, j1, row0, n) in ((hip, knee, HIP_Y, THIGH), (knee, ankle, KNEE_Y, SHIN)):
        L = math.hypot(j1[0] - j0[0], j1[1] - j0[1])
        ux, uy = (j1[0] - j0[0]) / L, (j1[1] - j0[1]) / L
        nx, ny = uy, -ux                               # across the bone: +x when it points down
        x0, x1 = int(min(j0[0], j1[0])) - 4, int(max(j0[0], j1[0])) + 5
        y0, y1 = int(min(j0[1], j1[1])) - 4, int(max(j0[1], j1[1])) + 5
        for y in range(y0, y1):
            for x in range(x0, x1):
                cx, cy = x + 0.5 - j0[0], y + 0.5 - j0[1]
                t = cx * ux + cy * uy
                s = cx * nx + cy * ny
                if not 0 <= t < L:
                    continue
                row = row0 + min(n - 1, int(t * n / L))
                dx = int(math.floor(s + 0.5))
                if dx in tex[row]:
                    fill[(x, y)] = tex[row][dx]
    ring = set()
    for (x, y) in fill:
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if (x + ex, y + ey) not in fill:
                    ring.add((x + ex, y + ey))
    H, W = can.shape[:2]
    for (x, y) in ring:
        if 0 <= x < W and 0 <= y < H:
            can[y, x, :3] = RING
            can[y, x, 3] = 255
    for (x, y), c in fill.items():
        if 0 <= x < W and 0 <= y < H:
            can[y, x, :3] = c
            can[y, x, 3] = 255
    fx, fy = int(math.floor(ankle[0])), int(math.floor(ankle[1] + 0.5))
    for (dx, dy), c in ft.items():
        x, y = fx + dx, fy + dy
        if 0 <= x < W and 0 <= y < H:
            can[y, x, :3] = c
            can[y, x, 3] = 255
    return ankle


HIP_NEAR = (LEG_X + 0.5, float(HIP_Y))          # the near thigh's top
HIP_FAR = (LEG_X + 5.5, float(HIP_Y) + 0.5)      # the far thigh's top (the design's far panel starts at column 62-63)
STAND_NEAR = (LEG_X + 0.5, float(FOOT_Y))        # the idle's near ankle
STAND_FAR = (LEG_X + 8.5, float(FOOT_Y))         # the idle's far ankle (its foot at columns 66-71)


def body(d, is_back_lasher):
    """The design without legs and back lasher: everything over the belt (row 84), the crotch between the thighs
    (rows 85-87, columns 59-62) and the near hand's claw (rows 85-86, columns 49-53)."""
    out = np.zeros_like(d)
    ys, xs = np.nonzero(d[..., 3] > 0)
    for y, x in zip(ys, xs):
        keep = (y <= HIP_Y - 1 and not is_back_lasher(x, y)) or (HIP_Y <= y <= HIP_Y + 2 and 59 <= x <= 62) or \
               (HIP_Y <= y <= HIP_Y + 1 and 49 <= x <= 53)
        if keep:
            out[y, x] = d[y, x]
    return out

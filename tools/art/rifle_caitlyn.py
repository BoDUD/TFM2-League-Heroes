"""league_caitlyn's rifle drawn straight, square by square, in her design's own colours (hd/design.png): the user,
2026-10-23, 「还有枪别做歪」 then 「不让codex补画了 你想办法修好」 - Codex's redrawn frames held the rifle at a
different angle, length and thickness every frame with uneven pixel steps.

    python tools/art/rifle_caitlyn.py --review DIR      # the rifle at every way it takes, 8x

master(n): the rifle level, pointing right, n squares from the stock's end to the muzzle (the design's is 59): the
stock (an open gold frame round an ivory plate), the grip and trigger guard under the receiver, the receiver (gold
rails, ivory plate, the cyan energy line) with two round blue-lensed scopes on top, the barrel (2 squares: light and
dark gold) and the muzzle cap; a 1-square near-black outline. Its parts keep their share of n.
rifle(ax, up): the rifle along a slope whose steps are even - level (1, 0), 1 in 2 (2, +-1), 1 in 1 (1, 1) - drawn by
moving each column of the master as one piece (floor(x * up / ax) squares), so every edge steps exactly the same way and
the cross-section never changes; its length along the slope stays LENGTH (fewer columns as it tilts). Steeper ways
(63.4 and 90 degrees) are these turned a quarter (np.rot90, lossless); pointing left, mirrored. WAYS lists all 16 with
their grip point (where the near hand holds it: GRIP of the length from the stock) for placing.
"""
import argparse
import math
import os

import numpy as np
from PIL import Image

LENGTH = 59
GRIP = 0.27                              # her trigger hand, from the stock's end
O = (14, 0, 21)                          # the design's outline
G1, G2, G3, G4 = (251, 204, 74), (238, 175, 49), (217, 152, 38), (186, 119, 29)   # gold, light to dark
G5 = (160, 97, 29)
IV, IV2 = (247, 237, 206), (242, 221, 175)                                        # ivory
C1, C2, B1, B2 = (97, 212, 241), (9, 185, 249), (8, 158, 237), (6, 111, 206)      # cyan / lens blues
H = 13                                   # rows of the master; the barrel's top row is BAR
BAR = 6


def master(n=LENGTH):
    """The level rifle, n columns: stock 22 %, receiver 34 %, barrel the rest, the muzzle cap 2 columns."""
    stock = max(8, round(n * 0.22))
    recv = max(12, round(n * 0.34))
    muz = 2
    bar = n - stock - recv - muz
    a = np.zeros((H, n, 4), np.uint8)

    def put(x, y, c):
        if 0 <= x < n and 0 <= y < H:
            a[y, x, :3] = c
            a[y, x, 3] = 255
    # the stock: an open frame (top rail, bottom rail, butt plate) round an ivory plate, tapering into the grip
    for x in range(stock):
        f = x / max(1, stock - 1)
        top, bot = BAR - 1 + round(f * 1), BAR + 4 - round(f * 1)
        for y in range(top, bot + 1):
            c = G2 if y == top else G4 if y == bot else IV if (x % 5) else IV2
            if x < 2:
                c = G3 if y not in (top, bot) else G2
            put(x, y, c)
    # the grip and trigger guard under the receiver's start
    for x in range(stock, stock + 4):
        for y in range(BAR + 3, BAR + 5):
            put(x, y, G4 if y == BAR + 4 else G3)
    # the receiver: gold rail, ivory plate with the cyan energy line, dark rail
    x0 = stock
    for x in range(x0, x0 + recv):
        put(x, BAR - 1, G1)
        put(x, BAR, IV)
        put(x, BAR + 1, C1 if (x - x0) % 6 < 4 else C2)
        put(x, BAR + 2, G3)
    # two scopes on top: gold rims round 2 x 2 lenses
    for sx in (x0 + recv // 5, x0 + recv * 3 // 5):
        for x in range(sx, sx + 4):
            for y in range(BAR - 5, BAR - 1):
                rim = x in (sx, sx + 3) or y in (BAR - 5, BAR - 2)
                if rim:
                    put(x, y, G2 if y == BAR - 5 else G3)
                else:
                    put(x, y, C1 if (x == sx + 1 and y == BAR - 4) else B1 if y == BAR - 4 else B2)
        put(sx + 1, BAR - 2, G4)                          # the mount
        put(sx + 2, BAR - 2, G4)
    # the barrel: 2 squares, light over dark, a band every 8
    x1 = x0 + recv
    for x in range(x1, x1 + bar):
        band = (x - x1) % 8 == 7
        put(x, BAR, G2 if band else G1)
        put(x, BAR + 1, G4 if band else G3)
    # the muzzle cap: 3 rows
    for x in range(x1 + bar, n):
        for y, c in ((BAR - 1, G1), (BAR, G2), (BAR + 1, G3), (BAR + 2, G5)):
            put(x, y, c)
    return outline(a)


def outline(a):
    op = a[..., 3] > 0
    pad = np.pad(op, 1)
    ring = np.zeros_like(pad)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ring |= np.roll(np.roll(pad, dy, 0), dx, 1)
    ring &= ~pad
    out = np.zeros((a.shape[0] + 2, a.shape[1] + 2, 4), np.uint8)
    out[1:-1, 1:-1] = a
    out[ring] = O + (255,)
    return out


def rifle(ax, up):
    """The rifle along the slope (ax across, up squares up; up < 0 falls), its length along the slope LENGTH."""
    k = up / ax
    n = round(LENGTH / math.hypot(1, k))
    m = master(n)
    h, w = m.shape[:2]
    lift = [math.floor(x * abs(k)) for x in range(w)]
    span = max(lift)
    out = np.zeros((h + span, w, 4), np.uint8)
    for x in range(w):
        y0 = span - lift[x] if k > 0 else lift[x]
        out[y0:y0 + h, x] = m[:, x]
    # where the grip and the axis are: the barrel's top row at the grip column
    gx = 1 + round((n - 1) * GRIP)
    gy = (span - lift[gx] if k > 0 else lift[gx]) + 1 + BAR + 0.5
    return out, (gx + 0.5, gy)


def ways():
    """{degrees: (picture, grip)} for the 16 ways: the five drawn slopes as they are, turned a quarter either way
    (lossless; the scopes stay on the rifle's upper side as a real turn keeps them) and mirrored left-right (pointing
    left). A way already given by a less-turned picture keeps that one."""
    base = [(0.0, rifle(1, 0)), (math.degrees(math.atan2(1, 2)), rifle(2, 1)),
            (-math.degrees(math.atan2(1, 2)), rifle(2, -1)), (45.0, rifle(1, 1)), (-45.0, rifle(1, -1))]
    out = {}

    def add(ang, im, g):
        key = round(((ang + 180) % 360) - 180, 1)
        if key == -180.0:
            key = 180.0
        out.setdefault(key, (np.ascontiguousarray(im), g))
    for turn in (0, 1, -1):
        for ang, (im, (gx, gy)) in base:
            h, w = im.shape[:2]
            if turn == 1:
                im2, g = np.rot90(im, 1), (gy, w - gx)
            elif turn == -1:
                im2, g = np.rot90(im, -1), (h - gy, gx)
            else:
                im2, g = im, (gx, gy)
            a2 = ang + 90 * turn
            add(a2, im2, g)
            add(180 - a2, im2[:, ::-1], (im2.shape[1] - g[0], g[1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True)
    a = ap.parse_args()
    os.makedirs(a.review, exist_ok=True)
    W = ways()
    z = 8
    cells = []
    for ang in sorted(W):
        im, (gx, gy) = W[ang]
        big = np.repeat(np.repeat(im, z, 0), z, 1)
        can = Image.new("RGBA", (big.shape[1] + 20, big.shape[0] + 20), (200, 205, 195, 255))
        can.alpha_composite(Image.fromarray(big), (10, 10))
        px = can.load()
        for dx in range(-3, 4):
            px[int(10 + gx * z) + dx, int(10 + gy * z)] = (255, 0, 0, 255)
        cells.append((ang, can))
    Wd = sum(c.width for _, c in cells[:8]) + 80
    rows = [cells[:8], cells[8:]]
    Ht = sum(max(c.height for _, c in r) for r in rows) + 40
    sheet = Image.new("RGB", (max(Wd, sum(c.width for _, c in cells[8:]) + 80), Ht), (255, 255, 255))
    y = 10
    for r in rows:
        x = 10
        for ang, c in r:
            sheet.paste(c.convert("RGB"), (x, y))
            x += c.width + 10
        y += max(c.height for _, c in r) + 10
    sheet.save(os.path.join(a.review, "rifles.png"))
    print(sorted(round(k, 1) for k in W))


if __name__ == "__main__":
    main()

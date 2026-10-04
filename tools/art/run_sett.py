#!/usr/bin/env python3
"""Sett's run on the design's own body (tools/art/strips_sett.py puts it in the run strip).

    python tools/art/run_sett.py --review <png>      # the eight frames next to the idle, 6x

The user, on the run made from Codex's drafts: 「跑步姿势有点怪吧？而且好像还有点变形」 - every frame's upper body was
Codex's own drawing (the torso, the mantle, the coat and the arms a different shape and narrower than the idle's in
each), the drawn legs stood in a stiff A in three frames, and the hips and the head rose and fell at random. As
Sivir's run (tools/art/rig_sivir_run.py, the version the user approved: 「新版很不错」):
  - the upper body is the design itself above the belt (its head, torso, mantle, clasps, coat fronts and belt), the
    arms taken off, one rigid block in every frame; it leans forward (each row shifted LEAN of a square per row over
    the belt) and sinks with the stride (BOB: low after each contact, high on the push);
  - the legs: each foot placed along the run cycle (ahead on the contact, drawn back under the body, off the toe,
    kicked up behind, swung through, reaching), the knee solved forward, both the design's length and width in the
    trousers' shades with the gold stripe and the design's shoe (strips_sett.leg), the hips where the design's are;
  - the arms pump against the legs, bent at the elbow (more ahead than behind): the upper arm in the skin's shades,
    the forearm in the bandage's, the design's own fist at the wrist; the far arm behind the body, the near one over;
  - the coat's tails stream back from the waist behind the legs, the hem in gold, fluttering a square.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pack_sett_strips as K  # noqa: E402
import strips as G  # noqa: E402
import strips_sett as R  # noqa: E402

PIVOT = (64, 88)                 # the design canvas's; its soles on row 99
BELT = 78                        # the design's last row above the trousers (the belt)
LEAN = 0.09                      # squares a row the upper body shifts forward over the belt (the head ~1.8 ahead)
BOB = [2, 3, 3, 1, 2, 3, 3, 1]   # rows the body sits lower: low after each contact (frames 0 and 4), high on the push
HIPS = {"near": 61.0, "far": 66.0}
HIP_ROW = 79.5
ANKLE_ROW = 95.0                 # the shoe's top row (the soles' row 99)
# one foot over the cycle (phase 0 = its contact): (ankle x from its hip, lift of the sole) - a shorter, heavier stride
# than Sivir's (her 6 ahead / 7 behind read as a stiff A on his bulk)
FOOT = [(4.5, 0), (2.0, 0), (-0.5, 0), (-3.0, 0), (-5.5, 1), (-5.0, 4.5), (-1.0, 4.5), (3.8, 1.8)]
# the arms, cut off the design: per row the columns of each (read off the design's material map: the near upper arm
# and forearm left of the torso, the far ones right of it)
NEAR_ARM = {70: (55, 56), 71: (55, 57), 72: (54, 58), 73: (54, 57), 74: (54, 57), 75: (53, 57), 76: (55, 57),
            77: (55, 57), 78: (52, 57)}
FAR_ARM = {74: (67, 70), 75: (67, 69), 76: (67, 70), 77: (68, 70), 78: (69, 70)}
NEAR_FIST = (50, 78, 57, 86)     # x0, y0, x1, y1 on the canvas: the design's near fist (gold knuckles, plum glove)
FAR_FIST = (70, 81, 76, 87)
NEAR_SHOULDER = (56.0, 71.5)
FAR_SHOULDER = (68.5, 74.5)
UPPER, FORE = 5.0, 3.5           # shoulder -> elbow, elbow -> wrist (the design's arm: 8 squares shoulder -> wrist)
# the near arm over the cycle (frame 0 = the near foot's contact): (upper arm, degrees from straight down, + ahead;
# the elbow's bend); the far arm half a cycle on
ARM = [(-30, 50), (-22, 55), (-5, 70), (18, 95), (30, 105), (22, 95), (5, 75), (-18, 55)]
SKIN = ("F9BC89", "DC9263", "B06B44")
BANDAGE = ("DCDFE8", "C4C9DB", "9FA8C3")
RING = "F7C414"
COAT = ("451A2A", "340F1E", "1F0917")       # lit, mid, dark
HEM = ("F7C414", "DF9704")
NOT_FIST = {"9FA8C3", "B2B9D2", "C4C9DB", "DCDFE8", "290B42", "3C1268", "531E8E"}


def rgba(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255), np.uint8)


def upper_block(d):
    """{(x, y): colour}: the design above the trousers without its arms."""
    cells = {}
    for y in range(0, BELT + 1):
        for x in range(d.shape[1]):
            if not d[y, x, 3]:
                continue
            for arm in (NEAR_ARM, FAR_ARM):
                if y in arm and arm[y][0] <= x <= arm[y][1]:
                    break
            else:
                cells[(x, y)] = d[y, x].copy()
    return cells


def fist(d, box):
    """The design's fist in box as {(dx, dy) from its top middle: colour} (its own outline, not the bandage's)."""
    x0, y0, x1, y1 = box
    out = {}
    for y in range(y0, y1):
        for x in range(x0, x1):
            if d[y, x, 3] and R.hexs(d[y, x]) not in NOT_FIST:
                out[(x - (x0 + x1) // 2, y - y0)] = d[y, x].copy()
    return out


def pt(a, deg, n):
    t = math.radians(deg)
    return (a[0] + math.sin(t) * n, a[1] + math.cos(t) * n)


def arm(shoulder, up, bend, hand):
    """{(x, y): colour} of an arm: the upper arm (skin, lit ahead), the forearm (bandage), a gold ring, the fist."""
    E = pt(shoulder, up, UPPER)
    W = pt(E, up + bend, FORE)
    cells = {}
    xs, ys = [shoulder[0], E[0], W[0]], [shoulder[1], E[1], W[1]]
    for y in range(int(min(ys)) - 3, int(max(ys)) + 4):
        for x in range(int(min(xs)) - 3, int(max(xs)) + 4):
            p = (x + 0.5, y + 0.5)
            d1, _, s1 = R.seg(p, shoulder, E)
            d2, t2, s2 = R.seg(p, E, W)
            if d2 <= 1.3:
                h = RING if t2 > FORE - 1.0 else (BANDAGE[0] if s2 > 0.5 else BANDAGE[2] if s2 < -0.5 else BANDAGE[1])
            elif d1 <= 1.7:
                h = SKIN[0] if s1 > 0.6 else SKIN[2] if s1 < -0.8 else SKIN[1]
            else:
                continue
            cells[(x, y)] = rgba(h)
    wx, wy = int(round(W[0] - 0.5)), int(round(W[1]))
    for (dx, dy), c in hand.items():
        cells[(wx + dx, wy + dy)] = c
    return ring(cells)


def ring(cells):
    out = {}
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in cells:
                out[(x + dx, y + dy)] = rgba("050302")
    out.update(cells)
    return out


def coat(k, dy):
    """The coat's tails streaming back from the waist behind the legs: a short band from under the belt, its open front
    and its hem trimmed in gold like the design's, the lit plum along its top, fluttering a square."""
    flutter = [0, 1, 1, 0, 0, 1, 1, 0][k]
    A = (56.0, BELT + 1.0 + dy)              # the waist's back
    B = (61.0, BELT + 2.0 + dy)              # the waist's middle, under the belt
    C = (55.0, 89.0 + dy + flutter)          # the hem's front end
    D = (47.5, 86.5 + dy - flutter)          # the tip, furthest back
    poly = [A, B, C, D]
    cells = {}
    for y in range(int(BELT + dy), 93 + dy):
        for x in range(42, 64):
            p = (x + 0.5, y + 0.5)
            if not inside(p, poly):
                continue
            to_hem, to_front, to_top = R.seg(p, C, D)[0], R.seg(p, B, C)[0], R.seg(p, A, D)[0]
            if to_hem < 0.8 or to_front < 0.7:
                h = HEM[0] if min(to_hem, to_front) < 0.4 else HEM[1]
            elif to_top < 0.9:
                h = COAT[0]
            elif to_hem < 1.8:
                h = COAT[2]
            else:
                h = COAT[1]
            cells[(x, y)] = rgba(h)
    return ring(cells)


def inside(p, poly):
    n, c = len(poly), False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < (x2 - x1) * (p[1] - y1) / (y2 - y1) + x1:
            c = not c
    return c


def lean(y):
    return int(math.floor((BELT - y) * LEAN + 0.5)) if y <= BELT else 0


def put(can, cells, under=False):
    for (x, y), c in cells.items():
        if 0 <= y < can.shape[0] and 0 <= x < can.shape[1] and not (under and can[y, x, 3]):
            can[y, x] = c


def frame(k, d=None):
    """Run frame k (0-7) on the 128 x 128 design canvas (the pivot (64, 88), the soles on row 99)."""
    d = K.design_1x() if d is None else d
    dy = BOB[k]
    near_fist, far_fist = fist(d, NEAR_FIST), fist(d, FAR_FIST)
    foot = R.shoe()
    can = np.zeros((128, 128, 4), np.uint8)
    up_f, bend_f = ARM[(k + 4) % 8]
    sh = (FAR_SHOULDER[0] + lean(int(FAR_SHOULDER[1])), FAR_SHOULDER[1] + dy)
    far_arm = arm(sh, up_f, bend_f, far_fist)
    legs = {}
    for side, ph in (("near", k % 8), ("far", (k + 4) % 8)):
        fx, lift = FOOT[ph]
        hip = (HIPS[side], HIP_ROW + dy)
        knee, ankle = R.ik(hip, (hip[0] + fx, ANKLE_ROW - lift))
        legs[side] = R.leg(hip, knee, ankle, R.RUN_SHADES[side], foot)
    body = {(x + lean(y), y + dy): c for (x, y), c in upper_block(d).items()}
    up_n, bend_n = ARM[k]
    sh = (NEAR_SHOULDER[0] + lean(int(NEAR_SHOULDER[1])), NEAR_SHOULDER[1] + dy)
    near_arm = arm(sh, up_n, bend_n, near_fist)
    put(can, body)
    put(can, near_arm)
    put(can, legs["near"], under=True)
    put(can, coat(k, dy), under=True)
    put(can, legs["far"], under=True)
    put(can, far_arm, under=True)
    can = R.pieces(can)
    can, _, _ = G.complete_outline(can, feet=99)
    return can


def review(path, z=6):
    d = K.design_1x()
    frames = [d] + [frame(k, d) for k in range(8)]
    x0, x1, y0, y1 = 36, 86, 54, 101
    W, H = (x1 - x0) * z, (y1 - y0) * z
    img = Image.new("RGB", ((W + 8) * 5, (H + 20) * 2), (40, 40, 40))
    dr = ImageDraw.Draw(img)
    for i, f in enumerate(frames):
        c = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 104, 88, 255))
        c.alpha_composite(Image.fromarray(np.ascontiguousarray(f[y0:y1, x0:x1])))
        X, Y = (i % 5) * (W + 8), (i // 5) * (H + 20)
        img.paste(c.resize((W, H), Image.NEAREST), (X, Y + 16))
        dr.text((X + 4, Y + 2), "idle" if i == 0 else f"run {i}", fill=(255, 255, 255))
    img.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", required=True)
    review(ap.parse_args().review)


if __name__ == "__main__":
    main()

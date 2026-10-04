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
  - the arms swing against the legs, close to the body as League's run holds them: the design's own two arms, square
    for square, the forearm (the gold gauntlet and the fist) moved a square or two ahead and back, upright, the upper
    arm's rows following it; the far arm behind the body, the near one over it, outlined where it crosses the coat and
    the legs as the design outlines its fist. Two versions before it failed: the arms drawn as lines in the skin's and
    the bandage's shades with the fist pasted at the wrist (half as thick as the design's, the gauntlets gone:
    「瑟提走路时手臂变形」), then the design's arms turned at the shoulder and the elbow by RotSprite (the far arm
    reached out level like a stick, the turned gauntlets read crooked: 「还是不对啊」「歪的？？」);
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
# the arms: the design's own, square for square (lines in the arm's colours read as deformed, as Ryze's did:
# tools/art/fix_ryze_strips_v2.py RUN_POSE). Each arm in two parts read off the design's material map, per row the
# columns: the upper arm (the skin with the bandage at the elbow) and the forearm (the gold gauntlet and the fist)
NEAR_UPPER = {70: (55, 56), 71: (55, 57), 72: (54, 58), 73: (54, 57), 74: (54, 57), 75: (53, 57), 76: (55, 57),
              77: (55, 57)}
NEAR_LOWER = {78: (52, 57), 79: (52, 54), 80: (52, 54), 81: (52, 54), 82: (52, 55), 83: (51, 55), 84: (51, 56),
              85: (55, 56)}
FAR_UPPER = {74: (68, 70), 75: (68, 69), 76: (68, 70), 77: (68, 70)}
FAR_LOWER = {78: (69, 70), 79: (70, 74), 80: (69, 72), 81: (70, 73), 82: (70, 73), 83: (70, 74), 84: (69, 74),
             85: (69, 74), 86: (69, 72)}
# the arms swing without turning (a turned gauntlet reads crooked: 「歪的？？」): over the cycle (frame 0 = the near
# foot's contact, the near arm back) the forearm with the gauntlet and the fist moves dx squares ahead and lift rows up
# (the elbow bending as it comes forward), upright as in the design; the upper arm's rows follow it a little more each
# row down from the shoulder, so the arm stays joined. The far arm the other way, a little less (behind the body)
NEAR_SWING = [(-1, 0), (-1, 0), (0, 0), (1, 0), (2, 1), (1, 0), (0, 0), (-1, 0)]
FAR_SWING = [(2, 1), (1, 0), (0, 0), (-1, 0), (-1, 0), (-1, 0), (0, 0), (1, 0)]
ARMS = (NEAR_UPPER, NEAR_LOWER, FAR_UPPER, FAR_LOWER)
OUTLINE = "050302"
COAT = ("451A2A", "340F1E", "1F0917")       # lit, mid, dark
HEM = ("F7C414", "DF9704")


def rgba(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255), np.uint8)


def in_rows(rows, x, y):
    return y in rows and rows[y][0] <= x <= rows[y][1]


def upper_block(d):
    """{(x, y): colour}: the design above the trousers without its arms. Where the near arm hid the body (the squares
    it leaves as it turns) the body's colour next to it in the row: the mane behind it, the coat's dark edge in front;
    none where that is the outline (the silhouette moves with the arm). The far arm's squares stay empty: it is drawn
    behind everything, so a fill there would hide it."""
    body = {}
    for y in range(0, BELT + 1):
        for x in range(d.shape[1]):
            if d[y, x, 3] and not any(in_rows(a, x, y) for a in ARMS):
                body[(x, y)] = d[y, x].copy()
    fill = {}
    for rows in (NEAR_UPPER, NEAR_LOWER):
        for y, (a, b) in rows.items():
            if y > BELT:
                continue
            for x in range(a, b + 1):
                for n in range(1, 4):
                    near = [c for c in (body.get((x - n, y)), body.get((x + n, y))) if c is not None]
                    if near:
                        if R.hexs(near[-1]) != OUTLINE:
                            fill[(x, y)] = near[-1].copy()
                        break
    body.update(fill)
    return body


def arm(d, upper, lower, dx, lift, shift):
    """The design's arm as {(x, y): (colour, forearm?)}: the forearm moved dx ahead and lift up, the upper arm's rows
    moved from 0 at the shoulder to most of dx at the elbow; both moved by shift (the lean and the bob)."""
    cells = {}
    y0, y1 = min(upper), max(upper)
    for y, (a, b) in upper.items():
        o = int(math.floor(dx * (y - y0 + 1) / (y1 - y0 + 2) + 0.5)) if dx > 0 else \
            -int(math.floor(-dx * (y - y0 + 1) / (y1 - y0 + 2) + 0.5))
        for x in range(a, b + 1):
            cells[(x + o + shift[0], y + shift[1])] = (d[y, x].copy(), False)
    for y, (a, b) in lower.items():
        for x in range(a, b + 1):
            if d[y, x, 3]:
                cells[(x + dx + shift[0], y - lift + shift[1])] = (d[y, x].copy(), True)
    return cells


def contour(cells, can, top):
    """The edge round the near arm where it lies over the body, the coat or the legs, as the design parts it: the
    gauntlet and the fist in the outline's black (the design's fist is outlined in black against the coat below it),
    the upper arm in the darkest plum (as the design parts it from the chest; black inside the figure was cleaned out:
    「去掉身体上没用的黑色素」). Without it the gauntlet's gold and plum melt into the coat's. None over the shoulder
    the arm hangs from (rows above top)."""
    out = {}
    for (x, y), (_, fore) in cells.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells and q[1] >= top and can[q[1], q[0], 3]:
                if fore or q not in out:
                    out[q] = rgba(OUTLINE if fore else COAT[2])
    return out


def ring(cells):
    out = {}
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in cells:
                out[(x + dx, y + dy)] = rgba(OUTLINE)
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
    foot = R.shoe()
    can = np.zeros((128, 128, 4), np.uint8)
    legs = {}
    for side, ph in (("near", k % 8), ("far", (k + 4) % 8)):
        fx, lift = FOOT[ph]
        hip = (HIPS[side], HIP_ROW + dy)
        knee, ankle = R.ik(hip, (hip[0] + fx, ANKLE_ROW - lift))
        legs[side] = R.leg(hip, knee, ankle, R.RUN_SHADES[side], foot)
    body = {(x + lean(y), y + dy): c for (x, y), c in upper_block(d).items()}
    near_arm = arm(d, NEAR_UPPER, NEAR_LOWER, *NEAR_SWING[k], (lean(min(NEAR_UPPER)), dy))
    far_arm = arm(d, FAR_UPPER, FAR_LOWER, *FAR_SWING[k], (lean(min(FAR_UPPER)), dy))
    put(can, body)
    put(can, legs["near"], under=True)
    put(can, coat(k, dy), under=True)
    put(can, legs["far"], under=True)
    put(can, {q: c for q, (c, _) in far_arm.items()}, under=True)
    put(can, contour(near_arm, can, min(NEAR_UPPER) + dy + 4))
    put(can, {q: c for q, (c, _) in near_arm.items()})
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

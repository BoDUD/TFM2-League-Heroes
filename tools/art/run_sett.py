#!/usr/bin/env python3
"""Sett's run on the design's own body (tools/art/strips_sett.py puts it in the run strip).

    python tools/art/run_sett.py --review <png>      # the eight frames next to the idle, 6x

The user, on the run made from Codex's drafts: 「跑步姿势有点怪吧？而且好像还有点变形」 - every frame's upper body was
Codex's own drawing (the torso, the mantle, the coat and the arms a different shape and narrower than the idle's in
each), the drawn legs stood in a stiff A in three frames, and the hips and the head rose and fell at random. As
Sivir's run (tools/art/rig_sivir_run.py, the version the user approved: 「新版很不错」):
  - the upper body is the design itself above the belt (its head, torso, upper arms, mantle, clasps, coat fronts and
    belt), the near gauntlet's top row taken off, one rigid block in every frame; it leans forward (each row shifted LEAN of a square per row over
    the belt) and sinks with the stride (BOB: low after each contact, high on the push);
  - the legs: each foot placed along the run cycle (ahead on the contact, drawn back under the body, off the toe,
    kicked up behind, swung through, reaching), the knee solved forward, both the design's length and width in the
    trousers' shades with the gold stripe and the design's shoe (strips_sett.leg), the hips where the design's are;
  - the arms are the design's own, square for square: the upper arms stay in the body as the design has them, the
    gauntlets with the fists swing a square ahead and back against the legs, upright, close to the body as League's
    run holds them; the far fist beside the hip over the far leg (as the idle shows it), the near one over the body,
    each outlined in black where it crosses the coat or a leg, as the design outlines its fist. The design's outline
    round its gaps (between the near arm and the coat) takes the darkest colour beside it once the coat fills the gap.
    Earlier versions failed: the arms drawn as lines in the skin's and the bandage's shades (half as thick as the
    design's, the gauntlets gone: 「瑟提走路时手臂变形」); the design's arms turned at the shoulder and the elbow
    (RotSprite: the far arm reached out level like a stick, the turned gauntlets read crooked: 「还是不对啊」
    「歪的？？」); the upper arms' rows moved with the gauntlets (holes in the body closed as black lines and notches,
    the far arm thinned: 「肚子上有一条黑线 还有右手臂比左手臂细？」「手臂那里还有一块凹进去的」);
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
# tools/art/fix_ryze_strips_v2.py RUN_POSE). The upper arms (skin, the bandage at the elbow) stay in the body as the
# design has them; only the forearms swing - the gold gauntlet and the fist, read off the design's material map (per
# row the columns), upright (turned gauntlets read crooked: 「歪的？？」). The far forearm's bandage rows (79, 80) stay
# with its elbow, so only its gauntlet moves. Moving the upper arms too left holes in the body that closed as black
# lines and notches (「肚子上有一条黑线 还有右手臂比左手臂细？」「手臂那里还有一块凹进去的」)
NEAR_FORE = {78: (52, 54), 79: (52, 54), 80: (52, 54), 81: (52, 54), 82: (52, 55), 83: (51, 55), 84: (51, 56),
             85: (55, 56)}
FAR_FORE = {79: (69, 71), 80: (69, 71), 81: (70, 73), 82: (70, 73), 83: (70, 74), 84: (69, 74), 85: (69, 74),
            86: (69, 72)}
FAR_WRIST = 81                   # the far forearm's first gauntlet row: the rows above it stay with the elbow
# the end of the mane's strand that hangs over the far arm's elbow, below the belt row: it stays with the body
STRAND = ((72, 79), (72, 80))
# over the cycle (frame 0 = the near foot's contact): the squares each gauntlet sits ahead of the design's place - the
# near one back while its foot is ahead, the far one the other way
NEAR_SWING = [-1, -1, 0, 1, 1, 1, 0, -1]
FAR_SWING = [1, 1, 0, -1, -1, -1, 0, 1]
ARMS = (NEAR_FORE, FAR_FORE)
OUTLINE = "050302"
COAT = ("451A2A", "340F1E", "1F0917")       # lit, mid, dark
HEM = ("F7C414", "DF9704")


def rgba(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255), np.uint8)


def in_rows(rows, x, y):
    return y in rows and rows[y][0] <= x <= rows[y][1]


def upper_block(d):
    """{(x, y): colour}: the design above the trousers without its forearms (only the near gauntlet's top row is that
    high). Where it leaves the body as it swings, the body's colour next to it in the row: the mane behind it, the
    bandage at the elbow; none where that is the outline."""
    body = {}
    for y in range(0, BELT + 1):
        for x in range(d.shape[1]):
            if d[y, x, 3] and not any(in_rows(a, x, y) for a in ARMS):
                body[(x, y)] = d[y, x].copy()
    for (x, y) in STRAND:
        body[(x, y)] = d[y, x].copy()
    fill = {}
    for rows in (NEAR_FORE,):
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


def fore(d, rows, dx, shift, wrist=0):
    """The design's forearm as {(x, y): colour}, its rows from wrist down moved dx ahead (the rows above stay with the
    elbow), all moved by shift (the lean and the bob)."""
    cells = {}
    for y, (a, b) in rows.items():
        for x in range(a, b + 1):
            if d[y, x, 3]:
                cells[(x + (dx if y >= wrist else 0) + shift[0], y + shift[1])] = d[y, x].copy()
    return cells


def contour(cells, can, top):
    """The outline round a gauntlet where it lies over the coat or the legs (rows from top down), black as the design
    outlines its fist against the coat; without it the gauntlet's gold and plum melt into the coat's."""
    out = {}
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells and q[1] >= top and can[q[1], q[0], 3]:
                out[q] = rgba(OUTLINE)
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
    near = fore(d, NEAR_FORE, NEAR_SWING[k], (lean(min(NEAR_FORE)), dy))
    far = fore(d, FAR_FORE, FAR_SWING[k], (0, dy), FAR_WRIST)
    put(can, body)
    put(can, legs["near"], under=True)
    put(can, coat(k, dy), under=True)
    put(can, far, under=True)            # the far fist beside the hip over the far leg, as the idle shows it
    put(can, legs["far"], under=True)
    put(can, {q: c for q, c in contour(far, can, FAR_WRIST + dy).items() if q in legs["far"]})
    put(can, contour(near, can, min(NEAR_FORE) + 1 + dy))
    put(can, near)
    can = R.pieces(can)
    can, _, _ = G.complete_outline(can, feet=99)
    return unblack(can, [q for q, c in body.items() if R.hexs(c) == OUTLINE])


def unblack(can, cells):
    """The design's outline squares round its gaps (between the near arm and the coat, under the arms) lie inside the
    figure once the coat and the legs fill the gaps: each takes the darkest colour beside it, as the design's own
    inner lines did (design_sett.clean; 「去掉身体上没用的黑色素」). The outline round the silhouette, the legs' and the
    near gauntlet's stay black."""
    out = can.copy()
    n4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
    lum = lambda c: 0.3 * int(c[0]) + 0.59 * int(c[1]) + 0.11 * int(c[2])
    for x, y in cells:
        if not all(can[y + dy, x + dx, 3] for dx, dy in n4):
            continue
        near = [can[y + dy, x + dx] for dx, dy in n4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
                if can[y + dy, x + dx, 3] and R.hexs(can[y + dy, x + dx]) != OUTLINE]
        if near:
            out[y, x] = min(near, key=lum)
    return out


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

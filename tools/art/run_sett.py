#!/usr/bin/env python3
"""Sett's run on the design's own body (tools/art/strips_sett.py puts it in the run strip).

    python tools/art/run_sett.py --review <png>      # the eight frames next to the idle, 6x

The user, on the run made from Codex's drafts: 「跑步姿势有点怪吧？而且好像还有点变形」 - every frame's upper body was
Codex's own drawing (the torso, the mantle, the coat and the arms a different shape and narrower than the idle's in
each), the drawn legs stood in a stiff A in three frames, and the hips and the head rose and fell at random. As
Sivir's run (tools/art/rig_sivir_run.py, the version the user approved: 「新版很不错」):
  - the upper body is the design itself above the belt (its head, torso, upper arms, mantle, clasps, coat fronts and
    belt), the near gauntlet's top row taken off, one rigid block in every frame; it leans forward (each row shifted
    LEAN of a square per row over the belt) and sinks with the stride (BOB: low after each contact, high on the push);
  - the legs: each foot placed along the run cycle (ahead on the contact, drawn back under the body, off the toe,
    kicked up behind, swung through, reaching), the knee solved forward, both the design's length and width in the
    trousers' shades with the gold stripe and the design's shoe (strips_sett.leg), the hips where the design's are;
  - the arms swing as League's run swings them (Sett_Run: the near arm back while the near foot leads, ahead while the
    far foot does; the far arm the other way; the elbows always bent) and as Ryze's approved run poses its arms
    (tools/art/ryze_arms.py): each arm is the design's own squares in two bones - the upper arm (skin, the bandage at
    the elbow) and the forearm (the gold gauntlet and the fist) - each bone sheared row by row toward its angle within
    45 degrees of hanging, quarter-turned with its lit side up past that, foreshortened by dropping rows where it
    points at the camera, the elbow's corner closed; nothing is resampled or turned by a fraction of a quarter. What an
    arm uncovers is painted with what lies behind it (the coat's side, the mane at its back edge, the far flank's
    shade); the near arm is drawn over the body. The far arm, behind the body, keeps the design's upper arm and the
    bandage's top row; only its gauntlet with the fist moves, upright (FAR_HAND_AT): ahead and up in front of the hip,
    back behind the far thigh. Each arm is outlined in black where it crosses a leg, the coat or the background;
    above the belt no black stays inside the figure (design_sett.clean, as
    the design: 「去掉身体上没用的黑色素」). Earlier versions failed: the arms drawn as lines in the skin's and the
    bandage's shades (「瑟提走路时手臂变形」); the arms turned at the shoulder and the elbow by RotSprite (the far arm
    reached out like a stick, the gauntlets crooked: 「还是不对啊」「歪的？？」); the upper arms' rows moved with the
    gauntlets and their holes left unpainted (black lines and notches: 「肚子上有一条黑线 还有右手臂比左手臂细？」
    「手臂那里还有一块凹进去的」); the arms hanging straight (「走路时手和手臂错误」); the gauntlets laid level at the
    waist, melting into the belt and snapping between two poses (「手还是不对」「一坨屎」);
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
# the design's arms, per row the columns (read off its material map): the upper arm (skin; the bandage at the elbow)
# and the forearm (the gold gauntlet, the plum glove, the skin knuckles; the far one's bandage on top)
NEAR_UP = {70: (55, 56), 71: (55, 57), 72: (54, 58), 73: (54, 57), 74: (54, 57), 75: (53, 57), 76: (55, 57),
           77: (55, 57)}
NEAR_FO = {78: (52, 57), 79: (52, 54), 80: (52, 54), 81: (52, 54), 82: (52, 55), 83: (51, 55), 84: (51, 56),
           85: (55, 55)}
FAR_UP = {74: (68, 70), 75: (68, 69), 76: (68, 70), 77: (68, 70)}
FAR_FO = {78: (69, 70), 79: (69, 71), 80: (69, 71), 81: (70, 73), 82: (70, 73), 83: (70, 74), 84: (69, 74),
          85: (69, 74), 86: (72, 72)}               # (the squares under the fists are the coat's, behind them)
# the far arm is behind the body: its upper arm and the bandage's top row stay as the design has them (posed, its
# squares left the flank in pieces: 「还有这里严重穿模 变形」), only its gauntlet with the fist (rows 81-86) moves,
# upright as the design's (laid level it read as a lump: 「不是变形吗？？」), the bandage's lower rows (79-80) bending
# to it: (squares ahead, rows up) per pose - ahead and up in front of the hip, back behind the far thigh
FAR_HAND = 81
FAR_HAND_AT = {"F": (3, -2), "Pf": (2, -1), "Pb": (0, 0), "B": (-1, 0)}
AXIS = {"near": (56, 55), "far": (69, 70)}      # the upper arm's and the forearm's axis columns
SHOULDER = {"near": (56, 70), "far": (69, 74)}  # the upper arm's top row on its axis
# the end of the mane's strand that hangs over the far arm's elbow, below the belt row: it stays with the body
STRAND = ((72, 79), (72, 80))
# the poses: (upper arm, forearm degrees from hanging, + ahead; forearm rows dropped as it points at the camera;
# upper arm rows dropped as it swings back, away from the camera - at -45 unshortened it reached out far too long:
# 「左手伸出去太长了吧」) - B the back of the swing, Pb passing behind, Pf passing ahead, F the front of the swing
POSES = {
    "near": {"B": (-30, -10, (), (3, 5)), "Pb": (-15, 15, ()), "Pf": (0, 40, (1,)), "F": (12, 40, (1, 2))},
}
# over the cycle (frame 0 = the near foot's contact), League's timing: the arms at their ends a frame before and on
# each contact, passing quickly between
NEAR_SCHED = ["B", "Pb", "Pf", "F", "F", "Pf", "Pb", "B"]
FAR_SCHED = ["F", "Pf", "Pb", "B", "B", "Pb", "Pf", "F"]
OUTLINE = "050302"
COAT = ("451A2A", "340F1E", "1F0917")       # lit, mid, dark
HEM = ("F7C414", "DF9704")
SKIN_SHADE = "B06B44"
MANE = {"531E8E", "3C1268", "290B42"}


def rgba(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255), np.uint8)


def cells_of(d, rows, outline=False):
    """{(x, y): colour} of the design's squares in rows (its outline squares too only if outline)."""
    out = {}
    for y, (a, b) in rows.items():
        for x in range(a, b + 1):
            if d[y, x, 3] and (outline or R.hexs(d[y, x]) != OUTLINE):
                out[(x, y)] = d[y, x].copy()
    return out


def body_block(d):
    """{(x, y): colour}: the design above the trousers without its arms, what the near arm hid painted with what lies
    behind it - the mane at the back of the shoulder (where the mane is beside it), else the coat's side, lit at the
    top as its lapel. The design's gaps between the near arm and the coat front (background there: the legs drawn
    under showed through) take the coat. The far arm's upper arm and the bandage's top row stay."""
    arm = set()
    for rows in (NEAR_UP, NEAR_FO):
        arm |= set(cells_of(d, rows, outline=True))
    arm |= {q for q in cells_of(d, FAR_FO, outline=True) if q[1] > BELT}
    out = {}
    for y in range(0, BELT + 1):
        for x in range(d.shape[1]):
            if d[y, x, 3] and (x, y) not in arm:
                out[(x, y)] = d[y, x].copy()
    mane = lambda x, y: (x, y) not in arm and d[y, x, 3] and R.hexs(d[y, x]) in MANE
    for (x, y) in sorted(arm, key=lambda q: (q[1], q[0])):
        if y > BELT or x >= SHOULDER["far"][0] - 6:
            continue
        if x <= AXIS["near"][1] and y < BELT and any(mane(x + a, y + b) for a, b in
                                                       ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1))):
            out[(x, y)] = rgba(sorted(MANE)[0])                 # 290B42, the mane's darkest
        else:
            out[(x, y)] = rgba(COAT[0] if y <= 75 else COAT[1])
    for y in range(SHOULDER["near"][1], BELT + 1):
        for x in range(AXIS["near"][0], SHOULDER["far"][0] - 6):
            if (x, y) not in out and (x - 1, y) in out and (x + 1, y) in out and (x, y - 1) in out:
                out[(x, y)] = rgba(COAT[1])
    for (x, y) in STRAND:
        out[(x, y)] = d[y, x].copy()
    return out


def posed(d, side, up, fore, drop_fore, shoulder, drop_up=()):
    """{(x, y): colour} of the design's arm, its upper arm `up` and its forearm `fore` degrees from hanging (+ ahead),
    the shoulder on `shoulder`: Ryze's posing of the idle's own squares (tools/art/ryze_arms.py)."""
    import ryze_arms as RA
    keep, RA.OUTLINE = RA.OUTLINE, {tuple(rgba(OUTLINE)[:3])}
    try:
        up_rows, fo_rows = (NEAR_UP, NEAR_FO) if side == "near" else (FAR_UP, FAR_FO)
        ub = RA.strip(cells_of(d, up_rows), AXIS[side][0])
        fb = RA.strip(cells_of(d, fo_rows), AXIS[side][1])
        cu, end = RA.place(ub, up, side, drop_up)
        out = {(shoulder[0] + x, shoulder[1] + y): c for (x, y), c in cu.items()}
        st = RA.step_of(fore)
        ex = shoulder[0] + end[0] + st[0] + AXIS[side][1] - AXIS[side][0]
        ey = shoulder[1] + end[1] + st[1]
        cf, _ = RA.place(fb, fore, side, drop_fore)
        for (x, y), c in cf.items():
            out[(ex + x, ey + y)] = c
        return RA.close_gaps(out, RA.OUTLINE)
    finally:
        RA.OUTLINE = keep


def far_hand(d, pose, shift):
    """{(x, y): colour} of the far forearm below the belt: the gauntlet with the fist (rows from FAR_HAND) moved as
    FAR_HAND_AT says, upright as the design's; the bandage rows above it shifted a part of that, row by row, so it
    stays joined to the elbow (a gauntlet lifted over them hides them: the forearm points at the camera)."""
    dx, dy = FAR_HAND_AT[pose]
    rows = sorted(y for y in FAR_FO if y > BELT)
    wrap = [y for y in rows if y < FAR_HAND]
    out = {}
    for y in rows:
        if y < FAR_HAND:
            ox, oy = int(math.floor(dx * (wrap.index(y) + 1) / (len(wrap) + 1) + 0.5)), 0
        else:
            ox, oy = dx, dy
        a, b = FAR_FO[y]
        for x in range(a, b + 1):
            if d[y, x, 3] and R.hexs(d[y, x]) != OUTLINE:
                out[(x + ox + shift[0], y + oy + shift[1])] = d[y, x].copy()
    for y in rows:                              # the hand drawn over the wrap where it was lifted onto it
        if y >= FAR_HAND:
            a, b = FAR_FO[y]
            for x in range(a, b + 1):
                if d[y, x, 3] and R.hexs(d[y, x]) != OUTLINE:
                    out[(x + dx + shift[0], y + dy + shift[1])] = d[y, x].copy()
    return out


def edge(cells):
    """The squares round cells (4-neighbours outside them)."""
    out = set()
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in cells:
                out.add((x + dx, y + dy))
    return out


def fill_dents(can):
    """A transparent square with the figure left, right and above it (a notch between an arm and the coat or a leg)
    takes the outline's black."""
    out = can.copy()
    for _ in range(4):
        op = out[..., 3] > 0
        hit = op[1:-1, :-2] & op[1:-1, 2:] & op[:-2, 1:-1] & ~op[1:-1, 1:-1]
        if not hit.any():
            break
        ys, xs = np.nonzero(hit)
        out[ys + 1, xs + 1] = rgba(OUTLINE)
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
    A0 = (51.0, BELT + 1.0 + dy)             # under the mane's back: the back panel hangs behind the near forearm
    A = (56.0, BELT + 1.0 + dy)              # the waist's back
    B = (61.0, BELT + 2.0 + dy)              # the waist's middle, under the belt
    C = (55.0, 89.0 + dy + flutter)          # the hem's front end
    D = (47.5, 86.5 + dy - flutter)          # the tip, furthest back
    poly = [A0, A, B, C, D]
    cells = {}
    for y in range(int(BELT + dy), 93 + dy):
        for x in range(42, 64):
            p = (x + 0.5, y + 0.5)
            if not inside(p, poly):
                continue
            to_hem, to_front, to_top = R.seg(p, C, D)[0], R.seg(p, B, C)[0], R.seg(p, A0, D)[0]
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
    import design_sett as D
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
    body = {(x + lean(y), y + dy): c for (x, y), c in body_block(d).items()}
    arms = {}
    up, fore, drop, *rest = POSES["near"][NEAR_SCHED[k]]
    sx, sy = SHOULDER["near"]
    arms["near"] = posed(d, "near", up, fore, drop, (sx + lean(sy), sy + dy), *rest)
    arms["far"] = far_hand(d, FAR_SCHED[k], (0, dy))
    ahead = FAR_SCHED[k] in ("F", "Pf")
    put(can, body)
    put(can, legs["near"], under=True)
    put(can, coat(k, dy), under=True)
    if ahead:                                    # in front of the hip: over the far leg, outlined against it
        put(can, arms["far"], under=True)
        put(can, legs["far"], under=True)
        put(can, {q: rgba(OUTLINE) for q in edge(arms["far"]) if q in legs["far"] or not can[q[1], q[0], 3]})
    else:                                        # swung back: behind the far thigh
        put(can, legs["far"], under=True)
        put(can, arms["far"], under=True)
        put(can, {q: rgba(OUTLINE) for q in edge(arms["far"]) if not can[q[1], q[0], 3]})
    can = R.pieces(can)
    can, _, _ = G.complete_outline(can, feet=99)
    can = fill_dents(can)
    clean = D.clean(can)                        # above the belt no black inside the figure, as the design
    can[:BELT + dy + 1] = clean[:BELT + dy + 1]
    # the near arm last, over the cleaned body, with an edge: against the background, the legs and the coat's tails
    # (below the belt) black, as the design outlines its fist; above the belt the darkest of what it lies on, as the
    # design parts its arm from its lapel (the skin's shade on skin, the mane's darkest on the mane, else the coat's
    # darkest plum) - no black line beside the belly (「肚子上有一条黑线」); none where it hangs from the shoulder
    top = SHOULDER["near"][1] + dy + 3
    skin = {"F9BC89", "DC9263", SKIN_SHADE}
    ring = {}
    for (x, y) in edge(arms["near"]):
        if not can[y, x, 3]:
            ring[(x, y)] = rgba(OUTLINE)
        elif y >= top:
            h = R.hexs(can[y, x])
            ring[(x, y)] = rgba(OUTLINE if y > BELT + dy else SKIN_SHADE if h in skin else
                                min(MANE) if h in MANE else COAT[2])
    put(can, ring)
    put(can, arms["near"])
    can, _, _ = G.complete_outline(can, feet=99)
    return fill_dents(can)


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

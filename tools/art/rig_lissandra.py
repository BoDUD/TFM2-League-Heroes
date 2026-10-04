#!/usr/bin/env python3
"""Lissandra's action strips posed from the approved design's own parts (2026-10-05): the casting body = the idle's.

    python tools/art/rig_lissandra.py [--check] [--review DIR]

Codex's step-2 delivery (assets/source/lissandra/codex_strips/) was, by its own HANDOFF, not usable: the image tool drew
her 47-60 rows tall against the design's 42, with thin arms and a narrow braid. The user: 「如果有奇怪的地方请你修好」.
She has no legs (League's gown reaches the ground and she glides), so every frame here is the design
(tools/art/design_lissandra.py) with only what the action moves moved, the way league_twistedfate's and league_ryze's
arms were posed (tools/art/rig_twistedfate.py, ryze_arms.py):
- NEAR_ARM (image right) and FAR_ARM (image left, between the braid and the gown) are taken off the design and posed
  from their own squares: two bones each, UPPER (rows 74-79 under the shoulder crystal) and FORE (rows 80-85, the
  glowing forearm and the clawed hand); a bone within 45 degrees of straight down keeps its rows and shifts each by
  its slope, one pointing across is quarter-turned, one near 45 degrees gets a square wider (rig_twistedfate.place_bone);
  every square keeps the design's colour. The far arm lies behind the body, the near one in front of it.
- the angles per frame follow League's clips at the release frames of the kit (poses.json): attack and Q fling the
  near arm forward to the right on frame 4 (ticks 13 / 12), W throws both arms down and out, E swings the near arm
  forward-low on frame 2 and holds it, R raises both arms and sweeps them down-forward on frame 3, her own tomb holds
  them spread up, the hit leans the upper body back a column.
- the glide (League's run, 2 s a cycle, 8 frames): the arms trail back, swinging a few degrees against each other; the
  upper body (everything above the hem's crystals) bobs a row; the hem stays on the line.
- the death (League's: she raises her arms and freezes into an ice statue): the arms rise, then dark ice shards (the
  hem crystals' steel blues, outlined) grow up from the hem, frame by frame, to her chest; 7 and 8 the same.
Every built frame is finished alike (rig_twistedfate.finish): pinholes filled, the outline closed round the moved edges,
stray crumbs dropped.
Writes assets/source/native/lissandra_<tag>.png (8x, 128x96 cells) and lissandra_cells.json; then
tools/art/import_native.py --hero lissandra. --check compares instead of writing; --review writes review sheets.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rig_twistedfate as T  # noqa: E402

ROOT = T.ROOT
NATIVE = T.NATIVE
DESIGN = os.path.join(NATIVE, "lissandra_native.png")
Z = 8
PIVOT = (64, 88)
SOLES = 99
OUT = (0x0B, 0x0A, 0x14)
CELL = (128, 96)
CELL_PIVOT = (64, 70)            # the hem on cell row 81 (the references' feet line)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "ult_self", "hit", "dead"]
MS = {"idle": [200] * 6, "run": [250] * 8, "attack": [70, 70, 80, 80, 70, 63], "skill": [60, 70, 70, 80, 80, 73],
      "skill2": [60, 70, 80, 90, 100], "skill2_e": [60, 80, 90, 120, 160, 223], "ult": [80, 80, 90, 100, 150],
      "ult_self": [500] * 5, "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}

# the arms on the design canvas: (row0, row1, col0, col1) boxes, their shoulders (the upper bone's joint square) and
# where the forearm starts
NEAR_BOX, NEAR_SH = (74, 85, 70, 73), (70, 74)
FAR_BOX, FAR_SH = (74, 85, 60, 62), (61, 74)
ELBOW_ROW = 80
HEM_TOP = 92                     # the hem's crystals: the glide's bob moves everything above this row
# per frame: ((near upper, near fore), (far upper, far fore), lean columns, lift rows) - degrees from the hang,
# + toward the image right (180 = straight up); None = the design's own arm
POSES = {
    "attack": [None, ((-20, -35), None, -1, 0), ((55, 95), None, -1, 0), ((92, 96), None, 1, 0),
               ((84, 88), None, 1, 0), ((35, 45), None, 0, 0)],
    "skill": [((10, 20), (-10, -15), 0, 0), ((-30, -60), (-20, -30), -1, 0), ((-45, -90), (-30, -45), -1, 0),
              ((95, 95), (-40, -60), 1, 0), ((85, 90), (-30, -45), 1, 0), ((30, 40), (-10, -15), 0, 0)],
    "skill2": [((55, 65), (-55, -65), 0, 0), ((70, 80), (-70, -80), 0, 0), ((72, 82), (-72, -82), 0, 0),
               ((40, 50), (-40, -50), 0, 0), ((15, 20), (-15, -20), 0, 0)],
    "skill2_e": [((-20, -40), None, -1, 0), ((70, 80), (-15, -20), 1, 0), ((75, 85), (-15, -20), 1, 0),
                 ((75, 85), (-15, -20), 1, 0), ((70, 80), (-12, -15), 1, 0), ((60, 70), (-10, -12), 0, 0)],
    "ult": [((150, 160), (-125, -140), 0, 0), ((165, 172), (-130, -150), -1, 0), ((70, 60), (40, 30), 1, 0),
            ((50, 40), (20, 20), 1, 0), ((20, 20), (5, 5), 0, 0)],
    "ult_self": [((110, 122), (-110, -122), 0, 0), ((113, 125), (-108, -120), 0, 0), ((110, 122), (-110, -122), 0, 0),
                 ((107, 119), (-112, -124), 0, 0), ((110, 122), (-110, -122), 0, 0)],
    "hit": [((-15, -20), (-15, -20), -1, 0), None],
}
# the glide: (near, far) arm angles and the upper body's drop per frame
RUN_ARMS = [((-20, -28), (-16, -22)), ((-22, -30), (-14, -20)), ((-24, -32), (-12, -18)), ((-22, -30), (-14, -20)),
            ((-20, -28), (-16, -22)), ((-18, -26), (-18, -24)), ((-16, -24), (-20, -26)), ((-18, -26), (-18, -24))]
RUN_DROP = [0, 0, 1, 1, 0, 0, 1, 1]
# the death: arms per frame and the ice's height (rows above the hem's line it reaches)
DEAD_ARMS = [((-15, -20), (-15, -20)), ((140, 155), (-120, -135)), ((150, 160), (-125, -140)),
             ((150, 160), (-125, -140)), ((150, 160), (-125, -140)), ((150, 160), (-125, -140)),
             ((150, 160), (-125, -140)), ((150, 160), (-125, -140))]
DEAD_ICE = [0, 0, 6, 10, 15, 20, 24, 24]
ICE = [(0x2B, 0x3C, 0x8D), (0x3F, 0x62, 0xCE), (0x6A, 0x97, 0xF5), (0xD2, 0xF2, 0xFD)]   # dark, mid, lit, glint


def lp(p):
    return T.lp(p)


def design():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def bone_of(d, box, shoulder, rows):
    """{(along, across): rgba} of the design's squares of the arm box in `rows`, relative to the bone's joint."""
    r0, r1, c0, c1 = box
    j = rows[0]
    out = {}
    for r in rows:
        for c in range(c0, c1 + 1):
            if d[r, c, 3]:
                out[(r - j, c - shoulder[0])] = tuple(int(v) for v in d[r, c])
    return out


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        self.body = d.copy()
        self.arms = {}
        for side, box, sh in (("near", NEAR_BOX, NEAR_SH), ("far", FAR_BOX, FAR_SH)):
            r0, r1, c0, c1 = box
            self.body[r0:r1 + 1, c0:c1 + 1] = 0
            up = bone_of(d, box, sh, list(range(r0, ELBOW_ROW)))
            fo = bone_of(d, box, (sh[0], ELBOW_ROW), list(range(ELBOW_ROW, r1 + 1)))
            self.arms[side] = (up, fo, sh)


def arm(P, side, angles, dx=0, dy=0):
    """{(x, y): rgba} of one arm posed: the upper bone `angles[0]`, the forearm `angles[1]` degrees from the hang."""
    up, fo, sh = P.arms[side]
    cu, end = T.place_bone(up, angles[0])
    sx, sy = sh[0] + dx, sh[1] + dy
    out = {(sx + x, sy + y): k for (x, y), k in cu.items()}
    st = T.step_of(angles[1])
    ex, ey = sx + end[0] + st[0], sy + end[1] + st[1]
    cf, _ = T.place_bone(fo, angles[1])
    for (x, y), k in cf.items():
        out[(ex + x, ey + y)] = k
    # close one-square gaps at the elbow (the colour beside them)
    for _ in range(2):
        add = {}
        for (x, y), k in out.items():
            for ox, oy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                q, opp = (x + ox, y + oy), (x + 2 * ox, y + 2 * oy)
                if q not in out and q not in add and opp in out and k[:3] != OUT and out[opp][:3] != OUT:
                    add[q] = k
        out.update(add)
    return out


def paint(c, cells, under=False):
    for (x, y), k in cells.items():
        if 0 <= y < 128 and 0 <= x < 128 and (not under or not c[y, x, 3]):
            c[y, x] = k
    return c


def upper_shift(body, dx, dy):
    """Everything above the hem's crystals moved (dx, dy), laid over the hem (the hem stays on its line)."""
    if not dx and not dy:
        return body
    out = body.copy()
    top = np.zeros_like(body)
    top[:HEM_TOP] = body[:HEM_TOP]
    out[:HEM_TOP] = 0
    return T.put(out, top, dx, dy)


def posed(P, pose, base=None):
    if pose is None:
        return P.design.copy()
    near, far, lean, lift = pose
    body = P.body if base is None else base
    c = np.zeros((128, 128, 4), np.uint8)
    farp = far if far is not None else (0, 0)
    paint(c, arm(P, "far", farp, lean, 0))
    T.put(c, upper_shift(body, lean, 0), 0, 0)
    paint(c, arm(P, "near", near if near is not None else (0, 0), lean, 0))
    return T.shifted(c, 0, -lift) if lift else c


def glide(P, k):
    near, far = RUN_ARMS[k]
    dy = RUN_DROP[k]
    c = np.zeros((128, 128, 4), np.uint8)
    paint(c, arm(P, "far", far, 0, dy))
    T.put(c, upper_shift(P.body, 0, dy), 0, 0)
    paint(c, arm(P, "near", near, 0, dy))
    return c


def ice(c, height, seed):
    """Dark ice shards growing up from the hem to about `height` rows above the soles' line, in front of the gown: wide
    jagged cones (a column wider every three rows down, five at most), dark on the left, lit on the right, a glint at the tip,
    outlined against the gown and each other; the tallest in the middle, lower to the sides."""
    if not height:
        return c
    xs = np.nonzero(c[SOLES - 2:SOLES + 1, :, 3].any(0))[0]
    x0, x1 = xs.min() + 1, xs.max() - 1
    mid = (x0 + x1) / 2
    rng = np.random.default_rng(seed)
    peaks, x = [], x0 + 1
    while x <= x1 - 1:
        side = 1 - 0.45 * abs(x - mid) / max(1, (x1 - x0) / 2)
        peaks.append((x, max(3, int(round(height * side)) - int(rng.integers(0, 6)))))
        x += int(rng.integers(5, 7))
    peaks.sort(key=lambda p: p[1])          # the tallest drawn last, in front
    for px, h in peaks:
        top = SOLES - h
        for y in range(top, SOLES + 1):
            half = min(2, (y - top + 2) // 3)
            for xx in range(px - half, px + half + 1):
                if x0 - 1 <= xx <= x1 + 1:
                    col = ICE[0] if xx < px else ICE[2] if xx > px else (ICE[3] if y <= top + 1 else ICE[1])
                    c[y, xx] = (*col, 255)
            for xx in (px - half - 1, px + half + 1):
                if x0 - 1 <= xx <= x1 + 1:
                    c[y, xx] = (*OUT, 255)
        c[top - 1, px] = (*OUT, 255)
    return c


def dead(P, k):
    near, far = DEAD_ARMS[k]
    c = np.zeros((128, 128, 4), np.uint8)
    paint(c, arm(P, "far", far))
    T.put(c, P.body, 0, 0)
    paint(c, arm(P, "near", near))
    return ice(c, DEAD_ICE[k], 7)


def finish(a):
    T.OUT = OUT
    T.SOLES = SOLES
    return T.finish(a)


def frames(P, tag):
    n = len(MS[tag])
    if tag == "idle":
        return [P.design.copy() for _ in range(n)]
    if tag == "run":
        return [finish(glide(P, k)) for k in range(n)]
    if tag == "dead":
        return [finish(dead(P, k)) for k in range(n)]
    return [finish(posed(P, p)) if p is not None else P.design.copy() for p in POSES[tag]]


def sheet(frs):
    T.CELL, T.PIVOT, T.CELL_PIVOT = CELL, PIVOT, CELL_PIVOT
    return T.sheet(frs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write review sheets to this folder")
    ap.add_argument("--out", default=NATIVE)
    a = ap.parse_args()
    P = Parts()
    built = {tag: frames(P, tag) for tag in TAGS}
    bad = 0
    for tag in TAGS:
        big = Image.fromarray(np.repeat(np.repeat(sheet(built[tag]), Z, 0), Z, 1))
        path = os.path.join(a.out, f"lissandra_{tag}.png")
        if a.check:
            same = os.path.exists(lp(path)) and np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")),
                                                                np.asarray(big))
            print(tag, "same" if same else "DIFFERS")
            bad += not same
        else:
            big.save(lp(path))
        print(f"{tag}: {len(built[tag])} frames, pieces {[len(T.pieces(f)) for f in built[tag]]}")
    cells = {"cell": list(CELL), "scale": Z,
             "tags": {tag: [{"pivot": list(CELL_PIVOT), "ms": ms} for ms in MS[tag]] for tag in TAGS}}
    cpath = os.path.join(a.out, "lissandra_cells.json")
    text = json.dumps(cells, indent=1) + "\n"
    if a.check:
        same = os.path.exists(lp(cpath)) and open(lp(cpath), encoding="utf-8").read() == text
        print("cells", "same" if same else "DIFFERS")
        bad += not same
    else:
        with open(lp(cpath), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    if a.review:
        T.DESIGN = DESIGN
        T.SOLES = SOLES
        T.review(P, built, a.review)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

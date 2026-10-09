#!/usr/bin/env python3
"""Lillia's action strips posed from design step 12 (the Codex grid redraw: the girl growing from the deer's withers,
League's ice-blue eyes; design_lillia.py --pick grid12).

    python tools/art/rig_lillia2.py [--check] [--review DIR] [--tags attack,skill] [--parts PNG]

2026-10-09, the user: 「眼睛做的像英雄联盟一点」「把形状也换了」「人形和身体连接也不像英雄联盟」 -> Codex redrew the design
on the game grid; this rig replaces rig_lillia.py for it. Nothing is resampled but the whole figure's leans (RotSprite,
one piece, as rig_lillia's - accepted on 10-09) and the bough's 45-degree turns: every frame is the design with
- the bough's top (the blossom, the gold hook and the lantern: one rigid piece) turned about the shaft's joint and the
  shaft drawn as a straight line from the grip between her hands (the design's own bough when it rests);
- the four legs the design's own, each swung about the hip by whole-row shifts (rigkit.swing_leg), the boots lifted
  or planted; a leg whose top the body's lean or rise leaves open is lengthened by repeating its top row;
- the figure above the legs leaning (K.turn) or moved whole; the run a trot with the body bobbing;
- the death League's fall on her side: the whole figure turned over, the bough on the ground.
The idle is the design six times (import_native breathes it). Writes assets/source/native/lillia_<tag>.png (8x, cells
CELL) and lillia_cells.json; then tools/art/import_native.py.
"""
import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "lillia_native.png")
HERO = "lillia"
PIVOT = (64, 88)                       # the standing point (the hooves on row 99, their middle on column 64)
CELL, CELL_PIVOT = (112, 96), (52, 75)
SOLES = 99
OUTLINE = K.rgb("#090617")
MS = {"idle": [200] * 6, "run": [92] * 8, "attack": [60, 60, 80, 80, 100], "skill": [60, 60, 70, 70, 70, 80],
      "skill2": [60, 60, 70, 80], "skill2_w": [80, 100, 100, 150, 80, 120, 120], "ult": [80, 80, 100, 100, 100, 100],
      "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}

# ------------------------------------------------------------------------------------------------ the design's parts
LEG_TOP = 88                           # the legs: rows from here down (row 87 is the belly line)
HOOF_ROW = 97                          # the hooves' top row (98-99 the hoof and its outline)
LEGS = {"A": (48, 55), "B": (56, 63), "C": (64, 70), "D": (71, 77)}   # column spans; A, B hind (image left), C, D front
TOP_BOX = (47, 53, 74, 83)             # rows, columns: the blossom and the gold hook
LANTERN_BOX = (54, 71, 76, 83)         # the chain from the hook's end, the lantern and its tassel
TOP_JOINT = (75.5, 53.5)               # the shaft square under the hook
LANTERN_JOINT = (78.5, 53.5)           # the chain's top (the hook's end)
HOOK_END = (LANTERN_JOINT[0] - TOP_JOINT[0], LANTERN_JOINT[1] - TOP_JOINT[1])
SHAFT = {K.rgb("#780843"), K.rgb("#B60970"), K.rgb("#601768"), K.rgb("#8842C2")}   # the shaft's purples
SHAFT_COL = K.rgb("#780843")
GRIP = (72.5, 73.5)                    # between her hands on the shaft
SHAFT_UP = (TOP_JOINT[0] - GRIP[0], TOP_JOINT[1] - GRIP[1])          # from the grip to the top's joint (design pose)
SHAFT_DOWN = 5.0                       # squares of shaft below the grip
MIDDLE = (64.0, 90.0)                  # a lean's pivot: the middle of the body
HIND_HOOVES = (56.0, 98.0)             # a rear's / the fall's pivot
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = D.a.copy()
        self.full = a
        op = a[..., 3] > 0
        R, C = np.mgrid[0:128, 0:128]
        ink = op & (a[..., :3] == np.array(OUTLINE, np.uint8)).all(-1)
        r0, r1, c0, c1 = TOP_BOX
        top_c = op & ~ink & (R >= r0) & (R <= r1) & (C >= c0) & (C <= c1)
        for y, x in zip(*np.nonzero(top_c)):
            if tuple(int(v) for v in a[y, x, :3]) == K.rgb("#EE168E"):     # her hair's strands reaching in
                top_c[y, x] = False
        shaft = np.zeros_like(op)
        for y in range(r1 + 1, 80):
            for x in range(66, 80):
                if op[y, x] and tuple(int(v) for v in a[y, x, :3]) in SHAFT:
                    shaft[y, x] = True
        l0, l1, lc0, lc1 = LANTERN_BOX
        lan_c = op & ~ink & (R >= l0) & (R <= l1) & (C >= lc0) & (C <= lc1)
        for y, x in zip(*np.nonzero(lan_c)):
            if tuple(int(v) for v in a[y, x, :3]) == K.rgb("#EE168E"):
                lan_c[y, x] = False
        others = op & ~ink & ~top_c & ~shaft & ~lan_c
        self.top_m = top_c | ring(ink, top_c, others | shaft | lan_c)
        self.lan_m = lan_c | ring(ink, lan_c, others | shaft | top_c)
        self.shaft_m = shaft | ring(ink, shaft, others | top_c | lan_c)
        self.top = K.Part.from_canvas(a, self.top_m, TOP_JOINT)
        self.lantern = K.Part.from_canvas(a, self.lan_m, LANTERN_JOINT)
        self.legs_m = {n: op & (R >= LEG_TOP) & (C >= s[0]) & (C <= s[1]) for n, s in LEGS.items()}
        self.body = a.copy()                          # the design without the bough (the hands stay)
        self.body[self.top_m | self.shaft_m | self.lan_m] = 0
        self.upper = self.body.copy()
        self.upper[LEG_TOP:] = 0


def ring(ink, c, others):
    """The outline squares round c that no square of `others` touches (4-neighbours)."""
    m = np.zeros_like(c)
    for y, x in zip(*np.nonzero(ink)):
        if any(c[y + dy, x + dx] for dy, dx in N8) and not any(others[y + dy, x + dx] for dy, dx in N4):
            m[y, x] = True
    return m


# ------------------------------------------------------------------------------------------------ the bough
def bough_layer(P, deg=0, slide=0.0, at=None, rest=None):
    """The bough turned deg clockwise on screen about the grip (the top in quarter turns exact, 45s by RotSprite),
    slid `slide` squares up its length, the grip at `at` (default the design's): the shaft a straight line of its
    purple from below the grip to the top's joint, ringed with outline, the top piece at the joint."""
    th = math.radians(deg)
    ux, uy = SHAFT_UP
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    rx, ry = ux * math.cos(th) - uy * math.sin(th), ux * math.sin(th) + uy * math.cos(th)     # up the bough, turned
    g = at or GRIP
    g = (g[0] - rx * slide, g[1] - ry * slide)
    layer = np.zeros_like(P.full)
    line = []
    for k in range(-int(SHAFT_DOWN), int(round(n)) + 1):
        x, y = int(math.floor(g[0] + rx * k)), int(math.floor(g[1] + ry * k))
        if 0 <= x < 128 and 0 <= y < 128:
            line.append((x, y))
            layer[y, x] = (*SHAFT_COL, 255)
    top = P.top
    if deg % 90 == 0:
        top = K.rot90(top, (deg // 90) % 4)
    else:
        top = K.turn(top, -deg)
    tip = (g[0] + rx * n, g[1] + ry * n)
    if deg % 90:                                   # a 45-degree top (RotSprite) breaks the thin gold hook into
        tl = np.zeros_like(layer)                  # crumbs: the gaps of one square between its pieces closed
        K.place(tl, top, tip)                      # with outline
        tm = tl[..., 3] > 0
        for _ in range(2):
            add = np.zeros_like(tm)
            for y, x in zip(*np.nonzero(~tm)):
                if 44 <= y < 100 and 40 <= x < 100 and sum(tm[y + dy, x + dx] for dy, dx in N4) >= 2:
                    add[y, x] = True
            tl[add] = (*OUTLINE, 255)
            tm |= add
        K.put(layer, tl, 0, 0)
    else:
        K.place(layer, top, tip)
    for k in range(int(round(n)) + 1, int(round(n)) + 6):      # the line runs on until it meets the turned top
        x, y = int(math.floor(g[0] + rx * k)), int(math.floor(g[1] + ry * k))
        if not (0 <= x < 128 and 0 <= y < 128) or layer[y, x, 3]:
            break
        line.append((x, y))
        layer[y, x] = (*SHAFT_COL, 255)
    hx, hy = HOOK_END
    hang = (tip[0] + hx * math.cos(th) - hy * math.sin(th), tip[1] + hx * math.sin(th) + hy * math.cos(th))
    if rest is not None:                     # the lantern resting on the ground
        hang = (hang[0], rest + 0.5 - (P.lantern.s.shape[0] - P.lantern.j[1]))
    K.place(layer, P.lantern, hang)          # the lantern hangs upright from the hook's end
    hook = (tip[0] + hx * 0.5 * math.cos(th) - hy * 0.5 * math.sin(th), tip[1] + hx * 0.5 * math.sin(th) + hy * 0.5 * math.cos(th))
    for k in range(0, 4):                    # a short dark link from the hook's middle to the chain's top
        x = int(math.floor(hook[0] + (hang[0] - hook[0]) * k / 3))
        y = int(math.floor(hook[1] + (hang[1] - hook[1]) * k / 3))
        if 0 <= x < 128 and 0 <= y < 128 and not layer[y, x, 3]:
            layer[y, x] = (*OUTLINE, 255)
    m = layer[..., 3] > 0
    rim = np.zeros_like(m)
    for x, y in line:
        for dy, dx in N4:
            if 0 <= y + dy < 128 and 0 <= x + dx < 128 and not m[y + dy, x + dx]:
                rim[y + dy, x + dx] = True
    layer[rim] = (*OUTLINE, 255)
    return layer


# ------------------------------------------------------------------------------------------------ legs and the body
def legs_layer(P, spec=None):
    """The four legs: spec = {name: (dx, lift)} swung about the hip row (whole-row shifts), far legs first."""
    out = np.zeros_like(P.full)
    spec = spec or {}
    for name in ("A", "C", "B", "D"):
        dx, lift = spec.get(name, (0, 0))
        m = P.legs_m[name]
        K.put(out, leg_pose(P, m, dx, lift, JOINT[name]), 0, 0)
    return out


JOINT = {"A": 93, "B": 93, "C": 92, "D": 92}     # the hock (hind) / the knee (front): where the design's legs bend


def leg_pose(P, m, dx, lift, joint=93):
    """The leg's lower part (from the joint row down) moved dx whole, the upper part in place, the whole leg lifted
    `lift` rows: every square kept (「腿部有点失去像素和变形」, then 「还是有点断腿的感觉」 at a hip-side shear) and the one
    step falls on the joint where the leg bends anyway."""
    leg = np.zeros_like(P.full)
    dx = max(-2, min(2, dx))                       # a stride of two: one column at the hip, one at the joint - a
    up = max(-1, min(1, dx))                       # jog of one square each, never a two-square break
    low = dx - up
    for r, c in zip(*np.nonzero(m & (P.full[..., 3] > 0))):
        sh = up + (low if r >= joint else 0)
        rr, cc = r - lift, c + sh
        if 0 <= rr < 128 and 0 <= cc < 128:
            leg[rr, cc] = P.full[r, c]
    return leg


def turned(a, deg, pivot, move=(0, 0)):
    out = np.zeros_like(a)
    if not a[..., 3].any():
        return out
    if deg:
        part = K.Part.from_canvas(a, a[..., 3] > 0, pivot)
        K.place(out, K.turn(part, deg), (pivot[0] + move[0], pivot[1] + move[1]))
    else:
        K.put(out, a, int(move[0]), int(move[1]))
    return out


def join_legs(up, low, spans, most=9):
    """Where a leg's top row sits under open space (the body leaned or risen off it), the leg's top row is repeated
    upward until it meets the body (at most `most` rows)."""
    out = low.copy()
    for c0, c1 in spans:
        cols = range(c0, c1 + 1)
        tops = [y for y in range(128) if any(low[y, x, 3] for x in cols)]
        if not tops:
            continue
        t = tops[0]
        for k in range(1, most + 1):
            y = t - k
            if y < 0:
                break
            row_has_body = any(up[y, x, 3] for x in cols)
            if row_has_body:
                break
            for x in cols:
                if low[t, x, 3] and not up[y, x, 3]:
                    out[y, x] = low[t, x]
    return out


def frame(P, bough=None, tilt=0.0, pivot=MIDDLE, move=(0, 0), legs=None, sink=0, join=9):
    """One frame: the upper figure (the bough turned per (deg, slide), or the design's own when None) leaned `tilt`
    about `pivot` and moved whole, over the legs swung per `legs` and moved with it; `sink` lowers the upper body
    onto the legs (a crouch)."""
    if bough is None:
        up = P.full.copy()
        up[LEG_TOP:] = 0
    else:
        deg, slide = bough
        up = P.upper.copy()
        K.put(up, bough_layer(P, deg, slide), 0, 0)
    up = turned(up, tilt, pivot, (move[0], move[1] + sink))
    low = legs_layer(P, legs)
    if move != (0, 0):
        low = K.shifted(low, int(move[0]), int(move[1]))
    spans = [(s[0] + int(move[0]) - 3, s[1] + int(move[0]) + 3) for s in LEGS.values()]
    low = join_legs(up, low, spans, join)
    out = low.copy()
    K.put(out, up, 0, 0)
    out[SOLES + 1:] = 0
    return finish(P, out, move)


def finish(P, a, move=(0, 0)):
    """rigkit.finish on what the frame changed: every square still the design's own (moved whole with the frame)
    is kept as drawn - the design's gaps, its lone outline squares (the lantern's chain and tassel) stay."""
    ref = K.shifted(P.full, int(move[0]), int(move[1]))
    keep = (a[..., 3] > 0) & (a == ref).all(-1)
    return bridge(K.finish(a, OUTLINE, SOLES, keep=keep, pinholes=3))


def bridge(a, small=80, reach=2):
    """A turn (RotSprite) breaks the design's thin lines - the lantern's chain and tassel, the gold hook - into
    crumbs a square or two off the figure: every piece under `small` squares within `reach` of the main piece is
    joined to it by outline squares along the gap."""
    for _ in range(3):
        ps = K.pieces(a)
        if len(ps) <= 1:
            break
        main = set(ps[0])
        did = False
        for comp in ps[1:]:
            if len(comp) >= small:
                continue
            best = None
            for (y, x) in comp:
                for (my, mx) in main:
                    d = max(abs(my - y), abs(mx - x))
                    if d <= reach + 1 and (best is None or d < best[0]):
                        best = (d, y, x, my, mx)
            if best is None:
                continue
            d, y, x, my, mx = best
            for k in range(1, d):
                yy = y + round((my - y) * k / d)
                xx = x + round((mx - x) * k / d)
                if not a[yy, xx, 3]:
                    a[yy, xx] = (*OUTLINE, 255)
                    did = True
            if d == 1 or (d == 2 and not did):
                yy, xx = (y + my) // 2, (x + mx) // 2
                if not a[yy, xx, 3]:
                    a[yy, xx] = (*OUTLINE, 255)
                    did = True
        if not did:
            break
    return a


# ------------------------------------------------------------------------------------------------ the run (a trot)
STANCE = [2, 1, -1, -2]
SWING = [(1, -2), (2, -1), (2, 1), (1, 2)]       # (lift, dx) of the pair in the air
BOB = [1, 0, 0, 0, 1, 0, 0, 0]


def trot_spec(i):
    ground, air = (("B", "C"), ("A", "D")) if i < 4 else (("A", "D"), ("B", "C"))
    k = i % 4
    spec = {n: (STANCE[k], 0) for n in ground}
    lift, dx = SWING[k]
    for n in air:
        spec[n] = (dx, lift)
    return spec


def run_frame(P, i):
    return frame(P, None, move=(0, BOB[i]), legs=trot_spec(i))


# ------------------------------------------------------------------------------------------------ the death
def grounded(a, ground=SOLES):
    ys = np.nonzero(a[..., 3].any(1))[0]
    return K.shifted(a, 0, ground - int(ys.max())) if len(ys) else a


def fall(P, deg, bough_x=62.5):
    src = P.body.copy()
    out = grounded(turned(src, deg, HIND_HOOVES))
    xs = np.nonzero(out[..., 3].any(0))[0]
    left = PIVOT[0] - CELL_PIVOT[0] + 2
    if len(xs) and xs.min() < left:
        out = K.shifted(out, left - int(xs.min()), 0)
    lay = bough_layer(P, 90, 0, (bough_x, 96.5))
    K.put(out, grounded(lay, SOLES - 1), 0, 0, under=True)
    out[SOLES + 1:] = 0
    return finish(P, out)


# ------------------------------------------------------------------------------------------------ the actions
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_w", "ult", "hit", "dead"]
HOP = {"A": (-2, 1), "B": (-2, 1), "C": (1, 2), "D": (1, 2)}        # hind legs back, front legs tucked up a little
REACH = {"A": (-2, 0), "B": (-2, 0), "C": (2, 0), "D": (2, 0)}
BENT = {"A": (-1, 0), "B": (-1, 0), "C": (1, 0), "D": (1, 0)}
REAR = {"C": (-3, 4), "D": (-3, 4)}                                  # rearing: the front legs folded back under the
REAR7 = {"C": (-4, 6), "D": (-4, 6)}                                 # raised chest (hidden behind the body)
LIFT2 = {"C": (0, 2), "D": (0, 2)}


def build(P):
    F = {}
    F["idle"] = [P.full.copy() for _ in range(6)]
    F["run"] = [run_frame(P, i) for i in range(8)]
    # the basic attack: lean back with the bough over her shoulder, hop forward, the swing lands, the landing
    F["attack"] = [frame(P, (-45, 0), tilt=5), frame(P, (0, 3), tilt=-10, move=(1, -4), legs=HOP),
                   frame(P, (90, 0), tilt=-6, move=(1, -2), legs=REACH), frame(P, (135, -3), tilt=-3, sink=1, legs=BENT),
                   P.full.copy()]
    # Q: the bough spun round her - back, overhead with a hop, swept forward (the hit), low, back
    F["skill"] = [frame(P, (-90, 0), tilt=4, sink=1, legs=BENT), frame(P, (0, 3), tilt=-4, move=(0, -3), legs=HOP),
                  frame(P, (90, 0), tilt=-3, move=(1, -2), legs=REACH), frame(P, (135, -3), tilt=-4, move=(1, 0)),
                  frame(P, (-90, 0), tilt=3), P.full.copy()]
    # E: a crouch with the bough low behind, up leaning back, the throw up and forward
    F["skill2"] = [frame(P, (-90, 0), tilt=-3, sink=2, legs=BENT), frame(P, (-45, 2), tilt=8),
                   frame(P, (45, 3), tilt=-6, move=(1, -1), legs=REACH), P.full.copy()]
    # W: crouch, rear up with the bough raised high, hold, slam it down in front, recover
    F["skill2_w"] = [frame(P, (-90, 0), tilt=-4, sink=2, legs=BENT), frame(P, (0, 5), tilt=20, pivot=HIND_HOOVES, legs=REAR, join=1),
                     frame(P, (0, 7), tilt=28, pivot=HIND_HOOVES, legs=REAR7, join=1),
                     frame(P, (0, 7), tilt=28, pivot=HIND_HOOVES, legs=REAR7, join=1),
                     frame(P, (135, -5), tilt=-6, move=(1, 1), legs=REACH), frame(P, (135, -4), tilt=-4, legs=BENT),
                     P.full.copy()]
    # R: gather, rise with the bough up, the lullaby swung over her head
    F["ult"] = [frame(P, (0, 0), sink=1, legs=BENT), frame(P, (0, 3), tilt=8, pivot=HIND_HOOVES, legs=LIFT2),
                frame(P, (45, 3), tilt=6, pivot=HIND_HOOVES, legs=LIFT2),
                frame(P, (-45, 3), tilt=4, pivot=HIND_HOOVES, legs={"C": (0, 1), "D": (0, 1)}),
                frame(P, (45, 2), tilt=2, pivot=HIND_HOOVES), P.full.copy()]
    F["hit"] = [frame(P, None, tilt=6, pivot=HIND_HOOVES, legs=LIFT2), P.full.copy()]
    lie = fall(P, 80)
    F["dead"] = [frame(P, None, tilt=8, pivot=HIND_HOOVES, legs=LIFT2),
                 frame(P, None, tilt=22, pivot=HIND_HOOVES, legs=REAR, join=1),
                 fall(P, 45, bough_x=66.5), lie, lie.copy(), lie.copy(), lie.copy(), lie.copy()]
    return F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="folder for the review sheet and GIF")
    ap.add_argument("--tags")
    ap.add_argument("--parts", help="write the part overlay PNG and stop")
    a = ap.parse_args()
    P = Parts()
    if a.parts:
        from PIL import Image
        d = P.full.astype(float)
        out = d.copy()
        tint = {"top": ((255, 0, 0), P.top_m), "shaft": ((255, 120, 0), P.shaft_m), "lantern": ((0, 120, 255), P.lan_m)}
        for n in LEGS:
            tint[n] = ({"A": (0, 200, 0), "B": (0, 220, 255), "C": (255, 0, 255), "D": (255, 200, 0)}[n], P.legs_m[n])
        for n, (colr, m) in tint.items():
            out[m, :3] = d[m, :3] * 0.4 + np.array(colr) * 0.6
        sub = out[44:101, 44:86].astype(np.uint8)
        Image.fromarray(sub).resize((sub.shape[1] * 12, sub.shape[0] * 12), Image.NEAREST).save(a.parts)
        print({n: int(m.sum()) for n, (_, m) in tint.items()})
        return
    F = build(P)
    if a.tags:
        F = {t: F[t] for t in a.tags.split(",") if t in F}
    for tag, frs in F.items():
        print(tag, K.audit(frs, P.full, OUTLINE, SOLES))
    x0, y0 = PIVOT[0] - CELL_PIVOT[0], PIVOT[1] - CELL_PIVOT[1]
    for tag, frs in F.items():
        for i, f in enumerate(frs):
            ys, xs = np.nonzero(f[..., 3])
            if xs.min() < x0 or xs.max() >= x0 + CELL[0] or ys.min() < y0 or ys.max() >= y0 + CELL[1]:
                print("OUT OF THE CELL:", tag, i, xs.min(), xs.max(), ys.min(), ys.max())
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        rows = [(t, frs) for t, frs in F.items()]
        K.review_sheet(rows, os.path.join(a.review, "lillia_rig.png"), z=6, soles=SOLES)
        K.review_gif(rows, MS, os.path.join(a.review, "lillia_rig.gif"), z=4)
    if not a.tags:
        bad = K.write_strips(HERO, F, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
            sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

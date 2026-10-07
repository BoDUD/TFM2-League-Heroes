#!/usr/bin/env python3
"""Lillia's action strips posed from the approved design itself (the casting body = the idle's).

    python tools/art/rig_lillia.py [--check] [--review DIR] [--tags attack,skill]

Codex's step-2 round (assets/source/lillia/codex_strips/) re-posed the design's pixels, but squares went missing, the
run slid (no bob, the legs barely moving) and the chest stuck out where the bough left it. The user: 「像素缺失 还有走路
不掉很奇怪 还有应该有不少问题」, 「这里露出来一大截啊」. A first rig took her arms off and drew them per pose (rigkit.bone_arm
over a torso drawn without arms): 「我觉得还是奇怪 这个身体」, 「腰部大规模像素消失啊 而且这个莉莉娅没有英雄联盟那种自然的感觉」,
「感觉不像是连体的」. So this rig never takes the girl apart:
- every frame is the design (design_lillia.py step 10) - her arms, hands, waist, hair and the deer as drawn;
- the bough (one purple line, the design's top part turned with it in steps of 45 degrees, the lantern hanging upright
  from the hook or resting on the ground) turns about the grip between her two hands and slides through them;
- the motion is the whole body's, as League's Lillia moves (poses.json's clips rendered by native_pose.py): the figure
  above the legs turned whole by RotSprite about a pivot (lean back, hop forward, rear up, crouch) and moved, the four
  legs drawn again from the turned hips in the design's style (2 squares, the hocks, the hooves), tucked or planted;
- the run: a trot - the legs in diagonal pairs, the lifted pair 1-2 rows up, the body 1 row down on each landing, the
  lantern swinging;
- the death: League's fall-over - jolted and rearing back, then the figure with its legs curled turned over on its side,
  the bough dropped on the ground in front.
The idle frames are the design (import_native breathes them). Every frame is finished alike (rigkit.finish, doubled
outline on the edge taken off). Writes assets/source/native/lillia_<tag>.png (8x, cells CELL) and lillia_cells.json;
then tools/art/import_native.py.
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
import design_lillia as DL  # noqa: E402
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "lillia_native.png")
HERO = "lillia"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the hooves on row 99)
CELL, CELL_PIVOT = (112, 96), (52, 75)
SOLES = 99
MS = {"idle": [200] * 6, "run": [92] * 8, "attack": [60, 60, 80, 80, 100], "skill": [60, 60, 70, 70, 70, 80],
      "skill2": [60, 60, 70, 80], "skill2_w": [80, 100, 100, 150, 80, 120, 120], "ult": [80, 80, 100, 100, 100, 100],
      "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}


def C(ch):
    return (*DL.hx(DL.LETTERS[ch]), 255)


OUTLINE = DL.hx(DL.LETTERS["K"])

# ------------------------------------------------------------------------------------------------ the design's parts
# the bough on the design: the line at column 75, its top part rows 54-62, the lantern from row 63
TOP_BOX = (54, 62, 72, 81)            # rows, columns: the blossom, the hook, the shaft's top and its two leaves
TOP_JOINT = (75.5, 62.5)              # the shaft square under the top part
HOOK_END = (78.5, 62.5)               # the gold link the lantern hangs from
LANTERN_BOX = (63, 78, 76, 84)
LANTERN_JOINT = (79.0, 63.0)          # the top of its cap
TOP_LEN, BOTTOM_LEN = 18, 7           # squares from the grip to the top part's joint / to the tip at the bottom
DESIGN_FIX = DL.FIX10                  # in the design since step 10 (applying it again changes nothing)


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = DL.apply_letters(D.a.copy(), DESIGN_FIX)
        self.full = a
        r0, r1, c0, c1 = TOP_BOX
        top = K.mask_box(r0, r1, c0, c1)
        self.top = K.Part.from_canvas(a, top, TOP_JOINT)
        r0, r1, c0, c1 = LANTERN_BOX
        lan = K.mask_box(r0, r1, c0, c1)
        self.lantern = K.Part.from_canvas(a, lan, LANTERN_JOINT)


# ------------------------------------------------------------------------------------------------ the bough
DIRS = {0: (0, -1), 45: (1, -1), 90: (1, 0), 135: (1, 1), 180: (0, 1), -45: (-1, -1), -90: (-1, 0), -135: (-1, 1)}


def turned_top(P, deg):
    """The top part turned deg clockwise on screen (quarter turns exact, 45s by RotSprite)."""
    if deg % 90 == 0:
        return K.rot90(P.top, (deg // 90) % 4)
    return K.turn(P.top, -deg)


def rotate_offset(off, deg):
    th = math.radians(deg)
    x, y = off
    return (x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th))


def bough(dst, P, grip, deg, rest=None, behind=False, flip=False):
    """The bough drawn into dst: the line from the grip, the top part at its end, the lantern hanging from the hook (or
    resting with its bottom on row `rest`); behind=True draws it under the figure. Returns the unit vector up the
    bough (from the tip toward the top)."""
    dx, dy = DIRS[deg]
    diag = dx != 0 and dy != 0
    top_n = int(round(TOP_LEN / (math.sqrt(2) if diag else 1)))
    bot_n = int(round(BOTTOM_LEN / (math.sqrt(2) if diag else 1)))
    gx, gy = int(math.floor(grip[0])), int(math.floor(grip[1]))
    line = [(gx + dx * i, gy + dy * i) for i in range(-bot_n, top_n + 1)]
    layer = np.zeros_like(dst)
    for x, y in line[:-1]:
        layer[y, x] = C("Q")
    tx, ty = line[-1]
    tip = (tx + 0.5, ty + 0.5)
    top = turned_top(P, deg)
    K.place(layer, top.flip_v() if flip else top, tip)
    bx, by = line[0]
    layer[by, bx] = C("q")
    out = K.put(dst.copy(), layer, 0, 0, under=behind)
    # the line's outline where it stands free (over the body it is drawn bare, as on the design's chest)
    ring = np.zeros(dst.shape[:2], bool)
    for x, y in line[:-1]:
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < 128 and 0 <= nx < 128 and out[ny, nx, 3] == 0:
                ring[ny, nx] = True
    out[ring] = (*OUTLINE, 255)
    hx, hy = rotate_offset((HOOK_END[0] - TOP_JOINT[0], HOOK_END[1] - TOP_JOINT[1]), deg)
    hang = (tip[0] + hx, tip[1] + hy)
    if rest is not None:
        h = P.lantern.s.shape[0] - P.lantern.j[1]
        hang = (hang[0], rest + 1 - h)
    K.place(out, P.lantern, (hang[0] + 0.5, hang[1] + 0.5), under=behind)
    dst[:] = out
    n = math.hypot(dx, dy)
    return dx / n, dy / n


# ------------------------------------------------------------------------------------------------ legs
# the design's legs: 2 squares each (lit, shade), rows 89-96, the hoof 3 x 2 on rows 97-98 (its outline on 99); the
# hind legs' hock one more square behind on rows 93-94. Drawn legs keep exactly that, each row moved whole columns
LEG_X = {"A": 54, "B": 58, "C": 66, "D": 72}
NEAR_LEG = {"A": False, "B": True, "C": True, "D": False}
HIND = {"A", "B"}
LEG_TOP, LEG_N = 89, 8


def rnd(v):
    return int(math.floor(v + 0.5))


def leg_shifts(n, hoof, bend=0.0, joint=None):
    """Column shifts of a leg's n rows: a straight slant to `hoof`, or bent - the joint row (the knee / hock) out by
    `bend`, then on to `hoof`."""
    if not bend:
        return [rnd(hoof * k / max(1, n - 1)) for k in range(n)]
    j = joint if joint is not None else n // 2
    j = max(1, min(n - 2, j))
    up = [rnd(bend * k / j) for k in range(j + 1)]
    low = [rnd(bend + (hoof - bend) * (k - j) / (n - 1 - j)) for k in range(j + 1, n)]
    return up + low


def leg_layer(name, top, shifts, hock=True):
    """One leg in the design's style from row `top`, row k moved shifts[k] columns, the hoof under it."""
    lit, dark = ("O", "b") if NEAR_LEG[name] else ("b", "a")
    L = np.zeros((128, 128, 4), np.uint8)
    x0 = LEG_X[name]
    n = len(shifts)
    for k, sh in enumerate(shifts):
        L[top + k, x0 + sh] = C(lit)
        L[top + k, x0 + sh + 1] = C(dark)
    if name in HIND and hock and n >= 6:
        for k in (n * 4 // 8, n * 5 // 8):
            L[top + k, x0 + shifts[k] - 1] = C(lit)
    fx, fy = x0 + shifts[-1], top + n
    for i, ch in enumerate("eeV"):
        L[fy, fx + i] = C(ch)
    for i, ch in enumerate("uee"):
        L[fy + 1, fx + i] = C(ch)
    m = L[..., 3] > 0
    ring = np.zeros_like(m)
    ring[1:] |= m[:-1]
    ring[:-1] |= m[1:]
    ring[:, 1:] |= m[:, :-1]
    ring[:, :-1] |= m[:, 1:]
    ring &= ~m
    ring[:top] = False
    L[ring] = (*OUTLINE, 255)
    return L


def legs_layer(spec, body_dy=0):
    """The four legs: spec = {name: dict(hoof=, lift=, bend=, joint=, shifts=)} (missing: standing straight), hips on
    row LEG_TOP + body_dy; far legs first, the near legs over them."""
    out = np.zeros((128, 128, 4), np.uint8)
    for name in ("A", "D", "B", "C"):
        kw = dict(spec.get(name, {}))
        top = LEG_TOP + body_dy
        n = LEG_N - body_dy - kw.get("lift", 0)
        sh = kw.get("shifts") or leg_shifts(n, kw.get("hoof", 0), kw.get("bend", 0), kw.get("joint"))
        K.put(out, leg_layer(name, top, sh), 0, 0)
    return out


def design_legs(P):
    a = np.zeros_like(P.full)
    a[LEG_TOP:] = P.full[LEG_TOP:]
    return a


def figure(P, upper, legs=None, body_dy=0, low=None):
    """The upper figure (no legs) moved body_dy rows down, over the legs: `low` (a legs layer), the design's own, or
    drawn from the spec `legs`."""
    if low is None:
        low = design_legs(P) if legs is None and body_dy == 0 else legs_layer(legs or {}, body_dy)
    out = low.copy()
    K.put(out, upper, 0, body_dy)
    return out


# ------------------------------------------------------------------------------------------------ frames


def lantern_swing(a, dx):
    """The design's lantern (on a frame built from P.full) moved dx columns."""
    if not dx:
        return a
    r0, r1, c0, c1 = LANTERN_BOX
    out = a.copy()
    lan = np.zeros_like(a)
    lan[r0:r1 + 1, c0 + 1:c1 + 1] = a[r0:r1 + 1, c0 + 1:c1 + 1]
    out[r0:r1 + 1, c0 + 1:c1 + 1] = 0
    return K.put(out, K.shifted(lan, dx, 0), 0, 0)


# the trot: diagonal pairs - X (B near hind, D far front) and Y (A far hind, C near front); 8 frames, X on the ground
# in 0-3 (its hooves going back under the body), Y in 4-7; the lifted pair passing forward 1-2 rows up; the body one
# row down on each landing (frames 0 and 4)
STANCE = [2, 1, -1, -2]
SWING = [(1, -2), (2, -1), (2, 1), (1, 2)]
BOB = [1, 0, 0, 0, 1, 0, 0, 0]
SWAY = [0, 1, 1, 0, 0, 1, 1, 0]


def trot_spec(i):
    ground, air = (("B", "D"), ("A", "C")) if i < 4 else (("A", "C"), ("B", "D"))
    k = i % 4
    spec = {}
    for name in ground:
        spec[name] = dict(hoof=STANCE[k])
    lift, hoof = SWING[k]
    for name in air:
        front = name not in HIND
        # the knee (front) one square ahead of the straight line at its middle, the hock (hind) one behind
        spec[name] = dict(hoof=hoof, lift=lift, bend=hoof / 2 + (1 if front else -1), joint=None if front else 4)
    return spec


def run_frame(P, i):
    up = lantern_swing(P.full, SWAY[i]).copy()
    up[LEG_TOP:] = 0
    a = figure(P, up, trot_spec(i), BOB[i])
    return done(P, a)




def unarmed(P):
    """The design without the bough (its top, lantern and shaft); the hands stay."""
    a = P.full.copy()
    a[K.mask_box(*TOP_BOX)] = 0
    a[K.mask_box(*LANTERN_BOX)] = 0
    for y in range(63, 89):
        if tuple(a[y, 75, :3]) in (DL.hx(DL.LETTERS["Q"]), DL.hx(DL.LETTERS["q"])) and a[y, 75, 3]:
            a[y, 75] = (*OUTLINE, 255) if y >= 85 else (0, 0, 0, 0)
            a[y, 76] = 0
    return a


# ------------------------------------------------------------------------------------------------ the puppet
# The user at the arms-off torso: 「腰部大规模像素消失啊 而且这个莉莉娅没有英雄联盟那种自然的感觉」, 「感觉不像是连体的」.
# So the girl keeps the design's own arms and hands in every frame (the waist never opens, the girl and the deer stay
# one body); the bough turns about the grip between her hands (and slides up / down through them); the motion comes
# from the whole body as League's Lillia moves (assets/source/lillia/poses.json's clips, rendered by native_pose.py):
# she leans back to wind up, hops forward to strike, rears to raise W, crouches before E, falls over when she dies -
# the figure above the legs turned whole by RotSprite about a pivot, the four legs drawn again from the turned hips.
GRIP = (75.5, 80.5)                   # between the design's two hands on the bough
HANDS = [(78, 74), (78, 75), (79, 74), (79, 75), (81, 74), (81, 75), (82, 74), (82, 75)]   # (row, column)
HIP_Y = 88.5


def upper(P, deg=None, slide=0.0, rest=None, lantern_dx=0):
    """The figure above the legs: the design (its arms and hands as drawn) with the bough turned to `deg` about the
    grip and slid `slide` squares up its length (None: the design's own bough, its lantern moved lantern_dx)."""
    if deg is None:
        a = lantern_swing(P.full, lantern_dx).copy()
        a[LEG_TOP:] = 0
        return a
    a = unarmed(P)
    a[LEG_TOP:] = 0
    dx, dy = DIRS[deg]
    n = math.hypot(dx, dy)
    g = (GRIP[0] + dx / n * slide, GRIP[1] + dy / n * slide)
    bough(a, P, g, deg, rest=rest, behind=True)
    for y, x in HANDS:
        a[y, x] = P.full[y, x]
    return a


def outside(a):
    """The clear squares joined to the canvas edge."""
    clear = a[..., 3] == 0
    seen = np.zeros_like(clear)
    H, W = clear.shape
    st = [(y, x) for y in range(H) for x in (0, W - 1) if clear[y, x]] +          [(y, x) for x in range(W) for y in (0, H - 1) if clear[y, x]]
    for p in st:
        seen[p] = True
    while st:
        y, x = st.pop()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < H and 0 <= nx < W and clear[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                st.append((ny, nx))
    return seen


def done(P, a):
    """rigkit.finish, then the outline squares a turn doubled up on the silhouette's edge (nothing coloured round
    them) gone; inside the figure they stay (taking them would open a hole: 「像素缺失」)."""
    a = K.finish(a, P.D.outline, SOLES)
    while True:
        out = outside(a)
        edge = np.zeros_like(out)
        edge[1:] |= out[:-1]
        edge[:-1] |= out[1:]
        edge[:, 1:] |= out[:, :-1]
        edge[:, :-1] |= out[:, 1:]
        gone = K.orphan_outline(a, P.D.outline) & edge
        if not gone.any():
            return a
        a[gone] = 0


def turn_point(q, pivot, deg):
    """Where the point q goes when the figure turns deg counter-clockwise on screen about pivot (rigkit.turn's way)."""
    th = math.radians(deg)
    dx, dy = q[0] - pivot[0], q[1] - pivot[1]
    return (pivot[0] + dx * math.cos(th) + dy * math.sin(th), pivot[1] - dx * math.sin(th) + dy * math.cos(th))


def turned(a, deg, pivot, move=(0, 0)):
    """The layer a turned deg about pivot (RotSprite) and moved."""
    out = np.zeros_like(a)
    if not a[..., 3].any():
        return out
    if deg:
        part = K.Part.from_canvas(a, a[..., 3] > 0, pivot)
        K.place(out, K.turn(part, deg), (pivot[0] + move[0], pivot[1] + move[1]))
    else:
        K.put(out, a, int(move[0]), int(move[1]))
    return out


def leg_to(name, hip, hoof, bend=0.0, joint=0.5):
    """One leg in the design's style from the hip point (its top centre) down to the hoof (its top-left square), the
    joint (knee / hock) `joint` of the way down pushed `bend` columns (+ forward)."""
    top = int(math.floor(hip[1])) - 1
    fx, fy = hoof
    n = max(2, fy - top)
    x_top = hip[0] - 1.0
    j = max(1, min(n - 2, int(round(joint * (n - 1)))))
    xs = []
    for k in range(n):
        straight = x_top + (fx - x_top) * k / (n - 1)
        off = bend * (k / j if k <= j else (n - 1 - k) / (n - 1 - j))
        xs.append(rnd(straight + off))
    return leg_layer(name, top, [x - LEG_X[name] for x in xs])


def body(P, up, tilt=0.0, pivot=(56.0, 98.0), move=(0, 0), legs=None):
    """A frame: `up` turned `tilt` degrees about `pivot` (counter-clockwise: the front rises) and moved, over the four
    legs drawn from the turned hips - legs = {name: dict(hoof=(x, y), bend=, joint=)}, a missing leg stands on its
    design hoof; the design's own legs when nothing moves."""
    if not tilt and move == (0, 0) and legs is None:
        out = design_legs(P)
        K.put(out, up, 0, 0)
        return done(P, out)
    out = np.zeros_like(up)
    legs = legs or {}
    for name in ("A", "D", "B", "C"):
        hip = turn_point((LEG_X[name] + 1.0, HIP_Y), pivot, tilt)
        hip = (hip[0] + move[0], hip[1] + move[1])
        kw = dict(legs.get(name, {}))
        hoof = kw.pop("hoof", (LEG_X[name], 97))
        K.put(out, leg_to(name, hip, hoof, **kw), 0, 0)
    K.put(out, turned(up, tilt, pivot, move), 0, 0)
    return done(P, out)


def tuck(name, hip_dx=0, up=4, bend=2):
    """A leg folded up under the body: its hoof `up` rows above the ground, the knee (front) forward / the hock
    (hind) back."""
    front = name not in HIND
    return dict(hoof=(LEG_X[name] + hip_dx, 97 - up), bend=bend if front else -bend, joint=0.5)


HIND_HOOVES = (56.0, 98.0)            # the pivot of a rear / a flinch / the fall: the hind hooves on the ground
MIDDLE = (64.0, 90.0)                 # the pivot of a lean or a hop: the middle of the body


def grounded(P, a, ground=99):
    """A fallen frame moved up or down whole so its lowest square sits on the ground row."""
    ys = np.nonzero(a[..., 3].any(1))[0]
    return K.shifted(a, 0, ground - int(ys.max())) if len(ys) else a


# the death: League's Lillia falls over on her side, the legs loose - the figure (the bough dropped) with its legs
# curled turned over whole about the hind hooves, set on the ground, the bough lying in front of the legs
LOOSE = {"C": dict(hoof=(LEG_X["C"], 94), bend=2, joint=0.5), "D": dict(hoof=(LEG_X["D"], 95), bend=1, joint=0.5),
         "A": dict(hoof=(LEG_X["A"] + 2, 95), bend=-1, joint=0.5), "B": dict(hoof=(LEG_X["B"] + 2, 94), bend=-2, joint=0.5)}


def fall(P, deg, bough_x=62.5):
    a = unarmed(P)
    a[LEG_TOP:] = 0
    src = np.zeros_like(a)
    for name in ("A", "D", "B", "C"):
        kw = dict(LOOSE[name])
        hoof = kw.pop("hoof")
        K.put(src, leg_to(name, (LEG_X[name] + 1.0, HIP_Y), hoof, **kw), 0, 0)
    K.put(src, a, 0, 0)
    out = grounded(P, turned(src, deg, HIND_HOOVES))
    lay = np.zeros_like(out)
    bough(lay, P, (bough_x, 95.5), 90, rest=98, flip=True)
    K.put(out, lay, 0, 0, under=True)
    return done(P, out)


def build(P):
    F = {}
    F["idle"] = [P.full.copy() for _ in range(6)]
    F["run"] = [run_frame(P, i) for i in range(8)]
    front_up = lambda up, bend=2: {n: tuck(n, up=up, bend=bend) for n in "CD"}
    hop = {"C": tuck("C", hip_dx=1, up=5, bend=2), "D": tuck("D", hip_dx=1, up=5, bend=2),
           "A": dict(hoof=(LEG_X["A"] - 3, 95), bend=-1), "B": dict(hoof=(LEG_X["B"] - 3, 95), bend=-1)}
    reach = {"C": dict(hoof=(LEG_X["C"] + 2, 96)), "D": dict(hoof=(LEG_X["D"] + 2, 96)),
             "A": dict(hoof=(LEG_X["A"] - 2, 97)), "B": dict(hoof=(LEG_X["B"] - 2, 97))}
    bent = {n: dict(bend=(-1 if n in HIND else 1)) for n in "ABCD"}
    # the basic attack: lean back with the bough over her shoulder, hop forward, the swing lands, the landing
    F["attack"] = [body(P, upper(P, -45), tilt=5, pivot=MIDDLE),
                   body(P, upper(P, 0, slide=4), tilt=-10, pivot=MIDDLE, move=(1, -4), legs=hop),
                   body(P, upper(P, 90), tilt=-6, pivot=MIDDLE, move=(1, -2), legs=reach),
                   body(P, upper(P, 135, slide=-4, rest=97), tilt=-3, pivot=MIDDLE, move=(0, 1), legs=bent),
                   P.full.copy()]
    # Q: the bough spun round her - back, overhead with a small hop, swept forward (the hit), low, back
    F["skill"] = [body(P, upper(P, -90), tilt=4, pivot=MIDDLE, move=(0, 1), legs=bent),
                  body(P, upper(P, 0, slide=3), tilt=-4, pivot=MIDDLE, move=(0, -3), legs=hop),
                  body(P, upper(P, 90), tilt=-3, pivot=MIDDLE, move=(1, -2), legs=reach),
                  body(P, upper(P, 135, slide=-4, rest=95), tilt=-4, pivot=MIDDLE, move=(1, 0)),
                  body(P, upper(P, -90), tilt=3, pivot=MIDDLE),
                  P.full.copy()]
    # E: a crouch with the bough low behind, up leaning back, the throw up and forward
    F["skill2"] = [body(P, upper(P, -90), tilt=-3, pivot=MIDDLE, move=(0, 2), legs=bent),
                   body(P, upper(P, -45, slide=2), tilt=8, pivot=MIDDLE),
                   body(P, upper(P, 45, slide=3), tilt=-6, pivot=MIDDLE, move=(1, -1), legs=reach),
                   P.full.copy()]
    # W: crouch, rear up with the bough raised high, hold, slam it down in front, recover
    F["skill2_w"] = [body(P, upper(P, -90), tilt=-4, pivot=MIDDLE, move=(0, 2), legs=bent),
                     body(P, upper(P, 0, slide=5), tilt=20, pivot=HIND_HOOVES, legs=front_up(5)),
                     body(P, upper(P, 0, slide=7), tilt=28, pivot=HIND_HOOVES, legs=front_up(7, 3)),
                     body(P, upper(P, 0, slide=7), tilt=28, pivot=HIND_HOOVES, legs=front_up(7, 3)),
                     body(P, upper(P, 135, slide=-5, rest=94), tilt=-6, pivot=MIDDLE, move=(1, 1), legs=reach),
                     body(P, upper(P, 135, slide=-4, rest=95), tilt=-4, pivot=MIDDLE, legs=bent),
                     P.full.copy()]
    # R: gather, rise with the bough up, the lullaby swung over her head
    F["ult"] = [body(P, upper(P), move=(0, 1), legs=bent),
                body(P, upper(P, 0, slide=3), tilt=8, pivot=HIND_HOOVES, legs=front_up(2, 1)),
                body(P, upper(P, 45, slide=3), tilt=6, pivot=HIND_HOOVES, legs=front_up(2, 1)),
                body(P, upper(P, -45, slide=3), tilt=4, pivot=HIND_HOOVES, legs=front_up(1, 1)),
                body(P, upper(P, 45, slide=2), tilt=2, pivot=HIND_HOOVES),
                P.full.copy()]
    F["hit"] = [body(P, upper(P), tilt=6, pivot=HIND_HOOVES, legs=front_up(2, 1)), P.full.copy()]
    lie = fall(P, 80)
    F["dead"] = [body(P, upper(P), tilt=8, pivot=HIND_HOOVES, legs=front_up(2, 1)),
                 body(P, upper(P), tilt=22, pivot=HIND_HOOVES, legs=front_up(5, 2)),
                 fall(P, 45, bough_x=66.5), lie, lie.copy(), lie.copy(), lie.copy(), lie.copy()]
    return F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="folder for the review sheet and GIF")
    ap.add_argument("--tags")
    a = ap.parse_args()
    P = Parts()
    F = build(P)
    if a.tags:
        F = {t: F[t] for t in a.tags.split(",") if t in F}
    idle = P.full
    for tag, frs in F.items():
        print(tag, K.audit(frs, idle, P.D.outline, SOLES))
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

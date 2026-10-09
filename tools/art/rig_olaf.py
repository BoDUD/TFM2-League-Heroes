#!/usr/bin/env python3
"""Olaf's action strips posed from the approved design's own parts (2026-10-09): the casting body = the idle's.

    python tools/art/rig_olaf.py [--check] [--review DIR] [--run trot|cross] [--no-write]

Codex's step-2 delivery (assets/source/olaf/codex_strips/, its own HANDOFF: 「待视觉修正」) pasted the design's head on
bodies it drew anew: the run 55-62 rows tall (the design 42), the other casts with boots 1.3-1.7 and bare arms 1.5-3.4
times the design's (work/ol/body_scale.py), the legs not the design's, and a strip of the head piece's shoulder fur
beside every pasted head. The user: 「好的留，坏的我来修」, then 「认真修复 修复到完美版了喊我review」. So, as for Zed
(rig_zed.py), every frame is the design with only what the action moves moved; Codex's frames and League's clips
(tools/lol/native_pose.py) are the pose references:
- the BODY is the design without its two arms, the torso they hid painted in the design's own materials (BODY: the
  leather vest, the studded steel belt and its buckle, the waist); head, beard, fur, loincloth and legs are the
  design's squares;
- an arm that keeps the idle's pose is the design's own arm (its squares, moved only with the body); an arm that moves
  is drawn along shoulder -> elbow -> hand (rigkit.bone_arm: the upper arm in the design's three skin shades, the
  forearm in the leather wrap's (near) or the steel bracer's (far), one outline ring), the design's fist at the hand
  and the near axe - the design's head with a straight handle, gripped by the fist - in exact quarter turns or
  mirrors only (no-deformation rule: nothing resampled);
- whole-body moves: a lean (the upper body moved over the legs), a crouch (the upper body sunk over the boots,
  layering), a hop (the whole figure), the lower legs swung about the knee row (rigkit.swing_leg: whole rows);
- the death falls on his back (League's): struck, staggering with the axes thrown up, sinking, then the whole figure
  turned exactly a quarter counter-clockwise (head to the left, face up) onto the ground;
- the run (League's pace, 8 x 120 ms): the lower legs alternate (TROT: in place; CROSS: brought in under the body so
  the boots pass), the body dropping a row at each contact, both arms swaying with the stride as rigid units.
Writes assets/source/native/olaf_<tag>.png (8x, 112x96 cells, soles on cell row 81) and olaf_cells.json; then
tools/art/import_native.py. --check compares instead of writing; --review writes review sheets and a GIF.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_olaf as DO  # noqa: E402
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
FINAL = os.path.join(ROOT, "assets", "source", "olaf", "design", "olaf_design_42.txt")
POSES_JSON = os.path.join(ROOT, "assets", "source", "olaf", "poses.json")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
CELL = (112, 96)
CELL_PIVOT = (56, 70)            # the soles on cell row 81 (the references' feet line)
C = {k: DO.hx(v) for k, v in DO.PAL.items()}
OUT = C["0"]
SKIN = (C["S"], C["K"], C["k"])
WRAP = (C["n"], C["B"], C["b"])
BRACER = (C["h"], C["G"], C["g"])
STEEL = set("dgGhwW")
ORANGE = set("rRoO")
WAIST = 88                       # the upper body: rows up to here (and the loincloth); the legs below
L_LEG, R_LEG = (45, 60), (69, 83)
KNEE_ROW, FEET_ROW = 88, 96      # swing_leg: the greaves (89-95) turn about the knee row, the boots (96-99) move whole
N_SHOULDER, F_SHOULDER = (52.5, 76.5), (77.0, 79.0)
N_UPPER, N_FORE = 6.0, 5.5       # bone lengths (the idle's arm: shoulder row 74, elbow ~80, hand ~85)
F_UPPER, F_FORE = 5.0, 5.0
N_WIDTH, F_WIDTH = (7.0, 6.0), (5.0, 4.0)

# the torso the arms hid: (row, first column, letters; '.' keeps, ' ' clears)
BODY = [
    (75, 46, "   "),
    (75, 56, "0b"),
    (76, 55, "0bb"),
    (77, 55, "0bb"),
    (78, 54, "0bBb"),
    (79, 54, "0rRbbBBBBBbbb0"),
    (80, 54, "0nBBBBBBBbbbb0"),
    (81, 54, "0nBBBBBBbbbbbb0"),
    (82, 54, "0nBBnBBbbbbbbb0"),
    (83, 54, "0000000000000000"),
    (84, 54, "0hhhhhhh0hwwhh00"),
    (85, 54, "0GWGGGWG0hGGGGg0"),
    (86, 54, "0GGGGGGG0hGWGGg0"),
    (87, 54, "0ggggggg0GGGGgg0"),
    (88, 62, "0gg"),
    (78, 80, "  "),
    (79, 74, "0bBn0"),
    (80, 74, "0bBn0"),
    (81, 74, "bbBn0"),
    (82, 74, "bBBn0"),
    (83, 74, "00000"),
    (84, 74, "hhhh0"),
    (85, 74, "GGWG0"),
    (86, 74, "GGGG0"),
    (87, 74, "gggg0"),
    (88, 74, "0000"),
]
FAR_FIST = ["0000", "0SK0", "0Kk0", "0000"]


# ------------------------------------------------------------------------------------------------ the design's parts
def grid():
    rows = [r.rstrip("\r\n") for r in open(K.lp(FINAL), encoding="utf-8") if not r.startswith("#")]
    return {(y + 58, x + 45): c for y, r in enumerate(rows) for x, c in enumerate(r) if c != "."}


def to_rgba(g):
    a = np.zeros((128, 128, 4), np.uint8)
    for (y, x), c in g.items():
        a[y, x, :3] = C[c]
        a[y, x, 3] = 255
    return a


def near_arm_keys(g):
    m = set()
    for (y, x), c in g.items():
        if 74 <= y <= 78 and 45 <= x <= 56 and not (y == 75 and x <= 48 and c in "Www"):
            m.add((y, x))                                  # the shoulder's skin and the bicep under the fur
        elif 79 <= y <= 82 and 45 <= x <= 53:
            m.add((y, x))                                  # the leather wrap
        elif 83 <= y <= 88 and 45 <= x <= 54:
            m.add((y, x))                                  # the fist, the handle's end cap
        elif (y, x) in {(85, 55), (86, 56), (81, 55), (81, 56), (82, 54), (82, 55)}:
            m.add((y, x))                                  # the fist's knuckle, the handle, the head's spike
        elif 79 <= y <= 87 and 60 <= x <= 68 and c in STEEL:
            m.add((y, x))                                  # the axe head
        elif 79 <= y <= 87 and 61 <= x <= 68 and c == "0":
            m.add((y, x))
    return m


def far_arm_keys(g):
    return {(y, x) for (y, x), c in g.items()
            if 79 <= y <= 88 and 74 <= x <= 84 and c not in ORANGE and not (y == 88 and x <= 76)}


def ring(a):
    """One outline ring round a's opaque squares (4-neighbours), on clear squares."""
    m = a[..., 3] > 0
    r = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        r |= np.roll(np.roll(m, dy, 0), dx, 1)
    r &= ~m
    out = a.copy()
    out[r, :3] = OUT
    out[r, 3] = 255
    return out


class Parts:
    def __init__(self):
        g = grid()
        self.g = g
        self.design = to_rgba(g)
        nk, fk = near_arm_keys(g), far_arm_keys(g)
        self.near = to_rgba({k: g[k] for k in nk})
        self.far = to_rgba({k: g[k] for k in fk})
        body = {k: v for k, v in g.items() if k not in nk and k not in fk}
        for y, x0, text in BODY:
            for i, ch in enumerate(text):
                if ch == " ":
                    body.pop((y, x0 + i), None)
                elif ch != ".":
                    body[(y, x0 + i)] = ch
        self.body = to_rgba(body)
        # the head and the beard over a near arm crossing the body: the face (rows 69-75, columns 60-78) and the
        # beard's orange squares (rows 76-88, columns 60-75), with the outline squares that ring them
        bd = {k: c for k, c in body.items() if (76 <= k[0] <= 88 and 60 <= k[1] <= 75 and c in ORANGE)
              or (69 <= k[0] <= 75 and 60 <= k[1] <= 78 and c != "0")}
        self.beard = ring(to_rgba(bd))
        R, Cc = np.mgrid[0:128, 0:128]
        op = self.design[..., 3] > 0
        self.lleg = op & (R > WAIST) & (Cc >= L_LEG[0]) & (Cc <= L_LEG[1])
        self.rleg = op & (R > WAIST) & (Cc >= R_LEG[0]) & (Cc <= R_LEG[1])
        # the near fist: the design's skin squares of rows 83-87, columns 47-55, with an outline ring
        f = to_rgba({k: c for k, c in g.items() if 83 <= k[0] <= 87 and 47 <= k[1] <= 55 and c in "SKk"})
        self.fist_n = K.Part.from_canvas(ring(f), ring(f)[..., 3] > 0, (51.5, 85.5))
        ff = np.zeros((128, 128, 4), np.uint8)
        for y, row in enumerate(FAR_FIST):
            for x, ch in enumerate(row):
                if ch != " ":
                    ff[60 + y, 60 + x, :3] = C[ch]
                    ff[60 + y, 60 + x, 3] = 255
        self.fist_f = K.Part.from_canvas(ff, ff[..., 3] > 0, (62.0, 62.0))
        # the near axe: the design's head (rows 79-87, columns 60-69 steel) with a straight handle on row 86 from an end
        # cap at columns 45-46 to the head; the grip (the fist's middle) on column 51
        ax = to_rgba({k: c for k, c in g.items() if 79 <= k[0] <= 87 and 60 <= k[1] <= 69 and c in STEEL})
        for x in range(47, 61):
            if not ax[86, x, 3]:
                ax[86, x, :3] = C["B"]
                ax[86, x, 3] = 255
        ax[85:88, 45:47, :3] = C["b"]
        ax[85:88, 45:47, 3] = 255
        ax = ring(ax)
        self.axe = K.Part.from_canvas(ax, ax[..., 3] > 0, (51.5, 86.5))

    def axe_turned(self, how):
        """how: 'fwd' (as drawn: the handle forward, the head up), 'down' (the handle down, the blade forward), 'up'
        (the handle up, the blade back), 'up_f' (the handle up, the blade forward), 'chop' (the handle forward, the
        blade down), 'back' (the handle back, the blade down), 'back_up' (the handle back, the head up)."""
        a = self.axe
        return {"fwd": a, "down": K.rot90(a, 1), "up": K.rot90(a, 3), "up_f": K.rot90(a, 3).flip_h(),
                "chop": a.flip_v(), "back": K.rot90(a, 2), "back_up": a.flip_h()}[how]


# ------------------------------------------------------------------------------------------------ one frame
def arm_layer(P, side, spec):
    """A drawn arm (upper-body coordinates): spec = dict(hand=(x, y), axe=how or None, bend=+1/-1)."""
    layer = np.zeros((128, 128, 4), np.uint8)
    sh = N_SHOULDER if side == "n" else F_SHOULDER
    up, fo = (N_UPPER, N_FORE) if side == "n" else (F_UPPER, F_FORE)
    if spec.get("reach"):
        up, fo = spec["reach"]
    hand = spec["hand"]
    elb, hand = K.elbow(sh, hand, up, fo, spec.get("bend", 1))
    if spec.get("axe"):
        K.place(layer, P.axe_turned(spec["axe"]), hand)
    mats = {"upper": [(0, 1, SKIN)],
            "fore": [(0, 0.8, WRAP), (0.8, 1, SKIN)] if side == "n" else [(0, 0.45, SKIN), (0.45, 1, BRACER)]}
    K.bone_arm(layer, sh, elb, hand, mats, width=N_WIDTH if side == "n" else F_WIDTH, outline=OUT)
    K.place(layer, P.fist_n if side == "n" else P.fist_f, hand)
    return layer


def build(P, f):
    """f: dx / dy (the whole figure), lean (the upper body's columns), sink (its rows: a crouch over the legs),
    legs ((dx, lift) image-left, image-right), near / far (None: the design's arm; a dict: a drawn arm), far_front."""
    f = f or {}
    upper = P.body.copy()
    upper[P.lleg | P.rleg] = 0
    near, far = f.get("near"), f.get("far")
    if far is None:
        K.put(upper, P.far, 0, 0)
    else:
        lay = arm_layer(P, "f", far)
        K.put(upper, lay, 0, 0, under=not f.get("far_front"))
    if near is None:
        K.put(upper, P.near, 0, 0)
    else:
        K.put(upper, arm_layer(P, "n", near), 0, 0)
        if near["hand"][0] > 58 and not near.get("front"):   # across the body: behind the beard (stays readable)
            K.put(upper, P.beard, 0, 0)
    legs = np.zeros_like(upper)
    (lx, ll), (rx, rl) = f.get("legs", ((0, 0), (0, 0)))
    K.put(legs, K.swing_leg(P.design, P.rleg, KNEE_ROW, FEET_ROW, rx, rl), 0, 0)
    K.put(legs, K.swing_leg(P.design, P.lleg, KNEE_ROW, FEET_ROW, lx, ll), 0, 0)
    c = K.put(legs, K.shifted(upper, f.get("lean", 0), f.get("sink", 0)), 0, 0)
    if f.get("dx") or f.get("dy"):
        c = K.shifted(c, f.get("dx", 0), f.get("dy", 0))
    c[SOLES + 1:] = 0
    return c


def finish_near(a, ref):
    """rigkit.finish, kept to the squares within 2 of a change from `ref` (the rest stays the design's)."""
    changed = (a != ref).any(-1)
    near = changed.copy()
    for _ in range(2):
        g = near.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                g |= np.roll(np.roll(near, dy, 0), dx, 1)
        near = g
    out = K.finish(a, OUT, SOLES, keep=~near, pinholes=4)
    out[~near] = a[~near]
    return out


def frame(P, f):
    if f is None:
        return P.design.copy()
    c = build(P, f)
    ref = K.shifted(P.design, f.get("dx", 0) + f.get("lean", 0), f.get("dy", 0))
    return finish_near(c, ref)


# ------------------------------------------------------------------------------------------------ the actions
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
NA = dict(hand=(51.5, 85.5), axe="fwd")          # the near arm drawn where the design's hangs
FA = dict(hand=(80.5, 86.5))                     # the far arm likewise (its axe: the design's, see build)
POSES = {
    # the basic attack with the far (image-right) arm (League's Olaf alternates hands; the near arm would cross the whole
    # body and hide behind the beard): the axe raised behind the head, at the top of the swing, chopped down in front
    # (frame 4: the hit), followed through low, back to the idle stance
    "attack": [dict(lean=-1, far=dict(hand=(84.5, 72.5), axe="up", bend=-1)),
               dict(lean=-2, far=dict(hand=(81.5, 61.5), axe="up", bend=-1)),
               dict(far=dict(hand=(86.5, 62.5), axe="up_f", bend=-1, reach=(6.0, 6.0))),
               dict(lean=3, sink=1, far=dict(hand=(93.5, 72.5), axe="down", bend=1, reach=(8.0, 8.0)), far_front=True),
               dict(lean=2, sink=1, far=dict(hand=(91.5, 79.5), axe="down", bend=1, reach=(7.5, 7.5)), far_front=True),
               None],
    # Undertow: thrown with the far (image-right) arm - the near one would cross the whole body and hide behind the
    # beard: the axe raised behind the head, cocked, hurled forward to the right with a lunge (frame 4: it leaves; the
    # hand empty from then on)
    "skill": [dict(far=dict(hand=(84.5, 70.5), axe="up", bend=-1)),
              dict(lean=-1, far=dict(hand=(82.5, 61.5), axe="up", bend=-1)),
              dict(lean=-2, far=dict(hand=(85.5, 63.5), axe="up", bend=-1, reach=(6.0, 6.0))),
              dict(lean=3, sink=2, legs=((-3, 0), (3, 0)),
                   far=dict(hand=(96.5, 76.5), axe=None, bend=1, reach=(8.0, 8.0)), far_front=True),
              dict(lean=2, sink=2, legs=((-3, 0), (3, 0)),
                   far=dict(hand=(92.5, 84.5), axe=None, bend=1, reach=(7.5, 7.5)), far_front=True),
              dict(far=dict(hand=(80.5, 86.5), axe=None))],
    # Reckless Swing: a crouch, the leap with both axes up, the top, the two-handed slam in front (frame 4: the blades
    # down at waist height), crouched after the blow, rising
    "skill2": [dict(sink=2),
               dict(dy=-2, near=dict(hand=(50.5, 64.5), axe="up", bend=1), far=dict(hand=(74.5, 66.5), axe="up_f"),
                    legs=((1, 1), (-1, 1))),
               dict(dy=-3, near=dict(hand=(55.5, 60.5), axe="up_f", bend=1), far=dict(hand=(70.5, 61.5), axe="up_f"),
                    legs=((1, 2), (-1, 2))),
               dict(lean=3, sink=2, near=dict(hand=(72.5, 84.5), axe="chop", bend=-1, reach=(8.5, 8.0)),
                    far=dict(hand=(82.5, 86.5), axe="chop", bend=-1, reach=(6.0, 6.0))),
               dict(lean=2, sink=3, near=dict(hand=(70.5, 87.5), axe="chop", bend=-1, reach=(8.5, 8.0)),
                    far=dict(hand=(80.5, 89.5), axe="chop", bend=-1, reach=(6.0, 6.0))),
               dict(sink=1)],
    # Ragnarok: gathering (a crouch), both axes lifted to the shoulders, the roar with both axes high (frame 3), held
    # (the axes shaking a square), lowered
    "ult": [dict(sink=1),
            dict(near=dict(hand=(46.5, 73.5), axe="up_f", bend=1), far=dict(hand=(84.5, 74.5), axe="up", bend=-1)),
            dict(lean=-1, dy=-1, near=dict(hand=(48.5, 62.5), axe="up_f", bend=1),
                 far=dict(hand=(81.5, 62.5), axe="up", bend=-1)),
            dict(lean=-1, dy=-1, near=dict(hand=(48.5, 61.5), axe="up_f", bend=1),
                 far=dict(hand=(81.5, 63.5), axe="up", bend=-1)),
            dict(lean=-1, dy=-1, near=dict(hand=(49.5, 62.5), axe="up_f", bend=1),
                 far=dict(hand=(80.5, 62.5), axe="up", bend=-1)),
            dict(near=dict(hand=(49.5, 72.5), axe="up_f", bend=1), far=dict(hand=(80.5, 73.5), axe="up", bend=-1))],
    # hit: jolted back (the whole figure 2 columns left, the upper body a column more), the near arm thrown up
    "hit": [dict(dx=-2, lean=-1, near=dict(hand=(45.5, 73.5), axe="up", bend=1)), dict(dx=-1)],
}


CODEX = os.path.join(ROOT, "assets", "source", "olaf", "codex_strips")


HEAD_ROWS, HEAD_COLS = (58, 75), (57, 79)       # the head piece Codex pasted (work/ol/head_ol.py)


def head_piece(d):
    """The head piece's mask on the canvas: rows 58-75, columns 57-79, its largest 8-connected piece."""
    from collections import deque
    op = d[..., 3] > 0
    m = np.zeros(op.shape, bool)
    m[HEAD_ROWS[0]:HEAD_ROWS[1] + 1, HEAD_COLS[0]:HEAD_COLS[1] + 1] =         op[HEAD_ROWS[0]:HEAD_ROWS[1] + 1, HEAD_COLS[0]:HEAD_COLS[1] + 1]
    seen, best = np.zeros_like(m), []
    for sy, sx in zip(*np.nonzero(m)):
        if seen[sy, sx]:
            continue
        q, pts = deque([(sy, sx)]), []
        seen[sy, sx] = True
        while q:
            y, x = q.popleft()
            pts.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    v, u = y + dy, x + dx
                    if 0 <= v < 128 and 0 <= u < 128 and m[v, u] and not seen[v, u]:
                        seen[v, u] = True
                        q.append((v, u))
        if len(pts) > len(best):
            best = pts
    out = np.zeros_like(m)
    out[tuple(np.array(best).T)] = True
    return out


def codex_frame(tag, i, P=None):
    """Codex's frame i of `tag` on a 128 x 128 canvas (its cell's standing point on PIVOT). With P: the shoulder fur
    that came with the pasted head piece (light squares at its lower left - a light patch beside the head) is given to
    the square next to it on the body's side or cleared, and the frame finished (crumbs, stray outline squares)."""
    cells = json.load(open(K.lp(os.path.join(CODEX, "olaf_cells.json")), encoding="utf-8"))
    man = json.load(open(K.lp(os.path.join(CODEX, "manifest.json")), encoding="utf-8"))
    a = np.asarray(Image.open(K.lp(os.path.join(CODEX, f"olaf_{tag}_1x.png"))).convert("RGBA"))
    mf = man["animations"][tag]["frames"][i]
    X, Y, w, h = mf["cell_rect"]
    cell = a[Y:Y + h, X:X + w].copy()
    if P is not None:
        hm = head_piece(P.design)
        ys, xs = np.nonzero(hm)
        y0, x0, H = ys.min(), xs.min(), ys.max() - ys.min() + 1
        # the shoulder fur in the piece: its light and grey squares in columns 57-60, rows 70-75
        fur = [(y - y0, x - x0) for y, x in zip(ys, xs)
               if 57 <= x <= 60 and 70 <= y <= 75 and P.g.get((y, x)) in ("w", "W", "h", "G", "g")]
        hx, hy = mf["head_top_left"]
        rot = mf["head_rotation_deg"]
        for dy, dx in fur:
            if rot == 90:                    # turned a quarter clockwise: (row, col) -> (col, H - 1 - row)
                yy, xx, ny, nx = hy + dx, hx + H - 1 - dy, 1, 0
            else:
                yy, xx, ny, nx = hy + dy, hx + dx, 0, -1
            nb = cell[yy + ny, xx + nx] if 0 <= yy + ny < h and 0 <= xx + nx < w else np.zeros(4, np.uint8)
            cell[yy, xx] = nb if nb[3] else 0
    px, py = cells["tags"][tag][i]["pivot"]
    c = np.zeros((128, 128, 4), np.uint8)
    K.put(c, cell, PIVOT[0] - px, PIVOT[1] - py)
    c[SOLES + 1:] = 0
    if P is not None:
        c = K.finish(c, OUT, SOLES, keep=None, pinholes=2)
    return c


def dead(P, k):
    """Struck (the axes thrown up), staggering forward, sinking to his knees with the arms hanging (the rig: the upper
    body sunk over the legs), then lying - Codex's drawing of him fallen forward (frames 6-8; a lying body is drawn,
    not posed: feedback-legs-like-idle)."""
    steps = [dict(dx=-1, lean=-1, near=dict(hand=(46.5, 72.5), axe="up", bend=1), far=dict(hand=(84.5, 74.5), axe="up")),
             dict(lean=1),
             dict(lean=2, sink=3),
             dict(lean=3, sink=5),
             dict(lean=4, sink=7)]
    if k < len(steps):
        return frame(P, steps[k])
    return codex_frame("dead", k, P)


# the run (League's pace: Olaf_Run cycles in 0.968 s -> 8 x 120 ms). His boots stand 26 columns apart (a wide
# brawler's stance, wider than Rengar's - the user took a trot there: 「不对选A 不用交叉步」), so TROT: each lower leg
# planted ahead, sliding back under the body, then lifted and carried forward (the other half a cycle later), the
# body dipping a row as a boot lands, both arms swinging opposite the legs as rigid units. CROSS: the lower legs
# brought in and swung (kept for comparison).
STEP = [(3, 0), (1, 0), (-1, 0), (-3, 0), (-2, 2), (0, 3), (2, 2), (3, 0)]      # (columns, lift) of one boot
DROP = [1, 0, 0, 0, 1, 0, 0, 0]
SWAY = [2, 1, 0, -1, -2, -1, 0, 1]
STRIDE = [4, 3, 0, -3, -4, -3, 0, 3]
R_LIFT = [0, 0, 0, 0, 0, 2, 3, 2]
L_LIFT = [0, 2, 3, 2, 0, 0, 0, 0]
RUN = {"trot": dict(scale=1.0), "cross": dict(l_in=6, r_in=-6, stride=2.0)}
RUN_VARIANT = "trot"


def run_frames(P, variant=None):
    name = variant or RUN_VARIANT
    v = RUN[name]
    out = []
    for k in range(8):
        legs = np.zeros_like(P.design)
        if name == "trot":
            (lx, ll), (rx, rl) = STEP[k], STEP[(k + 4) % 8]
            lx, rx = int(round(lx * v["scale"])), int(round(rx * v["scale"]))
        else:
            st = int(round(STRIDE[k] * v["stride"]))
            (lx, ll), (rx, rl) = (v["l_in"] + st, L_LIFT[k]), (v["r_in"] - st, R_LIFT[k])
        K.put(legs, K.swing_leg(P.design, P.rleg, KNEE_ROW, FEET_ROW, rx, rl), 0, 0)
        K.put(legs, K.swing_leg(P.design, P.lleg, KNEE_ROW, FEET_ROW, lx, ll), 0, 0)
        upper = P.body.copy()
        upper[P.lleg | P.rleg] = 0
        K.put(upper, K.shifted(P.far, -SWAY[k] // 2, 0), 0, 0, under=True)
        K.put(upper, K.shifted(P.near, SWAY[k], 0), 0, 0)
        c = K.put(legs, K.shifted(upper, 1, DROP[k]), 0, 0)      # leaning a column into the run
        c[SOLES + 1:] = 0
        keep = np.zeros((128, 128), bool)
        keep[:72] = True
        out.append(K.finish(c, OUT, SOLES, keep=keep, pinholes=4))
    return out


# the idle breathes here (as league_zed's): the shared idle_breathe cuts a row through his spiked greaves, so the whole
# figure but the boots sinks 0 0 1 2 2 2 1 0 rows over the boots (layering), the axes with it, rigid; the base game's
# pace (8 x 140 ms); import_native skips him (BREATHE_SKIP)
BREATH = [0, 0, 1, 2, 2, 2, 1, 0]


def breath(P, n):
    if n == 0:
        return P.design.copy()
    R = np.arange(128)[:, None]
    boots = (P.lleg | P.rleg) & (R >= FEET_ROW)
    feet = np.zeros_like(P.design)
    feet[boots] = P.design[boots]
    top = P.design.copy()
    top[boots] = 0
    c = K.put(feet, K.shifted(top, 0, n), 0, 0)
    c[SOLES + 1:] = 0
    return c


def frames(P, tag, run=None):
    if tag == "idle":
        return [breath(P, n) for n in BREATH]
    if tag == "run":
        return run_frames(P, run)
    if tag == "dead":
        return [dead(P, k) for k in range(8)]
    return [frame(P, f) for f in POSES[tag]]


def ms_of(tag):
    if tag == "idle":
        return [140] * len(BREATH)
    spec = json.load(open(K.lp(POSES_JSON), encoding="utf-8"))
    return [m for _, m in spec["tags"][tag]["frames"]]


def build_all(run=None):
    P = Parts()
    built = {tag: frames(P, tag, run) for tag in TAGS}
    return P.design, built, {tag: ms_of(tag) for tag in TAGS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write review sheets and a GIF into this folder")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--run", choices=sorted(RUN), help="the run variant (default RUN_VARIANT)")
    a = ap.parse_args()
    d, built, ms = build_all(a.run)
    for tag in TAGS:
        rows = K.audit(built[tag], d, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}" for r in rows))
    if not a.no_write:
        # the strips are fix_olaf_strips.py's since 2026-10-09 (Codex's League-driven redraw): this rig only reviews
        raise SystemExit("rig_olaf.py no longer writes the strips (the user rejected them: 「身体太奇怪了吧」) - "
                         "run tools/art/fix_olaf_strips.py; use --no-write --review here")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "olaf_strips_review.png"), z=4,
                       soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], ms, os.path.join(a.review, "olaf_strips_review.gif"), z=4)


if __name__ == "__main__":
    main()

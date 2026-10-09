#!/usr/bin/env python3
"""Kog'Maw's action strips posed from the approved design's own parts (2026-10-09): the casting body = the idle's.

    python tools/art/rig_kogmaw.py [--check] [--review DIR] [--parts PNG] [--no-write]

Codex's step-2 delivery (assets/source/kogmaw/codex_strips/) pasted the design's head on bodies it drew anew: the
shell turned into one tall fin, the bone spikes, the belly and the feet changed, R's upright frames in another style
(a long teal trunk, stick arms, sideways antennae), the spit tubes a speckle of five crimson shades; its own HANDOFF
listed the feet, the body, the tube lengths and R's timing as not done. The user: 「有问题的地方帮我修复」. So, as for
Rengar (rig_rengar.py) and Vladimir, every frame is the design with only what the action moves moved, nothing
resampled (the no-deformation rule: translation, quarter turns, whole-row shifts, layering):
- the parts are cut square for square with the outline squares that ring them alone: the two FEET (rows 95-99, the far
  one at the image left, the near one at the right), the TAIL (the bony tail from the hip up to its tip at the image
  left), and the HEAD (the four antennae, the skull plate, the eyes: work/km/head_km.py's ranges); the shell, the belly,
  the mouth and the fore-claws are the body;
- the spit TUBE is the one new drawing (the design has no tube): a straight fleshy tube in the mouth's own crimson
  shades (a lit top row, two mid rows, a shadow row, one outline ring), a ring groove with a bone spike above and below
  every four squares, and an open end - a rim with fang squares round the dark throat. It leaves the middle of the
  mouth; its length per frame is in POSES;
- whole-figure moves only: a lunge / recoil (columns), a hop (rows, the feet with it); the body never sinks over the
  feet or stretches its legs in an action (the user, 2026-10-09: 「攻击和放技能的时候模型有点变形 身体压到腿了」,
  「移动的时候也是」 - the first version crouched by sinking the body behind the feet and rose by repeating the legs' row);
- R stands up: the figure without the feet and the tail, with the tube already out of the mouth, turned exactly a
  quarter counter-clockwise (the tube straight up, the face up, the belly to the right, the antennae swept back to the
  left) and stood on the design's own feet; the tail lies on the ground behind him;
- the death: struck back, then the body sinks over the feet until it lies flat on the ground (the rows under the soles
  cut), the eyes closed (each eye's squares the skull's bone, one dark lid row); the void form that leaves the body is
  an effect (step 3);
- the run (League's pace, 8 x 89 ms): a waddle - the two feet step in turn (the swinging foot lifted a row and carried
  forward, the planted one sliding back), the whole figure hopping a row while a foot passes, the tail and the
  antennae swaying;
- the idle: the antennae and the tail sway a column, a beat apart (no breathing sink - it pressed the body on the feet);
  import_native skips him (BREATHE_SKIP).
Writes assets/source/native/kogmaw_<tag>.png (8x, 96x80 cells, the soles on cell row 65) and kogmaw_cells.json; then
tools/art/import_native.py. --check compares instead of writing; --review writes a review sheet and a GIF.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import design_kogmaw as DK  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "kogmaw_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
L = DK.RGB                       # the design's letters -> RGB
OUT = L["0"]
CELL = (96, 80)
CELL_PIVOT = (46, 54)            # the soles on cell row 65 (the references' feet line)
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)

FEET_ROW = 95                    # the feet: rows 95-99
MID = 64                         # the far foot left of this column, the near foot from it
# the head piece: per row (first, last) column on the design canvas (= work/km/head_km.py)
HEAD = {**{y: (55, 90) for y in range(62, 73)}, **{y: (62, 90) for y in range(73, 82)}}
# the tail: per row (first, last) column - the bony tail from its tip (rows 82-89) to where it leaves the hip (90-91)
TAIL = {82: (43, 47), 83: (43, 48), 84: (43, 49), 85: (44, 50), 86: (45, 50), 87: (46, 49), 88: (46, 49),
        89: (47, 50), 90: (48, 55), 91: (49, 55)}
TAIL_ROOT_ROW = 91
ANTENNA_ROWS = (62, 68)          # rows that hold only the antennae (above the short right one): rows shifted sway them
MOUTH = (73.5, 87.5)             # the middle of the open mouth: where the tube leaves


def design():
    a = np.asarray(Image.open(K.lp(DESIGN)).convert("RGBA"))
    a = (a if a.shape[0] == 128 else a[Z // 2::Z, Z // 2::Z]).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def region(rows_cols):
    m = np.zeros((128, 128), bool)
    for y, (c0, c1) in rows_cols.items():
        m[y, c0:c1 + 1] = True
    return m


def rgba(ch):
    return np.array(list(L[ch]) + [255], np.uint8)


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        op = d[..., 3] > 0
        ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
        colour = op & ~ink
        R, C = np.mgrid[0:128, 0:128]
        bone = np.isin(self._letters(d), list("abcd"))
        lfoot_c = colour & (R >= FEET_ROW) & (C < MID)
        rfoot_c = colour & (R >= FEET_ROW) & (C >= MID)
        tail_c = colour & region(TAIL) & bone
        head_c = colour & region(HEAD)
        parts_c = {"lfoot": lfoot_c, "rfoot": rfoot_c, "tail": tail_c, "head": head_c}
        taken = np.zeros((128, 128), bool)
        for k, m in parts_c.items():
            assert not (m & taken).any(), k
            taken |= m
        body_c = colour & ~taken

        def ring(c, others):
            """The outline squares round c that no square of `others` touches (4-neighbours)."""
            m = np.zeros_like(c)
            for y, x in zip(*np.nonzero(ink)):
                if any(c[y + a, x + b] for a, b in N8) and not any(others[y + a, x + b] for a, b in N4):
                    m[y, x] = True
            return m

        self.masks = {}
        for k, c in parts_c.items():
            others = body_c | (taken & ~c)
            self.masks[k] = c | ring(c, others)
        self.feet = self.masks["lfoot"] | self.masks["rfoot"]
        self.body = d.copy()                      # the design without the feet and the tail
        self.body[self.feet | self.masks["tail"]] = 0
        self.letters = self._letters(d)

    @staticmethod
    def _letters(d):
        inv = {v: k for k, v in L.items()}
        out = np.full((128, 128), " ", "U1")
        for y, x in zip(*np.nonzero(d[..., 3] > 0)):
            out[y, x] = inv[tuple(int(v) for v in d[y, x, :3])]
        return out

    def overlay(self, path, z=12):
        """The design with every part tinted (feet cyan / magenta, tail yellow, head blue)."""
        d = self.design.astype(float)
        tint = {"lfoot": (0, 220, 255), "rfoot": (255, 0, 255), "tail": (255, 220, 0), "head": (60, 90, 255)}
        out = d.copy()
        for k, col in tint.items():
            m = self.masks[k]
            out[m, :3] = d[m, :3] * 0.45 + np.array(col) * 0.55
        sub = out[58:101, 40:90].astype(np.uint8)
        Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST).save(path)


# ------------------------------------------------------------------------------------------------ the tube
def tube(n):
    """The spit tube pointing right, n squares of shaft before its open end: 8 rows (a spike row, the outline, the
    lit row s, two mid rows R, the shadow row r, the outline, a spike row), joint = the left end's middle."""
    w = n + 3
    g = np.full((8, w), " ", "U1")
    shaft = ["0", "s", "R", "R", "r", "0"]
    groove = ["b", "R", "r", "r", "q", "b"]          # a ring: darker band, a bone spike over and under it
    for x in range(n):
        ring = x >= 2 and (n - x) % 4 == 2
        for k, ch in enumerate(groove if ring else shaft):
            g[1 + k, x] = ch
        if ring:
            g[0, x] = "0"
            g[7, x] = "0"
    end = [["0", "c", "s", "q", "q", "r", "c", "0"],      # the rim: fangs at the top and the bottom, the dark throat
           [" ", "0", "c", "q", "q", "c", "0", " "],
           [" ", " ", "0", "0", "0", "0", " ", " "]]
    for i, col in enumerate(end):
        for k, ch in enumerate(col):
            g[k, n + i] = ch
    s = np.zeros((8, w, 4), np.uint8)
    for y in range(8):
        for x in range(w):
            if g[y, x] != " ":
                s[y, x] = rgba(g[y, x])
    return K.Part(s, (0.0, 4.0))


def with_tube(c, n, dx=0):
    """The tube put over the mouth (its left end inside the open mouth), the figure moved dx."""
    if n:
        K.place(c, tube(n), (MOUTH[0] + dx, MOUTH[1]))
    return c


# ------------------------------------------------------------------------------------------------ the frame
def finish_near(a, ref, pinholes=4):
    """rigkit.finish, but every square more than 2 from a square that differs from `ref` keeps ref's (the design's own
    gaps stay open, the untouched body stays the design's square for square)."""
    changed = (a != ref).any(-1)
    near = changed.copy()
    for _ in range(2):
        g = near.copy()
        for dy, dx in N8:
            g |= np.roll(np.roll(near, dy, 0), dx, 1)
        near = g
    out = K.finish(a, OUT, SOLES, keep=~near, pinholes=pinholes)
    out[~near] = a[~near]
    return out


def sway_rows(a, r0, r1, dx):
    """Rows r0..r1 of `a` moved dx columns (whole rows: the antennae swaying)."""
    if not dx:
        return a
    out = a.copy()
    out[r0:r1 + 1] = 0
    seg = a[r0:r1 + 1]
    out[r0:r1 + 1] = K.shifted(np.pad(seg, ((0, 128 - seg.shape[0]), (0, 0), (0, 0))), dx, 0)[:seg.shape[0]]
    return out


def tail_part(P, dx=0, dy=0):
    """The tail, its tip swung dx columns (the root fixed: each row moved in proportion to its height over the root)."""
    out = np.zeros_like(P.design)
    m = P.masks["tail"]
    top = min(TAIL)
    for r, c in zip(*np.nonzero(m)):
        sh = int(np.floor(dx * (TAIL_ROOT_ROW - r) / (TAIL_ROOT_ROW - top) + 0.5))
        if 0 <= c + sh < 128 and 0 <= r + dy < 128:
            out[r + dy, c + sh] = P.design[r, c]
    return out


def feet_part(P, l=(0, 0), r=(0, 0)):
    """The two feet: each (dx, lift); the near (image-right) one drawn over the far one."""
    out = np.zeros_like(P.design)
    for m, (dx, lift) in ((P.masks["lfoot"], l), (P.masks["rfoot"], r)):
        f = np.zeros_like(P.design)
        f[m] = P.design[m]
        K.put(out, K.shifted(f, dx, -lift), 0, 0)
    return out


def build(P, f):
    """One frame from a pose dict: sink / rise (rows: the body over the feet - only the death uses them now: the user,
    「攻击和放技能的时候模型有点变形 身体压到腿了」「移动的时候也是」), dx / hop (the whole figure, feet included), tube (squares),
    tail (the tip's columns), ant (the antennae's columns), feet ((dx, lift) far, (dx, lift) near), closed (eyes)."""
    top = P.body.copy()
    if f.get("closed"):
        top = closed_eyes(P, top)
    top = sway_rows(top, ANTENNA_ROWS[0], ANTENNA_ROWS[1], f.get("ant", 0))
    top = K.put(top, tail_part(P, f.get("tail", 0)), 0, 0, under=True)
    with_tube(top, f.get("tube", 0))
    sink, rise = f.get("sink", 0), f.get("rise", 0)
    if rise:                       # the legs' row (93) repeated: the stubby legs show; the body's lowest outline row stays
        leg_row, low_row = FEET_ROW - 2, FEET_ROW - 1
        upper = top.copy()
        upper[low_row:] = 0
        lifted = K.shifted(upper, 0, -rise)
        for k in range(rise):
            r = low_row - 1 - k
            lifted[r] = np.where(lifted[r, :, 3:] > 0, lifted[r], top[leg_row])
        lifted[low_row:] = top[low_row:]
        top = lifted
    if sink:
        top = K.shifted(top, 0, sink)
    lf, rf = f.get("feet", ((0, 0), (0, 0)))
    c = K.put(top, feet_part(P, lf, rf), 0, 0)      # the feet in front of the sunk body
    c[SOLES + 1:] = 0
    if f.get("dx") or f.get("hop"):
        c = K.shifted(c, f.get("dx", 0), -f.get("hop", 0))
    return c


def leg_gaps(c, design_holes):
    """Gaps a moved foot leaves against the body (not the design's own gaps): the stubby legs in shadow."""
    for h in K.holes(c):
        if min(y for y, _ in h) >= FEET_ROW - 7 and not any(p in design_holes for p in h):
            for y, x in h:
                c[y, x] = rgba("C")
    return c


def frame(P, f):
    if f is None:
        return P.design.copy()
    c = build(P, f)
    ref = K.shifted(P.design, f.get("dx", 0), -f.get("hop", 0))
    own = {p for h in K.holes(ref) for p in h}
    c = leg_gaps(finish_near(c, ref), own)
    return drop_orphans(c, ref)


def drop_orphans(c, ref):
    """Outline squares with no colour round them that the (shifted) design does not have, unless one holds a piece on."""
    keep = K.orphan_outline(ref, OUT)
    for y, x in zip(*np.nonzero(K.orphan_outline(c, OUT) & ~keep)):
        t = c.copy()
        t[y, x] = 0
        if len(K.pieces(t)) <= len(K.pieces(c)):
            c = t
    return c


def closed_eyes(P, a):
    """Each eye's squares (the amber and the glint) painted the skull's bone, with one dark lid row through its middle."""
    out = a.copy()
    eye = np.isin(P.letters, ["o", "w"])
    seen = np.zeros_like(eye)
    for sy, sx in zip(*np.nonzero(eye)):
        if seen[sy, sx]:
            continue
        stack, pts = [(sy, sx)], []
        seen[sy, sx] = True
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for dy, dx in N8:
                v, u = y + dy, x + dx
                if eye[v, u] and not seen[v, u]:
                    seen[v, u] = True
                    stack.append((v, u))
        ys = [p[0] for p in pts]
        mid = (min(ys) + max(ys) + 1) // 2
        for y, x in pts:
            out[y, x] = rgba("a" if y == mid else "b")
    return out


# ------------------------------------------------------------------------------------------------ R: standing up
def standing(P, n, rise=0):
    """The figure without the feet and the tail, the tube (n squares) out of the mouth, turned a quarter counter-
    clockwise (the tube up, the belly to the right, the antennae back to the left), stood on the design's feet with
    the tail on the ground behind him."""
    up = P.body.copy()
    with_tube(up, n)
    m = up[..., 3] > 0
    # keep only the figure above the feet's top row (the body's bottom outline joins the feet)
    fig = K.Part.from_canvas(up, m, (64.0, 94.0))
    t = K.rot90(fig, 3)
    c = np.zeros_like(P.design)
    ys, xs = np.nonzero(t.s[..., 3] > 0)
    h, w = ys.max() + 1, xs.max() + 1
    # its lowest row on the row over the feet, its middle over the feet's middle (the pivot's column), a little back
    oy = FEET_ROW - h + 1 - rise
    ox = MID - w // 2 - 2
    K.put(c, t.s, ox, oy)
    # the tail lying lower, on the ground behind him, its root against the body's lowest left edge
    tail = tail_part(P, 0, 4)
    low = c[FEET_ROW - 4:FEET_ROW, :, 3] > 0
    left = int(np.nonzero(low.any(0))[0].min())
    K.put(c, tail, left + 2 - 55, 0, under=True)
    K.put(c, feet_part(P), 0, 0)
    c[SOLES + 1:] = 0
    c = K.finish(c, OUT, SOLES, keep=None, pinholes=4)
    # the gaps the turned body leaves over the feet are the stubby legs in shadow: the shell's dark blue
    for h in K.holes(c):
        if min(y for y, _ in h) >= FEET_ROW - 7:
            for y, x in h:
                c[y, x] = rgba("C")
    return c


# ------------------------------------------------------------------------------------------------ the actions
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
MS = {"idle": [140] * 8, "run": [89] * 8, "attack": [60, 60, 70, 70, 70, 70],
      "skill": [70, 70, 60, 70, 80, 80, 80, 80], "skill2": [70, 70, 80, 80, 90, 90, 90, 80],
      "ult": [70, 70, 70, 70, 80, 90, 90, 80], "hit": [120, 120], "dead": [100, 100, 120, 120, 150, 150, 200, 500]}
POSES = {
    # League's attack1: a crouch, rearing back, the head thrust forward with the tube out (the glob on frame 3)
    "attack": [dict(dx=-1, ant=-1), dict(dx=-1, ant=-1, tail=1), dict(dx=1, tube=16, ant=1),
               dict(dx=1, tube=13, ant=1), dict(tube=7), None],
    # Q: rearing up, drawn back, coiled low, the lunge, the long tube (the spittle on frame 5), recoiling
    "skill": [dict(ant=-1), dict(dx=-1, ant=-1, tail=1), dict(dx=-2, ant=-1, tail=1), dict(dx=1, ant=1),
              dict(dx=2, tube=22, ant=1), dict(dx=2, tube=18, ant=1), dict(dx=1, tube=8), None],
    # E: drawn back, then pushed forward spewing (a short tube; the ooze leaves on frame 4), back again
    "skill2": [dict(ant=-1), dict(dx=-1, ant=-1, tail=1), dict(dx=1, tube=6, ant=1), dict(dx=2, tube=11, ant=1),
               dict(dx=2, tube=11, ant=1, tail=-1), dict(dx=1, tube=5), dict(ant=-1), None],
    "hit": [dict(dx=-2, ant=-1, tail=1), dict(dx=-1, ant=-1)],
}


def ult_frames(P):
    """R: crouch, rise, stand up with the tube growing (the shell on frame 5), the tube shrinking, back down."""
    return [frame(P, dict(ant=-1)), frame(P, dict(dx=-1, ant=-1, tail=1)), standing(P, 6), standing(P, 12),
            standing(P, 16), standing(P, 10), frame(P, dict(ant=1)), P.design.copy()]


def dead_frames(P):
    """Struck back, then sinking over the feet until he lies flat, the eyes closed."""
    steps = [dict(dx=-2, ant=-1, tail=1), dict(dx=-2, sink=2, ant=1), dict(dx=-2, sink=4, closed=True, ant=2),
             dict(dx=-2, sink=6, closed=True, ant=2)]
    out = [frame(P, s) for s in steps]
    return out + [out[-1].copy() for _ in range(4)]


# the run (League's pace: kogmaw_run cycles in 0.71 s -> 8 x 89 ms): a waddle on the two big feet
L_STEP = [3, 2, 0, -2, -3, -2, 0, 2]
L_LIFT = [0, 0, 0, 0, 0, 1, 1, 1]
R_STEP = [-3, -2, 0, 2, 3, 2, 0, -2]
R_LIFT = [0, 1, 1, 1, 0, 0, 0, 0]
HOP = [0, 0, 1, 0, 0, 0, 1, 0]                   # the whole waddle off the ground a row while a foot passes
TAIL_SW = [-1, 0, 1, 0, -1, 0, 1, 0]
ANT_SW = [0, -1, 0, 1, 0, -1, 0, 1]


def fill_dents(c, r0, r1):
    """Squares in rows r0..r1 that are clear but walled on 3-4 sides (a moved foot's one-frame notch against the body):
    the most common colour round them (the outline where it closes the edge)."""
    for _ in range(2):
        op = c[..., 3] > 0
        for y in range(r0, r1 + 1):
            for x in range(1, 127):
                if op[y, x]:
                    continue
                nb = [c[y + a, x + b] for a, b in N4 if op[y + a, x + b]]
                if len(nb) >= 3:
                    cols = [tuple(int(v) for v in q) for q in nb]
                    c[y, x] = max(set(cols), key=cols.count)
    return c


def run_frames(P):
    out = []
    for k in range(8):
        f = dict(hop=HOP[k], tail=TAIL_SW[k], ant=ANT_SW[k],
                 feet=((L_STEP[k], L_LIFT[k]), (R_STEP[k], R_LIFT[k])))
        c = fill_dents(frame(P, f), 88, SOLES - 1)
        zone = np.zeros((128, 128), bool)
        zone[86:SOLES + 1] = True
        for y, x in zip(*np.nonzero(K.orphan_outline(c, OUT) & zone)):
            t = c.copy()
            t[y, x] = 0
            if len(K.pieces(t)) <= len(K.pieces(c)):
                c = t
        out.append(c)
    return out


IDLE_ANT = [0, 0, 1, 1, 1, 0, -1, 0]
IDLE_TAIL = [0, 0, 0, 1, 1, 1, 0, 0]


def frames(P, tag):
    if tag == "idle":
        return [P.design.copy() if a == 0 and t == 0 else frame(P, dict(ant=a, tail=t))
                for a, t in zip(IDLE_ANT, IDLE_TAIL)]
    if tag == "run":
        return run_frames(P)
    if tag == "ult":
        return ult_frames(P)
    if tag == "dead":
        return dead_frames(P)
    return [frame(P, f) for f in POSES[tag]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", help="write the part overlay PNG and stop")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    P = Parts()
    if a.parts:
        P.overlay(a.parts)
        print({k: int(m.sum()) for k, m in P.masks.items()})
        return
    built = {tag: frames(P, tag) for tag in TAGS}
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}" for r in rows))
    if not a.no_write:
        bad = K.write_strips("kogmaw", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "kogmaw_strips_review.png"), z=4,
                       soles=SOLES)
    return built


if __name__ == "__main__":
    main()

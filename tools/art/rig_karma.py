#!/usr/bin/env python3
"""Karma's action strips posed from the approved design's own parts (2026-10-09): the casting body = the idle's.

    python tools/art/rig_karma.py [--parts PNG] [--check] [--review DIR] [--no-write]

Codex's step-2 delivery (assets/source/karma/codex_strips/) pasted the design's head on bodies it drew anew: slimmer
than the idle (attack 82-92%, hit 77% of its squares), the waist prongs gone, the legs and boots not the design's (its
own HANDOFF: 30 standing frames differ). The user: 「有问题你要修复」「你修复到完美版再喊我review」. So, as for Vladimir,
Rengar, Kog'Maw and Zed, every frame is the design with only what the action moves moved, nothing resampled
(no-deformation rule: translation, quarter turns, mirrors, whole-row shifts, layering; no body sunk over the feet):
- the parts are cut square for square with the outline squares that ring them alone: the two ARMS (NEAR = image left,
  hanging from the shoulder to the hand at the hip; FAR = image right, reaching forward to the open hand), the jade
  RING over the head, the four ivory PRONGS (beside the head and the waist), the skirt's left HEM and right FLAP, the
  two LEGS (the far one: the ankle and the boot under the hem; the near one: the bare leg in the slit and the boot);
- arm poses are rigid units about the shoulder: the near arm HANG (as drawn), BACK (a quarter turn: swept back and up),
  FWD (a quarter turn the other way: across the chest), UP (mirrored: raised beside the head), OUT (mirrored the
  other way: the hand in front of the skirt); the far arm FWD (as drawn), PUSH (mirrored: level at the shoulder), UP
  (a quarter turn: raised), DOWN (a quarter turn: hanging behind the body); a raised arm takes its shoulder up with it;
- whole-figure moves: a lunge / recoil (columns), a hop (rows, the feet included);
- the ring and the prongs float: they bob a row or two (the idle), lift on the mantra and fall off in the death;
- the hem and the flap flare by whole rows (rigkit.swing_leg about the hip row);
- the death: struck back, the ring and the prongs flying off, then the figure turned exactly a quarter counter-
  clockwise about the feet (lying on her back, the head to the left), the ring and the prongs on the ground behind her;
- the run (League's pace: karma_2012_run cycles in 0.8 s -> 6 x 133 ms): the legs swung about the hips by whole rows
  (the boots at most 11 columns apart), the hem and the flap swaying against them, the arms swinging a column, a hop
  of a row while a foot passes.
Each built frame is finished only round what moved (finish_near); the rest stays the design's square for square.
Writes assets/source/native/karma_<tag>.png (8x, 96x80 cells, soles on cell row 65) and karma_cells.json; then
tools/art/import_native.py (BREATHE_SKIP: the idle floats here; UNSTEADY: the ring is the top of every idle/run frame).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import design_karma as DK  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "karma_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
L = DK.RGB
OUT = L["0"]
CELL = (96, 80)
CELL_PIVOT = (46, 54)            # the soles on cell row 65 (the references' feet line, poses.json cell [96, 80, 14])
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)


def sq(spec):
    m = np.zeros((128, 128), bool)
    for r, cols in spec.items():
        m[r, cols] = True
    return m


# the parts' coloured squares, {row: [cols]} on the design canvas (karma_design.txt)
NEAR = {78: [59, 60, 61], 79: [59, 60, 61], 80: [59, 60], 81: [58, 59], 82: [58, 59, 60], 83: [58, 59, 60],
        84: [57, 58], 85: [57, 58], 86: [56, 57], 87: [56]}
FAR = {80: [71], 81: [71, 72, 73], 82: [75, 76]}
NEAR_SHOULDER = (60.5, 78.0)     # (x, y): the top of the near arm under the shoulder's shade (row 77)
FAR_SHOULDER = (71.0, 80.0)      # the far arm comes out from behind the chest here
RING_ROWS = (58, 62)             # the jade ring: every square of these rows (row 63 is the hair's top outline)
PRONGS = {"ul": {65: [54], 66: [53, 54], 67: [53, 54], 68: [53]},
          "ur": {65: [74], 66: [74]},
          "ll": {76: [55], 77: [54], 78: [54, 55, 56, 57], 79: [55, 56, 57]},
          "lr": {76: [73], 77: [74], 78: [72, 73, 74], 79: [72, 73]}}
HIP = 87                         # the hem and the flap swing from here
NEAR_LEG = {88: [66, 67, 68], 89: [66, 67, 68], 90: [67, 68, 69], 91: [67, 68, 69, 70], 92: [66, 67, 68, 69, 70],
            93: [66, 67, 68, 69], 94: [66, 67, 68, 69], 96: [67, 68, 69, 70], 97: [67, 68, 69, 70],
            98: [67, 68, 69, 70, 71]}
FAR_LEG = {95: [57, 58], 96: [57, 58], 97: [57, 58], 98: [56, 57, 58]}
ANKLE = 95                       # the boots from here down (moved whole)


def design():
    a = np.asarray(Image.open(K.lp(DESIGN)).convert("RGBA"))
    a = (a if a.shape[0] == 128 else a[Z // 2::Z, Z // 2::Z]).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        op = d[..., 3] > 0
        self.ink = ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
        R_, C_ = np.mgrid[0:128, 0:128]
        col = {"near": sq(NEAR), "far": sq(FAR), **{k: sq(v) for k, v in PRONGS.items()}}
        for k, m in col.items():
            assert all(op[y, x] and not ink[y, x] for y, x in zip(*np.nonzero(m))), k
        ring = op & (R_ >= RING_ROWS[0]) & (R_ <= RING_ROWS[1])
        legs_c = {"nleg": sq(NEAR_LEG) & op & ~ink, "fleg": sq(FAR_LEG) & op & ~ink}
        taken = np.zeros_like(op)
        for m in list(col.values()) + list(legs_c.values()):
            taken |= m
        taken |= ring
        body_c = op & ~ink & ~taken

        def ring_of(c, others):
            """The outline squares round c that no square of `others` touches (4-neighbours)."""
            m = np.zeros_like(c)
            for y, x in zip(*np.nonzero(ink & ~taken)):
                if any(c[y + a, x + b] for a, b in N8) and not any(others[y + a, x + b] for a, b in N4):
                    m[y, x] = True
            return m

        self.masks = {}
        for k, c in col.items():
            self.masks[k] = c | ring_of(c, body_c | (taken & ~c))
        self.masks["ring"] = ring
        for k, c in legs_c.items():
            self.masks[k] = c | ring_of(c, body_c | (taken & ~c))
        # the boots' outline rows under the soles' line belong to the legs (rows 95-99 round each boot)
        for k, (c0, c1) in (("fleg", (55, 60)), ("nleg", (65, 72))):
            box = (R_ >= ANKLE) & (R_ <= SOLES) & (C_ >= c0) & (C_ <= c1) & op
            self.masks[k] |= box
        # the hem (left of the slit's dark inside) and the flap (right of the bare leg), rows HIP+1 .. 95
        busy = np.zeros_like(op)
        for k in ("near", "far", "nleg", "fleg", "ul", "ur", "ll", "lr"):
            busy |= self.masks[k]
        self.masks["hem"] = op & ~busy & (R_ > HIP) & (R_ <= 95) & (C_ <= 61)
        self.masks["flap"] = op & ~busy & (R_ > HIP) & (R_ <= 95) & (C_ >= 71)
        for a_ in self.masks:
            for b_ in self.masks:
                if a_ < b_:
                    assert not (self.masks[a_] & self.masks[b_]).any(), (a_, b_)
        self.body = d.copy()
        for m in self.masks.values():
            self.body[m] = 0
        self.part = {k: K.Part.from_canvas(d, self.masks[k], j) for k, j in
                     (("near", NEAR_SHOULDER), ("far", FAR_SHOULDER))}
        assert np.array_equal(self.build({}), d)

    def piece(self, k, dx=0, dy=0):
        out = np.zeros_like(self.design)
        out[self.masks[k]] = self.design[self.masks[k]]
        return K.shifted(out, dx, dy) if dx or dy else out

    def overlay(self, path, z=12):
        cols = {"near": (255, 80, 80), "far": (80, 160, 255), "ring": (60, 220, 120), "ul": (250, 220, 60),
                "ur": (250, 220, 60), "ll": (240, 160, 40), "lr": (240, 160, 40), "nleg": (200, 80, 255),
                "fleg": (140, 60, 200), "hem": (255, 140, 200), "flap": (120, 255, 255)}
        a = self.design.copy()
        for k, c in cols.items():
            m = self.masks[k]
            a[m, :3] = (a[m, :3] * 0.35 + np.array(c) * 0.65).astype(np.uint8)
        c = Image.fromarray(a).crop((46, 54, 82, 102))
        bg = Image.new("RGBA", c.size, (96, 104, 84, 255))
        bg.alpha_composite(c)
        bg.resize((c.width * z, c.height * z), Image.NEAREST).save(path)

    # ------------------------------------------------------------------------------------------ poses
    def arm(self, which, how):
        """(part, (dx, dy) of the shoulder) for a pose."""
        u = self.part[which]
        if which == "near":
            table = {"hang": (u, (0, 0)), "back": (K.rot90(u, 1), (0, 0)), "fwd": (K.rot90(u, 3), (1, 0)),
                     "up": (u.flip_v(), (0, -2)), "out": (u.flip_h(), (0, 0))}
        else:
            # the far arm in the design is foreshortened (it points at the viewer); stretched out toward the target it
            # is the near arm's own unit (the same skin and bracer squares) turned a quarter and set on the far
            # shoulder: LONG reaching forward and a little down, REACH forward and a little up
            n = self.part["near"]
            table = {"fwd": (u, (0, 0)), "push": (u.flip_v(), (0, -1)), "up": (K.rot90(u, 3), (1, -2)),
                     "down": (K.rot90(u, 1), (-1, 0)),
                     "long": (K.rot90(n, 3), (0, -1)), "reach": (K.rot90(n, 3).flip_v(), (0, -1))}
        return table[how]

    def build(self, f):
        """One frame: f = dict(near, far, dx, hop, ring (dx, dy), prongs {k: (dx, dy)}, hem, flap (hem columns),
        legs ((dx, lift) far, (dx, lift) near), near_under, far_over)."""
        c = np.zeros_like(self.design)
        # behind everything: the far arm when it hangs or is raised (it is behind the chest and the head)
        far = f.get("far", "fwd")
        far_behind = far in ("down", "up") and not f.get("far_over")
        if far_behind:
            u, (dx, dy) = self.arm("far", far)
            K.place(c, u, (FAR_SHOULDER[0] + dx, FAR_SHOULDER[1] + dy))
        # the legs, then the hem and the flap over them, then the body
        lf, ln = f.get("legs", ((0, 0), (0, 0)))
        for k, (dx, lift) in (("fleg", lf), ("nleg", ln)):
            if dx or lift:
                K.put(c, K.swing_leg(self.design, self.masks[k], HIP, ANKLE, dx, lift), 0, 0)
            else:
                K.put(c, self.piece(k), 0, 0)
        for k in ("hem", "flap"):
            t = f.get(k, 0)
            K.put(c, K.swing_leg(self.design, self.masks[k], HIP, 96, t) if t else self.piece(k), 0, 0)
        K.put(c, self.body, 0, 0)
        # the prongs and the ring float (drawn behind the body's squares: the head and the shoulders stay in front)
        pr = f.get("prongs", {})
        for k in ("ul", "ur", "ll", "lr"):
            K.put(c, self.piece(k, *pr.get(k, (0, 0))), 0, 0, under=True)
        K.put(c, self.piece("ring", *f.get("ring", (0, 0))), 0, 0, under=f.get("ring", (0, 0))[1] > 0)
        if not far_behind:
            u, (dx, dy) = self.arm("far", far)
            K.place(c, u, (FAR_SHOULDER[0] + dx, FAR_SHOULDER[1] + dy), under=f.get("far_under", False))
        if f.get("near_swing"):
            K.put(c, K.swing_leg(self.design, self.masks["near"], int(NEAR_SHOULDER[1]), 88, f["near_swing"]), 0, 0)
        else:
            u, (dx, dy) = self.arm("near", f.get("near", "hang"))
            K.place(c, u, (NEAR_SHOULDER[0] + dx, NEAR_SHOULDER[1] + dy), under=f.get("near_under", False))
        c[SOLES + 1:] = 0
        if f.get("dx") or f.get("hop"):
            c = K.shifted(c, f.get("dx", 0), -f.get("hop", 0))
        return c


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


def drop_orphans(c, ref):
    """Outline squares with no colour round them that the (shifted) design does not have, unless one holds a piece on."""
    keep = K.orphan_outline(ref, OUT)
    for y, x in zip(*np.nonzero(K.orphan_outline(c, OUT) & ~keep)):
        t = c.copy()
        t[y, x] = 0
        if len(K.pieces(t)) <= len(K.pieces(c)):
            c = t
    return c


def frame(P, f):
    if f is None:
        return P.design.copy()
    c = P.build(f)
    ref = K.shifted(P.design, f.get("dx", 0), -f.get("hop", 0))
    return drop_orphans(finish_near(c, ref), ref)


# ------------------------------------------------------------------------------------------------ the strips
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill_e", "ult", "hit", "dead"]
MS = {"idle": [200] * 6, "run": [133] * 6, "attack": [60, 60, 70, 70, 70, 70], "skill": [55, 55, 60, 60, 70, 70],
      "skill2": [55, 55, 60, 60, 70, 70], "skill_e": [50, 50, 55, 60, 55], "ult": [50, 50, 60, 70, 70],
      "hit": [120, 120], "dead": [100, 100, 100, 120, 150, 150, 200, 500]}
UP = {"ul": (0, -1), "ur": (0, -1), "ll": (0, -1), "lr": (0, -1)}
SPREAD = {"ul": (-1, -1), "ur": (1, -1), "ll": (-1, 0), "lr": (1, 0)}
POSES = {
    # the spirit bolt (League's attack1: an arm drawn back beside the head, then flung forward): the near arm swings
    # back, the far arm stretches out and the bolt leaves its palm (frame 4), the near arm following through in front
    # (an arm across the chest would hide the wrap and the top: it read as a bare torso)
    "attack": [dict(dx=-1), dict(near="back", dx=-1, hem=1), dict(near="back", far="push"),
               dict(near="out", far="reach", dx=1, hem=-1), dict(far="reach", dx=1, hem=-1), dict(far="push")],
    # Inner Flame: gather, the near arm swept back, a lunge and the far palm pushed out (frame 4)
    "skill": [dict(near="out"), dict(near="back", dx=-1, hem=1), dict(far="push", dx=1, hem=-1),
              dict(far="reach", dx=2, hem=-2, flap=-1), dict(far="reach", dx=2, hem=-1), dict(far="push", dx=1)],
    # Focused Resolve: the arms spread, the ring lifting, then the far hand pointing at the target (frame 4)
    "skill2": [dict(near="back", far="push"), dict(near="back", far="reach", ring=(0, -1), prongs=UP, dx=-1),
               dict(near="out", far="long", dx=1), dict(near="out", far="long", dx=1, hem=-1),
               dict(far="long", dx=1), dict(far="push")],
    # Inspire: the near arm raised, then the far arm sweeping out to the ally, the skirt swirling (frame 3)
    "skill_e": [dict(near="out"), dict(near="back", ring=(0, -1)), dict(far="long", hem=1, flap=1, prongs=UP),
                dict(far="long", hem=1), dict(far="push")],
    # Mantra: the hand gathered, then both arms raised wide, the hem and the flap flaring, the ring lifting and the
    # prongs spreading (frame 3)
    "ult": [dict(near="out"), dict(near="back", far="reach", hem=-1, flap=1, ring=(0, -1)),
            dict(near="back", far="reach", hem=-2, flap=1, ring=(0, -2), prongs=SPREAD),
            dict(near="back", far="reach", hem=-2, flap=1, ring=(0, -2), prongs=SPREAD),
            dict(far="push", hem=-1, flap=1, ring=(0, -1))],
    "hit": [dict(near="out", dx=-2, ring=(-1, 0), hem=1), dict(dx=-1)],
}
IDLE_RING = [0, -1, -2, -2, -1, 0]
IDLE_UP = [0, 0, -1, -1, -1, 0]                    # the head's prongs, a frame behind the ring
IDLE_LOW = [0, -1, -1, 0, 0, 0]                    # the waist's prongs


def idle_frames(P):
    out = []
    for r, u, w in zip(IDLE_RING, IDLE_UP, IDLE_LOW):
        f = dict(ring=(0, r), prongs={"ul": (0, u), "ur": (0, u), "ll": (0, w), "lr": (0, w)})
        out.append(P.design.copy() if not (r or u or w) else frame(P, f))
    return out


# the run: Codex's skin swap on oppi's Ahri run (sprite-pipeline: the run alone keeps the oppi skeleton - a lively
# crossing stride with the back leg kicking up, the arms pumping and the skirt flying, which the design's own parts
# cannot give under the long skirt; the rig's own try shuffled), 6 x 133 ms (karma_2012_run cycles in 0.8 s). Codex
# pasted the old head translated only; here every frame gets the approved design's head (the face of POLISH 1/3) at the
# same place, the four prongs from the design at the same offset (Codex drew them only in bits), and no jade on the
# legs (POLISH 2: the user had the leg's dot removed); finished round what changed.
CODEX = os.path.join(ROOT, "assets", "source", "karma", "codex_strips")
RUN_PIVOT = (32, 47)              # Codex's 64x64 run cells: the soles on cell row 58
HEAD_RANGES = {**{y: (55, 73) for y in range(58, 64)}, **{y: (54, 71) for y in range(64, 69)},
               **{y: (51, 73) for y in range(69, 76)}}
RUN_HEAD = {**{y: (55, 73) for y in range(58, 64)}, **{y: (51, 76) for y in range(64, 69)},
            **{y: (51, 73) for y in range(69, 76)}}       # the run's paste: the hair's sides and the head's prongs too
JADE = ("e", "m", "j", "J", "l", "n", "i")         # the ring's and the prongs' colours (none of them on the body)


def head_mask(a, ranges=HEAD_RANGES):
    """The head piece (the ring, the bob, the circlet, the face, the earrings): the opaque squares in `ranges`, the
    largest 8-connected piece (work/kr/head_kr.py)."""
    op = a[..., 3] > 0
    m = np.zeros(op.shape, bool)
    for y, (c0, c1) in ranges.items():
        m[y, c0:c1 + 1] = op[y, c0:c1 + 1]
    comps = K.pieces(np.where(m[..., None], a, 0).astype(np.uint8))
    out = np.zeros_like(m)
    for y, x in comps[0]:
        out[y, x] = True
    return out


def find_head(c, old, hm):
    ys, xs = np.nonzero(hm)
    patch = old[ys, xs]
    for oy in range(-ys.min(), 128 - ys.max()):
        for ox in range(-xs.min(), 128 - xs.max()):
            if (c[ys + oy, xs + ox] == patch).all():
                return oy, ox
    raise SystemExit("the old head is not in a Codex run frame")


def run_frames(P):
    old = np.asarray(Image.open(K.lp(os.path.join(CODEX, "design", "karma_design_1x.png"))).convert("RGBA"))
    hm_old = head_mask(old)
    hm = head_mask(old, RUN_HEAD) | head_mask(P.design, RUN_HEAD)
    jade = [np.array(L[k], np.uint8) for k in JADE]
    out = []
    for k in range(6):
        f = np.asarray(Image.open(K.lp(os.path.join(CODEX, "native", f"karma_run_{k + 1:02d}.png"))).convert("RGBA"))
        c = np.zeros_like(P.design)
        K.put(c, f, PIVOT[0] - RUN_PIVOT[0], PIVOT[1] - RUN_PIVOT[1])
        oy, ox = find_head(c, old, hm_old)
        before = c.copy()
        # Codex's own ring / prong / tattoo squares outside the head go (the design's prongs come back below)
        head_here = np.zeros((128, 128), bool)
        ys, xs = np.nonzero(hm)
        head_here[ys + oy, xs + ox] = True
        for col in jade:
            hit = (c[..., :3] == col).all(-1) & (c[..., 3] > 0) & ~head_here
            c[hit] = 0
        for y, x in zip(ys, xs):
            c[y + oy, x + ox] = P.design[y, x]
        # the waist's prongs are left out of the run, as Codex drew it: the pumping arms pass where they float, and
        # partly hidden they read as specks (one frame here, one there - a blink)
        # the squares the tattoo left: the leg's skin round them
        for y, x in zip(*np.nonzero((before[..., 3] > 0) & (c[..., 3] == 0) & ~head_here)):
            if y >= 86 + oy:
                nb = [tuple(int(v) for v in c[y + a_, x + b_]) for a_, b_ in N4 if c[y + a_, x + b_, 3]]
                skin = [q for q in nb if q[:3] in (L["s"], L["S"], L["z"])]
                if skin:
                    c[y, x] = max(set(skin), key=skin.count)
        out.append(drop_orphans(finish_near(c, before), np.zeros_like(c)))
    return out


# the death: struck back, the ring and the prongs flying off, sinking to her knees into the skirt (everything above
# the boots laid lower over them), then lying on her side (an exact quarter turn counter-clockwise: the head to the left,
# the skirt's flare on the ground, the far arm hidden behind her), the ring and two prongs on the ground behind her
SHOE_ROW = 95


def sunk(a, n):
    """Everything above SHOE_ROW n rows lower, laid over the boots (layering: nothing is taken out)."""
    low = np.zeros_like(a)
    low[SHOE_ROW:] = a[SHOE_ROW:]
    top = np.zeros_like(a)
    top[:SHOE_ROW] = a[:SHOE_ROW]
    return K.put(low, top, 0, n)


def dead_frames(P):
    scatter = {"ul": (-2, -2), "ur": (2, -2), "ll": (-2, 1), "lr": (2, 1)}
    out = [frame(P, dict(near="out", dx=-1, ring=(-1, -1))),
           frame(P, dict(near="back", far="push", dx=-2, ring=(-5, -4), prongs=scatter))]
    # on her knees: the body without the ring and the prongs sunk 4 rows, the ring and the prongs falling
    kneel = P.build(dict(far="push"))
    for k in ("ring", "ul", "ur", "ll", "lr"):
        kneel[P.masks[k]] = 0
    kneel = finish_near(sunk(kneel, 4), sunk(P.design, 4))
    K.put(kneel, P.piece("ring", -9, 4), 0, 0, under=True)
    for k, (dx, dy) in {"ul": (-4, 9), "ur": (4, 6), "ll": (-4, 12), "lr": (4, 12)}.items():
        K.put(kneel, P.piece(k, dx, dy), 0, 0, under=True)
    out.append(K.shifted(K.finish(kneel, OUT, SOLES, keep=None, pinholes=2), -2, 0))
    body = P.build(dict(far="down"))
    for k in ("ring", "ul", "ur", "ll", "lr"):
        body[P.masks[k]] = 0
    body = finish_near(body, P.design)
    fig = K.Part.from_canvas(body, body[..., 3] > 0, (64.0, 100.0))
    lying = K.turn(fig, 90)                          # an exact quarter turn counter-clockwise: the head to the left
    ring = P.piece("ring")
    rows = np.nonzero(ring[..., 3].any(1))[0]

    def lie(drop):
        c = np.zeros_like(P.design)
        K.place(c, lying, (64.0 + 6, 100.0))
        low = int(np.nonzero(c[..., 3].any(1))[0].max())
        c = K.shifted(c, 0, SOLES - low - drop)
        K.put(c, K.shifted(ring, -38, SOLES - int(rows.max())), 0, 0, under=True)
        for k, base in (("ul", -24), ("ll", -27)):
            p = P.piece(k)
            pr = np.nonzero(p[..., 3].any(1))[0]
            K.put(c, K.shifted(p, base, SOLES - int(pr.max())), 0, 0, under=True)
        return K.finish(c, OUT, SOLES, keep=None, pinholes=2)
    out += [lie(3), lie(1), lie(0), lie(0), lie(0)]
    return out


def frames(P, tag):
    if tag == "idle":
        return idle_frames(P)
    if tag == "run":
        return run_frames(P)
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
        bad = K.write_strips("karma", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "karma_rig_review.png"), z=4, soles=SOLES)
    return built


if __name__ == "__main__":
    main()

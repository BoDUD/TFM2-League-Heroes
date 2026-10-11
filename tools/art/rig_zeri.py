#!/usr/bin/env python3
"""Zeri's action strips posed from the approved design's own parts: the casting body = the idle's.

    python tools/art/rig_zeri.py [--check] [--review DIR] [--tags attack,run]

Codex's step-2 delivery on the 40-row design (assets/source/zeri/codex_strips_v2/) cut the design into parts and moved
them by translations and quarter turns, but it turned the free arm a quarter turn in the attack, W, E and R (the
hanging arm stuck out to the image left), fired the rifle from the hip (a quarter turn about the elbow), slid whole
legs to and fro for the run and laid the death down in one jump. The user: 「有问题的地方你帮我修复 模型穿模 色素多
模型变形之类的 完美了再喊我review」. Every frame here is the design (assets/source/native/zeri_native.png,
tools/art/design_zeri.py) with only what the action moves moved, nothing resampled:
- the arm unit (RIFLE: the rifle with the hand gripping it, FOREARM: the glove, the cuff and the elbow under it) is one
  rigid piece: upright as drawn, or a quarter turn clockwise about the elbow (ELBOW) so the forearm reaches forward and
  the rifle lies level at the hip, clear of the hair and the face (League's Q fires from the hip); the free arm at the
  image left never moves.
- the whole figure moves: a column back for the recoil and the hit; the upper body lowered a row over the legs for the
  crouches and the landings (lowered(): everything above the hips comes down over them); lifted for E's hop and R's
  spring; leant by moving the head rows and the chest rows whole (lean()).
- the run (8 frames, league_caitlyn's way): the upper body the idle's with the rifle held level at the hip (as League's
  Zeri runs), stepping down a row as a foot lands; the legs one leg's eight phases drawn square by square at one
  length in the leggings' colours on the design's own flat boots, the far leg four phases on and three squares
  right so the feet cross every other step (RUN_PHASES); E's lunge and R's hop are strides of it.
- the death (League's): struck back, sinking to her knees (whole shin rows out, the boots kept), then down on her face:
  the figure without the rifle a quarter turn clockwise (League falls forward), the rifle lying level by her.
Each frame is finished round what moved (rigkit.finish: the outline closed on moved edges, pinholes filled, stray
outline squares dropped; the head never changes), then audited: pieces, holes, orphan outline squares, nothing under the
soles, the head the design's in every standing frame.
Writes assets/source/native/zeri_<tag>.png (8x, 96 x 80 cells) and zeri_cells.json; then tools/art/import_native.py.
--check compares instead of writing; --review writes a review sheet and GIF.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "zeri_native.png")
HERO = "zeri"
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
import json as _json
# the design table on the canvas (design40/zeri40_final.txt, its soles on row 99). The constants below are written in
# the 40-row table's rows; the 37-row design took whole rows out (design40/shrink37.json): Rw() maps them
_KEPT = _json.load(open(os.path.join(ROOT, "assets", "source", "zeri", "design40", "shrink37.json")))["rows"]


def Rw(r):
    """A 40-row table row (int or float) -> the design's row (a row taken out -> the next one kept)."""
    base = int(r // 1)
    frac = r - base
    nxt = next((k for k, v in enumerate(_KEPT) if v >= base), len(_KEPT) - 1)
    return nxt + frac


OX, OY = 53, 100 - len(_KEPT)
CELL, CELL_PIVOT = (96, 80), (48, 64)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_back", "ult", "hit", "dead"]
MS = {"idle": [125] * 8, "run": [107] * 7 + [106], "attack": [67, 66, 100, 84, 83], "skill": [90, 90, 87, 117, 116],
      "skill2": [75] * 4, "skill2_back": [75] * 4, "ult": [75, 75, 90, 93], "hit": [100, 100],
      "dead": [100, 100, 100, 120, 150, 200, 300, 400]}


def T(r, c):
    """Table square (row, column, 40-row coordinates) -> canvas (x, y)."""
    return OX + c, OY + Rw(r)


# ------------------------------------------------------------------------------------------------ the parts (table)
# the rifle with the hand on its grip, by table rows: (first, last column); the glove under the hand stays
RIFLE_ROWS = {0: (19, 21), 1: (19, 22), 2: (19, 23), 3: (19, 23), 4: (18, 23), 5: (18, 22), 6: (18, 22), 7: (18, 23),
              8: (17, 23), 9: (17, 23), 10: (16, 22), 11: (16, 21), 12: (16, 20), 13: (16, 21), 14: (16, 22),
              15: (16, 18), 16: (16, 18), 17: (16, 18)}
RIFLE_EXTRA = [(15, 20), (15, 21), (15, 22), (16, 21), (16, 22), (16, 23)]   # the hand's knuckles, the grip's end
GRIP = (T(14, 20)[0] + 0.5, T(14, 20)[1] + 0.5)   # the middle of the hand (the rifle alone turns about it)
# the forearm under the hand (the maroon glove, the white cuff, the elbow out of the coat's sleeve): with the rifle and
# the hand it makes the arm unit, turned a quarter turn clockwise about the elbow so the rifle lies level at the hip
FOREARM = [(15, 19), (16, 19), (16, 20), (17, 19), (17, 20), (18, 18), (18, 19), (18, 20), (19, 18), (19, 19), (20, 18)]
# levelled, the forearm is one maroon band from the elbow to the hand: the white cuff (the design's, under the hand)
# would sit in the middle of it as a white blot (the user: 「这里多余的色素是什么？？」)
LEVEL_RECOLOUR = {"#F4F4F8": "#73234B", "#C0BAD3": "#45183A"}
ELBOW = (T(20, 18)[0] + 0.5, T(20, 18)[1] + 0.5)
HEAD_BOX = (0, 16, 0, 15)        # table rows r0..r1, columns c0..c1: the buns, the hair, the face, the neck
LEG_TOP = 28                     # the legs: the table rows from here down
BODY_KEEP = {28: [(0, 3)], 29: [(0, 2)]}          # the free hand's fingers stay with the body
SHIN_ROWS = (30, 32)             # the rows the knees fold away (the death's kneel)
# the run: league_caitlyn's way (tools/art/fix_caitlyn_run_v2.py, the run the user approved). League's run traced here
# made her legs change length frame to frame (the leg swings in depth: a shin 3 to 8 squares on screen) and the legs on
# League's angles came out thick and folded - the user: 「这腿肯定是有大问题的」「腿变形啊」「我要的是模型不变形自然的交叉步
# 走路」「现在好多英雄都已经做好了啊 参考都不会吗」. So one leg is set in eight phases (RUN_PHASES: where its ankle is),
# its knee solved at the same thigh and shin length in every frame (RUN_LEG), and it is drawn square by square two
# squares wide in the leggings' colours (lit left, dark right: the idle's 'da'), the tan patch on the near knee, the
# design's own whole boot flat on the ankle; the far leg is the same phases four on, RUN_FAR squares right, so the feet
# cross every other step; the legs stay on the ground and the body steps down a row as a foot lands (RUN_STEP), the
# hips with it; the far leg drawn first with its outline ring, the near one over it, the body (the coat's panels) over
# both
RUN_HIP = (-1.0, -3.0)          # the near hip, squares from the standing point (under the belt, between the panels)
RUN_FAR = 3.0                   # the far leg: the near leg's drawing this many squares right
RUN_LEG = (4.3, 4.3)            # thigh and shin (hip -> knee -> the boot's cuff), the same in every frame
RUN_CUFF = 5                    # the boot's cuff row with the boot on the ground (squares under the standing point)
RUN_STEP = [1, 1, 0, 0, 1, 1, 0, 0]      # rows the body (and the hips) come down: as a foot lands, up as they pass
# one leg's eight phases: its ankle (the cuff's middle) in squares from the standing point, and how far it is lifted
RUN_PHASES = [(+3.0, 0),        # 1 the heel landing ahead of the hip
              (+1.0, 0),        # 2 planted, the body coming over it
              (-1.0, 0),        # 3 planted, sliding back under her
              (-3.5, 1),        # 4 pushing off behind, the heel up
              (-5.0, 3),        # 5 the heel lifting behind, the knee bent
              (-4.5, 4),        # 6 the heel up behind (the far boot shows behind the near leg)
              (+0.5, 3.5),      # 7 swung through, the knee forward, the foot tucked under her
              (+3.0, 1.5)]      # 8 reaching forward, about to land
LEGGINGS = ("#73234B", "#45183A")                    # lit, dark: the design's leggings
PATCH = ("#F2CC8F", "#AC8157")                       # the near knee's tan patch
# what stays of the design under the belt in the run (table rows: (first, last) columns): the coat's two panels and
# the hanging hand; the boots (rows 33-39) are cut whole with their outline
RUN_KEEP = {25: [(0, 9), (17, 19)], 26: [(0, 9), (17, 20)], 27: [(0, 9)], 28: [(0, 3)], 29: [(0, 2)]}
RUN_BOOTS = {"near": (33, 39, 0, 8), "far": (33, 39, 13, 22)}
# the idle: her own breath (import_native's shared cut would run through the upright rifle): everything above the legs
# sinks 0 0 1 1 1 1 0 0 rows over them (lowered), as league_viego's
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]


def table_mask(rows=None, box=None, cells=None):
    m = np.zeros((128, 128), bool)
    if rows:
        for r, (c0, c1) in rows.items():
            if r in _KEPT:
                m[OY + int(Rw(r)), OX + c0:OX + c1 + 1] = True
    if box:
        r0, r1, c0, c1 = box
        m[OY + int(Rw(r0)):OY + int(Rw(r1)) + 1, OX + c0:OX + c1 + 1] = True
    for r, c in cells or []:
        if r in _KEPT:
            m[OY + int(Rw(r)), OX + c] = True
    return m


class Rig:
    def __init__(self):
        self.D = K.Design(DESIGN)
        self.a = self.D.a
        self.out = self.D.outline
        op = self.a[..., 3] > 0
        self.rifle_m = table_mask(rows=RIFLE_ROWS, cells=RIFLE_EXTRA) & op
        self.forearm_m = table_mask(cells=FOREARM) & op & ~self.rifle_m
        self.arm_m = self.rifle_m | self.forearm_m
        self.head_m = table_mask(box=HEAD_BOX) & op & ~self.rifle_m
        legs = np.zeros((128, 128), bool)
        legs[OY + int(Rw(LEG_TOP)):] = True
        for r, spans in BODY_KEEP.items():
            for c0, c1 in spans:
                legs[OY + int(Rw(r)), OX + c0:OX + c1 + 1] = False
        self.legs_m = legs & op
        self.rifle = K.Part.from_canvas(self.a, self.rifle_m, GRIP)
        self.arm = K.Part.from_canvas(self.a, self.arm_m, ELBOW)

    # ---------------------------------------------------------------------------------------- building blocks
    def layer(self, m):
        out = np.zeros_like(self.a)
        out[m] = self.a[m]
        return out

    def body(self, rifle=True):
        m = (self.a[..., 3] > 0) & ~self.legs_m
        if not rifle:
            m &= ~self.arm_m
        return self.layer(m)

    def level_arm(self, c, dy=0):
        """The arm unit a quarter turn clockwise about the elbow (dy rows lower), its forearm one maroon band: the
        cuff's squares (each forearm square (r, c) of the table lands on (c + 2, 38 - r) about ELBOW) recoloured."""
        K.place(c, K.rot90(self.arm, 1), (ELBOW[0], ELBOW[1] + dy))
        sw = {K.rgb(a_): K.rgb(b_) for a_, b_ in LEVEL_RECOLOUR.items()}
        er, ec = int(Rw(20)), 18                       # the elbow's square (the turn's centre)
        for r, col in FOREARM:
            if r not in _KEPT:
                continue
            y, x = OY + er + (col - ec) + dy, OX + ec + (er - int(Rw(r)))
            got = tuple(int(v) for v in c[y, x, :3])
            if c[y, x, 3] and got in sw:
                c[y, x, :3] = sw[got]
        return c

    def rifle_level(self):
        """The rifle alone, level (the death's rifle on the ground)."""
        return K.rot90(self.rifle, 1)

    def lowered(self, upper, legs, dy):
        c = np.zeros_like(self.a)
        K.put(c, legs, 0, 0)
        K.put(c, upper, 0, dy)
        return c

    def lean(self, upper, dx_head, dx_chest):
        out = np.zeros_like(upper)
        r_head = OY + int(Rw(HEAD_BOX[1]))
        for y in range(upper.shape[0]):
            dx = dx_head if y <= r_head else (dx_chest if OY + 17 <= y <= OY + 22 else 0)
            out[y] = np.roll(upper[y], dx, 0) if dx else upper[y]
        return out

    def pose(self, rifle="up", dx=0, dy=0, low=0, lean=(0, 0)):
        upper = self.body(rifle=False)
        if rifle == "up":
            K.put(upper, self.layer(self.arm_m), 0, 0)
        elif rifle == "level":
            self.level_arm(upper)
        if lean != (0, 0):
            upper = self.lean(upper, *lean)
        c = self.lowered(upper, self.layer(self.legs_m), low)
        return K.shifted(c, dx, dy)

    # ---------------------------------------------------------------------------------------- the run
    def run_pieces(self):
        """The body above the legs (the design under the belt cut away but the coat's panels and the hand), the two
        boots with their tops' middles and heights. Cached."""
        if getattr(self, "_run", None) is not None:
            return self._run
        op = self.a[..., 3] > 0
        low = np.zeros((128, 128), bool)
        low[OY + int(Rw(25)):] = True
        for r, spans in RUN_KEEP.items():
            for c0, c1 in spans:
                low[OY + int(Rw(r)), OX + c0:OX + c1 + 1] = False
        body = self.layer(op & ~low & ~self.arm_m)      # the arm unit goes on level (League's run holds the rifle forward)
        boots = {}
        for leg, (r0, r1, c0, c1) in RUN_BOOTS.items():
            b = self.layer(table_mask(box=(r0, r1, c0, c1)) & op)
            ys, xs = np.nonzero(b[..., 3] > 0)
            top = ys.min()
            row = xs[ys == top]
            boots[leg] = (b, ((row.min() + row.max() + 1) / 2.0, float(top)), float(ys.max() + 1 - top))
        self._run = (body, boots)
        return self._run

    def run_leg(self, phase, dx, leg, step):
        """One leg at a phase: the knee solved at RUN_LEG, two squares wide along hip -> knee -> ankle, the design's
        boot flat with its cuff's middle on the ankle, one outline ring round both."""
        import math
        _, boots = self.run_pieces()
        hip = (PIVOT[0] + RUN_HIP[0] + dx + 0.5, PIVOT[1] + RUN_HIP[1] + step + 0.5)
        ax, lift = RUN_PHASES[phase]
        ank = (PIVOT[0] + ax + dx + 0.5, PIVOT[1] + RUN_CUFF + 0.5 - lift)
        lt, ls = RUN_LEG
        k1, _ = K.elbow(hip, ank, lt, ls, bend=-1)
        k2, _ = K.elbow(hip, ank, lt, ls, bend=1)
        knee = k1 if k1[0] >= k2[0] else k2                  # the knee bends forward
        lit, dark = (K.rgb(h) for h in LEGGINGS)
        cells = {}
        for p0, p1 in ((hip, knee), (knee, ank)):
            n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])) * 4) + 1
            steep = abs(p1[1] - p0[1]) >= abs(p1[0] - p0[0])
            for i in range(n + 1):
                x = p0[0] + (p1[0] - p0[0]) * i / n
                y = p0[1] + (p1[1] - p0[1]) * i / n
                xi, yi = int(math.floor(x)), int(math.floor(y))
                cells.setdefault((xi, yi), lit)
                cells.setdefault((xi + 1, yi) if steep else (xi, yi + 1), dark)
        if leg == "near":                     # the tan patch on her near knee (the design's)
            kx, ky = int(math.floor(knee[0])), int(math.floor(knee[1]))
            for q, col in (((kx, ky), PATCH[0]), ((kx + 1, ky), PATCH[1]), ((kx, ky + 1), PATCH[1])):
                if q in cells:
                    cells[q] = K.rgb(col)
        g = np.zeros_like(self.a)
        for (x, y), col in cells.items():
            g[y, x] = (*col, 255)
        boot, (mid, top), _ = boots[leg]
        K.put(g, K.shifted(boot, int(round(ank[0] - mid)), int(round(ank[1] - 0.5 - top))), 0, 0)
        m = g[..., 3] > 0
        p = np.pad(m, 1)
        g[~m & (p[2:, 1:-1] | p[:-2, 1:-1] | p[1:-1, 2:] | p[1:-1, :-2])] = (*self.out, 255)
        return g

    def run_frame(self, k):
        body, _ = self.run_pieces()
        step = RUN_STEP[k]
        c = np.zeros_like(self.a)
        K.put(c, self.run_leg((k + 4) % 8, RUN_FAR, "far", step), 0, 0)      # the far leg first
        K.put(c, self.run_leg(k, 0.0, "near", step), 0, 0)
        K.put(c, K.shifted(body, 0, step), 0, 0)
        self.level_arm(c, step)
        c[SOLES + 1:] = 0
        return c

    # ---------------------------------------------------------------------------------------- the death
    def kneel(self, n, dx=0):
        legs = self.layer(self.legs_m)
        r_hi = OY + int(Rw(SHIN_ROWS[1]))
        cut0 = r_hi - n + 1
        upper_legs = legs.copy()
        upper_legs[cut0:] = 0
        boots = legs.copy()
        boots[:r_hi + 1] = 0
        c = np.zeros_like(self.a)
        K.put(c, boots, 0, 0)
        K.put(c, upper_legs, 0, n)
        up = self.body(rifle=True)
        K.put(c, up, 0, n)
        return K.shifted(c, dx, 0)

    def lying(self):
        fig = self.layer((self.a[..., 3] > 0) & ~self.rifle_m)
        part = K.Part.from_canvas(fig, fig[..., 3] > 0, (PIVOT[0] + 0.5, SOLES + 0.5))
        turned = K.rot90(part, 1)
        c = np.zeros_like(self.a)
        K.place(c, turned, (PIVOT[0] - 18 + 0.5, SOLES + 0.5))
        ys, xs = np.nonzero(c[..., 3])
        c = K.shifted(c, 0, SOLES - ys.max())
        tmp = np.zeros_like(self.a)
        K.place(tmp, self.rifle_level(), (40, 40))
        gy, gx = np.nonzero(tmp[..., 3])
        ys, xs = np.nonzero(c[..., 3])
        K.put(c, K.shifted(tmp, xs.max() - gx.min() - 8, SOLES - gy.max()), 0, 0, under=True)
        return c

    # ---------------------------------------------------------------------------------------- the strips
    def build(self, tag):
        P = self.pose
        if tag == "idle":
            return [P(low=n) for n in BREATH]
        if tag == "run":
            return [self.run_frame(k) for k in range(8)]
        if tag == "attack":
            return [P(), P(rifle="level"), P(rifle="level", dx=-1), P(rifle="level"), P()]
        if tag == "skill":
            return [P(low=1), P(rifle="level", low=1), P(rifle="level", low=1, dx=-1),
                    P(rifle="level", dx=-2, low=1), P()]
        R = lambda k, dx, dy: K.shifted(self.run_frame(k), dx, dy)     # a stride of the run, moved whole
        if tag == "skill2":                   # E forward: crouch, the run's long stride lunging forward, its landing
            return [P(low=1), R(0, 2, -1), R(1, 1, 0), P()]
        if tag == "skill2_back":              # E back: crouch, the run's tucked hop back, the landing
            return [P(low=1), R(3, -2, -1), P(dx=-1, low=1), P()]
        if tag == "ult":                      # R: crouch, a hop (the run's tucked frame), the nova fired level
            return [P(low=1), R(3, 0, -1), P(low=1, rifle="level", dx=-1), P()]
        if tag == "hit":
            return [P(dx=-2), P(dx=-1)]
        if tag == "dead":
            return [P(dx=-1), P(dx=-1, low=1), self.kneel(2, dx=-1), self.kneel(3, dx=-1),
                    self.lying(), self.lying(), self.lying(), self.lying()]
        raise KeyError(tag)

    def head_keep(self, f):
        hm = self.head_m
        ys, xs = np.nonzero(hm)
        best = None
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                yy, xx = ys + dy, xs + dx
                ok = (yy >= 0) & (yy < 128) & (xx >= 0) & (xx < 128)
                same = (f[yy[ok], xx[ok]] == self.a[ys[ok], xs[ok]]).all(-1).sum()
                if best is None or same > best[0]:
                    best = (same, dy, dx)
        _, dy, dx = best
        keep = np.zeros(hm.shape, bool)
        yy, xx = ys + dy, xs + dx
        ok = (yy >= 0) & (yy < 128) & (xx >= 0) & (xx < 128)
        keep[yy[ok], xx[ok]] = True
        return keep

    def finished(self, frames, tag):
        out = []
        for f in frames:
            keep = None if tag == "dead" else self.head_keep(f)
            g = K.finish(f, self.out, SOLES, keep=keep)
            # finish leaves the kept head's light edges open (complete_outline skips light squares it may not touch):
            # the outline goes outside them too - only clear squares are filled
            g, _, _ = K.strips.complete_outline(g, color=tuple(self.out), feet=SOLES)
            for h in K.holes(g):
                if len(h) <= 6:
                    for y, x in h:
                        g[y, x] = (*self.out, 255)
            out.append(g)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--tags", default=",".join(TAGS))
    a = ap.parse_args()
    rig = Rig()
    built = {}
    for tag in a.tags.split(","):
        built[tag] = rig.finished(rig.build(tag), tag)
    for tag, frs in built.items():
        rows = K.audit(frs, rig.a, rig.out, SOLES)
        print(f"{tag:12s}", " ".join(f"{i + 1}:{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}"
                                     for i, r in enumerate(rows)))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, f) for t, f in built.items()], os.path.join(a.review, "zeri_rig_frames.png"), z=6,
                       soles=SOLES)
        K.review_gif([(t, f) for t, f in built.items()], MS, os.path.join(a.review, "zeri_rig_actions.gif"), z=6)
    if len(built) == len(TAGS):
        bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        print("check:", "identical" if a.check and not bad else (bad if a.check else "written"))


if __name__ == "__main__":
    main()

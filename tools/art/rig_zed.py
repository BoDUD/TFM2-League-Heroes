#!/usr/bin/env python3
"""Zed's action strips posed from the approved design's own parts (2026-10-09): the casting body = the idle's.

    python tools/art/rig_zed.py [--check] [--review DIR] [--parts PNG]

Codex's step-2 delivery (assets/source/zed/codex_strips/) pasted the design's head on bodies it drew anew: bigger than
the idle in W, Q and E, the legs not the design's (its own HANDOFF: design_legs_square_for_square false), the wrist
blades unclear, old outlines possible round the pasted heads. The user: 「有问题的地方帮我修复」. So, as for Rengar
(rig_rengar.py), every frame is the design with only what the action moves moved, nothing resampled (no-deformation
rule: translation, quarter turns, mirrors, whole-row shifts, layering):
- the parts are cut square for square with the outline squares that ring them alone: the two FOREARMS (the gold bracer
  with its silver spurs and the two wrist blades; the red sleeve and the pauldron above stay the torso's), the two
  LOWER LEGS (the greaves and the pointed boots) and the head (work/zd/head_zd.py's ranges: the hood and the helmet);
- forearm poses are rigid units turned about the elbow (the bracer's top): HANG (as drawn), OUT (a quarter turn: the
  blades pointing right - or, for the image-left arm, left), UP (mirrored about the elbow: raised, the blades up),
  IN (pulled to the chest), FWD (the image-left forearm brought across the body, its blades pointing right), BACK (the
  image-right forearm turned to point left behind the body), LOW (OUT held lower);
- whole-figure moves: a lunge / recoil (columns), a hop (rows), a crouch (everything above the boots sunk over them,
  layering), the lower legs swung back or tucked (rigkit.swing_leg: whole rows);
- the death: struck back, sunk to his knees, then the figure turned exactly a quarter clockwise about the feet (face
  down, the head to the right, League's fall forward);
- the run: a cross-step after League's Zed_run on two-part legs (thigh, shin, the boot whole), the near forearm
  swung back whole with its own edge (run_frames); the body drops a row at each mid-stance.
Writes assets/source/native/zed_<tag>.png (8x, 112x96 cells, soles on cell row 81) and zed_cells.json; then
tools/art/import_native.py. --check compares instead of writing; --review writes a review sheet and GIF.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "zed_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
OUT = K.rgb("#100F19")               # the grid design's outline
CELL = (112, 96)
CELL_PIVOT = (56, 70)            # the soles on cell row 81 (the references' feet line)
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)

# the head piece: per row (first, last) column on the design canvas (= work/zd/head_zd.py)
# 2026-10-09 design B (Codex's grid redraw after picture A, assets/source/zed/codex_grid/zed-grid-B_1x.png, de-speckled by
# work/zd4/polish_b_zd.py): the hood's point row 54, the mask rows 62-66 with the eyes at (66,64) (68,64), the scarf
# rows 65-70, the back blades rows 56-66 (part of the body), bracers rows 73-80, claws down to row 92, legs from
# row 81, boots rows 95-99
HEAD = {54: (62, 64), 55: (61, 65), 56: (61, 65), 57: (60, 66), 58: (60, 66), **{y: (59, 70) for y in range(59, 70)},
        70: (60, 69)}
L_ELBOW = (53.5, 76.0)           # (x, y): the top of the image-left bracer
R_ELBOW = (74.5, 78.0)           # the top of the image-right bracer
KNEE_ROW, FEET_ROW = 90, 95      # the lower legs: the greaves (93-95) and the boots (96-98)
TABARD = set()   # the tabard's hem squares among the near leg's rows
# the run's whole legs (rows from, first and last column; never a forearm or the tabard's reds and golds) and their
# hips (the thighs lean from there) - all on the full design
RUN_LEGS = {"far": (77, 56, 63), "near": (85, 64, 75)}
RUN_HIPS = {"far": 77, "near": 80}               # the near hip under the tabard

# Smaller (the user, 2026-10-10: 「做的挺好的 劫 就是有点太大了」, then 「还可继续缩一点」): the design loses whole rows
# and columns ONCE (as rig_xinzhao.py's SCALE: cut afterwards from the finished frames, one cut would run through a
# different part of him in every frame as he breathes and crouches) before any action is posed from it. Every part is
# cut on the full design and shrunk with it; every point and row above is read on the full design and moved with it
# (_shrink_globals). The first cut (90%, tools/art/shrink_frames.py's plan_tag) took column 58 through the far shin:
# its one-square ankle row lost its colour (「腿部有点奇怪吧？没改好？模型丢失」). So the lines are picked by hand
# (85%, 47 -> 40 rows, 31 -> 28 columns), each where the rows or columns on both sides already draw the same:
#   rows    57 (the back blades' diagonal, one step steeper), 67 and 73 (the chest, the elbows), 84 (= row 83), 87
#           (= 86), 91 (the claw tips' middle row) and 94 (the far shin's narrow ankle row: the shin stays two wide);
#   columns 59 (the far boot one square shorter), 70 and 73 (the near side of the chest and the near boot) -
# never the hood's point (61-63), the eyes and mask (64-68), the claws (49-55, 74-78) or the far shin (56-58).
SCALE = 0.85
CUT_ROWS = (57, 67, 73, 84, 87, 91, 94)
CUT_COLS = (59, 70, 73)
SHRUNK_PLAN = None
FULL_KNEE_ROW = KNEE_ROW
# the outline closed from this luminance up in every frame (design_zed2.DARK): his blue steel, reds and dark red edge
# the silhouette too
DARK = 30
# the wrist blades redrawn on the 85% design (2026-10-10, the user: 「武器做的太长了吧」, then 「只能说武器形状做的不像」).
# League's Zed (tools/lol/native_pose.py at game size) hangs two straight parallel blades from each bracer, their points
# by the knees; C drew the near (image-right) one as a single one-square line that kinked into a fork and hung to the
# boot, and the far one's two points split apart. Now each arm has two straight blades a column apart, silver with white
# points: the near ones from under the bracer in columns 73 and 75 to rows 92-93 (three rows shorter), the far ones'
# points straight down in columns 52 and 54. Rows top to bottom from (row, first column); "." clears a square; every
# square goes with that forearm, but BLADES_BODY (the tabard's hem square the near blade passes in front of: its
# outline now) stays the body's.
BLADES = {"rfore": (88, 72, ["06060.", "06060.", "06060.", "08060.", "08080.", ".0080.", "...0..", "......", "......",
                             "......"]),
          "lfore": (91, 51, ["08080", ".0.0..", "......"])}
BLADES_BODY = {(92, 72)}


def map_x(x):
    """A canvas column (or point) on the shrunk design: the removed columns between it and the pivot close in."""
    if SHRUNK_PLAN is None:
        return x
    cs = [PIVOT[0] + c for c in SHRUNK_PLAN["cols"]]
    if x < PIVOT[0]:
        return x + sum(1 for c in cs if x < c < PIVOT[0])
    return x - sum(1 for c in cs if PIVOT[0] < c <= x)


def map_y(y):
    """A canvas row (or point): down one for every removed row under it (all above the soles, which stay)."""
    if SHRUNK_PLAN is None:
        return y
    return y + sum(1 for r in SHRUNK_PLAN["rows"] if PIVOT[1] + r > y)


def shrunk(c):
    """A 128x128 canvas (image or mask) without the plan's rows and columns, the soles on their row."""
    if SHRUNK_PLAN is None:
        return c
    gone_r = {PIVOT[1] + r for r in SHRUNK_PLAN["rows"]}
    gone_c = {PIVOT[0] + q for q in SHRUNK_PLAN["cols"]}
    out = np.zeros_like(c)
    for y in range(c.shape[0]):
        if y in gone_r:
            continue
        ny = map_y(y)
        for x in range(c.shape[1]):
            if x not in gone_c and 0 <= ny < c.shape[0]:
                nx = map_x(x)
                if 0 <= nx < c.shape[1]:
                    out[ny, nx] = c[y, x]
    return out


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


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        op = d[..., 3] > 0
        ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
        colour = op & ~ink
        R, C = np.mgrid[0:128, 0:128]
        # design C (Codex's flat redraw of B, design_zed2.py): the claws hang in columns 51-54; columns 56-57 under the
        # bracer are the thigh's outer edge (they had travelled with the forearm: a notch in the thigh)
        lfore_c = colour & (R >= 76) & (R <= 94) & (((C <= 57) & (R <= 82)) | (C <= 55))
        # the tabard hem reaches column 72 at rows 87-89 (its red travelled with the forearm as a red bar under the
        # blades): the forearm keeps to 72+ and never takes the tabard's reds
        red = np.zeros((128, 128), bool)
        for col in ("#AA1027", "#470C1A"):
            red |= (d[..., :3] == np.array(K.rgb(col), np.uint8)).all(-1)
        rfore_c = colour & (R >= 78) & (R <= 97) & (C >= 72) & ~red
        tab = np.zeros((128, 128), bool)
        for y, x in TABARD:
            tab[y, x] = True
        lleg_c = colour & (R >= FULL_KNEE_ROW) & (C >= 57) & (C <= 64) & ~lfore_c
        rleg_c = colour & (R >= FULL_KNEE_ROW) & (C >= 65) & (C <= 74) & ~tab & ~rfore_c
        head_c = colour & region(HEAD)
        silver = np.zeros((128, 128), bool)        # the back ornament's prongs above the brows ride on the body
        for y, x in zip(*np.nonzero(head_c)):
            if False:
                silver[y, x] = True
        head_c &= ~silver
        self.colour = colour
        parts_c = {"lfore": lfore_c, "rfore": rfore_c, "lleg": lleg_c, "rleg": rleg_c, "head": head_c}
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
        self.body = d.copy()
        for k in ("lfore", "rfore", "lleg", "rleg"):
            self.body[self.masks[k]] = 0
        # the run's whole legs: the far one from its hip between the claws and the tabard, the near one below the
        # tabard's hem (the lower legs with them)
        cloth = red.copy()
        for col in ("#D4A64B", "#A17231"):
            cloth |= (d[..., :3] == np.array(K.rgb(col), np.uint8)).all(-1)
        run_c = {}
        for k, fore, low in (("far", "lfore", lleg_c), ("near", "rfore", rleg_c)):
            r0, c0, c1 = RUN_LEGS[k]
            run_c[k] = (colour & (R >= r0) & (C >= c0) & (C <= c1) & ~self.masks[fore] & ~cloth) | low
        run_c["near"] &= ~run_c["far"]
        rest = colour & ~run_c["far"] & ~run_c["near"]
        self.run = {k: run_c[k] | ring(run_c[k], rest | run_c[o]) for k, o in (("far", "near"), ("near", "far"))}
        if SHRUNK_PLAN is not None:            # everything cut on the full design, then made smaller as one
            d = shrunk(d)
            self.colour = shrunk(colour)
            self.masks = {k: shrunk(m) for k, m in self.masks.items()}
            self.body = shrunk(self.body)
            self.run = {k: shrunk(m) for k, m in self.run.items()}
            # a removed line at a turn of the outline opens it: closed once here (and the notches that walls in
            # filled), so the idle's copies and the posed frames leave the import alike; a square it adds goes with
            # the one part whose colour alone it touches (the far shin lost its outline column with column 59: the new
            # one would have stayed behind in the body when the leg moved), any other with the body
            fin = K.finish(d, OUT, SOLES, pinholes=2, dark=DARK)
            new = (fin != d).any(-1)
            col = (fin[..., 3] > 0) & ~(fin[..., :3] == np.array(OUT, np.uint8)).all(-1)
            claim(self.masks, ("lfore", "rfore", "lleg", "rleg"), new, col)
            claim(self.run, ("far", "near"), new, col)
            part = np.zeros_like(new)
            for k in ("lfore", "rfore", "lleg", "rleg"):
                part |= self.masks[k]
            self.body[new & ~part] = fin[new & ~part]
            d = fin
            self.design = d
            self.blades()
            self.legs_alike()
            d = self.design
        self.lfore = K.Part.from_canvas(d, self.masks["lfore"], L_ELBOW)
        self.rfore = K.Part.from_canvas(d, self.masks["rfore"], R_ELBOW)

    def blades(self):
        """BLADES painted on the 85% design, each square given to its forearm (or kept by the body)."""
        colour = {"0": OUT, "6": K.rgb("#9DAAC4"), "8": K.rgb("#DFE9F4")}
        d = self.design
        for key, (r0, c0, rows) in BLADES.items():
            for dy, line in enumerate(rows):
                for dx, ch in enumerate(line):
                    y, x = r0 + dy, c0 + dx
                    for m in self.masks.values():
                        m[y, x] = False
                    if ch == ".":
                        d[y, x] = 0
                        self.body[y, x] = 0
                        continue
                    d[y, x, :3], d[y, x, 3] = colour[ch], 255
                    if (y, x) in BLADES_BODY:
                        self.body[y, x] = d[y, x]
                    else:
                        self.body[y, x] = 0
                        self.masks[key][y, x] = True

    def legs_alike(self):
        """The far lower leg becomes a copy of the near one (the user, 10-10: 「腿左右也要一样吧」 - C drew the far shin
        as a light 2-wide greave with a 3-wide boot and the near one as a dark trouser leg with a 9-wide toed boot):
        every square of the near leg part from the knee row down, LEG_COPY columns left, in place of everything in
        the far leg's columns there (the old greave, boot and its outline column the box mask had left to the body);
        the part masks and the run's far leg follow."""
        d = self.design
        R, C = np.mgrid[0:128, 0:128]
        old = (R >= KNEE_ROW) & (C >= LEG_FAR_COLS[0]) & (C <= LEG_FAR_COLS[1]) & ~self.masks["lfore"]   # not the claw tips
        src = self.masks["rleg"] & (R >= KNEE_ROW) & (d[..., 3] > 0)
        new = np.zeros_like(src)
        ys, xs = np.nonzero(src)
        new[ys, xs - LEG_COPY] = True
        assert not (new & ~old).any(), "the copy leaves the far leg's columns"
        for m in list(self.masks.values()) + list(self.run.values()):
            m[old] = False
        d[old] = 0
        self.body[old] = 0
        d[ys, xs - LEG_COPY] = self.design[ys, xs]
        # the shin's right outline at the knee row was the tabard hem's on the near side: closed here, not at import
        ink = np.zeros_like(new)
        for dy, dx in N4:
            ink |= np.roll(np.roll(new & (d[..., :3] != np.array(OUT, np.uint8)).any(-1), dy, 0), dx, 1)
        ink &= old & (d[..., 3] == 0)
        d[ink, :3], d[ink, 3] = OUT, 255
        new |= ink
        self.masks["lleg"] |= new
        self.run["far"] |= new

    def overlay(self, path, z=12):
        """The design with every part tinted (forearms red / green, legs cyan / magenta, head blue)."""
        d = self.design.astype(float)
        tint = {"rfore": (255, 0, 0), "lfore": (0, 200, 0), "lleg": (0, 220, 255), "rleg": (255, 0, 255),
                "head": (60, 90, 255)}
        out = d.copy()
        for k, col in tint.items():
            m = self.masks[k]
            out[m, :3] = d[m, :3] * 0.45 + np.array(col) * 0.55
        sub = out[58:101, 44:82].astype(np.uint8)
        Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST).save(path)


def claim(masks, keys, new, col):
    """Each `new` square whose coloured 8-neighbours all belong to one of masks[keys] joins that mask."""
    for y, x in zip(*np.nonzero(new)):
        owners = set()
        for a, b in N8:
            q = (y + a, x + b)
            if col[q]:
                owners.add(next((k for k in keys if masks[k][q]), None))
        if len(owners) == 1 and None not in owners:
            masks[owners.pop()][y, x] = True


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
    # closed until nothing changes: a square the closure adds can give a one-square line a second side, which the
    # import's own closing pass then outlined, walling in pinholes (the low forearm's frames at 85%)
    out = a
    for _ in range(4):
        nxt = K.finish(out, OUT, SOLES, keep=~near, pinholes=pinholes, dark=DARK)
        nxt[~near] = a[~near]
        if np.array_equal(nxt, out):
            break
        out = nxt
    # an outline square the move left touching no colour goes too (the design has none) - unless it is walled in by
    # outline all round: then it is where three outlines meet (the crouch's 2-row sink brings the near claw's tip
    # down onto the boot's toe and the shin's edge at 85%), and clearing it would open a pinhole
    op = out[..., 3] > 0
    walled = np.ones_like(op)
    for dy, dx in N4:
        walled &= np.roll(np.roll(op, dy, 0), dx, 1)
    out[K.orphan_outline(out, OUT) & ~walled] = 0
    return out


def arm_unit(P, which, how):
    """(Part, joint offset from the elbow, drawn behind the body?) for a forearm pose."""
    u = P.rfore if which == "r" else P.lfore
    if how in (None, "hang"):
        return u, (0, 0), False
    if how == "out":             # the image-right blades pointing right / the image-left ones pointing left
        return (K.rot90(u, 3) if which == "r" else K.rot90(u, 1)), (0, 1), which == "l"
    if how == "low":             # pointing right, held lower (a low throw, a follow-through)
        return K.rot90(u, 3), (0, 4), False
    if how == "up":              # raised beside the helmet: the forearm mirrored about the elbow, the blades up
        return u.flip_v(), ((1, -5) if which == "r" else (-1, -4)), which == "l"
    if how == "in":              # pulled up toward the chest
        return u, ((-3, -2) if which == "r" else (3, -2)), which == "l"
    if how == "fwd":             # the image-left forearm brought across in front, its blades pointing right
        return K.rot90(u, 3), (9, 3), False
    if how == "back":            # the image-right forearm turned to point left, behind the body
        return K.rot90(u, 1), (-2, 1), True
    raise ValueError(how)


def build(P, f):
    """One frame from a pose dict: r / l (forearm poses), rdy / ldy (forearm rows), legs ((dx, lift) left, right),
    sink (rows, the boots stay), dx / dy (the whole figure)."""
    c = P.body.copy()
    legs_spec = f.get("legs", ((0, 0), (0, 0)))
    (lx, ll), (rx, rl) = legs_spec
    for m, dx, lift in ((P.masks["lleg"], lx, ll), (P.masks["rleg"], rx, rl)):
        K.put(c, K.swing_leg(P.design, m, KNEE_ROW - 1, FEET_ROW, dx, lift), 0, 0, under=True)
    behind, front = [], []
    for which, el in (("l", L_ELBOW), ("r", R_ELBOW)):
        u, (ox, oy), back = arm_unit(P, which, f.get(which))
        at = (el[0] + ox, el[1] + oy + f.get(which + "dy", 0))
        (behind if back else front).append((u, at))
    for u, at in behind:
        K.place(c, u, at, under=True)
    for u, at in front:
        K.place(c, u, at)
    if f.get("sink"):
        n = f["sink"]
        R = np.arange(128)[:, None]
        feet_m = (P.masks["lleg"] | P.masks["rleg"]) & (R >= FEET_ROW)
        moved_legs = any(v for pair in legs_spec for v in pair)
        feet = np.zeros_like(c)
        top = c.copy()
        if not moved_legs:
            feet[feet_m] = P.design[feet_m]
            top[feet_m] = 0
        c = K.put(K.shifted(top, 0, n), feet, 0, 0)     # the boots in front of the sunk greaves: the toes stay
        c[SOLES + 1:] = 0
    if f.get("mirror"):                     # the whole figure turned to face left (League's Q wind-up turns his
        c = mirrored(c)                      # back, E spins): a lossless flip about the standing column
    if f.get("dx") or f.get("dy"):
        c = K.shifted(c, f.get("dx", 0), f.get("dy", 0))
    return c


def mirrored(c):
    m = c[:, ::-1].copy()                    # x -> 127 - x: the standing column 64 lands on 63
    return K.shifted(m, 1, 0)


def frame(P, f):
    if f is None:
        return P.design.copy()
    c = build(P, f)
    ref = mirrored(P.design) if f.get("mirror") else P.design
    return finish_near(c, K.shifted(ref, f.get("dx", 0), f.get("dy", 0)))


# ------------------------------------------------------------------------------------------------ the actions
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill_e", "ult", "hit", "dead"]
# frame lengths = assets/source/zed/poses.json (the release frames land on the kit's ticks: attack 9, W 3, Q 10, E 8,
# R 6)
MS = {"idle": [140] * 8, "run": [120] * 8, "attack": [60, 50, 40, 80, 100, 110], "skill": [50, 60, 80, 90],
      "skill2": [60, 50, 60, 80, 100, 120], "skill_e": [50, 40, 43, 70, 70, 100],
      "ult": [50, 50, 80, 80, 80, 90, 110], "hit": [120, 120], "dead": [100, 100, 120, 150, 200, 150, 150, 500]}
TUCK = ((-1, 1), (-1, 1))        # the lower legs trailing back in the dash (design B: a boot swung 3 came off the shin)
LUNGE = ((-3, 0), (1, 0))        # the back leg swung back, the front one a column forward
POSES = {
    # League's attack1 (head +9 rows at the stab): coiled low, the stab a low lunge forward, rising back
    "attack": [dict(r="in", sink=1), dict(r="in", dx=-1, sink=2), dict(r="out", dx=1, sink=1),
               dict(r="out", dx=3, sink=4, legs=LUNGE), dict(r="out", dx=2, sink=3, legs=LUNGE), dict(sink=1)],
    # W: the near arm raised by the head with a small rise, flung forward, the follow-through low
    "skill": [dict(r="up"), dict(r="out", dx=1, dy=-1), dict(r="low", dx=1, sink=1), None],
    # Q (League turns his back winding up, then throws from a deep crouch, head +23): the hand to the ornament, the
    # wind-up turned away (mirrored), the throw crouched low and lunging, rising
    "skill2": [dict(r="up", sink=1), dict(r="up", mirror=True, sink=1), dict(r="in", mirror=True, sink=2, dx=1),
               dict(r="low", l="out", sink=5, dx=3, legs=LUNGE), dict(r="low", sink=3, dx=2, legs=LUNGE), dict(sink=1)],
    # E (a leaping spin, both blades out): pulled in, the crouch, the leap forward with the blades out, mid-spin
    # turned away in the air, facing again, the landing crouch
    "skill_e": [dict(r="in", l="in"), dict(r="in", l="in", sink=2), dict(r="out", l="out", dx=2, dy=-2, legs=TUCK),
                dict(r="out", l="out", mirror=True, dy=-3, legs=TUCK), dict(r="out", l="out", dx=-1, dy=-1, legs=TUCK),
                dict(r="out", l="hang", sink=2)],
    # R (the lead-in coils back, the dash, the strike a deep lunging crouch, head +12): the crouch, the coil back,
    # the dash with both blades forward, still dashing, the low strike, the landing crouch, rising
    "ult": [dict(r="in", l="in", sink=1), dict(r="in", l="in", dx=-2, sink=2),
            dict(r="out", l="fwd", dx=3, dy=-2, legs=TUCK), dict(r="out", l="fwd", dx=5, dy=-1, legs=TUCK),
            dict(r="out", l="fwd", dx=4, sink=4, legs=LUNGE), dict(r="low", l="out", dx=3, sink=3, legs=LUNGE),
            dict(r="out", l="out", dx=1, sink=1)],
    "hit": [dict(l="out", r="back", dx=-2), dict(dx=-1)],
}


def lying(P, above):
    """The whole figure (arms hanging) turned exactly a quarter clockwise about the feet: face down, the head to the
    right (League's fall forward), `above` rows over the ground."""
    fig = K.Part.from_canvas(P.design, P.design[..., 3] > 0, (64.0, 100.0))
    t = K.turn(fig, -90)
    c = np.zeros_like(P.design)
    K.place(c, t, (60.0, 100.0))
    low = int(np.nonzero(c[..., 3].any(1))[0].max())
    c = K.shifted(c, 0, SOLES - above - low)
    c[SOLES + 1:] = 0
    return K.finish(c, OUT, SOLES, keep=None, pinholes=4, dark=DARK)


def dead(P, k):
    """Struck back, sinking to his knees, kneeling slumped, then falling forward face down."""
    steps = [dict(dx=-1, l="out"), dict(dx=-1, sink=2), dict(sink=4, legs=((-3, 0), (0, 0))),
             dict(sink=5, legs=((-3, 0), (0, 0)), r="low"), dict(sink=5, legs=((-3, 0), (0, 0)), r="low")]
    if k < len(steps):
        return frame(P, steps[k])
    return lying(P, [3, 0, 0][k - len(steps)])


# the run (League's pace: Zed_run cycles in 0.968 s -> 8 x 120 ms), a cross-step (the user, 2026-10-10: 「走路有交叉步没」,
# then 「像奥拉夫那样给 Codex 准备一个跑步腿部的素材包，照英雄联盟的跑姿画交叉步」). Codex's redraw on the guide
# (assets/source/zed/RUN_CROSS.md) kept the image-right boot planted in 7 of 8 frames, creeping forward from +2 to +5
# while the other leg kicked - a skate - and added squares beside the right claw; the user: 「灵活利用工具吧 还有走路别
# 导致武器变形 codex已经犯了这个问题」, 「修复到完美版本再喊我review」. So the legs are the design's own again, each as a
# two-part leg per frame (knee_dx, boot_dx, lift): the thigh's rows shifted in proportion from the hip down to knee_dx
# at the knee, the shin's rows leaning on from knee_dx to boot_dx, the boot's rows (BOOT_TOP down) moved whole -
# unbent - and the shin + boot raised `lift` rows behind the thigh (a bent knee: its top hides behind the thigh).
# League's phase (tools/lol/pose_joints.py): the near (image-right) boot planted in frames 7, 8, 1, 2 sliding back
# 2 a frame, pushed off behind the far leg in 3 and kicked up behind it in 4 - the cross: the near leg in front of
# the far one, its boot behind the far boot - then the knee comes through in 5 and the foot reaches in 6; the far
# boot planted in 3-6 sliding back 2 a frame, pushed off in 7, kicked up behind the claws in 8, through in 1 and
# reaching in 2. The boots change order twice a cycle (the far one ahead in 2-4), stand at most 12 apart, one is
# always on the ground, and no two boots stack. The near forearm swings a column back over the tabard while the near
# leg is forward (6-8, 1), whole (run_fore: the claws exactly as drawn - the old run sheared their rows) and with its
# own edge; it never swings forward or the far one at all: either opened a gap at the tabard's / torso's edge that
# only made-up squares could fill (an extra square beside the first claw, a red tabard column, a dark blot at the far
# elbow). The body drops a row at each mid-stance.
RUN_STEPS = {
    # (knee_dx, boot_dx, lift) from each leg's hip. The user, 10-10: 「交叉步还能明显一点吗」 - the near boot had stayed
    # 8-16 columns ahead of the far one in every frame. League's Zed_run has the far foot ahead in frames 2-5; here in 3
    # and 4 the far boot lands 1-3 columns ahead of the near one and the near heel is kicked up behind across the far
    # leg (drawn over it, up 4-5). The hips stay put (moving the far one in tucked its thigh's top under the tabard:
    # 「腿和腰这里有点变形」) - the legs lean in from the hip, the shin at most 3 columns more than the thigh
    # the near boot stays left of the near blades until frame 7 (in 6, sunk 4 rows, its toe had met the blade tips:
    # 「右手武器看起来有点变形」)
    "near": [(0, 0, 0), (-1, -2, 0), (-3, -7, 4), (-3, -7, 5), (-1, -3, 3), (0, -3, 2), (1, 2, 0), (1, 1, 0)],
    "far": [(1, -1, 3), (3, 5, 1), (3, 6, 0), (2, 4, 0), (1, 2, 0), (0, 0, 0), (0, -2, 3), (0, -3, 5)],
}
RUN_HIP_DX = {"near": [0] * 8, "far": [0] * 8}
BOOT_TOP = 97                    # the boots' top row (full design): rows from here move whole
LEG_COPY = 10                    # the far lower leg = the near one this many columns left (85% canvas, legs_alike)
LEG_FAR_COLS = (54, 62)          # the far lower leg's columns on the 85% canvas (cleared before the copy)
DROP = [3, 4, 0, 0, 3, 4, 0, 0]           # the body (and the thighs) sunk: League's hip, high at a landing
RUN_ARM_DY = [0, -1, 0, 0, 0, -1, 0, 0]  # the forearms a row behind the drop at its lowest (the claws off the ground)
RUN_ARM = [0, 0, 0, 0, -1, -1, -1, -1]         # the near forearm's column per frame (back while its leg is ahead)


def run_leg(P, side, knee_dx, boot_dx, lift, drop=0, hip_dx=0):
    """One leg of the run: the thigh leaning to knee_dx at the knee, the shin on to boot_dx, the boot whole, the shin
    + boot raised `lift` rows behind the thigh; the thigh sinks `drop` rows with the body over the shin's top (a bent
    knee - left where it was, the hip end walled in the gap between the far forearm and the torso: a dark blot)."""
    d = P.design
    hip = RUN_HIPS[side]
    thigh = np.zeros_like(d)
    low = np.zeros_like(d)
    for r, c in zip(*np.nonzero(P.run[side] & (d[..., 3] > 0))):
        if r < KNEE_ROW:
            sh = hip_dx + int(np.floor(knee_dx * max(0, r - hip) / max(1, KNEE_ROW - hip) + 0.5))
            if 0 <= c + sh < 128:
                thigh[r + drop, c + sh] = d[r, c]
        else:
            t = min(1.0, (r - KNEE_ROW) / max(1, BOOT_TOP - KNEE_ROW))
            sh = hip_dx + int(np.floor(knee_dx + (boot_dx - knee_dx) * t + 0.5))
            if 0 <= c + sh < 128 and 0 <= r - lift < 128:
                low[r - lift, c + sh] = d[r, c]
    return K.put(thigh, low, 0, 0, under=True)


def run_fore(P):
    """The near forearm whole for the run: its squares, the body squares it walls in (the dark red under the bracer)
    and copies of the outline squares beside it that it shares with the body (the body keeps its own), so a column
    back over the tabard it brings its own edge and leaves no hole."""
    d = P.design
    m = P.masks["rfore"].copy()
    op = d[..., 3] > 0
    ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
    walled = op & ~m
    for dy, dx in N4:
        walled &= np.roll(np.roll(m, -dy, 0), -dx, 1)
    m |= walled
    beside = np.roll(m & ~ink, 1, 1) | np.roll(m & ~ink, -1, 1)
    whole = m | (ink & beside)
    part = np.zeros_like(d)
    part[whole] = d[whole]
    return part, walled


def run_frames(P):
    out = []
    fore, walled = run_fore(P)
    for k in range(8):
        legs = np.zeros_like(P.design)
        # the far (image-left) leg drawn first, the near one over it, both under the body (the tabard's hem and the
        # claws hang in front of them)
        K.put(legs, run_leg(P, "far", *RUN_STEPS["far"][k], drop=DROP[k], hip_dx=RUN_HIP_DX["far"][k]), 0, 0)
        K.put(legs, run_leg(P, "near", *RUN_STEPS["near"][k], drop=DROP[k], hip_dx=RUN_HIP_DX["near"][k]), 0, 0)
        top = P.body.copy()
        top[P.run["far"] | P.run["near"] | walled] = 0
        K.place(top, P.lfore, (L_ELBOW[0], L_ELBOW[1] + RUN_ARM_DY[k]), under=True)
        K.put(top, fore, RUN_ARM[k], RUN_ARM_DY[k])
        c = K.put(K.shifted(top, 0, DROP[k]), legs, 0, 0, under=True)
        c[SOLES + 1:] = 0
        # finished only near what moved, as the actions (the old run kept every row above the hips as drawn)
        out.append(finish_near(c, K.shifted(P.design, 0, DROP[k])))
    return out


# the idle breathes here (as league_rengar's): the shared idle_breathe cut a row through the wrist blades (they hang to
# the shins) and shortened them as he bobbed, so the whole figure but the boots sinks 0 0 1 2 2 2 1 0 rows over the
# boots (layering, like the crouch), the forearms and their blades with it, rigid; the base game's pace (8 x 140 ms);
# import_native skips him (BREATHE_SKIP).
BREATH = [0, 0, 1, 2, 2, 2, 1, 0]


def frames(P, tag):
    if tag == "idle":
        return [P.design.copy() if n == 0 else frame(P, dict(sink=n)) for n in BREATH]
    if tag == "run":
        return run_frames(P)
    if tag == "dead":
        return [dead(P, k) for k in range(len(MS["dead"]))]
    return [frame(P, f) for f in POSES[tag]]


def _shrink_globals():
    global SHRUNK_PLAN, L_ELBOW, R_ELBOW, KNEE_ROW, FEET_ROW, RUN_HIPS, BOOT_TOP
    SHRUNK_PLAN = {"rows": [r - PIVOT[1] for r in CUT_ROWS], "cols": [c - PIVOT[0] for c in CUT_COLS]}
    L_ELBOW, R_ELBOW = ((map_x(x), map_y(y)) for x, y in (L_ELBOW, R_ELBOW))
    KNEE_ROW, FEET_ROW = map_y(KNEE_ROW), map_y(FEET_ROW)
    RUN_HIPS = {k: map_y(r) for k, r in RUN_HIPS.items()}
    BOOT_TOP = map_y(BOOT_TOP)


if SCALE != 1:
    _shrink_globals()


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
        bad = K.write_strips("zed", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "zed_strips_review.png"), z=4,
                       soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], MS, os.path.join(a.review, "zed_strips_review.gif"), z=4)


if __name__ == "__main__":
    main()

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
- the run (8 frames, League's sprint): the upper body leant forward on an even line (RUN_LEAN: the head six squares
  ahead of the hips, unchanged), the rifle held level; the legs straight lines from the hips as the pack's ADCs run,
  in the leggings' colours on the design's own flat boots, one length in every frame: a foot slides back on the
  ground, kicks up behind, swings forward a row up, both feet off the ground at the widest stride (RUN_SEQ); the far
  leg four phases on and a shade darker; the body a row down as a foot lands. Finished square by square in a table
  (RUN_TABLE, --base writes the rig's own frames to start from). E's lunge and R's hop are strides of it; E's hop back
  is the figure lifted whole (a forward-leaning stride moving backwards read as running in place).
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
# the 40-row table's rows; a design with whole rows taken out lists the rows it kept in design40/shrink.json and Rw()
# maps them (the 37-row cut was undone: 「恢复到40」 - the torso it shortened read as a pot belly)
_SHRINK = os.path.join(ROOT, "assets", "source", "zeri", "design40", "shrink.json")
_KEPT = _json.load(open(_SHRINK))["rows"] if os.path.exists(_SHRINK) else list(range(40))


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
# the run, leant forward as League's Zeri sprints (「泽丽不应该是身体前倾着跑的的吗 再LOL里面」「你去网上看看视频吧 泽丽
# 怎么跑的 然后全部重改」), on straight legs as every ADC of the pack runs (league_varus, league_samira, league_sivir: 「所有的
# AD都是画直了移动的」「把腿画直吧 歪着造成整个身体变形」). The lean is an even line, no square resampled: every row of the
# upper body above RUN_LEAN one square further right every two rows, the head one block by its lowest row's amount, the
# levelled arm by its elbow's - the head six squares ahead of the hips, the free arm trailing. Legs on League's run
# changed length frame to frame and bent their knees (「腿变形啊」「我要的是模型不变形自然的交叉步走路」), and knees bent
# on solved legs read as crooked legs (「走路时候腿应该是直的吧 现在泽丽画成歪的了」). Each leg is one straight line from
# its hip to its ankle, drawn row by row in the leggings' colours (the thigh full at the hip as the design's far thigh
# 'ddda', two squares from the knee down as the design's shin 'da', wider across a row the more it slants), the tan
# patch at the near knee, the design's own whole boot flat on the ankle with its own outline, about one length
# (RUN_LEG) in every frame: a foot on the ground slides back from ahead of the hips to behind them, kicks up behind,
# swings forward a row up, both feet off the ground at the widest stride (League's sprint). The far leg is the same
# eight phases four on, its hip RUN_FAR right of the near one, drawn first and one shade darker (its boot too), the
# near one over it. The body and the hips come down a row as a foot lands; the coat's panels over both
RUN_LEAN = 87                   # the row the lean turns about (rows above move right, rows below stay)
RUN_DX = -3                     # the whole run frame moved back, so the hips stand where the idle stands (the feet do
                                # not jump forward as she starts to run; the head leans ahead)
RUN_HIP = (3.0, -3.0)           # the hips' middle (after the lean), squares from the standing point: under the shorts
RUN_FAR = 2.0                   # the far hip this many squares right of the near one (each one from the middle)
RUN_THIGH = (4, 2)              # the thigh's width at the hip and from the knee down (squares)
# the boot's cuff row with the boot on the ground (squares under the standing point): the boot's top (table row 33)
RUN_CUFF = SOLES - PIVOT[1] - (sum(1 for r in range(33, 40) if r in _KEPT) - 1)
RUN_LEG = RUN_CUFF - RUN_HIP[1]          # hip to cuff, squares (8)
RUN_STEP = [1, 0, 0, 0, 1, 0, 0, 0]      # rows the body and the hips come down: a row as a foot lands
# one leg's eight phases: its ankle (the cuff's middle) in squares right of the hips' middle, and how far it is lifted
# (None: as far as the leg's length takes it, never under the ground); the far leg is four phases on
RUN_SEQ = [(+3.5, 0),           # 1 landing ahead of the hips
           (+1.0, 0),           # 2 under them
           (-2.5, 0),           # 3 sliding back
           (-5.0, 2.0),         # 4 pushed off behind, two rows up: both feet off the ground
           (-7.0, 2.0),         # 5 kicked up behind (on the ground under the coat's hem a row of ground showed)
           (-3.5, 1.0),         # 6 swinging forward, a row up (its length would scrape the ground)
           (+1.5, 1.0),         # 7 passing under the hips, a row up
           (+5.0, None)]        # 8 reaching forward: both feet off the ground
LEGGINGS = ("#73234B", "#45183A")                    # lit, dark: the design's leggings
PATCH = ("#F2CC8F", "#AC8157")                       # the near knee's tan patch
# the far leg and its boot one shade darker on the design's own ramps, so the two legs read apart where they cross
FAR_DARKER = {"#73234B": "#45183A", "#9E493D": "#5A2418", "#F48C06": "#9E493D", "#F8C00C": "#F48C06",
              "#AC8157": "#5A2418", "#F2CC8F": "#AC8157"}
# what stays of the design under the belt in the run (table rows: (first, last) columns): the shorts' hem, the coat's
# two panels and the hanging hand; the boots (rows 33-39) are cut whole with their outline
RUN_KEEP = {25: [(0, 19)], 26: [(0, 20)], 27: [(0, 10)], 28: [(0, 3)], 29: [(0, 2)]}
# (rows 25 and 26 kept across: the shorts' hem under the belt - cut away, a square of ground showed between a thigh
# and the coat's panel under the belt: 「我怎么发现腿抬高时这里会略微变形」「这里没对齐留空档要注意吧」; row 27 to the
# outline right of the coat's hem, so a thigh swinging back behind it does not run into the hem's blue)
RUN_BOOTS = {"near": (33, 39, 0, 8), "far": (33, 39, 13, 22)}
# the idle: her own breath (import_native's shared cut would run through the upright rifle): everything above the legs
# sinks 0 0 1 1 1 1 0 0 rows over them (lowered), as league_viego's
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
# the run as finished frame by frame: one table of design40/palette.json letters per frame over the canvas window
# RUN_WINDOW ('.' clear). --base writes the rig's frames into it to start from; the tables are what is built (the
# user: 「你给我一帧一帧改到完美」 - every square of every frame checked and touched up by hand)
RUN_TABLE = os.path.join(ROOT, "assets", "source", "zeri", "run40", "run.txt")
RUN_WINDOW = (40, 54, 104, 100)            # x0, y0, x1, y1 (canvas, end exclusive)
PALETTE = os.path.join(ROOT, "assets", "source", "zeri", "design40", "palette.json")


def run_shift(y):
    """Squares a canvas row of the upper body moves right in the run's lean (the head as one block)."""
    ref = max(y, OY + int(Rw(HEAD_BOX[1])))
    return (RUN_LEAN - ref + 1) // 2 if ref < RUN_LEAN else 0


def read_run_table(path=RUN_TABLE):
    """The hand-finished run frames (canvases), or None when there is no table."""
    if not os.path.exists(path):
        return None
    pal = {k: K.rgb(v) for k, v in _json.load(open(PALETTE, encoding="utf-8")).items()}
    x0, y0, x1, y1 = RUN_WINDOW
    frames, cur = [], None
    for line in open(path, encoding="utf-8").read().splitlines():
        if line.startswith("# frame"):
            cur = np.zeros((128, 128, 4), np.uint8)
            frames.append(cur)
            row = y0
        elif line.startswith("#") or not line.strip() or cur is None:
            continue
        else:
            assert len(line) == x1 - x0, (len(frames), row, len(line))
            for i, ch in enumerate(line):
                if ch != ".":
                    cur[row, x0 + i] = (*pal[ch], 255)
            row += 1
    return frames


def write_run_table(frames, path=RUN_TABLE):
    inv = {}
    for k, v in _json.load(open(PALETTE, encoding="utf-8")).items():
        inv.setdefault(K.rgb(v), k)
    x0, y0, x1, y1 = RUN_WINDOW
    out = [f"# Zeri's run, finished frame by frame (tools/art/rig_zeri.py): canvas x {x0}-{x1 - 1}, y {y0}-{y1 - 1}; "
           f"letters as design40/palette.json, '.' clear"]
    for k, f in enumerate(frames):
        assert not f[..., 3][:y0].any() and not f[..., 3][y1:].any(), k
        assert not f[..., 3][:, :x0].any() and not f[..., 3][:, x1:].any(), k
        out.append(f"# frame {k + 1}")
        for y in range(y0, y1):
            out.append("".join(inv[tuple(int(v) for v in f[y, x, :3])] if f[y, x, 3] else "." for x in range(x0, x1)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")


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
    def __init__(self, table=True):
        self.table = read_run_table() if table else None      # the run as finished by hand (None: the rig's own)
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

    def run_upper(self):
        """The body above the legs with the rifle held level, leant forward (RUN_LEAN). Cached."""
        if getattr(self, "_upper", None) is not None:
            return self._upper
        body, _ = self.run_pieces()
        arm = np.zeros_like(self.a)
        self.level_arm(arm)
        up = np.zeros_like(self.a)
        for y in range(up.shape[0]):
            dx = run_shift(y)
            up[y] = np.roll(body[y], dx, 0) if dx else body[y]
        sh = run_shift(OY + int(Rw(20)))
        arm = K.shifted(arm, sh, 0)
        K.put(up, arm, 0, 0)                  # the arm by its elbow's row
        # the coat's rows beside the levelled forearm (under the elbow) moved a square less than the arm: the forearm
        # reaches back that square to the coat, as it leaves the sleeve in the attack (a square of outline between
        # them cut the arm off the body)
        ink = np.array(self.out, np.uint8)
        for r in (21, 22):
            y = OY + int(Rw(r))
            xs = [x for x in np.nonzero(arm[y, :, 3])[0] if not (arm[y, x, :3] == ink).all()]
            if xs:
                x0 = min(xs)
                for x in range(x0 - (sh - run_shift(y)), x0):
                    up[y, x] = arm[y, x0]
        self._upper = up
        return up

    def run_leg(self, phase, leg, step):
        """One leg at a phase: a straight line from its hip to its ankle, square by square (the thigh full at the hip,
        two squares from the knee down), the design's boot flat with its cuff's middle on the ankle, one outline ring
        round both; the far leg one shade darker."""
        import math
        _, boots = self.run_pieces()
        mid = PIVOT[0] + RUN_HIP[0] + 0.5
        hip = (mid + (RUN_FAR / 2 if leg == "far" else -RUN_FAR / 2), PIVOT[1] + RUN_HIP[1] + step + 0.5)
        ax, lift = RUN_SEQ[phase]
        if lift is None:                      # as high as the leg's length takes the foot (measured from the middle)
            lift = RUN_LEG - step - math.sqrt(max(0.0, RUN_LEG ** 2 - ax ** 2))
            lift = max(0.0, round(lift * 2) / 2)
        ank = (mid + ax, PIVOT[1] + RUN_CUFF + 0.5 - lift)
        lit, dark = (K.rgb(h) for h in LEGGINGS)
        cells = {}
        # row by row: the line's middle on the row, the leg's width across it (wider the more the leg slants, so a
        # slanting leg is as thick as an upright one - the pack's runs draw a slanting shin three squares a row), the
        # last square the shadow as on the design's legs ('da')
        th = math.atan2(abs(ank[0] - hip[0]), ank[1] - hip[1])
        for yi in range(int(math.floor(hip[1])), int(math.floor(ank[1])) + 1):
            f = min(1.0, max(0.0, (yi + 0.5 - hip[1]) / (ank[1] - hip[1])))
            cx = hip[0] + (ank[0] - hip[0]) * f
            w = max(2, int(round((RUN_THIGH[0] + (RUN_THIGH[1] - RUN_THIGH[0]) * min(1.0, f * 2)) / math.cos(th))))
            x0 = int(math.floor(cx - w / 2.0 + 0.5))
            for x in range(x0, x0 + w - 1):
                cells[(x, yi)] = lit
            cells[(x0 + w - 1, yi)] = dark
        if leg == "near":                     # the tan patch on her near knee (the design's), the leg's middle:
            ky = int(math.floor((hip[1] + ank[1]) / 2))      # on that row's own squares, wherever the leg slants
            for y, cols in ((ky, (PATCH[0], PATCH[1])), (ky + 1, (PATCH[1],))):
                row = sorted(x for x, yy in cells if yy == y)
                for x, col in zip(row, cols):
                    cells[(x, y)] = K.rgb(col)
        g = np.zeros_like(self.a)
        for (x, y), col in cells.items():
            g[y, x] = (*col, 255)
        # the outline round the leg, then the boot over it with its own (the design's): ringed again, a boot stood in
        # two rows of outline and next to the other boot four
        m = g[..., 3] > 0
        p = np.pad(m, 1)
        g[~m & (p[2:, 1:-1] | p[:-2, 1:-1] | p[1:-1, 2:] | p[1:-1, :-2])] = (*self.out, 255)
        boot, (mid, top), _ = boots[leg]
        K.put(g, K.shifted(boot, int(round(ank[0] - mid)), int(round(ank[1] - 0.5 - top))), 0, 0)
        if leg == "far":
            sw = {K.rgb(a_): K.rgb(b_) for a_, b_ in FAR_DARKER.items()}
            for y, x in zip(*np.nonzero(g[..., 3])):
                got = tuple(int(v) for v in g[y, x, :3])
                if got in sw:
                    g[y, x, :3] = sw[got]
        return g

    def run_frame(self, k):
        if self.table is not None:
            return self.table[k].copy()
        step = RUN_STEP[k]
        c = np.zeros_like(self.a)
        K.put(c, self.run_leg((k + 4) % 8, "far", step), 0, 0)      # the far leg first
        K.put(c, self.run_leg(k, "near", step), 0, 0)
        K.put(c, K.shifted(self.run_upper(), 0, step), 0, 0)
        c[SOLES + 1:] = 0
        return K.shifted(c, RUN_DX, 0)

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
        if tag == "skill2_back":              # E back: crouch, a hop back (the figure lifted whole: the run's frames
            return [P(low=1), P(dx=-2, dy=-2), P(dx=-1, low=1), P()]     # lean forward), the landing
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
        if tag == "run" and self.table is not None:
            return [f.copy() for f in frames]       # finished by hand
        out = []
        for f in frames:
            keep = None if tag == "dead" else self.head_keep(f)
            g = K.finish(f, self.out, SOLES, keep=keep)
            if tag == "run":
                # a pinhole shut between the legs and the coat is ground, not coat: the outline (finish gives it the
                # commonest colour round it - a square of the coat's blue under the hem)
                g[(f[..., 3] == 0) & (g[..., 3] > 0) & ~(g[..., :3] == np.array(self.out, np.uint8)).all(-1)] = \
                    (*self.out, 255)
            # finish leaves the kept head's light edges open (complete_outline skips light squares it may not touch):
            # the outline goes outside them too - only clear squares are filled
            g, _, _ = K.strips.complete_outline(g, color=tuple(self.out), feet=SOLES)
            legs_y = OY + int(Rw(24))                       # under the belt: between the legs
            for h in K.holes(g):
                if len(h) <= 6:
                    # a slit shut between the legs or the boots: the outline (in the leggings' dark colour a slit
                    # between two boots read as a third leg)
                    for y, x in h:
                        g[y, x] = (*self.out, 255)
            g[K.orphan_outline(g, tuple(self.out))] = 0       # outline squares touching no colour: stray
            # the design is ringed in the outline all round: no coloured square may meet the ground (the dark blues and
            # maroons complete_outline leaves open where a part moved off what it lay on: the coat's hem over a leg
            # that stepped away, the levelled forearm's underside, the bun beside the rifle that went level); and no
            # square of ground may sit in a dent (three sides closed) where parts were moved against each other: under
            # the belt in the run (a bite out of her hips, a split between the legs: 「腿抬高时这里会略微变形」「这里
            # 没对齐留空档要注意吧」), round the levelled forearm in every action (under the elbow and under the grip;
            # in the run where the lean took it, and the coat's front where the upright rifle's foot was). Both take
            # the outline. The design's own notches (the hair's, the crotch's, the hand's, the boots') lie outside
            # the boxes, the head's always (its box is skipped)
            lean = run_shift(OY + int(Rw(20))) + RUN_DX if tag == "run" else 0
            boxes = [(OY + int(Rw(17 if tag == "run" else 18)), OY + int(Rw(23)) + 3,
                      OX + 16 + lean - (2 if tag == "run" else 0), OX + 30 + lean)]
            if tag == "run":
                boxes.append((legs_y, SOLES, OX - 3 + RUN_DX, OX + 25 + RUN_DX))
            inbox = np.zeros(g.shape[:2], bool)
            for y0, y1, x0, x1 in boxes:
                inbox[y0:y1, x0:x1] = True
            if keep is not None and keep.any():
                ys, xs = np.nonzero(keep)
                inbox[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = False
            inbox[SOLES + 1:] = False
            ink = np.array(self.out, np.uint8)
            while True:
                op = g[..., 3] > 0
                col = op & ~(g[..., :3] == ink).all(-1)
                p = np.pad(col, 1)
                fill = ~op & (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
                fill[SOLES + 1:] = False
                if tag != "dead":
                    q = np.pad(op, 1).astype(int)
                    fill |= ~op & inbox & (q[:-2, 1:-1] + q[2:, 1:-1] + q[1:-1, :-2] + q[1:-1, 2:] >= 3)
                if not fill.any():
                    break
                g[fill] = (*self.out, 255)
            out.append(g)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--tags", default=",".join(TAGS))
    ap.add_argument("--base", action="store_true", help="write the rig's own run frames into RUN_TABLE (then finish "
                    "them by hand) and stop")
    a = ap.parse_args()
    if a.base:
        rig = Rig(table=False)
        write_run_table(rig.finished(rig.build("run"), "run"))
        print("written", RUN_TABLE)
        return
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

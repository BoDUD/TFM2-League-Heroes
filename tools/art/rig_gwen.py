#!/usr/bin/env python3
"""Gwen's action strips posed from the approved design's own parts (the casting body = the idle's).

    python tools/art/rig_gwen.py [--check] [--review DIR] [--tags attack,skill]

Codex's step-2 round (assets/source/gwen/codex_strips/) built the strips from the design's parts itself, but turned the
arms by 85-90 degrees with nearest-neighbour rotation (deformed), left R's throw and the hit as the idle, pointed the
scissors left in two frames, jumped the body up in the attack and left her standing upright for three death frames
while the scissors lay on the ground. The user: 「有奇怪的地方你帮我修复 灵活运用工具」. This rig (rig_samira's way) poses
her from the design instead:
- the body: the design with League's scissors lifted off (design_gwen.build(with_mask=True)) wherever she holds them;
- arms: straight, two squares thick in the design's own materials (fair skin lit / shade, the purple glove's two steps
  at the hand), one outline ring, as long as the design's hanging arm (3 skin steps, 2 glove steps); the far arm (image
  right) leaves the far shoulder and is drawn under the body (it shows where it comes out), the near arm (image left)
  over it, its outline never over the body's colours. Where an arm leaves her side what it covered is filled
  (FAR_FILL / NEAR_FILL).
- the scissors in her hand: drawn with design_gwen's own blade and ring recipe (the same colours and shading as the
  design's scissors), closed (one long blade) or, to snip, opened into two blades; the grip between the rings in the
  glove; the blade's direction per frame (0 right, 90 down) - never a rotated copy of pixels.
- the run (League's 8 frames): the upper body the idle's with its scissors, a row lower at each contact; each leg the
  design's own leg (rows 86-98, split at column 64) moved whole forward / back and lifted when it swings, the legs half
  a cycle apart so they cross under the skirt, the far leg a shade darker.
- the death (league_sivir's, the user's accepted one): struck back, knocked, the whole figure turned 45 degrees, lying on
  her back (a quarter turn), the scissors on the ground beside her.
Every frame is finished alike (rigkit.finish, then the 2+ square gaps of the raw frame cleared again, rig_samira).
Writes assets/source/native/gwen_<tag>.png (8x, 128x96 cells) and gwen_cells.json; then tools/art/import_native.py.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_gwen as DG  # noqa: E402
import rig_nocturne as RN  # noqa: E402
import rigkit as K  # noqa: E402
import strips  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "gwen_native.png")
HERO = "gwen"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the soles on row 99)
CELL, CELL_PIVOT = (128, 96), (64, 70)
SOLES = 99
MS = {"idle": [200] * 6, "run": [150] * 8, "attack": [60, 60, 70, 70, 80, 100],
      "skill": [50, 60, 60, 60, 60, 70, 80, 100], "skill2": [40, 40, 40, 60, 80, 80, 80, 100],
      "ult": [50, 60, 60, 70, 80, 100], "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}
TAGS = list(MS)

# ------------------------------------------------------------------------------------------------ the design's parts
# (rigkit.Design.letters: 0 ink, a navy, b dark violet, d bodice, e bow violet, f glove lit, r skin shade, v skin, ...)
SKIN_LIT, SKIN_SHADE, GLOVE_LIT, GLOVE_SHADE = "v", "r", "f", "d"
# the arms as drawn, taken off when the arm moves (rows: (first, last) column), and what they covered, filled in
NEAR_OFF = {75: (58, 59), 76: (58, 59), 77: (58, 58), 78: (57, 58), 79: (57, 58)}
NEAR_FILL = {75: (58, "0e"), 76: (58, "0e"), 77: (58, "0e"), 78: (58, "0"), 79: (58, "0")}
FAR_OFF = {74: (71, 73), 75: (71, 73), 76: (71, 72), 77: (71, 72)}
FAR_FILL = {74: (71, "b0"), 75: (71, "b0"), 76: (71, "e0"), 77: (71, "e0")}
NEAR_SH, FAR_SH = (58, 75), (71, 73)   # the arms' first squares (top-left of the two-square cross-section): the far one
                                       # right under its puffed sleeve, so it shows over the curls
ARM_STEPS, GLOVE_STEPS = 3, 2         # the design's arm: 3 skin steps and the glove's 2 (the user: longer ones were wrong)
STRAY = [(58, 86), (58, 87), (58, 88)] # squares left of the old small scissors under the skirt's left edge
LEG_TOP, LEG_SPLIT = 86, 64            # the legs' rows (to the soles) and the column between them
SC_LEN, SC_OPEN = 30, 44               # the held scissors: blade (squares), the snip's opening (degrees)
IDLE_DEG = 155                         # the design's blade points 155 degrees (down and back)
HAIR = "acghknt"                       # the hair's colours: the far arm and what it holds pass over them (the curls
HAIR_ROWS = (56, 80)                   # hang behind her shoulders), under everything else; right of the torso's edge
TORSO_RIGHT = 70                       # (column 70) only the curls and the sleeve are there: the far arm goes over them


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        self.L = L = D.letters()
        self.rgba = {k: np.array(tuple(c) + (255,), np.uint8) for k, c in L.items()}
        canvas, sc = DG.build(with_mask=True)
        if not np.array_equal(canvas, D.a):
            raise SystemExit("gwen_native.png differs from design_gwen.build(): run tools/art/design_gwen.py first")
        self.scissors = np.zeros_like(canvas)
        self.scissors[sc] = canvas[sc]
        body = canvas.copy()
        body[sc] = 0
        for x, y in STRAY:
            body[y, x] = 0
        self.body = body
        inv = {tuple(v): k for k, v in L.items()}
        self.hair = np.zeros(body.shape[:2], bool)
        ys, xs = np.nonzero(body[..., 3] > 0)
        for y, x in zip(ys, xs):
            if HAIR_ROWS[0] <= y <= HAIR_ROWS[1] and (inv.get(tuple(body[y, x, :3])) in HAIR or x > TORSO_RIGHT):
                self.hair[y, x] = True


# the idle's handle (design_gwen.LEAGUE) measured from the midpoint of its two rings: x along the handle away from the
# blade, y across it (down in the idle)
HANDLE_MID = (32.25, 25.5)
BLADE_FROM = 3.8                       # the blade starts this far past the grip, at the rings' near edge


def handle_frame(deg):
    """The blade's direction u (deg: 0 right, 90 down), the handle's h (back from the blade) and its cross n - turned
    the idle's way, or mirrored where turning would hang the idle's upper spikes below (n always points down)."""
    t = math.radians(deg)
    u = np.array([math.cos(t), math.sin(t)])
    h = -u
    n = np.array([-h[1], h[0]])
    if n[1] < 0 or (abs(n[1]) < 1e-9 and n[0] < 0):
        n = -n
    return u, h, n


def scissors_unit(P, deg, length=SC_LEN, opening=0):
    """The scissors in her hand as a part with its joint on the grip: the idle's own two cyan rings and four spikes
    round the grip (design_gwen.LEAGUE, the same size), the long blade along `deg` (0 right, 90 down) from the rings'
    near edge - or, open, two blades opening/2 either side, without the one spike that points along the blade (it
    crossed the upper blade); drawn with design_gwen's recipe and colours at every angle, never rotated pixels. (The
    user: the held pair had no spikes - 「继续改」; a round silver handle with a split blade was tried on 2026-10-06 and
    put back: 「这剪刀还不如之前的」.)"""
    N = 2 * length + 40
    c = np.zeros((N, N, 4), np.uint8)
    g = np.array([N / 2, N / 2])
    u, h, n = handle_frame(deg)
    at = lambda q: tuple(g + q[0] * h + q[1] * n)  # noqa: E731
    mx, my = HANDLE_MID
    for (cx, cy), ro, ri in DG.LEAGUE["rings"]:
        DG.league_ring(c, at((cx - mx, cy - my)), ro, ri)
    for b0, b1, w in DG.LEAGUE["spikes"]:
        q0, q1 = (b0[0] - mx, b0[1] - my), (b1[0] - mx, b1[1] - my)
        if opening and q1[0] <= 0:
            continue
        DG.league_blade(c, at(q0), at(q1), w)
    base = g + BLADE_FROM * u
    if opening:
        for sgn in (1, -1):
            a = math.radians(deg) + sgn * math.radians(opening / 2)
            w = np.array([math.cos(a), math.sin(a)])
            DG.league_blade(c, tuple(base), tuple(base + length * w), 2.8)
    else:
        DG.league_blade(c, tuple(base), tuple(base + length * u), 3.4)
    can, _, _ = strips.complete_outline(np.pad(c, ((1, 1), (1, 1), (0, 0))), color=DG.C["I"], feet=N + 2)
    c = can[1:-1, 1:-1]
    ys, xs = np.nonzero(c[..., 3] > 0)
    s = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    return K.Part(s, (g[0] - xs.min(), g[1] - ys.min()))


# ------------------------------------------------------------------------------------------------ drawing
def arm_cells(P, sh, deg, steps=ARM_STEPS, glove=GLOVE_STEPS):
    """A straight arm from the shoulder square `sh`, `deg` from hanging (+90 image right, -90 left, 180 up), two
    squares across (lit, shade), the glove's last steps; its outline ring, its colour squares and the hand (the
    glove's last step, a continuous point)."""
    t = math.radians(deg)
    dx, dy = math.sin(t), math.cos(t)
    horiz = abs(dx) > abs(dy) + 1e-9
    cells = {}
    for i in range(steps + glove):
        if horiz:
            x = sh[0] + i * (1 if dx > 0 else -1)
            y = int(math.floor(sh[1] + i * dy / abs(dx) + 0.5))
            sq = [(x, y), (x, y + 1)]
        else:
            y = sh[1] + i * (1 if dy > 0 else -1)
            x = int(math.floor(sh[0] + i * dx / abs(dy) + 0.5))
            sq = [(x, y), (x + 1, y)]
        g = i >= steps
        for k, q in enumerate(sq):
            cells[q] = (GLOVE_LIT if k == 0 else GLOVE_SHADE) if g else (SKIN_LIT if k == 0 else SKIN_SHADE)
        hand = (sq[0][0] + sq[1][0]) / 2 + 0.5, (sq[0][1] + sq[1][1]) / 2 + 0.5
    add = {}
    for (x, y), ch in cells.items():                   # a slanted arm's steps meet at corners: close them
        for ox, oy in K.N4:
            q, q2 = (x + ox, y + oy), (x + 2 * ox, y + 2 * oy)
            if q not in cells and q not in add and cells.get(q2) == ch:
                add[q] = ch
    cells.update(add)
    ring = {}
    for (x, y) in cells:
        for ox, oy in K.N4:
            q = (x + ox, y + oy)
            if q not in cells:
                ring[q] = P.rgba["0"]
    return ring, {q: P.rgba[ch] for q, ch in cells.items()}, hand


def part_cells(part, at):
    ox = int(math.floor(at[0] - part.j[0] + 1e-9))
    oy = int(math.floor(at[1] - part.j[1] + 1e-9))
    ys, xs = np.nonzero(part.s[..., 3])
    return {(int(x) + ox, int(y) + oy): part.s[y, x].copy() for y, x in zip(ys, xs)}


def put_cells(c, cells, ok=None):
    for (x, y), v in cells.items():
        if 0 <= y <= SOLES and 0 <= x < c.shape[1] and (ok is None or ok(x, y)):
            c[y, x] = v


def fill(P, a, spec):
    for y, (x0, s) in spec.items():
        for i, ch in enumerate(s):
            a[y, x0 + i] = P.rgba[ch]


def clear(a, spec):
    for y, (x0, x1) in spec.items():
        a[y, x0:x1 + 1] = 0


def shifted(a, dx, dy):
    return K.shifted(a, dx, dy) if (dx or dy) else a


NEEDLE = "xxssssm"                      # a needle from its point: white, silver, the eye's lilac
FAN = (-35, 0, 35)                      # R: three needles in the raised hand, degrees from straight up (25 apart
                                        # they merged into one white claw)
LOOSE = (-12, 0, 12)                    # at the release: three leaving the hand, degrees from level (to image right)


def needles(P, hand, held):
    """R's needles as cells, outlined: "fan" - three six-square needles fanned up out of the hand (one alone did not
    read: 「R的动作还是偏小」); "loose" - three flying out of the hand to the right, two squares clear of it."""
    hx, hy = hand[0] - 0.5, hand[1] - 0.5
    if held == "fan":
        dirs, d0 = [(math.sin(math.radians(a)), -math.cos(math.radians(a))) for a in FAN], 1
    else:
        dirs, d0 = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in LOOSE], 3
    cells = {}
    for dx, dy in dirs:
        for i, ch in enumerate(reversed(NEEDLE)):
            d = d0 + i
            q = (int(math.floor(hx + d * dx + 0.5)), int(math.floor(hy + d * dy + 0.5)))
            if q not in cells or ch in "xs":
                cells[q] = P.rgba[ch]
    ring = {}
    for (x, y) in cells:
        for ox, oy in K.N4:
            q = (x + ox, y + oy)
            if q not in cells:
                ring[q] = P.rgba["0"]
    ring.update(cells)
    return ring


# ------------------------------------------------------------------------------------------------ standing actions
# per frame: "far": (arm degrees, scissors degrees, opening) - the scissors in the far hand; "throw": (arm degrees,
# "fan", "loose" or None - needles()) - the far arm free, the scissors behind her as drawn (R: the open side of her, where the arm reads);
# "near": the same for the near arm; "move": the whole frame (dx, dy); a frame without "far" keeps the scissors behind
# her as drawn
STAND = {
    # the thrust (release frame 4), held at the hip (held at the shoulder the rings sank into the curls): leaning back
    # with the idle hold, the blade swung back low, brought forward, thrust out level with the figure two columns
    # forward, drawn back, home (a blade 30 degrees or more down reached the ground like a pole)
    "attack": [{"move": (-1, 0)}, {"far": (35, 160, 0), "move": (-1, 0)}, {"far": (45, 20, 0)},
               {"far": (60, 0, 0), "move": (2, 0)}, {"far": (50, 10, 0), "move": (1, 0)}, {}],
    # Snip Snip! (release frame 6): brought round in front at the hip, four quick snips (open, shut, open, shut), the
    # final wide snip with a lunge, shut, home (no blade a few degrees off level: its rows stepped as if broken)
    "skill": [{"far": (45, 25, 0)}, {"far": (60, 0, SC_OPEN)}, {"far": (60, 0, 0)}, {"far": (60, 0, SC_OPEN)},
              {"far": (60, 0, 0)}, {"far": (60, 0, 70), "move": (2, 0)}, {"far": (60, 0, 0), "move": (1, 0)}, {}],
    # E then W (release frame 6): the skip on the run's own legs ("leap": the run frame) with the scissors as in the
    # idle - pushing off low, in the air two rows up, landing - (the idle slid along read as gliding), home, the
    # scissors raised from the hip, the point up and out clear of the curls, home
    "skill2": [{"leap": 0, "move": (1, 0)}, {"leap": 6, "move": (3, -2)}, {"leap": 7, "move": (2, 0)}, {},
               {"far": (45, -45, 0)}, {"far": (60, -70, 0)}, {"far": (45, -45, 0)}, {}],
    # Needlework (release frame 4) with the free near hand (the far one is by the scissors and in the curls): the
    # hand at her side, swung back and up over the near curl with a fan of three needles (one beside the hanging arm
    # read as a white stripe on her side; 「R的动作还是偏小」), whipped across her chest to the right, the needles gone
    # (thrown - the effect flies them; drawn leaving the hand they lay across her chest as a white bar), the
    # follow-through, home;
    # leaning back two columns for the wind-up and forward two at the release (in place it read as the idle)
    "ult": [{"near": (-30, None), "move": (-1, 0)}, {"near": (-150, "fan"), "move": (-2, 0)},
            {"near": (-160, "fan"), "move": (-2, 0)}, {"near": (100, None), "move": (2, 0)},
            {"near": (70, None), "move": (1, 0)}, {}],
    # the hit: pushed back and recovering (the head alone moved tore the curls at the chin)
    "hit": [{"move": (-2, 0)}, {"move": (-1, 0)}],
}


def stand(P, pose):
    far, near, throw = pose.get("far"), pose.get("near"), pose.get("throw")
    a = P.body.copy()
    sc_behind = np.zeros(a.shape[:2], bool)                       # the scissors behind her: the throwing arm over them
    if far is None:
        sc_behind = (P.scissors[..., 3] > 0) & (a[..., 3] == 0)
    if far is None:
        K.put(a, P.scissors, 0, 0, under=True)
    if far is not None or throw is not None:
        clear(a, FAR_OFF)
        fill(P, a, FAR_FILL)
    if near is not None:
        clear(a, NEAR_OFF)
        fill(P, a, NEAR_FILL)
    body = a[..., 3] > 0
    ink = (a[..., :3] == P.rgba["0"][:3]).all(-1) & body
    hair = P.hair
    under = lambda x, y: not body[y, x] or hair[y, x]              # the far arm and its scissors: over the hair,
                                                                   # behind the body
    clear_ok = lambda x, y: not body[y, x] or ink[y, x]            # the near arm's outline: never over body colours
    c = a.copy()
    keep = np.zeros(a.shape[:2], bool)                            # the weapon's and the needle's outline stays black
    if far is not None:
        deg, sdeg, opening = far
        ring, col, hand = arm_cells(P, FAR_SH, deg)
        sc = part_cells(scissors_unit(P, sdeg, opening=opening), hand)
        put_cells(c, ring, under)
        put_cells(c, {q: v for q, v in sc.items()}, under)        # the scissors over the arm's ring, under the body
        for (x, y) in sc:
            if 0 <= y < 128 and 0 <= x < 128 and under(x, y):
                keep[y, x] = True
        put_cells(c, col, under)
        glove = {q: v for q, v in col.items() if (v[:3] == P.rgba[GLOVE_LIT][:3]).all()
                 or (v[:3] == P.rgba[GLOVE_SHADE][:3]).all()}
        put_cells(c, glove)                                         # the hand on the grip, in sight
    if throw is not None:
        deg, held = throw
        ring, col, hand = arm_cells(P, FAR_SH, deg)
        over_sc = lambda x, y: under(x, y) or sc_behind[y, x]  # noqa: E731
        put_cells(c, ring, over_sc)
        put_cells(c, col, over_sc)
        if held:
            nd = needles(P, hand, held)
            put_cells(c, nd, over_sc)
            for (x, y) in nd:
                if 0 <= y < 128 and 0 <= x < 128:
                    keep[y, x] = True
    if near is not None:
        deg, held = near
        ring, col, hand = arm_cells(P, NEAR_SH, deg)
        put_cells(c, ring, clear_ok)
        put_cells(c, col)
        if held:
            nd = needles(P, hand, held)
            put_cells(c, nd)
            for (x, y) in nd:
                if 0 <= y < 128 and 0 <= x < 128:
                    keep[y, x] = True
    c[SOLES + 1:] = 0
    dx, dy = pose.get("move", (0, 0))
    k4 = np.zeros(a.shape, np.uint8)
    k4[keep] = 255
    P.keep = shifted(k4, dx, dy)[..., 3] > 0
    return shifted(c, dx, dy)


# ------------------------------------------------------------------------------------------------ the run
# one leg's cycle (8 frames): (knee columns, ankle columns from the hip - + forward = image right -, rows lifted):
# contact, loading, mid-stance, push, toe-off, kick, passing, reach; the other leg half a cycle later. The hip stays
# under the skirt; the thigh rows lean to the knee, the shin rows on to the ankle, the boot rows move whole with the
# ankle (the user: v1's legs slid as straight sticks, 「走路的时候 说不出的怪」)
CYCLE = [(1, 4, 0), (1, 2, 0), (0, 0, 0), (-1, -2, 0), (-1, -4, 1), (0, -3, 3), (2, 0, 3), (2, 3, 1)]
# the hips drawn in under the skirt (the near leg 2 columns right, the far one 2 left): 6 apart, a stride of 3 put both
# feet on one spot at the contacts and the near leg hid the far one (「两个腿上都有像素丢失吧？」); 2 apart they part at
# the contacts and cross while passing (run-crossing: twice the swing must exceed the hip gap)
HIP_IN = {"near": 2, "far": -2}
BOB = [1, 1, 0, 0, 1, 1, 0, 0]          # the body a row lower at each contact - two rows (and the curls and scissors a frame
LAG = 0                                # late, a reviewer's idea) squashed her onto her legs and tore the curls from the
CURLS = ((68, 82), (60, 68))           # head: 「走路时模型变形了吧？」
KNEE_ROW, BOOT_ROW = 91, 94            # the stockings to the knee, the shin, the boots from row 94
FAR_SHADE = {"f": "d", "d": "b", "x": "s", "s": "m", "m": "j", "w": "x", "q": "l", "u": "q"}


def bent(leg, knee, ankle, lift, hip_in=0):
    """The leg's own rows moved whole: row by row along hip -> knee -> ankle, the boot rows at the ankle, all lifted;
    hip_in draws the leg in toward the other from nothing at the hip to all of it at the knee (moving the hip itself left
    a gap under the skirt's edge: 「这里少一块看不到吗」)."""
    out = np.zeros_like(leg)
    for y in range(LEG_TOP, SOLES + 1):
        inward = hip_in * min(1.0, (y - LEG_TOP) / (KNEE_ROW - LEG_TOP))
        if y <= KNEE_ROW:
            dx = knee * (y - LEG_TOP) / (KNEE_ROW - LEG_TOP)
        elif y < BOOT_ROW:
            dx = knee + (ankle - knee) * (y - KNEE_ROW) / (BOOT_ROW - KNEE_ROW)
        else:
            dx = ankle
        dx += inward
        dx = int(math.floor(dx + 0.5))
        row = leg[y]
        ty = y - lift
        if dx >= 0:
            out[ty, dx:] = np.maximum(out[ty, dx:], row[:row.shape[0] - dx]) if dx else row
        else:
            out[ty, :dx] = row[-dx:]
    return out


def run_parts(P):
    full = P.body.copy()
    K.put(full, P.scissors, 0, 0, under=True)
    upper = full.copy()
    upper[LEG_TOP:] = 0
    upper[LEG_TOP:, :] = 0
    legs = P.body.copy()
    legs[:LEG_TOP] = 0
    near, far = legs.copy(), legs.copy()
    near[:, LEG_SPLIT + 1:] = 0
    far[:, :LEG_SPLIT] = 0
    inv = {tuple(v): k for k, v in P.L.items()}
    ys, xs = np.nonzero(far[..., 3] > 0)
    for y, x in zip(ys, xs):
        ch = inv.get(tuple(far[y, x, :3]))
        if ch in FAR_SHADE:
            far[y, x] = P.rgba[FAR_SHADE[ch]]
    # the scissors' blade under the skirt's left edge belongs to the upper body (it rides with it)
    sc_low = P.scissors.copy()
    sc_low[:LEG_TOP] = 0
    return upper, sc_low, near, far


def run_frame(P, k):
    upper, sc_low, near, far = run_parts(P)
    body = P.body.copy()
    body[LEG_TOP:] = 0
    (r0, r1), (c0, c1) = CURLS
    curls = np.zeros(body.shape[:2], bool)
    curls[r0:r1 + 1] = P.hair[r0:r1 + 1]
    curls[:, c0:c1 + 1] = False
    lag = np.zeros_like(body)
    lag[curls] = body[curls]
    sc = P.scissors.copy()
    body[curls] = 0
    c = np.zeros((128, 128, 4), np.uint8)
    for leg, ph, side in ((far, (k + 4) % 8, "far"), (near, k, "near")):
        K.put(c, bent(leg, *CYCLE[ph], hip_in=HIP_IN[side]), 0, 0)
    dy = BOB[k]
    late = BOB[k - LAG]
    K.put(c, shifted(body, 0, dy), 0, 0)
    K.put(c, shifted(lag, 0, late), 0, 0, under=True)
    K.put(c, shifted(sc, 0, late), 0, 0, under=True)
    c[SOLES + 1:] = 0
    return c


def posed(P, pose):
    """A STAND frame: stand(), or for "leap" the run's frame of that number moved by "move"."""
    if "leap" in pose:
        c = shifted(run_frame(P, pose["leap"]), *pose.get("move", (0, 0)))
        c[SOLES + 1:] = 0
        return c
    return stand(P, pose)


# ------------------------------------------------------------------------------------------------ the death
def turned(a, deg, joint):
    ys, xs = np.nonzero(a[..., 3] > 0)
    x0, y0 = xs.min(), ys.min()
    s = a[y0:ys.max() + 1, x0:xs.max() + 1]
    jx, jy = joint[0] - x0 - 0.5, joint[1] - y0 - 0.5
    if deg % 90 == 0:
        r, (rx, ry) = RN.op(s, (jx, jy), ("rot", int(deg // 90) % 4))
    else:
        r, (rx, ry) = RN.rotsprite(s, (jx, jy), deg)
    out = np.zeros_like(a)
    K.put(out, r, int(math.floor(joint[0] - 0.5 - rx + 0.5)), int(math.floor(joint[1] - 0.5 - ry + 0.5)))
    return out


def on_ground(a, dx=0):
    ys, _ = np.nonzero(a[..., 3] > 0)
    return shifted(a, dx, SOLES - ys.max())


def laid_out(P):
    """The figure ready to lie down: the scissors gone from her (they fell), the arms down her sides as drawn."""
    a = P.body.copy()
    a[SOLES + 1:] = 0
    return finish(P, a)


def lying(P):
    """On her back: the figure a quarter turn counter-clockwise (the head to the left, face up) on the ground line."""
    a = laid_out(P)
    ys, xs = np.nonzero(a[..., 3] > 0)
    rot = np.rot90(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 1).copy()
    out = np.zeros_like(a)
    h, w = rot.shape[:2]
    x0 = 64 - w // 2 + 2
    out[SOLES + 1 - h:SOLES + 1, x0:x0 + w] = rot
    return out


def scissors_on_ground(P, x_grip=86):
    """The scissors lying on the ground in front of her feet, the blade pointing right (closed), clear of her body
    (under the boots they read as one lump)."""
    part = scissors_unit(P, 0)
    c = np.zeros((128, 128, 4), np.uint8)
    cells = part_cells(part, (x_grip, 0))
    lo = max(y for _, y in cells)
    put_cells(c, {(x, y + SOLES - lo): v for (x, y), v in cells.items()})
    return c


# struck, knocked back, falling and lying - every frame turned about the feet (the lying frames placed on their own
# jumped 20 columns from the 70-degree one), (degrees, columns back, rows up); the scissors: in her hand as she tips
# (moved with the hand, standing on their tip beside her they floated), then lying on the ground in front of her
DEAD = ["hit", "knocked", (20, -1, 0), (45, -3, 2), (70, -4, 1), (90, -5, 1), (90, -5, 0), (90, -5, 0)]
FEET = (60.0, 99.0)
GRIP = (72.0, 77.0)                    # the far hand on the idle's scissors (the glove's squares 71-72, rows 76-77)


def about_feet(q, deg):
    """Where the square q goes when the figure turns deg about FEET (positive: the head to the left, as turned())."""
    t = math.radians(deg)
    rx, ry = q[0] - FEET[0], q[1] - FEET[1]
    return FEET[0] + rx * math.cos(t) + ry * math.sin(t), FEET[1] - rx * math.sin(t) + ry * math.cos(t)


def dead_frame(P, i):
    what = DEAD[i]
    if what == "hit":
        return stand(P, {"move": (-1, 0)})
    if what == "knocked":
        return stand(P, {"move": (-2, -1)})
    deg, dx, up = what
    out = np.zeros((128, 128, 4), np.uint8)
    t = turned(laid_out(P), deg, FEET)
    ys, _ = np.nonzero(t[..., 3] > 0)
    sy = SOLES - int(ys.max()) - up
    K.put(out, shifted(t, dx, sy), 0, 0)
    if deg == 20:
        gx, gy = about_feet(GRIP, deg)
        mx, my = int(round(gx - GRIP[0])) + dx, int(round(gy - GRIP[1])) + sy
        K.put(out, shifted(P.scissors, mx, my), 0, 0, under=True)
    else:
        K.put(out, scissors_on_ground(P, 82), 0, 0, under=True)
    return out


# ------------------------------------------------------------------------------------------------ build
def finish(P, raw):
    """rigkit.finish, then the open gaps the raw frame has (2+ squares) cleared again where the finish filled them
    (rig_samira: its pinhole fill made a patch between the legs)."""
    f = K.finish(raw, P.D.outline, SOLES, pinholes=1)
    ink = np.array(P.D.outline, np.uint8)
    for comp in K.holes(raw):
        if len(comp) < 2:
            continue
        for y, x in comp:
            if f[y, x, 3] and not (f[y, x, :3] == ink).all():
                f[y, x] = 0
    while True:
        gone = K.orphan_outline(f, P.D.outline)
        if not gone.any():
            break
        f[gone] = 0
    keep = getattr(P, "keep", None)
    P.keep = None
    soften_inner_ink(P, f, keep)
    return f


def soften_inner_ink(P, f, keep=None):
    """Outline squares a pose puts inside the figure (an arm's or the scissors' ring over the hair and the dress, a leg's
    over the other leg, the seam of a moved body) - not in the idle there, every 4-neighbour opaque, two or more of them
    coloured - take the darkest colour beside them: one near-black ring outside, the material's own dark inside (oppi's
    rule; the user: 「清理一下没用的黑色素」「弄干净点」). The idle is matched first by the shift that best fits the head."""
    ink = np.array(P.D.outline, np.uint8)
    idle = P.D.a
    best = None
    for dx in range(-5, 6):
        for dy in range(-3, 4):
            s = K.shifted(idle, dx, dy) if (dx or dy) else idle
            cost = int((s[56:72, 50:80, :3] != f[56:72, 50:80, :3]).any(-1).sum())
            if best is None or cost < best[0]:
                best = (cost, s)
    s = best[1]
    was = (s[..., 3] > 0) & (s[..., :3] == ink).all(-1)
    op = f[..., 3] > 0
    isk = op & (f[..., :3] == ink).all(-1)
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]  # noqa: E731
    change = {}
    for y, x in zip(*np.nonzero(isk & ~was)):
        if y >= SOLES or (keep is not None and keep[y, x]):
            continue
        n4 = [(y + dy, x + dx) for dy, dx in K.N4]
        if not all(0 <= yy < f.shape[0] and 0 <= xx < f.shape[1] and op[yy, xx] for yy, xx in n4):
            continue
        cols = [tuple(int(v) for v in f[yy, xx, :3]) for yy, xx in n4 if not isk[yy, xx]]
        if len(cols) >= 2:
            change[(y, x)] = min(cols, key=lum)
    for (y, x), c in change.items():
        f[y, x, :3] = c


def frames(P, tag):
    n = len(MS[tag])
    fin = lambda a: finish(P, a)  # noqa: E731
    if tag == "run":
        return [fin(run_frame(P, k)) for k in range(n)]
    if tag == "dead":
        return [fin(dead_frame(P, k)) for k in range(n)]
    if tag in STAND:
        return [fin(posed(P, p)) for p in STAND[tag]]
    if tag == "idle":
        return [breathe(P, d) for d in BREATH]
    return [P.D.a.copy() for _ in range(n)]


BREATH = [0, 0, 1, 1, 0, 0]            # the upper body (to row BREATH_ROW) a row lower in two of the six frames
BREATH_ROW = 80


def breathe(P, d):
    """The idle with the body above BREATH_ROW and the scissors sunk d rows (the row under it covered) (a reviewer:
    the idle read as a still picture)."""
    if not d:
        return P.D.a.copy()
    a = P.body.copy()
    top = a.copy()
    top[BREATH_ROW + 1:] = 0
    a[:BREATH_ROW + 1] = 0
    K.put(a, shifted(top, 0, d), 0, 0)
    K.put(a, shifted(P.scissors, 0, d), 0, 0, under=True)      # with the hand that holds them (they stayed: the grip
    return finish(P, a)                                         # slid a row on the rings)


def review_gif(P, built, path, z=4):
    """Every strip twice at its own timing, one shared palette (no per-frame palettes: 「怎么gif图又是彩色的？」)."""
    allf = [f for frs in built.values() for f in frs]
    x0, x1, y0, y1 = K.crop_box(allf)
    W, H = (x1 - x0) * z, (y1 - y0) * z
    tiles, durs = [], []
    for tag, frs in built.items():
        for _ in range(2):
            for f, m in zip(frs, MS[tag]):
                tile = Image.new("RGBA", (W, H), (110, 120, 108, 255))
                tile.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]).resize((W, H), Image.NEAREST))
                tiles.append(tile.convert("RGB"))
                durs.append(max(20, int(m)))
    sheet = Image.new("RGB", (W, H * len(tiles)))
    for i, t in enumerate(tiles):
        sheet.paste(t, (0, i * H))
    pal = sheet.quantize(colors=255, dither=Image.Dither.NONE)
    imgs = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in tiles]
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=durs, loop=0, disposal=2, optimize=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write review sheets to this folder")
    ap.add_argument("--tags", help="comma-separated tags to build (review only)")
    a = ap.parse_args()
    P = Parts()
    tags = a.tags.split(",") if a.tags else TAGS
    built = {t: frames(P, t) for t in tags}
    for t in tags:
        rows = K.audit(built[t], P.D.a, P.D.outline, SOLES)
        print(t, " ".join(f"[{r['pieces']}p {r['holes']}h {r['orphans']}o {r['area']}]" for r in rows))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, [P.D.a] + built[t]) for t in tags], os.path.join(a.review, "rig_sheet.png"), z=4,
                       soles=SOLES)
        review_gif(P, built, os.path.join(a.review, "rig_actions.gif"))
        return
    bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differ:", bad or "none")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

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
SC_LEN, SC_OPEN = 30, 44               # the held scissors: blade length (squares), the snip's opening (degrees)
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


def scissors_unit(P, deg, length=SC_LEN, opening=0):
    """The scissors as a part with its joint on the grip: the two spiked rings behind the grip, the blade (or, open,
    two blades opening/2 either side) along `deg` (0 right, 90 down), design_gwen's recipe and colours."""
    n = 2 * length + 24
    c = np.zeros((n, n, 4), np.uint8)
    g = np.array([n / 2, n / 2])
    t = math.radians(deg)
    u = np.array([math.cos(t), math.sin(t)])
    v = np.array([-u[1], u[0]])
    for side in (1, -1):
        DG.league_ring(c, tuple(g - 2.6 * u + side * 2.3 * v), 2.5, 1.1)
        DG.league_blade(c, tuple(g - 2.6 * u + side * 4.2 * v - 1.5 * u), tuple(g - 2.6 * u + side * 6.5 * v - 2.5 * u),
                        1.4)
    if opening:
        for s in (1, -1):
            a = t + s * math.radians(opening / 2)
            w = np.array([math.cos(a), math.sin(a)])
            DG.league_blade(c, tuple(g + 0.5 * w), tuple(g + length * w), 2.8)
    else:
        DG.league_blade(c, tuple(g + 0.5 * u), tuple(g + length * u), 3.4)
    can, _, _ = strips.complete_outline(np.pad(c, ((1, 1), (1, 1), (0, 0))), color=DG.C["I"], feet=n + 2)
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


def needle(P):
    """R's needle in the hand: two silver squares and a white point, outlined (a part pointing up)."""
    s = np.zeros((5, 3, 4), np.uint8)
    for y, ch in ((1, "x"), (2, "s"), (3, "s")):
        s[y, 1] = P.rgba[ch]
    for y, x in ((0, 1), (1, 0), (1, 2), (2, 0), (2, 2), (3, 0), (3, 2), (4, 1)):
        s[y, x] = P.rgba["0"]
    return K.Part(s, (1.5, 4.0))


# ------------------------------------------------------------------------------------------------ standing actions
# per frame: "far": (arm degrees, scissors degrees, opening) - the scissors in the far hand; "throw": (arm degrees,
# "needle" or None) - the far arm free, the scissors behind her as drawn (R: the open side of her, where the arm reads);
# "near": the same for the near arm; "move": the whole frame (dx, dy); a frame without "far" keeps the scissors behind
# her as drawn
STAND = {
    # the thrust (release frame 4): lifted forward, drawn back level, held back, thrust out with the body leaning in,
    # a twirl up, home
    "attack": [{"far": (40, 30, 0)}, {"far": (70, 0, 0), "move": (-1, 0)}, {"far": (80, 0, 0), "move": (-1, 0)},
               {"far": (90, 0, 0), "move": (2, 0)}, {"far": (120, -45, 0), "move": (1, 0)}, {}],
    # Snip Snip! (release frame 6): brought round in front, four quick snips (open, shut, open, shut), the final wide
    # snip low with a lunge, held, home
    "skill": [{"far": (80, 0, 0)}, {"far": (90, 0, SC_OPEN)}, {"far": (90, 0, 0)}, {"far": (90, 0, SC_OPEN)},
              {"far": (90, 0, 0)}, {"far": (70, 15, 64), "move": (2, 0)}, {"far": (70, 15, 0), "move": (1, 0)}, {}],
    # Skip 'n Slash then Hallowed Mist (release frame 6): the skip forward (the scissors held low ahead), landing, the
    # scissors raised and twirled over her head (up-right, level, up-left), home
    "skill2": [{"far": (50, 30, 0), "move": (2, 0)}, {"far": (50, 30, 0), "move": (4, 0)},
               {"far": (50, 30, 0), "move": (2, 0)}, {}, {"far": (150, -45, 0)}, {"far": (175, 0, 0)},
               {"far": (150, -60, 0)}, {}],
    # Needlework (release frame 4): the needle drawn at her side, the arm swung back and up, whipped forward to the
    # right (the needle gone), the follow-through, home
    "ult": [{"throw": (45, "needle")}, {"throw": (135, "needle")}, {"throw": (155, "needle")}, {"throw": (95, None)},
            {"throw": (60, None)}, {}],
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
    if far is not None:
        deg, sdeg, opening = far
        ring, col, hand = arm_cells(P, FAR_SH, deg)
        sc = part_cells(scissors_unit(P, sdeg, opening=opening), hand)
        put_cells(c, ring, under)
        put_cells(c, {q: v for q, v in sc.items()}, under)        # the scissors over the arm's ring, under the body
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
        if held == "needle":
            put_cells(c, part_cells(needle(P), (hand[0], hand[1] - 1)), over_sc)
    if near is not None:
        deg, held = near
        ring, col, hand = arm_cells(P, NEAR_SH, deg)
        put_cells(c, ring, clear_ok)
        put_cells(c, col)
        if held == "needle":
            put_cells(c, part_cells(needle(P), (hand[0], hand[1] - 1)))
    c[SOLES + 1:] = 0
    dx, dy = pose.get("move", (0, 0))
    return shifted(c, dx, dy)


# ------------------------------------------------------------------------------------------------ the run
# one leg's cycle (8 frames): (knee columns, ankle columns from the hip - + forward = image right -, rows lifted):
# contact, loading, mid-stance, push, toe-off, kick, passing, reach; the other leg half a cycle later. The hip stays
# under the skirt; the thigh rows lean to the knee, the shin rows on to the ankle, the boot rows move whole with the
# ankle (the user: v1's legs slid as straight sticks, 「走路的时候 说不出的怪」)
CYCLE = [(1, 3, 0), (1, 1, 0), (0, -1, 0), (-1, -2, 0), (-1, -3, 1), (0, -2, 2), (1, 0, 2), (2, 3, 1)]
BOB = [1, 1, 0, 0, 1, 1, 0, 0]
KNEE_ROW, BOOT_ROW = 91, 94            # the stockings to the knee, the shin, the boots from row 94
FAR_SHADE = {"f": "d", "d": "b", "x": "s", "s": "m", "m": "j", "w": "x", "q": "l", "u": "q"}


def bent(leg, knee, ankle, lift):
    """The leg's own rows moved whole: row by row along hip -> knee -> ankle, the boot rows at the ankle, all lifted."""
    out = np.zeros_like(leg)
    for y in range(LEG_TOP, SOLES + 1):
        if y <= KNEE_ROW:
            dx = knee * (y - LEG_TOP) / (KNEE_ROW - LEG_TOP)
        elif y < BOOT_ROW:
            dx = knee + (ankle - knee) * (y - KNEE_ROW) / (BOOT_ROW - KNEE_ROW)
        else:
            dx = ankle
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
    c = np.zeros((128, 128, 4), np.uint8)
    for leg, ph in ((far, (k + 4) % 8), (near, k)):
        K.put(c, bent(leg, *CYCLE[ph]), 0, 0)
    dy = BOB[k]
    K.put(c, shifted(sc_low, 0, dy), 0, 0, under=True)
    K.put(c, shifted(upper, 0, dy), 0, 0)
    c[SOLES + 1:] = 0
    return c


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


DEAD = ["hit", "knocked", ("tilt", 45), ("lying", 1), ("lying", 0), ("lying", 0), ("lying", 0), ("lying", 0)]


def dead_frame(P, i):
    what = DEAD[i]
    if what == "hit":
        return stand(P, {"move": (-1, 0)})
    if what == "knocked":
        return stand(P, {"move": (-2, -1)})
    out = scissors_on_ground(P)
    if what[0] == "tilt":
        fig = shifted(on_ground(turned(laid_out(P), what[1], (60.0, 99.0)), -4), 0, -2)
        K.put(out, fig, 0, 0)
        return out
    body = lying(P)
    if what[1]:
        body = shifted(body, 0, -what[1])
    K.put(out, body, 0, 0)
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
            return f
        f[gone] = 0


def frames(P, tag):
    n = len(MS[tag])
    fin = lambda a: finish(P, a)  # noqa: E731
    if tag == "run":
        return [fin(run_frame(P, k)) for k in range(n)]
    if tag == "dead":
        return [fin(dead_frame(P, k)) for k in range(n)]
    if tag in STAND:
        return [fin(stand(P, p)) for p in STAND[tag]]
    return [P.D.a.copy() for _ in range(n)]


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

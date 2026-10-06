#!/usr/bin/env python3
"""Samira's action strips posed from the approved design's own parts (the casting body = the idle's).

    python tools/art/rig_samira.py [--check] [--review DIR] [--tags attack,skill]

Codex's step-2 round (assets/source/samira/codex_strips/) redrew her in every strip and passed none of its own checks;
the user picked posing her from the design (rig_tryndamere's way). v1 was rejected: 「手变形 走路没交叉步 死亡动画完全错误
模型变形」; v2 (two-bone arms, League's run joints) too: 「手臂对吗 走路对吗？」「你看了不奇怪吗 没违和感吗」 - its arms grew
out of her chest (the far shoulder put by the neck and the arm drawn over the corset and the hair; in R both arms one bar
through her), and its run legs were not her legs (a bare-skin thigh she does not have, the red band at the hip instead
of the knee, both legs drawn in to one column so they made a V). v3 learns from oppi's Samira (the shooting arm straight
and level at the shoulder, three squares thick, lit on top) and the accepted Varus / Kai'Sa runs:
- arms: straight, three squares thick in the design's skin (lit, lit, shade toward the bottom / the back), the dark
  green glove's two squares at the hand, one outline ring, as long as the design's akimbo arm; an arm leaves the torso
  at a top corner - the near arm at the near shoulder's outer edge, drawn over the body; the far arm at the torso's
  upper right corner (right of the corset), drawn under the torso and over the hair falling behind the far shoulder.
  Where an arm leaves the hip, what it covered is filled in: the torso's near side (NEAR_FILL), the hair behind the far
  forearm (FAR_FILL). A hand that does not move stays on the hip as drawn.
- weapons: the long revolver level in the glove; the greatsword (taken off her back: the hilt over the near shoulder,
  the blade by the far boot) in eight exact orientations (level, upright, 45 degrees; never RotSprite), in the far hand.
- the run (League's 8 frames): the upper body the idle's (both hands at the waist, as League's run carries them), a row
  lower at each contact; each leg made of the design's own leg rows (green: two shade, two lit; the red band at the knee;
  the far boot's foot, toe forward, its gold heel) laid along hip -> knee -> ankle from the design's hips; the near boot
  crosses in front of the far one, the swinging foot is lifted up to 3 rows.
- the death (league_sivir's): struck back, knocked, falling (the whole figure turned 45 degrees), lying on her back (a
  quarter turn), the greatsword on the ground by her head.
Every frame is finished alike (rigkit.finish: pinholes, the outline closed round moved edges, crumbs dropped).
Writes assets/source/native/samira_<tag>.png (8x, 128x96 cells) and samira_cells.json; then tools/art/import_native.py.
"""
import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import rig_nocturne as RN  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "samira_native.png")
HERO = "samira"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the soles on row 99)
CELL, CELL_PIVOT = (128, 96), (64, 70)
SOLES = 99
MS = {"idle": [200] * 6, "run": [133] * 8, "attack": [60, 60, 60, 70, 80, 100], "attack_m": [50, 40, 50, 90, 100, 110],
      "skill": [60, 60, 90, 90, 80, 100], "skill_m": [50, 50, 40, 100, 100, 110],
      "skill2": [50, 50, 67, 90, 90, 90, 90, 90, 90, 90, 90, 100],
      "ult": [150, 184, 184, 184, 184, 184, 184, 184, 184, 380], "hit": [100, 100],
      "dead": [100, 110, 110, 120, 130, 150, 200, 300]}
TAGS = list(MS)

# the design's palette by letter (rigkit.Design.letters: dark to light), as the grid prints it
#   0 ink  a #440B13  b #6E020F  d #232B29 (green shade)  e #262936 (navy)  f #3B241D  g #B20413 (red)  h #951517
#   i #38433D (green lit)  l #2B5664 (teal)  m #94510B  o #777B90  p #D47603 (gold shade)  q #DA6D40 (skin mid)
#   u #F1955D (skin lit)  v #F6B205 (gold)  w #B5BAD2  A #E9EBF2
SKIN_LIT, SKIN_SHADE, GLOVE_LIT, GLOVE_SHADE = "u", "q", "i", "d"

# ------------------------------------------------------------------------------------------------ the design's parts
# the arms on the hips taken off when an arm moves (rows: (first, last) column): the near arm under its shoulder (the
# elbow, the forearm, the glove on the hip), the far forearm and glove on the hip
NEAR_OFF = {78: (53, 58), 79: (53, 59), 80: (54, 60), 81: (55, 60), 82: (56, 60)}
FAR_OFF = {79: (70, 72), 80: (71, 73), 81: (71, 72), 82: (70, 70)}
# what they covered, filled in (first column, letters): the torso's near side - the red top down the side, the corset,
# its outline a column inside the shoulder's; the hair behind the far forearm (navy), the torso's outline on column 70
NEAR_FILL = {78: (57, "0q"), 79: (57, "0ggdd"), 80: (57, "0hgd0"), 81: (57, "0dih0"), 82: (57, "0dii0")}
FAR_FILL = {79: (70, "0ee"), 80: (71, "eee"), 81: (71, "ee"), 82: (70, "0")}
NEAR_SH = (55.0, 77.0)                 # the near shoulder's outer edge: the arm's first step
FAR_SH = (71.0, 78.0)                  # the torso's upper right corner, right of the corset's edge (column 70)
ARM_STEPS, GLOVE_STEPS = 6, 2          # skin steps along the arm, then the glove: the design's akimbo arm's length
# the hair falling behind the far shoulder (the far arm and what it holds pass over it, under everything else)
HAIR_BOX = (66, 90, 71, 79)            # rows r0..r1, columns c0..c1
# the greatsword on her back: the hilt and its ribbon over the near shoulder, the blade under the hip by the far boot
BACK_HILT = {61: (52, 54), 62: (52, 54), 63: (52, 54), 64: (52, 54), 65: (52, 55), 66: (52, 55), 67: (52, 55),
             68: (52, 55), 69: (52, 55), 70: (52, 55), 71: (53, 56), 72: (54, 56), 73: (54, 55), 74: (54, 55)}
BLADE_ROWS = {**{r: (76, 84) for r in range(86, 97)}, 97: (78, 84), 98: (78, 84)}

# the long revolver, pointing right, the grip in the hand at GUN_GRIP (letters: rigkit.Design.letters)
GUN = [
    "....000000000",
    "...0vpAAAAAA0",
    "..0oooowwwww0",
    ".0ff00000000.",
    "0ff0.........",
    "000..........",
]
GUN_GRIP = (2.0, 3.5)
BLADE = 22                             # the held greatsword's blade (level), squares
DIAG_BLADE = 14                        # the same at 45 degrees, steps


def unit_from(rows, letters, joint):
    s = np.zeros((len(rows), len(rows[0]), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != ".":
                s[y, x, :3] = letters[ch]
                s[y, x, 3] = 255
    return K.Part(s, joint)


def outlined(g):
    H, W = len(g), len(g[0])
    out = [r[:] for r in g]
    for y in range(H):
        for x in range(W):
            if g[y][x] == "." and any(0 <= y + dy < H and 0 <= x + dx < W and g[y + dy][x + dx] != "."
                                      for dy, dx in K.N4):
                out[y][x] = "0"
    return ["".join(r) for r in out]


def sword_rows(blade=BLADE):
    """The greatsword level to the image right, the grip in the hand (column 2): a red pommel, the dark grip, a gold
    guard 4 tall, the blade 3 tall (silver edge on top, steel, dark back) tapering to the point, one outline ring."""
    W = 6 + blade + 1
    g = [["."] * W for _ in range(7)]
    g[3][1], g[4][1] = "k", "b"
    g[3][2], g[4][2] = "f", "f"
    g[3][3], g[4][3] = "f", "f"
    for y, ch in zip(range(2, 6), "vppv"):
        g[y][4] = ch
    for x in range(5, 5 + blade):
        left = 5 + blade - 1 - x
        g[3][x] = "A"
        if left >= 1:
            g[4][x] = "o"
        if left >= 2:
            g[5][x] = "e"
    return outlined(g)


def diag_rows(blade=DIAG_BLADE):
    """The greatsword at 45 degrees pointing down-left from the grip (the grip at the top right), for
    rigkit.orientations: pommel, grip, a gold guard across the line, the blade 3 wide tapering, one outline ring."""
    n = 3 + blade
    W = n + 7
    g = [["."] * W for _ in range(n + 5)]

    def put(x, y, ch):
        if 0 <= y < len(g) and 0 <= x < W:
            g[y][x] = ch
    x0, y0 = n + 3, 2
    put(x0 + 1, y0 - 1, "k")
    for t in range(n):
        x, y = x0 - t, y0 + t
        if t < 2:
            put(x, y, "f"), put(x + 1, y, "f")
        elif t == 2:
            put(x - 1, y - 1, "v"), put(x, y, "p"), put(x + 1, y, "p"), put(x + 2, y + 1, "v")
        else:
            left = n - 1 - t
            mats = ("e", "o", "A") if left >= 2 else (("o", "A") if left == 1 else ("A",))
            for k, ch in enumerate(mats):
                put(x - 1 + k + (3 - len(mats)), y, ch)
    return outlined(g), (x0 + 0.5, y0 + 0.5)


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = D.a
        self.L = L = D.letters()
        self.rgba = {k: np.array(tuple(c) + (255,), np.uint8) for k, c in L.items()}
        self.gun = unit_from(GUN, L, GUN_GRIP)                  # pointing right
        self.gun_l = self.gun.flip_h()                          # pointing left
        lvl = unit_from(sword_rows(), L, (2.5, 3.5))
        rows, joint = diag_rows()
        dg = K.orientations(unit_from(rows, L, joint))
        self.sword = {"r": lvl, "l": lvl.flip_h(), "u": K.rot90(lvl, 3), "d": K.rot90(lvl, 1), **dg}
        self.sword_m = K.mask_rows(BACK_HILT) | K.mask_rows(BLADE_ROWS)
        r0, r1, c0, c1 = HAIR_BOX
        skin = K.colour_mask(a, [L["u"], L["q"]])
        self.hair = np.zeros(a.shape[:2], bool)
        self.hair[r0:r1 + 1, c0:c1 + 1] = True
        self.hair &= ~skin & ~K.mask_rows(BLADE_ROWS)
        self.hair |= K.mask_rows(FAR_OFF)                       # the far forearm's place: the hair once it moves


# ------------------------------------------------------------------------------------------------ drawing
def arm_layers(P, sh, deg, steps=ARM_STEPS, glove=GLOVE_STEPS):
    """A straight arm from the shoulder square `sh`, `deg` from hanging (+90 image right, -90 left, 180 up): each step
    along it a cross-section of 3 squares (skin lit, lit, shade - the shade toward the bottom, or the back when it
    hangs), the glove's last two steps (lit, lit, shade); returns its outline ring, skin, glove ({(x, y): rgba}) and
    the hand (the glove's first middle square)."""
    t = math.radians(deg)
    dx, dy = math.sin(t), math.cos(t)
    horiz = abs(dx) >= abs(dy)
    cells, hand, glove_q = {}, None, set()
    # near 45 degrees a cross-section of 3 squares a step is thinner across the arm than the level arm: one more
    # (the design's own slanted upper arm is 4 squares a row)
    across = (-1, 0, 1, 2) if min(abs(dx), abs(dy)) / max(abs(dx), abs(dy)) > 0.5 else (-1, 0, 1)
    for i in range(steps + glove):
        if horiz:
            x = int(round(sh[0])) + i * (1 if dx > 0 else -1)
            yc = sh[1] + i * dy / abs(dx)
            sq = [(x, int(math.floor(yc + 0.5)) + k) for k in across]
        else:
            y = int(round(sh[1])) + i * (1 if dy > 0 else -1)
            xc = sh[0] + i * dx / abs(dy)
            sq = [(int(math.floor(xc + 0.5)) + k, y) for k in across]
        g = i >= steps
        n = len(sq)
        for k, q in enumerate(sq):
            lit = k < n - 1
            cells[q] = (GLOVE_LIT if lit else GLOVE_SHADE) if g else (SKIN_LIT if lit else SKIN_SHADE)
            if g:
                glove_q.add(q)
        if i == steps:
            hand = sq[1]
    # a slanted arm's steps meet at corners: the square between two of one colour two apart takes it (3 thick stays)
    add = {}
    for (x, y), ch in cells.items():
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
    skin = {q: P.rgba[ch] for q, ch in cells.items() if q not in glove_q}
    glove = {q: P.rgba[ch] for q, ch in cells.items() if q in glove_q}
    return ring, skin, glove, hand


def held(P, sh, deg, part):
    """An arm holding a rigid weapon by its grip: (colour squares, outline squares) - the weapon, the arm over its grip
    and pommel, the glove round the grip on top; the outline the arm's and the weapon's where neither is coloured (the
    weapon's ring never cuts across the arm)."""
    ring, skin, glove, hand = arm_layers(P, sh, deg)
    w = part_cells(part, (hand[0] + 0.5, hand[1] + 0.5))
    ink = P.rgba["0"]
    col = {q: v for q, v in w.items() if not (v == ink).all()}
    col.update(skin)
    col.update(glove)
    rng = {q: v for q, v in list(w.items()) + list(ring.items()) if q not in col and (v == ink).all()}
    return col, rng


def put_cells(c, cells, ok=None):
    for (x, y), v in cells.items():
        if 0 <= y <= SOLES and 0 <= x < c.shape[1] and (ok is None or ok(x, y)):
            c[y, x] = v


def part_cells(part, at):
    """{(x, y): rgba} of a rigid part with its joint on the canvas point `at`."""
    ox = int(math.floor(at[0] - part.j[0] + 1e-9))
    oy = int(math.floor(at[1] - part.j[1] + 1e-9))
    ys, xs = np.nonzero(part.s[..., 3])
    return {(int(x) + ox, int(y) + oy): part.s[y, x].copy() for y, x in zip(ys, xs)}


def fill(P, a, spec):
    for y, (x0, s) in spec.items():
        for i, ch in enumerate(s):
            a[y, x0 + i] = P.rgba[ch]


def shifted(a, dx, dy):
    return K.shifted(a, dx, dy) if (dx or dy) else a


# ------------------------------------------------------------------------------------------------ standing actions
# per frame: "far" / "near": (degrees from hanging, weapon, way) - weapon "gun" (way "r" / "l") or "sword" (way r l u d
# ur dr dl ul); an arm not given stays on the hip as drawn. "move": the whole frame (dx, dy); "sword_off": the sword
# taken off her back.
G, S = "gun", "sword"
STAND = {
    # the shot (release frame 4): the gun drawn up from the hip, level, fired with a kick (the whole figure a column
    # back), held, lowered
    "attack": [{"far": (45, G, "r")}, {"far": (70, G, "r")}, {"far": (90, G, "r")},
               {"far": (90, G, "r"), "move": (-1, 0)}, {"far": (90, G, "r")}, {"far": (60, G, "r")}],
    # Q, gun (release frame 3): drawn, aimed a little high, fired with a bigger kick, lowered after the shot, held,
    # lowered
    "skill": [{"far": (60, G, "r")}, {"far": (95, G, "r"), "move": (1, 0)}, {"far": (95, G, "r"), "move": (-1, 0)},
              {"far": (80, G, "r"), "move": (-1, 0)}, {"far": (88, G, "r")}, {"far": (60, G, "r")}],
    # the sword slash (release frame 4): the blade raised up-right beside her head, drawn back, levelled, chopped down
    # and forward in a lunge, held, home
    "attack_m": [{"far": (150, S, "ur"), "sword_off": 1}, {"far": (160, S, "ur"), "move": (-1, 0), "sword_off": 1},
                 {"far": (100, S, "r"), "move": (1, 0), "sword_off": 1},
                 {"far": (55, S, "dr"), "move": (2, 0), "sword_off": 1},
                 {"far": (55, S, "dr"), "move": (1, 0), "sword_off": 1}, {}],
    # Q, sword (release frame 4): raised, drawn back over her head (the blade up behind it), raised again, a lunge with
    # the blade swept level and far, held, home
    "skill_m": [{"far": (150, S, "ur"), "sword_off": 1}, {"far": (178, S, "ul"), "move": (-1, 0), "sword_off": 1},
                {"far": (150, S, "ur"), "sword_off": 1}, {"far": (95, S, "r"), "move": (2, 0), "sword_off": 1},
                {"far": (95, S, "r"), "move": (1, 0), "sword_off": 1}, {}],
    # E then W: the dash (the blade levelled ahead, the whole figure forward), the landing chop, the spin - the blade
    # round her a quarter a frame: out front, low front, over her head to the back, raised - twice, then home (the hand
    # and the blade always in sight: never behind her body)
    "skill2": [{"far": (95, S, "r"), "move": (2, 0), "sword_off": 1},
               {"far": (100, S, "r"), "move": (3, 0), "sword_off": 1},
               {"far": (55, S, "dr"), "move": (1, 0), "sword_off": 1}]
              + [f for _ in range(2) for f in (
                  {"far": (95, S, "r"), "sword_off": 1}, {"far": (55, S, "dr"), "sword_off": 1},
                  {"far": (178, S, "ul"), "sword_off": 1}, {"far": (150, S, "ur"), "sword_off": 1})]
              + [{}],
    # R: both pistols out to both sides, firing as she turns - the arms see-sawing (one up as the other goes down)
    "ult": [{"far": (70, G, "r"), "near": (-70, G, "l")}]
           + [{"far": (90 + (0, 18, 0, -18)[k % 4], G, "r"), "near": (-90 + (0, 18, 0, -18)[k % 4], G, "l")}
              for k in range(8)]
           + [{}],
    "hit": [{"move": (-1, 0)}, {"move": (-1, 0)}],
}


def stand(P, pose):
    a = P.D.a.copy()
    if pose.get("sword_off"):
        a[P.sword_m] = 0
    near, far = pose.get("near"), pose.get("far")
    if near is not None:
        for y, (x0, x1) in NEAR_OFF.items():
            a[y, x0:x1 + 1] = 0
        fill(P, a, NEAR_FILL)
    if far is not None:
        for y, (x0, x1) in FAR_OFF.items():
            a[y, x0:x1 + 1] = 0
        fill(P, a, FAR_FILL)
    body = a[..., 3] > 0
    ink = (a[..., :3] == P.rgba["0"][:3]).all(-1) & body
    behind = lambda x, y: not body[y, x] or P.hair[y, x]          # the far arm: over the hair, under the rest
    clear = lambda x, y: not body[y, x] or ink[y, x]               # the near arm's outline: never over the body's
    c = a.copy()                                                   # colours (the shoulder runs into the arm)
    for key, sh, ok, ok_ring in (("far", FAR_SH, behind, behind), ("near", NEAR_SH, None, clear)):
        spec = pose.get(key)
        if spec is None:
            continue
        deg, weapon, way = spec
        part = (P.gun if way == "r" else P.gun_l) if weapon == G else P.sword[way]
        col, rng = held(P, sh, deg, part)
        put_cells(c, rng, ok_ring)
        put_cells(c, col, ok)
    c[SOLES + 1:] = 0
    dx, dy = pose.get("move", (0, 0))
    return shifted(c, dx, dy)


# ------------------------------------------------------------------------------------------------ the run
LEG_TOP = 89                           # the body keeps the rows above (the belt, the holster, the thigh tops)
HOLSTER_TIP = {89: (53, 55), 90: (53, 55)}      # the near holster's tip under the belt stays with the body
HIPS = {"near": 61.5, "far": 67.5}     # the leg tops' middles on row 89: under the hips, 6 apart (the A-stance's
                                       # are 10: the feet met and the legs made a lump instead of crossing)
LEG_ROW, BAND_ROW = "ddii", "bggg"      # a leg row (two shade, two lit), the red band at the knee
FOOT = ["dddiii", "pdddiiii"]          # the far boot's foot as drawn (toe forward), from the shin's first column
FOOT_UP = ["ddii", "pdii"]             # a lifted foot, toe down
# the far leg a shade darker (the design's own darker squares: the green's shade for its lit, the navy for its shade,
# the band's dark reds) - drawn alike, the two crossing legs were one dark lump
FAR_SHADE = {"d": "e", "i": "d", "g": "b", "b": "a"}
# one leg's cycle (8 frames): the knee's and the ankle's columns from the hip (+ forward = image right), the foot's
# lift (rows): contact, loading, mid-stance, push, toe-off, kick, passing, reach
CYCLE = [(2, 5, 0), (2, 2, 0), (1, -1, 0), (-1, -4, 0), (-2, -5, 1), (-1, -5, 3), (2, -1, 3), (3, 4, 1)]
BOB = [1, 1, 0, 0, 1, 1, 0, 0]          # the body a row lower at each contact and loading


def leg_cells(P, hip_x, top, knee_dx, ankle_dx, lift, far=False):
    """A leg of the design's rows: thigh rows, the band, shin rows, the foot (its last row on 98 - lift), each row's
    middle on the line hip -> knee -> ankle (the far leg a shade darker); one outline ring."""
    bottom = (SOLES - 1) - lift
    rows = bottom - top + 1 - 2
    nt = max(1, min(3, rows - 3))
    ns = rows - nt - 1
    cells = {}

    def row(y, xm, pat):
        x0 = int(math.floor(xm - len(pat) / 2 + 0.5))
        for i, ch in enumerate(pat):
            cells[(x0 + i, y)] = ch
    kx, ax = hip_x + knee_dx, hip_x + ankle_dx
    y = top
    for i in range(nt):
        row(y, hip_x + (kx - hip_x) * i / nt, LEG_ROW)
        y += 1
    row(y, kx, BAND_ROW)
    y += 1
    for i in range(1, ns + 1):
        row(y, kx + (ax - kx) * i / (ns + 1), LEG_ROW)
        y += 1
    x0 = int(math.floor(ax - 2 + 0.5))
    for i, pat in enumerate(FOOT_UP if lift >= 2 else FOOT):
        for j, ch in enumerate(pat):
            cells[(x0 + j, y + i)] = ch
    out = {}
    for (x, y) in cells:
        for ox, oy in K.N4:
            q = (x + ox, y + oy)
            if q not in cells:
                out[q] = P.rgba["0"]
    out.update({q: P.rgba[FAR_SHADE.get(ch, ch) if far else ch] for q, ch in cells.items()})
    return out


def run_parts(P):
    a = P.D.a
    body = a.copy()
    body[LEG_TOP:] = 0
    tip = K.mask_rows(HOLSTER_TIP)
    body[tip] = a[tip]
    blade = np.zeros_like(a)
    m = K.mask_rows(BLADE_ROWS)
    blade[m] = a[m]
    return body, blade


def run_frame(P, k):
    body, blade = run_parts(P)
    dy = BOB[k]
    c = np.zeros((128, 128, 4), np.uint8)
    K.put(c, shifted(blade, 0, dy), 0, 0)
    for side, ph in (("far", (k + 4) % 8), ("near", k)):
        kd, ad, lift = CYCLE[ph]
        put_cells(c, leg_cells(P, HIPS[side], LEG_TOP + dy, kd, ad, lift, side == "far"))
    K.put(c, shifted(body, 0, dy), 0, 0)
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
    ys, xs = np.nonzero(a[..., 3] > 0)
    return shifted(a, dx, SOLES - ys.max())


def laid_out(P):
    """The standing figure made ready to lie down (league_sivir's death): the sword off her back, the legs together and
    straight under the hips (the design's A-stance turned a quarter would raise one leg), both arms down along her
    sides - so the turned figure lies flat."""
    a = P.D.a.copy()
    a[P.sword_m] = 0
    a[LEG_TOP:] = 0
    tip = K.mask_rows(HOLSTER_TIP)
    a[tip] = P.D.a[tip]
    for y, (x0, x1) in list(NEAR_OFF.items()) + list(FAR_OFF.items()):
        a[y, x0:x1 + 1] = 0
    fill(P, a, NEAR_FILL)
    fill(P, a, FAR_FILL)
    for hip, far in ((66.5, True), (61.5, False)):      # the far leg first, the near one in front of it
        put_cells(a, leg_cells(P, hip, LEG_TOP, 0, 0, 0, far))
    body = a[..., 3] > 0
    ink = (a[..., :3] == P.rgba["0"][:3]).all(-1) & body
    behind = lambda x, y: not body[y, x] or P.hair[y, x]
    clear = lambda x, y: not body[y, x] or ink[y, x]
    for sh, deg, ok, ok_ring in ((FAR_SH, -8, behind, behind), (NEAR_SH, 12, None, clear)):
        ring, skin, glove, _ = arm_layers(P, sh, deg)
        put_cells(a, ring, ok_ring)
        put_cells(a, {**skin, **glove}, ok)
    a[SOLES + 1:] = 0
    return finish(P, a)


def lying(P):
    """On her back: the laid-out figure a quarter turn counter-clockwise - the head to the left, the face up, the
    boots' toes up at the right - on the ground line."""
    a = laid_out(P)
    ys, xs = np.nonzero(a[..., 3] > 0)
    rot = np.rot90(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 1).copy()
    out = np.zeros_like(a)
    h, w = rot.shape[:2]
    x0 = 64 - w // 2 + 2
    out[SOLES + 1 - h:SOLES + 1, x0:x0 + w] = rot
    return out


def sword_on_ground(P):
    """The greatsword lying level on the ground behind her head (its point to the left)."""
    s = P.sword["l"].s
    c = np.zeros((128, 128, 4), np.uint8)
    ys, _ = np.nonzero(s[..., 3])
    K.put(c, s, 28, SOLES - ys.max())
    return c


DEAD = ["hit", "knocked", ("tilt", 45), ("lying", 1), ("lying", 0), ("lying", 0), ("lying", 0), ("lying", 0)]


def dead_frame(P, i):
    what = DEAD[i]
    if what == "hit":
        return stand(P, {"move": (-1, 0)})
    if what == "knocked":
        return stand(P, {"move": (-2, -1)})
    out = sword_on_ground(P)
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
    """rigkit.finish, then the open gaps the raw frame has (2+ squares: between the legs, the design's own beside the
    far hand) cleared again where the finish filled them with a colour (its pinhole fill takes them for pinholes - the
    run's legs had a lilac patch between them)."""
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
    fin = lambda a: finish(P, a)
    if tag == "run":
        return [fin(run_frame(P, k)) for k in range(n)]
    if tag == "dead":
        return [fin(dead_frame(P, k)) for k in range(n)]
    if tag in STAND:
        return [fin(stand(P, p)) for p in STAND[tag]]
    return [P.D.a.copy() for _ in range(n)]


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
        return
    bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differ:", bad or "none")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

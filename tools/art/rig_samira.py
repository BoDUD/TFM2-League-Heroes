#!/usr/bin/env python3
"""Samira's action strips posed from the approved design's own parts (the casting body = the idle's).

    python tools/art/rig_samira.py [--check] [--review DIR] [--tags attack,skill]

Second design (2026-10-09, tools/art/design_samira2.py: the user's ChatGPT picture cut to game size): the same pose
family as the first - both hands on her hips, the greatsword slung behind her (the hilt with its red tassel up at the
near shoulder, the blade's point out at the lower right), the braid at image right, a pistol in each gold holster - so
every action is built the way the first design's v3 was (the user's notes on v1/v2 still hold: 「手变形 走路没交叉步
死亡动画完全错误 模型变形」「手臂对吗 走路对吗？」), with the new design's own squares (the user: 「OK 动作帧全要大改吧」):
- arms: straight, three squares thick in the design's skin (lit, lit, shade toward the bottom / the back), a gold cuff
  step, the dark brown glove's two squares at the hand, one outline ring; the near arm leaves the near shoulder at its
  outer edge and is drawn over the body, the far arm leaves the torso's upper right corner, under the torso and over
  the braid. Where an arm leaves the hip, what it covered is filled in (NEAR_FILL: the belt under the near hand).
- weapons: the long revolver level in the glove; the greatsword (taken off her back: the hilt, tassel and guard at the
  near shoulder, the blade's point at the lower right) in eight exact orientations (level, upright, 45 degrees; never
  RotSprite), in the far hand. What the blade hid of the hair by the near shoulder is filled in (SWORD_FILL).
- the run (League's 8 frames): the upper body the idle's (both hands at the waist, as League's run carries them, the
  holsters and pistols with it), a row lower at each contact; each leg the design's own trouser rows (3 wide) laid
  along hip -> knee -> ankle, then the boot (red cuff, white buckle, the toe forward); the near boot crosses in front of
  the far one (the far leg a shade darker), the swinging foot lifted up to 3 rows; the greatsword's lower blade bobs
  with the body under the legs.
- the death (league_sivir's): struck back, knocked, falling (the whole figure turned 45 degrees), lying on her back (a
  quarter turn), the greatsword on the ground by her head.
Every frame is finished alike (rigkit.finish: pinholes, the outline closed round moved edges, crumbs dropped).
Writes assets/source/native/samira_<tag>.png (8x, 128x96 cells) and samira_cells.json; then tools/art/import_native.py.
The first design's version of this script is in git history (before 2026-10-09).
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

# the design's 25 colours, dark to light, pinned (rigkit.Design.letters gives them these letters)
PALETTE = ["050206", "2A0109", "101624", "0C231E", "291E22", "0F3627", "173343", "930222", "343743", "48312F", "1B4E3B",
           "B9112A", "714638", "7E4924", "9D5D40", "B47128", "7E8086", "C37950", "CD8B30", "E5A742", "B0B2BB", "C2C5D4",
           "FBCC51", "E6E5E0", "F3F2EF"]
#   0 ink  a #2A0109  b #101624 (hair dark)  c #0C231E (green dark)  d #291E22 (glove dark)  e #0F3627 (green)
#   f #173343 (hair)  g #930222 (red dark)  h #343743 (steel dark)  i #48312F (glove)  j #1B4E3B (green lit)
#   k #B9112A (red)  l #714638 (skin dark)  m #7E4924  n #9D5D40 (skin shade)  o #B47128 (gold dark)  p #7E8086 (steel)
#   q #C37950 (skin)  r #CD8B30 (gold)  s #E5A742 (gold lit)  t #B0B2BB (silver)  u #C2C5D4 (silver lit)
#   v #FBCC51 (gold bright)  w #E6E5E0 (white)  x #F3F2EF (white bright)
SKIN_LIT, SKIN_SHADE, GLOVE_LIT, GLOVE_SHADE, CUFF_LIT, CUFF_SHADE = "q", "n", "i", "d", "s", "o"

# ------------------------------------------------------------------------------------------------ the design's parts
# the arms on the hips taken off when an arm moves (rows: (first, last) column): the near arm under its shoulder (the
# upper arm, the elbow, the gold cuff, the glove on the hip), the far arm under its shoulder (to the glove on the hip)
NEAR_OFF = {79: (52, 56), 80: (51, 57), 81: (51, 54), 82: (50, 54), 83: (51, 54), 84: (52, 56), 85: (53, 57)}
FAR_OFF = {80: (67, 69), 81: (67, 70), 82: (67, 71), 83: (67, 72), 84: (67, 70), 85: (67, 68)}
# what the near glove covered, filled in (first column, letters): the belt at the hip down to the holster's top
NEAR_FILL = {84: (55, "0dd"), 85: (55, "0dd")}
NEAR_SH = (55.0, 79.0)                 # the near shoulder's outer edge: the arm's first step
FAR_SH = (67.0, 80.0)                  # the torso's upper right corner, under the far shoulder
ARM_STEPS, GLOVE_STEPS = 5, 2          # skin steps along the arm (the last a gold cuff), then the glove
# the braid behind the far shoulder (the far arm and what it holds pass over it, under everything else)
HAIR_BOX = (76, 86, 69, 75)            # rows r0..r1, columns c0..c1
# the greatsword on her back: the upper part as design_samira2.SWORD lists it (pommel, tassel, grip, guard, the blade
# down to the near shoulder) and the lower blade by the far boot (the far holster's pistol barrel beside it stays)
SWORD_UP = [(46, 64), (47, 64), (46, 65), (47, 65), (48, 65), (46, 66), (47, 66), (48, 66), (45, 67), (46, 67), (47, 67),
            (48, 67), (45, 68), (49, 68), (49, 69), (51, 69), (50, 70), (51, 70), (49, 71), (50, 71), (49, 72), (50, 72),
            (51, 72), (50, 73), (51, 73), (50, 74), (51, 74), (52, 74), (51, 75), (52, 75), (53, 75), (52, 76), (53, 76),
            (54, 76), (55, 76), (52, 77), (53, 77), (54, 77), (53, 78)]
BLADE_LOW = [(70, 88), (71, 89), (71, 90), (72, 90), (71, 91), (72, 91), (70, 92), (71, 92), (72, 92), (73, 92),
             (72, 93), (73, 93), (74, 93), (73, 94), (74, 94), (75, 94), (73, 95), (74, 95), (75, 95), (74, 96),
             (75, 96), (75, 97)]
# what the blade hid by the near shoulder once it is off her back: the hair falling onto the shoulder
SWORD_FILL = {75: (54, "b"), 76: (53, "bbb"), 77: (53, "bb")}

# the long revolver, pointing right, the grip in the hand at GUN_GRIP (letters: the pinned palette's)
GUN = [
    "....000000000",
    "...0voxxxxxx0",
    "..0ppppttttt0",
    ".0dd00000000.",
    "0dd0.........",
    "000..........",
]
GUN_GRIP = (2.0, 3.5)
BLADE = 20                             # the held greatsword's blade (level), squares
DIAG_BLADE = 13                        # the same at 45 degrees, steps


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
    g[3][1], g[4][1] = "k", "g"
    g[3][2], g[4][2] = "h", "h"
    g[3][3], g[4][3] = "h", "h"
    for y, ch in zip(range(2, 6), "vrrv"):
        g[y][4] = ch
    for x in range(5, 5 + blade):
        left = 5 + blade - 1 - x
        g[3][x] = "u"
        if left >= 1:
            g[4][x] = "t"
        if left >= 2:
            g[5][x] = "h"
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
            put(x, y, "h"), put(x + 1, y, "h")
        elif t == 2:
            put(x - 1, y - 1, "v"), put(x, y, "r"), put(x + 1, y, "r"), put(x + 2, y + 1, "v")
        else:
            left = n - 1 - t
            mats = ("h", "t", "u") if left >= 2 else (("t", "u") if left == 1 else ("u",))
            for k, ch in enumerate(mats):
                put(x - 1 + k + (3 - len(mats)), y, ch)
    return outlined(g), (x0 + 0.5, y0 + 0.5)


def mask_of(cells, shape=(128, 128)):
    m = np.zeros(shape, bool)
    for x, y in cells:
        m[y, x] = True
    return m


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        D.palette = [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in PALETTE]
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
        self.sword_m = mask_of(SWORD_UP) | mask_of(BLADE_LOW)
        self.blade_low = mask_of(BLADE_LOW)
        r0, r1, c0, c1 = HAIR_BOX
        skin = K.colour_mask(a, [L["q"], L["n"], L["l"]])
        self.hair = np.zeros(a.shape[:2], bool)
        self.hair[r0:r1 + 1, c0:c1 + 1] = True
        self.hair &= ~skin & ~self.blade_low
        self.hair |= K.mask_rows(FAR_OFF)                       # the far forearm's place: free once it moves


# ------------------------------------------------------------------------------------------------ drawing
def arm_layers(P, sh, deg, steps=ARM_STEPS, glove=GLOVE_STEPS):
    """A straight arm from the shoulder square `sh`, `deg` from hanging (+90 image right, -90 left, 180 up): each step
    along it a cross-section of 3 squares (skin lit, lit, shade - the shade toward the bottom, or the back when it
    hangs), the last skin step a gold cuff, the glove's last two steps (lit, lit, shade); returns its outline ring,
    skin, glove ({(x, y): rgba}) and the hand (the glove's first middle square)."""
    t = math.radians(deg)
    dx, dy = math.sin(t), math.cos(t)
    horiz = abs(dx) >= abs(dy)
    cells, hand, glove_q = {}, None, set()
    # near 45 degrees a cross-section of 3 squares a step is thinner across the arm than the level arm: one more
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
        cuff = i == steps - 1
        n = len(sq)
        for k, q in enumerate(sq):
            lit = k < n - 1
            if g:
                cells[q] = GLOVE_LIT if lit else GLOVE_SHADE
                glove_q.add(q)
            elif cuff:
                cells[q] = CUFF_LIT if lit else CUFF_SHADE
            else:
                cells[q] = SKIN_LIT if lit else SKIN_SHADE
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


def sword_off(P, a):
    """The greatsword taken off her back: its squares cleared, the hair it hid by the near shoulder filled in."""
    a[P.sword_m] = 0
    fill(P, a, SWORD_FILL)
    return a


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
        sword_off(P, a)
    near, far = pose.get("near"), pose.get("far")
    if near is not None:
        for y, (x0, x1) in NEAR_OFF.items():
            a[y, x0:x1 + 1] = 0
        fill(P, a, NEAR_FILL)
    if far is not None:
        for y, (x0, x1) in FAR_OFF.items():
            a[y, x0:x1 + 1] = 0
    body = a[..., 3] > 0
    ink = (a[..., :3] == P.rgba["0"][:3]).all(-1) & body
    behind = lambda x, y: not body[y, x] or P.hair[y, x]          # the far arm: over the braid, under the rest
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
LEG_TOP = 88                           # the body keeps the rows above (the belt, the holsters' tops)
# the holsters and their pistols under LEG_TOP stay with the body
HOLSTERS = {88: [(52, 57), (66, 69)], 89: [(52, 57), (66, 70)], 90: [(52, 57), (67, 70)], 91: [(52, 56), (67, 70)],
            92: [(52, 55), (68, 69)], 93: [(53, 54)]}
HIPS = {"near": 60.0, "far": 64.5}     # the leg tops' middles on row 88 (the trousers' own columns)
LEG_ROW = "cjc"                        # a trouser row (shade, lit, shade)
# the boot under the trousers, from the ankle's middle (column offset of the first letter, letters): the red cuff, the
# dark red and white buckle, the boot and the white buckle, the foot (heel to toe, the toe forward)
BOOT = [(-1, "kck"), (-1, "ggw"), (0, "cx"), (-1, "ecjj")]
BOOT_UP = [(-1, "kck"), (-1, "ggw"), (0, "cx"), (0, "cjj")]     # a lifted foot, toe down
# the far leg a shade darker (the design's own darker squares) - drawn alike, the two crossing legs were one dark lump
FAR_SHADE = {"j": "e", "e": "c", "k": "g", "g": "a", "w": "t", "x": "u"}
# one leg's cycle (8 frames): the knee's and the ankle's columns from the hip (+ forward = image right), the foot's
# lift (rows): contact, loading, mid-stance, push, toe-off, kick, passing, reach
CYCLE = [(2, 5, 0), (2, 2, 0), (1, -1, 0), (-1, -4, 0), (-2, -5, 1), (-1, -5, 3), (2, -1, 3), (3, 4, 1)]
BOB = [1, 1, 0, 0, 1, 1, 0, 0]          # the body a row lower at each contact and loading


def leg_cells(P, hip_x, top, knee_dx, ankle_dx, lift, far=False):
    """A leg of the design's rows: trouser rows along hip -> knee -> ankle, then the boot (its last row on 98 - lift),
    each row's middle on the line; one outline ring (the far leg a shade darker)."""
    boot = BOOT_UP if lift >= 2 else BOOT
    bottom = (SOLES - 1) - lift
    first_boot = bottom - len(boot) + 1
    rows = first_boot - top
    nt = max(1, rows // 2)
    ns = rows - nt
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
    for i in range(ns):
        row(y, kx + (ax - kx) * (i + 1) / ns, LEG_ROW)
        y += 1
    x_mid = int(math.floor(ax + 0.5))
    for i, (off, pat) in enumerate(boot):
        for j, ch in enumerate(pat):
            cells[(x_mid + off + j, first_boot + i)] = ch
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
    for y, spans in HOLSTERS.items():
        for x0, x1 in spans:
            body[y, x0:x1 + 1] = a[y, x0:x1 + 1]
    blade = np.zeros_like(a)
    blade[P.blade_low] = a[P.blade_low]
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
    sword_off(P, a)
    a[LEG_TOP:] = 0
    for y, spans in HOLSTERS.items():
        for x0, x1 in spans:
            a[y, x0:x1 + 1] = P.D.a[y, x0:x1 + 1]
    a[P.blade_low] = 0
    for y, (x0, x1) in list(NEAR_OFF.items()) + list(FAR_OFF.items()):
        a[y, x0:x1 + 1] = 0
    fill(P, a, NEAR_FILL)
    for hip, far in ((HIPS["far"], True), (HIPS["near"], False)):      # the far leg first, the near one in front
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
    """rigkit.finish, then the open gaps the raw frame has (2+ squares: between the legs, beside the hands on the
    hips) cleared again where the finish filled them with a colour (its pinhole fill takes them for pinholes)."""
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

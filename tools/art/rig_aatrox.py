#!/usr/bin/env python3
"""Aatrox's action strips put together from the approved design's own parts (2026-10-03, the frame audit 2026-10-04).

    python tools/art/rig_aatrox.py [--check] [--out DIR]

Codex's strips (assets/source/aatrox/codex_strips/, its animation_source.py) cut the design into layers and moved them:
the body kept only a 4-square column under the chest (the hips and thighs cut away), was shifted 1-2 squares off the
legs, the arms were drawn as tubes and the ult's wings as flat polygons. The user: 「腿变形还有上下身体脱节 开大时大招
翅膀极度奇怪」. Here every frame keeps the design whole and moves only what the action moves:
- BODY: the design without the blade, the near arm and its fist (NEAR_ARM) - the near hip painted where the fist and
  the grip covered it (NEAR_HIP) - and, where the far red arm moves (W, the ult), without it (FAR_ARM, the waist
  painted: WAIST). Head, wings, chest, hips and both legs stay square for square on the idle's place (the user's rule:
  every standing pose on the idle's own legs). The cut keeps every outline square of the design that still outlines
  something (the horns' crest, the wing tips, the boots: the audit found 9-13 of them deleted in every moved frame).
- the near arm: shoulder -> elbow -> fist in the gauntlet's plates (plated_arm: three squares under the pauldron, then
  two like the idle's arm, lit '3' / '2' / shadow '1', a dark plate break at the elbow) with one outline ring, the fist
  a 3 x 3 block on the grip; every fist is placed within the arm's reach (REACH) so the elbow bends - a fist out of
  reach used to be clamped into a straight pipe (attack 3, W 4-5). The far red arm the same in the idle red arm's
  reds, the claw solid (CLAW), three squares across with its own outline ring over the far wing (W).
- the greatsword: the design's own blade, never resampled: the drawn blade (slanted, BASE) and its level copy
  (BLADE_LEVEL: the same squares, its columns moved up to the grip's row, two columns longer so it keeps the design's
  length) mirrored and transposed - twelve exact directions (ORIENT) - its grip in the fist. RotSprite broke the blade
  up at the old angles (teeth on both edges, dotted tips, black squares hanging off it).
- the idle: the design, its breath drawn in frames 3-5 (BREATH: the body a row lower, each leg losing one of its two
  equal shin rows - import_native's row seam across the boots squashed them).
- the hit: the upper body turned back about the hips (RotSprite; its doubled outlines given back their colours,
  restore_inside) on the idle's own legs, then moved whole a square back (HIT: RotSprite at 3 degrees thickened it), the
  blade hanging from the fist as drawn, the head pasted square for square; a row shear split the head and jogged the
  knees.
- the death (League's Death): turned back about the near heel, the boots rolling with him (RotSprite, each leg turned
  and cleaned on its own, the head laid on square for square, no wing spike over its crest), the blade knocked out of
  the fist and spinning up behind him, then on his back - the head, chest and near arm a lossless quarter turn, the
  near wing folded under him, both knees up: the idle's thighs with their red plates turned, the shins drawn, the
  idle's boots from their top row - a row of bounce and still, the blade on the ground behind his head (dead(), DEAD_*,
  LYING_*); the old row shear made a staircase of him and the old quarter turn of the whole idle lay like a plank.
- the run: the idle's legs turned whole about the hips, the lead leg swapping each half cycle, four frames each, the
  near hip turning with its leg (RUN, run()), every turned leg cleaned (clean_leg).
Every rigged frame is finished the same way (finish): hanging outline squares go, enclosed pinholes of the background
take the outline, the outline closes round the mid-dark edges too (complete_outline at design_aatrox.OUTLINE_DARK, and
outside the pasted head, which is never repainted), solid 3 x 3 blocks of outline get a coloured middle (unblob), loose
bits go.
--check compares the strips with assets/source/native/; --out writes them to another folder, --tag picks tags.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_aatrox as D  # noqa: E402
import strips  # noqa: E402  (design_aatrox puts the skill's scripts on the path)
from rig_nocturne import rotsprite  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "native")
CELLS = os.path.join(OUT, "aatrox_cells.json")
TAGS = ["idle", "run", "attack", "attack_p", "skill", "q2", "q3", "skill2", "ult", "hit", "dead"]
# drawn by Codex since 2026-10-04 (League's full-body Q casts, the transformation with League's wings):
# tools/art/import_redo_aatrox.py writes them
CODEX = {"skill", "q2", "q3", "ult"}
# kept as committed and not rebuilt: the run is v11 (55b19749), the one the user approved (「挺不错的」); the audit round's
# run below (lead leg swapping, swings to 49 degrees) read in game as 「看起来极度不协调」 and was taken back
KEEP = {"run"}
Z = 8
PIVOT = (64, 88)
SOLES = 99                           # the soles' row on the canvas (the feet line, pivot + 11)
# canvas row -> (first col, last col) cleared
NEAR_ARM = {77: (53, 58), 78: (53, 58), 79: (54, 58), 80: (54, 58), 81: (56, 58), 82: (57, 59), 83: (57, 60),
            84: (58, 61), 85: (57, 60), 86: (57, 60)}
FAR_ARM = {77: (68, 70), 78: (68, 71), 79: (68, 72), 80: (67, 71), 81: (67, 71), 82: (65, 70), 83: (65, 68),
           84: (65, 67)}
NEAR_HIP = {(84, 59): "o", (84, 60): "0", (84, 61): "e", (85, 58): "o", (85, 59): "0", (85, 60): "e",
            (86, 57): "o", (86, 58): "0", (86, 59): "0", (86, 60): "e"}
WAIST = {(82, 64): "a", (82, 65): "o", (83, 65): "o", (83, 66): "o", (83, 67): "o", (84, 65): "e", (84, 66): "e",
         (84, 67): "o", (85, 65): "0", (85, 66): "e"}   # (fix round 2) the waist's 'ee' joined to the hip under it:
#   alone it was a 2-square speck ringed by outline in W 2-5 (the review); (fix round 3) the waist's line closed across
#   (66-67, 83): the hip's outline square (68, 83) hung there alone, a black tick
NEAR_SHOULDER = (57.0, 77.0)
FAR_SHOULDER = (68.0, 77.0)
REACH = 10.5                         # shoulder to fist, the design's arm (77, 55) -> (84, 60) plus the fist
GRIP = (58, 85)                      # the blade's grip square on the design (the fist is centred on it)
BASE = math.degrees(math.atan2(9, -20.5))   # the drawn blade's direction, grip to tip (screen degrees, y down)
STEEL = ("3", "2", "1")              # the gauntlet arm: lit edge, core, shadow
RED = ("8", "8", "6")                # the red arm as the idle draws it: bright '8' over its crimson '6' shadow
FIST = ["e23", "123", "ee1"]
# the far claw open for W's throw, pointing ahead: a solid 3 x 3 red hand, the middle finger reaching on, no black
# between the fingers (the old 「7o7o」 rows read as a ragged comb)
CLAW = ["88.", "668", "87."]
# the level blade: the drawn blade's squares with each column moved up by 0.4 x its distance from the grip (the drawn
# slope), the top edge's gap filled, two columns repeated in the middle (the drawn blade is 22.4 squares from the grip
# to the tip, a level one 20.5 wide), the lower edge's outline closed with two crimson barbs two squares wide (teeth
# on one edge; a one-square barb leaves its outline square hanging under it like a crumb). The
# guard with the orange eye, the two red prongs of the tip boxed in outline - as drawn.
BLADE_LEVEL = ["......ooooooooooooo.....",
               ".ooooo7767777767777ooo..",
               "oo77o7a8aa8a8a78baaffoa9",
               "..ooo9bbb69699bb9999aobo",
               "oo77ooa6666666666669aoo.",
               "..oooooo66oooo66ooooo...",
               "........oo....oo........"]
LEVEL_GRIP = (23, 2)                 # its grip square (the drawn blade's GRIP)
# Codex's pose plans (codex_strips/animation_source.py), per frame (blade angle, fist x, y) on the canvas, None = the
# design's own hold; the frame audit (2026-10-04): every fist within REACH of the shoulder, angles from ORIENT.
# attack: 2 the back-swing raised to the shoulder (League's frame 2; it was level at the hip), 3 the swing through with
# a bent elbow in front of the waist (a straight pipe across the chest), 4-5 the thrust, the arm nearly straight.
# attack_p: 1 the blade upright beside the near wing, the fist 7 squares from the shoulder (League's frame 1; the fist
# sat against the shoulder in a 7 x 9 steel lump), 2-3 drawn back low, 4-5 the thrust (5 a
# square further, as attack 5: the two frames were one 200 ms hold, fix round 3; phase 1b fix 1, the review: 5 only
# dropped a row - now 4 drives in at the waist and 5 reaches 2 squares further, the arm at its full REACH, the tip 3
# squares further ahead).
POSES = {
    "attack": [None, (180, (50, 78)), (22, (64, 82)), (0, (66, 81)), (0, (66, 82)), None],
    "attack_p": [(-90, (51, 81)), (180, (54, 85)), (158, (55, 85)), (0, (65, 82)), (0, (67, 80)), None],
}
# W: the far claw per frame (the elbow bends out and down from FAR_SHOULDER): drawn back by the shoulder (2-3), then
# thrown forward at the shoulder's height (4-5), behind the head (the claw had covered the jaw)
THROW = [None, (71, 71), (72, 69), (77, 75), (77, 75), None]
# the ult (Codex's since 2026-10-04, kept for reference): wings turned out per frame, the arms
ULT_SPREAD = [None, 0.25, 0.55, 1.0, 1.0, None]
ULT_ARMS = [None, (156, (53, 83), (72, 79), (75, 80)), (156, (49, 81), (73, 78), (78, 77)),
            (156, (49, 81), (73, 78), (78, 77)), (156, (49, 81), (73, 78), (78, 77)), None]
FAR_ROOT = (69, 75)                  # where the drawn wings join the back (behind the shoulders)
NEAR_ROOT = (58, 75)
# the run (8 frames, 2026-10-04): every leg I drew was turned down - the whole-leg shear slid the knee plate off the shin
# as it played (「是膝盖那和下面的小腿 走路的时候感觉脱节的」), legs from close hips read as a skirt under the wide waist
# (「怎么看起来剑魔像穿了裙子？？」), two-bone legs on League's joints were 「不自然」, Codex's redraw lost to them; then
# 「你把待机的腿用到走路啊」, and the idle's legs slid whole on the ground were 「你觉得对吗？ 不自然啊」 (no swing, no
# knee). Now each of the idle's legs, every square as drawn, is TURNED about its hip by RotSprite (RUN: degrees, + = the
# foot ahead - a forward leg lands heel first, a back one leaves on the toe) and lifted RUN rows off the ground while it
# swings; the hips come RUN_HIP_IN in under the waist so the feet cross (the near leg in front of the far one in an X in
# frames 8 and 1; spread at most ~12 squares in 4-5); the body sinks RUN_DROP rows on the contacts.
# 「换腿的时候这里就像是断了的」 (v7): the near leg's shin + boot were mirrored about the knee (toe forward) while its thigh
# leans the other way - a kink at the knee in every frame - its knee row has a black square inside (95, 58), and the
# lifted legs were bent (thigh and shin turned apart: a one-square joint). Now only the near FOOT (rows NEAR_FOOT down)
# is mirrored about the ankle, the knee square is the leg's dark steel (NEAR_KNEE_FILL) and every leg turns whole.
# The frame audit (2026-10-04) on v11 (「挺不错的」, kept as the fallback in the review): the near leg was always the
# back one - its feet never passed the far ones (near minus far foot -14..0 squares), a scissor instead of steps - and
# in 1 and 8 the far leg hid behind the near one. Now the near leg swings ahead of the far one from its reach (8)
# through its contact (1-2) - the shins crossed, near minus far +4..+5 - and the far leg leads from its swing through
# its stance (3-7, -4..-9); the swing leg kicks back up after it leaves the ground (far 2, near 6) and comes through in
# one frame, so no frame has the two feet on one spot (the far leg shows 39+ of its 63 squares in every frame).
# The review of that pass: the near foot led 3 frames and the far one 5, a swing in one frame, the far leg cut by a row of
# outline across its knee or ankle (a 0-square row RotSprite left at -40/-44 degrees), a black tick under the lifted toe.
# Now (fix round 1) every foot runs the same cycle half a cycle apart: planted ahead (contact), drawn back under the
# body (lift 0, 1/3 of the stride a frame), off the toe at the back (lift 1), swung through lifted 3 rows (two frames, the
# lifted foot behind the planted one, then past it - the passing frames, the shins crossed), reaching ahead (lift 1):
# the near foot leads in 7, 8, 1, 2 and the far one in 3-6 (near minus far foot +6.5, +4.5, -5.5, -11, -11, -6, +2.5,
# +6.5), the angles solved for those foot places (tools in the review folder). The two legs' angles differ (near -9..+29,
# far -47..+26) because the far hip sits 3 squares ahead of the near one in the 3/4 view and only comes in 1 square
# (its red plate outside); the near hip goes with its leg (the pelvis turning: in 3 when the near leg is back, in 7 when
# it is ahead) so the far leg drawn back shows behind the near thigh instead of under it. Every turned leg is cleaned
# (clean_leg: a row under two coloured squares bridged with the leg's own colours, a tick under a one-square toe nub
# folded into the outline, the ring closed).
# Fix round 2 (the review): frames 8/1 and 4/5 had the same angles (the stride stalled at each contact, then jumped 4-6
# squares); now every foot slides back evenly through its stance (about 2 squares a frame, 1 across the contact and the
# toe-off), is kicked up behind the planted leg (lift 2) and swung through (lift 3, the passing frame) to its reach
# (lift 1): ankles near 69.5 67.5 65.5 63.5 62.5 61.5 66.5 70.6, far 63 62 67.4 71 70 68 66 64 (near minus far +6.5 +5.6
# -1.9 -7.5 -7.4 -6.5 +0.5 +6.6: the near foot leads in 7, 8, 1, 2, the far one in 3-6). The far leg's thigh and shin
# turn while its boot stays the idle's own, flat, at the turned ankle (FAR_BOOT; RotSprite had shrunk it to a 2-square
# peg whenever it was drawn back), and both red hip plates are laid back on their turned thighs after the body
# (HIP_PLATES: the near thigh and the skirt had hidden the far one in 1-3 and 6-8).
# per frame: [near deg, near lift, far deg, far lift, near hip in(, far hip in: RUN_HIP_IN by default)]
# Fix round 3 (the review): in 7, the near foot's passing frame, it hung straight over the planted far boot (ankles 65.8 /
# 66.3, one thick leg with two boots stacked) - now it is through, 2.4 squares ahead (+34 degrees, its hip in 7: the
# shins crossed), reaching to 69.8 in 8 (+44); kicked up behind to 62.0 in 6 (+12); the far leg drawn back a little less
# in 1-2 (-37, -44: its boot tipped toe-down, FAR_BOOT_TIP) - near minus far +4.8 +4.0 -2.4 -7.3 -7.3 -6.0 +2.4 +5.5.
# Phase 1b fix 1 (the review: 7 still one leg with a spur - the lifted near leg a stub over the planted far boot; 8, 1, 2
# the far boot under the near shin, a C of outline, the far thigh a 1-square sliver beside the near one): the hips of
# the crossed legs stand apart - the near one a square further in (8), the far one 2 squares further in (3) - so each
# boot stays under its own shin with background between them from the knee down, the far thigh 2 squares wide; 7 is a
# passing frame like League's run 3 / 7: the near thigh swung ahead (+50, its hip 10 in) and its shin hanging straight
# down from the knee (RUN_BEND -50), the foot under the knee 2 rows up, the far leg planted a little further back (-19,
# its hip 4 in; its boot flat: from -20 back it tips and hooked forward into a C), background between the legs.
RUN = [[33, 0, -37, 1, 8, 3], [21, 0, -44, 2, 8, 3], [21, 0, -4, 3, 5], [15, 0, 22, 1, 4],
       [15, 1, 14, 0, 3], [12, 2, 0, 0, 3], [50, 2, -19, 0, 10, 4], [44, 1, -32, 0, 8, 3]]
# per frame (near, far): the shin's further turn about the knee (degrees; the thigh and the shin turned as two pieces
# that share the knee row)
RUN_BEND = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (-50, 0), (0, 0)]
# the far boot: from this row down laid on the turned ankle as drawn (the ankle: the shin's last row, this point)
FAR_BOOT = (96, (69.0, 95.0))
# (fix round 3, the review: the far leg drawn back with its boot flat, toe ahead, under the slanted shin read as a 'C' -
# a backward knee - in 8, 1, 2) from this angle back the boot is tipped toe-down about the ankle by this share of the
# leg's turn (RotSprite; the toe leaving the ground)
FAR_BOOT_TIP = (-20, 0.6)
DEAD_FAR_BOOT = (45,)                # (fix round 3) from this fall on the far boot turns on its own (dead 4: specks)
# the idle's red hip plates (canvas squares): laid back square for square where the thigh's turn takes them
HIP_PLATES = {"far": [(70, 88), (71, 88), (69, 89), (70, 89), (71, 89), (68, 90), (69, 90), (70, 90)],
              "near": [(59, 89), (60, 89), (58, 90), (59, 90), (60, 90)]}
RUN_DROP = [1, 1, 0, 0, 1, 1, 0, 0]  # rows the upper body sinks: on both contacts (it sank on the far one only)
# squares the far hip comes in under the waist: it carries the bright red hip plate on its outer side, which rode
# 3 squares into the middle of the body (「待机的腿上的红色部位是在外面的 然后走路时就到里面了」); held still where the idle
# has it, it floated off the moving thigh (「红色的也要贴着自然的动啊」) - so the far hip comes in 1 (the plate rides its leg,
# outside). The near hip: RUN's last column.
RUN_HIP_IN = {"far": 1}
# the idle's own thigh tops (row LEG_TOP, these columns) stay under the waist behind the moving legs: the near leg
# coming in left a notch there (the waist hung 5 squares over the near thigh)
HIP_BAND = (58, 63)
LEG_TOP = 88                         # the legs below this row move; the hips and the skirt above stay
NEAR_FOOT = (97, 57.0)               # the near foot: from this row down, mirrored about this column (under the knee:
#                                      「往膝盖那移一点都解决了」 - 57.5 left it a square out from the shin)
NEAR_KNEE_FILL = {(95, 58): "e"}     # the near knee's black square inside the leg (design_aatrox MENDS has it now too)
# the idle's legs (canvas squares): their columns and hips
NEAR_LEG = {"cols": (52, 64), "hip": (59.0, 88.0)}
FAR_LEG = {"cols": (64, 76), "hip": (69.0, 88.0)}
# the idle's breath (6 frames; it was import_native's BOB on slots 3-5, a seam across the boots' middle row 97 that
# squashed both boots and blinked their lights, the frame audit): frames 3-5 a row lower, but for each leg from the
# second of its two equal shin rows down (the near leg's rows 94/95, the far one's 93/94: (first row kept, columns))
BREATH = [0, 0, 1, 1, 1, 0]
BREATH_KEEP = {"near": (95, (52, 63)), "far": (94, (64, 76))}
# the hit (2 frames): degrees the upper body turns back about the standing point - jolted, then half way back
HIT = [6, (-1, 0)]
# (fix round 3, the review: RotSprite at 3 degrees doubled the outlines round the armpit and thinned the red far arm)
# the half-way-back frame is the upper body moved whole one square back (a tuple: a rigid move (dx, dy))
# its near wing's hook (the near wing from this row up) moved whole, not turned: RotSprite at 6 / 3 degrees uncurled it
# into a 1-square strand with its crimson cap beside it (fix round 2, the review)
HIT_TIP = 66
# the death (8 frames): per frame (degrees turned back about the near heel, quarter turns of the head) - None: lying
DEAD_HEEL = (54, 99)                 # the near boot's heel on the soles' row
DEAD_TILT = [None, (15, 0), (30, 0), (60, 1), (None, 1), (None, 1), (None, 1), (None, 1)]
DEAD_WING = [0, 12, 12, 0, 0, 0, 0, 0]   # degrees the near wing turns further (falling)
DEAD_SETTLE = [0, 0, 0, 0, 1, 0, 0, 0]   # rows the lying body still rides over the ground
# the blade per frame: (direction, grip square) - knocked out of the fist, spinning up and back, on the ground behind
# the head (level), clear of the boots. (phase 1b fix 1, the review: it flew 9-17 squares off him, in 4 against the cell's
# edge) it tumbles close behind him - 3 squares over the wing in 2, 2 behind the shoulders in 3, 5 beside the head in 4,
# falling tip first - each grip the nearest to its place with that gap
DEAD_BLADE = [None, (-66, (39, 60)), (-156, (45, 59)), (114, (19, 61)), (180, (24, 86)), (180, (24, 86)),
              (180, (24, 86)), (180, (24, 86))]
# the lying pose: the near wing's offset under the shoulders, the hips' height over the soles, the knee from the hip,
# the ankle from the knee, the far leg's hip from the near one's
LYING_WING = (-4, -3)
LYING_HEAD_X = 34                    # the lying head's middle column: where the fall (frame 4) lays it
LYING_HIP = 4
LYING_TIP = 3                        # the lying wing's claw: its one-square strand folded in this many rows up
# (phase 1b fix 1, the review) frame -> (first row, last column, squares): the falling near wing's hook in 4 hung under
# him as a one-square strand ('9e' / 'e' / '2') with a steel tip - shortened to the wing; lying (5-8), the folded wing's
# claw ended in a crimson '55' strand under its steel knuckle (x25, rows 91-92) - folded in
DEAD_TRIM = {3: (91, 40, 6), 4: (90, 27, 2), 5: (90, 27, 2), 6: (90, 27, 2), 7: (90, 27, 2)}
LYING_LEGS = ((4, -5), (3, 6), (2, -2))
LEG_STEEL = ("2", "e", "0")          # the idle's leg steel: lit, core, the darkest shade
BOOT_TOP = 97                        # the boots' first row on the design
NEAR_BOOT = (96, (57.5, 95.0))       # the near boot (the death): from this row down, laid flat under the turned ankle
#                                      (the middle of the shin's last row; on the design (57.5, 95))
HALO = 3                             # the squares round the laid head kept clear of parts that were not there


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) or os.name != "nt" else pre + p


def rgba(k):
    return np.array(list(D.COL[k]) + [255], np.uint8)


def design():
    return D.load(D.OUT)[4::8, 4::8].copy()


def sword_mask(des):
    g = D.letters(des)
    part = D.blade(D.load(D.FIRST))
    keys = list(part)
    r0, c0 = min(r for r, _ in keys), min(c for _, c in keys)
    for dy in range(-r0, 128 - r0):
        for dx in range(-c0, 128 - c0):
            if all(0 <= r + dy < 128 and 0 <= c + dx < 128 and g[r + dy][c + dx] == part[(r, c)] for r, c in keys):
                m = np.zeros((128, 128), bool)
                for r, c in keys:
                    m[r + dy, c + dx] = True
                return m
    raise SystemExit("blade not found")


def ink(a):
    return (a[..., 3] > 0) & (a[..., :3] == D.COL["o"]).all(-1)


def grow(m, n=1):
    """The mask grown by n squares (8-neighbours)."""
    out = m.copy()
    for _ in range(n):
        p = np.pad(out, 1)
        out = np.zeros_like(m)
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                out |= p[dy:dy + m.shape[0], dx:dx + m.shape[1]]
    return out


def loose_outline(a, zone=None):
    """Outline squares with no coloured square round them go - inside `zone` only (the squares a cut took and their
    neighbours: the blade's ring left on the body); the design's own outline elsewhere stays as drawn."""
    k = ink(a)
    col = (a[..., 3] > 0) & ~k
    loose = k & ~grow(col)
    if zone is not None:
        loose &= zone
    a[loose] = 0
    return a


def body(des, sm, near_arm=True, far_arm=False):
    """The design without what the frame poses anew: the blade and the near arm (near_arm), the far red arm
    (far_arm). The design's outline squares on the cut's edge that still outline a square left stay."""
    a = des.copy()
    cut = np.zeros(des.shape[:2], bool)
    if near_arm:
        cut |= sm
        for r, (c0, c1) in NEAR_ARM.items():
            cut[r, c0:c1 + 1] = True
    if far_arm:
        for r, (c0, c1) in FAR_ARM.items():
            cut[r, c0:c1 + 1] = True
    cut &= des[..., 3] > 0
    a[cut] = 0
    if near_arm:
        for (r, c), k in NEAR_HIP.items():
            a[r, c] = rgba(k)
    if far_arm:
        for (r, c), k in WAIST.items():
            a[r, c] = rgba(k)
    col = (a[..., 3] > 0) & ~ink(a)
    back = cut & ink(des) & grow(col) & (a[..., 3] == 0)
    a[back] = des[back]
    return loose_outline(a, grow(cut))


def sword_sprite(des, sm):
    s = np.zeros_like(des)
    s[sm] = des[sm]
    return s


def over(dst, src, dx=0, dy=0):
    """src laid over dst, moved (dx, dy)."""
    h, w = src.shape[:2]
    H, W = dst.shape[:2]
    y0, x0 = max(0, dy), max(0, dx)
    y1, x1 = min(H, dy + h), min(W, dx + w)
    if y1 <= y0 or x1 <= x0:
        return dst
    s = src[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    m = s[..., 3] > 0
    dst[y0:y1, x0:x1][m] = s[m]
    return dst


def turned(sprite, joint, deg, to):
    """sprite turned deg (counter-clockwise on screen) about joint, the joint put on `to` of a 128 canvas."""
    r, (jx, jy) = rotsprite(sprite, joint, deg)
    out = np.zeros((128, 128, 4), np.uint8)
    return over(out, r, int(round(to[0] - jx)), int(round(to[1] - jy)))


def letters_sprite(rows):
    a = np.zeros((len(rows), len(rows[0]), 4), np.uint8)
    for r, row in enumerate(rows):
        for c, k in enumerate(row):
            if k != ".":
                a[r, c] = rgba(k)
    return a


ORIENT = None


def orientations(des, sm):
    """The blade's exact directions: the drawn blade and the level one, mirrored and transposed (lossless). A list of
    (angle, sprite, grip square in it)."""
    global ORIENT
    if ORIENT is None:
        s = sword_sprite(des, sm)
        ys, xs = np.nonzero(s[..., 3])
        drawn = (s[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (GRIP[0] - xs.min(), GRIP[1] - ys.min()), BASE)
        level = (letters_sprite(BLADE_LEVEL), LEVEL_GRIP, 180.0)
        ORIENT = []
        for spr, (jx, jy), ang in (drawn, level):
            for t in (False, True):
                for fx in (False, True):
                    for fy in (False, True):
                        a, x, y = spr, jx, jy
                        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                        if t:
                            a, x, y, dx, dy = a.transpose(1, 0, 2), y, x, dy, dx
                        if fx:
                            a, x, dx = a[:, ::-1], a.shape[1] - 1 - x, -dx
                        if fy:
                            a, y, dy = a[::-1], a.shape[0] - 1 - y, -dy
                        ORIENT.append((math.degrees(math.atan2(dy, dx)), np.ascontiguousarray(a), (x, y)))
    return ORIENT


def blade(des, sm, fist, angle):
    """The design's blade pointing `angle` (screen degrees, y down: 0 = ahead, 90 = down) with its grip square on the
    fist: the exact direction nearest to it (ORIENT)."""
    def off(a):
        return abs((a - angle + 180) % 360 - 180)
    ang, spr, (jx, jy) = min(orientations(des, sm), key=lambda o: off(o[0]))
    if off(ang) > 3:
        raise ValueError(f"no exact blade direction near {angle} (nearest {ang:.1f})")
    out = np.zeros((128, 128, 4), np.uint8)
    return over(out, spr, int(math.floor(fist[0] - jx + 0.5)), int(math.floor(fist[1] - jy + 0.5)))


def reach(shoulder, fist):
    sx, sy = shoulder
    fx, fy = fist
    d = math.hypot(fx - sx, fy - sy)
    if d <= REACH:
        return fist
    raise ValueError(f"fist {fist} out of reach of {shoulder} ({d:.1f} > {REACH})")


def elbow(shoulder, fist, out=1.0):
    """The elbow of a two-bone arm (two halves of REACH), bent away from the body (down and out)."""
    sx, sy = shoulder
    fx, fy = fist
    d = max(1e-6, math.hypot(fx - sx, fy - sy))
    half = REACH / 2
    h = math.sqrt(max(0.0, half * half - (d / 2) ** 2))
    mx, my = (sx + fx) / 2, (sy + fy) / 2
    nx, ny = -(fy - sy) / d, (fx - sx) / d          # a normal; the elbow takes the one pointing down / outward
    if ny < 0 or (abs(ny) < 1e-6 and nx * out < 0):
        nx, ny = -nx, -ny
    return (mx + nx * h, my + ny * h)


def limb(a, points, mats, keep=None, joint=None, core_r=1.6):
    """A three-square limb along the polyline: lit edge on the side toward the top-left, core, shadow; one outline ring,
    drawn over what is under it (the arm is in front) but not over `keep` (the head) nor round `joint` (where it grows
    out of the shoulder). core_r: the core's half width (1.6: three squares across, four on a slant; 1.25: three
    across, two on a slant - the idle's red arm)."""
    H, W = a.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    px, py = xs + 0.5, ys + 0.5
    best = np.full((H, W), 1e9)
    side = np.zeros((H, W))
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        x0, y0, x1, y1 = x0 + 0.5, y0 + 0.5, x1 + 0.5, y1 + 0.5
        vx, vy = x1 - x0, y1 - y0
        L2 = max(1e-6, vx * vx + vy * vy)
        t = np.clip(((px - x0) * vx + (py - y0) * vy) / L2, 0, 1)
        dx, dy = px - (x0 + t * vx), py - (y0 + t * vy)
        dist = np.hypot(dx, dy)
        nx, ny = -vy / math.sqrt(L2), vx / math.sqrt(L2)
        if nx + ny > 0:                                 # the normal toward the top-left (light)
            nx, ny = -nx, -ny
        s = dx * nx + dy * ny
        closer = dist < best
        best = np.where(closer, dist, best)
        side = np.where(closer, s, side)
    core = best <= core_r
    ring = (best <= core_r + 1.0) & ~core
    if keep is not None:
        ring &= ~keep
    if joint is not None:
        ring &= np.hypot(px - joint[0] - 0.5, py - joint[1] - 0.5) > 2.6
    a[ring] = rgba("o")
    lit, mid, dark = mats
    a[core & (side > 0.55)] = rgba(lit)
    a[core & (np.abs(side) <= 0.55)] = rgba(mid)
    a[core & (side < -0.55)] = rgba(dark)
    return a


def stamp(a, rows, at, ring=True):
    """Letter rows centred on `at` (x, y), with an outline ring where clear."""
    h, w = len(rows), len(rows[0])
    x0, y0 = int(math.floor(at[0] - w // 2 + 0.5)), int(math.floor(at[1] - h // 2 + 0.5))
    if ring:
        for r in range(-1, h + 1):
            for c in range(-1, w + 1):
                y, x = y0 + r, x0 + c
                if 0 <= y < 128 and 0 <= x < 128 and a[y, x, 3] == 0:
                    a[y, x] = rgba("o")
    for r, row in enumerate(rows):
        for c, k in enumerate(row):
            if k != ".":
                a[y0 + r, x0 + c] = rgba(k)
    return a


def plated_arm(a, points, keep=None, joint=None, plate=2.5, r_plate=1.55, r_arm=1.05):
    """The idle's gauntlet arm re-posed along shoulder -> elbow -> fist: three squares across for `plate` squares from
    the shoulder (the plate under the pauldron), then two (the idle's upper arm and forearm, rows 79-82: '33', '11',
    '13', '32'; the review: the old three-to-four-square tube with one lit stripe read paler and heavier, a lump at the
    elbow), lit '3' on the top-left side, '2' between, '1' in shadow, the elbow a dark '1' plate break, an 'e' under
    the shoulder plate; one outline ring, not over `keep` (the head) nor round `joint` (the shoulder)."""
    H, W = a.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    px, py = xs + 0.5, ys + 0.5
    best = np.full((H, W), 1e9)
    side = np.zeros((H, W))
    s_at = np.zeros((H, W))
    s0, joints = 0.0, []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        x0, y0, x1, y1 = x0 + 0.5, y0 + 0.5, x1 + 0.5, y1 + 0.5
        vx, vy = x1 - x0, y1 - y0
        L = max(1e-6, math.hypot(vx, vy))
        t = np.clip(((px - x0) * vx + (py - y0) * vy) / (L * L), 0, 1)
        dx, dy = px - (x0 + t * vx), py - (y0 + t * vy)
        dist = np.hypot(dx, dy)
        nx, ny = -vy / L, vx / L
        if nx + ny > 0:
            nx, ny = -nx, -ny
        sd = dx * nx + dy * ny
        closer = dist < best
        best = np.where(closer, dist, best)
        side = np.where(closer, sd, side)
        s_at = np.where(closer, s0 + t * L, s_at)
        s0 += L
        joints.append(s0)
    core = best <= np.where(s_at < plate, r_plate, r_arm)
    ring = (best <= np.where(s_at < plate, r_plate, r_arm) + 1.0) & ~core
    if keep is not None:
        ring &= ~keep
    if joint is not None:
        ring &= np.hypot(px - joint[0] - 0.5, py - joint[1] - 0.5) > 2.6
    a[ring] = rgba("o")
    a[core & (side > 0.3)] = rgba("3")
    a[core & (np.abs(side) <= 0.3)] = rgba("2")
    a[core & (side < -0.3)] = rgba("1")
    a[core & (np.abs(s_at - joints[0]) <= 0.7)] = rgba("1")
    a[core & (np.abs(s_at - plate) <= 0.5) & (side < 0)] = rgba("e")
    return a


def near_arm(a, fist, keep=None):
    fist = reach(NEAR_SHOULDER, fist)
    el = elbow(NEAR_SHOULDER, fist, out=-1)
    plated_arm(a, [NEAR_SHOULDER, el, fist], keep, NEAR_SHOULDER)
    return stamp(a, FIST, fist)


def far_arm(a, fist, claw=False, keep=None):
    fist = reach(FAR_SHOULDER, fist)
    el = elbow(FAR_SHOULDER, fist, out=1)
    # (fix round 3, the review: two squares thick, its top on the far wing's purple with no outline between - a flat
    # bright band) three squares across like the idle's red arm ('888' / '8886'), ringed where it crosses the wing
    limb(a, [FAR_SHOULDER, el, fist], RED, keep, FAR_SHOULDER, core_r=1.6)
    if claw:
        return stamp(a, CLAW, (fist[0] + 1, fist[1]))
    return stamp(a, ["66", "56"], fist)


HEAD = None


def head_mask(des):
    """The head's squares on the design (design_aatrox step 6: the first design's head mirrored)."""
    global HEAD
    if HEAD is None:
        HEAD = np.zeros((128, 128), bool)
        for r, c in D.head_squares(des, D.load(D.FIRST), mirrored=True):
            HEAD[r, c] = True
    return HEAD


def paste_head(a, des, dx=0, dy=0):
    """The approved head laid over the frame square for square (its own squares only, by shape), moved (dx, dy)."""
    hm = head_mask(des)
    ys, xs = np.nonzero(hm)
    a[ys + dy, xs + dx] = des[ys, xs]
    keep = np.zeros(hm.shape, bool)
    keep[ys + dy, xs + dx] = True
    return a, keep


def holes(a, most=6):
    """Enclosed pockets of background (4-connected, `most` squares or fewer): a list of square lists."""
    bg = a[..., 3] == 0
    H, W = bg.shape
    seen = np.zeros_like(bg)
    out = []
    for y0 in range(H):
        for x0 in range(W):
            if not bg[y0, x0] or seen[y0, x0]:
                continue
            stack, part, edge = [(y0, x0)], [], False
            seen[y0, x0] = True
            while stack:
                y, x = stack.pop()
                part.append((y, x))
                edge |= y in (0, H - 1) or x in (0, W - 1)
                for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= yy < H and 0 <= xx < W and bg[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
            if not edge and len(part) <= most:
                out.append(part)
    return out


DESIGN_INK = None


def finish(a, des, keep, shift=None):
    """A rigged frame finished: outline squares with at most one opaque neighbour, or on the silhouette's edge with no
    coloured neighbour where the design has none (a black tick sticking out), go (loose_ink); enclosed background
    pockets of 1-6 squares take the outline (between an arm and the torso; the head's own pinhole, walled by the head
    alone, stays); the outline closes round every edge square from design_aatrox.OUTLINE_DARK up, and outside the
    pasted head (`keep`, never repainted) - repeated until nothing changes; bits of two squares or fewer go."""
    global DESIGN_INK
    if DESIGN_INK is None:
        d = ink(des)
        DESIGN_INK = d & ~grow((des[..., 3] > 0) & ~d)       # the design's own black-only squares (horn crest...)
    di = DESIGN_INK.copy()
    if shift is not None:                                         # the run: every outline square of the upper body,
        di = ink(des)                                             # pasted whole, moved with it (the review: the wing
        di[LEG_TOP:] = False                                      # tips, the blade's prongs and the far hip's spike
        di = np.roll(di, shift, 0)                                # blinked with the drop)
    exempt = keep | di
    for _ in range(6):
        lonely = loose_ink(a, exempt)
        filled = 0
        for part in holes(a):
            inside = set(part)
            if all((yy, xx) in inside or keep[yy, xx]                    # the head's own pinhole: walled by the head
                   for y, x in part for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1))):
                continue
            for y, x in part:
                a[y, x] = rgba("o")
            filled += 1
        a, n, d = strips.complete_outline(a, color=D.COL["o"], dark=D.OUTLINE_DARK, feet=SOLES, keep=keep)
        light = keep & (strips.lum(a[..., :3]) >= D.OUTLINE_DARK)    # the pasted head's own edge: outlined outside it
        q = np.pad(light, 1)
        ring = (a[..., 3] == 0) & (q[:-2, 1:-1] | q[2:, 1:-1] | q[1:-1, :-2] | q[1:-1, 2:])
        a[ring] = rgba("o")
        if not (lonely.any() or filled or n or d or ring.any()):
            break
    return crumbs(specks(unblob(a, keep), des, keep))     # unblob paints lone squares too: specks after it


def islands(a, most=2):
    """Coloured squares cut off from every other coloured square (4-neighbours) by the outline: lists of `most` or
    fewer (y, x)."""
    c = colm(a)
    seen = np.zeros_like(c)
    out = []
    for y0, x0 in zip(*np.nonzero(c)):
        if seen[y0, x0]:
            continue
        stack, part = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            part.append((y, x))
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < 128 and 0 <= xx < 128 and c[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if len(part) <= most:
            out.append(part)
    return out


DESIGN_PAIRS = None


def specks(a, des, keep):
    """New specks of colour (fix round 2, the review: a bright red square at the far claw in attack 3, a steel one
    beside the forearm in attack_p 1, a dotted chain along a wing's edge in dead 3, dark specks at the lying hips): a
    coloured square, or two, walled off by the outline that the design does not have - every island of the design is
    two squares (the blade's prongs '77', the wing hook's '55', the boot heel's '02', the claw's '0e' / '00'), so a lone
    square, or a pair of other colours, takes the outline colour. The pasted head (`keep`) is left as it is."""
    global DESIGN_PAIRS
    if DESIGN_PAIRS is None:
        g = D.letters(des)
        DESIGN_PAIRS = {"".join(sorted(g[y][x] for y, x in p)) for p in islands(des) if len(p) == 2}
        assert not [p for p in islands(des) if len(p) == 1], "the design has a lone square"
    g = D.letters(a)
    lum = strips.lum(a[..., :3])
    for part in islands(a):
        if any(keep[y, x] for y, x in part):
            continue
        if len(part) == 2 and "".join(sorted(g[y][x] for y, x in part)) in DESIGN_PAIRS:
            continue
        # joined to the coloured square nearest in shade across one outline square (inside the figure): a 3 x 3 of
        # outline in its place read as a black hole (and unblob would paint it back)
        c = colm(a)
        best = None
        for y, x in part:
            for dy, dx in N4:
                ny, nx = y + dy, x + dx
                my, mx = ny + dy, nx + dx
                if not (0 < ny < 127 and 0 < nx < 127 and 0 <= my < 128 and 0 <= mx < 128):
                    continue
                if not ink(a[ny:ny + 1, nx:nx + 1])[0, 0] or keep[ny, nx] or not c[my, mx] or (my, mx) in part:
                    continue
                if any(a[ny + ey, nx + ex, 3] == 0 for ey, ex in N4):
                    continue
                d = abs(float(lum[y, x]) - float(lum[my, mx]))
                if best is None or d < best[0]:
                    best = (d, ny, nx, y, x)
        if best is None:
            for y, x in part:
                a[y, x] = rgba("o")
            continue
        _, ny, nx, y, x = best
        a[ny, nx] = a[y, x]
    return a


def fill_blocks(a, des, keep):
    """Outline 2 x 3 (or 3 x 2) solid where the design has colour (fix round 2, the review: under the thrusting forearm,
    where the idle's near arm hung, a 2 x 5 run of bare outline read as a black hole in the waist at 3x; unblob only
    catches 3 x 3): one square at a time - the one with the most coloured neighbours, inside the figure - takes the
    design's own colour there (the waist the arm had covered), until no such block is left."""
    dc = colm(des)
    for _ in range(40):
        k = ink(a)
        bg = a[..., 3] == 0
        best = None
        for h, w in ((2, 3), (3, 2)):
            for y in range(128 - h + 1):
                for x in range(128 - w + 1):
                    if not k[y:y + h, x:x + w].all():
                        continue
                    for yy in range(y, y + h):
                        for xx in range(x, x + w):
                            if keep[yy, xx] or not dc[yy, xx] or bg[yy - 1:yy + 2, xx - 1:xx + 2].any():
                                continue
                            n = int(colm(a)[yy - 1:yy + 2, xx - 1:xx + 2].sum())
                            if best is None or n > best[0]:
                                best = (n, yy, xx)
        if best is None:
            break
        _, y, x = best
        a[y, x] = des[y, x]
    return a


def unblob(a, keep):
    """Solid 3 x 3 blocks of outline inside the figure (filled pockets, doubled outlines: the review found them in
    attack 3, attack_p 1, the run and the death; the design has none): the middle square of each takes the commonest
    colour round it (5 x 5), so the black stays a line."""
    for _ in range(8):
        k = ink(a)
        found = False
        for y in range(1, 127):
            for x in range(1, 127):
                if keep[y, x] or not k[y - 1:y + 2, x - 1:x + 2].all():
                    continue
                win = a[max(0, y - 2):y + 3, max(0, x - 2):x + 3].reshape(-1, 4)
                cols = [tuple(int(v) for v in c) for c in win if c[3] and tuple(int(v) for v in c[:3]) != D.COL["o"]]
                if not cols:
                    continue
                a[y, x] = max(set(cols), key=cols.count)
                k[y, x] = False
                found = True
        if not found:
            break
    return a


def loose_ink(a, exempt=None):
    """Outline squares with at most one opaque neighbour, or on the silhouette's edge with no coloured neighbour (a
    black tick sticking out), cleared - `exempt` ones kept; the mask of what went."""
    gone = np.zeros(a.shape[:2], bool)
    for _ in range(4):
        op = a[..., 3] > 0
        k = ink(a)
        col = op & ~k
        p = np.pad(op, 1).astype(int)
        n = sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx]
                for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
        q = np.pad(~op, 1)
        open_side = q[:-2, 1:-1] | q[2:, 1:-1] | q[1:-1, :-2] | q[1:-1, 2:]
        lone = k & ((n <= 1) | (~grow(col) & open_side))
        if exempt is not None:
            lone &= ~exempt
        if not lone.any():
            break
        a[lone] = 0
        gone |= lone
    return gone


def crumbs(a, most=2):
    """Loose bits of `most` squares or fewer (8-connected) go."""
    op = a[..., 3] > 0
    seen = np.zeros_like(op)
    H, W = op.shape
    for y0, x0 in zip(*np.nonzero(op)):
        if seen[y0, x0]:
            continue
        stack, part = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            part.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and op[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
        if len(part) <= most:
            for y, x in part:
                a[y, x] = 0
    return a


def idle(i, des):
    """The design; in the breath (BREATH) a row lower but for the shins' lowest rows and the boots (BREATH_KEEP): each
    leg loses one of its two equal shin rows, so every square of the legs, the boots and the blade stays as drawn."""
    if not BREATH[i]:
        return des.copy()
    b = np.zeros_like(des)
    b[1:] = des[:-1]
    for r0, (c0, c1) in BREATH_KEEP.values():
        assert (des[r0 - 1, c0:c1 + 1] == des[r0, c0:c1 + 1]).all(), "the breath needs two equal shin rows"
        b[r0:, c0:c1 + 1] = des[r0:, c0:c1 + 1]
    return b


def frame(tag, i, des, sm):
    """One frame on the 128 canvas, the standing point at PIVOT."""
    if tag == "idle":
        return idle(i, des)
    if tag == "dead":
        return dead(i, des, sm)
    if tag == "run":
        return run(i, des, sm)
    if tag == "hit":
        return hit(i, des, sm)
    keep = head_mask(des)
    if tag in POSES:
        pose = POSES[tag][i]
        if pose is None:
            return des.copy()
        angle, fist = pose
        a = body(des, sm)
        a = over(a, blade(des, sm, fist, angle))
        a = near_arm(a, fist, keep)
        return fill_blocks(finish(a, des, keep), des, keep)
    if tag == "skill2":
        claw = THROW[i]
        if claw is None:
            return des.copy()
        a = body(des, sm, near_arm=False, far_arm=True)    # the near arm and the blade stay as the idle holds them
        a = far_arm(a, claw, claw=True, keep=keep)
        a, keep = paste_head(a, des)                        # the claw passes behind the head
        return finish(a, des, keep)
    if tag == "ult":
        spread = ULT_SPREAD[i]
        if spread is None:
            return des.copy()
        _, near, far = wings(des, 0)
        b = body(des, sm, far_arm=True)
        b[(near[..., 3] > 0) | (far[..., 3] > 0)] = 0
        b = loose_outline(b)
        out = np.zeros_like(des)
        r, (jx, jy) = spread_wing(spread)
        over(out, r, int(FAR_ROOT[0] - jx), int(FAR_ROOT[1] - jy))
        l = r[:, ::-1]
        over(out, l, int(NEAR_ROOT[0] - (l.shape[1] - 1 - jx)), int(NEAR_ROOT[1] - jy))
        out = over(out, b)
        angle, fist, _, claw = ULT_ARMS[i]
        out = over(out, blade(des, sm, fist, angle))
        out = near_arm(out, fist, keep)
        return far_arm(out, claw, claw=True, keep=keep)
    raise ValueError(tag)


def wings(des, deg):
    """The design's wings turned out about the shoulders, a second copy turned further for the spread membrane."""
    near = np.zeros_like(des)
    far = np.zeros_like(des)
    hm = head_mask(des)
    for r in range(56, 84):
        for c in range(0, 128):
            if not des[r, c, 3] or hm[r, c]:
                continue
            if c <= (58 if r <= 72 else 55 if r <= 76 else 52):
                near[r, c] = des[r, c]
            elif c >= (70 if r <= 76 else 72):
                far[r, c] = des[r, c]
    out = np.zeros_like(des)
    for part, joint, sign in ((near, (57, 73), 1), (far, (70, 73), -1)):
        for k, extra in ((1, 1.6), (0, 1.0)):            # the far copy first, behind
            over(out, turned(part, joint, sign * deg * extra, joint))
    return out, near, far


def seg_dist(px, py, a, b):
    (x0, y0), (x1, y1) = a, b
    vx, vy = x1 - x0, y1 - y0
    L2 = max(1e-9, vx * vx + vy * vy)
    t = np.clip(((px - x0) * vx + (py - y0) * vy) / L2, 0, 1)
    return np.hypot(px - (x0 + t * vx), py - (y0 + t * vy))


def spread_wing(spread=1.0, size=1.0, bowk=0.22):
    """The right (far) wing, root at the returned joint; x right, y down. spread 0 = folded up, 1 = open."""
    S = size
    W = (8 * S, -13 * S)                                     # the wrist
    tips = [(17 * S, -20 * S), (20 * S, -9 * S), (13 * S, 0 * S)]
    folded = [(10 * S, -22 * S), (11 * S, -16 * S), (10 * S, -9 * S)]
    tips = [(f[0] + (t[0] - f[0]) * spread, f[1] + (t[1] - f[1]) * spread) for t, f in zip(tips, folded)]

    def bow(a, b, k=bowk):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        return (mx + (W[0] - mx) * k, my + (W[1] - my) * k)
    root = (0.0, 0.0)
    trail = [tips[0], bow(tips[0], tips[1]), tips[1], bow(tips[1], tips[2]), tips[2], bow(tips[2], root, 0.15)]
    poly = [root, W] + trail
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    x0, y0 = int(math.floor(min(xs))) - 3, int(math.floor(min(ys))) - 3
    w, h = int(math.ceil(max(xs))) - x0 + 4, int(math.ceil(max(ys))) - y0 + 4
    im = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(im).polygon([((x - x0) * 4, (y - y0) * 4) for x, y in poly], fill=255)
    mem = np.asarray(im.resize((w, h), Image.BOX)) >= 128
    yy, xx = np.mgrid[0:h, 0:w]
    px, py = xx + x0 + 0.5, yy + y0 + 0.5
    arm = seg_dist(px, py, root, W) <= 0.7
    fingers = np.zeros_like(arm)
    for t in tips:
        fingers |= seg_dist(px, py, W, t) <= 0.5
    folds = np.zeros_like(arm)                                # dark folds from the wrist to each scallop
    for a_, b_ in ((tips[0], tips[1]), (tips[1], tips[2])):
        folds |= seg_dist(px, py, W, bow(a_, b_, 0.0)) <= 0.45
    edge = np.zeros_like(mem)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        edge |= mem & ~np.roll(np.roll(mem, dy, 0), dx, 1)
    lead = np.minimum(seg_dist(px, py, root, W), seg_dist(px, py, W, tips[0])) <= 1.2
    a = np.zeros((h, w, 4), np.uint8)
    a[mem] = rgba("a")
    a[mem & folds] = rgba("9")
    a[edge & mem] = rgba("6")                                 # the crimson trailing rim
    a[edge & mem & lead] = rgba("8")                          # the lit leading edge
    a[fingers & mem] = rgba("0")
    a[arm] = rgba("0")
    a[arm & lead & edge] = rgba("2")
    for t in tips:
        ty, tx = int(round(t[1] - y0 - 0.5)), int(round(t[0] - x0 - 0.5))
        if 0 <= ty < h and 0 <= tx < w and a[ty, tx, 3]:
            a[ty, tx] = rgba("7")
    wy, wx = int(round(W[1] - y0 - 0.5)), int(round(W[0] - x0 - 0.5))
    for dy, dx, k in ((-1, -1, "2"), (-2, -1, "3"), (-3, 0, "3")):
        if 0 <= wy + dy < h and 0 <= wx + dx < w:
            a[wy + dy, wx + dx] = rgba(k)
    op = a[..., 3] > 0
    ring = np.zeros_like(op)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ring |= np.roll(np.roll(op, dy, 0), dx, 1)
    a[ring & ~op] = rgba("o")
    return a, (-x0, -y0)


def turn(sprite, joint, deg):
    """RotSprite about joint (+ = counter-clockwise on screen: a hanging part swings ahead): (sprite, joint in it)."""
    if abs(deg) < 0.5:
        return sprite, joint
    r, (jx, jy) = rotsprite(sprite, joint, deg)
    return r, (jx + (joint[0] - round(joint[0])), jy + (joint[1] - round(joint[1])))


def leg_piece(des, sm, L, near=False):
    """One of the idle's legs below LEG_TOP (its red hip plate on it), the blade's squares left out; the near one with its
    knee square filled and its foot mirrored about the ankle (the toe forward, the leg above it as drawn)."""
    c0, c1 = L["cols"]
    leg = np.zeros_like(des)
    leg[LEG_TOP:, c0:c1] = des[LEG_TOP:, c0:c1]
    leg[sm] = 0
    if near:
        for (r, c), k in NEAR_KNEE_FILL.items():
            leg[r, c] = rgba(k)
        row, ax = NEAR_FOOT
        foot = np.zeros_like(leg)
        foot[row:] = leg[row:]
        leg[row:] = 0
        ys, xs = np.nonzero(foot[..., 3])
        leg[ys, np.round(2 * ax - xs).astype(int)] = foot[ys, xs]
    return leg


def run_leg(leg, L, deg, hip_at):
    """A leg turned deg about its hip (RotSprite, + = the foot ahead), its hip on hip_at."""
    out = np.zeros((128, 128, 4), np.uint8)
    s, j = turn(leg, L["hip"], deg)
    return over(out, s, int(round(hip_at[0] - j[0])), int(round(hip_at[1] - j[1])))


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def colm(a):
    """The coloured (not outline) squares."""
    return (a[..., 3] > 0) & ~ink(a)


def nb4(m):
    """The number of 4-neighbours in the mask."""
    p = np.pad(m, 1).astype(int)
    return p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]


def bridge(a):
    """Rows of a turned leg with fewer than two coloured squares between its first and last coloured rows get the
    leg's own colours along its axis (the squares of the rows above and below): RotSprite pinches the idle's two-square
    knees and ankles to one square or to a row of bare outline on some turns (「像快要断腿了」; the review found a 0-square
    row across the far knee and ankle at -40/-44 degrees)."""
    for _ in range(2):
        c = colm(a)
        ys = np.nonzero(c.any(1))[0]
        for r in range(ys.min() + 1, ys.max()):
            if c[r].sum() >= 2:
                continue
            xs = [x for rr in (r - 1, r + 1) for x in np.nonzero(c[rr])[0]]
            if not xs:
                continue
            centre = float(np.mean(xs))
            have = list(np.nonzero(c[r])[0])
            for x in sorted(range(int(centre) - 2, int(centre) + 3), key=lambda x: abs(x - centre)):
                if len(have) >= 2:
                    break
                if x in have or (have and abs(x - have[0]) != 1):
                    continue
                src = None
                for rr in (r - 1, r + 1):
                    if c[rr, x]:
                        src = a[rr, x]
                        break
                if src is None:
                    for rr in (r - 1, r + 1):
                        cx = np.nonzero(c[rr])[0]
                        if len(cx):
                            src = a[rr, cx[np.argmin(abs(cx - x))]]
                            break
                a[r, x] = src
                have.append(x)
            c = colm(a)
    return a


def ring4(a):
    """The outline closed round the coloured squares (their clear 4-neighbours)."""
    add = (a[..., 3] == 0) & (nb4(colm(a)) > 0)
    a[add] = rgba("o")
    return a


def ticks(a):
    """Outline squares with a single opaque 4-neighbour (a black tick)."""
    return ink(a) & (nb4(a[..., 3] > 0) == 1)


def clean_leg(a):
    """A turned leg cleaned: cut rows bridged (bridge); a black tick hanging under a one-square nub (a toe or a knee
    tip RotSprite left: the review's crumb under the lifted far toe) folded in - the nub takes the outline, the tick
    goes; outline squares with no coloured neighbour go; the ring closed (ring4)."""
    a = bridge(a)
    for _ in range(3):
        c = colm(a)
        n = nb4(c)
        done = False
        for y, x in zip(*np.nonzero(ticks(a))):
            for dy, dx in N4:
                py, px = y + dy, x + dx
                if 0 <= py < 128 and 0 <= px < 128 and c[py, px] and n[py, px] <= 1:
                    a[py, px] = rgba("o")
                    a[y, x] = 0
                    done = True
        a[ink(a) & ~grow(colm(a))] = 0
        a = ring4(a)
        if not done:
            break
    return a


def over_soft(dst, src):
    """src over dst: its coloured squares everywhere, its outline only where dst is clear (a boot laid on a shin keeps
    the shin's colours across the join)."""
    m = src[..., 3] > 0
    put = m & (~ink(src) | (dst[..., 3] == 0))
    dst[put] = src[put]
    return dst


def run_legs(i, des, sm):
    """Frame i's two legs on the canvas (far, near) and their hip plates [(x, y, colour)]: the idle's legs turned about
    their hips (RUN) - the far one's boot laid back flat as drawn on its turned ankle (FAR_BOOT) - each with its lowest
    square `lift` rows over the soles' row, cleaned (clean_leg). A leg with a knee bend (RUN_BEND) turns in two pieces:
    the thigh about the hip, the shin and boot (from the knee row, both pieces share it) a further `bend` about the
    turned knee."""
    na, nl, fa, fl, nin = RUN[i][:5]
    fin = RUN[i][5] if len(RUN[i]) > 5 else RUN_HIP_IN["far"]
    nb, fb = RUN_BEND[i]
    out = []
    for L, deg, lift, near, bend in ((FAR_LEG, fa, fl, False, fb), (NEAR_LEG, na, nl, True, nb)):
        dx = nin if near else -fin
        hip = (L["hip"][0] + dx, L["hip"][1])
        leg = leg_piece(des, sm, L, near)
        kn = KNEES["near" if near else "far"]
        tk = about(kn, L["hip"], deg)                     # the turned knee (before the hip's move)
        shin_deg = deg + bend
        boot = None
        if not near:
            row, ankle = FAR_BOOT
            boot = np.zeros_like(leg)
            boot[row:] = leg[row:]
            leg[row:] = 0
        if bend:
            rows = np.arange(128)[:, None]
            thigh = leg.copy()
            thigh[rows[:, 0] > kn[1]] = 0
            shin = leg.copy()
            shin[rows[:, 0] < kn[1]] = 0
            a = np.zeros_like(des)
            s, j = turn(shin, kn, shin_deg)
            over(a, s, int(round(tk[0] + dx - j[0])), int(round(tk[1] - j[1])))
            over_soft(a, run_leg(thigh, L, deg, hip))
        else:
            a = run_leg(leg, L, deg, hip)
        if boot is not None:
            k2 = about(ankle, kn, shin_deg)
            ax, ay = tk[0] + k2[0] - kn[0], tk[1] + k2[1] - kn[1]
            if shin_deg <= FAR_BOOT_TIP[0]:               # drawn back: the boot tipped toe-down about the ankle
                bs, (jx, jy) = turn(boot, ankle, shin_deg * FAR_BOOT_TIP[1])
                b = over(np.zeros_like(des), bs, int(round(ax + dx - jx)), int(round(ay - jy)))
            else:
                b = over(np.zeros_like(des), boot, int(round(ax + dx - ankle[0])), int(round(ay - ankle[1])))
            over_soft(a, b)
        loose_ink(a)
        a = clean_leg(crumbs(a))
        ys = np.nonzero(a[..., 3].any(1))[0]
        sh = SOLES - lift - int(ys.max())
        plates = []
        for x, y in HIP_PLATES["near" if near else "far"]:
            px, py = about((x, y), L["hip"], deg)
            plates.append((int(round(px + dx)), int(round(py)) + sh, des[y, x].copy()))
        out.append((np.roll(a, sh, 0), plates))
    return out


def run(i, des, sm):
    """The idle's legs turned about the hips (run_legs), the idle's own thigh tops under the waist behind them
    (HIP_BAND); the upper body - head, wings, arms, the blade - the design's own, RUN_DROP rows lower on the
    contacts; the red hip plates laid back on their thighs over the skirt's edge (a plate the skirt would cover rides
    down with the hips, whole), the far one behind the near thigh."""
    upper = des.copy()
    upper[LEG_TOP:, NEAR_LEG["cols"][0]:FAR_LEG["cols"][1]] = 0
    upper[sm] = des[sm]                                   # the blade hangs below the hips with the fist
    out = np.zeros_like(des)
    c0, c1 = HIP_BAND
    out[LEG_TOP, c0:c1 + 1] = des[LEG_TOP, c0:c1 + 1]
    legs = run_legs(i, des, sm)
    for a, _ in legs:                                     # the near leg over the far one
        over(out, a)
    drop = RUN_DROP[i]
    out = over(out, upper, 0, drop)
    near = colm(legs[1][0])
    for k, (a, plates) in enumerate(legs):
        push = max(0, LEG_TOP + drop - min(y for _, y, _ in plates))
        for x, y, c in plates:
            if out[y + push, x, 3] and not (k == 0 and near[y + push, x]):
                out[y + push, x] = c
    _, keep = paste_head(out, des, 0, drop)
    out = finish(out, des, keep, drop)
    return fold_ticks(hip_spur(out, des, drop), des, keep, drop)


def fold_ticks(a, des, keep, drop=0):
    """(fix round 3, the review) black ticks the design does not have (an outline square with one opaque 4-neighbour:
    beside the laid far hip plate, under a tipped boot's heel) - one on an outline square goes; one on a coloured nub
    (a square with one coloured 4-neighbour) folds in: the nub takes the outline, the tick goes."""
    own = np.roll(ticks(des), drop, 0)
    for _ in range(3):
        c = colm(a)
        n = nb4(c)
        t = ticks(a) & ~own & ~keep
        if not t.any():
            break
        for y, x in zip(*np.nonzero(t)):
            for dy, dx in N4:
                py, px = y + dy, x + dx
                if a[py, px, 3] == 0:
                    continue
                if not c[py, px]:
                    a[y, x] = 0
                elif n[py, px] <= 1 and not keep[py, px]:
                    a[py, px] = rgba("o")
                    a[y, x] = 0
    return a


def hip_spur(a, des, drop):
    """Outline squares round the hips (rows LEG_TOP-2 down) with no coloured square round them, on the silhouette's
    edge, that the design does not have so (the far hip's spike (71, 86) got a second black square under it once the
    far thigh moved: the review) - cleared."""
    d = ink(des) & ~grow(colm(des))
    d = np.roll(d, drop, 0)
    for _ in range(3):
        k = ink(a)
        q = np.pad(a[..., 3] == 0, 1)
        open_side = q[:-2, 1:-1] | q[2:, 1:-1] | q[1:-1, :-2] | q[1:-1, 2:]
        lone = k & ~grow(colm(a)) & open_side & ~d
        lone[:LEG_TOP - 2] = False
        if not lone.any():
            break
        a[lone] = 0
    return a


def about(p, joint, deg):
    """The point p turned deg (counter-clockwise on screen, RotSprite's sense) about joint."""
    t = math.radians(deg)
    vx, vy = p[0] - joint[0], p[1] - joint[1]
    return (joint[0] + vx * math.cos(t) + vy * math.sin(t), joint[1] - vx * math.sin(t) + vy * math.cos(t))


def piece(des, m):
    a = np.zeros_like(des)
    a[m] = des[m]
    return a


def biggest(m):
    """The largest 8-connected part of the mask."""
    H, W = m.shape
    lab = np.zeros((H, W), int)
    best, n = (0, 0), 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        n += 1
        stack, size = [(y0, x0)], 0
        lab[y0, x0] = n
        while stack:
            y, x = stack.pop()
            size += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        stack.append((yy, xx))
        best = max(best, (size, n))
    return lab == best[1]


def parts(des, sm):
    """The design cut into masks: legs (from LEG_TOP down between the legs' columns), the near and far wings (the
    columns wings() uses), the torso (the rest without the blade: head, chest, both arms, the hips' skirt)."""
    op = des[..., 3] > 0
    rows = np.arange(128)[:, None]
    cols = np.arange(128)[None, :]
    legs = op & ~sm & (rows >= LEG_TOP) & (cols >= NEAR_LEG["cols"][0]) & (cols < FAR_LEG["cols"][1])
    upper = biggest(op & ~sm & ~legs)
    hm = head_mask(des)
    near_w = np.zeros_like(op)
    far_w = np.zeros_like(op)
    for r in range(56, 84):
        for c in range(128):
            if not upper[r, c] or hm[r, c]:
                continue
            if c <= (58 if r <= 72 else 55 if r <= 76 else 52):
                near_w[r, c] = True
            elif c >= (70 if r <= 76 else 72):
                far_w[r, c] = True
    return {"legs": legs, "upper": upper, "near_wing": near_w, "far_wing": far_w,
            "torso": biggest(upper & ~near_w & ~far_w)}


def ink_blocks(a):
    """The outline squares in solid 2 x 3 (or 3 x 2) blocks of outline."""
    k = ink(a)
    m = np.zeros_like(k)
    for h, w in ((2, 3), (3, 2)):
        win = np.ones((128 - h + 1, 128 - w + 1), bool)
        for dy in range(h):
            for dx in range(w):
                win &= k[dy:128 - h + 1 + dy, dx:128 - w + 1 + dx]
        for dy in range(h):
            for dx in range(w):
                m[dy:128 - h + 1 + dy, dx:128 - w + 1 + dx] |= win
    return m


def restore_inside(r, src, joint, deg):
    """(fix round 3, the review: RotSprite at 6 / 3 degrees doubled outlines round the armpit and the chest - 16 and 15
    solid 2 x 3 blocks of outline against the design's 9 - and thinned the red far arm) an outline square inside the
    turned sprite (opaque all round) whose square on the source, turned back, lies deep in a colour (that square and its
    4-neighbours coloured) takes that colour back."""
    c = colm(src)
    deep = c & (nb4(c) == 4)
    sblk = ink_blocks(src)
    for _ in range(3):
        op = r[..., 3] > 0
        blk = ink_blocks(r)
        m = ink(r) & (nb4(op) == 4)
        done = False
        for y, x in zip(*np.nonzero(m)):
            sx, sy = about((x, y), joint, -deg)
            sx, sy = int(round(sx)), int(round(sy))
            if not (0 <= sy < 128 and 0 <= sx < 128):
                continue
            if deep[sy, sx] or (blk[y, x] and c[sy, sx] and not sblk[sy, sx] and nb4(c[sy - 1:sy + 2, sx - 1:sx + 2])[1, 1] >= 2):
                r[y, x] = src[sy, sx]
                done = True
        if not done:
            break
    return r


def hit(i, des, sm):
    """Jolted back: everything over the hips turned HIT[i] degrees back about the standing point by RotSprite (or moved
    whole, HIT[i] a tuple (dx, dy)), on the
    idle's own legs; the blade - never resampled - hanging from the turned fist as drawn (it trails the lean); the
    approved head pasted square for square where the turn takes it."""
    p = parts(des, sm)
    hm = head_mask(des)
    if isinstance(HIT[i], tuple):                         # a rigid move of everything over the hips
        dx, dy = HIT[i]
        upper = des.copy()
        upper[p["legs"] | sm] = 0
        upper = loose_outline(upper, grow(sm))
        out = over(np.zeros_like(des), piece(des, p["legs"]))
        over(out, upper, dx, dy)
        out = over(out, blade(des, sm, (GRIP[0] + dx, GRIP[1] + dy), BASE))
        out, keep = paste_head(out, des, dx, dy)
        return finish(out, des, keep)
    rows = np.arange(128)[:, None]
    tip = p["near_wing"] & (rows <= HIT_TIP)
    upper = des.copy()
    upper[p["legs"] | hm | sm | tip] = 0
    upper = loose_outline(upper, grow(sm))
    r, (jx, jy) = rotsprite(upper, PIVOT, HIT[i])
    ru = over(np.zeros_like(des), r, int(round(PIVOT[0] - jx)), int(round(PIVOT[1] - jy)))
    ru = restore_inside(ru, upper, PIVOT, HIT[i])
    out = over(np.zeros_like(des), piece(des, p["legs"]))
    over(out, ru)
    ys, xs = np.nonzero(tip)                              # the near wing's hook moved whole where the turn takes it
    c = (xs.mean(), ys.mean())
    t = about(c, PIVOT, HIT[i])
    over(out, piece(des, tip), int(round(t[0] - c[0])), int(round(t[1] - c[1])))
    g = about(GRIP, PIVOT, HIT[i])
    out = over(out, blade(des, sm, (int(round(g[0])), int(round(g[1]))), BASE))
    ys, xs = np.nonzero(hm)
    c = (xs.mean(), ys.mean())
    t = about(c, PIVOT, HIT[i])
    out, keep = paste_head(out, des, int(round(t[0] - c[0])), int(round(t[1] - c[1])))
    return finish(out, des, keep)


def head_turned(des, quarter):
    """The approved head as a sprite turned by quarter turns (lossless), its middle (x, y) in it, and its middle on the
    design."""
    hm = head_mask(des)
    ys, xs = np.nonzero(hm)
    h = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    h[ys - ys.min(), xs - xs.min()] = des[ys, xs]
    h = np.ascontiguousarray(np.rot90(h, quarter))
    return h, ((h.shape[1] - 1) / 2, (h.shape[0] - 1) / 2), ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2)


def lay_head(a, des, quarter, centre):
    """The approved head (turned `quarter` quarter turns) laid over the frame with its middle on `centre`."""
    h, (cx, cy), _ = head_turned(des, quarter)
    x0, y0 = int(math.floor(centre[0] - cx + 0.5)), int(math.floor(centre[1] - cy + 0.5))
    over(a, h, x0, y0)
    keep = np.zeros(a.shape[:2], bool)
    ys, xs = np.nonzero(h[..., 3])
    keep[ys + y0, xs + x0] = True
    return a, keep


def qturn(sprite, joint, q):
    """The sprite turned q quarter turns counter-clockwise on screen (lossless) about joint: (sprite, joint in it)."""
    s, (jx, jy) = sprite, joint
    for _ in range(int(q) % 4):
        w = s.shape[1]
        s, jx, jy = np.ascontiguousarray(np.rot90(s)), jy, w - 1 - jx
    return s, (jx, jy)


def fill_inner(a):
    """Outline squares inside a turned leg - coloured on both sides along a row or a column, opaque all round (RotSprite
    left a row of outline through a knee or a boot: dead 4's lone '3', the near knee's 'oeo2e') - take the colour above,
    else to the left."""
    for _ in range(2):
        c = colm(a)
        op = a[..., 3] > 0
        k = ink(a)
        p, q = np.pad(c, 1), np.pad(op, 1)
        lr = p[1:-1, :-2] & p[1:-1, 2:]
        ud = p[:-2, 1:-1] & p[2:, 1:-1]
        shut = q[:-2, 1:-1] & q[2:, 1:-1] & q[1:-1, :-2] & q[1:-1, 2:]
        m = k & (lr | ud) & shut
        if not m.any():
            break
        for y, x in zip(*np.nonzero(m)):
            for yy, xx in ((y - 1, x), (y, x - 1), (y + 1, x), (y, x + 1)):
                if c[yy, xx]:
                    a[y, x] = a[yy, xx]
                    break
    return a


LIT = {("0", "0"): ("0", "e"), ("1", "1"): ("1", "2")}   # a dark pair and the design's own lit pair for it


def lit_rows(leg, last):
    """(phase 1b fix 1, the review: the near leg of dead 3 an almost black strip - '11' at the hip, '00' / '00' down the
    shin where the design has '0e') rows of a turned leg above `last` that are two dark squares of one colour take the
    design's pair with its light on the right ('0e', '12')."""
    g = colm(leg)
    for y in range(last):
        xs = np.nonzero(g[y])[0]
        if len(xs) != 2 or xs[1] != xs[0] + 1:
            continue
        key = tuple(D.letters(leg[y:y + 1, xs[0]:xs[1] + 1])[0])
        if key in LIT:
            for x, k in zip(xs, LIT[key]):
                leg[y, x] = rgba(k)
    return leg


def falling(des, sm, deg, quarter, wing=0):
    """The design without the blade turned deg back about DEAD_HEEL (RotSprite), each leg turned as a piece of its own
    and cleaned (clean_leg: no cut rows, no ticks), the upper body over them; the head left out and laid back on
    square for square, upright (quarter 0) or turned a quarter with the fall (quarter 1); nothing under the soles.
    Fix round 2 (the review): the near boot turned with the leg ended it in a 2-square peg ('oo' on the soles' row) - now
    only the shin turns and the idle's boot (NEAR_BOOT) is laid back as drawn under the turned ankle, flat on the soles'
    row (the heel planted); and the turn brought the near wing's top hook against the upright head (a third horn, an
    11-12 square pocket of background between hook, head and shoulder) - now nothing in the head's 3-square halo that
    was not within 3 squares of it on the design, nor of the near wing's hook within 2 (HALO: the turned figure's
    squares are marked by where they came from), the near wing turned `wing` degrees further down and out about its
    root (DEAD_WING) so its hook stays off the helmet."""
    hm = head_mask(des)
    fig = des.copy()
    fig[sm | hm] = 0
    fig = loose_outline(fig, grow(sm))
    for (r, c), k in NEAR_HIP.items():                    # (fix round 3) the near thigh's top under the fist, where the
        if r > 84:                                        # grip was: one square wide on the design, the 30-degree turn
            fig[r, c] = rgba(k)                           # pinched it to one square in two rows (dead 3)
    p = parts(des, sm)
    cols = np.arange(128)[None, :]
    rows = np.arange(128)[:, None]
    legs = [p["legs"] & (cols >= FAR_LEG["cols"][0]), p["legs"] & (cols < NEAR_LEG["cols"][1])]
    upper = fig.copy()
    upper[p["legs"]] = 0
    out = np.zeros_like(des)
    laid = []
    for k, m in enumerate(legs):
        boot = None
        if k == 0 and deg >= DEAD_FAR_BOOT[0]:            # the far boot turned on its own and laid on the turned ankle
            row, ankle = FAR_BOOT
            fb = piece(fig, m & (rows >= row))
            m = m & (rows < row)
        if k == 1:
            row, ankle = NEAR_BOOT
            boot = piece(fig, m & (rows >= row))
            m = m & (rows < row)
        r, (jx, jy) = rotsprite(piece(fig, m), DEAD_HEEL, deg)
        leg = over(np.zeros_like(des), r, int(round(DEAD_HEEL[0] - jx)), int(round(DEAD_HEEL[1] - jy)))
        loose_ink(leg)
        leg = clean_leg(crumbs(leg))
        if k == 0 and deg >= DEAD_FAR_BOOT[0]:
            ax, ay = about(FAR_BOOT[1], DEAD_HEEL, deg)
            bs, (jx, jy) = qturn(fb, FAR_BOOT[1], round(deg / 90))   # lossless: RotSprite broke it into specks
            bt = over(np.zeros_like(des), bs, int(round(ax - jx)), int(round(ay - jy)))
            over_soft(leg, bt)
            leg = clean_leg(fill_inner(leg))
        else:
            leg = fill_inner(leg)
        if boot is not None:                              # laid after the clean-up: the boot square for square
            c = colm(leg)
            last = int(np.nonzero(c.any(1))[0].max())
            ax = float(np.nonzero(c[last])[0].mean())     # the turned shin's last row: the ankle
            for y in range(last + 1, row):                # the shin ends higher: its last row carried down to the boot
                for x in np.nonzero(c[last])[0]:
                    leg[y, x] = leg[last, x]
            over_soft(leg, over(np.zeros_like(des), boot, int(round(ax - ankle[0])), 0))
            leg = ring4(leg)
            lit_rows(leg, row)
        over(out, leg)
        laid.append(leg)
    # where each square of the turned upper body came from: the head's 3-square halo on the design (HALO), the near
    # wing's squares there (its hook beside the horn)
    halo = grow(hm, HALO) & ~hm
    op = upper[..., 3] > 0
    mark = np.zeros_like(des)
    mark[op & halo] = (255, 0, 255, 255)
    mark[op & ~halo] = (0, 255, 0, 255)
    mark[op & p["near_wing"] & halo] = (0, 0, 255, 255)
    if quarter:                                           # the head turned a quarter ahead of the body: the far wing's
        mark[op & p["far_wing"] & halo] = (0, 255, 255, 255)  # hook came over its crest ('o55o', the review)
    nw = op & p["near_wing"]
    root = about(NEAR_ROOT, DEAD_HEEL, deg)
    for part, m, joint, d, at in ((upper, nw, NEAR_ROOT, deg + wing, root), (upper, op & ~nw, DEAD_HEEL, deg, DEAD_HEEL),
                                  (mark, nw, NEAR_ROOT, deg + wing, root), (mark, op & ~nw, DEAD_HEEL, deg, DEAD_HEEL)):
        r, (jx, jy) = rotsprite(piece(part, m), joint, d)
        if part is mark:
            if joint is NEAR_ROOT:
                mk = np.zeros_like(des)
            over(mk, r, int(round(at[0] - jx)), int(round(at[1] - jy)))
        else:
            over(out, r, int(round(at[0] - jx)), int(round(at[1] - jy)))     # the wing first, under the body
    for leg in laid:                                      # (fix round 3) the turned skirt's outline laid across a thigh's
        m = colm(leg) & ink(out)                          # top pinched it to one square (dead 3): the thigh's colours
        out[m] = leg[m]                                   # stay over it
    def marked(r, g, b):
        return (mk[..., 0] == r) & (mk[..., 1] == g) & (mk[..., 2] == b) & (mk[..., 3] > 0)
    _, _, c = head_turned(des, 0)
    out, keep = lay_head(out, des, quarter, about(c, DEAD_HEEL, deg))
    ys, _ = np.nonzero(keep)
    rows = np.arange(128)[:, None]
    near2 = grow(keep, HALO - 1) & ~keep
    out[near2 & marked(0, 0, 255)] = 0                    # the near wing's hook
    out[near2 & marked(0, 255, 255) & (rows < ys.min())] = 0
    if quarter == 0:                                      # upright: nothing from away from the head in its halo, and
        out[grow(keep, HALO) & ~keep & marked(0, 255, 0)] = 0   # nothing of the turned wings over the crest
        out[grow(keep, HALO) & ~keep & (rows < ys.min() + HALO)] = 0
    low = int(np.nonzero(out[..., 3].any(1))[0].max())
    if low > SOLES:
        out = np.roll(out, SOLES - low, 0)
        keep = np.roll(keep, SOLES - low, 0)
    return out, keep


THIGH_LAST = 92                      # the idle's thighs: rows LEG_TOP-92 (the red hip plates on them), knees on row 93
KNEES = {"near": (58.5, 93.0), "far": (68.5, 93.0)}


def leg_drawn(a, des, legm, near, hip, knee, ankle):
    """A leg bent at the knee for the lying pose: the idle's own thigh with its red hip plate (rows LEG_TOP-THIGH_LAST)
    turned from hip to knee (RotSprite), the shin knee -> ankle drawn in the idle's leg steel (LEG_STEEL, two squares on
    the slant) under it, the idle's own boot from its top row (BOOT_TOP - 1: '33' / '002') under the ankle (the near
    one mirrored about the ankle, its toe ahead like the far one's). The review: plain steel tubes lost the plates and
    the boots' top row in the death's longest frames."""
    rows = np.arange(128)[:, None]
    L = NEAR_LEG if near else FAR_LEG
    dh, dk = L["hip"], KNEES["near" if near else "far"]
    deg = math.degrees(math.atan2(dk[1] - dh[1], dk[0] - dh[0]) - math.atan2(knee[1] - hip[1], knee[0] - hip[0]))
    thigh = turned(piece(des, legm & (rows <= THIGH_LAST)), dh, deg, hip)
    loose_ink(thigh)
    thigh = clean_leg(crumbs(thigh))
    top = BOOT_TOP - 1
    boot = piece(des, legm & (rows >= top))
    ys, xs = np.nonzero(legm & (rows == top - 1) & colm(des))
    ax = xs.mean()
    if near:
        m = np.zeros_like(boot)
        ys, xs = np.nonzero(boot[..., 3])
        m[ys, np.round(2 * ax - xs).astype(int)] = boot[ys, xs]
        boot = m
    limb(a, [knee, ankle], LEG_STEEL, core_r=1.25)
    over(a, thigh)
    return over(a, boot, int(round(ankle[0] - ax)), int(round(ankle[1] - (top - 1))))


def lying(des, sm, settle):
    """On his back (League's Death, frames 5-8): the head, chest, near arm and the hips' skirt turned a quarter
    (lossless: the head square for square, the face up, the horns behind), the far red arm under him (FAR_ARM cut, the
    waist painted), the near wing folded under the shoulders and out behind the head, the far wing hidden behind the
    body; both legs bent with the knees up (LYING_LEGS) on the idle's own boots. settle: rows the body and the knees
    still ride over the rest (the frame after the fall)."""
    p = parts(des, sm)
    far = np.zeros(des.shape[:2], bool)
    for r, (c0, c1) in FAR_ARM.items():
        far[r, c0:c1 + 1] = True
    t = piece(des, p["torso"] & ~far)
    for (r, c), k in WAIST.items():
        t[r, c] = rgba(k)
    T = np.ascontiguousarray(np.rot90(t))
    ys, xs = np.nonzero(T[..., 3])
    dy = SOLES - ys.max()
    T = np.roll(T, dy, 0)
    out = np.zeros_like(des)
    W = np.ascontiguousarray(np.rot90(piece(des, p["near_wing"])))
    # (fix round 3, the review) the wing's claw tip - one square on its lowest coloured row - hung under him to the soles
    # like a spike: folded into the wing's outline
    # (phase 1b fix 1, the review: two crimson squares of the strand still hung under the claw) the strand folded in
    # from its end while it is one square wide, within LYING_TIP rows of the lowest
    c = colm(W)
    low = int(np.nonzero(c.any(1))[0].max())
    for _ in range(LYING_TIP):
        c = colm(W)
        tip = c & (nb4(c) <= 1)
        tip[:low - LYING_TIP + 1] = False
        if not tip.any():
            break
        W[tip] = rgba("o")
    W = loose_outline(W)
    over(out, W, LYING_WING[0], LYING_WING[1] + dy)
    ys, xs = np.nonzero(T[..., 3])
    hip = (xs.max() - 3, SOLES - LYING_HIP)
    cols = np.arange(128)[None, :]
    near_m = p["legs"] & (cols < NEAR_LEG["cols"][1])
    far_m = p["legs"] & (cols >= FAR_LEG["cols"][0])
    (kx, ky), (ax, ay), (fx, fy) = LYING_LEGS
    legs = np.zeros_like(des)
    leg_drawn(legs, des, far_m, False, (hip[0] + fx, hip[1] + fy), (hip[0] + kx + fx + 1, hip[1] + ky + fy - settle),
              (hip[0] + kx + ax + fx + 2, hip[1] + ky + ay))
    over(out, legs)
    over(out, T)
    legs = np.zeros_like(des)
    leg_drawn(legs, des, near_m, True, hip, (hip[0] + kx, hip[1] + ky - settle), (hip[0] + kx + ax, hip[1] + ky + ay))
    over(out, legs)
    keep = np.roll(np.ascontiguousarray(np.rot90(head_mask(des))), dy, 0)
    ys, xs = np.nonzero(keep)
    sx = int(round(LYING_HEAD_X - (xs.min() + xs.max()) / 2))
    sy = SOLES - settle - int(np.nonzero(out[..., 3].any(1))[0].max())
    return np.roll(np.roll(out, sy, 0), sx, 1), np.roll(np.roll(keep, sy, 0), sx, 1)


def trim_strands(a, keep, r0, c1, n):
    """Coloured squares at the end of a one-square strand (one coloured 4-neighbour or none) from row r0 down, left of
    column c1, take the outline, `n` times over; the outline left with no colour round it goes (loose_ink, in finish)."""
    rows = np.arange(128)[:, None]
    cols = np.arange(128)[None, :]
    zone = (rows >= r0) & (cols <= c1) & ~keep
    for _ in range(n):
        c = colm(a)
        end = c & (nb4(c) <= 1) & zone
        if not end.any():
            break
        a[end] = rgba("o")
    a[ink(a) & ~grow(colm(a)) & zone] = 0
    return a


def dead(i, des, sm):
    """League's Death: thrown back - the figure turns back about the near heel (DEAD_TILT, RotSprite; the head laid on
    square for square, upright, then turned a quarter with the fall), the blade knocked out of the fist and flying up
    behind him (DEAD_BLADE: exact directions, ORIENT), then on his back with the knees up (lying), a row of bounce
    (DEAD_SETTLE) and still; the blade on the ground behind his head, clear of the boots."""
    if i == 0:
        return des.copy()
    tilt, quarter = DEAD_TILT[i]
    if tilt is None:
        out, keep = lying(des, sm, DEAD_SETTLE[i])
    else:
        out, keep = falling(des, sm, tilt, quarter, DEAD_WING[i])
    if i in DEAD_TRIM:                                    # a one-square strand of the falling wing's hook
        r0, c1, n = DEAD_TRIM[i]
        trim_strands(out, keep, r0, c1, n)
    angle, grip = DEAD_BLADE[i]
    out = over(blade(des, sm, grip, angle), out)          # the blade behind him
    return finish(out, des, keep)


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def build(tags=None):
    with open(lp(CELLS), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    des = design()
    sm = sword_mask(des)
    out = {}
    for tag in TAGS:
        if tag in CODEX or tag in KEEP or (tags and tag not in tags):
            continue
        frs = cells["tags"][tag]
        cols, rows = layout(len(frs))
        sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
        for i, fr in enumerate(frs):
            a = frame(tag, i, des, sm)
            px, py = fr["pivot"]
            X, Y = (i % cols) * cw, (i // cols) * ch
            cell = np.zeros((ch, cw, 4), np.uint8)
            over(cell, a, px - PIVOT[0], py - PIVOT[1])
            sheet[Y:Y + ch, X:X + cw] = cell
        out[tag] = sheet
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", help="write the strips to this folder instead of assets/source/native")
    ap.add_argument("--tag", action="append", help="only these tags")
    args = ap.parse_args()
    same = True
    for tag, a in build(args.tag).items():
        big = np.repeat(np.repeat(a, Z, 0), Z, 1)
        path = os.path.join(args.out or OUT, f"aatrox_{tag}.png")
        if args.check:
            same &= np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")), big)
        else:
            Image.fromarray(big).save(lp(path))
        print(tag, a.shape)
    if args.check:
        print("same" if same else "DIFFERS")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()

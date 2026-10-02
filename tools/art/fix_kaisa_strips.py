#!/usr/bin/env python3
"""Kai'Sa's strips finished after Codex's deliveries: the run rebuilt from her idle, the dark legs of W's crouch and
the far pod of R's launch given their colours.

    python tools/art/fix_kaisa_strips.py [--check] [--preview DIR]

Codex's first strips (assets/source/kaisa/codex_strips, 2026-10-02) drew every swinging leg as a solid block of the
outline colour (#160722) two to four squares thick, a dark stick that read as a tail (run 1-3 and 5-8, W 2 and 6), and
the far pod of R's launch (1-2) as a near-black spike; its run planted one leg for the whole loop (one step a cycle
where League's run_base takes two). The user: "有问题的地方你进行收尾修正就行了" (no fix pack).
- run (the user, of the accepted version: "这版走路可以了"): built from the idle's own pixels. The cut is the belt: the
  idle above it and its two arms stay, lowered a row on the contact frames (RUN_DY). The two magenta-and-gold pieces
  under the belt are her thighs - every earlier run froze them in the idle's A-stance and redrew only the legs from
  the knee down ("脱节", "大腿小腿一起动", a leg hanging off the side) - so each thigh is the idle's own thigh piece,
  sheared so its knee swings under her middle; both lower legs are the idle's screen-right one (knee guard, shin and
  boot, equally thick), hung from the thigh: on the ground sheared so the boot slides back, swinging sheared, for the
  heel kick the boot lifted and moved back behind the knee guard (RUN_POSE). The gait is League's in the game's camera
  (its run rendered at game size per joint: the legs stay under her and lift, not splay): the near leg stands in
  frames 2-5, the far one in 6-8 and 1. Earlier tries, all rejected: legs drawn under Codex's or the idle's upper body
  in its materials, Codex's redo and legs-only passes, row-shifted idle legs ("截肢"), skinned bones, capsules on
  League's side-view angles, whole idle legs sliding ("腿像木板整条滑, 腿叉得太开, 两腿一粗一细, 整体不像跑步");
- the idle: its two lower legs were one thin, one thick ("待机时候腿一粗一细"): the screen-left one is now the
  screen-right one mirrored, its boot where the old one stood (EVEN_ROWS); every standing action and the run take
  their legs from this idle, and kaisa_idle.png is written with it;
- the posed frames (R's launch 1-3, its dash, its landing 1-2, the death 1-6) on the idle's own legs, posed per frame
  (POSED_LEGS: thigh pieces sheared or turned, the lower legs sheared, bent or turned, the soles on the ground): Codex
  drew their legs bulkier and darker than the idle's (the user: "你要改全改啊 什么SKILL 大招里面的腿还是不一样"); R 3's
  back leg, first redrawn in the idle's materials, is the idle's own leg too; the death's last two frames (face down)
  keep Codex's;
- R 1 and 2: the dark hair spike's inside in the hair's mid shade, its left edge lit;
- the standing action frames (attack 2-5, Q 2-5, W 2-6) on the idle's whole body: Codex drew them on long legs
  spread 30 squares apart under a narrower, darker torso (the user: "待机时腿部和放技能时候不一样？待机时的腿部更好"; with
  the idle's legs alone under Codex's torso the waist looked pinched: "你统一一下吧 感觉模型有点变形了"). Each frame is the
  idle's torso and plates (rows 11 over to 2 under the pivot, its hanging arms cut out: ARM_CUT) and its legs at the
  idle's own place, over Codex's head, pods, hair and arms - its frame without its legs (its pieces under the pivot
  reaching 6 rows down), moved so its pasted head sits on the idle's head (the crouch of W 3-4, 4 rows, and the hops of
  Q 5 and W 5 undone: W fires standing, as League's); specks left over go. Hit 1 (a head Codex turned) keeps its
  torso and only stands on the idle's legs (the idle's rows 1-11 under its pivot moved under its torso).
Writes assets/source/native/kaisa_idle.png, kaisa_run.png, kaisa_attack.png, kaisa_skill.png, kaisa_skill2.png, kaisa_hit.png,
kaisa_ult.png, kaisa_ult_dash.png, kaisa_ult_land.png and kaisa_dead.png (8x, the cells of
kaisa_cells.json: R's delivered 4-frame strip split into the launch, 1-3, and the dash pose the kit forces while she
flies, 4); then run tools/art/import_native.py --hero kaisa.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from rig_nocturne import rotsprite  # noqa: E402
from native_refs import Z, layout  # noqa: E402

NAT = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "kaisa", "codex_strips")


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


INK = rgb("160722")                       # the outline
INK2 = rgb("1E0A2A")                      # the second near-black
DARK = {INK, INK2}
# the idle's pivot; its legs (the one place every standing action and the run take theirs from)
IDLE_PIVOT = (48, 70)
# the idle's two lower legs were one thin, one thick (its A-stance: the screen-left one seen slanting; the user:
# "待机时候腿一粗一细"): the screen-left lower leg (rows 4-11 under the pivot) is the screen-right one mirrored, hung under
# the left thigh's bottom middle and sheared EVEN_FOOT squares at the sole so its boot stands where the old one stood
EVEN_ROWS = (4, 11)
EVEN_FOOT = -3
# the frames Codex drew as the idle itself (the attack's, Q's and W's first and last, the hit's second, the landing's
# last): their legs evened the same way (the user: "你要改全改啊", "攻击的腿也不一样")
EVEN_FRAMES = {"attack": [0, 5], "skill": [0, 5], "skill2": [0, 6], "hit": [1], "ult_land": [3]}
# the run (the user, of the accepted version: "这版走路可以了"), built from the idle's own pixels: the idle above the
# belt (row RUN_BELT under the pivot... -4) and its two arms stay, lowered RUN_DY; each thigh is the idle's own thigh
# piece under the belt (rows -3..3: the magenta-and-gold plate over the bodysuit - her THIGHS, which every earlier run
# froze in the idle's A-stance: "脱节", "大腿小腿一起动", a leg hanging off the side), sheared so its knee swings under
# her middle; BOTH lower legs are the idle's screen-right lower leg (rows 4-11: knee guard, shin, boot - equally thick:
# "左腿细右腿粗？"), hung from the thigh's bottom middle: on the ground sheared so the boot slides back, swinging
# sheared, or for the heel kick ("fold") the knee guard under the knee and the boot lifted and moved back behind it.
# Gait as League's in the game's camera (its run rendered at game size per joint): the near (screen-left) leg stands in
# frames 2-5, the far one in 6-8 and 1; the body a row lower on the contact frames
RUN_BELT = -4
RUN_THIGH = (-3, 3)                       # thigh rows from the pivot
RUN_LOWER = (4, 11)                       # lower-leg rows
RUN_ARMS = (-9, 9)                        # columns from the pivot at or beyond which rows -3..3 are the arms
RUN_SPLIT = 0                             # near thigh x <= RUN_SPLIT, far thigh x > RUN_SPLIT
RUN_DY = [1, 1, 0, 0, 1, 1, 0, 0]
# per frame and leg: (lift rows, thigh shear at the knee, "down" / "rot", the lower leg's shear at the sole / its turn
# about the knee in degrees (RotSprite, + counter-clockwise: the heel kicks swing it back, clockwise), x shift). The
# heel kicks first moved the boot up behind the knee guard, the shin between gone (the user: "脚跟和脚空出来一大截"); the
# far leg's kick in frame 3 went behind the near leg, so there it is a lifted leg, its shin turned back 35 degrees,
# in front of the other. A standing leg on a frame the body is lowered (RUN_DY 1) is lifted 1 too, so its sole stays
# on the soles row (lowered with the body, its sole outline fell under row 11 and was cut off)
RUN_POSE = [
    {"near": (2, 3, "down", 0, 0), "far": (1, -2, "down", -1, 0)},
    {"near": (1, 2, "down", 0, 0), "far": (1, -3, "down", -2, 0)},
    {"near": (0, 1, "down", 0, 0), "far": (3, -1, "rot", -35, 0)},
    {"near": (0, 1, "down", -1, 0), "far": (3, 0, "down", -1, 0)},
    {"near": (1, 0, "down", -1, 0), "far": (2, 0, "down", 0, 0)},
    {"near": (1, 0, "down", -2, 0), "far": (1, -1, "down", 0, 0)},
    {"near": (2, 1, "rot", -70, 0), "far": (0, -2, "down", 0, 0)},
    {"near": (3, 3, "down", -1, 0), "far": (0, -2, "down", -1, 0)},
]
# standing frames (indices from 0) on the idle's whole body; hit 1 on its legs only
IDLE_BODY = {"attack": [1, 2, 3, 4], "skill": [1, 2, 3, 4], "skill2": [1, 2, 3, 4, 5]}
IDLE_LEGS = {"hit": [0]}
LEG_CUT = 0                               # legs only: the frame keeps its rows down to this one under the pivot
# the idle's part under that: HIP_SPAN columns (from its pivot) for the rows 1-3 under it (its plates, not its hanging
# arms), LEG_SPAN for the rows 4-11 (both legs and boots)
HIP_SPAN, LEG_SPAN = (-6, 10), (-12, 12)
# the idle's torso and plates: rows TORSO from its pivot, less its hanging arms - per row (from the pivot) the left arm
# is x <= ARM_CUT[y][0], the right arm x >= ARM_CUT[y][1]
TORSO = (-11, 2)
ARM_CUT = {-7: (-8, 14), -6: (-8, 6), -5: (-8, 6), -4: (-10, 7), **{y: (-10, 9) for y in range(-3, 3)}}
ARM_ROW = (-13, 14)                       # the other torso rows (under the chin): columns -12 to 13
# Codex pasted the design's head in every frame: the idle's rows 20 to 12 over its pivot, columns -4 to 8, find it
HEAD = (-4, -20, 9, -11)                  # x0, y0, x1, y1 from the pivot (x1, y1 exclusive)
# R's launch (frames 1 and 2): the hair whipping up over her head (League's Spell4_in) was drawn in the hair's darkest
# shade only and read as a black spike: its inside in the hair's mid shade, its left edge lit (box from the pivot)
HAIR_D, HAIR, HAIR_L = rgb("351036"), rgb("4E194C"), rgb("8A387A")
R_HAIR = {0: (-9, -33, -1, -19), 1: (-9, -29, -1, -19)}
# the frames whose legs Codex drew in a pose (R's launch 1-3, its dash, its landing 1-2, the death 1-6) on the idle's
# own legs, posed (the user: "你要改全改啊 什么SKILL 大招里面的腿还是不一样"): the frame keeps its rows down to "belt"
# (rows from its pivot, + down) and the "keep" boxes (x0, y0, x1, y1 from the pivot: its claws, arms, hair); its other
# pixels in the "clear" columns under the belt go. Each leg is the idle's thigh piece (rows -3..3: plate and
# bodysuit; near x <= 0) over its screen-right lower leg (rows 4-11, both legs equally thick), per leg: "hip" where
# the thigh's top middle goes; "drop" thigh rows left out of its middle (foreshortened); "kt" its shear at the knee,
# or "tr" degrees turned about the top (RotSprite, + counter-clockwise); "mode" "down" (the lower leg sheared "ks" at
# the sole), "bend" (only the shin sheared, the boot moved whole, so it keeps the idle's shape) or "rot" (turned "ks"
# degrees about the knee); "ground" the shin lengthened or shortened so the sole lands on the soles row; "flip" the
# lower leg mirrored (toe left). Fitted per frame (work/ks/legs_onto.py); death 7-8 (face down on the ground) keep
# Codex's legs, hardly seen
POSED_LEGS = {
    ("ult", 0): {"belt": 0, "keep": [[-12, 1, -8, 1]],
                 "near": {"hip": [-4, -1], "tr": -65, "flip": True, "mode": "bend", "ks": -2, "ground": True},
                 "far": {"hip": [3, -1], "tr": 25, "mode": "bend", "ks": 1, "ground": True}},
    ("ult", 1): {"belt": 0, "clear": [-25, 14], "keep": [[-9, 1, 1, 4], [-19, 1, -15, 4]],
                 "near": {"hip": [-12, -1], "drop": 2, "kt": -1, "mode": "down", "ks": -5, "flip": True},
                 "far": {"hip": [2, -1], "tr": 35, "mode": "bend", "ks": 1, "ground": True}},
    ("ult", 2): {"belt": 0, "clear": [-28, 16], "keep": [[8, -4, 16, 3]],
                 "near": {"hip": [-8, -3], "kt": -5, "mode": "down", "ks": -2, "flip": True},
                 "far": {"hip": [1, -2], "tr": 80, "drop": 1, "mode": "rot", "ks": -35}},
    ("ult_dash", 0): {"belt": 0, "clear": [-32, -8], "keep": [[-12, 1, -7, 7]],
                      "near": {"hip": [-15, -1], "drop": 1, "kt": -6, "mode": "rot", "ks": -103},
                      "far": {"hip": [-16, 2], "drop": 2, "kt": -1, "mode": "rot", "ks": -95}},
    ("ult_land", 0): {"belt": 1, "clear": [-18, 16], "keep": [[7, -2, 16, 11]],
                      "near": {"hip": [-4, 1], "drop": 3, "kt": -7, "mode": "bend", "ks": -2, "flip": True,
                               "ground": True},
                      "far": {"hip": [1, 1], "drop": 4, "kt": -3, "mode": "down", "ks": -1}},
    ("ult_land", 1): {"belt": 0, "clear": [-20, 16], "keep": [[7, 1, 13, 9]],
                      "near": {"hip": [-4, -2], "drop": 1, "kt": -5, "mode": "bend", "ks": -2, "flip": True,
                               "ground": True},
                      "far": {"hip": [2, -2], "drop": 1, "kt": 0, "mode": "bend", "ks": -1, "ground": True}},
    ("dead", 0): {"belt": -4, "near": {"hip": [-2, -3], "kt": -2, "flip": True, "ks": 1.4},
                  "far": {"hip": [5, -3], "kt": -1, "ks": -1.5}},
    ("dead", 1): {"belt": -4, "near": {"hip": [1, -3], "flip": True, "kt": -3}, "far": {"hip": [6, -3], "ks": -1}},
    ("dead", 2): {"belt": -4, "keep": [[-10, -3, -3, 3], [12, -3, 20, 0]],
                  "near": {"hip": [1, -3], "kt": 0, "flip": True, "mode": "down", "ks": -1.5},
                  "far": {"hip": [5, -3], "kt": 2, "mode": "down", "ks": -2.5}},
    ("dead", 3): {"belt": -1, "keep": [[-10, -1, -6, 7], [10, -1, 14, 4]],
                  "near": {"hip": [-1, -2], "drop": 1, "flip": True, "ks": 1},
                  "far": {"hip": [5, -2], "drop": 1, "ks": -2}},
    ("dead", 4): {"belt": 0, "keep": [[-14, -6, -8, 3], [-13, 4, -11, 4], [4, -2, 12, 9]],
                  "far": {"hip": [2, 1], "drop": 4, "kt": -2, "ks": -1},
                  "near": {"hip": [-4, -1], "drop": 2, "kt": -3, "ks": -1, "flip": True}},
    ("dead", 5): {"belt": 2, "clear": [-18, 12],
                  "near": {"hip": [-6, 1], "drop": 4, "kt": -1, "mode": "down", "ks": -5, "flip": True},
                  "far": {"hip": [-1, 1], "drop": 4, "kt": 1, "mode": "down", "ks": 2}},
}


def lp(path):
    return G.lp(path)


def cells_of(path, n, cell):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    cols, _ = layout(n)
    cw, ch = cell
    return [a[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw].copy() for k in range(n)]


def sheet_of(frames, cell):
    cols, rows = layout(len(frames))
    cw, ch = cell
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k, f in enumerate(frames):
        out[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw] = f
    return np.repeat(np.repeat(out, Z, 0), Z, 1)


def colour(a, y, x):
    return tuple(int(v) for v in a[y, x, :3])


def rnd(v):
    return int(math.floor(v + 0.5))


def even_legs(idle):
    """The idle with its screen-left lower leg replaced by the screen-right one mirrored (EVEN_ROWS, EVEN_FOOT)."""
    ix, iy = IDLE_PIVOT
    a = idle.copy()
    y0, y1 = iy + EVEN_ROWS[0], iy + EVEN_ROWS[1]
    right = {(x, y): idle[y, x].copy() for y in range(y0, y1 + 1) for x in range(ix + 1, ix + 12) if idle[y, x, 3]}
    top = [x for (x, y) in right if y == y0]
    rmid = (min(top) + max(top)) // 2
    lx = [x for x in range(ix - 10, ix + 1) if idle[y0 - 1, x, 3]]
    lmid = (min(lx) + max(lx)) // 2
    a[y0:y1 + 1, ix - 18:ix + 1] = 0
    for (x, y), c in right.items():
        a[y, lmid - (x - rmid) + rnd(EVEN_FOOT * (y - y0) / (y1 - y0))] = c
    return a


def even_frame(frame, pivot):
    """even_legs on a frame standing on `pivot` (a copy of the idle)."""
    dx, dy = IDLE_PIVOT[0] - pivot[0], IDLE_PIVOT[1] - pivot[1]
    return np.roll(np.roll(even_legs(np.roll(np.roll(frame, dx, 1), dy, 0)), -dx, 1), -dy, 0)


def run_thigh(idle, leg):
    ix, iy = IDLE_PIVOT
    out = {}
    for y in range(iy + RUN_THIGH[0], iy + RUN_THIGH[1] + 1):
        for x in range(ix + RUN_ARMS[0] + 1, ix + RUN_ARMS[1]):
            if idle[y, x, 3] and ((leg == "near") == (x <= ix + RUN_SPLIT)):
                out[(x, y)] = idle[y, x].copy()
    return out


def run_lower(idle):
    """The idle's screen-right lower leg, outline and all, from its top row's middle (whole squares)."""
    ix, iy = IDLE_PIVOT
    px = {(x, y): idle[y, x].copy() for y in range(iy + RUN_LOWER[0], iy + RUN_LOWER[1] + 1)
          for x in range(ix, ix + 12) if idle[y, x, 3]}
    top = [x for (x, y) in px if y == iy + RUN_LOWER[0]]
    mid = (min(top) + max(top)) // 2
    return {(x - mid, y - iy - RUN_LOWER[0]): c for (x, y), c in px.items()}


def run_leg(idle, lower, leg, lift, kt, mode, ks, sx, dy):
    ix, iy = IDLE_PIVOT
    t0, t1 = iy + RUN_THIGH[0], iy + RUN_THIGH[1]
    thigh = {(x + rnd(kt * (y - t0) / (t1 - t0)) + sx, y - lift + dy): c for (x, y), c in run_thigh(idle, leg).items()}
    yb = max(y for _, y in thigh)
    xs = [x for (x, y) in thigh if y == yb]
    kx = (min(xs) + max(xs)) // 2
    n = RUN_LOWER[1] - RUN_LOWER[0]
    out = {}
    for (dx, r), c in lower.items():
        if mode == "down":
            out[(kx + dx + rnd(ks * r / n), yb + 1 + r)] = c
    if mode == "rot":                                 # the whole lower leg turned about the knee
        xs_ = [dx for dx, _ in lower]
        x0, h = min(xs_), max(r for _, r in lower) + 1
        arr = np.zeros((h, max(xs_) - x0 + 1, 4), np.uint8)
        for (dx, r), c in lower.items():
            arr[r, dx - x0] = c
        rot, (jx, jy) = rotsprite(arr, (-x0, 0), ks)
        for yy, xx in zip(*np.nonzero(rot[..., 3])):
            out[(kx + xx - jx, yb + 1 + yy - jy)] = rot[yy, xx]
    out.update(thigh)
    return out


def run_frame(idle, k, pivot):
    """Run frame k on its cell: the far leg, the near leg over it, then the idle above the belt and its arms lowered
    RUN_DY[k]; standing on `pivot`."""
    ix, iy = IDLE_PIVOT
    dy = RUN_DY[k]
    lower = run_lower(idle)
    out = np.zeros_like(idle)
    for leg in ("far", "near"):
        for (x, y), c in run_leg(idle, lower, leg, *RUN_POSE[k][leg], dy).items():
            if y > iy + RUN_BELT + dy:
                out[y, x] = c
    up = idle.copy()
    for y in range(iy + RUN_BELT + 1, up.shape[0]):
        for x in range(up.shape[1]):
            if not (y <= iy + RUN_THIGH[1] and (x <= ix + RUN_ARMS[0] or x >= ix + RUN_ARMS[1])):
                up[y, x] = 0
    up = np.roll(up, dy, 0)
    m = up[..., 3] > 0
    out[m] = up[m]
    out[iy + 12:] = 0
    return np.roll(out, pivot[0] - ix, 1) if pivot[0] != ix else out


def drop_specks(a, most=9):
    """Pieces (8-connected) of at most `most` squares cleared: what is left of a long leg after it is cleared by colour."""
    op = a[..., 3] > 0
    seen = np.zeros(op.shape, bool)
    out = a.copy()
    for y0, x0 in zip(*np.nonzero(op)):
        if seen[y0, x0]:
            continue
        stack, piece = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            piece.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        if len(piece) <= most:
            for y, x in piece:
                out[y, x] = 0
    return out


def run_at(cell, y, px, lo=-10, hi=12):
    """The run of opaque squares on row y holding the column nearest px: (first, last)."""
    row = cell[y, :, 3] > 0
    best, x = None, px + lo
    while x <= px + hi:
        if row[x]:
            a = x
            while x + 1 < len(row) and row[x + 1]:
                x += 1
            d = 0 if a <= px <= x else min(abs(a - px), abs(x - px))
            if best is None or d < best[0]:
                best = (d, a, x)
        x += 1
    return best[1], best[2]


def pieces_of(mask):
    """8-connected pieces: (labels, count)."""
    lab = np.zeros(mask.shape, int)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        stack = [(y0, x0)]
        lab[y0, x0] = n
        while stack:
            y, x = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        stack.append((ny, nx))
    return lab, n


def on_idle_legs(frame, pivot, idle):
    """The frame down to LEG_CUT under its pivot over the idle's plates' lower edge and legs, moved under its torso."""
    px, py = pivot
    ix, iy = IDLE_PIVOT
    out = without_legs(frame, py + LEG_CUT)
    a0, a1 = run_at(frame, py + LEG_CUT, px)
    b0, b1 = run_at(idle, iy + LEG_CUT, ix)
    idle_legs_at(out, px, py, idle, dx=int(round((a0 + a1) / 2 - (b0 + b1) / 2)), first=LEG_CUT + 1)
    return drop_specks(out)


def head_at(frame, head, hm):
    """(x, y) of the pasted head's box in the frame (every square of it exact), or None."""
    h, w = hm.shape
    for y in range(frame.shape[0] - h):
        for x in range(frame.shape[1] - w):
            win = frame[y:y + h, x:x + w]
            if ((win[..., 3] > 0) == hm).all() and (win[hm][:, :3] == head[hm][:, :3]).all():
                return x, y
    return None


def without_legs(frame, py):
    """The frame less its pieces under the pivot that reach 6 rows down (legs); arm tips over that stay."""
    out = frame.copy()
    below = np.zeros(frame.shape[:2], bool)
    below[py + 1:] = frame[py + 1:, :, 3] > 0
    lab, n = pieces_of(below)
    for k in range(1, n + 1):
        if np.nonzero(lab == k)[0].max() >= py + 6:
            out[lab == k] = 0
    return out


def idle_legs_at(out, px, py, idle, dx=0, first=1):
    """The idle's rows first..11 under its pivot (plates' lower edge between its arms, then both legs) at (px + dx, py)."""
    ix, iy = IDLE_PIVOT
    for y in range(first, 12):
        x0, x1 = HIP_SPAN if y <= 3 else LEG_SPAN
        for x in range(x0, x1 + 1):
            if idle[iy + y, ix + x, 3]:
                out[py + y, px + x + dx] = idle[iy + y, ix + x]


def on_idle_body(frame, pivot, idle):
    """Codex's head, pods, hair and arms moved onto the idle's torso, plates and legs (see the docstring)."""
    px, py = pivot
    ix, iy = IDLE_PIVOT
    x0, y0, x1, y1 = HEAD
    head = idle[iy + y0:iy + y1, ix + x0:ix + x1]
    hm = head[..., 3] > 0
    pos = head_at(frame, head, hm)
    if pos is None:
        sys.exit("no pasted head in a standing frame")
    dx, dy = pos[0] - (px + x0), pos[1] - (py + y0)
    parts = without_legs(frame, py)
    out = np.zeros_like(frame)
    ys, xs = np.nonzero(parts[..., 3])
    ty, tx = ys - dy, xs - dx
    ok = (ty >= 0) & (ty < out.shape[0]) & (tx >= 0) & (tx < out.shape[1])
    out[ty[ok], tx[ok]] = parts[ys[ok], xs[ok]]
    for y in range(TORSO[0], TORSO[1] + 1):
        lo, hi = ARM_CUT.get(y, ARM_ROW)
        for x in range(lo + 1, hi):
            if idle[iy + y, ix + x, 3]:
                out[py + y, px + x] = idle[iy + y, ix + x]
    idle_legs_at(out, px, py, idle, first=TORSO[1] + 1)
    return drop_specks(out)


def r_frame(frame, pivot, k):
    px, py = pivot
    a = frame.copy()
    if k in R_HAIR:
        x0, y0, x1, y1 = R_HAIR[k]
        for y in range(py + y0, py + y1 + 1):
            for x in range(px + x0, px + x1 + 1):
                if a[y, x, 3] and colour(a, y, x) == HAIR_D:
                    left = colour(a, y, x - 1) if a[y, x - 1, 3] else None
                    a[y, x, :3] = HAIR_L if left in DARK else HAIR
    return a


def posed_leg(idle, lower, leg, p):
    """One of the idle's legs posed by p (see POSED_LEGS): {(x, y) from the frame's pivot: rgba}."""
    ix, iy = IDLE_PIVOT
    th = {(x - ix, y - iy): c for (x, y), c in run_thigh(idle, leg).items()}
    yt = min(y for _, y in th)
    xs = [x for (x, y) in th if y == yt]
    tx = (min(xs) + max(xs)) // 2
    rows = sorted({y for _, y in th})
    drop = int(p.get("drop", 0))
    mid = len(rows) // 2
    gone = set(rows[mid - drop // 2: mid - drop // 2 + drop]) if drop else set()
    keep_rows = [y for y in rows if y not in gone]
    kt = float(p.get("kt", 0))
    n = max(1, len(keep_rows) - 1)
    hx, hy = p["hip"]
    out_t = {}
    for i, y in enumerate(keep_rows):
        for (x, yy), c in th.items():
            if yy == y:
                out_t[(x - tx + hx + rnd(kt * i / n), hy + i)] = c
    if p.get("tr"):                                   # the thigh turned about its top middle
        x0, y0 = min(x for x, _ in out_t), min(y for _, y in out_t)
        arr = np.zeros((max(y for _, y in out_t) - y0 + 1, max(x for x, _ in out_t) - x0 + 1, 4), np.uint8)
        for (x, y), c in out_t.items():
            arr[y - y0, x - x0] = c
        rot, (jx, jy) = rotsprite(arr, (hx - x0, hy - y0), float(p["tr"]))
        out_t = {(hx + xx - jx, hy + yy - jy): rot[yy, xx] for yy, xx in zip(*np.nonzero(rot[..., 3]))}
    yb = max(y for _, y in out_t)
    xs = [x for (x, y) in out_t if y == yb]
    kx = (min(xs) + max(xs)) // 2
    lw = {((-dx, r) if p.get("flip") else (dx, r)): c for (dx, r), c in lower.items()}
    mode, ks = p.get("mode", "down"), float(p.get("ks", 0))
    if p.get("ground") and mode != "rot":             # the sole on the soles row: plain shin rows in or out
        need = 11 - (yb + 1 + max(r for _, r in lw))
        if need > 0:
            plain = {dx: c for (dx, r), c in lw.items() if r == 1}
            lw = {(dx, r + (need if r > 1 else 0)): c for (dx, r), c in lw.items()}
            lw.update({(dx, 1 + i): c for dx, c in plain.items() for i in range(1, need + 1)})
        elif need < 0:
            gone = [1, 3, 2][:min(3, -need)]
            remap = {r: i for i, r in enumerate(r for r in sorted({r for _, r in lw}) if r not in gone)}
            lw = {(dx, remap[r]): c for (dx, r), c in lw.items() if r in remap}
    out = {}
    if mode == "rot":
        x0, y0 = min(dx for dx, _ in lw), min(r for _, r in lw)
        arr = np.zeros((max(r for _, r in lw) - y0 + 1, max(dx for dx, _ in lw) - x0 + 1, 4), np.uint8)
        for (dx, r), c in lw.items():
            arr[r - y0, dx - x0] = c
        rot, (jx, jy) = rotsprite(arr, (-x0, 0), ks)
        for yy, xx in zip(*np.nonzero(rot[..., 3])):
            out[(kx + xx - jx, yb + 1 + yy - jy)] = rot[yy, xx]
    elif mode == "bend":
        nb = max(1, max(r for _, r in lw) - 3)
        for (dx, r), c in lw.items():
            out[(kx + dx + rnd(ks * min(r, nb) / nb), yb + 1 + r)] = c
    else:
        nr = max(r for _, r in lw)
        for (dx, r), c in lw.items():
            out[(kx + dx + rnd(ks * r / nr), yb + 1 + r)] = c
    out.update(out_t)
    return out


def legs_onto(frame, pivot, params, idle):
    """The frame's legs replaced by the idle's, posed (POSED_LEGS)."""
    px, py = pivot
    lower = run_lower(idle)
    belt = int(params["belt"])
    c0, c1 = params.get("clear", [-16, 16])
    kept = frame.copy()
    keep = np.zeros(frame.shape[:2], bool)
    keep[:py + belt + 1] = True
    for x0, y0, x1, y1 in params.get("keep", []):
        keep[py + y0:py + y1 + 1, px + x0:px + x1 + 1] = True
    clear = np.zeros(frame.shape[:2], bool)
    clear[py + belt + 1:, px + c0:px + c1 + 1] = True
    kept[clear & ~keep] = 0
    out = np.zeros_like(frame)
    for leg in ("far", "near"):
        p = params.get(leg)
        if not p or p.get("hide"):
            continue
        for (x, y), c in posed_leg(idle, lower, leg, p).items():
            X, Y = px + x, py + y
            if 0 <= Y <= py + 11 and 0 <= X < out.shape[1]:
                out[Y, X] = c
    m = kept[..., 3] > 0
    out[m] = kept[m]
    return out


def build():
    cells = json.load(open(lp(os.path.join(NAT, "kaisa_cells.json")), encoding="utf-8"))
    cell = tuple(cells["cell"][:2])
    out = {}
    run = cells["tags"]["run"]
    idles = [even_legs(f) for f in cells_of(os.path.join(NAT, "kaisa_idle.png"), len(cells["tags"]["idle"]), cell)]
    if tuple(cells["tags"]["idle"][0]["pivot"]) != IDLE_PIVOT:
        sys.exit("the idle's pivot moved: IDLE_PIVOT")
    out["idle"] = (idles, cells["tags"]["idle"])
    idle = idles[0]
    out["run"] = ([run_frame(idle, k, tuple(r["pivot"])) for k, r in enumerate(run)], run)
    w = cells["tags"]["skill2"]
    src = cells_of(os.path.join(SRC, "kaisa_skill2.png"), len(w), cell)
    out["skill2"] = (src, w)
    for tag in ("attack", "skill", "hit"):
        rows = cells["tags"][tag]
        out[tag] = (cells_of(os.path.join(SRC, f"kaisa_{tag}.png"), len(rows), cell), rows)
    out["ult_land"] = (cells_of(os.path.join(SRC, "kaisa_ult_land.png"), len(cells["tags"]["ult_land"]), cell),
                       cells["tags"]["ult_land"])
    for tag, ks in EVEN_FRAMES.items():
        frames, rows = out[tag]
        for k in ks:
            frames[k] = even_frame(frames[k], tuple(rows[k]["pivot"]))
    for tag, ks in IDLE_BODY.items():
        frames, rows = out[tag]
        for k in ks:
            frames[k] = on_idle_body(frames[k], tuple(rows[k]["pivot"]), idle)
    for tag, ks in IDLE_LEGS.items():
        frames, rows = out[tag]
        for k in ks:
            frames[k] = on_idle_legs(frames[k], tuple(rows[k]["pivot"]), idle)
    # R's strip as Codex delivered it (4 frames) is split into ult (1-3) and ult_dash (4) by work/ks/prep_strips.py's
    # layout: the fixed launch frames go to kaisa_ult.png, the dash frame to kaisa_ult_dash.png
    u = cells["tags"]["ult"] + cells["tags"]["ult_dash"]
    src = cells_of(os.path.join(SRC, "kaisa_ult.png"), 4, cell)
    fixed = [r_frame(f, tuple(r["pivot"]), k) for k, (f, r) in enumerate(zip(src, u))]
    out["ult"] = (fixed[:3], cells["tags"]["ult"])
    out["ult_dash"] = (fixed[3:], cells["tags"]["ult_dash"])
    out["dead"] = (cells_of(os.path.join(SRC, "kaisa_dead.png"), len(cells["tags"]["dead"]), cell),
                   cells["tags"]["dead"])
    for (tag, k), params in POSED_LEGS.items():
        frames, rows = out[tag]
        frames[k] = legs_onto(frames[k], tuple(rows[k]["pivot"]), params, idle)
    return out, cell


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview", help="write run_fix.png (every frame at 8x) there")
    a = ap.parse_args()
    built, cell = build()
    for tag, (frames, rows) in built.items():
        path = os.path.join(NAT, f"kaisa_{tag}.png")
        big = sheet_of(frames, cell)
        if a.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA"))
            print(tag, "identical" if old.shape == big.shape and (old == big).all() else "DIFFERENT")
            continue
        Image.fromarray(big, "RGBA").save(lp(path))
        print(path, big.shape[1], "x", big.shape[0])
        if a.preview:
            os.makedirs(a.preview, exist_ok=True)
            tiles = []
            for f, r in zip(frames, rows):
                px, py = r["pivot"]
                c = f[py - 40:py + 14, px - 26:px + 26]
                t = Image.new("RGBA", (c.shape[1], c.shape[0]), (150, 170, 120, 255))
                t.alpha_composite(Image.fromarray(c, "RGBA"))
                tiles.append(t)
            w, h = tiles[0].size
            strip = Image.new("RGBA", (w * 4, h * 2), (150, 170, 120, 255))
            for k, t in enumerate(tiles):
                strip.paste(t, ((k % 4) * w, (k // 4) * h))
            strip.resize((strip.width * 8, strip.height * 8), Image.NEAREST).save(os.path.join(a.preview, f"{tag}_fix.png"))
            gif = [t.resize((w * 4, h * 4), Image.NEAREST).convert("RGB") for t in tiles]
            gif[0].save(os.path.join(a.preview, f"{tag}_fix.gif"), save_all=True, append_images=gif[1:],
                        duration=[r["ms"] for r in rows], loop=0)


if __name__ == "__main__":
    main()

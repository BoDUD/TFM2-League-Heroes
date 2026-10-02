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
- R 3: Codex's back leg, pushed off 25 squares behind her, redrawn in the idle's leg materials, as long and as thick
  as the idle's leg (the user: "放技能的时候注意如果腿不一致也要调整");
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
kaisa_ult.png and kaisa_ult_dash.png (8x, the cells of
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
from native_refs import Z, layout  # noqa: E402

NAT = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "kaisa", "codex_strips")


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


INK = rgb("160722")                       # the outline
INK2 = rgb("1E0A2A")                      # the second near-black
DARK = {INK, INK2}
# the idle's leg materials
PLATE, LIT, SHADE = rgb("352657"), rgb("463970"), rgb("2A1F46")
GOLD, GOLD_L = rgb("D7A965"), rgb("F7D896")
BOOT, BOOT_D = rgb("887CBF"), rgb("6D5EA2")
# the idle's pivot; its legs (the one place every standing action and the run take theirs from)
IDLE_PIVOT = (48, 70)
# the idle's two lower legs were one thin, one thick (its A-stance: the screen-left one seen slanting; the user:
# "待机时候腿一粗一细"): the screen-left lower leg (rows 4-11 under the pivot) is the screen-right one mirrored, hung under
# the left thigh's bottom middle and sheared EVEN_FOOT squares at the sole so its boot stands where the old one stood
EVEN_ROWS = (4, 11)
EVEN_FOOT = -3
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
# per frame and leg: (lift rows, thigh shear at the knee, "down" / "fold", lower shear at the sole (fold: the boot's
# rows up and squares back), x shift)
RUN_POSE = [
    {"near": (2, 3, "down", 0, 0), "far": (0, -2, "down", -1, 0)},
    {"near": (0, 2, "down", 0, 0), "far": (1, -3, "down", -2, 0)},
    {"near": (0, 1, "down", 0, 0), "far": (2, -2, "fold", 4, 0)},
    {"near": (0, 1, "down", -1, 0), "far": (3, 0, "down", -1, 0)},
    {"near": (0, 0, "down", -1, 0), "far": (2, 0, "down", 0, 0)},
    {"near": (1, 0, "down", -2, 0), "far": (0, -1, "down", 0, 0)},
    {"near": (2, 1, "fold", 4, 0), "far": (0, -2, "down", 0, 0)},
    {"near": (3, 3, "down", -1, 0), "far": (0, -2, "down", -1, 0)},
]
THIGH, SHIN, FOOT = 3.8, 3.2, 2.8         # widths in game px (the inside, 4 squares like the idle's and the run's legs;
#                                           the outline ring goes round it)
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
# R's launch, frame 3: Codex's back leg pushed off 25 squares behind her: everything in the box cleared (from the
# pivot: the leg alone, under and behind the torso) and the leg redrawn as long as the idle's
R_LEGS = {2: (((-10, 3), (-13, 6), (-16, 9), (-18, 10)), (-27, 3, -11, 12))}
# R's launch (frames 1 and 2): the hair whipping up over her head (League's Spell4_in) was drawn in the hair's darkest
# shade only and read as a black spike: its inside in the hair's mid shade, its left edge lit (box from the pivot)
HAIR_D, HAIR, HAIR_L = rgb("351036"), rgb("4E194C"), rgb("8A387A")
R_HAIR = {0: (-9, -33, -1, -19), 1: (-9, -29, -1, -19)}


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


def seg(p, a, b):
    """(distance from p to segment ab, signed side: + on the left of a->b's direction, t along it)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    cx, cy = ax + t * dx, ay + t * dy
    side = (dx * (p[1] - ay) - dy * (p[0] - ax)) / math.sqrt(L2)
    return math.hypot(p[0] - cx, p[1] - cy), side, t


def draw_leg(pts):
    """{(x, y): rgb} of one leg through hip, knee, ankle, toe. The light falls from the upper front: the side of each
    segment facing up (smaller y) is lit, the other shaded."""
    hip, knee, ankle, toe = pts
    out = {}
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    for y in range(int(min(ys)) - 3, int(max(ys)) + 4):
        for x in range(int(min(xs)) - 3, int(max(xs)) + 4):
            p = (x, y)
            best = None
            for name, a, b, w in (("thigh", hip, knee, THIGH), ("shin", knee, ankle, SHIN), ("foot", ankle, toe, FOOT)):
                d, side, t = seg(p, a, b)
                if d <= w / 2 and (best is None or d < best[1]):
                    best = (name, d, side, t, a, b, w)
            if best is None:
                continue
            name, d, side, t, a, b, w = best
            # which side of the segment faces up: the normal's y; lit if that side is toward smaller y
            dx, dy = b[0] - a[0], b[1] - a[1]
            nx, ny = -dy, dx                       # the left normal (side > 0)
            up_is_left = ny < 0 or (ny == 0 and nx > 0)
            lit = (side > 0) == up_is_left
            edge = d > w / 2 - 1.0
            if name == "foot":
                c = BOOT if (lit or not edge) else BOOT_D
            else:
                c = (LIT if lit else SHADE) if edge else PLATE
            out[p] = c
    # the knee's gold plate and its highlight (no magenta on the legs: the idle has it on the hip plates only), the
    # boot's claw
    kx, ky = int(round(knee[0])), int(round(knee[1]))
    for q, c in (((kx, ky), GOLD), ((kx, ky - 1), GOLD_L)):
        if q in out:
            out[q] = c
    tx = int(round(toe[0] + (toe[0] - ankle[0]) * 0.4))
    ty = int(round(toe[1] + (toe[1] - ankle[1]) * 0.4))
    if (tx, ty) not in out:
        out[(tx, ty)] = BOOT_D
    return out


def ring(px):
    out = set()
    for (x, y) in px:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in px:
                out.add((x + dx, y + dy))
    return out


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
        elif r <= 3:                                  # fold: the knee guard stays under the knee
            out[(kx + dx, yb + 1 + r)] = c
        else:                                         # and the boot goes up and back behind it
            out[(kx + dx - ks, yb + 1 + r - ks)] = c
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
    if k in R_LEGS:
        pts, (x0, y0, x1, y1) = R_LEGS[k]
        a[py + y0:py + y1 + 1, px + x0:px + x1 + 1] = 0
        out = np.zeros_like(a)
        leg = draw_leg(pts)
        for (x, y) in ring(leg):
            if y <= 11:
                out[py + y, px + x] = INK + (255,)
        for (x, y), c in leg.items():
            out[py + y, px + x] = c + (255,)
        m = a[..., 3] > 0
        out[m] = a[m]
        a = drop_specks(out)
    return a


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

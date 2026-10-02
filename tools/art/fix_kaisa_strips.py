#!/usr/bin/env python3
"""Kai'Sa's strips finished after Codex's deliveries: the run rebuilt from her idle, the dark legs of W's crouch and
the far pod of R's launch given their colours.

    python tools/art/fix_kaisa_strips.py [--check] [--preview DIR]

Codex's first strips (assets/source/kaisa/codex_strips, 2026-10-02) drew every swinging leg as a solid block of the
outline colour (#160722) two to four squares thick, a dark stick that read as a tail (run 1-3 and 5-8, W 2 and 6), and
the far pod of R's launch (1-2) as a near-black spike; its run planted one leg for the whole loop (one step a cycle
where League's run_base takes two). The user: "有问题的地方你进行收尾修正就行了" (no fix pack).
- run: four tries went wrong - my legs under Codex's run ("移动时不合格 腿部和身体脱节分离", "不自然"), Codex's redo
  (13 rows of legs under a 6-row torso, the pods half size: "腿这么长？身体去哪了？"), Codex's legs under the idle's
  upper body (wide squatting legs; the user: "有奇怪的地方你在调一下吧 codex太笨了"). Built here the way
  tools/art/fix_caitlyn_run.py built Caitlyn's run (the user: "挺不错的"): every frame is the idle's frame 1 down to the
  hip plates (rows to 2 under the pivot, and the arms' tips: head, pods, torso, arms as one block), lowered by League's
  step (DY: 0, 1, 2, 1, 0, 1, 2, 1 - the pelvis lowest as each leg passes under her), over two legs drawn square by
  square on Caitlyn's leg poses (League's run joints at game size, about 1.6 times League's swing): in 1-3 the
  screen-left (near) leg is planted under her while the other kicks its heel up behind and swings its knee through,
  5-7 the other way round, 4 and 8 the landings. The legs are the idle's: 4 squares wide with the shaded and lit plate
  edges, the gold knee, the lavender boot, 9 rows from the hip plates to the soles; one outline ring each, the near
  leg's over the far one;
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
Writes assets/source/native/kaisa_run.png, kaisa_attack.png, kaisa_skill.png, kaisa_skill2.png, kaisa_hit.png,
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
# the run: the idle's rows down to the hip plates (2 under the pivot) and its arms' tips, lowered by League's step
IDLE_PIVOT = (48, 70)
HIP_ROW = 2
ARM_TIPS = [(-12, 3), (12, 3), (13, 3)]
DY = [0, 1, 2, 1, 0, 1, 2, 1]
LEG_MAT = {"s": SHADE, "p": PLATE, "l": LIT, "g": GOLD, "G": GOLD_L, "b": BOOT, "c": BOOT_D}
LEG_X0 = -8                               # column 0 of every leg grid, from the pivot; rows 3..10 under it
# each frame: (far leg, near leg); "." empty. The far leg's hip is the right half of the plates, the near one's the left
RUN_LEGS = [
    # 1: the near leg planted under her, the far one bent up behind it
    (["........sppl......",
      ".......sppl.......",
      "......sppl........",
      "...sgGppl.........",
      "..cbbbb...........",
      "..cbb.............",
      "..................",
      ".................."],
     [".....sppl.........",
      ".....sppl.........",
      "......sgGl........",
      "......sppl........",
      "......sppl........",
      "......sppl........",
      "......cbbbb.......",
      "......cbbbbb......"]),
    # 2: planted; the far heel kicked up behind
    (["........sppl......",
      "........sppl......",
      "...sgGppppl.......",
      "..cbbbbb..........",
      "..cbb.............",
      "..................",
      "..................",
      ".................."],
     [".....sppl.........",
      ".....sppl.........",
      ".....sppl.........",
      "......sgGl........",
      "......sppl........",
      "......sppl........",
      "......cbbbb.......",
      "......cbbbbb......"]),
    # 3: lowest; the far knee swings through in front, its foot tucked under
    (["........sppl......",
      "........sppl......",
      ".........sppl.....",
      "......sgGpppl.....",
      "......cbbbbb......",
      ".......cbbb.......",
      "..................",
      ".................."],
     [".....sppl.........",
      ".....sppl.........",
      ".....sppl.........",
      ".....sppl.........",
      ".....sgGl.........",
      ".....sppl.........",
      ".....cbbbb........",
      ".....cbbbbb......."]),
    # 4: the far foot lands in front, the near leg pushes off behind
    (["........sppl......",
      "........sppl......",
      ".........sppl.....",
      ".........sgGl.....",
      ".........sppl.....",
      ".........sppl.....",
      ".........cbbbb....",
      ".........cbbbbb..."],
     [".....sppl.........",
      "....sppl..........",
      "....sppl..........",
      "...sgGl...........",
      "...sppl...........",
      "..sppl............",
      "..cbbb............",
      ".cbbb............."]),
    # 5: the far leg planted, the near one bent up behind
    (["........sppl......",
      "........sppl......",
      "........sppl......",
      ".........sgGl.....",
      ".........sppl.....",
      ".........sppl.....",
      ".........cbbbb....",
      ".........cbbbbb..."],
     [".....sppl.........",
      "....sppl..........",
      "...spppl..........",
      "..sgGppl..........",
      ".cbbbb............",
      ".cbb..............",
      "..................",
      ".................."]),
    # 6: planted; the near heel kicked up behind
    (["........sppl......",
      "........sppl......",
      "........sppl......",
      ".........sgGl.....",
      ".........sppl.....",
      ".........sppl.....",
      ".........cbbbb....",
      ".........cbbbbb..."],
     [".....sppl.........",
      ".....sppl.........",
      "..sgGppppl........",
      ".cbbbbb...........",
      ".cbb..............",
      "..................",
      "..................",
      ".................."]),
    # 7: lowest; the near knee swings through, its foot tucked under
    (["........sppl......",
      "........sppl......",
      "........sppl......",
      "........sppl......",
      "........sgGl......",
      "........sppl......",
      "........cbbbb.....",
      "........cbbbbb...."],
     [".....sppl.........",
      ".....sppl.........",
      "......sppl........",
      "...sgGpppl........",
      "...cbbbbb.........",
      "....cbbb..........",
      "..................",
      ".................."]),
    # 8: the near foot lands in front, the far leg pushes off behind it
    (["........sppl......",
      ".......sppl.......",
      ".......sppl.......",
      "......sgGl........",
      "......sppl........",
      ".....sppl.........",
      ".....cbbb.........",
      "....cbbb.........."],
     [".....sppl.........",
      ".....sppl.........",
      "......sppl........",
      "......sgGl........",
      "......sppl........",
      "......sppl........",
      "......cbbbb.......",
      "......cbbbbb......"]),
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


def leg_pixels(grid):
    """{(x, y): rgb} of one leg grid, from the pivot."""
    return {(LEG_X0 + c, 3 + r): LEG_MAT[ch] for r, row in enumerate(grid) for c, ch in enumerate(row) if ch != "."}


def leg_ring(px):
    """The 4-neighbour ring of a leg, plus the corners under its soles (tools/art/fix_caitlyn_run.py)."""
    out = set()
    for (x, y) in px:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in px:
                out.add((x + dx, y + dy))
        if (x, y + 1) not in px:
            for dx in (-1, 1):
                if (x + dx, y + 1) not in px and (x + dx, y) not in px:
                    out.add((x + dx, y + 1))
    return out


def run_frame(idle, k, pivot):
    """Run frame k on its cell: the legs, then the idle's upper body lowered by DY[k]; standing on `pivot`."""
    out = np.zeros_like(idle)
    ix, iy = IDLE_PIVOT
    for grid in RUN_LEGS[k]:
        px = leg_pixels(grid)
        for (x, y) in leg_ring(px):
            if y <= 11:
                out[iy + y, ix + x] = INK + (255,)
        for (x, y), c in px.items():
            out[iy + y, ix + x] = c + (255,)
    up = idle.copy()
    keep = np.zeros(up.shape[:2], bool)
    keep[:iy + HIP_ROW + 1] = True
    for x, y in ARM_TIPS:
        keep[iy + y, ix + x] = True
    up[~keep] = 0
    up = np.roll(up, DY[k], 0)
    m = up[..., 3] > 0
    out[m] = up[m]
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
    idle = cells_of(os.path.join(NAT, "kaisa_idle.png"), len(cells["tags"]["idle"]), cell)[0]
    if tuple(cells["tags"]["idle"][0]["pivot"]) != IDLE_PIVOT:
        sys.exit("the idle's pivot moved: IDLE_PIVOT")
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

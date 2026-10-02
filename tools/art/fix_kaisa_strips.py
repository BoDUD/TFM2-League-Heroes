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
- W 2 and 6: the back leg Codex drew as a dark block, redrawn on its own line in the idle's leg materials, as long
  and as thick as the idle's leg (the user: "放技能的时候注意如果腿不一致也要调整"); R 3: Codex's back leg, pushed off
  25 squares behind her, redrawn the same way;
- R 1 and 2: the dark hair spike's inside in the hair's mid shade, its left edge lit.
Writes assets/source/native/kaisa_run.png, kaisa_skill2.png, kaisa_ult.png and kaisa_ult_dash.png (8x, the cells of
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
# W's crouch (frames 2 and 6): the back leg Codex drew as a dark block, redrawn on its own line behind the body (hip,
# knee, ankle, toe from the pivot; the block cleared first: dark squares in the box). Its first redraw followed the
# block to 21-22 squares behind the hip, twice the idle's leg; the user: "放技能的时候注意如果腿不一致也要调整" - now
# hip to ankle as long as the idle's leg (about 8), the foot on the soles' row
W_LEGS = {1: (((-9, 1), (-12, 4), (-15, 8), (-17, 10)), (-23, 1, -9, 11)),
          5: (((-10, 1), (-13, 4), (-16, 8), (-18, 10)), (-24, 1, -10, 11))}
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


def w_frame(frame, pivot, k):
    if k not in W_LEGS:
        return frame
    px, py = pivot
    pts, (x0, y0, x1, y1) = W_LEGS[k]
    a = frame.copy()
    for y in range(py + y0, py + y1 + 1):
        for x in range(px + x0, px + x1 + 1):
            if a[y, x, 3] and colour(a, y, x) in DARK:
                a[y, x] = 0
    out = np.zeros_like(frame)
    leg = draw_leg(pts)
    for (x, y) in ring(leg):
        if y <= 11:
            out[py + y, px + x] = INK + (255,)
    for (x, y), c in leg.items():
        out[py + y, px + x] = c + (255,)
    m = a[..., 3] > 0
    out[m] = a[m]
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
    out["skill2"] = ([w_frame(f, tuple(r["pivot"]), k) for k, (f, r) in enumerate(zip(src, w))], w)
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

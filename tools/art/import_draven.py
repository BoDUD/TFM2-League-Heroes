#!/usr/bin/env python3
"""Import Draven's effects (assets/source/draven/PROMPTS_FX.md, 19 sheets) as the game sheets league_draven_fx and
league_draven_big.

    python tools/art/import_draven.py

Codex delivered every effect at the pack's layout (16 px a game pixel) and, in codex_fx/1x/, one pixel a game pixel,
already snapped to the pack's ramps with binary alpha (its HANDOFF: only grid sampling, the ramps, alpha - nothing
moved or scaled). The 1x strips are read as they are: n equal cells in a row, each cell the size the pack asked for, so
no scaling. The thrown axe of the attack is the design's own near axe instead (Codex's a_axe broke into specks at 14
px): cut from assets/source/native/draven_native.png and turned by quarter turns (lossless), the same axe he holds.
Anchors (cell px, from the pack's layout lines): the flying ones on their middle, the hits on their middle, the ground
pictures on their ground point, the auras on the feet line they were drawn over, the axe icons above the head.
Each cell is placed by its anchor on a spot from the pivot (game px, x right, y down; the soles 10.5 under the pivot,
as import_native.py centres his frames) and timed by the kit (tools/kit/build_draven.py, 60 ticks a second).
The red side: the client never mirrors a data picture and turns a projectile's picture with its flight (a leftward
axe turns upside down, still an axe), so the axes are not folded over their flip (an axe drawn over its own flip would
be two crossed axes); the bursts on him that lint_mod found lopsided (SYMMETRIC: Codex's sparks were not mirrored) are
drawn over their own left-right flip.
Writes league/effects/league_draven_fx and league_draven_big.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import import_xayah as X  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "draven", "codex_fx", "1x")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "draven_native.png")
MOD = os.path.join(ROOT, "league")

# name: frames, anchor in the cell ("mid" or (x, y) in cell px)
CELLS = {
    "a_hit": (4, "mid"), "q_axe": (4, "mid"), "q_hit": (5, (8, 32)), "q_zone": (7, "mid"), "q_fall": (7, (7, 63)),
    "q_catch": (4, (12, 24)), "q_lost": (5, (8, 16)), "ax1": (4, "mid"), "ax2": (4, "mid"), "w_cast": (5, (20, 37)),
    "w_ms": (4, (16, 8)), "e_axes": (4, "mid"), "e_hit": (4, "mid"), "e_slow": (4, "mid"), "r_axes": (4, "mid"),
    "r_hit": (5, "mid"), "p_cash": (6, (16, 42)), "p_6": (4, (15, 38)),
}
# spots from the pivot (game px, x right, y down)
HIT = (0, -12)              # a hit on the upper body of a 36-44 px unit
FEET = (0, 10)              # the ground under a unit (his soles are 10.5 under the pivot); a point on the ground
CENTRE = (0, 0)             # a projectile (centred on itself)
HEAD = (0, -37)             # over his head (the crest is 40 rows over the soles)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
# the design's near axe (canvas rows, columns), without the fist that holds it (rows 79-83, columns 78-82)
AXE_BOX = ((72, 93), (77, 91))
FIST = ((79, 83), (77, 82))


def loop(n, ms):
    return seq(range(n), [ms] * n)


def strip(name):
    n, anchor = CELLS[name]
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"draven_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] >= 128, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"draven_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    cells = [a[:, k * w:(k + 1) * w] for k in range(n)]
    anc = (w / 2 - 0.5, a.shape[0] / 2 - 0.5) if anchor == "mid" else anchor
    return cells, anc


def axe_frames():
    """The design's near axe turned 0, 90, 180, 270 degrees (clockwise on screen), each centred in a square cell."""
    d = np.asarray(Image.open(G.lp(DESIGN)).convert("RGBA"))[4::8, 4::8].copy()
    (r0, r1), (c0, c1) = AXE_BOX
    (f0, f1), (g0, g1) = FIST
    a = d[r0:r1 + 1, c0:c1 + 1].copy()
    a[f0 - r0:f1 - r0 + 1, g0 - c0:g1 - c0 + 1] = 0
    # the axe alone: the biggest 8-connected piece (drops the forearm's and the leg's squares the box catches)
    from scipy import ndimage
    lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    big = 1 + int(np.argmax([(lab == i).sum() for i in range(1, n + 1)]))
    a[lab != big] = 0
    ys, xs = np.nonzero(a[..., 3])
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    S = max(a.shape[:2]) + 2
    out = []
    for q in range(4):
        t = np.rot90(a, -q)                   # clockwise
        c = np.zeros((S, S, 4), np.uint8)
        y0, x0 = (S - t.shape[0]) // 2, (S - t.shape[1]) // 2
        c[y0:y0 + t.shape[0], x0:x0 + t.shape[1]] = t
        out.append(c)
    return out, (S / 2 - 0.5, S / 2 - 0.5)


SYMMETRIC = {"w_cast", "q_catch"}


def frames(name, order, spots):
    if name == "a_axe":
        cells, anc = axe_frames()
    else:
        cells, anc = strip(name)
    out = []
    for k, ms in order:
        if k == EMPTY:
            out.append((np.zeros((3, 3, 4), np.uint8), ms))
        else:
            f = J.place(cells[k], anc, spots)
            out.append((X.over_flip(f, "lr") if name in SYMMETRIC else f, ms))
    return out


FX = {
    # the flying ones: the axes 6000 a tick for ~55000 (9 ticks) - homing; the spinning one the same; E's pair 6000 for
    # 105000 (18 ticks)
    "a_axe": ("a_axe", flight(4, 50, 400), [CENTRE]),
    "q_axe": ("q_axe", flight(4, 50, 400), [CENTRE]),
    "e_axes": ("e_axes", flight(4, 60, 700), [CENTRE]),
    # the hits
    "a_hit": ("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_hit": ("q_hit", seq(range(5), [40, 60, 70, 80, 100]), [HIT]),
    "e_hit": ("e_hit", seq(range(4), [40, 50, 60, 80]), [HIT]),
    "r_hit": ("r_hit", seq(range(5), [40, 50, 60, 80, 100]), [HIT]),
    # Spinning Axe: the catch circle and the axe falling into it play together for the lob's 42 ticks (700 ms)
    "q_zone": ("q_zone", seq(range(7), [100] * 7), [FEET]),
    "q_fall": ("q_fall", seq(range(7), [100] * 7), [FEET]),
    "q_catch": ("q_catch", seq(range(4), [40, 60, 70, 80]), [FEET]),
    "q_lost": ("q_lost", seq(range(5), [80, 100, 120, 150, 150]), [FEET]),
    "w_cast": ("w_cast", seq(range(5), [50, 60, 70, 80, 100]), [FEET]),
    "p_cash": ("p_cash", seq(range(6), [60, 80, 100, 120, 150, 180]), [FEET]),
    # the buffs' loops
    "ax1": ("ax1", loop(4, 80), [HEAD]),
    "ax2": ("ax2", loop(4, 80), [HEAD]),
    "w_ms": ("w_ms", loop(4, 80), [FEET]),
    "e_slow": ("e_slow", loop(4, 110), [FEET]),
    "p_6": ("p_6", loop(4, 150), [FEET]),
}
BIG = {
    # the ult's blades: 4500 a tick out to 200000 (45 ticks) and back at 5000 - looped while they fly
    "r_axes": ("r_axes", loop(4, 60), [CENTRE]),
}


def main():
    for sheet, table in (("league_draven_fx", FX), ("league_draven_big", BIG)):
        tags = {tag: frames(src, order, spots) for tag, (src, order, spots) in table.items()}
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

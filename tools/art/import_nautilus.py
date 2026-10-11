#!/usr/bin/env python3
"""Import Nautilus's effects (assets/source/nautilus/PROMPTS_FX.md, 17 sheets) as the game sheets league_nautilus_fx and
league_nautilus_big.

    python tools/art/import_nautilus.py

Codex delivered every sheet at game size as well (assets/source/nautilus/codex_fx/nautilus-fx/pixel_1x/, one game
pixel a square, a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out,
given its anchor and placed on its spot (tools/art/import_viego.py's way).

Red side and blue side alike: the client mirrors his own frames with his facing and never an effect picture, so Codex
drew (and check() asserts) the flying pictures symmetric top to bottom (the anchor and the shockwave: cast leftward
the engine turns them upside down), every picture on a unit and the buffs symmetric left to right, the ground waves
both ways. Nothing rides in his action frames. Spots are game px from the pivot (x forward, y down); a unit's soles
are 11 under it. Times from the kit (build_nautilus.P, 60 ticks a second).
"""
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

SRC = os.path.join(ROOT, "assets", "source", "nautilus", "codex_fx", "nautilus-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the figure's place the
# pack left empty; "tip": the front, a column in from the right), symmetry asserted
SHEETS = {
    "a_hit": (4, "core", "lr"), "p_hit": (5, ("feet", 0), "lr"), "p_root": (4, "core", "lr"),
    "q_anchor": (4, "tip", "tb"), "q_hit": (4, "core", "lr"), "w_on": (4, ("feet", 1), "lr"), "w_hit": (4, "core", "lr"),
    "e_wave1": (5, "core", "lr tb"), "e_wave2": (5, "core", "lr tb"), "e_wave3": (5, "core", "lr tb"),
    "e_hit": (4, "core", "lr"), "e_slow": (4, "core", "lr"), "r_cast": (5, ("feet", 0), "lr"),
    "r_wave": (4, "tip", "tb"), "r_up": (4, ("feet", 0), "lr"), "r_hit": (6, ("feet", 0), "lr"),
    "r_stun": (4, "core", "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -32)                 # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the anchor: a line at 6 px a tick over 85 px (14 ticks)
    "q_anchor": [("q_anchor", flight(4, 60, 480), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_hit": [("p_hit", seq(range(5), [40, 50, 60, 70, 80]), [SOLES])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [50, 60, 70, 80]), [SOLES])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_up": [("r_up", seq(range(4), [50, 60, 70, 80]), [SOLES])],
    # on him as he slams for R
    "r_cast": [("r_cast", seq(range(5), [40, 50, 60, 70, 80]), [SOLES])],
    # buffs (looped while they last): the root 50 ticks, the slow 75, R's stun 45, the shield 6 s
    "p_root": [("p_root", seq(range(4), [100] * 4), [SOLES])],
    "e_slow": [("e_slow", seq(range(4), [100] * 4), [SOLES])],
    "r_stun": [("r_stun", seq(range(4), [100] * 4), [OVER])],
    "w_on": [("w_on", seq(range(4), [110] * 4), [SOLES])],
}
BIG = {
    # the shockwave homes on its champion at 2.5 px a tick over at most 80 px (32 ticks): 2 empty ticks first
    "r_wave": [("r_wave", flight(4, 70, 1100, lead=2), [(0, 0)])],
    # Riptide's three waves round his feet, 5 ticks apart (build_nautilus e_gap)
    "e_wave1": [("e_wave1", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
    "e_wave2": [("e_wave2", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
    "e_wave3": [("e_wave3", seq(range(5), [50, 60, 70, 80, 100]), [SOLES])],
    # R's eruption on its champion (its soles)
    "r_hit": [("r_hit", seq(range(6), [40, 50, 60, 70, 80, 100]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"nautilus_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"nautilus_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "tip":
        return [w - 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def check(name, strip, sym):
    """The red side's symmetry, cell by cell (the effect picture is never mirrored by the client)."""
    for k, c in enumerate(strip):
        if "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"nautilus_fx_{name} cell {k + 1} is not symmetric left to right")
        if "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"nautilus_fx_{name} cell {k + 1} is not symmetric top to bottom")


def build(table):
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            n, kind, sym = SHEETS[src]
            strip = cells(src, n)
            check(src, strip, sym)
            anc = anchor(strip[0], kind)
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                out[tag].append((J.place(strip[k], anc, spots), ms))
    return out


def main():
    used = {src for table in (FX, BIG) for parts in table.values() for src, _, _ in parts}
    if used != set(SHEETS):
        sys.exit(f"sheets not imported: {sorted(set(SHEETS) - used)}")
    for sheet, table in (("league_nautilus_fx", FX), ("league_nautilus_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

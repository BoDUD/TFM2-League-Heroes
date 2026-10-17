#!/usr/bin/env python3
"""Import Lillia's effects (assets/source/lillia/PROMPTS_FX.md, 17 sheets) as the game sheets league_lillia_fx and
league_lillia_big.

    python tools/art/import_lillia.py

Codex delivered every sheet at game size as well (assets/source/lillia/codex_fx/lillia-fx/pixel_1x/, one game pixel a
square, a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its
anchor and placed on its spot (tools/art/import_seraphine.py's way).

Red side and blue side alike: the client mirrors her own frames with her facing and never an effect picture, so Codex
drew (and check() asserts) the seed symmetric top to bottom (lobbed leftward the engine turns it upside down), every
picture on a unit, the buffs and what plays on her (q_spin at the action's first tick, r_cast late) symmetric left to
right, the ground pictures (q_spin, e_land, w_mark, w_land) both ways. Nothing rides in her action frames: the bough
throws the seed, the rest is round her or on the targets.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it (her hooves too), her bud's top 34
over it. Times from the kit (build_lillia.P, 60 ticks a second) and the strips.
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

SRC = os.path.join(ROOT, "assets", "source", "lillia", "codex_fx", "lillia-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the figure's place the
# pack left empty, or the ground glow on the bottom), symmetry asserted
SHEETS = {
    "a_hit": (4, "core", "lr"), "q_spin": (6, "core", "lr tb"), "q_hit": (4, "core", "lr"),
    "e_seed": (4, "core", "tb"), "e_land": (5, "core", "lr tb"), "e_hit": (4, "core", "lr"), "e_slow": (4, "core", "lr"),
    "w_mark": (6, "core", "lr tb"), "w_land": (6, "core", "lr tb"), "w_hit": (4, "core", "lr"),
    "w_sweet": (5, "core", "lr"), "r_cast": (6, ("feet", 0), "lr"), "drowsy": (4, "core", "lr"),
    "sleep": (4, "core", "lr"), "wake": (5, "core", "lr"), "dust": (4, ("feet", 0), "lr"),
    "prance": (4, ("feet", 0), "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-46 px unit
OVER = (0, -31)                 # over a unit's head (the haze, the sleep bubble)
SOLES = (0, 11)                 # on the ground under a unit (her hooves, or a lob's landing point)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the swirlseed: a 20-tick lob (e_travel); one empty tick so it shows past the bough's tip
    "e_seed": [("e_seed", flight(4, 70, 400, lead=1), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_sweet": [("w_sweet", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "wake": [("wake", seq(range(5), [40, 50, 60, 80, 90]), [HIT])],
    # the seed bursting where it lands, under the units
    "e_land": [("e_land", seq(range(5), [40, 50, 60, 70, 80]), [SOLES])],
    # buffs (looped while they last)
    "e_slow": [("e_slow", seq(range(4), [100] * 4), [SOLES])],
    "drowsy": [("drowsy", seq(range(4), [120] * 4), [OVER])],
    "sleep": [("sleep", seq(range(4), [130] * 4), [OVER])],
    "dust": [("dust", seq(range(4), [110] * 4), [SOLES])],
    "prance": [("prance", seq(range(4), [90] * 4), [SOLES])],
}
BIG = {
    # Q's ring opens round her feet as she spins (the hit at q_st 7 ticks = 117 ms: frame 3, the widest)
    "q_spin": [("q_spin", seq(range(6), [40, 50, 60, 70, 80, 90]), [SOLES])],
    # W's warning ring for the w_wind 30 ticks (500 ms) the strike takes to land, then the slam
    "w_mark": [("w_mark", seq(range(6), [80, 80, 80, 80, 90, 90]), [SOLES])],
    "w_land": [("w_land", seq(range(6), [40, 50, 60, 70, 80, 90]), [SOLES])],
    "r_cast": [("r_cast", seq(range(6), [60, 80, 100, 100, 110, 120]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"lillia_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"lillia_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def check(name, strip, sym):
    """The red side's symmetry, cell by cell (the effect picture is never mirrored by the client)."""
    for k, c in enumerate(strip):
        if "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"lillia_fx_{name} cell {k + 1} is not symmetric left to right")
        if "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"lillia_fx_{name} cell {k + 1} is not symmetric top to bottom")


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
    for sheet, table in (("league_lillia_fx", FX), ("league_lillia_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

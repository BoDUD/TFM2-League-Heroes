#!/usr/bin/env python3
"""Import Irelia's effects (assets/source/irelia/PROMPTS_FX.md, 18 sheets) as the game sheets league_irelia_fx and
league_irelia_big.

    python tools/art/import_irelia.py

Codex delivered every sheet at game size as well (assets/source/irelia/codex_fx/irelia-fx/pixel_1x/, one game pixel a
square, a row of equal cells), so nothing is resampled here: each cell is cut out, given its anchor and placed on its
spot (tools/art/import_zeri.py's way).

Red side and blue side alike: the client mirrors her own frames with her facing and never an effect picture, so the
two lines (e_line, w_line) and the flying volley (r_blades) are symmetric top to bottom (cast leftward the engine turns
them upside down) and everything on a unit, at her feet or on the ground symmetric left to right (check() asserts it).
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. A line's picture (a
LineRangeProjectile's view, champion-data "Cone / fan") is centred on the line's middle and spans it, so its cell is
anchored at its centre: the left edge on her, the right edge at the line's end (e_len 80, w_len 55 px). Times from the
kit (tools/kit/build_irelia.py P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "irelia", "codex_fx", "irelia-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): that row's middle on the
# spot; "tip": the front, a column in from the right), symmetry asserted
SHEETS = {
    "a_hit": (4, "core", "lr"), "p_hit": (4, "core", "lr"), "pv4": (4, ("feet", 0), "lr"),
    "q_hit": (5, "core", "lr"), "mark": (4, ("feet", 0), "lr"),
    "e_cast": (5, ("feet", 4), "lr"), "e_line": (6, "core", "tb"), "e_hit": (4, "core", "lr"),
    "e_stun": (4, ("feet", 0), "lr"),
    "w_on": (4, ("feet", 0), "lr"), "w_slash": (5, ("feet", 0), "lr"), "w_line": (5, "core", "tb"),
    "w_hit": (4, "core", "lr"),
    "r_blades": (4, "tip", "tb"), "r_hit": (5, "core", "lr"), "r_wall_v": (10, ("feet", 16), "lr"),
    "r_slow": (4, ("feet", 3), "lr"), "r_wslow": (4, ("feet", 3), "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
SOLES = (0, 11)                 # on the ground under a unit
seq = J.seq
flight = J.flight

FX = {
    # hits on the target
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_hit": [("p_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    # E's first blade at her feet (the cast's first ticks)
    "e_cast": [("e_cast", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
    # the buffs, looped while they last: the full passive, the mark (mark_t 300 ticks), the stun (e_stun 45), W's
    # guard (w_charge 32), the slows (r_slow_t 60; the wall's renewed every r_wper 10)
    "pv4": [("pv4", seq(range(4), [110] * 4), [SOLES])],
    "mark": [("mark", seq(range(4), [120] * 4), [SOLES])],
    "e_stun": [("e_stun", seq(range(4), [90] * 4), [SOLES])],
    "w_on": [("w_on", seq(range(4), [90] * 4), [SOLES])],
    "r_slow": [("r_slow", seq(range(4), [100] * 4), [SOLES])],
    "r_wslow": [("r_wslow", seq(range(4), [110] * 4), [SOLES])],
}
BIG = {
    # E's line: the two blades meet when it strikes (e_rel 18 ticks = 300 ms after it appears, delay 24 = 400 ms)
    "e_line": [("e_line", seq(range(6), [60, 60, 60, 60, 70, 90]), [(0, 0)])],
    # W's slash along the line (w_line_t 16 ticks = 267 ms) and the release burst on her
    "w_line": [("w_line", seq(range(5), [45, 50, 55, 55, 62]), [(0, 0)])],
    "w_slash": [("w_slash", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
    # R's volley: 6 px a tick to 85 px (r_speed, r_range), from her pivot
    "r_blades": [("r_blades", flight(4, 60, 400, lead=1), [(0, 0)])],
    # the blade wall on the ground where the volley stopped, played once over r_wall_t 150 ticks (2.5 s)
    "r_wall_v": [("r_wall_v", seq(range(10), [100, 120, 330, 330, 330, 330, 330, 330, 150, 150]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"irelia_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"irelia_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
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
            sys.exit(f"irelia_fx_{name} cell {k + 1} is not symmetric left to right")
        if "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"irelia_fx_{name} cell {k + 1} is not symmetric top to bottom")


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
                if k == J.EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                out[tag].append((J.place(strip[k], anc, spots), ms))
    return out


def main():
    used = {src for table in (FX, BIG) for parts in table.values() for src, _, _ in parts}
    if used != set(SHEETS):
        sys.exit(f"sheets not imported: {sorted(set(SHEETS) - used)}")
    for sheet, table in (("league_irelia_fx", FX), ("league_irelia_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Import Viktor's effects (assets/source/viktor/PROMPTS_FX.md, 23 sheets) as the game sheets league_viktor_fx and
league_viktor_big.

    python tools/art/import_viktor.py

Codex delivered every sheet at game size as well (assets/source/viktor/codex_fx/viktor-fx/pixel_1x/, one game pixel a
square, a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its
anchor and placed on its spot (tools/art/import_seraphine.py's way).

Red side and blue side alike: the client mirrors his own frames with his facing and never an effect picture, so Codex
drew (and check() asserts) the flying bolts and the ray's line pictures symmetric top to bottom (cast leftward the
engine turns them upside down), every picture on a unit, the buffs and what plays on him late (q_shield, evo) symmetric
left to right, the ground pictures (w_field, w_burst, r_land) both ways. The ray (e_ray, e_after) is a hitless line on
the landing point turned from him to it: its cell's centre goes on the pivot, so the beam reaches on from the target.
Nothing rides in his action frames. Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under
it. Times from the kit (build_viktor.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "viktor", "codex_fx", "viktor-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the figure's place the
# pack left empty; "tip": the front, a column in from the right; "line": the cell's centre, the beam reaching right of
# it), symmetry asserted
SHEETS = {
    "a_bolt": (4, "tip", "tb"), "a_blast": (4, "tip", "tb"), "a_hit": (4, "core", "lr"),
    "a_blast_hit": (5, "core", "lr"), "q_bolt": (4, "tip", "tb"), "q_hit": (4, "core", "lr"),
    "q_shield": (5, ("feet", 1), "lr"), "q_charged": (4, ("feet", 0), "lr"), "q_ms": (4, "core", "lr"),
    "w_field": (10, "core", "lr tb"), "w_burst": (5, "core", "lr tb"), "w_stun": (4, "core", "lr"),
    "w_slow": (4, "core", "lr"), "evo_slow": (4, "core", "lr"), "e_ray": (6, "line", "tb"), "e_after": (6, "line", "tb"),
    "e_hit": (4, "core", "lr"), "e_after_hit": (4, "core", "lr"), "r_land": (6, "core", "lr tb"),
    "r_storm": (6, ("feet", 0), "lr"), "r_storm_big": (6, ("feet", 0), "lr"), "r_hit": (4, ("feet", 0), "lr"),
    "evo": (6, ("feet", 0), "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -30)                 # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

# W's field lasts w_t 240 ticks (4000 ms): it opens (2 frames), pulls in (frames 3-8 looped), fades (2 frames)
FIELD_LOOP = 3640 // 36
FX = {
    # the bolts: 55-60 px at 4.5 / 5 px a tick (bolt_speed 4500, q_speed 5000); 2 empty ticks past his hand
    "a_bolt": [("a_bolt", flight(4, 60, 320, lead=2), [(0, 0)])],
    "a_blast": [("a_blast", flight(4, 60, 320, lead=2), [(0, 0)])],
    "q_bolt": [("q_bolt", flight(4, 60, 320, lead=2), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "a_blast_hit": [("a_blast_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_after_hit": [("e_after_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # R's tick: the bolt strikes down onto the unit's chest
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [(0, -6)])],
    # Q's shield lighting up round him (a 150-tick shield; the flash only)
    "q_shield": [("q_shield", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
    # the stun (w_stun 75 ticks = 1250 ms: the loop three times)
    "w_stun": [("w_stun", seq([k % 4 for k in range(12)], [104] * 12), [OVER])],
    "evo": [("evo", seq(range(6), [60, 70, 80, 90, 100, 120]), [SOLES])],
    # buffs (looped while they last)
    "q_charged": [("q_charged", seq(range(4), [120] * 4), [SOLES])],
    "q_ms": [("q_ms", seq(range(4), [100] * 4), [SOLES])],
    "w_slow": [("w_slow", seq(range(4), [100] * 4), [SOLES])],
    "evo_slow": [("evo_slow", seq(range(4), [100] * 4), [SOLES])],
}
BIG = {
    # the ray and the aftershock: hitless lines of delay 14 ticks (233 ms), the beam full on frame 3 (the hit, tick 8)
    "e_ray": [("e_ray", seq(range(6), [30, 30, 40, 45, 45, 43]), [(0, 0)])],
    "e_after": [("e_after", seq(range(6), [30, 30, 40, 45, 45, 43]), [(0, 0)])],
    # the ground pictures on their points, under the units
    "w_field": [("w_field", seq([0, 1] + [2 + k % 6 for k in range(36)] + [8, 9],
                                [80, 80] + [FIELD_LOOP] * 36 + [100, 100]), [(0, 0)])],
    "w_burst": [("w_burst", seq(range(5), [40, 50, 60, 80, 100]), [(0, 0)])],
    "r_land": [("r_land", seq(range(6), [50, 60, 70, 80, 90, 100]), [(0, 0)])],
    # the storm over its champion, played once a second (six frames, 1000 ms)
    "r_storm": [("r_storm", seq(range(6), [167, 167, 167, 167, 166, 166]), [SOLES])],
    "r_storm_big": [("r_storm_big", seq(range(6), [167, 167, 167, 167, 166, 166]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"viktor_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"viktor_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "line":
        return [w / 2, (h - 1) / 2]
    if kind == "tip":
        return [w - 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def check(name, strip, sym, kind):
    """The red side's symmetry, cell by cell (the effect picture is never mirrored by the client); a line's left half
    empty (it reaches on from the landing point)."""
    for k, c in enumerate(strip):
        if sym and "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"viktor_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym and "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"viktor_fx_{name} cell {k + 1} is not symmetric top to bottom")
        if kind == "line" and c[:, :c.shape[1] // 2, 3].any():
            sys.exit(f"viktor_fx_{name} cell {k + 1} draws left of the landing point")


def build(table):
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            n, kind, sym = SHEETS[src]
            strip = cells(src, n)
            check(src, strip, sym, kind)
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
    for sheet, table in (("league_viktor_fx", FX), ("league_viktor_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

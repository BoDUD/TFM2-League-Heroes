#!/usr/bin/env python3
"""Import Zeri's effects (assets/source/zeri/PROMPTS_FX.md, 24 sheets) as the game sheets league_zeri_fx and
league_zeri_big.

    python tools/art/import_zeri.py

Codex delivers every sheet at game size as well (assets/source/zeri/codex_fx/zeri-fx/pixel_1x/, one game pixel a
square, a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its
anchor and placed on its spot (tools/art/import_syndra.py's way).

Red side and blue side alike: the client mirrors her own frames with her facing and never an effect picture, so the
flying rounds, pulses, the spark and the add-on's wall laser are symmetric top to bottom (cast leftward the engine turns
them upside down), the laser's line picture too (its left half empty: it reaches on from the point the pulse stopped
on), every picture on a unit, the buffs and what plays on her (p_ready, w_cast, e_cast, r_nova, the overcharge)
symmetric left to right, the nova on the ground both ways (check() asserts it). Nothing rides in her action frames.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. The rounds leave her pivot 5 px
up (build_zeri a_y) and stay unseen for `lead` ticks, until they pass the levelled rifle's muzzle (26 px ahead of her,
17 over the soles: rig_zeri's release frames). Times from the kit (build_zeri.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "zeri", "codex_fx", "zeri-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the bottom row; "tip":
# the front, a column in from the right; "line": the cell's centre, the beam reaching right of it), symmetry asserted
SHEETS = {
    "a_burst": (4, "tip", "tb"), "a_hit": (4, "core", "lr"),
    "p_spark": (4, "tip", "tb"), "p_hit": (5, "core", "lr"), "p_ready": (6, ("feet", 0), "lr"),
    "p_shv": (4, ("feet", 0), "lr"), "p_slow": (4, "core", "lr"), "p_haste": (4, "core", "lr"),
    "w_cast": (5, ("feet", 0), "lr"), "w_pulse": (4, "tip", "tb"), "w_laser": (6, "line", "tb"),
    "w_wall": (4, "tip", "tb"), "w_hit": (4, "core", "lr"), "w_slow": (4, "core", "lr"),
    "e_cast": (5, "core", "lr"), "e_on": (4, ("feet", 0), "lr"), "e_shot": (4, "tip", "tb"), "e_hit": (4, "core", "lr"),
    "r_nova": (6, "core", "lr tb"), "r_on": (4, ("feet", 0), "lr"), "r_st2": (4, ("feet", 0), "lr"),
    "r_shot": (4, "tip", "tb"), "r_hit": (5, "core", "lr"), "r_zap": (4, "core", "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
SOLES = (0, 11)                 # on the ground under a unit
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
LEAD = 3                        # ticks: the rounds fly 8-9 px a tick and the muzzle is 26 px ahead of her pivot

FX = {
    # the rounds: the burst, E's piercing round and R's triple shot 9 px a tick to ~80 px (burst_speed, atk_range +
    # 20000), the charged spark 8 px a tick (homing: its first tick points up), W's pulse 9 px a tick to 110 px
    "a_burst": [("a_burst", flight(4, 50, 300, lead=LEAD), [(0, 0)])],
    "e_shot": [("e_shot", flight(4, 50, 300, lead=LEAD), [(0, 0)])],
    "r_shot": [("r_shot", flight(4, 50, 300, lead=LEAD), [(0, 0)])],
    "p_spark": [("p_spark", flight(4, 50, 360, lead=LEAD), [(0, 0)])],
    "w_pulse": [("w_pulse", flight(4, 50, 380, lead=LEAD), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_hit": [("p_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "r_zap": [("r_zap", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # on her: the pack full (about half a second), W's charge over its wind-up (w_rel 16 ticks = 267 ms)
    "p_ready": [("p_ready", seq(range(6), [60, 70, 80, 90, 100, 100]), [SOLES])],
    "w_cast": [("w_cast", seq(range(5), [50, 50, 55, 55, 57]), [SOLES])],
    # the buffs (looped while they last): the shield 180 ticks, E's 300, the slows, the haste
    "p_shv": [("p_shv", seq(range(4), [100] * 4), [SOLES])],
    "e_on": [("e_on", seq(range(4), [100] * 4), [SOLES])],
    "p_slow": [("p_slow", seq(range(4), [100] * 4), [SOLES])],
    "w_slow": [("w_slow", seq(range(4), [100] * 4), [SOLES])],
    "p_haste": [("p_haste", seq(range(4), [80] * 4), [SOLES])],
}
BIG = {
    # W's laser: a hitless line (delay w_ldelay 14 ticks = 233 ms) whose view sits on the point the pulse stopped on
    "w_laser": [("w_laser", seq(range(6), [40, 45, 45, 40, 33, 30]), [(0, 0)])],
    # the add-on's wall laser: a projectile league_zeri:laser spawns at the wall, 9 px a tick (w_speed) over w_laser
    "w_wall": [("w_wall", flight(4, 50, 400, lead=1), [(0, 0)])],
    # on the ground round her feet: E's dash burst, R's nova (r_reach 75 px)
    "e_cast": [("e_cast", seq(range(5), [40, 50, 60, 80, 100]), [SOLES])],
    "r_nova": [("r_nova", seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES])],
    # the overcharge (r_t 300 ticks) and its extension (r_st2, at most r_ext_t 150 ticks)
    "r_on": [("r_on", seq(range(4), [90] * 4), [SOLES])],
    "r_st2": [("r_st2", seq(range(4), [110] * 4), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"zeri_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"zeri_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
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
    empty (it reaches on from its point)."""
    for k, c in enumerate(strip):
        if sym and "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"zeri_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym and "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"zeri_fx_{name} cell {k + 1} is not symmetric top to bottom")
        if kind == "line" and c[:, :c.shape[1] // 2, 3].any():
            sys.exit(f"zeri_fx_{name} cell {k + 1} draws behind its point")


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
    for sheet, table in (("league_zeri_fx", FX), ("league_zeri_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

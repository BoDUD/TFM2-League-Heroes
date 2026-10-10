#!/usr/bin/env python3
"""Import Viego's effects (assets/source/viego/PROMPTS_FX.md, 25 sheets: 17 for the kit, 8 s_* for the add-on's soul
kits) as the game sheets league_viego_fx and league_viego_big.

    python tools/art/import_viego.py

Codex delivered every sheet at game size as well (assets/source/viego/codex_fx/viego-fx/pixel_1x/, one game pixel a
square, a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its
anchor and placed on its spot (tools/art/import_viktor.py's way). The one fix: the ground rings and a few bursts filled
their cells to the edges (flat-sided slabs, e_mist's last frame a solid block) - CLIP trims them to the ellipse inside
the cell (squares removed only, so the symmetry holds) and e_mist fades on its own frames played back.

Red side and blue side alike: the client mirrors his own frames with his facing and never an effect picture, so Codex
drew (and check() asserts) the flying pictures symmetric top to bottom (cast leftward the engine turns them upside
down), every picture on a unit and the buffs symmetric left to right, the ground pictures (e_mist, r_land, s_ring) both
ways. Nothing rides in his action frames. Spots are game px from the pivot (x forward, y down); a unit's soles are 11
under it. Times from the kit (build_viego.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "viego", "codex_fx", "viego-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the figure's place the
# pack left empty; "tip": the front, a column in from the right), symmetry asserted
SHEETS = {
    "a_hit": (4, "core", "lr"), "a_double": (5, "core", "lr"), "q_thrust": (4, "tip", "tb"),
    "q_hit": (4, "core", "lr"), "q_marked": (4, "core", "lr"), "w_maw": (4, "tip", "tb"), "w_hit": (4, "core", "lr"),
    "w_stun": (4, "core", "lr"), "e_mist": (8, "core", "lr tb"), "e_on": (4, ("feet", 0), "lr"),
    "p_take": (6, ("feet", 0), "lr"), "p_on": (4, ("feet", 0), "lr"), "p_safe": (4, ("feet", 1), "lr"),
    "p_end": (5, ("feet", 0), "lr"), "r_cast": (5, ("feet", 0), "lr"), "r_hit": (6, ("feet", 0), "lr"),
    "r_land": (6, "core", "lr tb"),
    "s_bolt": (4, "tip", "tb"), "s_line": (4, "tip", "tb"), "s_hit": (4, "core", "lr"), "s_burst": (5, "core", "lr"),
    "s_ring": (6, "core", "lr tb"), "s_slow": (4, "core", "lr"), "s_heal": (4, ("feet", 0), "lr"),
    "s_haste": (4, "core", "lr"),
}
# sheets trimmed to the ellipse inscribed in their cell (they filled it to the edges)
CLIP = {"e_mist", "r_land", "s_ring", "w_hit", "s_burst"}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -32)                 # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the thrust: a line at 8 px a tick over 40 px (5 ticks); the maw 4 px a tick over 42 (11 ticks); the soul bolt
    # homes (5 px a tick), the soul shot is a line (8 px a tick over 50)
    "q_thrust": [("q_thrust", flight(4, 50, 200), [(0, 0)])],
    "w_maw": [("w_maw", flight(4, 60, 400), [(0, 0)])],
    "s_bolt": [("s_bolt", flight(4, 60, 400, lead=2), [(0, 0)])],
    "s_line": [("s_line", flight(4, 50, 250), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "a_double": [("a_double", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [50, 60, 70, 80]), [HIT])],
    "s_hit": [("s_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # on him: the leap's puff, the mist leaving
    "r_cast": [("r_cast", seq(range(5), [40, 50, 60, 70, 80]), [SOLES])],
    "p_end": [("p_end", seq(range(5), [60, 70, 80, 90, 100]), [SOLES])],
    # buffs (looped while they last): Q's mark 4 s, the maw's stun 66 ticks, the mist's haste, the untouchable second,
    # the add-on's slow / heal / haste
    "q_marked": [("q_marked", seq(range(4), [120] * 4), [OVER])],
    "w_stun": [("w_stun", seq(range(4), [110] * 4), [OVER])],
    "e_on": [("e_on", seq(range(4), [110] * 4), [SOLES])],
    "p_safe": [("p_safe", seq(range(4), [100] * 4), [SOLES])],
    "s_slow": [("s_slow", seq(range(4), [100] * 4), [SOLES])],
    "s_heal": [("s_heal", seq(range(4), [120] * 4), [SOLES])],
    "s_haste": [("s_haste", seq(range(4), [100] * 4), [SOLES])],
}
BIG = {
    # the mist round his feet as he casts (the haste lasts 5 s on him as e_on): it spills out, curls twice, recedes
    "e_mist": [("e_mist", seq([0, 1] + [2 + k % 5 for k in range(10)] + [1, 0], [80, 80] + [100] * 10 + [100, 100]),
                [SOLES])],
    # the soul pulled in (the possess strip lasts 24 ticks), the possession's mist (looped)
    "p_take": [("p_take", seq(range(6), [60, 70, 80, 90, 100, 120]), [SOLES])],
    "p_on": [("p_on", seq(range(4), [120] * 4), [SOLES])],
    # R's stab on the target (its soles), the shockwave round him as he lands
    "r_hit": [("r_hit", seq(range(6), [40, 50, 60, 70, 80, 100]), [SOLES])],
    "r_land": [("r_land", seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES])],
    "s_burst": [("s_burst", seq(range(5), [40, 50, 60, 80, 100]), [HIT])],
    "s_ring": [("s_ring", seq(range(6), [40, 50, 60, 70, 80, 100]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"viego_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"viego_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(n)]
    if name in CLIP:
        h = a.shape[0]
        y, x = np.mgrid[0:h, 0:w]
        outside = ((x - (w - 1) / 2) / (w / 2)) ** 2 + ((y - (h - 1) / 2) / (h / 2)) ** 2 > 1
        for c in out:
            c[outside] = 0
    return out


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
            sys.exit(f"viego_fx_{name} cell {k + 1} is not symmetric left to right")
        if "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"viego_fx_{name} cell {k + 1} is not symmetric top to bottom")


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
    for sheet, table in (("league_viego_fx", FX), ("league_viego_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

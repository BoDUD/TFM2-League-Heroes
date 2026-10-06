#!/usr/bin/env python3
"""Import Kha'Zix's effects (assets/source/khazix/PROMPTS_FX.md, 16 sheets) as the game sheets league_khazix_fx and
league_khazix_big.

    python tools/art/import_khazix.py

Codex delivered every sheet at game size as well (assets/source/khazix/codex_fx/pixel_1x/, one game pixel a square, a
row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its anchor and
placed on its spot.

Red side and blue side alike (the user: 「注意红色方和蓝色方的技能特效不要不对称 导致歪的」): the client mirrors his own
frames with his facing and never an effect picture, so Codex drew (and check() asserts)
- the flying spike symmetric top to bottom (cast leftward the engine turns it upside down);
- what plays on him late, whichever way he faces (w_heal, p_ready, e_reset, evo), the buffs on him and under his feet
  (ut, r_on, slow), R's burst and the landing's shockwave symmetric left to right (the shockwave both ways).
The hits on a target (claw streaks, bursts) follow the target and point nowhere, as Pyke's.
Spots are game px from the pivot (x forward, y down; his soles 11 under it), measured on the strips (pack_khazix_fx
SHOTS); times from the kit (build_khazix.P, 60 ticks a second) and the strips.
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

SRC = os.path.join(ROOT, "assets", "source", "khazix", "codex_fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the figure's place the
# pack left empty; "tip": the spike's point, a column in from the right), symmetry asserted
SHEETS = {
    "a_hit": (4, "core", None), "p_hit": (5, "core", None), "q_hit": (4, "core", None), "q_iso_hit": (6, "core", None),
    "e_hit": (4, "core", None), "w_hit": (5, "core", None), "p_ready": (5, "core", "lr"), "e_reset": (5, "core", "lr"),
    "ut": (4, "core", "lr"), "slow": (4, "core", "lr"), "e_land": (6, "core", "lr tb"), "w_spike": (4, "tip", "tb"),
    "w_heal": (5, ("feet", 2), "lr"), "r_cast": (6, ("feet", 3), "lr"), "r_on": (4, ("feet", 2), "lr"),
    "evo": (8, ("feet", 2), "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
CHEST = (2, -14)                # his chest (the pack's ut: two flames either side of it)
OVER = (6, -34)                 # over his head (the face plate's top is 22 over the pivot, the antenna tips 33)
BODY = (2, -11)                 # the middle of his body
SOLES = (0, 11)                 # on the ground under a unit (his feet, or a point's)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the spike: 70 px at 9 px a tick (build_khazix.P w_speed 9000, w_len 70000); 2 empty ticks so it shows past the
    # claw (the throw frame's claw tip is 26 px ahead of the pivot)
    "w_spike": [("w_spike", flight(4, 50, 300, lead=2), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_hit": [("p_hit", seq(range(5), [40, 50, 60, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(5), [40, 50, 60, 60, 70]), [HIT])],
    "w_heal": [("w_heal", seq(range(5), [80] * 5), [SOLES])],
    "p_ready": [("p_ready", seq(range(5), [60, 60, 80, 60, 60]), [OVER])],
    "e_reset": [("e_reset", seq(range(5), [50, 60, 70, 70, 80]), [BODY])],
    # buffs (looped while they last); the two slows share one picture
    "ut": [("ut", seq(range(4), [100] * 4), [CHEST])],
    "slow": [("slow", seq(range(4), [100] * 4), [SOLES])],
}
BIG = {
    "q_iso_hit": [("q_iso_hit", seq(range(6), [40, 50, 60, 70, 70, 80]), [HIT])],
    # where he lands (the cast's tick 14), on the ground
    "e_land": [("e_land", seq(range(6), [50, 60, 60, 70, 70, 80]), [SOLES])],
    # R: the burst as he vanishes (the strip's 300 ms), and the shimmer while he is hidden (a buff)
    "r_cast": [("r_cast", seq(range(6), [50, 50, 60, 60, 70, 80]), [SOLES])],
    "r_on": [("r_on", seq(range(4), [90] * 4), [SOLES])],
    "evo": [("evo", seq(range(8), [80, 80, 80, 90, 90, 100, 100, 120]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"khazix_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"khazix_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
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
        if sym and "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"khazix_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym and "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"khazix_fx_{name} cell {k + 1} is not symmetric top to bottom")


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
    for sheet, table in (("league_khazix_fx", FX), ("league_khazix_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

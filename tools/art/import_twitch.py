#!/usr/bin/env python3
"""Import Twitch's effects (assets/source/twitch/PROMPTS_FX.md, 17 sheets) as the game sheets league_twitch_fx and
league_twitch_big.

    python tools/art/import_twitch.py

Codex delivered every sheet at game size as well (assets/source/twitch/codex_fx/twitch-fx/pixel_1x/, one game pixel a
square, a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its
anchor and placed on its spot (tools/art/import_khazix.py's way).

Red side and blue side alike (the user: 「注意红色方和蓝色方的技能特效不要不对称 导致歪的」): the client mirrors his own
frames with his facing and never an effect picture, so Codex drew (and check() asserts)
- the bolts and the cask symmetric top to bottom (cast leftward the engine turns them upside down);
- what plays on him late (q_out, q_reset, e_cast, r_cast), the buffs on him and under feet (q_as, r_on, w_slow) and
  Q's smoke symmetric left to right; the puddle both ways;
- the muzzle puff a_flash, which points forward, is drawn into the attack's release frame instead
  (assets/source/native/twitch_bake.json; tools/art/import_native.py bakes it), at the crossbow's tip there.
The hits on a target follow the target and point nowhere. Everything on him sits on his pivot's column (x 0).
Spots are game px from the pivot (x forward, y down; his soles 11 under it); the crossbow's tip in the attack's
release frame is 19 px ahead at the pivot's row (Codex's manifest: bow_tip (78, 70), pivot (59, 70)). Times from the
kit (build_twitch.P, 60 ticks a second) and the strips.
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

SRC = os.path.join(ROOT, "assets", "source", "twitch", "codex_fx", "twitch-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the figure's place the
# pack left empty; "tip": the arrowhead's point, a column in from the right; "left": the puff's start, the left
# middle), symmetry asserted
SHEETS = {
    "a_bolt": (4, "tip", "tb"), "a_flash": (3, "left", None), "a_hit": (4, "core", None), "v_pop": (6, "core", None),
    "w_cask": (4, "core", "tb"), "w_hit": (5, "core", None), "w_pool": (4, "core", "lr tb"), "w_slow": (4, "core", "lr"),
    "q_cast": (6, ("feet", 2), "lr"), "q_out": (5, ("feet", 2), "lr"), "q_as": (4, "core", "lr"),
    "q_reset": (5, "core", "lr"), "e_cast": (6, ("feet", 2), "lr"), "r_cast": (6, ("feet", 2), "lr"),
    "r_on": (4, ("feet", 2), "lr"), "r_bolt": (4, "tip", "tb"), "r_hit": (4, "core", None),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
WAIST = (0, -3)                 # his waist (q_as: two flames either side of it)
OVER = (0, -28)                 # over his head (his ears' tips are 26 over the pivot)
SOLES = (0, 11)                 # on the ground under a unit (his feet, or a point's)
MUZZLE = (19, 0)                # the crossbow's tip in the attack's release frame
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the bolts: 55 px at 7.5 px a tick (build_twitch.P bolt_speed 7500), R's 115 at 10; 2 empty ticks so they show
    # past the crossbow's tip (19 px ahead)
    "a_bolt": [("a_bolt", flight(4, 50, 300, lead=2), [(0, 0)])],
    "r_bolt": [("r_bolt", flight(4, 50, 300, lead=2), [(0, 0)])],
    # the cask: a 14-tick lob (w_travel)
    "w_cask": [("w_cask", flight(4, 60, 400, lead=1), [(0, 0)])],
    "a_flash": [("a_flash", seq(range(3), [40, 50, 60]), [MUZZLE])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(5), [40, 50, 60, 60, 70]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_cast": [("q_cast", seq(range(6), [50, 50, 60, 60, 70, 80]), [SOLES])],
    "q_out": [("q_out", seq(range(5), [50, 60, 60, 70, 80]), [SOLES])],
    "q_reset": [("q_reset", seq(range(5), [60, 60, 80, 60, 60]), [OVER])],
    # buffs (looped while they last)
    "q_as": [("q_as", seq(range(4), [100] * 4), [WAIST])],
    "w_slow": [("w_slow", seq(range(4), [100] * 4), [SOLES])],
}
BIG = {
    # Contaminate on every poisoned unit
    "v_pop": [("v_pop", seq(range(6), [40, 50, 60, 70, 70, 80]), [HIT])],
    # the puddle: a ViewEffect on the landing point for the zone's 180 ticks (3 s: the 4-frame loop 6 times + 120 ms)
    "w_pool": [("w_pool", seq([k % 4 for k in range(25)], [120] * 25), [(0, 0)])],
    "e_cast": [("e_cast", seq(range(6), [50, 60, 60, 70, 70, 80]), [SOLES])],
    "r_cast": [("r_cast", seq(range(6), [50, 50, 60, 60, 70, 80]), [SOLES])],
    "r_on": [("r_on", seq(range(4), [90] * 4), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"twitch_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"twitch_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "tip":
        return [w - 2, (h - 1) / 2]
    if kind == "left":
        return [0, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def check(name, strip, sym):
    """The red side's symmetry, cell by cell (the effect picture is never mirrored by the client)."""
    for k, c in enumerate(strip):
        if sym and "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"twitch_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym and "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"twitch_fx_{name} cell {k + 1} is not symmetric top to bottom")


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
    for sheet, table in (("league_twitch_fx", FX), ("league_twitch_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Import Renekton's effects (assets/source/renekton/PROMPTS_FX.md, 15 sheets) as the game sheets league_renekton_fx and
league_renekton_big.

    python tools/art/import_renekton.py

Codex delivered every sheet at game size as well (assets/source/renekton/codex_fx/pixel_1x/, one game pixel a square,
a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its anchor and
placed on its spot (tools/art/import_twitch.py's way).

Red side and blue side alike: the client mirrors his own frames with his facing and never an effect picture, so Codex
drew (and check() asserts) every hit, every picture on him (Q's rings, W's fury flare, R's burst) and every buff (full
Fury, the stun stars, the shred mark, R's sand aura) symmetric left to right. The two pictures with a front and a back -
the attack's slash a_slash and E's dash streak e_dash - are drawn into his frames instead
(assets/source/native/renekton_bake.json; tools/art/import_native.py bakes them): the slash at the blade's middle in
the attack's release frame (codex_strips_narrow/manifest.json: (88.8, 48.4), pivot (60, 70) -> 29 px ahead, 22 over the pivot), the
streak from just behind him in the dash frames, under the body.
Spots are game px from the pivot (x forward, y down; his soles 11 under it). Times from the kit (build_renekton.P, 60
ticks a second) and the strips.
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

SRC = os.path.join(ROOT, "assets", "source", "renekton", "codex_fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the figure's place the
# pack left empty; "right": the streak's start, the right middle), symmetry asserted
SHEETS = {
    "a_slash": (3, "core", None), "a_hit": (4, "core", "lr"), "q_spin": (6, "core", "lr"), "q_spin_e": (6, "core", "lr"),
    "q_hit": (4, "core", "lr"), "e_dash": (4, "right", None), "e_hit": (4, "core", "lr"), "w_hit": (4, "core", "lr"),
    "w_glow": (5, ("feet", 4), "lr"), "w_stun": (4, "core", "lr"), "e_shred": (4, "core", "lr"),
    "f5": (6, ("feet", 2), "lr"), "r_cast": (8, ("feet", 3), "lr"), "r_on": (6, ("feet", 6), "lr"),
    "r_burn": (4, "core", "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
STARS = (0, -31)                # over a unit's head
SHRED = (0, -38)                # over the stars
SOLES = (0, 11)                 # on the ground under him
WAIST = (0, -2)                 # Q's ring round his waist (it spans 64 px: Q's radius 32000)
BLADE = (29, -22)               # the blade's middle in the attack's release frame (the narrowed strips)
BACK = (-8, 2)                  # E's streak starts behind his hips and trails back
EMPTY = J.EMPTY
seq = J.seq

FX = {
    # baked into his frames (renekton_bake.json), not views
    "a_slash": [("a_slash", seq(range(3), [50, 60, 70]), [BLADE])],
    "e_dash": [("e_dash", seq(range(4), [50, 60, 60, 70]), [BACK])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_burn": [("r_burn", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_glow": [("w_glow", seq(range(5), [60, 60, 70, 70, 80]), [SOLES])],
    # buffs (looped while they last)
    "f5": [("f5", seq(range(6), [90] * 6), [SOLES])],
    "w_stun": [("w_stun", seq(range(4), [100] * 4), [STARS])],
    "e_shred": [("e_shred", seq(range(4), [120] * 4), [SHRED])],
}
BIG = {
    # Q's sweep lands on tick 7 (117 ms): the ring's widest frame 3 is there
    "q_spin": [("q_spin", seq(range(6), [50, 50, 60, 60, 70, 80]), [WAIST])],
    "q_spin_e": [("q_spin_e", seq(range(6), [50, 50, 60, 60, 70, 80]), [WAIST])],
    "r_cast": [("r_cast", seq(range(8), [60, 60, 70, 70, 80, 80, 90, 100]), [SOLES])],
    "r_on": [("r_on", seq(range(6), [100] * 6), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"renekton_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"renekton_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "right":
        return [w - 1, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def check(name, strip, sym):
    """The red side's symmetry, cell by cell (the effect picture is never mirrored by the client)."""
    for k, c in enumerate(strip):
        if sym and "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"renekton_fx_{name} cell {k + 1} is not symmetric left to right")


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
    for sheet, table in (("league_renekton_fx", FX), ("league_renekton_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

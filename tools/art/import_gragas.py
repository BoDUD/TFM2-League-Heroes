#!/usr/bin/env python3
"""Import Gragas's effects (assets/source/gragas/PROMPTS_FX.md, 16 sheets) as the game sheets league_gragas_fx and
league_gragas_big.

    python tools/art/import_gragas.py

Codex delivered every sheet at game size as well (assets/source/gragas/codex_fx/pixel_1x/, one game pixel a square, a
row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its anchor and
placed on its spot (tools/art/import_nautilus.py's way).

Red side and blue side alike: the client mirrors his own frames with his facing and never an effect picture, so Codex
drew (and check() asserts) the two flying kegs symmetric top to bottom (cast leftward the engine turns them upside
down) and every other picture symmetric left to right. Nothing rides in his action frames. Spots are game px from the
pivot (x forward, y down); a unit's soles are 11 under it, and a point on the ground (Q's barrel, the blasts) is drawn
the same way. Times from the kit (build_gragas.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "gragas", "codex_fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the ground or the
# figure's soles; "tip": the front), symmetry asserted
SHEETS = {
    "a_hit": (4, "core", "lr"), "w_hit": (5, "core", "lr"), "q_barrel": (4, "core", "tb"), "q_land": (6, ("feet", 0), "lr"),
    "q_boom": (6, ("feet", 7), "lr"), "q_hit": (4, "core", "lr"), "q_slow": (4, "core", "lr"),
    "e_dust": (5, ("feet", 4), "lr"), "e_hit": (5, "core", "lr"), "e_stun": (4, "core", "lr"),
    "w_drink": (6, "core", "lr"), "w_on": (4, ("feet", 0), "lr"), "p_heal": (5, ("feet", 0), "lr"),
    "r_cask": (4, "core", "tb"), "r_boom": (7, ("feet", 8), "lr"), "r_hit": (4, "core", "lr"),
}
# Q's pictures drawn twice as big (every square 2 x 2): the user, 「Q技能特效要做大点吧 现在也太小了」, chose 「我直接放大 2 倍」
TWICE = {"q_barrel", "q_land", "q_boom"}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -34)                 # over a unit's head (his crown is 31 over the pivot)
SOLES = (0, 11)                 # on the ground under a unit or a point
HEAD = (0, -25)                 # round his head (the drink); x 0 keeps the picture symmetric about his pivot
GROUND_HIT = (0, 2)             # an area burst round a unit, on its lower body
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the barrel: a lob of 22 ticks (367 ms)
    "q_barrel": [("q_barrel", flight(4, 70, 400), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # the barrel on the ground for q_wait 45 ticks (750 ms), shaking harder, then the blast
    "q_land": [("q_land", seq(range(6), [125] * 6), [SOLES])],
    # the dust where he starts the charge (left there), his drink round his head, the swig
    "e_dust": [("e_dust", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
    "w_drink": [("w_drink", seq(range(6), [60] * 6), [HEAD])],
    "p_heal": [("p_heal", seq(range(5), [60, 70, 80, 90, 100]), [SOLES])],
    # buffs (looped while they last): the slow 120 ticks, the stun 60, the rage 300
    "q_slow": [("q_slow", seq(range(4), [100] * 4), [SOLES])],
    "e_stun": [("e_stun", seq(range(4), [100] * 4), [OVER])],
    "w_on": [("w_on", seq(range(4), [110] * 4), [SOLES])],
}
BIG = {
    # the cask: a lob of 16 ticks (267 ms)
    "r_cask": [("r_cask", flight(4, 70, 300), [(0, 0)])],
    "w_hit": [("w_hit", seq(range(5), [40, 50, 60, 70, 80]), [GROUND_HIT])],
    "q_boom": [("q_boom", seq(range(6), [40, 50, 60, 70, 80, 100]), [SOLES])],
    "r_boom": [("r_boom", seq(range(7), [40, 50, 60, 70, 80, 90, 110]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"gragas_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"gragas_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
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
            sys.exit(f"gragas_fx_{name} cell {k + 1} is not symmetric left to right")
        if "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"gragas_fx_{name} cell {k + 1} is not symmetric top to bottom")


def odd(cell):
    """An even-width cell symmetric left to right gets its middle column doubled: frames are centred on the pivot's
    pixel (odd widths), so only an odd-width picture stays symmetric about the pivot (lint's caster-picture check)."""
    w = cell.shape[1]
    if w % 2 or not (cell == cell[:, ::-1]).all():
        return cell
    return np.concatenate([cell[:, :w // 2], cell[:, w // 2 - 1:w // 2], cell[:, w // 2:]], axis=1)


def build(table):
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            n, kind, sym = SHEETS[src]
            strip = cells(src, n)
            check(src, strip, sym)
            if src in TWICE:
                strip = [np.repeat(np.repeat(c, 2, 0), 2, 1) for c in strip]
                kind = ("feet", 2 * kind[1]) if isinstance(kind, tuple) else kind
            if "lr" in sym:
                strip = [odd(c) for c in strip]
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
    for sheet, table in (("league_gragas_fx", FX), ("league_gragas_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

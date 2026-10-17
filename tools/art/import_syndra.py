#!/usr/bin/env python3
"""Import Syndra's effects (assets/source/syndra/PROMPTS_FX.md, 17 sheets) as the game sheets league_syndra_fx and
league_syndra_big.

    python tools/art/import_syndra.py

Codex delivers every sheet at game size as well (assets/source/syndra/codex_fx/syndra-fx/pixel_1x/, one game pixel a
square, a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out, given its
anchor and placed on its spot (tools/art/import_viktor.py's way).

Red side and blue side alike: the client mirrors her own frames with her facing and never an effect picture, so the
flying bolt and spheres and the wave's line picture are symmetric top to bottom (cast leftward the engine turns them
upside down), every picture on a unit, the buff and what plays on her (r_cast, evo) symmetric left to right, the
ground pictures (q_form, q_blast, w_land) both ways, the resting sphere left to right (check() asserts it). The wave
(e_wave) is a hitless 1000-unit line from her toward the target, its view on the line's middle (on her): its cell's
centre goes on the pivot, so the wave reaches on from her. Nothing rides in her action frames. Spots are game px from
the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit (build_syndra.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "syndra", "codex_fx", "syndra-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the bottom row; "tip":
# the front, a column in from the right; "line": the cell's centre, the wave reaching right of it), symmetry asserted
SHEETS = {
    "a_bolt": (4, "tip", "tb"), "a_hit": (4, "core", "lr"),
    "q_form": (6, "core", "lr tb"), "q_blast": (5, "core", "lr tb"), "q_hit": (4, "core", "lr"),
    "orb": (12, ("feet", 0), "lr"),
    "w_throw": (4, "tip", "tb"), "w_land": (5, "core", "lr tb"), "w_hit": (4, "core", "lr"), "w_slow": (4, "core", "lr"),
    "e_wave": (5, "line", "tb"), "e_hit": (4, "core", "lr"), "e_stun": (8, ("feet", 0), "lr"),
    "r_cast": (6, ("feet", 0), "lr"), "r_orb": (4, "tip", "tb"), "r_hit": (5, "core", "lr"),
    "evo": (6, ("feet", 0), "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
SOLES = (0, 11)                 # on the ground under a unit
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight


def only(frames, keep):
    """A flight's frames drawn from `keep` only (frame k -> keep[k % len(keep)]): Codex's thrown sphere and R's sphere
    are clean in their cells 3-4, while forcing the top-bottom symmetry split cells 1-2 into two half-spheres round a
    magenta seam (r_orb) and a finned shape (w_throw) - those two cells are not played."""
    return [(k if k == EMPTY else keep[k % len(keep)], ms) for k, ms in frames]

FX = {
    # the bolt and the spheres: a_bolt 4.5 px a tick to ~55 px; the thrown sphere a 16-tick lob; R's spheres 4.2 px a
    # tick to ~75 px; empty ticks past her hand (a homing shot's first tick points up)
    "a_bolt": [("a_bolt", flight(4, 60, 320, lead=2), [(0, 0)])],
    "w_throw": [("w_throw", only(flight(4, 60, 280, lead=1), [2, 3]), [(0, 0)])],
    "r_orb": [("r_orb", only(flight(4, 60, 420, lead=2), [2, 3]), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    # a sphere crashing into a unit, then the stun over it (e_stun 75 ticks = 1250 ms)
    "e_stun": [("e_stun", seq(range(8), [60, 70, 80, 208, 208, 208, 208, 208]), [SOLES])],
    "evo": [("evo", seq(range(6), [60, 70, 80, 90, 100, 120]), [SOLES])],
    # the buff (looped while it lasts)
    "w_slow": [("w_slow", seq(range(4), [100] * 4), [SOLES])],
}
BIG = {
    # E's wave: a hitless line of delay 14 ticks (233 ms) from her
    "e_wave": [("e_wave", seq(range(5), [40, 45, 50, 50, 48]), [(0, 0)])],
    # the ground pictures on their points
    "q_form": [("q_form", seq(range(6), [80, 80, 85, 85, 85, 85]), [(0, 0)])],          # q_fall 30 ticks
    "q_blast": [("q_blast", seq(range(5), [40, 50, 60, 80, 100]), [(0, 0)])],
    "w_land": [("w_land", seq(range(5), [40, 50, 60, 80, 100]), [(0, 0)])],
    # the resting sphere: orb_t 360 ticks = 6000 ms (it appears, floats, fades)
    "orb": [("orb", seq(range(12), [150, 150] + [650] * 8 + [300, 200]), [(0, 0)])],
    # R: the spheres gathering round her (r_anim 40 ticks)
    "r_cast": [("r_cast", seq(range(6), [100, 110, 110, 115, 116, 116]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"syndra_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"syndra_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
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
    empty (it reaches on from her)."""
    for k, c in enumerate(strip):
        if sym and "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"syndra_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym and "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"syndra_fx_{name} cell {k + 1} is not symmetric top to bottom")
        if kind == "line" and c[:, :c.shape[1] // 2, 3].any():
            sys.exit(f"syndra_fx_{name} cell {k + 1} draws behind her")


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
    for sheet, table in (("league_syndra_fx", FX), ("league_syndra_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

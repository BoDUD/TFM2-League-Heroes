#!/usr/bin/env python3
"""Import Corki's effects (assets/source/corki/PROMPTS_FX.md, 17 sheets) as the game sheets league_corki_fx and
league_corki_big.

    python tools/art/import_corki.py

Codex delivered every sheet at game size as well (assets/source/corki/codex_fx/pixel_1x/, one game pixel a square, a
row of equal cells, the pack's colours only; manifest.json gives the cells), so nothing is resampled here: each cell is
cut out, given its anchor and placed on its spot (tools/art/import_gragas.py's way). The effects stay 1x while his body
is dense (PPU 5): league.dll scales only the hero's own sheet.

Red side and blue side alike: the client mirrors his own frames with his facing and never an effect picture, so Codex
drew (and check() asserts) the bullet, the bomb and the missiles symmetric top to bottom (cast leftward the engine turns
them upside down) and every other picture symmetric left to right. Nothing rides in his action frames. Spots are game
px from the pivot (x forward, y down); a unit's soles are 11 under it, and a point on the ground (the blasts, the fire
patches) is drawn the same way. Times from the kit (build_corki.P, 60 ticks a second).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from build_corki import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "corki", "codex_fx")
MOD = os.path.join(ROOT, "league")

# the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the ground), symmetry asserted
SHEETS = {
    "a_bolt": ("core", "tb"), "a_hit": ("core", "lr"), "q_bomb": ("core", "tb"), "q_boom": (("feet", 7), "lr"),
    "q_hit": ("core", "lr"), "e_hit": ("core", "lr"), "e_shred": ("core", "lr"), "w_fire": (("feet", 2), "lr"),
    "w_fire_big": (("feet", 3), "lr"), "w_burn": ("core", "lr"), "pk_blast": (("feet", 5), "lr"),
    "pk_hit": ("core", "lr"), "r_missile": ("core", "tb"), "r_big_missile": ("core", "tb"),
    "r_boom": (("feet", 5), "lr"), "r_big_boom": (("feet", 7), "lr"), "r_hit": ("core", "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -32)                 # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MUZZLE = 19                     # px in front of his pivot: the gun's mouth (the bullets and missiles stay unseen to it)


def ticks_ms(t):
    return t * 1000 / 60


A_LEAD = max(1, round(MUZZLE / (P["a_speed"] / 1000)))
R_LEAD = max(1, round(MUZZLE / (P["r_speed"] / 1000)))
FX = {
    # the shot: 55 px at 6 px a tick (homing: twice the straight flight)
    "a_bolt": [("a_bolt", flight(2, 60, 2 * ticks_ms(P["atk_range"] / P["a_speed"]), A_LEAD), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # the bomb: a lob of q_fly ticks
    "q_bomb": [("q_bomb", flight(4, 60, ticks_ms(P["q_fly"]) + 100), [(0, 0)])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # the gatling's hits every e_per ticks (250 ms): short
    "e_hit": [("e_hit", seq(range(3), [50, 60, 70]), [HIT])],
    # the shred over the head, looped while it lasts (e_shred_t)
    "e_shred": [("e_shred", seq(range(4), [100] * 4), [OVER])],
    # the fire patch for w_fire_t ticks (2.5 s: 10 frames of 250 ms), under the units
    "w_fire": [("w_fire", seq(range(10), [ticks_ms(P["w_fire_t"]) / 10] * 10), [SOLES])],
    "w_burn": [("w_burn", seq(range(4), [50, 60, 70, 80]), [HIT])],
    "pk_hit": [("pk_hit", seq(range(4), [40, 50, 70, 90]), [HIT])],
    # the missile: r_range + 10000 at 6 px a tick
    "r_missile": [("r_missile", flight(3, 60, ticks_ms((P["r_range"] + 10000) / P["r_speed"]), R_LEAD), [(0, 0)])],
    "r_boom": [("r_boom", seq(range(5), [40, 50, 60, 80, 100]), [SOLES])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
}
BIG = {
    "q_boom": [("q_boom", seq(range(6), [40, 50, 60, 70, 80, 100]), [SOLES])],
    # the Package's fire for pk_fire_t ticks (4 s: 12 frames)
    "w_fire_big": [("w_fire_big", seq(range(12), [ticks_ms(P["pk_fire_t"]) / 12] * 12), [SOLES])],
    # the take-off blast where he leaves (it stays there)
    "pk_blast": [("pk_blast", seq(range(6), [40, 50, 60, 80, 90, 110]), [SOLES])],
    "r_big_missile": [("r_big_missile", flight(3, 60, ticks_ms((P["r_range"] + 10000) / P["r_speed"]), R_LEAD),
                       [(0, 0)])],
    "r_big_boom": [("r_big_boom", seq(range(7), [40, 50, 60, 70, 80, 90, 110]), [SOLES])],
}


def cells(name):
    man = {a["file"]: a for a in json.load(open(os.path.join(SRC, "manifest.json"), encoding="utf-8"))["assets"]}
    spec = man[f"corki_fx_{name}.png"]
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, "pixel_1x", f"corki_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    (w, h), n = spec["cell_1x"], spec["frames"]
    if a.shape[1] != w * n or a.shape[0] != h:
        sys.exit(f"corki_fx_{name}.png: {a.shape[1]}x{a.shape[0]} is not {n} cells of {w}x{h}")
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
            sys.exit(f"corki_fx_{name} cell {k + 1} is not symmetric left to right")
        if "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"corki_fx_{name} cell {k + 1} is not symmetric top to bottom")


def odd(cell, axis):
    """An even-sized cell symmetric along `axis` gets its middle line doubled: frames are centred on the pivot's pixel
    (odd sizes), so only an odd-sized picture stays symmetric about the pivot."""
    n = cell.shape[axis]
    if n % 2:
        return cell
    mid = cell.take([n // 2 - 1], axis=axis)
    lo, hi = np.split(cell, [n // 2], axis=axis)
    return np.concatenate([lo, mid, hi], axis=axis)


def build(table):
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            kind, sym = SHEETS[src]
            strip = cells(src)
            check(src, strip, sym)
            strip = [odd(c, 1 if sym == "lr" else 0) for c in strip]
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
    for sheet, table in (("league_corki_fx", FX), ("league_corki_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

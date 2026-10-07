#!/usr/bin/env python3
"""Import Seraphine's effects (assets/source/seraphine/PROMPTS_FX.md, 25 sheets) as the game sheets league_seraphine_fx
and league_seraphine_big.

    python tools/art/import_seraphine.py

Codex delivered every sheet at game size as well (assets/source/seraphine/codex_fx/seraphine-fx/pixel_1x/, one game
pixel a square, a row of equal cells, the pack's colours only), so nothing is resampled here: each cell is cut out,
given its anchor and placed on its spot (tools/art/import_twitch.py's way).

Red side and blue side alike: the client mirrors her own frames with her facing and never an effect picture, so Codex
drew (and check() asserts) the flying notes and waves symmetric top to bottom (cast leftward the engine turns them
upside down), every picture on a unit, the buffs and what plays on her late (w_cast, r_cast, echo) symmetric left to
right, the ground rings (q_land, w_cast) both ways. Nothing rides in her action frames: her hand sends everything.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it - hers are the stage's bottom, her
boots stand on the deck 1 under the pivot, her head's top is 40 over it. Times from the kit (build_seraphine.P, 60
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

SRC = os.path.join(ROOT, "assets", "source", "seraphine", "codex_fx", "seraphine-fx", "pixel_1x")
MOD = os.path.join(ROOT, "league")

# frames per sheet, the anchor in the cell ("core": the middle; ("feet", rows over the bottom): the figure's place the
# pack left empty; "tip": the front, a column in from the right), symmetry asserted
SHEETS = {
    "a_bolt": (4, "tip", "tb"), "a_note": (4, "tip", "tb"), "a_hit": (4, "core", "lr"), "a_note_hit": (5, "core", "lr"),
    "q_note": (4, "core", "tb"), "q_land": (6, "core", "lr tb"), "q_hit": (4, "core", "lr"), "q_amp": (5, "core", "lr"),
    "e_wave": (4, "tip", "tb"), "e_hit": (4, "core", "lr"), "e_root": (6, "core", "lr"), "e_stun": (4, "core", "lr"),
    "w_cast": (6, "core", "lr tb"), "w_on": (4, ("feet", 2), "lr"), "w_heal": (6, ("feet", 0), "lr"),
    "r_wave": (4, "tip", "tb"), "r_cast": (6, ("feet", 0), "lr"), "r_hit": (5, "core", "lr"),
    "echo": (5, "core", "lr"), "n1": (4, ("feet", 0), "lr"), "n2": (4, ("feet", 0), "lr"), "n3": (4, ("feet", 0), "lr"),
    "n4": (4, ("feet", 0), "lr"), "echo_ready": (4, "core", "lr"), "e_slow": (4, "core", "lr"),
}
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -30)                 # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit (her stage's bottom)
BODY = (0, -19)                 # the middle of her figure above the deck (boots 1 under the pivot, head 40 over)
NOTES = (0, -6)                 # the notes' figure area (18 x 34) stands here: its top at her head's top
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the notes: 55 px at 6 px a tick (build_seraphine.P bolt_speed 6000); 3 empty ticks so they show past her hand
    # (22 px ahead)
    "a_bolt": [("a_bolt", flight(4, 60, 320, lead=3), [(0, 0)])],
    "a_note": [("a_note", flight(4, 60, 320, lead=3), [(0, 0)])],
    # High Note: an 18-tick lob (q_travel)
    "q_note": [("q_note", flight(4, 70, 400, lead=1), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "a_note_hit": [("a_note_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_amp": [("q_amp", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # the root (e_root 45 ticks = 750 ms) and the stun's dizzy notes (e_stun 45 ticks, the loop played twice)
    "e_root": [("e_root", seq(range(6), [100, 120, 130, 130, 140, 130]), [SOLES])],
    "e_stun": [("e_stun", seq([k % 4 for k in range(8)], [95] * 8), [OVER])],
    "w_heal": [("w_heal", seq(range(6), [60, 70, 80, 90, 100, 100]), [SOLES])],
    "r_hit": [("r_hit", seq(range(5), [50, 60, 80, 100, 110]), [HIT])],
    "echo": [("echo", seq(range(5), [50, 60, 70, 80, 90]), [BODY])],
    # buffs (looped while they last)
    "n1": [("n1", seq(range(4), [120] * 4), [NOTES])],
    "n2": [("n2", seq(range(4), [120] * 4), [NOTES])],
    "n3": [("n3", seq(range(4), [120] * 4), [NOTES])],
    "n4": [("n4", seq(range(4), [120] * 4), [NOTES])],
    "echo_ready": [("echo_ready", seq(range(4), [110] * 4), [SOLES])],
    "e_slow": [("e_slow", seq(range(4), [100] * 4), [SOLES])],
    "w_on": [("w_on", seq(range(4), [100] * 4), [SOLES])],
}
BIG = {
    # the waves fly as lines (E 100000 at 6000 a tick, R 90000-150000 at 5000): looped over their flight
    "e_wave": [("e_wave", flight(4, 60, 400, lead=1), [(0, 0)])],
    "r_wave": [("r_wave", flight(4, 70, 600, lead=1), [(0, 0)])],
    # High Note's landing ring on the point, under the units
    "q_land": [("q_land", seq(range(6), [40, 50, 60, 70, 80, 90]), [(0, 0)])],
    # the song's ring spreading from her stage, under the units
    "w_cast": [("w_cast", seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES])],
    "r_cast": [("r_cast", seq(range(6), [60, 80, 100, 100, 110, 120]), [SOLES])],
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"seraphine_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"seraphine_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
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
            sys.exit(f"seraphine_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym and "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"seraphine_fx_{name} cell {k + 1} is not symmetric top to bottom")


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
    for sheet, table in (("league_seraphine_fx", FX), ("league_seraphine_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

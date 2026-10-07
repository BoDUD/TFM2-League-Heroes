#!/usr/bin/env python3
"""Import Kayle's ascension pictures (assets/source/kayle/PROMPTS_ASCEND.md, 11 sheets) as the game sheet
league_kayle_ascend.

    python tools/art/import_kayle_ascend.py

Codex delivered every sheet at game size as well (assets/source/kayle/codex_ascend/kayle-ascend/pixel_1x/, one game
pixel a square, a row of equal cells), so nothing is resampled: each cell is cut out, its anchor put on its spot
(tools/art/import_viktor.py's way), the red side's symmetry asserted (the client never mirrors an effect picture): the
wings and the hits left to right, the flying ones top to bottom, the ground blast both ways.
Spots and times follow her base pictures (tools/art/import_kayle.py: the flying ones centred on the projectile's point,
60 ms a frame; the hits on the chest (0, -4), 50 ms; the blasts centred, 60 ms); the wings' root (the cell's centre)
sits 20 px over her pivot, at her upper back, looped at 100 ms. tools/fix/kayle_ascend.py binds them.
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

SRC = os.path.join(ROOT, "assets", "source", "kayle", "codex_ascend", "kayle-ascend", "pixel_1x")
MOD = os.path.join(ROOT, "league")
CHEST = (0, -4)
WINGS = (0, -20)
seq = J.seq

# name: (frames, symmetry, spot, ms per frame)
SHEETS = {
    "wings1": (4, "lr", WINGS, [100] * 4), "wings2": (4, "lr", WINGS, [100] * 4), "wings3": (4, "lr", WINGS, [100] * 4),
    "bolt_x": (4, "tb", (0, 0), [60] * 4), "wave_x": (4, "tb", (0, 0), [60] * 4),
    "q_sword_x": (4, "tb", (0, 0), [60] * 4), "e_bolt_x": (4, "tb", (0, 0), [60] * 4),
    "bolt_hit_x": (5, "lr", CHEST, [50] * 5), "e_hit_x": (6, "lr", CHEST, [50] * 6),
    "q_blast_x": (7, "lr tb", (0, 0), [60] * 7), "e_blast_x": (7, "lr", (0, 0), [60] * 7),
}


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"kayle_fx_{name}.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w = a.shape[1] // n
    if w * n != a.shape[1]:
        sys.exit(f"kayle_fx_{name}.png: {a.shape[1]} px is not {n} equal cells")
    return [a[:, k * w:(k + 1) * w].copy() for k in range(n)]


def check(name, strip, sym):
    for k, c in enumerate(strip):
        if "lr" in sym and not (c == c[:, ::-1]).all():
            sys.exit(f"kayle_fx_{name} cell {k + 1} is not symmetric left to right")
        if "tb" in sym and not (c == c[::-1]).all():
            sys.exit(f"kayle_fx_{name} cell {k + 1} is not symmetric top to bottom")


def main():
    tags = {}
    for name, (n, sym, spot, ms) in SHEETS.items():
        strip = cells(name, n)
        check(name, strip, sym)
        h, w = strip[0].shape[:2]
        anc = [(w - 1) / 2, (h - 1) / 2]
        tags[name] = [(J.place(c, anc, [spot]), m) for c, m in zip(strip, ms)]
    w, h = G.write_sheet(os.path.join(MOD, "effects", "league_kayle_ascend"), tags)
    print(f"league/effects/league_kayle_ascend#sheet.png {w}x{h}: " + ", ".join(
        f"{t} {len(v)}f" for t, v in tags.items()))


if __name__ == "__main__":
    main()

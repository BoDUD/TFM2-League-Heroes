#!/usr/bin/env python3
"""Import Darius's effects (assets/source/darius/PROMPTS.md, 11-20) as game sheets.

    python tools/art/import_darius.py

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. The ten effect
strips came back from the Codex run as native pixel art: every game pixel one flat 8x8 block, frames
in equal cells (32 px square; the E sweep 64x32, the R impact 32x64). They are read one pixel per
block and anchored as the prompts drew them: hits and bleeding on their centre, the effects around a
person on that person's feet, the ground ring on its centre, the sweep on the middle of its left
edge (Darius), the impact on its landing point. Whatever was drawn around a person-sized space is
enlarged 2x: the space is 60% of a 32 px cell, about 19 px, a hero 34. The Q ring was drawn around a
person 40% tall; 2x it spans about 59 px, so league_darius's Q hits within 32000 (1000 units a
pixel). The sweep stays 1x (64 px; the hook reaches 46000). Views are drawn at the unit's pivot,
11 px above the feet line (the other importers do the same), so feet and ground anchors go 11 px
below it. No palette or outline pass: the effects keep the delivery's colours.
Writes league/effects/league_darius_fx (hit, bleed, q_heal, might, w_ready, w_hit, e_hook) and
league/effects/league_darius_big (q_spin, e_sweep, r_impact).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "darius")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)                        # the feet line / the ground, from the pivot
CHEST = (0, -4)


def cells(name, n):
    """The strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"darius_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"darius_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] >= 128, 3] = 255
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (strip, frames, enlarge, anchor in the cell, spot from the pivot, ms per frame)}
FX = {
    "league_darius_fx": {
        "hit": ("fx_hit", 5, 1, (16, 16), CHEST, [60] * 5),
        "bleed": ("fx_bleed", 5, 1, (16, 16), CHEST, [80] * 5),
        "q_heal": ("fx_q_heal", 6, 2, (16, 28), FEET, [80] * 6),
        "might": ("fx_might", 6, 2, (16, 28), FEET, [167] * 6),          # one pulse a second for 5 s
        "w_ready": ("fx_w_ready", 4, 2, (16, 24), FEET, [100] * 4),      # loops while the buff lasts
        "w_hit": ("fx_w_hit", 6, 2, (16, 28), FEET, [70] * 6),
        "e_hook": ("fx_e_hook", 5, 2, (16, 28), FEET, [60] * 5),
    },
    "league_darius_big": {
        "q_spin": ("fx_q_spin", 6, 2, (16, 22), FEET, [50] * 6),         # person 40% tall, feet at 70%
        "e_sweep": ("fx_e_sweep", 5, 1, (0, 16), (0, 0), [55] * 5),       # the projectile, turned toward the target
        "r_impact": ("fx_r_impact", 8, 2, (16, 56), FEET, [70] * 8),
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (strip, n, k, (ax, ay), (sx, sy), ms) in tags.items():
            frames = []
            for f, m in zip(cells(strip, n), ms):
                if k > 1:
                    f = np.kron(f, np.ones((k, k, 1), np.uint8))
                # the frame's top-left corner relative to the pivot pixel (anchors are pixel corners)
                u0, r0 = int(sx - ax * k), int(sy - ay * k)
                frames.append((G.centre_frame(f, u0, r0), m))
            out[tag] = frames
        sheets[sprite] = out
    return sheets


def main():
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

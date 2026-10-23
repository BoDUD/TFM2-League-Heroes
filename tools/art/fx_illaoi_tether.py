#!/usr/bin/env python3
"""Illaoi's spirit tether drawn at game size (the user, 2026-10-23: 「拉灵魂没有特效 完全看不出 也和英雄联盟不一样」).

    python tools/art/fx_illaoi_tether.py [--review out.png]     (tools/art/import_illaoi_fx.py calls frames())

  e_tether  one link of the ghostly line between a torn-out spirit and its body, drawn pointing right (the game turns
            it): a 10 x 3 px strand in the GHOST ramp (tools/art/pack_illaoi_fx.py) with a pale core, two frames that
            shift its bright beads so the line seems to flow. The add-on (addons/league_illaoi) lays a chain of them
            along the line every tick, LINK_STEP world units apart (one link's length: 1000 units a game px).
No outline (VFX spec): a thin line read against the ground by its pale core.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402


def hexes(*hs):
    return [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in hs]


GHOST = hexes("#FFFFFF", "#E0FFF8", "#A8F0E4", "#5CC8C0", "#2A7A80")
LENGTH = 10                      # game px a link; LINK_STEP in addons/league_illaoi/src/lib.rs is LENGTH x 1000


def e_tether():
    out = []
    for f in range(2):
        a = np.zeros((3, LENGTH, 4), np.uint8)
        for x in range(LENGTH):
            bead = (x + 3 * f) % 5 == 0
            a[1, x, :3] = GHOST[0] if bead else GHOST[1]
            a[0, x, :3] = a[2, x, :3] = GHOST[2] if bead else GHOST[3]
            a[0, x, 3] = a[2, x, 3] = 255 if bead or x % 2 == f else 0
            a[1, x, 3] = 255
        out.append((G.centre_frame(a, -(LENGTH // 2), -1), 60))
    return out


def e_echo():
    """The spirit struck (the user: 「打灵魂时也没特效啊 别人看了不知道在干嘛」): a white flash on its chest and a pale ring
    thrown out round it, 4 frames - played on the spirit's spot each time a hit on its body echoes."""
    out = []
    for k, (core, ring) in enumerate([(3, 0), (2, 6), (1, 9), (0, 11)]):
        n = 2 * 12 + 1
        a = np.zeros((n, n, 4), np.uint8)
        c = 12
        for y in range(n):
            for x in range(n):
                d = ((x - c) ** 2 + (y - c) ** 2) ** 0.5
                col = None
                if core and d <= core:
                    col = GHOST[0] if d <= core - 1 else GHOST[1]
                elif ring and abs(d - ring) < 0.7:
                    col = GHOST[1] if k < 2 else GHOST[3]
                if col is not None:
                    a[y, x, :3] = col
                    a[y, x, 3] = 255
        # the ring breaks up as it fades
        if k == 3:
            a[::2, :, 3] = 0
        out.append((G.centre_frame(a, -c, -c), [40, 50, 60, 70][k]))
    return out


def frames():
    """{tag: [(frame centred on its pivot, ms)]} - in league_illaoi_fx (tools/art/import_illaoi_fx.py)."""
    return {"e_tether": e_tether(), "e_echo": e_echo()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="the link at 12x")
    a = ap.parse_args()
    for tag, fr in frames().items():
        print(tag, " ".join(f"{f.shape[1]}x{f.shape[0]}" for f, _ in fr))
        if a.review:
            Z = 12
            ims = [Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST) for f, _ in fr]
            can = Image.new("RGBA", (sum(i.width + 12 for i in ims), max(i.height for i in ims) + 12), (70, 78, 60, 255))
            x = 6
            for i in ims:
                can.alpha_composite(i, (x, 6))
                x += i.width + 12
            can.save(a.review)


if __name__ == "__main__":
    main()

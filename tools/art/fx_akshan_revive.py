#!/usr/bin/env python3
"""Akshan's revive effect: a golden beam of light down onto the revived ally (and onto Akshan as he triggers it).

    python tools/art/fx_akshan_revive.py [--review out.png]

The user, 2026-10-21: 「阿克尚现在的复活机制和英雄联盟一样吗 泉水秒复活？我一直在游戏里看不出什么效果」 - the add-on did revive
(league_akshan.log REVIVE: 92 in two sessions) but showed nothing: the ally comes back at his fountain a second later.
league_akshan plays this as league_akshan_w_revive: on Akshan the moment the Scoundrel falls, and on each revived ally
the tick he stands again. Drawn here on the game grid (1x pixels), symmetric left to right (the client never mirrors
an effect): a thin beam from above widening onto him, a ring of light at his feet, sparks rising as it fades. Written as
league/effects/league_akshan_rv (its own small sheet; the hero's fx sheets come from Codex's packs).
"""
import argparse
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

OUT = os.path.join(ROOT, "league", "effects", "league_akshan_rv")
W, H = 31, 72                  # the cell: the beam's full height over a 36-px unit, the ring under him
CX = W // 2
GROUND = H - 4                 # the ring's centre row (its bottom 3 rows under it)
WHITE = (255, 253, 232)
PALE = (255, 238, 160)
GOLD = (255, 205, 80)
AMBER = (236, 150, 40)
DEEP = (170, 92, 24)
SOLES = (0, 11)                # on the ground under a unit (import_mel_fx's)


def blank():
    return np.zeros((H, W, 4), np.uint8)


def put(a, x, y, c):
    for xx in {x, 2 * CX - x}:                  # symmetric left to right
        if 0 <= xx < W and 0 <= y < H:
            a[y, xx, :3] = c
            a[y, xx, 3] = 255


def beam(a, half, top, bottom):
    """A column `half` wide each side of the centre: white core, gold, amber, a deep edge."""
    for y in range(top, bottom + 1):
        for d in range(half + 1):
            c = WHITE if d <= half // 3 else PALE if d <= half // 2 else GOLD if d < half else AMBER
            put(a, CX + d, y, c)
        if half >= 2:
            put(a, CX + half + 1, y, DEEP)


def ring(a, rx, ry, c, edge=None):
    for t in np.linspace(0, np.pi, 90):
        x, y = int(round(CX + rx * np.cos(t))), int(round(GROUND + ry * np.sin(t)))
        put(a, x, y, c)
        put(a, x, int(round(GROUND - ry * np.sin(t))), edge or c)


def sparks(a, pts, c=PALE):
    for x, y in pts:
        put(a, CX + x, y, c)


def frames():
    out = []
    a = blank(); beam(a, 0, 0, H // 3); out.append((a, 50))
    a = blank(); beam(a, 1, 0, GROUND); ring(a, 4, 1, GOLD); out.append((a, 60))
    a = blank(); beam(a, 3, 0, GROUND); ring(a, 8, 2, GOLD, AMBER); out.append((a, 70))
    a = blank(); beam(a, 5, 0, GROUND); ring(a, 12, 3, PALE, GOLD); sparks(a, [(8, GROUND - 8), (11, GROUND - 14)]); out.append((a, 90))
    a = blank(); beam(a, 4, 0, GROUND); ring(a, 13, 3, GOLD, AMBER); sparks(a, [(9, GROUND - 14), (12, GROUND - 22), (7, GROUND - 28)]); out.append((a, 90))
    a = blank(); beam(a, 2, 6, GROUND); ring(a, 13, 3, AMBER); sparks(a, [(9, GROUND - 22), (12, GROUND - 32), (6, GROUND - 40)], GOLD); out.append((a, 90))
    a = blank(); beam(a, 0, 20, GROUND); sparks(a, [(9, GROUND - 30), (12, GROUND - 42), (5, GROUND - 50)], GOLD); out.append((a, 100))
    a = blank(); sparks(a, [(10, GROUND - 40), (6, GROUND - 56)], AMBER); out.append((a, 110))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    fr = frames()
    for k, (f, _) in enumerate(fr):
        assert (f == f[:, ::-1]).all(), f"frame {k + 1} is not symmetric"
    anchor = [(W - 1) / 2, GROUND + 3]          # the ring's bottom row on the unit's soles
    tags = {"w_revive": [(J.place(f, anchor, [SOLES]), ms) for f, ms in fr]}
    w, h = G.write_sheet(OUT, tags, share=True)
    print(f"league/effects/league_akshan_rv#sheet.png {w}x{h}: w_revive {len(fr)}f {sum(m for _, m in fr)}ms")
    if a.review:
        Z = 6
        img = Image.new("RGBA", ((W + 2) * Z * len(fr), H * Z), (60, 70, 60, 255))
        for k, (f, _) in enumerate(fr):
            img.alpha_composite(Image.fromarray(f).resize((W * Z, H * Z), Image.NEAREST), (k * (W + 2) * Z, 0))
        img.convert("RGB").save(a.review)
        print("review", a.review)


if __name__ == "__main__":
    main()

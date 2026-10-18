#!/usr/bin/env python3
"""A PPU hero's 1x tags made again from its hd_ frames, so the 1x frames show the hero the game draws.

    python tools/art/ppu_one.py --hero garen [--hero ashe ...]

league.dll draws a PPU hero from its hd_ frames (lo_ in the ban/pick UI), so the plain 1x tags are only the timing,
the fallback without the DLL - and what every other hero's preview clip draws when it brings the hero in as a foe or an
ally (tools/art/preview_*.py: frames_of). Heroes made dense by restyling or redrawing their old frames (league_garen,
league_ashe, league_soraka, league_yasuo) kept their old 1x drawings, so those clips showed the old models (the user,
2026-10-18, after league_darius's redo: 「还有所有设计诺手的gif图全要重做吧」「盖伦也是吧？」). Each 1x frame here: its
hd_ frame brought to one square a game pixel the way ppu_hd.add_lo brings it to the UI's density (pixel_down.pixelate,
centred), on the 1x frame's own rectangle - sizes, pivots and timing unchanged (ppu_hd.check: hd = PPU x 1x). Only
tags whose hd_ frames are drawn (ppu_hd.is_drawn): a tag scaled up from its 1x frames would feed on itself.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402
import pixel_down as D  # noqa: E402

G = P.G


def one_frame(b, w, h, k):
    """The hd_ frame b brought to 1/k, centred on a w x h frame."""
    f = np.zeros((h, w, 4), np.uint8)
    if not (b[..., 3] > 0).any():
        return f
    lo, (px, py) = D.pixelate(b, 1.0 / k, (b.shape[1] / 2, b.shape[0] / 2), D.edge_colour(b))
    ys, xs = np.nonzero(lo[..., 3] > 0)
    ox, oy = int(np.floor(w / 2 - px + 0.5)), int(np.floor(h / 2 - py + 0.5))
    ok = (ys + oy >= 0) & (ys + oy < h) & (xs + ox >= 0) & (xs + ox < w)
    f[ys[ok] + oy, xs[ok] + ox] = lo[ys[ok], xs[ok]]
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", action="append", required=True)
    a = ap.parse_args()
    for hero in a.hero:
        stem = os.path.join(P.ROOT, "league", "champions", f"league_{hero}")
        sheet = P.read_sheet(stem)
        k = P.PPU[hero]
        done = []
        for tag in [t for t in sheet if P.plain(t)]:
            if P.PREFIX + tag not in sheet or not P.is_drawn(hero, tag):
                continue
            sheet[tag] = [(one_frame(b, one.shape[1], one.shape[0], k), ms)
                          for (one, ms), (b, _) in zip(sheet[tag], sheet[P.PREFIX + tag])]
            done.append(tag)
        problems = P.check(hero, sheet)
        if problems:
            sys.exit(f"{hero}: {problems[:5]}")
        w, h = G.write_sheet(stem, sheet)
        print(f"league_{hero}: 1x {', '.join(done)} from hd_ (PPU {k}); sheet {w}x{h}")


if __name__ == "__main__":
    main()

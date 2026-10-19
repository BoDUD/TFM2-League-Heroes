#!/usr/bin/env python3
"""A PPU hero's 1x tags made again from its hd_ frames, so the 1x frames show the hero the game draws.

    python tools/art/ppu_one.py --hero garen [--hero ashe ...]

league.dll draws a PPU hero from its hd_ frames (lo_ in the ban/pick UI), so the plain 1x tags are only the timing,
the fallback without the DLL - and what every other hero's preview clip draws when it brings the hero in as a foe or an
ally (tools/art/preview_*.py: frames_of). Heroes made dense by restyling or redrawing their old frames (league_garen,
league_ashe, league_soraka, league_yasuo) kept their old 1x drawings, so those clips showed the old models (the user,
2026-10-18, after league_darius's redo: 「还有所有设计诺手的gif图全要重做吧」「盖伦也是吧？」). Each 1x frame here: its
hd_ frame brought to one square a game pixel the way ppu_hd.add_lo brings it to the UI's density (pixel_down.pixelate,
centred), on the 1x frame's own rectangle - pivots and timing unchanged (ppu_hd.check: hd = PPU x 1x). Only
tags whose hd_ frames are drawn (ppu_hd.is_drawn): a tag scaled up from its 1x frames would feed on itself.

2026-10-19 (players without league.dll - Mac / Linux, code mods off, another game build - saw the old Zeri, Karma and
Vladimir): a hero the DLL shows smaller (hd.rs SIZES under 1: Corki, Braum, Nilah) is brought down by PPU / size, the
factor the DLL shows it at (Hero::shown) - its dense frames sit lower for that size (ppu_restyle lift_sq), so at 1 / PPU
its soles sank 1-3 px into the ground; one shown bigger stays at 1 / PPU (its 1x frame could not hold it within
ppu_hd.check: hd_ at least PPU x the 1x frame). A drawing that comes out bigger than the 1x frame grows the frame by
whole pixels at both ends (the centre, the pivot, kept) as far as ppu_hd.check allows - hd_ / lo_ at least PPU x /
UI_PPU x the 1x size, hd_idle exactly PPU x as wide (the DLL's test) - instead of losing the propeller, the spear or the
shield off its edge; the squares that still do not fit are reported.
"""
import argparse
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402
import pixel_down as D  # noqa: E402

G = P.G


def sizes():
    """addons/league_main/src/hd.rs SIZES -> {hero: size} (league_ and tft_ ids alike)."""
    src = open(os.path.join(P.ROOT, "addons", "league_main", "src", "hd.rs"), encoding="utf-8").read()
    m = re.search(r"pub const SIZES[^=]*=\s*&\[(.*?)\];", src, re.S)
    return {h: float(v) for h, v in re.findall(r'\("(?:league|tft)_(\w+)",\s*([0-9.]+)\)', m.group(1))} if m else {}


def lengths(n, k, dense, lo, exact):
    """The 1x lengths (n, n + 2, ...) a frame side may take: PPU x it within the hd_ side (exactly it, for hd_idle's
    width), UI_PPU x it within the lo_ side."""
    out = []
    for m in range(n, n + 400, 2):
        d, u = round(m * k), round(m * P.UI_PPU)
        if d > dense or u > lo:
            break
        if d == dense or not exact:
            out.append(m)
    return out or [n]


def one_frame(b, w, h, f, ws, hs):
    """The hd_ frame b brought to f x its size, centred on a frame of the first width of ws / height of hs it fits
    (the last when none does). -> (frame, squares left off)."""
    if not (b[..., 3] > 0).any():
        return np.zeros((h, w, 4), np.uint8), 0
    lo, (px, py) = D.pixelate(b, f, (b.shape[1] / 2, b.shape[0] / 2), D.edge_colour(b))
    ys, xs = np.nonzero(lo[..., 3] > 0)

    def fits(n, p, v):
        o = int(np.floor(n / 2 - p + 0.5))
        return o, v.min() + o >= 0 and v.max() + o < n

    W = next((n for n in ws if fits(n, px, xs)[1]), ws[-1])
    H = next((n for n in hs if fits(n, py, ys)[1]), hs[-1])
    ox, oy = fits(W, px, xs)[0], fits(H, py, ys)[0]
    f_ = np.zeros((H, W, 4), np.uint8)
    ok = (ys + oy >= 0) & (ys + oy < H) & (xs + ox >= 0) & (xs + ox < W)
    f_[ys[ok] + oy, xs[ok] + ox] = lo[ys[ok], xs[ok]]
    return f_, int((~ok).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", action="append", required=True)
    a = ap.parse_args()
    size_of = sizes()
    for hero in a.hero:
        stem = P.stem_of(hero)
        sheet = P.read_sheet(stem)
        k = P.PPU[hero]
        shown = k / min(1.0, size_of.get(hero, 1.0))
        done, grown, lost = [], [], []
        for tag in [t for t in sheet if P.plain(t)]:
            if P.PREFIX + tag not in sheet or not P.is_drawn(hero, tag):
                continue
            frames = []
            for i, ((one, ms), (b, _), (c, _)) in enumerate(zip(sheet[tag], sheet[P.PREFIX + tag], sheet[P.LO + tag])):
                h, w = one.shape[:2]
                ws = lengths(w, k, b.shape[1], c.shape[1], tag == "idle")
                hs = lengths(h, k, b.shape[0], c.shape[0], False)
                f, off = one_frame(b, w, h, 1.0 / shown, ws, hs)
                if f.shape[:2] != (h, w):
                    grown.append(f"{tag}[{i}] {w}x{h}->{f.shape[1]}x{f.shape[0]}")
                if off:
                    lost.append(f"{tag}[{i}] {off}")
                frames.append((f, ms))
            sheet[tag] = frames
            done.append(tag)
        problems = P.check(hero, sheet)
        if problems:
            sys.exit(f"{hero}: {problems[:5]}")
        w, h = G.write_sheet(stem, sheet)
        print(f"{P.hero_id(hero)}: 1x {', '.join(done)} from hd_ (PPU {k}, shown at 1 / {shown:.3f}); sheet {w}x{h}")
        if grown:
            print(f"  frames grown: {len(grown)} ({', '.join(grown[:6])}{' ...' if len(grown) > 6 else ''})")
        if lost:
            print(f"  squares still off the frame: {', '.join(lost)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""league_bard's sheet from the frames on the design's grid (assets/source/bard/frames, tools/art/import_bard_strips.py).

    python tools/art/rig_bard.py [--review DIR]

The frames are drawn at 1.5 squares a game pixel (one design square a canvas pixel); every tag's 1x frame (the only
tags in the sheet) is the canvas brought to 1 square a game pixel by pixel_down.pixelate (each 1x square the mean of
its 1.5 x 1.5 canvas pixels snapped to the frame's own colours, the outline rules), centred on the pivot's square;
the pivot: the standing column's centre, FEET 1x rows above the soles (the pack's 128-canvas heroes).
Bard was a dense hero first (PPU 1.5, hd_ / lo_ tags, league.dll 0.6.66); the user, 2026-10-14: 「巴德在游戏里像素太高」,
picked 1.0 - as coarse as the base champions - from a true-scale sheet: no dense frames, not in league.dll's HEROES.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402

FRAMES = os.path.join(ROOT, "assets", "source", "bard", "frames")
STEM = os.path.join(ROOT, "league", "champions", "league_bard")
PPU = 1.5                       # the frames' squares a game pixel
FEET = 11
ORDER = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]


def pivot(meta):
    """The pivot's centre on the canvas (dense px): the standing column's centre, (FEET + 0.5) 1x rows above the soles'
    bottom edge."""
    pc, sole = meta["standing"]
    return pc + 0.5, sole + 1 - (FEET + 0.5) * PPU


def one_x(can, p):
    """The 1x frame: pixelate at 1 / PPU on a grid whose square round the pivot is centred on it; odd size, the pivot's
    square in the middle."""
    px, py = p
    lo, (nx0, ny0) = PD.pixelate(can, 1 / PPU, (px - PPU / 2, py - PPU / 2), PD.edge_colour(can))
    ys, xs = np.nonzero(lo[..., 3])
    hw, hh = max(nx0 - xs.min(), xs.max() - nx0), max(ny0 - ys.min(), ys.max() - ny0)
    out = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    out[ys - ny0 + hh, xs - nx0 + hw] = lo[ys, xs]
    out, _, _ = G.complete_outline(out, color=PD.edge_colour(can), feet=hh + FEET)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's 1x frames at 6x on magenta here")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(FRAMES, "frames.json"), encoding="utf-8"))
    p = pivot(meta)
    sheet = {}
    for tag in ORDER:
        ones = []
        for k, ms in enumerate(meta["ms"][tag], 1):
            can = np.asarray(Image.open(os.path.join(FRAMES, f"{tag}_{k}.png")).convert("RGBA")).copy()
            one = one_x(can, p)
            ones.append((one, round(ms, 3)))
        sheet[tag] = ones
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 6
            tiles = [Image.fromarray(o) for o, _ in ones]
            w = max(t.width for t in tiles)
            hh = max(t.height for t in tiles)
            big = Image.new("RGBA", (len(tiles) * w * Z, hh * Z), (255, 0, 255, 255))
            for j, t in enumerate(tiles):
                big.alpha_composite(t.resize((t.width * Z, t.height * Z), Image.NEAREST), (j * w * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"bard_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_bard#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()

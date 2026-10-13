#!/usr/bin/env python3
"""league_bard's sheets from the frames on the design's grid (assets/source/bard/frames, tools/art/import_bard_strips.py).

    python tools/art/rig_bard.py [--review DIR]

The frames are drawn at the game's own density (PPU 1.5: one design square = one dense pixel, 1.5 a game pixel - the
user's pick, league_galio's), so for every frame:
  * the dense frame (ppu_hd.py's drawn strip, assets/source/ppu/bard_<tag>.png + .json) is the canvas itself round the
    pivot, no resampling: a frame of round(1.5 x the 1x frame's size) - grown alike at both ends where the drawing
    needs more - with the pivot at its centre;
  * the 1x frame (the sheet's plain tags) is the canvas brought to 1 square a game pixel by pixel_down.pixelate (each
    1x square the mean of its 1.5 x 1.5 dense pixels snapped to the frame's own colours, the outline rules), centred on
    the pivot's square;
  * the pivot: the standing column's centre, FEET 1x rows above the soles (the pack's 128-canvas heroes).
Then `python tools/art/ppu_hd.py --hero bard` adds the hd_ / lo_ tags to the sheet from the strips written here.
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
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")
PPU = 1.5
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


def dense(can, one, p):
    """The game's frame: the canvas on a frame of round(PPU x the 1x frame's size), grown alike at both ends where the
    drawing needs more, the pivot at its centre."""
    lx, ly = p
    W, H = round(one.shape[1] * PPU), round(one.shape[0] * PPU)
    ys, xs = np.nonzero(can[..., 3])
    while W / 2 < max(lx - xs.min(), xs.max() + 1 - lx):
        W += 2
    while H / 2 < max(ly - ys.min(), ys.max() + 1 - ly):
        H += 2
    f = np.zeros((H, W, 4), np.uint8)
    ox, oy = int(np.floor(W / 2 - lx + 0.5)), int(np.floor(H / 2 - ly + 0.5))
    f[ys + oy, xs + ox] = can[ys, xs]
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's 1x and dense frames at 4x on magenta here")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(FRAMES, "frames.json"), encoding="utf-8"))
    p = pivot(meta)
    sheet = {}
    for tag in ORDER:
        ones, hds = [], []
        for k, ms in enumerate(meta["ms"][tag], 1):
            can = np.asarray(Image.open(os.path.join(FRAMES, f"{tag}_{k}.png")).convert("RGBA")).copy()
            one = one_x(can, p)
            ones.append((one, round(ms, 3)))
            hds.append(dense(can, one, p))
        sheet[tag] = ones
        H = max(h.shape[0] for h in hds)
        strip = np.zeros((H, sum(h.shape[1] + 1 for h in hds) - 1, 4), np.uint8)
        x = 0
        for h in hds:
            strip[:h.shape[0], x:x + h.shape[1]] = h
            x += h.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(PPU_SRC, f"bard_{tag}.png"))
        with open(os.path.join(PPU_SRC, f"bard_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds]}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 4
            tiles = [Image.fromarray(h) for h in hds]
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

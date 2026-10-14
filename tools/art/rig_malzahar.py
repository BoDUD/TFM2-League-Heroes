#!/usr/bin/env python3
"""Malzahar's game sheets from his dense frames (tools/art/import_malzahar_strips.py -> assets/source/malzahar/frames) -
league_kindred's way (tools/art/rig_kindred.py).

    python tools/art/rig_malzahar.py [--review DIR]

The frames are drawn at PPU 2.2 (one design square a dense pixel: the user's density, league_zeri's look), on a canvas
whose standing column is PIV_C and ground row SOLE (frames.json); the pivot: the standing column's centre, FEET 1x rows
above the ground row's bottom edge. He floats: the idle's boots hang 6 squares over the ground row (2.7 game px), the
death lies on it.
Writes assets/source/ppu/orig/malzahar_<tag>.png / .json (the dense frames, each round(PPU x its 1x frame) round the
pivot) and league/champions/league_malzahar#sheet.png / #anim.fanim (the 1x tags: each 1x pixel the commonest colour
of its squares; the fallback without league.dll). Then tools/art/ppu_restyle.py --hero malzahar (RESTYLE: the outline
grown to about a game pixel, the frames lifted for hd.rs SIZES 1.15) and tools/art/ppu_hd.py --hero malzahar.
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
import strips as G  # noqa: E402

PPU = 2.2                         # dense squares a game pixel
FEET = 11                         # 1x rows from the pivot down to the ground row (the pack's 128-canvas heroes)
FRAMES = os.path.join(ROOT, "assets", "source", "malzahar", "frames")
STEM = os.path.join(ROOT, "league", "champions", "league_malzahar")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
ORDER = ["idle", "run", "attack", "skill", "skill2", "ult", "ult_loop", "hit", "dead"]


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def one_of(can, px, py, hw, hh, need=0.5):
    """The 1x frame (2 hw + 1 by 2 hh + 1, centred on (px, py)): every pixel the commonest colour of the dense squares
    under it, clear when fewer than `need` of them are drawn."""
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_hd(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


def down(can, piv, sole):
    """The dense canvas -> (the 1x frame centred on the pivot, the dense frame round(PPU x its size))."""
    px, py = piv + 0.5, sole + 1 - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh))[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    return one, crop_hd(can, px, py, W, H)


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's 1x frames at 6x here")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(FRAMES, "frames.json"), encoding="utf-8"))
    piv, sole = meta["standing"]
    sheet = {}
    os.makedirs(ORIG, exist_ok=True)
    for tag in ORDER:
        ones, hds = [], []
        for k, ms in enumerate(meta["ms"][tag], 1):
            one, hd = down(rgba(os.path.join(FRAMES, f"{tag}_{k}.png")), piv, sole)
            ones.append((one, float(ms)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(os.path.join(ORIG, f"malzahar_{tag}.png"))
        with open(os.path.join(ORIG, f"malzahar_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 6
            tiles = [Image.fromarray(o) for o, _ in ones]
            w = max(t.width for t in tiles)
            h = max(t.height for t in tiles)
            big = Image.new("RGBA", (len(tiles) * w * Z, h * Z), (96, 112, 96, 255))
            for j, t in enumerate(tiles):
                big.alpha_composite(t.resize((t.width * Z, t.height * Z), Image.NEAREST), (j * w * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"malzahar_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_malzahar#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()

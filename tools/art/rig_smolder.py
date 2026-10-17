#!/usr/bin/env python3
"""league_smolder's sheets from the frames on the design's grid (assets/source/smolder/frames,
tools/art/import_smolder_strips.py) - league_bard's dense-era way (rig_bard.py at 6ef47fba), Malzahar's 1x downscale.

    python tools/art/rig_smolder.py [--review DIR]

The frames are drawn at the game's own density (PPU 1.5: one design square = one dense pixel, 1.5 a game pixel - the
user's pick), so for every frame:
  * the dense frame (ppu_hd.py's drawn strip, assets/source/ppu/smolder_<tag>.png + .json) is the canvas itself round
    the pivot, no resampling: a frame of round(1.5 x the 1x frame's size) - grown alike at both ends where the drawing
    needs more - with the pivot at its centre;
  * the 1x frame (the sheet's plain tags: the fallback without league.dll) - every 1x pixel the commonest colour of
    the dense squares under it (rig_malzahar.one_of: no means, so no muddy new colours), the outline closed, centred on
    the pivot's pixel;
  * the pivot: the standing column's centre, FEET 1x rows above the soles' bottom edge (the pack's 128-canvas heroes).
Then `python tools/art/ppu_hd.py --hero smolder` adds the hd_ / lo_ tags to the sheet from the strips written here.
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

FRAMES = os.path.join(ROOT, "assets", "source", "smolder", "frames")
STEM = os.path.join(ROOT, "league", "champions", "league_smolder")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")
PPU = 1.5
FEET = 11
ORDER = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]
K = (7, 0, 16)


def pivot(meta):
    """The pivot's centre on the canvas (dense px): the standing column's centre, (FEET + 0.5) 1x rows above the soles'
    bottom edge."""
    pc, sole = meta["standing"]
    return pc + 0.5, sole + 1 - (FEET + 0.5) * PPU


def one_x(can, p, need=0.5):
    """The 1x frame (odd size, the pivot's pixel in the middle): every pixel the commonest colour of the dense squares
    under it (the outline where a third or more of them is outline), clear when fewer than `need` of them are drawn."""
    px, py = p
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
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
            drawn = blk[blk[:, 3] > 0][:, :3]
            dark = (drawn.astype(int).sum(1) < 120)
            if dark.sum() * 3 >= len(drawn):
                one[j, i, :3] = K
            else:
                cols, n = np.unique(drawn[~dark], axis=0, return_counts=True)
                one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    one, _, _ = G.complete_outline(one, color=K, feet=hh + FEET)
    return one


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
    ap.add_argument("--review", help="write every tag's 1x and dense frames at 4x here")
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
        Image.fromarray(strip).save(os.path.join(PPU_SRC, f"smolder_{tag}.png"))
        with open(os.path.join(PPU_SRC, f"smolder_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds]}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 4
            for name, tiles in (("hd", [Image.fromarray(h) for h in hds]), ("1x", [Image.fromarray(o) for o, _ in ones])):
                w = max(t.width for t in tiles)
                hh = max(t.height for t in tiles)
                z = Z if name == "hd" else 6
                big = Image.new("RGBA", (len(tiles) * w * z, hh * z), (150, 160, 150, 255))
                for j, t in enumerate(tiles):
                    big.alpha_composite(t.resize((t.width * z, t.height * z), Image.NEAREST), (j * w * z, 0))
                big.convert("RGB").save(os.path.join(a.review, f"smolder_{name}_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_smolder#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()

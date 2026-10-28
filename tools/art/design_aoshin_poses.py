#!/usr/bin/env python3
"""Ao Shin's Codex poses (assets/source/aoshin/codex_poses: POSE_PROMPTS.md, 15 key poses of his own TFT clips on his
design, 2026-10-28) at the design's density.

    python tools/art/design_aoshin_poses.py --sheet DIR    # all poses beside the design (4x)
    python tools/art/design_aoshin_poses.py                # writes assets/source/aoshin/hd/pose_<name>.png (+ .json)

Codex kept the asked grid this time (every pose on 12 px squares from the canvas corner, alpha 0 / 255, every colour
one of the design's: checked 2026-10-28) and drew each pose as tall as its reference, so a pose is read back square for
square (the middle pixel of each 12 x 12 square) - no reduction. The small holes are closed (design_silco_poses.
close_gaps) and loose specks dropped. Each pose's json keeps where its reference put his hips (Tail0, the root of his
body) in it: the pack set every pose's hips on the design's column, except the poses it moved back inside the canvas
(MOVED: pack_aoshin_poses' MARGIN shift, worked out again from the same model and clips), so the rig places every
frame by that point and his lowest row (all on the pack's ground line).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_aoshin_poses as PA  # noqa: E402
from design_aoshin_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aoshin", "codex_poses", "aoshin-poses")
OUT = os.path.join(ROOT, "assets", "source", "aoshin", "hd")
HIPS_X = 657                  # the pack's hip column on the canvas (pack_aoshin_poses: the design's column 39.75)
MOVED = {"a_coil": 62.1, "a_lunge": 128.1, "a_back": 69.1, "run1": 124.3, "run2": 135.0, "run3": 120.2,
         "run4": 109.0, "d_back": 38.1}   # canvas px the pack moved a pose right to keep it inside (MARGIN 60)
SPECK = 4                     # parts apart from the figure smaller than this are dropped
NAMES = list(PA.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def read(name):
    """The pose square for square -> (figure, the hips' column and the ground row in it)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"aoshin-pose-{name}.png"))).convert("RGBA"))
    h = PA.PX // 2
    g = a[h::PA.PX, h::PA.PX][:PA.CANVAS // PA.PX, :PA.CANVAS // PA.PX].copy()
    g[..., 3] = np.where(g[..., 3] >= 128, 255, 0)
    g[g[..., 3] == 0] = 0
    g = close_gaps(g, design())
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    hips = (HIPS_X + MOVED.get(name, 0.0)) / PA.PX
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (round(float(hips - xs.min()), 2), int(PA.SOLE_Y // PA.PX - ys.min()))


def big4(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    figs = {n: read(n) for n in names}
    for n, (fig, piv) in figs.items():
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, hips / ground at {piv}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 4] for i in range(0, len(tiles), 4)]
        for j, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big4(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"aoshin_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"hips": piv[0], "ground": piv[1]}, fh)


if __name__ == "__main__":
    main()

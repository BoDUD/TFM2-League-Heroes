#!/usr/bin/env python3
"""Nomsy's Codex poses (assets/source/nomsy/codex_poses: POSE_PROMPTS.md, 20 key poses of her own TFT clips on her
design, 2026-10-29) on the design's palette, gaps closed.

    python tools/art/design_nomsy_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_nomsy_poses.py                  # writes assets/source/nomsy/hd/pose_<name>.png (+ .json)

Codex kept the asked grid this time: every pose is exactly 7 x 7 px squares from the canvas corner (its pixel_1x/ is the
1254 canvas read one square a pixel, 179 x 179, checked square for square 2026-10-29), at the design's density (it
evened the poses' bulk by the pink belly's area: 1931-2360 squares against the design's 2135). So a pose is taken 1:1
from pixel_1x/, its colours snapped to the design's own (nearest in Lab: Codex read its squares back on a palette of its
own, none of them the design's), the one-square cracks and small holes closed (design_silco_poses.close_gaps) and loose
specks dropped. Each pose's json keeps where PIVOT fell in it: the pack drew every reference with her root on one canvas
column and her lowest point on the ground line, and Codex placed each pose by its body over its reference (its HANDOFF),
so the rig stands the frames by it.
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
import pack_nomsy_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_nomsy_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nomsy", "codex_poses", "nomsy-poses", "pixel_1x")
OUT = os.path.join(ROOT, "assets", "source", "nomsy", "hd")
# the pack's root column on the canvas (pack_nomsy_poses: the design centred on whole squares, her root on its column
# 61.3 -> canvas x 604) and the ground line, in squares
PIVOT = (604 / PK.PX, PK.SOLE_Y / PK.PX)
SPECK = 6                     # parts apart from the figure smaller than this are dropped
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def snap(a, d):
    """Every opaque square to the nearest of the design's colours (in Lab)."""
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    op = a[..., 3] > 0
    lab_p = PD._lab(pal.astype(float))
    lab_a = PD._lab(a[op][:, :3].astype(float))
    idx = np.argmin(((lab_a[:, None, :] - lab_p[None, :, :]) ** 2).sum(-1), axis=1)
    out = np.zeros_like(a)
    out[op, :3] = pal[idx]
    out[op, 3] = 255
    return out


def read(name):
    """The pose on the design's palette -> (figure, PIVOT's square in it)."""
    d = design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"nomsy-pose-{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    g = close_gaps(snap(a, d), d)
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (round(PIVOT[0] - xs.min()), round(PIVOT[1] - ys.min()))


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
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, pivot at {piv}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
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
            path = os.path.join(a.sheet, f"nomsy_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]]}, fh)


if __name__ == "__main__":
    main()

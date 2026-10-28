#!/usr/bin/env python3
"""The Ancient Krug's Codex poses (assets/source/krug/codex_poses: POSE_PROMPTS.md, 15 key poses of his own TFT clips on
his design, 2026-10-28) at the design's density, on the design's palette, gaps closed.

    python tools/art/design_krug_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_krug_poses.py                  # writes assets/source/krug/hd/pose_<name>.png (+ .json)

Codex did not keep the asked grid this time (its VALIDATION.md: no pose on the 12 px grid; regrid finds 10 px squares
in most, 12 in e_shell / r_crouch / run1 / run3, 8 in d_crack) and drew every pose bigger than the pack's reference:
a_back (back on all fours, close to the design) 1020 canvas px tall against the design's 76 rows x 12 = 912. The poses
do share one body size between them (Codex drew each over its reference, which all had the one scale), so every pose
is brought down by ONE factor, ROW_PX canvas px a game row (a_back -> the design's 76 rows), with pixel_down.pixelate
(the reduction the size review and design_krug_model used, so the frames read like the design) about one canvas
point PIVOT (the pack's pelvis column on the ground line), snapped to the design's own colours. Then the small holes
and cracks closed (design_silco_poses.close_gaps) and loose specks dropped - d_down's flying chip of boulder is a part
of the pose (the reference's), kept. Each pose's json keeps where PIVOT fell in it (the rig places the frames by it:
they all stand where their references did) and the head match is not needed: Codex kept the design's small face in
every pose (looked at 12x, 2026-10-28).
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
import pixel_down as PD  # noqa: E402
import pack_krug_poses as PK  # noqa: E402
from design_krug_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "krug", "codex_poses", "krug-poses")
OUT = os.path.join(ROOT, "assets", "source", "krug", "hd")
ROW_PX = 1020 / 76            # canvas px a game row: a_back's 1020 px = the design's 76 rows
PIVOT = (PK.CANVAS // 2, PK.SOLE_Y)
SCALE = {}                    # pose -> its own factor on ROW_PX (none needed so far)
SPECK = 6                     # parts apart from the figure smaller than this are dropped
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def read(name):
    """The pose at the design's density -> (figure, PIVOT's square in it)."""
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(float)
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"krug-pose-{name}.png"))).convert("RGBA")).copy()
    op = a[..., 3] >= 128
    a[..., 3] = np.where(op, 255, 0)
    a[~op, :3] = 0
    k = SCALE.get(name, 1.0) / ROW_PX
    g, (px, py) = PD.pixelate(a, k, PIVOT, PD.edge_colour(d), pal)
    g[..., 3] = np.where(g[..., 3] > 0, 255, 0)
    g = close_gaps(g, d)
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (int(px - xs.min()), int(py - ys.min()))


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
            path = os.path.join(a.sheet, f"krug_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]], "row_px": round(ROW_PX / SCALE.get(n, 1.0), 3)}, fh)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Idas's run (Codex's run2: assets/source/idas/RUN_PROMPTS.md, TFT's own low bound in 8 frames, 2026-10-30) at the
design's density, on its colours, gaps closed.

    python tools/art/design_idas_run.py [--sheet DIR]   # writes assets/source/idas/hd/run<k>.png (+ .json); --sheet: 3x

Codex drew each frame whole with image_gen and read it back itself on its 7 px squares (codex_run2/idas-run2/pixel_1x:
179 x 179, the design's colours, alpha 0 / 255, every figure scaled to the same box - x 31-158, its lowest row 167 -
so the snout and the tail tip stand still and the body bobs). But it drew her small: the crest is 19-24 squares wide
against the design's 32 (the head 0.65 of the design's; regrid-free count on its pixel_1x, 2026-10-30). So each frame
is brought up SCALE (1.5: the head the design's again) the pixel-art way - EPX twice (4x, edges kept) then pixel_down
.pixelate back to 1.5x on the design's colours - its one-square cracks and small holes closed
(design_silco_poses.close_gaps), the thin slits of ground inside the body shaded (SLIT) and loose specks dropped. Its
json keeps the pivot: the figure's middle column (her hips: every frame has the same box) and its lowest row.
Codex's own check (its HANDOFF): the leading leg is right in frames 2-4 (far) and 6-8 (near), frame 5 nearly crossing,
frame 1 the near leg still 22 squares ahead (not the asked crossing) - so the legs swap between frames 1 and 2 and 5 and 6.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_idas_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "idas", "codex_run2", "idas-run2", "pixel_1x")
OUT = os.path.join(ROOT, "assets", "source", "idas", "hd")
SCALE = 1.5
SPECK = 6                     # parts apart from the figure smaller than this are dropped
N = 8
# Codex's frames leave thin slits of ground inside the body (between the neck and the forward wing-arm, under the jaw,
# along the thigh: gap-check, 21-77 squares each, 2026-10-30): every enclosed clear patch no thicker than SLIT (its
# widest inscribed radius, squares) takes the design's darkest body brown; the wide gaps between the legs stay open
SLIT = 2.5
SHADE = (67, 29, 7)           # #431D07, the design's darkest gold-brown


def epx(a):
    """Scale2x (EPX): every pixel to 2 x 2, a corner taking a neighbour's colour where the two edges by it agree."""
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    up, right, left, down = p[:-2, 1:-1], p[1:-1, 2:], p[1:-1, :-2], p[2:, 1:-1]

    def eq(x, y):
        return (x == y).all(-1)
    out = np.zeros((a.shape[0] * 2, a.shape[1] * 2, 4), a.dtype)
    out[0::2, 0::2] = np.where((eq(left, up) & ~eq(left, down) & ~eq(up, right))[..., None], up, a)
    out[0::2, 1::2] = np.where((eq(up, right) & ~eq(up, left) & ~eq(right, down))[..., None], right, a)
    out[1::2, 0::2] = np.where((eq(down, left) & ~eq(down, right) & ~eq(left, up))[..., None], left, a)
    out[1::2, 1::2] = np.where((eq(right, down) & ~eq(right, up) & ~eq(down, left))[..., None], down, a)
    return out


def design():
    return np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))


def read(k, d):
    """Frame k at the design's density -> (figure, pivot (column, row) in it)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"idas-run-run{k}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    ys, xs = np.nonzero(a[..., 3] > 0)
    pivot = ((xs.min() + xs.max() + 1) / 2, ys.max() + 1)          # the box's middle, the soles' bottom edge
    big = epx(epx(a))
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(float)
    g, (px, py) = PD.pixelate(big, SCALE / 4, (pivot[0] * 4, pivot[1] * 4), PD.edge_colour(d), pal=pal)
    g = close_gaps(np.asarray(g).copy(), d)
    op = g[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    hl, hn = ndimage.label(holes)
    for j in range(1, hn + 1):
        h = hl == j
        if ndimage.distance_transform_edt(h).max() <= SLIT:
            g[h] = (*SHADE, 255)
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (int(round(px - xs.min())), int(ys.max() - ys.min()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    d = design()
    figs = {k: read(k, d) for k in range(1, N + 1)}
    for k, (fig, piv) in figs.items():
        print(f"run{k} {fig.shape[1]} x {fig.shape[0]}, pivot at {piv}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 3
        W = max(f.shape[1] for f, _ in figs.values()) * z + 12
        H = max(f.shape[0] for f, _ in figs.values()) * z + 12
        sheet = Image.new("RGBA", (W * 2, H * 4), (90, 96, 90, 255))
        for i, (fig, _) in enumerate(figs.values()):
            im = Image.fromarray(np.repeat(np.repeat(fig, z, 0), z, 1))
            sheet.alpha_composite(im, ((i % 2) * W, (i // 2) * H + H - 12 - im.height))
        path = os.path.join(a.sheet, "idas_run.png")
        sheet.convert("RGB").save(lp(path))
        print(path)
        return
    for k, (fig, piv) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"run{k}.png")))
        with open(lp(os.path.join(OUT, f"run{k}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]]}, fh)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Illaoi's legs redo (assets/source/illaoi/codex_legs: LEGS_PROMPTS.md, Codex's redraw of 7 poses with the design's
chibi legs under the upper bodies tools/art/pack_illaoi_legs.py laid on the canvas; the runs alternating) read back and
joined to those upper bodies square for square (the Ivern way, design_ivern_legs.py).

    python tools/art/design_illaoi_legs.py --sheet DIR      # every pose: the design, the first readback, the join (5x)
    python tools/art/design_illaoi_legs.py                  # writes hd/pose_<name>.png (+ .json: head_at, ground)

Codex drew each picture on the guide's own grid (12 px squares from the canvas corner, the ground on row 100). Each is
read on that grid (a square opaque when most of it is, the median colour - design_shyvana_poses.sample_grid), its
colours snapped to the design's (Lab). The join keeps every square of the guide's upper body (where it went on the
canvas: assets/source/illaoi/codex_legs_guides.json) and takes from the redo only the squares that are not the upper
body's and lie in the cut-away zone (pack_illaoi_legs.cut moved with the body, grown GROW squares) or within REACH squares
of the leg skeletons - the legs, the skirt's and the loincloth's hems and what the old legs hid; loose specks go, the outline is closed.
The pose's json keeps the head box (from the first readback, moved with the body) and the ground row - the guide's for a
pose in the air, for one on the ground the lowest square round the skeletons' ankles and toes (Codex's feet come a row
or three off the guide's line) - so rig_illaoi stands her boots on the ground.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_shyvana_poses as SP  # noqa: E402  sample_grid, finish
import pack_illaoi_legs as L  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_illaoi_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "illaoi")
REDO = os.path.join(SRC, "codex_legs", "illaoi-legs")
OUT = os.path.join(SRC, "hd")
FIRST = os.path.join(SRC, "hd_first")          # the first readbacks (long legs), kept for the guides
GROW = 2
REACH = 5.0
FOOT = 5.0                       # squares round a skeleton's ankle and toe where its foot is looked for
SPECK = 6


def redo(name):
    for d in (REDO, os.path.join(REDO, "raw")):
        for fn in (f"illaoi-legs-{name}.png", f"illaoi-legs-{name}-raw.png"):
            p = os.path.join(d, fn)
            if os.path.isfile(lp(p)):
                return np.asarray(Image.open(lp(p)).convert("RGBA"))
    return None


def first(name):
    path = os.path.join(FIRST, f"pose_{name}.png")
    if not os.path.isfile(lp(path)):
        path = os.path.join(OUT, f"pose_{name}.png")
    with open(lp(path[:-4] + ".json"), encoding="utf-8") as f:
        meta = json.load(f)
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy(), meta


def near_lines(shape, legs, reach):
    """Squares within reach of the leg skeleton polylines (canvas squares)."""
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    px, py = xx + 0.5, yy + 0.5
    best = np.full(shape, np.inf)
    for pts in legs.values():
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            vx, vy = bx - ax, by - ay
            L2 = vx * vx + vy * vy or 1e-9
            t = np.clip(((px - ax) * vx + (py - ay) * vy) / L2, 0, 1)
            d = (px - ax - t * vx) ** 2 + (py - ay - t * vy) ** 2
            best = np.minimum(best, d)
    return best <= reach * reach


def join(name, design):
    """(the joined pose on the canvas grid, the ground row in it, the canvas offset of the first readback in it)."""
    keep, (ox, oy), legs = L.guide(name)
    _, cutm, _ = L.cut(name)
    G = L.COLS + 2
    can = np.zeros((G, G, 4), np.uint8)
    ys, xs = np.nonzero(keep[..., 3] > 0)
    ok = (ys + oy >= 0) & (ys + oy < can.shape[0]) & (xs + ox >= 0) & (xs + ox < can.shape[1])
    can[ys[ok] + oy, xs[ok] + ox] = keep[ys[ok], xs[ok]]
    body = can[..., 3] > 0
    r = redo(name)
    read, (ci, cj) = SP.sample_grid(r, float(L.PX), 0.0, 0.0)      # the guide's grid from the canvas corner
    red = np.zeros_like(can)
    h, w = read.shape[:2]
    y0, x0 = -cj, -ci                                              # read's (0, 0) is canvas square (x0, y0)
    yy0, xx0 = max(0, y0), max(0, x0)
    yy1, xx1 = min(can.shape[0], y0 + h), min(can.shape[1], x0 + w)
    red[yy0:yy1, xx0:xx1] = read[yy0 - y0:yy1 - y0, xx0 - x0:xx1 - x0]
    red = snap(red, design)
    zone = np.zeros(can.shape[:2], bool)
    ys, xs = np.nonzero(cutm)
    ok = (ys + oy >= 0) & (ys + oy < can.shape[0]) & (xs + ox >= 0) & (xs + ox < can.shape[1])
    zone[ys[ok] + oy, xs[ok] + ox] = True
    zone = ndimage.binary_dilation(zone, iterations=GROW) | near_lines(can.shape[:2], legs, REACH)
    take = zone & ~body & (red[..., 3] > 0)
    out = can.copy()
    out[take] = red[take]
    lbl, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        size = ndimage.sum(out[..., 3] > 0, lbl, range(1, n + 1))
        main = int(np.argmax(size)) + 1
        for j in range(1, n + 1):
            if j != main and size[j - 1] < SPECK:
                out[lbl == j] = 0
    out = SP.finish(out)                                           # one square of padding round it
    ys2, xs2 = np.nonzero(out[..., 3] > 0)
    top, left = ys2.min(), xs2.min()
    fig = out[top:ys2.max() + 1, left:xs2.max() + 1]
    ground = L.GROUND + 1 - top                                    # the canvas ground row, in the figure (finish padded 1)
    if L.legs_of(name)[1] is None or name in L.RUN:              # (every run frame has a foot on the ground)
        feet = np.zeros(out.shape[:2], bool)
        for pts in legs.values():
            for x, y in pts[-2:]:
                feet |= near_lines(out.shape[:2], {"f": [(x + 1, y + 1), (x + 1, y + 1.01)]}, FOOT)
        fy = np.nonzero((feet & (out[..., 3] > 0)).any(1))[0]
        if len(fy):
            ground = fy.max() + 1 - top
    return fig, ground, (ox + 1 - left, oy + 1 - top)


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma-separated pose names")
    a = ap.parse_args()
    design = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    names = [n for n in L.NAMES if (not a.only or n in a.only.split(",")) and redo(n) is not None]
    os.makedirs(lp(FIRST), exist_ok=True)
    results = {}
    for n in names:
        f0, meta = first(n)
        if not os.path.isfile(lp(os.path.join(FIRST, f"pose_{n}.png"))):
            Image.fromarray(f0).save(lp(os.path.join(FIRST, f"pose_{n}.png")))
            with open(lp(os.path.join(FIRST, f"pose_{n}.json")), "w", encoding="utf-8") as f:
                json.dump(meta, f)
        fig, ground, (bx, by) = join(n, design)
        hx, hy = meta["head_at"]
        results[n] = (fig, ground, (int(hx + bx), int(hy + by)), meta, f0)
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, ground row {ground}, head box at ({hx + bx}, {hy + by}) - "
              f"was {f0.shape[1]} x {f0.shape[0]}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 5
        for n, (fig, ground, at, meta, f0) in results.items():
            tiles = [design, f0, fig]
            Hm = max(t.shape[0] for t in tiles)
            W = sum(t.shape[1] * z + 12 for t in tiles)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for label, t in zip(("design", "first", "joined"), tiles):
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{label} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            sheet.convert("RGB").save(lp(os.path.join(a.sheet, f"legs_{n}.png")))
        return
    for n, (fig, ground, at, meta, f0) in results.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump(dict(meta, head_at=[at[0], at[1]], ground=int(ground)), f)


if __name__ == "__main__":
    main()

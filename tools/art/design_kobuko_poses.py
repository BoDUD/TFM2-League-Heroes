#!/usr/bin/env python3
"""Kobuko's Codex poses (assets/source/kobuko/codex_poses: POSE_PROMPTS.md, 16 key poses of his own TFT clips on his
design, 2026-10-27) on the design's palette, at the design's scale, with the design's own head pasted in (one face in
all frames), gaps closed (design_loris_poses.py's way).

    python tools/art/design_kobuko_poses.py --measure        # each pose's scale and head match
    python tools/art/design_kobuko_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_kobuko_poses.py                  # writes assets/source/kobuko/hd/pose_<name>.png (+ .json)

Codex delivered on the asked grid (12 px squares from the canvas corner, one colour a square, the soles on y 1176; its
pixel_1x/ is the same picture one pixel a square) in its own colours (88-95 a pose, none of hd/idle.png's) and a
little small: the standing a_back 76 rows against the design's 80, its HANDOFF says each pose was scaled to the
reference's head width. So each pose is read one pixel a square, every colour taken to the nearest of the design's in
Lab, then brought to the scale SCALES finds best for the design's head box (POLY: the topknot, the ears, the face and
the beard, not the near paw at his chin), the standing ones (STAND) to the design's 80 rows. The design's head is
pasted there, Codex's own head squares round it that the paste did not lay cleared where they are head-only colours,
loose specks dropped and the small holes and cracks closed (design_silco_poses.close_gaps: the gap check).
Each pose's json keeps where the head box went (its top-left square), the scale and where the figure's top-left square
was on Codex's 12 px grid (grid_at): Codex drew every pose where its reference put it, so rig_kobuko places them by it.
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
from design_kobuko_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_varus import srgb2lab  # noqa: E402
import pack_kobuko_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kobuko", "codex_poses", "kobuko-poses")
OUT = os.path.join(ROOT, "assets", "source", "kobuko", "hd")
SQ = 12
# the topknot, the ears, the face and the beard in hd/idle.png (x, y) - not the near paw at his chin (x 56+, y 20+)
POLY = [(29.0, 0.0), (34.0, 0.0), (37.0, 3.0), (41.0, 5.0), (45.0, 8.5), (49.0, 9.5), (55.5, 13.0), (60.0, 15.5),
        (60.0, 19.0), (57.0, 20.5), (55.5, 26.0), (52.0, 28.5), (40.0, 29.5), (30.0, 29.5), (22.0, 30.5), (10.0, 30.5),
        (7.0, 27.5), (3.0, 24.5), (0.0, 19.5), (2.0, 16.0), (5.0, 13.0), (9.0, 8.0), (15.0, 5.0), (20.0, 6.0),
        (25.0, 7.0), (28.0, 3.0)]
SCALES = [0.96, 1.0, 1.04, 1.08, 1.12]
# one body size for every frame: a_back (standing up again, as the design) 76 rows -> the design's 80 = 1.05 for all
# (a free head-match search put the poses anywhere from 1.00 to 1.12: the body would swell and shrink between frames);
# the run's height kept to 81 / 80 / 81 / 80 (a half-pixel bob; Codex drew 83 / 79 / 77 / 78)
STAND = {"run1": 81, "run2": 80, "run3": 81, "run4": 80}
SCALE = {}
DEFAULT = 1.05
TURN = {}
# the falling and lying frames keep Codex's own head (on the design's colours): the design's is upright, and these
# bodies are tipped over and laid down (an upright head pasted on them read wrong at 4x)
NO_PASTE = {"d_fall", "d_down"}
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def palette(d):
    cols = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    return cols, srgb2lab(cols.astype(float) / 255.0)


def pose(name, d):
    """The pose one pixel a square, every colour the nearest of the design's, cropped -> (figure, its top-left square
    on Codex's grid)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"kobuko-pose-{name}.png"))).convert("RGBA"))
    g = a[SQ // 2::SQ, SQ // 2::SQ].copy()
    op = g[..., 3] > 0
    cols, lab = palette(d)
    src = g[op][:, :3]
    uniq, inv = np.unique(src, axis=0, return_inverse=True)
    ul = srgb2lab(uniq.astype(float) / 255.0)
    near = np.argmin(((ul[:, None, :] - lab[None, :, :]) ** 2).sum(-1), axis=1)
    g[op, :3] = cols[near[inv.ravel()]]
    g[..., 3] = np.where(op, 255, 0)
    ys, xs = np.nonzero(op)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (int(xs.min()), int(ys.min()))


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def scaled(fig, k):
    h, w = fig.shape[:2]
    im = Image.fromarray(fig).resize((max(1, round(w * k)), max(1, round(h * k))), Image.NEAREST)
    return np.asarray(im).copy()


def match(fig, d, hm):
    """The offset (dx, dy) of the design's head in `fig` with the most squares of the same colour -> (dx, dy, share)."""
    ys, xs = np.nonzero(hm)
    want = d[ys, xs]
    best = (0, 0, -1.0)
    H, W = fig.shape[:2]
    for dy in range(-ys.min(), H - ys.max()):
        for dx in range(-xs.min(), W - xs.max()):
            got = fig[ys + dy, xs + dx]
            share = float(np.all(got == want, axis=1).mean())
            if share > best[2]:
                best = (dx, dy, share)
    return best


def head_colours(d, hm):
    """The colours only the head uses: not shared with the body or the outline."""
    head = {tuple(c) for c in d[hm][:, :3]}
    rest = {tuple(c) for c in d[~hm & (d[..., 3] > 0)][:, :3]}
    return head - rest


def fit(name, d, hm, scale=None):
    """The pose at the scale its head matches best -> (figure, scale, dx, dy, share, its top-left on Codex's grid: a
    scaled pose grown about its bottom middle)."""
    raw, (gx, gy) = pose(name, d)
    best = None
    for k in ([scale] if scale else SCALES):
        fig = scaled(raw, k)
        dx, dy, share = match(fig, d, hm)
        if best is None or share > best[4]:
            at = (gx + (raw.shape[1] - fig.shape[1]) / 2, gy + raw.shape[0] - fig.shape[0])
            best = (fig, float(k), dx, dy, share, at)
    return best


def read(name, scale=None):
    """The pose with the design's head -> (figure, the head box's top-left square in it, scale, the match share, the
    figure's top-left square on Codex's grid)."""
    d = design()
    hm = head_mask(d)
    if scale is None:
        scale = STAND[name] / pose(name, d)[0].shape[0] if name in STAND else SCALE.get(name, DEFAULT)
    fig, k, dx, dy, share, (gx, gy) = fit(name, d, hm, scale)
    pad = 6
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    ys, xs = np.nonzero(hm)
    head = np.zeros_like(d)
    head[hm] = d[hm]
    y0_, x0_ = ys.min(), xs.min()
    head = head[y0_:ys.max() + 1, x0_:xs.max() + 1]
    if name in TURN:   # the head box turned about its middle, where the upright one matched
        cy, cx = dy + y0_ + (head.shape[0] - 1) / 2, dx + x0_ + (head.shape[1] - 1) / 2
        head = np.flipud(np.rot90(head, -1)) if TURN[name] == "up" else np.rot90(head, TURN[name])
        dy, dx = int(round(cy - (head.shape[0] - 1) / 2)) - 0, int(round(cx - (head.shape[1] - 1) / 2))
        y0_, x0_ = 0, 0
    hy, hx = np.nonzero(head[..., 3] > 0)
    ys, xs = hy + y0_, hx + x0_
    py, px = ys + dy + pad, xs + dx + pad
    pasted = np.zeros(big.shape[:2], bool)
    pasted[py, px] = True
    only = head_colours(d, hm)
    y0, y1, x0, x1 = py.min() - 3, py.max() + 4, px.min() - 3, px.max() + 4
    for y in range(max(0, y0), min(big.shape[0], y1)) if name not in NO_PASTE else ():
        for x in range(max(0, x0), min(big.shape[1], x1)):
            if not pasted[y, x] and big[y, x, 3] and tuple(big[y, x, :3]) in only:
                big[y, x] = 0
    if name not in NO_PASTE:
        big[py, px] = head[hy, hx]
    big = close_gaps(big, d)
    op = big[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            big[lb == j] = 0
    ys2, xs2 = np.nonzero(big[..., 3] > 0)
    oy, ox = ys2.min(), xs2.min()
    at = (int(xs.min() + dx + pad - ox), int(ys.min() + dy + pad - oy))
    grid = (round(float(gx + ox - pad), 1), round(float(gy + oy - pad), 1))
    return big[oy:ys2.max() + 1, ox:xs2.max() + 1], at, k, share, grid


def big4(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    figs = {}
    for n in names:
        fig, at, k, share, grid = read(n)
        figs[n] = (fig, at, k, share, grid)
        print(f"{n:9s} scale {k:.2f}, head {share:5.1%} of its squares as drawn -> {fig.shape[1]} x {fig.shape[0]}, "
              f"head box at {at}")
    if a.measure:
        return
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
            path = os.path.join(a.sheet, f"kobuko_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, k, share, grid) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])], "scale": round(k, 2), "share": round(share, 3),
                       "grid_at": [grid[0], grid[1]]}, fh)


if __name__ == "__main__":
    main()

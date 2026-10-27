#!/usr/bin/env python3
"""Loris's Codex poses (assets/source/loris/codex_poses: POSE_PROMPTS.md, 16 key poses of his own TFT clips on his
design, 2026-10-27) on the design's palette, at the design's scale, with the design's own head pasted in (one face in
all frames), gaps closed.

    python tools/art/design_loris_poses.py --measure        # each pose's scale and head match
    python tools/art/design_loris_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_loris_poses.py                  # writes assets/source/loris/hd/pose_<name>.png (+ .json)

Codex delivered on the asked grid (12 px squares from the canvas corner, one colour a square, the soles on y 1176) but
in its own colours (1100-2100 a pose, none of hd/idle.png's 35) and at sizes that drift: the standing poses 82-91 rows
against the design's 84, the head bigger or smaller from frame to frame (its HANDOFF says so). So each pose is read
one pixel a square, every colour taken to the nearest of the design's in Lab, then brought to the scale SCALES finds:
to the design's size (STAND, SCALE, DEFAULT below), and the design's head box (POLY: the hair,
the headband, the face and the beard, not the pauldrons under it) is found at the offset where most of its squares'
colours match (a scale search, SCALES, put every body at 1.04-1.12: Codex drew the heads smaller than the design's). The design's head is pasted there,
Codex's own head squares round it that the paste did not lay cleared where they are head-only colours, loose specks
dropped and the small holes and cracks closed (design_silco_poses.close_gaps: the gap check).
Each pose's json keeps where the head box went (its top-left square), the scale and where the figure's top-left square
was on Codex's 12 px grid (grid_at): Codex drew every pose where its reference put it, so rig_loris places them by it.
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
from design_loris_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_varus import srgb2lab  # noqa: E402
import pack_loris_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "loris", "codex_poses", "loris-poses")
OUT = os.path.join(ROOT, "assets", "source", "loris", "hd")
SQ = 12
# the hair, the headband, the face and the beard in hd/idle.png (x, y) - not the pauldrons under the beard
POLY = [(22.0, 0.0), (33.0, 0.0), (35.5, 2.0), (36.5, 5.0), (36.5, 10.0), (35.5, 13.0), (35.5, 16.5), (34.5, 19.0),
        (33.0, 21.5), (28.0, 22.0), (24.0, 21.0), (20.0, 18.5), (16.5, 17.5), (13.5, 16.0), (13.0, 12.0), (13.0, 8.0),
        (14.0, 5.0), (16.0, 2.0), (19.5, 0.5)]
SCALES = [1.0]
# Codex drew every body 4-8 % over the design (standing 87-91 rows against its 84) and the run's head 9 rows up and
# down (4.5 game px): each pose brought back - the upright ones to the design's 84 rows, the run to 84 / 83 / 84 / 83
# (a 1 px bob), r_lift's body (drawn small under the raised shield, Codex's HANDOFF) up, the rest by Codex's mean excess
STAND = {"a_back": 84, "e_plant": 84, "run1": 84, "run2": 83, "run3": 84, "run4": 83}
SCALE = {"r_lift": 1.16}
DEFAULT = 0.95
TURN = {"d_down": "up"}                          # the pasted head laid down: "up" = the face to the sky, the crown to
                                                 # the image right (face down, the head was a ball of hair)
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
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"loris-pose-{name}.png"))).convert("RGBA"))
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
    """The colours only the head uses: not shared with the body, the shield or the outline."""
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
    for y in range(max(0, y0), min(big.shape[0], y1)):
        for x in range(max(0, x0), min(big.shape[1], x1)):
            if not pasted[y, x] and big[y, x, 3] and tuple(big[y, x, :3]) in only:
                big[y, x] = 0
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
            path = os.path.join(a.sheet, f"loris_poses_{j}.png")
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

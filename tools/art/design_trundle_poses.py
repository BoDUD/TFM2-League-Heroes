#!/usr/bin/env python3
"""Trundle's Codex poses (assets/source/trundle/codex_poses/trundle-poses: POSE_PROMPTS.md, 16 key poses of his League
clips on his design, 2026-10-25) read back at the design's scale, in its colours, with the design's own head
(design_yorick_poses.py's way).

    python tools/art/design_trundle_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_trundle_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_trundle_poses.py                  # writes assets/source/trundle/hd/pose_<name>.png (+ .json)
    python tools/art/design_trundle_poses.py --rematch        # the same, the heads searched again (else the json's)

His poses copy the design's head, so the head gives the scale: the head box (pack_trundle_poses.HEAD: the mane, the
face and the beard, hd/idle.png rows 12-48, columns 51-83) scaled over a range of px a square is matched against the
picture (design_shyvana_poses.match_head), the pose sampled on squares of the head's own size, the grid laid so the
matched head box keeps its middle, every colour snapped to the design's own (Lab), the design's head pasted square for
square on Codex's head's place (the polygon "poly": one face in all frames - Codex redrew the head, not copied it), the
outline closed. Each pose's json keeps where the head box went (its top-left square), for rig_trundle to place the pose.
Codex's own 9 px exports are read: pixel_1x/ for the squares (on the pack's grid, hard alpha), the root pictures for the
head match (only its place: the scale is the grid's); its raw/ pictures are soft and off the grid.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_shyvana_poses import match_head, sample_grid  # noqa: E402
from design_trundle_hd import lp  # noqa: E402
import pack_trundle_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "trundle", "codex_poses", "trundle-poses")
OUT = os.path.join(ROOT, "assets", "source", "trundle", "hd")
# the mane, the face and the beard (to the bottom of the beard) - not the fur collar round them
POLY = [(57.0, 13.0), (70.0, 12.0), (80.0, 18.0), (83.0, 30.0), (81.0, 42.0), (75.0, 49.0), (64.0, 49.0), (56.0, 44.0),
        (53.0, 34.0), (53.0, 22.0)]
SCALES = np.array([9.0])                         # the delivery is on the pack's 9 px grid: only the place is searched
TILTED = {}
# poses Codex drew on another canvas and then shrank to fit (manifest "source_size"): read from raw/ on the head's own
# squares (design_yorick_poses' way), not from the 9 px export (run1: a 1536 x 1024 draft fitted to 1254 wide, 0.8x)
RAW = {"run1": np.arange(8.0, 14.01, 0.25)}
MANE_COST = 0.3    # a head match worse than this places the head by the mane instead
TOP = {"q_rear"}   # the head thrown back and roaring: drawn taller than the design's, set by the mane's top
SCALE = {}                                       # px a square set by hand where the head's own does not fit the body
CACHE = "C:/t/tr_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    """The picture the head is matched on: the 9 px export, or Codex's raw draft for the RAW poses."""
    prefix = "trundle-pose-"
    sub = "raw" if name in RAW else ""
    return np.asarray(Image.open(lp(os.path.join(SRC, sub, f"{prefix}{name}.png"))).convert("RGBA"))


def head_box(d):
    r0, r1, c0, c1 = PK.HEAD
    return d[r0:r1, c0:c1]


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def finish(fig):
    """The outline closed; single enclosed holes the read-back left take the outline."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lb == j
        if h.sum() <= 1:
            pad[h] = (*ink, 255)
    return pad


def matched(name, again=False):
    """match_head's (px a square, x, y, cost, tilt) for a pose, kept in hd/pose_<name>.json ("match") once found."""
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    if not again and os.path.isfile(CACHE):
        c = json.load(open(CACHE, encoding="utf-8"))
        if name in c:
            return tuple(c[name])
    m = match_head(raw(name), head_box(design()), scales=RAW.get(name, SCALES), angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def mane(a, top=False):
    """The middle (column, row) of the biggest blob of his crimson mane and beard in a picture on the design's grid (its
    top row instead of its middle with `top`)."""
    rgb = a[..., :3].astype(int)
    m = (a[..., 3] > 0) & (rgb[..., 0] > 130) & (rgb[..., 0] > rgb[..., 1] + 70) & (rgb[..., 0] > rgb[..., 2] + 40)
    lb, n = ndimage.label(m)
    if not n:
        return None
    k = 1 + int(np.argmax(ndimage.sum(m, lb, range(1, n + 1))))
    ys, xs = np.nonzero(lb == k)
    return (xs.min() + xs.max()) / 2, (ys.min() if top else (ys.min() + ys.max()) / 2)


def is_mane(rgb):
    """His crimson mane and beard's colours (mane()'s test) on an (..., 3) array."""
    rgb = rgb.astype(int)
    return (rgb[..., 0] > 130) & (rgb[..., 0] > rgb[..., 1] + 70) & (rgb[..., 0] > rgb[..., 2] + 40)


def clear_leftovers(fig, pasted, box):
    """Codex's own mane and beard left round the pasted head (it drew some heads bigger: q_rear's thrown-back roar):
    every mane-coloured square in `box` (rows / columns, the head box grown) that the paste did not lay takes the most
    common colour round it that is not mane (the fur collar, the cape, the skin), or goes clear where most round it is
    clear; repeated until none is left."""
    y0, y1, x0, x1 = box
    for _ in range(12):
        op = fig[..., 3] > 0
        left = np.zeros(op.shape, bool)
        left[y0:y1, x0:x1] = True
        left &= op & ~pasted & is_mane(fig[..., :3])
        if not left.any():
            return fig
        out = fig.copy()
        for y, x in zip(*np.nonzero(left)):
            nb = fig[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
            clear = int((nb[:, 3] == 0).sum())
            keep = [tuple(c) for c in nb if c[3] > 0 and not is_mane(c[None, :3])[0]]
            if clear >= 5 or not keep:
                if clear >= 3:
                    out[y, x] = 0
                continue
            out[y, x] = max(set(keep), key=keep.count)
        fig = out
    return fig


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt). The delivery's pixel_1x/ is the pose square for square on the
    design's grid (its 9 px export, cell (0, 0) at the canvas corner); the head match (on the 9 px picture) gives where
    Codex's head box lies, rounded to its squares."""
    d = design()
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = PK.HEAD
    if name in RAW:                                    # on the head's own squares, the grid laid round the head box
        hw, hh = c1 - c0, r1 - r0
        a, (ci, cj) = sample_grid(raw(name), s, hx, hy)
    else:
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"trundle-pose-{name}.png"))).convert("RGBA")).copy()
        ci, cj = int(round(hx / PK.PX)), int(round(hy / PK.PX))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    # a poor match (a roaring head is drawn unlike the design's; MANE_COST): the design's mane middle set on Codex's
    # (the mane is the same shape), the head box with it
    dm, pm = mane(d, name in TOP), mane(a, name in TOP)
    if dm and pm and cost > MANE_COST and name not in RAW:
        ci, cj = int(round(pm[0] - (dm[0] - c0))), int(round(pm[1] - (dm[1] - r0)))
    fig = snap(a, d)
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if not ang:                                        # a tipped head keeps Codex's own (the design's is upright)
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
        pasted = np.zeros(big_.shape[:2], bool)
        pasted[ys - r0 + cj + pad, xs - c0 + ci + pad] = True
        gy, gx = cj + pad, ci + pad
        big_ = clear_leftovers(big_, pasted, (max(0, gy - 10), gy + (r1 - r0) + 10, max(0, gx - 10), gx + (c1 - c0) + 10))
    big_ = finish(big_)
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), float(s if name in RAW else PK.PX), cost, ang


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--rematch", action="store_true", help="search the heads again (else the json's)")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    if a.measure:
        d = design()
        for n in names:
            r = raw(n)
            s, x, y, cost, ang = match_head(r, head_box(d), scales=RAW.get(n, SCALES), angles=TILTED.get(n, (0,)))
            area = float(np.sqrt((r[..., 3] >= 128).sum() / (d[..., 3] > 0).sum()))
            print(f"{n:9s} head {s:5.2f} px a square at ({x}, {y}) tilted {ang}, cost {cost:.4f}; area {area:5.2f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:9s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        for f, ref, group in (("trundle", "idle.png", NAMES),):
            tiles = [("design", design(ref))] + [(n, figs[n][0]) for n in group if n in figs]
            rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
            for k, row in enumerate(rows):
                Hm = max(t.shape[0] for _, t in row)
                W = sum(t.shape[1] * z + 12 for _, t in row)
                sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
                dr = ImageDraw.Draw(sheet)
                x = 0
                for n, t in row:
                    sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                    dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                    x += t.shape[1] * z + 12
                path = os.path.join(a.sheet, f"{f}_poses_{k}.png")
                sheet.convert("RGB").save(lp(path))
                print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        stem = f"pose_{n}"
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{stem}.png")))
        if at is not None:
            with open(lp(os.path.join(OUT, f"{stem}.json")), "w", encoding="utf-8") as fh:
                json.dump({"head_at": [int(at[0]), int(at[1])],
                           "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, fh)


if __name__ == "__main__":
    main()

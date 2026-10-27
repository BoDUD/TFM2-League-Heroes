#!/usr/bin/env python3
"""Maddie's Codex poses (assets/source/maddie/codex_poses: POSE_PROMPTS.md, 15 key poses of her own TFT clips on her
design, 2026-10-27) with the design's own head pasted in (one face in all frames), gaps closed.

    python tools/art/design_maddie_poses.py --measure        # each pose's head match
    python tools/art/design_maddie_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_maddie_poses.py                  # writes assets/source/maddie/hd/pose_<name>.png (+ .json)

Codex delivered this pack already on the design's grid: pixel_grid/maddie-pose-<name>.png are 70 x 70 squares (its
18 px squares one pixel each), every colour one of hd/idle.png's own, the soles on row 64 (its HANDOFF: the 1254 canvas
is no multiple of 18, so the ground sits 6 px over the asked y 1176), the figures 56-61 rows tall like the design's 57.
So no reading back: the head box (the beret, the bob, the face to the chin: hd/idle.png's polygon POLY, the rifle
passing behind it left out) is searched square for square in each pose (the offset with the most squares of the same
colour, TILT none: Codex kept every head upright, the lying one too), the design's head pasted there, Codex's own head
squares round it that the paste did not lay cleared where they are the head's colours (hair, beret, skin), loose specks
dropped and the small holes and cracks closed (design_silco_poses.close_gaps: the gap check).
Each pose's json keeps where the head box went (its top-left square), for rig_maddie to place the pose.
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
from design_maddie_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
import pack_maddie_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "maddie", "codex_poses", "pixel_grid")
OUT = os.path.join(ROOT, "assets", "source", "maddie", "hd")
# the beret, the orange bob, the face and the chin in hd/idle.png (x, y) - not the rifle crossing behind the head on
# the left (columns 0-22, rows 3-15) or the collar under the chin
POLY = [(27.0, 0.0), (36.5, 0.0), (40.5, 3.0), (41.5, 5.0), (40.5, 8.0), (41.5, 12.0), (41.5, 14.5), (39.5, 16.5),
        (32.5, 17.0), (25.0, 17.0), (23.0, 15.0), (21.5, 13.0), (20.5, 10.0), (19.5, 7.5), (21.5, 3.0), (24.5, 1.0)]
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def pose(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"maddie-pose-{name}.png"))).convert("RGBA")).copy()


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


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
    """The colours only the head uses (the beret, the hair, the skin): not shared with the body, the rifle or the
    outline - a Codex square in one of these round the pasted head is Codex's own head."""
    head = {tuple(c) for c in d[hm][:, :3]}
    rest = {tuple(c) for c in d[~hm & (d[..., 3] > 0)][:, :3]}
    return head - rest


def read(name):
    """The pose with the design's head -> (figure, the head box's top-left square in it, the match share)."""
    d = design()
    hm = head_mask(d)
    fig = pose(name)
    dx, dy, share = match(fig, d, hm)
    pad = 6
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    ys, xs = np.nonzero(hm)
    py, px = ys + dy + pad, xs + dx + pad
    pasted = np.zeros(big.shape[:2], bool)
    pasted[py, px] = True
    # Codex's own head squares round the paste (head-only colours, 3 squares round the head box) go clear
    only = head_colours(d, hm)
    y0, y1, x0, x1 = py.min() - 3, py.max() + 4, px.min() - 3, px.max() + 4
    for y in range(max(0, y0), min(big.shape[0], y1)):
        for x in range(max(0, x0), min(big.shape[1], x1)):
            if not pasted[y, x] and big[y, x, 3] and tuple(big[y, x, :3]) in only:
                big[y, x] = 0
    big[py, px] = d[ys, xs]
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
    return big[oy:ys2.max() + 1, ox:xs2.max() + 1], at, share


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
        fig, at, share = read(n)
        figs[n] = (fig, at, share)
        print(f"{n:9s} head {share:5.1%} of its squares as drawn -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.measure:
        return
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
        for k, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big4(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"maddie_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, share) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])], "share": round(share, 3)}, fh)


if __name__ == "__main__":
    main()

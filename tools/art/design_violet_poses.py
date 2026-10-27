#!/usr/bin/env python3
"""Violet's Codex poses (assets/source/violet/codex_poses: POSE_PROMPTS.md, 19 key poses of her own TFT clips on her
design, 2026-10-28) on the design's palette, at the design's scale, with the design's own head pasted in (one face in
all frames), gaps closed.

    python tools/art/design_violet_poses.py --measure        # each pose's square, scale and head match
    python tools/art/design_violet_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_violet_poses.py                  # writes assets/source/violet/hd/pose_<name>.png (+ .json)

Vander's way (design_vander_poses.py), but Codex did NOT draw on the asked 12 px grid: its squares came out 9-12 px
(regrid's measure, a different one in each pose) with a faint soft alpha over the whole canvas, and the bodies were
drawn about as tall in PIXELS as their references (so as tall as the design at 12 px a square). So each pose is read
on its own squares (regrid, alpha >= 128), every colour taken to the nearest of the design's in Lab, and brought to
the design's density by its square / 12 (SCALE adjusts a pose drawn off its reference's size); then the design's head
box (POLY: the hair and the face, not the vest's collar nor the shoulder guard under it) is pasted where most of its
squares' colours match, Codex's own head squares round it that the paste did not lay cleared where they are head-only
colours, loose specks dropped and the small holes and cracks closed (design_silco_poses.close_gaps).
Each pose's json keeps where the head box went (its top-left square), the scale and where the figure's top-left was
on the design's 12 px grid of Codex's canvas (grid_at): Codex drew every pose where its reference put it, so
rig_violet places them by it.
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
from design_violet_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_varus import srgb2lab  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import pack_violet_poses as PK
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "violet", "codex_poses", "violet-poses")
OUT = os.path.join(ROOT, "assets", "source", "violet", "hd")
SQ = 12                          # the design's square on the pose pack's canvas
# the hair and the face in hd/idle.png (x, y) - not the vest's collar nor the far shoulder guard (cols 15-21, rows 20+)
POLY = [(30.0, 0.0), (38.0, 0.0), (44.0, 3.0), (46.0, 6.0), (46.0, 16.0), (45.0, 20.0), (44.0, 26.0), (35.0, 26.0),
        (30.0, 25.0), (22.0, 25.0), (21.0, 20.0), (19.0, 16.0), (18.5, 10.0), (20.0, 6.0), (23.0, 2.5), (27.0, 0.5)]
SCALES = [1.0]
# the run's four frames to one height (Codex drew run1 / run3 on bigger squares: 80 / 75 rows against run2's 73 at the
# same factor, a head bob of 7 rows): upright, a little taller than the crouched design's 76
STAND = {f"run{k}": 77 for k in range(1, 5)}
# a pose drawn bigger than the rest: its own factor on top of square / 12 (2026-10-28: the poses' heights against
# their references' ran 1.2-1.3 for most, 1.37-1.48 for these; the run, as Vander's (「怎么体型现在这么大啊 跑步的时候」),
# drew ~15% over its references: 0.88 for all four frames, so the cycle keeps one size)
SCALE = {"a_wind": 0.87, "q_coil": 0.89, "e_punch": 0.90, "q_land": 0.94, "r_slam": 0.95, "d_down": 0.90,
}
DEFAULT = 1.0
# d_down: Codex's own head lying there read muddy at 8x and the upright paste stood up off the lying body; the design's
# head turned to lie face up (the top of the head to the image right), centred where Codex's lay
TURN = {"d_down": "up"}
HEAD_CENTRE = {"d_down": (88, 18)}
# d_fall: Codex's own head, thrown back with the body, reads (two eyes, the mouth); the upright paste did not
NO_PASTE = {"d_fall"}
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def palette(d):
    cols = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    return cols, srgb2lab(cols.astype(float) / 255.0)


def pose(name, d):
    """The pose one pixel a square of Codex's own grid, every colour the nearest of the design's, cropped -> (figure,
    its top-left on the design's 12 px grid, Codex's square in px)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"violet-pose-{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    g, sq, (cb, rb) = RG.regrid(a)
    op = g[..., 3] >= 128
    cols, lab = palette(d)
    src = g[op][:, :3]
    uniq, inv = np.unique(src, axis=0, return_inverse=True)
    ul = srgb2lab(uniq.astype(float) / 255.0)
    near = np.argmin(((ul[:, None, :] - lab[None, :, :]) ** 2).sum(-1), axis=1)
    g[op, :3] = cols[near[inv.ravel()]]
    g[..., 3] = np.where(op, 255, 0)
    ys, xs = np.nonzero(op)
    return (g[ys.min():ys.max() + 1, xs.min():xs.max() + 1],
            (float(cb[xs.min()]) / SQ, float(rb[ys.min()]) / SQ), float(sq))


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
    """The colours only the head uses: not shared with the body, the gauntlet or the outline."""
    head = {tuple(c) for c in d[hm][:, :3]}
    rest = {tuple(c) for c in d[~hm & (d[..., 3] > 0)][:, :3]}
    return head - rest


def fit(name, d, hm, scale=None):
    """The pose at the scale its head matches best -> (figure, scale, dx, dy, share, its top-left on Codex's grid: a
    scaled pose grown about its bottom middle)."""
    raw, (gx, gy), sq = pose(name, d)
    best = None
    for k in [sq / SQ * (scale or 1.0)]:
        fig = scaled(raw, k)
        dx, dy, share = match(fig, d, hm)
        if best is None or share > best[4]:
            # Codex's figure spans raw * sq / 12 of the design's squares; scaled by k about its bottom middle
            rw, rh = raw.shape[1] * sq / SQ, raw.shape[0] * sq / SQ
            at = (gx + (rw - fig.shape[1]) / 2, gy + rh - fig.shape[0])
            best = (fig, float(k), dx, dy, share, at)
    return best


def read(name, scale=None):
    """The pose with the design's head -> (figure, the head box's top-left square in it, scale, the match share, the
    figure's top-left square on Codex's grid)."""
    d = design()
    hm = head_mask(d)
    if scale is None:
        if name in STAND:
            raw, _, sq = pose(name, d)
            scale = STAND[name] / (raw.shape[0] * sq / SQ)
        else:
            scale = SCALE.get(name, DEFAULT)
    fig, k, dx, dy, share, (gx, gy) = fit(name, d, hm, scale)
    pad = 6
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    ys, xs = np.nonzero(hm)
    head = np.zeros_like(d)
    head[hm] = d[hm]
    y0_, x0_ = ys.min(), xs.min()
    head = head[y0_:ys.max() + 1, x0_:xs.max() + 1]
    if name in HEAD_CENTRE:   # put the box's middle there instead of where the upright head matched
        cx_, cy_ = HEAD_CENTRE[name]
        dx = int(round(cx_ - x0_ - (head.shape[1] - 1) / 2))
        dy = int(round(cy_ - y0_ - (head.shape[0] - 1) / 2))
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
    if name in NO_PASTE:
        pasted[:] = False
    only = head_colours(d, hm) if name not in NO_PASTE else set()
    y0, y1, x0, x1 = py.min() - 3, py.max() + 4, px.min() - 3, px.max() + 4
    for y in range(max(0, y0), min(big.shape[0], y1)):
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
            path = os.path.join(a.sheet, f"violet_poses_{j}.png")
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

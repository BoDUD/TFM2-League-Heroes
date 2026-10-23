#!/usr/bin/env python3
"""Zac's Codex poses (assets/source/zac/codex_poses/zac-poses: POSE_PROMPTS.md, 17 key poses of his League clips on
the design) read back at the design's scale, in its colours, with the design's own head (design_nunu_poses.py's way).

    python tools/art/design_zac_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_zac_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_zac_poses.py                  # writes assets/source/zac/hd/pose_<name>.png (+ .json)
    python tools/art/design_zac_poses.py --rematch        # the same, the heads searched again (else the json's)

The poses copy the design's head box (pack_zac_poses.HEAD: the head with the tendril). Codex drew every body at one
size (its squares ~9.8 px: the FFT of the colour edges, every pose's height against the design's) but his head a little
smaller in some (matched alone it came out 8.0-10 px a square: read at that scale e_pull's body would grow a fifth), so
every pose is read on its own grid by regrid at SIZE (a little above the square, regrid's rule), every colour snapped to
the design's own (Lab); then the design's head and tendril are pasted square for square (POLY and TENDRIL: one face in
all frames) with their eyes' middle on the middle of the pose's two yellow eyes, the outline closed. Each pose's json
keeps where the face box went (its top-left square), for rig_zac to place the pose. Where League changes his face on
purpose the pose keeps Codex's (KEEP_FACE: d_melt's half-closed eyes, d_puddle's closed ones and limp tendril, r_splat's
squashed head).
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
from design_shyvana_poses import match_head  # noqa: E402
from regrid import regrid  # noqa: E402
from design_zac_hd import lp  # noqa: E402
import pack_zac_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zac", "codex_poses", "zac-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "zac", "hd")
HEAD = (12, 43, 48, 72)            # rows / columns of the face box in hd/idle.png: the skull, the eyes, the grin, the chin
# the head: the skull under the tendril's root, the eyes, the grin, the chin - not the far shoulder beside it (the dark
# line from the skull's top down to the cheek parts them)
POLY = [(49.0, 13.0), (58.0, 12.0), (62.0, 15.0), (66.0, 19.0), (69.5, 22.0), (70.0, 30.0), (69.5, 38.0), (66.0, 42.0),
        (56.0, 42.0), (51.0, 39.0), (49.0, 32.0)]
TENDRIL = [(41.0, 0.0), (64.0, 0.0), (64.0, 8.0), (57.0, 9.0), (53.0, 8.0), (51.0, 11.0), (55.0, 13.0), (49.0, 14.0),
           (43.0, 10.0), (41.0, 5.0)]
SCALES = np.arange(7.0, 12.01, 0.25)
SIZE = 10.3                        # regrid's square: a little above Codex's ~9.8 px
EYES = (61.0, 24.5)                # the middle of the design's two eyes (hd/idle.png square edges)
ANGLES = (0,)
KEEP_FACE = {"r_splat", "d_melt", "d_puddle"}     # League squashes or melts his face here: Codex's face stays
NO_TENDRIL = {"r_splat", "d_melt", "d_puddle", "r_ball"}   # the tendril as Codex drew it (squashed, limp, tucked)
# rows dropped under the face (least loss, spread: design_riven.pick) where Codex's pose stands taller than League's: the
# crouch before R's hop came back a row taller than the idle (its eyes a row higher) - League's is a deep crouch
CROUCH = {"r_crouch": 7}
CACHE = "C:/t/za_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"zac-pose-{name}-raw.png"))).convert("RGBA"))


def poly_mask(d, pts):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(pts, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def head_box(d):
    """The face box with only the head opaque (POLY)."""
    r0, r1, c0, c1 = HEAD
    t = d[r0:r1, c0:c1].copy()
    t[~poly_mask(d, POLY)[r0:r1, c0:c1]] = 0
    return t


def finish(fig):
    """The outline closed; enclosed holes the read-back left take the outline where they are a single square or a slit
    one square wide; wider holes stay (the design shows the ground between his arms and legs too)."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lb == j
        if h.sum() <= 1 or (h.sum() <= 4 and min(np.ptp(np.nonzero(h)[0]), np.ptp(np.nonzero(h)[1])) == 0):
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
    m = match_head(raw(name), head_box(design()), scales=SCALES, angles=ANGLES)
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def drop_specks(a, most=6):
    """Pieces apart from the figure's biggest (8-connected) of at most `most` squares cleared (the read-back's crumbs)."""
    a = a.copy()
    lb, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lb, range(1, n + 1))
        keep = int(np.argmax(sizes)) + 1
        for j in range(1, n + 1):
            if j != keep and sizes[j - 1] <= most:
                a[lb == j] = 0
    return a


def eye_squares(fig):
    """The yellow-orange eye squares of a read-back (red over green over blue by far; the yellow-green highlights have
    more green than red)."""
    rgb = fig[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (fig[..., 3] > 0) & (r > 170) & (r >= g) & (g > b + 60)


def eyes_middle(fig):
    """The middle of the two biggest eye blobs (square edges), or None."""
    lb, n = ndimage.label(eye_squares(fig), structure=np.ones((3, 3)))
    if n < 2:
        return None
    sizes = ndimage.sum(np.ones_like(lb), lb, range(1, n + 1))
    keep = np.argsort(-sizes)[:2] + 1
    pts = [np.argwhere(lb == k).mean(0) for k in keep]
    (y0, x0), (y1, x1) = pts
    return ((x0 + x1) / 2 + 0.5, (y0 + y1) / 2 + 0.5)


def read(name, match=None):
    """The pose on its own grid in the design's colours with the design's head (and tendril) -> (figure, the face box's
    top-left square in it, the square's size in px, the eyes' offset found)."""
    d = design()
    a = raw(name).copy()
    fig, sq, _ = regrid(a, SIZE)
    op = fig[..., 3] >= 128
    fig[..., 3] = np.where(op, 255, 0)
    fig[~op] = 0
    ys, xs = np.nonzero(op)
    fig = snap(fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1], d)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    r0, r1, c0, c1 = HEAD
    at = None
    if name not in KEEP_FACE:
        em = eyes_middle(big_)
        if em is None:
            sys.exit(f"{name}: no two eyes found")
        dx, dy = int(round(em[0] - EYES[0])), int(round(em[1] - EYES[1]))
        paste = poly_mask(d, POLY)
        if name not in NO_TENDRIL:
            paste |= poly_mask(d, TENDRIL)
        ys, xs = np.nonzero(paste)
        ty, tx = ys + dy, xs + dx
        if ty.min() < 0 or tx.min() < 0 or ty.max() >= big_.shape[0] or tx.max() >= big_.shape[1]:
            sys.exit(f"{name}: the head lands off the picture")
        big_[ty, tx] = d[ys, xs]
        at = (c0 + dx, r0 + dy)
    big_ = finish(drop_specks(big_))
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    at = None if at is None else (at[0] + 1 - x0, at[1] + 1 - y0)
    fig = big_[y0:ys2.max() + 1, x0:xs2.max() + 1]
    if name in CROUCH:
        fig = crouched(fig, at[1] + (r1 - r0) + 1, CROUCH[name])
    return fig, at, sq, None


def crouched(fig, chin, n):
    """n rows dropped between the chin's row and the soles' last three (the legs and the hands lower: a deeper crouch),
    the least-loss ones spread over that band (design_riven.pick), the face untouched."""
    from design_riven import pick
    H = fig.shape[0]
    band = list(range(chin + 1, H - 3))
    keep, _ = pick([fig[y] for y in band], len(band) - n, 0)
    rows = list(range(0, chin + 1)) + [band[i] for i in keep] + list(range(H - 3, H))
    return fig[rows]


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
            s, x, y, cost, ang = match_head(r, head_box(d), scales=SCALES, angles=ANGLES)
            area = float(np.sqrt((r[..., 3] >= 128).sum() / (d[..., 3] > 0).sum()))
            print(f"{n:9s} head {s:5.2f} px a square at ({x}, {y}), cost {cost:.4f}; area {area:5.2f}")
        return
    figs = {}
    for n in names:
        fig, at, s, _ = read(n)
        figs[n] = (fig, at, None)
        print(f"{n:9s} {s:5.2f} px a square -> {fig.shape[1]} x {fig.shape[0]}, face box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in names if n in figs]
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
            path = os.path.join(a.sheet, f"zac_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": None if at is None else [int(at[0]), int(at[1])]}, fh)


if __name__ == "__main__":
    main()

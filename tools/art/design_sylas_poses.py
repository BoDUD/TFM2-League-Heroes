#!/usr/bin/env python3
"""Sylas's Codex poses (assets/source/sylas/codex_poses: POSE_PROMPTS.md, twelve of League's whole-body poses and four
run frames on skeletons) read back at the design's scale, in its colours, with the design's own head.

    python tools/art/design_sylas_poses.py --measure          # each raw pose's scale measures
    python tools/art/design_sylas_poses.py --sheet DIR        # all poses beside the design (5x)
    python tools/art/design_sylas_poses.py                    # writes assets/source/sylas/hd/pose_<name>.png

Codex drew every pose bigger than the 16 px asked (the figures fill the canvas), so the scale of each (Codex px a
design square) comes from his eyes (two small white squares, the only small white next to skin): an upright pose's
eye-to-sole height over the design's 37.5 squares, the folded poses the median of the upright ones (the same canvas
and skeleton grid), `lie` (returned 1774 wide) by its eyes' spacing. (The area measures, --measure, disagreed by up to a
quarter: Codex's poses are slimmer than the chunky design.) Each pose is sampled on that grid from the figure's top-left
(design_chogath_poses.sample: a square opaque when most of it is, the median colour), every colour snapped to the
design's own (Lab), the outline closed. One face in all frames (memory one-face-all-frames): Codex's head is covered by
the design's (HEAD_POLY: the hair, the face and the beard, never the scarf or the shoulders), its near eye laid on
Codex's near eye.
"""
import argparse
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
from design_chogath_poses import sample  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_sylas_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sylas", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "sylas", "hd")
NAMES = ["wind", "lash", "spin", "leap", "stab", "slam", "dash", "throw", "pull", "stagger", "kneel", "lie",
         "run1", "run2", "run3", "run4"]
DESIGN_NEAR_EYE = (37.0, 8.0)   # (x, y) of the near eye's white square in hd/idle.png (the far one at (40, 8))
DESIGN_EYE_TO_SOLE = 37.5       # squares from the eyes' middle to the soles' bottom edge in the design
UPRIGHT = ["stagger", "throw", "wind", "run1", "run2", "run3", "run4"]   # standing on the ground, legs not folded
# drawn lankier than the others (stagger: eye to sole 910 px against 710-800, its body area 0.72 of the design's at its
# own height): halfway between its own height and the wind-up's scale - a little taller than the idle, not as thin
LANKY = ["stagger"]
# the design's head (hair, face, beard) as a polygon in design squares (x, y) on hd/idle.png
HEAD_POLY = [(31, 0), (44, 0), (46, 4), (46, 10), (44, 13), (36, 13), (32, 11), (30, 6), (31, 0)]


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"sylas-pose-{name}.png"))).convert("RGBA"))


def masks(a):
    rgb = a[..., :3].astype(int)
    op = a[..., 3] >= 128
    white = op & (rgb.min(2) > 200)
    skin = op & (rgb[..., 0] > 200) & (rgb[..., 1] > 120) & (rgb[..., 1] < 200) & (rgb[..., 2] < 160) & (rgb[..., 2] > 60)
    return white, skin, op


def scale_of(a, idle):
    ma, mi = masks(a), masks(idle)
    return float(np.median([np.sqrt(x.sum() / y.sum()) for x, y in zip(ma, mi)]))


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(HEAD_POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def lab(rgb):
    import design_varus as V
    return V.srgb2lab(rgb)


def best_head(fig, idle):
    """(dy, dx): where the design's head lies best on the sampled pose (the head's squares at (y + dy, x + dx))."""
    hm = head_mask(idle)
    ys, xs = np.nonzero(hm)
    hl = lab(idle[ys, xs, :3].astype(float))
    H, W = fig.shape[:2]
    fl = lab(fig[..., :3].reshape(-1, 3).astype(float)).reshape(H, W, 3)
    op = fig[..., 3] > 0
    best = None
    for dy in range(-ys.min(), H - ys.max()):
        for dx in range(-xs.min(), W - xs.max()):
            yy, xx = ys + dy, xs + dx
            inside = op[yy, xx]
            if inside.mean() < 0.8:
                continue
            d = np.linalg.norm(fl[yy, xx] - hl, axis=1)
            cost = np.where(inside, np.minimum(d, 60), 60).mean()
            if best is None or cost < best[0]:
                best = (cost, dy, dx)
    return best


def with_head(fig, idle, dy, dx):
    hm = head_mask(idle)
    ys, xs = np.nonzero(hm)
    pad = 20
    out = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    out[ys + dy + pad, xs + dx + pad] = idle[ys, xs]
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def finish(fig, most=6):
    """The outline closed; small enclosed holes the readback left take the outline (the chain links' own holes stay:
    a hole bigger than `most` squares is kept)."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lb == j
        if h.sum() <= 1:
            pad[h] = (*ink, 255)
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def eyes_px(a):
    """Codex's eyes: the small white blobs next to skin (the manacles' white is far bigger), the pair at one height
    and 30-70 px apart; (x, y) of the near (left) eye, and of the far one or None when only one shows."""
    rgb = a[..., :3].astype(int)
    op = a[..., 3] >= 128
    w = op & (rgb.min(2) > 215)
    skin = op & (rgb[..., 0] > 200) & (rgb[..., 1] > 120) & (rgb[..., 1] < 200) & (rgb[..., 2] < 160) & (rgb[..., 2] > 60)
    near_skin = ndimage.binary_dilation(skin, iterations=25)
    lb, k = ndimage.label(w)
    blobs = []
    for i in range(1, k + 1):
        b = lb == i
        if 60 <= b.sum() <= 900 and near_skin[b].any():
            ys, xs = np.nonzero(b)
            blobs.append((xs.mean(), ys.mean()))
    pairs = [(p, q) for p in blobs for q in blobs if 30 <= q[0] - p[0] <= 70 and abs(q[1] - p[1]) <= 6]
    if pairs:
        return min(pairs, key=lambda pq: pq[0][1])
    return min(blobs, key=lambda b: b[1]), None


def scale_by_eyes(name, a):
    """Codex px a design square: an upright pose's eye-to-sole height over the design's (37.5 squares); the others take
    the median of the upright ones (Codex drew them on the same canvas); `lie` came back at its own size (1774 wide),
    by its eyes' spacing against the upright poses'."""
    if name in UPRIGHT:
        (ex, ey), _ = eyes_px(a)
        ys = np.nonzero(a[..., 3] >= 128)[0]
        own = (ys.max() + 1 - ey) / DESIGN_EYE_TO_SOLE
        if name in LANKY:
            return (own + scale_by_eyes("wind", raw("wind"))) / 2
        return own
    common = float(np.median([scale_by_eyes(n, raw(n)) for n in UPRIGHT if n not in LANKY]))
    if name == "lie":
        gaps = [eyes_px(raw(n)) for n in UPRIGHT]
        gap = float(np.median([q[0] - p[0] for p, q in gaps if q is not None]))
        p, q = eyes_px(a)
        return common * (q[0] - p[0]) / gap
    return common


def read(name, idle):
    a = raw(name)
    sc = scale_by_eyes(name, a)
    fig = snap(sample(a, sc), idle)
    ys, xs = np.nonzero(a[..., 3] >= 128)
    (ex, ey), _ = eyes_px(a)
    # the design's near eye on Codex's near eye
    dy = int(round((ey - ys.min()) / sc - 0.5 - DESIGN_NEAR_EYE[1]))
    dx = int(round((ex - xs.min()) / sc - 0.5 - DESIGN_NEAR_EYE[0]))
    return finish(with_head(fig, idle, dy, dx)), sc, 0.0


def measure():
    idle = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    mi = masks(idle)
    for n in NAMES:
        a = raw(n)
        ma = masks(a)
        r = [np.sqrt(x.sum() / y.sum()) for x, y in zip(ma, mi)]
        print(f"{n:8s} white {r[0]:5.2f} skin {r[1]:5.2f} all {r[2]:5.2f} -> {np.median(r):5.2f} px a square")


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.measure:
        measure()
        return
    idle = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    figs = {}
    for n in NAMES:
        f, sc, cost = read(n, idle)
        figs[n] = f
        print(f"{n:8s} scale {sc:5.2f} -> {f.shape[1]}x{f.shape[0]}, head cost {cost:5.1f}")
    if a.sheet:
        os.makedirs(a.sheet, exist_ok=True)
        z = 5
        cells = [("design", idle)] + list(figs.items())
        rows = [cells[i:i + 5] for i in range(0, len(cells), 5)]
        W = max(sum(f.shape[1] * z + 20 for _, f in r) for r in rows) + 20
        Hs = [max(f.shape[0] for _, f in r) * z + 40 for r in rows]
        can = Image.new("RGB", (W, sum(Hs)), (255, 255, 255))
        dr = ImageDraw.Draw(can)
        y0 = 0
        for r, H in zip(rows, Hs):
            x = 20
            for name, f in r:
                b = big(f, z)
                can.paste(b.convert("RGB"), (x, y0 + H - 10 - b.height))
                dr.text((x, y0 + 4), f"{name} {f.shape[1]}x{f.shape[0]}", fill=(0, 0, 0))
                x += b.width + 20
            dr.line([(0, y0 + H - 10), (W, y0 + H - 10)], fill=(200, 0, 0))
            y0 += H
        can.save(os.path.join(a.sheet, "sylas_poses_sheet.png"))
        print(os.path.join(a.sheet, "sylas_poses_sheet.png"))
        return
    for n, f in figs.items():
        Image.fromarray(f).save(lp(os.path.join(OUT, f"pose_{n}.png")))


if __name__ == "__main__":
    main()

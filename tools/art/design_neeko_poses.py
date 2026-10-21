#!/usr/bin/env python3
"""Neeko's Codex poses (assets/source/neeko/codex_poses: POSE_PROMPTS.md, thirteen of League's whole-body poses and four
run frames on skeletons, the user's neeko_poses_done.zip) read back at the design's scale, in its colours, with the
design's own head (design_shyvana_poses.py's way).

    python tools/art/design_neeko_poses.py --measure        # each pose's scale and head position (the head matched)
    python tools/art/design_neeko_poses.py --sheet DIR      # all poses beside the design (5x)
    python tools/art/design_neeko_poses.py                  # writes assets/source/neeko/hd/pose_<name>.png (+ .json)
    python tools/art/design_neeko_poses.py --rematch        # the same, the heads searched again (else the json's)

Codex drew the poses on the asked 10 px squares (its cleaned pictures neeko-pose-<name>.png, palette-snapped), but not
all at one size: it shrank the ones that would not fit its canvas (manifest.json whole_pose_fit: soar 0.83, throw_air
0.90, land 0.96, twirl 0.97, coil 0.99) and drew some heads bigger than others. Every pose copies the design's head
(1_head.png), so the head itself gives the scale: the design's head box (HEAD, the quills, the face and the hair round
it) scaled 7-13 px a square is matched against the picture (masked colour distance by FFT, at half size), the best
scale and place kept. The picture is sampled on squares BODY times that size, the grid laid so the matched head box
keeps its middle (a square opaque when most of it is, the median colour), every colour snapped to the design's own
(Lab), the design's head pasted square for square on Codex's head's middle (HEAD_POLY: the quills, the face and the
hair round it, never the neck - one face in all frames), the outline closed. Each pose's json keeps where the head box
went (its top-left square), for rig_neeko to place the pose.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage, signal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_neeko_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "neeko", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "neeko", "hd")
NAMES = ["stance", "thrust", "kick", "pounce", "tuck", "throw_air", "coil", "fling", "hunch", "soar", "land",
         "run1", "run2", "run3", "run4", "twirl", "sit"]
HEAD = (0, 41, 4, 49)           # rows / columns of the head box in hd/idle.png (ends exclusive): 1_head.png of the pack
# the design's head to paste (x, y square edges on hd/idle.png): the quills, the face and the hair round it down to the
# chin - not the neck under the chin
HEAD_POLY = [(4.0, 0.0), (49.0, 0.0), (49.0, 41.0), (34.0, 41.0), (33.0, 39.0), (26.0, 39.0), (25.0, 41.0),
             (4.0, 41.0)]
SCALES = np.arange(7.0, 15.01, 0.25)


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"neeko-pose-{name}.png"))).convert("RGBA"))


def head_box(idle):
    r0, r1, c0, c1 = HEAD
    return idle[r0:r1, c0:c1]


def match_head(a, head, scales=SCALES, half=2, angles=(0,)):
    """(px a square, x, y, cost, angle): the scale, the top-left (picture px) and the tilt where the design's head box,
    each square s x s px, lies best on the picture - the mean colour distance over the head's opaque squares, the
    picture's clear pixels counted as far off (a masked SSD by FFT, at 1 / half size). With a tilt the head box is
    turned about its middle and (x, y) is where the upright box's top-left would be (its middle where the turned one's
    is)."""
    small = a[::half, ::half]
    op = small[..., 3] >= 128
    A = small[..., :3].astype(float) / 255.0
    A[~op] = (0.0, 1.0, 0.0)                                   # clear: far from every colour of the head
    best = None
    for s in scales:
        k = s / half
        H, W = int(round(head.shape[0] * k)), int(round(head.shape[1] * k))
        ys = np.minimum((np.arange(H) / k).astype(int), head.shape[0] - 1)
        xs = np.minimum((np.arange(W) / k).astype(int), head.shape[1] - 1)
        T0 = head[np.ix_(ys, xs)]
        for ang in angles:
            T = T0 if not ang else np.asarray(Image.fromarray(T0).rotate(ang, resample=Image.NEAREST, expand=True))
            M = (T[..., 3] > 0).astype(float)
            Tc = T[..., :3].astype(float) / 255.0
            n = M.sum()
            ssd = np.zeros((A.shape[0] - T.shape[0] + 1, A.shape[1] - T.shape[1] + 1))
            for c in range(3):
                ssd += signal.fftconvolve(A[..., c] ** 2, M[::-1, ::-1], mode="valid")
                ssd -= 2 * signal.fftconvolve(A[..., c], (M * Tc[..., c])[::-1, ::-1], mode="valid")
                ssd += (M * Tc[..., c] ** 2).sum()
            ssd /= n
            j, i = np.unravel_index(np.argmin(ssd), ssd.shape)
            cost = float(ssd[j, i])
            if best is None or cost < best[0]:
                # the upright box with the same middle as the turned one
                cx, cy = (i + T.shape[1] / 2) * half, (j + T.shape[0] / 2) * half
                best = (cost, float(s), int(round(cx - W * half / 2)), int(round(cy - H * half / 2)), ang)
    return best[1], best[2], best[3], best[0], best[4]


TILTED = {}                     # the poses whose head Codex drew tipped (none so far)
HEAD_W, HEAD_H = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]
# the body round the matched head: BODY times the head's squares (measured below, --measure)
BODY_ALL = 1.0
BODY = {}


def sample_grid(a, s, ox, oy):
    """One square per s x s px cell, the cells' lines through (ox, oy): opaque when most of it is, the median colour.
    -> (squares, the cell index of (ox, oy))."""
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    i0 = int(np.floor((xs.min() - ox) / s))
    j0 = int(np.floor((ys.min() - oy) / s))
    i1 = int(np.ceil((xs.max() + 1 - ox) / s))
    j1 = int(np.ceil((ys.max() + 1 - oy) / s))
    out = np.zeros((j1 - j0, i1 - i0, 4), np.uint8)
    for j in range(j0, j1):
        ya, yb = int(round(oy + j * s)), int(round(oy + (j + 1) * s))
        for i in range(i0, i1):
            xa, xb = int(round(ox + i * s)), int(round(ox + (i + 1) * s))
            m = op[max(0, ya):max(0, yb), max(0, xa):max(0, xb)]
            if m.size and m.mean() > 0.5:
                out[j - j0, i - i0, :3] = np.median(a[max(0, ya):yb, max(0, xa):xb][m][:, :3], 0)
                out[j - j0, i - i0, 3] = 255
    return out, (-i0, -j0)


def head_mask(idle):
    img = Image.new("L", (idle.shape[1], idle.shape[0]), 0)
    ImageDraw.Draw(img).polygon(HEAD_POLY, fill=255)
    return (np.asarray(img) > 0) & (idle[..., 3] > 0)


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


def matched(name, idle, again=False):
    """match_head's (px a square, x, y, cost, tilt) for a pose, kept in hd/pose_<name>.json ("match") once found (the
    search takes a minute a pose)."""
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    return match_head(raw(name), head_box(idle), angles=TILTED.get(name, (0,)))


def fit_of(name):
    """Codex's whole-pose shrink for this pose (manifest.json whole_pose_fit: 1 for most)."""
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
    return next(float(p["whole_pose_fit"]) for p in man["poses"] if p["pose"] == name)


def pixel_1x(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"neeko-pose-{name}.png"))).convert("RGBA")).copy()


CHIN = (26.0, 39.0)             # the chin in the head box (squares from its top-left): where the design's head sits on the neck
SPECK = 120                     # loose bits smaller than this (squares) are what Codex's own head left round the design's


def read(name, idle, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    body's squares in px, the head match's cost and tilt).
    The BODY is read on the skeleton's own squares: the pack's 10 px times Codex's whole-pose shrink (pixel_1x as it is
    where it did not shrink; the 1254 picture sampled on 10 x fit px squares where it did), so every pose's limbs keep
    the design's size. Codex's HEAD came out 0-45% bigger than the design's round those bodies (the match's scale against
    the body's squares): its head (HEAD_POLY at that size) is taken out and the design's head put in at the design's
    size, its chin on Codex's chin - the same face and the same head size as the idle in every frame."""
    s, hx, hy, cost, ang = match
    fit = fit_of(name)
    g = 10.0 * fit
    if fit >= 0.999:
        fig = pixel_1x(name)
    else:
        fig, (ci, cj) = sample_grid(raw(name), g, 0.0, 0.0)
        big0 = np.zeros((int(np.ceil(1254 / g)) + 2, int(np.ceil(1254 / g)) + 2, 4), np.uint8)
        y0, x0 = -cj, -ci
        big0[y0 + 0:y0 + fig.shape[0], x0 + 0:x0 + fig.shape[1]] = fig
        fig = big0
    fig = snap(fig, idle)
    r = s / g                                            # Codex's head against the design's, on the body's squares
    bx, by = hx / g, hy / g                              # Codex's head box's top-left in body squares
    # Codex's head out: its HEAD_POLY at r times the size
    r0, _, c0, _ = HEAD
    poly = [((x - c0) * r + bx, (y - r0) * r + by) for x, y in HEAD_POLY]
    m = Image.new("L", (fig.shape[1], fig.shape[0]), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    fig[np.asarray(m) > 0] = 0
    # the design's head in, its chin on Codex's chin
    chin = (bx + CHIN[0] * r, by + CHIN[1] * r)
    ox, oy = int(round(chin[0] - CHIN[0])), int(round(chin[1] - CHIN[1]))
    hm = head_mask(idle)
    ys, xs = np.nonzero(hm)
    pad = 24
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    big[ys - r0 + oy + pad, xs - c0 + ox + pad] = idle[ys, xs]
    # the bits of Codex's bigger head left outside the design's (hair and quill tips, loose specks) go
    lbl, n = ndimage.label(big[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        size = ndimage.sum(big[..., 3] > 0, lbl, range(1, n + 1))
        for j in range(1, n + 1):
            if size[j - 1] < SPECK:
                big[lbl == j] = 0
    big = finish(big)                                    # one more square of padding round it
    ys2, xs2 = np.nonzero(big[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big[y0:ys2.max() + 1, x0:xs2.max() + 1], (ox + pad + 1 - x0, oy + pad + 1 - y0), g, cost, ang


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--rematch", action="store_true", help="search the heads again (else the json's match)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    if a.measure:
        head = head_box(idle)
        for n in NAMES:
            s, x, y, cost, ang = match_head(raw(n), head, angles=TILTED.get(n, (0,)))
            print(f"{n:9s} {s:5.2f} px a square, head at ({x}, {y}) tilted {ang}, cost {cost:.4f}")
        return
    figs = {}
    for n in NAMES:
        m = matched(n, idle, a.rematch)
        fig, at, s, cost, ang = read(n, idle, m)
        figs[n] = (fig, at, m)
        print(f"{n:9s} body {s:5.2f} px a square, head {m[0] / s:.2f} x the design's, cost {cost:.4f} -> "
              f"{fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 5
        tiles = [("design", idle)] + [(n, f) for n, (f, _, _) in figs.items()]
        Hm = max(t.shape[0] for _, t in tiles)
        W = sum(t.shape[1] * z + 12 for _, t in tiles)
        sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
        dr = ImageDraw.Draw(sheet)
        x = 0
        for n, t in tiles:
            sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
            dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
            x += t.shape[1] * z + 12
        sheet.convert("RGB").save(lp(os.path.join(a.sheet, "neeko_poses.png")))
        print(os.path.join(a.sheet, "neeko_poses.png"))
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, f)


if __name__ == "__main__":
    main()

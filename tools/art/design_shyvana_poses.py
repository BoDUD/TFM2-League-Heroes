#!/usr/bin/env python3
"""Shyvana's Codex poses (assets/source/shyvana/codex_poses: POSE_PROMPTS.md, ten of League's whole-body poses of her
human form and four run frames on skeletons) read back at the design's scale, in its colours, with the design's own head.

    python tools/art/design_shyvana_poses.py --measure        # each pose's scale and head position (the head matched)
    python tools/art/design_shyvana_poses.py --sheet DIR      # all poses beside the design (5x)
    python tools/art/design_shyvana_poses.py                  # writes assets/source/shyvana/hd/pose_<name>.png (+ .json)
    python tools/art/design_shyvana_poses.py --rematch        # the same, the heads searched again (else the json's)

Codex drew every pose bigger than the 14 px asked and not all at one size (regrid's squares 9-13 px; the material areas
against the design's gave 11.5-16.3 px a square, the folded poses low because they hide their legs). Every pose copies
the design's head (1_head.png), so the head itself gives the scale: the design's head box (HEAD, the horn crown, the face
and the hair round it) scaled 10-18 px a square is matched against the picture (masked colour distance by FFT, at half
size), the best scale and place kept. The bodies round those heads are BODY_ALL (1.2) times the design's, so the picture
is sampled on squares that much bigger, the grid laid so the matched head box keeps its middle (a square opaque when
most of it is, the median colour), every colour snapped to the design's own (Lab), the
design's head pasted square for square on Codex's head's middle (HEAD_POLY: the crown, the face and the hair over it,
never the neck or the shoulders - one face in all frames), the outline closed. Each pose's json keeps where the head box went (its
top-left square), for rig_shyvana to place the pose.
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
from design_shyvana_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shyvana", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "shyvana", "hd")
NAMES = ["crouch", "rise", "slash", "flip", "sweep", "throw", "leap", "stagger", "kneel", "collapse",
         "run1", "run2", "run3", "run4"]
HEAD = (0, 21, 13, 40)          # rows / columns of the head box in hd/idle.png (ends exclusive): 1_head.png of the pack
# the design's head to paste (x, y square edges on hd/idle.png): the horn crown, the face and the hair framing it down to
# the chin - not the hair hanging down the back (Codex's flows with each pose) nor the neck
HEAD_POLY = [(13.0, 0.0), (40.0, 0.0), (40.0, 12.0), (34.0, 13.0), (33.0, 21.0), (21.0, 21.0), (19.0, 16.0),
             (13.0, 13.0)]
SCALES = np.arange(10.0, 18.01, 0.25)


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"shyvana-pose-{name}.png"))).convert("RGBA"))


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


TILTED = {"flip": range(-60, 61, 10), "stagger": range(-50, 51, 10), "kneel": range(-50, 51, 10),
          "collapse": range(-60, 61, 10)}   # the poses whose head Codex drew tipped (upright, no match under 0.3)
HEAD_W, HEAD_H = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]
# Codex drew the bodies bigger round the design's head than the design has them: read at the head's squares, a pose
# stood 10-25% taller than the design (the head to the soles against the skeleton the pose was drawn on, bone lengths
# the design's own) and its limbs a square or two thicker. Read at 1.2 times the head's squares the limbs are the
# design's thickness, the upright poses (rise, run 2, stagger) the design's height (checked side by side at 1.0 / 1.1 /
# 1.2 / 1.3); the design's head then sits on a body of the design's size (one face, one build in every frame).
BODY_ALL = 1.2
BODY = {"leap": 1.3}            # the leap's head Codex drew smallest of all (11.5 px): at 1.2 she stood 73 tall


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


def read(name, idle, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt). The grid's squares are BODY times the matched head's, laid so
    the head box keeps its middle: the design's head goes on that middle."""
    a = raw(name)
    s, hx, hy, cost, ang = match
    s2 = s * BODY.get(name, BODY_ALL)
    cx, cy = hx + HEAD_W * s / 2, hy + HEAD_H * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - HEAD_W * s2 / 2, cy - HEAD_H * s2 / 2)
    s = s2
    fig = snap(fig, idle)
    hm = head_mask(idle)
    r0, _, c0, _ = HEAD
    ys, xs = np.nonzero(hm)
    pad = 24
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    big[ys - r0 + cj + pad, xs - c0 + ci + pad] = idle[ys, xs]
    big = finish(big)                                    # one more square of padding round it
    ys2, xs2 = np.nonzero(big[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), s, cost, ang


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
        print(f"{n:9s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
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
        sheet.convert("RGB").save(lp(os.path.join(a.sheet, "shyvana_poses.png")))
        print(os.path.join(a.sheet, "shyvana_poses.png"))
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, f)


if __name__ == "__main__":
    main()

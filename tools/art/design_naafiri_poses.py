#!/usr/bin/env python3
"""Naafiri's Codex poses (assets/source/naafiri/codex_poses: POSE_PROMPTS.md, thirteen of League's whole-body poses of her
and five of a packmate's, drawn on League's frames at the designs' size) read back at the designs' scale, in their
colours, with the designs' own heads where the pose holds the head as the design does.

    python tools/art/design_naafiri_poses.py --measure        # each pose's scale and head position (the head matched)
    python tools/art/design_naafiri_poses.py --check DIR      # each picture with its matched head box drawn on it
    python tools/art/design_naafiri_poses.py --sheet DIR      # all poses beside the designs (4x)
    python tools/art/design_naafiri_poses.py                  # writes assets/source/naafiri/hd/pose_<name>.png (+ .json)
    python tools/art/design_naafiri_poses.py --rematch        # the same, the heads searched again (else the json's)

design_shyvana_poses.py's way (its match_head, sample_grid and finish copied below): Codex drew the poses at their own sizes (its HANDOFF: not one grid, rear and rise too big),
but every pose copies the design's head (1_head_*.png), so the head gives the scale: the design's head box (HEADS: the
face with its eyes, white blaze, fangs and the dagger's hilt; the packmate's helmet blade, eye and teeth) scaled
SCALES px a square is matched against the picture (masked colour distance by FFT, at half size; the poses that turn the
head searched at TILTED angles), the best scale and place kept. The picture is then sampled on squares BODY times the
head's (Codex's bodies round the design's head, measured against the designs' lengths and heights), the grid laid so the
matched head box keeps its middle (a square opaque when most of it is, the median colour), every colour snapped to the
design's own (Lab), and - in the poses that hold the head as the design does - the design's own head
pasted square for square on the matched head's middle (one face in all frames); a pose with the jaws wide open or the head
thrown up (NOHEAD) is read at the scale that gives its body the design's area and keeps Codex's head in the design's
colours. The outline closed. Each pose's json keeps where the head
box went (its top-left square), for rig_naafiri to place the pose.
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
from design_naafiri_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "naafiri", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "naafiri", "hd")
HERS = ["crouch", "rear", "lunge", "fling", "flare", "dash", "rise", "howl", "lie", "run1", "run2", "run3", "run4"]
PACKS = ["p_run1", "p_run2", "p_run3", "p_run4", "p_bite"]
NAMES = HERS + PACKS
# design file, head box (rows, columns, ends exclusive) in it
DESIGN = {"her": ("idle.png", (17, 37, 49, 67)), "pack": ("pack.png", (4, 17, 33, 49))}
SCALES = {"her": np.arange(7.0, 16.01, 0.5), "pack": np.arange(12.0, 28.01, 1.0)}
# the poses whose head Codex drew turned (degrees counter-clockwise on screen): the fling's whipped down, the bite's
# diving, the lying head
TILTED = {"fling": range(-60, 1, 10), "p_bite": range(-60, 1, 10), "lie": range(-20, 21, 10)}
# Codex drew the bodies bigger round the design's head than the design has them (design_shyvana_poses's BODY_ALL 1.2):
# the square size from the figure's area against the design's (sqrt(opaque px / design squares)) was 0.81-0.98 of the
# matched head's, 0.884 on average for her nine matched poses and 0.862 for the packmate's five (2026-10-21), so the
# picture is sampled on squares 1 / that times the head's: the bodies come out the designs' size round the design's head
BODY_ALL = {"her": 1 / 0.884, "pack": 1 / 0.862}
# the poses Codex drew with the head in profile, raised or with the jaws wide (the crouch's side-on snout, the rear, the
# rise, the howl): the head box matched the body's red and blue stripes at any scale and tilt (the crouch's still, inside
# a box round its head and at 10-12.5 px), so they are read at the area's scale (the body the design's size) from their
# own bounding box and keep Codex's head in the design's colours
NOHEAD = {"crouch", "rear", "rise", "howl"}


# ---- design_shyvana_poses.py's readers (Shyvana's branch, 2026-10-21), kept here as they are
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


def who(name):
    return "pack" if name.startswith("p_") else "her"


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"naafiri-pose-{name}.png"))).convert("RGBA"))


def design(w):
    return np.asarray(Image.open(lp(os.path.join(OUT, DESIGN[w][0]))).convert("RGBA"))


def head_box(w):
    r0, r1, c0, c1 = DESIGN[w][1]
    return design(w)[r0:r1, c0:c1]


def matched(name, again=False):
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    w = who(name)
    return match_head(raw(name), head_box(w), scales=SCALES[w], angles=TILTED.get(name, (0,)))


def area_scale(name):
    """The square size (px) at which the picture's opaque area is the design's."""
    op = raw(name)[..., 3] >= 128
    return float(np.sqrt(op.sum() / (design(who(name))[..., 3] > 0).sum()))


def read(name, match):
    """The pose on the design's grid -> (figure, the head box's top-left square in it - for a NOHEAD pose its own top-left
    instead -, squares' px, cost, tilt)."""
    w = who(name)
    d = design(w)
    r0, r1, c0, c1 = DESIGN[w][1]
    HW, HH = c1 - c0, r1 - r0
    a = raw(name)
    s, hx, hy, cost, ang = match
    if name in NOHEAD:
        s2 = area_scale(name)
        ys, xs = np.nonzero(a[..., 3] >= 128)
        fig, (ci, cj) = sample_grid(a, s2, float(xs.min()), float(ys.min()))
    else:
        s2 = s * BODY_ALL[w]
        cx, cy = hx + HW * s / 2, hy + HH * s / 2
        fig, (ci, cj) = sample_grid(a, s2, cx - HW * s2 / 2, cy - HH * s2 / 2)
    fig = snap(fig, d)
    pad = 24
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if name not in NOHEAD:
        hm = np.zeros(d.shape[:2], bool)
        hm[r0:r1, c0:c1] = d[r0:r1, c0:c1, 3] > 0
        ys, xs = np.nonzero(hm)
        big[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
    big = finish(big)
    ys2, xs2 = np.nonzero(big[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), s2, cost, ang


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--check")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--rematch", action="store_true", help="search the heads again (else the json's match)")
    ap.add_argument("--only", help="these poses (comma separated)")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    if a.measure or a.check:
        res = {}
        for n in names:
            m = matched(n, again=True)
            res[n] = m
            op = raw(n)[..., 3] >= 128
            ys, xs = np.nonzero(op)
            dh, dw = design(who(n)).shape[:2]
            print(f"{n:7s} {m[0]:5.2f} px a square, head at ({m[1]}, {m[2]}) tilted {m[4]:4d}, cost {m[3]:.4f}; "
                  f"the picture {(xs.max() - xs.min() + 1) / m[0]:5.1f} x {(ys.max() - ys.min() + 1) / m[0]:5.1f} "
                  f"squares at that size (design {dw} x {dh})", flush=True)
            with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
                json.dump({"match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, f)
        if a.check:
            os.makedirs(lp(a.check), exist_ok=True)
            for n, (s, x, y, cost, ang) in res.items():
                r0, r1, c0, c1 = DESIGN[who(n)][1]
                im = Image.fromarray(raw(n)).convert("RGBA")
                bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
                bg.alpha_composite(im)
                dr = ImageDraw.Draw(bg)
                dr.rectangle([x, y, x + (c1 - c0) * s, y + (r1 - r0) * s], outline=(0, 160, 255, 255), width=4)
                dr.text((10, 10), f"{n} {s:.2f}px tilt {ang} cost {cost:.3f}", fill=(0, 0, 0, 255))
                bg.convert("RGB").save(lp(os.path.join(a.check, f"check_{n}.png")))
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:7s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design("her")), ("pack", design("pack"))] + [(n, f) for n, (f, _, _) in figs.items()]
        rows = [tiles[:8], tiles[8:]]
        Wd = max(sum(t.shape[1] * z + 12 for _, t in r) for r in rows)
        Hs = [max(t.shape[0] for _, t in r) * z + 24 for r in rows]
        sheet = Image.new("RGBA", (Wd, sum(Hs)), (90, 96, 90, 255))
        dr = ImageDraw.Draw(sheet)
        y = 0
        for r, H in zip(rows, Hs):
            x = 0
            for n, t in r:
                sheet.alpha_composite(big(t, z), (x, y + H - t.shape[0] * z))
                dr.text((x + 4, y + 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            y += H
        sheet.convert("RGB").save(lp(os.path.join(a.sheet, "naafiri_poses.png")))
        print(os.path.join(a.sheet, "naafiri_poses.png"))
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, f)


if __name__ == "__main__":
    main()

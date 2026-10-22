#!/usr/bin/env python3
"""Qiyana's Codex poses (assets/source/qiyana/codex_poses: POSE_PROMPTS.md, League's whole-body poses on skeletons with
the ring blade as a rigid prop, the user's qiyana_poses_done.zip) read back at the design's scale, in its colours, with
the design's own head - design_ksante_poses.py's way.

    python tools/art/design_qiyana_poses.py --measure        # each pose's scale and head position (the head matched)
    python tools/art/design_qiyana_poses.py --sheet DIR      # all poses beside the design (5x)
    python tools/art/design_qiyana_poses.py                  # writes assets/source/qiyana/hd/pose_<name>.png (+ .json)
    python tools/art/design_qiyana_poses.py --rematch        # the same, the heads searched again (else the json's)

Every pose copies the design's head (1_head.png of the pack), so the head gives the scale: the design's head box (HEAD:
the crest, the tiara, the hair and the face down to the chin) scaled over SCALES px a square is matched against the
picture (masked colour distance by FFT, at half size), the best scale and place kept. Codex drew the poses at 10-14.5 px
a square (asked 13) and kept its heads in proportion with its bodies this time (the heads matched at low cost, 0.06-0.32,
and the bodies read at the head's scale come out the design's size: legs, arms and the ring checked at 8x against
hd/idle.png - BODY corrects a pose whose body Codex drew bigger or smaller than its head). The picture is sampled on
squares of that size, laid so the matched head box keeps its middle (a square opaque when most of it is, the median
colour), every colour snapped to the design's own (Lab), the design's head pasted square for square there (one face in
all frames), the outline closed. Each pose's json keeps where the head box went (its top-left square), for rig_qiyana to
place the pose.
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
import design_shyvana_poses as SP  # noqa: E402  match_head, sample_grid, finish
from design_chogath_side import snap  # noqa: E402
from design_qiyana_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "qiyana", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "qiyana", "hd")
NAMES = ["a_wind", "a_strike", "q_wind", "q_sweep", "q_end", "e_dash", "e_hit", "r_leap", "r_slam",
         "run1", "run2", "run3", "run4", "d_fall", "d_lie"]
HEAD = (0, 27, 20, 48)          # rows / columns of the head box in hd/idle.png (ends exclusive): crest to chin
SCALES = np.arange(9.0, 18.01, 0.25)
TILTED = {"d_fall": range(-20, 21, 10), "d_lie": range(-20, 21, 10), "e_dash": range(-20, 21, 10)}
BODY = {}                       # pose -> the body's squares over the head's (1 where Codex kept them in proportion)
SPECK = 6                       # loose bits smaller than this (squares) left round the pasted head go


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"qiyana-pose-{name}.png"))).convert("RGBA"))


def design():
    return np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA")).copy()


def head_box(d):
    r0, r1, c0, c1 = HEAD
    return d[r0:r1, c0:c1].copy()


def matched(name, again=False):
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    return SP.match_head(raw(name), head_box(design()), scales=SCALES, angles=TILTED.get(name, (0,)))


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    r0, r1, c0, c1 = HEAD
    hw, hh = c1 - c0, r1 - r0
    a = raw(name)
    s, hx, hy, cost, ang = match
    s2 = s * BODY.get(name, 1.0)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = SP.sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    pad = 24
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    head = d[r0:r1, c0:c1]
    m = head[..., 3] > 0
    reg = big[cj + pad:cj + pad + hh, ci + pad:ci + pad + hw]
    reg[:] = np.where(m[..., None], head, reg)
    # Codex's own hair / crest squares sticking out past the design's head box top and sides go: they are its head's,
    # bigger or placed differently (the pose's own hair below the chin stays)
    lbl, n = ndimage.label(big[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        size = ndimage.sum(big[..., 3] > 0, lbl, range(1, n + 1))
        for j in range(1, n + 1):
            if size[j - 1] < SPECK:
                big[lbl == j] = 0
    big = SP.finish(big)
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
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--rematch", action="store_true", help="search the heads again (else the json's match)")
    ap.add_argument("--only", help="comma-separated pose names")
    a = ap.parse_args()
    names = [n for n in NAMES if not a.only or n in a.only.split(",")]
    if a.measure:
        for n in names:
            s, x, y, cost, ang = SP.match_head(raw(n), head_box(design()), scales=SCALES, angles=TILTED.get(n, (0,)))
            print(f"{n:9s} {s:5.2f} px a square, head at ({x}, {y}) tilted {ang}, cost {cost:.4f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:9s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 5
        tiles = [("design", design())] + [(n, figs[n][0]) for n in names]
        rows = [tiles[:8], tiles[8:]]
        imgs = []
        for row in rows:
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            imgs.append(sheet)
        W = max(i.width for i in imgs)
        out = Image.new("RGBA", (W, sum(i.height for i in imgs)), (90, 96, 90, 255))
        y = 0
        for i in imgs:
            out.alpha_composite(i, (0, y))
            y += i.height
        path = os.path.join(a.sheet, "qiyana_poses.png")
        out.convert("RGB").save(lp(path))
        print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, f)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Udyr's Codex poses (assets/source/udyr/codex_poses: POSE_PROMPTS.md, 29 key poses of League's clips on the four
stance designs) read back at the design's scale, in its colours, with the design's own head (design_shyvana_poses.py's
way).

    python tools/art/design_udyr_poses.py --measure        # each pose's scale and head position (the head matched)
    python tools/art/design_udyr_poses.py --sheet DIR      # all poses beside their stance's design (5x)
    python tools/art/design_udyr_poses.py                  # writes assets/source/udyr/hd/pose_<name>.png (+ .json)
    python tools/art/design_udyr_poses.py --rematch        # the same, the heads searched again (else the json's)

Every pose copies its stance design's head (1_head_<stance>.png of the pack), so the head gives the scale: the design's
head box (HEAD) scaled over a range of px a square is matched against the picture (masked colour distance by FFT, at half
size), the best scale and place kept. The picture is sampled on squares BODY times that size, the grid laid so the
matched head box keeps its middle (a square opaque when most of it is, the median colour), every colour snapped to the
stance design's own (Lab), the design's head pasted square for square on Codex's head's middle (HEAD_POLY: the hair's
crown, the face, the feather braid's top and the beard - one face in all frames), the outline closed. Each pose's json
keeps where the head box went (its top-left square), for rig_udyr to place the pose.
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
from design_udyr_model import lp  # noqa: E402
import pack_udyr_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "udyr", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "udyr", "hd")
NAMES = list(PK.POSES)
DESIGN = {"A": "idle.png", "Q": "q_idle.png", "E": "e_idle.png", "R": "r_idle.png"}
HEAD = {st: v[5] for st, v in PK.STANCES.items()}          # rows / columns of each design's head box (ends exclusive)
# each design's head to paste (x, y square edges on hd/<design>): the hair's crown, the face, the top of the feather braid
# and the beard - not the dreadlocks hanging down the back and shoulders (Codex's swing with each pose) nor the neck
HEAD_POLY = {
    "A": [(20.0, 0.0), (34.0, 0.0), (36.0, 8.0), (35.0, 21.0), (30.0, 22.0), (24.0, 22.0), (21.0, 14.0), (20.0, 6.0)],
    "Q": [(37.0, 11.0), (49.0, 11.0), (50.0, 18.0), (48.0, 30.0), (41.0, 30.0), (38.0, 22.0)],
    "E": [(42.0, 19.0), (53.0, 19.0), (54.0, 27.0), (52.0, 38.0), (45.0, 38.0), (42.0, 28.0)],
    "R": [(58.0, 23.0), (71.0, 23.0), (72.0, 32.0), (70.0, 43.0), (62.0, 43.0), (58.0, 32.0)],
}
SCALES = np.arange(8.0, 22.01, 0.25)
TILTED = {"d_hit": range(-40, 41, 10), "d_kneel": range(-40, 41, 10), "e_slam": range(-50, 51, 10),
          "e_leap": range(-30, 31, 10), "q_swipe": range(-30, 31, 10), "e_hook": range(-30, 31, 10),
          "r_thrust": range(-30, 31, 10), "r_flap": range(-30, 31, 10)}
BODY_ALL = 1.0                  # set after the delivery (the bodies against the head, design_shyvana_poses' BODY_ALL)
BODY = {}


def stance(name):
    return PK.POSES[name][0]


def design(st):
    return np.asarray(Image.open(lp(os.path.join(OUT, DESIGN[st]))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"udyr-pose-{name}.png"))).convert("RGBA"))


def head_box(d, st):
    r0, r1, c0, c1 = HEAD[st]
    return d[r0:r1, c0:c1]


def head_mask(d, st):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(HEAD_POLY[st], fill=255)
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
    st = stance(name)
    return match_head(raw(name), head_box(design(st), st), scales=SCALES, angles=TILTED.get(name, (0,)))


def read(name, match):
    """The pose on its design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    st = stance(name)
    d = design(st)
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = HEAD[st]
    hw, hh = c1 - c0, r1 - r0
    s2 = s * BODY.get(name, BODY_ALL)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    hm = head_mask(d, st)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if not ang:                                        # a tipped head keeps Codex's own (the design's is upright)
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
    big_ = finish(big_)
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), s2, cost, ang


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
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    if a.measure:
        for n in names:
            st = stance(n)
            s, x, y, cost, ang = match_head(raw(n), head_box(design(st), st), scales=SCALES,
                                            angles=TILTED.get(n, (0,)))
            print(f"{n:9s} {st} {s:5.2f} px a square, head at ({x}, {y}) tilted {ang}, cost {cost:.4f}")
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
        for st in DESIGN:
            tiles = [("design", design(st))] + [(n, f) for n, (f, _, _) in figs.items() if stance(n) == st]
            if len(tiles) == 1:
                continue
            Hm = max(t.shape[0] for _, t in tiles)
            W = sum(t.shape[1] * z + 12 for _, t in tiles)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in tiles:
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"udyr_poses_{st}.png")
            sheet.convert("RGB").save(lp(path))
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

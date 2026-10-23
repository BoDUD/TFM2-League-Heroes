#!/usr/bin/env python3
"""Azir's Codex poses (assets/source/azir/codex_poses/azir-poses: POSE_PROMPTS.md, 15 key poses of his League clips on
the design) read back at the design's scale, in its colours, with the design's own helmet (design_aurora_poses.py's way).

    python tools/art/design_azir_poses.py --measure        # each pose's helmet match over a range of scales
    python tools/art/design_azir_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_azir_poses.py                  # writes assets/source/azir/hd/pose_<name>.png (+ .json)
    python tools/art/design_azir_poses.py --rematch        # the same, the helmets searched again (else the json's)

His poses copy the design's helmet, so the helmet gives the scale: the helmet (the polygon POLY on hd/idle.png: the
crest, the back wing, the purple hood, the beak, the glowing eye and the cheek wing - not the near shoulder plate under
it) scaled over a range of px a square is matched against the picture (design_shyvana_poses.match_head on the head box
with everything outside POLY clear), the pose sampled on squares of the helmet's own size, the grid laid so the matched
head box keeps its middle, every colour snapped to the design's own (Lab), the design's helmet pasted square for square
on Codex's helmet's place (one face in all frames), the outline closed. Each pose's json keeps where the head box went
(its top-left square), for rig_azir to place the pose.
The picture read is Codex's raw draft (raw/azir-pose-<name>.png, soft alpha; raw/rejected/ never). The summons' poses
(s_lift s_stab g_push1 g_push2) are read by design_azir_summons.py.
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
from design_azir_hd import lp  # noqa: E402
import pack_azir_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "azir", "codex_poses", "azir-poses")
OUT = os.path.join(ROOT, "assets", "source", "azir", "hd")
# the helmet (square edges on hd/idle.png): the crest, the back wing, the purple hood, the beak, the eye and the cheek
# wing - not the near shoulder plate below the hood (rows 32 on, columns < 30), nor the sceptre
POLY = [(22.0, 18.0), (25.0, 17.0), (27.0, 15.5), (30.0, 15.5), (32.0, 18.0), (35.0, 20.0), (38.0, 22.0), (41.0, 25.0),
        (43.0, 28.0), (44.0, 32.0), (44.0, 36.0), (37.0, 36.0), (35.0, 34.5), (30.0, 34.5), (27.0, 33.5), (24.0, 31.5),
        (21.0, 29.0), (20.0, 26.0), (20.0, 21.0)]
SCALES = np.arange(9.0, 18.01, 0.25)
TILTED = {"d_stagger": range(-30, 31, 10), "d_kneel": range(-20, 21, 10)}
# px a square set by hand where the helmet's own does not fit the body: Codex drew the bodies 3-12% bigger against the
# helmet than the design (crest to soles 60-64 rows read at the helmet's scale where the skeleton gives 54-58), so each
# is read at the scale that brings its crest-to-soles to its skeleton's (pack_azir_poses.build, the lowest foot); the
# four runs share one scale (15.5: no size flicker in the cycle); r_sweep's lowest square is the sceptre's head in front
# of him, so its feet were matched by eye; d_kneel at 14.5 (the kneel came drawn as tall as the standing design)
SCALE = {"c_wind": 15.75, "c_point": 14.5, "q_wind": 15.0, "q_thrust": 12.5, "e_land": 13.75, "r_raise": 14.75,
         "r_lift": 14.0, "r_sweep": 15.5, "run1": 15.5, "run2": 15.5, "run3": 15.5, "run4": 15.5, "d_stagger": 14.5,
         "d_kneel": 14.5}
UPRIGHT = {"d_stagger"}   # matched tilted (20 degrees, reeling back) but given the design's upright helmet (one face)
CACHE = "C:/t/az_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"azir-pose-{name}.png"))).convert("RGBA"))


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def head_box(d):
    """The head box with everything outside POLY clear (the sceptre never steers the match)."""
    r0, r1, c0, c1 = PK.HEAD
    h = d.copy()
    h[~head_mask(d)] = 0
    return h[r0:r1, c0:c1]


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
    m = match_head(raw(name), head_box(design()), scales=SCALES, angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = PK.HEAD
    hw, hh = c1 - c0, r1 - r0
    s2 = SCALE.get(name, s)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if not ang or name in UPRIGHT:                     # a tipped head keeps Codex's own unless UPRIGHT
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
    ap.add_argument("--rematch", action="store_true", help="search the heads again (else the json's)")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    if a.measure:
        d = design()
        for n in names:
            r = raw(n)
            s, x, y, cost, ang = match_head(r, head_box(d), scales=SCALES, angles=TILTED.get(n, (0,)))
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
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
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
            path = os.path.join(a.sheet, f"azir_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, fh)


if __name__ == "__main__":
    main()

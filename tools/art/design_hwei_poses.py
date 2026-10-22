#!/usr/bin/env python3
"""Hwei's Codex poses (assets/source/hwei/codex_poses/hwei-poses: POSE_PROMPTS.md, 21 key poses of League's clips on the
design) read back at the design's scale, in its colours, with the design's own head (design_udyr_poses.py's way).

    python tools/art/design_hwei_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_hwei_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_hwei_poses.py                  # writes assets/source/hwei/hd/pose_<name>.png (+ .json)
    python tools/art/design_hwei_poses.py --rematch        # the same, the heads searched again (else the json's)

Every pose copies the design's head (1_head.png of the pack), so the head gives the scale: the design's head box (HEAD,
hd/idle.png rows 14-38, columns 17-46) scaled over a range of px a square is matched against the picture (masked colour
distance by FFT, at half size; design_shyvana_poses.match_head), the best scale and place kept. Codex drew the poses
about 1.3x the size asked (its HANDOFF: the grid, the soles' line and the lengths not met) but the heads and bodies in
the design's proportions, so the pose is sampled on squares of the head's own size (BODY 1.0; a pose that differs is
set in SCALE), the grid laid so the matched head box keeps its middle (a square opaque when most of it is, the median
colour), every colour snapped to the design's own (Lab), the design's head pasted square for square on Codex's head's
place (HEAD_POLY: the hair, the face, the earrings and the choker - one face in all frames), the outline closed. Codex's
crescent of paint stays its own (it copied the design's; a little sway between poses reads as its float). Codex's
brush, 1.1-1.5 times the design's, is replaced by the design's at the same grip and direction (brush_hwei.normalize,
BRUSH: read at 7x on the readbacks). Each pose's json keeps where the head box went (its top-left square) and the brush
(grip, direction), for rig_hwei to place the pose.
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
from design_hwei_hd import lp  # noqa: E402
import brush_hwei as BR  # noqa: E402
import pack_hwei_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "hwei", "codex_poses", "hwei-poses")
OUT = os.path.join(ROOT, "assets", "source", "hwei", "hd")
NAMES = list(PK.POSES)
HEAD = PK.HEAD                                   # rows / columns of the design's head box (ends exclusive)
# the design's head to paste (x, y square edges on hd/idle.png): the hair's crown and its fringe, the face, the earrings
# and the choker - not the crescent above (Codex's own) nor the collar
HEAD_POLY = [(17.0, 15.0), (31.0, 14.0), (44.0, 17.0), (47.0, 25.0), (45.0, 33.0), (39.0, 37.0), (29.0, 38.0),
             (20.0, 36.0), (16.0, 29.0)]
SCALES = np.arange(10.0, 24.01, 0.25)
TILTED = {"d_kneel": range(-30, 31, 10), "d_stagger": range(-30, 31, 10)}
BODY = 1.0
SCALE = {}                                       # px a square set by hand where the head's own does not fit the body
CACHE = "C:/t/hw_work/pose_match_cache.json"
# a_wind is left out: Codex drew the brush held in both hands across his waist, 40 squares between the hands - the
# design's brush (26.5 from the grip to the point) cannot lie there; the attack winds up on another pose (rig_hwei)
SKIP = {"a_wind"}
# each pose's brush on its readback (squares, before brush_hwei.normalize): the hand on the shaft (None: lying on the
# ground), the point's end, the butt's end (None: hidden in the sleeve) - read at 7x, 2026-10-22
BRUSH = {
    "a_flick": dict(grip=(54, 32), tip=(86, 27), butt=None),
    "q_wind": dict(grip=(53, 21), tip=(89, 2), butt=(48, 26)),
    "q_throw": dict(grip=(54, 59), tip=(80, 81), butt=None),
    "qw_raise": dict(grip=(57, 41), tip=(59, 2), butt=(57, 54)),
    "qw_point": dict(grip=(60, 60), tip=(87, 77), butt=None),
    "qe_raise": dict(grip=(53, 42), tip=(59, 74), butt=(51, 27)),
    "qe_slam": dict(grip=(54, 49), tip=(75, 73), butt=(51, 41)),
    "ew_low": dict(grip=(29, 48), tip=(1, 68), butt=(37, 45)),
    "ew_high": dict(grip=(53, 31), tip=(76, 1), butt=(48, 37)),
    "ee_wind": dict(grip=(33, 40), tip=(1, 40), butt=None),
    "ee_swing": dict(grip=(52, 56), tip=(78, 78), butt=None),
    "r_open": dict(grip=(60, 51), tip=(91, 51), butt=None),
    "r_fling": dict(grip=(55, 43), tip=(91, 56), butt=None),
    "r_hop": dict(grip=(35, 43), tip=(1, 43), butt=None),
    "run1": dict(grip=(46, 53), tip=(68, 72), butt=None),
    "run2": dict(grip=(43, 52), tip=(66, 71), butt=None),
    "run3": dict(grip=(44, 54), tip=(68, 74), butt=None),
    "run4": dict(grip=(44, 56), tip=(70, 77), butt=None),
    "d_stagger": dict(grip=None, tip=(95, 75), butt=(49, 74)),
    "d_kneel": dict(grip=None, tip=(78, 62), butt=(37, 61)),
}


def design():
    return np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"hwei-pose-{name}-raw.png"))).convert("RGBA"))


def head_box(d):
    r0, r1, c0, c1 = HEAD
    return d[r0:r1, c0:c1]


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(HEAD_POLY, fill=255)
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
    if not again and os.path.isfile(CACHE):
        c = json.load(open(CACHE, encoding="utf-8"))
        if name in c:
            return tuple(c[name])
    m = match_head(raw(name), head_box(design()), scales=SCALES, angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(c, f)
    return m


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = HEAD
    hw, hh = c1 - c0, r1 - r0
    s2 = SCALE.get(name, s * BODY)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    hm = head_mask(d)
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
    names = a.only.split(",") if a.only else [n for n in NAMES if n not in SKIP]
    if a.measure:
        d = design()
        area_d = (d[..., 3] > 0).sum()
        for n in names:
            r = raw(n)
            s, x, y, cost, ang = match_head(r, head_box(d), scales=SCALES, angles=TILTED.get(n, (0,)))
            area = float(np.sqrt((r[..., 3] >= 128).sum() / area_d))
            print(f"{n:9s} head {s:5.2f} px a square at ({x}, {y}) tilted {ang}, cost {cost:.4f}; area {area:5.2f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        brush = None
        if n in BRUSH:                               # the design's brush in place of Codex's
            fig, (grip, deg), (dx, dy) = BR.normalize(fig, BRUSH[n])
            at = (at[0] + dx, at[1] + dy)
            brush = {"grip": [round(float(grip[0]), 2), round(float(grip[1]), 2)], "deg": round(float(deg), 1),
                     "lying": BRUSH[n]["grip"] is None}
        figs[n] = (fig, at, m, brush)
        print(f"{n:9s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, f) for n, (f, _, _, _) in figs.items()]
        rows = [tiles[i:i + 8] for i in range(0, len(tiles), 8)]
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
            path = os.path.join(a.sheet, f"hwei_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m, brush) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])], "brush": brush}, f)


if __name__ == "__main__":
    main()

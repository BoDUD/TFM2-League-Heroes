#!/usr/bin/env python3
"""Yorick's Codex poses (assets/source/yorick/codex_poses/yorick-poses: POSE_PROMPTS.md, 17 key poses of his League clips
on his design, 2026-10-25) read back at the design's scale, in its colours, with the design's own head
(design_yorick_poses.py's way).

    python tools/art/design_yorick_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_yorick_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_yorick_poses.py                  # writes assets/source/yorick/hd/pose_<name>.png (+ .json)
    python tools/art/design_yorick_poses.py --rematch        # the same, the heads searched again (else the json's)

His poses copy the design's head, so the head gives the scale: the head box (pack_yorick_poses.HEAD: the hood and the
face, hd/idle.png rows 19-43, columns 34-54) scaled over a range of px a square is matched against the picture
(design_shyvana_poses.match_head), the pose sampled on squares of the head's own size, the grid laid so the matched head
box keeps its middle, every colour snapped to the design's own (Lab), the design's head pasted square for square on
Codex's head's place (the polygon "poly": one face in all frames), the outline closed. Each pose's json keeps where the
head box went (its top-left square), for rig_yorick to place the pose.
Codex's raw pictures (raw/, 1254 canvases, soft alpha) are read, not its own 11 px cut: the head match sets the scale.
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
from design_yorick_hd import lp  # noqa: E402
import pack_yorick_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yorick", "codex_poses", "yorick-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "yorick", "hd")
# the hood and the face in it (the goatee down to the vest) - not the pauldrons beside it
POLY = [(39.0, 18.0), (49.0, 18.0), (53.0, 23.0), (53.0, 42.0), (36.0, 44.0), (34.0, 36.0), (35.0, 26.0)]
SCALES = np.arange(8.0, 15.01, 0.25)
TILTED = {"d_drop": range(-20, 21, 10)}
SCALE = {}                                       # px a square set by hand where the head's own does not fit the body
CACHE = "C:/t/yo_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    prefix = "yorick-pose-"
    return np.asarray(Image.open(lp(os.path.join(SRC, f"{prefix}{name}.png"))).convert("RGBA"))


def head_box(d):
    r0, r1, c0, c1 = PK.HEAD
    return d[r0:r1, c0:c1]


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
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
        for f, ref, group in (("yorick", "idle.png", NAMES),):
            tiles = [("design", design(ref))] + [(n, figs[n][0]) for n in group if n in figs]
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
                path = os.path.join(a.sheet, f"{f}_poses_{k}.png")
                sheet.convert("RGB").save(lp(path))
                print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        stem = f"pose_{n}"
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{stem}.png")))
        if at is not None:
            with open(lp(os.path.join(OUT, f"{stem}.json")), "w", encoding="utf-8") as fh:
                json.dump({"head_at": [int(at[0]), int(at[1])],
                           "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, fh)


if __name__ == "__main__":
    main()

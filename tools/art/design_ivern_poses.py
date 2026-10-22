#!/usr/bin/env python3
"""Ivern's and Daisy's Codex poses (assets/source/ivern/codex_poses/ivern-poses: POSE_PROMPTS.md, 15 key poses of his
League clips and 6 of Daisy's, on the designs) read back at the design's scale, in its colours, with the design's own
head (design_hwei_poses.py's way).

    python tools/art/design_ivern_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_ivern_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_ivern_poses.py                  # writes assets/source/ivern/hd/pose_<name>.png (+ .json)
    python tools/art/design_ivern_poses.py --rematch        # the same, the heads searched again (else the json's)

Every pose copies its design's head, so the head gives the scale: the design's head box (FIG[...]["head"]: Ivern's
mushroom, horns and face, hd/idle.png rows 0-25, columns 8-61; Daisy's sprout, stone head, flowers and crystal,
hd/daisy.png rows 0-39, columns 27-69) scaled over a range of px a square is matched against the picture (masked colour
distance by FFT, at half size; design_shyvana_poses.match_head), the best scale and place kept. The pose is sampled on
squares of the head's own size (BODY 1.0; a pose that differs is set in SCALE), the grid laid so the matched head box
keeps its middle (a square opaque when most of it is, the median colour), every colour snapped to the design's own
(Lab), the design's head pasted square for square on Codex's head's place (the polygon "poly": one face in all
frames), the outline closed. Each pose's json keeps where the head box went (its top-left square), for rig_ivern to
place the pose. Daisy's poses are written as hd/daisy_<name>.png.
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
from design_ivern_hd import lp  # noqa: E402
import pack_ivern_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ivern", "codex_poses", "ivern-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "ivern", "hd")
# the two figures: design file, head box (rows / columns, ends exclusive), the head to paste (x, y square edges on the
# design), the raw files' prefix, the written files' prefix, the poses
FIG = {
    "ivern": dict(design="idle.png", head=PK.HEAD, prefix="ivern-pose-", out="pose_", names=list(PK.POSES),
                  # the mushroom, both horns with the wooden ring, the face and the beard's top round the grin - not the
                  # twig hand by the near horn
                  poly=[(9.0, 5.0), (27.0, 0.0), (40.0, 0.0), (61.0, 4.0), (61.0, 17.0), (52.0, 21.0), (47.0, 25.0),
                        (27.0, 25.0), (19.0, 20.0), (9.0, 15.0)]),
    "daisy": dict(design="daisy.png", head=(0, 39, 27, 69), prefix="ivern-daisy-", out="daisy_", names=list(PK.DAISY),
                  # the clover sprout, the dark stone head, the two flowers and the crystal
                  poly=[(44.0, 0.0), (51.0, 0.0), (57.0, 7.0), (66.0, 12.0), (66.0, 36.0), (58.0, 39.0), (37.0, 39.0),
                        (29.0, 36.0), (29.0, 12.0), (38.0, 7.0)]),
}
SCALES = np.arange(9.0, 20.01, 0.25)             # 53 squares of horns x 20 px fill the 1254 canvas
TILTED = {"d_slump": range(-20, 21, 10), "d_stagger": range(-20, 21, 10)}
BODY = 1.0
SCALE = {}                                       # px a square set by hand where the head's own does not fit the body
CACHE = "C:/t/iv_work/pose_match_cache.json"
SKIP = set()


def fig_of(name):
    return "daisy" if name in PK.DAISY else "ivern"


def design(f):
    return np.asarray(Image.open(lp(os.path.join(OUT, FIG[f]["design"]))).convert("RGBA"))


def raw(name):
    f = FIG[fig_of(name)]
    return np.asarray(Image.open(lp(os.path.join(SRC, f"{f['prefix']}{name}.png"))).convert("RGBA"))


def head_box(f, d):
    r0, r1, c0, c1 = FIG[f]["head"]
    return d[r0:r1, c0:c1]


def head_mask(f, d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(FIG[f]["poly"], fill=255)
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
    """match_head's (px a square, x, y, cost, tilt) for a pose, kept in hd/<out><name>.json ("match") once found."""
    f = fig_of(name)
    path = lp(os.path.join(OUT, f"{FIG[f]['out']}{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    if not again and os.path.isfile(CACHE):
        c = json.load(open(CACHE, encoding="utf-8"))
        if name in c:
            return tuple(c[name])
    m = match_head(raw(name), head_box(f, design(f)), scales=SCALES, angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    f = fig_of(name)
    d = design(f)
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = FIG[f]["head"]
    hw, hh = c1 - c0, r1 - r0
    s2 = SCALE.get(name, s * BODY)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    hm = head_mask(f, d)
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
    every = FIG["ivern"]["names"] + FIG["daisy"]["names"]
    names = a.only.split(",") if a.only else [n for n in every if n not in SKIP]
    if a.measure:
        for n in names:
            f = fig_of(n)
            d = design(f)
            r = raw(n)
            s, x, y, cost, ang = match_head(r, head_box(f, d), scales=SCALES, angles=TILTED.get(n, (0,)))
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
        for f in ("ivern", "daisy"):
            tiles = [("design", design(f))] + [(n, t) for n, (t, _, _) in figs.items() if fig_of(n) == f]
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
        stem = FIG[fig_of(n)]["out"] + n
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{stem}.png")))
        with open(lp(os.path.join(OUT, f"{stem}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, fh)


if __name__ == "__main__":
    main()

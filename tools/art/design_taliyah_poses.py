#!/usr/bin/env python3
"""Taliyah's Codex poses (assets/source/taliyah/codex_poses/taliyah-poses: POSE_PROMPTS.md, 14 key poses of her League
clips on the design) read back at the design's scale, in its colours, with the design's own face (design_singed_poses.py's
way).

    python tools/art/design_taliyah_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_taliyah_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_taliyah_poses.py                  # writes assets/source/taliyah/hd/pose_<name>.png (+ .json)
    python tools/art/design_taliyah_poses.py --rematch        # the same, the heads searched again (else the json's)

Her poses copy the design's head, so the head gives the scale: the head (the polygon POLY on hd/idle.png: the gold
ornament, the middle of the piled hair, the brows, the eyes, the mouth and the chin - not the hair's outer tufts, which
Codex drew a little differently in every pose) scaled over a range of px a square is matched against the picture
(design_shyvana_poses.match_head on the head box with everything outside POLY clear), the pose sampled on squares of the
head's own size, the grid laid so the matched head box keeps its middle, every colour snapped to the design's own (Lab),
the design's POLY squares pasted on Codex's head's place (one face in all frames), the outline closed. Each pose's json
keeps where the head box went (its top-left square), for rig_taliyah to place the pose. The picture read is
raw/taliyah-pose-<name>.png (Codex's own pixel_1x is cut on an 11-px grid from the corner while it drew on ~9.8 px
squares: not used).
Codex drew every pose with a soft edge (alpha 1-254 on the rim): a square is opaque when most of its pixels are
(alpha >= 128), its colour the median of those.
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
from design_taliyah_hd import lp  # noqa: E402
import pack_taliyah_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "taliyah", "codex_poses", "taliyah-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "taliyah", "hd")
# the gold ornament (rows 6-12, columns 15-24), the hair's middle above the face, the brows (row 19), the eyes (rows
# 20-23: the near one columns 16-20, the far one 24-25), the mouth (row 26) and the chin (row 29) - square edges on
# hd/idle.png; not the hair's outer tufts left of column 13 and above row 5
POLY = [(15.0, 5.0), (25.0, 5.0), (26.0, 12.0), (28.0, 16.0), (29.0, 22.0), (28.0, 29.0), (22.0, 30.0), (15.0, 30.0),
        (13.0, 25.0), (13.0, 16.0), (14.0, 12.0)]
SCALES = np.arange(8.5, 14.01, 0.25)
TILTED = {}
SCALE = {}                                       # px a square set by hand where the skeleton's does not fit the body
# head matches set by hand (px a square, x, y, cost, tilt)
MATCH = {}
# Codex drew the bodies bigger round the design's head than the design has them (its squares about 9.8 px, the
# skeleton's 11): read at the head's scale a pose stood up to 1.3 times its skeleton's height. Her head is as wide as
# her body, so whole columns dropped outside the head box (design_singed_poses.shrink) cannot narrow the torso under it:
# the pose is read at the BODY's scale instead - the raw px from the matched head's middle to the lowest opaque row
# over the squares the skeleton puts between them (pack_taliyah_poses.build: the head box's middle to the ground) - and
# the design's whole head (WHOLE_HEAD: the hair, the ornament, the face down to the chin's outline, not the mantle's
# top) pasted on the head's middle, covering Codex's own, smaller there.
BODY = {}
HEAD_ROWS = 29                                   # the head's rows in hd/idle.png: 0 (the hair's top) to 28 (the chin)
MANTLE = {(0xF6, 0xE5, 0xBD), (0xF0, 0xDC, 0xAE), (0xA9, 0x95, 0x71), (0x96, 0x81, 0x62), (0x74, 0x5F, 0x49),
          (0x5C, 0x4A, 0x3A)}                    # the stone mantle's colours (its top reaches row 25 beside the hair)
# raw px boxes (x0, y0, x1, y1) whose squares are drawn back over the pasted head: a hand or a sleeve Codex drew in
# front of the hair's side - only the arm's own squares (not the hair's browns, not the outline unless it edges them)
KEEP_RAW = {"e_raise": [(395, 455, 520, 615), (735, 480, 885, 615)]}   # both hands raised beside the hair
HAIR = {(0x97, 0x54, 0x3D), (0x61, 0x2D, 0x1D), (0x52, 0x26, 0x1A), (0x27, 0x14, 0x17), (0x7E, 0x42, 0x13),
        (0x76, 0x3A, 0x27), (0x3C, 0x22, 0x1E)}
INK = {(0x0A, 0x01, 0x0D), (0x0C, 0x01, 0x11)}
CACHE = "C:/t/ta_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"taliyah-pose-{name}.png"))).convert("RGBA"))


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def head_box(d):
    """The head box with everything outside POLY clear (the hair's outer tufts never steer the match)."""
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


def drop_specks(a, most=4):
    """Pieces apart from the figure's biggest (8-connected) of at most `most` squares cleared (the read-back's crumbs)."""
    a = a.copy()
    lb, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lb, range(1, n + 1))
        keep = int(np.argmax(sizes)) + 1
        for j in range(1, n + 1):
            if j != keep and sizes[j - 1] <= most:
                a[lb == j] = 0
    return a


def matched(name, again=False):
    """match_head's (px a square, x, y, cost, tilt) for a pose, kept in hd/pose_<name>.json ("match") once found."""
    if name in MATCH:
        return MATCH[name]
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


def whole_head(d):
    """The design's head: every square of rows 0-28 but the mantle's."""
    m = np.zeros(d.shape[:2], bool)
    m[:HEAD_ROWS] = d[:HEAD_ROWS, ..., 3] > 0
    yy = np.arange(d.shape[0])[:, None]
    mantle = np.zeros_like(m)
    for c in MANTLE:
        mantle |= (d[..., 0] == c[0]) & (d[..., 1] == c[1]) & (d[..., 2] == c[2])
    return m & ~(mantle & (yy >= 24))


def body_scale(name, a, cy):
    """px a square of the body: the raw px from the head's middle (cy) down to the lowest opaque row, over the squares
    the pose's skeleton puts between the head box's middle and the ground."""
    spec = PK.POSES[name][3]
    sk = PK.build(spec)
    low = np.nonzero((a[..., 3] >= 128).any(1))[0].max() + 1
    return (low - cy) / (PK.GROUND - sk["head"][1])


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = PK.HEAD
    hw, hh = c1 - c0, r1 - r0
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    s2 = SCALE.get(name) or body_scale(name, a, cy)
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    pad = 24
    keep = np.zeros(fig.shape[:2], bool)               # a hand in front of the hair: drawn back over the head
    for x0, y0, x1, y1 in KEEP_RAW.get(name, ()):
        i0, i1 = int((x0 - (cx - hw * s2 / 2)) // s2) + ci, int((x1 - (cx - hw * s2 / 2)) // s2) + ci
        j0, j1 = int((y0 - (cy - hh * s2 / 2)) // s2) + cj, int((y1 - (cy - hh * s2 / 2)) // s2) + cj
        keep[max(0, j0):j1 + 1, max(0, i0):i1 + 1] = True
    keep &= fig[..., 3] > 0
    if keep.any():
        def is_in(colours):
            m = np.zeros(keep.shape, bool)
            for c in colours:
                m |= (fig[..., 0] == c[0]) & (fig[..., 1] == c[1]) & (fig[..., 2] == c[2])
            return m
        core = keep & ~is_in(HAIR) & ~is_in(INK)
        edge = keep & is_in(INK) & ndimage.binary_dilation(core)
        keep = core | edge
    kept = fig.copy()
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if not ang:                                        # a tipped head keeps Codex's own (the design's is upright)
        hm = whole_head(d)
        ys, xs = np.nonzero(hm)
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
    ky, kx = np.nonzero(keep)
    big_[ky + pad, kx + pad] = kept[ky, kx]
    big_ = finish(drop_specks(big_))
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    fig, at = big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0)
    if BODY.get(name, 1.0) != 1.0:
        fig, at = shrink(fig, at, BODY[name])
    return fig, at, s2, cost, ang


def shrink(fig, at, k):
    """The body brought down by k: whole rows and columns dropped (least loss: design_gnar_model.keep_axis on the
    figure's colour indices), the head box's rows and columns kept whole; the outline closed again. -> (figure, the head
    box's new top-left square)."""
    from design_gnar_model import keep_axis
    r0, r1, c0, c1 = PK.HEAD
    hw, hh = c1 - c0, r1 - r0
    flat = fig.reshape(-1, 4).astype(np.int64)
    key = (flat[:, 0] << 24) | (flat[:, 1] << 16) | (flat[:, 2] << 8) | flat[:, 3]
    idx = np.unique(key, return_inverse=True)[1].reshape(fig.shape[:2])
    H, W = idx.shape
    rows = keep_axis([idx[y] for y in range(H)], round(H / k), range(at[1], at[1] + hh))
    sub = idx[rows]
    cols = keep_axis([sub[:, x] for x in range(W)], round(W / k), range(at[0], at[0] + hw))
    out = fig[np.ix_(rows, cols)]
    at2 = (cols.index(at[0]), rows.index(at[1]))
    out = finish(out)
    ys, xs = np.nonzero(out[..., 3] > 0)
    y0, x0 = ys.min(), xs.min()
    return out[y0:ys.max() + 1, x0:xs.max() + 1], (at2[0] + 1 - x0, at2[1] + 1 - y0)


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
            path = os.path.join(a.sheet, f"taliyah_poses_{k}.png")
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

#!/usr/bin/env python3
"""Ambessa's Codex poses (assets/source/ambessa/codex_poses/ambessa-poses: POSE_PROMPTS.md, 21 key poses of her League
clips on the design, 2026-10-25) read back at the design's scale, in its colours, with the design's own head
(design_sejuani_poses.py's way).

    python tools/art/design_ambessa_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_ambessa_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_ambessa_poses.py                  # writes assets/source/ambessa/hd/pose_<name>.png (+ .json)
    python tools/art/design_ambessa_poses.py --rematch        # the same, the heads searched again (else the json's)

Her head (HEAD: the silver hair and the face, hd/idle.png rows 0-25, columns 49-81) is matched over a range of px a
square against the picture (design_shyvana_poses.match_head) - where it is, and its own scale. Codex drew the heads 5-25 %
smaller than the bodies round them, by a different amount in each picture (2026-10-25: the head's scale 6.5-8.75 px a
square, the bodies' 7.3-9.5), so the body is read at its OWN scale (body_scale: the median of three estimates - the
picture's head-top-to-soles height over the skeleton's, the square root of its drawn area over the design's, the head's
scale x HEAD_BODY - or SCALE by hand): every pose comes back at the design's size, whatever size Codex drew it. The
pose is sampled on squares of that size, every colour snapped to the design's own (Lab); Codex's head cleared (POLY at
the head's own scale, tipped as matched) and the design's head pasted square for square with its chin where Codex's chin
was (head_mask: the polygon POLY without the teal mantle and the red scarf under the chin: one face in all frames), the
holes left enclosed filled from round them, the outline closed. Each pose's json keeps where the head went (its top-left
square) and the body's scale, for rig_ambessa to place the pose.
Codex's raw pictures (raw/, 1254 canvases, soft alpha) are read, not its hard-alpha copies: the head match sets the
scale (Codex did not keep the pack's 8 px grid: HANDOFF.md).
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
from design_ambessa_hd import lp  # noqa: E402
import pack_ambessa_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ambessa", "codex_poses", "ambessa-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "ambessa", "hd")
HEAD = (0, 26, 49, 82)             # rows / columns of her head in hd/idle.png: the silver hair, the face, the earring
# the hair and the face; head_mask leaves out the teal mantle at its lower left and the red scarf under the chin
POLY = [(52.0, 1.0), (57.0, 0.0), (75.0, 0.0), (80.0, 4.0), (81.0, 12.0), (78.0, 18.0), (75.0, 23.0), (68.0, 25.5),
        (60.0, 25.0), (55.0, 22.0), (52.0, 17.0), (50.0, 10.0), (50.0, 4.0)]
SCALES = np.arange(6.0, 11.01, 0.25)
TILTED = {"d_kneel": range(-40, 41, 10), "d_slump": range(-60, 61, 10)}
ANGLES = range(-20, 21, 10)
SCALE = {}                         # the body's px a square set by hand (else body_scale's; see --measure)
HEAD_BODY = 1.09                   # the median body / head scale over the 21 pictures (their heights on the skeletons)
KEEP_HEAD = set()                  # poses keeping Codex's own head
CACHE = "C:/t/am_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"ambessa-pose-{name}.png"))).convert("RGBA"))


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    m = (np.asarray(img) > 0) & (d[..., 3] > 0)
    rgb = d[..., :3].astype(int)
    teal = (rgb[..., 1] > rgb[..., 0] + 25) & (rgb[..., 2] > rgb[..., 0] + 15)
    scarf = (rgb[..., 0] > 110) & (rgb[..., 1] < 40) & (rgb[..., 2] < 60)
    scarf[:24] = False                                  # (the lips are red too: only under the chin)
    return m & ~teal & ~scarf


def head_box(d):
    r0, r1, c0, c1 = HEAD
    t = d[r0:r1, c0:c1].copy()
    t[~head_mask(d)[r0:r1, c0:c1]] = 0
    return t


def finish(fig):
    """The outline closed; single squares or one-square slits enclosed by the figure take the outline."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lb == j
        if h.sum() <= 1 or (h.sum() <= 4 and min(np.ptp(np.nonzero(h)[0]), np.ptp(np.nonzero(h)[1])) == 0):
            pad[h] = (*ink, 255)
    return pad


def matched(name, again=False):
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    if not again and os.path.isfile(CACHE):
        c = json.load(open(CACHE, encoding="utf-8"))
        if name in c:
            return tuple(c[name])
    m = match_head(raw(name), head_box(design()), scales=SCALES, angles=TILTED.get(name, ANGLES))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def body_scale(name, match):
    """The body's px a square: the median of the picture's height (head top to the lowest drawn row) over the
    skeleton's (pack_ambessa_poses: the head box's top to the lowest foot), the square root of its drawn area over the
    design's, and the head's scale x HEAD_BODY. -> (scale, (height's, area's, head's))."""
    s, hx, hy, cost, ang = match
    a = raw(name)
    op = a[..., 3] >= 128
    sk = PK.poses_built()[name][0]
    top = sk["head"][1] - PK.HH / 2
    sole = max(p[1] for leg in ("near_leg", "far_leg") for p in sk[leg])
    by_h = float((np.nonzero(op.any(1))[0].max() + 1 - hy) / (sole - top))
    by_a = float(np.sqrt(op.sum() / (design()[..., 3] > 0).sum()))
    by_s = s * HEAD_BODY
    return float(np.median([by_h, by_a, by_s])), (by_h, by_a, by_s)


def codex_head(match, s2, chin, shape):
    """Codex's head on the read grid: POLY at the head's own scale (s / s2 of the design's squares), tipped as matched,
    its chin's middle on `chin`; one square more round it."""
    s, _, _, _, ang = match
    r0, r1, c0, c1 = HEAD
    k = s / s2
    mx, cy0 = (c1 - c0) / 2, r1 - r0                  # the box's bottom middle
    t = np.radians(ang)
    pts = []
    for x, y in POLY:
        dx, dy = (x - c0 - mx) * k, (y - r0 - cy0) * k
        pts.append((chin[0] + dx * np.cos(t) + dy * np.sin(t), chin[1] - dx * np.sin(t) + dy * np.cos(t)))
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon(pts, fill=255)
    return ndimage.binary_dilation(np.asarray(img) > 0, iterations=1)


def turned_head(ang, at, shape):
    r0, r1, c0, c1 = HEAD
    mx, my = (c1 - c0) / 2, (r1 - r0) / 2
    t = np.radians(ang)
    pts = []
    for x, y in POLY:
        dx, dy = x - c0 - mx, y - r0 - my
        pts.append((at[0] + mx + dx * np.cos(t) + dy * np.sin(t), at[1] + my - dx * np.sin(t) + dy * np.cos(t)))
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon(pts, fill=255)
    return ndimage.binary_dilation(np.asarray(img) > 0, iterations=1)


def fill_holes(a, near=None, iters=8):
    """Enclosed holes filled from round them, square by square inward; with `near` only the holes that touch it (the
    room a cleared head left - not the background enclosed between a chain, a blade and an arm)."""
    a = a.copy()
    if near is not None:
        op = a[..., 3] > 0
        lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
        keep = np.zeros(op.shape, bool)
        for j in range(1, n + 1):
            h = lb == j
            if (h & near).any():
                keep |= h
    for _ in range(iters):
        op = a[..., 3] > 0
        hole = ndimage.binary_fill_holes(op) & ~op
        if near is not None:
            hole &= keep
        if not hole.any():
            break
        ys, xs = np.nonzero(hole)
        new = a.copy()
        for y, x in zip(ys, xs):
            nb = [tuple(a[j, i, :3]) for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if 0 <= j < a.shape[0] and 0 <= i < a.shape[1] and a[j, i, 3] > 0]
            if nb:
                new[y, x, :3] = max(set(nb), key=nb.count)
                new[y, x, 3] = 255
        a = new
    return a


def drop_specks(a, most=6):
    """Pieces apart from the figure's biggest (8-connected) of at most `most` squares cleared (stray specks of the
    soft alpha)."""
    a = a.copy()
    lb, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lb, range(1, n + 1))
        for j in range(1, n + 1):
            if sizes[j - 1] <= most:
                a[lb == j] = 0
    return a


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    body's px a square, the head match's cost and tilt)."""
    d = design()
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = HEAD
    hw, hh = c1 - c0, r1 - r0
    s2 = SCALE.get(name) or body_scale(name, match)[0]
    # the head box's bottom middle (its chin) where Codex's is, on squares of the body's size
    bx, by = hx + hw * s / 2, hy + hh * s
    if ang:                                            # a tipped head: its chin turned about the box's middle
        t = np.radians(ang)
        mx, my = hx + hw * s / 2, hy + hh * s / 2
        bx, by = mx + (hh * s / 2) * np.sin(t), my + (hh * s / 2) * np.cos(t)
    fig, (ci, cj) = sample_grid(a, s2, bx - hw * s2 / 2, by - hh * s2)
    fig = snap(fig, d)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if name not in KEEP_HEAD:
        hm = head_mask(d)
        ys, xs = np.nonzero(hm)
        chin = (ci + pad + hw / 2, cj + pad + hh)
        old = codex_head(match, s2, chin, big_.shape[:2])
        big_[old] = 0
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
        big_ = fill_holes(big_, near=old & (big_[..., 3] == 0))
    big_ = finish(drop_specks(big_))
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    fig, at = big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0)
    return fig, at, s2, cost, ang


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
        for n in names:
            m = matched(n, a.rematch)
            b, (bh, ba, bs) = body_scale(n, m)
            hand = f" hand {SCALE[n]}" if n in SCALE else ""
            print(f"{n:9s} head {m[0]:5.2f} px a square at ({m[1]}, {m[2]}) tilted {m[4]}, cost {m[3]:.4f}; body {b:5.2f} "
                  f"(height {bh:5.2f}, area {ba:5.2f}, head {bs:5.2f}){hand}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m, s)
        print(f"{n:9s} body {s:5.2f} px a square (head {m[0]:5.2f}), tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x "
              f"{fig.shape[0]}, head at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in names if n in figs]
        rows = [tiles[i:i + 4] for i in range(0, len(tiles), 4)]
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
            path = os.path.join(a.sheet, f"ambessa_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m, sc) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])], "scale": round(float(sc), 4),
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, fh)


if __name__ == "__main__":
    main()

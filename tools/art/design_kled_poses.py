#!/usr/bin/env python3
"""Kled's Codex poses (assets/source/kled/codex_poses/kled-poses: POSE_PROMPTS.md, 20 key poses of his League clips -
11 mounted on Skaarl, 9 on foot) read back at the designs' scale, in their colours, with the design's own head
(design_sejuani_poses.py's way).

    python tools/art/design_kled_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_kled_poses.py --sheet DIR      # all poses beside the designs (4x)
    python tools/art/design_kled_poses.py                  # writes assets/source/kled/hd/pose_<name>.png (+ .json)
    python tools/art/design_kled_poses.py --rematch        # the same, the heads searched again (else the json's)

The scale comes from KLED's head (HEAD: the hat and spike, the face and beard, not the big near ear - it is drawn at
different angles; hd/idle.png rows 0-39, columns 15-43; hd/foot.png wears the same head), matched over a range of px a
square against the picture (design_shyvana_poses.match_head), the pose sampled on squares of that size, the grid laid so
the matched head keeps its middle, every colour snapped to the designs' own (Lab: hd/idle.png and hd/foot.png), the
design's head pasted square for square on Codex's (the polygon POLY: one face in all frames), the outline closed. Each
pose's json keeps where the head went (its top-left square), for rig_kled to place the pose. A head that came back tipped
(searched over ANGLES; TILTED wider where he falls) is cleared and the design's upright head put on its middle.
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
from design_kled_hd import lp  # noqa: E402
import pack_kled_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kled", "codex_poses", "kled-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "kled", "hd")
HEAD = (0, 40, 15, 43)             # rows / columns of his head in hd/idle.png: the spike, the hat, the face, the beard
# the hat with its spike, the face, the beard and the small far ear - not the big near ear (Codex turns it)
POLY = [(17.0, 10.0), (22.0, 6.0), (28.0, 0.0), (31.0, 0.0), (34.0, 7.0), (38.0, 8.0), (40.0, 12.0), (42.0, 14.0),
        (42.0, 26.0), (40.0, 30.0), (38.0, 36.0), (35.0, 39.0), (26.0, 39.0), (22.0, 37.0), (19.0, 33.0), (17.0, 28.0),
        (16.0, 18.0)]
SCALES = np.arange(8.5, 15.51, 0.25)
TILTED = {"d_fall": range(-50, 51, 10), "d_down": range(-40, 41, 10), "f_recoil": range(-40, 41, 10)}
ANGLES = range(-20, 21, 10)
SCALE = {}                         # px a square set by hand where his head does not fit the body (see --measure)
# Codex kept Kled's head at the design's size but drew Skaarl taller round it (longer legs and body: the runs 90-93 rows
# against the design's 80, 2026-10-25). Each mounted pose is brought back by Skaarl's eye-to-claws height against the
# design's 31.5 rows - whole rows and columns dropped (least loss, design_gnar_model.keep_axis; never through Kled's head
# box), at most 1.15: more crushed him into the saddle (a_wind measured 1.41 - he rises out of it - and the stretched
# dash e_lunge 1.35 came out squashed).
BODY = {"a_wind": 1.12, "a_chop": 1.05, "q_throw": 1.15, "q_yank": 1.14, "e_lunge": 1.15, "e_slash": 1.10,
        "r_charge": 1.15, "run1": 1.15, "run2": 1.15, "run3": 1.15, "run4": 1.15,
        # on foot: the body under the head drawn longer than hd/foot.png's (its 60 rows: f_aim 68, f_wind 71): the
        # standing ones brought to about 60 the same way
        "f_wind": 1.15, "f_chop": 1.07, "f_aim": 1.13, "f_recoil": 1.12, "f_run1": 1.05, "f_run2": 1.10,
        "f_run3": 1.08, "d_fall": 1.10}
KEEP_HEAD = {"d_down", "a_chop"}   # d_down keeps Codex's own head: eyes closed, drooping (POSE_PROMPTS); a_chop's is
# tipped 20 degrees into the chop and on-model (the upright head pasted on it left a dark fill behind his raised arm)
CACHE = "C:/t/kl_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def palette_ref():
    """Both designs' colours side by side (snap reads every opaque square's colour)."""
    i, r = design(), design("foot.png")
    h = max(i.shape[0], r.shape[0])
    out = np.zeros((h, i.shape[1] + r.shape[1], 4), np.uint8)
    out[:i.shape[0], :i.shape[1]] = i
    out[:r.shape[0], i.shape[1]:] = r
    return out


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"kled-pose-{name}.png"))).convert("RGBA"))


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


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


def fill_holes(a, iters=8):
    a = a.copy()
    for _ in range(iters):
        op = a[..., 3] > 0
        hole = ndimage.binary_fill_holes(op) & ~op
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
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = HEAD
    hw, hh = c1 - c0, r1 - r0
    s2 = SCALE.get(name, s)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, palette_ref())
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if name not in KEEP_HEAD:
        hm = head_mask(d)
        ys, xs = np.nonzero(hm)
        if ang:
            old = turned_head(ang, (ci + pad, cj + pad), big_.shape[:2])
            big_[old] = 0
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
        if ang:
            big_ = fill_holes(big_)
    big_ = finish(drop_specks(big_))
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    fig, at = big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0)
    if BODY.get(name, 1.0) != 1.0:
        fig, at = shrink(fig, at, BODY[name])
    return fig, at, s2, cost, ang


def shrink(fig, at, k):
    """The body brought down by k: whole rows and columns dropped (least loss: design_gnar_model.keep_axis on the
    figure's colour indices), his head box's rows and columns kept whole; the outline closed again. -> (figure, the head
    box's new top-left square)."""
    from design_gnar_model import keep_axis
    r0, r1, c0, c1 = HEAD
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
    out = finish(drop_specks(out))
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
            s, x, y, cost, ang = match_head(r, head_box(d), scales=SCALES, angles=TILTED.get(n, ANGLES))
            area = float(np.sqrt((r[..., 3] >= 128).sum() / (d[..., 3] > 0).sum()))
            print(f"{n:9s} head {s:5.2f} px a square at ({x}, {y}) tilted {ang}, cost {cost:.4f}; area {area:5.2f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:9s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design()), ("foot", design("foot.png"))] + [(n, figs[n][0]) for n in names if n in figs]
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
            path = os.path.join(a.sheet, f"kled_poses_{k}.png")
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

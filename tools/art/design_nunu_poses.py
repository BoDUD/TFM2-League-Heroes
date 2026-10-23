#!/usr/bin/env python3
"""Nunu & Willump's Codex poses (assets/source/nunu/codex_poses/nunu-poses: POSE_PROMPTS.md, 18 key poses of their League
clips on the design) read back at the design's scale, in its colours, with the design's own Nunu head
(design_illaoi_poses.py's way).

    python tools/art/design_nunu_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_nunu_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_nunu_poses.py                  # writes assets/source/nunu/hd/pose_<name>.png (+ .json)
    python tools/art/design_nunu_poses.py --rematch        # the same, the heads searched again (else the json's)

The poses copy the design's head box (pack_nunu_poses.HEAD: Nunu, the antlers and Willump's head), but Willump's face
changes with the pose on purpose (the jaws wide in b_open, w_hit and r_raise) and the antlers turn: the scale comes from
NUNU's head alone (HEAD: the pompom, the hood with its ears, the face; hd/idle.png rows 0-18, columns 16-35), matched over
a range of px a square against the picture (design_shyvana_poses.match_head), the pose sampled on squares of that size,
the grid laid so the matched head keeps its middle, every colour snapped to the design's own (Lab), the design's Nunu
head pasted square for square on Codex's (the polygon POLY: one face in all frames), the outline closed. Each pose's
json keeps where the head went (its top-left square), for rig_nunu to place the pose. Where Nunu's head came back
tipped (searched over ANGLES; TILTED wider: he tumbles off in d_fall, sits on the ground in d_lie) Codex's turned head is
cleared and the design's upright head put on its middle, the squares between filled from round them (its eyes and
mouth came back smeared at 12x: one face in all frames).
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
from design_nunu_hd import lp  # noqa: E402
import pack_nunu_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nunu", "codex_poses", "nunu-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "nunu", "hd")
HEAD = (0, 18, 16, 35)             # rows / columns of Nunu's head in hd/idle.png: the pompom, the hood, the face
# the pompom, the hood with its two ears and the face - not the antler tips by his cheeks nor the cape under his chin
POLY = [(21.0, 0.0), (29.0, 0.0), (29.0, 4.0), (34.0, 4.0), (35.0, 5.0), (35.0, 16.0), (33.0, 17.0), (22.0, 17.0),
        (20.0, 15.0), (17.0, 14.0), (17.0, 5.0), (20.0, 4.0)]
SCALES = np.arange(13.0, 19.51, 0.25)
TILTED = {"d_fall": range(-40, 41, 10), "d_lie": range(-30, 31, 10)}
ANGLES = range(-30, 31, 10)                      # the others searched tilted too: his head tips with the pose
PASTE_MAX_TILT = 0                               # the design's head pasted only on an upright match
# px a square set by hand where Nunu's head does not fit Willump's body: Codex drew Willump bigger or smaller round the
# same Nunu from pose to pose, and frames that alternate must keep him one size (2026-10-23, judged by three measures -
# Willump's face features matched near his nose, his fur's area, the pairs laid side by side at the picture's px):
# e_throw2's Willump ~9% bigger than e_throw1's, w_push1's ~13% bigger than w_push2's (w_push2 by his face, cost 0.31),
# r_raise's and w_hit's bodies too big at their heads' scale (their heads tipped back)
# run3's head matched at 19 stood the whole figure 60 rows tall against the other runs' 63-64: read at 18 (63 rows)
SCALE = {"e_throw2": 17.0, "w_push1": 14.4, "w_push2": 12.75, "w_hit": 16.0, "r_raise": 16.75, "d_lie": 13.5,
         "run3": 18.0}
# poses whose small pieces apart from the body go: e_throw1's snowball drawn just off Nunu's hand (the barrage's own
# projectile flies from the cast, and the frame alternating with e_throw2 every 100 ms made it blink in place)
DROP_DETACHED = {"e_throw1"}
CACHE = "C:/t/nu_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"nunu-pose-{name}-generated.png"))).convert("RGBA"))


def head_box(d):
    """Nunu's head box with only his head opaque (POLY): the antler tips by his cheeks and the cape under his chin turn
    and change from pose to pose, and matched with the head they pulled it off his face."""
    r0, r1, c0, c1 = HEAD
    t = d[r0:r1, c0:c1].copy()
    t[~head_mask(d)[r0:r1, c0:c1]] = 0
    return t


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def finish(fig):
    """The outline closed; enclosed holes the read-back left take the outline where they are a single square or a slit
    one square wide (a crack between the hood and an antler reads as a broken outline); wider holes stay (the design
    shows the ground between its antler tines and its body too)."""
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
    m = match_head(raw(name), head_box(design()), scales=SCALES, angles=TILTED.get(name, ANGLES))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def read(name, match):
    """The pose on the design's grid with the design's Nunu head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = HEAD
    hw, hh = c1 - c0, r1 - r0
    s2 = SCALE.get(name, s)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if ang:
        # Codex's tipped head goes (its eyes and mouth came back smeared at 12x): the head polygon turned as matched,
        # one square wider, cleared; the design's upright head goes on the same middle; what the turned head covered
        # and the upright one does not is filled from round it where the figure closes over it (the neck, the cape)
        old = turned_head(ang, (ci + pad, cj + pad), big_.shape[:2])
        big_[old] = 0
    big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
    if ang:
        big_ = fill_holes(big_)
    if name in DROP_DETACHED:
        big_ = drop_detached(big_)
    big_ = finish(big_)
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), s2, cost, ang


def turned_head(ang, at, shape):
    """The head polygon (POLY, one square wider all round) turned by ang degrees (PIL's way: counter-clockwise on
    screen) about the head box's middle, the box's top-left square at `at` -> a mask of that shape."""
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
    """Clear squares the figure closes round (holes) take the commonest colour of their drawn neighbours, a ring at a
    time."""
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


def drop_detached(a, most=40):
    """Pieces apart from the figure's biggest (8-connected) of at most `most` squares cleared."""
    a = a.copy()
    lb, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lb, range(1, n + 1))
        keep = int(np.argmax(sizes)) + 1
        for j in range(1, n + 1):
            if j != keep and sizes[j - 1] <= most:
                a[lb == j] = 0
    return a


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
        tiles = [("design", design())] + [(n, figs[n][0]) for n in names if n in figs]
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
            path = os.path.join(a.sheet, f"nunu_poses_{k}.png")
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

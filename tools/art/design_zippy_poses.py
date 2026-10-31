#!/usr/bin/env python3
"""Zippy's Codex poses (assets/source/zippy/codex_poses: POSE_PROMPTS.md, 12 key poses, 8 run frames and 2 of its fall
from its own TFT clips on its design, 2026-10-31) at the design's body size, on the design's palette, gaps closed, the
design's face on each where the head is not turned.

    python tools/art/design_zippy_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_zippy_poses.py                  # writes assets/source/zippy/hd/pose_<name>.png (+ .json)

Codex drew every pose over its reference (1254 canvas, the soles on y 1176, the root on column ROOT_X) and only moved
each drawing up or down to put its lowest row on the line (manifest.json translation_px, x always 0), so the root's
column in the raw drawing is ROOT_X. The squares are mostly the 10 px asked (e_curl 13, r_spring 12), but the bodies are
not one size: the saddle's gold, the eye and the whole area put them at 1.0 to 1.4 of the design's (C:/t/zz_work/
measure.py, 2026-10-31). So each pose is read from Codex's raw drawing on its own squares (regrid) and brought to the
design's body by SCALE[name] (raw px per design square / 10, set from those measures and checked on the sheet beside the
design: the head's width and the leg's length). Then the colours are snapped to the design's own (nearest in Lab), the
one-square cracks and small holes closed (design_silco_poses.close_gaps), loose specks dropped, and the design's own
face (the black shards, the half-closed eye under its heavy lid, the mouth line) pasted where it matches best (the
user's rule: one face in every frame; FACE_*), only where at least FACE_MIN of its squares already match (a head thrown
back or upside down keeps Codex's).
Each pose's json keeps where its root and the ground fall in it (pivot) and where the face went.
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
import pack_zippy_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_zippy_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zippy", "codex_poses", "zippy-poses")
OUT = os.path.join(ROOT, "assets", "source", "zippy", "hd")
ROOT_X = 565                  # the pack's root column on the canvas (360 + the design's root column 20.5 x 10)
# raw px per design square / 10 (the saddle's gold, the eye and the area against the design's, 2026-10-31)
SCALE = {"a_wind": 1.12, "a_kick": 1.08, "q_crouch": 1.15, "q_flip": 1.12, "q_kick": 1.25, "q_land": 1.10,
         "e_curl": 1.40, "e_ball": 1.14, "r_crouch": 1.08, "r_spring": 1.32, "r_open": 1.10, "r_land": 1.08,
         "run1": 1.04, "run2": 1.04, "run3": 1.06, "run4": 1.02, "run5": 1.04, "run6": 1.12, "run7": 1.05,
         "run8": 1.12, "d_fall": 1.04, "d_down": 1.14}
SPECK = 6                     # parts apart from the figure smaller than this are dropped
# the face (the user's rule: the idle's face in every frame): the design's black shards, eye and mouth, rows / columns
# of hd/idle.png, pasted on each pose where it matches best (searched FACE_SEARCH squares round the violet eye)
FACE_ROWS, FACE_COLS = (17, 33), (25, 50)
FACE_SEARCH = 4
FACE_MIN = 0.45
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def snap(a, d):
    """Every opaque square to the nearest of the design's colours (in Lab)."""
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    op = a[..., 3] > 0
    lab_p = PD._lab(pal.astype(float))
    lab_a = PD._lab(a[op][:, :3].astype(float))
    idx = np.argmin(((lab_a[:, None, :] - lab_p[None, :, :]) ** 2).sum(-1), axis=1)
    out = np.zeros_like(a)
    out[op, :3] = pal[idx]
    out[op, 3] = 255
    return out


def eyes(a):
    """The violet eye's middle (x, y), or None."""
    c = a[..., :3].astype(int)
    m = (a[..., 3] > 0) & (c[..., 2] > 170) & (c[..., 0] > 100) & (c[..., 0] < 230) & (c[..., 1] < 110)
    ys, xs = np.nonzero(m)
    return (xs.mean(), ys.mean()) if len(xs) else None


def put_face(g, d, hint=None):
    """The design's face pasted on the pose at the offset where most of its squares already match (in Lab, within a
    few steps), searched round where the eye says (or `hint`, where it was before the pose was brought down); only on
    the pose's own squares. -> (pose, offset, match share)."""
    (r0, r1), (c0, c1) = FACE_ROWS, FACE_COLS
    patch = d[r0:r1, c0:c1]
    pm = patch[..., 3] > 0
    ed, ep = eyes(d), eyes(g)
    ep = ep or hint
    if ep is None:
        return g, None, 0.0
    bx, by = round(ep[0] - ed[0]) + c0, round(ep[1] - ed[1]) + r0
    lab_g = PD._lab(g[..., :3].reshape(-1, 3).astype(float)).reshape(g.shape[0], g.shape[1], 3)
    lab_p = PD._lab(patch[..., :3].reshape(-1, 3).astype(float)).reshape(patch.shape[0], patch.shape[1], 3)
    best = (-1, 0, 0)
    for dy in range(-FACE_SEARCH, FACE_SEARCH + 1):
        for dx in range(-FACE_SEARCH, FACE_SEARCH + 1):
            x, y = bx + dx, by + dy
            if x < 0 or y < 0 or y + patch.shape[0] > g.shape[0] or x + patch.shape[1] > g.shape[1]:
                continue
            win = g[y:y + patch.shape[0], x:x + patch.shape[1]]
            both = pm & (win[..., 3] > 0)
            dist = ((lab_g[y:y + patch.shape[0], x:x + patch.shape[1]] - lab_p) ** 2).sum(-1)
            score = int((both & (dist < 400)).sum())
            if score > best[0]:
                best = (score, x, y)
    score, x, y = best
    if score < FACE_MIN * pm.sum():   # the head turned (thrown back, upside down): Codex's own face stays
        return g, None, score / pm.sum()
    out = g.copy()
    win = out[y:y + patch.shape[0], x:x + patch.shape[1]]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out, (x - c0, y - r0), score / pm.sum()


def raw_read(name):
    """Codex's raw drawing at the design's body size and palette -> (figure, root (x, y) in it: y the soles' line under
    the lowest row, the eye (x, y) in it)."""
    d = design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"zippy-pose-{name}-raw.png"))).convert("RGBA")).copy()
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    sq = RG.square_size(RG.profile(a, op, 1), xs.min(), xs.max())
    body = 10 * SCALE[name] / sq
    if body < 1:   # its squares bigger than the design's at this body: read on finer squares
        sq *= body
        body = 1.0
    g, _, (bx, _) = RG.regrid(a, sq)
    gy, gx = np.nonzero(g[..., 3] >= 128)
    i = max(0, np.searchsorted(bx, ROOT_X) - 1)
    col = i + (ROOT_X - bx[i]) / sq
    g = g[gy.min():gy.max() + 1, gx.min():gx.max() + 1].copy()
    g[..., 3] = np.where(g[..., 3] >= 128, 255, 0)
    root = (col - gx.min(), g.shape[0])
    g = snap(g, d)
    k = 1 / body
    e = eyes(g)
    if k < 1:
        pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
        im, root2 = PD.pixelate(g, k, root, PD.edge_colour(d), pal=pal)
        e = None if e is None else (root2[0] + (e[0] - root[0]) * k, root2[1] + (e[1] - root[1]) * k)
        g, root = snap(np.asarray(im).copy(), d), root2
    return g, root, e


def read(name):
    """The pose at the design's body size, on the design's palette, with the design's face -> (figure, the root's
    square in it, the face's offset)."""
    d = design()
    g, root, e = raw_read(name)
    g = close_gaps(g, d)
    g, off, share = put_face(g, d, e)
    print(f"{name:9s} scale {SCALE[name]:.2f}: face at {off}, {share:.0%} of its squares matched before")
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    face = None if off is None else (int(off[0] - xs.min()), int(off[1] - ys.min()))
    return (g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (round(root[0] - xs.min()), round(root[1] - ys.min())),
            face)


def big4(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    figs = {n: read(n) for n in names}
    for n, (fig, piv, _) in figs.items():
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, pivot at {piv}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
        for j, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big4(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"zippy_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv, face) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]], "face": None if face is None else [face[0], face[1]]}, fh)


if __name__ == "__main__":
    main()

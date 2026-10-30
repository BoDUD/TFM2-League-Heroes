#!/usr/bin/env python3
"""Shi Oh Yu's Codex poses (assets/source/shiohyu/codex_poses: POSE_PROMPTS.md, 12 key poses of his own TFT clips + TFT's
run in 8 frames, on his design, 2026-10-30) at the design's body size, on the design's palette, gaps closed, the design's
face on each.

    python tools/art/design_shiohyu_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_shiohyu_poses.py                  # writes assets/source/shiohyu/hd/pose_<name>.png (+ .json)

Codex drew every pose on the pack's 1254 canvas (raw/shiohyu-pose-<name>.png = the delivered file, soft alpha), its
squares 7.8-9.8 px (the phase of the colour edges), the figure wider than its reference (the chibi body is chunkier than
the model) but the BODY at the design's own size: the pale jade beard's area is 0.93-1.13 times the design's at the
pack's 8 px a square in every pose but the dash (0.70: the beard turned down, out of view). So every pose is brought to
game squares at the pack's PX (8 dense px a square: pixel_down.pixelate on a grid through the root, alpha cut at 128),
then the colours are snapped to the design's own (nearest in Lab), the one-square cracks and small holes closed
(design_silco_poses.close_gaps), loose specks dropped, and the design's own face (the teal brow, the glowing eye, the
bronze muzzle) pasted where it matches best (the user's rule: one face in every frame; FACE_*) - not where the pose
turns the head away from the design's (a match under FACE_MIN: the slam, the face in the ground).
Each pose's json keeps where his root and the ground fall in it (pivot: the pack's root column ROOT_X on the canvas,
over which Codex drew every pose; the soles = the lowest row) and where the face went.
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
import pack_shiohyu_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_shiohyu_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shiohyu", "codex_poses", "shiohyu-poses")
OUT = os.path.join(ROOT, "assets", "source", "shiohyu", "hd")
ROOT_X = 699                  # the pack's root column on the canvas (the design's root column 46.4 at 8 px, centred)
SPECK = 6                     # parts apart from the figure smaller than this are dropped
# the face (the user's rule: the idle's face in every frame): the design's brow, eye and muzzle, rows / columns of
# hd/idle.png, pasted on each pose where it matches best (searched FACE_SEARCH squares round its glowing eye)
FACE_ROWS, FACE_COLS = (31, 45), (44, 63)
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
    """The glowing eye's orange squares' middle (x, y), or None."""
    c = a[..., :3].astype(int)
    m = (a[..., 3] > 0) & (c[..., 0] > 220) & (c[..., 1] > 60) & (c[..., 1] < 140) & (c[..., 2] < 60)
    ys, xs = np.nonzero(m)
    return (xs.mean(), ys.mean()) if len(xs) else None


def put_face(g, d):
    """The design's face pasted on the pose at the offset where most of its squares already match (in Lab, within a
    few steps), searched round where the eye says; only on the pose's own squares, only on a match of FACE_MIN or
    more. -> (pose, offset or None, match share)."""
    (r0, r1), (c0, c1) = FACE_ROWS, FACE_COLS
    patch = d[r0:r1, c0:c1]
    pm = patch[..., 3] > 0
    ed, ep = eyes(d), eyes(g)
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
    share = score / pm.sum()
    if share < FACE_MIN:
        return g, None, share
    out = g.copy()
    win = out[y:y + patch.shape[0], x:x + patch.shape[1]]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out, (x - c0, y - r0), share


def raw_read(name):
    """Codex's drawing at the design's density and palette -> (figure, root (x, y) in it: y the soles' line)."""
    d = design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"shiohyu-pose-{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    ys = np.nonzero(a[..., 3].any(1))[0]
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    im, root = PD.pixelate(a, 1 / PK.PX, (ROOT_X, ys.max() + 1), PD.edge_colour(d), pal=pal)
    return snap(np.asarray(im).copy(), d), root


def read(name):
    """The pose at the design's body size, on the design's palette, with the design's face -> (figure, the root's
    square in it, the face's offset or None, the face's match)."""
    d = design()
    g, root = raw_read(name)
    g = close_gaps(g, d)
    g, off, share = put_face(g, d)
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    face = None if off is None else (off[0] - xs.min(), off[1] - ys.min())
    return (g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (round(root[0] - xs.min()), round(root[1] - ys.min())),
            face, share)


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
    for n, (fig, piv, face, share) in figs.items():
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, pivot at {piv}, face {face} ({share:.0%} matched before)")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in names]
        rows = [tiles[i:i + 7] for i in range(0, len(tiles), 7)]
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
            path = os.path.join(a.sheet, f"shiohyu_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv, face, _) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]], "face": None if face is None else [int(face[0]), int(face[1])]}, fh)


if __name__ == "__main__":
    main()

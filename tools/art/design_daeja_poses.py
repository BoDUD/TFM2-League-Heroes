#!/usr/bin/env python3
"""Daeja's Codex poses (assets/source/daeja/codex_poses: POSE_PROMPTS.md, 13 key poses of his own TFT clips and 8 run
frames on his design, 2026-10-30) on the design's palette, gaps closed.

    python tools/art/design_daeja_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_daeja_poses.py                  # writes assets/source/daeja/hd/pose_<name>.png (+ .json)

Codex kept the asked 10 px squares (the design's own, 1:1), but on the grid of its step-0 picture: x from the canvas
corner, y from row 6 (its HANDOFF: grid_origin [0, 6], so the soles' line 1176 falls on a square's edge); its pixel_1x/
is the canvas read one square a pixel that way, 125 x 125 (the soles' row 116). The poses stand 69 rows tall where the
design does (a_wind, a_punch: the idle's own height). So a pose is taken 1:1 from pixel_1x/, its colours snapped to the
design's own (nearest in Lab), the one-square cracks and small holes closed (design_silco_poses.close_gaps) and loose
specks dropped, and the design's own face (mask, eyes, the mane's top) pasted where it matches best (the user's rule:
one face in every frame; FACE_*). Each pose's json keeps where PIVOT fell in it (and where the face went): the pack drew every reference with his root on one
canvas column (pack_daeja_poses: the design's root column 31.9 -> canvas x 649) and his lowest point on the ground line,
and Codex placed each pose over its reference, so the rig stands the frames by it.
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
import pack_daeja_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_daeja_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "daeja", "codex_poses", "daeja-poses", "pixel_1x")
OUT = os.path.join(ROOT, "assets", "source", "daeja", "hd")
# the pack's root column on the canvas (pack_daeja_poses: the design centred on whole squares, his root on its column
# 31.9 -> canvas x 649) and the ground line, in pixel_1x's squares (its rows start at canvas y 6)
GRID_Y0 = 6
PIVOT = (649 / PK.PX, (PK.SOLE_Y - GRID_Y0) / PK.PX)
SPECK = 6                     # parts apart from the figure smaller than this are dropped
# the face (the user's rule: the idle's face in every frame): the design's mask, eyes and the mane's top, rows / columns
# of hd/idle.png, pasted on each pose where it matches best (searched FACE_SEARCH squares round the magenta eyes)
FACE_ROWS, FACE_COLS = (21, 32), (28, 42)
FACE_SEARCH = 4
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
    """The magenta squares' middle (x, y) (his glowing eyes), or None."""
    c = a[..., :3].astype(int)
    m = (a[..., 3] > 0) & (c[..., 0] > 200) & (c[..., 1] < 90) & (c[..., 2] > 190)
    ys, xs = np.nonzero(m)
    return (xs.mean(), ys.mean()) if len(xs) else None


def put_face(g, d):
    """The design's face pasted on the pose at the offset where most of its squares already match (in Lab, within a
    few steps), searched round where the eyes say; only on the pose's own squares. -> (pose, offset, match share)."""
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
    out = g.copy()
    win = out[y:y + patch.shape[0], x:x + patch.shape[1]]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out, (x - c0, y - r0), score / pm.sum()


def read(name):
    """The pose on the design's palette -> (figure, PIVOT's square in it)."""
    d = design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"daeja-pose-{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    g = close_gaps(snap(a, d), d)
    g, off, share = put_face(g, d)
    print(f"{name:9s} face at {off}, {share:.0%} of its squares matched before")
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    face = None if off is None else (off[0] - xs.min(), off[1] - ys.min())
    return (g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (round(PIVOT[0] - xs.min()), round(PIVOT[1] - ys.min())),
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
            path = os.path.join(a.sheet, f"daeja_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv, face) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]], "face": [int(face[0]), int(face[1])]}, fh)


if __name__ == "__main__":
    main()

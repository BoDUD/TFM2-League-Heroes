#!/usr/bin/env python3
"""Terra's Codex poses (assets/source/terra/codex_poses: POSE_PROMPTS.md, 12 key poses and 6 flight frames of her own
TFT clips on her design, 2026-10-31) at the design's body size, on the design's palette, gaps closed, the design's face
on each where the head is not turned.

    python tools/art/design_terra_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_terra_poses.py                  # writes assets/source/terra/hd/pose_<name>.png (+ .json)

Codex was asked the design at 9 px a square but drew every pose bigger and each a little differently (its own squares
8-10 px, regrid's edge phase): read on its own squares the bodies came out 1.3-2 times the design. What does not bend
is her head: the eye to the snout tip is 8.7 of the design's squares, and on the poses with the head level it measured
12.4-13.0 px in the raw drawings - so the design's square is BODY[name] raw px (12.6 unless the pose says otherwise:
the heads thrown up, down or open measure wrong and were set by eye on the sheet). Each raw drawing is read on squares of BODY
px (raw_read: the commonest design colour round each square's centre), the one-square cracks and small holes closed
(design_silco_poses.close_gaps), loose specks dropped, and the design's own face (the brow plates, the eye, the upper
snout) pasted where it matches best (the user's rule: one face in every frame), only where at least FACE_MIN of its
squares already match (NO_FACE: a head turned so far that the best match lands elsewhere).
Each pose's json keeps where the pivot falls in it: the pack put her root on canvas column ROOT_X; Codex drew bigger,
so the column is taken where her hind legs stand (the middle of the body's lowest third, PIVOT) and the ground is the
figure's lowest row.
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
import pack_terra_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_terra_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import snap, put_face  # noqa: E402
import design_sohm_poses as SP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "terra", "codex_poses", "terra-poses")
OUT = os.path.join(ROOT, "assets", "source", "terra", "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the brow plates, the eye, the upper snout - rows / columns
# of hd/idle.png (the jaw left out: it opens)
FACE_ROWS, FACE_COLS = (18, 32), (64, 86)
FACE_MIN = 0.38
NO_FACE = {"e_roar"}           # the head thrown up: the best match lands on her chest (two eyes)
BODY_DEFAULT = 12.6
WIN = 5                       # raw pixels round each design square's centre that vote
BODY = {}
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw_read(name):
    """Codex's raw drawing at the design's body, on the design's palette -> (figure, its own square size).
    Every design square takes the commonest design colour among the raw pixels round its centre (WIN x WIN, each
    snapped to the design's palette in Lab): a mean over Codex's squares mixed the stone with the outline into brown."""
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"terra-pose-{name}.png"))).convert("RGBA")).copy()
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    sq = RG.square_size(RG.profile(a, op, 1), xs.min(), xs.max())
    body = BODY.get(name, BODY_DEFAULT)
    x0, y1 = xs.min(), ys.max() + 1                      # cells laid from the left edge and the soles up
    nw, nh = int(np.ceil((xs.max() + 1 - x0) / body)), int(np.ceil((y1 - ys.min()) / body))
    cx = x0 + (np.arange(nw) + 0.5) * body
    cy = y1 - (nh - np.arange(nh) - 0.5) * body
    r = WIN // 2
    out = np.zeros((nh, nw, 4), np.uint8)
    lab_p = PD._lab(pal.astype(float))
    for j, y in enumerate(cy):
        for i, x in enumerate(cx):
            yi, xi = int(y), int(x)
            win = a[max(0, yi - r):yi + r + 1, max(0, xi - r):xi + r + 1].reshape(-1, 4)
            on = win[win[:, 3] >= 128]
            if len(on) * 2 < len(win):
                continue
            lab_w = PD._lab(on[:, :3].astype(float))
            idx = np.argmin(((lab_w[:, None, :] - lab_p[None]) ** 2).sum(-1), axis=1)
            out[j, i, :3] = pal[np.bincount(idx).argmax()]
            out[j, i, 3] = 255
    return out, sq


def pivot_of(g):
    """Her hind legs: the middle column of the lowest third of the figure's left half (the tail lies higher)."""
    op = g[..., 3] > 0
    h, w = op.shape
    low = op[int(h * 2 / 3):, :]
    cols = np.nonzero(low.any(axis=0))[0]
    left = cols[cols < cols.min() + (cols.max() - cols.min()) / 2]
    return (int(round(left.mean())) if len(left) else w // 2), h


def read(name):
    d = design()
    g, sq = raw_read(name)
    g = close_gaps(g, d)
    SP.FACE_ROWS, SP.FACE_COLS, SP.FACE_MIN = FACE_ROWS, FACE_COLS, FACE_MIN
    if name in NO_FACE:
        off, share = None, 0.0
    else:
        g, off, share = put_face(g, d)
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    face = None if off is None else (int(off[0] - xs.min()), int(off[1] - ys.min()))
    g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    print(f"{name:9s} squares {sq:.1f} px -> body {BODY.get(name, BODY_DEFAULT)}: {g.shape[1]}x{g.shape[0]}, face "
          f"{face}, {share:.0%} matched")
    return g, pivot_of(g), face


def big(a, z):
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
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 5] for i in range(0, len(tiles), 5)]
        for j, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"terra_poses_{j}.png")
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

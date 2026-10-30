#!/usr/bin/env python3
"""Sy'fen's Codex poses (assets/source/syfen/codex_poses: POSE_PROMPTS.md, 13 key poses and 8 run frames of his own
TFT clips on his design, 2026-10-30) at the design's body size, on the design's palette, gaps closed, the design's face
on each where the head is not turned.

    python tools/art/design_syfen_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_syfen_poses.py                  # writes assets/source/syfen/hd/pose_<name>.png (+ .json)

Codex's own cut (syfen-pose-<name>.png) brought every drawing down by one shared 0.90 onto 8 px squares: the same scale
for all, but 0.9 of the design, and the drawings themselves are not one body size - the run's body was drawn about
0.85 of the others' (the horns' and the plates' areas, 2026-10-30). So each pose is read from Codex's raw drawing
(raw/syfen-pose-<name>.png, on its own squares: regrid) and brought to the design's body by BODY[name]: how many of
its own squares make one of the design's (its horn scale - the horns' area against the design's, the one colour only
the horns have - times 8 px over its square). BODY > 1: brought down (pixel_down, the design's palette); BODY < 1: the
raw read again on squares BODY times its own (finer than drawn: a square now and then read twice). Then the colours are
snapped to the design's own (nearest in Lab), the one-square cracks and small holes closed (design_silco_poses
.close_gaps), loose specks dropped, and the design's own face (the head plate round the eye and the snout's top)
pasted where it matches best (the user's rule: one face in every frame; FACE_*), only where at least FACE_MIN of its
squares already match (a head turned down to bite keeps Codex's).
Each pose's json keeps where his root and the ground fall in it (pivot) and where the face went: the pack drew every
reference with his root on canvas column ROOT_X and his lowest point on SOLE_Y, and Codex drew over the reference in
place, so the root's column in the raw drawing is ROOT_X; the soles are its lowest row.
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
import pack_syfen_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_syfen_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "syfen", "codex_poses", "syfen-poses")
OUT = os.path.join(ROOT, "assets", "source", "syfen", "hd")
ROOT_X = 560                  # the pack's root column on the canvas (the design's root column 56.0, centred)
# the raw drawings' horn scale (raw px per design square / 8: the horns' area against the design's, 2026-10-30)
HORN = {"a1_wind": 1.11, "a1_hit": 0.97, "a2_wind": 1.04, "a2_hit": 1.02, "q_rear": 0.90, "q_bite": 0.87,
        "e_spread": 1.03, "e_sweep": 0.97, "r_roar": 0.96, "r_charge": 0.81, "r_bite": 1.02, "d_fall": 1.05,
        "d_down": 0.82, "run1": 0.82, "run2": 0.88, "run3": 0.84, "run4": 0.88, "run5": 0.89, "run6": 0.94,
        "run7": 0.85, "run8": 0.95}
SPECK = 6                     # parts apart from the figure smaller than this are dropped
# the face (the user's rule: the idle's face in every frame): the design's mask, eyes and the mane's top, rows / columns
# of hd/idle.png, pasted on each pose where it matches best (searched FACE_SEARCH squares round the magenta eyes)
FACE_ROWS, FACE_COLS = (22, 35), (106, 125)
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
    """The near-white pink squares' middle (x, y) (his glowing eye), or None."""
    c = a[..., :3].astype(int)
    m = (a[..., 3] > 0) & (c[..., 0] > 235) & (c[..., 2] > 235) & (c[..., 1] > 190) & (c[..., 1] < 240)
    ys, xs = np.nonzero(m)
    return (xs.mean(), ys.mean()) if len(xs) else None


def put_face(g, d, hint=None):
    """The design's face pasted on the pose at the offset where most of its squares already match (in Lab, within a
    few steps), searched round where the eyes say (or `hint`, where they were before the pose was brought down);
    only on the pose's own squares. -> (pose, offset, match share)."""
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
    if score < FACE_MIN * pm.sum():   # the head turned (a bite): Codex's own face stays
        return g, None, score / pm.sum()
    out = g.copy()
    win = out[y:y + patch.shape[0], x:x + patch.shape[1]]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out, (x - c0, y - r0), score / pm.sum()


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("syfen-pose-"):-4]: e for e in json.load(f)["assets"]}


def body_of(name, sq):
    """How many of the raw drawing's own squares make one of the design's."""
    return 8 * HORN[name] / sq


def raw_read(name, m=None):
    """Codex's raw drawing at the design's body size and palette -> (figure, root (x, y) in it: y the soles' line under
    the lowest row, the eye (x, y) in it: its glow can go in the bringing down)."""
    d = design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"syfen-pose-{name}.png"))).convert("RGBA")).copy()
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    sq = RG.square_size(RG.profile(a, op, 1), xs.min(), xs.max())
    body = body_of(name, sq)
    if body < 1:   # its squares bigger than the design's at this body: read on finer squares
        sq *= body
        body = 1.0
    g, _, (bx, _) = RG.regrid(a, sq)
    gy, gx = np.nonzero(g[..., 3] >= 128)
    col = np.searchsorted(bx, ROOT_X) - 1 + (ROOT_X - bx[max(0, np.searchsorted(bx, ROOT_X) - 1)]) / sq
    root = (col - gx.min(), 0)
    g = g[gy.min():gy.max() + 1, gx.min():gx.max() + 1].copy()
    g[..., 3] = np.where(g[..., 3] >= 128, 255, 0)
    root = (root[0], g.shape[0])
    g = snap(g, d)
    k = 1 / body
    e = eyes(g)
    if k < 1:
        pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
        im, root2 = PD.pixelate(g, k, root, PD.edge_colour(d), pal=pal)
        e = None if e is None else (root2[0] + (e[0] - root[0]) * k, root2[1] + (e[1] - root[1]) * k)
        g, root = snap(np.asarray(im).copy(), d), root2
    return g, root, e


def read(name, m=None):
    """The pose at the design's body size, on the design's palette, with the design's face -> (figure, the root's
    square in it, the face's offset)."""
    d = design()
    g, root, e = raw_read(name, m or manifest())
    g = close_gaps(g, d)
    g, off, share = put_face(g, d, e)
    print(f"{name:9s} horn {HORN[name]:.2f}: face at {off}, {share:.0%} of its squares matched before")
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
    m = manifest()
    figs = {n: read(n, m) for n in names}
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
            path = os.path.join(a.sheet, f"syfen_poses_{j}.png")
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

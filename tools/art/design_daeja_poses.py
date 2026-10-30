#!/usr/bin/env python3
"""Daeja's Codex poses (assets/source/daeja/codex_poses: POSE_PROMPTS.md, 13 key poses of his own TFT clips on his
design, 2026-10-30) at the design's body size, on the design's palette, gaps closed, the design's face on each.

    python tools/art/design_daeja_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_daeja_poses.py                  # writes assets/source/daeja/hd/pose_<name>.png (+ .json)

Codex's own cut (pixel_1x/: every raw drawing shrunk or grown until its whole figure filled its reference's box, then
read on 10 px squares) made the body a different size in every pose: the wider a pose's wings, the smaller its body -
0.6 to 1 times the design's (the user, 2026-10-30: 「怎么模型会一大一小」). So each pose is read from Codex's raw drawing
instead (raw/daeja-pose-<name>.png, on its own squares: regrid), where the body is drawn whole at one size, and brought
down by BODY[name] - how many times the design's body the raw drawing's is - to the design's body size (pixel_down,
the design's palette). BODY: a_wind and a_punch from Codex's own fit (their references were the idle at the design's
height: 944 / 690 and 873 / 690 raw px to canvas px), the others judged against the design side by side on the raw
reads (chest plate, shoulders, thighs; the eyes-to-soles height and the legs' area as checks). Then the colours are
snapped to the design's own (nearest in Lab), the one-square cracks and small holes closed (design_silco_poses
.close_gaps), loose specks dropped, and the design's own face (mask, eyes, the mane's top) pasted where it matches best
(the user's rule: one face in every frame; FACE_*).
Each pose's json keeps where his root and the ground fall in it (pivot) and where the face went: the pack drew every
reference with his root on one canvas column (pack_daeja_poses: the design's root column 31.9 -> canvas x 649), and
Codex's manifest says how it placed the raw drawing over the reference (raw_actor_bbox -> actor_bbox), so the root's
column in the raw drawing is known; the soles are its lowest row. The run is not read: rig_daeja walks on the idle's
own legs (Codex's eight run frames kept one leg ahead).
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
import pack_daeja_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_daeja_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "daeja", "codex_poses", "daeja-poses")
OUT = os.path.join(ROOT, "assets", "source", "daeja", "hd")
ROOT_X = 649                  # the pack's root column on the canvas (the design's root column 31.9, centred)
# how many times the design's body each raw drawing's body is (read on its own squares)
BODY = {"a_wind": 944 / 690, "a_punch": 873 / 690, "q_raise": 1.33, "q_sweep": 1.10, "e_beat": 1.28, "e_hop": 1.10,
        "r_up": 1.05, "r_fly1": 1.08, "r_fly2": 1.12, "r_blast": 1.00, "r_land": 1.25, "d_fall": 1.15, "d_down": 1.00}
SPECK = 6                     # parts apart from the figure smaller than this are dropped
# the face (the user's rule: the idle's face in every frame): the design's mask, eyes and the mane's top, rows / columns
# of hd/idle.png, pasted on each pose where it matches best (searched FACE_SEARCH squares round the magenta eyes)
FACE_ROWS, FACE_COLS = (21, 32), (28, 42)
FACE_SEARCH = 4
NAMES = [n for n in PK.POSES if not n.startswith("run")]


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
    out = g.copy()
    win = out[y:y + patch.shape[0], x:x + patch.shape[1]]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out, (x - c0, y - r0), score / pm.sum()


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("daeja-pose-"):-4]: e for e in json.load(f)["assets"]}


def raw_read(name, m):
    """Codex's raw drawing on its own squares, at the design's body size and palette -> (figure, root (x, y) in it:
    y the soles' line under the lowest row, the eyes (x, y) in it: their magenta can go in the bringing down)."""
    d = design()
    e = m[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, e["raw"]))).convert("RGBA")).copy()
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    sq = RG.square_size(RG.profile(a, op, 1), xs.min(), xs.max())
    g, _, _ = RG.regrid(a, sq)
    # the root's column: the canvas column ROOT_X in Codex's placed figure (actor) back in the raw drawing's px
    rx0, _, rx1, _ = e["raw_actor_bbox"]
    ax0, _, ax1, _ = e["actor_bbox"]
    raw_x = rx0 + (ROOT_X - ax0) * (rx1 - rx0) / (ax1 - ax0)
    root = ((raw_x - xs.min()) / sq, g.shape[0])
    g = snap(g, d)
    k = 1 / BODY[name]
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
    print(f"{name:9s} body / {BODY[name]:.2f}: face at {off}, {share:.0%} of its squares matched before")
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    face = None if off is None else (off[0] - xs.min(), off[1] - ys.min())
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

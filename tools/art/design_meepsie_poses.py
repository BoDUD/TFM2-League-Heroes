#!/usr/bin/env python3
"""Meepsie's Codex poses (assets/source/meepsie/codex_poses: POSE_PROMPTS.md, 20 poses of its own TFT clips on its
design, 2026-11-01) at the design's body size, on the design's palette, gaps closed, the design's pilot face on each.

    python tools/art/design_meepsie_poses.py --sheet DIR      # all poses beside the design (4x), pivots marked
    python tools/art/design_meepsie_poses.py                  # writes assets/source/meepsie/hd/pose_<name>.png (+ .json)

Codex was asked the design at 6 px a square but drew every pose a little bigger and each a different size (run4 6.2,
run3 7.7 raw px a design square; its own edge squares 5-8 px). BODY[name] raw px is the design's square, measured two
ways and averaged (codex-fit-shrinks-bodies): the figure's area against the design's (sqrt) and the meep pilot's pale
lime against the design's (sqrt of the areas); the walk frames also by their height against the design's 115 rows;
d_down (the pilot hidden) by its area alone. Each raw drawing is read on squares of BODY px (raw_read: the commonest
design colour round each square's centre), the one-square cracks and small holes closed (design_silco_poses.close_gaps),
loose specks dropped, and the design's own pilot face (its antenna, its head with the two big black eyes and the smile)
pasted where it matches best (the user's rule: one face in every frame), only where at least FACE_MIN of its squares
already match and the pale lime of the pose's own pilot lies under the patch's.
Each pose's json keeps its pivot (the point between its feet, on the ground): the design's pivot column DESIGN_PIVOT
carried by where the face landed (the torso carries the cockpit; the walk keeps it steady), PIVOT[name] where the face
does not tell (d_down) or the body bends away from its feet (set on the sheet by eye); the ground is the figure's
lowest row.
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
import pack_meepsie_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_meepsie_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import snap, lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "meepsie", "codex_poses", "meepsie-poses")
OUT = os.path.join(ROOT, "assets", "source", "meepsie", "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the meep pilot's antenna and head, the two big black eyes
# and the smile - rows / columns of hd/idle.png (its hands below row 44 stay the pose's own: e_call cheers)
FACE_ROWS, FACE_COLS = (23, 44), (70, 88)
FACE_MIN = 0.38
NO_FACE = {"d_down"}           # ducked down into its cockpit (POSE_PROMPTS): no face to paste
LIME = np.array([[218, 247, 112], [166, 210, 81]])   # the pilot's own pale lime (the leaves are darker greens)
WIN = 5                       # raw pixels round each design square's centre that vote
BODY_DEFAULT = 7.0
BODY = {"a_punch": 6.99, "a_raise": 6.6, "q_raise": 7.05, "q_smash": 7.13, "e_ready": 7.11, "e_call": 6.59,
        "r_jump": 6.74, "r_air": 6.94, "r_land": 7.11, "r_slam": 6.73,
        "run1": 7.15, "run2": 7.43, "run3": 7.71, "run4": 6.18, "run5": 6.73, "run6": 7.11, "run7": 7.27, "run8": 7.31,
        "d_fall": 6.65, "d_down": 6.62}
DESIGN_PIVOT = 64             # hd/idle.png: between its two legs
PIVOT = {}                    # name -> pivot column in the read pose where the face does not carry it
FACE_NEAR = {}
NEAR = 4
NEAR_MIN = 0.2
DARK_EYE = set()


def lime(px):
    """The pilot's pale lime (exactly the design's two colours: the reads are snapped to its palette)."""
    m = np.zeros(px.shape[:2], bool)
    for c in LIME:
        m |= (px[..., :3] == c).all(-1)
    return m & (px[..., 3] > 0)


def put_face(g, d, near=None):
    """The design's face pasted where most of its squares already match (in Lab, within a few steps) AND its pale lime
    lands on the pose's own pilot (at least half the patch's lime squares lime). -> (pose, offset, match share)."""
    (r0, r1), (c0, c1) = FACE_ROWS, FACE_COLS
    patch = d[r0:r1, c0:c1]
    pm = patch[..., 3] > 0
    ph, pw = patch.shape[:2]
    eye = lime(patch)
    lab_g, lab_p = lab(g), lab(patch)
    best = (-1, 0, 0)
    for y in range(0, g.shape[0] - ph + 1):
        for x in range(0, g.shape[1] - pw + 1):
            win = g[y:y + ph, x:x + pw]
            if near and (abs(x - near[0]) > NEAR or abs(y - near[1]) > NEAR):
                continue
            if (lime(win) & eye).sum() * 2 < eye.sum():
                continue
            both = pm & (win[..., 3] > 0)
            dist = ((lab_g[y:y + ph, x:x + pw] - lab_p) ** 2).sum(-1)
            score = int((both & (dist < 400)).sum())
            if score > best[0]:
                best = (score, x, y)
    score, x, y = best
    if score < (NEAR_MIN if near else FACE_MIN) * pm.sum():   # the head turned: Codex's own face stays
        return g, None, max(score, 0) / pm.sum()
    out = g.copy()
    win = out[y:y + ph, x:x + pw]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out, (x - c0, y - r0), score / pm.sum()


NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw_read(name):
    """Codex's raw drawing at the design's body, on the design's palette -> (figure, its own square size).
    Every design square takes the commonest design colour among the raw pixels round its centre (WIN x WIN, each
    snapped to the design's palette in Lab): a mean over Codex's squares mixed the stone with the outline into brown."""
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"meepsie-pose-{name}.png"))).convert("RGBA")).copy()
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


def pivot_of(name, g, face):
    """Between its feet: the design's pivot carried by the face, else PIVOT[name], else the figure's middle."""
    h, w = g.shape[:2]
    if name in PIVOT:
        return PIVOT[name], h
    if face is not None:
        return int(round(DESIGN_PIVOT + face[0])), h
    return w // 2, h


def read(name):
    d = design()
    g, sq = raw_read(name)
    g = close_gaps(g, d)
    if name in NO_FACE:
        off, share = None, 0.0
    else:
        g, off, share = put_face(g, d, FACE_NEAR.get(name))
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
    return g, pivot_of(name, g, face), face


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
                px = DESIGN_PIVOT if n == "design" else figs[n][1][0]
                dr.line([(x + px * z, 24 + (Hm - t.shape[0]) * z), (x + px * z, 24 + Hm * z)], fill=(255, 0, 0, 255))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"meepsie_poses_{j}.png")
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

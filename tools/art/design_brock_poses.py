#!/usr/bin/env python3
"""Brock's Codex poses (assets/source/brock/codex_poses: POSE_PROMPTS.md, 20 poses of his own TFT clips on his design,
2026-11-02) at the design's body size, on the design's palette, gaps closed, the design's face on each.

    python tools/art/design_brock_poses.py --sheet DIR      # all poses beside the design (4x), pivots marked
    python tools/art/design_brock_poses.py                  # writes assets/source/brock/hd/pose_<name>.png (+ .json)

Codex was asked the design at 12 px a square and drew each pose at its own size, 12-16 px a design square (each fitted
to its reference's box: codex-fit-shrinks-bodies; run2 and run3 a fifth bigger than run1). BODY[name] raw px is the
design's square: the square root of the pose's violet chest-emblem pixels over the design's 20 emblem squares, averaged
with the same for the whole figure's area (the emblem alone is too small to trust; the area alone grows with spread
fists), or BODY_DEFAULT where the emblem is hidden (the slams and the landing: curled over, face down). The run frames are
read too but not used: all eight drew the legs about 40% longer than the design's (27-32 rows under the emblem against
21) and run3 / run5 the upper body a seventh bigger, so he would grow a head taller each time he set off; his walk is
rig_brock.py's, from the design itself. Each raw
drawing is read on squares of BODY px (raw_read: the commonest design colour round each square's centre), the one-square
cracks and small holes closed (design_silco_poses.close_gaps), loose specks dropped, and the design's own face (the
grey-blue hood, the orange face plate and its two ring eyes) pasted where it matches best (the user's rule: one face in
every frame), only where at least FACE_MIN of its squares already match and its eyes land on the pose's own glow.
Each pose's json keeps its pivot (the point between its feet, on the ground): the design's pivot column DESIGN_PIVOT
carried by where the face landed (the torso carries the head; the run keeps it steady), PIVOT[name] where the face
does not tell (lying down) or the body bends away from its feet (the slams: set on the sheet by eye); the ground is the
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
import pack_brock_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_brock_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import snap, lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "brock", "codex_poses", "brock-poses")
OUT = os.path.join(ROOT, "assets", "source", "brock", "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the grey-blue hood, the orange face plate, the two ring
# eyes - rows / columns of hd/idle.png
FACE_ROWS, FACE_COLS = (11, 23), (34, 45)
FACE_MIN = 0.38
NO_FACE = {"d_down", "a_slam", "r_land"}   # face down / curled over the fists: no face to paste
BODY_DEFAULT = 13.5
WIN = 5                       # raw pixels round each design square's centre that vote
BODY = {}                     # filled by body_of() from the raws (emblem + area), printed with every read
EMBLEM, AREA = 20, None       # the design's violet emblem squares; its figure squares (set on first use)


def violet(px):
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (b > 150) & (r > 80) & (g < 120) & (b - g > 60)


def body_of(name):
    """The raw px a design square takes in this pose: the emblem's scale and the area's, averaged."""
    if name in BODY:
        return BODY[name]
    d = design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"brock-pose-{name}.png"))).convert("RGBA"))
    op = a[..., 3] >= 128
    area = np.sqrt(op.sum() / (d[..., 3] > 0).sum())
    emb = violet(a) & op
    if name in NO_FACE or emb.sum() < 1000:
        BODY[name] = BODY_DEFAULT
    else:
        BODY[name] = round((np.sqrt(emb.sum() / EMBLEM) + area) / 2, 2)
    return BODY[name]


DESIGN_PIVOT = 36             # hd/idle.png: between his two legs
PIVOT = {}                    # name -> pivot column in the read pose where the face does not carry it
EYE = (slice(5, 8), slice(2, 9))      # the two ring eyes inside the face patch (hd/idle.png rows 16-18, columns 36-42)
DARK_EYE = {"d_down"}         # the face plate gone dark
# where Codex drew the head (the face patch's top-left, read off a 5x grid of the read pose) on the poses whose fists or
# chest also hold the face's colours: the search stays within NEAR squares of it
FACE_NEAR = {"a_raise": (27, 35)}   # under the raised arms: its own face read loosely
NEAR = 4
NEAR_MIN = 0.2               # where FACE_NEAR names the head, its own looser stump still takes the face         # the eye gone dark: its glowing squares take the design's darkest teal


def glowing(px):
    """The face plate's warm glow (orange, the yellow rings), not the stone."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (r > 200) & (b < 100) & (r - b > 120)


def put_face(g, d, near=None):
    """The design's face pasted where most of its squares already match (in Lab, within a few steps) AND its eye lands
    on the pose's own glowing face (at least half the eyes' squares warm): without it the grey-blue hood also matched
    the pale shoulder boulders and a fist (two heads). -> (pose, offset, match share)."""
    (r0, r1), (c0, c1) = FACE_ROWS, FACE_COLS
    patch = d[r0:r1, c0:c1]
    pm = patch[..., 3] > 0
    ph, pw = patch.shape[:2]
    eye = np.zeros_like(pm)
    eye[EYE] = glowing(patch[EYE]) & pm[EYE]
    lab_g, lab_p = lab(g), lab(patch)
    best = (-1, 0, 0)
    for y in range(0, g.shape[0] - ph + 1):
        for x in range(0, g.shape[1] - pw + 1):
            win = g[y:y + ph, x:x + pw]
            if near and (abs(x - near[0]) > NEAR or abs(y - near[1]) > NEAR):
                continue
            if (glowing(win) & eye).sum() * 2 < eye.sum():
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


def dark_eye(g, d):
    """The face gone out: every glowing square takes the design's darkest root brown."""
    op = d[..., 3] > 0
    cols = np.unique(d[op][:, :3], axis=0)
    brown = cols[(cols[:, 0] > cols[:, 2] + 30) & (cols[:, 1] < 110) & (cols.sum(1) > 120)]
    dark = brown[np.argmin(brown.sum(1))]
    out = g.copy()
    m = glowing(out) & (out[..., 3] > 0)
    out[m, :3] = dark
    return out
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw_read(name):
    """Codex's raw drawing at the design's body, on the design's palette -> (figure, its own square size).
    Every design square takes the commonest design colour among the raw pixels round its centre (WIN x WIN, each
    snapped to the design's palette in Lab): a mean over Codex's squares mixed the stone with the outline into brown."""
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"brock-pose-{name}.png"))).convert("RGBA")).copy()
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    sq = RG.square_size(RG.profile(a, op, 1), xs.min(), xs.max())
    body = body_of(name)
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
    if name in DARK_EYE:
        g = dark_eye(g, d)
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
    print(f"{name:9s} squares {sq:.1f} px -> body {body_of(name)}: {g.shape[1]}x{g.shape[0]}, face "
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
            path = os.path.join(a.sheet, f"brock_poses_{j}.png")
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

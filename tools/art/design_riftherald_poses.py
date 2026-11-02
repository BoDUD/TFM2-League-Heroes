#!/usr/bin/env python3
"""The Rift Herald's Codex poses (assets/source/riftherald/codex_poses: POSE_PROMPTS.md, 18 poses of its own TFT clips on its
design, 2026-11-02) at the design's body size, on the design's palette, gaps closed, the design's face on each.

    python tools/art/design_riftherald_poses.py --sheet DIR      # all poses beside the design (4x), pivots marked
    python tools/art/design_riftherald_poses.py                  # writes assets/source/riftherald/hd/pose_<name>.png (+ .json)

Codex was asked the design at 8 px a square and drew each pose at its own size (each fitted to its reference's box:
codex-fit-shrinks-bodies). BODY[name] raw px is the design's square: the square root of the pose's blue-violet SHELL
pixels over the design's shell squares (the shell is one rigid dome in every pose: the steadiest measure; the whole
figure's area grows with a raised pincer or a flung tail), or BODY_DEFAULT where the shell is seen edge-on or curled
(none so far). The run frames are read too but not used: Codex's six differ in body size and style from frame to frame
(codex-walk-drafts-differ); its scuttle is rig_riftherald.py's, from the design itself. Each raw drawing is read on
squares of BODY px (raw_read: the commonest design colour round each square's centre), the one-square cracks and small
holes closed (design_silco_poses.close_gaps), loose specks dropped, and the design's own face (the two magenta eyes,
the gold fangs under them) pasted where it matches best (the user's rule: one face in every frame), only where at least
FACE_MIN of its squares already match and its eyes land on the pose's own magenta glow.
Each pose's json keeps its pivot (the point between its feet, on the ground): the design's pivot column DESIGN_PIVOT
carried by where the face landed, PIVOT[name] where the face does not tell (flipped, spinning, lying down); the ground is
the figure's lowest row.
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
import pack_riftherald_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_riftherald_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "riftherald", "codex_poses", "riftherald-poses")
OUT = os.path.join(ROOT, "assets", "source", "riftherald", "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the two magenta eyes and the gold fangs under them - rows /
# columns of hd/idle.png (design_riftherald_model.EYES)
FACE_ROWS, FACE_COLS = (35, 47), (70, 90)
FACE_MIN = 0.38
NO_FACE = {"q_spin", "e_flip", "e_charge", "d_fall", "d_down", "r_slam"}   # turned away, head down, curled, or (r_slam)
# the face matched a pincer's magenta and gold: Codex's own face stays
BODY_DEFAULT = 9.0
WIN = 5                       # raw pixels round each design square's centre that vote
BODY = {}                     # filled by body_of() from the raws (the shell), printed with every read
# set by hand: reared up its shell is seen side-on, its area a fifth smaller - read by it the pose came out 144 rows,
# a 1.64x rise over the design's 88 (TFT's rear is 1.45x: step 0's B, 61 squares against A's 42)
BODY_FIX = {"e_rear": 8.7}


def shell(px):
    """The blue-violet crystal plates (not the plum body, not the gold, not the magenta spots)."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (b - r > 45) & (b > 110)


def body_of(name):
    """The raw px a design square takes in this pose: the shell's scale."""
    if name in BODY:
        return BODY[name]
    if name in BODY_FIX:
        BODY[name] = BODY_FIX[name]
        return BODY[name]
    d = design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"riftherald-pose-{name}.png"))).convert("RGBA"))
    op = a[..., 3] >= 128
    sh = shell(a) & op
    ds = (shell(d) & (d[..., 3] > 0)).sum()
    BODY[name] = round(float(np.sqrt(sh.sum() / ds)), 2) if sh.sum() > 2000 else BODY_DEFAULT
    return BODY[name]


DESIGN_PIVOT = 55             # hd/idle.png: between its two hind feet (far foot columns 36-51, near 58-73)
PIVOT = {"a_raise": 56, "a_strike": 55, "e_rear": 60}   # between the hind feet where the face does not carry it (by eye)
EYE = (slice(4, 6), slice(5, 17))     # the two eyes inside the face patch (hd/idle.png rows 39-40, columns 75-86)
DARK_EYE = {"d_down"}         # the eyes and spots gone dark
FACE_NEAR = {}
NEAR = 4
NEAR_MIN = 0.2


def glowing(px):
    """The magenta glow (its eyes, its shell spots)."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (r > 170) & (b > 140) & (g < 120)


def put_face(g, d, near=None):
    """The design's face pasted where most of its squares already match (in Lab, within a few steps) AND its eyes land
    on the pose's own magenta glow (at least half the eyes' squares glowing). -> (pose, offset, match share)."""
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
    """The eyes and the shell's spots gone out: every magenta square takes the design's darkest plum."""
    op = d[..., 3] > 0
    cols = np.unique(d[op][:, :3], axis=0)
    plum = cols[(cols[:, 0] > cols[:, 1] + 15) & (cols[:, 2] > cols[:, 1] + 15) & (cols.sum(1) > 90)]
    dark = plum[np.argmin(plum.sum(1))]
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
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"riftherald-pose-{name}.png"))).convert("RGBA")).copy()
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
            path = os.path.join(a.sheet, f"riftherald_poses_{j}.png")
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

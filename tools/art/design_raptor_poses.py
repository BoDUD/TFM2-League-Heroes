#!/usr/bin/env python3
"""The Crimson Raptor's Codex poses (assets/source/raptor/codex_poses: POSE_PROMPTS.md, 18 poses of its own TFT clips
on its design, 2026-10-31) at the design's body size, on the design's palette, gaps closed, the design's face on each.

    python tools/art/design_raptor_poses.py --sheet DIR      # all poses beside the design (4x), pivots marked
    python tools/art/design_raptor_poses.py                  # writes assets/source/raptor/hd/pose_<name>.png (+ .json)

Codex was asked the design at 10 px a square and drew its own 9-10 px squares, but every pose at its own body size:
10-14 raw px for one design square (measured by the purple ruff's and the whole figure's areas against hd/idle.png's,
then set by eye on the sheet so the head matches the design's): BODY[name]. Each raw drawing is read on squares of BODY
px (raw_read: the commonest design colour round each square's centre), the one-square cracks and small holes closed
(design_silco_poses.close_gaps), loose specks dropped, and the design's own upper face (the brow, the two orange eyes,
the top of the hooked beak; not the lower beak, which the open-mouthed poses swing down) pasted where it matches best
(the user's rule: one face in every frame), only where at least FACE_MIN of its squares already match.
Each pose's json keeps its pivot (the point between its feet, on the ground): the design's pivot column DESIGN_PIVOT
carried by where the face landed (the torso carries the head), PIVOT[name] where set by eye (lying down), else the
middle of its talons in its lowest rows less CLAW_TO_PIVOT (the design's talons stand that far right of its pivot: the
tilted heads, where no face is pasted); the ground is the figure's lowest row. The run is not Codex's: rig_raptor.py
walks the design's own idle (each run frame here was its own body).
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
import pack_raptor_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_raptor_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import snap, lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "raptor", "codex_poses", "raptor-poses")
OUT = os.path.join(ROOT, "assets", "source", "raptor", "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the brow, the two orange eyes, the top of the hooked
# beak - rows / columns of hd/idle.png (the lower beak below row 34 stays Codex's: the open-mouthed poses)
FACE_ROWS, FACE_COLS = (18, 34), (46, 75)
FACE_MIN = 0.38
NO_FACE = {"d_down"}           # lying on its side, the head upside down, the eyes dark (POSE_PROMPTS)
BODY_DEFAULT = 11.0
WIN = 5                       # raw pixels round each design square's centre that vote
# fitted (C:/t/rp_work/fit_body.py: the body size where the design's face matches best, 0.84-1.2 x the area estimate) where
# the face is level; the tilted heads (a_back's eyes read too small, q_rear, r_rear, r_call, d_fall) keep the area
# estimate, checked by eye on the sheet; q_spread between the fit (11.3, its head turned to the front) and its area (13.5,
# swollen by the spread wings)
BODY = {"a_back": 13.4, "a_jab": 10.4, "d_down": 12.0, "d_fall": 12.4, "e_hop": 12.85, "e_land": 11.3, "q_rear": 12.6,
        "q_spread": 12.0, "r_call": 11.4, "r_rear": 14.0, "run1": 11.1, "run2": 10.1, "run3": 10.1, "run4": 9.6,
        "run5": 10.8, "run6": 11.5, "run7": 12.0, "run8": 10.2}
DESIGN_PIVOT = 42             # hd/idle.png: between its two legs (pack_raptor_poses' root column 42.5)
PIVOT = {"d_down": 46}        # name -> pivot column in the read pose where neither the face nor the talons tell
CLAW_TO_PIVOT = 7             # hd/idle.png: its talons' middle (bottom CLAW_ROWS rows, 48.6) stands 7 columns right of its pivot
CLAW_ROWS = 8
EYE = (slice(9, 14), slice(7, 13))   # the near orange eye inside the face patch (hd/idle.png rows 27-31, columns 53-58)
DARK_EYE = {"d_down"}
# where Codex drew the head (the face patch's top-left, read off the sheet) on the poses whose open mouth also glows
# orange: the search stays within NEAR squares of it
FACE_NEAR = {}
NEAR = 4
NEAR_MIN = 0.2               # where FACE_NEAR names the head, its own looser match still takes the face


def glowing(px):
    """The eyes' bright orange to yellow (and the lit mouth), not the brown head or the red feathers."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (r > 220) & (g > 110) & (b < 110) & (r - b > 140)


def put_face(g, d, near=None):
    """The design's face pasted where most of its squares already match (in Lab, within a few steps) AND its eye lands
    on the pose's own glowing eye (at least half the eye's squares cyan): without the eye the pale stump also matched
    the brown legs (two heads). -> (pose, offset, match share)."""
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
    """The eyes gone out: every glowing square takes the design's darkest brown that is not the outline."""
    op = d[..., 3] > 0
    cols = np.unique(d[op][:, :3], axis=0)
    brown = cols[(cols[:, 0] > cols[:, 2]) & (cols[:, 1] > cols[:, 2]) & (cols.sum(1) > 150)]
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
    snapped to the design's palette in Lab): a mean over Codex's squares mixes the feathers with the outline."""
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"raptor-pose-{name}.png"))).convert("RGBA")).copy()
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


def talons(g):
    """The dark navy talon squares (blue over red, not the purple ruff's light blues)."""
    r, gg, b = g[..., 0].astype(int), g[..., 1].astype(int), g[..., 2].astype(int)
    return (g[..., 3] > 0) & (b > r + 10) & (r < 90) & (gg < 90)


def pivot_of(name, g, face):
    """Between its feet: the design's pivot carried by the face, else PIVOT[name], else its talons' middle less
    CLAW_TO_PIVOT, else the figure's middle."""
    h, w = g.shape[:2]
    if face is not None:
        return int(round(DESIGN_PIVOT + face[0])), h
    if name in PIVOT:
        return PIVOT[name], h
    low = talons(g)
    low[:h - CLAW_ROWS] = False
    if low.any():
        return int(round(np.nonzero(low)[1].mean())) - CLAW_TO_PIVOT, h
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
            path = os.path.join(a.sheet, f"raptor_poses_{j}.png")
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

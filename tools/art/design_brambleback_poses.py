#!/usr/bin/env python3
"""The Crimson Brambleback's Codex poses (assets/source/brambleback/codex_poses: POSE_PROMPTS.md, 19 poses of its own
TFT clips on its design, 2026-10-31) at the design's body size, on the design's palette, gaps closed, the design's face
on each.

    python tools/art/design_brambleback_poses.py --sheet DIR      # all poses beside the design (4x), pivots marked
    python tools/art/design_brambleback_poses.py                  # writes assets/source/brambleback/hd/pose_<name>.png (+ .json)

Codex was asked the design at 8 px a square but drew every pose bigger (fitted to the canvas: the crouched frames
660-700 px from the branches to the claws against the design's 68 squares), and not all at one size: BODY[name] raw px
is the design's square (BODY_DEFAULT unless the pose says otherwise, set by the claws and the head against the design's
on the sheet). Each raw drawing is read on squares of BODY px (raw_read: the commonest design colour round each
square's centre), the one-square cracks and small holes closed (design_silco_poses.close_gaps), loose specks dropped,
and the design's own face (the wedge head, its two red eyes with their hot centres and the orange forehead spiral)
pasted where it matches best (the user's rule: one face in every frame), only where at least FACE_MIN of its squares
already match and its eyes land on the pose's own glowing eyes.
Each pose's json keeps its pivot (the point under its body, on the ground): the design's pivot column DESIGN_PIVOT
carried by where the face landed, PIVOT[name] where the face does not tell (rearing up, lying down: set on the sheet by
eye); the ground is the figure's lowest row.
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
import pack_brambleback_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_brambleback_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import snap, lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "brambleback", "codex_poses", "brambleback-poses")
OUT = os.path.join(ROOT, "assets", "source", "brambleback", "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the wedge head, its two red eyes, the forehead spiral -
# rows / columns of hd/idle.png
FACE_ROWS, FACE_COLS = (20, 35), (67, 88)
FACE_MIN = 0.38
NO_FACE = {"d_down"}           # lying flat: the eyes are dark (POSE_PROMPTS), no face to paste
BODY_DEFAULT = 10.2
WIN = 5                       # raw pixels round each design square's centre that vote
BODY = {"run7": 8.6}          # run7 drawn smaller (55 rows at 10.2 against the walk's 66-77)
DESIGN_PIVOT = 52             # hd/idle.png: under the middle of its body
PIVOT = {}                    # name -> pivot column in the read pose where the face does not carry it
EYE = (slice(9, 13), slice(3, 18))   # the two red eyes inside the face patch (hd/idle.png rows 29-32, columns 70-84)
DARK_EYE = set()              # d_down: Codex already put out the eyes and the core (its claws keep their red)
# where Codex drew the head (the face patch's top-left = its near eye - (6, 11), read off a 5x grid of each read pose):
# its claws and veins hold the same hot reds as the eyes, so the search stays within NEAR squares of it on every pose
FACE_NEAR = {"a_raise": (57, 45), "a_swipe": (62, 34), "q_jump": (76, 23), "q_reach": (54, 48), "q_land": (66, 22),
             "e_crouch": (71, 27), "e_rear": (63, 20), "r_rear": (58, 62), "r_slam": (70, 36), "run1": (60, 21),
             "run2": (64, 22), "run3": (60, 16), "run4": (61, 26), "run5": (60, 22), "run6": (66, 22),
             "run7": (70, 20), "run8": (78, 23), "d_rear": (36, 40)}
NEAR = 4
NEAR_MIN = 0.2               # where FACE_NEAR names the head, its own looser wedge still takes the face


def glowing(px):
    """The eyes' hot centres (yellow-white to bright orange; Codex's eyes are often only orange), not the red veins or
    the claws' darker reds."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (r > 220) & (g > 95) & (b < 90)


def put_face(g, d, near=None):
    """The design's face pasted where most of its squares already match (in Lab, within a few steps) AND its eye lands
    on the pose's own glowing eyes (at least half the eyes' hot squares): without the eyes the bark also matched
    any bark plate. -> (pose, offset, match share)."""
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
            hits = (glowing(win) & eye).sum()
            if (hits * 2 < eye.sum()) if near is None else hits < 1:   # by hand: one eye square is enough
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
    """The eyes and the core gone out: every glowing square takes the design's darkest red-brown that is not the
    outline."""
    op = d[..., 3] > 0
    cols = np.unique(d[op][:, :3], axis=0)
    brown = cols[(cols[:, 0] > cols[:, 2]) & (cols.sum(1) > 90) & (cols[:, 0] < 120)]
    dark = brown[np.argmin(brown.sum(1))]
    out = g.copy()
    r, gg, b = out[..., 0].astype(int), out[..., 1].astype(int), out[..., 2].astype(int)
    m = (r > 200) & (r - b > 120) & (out[..., 3] > 0)
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
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"brambleback-pose-{name}.png"))).convert("RGBA")).copy()
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
            path = os.path.join(a.sheet, f"brambleback_poses_{j}.png")
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

#!/usr/bin/env python3
"""The Mighty Mech's Codex poses (assets/source/mightymech/codex_poses: POSE_PROMPTS.md, 18 poses of its own TFT clips on
its design, 2026-11-03) at the design's body size, on the design's palette, gaps closed, the design's face on each.

    python tools/art/design_mightymech_poses.py --sheet DIR      # all poses beside the design (4x), pivots marked
    python tools/art/design_mightymech_poses.py                  # writes assets/source/mightymech/hd/pose_<name>.png (+ .json)

Codex was asked the design at 9 px a square and drew each pose on its own squares (6-10 px, read by regrid) at its own
size, the mech some 1.3x the design's (Codex's HANDOFF: "the bodies' sizes vary"). The design's small head (a 3x2 yellow
visor) cannot measure a pose, and the whole figure's area grows with the blade-wings spread (q_brace, e_air): every pose
is read at ONE body, BODY raw px a design square = the eight run frames' mean sqrt(area / the design's area) (they stand
upright with the sword held up, wings folded: the design's own bulk), so the sword stays one length in every frame. Each
raw drawing is read on squares of BODY px (raw_read: the commonest design colour round each square's centre), the
one-square cracks and small holes closed (design_silco_poses.close_gaps), loose specks dropped, and the design's own
face (the red helmet, the silver V horn, the face plate and the yellow visor, FACE_ROWS x FACE_COLS of hd/idle.png)
pasted where it matches best (the user's rule: one face in every frame), only where at least FACE_MIN of its squares
already match and its visor lands on the pose's own yellow.
Each pose's json keeps its pivot (the point between its feet, on the ground): between its two feet (feet_mid: the two
biggest pieces in its lowest rows, the design's own DESIGN_PIVOT likewise), so the planted feet stay put; the run frames
take the design's pivot carried by where the face landed (the head runs steady, the feet step under it); PIVOT[name]
where neither tells (a sword tip in the lowest rows, kneeling). The ground is the figure's lowest row.
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
import pack_mightymech_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_mightymech_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "mightymech", "codex_poses", "mightymech-poses")
OUT = os.path.join(ROOT, "assets", "source", "mightymech", "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the red helmet, the silver V horn, the face plate and the
# yellow visor - rows / columns of hd/idle.png (design_mightymech_model.FACE_BOX)
FACE_ROWS, FACE_COLS = (20, 38), (34, 50)
FACE_MIN = 0.4
NO_FACE = {"d_down"}          # kneeling, the head hanging, the visor gone dark: Codex's own head stays
RUNS = tuple(f"run{i}" for i in range(1, 9))
MIRROR = {"a_up"}             # Codex drew it facing left (its tail and wings on the right): mirrored to face right
WIN = 5                       # raw pixels round each design square's centre that vote
BODY = {}                     # filled by body_of() from the raws (visor + area), printed with every read


def yellow(px):
    """The yellow visor and lamps."""
    r, g, b = (px[..., k].astype(int) for k in range(3))
    return (r > 200) & (g > 170) & (b < 110)


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"mightymech-pose-{name}.png"))).convert("RGBA")).copy()


def body_of(name):
    """The raw px a design square takes: the run frames' mean sqrt(area / the design's area), for every pose."""
    if not BODY:
        d = design()
        da = (d[..., 3] > 0).sum()
        b = round(float(np.mean([np.sqrt((raw(n)[..., 3] >= 128).sum() / da) for n in RUNS])), 2)
        BODY.update({n: b for n in NAMES})
    return BODY[name]


FOOT_ROWS = 8                 # the lowest rows the feet are read in
FOOT_GAP = 2                  # columns between the plates of one boot
# name -> pivot column in the read pose where its feet do not tell (the --sheet check, 2026-11-03): the sword's blade
# lies in the lowest rows (a_down, e_crouch, e_land, d_fall) - the torso's middle over the ground instead, as the
# design's pivot sits
PIVOT = {"a_down": 30, "e_crouch": 48, "e_land": 40, "d_fall": 36}
# the run: Codex's eight upper bodies differ (the sword a few squares this way or that, a wing more or less: it would
# shake every step), so every frame wears RUN_UPPER's upper body, the rows above RUN_SPLIT rows under the face's top
# (under the sword's hilt and the fists), and keeps its own hips, legs and tail below, set by its own face (codex-walk-
# drafts-differ: one upper body, the legs stepping under it)
RUN_UPPER = "run1"
RUN_SPLIT = 56


def feet_mid(g):
    """Between its feet: the middle of the two widest runs of columns in its lowest FOOT_ROWS rows (its two
    boots; pieces FOOT_GAP columns apart count as one boot)."""
    cols = (g[-FOOT_ROWS:, :, 3] > 0).any(0)
    runs, x = [], 0
    while x < len(cols):
        if cols[x]:
            x0 = x
            while x < len(cols) and (cols[x] or cols[x:x + FOOT_GAP + 1].any()):
                x += 1
            runs.append((x0, x))
        x += 1
    if len(runs) < 2:
        return None
    two = sorted(runs, key=lambda r: r[1] - r[0])[-2:]
    return int(round(np.mean([(r[0] + r[1] - 1) / 2 for r in two])))


def put_face(g, d):
    """The design's face pasted where most of its squares already match (in Lab, within a few steps) AND its visor
    lands on the pose's own yellow (at least half the visor's squares) -> (pose, offset, match share)."""
    (r0, r1), (c0, c1) = FACE_ROWS, FACE_COLS
    patch = d[r0:r1, c0:c1]
    pm = patch[..., 3] > 0
    ph, pw = patch.shape[:2]
    vis = yellow(patch) & pm
    lab_g, lab_p = lab(g), lab(patch)
    best = (-1, 0, 0)
    for y in range(0, g.shape[0] - ph + 1):
        for x in range(0, g.shape[1] - pw + 1):
            win = g[y:y + ph, x:x + pw]
            if (yellow(win) & vis).sum() * 2 < vis.sum():
                continue
            both = pm & (win[..., 3] > 0)
            dist = ((lab_g[y:y + ph, x:x + pw] - lab_p) ** 2).sum(-1)
            score = int((both & (dist < 400)).sum())
            if score > best[0]:
                best = (score, x, y)
    score, x, y = best
    if score < FACE_MIN * pm.sum():   # the head turned: Codex's own face stays
        return g, None, max(score, 0) / pm.sum()
    out = g.copy()
    win = out[y:y + ph, x:x + pw]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out, (x - c0, y - r0), score / pm.sum()


NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


DESIGN_PIVOT = feet_mid(design())   # hd/idle.png: between its two feet


def raw_read(name):
    """Codex's raw drawing at the design's body, on the design's palette -> (figure, its own square size).
    Every design square takes the commonest design colour among the raw pixels round its centre (WIN x WIN, each
    snapped to the design's palette in Lab)."""
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    a = raw(name)
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
    """The run: the design's pivot carried by the face (the head runs steady, the feet step under it); the rest: PIVOT[name],
    else between its own feet (planted: the attack's recoil rears the head back over them), else the figure's middle."""
    h, w = g.shape[:2]
    if name in RUNS and face is not None:
        return int(round(DESIGN_PIVOT + face[0])), h
    if name in PIVOT:
        return PIVOT[name], h
    f = feet_mid(g)
    return (w // 2 if f is None else f), h


def read(name):
    d = design()
    g, sq = raw_read(name)
    if name in MIRROR:
        g = g[:, ::-1].copy()
    g = close_gaps(g, d)
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
    print(f"{name:9s} squares {sq:.1f} px -> body {body_of(name)}: {g.shape[1]}x{g.shape[0]}, face "
          f"{face}, {share:.0%} matched")
    return g, pivot_of(name, g, face), face


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def one_upper(figs):
    """Every run frame: RUN_UPPER's rows above RUN_SPLIT (counted from the face's top) over the frame's own rows below
    it, both set by their faces -> {name: (figure, pivot, face)}."""
    up, _, uf = figs[RUN_UPPER]
    out = {}
    for n in RUNS:
        g, _, f = figs[n]
        dx, dy = uf[0] - f[0], uf[1] - f[1]                 # the frame moved so its face sits on the upper's
        split = uf[1] + RUN_SPLIT
        x0, y0 = min(0, dx), min(0, dy)
        x1, y1 = max(up.shape[1], g.shape[1] + dx), max(up.shape[0], g.shape[0] + dy)
        c = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
        top = up[:split]
        c[-y0:-y0 + top.shape[0], -x0:-x0 + top.shape[1]] = top
        low = g[max(0, split - dy):]
        ly, lx = max(split, dy) - y0, dx - x0
        m = low[..., 3] > 0
        c[ly:ly + low.shape[0], lx:lx + low.shape[1]][m] = low[m]
        ys, xs = np.nonzero(c[..., 3] > 0)
        face = (int(uf[0] - x0 - xs.min()), int(uf[1] - y0 - ys.min()))
        c = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        out[n] = (c, pivot_of(n, c, face), face)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    figs = {n: read(n) for n in names}
    if all(n in figs for n in RUNS):
        figs.update(one_upper(figs))
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
            path = os.path.join(a.sheet, f"mightymech_poses_{j}.png")
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

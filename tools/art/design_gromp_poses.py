#!/usr/bin/env python3
"""Gromp's Codex poses (assets/source/gromp/codex_poses: POSE_PROMPTS.md, 18 poses of its own TFT / Rift clips on its
design, 2026-11-01) at the design's body size, on the design's palette, gaps closed, the design's face on each.

    python tools/art/design_gromp_poses.py --fit                # each pose's body size by its face (printed)
    python tools/art/design_gromp_poses.py --sheet DIR          # all poses beside the design (4x), pivots marked
    python tools/art/design_gromp_poses.py                      # writes assets/source/gromp/hd/pose_<name>.png (+ .json)

Codex was asked the design at 7 px a square and drew every pose at a body of its own (its HANDOFF: the grid and the
body sizes not kept). BODY[name] is the raw px for one design square where the design's face matches the drawing best
(--fit scans BODY_SCAN, the face's match, the area estimate printed beside it), set by eye on the sheet. Each raw
drawing is read on squares of BODY px (raw_read: the commonest design colour round each square's centre), the
one-square cracks and small holes closed (design_silco_poses.close_gaps), loose specks dropped, and the design's upper
face (FACES: the brow, the crest and both yellow-green eyes; never the mouth, which the open-mouthed poses swing down)
pasted where it matches best with its eye on a yellow-green eye of the drawing, only where at least FACE_MIN of its
squares already match (the belching poses tip the head up: Codex's own face is kept there).
Each pose's json keeps its pivot (the root column, on the ground): the middle of its belly carried to the design's
(DESIGN_PIVOT is the design's root column; the belly is rigid, the mass middle drifts back as the hop's hind legs
stretch), PIVOT[name] where set by eye; the ground is the figure's lowest row.
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
import pack_gromp_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_gromp_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gromp", "codex_poses", "gromp-poses")
OUT = os.path.join(ROOT, "assets", "source", "gromp", "hd")
SPECK = 6
# the upper face of hd/idle.png (rows, columns; ends exclusive): the crest, the brow, both eyes - not the mouth
FACES = {"face": ((3, 15), (48, 80))}
FACE_MIN = 0.40
NO_FACE = {"d_down"}           # the eyes gone dark (POSE_PROMPTS): Codex's own heads, darkened
DARK_EYE = {"d_down"}
BODY_DEFAULT = 12.0
BODY_SCAN = np.arange(9.0, 15.01, 0.2)
WIN = 5                       # raw pixels round each design square's centre that vote
# BODY: the face's best fit where it holds (>= 75 %), then levelled by the belly (rigid but for the swells): its area
# against the design's (684 squares) taken back to the design's; run4's flattened belly half way; the swells kept
# (q_puff 1.44, r_belch 1.64 the biggest - Codex drew r_rear's bigger: read smaller, 1.52)
BODY = {"a_back": 10.4, "a_spit": 10.2, "q_puff": 10.2, "q_belch": 10.8, "e_back": 10.2, "e_spit": 10.5, "r_rear": 12.2,
        "r_belch": 10.4, "run1": 10.1, "run2": 9.9, "run3": 9.9, "run4": 8.4, "run5": 9.1, "run6": 9.85, "run7": 10.0,
        "run8": 9.9, "d_fall": 11.0, "d_down": 11.5}
DESIGN_PIVOT = 47             # hd/idle.png: pack_gromp_poses' root column 47.4
PIVOT = {"d_fall": 46, "d_down": 45}   # name -> pivot column where the belly does not tell (tipped over: the middle)


def cyan(px):
    """Its glowing yellow-green eyes (not the olive belly or the pale tusks); the name kept from the Murk Wolf's."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (g > 170) & (b < 90) & (g - b > 110) & (g > r)


NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"gromp-pose-{name}.png"))).convert("RGBA")).copy()


def raw_read(name, body=None, a=None):
    """Codex's raw drawing at the design's body, on the design's palette -> (figure, its own square size).
    Every design square takes the commonest design colour among the raw pixels round its centre (WIN x WIN, each
    snapped to the design's palette in Lab): a mean over Codex's squares mixes the fur with the outline."""
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    a = raw(name) if a is None else a
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    sq = RG.square_size(RG.profile(a, op, 1), xs.min(), xs.max())
    body = BODY.get(name, BODY_DEFAULT) if body is None else body
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


def face_patch(d, which):
    (r0, r1), (c0, c1) = FACES[which]
    patch = d[r0:r1, c0:c1]
    return patch, patch[..., 3] > 0, (c0, r0)


def find_face(g, d, which, taken=None):
    """Where the design's `which` face matches best (in Lab, within a few steps) with its eye on a cyan eye of the
    pose (at least half the eye's squares) -> (score share, x, y). `taken`: a box the other face already holds."""
    patch, pm, _ = face_patch(d, which)
    ph, pw = patch.shape[:2]
    eye = cyan(patch) & pm
    lab_g, lab_p = lab(g), lab(patch)
    gc = cyan(g) & (g[..., 3] > 0)
    best = (-1, 0, 0)
    for y in range(0, g.shape[0] - ph + 1):
        for x in range(0, g.shape[1] - pw + 1):
            if (gc[y:y + ph, x:x + pw] & eye).sum() * 2 < eye.sum():
                continue
            if taken is not None:
                tx, ty, tw, th = taken
                if abs((x + pw / 2) - (tx + tw / 2)) < pw * 0.5 and abs((y + ph / 2) - (ty + th / 2)) < ph * 0.5:
                    continue
            win = g[y:y + ph, x:x + pw]
            both = pm & (win[..., 3] > 0)
            dist = ((lab_g[y:y + ph, x:x + pw] - lab_p) ** 2).sum(-1)
            score = int((both & (dist < 400)).sum())
            if score > best[0]:
                best = (score, x, y)
    return max(best[0], 0) / pm.sum(), best[1], best[2]


def put_faces(g, d):
    """The face pasted where it matches (at least FACE_MIN) -> (pose, {which: offset}, {which: share})."""
    out, offs, shares = g.copy(), {}, {}
    for which in FACES:
        share, x, y = find_face(g, d, which)
        shares[which] = share
        patch, pm, (c0, r0) = face_patch(d, which)
        if share < FACE_MIN:
            continue
        win = out[y:y + patch.shape[0], x:x + patch.shape[1]]
        put = pm & (win[..., 3] > 0)
        win[put] = patch[put]
        offs[which] = (x - c0, y - r0)
    return out, offs, shares


def dark_eye(g, d):
    """The eyes gone out: every yellow-green square takes the design's darkest purple that is not the outline."""
    op = d[..., 3] > 0
    cols = np.unique(d[op][:, :3], axis=0)
    purple = cols[(cols[:, 2] > cols[:, 1]) & (cols[:, 0] > cols[:, 1]) & (cols.sum(1) > 120)]
    dark = purple[np.argmin(purple.sum(1))]
    out = g.copy()
    m = cyan(out) & (out[..., 3] > 0)
    out[m, :3] = dark
    return out


def belly(g):
    """Its belly's squares (olive): the rigid part, the same place on its body in every pose."""
    r, gg, b = (g[..., i].astype(int) for i in range(3))
    return (g[..., 3] > 0) & (r > 110) & (gg > 95) & (b < 110) & (abs(r - gg) < 35) & (r - b > 30)


def feet_mid(g):
    """The middle of its belly (its mean column): the hop's stretched hind legs would drag the mass middle back."""
    return float(np.nonzero(belly(g))[1].mean())


FEET_TO_PIVOT = None


def pivot_of(name, g):
    global FEET_TO_PIVOT
    if FEET_TO_PIVOT is None:
        FEET_TO_PIVOT = feet_mid(design()) - DESIGN_PIVOT
    if name in PIVOT:
        return PIVOT[name], g.shape[0]
    return int(round(feet_mid(g) - FEET_TO_PIVOT)), g.shape[0]


def read(name):
    d = design()
    g, sq = raw_read(name)
    g = close_gaps(g, d)
    if name in NO_FACE:
        offs, shares = {}, {}
    else:
        g, offs, shares = put_faces(g, d)
    if name in DARK_EYE:
        g = dark_eye(g, d)
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    faces = {k: (int(v[0] - xs.min()), int(v[1] - ys.min())) for k, v in offs.items()}
    print(f"{name:9s} squares {sq:.1f} px -> body {BODY.get(name, BODY_DEFAULT)}: {g.shape[1]}x{g.shape[0]}, faces "
          + ", ".join(f"{k} {shares.get(k, 0):.0%}{'' if k in offs else ' (kept)'}" for k in FACES))
    return g, pivot_of(name, g), faces


def fit(names):
    """Each pose's body size: the faces' summed match over BODY_SCAN (and the area estimate)."""
    d = design()
    area = (d[..., 3] > 0).sum()
    for name in names:
        a = raw(name)
        est = np.sqrt((a[..., 3] >= 128).sum() / area)
        rows = []
        for body in BODY_SCAN:
            g, _ = raw_read(name, body, a)
            g = close_gaps(g, d)
            s = [find_face(g, d, w)[0] for w in FACES]
            rows.append((sum(s), body, s))
        best = max(rows)
        print(f"{name:9s} area {est:.2f}  best {best[1]:.1f} (face {best[2][0]:.0%})  "
              + " ".join(f"{b:.1f}:{t:.2f}" for t, b, _ in rows))


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    if a.fit:
        fit(names)
        return
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
            path = os.path.join(a.sheet, f"gromp_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv, faces) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]], "faces": {k: list(v) for k, v in faces.items()}}, fh)


if __name__ == "__main__":
    main()

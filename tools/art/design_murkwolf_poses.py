#!/usr/bin/env python3
"""Murk Wolf's Codex poses (assets/source/murkwolf/codex_poses: POSE_PROMPTS.md, 19 poses of its own TFT clips on its
design, 2026-11-01) at the design's body size, on the design's palette, gaps closed, the design's two faces on each.

    python tools/art/design_murkwolf_poses.py --fit                # each pose's body size by its faces (printed)
    python tools/art/design_murkwolf_poses.py --sheet DIR          # all poses beside the design (4x), pivots marked
    python tools/art/design_murkwolf_poses.py                      # writes assets/source/murkwolf/hd/pose_<name>.png (+ .json)

Codex was asked the design at 10 px a square and drew every pose at a body of its own: 11-14 raw px for one design
square. BODY[name] is the size where the design's two faces match the drawing best (--fit scans BODY_SCAN, the faces'
summed match, the area estimate printed beside it), set by eye on the sheet where the heads are turned. Each raw
drawing is read on squares of BODY px (raw_read: the commonest design colour round each square's centre), the
one-square cracks and small holes closed (design_silco_poses.close_gaps), loose specks dropped, and each of the
design's two upper faces (FACES: the ears, the brow and the cyan eye of the near head and of the far head; never the
jaws, which the open-mouthed poses swing down) pasted where it matches best with its eye on a cyan eye of the drawing
(the user's rule: one face in every frame), only where at least FACE_MIN of its squares already match - each head on
its own, so heads Codex moved apart (the leap, the howl, the fall) still get theirs.
Each pose's json keeps its pivot (the root column, on the ground): the middle of its mass (its squares' mean column)
carried to the design's (DESIGN_PIVOT is the design's root column, FEET_TO_PIVOT the design's own mass middle less it;
its planted hind foot moved the stretched poses - the rend, the growl, the fall - far back), PIVOT[name] where set by
eye; the ground is the figure's lowest row.
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
import pack_murkwolf_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_murkwolf_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "murkwolf", "codex_poses", "murkwolf-poses")
OUT = os.path.join(ROOT, "assets", "source", "murkwolf", "hd")
SPECK = 6
# the two upper faces of hd/idle.png (rows, columns; ends exclusive): the ears, the brow, the cyan eye - not the jaws
FACES = {"near": ((19, 36), (40, 62)), "far": ((18, 34), (62, 82))}
FACE_MIN = 0.40
NO_FACE = {"d_down"}           # the eyes gone dark (POSE_PROMPTS): Codex's own heads, darkened
DARK_EYE = {"d_down"}
BODY_DEFAULT = 12.0
BODY_SCAN = np.arange(10.0, 15.01, 0.2)
WIN = 5                       # raw pixels round each design square's centre that vote
BODY = {"a_back": 12.0, "a_bite": 12.8, "q_crouch": 12.1, "q_leap": 12.7, "q_rend": 11.8, "e_gather": 10.9,
        "e_howl": 11.6, "r_growl": 10.8, "r_bark": 13.1, "run1": 10.9, "run2": 12.5, "run3": 11.6, "run4": 11.2,
        "run5": 11.2, "run6": 12.3, "run7": 11.9, "run8": 11.5, "d_fall": 13.6, "d_down": 10.3}
DESIGN_PIVOT = 36             # hd/idle.png: pack_murkwolf_poses' root column 36.5
PIVOT = {}                    # name -> pivot column in the read pose where its feet do not tell


def cyan(px):
    """Its glowing cyan eyes (not the pale blue fur or the white ruff)."""
    r, g, b = px[..., 0].astype(int), px[..., 1].astype(int), px[..., 2].astype(int)
    return (b > 190) & (g > 170) & (r < 140) & (b - r > 90)


NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"murkwolf-pose-{name}.png"))).convert("RGBA")).copy()


# the design's eyes (hd/idle.png rows 30-32, columns 67-69 and rows 33-34, columns 50-51): C cyan, W the glint, K the dark
# round it (only on squares the figure already covers)
EYE_BIG = ("CCK", "CWC", "KCK")
EYE_MID = ("CW", "CC")
EYE_SMALL, EYE_LARGE = 120, 350     # raw px of a cyan blob: smaller ones are specks, larger ones get EYE_BIG


def eye_colours(d):
    return {"C": d[33, 50, :3], "W": d[31, 68, :3], "K": d[30, 66, :3]}


def stamp_eyes(out, a, body, x0, y1, d):
    """Every cyan blob of the raw drawing stamped back as one of the design's eyes, centred on it."""
    m = cyan(a) & (a[..., 3] >= 128)
    lb, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    cols = eye_colours(d)
    nh = out.shape[0]
    for j in range(1, n + 1):
        ys, xs = np.nonzero(lb == j)
        if len(ys) < EYE_SMALL:
            continue
        shape = EYE_BIG if len(ys) >= EYE_LARGE else EYE_MID
        ci = (xs.mean() - x0) / body - 0.5
        cj = nh - 0.5 - (y1 - ys.mean()) / body
        top, left = round(cj - (len(shape) - 1) / 2), round(ci - (len(shape[0]) - 1) / 2)
        for dy, row in enumerate(shape):
            for dx, c in enumerate(row):
                y, x = top + dy, left + dx
                if not (0 <= y < nh and 0 <= x < out.shape[1]):
                    continue
                if c == "K" and out[y, x, 3] == 0:
                    continue
                out[y, x, :3] = cols[c]
                out[y, x, 3] = 255
    return out


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
    return stamp_eyes(out, a, body, x0, y1, d), sq


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
    """Both faces pasted where they match (each at least FACE_MIN) -> (pose, {which: offset}, {which: share})."""
    out, offs, shares, taken = g.copy(), {}, {}, None
    for which in ("near", "far"):
        share, x, y = find_face(g, d, which, taken)
        shares[which] = share
        patch, pm, (c0, r0) = face_patch(d, which)
        if share < FACE_MIN:
            continue
        win = out[y:y + patch.shape[0], x:x + patch.shape[1]]
        put = pm & (win[..., 3] > 0)
        win[put] = patch[put]
        offs[which] = (x - c0, y - r0)
        taken = (x, y, patch.shape[1], patch.shape[0])
    return out, offs, shares


def dark_eye(g, d):
    """The eyes gone out: every cyan square takes the design's darkest slate that is not the outline."""
    op = d[..., 3] > 0
    cols = np.unique(d[op][:, :3], axis=0)
    slate = cols[(cols[:, 2] > cols[:, 0]) & (cols.sum(1) > 150) & ~cyan(cols[None])[0]]
    dark = slate[np.argmin(slate.sum(1))]
    out = g.copy()
    m = cyan(out) & (out[..., 3] > 0)
    out[m, :3] = dark
    return out


def feet_mid(g):
    """The middle of its mass: its squares' mean column."""
    return float(np.nonzero(g[..., 3] > 0)[1].mean())


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
          + ", ".join(f"{k} {shares.get(k, 0):.0%}{'' if k in offs else ' (kept)'}" for k in ("near", "far")))
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
            s = [find_face(g, d, w)[0] for w in ("near", "far")]
            rows.append((s[0] + s[1], body, s))
        best = max(rows)
        print(f"{name:9s} area {est:.2f}  best {best[1]:.1f} (near {best[2][0]:.0%} far {best[2][1]:.0%})  "
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
            path = os.path.join(a.sheet, f"murkwolf_poses_{j}.png")
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

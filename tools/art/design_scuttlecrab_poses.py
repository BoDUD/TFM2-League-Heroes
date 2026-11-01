#!/usr/bin/env python3
"""The Scuttle Crab's Codex poses (assets/source/scuttlecrab/codex_poses: POSE_PROMPTS.md, 20 poses of League's crab
clips on its design, 2026-11-01) at the design's body size, on the design's palette, gaps closed, the design's face on
each.

    python tools/art/design_scuttlecrab_poses.py --sheet DIR      # all poses beside the design (4x), pivots marked
    python tools/art/design_scuttlecrab_poses.py                  # writes assets/source/scuttlecrab/hd/pose_<name>.png (+ .json)

Codex was asked the design at 8 px a square and drew each pose a different size (7.2-9.3 raw px a design square). Its
exported scuttle-pose-<name>.png are its raw drawings only shifted (soles on y 1100) and thresholded, the colours untouched
(HANDOFF.md), so they are read. BODY[name] raw px is the design's square, measured two ways and averaged
(codex-fit-shrinks-bodies): the figure's area against the design's (sqrt) and the grey stone face plate's against the
design's; the shell poses (e_shell, d_down: no face, nothing but the shell) by the shell's width against the idle's shell.
Each drawing is read on squares of BODY px (raw_read: the commonest design colour round each square's centre), the
one-square cracks and small holes closed (design_silco_poses.close_gaps), loose specks dropped, and the design's own face
(FACE_ROWS / FACE_COLS of hd/idle.png: the stone face plate; the shell round it and the eyes on their stalks stay the
pose's own) pasted
where it matches best (the user's rule: one face in every frame), only where at least FACE_MIN of its squares already
match and the grey of the pose's own face plate lies under the patch's.
Each pose's json keeps its pivot (between its legs, on the ground): the design's pivot column DESIGN_PIVOT carried by
where the face landed, PIVOT[name] where the face does not tell (the shell poses); the ground is the figure's lowest row.
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
import pack_scuttlecrab_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_scuttlecrab_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import snap, lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "scuttlecrab", "codex_poses", "scuttle-poses")
OUT = os.path.join(ROOT, "assets", "source", "scuttlecrab", "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the stone face plate, rows / columns of hd/idle.png; only
# the plate's grey and the outline touching it are pasted (not the shell round it, not the eyes: face_mask)
FACE_ROWS, FACE_COLS = (20, 70), (54, 108)
FACE_MIN = 0.38
NO_FACE = {"e_shell", "d_down"}   # pulled into the shell (POSE_PROMPTS): no face to paste
WIN = 5                       # raw pixels round each design square's centre that vote
BODY_DEFAULT = 7.7
BODY = {"a_rise": 7.2, "a_hop": 8.6, "a_stomp": 7.7, "q_raise": 8.25, "q_call": 7.3, "e_tuck": 7.65, "e_shell": 9.0,
        "e_pop": 9.3, "r_up1": 7.4, "r_up2": 7.5, "r_up3": 7.55,
        "run1": 8.15, "run2": 7.5, "run3": 7.8, "run4": 7.65, "run5": 7.5, "run6": 7.55, "run7": 7.65, "run8": 7.4,
        "d_down": 9.0}
DESIGN_PIVOT = 57             # hd/idle.png: the root between its legs (pack_scuttlecrab_poses' pelvis column)
PIVOT = {}                    # name -> pivot column in the read pose where the face does not carry it
FACE_NEAR = {}
NEAR = 4
NEAR_MIN = 0.2
DARK_EYE = set()


def grey(px):
    """The stone face plate's greys (low saturation, bright)."""
    rgb = px[..., :3].astype(int)
    return (px[..., 3] > 0) & (rgb.max(-1) - rgb.min(-1) < 28) & (rgb.max(-1) > 95)


def face_mask(patch):
    """What of FACE_BOX is pasted: the stone plate's grey with the outline squares touching it. The eyes stay the pose's
    own: Codex draws them on its own stalks, often higher than the design's, and a pasted pair beside them read as four
    eyes (run6, run8, r_up1)."""
    return ndimage.binary_dilation(grey(patch), np.ones((3, 3), bool)) & (patch[..., 3] > 0)


def lone_lime(g, most=3):
    """Lime crumbs (blobs of at most `most` squares of the eyes' and plate edges' lime-yellow) take the commonest colour
    round them: halves of Codex's eyes left beside the read eye (run8, r_up1, a_stomp)."""
    rgb = g[..., :3].astype(int)
    lime = (g[..., 3] > 0) & (rgb[..., 0] > 150) & (rgb[..., 1] > 180) & (rgb[..., 2] < 120)
    lb, n = ndimage.label(lime, structure=np.ones((3, 3), bool))
    for j in range(1, n + 1):
        m = lb == j
        if m.sum() > most:
            continue
        ring = ndimage.binary_dilation(m, np.ones((3, 3), bool)) & ~m & (g[..., 3] > 0)
        if ring.any():
            cols, cnt = np.unique(g[ring], axis=0, return_counts=True)
            g[m] = cols[cnt.argmax()]
    return g


def put_face(g, d, near=None):
    """The design's face pasted where most of its squares already match (in Lab, within a few steps) AND its grey plate
    lands on the pose's own plate (at least half the patch's grey squares grey). -> (pose, offset, match share)."""
    (r0, r1), (c0, c1) = FACE_ROWS, FACE_COLS
    patch = d[r0:r1, c0:c1]
    pm = face_mask(patch)
    ph, pw = patch.shape[:2]
    plate = grey(patch)
    lab_g, lab_p = lab(g), lab(patch)
    best = (-1, 0, 0)
    for y in range(-ph // 3, g.shape[0] - ph + ph // 3 + 1):     # the plate may run off an edge (r_up1: under the ground)
        for x in range(-pw // 3, g.shape[1] - pw + pw // 3 + 1):
            if near and (abs(x - near[0]) > NEAR or abs(y - near[1]) > NEAR):
                continue
            ys0, xs0 = max(0, y), max(0, x)
            win = g[ys0:y + ph, xs0:x + pw]
            sl = (slice(ys0 - y, ys0 - y + win.shape[0]), slice(xs0 - x, xs0 - x + win.shape[1]))
            if (grey(win) & plate[sl]).sum() * 2 < plate.sum():
                continue
            both = pm[sl] & (win[..., 3] > 0)
            dist = ((lab_g[ys0:y + ph, xs0:x + pw] - lab_p[sl]) ** 2).sum(-1)
            score = int((both & (dist < 400)).sum())
            if score > best[0]:
                best = (score, x, y)
    score, x, y = best
    if score < (NEAR_MIN if near else FACE_MIN) * pm.sum():   # the face turned away: Codex's own face stays
        return g, None, max(score, 0) / pm.sum()
    out = g.copy()
    ys0, xs0 = max(0, y), max(0, x)
    win = out[ys0:y + ph, xs0:x + pw]
    sl = (slice(ys0 - y, ys0 - y + win.shape[0]), slice(xs0 - x, xs0 - x + win.shape[1]))
    put = pm[sl] & (win[..., 3] > 0)
    win[put] = patch[sl][put]
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
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"scuttle-pose-{name}.png"))).convert("RGBA")).copy()
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
    """Between its legs: the design's pivot carried by the face, else PIVOT[name], else the figure's middle."""
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
    g = lone_lime(g)
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
            path = os.path.join(a.sheet, f"scuttle_poses_{j}.png")
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

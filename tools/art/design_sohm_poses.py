#!/usr/bin/env python3
"""Sohm's Codex poses (assets/source/sohm/codex_poses: POSE_PROMPTS.md, 11 key poses and 4 swim frames of her own TFT
clips on her design, 2026-10-30) at the design's body size, on the design's palette, gaps closed, the design's face
on each where the head is not turned.

    python tools/art/design_sohm_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_sohm_poses.py                  # writes assets/source/sohm/hd/pose_<name>.png (+ .json)

Codex drew every pose on squares of its own size (8 px for most, 10 for e_push, 9 for r_rise, 7 / 6 for the swim) but
with the design's count of squares to the body: read on its own squares (regrid), each raw drawing comes out at the
design's body (the antlers and the crown 0.91 - 1.05 of the design's area, 2026-10-30). Codex's own cut
(sohm-pose-<name>.png) put them all on 8 px, so the bodies drawn on bigger or smaller squares came out bigger or
smaller: not used. Then the colours are snapped to the design's own (nearest in Lab), the one-square cracks and small
holes closed (design_silco_poses.close_gaps), loose specks dropped, and the design's own face (the ear, the crown and
gem, the eye, the snout) pasted where it matches best (the user's rule: one face in every frame; FACE_*), only where
at least FACE_MIN of its squares already match (a head turned up or down keeps Codex's).
HEAD_AT: a_rear's head was drawn smaller, e_push's bigger, r_swirl's and d_fall's antlers swept back a third longer:
on those the design's whole head is laid over Codex's (put_head); a_spit's and q_send's open mouths, r_rise's head
thrown up and d_down's lying head stay Codex's.
Each pose's json keeps where her neck root column and the ground fall in it (pivot) and where the face went: the pack
put the design's column 0 on canvas column DESIGN_X and every reference's neck root on the design's, and Codex drew
over the reference in place, so the design's column PIVOT_COL is canvas column DESIGN_X + PIVOT_COL * 8 in every raw
drawing; the ground is its lowest row.
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
import pack_sohm_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_sohm_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sohm", "codex_poses", "sohm-poses")
OUT = os.path.join(ROOT, "assets", "source", "sohm", "hd")
DESIGN_X = 392                # the pack's design on the canvas: (1254 - 58 * 8) // 2 rounded down to the 8 px grid
PIVOT_COL = 29                # the design's middle column: the pivot every pose keeps
SPECK = 6                     # parts apart from the figure smaller than this are dropped
# the face (the user's rule: the idle's face in every frame): the ear, the crown's foot and the gem, the eye, the snout -
# rows / columns of hd/idle.png, pasted on each pose where it matches best (searched over the whole pose)
FACE_ROWS, FACE_COLS = (18, 38), (32, 58)
FACE_MIN = 0.45
# the design's whole head, laid on the poses whose heads were drawn another size (a_rear's smaller, e_push's bigger) or
# with other antlers (r_swirl's and d_fall's swept back a third longer): offset design -> pose of its gem's top square
# (r_swirl's by the eye: its head was drawn turned to the front, the gem long)
HEAD_ROWS, HEAD_COLS = (0, 40), (22, 58)
HEAD_CLEAR = 36               # design rows above this in the head's columns hold only the design's squares
HEAD_FRONT = 8                # ... and so many columns in front of its snout
HEAD_AT = {"a_rear": (-3, -5), "e_push": (5, -1), "d_fall": (29, 7), "r_swirl": (15, 17)}
# more of Codex's head to clear, boxes (x0, y0, x1, y1) in the design's squares: e_push's bigger lower jaw under the
# design's snout (r_swirl's too: its head was drawn turned to the front); r_swirl's mane flung up in a ribbon over her head (everything above the antlers' tips)
HEAD_CUT = {"e_push": [(47, 36, 70, 43)], "r_swirl": [(-40, -40, 80, 0), (46, 36, 70, 44)]}
NAMES = list(PK.POSES)


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


def coral(a):
    """The antlers' and the crown's squares: the design's warm colours (coral, gold, brown) and its pale gold - none of
    them anywhere but on her head."""
    c = a[..., :3].astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    warm = (r >= 60) & (r > g + 20) & (r > b + 30)
    pale_gold = (r > 230) & (g > 210) & (b < 170)
    return (a[..., 3] > 0) & (warm | pale_gold)


def lab(a):
    return PD._lab(a[..., :3].reshape(-1, 3).astype(float)).reshape(a.shape[0], a.shape[1], 3)


def put_face(g, d):
    """The design's face pasted on the pose at the offset where most of its squares already match (in Lab, within a
    few steps), searched over the whole pose; only on the pose's own squares. -> (pose, offset, match share)."""
    (r0, r1), (c0, c1) = FACE_ROWS, FACE_COLS
    patch = d[r0:r1, c0:c1]
    pm = patch[..., 3] > 0
    ph, pw = patch.shape[:2]
    lab_g, lab_p = lab(g), lab(patch)
    best = (-1, 0, 0)
    for y in range(-ph // 2, g.shape[0] - ph // 2):
        for x in range(-pw // 2, g.shape[1] - pw // 2):
            ya, xa = max(0, y), max(0, x)
            yb, xb = min(g.shape[0], y + ph), min(g.shape[1], x + pw)
            win = g[ya:yb, xa:xb]
            sub = (slice(ya - y, yb - y), slice(xa - x, xb - x))
            both = pm[sub] & (win[..., 3] > 0)
            dist = ((lab_g[ya:yb, xa:xb] - lab_p[sub]) ** 2).sum(-1)
            score = int((both & (dist < 400)).sum())
            if score > best[0]:
                best = (score, x, y)
    score, x, y = best
    if score < FACE_MIN * pm.sum():   # the head turned: Codex's own face stays
        return g, None, score / pm.sum()
    out = np.pad(g, ((ph, ph), (pw, pw), (0, 0)))
    win = out[y + ph:y + 2 * ph, x + pw:x + 2 * pw]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out[ph:-ph, pw:-pw], (x - c0, y - r0), score / pm.sum()


def put_head(g, d, off, boxes=()):
    """The design's whole head (HEAD_ROWS / HEAD_COLS of hd/idle.png: the antlers, the crown and gem, the ear, the
    eye, the snout, the mane's top behind them) laid on at `off` (design -> pose) over Codex's own: Codex's squares
    in the head's rows where the design has none (its own antlers and snout drawn longer or shorter) and its coral
    antler squares above the face anywhere are cleared first; clear squares left inside the figure take their
    neighbours' colour, the new edges the outline. -> (pose, shift of its top-left)."""
    (r0, r1), (c0, c1) = HEAD_ROWS, HEAD_COLS
    pad = 24
    out = np.pad(g, ((pad, pad), (pad, pad), (0, 0)))
    before = out[..., 3] > 0
    y, x = r0 + off[1] + pad, c0 + off[0] + pad
    patch = d[r0:r1, c0:c1]
    pm = patch[..., 3] > 0
    zone = np.zeros(out.shape[:2], bool)       # the head's rows: only the design's squares stay
    zone[y:y + HEAD_CLEAR - r0, x:x + (c1 - c0) + HEAD_FRONT] = True
    zone[y + HEAD_CLEAR - r0:] = False
    for bx0, by0, bx1, by1 in boxes:
        zone[max(0, by0 + off[1] + pad):by1 + off[1] + pad, max(0, bx0 + off[0] + pad):bx1 + off[0] + pad] = True
    zone[y:y + (r1 - r0), x:x + (c1 - c0)] &= ~pm
    head = np.zeros_like(zone)                 # Codex's antlers and crown outside the design's head go
    head[y:y + (r1 - r0), x:x + (c1 - c0)] = True
    cut = (zone | (coral(out) & ~head)) & before
    out[cut] = 0
    ink = tuple(PD.edge_colour(d))[:3] + (255,)
    dark = lambda a: (a[..., 3] > 0) & (a[..., :3].astype(int).sum(-1) < 60)  # noqa: E731
    while True:   # the outline the cut left hanging: dark squares that no longer touch a coloured one
        op = out[..., 3] > 0
        col = op & ~dark(out)
        lone = dark(out) & ~ndimage.binary_dilation(col, structure=np.ones((3, 3), bool)) & cut.any()
        lone &= ndimage.binary_dilation(cut, iterations=3)
        if not lone.any():
            break
        cut |= lone
        out[lone] = 0
    win = out[y:y + (r1 - r0), x:x + (c1 - c0)]
    win[pm] = patch[pm]
    op = out[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    if n > 1:
        sizes = ndimage.sum(op, lb, range(1, n + 1))
        out[(lb != 1 + int(np.argmax(sizes))) & (lb > 0)] = 0
    # holes the cut left inside the figure: the neighbours' most common colour, from the edges in
    op = out[..., 3] > 0
    hole = ndimage.binary_fill_holes(op) & ~op & cut
    while hole.any():
        done = False
        for yy, xx in zip(*np.nonzero(hole)):
            nb = out[max(0, yy - 1):yy + 2, max(0, xx - 1):xx + 2].reshape(-1, 4)
            nb = [tuple(c) for c in nb if c[3] > 0]
            if len(nb) >= 3:
                out[yy, xx] = max(set(nb), key=nb.count)
                hole[yy, xx] = False
                done = True
        if not done:
            break
    # the cut's new edges: an outline square outside every light square that now meets the clear
    op = out[..., 3] > 0
    c = out[..., :3].astype(int).sum(-1)
    light = op & (c > 120)
    near = ndimage.binary_dilation(cut, iterations=2)
    grow = ndimage.binary_dilation(light, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)) & ~op & near
    out[grow] = ink
    ys, xs = np.nonzero(out[..., 3] > 0)
    shift = (xs.min() - pad, ys.min() - pad)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1], shift


def raw_read(name):
    """Codex's raw drawing read on its own squares, on the design's palette -> (figure, pivot (x, y) in it: x the
    design's PIVOT_COL, y the ground under the lowest row)."""
    d = design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"sohm-pose-{name}.png"))).convert("RGBA")).copy()
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    sq = RG.square_size(RG.profile(a, op, 1), xs.min(), xs.max())
    g, _, (bx, _) = RG.regrid(a, sq)
    gy, gx = np.nonzero(g[..., 3] >= 128)
    px = DESIGN_X + PIVOT_COL * 8 + 4
    i = max(0, np.searchsorted(bx, px) - 1)
    col = i + (px - bx[i]) / sq
    g = g[gy.min():gy.max() + 1, gx.min():gx.max() + 1].copy()
    g[..., 3] = np.where(g[..., 3] >= 128, 255, 0)
    return snap(g, d), (col - gx.min(), g.shape[0]), sq


def read(name):
    """The pose at the design's body size, on the design's palette, with the design's face -> (figure, the pivot's
    square in it, the face's offset)."""
    d = design()
    g, root, sq = raw_read(name)
    g = close_gaps(g, d)
    if name in HEAD_AT:
        g, (sx, sy) = put_head(g, d, HEAD_AT[name], HEAD_CUT.get(name, ()))
        root = (root[0] - sx, root[1] - sy)
        off, share = (int(HEAD_AT[name][0] - sx), int(HEAD_AT[name][1] - sy)), 1.0
    else:
        g, off, share = put_face(g, d)
    print(f"{name:9s} squares {sq:.1f} px: face at {off}, {share:.0%} of its squares matched before")
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    face = None if off is None else (int(off[0] - xs.min()), int(off[1] - ys.min()))
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
    figs = {n: read(n) for n in names}
    for n, (fig, piv, _) in figs.items():
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, pivot at {piv}")
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
                sheet.alpha_composite(big4(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"sohm_poses_{j}.png")
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

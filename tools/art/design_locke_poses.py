#!/usr/bin/env python3
"""Locke's Codex poses (assets/source/locke/codex_poses/locke-poses: POSE_PROMPTS.md, 16 key poses of his League clips
on his design, 2026-10-26) read back at the design's scale, in its colours, with the design's own head
(design_trundle_poses.py's way).

    python tools/art/design_locke_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_locke_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_locke_poses.py                  # writes assets/source/locke/hd/pose_<name>.png (+ .json)
    python tools/art/design_locke_poses.py --rematch        # the same, the heads searched again (else the json's)

His poses copy the design's head, so the head gives the scale: the head box (pack_locke_poses.HEAD: the hair, the
glasses and the face, hd/idle.png rows 0-25, columns 19-46) is matched against the picture (design_shyvana_poses.
match_head), the pose read on the delivery's 11 px grid (one square = one pixel of the design: the pack's PX), every
colour snapped to the design's own (Lab), the design's head pasted square for square on Codex's head's place (the
polygon POLY grown by a square above the collar: one face in all frames - Codex redrew the head, not copied it), the
outline closed. Each pose's json keeps where the head box went (its top-left square), for rig_locke to place the pose.
Codex's 1254 exports are on the pack's grid with hard alpha (its QA: grid_11_pass), their pixel_1x/ folder came empty:
the squares are read at each cell's middle. Poses whose head came out off the design's scale (SCALE) are read from
raw/ on the head's own squares instead.
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
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_shyvana_poses import match_head, sample_grid  # noqa: E402
from design_riven import pick  # noqa: E402
from design_locke_hd import lp  # noqa: E402
import pack_locke_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "locke", "codex_poses", "locke-poses")
OUT = os.path.join(ROOT, "assets", "source", "locke", "hd")
# the hair, the glasses and the face to the chin - not the coat's collar under them (rows 22 on, on the image left)
POLY = [(31.0, 0.0), (40.0, 0.0), (42.0, 2.0), (44.0, 5.0), (45.0, 9.0), (47.0, 12.0), (48.0, 17.0), (46.0, 21.0),
        (43.0, 24.0), (37.0, 25.0), (33.0, 24.0), (30.0, 22.0), (19.0, 22.0), (16.5, 18.0), (16.5, 12.0), (19.0, 9.0),
        (22.0, 6.0), (25.0, 2.0), (29.0, 1.0)]
GROW_ROWS = 22                                   # the polygon grows by a square (its outline) above this row only
SCALES = np.arange(9.0, 13.01, 0.25)            # Codex drew some heads smaller than the design's (9-9.5 px a square)
TILTED = {}
RAW = {}                                         # pose -> scales: read from raw/ on the head's own squares
# Codex drew the bodies bigger than the design has them round the design's head (legs, coat and case ~14% longer:
# run4's head matches at 11 px a square, its body is 98 rows to the design's 88): every pose is read on squares of BODY
# px of the 11 px export (shrink(): whole-line cuts spread evenly, the head's middle followed), so the body is the
# design's size, and the design's head is pasted on it - checked side by side with the design at 12 / 12.5 / 13
# (C:/t/lk_work/scale). r_throw Codex had already shrunk (its case 39 squares long at 11 px, the design's 38).
BODY_PX = 12.5
BODY = {"r_throw": 11.0}
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
CACHE = "C:/t/lk_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    """The picture the head is matched on: the 11 px export, or Codex's raw draft for the RAW poses."""
    sub = "raw" if name in RAW else ""
    return np.asarray(Image.open(lp(os.path.join(SRC, sub, f"locke-pose-{name}.png"))).convert("RGBA"))


def head_box(d):
    r0, r1, c0, c1 = PK.HEAD
    return d[r0:r1, c0:c1]


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    m = np.asarray(img) > 0
    grown = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool))
    grown[GROW_ROWS:] = m[GROW_ROWS:]
    return grown & (d[..., 3] > 0)


def on_grid(a):
    """The export's squares: each 11 px cell's middle pixel (the grid from the canvas corner), alpha 0 / 255."""
    h = PK.PX // 2
    g = a[h::PK.PX, h::PK.PX].copy()
    g[..., 3] = np.where(g[..., 3] >= 128, 255, 0)
    g[g[..., 3] == 0] = 0
    return g


def finish(fig):
    """The outline closed; single enclosed holes the read-back left take the outline."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lb == j
        if h.sum() <= 1:
            pad[h] = (*ink, 255)
    return pad


def matched(name, again=False):
    """match_head's (px a square, x, y, cost, tilt) for a pose, kept in hd/pose_<name>.json ("match") once found."""
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    if not again and os.path.isfile(CACHE):
        c = json.load(open(CACHE, encoding="utf-8"))
        if name in c:
            return tuple(c[name])
    m = match_head(raw(name), head_box(design()), scales=RAW.get(name, SCALES), angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def is_hair(rgb):
    """His blond hair's colours on an (..., 3) array (the design's golds 99702b ccac49 f9ec83 fbf39d: red and green
    within 41 of each other) - not his skin (fbc692 ec9b65 dd8451 c38e68: red 53 or more above green), which a looser
    test took for hair and painted over a hand raised by his head (d_fall's forearm came out black)."""
    rgb = rgb.astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (r > 140) & (g > 100) & (r - g < 45) & (b < g - 30)


def clear_leftovers(fig, pasted, box):
    """Codex's own hair left round the pasted head (where it drew the head bigger or elsewhere): every hair-coloured
    square in `box` (rows / columns, the head box grown) that the paste did not lay takes the most common colour round
    it that is not hair (the collar, the coat, the case), or goes clear where most round it is clear; repeated until
    none is left."""
    y0, y1, x0, x1 = box
    for _ in range(12):
        op = fig[..., 3] > 0
        left = np.zeros(op.shape, bool)
        left[y0:y1, x0:x1] = True
        left &= op & ~pasted & is_hair(fig[..., :3])
        if not left.any():
            return fig
        out = fig.copy()
        for y, x in zip(*np.nonzero(left)):
            nb = fig[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
            clear = int((nb[:, 3] == 0).sum())
            keep = [tuple(c) for c in nb if c[3] > 0 and not is_hair(c[None, :3])[0]]
            if clear >= 5 or not keep:
                if clear >= 3:
                    out[y, x] = 0
                continue
            out[y, x] = max(set(keep), key=keep.count)
        fig = out
    return fig


def shrink(a, k, mid):
    """`a` brought to k of its rows and columns by whole-line cuts spread evenly (design_riven.pick: in each stretch the
    line most like its neighbour goes) - no resampling, so a 1-square outline stays one square and a small hand or nail
    is not swallowed by the outline the way pixel_down.pixelate's edge rule did (d_fall's raised hand came out black).
    -> (the smaller picture, where `mid` (column, row) lands in it)."""
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    cols = sorted({tuple(int(v) for v in p[:3]) for p in a[op]})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full((H, W), -1, int)
    for y, x in zip(*np.nonzero(op)):
        idx[y, x] = lut[tuple(int(v) for v in a[y, x, :3])]

    def keep(lines, n):
        best = None
        for off in range(3):
            got, lost = pick(lines, n, off)
            if got is not None and (best is None or lost < best[1]):
                best = (got, lost)
        return best[0]

    rows = keep([idx[y] for y in range(H)], round(H * k))
    sub = idx[rows]
    kc = keep([sub[:, x] for x in range(W)], round(W * k))
    small = sub[:, kc]
    out = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    out[m, :3] = np.array(cols, np.uint8)[small[m]]
    out[m, 3] = 255
    return out, (float(np.interp(mid[0], kc, range(len(kc)))), float(np.interp(mid[1], rows, range(len(rows)))))


def read(name, match, body=None):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt). `body`: px of the export a square (BODY's by default)."""
    d = design()
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = PK.HEAD
    hw, hh = c1 - c0, r1 - r0
    if name in RAW:                                    # on the head's own squares, the grid laid round the head box
        a, (ci, cj) = sample_grid(raw(name), s, hx, hy)
    else:
        sb = body or BODY.get(name, BODY_PX)
        a = on_grid(raw(name))
        mid = ((hx + hw * s / 2) / PK.PX, (hy + hh * s / 2) / PK.PX)   # Codex's head middle, in the export's squares
        if sb > PK.PX + 0.01:                          # the body brought to the design's size round the head's middle
            a, mid = shrink(a, PK.PX / sb, mid)
        ci, cj = int(round(mid[0] - hw / 2)), int(round(mid[1] - hh / 2))
        s = sb
    fig = snap(a, d)
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if not ang:                                        # a tipped head keeps Codex's own (the design's is upright)
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
        pasted = np.zeros(big_.shape[:2], bool)
        pasted[ys - r0 + cj + pad, xs - c0 + ci + pad] = True
        gy, gx = cj + pad, ci + pad
        big_ = clear_leftovers(big_, pasted, (max(0, gy - 6), gy + (r1 - r0) + 4, max(0, gx - 6), gx + (c1 - c0) + 6))
    big_ = finish(big_)
    # specks the read-back left apart from the figure (w_spread, r_throw: one square each); a part of its own as big as
    # d_fall's flying nail (48 squares) stays
    op = big_[..., 3] > 0
    lb, k = ndimage.label(op, structure=np.ones((3, 3), bool))
    for j in range(1, k + 1):
        if (lb == j).sum() < SPECK:
            big_[lb == j] = 0
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), float(s), cost, ang


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--rematch", action="store_true", help="search the heads again (else the json's)")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    if a.measure:
        d = design()
        for n in names:
            r = raw(n)
            s, x, y, cost, ang = match_head(r, head_box(d), scales=np.arange(9.0, 13.01, 0.25), angles=(0,))
            s0, x0, y0, cost0, _ = match_head(r, head_box(d), scales=SCALES, angles=(0,))
            print(f"{n:9s} best {s:5.2f} px a square at ({x}, {y}) cost {cost:.4f};  at {PK.PX}: ({x0}, {y0}) cost {cost0:.4f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:9s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
        for k, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"locke_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        stem = f"pose_{n}"
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{stem}.png")))
        with open(lp(os.path.join(OUT, f"{stem}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, fh)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Zaahen's Codex poses (assets/source/zaahen/codex_poses/zaahen-poses: POSE_PROMPTS.md, 20 key poses of his League
clips on his design, 2026-10-26) read back at the design's scale, in its colours, with the design's own head
(design_locke_poses.py's way).

    python tools/art/design_zaahen_poses.py --measure        # each pose's head match and its body against the design
    python tools/art/design_zaahen_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_zaahen_poses.py                  # writes assets/source/zaahen/hd/pose_<name>.png (+ .json)
    python tools/art/design_zaahen_poses.py --rematch        # the same, the heads searched again (else the json's)

His poses copy the design's head, so the head gives the place and the scale: the head box (pack_zaahen_poses.HEAD: the
horns, the circlet, the hair over the brow and the face, hd/idle.png rows 0-33, columns 42-64) is matched against the
picture (design_shyvana_poses.match_head). Codex's exports came off the pack's 9 px grid with soft alpha (its own
HANDOFF), so every pose is read on the matched head's own squares (design_shyvana_poses.sample_grid: the grid laid
through the head box's corner, one square per cell, opaque where most of it is, the median colour), then - where Codex
drew the body bigger or smaller round the head than the design has it - brought to the design's size by whole-line cuts
or repeats about the head's middle (BODY: the ratio of the pose's body to the design's, measured on the standing poses'
heights), every colour snapped to the design's own (Lab), the design's head pasted square for square on Codex's head's
place (the polygon POLY grown by a square above GROW_ROWS: one face in all frames - Codex redrew the head), Codex's own
hair left round it and its own horns left beside the pasted ones cleared, the outline closed. Each pose's json keeps where the head box went (its top-left square), for
rig_zaahen to place the pose. Heads Codex drew tipped (TILTED) keep Codex's own.
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
from design_zaahen_hd import lp  # noqa: E402
import pack_zaahen_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zaahen", "codex_poses", "zaahen-poses")
OUT = os.path.join(ROOT, "assets", "source", "zaahen", "hd")
# the horns, the circlet and its gold side pieces, the hair over the brow and the face to the chin - not the hair that
# falls down his back past the chin (rows 30 on), the wings or the shoulder plates (columns 38-44 from row 25)
POLY = [(48.0, 0.0), (51.0, 0.0), (52.0, 4.0), (53.0, 9.0), (54.0, 2.0), (58.0, 2.0), (59.0, 8.0), (60.0, 14.0),
        (62.0, 16.0), (62.0, 22.0), (61.0, 25.0), (60.0, 29.0), (57.0, 30.5), (53.0, 30.5), (50.0, 30.0),
        (45.0, 30.0), (44.0, 24.0), (41.0, 22.0), (41.0, 15.0), (44.0, 12.0), (46.0, 9.0), (47.0, 4.0)]
GROW_ROWS = 22                                   # the polygon grows by a square (its outline) above this row only
SCALES = np.arange(6.5, 12.01, 0.25)            # Codex's squares round the head (asked 9 px)
TILTED = {"d_fall": range(-50, 51, 10), "d_down": range(-50, 51, 10)}   # heads Codex drew tipped
# the body's size round the head against the design's (1.0 = the design's): a pose read on its head's squares is
# scaled by 1 / BODY[name] (whole lines cut or repeated about the head's middle) so its body is the design's size.
# Measured 2026-10-26 as the read-back's head top to its lowest square over the pose's skeleton's (pack_zaahen_poses.
# build: Codex followed the skeletons): 1.02-1.14 for most, 1.22-1.27 for q_up, e_spin, run4, rv_kneel (and r_rise by
# its feet); the four runs set so their bodies end within a square of their skeletons' heights
BODY = {"a_wind": 1.12, "a_sweep": 1.08, "q_cut1": 1.03, "q_cut2": 1.12, "q_crouch": 1.05, "q_up": 1.25, "w_thrust": 1.08,
        "w_pull": 1.12, "e_dash": 1.03, "e_spin": 1.2, "r_crouch": 1.1, "r_rise": 1.15, "r_stab": 1.12, "run1": 1.06,
        "run2": 1.1, "run3": 1.1, "run4": 1.2, "d_fall": 1.1, "d_down": 1.1, "rv_kneel": 1.22}
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
CACHE = "C:/t/za_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"zaahen-pose-{name}.png"))).convert("RGBA"))


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
    m = match_head(raw(name), head_box(design()), scales=SCALES, angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def is_hair(rgb):
    """His white-blond hair's creams on an (..., 3) array (the design's f8f0dc e0cfa6 bba175: blue well above 90 and
    under green) - not the gold of his circlet and armour (blue under 100), not the blue-grey skin (blue over green)."""
    rgb = rgb.astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (r > 150) & (g > 130) & (r - g < 45) & (b > 100) & (b < g - 8)


def clear_leftovers(fig, pasted, box):
    """Codex's own hair left round the pasted head (where it drew the head bigger or elsewhere): every hair-coloured
    square in `box` (rows / columns, the head box grown, above the chin) that the paste did not lay takes the most common
    colour round it that is not hair, or goes clear where most round it is clear; repeated until none is left."""
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


HORN_ROWS = 13                                   # the head box's rows from its top down to the circlet: the horns


def clear_horns(fig, pasted, box):
    """Codex's own horns left beside the pasted ones (w_pull's third horn, a strip between the two in w_pull and
    rv_kneel): in `box` (rows / columns: the horns' rows of the head box, three squares round), every part the paste did
    not lay that stays inside the box goes clear; a part that runs out of it (the glaive's shaft or a wing passing
    behind the head) stays."""
    y0, y1, x0, x1 = box
    sub = (fig[y0:y1, x0:x1, 3] > 0) & ~pasted[y0:y1, x0:x1]
    lb, n = ndimage.label(sub, structure=np.ones((3, 3), bool))
    for j in range(1, n + 1):
        m = lb == j
        ys, xs = np.nonzero(m)
        if ys.min() == 0 or ys.max() == m.shape[0] - 1 or xs.min() == 0 or xs.max() == m.shape[1] - 1:
            continue
        fig[y0:y1, x0:x1][m] = 0
    return fig


def resize_lines(a, k, mid):
    """`a` brought to k of its rows and columns by whole-line cuts (k < 1, design_riven.pick: in each stretch the line
    most like its neighbour goes) or repeats (k > 1, lines spread evenly) - no resampling, so a 1-square outline stays
    one square. -> (the new picture, where `mid` (column, row) lands in it)."""
    if abs(k - 1.0) < 0.005:
        return a, mid
    H, W = a.shape[:2]
    if k > 1.0:
        rows = np.minimum((np.arange(round(H * k)) / k).astype(int), H - 1)
        cols = np.minimum((np.arange(round(W * k)) / k).astype(int), W - 1)
        return a[np.ix_(rows, cols)], (mid[0] * k, mid[1] * k)
    op = a[..., 3] > 0
    pal = sorted({tuple(int(v) for v in p[:3]) for p in a[op]})
    lut = {c: i for i, c in enumerate(pal)}
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
    out[m, :3] = np.array(pal, np.uint8)[small[m]]
    out[m, 3] = 255
    return out, (float(np.interp(mid[0], kc, range(len(kc)))), float(np.interp(mid[1], rows, range(len(rows)))))


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = PK.HEAD
    hw, hh = c1 - c0, r1 - r0
    a, (ci, cj) = sample_grid(raw(name), s, hx, hy)   # the head box's top-left at cell (ci, cj)
    k = 1.0 / BODY.get(name, 1.0)
    a, mid = resize_lines(a, k, (ci + hw / 2, cj + hh / 2))
    ci, cj = int(round(mid[0] - hw / 2)), int(round(mid[1] - hh / 2))
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
        big_ = clear_leftovers(big_, pasted, (max(0, gy - 4), gy + 31, max(0, gx - 4), gx + hw + 4))
        big_ = clear_horns(big_, pasted, (gy - 3, gy + HORN_ROWS, gx - 3, gx + hw + 3))
    big_ = finish(big_)
    op = big_[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    for j in range(1, n + 1):
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
            m = matched(n, a.rematch)
            s, x, y, cost, ang = m
            r = raw(n)
            op = r[..., 3] >= 128
            ys, xs = np.nonzero(op)
            # the soles to the head box's top, in the head's squares, against the design's 84 rows
            print(f"{n:9s} {s:5.2f} px a square at ({x}, {y}) cost {cost:.4f}; figure {(xs.max() - xs.min()) / s:5.1f} x "
                  f"{(ys.max() - ys.min()) / s:5.1f} squares, head top to the lowest pixel {(ys.max() - y) / s:5.1f}")
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
            path = os.path.join(a.sheet, f"zaahen_poses_{k}.png")
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

#!/usr/bin/env python3
"""Aurelion Sol's Codex poses (assets/source/aurelionsol/codex_poses/aurelionsol-poses: POSE_PROMPTS.md, 10 key poses
of his League clips on the design) read back at the design's scale, in its colours, with the design's own head
(design_belveth_poses.py's way).

    python tools/art/design_aurelionsol_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_aurelionsol_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_aurelionsol_poses.py                  # writes assets/source/aurelionsol/hd/pose_<name>.png (+ .json)
    python tools/art/design_aurelionsol_poses.py --rematch        # the same, the heads searched again (else the json's)

His poses copy the design's head, so the head gives the scale: the head (the polygon POLY on hd/idle.png: the mane, the
gold crown and horns, the bony face with both cyan eyes, the teeth and the chin's gold point - not the neck under it)
scaled over a range of px a square is matched against the picture (design_shyvana_poses.match_head on the head box with
everything outside POLY clear), the pose sampled on squares of the head's own size, the grid laid so the matched head box
keeps its middle, every colour snapped to the design's own (Lab), the design's head pasted square for square on Codex's
head's place (one face in all frames) - in q_breath only above the jaw (JAW_ROW: Codex opened the mouth there, the
breath; the eyes, the crown and the mane are the design's), the outline closed. Each pose's json keeps where the head box
went (its top-left square), for rig_aurelionsol to place the pose. The picture read is raw/aurelionsol-pose-<name>.png.
Codex drew every pose with a soft edge (alpha 1-254 on the rim): a square is opaque when most of its pixels are
(alpha >= 128), its colour the median of those.
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
from design_aurelionsol_hd import lp  # noqa: E402
import pack_aurelionsol_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aurelionsol", "codex_poses", "aurelionsol-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "aurelionsol", "hd")
# the mane's top (row 0), the crown and the horns, the face with the eyes (27, 20) and (34, 21), the teeth and the chin's gold
# point down to row 31 (square edges on hd/idle.png) - not the neck and the chest under it (the cyan lines from row 26 at
# columns 16-26), not the mane's strands hanging at the lower left
POLY = [(3.0, 9.0), (7.0, 3.0), (12.0, 0.0), (21.0, 0.0), (27.0, 3.0), (31.0, 6.0), (34.0, 9.0), (37.0, 13.0),
        (38.5, 18.0), (38.5, 27.0), (37.0, 32.0), (33.0, 32.0), (28.0, 30.0), (24.0, 28.5), (20.0, 26.0), (16.0, 23.0),
        (11.0, 21.0), (6.0, 19.0), (3.0, 15.0)]
JAW_ROW = {"q_breath": 23}   # the design's head pasted only above this row (the open jaw below it is Codex's)
SCALES = np.arange(7.0, 16.01, 0.25)
TILTED = {}
SCALE = {"d_rear": 11.5}                         # px a square set by hand where the head's own does not fit the body
# (d_rear: Codex flattened the head as it falls back, so the upright design head matched at 9.75 and the body read 1.6x)
MATCH = {}                                       # head matches set by hand (px a square, x, y, cost, tilt)
# Codex kept the head at the design's size but drew the body bigger round it in most poses: read at the head's scale the
# shoulder orbs came out 21-24 squares apart (the design's 20) and the head-box top to the lowest claw up to 94 rows
# (the design's 71). The body is brought back by whole rows and columns dropped (least loss, design_gnar_model.keep_axis;
# never through the head box) by this factor - the orbs and the height read together, set by eye beside the design:
# Codex kept the head at the design's size but drew the body bigger round it: the opaque squares outside the head came out
# 1.1-1.6 times the design's body (sqrt of the area), partly the limbs spread clear of the body where the design's
# overlap. The body is brought back by whole rows and columns dropped (least loss, design_gnar_model.keep_axis; never
# through the head box) by this factor - the chest's width, the tail's thickness and the arms' length read together
# beside the design:
BODY = {"a_wind": 1.12, "a_throw": 1.12, "q_wind": 1.08, "q_breath": 1.18, "e_reach": 1.2, "e_hold": 1.03,
        "r_call": 1.15, "r_pull": 1.2, "d_rear": 1.15, "d_down": 1.1}
CACHE = "C:/t/as_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"aurelionsol-pose-{name}.png"))).convert("RGBA"))


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def head_box(d):
    """The head box with everything outside POLY clear (the neck's and the chest's squares never steer the match)."""
    r0, r1, c0, c1 = PK.HEAD
    h = d.copy()
    h[~head_mask(d)] = 0
    return h[r0:r1, c0:c1]


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


MOUTH = (40, 10, 70)   # Codex's mouth inside (raw q_breath: dark purple with a magenta and cyan glow), snapped to the design


def mouth(fig, d, box):
    """Enclosed clear squares inside the head box (top-left square `box`) filled with the mouth's dark purple: pasting the
    design's upper face over Codex's open jaw closed the gap between the jaws into a see-through pocket (it showed the
    ground through the mouth)."""
    from scipy import ndimage as nd
    r0, r1, c0, c1 = PK.HEAD
    op = fig[..., 3] > 0
    hole = nd.binary_fill_holes(op) & ~op
    inbox = np.zeros_like(hole)
    inbox[box[1]:box[1] + (r1 - r0) + 12, box[0]:box[0] + (c1 - c0) + 6] = True
    lab, n = nd.label(hole)
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)
    colour = pal[((pal - np.array(MOUTH)) ** 2).sum(1).argmin()]
    out = fig.copy()
    for j in range(1, n + 1):
        h = lab == j
        if (h & inbox).sum() * 2 > h.sum():
            out[h] = (*colour, 255)
    return out


def drop_specks(a, most=12):
    """Pieces apart from the figure's biggest (8-connected) of at most `most` squares cleared (the read-back's crumbs)."""
    a = a.copy()
    lb, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lb, range(1, n + 1))
        keep = int(np.argmax(sizes)) + 1
        for j in range(1, n + 1):
            if j != keep and sizes[j - 1] <= most:
                a[lb == j] = 0
    return a


def matched(name, again=False):
    """match_head's (px a square, x, y, cost, tilt) for a pose, kept in hd/pose_<name>.json ("match") once found."""
    if name in MATCH:
        return MATCH[name]
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


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = PK.HEAD
    hw, hh = c1 - c0, r1 - r0
    s2 = SCALE.get(name, s)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if not ang:                                        # a tipped head keeps Codex's own (the design's is upright)
        keep = ys < JAW_ROW.get(name, 10 ** 6)
        big_[ys[keep] - r0 + cj + pad, xs[keep] - c0 + ci + pad] = d[ys[keep], xs[keep]]
    big_ = finish(drop_specks(big_))
    if name in JAW_ROW:                                # the open mouth: the pocket the design's upper face closed off
        big_ = mouth(big_, d, (ci + pad + 1, cj + pad + 1))
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    fig, at = big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0)
    if BODY.get(name, 1.0) != 1.0:
        fig, at = shrink(fig, at, BODY[name])
    fig, (tx, ty) = trim_tip(drop_specks(fig))   # (again: the shrink's outline can leave a crumb on its own row)
    return fig, (at[0] - tx, at[1] - ty), s2, cost, ang


def shrink(fig, at, k):
    """The body brought down by k: whole rows and columns dropped (least loss: design_gnar_model.keep_axis on the
    figure's colour indices), the head box's rows and columns kept whole; the outline closed again. -> (figure, the head
    box's new top-left square)."""
    from design_gnar_model import keep_axis
    r0, r1, c0, c1 = PK.HEAD
    hw, hh = c1 - c0, r1 - r0
    flat = fig.reshape(-1, 4).astype(np.int64)
    key = (flat[:, 0] << 24) | (flat[:, 1] << 16) | (flat[:, 2] << 8) | flat[:, 3]
    idx = np.unique(key, return_inverse=True)[1].reshape(fig.shape[:2])
    H, W = idx.shape
    rows = keep_axis([idx[y] for y in range(H)], round(H / k), range(at[1], at[1] + hh))
    sub = idx[rows]
    cols = keep_axis([sub[:, x] for x in range(W)], round(W / k), range(at[0], at[0] + hw))
    out = fig[np.ix_(rows, cols)]
    at2 = (cols.index(at[0]), rows.index(at[1]))
    out = finish(out)
    ys, xs = np.nonzero(out[..., 3] > 0)
    y0, x0 = ys.min(), xs.min()
    return out[y0:ys.max() + 1, x0:xs.max() + 1], (at2[0] + 1 - x0, at2[1] + 1 - y0)


def trim_tip(fig, rows=4):
    """The tail tip's outline spurs: in the figure's lowest `rows` rows, near-black squares with no coloured square
    among their eight neighbours cleared, again until none is left (Codex ended the tail with a little star or a hooked
    flick that read back as a knob of bare outline under the tip: 「这里多出来一个是什么意思」)."""
    fig = fig.copy()
    op = fig[..., 3] > 0
    luma = fig[..., :3].astype(float) @ (0.3, 0.59, 0.11)
    dark = op & (luma < 25)
    H = fig.shape[0]
    y0 = H - rows
    while True:
        col = np.pad(op & ~dark, 1)
        near = np.zeros_like(op)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    near |= col[1 + dy:1 + dy + H, 1 + dx:1 + dx + fig.shape[1]]
        bare = dark & ~near
        bare[:y0] = False
        if not bare.any():
            break
        fig[bare] = 0
        op &= ~bare
        dark &= ~bare
    ys, xs = np.nonzero(fig[..., 3] > 0)
    return fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (xs.min(), ys.min())


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
            s, x, y, cost, ang = match_head(r, head_box(d), scales=SCALES, angles=TILTED.get(n, (0,)))
            area = float(np.sqrt((r[..., 3] >= 128).sum() / (d[..., 3] > 0).sum()))
            print(f"{n:9s} head {s:5.2f} px a square at ({x}, {y}) tilted {ang}, cost {cost:.4f}; area {area:5.2f}")
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
            path = os.path.join(a.sheet, f"aurelionsol_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, fh)


if __name__ == "__main__":
    main()

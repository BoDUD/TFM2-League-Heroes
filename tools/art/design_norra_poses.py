#!/usr/bin/env python3
"""Norra's Codex poses (assets/source/norra/codex_poses/norra-poses: POSE_PROMPTS.md, 13 key poses after the videos on
her design, 2026-10-26) read back at the design's scale, in its colours, with the design's own head
(design_locke_poses.py's way).

    python tools/art/design_norra_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_norra_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_norra_poses.py                  # writes assets/source/norra/hd/pose_<name>.png (+ .json)
    python tools/art/design_norra_poses.py --rematch        # the same, the heads searched again (else the json's)

Her poses copy the design's head, so the head gives the place: the head box (pack_norra_poses.HEAD: the hat, the head
wrap, the glasses and the face, hd/idle.png rows 0-47, columns 7-44) is matched against the export
(design_shyvana_poses.match_head), the pose read on the delivery's 14 px grid (one square = one pixel of the design:
the pack's PX; Codex's QA: hard alpha, grid_errors 0, every pose framed to the design's 72 rows), every colour snapped
to the design's own (Lab), the design's head pasted square for square on Codex's head's place (the polygon POLY:
the hat with its feathers, bead ring and discs, the wrap and the face to the scarf - not the floppy ears below it,
which Codex swung with each move; one face in all frames: Codex redrew the head, not copied it), Codex's own hat
colours left round the paste cleared, the outline closed. Each pose's json keeps where the head box went (its
top-left square), for rig_norra to place the pose.
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
from design_shyvana_poses import match_head  # noqa: E402
from design_locke_poses import shrink  # noqa: E402
from design_norra_hd import lp  # noqa: E402
import pack_norra_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "norra", "codex_poses", "norra-poses")
OUT = os.path.join(ROOT, "assets", "source", "norra", "hd")
# the hat (feathers, bead ring, the discs hanging from it), the head wrap and the face to the scarf, in hd/idle.png's
# squares - the floppy ears below row 36 left out (Codex swung them with the move)
POLY = [(30, 0), (37, 0), (38, 6), (41, 9), (43, 12), (44, 17), (46, 19), (46, 28), (42, 30), (40, 33), (39, 38),
        (39, 44), (36, 47), (18, 47), (15, 44), (14, 38), (12, 33), (9, 33), (6, 30), (4, 27), (4, 19), (8, 17),
        (10, 9), (14, 6), (26, 5), (28, 2)]
GROW_ROWS = 34                                   # the polygon grows by a square (its outline) above this row only
SCALES = np.arange(12.0, 16.01, 0.25)
BODY_PX = 14.0                                   # px of the export a square (the design's; BODY: per pose)
BODY = {}
# the poses whose head Codex drew tipped (no upright match under 0.3; d_fall's head thrown back, q_throw's following the
# fling): matched at these tilts; a tipped head keeps Codex's own (the design's is upright, Locke's way)
TILTED = {"q_throw": range(-20, 21, 10), "d_fall": range(-20, 21, 10)}
KEEP_HEAD = {"d_fall"}
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
CACHE = "C:/t/nr_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    """The picture the head is matched on: Codex's 14 px export."""
    return np.asarray(Image.open(lp(os.path.join(SRC, f"norra-pose-{name}.png"))).convert("RGBA"))


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
    """The export's squares: each 14 px cell's middle pixel (the grid from the canvas corner), alpha 0 / 255."""
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
    m = match_head(raw(name), head_box(design()), scales=SCALES, angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def hat_palette():
    """The colours only her hat carries in the design (teal, the feathers' blue and pink, the bead ring's cream and
    beige, the discs): the design's head squares above the face (rows 0-33) whose colour appears nowhere below row 47
    (so not the red wrap, which the scarf and sash share, nor the outline)."""
    d = design()
    hm = head_mask(d)
    top = {tuple(int(v) for v in d[y, x, :3]) for y, x in zip(*np.nonzero(hm)) if y < 34}
    below = {tuple(int(v) for v in p[:3]) for p in d[48:][d[48:, :, 3] > 0]}
    return top - below


def body_palette():
    """The colours only her body carries (the robe's purples, the gold ring, the hands' lit skin): the design's below the
    head (row 48 on) that the hat (the head's rows 0-27) never shows."""
    d = design()
    hm = head_mask(d)
    hat = {tuple(int(v) for v in d[y, x, :3]) for y, x in zip(*np.nonzero(hm)) if y < 28}
    below = {tuple(int(v) for v in p[:3]) for p in d[48:][d[48:, :, 3] > 0]}
    return below - hat


def clear_old_hat(fig, pasted, top, body_pal, ink, reach=5, rows=30):
    """Codex's own hat round the paste where it drew the head bigger or tipped (q_swirl 15 px a square, r_cast 15.25,
    run1 15, q_throw tipped 10 degrees: a second brim and a band outside the feathers showed round the design's hat -
    the user, 2026-10-26: 「放技能的时候帽子有点重影 看起来像多出来了一点帽子」): within `reach` squares of the paste and
    above the head wrap (`rows` rows down from the head box's top `top`), every square that is not her body's (a body-only
    colour, or the outline touching one) goes clear; finish() closes the outline round the design's hat again."""
    op = fig[..., 3] > 0
    rgb = fig[..., :3]
    body = np.zeros(op.shape, bool)
    for c in body_pal:
        body |= np.all(rgb == np.array(c, rgb.dtype), -1)
    body &= op & ~pasted
    line = op & np.all(rgb == np.array(ink, rgb.dtype), -1)
    keep = body | (line & ndimage.binary_dilation(body, structure=np.ones((3, 3), bool)))
    band = ndimage.binary_dilation(pasted, structure=np.ones((3, 3), bool), iterations=reach) & ~pasted
    band[top + rows:] = False
    out = fig.copy()
    out[band & op & ~keep] = 0
    return out


def clear_leftovers(fig, pasted, box, pal):
    """Codex's own hat left round the pasted head (where it drew the hat bigger or elsewhere): every square of a hat-only
    colour in `box` (rows / columns, the head box grown) that the paste did not lay takes the most common colour round
    it that is not a hat colour, or goes clear where most round it is clear; repeated until none is left."""
    y0, y1, x0, x1 = box
    hat = lambda c: tuple(int(v) for v in c[:3]) in pal
    for _ in range(12):
        op = fig[..., 3] > 0
        left = np.zeros(op.shape, bool)
        left[y0:y1, x0:x1] = True
        left &= op & ~pasted
        left &= np.array([[hat(fig[y, x]) for x in range(fig.shape[1])] for y in range(fig.shape[0])])
        if not left.any():
            return fig
        out = fig.copy()
        for y, x in zip(*np.nonzero(left)):
            nb = fig[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
            clear = int((nb[:, 3] == 0).sum())
            keep = [tuple(c) for c in nb if c[3] > 0 and not hat(c)]
            if clear >= 5 or not keep:
                if clear >= 3:
                    out[y, x] = 0
                continue
            out[y, x] = max(set(keep), key=keep.count)
        fig = out
    return fig


def read(name, match, body=None):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt). `body`: px of the export a square (BODY's by default)."""
    d = design()
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = PK.HEAD
    hw, hh = c1 - c0, r1 - r0
    sb = body or BODY.get(name, BODY_PX)
    a = on_grid(raw(name))
    mid = ((hx + hw * s / 2) / PK.PX, (hy + hh * s / 2) / PK.PX)   # Codex's head middle, in the export's squares
    if sb > PK.PX + 0.01:                          # the body brought to the design's size round the head's middle
        a, mid = shrink(a, PK.PX / sb, mid)
    ci, cj = int(round(mid[0] - hw / 2)), int(round(mid[1] - hh / 2))
    fig = snap(a, d)
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if name not in KEEP_HEAD:
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
        pasted = np.zeros(big_.shape[:2], bool)
        pasted[ys - r0 + cj + pad, xs - c0 + ci + pad] = True
        gy, gx = cj + pad, ci + pad
        if abs(s - PK.PX) > 0.01 or ang:          # Codex's head drawn bigger or tipped: its hat shows round the paste
            big_ = clear_old_hat(big_, pasted, gy, body_palette(), PD.edge_colour(d))
        big_ = clear_leftovers(big_, pasted, (max(0, gy - 6), gy + 36, max(0, gx - 6), gx + (c1 - c0) + 6),
                               hat_palette())
    big_ = finish(big_)
    op = big_[..., 3] > 0
    lb, k = ndimage.label(op, structure=np.ones((3, 3), bool))
    for j in range(1, k + 1):
        if (lb == j).sum() < SPECK:
            big_[lb == j] = 0
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), float(sb), cost, ang


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
            s, x, y, cost, ang = match_head(r, head_box(d), scales=SCALES, angles=(0,))
            s0, x0, y0, cost0, _ = match_head(r, head_box(d), scales=(float(PK.PX),), angles=(0,))
            print(f"{n:8s} best {s:5.2f} px a square at ({x}, {y}) cost {cost:.4f};  at {PK.PX}: ({x0}, {y0}) "
                  f"cost {cost0:.4f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:8s} {s:5.2f} px a square, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 7] for i in range(0, len(tiles), 7)]
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
            path = os.path.join(a.sheet, f"norra_poses_{k}.png")
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

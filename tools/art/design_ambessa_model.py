#!/usr/bin/env python3
"""Ambessa's step-1 designs (assets/source/ambessa/codex_model/ambessa-model, 2026-10-25) read back on their own grids
and brought to the game's count: A (her idle 3/4 front: idle, run, every action) and SA (her side) both 84 rows from
the top of her hair to her soles (48 game px at PPU 1.75, the step-1 pack's numbers).

    python tools/art/design_ambessa_model.py --options DIR   # the candidates side by side
    python tools/art/design_ambessa_model.py                 # writes assets/source/ambessa/hd/{idle,side}.png (PICK)

Codex's squares (asked 13 px; its HANDOFF: no exact grid, soft alpha, the alpha cut at 128 in its own copies): the
faces' steps at 3x about 30 px, the colour edges' period A-1 9.7 (10 / 19-20 / 29) both ways, the others less clear
(A-2 10-14, SA-1 / SA-2 7-16) - read on about 10 px, about 115 rows, and cut to the count the design-tryndamere way
(design_gnar_model's keep_axis): its own K colours (design_varus.kmeans), whole rows then columns dropped to the count
(least loss - a twin first - never the face's rows / columns: the eyes, the brows, the lips), the width in proportion,
strips.complete_outline with that box kept. The hair's top is the figure's first row.
The picks (the user, 2026-10-25: 「头可以缩小点」「身体清晰点」「你调整一下」): A-1 (idle) and SA-1 (side), at PPU 2.0 (96 rows,
48 game px) - the body cut to 70 rows from Codex's ~77 (few dropped, its plates and blades stay clear), the head
(HEADS: a polygon and its outline ring, not the fur or the scarf) cut on its own to 26 rows (HEAD_SHARE 0.27; the pack
drew a third), the eye band whole, its chin where it was, the pixels it leaves the nearest body colour within 3 squares
(the fur behind it) or clear (small_head). --options shows the four takes cut whole to the count, as first read.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as dv  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_gnar_model import keep_axis, sheet  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ambessa", "codex_model", "ambessa-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "ambessa", "hd")
K = 40
TOP_PX = 48      # game px from the top of her hair to her soles
PPU = 2.0        # 1.75 in the step-1 pack; 2.0 so the body keeps nearly every row Codex drew (the user: 「身体清晰点」)
TOP_ROWS = round(TOP_PX * PPU)
HEAD_SHARE = 0.27   # hair top to chin, of the height (the pack asked a third; the user: 「头可以缩小点」)
PICK = {"idle": "A-1", "side": "SA-1"}   # the user left the pick to Claude (「你调整一下」, 2026-10-25)
# take -> (her head on the read-back: a polygon (x, y) round the hair and the face down to the chin; the eye band kept
# whole when the head shrinks: rows y0..y1, columns x0..x1)
HEADS = {
    "A-1": ([(36, 15), (40, 10), (44, 5), (52, 1), (58, 0), (65, 1), (72, 4), (80, 8), (84, 13), (87, 18), (84, 24),
             (81, 28), (80, 33), (77, 37), (70, 39), (62, 39), (58, 36), (54, 33), (52, 30), (47, 30), (43, 28),
             (39, 25), (37, 21)], (19, 27, 60, 80)),
    "SA-1": ([(17, 13), (21, 8), (27, 3), (35, 0), (46, 0), (55, 3), (61, 8), (62, 14), (64, 20), (65, 26), (63, 31),
              (61, 35), (55, 38), (48, 38), (44, 33), (40, 31), (30, 31), (22, 31), (18, 27), (16, 20)], (17, 25, 50, 63)),
}
# take -> (file, square px read at, rows to (None: TOP_ROWS), the face box kept whole on the raw canvas: x0, y0, x1, y1:
# the eyes, the brows, the lips)
DRAFTS = {
    "A-1": ("A-1", 9.9, None, (559, 257, 813, 479)),
    "A-2": ("A-2", 10.4, None, (541, 250, 804, 460)),
    "SA-1": ("SA-1", 10.4, None, (620, 235, 823, 458)),
    "SA-2": ("SA-2", 10.4, None, (628, 242, 829, 447)),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, kept rows, kept columns) on the cropped read-back."""
    f, size, _, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"ambessa-{f}.png"))).convert("RGBA"))
    raw, _, (bx, by) = regrid(a, size)
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    y0, x0 = ys.min(), xs.min()
    raw = raw[y0:ys.max() + 1, x0:xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    bx, by = np.asarray(bx), np.asarray(by)
    cell = lambda b, v: int(np.searchsorted(b, v, side="right")) - 1
    fr = range(cell(by, fy0) - y0, cell(by, fy1) - y0 + 1)
    fc = range(cell(bx, fx0) - x0, cell(bx, fx1) - x0 + 1)
    return raw, fr, fc


def paint(idx, pal):
    fig = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    fig[m, :3] = pal[idx[m]]
    fig[m, 3] = 255
    return fig


def cut_to(raw, fr, fc, idx, pal, rows_to):
    H, W = idx.shape
    if rows_to >= H:
        return paint(idx, pal), list(range(H)), list(range(W))
    rows = [0] + [r + 1 for r in keep_axis([idx[y] for y in range(1, H)], rows_to - 1,
                                             range(fr.start - 1, fr.stop - 1))]
    sub = idx[rows]
    cols = keep_axis([sub[:, x] for x in range(W)], round(W * rows_to / H), fc)
    fig = paint(idx[np.ix_(rows, cols)], pal)
    keep = np.zeros(fig.shape[:2], bool)
    r_in = [rows.index(r) for r in fr if r in rows]
    c_in = [cols.index(c) for c in fc if c in cols]
    keep[min(r_in):max(r_in) + 1, min(c_in):max(c_in) + 1] = True
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1], rows, cols


def polygon(shape, pts):
    im = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon(pts, fill=1)
    return np.asarray(im).astype(bool)


def small_head(take):
    """The take at TOP_ROWS with its head HEAD_SHARE of them: the body cut to the rest (few rows dropped), the head
    (HEADS polygon) cut on its own to its share - rows and columns, the eye band whole - its chin back where it was,
    the pixels it no longer covers taking the nearest body colour within 3 squares (the fur behind it) or clear.
    -> (picture, rows read)."""
    raw, fr, fc = read_back(take)
    idx, pal = dv.kmeans(raw, K)
    idx = np.where(raw[..., 3] > 0, idx, -1)
    H, W = idx.shape
    poly, (e0, e1, x0, x1) = HEADS[take]
    # the polygon and its outline ring (2 squares out), the fur (teal) and the scarf (red) left to the body
    from scipy import ndimage
    inside = polygon(idx.shape, poly)
    rgb = pal[np.maximum(idx, 0)].astype(int)
    fur = (rgb[..., 1] > rgb[..., 0] + 15) & (idx >= 0)
    red = (rgb[..., 0] > rgb[..., 1] + 80) & (idx >= 0)
    head = (inside | (ndimage.binary_dilation(inside, iterations=2) & ~fur & ~red)) & (idx >= 0)
    chin = int(np.nonzero(head.any(1))[0].max())
    ht = round(TOP_ROWS * HEAD_SHARE)
    bt = TOP_ROWS - ht
    rows_to = round(H * bt / (H - chin - 1))
    rows = [0] + [r + 1 for r in keep_axis([idx[y] for y in range(1, H)], rows_to - 1, range(e0 - 1, e1))]
    cols = keep_axis([idx[rows][:, x] for x in range(W)], round(W * rows_to / H), range(x0, x1 + 1))
    sub, hm = idx[np.ix_(rows, cols)], head[np.ix_(rows, cols)]
    ri = [i for i, r in enumerate(rows) if e0 <= r <= e1]
    ci = [i for i, c in enumerate(cols) if x0 <= c <= x1]
    hy, hx = np.nonzero(hm)
    by0, by1, bx0, bx1 = hy.min(), hy.max() + 1, hx.min(), hx.max() + 1
    hs = np.where(hm[by0:by1, bx0:bx1], sub[by0:by1, bx0:bx1], -1)
    k = ht / (by1 - by0)
    kr = keep_axis([hs[y] for y in range(hs.shape[0])], ht, range(min(ri) - by0, max(ri) - by0 + 1))
    hs = hs[kr]
    kc = keep_axis([hs[:, x] for x in range(hs.shape[1])], round(hs.shape[1] * k), range(min(ci) - bx0, max(ci) - bx0 + 1))
    hs = hs[:, kc]
    # the chin's centre stays: the new head's bottom row on the old one's, centred where the old bottom row was
    bottom = np.nonzero(hm[by1 - 1])[0]
    cx = (bottom.min() + bottom.max()) / 2
    nb = np.nonzero(hs[-1] >= 0)[0]
    ox = round(cx - (nb.min() + nb.max()) / 2)
    oy = by1 - hs.shape[0]
    body = np.where(hm, -1, sub)
    dist, (iy, ix) = ndimage.distance_transform_edt(body < 0, return_indices=True)
    fill = np.where(hm & (dist <= 3), body[iy, ix], -1)
    out = np.where(hm, fill, body)
    ys, xs = np.nonzero(hs >= 0)
    out[ys + oy, xs + ox] = hs[ys, xs]
    fig = paint(out, pal)
    keep = np.zeros(fig.shape[:2], bool)
    keep[ys.min() + oy:ys.max() + oy + 1, xs.min() + ox:xs.max() + ox + 1] = True
    fig = PD.despeckle(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=PD.edge_colour(fig), feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1], H


def cut(take):
    """The take at its count: (picture, rows kept, columns kept, rows read)."""
    raw, fr, fc = read_back(take)
    idx, pal = dv.kmeans(raw, K)
    idx = np.where(raw[..., 3] > 0, idx, -1)
    H = idx.shape[0]
    rows_to = DRAFTS[take][2] or TOP_ROWS   # the hair's top is row 0: the whole figure is TOP_ROWS
    fig, rows, cols = cut_to(raw, fr, fc, idx, pal, rows_to)
    return fig, rows, cols, H


def write(fig, name):
    Image.fromarray(fig).save(lp(os.path.join(OUT, f"{name}.png")))
    Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    a = ap.parse_args()
    if a.options:
        os.makedirs(lp(a.options), exist_ok=True)
        cells = []
        for t in DRAFTS:
            fig, rows, cols, H = cut(t)
            cells.append((t, fig))
            Image.fromarray(fig).save(lp(os.path.join(a.options, f"opt_{t}.png")))
            print(t, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)
        sheet(cells, os.path.join(a.options, "ambessa_model_options.png"))
        return
    if not all(PICK.values()):
        sys.exit("no pick yet: run --options and ask the user")
    os.makedirs(lp(OUT), exist_ok=True)
    for name, take in PICK.items():
        fig, H = small_head(take)
        write(fig, name)
        print(name, take, fig.shape[1], "x", fig.shape[0], "of", H, "rows read")

if __name__ == "__main__":
    main()

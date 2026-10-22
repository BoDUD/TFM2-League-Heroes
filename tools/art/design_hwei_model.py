#!/usr/bin/env python3
"""Hwei's step-1 designs (assets/source/hwei/codex_model/hwei-model, 2026-10-22, Codex 2026-10-22/new-chat-4) read back
on their own grids and brought to the game's count: 60 rows from the top of his hair to the soles, the crescent of
paint above on the same scale (40 game px at PPU 1.5, the user's picks: 「头发顶到脚底 40 游戏像素，PPU 1.5，只做四分之三侧面」).

    python tools/art/design_hwei_model.py --options DIR   # the candidates side by side
    python tools/art/design_hwei_model.py                 # writes assets/source/hwei/hd/idle.png

Codex's squares (asked 15 px; its HANDOFF: not one exact grid, soft alpha, the tops and soles off the layout), by the
autocorrelation of the edge profiles: A-1 16 px (hair top y 292 to the soles y 1247: 59.7 squares - on the count),
A-2 17 px but drawn smaller (hair top y 335 to the soles y 1232: 52.8 squares). Read finer than drawn, A-2 still
comes back 73 rows of its count 76 (regrid snaps to the drawn edges: at 15 or 14.5 px the same 73 rows, no twins),
so A-2 stays a little short (hair to soles ~57.6 rows = 38.4 game px); it is never blown up by doubled rows. Each
take is read at the size in DRAFTS and then cut to its count the design-tryndamere way (design_gnar_model's keep_axis): its own K colours
(design_varus.kmeans), whole rows then columns dropped to the count (least loss - a twin first - never the face's rows /
columns: brows, eyes, the mouth), the width in proportion, strips.complete_outline with the face kept. The count of a
take is 60 x its whole height over its hair-to-soles height (the crescent in proportion).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as dv  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_gnar_model import keep_axis, sheet  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "hwei", "codex_model", "hwei-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "hwei", "hd")
K = 40
BODY = 60
PICK = None   # the user's pick: "A-1" or "A-2"
# take -> (square px read at, the hair's top y on the raw canvas, the face's box there: x0, y0, x1, y1 - brows to mouth)
DRAFTS = {
    "A-1": (16.0, 292, (600, 440, 760, 560)),
    "A-2": (15.0, 335, (600, 460, 800, 590)),
}
# the face squares redrawn on the written design (codex-face-half-squares): (x, y, colour) on hd/idle.png
FACE = []


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, face rows, face columns, the count) on the cropped read-back."""
    size, hair, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"hwei-model-{take}-raw.png"))).convert("RGBA"))
    raw, _, (bx, by) = regrid(a, size)
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    y0, x0 = ys.min(), xs.min()
    raw = raw[y0:ys.max() + 1, x0:xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    bx, by = np.asarray(bx), np.asarray(by)
    cell = lambda b, v: int(np.searchsorted(b, v, side="right")) - 1
    fr = range(cell(by, fy0) - y0, cell(by, fy1) - y0 + 1)
    fc = range(cell(bx, fx0) - x0, cell(bx, fx1) - x0 + 1)
    oy = np.nonzero(a[..., 3] >= 128)[0]
    rows_to = round(BODY * (oy.max() + 1 - oy.min()) / (oy.max() + 1 - hair))
    return raw, fr, fc, rows_to


def recolour(raw):
    idx, pal = dv.kmeans(raw, K)
    idx = np.where(raw[..., 3] > 0, idx, -1)
    return idx, pal


def paint(idx, pal):
    fig = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    fig[m, :3] = pal[idx[m]]
    fig[m, 3] = 255
    return fig


def cut(take):
    """The take at its count: (picture, rows kept, columns kept, rows read)."""
    raw, fr, fc, rows_to = read_back(take)
    idx, pal = recolour(raw)
    H, W = idx.shape
    if rows_to >= H:
        return paint(idx, pal), list(range(H)), list(range(W)), H
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
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1], rows, cols, H


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
        sheet(cells, os.path.join(a.options, "hwei_model_options.png"))
        return
    if not PICK:
        sys.exit("no pick yet: run --options and ask the user")
    os.makedirs(lp(OUT), exist_ok=True)
    fig, rows, cols, H = cut(PICK)
    fig = fig.copy()
    for x, y, c in FACE:
        assert fig[y, x, 3] > 0, (x, y)
        fig[y, x, :3] = c
    Image.fromarray(fig).save(lp(os.path.join(OUT, "idle.png")))
    Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, "idle_4x.png")))
    print("idle", PICK, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)


if __name__ == "__main__":
    main()

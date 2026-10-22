#!/usr/bin/env python3
"""Udyr's step-1 designs (assets/source/udyr/codex_model, 2026-10-22, Codex 2026-10-22/new-chat-2) read back on their
own grids and brought to the game's count: 60 rows from the raised fists to the soles in his plain guard, 61 for the
bear, 69 for the ram, 73 for the phoenix (40 game px at PPU 1.5 and the stances on its scale, the user's picks:
「平常姿态 40 游戏像素，PPU 1.5，只做四分之三侧面」).

    python tools/art/design_udyr_model.py --options DIR   # the candidates side by side
    python tools/art/design_udyr_model.py                 # writes assets/source/udyr/hd/{idle,q_idle,e_idle,r_idle}.png

Codex's squares (asked A 18 px, Q / E 15, R 13; its HANDOFF: not one exact grid, the tops and soles off the layout):
read at the 8x faces, A about 16-17 px, the stances about 12-14 px. Each take is read a little FINER than it was drawn
(SQ below; regrid snaps to the drawn edges, so a smaller size only splits a square into twins) and then cut to the
count the design-tryndamere way (design_gnar_model's keep_axis): its own K colours (design_varus.kmeans), whole rows
then columns dropped to the count (least loss - a twin first - never the face's rows / columns: brows, eyes, the mouth,
the beard), the width in proportion, strips.complete_outline with the face kept. Cutting every take to its count also
evens out Codex's sizes (A-1 came 1.05x, E-1 1.10x, Q-2 0.9x their boxes). The written set shares one palette (K
colours by k-means over the picks' read-backs together).
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

SRC = os.path.join(ROOT, "assets", "source", "udyr", "codex_model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "udyr", "hd")
K = 40
PICKS = {}   # part -> take, the user's picks
PART = {"A": "idle", "Q": "q_idle", "E": "e_idle", "R": "r_idle"}
ROWS = {"A": 60, "Q": 61, "E": 69, "R": 73}
# take -> (square px read at, the face's box on the raw canvas: x0, y0, x1, y1 - brows to the beard's end)
DRAFTS = {
    "A-1": (15.5, (700, 360, 840, 520)), "A-2": (15.5, (660, 370, 800, 530)),
    "Q-1": (11.5, (740, 480, 860, 620)), "Q-2": (11.5, (740, 470, 860, 600)),
    "E-1": (12.0, (690, 520, 810, 660)), "E-2": (12.0, (710, 540, 830, 680)),
    "R-1": (12.0, (770, 550, 890, 690)), "R-2": (9.5, (780, 600, 900, 740)),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, face rows, face columns) on the cropped read-back."""
    size, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    raw, _, (bx, by) = regrid(np.asarray(Image.open(lp(os.path.join(SRC, f"udyr-model-{take}.png"))).convert("RGBA")),
                              size)
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    y0, x0 = ys.min(), xs.min()
    raw = raw[y0:ys.max() + 1, x0:xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    bx, by = np.asarray(bx), np.asarray(by)
    cell = lambda b, v: int(np.searchsorted(b, v, side="right")) - 1
    fr = range(cell(by, fy0) - y0, cell(by, fy1) - y0 + 1)
    fc = range(cell(bx, fx0) - x0, cell(bx, fx1) - x0 + 1)
    return raw, fr, fc


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


def joint(takes):
    """{take: (colour index map, shared palette)} with K colours over all the read-backs together."""
    raws = [read_back(t)[0] for t in takes]
    h = max(r.shape[0] for r in raws)
    both = np.zeros((h, sum(r.shape[1] for r in raws), 4), np.uint8)
    x = 0
    for r in raws:
        both[:r.shape[0], x:x + r.shape[1]] = r
        x += r.shape[1]
    idx, pal = recolour(both)
    out, x = {}, 0
    for t, r in zip(takes, raws):
        out[t] = (np.where(r[..., 3] > 0, idx[:r.shape[0], x:x + r.shape[1]], -1), pal)
        x += r.shape[1]
    return out


def cut(take, coloured=None):
    """The take at its count: (picture, rows kept, columns kept)."""
    raw, fr, fc = read_back(take)
    rows_to = ROWS[take[0]]
    idx, pal = coloured if coloured is not None else recolour(raw)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    a = ap.parse_args()
    if a.options:
        os.makedirs(lp(a.options), exist_ok=True)
        cells = [(t, cut(t)[0]) for t in DRAFTS]
        sheet(cells, os.path.join(a.options, "udyr_model_options.png"))
        for t, c in cells:
            Image.fromarray(c).save(lp(os.path.join(a.options, f"opt_{t}.png")))
            print(t, c.shape[1], "x", c.shape[0])
        return
    if not PICKS:
        sys.exit("no picks yet: run --options and ask the user")
    os.makedirs(lp(OUT), exist_ok=True)
    col = joint(list(PICKS.values()))
    for stance, take in PICKS.items():
        fig, rows, cols = cut(take, col[take])
        part = PART[stance]
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{part}.png")))
        Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{part}_4x.png")))
        print(part, take, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", max(rows) + 1)


if __name__ == "__main__":
    main()

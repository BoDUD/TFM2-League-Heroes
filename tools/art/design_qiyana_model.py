#!/usr/bin/env python3
"""Qiyana's step-1 designs (assets/source/qiyana/codex_model, 2026-10-22, Codex 2026-10-22/new-chat-3) read back on their
own grids and brought to the game's count: 60 rows from her crest's tip to her soles (40 game px at PPU 1.5, the user's
picks: 「40」, PPU 1.5, 3/4 only).

    python tools/art/design_qiyana_model.py --options DIR   # the candidates side by side
    python tools/art/design_qiyana_model.py                 # writes assets/source/qiyana/hd/idle.png

Codex's squares (asked 18 px; its HANDOFF: not one exact grid, semi-transparent edges): by the least read-back error
(sqfit: each square's spread round its median) A-1 reads 72 x 62 squares at 12.2-12.8 px (finer than asked: more of the
hair's locks and the jewellery), A-2 exactly 60 x 50 at 16.4-17.0 px. Each take is cut to the count the design-tryndamere
way (design_gnar_model's keep_axis): its own K colours (design_varus.kmeans), whole rows then columns dropped to the
count (least loss - a twin first - never the face's rows / columns: brows, eyes, the mouth), the width in proportion,
strips.complete_outline with the face kept.
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

SRC = os.path.join(ROOT, "assets", "source", "qiyana", "codex_model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "qiyana", "hd")
K = 40
PICKS = {"A": "A-1"}   # the user's pick, 2026-10-22: 「用 A-1」
PART = {"A": "idle"}
ROWS = {"A": 60}
# take -> (square px read at, the face's box on the raw canvas: x0, y0, x1, y1 - brows to the beard's end)
DRAFTS = {
    "A-1": (12.4, (690, 360, 910, 560)), "A-2": (16.4, (690, 360, 910, 545)),
}


# the face squares redrawn on the written design (codex-face-half-squares), after the pick: (x, y, colour) on
# hd/<part>.png. A-1's near eye came out eye-white + amber with no pupil (the far eye has one): its lower amber square
# made the dark pupil, so both eyes read amber with a pupil at 12x.
PUPIL = (95, 29, 14)
FACE = {"idle": [(31, 20, PUPIL)]}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, face rows, face columns) on the cropped read-back."""
    size, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    raw, _, (bx, by) = regrid(np.asarray(Image.open(lp(os.path.join(SRC, f"qiyana-model-{take}.png"))).convert("RGBA")),
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
        sheet(cells, os.path.join(a.options, "qiyana_model_options.png"))
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
        fig = fig.copy()
        for x, y, c in FACE.get(part, []):
            assert fig[y, x, 3] > 0, (part, x, y)
            fig[y, x, :3] = c
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{part}.png")))
        Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{part}_4x.png")))
        print(part, take, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", max(rows) + 1)


if __name__ == "__main__":
    main()

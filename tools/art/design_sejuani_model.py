#!/usr/bin/env python3
"""Sejuani's step-1 designs (assets/source/sejuani/codex_model/sejuani-model, 2026-10-24, Codex 2026-10-24/new-chat-4)
read back on their own grids and brought to the game's count: A (the idle) 54 rows from the tip of her helm's ice horn to
Bristle's hooves (36 game px at PPU 1.5, the user's picks 2026-10-24), B (the charge: the run and Q) 56 rows on A's
scale.

    python tools/art/design_sejuani_model.py --options DIR   # the candidates side by side
    python tools/art/design_sejuani_model.py                 # writes assets/source/sejuani/hd/{idle,run}.png
    python tools/art/design_sejuani_model.py --round 1 ...   # the first round (PPU 1.5, 54 / 56 rows)

Round 2 (the default): the user asked for a higher PPU after picking A-2 / B-1 (「先调高ppu像素吧」, PPU 2.0: A 72 rows,
B 76 on A's scale); Codex redrew the picked two finer (assets/source/sejuani/codex_redraw/sejuani-redraw, 2026-10-24,
asked 14 px squares, drawn on about A-1 11.5, A-2 10.4, B-1 11.4, B-2 9.5 by the edges' autocorrelation: 87-114 rows),
all cut to the count the same way. Round 1's face fixes (FACE) belong to round 1's picks.

Codex's squares (asked 18 px for both; its HANDOFF: no exact grid, soft alpha): by the period of the colour edges A-1
10.0, A-2 17.9, B-1 17.9, B-2 9.8 both ways - A-2 and B-1 on the asked grid (about 52 / 56 rows), A-1 and B-2 on a fine
one (about 94 / 99 rows) and cut to the count the design-tryndamere way (design_gnar_model's keep_axis): its own K
colours (design_varus.kmeans), whole rows then columns dropped to the count (least loss - a twin first - never the
face's rows / columns: her eyes and mouth), the width in proportion, strips.complete_outline with that box kept. A take
short of its count is kept as drawn (no rows invented). The horn's tip is the figure's first row.
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

SRC1 = os.path.join(ROOT, "assets", "source", "sejuani", "codex_model", "sejuani-model", "raw")
SRC2 = os.path.join(ROOT, "assets", "source", "sejuani", "codex_redraw", "sejuani-redraw", "raw")
SRC = SRC2
OUT = os.path.join(ROOT, "assets", "source", "sejuani", "hd")
K = 36
TOP_PX = 36      # game px from the ice horn's tip to the hooves (the user's pick)
PPU = 2.0
TOP_ROWS = round(TOP_PX * PPU)
B_ROWS = 76      # the charge on A's scale (round 1: hd/B 193 rows x 54 / 187 = 56; x 72 / 53 = 76)
PICK1 = {"idle": "A-2", "run": "B-1"}   # the user's round-1 picks, 2026-10-24
PICK = {"idle": "A-2", "run": "B-1"}    # round 2, the user's picks 2026-10-24
# take -> (file, square px read at, rows to (None: TOP_ROWS), the face box kept whole on the raw canvas: x0, y0, x1, y1)
DRAFTS1 = {
    "A-1": ("A-1", 10.2, None, (700, 420, 800, 545)),
    "A-2": ("A-2", 18.2, None, (690, 420, 820, 545)),
    "B-1": ("B-1", 18.2, 56, (840, 470, 1000, 600)),
    "B-2": ("B-2", 10.0, 56, (840, 500, 1000, 620)),
}
DRAFTS2 = {
    "A-1": ("A-1", 11.7, None, (670, 370, 810, 500)),
    "A-2": ("A-2", 10.6, None, (690, 360, 830, 490)),
    "B-1": ("B-1", 11.6, B_ROWS, (840, 400, 965, 500)),
    "B-2": ("B-2", 9.7, B_ROWS, (840, 410, 960, 510)),
}
DRAFTS = DRAFTS2
# the face squares redrawn on the written designs (codex-face-half-squares): name -> [(x, y, colour)]. The picked takes
# drew her face on few squares (the user picked them for their proportions, 2026-10-24): at 16x the near eye was a light
# square beside a dark one, the far eye a single blue square, a pink smear for the brow and no mouth. Redrawn from the
# take's own palette: the near eye 2x2 (a white highlight, a bright blue, two deep blue), the far eye 1x2 against the
# face's edge, dark brows above both, skin between them, a pink mouth square.
SKIN_I, SKIN_R = (216, 171, 124), (224, 191, 151)
FACE = {"idle": [(34, 11, (163, 198, 250)), (35, 11, (5, 167, 241)), (34, 12, (4, 67, 208)), (35, 12, (4, 67, 208)),
                 (38, 11, (5, 167, 241)), (38, 12, (4, 67, 208)), (35, 10, (81, 53, 39)), (36, 11, SKIN_I),
                 (36, 14, (211, 126, 113))],
        "run": [(44, 16, (249, 249, 250)), (45, 16, (4, 150, 248)), (44, 17, (0, 79, 243)), (45, 17, (0, 79, 243)),
                (47, 16, (4, 150, 248)), (47, 17, (0, 79, 243)), (44, 15, (48, 39, 37)), (45, 15, (48, 39, 37)),
                (47, 15, (48, 39, 37)), (46, 16, SKIN_R), (46, 19, (209, 118, 107))]}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, kept rows, kept columns) on the cropped read-back."""
    f, size, _, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"sejuani-{f}-original.png"))).convert("RGBA"))
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


def cut(take):
    """The take at its count: (picture, rows kept, columns kept, rows read)."""
    raw, fr, fc = read_back(take)
    idx, pal = dv.kmeans(raw, K)
    idx = np.where(raw[..., 3] > 0, idx, -1)
    H = idx.shape[0]
    rows_to = DRAFTS[take][2]
    if rows_to is None:   # the horn's tip is row 0: the whole figure is TOP_ROWS
        rows_to = TOP_ROWS
    fig, rows, cols = cut_to(raw, fr, fc, idx, pal, rows_to)
    return fig, rows, cols, H


def write(fig, name):
    Image.fromarray(fig).save(lp(os.path.join(OUT, f"{name}.png")))
    Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    ap.add_argument("--ppu", type=float, help="PPU to cut at (default PPU)")
    ap.add_argument("--round", type=int, default=2)
    a = ap.parse_args()
    if a.round == 1:
        global SRC, DRAFTS, PICK, TOP_ROWS, FACE
        SRC, DRAFTS, PICK, TOP_ROWS = SRC1, DRAFTS1, PICK1, round(TOP_PX * 1.5)
    else:
        FACE = {"idle": [], "run": []}
    if a.ppu:
        TOP_ROWS = round(TOP_PX * a.ppu)
    if a.options:
        os.makedirs(lp(a.options), exist_ok=True)
        cells = []
        for t in DRAFTS:
            fig, rows, cols, H = cut(t)
            cells.append((t, fig))
            Image.fromarray(fig).save(lp(os.path.join(a.options, f"opt_{t}.png")))
            print(t, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)
        sheet(cells, os.path.join(a.options, "sejuani_model_options.png"))
        return
    if not all(PICK.values()):
        sys.exit("no pick yet: run --options and ask the user")
    os.makedirs(lp(OUT), exist_ok=True)
    for name, take in PICK.items():
        fig, rows, cols, H = cut(take)
        fig = fig.copy()
        for x, y, c in FACE[name]:
            assert fig[y, x, 3] > 0, (x, y)
            fig[y, x, :3] = c
        write(fig, name)
        print(name, take, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)

if __name__ == "__main__":
    main()

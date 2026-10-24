#!/usr/bin/env python3
"""Bel'Veth's step-1 designs (assets/source/belveth/codex_model/belveth-model, 2026-10-24, Codex 2026-10-24/new-chat)
read back on their own grids and brought to the game's count: 82 rows from the shoulder-spike tips to the lowest claw (40
game px head to claws at PPU 1.75, the user's pick: A wings folded / 40 / PPU 1.75; the spikes add 12 rows above the head).

    python tools/art/design_belveth_model.py --options DIR   # the candidates side by side (cut to 82 rows, and as drawn)
    python tools/art/design_belveth_model.py                 # writes assets/source/belveth/hd/idle.png

Codex's squares (asked 14 px; its HANDOFF: no exact grid, soft alpha), by the FFT of the colour edges: A-1 ~9.8 (~116
rows), A-2 ~11.2 (~102 rows) - both drawn finer than asked, so both pass 82 rows: "as drawn" keeps every row (more
squares: a higher PPU at 40 game px). A cut take loses rows the design-tryndamere way (design_gnar_model's keep_axis):
its own K colours (design_varus.kmeans), whole rows then columns dropped to the count (least loss - a twin first - never
in the face box: the crest, the eyes and the chin), the width in proportion, strips.complete_outline with that box kept.
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

SRC = os.path.join(ROOT, "assets", "source", "belveth", "codex_model", "belveth-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "belveth", "hd")
K = 36
ROWS = 82    # 40 game px x PPU 1.75 head to claws + the shoulder spikes above (their tips the first row)
PICK = "A-1"   # the user's pick 2026-10-24 (both eyes clear): 82 rows, 40 game px head to claws at PPU 1.77 (1.75 asked)
# take -> (file, square px read at (a little above the measured square), rows to, the box kept whole on the raw canvas)
DRAFTS = {
    "A-1": ("A-1", 10.0, ROWS, (760, 250, 900, 400)),   # the crest, the eyes and the chin
    "A-1 as drawn": ("A-1", 10.0, 999, (760, 250, 900, 400)),
    "A-2": ("A-2", 11.4, ROWS, (740, 250, 880, 400)),
    "A-2 as drawn": ("A-2", 11.4, 999, (740, 250, 880, 400)),
}
# the face squares redrawn on the written design (codex-face-half-squares): (x, y, colour) on hd/idle.png
FACE = []


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, kept rows, kept columns) on the cropped read-back."""
    f, size, _, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"belveth-{f}.png"))).convert("RGBA"))
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
            Image.fromarray(fig).save(lp(os.path.join(a.options, f"opt_{t.replace(' ', '_')}.png")))
            print(t, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)
        sheet(cells, os.path.join(a.options, "belveth_model_options.png"))
        return
    if not PICK:
        sys.exit("no pick yet: run --options and ask the user")
    os.makedirs(lp(OUT), exist_ok=True)
    fig, rows, cols, H = cut(PICK)
    fig = fig.copy()
    for x, y, c in FACE:
        assert fig[y, x, 3] > 0, (x, y)
        fig[y, x, :3] = c
    write(fig, "idle")
    print("idle", PICK, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)


if __name__ == "__main__":
    main()

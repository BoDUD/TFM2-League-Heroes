#!/usr/bin/env python3
"""Azir's step-1 designs (assets/source/azir/codex_model/azir-model, 2026-10-23, Codex 2026-10-23/new-chat-4) read back
on their own grids and brought to the game's count: 57 rows from the top of his helmet's crest to his soles (the sceptre
rises above it), 38 game px at PPU 1.5 (the user's picks); the soldier T, the guard US and the Sun Disc D kept at what
Codex drew when it is at or under the asked count (T 54, US 48, D 72 rows).

    python tools/art/design_azir_model.py --options DIR   # the candidates side by side
    python tools/art/design_azir_model.py                 # writes assets/source/azir/hd/idle.png, soldier.png, guard.png, disc.png

Codex's squares (asked A 16, T 20, US 22, D 16 px; its HANDOFF: no exact grid, soft alpha), by the period of the colour
edges: A-1 ~14.4, A-2 ~15.7, T ~20.8, US ~26.3 (drawn coarser: 45 rows), D ~16.8; regrid is given a little above each.
A take is cut the design-tryndamere way (design_gnar_model's keep_axis): its own K colours (design_varus.kmeans), whole
rows then columns dropped to the count (least loss - a twin first - never the helmet's rows / columns: the crest, the
beak, the eye), the width in proportion, strips.complete_outline with that box kept. A take's count is found so the
crest top (the first row in the helmet's columns) to the soles is CREST_ROWS after the cut.
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

SRC = os.path.join(ROOT, "assets", "source", "azir", "codex_model", "azir-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "azir", "hd")
K = 40
CREST_ROWS = 57   # 38 game px x PPU 1.5, the helmet's crest to the soles
PICK = "A-2"      # the user's pick, 2026-10-23: A-2, the summons as drawn
# take -> (file, square px read at, rows to (None: by CREST_ROWS), the box kept whole on the raw canvas: x0, y0, x1, y1)
DRAFTS = {
    "A-1": ("A-1", 15.0, None, (560, 270, 820, 560)),
    "A-2": ("A-2", 16.5, None, (590, 310, 840, 590)),
    "T": ("T", 21.5, 54, (500, 220, 660, 470)),
    "US": ("US", 27.0, 48, (610, 235, 785, 565)),
    "D": ("D", 17.5, 72, (517, 63, 784, 470)),
}
NAMES = {"T": "soldier", "US": "guard", "D": "disc"}
# helmet squares redrawn on the written design (codex-face-half-squares): (x, y, colour) on hd/idle.png
FACE = [(35, 28, (2, 188, 246))]   # A-2: the eye 2x2 (it came 1 teal + 1 white over a dark square)
# A-2's sceptre under his hand stepped a column right at the gem (rows 62-70: 「法杖要做直了啊 下面有点歪」): the shaft
# runs straight down column SHAFT[0] from SHAFT[1] to its foot, one square wide between outlines, its gem on GEM rows
SHAFT = (12, 48, 70, 57)  # column, first row, last row (the foot; its outline under it), first row it had drifted from
GEM = {63: (2, 209, 247), 64: (252, 252, 253), 65: (2, 188, 246)}


def straighten(fig):
    c, y0, y1, drift = SHAFT
    out = fig.copy()
    ink = out[y0, c - 1].copy()
    gold = out[y0 + 4, c].copy()
    for y in range(y0, y1 + 2):
        if y >= drift:
            out[y, c + 1:c + 4] = 0                 # the old shaft and its outline right of the line (nothing behind)
        out[y, c - 1] = ink
        out[y, c + 1] = ink
        out[y, c] = ink
        if y <= y1:
            out[y, c, :3] = GEM.get(y, gold[:3])
    out[y1 + 1, c - 1:c + 2] = 0
    out[y1 + 1, c] = ink
    return out


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, kept rows, kept columns) on the cropped read-back."""
    f, size, _, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"azir-model-{f}.png"))).convert("RGBA"))
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


def crest_to_soles(raw, fc, rows=None):
    """Rows from the first opaque row in the helmet's columns (the crest) to the soles."""
    top = min(int(np.nonzero(raw[:, c, 3] > 0)[0].min()) for c in fc if raw[:, c, 3].any())
    if rows is None:
        return raw.shape[0] - top
    return sum(1 for r in rows if r >= top)


def cut(take):
    """The take at its count: (picture, rows kept, columns kept, rows read)."""
    raw, fr, fc = read_back(take)
    idx, pal = dv.kmeans(raw, K)
    idx = np.where(raw[..., 3] > 0, idx, -1)
    H = idx.shape[0]
    rows_to = DRAFTS[take][2]
    if rows_to is None:   # the count that leaves CREST_ROWS from the crest to the soles
        rows_to = round(CREST_ROWS * H / crest_to_soles(raw, fc))
        for _ in range(6):
            _, rows, _ = cut_to(raw, fr, fc, idx, pal, rows_to)
            got = crest_to_soles(raw, fc, rows)
            if got == CREST_ROWS:
                break
            rows_to += CREST_ROWS - got
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
        sheet(cells, os.path.join(a.options, "azir_model_options.png"))
        return
    if not PICK:
        sys.exit("no pick yet: run --options and ask the user")
    os.makedirs(lp(OUT), exist_ok=True)
    fig, rows, cols, H = cut(PICK)
    fig = straighten(fig)
    for x, y, c in FACE:
        assert fig[y, x, 3] > 0, (x, y)
        fig[y, x, :3] = c
    write(fig, "idle")
    print("idle", PICK, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)
    for t, name in NAMES.items():
        fig, rows, _, H = cut(t)
        write(fig, name)
        print(name, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)


if __name__ == "__main__":
    main()

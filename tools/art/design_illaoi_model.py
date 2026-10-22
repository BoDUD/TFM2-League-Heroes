#!/usr/bin/env python3
"""Illaoi's step-1 designs (assets/source/illaoi/codex_model/illaoi-model, 2026-10-23, Codex 2026-10-22/new-chat-5) read
back on their own grids and brought to the game's count: 63 rows from the top of her hair bun to her soles (the idol
rises above it) and 66 from the tentacle's hook to its root (42 and 44 game px at PPU 1.5, the user's picks: 「俄洛伊发髻到
脚底 42 游戏像素，PPU 1.5，触手 44，只做四分之三侧面」).

    python tools/art/design_illaoi_model.py --options DIR   # the candidates side by side
    python tools/art/design_illaoi_model.py                 # writes assets/source/illaoi/hd/idle.png and tentacle.png

Codex's squares (asked 17 px; its HANDOFF: no exact grid, soft alpha, the soles off the layout), by a comb over the edge
profiles: A-1 ~14.7 (15.5 across), A-2 13.1, T 15.6 - all drawn finer than asked, so every take is cut to its count
the design-tryndamere way (design_gnar_model's keep_axis): its own K colours (design_varus.kmeans), whole rows then
columns dropped to the count (least loss - a twin first - never the face's rows / columns: the brows, the eyes, the
nose ring, the mouth; the tentacle's hook), the width in proportion, strips.complete_outline with that box kept. A take's
count is found so the bun top (the first row in the face's columns) to the soles is BUN_ROWS after the cut.
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

SRC = os.path.join(ROOT, "assets", "source", "illaoi", "codex_model", "illaoi-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "illaoi", "hd")
K = 40
BUN_ROWS = 63    # 42 game px x PPU 1.5, the bun's top to the soles
PICK = "A-2"     # the user's pick, 2026-10-23: 「俄洛伊用 A-2」
# take -> (file, square px read at, rows to (None: by BUN_ROWS), the box kept whole on the raw canvas: x0, y0, x1, y1)
DRAFTS = {
    "A-1": ("A-1", 14.7, None, (660, 230, 860, 400)),
    "A-2": ("A-2", 13.1, None, (640, 250, 840, 420)),
    "T": ("T", 15.6, 66, (410, 140, 670, 520)),
}
# the face squares redrawn on the written design (codex-face-half-squares): (x, y, colour) on hd/idle.png
CHEEK = (205, 121, 68)   # her lit cheek, cd7944
# A-2: the green smeared under both eyes back to skin (the prompt: the green only in the eyes)
FACE = [(30, 18, CHEEK), (31, 18, CHEEK), (32, 18, CHEEK), (37, 18, CHEEK)]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, kept rows, kept columns) on the cropped read-back."""
    f, size, _, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"illaoi-model-{f}.png"))).convert("RGBA"))
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


def bun_to_soles(raw, fc, rows=None):
    """Rows from the first opaque row in the face's columns (the bun) to the soles."""
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
    if rows_to is None:   # the count that leaves BUN_ROWS from the bun to the soles
        rows_to = round(BUN_ROWS * H / bun_to_soles(raw, fc))
        for _ in range(6):
            _, rows, _ = cut_to(raw, fr, fc, idx, pal, rows_to)
            got = bun_to_soles(raw, fc, rows)
            if got == BUN_ROWS:
                break
            rows_to += BUN_ROWS - got
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
        sheet(cells, os.path.join(a.options, "illaoi_model_options.png"))
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
    fig, rows, _, H = cut("T")
    write(fig, "tentacle")
    print("tentacle", fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)


if __name__ == "__main__":
    main()

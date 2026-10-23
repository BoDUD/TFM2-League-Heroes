#!/usr/bin/env python3
"""Aurora's step-1 designs (assets/source/aurora/codex_model/aurora-model, 2026-10-23, Codex 2026-10-23/new-chat-2) read
back on their own grids and brought to the game's count: 57 rows from the top of her hat's crown to her soles (the
rabbit ears rise above it; 38 game px at PPU 1.5, the user's picks: hat top to soles 38, PPU 1.5, 3/4 only).

    python tools/art/design_aurora_model.py --options DIR   # the candidates side by side
    python tools/art/design_aurora_model.py                 # writes assets/source/aurora/hd/idle.png

Codex's squares (asked 16 px; its HANDOFF: no exact grid, soft alpha, the glasses' frames drawn finer than a square):
read where columns and rows come out the same size - A-1 on 19 px peaks (15.9 / 15.8 px, 42x77), A-2 on 17 (15.2 /
15.5, 40x75) - then every take is cut to its count the design-tryndamere way (design_gnar_model's keep_axis): its own K
colours (design_varus.kmeans), whole rows then columns dropped to the count (least loss - a twin first - never the
face's rows / columns: the glasses, the eyes, the mouth), the width in proportion, strips.complete_outline with that box
kept. A take's count is found so the hat's top (the first row with the hat's teal) to the soles is HAT_ROWS after the cut.
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

SRC = os.path.join(ROOT, "assets", "source", "aurora", "codex_model", "aurora-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "aurora", "hd")
K = 40
HAT_PX = 38      # game px from the hat crown's top to the soles (the user's pick)
PPU = 2.25       # the user: 「太模糊了 用PPU调下像素」, then A-2 at 2.25 (PPU 1.5 read the takes far too coarse)
HAT_ROWS = round(HAT_PX * PPU)
PICK = "A-2"     # the user's pick, 2026-10-23
# take -> (file, square px read at, rows to (None: by HAT_ROWS), the face box kept whole on the raw canvas: x0, y0, x1, y1)
# Read on Codex's FINE squares (its glasses, eyes and trim are drawn on about half its 16 px squares): A-1 on 9.5 px
# peaks (9.5 across, 10.9 down: 70x112, hat to soles 91), A-2 on 11 (10.8 / 10.6: 56x109, 90).
DRAFTS = {
    "A-1": ("A-1", 9.5, None, (580, 500, 780, 650)),
    "A-2": ("A-2", 11, None, (570, 470, 770, 610)),
}
# the face squares redrawn on the written design (codex-face-half-squares): (x, y, colour) on hd/idle.png
# A-2 at PPU 2.25: the far eye (behind the far lens, cols 35-36) sat a row above the near one (rows 41-43 against 42-44)
# and was one column of navy - redrawn like the near eye: the lash row 41, navy 2x2 on rows 42-43 with the highlight on
# its lower right, the bright blue row 44.
LASH, NAVY, HI, BLUE = (13, 2, 25), (19, 9, 132), (220, 244, 252), (48, 57, 238)
FACE = [(35, 41, LASH), (36, 41, LASH), (35, 42, NAVY), (36, 42, NAVY), (35, 43, NAVY), (36, 43, HI),
        (35, 44, BLUE), (36, 44, BLUE)]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, kept rows, kept columns) on the cropped read-back."""
    f, size, _, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"aurora-model-{f}.png"))).convert("RGBA"))
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


def hat_top(raw):
    """The first row with the hat's teal (the crown; the ears above it are orange and pink)."""
    c = raw[..., :3].astype(int)
    teal = (raw[..., 3] > 0) & (c[..., 1] > c[..., 0] + 25) & (c[..., 2] > c[..., 0] + 15) & (c[..., 1] > 60)
    rows = np.nonzero(teal.sum(axis=1) >= 2)[0]
    return int(rows.min())


def hat_to_soles(raw, rows=None):
    """Rows from the hat's top to the soles (of the kept rows)."""
    top = hat_top(raw)
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
    if rows_to is None:   # the count that leaves HAT_ROWS from the hat's top to the soles
        rows_to = round(HAT_ROWS * H / hat_to_soles(raw))
        for _ in range(6):
            _, rows, _ = cut_to(raw, fr, fc, idx, pal, rows_to)
            got = hat_to_soles(raw, rows)
            if got == HAT_ROWS:
                break
            rows_to += HAT_ROWS - got
    fig, rows, cols = cut_to(raw, fr, fc, idx, pal, rows_to)
    return fig, rows, cols, H


def write(fig, name):
    Image.fromarray(fig).save(lp(os.path.join(OUT, f"{name}.png")))
    Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    ap.add_argument("--ppu", type=float, help="PPU to cut at (default PPU)")
    a = ap.parse_args()
    if a.ppu:
        global HAT_ROWS
        HAT_ROWS = round(HAT_PX * a.ppu)
    if a.options:
        os.makedirs(lp(a.options), exist_ok=True)
        cells = []
        for t in DRAFTS:
            fig, rows, cols, H = cut(t)
            cells.append((t, fig))
            Image.fromarray(fig).save(lp(os.path.join(a.options, f"opt_{t}.png")))
            print(t, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)
        sheet(cells, os.path.join(a.options, "aurora_model_options.png"))
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

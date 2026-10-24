#!/usr/bin/env python3
"""Kled's step-1 designs (assets/source/kled/codex_model/kled-model, 2026-10-24, Codex 2026-10-24/new-chat-8) read back
on their own grids and brought to the game's count: A (mounted on Skaarl: idle, run, every mounted action) 80 rows from
the tip of his hat spike to Skaarl's claws (40 game px at PPU 2.0, the user's picks 2026-10-24), B (on foot with the
axe: the dismounted idle, run, attack and Pocket Pistol) 58 rows on A's scale.

    python tools/art/design_kled_model.py --options DIR   # the candidates side by side
    python tools/art/design_kled_model.py                 # writes assets/source/kled/hd/{idle,foot}.png

Codex's squares (asked 14 px for both; its HANDOFF: no exact grid, soft alpha, the second round's four takes kept): by
the period of the colour edges A-1 11-12, A-2 11-12, B-1 16-17, B-2 13-14 both ways - A-1 / A-2 on a finer grid (about
95 rows) and B-2 (about 59) cut to the count the design-tryndamere way (design_gnar_model's keep_axis): its own K colours
(design_varus.kmeans), whole rows then columns dropped to the count (least loss - a twin first - never the face's rows /
columns: his eyes, the scar, the grin), the width in proportion, strips.complete_outline with that box kept. A take short
of its count (B-1, about 53 rows on 16 px) is kept as drawn (no rows invented). The hat spike's tip is the figure's
first row.
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

SRC = os.path.join(ROOT, "assets", "source", "kled", "codex_model", "kled-model")
OUT = os.path.join(ROOT, "assets", "source", "kled", "hd")
K = 36
TOP_PX = 40      # game px from the hat spike's tip to Skaarl's claws (the user's pick)
PPU = 2.0
TOP_ROWS = round(TOP_PX * PPU)
B_ROWS = 58      # on foot on A's scale (hd/B 177 rows x 80 / 244)
PICK = {"idle": "A-1", "foot": "B-1"}   # the user's picks, 2026-10-24
# take -> (file, square px read at, rows to (None: TOP_ROWS), the face box kept whole on the raw canvas: x0, y0, x1, y1:
# both eyes, the scar and the grin)
DRAFTS = {
    "A-1": ("A-1", 11.7, None, (540, 370, 720, 500)),
    "A-2": ("A-2", 11.7, None, (540, 380, 720, 505)),
    "B-1": ("B-1", 16.4, B_ROWS, (490, 690, 670, 800)),
    "B-2": ("B-2", 13.8, B_ROWS, (485, 665, 650, 780)),
}
FACE = {"idle": [], "foot": []}
# One face in all frames (the user's picks: A-1 + B-1, 2026-10-24): B-1 was drawn on 16 px squares, 52 rows, its head
# 30 rows to A-1's 38 and its eyes one square each. Its head is taken off (HEAD_B, a polygon on the read-back) and A-1's
# (HEAD_A: hat spike, both ears, the flaps, the beard) put on with the beard's tip on B's (CHIN: A -> B), the outline
# closed after: 60 rows, about the 58 that A's scale asks.
HEAD_A = [(3, 13), (12, 12), (16, 10), (22, 6), (28, 0), (31, 0), (34, 7), (38, 8), (40, 12), (42, 14), (42, 26),
          (40, 30), (38, 36), (35, 39), (26, 39), (22, 37), (21, 35), (19, 33), (15, 33), (12, 28), (3, 16)]
HEAD_B = [(0, 11), (8, 10), (12, 6), (19, 0), (22, 0), (25, 6), (27, 7), (29, 11), (31, 13), (31, 20), (29, 24),
          (27, 27), (26, 30), (19, 31), (16, 28), (13, 27), (10, 25), (7, 22), (0, 14)]
CHIN = ((31, 38), (23, 30))


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(take):
    """(1 px a square, kept rows, kept columns) on the cropped read-back."""
    f, size, _, (fx0, fy0, fx1, fy1) = DRAFTS[take]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"kled-{f}.png"))).convert("RGBA"))
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
    if rows_to is None:   # the spike's tip is row 0: the whole figure is TOP_ROWS
        rows_to = TOP_ROWS
    fig, rows, cols = cut_to(raw, fr, fc, idx, pal, rows_to)
    return fig, rows, cols, H


def polygon(shape, pts):
    im = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon(pts, fill=1)
    return np.asarray(im).astype(bool)


def head_swap(foot, idle):
    """B's body under A's head (HEAD_A / HEAD_B / CHIN above)."""
    (ax, ay), (bx, by) = CHIN
    dx, dy = bx - ax, by - ay
    ma = polygon(idle.shape, HEAD_A) & (idle[..., 3] > 0)
    mb = polygon(foot.shape, HEAD_B) & (foot[..., 3] > 0)
    ys, xs = np.nonzero(ma)
    top, left = max(0, -(ys.min() + dy)), max(0, -(xs.min() + dx))
    right = max(0, xs.max() + dx + 1 - foot.shape[1])
    can = np.zeros((foot.shape[0] + top, foot.shape[1] + left + right, 4), np.uint8)
    can[top:, left:left + foot.shape[1]] = foot
    yb, xb = np.nonzero(mb)
    can[yb + top, xb + left] = 0
    can[ys + dy + top, xs + dx + left] = idle[ys, xs]
    pad = np.pad(can, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=PD.edge_colour(foot), feet=pad.shape[0] - 1)
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


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
        sheet(cells, os.path.join(a.options, "kled_model_options.png"))
        return
    if not all(PICK.values()):
        sys.exit("no pick yet: run --options and ask the user")
    os.makedirs(lp(OUT), exist_ok=True)
    figs = {}
    for name, take in PICK.items():
        fig, rows, cols, H = cut(take)
        if name == "foot":
            fig = head_swap(fig, figs["idle"])
        fig = fig.copy()
        for x, y, c in FACE[name]:
            assert fig[y, x, 3] > 0, (x, y)
            fig[y, x, :3] = c
        figs[name] = fig
        write(fig, name)
        print(name, take, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)

if __name__ == "__main__":
    main()

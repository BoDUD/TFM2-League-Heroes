#!/usr/bin/env python3
"""Shyvana's step-1 designs (assets/source/shyvana/codex_model, 2026-10-21, Codex new-chat-2) read back on their own
grids and brought to the game's count: her 63 rows from her horn tips to her soles, the dragon 72 from its highest wing
tip (42 / 48 game px at PPU 1.5, the user's sizes: 「人42 龙48 PPU1.5」).

    python tools/art/design_shyvana_model.py --options DIR   # the candidates side by side
    python tools/art/design_shyvana_model.py                 # writes assets/source/shyvana/hd/{idle,d_idle,...}.png

Codex's squares (regrid's, the outline steps at 3x agree; asked A / SA 17 px, D 10, SD 8): A-1 16 px (79 rows), A-2
18 px (67), SA 14 px (88), D-1 11 px (64), D-2 12 px (65), SD 10 px (66). Each read back with regrid at its own size
(alpha >= 128); then, the design-tryndamere way (design_gnar_model's): its own K colours (design_varus.kmeans), whole
rows then columns dropped to the count (keep_axis: least loss, never the eyes' rows / columns), the width in
proportion, strips.complete_outline with the face kept. The dragons came SHORT of 72 rows (64-66): a design is never
blown up (the squares would double), so they are kept as drawn - 43-44 game px at PPU 1.5, not 48 (the user: keep
the dragon as drawn; 3/4 views only, no side-on designs). The written set shares one palette (K colours by k-means over the picks' read-backs together).
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

SRC = os.path.join(ROOT, "assets", "source", "shyvana", "codex_model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "shyvana", "hd")
K = 40
PICKS = {"idle": "A-2", "d_idle": "D-1"}   # the user's picks, 2026-10-21: 「人形用 A-2，龙形用 D-1，龙就按画的大小，只做四分之三侧面」
# label -> (draft, Codex's square px, rows wanted or None = as drawn, eye rows, eye columns) on its own read-back
DRAFTS = {
    "A-1": ("A-1", 16.0, 63, range(15, 23), range(27, 43)),
    "A-2": ("A-2", 18.0, 63, range(13, 22), range(23, 36)),
    "A-2 drawn": ("A-2", 18.0, None, None, None),
    "SA": ("SA", 14.0, 63, range(21, 29), range(30, 45)),
    "D-1": ("D-1", 11.0, None, None, None),
    "D-2": ("D-2", 12.0, None, None, None),
    "SD": ("SD", 10.0, None, None, None),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(name):
    draft, size = DRAFTS[name][:2]
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, f"shyvana-model-{draft}.png"))).convert("RGBA")),
                       size)
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


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


def joint(names):
    """{name: (colour index map, shared palette)} with K colours over all the read-backs together."""
    raws = [read_back(n) for n in names]
    h = max(r.shape[0] for r in raws)
    both = np.zeros((h, sum(r.shape[1] for r in raws), 4), np.uint8)
    x = 0
    for r in raws:
        both[:r.shape[0], x:x + r.shape[1]] = r
        x += r.shape[1]
    idx, pal = recolour(both)
    out, x = {}, 0
    for n, r in zip(names, raws):
        out[n] = (np.where(r[..., 3] > 0, idx[:r.shape[0], x:x + r.shape[1]], -1), pal)
        x += r.shape[1]
    return out


def cut(name, coloured=None):
    """The draft at the count: (picture, rows kept, columns kept)."""
    _, _, rows_to, fr, fc = DRAFTS[name]
    idx, pal = coloured if coloured is not None else recolour(read_back(name))
    H, W = idx.shape
    if rows_to is None or rows_to >= H:
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
        cells = [(n, cut(n)[0]) for n in DRAFTS]
        sheet(cells, os.path.join(a.options, "shyvana_model_options.png"))
        for n, c in cells:
            Image.fromarray(c).save(lp(os.path.join(a.options, f"opt_{n.replace(' ', '_')}.png")))
            print(n, c.shape[1], "x", c.shape[0])
        return
    if not PICKS:
        sys.exit("no picks yet: run --options and ask the user")
    os.makedirs(lp(OUT), exist_ok=True)
    col = joint(list(PICKS.values()))
    for part, name in PICKS.items():
        fig, rows, cols = cut(name, col[name])
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{part}.png")))
        Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{part}_4x.png")))
        print(part, name, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", max(rows) + 1)


if __name__ == "__main__":
    main()

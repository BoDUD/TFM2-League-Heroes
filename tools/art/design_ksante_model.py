#!/usr/bin/env python3
"""K'Sante's step-1 designs (assets/source/ksante/codex_model, 2026-10-22, Codex 2026-10-22/new-chat) read back on their
own grids and brought to the game's count: 72 rows from the ntofo tops to the soles in the base stance, 73 in All Out
(48 / ~49 game px at PPU 1.5, the user's picks: 「陀斧顶到脚底 48 游戏像素，PPU 1.5，只做四分之三侧面」).

    python tools/art/design_ksante_model.py --options DIR   # the candidates side by side
    python tools/art/design_ksante_model.py                 # writes assets/source/ksante/hd/{idle,ao_idle}.png

Codex's squares (asked A 15 px / O 11 px; its HANDOFF: A-1 ~15.3, A-2 ~17, O ~9.8, not on one exact grid): the size
whose read-back differs least from the raw within each square (C:/t/ks_work/sqfit.py; regrid snaps to the drawn edges,
so the size only fills the gaps) - A-1 / A-2 15 px (80 rows), O-1 / O-2 9.6 px (81 rows). All four came TALLER than the
count, so each is cut, the design-tryndamere way (design_gnar_model's): its own K colours (design_varus.kmeans), whole
rows then columns dropped to the count (keep_axis: least loss, never the face's rows / columns - brows, eyes, the mouth
and the teeth), the width in proportion, strips.complete_outline with the face kept. The written set shares one
palette (K colours by k-means over the picks' read-backs together).
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

SRC = os.path.join(ROOT, "assets", "source", "ksante", "codex_model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "ksante", "hd")
K = 40
PICKS = {}   # the user's picks: {"idle": "A-?", "ao_idle": "O-?"}
# label -> (draft, Codex's square px, rows wanted or None = as drawn, face rows, face columns) on its own read-back
DRAFTS = {
    "A-1": ("A-1", 15.0, 72, range(18, 29), range(30, 47)),
    "A-2": ("A-2", 15.0, 72, range(16, 26), range(30, 46)),
    "O-1": ("O-1", 9.6, 73, range(13, 24), range(60, 76)),
    "O-2": ("O-2", 9.6, 73, range(13, 24), range(60, 77)),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(name):
    draft, size = DRAFTS[name][:2]
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, f"ksante-model-{draft}.png"))).convert("RGBA")),
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
        sheet(cells, os.path.join(a.options, "ksante_model_options.png"))
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

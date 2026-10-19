#!/usr/bin/env python3
"""Yuumi's step-1 designs (assets/source/yuumi/codex_model, 2026-10-19, Codex new-chat-5) read back on their own grids
and brought to the game's count: A and S 48 rows orb top to the book's bottom (32 game px at PPU 1.5), L and R at A's
scale (their eye spacing matched to A's), B 21 rows (14 game px), C 38 columns (the book in A).

    python tools/art/design_yuumi_model.py --options DIR    # the candidates side by side (the user's pick)
    python tools/art/design_yuumi_model.py                  # writes assets/source/yuumi/hd/{idle,side,leap,ult,book}.png

Codex's squares (Fourier pitch of the colour edges across / down the figure; asked 22 / 44 / 30 px, every draft fills
its canvas instead): A-1 15.4 / 13.4, A-2 18.8 / 17.0, S-1 19.4 / 18.2, S-2 17.0 / 16.6, L-1 14.6 / 14.4, L-2 15.0 /
14.6, R-1 20.8 / 20.6, R-2 24.2 / 22.4, B-1 21 / 19.2, B-2 18.8 / 17.6, C-1 19.6 / 17.6 - each read back with regrid at
the mean. Then the design-tryndamere way: one K-colour palette (design_varus.kmeans), whole rows then columns dropped to
the count (design_zoe_model.keep_axis: least loss, never the face's rows / columns - the eyes found by their cyan,
the nose and mouth below), the width in proportion, strips.complete_outline with the face kept.
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
import design_zoe_model as Z  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yuumi", "codex_model", "yuumi-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "yuumi", "hd")
ROWS, B_ROWS, C_COLS, K = 48, 21, 38, 28
SQUARE = {"A-1": 14.4, "A-2": 17.9, "S-1": 18.8, "S-2": 16.8, "L-1": 14.5, "L-2": 14.8, "R-1": 20.7, "R-2": 23.3,
          "B-1": 20.1, "B-2": 18.2, "C-1": 18.6}
# the user's picks (2026-10-19); B (the ride) cut to 21 rows was muddy -> its own on-grid redraw pack (pack_yuumi_ride.py)
PICKS = {"idle": "A-2", "side": "S-1", "leap": "L-2", "ult": "R-2", "book": "C-1"}


def lp(path):
    return Z.lp(path)


def read_back(name):
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, f"yuumi-model-{name}.png"))).convert("RGBA")),
                       SQUARE[name])
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def eyes(raw):
    """The two cyan irises (the two biggest cyan blobs between 12 % and 55 % of the height - the orb above and the
    collar gem below are the same cyan): (rows, columns) of their box, and the distance between their centres."""
    from scipy import ndimage
    c = raw[..., :3].astype(int)
    H = raw.shape[0]
    m = (raw[..., 3] > 0) & (c[..., 2] > 200) & (c[..., 1] > 130) & (c[..., 0] < 90)
    m[:round(H * 0.12)] = False
    m[round(H * 0.55):] = False
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    keep = np.argsort(sizes)[::-1][:2] + 1
    ys, xs = np.nonzero(np.isin(lab, keep))
    cx = [np.nonzero(lab == k)[1].mean() for k in keep]
    gap = abs(cx[0] - cx[1]) if len(cx) == 2 else 0
    return range(ys.min(), ys.max() + 1), range(xs.min(), xs.max() + 1), gap


def face(raw):
    """Protected rows / columns: the eyes, a row above (the lashes), the nose and mouth below."""
    e = eyes(raw)
    if e is None:
        return None, None
    r, c, _ = e
    return range(max(0, r.start - 1), min(raw.shape[0], r.stop + 3)), range(max(0, c.start - 1), min(raw.shape[1], c.stop + 1))


def cut(raw, idx, pal, rows_to, cols_to=None):
    H, W = idx.shape
    fr, fc = face(raw)
    if rows_to < H:
        pr = fr if fr is not None else range(H // 2, H // 2 + 1)
        rows = [0] + [r + 1 for r in Z.keep_axis([idx[y] for y in range(1, H)], rows_to - 1,
                                                 range(pr.start - 1, pr.stop - 1))]
    else:
        rows = list(range(H))
    sub = idx[rows]
    want = cols_to or round(W * len(rows) / H)
    if want < W:
        pc = fc if fc is not None else range(W // 2, W // 2 + 1)
        cols = Z.keep_axis([sub[:, x] for x in range(W)], want, pc)
    else:
        cols = list(range(W))
    fig = Z.paint(idx[np.ix_(rows, cols)], pal)
    keep = np.zeros(fig.shape[:2], bool)
    if fr is not None:
        r_in = [rows.index(r) for r in fr if r in rows]
        c_in = [cols.index(c) for c in fc if c in cols]
        keep[min(r_in):max(r_in) + 1, min(c_in):max(c_in) + 1] = True
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def counts(raws):
    """Rows (or columns for C) wanted per draft: A / S fixed, L / R by eye spacing against the mean of the A drafts."""
    gapA = np.mean([eyes(raws[n])[2] * ROWS / raws[n].shape[0] for n in raws if n.startswith("A")])
    out = {}
    for n, r in raws.items():
        kind = n[0]
        if kind in "AS":
            out[n] = (ROWS, None)
        elif kind in "LR":
            # an eye hidden behind the book's edge (R-2: one blob found) -> the other take's scale of the same pose
            ok = [m for m in raws if m[0] == kind and eyes(raws[m])[2] >= 5]
            ref = n if n in ok else ok[0]
            out[n] = (round(r.shape[0] * raws[ref].shape[0] / r.shape[0] * gapA / eyes(raws[ref])[2]), None)
        elif kind == "B":
            out[n] = (B_ROWS, None)
        else:
            out[n] = (round(r.shape[0] * C_COLS / r.shape[1]), C_COLS)
    return out


def all_cuts(names):
    raws = {n: read_back(n) for n in names}
    h = max(r.shape[0] for r in raws.values())
    both = np.zeros((h, sum(r.shape[1] for r in raws.values()), 4), np.uint8)
    x, at = 0, {}
    for n, r in raws.items():
        both[:r.shape[0], x:x + r.shape[1]] = r
        at[n] = x
        x += r.shape[1]
    idx, pal = dv.kmeans(both, K)
    # the counts from every draft (the same as on the options sheet, whichever are picked)
    want = counts({n: (raws[n] if n in raws else read_back(n)) for n in SQUARE if n[0] != "C"} | {"C-1": read_back("C-1")})
    out = {}
    for n, r in raws.items():
        i = np.where(r[..., 3] > 0, idx[:r.shape[0], at[n]:at[n] + r.shape[1]], -1)
        out[n] = cut(r, i, pal, *want[n])
        print(n, "read back", r.shape[1], "x", r.shape[0], "->", out[n].shape[1], "x", out[n].shape[0])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    a = ap.parse_args()
    if a.options:
        os.makedirs(lp(a.options), exist_ok=True)
        cells = all_cuts(list(SQUARE))
        for n, c in cells.items():
            Image.fromarray(c).save(lp(os.path.join(a.options, f"opt_{n}.png")))
        Z.sheet(list(cells.items())[:6], os.path.join(a.options, "yuumi_model_options_1.png"))
        Z.sheet(list(cells.items())[6:], os.path.join(a.options, "yuumi_model_options_2.png"))
        return
    os.makedirs(lp(OUT), exist_ok=True)
    cells = all_cuts(list(PICKS.values()))
    for part, name in PICKS.items():
        fig = cells[name]
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{part}.png")))
        Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{part}_4x.png")))


if __name__ == "__main__":
    main()

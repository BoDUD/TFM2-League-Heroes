#!/usr/bin/env python3
"""Azir's summons' Codex poses (assets/source/azir/codex_poses/azir-poses: s_lift s_stab - the sand soldier from the
front; g_push1 g_push2 - the Imperial Guard from the side facing right) read back on squares that give them their
designs' size, in their designs' colours.

    python tools/art/design_azir_summons.py --sheet DIR   # the designs and the poses side by side (6x)
    python tools/art/design_azir_summons.py               # writes assets/source/azir/hd/soldier_lift.png, soldier_stab.png,
                                                          # guard_push1.png, guard_push2.png

Codex drew them on ~21 px (the soldier) and ~22.5-24 px (the guard) squares, the soldier about a fifth bigger than its
design (helmet top to soles 55 rows on its own squares against hd/soldier.png's 45). regrid locks onto the drawn grid
whatever size it is given, so each is read on its own squares (SIZE) and then cut to its count the design-tryndamere way
(design_gnar_model.keep_axis: whole rows, then columns in proportion, the cheapest first, never the helmet's): the soldier's
two by one factor (45 / 55: s_lift's helmet to soles 45, s_stab crouched 44), g_push1 to 45 rows (shield top to the ground,
as hd/guard.png), g_push2 as drawn (45). Colours snapped to the design's (Lab), alpha 0/255, the outline closed.
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
import regrid as RG  # noqa: E402
from design_azir_hd import lp  # noqa: E402
from design_azir_poses import finish  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_gnar_model import keep_axis  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "azir", "codex_poses", "azir-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "azir", "hd")
# pose -> (square px Codex drew, the design it copies, the file written, the factor the rows are cut by, the helmet kept
# whole: rows and columns as fractions of the read-back)
SUMMONS = {"s_lift": (21.0, "soldier", "soldier_lift", 45 / 55, (0.0, 0.26), (0.30, 0.72)),
           "s_stab": (21.0, "soldier", "soldier_stab", 45 / 55, (0.0, 0.28), (0.30, 0.68)),
           "g_push1": (22.5, "guard", "guard_push1", 45 / 48, (0.12, 0.42), (0.32, 0.68)),
           "g_push2": (24.0, "guard", "guard_push2", 1.0, (0.12, 0.42), (0.32, 0.68))}


def read(name):
    size, design, _, factor, (r0, r1), (c0, c1) = SUMMONS[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"azir-pose-{name}.png"))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    ref = np.asarray(Image.open(lp(os.path.join(OUT, f"{design}.png"))).convert("RGBA"))
    d = snap(d, ref)
    if factor < 1:
        pal = {tuple(c): i for i, c in enumerate(np.unique(d[d[..., 3] > 0][:, :3], axis=0))}
        idx = np.full(d.shape[:2], -1, int)
        for (y, x) in zip(*np.nonzero(d[..., 3] > 0)):
            idx[y, x] = pal[tuple(d[y, x, :3])]
        H, W = idx.shape
        rows_to = round(H * factor)
        rows = keep_axis([idx[y] for y in range(H)], rows_to, range(int(H * r0), int(H * r1) + 1))
        sub = idx[rows]
        cols = keep_axis([sub[:, x] for x in range(W)], round(W * factor), range(int(W * c0), int(W * c1) + 1))
        d = d[np.ix_(rows, cols)]
    d = finish(d)
    ys, xs = np.nonzero(d[..., 3] > 0)
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    figs = {n: read(n) for n in SUMMONS}
    for n, f in figs.items():
        print(f"{n:8s} {f.shape[1]} x {f.shape[0]}")
    if a.sheet:
        z = 6
        tiles = [("soldier", np.asarray(Image.open(lp(os.path.join(OUT, "soldier.png"))).convert("RGBA")))]
        tiles += [(n, figs[n]) for n in ("s_lift", "s_stab")]
        tiles += [("guard", np.asarray(Image.open(lp(os.path.join(OUT, "guard.png"))).convert("RGBA")))]
        tiles += [(n, figs[n]) for n in ("g_push1", "g_push2")]
        W = sum(t.shape[1] * z + 12 for _, t in tiles)
        H = max(t.shape[0] for _, t in tiles) * z + 20
        sheet = Image.new("RGBA", (W, H), (200, 205, 195, 255))
        dr = ImageDraw.Draw(sheet)
        x = 0
        for n, t in tiles:
            sheet.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, z, 0), z, 1)), (x, H - t.shape[0] * z))
            dr.text((x + 2, 2), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(0, 0, 0, 255))
            x += t.shape[1] * z + 12
        os.makedirs(lp(a.sheet), exist_ok=True)
        sheet.convert("RGB").save(lp(os.path.join(a.sheet, "azir_summons.png")))
        return
    for n, f in figs.items():
        Image.fromarray(f).save(lp(os.path.join(OUT, f"{SUMMONS[n][2]}.png")))


if __name__ == "__main__":
    main()

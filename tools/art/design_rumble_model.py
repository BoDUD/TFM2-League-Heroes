#!/usr/bin/env python3
"""Rumble's step-1 designs (assets/source/rumble/codex_model/rumble-model, 2026-10-25) read back on their own grids and
brought to the game's count: 63 rows from the tip of his mohawk to the mech's red feet (36 game px at PPU 1.75).

    python tools/art/design_rumble_model.py --options DIR   # the candidates side by side, faces at 12x
    python tools/art/design_rumble_model.py                 # writes assets/source/rumble/hd/idle.png (PICK)

Codex's squares (asked 12 px; its HANDOFF: no exact grid, soft alpha; the final round edited 2_target_B, the first
round's two takes - far finer, ~5-7 px - kept in raw/ and not read): by regrid B-1 12 px (62 rows x 92: kept as drawn,
no row invented), B-2 10 px (about 74 rows: cut to the count the design-kled-model way - its own K colours, whole rows
then columns dropped to the count, least loss first, never the face's rows / columns: both eyes, the nose, the grin;
the width in proportion, strips.complete_outline with that box kept). The mohawk's tip is the figure's first row.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_kled_model as KM  # noqa: E402
from design_gnar_model import sheet  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rumble", "codex_model", "rumble-model")
OUT = os.path.join(ROOT, "assets", "source", "rumble", "hd")
TOP_PX = 36      # game px from the mohawk's tip to the red feet
PPU = 1.75
TOP_ROWS = round(TOP_PX * PPU)
PICK = {"idle": "B-1"}   # 2026-10-25: B-1 (drawn on the 12 px grid, kept whole; B-2 lost 11 rows and its eyes to dashes)
# take -> (file, square px read at, rows to (None: TOP_ROWS), the face box kept whole on the raw canvas: x0, y0, x1, y1)
DRAFTS = {
    "B-1": ("B-1", 12.0, None, (560, 630, 790, 735)),
    "B-2": ("B-2", 10.0, None, (560, 640, 790, 745)),
}


def setup():
    """design_kled_model's read-back and cut, pointed at Rumble's takes."""
    KM.SRC = SRC
    KM.TOP_ROWS = TOP_ROWS
    KM.DRAFTS = {t: (f, s, r, box) for t, (f, s, r, box) in DRAFTS.items()}
    KM.K = 36
    real = KM.read_back

    def read_back(take):
        f, size, _, (fx0, fy0, fx1, fy1) = DRAFTS[take]
        a = np.asarray(Image.open(KM.lp(os.path.join(SRC, f"rumble-{f}.png"))).convert("RGBA"))
        raw, _, (bx, by) = KM.regrid(a, size)
        ys, xs = np.nonzero(raw[..., 3] >= 128)
        y0, x0 = ys.min(), xs.min()
        raw = raw[y0:ys.max() + 1, x0:xs.max() + 1].copy()
        raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
        bx, by = np.asarray(bx), np.asarray(by)
        cell = lambda b, v: int(np.searchsorted(b, v, side="right")) - 1
        fr = range(cell(by, fy0) - y0, cell(by, fy1) - y0 + 1)
        fc = range(cell(bx, fx0) - x0, cell(bx, fx1) - x0 + 1)
        return raw, fr, fc
    KM.read_back = read_back
    return real


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    a = ap.parse_args()
    setup()
    if a.options:
        os.makedirs(KM.lp(a.options), exist_ok=True)
        cells = []
        for t in DRAFTS:
            fig, rows, cols, H = KM.cut(t)
            cells.append((t, fig))
            Image.fromarray(fig).save(KM.lp(os.path.join(a.options, f"opt_{t}.png")))
            print(t, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)
        sheet(cells, os.path.join(a.options, "rumble_model_options.png"))
        return
    if not all(PICK.values()):
        sys.exit("no pick yet: run --options and ask the user")
    os.makedirs(KM.lp(OUT), exist_ok=True)
    for name, take in PICK.items():
        fig, rows, cols, H = KM.cut(take)
        Image.fromarray(fig).save(KM.lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(KM.lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, take, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", H)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Caitlyn's idle with the strips' shorter skirt: the design's hem a row higher, the lining and the thighs under it.

    python tools/art/fix_caitlyn_skirt.py [--check]

The design (assets/source/native/caitlyn_native.png, the user's pick "B42") ends its skirt in a gold hem 2 rows under
the pivot with the boots right below it; Codex's action strips drew the skirt shorter, a dark lining under it and 2-3
rows of navy tights before the boot cuffs. The run, rebuilt on the idle (tools/art/fix_caitlyn_run.py), carried the
design's skirt, so walking and attacking showed two lengths (the user: "凯特琳走路时和平A 放技能时 裙子长短不一样";
picked "统一成短裙"). Here the idle - six copies of the design, its pack's idle - is rebuilt from the design with
- row 1: the skirt's gold hem (the design's row 2) moved up a row, the rifle's stock (columns to -7) as it was;
- row 2: the lining (the darkest purple) across the skirt, the thighs' navy where they come out;
- row 3: the thighs only (navy, the near one widened to 3 squares), the stock's outline as it was;
everything else is the design's. import_native's COMPLETE closes the outline round the new rows.
Writes assets/source/native/caitlyn_idle.png (8x, the cells and pivots of caitlyn_cells.json); then run
tools/art/fix_caitlyn_run.py (the run's upper body is the idle's) and tools/art/import_native.py --hero caitlyn.
--check compares with the file instead of writing it.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from native_refs import Z, layout  # noqa: E402

NAT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NAT, "caitlyn_native.png")
OUT = os.path.join(NAT, "caitlyn_idle.png")
SOLES = 99                     # the design canvas: the soles' row, the middle of the feet on column 64
PAL = {"V": "23102D", "C": "1D1C34"}
STOCK = -7                     # the rifle's stock and its outline: columns up to here keep the design's rows
# rows 1-3 under the pivot, columns from -6 (None: the design's row `src` shifted, else these squares)
LINING = {2: (-6, "CCVVVVVVVCCC")}            # -6..+5: the near thigh, the lining, the far thigh
THIGHS = {3: [(-7, "CCC"), (3, "CCC")]}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def design_frame():
    """The design on its canvas, 1x, and its pivot (11 rows over the soles, the middle of the feet)."""
    a = np.asarray(Image.open(G.lp(DESIGN)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    return a, (64, SOLES - 11)


def shorten(a, pivot):
    px, py = pivot
    out = a.copy()
    right = slice(px + STOCK + 1, a.shape[1])
    out[py + 1, right] = a[py + 2, right]                   # the hem a row up
    out[py + 2, right] = 0
    out[py + 3, right] = 0
    x0, s = LINING[2]
    for k, ch in enumerate(s):
        out[py + 2, px + x0 + k, :3] = rgb(PAL[ch])
        out[py + 2, px + x0 + k, 3] = 255
    for x0, s in THIGHS[3]:
        for k, ch in enumerate(s):
            out[py + 3, px + x0 + k, :3] = rgb(PAL[ch])
            out[py + 3, px + x0 + k, 3] = 255
    return out


def build():
    cells = json.load(open(G.lp(os.path.join(NAT, "caitlyn_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    a, (dx, dy) = design_frame()
    a = shorten(a, (dx, dy))
    idle = cells["tags"]["idle"]
    cols, rows = layout(len(idle))
    sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    ys, xs = np.nonzero(a[..., 3])
    for k, c in enumerate(idle):
        px, py = c["pivot"]
        ox, oy = (k % cols) * cw, (k // cols) * ch
        for y, x in zip(ys, xs):
            sheet[oy + py + (y - dy), ox + px + (x - dx)] = a[y, x]
    return np.repeat(np.repeat(sheet, Z, 0), Z, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    big = build()
    if a.check:
        old = np.asarray(Image.open(G.lp(OUT)).convert("RGBA"))
        same = old.shape == big.shape and (old == big).all()
        print("identical" if same else "DIFFERENT", OUT)
        sys.exit(0 if same else 1)
    Image.fromarray(big, "RGBA").save(G.lp(OUT))
    print(OUT, big.shape[1], "x", big.shape[0])


if __name__ == "__main__":
    main()

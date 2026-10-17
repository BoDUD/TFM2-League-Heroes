#!/usr/bin/env python3
"""Kog'Maw's game-size design (step 1) from Codex's generator draft (assets/source/kogmaw/codex_model/raw).

    python tools/art/design_kogmaw.py --base             # print the read-back as letters (row/column numbers)
    python tools/art/design_kogmaw.py --cuts OUT_DIR     # the size options for the user (PNGs + letter files)
    python tools/art/design_kogmaw.py --final            # the approved letter grid (FINAL) -> assets/source/native

How it came about (2026-10-09): the user picked Codex's picture A (League's idle: squatting on two big feet, the skull
face and the fanged mouth to the viewer). Codex's step 1 drew a generator draft of ~18 px squares
(kogmaw_design_1_final_raw.png) and sampled it itself (its 38/34-row versions: broken feet, gaps in the outline).
Here, as for league_rengar:
  1. read back on its own grid (the skill's regrid.py) - 44 x 47;
  2. every square to the nearest of PAL (CIELAB) - the draft's own colours;
  3. whole rows and columns deleted EVENLY per part to the size the user picks (never two neighbours, never the
     face's rows and columns, the soles kept);
  4. strips.complete_outline; 5. on the 128 x 128 canvas: the soles on row 99, the middle of the feet on column 64.
The user picked 38 rows x 43 columns (「38 行 × 43 列」, 2026-10-09; options 44 / 40 / 38 / 34); after the strips and effects
were in, 「大嘴的模型可以缩小一点」 -> 34s (34 x 41: the mouth's lower rows and the skull's right side give too) - FINAL.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips  # noqa: E402
from regrid import regrid  # noqa: E402
import design_rengar as R  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "kogmaw", "codex_model", "raw", "kogmaw_design_1_final_raw.png")
FINAL = os.path.join(ROOT, "assets", "source", "kogmaw", "design", "kogmaw_design.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "kogmaw_native.png")

PAL = {
    "0": "#030312",   # outline
    "a": "#130B0A",   # dark line in the bone
    "c": "#FDEEC9",   # bone light
    "b": "#E7C18D",   # bone mid
    "d": "#BC9972",   # bone dark
    "w": "#FCFBFC",   # the eyes' glint
    "B": "#1A83FD",   # shell light
    "C": "#1931EA",   # shell mid
    "H": "#155FFC",   # shell between
    "T": "#00E4FD",   # antenna tip cyan
    "p": "#D2E2FC",   # antenna base, pale
    "t": "#15979F",   # teal light
    "u": "#025A6B",   # teal dark
    "q": "#440917",   # throat darkest
    "r": "#600125",   # crimson dark
    "R": "#950132",   # crimson mid
    "s": "#FB124C",   # crimson light
    "o": "#FD5001",   # the eyes (amber-orange)
    "y": "#A3A708",   # olive rim
    "z": "#404805",   # olive dark
}
RGB = {k: R.hx(v) for k, v in PAL.items()}


def letters(a):
    keys = list(PAL)
    pl = R.lab(np.array([RGB[k] for k in keys]))
    near = ((R.lab(a[..., :3])[..., None, :] - pl[None, None]) ** 2).sum(-1).argmin(-1)
    return ["".join(keys[near[y, x]] if a[y, x, 3] >= 128 else " " for x in range(a.shape[1]))
            for y in range(a.shape[0])]


def to_rgba(rows):
    a = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch not in " .":
                a[y, x, :3] = RGB[ch]
                a[y, x, 3] = 255
    return a


def from_rgba(a):
    inv = {v: k for k, v in RGB.items()}
    return ["".join(inv[tuple(int(v) for v in a[y, x, :3])] if a[y, x, 3] else " " for x in range(a.shape[1]))
            for y in range(a.shape[0])]


def close_outline(a):
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    p, _, _ = strips.complete_outline(p, color=RGB["0"], feet=a.shape[0], keep=None)
    return R.crop(p)


def base():
    raw, _, _ = regrid(np.asarray(Image.open(R.lp(RAW)).convert("RGBA")))
    return letters(raw)


def show(rows):
    print("    " + "".join(str(x // 10) for x in range(len(rows[0]))))
    print("    " + "".join(str(x % 10) for x in range(len(rows[0]))))
    for y, r in enumerate(rows):
        print(f"{y:3d} {r}")


FACE_ROWS, FACE_COLS = set(range(19, 36)), set(range(26, 47))
HARD_ROWS = {42, 43}
WEIGHT = {"o": 20, "w": 20, "T": 6, "s": 4, "y": 3, "t": 2, "p": 3}
# size options: name -> (row parts, column parts) as (first, last, deletions)
CUTS = {
    "44": ([], []),
    "40": ([(0, 14, 3), (36, 41, 1)], [(1, 25, 3)]),
    "38": ([(0, 14, 4), (16, 18, 1), (36, 41, 1)], [(1, 25, 4)]),
    "34": ([(0, 14, 7), (16, 18, 1), (36, 41, 2)], [(1, 25, 5)]),
    # the user, 2026-10-09: 「大嘴的模型可以缩小一点」 - the eyes' rows (19-24) and columns (28-37, 43-46) kept, the
    # mouth's lower rows and the skull's right side give a little too (antennae alone squashed the 34 above)
    "36s": ([(0, 14, 4), (16, 18, 1), (26, 33, 2), (36, 41, 1)], [(1, 25, 4), (38, 42, 1)],
            {19, 20, 21, 22, 23, 24, 42, 43}, set(range(28, 38)) | {43, 44, 45, 46}),
    "34s": ([(0, 14, 5), (16, 18, 1), (26, 33, 3), (36, 41, 1)], [(1, 25, 5), (38, 42, 1)],
            {19, 20, 21, 22, 23, 24, 42, 43}, set(range(28, 38)) | {43, 44, 45, 46}),
}


def cut(rows, row_parts, col_parts, hard_rows=None, hard_cols=None):
    R.JITTER = 1
    idx = np.array([[ord(c) for c in r.ljust(len(rows[0]))] for r in rows])
    w = np.vectorize(lambda v: WEIGHT.get(chr(v), 1))(idx)
    H, W = idx.shape
    dr = []
    for lo, hi, q in row_parts:
        dr += R.even_drop([idx[y] for y in range(H)], [w[y] for y in range(H)], lo, hi, q,
                          HARD_ROWS | FACE_ROWS if hard_rows is None else hard_rows)
    kr = [y for y in range(H) if y not in dr]
    sub, ws = idx[kr], w[kr]
    dc = []
    for lo, hi, q in col_parts:
        dc += R.even_drop([sub[:, x] for x in range(W)], [ws[:, x] for x in range(W)], lo, hi, q,
                          FACE_COLS if hard_cols is None else hard_cols)
    kc = [x for x in range(W) if x not in dc]
    return ["".join(chr(v) for v in r) for r in sub[:, kc]], dr, dc


def on_canvas(fig):
    fig = R.crop(fig)
    feet = np.nonzero((fig[-3:, :, 3] > 0).any(0))[0]
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = R.SOLE_ROW + 1 - fig.shape[0], int(round(R.MID_COL - (feet.min() + feet.max()) / 2))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def options(out_dir):
    b = base()
    figs = {}
    for name, spec in CUTS.items():
        rows, dr, dc = cut(b, *spec)
        fig = close_outline(to_rgba(rows))
        figs[name] = fig
        Image.fromarray(fig).save(os.path.join(out_dir, f"kogmaw_cut{name}.png"))
        with open(os.path.join(out_dir, f"kogmaw_cut{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(from_rgba(fig)) + "\n")
        print(f"{name}: {fig.shape[0]} x {fig.shape[1]}  rows dropped {dr}  cols dropped {dc}")
    return figs


def write_letters(can, path):
    ys, xs = np.nonzero(can[..., 3] > 0)
    x0 = xs.min()
    inv = {v: k for k, v in RGB.items()}
    os.makedirs(os.path.dirname(R.lp(path)), exist_ok=True)
    with open(R.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# x0 {x0}\n")
        for y in range(ys.min(), ys.max() + 1):
            f.write(f"{y:3d}" + "".join(inv[tuple(int(v) for v in can[y, x, :3])] if can[y, x, 3] else " "
                                        for x in range(x0, xs.max() + 1)).rstrip() + "\n")


def read_letters(path):
    can = np.zeros((128, 128, 4), np.uint8)
    x0 = 0
    for line in open(R.lp(path), encoding="utf-8"):
        line = line.rstrip("\r\n")
        if line.startswith("# x0"):
            x0 = int(line.split()[2])
            continue
        if len(line) < 4 or not line[:3].strip().isdigit():
            continue
        y = int(line[:3])
        for i, ch in enumerate(line[3:]):
            if ch not in " .":
                can[y, x0 + i, :3] = RGB[ch]
                can[y, x0 + i, 3] = 255
    return can


def rebuild(name="34s"):
    rows, _, _ = cut(base(), *CUTS[name])
    return on_canvas(close_outline(to_rgba(rows)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", action="store_true")
    ap.add_argument("--cuts", metavar="OUT_DIR")
    ap.add_argument("--final", action="store_true", help="write FINAL to OUT")
    ap.add_argument("--rebuild", action="store_true", help="the route from the raw draft, compared with FINAL")
    ap.add_argument("--write-letters", action="store_true", help="with --rebuild: (re)write FINAL from the route")
    a = ap.parse_args()
    if a.rebuild:
        can = rebuild()
        if a.write_letters:
            write_letters(can, FINAL)
            print("wrote", FINAL)
        else:
            old = read_letters(FINAL)
            print("same as FINAL" if (old == can).all() else
                  f"differs from FINAL in {int((old != can).any(-1).sum())} squares (hand edits?)")
    if a.final:
        can = read_letters(FINAL)
        Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(R.lp(OUT))
        print("wrote", OUT, "box", Image.fromarray(can).getbbox())
    if a.base:
        show(base())
    if a.cuts:
        os.makedirs(a.cuts, exist_ok=True)
        options(a.cuts)


if __name__ == "__main__":
    main()

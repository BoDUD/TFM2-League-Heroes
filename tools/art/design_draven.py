#!/usr/bin/env python3
"""Draven's game-size design (step 1) from Codex's generator drafts (assets/source/draven/codex_model/raw).

    python tools/art/design_draven.py --base [1|2]        # print a draft's read-back as letters (row/column numbers)
    python tools/art/design_draven.py --cuts OUT_DIR      # the size options for the user (PNGs + letter files)
    python tools/art/design_draven.py --final             # the approved letter grid (FINAL) -> assets/source/native

How it came about (2026-10-10): the user picked Codex's picture A (standing tall, an axe out in each hand). Codex's
step 1 drew two generator drafts of ~19.6 px squares (draven_design_1/2_generator.png: version 1 the picture's head,
version 2 a bigger head) and sampled them itself at a fixed 64 grid (44 / 46 rows crest to soles; the drafts' squares
run 12-30 px wide, so a fixed pitch skips the narrow ones). Here, as for league_karma:
  1. read back on its own grid (the skill's regrid.py, --size 19.6) - 67 x 61 (both);
  2. every square to the nearest of PAL (CIELAB) - Codex's own 26-colour palette (its own mapping had sent every
     square darker than 65 to the outline: the trousers, the straps and the axes' panels went black);
  3. whole rows and columns deleted EVENLY per part to the size the user picks (never two neighbours, never the
     face's rows and columns, the soles kept);
  4. strips.complete_outline; 5. on the 128 x 128 canvas: the soles on row 99, the middle of the feet on column 64.
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

RAW = {v: os.path.join(ROOT, "assets", "source", "draven", "codex_model", "raw", f"draven_design_{v}_generator.png")
       for v in "12"}
FINAL = os.path.join(ROOT, "assets", "source", "draven", "design", "draven_design.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "draven_native.png")
SQUARE = 19.6                                      # the drafts' square (regrid's own guess, 14, splits squares)

PAL = {                # Codex's palette.hex (assets/source/draven/codex_model), one letter a colour
    "0": "#1A0E0E",   # outline
    "h": "#6B343D",   # hair mid / maroon
    "H": "#9C344C",   # hair light / crimson shade
    "c": "#CA224A",   # crimson (wraps, ribbons, gems)
    "m": "#742342",   # crimson dark
    "u": "#421D30",   # plum darkest
    "k": "#AF714D",   # skin dark
    "K": "#D59660",   # skin mid
    "s": "#F0AF76",   # skin
    "S": "#FFCF94",   # skin light
    "G": "#BD8D32",   # gold dark
    "g": "#F3CB57",   # gold
    "y": "#FFE59A",   # gold glint
    "f": "#877A70",   # fur dark
    "F": "#C4C0AE",   # fur mid
    "w": "#F5EFDD",   # fur light
    "t": "#064853",   # teal dark
    "T": "#087082",   # teal
    "q": "#319793",   # teal light
    "b": "#443631",   # brown strap / boots dark
    "B": "#695044",   # brown light
    "d": "#292A32",   # trousers dark
    "D": "#474958",   # trousers / steel darkest
    "e": "#71829D",   # steel mid
    "E": "#B0C6DE",   # steel light
    "W": "#F5F8FF",   # white glint / teeth / blade edge
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


def base(v="1"):
    raw, _, _ = regrid(np.asarray(Image.open(R.lp(RAW[v])).convert("RGBA")), SQUARE)
    return letters(raw)


def show(rows):
    print("    " + "".join(str(x // 10) for x in range(len(rows[0]))))
    print("    " + "".join(str(x % 10) for x in range(len(rows[0]))))
    for y, r in enumerate(rows):
        print(f"{y:3d} {r}")


WEIGHT = {"W": 6, "c": 4, "g": 4, "T": 3, "w": 2, "s": 2}
# size options: name -> (draft, row parts, column parts, hard rows, hard cols) as (first, last, deletions); the raised
# axe (rows 0-17 / 0-15) and the hair crest / the beard give rows too, so the head does not grow against the body
H1 = set(range(23, 28)) | {64, 65, 66}               # draft 1: headband 23, eyes 24-25, mouth 27; the soles
H2 = set(range(22, 28)) | {64, 65, 66}               # draft 2: headband 22, eyes 24-25, mouth 27; the soles
C1 = set(range(26, 41))                               # the face's columns
COLS = {44: [(0, 14, 2), (15, 25, 1), (41, 46, 1), (47, 60, 2)],
        42: [(0, 14, 2), (15, 25, 1), (41, 46, 1), (47, 60, 3)],
        40: [(0, 14, 3), (15, 25, 2), (41, 46, 1), (47, 60, 3)]}
CUTS = {
    "1_44": ("1", [(0, 17, 2), (18, 22, 1), (34, 48, 2), (49, 63, 2)], COLS[44], H1, C1),
    "1_42": ("1", [(0, 17, 3), (18, 22, 1), (28, 33, 1), (34, 48, 2), (49, 63, 3)], COLS[42], H1, C1),
    "1_40": ("1", [(0, 17, 3), (18, 22, 2), (28, 33, 1), (34, 48, 3), (49, 63, 3)], COLS[40], H1, C1),
    "1_40h": ("1", [(0, 17, 4), (18, 22, 2), (28, 33, 2), (34, 48, 2), (49, 63, 3)], COLS[40], H1, C1),
    "2_40": ("2", [(0, 15, 3), (16, 21, 2), (28, 34, 2), (35, 48, 4), (49, 63, 3)], COLS[40], H2, C1),
}


def cut(rows, row_parts, col_parts, hard_rows, hard_cols):
    R.JITTER = 1
    idx = np.array([[ord(c) for c in r.ljust(len(rows[0]))] for r in rows])
    w = np.vectorize(lambda v: WEIGHT.get(chr(v), 1))(idx)
    H, W = idx.shape
    dr = []
    for lo, hi, q in row_parts:
        dr += R.even_drop([idx[y] for y in range(H)], [w[y] for y in range(H)], lo, hi, q, hard_rows)
    kr = [y for y in range(H) if y not in dr]
    sub, ws = idx[kr], w[kr]
    dc = []
    for lo, hi, q in col_parts:
        dc += R.even_drop([sub[:, x] for x in range(W)], [ws[:, x] for x in range(W)], lo, hi, q, hard_cols)
    kc = [x for x in range(W) if x not in dc]
    return ["".join(chr(v) for v in r) for r in sub[:, kc]], dr, dc


def on_canvas(fig):
    fig = R.crop(fig)
    feet = np.nonzero((fig[-3:, :, 3] > 0).any(0))[0]
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = R.SOLE_ROW + 1 - fig.shape[0], int(round(R.MID_COL - (feet.min() + feet.max()) / 2))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def make(name):
    v, rp, cp, hr, hc = CUTS[name]
    rows, dr, dc = cut(base(v), rp, cp, hr, hc)
    return close_outline(to_rgba(rows)), dr, dc


PICK = "1_40h"          # the user's pick (「1_40h」, 2026-10-10)
POLISH = []


def rebuild():
    """The picked cut on the canvas with POLISH applied (what FINAL holds)."""
    fig, _, _ = make(PICK)
    can = on_canvas(fig)
    ys, xs = np.nonzero(can[..., 3] > 0)
    x0 = xs.min()
    for y, c, text in POLISH:
        for i, ch in enumerate(text):
            if ch == ".":
                can[y, x0 + c + i] = 0
            elif ch != " ":
                can[y, x0 + c + i, :3] = RGB[ch]
                can[y, x0 + c + i, 3] = 255
    return can


def options(out_dir):
    figs = {}
    for name in CUTS:
        fig, dr, dc = make(name)
        figs[name] = fig
        Image.fromarray(fig).save(os.path.join(out_dir, f"draven_cut{name}.png"))
        with open(os.path.join(out_dir, f"draven_cut{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", nargs="?", const="1")
    ap.add_argument("--cuts", metavar="OUT_DIR")
    ap.add_argument("--final", action="store_true", help="write FINAL to OUT")
    ap.add_argument("--rebuild", action="store_true", help="PICK + POLISH, compared with FINAL")
    ap.add_argument("--write-letters", action="store_true", help="with --rebuild: (re)write FINAL")
    a = ap.parse_args()
    if a.rebuild:
        can = rebuild()
        if a.write_letters:
            write_letters(can, FINAL)
            print("wrote", FINAL)
        else:
            old = read_letters(FINAL)
            print("same as FINAL" if (old == can).all() else f"differs from FINAL in {int((old != can).any(-1).sum())} squares")
    if a.final:
        can = read_letters(FINAL)
        Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(R.lp(OUT))
        print("wrote", OUT, "box", Image.fromarray(can).getbbox())
    if a.base:
        show(base(a.base))
    if a.cuts:
        os.makedirs(a.cuts, exist_ok=True)
        options(a.cuts)


if __name__ == "__main__":
    main()

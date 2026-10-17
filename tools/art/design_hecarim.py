#!/usr/bin/env python3
"""Hecarim's game-size design (step 1) from Codex's generator draft (assets/source/hecarim/codex_model/raw).

    python tools/art/design_hecarim.py --base [1]          # print the draft's read-back as letters (row/column numbers)
    python tools/art/design_hecarim.py --cuts OUT_DIR      # the size options for the user (PNGs + letter files)
    python tools/art/design_hecarim.py --final             # the approved letter grid (FINAL) -> assets/source/native

How it came about (2026-10-09): the user picked Codex's picture A (League's idle: the centaur standing side-on, the
glaive across the body). Codex's first step 1 (assets/source/hecarim/codex_model) drew a chibi helm 15 rows tall with a
cream line round every plate - rejected: 「你这个脸不对啊」「学别人那种画法啊 头这么大干嘛」. The second round
(codex_model_v2, drawn oppi's way: a small helm between big pauldrons, 1-square glowing eyes, dark shaded armour) gave
two generator originals of ~14 px squares, version 1 a helm of 8 rows, version 2 of 7. Here, as for league_karma:
  1. read back on its own grid (the skill's regrid.py) - 54 x 81 both;
  2. every square to the nearest of PAL (CIELAB) - the draft's own colours;
  3. whole rows and columns deleted EVENLY per part to the size the user picks (never two neighbours, never the
     helm's eye rows and columns, the hooves kept);
  4. strips.complete_outline; 5. on the 128 x 128 canvas: the hooves on row 99, the horse's middle on column 64.
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

RAW = {v: os.path.join(ROOT, "assets", "source", "hecarim", "codex_model_v2", "raw",
                       f"hecarim_design_{v}_generator.png") for v in "12"}
FINAL = os.path.join(ROOT, "assets", "source", "hecarim", "design", "hecarim_design.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "hecarim_native.png")

PAL = {
    "0": "#000000",   # outline and the deepest gaps
    "k": "#282828",   # armour darkest
    "v": "#3C283C",   # armour shade, plum
    "a": "#3C3C3C",   # armour dark
    "A": "#505050",   # armour mid
    "B": "#646464",   # armour light
    "p": "#645064",   # plum light
    "w": "#786464",   # warm grey edge light
    "W": "#787878",   # cold grey edge light
    "x": "#B4C8C8",   # blade
    "S": "#F0F0F0",   # blade edge
    "t": "#005A5A",   # ghost teal darkest
    "T": "#148C82",   # teal dark
    "u": "#28C8B4",   # teal
    "U": "#50F0DC",   # teal bright (eyes)
    "r": "#3C1428",   # tabard dark
    "R": "#642828",   # tabard
    "o": "#C8A078",   # copper
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
    raw, _, _ = regrid(np.asarray(Image.open(R.lp(RAW[v])).convert("RGBA")))
    return letters(raw)


def show(rows):
    print("    " + "".join(str(x // 10) for x in range(len(rows[0]))))
    print("    " + "".join(str(x % 10) for x in range(len(rows[0]))))
    for y, r in enumerate(rows):
        print(f"{y:3d} {r}")


WEIGHT = {"U": 8, "u": 3, "S": 3, "x": 2, "o": 4, "R": 2, "W": 2, "w": 2}
# size options: name -> (draft, row parts, column parts, hard rows, hard cols) as (first, last, deletions)
# v2 drafts' rows: horn 0-8, helm 9-17 (eyes 12, teeth 15), chest grin 19-22, body 23-53 (hooves 49-53)
H1 = {12, 15, 49, 50, 51, 52, 53}
C1 = set(range(46, 53))                            # the helm's eyes and teeth
CUTS = {
    "1_45": ("1", [(0, 8, 2), (9, 17, 1), (18, 30, 2), (31, 48, 4)], [(0, 14, 4), (15, 42, 5), (54, 80, 6)], H1, C1),
    "2_45": ("2", [(0, 8, 2), (9, 17, 1), (18, 30, 2), (31, 48, 4)], [(0, 14, 4), (15, 42, 5), (54, 80, 6)], H1, C1),
    "1_48": ("1", [(0, 8, 2), (18, 30, 1), (31, 48, 3)], [(0, 14, 3), (15, 42, 4), (54, 80, 5)], H1, C1),
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


PICK = "2_45"         # the user's pick (2026-10-09, from hecarim_design_v2_sizes.png)
# hand edits on the picked cut, in FINAL's coordinates: (canvas row, column from x0, letters; '.' clears)
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
        Image.fromarray(fig).save(os.path.join(out_dir, f"hecarim_cut{name}.png"))
        with open(os.path.join(out_dir, f"hecarim_cut{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
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

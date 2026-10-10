#!/usr/bin/env python3
"""Syndra's game-size design (step 1) from Codex's generator drafts (assets/source/syndra/codex_model/raw).

    python tools/art/design_syndra.py --base [1|2]        # print a draft's read-back as letters (row/column numbers)
    python tools/art/design_syndra.py --cuts OUT_DIR      # the size options for the user (PNGs + letter files)
    python tools/art/design_syndra.py --final             # the approved letter grid (FINAL) -> assets/source/native

How it came about (2026-10-10): the user picked Codex's picture A (the relic cannon resting on her shoulder). Codex's
step 1 drew three generator drafts of 10 px squares (syndra-generation-01/02/03.png): 01 the picture's detail at 97 rows,
02 redrawn to the pack's target silhouette at 67 rows (claws to soles), 03 a further low-detail redraw at ~46 rows that
Codex sampled into its syndra_design.png - the face a blob, the claws and the body a jumble of gold specks. So here, as
for league_draven, from draft 02 (01 is too big to cut):
  1. read back on its own grid (the skill's regrid.py, --size 10);
  2. every square to the nearest of PAL (CIELAB) - Codex's own 27-colour palette (codex_model/validation.json);
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

RAW = {v: os.path.join(ROOT, "assets", "source", "syndra", "codex_model", "raw", f"generation-{v}.png")
       for v in "123"}
FINAL = os.path.join(ROOT, "assets", "source", "syndra", "design", "syndra_design.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "syndra_native.png")
SQUARE = {"1": 10.0, "2": 14.0, "3": 17.0}       # the drafts' squares (regrid's own measure)

PAL = {                # draft 3's own colours (k-means in CIELAB on its read-back, 24 -> 19: the near-blacks one outline)
    "0": "#100017",   # outline
    "1": "#190323",   # black-violet
    "d": "#2F0F48",   # dark violet
    "h": "#43176A",   # violet
    "H": "#571D8B",   # violet light
    "I": "#9738E0",   # bright violet (horns' light)
    "c": "#750242",   # crimson dark
    "r": "#A70743",   # crimson
    "R": "#AA2616",   # lips
    "M": "#F50684",   # magenta (eyes, gem, gloves, belt)
    "b": "#693E38",   # skin darkest
    "k": "#DB8045",   # skin dark
    "s": "#FDC087",   # skin
    "G": "#9A7940",   # gold darkest
    "g": "#CC9228",   # gold dark
    "y": "#FCC838",   # gold
    "A": "#A7A1C0",   # hair shade
    "W": "#E2E4EE",   # hair
    "X": "#FBF9F9",   # white glint
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
    raw, _, _ = regrid(np.asarray(Image.open(R.lp(RAW[v])).convert("RGBA")), SQUARE[v])
    return letters(raw)


def show(rows):
    print("    " + "".join(str(x // 10) for x in range(len(rows[0]))))
    print("    " + "".join(str(x % 10) for x in range(len(rows[0]))))
    for y, r in enumerate(rows):
        print(f"{y:3d} {r}")


WEIGHT = {"M": 8, "R": 6, "r": 4, "s": 2, "y": 2, "X": 3}
# size options from draft 3 (--base 3, read on its own 17 px grid: 53 rows horn tips to toes, 33 columns; the user's
# pick was Codex's picture A, Codex sampled this draft into its own A / B by deleting rows only): the horns 0-7, the
# helmet 8-14, the eyes 17-18, the mouth 20-21, the chin 22, the body and skirt 23-41, the legs 42-48, the toes 49-52;
# the face's columns 11-20. Deletions per part (never two neighbours: at most half a part): rows (horns, helmet, body,
# legs), columns (hair 0-10, arm / skirt 21-32). The name's number is the rows left; "h" takes more from the head.
H3 = set(range(15, 23)) | set(range(49, 53))
C3 = set(range(11, 21))
PLANS = {"3_46": ((2, 1, 3, 1), (2, 2)), "3_44": ((2, 2, 4, 1), (2, 3)), "3_42": ((3, 2, 4, 2), (3, 3)),
         "3_40": ((3, 2, 6, 2), (3, 4)), "3_40h": ((4, 3, 4, 2), (3, 4))}


def plan(name):
    (horns, helm, body, legs), (left, right) = PLANS[name]
    rows = [(0, 7, horns), (8, 14, helm), (23, 41, body), (42, 48, legs)]
    cols = [(0, 10, left), (21, 32, right)]
    return ("3", [r for r in rows if r[2]], [c for c in cols if c[2]], H3, C3)


CUTS = {name: plan(name) for name in PLANS}


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


PICK = "3_42"          # the user's pick (「3_42」, 2026-10-11)
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
        Image.fromarray(fig).save(os.path.join(out_dir, f"syndra_cut{name}.png"))
        with open(os.path.join(out_dir, f"syndra_cut{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
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
    ap.add_argument("--base", nargs="?", const="2")
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

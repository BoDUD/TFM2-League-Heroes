#!/usr/bin/env python3
"""Senna's game-size design (step 1) from Codex's generator drafts (assets/source/senna/codex_model/raw).

    python tools/art/design_senna.py --base [1|2]        # print a draft's read-back as letters (row/column numbers)
    python tools/art/design_senna.py --cuts OUT_DIR      # the size options for the user (PNGs + letter files)
    python tools/art/design_senna.py --final             # the approved letter grid (FINAL) -> assets/source/native

How it came about (2026-10-10): the user picked Codex's picture A (the relic cannon resting on her shoulder). Codex's
step 1 drew three generator drafts of 10 px squares (senna-generation-01/02/03.png): 01 the picture's detail at 97 rows,
02 redrawn to the pack's target silhouette at 67 rows (claws to soles), 03 a further low-detail redraw at ~46 rows that
Codex sampled into its senna_design.png - the face a blob, the claws and the body a jumble of gold specks. So here, as
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

RAW = {v: os.path.join(ROOT, "assets", "source", "senna", "codex_model", "raw", f"senna-generation-0{v}.png")
       for v in "123"}
FINAL = os.path.join(ROOT, "assets", "source", "senna", "design", "senna_design.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "senna_native.png")
SQUARE = 10.0                                      # the drafts' square (regrid's own measure)

PAL = {                # Codex's palette (codex_model/validation.json), one letter a colour
    "0": "#1E1424",   # outline
    "9": "#171721",   # blue-black (the cannon's barrel, locs' darkest)
    "p": "#2E293B",   # locs / plum-grey dark
    "P": "#34203F",   # plum darkest
    "q": "#43344F",   # plum-grey
    "r": "#513057",   # plum (clothes)
    "x": "#25564E",   # eye dark green
    "X": "#77E3B3",   # eye bright green
    "n": "#36434E",   # slate dark
    "N": "#4C6B73",   # slate
    "t": "#65828A",   # teal grey
    "T": "#769BA1",   # teal
    "e": "#92ABB2",   # pale teal
    "E": "#AACDD0",   # crystal / hood shade
    "W": "#EAF5EB",   # white (hood, sash, crystal light)
    "m": "#42202D",   # maroon darkest
    "M": "#6E2C38",   # maroon (wing plates)
    "c": "#97253F",   # crimson (lips, plates' light)
    "a": "#A34B4F",   # rose
    "b": "#613329",   # skin darkest
    "k": "#8F4C36",   # skin dark
    "K": "#B46C47",   # skin mid
    "s": "#D48B58",   # skin light
    "G": "#765025",   # gold dark
    "g": "#B38232",   # gold mid
    "y": "#EABA4E",   # gold
    "Y": "#FFE59B",   # gold glint
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


WEIGHT = {"X": 8, "x": 6, "c": 4, "W": 3, "Y": 3, "s": 2}
# size options: name -> (draft, row parts, column parts, hard rows, hard cols) as (first, last, deletions). Draft 2's
# letters (--base 2): the claws 0-8, the hood's top row 9, the eyes 25-26, the mouth 28-29, the chin ~31, the soles
# 64-66 - 58 rows hood to soles; the face's columns 36-48. The name's number is the rows left hood to soles; "h"
# takes more of them from the head (the user picked league_draven's "h" cut).
H2 = {25, 26, 28, 29, 64, 65, 66}
C2 = set(range(36, 49))


def plan(t, head):
    """Rows: claws, the hood above the eyes, the neck and body, the legs; columns: the cannon's side, the arm's."""
    d = 58 - t
    claws = round(9 * d / 58)
    top = round(16 * d / 58) + head
    legs = round(16 * d / 58)
    body = d - top - legs
    rows = [(0, 8, claws), (9, 24, top), (30, 47, body), (48, 63, legs)]
    dc = round(65 * d / 58)
    left = round(dc * 0.65)
    cols = [(0, 35, left), (49, 64, dc - left)]
    return ("2", [r for r in rows if r[2] > 0], [c for c in cols if c[2] > 0], H2, C2)


CUTS = {"2_46": plan(46, 0), "2_44": plan(44, 0), "2_42": plan(42, 0), "2_40": plan(40, 0), "2_40h": plan(40, 2)}


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


PICK = "2_40"            # the user's pick (「2_40」, 2026-10-10)
# (canvas row, column from the figure's left, letters): draft 02 shows only her near eye - the far eye added (a brow
# square, a lash and a dark-over-bright green eye, 4 squares); 2026-10-10 (「眼睛有很多奇怪的地方」) the draft's dark +
# white squares past that eye (a third eye on the face's edge) and the lash square between the eyes made skin, as on the
# action strips' head (fix_senna_strips CANON_EDITS); then the brows apart (「眉毛连在一起不修吗」): the near brow 3 squares
# over the near eye, the far one 2 over the far eye, skin between (the near one had run on into the far one)
POLISH = [(69, 28, "KKPP"), (70, 28, "KKk"), (71, 28, "K9x"), (72, 30, "XKk"),
          # the ground showing through her (「像素缺失」): a pinhole between the locs and the claws, the slit beside them,
          # the gaps round the hand at her hip - each the commonest colour round it (the claws' open prongs stay)
          (65, 37, "9"), (73, 38, "9"), (74, 38, "9"), (75, 38, "9"), (83, 18, "99"), (83, 22, "99"), (84, 22, "9"),
          (85, 21, "9"), (90, 21, "r")]


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
        Image.fromarray(fig).save(os.path.join(out_dir, f"senna_cut{name}.png"))
        with open(os.path.join(out_dir, f"senna_cut{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
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

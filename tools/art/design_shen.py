#!/usr/bin/env python3
"""Shen's game-size design (step 1) from Codex's generator drafts (assets/source/shen/codex_model/raw).

    python tools/art/design_shen.py --base [1|2]        # print a draft's read-back as letters (row/column numbers)
    python tools/art/design_shen.py --cuts OUT_DIR      # the size options for the user (PNGs + letter files)
    python tools/art/design_shen.py --final             # the approved letter grid (FINAL) -> assets/source/native

How it came about (2026-10-10): the user picked Codex's picture A (League's idle: the sword up in a reverse grip). Codex's
step 1 drew two generator drafts (shen_design_1/2_generator.png: version 1 the picture's head, version 2 a bigger
head) and sampled them itself at a fixed 64 grid (46 / 43 rows hood to soles) - not used. Here, as for league_draven:
  1. read back on its own grid (the skill's regrid.py): draft 1 ~19.0 px squares, draft 2 ~15.7 px (regrid's own guess
     for draft 2, 10, splits squares);
  2. every square to the nearest colour (CIELAB) of that draft's PALS (its own colours, see there);
  3. whole rows and columns deleted EVENLY per part to the size the user picks (never two neighbours, never the
     eyes' rows and columns, the soles kept);
  4. strips.complete_outline; 5. on the 128 x 128 canvas: the soles on row 99, the middle of the feet on column 64.
Round 1's drafts were 43 / 64 rows hood to soles; the user had Codex redraw draft 2 at 40 (round 2, codex_model_v2:
six tries, none at 40-44 - draft 3 "redraw" ~60 rows, draft 4 "compact" 50 rows). The user picked draft 4 cut to 42
(4_42), its face and hands brought back to the picture (POLISH: a skin slit with two glowing eyes; RECOLOR: brown
gloves), then 「再帮我略微缩小点」 -> SHRINK s40: 40 rows hood to soles (46 x 37 with the raised pommel), 30 colours.
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

SRC = os.path.join(ROOT, "assets", "source", "shen", "codex_model")
RAW = {v: os.path.join(SRC, "raw", f"shen_design_{v}_generator.png") for v in "12"}
RAW.update({v: os.path.join(SRC + "_v2", "raw", f"shen_design_{v}_generator.png") for v in "34"})
FINAL = os.path.join(ROOT, "assets", "source", "shen", "design", "shen_design.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "shen_native.png")
SQUARE = {"1": 19.0, "2": 15.7, "3": 17.0, "4": 10.0}
CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# Each draft's colours: 30 k-means centres (CIELAB, seed 1) of its own read-back squares - Codex's 28-colour exports
# flattened the bare arms' muscle shading - plus what k-means merges away: the glowing eyes' violet and lavender and
# (draft 2) the ice-blue pommel.
PALS = {
    "1": ["#0F0713", "#180E23", "#271417", "#261031", "#1F1A3A", "#2C133F", "#331B18", "#37184F", "#252457", "#45241A",
          "#3C1A6C", "#2A2C6A", "#3D384A", "#433A55", "#623622", "#422EA2", "#39459B", "#59546A", "#8140CC", "#6C6B8D",
          "#A56652", "#C87150", "#8986A3", "#D37E56", "#9F9DBD", "#B0AFCC", "#96BEE8", "#F8A773", "#C5C5D9", "#EBBEFD",
          "#EAEAF0"],
    "2": ["#0F0515", "#13071C", "#220D31", "#191842", "#2D1040", "#221B2D", "#321A18", "#311C2C", "#202257", "#3A1658",
          "#45251D", "#421B70", "#272B6A", "#362E48", "#48394D", "#623827", "#4830AD", "#38429E", "#6C648D", "#B56243",
          "#847DA4", "#8E49D9", "#D87E53", "#938FB5", "#A7A3C4", "#96BEE8", "#E4A181", "#BAB6D5", "#FAA975", "#CCCBE4",
          "#EBBEFD", "#E1DFEF", "#F9F8FA"],
    "3": ["#0E0212", "#0F0315", "#150C2F", "#230B3A", "#270C40", "#151743", "#2E1714", "#2F104F", "#1A1E51", "#381562",
          "#391669", "#212663", "#46281B", "#232B75", "#431C82", "#462295", "#2C3897", "#613823", "#673572", "#534A67",
          "#77739B", "#8E8CB4", "#A662F5", "#D28253", "#E0915F", "#A8A7CA", "#F8AD75", "#BCBEDC", "#CDCDE6", "#E2E2F4",
          "#FCFBFD"],
    "4": ["#0B010F", "#110218", "#0F0C30", "#120F3B", "#2B171A", "#231548", "#1B1B56", "#341E1A", "#202062", "#3D241E",
          "#262676", "#302D47", "#2C2C8D", "#573327", "#514B50", "#583B95", "#593C9C", "#784630", "#686A81", "#6066D7",
          "#767A8B", "#B67346", "#8A8D98", "#98A1BA", "#61BCDB", "#A3A5AB", "#EEA96D", "#C3C3C5", "#DEE0E3", "#EFE2F6"],
}


def palette(v):
    """Draft v's colours, darkest first, one letter each ('0' = the outline)."""
    cols = sorted((R.hx(h) for h in PALS[v]), key=lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])
    return {CHARS[i]: tuple(int(x) for x in c) for i, c in enumerate(cols)}


def letters(a, pal):
    keys = list(pal)
    pl = R.lab(np.array([pal[k] for k in keys], float))
    near = ((R.lab(a[..., :3])[..., None, :] - pl[None, None]) ** 2).sum(-1).argmin(-1)
    return ["".join(keys[near[y, x]] if a[y, x, 3] >= 128 else " " for x in range(a.shape[1]))
            for y in range(a.shape[0])]


def to_rgba(rows, pal):
    a = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch not in " .":
                a[y, x, :3] = pal[ch]
                a[y, x, 3] = 255
    return a


def from_rgba(a, pal):
    inv = {v: k for k, v in pal.items()}
    return ["".join(inv[tuple(int(v) for v in a[y, x, :3])] if a[y, x, 3] else " " for x in range(a.shape[1]))
            for y in range(a.shape[0])]


def close_outline(a, pal):
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    p, _, _ = strips.complete_outline(p, color=pal["0"], feet=a.shape[0], keep=None)
    return R.crop(p)


def base(v="2"):
    raw, _, _ = regrid(np.asarray(Image.open(R.lp(RAW[v])).convert("RGBA")), SQUARE[v])
    rows = letters(raw, palette(v))
    ys = [y for y, r in enumerate(rows) if r.strip()]
    xs = [x for r in rows for x, c in enumerate(r) if c != " "]
    return [r[min(xs):max(xs) + 1] for r in rows[ys[0]:ys[-1] + 1]]


def show(rows):
    print("    " + "".join(str(x // 10) for x in range(len(rows[0]))))
    print("    " + "".join(str(x % 10) for x in range(len(rows[0]))))
    for y, r in enumerate(rows):
        print(f"{y:3d} {r}")


def keys_of(v, hexes):
    pal = palette(v)
    return {k for k, c in pal.items() if "#%02X%02X%02X" % c in hexes}


EYES = {"#8140CC", "#8E49D9", "#EBBEFD", "#A662F5", "#EFE2F6"}
SILVER = {"#EAEAF0", "#C5C5D9", "#F9F8FA", "#E1DFEF", "#CCCBE4", "#96BEE8", "#E2E2F4", "#FCFBFD", "#DEE0E3", "#C3C3C5",
          "#61BCDB"}


def weights(v):
    w = {k: 12 for k in keys_of(v, EYES)}
    w.update({k: 3 for k in keys_of(v, SILVER)})
    return w


def hard(v, rows, extra_rows=()):
    """The eyes' rows and columns, the soles' two rows and any extra rows: never deleted."""
    eyes = keys_of(v, EYES)
    hr = {y for y, r in enumerate(rows) for c in r if c in eyes} | {len(rows) - 2, len(rows) - 1} | set(extra_rows)
    hc = {x for r in rows for x, c in enumerate(r) if c in eyes}
    return hr, hc


# size options: name -> (draft, row parts, column parts) as (first, last, deletions); the hood's top is row 12 in both
# read-backs (draft 1: 43 rows hood to soles, draft 2: 64), the rows above it are the raised fist and pommel
CUTS = {
    "1_42": ("1", [(23, 38, 1)], []),
    "1_40": ("1", [(23, 38, 1), (39, 52, 2)], [(0, 38, 1)]),
    "2_40": ("2", [(0, 11, 4), (12, 30, 6), (31, 50, 9), (51, 73, 9)], [(0, 53, 14)]),
    # round 2 (codex_model_v2): draft 4 = Codex's "compact" try, 45 x 57, the hood's top row 7, the soles row 56 (50)
    "4_42": ("4", [(0, 6, 1), (8, 18, 1), (20, 37, 3), (38, 54, 4)], [(0, 18, 3), (19, 44, 3)]),
    "4_40": ("4", [(0, 6, 2), (8, 18, 2), (20, 37, 4), (38, 54, 4)], [(0, 18, 4), (19, 44, 4)]),
}
PICK = "4_42"         # the user's pick (「用 4_42，我把脸和手套修回原画」, 2026-10-10)
# (row, column from the figure's left edge, letters; '.' clears, ' ' keeps) - draft 4's palette
POLISH = [
    (63, 18, "0ltqqtl0"),    # the dark slit -> a skin slit with two glowing eyes (picture A)
    (64, 19, "mrsrm"),       # the mask's lit top under it
]
# (row0, row1, col0, col1, {from: to}) - recolour inside a box: bare hands -> the picture's brown gloves
GLOVE = {"q": "h", "l": "d", "h": "9"}
RECOLOR = [
    (55, 60, 12, 15, GLOVE),  # the raised fist on the grip
    (78, 84, 32, 38, GLOVE),  # the near hand, open
]


# The user on the fixed 4_42: 「挺不错的 再帮我略微缩小点就可以了」 - whole rows / columns more, evenly, from the
# polished figure (rows: 0-5 the pommel and fist, 6 the hood's top, 10-14 the face, 47 the soles), the face kept.
SHRINKS = {
    "s40": ([(16, 32, 1), (33, 45, 1)], [(0, 14, 1), (25, 38, 1)]),
    "s38": ([(0, 5, 1), (7, 9, 1), (16, 32, 2), (33, 45, 1)], [(0, 14, 2), (25, 38, 2)]),
}
SHRINK_HARD = (set(range(10, 15)) | {46, 47}, set(range(19, 26)))
SHRINK = "s40"          # the user's pick (「40 格」, 2026-10-10)


def shrink(can, name):
    """The polished canvas with SHRINKS[name]'s rows and columns deleted, back on the canvas."""
    pal = palette(CUTS[PICK][0])
    rows = from_rgba(R.crop(can), pal)
    rp, cp = SHRINKS[name]
    out, dr, dc = cut(rows, rp, cp, SHRINK_HARD[0], SHRINK_HARD[1], weights(CUTS[PICK][0]))
    return on_canvas(to_rgba(out, pal)), dr, dc


def cut(rows, row_parts, col_parts, hard_rows, hard_cols, weight):
    R.JITTER = 1
    idx = np.array([[ord(c) for c in r.ljust(len(rows[0]))] for r in rows])
    w = np.vectorize(lambda v: weight.get(chr(v), 1))(idx)
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
    v, rp, cp = CUTS[name]
    pal = palette(v)
    rows = base(v)
    hr, hc = hard(v, rows)
    rows, dr, dc = cut(rows, rp, cp, hr, hc, weights(v))
    return close_outline(to_rgba(rows, pal), pal), dr, dc


def rebuild():
    """The picked cut on the canvas with POLISH applied (what FINAL holds)."""
    fig, _, _ = make(PICK)
    pal = palette(CUTS[PICK][0])
    can = on_canvas(fig)
    ys, xs = np.nonzero(can[..., 3] > 0)
    x0 = xs.min()
    inv = {v: k for k, v in pal.items()}
    for y0, y1, c0, c1, m in RECOLOR:
        for y in range(y0, y1 + 1):
            for x in range(x0 + c0, x0 + c1 + 1):
                if can[y, x, 3]:
                    k = inv[tuple(int(v) for v in can[y, x, :3])]
                    if k in m:
                        can[y, x, :3] = pal[m[k]]
    for y, c, text in POLISH:
        for i, ch in enumerate(text):
            if ch == ".":
                can[y, x0 + c + i] = 0
            elif ch != " ":
                can[y, x0 + c + i, :3] = pal[ch]
                can[y, x0 + c + i, 3] = 255
    if SHRINK:
        can = shrink(can, SHRINK)[0]
    return can


def options(out_dir):
    figs = {}
    for name in CUTS:
        fig, dr, dc = make(name)
        figs[name] = fig
        Image.fromarray(fig).save(os.path.join(out_dir, f"shen_cut{name}.png"))
        with open(os.path.join(out_dir, f"shen_cut{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(from_rgba(fig, palette(CUTS[name][0]))) + "\n")
        print(f"{name}: {fig.shape[0]} x {fig.shape[1]}  rows dropped {dr}  cols dropped {dc}")
    return figs


def write_letters(can, path, pal):
    ys, xs = np.nonzero(can[..., 3] > 0)
    x0 = xs.min()
    inv = {v: k for k, v in pal.items()}
    os.makedirs(os.path.dirname(R.lp(path)), exist_ok=True)
    with open(R.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# x0 {x0} draft {CUTS[PICK][0]}\n")
        for y in range(ys.min(), ys.max() + 1):
            f.write(f"{y:3d}" + "".join(inv[tuple(int(v) for v in can[y, x, :3])] if can[y, x, 3] else " "
                                        for x in range(x0, xs.max() + 1)).rstrip() + "\n")


def read_letters(path):
    can = np.zeros((128, 128, 4), np.uint8)
    x0, pal = 0, None
    for line in open(R.lp(path), encoding="utf-8"):
        line = line.rstrip("\r\n")
        if line.startswith("# x0"):
            parts = line.split()
            x0, pal = int(parts[2]), palette(parts[4])
            continue
        if len(line) < 4 or not line[:3].strip().isdigit():
            continue
        y = int(line[:3])
        for i, ch in enumerate(line[3:]):
            if ch not in " .":
                can[y, x0 + i, :3] = pal[ch]
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
            write_letters(can, FINAL, palette(CUTS[PICK][0]))
            print("wrote", FINAL)
        else:
            old = read_letters(FINAL)
            print("same as FINAL" if (old == can).all() else f"differs from FINAL in {int((old != can).any(-1).sum())} squares")
    if a.final:
        can = read_letters(FINAL)
        Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(R.lp(OUT))
        print("wrote", OUT, "box", Image.fromarray(can).getbbox())
    if a.base:
        for k, c in palette(a.base).items():
            print(k, "#%02X%02X%02X" % c, end="  ")
        print()
        show(base(a.base))
    if a.cuts:
        os.makedirs(a.cuts, exist_ok=True)
        options(a.cuts)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Rengar's game-size design (step 1) from Codex's generator draft (assets/source/rengar/codex_model/raw).

    python tools/art/design_rengar.py --final      # the approved letter grid (FINAL) -> assets/source/native/rengar_native.png
    python tools/art/design_rengar.py --check      # FINAL vs the committed native design
    python tools/art/design_rengar.py --rebuild    # the whole route again from the raw draft; compared with FINAL

How it came about (2026-10-09): the user picked Codex's picture A (League's idle: hunched, three claw blades on the far
wrist, the serrated blade in the near hand). Codex's step 1 drew one generator draft (rengar_generated_refined.png:
squares of ~10 px, 53 x 50 of them) and sampled it itself at 1254/128 px plus row/column deletions - specks again (as
Vladimir's first round). The user sent that draft back: 「按做吸血鬼的方法 慢慢做成这样吧」 - this draft is the look. So:
  1. read back on its own grid (the skill's regrid.py: square bounds from the colour changes, the middle 3x3's median
     colour) - 53 x 50, exactly the draft;
  2. every square to the nearest of PAL (CIELAB): the draft's own colours (k-means 40 of the read-back merged by hand),
     the far eye (E), the ear (P, Q) and the nose (N) kept apart;
  3. whole rows and columns deleted to 40 rows, EVENLY per part (each part shrinks by the same share, so the horn, the
     mane's braids and the claws keep their proportions; plain cheapest-line cuts bunched six deletions in the horn);
     each deletion may move one line to the cheapest neighbour, never two neighbours, never a hard line (the face's
     rows 19-26 and columns 26-38, the buckle rows 30-32, the feet). The user picked B = the claws' columns 0-11 kept
     whole; B's seven body deletions in columns 12-25 crushed the pauldron, so B41 = the body loses five (41 wide);
  4. strips.complete_outline;
  5. POLISH by hand, every square traced to base53: the tall horn redrawn at its full width (its light column was
     dropped), the mane's top highlights, the pauldron rivet, three chest-strap studs, the left knee pad's bottom, a
     tail ring, 14 outline squares on dropped lines (dark reds are not ringed by complete_outline); the outline again;
  6. on the 128 x 128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
The user approved it (「可以了」, 2026-10-09): 40 x 41, one piece, 25 colours, the outline closed.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "rengar", "codex_model", "raw", "rengar_generated_refined.png")
FINAL = os.path.join(ROOT, "assets", "source", "rengar", "design", "rengar_design_40.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "rengar_native.png")
SOLE_ROW, MID_COL = 99, 64

PAL = {
    "0": "#0E0206",   # outline
    "a": "#3A1A26",   # darkest leather / inner dark lines
    "b": "#70292B",   # dark leather
    "c": "#923937",   # leather
    "d": "#B04218",   # rust trim
    "e": "#A8031E",   # the blade's blood edge
    "f": "#FBD88C",   # bone light
    "g": "#E0A65A",   # bone mid / tan
    "h": "#C4843C",   # bone dark / bronze
    "i": "#7D512D",   # brown
    "j": "#F4B507",   # gold (rivets, studs, buckle, the eye-piece)
    "k": "#D5800F",   # orange
    "l": "#F4D05A",   # yellow (laces)
    "m": "#444B6F",   # fur dark
    "n": "#5F6A90",   # fur mid-dark
    "t": "#909BBB",   # fur mid
    "v": "#C2C7DB",   # fur light / mane shade
    "w": "#EFF0F5",   # white (face, mane)
    "s": "#7593CE",   # steel blue
    "x": "#5068A0",   # steel dark
    "y": "#A9C9F4",   # steel light
    "E": "#0297EA",   # the far eye (blue)
    "P": "#F9AED8",   # ear pink light
    "Q": "#E47FB4",   # ear pink
    "N": "#D03379",   # nose
}

# step 3: even deletions per part (first, last, deletions) on base53; hard lines never deleted
FACE_ROWS, FACE_COLS = set(range(19, 27)), set(range(26, 39))
ROW_PARTS = [(0, 18, 5), (27, 49, 8)]
COL_PARTS = [(12, 25, 5), (39, 49, 4)]
HARD_ROWS = {30, 31, 32, 50, 51, 52}
JITTER = 1
WEIGHT = {"E": 20, "j": 6, "N": 12, "P": 8, "Q": 8, "e": 4, "l": 4, "y": 3, "s": 3, "w": 2}

# step 5: (row, first column, letters) on the cut figure; '.' clears a square
POLISH = [
    # the tall horn at its full width from base53 rows 0,2,3,5,6,(8+9),10,11 x columns 37-42
    (0, 32, "000"), (1, 32, "0hh0"), (2, 33, "0g0"), (3, 33, "0fh0"), (4, 33, "0fhh0"), (5, 32, "0ffhh0"),
    (6, 31, "b0ffhh0"), (7, 31, "baihh00"), (8, 31, "0ca000"),
    # the mane's top: base53 row 5 'wvvw' lost both white ends
    (2, 19, "000"), (3, 18, "0wvw000"),
    # the pauldron's top rivet, the chest strap's studs, the left knee pad's bottom, a tail ring
    (10, 13, "j"), (13, 19, "j"), (15, 19, "j"), (18, 19, "j"),
    (31, 20, "b0"), (32, 20, "0"), (29, 14, "c0"),
    # outline squares on dropped lines
    (5, 31, "0"), (22, 14, "0"), (28, 33, "0"), (31, 15, "0"), (32, 31, "0"), (32, 40, "0"),
    (33, 14, "0"), (33, 19, "0"), (34, 28, "0"), (34, 39, "0"), (35, 12, "0"), (35, 38, "0"),
    (36, 33, "0"), (37, 33, "0"),
]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


RGB = {k: hx(v) for k, v in PAL.items()}


def lab(rgb):
    c = np.asarray(rgb, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def letters(a):
    keys = list(PAL)
    pl = lab(np.array([RGB[k] for k in keys]))
    near = ((lab(a[..., :3])[..., None, :] - pl[None, None]) ** 2).sum(-1).argmin(-1)
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


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def close_outline(a):
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    p, _, _ = strips.complete_outline(p, color=RGB["0"], feet=a.shape[0], keep=None)
    return crop(p)


def even_drop(lines, weights, lo, hi, q, hard):
    """q deletions in lo..hi, the i-th near lo + (i + 0.5) * L / q (+-JITTER, wider when hard lines are in the way),
    never two neighbours, the cheapest (a deleted line costs its weighted difference from the nearer neighbour)."""
    def cost(j, k):
        return float(((lines[j] != lines[k]) * np.maximum(weights[j], weights[k])).sum())

    L = hi - lo + 1
    cands = []
    for i in range(q):
        p = lo + (i + 0.5) * L / q - 0.5
        j = JITTER
        while True:
            c = [x for x in range(int(round(p)) - j, int(round(p)) + j + 1)
                 if lo <= x <= hi and x not in hard and 0 < x < len(lines) - 1]
            if len(c) >= 2 or j > 4:
                break
            j += 1
        cands.append(c)
    best = [{x: (min(cost(x, x - 1), cost(x, x + 1)), None) for x in cands[0]}]
    for i in range(1, q):
        cur = {}
        for x in cands[i]:
            prev = [(v[0], px) for px, v in best[-1].items() if x - px >= 2]
            if prev:
                v, px = min(prev)
                cur[x] = (v + min(cost(x, x - 1), cost(x, x + 1)), px)
        best.append(cur)
    x = min(best[-1], key=lambda k: best[-1][k][0])
    out = [x]
    for i in range(q - 1, 0, -1):
        x = best[i][x][1]
        out.append(x)
    return sorted(out)


def cut(rows):
    idx = np.array([[ord(c) for c in r] for r in rows])
    w = np.vectorize(lambda v: WEIGHT.get(chr(v), 1))(idx)
    H, W = idx.shape
    dr = []
    for lo, hi, q in ROW_PARTS:
        dr += even_drop([idx[y] for y in range(H)], [w[y] for y in range(H)], lo, hi, q, HARD_ROWS | FACE_ROWS)
    kr = [y for y in range(H) if y not in dr]
    sub, ws = idx[kr], w[kr]
    dc = []
    for lo, hi, q in COL_PARTS:
        dc += even_drop([sub[:, x] for x in range(W)], [ws[:, x] for x in range(W)], lo, hi, q, FACE_COLS)
    kc = [x for x in range(W) if x not in dc]
    return ["".join(chr(v) for v in r) for r in sub[:, kc]], dr, dc


def polish(rows):
    g = [list(r) for r in rows]
    for y, x0, text in POLISH:
        for i, ch in enumerate(text):
            if ch != " ":
                g[y][x0 + i] = " " if ch == "." else ch
    return ["".join(r) for r in g]


def on_canvas(fig):
    fig = crop(fig)
    feet = np.nonzero((fig[-3:, :, 3] > 0).any(0))[0]
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - (feet.min() + feet.max()) / 2))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def rebuild():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    base = letters(raw)
    rows, dr, dc = cut(base)
    rows = from_rgba(close_outline(to_rgba(rows)))
    rows = from_rgba(close_outline(to_rgba(polish(rows))))
    print(f"read back {len(base)} x {len(base[0])}; rows dropped {dr}; columns dropped {dc}")
    return on_canvas(to_rgba(rows))


def write_letters(can, path):
    ys, xs = np.nonzero(can[..., 3] > 0)
    x0 = xs.min()
    inv = {v: k for k, v in RGB.items()}
    with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# x0 {x0}\n")
        for y in range(ys.min(), ys.max() + 1):
            f.write(f"{y:3d}" + "".join(inv[tuple(int(v) for v in can[y, x, :3])] if can[y, x, 3] else " "
                                        for x in range(x0, xs.max() + 1)).rstrip() + "\n")


def final():
    can = np.zeros((128, 128, 4), np.uint8)
    x0 = 0
    for line in open(lp(FINAL), encoding="utf-8"):
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
    ap.add_argument("--final", action="store_true", help="write FINAL to OUT")
    ap.add_argument("--check", action="store_true", help="compare FINAL with the committed OUT")
    ap.add_argument("--rebuild", action="store_true", help="the route from the raw draft, compared with FINAL")
    ap.add_argument("--write-letters", action="store_true", help="with --rebuild: (re)write FINAL from the route")
    a = ap.parse_args()
    if a.rebuild:
        can = rebuild()
        if a.write_letters:
            write_letters(can, FINAL)
            print("wrote", FINAL)
        elif os.path.exists(lp(FINAL)):
            old = final()
            print("same as FINAL" if (old == can).all() else
                  f"differs from FINAL in {int((old != can).any(-1).sum())} squares (FINAL has hand edits?)")
        return
    can = final()
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))[4::8, 4::8]
        print("same" if (old == can).all() else f"differs in {int((old != can).any(-1).sum())} squares")
        return
    if a.final:
        Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(lp(OUT))
        print("wrote", OUT, "box", Image.fromarray(can).getbbox())


if __name__ == "__main__":
    main()

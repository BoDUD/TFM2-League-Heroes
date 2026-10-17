#!/usr/bin/env python3
"""Zed's game-size design (step 1) from Codex's generator draft (assets/source/zed/codex_model/raw).

    python tools/art/design_zed.py --final      # the approved letter grid (FINAL) -> assets/source/native/zed_native.png
    python tools/art/design_zed.py --check      # FINAL vs the committed native design
    python tools/art/design_zed.py --rebuild    # the whole route again from the raw draft; compared with FINAL

How it came about (2026-10-09): the user picked Codex's picture A (League's idle: hunched forward, two silver blades
hanging from each wrist). Codex's step 1 drew two generator drafts (squares of ~19 px: 50 x 32 and 53 x 34) and made
its own 27 x 40 finals from them by recolouring and row/column deletions - the gold face mask became a maroon blob. The
drafts themselves are good, so (the Rengar route):
  1. draft 1 read back on its own grid (the skill's regrid.py) - 50 x 32;
  2. every square to the nearest of PAL (CIELAB): the drafts' own colours (k-means 32 of both read-backs, merged by
     hand), the eye slits (E) kept apart;
  3. whole rows and columns deleted to 40 rows, EVENLY per part, each deletion free to move one line to the cheapest
     neighbour, never two neighbours, never a hard line (the helmet's rows 12-20 and columns 15-25, the soles' rows
     46-49). The user picked 「3」 (this cut); its column deletions had taken both bracers'
     outer silver spurs (columns 1 and 30), so those two are hard too and the deletions move next door (2 and 29);
  4. strips.complete_outline;
  5. on the 128 x 128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
The user approved it (「可以了」, 2026-10-09): 40 x 27, 20 colours, the outline closed.
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

RAW = os.path.join(ROOT, "assets", "source", "zed", "codex_model", "raw", "zed_design_1_raw.png")
FINAL = os.path.join(ROOT, "assets", "source", "zed", "design", "zed_design_40.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "zed_native.png")
SOLE_ROW, MID_COL = 99, 64

PAL = {
    "0": "#020206",   # outline
    "a": "#73011C",   # maroon (cloth dark)
    "b": "#95001F",   # crimson dark
    "c": "#C80823",   # crimson
    "d": "#DD0623",   # crimson light
    "n": "#292A3E",   # navy darkest (trousers, helmet dark)
    "m": "#363955",   # navy dark
    "o": "#424462",   # navy / gunmetal
    "p": "#5A5D80",   # gunmetal light
    "q": "#686B8B",   # steel dark
    "s": "#8991B1",   # steel
    "t": "#A3ABC6",   # silver mid
    "u": "#D7DEF0",   # silver light
    "w": "#E6EBF8",   # silver white
    "i": "#785634",   # bronze dark
    "h": "#B0722E",   # bronze / gold dark
    "g": "#E39B33",   # gold mid
    "j": "#FBBB40",   # gold
    "l": "#FCCD5E",   # gold light
    "E": "#F70209",   # the eye slits
}

# step 3: even deletions per part (first, last, deletions) on the read-back; hard lines never deleted
FACE_ROWS, FACE_COLS = set(range(12, 21)), set(range(15, 26)) | {1, 30}
ROW_PARTS = [(0, 11, 3), (21, 49, 7)]
COL_PARTS = [(0, 14, 3), (26, 31, 2)]
HARD_ROWS = {46, 47, 48, 49}
JITTER = 1
WEIGHT = {"E": 20, "j": 4, "l": 4, "g": 3, "u": 3, "w": 3}

# step 5: (row, first column, letters) on the cut figure; '.' clears a square (none: approved as cut)
POLISH = []


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

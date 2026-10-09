#!/usr/bin/env python3
"""Karma's game-size design (step 1) from Codex's generator drafts (assets/source/karma/codex_model/raw).

    python tools/art/design_karma.py --base [1|2]        # print a draft's read-back as letters (row/column numbers)
    python tools/art/design_karma.py --cuts OUT_DIR      # the size options for the user (PNGs + letter files)
    python tools/art/design_karma.py --final             # the approved letter grid (FINAL) -> assets/source/native

How it came about (2026-10-09): the user picked Codex's picture A (League's idle, standing calm in 3/4 view). Codex's
step 1 drew two generator drafts of ~7 px squares (karma_design_1/2_generator.png: version 1 the bigger jade ring,
version 2 the smaller ring) and sampled them itself to 42/40 rows (muddy: hair a blob, the ring broken). Here, as for
league_kogmaw and league_rengar:
  1. read back on its own grid (the skill's regrid.py) - 62 x 33 (1) and 60 x 31 (2);
  2. every square to the nearest of PAL (CIELAB) - the drafts' own colours (24 clusters);
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

RAW = {v: os.path.join(ROOT, "assets", "source", "karma", "codex_model", "raw", f"karma_design_{v}_generator.png")
       for v in "12"}
FINAL = os.path.join(ROOT, "assets", "source", "karma", "design", "karma_design.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "karma_native.png")

PAL = {
    "0": "#030202",   # outline
    "k": "#150616",   # hair darkest
    "h": "#220C25",   # hair dark
    "H": "#370644",   # hair light / dress darkest
    "u": "#42074B",   # dress dark
    "v": "#5F0970",   # dress violet
    "z": "#452320",   # skin darkest
    "S": "#825238",   # skin shade
    "s": "#C4815A",   # skin
    "G": "#C7864A",   # gold dark
    "g": "#EEB956",   # gold
    "W": "#BAB0AD",   # wrap shade
    "x": "#DDDBC4",   # wrap mid
    "w": "#F5EDE8",   # wrap light
    "P": "#780C4B",   # pink dark
    "p": "#E3118E",   # pink (hem, eyes, tassels)
    "m": "#5C7D5F",   # jade dark
    "j": "#91CD9F",   # jade
    "J": "#ABDCB3",   # jade light
    "l": "#CAE7C0",   # jade pale
    "e": "#1BB663",   # the gem / tattoo green
    "i": "#F2E9C6",   # ivory prongs
    "b": "#222048",   # boots
    "n": "#2C302A",   # dark green-grey line
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


WEIGHT = {"p": 12, "e": 12, "g": 4, "w": 3, "j": 3, "s": 2}
# size options: name -> (draft, row parts, column parts, hard rows, hard cols) as (first, last, deletions)
H1 = set(range(18, 26)) | {58, 59, 60, 61}         # draft 1: the face (eyes 20-21, chin 25) and the boots
H2 = set(range(16, 23)) | {56, 57, 58, 59}         # draft 2: the face (eyes 18-19, chin 22) and the boots
C1, C2 = set(range(11, 23)), set(range(10, 22))     # the face's columns
CUTS = {
    "1_46": ("1", [(0, 9, 3), (10, 17, 2), (26, 57, 11)], [(0, 10, 2), (23, 32, 1)], H1, C1),
    "1_42": ("1", [(0, 9, 4), (10, 17, 3), (26, 57, 13)], [(0, 10, 2), (23, 32, 2)], H1, C1),
    "1_40": ("1", [(0, 9, 5), (10, 17, 3), (26, 57, 14)], [(0, 10, 3), (23, 32, 2)], H1, C1),
    "2_44": ("2", [(0, 6, 2), (7, 15, 2), (23, 55, 12)], [(0, 9, 1), (22, 30, 1)], H2, C2),
    "2_42": ("2", [(0, 6, 2), (7, 15, 3), (23, 55, 13)], [(0, 9, 2), (22, 30, 1)], H2, C2),
    "2_40": ("2", [(0, 6, 3), (7, 15, 3), (23, 55, 14)], [(0, 9, 2), (22, 30, 2)], H2, C2),
    # the user on 2_42 (2026-10-09): 「手和腿再挑挑吧 有点怪」 - the cut had dropped draft rows 31 and 33, so the far
    # forearm (rows 30-35) collapsed into an outline stroke and the near hand vanished; these keep the arms whole and
    # take the body's rows from the waist and the skirt instead
    "2_42a": ("2", [(0, 6, 2), (7, 15, 4), (23, 28, 3), (36, 55, 9)], [(0, 9, 2), (22, 30, 1)],
              H2 | set(range(29, 36)), C2),
    "2_43a": ("2", [(0, 6, 2), (7, 15, 3), (23, 28, 3), (36, 55, 9)], [(0, 9, 2), (22, 30, 1)],
              H2 | set(range(29, 36)), C2),
    "2_43b": ("2", [(0, 6, 2), (7, 15, 4), (23, 28, 3), (36, 46, 6), (51, 55, 2)], [(0, 9, 2), (22, 30, 1)],
              H2 | set(range(29, 36)) | {47, 48, 49, 50}, C2),
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


PICK = "2_42"          # the user's pick (「那就2-42吧」)
# hand edits on the picked cut, in FINAL's coordinates: (canvas row, column from x0, letters; '.' clears).
# Tried 2026-10-09 and withdrawn: (82, 23, "ss"), (83, 23, "00") joined the far forearm to the hand (「你把这个色素缺失
# 的补上就行了」), then the user kept the cut as it was (「算了就用这个吧」, pointing at the "before" picture).
# 1. 「可以优化一下眼睛这个五官 做精致点」 -> the user's 「眼睛用A」 (legs left as they are: 「腿不用换」): both eyes a 2x2
#    magenta iris (P / p) with a white glint up-right under a lash row, the far eye moved onto the face (cols 69-70,
#    col 71 skin), a nose shade, plum lips, thinner brows (work/kr/edit/face_legs_kr.py option A without LEG)
POLISH = [(69, 12, "zS"), (69, 19, "z"),
          (70, 12, "0000   000"), (71, 13, "Pw0   Pws"), (72, 13, "pPs   pPS"),
          (73, 19, "S"), (74, 17, "PP"),
          # 2. 「把腿上绿色的点删了吧」: the leg's one jade tattoo square becomes skin (its neighbours above and below)
          (92, 18, "s"),
          # 3. 「眼睛要做的特色一点 比如莎米拉的眼睛就做的非常好」: Samira's framing (a lash row above, a lower lash, a coloured
          #    liner flick at the outer corner, a white glint) with League Karma's own marks (glowing magenta irises, dark
          #    winged liner, the dark tear streak under the near eye): the near eye 3 wide, thin brows, the dark square
          #    between the brows gone (work/kr/edit/eyes2_kr.py option C2)
          (69, 12, "hzzsssszz"), (70, 11, "00000"), (71, 12, "Ppw0"), (71, 19, "pwP"), (72, 12, "PpPs"),
          (72, 19, "PpS"), (73, 12, "S0"), (74, 13, "z")]


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
        Image.fromarray(fig).save(os.path.join(out_dir, f"karma_cut{name}.png"))
        with open(os.path.join(out_dir, f"karma_cut{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
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

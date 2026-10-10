#!/usr/bin/env python3
"""Syndra's game-size design (step 1) from Codex's generator drafts (assets/source/syndra/codex_model/raw).

    python tools/art/design_syndra.py --final [--check]   # PICK -> assets/source/native/syndra_native.png
    python tools/art/design_syndra.py --tryn 3 42 --tryn-out x.png   # one option, league_tryndamere's way
    python tools/art/design_syndra.py --base 3             # a draft's read-back as letters (row/column numbers)
    python tools/art/design_syndra.py --cuts OUT_DIR       # the first round of options (even cuts)

How it came about (2026-10-11): the user picked Codex's picture A (League's idle1: floating, arms spread down, one knee
bent). Codex's step 1 drew three generator drafts (raw/generation-1/2/3.png): 1 the picture's detail (109 x 83 on its
10 px grid), 2 a chunkier redraw (67 x 44, 14 px), 3 a chibi redraw (53 x 33 on its 17 px grid); its own A / B were
draft 3 cut by whole rows only (30 wide, squat). First round: draft 3 cut evenly per part (league_senna's way, CUTS) -
the user picked 「3_42」, then 「眼睛上脏的黑色素清理掉 全身也是」 / 「还有缺失色素的地方补一补 精修一下」 and
「之前蛮王什么的弄的不是挺好的吗 就按照那种方式」: so league_tryndamere's way (tryn()): draft 3 read on its own grid, its
own 24 colours, whole rows and columns dropped where least is lost, the face kept, only the outline closed - 「第三稿→42」
(26 x 42 on the 128 canvas: the lowest toe on row 99, column 64).
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


# 2026-10-11 the user's crops (Screenshots 002951 / 003003): 「眼睛旁边多了一块元素 左腿缺失了元素」 - a black square right
# of the near eye and a black square where the image-left thigh meets its gold boot top: both the skin's colour
# and (rig_syndra's audit, 2026-10-11) three 1-square pinholes inside outline rings - between the image-right arm and
# the body (83,68), (84,69) and in the hair at the left (88,52): the ground showed through them; the outline's colour
FIXES = [(71, 64, "#FDC087"), (90, 63, "#FDC087"),
         (83, 68, "#100117"), (84, 69, "#100117"), (88, 52, "#100117")]       # (canvas row, column, colour) after tryn(*PICK)
PICK = ("3", 42)       # the user's pick: draft 3 at 42 rows, league_tryndamere's way (「第三稿→42」, 2026-10-11); the
                       # even cuts (CUTS, 「3_42」 first) were dropped for their dirty black squares round the eyes


# league_tryndamere's way (the user, 2026-10-11: 「之前蛮王什么的弄的不是挺好的吗 就按照那种方式」, design_tryndamere.py):
# a draft read back on its own grid, every square one of K colours of the read-back's own (design_varus.kmeans), whole
# rows then columns deleted by design_riven.keep_axis (in each group the line most like a neighbour goes, three offsets,
# the least loss kept), the width in proportion, never the face's rows / columns nor row 0 (the horn tips), then only
# strips.complete_outline (the face kept). Draft 1: 109 x 83 on its 10 px grid (the picture's detail); draft 2: 67 x 44.
TRYN = {"1": (range(24, 33), range(43, 56)), "2": (range(21, 30), range(12, 24)), "3": (range(15, 23), range(11, 21))}
K = 24


def tryn(v, height):
    import design_riven as DR
    import design_varus as dv
    raw, _, _ = regrid(np.asarray(Image.open(R.lp(RAW[v])).convert("RGBA")), SQUARE[v])
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    fr_, fc_ = TRYN[v]
    face = range(fr_.start - 1, fr_.stop - 1)
    rows = [0] + [r + 1 for r in DR.keep_axis([idx[y] for y in range(1, H)], height - 1, face)]
    sub = idx[rows]
    cols = DR.keep_axis([sub[:, x] for x in range(W)], round(W * height / H), fc_)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in fr_]
    fc = [cols.index(c) for c in fc_]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    ink = tuple(int(c) for c in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=ink, feet=fig.shape[0], keep=np.pad(keep, 1))
    return on_canvas(R.crop(can)), rows, cols, added


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", nargs="?", const="2")
    ap.add_argument("--cuts", metavar="OUT_DIR")
    ap.add_argument("--final", action="store_true", help="write PICK to OUT (--check: compare instead)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tryn", nargs=2, metavar=("DRAFT", "ROWS"), help="league_tryndamere's way: write a PNG option")
    ap.add_argument("--tryn-out")
    a = ap.parse_args()
    if a.final:
        can, rows, cols, added = tryn(*PICK)
        for y, x, col in FIXES:
            can[y, x, :3] = R.hx(col)
            can[y, x, 3] = 255
        bb = Image.fromarray(can).getbbox()
        info = f"{bb[2] - bb[0]} x {bb[3] - bb[1]} box {bb}, outline +{added}, rows kept {rows}, cols kept {cols}"
        if a.check:
            old = np.asarray(Image.open(R.lp(OUT)).convert("RGBA"))[4::8, 4::8]
            print("identical" if np.array_equal(old, can) else "DIFFERENT", info)
        else:
            Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(R.lp(OUT))
            print("wrote", OUT, info)
    if a.base:
        show(base(a.base))
    if a.tryn:
        can, rows, cols, added = tryn(a.tryn[0], int(a.tryn[1]))
        Image.fromarray(can).save(R.lp(a.tryn_out))
        bb = Image.fromarray(can).getbbox()
        print(f"draft {a.tryn[0]}: {bb[2] - bb[0]} x {bb[3] - bb[1]}, outline +{added}, rows kept {rows}, cols kept {cols}")
    if a.cuts:
        os.makedirs(a.cuts, exist_ok=True)
        options(a.cuts)


if __name__ == "__main__":
    main()

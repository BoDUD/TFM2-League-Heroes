#!/usr/bin/env python3
"""Seraphine's design (assets/source/native/seraphine_native.png): Codex's game-size draft read back on its own grid,
cut to 52 rows by whole rows and columns, region by region.

    python tools/art/design_seraphine.py [--check] [--review OUT.png]

How it came about (2026-10-07): the user picked Codex's picture A (codex_picture/seraphine-model-A.png: she stands on
her floating stage, one gloved hand at her ear, the pink hair streaming behind). For the game-size step Codex drew
codex_model/seraphine_design_1.png (the 12-square head version, ~11 px squares on 1254 x 1254) that reads back 73 x 51
squares - far over the 46 asked. Cut candidates (whole rows / columns at 46 and 52, a block vote at 46, region quotas
at 46 and 52) went to the user, who picked the region cut at 52 (「E 分区删到 52 行」); a 48-row cut was rejected
(「48明显不行」, 「还是52吧」). Steps:
  1. the draft read back on its own grid (the skill's regrid.py): 73 x 51;
  2. the opaque squares median-cut to 36 colours (PIL, deterministic);
  3. the rows and columns kept by tools/art/design_akali.dp_keep, region by region: the curl 7 -> 5 rows, the head and
     the hair 31 -> 21 (the eyes' rows 21-25 never deleted), the top and the skirt 11 -> 8, the legs 10 -> 8, the
     stage 14 -> 10; the columns 51 -> 36 (the face's columns 27-37 never deleted) - weights: the eye blues 10, gold 3;
  4. on the 128x128 canvas at 8x: the stage's bottom on row 99, the stage's middle on column 64;
  5. strips.complete_outline (one outline square outside every light edge, nothing under the stage);
  6. the face redrawn after Gwen's (FACE; the user: 「脸的质量有点差 灵活运用工具修一修啊」「参考格温怎么弄的 多精致」 and a crop of
     the chin, 「这里全是个啥啊」);
  7. the legs and the boots redrawn (LEGS; 「这里也是」 with a crop of them - the draft itself drew them crudely); the
     one-square gaps in the outline under the raised arm's elbow and under the near glove closed (NOTCH, 「这里少一块？」);
  8. Gwen's clean-up off the drawn squares: lone squares no neighbour shares take their four neighbours' colour (two
     rounds, gold kept), then outline squares that join no line take their neighbours' colour;
  9. shrunk (「萨勒芬妮在游戏里实在太大了」, 「还有感觉有点胖啊模型」, 「萨勒芬妮头有点大」): the figure 37 rows by whole rows
     (the head 15 of them), 6 columns from the back hair and 2 a side from the shoulders down, the crown rounded (DOME),
     the stage drawn again at 24 x 6; old_to_new() maps a point of step 8 for tools/art/rig_seraphine.py.
--check compares the result with the committed seraphine_native.png instead of writing it.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "seraphine", "codex_model", "seraphine_design_1.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "seraphine_native.png")
COLOURS = 36
SOLE_ROW, MID_COL = 99, 64
ROWS = [0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 19, 21, 22, 23, 24, 25, 27, 28, 30, 31, 32, 33, 34, 36, 37, 38, 39, 41, 42,
        43, 44, 46, 48, 49, 50, 51, 52, 53, 55, 57, 58, 60, 62, 63, 64, 65, 66, 67, 68, 69, 71]
COLS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 18, 19, 20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        41, 42, 43, 45, 47, 49]


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


C = {"I": hx("#0D0222"), "W": hx("#FDFCFE"), "B": hx("#13136E"), "C": hx("#01BFFA"), "c": hx("#80D4F2"),
     "G": hx("#FDDAB8"), "N": hx("#F2B89A"), "K": hx("#F8A0A8"), "P": hx("#E8506E"), "h": hx("#EEE5E5"),
     "g": hx("#FC3581"), "d": hx("#C81260"), "s": hx("#5E0333"), "y": hx("#F7BD3A"), "n": hx("#444959"),
     "v": hx("#17093C"), "q": hx("#FCCF8A"), "z": hx("#0483C4"),
     "L": hx("#D8D2EE"), "M": hx("#A8A0C8"), "Y": hx("#BC7B25"), "w": hx("#CFCBE4"), "O": hx("#8A4A24"),
     "o": hx("#4A2412"), "b": hx("#B87040")}
# step 7 (「这里也是」, the legs and boots): two clean legs - the near one silver-lilac with a gold curl on the shin,
# the far one white - and two brown boots with gold cuffs, toes forward, on the deck; rows: (first column, string),
# '-' keeps the square, '.' clears it
LEGS = {
    82: (56, "----IGGGNI.IGGGGNI--"),
    83: (56, "----ILLLMI.IWWWWwI--"),
    84: (56, "---ILLLLMI.IWWWWwI--"),
    85: (56, "--.ILyLMI..IWWWWwI--"),
    86: (56, "--ILyyLMI..IWWWwI---"),
    87: (56, "-IyyyyYI...IyyyyYI--"),
    88: (56, ".IbOOOoI...IbOOOoI--"),
    89: (56, ".IbOOOOoI..IbOOOOoI-"),
    90: (56, "-IIIIIIII--IIIIIIIII"),
}

# step 7b (「这里少一块？」, then 「你没修好啊」): the raised far arm's elbow had a one-square gap in its lower outline at
# (76, 73) that showed the background - the square the user pointed at; the near glove's lower outline had one too at
# (59, 81), closed first by mistake for it
NOTCH = {73: (76, "I"), 81: (59, "I")}
# step 6 (「脸的质量有点差」, the chin crop 「这里全是个啥啊」): Gwen's cute face - a lash row, 3 x 3 eyes (white top-left,
# dark blue, bright and light cyan below), a blush square pair, a one-square mouth, the chin closed, a 4-square neck,
# a navy choker with a cyan gem, a pendant dot
FACE = {
    60: (61, "-IIII-----IIII--"),
    61: (61, "-GWBBGGGGGWBBG--"),
    62: (61, "-GBCCGGGGGBCCG--"),
    63: (61, "-GCcCGGGGGCcCG--"),
    64: (61, "-GKKGGGGGGGKKG--"),
    65: (61, "-GGGGGGPGGGGGG--"),
    66: (61, "-IGGGGGGGGGGGI--"),
    67: (61, "--IIGGGGGGGGII--"),
    68: (61, "-G--IINNNNII----"),
    69: (61, "-GGGGBBCBBGGG---"),
    70: (61, "--GGGGGcGGGGG---"),
}


def paint(can, table):
    out = can.copy()
    for y, (x0, row) in table.items():
        for i, ch in enumerate(row):
            if ch == "-":
                continue
            if ch == ".":
                out[y, x0 + i] = 0
                continue
            out[y, x0 + i, :3] = C[ch]
            out[y, x0 + i, 3] = 255
    return out


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
GOLDS = {C["y"], C["Y"], hx("#FCBA5F"), hx("#BC7B25")}


def painted(*tables):
    """The squares the tables draw."""
    m = np.zeros((128, 128), bool)
    for t in tables:
        for y, (x0, row) in t.items():
            for i, ch in enumerate(row):
                if ch != "-":
                    m[y, x0 + i] = True
    return m


def lone(a, keep, rounds=2, need=2):
    """Squares no 8-neighbour shares take their four neighbours' commonest colour (not gold, not keep)."""
    n = 0
    for _ in range(rounds):
        b = a.copy()
        for y in range(1, 127):
            for x in range(1, 127):
                if a[y, x, 3] == 0 or keep[y, x]:
                    continue
                p = tuple(int(v) for v in a[y, x, :3])
                if p in GOLDS:
                    continue
                n8 = [a[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
                if any(q[3] == 0 for q in n8) or any(tuple(int(v) for v in q[:3]) == p for q in n8):
                    continue
                n4 = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy, dx in N4]
                best = max(set(n4), key=n4.count)
                if n4.count(best) >= need and best not in GOLDS:
                    b[y, x, :3] = best
                    n += 1
        a = b
    return a, n


def lone_ink(a, keep, ink):
    """Near-black squares inside the figure joining no line take their neighbours' commonest colour."""
    op = a[..., 3] > 0
    isk = op & (a[..., :3] == np.array(ink, np.uint8)).all(-1)
    hits = []
    for y, x in zip(*np.nonzero(isk & ~keep)):
        nb = [(y + dy, x + dx) for dy, dx in N4]
        if not all(op[yy, xx] for yy, xx in nb) or sum(isk[yy, xx] for yy, xx in nb) > 1:
            continue
        cols = [tuple(int(v) for v in a[yy, xx, :3]) for yy, xx in nb if not isk[yy, xx]]
        hits.append((y, x, max(set(cols), key=cols.count)))
    out = a.copy()
    for y, x, c in hits:
        out[y, x, :3] = c
    return out, len(hits)



def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    assert raw.shape[:2] == (73, 51), raw.shape
    return raw


def palette(raw):
    """Every opaque square the colour of its median-cut box."""
    m = raw[..., 3] > 0
    q = Image.fromarray(raw[m][:, :3][None].astype(np.uint8)).quantize(COLOURS, method=Image.Quantize.MEDIANCUT)
    pal = np.array(q.getpalette()[:COLOURS * 3], np.uint8).reshape(-1, 3)
    out = np.zeros_like(raw)
    out[m, :3] = pal[np.array(q)[0]]
    out[m, 3] = 255
    return out, pal


def build(full=False):
    a, pal = palette(read_back())
    outline = tuple(int(v) for v in pal[np.argmin(pal.astype(int).sum(1))])
    a = a[np.ix_(ROWS, COLS)]
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    low = np.nonzero(a[-3:, :, 3].any(0))[0]
    can = np.zeros((128, 128, 4), np.uint8)
    y0 = SOLE_ROW + 1 - a.shape[0]
    x0 = int(round(MID_COL - (low.min() + low.max()) / 2))
    can[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    can, added, darkened = strips.complete_outline(can, color=outline, feet=SOLE_ROW)
    can = paint(paint(can, FACE), LEGS)
    keep = painted(FACE, LEGS)
    can, _ = lone(can, keep)
    can, _ = lone_ink(can, keep, C["I"])
    can = paint(can, NOTCH)                              # after the clean-up, which would spread it
    if full:
        return can, added, darkened
    return shrink(can, outline), added, darkened


# step 9 (「萨勒芬妮在游戏里实在太大了 整体缩小一点」, the user picked 「C 身体和舞台都缩 → 42 行」): the figure 42 -> 36 rows by
# whole rows region by region (design_akali.dp_keep: the hair over the face 12 -> 9 with the curl's top kept, the torso
# 12 -> 10, the legs 9 -> 8; the face from the lashes to the choker, rows 60-68, untouched) and 38 -> 32 columns, all
# from the back hair (the face, the hands and the glove keep theirs); the stage, which no cut kept readable at 6 rows
# (the flower medallion and the crystals turned to mush), drawn again at 24 x 6 after the design's: the teal deck, the
# gold hull, the blue flower medallion with its pink orb, a cyan crystal on each side, left-right symmetric.
BODY_ROWS = [48, 50, 52, 55, 56, 57, 58, 60, 61, 62, 63, 64, 65, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
             81, 82, 83, 84, 85, 86, 87, 88, 89]
DROP_COLS = [43, 45, 47, 49, 51, 55]
# 「还有感觉有点胖啊模型」 (the user picked 「C 两边各收 2 列 + 高 45」): the 36-row cut kept the body's full width, so she
# read squat; three of the cut rows came back (73, 75 in the torso, 84 in the legs) and from the shoulders down two
# columns go on each side - 61-62 left of the middle from row 69, 70-71 right of it from row 73 (under the raised arm)
SLIM = [(69, (61, 62)), (73, (70, 71))]
# 「萨勒芬妮头有点大」 and 「最上面的方形看起来是平的 好奇怪」 (the user picked 「B 头顶少 2 行 + 下巴少 1 行」): two more hair
# rows over the face (53 and 59) and the chin's middle row (66) go - the head
# 18 -> 15 rows - and the crown, cut flat by the row cuts, is rounded: its first DOME_RY - 1 wide rows keep only what lies
# in an ellipse round the head's middle column (the curl above them and the blue fins stay)
DOME_CX, DOME_RX, DOME_RY = 66.5, 12.5, 6
BODY_TOP = SOLE_ROW + 1 - 6 - len(BODY_ROWS)             # the figure's new top row; its feet on row 93, the deck under


def kept_cols(r):
    """The columns of old row r the shrunk design keeps."""
    gone = set(DROP_COLS)
    for r0, cols in SLIM:
        if r >= r0:
            gone |= set(cols)
    return [c for c in range(128) if c not in gone]


STAGE_C = {"t": hx("#0483C4"), "T": hx("#01BFFA"), "g": hx("#F7BD3A"), "G": hx("#BC7B25"), "c": hx("#80D4F2"),
           "r": hx("#13136E"), "p": hx("#FC3581"), "P": hx("#FC4187")}   # its own letters (C's are the face's)
STAGE = ["0ttTttttttttttttttttTtt0",
         "0gGgcgg0rTTTTTTr0ggcgGg0",
         ".0gGggg0rTppppTr0gggGg0.",
         "..0gGgg0rTpPPpTr0ggGg0..",
         "...0ggg0rrTTTTrr0ggg0...",
         "....0000000000000000...."]
STAGE_X0 = MID_COL - len(STAGE[0]) // 2


def old_to_new(x, y):
    """A point of the 52-row design (step 8) on the shrunk one: rows by the kept rows (a point between two keeps lands
    proportionally), columns by their rank among the row's kept columns, the middle column staying put."""
    if y >= BODY_ROWS[-1] + 1:                           # the stage: its 10 rows pressed into 6, its columns as drawn
        return x, SOLE_ROW + 1 - len(STAGE) + (y - 90) * len(STAGE) / 10
    ny = BODY_TOP + float(np.interp(y, BODY_ROWS, range(len(BODY_ROWS))))
    r = min(BODY_ROWS, key=lambda k: abs(k - y))
    cols = kept_cols(r)
    rank = float(np.interp(x, cols, range(len(cols))))
    return MID_COL + rank - cols.index(MID_COL), ny


def shrink(can, outline):
    out = np.zeros_like(can)
    for i, r in enumerate(BODY_ROWS):
        cols = kept_cols(r)
        x0 = MID_COL - cols.index(MID_COL)
        row = can[r, cols]
        out[BODY_TOP + i, max(0, x0):x0 + len(cols)] = row[max(0, -x0):128 - x0]
    for i, row in enumerate(STAGE):
        y = SOLE_ROW + 1 - len(STAGE) + i
        for j, ch in enumerate(row):
            if ch != ".":
                out[y, STAGE_X0 + j] = (*(outline if ch == "0" else STAGE_C[ch]), 255)
    out, _, _ = strips.complete_outline(out, color=outline, feet=SOLE_ROW)
    op = out[..., 3] > 0
    r0 = next(y for y in range(128) if op[y].sum() >= 14)    # the crown's first wide row (outline included)
    for i in range(DOME_RY - 1):
        half = DOME_RX * math.sqrt(max(0.0, 1 - ((DOME_RY - (i + 0.5)) / DOME_RY) ** 2))
        for x in range(128):
            r, g, bl = (int(v) for v in out[r0 + i, x, :3])
            if out[r0 + i, x, 3] and abs(x - DOME_CX) > half and not bl > r + 40:
                out[r0 + i, x] = 0
    out, _, _ = strips.complete_outline(out, color=outline, feet=SOLE_ROW)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a 6x review picture")
    a = ap.parse_args()
    can, added, darkened = build()
    big = Image.fromarray(can).resize((1024, 1024), Image.NEAREST)
    ys, xs = np.nonzero(can[..., 3] > 0)
    cols = len({tuple(c) for c in can[can[..., 3] > 0][:, :3]})
    print(f"seraphine_native: {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {cols} colours, "
          f"outline +{added} / darkened {darkened}, rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        same = np.array_equal(old, np.asarray(big))
        print("same as the committed file" if same else "DIFFERS from the committed file")
        sys.exit(0 if same else 1)
    big.save(lp(OUT))
    if a.review:
        crop = can[ys.min() - 2:ys.max() + 3, xs.min() - 2:xs.max() + 3]
        im = Image.fromarray(crop).resize((crop.shape[1] * 6, crop.shape[0] * 6), Image.NEAREST)
        bg = Image.new("RGBA", im.size, (92, 98, 86, 255))
        bg.alpha_composite(im)
        ImageDraw.Draw(bg).text((4, 4), "seraphine_native", fill=(255, 255, 255))
        bg.convert("RGB").save(a.review)
    print(OUT)


if __name__ == "__main__":
    main()

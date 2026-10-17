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
  9. shrunk (「萨勒芬妮在游戏里实在太大了」, 「还有感觉有点胖啊模型」): the figure 39 rows by whole rows
     (the head 18 of them), 6 columns from the back hair and 2 a side from the shoulders down, the crown rounded (DOME),
     the stage drawn again at 24 x 6; old_to_new() maps a point of step 8 for tools/art/rig_seraphine.py;
 10. the jaw tapered over three rows and the crown drawn again with the picture's curl (JAW, CROWN, head_fix).
 11. a smaller head with a new face, the hairstyle kept (2026-10-09, the user: 「萨勒芬妮应该是头过大 发型太少」; after my
     hair drafts 「做的太怪了 整个头部你都能改 包括眼睛」, their reference picture 「照着这个画」, then 「五官和头及格了」 and
     「用我之前的发型 但是脸换了」「保留粉色」): the old head (rows 50-71) cleared but the far arm's squares at her ear
     (rig_seraphine.FAR_OFF) and the back hair from row 66; HEAD2 drawn - a 15-row head (the old one 18), a round crown
     in the old pinks lit from the upper left, swept bangs, big lashed violet-blue eyes with a white catch-light, a small
     open mouth, blush; the old curl on top (CURL2), the blue ornaments at the sides (ORNAMENTS2), a lock behind the
     raised hand (it was left a square off the face), the hair behind the head's left side widening into the kept back
     hair (JOIN2), the old ear's skin squares left in that hair made hair and the pockets of ground the narrower jaw
     left beside it filled with dark hair (head2). The jaw narrows over its last two rows (11 -> 8 -> 5 squares, the
     near side two squares a row as on the old head) so the chin sits on the neck: 「脖子和脸连接那里有点怪吧」 - an
     8-square chin rested on the bare shoulder with no outline between them, two squares left of the neck (A of three).
 12. the shoulders slimmer (「身体也调一调吧 肩膀啥的 手臂也有点粗」): the near side's two columns of bare shoulder out
     (rows 72-76, NEAR_CUT2) - the near puffed sleeve and the near arm with its glove two squares in (the far side, the
     raised arm at her ear, stays: tools/art/rig_seraphine.py lifts its squares for every cast and they touch the
     face); what the sleeve and the arm left takes the back hair beside it; the near glove's outer column off; the
     outline closed (body2).
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
BODY_ROWS = [48, 50, 52, 53, 56, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77,
             78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
DROP_COLS = [43, 45, 47, 49, 51, 55]
# 「萨勒芬妮的头想办法给我缩小一点」 (after the merge; the user picked 「C 少 2 行 + 收 4 列」 of four, the rounded crown and the
# face kept): two hair rows under the crown (55, 57: they were in BODY_ROWS) and, down to the eyes' lower row (63), four
# hair columns beside the face - 57 and 59 between the left fin and the face, 76 and 77 between the face and the right fin
HEAD_COLS, HEAD_LAST = (57, 59, 76, 77), 63
# 「还有感觉有点胖啊模型」 (the user picked 「C 两边各收 2 列 + 高 45」): the 36-row cut kept the body's full width, so she
# read squat; three of the cut rows came back (73, 75 in the torso, 84 in the legs) and from the shoulders down two
# columns go on each side - 61-62 left of the middle from row 69, 70-71 right of it from row 73 (under the raised arm)
SLIM = [(69, (61, 62)), (73, (70, 71))]
# 「最上面的方形看起来是平的 好奇怪」: the crown, cut flat by the row cuts, is rounded - its first DOME_RY - 1 wide rows
# keep only what lies in an ellipse round the head's middle column (the curl above them and the blue fins stay). Two
# hair rows and a chin row fewer (「萨勒芬妮头有点大」, option B) were tried and dropped: the user kept the 45 rows with
# the rounded crown alone (「用这个啊 这个发型完美」, the preview's 「dome 32x45」)
DOME_CX, DOME_RX, DOME_RY = 66.5, 12.5, 6
# 「萨勒芬妮右腿少一块白色的」: the cuts left the far (white) stocking a column narrow on its last row over the boot (row
# 90: outline where its lilac shade square was) - the shade square back and the outline one column out, as the rows above
SOCK = {(70, 90): "#cfcbe4", (71, 90): "#0d0222"}
BODY_TOP = SOLE_ROW + 1 - 6 - len(BODY_ROWS)             # the figure's new top row; its feet on row 93, the deck under
# step 10 (2026-10-08, 「帮我修复一下萨勒芬妮的头部吧 也看着像正方形」, then pointing at the crown: 「头这里有点怪 可能是发型
#怪？」; the user picked 「S1 + crown」): the face, 13 squares wide with straight sides from the eyes to the mouth, tapers
# over three rows (JAW: the skin squares outside each row's span take the outline, or on row 69 the hair beside them):
# 13 -> 11 -> 9 -> 6 down to the chin; the crown (rows 54-60, cols 59-74 - the picture's curl had been cut to a flat
# dark-maroon block on a flat top row) is drawn again after picture A (CROWN): a round dome in the hair's pinks, the
# pink curl on its top-left hooking back to the left. Rows 61 down besides the jaw, the fins (cols 75-78) and the
# fringe stay.
JAW = {69: (63, 73), 70: (64, 72), 71: (66, 71)}
JAW_SKIN = "#fddab8"
CROWN = {   # row: {col: colour key}; every other square of cols 59-74 on these rows is cleared
    54: {60: "I", 61: "I", 62: "I", 63: "I"},
    55: {59: "I", 60: "E", 61: "H", 62: "H", 63: "E", 64: "I"},
    56: {59: "I", 60: "S", 61: "I", 62: "I", 63: "E", 64: "I"},
    57: {60: "I", 62: "I", 63: "E", 64: "I", 65: "I", 66: "I", 67: "I", 68: "I", 69: "I", 70: "I"},
    58: {62: "I", 63: "H", 64: "H", 65: "H", 66: "E", 67: "E", 68: "E", 69: "E", 70: "M", 71: "S", 72: "I"},
    59: {60: "I", 61: "E", 62: "H", 63: "H", 64: "E", 65: "E", 66: "E", 67: "E", 68: "E", 69: "E", 70: "M", 71: "S",
         72: "S", 73: "I"},
    60: {59: "I", 60: "E", 61: "E", 62: "H", 63: "E", 64: "E", 65: "E", 66: "E", 67: "E", 68: "E", 69: "E", 70: "E",
         71: "M", 72: "S", 73: "S", 74: "I"},
}
CROWN_C = {"I": "#0d0222", "E": "#fc3581", "H": "#fc4187", "M": "#d11563", "S": "#c81260"}


def head_fix(out):
    """Step 10: the jaw's taper and the crown (JAW, CROWN)."""
    skin = hx(JAW_SKIN)
    ink = hx(CROWN_C["I"])
    for r, (lo, hi) in JAW.items():
        for x in range(60, 77):
            if tuple(int(v) for v in out[r, x, :3]) == skin and out[r, x, 3] and not lo <= x <= hi:
                side = out[r, x - 1] if x < lo else out[r, x + 1]
                col = ink if tuple(int(v) for v in side[:3]) == ink or r >= 70 else tuple(int(v) for v in side[:3])
                out[r, x] = (*col, 255)
    for r, row in CROWN.items():
        out[r, 59:75] = 0
        for x, k in row.items():
            out[r, x] = (*hx(CROWN_C[k]), 255)
    return out


def kept_cols(r):
    """The columns of old row r the shrunk design keeps."""
    gone = set(DROP_COLS)
    if r <= HEAD_LAST:
        gone |= set(HEAD_COLS)
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
    for (x, y), c in SOCK.items():
        out[y, x] = (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255)
    return face3(body2(head2(head_fix(out))))


# step 11 ------------------------------------------------------------------------------------------------------------
HEAD2_C = {"0": "#0d0222", "1": "#fc4187", "2": "#fc3581", "3": "#e62574", "4": "#d31865", "5": "#c81260",
           "6": "#5f0033", "J": "#fddab8", "F": "#f2b89a", "C": "#f8a0a8", "x": "#e8506e",
           "w": "#ffffff", "E": "#4a5ad8", "e": "#2a2a8e", "L": "#8fa8f8",                 # the eyes
           "A": "#01bffa", "D": "#80d4f2", "d": "#001d45", "f": "#13136e"}                  # the ornaments' blues
# (first column, squares) per row; '0' outline, 1-6 the hair from light to dark, J/F skin, C blush, x mouth, eyes w E e L
HEAD2 = {57: [(63, "00000000")],
         58: [(62, "0"), (63, "22112233"), (71, "0")],
         59: [(61, "0"), (62, "1122223334"), (72, "40")],
         60: [(61, "0"), (62, "1222333344"), (72, "440")],
         61: [(59, "0021"), (63, "2223333444455"), (76, "0")],
         62: [(58, "0211"), (62, "2233334444455"), (75, "50")],
         63: [(58, "023322"), (64, "334433445"), (73, "5550")],
         64: [(58, "03344"), (63, "4434J44J4454"), (75, "50")],
         65: [(58, "0455"), (62, "0000JJJ0000J"), (74, "50")],
         66: [(58, "0456"), (62, "JwEeJJJwEeJJ"), (74, "50")],
         67: [(58, "0456"), (62, "JELEJJJELEJJ"), (74, "0")],
         68: [(58, "0456"), (62, "JeLeJJJeLeJJ"), (74, "0")],
         69: [(59, "056"), (62, "CJJJJJJJJCJ"), (73, "0")],
         70: [(60, "06"), (62, "00JJxxJJJJ"), (72, "0")],
         71: [(61, "00000"), (66, "JJJJJ"), (71, "0")]}
CURL2 = {54: [(64, "0000")], 55: [(63, "012210")], 56: [(63, "050020")], 57: [(64, "0"), (66, "0"), (67, "2")]}
ORNAMENTS2 = {(57, 62): "0", (57, 63): "0", (57, 64): "0", (57, 65): "0", (58, 62): "D", (58, 63): "D", (58, 64): "A",
              (58, 65): "d", (75, 61): "0", (76, 61): "0", (75, 62): "A", (76, 62): "0", (75, 63): "A", (76, 63): "0",
              (75, 64): "f", (76, 64): "0"}
LOCK2 = {65: "5", 66: "5", 67: "6", 68: "5", 69: "6", 70: "6", 71: "0"}          # column 75, behind the raised hand
JOIN2 = {63: (57, "012"), 64: (55, "01234"), 65: (53, "0123445"), 66: (52, "012345623")}
FAR_ARM2 = {67: (75, 76), 68: (76, 77), 69: (76, 77), 70: (76, 77), 71: (77, 77)}   # rig_seraphine.FAR_OFF's head rows
BACK_HAIR2 = (66, 57)              # the old back hair kept: from this row, left of (and at) this column


def head2(out):
    rgb = {k: (int(v[1:3], 16), int(v[3:5], 16), int(v[5:7], 16), 255) for k, v in HEAD2_C.items()}
    far = np.zeros(out.shape[:2], bool)
    for y, (c0, c1) in FAR_ARM2.items():
        far[y, c0:c1 + 1] = True
    r0, c1 = BACK_HAIR2
    clear = np.zeros_like(far)
    clear[50:72, 46:82] = True
    clear[r0:72, :c1 + 1] = False
    out[clear & ~far] = 0
    for table in (HEAD2, CURL2):
        for y, segs in table.items():
            for x0, sq in segs:
                for i, ch in enumerate(sq):
                    if not far[y, x0 + i]:
                        out[y, x0 + i] = rgb[ch]
    for (x, y), ch in ORNAMENTS2.items():
        out[y, x] = rgb[ch]
    for y, ch in LOCK2.items():
        if not far[y, 75]:
            out[y, 75] = rgb[ch]
    for y, (x0, sq) in JOIN2.items():
        for i, ch in enumerate(sq):
            if not out[y, x0 + i, 3]:
                out[y, x0 + i] = rgb[ch]
    # the old ear's skin and ornament squares left in the kept back hair: hair
    hair = {tuple(rgb[k][:3]) for k in "0123456"} | {hx(h) for h in ("#d11563", "#d61565", "#fb2f7d", "#fb327e",
                                                                      "#fc3280", "#fc3380", "#fc3480", "#5e0333",
                                                                      "#130327")}
    for y in range(r0, 72):
        for x in range(52, c1 + 1):
            if out[y, x, 3] and tuple(int(v) for v in out[y, x, :3]) not in hair:
                out[y, x] = rgb["5"]
    # the narrower jaw left pockets of ground between it and the hair beside it (they were hair): dark hair
    op = out[..., 3] > 0
    lab, n = strips.label(~op)
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) <= 8 and ys.min() >= 54 and ys.max() <= 72 and xs.min() >= 56 and xs.max() <= 78:
            out[ys, xs] = rgb["5"]
    return out


# step 12 ------------------------------------------------------------------------------------------------------------
NEAR_CUT2 = (63, 64)                # the near side's bare shoulder columns (rows 72-76) the moved sleeve covers
NEAR_PART2 = (72, 85, 58, 62)       # rows, columns of the near sleeve, arm and glove (and their outline) moved in
HAIR_PINKS2 = ("#d31865", "#d61565", "#d11563", "#c81260", "#fc3581", "#fc4187", "#e62574", "#5f0033", "#5e0333",
               "#fb2f7d", "#fb327e", "#fc3280", "#fc3380", "#fc3480")


def body2(out):
    a = out.copy()
    hair = {hx(h) for h in HAIR_PINKS2}
    ink = hx("#0d0222")
    dx = len(NEAR_CUT2)

    def is_hair(y, x):
        return a[y, x, 3] and tuple(int(v) for v in a[y, x, :3]) in hair
    res = a.copy()
    r0, r1, c0, c1 = NEAR_PART2
    for y in range(r0, r1 + 1):
        part = [(x, a[y, x].copy()) for x in range(c0, c1 + 1) if a[y, x, 3] and not is_hair(y, x)]
        if not part:
            continue
        for x, _ in part:                                           # lifted: the hair beside it fills in, else clear
            res[y, x] = 0
        for x, px in part:
            res[y, x + dx] = px
        fill = next((a[y, x] for x in range(c0 - 1, c0 - 6, -1) if is_hair(y, x)), None)
        for x in range(c0, min(x for x, _ in part) + dx):
            if not res[y, x, 3] and fill is not None:
                res[y, x] = fill
    # the near glove's outer column (now at c0 + dx)
    for y in range(82, 86):
        x = c0 + dx
        if res[y, x, 3] and tuple(int(v) for v in res[y, x, :3]) not in hair:
            res[y, x] = next((res[y, xx] for xx in range(x - 1, x - 5, -1)
                              if res[y, xx, 3] and tuple(int(v) for v in res[y, xx, :3]) in hair), (*ink, 255))
    res, _, _ = strips.complete_outline(res, color=ink, feet=SOLE_ROW)
    return res


# step 13 ------------------------------------------------------------------------------------------------------------
# (2026-10-09, 「格温和萨勒芬妮的脸部立绘可以修好看一点」「像莎弥拉脸部修改后就很有个性」; the user picked Codex's
# star-wink picture, assets/source/seraphine/codex_face/seraphine-face-B-initial.png, drawn on this design's own grid:
# read back on its 27.6-px squares it is 46 x 31 like the design): its face square by square - the near eye a lash
# row over a white outer corner, a blue iris with a white glint and cyan under it; the far eye winking (an arch); a
# two-square blush under each eye; the forehead a row taller with the dark lock over the near eye; the picture's open
# mouth without its tongue (3 x 2, the lower row a lighter red: the tongue read as stuck on, 「不要吐舌头了」). The hair,
# the ornaments and the body stay this design's.
FACE3_C = {"0": "#0d0222", "4": "#d31865", "5": "#c81260", "6": "#5f0033", "J": "#fddab8", "C": "#f8a0a8",
           "w": "#ffffff", "B": "#1438a8", "q": "#180f3b", "K": "#10b0f4", "V": "#0e8edc", "r": "#a5193a",
           "R": "#d04058"}
# (first column, squares) per row; '-' keeps the square
FACE3 = {65: [(62, "566JJJJ44J4J")],
         66: [(62, "J000JJJJJJJJ")],
         67: [(62, "0wBwqJJJ00JJ0")],
         68: [(62, "JwKBVJJ0JJ0J0")],
         69: [(62, "JCCJJJJJCCJ0")],
         70: [(62, "0JJJrrrJJJ0")],          # an open mouth, no tongue (「不要吐舌头了」), its lower row lighter
         71: [(61, "0000JRRRJJ0")]}          # (「J 张嘴下排浅」; three over one read as a T)


def face3(out):
    rgb = {k: (int(v[1:3], 16), int(v[3:5], 16), int(v[5:7], 16), 255) for k, v in FACE3_C.items()}
    for y, segs in FACE3.items():
        for x0, sq in segs:
            for i, ch in enumerate(sq):
                if ch != "-":
                    out[y, x0 + i] = rgb[ch]
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

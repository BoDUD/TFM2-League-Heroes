#!/usr/bin/env python3
"""Lillia's game-size design candidates from Codex's step-1 raws (assets/source/lillia/codex_model/lillia-model/raw).

    python tools/art/design_lillia.py --sheet <png>        # every candidate side by side (1x and 8x)
    python tools/art/design_lillia.py --pick NAME          # write assets/source/native/lillia_native.png

Codex drew the raws on its own ~18 px grid (regrid.py reads them back square for square): 05 = version A (the long
bough, 72 rows), 07 = version B (the shorter bough, 65 rows), 06 = another B (59 rows). Its own 42-row designs
(lillia_design_A/B_1x.png) came out speckled, so the candidates here are read back by this script:
  cut   whole rows and columns deleted down to 42 rows (design_akali.dp_keep: never two neighbours, each deleted line
        costing its difference from the nearer neighbour; the face rows and columns kept), then the outline closed;
  vote  each 42-row cell the colour most of its source block shows (ink only over half the block), then the outline
        closed (league_gwen's route).
Step 6 (B46_slim, the design now): step 5 slimmed. Step 5 (B46_fixed): raw 07 cut gently to 46 rows and fixed by hand, square by square (see
FIXES46). Steps 2-4 (B_polish, the user's 「你选一个吧 ... 需要调用工具修复」): crumbs and lone ink cleaned, the face and the bough's
top with the lantern redrawn by tables. Colours: every square to the nearest of Codex's own palette (palette.hex, 32). The figure stands on the 128 canvas with
the hooves on row 99 and their middle on column 64.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips  # noqa: E402
from design_akali import dp_keep  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "lillia", "codex_model", "lillia-model")
OUT = os.path.join(ROOT, "assets", "source", "native", "lillia_native.png")
RAWS = {"05": "05_f0cb716e-a0b8-4e84-82e2-2dc6d4f9d144.png", "06": "06_92f25173-e5ae-49e2-817f-3babdf3e3bca.png",
        "07": "07_721ca5dd-a126-41d3-ae8f-b65711d71af0.png"}
# the face (eyes, nose, mouth, cheeks) in each raw's own squares: rows and columns never deleted
FACE = {"05": (range(22, 30), range(21, 30)), "06": (range(14, 22), range(20, 29)), "07": (range(15, 23), range(21, 30))}
ROWS, SOLE_ROW, MID_COL = 42, 99, 64


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def palette():
    with open(lp(os.path.join(SRC, "palette.hex"))) as f:
        return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in f.read().split()], np.uint8)


PAL = palette()
OUTLINE = tuple(int(v) for v in PAL[0])


def read_back(name):
    """The raw on its own grid, cropped, hard alpha, every square on the nearest palette colour (index; -1 = clear)."""
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, "raw", RAWS[name]))).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    d = ((raw[..., None, :3].astype(int) - PAL[None, None].astype(int)) ** 2).sum(-1)
    idx = d.argmin(-1)
    idx[raw[..., 3] < 128] = -1
    return idx, (int(ys.min()), int(xs.min()))


def weights(idx):
    """Deleting a line through the eyes, the bud, the blossom or the outline costs more."""
    w = np.ones(idx.shape, int)
    for c, k in (("#FFFFFF", 6), ("#8A4AF0", 6), ("#4A1AA0", 6), ("#56C8FE", 4), ("#140808", 2)):
        rgb = np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)])
        j = int(np.argmin(((PAL.astype(int) - rgb) ** 2).sum(1)))
        w[idx == j] = k
    return w


def cut(name, rows=ROWS):
    idx, _ = read_back(name)
    H, W = idx.shape
    face_rows, face_cols = FACE[name]
    w = weights(idx)
    rows_n = rows - 1 if rows == ROWS else rows  # the outline closed over the top adds a row
    tw = round(W * rows_n / H)
    best = None
    for order in ("rc", "cr"):
        if order == "rc":
            r_, lr = dp_keep(list(idx), list(w), rows_n, set(face_rows))
            c_, lc = dp_keep(list(idx[r_].T), list(w[r_].T), tw, set(face_cols))
        else:
            c_, lc = dp_keep(list(idx.T), list(w.T), tw, set(face_cols))
            r_, lr = dp_keep(list(idx[:, c_]), list(w[:, c_]), rows_n, set(face_rows))
        if best is None or lr + lc < best[0]:
            best = (lr + lc, r_, c_)
    _, rows, cols = best
    return idx[np.ix_(rows, cols)]


def vote(name):
    idx, _ = read_back(name)
    H, W = idx.shape
    tw = round(W * ROWS / H)
    ys = np.linspace(0, H, ROWS + 1)
    xs = np.linspace(0, W, tw + 1)
    out = np.full((ROWS, tw), -1, int)
    for r in range(ROWS):
        for c in range(tw):
            blk = idx[int(ys[r]):max(int(ys[r]) + 1, int(round(ys[r + 1]))), int(xs[c]):max(int(xs[c]) + 1, int(round(xs[c + 1])))]
            v = blk[blk >= 0]
            if v.size * 2 <= blk.size:
                continue
            vals, cnt = np.unique(v, return_counts=True)
            out[r, c] = vals[np.argmax(cnt)]
    return out


def to_canvas(small):
    """Palette indices -> RGBA on the 128 canvas, the outline closed, hooves on row 99 centred on column 64."""
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = PAL[small[m]]
    fig[m, 3] = 255
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, _, _ = strips.complete_outline(can, color=OUTLINE, feet=fig.shape[0])
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero(fig[-2:, :, 3].max(0) > 0)[0]
    mid_x = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


# step 2 (the user: 「的确不满意 需要调用工具修复 参考之前那几个模糊不清的英雄怎么修复的」): B_cut cleaned like league_gwen /
# league_seraphine - colour families; a crumb (a 4-connected piece of 1-2 squares of one family) inside another family
# takes the commonest colour round it; lone near-black squares joining no line likewise
FAMILIES = {
    "ink": ["#140808"], "hair": ["#6E0A40", "#B8075E", "#F00480", "#FF6EB8"],
    "leaf": ["#036A2E", "#3E8A2A", "#B1DC43", "#2E4A10"], "fawn": ["#9A2A08", "#D84A0A", "#FF7F00", "#FFA840"],
    "cream": ["#E8C890", "#FFF0C8"], "skin": ["#D88C68", "#F8C8A0", "#FFE4CC"],
    "bough": ["#2A0838", "#5A1078", "#9A3AD8", "#7A3CC8"], "violet": ["#3A2C9A", "#5A5AE0", "#9499FC", "#4A1AA0", "#8A4AF0"],
    "gold": ["#8A5A10", "#E8A010", "#FBD70B"], "cyan": ["#56C8FE"], "white": ["#FFFFFF"],
}
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


FAMILY_OF = {hx(c): k for k, cs in FAMILIES.items() for c in cs}


def fam(a, y, x):
    return FAMILY_OF.get(tuple(int(v) for v in a[y, x, :3]), "?") if a[y, x, 3] else None


def crumbs(a, keep, size=2):
    """1-2-square pieces of one family whose every outside 4-neighbour is one other (not ink) family take that family's
    commonest neighbouring colour. Returns (picture, squares changed)."""
    out = a.copy()
    seen = np.zeros(a.shape[:2], bool)
    n = 0
    for y0, x0 in zip(*np.nonzero(a[..., 3] > 0)):
        if seen[y0, x0]:
            continue
        f0 = fam(a, y0, x0)
        comp, stack = [], [(y0, x0)]
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < 128 and 0 <= xx < 128 and not seen[yy, xx] and fam(a, yy, xx) == f0:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if f0 == "ink" or len(comp) > size or any(keep[y, x] for y, x in comp):
            continue
        around = [(y + dy, x + dx) for y, x in comp for dy, dx in N4 if (y + dy, x + dx) not in comp]
        fams = {fam(a, yy, xx) for yy, xx in around}
        if len(fams) != 1 or None in fams or "ink" in fams:
            continue
        cols = [tuple(int(v) for v in a[yy, xx, :3]) for yy, xx in around]
        best = max(set(cols), key=cols.count)
        for y, x in comp:
            out[y, x, :3] = best
            n += 1
    return out, n


def lone_ink(a, keep):
    """Near-black squares inside the figure joining no line take their neighbours' commonest colour."""
    ink = np.array(hx("#140808"), np.uint8)
    op = a[..., 3] > 0
    isk = op & (a[..., :3] == ink).all(-1)
    out = a.copy()
    n = 0
    for y, x in zip(*np.nonzero(isk & ~keep)):
        nb = [(y + dy, x + dx) for dy, dx in N4]
        if not all(op[yy, xx] for yy, xx in nb) or sum(isk[yy, xx] for yy, xx in nb) > 1:
            continue
        cols = [tuple(int(v) for v in a[yy, xx, :3]) for yy, xx in nb if not isk[yy, xx]]
        out[y, x, :3] = max(set(cols), key=cols.count)
        n += 1
    return out, n


def cleaned(can, keep):
    total = []
    for _ in range(3):
        can, a = crumbs(can, keep)
        can, b = lone_ink(can, keep)
        total.append(a + b)
        if a + b == 0:
            break
    return can, total


def codex(version):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"lillia_design_{version}_1x.png"))).convert("RGBA")).copy()
    return a


# step 3: the face (canvas rows 69-75, columns 64-70) drawn by hand in league_gwen's / league_seraphine's way - 2x2
# purple eyes (dark lash row over an iris with a white highlight), blush on both cheeks, a one-square mouth
C = {"K": "#140808", "s": "#F8C8A0", "d": "#D88C68", "l": "#FFE4CC", "H": "#F00480", "h": "#B8075E", "E": "#4A1AA0",
     "e": "#8A4AF0", "W": "#FFFFFF", "p": "#FF6EB8", "Q": "#5A1078", "R": "#9A3AD8", "Y": "#FBD70B", "G": "#E8A010",
     "g": "#8A5A10", "c": "#56C8FE", "O": "#FF7F00", "o": "#D84A0A", "F": "#036A2E", "f": "#3E8A2A"}
FACE_TABLE = {
    69: (64, "HHsHHHh"),
    70: (64, "Hssssss"),
    71: (64, "hEEsEEs"),
    72: (64, "sWesWes"),
    73: (64, "pssssps"),
    74: (64, "ssssmsd"),
    75: (65, "s"),
}
C["m"] = "#B8075E"


def paint(can, table):
    out = can.copy()
    for y, (x0, row) in table.items():
        for i, ch in enumerate(row):
            if ch == "-":
                continue
            if ch == ".":
                out[y, x0 + i] = 0
                continue
            out[y, x0 + i, :3] = hx(C[ch])
            out[y, x0 + i, 3] = 255
    return out


# step 4: the bough's top and the lantern redrawn (the read-back left crumbs): everything right of the hair from row
# BOUGH_ROWS up cleared, then a one-square purple shaft from her hands (SHAFT) up to the gold hook, a cyan blossom on
# its tip (42 rows: the blossom's outline on the bud-to-hooves design's top row 58), the lantern (gold caps, orange body with two darker staves and a highlight) hanging from the hook's end, a
# gold tassel under it, two leaves on the shaft; the outline closed round it afterwards
BOUGH_ROWS = (56, 80)
BOUGH_X = 74                # clear from this column (row < 71: from column 73)
SHAFT = ((74, 80), (75, 64))
BOUGH = {
    59: (74, "-c-"),
    60: (74, "cWc"),
    61: (74, "-c-"),
    62: (75, "YYY"),
    63: (75, "G--Y"),
    64: (78, "GY"),
    65: (79, "G"),
    66: (78, "gGg"),
    67: (77, "oOOOo"),
    68: (77, "OYOoO"),
    69: (77, "OYOoO"),
    70: (77, "oOOOo"),
    71: (77, "oOoOo"),
    72: (78, "gGg"),
    73: (79, "G"),
    74: (79, "Y"),
    75: (79, "Y"),
    76: (79, "G"),
}
LEAVES = {68: (73, "f"), 69: (73, "F")}


def bough(can):
    out = can.copy()
    y0, y1 = BOUGH_ROWS
    out[y0:y1, BOUGH_X:] = 0
    out[y0:71, BOUGH_X - 1:] = 0
    out[y1:y1 + 3, BOUGH_X + 3:] = 0          # the old tassel's end
    (xa, ya), (xb, yb) = SHAFT
    for y in range(yb, ya + 1):
        x = round(xa + (xb - xa) * (ya - y) / (ya - yb))
        out[y, x, :3] = hx(C["Q"])
        out[y, x, 3] = 255
    rows = {}
    for y, spec in BOUGH.items():
        rows.setdefault(y, []).append(spec)
    for y, specs in rows.items():
        for spec in specs:
            out = paint(out, {y: spec})
    return paint(out, LEAVES)


def polished():
    can = to_canvas(cut("07"))
    face = np.zeros((128, 128), bool)
    face[68:78, 61:73] = True
    can, _ = cleaned(can, face)
    can = paint(can, FACE_TABLE)
    can = bough(can)
    can, _, _ = strips.complete_outline(can, color=OUTLINE, feet=SOLE_ROW + 1)
    return can


# step 5 (the user: 「继续改 太多地方不对了」, then at raw 07 「用这个慢慢调不就行了吗」): raw 07 cut gently to 46 rows
# (cut46: dp_keep to 45 + the closed outline; at 42 rows the cut shreds the legs, the body and the lantern) and fixed by
# hand, square by square from its char map (charmap letters, LETTERS) - the face (2x2 purple eyes, blush, a soft mouth),
# one purple bough line, the gold hook, a round lantern with gold bands and two ribs, a clean leaf curl, the torso (the
# far hand high on the bough, the near arm across to the low grip, leaf top, bare waist, leaf skirt), the lower bough
# ending at the deer's chest, four 2-square legs with hocks on the hind ones and 3-square hooves; outline closed, the
# hooves' middle back on column 64. Body (bud to hooves) 40 rows, 46 with the bough's blossom.
LETTERS = {"K": "#140808", "a": "#9A2A08", "b": "#D84A0A", "O": "#FF7F00", "o": "#FFA840", "c": "#E8C890",
           "C": "#FFF0C8", "v": "#7A3CC8", "x": "#6E0A40", "h": "#B8075E", "H": "#F00480", "P": "#FF6EB8",
           "d": "#D88C68", "s": "#F8C8A0", "l": "#FFE4CC", "F": "#036A2E", "f": "#3E8A2A", "L": "#B1DC43",
           "z": "#2E4A10", "u": "#3A2C9A", "U": "#5A5AE0", "V": "#9499FC", "E": "#4A1AA0", "e": "#8A4AF0",
           "q": "#2A0838", "Q": "#5A1078", "R": "#9A3AD8", "g": "#8A5A10", "G": "#E8A010", "Y": "#FBD70B",
           "j": "#56C8FE", "W": "#FFFFFF"}
FACE46 = {
    67: [(66, "KsssK")],
    68: [(65, "hsssssh")],
    69: [(64, "hKKssKKh")],
    70: [(64, "hWEssWEK")],
    71: [(64, "heessees")],
    72: [(64, "KPssssPs")],
    73: [(63, "KdsssdssdK")],
    74: [(64, "KdssssdK")],
    75: [(66, "KddK")],
}
# the bough: one purple line (col 76 rows 58-67, col 75 rows 68-77), its outline on both sides
SHAFT46 = {58: [(75, "KQK")], 59: [(75, "KQ")], 60: [(75, "fQK")], 61: [(75, "FQK")], 62: [(75, "KQK")],
         63: [(75, "KQK")], 64: [(75, "KQK")], 65: [(75, "KQK")], 66: [(75, "KQK")], 67: [(75, "KQK")],
         68: [(74, "KQK")], 69: [(74, "KQK")], 70: [(74, "KQK")], 71: [(74, "KQK")], 72: [(74, "KQK")],
         73: [(74, "KQK")], 74: [(74, "KQK")], 75: [(74, "KQK")], 76: [(74, "KQK")]}
# the gold hook from the blossom over to the right and back down to the lantern's link
HOOK46 = {57: [(79, "GY")], 58: [(80, "Y")], 59: [(77, "GKKG")], 60: [(78, "gG")], 61: [(78, "G")], 62: [(77, "KgK")]}
CURL46 = {
    65: [(56, "KLffK")],
    66: [(56, "KfzfK")],
    67: [(56, "KffFK")],
    68: [(56, "KKFFK")],
    69: [(57, "KhfKh")],
    70: [(57, "KhFhh")],
    71: [(56, "KHhfK")],
    72: [(56, "KHhfK")],
    73: [(56, "KHhGK")],
    74: [(55, "KHHhYK")],
}

TORSO46 = {
    76: [(61, "KFFfKKssKKfFKKQK.")],
    77: [(61, "KsFfFdssdfFfKKQK.")],
    78: [(61, "KssfFfPfFfsffssK.")],
    79: [(61, "KsdFfHHfFfsFfdsK.")],
    80: [(61, "KsdfFfhFfssdKQK..")],
    81: [(61, "KdssssssdKKsssK..")],
    82: [(61, "KssFfFfssssdsK...")],
    83: [(61, "KKdsssdKKKQK.....")],
    84: [(61, "FfFfFfFfFKQK")],
    85: [(60, "KfFfFfFfFfKQKKKK")],
    86: [(60, "FfFfOOFfFFKQKKffK")],
    87: [(69, "KKQKCCF")],
    88: [(68, "KKQK")],
}
LEGS46 = {
    90: [(51, "KbaObOOObCCCCbOOObbCbbaK")],
    91: [(50, ".KbaKKOObK....KOObK.KbbaK...")],
    92: [(50, ".KbaK.KObK.....KObK..KbaK...")],
    93: [(50, ".KbaK.KObK.....KObK..KbaK...")],
    94: [(50, ".KbaK..KObK....KObK..KbaK...")],
    95: [(50, ".KbaK..KObK....KObK..KbaK...")],
    96: [(50, ".KbaK..KObK....KObK..KbaK...")],
    97: [(50, ".KeeVK.KeeVK...KeeVK.KeeVK..")],
    98: [(50, ".KueeK.KueeK...KueeK.KueeK..")],
    99: [(50, "..KKK...KKK.....KKK...KKK...")],
}
LANTERN46 = {
    62: [(77, "KgK...")],
    63: [(77, "KKHK..")],
    64: [(77, "KFHPK.")],
    65: [(77, "KGGGK.")],
    66: [(77, "KYYObK")],
    67: [(76, "KYYgOObK")],
    68: [(76, "KYOgOgbK")],
    69: [(76, "KOOgOgbK")],
    70: [(76, "KbOgObaK")],
    71: [(76, "KKbGGbKK")],
    72: [(77, "KKGgKK")],
    73: [(77, ".KYK..")],
    74: [(77, ".KYK..")],
    75: [(77, ".KGK..")],
    76: [(77, ".KGK..")],
    77: [(77, "..K...")],
    78: [(78, ".....")],     # the read-back's own tassel below
    79: [(78, ".....")],
    80: [(78, ".....")],
}
HOCKS46 = {
    93: [(50, "KbbaK"), (56, "KOObK")],
    94: [(50, "KbbaK"), (56, "KOObK")],
    95: [(50, ".KbaK"), (56, ".KObK")],
}
FIXES46 = [FACE46, SHAFT46, HOOK46, CURL46, TORSO46, LEGS46, LANTERN46, HOCKS46]


def apply_letters(can, edits):
    """edits {row: [(col, "letters")]} on the canvas: '-' leaves a square, '.' clears it."""
    out = can.copy()
    for y, frags in edits.items():
        for x0, s in frags:
            for i, ch in enumerate(s):
                if ch == "-":
                    continue
                if ch == ".":
                    out[y, x0 + i] = 0
                    continue
                out[y, x0 + i, :3] = hx(LETTERS[ch])
                out[y, x0 + i, 3] = 255
    return out


def recentre(can):
    """The hooves' middle (bottom two rows) back on MID_COL."""
    feet = np.nonzero(can[SOLE_ROW - 2:SOLE_ROW, :, 3].max(0) > 0)[0]
    dx = int(round(MID_COL - (feet.min() + feet.max()) / 2))
    return np.roll(can, dx, axis=1) if dx else can


def design46():
    can = to_canvas(cut("07", 45))
    for t in FIXES46:
        can = apply_letters(can, t)
    can, _, _ = strips.complete_outline(can, color=OUTLINE, feet=SOLE_ROW + 1)
    return recentre(can)


# step 6 (the user: 「改的挺好的 就是有点胖」 and 「还有身体和小鹿的腿连接的那里有点歪」 - the near hind leg drifted right
# down its length, the hips stepped): option V2 picked - two rows of the deer's barrel out (SLIM_DROP_ROWS: the skirt's
# middle and the lower body), the four legs redrawn two rows longer and straight under the body (SLIM_LEGS: A 53-54,
# B 58-59, C 67-68, D 73-74, hocks on the hind legs, 3-square hooves), the bough's lower end a dark tip, then two columns
# out (SLIM_DROP_COLS: picked where nothing but hair, arm and barrel is - never the face, the lantern or a leg) -> 32x46.
SLIM_DROP_ROWS = (85, 88)
SLIM_LEGS = {
    89: [(51, ".KbaK.KObK.....KObK..KbaK.....")],
    90: [(51, ".KbaK.KObK.....KObK..KbaK.....")],
    91: [(51, ".KbaK.KObK.....KObK..KbaK.....")],
    92: [(51, ".KbaK.KObK.....KObK..KbaK.....")],
    93: [(51, "KbbaKKOObK.....KObK..KbaK.....")],
    94: [(51, "KbbaKKOObK.....KObK..KbaK.....")],
    95: [(51, ".KbaK.KObK.....KObK..KbaK.....")],
    96: [(51, ".KbaK.KObK.....KObK..KbaK.....")],
    97: [(51, ".KeeVKKeeVK....KeeVK.KeeVK....")],
    98: [(51, ".KueeKKueeK....KueeK.KueeK....")],
    99: [(51, "..KKK..KKK......KKK...KKK.....")],
    87: [(72, "q")],
}
SLIM_DROP_COLS = (56, 62)


def slim(can):
    rows = [r for r in range(54, 91) if r not in SLIM_DROP_ROWS]
    out = np.zeros_like(can)
    out[SOLE_ROW - 10 - len(rows):SOLE_ROW - 10] = can[rows]
    out = apply_letters(out, SLIM_LEGS)
    out, _, _ = strips.complete_outline(out, color=OUTLINE, feet=SOLE_ROW + 1)
    keep = [c for c in range(128) if c not in SLIM_DROP_COLS]
    narrow = np.zeros_like(out)
    narrow[:, :len(keep)] = out[:, keep]
    return recentre(narrow)


CANDIDATES = {
    "codex_A": lambda: codex("A"), "codex_B": lambda: codex("B"),
    "A_cut": lambda: to_canvas(cut("05")), "A_vote": lambda: to_canvas(vote("05")),
    "B_cut": lambda: to_canvas(cut("07")), "B_vote": lambda: to_canvas(vote("07")),
    "B2_cut": lambda: to_canvas(cut("06")), "B2_vote": lambda: to_canvas(vote("06")),
    "B_clean": lambda: cleaned(to_canvas(cut("07")), np.zeros((128, 128), bool))[0],
    "B_polish": polished,
    "B46_fixed": design46, "B46_cut": lambda: to_canvas(cut("07", 45)), "B46_slim": lambda: slim(design46()),
}


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def sheet(path, names, z=8):
    figs = [(n, crop(CANDIDATES[n]())) for n in names]
    pad, label = 24, 20
    tall = max(f.shape[0] for _, f in figs)
    w = sum(f.shape[1] * z + pad for _, f in figs) + pad
    img = Image.new("RGBA", (w, tall * z + tall + 3 * pad + label), (225, 225, 225, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for n, f in figs:
        im = Image.fromarray(f)
        big = im.resize((im.width * z, im.height * z), Image.NEAREST)
        img.alpha_composite(big, (x, pad + (tall - f.shape[0]) * z))
        img.alpha_composite(im, (x, 2 * pad + tall * z + (tall - f.shape[0])))
        d.text((x, img.height - label), f"{n} {f.shape[1]}x{f.shape[0]}", fill=(0, 0, 0, 255))
        x += big.width + pad
    img.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet")
    ap.add_argument("--pick", choices=sorted(CANDIDATES))
    a = ap.parse_args()
    if a.sheet:
        sheet(a.sheet, list(CANDIDATES))
        print("wrote", a.sheet)
    if a.pick:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        Image.fromarray(CANDIDATES[a.pick]()).save(lp(OUT))
        print("wrote", OUT)


if __name__ == "__main__":
    main()

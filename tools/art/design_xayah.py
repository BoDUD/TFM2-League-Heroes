#!/usr/bin/env python3
"""Xayah's game-size design candidates from Codex's step-1 raw (assets/source/xayah/codex_model/raw).

    python tools/art/design_xayah.py --sheet <png> [--zoom 8]   # every candidate side by side
    python tools/art/design_xayah.py --pick NAME                # write assets/source/native/xayah_native.png

Codex drew the raw on its own ~9 px grid (regrid.py reads it back square for square: 70 x 51). Its own 40-row designs
(xayah_design_1/2_sprite.png) came out speckled, and my whole-line cuts to 40/44/48 straight from the read-back were
「都太模糊了 你利用工具好好修复吧」 - the user pointed at league_gwen / league_tryndamere / league_lillia, which were
cleaned step by step. So, league_lillia's route:
  1. the raw read back on its own grid (alpha >= 128), every square the nearest of Codex's palette (palette.json, 24) in
     CIELAB;
  2. to ROWS rows - cut: whole rows and columns (design_akali.dp_keep: never two neighbours, each deleted line costing
     its weighted difference from the nearer neighbour; the face's rows and columns and the ear's tip kept); vote: each
     cell the colour most of its source block shows (see-through when less than half is opaque);
  3. cleaned (design_lillia's crumbs / lone ink with Xayah's colour families), the outline closed
     (strips.complete_outline);
  4. on the 128 canvas: the soles on row 99, the middle of the feet on column 64.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import design_riven as R  # noqa: E402
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
from design_akali import dp_keep  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "xayah", "codex_model")
OUT = os.path.join(ROOT, "assets", "source", "native", "xayah_native.png")
RAW = os.path.join(SRC, "raw", "xayah_generated_source.png")
SOLE_ROW, MID_COL = 99, 64
# the raw's own squares (70 x 51): the ear's tip row 0, the brows 17, the eyes 18-19 (gold at columns 31 and 34), the
# mouth 20, the chin 21; the face's columns 29-36
FACE_ROWS = range(15, 22)
FACE_COLS = range(29, 37)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


PAL_HEX = json.load(open(lp(os.path.join(SRC, "palette.json"))))["colors"]
PAL = np.array([hx(h) for h in PAL_HEX], np.uint8)
OUTLINE = hx("#0C0204")
EYE = "#FFC93A"


def srgb2lab(c):
    c = np.asarray(c, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def read_back():
    """The raw on its own grid, cropped, every square a palette index (-1 = see-through)."""
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    d = ((srgb2lab(raw[..., :3])[:, :, None, :] - srgb2lab(PAL)[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    idx[raw[..., 3] < 128] = -1
    eye = PAL_HEX.index(EYE)
    face = np.zeros(idx.shape, bool)
    face[FACE_ROWS.start:FACE_ROWS.stop, FACE_COLS.start:FACE_COLS.stop] = True
    idx[(idx == eye) & ~face] = PAL_HEX.index("#FCC24F")     # the eye colour only in the eyes
    return idx


def weights(idx):
    """Deleting a line through the eyes, the skull, the blades or the outline costs more."""
    w = np.ones(idx.shape, int)
    for c, k in ((EYE, 8), ("#F2E6D0", 4), ("#FF5AC8", 4), ("#C02AB0", 4), ("#F8D2BC", 3), ("#0C0204", 2)):
        w[idx == PAL_HEX.index(c)] = k
    return w


def cut(idx, rows):
    H, W = idx.shape
    w = weights(idx)
    tw = round(W * rows / H)
    best = None
    for order in ("rc", "cr"):
        if order == "rc":
            r_, lr = dp_keep(list(idx), list(w), rows, set(FACE_ROWS) | {0})
            c_, lc = dp_keep(list(idx[r_].T), list(w[r_].T), tw, set(FACE_COLS))
        else:
            c_, lc = dp_keep(list(idx.T), list(w.T), tw, set(FACE_COLS))
            r_, lr = dp_keep(list(idx[:, c_]), list(w[:, c_]), rows, set(FACE_ROWS) | {0})
        if best is None or lr + lc < best[0]:
            best = (lr + lc, r_, c_)
    _, r_, c_ = best
    return idx[np.ix_(r_, c_)]


def vote(idx, rows):
    H, W = idx.shape
    tw = round(W * rows / H)
    ys = np.linspace(0, H, rows + 1)
    xs = np.linspace(0, W, tw + 1)
    out = np.full((rows, tw), -1, int)
    for r in range(rows):
        for c in range(tw):
            blk = idx[int(ys[r]):max(int(ys[r]) + 1, int(round(ys[r + 1]))),
                      int(xs[c]):max(int(xs[c]) + 1, int(round(xs[c + 1])))]
            v = blk[blk >= 0]
            if v.size * 2 <= blk.size:
                continue
            vals, cnt = np.unique(v, return_counts=True)
            out[r, c] = vals[np.argmax(cnt)]
    return out


def to_canvas(small):
    """Palette indices -> RGBA on the 128 canvas, the outline closed, the soles on row 99 centred on column 64."""
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


# colour families for the clean-up: a crumb of one family inside another takes the commonest colour round it
FAMILIES = {
    "ink": ["#0C0204"], "violet": ["#1C1945", "#3C2F8E", "#5A4CC0", "#8FA3D8"],
    "hair": ["#7B0624", "#BD0A44", "#FB1C5B", "#FF7FA0"], "cloth": ["#5E0529", "#9D1439", "#D41644"],
    "warm": ["#F08122", "#FCC24F"], "eye": [EYE], "mauve": ["#794552", "#B08A9A"],
    "skin": ["#B0705A", "#E8A88C", "#F8D2BC"], "bone": ["#F2E6D0"], "rope": ["#A0602E"],
    "blade": ["#C02AB0", "#FF5AC8"],
}
FAMILY_OF = {hx(c): k for k, cs in FAMILIES.items() for c in cs}
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def fam(a, y, x):
    return FAMILY_OF.get(tuple(int(v) for v in a[y, x, :3]), "?") if a[y, x, 3] else None


def crumbs(a, keep, size=2):
    """1-2-square pieces of one family whose every outside 4-neighbour is one other (not ink) family take that family's
    commonest neighbouring colour (design_lillia.crumbs)."""
    out = a.copy()
    seen = np.zeros(a.shape[:2], bool)
    n = 0
    H, W = a.shape[:2]
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
                if 0 <= yy < H and 0 <= xx < W and not seen[yy, xx] and fam(a, yy, xx) == f0:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if f0 in ("ink", "eye") or len(comp) > size or any(keep[y, x] for y, x in comp):
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
    ink = np.array(OUTLINE, np.uint8)
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


def face_keep(can):
    """The face box (skin and eyes and the ink between them) kept from the clean-up."""
    keep = np.zeros(can.shape[:2], bool)
    eye = np.array(hx(EYE))
    ys, xs = np.nonzero((can[..., :3] == eye).all(-1) & (can[..., 3] > 0))
    if len(ys):
        keep[ys.min() - 2:ys.max() + 4, xs.min() - 2:xs.max() + 3] = True
    return keep


def cleaned(can):
    keep = face_keep(can)
    for _ in range(3):
        can, a = crumbs(can, keep)
        can, b = lone_ink(can, keep)
        if a + b == 0:
            break
    return can


EYE_ROWS = range(17, 21)            # the brows, the eyes, the mouth (the read-back's own rows)
EYE_COLS = range(30, 37)
K = 28


def read_rgba():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def even(height):
    """league_samira's route: K colours of the read-back's own (design_varus.kmeans), the rows and columns kept by
    design_riven.keep_axis - head and body lose lines in proportion, only the eyes' rows and columns stay whole - the
    outline closed, on the canvas."""
    raw = read_rgba()
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    width = round(W * height / H)
    mid = R.keep_axis([idx[y] for y in range(1, H - 1)], height - 2, range(EYE_ROWS.start - 1, EYE_ROWS.stop - 1))
    rows = [0] + [r + 1 for r in mid] + [H - 1]
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], width, EYE_COLS)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in EYE_ROWS]
    fc = [cols.index(c) for c in EYE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, _, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((fig[-3:, :, 3] > 0).any(0))[0]
    mid_x = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


REGIONS = ((0, 8), (8, 22), (22, 70))   # the ears above the hood, the hood's top to the chin, the body (read-back rows)


def regional(ears, head, body, width=None):
    """The read-back's regions each kept in its own proportion (design_riven.keep_axis per region: the ears to `ears`,
    the head to `head` with the eyes' rows whole, the body to `body`), the columns in proportion with the face's whole,
    the outline closed, on the canvas."""
    raw = read_rgba()
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    rows = []
    for (lo, hi), n in zip(REGIONS, (ears, head, body)):
        lines = [idx[y] for y in range(lo, hi)]
        if lo <= EYE_ROWS.start < hi:
            kept = R.keep_axis(lines, n, range(EYE_ROWS.start - lo, EYE_ROWS.stop - lo))
        else:
            kept = min((R.pick(lines, n, off) for off in range(3)), key=lambda t: t[1])[0]
        rows += [lo + r for r in kept]
    width = width or round(W * (ears + head + body) / H * 1.05)
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], width, EYE_COLS)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in EYE_ROWS]
    fc = [cols.index(c) for c in EYE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, _, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((fig[-3:, :, 3] > 0).any(0))[0]
    mid_x = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


# ----------------------------------------------------------------------------- step 5: polished by hand (reg44b)
# the colours of regional(6, 13, 25) by letter (design_lillia's LETTERS way), plus three new ones: y (the cloak's and the
# tuft's yellow - the eyes' bright gold l is now the eyes' alone), z (the blades' bright magenta)
LETTERS = {
    "0": "#0B040E", "1": "#1A1236", "2": "#44041C", "3": "#5F0A3D", "4": "#74082F", "5": "#28255F", "6": "#753D27",
    "7": "#3B2782", "8": "#A71238", "9": "#761481", "a": "#B84313", "b": "#714759", "c": "#4E2EAA", "d": "#B21590",
    "e": "#E06E0B", "f": "#E91F52", "g": "#CF880B", "h": "#986471", "i": "#D7416A", "j": "#F02D71", "k": "#6E71C0",
    "l": "#F7A313", "m": "#E89C86", "n": "#C5AB9E", "o": "#969FDD", "p": "#FAC6AF", "q": "#FBC9D6", "r": "#F6E7E8",
    "y": "#F6C443", "z": "#FF5AC8",
}
# row: (first column, letters); "." clears a square, " " leaves it
EDITS = {
    # the ears: specks out (q, i, n inside the white tips and the pink)
    57: (61, "0rr00"), 58: (61, "0rrff00"), 63: (56, "0rfffff0"), 64: (57, "0r84fff"), 65: (57, "0rf44ff0"),
    # the face: fringe, lash row, 2x2 eyes (light + dark gold over two bright gold), a skin square between, the cheek
    # stripe under the near eye, a mouth square, the chin
    68: (66, "ffffjff4"),
    69: (66, "f4pppfff"),
    70: (66, "8pp4pp4f"),
    71: (66, "8prgprgm"),
    72: (66, "2mllpllm"),
    73: (66, "8mpppim "),
    74: (67, "4mp3pm2"),
    # the skull on the near shoulder: a tuft of orange-yellow feathers, the bone with a dark socket, the beak down-right
    73.5: (0, ""),
    # the hand's blades: two magenta blades fanning down from the hand
}
SKULL = {74: (75, ".0y0."), 75: (75, "0eye0"), 76: (75, "rrrn0"), 77: (75, "r0rrn0"), 78: (75, "nrrnn0"),
         79: (75, "0nn0n0"), 80: (76, "0..0")}
TUFT = {73: (76, ".0.")}
BLADES = {89: (77, "00zd0..."), 90: (77, ".0z0d0.."), 91: (77, ".0d0z0.."), 92: (77, ".0d0zd0."), 93: (77, ".09.0d0."),
          94: (77, "..0..0.."), 95: (77, "........")}
WARM_TO_Y = "l"                     # outside the eyes the bright gold becomes y
FAMILY_L = {"0": "ink", "1": "violet", "5": "violet", "7": "violet", "c": "violet", "k": "violet", "o": "violet",
            "4": "hair", "8": "hair", "f": "hair", "j": "hair", "i": "hair", "q": "hair", "2": "cloth", "3": "cloth",
            "a": "warm", "e": "warm", "y": "warm", "g": "eye", "l": "eye", "b": "mauve", "h": "mauve", "m": "skin",
            "p": "skin", "r": "bone", "n": "bone", "6": "rope", "9": "blade", "d": "blade", "z": "blade"}


def paint(can, table):
    for y, (x0, text) in table.items():
        if not text:
            continue
        for i, ch in enumerate(text):
            if ch == " ":
                continue
            if ch == ".":
                can[int(y), x0 + i] = 0
            else:
                can[int(y), x0 + i, :3], can[int(y), x0 + i, 3] = hx(LETTERS[ch]), 255


def polished():
    can = regional(6, 13, 25).copy()
    rgb2l = {hx(v): k for k, v in LETTERS.items()}
    # the bright gold outside the face box -> y
    for y, x in zip(*np.nonzero(can[..., 3] > 0)):
        k = rgb2l.get(tuple(int(v) for v in can[y, x, :3]))
        if k == WARM_TO_Y and not (68 <= y <= 74 and 66 <= x <= 74):
            can[y, x, :3] = hx(LETTERS["y"])
    paint(can, EDITS)
    paint(can, BLADES)
    paint(can, SKULL)
    paint(can, TUFT)
    keep = np.zeros(can.shape[:2], bool)
    keep[68:76, 65:76] = True
    keep[71:81, 74:82] = True
    keep[88:96, 76:85] = True
    fam_of = {hx(v): FAMILY_L[k] for k, v in LETTERS.items() if k in FAMILY_L}
    for _ in range(3):
        can, a = crumbs_l(can, keep, fam_of)
        can, b = lone_ink(can, keep)
        if a + b == 0:
            break
    can, _, _ = strips.complete_outline(can, color=OUTLINE_L, feet=SOLE_ROW + 1, keep=keep)
    can[SOLE_ROW + 1:] = 0
    return can


OUTLINE_L = hx("#0B040E")


def crumbs_l(a, keep, fam_of, size=2):
    """design_lillia.crumbs with this design's own families."""
    out = a.copy()
    seen = np.zeros(a.shape[:2], bool)
    n = 0
    H, W = a.shape[:2]

    def f(y, x):
        return fam_of.get(tuple(int(v) for v in a[y, x, :3]), "?") if a[y, x, 3] else None

    for y0, x0 in zip(*np.nonzero(a[..., 3] > 0)):
        if seen[y0, x0]:
            continue
        f0 = f(y0, x0)
        comp, stack = [], [(y0, x0)]
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and not seen[yy, xx] and f(yy, xx) == f0:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if f0 in ("ink", "eye") or len(comp) > size or any(keep[y, x] for y, x in comp):
            continue
        around = [(y + dy, x + dx) for y, x in comp for dy, dx in N4 if (y + dy, x + dx) not in comp]
        fams = {f(yy, xx) for yy, xx in around}
        if len(fams) != 1 or None in fams or "ink" in fams:
            continue
        cols = [tuple(int(v) for v in a[yy, xx, :3]) for yy, xx in around]
        best = max(set(cols), key=cols.count)
        for y, x in comp:
            out[y, x, :3] = best
            n += 1
    return out, n


# step 6 (the user picked regional(6, 13, 25) as it is - 「用这个就行 头顶一大块黑线帮我处理了」): only the black band on
# the head's top changes - row 62 under the upper ear and the dark lump at the hood's top right become the hood's violet
# (the ear now grows out of the hood), a hair-dark square where the hood meets the hair; every other square as cut
HEAD_TOP = {62: (65, "77o77"), 63: (71, "7"), 64: (70, "k75"), 65: (69, "74"), 66: (67, "5")}


# step 7 (the user, reviewing the strips: 「仔细排查问题」「不要有任何模型变形的问题」「像素缺失也是」): the design's own two
# defects - a see-through square shut in by outline between the near shoulder and the skull (80, 77: a hole showing the
# ground) gets the outline colour, and a lone outline square floating right of the blades' tips (93, 83) goes
HOLES = {80: (77, "0"), 93: (83, ".")}


def picked():
    can = regional(6, 13, 25).copy()
    paint(can, HEAD_TOP)
    paint(can, HOLES)
    return can


def candidates():
    raw = read_rgba()
    out = {"raw": raw, "reg44b": regional(6, 13, 25), "picked": picked()}
    return out


def candidates_old():
    raw = read_rgba()
    out = {"raw": raw, "even44": even(44)}
    out["reg40"] = regional(5, 11, 24)
    out["reg44"] = regional(5, 12, 27)
    out["reg44b"] = regional(6, 13, 25)
    return out


def to_canvas_any(idx):
    fig = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    fig[m, :3] = PAL[idx[m]]
    fig[m, 3] = 255
    return fig


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def idle0(hero):
    base = os.path.join(ROOT, "league", "champions", f"league_{hero}")
    anim = json.load(open(lp(base + "#anim.fanim"), encoding="utf-8"))
    fr = anim["anims"]["idle"]["frames"][0]["data"]
    im = Image.open(lp(base + "#sheet.png")).convert("RGBA")
    return crop(np.asarray(im.crop((int(fr["x"]), int(fr["y"]), int(fr["x"] + fr["w"]), int(fr["y"] + fr["h"])))))


def sheet(path, cands, z=8, refs=("rakan", "samira", "seraphine", "evelynn")):
    figs = [(k, crop(v)) for k, v in cands.items()]
    H1 = max(f.shape[0] for _, f in figs) * z + 30
    W1 = sum(f.shape[1] * z + 24 for _, f in figs) + 24
    game = figs + [(r, idle0(r)) for r in refs]
    H3 = max(f.shape[0] for _, f in game) * 2 + 20
    W3 = sum(f.shape[1] * 2 + 20 for _, f in game) + 20
    out = Image.new("RGB", (max(W1, W3), H1 + 2 * (H3 + 8)), (92, 98, 86))
    d = ImageDraw.Draw(out)
    x = 24
    for k, f in figs:
        im = Image.fromarray(f).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST)
        out.paste(im, (x, H1 - 8 - im.height), im)
        d.text((x, 4), f"{k} {f.shape[0]}x{f.shape[1]}", fill=(255, 255, 255))
        x += im.width + 24
    y0 = H1 + 8
    for bg in [(92, 98, 86), (32, 30, 40)]:
        out.paste(bg, (0, y0, out.width, y0 + H3))
        x = 20
        for _, f in game:
            im = Image.fromarray(f).resize((f.shape[1] * 2, f.shape[0] * 2), Image.NEAREST)
            out.paste(im, (x, y0 + H3 - 6 - im.height), im)
            x += im.width + 20
        y0 += H3 + 8
    out.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--zoom", type=int, default=8)
    ap.add_argument("--pick")
    a = ap.parse_args()
    cands = candidates()
    if a.sheet:
        sheet(a.sheet, cands, a.zoom)
        for k, v in cands.items():
            f = crop(v)
            print(k, f.shape[:2], len({tuple(c) for c in f[f[..., 3] > 0][:, :3]}), "colours")
    if a.pick:
        Image.fromarray(cands[a.pick]).save(lp(OUT))
        print(OUT)


if __name__ == "__main__":
    main()

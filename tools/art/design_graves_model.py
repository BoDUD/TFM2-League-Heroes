#!/usr/bin/env python3
"""Graves's step-1 designs (assets/source/graves/codex_model, 2026-10-20, Codex new-chat-4) read back on their own
grids and brought to the game's count: 57 rows hair top to soles (38 game px at PPU 1.5).

    python tools/art/design_graves_model.py --options DIR     # the candidates side by side (the user's pick)
    python tools/art/design_graves_model.py                   # writes assets/source/graves/hd/{idle,side}.png

Codex's squares (asked 16 px; regrid's own estimate): A-1 ~15 px (61 rows), A-2 ~16 px (61), side-1 ~9 px (109: drawn
far finer than asked), side-2 ~12 px (76). Each read back with regrid at its own size (alpha >= 128); then Zoe's way
(Cho'Gath's design_chogath_model.py): K colours (design_varus.kmeans), whole rows then columns dropped to the count
(keep_axis: least loss, never the face's rows / columns), the width in proportion, strips.complete_outline with the face
kept. The written pair shares one palette.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
from review_graves_size import body_height  # noqa: E402
import design_varus as dv  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "graves", "codex_model")
OUT = os.path.join(ROOT, "assets", "source", "graves", "hd")
BODY, K = 57, 32            # hair top to soles; colours
PICKS = {"idle": "A-1", "side": "side-2"}   # provisional until the user picks
# name -> (Codex's square px, face rows, face columns) on its own read-back
DRAFTS = {
    "A-1": (15.0, range(8, 19), range(25, 39)),
    "A-2": (16.0, range(8, 20), range(25, 40)),
    "side-1": (9.0, range(12, 33), range(60, 83)),
    "side-2": (12.0, range(9, 24), range(42, 60)),
}


# the faces redrawn on the grid (memory codex-face-half-squares: the cut read back a muddy skull, dark teal eyes):
# K outline, A / B / C / D the skin's four greens light to dark, E the eyes' cyan, F their pale centre, W the teeth,
# "." left as cut. (first row, first column, rows) in the written design's squares.
INK = {"K": (6, 1, 10), "A": (218, 218, 184), "B": (167, 166, 127), "C": (134, 134, 106), "D": (66, 68, 57),
       "E": (7, 234, 247), "F": (180, 250, 252), "W": (245, 251, 252)}
FACES = {
    # 3/4: both eyes two squares at one height (near 16-17, far 19-20), the open jaw: teeth, mouth, teeth
    "idle": (19, 15, ["BAAABK",
                      "CEFDFE",
                      "CDBDBK",
                      "BKWKWK",
                      "BKKKKK",
                      "BKWKWK",
                      "CBAABK",
                      "KCBCK."]),
    # side: the same face (its head stays the 3/4 one), a square wider
    "side": (28, 24, ["CEFDFEK",
                      "CABDBAK",
                      "BAABAAK",
                      "BKWKWWK",
                      "BKKKKKK",
                      "BKWKWK.",
                      "CBAABK.",
                      "KCBBK.."]),
}
# the side's staff as long as the idle's: its head (rows 0..STAFF_HEAD of the columns from STAFF_COL) set STAFF_DOWN
# rows lower over the shaft, the empty rows over it dropped (Codex drew it 13 rows over the crown, the idle 6); the
# head's collar reaches column HEAD_COL, the crown's edge column 32 from row 12 down, so the shaft is cleared from STAFF_COL
STAFF_COL, HEAD_COL, STAFF_HEAD, STAFF_DOWN = 33, 30, 11, 7


def redraw_face(fig, part):
    y0, x0, rows = FACES[part]
    out = fig.copy()
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != ".":
                out[y0 + j, x0 + i, :3] = INK[ch]
                out[y0 + j, x0 + i, 3] = 255
    return out


def shorter_staff(fig):
    out = fig.copy()
    head = fig[:STAFF_HEAD + 1, HEAD_COL:].copy()
    out[:STAFF_HEAD + 1, HEAD_COL:] = 0
    out[STAFF_HEAD + 1:STAFF_HEAD + 1 + STAFF_DOWN, STAFF_COL:] = 0
    m = head[..., 3] > 0
    out[STAFF_DOWN:STAFF_DOWN + STAFF_HEAD + 1, HEAD_COL:][m] = head[m]
    ys = np.nonzero((out[..., 3] > 0).any(1))[0]
    return out[ys.min():]


# one head in every frame (memory one-face-all-frames): the side's own head (Codex drew it bigger: the crown 3 columns
# wider, 4 rows taller) is cleared and the idle's laid on it, its near eye on the side's (idle (16, 20) -> side (25, 21)
# once the side's staff has moved). The idle's head: rows to IDLE_NECK in columns IDLE_HEAD_COLS, below them down to
# IDLE_CHIN the jaw and the hair in IDLE_JAW_COLS. The side's head cleared: rows to SIDE_NECK in SIDE_HEAD_COLS, never the
# staff (columns from 34, and its collar's rows 9-11 from column 32).
HEAD_OFF = (9, 1)
IDLE_NECK, IDLE_CHIN, IDLE_HEAD_COLS, IDLE_JAW_COLS = 23, 27, (9, 26), (14, 21)
SIDE_NECK, SIDE_HEAD_COLS = 23, (14, 33)


def same_head(side, idle):
    out = side.copy()
    H, W = out.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    staff = (xx >= 34) | ((yy >= 9) & (yy <= 11) & (xx >= 32))
    clear = (yy <= SIDE_NECK) & (xx >= SIDE_HEAD_COLS[0]) & (xx <= SIDE_HEAD_COLS[1]) & ~staff
    out[clear] = 0
    iy, ix = np.mgrid[0:idle.shape[0], 0:idle.shape[1]]
    head = (((iy <= IDLE_NECK) & (ix >= IDLE_HEAD_COLS[0]) & (ix <= IDLE_HEAD_COLS[1])) |
            ((iy > IDLE_NECK) & (iy <= IDLE_CHIN) & (ix >= IDLE_JAW_COLS[0]) & (ix <= IDLE_JAW_COLS[1])))
    head &= (idle[..., 3] > 0) & (ix < 30)            # the idle's staff stands from column 31
    ys, xs = np.nonzero(head)
    out[ys + HEAD_OFF[1], xs + HEAD_OFF[0]] = idle[ys, xs]
    return out


# one staff in every frame: the idle's staff head (Codex drew a cross of spikes there, the side a round crystal over a
# crimson bar) is the side's - rows to HEAD_ROWS of the side's columns from 31, moved STAFF_DX onto the idle's shaft
# (its middle column 33, the side's 38), the idle's own cleared from column 26 in those rows (its crown ends at 24)
HEAD_ROWS, STAFF_DX = 16, -5
IDLE_HAND = (35, 39)                    # the idle's rows of the hand gripping the staff


def same_staff(idle, side):
    """... and the shaft below it too (the idle's had cyan runes, the side's is plain steel): every row but the hand's
    (IDLE_HAND), columns 31-37 (the idle's robe ends at 30)."""
    out = idle.copy()
    out[:HEAD_ROWS + 1, 26:] = 0
    src = side[:HEAD_ROWS + 1, 31:]
    ys, xs = np.nonzero(src[..., 3] > 0)
    out[ys, xs + 31 + STAFF_DX] = src[ys, xs]
    for y in range(HEAD_ROWS + 1, min(idle.shape[0], side.shape[0])):
        if IDLE_HAND[0] <= y <= IDLE_HAND[1]:
            continue
        out[y, 31:38] = 0
        row = side[y, 31 - STAFF_DX:38 - STAFF_DX]
        m = row[:, 3] > 0
        out[y, 31:38][m] = row[m]
    return out


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(name):
    size = DRAFTS[name][0]
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"graves-model-{name}.png"))).convert("RGBA")),
                       size)
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def recolour(raw):
    idx, pal = dv.kmeans(raw, K)
    idx = np.where(raw[..., 3] > 0, idx, -1)
    return idx, pal


def paint(idx, pal):
    fig = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    fig[m, :3] = pal[idx[m]]
    fig[m, 3] = 255
    return fig


def keep_axis(lines, target, protect):
    """design_riven.keep_axis, also when the protected run touches an end (an empty part loses nothing)."""
    n = len(lines)
    lo, hi = min(protect), max(protect) + 1
    parts = [list(range(0, lo)), list(range(hi, n))]
    drop = n - target
    q0 = round(drop * len(parts[0]) / max(1, len(parts[0]) + len(parts[1])))
    kept = []
    for part, q in zip(parts, (q0, drop - q0)):
        if not part or q <= 0:
            kept.append(part)
            continue
        sub = [lines[i] for i in part]
        best = None
        for off in range(3):
            k, lost = R.pick(sub, len(part) - q, off)
            if k is not None and (best is None or lost < best[1]):
                best = (k, lost)
        kept.append([part[i] for i in best[0]])
    return kept[0] + list(range(lo, hi)) + kept[1]


def joint(names):
    """{name: (colour index map, shared palette)} with K colours over all the read-backs together."""
    raws = [read_back(n) for n in names]
    h = max(r.shape[0] for r in raws)
    both = np.zeros((h, sum(r.shape[1] for r in raws), 4), np.uint8)
    x = 0
    for r in raws:
        both[:r.shape[0], x:x + r.shape[1]] = r
        x += r.shape[1]
    idx, pal = recolour(both)
    out, x = {}, 0
    for n, r in zip(names, raws):
        out[n] = (np.where(r[..., 3] > 0, idx[:r.shape[0], x:x + r.shape[1]], -1), pal)
        x += r.shape[1]
    return out


def cut(name, coloured=None):
    """The draft at the count: (picture, rows kept, columns kept)."""
    _, fr, fc = DRAFTS[name]
    idx, pal = coloured if coloured is not None else recolour(read_back(name))
    H, W = idx.shape
    rows_to = round(H * BODY / body_height(paint(idx, pal)))
    if rows_to is None or rows_to >= H:
        return paint(idx, pal), list(range(H)), list(range(W))
    protect_r = fr if fr is not None else range(H // 2, H // 2 + 1)
    protect_c = fc if fc is not None else range(W // 2, W // 2 + 1)
    rows = [0] + [r + 1 for r in keep_axis([idx[y] for y in range(1, H)], rows_to - 1,
                                             range(protect_r.start - 1, protect_r.stop - 1))]
    sub = idx[rows]
    cols = keep_axis([sub[:, x] for x in range(W)], round(W * rows_to / H), protect_c)
    fig = paint(idx[np.ix_(rows, cols)], pal)
    keep = np.zeros(fig.shape[:2], bool)
    if fr is not None:
        r_in = [rows.index(r) for r in fr if r in rows]
        c_in = [cols.index(c) for c in fc if c in cols]
        keep[min(r_in):max(r_in) + 1, min(c_in):max(c_in) + 1] = True
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1], rows, cols


def sheet(cells, path, k=6, game=3):
    """Each candidate at k x (one square = k px) and below it as the game draws it (1/1.5 game px a square, game x)."""
    ims = []
    for label, a in cells:
        big = Image.fromarray(np.repeat(np.repeat(a, k, 0), k, 1))
        s = game / 1.5
        small = Image.fromarray(a).resize((round(a.shape[1] * s), round(a.shape[0] * s)), Image.NEAREST)
        ims.append((f"{label}  {a.shape[1]}x{a.shape[0]}", big, small))
    gap = 24
    W = sum(max(b.width, s.width) for _, b, s in ims) + gap * (len(ims) + 1)
    H = max(b.height for _, b, _ in ims) + max(s.height for _, _, s in ims) + 80
    can = Image.new("RGBA", (W, H), (196, 200, 190, 255))
    dr = ImageDraw.Draw(can)
    x = gap
    hb = max(b.height for _, b, _ in ims)
    for label, b, s in ims:
        dr.text((x, 6), label, fill=(20, 20, 20, 255))
        can.alpha_composite(b, (x, 24 + hb - b.height))
        can.alpha_composite(s, (x, H - 12 - s.height))
        x += max(b.width, s.width) + gap
    can.convert("RGB").save(lp(path))
    print(path, can.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    a = ap.parse_args()
    if a.options:
        os.makedirs(lp(a.options), exist_ok=True)
        cells = [(n, cut(n)[0]) for n in DRAFTS]
        sheet(cells, os.path.join(a.options, "graves_model_options.png"))
        for n in DRAFTS:
            r = read_back(n)
            Image.fromarray(r).save(lp(os.path.join(a.options, f"raw_{n}.png")))
            print(n, "read back", r.shape[1], "x", r.shape[0])
        for n, c in cells:
            Image.fromarray(c).save(lp(os.path.join(a.options, f"opt_{n.replace(' ', '_')}.png")))
        return
    os.makedirs(lp(OUT), exist_ok=True)
    col = joint(list(PICKS.values()))
    written = {}
    for part, name in PICKS.items():
        fig, rows, cols = cut(name, col[name])
        fig = redraw_face(fig, part)                  # FACES are in the cut's squares, before the staff moves
        if part == "side":
            fig = same_head(shorter_staff(fig), written["idle"])
        written[part] = fig
    written["idle"] = same_staff(written["idle"], written["side"])
    for part, fig in written.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{part}.png")))
        Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{part}_4x.png")))
        print(part, PICKS[part], fig.shape[1], "x", fig.shape[0])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Vladimir's game-size design candidates from Codex's step-1 raw (assets/source/vladimir/codex_model/raw).

    python tools/art/design_vladimir.py --sheet <png> [--zoom 8]   # every candidate side by side
    python tools/art/design_vladimir.py --pick NAME                # write assets/source/native/vladimir_native.png

How it came about (2026-10-08): the user picked Codex's picture A (League's idle, both clawed hands held out). Codex's
step 1 drew 86 x 48 squares three times (the generator would not draw 40 rows) and sampled the draft down to 40/37
rows itself: the face, the clasps and the coat broke into specks (Kai'Sa / Ryze / Xerath / Pyke / Gwen). At 86 -> 40
rows deleting whole lines can't get there (never two neighbours: 43 at least), so league_gwen's route (105 -> 44, the
user: 「你要参考之前的工具 ... 慢慢调整啊」):
  1. the green (#00FF00) keyed out, the raw read back on its own 16-px grid (the skill's regrid.py, alpha >= 128):
     86 x 48 (the crest's tip row 0, the eyes rows 27-29, the soles row 85);
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. to the target rows by block votes (design_gwen.votes): each game pixel looks at the source block it covers:
     see-through when less than half is opaque; the outline colour when more than INK_SHARE of it is outline (thin inner
     lines go, flat areas stay clean); else the commonest colour of the rest. Uniform: the whole figure at one scale;
     regional: the crest over the face (rows 0-REGION) squeezed harder so the face and body keep more rows;
  4. strips.complete_outline round the silhouette;
  5. lone squares (no 8-neighbour shares the colour, inside the figure, off the face) take their four neighbours'
     commonest colour when two or more agree, and dark crumbs (CRUMB squares or fewer, inside) take their lighter
     neighbours' colour (design_gwen.lone / clean_dark);
  6. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64.
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
import design_riven as R  # noqa: E402
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vladimir", "codex_model")
OUT = os.path.join(ROOT, "assets", "source", "native", "vladimir_native.png")
DRAFTS = {   # raw file, FACE_ROWS, FACE_COLS on its read-back, the crest's rows above the face
    "v1": ("vladimir_generated_source.png", range(26, 33), range(25, 36), 25),       # 86 x 48
    "v2": ("vladimir_generated_v2.png", range(21, 29), range(22, 37), 20),           # 82 x 49 (the redraw pack's
                                                                                    # generator attempt, 2026-10-08)
}
RAW = os.path.join(SRC, "raw", DRAFTS["v1"][0])
SOLE_ROW, MID_COL = 99, 64
K, INK_SHARE = 24, 0.5
REGION = 24                 # read-back rows 0-23: the crest above the face (the brow line is row 25)
FACE_RAW = (25, 34, 22, 37)  # read-back rows r0..r1, columns c0..c1: the brows, the eyes, the mouth, the chin
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
DARK, CRUMB = 60, 3
FACE_ROWS = DRAFTS["v1"][1]   # on the read-back: the brows, the eyes, the nose, the mouth (kept whole)
FACE_COLS = DRAFTS["v1"][2]   # the near lock's edge, both eyes, the cheek


def use(draft):
    global RAW, FACE_ROWS, FACE_COLS
    RAW = os.path.join(SRC, "raw", DRAFTS[draft][0])
    FACE_ROWS, FACE_COLS = DRAFTS[draft][1], DRAFTS[draft][2]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def keyed():
    a = np.asarray(Image.open(lp(RAW)).convert("RGBA")).copy()
    g = (a[..., 1].astype(int) - np.maximum(a[..., 0], a[..., 2]) > 40)
    a[g, 3] = 0
    return a


def read_back():
    """Step 1: the raw on its own grid, cropped, alpha 0/255."""
    raw, _, _ = regrid(keyed())
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def votes(idx, ink, ys, xs):
    """Step 3: one palette index (or -1) per game pixel; ys/xs the source edges of the rows/columns."""
    h, w = len(ys) - 1, len(xs) - 1
    out = np.full((h, w), -1)
    for j in range(h):
        for i in range(w):
            b = idx[int(ys[j]):max(int(ys[j]) + 1, int(np.ceil(ys[j + 1] - 1e-9))),
                    int(xs[i]):max(int(xs[i]) + 1, int(np.ceil(xs[i + 1] - 1e-9)))].ravel()
            op = b[b >= 0]
            if len(op) * 2 < len(b) or not len(op):
                continue
            rest = op[op != ink]
            if (op == ink).sum() > INK_SHARE * len(op) or not len(rest):
                out[j, i] = ink
                continue
            vals, cnt = np.unique(rest, return_counts=True)
            out[j, i] = vals[np.argmax(cnt)]
    return out


def edges(H, W, rows, crest=None):
    """Source row / column edges: uniform, or the crest (rows 0-REGION) into `crest` rows and the rest into the
    others; the columns at the body's scale."""
    if crest is None:
        ys = np.linspace(0, H, rows + 1)
        s = H / rows
    else:
        ys = np.concatenate([np.linspace(0, REGION, crest + 1), np.linspace(REGION, H, rows - crest + 1)[1:]])
        s = (H - REGION) / (rows - crest)
    w = round(W / s)
    return ys, np.linspace(0, W, w + 1)


def face_box(ys, xs):
    """The face's rows and columns on the small grid (from FACE_RAW)."""
    r0, r1, c0, c1 = FACE_RAW
    rr = [j for j in range(len(ys) - 1) if ys[j + 1] > r0 and ys[j] < r1 + 1]
    cc = [i for i in range(len(xs) - 1) if xs[i + 1] > c0 and xs[i] < c1 + 1]
    return rr[0], rr[-1], cc[0], cc[-1]


def lone(a, protect, rounds=2, need=2):
    """Step 5a (design_gwen.lone): squares no neighbour shares take their four neighbours' commonest colour."""
    for _ in range(rounds):
        b = a.copy()
        for y in range(1, a.shape[0] - 1):
            for x in range(1, a.shape[1] - 1):
                if a[y, x, 3] == 0 or protect[y, x]:
                    continue
                p = tuple(int(v) for v in a[y, x, :3])
                n8 = [a[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
                if any(q[3] == 0 for q in n8) or any(tuple(int(v) for v in q[:3]) == p for q in n8):
                    continue
                n4 = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy, dx in N4]
                best = max(set(n4), key=n4.count)
                if n4.count(best) >= need:
                    b[y, x, :3] = best
        a = b
    return a


def clean_dark(a, protect):
    """Step 5b (design_gwen.clean_dark): dark pieces of CRUMB squares or fewer inside the silhouette take their
    lighter neighbours' commonest colour."""
    H, W = a.shape[:2]
    for _ in range(2):
        op = a[..., 3] > 0
        dk = op & ((0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]) < DARK)
        seen = np.zeros((H, W), bool)
        for y0, x0 in zip(*np.nonzero(dk)):
            if seen[y0, x0]:
                continue
            comp, st, out = [], [(y0, x0)], False
            seen[y0, x0] = True
            while st:
                y, x = st.pop()
                comp.append((y, x))
                for dy, dx in N4:
                    yy, xx = y + dy, x + dx
                    if not (0 <= yy < H and 0 <= xx < W) or not op[yy, xx]:
                        out = True
                    elif dk[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        st.append((yy, xx))
            if out or len(comp) > CRUMB or any(protect[y, x] for y, x in comp):
                continue
            for y, x in comp:
                nb = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy, dx in N4
                      if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and not dk[y + dy, x + dx]]
                if nb:
                    a[y, x, :3] = max(set(nb), key=nb.count)
    return a


def on_canvas(fig):
    ys, xs = np.nonzero(fig[..., 3] > 0)
    fig = fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((fig[-3:, :, 3] > 0).any(0))[0]
    mid_x = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def build(rows, crest=None, clean=True):
    raw = read_back()
    idx, pal = dv.kmeans(raw, K)
    ink = int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))
    H, W = idx.shape
    ys, xs = edges(H, W, rows, crest)
    small = votes(idx, ink, ys, xs)
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    r0, r1, c0, c1 = face_box(ys, xs)
    keep = np.zeros(m.shape, bool)
    keep[r0:r1 + 1, c0:c1 + 1] = True
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    keep = np.pad(keep, 1)
    can, _, _ = strips.complete_outline(can, color=tuple(int(v) for v in pal[ink]), feet=fig.shape[0], keep=keep)
    if clean:
        can = lone(can, keep)
        can = clean_dark(can, keep)
    return on_canvas(can)


def keep_rows(idx, rows, crest):
    """Rows kept: crest=None -> design_riven.keep_axis over the whole height (FACE_ROWS whole, row 0 kept); else the
    crest (rows 0..FACE_ROWS.start-1) to `crest` rows and the body (below FACE_ROWS) to the rest, each by
    design_riven.pick at its least-loss offset."""
    H = idx.shape[0]
    if crest is None:
        face = range(FACE_ROWS.start - 1, FACE_ROWS.stop - 1)
        return [0] + [r + 1 for r in R.keep_axis([idx[y] for y in range(1, H)], rows - 1, face)]
    out = []
    for lo, hi, n in ((0, FACE_ROWS.start, crest), (FACE_ROWS.stop, H, rows - crest - len(FACE_ROWS))):
        lines = [idx[y] for y in range(lo, hi)]
        k = min((R.pick(lines, n, off) for off in range(3)), key=lambda t: t[1])[0]
        out += [lo + r for r in k]
        if lo == 0:
            out += list(FACE_ROWS)
    return sorted(set(out) | {0})


def build_keep(rows, clean=False, crest=None):
    """league_tryndamere's route (80 -> 40 there): whole rows and columns of the read-back deleted by
    design_riven.keep_axis (in groups, the line most like a neighbour goes, three offsets), FACE_ROWS / FACE_COLS and
    the crest's tip row whole, the width in proportion; every kept square the draft's own (k-means colours)."""
    raw = read_back()
    idx, pal = dv.kmeans(raw, K)
    ink = int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))
    H, W = idx.shape
    rr = keep_rows(idx, rows, crest)
    sub = idx[rr]
    cc = R.keep_axis([sub[:, x] for x in range(W)], round(W * rows / H), FACE_COLS)
    small = idx[np.ix_(rr, cc)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rr.index(r) for r in FACE_ROWS]
    fc = [cc.index(c) for c in FACE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    keep = np.pad(keep, 1)
    can, _, _ = strips.complete_outline(can, color=tuple(int(v) for v in pal[ink]), feet=fig.shape[0], keep=keep)
    if clean:
        can = lone(can, keep)
        can = clean_dark(can, keep)
    return on_canvas(can)


def edges_hybrid(H, W, rows, crest, body_w=None):
    """Row edges: the crest (above FACE_ROWS) into `crest` rows, FACE_ROWS one square each, the body into the rest;
    column edges: FACE_COLS one square each, the columns outside them at the body's scale."""
    f0, f1 = FACE_ROWS.start, FACE_ROWS.stop
    body_rows = rows - crest - (f1 - f0)
    ys = np.concatenate([np.linspace(0, f0, crest + 1)[:-1], np.arange(f0, f1), np.linspace(f1, H, body_rows + 1)])
    s = (H - f1) / body_rows
    c0, c1 = FACE_COLS.start, FACE_COLS.stop
    left = body_w if body_w else max(1, round(c0 / s))
    right = max(1, round((W - c1) / s))
    xs = np.concatenate([np.linspace(0, c0, left + 1)[:-1], np.arange(c0, c1), np.linspace(c1, W, right + 1)])
    return ys, xs


def build_hybrid(rows, crest, clean=True):
    """The user (v2 cuts, 2026-10-08): 「头太大了 身体细节太差了」 - the head squeezed harder, the body voted in blocks
    (design_gwen's votes keep the colour masses whole where deleted lines broke them), the face square for square."""
    raw = read_back()
    idx, pal = dv.kmeans(raw, K)
    ink = int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))
    H, W = idx.shape
    ys, xs = edges_hybrid(H, W, rows, crest)
    small = votes(idx, ink, ys, xs)
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    r0, r1, c0, c1 = face_box(ys, xs)
    keep = np.zeros(m.shape, bool)
    keep[r0:r1 + 1, c0:c1 + 1] = True
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    keep = np.pad(keep, 1)
    can, _, _ = strips.complete_outline(can, color=tuple(int(v) for v in pal[ink]), feet=fig.shape[0], keep=keep)
    if clean:
        can = lone(can, keep)
        can = clean_dark(can, keep)
    return on_canvas(can)


def build_vote(rows, crest=None, clean=True):
    """Uniform block votes (82 -> 41 = exact 2x2 blocks) with the eyes winning their block (a 2x2 eye would lose a
    vote to skin), the brows too; optional: the crest (above FACE_ROWS) into `crest` rows, the rest at the body's
    scale. design_gwen's route, the face then fixed by hand in polish."""
    raw = read_back()
    idx, pal = dv.kmeans(raw, K)
    ink = int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))
    H, W = idx.shape
    f0 = FACE_ROWS.start
    if crest is None:
        ys = np.linspace(0, H, rows + 1)
        sc = H / rows
    else:
        ys = np.concatenate([np.linspace(0, f0, crest + 1)[:-1], np.linspace(f0, H, rows - crest + 1)])
        sc = (H - f0) / (rows - crest)
    xs = np.linspace(0, W, round(W / sc) + 1)
    small = votes(idx, ink, ys, xs)
    # the eyes: a block holding an eye square in the face box takes the eye colour
    lab = (pal.astype(int) * [0.299, 0.587, 0.114]).sum(1)
    eye = [i for i in range(len(pal)) if pal[i][0] > 190 and pal[i][1] < 90 and pal[i][2] < 90]
    r0, r1, c0, c1 = face_box(ys, xs)
    for j in range(r0, r1 + 1):
        for i in range(c0, c1 + 1):
            b = idx[int(ys[j]):int(np.ceil(ys[j + 1] - 1e-9)), int(xs[i]):int(np.ceil(xs[i + 1] - 1e-9))]
            hit = [e for e in eye if (b == e).any()]
            if hit:
                small[j, i] = hit[0]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    keep[r0:r1 + 1, c0:c1 + 1] = True
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    keep = np.pad(keep, 1)
    can, _, _ = strips.complete_outline(can, color=tuple(int(v) for v in pal[ink]), feet=fig.shape[0], keep=keep)
    if clean:
        can = lone(can, keep)
        can = clean_dark(can, keep)
    return on_canvas(can)


def build_hybrid2(rows, crest, ink_share=0.6, clean=True):
    """Rows: the crest (above FACE_ROWS) voted into `crest` rows, FACE_ROWS one square each, the body voted at its
    own scale; columns: ALL voted at the body's scale (the face's columns too - whole columns made the head wide);
    the eyes win their block inside the face box; inner dark lines drop (a block is ink only when more than
    ink_share of it is), the outline closed. The user (2026-10-08): the line cuts left the body a dark speckle."""
    global INK_SHARE
    raw = read_back()
    idx, pal = dv.kmeans(raw, K)
    ink = int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))
    H, W = idx.shape
    f0, f1 = FACE_ROWS.start, FACE_ROWS.stop
    body_rows = rows - crest - (f1 - f0)
    ys = np.concatenate([np.linspace(0, f0, crest + 1)[:-1], np.arange(f0, f1), np.linspace(f1, H, body_rows + 1)])
    sc = (H - f1) / body_rows
    xs = np.linspace(0, W, round(W / sc) + 1)
    old, INK_SHARE = INK_SHARE, ink_share
    try:
        small = votes(idx, ink, ys, xs)
    finally:
        INK_SHARE = old
    eye = [i for i in range(len(pal)) if pal[i][0] > 190 and pal[i][1] < 90 and pal[i][2] < 90]
    r0, r1, c0, c1 = face_box(ys, xs)
    for j in range(r0, r1 + 1):
        for i in range(c0, c1 + 1):
            b = idx[int(ys[j]):int(np.ceil(ys[j + 1] - 1e-9)), int(xs[i]):int(np.ceil(xs[i + 1] - 1e-9))]
            hit = [e for e in eye if (b == e).any()]
            if hit:
                small[j, i] = hit[0]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    keep[r0:r1 + 1, c0:c1 + 1] = True
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    keep = np.pad(keep, 1)
    can, _, _ = strips.complete_outline(can, color=tuple(int(v) for v in pal[ink]), feet=fig.shape[0], keep=keep)
    if clean:
        can = lone(can, keep)
        can = clean_dark(can, keep)
    return on_canvas(can)


# ---------------------------------------------------------------- detail-priority 2:1 (the user: 「太模糊了」)
# families of the v2 draft's k-means colours (K 24, seed 1), by rule: ink dark; steel bluish; skin/hair/peach/stripe
# by hue and lightness; the rest coat red. A 2x2 source block takes the colour with the highest count x weight, so a
# 1-px trim, claw, clasp or stripe line of the draft survives against the coat's red around it (majority votes ate them).
WEIGHTS = {"ink": 1.0, "coat": 1.0, "hair": 1.15, "skin": 1.2, "peach": 1.6, "steel": 1.6, "stripe": 1.6, "?": 1.0}
W2 = {"ink": 1.0, "coat": 1.0, "hair": 1.15, "skin": 1.2, "peach": 2.1, "steel": 2.1, "stripe": 2.1, "?": 1.0}
W3 = {"ink": 1.3, "coat": 1.0, "hair": 1.15, "skin": 1.2, "peach": 1.6, "steel": 1.6, "stripe": 1.6, "?": 1.0}


FAMILY_HEX = {"#B3604B": "peach", "#817A8E": "steel", "#EC6C80": "stripe"}   # the rules' misses on the v2 palette


def family(c):
    r, g, b = (int(v) for v in c)
    h = "#%02X%02X%02X" % (r, g, b)
    if h in FAMILY_HEX:
        return FAMILY_HEX[h]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum < 25:
        return "ink"
    if b > r + 15:
        return "steel"
    if r > 200 and g > 190 and b > 170:
        return "skin" if r - b > 30 and g > 205 and b < 215 else "hair"
    if r > 200 and g > 85 and b < 160 and r - b > 90:
        return "peach"
    if r > 200 and 90 < g < 160 and b > 110:
        return "stripe"
    if 140 < r < 235 and g > 80 and b > 100:
        return "hair"
    return "coat"


def detail_votes(idx, pal, ys, xs, weights=None):
    """One palette index (or -1) per output square: the family with the highest (squares in the block) x weight wins,
    then its commonest colour in the block (the coat's five reds vote together, else a 1-square trim beat them);
    see-through when the block is at least half see-through and the winner is ink or coat."""
    weights = weights or WEIGHTS
    fam = [family(c) for c in pal]
    lum = (pal.astype(int) * [0.299, 0.587, 0.114]).sum(1)
    h, w = len(ys) - 1, len(xs) - 1
    out = np.full((h, w), -1)
    for j in range(h):
        for i in range(w):
            b = idx[int(ys[j]):max(int(ys[j]) + 1, int(np.ceil(ys[j + 1] - 1e-9))),
                    int(xs[i]):max(int(xs[i]) + 1, int(np.ceil(xs[i + 1] - 1e-9)))].ravel()
            op = b[b >= 0]
            if not len(op):
                continue
            tally = {}
            for v in op:
                tally[fam[v]] = tally.get(fam[v], 0) + 1
            best = max(tally, key=lambda f: (tally[f] * weights[f], f != "ink"))
            empty = len(b) - len(op)
            if empty > tally[best] * weights[best] and best in ("ink", "coat"):
                continue
            if empty * 2 > len(b) and best in ("ink", "coat"):
                continue
            mem = [v for v in op if fam[v] == best]
            vals, cnt = np.unique(mem, return_counts=True)
            top = vals[cnt == cnt.max()]
            out[j, i] = int(top[np.argsort(lum[top])[len(top) // 2]])
    return out


def build_detail(phase=(0, 0), crest_rows=None, weights=None, outline=True):
    """Uniform 2:1 from the v2 draft (82 x 49 -> ~41 x 25) with detail priority; phase = (row, column) offset of the
    2x2 grid; crest_rows: the rows above FACE_ROWS squeezed into this many output rows instead of half."""
    raw = read_back()
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    oy, ox = phase
    f0 = FACE_ROWS.start
    if crest_rows:
        top = np.linspace(0, f0, crest_rows + 1)[:-1]
        rest = np.arange(f0, H + 2, 2.0)
        ys = np.concatenate([top, rest])
    else:
        ys = np.arange(-oy, H + 2, 2.0)
        ys[0] = 0
    ys = ys[ys < H]
    ys = np.append(ys, H)
    xs = np.arange(-ox, W + 2, 2.0)
    xs[0] = 0
    xs = xs[xs < W]
    xs = np.append(xs, W)
    small = detail_votes(idx, pal, ys, xs, weights)
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    if outline:
        ink = int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))
        can, _, _ = strips.complete_outline(can, color=tuple(int(v) for v in pal[ink]), feet=fig.shape[0])
    return on_canvas(can)


CANDS = {"u42": (40, None), "r42": (42, 8)}
HYB2 = {"g44_5": (44, 5), "g44_5i": (44, 5, 0.5), "g46_6": (46, 6), "g42_5": (42, 5)}
VOTES = {"v41": (41, None), "v41raw": (41, None, False), "v39": (39, 7), "v43": (43, None)}
HYBRIDS = {"h42_5": (42, 5), "h44_5": (44, 5), "h44_6": (44, 6), "h46_6": (46, 6)}
KEEPS = {"k42": (42, False), "k42c": (42, True), "c40": (40, True, 7), "c42": (42, True, 8), "c44": (44, True, 8)}


def candidates(clean=True):
    out = {f"d{oy}{ox}": build_detail((oy, ox)) for oy in (0, 1) for ox in (0, 1)}
    out["d00_w2"] = build_detail((0, 0), weights=W2)
    out["d00_w3"] = build_detail((0, 0), weights=W3)
    return out


def sheet(path, zoom, extra=()):
    figs = []
    for name, a in list(candidates().items()) + list(extra):
        ys, xs = np.nonzero(a[..., 3] > 0)
        figs.append((name, a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]))
    gap = 4
    Hm = max(f.shape[0] for _, f in figs) + 4
    W = sum(f.shape[1] for _, f in figs) + gap * (len(figs) + 1)
    img = Image.new("RGBA", (W * zoom, Hm * zoom + 16), (225, 225, 225, 255))
    d = ImageDraw.Draw(img)
    x = gap
    for name, f in figs:
        img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * zoom, f.shape[0] * zoom), Image.NEAREST),
                            (x * zoom, 16 + (Hm - 2 - f.shape[0]) * zoom))
        d.text((x * zoom, 2), f"{name} {f.shape[0]}x{f.shape[1]}", fill=(20, 20, 20, 255))
        x += f.shape[1] + gap
    img.convert("RGB").save(path)
    print(path, img.size)


# ------------------------------------------------------------------ the approved design (the user, 2026-10-08: 「40 行 可以了」)
# None of the automatic routes above reached the quality bar (「太模糊了」): the head is k44_5's (the v2 draft's own squares,
# the face rows whole), the eyes and crest specks fixed by hand; the body was written square by square on the v2 draft's
# reference grid (the draft's own block in every square, work/vl/edit in the 弗拉基米尔 session); then whole rows and
# columns were deleted to 40 rows (design_akali.dp_keep, the face, the clasps, the cuffs, the knees and the shoes kept).
# The result is kept as a letter grid (assets/source/vladimir/design/vladimir_design_40.txt: "NNN" canvas row + the
# letters of columns 47-78); --final renders it to the native design.
FINAL = os.path.join(ROOT, "assets", "source", "vladimir", "design", "vladimir_design_40.txt")
FINAL_PAL = {"0": "#1D010B", "a": "#2E010D", "b": "#5D0315", "c": "#910419", "e": "#DA010F",
             "p": "#FBC891", "q": "#FA9C6B", "r": "#B3604B",
             "s": "#D5E6F7", "t": "#87A1C6", "u": "#3D496A",
             "v": "#F3909F", "w": "#EC6C80",
             "k": "#F4E0CC", "h": "#FCEBE8", "i": "#E1B3BB", "j": "#B98495", "m": "#965B70",
             "x": "#FF2A2A", "y": "#FFC8C8"}
FINAL_X0 = 47


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def final():
    can = np.zeros((128, 128, 4), np.uint8)
    for line in open(lp(FINAL), encoding="utf-8"):
        line = line.rstrip("\r\n")
        if len(line) < 4 or not line[:3].strip().isdigit():
            continue
        y = int(line[:3])
        for i, ch in enumerate(line[3:]):
            if ch in (" ", "."):
                continue
            can[y, FINAL_X0 + i, :3] = hx(FINAL_PAL[ch])
            can[y, FINAL_X0 + i, 3] = 255
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--zoom", type=int, default=8)
    ap.add_argument("--pick")
    ap.add_argument("--draft", default="v1", choices=list(DRAFTS))
    ap.add_argument("--final", action="store_true", help="write the approved design (FINAL) to OUT")
    ap.add_argument("--check", action="store_true", help="compare FINAL with the committed OUT")
    a = ap.parse_args()
    if a.final or a.check:
        can = final()
        if a.check:
            old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))[4::8, 4::8]
            print("same" if (old == can).all() else f"differs in {int((old != can).any(-1).sum())} squares")
        else:
            Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(lp(OUT))
            print("wrote", OUT)
        return
    use(a.draft)
    if a.sheet:
        sheet(a.sheet, a.zoom)
    if a.pick:
        can = build_hybrid2(*HYB2[a.pick]) if a.pick in HYB2 else build_keep(*KEEPS[a.pick])
        Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(lp(OUT))
        print("wrote", OUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Nautilus's design (assets/source/native/nautilus_native.png): Codex's generated draft read back on its own grid and
shrunk by whole rows and columns, every kept square the draft's own (tools/art/design_tryndamere.py's way, as
tools/art/design_viego.py).

    python tools/art/design_nautilus.py --sheet OUT.png      # the cut options beside Codex's cut and the pack's heroes
    python tools/art/design_nautilus.py --pick p35 [--check]  # write (or compare) the native design

How it came about (2026-10-11): the user picked Codex's picture A (codex_picture/nautilus-model-A.png: League's idle,
the anchor on his back). Codex's step 1 (codex_model/) came back with its own 35-row A / B cut from a coarse draft
(raw/A_simple.png, 10 px squares): the helmet and the red eyes clean, but the anchor on his back cut into grey specks.
The draft itself reads back as 67 x 83 squares; the helmet's hood tops row HELMET (21), the soles row 82 (62 rows helmet
to soles); the anchor rises 21 rows above the helmet - at 35 rows that is 12 above, too tall (「注意模型不要过大」).
Options (OPTIONS): `p<N>` = every row in proportion (N rows helmet to soles); `s<N>` = the body's rows (HELMET..82) to N
and the rows above the helmet (the anchor's crown and flukes) to TOP[N], so the anchor stands lower above him.
The user first picked s35, then (「你这头也太大了 不奇怪吗」, region cuts shrinking the helmet tried and dropped) settled
on **p35** (39 x 48, the anchor 11 rows above the helmet): 「用这个吧 感觉这个最还原」.
Steps:
  1. the raw read back on its own grid (the skill's regrid.py, alpha >= 128);
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. rows by design_riven.keep_axis (rows most like a neighbour go, three offsets, the least loss kept) - the anchor's
     rows above the helmet by design_riven.pick on their own for s<N> - never FACE_ROWS (the viewing slit and the eyes);
     then the columns the same, the width in proportion to the body, never FACE_COLS;
  4. strips.complete_outline where a deleted line held the outline (the slit and the eyes never touched);
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64.
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
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
import tfm2_ase  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nautilus", "codex_model")
OUT = os.path.join(ROOT, "assets", "source", "native", "nautilus_native.png")
K = 24
# the two raw drafts, on their own read-back grids (row, column; ranges inclusive of start, exclusive of stop)
DRAFTS = {
    # raw/A_simple.png (10 px squares, 67 x 83): options p<N> / s<N>
    "simple": dict(raw="A_simple.png", shape=(83, 67), helmet=21, soles=82,
                   face_rows=range(37, 43), face_cols=range(32, 47),        # the slit with the eyes, the jaw guard's top
                   holes=((27, 28), (30, 31), (33, 34)), hole_cols=(38, 39), hole_box=(27, 35, 37, 40)),
    # raw/A_first.png (11 px squares, 71 x 78), Codex's first draft: the helmet narrower than the shoulders, the chest
    # plates showing - the user, pointing at it: 「头适当的小一点 学这张图」. Options f<N> (in proportion)
    "first": dict(raw="A_first.png", shape=(78, 71), helmet=22, soles=77,
                  face_rows=range(39, 43), face_cols=range(38, 50),
                  holes=((29, 29), (31, 32), (34, 35)), hole_cols=(43, 44), hole_box=(29, 36, 42, 45)),
}
OPTIONS = ("p35", "f35", "f33", "f31")

TOP = {32: 6, 35: 7, 38: 8}         # s<N>: rows kept above the helmet (the anchor's crown and flukes)
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3
NEIGHBOURS = ["alistar", "blitzcrank", "leona", "thresh", "shen", "viego"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(draft="simple"):
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, "raw", DRAFTS[draft]["raw"]))).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def least(lines, n_out):
    """design_riven.pick at the offset that loses least (no protected run)."""
    best = None
    for off in range(3):
        k, lost = R.pick(lines, n_out, off)
        if k is not None and (best is None or lost < best[1]):
            best = (k, lost)
    return best[0]


def holes(small, rows, cols, idx, pal, d):
    """The three vent holes stay three dots: deleted rows between them merged two or three into one dark bar (a "B"
    on the helmet). The holes' squares that survived (every square in HOLE_BOX darker than 150 summed RGB: the draft's
    holes hold three of the K near-blacks) go back to the bronze beside them, then each hole is one dark square on the
    first kept hole column, a bronze row between them."""
    HOLES, HOLE_COLS = d["holes"], d["hole_cols"]
    dark = idx[HOLES[0][0], HOLE_COLS[0]]
    col = next(cols.index(c) for c in HOLE_COLS if c in cols)
    bronze = idx[HOLES[0][0], HOLE_COLS[0] - 1]
    y0, y1, x0, x1 = d["hole_box"]
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            if y0 <= r <= y1 and x0 <= c <= x1 and small[i, j] >= 0 and pal[small[i, j]].sum() < 150:
                small[i, j] = bronze
    kept = [i for i, r in enumerate(rows) if HOLES[0][0] - 1 <= r <= HOLES[-1][1] + 1]
    first = kept[0] + (1 if len(kept) >= 6 else 0)
    for k in range(3):
        if first + 2 * k <= kept[-1]:
            small[first + 2 * k, col] = dark


def build(option):
    kind, n = option[0], int(option[1:])
    d = DRAFTS["first" if kind == "f" else "simple"]
    kind = "p" if kind == "f" else kind
    HELMET, SOLES, FACE_ROWS, FACE_COLS = d["helmet"], d["soles"], d["face_rows"], d["face_cols"]
    raw = read_back("first" if option[0] == "f" else "simple")
    assert raw.shape[:2] == d["shape"], raw.shape
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    body = SOLES - HELMET + 1
    lines = [idx[y] for y in range(H)]
    if kind == "p":
        rows = R.keep_axis(lines, round(H * n / body), FACE_ROWS)
    else:
        top = [i for i in least(lines[:HELMET], TOP[n])]
        low = R.keep_axis(lines[HELMET:], n, [r - HELMET for r in FACE_ROWS])
        rows = top + [HELMET + r for r in low]
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], round(W * n / body), FACE_COLS)
    small = idx[np.ix_(rows, cols)]
    holes(small, rows, cols, idx, pal, d)
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in FACE_ROWS if r in rows]
    fc = [cols.index(c) for c in FACE_COLS if c in cols]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    helmet = rows.index(min(r for r in rows if r >= HELMET))
    return out, rows, cols, added, fig.shape, helmet


def idle(hero):
    sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    f = sp.frames[sp.tag_frames("idle")[0]]
    return np.asarray(f.crop(f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox()))


def trimmed(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def sheet(path):
    """Codex's own A / B cuts, the options, then the pack's heroes, on one soles line at 2x and 4x."""
    shots = [(f"codex {v}", trimmed(np.asarray(Image.open(lp(os.path.join(SRC, f"nautilus_design_{v}_1x.png")))
                                               .convert("RGBA")))) for v in "AB"]
    for o in OPTIONS:
        out, rows, cols, added, shape, helmet = build(o)
        shots.append((f"{o}: {shape[1]}x{shape[0]}, anchor +{helmet}", trimmed(out)))
    for hero in NEIGHBOURS:
        a = idle(hero)
        shots.append((f"{hero} {a.shape[1]}x{a.shape[0]}", a))
    tall = max(a.shape[0] for _, a in shots)
    big, pad = 4, 6
    w2 = sum(a.shape[1] * 2 + pad for _, a in shots) + pad
    w4 = sum(max(a.shape[1] * big, 150) + pad * 3 for _, a in shots) + pad * 3
    W = max(w2, w4)
    img = Image.new("RGBA", (W, tall * 2 + tall * big + 70), (205, 205, 205, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for name, a in shots:
        im = Image.fromarray(a).resize((a.shape[1] * 2, a.shape[0] * 2), Image.NEAREST)
        img.alpha_composite(im, (x, tall * 2 - im.height + 4))
        x += im.width + pad
    y4 = tall * 2 + 20
    x = pad * 3
    for name, a in shots:
        im = Image.fromarray(a).resize((a.shape[1] * big, a.shape[0] * big), Image.NEAREST)
        img.alpha_composite(im, (x, y4 + tall * big - im.height))
        d.text((x, y4 + tall * big + 6), name, fill=(0, 0, 0, 255))
        x += max(im.width, 150) + pad * 3
    img.convert("RGB").save(path)
    print("wrote", path, img.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--pick")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.sheet:
        sheet(a.sheet)
    if a.pick:
        out, rows, cols, added, shape, helmet = build(a.pick)
        print("rows kept", len(rows), "cols kept", len(cols), "figure", shape, "anchor above the helmet", helmet,
              "outline squares added", added)
        if a.check:
            old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
            print("same as the committed design:", np.array_equal(old, out))
        else:
            Image.fromarray(out).save(lp(OUT))
            print("wrote", OUT)


if __name__ == "__main__":
    main()

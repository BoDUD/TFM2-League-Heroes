#!/usr/bin/env python3
"""Viego's design (assets/source/native/viego_native.png): Codex's generated draft read back on its own grid and
shrunk by whole rows and columns, every kept square the draft's own (tools/art/design_tryndamere.py's way).

    python tools/art/design_viego.py --sheet OUT.png      # the cut options beside the pack's heroes
    python tools/art/design_viego.py --pick 46 [--check]  # write (or compare) the native design

How it came about (2026-10-11): the user picked Codex's picture A (codex_picture/viego-model-A.png: League's idle, the
greatsword on his far shoulder). Codex's step 1 (codex_model/) came back with its own 40-row A / B cut from a coarse
draft: the face a white blob, the guard and crown in specks. The user: 「按蛮王那种方法慢慢调吧 codex做的太差了」. Its
second raw draft (raw/viego-A-attempt2.png, 10 px squares) has the cleanest face and chibi proportions: 77 x 77 squares on
its own grid, the crown's top on row 12, the soles on row 76 (65 rows crown to soles; the blade's tip 12 rows higher).
Steps:
  1. the raw read back on its own grid (the skill's regrid.py, alpha >= 128);
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. to the picked height (crown to soles) by whole rows - all 77 rows in proportion, so the blade above the crown shrinks
     with him - then the columns the same, the width in proportion (design_riven.keep_axis: rows most like a neighbour
     go, three offsets of the grouping, the least loss kept), never FACE_ROWS / FACE_COLS (the hair's fringe, the brows,
     the teal eyes, the nose, the mouth and the chin) which stay square for square;
  4. strips.complete_outline where a deleted line held the outline (the face never touched);
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

RAW = os.path.join(ROOT, "assets", "source", "viego", "codex_model", "raw", "viego-A-attempt2.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "viego_native.png")
K = 28
CROWN, SOLES = 12, 76               # on the 77 x 77 read-back
FACE_ROWS = range(26, 35)           # the fringe over the brows, the eyes, the nose, the mouth, the chin
FACE_COLS = range(31, 42)           # the near cheek to the far eye
HEIGHTS = (52, 46, 42, 40)          # the options: rows from the crown's top to the soles
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3
NEIGHBOURS = ["talon", "zed", "shen", "garen", "tryndamere", "xinzhao"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def build(height):
    raw = read_back()
    assert raw.shape[:2] == (77, 77), raw.shape
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    n_rows = round(H * height / (SOLES - CROWN + 1))
    rows = R.keep_axis([idx[y] for y in range(H)], n_rows, FACE_ROWS)
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], round(W * n_rows / H), FACE_COLS)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in FACE_ROWS]
    fc = [cols.index(c) for c in FACE_COLS]
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
    crown = rows.index(min(r for r in rows if r >= CROWN))
    return out, rows, cols, added, fig.shape, crown


def idle(hero):
    sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    f = sp.frames[sp.tag_frames("idle")[0]]
    return np.asarray(f.crop(f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox()))


def sheet(path):
    """Codex's own 40-row cut, the options, then the pack's heroes, on one soles line at 1x and 4x."""
    shots = [("codex 40", np.asarray(Image.open(lp(os.path.join(ROOT, "assets", "source", "viego", "codex_model",
                                                                  "viego_design_A_1x.png"))).convert("RGBA")))]
    for h in HEIGHTS:
        out, rows, cols, added, shape, _ = build(h)
        ys, xs = np.nonzero(out[..., 3] > 0)
        shots.append((f"{h} rows ({shape[1]}x{shape[0]})", out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]))
    for hero in NEIGHBOURS:
        a = idle(hero)
        shots.append((f"{hero} {a.shape[1]}x{a.shape[0]}", a))
    tall = max(a.shape[0] for _, a in shots)
    big = 4
    pad = 6
    w1 = sum(a.shape[1] + pad for _, a in shots) + pad
    w4 = sum(a.shape[1] * big + pad * 3 for _, a in shots) + pad * 3
    W = max(w1 * 2, w4)
    img = Image.new("RGBA", (W, tall * 2 + tall * big + 70), (205, 205, 205, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for name, a in shots:      # 2x row (game size doubled)
        im = Image.fromarray(a).resize((a.shape[1] * 2, a.shape[0] * 2), Image.NEAREST)
        img.alpha_composite(im, (x, tall * 2 - im.height + 4))
        x += im.width + pad
    y4 = tall * 2 + 20
    x = pad * 3
    for name, a in shots:
        im = Image.fromarray(a).resize((a.shape[1] * big, a.shape[0] * big), Image.NEAREST)
        img.alpha_composite(im, (x, y4 + tall * big - im.height))
        d.text((x, y4 + tall * big + 6), name, fill=(0, 0, 0, 255))
        x += im.width + pad * 3
    img.convert("RGB").save(path)
    print("wrote", path, img.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--pick", type=int)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.sheet:
        sheet(a.sheet)
    if a.pick:
        out, rows, cols, added, shape, crown = build(a.pick)
        print("rows kept", len(rows), "cols kept", len(cols), "figure", shape, "outline squares added", added)
        if a.check:
            old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
            print("same as the committed design:", np.array_equal(old, out))
        else:
            Image.fromarray(out).save(lp(OUT))
            print("wrote", OUT)


if __name__ == "__main__":
    main()

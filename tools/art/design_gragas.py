#!/usr/bin/env python3
"""Gragas's design (assets/source/native/gragas_native.png = the 3/4 front for the idle and the card,
assets/source/native/gragas_side.png = the side-on view every action is posed from): Codex's step-1 drafts read back on
their own grids and shrunk by whole rows and columns, every kept square the draft's own (tools/art/design_tryndamere.py's
way, as design_nautilus.py; memory design-tryndamere-way).

    python tools/art/design_gragas.py --sheet OUT.png              # the cut options beside Codex's cuts and the pack's heroes
    python tools/art/design_gragas.py --pick A40 [--check]         # write (or compare) the front and side designs

How it came about (2026-10-12): the user picked Codex's picture A (codex_picture/gragas-model-A.png: the keg on his back).
Codex's step 1 (codex_model/) drew the design in two views and two takes (front-A/B, side-A/B) and cut its own 36-row
copies from them - muddy (the eyes, the X scar and the beard braids merged). Its raw drafts (codex_model/raw/) are clean
pixel art on their own grids (14 px squares for the fronts, 12 for the sides): front-A reads back as 71 x 86 squares,
side-A 71 x 96, front-B 70 x 85, side-B 80 x 100.
Options `<take><N>`: the take's front and side, each brought to N rows from the top of his head to the soles (the keg's
rows above the head in proportion).
Steps:
  1. each raw read back on its own grid (the skill's regrid.py, alpha >= 128);
  2. every square one of K colours of that read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. rows by design_riven.keep_axis (rows most like a neighbour go, three offsets, the least loss kept), never the face's
     rows (brows, eyes, nose); then the columns the same, the width in proportion, never the face's columns;
  4. strips.complete_outline where a deleted line held the outline (the face never touched);
  5. on the 128x128 canvas: the soles on row 99, the middle of the feet (the lowest three rows) on column 64.
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

SRC = os.path.join(ROOT, "assets", "source", "gragas", "codex_model")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
OUT = {"front": os.path.join(NATIVE, "gragas_native.png"), "side": os.path.join(NATIVE, "gragas_side.png")}
K = 24
# the raw drafts read back (rows, columns), the top of his head and the soles, the face (brows to the mouth) kept whole
DRAFTS = {
    "front-A": dict(shape=(86, 71), head=2, soles=85, face_rows=range(9, 19), face_cols=range(36, 53)),
    "side-A": dict(shape=(96, 71), head=4, soles=95, face_rows=range(9, 19), face_cols=range(44, 62)),
    "front-B": dict(shape=(85, 70), head=2, soles=84, face_rows=range(8, 20), face_cols=range(35, 53)),
    "side-B": dict(shape=(100, 80), head=2, soles=99, face_rows=range(9, 20), face_cols=range(44, 65)),
}
OPTIONS = ("A36", "A40", "A43", "B36", "B40", "B43")
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3
NEIGHBOURS = ["nautilus", "tryndamere", "sett", "shen", "alistar"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(draft):
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"gragas-{draft}-raw.png"))).convert("RGBA")))
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


def axis(lines, n_out, protect):
    return R.keep_axis(lines, n_out, protect) if protect else least(lines, n_out)


def build(draft, n, protect=False):
    """One view of a take at n rows head to soles, on the 128 canvas; protect = never cut the face's rows and columns
    (that crushed the body under a giant head here: the face is 10 of the draft's 84 rows, so all the cuts fell below it)."""
    d = DRAFTS[draft]
    raw = read_back(draft)
    assert raw.shape[:2] == d["shape"], (draft, raw.shape)
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    body = d["soles"] - d["head"] + 1
    rows = axis([idx[y] for y in range(H)], round(H * n / body), d["face_rows"] if protect else [])
    sub = idx[rows]
    cols = axis([sub[:, x] for x in range(W)], round(W * n / body), d["face_cols"] if protect else [])
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in d["face_rows"] if r in rows]
    fc = [cols.index(c) for c in d["face_cols"] if c in cols]
    if fr and fc:
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
    return out, fig.shape, added


def idle(hero):
    sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    f = sp.frames[sp.tag_frames("idle")[0]]
    return np.asarray(f.crop(f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox()))


def trimmed(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def sheet(path):
    """Codex's own 36-row cuts, the options (front and side), then the pack's heroes, on one soles line at 2x and 4x."""
    shots = [(f"codex {v}", trimmed(np.asarray(Image.open(lp(os.path.join(SRC, f"gragas-{v}_1x.png"))).convert("RGBA"))))
             for v in ("front-A", "side-A")]
    for o in OPTIONS:
        take, n = o[0], int(o[1:])
        for view in ("front", "side"):
            out, shape, _ = build(f"{view}-{take}", n)
            shots.append((f"{o} {view} {shape[1]}x{shape[0]}", trimmed(out)))
    for hero in NEIGHBOURS:
        a = idle(hero)
        shots.append((f"{hero} {a.shape[1]}x{a.shape[0]}", a))
    tall = max(a.shape[0] for _, a in shots)
    big, pad = 4, 6
    per_row = 8
    rows_ = [shots[i:i + per_row] for i in range(0, len(shots), per_row)]
    W = max(sum(max(a.shape[1] * big, 150) + pad * 3 for _, a in r) for r in rows_) + pad * 3
    w2 = sum(a.shape[1] * 2 + pad for _, a in shots) + pad
    W = max(W, w2)
    img = Image.new("RGBA", (W, tall * 2 + 30 + len(rows_) * (tall * big + 30)), (205, 205, 205, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for name, a in shots:
        im = Image.fromarray(a).resize((a.shape[1] * 2, a.shape[0] * 2), Image.NEAREST)
        img.alpha_composite(im, (x, tall * 2 - im.height + 4))
        x += im.width + pad
    y4 = tall * 2 + 20
    for r in rows_:
        x = pad * 3
        for name, a in r:
            im = Image.fromarray(a).resize((a.shape[1] * big, a.shape[0] * big), Image.NEAREST)
            img.alpha_composite(im, (x, y4 + tall * big - im.height))
            d.text((x, y4 + tall * big + 4), name, fill=(0, 0, 0, 255))
            x += max(im.width, 150) + pad * 3
        y4 += tall * big + 30
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
        take, n = a.pick[0], int(a.pick[1:])
        for view in ("front", "side"):
            out, shape, added = build(f"{view}-{take}", n)
            print(view, "figure", shape, "outline squares added", added)
            if a.check:
                old = np.asarray(Image.open(lp(OUT[view])).convert("RGBA"))
                print("  same as the committed design:", np.array_equal(old, out))
            else:
                Image.fromarray(out).save(lp(OUT[view]))
                print("  wrote", OUT[view])


if __name__ == "__main__":
    main()

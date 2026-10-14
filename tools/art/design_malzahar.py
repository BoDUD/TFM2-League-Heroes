#!/usr/bin/env python3
"""league_malzahar's dense design (PPU 2.2) from Codex's on-grid delivery: assets/source/malzahar/hd/front.png.

    python tools/art/design_malzahar.py [--check]

The user's picks (2026-10-14): version **B** (League's float: puffy trousers, shin guards, pointed boots hanging toes
down) at **PPU 2.2** (league_zeri's density) from dist/malzahar_packs/review/malzahar_density.png / malzahar_AB.png.
Codex's own 53 x 80 grid version (codex_grid/malzahar-grid-B_1x.png) is a programmatic repaint that lost the face and
broke the arms; its raw draft (codex_grid/raw/B-01.png) is clean pixel art on ~8-px squares (116 x 152 read back), so
the design is that draft brought to 77 rows (35 game px x 2.2) my way:
  1. regrid.py reads the draft on its own grid; Codex's haze (alpha < 128, near-white joined to it) cleared.
  2. 40 k-means colours (Lab) of the lit squares + the outline (near-black).
  3. pixel_down.pixelate to 77 rows, the pivot under the middle (each square the mean snapped to the palette, outline
     where dark).
  4. The glow (the four diamond marks on the hood, the two eyes) brightness-wins: in the head's rows a square takes
     white where a quarter of it is white in the draft, pale blue where a third is pale blue - the plain mean merged the
     small marks into the magenta and the eyes into the shadow.
  4b. The dagger and the buckle the same way: gold (three golds) where 30 % of a square is gold in the draft, the
     sheath's blue-grey where 40 % is, in the gold's band - the plain mean turned the dagger into a brown blob.
  5. The face finished by hand (one face for every frame): the four diamond marks as League's cluster - four white
     points in a diamond (top, two in the middle, bottom) in a pale-blue glow (rows 6-10) - and both eyes 2 x 1 white under the
     brow (the far eye read grey), the face cloth under them.
  6. Calm: PASSES majority passes (pixel_down._majority) that never turn a lit square dark, the face (marks, eyes)
     and the outline kept. A palette cut (k-means over the design's squares, 28-36 colours) flattened the bracers and
     the skin into one shade each, and two passes ate the dagger: not used.
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts")
sys.path.insert(0, SKILL)
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_bard_hd import kmeans  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "malzahar")
RAW = os.path.join(SRC, "codex_grid", "raw", "B-01.png")
OUT = os.path.join(SRC, "hd", "front.png")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "mz_work", "design")
K = (14, 12, 18)
ROWS = 77                     # 35 game px at PPU 2.2
HEAD = 0.36                   # the head's share of the height (hood tip to the scarf's bottom)


def draft():
    os.makedirs(WORK, exist_ok=True)
    rg = os.path.join(WORK, "B-01_rg.png")
    subprocess.run([sys.executable, os.path.join(SKILL, "regrid.py"), RAW, rg], check=True, capture_output=True)
    a = np.array(Image.open(rg).convert("RGBA"))
    clear = a[..., 3] < 128
    pale = a[..., :3].astype(int).min(-1) > 235
    # near-white haze only where it joins the clear background (the diamonds' and eyes' white stay)
    lab_, _n = ndimage.label(clear | pale)
    outside = np.isin(lab_, np.unique(lab_[clear]))
    drop = clear | (pale & outside)
    a[drop] = 0
    a[~drop, 3] = 255
    im = Image.fromarray(a)
    return np.array(im.crop(im.getbbox()))


def cells(a, d, k, pivot):
    """(row, col, ys, xs) for every square of `d` (pixelate's grid of 1 / k draft px through `pivot`) and the draft
    pixels under it."""
    H, W = a.shape[:2]
    c = 1.0 / k
    px, py = pivot
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))
    for r in range(d.shape[0]):
        y0, y1 = (r - ny0) * c + py, (r - ny0 + 1) * c + py
        ys = slice(max(0, int(np.floor(y0))), min(H, int(np.ceil(y1))))
        for col in range(d.shape[1]):
            x0, x1 = (col - nx0) * c + px, (col - nx0 + 1) * c + px
            xs = slice(max(0, int(np.floor(x0))), min(W, int(np.ceil(x1))))
            yield r, col, y0, x0, ys, xs


def glow(a, d, k, pivot=None, box=None):
    """Brightness wins for the marks and the eyes (step 4): in the head's rows (the design) or inside `box` (x0, y0,
    x1, y1 in draft px: round the marks of an action frame)."""
    H, W = a.shape[:2]
    pivot = pivot or (W / 2, H)
    s = a[..., :3].astype(int)
    lit = s.sum(-1)
    white = (a[..., 3] > 0) & (lit > 650)
    blue = (a[..., 3] > 0) & (s[..., 2] > 170) & (lit > 420) & ~white
    if box is not None:
        inside = np.zeros(white.shape, bool)
        inside[max(0, box[1]):box[3], max(0, box[0]):box[2]] = True
        white &= inside
        blue &= inside
    wcol = np.array(a[white][:, :3].mean(0).round(), np.uint8) if white.any() else np.array([255, 255, 255], np.uint8)
    bcol = np.array(a[blue][:, :3].mean(0).round(), np.uint8) if blue.any() else np.array([120, 170, 255], np.uint8)
    for r, col, y0, x0, ys, xs in cells(a, d, k, pivot):
        if box is None and y0 > HEAD * H:
            break
        n = white[ys, xs].size
        if not n:
            continue
        if white[ys, xs].sum() >= 0.25 * n:
            d[r, col, :3], d[r, col, 3] = wcol, 255
        elif blue[ys, xs].sum() >= 0.34 * n:
            d[r, col, :3], d[r, col, 3] = bcol, 255
    return d


GOLDS = np.array([(248, 171, 61), (211, 124, 41), (160, 96, 30)], float)
SHEATH = np.array([(73, 77, 99), (54, 60, 80)], float)


def dagger(a, d, k, pivot=None):
    """The dagger and the buckle (step 4b): gold wins where 30 % of a square is gold in the draft (snapped to three
    golds), the sheath's blue-grey where 40 % is, in the gold's own band - the mean took them for skin and leather."""
    H, W = a.shape[:2]
    pivot = pivot or (W / 2, H)
    s = a[..., :3].astype(int)
    r_, g_, b_ = s[..., 0], s[..., 1], s[..., 2]
    op = a[..., 3] > 0
    gold = op & (r_ > 170) & (g_ > 110) & (b_ < 110) & (r_ - b_ > 90)
    sheath = op & (np.abs(r_ - g_) < 30) & (b_ > r_ + 10) & (b_ < 170) & (r_ > 55) & (r_ < 150)
    gy, gx = np.nonzero(gold)
    if not len(gy):
        return d
    band = np.zeros(op.shape, bool)
    band[max(0, gy.min() - 3):gy.max() + 4, max(0, gx.min() - 3):gx.max() + 4] = True
    sheath &= band
    for r, col, _, _, ys, xs in cells(a, d, k, pivot):
        n = gold[ys, xs].size
        if not n or d[r, col, 3] == 0:
            continue
        for m, pal, th in ((gold, GOLDS, 0.3), (sheath, SHEATH, 0.4)):
            cell = m[ys, xs]
            if cell.sum() >= th * n:
                mean = s[ys, xs][cell].mean(0)
                d[r, col, :3] = pal[((pal - mean) ** 2).sum(1).argmin()].astype(np.uint8)
                break
    return d


# step 5: (row, col) -> colour on the cropped 60 x 77 design; '.' = the hood's magenta
MARKS = ["..n..", ".nWn.", "nWnWn", ".nWn.", "..n.."]
MARK_AT = (6, 30)
FACE = {"W": (245, 250, 251), "n": (33, 145, 235), ".": (228, 14, 101), "c": (117, 1, 57)}
EYES = [(12, 29), (12, 30), (12, 33), (12, 34)]
CLOTH = [(13, c) for c in range(29, 36)] + [(11, 32)]


def face(d):
    r0, c0 = MARK_AT
    for r, row in enumerate(MARKS):
        for c, ch in enumerate(row):
            d[r0 + r, c0 + c, :3], d[r0 + r, c0 + c, 3] = FACE[ch], 255
    for r, c in EYES:
        d[r, c, :3] = FACE["W"]
    for r, c in CLOTH:
        d[r, c, :3] = FACE["c"]
    return d


PASSES = 1


def calm(d):
    op = d[..., 3] > 0
    lit = op & (d[..., :3].astype(int).sum(-1) >= 70)
    keep = np.zeros(op.shape, bool)
    keep[MARK_AT[0]:MARK_AT[0] + len(MARKS), MARK_AT[1]:MARK_AT[1] + len(MARKS[0])] = True
    for r, c in EYES + CLOTH:
        keep[r, c] = True
    for _ in range(PASSES):
        e = PD._majority(d, op, keep | ~lit)
        grew = (e[..., :3].astype(int).sum(-1) < 70) & lit
        e[grew] = d[grew]                   # a lit square never turns outline (dark spread into the arms)
        d = e
    return d


def build():
    a = draft()
    H, W = a.shape[:2]
    px = a[a[..., 3] > 0][:, :3]
    pal = np.vstack([kmeans(px[px.astype(int).sum(1) >= 70], 40).astype(float), [K]])
    k = ROWS / H
    d, _ = PD.pixelate(a, k, (W / 2, H), K, pal=pal)
    d = dagger(a, glow(a, d, k), k)
    im = Image.fromarray(d)
    return calm(face(np.array(im.crop(im.getbbox()))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare with the written design instead of writing")
    a = ap.parse_args()
    d = build()
    if a.check:
        old = np.array(Image.open(OUT).convert("RGBA"))
        print("identical" if old.shape == d.shape and (old == d).all() else "DIFFERENT")
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    Image.fromarray(d).save(OUT)
    print(OUT, d.shape[1], "x", d.shape[0], len(np.unique(d[d[..., 3] > 0][:, :3], axis=0)), "colours")


if __name__ == "__main__":
    main()

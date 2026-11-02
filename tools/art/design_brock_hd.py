#!/usr/bin/env python3
"""Brock's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_brock_hd.py   # writes assets/source/brock/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/brock/codex_picture/brock-picture, 2026-11-02, Codex 2026-11-02/new-chat-2,
brock_picture_done.zip): asked 1536 and 11 px squares; delivered brock-A/B.png (Codex's own cut, 64 x 50 / 46 x 70:
the face a blur of orange, eyes lost) and two rounds of raws, 1254 soft alpha: raw/brock-{A,B}-raw.png (the final
round, flat and clean, both ring eyes clear) drawn on 14 px squares, raw/brock-{A,B}-detail-v1.png (the first round,
closer to the model: horns, lichen, shoulder plates) on 6 / 7 px. A-1 / B-1 = the final raws on 14 (one pixel per
drawn square); A-2 / B-2 = the first round brought to the same height by pixel_down.pixelate (a smaller figure: read
on coarser squares, regrid still follows the drawn 6 / 7 px edges). Colours cut by k-means in Lab (design_varus.kmeans),
alpha 0/255.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "brock", "codex_picture", "brock-picture")
OUT = os.path.join(ROOT, "assets", "source", "brock", "hd")
COLOURS = {"A-1": 32, "A-2": 32, "B-1": 32, "B-2": 32}
FILES = {"A-1": "raw/brock-A-raw.png", "A-2": "raw/brock-A-detail-v1.png", "B-1": "raw/brock-B-raw.png",
         "B-2": "raw/brock-B-detail-v1.png"}
SIZES = {"A-1": 14.0, "A-2": 6.0, "B-1": 14.0, "B-2": 7.0}
# the raws draw each ring eye on half squares (a plus of 4 yellow half squares round a dark red one): read on 14 px
# they came back as yellow smears. Redrawn as a 3x3 plus ring on the face plate - yellow edges, a dark red middle, the
# corners left the plate's orange - centred where the read-back eyes sit (codex-face-half-squares).
EYES = {"A-1": [(37, 17), (41, 17)], "B-1": [(26, 37), (30, 37)]}
SHRINK = {"A-2": 0.38, "B-2": 0.6}   # A-2: 138 -> ~52 rows like A-1; B-2: 137 -> ~82 like B-1


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, FILES[name]))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def clear_eyes(out, eyes):
    """The read-back eye smears (yellow / red squares within 2 of the eyes) painted over in the plate's commonest
    orange, so the new rings stand alone."""
    xs, ys = [e[0] for e in eyes], [e[1] for e in eyes]
    x0, x1, y0, y1 = min(xs) - 2, max(xs) + 3, min(ys) - 2, max(ys) + 3
    box = out[y0:y1, x0:x1]
    rgb = box[..., :3].astype(int)
    op = box[..., 3] > 0
    yel = op & (rgb[..., 0] > 200) & (rgb[..., 1] > 180) & (rgb[..., 2] < 120)
    red = op & (rgb[..., 0] > 100) & (rgb[..., 1] < 60) & (rgb[..., 2] < 60)
    ora = op & ~yel & ~red & (rgb[..., 0] > 180) & (rgb[..., 1] < 170) & (rgb[..., 2] < 90)
    cols, n = np.unique(rgb[ora], axis=0, return_counts=True)
    box[yel | red, :3] = cols[np.argmax(n)]


def eye_colours(out):
    """The picture's brightest yellow and darkest red (the eyes' own colours)."""
    rgb = out[..., :3].astype(int)
    op = out[..., 3] > 0
    yel = op & (rgb[..., 0] > 200) & (rgb[..., 1] > 180) & (rgb[..., 2] < 120)
    red = op & (rgb[..., 0] > 100) & (rgb[..., 1] < 60) & (rgb[..., 2] < 60)
    return rgb[yel][np.argmax(rgb[yel].sum(1))], rgb[red][np.argmin(rgb[red].sum(1))]


def ring(out, cx, cy, y, r):
    """A 3x3 plus ring eye at (cx, cy): yellow `y` on the four edges, red `r` in the middle."""
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        out[cy + dy, cx + dx, :3] = y
    out[cy, cx, :3] = r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", nargs="*", default=[], metavar="NAME=PX", help="another square for a picture")
    a = ap.parse_args()
    SIZES.update({k: float(v) for k, v in (x.split("=") for x in a.size)})
    os.makedirs(lp(OUT), exist_ok=True)
    for name in FILES:
        d = read(name, SIZES[name])
        if name in SHRINK:
            _, pal = V.kmeans(d, 48)   # the drawing's own colours (pixelate's default 64 commonest are all stone greys here)
            d, _ = PD.pixelate(d, SHRINK[name], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d), pal.astype(float))
            op_ = d[..., 3] > 0
            ys, xs = np.nonzero(op_)
            d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        op = d[..., 3] > 0
        idx, pal = V.kmeans(d, COLOURS[name])
        out = np.zeros_like(d)
        out[op, :3] = pal[idx[op]]
        out[op, 3] = 255
        if name in EYES:
            cols = eye_colours(out)
            clear_eyes(out, EYES[name])
            for cx, cy in EYES[name]:
                ring(out, cx, cy, *cols)
        Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(out, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""A Codex design draft (a small pixel picture stretched to a big canvas) -> a game-size design on the game grid.

    python tools/art/draft_to_grid.py DRAFT.png --spec assets/source/morgana/morgana_design.json --out OUT.png [--review DIR]

league_morgana's design (assets/source/morgana/MODEL_PROMPTS.md, "选定"): Codex's four drafts were each a
`blocks` x `blocks` picture stretched to 1254 px (a square every 9.797 px, the soft edges of an image model round
them), the figure two to three times the game's size. The spec (JSON) says how to bring one onto the game grid:
  - "blocks": the draft's own grid; every square takes the majority colour of its middle half (clear of the edges);
  - "palette": {letter: "RRGGBB"} - every square takes the nearest of these colours ('#' is the outline);
  - "offset": [rows, cols] - where the one-in-three dropping starts: in every run of three rows the row most like
    its neighbour goes, then the same for the columns. The proportions stay those of a uniform 2/3 scale while the
    one-square features (eyes, mouth, trim, outline) mostly survive; a colour vote per game pixel let the outline
    swallow the mid-tones and lost the face, uniform sampling dropped features at random;
  - "edits": [[x, y, letters], ...] - hand fixes on the result, a run of letters from (x, y) rightward ('_' keeps a
    pixel);
  - then every transparent pixel touching a coloured (not outline) pixel becomes outline: one closed ring;
  - "pivot_x": the design's column that stands on the canvas's middle column; the lowest row goes on "soles_row"
    of a "canvas" x "canvas" canvas (the native_pose design canvas: 128, soles on row 99).
Writes OUT at 8x (one 8x8 block per game pixel) and, with --review, the 1x design and a 16x grid view.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw

Z = 8


def snap(img, blocks):
    """Each square of the draft's grid -> the majority colour of its middle half (None where mostly clear)."""
    a = np.asarray(img.convert("RGBA")).astype(int)
    p = a.shape[0] / blocks
    out = np.zeros((blocks, blocks, 4), np.uint8)
    for i in range(blocks):
        for j in range(blocks):
            y0, y1 = int(i * p + p * 0.25), int((i + 1) * p - p * 0.25)
            x0, x1 = int(j * p + p * 0.25), int((j + 1) * p - p * 0.25)
            blk = a[y0:y1 + 1, x0:x1 + 1].reshape(-1, 4)
            op = blk[blk[:, 3] > 127]
            if len(op) * 2 < len(blk):
                continue
            keys, cnt = np.unique(op[:, :3] // 6, axis=0, return_counts=True)
            k = keys[cnt.argmax()]
            out[i, j, :3] = op[(op[:, :3] // 6 == k).all(1)][:, :3].mean(0)
            out[i, j, 3] = 255
    return out


def to_index(f, pal):
    """Palette index + 1 per pixel, 0 where transparent."""
    k = np.zeros(f.shape[:2], int)
    on = f[..., 3] > 0
    d = ((f[..., :3][on][:, None, :].astype(float) - pal[None]) ** 2).sum(-1)
    k[on] = d.argmin(1) + 1
    return k


def drop_one_in_three(k, axis):
    """In every run of three lines drop the one that differs least from a kept neighbour."""
    n = k.shape[axis]
    lines = [k[i] if axis == 0 else k[:, i] for i in range(n)]
    drop = []
    for g0 in range(0, n - 2, 3):
        best, bi = None, None
        for i in range(g0, g0 + 3):
            nb = [j for j in (i - 1, i + 1) if 0 <= j < n and j not in drop]
            diff = min((lines[i] != lines[j]).sum() for j in nb) if nb else 0
            if best is None or diff < best:
                best, bi = diff, i
        drop.append(bi)
    return [i for i in range(n) if i not in drop]


def grid_view(f, path, z=16):
    im = Image.fromarray(f, "RGBA")
    base = Image.new("RGBA", im.size, (92, 98, 86, 255))
    base.alpha_composite(im)
    big = base.resize((im.width * z, im.height * z), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for x in range(0, big.width, z):
        d.line([x, 0, x, big.height], fill=(70, 76, 66))
    for y in range(0, big.height, z):
        d.line([0, y, big.width, y], fill=(70, 76, 66))
    big.save(path)


def build(draft, spec):
    letters = list(spec["palette"])
    pal = np.array([[int(spec["palette"][c][i:i + 2], 16) for i in (0, 2, 4)] for c in letters], float)
    b = snap(Image.open(draft), spec["blocks"])
    ys, xs = np.nonzero(b[..., 3] > 0)
    b = b[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = to_index(b, pal)
    oy, ox = spec.get("offset", [0, 0])
    k = k[oy:]
    k = k[drop_one_in_three(k, 0)]
    k = k[:, ox:]
    k = k[:, drop_one_in_three(k, 1)]
    for x, y, run in spec.get("edits", []):
        for i, c in enumerate(run):
            if c != "_":
                k[y, x + i] = 0 if c == "." else letters.index(c) + 1
    out_i = letters.index("#") + 1
    col = (k > 0) & (k != out_i)
    ring = np.zeros_like(col)
    ring[1:] |= col[:-1]; ring[:-1] |= col[1:]; ring[:, 1:] |= col[:, :-1]; ring[:, :-1] |= col[:, 1:]
    k[ring & (k == 0)] = out_i
    f = np.zeros(k.shape + (4,), np.uint8)
    on = k > 0
    f[on, :3] = pal[k[on] - 1].astype(np.uint8)
    f[on, 3] = 255
    return f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--review")
    a = ap.parse_args()
    with open(a.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    f = build(a.draft, spec)
    n = spec.get("canvas", 128)
    canvas = np.zeros((n, n, 4), np.uint8)
    x0 = n // 2 - spec["pivot_x"]
    y0 = spec.get("soles_row", 99) - (f.shape[0] - 1)
    canvas[y0:y0 + f.shape[0], x0:x0 + f.shape[1]] = f
    Image.fromarray(canvas, "RGBA").resize((n * Z, n * Z), Image.NEAREST).save(a.out)
    colours = len(np.unique(f[f[..., 3] > 0][:, :3], axis=0))
    print(f"{a.out}: design {f.shape[1]}x{f.shape[0]}, {colours} colours, rows {y0}-{y0 + f.shape[0] - 1} of the canvas")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Image.fromarray(f, "RGBA").save(os.path.join(a.review, "design_1x.png"))
        grid_view(f, os.path.join(a.review, "design_16x.png"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Quinn's PPU 2.0 redraws (tools/art/pack_quinn_grid.py) read back on their own grids, one palette, cut to 75 rows.

    python tools/art/design_quinn_grid.py   # writes assets/source/quinn/hd2/grid{A1,A2,B}.png (+ _8x), the cuts
                                            # grid{A1,A2}_cut.png and grid_review.png (beside the PPU 1.3 design)

The delivery (assets/source/quinn/codex_grid/quinn-grid, 2026-10-19, Codex new-chat-4): asked 13-px squares, the idle
75 rows crest to soles and the ride 71 rows; Codex's image_gen drew A-1 on ~12-px squares (91 rows), A-2 on ~11 (96),
the ride (raw/Bfix) on ~14 (72), and its own 1x readbacks squeezed each into the asked box by block votes - the face
and the crossbow came back as mush (the art-spec's "never shrink a bigger drawing"). Here regrid.py reads each raw
picture one pixel per drawn square, the colours of all three are cut together by k-means in Lab (design_varus.kmeans,
the near-black outline shades merged), alpha 0/255; the idles are cut to ROWS rows by whole rows and columns
(design_rell_cut.even_cut, never the face's rows and columns: the eyes, nose and mouth stay as drawn; the head,
about a third of her height as drawn, stays a third - the user's pick for the 1.3 design), the ride is kept as drawn (72 rows: PPU 2.0 already).
The user picked A-1; its face is then redrawn on the grid (FACE): Codex drew the eyes, the brows and the lips on half
squares, and read back the near eye came out a grey square beside an amber smear and the lips a red slash down the jaw
line (「脸部给我弄好看点」「现在有点奇怪」) - now each eye a white square, a dark pupil and amber under it, the lashes
apart over the nose, a blush, a small mouth inside the face and a rounder jaw; the ride's face (RIDE) the same way, one
face in every frame. The results are the designs, assets/source/quinn/hd/idle.png and hd/ride.png (the PPU 1.3 ones
kept in hd/ppu13/).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_rell_cut as RC  # noqa: E402
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402
from design_quinn_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "quinn", "codex_grid", "quinn-grid", "raw")
OUT = os.path.join(ROOT, "assets", "source", "quinn", "hd2")
OLD = os.path.join(ROOT, "assets", "source", "quinn", "hd", "ppu13", "idle.png")
IDLE = os.path.join(ROOT, "assets", "source", "quinn", "hd", "idle.png")
RIDE_OUT = os.path.join(ROOT, "assets", "source", "quinn", "hd", "ride.png")
COLOURS = 40
ROWS = 75            # 38 game px x PPU 2.0 (the 1.3 design's 49 rows x 2.0 / 1.3)
INK = (0x09, 0x00, 0x13)
FILES = {"A1": ("A1.png", None), "A2": ("A2.png", None), "B": ("Bfix.png", None)}
# A-1's face redrawn, columns 24-32 from row 11 down ('=' keeps the cut's square): K outline, c skin, s blush, y and A
# the mouth, W the eye white, o and i the iris (dark over amber)
FACE_AT = (24, 11)
FACE = ["= = c = = = = = =",
        "= = = = = c = = =",
        "= = = = = c K K K",
        "= s W K o c W K K",
        "= = c i i c c i K",
        "= = s s c c c c K",
        "= = c c c c c c K",
        "= = c c c y A c K",
        "= = c c c c c K K",
        "= = = c c c K K =",
        "= = = = = = = = ="]
# the ride's face, columns 58-65 from row 11 down: the same eyes, lashes, blush and mouth
RIDE_AT = (58, 11)
RIDE = ["= = = = = = = =",
        "= = = K c K = =",
        "= = = = c K K =",
        "= W K o c W K =",
        "= c i i c c i =",
        "= s s c c c = =",
        "= = = = y A = =",
        "= = = = = = = =",
        "= = = = = = = ="]
FACE_COLOURS = dict(K=INK, c=(0xfc, 0xd1, 0xb3), s=(0xee, 0x97, 0x78), y=(0xc9, 0x5e, 0x4f), A=(0x9a, 0x14, 0x28),
                    W=(0xfb, 0xf7, 0xf2), o=(0x51, 0x24, 0x1c), i=(0xc9, 0x7d, 0x24))


def read(name):
    fname, size = FILES[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, fname))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def save(name, d, z=8):
    os.makedirs(lp(OUT), exist_ok=True)
    Image.fromarray(d).save(lp(os.path.join(OUT, f"grid{name}.png")))
    Image.fromarray(np.repeat(np.repeat(d, z, 0), z, 1)).save(lp(os.path.join(OUT, f"grid{name}_8x.png")))
    print(name, d.shape[1], "x", d.shape[0])


def face(d):
    """Her face's rows and columns (the skin of the upper half: brows to chin, cheek to cheek) - never cut, so the eyes,
    the nose and the mouth stay as drawn; everything else gives rows and columns evenly."""
    c = d[..., :3].astype(int)
    # peach skin (#FCD1B3 / #EE9778): red high, green within 60 of blue (the pale golds of the visor and the crossbow are
    # far greener than blue)
    skin = (d[..., 3] > 0) & (c[..., 0] > 200) & (c[..., 2] > 90) & (c[..., 1] - c[..., 2] < 60) & (c[..., 0] - c[..., 2] > 40)
    skin[int(d.shape[0] * 0.5):] = False
    rows = np.nonzero(skin.sum(1) >= 2)[0]
    cols = np.nonzero(skin[rows.min():rows.max() + 1].sum(0) >= 2)[0]
    return list(range(int(rows.min()), int(rows.max()) + 1)), list(range(int(cols.min()), int(cols.max()) + 1))


def paint(d, at, rows):
    """A copy of d with the squares of rows ('=' keeps one) painted from at (column, row) on."""
    d = d.copy()
    x0, y0 = at
    for j, row in enumerate(rows):
        for i, ch in enumerate(row.split()):
            if ch != "=":
                d[y0 + j, x0 + i] = (*FACE_COLOURS[ch], 255)
    return d


def main():
    parts = {k: read(k) for k in FILES}
    h = max(p.shape[0] for p in parts.values())
    both = np.zeros((h, sum(p.shape[1] for p in parts.values()), 4), np.uint8)
    x = 0
    for p in parts.values():
        both[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    pal = pal.copy()
    pal[pal.astype(int).sum(1) < 70] = INK                     # the outline's shades are one near-black
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    x = 0
    done = {}
    for name, p in parts.items():
        part = out[:p.shape[0], x:x + p.shape[1]]
        x += p.shape[1]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))].copy()
        done[name] = part
        save(name, part)
    cuts = {}
    for name in ("A1", "A2"):
        d = done[name]
        fr, fc = face(d)
        cols = round(d.shape[1] * ROWS / d.shape[0])
        cuts[name] = RC.even_cut(d, ROWS, cols, (fr, fc))
        print(name, "face rows", fr[0], "-", fr[-1], "columns", fc[0], "-", fc[-1], "kept whole")
    for name, d in cuts.items():
        save(name + "_cut", d)
    idle = paint(cuts["A1"], FACE_AT, FACE)
    ride = paint(done["B"], RIDE_AT, RIDE)
    for path, d in ((IDLE, idle), (RIDE_OUT, ride)):
        Image.fromarray(d).save(lp(path))
        print("design", path, d.shape[1], "x", d.shape[0])
    # the review: the 1.3 design and each take at the same game size (4 screen px a game px), and the takes at 6x
    old = np.asarray(Image.open(lp(OLD)).convert("RGBA"))
    game = [("PPU 1.3", old, 3), ("A-1 cut", cuts["A1"], 2), ("A-1 face redrawn", idle, 2), ("A-2 cut", cuts["A2"], 2),
            ("ride", ride, 2)]
    big = [("A-1 cut", cuts["A1"], 6), ("A-1 face redrawn", idle, 6), ("ride", ride, 5)]
    rows_ = [game, big]
    W = max(sum(d.shape[1] * z + 24 for _, d, z in r) for r in rows_) + 24
    Hs = [max(d.shape[0] * z for _, d, z in r) + 40 for r in rows_]
    can = Image.new("RGBA", (W, sum(Hs)), (104, 112, 72, 255))
    dr = ImageDraw.Draw(can)
    y = 0
    for r, H in zip(rows_, Hs):
        x = 24
        for label, d, z in r:
            im = Image.fromarray(np.repeat(np.repeat(d, z, 0), z, 1))
            can.alpha_composite(im, (x, y + H - im.height - 6))
            dr.text((x, y + 6), f"{label} {d.shape[1]}x{d.shape[0]}", fill=(255, 255, 255, 255))
            x += im.width + 24
        y += H
    can.convert("RGB").save(lp(os.path.join(OUT, "grid_review.png")))
    print("review", can.size)


if __name__ == "__main__":
    main()

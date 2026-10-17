#!/usr/bin/env python3
"""Swain's step-1 takes read back on their own grids and brought to the picked game size (PPU 1.5: 60 rows from the
hair's top to the soles, A and B alike - B's wings follow at the same factor), two ways each, with review sheets.

    python tools/art/design_swain_cut.py [--out dist/swain_packs]

Step 1 (assets/source/swain/codex_model, 2026-10-17, Codex new-chat-2): swain-model-A-1/A-2/B-1/B-2 on 1254 squares
(asked 1024), squares 10 / 12 / 10 / 11 px (regrid's measure; asked 12 on 1024 = 14.7 on 1254), so A-1 101, A-2 80,
B-1 105 (wings included), B-2 93 rows - all taller than asked. Each is read back on its own grid (regrid.py, alpha 0/255
at 128), its colours cut to COLOURS by k-means (design_varus.kmeans), then brought to 60 rows of body (B: its hair's top
row found by the silver hair) two ways:
  cut - design_rell_cut.even_cut: whole rows / columns dropped one per equal window, never the face's rows and columns
        (the pale skin in the head) nor two neighbours;
  px  - pixel_down.pixelate (area vote; softer).
Writes assets/source/swain/hd/model<take>{,_cut,_px}.png and <out>/swain_model_review.png (the takes at game size beside
the mids, Pantheon and Darius) + swain_model_takes.png (every cut at 6x).
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
import design_orianna_cut as OC  # noqa: E402
import design_rell_cut as RC  # noqa: E402
import design_varus as V  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
import review_swain_size as RS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "swain")
COLOURS = 40
PPU = 1.5
ROWS = 60
TAKES = {"A-1": 10.0, "A-2": 12.0, "B-1": 10.0, "B-2": 11.0}
NEIGHBOURS = ["vladimir", "viktor", "syndra", "orianna", "pantheon", "darius"]
BG = (196, 200, 190, 255)
FACE = 0.09            # the face rows kept whole, a share of the body's height


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read(take, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"swain-model-{take}.png"))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    d = d[np.ix_(np.any(op, 1), np.any(op, 0))].copy()
    op = d[..., 3] >= 128
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def skin(d):
    r, g, b = (d[..., i].astype(int) for i in range(3))
    return (d[..., 3] > 0) & (r > 150) & (r - b > 35) & (r > g) & (g > b)


def silver(d):
    c = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (c.min(-1) > 150) & (c.max(-1) - c.min(-1) < 40)


def hair_top(d):
    """The first row with silver hair (B's wings reach above it)."""
    return int(np.nonzero(silver(d).any(1))[0].min())


def face_lines(d, top):
    """His face: from the first pale-skin row under the hair's top, FACE x the body's rows down; the skin's columns."""
    sk = skin(d)
    sk[:top] = False
    sk[top + (d.shape[0] - top) // 3:] = False
    y0 = int(np.nonzero(sk.any(1))[0].min())
    rows = list(range(y0, y0 + max(4, round(FACE * (d.shape[0] - top)))))
    cols = sorted(set(np.nonzero(sk[rows[0]:rows[-1] + 1].any(0))[0].tolist()))
    return rows, cols


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "swain_packs"))
    a = ap.parse_args()
    cells, closeups = [], []
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    for take, size in TAKES.items():
        d = read(take, size)
        top = hair_top(d)
        k = ROWS / (d.shape[0] - top)
        rows, cols = round(d.shape[0] * k), round(d.shape[1] * k)
        fr, fc = face_lines(d, top)
        cut = RC.even_cut(d, rows, cols, (fr, fc))
        px, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        px = OC.crop(px)
        tag = take.replace("-", "")
        for name, im in ((f"model{tag}", d), (f"model{tag}_cut", cut), (f"model{tag}_px", px)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"{name}.png")))
        print(take, "read", d.shape[1], "x", d.shape[0], "hair top", top, "-> cut", cut.shape[1], "x", cut.shape[0],
              "px", px.shape[1], "x", px.shape[0], "face rows", fr[0], "-", fr[-1])
        for label, im in ((f"{take} cut", cut), (f"{take} px", px)):
            cells.append((label, f"{im.shape[1] / PPU:.0f}x{im.shape[0] / PPU:.0f}", RS.shown(Image.fromarray(im), PPU, 3)))
            closeups.append((label, Image.fromarray(np.repeat(np.repeat(im, 6, 0), 6, 1))))
    for hero in NEIGHBOURS:
        im, p = RS.frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", RS.shown(im, p, 3)))
    for fname, items, top in (("swain_model_review.png", cells, 34), ("swain_model_takes.png", closeups, 20)):
        gap = 16
        W = sum(c[-1].width for c in items) + gap * (len(items) + 1)
        H = max(c[-1].height for c in items) + top + gap
        can = Image.new("RGBA", (W, H), BG)
        dr = ImageDraw.Draw(can)
        x = gap
        for c in items:
            im = c[-1]
            can.alpha_composite(im, (x, H - gap - im.height))
            dr.text((x, 4), c[0], fill=(30, 30, 30, 255))
            if len(c) == 3:
                dr.text((x, 18), c[1], fill=(30, 30, 30, 255))
            x += im.width + gap
        dr.line([(0, H - gap), (W, H - gap)], fill=(120, 120, 120, 255))
        os.makedirs(lp(a.out), exist_ok=True)
        can.convert("RGB").save(lp(os.path.join(a.out, fname)))
        print(fname, can.size)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Jarvan IV's step-1 takes read back on their own grids and brought to the picked game size (PPU 1.5: 60 rows from the
helmet's top to the soles = 40 game rows, the lance above that), two ways each, with review sheets.

    python tools/art/design_jarvaniv_cut.py [--out dist/jarvaniv_packs]

Step 1 (assets/source/jarvaniv/codex_model, 2026-10-17, Codex new-chat-6) on 1254 squares (asked 1024): the corrected
takes jarvaniv-model-A-1 (squares 12 px by regrid, 88 rows with the lance, body 72 from row 16) and A-2 (13.5 px, 83
rows, body 68 from row 15); Codex's first, finer round initial-A-1 (10 px, body 95) and initial-A-2 (8 px, body 131) is
kept as sent (cut to 60 rows they come out squashed, so they are not offered). Each is read back on its own grid (regrid.py, alpha 0/255 at 128), its colours cut to
COLOURS by k-means (design_varus.kmeans), then brought to 60 body rows two ways:
  cut - design_rell_cut.even_cut: whole rows / columns dropped one per equal window, never the face's lines (skin and
        the eyes in the head) nor the lance's shaft columns nor two neighbours; blue gems and the outline cost more;
  px  - pixel_down.pixelate (area vote; softer).
Writes assets/source/jarvaniv/hd/model<take>{,_cut,_px}.png and <out>/jarvaniv_model_review.png (the takes at game size
beside the pack's heroes) + jarvaniv_model_takes.png (every cut at 6x).
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
from design_jarvaniv_hd import lp  # noqa: E402,F811

SRC = os.path.join(ROOT, "assets", "source", "jarvaniv")
COLOURS = 40
PPU = 1.5
BODY = 60   # helmet top to soles (40 game rows)
# file stem -> (square px, body top row in the read-back)
TAKES = {"jarvaniv-model-A-1": (12.0, 16), "jarvaniv-model-A-2": (13.5, 15)}
# Codex's first round, cut the same way, came out squashed (initial-A-1 95 -> 60 body rows, initial-A-2 131 -> 60 broke
# the body round the kept face): not offered; add "initial-A-1": (10.0, 23), "initial-A-2": (8.0, 24) to see them
NEIGHBOURS = ["garen", "pantheon", "xinzhao", "vi", "leesin", "swain"]
BG = (196, 200, 190, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read(take, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"{take}.png"))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    d = d[np.ix_(np.any(op, 1), np.any(op, 0))].copy()
    op = d[..., 3] >= 128
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def face_lines(d, top):
    """His face (skin and the eyes inside it: rows and columns) in the head - helmet top to 25% of the body below it -
    and the lance's shaft columns (opaque in most rows of the right third)."""
    h, w = d.shape[:2]
    rgb = d[..., :3].astype(int)
    on = d[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    skin = on & (r > 170) & (g > 110) & (b > 80) & (r - b > 40) & (r - g < 80) & (g - b > 10)
    m = skin.copy()
    m[:top] = False
    m[top + int((h - top) * 0.25):] = False
    m[:, int(w * 0.62):] = False
    rows = sorted(set(np.nonzero(m.any(1))[0].tolist()))
    cols = set(np.nonzero(m.any(0))[0].tolist())
    if rows:   # the eyes: dark or white squares between the face's own columns
        cols |= set(range(min(cols), max(cols) + 1))
    shaft = [x for x in range(int(w * 0.62), w) if on[top:, x].mean() > 0.6]
    return rows, sorted(cols | set(shaft))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "jarvaniv_packs"))
    a = ap.parse_args()
    cells, closeups = [], []
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    for take, (size, top) in TAKES.items():
        d = read(take, size)
        k = BODY / (d.shape[0] - top)
        rows, cols = round(d.shape[0] * k), round(d.shape[1] * k)
        fr, fc = face_lines(d, top)
        cut = RC.even_cut(d, rows, cols, (fr, fc))
        px, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        px = OC.crop(px)
        tag = take.replace("jarvaniv-model-", "").replace("initial-", "i").replace("-", "")
        for name, im in ((f"model{tag}", d), (f"model{tag}_cut", cut), (f"model{tag}_px", px)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"{name}.png")))
        print(take, "read", d.shape[1], "x", d.shape[0], "-> cut", cut.shape[1], "x", cut.shape[0],
              "px", px.shape[1], "x", px.shape[0], "face rows", fr, "cols", fc)
        for label, im in ((f"{tag} cut", cut), (f"{tag} px", px)):
            cells.append((label, f"{im.shape[1] / PPU:.0f}x{im.shape[0] / PPU:.0f}", RS.shown(Image.fromarray(im), PPU, 3)))
            closeups.append((label, Image.fromarray(np.repeat(np.repeat(im, 6, 0), 6, 1))))
    for hero in NEIGHBOURS:
        im, p = RS.frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", RS.shown(im, p, 3)))
    for fname, items, top in (("jarvaniv_model_review.png", cells, 34), ("jarvaniv_model_takes.png", closeups, 20)):
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

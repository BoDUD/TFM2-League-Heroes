#!/usr/bin/env python3
"""Maokai's step-1 takes read back on their own grids and brought to the picked game size (PPU 1.5: A 60 rows from the
crown to the feet = 40 game rows, C 18 = 12), three ways each, with review sheets.

    python tools/art/design_maokai_cut.py [--out dist/maokai_packs]

Step 1 (assets/source/maokai/codex_model, 2026-10-18, Codex new-chat): maokai-model-A-1/A-2/C-1/C-2 on 1254 squares
(asked 1024), squares all 10 px (regrid's measure, checked at 4x), so A-1 77 rows, A-2 80, C-1 38, C-2 23 - all taller
than asked. Each is read back on its own grid (regrid.py, alpha 0/255 at 128), its colours cut to COLOURS by k-means
(design_varus.kmeans), then brought to ROWS two ways:
  cut - design_rell_cut.even_cut: whole rows / columns dropped one per equal window, never the eyes' lines (the trunk
        face's and the fist face's glowing blue) nor two neighbours (design_orianna_cut.weights);
  px  - pixel_down.pixelate (area vote; softer);
  dp  - design_akali.dp_keep on rows, then columns: the lines whose loss costs least (a deleted line's difference from
        its nearer-looking neighbour, glowing blue x10, outline x3), never two neighbours.
The pack asked for PPU 1.2 (48 rows); the user saw it muddy (「太模糊了 PPU调整一下像素」, 2026-10-18) -> PPU 1.5: the
80-row A-2 cut to 60 rows keeps the faces, the lantern's cord and the outline (the design = modelA2_dp, C = modelC2_dp).
Writes assets/source/maokai/hd/model<take>{,_cut,_px}.png and <out>/maokai_model_review.png (the takes at game size
beside the pack's big supports) + maokai_model_takes.png (every cut at 6x).
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
import design_akali as DA  # noqa: E402
import design_orianna_cut as OC  # noqa: E402
import design_rell_cut as RC  # noqa: E402
import design_varus as V  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
import review_swain_size as RS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "maokai")
COLOURS = 40
PPU = 1.5
ROWS = {"A": 60, "C": 18}
TAKES = {"A-1": 10.0, "A-2": 10.0, "C-1": 10.0, "C-2": 10.0}
NEIGHBOURS = ["tahmkench", "braum", "nasus", "malphite", "alistar"]
BG = (196, 200, 190, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read(take, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"maokai-model-{take}.png"))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    d = d[np.ix_(np.any(op, 1), np.any(op, 0))].copy()
    op = d[..., 3] >= 128
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def face_lines(d):
    """The glowing blue below the lantern (rows from 30% down): every row of it (the trunk face's eyes, the fist face's
    eyes and grin, the sapling's eye) and the columns of the trunk face's eyes (right half, rows 30-65%) - the grin's
    long band keeps its rows only. The sapling (C) keeps its eye's rows and columns."""
    h, w = d.shape[:2]
    rgb = d[..., :3].astype(int)
    on = d[..., 3] > 0
    blue = on & (rgb[..., 2] > 200) & (rgb[..., 1] > 140) & (rgb[..., 0] < 140)
    if h < 40:
        return sorted(set(np.nonzero(blue.any(1))[0].tolist())), sorted(set(np.nonzero(blue.any(0))[0].tolist()))
    m = blue.copy()
    m[:int(h * 0.3)] = False
    rows = sorted(set(np.nonzero(m.any(1))[0].tolist()))
    eyes = m.copy()
    eyes[int(h * 0.65):] = False
    eyes[:, :w // 2] = False
    cols = sorted(set(np.nonzero(eyes.any(0))[0].tolist()))
    return rows, cols


def dp_cut(d, rows, cols):
    rgb = d[..., :3].astype(int)
    on = d[..., 3] > 0
    blue = on & (rgb[..., 2] > 200) & (rgb[..., 1] > 140) & (rgb[..., 0] < 140)
    w = np.where(on, 1.0, 0.3)
    w[on & (rgb.max(-1) < 45)] = 3.0
    w[blue] = 10.0
    key = (rgb[..., 0] * 65536 + rgb[..., 1] * 256 + rgb[..., 2] + on * (1 << 30)).astype(np.int64)
    keep_r, _ = DA.dp_keep([key[i] for i in range(d.shape[0])], [w[i] for i in range(d.shape[0])], rows)
    d, key, w = d[keep_r], key[keep_r], w[keep_r]
    keep_c, _ = DA.dp_keep([key[:, j] for j in range(d.shape[1])], [w[:, j] for j in range(d.shape[1])], cols)
    return d[:, keep_c]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "maokai_packs"))
    a = ap.parse_args()
    cells, closeups = [], []
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    for take, size in TAKES.items():
        d = read(take, size)
        k = ROWS[take[0]] / d.shape[0]
        rows, cols = round(d.shape[0] * k), round(d.shape[1] * k)
        fr, fc = face_lines(d)
        cut = RC.even_cut(d, rows, cols, (fr, fc))
        px, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        px = OC.crop(px)
        dp = dp_cut(d, rows, cols)
        tag = take.replace("-", "")
        for name, im in ((f"model{tag}", d), (f"model{tag}_cut", cut), (f"model{tag}_px", px), (f"model{tag}_dp", dp)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"{name}.png")))
        print(take, "read", d.shape[1], "x", d.shape[0], "-> cut", cut.shape[1], "x", cut.shape[0],
              "px", px.shape[1], "x", px.shape[0], "face rows", fr, "cols", fc)
        for label, im in ((f"{take} cut", cut), (f"{take} px", px), (f"{take} dp", dp)):
            cells.append((label, f"{im.shape[1] / PPU:.0f}x{im.shape[0] / PPU:.0f}", RS.shown(Image.fromarray(im), PPU, 3)))
            closeups.append((label, Image.fromarray(np.repeat(np.repeat(im, 6, 0), 6, 1))))
    for hero in NEIGHBOURS:
        im, p = RS.frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", RS.shown(im, p, 3)))
    for fname, items, top in (("maokai_model_review.png", cells, 34), ("maokai_model_takes.png", closeups, 20)):
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

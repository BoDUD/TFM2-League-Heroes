#!/usr/bin/env python3
"""Gangplank's step-1 take read back on its own grid and brought to the picked game size (PPU 1.2: 50 rows from the
hat's top to the soles = 42 game rows), two ways, with review sheets.

    python tools/art/design_gangplank_cut.py [--out dist/gangplank_packs]

Step 1 (assets/source/gangplank/codex_model, 2026-10-18, Codex new-chat-3) on 1254 squares (asked 1024, 14 px squares,
50 rows): A-1 has ~13.4 px columns and ~12 px rows (regrid's own boundaries, row heights mostly 11-14), read back
81 x 78; A-2 76 x 73 at 14.3, simpler and its face darker - A-1 is the take (closest to the picked picture; the user
left the strips to me: 「动作帧参考塔姆那种做法 不用依赖codex 然后做完了你自己review 完美了再喊我review」). Read back
(regrid.py, alpha 0/255 at 128), colours cut to COLOURS by k-means (design_varus.kmeans), then brought to 50 rows:
  cut - design_rell_cut.even_cut: whole rows / columns dropped one per equal window, never the face's lines (FACE: the
        brows, the eyes, the nose and the moustache rows; the face's columns) nor two neighbours;
  px  - pixel_down.pixelate (area vote; softer).
Writes assets/source/gangplank/hd/modelA1{,_cut,_px}.png and <out>/gangplank_model_review.png (at game size beside the
pack's big men) + gangplank_model_takes.png (each at 6x).
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
from design_gangplank_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gangplank")
COLOURS = 40
PPU = 1.2
BODY = 50   # hat top to soles (42 game rows)
# file stem -> (square px, (face rows), (face cols)) in the read-back
TAKES = {"gangplank-model-A-1": (13.4, (11, 18), (31, 41))}
NEIGHBOURS = ["missfortune", "swain", "nasus", "darius", "olaf", "tahmkench"]
BG = (196, 200, 190, 255)


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "gangplank_packs"))
    a = ap.parse_args()
    cells, closeups = [], []
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    for take, (size, fr, fc) in TAKES.items():
        d = read(take, size)
        k = BODY / d.shape[0]
        rows, cols = round(d.shape[0] * k), round(d.shape[1] * k)
        cut = RC.even_cut(d, rows, cols, (list(range(fr[0], fr[1] + 1)), list(range(fc[0], fc[1] + 1))))
        px, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        px = OC.crop(px)
        tag = take.replace("gangplank-model-", "").replace("-", "")
        for name, im in ((f"model{tag}", d), (f"model{tag}_cut", cut), (f"model{tag}_px", px)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"{name}.png")))
        print(take, "read", d.shape[1], "x", d.shape[0], "-> cut", cut.shape[1], "x", cut.shape[0],
              "px", px.shape[1], "x", px.shape[0])
        for label, im in ((f"{tag} cut", cut), (f"{tag} px", px)):
            cells.append((label, f"{im.shape[1] / PPU:.0f}x{im.shape[0] / PPU:.0f}", RS.shown(Image.fromarray(im), PPU, 4)))
            closeups.append((label, Image.fromarray(np.repeat(np.repeat(im, 6, 0), 6, 1))))
    for hero in NEIGHBOURS:
        im, p = RS.frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", RS.shown(im, p, 4)))
    for fname, items, top in (("gangplank_model_review.png", cells, 34), ("gangplank_model_takes.png", closeups, 20)):
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

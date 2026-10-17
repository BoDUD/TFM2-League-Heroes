#!/usr/bin/env python3
"""Rell's step-1 takes read back on their own grids and brought to the picked game size (PPU 1.5: A 66 rows hair top to
hooves, B 60 rows hair top to soles), two ways each, with a review sheet for the user's pick.

    python tools/art/design_rell_cut.py [--out dist/rell_packs]

Step 1 (assets/source/rell/codex_model, 2026-10-16, Codex new-chat-5): rell-model-A-1/A-2/B-1/B-2 on 1254 squares
(asked 1024), squares 11 / 12 / 10 / 13 px (regrid's measure; asked 12), so A-1 93, A-2 86, B-1 120, B-2 82 rows - all
taller than asked. Each is read back on its own grid (regrid.py, alpha 0/255 at 128), its colours cut to COLOURS by
k-means (design_varus.kmeans), then brought to the target rows two ways:
  cut - design_orianna_cut.even_cut: whole rows / columns dropped one per equal window, never the face's rows (the skin
        squares in the head) nor two neighbours;
  px  - pixel_down.pixelate (area vote; softer).
Writes assets/source/rell/hd/model<take>{,_cut,_px}.png and <out>/rell_model_review.png (the takes at game size beside
the tank supports, Hecarim and Darius) + rell_model_takes.png (every cut at 6x).
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
import design_varus as V  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
import review_rell_size as RS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rell")
COLOURS = 40
PPU = 1.5
ROWS = {"A": 66, "B": 60}
TAKES = {"A-1": 11.0, "A-2": 12.0, "B-1": 10.0, "B-2": 13.0}
NEIGHBOURS = ["alistar", "braum", "leona", "hecarim", "darius"]
BG = (196, 200, 190, 255)
FACE = 0.09            # the face rows kept whole, a share of the take's height


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read(take, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"rell-model-{take}.png"))).convert("RGBA")).copy()
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
    """Her face: from the first row with dark brown skin squares, FACE x the height rows down; the skin's columns there
    (the eyes, brows and mouth live in them)."""
    top = d.shape[0] // 3
    r, g, b = (d[:top, :, i].astype(int) for i in range(3))
    skin = (d[:top, :, 3] > 0) & (r > 70) & (r - b > 35) & (r > g) & (g > b) & (r < 200) & (g < 140)
    y0 = int(np.nonzero(skin.any(1))[0].min())
    rows = list(range(y0, y0 + max(4, round(FACE * d.shape[0]))))
    cols = sorted(set(np.nonzero(skin[rows[0]:rows[-1] + 1].any(0))[0].tolist()))
    return rows, cols


def even_cut(d, rows, cols, keep, index=False):
    """design_orianna_cut.even_cut with her face kept and no eye-colour rule: whole lines dropped one per equal window
    (the cheapest by design_orianna_cut.weights), never a kept line nor a neighbour of one just dropped; a window that is
    all face gives its line to the nearest free one outside the face. index: also return the kept rows and columns
    (league_anivia's rig maps its part outlines through them)."""
    wt = OC.weights(d)

    def drop(a, w, n_keep, hard):
        n = a.shape[0]
        k = n - n_keep
        code = a.astype(np.int64) @ np.array([1 << 24, 1 << 16, 1 << 8, 1], np.int64)

        def cost(j):
            c = [float(((code[j] != code[m]) * np.maximum(w[j], w[m])).sum()) for m in (j - 1, j + 1) if 0 <= m < n]
            return min(c) if c else 0.0
        gone = []
        edges = np.linspace(0, n, k + 1)
        for i in range(k):
            lo, hi = int(round(edges[i])), int(round(edges[i + 1]))
            ok = lambda j: j not in hard and j not in gone and (j - 1) not in gone and (j + 1) not in gone
            cand = [j for j in range(max(lo, 1), min(hi, n - 1)) if ok(j)]
            if not cand:
                free = [j for j in range(1, n - 1) if ok(j)] or [j for j in range(n) if j not in hard and j not in gone]
                mid = (lo + hi) / 2
                cand = sorted(free, key=lambda j: abs(j - mid))[:3]
            gone.append(min(cand, key=cost))
        return [j for j in range(n) if j not in gone]

    keep_r = drop(d, wt, rows, set(keep[0]))
    sub = d[keep_r]
    keep_c = drop(sub.transpose(1, 0, 2), wt[keep_r].T, cols, set(keep[1]))
    if index:
        return sub[:, keep_c], keep_r, keep_c
    return sub[:, keep_c]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "rell_packs"))
    a = ap.parse_args()
    cells, closeups = [], []
    for take, size in TAKES.items():
        d = read(take, size)
        form = take[0]
        rows = ROWS[form]
        k = rows / d.shape[0]
        cols = round(d.shape[1] * k)
        fr, fc = face_lines(d)
        cut = even_cut(d, rows, cols, (fr, fc))
        px, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        px = OC.crop(px)
        tag = take.replace("-", "")
        for name, im in ((f"model{tag}", d), (f"model{tag}_cut", cut), (f"model{tag}_px", px)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"{name}.png")))
        print(take, "read", d.shape[1], "x", d.shape[0], "-> cut", cut.shape[1], "x", cut.shape[0],
              "px", px.shape[1], "x", px.shape[0], "face rows", len(fr))
        for label, im in ((f"{take} cut", cut), (f"{take} px", px)):
            cells.append((label, f"{im.shape[1] / PPU:.0f}x{im.shape[0] / PPU:.0f}", RS.shown(Image.fromarray(im), PPU, 3)))
            closeups.append((label, Image.fromarray(np.repeat(np.repeat(im, 6, 0), 6, 1))))
    for hero in NEIGHBOURS:
        im, p = RS.frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", RS.shown(im, p, 3)))
    for fname, items, top in (("rell_model_review.png", cells, 34), ("rell_model_takes.png", closeups, 20)):
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

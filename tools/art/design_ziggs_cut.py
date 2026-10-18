#!/usr/bin/env python3
"""Ziggs's step-1 takes read back on their own grids and brought to the picked game size (PPU 1.5: 48 rows from the
helmet's top to the soles = 32 game rows), two ways each, with review sheets.

    python tools/art/design_ziggs_cut.py [--out dist/ziggs_packs]

Step 1 (assets/source/ziggs/codex_model, 2026-10-18, Codex new-chat-2) on 1254 squares (asked 1024, 14 px squares,
48 rows): regrid reads A-1 at 15 px (79 x 62) and A-2 at 14 px (79 x 61). Each is read back on its own grid (regrid.py,
alpha 0/255 at 128), its colours cut to COLOURS by k-means (design_varus.kmeans), then brought to 48 rows two ways:
  cut - design_rell_cut.even_cut: whole rows / columns dropped one per equal window, never the goggles' lines (the green
        lenses and their rims) nor the teeth's rows nor two neighbours;
  px  - pixel_down.pixelate (area vote; softer).
Writes assets/source/ziggs/hd/model<take>{,_cut,_px}.png and <out>/ziggs_model_review.png (the takes at game size beside
the pack's yordles) + ziggs_model_takes.png (every cut at 6x).
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
from design_ziggs_hd import lp  # noqa: E402,F811

SRC = os.path.join(ROOT, "assets", "source", "ziggs")
COLOURS = 40
PPU = 1.5
BODY = 48   # helmet top to soles (32 game rows)
# file stem -> (square px, body top row in the read-back)
TAKES = {"ziggs-model-A-1": (15.0, 0), "ziggs-model-A-2": (14.0, 0)}
NEIGHBOURS = ["fizz", "corki", "tristana", "teemo", "kennen", "lulu"]
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
    """The goggles' green lenses (their rows, and their columns with a rim square each side) and the teeth's rows (white
    in the upper half inside the face columns): never dropped. The bombs are cut on their own (bomb_cut)."""
    h, w = d.shape[:2]
    rgb = d[..., :3].astype(int)
    on = d[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = on & (g > r + 40) & (g > b + 20)
    white = on & (r > 200) & (g > 200) & (b > 190)
    ys, xs = np.nonzero(green)
    rows = set(range(ys.min(), ys.max() + 1)) if len(ys) else set()
    cols = set(range(xs.min() - 1, xs.max() + 2)) if len(xs) else set()
    face = np.zeros_like(white)
    face[:h // 2, int(w * 0.25):int(w * 0.75)] = True
    rows |= set(np.nonzero((white & face).any(1))[0].tolist())
    return sorted(r_ for r_ in rows if 0 <= r_ < h), sorted(c for c in cols if 0 <= c < w)


# each bomb with its glove and fuse in the read-back (rows, cols inclusive), per take: cut on its own with the skull's
# rows and columns kept, to exactly as many rows / columns as the body cut keeps in that box, and pasted over it
BOMBS = {"ziggs-model-A-1": [(8, 38, 0, 18), (16, 46, 61, 78)]}


def bomb_cut(d, cut, keep_r, keep_c, box):
    r0, r1, c0, c1 = box
    sub = d[r0:r1 + 1, c0:c1 + 1]
    white = (sub[..., 3] > 0) & (sub[..., :3].astype(int).min(2) > 190)
    kr = [i for i, r_ in enumerate(keep_r) if r0 <= r_ <= r1]
    kc = [i for i, c in enumerate(keep_c) if c0 <= c <= c1]
    part = RC.even_cut(sub, len(kr), len(kc), (np.nonzero(white.any(1))[0].tolist(), np.nonzero(white.any(0))[0].tolist()))
    out = cut.copy()
    out[kr[0]:kr[0] + len(kr), kc[0]:kc[0] + len(kc)] = part
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "ziggs_packs"))
    a = ap.parse_args()
    cells, closeups = [], []
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    for take, (size, top) in TAKES.items():
        d = read(take, size)
        k = BODY / (d.shape[0] - top)
        rows, cols = round(d.shape[0] * k), round(d.shape[1] * k)
        fr, fc = face_lines(d, top)
        cut, keep_r, keep_c = RC.even_cut(d, rows, cols, (fr, fc), index=True)
        for box in BOMBS.get(take, []):
            cut = bomb_cut(d, cut, keep_r, keep_c, box)
        px, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        px = OC.crop(px)
        tag = take.replace("ziggs-model-", "").replace("initial-", "i").replace("-", "")
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
    for fname, items, top in (("ziggs_model_review.png", cells, 34), ("ziggs_model_takes.png", closeups, 20)):
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

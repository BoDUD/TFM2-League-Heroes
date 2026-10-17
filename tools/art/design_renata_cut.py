#!/usr/bin/env python3
"""Renata's step-1 takes (Codex image_gen, 2026-10-17, assets/source/renata/codex_model) read back on their own grid
and brought to the user's size - the hair's top to the soles BODY game rows at DENS squares a game pixel
(「选 A，40 行，第 1 步按游戏格子重画，头放大到约四分之一，C 去掉多余的手臂、机械单独一张」) - two ways, league_yunara's
(design_yunara_cut.py):
  cut  whole rows and columns deleted (design_akali.dp_keep: never two neighbours, the cheapest lines first; the face,
       the magenta eyes, the mask, the skin, the gold and the magenta cost more), every square left as Codex drew it;
  px   pixel_down.pixelate (each new square the commonest colour under it, outline-first).

    python tools/art/design_renata_cut.py [--review DIR]

Asked for 12-px squares on a 1024 canvas (60 squares), Codex's image_gen gave 1254 px pictures with 9-9.5 px squares,
82 / 106 squares hair top to soles, soft alpha (hard alpha >= 128 here). Each take: regrid, a k-means palette of
COLOURS, then the two ways. Writes assets/source/renata/hd/model<take>.png (the read-back), model<take>_cut.png,
model<take>_px.png and model<take>_keep.json; with --review <dir>/renata_model_takes.png (8x) and
<dir>/renata_model_lineup.png (at game size next to the pack's supports, 4x).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_akali as DA  # noqa: E402
import design_varus as V  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renata")
CHAMPS = os.path.join(ROOT, "league", "champions")
BODY, DENS = 40, 1.5
TALL = round(BODY * DENS)          # 60 squares hair top to soles
SIZE = {"1": 9.5, "2": 9.0}        # regrid's measure of each take's squares
COLOURS = 40
PEERS = [("nami", 1.5), ("janna", 1.5), ("yunara", 1.5), ("swain", 1.5), ("darius", 1.0)]
BG = (196, 200, 190, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"renata-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d = crop(d)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def weights(d):
    """Outline, skin, the magenta (eyes, shirt, the arm's lines), the mask's silver and the gold cost more to delete."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    w = np.ones(d.shape[:2])
    w[rgb.sum(-1) < 120] = 3.0
    skin = (r > 120) & (r < 230) & (g > 60) & (g < 170) & (b > 30) & (b < 130) & (r > g + 25) & (g > b)
    w[skin] = 5.0
    magenta = (r > 170) & (g < 90) & (b > 80)
    w[magenta] = 6.0
    gold = (r > 180) & (g > 130) & (b < 90)
    w[gold] = 5.0
    silver = (r > 150) & (g > 160) & (b > 170) & (np.abs(r - b) < 50)
    w[silver] = 2.0
    w[d[..., 3] == 0] = 0.5
    return w


def cut(d, k, keep=None):
    """d with whole rows and columns deleted to about k of its size; keep: a dict that gets the kept rows / cols."""
    h, w = d.shape[:2]
    wt = weights(d)
    code = d.astype(np.int64) @ np.array([1 << 24, 1 << 16, 1 << 8, 1], np.int64)   # one number a square
    rows, _ = DA.dp_keep(list(code), list(wt), max(round(h * k), (h + 1) // 2))
    cols, _ = DA.dp_keep(list(code[rows].T), list(wt[rows].T), max(round(w * k), (w + 1) // 2))
    if keep is not None:
        keep.update(rows=[int(r) for r in rows], cols=[int(c) for c in cols])
    return d[rows][:, cols]


def frame0(hero):
    stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    tag = "hd_idle" if "hd_idle" in anims else "idle"
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    return im.crop(im.getbbox())


def strip(cells, scale_of, top=24, gap=18):
    ims = [(lab, Image.fromarray(a) if isinstance(a, np.ndarray) else a) for lab, a in cells]
    ims = [(lab, im.resize((round(im.width * scale_of(lab)), round(im.height * scale_of(lab))), Image.NEAREST))
           for lab, im in ims]
    W = sum(im.width for _, im in ims) + gap * (len(ims) + 1)
    H = max(im.height for _, im in ims) + top + gap
    can = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(can)
    x = gap
    for lab, im in ims:
        can.alpha_composite(im, (x, H - gap - im.height))
        dr.text((x, 6), lab, fill=(30, 30, 30, 255))
        x += im.width + gap
    dr.line([(0, H - gap), (W, H - gap)], fill=(120, 120, 120, 255))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    out = {}
    for take in SIZE:
        d = read(f"model-{take}", SIZE[take])
        k = TALL / d.shape[0]
        keep = {}
        c = cut(d, k, keep)
        with open(lp(os.path.join(SRC, "hd", f"model{take}_keep.json")), "w", encoding="utf-8") as f:
            json.dump(keep, f)
        p, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        p = crop(p)
        for name, im in (("", d), ("_cut", c), ("_px", p)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"model{take}{name}.png")))
        out[take] = (d, c, p)
        print(f"take {take}: read back {d.shape[1]}x{d.shape[0]}, k {k:.3f} -> cut {c.shape[1]}x{c.shape[0]}, "
              f"px {p.shape[1]}x{p.shape[0]}")
    if not a.review:
        return
    cells = []
    for take, (d, c, p) in out.items():
        cells += [(f"take {take} cut", c), (f"take {take} px", p)]
    os.makedirs(a.review, exist_ok=True)
    strip(cells, lambda lab: 8).convert("RGB").save(os.path.join(a.review, "renata_model_takes.png"))
    ppu = dict(PEERS)
    lineup = cells + [(h, frame0(h)) for h, _ in PEERS]
    strip(lineup, lambda lab: 4 / DENS if lab.split()[0] == "take" else 4 / ppu[lab])         .convert("RGB").save(os.path.join(a.review, "renata_model_lineup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()

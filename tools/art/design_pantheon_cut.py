#!/usr/bin/env python3
"""Pantheon's step-1 takes (Codex image_gen, 2026-10-16, assets/source/pantheon/codex_model) read back on their own grid
and brought to the user's size - helmet top to soles BODY game rows at DENS squares a game pixel (「选A 40尺寸 PPU1.5」)
- two ways, for the user to compare:
  cut  whole rows and columns deleted (design_akali.dp_keep: never two neighbours, the cheapest lines first), every
       square left as Codex drew it;
  px   pixel_down.pixelate (each new square the commonest colour under it, outline-first), the size sheet's way.

    python tools/art/design_pantheon_cut.py [--review DIR]

Asked for 12-px squares on a 1024 canvas (72 squares), Codex's image_gen gave 1254 px pictures with squares of about
8.8 (take 1) and 10.5 px (take 2) - 105-122 squares - and alpha 254 inside (hard alpha >= 128 here). Each take: regrid at
SIZE, a k-means palette of COLOURS, then the two ways. Writes assets/source/pantheon/hd/model<take>.png (the read-back),
model<take>_cut.png, model<take>_px.png; with --review <dir>/pantheon_model_takes.png (every version 8x) and
<dir>/pantheon_model_lineup.png (at game size next to the pack's top laners, 4x).
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

SRC = os.path.join(ROOT, "assets", "source", "pantheon")
CHAMPS = os.path.join(ROOT, "league", "champions")
BODY, DENS = 40, 1.5
HELM = round(BODY * DENS)          # 60 squares helmet top to soles
SIZE = {"1": 8.8, "2": 10.5}
COLOURS = 40
PEERS = [("garen", 1.9), ("darius", 1.0), ("jax", 1.0), ("shen", 1.0)]
BG = (196, 200, 190, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def read(take):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"pantheon-model-{take}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, SIZE[take])
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d = crop(d)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def helmet_top(d):
    """The helmet's top row: the first row whose drawn run is wider than the crest (a fifth of the widest row's...
    the helmet dome is about a tenth of the figure's width)."""
    op = d[..., 3] > 0
    w = op.shape[1]
    for y in range(op.shape[0]):
        xs = np.nonzero(op[y])[0]
        if len(xs) and xs.max() - xs.min() + 1 >= w // 7 and len(xs) >= w // 9:
            return y
    return 0


def weights(d):
    """Dark (outline) squares and the gem cost more to delete."""
    rgb = d[..., :3].astype(int)
    w = np.ones(d.shape[:2])
    w[rgb.sum(-1) < 120] = 3.0
    w[(rgb[..., 2] > 180) & (rgb[..., 0] < 150)] = 4.0
    w[d[..., 3] == 0] = 0.5
    return w


def cut(d, k):
    h, w = d.shape[:2]
    wt = weights(d)
    code = d.astype(np.int64) @ np.array([1 << 24, 1 << 16, 1 << 8, 1], np.int64)   # one number a square
    rows, _ = DA.dp_keep(list(code), list(wt), max(round(h * k), (h + 1) // 2))
    cols, _ = DA.dp_keep(list(code[rows].T), list(wt[rows].T), max(round(w * k), (w + 1) // 2))
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
        d = read(take)
        top = helmet_top(d)
        k = HELM / (d.shape[0] - top)
        c = cut(d, k)
        p, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        p = crop(p)
        for name, im in (("", d), ("_cut", c), ("_px", p)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"model{take}{name}.png")))
        out[take] = (d, c, p)
        print(f"take {take}: read back {d.shape[1]}x{d.shape[0]} (helmet top row {top}), k {k:.3f} -> cut "
              f"{c.shape[1]}x{c.shape[0]}, px {p.shape[1]}x{p.shape[0]}")
    if not a.review:
        return
    auto = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A_ppu15.png"))).convert("RGBA"))
    cells = [("step 0 A, auto", auto)]
    for take, (d, c, p) in out.items():
        cells += [(f"take {take} cut", c), (f"take {take} px", p)]
    os.makedirs(a.review, exist_ok=True)
    strip(cells, lambda lab: 8).convert("RGB").save(os.path.join(a.review, "pantheon_model_takes.png"))
    peers = [(f"{h}", frame0(h)) for h, _ in PEERS]
    ppu = dict(PEERS)
    lineup = cells + peers
    strip(lineup, lambda lab: 4 / DENS if lab.split()[0] in ("step", "take") else 4 / ppu[lab]) \
        .convert("RGB").save(os.path.join(a.review, "pantheon_model_lineup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()

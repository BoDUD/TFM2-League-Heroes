#!/usr/bin/env python3
"""Yunara's step-1 takes (Codex image_gen, 2026-10-17, assets/source/yunara/codex_model) read back on their own grid
and brought to the user's size - the golden ornaments' top to the soles BODY game rows at DENS squares a game pixel
(「选 A，40 行，第 1 步按游戏格子重画，头放大到约四分之一，念珠画小一点」) - two ways, league_aphelios's
(design_aphelios_cut.py):
  cut  whole rows and columns deleted (design_akali.dp_keep: never two neighbours, the cheapest lines first; the face,
       the eye, the skin and the gold cost more), every square left as Codex drew it;
  px   pixel_down.pixelate (each new square the commonest colour under it, outline-first).

    python tools/art/design_yunara_cut.py [--review DIR]

Asked for 12-px squares on a 1024 canvas (60 squares), Codex's image_gen gave 1254 px pictures with 9-9.5 px squares,
95-103 squares ornament top to soles, soft alpha (hard alpha >= 128 here). Each take: regrid, a k-means palette of
COLOURS, then the two ways; the bead sheets at the take's cut scale times the sheet's own square size. Writes
assets/source/yunara/hd/model<take>.png (the read-back), model<take>_cut.png, model<take>_px.png, beads<take>.png /
beads<take>_cut.png and model<take>_keep.json; with --review <dir>/yunara_model_takes.png (8x) and
<dir>/yunara_model_lineup.png (at game size next to the pack's ADCs, 4x).
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

SRC = os.path.join(ROOT, "assets", "source", "yunara")
CHAMPS = os.path.join(ROOT, "league", "champions")
BODY, DENS = 40, 1.5
TALL = round(BODY * DENS)          # 60 squares ornament top to soles
SIZE = {"1": 9.5, "2": 9.0}
W_SIZE = {"1": 11.5, "2": 11.0}    # the bead sheets' squares (regrid's measure)
COLOURS = 40
PEERS = [("kalista", 1.4), ("aphelios", 1.5), ("katarina", 1.5), ("jinx", 1.0), ("kaisa", 1.0)]
BG = (196, 200, 190, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"yunara-{name}.png"))).convert("RGBA")).copy()
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
    """Outline (the closed eye's line), skin, the silver forehead jewel and the gold cost more to delete."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    w = np.ones(d.shape[:2])
    w[rgb.sum(-1) < 120] = 3.0
    skin = (r > 190) & (g > 140) & (b > 120) & (r > b)
    w[skin] = 5.0
    gold = (r > 180) & (g > 130) & (b < 90)
    w[gold] = 5.0
    silver = (r > 170) & (g > 190) & (b > 210)
    w[silver] = 6.0
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
            json.dump(keep, f)        # the read-back's rows / columns the cut keeps (rig_aphelios maps parts with them)
        p, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        p = crop(p)
        wd = read(f"beads-{take}", W_SIZE[take])
        # the sheet's beads at the take's scale: the same k on the take's grid, times the sheet's own square size
        # against the model's
        kw = k * W_SIZE[take] / SIZE[take]
        wc = cut(wd, kw) if kw >= 0.5 else crop(PD.pixelate(wd, kw, (wd.shape[1] / 2, wd.shape[0]), PD.edge_colour(wd))[0])
        for name, im in (("", d), ("_cut", c), ("_px", p)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"model{take}{name}.png")))
        Image.fromarray(wd).save(lp(os.path.join(SRC, "hd", f"beads{take}.png")))
        Image.fromarray(wc).save(lp(os.path.join(SRC, "hd", f"beads{take}_cut.png")))
        out[take] = (d, c, p, wc)
        print(f"take {take}: read back {d.shape[1]}x{d.shape[0]}, k {k:.3f} -> cut "
              f"{c.shape[1]}x{c.shape[0]}, px {p.shape[1]}x{p.shape[0]}; beads {wd.shape[1]}x{wd.shape[0]} (k {kw:.3f}) -> "
              f"{wc.shape[1]}x{wc.shape[0]}")
    if not a.review:
        return
    cells = []
    for take, (d, c, p, wc) in out.items():
        cells += [(f"take {take} cut", c), (f"take {take} px", p)]
    os.makedirs(a.review, exist_ok=True)
    strip(cells + [(f"beads {t} cut", v[3]) for t, v in out.items()], lambda lab: 8).convert("RGB").save(
        os.path.join(a.review, "yunara_model_takes.png"))
    ppu = dict(PEERS)
    lineup = cells + [(h, frame0(h)) for h, _ in PEERS]
    strip(lineup, lambda lab: 4 / DENS if lab.split()[0] == "take" else 4 / ppu[lab]) \
        .convert("RGB").save(os.path.join(a.review, "yunara_model_lineup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()

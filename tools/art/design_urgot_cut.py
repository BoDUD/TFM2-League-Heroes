#!/usr/bin/env python3
"""Urgot's step-1 takes (Codex image_gen, 2026-10-16, assets/source/urgot/codex_model) read back on their own grid and
brought to the user's size - the cannon's top to the leg tips 42 game px at 1.5 squares a game pixel = 63 squares
(「选 A，炮顶到腿尖 42 px，PPU 1.5，第 1 步按游戏格子重画」) - two ways:
  cut  whole rows and columns deleted (design_akali.dp_keep: never two neighbours, the cheapest lines first; the
       outline, the skin, the red eye, the green hoses and the gold cost more), every square left as Codex drew it -
       only where the take is at most twice too big;
  box  an area mean (colour weighted by alpha, clear under half cover) snapped to the take's palette
       (pixel_down.pixelate's near-black vote blackened Urgot's dense lines, review_urgot_size.py).

    python tools/art/design_urgot_cut.py [--review DIR]

Asked for 12-px squares on a 1024 canvas (63 squares), Codex's image_gen gave 1254 px pictures: take 1 with ~6 px
squares, 202 squares tall (A's detail, too fine for any cut); take 2 with 12 px squares, 82 squares tall (coarse blocks,
the head simplified). Each take: regrid, a k-means palette of COLOURS, then the ways that fit. Writes
assets/source/urgot/hd/model<take>.png (the read-back), model<take>_cut.png / model<take>_box.png; with --review
<dir>/urgot_model_takes.png (8x) and <dir>/urgot_model_lineup.png (at game size next to the pack's big tops, 4x).
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
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "urgot")
CHAMPS = os.path.join(ROOT, "league", "champions")
TALL = 63                        # 42 game px x 1.5, the cannon's top to the leg tips
SIZE = {"1": 6.0, "2": 12.0}     # regrid's own measure
COLOURS = 40
PEERS = [("darius", 1.0), ("drmundo", 1.5), ("sion", 1.0), ("tahmkench", 1.2), ("pantheon", 1.5)]
BG = (196, 200, 190, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def read(take):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"urgot-model-{take}.png"))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, SIZE[take])
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d = crop(d)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out, pal


def weights(d):
    """The outline, the pale skin, the red eye, the green hoses and the gold cost more to delete."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    w = np.ones(d.shape[:2])
    w[rgb.sum(-1) < 120] = 3.0
    w[(r > 190) & (g > 170) & (b > 160)] = 5.0            # pale skin
    w[(r > 170) & (g < 80) & (b < 80)] = 12.0              # the red eye / light
    w[(g > 150) & (r < 140) & (b < 120)] = 5.0             # toxic green
    w[(r > 180) & (g > 120) & (b < 90)] = 4.0              # gold
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


def box(d, k, pal):
    """Area mean (colour weighted by alpha), clear under half cover, every square snapped to the palette."""
    w, h = max(1, round(d.shape[1] * k)), max(1, round(d.shape[0] * k))
    f = d.astype(np.float64)
    al = f[..., 3:] / 255.0
    pre = np.concatenate([f[..., :3] * al, al * 255], axis=2).astype(np.float32)
    s = np.stack([np.asarray(Image.fromarray(pre[..., c]).resize((w, h), Image.BOX)) for c in range(4)], axis=2)
    a = s[..., 3] / 255.0
    rgb = s[..., :3] / np.maximum(a[..., None], 1e-6)
    op = a >= 0.5
    dist = ((rgb[:, :, None, :] - pal[None, None, :, :].astype(np.float64)) ** 2).sum(-1)
    out = np.zeros((h, w, 4), np.uint8)
    out[op, :3] = pal[dist.argmin(-1)][op]
    out[op, 3] = 255
    return crop(out)


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
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    cells = []
    for take in SIZE:
        d, pal = read(take)
        k = TALL / d.shape[0]
        Image.fromarray(d).save(lp(os.path.join(SRC, "hd", f"model{take}.png")))
        ways = [("box", box(d, k, pal))]
        if k >= 0.5:
            keep = {}
            ways.insert(0, ("cut", cut(d, k, keep)))
            with open(lp(os.path.join(SRC, "hd", f"model{take}_keep.json")), "w", encoding="utf-8") as f:
                json.dump(keep, f)    # the read-back's rows / columns the cut keeps (the rig maps parts with them)
        for name, im in ways:
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"model{take}_{name}.png")))
            cells.append((f"take {take} {name}", im))
        print(f"take {take}: read back {d.shape[1]}x{d.shape[0]}, k {k:.3f} -> "
              + ", ".join(f"{n} {im.shape[1]}x{im.shape[0]}" for n, im in ways))
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    strip(cells, lambda lab: 8).convert("RGB").save(os.path.join(a.review, "urgot_model_takes.png"))
    ppu = dict(PEERS)
    lineup = cells + [(h, frame0(h)) for h, _ in PEERS]
    strip(lineup, lambda lab: 4 / 1.5 if lab.split()[0] == "take" else 4 / ppu[lab]) \
        .convert("RGB").save(os.path.join(a.review, "urgot_model_lineup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()

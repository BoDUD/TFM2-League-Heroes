#!/usr/bin/env python3
"""Kai'Sa's dense design: Codex's step-0 picture read back on its own grid (tools/art/design_xinzhao_hd.py's way).

    python tools/art/design_kaisa_hd.py [--review DIR]

Asked (assets/source/kaisa/PICTURE_PROMPT_PPU.md) for 63 squares of 11 px from the raised pods' tips to the soles,
Codex (assets/source/kaisa/hd/, its HANDOFF.md) delivered codex.png / codex_grid.png = its own 44 x 63 export, made by
sampling the centre of each cell of a 1254-px generation (raw/generation-02.png) - fewer rows than drawn, the face and
the gems broke into specks (memory sprite-pipeline: never read a Codex draft below the rows it was drawn at). So
raw/generation-02.png (coarse pixel art, squares of SIZE px: the autocorrelation of its colour edges peaks at 19-20 and
39) is read back here one square a design square (regrid.py), its colours cut to COLOURS by k-means in Lab, nothing
cut: 42 x 61 (2 rows short of the 63 asked - never stretched). raw/generation-01.png is a fine pixel illustration
(~180 rows, no regular grid) Codex itself set aside. The eyes are then set square by square (EYES: both 2 x 2, white
then the iris, at the same rows) and the near cheek's marking moved a row down under the near eye.

Writes assets/source/kaisa/hd/readback.png and design.png; with --review <dir>/kaisa_ppu_size.png (the design at
PPU 1.5 and at 1.45 = 61 / 42, her height now, next to Kai'Sa now, Jax, Katarina and Xin Zhao as the game draws them,
3 screen px a game pixel) and <dir>/kaisa_ppu_closeup.png (Codex's own export, the read-back, the design, 8x).
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
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "kaisa", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
SIZE = 19.3                       # Codex's square in raw/generation-02.png, px
COLOURS = 40
GAME_ROWS = 42                    # her 1x idle, pods' tips to soles
WHITE, IRIS_D, IRIS_L, MARK = (251, 249, 250), (141, 1, 155), (204, 0, 222), (180, 71, 197)
# design squares (x, y) -> rgb: the near eye (cols 25-26) and the far eye (29-30), rows 19-20, white then the iris;
# the near cheek's marking (it sat where the near eye's lower row goes) one row lower
EYES = {(25, 19): WHITE, (26, 19): IRIS_D, (25, 20): WHITE, (26, 20): IRIS_L,
        (29, 19): WHITE, (30, 19): IRIS_D, (29, 20): WHITE, (30, 20): IRIS_L,
        (24, 22): MARK}
BG = (196, 200, 190, 255)
PEERS = ["kaisa", "jax", "katarina", "xinzhao"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def read():
    a = np.asarray(Image.open(lp(os.path.join(HD, "raw", "generation-02.png"))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, SIZE)
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d = crop(d)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def frame0(hero):
    import ppu_hd
    stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    ppu = ppu_hd.PPU.get(hero)
    tag = "hd_idle" if ppu and "hd_idle" in anims else "idle"
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    return im.crop(im.getbbox()), (ppu if tag == "hd_idle" else 1.0)


def strip(cells, gap=28, top=24):
    W = sum(im.width for _, im in cells) + gap * (len(cells) + 1)
    H = max(im.height for _, im in cells) + top + gap
    can = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(can)
    x = gap
    for lab, im in cells:
        can.alpha_composite(im, (x, H - gap - im.height))
        dr.text((x, 6), lab, fill=(30, 30, 30, 255))
        x += im.width + gap
    dr.line([(0, H - gap), (W, H - gap)], fill=(120, 120, 120, 255))
    return can


def shown(im, ppu, scale):
    k = scale / ppu
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    d = read()
    c = d.copy()
    for (x, y), col in EYES.items():
        c[y, x, :3] = col
        c[y, x, 3] = 255
    Image.fromarray(d).save(lp(os.path.join(HD, "readback.png")))
    Image.fromarray(c).save(lp(os.path.join(HD, "design.png")))
    print(f"read back {d.shape[1]}x{d.shape[0]}, {len(np.unique(c[c[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    rows = c.shape[0]
    cells = [(f"new 1.5 ({rows / 1.5:.0f}px)", shown(Image.fromarray(c), 1.5, 3)),
             (f"new {rows / GAME_ROWS:.2f} (42px)", shown(Image.fromarray(c), rows / GAME_ROWS, 3))]
    for h in PEERS:
        im, p = frame0(h)
        cells.append((("now" if h == "kaisa" else h) + (f" {p}" if p != 1 else " 1x"), shown(im, p, 3)))
    strip(cells).convert("RGB").save(os.path.join(a.review, "kaisa_ppu_size.png"))
    codex = np.asarray(Image.open(lp(os.path.join(HD, "codex_grid.png"))).convert("RGBA"))
    z = 8
    strip([("Codex's own 44x63 (cell centres sampled: not used)", shown(Image.fromarray(codex), 1, z)),
           (f"read back {d.shape[1]}x{rows} (raw/generation-02, its own squares)", shown(Image.fromarray(d), 1, z)),
           ("design (eyes set square by square)", shown(Image.fromarray(c), 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, "kaisa_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()

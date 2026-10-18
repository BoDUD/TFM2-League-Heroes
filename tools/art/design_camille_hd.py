#!/usr/bin/env python3
"""Camille's dense (PPU 1.5) design: Codex's step-0 picture read back on its own grid, then cut to the asked height.

    python tools/art/design_camille_hd.py [--review DIR]

Asked (assets/source/camille/PICTURE_PROMPT_PPU.md) for 69 squares of 11 px from the hair's top to the blade tips,
Codex's image_gen drew two pictures (assets/source/camille/hd/raw/, its HANDOFF.md): generation-01 on ~9.3-px squares
(~128 rows, far too many) and generation-02 (= its camille-A.png, hd/codex.png) on squares of SIZE px (the
autocorrelation of its colour edges peaks at 13, 26, 39), alpha soft at the edges (< 128 dropped). regrid.py reads
generation-02 one square a design square (35 x 76), its colours cut to COLOURS by k-means in Lab (design_varus.kmeans)
-> hd/readback.png. The eyes are set square by square there (EYES: Codex's near eye was one row - white and two
cyans - and its far eye a single cyan square on the cheek's edge with no outline beyond: both now 2 x 2, white then
the iris, the cheek's outline closed). Never sampled at fewer rows than drawn (memory sprite-pipeline): whole rows and
columns are deleted to ROWS (her 46 game rows x 1.5; at 76 rows she would stand 51 game rows - the user refused 50:
「50太大了 用46」) by design_rell_cut.even_cut (one per equal window, never two neighbours; the face's rows and
columns, the hair's top row and the blade tips' row kept) -> hd/design.png.

With --review: <dir>/camille_ppu_size.png (the design at PPU 1.5, the uncut read-back at 1.5, next to Camille now,
Jax, Xin Zhao and Kai'Sa as the game draws them, feet on one line, 3 screen pixels a game pixel) and
<dir>/camille_ppu_closeup.png (Codex's picture, the read-back and the design at 8x).
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
import design_rell_cut as RC  # noqa: E402
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "camille", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
SIZE = 12.9                       # Codex's square in raw/generation-02.png, px
COLOURS = 40
PPU = 1.5
GAME_ROWS = 46                    # her 1x idle, hair to blade tips
ROWS = round(GAME_ROWS * PPU)     # 69
# read-back squares kept whole: the hair's crown to the chin and the ear to the cheek
FACE_ROWS = range(8, 19)
FACE_COLS = range(12, 22)
WHITE, IRIS_D, IRIS_L, SKIN, LINE = (251, 251, 252), (4, 149, 212), (0, 191, 233), (252, 213, 182), (1, 0, 16)
# read-back squares (x, y) -> rgb: the near eye (cols 15-16) and the far eye (19-20), rows 13-14, white then the iris;
# the near eye's third square back to skin; the cheek's outline beside the far eye
EYES = {(15, 13): WHITE, (16, 13): IRIS_D, (15, 14): WHITE, (16, 14): IRIS_L, (17, 13): SKIN,
        (19, 13): WHITE, (20, 13): IRIS_D, (19, 14): WHITE, (20, 14): IRIS_L, (21, 13): LINE, (21, 14): LINE}
BG = (196, 200, 190, 255)
PEERS = ["camille", "jax", "xinzhao", "kaisa"]


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


def eyes(d):
    for (x, y), c in EYES.items():
        d[y, x, :3] = c
        d[y, x, 3] = 255


def cut(d):
    h, w = d.shape[:2]
    keep = (set(FACE_ROWS) | {0, h - 1}, set(FACE_COLS) | {0, w - 1})
    return RC.even_cut(d, ROWS, round(w * ROWS / h), keep, index=True)


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


def strip(cells, gap=40, top=24):
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
    Image.fromarray(d).save(lp(os.path.join(HD, "readback.png")))
    e = d.copy()
    eyes(e)
    c, rows, cols = cut(e)
    Image.fromarray(c).save(lp(os.path.join(HD, "design.png")))
    gone_r = sorted(set(range(d.shape[0])) - set(rows))
    gone_c = sorted(set(range(d.shape[1])) - set(cols))
    print(f"read back {d.shape[1]}x{d.shape[0]} -> design {c.shape[1]}x{c.shape[0]}, "
          f"{len(np.unique(c[c[..., 3] > 0][:, :3], axis=0))} colours; rows cut {gone_r}; cols cut {gone_c}")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    cells = [(f"new {PPU}: {c.shape[0] / PPU:.0f}px", shown(Image.fromarray(c), PPU, 3)),
             (f"uncut: {e.shape[0] / PPU:.0f}px", shown(Image.fromarray(e), PPU, 3))]
    for h in PEERS:
        im, p = frame0(h)
        cells.append((("now" if h == "camille" else h) + (f" {p}" if p != 1 else " 1x"), shown(im, p, 3)))
    strip(cells).convert("RGB").save(os.path.join(a.review, "camille_ppu_size.png"))
    codex = np.asarray(Image.open(lp(os.path.join(HD, "codex.png"))).convert("RGBA"))
    z = 8
    cdx = Image.fromarray(crop(np.where(codex[..., 3:] >= 128, codex, 0).astype(np.uint8)))
    cdx = cdx.resize((round(cdx.width * e.shape[0] * z / cdx.height), e.shape[0] * z), Image.NEAREST)
    strip([("Codex's picture (generation-02)", cdx),
           (f"read back {d.shape[1]}x{d.shape[0]} on its own squares", shown(Image.fromarray(d), 1, z)),
           (f"design {c.shape[1]}x{c.shape[0]} (eyes set, even cut)", shown(Image.fromarray(c), 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, "camille_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()

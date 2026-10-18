#!/usr/bin/env python3
"""Xin Zhao's dense (PPU 1.5) design: Codex's step-0 picture read back on its own grid, then cut to the asked height.

    python tools/art/design_xinzhao_hd.py [--review DIR]

Asked (assets/source/xinzhao/PICTURE_PROMPT_PPU.md) for 63 squares of 11 px from the topknot's top to the soles, Codex's
image_gen (assets/source/xinzhao/hd/codex.png, its xinzhao-A.png, the third generation; raw/ the first two) drew squares
of SIZE px (the autocorrelation of its colour edges peaks at 12, 24, 36, 48 across and down) with a soft glow round the
figure (alpha < 128, dropped) - its HANDOFF.md. regrid.py reads it one square a design square (77 rows topknot to soles,
123 columns with the spear), its colours cut to COLOURS by k-means in Lab (design_varus.kmeans) -> hd/readback.png.
Never sampled at fewer rows than drawn (memory sprite-pipeline): whole rows and columns are deleted to ROWS
(design_rell_cut.even_cut: one per equal window, never two neighbours; the face's rows and columns, the topknot's top row and
the soles' row kept) -> hd/design.png. The eyes are then set square by square (EYES: the near eye and the far eye the
same height, two rows each).

With --review: <dir>/xinzhao_ppu_size.png (the design at PPU 1.5 next to Xin Zhao now, Jax and Katarina as the game
draws them, feet on one line, 3 screen pixels a game pixel) and <dir>/xinzhao_ppu_closeup.png (read-back and design 8x).
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

HD = os.path.join(ROOT, "assets", "source", "xinzhao", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
SIZE = 12.0                       # Codex's square, px
COLOURS = 40
PPU = 1.5
GAME_ROWS = 42                    # his 1x idle, topknot to soles
ROWS = round(GAME_ROWS * PPU)     # 63
# read-back squares kept whole: brows to chin and ear to cheek (rows / columns of hd/readback.png)
FACE_ROWS = range(26, 35)
FACE_COLS = range(73, 87)
# design squares (hd/design.png) set after the cut, (x, y) -> rgb. Codex's near eye was white + iris + two stray squares
# (brown, pink) and its far eye one dark square against the cheek's outline (HANDOFF: 两眼并非严格同宽同高): both now
# 2 x 2 at rows 23-24, white then the iris (dark over bright violet) so both look front-right, the far brow closed.
WHITE, IRIS_D, IRIS_L, SKIN, BROW = (252, 252, 252), (64, 3, 121), (93, 3, 186), (253, 188, 140), (6, 1, 12)
EYES = {(63, 23): WHITE, (64, 23): IRIS_D, (63, 24): WHITE, (64, 24): IRIS_L, (65, 23): SKIN, (65, 24): SKIN,
        (67, 23): WHITE, (68, 23): IRIS_D, (67, 24): WHITE, (68, 24): IRIS_L, (67, 22): BROW}
BG = (196, 200, 190, 255)
PEERS = ["xinzhao", "jax", "katarina"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def read():
    a = np.asarray(Image.open(lp(os.path.join(HD, "codex.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, SIZE)
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d = crop(d)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def cut(d):
    """design_rell_cut.even_cut: one line dropped per equal window (the cheapest there, never two neighbours), the face's
    rows and columns, the top row and the soles' row kept - a DP over the whole height took every line from the cheap
    edges (the spear's blade halved, the topknot and the shins squashed)."""
    h, w = d.shape[:2]
    keep = (set(FACE_ROWS) | {0, h - 1}, set(FACE_COLS) | {0, w - 1})
    return RC.even_cut(d, ROWS, round(w * ROWS / h), keep, index=True)


def eyes(d):
    for (x, y), c in EYES.items():
        d[y, x, :3] = c
        d[y, x, 3] = 255


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


def strip(cells, gap=18, top=24):
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
    c, rows, cols = cut(d)
    eyes(c)
    Image.fromarray(d).save(lp(os.path.join(HD, "readback.png")))
    Image.fromarray(c).save(lp(os.path.join(HD, "design.png")))
    gone_r = sorted(set(range(d.shape[0])) - set(rows))
    gone_c = sorted(set(range(d.shape[1])) - set(cols))
    print(f"read back {d.shape[1]}x{d.shape[0]} -> design {c.shape[1]}x{c.shape[0]}; rows cut {gone_r}; cols cut {gone_c}")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    cells = [(f"Xin Zhao new  PPU {PPU}  {c.shape[0]} squares", shown(Image.fromarray(c), PPU, 3))]
    for h in PEERS:
        im, p = frame0(h)
        cells.append((h + (" now" if h == "xinzhao" else "") + (f"  PPU {p}" if p != 1 else "  1x"), shown(im, p, 3)))
    strip(cells).convert("RGB").save(os.path.join(a.review, "xinzhao_ppu_size.png"))
    z = 8
    strip([(f"read back {d.shape[0]} rows (Codex's own 12-px squares)", shown(Image.fromarray(d), 1, z)),
           (f"design {c.shape[0]} rows (whole rows / columns cut)", shown(Image.fromarray(c), 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, "xinzhao_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()

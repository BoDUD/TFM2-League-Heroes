#!/usr/bin/env python3
"""Fiora's dense (PPU 1.5) design: Codex's step-0 picture read back on its own grid, then cut to the asked height.

    python tools/art/design_fiora_hd.py [--review DIR]

Asked (assets/source/fiora/PICTURE_PROMPT_PPU.md) for 60 squares of 11 px from the hair's top to the soles, Codex's
image_gen drew two pictures on a BLACK ground with a soft glow round the figure and a halo round the blade
(assets/source/fiora/hd/raw/, its HANDOFF.md); it exported generation-02 sampled at square centres (hd/codex.png, the
face broken), so generation-02 is read here. cutout() takes the figure off the ground and the glow, the blade left
out; regrid.py reads it one square a design square (~9.5 px, 79 rows), the colours cut to COLOURS by k-means in Lab
(design_varus.kmeans), the rim's glow-tinted squares cleaned (rim()) -> hd/readback.png. The eyes are set square by square there (EYES). Never sampled at fewer rows
than drawn (memory sprite-pipeline): whole rows and columns are deleted to ROWS (her 40 game rows x 1.5) by
design_rell_cut.even_cut (the face's rows and columns, the hair's top row, the soles' row and the blade's kept). The blade is drawn
last on the cut design, as Codex drew it but straight and clean: BLADE_W squares thick (white over blue-grey), no
outline, BLADE_LEN squares long from the guard (her rapier now, ~20.5 game px, x PPU) -> hd/design.png.

With --review: <dir>/fiora_ppu_size.png (the design at PPU 1.5, the uncut read-back at 1.5, next to Fiora now,
Kai'Sa, Camille and Xin Zhao as the game draws them, feet on one line, 3 screen pixels a game pixel) and
<dir>/fiora_ppu_closeup.png (Codex's picture, the read-back and the design at 8x).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_rell_cut as RC  # noqa: E402
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "fiora", "hd")
CHAMPS = os.path.join(ROOT, "league", "champions")
BRIGHT, OUTLINE, DARK = 70, 18, 14   # raw: colour above BRIGHT, outline below DARK within OUTLINE px of colour
CLOSE, HAIR_Y, GUARD_X = 2, 360, 905  # raw px: outline gap closing, the chin's row, the guard's tip
COLOURS = 40
GLOW = (50, 130)
PPU = 1.5
GAME_ROWS = 40                    # her 1x idle, hair to soles
ROWS = round(GAME_ROWS * PPU)     # 60
BLADE_W, BLADE_LEN = 2, 31
BLADE = [(250, 250, 252), (168, 176, 198)]   # Codex's blade: the white top square, the blue-grey under it
# read-back squares kept whole: the brows to the chin, the near cheek to the face's far outline
FACE_ROWS = range(9, 19)
FACE_COLS = range(33, 42)
WHITE, IRIS_D, IRIS_L, SKIN, LINE = (250, 249, 249), (4, 120, 169), (17, 197, 249), (252, 228, 205), (3, 3, 2)
# read-back squares (x, y) -> rgb: Codex drew the near eye three squares wide (a white and two blues) and the far eye
# one column of blue against the face's outline; both now 2 x 2 at rows 12-13, white then the iris (near 35-36, far
# 38-39), the nose's skin square 37 between them, the far eye's lash over it (38, 11) like the near one's
EYES = {(34, 13): SKIN, (35, 12): WHITE, (36, 12): IRIS_D, (35, 13): WHITE, (36, 13): IRIS_L,
        (38, 12): WHITE, (39, 12): IRIS_D, (38, 13): WHITE, (39, 13): IRIS_L, (38, 11): LINE, (37, 11): SKIN}
BG = (196, 200, 190, 255)
PEERS = ["fiora", "kaisa", "camille", "xinzhao"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def cutout():
    """Codex's figure off its black ground and glow. The outline pixels (near-black, within OUTLINE px of colour)
    are thickened by CLOSE px to shut their small gaps, and whatever the outside reaches round them is ground or glow;
    the rest is the figure. The crimson lock has no outline on its right, so above HAIR_Y (the chin) the colour
    mask stands instead (no glow is left there). The blade and its halo go: nothing right of GUARD_X."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "raw", "generation-02.png"))).convert("RGB")).astype(int)
    mx = a.max(axis=2)
    col = mx >= BRIGHT
    line = (mx < DARK) & (nd.distance_transform_edt(~col) <= OUTLINE)
    wall = nd.binary_dilation(line, iterations=CLOSE)
    wall[:, GUARD_X] = True
    lab, _ = nd.label(~wall)
    rim = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    fig = ~np.isin(lab, [v for v in np.unique(rim) if v])
    loose = nd.binary_fill_holes(col | line)
    fig[:HAIR_Y] = loose[:HAIR_Y]
    fig[:, GUARD_X + 1:] = False
    lab, n = nd.label(fig)
    big = np.argmax(nd.sum(fig, lab, range(1, n + 1))) + 1
    return np.dstack([a, np.where(lab == big, 255, 0)]).astype(np.uint8)


def rim(d):
    """The squares on the figure's rim the glow tinted: dull warm or grey ones (brightest channel GLOW, its spread
    under 70, blue not above red) are glow and go; darker ones are the outline, set to the outline's black."""
    op = d[..., 3] > 0
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    edge = op & nd.binary_dilation(~nd.binary_fill_holes(op), cross)
    c = d[..., :3].astype(int)
    mx, mn = c.max(axis=2), c.min(axis=2)
    glow = edge & (mx >= GLOW[0]) & (mx < GLOW[1]) & (mx - mn < 70) & (c[..., 2] <= c[..., 0] + 10)
    dark = edge & (mx < GLOW[0]) & ~glow
    black = c[op][np.argmin(c[op].sum(axis=1))]
    d[glow] = 0
    d[dark, :3] = black
    print(f"rim: {int(glow.sum())} glow squares off, {int(dark.sum())} set to the outline")
    return d


def read():
    d, size, _ = RG.regrid(cutout())
    d = crop(d)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return rim(out), size


def eyes(d):
    for (x, y), c in EYES.items():
        d[y, x, :3] = c
        d[y, x, 3] = 255


def cut(d, blade_row):
    h, w = d.shape[:2]
    keep = (set(FACE_ROWS) | {0, h - 1} | set(range(blade_row, blade_row + BLADE_W)), set(FACE_COLS) | {0, w - 1})
    return RC.even_cut(d, ROWS, round(w * ROWS / h), keep, index=True)


def blade(d, row):
    """The rapier's blade, BLADE_LEN squares from the stub Codex's blade left past the guard (the rightmost figure
    square on `row`) on."""
    x0 = int(np.nonzero(d[row:row + BLADE_W, :, 3].any(axis=0))[0].max())
    out = np.zeros((d.shape[0], x0 + BLADE_LEN, 4), np.uint8)
    out[:, :d.shape[1]] = d
    for k, c in enumerate(BLADE):
        out[row + k, x0:x0 + BLADE_LEN, :3] = c
        out[row + k, x0:x0 + BLADE_LEN, 3] = 255
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
    ap.add_argument("--blade-row", type=int, help="read-back row of the blade's top square")
    a = ap.parse_args()
    d, size = read()
    Image.fromarray(d).save(lp(os.path.join(HD, "readback.png")))
    print(f"square {size}, read back {d.shape[1]}x{d.shape[0]}")
    if a.blade_row is None:
        return
    e = d.copy()
    eyes(e)
    c, rows, cols = cut(e, a.blade_row)
    c = blade(c, rows.index(a.blade_row))
    Image.fromarray(c).save(lp(os.path.join(HD, "design.png")))
    gone_r = sorted(set(range(d.shape[0])) - set(rows))
    gone_c = sorted(set(range(d.shape[1])) - set(cols))
    print(f"design {c.shape[1]}x{c.shape[0]}, {len(np.unique(c[c[..., 3] > 0][:, :3], axis=0))} colours; "
          f"rows cut {gone_r}; cols cut {gone_c}")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    cells = [(f"new {PPU}: {c.shape[0] / PPU:.0f}px", shown(Image.fromarray(c), PPU, 3)),
             (f"uncut: {e.shape[0] / PPU:.0f}px", shown(Image.fromarray(blade(e, a.blade_row)), PPU, 3))]
    for h in PEERS:
        im, p = frame0(h)
        cells.append((("now" if h == "fiora" else h) + (f" {p}" if p != 1 else " 1x"), shown(im, p, 3)))
    strip(cells).convert("RGB").save(os.path.join(a.review, "fiora_ppu_size.png"))
    raw = Image.open(lp(os.path.join(HD, "raw", "generation-02.png"))).convert("RGBA")
    z = 8
    cdx = raw.crop(raw.getbbox())
    cdx = cdx.resize((round(cdx.width * e.shape[0] * z / 79 / 10), round(cdx.height * e.shape[0] * z / 79 / 10)),
                     Image.LANCZOS)
    strip([("Codex's picture (generation-02)", cdx),
           (f"read back {d.shape[1]}x{d.shape[0]} on its own squares", shown(Image.fromarray(d), 1, z)),
           (f"design {c.shape[1]}x{c.shape[0]} (eyes set, even cut, blade)", shown(Image.fromarray(c), 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, "fiora_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()

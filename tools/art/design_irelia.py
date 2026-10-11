#!/usr/bin/env python3
"""Irelia's design: assets/source/irelia/design42/irelia42.txt (a letter table, design42/palette.json) ->
assets/source/native/irelia_native.png (the 128x128 canvas: the soles on row 99, the middle of the feet on column 64).

    python tools/art/design_irelia.py            # write the native design
    python tools/art/design_irelia.py --check    # compare with the committed native design
    python tools/art/design_irelia.py --sheet OUT.png   # the design at 8x beside the picture, 1x-3x, the pack's heroes

How it came about (2026-10-11):
  * step 0: the user picked Codex's picture B (codex_picture/irelia-model-B.png, the blades folded behind her back);
  * step 1: Codex's game-grid pack (front + side views, tools/art/pack_irelia_model.py) came back drawn at 16 px a square,
    74 rows crest to soles (codex_model/raw/*-coarse.png), and its own nearest-neighbour 37-row copies were specks; the
    user rejected every cut of them (「全都不及格这能用？」) and pointed at Codex's finer front draft
    (codex_model/raw/irelia-front-B.png, ~14 px squares, 89 rows): 「这个就做的挺好的 为什么不能慢慢的按照这个来完美还原呢」
    「按照这版来还原」, 「你可以学泽丽啊 牺牲一点像素 重点做哪里的像素」, 「你可以不画嘴 但是眼睛一定要像刀妹」;
  * first pass: tools/art/restore_irelia.py (the head at 1.3x the body's scale, every square the material most of its
    picture pixels belong to and that material's commonest shade, then tidied);
  * then hand-finished square by square over that pass and the picture (on the same grid): the silver tiara diamond, a
    rounded hair dome with its blue sheen, the breastplate's red heart and cyan collar gem, the tabard lit on its left,
    the far sleeve and the boots shaded, the outline closed; v3 (「背后的刀刃目前看起来太模糊」「两个手臂也是歪的 手指也没画」
    「右腿是歪的」): crisp crescent blades, straight arms and legs, fingers, star knee guards, no mouth;
  * the eyes (「眼睛还是太怪」, then the user: 「整个身体按照现在让codex精修一版可以让你描的吧」): Codex redrew the whole sprite
    on the 26-px grid (tools/art/pack_irelia_grid.py, codex_grid/); its own 1x copies were specks again, its raw drafts
    drawn at ~15 px squares (take B: 86 x 44 read back, blade tips to soles);
  * the whole sprite traced from take B (the user on the old body: 「身体还是一塌糊涂吧 细节太差了 各种模型变形」): every
    game square decided by hand from the 2 x 2 read-back squares under it (read-back row 2r+2, column 2c - the phase with
    the fewest split squares), no vote and no average: take B's proportions (head, arms angled out, the long hair down to
    the knees, short navy legs, big boots), the three crescent blades each a red body with a white edge and its own
    outline, the silver blade and the lower blade with its 2x2 cyan gem, the breastplate's red heart and collar gem, the
    tabard (white edge, red, dark red) with an ink line off the near hip's red-and-white plates, straight arms with a
    white band, red guard and white wrist, hands with two finger tips, star knee guards, boots with white ankle bands and
    toe caps; the face six squares wide: brows slanting down to the nose, a black liner over one row of cyan iris with
    the white in the outer corners, no mouth; take B's own royal blues for the hair and the leggings (palette.json
    N n m h H). 42 rows from the blade tips to the soles, 22 wide, 20 colours.
The side-on view for the actions is still to come (step 2's pack).
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "irelia")
TABLE = os.path.join(SRC, "design42", "irelia42.txt")
PALETTE = os.path.join(SRC, "design42", "palette.json")
PICTURE = os.path.join(SRC, "codex_model", "raw", "irelia-front-B.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "irelia_native.png")
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3
PEERS = ["zeri", "gwen", "syndra", "seraphine", "xayah", "akali"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def table():
    pal = json.load(open(lp(PALETTE), encoding="utf-8"))
    rows = [r.rstrip("\n") for r in open(lp(TABLE), encoding="utf-8") if r.strip("\n")]
    a = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == ".":
                continue
            if ch not in pal:
                raise SystemExit(f"row {y} column {x}: letter {ch!r} is not in the palette")
            a[y, x, :3] = [int(pal[ch][i:i + 2], 16) for i in (1, 3, 5)]
            a[y, x, 3] = 255
    return a


def canvas(fig):
    ys, xs = np.nonzero(fig[..., 3])
    fig = fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def peer(name):
    im = Image.open(lp(os.path.join(ROOT, "assets", "source", "native", f"{name}_native.png"))).convert("RGBA")
    if im.width == 1024:
        im = im.resize((128, 128), Image.NEAREST)
    return np.asarray(im.crop(im.getbbox()))


def sheet(path):
    t = table()
    H, W = t.shape[:2]
    pic = Image.open(lp(PICTURE)).convert("RGBA")
    bg = Image.new("RGBA", pic.size, (205, 205, 205, 255))
    bg.alpha_composite(pic)
    p = bg.crop((190, 105, 850, 1465))
    p = p.resize((int(p.width * H * 8 / p.height), H * 8), Image.LANCZOS)
    big = Image.fromarray(t).resize((W * 8, H * 8), Image.NEAREST)
    peers = [Image.fromarray(t)] + [Image.fromarray(peer(n)) for n in PEERS]
    z = 4
    tall = max(i.height for i in peers) * z
    row2 = sum(i.width * z + 12 for i in peers) + 10
    img = Image.new("RGBA", (max(big.width + p.width + 70 + W * 3, row2), H * 8 + 70 + tall), (205, 205, 205, 255))
    d = ImageDraw.Draw(img)
    img.alpha_composite(big, (10, 24))
    d.text((10, 6), "design 8x", fill=(0, 0, 0, 255))
    img.alpha_composite(p, (big.width + 30, 24))
    d.text((big.width + 30, 6), "picture (irelia-front-B)", fill=(0, 0, 0, 255))
    x, y = big.width + p.width + 50, 24
    d.text((x, 6), "1x 2x 3x", fill=(0, 0, 0, 255))
    for k in (1, 2, 3):
        im = Image.fromarray(t).resize((W * k, H * k), Image.NEAREST)
        img.alpha_composite(im, (x, y))
        y += im.height + 10
    base = H * 8 + 40 + tall
    x = 10
    for i, name in zip(peers, ["irelia"] + PEERS):
        im = i.resize((i.width * z, i.height * z), Image.NEAREST)
        img.alpha_composite(im, (x, base - im.height))
        d.text((x, base + 4), name, fill=(0, 0, 0, 255))
        x += im.width + 12
    img.convert("RGB").save(path)
    print("wrote", path, img.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sheet")
    a = ap.parse_args()
    if a.sheet:
        sheet(a.sheet)
        return
    out = canvas(table())
    colours = len({tuple(p[:3]) for p in out[out[..., 3] > 0]})
    ys, xs = np.nonzero(out[..., 3])
    print(f"design {xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}, {colours} colours, rows {ys.min()}-{ys.max()}")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("same as the committed design:", np.array_equal(old, out))
        return
    Image.fromarray(out).save(lp(OUT))
    print("wrote", OUT)


if __name__ == "__main__":
    main()

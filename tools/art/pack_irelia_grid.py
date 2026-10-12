#!/usr/bin/env python3
"""Irelia's on-grid redraw pack for Codex (assets/source/irelia/GRID_PROMPTS.md): the whole sprite drawn again at game
size, square by square on a fixed 26-px grid (Gwen's geometry: 1024 x 1536, 39 x 59 squares), keeping the layout of the
current design.

    python tools/art/pack_irelia_grid.py --out dist/irelia_packs/irelia_grid_pack

Why (2026-10-11): the 42-row design (design42/irelia42.txt) is Codex's front draft (codex_model/raw/irelia-front-B.png)
restored square by square and finished by hand; the user: 「修的挺好的 细节部分可以做更好一点」, then on the details -
「眼睛还是太怪」「背后的刀刃目前看起来太模糊」「两个手臂也是歪的 手指也没画」「右腿是歪的」 - and proposed: 「整个身体按照现在让codex
精修一版可以让你描的吧？」. The skill's way for that (art-spec "A muddy design"): Codex redraws the sprite on the game grid
with the current sprite as the size/pose/place to keep; I read it back square for square.
  1_current_grid.png     the current design at 26 px a square with a yellow measuring grid (size, proportions, pose, place)
  2_picture.png          Codex's front draft the design restores (the look, the details)
  3_league_face.png      League's in-game model, her face (local render, never committed): the EYES
  4_example_picture.png  Gwen's on-grid delivery (Codex, approved) at 26 px a square: the way of working
  5_example_sprite.png   the same at 1x enlarged 8x
  6_quality_bar.png      heroes the user approved, 8x on one feet line
  current_1x.png         the current design on the 39 x 59 canvas at 1x
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "irelia")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
PAL = json.load(open(os.path.join(SRC, "design42", "palette.json")))
LEAGUE_FACE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ir_work", "eyes", "front.png")
LEAGUE_CROP = (1050, 180, 1250, 340)
SQ = 26
COLS, ROWS = 39, 59
TOP, SOLE = 9, 50          # the blade tips on row 9, the soles on row 50: 42 rows
MID = 19                   # the feet's middle column


def table():
    rows = [r.rstrip("\n") for r in open(os.path.join(SRC, "design42", "irelia42.txt"), encoding="utf-8") if r.strip("\n")]
    a = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL:
                a[y, x, :3] = [int(PAL[ch][i:i + 2], 16) for i in (1, 3, 5)]
                a[y, x, 3] = 255
    return a


def logical(a):
    """The design on the 39 x 59 canvas: its top on TOP, the middle of its feet (the lowest three rows) on MID."""
    ys, xs = np.nonzero(a[..., 3])
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((a[-3:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    x0 = int(round(MID - mid))
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[TOP:TOP + a.shape[0], x0:x0 + a.shape[1]] = a
    assert TOP + a.shape[0] - 1 == SOLE, a.shape
    return can, x0


def big(can):
    img = Image.new("RGBA", (1024, 1536), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can).resize((COLS * SQ, ROWS * SQ), Image.NEAREST))
    d = ImageDraw.Draw(img)
    for c in range(COLS + 1):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(ROWS + 1):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(0, ROWS, 5):
        d.text((2, r * SQ + 6), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 5):
        d.text((c * SQ + 6, 2), str(c), fill=(0, 0, 200, 255))
    return img


def quality_bar():
    shots = []
    for n in ("gwen", "zeri", "syndra", "seraphine", "xayah"):
        im = Image.open(os.path.join(NATIVE, f"{n}_native.png")).convert("RGBA")
        if im.width == 1024:
            im = im.resize((128, 128), Image.NEAREST)
        shots.append(im.crop(im.getbbox()))
    z, pad = 8, 24
    tall = max(s.height for s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for s in shots) + pad, tall + 2 * pad), (255, 255, 255, 255))
    x = pad
    for s in shots:
        img.alpha_composite(s.resize((s.width * z, s.height * z), Image.NEAREST), (x, pad + tall - s.height * z))
        x += s.width * z + pad
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, "irelia")
    os.makedirs(out, exist_ok=True)
    can, x0 = logical(table())
    big(can).convert("RGB").save(os.path.join(out, "1_current_grid.png"))
    pic = Image.open(os.path.join(SRC, "codex_model", "raw", "irelia-front-B.png")).convert("RGBA")
    bg = Image.new("RGBA", pic.size, (255, 255, 255, 255))
    bg.alpha_composite(pic)
    bg.convert("RGB").save(os.path.join(out, "2_picture.png"))
    lol = Image.open(LEAGUE_FACE).convert("RGB").crop(LEAGUE_CROP)
    lol.resize((lol.width * 4, lol.height * 4), Image.LANCZOS).save(os.path.join(out, "3_league_face.png"))
    shutil.copyfile(os.path.join(ROOT, "assets", "source", "gwen", "codex_grid", "gwen-grid-A.png"),
                    os.path.join(out, "4_example_picture.png"))
    gw = Image.open(os.path.join(ROOT, "assets", "source", "gwen", "codex_grid", "gwen-grid-A_1x.png")).convert("RGBA")
    gw = gw.crop(gw.getbbox())
    gw.resize((gw.width * 8, gw.height * 8), Image.NEAREST).save(os.path.join(out, "5_example_sprite.png"))
    quality_bar().convert("RGB").save(os.path.join(out, "6_quality_bar.png"))
    Image.fromarray(can).save(os.path.join(out, "current_1x.png"))
    shutil.copyfile(os.path.join(SRC, "GRID_PROMPTS.md"), os.path.join(a.out, "GRID_PROMPTS.md"))
    ys, xs = np.nonzero(can[..., 3])
    print(f"current design on the grid: rows {ys.min()}-{ys.max()}, columns {xs.min()}-{xs.max()}")
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()

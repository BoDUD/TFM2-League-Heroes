#!/usr/bin/env python3
"""Malzahar's on-grid redraw pack for Codex (assets/source/malzahar/GRID_PROMPTS.md): picture A-02 drawn again at game
size, plus version B on the same grid.

    python tools/art/pack_malzahar_grid.py --out dist/malzahar_packs/malzahar_grid_pack [--lol D:/WeGameApps/lol]

Why (2026-10-14): step 0 came back as A only (B hit Codex's usage limit) and on ~8-px squares, 130 rows hood tip to
hem instead of 52 rows of 12 px; brought down 2.5x by block votes (design_bard_hd.cut) the eyes, the four diamonds,
the hands and the dagger turned to mush (dist/malzahar_packs/review/malzahar_step0_A.png). The user picked A-02 and
「等额度，Codex 按格子重画」: Codex draws the same figure again on a fixed grid of 19-px squares (1024 x 1536 = 53 x 80
squares), 52 squares from the hood tip (row 12) to the hem (row 63) - PPU 1.5, about 35 game px - and B (League's
float: legs under the robe, toes down) from that redraw. The figure keeps A-02's size on the canvas (its 8-px squares
merge into 19-px ones), so the layout picture is A-02 itself, moved onto the grid.
  1_layout_grid.png    A-02 placed where the redraw goes (hood tip row 12, hem row 63), a yellow measuring grid
  2_look_A02.png       A-02 as Codex delivered it (the look: the user's pick)
  3_league_head.png    League's head render (step 0's refs/3): hood, diamonds, eyes
  4_example_picture.png  league_gwen's on-grid redraw (Codex, approved): the way of working
  5_example_sprite.png   the same at 1x enlarged 8x
  6..9_style_*.png     this pack's heroes at density 1.5, 8x (step 0's style refs)
  10_league_front.png, 11_league_side.png  League's idle (step 0's refs/1, 9): B's hanging legs
"""
import argparse
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "malzahar")
A02 = os.path.join(SRC, "codex_picture", "raw", "A-02.png")
PACK0 = os.path.join(ROOT, "dist", "malzahar_packs", "malzahar_pack0")
SQ = 19                       # Codex's square
COLS, ROWS = 53, 80           # 1007 x 1520 inside the 1024 x 1536 canvas
TOP, HEM = 12, 63             # hood tip on row 12, the hem on row 63: 52 rows
LEFT = 2                      # the near hand's tip on column 2


def clean(path):
    """A-02 with its haze dropped (alpha < 128 or near-white) and cropped to the figure."""
    a = np.array(Image.open(path).convert("RGBA"))
    drop = (a[..., 3] < 128) | (a[..., :3].astype(int).min(-1) > 235)
    a[drop] = 0
    a[~drop, 3] = 255
    im = Image.fromarray(a)
    return im.crop(im.getbbox())


def layout(fig):
    s = (HEM - TOP + 1) * SQ / fig.height
    fig = fig.resize((round(fig.width * s), round(fig.height * s)), Image.LANCZOS)
    img = Image.new("RGBA", (1024, 1536), (255, 255, 255, 255))
    img.alpha_composite(fig, (LEFT * SQ, TOP * SQ))
    d = ImageDraw.Draw(img)
    for c in range(COLS + 1):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(ROWS + 1):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(0, ROWS, 5):
        d.text((2, r * SQ + 4), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 5):
        d.text((c * SQ + 4, 2), str(c), fill=(0, 0, 200, 255))
    for r in (TOP, HEM):
        d.line([(0, r * SQ + SQ // 2), (COLS * SQ, r * SQ + SQ // 2)], fill=(230, 0, 0, 255), width=2)
    print("layout: figure", fig.size, "=", round(fig.width / SQ, 1), "x", round(fig.height / SQ, 1), "squares")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    fig = clean(A02)
    layout(fig).convert("RGB").save(os.path.join(out, "1_layout_grid.png"))
    look = Image.new("RGBA", (fig.width + 80, fig.height + 80), (255, 255, 255, 255))
    look.alpha_composite(fig, (40, 40))
    look.convert("RGB").save(os.path.join(out, "2_look_A02.png"))
    shutil.copyfile(os.path.join(PACK0, "refs", "3_malzahar_league_head.png"), os.path.join(out, "3_league_head.png"))
    gwen = os.path.join(ROOT, "assets", "source", "gwen", "codex_grid")
    shutil.copyfile(os.path.join(gwen, "gwen-grid-A.png"), os.path.join(out, "4_example_picture.png"))
    g = Image.open(os.path.join(gwen, "gwen-grid-A_1x.png")).convert("RGBA")
    g = g.crop(g.getbbox())
    g.resize((g.width * 8, g.height * 8), Image.NEAREST).save(os.path.join(out, "5_example_sprite.png"))
    for i, (name, f) in enumerate([("galio", "galio_hd_idle_x8.png"), ("braum", "braum_lo_idle_x8.png"),
                                   ("zeri", "zeri_lo_idle_x8.png"), ("nidalee", "nidalee_lo_idle_x8.png")]):
        shutil.copyfile(os.path.join(SRC, "style_ref", f), os.path.join(out, f"{6 + i}_style_{name}.png"))
    shutil.copyfile(os.path.join(PACK0, "refs", "1_malzahar_league_front.png"), os.path.join(out, "10_league_front.png"))
    shutil.copyfile(os.path.join(PACK0, "refs", "9_malzahar_league_side.png"), os.path.join(out, "11_league_side.png"))
    shutil.copyfile(os.path.join(SRC, "GRID_PROMPTS.md"), os.path.join(out, "GRID_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

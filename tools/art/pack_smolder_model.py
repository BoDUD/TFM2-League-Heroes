#!/usr/bin/env python3
"""Smolder's step-1 pack for Codex (assets/source/smolder/MODEL_PROMPTS.md): the picked picture B-01 drawn again on
the game grid - the 3/4 front design (idle + pick card; the user: front only, every action from it).

    python tools/art/pack_smolder_model.py --out dist/smolder_packs/smolder_model_pack

Why (2026-10-14): step 0 came back on ~8-px squares (B-01: flames to soles 935 px) with an alpha haze; brought down to
the PPU 1.5 size by cell means (tools/art/design_smolder_cut.py) the eyes, the teeth and the spikes turned to mush.
The user picked B-01 (standing on four legs), kept the size (horn tips to soles 48 squares = 32 game rows, League's
standing height 0.95 of the sitting 51) and 「只画正面，不要侧面」. So Codex draws B-01 again on a fixed grid of 16-px
squares (1536 x 1024 = 96 x 64 squares), the horn tips on row 11, the soles on row 58 (48 rows), the flame tufts above.
The layout picture is B-01 itself scaled onto that grid.
  1_layout_grid.png      B-01 placed where the redraw goes, a yellow measuring grid, red lines on rows 11 and 58
  2_look_B01.png         B-01 as Codex delivered it (the user's pick)
  3_league_head.png      League's head render (step 0's refs/3)
  4_example_picture.png  league_gwen's on-grid redraw (Codex, approved): the way of working
  5_example_sprite.png   the same at 1x enlarged 8x
  6..9_style_*.png       this pack's heroes at density 1.5, 8x (step 0's style refs)
  10_league_stand.png    League's model standing on four legs (step 0's refs/8)
"""
import argparse
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "smolder")
B01 = os.path.join(SRC, "codex_picture", "raw", "smolder-model-B-attempt-01.png")
PACK0 = os.path.join(ROOT, "dist", "smolder_packs", "smolder_pack0")
SQ = 16                        # Codex's square
COLS, ROWS = 96, 64            # 1536 x 1024
TOP, SOLE = 11, 58             # horn tips on row 11, the soles' last row 58: 48 rows (32 game rows at PPU 1.5)
HORN_Y = 97                    # B-01's horn tips (raw px; flames above them reach 49, the crest 130), soles 984


def clean(path):
    """B-01 with its haze dropped (alpha < 128 or near-white), opaque, uncropped."""
    a = np.array(Image.open(path).convert("RGBA"))
    drop = (a[..., 3] < 128) | (a[..., :3].astype(int).min(-1) > 235)
    a[drop] = 0
    a[~drop, 3] = 255
    return Image.fromarray(a)


def layout(im):
    a = np.array(im)
    ys, xs = np.nonzero(a[..., 3])
    sole = ys.max() + 1
    s = (SOLE - TOP + 1) * SQ / (sole - HORN_Y)
    fig = im.crop((xs.min(), ys.min(), xs.max() + 1, sole))
    fig = fig.resize((round(fig.width * s), round(fig.height * s)), Image.LANCZOS)
    x0 = round((COLS * SQ - fig.width) / 2 / SQ) * SQ
    y0 = (SOLE + 1) * SQ - fig.height
    img = Image.new("RGBA", (COLS * SQ, ROWS * SQ), (255, 255, 255, 255))
    img.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(img)
    for c in range(COLS + 1):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(ROWS + 1):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(0, ROWS, 5):
        d.text((2, r * SQ + 3), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 5):
        d.text((c * SQ + 3, 2), str(c), fill=(0, 0, 200, 255))
    for r in (TOP, SOLE):
        d.line([(0, r * SQ + SQ // 2), (COLS * SQ, r * SQ + SQ // 2)], fill=(230, 0, 0, 255), width=2)
    print(f"layout: figure {fig.size} = {fig.width / SQ:.1f} x {fig.height / SQ:.1f} squares, "
          f"columns {x0 // SQ}-{(x0 + fig.width) // SQ}, top row {y0 / SQ:.1f}")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    im = clean(B01)
    layout(im).convert("RGB").save(os.path.join(out, "1_layout_grid.png"))
    fig = im.crop(im.getbbox())
    look = Image.new("RGBA", (fig.width + 80, fig.height + 80), (255, 255, 255, 255))
    look.alpha_composite(fig, (40, 40))
    look.convert("RGB").save(os.path.join(out, "2_look_B01.png"))
    shutil.copyfile(os.path.join(PACK0, "refs", "3_smolder_league_head.png"), os.path.join(out, "3_league_head.png"))
    gwen = os.path.join(ROOT, "assets", "source", "gwen", "codex_grid")
    shutil.copyfile(os.path.join(gwen, "gwen-grid-A.png"), os.path.join(out, "4_example_picture.png"))
    g = Image.open(os.path.join(gwen, "gwen-grid-A_1x.png")).convert("RGBA")
    g = g.crop(g.getbbox())
    g.resize((g.width * 8, g.height * 8), Image.NEAREST).save(os.path.join(out, "5_example_sprite.png"))
    style = os.path.join(ROOT, "assets", "source", "bard", "style_ref")
    for i, (name, f) in enumerate([("galio", "galio_hd_idle_x8.png"), ("braum", "braum_lo_idle_x8.png"),
                                   ("zeri", "zeri_lo_idle_x8.png"), ("nidalee", "nidalee_lo_idle_x8.png")]):
        shutil.copyfile(os.path.join(style, f), os.path.join(out, f"{6 + i}_style_{name}.png"))
    shutil.copyfile(os.path.join(PACK0, "refs", "8_smolder_league_stand.png"), os.path.join(out, "10_league_stand.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

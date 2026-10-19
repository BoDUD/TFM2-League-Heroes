#!/usr/bin/env python3
"""Quinn's on-grid redraw pack for Codex (assets/source/quinn/GRID_PROMPTS.md): the approved idle (Q-1) and ride (R-2)
drawn again on a finer grid for PPU 2.0.

    python tools/art/pack_quinn_grid.py [--out dist/quinn_packs/quinn_grid_pack]

Why (2026-10-19): her actions were approved at PPU 1.3 (the designs 45 x 49 and 67 x 46 squares, 38 game px tall), then
the user: 「还有奎因的像素有点太低了 太多模糊的了 调一下PPU顺便」 and picked PPU 2.0 - 76 rows crest to soles. A design
brought up or down by resampling stays muddy (art-spec "A muddy design"); Codex draws the same figures again on a fixed
grid (league_gwen / league_malzahar's way), each square one flat colour, and rig_quinn.py poses the new designs.
  1_layout_idle.png     the approved idle scaled onto the grid (13-px squares, crest row 21, soles row 96), a yellow
                        measuring grid with its numbers, red lines on rows 21 and 96
  2_look_idle.png       the approved idle (Q-1) at 12x: every part and colour to keep
  3_picture_A.png       step 0's picture A (the look with more detail)
  4_league_head.png     League's Quinn: the face's character
  5_example_picture.png league_gwen's on-grid redraw (Codex, approved), 6_example_sprite.png its 1x at 8x
  7_layout_ride.png     the approved ride scaled onto a landscape grid (13-px squares, rows 3-73)
  8_look_ride.png       the approved ride (R-2) at 10x
  9_picture_R.png       step 0's ride picture
  10..12_style_*.png    pack heroes at density ~2 (their hd_idle, 6x): the quality bar
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "quinn")
PACK1 = "C:/Users/OWNER/AppData/Local/Temp/qn_work/quinn_model_pack"   # step 1's pack (step 0's pictures, League's head)
PPU_OLD, PPU_NEW = 1.3, 2.0
SQ = 13                                   # Codex's square
IDLE = dict(file="idle.png", canvas=(1024, 1536), top=21, left=4)      # portrait: 78 x 118 squares
RIDE = dict(file="ride.png", canvas=(1536, 1024), top=3, left=7)       # landscape: 118 x 78 squares


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith("\\\\?\\") else "\\\\?\\" + p


def design(name):
    return Image.open(lp(os.path.join(SRC, "hd", name))).convert("RGBA")


def size_new(img):
    """A design's figure in new squares (its bbox scaled by PPU_NEW / PPU_OLD)."""
    bb = img.getbbox()
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    k = PPU_NEW / PPU_OLD
    return int(round(w * k)), int(round(h * k)), img.crop(bb)


def layout(spec, out):
    img = design(spec["file"])
    nw, nh, fig = size_new(img)
    W, H = spec["canvas"]
    cols, rows = W // SQ, H // SQ
    big = fig.resize((nw * SQ, nh * SQ), Image.NEAREST)
    can = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    can.alpha_composite(big, (spec["left"] * SQ, spec["top"] * SQ))
    d = ImageDraw.Draw(can)
    for c in range(cols + 1):
        d.line([(c * SQ, 0), (c * SQ, rows * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(rows + 1):
        d.line([(0, r * SQ), (cols * SQ, r * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(0, rows, 5):
        d.text((1, r * SQ + 1), str(r), fill=(200, 0, 0, 255))
    for c in range(0, cols, 5):
        d.text((c * SQ + 2, 1), str(c), fill=(0, 0, 200, 255))
    bottom = spec["top"] + nh - 1
    for r in (spec["top"], bottom):
        d.line([(0, r * SQ + SQ // 2), (cols * SQ, r * SQ + SQ // 2)], fill=(230, 0, 0, 255), width=2)
    can.convert("RGB").save(out)
    print(spec["file"], "->", nw, "x", nh, "squares; rows", spec["top"], "-", bottom, "; columns", spec["left"], "-",
          spec["left"] + nw - 1, "of", cols, "x", rows)
    return nw, nh, bottom


def enlarged(img, z, out):
    bb = img.getbbox()
    f = img.crop(bb)
    bg = Image.new("RGBA", (f.width * z + 40, f.height * z + 40), (235, 235, 235, 255))
    bg.alpha_composite(f.resize((f.width * z, f.height * z), Image.NEAREST), (20, 20))
    bg.convert("RGB").save(out)


def style(hero, out, z=6):
    a = json.load(open(lp(os.path.join(ROOT, "league", "champions", f"league_{hero}#anim.fanim")),
                       encoding="utf-8-sig"))["anims"]
    sh = Image.open(lp(os.path.join(ROOT, "league", "champions", f"league_{hero}#sheet.png"))).convert("RGBA")
    r = a["hd_idle"]["frames"][0]["data"]
    f = sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"])))
    enlarged(f, z, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "quinn_packs", "quinn_grid_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    layout(IDLE, os.path.join(out, "1_layout_idle.png"))
    enlarged(design("idle.png"), 12, os.path.join(out, "2_look_idle.png"))
    shutil.copyfile(os.path.join(PACK1, "1_picture_A.png"), os.path.join(out, "3_picture_A.png"))
    shutil.copyfile(os.path.join(PACK1, "4_head.png"), os.path.join(out, "4_league_head.png"))
    gwen = os.path.join(ROOT, "assets", "source", "gwen", "codex_grid")
    shutil.copyfile(os.path.join(gwen, "gwen-grid-A.png"), os.path.join(out, "5_example_picture.png"))
    g = Image.open(os.path.join(gwen, "gwen-grid-A_1x.png")).convert("RGBA")
    g = g.crop(g.getbbox())
    g.resize((g.width * 8, g.height * 8), Image.NEAREST).save(os.path.join(out, "6_example_sprite.png"))
    layout(RIDE, os.path.join(out, "7_layout_ride.png"))
    enlarged(design("ride.png"), 10, os.path.join(out, "8_look_ride.png"))
    shutil.copyfile(os.path.join(PACK1, "1c_picture_R.png"), os.path.join(out, "9_picture_R.png"))
    for i, hero in enumerate(("braum", "nilah", "mordekaiser")):
        style(hero, os.path.join(out, f"{10 + i}_style_{hero}.png"))
    shutil.copyfile(os.path.join(SRC, "GRID_PROMPTS.md"), os.path.join(out, "GRID_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

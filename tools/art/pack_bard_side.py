#!/usr/bin/env python3
"""Bard's side-view pack for Codex (assets/source/bard/SIDE_PROMPT.md): a FINE side-on draft at the front draft's scale.

    python tools/art/pack_bard_side.py --out dist/bard_packs/bard_side_pack

Step 1's side views came back as the front's head and horn shifted three squares (no body turned), and Codex's own
cut of its fine drafts to the 12-px grid made them muddy; the user wants a true side view (「重画时一起画真正的侧面」).
So Codex draws only the fine draft, the way its raw front (codex_model/raw/front-01.png: ~8-px squares, mane top
y 340, soles y 1391, the feet's middle x 605) was drawn, and tools/art/design_bard_hd.py's cut brings it to the
design's 51 rows here. Pack files:
  1_front_draft.png     Codex's own fine front draft (raw/front-01.png): the look, the scale, the square size
  2_front_in_game.png   that draft as the game design (hd/front.png) at 8x: the proportions to keep
  3_league_side.png     League's model turned side-on facing right (idle, two run frames; local render, never committed)
  4_league_head.png,    League's head and the instrument on the shoulder (pack_bard_picture.py refs/3 and refs/8)
  5_league_instrument.png
  6_size_guide.png      the canvas with the mane-top line (green), the soles line (red) and the feet's middle (blue),
                        the front draft faint behind them: the size to draw
"""
import argparse
import os
import shutil

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "bard")
DRAFT = os.path.join(SRC, "codex_model", "raw", "front-01.png")
DESIGN = os.path.join(SRC, "hd", "front.png")
PACK0 = os.path.join(ROOT, "dist", "bard_packs", "bard_pack0", "refs")
SIDE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ba_work", "side", "league_side.png")
CROWN_Y, SOLE_Y, MID_X = 340, 1392, 600


def on_grey(im):
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg


def guide():
    img = Image.new("RGBA", (1024, 1536), (255, 255, 255, 255))
    ghost = Image.open(DRAFT).convert("RGBA")
    a = ghost.split()[3].point(lambda v: 60 if v >= 128 else 0)
    ghost.putalpha(a)
    img.alpha_composite(ghost, (MID_X - 605, 0))
    d = ImageDraw.Draw(img)
    d.line([(0, CROWN_Y), (1024, CROWN_Y)], fill=(30, 170, 60, 255), width=3)
    d.line([(0, SOLE_Y), (1024, SOLE_Y)], fill=(230, 30, 30, 255), width=3)
    d.line([(MID_X, 0), (MID_X, 1536)], fill=(40, 90, 230, 255), width=3)
    d.text((8, CROWN_Y - 16), "mane top y 340", fill=(30, 170, 60, 255))
    d.text((8, SOLE_Y + 4), "soles y 1392", fill=(230, 30, 30, 255))
    d.text((MID_X + 6, 8), "feet middle x 600", fill=(40, 90, 230, 255))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, "bard")
    os.makedirs(out, exist_ok=True)
    on_grey(Image.open(DRAFT).convert("RGBA")).convert("RGB").save(os.path.join(out, "1_front_draft.png"))
    d = Image.open(DESIGN).convert("RGBA")
    on_grey(d.resize((d.width * 8, d.height * 8), Image.NEAREST)).convert("RGB").save(
        os.path.join(out, "2_front_in_game.png"))
    shutil.copyfile(SIDE, os.path.join(out, "3_league_side.png"))
    Image.open(os.path.join(PACK0, "3_bard_league_head.png")).convert("RGB").save(os.path.join(out, "4_league_head.png"))
    Image.open(os.path.join(PACK0, "8_bard_league_instrument.png")).convert("RGB").save(
        os.path.join(out, "5_league_instrument.png"))
    guide().convert("RGB").save(os.path.join(out, "6_size_guide.png"))
    shutil.copyfile(os.path.join(SRC, "SIDE_PROMPT.md"), os.path.join(out, "SIDE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

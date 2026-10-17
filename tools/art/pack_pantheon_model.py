#!/usr/bin/env python3
"""Pantheon's step-1 pack for Codex (assets/source/pantheon/MODEL_PROMPTS.md): the picked picture A redrawn on the game's
own grid (PPU 1.5, 40 game rows from the helmet's top to the soles).

    python tools/art/pack_pantheon_model.py [--out %TEMP%/pn_work/pantheon_model_pack]

The user's pick, 2026-10-16: 「选A 40尺寸 PPU1.5」. Picture A read back (tools/art/design_pantheon_hd.py, 153 x 162
squares, the helmet's top on row 26) and brought to 1.5 squares a game pixel at 40 rows by pixel_down.pixelate (what the
size sheet showed) is 68 x 72 squares - and muddy: the visor's slit gone, the crest in pieces, the outline broken (the
skill's "A muddy design": back to the image model for an on-grid redraw). Codex redraws it with the image generator at
PX px a square on a 1024 square canvas, the auto-shrunk one as the size and place to keep.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png (Codex's picture A), 2_target_auto.png (the auto-shrunk
design at PX on the canvas), 3_layout.png (the same with the helmet-top, soles and grid lines), 4_helmet.png (A's head
4x), style/5..8 (the pack's PPU heroes' hd_idle at 8x: league_katarina and league_jayce at 1.5, league_smolder 1.5,
league_garen 1.9).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "pantheon")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "pn_work")
PX = 12                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960            # the soles' bottom edge on the canvas
HELM_ROW = 12           # the helmet's top row in the 68 x 72 design (the crest above it)
STYLE = {"5_style_katarina.png": "katarina", "6_style_jayce.png": "jayce", "7_style_smolder.png": "smolder",
         "8_style_garen.png": "garen"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def cut(hero, out):
    """Frame 0 of the hero's hd_idle at 8x (one square = one dense pixel), on grey."""
    anims = json.load(open(lp(os.path.join(CHAMPS, f"league_{hero}#anim.fanim")), encoding="utf-8-sig"))["anims"]
    f = anims["hd_idle"]["frames"][0]["data"]
    sheet = Image.open(lp(os.path.join(CHAMPS, f"league_{hero}#sheet.png"))).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), (225, 225, 225, 255))
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "pantheon_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A_ppu15.png"))).convert("RGBA"))
    h, w = d.shape[:2]
    x0 = (CANVAS - w * PX) // 2
    y0 = SOLE_Y - h * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(d, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target_auto.png"))
    g = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    g.alpha_composite(can)
    dr = ImageDraw.Draw(g)
    for x in range(x0 % PX, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(y0 % PX, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    helm = y0 + HELM_ROW * PX
    dr.line([(0, helm), (CANVAS, helm)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), f"green: helmet top y {helm}   red: soles y {SOLE_Y}   one square = {PX} px   "
                      f"{w} x {h} squares", fill=(40, 40, 40, 255))
    g.convert("RGB").save(os.path.join(out, "3_layout.png"))
    pic = os.path.join(SRC, "codex_picture", "pantheon-picture", "pantheon-A.png")
    shutil.copyfile(lp(pic), os.path.join(out, "1_picked_A.png"))
    full = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    head = full[:60, 55:125]
    hb = Image.new("RGBA", (head.shape[1] * 4, head.shape[0] * 4), (225, 225, 225, 255))
    hb.alpha_composite(Image.fromarray(up(head, 4)))
    hb.convert("RGB").save(os.path.join(out, "4_helmet.png"))
    for name, hero in STYLE.items():
        cut(hero, os.path.join(out, "style", name))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"design {w}x{h} at ({x0},{y0}), helmet top y {helm}, soles y {SOLE_Y} -> {zp}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ziggs's step-1 pack for Codex (assets/source/ziggs/MODEL_PROMPTS.md): picture A (League's idle, both bombs held
out wide) redrawn on the game's own grid (PPU 1.5).

    python tools/art/pack_ziggs_model.py [--out %TEMP%/zg_work/ziggs_model_pack]

The user's pick, 2026-10-18: 「用 A（两手张开托炸弹），游戏里 32 像素高」 - 48 squares from the helmet's top to the soles
(32 game rows x PPU 1.5), the head as drawn (helmet top to the beard's bottom ~ half his height, a yordle). The guide:
A read back on its own grid (tools/art/design_ziggs_hd.py, 114 x 89) brought down whole by pixel_down.pixelate to 48
rows - a rough guide of size, place and proportions (muddy). Codex redraws it twice with the image generator at PX px a
square on a 1024 square canvas.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png (Codex's step-0 picture), 2_target_A.png (the guide at
PX on the canvas), 3_layout_A.png (the same with the helmet-top, beard, ground and grid lines), 4_head.png (A's head 8x),
style/5..8 (pack heroes at 8x: league_jarvaniv, league_swain, league_renata at PPU 1.5, league_corki at 2.2).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ziggs")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "zg_work")
PX = 14                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960            # the soles' bottom edge on the canvas
ROWS = 48               # 32 game rows x PPU 1.5, helmet top to soles
HEAD_SQ = 0             # (unused: the head keeps its share)
# read-back rows (hd/A.png): helmet top, the beard's bottom; the head's columns (the ears in, the bombs out)
HEAD = {"A": (0, 48, 26, 96)}
STYLE = {"5_style_jarvaniv.png": ("jarvaniv", "hd_idle"), "6_style_swain.png": ("swain", "hd_idle"),
         "7_style_renata.png": ("renata", "hd_idle"), "8_style_corki.png": ("corki", "hd_idle")}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def crop(a):
    op = a[..., 3] > 0
    return a[np.ix_(np.any(op, 1), np.any(op, 0))]


def cut(hero, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density), on grey."""
    anims = json.load(open(lp(os.path.join(CHAMPS, f"league_{hero}#anim.fanim")), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(lp(os.path.join(CHAMPS, f"league_{hero}#sheet.png"))).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), (225, 225, 225, 255))
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(out)


def guide(name):
    """-> (guide, helmet-top row in it): the whole picture brought down to ROWS rows (helmet top to soles)."""
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
    top, beard, _, _ = HEAD[name]
    H, W = d.shape[:2]
    k = ROWS / (H - top)
    g, _ = PD.pixelate(d, k, (W / 2, H), PD.edge_colour(d))
    g = crop(g)
    return g, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "ziggs_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    for name in ("A",):
        g, hair = guide(name)
        gh, gw = g.shape[:2]
        x0 = (CANVAS // PX - gw) // 2 * PX
        y0 = SOLE_Y - gh * PX
        can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        can.paste(Image.fromarray(up(g, PX)), (x0, y0))
        can.save(os.path.join(out, f"2_target_{name}.png"))
        lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
        lay.alpha_composite(can)
        dr = ImageDraw.Draw(lay)
        for x in range(0, CANVAS, PX * 5):
            dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
        for y in range(0, CANVAS, PX * 5):
            dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
        top = y0 + hair * PX
        chin = top + round(HEAD[name][1] * gh / 89) * PX
        dr.line([(0, top), (CANVAS, top)], fill=(40, 170, 60, 255), width=3)
        dr.line([(0, chin), (CANVAS, chin)], fill=(60, 110, 230, 255), width=3)
        dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
        dr.text((12, 12), f"{name}: green helmet top y {top}   blue beard bottom y {chin}   red ground y {SOLE_Y}   one square = {PX} px"
                          f"   {gw} x {gh} squares", fill=(40, 40, 40, 255))
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", f"ziggs-{name}.png")), os.path.join(out, f"1_picked_{name}.png"))
        print(name, f"{gw}x{gh} squares at ({x0},{y0}), helmet top y {top}, beard y {chin}, ground y {SOLE_Y}")
    t, c, c0, c1 = HEAD["A"]
    h = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))[t:c + 4, c0 - 4:c1 + 4]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), (225, 225, 225, 255))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Anivia's step-1 pack for Codex (assets/source/anivia/MODEL_PROMPTS.md): pictures A (her idle) and B (the Rebirth
egg) redrawn on the game's own grid (PPU 1.2).

    python tools/art/pack_anivia_model.py [--out %TEMP%/av_work/anivia_model_pack]

The user's picks, 2026-10-17 (tools/art/review_anivia_size.py): 「A 高 44，冰蛋是她身高的一半，头保持原样」 - A 44 game
rows from the crown to the lowest wing tip (53 squares at PPU 1.2, about 80 wide), the egg on its nest half of that
(22 game rows, 26 squares); the proportions as drawn. Each guide is the read-back picture (assets/source/anivia/hd,
tools/art/design_anivia_hd.py)
brought down whole by pixel_down.pixelate to ROWS squares - a rough guide of size, place and pose (muddy). Codex redraws
both with the image generator at PX px a square on 1024 square canvases.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png, 1_picked_B.png (Codex's step-0 drafts, raw/),
2_target_A.png / 2_target_B.png (the guides at PX on the canvas), 3_layout_A.png / 3_layout_B.png (the same with the
crown / egg-top, ground and grid lines), 4_head.png (A's head 8x), style/5..8 (pack heroes at 8x: league_tahmkench,
league_nasus at PPU 1.2, league_swain at 1.5, league_lissandra at 1x).
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

SRC = os.path.join(ROOT, "assets", "source", "anivia")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "av_work")
PX = 11                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 990            # the soles' bottom edge on the canvas (a whole square row: 90 x 11)
ROWS = {"A": 53, "B": 26}   # crown to the lowest wing tip 44, the egg 22 game rows x PPU 1.2
# A's head in the read-back (rows, columns): the crown's spikes to the beak
HEAD_A = (18, 62, 64, 104)
STYLE = {"5_style_tahmkench.png": ("tahmkench", "hd_idle"), "6_style_nasus.png": ("nasus", "hd_idle"),
         "7_style_swain.png": ("swain", "hd_idle"), "8_style_lissandra.png": ("lissandra", "idle")}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


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
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
    H, W = d.shape[:2]
    g, _ = PD.pixelate(d, ROWS[name] / H, (W / 2, H), PD.edge_colour(d))
    op = g[..., 3] > 0
    ys, xs = np.nonzero(op)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "anivia_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    for name in ("A", "B"):
        g = guide(name)
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
        dr.line([(0, y0), (CANVAS, y0)], fill=(40, 170, 60, 255), width=3)
        dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
        dr.text((12, 12), f"{name}: green top y {y0}   red ground y {SOLE_Y}   one square = {PX} px"
                          f"   {gw} x {gh} squares, x {x0}-{x0 + gw * PX}", fill=(40, 40, 40, 255))
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "raw", f"anivia-{name}.png")), os.path.join(out, f"1_picked_{name}.png"))
        print(name, f"{gw}x{gh} squares at ({x0},{y0}), top y {y0}, ground y {SOLE_Y}")
    t, c, c0, c1 = HEAD_A
    h = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))[t:c, c0:c1]
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

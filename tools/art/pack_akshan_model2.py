#!/usr/bin/env python3
"""Akshan's step-1 redo pack for Codex (assets/source/akshan/MODEL_PROMPTS_V2.md): the first step-1 take A-1 redrawn
at the picked size on Codex's own square size.

    python tools/art/pack_akshan_model2.py [--out C:/t/ak_work/akshan_model_pack2]

Round 1 (assets/source/akshan/codex_model, 2026-10-18): asked 15 px squares and 57 rows hair to soles, Codex drew its
usual 10 px squares over the asked 855 px - 83 rows (PPU 2.18). Cut to 57 rows (design_akshan_cut.py, even_cut, the face
kept) the sash, the cape and the gun striped. So round 2 asks for Codex's own 10 px squares and a 570 px figure: the
guide is that 57-row cut (assets/source/akshan/hd/modelA1_cut.png) at 10 px, soles on y 1200 - right in size, place and
pose, striped in places. Writes <out>/ (and <out>.zip): MODEL_PROMPTS_V2.md, 1_picked_A1.png (round 1's A-1, the look),
2_target_A.png (the cut at 10 px on the canvas), 3_layout_A.png (with the hair-top, ground and grid lines), 4_face.png
(A-1's face 8x), style/5..7 (pack heroes at PPU 1.5, 8x).
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

SRC = os.path.join(ROOT, "assets", "source", "akshan")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = "C:/t/ak_work"
PX = 10                 # pixels a square on the canvas (Codex's own square size)
CANVAS = 1254
SOLE_Y = 1200           # the soles' bottom edge on the canvas (a whole square row: 80 x 15)
ROWS = 57               # hair top to soles: 38 game rows x PPU 1.5
CLOSE = {"4_face.png": (16, 46, 24, 58)}   # A-1's head in hd/modelA1.png   # A's face in the read-back (rows, columns)
STYLE = {"5_style_gangplank.png": ("gangplank", "hd_idle"), "6_style_xinzhao.png": ("xinzhao", "hd_idle"),
         "7_style_wukong.png": ("wukong", "hd_idle")}


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


def guide():
    g = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "modelA1_cut.png"))).convert("RGBA"))
    op = g[..., 3] > 0
    ys, xs = np.nonzero(op)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "akshan_model_pack2"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    g = guide()
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    hair = SOLE_Y - ROWS * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target_A.png"))
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(can)
    dr = ImageDraw.Draw(lay)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    dr.line([(0, hair), (CANVAS, hair)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), f"A: green hair top y {hair}   red ground y {SOLE_Y}   one square = {PX} px   {gw} x {gh} squares"
                      f" (gun top y {y0}), x {x0}-{x0 + gw * PX}", fill=(40, 40, 40, 255))
    lay.convert("RGB").save(os.path.join(out, "3_layout_A.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_model", "akshan-model-A-1.png")),
                    os.path.join(out, "1_picked_A1.png"))
    print(f"A {gw}x{gh} squares at ({x0},{y0}), hair top y {hair}, ground y {SOLE_Y}")
    A = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "modelA1.png"))).convert("RGBA"))
    for fname, (t, b, c0, c1) in CLOSE.items():
        h = A[t:b, c0:c1]
        hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), (225, 225, 225, 255))
        hb.alpha_composite(Image.fromarray(up(h, 8)))
        hb.convert("RGB").save(os.path.join(out, fname))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS_V2.md")), os.path.join(out, "MODEL_PROMPTS_V2.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()

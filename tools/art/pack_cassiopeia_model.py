#!/usr/bin/env python3
"""Cassiopeia's step-1 pack for Codex (assets/source/cassiopeia/MODEL_PROMPTS.md): picture A (her idle, the tail lying
out behind her) redrawn on the game's own grid (PPU 1.3).

    python tools/art/pack_cassiopeia_model.py [--out C:/t/cs_work/cassiopeia_model_pack]

The user's pick, 2026-10-18 (tools/art/review_cassiopeia_size.py): 「44 ppu1.3 A」 - A 44 game rows from the crest tip to
the ground = 57 squares at PPU 1.3. The guide is the read-back picture (assets/source/cassiopeia/hd/A.png,
tools/art/design_cassiopeia_hd.py) brought down whole by pixel_down.pixelate to that size - a rough guide of size, place
and pose (muddy). Codex draws on its own 1254 canvas, so the squares are PX px and the figure fills the canvas: "fill
the canvas" then lands on the count (Gangplank's lesson, 2026-10-18).
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png (Codex's step-0 picture), 2_target_A.png (the guide at
PX on the canvas), 3_layout_A.png (the same with the crest-tip, ground and grid lines), 4_face.png (A's head 8x),
style/5..7 (pack heroes near PPU 1.3, 8x: league_nami 1.5 (a tail), league_kalista 1.4, league_malzahar 1.38).
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
from review_cassiopeia_size import BODY_TOP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "cassiopeia")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = "C:/t/cs_work"
PX = 18                 # pixels a square on the canvas
CANVAS = 1254
SOLE_Y = 1206           # the ground (the tail's bottom edge) on the canvas: a whole square row, 67 x 18
ROWS = 57               # crest tip to ground: 44 game rows x PPU 1.3
CLOSE = {"4_face.png": (0, 50, 80, 124)}   # A's head in the read-back (rows, columns)
STYLE = {"5_style_nami.png": ("nami", "hd_idle"), "6_style_kalista.png": ("kalista", "hd_idle"),
         "7_style_malzahar.png": ("malzahar", "hd_idle")}


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
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    H, W = d.shape[:2]
    g, _ = PD.pixelate(d, ROWS / (H - BODY_TOP["A"]), (W / 2, H), PD.edge_colour(d))
    op = g[..., 3] > 0
    ys, xs = np.nonzero(op)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "cassiopeia_model_pack"))
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
    dr.text((12, 12), f"A: green crest tip y {hair}   red ground y {SOLE_Y}   one square = {PX} px   {gw} x {gh} squares"
                      f", x {x0}-{x0 + gw * PX}", fill=(40, 40, 40, 255))
    lay.convert("RGB").save(os.path.join(out, "3_layout_A.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "cassiopeia-A.png")),
                    os.path.join(out, "1_picked_A.png"))
    print(f"A {gw}x{gh} squares at ({x0},{y0}), crest tip y {hair}, ground y {SOLE_Y}")
    A = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    for fname, (t, b, c0, c1) in CLOSE.items():
        h = A[t:b, c0:c1]
        hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), (225, 225, 225, 255))
        hb.alpha_composite(Image.fromarray(up(h, 8)))
        hb.convert("RGB").save(os.path.join(out, fname))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()

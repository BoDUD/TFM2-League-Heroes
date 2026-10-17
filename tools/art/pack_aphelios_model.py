#!/usr/bin/env python3
"""Aphelios's step-1 pack for Codex (assets/source/aphelios/MODEL_PROMPTS.md): the picked picture A redrawn on the game's
own grid (PPU 1.5, 40 game rows from the hair's top to the soles), his head about a quarter of his height; the five
weapons redrawn on the same grid at his scale.

    python tools/art/pack_aphelios_model.py [--out %TEMP%/ap_work/aphelios_model_pack]

The user's picks, 2026-10-16: 「选 A，40 行，第 1 步按游戏格子重画，头放大到约四分之一」. Picture A read back
(tools/art/design_aphelios_hd.py: 64 x 176 squares; the hair's top row HAIR_TOP, the chin CHIN, the head between
HEAD_COLS) is shrunk by an area resample: the head to HEAD_SQ squares (League's A has 14%), the rest (the body,
Calibrum and the raised hand) to the other ROWS - HEAD_SQ, the head set back on its neck - a rough guide of the size,
place and proportions (muddy, with seams). The weapon sheet W at the scale Calibrum has in that guide. Codex redraws
both with the image generator at PX px a square on 1024 square canvases.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png, 2_target_body.png (the guide at PX on the canvas),
3_layout.png (with the hair-top, chin, soles and grid lines), 4_head.png (A's head 8x), 5_picked_W.png (Codex's sheet),
6_target_weapons.png (W's guide on its own canvas), style/7..10 (the pack's PPU heroes' hd_idle at 8x: league_katarina,
league_jayce, league_smolder at 1.5, league_kalista at 1.4).
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

SRC = os.path.join(ROOT, "assets", "source", "aphelios")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ap_work")
PX = 12                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960            # the soles' bottom edge on the canvas
ROWS = 60               # 40 game rows x PPU 1.5, hair top (not the tuft) to soles
HAIR_TOP, CHIN = 30, 51  # in the read-back A (the tuft starts at row 23)
HEAD_TOP = 23           # the head's crop starts at the tuft
HEAD_COLS = (20, 45)    # the head's columns (the rifle is left of them, the raised hand right)
HEAD_SQ = 15            # hair top to chin in the redraw (a quarter of 60; A's own share is 14%)
RIFLE = 130             # Calibrum's rows in A (it sets the weapon sheet's scale)
W_RIFLE = 159           # Calibrum's rows in W
STYLE = {"7_style_katarina.png": "katarina", "8_style_jayce.png": "jayce", "9_style_smolder.png": "smolder",
         "10_style_kalista.png": "kalista"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def crop(a):
    op = a[..., 3] > 0
    return a[np.ix_(np.any(op, 1), np.any(op, 0))]


def shrink(a, k):
    """A plain area resample, alpha cut at 96: pixel_down.pixelate's outline vote ate Calibrum's thin blades (6 squares
    wide in A, 2 here); the guide only carries the size, place and proportions."""
    im = Image.fromarray(a)
    w, h = max(1, round(a.shape[1] * k)), max(1, round(a.shape[0] * k))
    pre = Image.new("RGBA", im.size)
    pre.paste(im, (0, 0))
    r = np.asarray(pre.resize((w, h), Image.BOX)).copy()
    r[..., 3] = np.where(r[..., 3] >= 96, 255, 0)
    return r


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


def on_canvas(a, x0, y0):
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(a, PX)), (x0, y0))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "aphelios_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    A = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA")).copy()
    H = A.shape[0]
    c0, c1 = HEAD_COLS
    head = A[HEAD_TOP:CHIN + 1, c0:c1 + 1].copy()
    rest = A.copy()
    rest[HEAD_TOP:CHIN + 1, c0:c1 + 1] = 0
    kh = HEAD_SQ / (CHIN + 1 - HAIR_TOP)
    kb = (ROWS - HEAD_SQ) / (H - CHIN - 1)
    hs = crop(shrink(head, kh))
    rs = shrink(rest, kb)                       # the whole height kept: row r of A sits at row r * kb
    pad = 30
    guide = np.zeros((rs.shape[0] + pad, rs.shape[1] + pad, 4), np.uint8)
    guide[pad:, pad // 2:pad // 2 + rs.shape[1]] = rs
    # the head's chin on the chin's row of the shrunk body, its middle over the head's middle column
    chin_y = pad + int(round((CHIN + 1) * kb))
    mid_x = pad // 2 + int(round((c0 + c1 + 1) / 2 * kb))
    hy, hx = chin_y - hs.shape[0], mid_x - hs.shape[1] // 2
    sub = guide[hy:hy + hs.shape[0], hx:hx + hs.shape[1]]
    sub[hs[..., 3] > 0] = hs[hs[..., 3] > 0]
    guide = crop(guide)
    gh, gw = guide.shape[:2]
    # soles on SOLE_Y: the guide's bottom row is the soles
    x0 = (CANVAS - gw * PX) // 2 // PX * PX
    y0 = SOLE_Y - gh * PX
    hair_y = SOLE_Y - ROWS * PX
    chin_line = hair_y + HEAD_SQ * PX
    can = on_canvas(guide, x0, y0)
    can.save(os.path.join(out, "2_target_body.png"))
    g = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    g.alpha_composite(can)
    dr = ImageDraw.Draw(g)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    dr.line([(0, hair_y), (CANVAS, hair_y)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, chin_line), (CANVAS, chin_line)], fill=(60, 110, 230, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), f"green: hair top y {hair_y}   blue: chin y {chin_line}   red: soles y {SOLE_Y}   one square = "
                      f"{PX} px   the figure with Calibrum {gw} x {gh} squares", fill=(40, 40, 40, 255))
    g.convert("RGB").save(os.path.join(out, "3_layout.png"))
    # the weapon sheet at the guide's scale (Calibrum as long as in the guide)
    W = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "W.png"))).convert("RGBA"))
    kw = RIFLE * kb / W_RIFLE
    ws = crop(shrink(W, kw))
    wx0 = (CANVAS - ws.shape[1] * PX) // 2 // PX * PX
    wy0 = (CANVAS - ws.shape[0] * PX) // 2 // PX * PX
    on_canvas(ws, wx0, wy0).save(os.path.join(out, "6_target_weapons.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "aphelios-A.png")), os.path.join(out, "1_picked_A.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "aphelios-W.png")), os.path.join(out, "5_picked_W.png"))
    hb_ = A[HEAD_TOP - 2:CHIN + 3, c0 - 2:c1 + 3]
    hb = Image.new("RGBA", (hb_.shape[1] * 8, hb_.shape[0] * 8), (225, 225, 225, 255))
    hb.alpha_composite(Image.fromarray(up(hb_, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for name, hero in STYLE.items():
        cut(hero, os.path.join(out, "style", name))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"body {gw}x{gh} at ({x0},{y0}); hair top y {hair_y}, chin y {chin_line}, soles y {SOLE_Y}; "
          f"weapons {ws.shape[1]}x{ws.shape[0]} at ({wx0},{wy0}) -> {zp}")


if __name__ == "__main__":
    main()

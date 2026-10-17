#!/usr/bin/env python3
"""Renata's step-1 pack for Codex (assets/source/renata/MODEL_PROMPTS.md): the picked picture A redrawn on the game's
own grid (PPU 1.5, 40 game rows from the hair's top to the soles), her head about a quarter of her height; picture C
(Hostile Takeover) redrawn at her scale with one raised arm, and its chemtech machine alone.

    python tools/art/pack_renata_model.py [--out %TEMP%/rn_work/renata_model_pack]

The user's picks, 2026-10-17: 「选 A，40 行，第 1 步按游戏格子重画，头放大到约四分之一，C 去掉多余的手臂、机械单独一张」.
Picture A read back (tools/art/design_renata_hd.py: 44 x 77 squares; the hair's top HAIR_TOP, the chin CHIN, the head
between HEAD_COLS - the raised pistol right of them) is shrunk by an area resample: the head to HEAD_SQ squares from the
hair's top to the chin, the rest to the other rows, the head set back on its neck - a rough guide of the size, place and
proportions (muddy, with seams). Picture C (198 x 213; her hair's top C_HAIR, her soles the last row) shrunk so she
stands ROWS high, on a bigger canvas (the machine rises far above her). Codex redraws with the image generator at PX px
a square (the Yunara / Aphelios way, tools/art/pack_yunara_model.py).
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png, 2_target_body.png (the guide at PX on the canvas),
3_layout.png (hair-top, chin, soles and grid lines), 4_head.png (A's head 8x), 5_picked_C.png (Codex's C),
6_target_ult.png (C's guide on a 1536 canvas), 7_layout_ult.png, style/8..11 (the pack's PPU 1.5 heroes' hd_idle at 8x).
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

SRC = os.path.join(ROOT, "assets", "source", "renata")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "rn_work")
PX = 12                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960            # the soles' bottom edge on the canvas
ROWS = 60               # 40 game rows x PPU 1.5, the hair's top to the soles
HAIR_TOP, CHIN = 0, 13  # the hair's top and the chin (the mask's lower edge) in the read-back A
HEAD_TOP = HAIR_TOP
HEAD_COLS = (9, 28)     # the head's columns (the raised pistol is right of them, cols 33-42)
HEAD_SQ = 15            # hair top to chin in the redraw (a quarter of hair-to-soles; A's own share is 18%)
C_HAIR = 70             # her hair's top in the read-back C (her soles are its last row)
UCANVAS, USOLE = 1536, 1440   # the ult's canvas and soles: the machine rises about 28 squares over her hair
STYLE = {"8_style_katarina.png": "katarina", "9_style_yunara.png": "yunara", "10_style_swain.png": "swain",
         "11_style_nami.png": "nami"}


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
    """A plain area resample, alpha cut at 96; the guide only carries the size, place and proportions."""
    im = Image.fromarray(a)
    w, h = max(1, round(a.shape[1] * k)), max(1, round(a.shape[0] * k))
    r = np.asarray(im.resize((w, h), Image.BOX)).copy()
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
    ap.add_argument("--out", default=os.path.join(TMP, "renata_model_pack"))
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
    head_rows = round((CHIN + 1 - HEAD_TOP) * kh)
    kb = (ROWS - head_rows) / (H - CHIN - 1)
    hs = crop(shrink(head, kh))
    rs = shrink(rest, kb)                       # the whole height kept: row r of A sits at row r * kb
    pad = 40
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
    top_y = SOLE_Y - ROWS * PX
    hair_y = top_y + round((HAIR_TOP - HEAD_TOP) * kh) * PX
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
    dr.text((12, 12), f"green: hair top y {hair_y}   blue: chin y {chin_line}   red: soles y {SOLE_Y}   "
                      f"one square = {PX} px   with the raised pistol {gw} x {gh} squares",
            fill=(40, 40, 40, 255))
    g.convert("RGB").save(os.path.join(out, "3_layout.png"))
    # the ult: C shrunk so she stands ROWS high, soles on USOLE of a UCANVAS square
    C = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "C.png"))).convert("RGBA")).copy()
    kc = ROWS / (C.shape[0] - C_HAIR)
    cs = crop(shrink(C, kc))
    ux0 = (UCANVAS - cs.shape[1] * PX) // 2 // PX * PX
    uy0 = USOLE - cs.shape[0] * PX
    ucan = Image.new("RGBA", (UCANVAS, UCANVAS), (0, 0, 0, 0))
    ucan.paste(Image.fromarray(up(cs, PX)), (ux0, uy0))
    ucan.save(os.path.join(out, "6_target_ult.png"))
    ug = Image.new("RGBA", (UCANVAS, UCANVAS), (255, 255, 255, 255))
    ug.alpha_composite(ucan)
    ud = ImageDraw.Draw(ug)
    for x in range(0, UCANVAS, PX * 5):
        ud.line([(x, 0), (x, UCANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, UCANVAS, PX * 5):
        ud.line([(0, y), (UCANVAS, y)], fill=(205, 205, 205, 255))
    u_hair = USOLE - ROWS * PX
    ud.line([(0, u_hair), (UCANVAS, u_hair)], fill=(40, 170, 60, 255), width=3)
    ud.line([(0, u_hair + HEAD_SQ * PX), (UCANVAS, u_hair + HEAD_SQ * PX)], fill=(60, 110, 230, 255), width=3)
    ud.line([(0, USOLE), (UCANVAS, USOLE)], fill=(230, 40, 40, 255), width=3)
    ud.text((12, 12), f"green: hair top y {u_hair}   blue: chin y {u_hair + HEAD_SQ * PX}   red: soles y {USOLE}   "
                      f"one square = {PX} px   with the machine {cs.shape[1]} x {cs.shape[0]} squares, top y {uy0}",
            fill=(40, 40, 40, 255))
    ug.convert("RGB").save(os.path.join(out, "7_layout_ult.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "renata-A.png")), os.path.join(out, "1_picked_A.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "renata-C.png")), os.path.join(out, "5_picked_C.png"))
    hb_ = A[max(0, HEAD_TOP - 2):CHIN + 3, c0 - 2:c1 + 3]
    hb = Image.new("RGBA", (hb_.shape[1] * 8, hb_.shape[0] * 8), (225, 225, 225, 255))
    hb.alpha_composite(Image.fromarray(up(hb_, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for name, hero in STYLE.items():
        cut(hero, os.path.join(out, "style", name))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"body {gw}x{gh} at ({x0},{y0}); hair top y {hair_y}, chin y {chin_line}, soles y {SOLE_Y}; "
          f"ult {cs.shape[1]}x{cs.shape[0]} at ({ux0},{uy0}), kc {kc:.3f}; kh {kh:.3f} kb {kb:.3f} -> {zp}")


if __name__ == "__main__":
    main()

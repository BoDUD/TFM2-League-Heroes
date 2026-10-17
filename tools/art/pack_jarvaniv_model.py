#!/usr/bin/env python3
"""Jarvan IV's step-1 pack for Codex (assets/source/jarvaniv/MODEL_PROMPTS.md): picture A (League's idle, the lance
upright) redrawn on the game's own grid (PPU 1.5), his head bigger.

    python tools/art/pack_jarvaniv_model.py [--out %TEMP%/jv_work/jarvaniv_model_pack]

The user's picks, 2026-10-17: A, a body of 40 game rows from the helmet's top to the soles (60 squares, the lance not
counted), the head 「放大到约四分之一」. Read back (tools/art/design_jarvaniv_hd.py, one 7 px grid) A's head (helmet top
row 36 to the chin row 64) is 21% of his 133 body rows; the guide gives it HEAD_SQ = 15 squares of 60. The guide: the
whole picture (the lance too) brought down by pixel_down.pixelate to the body's factor (60 - HEAD_SQ squares for the rows
under the chin), the head (helmet top to chin, its own columns) to HEAD_SQ rows and pasted back over it, chin on chin -
a rough guide of size, place and proportions (muddy). Codex redraws it twice with the image generator at PX px a square
on a 1024 square canvas.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png (Codex's step-0 picture), 2_target_A.png (the guide at
PX on the canvas), 3_layout_A.png (the same with the helmet-top, chin, ground and grid lines), 4_head.png (A's head 8x),
style/5..8 (pack heroes at 8x at PPU 1.5: league_pantheon, league_swain, league_jax, and league_garen at 1.9).
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

SRC = os.path.join(ROOT, "assets", "source", "jarvaniv")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "jv_work")
PX = 12                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960            # the soles' bottom edge on the canvas
ROWS = 60               # 40 game rows x PPU 1.5, helmet top to soles (the lance not counted)
HEAD_SQ = 15            # helmet top to chin, about a quarter
# read-back rows (hd/A.png): helmet top, chin; the head's columns (the plume in, the near pauldron's spikes out)
HEAD = {"A": (36, 64, 16, 42)}
STYLE = {"5_style_pantheon.png": ("pantheon", "hd_idle"), "6_style_swain.png": ("swain", "hd_idle"),
         "7_style_jax.png": ("jax", "hd_idle"), "8_style_garen.png": ("garen", "hd_idle")}


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
    """-> (guide, helmet-top row in it): the picture at the body's factor, the head at its own, chin on chin."""
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
    top, chin, c0, c1 = HEAD[name]
    H, W = d.shape[:2]
    kb = (ROWS - HEAD_SQ) / (H - chin)
    kh = HEAD_SQ / (chin - top)
    out = PD.edge_colour(d)
    body, (bx, by) = PD.pixelate(d, kb, (W / 2, H), out)
    head_src = np.zeros_like(d[top:chin, c0:c1])
    part = d[top:chin, c0:c1]
    head_src[part[..., 3] > 0] = part[part[..., 3] > 0]
    head, (hx, hy) = PD.pixelate(head_src, kh, ((c1 - c0) / 2, chin - top), out)
    # the chin's middle in the body frame, then the head's bottom-middle on it
    cx = (c0 + c1) / 2
    gx, gy = int(round((cx - W / 2) * kb + bx)), int(round((chin - H) * kb + by))
    x0, y0 = gx - hx, gy - hy
    lo_x, lo_y = min(0, x0), min(0, y0)
    g = np.zeros((max(body.shape[0], y0 + head.shape[0]) - lo_y, max(body.shape[1], x0 + head.shape[1]) - lo_x, 4),
                 np.uint8)
    g[-lo_y:-lo_y + body.shape[0], -lo_x:-lo_x + body.shape[1]] = body
    hh = g[y0 - lo_y:y0 - lo_y + head.shape[0], x0 - lo_x:x0 - lo_x + head.shape[1]]
    hh[head[..., 3] > 0] = head[head[..., 3] > 0]
    op = g[..., 3] > 0
    ys, xs = np.nonzero(op)
    g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return g, y0 - lo_y - ys.min()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "jarvaniv_model_pack"))
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
        chin = top + HEAD_SQ * PX
        dr.line([(0, top), (CANVAS, top)], fill=(40, 170, 60, 255), width=3)
        dr.line([(0, chin), (CANVAS, chin)], fill=(60, 110, 230, 255), width=3)
        dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
        dr.text((12, 12), f"{name}: green helmet top y {top}   blue chin y {chin}   red ground y {SOLE_Y}   one square = {PX} px"
                          f"   {gw} x {gh} squares", fill=(40, 40, 40, 255))
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", f"jarvaniv-{name}.png")), os.path.join(out, f"1_picked_{name}.png"))
        print(name, f"{gw}x{gh} squares at ({x0},{y0}), helmet top y {top}, chin y {chin}, ground y {SOLE_Y}")
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

#!/usr/bin/env python3
"""Swain's step-1 pack for Codex (assets/source/swain/MODEL_PROMPTS.md): pictures A (his idle) and B (Demonic Ascension)
redrawn on the game's own grid (PPU 1.5), his head bigger.

    python tools/art/pack_swain_model.py [--out %TEMP%/swa_work/swain_model_pack]

The user's picks, 2026-10-17: 40 game rows from the hair's top to the soles (60 squares), the head 「加大到约 1/4」, the
wings as drawn. Read back (tools/art/design_swain_hd.py, one 7 px grid) A's head (hair top row 0 to the chin row 18) is
15% of his 122 rows; the guides give it HEAD_SQ = 15 squares of 60. B is the same man on the same scale (hair top row 22,
chin 40, soles 146): everything of B - the wings too - takes A's body factor, so the demon's wings keep the size the
user saw at 40 in tools/art/review_swain_size.py. Each guide: the whole picture brought down by pixel_down.pixelate to
the body's factor (60 - HEAD_SQ squares for the rows under the chin), the head (hair top to chin, its own columns) to
HEAD_SQ rows and pasted back over it, chin on chin, on the face's column - a rough guide of size, place and proportions
(muddy, the collar round the chin doubled). Codex redraws both with the image generator at PX px a square on 1024
square canvases.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png, 1_picked_B.png (Codex's step-0 pictures),
2_target_A.png / 2_target_B.png (the guides at PX on the canvas), 3_layout_A.png / 3_layout_B.png (the same with the
hair-top, chin, ground and grid lines), 4_head.png (A's head 8x), style/5..8 (pack heroes at 8x at PPU 1.5:
league_pantheon, league_katarina, league_morgana (wings), league_vladimir at 1.8).
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

SRC = os.path.join(ROOT, "assets", "source", "swain")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "swa_work")
PX = 12                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960            # the soles' bottom edge on the canvas
ROWS = 60               # 40 game rows x PPU 1.5, hair top to soles
HEAD_SQ = 15            # hair top to chin, about a quarter
# read-back rows (hd/{A,B}.png): hair top, chin; the head's columns
HEAD = {"A": (0, 18, 22, 54), "B": (22, 40, 74, 104)}
STYLE = {"5_style_pantheon.png": ("pantheon", "hd_idle"), "6_style_katarina.png": ("katarina", "hd_idle"),
         "7_style_morgana.png": ("morgana", "hd_idle"), "8_style_vladimir.png": ("vladimir", "hd_idle")}


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
    """-> (guide, hair-top row in it): the picture at the body's factor, the head at its own, chin on chin."""
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
    ap.add_argument("--out", default=os.path.join(TMP, "swain_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    for name in ("A", "B"):
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
        dr.text((12, 12), f"{name}: green hair top y {top}   blue chin y {chin}   red ground y {SOLE_Y}   one square = {PX} px"
                          f"   {gw} x {gh} squares", fill=(40, 40, 40, 255))
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", f"swain-{name}.png")), os.path.join(out, f"1_picked_{name}.png"))
        print(name, f"{gw}x{gh} squares at ({x0},{y0}), hair top y {top}, chin y {chin}, ground y {SOLE_Y}")
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

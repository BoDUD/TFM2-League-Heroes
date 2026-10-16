#!/usr/bin/env python3
"""Urgot's step-1 pack for Codex (assets/source/urgot/MODEL_PROMPTS.md): the picked picture A redrawn on the game's own
grid (PPU 1.5, 42 game px from the cannon's top to the leg tips = 63 squares), his head a little bigger.

    python tools/art/pack_urgot_model.py [--out %TEMP%/ur_work/urgot_model_pack]

The user's picks, 2026-10-16: 「选 A，炮顶到腿尖 42 px，PPU 1.5，第 1 步按游戏格子重画」. Codex's picture A (1254 px,
squares of ~5 px, the figure ~1180 px tall) is shrunk by an area resample to ROWS squares: the head (the box HEAD in
the picture's pixels, bald top to the mask's chin) to HEAD_SQ squares (A's own head is ~9% of the height: 6 squares,
too few for the eye and the mask), pasted back with its chin on the chin's row; the rest as it is - a rough guide of the
size, place and proportions (muddy). Codex redraws it with the image generator at PX px a square on a 1024 canvas.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png, 2_target_body.png (the guide at PX on the canvas),
3_layout.png (with the cannon-top, chin and leg-tip lines and the grid), 4_head.png (A's head 4x), style/5..8 (the
pack's PPU 1.5 heroes' hd_idle at 8x: league_drmundo, league_pantheon, league_jayce, league_smolder).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SRC = os.path.join(ROOT, "assets", "source", "urgot")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ur_work")
PX = 12                  # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960             # the leg tips' bottom edge on the canvas
ROWS = 63                # 42 game px x PPU 1.5, the cannon's top to the leg tips
HEAD = (600, 288, 736, 404)  # A's head in the picture's pixels: x0, y0 (the bald top), x1, y1 (the mask's chin)
HEAD_SQ = 9              # bald top to chin in the redraw (A's own: ~6)
STYLE = {"5_style_drmundo.png": "drmundo", "6_style_pantheon.png": "pantheon", "7_style_jayce.png": "jayce",
         "8_style_smolder.png": "smolder"}


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
    """An area resample (colour weighted by alpha), alpha cut at 96; the guide only carries the size, place and
    proportions."""
    f = a.astype(np.float64)
    al = f[..., 3:] / 255.0
    pre = np.concatenate([f[..., :3] * al, al * 255], axis=2).astype(np.float32)
    w, h = max(1, round(a.shape[1] * k)), max(1, round(a.shape[0] * k))
    s = np.stack([np.asarray(Image.fromarray(pre[..., c]).resize((w, h), Image.BOX)) for c in range(4)], axis=2)
    alpha = s[..., 3]
    rgb = s[..., :3] / np.maximum(alpha[..., None] / 255.0, 1e-6)
    out = np.zeros((h, w, 4), np.uint8)
    op = alpha >= 96
    out[op, :3] = np.clip(rgb[op], 0, 255)
    out[op, 3] = 255
    return out


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
    ap.add_argument("--out", default=os.path.join(TMP, "urgot_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    A = np.asarray(Image.open(lp(os.path.join(SRC, "codex_picture", "urgot-A.png"))).convert("RGBA")).copy()
    A[..., 3] = np.where(A[..., 3] >= 128, 255, 0)
    ys, xs = np.nonzero(A[..., 3])
    fy0, fx0 = ys.min(), xs.min()
    A = A[fy0:ys.max() + 1, fx0:xs.max() + 1].copy()
    hx0, hy0, hx1, hy1 = HEAD[0] - fx0, HEAD[1] - fy0, HEAD[2] - fx0, HEAD[3] - fy0
    k = ROWS / A.shape[0]
    body = shrink(A, k)
    head = crop(shrink(A[hy0:hy1, hx0:hx1], HEAD_SQ / (hy1 - hy0)))
    chin_r, mid_c = int(round(hy1 * k)), int(round((hx0 + hx1) / 2 * k))
    ty, tx = chin_r - head.shape[0], mid_c - head.shape[1] // 2
    sub = body[ty:ty + head.shape[0], tx:tx + head.shape[1]]
    m = head[..., 3] > 0
    sub[m] = head[m]
    guide = crop(body)
    gh, gw = guide.shape[:2]
    x0 = (CANVAS - gw * PX) // 2 // PX * PX
    y0 = SOLE_Y - gh * PX
    top_y = SOLE_Y - ROWS * PX
    chin_y = y0 + chin_r * PX
    head_y = chin_y - HEAD_SQ * PX
    can = on_canvas(guide, x0, y0)
    can.save(os.path.join(out, "2_target_body.png"))
    g = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    g.alpha_composite(can)
    dr = ImageDraw.Draw(g)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    dr.line([(0, top_y), (CANVAS, top_y)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, head_y), (CANVAS, head_y)], fill=(200, 140, 30, 255), width=3)
    dr.line([(0, chin_y), (CANVAS, chin_y)], fill=(60, 110, 230, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), f"green: cannon top y {top_y}   orange: bald top y {head_y}   blue: chin y {chin_y}   red: leg tips "
                      f"y {SOLE_Y}   one square = {PX} px   the figure {gw} x {gh} squares", fill=(40, 40, 40, 255))
    g.convert("RGB").save(os.path.join(out, "3_layout.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "urgot-A.png")), os.path.join(out, "1_picked_A.png"))
    hb = Image.fromarray(A[hy0 - 20:hy1 + 20, hx0 - 30:hx1 + 30])
    bg = Image.new("RGBA", hb.size, (225, 225, 225, 255))
    bg.alpha_composite(hb)
    bg.convert("RGB").resize((hb.width * 4, hb.height * 4), Image.NEAREST).save(os.path.join(out, "4_head.png"))
    for name, hero in STYLE.items():
        cut(hero, os.path.join(out, "style", name))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"body {gw}x{gh} at ({x0},{y0}); cannon top y {top_y}, bald top y {head_y}, chin y {chin_y}, "
          f"leg tips y {SOLE_Y} -> {zp}")


if __name__ == "__main__":
    main()

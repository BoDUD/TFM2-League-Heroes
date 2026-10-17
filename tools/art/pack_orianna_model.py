#!/usr/bin/env python3
"""Orianna's step-1 pack for Codex (assets/source/orianna/MODEL_PROMPTS.md): the picked picture A redrawn on the game's
own grid (PPU 1.5, 38 game rows from the bun's top to the soles), her head a little bigger, her ball apart and smaller.

    python tools/art/pack_orianna_model.py [--out %TEMP%/or_work/orianna_model_pack]

The user's picks, 2026-10-16: A, 38 rows, 「头稍大」 (the head with the bun about a quarter of her height and a bit
more, Pantheon's share), 「球稍小」 (the ball about 25% of her height; Codex drew 31%, League's is ~22%). Picture A read
back (tools/art/design_orianna_hd.py: the body 81 x 137 squares, bun top to chin rows 0-33; the ball 39 x 42) and
shrunk by pixel_down.pixelate: the head (rows 0-HEAD_ROWS) to HEAD_SQ squares, the body below to the rest of the 57,
stacked on the neck's column - a rough guide of the size, place and proportions (muddy, with a seam at the neck); the
ball to BALL_SQ squares across. Codex redraws both with the image generator at PX px a square on 1024 square canvases.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png (Codex's picture A), 2_target_body.png (the guide at PX
on the canvas), 3_layout.png (the same with the bun-top, chin, soles and grid lines, the ball where it floats),
4_head.png (A's head 8x), 5_target_ball.png (the ball guide on its own canvas), style/6..9 (the pack's PPU heroes'
hd_idle at 8x: league_katarina, league_jayce, league_smolder at 1.5, league_elise 1.8).
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
import design_orianna_hd as DH  # noqa: E402
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "orianna")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "or_work")
PX = 12                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960            # the soles' bottom edge on the canvas
ROWS = 57               # 38 game rows x PPU 1.5, bun top to soles
HEAD_ROWS = 34          # A's bun top to chin (the hair's lowest row) in the read-back body
HEAD_SQ = 16            # the head's squares in the redraw (28% of 57; A's own share is 25%)
BALL_SQ = 14            # the ball across (25% of 57)
STYLE = {"6_style_katarina.png": "katarina", "7_style_jayce.png": "jayce", "8_style_smolder.png": "smolder",
         "9_style_elise.png": "elise"}


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
    out, _ = PD.pixelate(a, k, (a.shape[1] / 2, a.shape[0]), PD.edge_colour(a))
    return crop(out)


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
    ap.add_argument("--out", default=os.path.join(TMP, "orianna_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    body = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    ball = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A_ball.png"))).convert("RGBA"))
    full = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A_full.png"))).convert("RGBA"))
    # the head and the body apart, each to its own share of the 57 rows, stacked on the neck's column
    head = shrink(body[:HEAD_ROWS], HEAD_SQ / HEAD_ROWS)
    rest = shrink(body[HEAD_ROWS:], (ROWS - HEAD_SQ) / (body.shape[0] - HEAD_ROWS))
    kh, kb = HEAD_SQ / HEAD_ROWS, (ROWS - HEAD_SQ) / (body.shape[0] - HEAD_ROWS)
    # the head's middle column stays over the same column of the body (both crops' left edges in A's columns)
    hcols = np.nonzero(np.any(body[:HEAD_ROWS, :, 3] > 0, 0))[0]
    rcols = np.nonzero(np.any(body[HEAD_ROWS:, :, 3] > 0, 0))[0]
    r = (hcols.min() + hcols.max()) / 2
    hx = int(round((r - rcols.min()) * kb - (r - hcols.min()) * kh))
    x_lo = min(0, hx)
    w = max(rest.shape[1], hx + head.shape[1]) - x_lo
    guide = np.zeros((head.shape[0] + rest.shape[0], w, 4), np.uint8)
    guide[head.shape[0]:, -x_lo:-x_lo + rest.shape[1]] = rest
    hh = guide[:head.shape[0], hx - x_lo:hx - x_lo + head.shape[1]]
    hh[head[..., 3] > 0] = head[head[..., 3] > 0]
    gh, gw = guide.shape[:2]
    x0 = (CANVAS - gw * PX) // 2
    y0 = SOLE_Y - gh * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(guide, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target_body.png"))
    # the ball guide on its own canvas, centred
    b = shrink(ball, BALL_SQ / ball.shape[0])
    bc = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    bx0 = (CANVAS // PX - b.shape[1]) // 2 * PX
    by0 = (CANVAS // PX - b.shape[0]) // 2 * PX
    bc.paste(Image.fromarray(up(b, PX)), (bx0, by0))
    bc.save(os.path.join(out, "5_target_ball.png"))
    # the layout: grid, lines, and the ball where A has it (its centre beside her, scaled like her body)
    g = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    g.alpha_composite(can)
    # the ball's centre in A_full (her body's box is A_full's own: she is the larger part), scaled like her body
    bys, bxs = np.array(DH.parts(full[..., 3] > 0)[1]).T
    bcx, bcy = (bxs.min() + bxs.max() + 1) / 2, (bys.min() + bys.max() + 1) / 2
    kx = gw / body.shape[1]
    bx = x0 + int(round(bcx * kx - b.shape[1] / 2)) * PX
    by = SOLE_Y - int(round((full.shape[0] - bcy) * (ROWS / body.shape[0]) + b.shape[0] / 2)) * PX
    g.alpha_composite(Image.fromarray(up(b, PX)), (int(bx), int(by)))
    dr = ImageDraw.Draw(g)
    for x in range(x0 % PX, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(y0 % PX, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    chin = y0 + HEAD_SQ * PX
    dr.line([(0, y0), (CANVAS, y0)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, chin), (CANVAS, chin)], fill=(60, 110, 230, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), f"green: bun top y {y0}   blue: chin y {chin}   red: soles y {SOLE_Y}   one square = {PX} px   "
                      f"{gw} x {gh} squares; the ball {b.shape[1]} x {b.shape[0]} (drawn apart)", fill=(40, 40, 40, 255))
    g.convert("RGB").save(os.path.join(out, "3_layout.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "orianna-A.png")), os.path.join(out, "1_picked_A.png"))
    hb_ = body[:HEAD_ROWS + 2]
    hb = Image.new("RGBA", (hb_.shape[1] * 8, hb_.shape[0] * 8), (225, 225, 225, 255))
    hb.alpha_composite(Image.fromarray(up(hb_, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for name, hero in STYLE.items():
        cut(hero, os.path.join(out, "style", name))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"body {gw}x{gh} at ({x0},{y0}), chin y {chin}, soles y {SOLE_Y}; ball {b.shape[1]}x{b.shape[0]} -> {zp}")


if __name__ == "__main__":
    main()

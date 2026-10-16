#!/usr/bin/env python3
"""Rell's step-1 pack for Codex (assets/source/rell/MODEL_PROMPTS.md): pictures A (mounted) and B (dismounted) redrawn on
the game's own grid (PPU 1.5), her head bigger.

    python tools/art/pack_rell_model.py [--out %TEMP%/rl_work/rell_model_pack]

The user's picks, 2026-10-16: A 44 game rows from the hair's top to the hooves (66 squares), B 40 rows hair to soles (60
squares), 「放大到约 1/4」 for the head. Read back (tools/art/design_rell_hd.py) the hair already makes the head (hair top to
chin) 17% of A and 22% of B, and the face reads too small at game size, so the guides give it 15 squares in A (23% of 66)
and 17 in B (28% of 60) - nearly the same head in both forms (A's rider was drawn smaller than B). Each picture is cut at
the chin (A row CHIN["A"], B row CHIN["B"]): the head shrunk by pixel_down.pixelate to HEAD_SQ squares, the rest to
ROWS - HEAD_SQ, stacked on the head's column - a rough guide of size, place and proportions (muddy, with a seam at the
neck). Codex redraws both with the image generator at PX px a square on 1024 square canvases.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picked_A.png, 1_picked_B.png (Codex's step-0 pictures),
2_target_A.png / 2_target_B.png (the guides at PX on the canvas), 3_layout_A.png / 3_layout_B.png (the same with the
hair-top, chin, ground and grid lines), 4_head.png (B's head 8x), style/5..8 (pack heroes at 8x: league_pantheon and
league_katarina hd_idle at PPU 1.5, league_hecarim's idle, league_kalista's hd_idle).
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

SRC = os.path.join(ROOT, "assets", "source", "rell")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "rl_work")
PX = 12                 # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960            # the hooves' / soles' bottom edge on the canvas
ROWS = {"A": 66, "B": 60}       # 44 / 40 game rows x PPU 1.5
CHIN = {"A": 28, "B": 45}       # the hair's top to the chin in the read-back pictures (hd/A.png, hd/B.png)
HEAD_SQ = {"A": 15, "B": 17}
STYLE = {"5_style_pantheon.png": ("pantheon", "hd_idle"), "6_style_katarina.png": ("katarina", "hd_idle"),
         "7_style_hecarim.png": ("hecarim", "idle"), "8_style_kalista.png": ("kalista", "hd_idle")}


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
    """The head and the rest apart, each to its own share of the rows, the head kept over its own columns."""
    body = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
    ch, rows, hs = CHIN[name], ROWS[name], HEAD_SQ[name]
    kh, kb = hs / ch, (rows - hs) / (body.shape[0] - ch)
    head = shrink(body[:ch], kh)
    rest = shrink(body[ch:], kb)
    hcols = np.nonzero(np.any(body[:ch, :, 3] > 0, 0))[0]
    rcols = np.nonzero(np.any(body[ch:, :, 3] > 0, 0))[0]
    # the face's column (the chin row's opaque middle) stays over the same column of the body
    chin = np.nonzero(body[ch - 1, :, 3] > 0)[0]
    r = (chin.min() + chin.max()) / 2
    hx = int(round((r - rcols.min()) * kb - (r - hcols.min()) * kh))
    x_lo = min(0, hx)
    w = max(rest.shape[1], hx + head.shape[1]) - x_lo
    g = np.zeros((head.shape[0] + rest.shape[0], w, 4), np.uint8)
    g[head.shape[0]:, -x_lo:-x_lo + rest.shape[1]] = rest
    hh = g[:head.shape[0], hx - x_lo:hx - x_lo + head.shape[1]]
    hh[head[..., 3] > 0] = head[head[..., 3] > 0]
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "rell_model_pack"))
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
        chin = y0 + HEAD_SQ[name] * PX
        dr.line([(0, y0), (CANVAS, y0)], fill=(40, 170, 60, 255), width=3)
        dr.line([(0, chin), (CANVAS, chin)], fill=(60, 110, 230, 255), width=3)
        dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
        dr.text((12, 12), f"{name}: green hair top y {y0}   blue chin y {chin}   red ground y {SOLE_Y}   one square = {PX} px"
                          f"   {gw} x {gh} squares", fill=(40, 40, 40, 255))
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", f"rell-{name}.png")), os.path.join(out, f"1_picked_{name}.png"))
        print(name, f"{gw}x{gh} squares at ({x0},{y0}), chin y {chin}, ground y {SOLE_Y}")
    b = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "B.png"))).convert("RGBA"))[:CHIN["B"] + 4, :80]
    hb = Image.new("RGBA", (b.shape[1] * 8, b.shape[0] * 8), (225, 225, 225, 255))
    hb.alpha_composite(Image.fromarray(up(b, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()

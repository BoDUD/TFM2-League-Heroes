#!/usr/bin/env python3
"""Rek'Sai's step-1 pack for Codex (assets/source/reksai/MODEL_PROMPTS.md): pictures A (the surface idle) and B
(burrowed) redrawn on the game's own grid (PPU 1.5, 36 game px from the crest's top to the claw tips = 54 squares), her
head (mouth and fangs) about 1.3x.

    python tools/art/pack_reksai_model.py [--out %TEMP%/rk_work/reksai_model_pack]

The user's picks, 2026-10-17: 「36 像素」「放大到约 1.3 倍」. Codex's picture A (1254 px, squares of ~8 px, crest top to
claw tips ~1130 px) is shrunk by an area resample to ROWS squares: the head (the box HEAD in the picture's pixels: the
helmet's front, the magenta mouth, the fangs and tusks) to HEAD_K times its share, pasted back with its top-left corner
where it was (the head grows forward and down, over the front claw's top); the rest as it is - a rough guide of the size,
place and proportions (muddy). B is brought to A's scale by the crest (the opaque width of each picture's top CREST_PX
rows: Codex drew B's crest ~1.16x A's). Codex redraws both with the image generator at PX px a square on 1024 canvases.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png, 1_picture_B.png, 2_target_A.png / 2_target_B.png
(the guides at PX on the canvas), 3_layout_A.png / 3_layout_B.png (crest top, head and claw-tip lines, the grid),
4_head.png (A's head 4x), style/5..8 (the pack's PPU 1.5-1.8 creatures at 8x: league_rell, league_smolder,
league_elise's spider, league_drmundo).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SRC = os.path.join(ROOT, "assets", "source", "reksai")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "rk_work")
PX = 12                  # pixels a square on the canvas
CANVAS = 1024
SOLE_Y = 960             # the claw tips' (A) / the dirt heap's (B) bottom edge on the canvas
ROWS = 54                # 36 game px x PPU 1.5, the crest's top to the claw tips
HEAD = (930, 540, 1220, 895)  # A's head in the picture's pixels: x0, y0, x1, y1 (helmet front, mouth, fangs, tusks)
HEAD_K = 1.3
CREST_PX = 250           # the top rows of each picture that hold only the crest
STYLE = {"5_style_rell.png": ("rell", "hd_idle"), "6_style_smolder.png": ("smolder", "hd_idle"),
         "7_style_elise_spider.png": ("elise", "hd_c_idle"), "8_style_drmundo.png": ("drmundo", "hd_idle")}


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


def cut(hero, tag, out):
    """Frame 0 of the hero's tag at 8x (one square = one dense pixel), on grey."""
    anims = json.load(open(lp(os.path.join(CHAMPS, f"league_{hero}#anim.fanim")), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(lp(os.path.join(CHAMPS, f"league_{hero}#sheet.png"))).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), (225, 225, 225, 255))
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(out)


def load(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_picture", f"reksai-{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(), (xs.min(), ys.min())


def crest(a):
    cols = np.nonzero(a[:CREST_PX, :, 3].any(axis=0))[0]
    return cols.max() - cols.min() + 1


def place(guide, out, name, lines, note):
    gh, gw = guide.shape[:2]
    x0 = (CANVAS - gw * PX) // 2 // PX * PX
    y0 = SOLE_Y - gh * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(guide, PX)), (x0, y0))
    can.save(os.path.join(out, f"2_target_{name}.png"))
    g = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    g.alpha_composite(can)
    dr = ImageDraw.Draw(g)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    for y, colour in lines:
        dr.line([(0, y), (CANVAS, y)], fill=colour, width=3)
    dr.text((12, 12), note + f"   one square = {PX} px   the figure {gw} x {gh} squares", fill=(40, 40, 40, 255))
    g.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
    return x0, y0, gw, gh


GREEN, ORANGE, BLUE, RED = (40, 170, 60, 255), (200, 140, 30, 255), (60, 110, 230, 255), (230, 40, 40, 255)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "reksai_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    A, (fx0, fy0) = load("A")
    B, _ = load("B")
    hx0, hy0, hx1, hy1 = HEAD[0] - fx0, HEAD[1] - fy0, HEAD[2] - fx0, HEAD[3] - fy0
    k = ROWS / A.shape[0]
    body = shrink(A, k)
    head = crop(shrink(A[hy0:hy1, hx0:hx1], HEAD_K * k))
    ty, tx = int(round(hy0 * k)), int(round(hx0 * k))
    big = np.zeros((max(body.shape[0], ty + head.shape[0]), max(body.shape[1], tx + head.shape[1]), 4), np.uint8)
    big[:body.shape[0], :body.shape[1]] = body
    sub = big[ty:ty + head.shape[0], tx:tx + head.shape[1]]
    m = head[..., 3] > 0
    sub[m] = head[m]
    guide_a = crop(big)
    xa, ya, wa, ha = place(guide_a, out, "A", [(SOLE_Y - ha_ * PX, GREEN) for ha_ in [guide_a.shape[0]]] +
                           [(SOLE_Y - guide_a.shape[0] * PX + ty * PX, ORANGE), (SOLE_Y, RED)],
                           f"A   green: crest top y {SOLE_Y - guide_a.shape[0] * PX}   orange: the head's top "
                           f"y {SOLE_Y - guide_a.shape[0] * PX + ty * PX}   red: claw tips y {SOLE_Y}")
    kb = k * crest(A) / crest(B)
    guide_b = crop(shrink(B, kb))
    xb, yb, wb, hb = place(guide_b, out, "B", [(SOLE_Y - guide_b.shape[0] * PX, GREEN), (SOLE_Y, RED)],
                           f"B   green: crest top y {SOLE_Y - guide_b.shape[0] * PX}   red: the dirt heap's bottom "
                           f"y {SOLE_Y}")
    for n in "AB":
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", f"reksai-{n}.png")), os.path.join(out, f"1_picture_{n}.png"))
    hbx = Image.fromarray(A[max(0, hy0 - 20):hy1 + 20, max(0, hx0 - 30):hx1 + 30])
    bg = Image.new("RGBA", hbx.size, (225, 225, 225, 255))
    bg.alpha_composite(hbx)
    bg.convert("RGB").resize((hbx.width * 3, hbx.height * 3), Image.NEAREST).save(os.path.join(out, "4_head.png"))
    for name, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", name))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"A {wa}x{ha} at ({xa},{ya}), head top row {ty}, head {head.shape[1]}x{head.shape[0]}; "
          f"B {wb}x{hb} at ({xb},{yb}) (scale {kb / k:.2f} of A's) -> {zp}")


if __name__ == "__main__":
    main()

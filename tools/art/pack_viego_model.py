#!/usr/bin/env python3
"""Viego's step 1 pack for Codex: the pictures that go with assets/source/viego/MODEL_PROMPTS.md.

    python tools/art/pack_viego_model.py --out <folder> [--league <1_viego_league_front.png>]

From the approved picture A (assets/source/viego/codex_picture/viego-model-A.png, the user's pick 2026-10-11: League's
idle, the glowing green greatsword resting on his far shoulder, the blade pointing up to image right over his head, the
big cross guard behind his head) and the pack's own game sprites (the layout of tools/art/pack_viktor_model.py). Both versions are
TOTAL squares from the top of the crown to the soles; the blade's tip may rise above the crown (the orange line). A
keeps the picture's sword (MAX_W["A"] squares across, guard and blade included), B makes the blade a third shorter so
the sprite is narrower (MAX_W["B"]).
  1_picture.png        picture A on white, cropped
  2_target_A.png       a 1024x1024 canvas (128 x 128 squares at 8x) with the picture's silhouette shrunk to TOTAL
  2_target_B.png       squares crown to soles (grey, the sword lighter): red = the bottom of the soles' row (row 99),
                       blue = the middle column (x 512), green = the crown's top, orange = the highest the blade's tip
                       may reach, purple = the widest the sprite may be (MAX_W squares, centred on the feet)
  3_quality_bar.png    league_talon, league_zed, league_shen, league_xinzhao and league_renekton as they are in the game
                       now (idle, first frame) at 8x on one soles line
  4_head.png           the head (white hair, the teal thorn crown, the face, the collar), enlarged
  5_parts.png          the guard with the gripping hand, the blade, the chest and belt, the far arm, the legs and boots
  6_size_guide.png     the picture shrunk straight to TOTAL rows on the same canvas - only to see what fits where
  7_league.png         with --league: League's render of this stance (Riot material: the pack only, never git)
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase  # noqa: E402

PICTURE = os.path.join(ROOT, "assets", "source", "viego", "codex_picture", "viego-model-A.png")
TOTALS = {"A": 40, "B": 40}      # squares from the crown's top to the soles
TOTAL = TOTALS["A"]
ANTENNA = 5                      # the blade's tip above the crown (squares)
MAX_W = {"A": 48, "B": 40}       # the widest the sprite may be, the sword included
SOLES_ROW, MID_COL, Z = 99, 64, 8
QUALITY = ["talon", "zed", "shen", "xinzhao", "renekton"]
BODY = 868                       # picture A: the crown's top (y 135) to the soles (y 1003)
WINGS = ((297, 19, 640, 440), (760, 19, 1316, 250))  # boxes holding only the sword (drawn lighter)
HEAD_BOX = (600, 110, 810, 320)                        # the crown, the hair, the face, the collar
CROP_BOXES = [(297, 40, 640, 430), (760, 15, 1316, 250), (620, 300, 920, 570), (860, 380, 1010, 640),
              (500, 600, 990, 1005)]


def shortened(pic):
    """Picture A with hard alpha (Codex's soft edges cut at 128)."""
    a = np.array(pic)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    return Image.fromarray(a)


def wing_mask(shape):
    """True where the picture shows the sword (and nothing else) - drawn lighter in the target silhouette."""
    m = np.zeros(shape, bool)
    for x0, y0, x1, y1 in WINGS:
        m[y0:y1, x0:x1] = True
    return m


VERSION = "A"


def drop_specks(img, least=200):
    """Clear opaque islands smaller than `least` pixels ."""
    a = np.array(img)
    m = a[..., 3] > 0
    seen = np.zeros_like(m)
    h, w = m.shape
    for y0, x0 in zip(*np.where(m)):
        if seen[y0, x0]:
            continue
        stack, comp = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(comp) < least:
            for y, x in comp:
                a[y, x, 3] = 0
    return Image.fromarray(a)


def lines(img):
    d = ImageDraw.Draw(img)
    top = (SOLES_ROW + 1 - TOTAL) * Z
    d.line([(0, (SOLES_ROW + 1) * Z), (1023, (SOLES_ROW + 1) * Z)], fill=(230, 30, 30, 255), width=2)
    d.line([(MID_COL * Z, 0), (MID_COL * Z, 1023)], fill=(40, 90, 230, 255), width=2)
    d.line([(0, top), (1023, top)], fill=(30, 170, 60, 255), width=2)
    d.line([(0, top - ANTENNA * Z), (1023, top - ANTENNA * Z)], fill=(245, 140, 20, 255), width=2)
    half = MAX_W[VERSION] * Z // 2
    for x in (MID_COL * Z - half, MID_COL * Z + half):
        d.line([(x, 0), (x, 1023)], fill=(150, 60, 200, 255), width=2)
    return img


def game_size(pic):
    """The picture cropped to its alpha box and shrunk so that he is TOTAL rows crown to soles: (colour, coverage)."""
    return game_size_box(pic, pic)


def game_size_box(pic, ref):
    """game_size of `pic` on the crop box of `ref` (a part keeps its place in the whole)."""
    a = np.asarray(pic).astype(float) / 255
    ys, xs = np.where(np.asarray(ref)[:, :, 3] > 127)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape[:2]
    k = TOTAL / BODY
    gw, gh = max(1, round(w * k)), max(1, round(h * k))
    pre = a[:, :, :3] * a[:, :, 3:4]
    small = [np.asarray(Image.fromarray((pre[:, :, i] * 255).astype(np.uint8)).resize((gw, gh), Image.BOX)) / 255
             for i in range(3)]
    cov = np.asarray(Image.fromarray((a[:, :, 3] * 255).astype(np.uint8)).resize((gw, gh), Image.BOX)) / 255
    return np.dstack(small), cov


def place(cov):
    """Top-left (col, row) on the 128-square canvas: the soles on SOLES_ROW, the middle of the feet on MID_COL
    (the crop box starts ABOVE_CROWN squares above the crown: the blade)."""
    gh, gw = cov.shape
    feet = np.where(cov[-3:].max(0) > 0.5)[0]
    mid = (feet.min() + feet.max()) / 2
    return round(MID_COL - mid), SOLES_ROW + 1 - gh


def canvas_from(cells, x0, y0, bg):
    img = Image.new("RGBA", (128, 128), bg)
    img.alpha_composite(cells, (x0, y0))
    return img.resize((1024, 1024), Image.NEAREST)


def target_size(pic):
    _, cov = game_size(pic)
    x0, y0 = place(cov)
    cells = np.zeros(cov.shape + (4,), np.uint8)
    cells[cov > 0.5] = (150, 150, 150, 255)
    a = np.array(pic)
    a[~wing_mask(a.shape[:2])] = 0
    _, hcov = game_size_box(Image.fromarray(a), pic)
    cells[(cov > 0.5) & (hcov > 0.5)] = (205, 205, 205, 255)
    return lines(canvas_from(Image.fromarray(cells, "RGBA"), x0, y0, (255, 255, 255, 255)))


def size_guide(pic):
    pre, cov = game_size(pic)
    x0, y0 = place(cov)
    rgb = np.where(cov[:, :, None] > 0, pre / np.maximum(cov[:, :, None], 1e-6), 0)
    cells = np.dstack([(rgb * 255).clip(0, 255), np.where(cov > 0.5, 255, 0)]).astype(np.uint8)
    return lines(canvas_from(Image.fromarray(cells, "RGBA"), x0, y0, (255, 255, 255, 255)))


def quality_bar():
    shots = []
    for h in QUALITY:
        sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{h}"))
        f = sp.frames[sp.tag_frames("idle")[0]]
        box = f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox()
        shots.append((h, f.crop(box)))
    pad, label = 24, 28
    tall = max(s.height for _, s in shots) * Z
    w = sum(s.width * Z + pad for _, s in shots) + pad
    img = Image.new("RGBA", (w, tall + 2 * pad + label), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for h, s in shots:
        big = s.resize((s.width * Z, s.height * Z), Image.NEAREST)
        img.alpha_composite(big, (x, pad + tall - big.height))
        d.text((x, pad + tall + 8), f"league_{h} {s.width}x{s.height}", fill=(0, 0, 0, 255))
        x += big.width + pad
    d.line([(0, pad + tall), (w, pad + tall)], fill=(230, 30, 30, 255), width=1)
    return img


def on_white(im, k):
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    return bg.resize((im.width * k, im.height * k), Image.NEAREST)


def crops(pic):
    head = on_white(pic.crop(HEAD_BOX), 3)
    parts = [on_white(pic.crop(b), 2) for b in CROP_BOXES]
    both = Image.new("RGBA", (sum(p.width for p in parts) + 30 * (len(parts) - 1), max(p.height for p in parts)),
                     (255, 255, 255, 255))
    x = 0
    for p in parts:
        both.paste(p, (x, 0))
        x += p.width + 30
    return head, both


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--league", help="League's render (refs/1_viego_league_front.png from the step 0 pack)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    raw = Image.open(PICTURE).convert("RGBA")
    pic = shortened(raw)
    box = pic.getchannel("A").getbbox()
    first = Image.new("RGBA", pic.size, (255, 255, 255, 255))
    first.alpha_composite(pic)
    first.crop((box[0] - 40, box[1] - 40, box[2] + 40, box[3] + 20)).convert("RGB").save(
        os.path.join(args.out, "1_picture.png"))
    global TOTAL, VERSION
    for v in ("B", "A"):
        TOTAL, VERSION = TOTALS[v], v
        target_size(pic).convert("RGB").save(os.path.join(args.out, f"2_target_{v}.png"))
    quality_bar().convert("RGB").save(os.path.join(args.out, "3_quality_bar.png"))
    hard = Image.fromarray(np.where((np.array(raw)[..., 3:] >= 128), np.array(raw), 0).astype(np.uint8))
    head, parts = crops(hard)
    head.convert("RGB").save(os.path.join(args.out, "4_head.png"))
    parts.convert("RGB").save(os.path.join(args.out, "5_parts.png"))
    size_guide(pic).convert("RGB").save(os.path.join(args.out, "6_size_guide.png"))
    if args.league:
        shutil.copy(args.league, os.path.join(args.out, "7_league.png"))
    print("wrote", ", ".join(sorted(os.listdir(args.out))))


if __name__ == "__main__":
    main()

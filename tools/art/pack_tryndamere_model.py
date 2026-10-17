#!/usr/bin/env python3
"""Tryndamere's step 1 pack for Codex: the pictures that go with assets/source/tryndamere/MODEL_PROMPTS.md.

    python tools/art/pack_tryndamere_model.py --out <folder> [--league <1_tryndamere_league_front.png>]

From the approved picture A (assets/source/tryndamere/codex_picture/tryndamere-model-A.png, the user's pick 2026-10-05)
and the pack's own game sprites (pack_sett_model.py's layout):
  1_picture.png       picture A on white, cropped
  2_target_size.png   a 1024x1024 canvas (128 x 128 squares at 8x) with A's silhouette shrunk to game size (grey):
                      red = the bottom of the soles' row (row 99, y 792-799), blue = the middle column (x 512),
                      green = the horn tips (TOTAL squares over the soles), orange / purple = the chin of version A / B
  3_quality_bar.png   league_sett, league_darius, league_aatrox, league_kayn and league_garen as they are in the game now
                      (idle, first frame) at 8x on one soles line
  4_head.png          A's horned helmet and face, enlarged
  5_sword.png         A's greatsword with the hand holding it, and the open free hand, enlarged
  6_size_guide.png    A shrunk straight to game size, on the same canvas - only to see what fits where
  7_league_idle.png   with --league: League's idle render (Riot material: it goes into the pack only, never into git)
The silhouette and the size guide keep A's own proportions (its head is 26% of its height); the prompt asks for the
bigger head of each version.
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

PICTURE = os.path.join(ROOT, "assets", "source", "tryndamere", "codex_picture", "tryndamere-model-A.png")
TOTAL = 42                       # squares from the horn tips to the soles (league_sett / darius 42, league_aatrox 40)
HEAD = {"A": 14, "B": 12}        # squares from the horn tips to the chin
SOLES_ROW, MID_COL, Z = 99, 64, 8
QUALITY = ["sett", "darius", "aatrox", "kayn", "garen"]
HEAD_BOX = (590, 200, 840, 520)  # in picture A: the horn tips to the chin
FIST_BOXES = [(0, 640, 480, 1330), (850, 620, 1020, 880)]   # the sword with its hand; the open free hand


def lines(img):
    d = ImageDraw.Draw(img)
    top = (SOLES_ROW + 1 - TOTAL) * Z
    d.line([(0, (SOLES_ROW + 1) * Z), (1023, (SOLES_ROW + 1) * Z)], fill=(230, 30, 30, 255), width=2)
    d.line([(MID_COL * Z, 0), (MID_COL * Z, 1023)], fill=(40, 90, 230, 255), width=2)
    d.line([(0, top), (1023, top)], fill=(30, 170, 60, 255), width=2)
    for v, col in (("A", (245, 140, 20, 255)), ("B", (150, 60, 200, 255))):
        y = top + HEAD[v] * Z
        d.line([(0, y), (1023, y)], fill=col, width=2)
    return img


def game_size(pic):
    """Picture A cropped to its alpha box and shrunk to TOTAL rows: (premultiplied colour, coverage) at game size."""
    a = np.asarray(pic).astype(float) / 255
    ys, xs = np.where(a[:, :, 3] > 0.5)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape[:2]
    gw, gh = max(1, round(w * TOTAL / h)), TOTAL
    pre = a[:, :, :3] * a[:, :, 3:4]
    small = [np.asarray(Image.fromarray((pre[:, :, i] * 255).astype(np.uint8)).resize((gw, gh), Image.BOX)) / 255
             for i in range(3)]
    cov = np.asarray(Image.fromarray((a[:, :, 3] * 255).astype(np.uint8)).resize((gw, gh), Image.BOX)) / 255
    return np.dstack(small), cov


def place(arr, cov):
    """Top-left (col, row) on the 128-square canvas: the soles on SOLES_ROW, the middle of the feet on MID_COL."""
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
    x0, y0 = place(None, cov)
    m = (cov > 0.5).astype(np.uint8)
    cells = np.zeros(cov.shape + (4,), np.uint8)
    cells[m == 1] = (150, 150, 150, 255)
    return lines(canvas_from(Image.fromarray(cells, "RGBA"), x0, y0, (255, 255, 255, 255)))


def size_guide(pic):
    pre, cov = game_size(pic)
    x0, y0 = place(None, cov)
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


def crops(pic):
    def on_white(im, k):
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        return bg.resize((im.width * k, im.height * k), Image.NEAREST)
    head = on_white(pic.crop(HEAD_BOX), 3)
    fists = [on_white(pic.crop(b), 3) for b in FIST_BOXES]
    both = Image.new("RGBA", (sum(f.width for f in fists) + 30, max(f.height for f in fists)), (255, 255, 255, 255))
    both.paste(fists[0], (0, 0))
    both.paste(fists[1], (fists[0].width + 30, 0))
    return head, both


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--league", help="League's idle render (refs/1_tryndamere_league_front.png from the step 0 pack)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    pic = Image.open(PICTURE).convert("RGBA")
    box = pic.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox()
    first = Image.new("RGBA", pic.size, (255, 255, 255, 255))
    first.alpha_composite(pic)
    first.crop((box[0] - 40, box[1] - 40, box[2] + 40, box[3] + 40)).convert("RGB").save(
        os.path.join(args.out, "1_picture.png"))
    target_size(pic).convert("RGB").save(os.path.join(args.out, "2_target_size.png"))
    quality_bar().convert("RGB").save(os.path.join(args.out, "3_quality_bar.png"))
    head, fists = crops(pic)
    head.convert("RGB").save(os.path.join(args.out, "4_head.png"))
    fists.convert("RGB").save(os.path.join(args.out, "5_sword.png"))
    size_guide(pic).convert("RGB").save(os.path.join(args.out, "6_size_guide.png"))
    if args.league:
        shutil.copy(args.league, os.path.join(args.out, "7_league_idle.png"))
    print("wrote", ", ".join(sorted(os.listdir(args.out))))


if __name__ == "__main__":
    main()

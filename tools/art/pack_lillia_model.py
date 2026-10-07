#!/usr/bin/env python3
"""Lillia's step 1 pack for Codex: the pictures that go with assets/source/lillia/MODEL_PROMPTS.md.

    python tools/art/pack_lillia_model.py --out <folder> [--league <1_lillia_league_idle.png>]

From the approved picture A (assets/source/lillia/codex_picture/lillia-model-A.png, the user's pick 2026-10-07: League's
idle, the fawn body on four legs, the bough held upright in both hands, the dream lantern hanging from its hook at the
upper right) and the pack's own game sprites (pack_renekton_model.py's layout). Both versions are TOTAL squares from
the bough's top (the blossom, her highest point) to the hooves:
  A  the bough as drawn: the picture's 867 px (blossom y 68 to hooves y 935) -> 42 rows, the body (bud y 242 to the
     hooves) about 34;
  B  the bough shortened: its top 4 rows above the bud, the bough and the lantern moved down whole (BOUGH_BOXES shifted),
     the 766 px left -> 42 rows, the body about 38 (a bigger girl, the user found 45-row heroes too big).
  1_picture.png        picture A on white, cropped
  2_target_A.png       a 1024x1024 canvas (128 x 128 squares at 8x) with the picture's silhouette shrunk to version A's
  2_target_B.png       size / B's (grey; the bough and the lantern lighter): red = the bottom of the hooves' row (row 99),
                       blue = the middle column (x 512), green = the top of the bough, orange = the top of the bud
  3_quality_bar.png    league_seraphine, league_gwen, league_renekton, league_khazix and league_twitch as they are in the
                       game now (idle, first frame) at 8x on one soles line
  4_head.png           the head, enlarged
  5_parts.png          the bough's top with the lantern, the hands on the bough, the tail and back, the legs and hooves
  6_size_guide.png     the picture shrunk straight to version A's size, on the same canvas - only to see what fits where
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

PICTURE = os.path.join(ROOT, "assets", "source", "lillia", "codex_picture", "lillia-model-A.png")
TOTAL = 42                       # squares from the bough's top to the hooves, both versions
TOP, BUD, SOLES = 68, 242, 935   # picture A: the blossom's top, the bud's top, the hooves' bottom
BOUGH_BOXES = ((885, 60, 1110, 440), (940, 440, 1110, 545))   # the bough above her hands and the lantern
SHIFT_B = BUD - 4 * (SOLES - BUD) / 38 - TOP                  # B: the bough's top 4 rows above the bud (body 38 rows)
SOLES_ROW, MID_COL, Z = 99, 64, 8
QUALITY = ["seraphine", "gwen", "renekton", "khazix", "twitch"]
HEAD_BOX = (660, 230, 900, 450)  # the bud, the leaf curls, the face
CROP_BOXES = [(885, 60, 1110, 545), (820, 420, 950, 580), (540, 470, 760, 700), (490, 690, 940, 940)]


def hard(pic):
    """Picture A with hard alpha (Codex's soft edges cut at 128)."""
    a = np.array(pic)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    return Image.fromarray(a)


def bough_mask(shape):
    m = np.zeros(shape, bool)
    for x0, y0, x1, y1 in BOUGH_BOXES:
        m[y0:y1, x0:x1] = True
    return m


def version_b(pic):
    """Picture A with the bough and the lantern moved down SHIFT_B px (what is left of the shaft below stays)."""
    a = np.array(pic)
    m = bough_mask(a.shape[:2]) & (a[..., 3] > 0)
    part = np.zeros_like(a)
    part[m] = a[m]
    a[m] = 0
    s = int(round(SHIFT_B))
    moved = np.zeros_like(a)
    moved[s:] = part[:-s]
    out = Image.fromarray(a)
    out.alpha_composite(Image.fromarray(moved))
    return out, moved[..., 3] > 0


def game_size(pic, top):
    """The picture from `top` to the hooves shrunk to TOTAL rows: (colour premultiplied, coverage, crop box)."""
    a = np.asarray(pic).astype(float) / 255
    ys, xs = np.where(np.asarray(pic)[:, :, 3] > 127)
    box = (xs.min(), top, xs.max() + 1, SOLES + 1)
    a = a[box[1]:box[3], box[0]:box[2]]
    h, w = a.shape[:2]
    k = TOTAL / h
    gw, gh = max(1, round(w * k)), TOTAL
    pre = a[:, :, :3] * a[:, :, 3:4]
    small = [np.asarray(Image.fromarray((pre[:, :, i] * 255).astype(np.uint8)).resize((gw, gh), Image.BOX)) / 255
             for i in range(3)]
    cov = np.asarray(Image.fromarray((a[:, :, 3] * 255).astype(np.uint8)).resize((gw, gh), Image.BOX)) / 255
    return np.dstack(small), cov, box


def shrink_mask(mask, box, shape):
    m = mask[box[1]:box[3], box[0]:box[2]].astype(np.uint8) * 255
    return np.asarray(Image.fromarray(m).resize((shape[1], shape[0]), Image.BOX)) > 127


def place(cov):
    """Top-left (col, row) on the 128-square canvas: the hooves on SOLES_ROW, the middle of the hooves on MID_COL."""
    gh, gw = cov.shape
    feet = np.where(cov[-3:].max(0) > 0.5)[0]
    mid = (feet.min() + feet.max()) / 2
    return round(MID_COL - mid), SOLES_ROW + 1 - gh


def lines(img, bud_rows):
    d = ImageDraw.Draw(img)
    top = (SOLES_ROW + 1 - TOTAL) * Z
    d.line([(0, (SOLES_ROW + 1) * Z), (1023, (SOLES_ROW + 1) * Z)], fill=(230, 30, 30, 255), width=2)
    d.line([(MID_COL * Z, 0), (MID_COL * Z, 1023)], fill=(40, 90, 230, 255), width=2)
    d.line([(0, top), (1023, top)], fill=(30, 170, 60, 255), width=2)
    bud = (SOLES_ROW + 1 - bud_rows) * Z
    d.line([(0, bud), (1023, bud)], fill=(245, 140, 20, 255), width=2)
    return img


def canvas_from(cells, x0, y0, bg):
    img = Image.new("RGBA", (128, 128), bg)
    img.alpha_composite(cells, (x0, y0))
    return img.resize((1024, 1024), Image.NEAREST)


def target(pic, light, top):
    _, cov, box = game_size(pic, top)
    x0, y0 = place(cov)
    cells = np.zeros(cov.shape + (4,), np.uint8)
    cells[cov > 0.5] = (150, 150, 150, 255)
    cells[(cov > 0.5) & shrink_mask(light, box, cov.shape)] = (205, 205, 205, 255)
    bud_rows = round(TOTAL * (SOLES + 1 - BUD) / (SOLES + 1 - top))
    return lines(canvas_from(Image.fromarray(cells, "RGBA"), x0, y0, (255, 255, 255, 255)), bud_rows), cov.shape


def size_guide(pic):
    pre, cov, _ = game_size(pic, TOP)
    x0, y0 = place(cov)
    rgb = np.where(cov[:, :, None] > 0, pre / np.maximum(cov[:, :, None], 1e-6), 0)
    cells = np.dstack([(rgb * 255).clip(0, 255), np.where(cov > 0.5, 255, 0)]).astype(np.uint8)
    bud_rows = round(TOTAL * (SOLES + 1 - BUD) / (SOLES + 1 - TOP))
    return lines(canvas_from(Image.fromarray(cells, "RGBA"), x0, y0, (255, 255, 255, 255)), bud_rows)


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
    ap.add_argument("--league", help="League's render (refs/1_lillia_league_idle.png from the step 0 pack)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    pic = hard(Image.open(PICTURE).convert("RGBA"))
    box = pic.getchannel("A").getbbox()
    first = Image.new("RGBA", pic.size, (255, 255, 255, 255))
    first.alpha_composite(pic)
    first.crop((box[0] - 40, box[1] - 40, box[2] + 40, box[3] + 20)).convert("RGB").save(
        os.path.join(args.out, "1_picture.png"))
    light_a = bough_mask(np.asarray(pic).shape[:2]) & (np.asarray(pic)[..., 3] > 0)
    img, shape = target(pic, light_a, TOP)
    img.convert("RGB").save(os.path.join(args.out, "2_target_A.png"))
    print("A", shape[1], "x", shape[0])
    pic_b, light_b = version_b(pic)
    img, shape = target(pic_b, light_b, int(round(TOP + SHIFT_B)))
    img.convert("RGB").save(os.path.join(args.out, "2_target_B.png"))
    print("B", shape[1], "x", shape[0], "shift", round(SHIFT_B))
    quality_bar().convert("RGB").save(os.path.join(args.out, "3_quality_bar.png"))
    head, parts = crops(pic)
    head.convert("RGB").save(os.path.join(args.out, "4_head.png"))
    parts.convert("RGB").save(os.path.join(args.out, "5_parts.png"))
    size_guide(pic).convert("RGB").save(os.path.join(args.out, "6_size_guide.png"))
    if args.league:
        shutil.copy(args.league, os.path.join(args.out, "7_league.png"))
    print("wrote", ", ".join(sorted(os.listdir(args.out))))


if __name__ == "__main__":
    main()

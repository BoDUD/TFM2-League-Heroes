"""Seraphine's step 1 pack for Codex: the pictures that go with assets/source/seraphine/MODEL_PROMPTS.md.

    python tools/art/pack_seraphine_model.py --out dist/seraphine_packs/seraphine_pack1/seraphine \n        [--league <1_seraphine_league_front.png>]

Writes the pictures below into --out, MODEL_PROMPTS.md beside it and the folder above as a zip.

From the approved picture A (assets/source/seraphine/codex_picture/seraphine-model-A.png, the user's pick 2026-10-07: she
stands on her floating stage, one hand at her ear, the pink hair streaming behind) and the pack's own game sprites
(pack_gwen_model.py's layout). The stage is her lowest point, so the soles' row of the canvas is the stage's bottom:
TOTAL squares from the top of her curl to the stage's bottom, her boots standing STAGE squares higher on its deck;
versions 1 / 2 = the head HEAD["1"] / HEAD["2"] squares from the curl's top to the chin (the picture's head is 1/5 of
her: the game wants a bigger one).
  1_picture.png       picture A on white, cropped
  2_target_size.png   a 1024x1024 canvas (128 x 128 squares at 8x) with the picture's silhouette shrunk to game size
                      (grey, the stage lighter): red = the bottom of the stage's row (row 99, y 792-799), cyan = the
                      bottom of her soles on the deck, blue = the middle column (x 512), green = the top (the curl),
                      orange / purple = the chin of version 1 / 2
  3_quality_bar.png   league_gwen, league_nami, league_janna, league_sona and league_samira as they are in the game now
                      (idle, first frame) at 8x on one soles line
  4_head.png          A's head, enlarged
  5_parts.png         A's crystal fins, the top with the sleeves, belt and skirt, the legs and boots, the stage, enlarged
  6_size_guide.png    the picture shrunk straight to game size, on the same canvas - only to see what fits where
  7_league.png        with --league: League's render of this stance (Riot material: it goes into the pack only, never git)
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

PICTURE = os.path.join(ROOT, "assets", "source", "seraphine", "codex_picture", "seraphine-model-A.png")
TOTAL = 46                       # squares from the curl's top to the stage's bottom
STAGE = 7                        # squares from the soles (on the deck) down to the stage's bottom
HEAD = {"1": 12, "2": 10}        # squares from the curl's top to the chin
SOLES_ROW, MID_COL, Z = 99, 64, 8
QUALITY = ["gwen", "nami", "janna", "sona", "samira"]
BODY = 992                       # picture A: the curl's top (y 18) to the stage's bottom (y 1010)
DECK_Y = 840                     # picture A: the stage's deck (everything below it is the stage)
HEAD_BOX = (690, 10, 960, 215)                     # the curl and the hair to the chin, the hand at her ear
CROP_BOXES = [(605, 135, 775, 250), (700, 210, 990, 470), (735, 470, 940, 870), (530, 820, 1050, 1012)]


def hard(pic):
    """The picture with hard alpha (Codex's soft edges cut at 128)."""
    a = np.array(pic)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    return Image.fromarray(a)


def lines(img):
    d = ImageDraw.Draw(img)
    top = (SOLES_ROW + 1 - TOTAL) * Z
    d.line([(0, (SOLES_ROW + 1) * Z), (1023, (SOLES_ROW + 1) * Z)], fill=(230, 30, 30, 255), width=2)
    d.line([(MID_COL * Z, 0), (MID_COL * Z, 1023)], fill=(40, 90, 230, 255), width=2)
    d.line([(0, top), (1023, top)], fill=(30, 170, 60, 255), width=2)
    d.line([(0, (SOLES_ROW + 1 - STAGE) * Z), (1023, (SOLES_ROW + 1 - STAGE) * Z)], fill=(20, 190, 210, 255), width=2)
    for v, col in (("1", (245, 140, 20, 255)), ("2", (150, 60, 200, 255))):
        y = top + HEAD[v] * Z
        d.line([(0, y), (1023, y)], fill=col, width=2)
    return img


def game_size(pic):
    """The picture cropped to its alpha box and shrunk so that she is TOTAL rows: (colour, coverage)."""
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
    x0, y0 = place(cov)
    cells = np.zeros(cov.shape + (4,), np.uint8)
    cells[cov > 0.5] = (150, 150, 150, 255)
    a = np.array(pic)
    a[:DECK_Y] = 0
    _, scov = game_size_box(Image.fromarray(a), pic)
    cells[(cov > 0.5) & (scov > 0.5)] = (205, 205, 205, 255)
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
    ap.add_argument("--league", help="League's render (refs/1_seraphine_league_front.png from the step 0 pack)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    raw = Image.open(PICTURE).convert("RGBA")
    pic = hard(raw)
    box = pic.getchannel("A").getbbox()
    first = Image.new("RGBA", pic.size, (255, 255, 255, 255))
    first.alpha_composite(pic)
    first.crop((box[0] - 40, box[1] - 40, box[2] + 40, box[3] + 20)).convert("RGB").save(
        os.path.join(args.out, "1_picture.png"))
    target_size(pic).convert("RGB").save(os.path.join(args.out, "2_target_size.png"))
    quality_bar().convert("RGB").save(os.path.join(args.out, "3_quality_bar.png"))
    head, parts = crops(pic)
    head.convert("RGB").save(os.path.join(args.out, "4_head.png"))
    parts.convert("RGB").save(os.path.join(args.out, "5_parts.png"))
    size_guide(pic).convert("RGB").save(os.path.join(args.out, "6_size_guide.png"))
    if args.league:
        shutil.copy(args.league, os.path.join(args.out, "7_league.png"))
    print("wrote", ", ".join(sorted(os.listdir(args.out))))
    root = os.path.dirname(os.path.abspath(args.out))
    shutil.copyfile(os.path.join(ROOT, "assets", "source", "seraphine", "MODEL_PROMPTS.md"),
                    os.path.join(root, "MODEL_PROMPTS.md"))
    print("written", shutil.make_archive(root, "zip", root))


if __name__ == "__main__":
    main()

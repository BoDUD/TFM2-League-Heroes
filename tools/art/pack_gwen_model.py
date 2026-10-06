"""Gwen's step 1 pack for Codex: the pictures that go with assets/source/gwen/MODEL_PROMPTS.md.

    python tools/art/pack_gwen_model.py --out <folder> [--league <1_gwen_league_front.png>]

From the approved picture A (assets/source/gwen/codex_picture/gwen-model-A.png, the user's pick 2026-10-06: the open
scissors held at her side, the blades trailing down and back) with the blades pressed shorter along their own axis
(beyond 70 px from the pivot every length x0.6, the taper kept: 36 squares wide at 40 rows -> 32) and the pack's own
game sprites (pack_samira_model.py's layout):
  1_picture.png       picture A, blades shortened, on white, cropped
  2_target_size.png   a 1024x1024 canvas (128 x 128 squares at 8x) with that picture's silhouette shrunk to game size
                      (grey): red = the bottom of the soles' row (row 99, y 792-799), blue = the middle column (x 512),
                      green = the top (the cowlick, TOTAL squares over the soles), orange / purple = the chin of version
                      1 / 2
  3_quality_bar.png   league_samira, league_kaisa, league_evelynn, league_varus and league_sivir as they are in the game
                      now (idle, first frame) at 8x on one soles line
  4_head.png          A's head, enlarged
  5_parts.png         A's scissors (shortened), the waist bow with the star brooch, the shoes, enlarged
  6_size_guide.png    the shortened picture shrunk straight to game size, on the same canvas - only to see what fits where
  7_league_idle.png   with --league: League's idle render (Riot material: it goes into the pack only, never into git)
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

PICTURE = os.path.join(ROOT, "assets", "source", "gwen", "codex_picture", "gwen-model-A.png")
TOTAL = 40                       # squares from the cowlick's top to the soles
HEAD = {"1": 12, "2": 10}        # squares from the cowlick's top to the chin
SOLES_ROW, MID_COL, Z = 99, 64, 8
QUALITY = ["samira", "kaisa", "evelynn", "varus", "sivir"]
BODY = 795                       # picture A: the cowlick's top (y 127) to the soles (y 922)
PIVOT, AXIS, KEEP, SQUEEZE = (640, 600), (-0.743, 0.669), 70, 0.6   # the blades' line, from the ring handles down-left
LEFT_OF = 770                    # only columns left of this are the scissors' (the shoes reach the same line further right)
HEAD_BOX = (690, 120, 1010, 345)                    # the cowlick and the bows to the chin
CROP_BOXES = [(470, 470, 775, 830), (800, 395, 1000, 525), (775, 780, 1010, 925)]


def shortened(pic):
    """Picture A with hard alpha and the scissor blades pressed shorter along their axis (the taper kept)."""
    a = np.array(pic)
    a[..., 3] = np.where(a[..., 3] >= 160, 255, 0)
    h, w = a.shape[:2]
    u = np.array(AXIS, float)
    u /= np.linalg.norm(u)
    v = np.array([-u[1], u[0]])
    yy, xx = np.mgrid[0:h, 0:w]
    proj = (xx - PIVOT[0]) * u[0] + (yy - PIVOT[1]) * u[1]
    perp = (xx - PIVOT[0]) * v[0] + (yy - PIVOT[1]) * v[1]
    zone = (xx < LEFT_OF) & (proj > KEEP)
    out = a.copy()
    out[zone] = 0
    sp = KEEP + (proj - KEEP) / SQUEEZE
    sx = np.round(PIVOT[0] + sp * u[0] + perp * v[0]).astype(int)
    sy = np.round(PIVOT[1] + sp * u[1] + perp * v[1]).astype(int)
    ok = zone & (sx >= 0) & (sx < LEFT_OF) & (sy >= 0) & (sy < h)
    out[ok] = a[sy[ok], sx[ok]]
    return drop_specks(Image.fromarray(out))


def drop_specks(img, least=200):
    """Clear opaque islands smaller than `least` pixels (leftovers of the slid butt)."""
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
    for v, col in (("1", (245, 140, 20, 255)), ("2", (150, 60, 200, 255))):
        y = top + HEAD[v] * Z
        d.line([(0, y), (1023, y)], fill=col, width=2)
    return img


def game_size(pic):
    """The picture cropped to its alpha box and shrunk so that his body is TOTAL rows: (colour, coverage)."""
    a = np.asarray(pic).astype(float) / 255
    ys, xs = np.where(a[:, :, 3] > 0.5)
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
    ap.add_argument("--league", help="League's idle render (refs/1_gwen_league_front.png from the step 0 pack)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    raw = Image.open(PICTURE).convert("RGBA")
    pic = shortened(raw)
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
        shutil.copy(args.league, os.path.join(args.out, "7_league_idle.png"))
    print("wrote", ", ".join(sorted(os.listdir(args.out))))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Kassadin's step-1 pack for Codex (assets/source/kassadin/MODEL_PROMPTS.md): the design drawn on a 2x game grid.

    python tools/art/pack_kassadin_model.py --out dist/kassadin_packs/kassadin_model_pack

The user picked picture A (assets/source/kassadin/codex_picture/kassadin-model-A.png, 2026-10-12: both hands open at
his sides, the near palm up). Gragas's lesson (memory gragas-session): Codex's own shrinks to game size come out muddy
while its raw drawings are crisp, and the approved design was its raw traced 2:1. So this pack asks for the design drawn
at TWICE the game size on a fixed 13-px grid (1024 x 1536 = 78 x 118 squares, every square one flat colour), which
Claude traces 2:1 square for square; Codex's own 1x copy is only a check. Two views from the start - the 3/4 front for
the idle and the ban/pick card, and SIDE-ON facing right for every action (memory side-view-design) with the same 3/4
mask (memory one-face-all-frames). Layout at 2x: the tips of his horns on row TOP, the robe's lowest point on row SOLE
(80 rows = 40 game rows), the robe's middle on column MID.
  1_guide_grid.png       picture A brought straight down to the layout (blurry, 13 px a square with a yellow measuring
                         grid and the rows marked): the size, the pose and the place only
  2_picture.png          picture A on light grey: the look
  3_league_head.png      League's in-game model, his head (local render, Riot's model: never committed)
  4_example_raw.png      Gragas's step-1 raw (Codex, 2x squares): the way of working - crisp squares, no blur
  5_example_sprite.png   Gragas's approved design (that raw traced 2:1) at 8x
  6_quality_bar.png      heroes the user approved, 8x on one feet line (Gragas, Xerath, Viktor, Syndra, Irelia)
  7_parts.png            picture A's head and near hand, enlarged
  8_league_side.png      League's model turned to the side, facing right (idle, two run frames; rendered at yaw -70
                         and flipped: local render, never committed)
  9_empty_grid.png       the same grid empty, with the rows and the middle column marked: the canvas for the side view
The League side render: python tools/lol/pose_ref.py --champ Kassadin --hq --bg 225,225,225 --no-labels --size 800
--fit 0.75 --ground 0.92 --width 1.25 --yaw -70 --mirror --name league_side_raw --out %TEMP%/ks_work/side --frame
kassadin_idle1@0 --frame kassadin_run@0 --frame kassadin_run@400, each cell then flipped left-right.
The head render is pack_kassadin_picture.py's 3_kassadin_league_head.png (dist/kassadin_packs/kassadin_pack0/refs).
"""
import argparse
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "kassadin")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
PICTURE = os.path.join(SRC, "codex_picture", "kassadin-model-A.png")
HEAD_REF = os.path.join(ROOT, "dist", "kassadin_packs", "kassadin_pack0", "refs", "3_kassadin_league_head.png")
SIDE_REF = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ks_work", "side", "league_side.png")
SQ = 13                         # Codex's square (half a game pixel's 26: the drawing is twice the game size)
COLS, ROWS = 78, 118            # 1014 x 1534 inside the 1024 x 1536 canvas
TOP, SOLE = 20, 99              # horn tips row 20, the robe's lowest point row 99 (80 rows = 40 game rows)
MID = 39                        # the robe's middle column
# picture A: the horn tips y 41, the robe's lowest point y 1503, the robe's middle x 530
P_TOP, P_SOLE, P_MID = 41, 1503, 530
HEAD_BOX = (330, 30, 760, 470)
HAND_BOX = (690, 560, 1010, 860)


def hard(im):
    a = np.array(im.convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] > 200, 255, 0)
    a[a[..., 3] == 0] = 0
    return Image.fromarray(a)


def guide(pic):
    """Picture A straight down to the layout: every square the picture's average where it covers half of it."""
    k = (SOLE + 1 - TOP) / (P_SOLE - P_TOP)
    x0, y0 = P_MID - (MID + 0.5) / k, P_TOP - TOP / k
    box = (round(x0), round(y0), round(x0 + COLS / k), round(y0 + ROWS / k))
    a = np.asarray(pic.crop(box)).astype(float) / 255
    pre = a[..., :3] * a[..., 3:4]
    ch = [np.asarray(Image.fromarray((pre[..., i] * 255).astype(np.uint8)).resize((COLS, ROWS), Image.BOX)) / 255
          for i in range(3)]
    cov = np.asarray(Image.fromarray((a[..., 3] * 255).astype(np.uint8)).resize((COLS, ROWS), Image.BOX)) / 255
    rgb = np.dstack(ch) / np.maximum(cov[..., None], 1e-6)
    out = np.zeros((ROWS, COLS, 4), np.uint8)
    out[..., :3] = (rgb.clip(0, 1) * 255).astype(np.uint8)
    out[..., 3] = np.where(cov > 0.5, 255, 0)
    return out


def big(can):
    img = Image.new("RGBA", (1024, 1536), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can).resize((COLS * SQ, ROWS * SQ), Image.NEAREST))
    d = ImageDraw.Draw(img)
    for c in range(COLS + 1):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(ROWS + 1):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(0, ROWS, 10):
        d.text((2, r * SQ + 1), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 10):
        d.text((c * SQ + 2, 2), str(c), fill=(0, 0, 200, 255))
    d.line([(0, (SOLE + 1) * SQ), (COLS * SQ, (SOLE + 1) * SQ)], fill=(230, 30, 30, 255), width=3)
    d.line([(0, TOP * SQ), (COLS * SQ, TOP * SQ)], fill=(30, 170, 60, 255), width=3)
    d.line([((MID + 0.5) * SQ, 0), ((MID + 0.5) * SQ, ROWS * SQ)], fill=(40, 90, 230, 255), width=3)
    return img


def on_grey(im, k=1):
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.resize((im.width * k, im.height * k), Image.NEAREST)


def hero(n):
    im = Image.open(os.path.join(NATIVE, f"{n}_native.png")).convert("RGBA")
    if im.width == 1024:
        im = im.resize((128, 128), Image.NEAREST)
    return im.crop(im.getbbox())


def quality_bar():
    shots = [hero(n) for n in ("gragas", "xerath", "viktor", "syndra", "irelia")]
    z, pad = 8, 24
    tall = max(s.height for s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for s in shots) + pad, tall + 2 * pad), (255, 255, 255, 255))
    x = pad
    for s in shots:
        img.alpha_composite(s.resize((s.width * z, s.height * z), Image.NEAREST), (x, pad + tall - s.height * z))
        x += s.width * z + pad
    return img


def parts(pic):
    tiles = [on_grey(pic.crop(HEAD_BOX), 2), on_grey(pic.crop(HAND_BOX), 2)]
    img = Image.new("RGBA", (sum(t.width for t in tiles) + 40, max(t.height for t in tiles)), (255, 255, 255, 255))
    x = 0
    for t in tiles:
        img.alpha_composite(t, (x, 0))
        x += t.width + 40
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, "kassadin")
    os.makedirs(out, exist_ok=True)
    pic = hard(Image.open(PICTURE))
    big(guide(pic)).convert("RGB").save(os.path.join(out, "1_guide_grid.png"))
    box = pic.getbbox()
    on_grey(pic.crop((box[0] - 30, box[1] - 30, box[2] + 30, box[3] + 20))).convert("RGB").save(
        os.path.join(out, "2_picture.png"))
    Image.open(HEAD_REF).convert("RGB").save(os.path.join(out, "3_league_head.png"))
    raw = os.path.join(ROOT, "assets", "source", "gragas", "codex_model", "raw", "gragas-front-A-raw.png")
    on_grey(Image.open(raw).convert("RGBA")).convert("RGB").save(os.path.join(out, "4_example_raw.png"))
    gr = hero("gragas")
    on_grey(gr, 8).convert("RGB").save(os.path.join(out, "5_example_sprite.png"))
    quality_bar().convert("RGB").save(os.path.join(out, "6_quality_bar.png"))
    parts(pic).convert("RGB").save(os.path.join(out, "7_parts.png"))
    Image.open(SIDE_REF).convert("RGB").save(os.path.join(out, "8_league_side.png"))
    big(np.zeros((ROWS, COLS, 4), np.uint8)).convert("RGB").save(os.path.join(out, "9_empty_grid.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(a.out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()

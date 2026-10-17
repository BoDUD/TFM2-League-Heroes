#!/usr/bin/env python3
"""Gragas's step-1 pack for Codex (assets/source/gragas/MODEL_PROMPTS.md): the design drawn ON THE GAME GRID.

    python tools/art/pack_gragas_model.py --out dist/gragas_packs/gragas_model_pack

The user picked picture A (assets/source/gragas/codex_picture/gragas-model-A.png, 2026-10-12: the keg slung on his
back, both fists hanging). The design is drawn at game size on a fixed 26-px grid (Gwen's geometry, 1024 x 1536 = 39 x 59
squares: art-spec "A design drawn at game size" and "A muddy design"), in TWO views from the start - the 3/4 front for the
idle and the ban/pick card, and SIDE-ON facing right for every action (memory side-view-design: Nautilus's front-only
design gave front-on strips). Layout: the top of his bald head on row TOP, the soles on row SOLE (36 rows), the keg no
higher than row KEG_TOP, the feet's middle on column MID (the keg reaches far to the image left).
  1_guide_grid.png       picture A brought straight down to the layout (blurry, at 26 px a square with a yellow
                         measuring grid and the rows marked): the size, the pose and the place only
  2_picture.png          picture A on light grey: the look
  3_league_face.png      League's in-game model, his head (local render, Riot's model: never committed)
  4_example_picture.png  Gwen's on-grid delivery (Codex, approved) at 26 px a square: the way of working
  5_example_sprite.png   the same at 1x enlarged 8x
  6_quality_bar.png      heroes the user approved, 8x on one feet line (the big ones: Nautilus, Tryndamere, Sett, Shen)
  7_parts.png            picture A's head and the keg, enlarged
  8_league_side.png      League's model turned to the side, facing right with the keg on his back (idle, two run
                         frames; rendered at yaw -70 and flipped: local render, never committed)
  9_empty_grid.png       the same grid empty, with the rows and the feet column marked: the canvas for the side view
The League side render: python tools/lol/pose_ref.py --champ Gragas --hq --bg 225,225,225 --no-labels --size 800
--fit 0.75 --ground 0.92 --width 1.25 --yaw -70 --mirror --name league_side_raw --out %TEMP%/gr_work/side --frame
gragas_idle1@0 --frame gragas_run@0 --frame gragas_run@373, each cell then flipped left-right.
The head render is pack_gragas_picture.py's 3_gragas_league_head.png.
"""
import argparse
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "gragas")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
PICTURE = os.path.join(SRC, "codex_picture", "gragas-model-A.png")
FACE_REF = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "gr_work", "face_ref", "face_head.png")
SIDE_REF = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "gr_work", "side", "league_side.png")
SQ = 26                         # Codex's square
COLS, ROWS = 39, 59             # 1014 x 1534 inside the 1024 x 1536 canvas
TOP, SOLE, KEG_TOP = 15, 50, 14   # head top row 15, soles row 50 (36 rows), the keg not above row 14
MID = 22                        # the feet's middle column (the keg reaches far to the image left)
# picture A: the top of his head y 478, the soles y 1178, the middle between the feet x 580
P_TOP, P_SOLE, P_MID = 478, 1178, 580
HEAD_BOX = (470, 470, 760, 820)
KEG_BOX = (160, 470, 480, 820)


def hard(im):
    a = np.array(im.convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] > 200, 255, 0)
    a[a[..., 3] == 0] = 0
    return Image.fromarray(a)


def guide(pic):
    """Picture B straight down to the layout: every square the picture's average where it covers half of it."""
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
    for r in range(0, ROWS, 5):
        d.text((2, r * SQ + 6), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 5):
        d.text((c * SQ + 6, 2), str(c), fill=(0, 0, 200, 255))
    d.line([(0, (SOLE + 1) * SQ), (COLS * SQ, (SOLE + 1) * SQ)], fill=(230, 30, 30, 255), width=3)
    d.line([(0, TOP * SQ), (COLS * SQ, TOP * SQ)], fill=(30, 170, 60, 255), width=3)
    d.line([(0, KEG_TOP * SQ), (COLS * SQ, KEG_TOP * SQ)], fill=(245, 140, 20, 255), width=3)
    d.line([((MID + 0.5) * SQ, 0), ((MID + 0.5) * SQ, ROWS * SQ)], fill=(40, 90, 230, 255), width=3)
    return img


def on_grey(im, k=1):
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.resize((im.width * k, im.height * k), Image.NEAREST)


def league_face():
    return Image.open(FACE_REF).convert("RGB")


def hero(n):
    im = Image.open(os.path.join(NATIVE, f"{n}_native.png")).convert("RGBA")
    if im.width == 1024:
        im = im.resize((128, 128), Image.NEAREST)
    return im.crop(im.getbbox())


def quality_bar():
    shots = [hero(n) for n in ("nautilus", "tryndamere", "sett", "shen", "gwen")]
    z, pad = 8, 24
    tall = max(s.height for s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for s in shots) + pad, tall + 2 * pad), (255, 255, 255, 255))
    x = pad
    for s in shots:
        img.alpha_composite(s.resize((s.width * z, s.height * z), Image.NEAREST), (x, pad + tall - s.height * z))
        x += s.width * z + pad
    return img


def parts(pic):
    tiles = [on_grey(pic.crop(HEAD_BOX), 2), on_grey(pic.crop(KEG_BOX), 2)]
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
    out = os.path.join(a.out, "gragas")
    os.makedirs(out, exist_ok=True)
    pic = hard(Image.open(PICTURE))
    g = guide(pic)
    big(g).convert("RGB").save(os.path.join(out, "1_guide_grid.png"))
    box = pic.getbbox()
    on_grey(pic.crop((box[0] - 30, box[1] - 30, box[2] + 30, box[3] + 20))).convert("RGB").save(
        os.path.join(out, "2_picture.png"))
    league_face().save(os.path.join(out, "3_league_face.png"))
    shutil.copyfile(os.path.join(ROOT, "assets", "source", "gwen", "codex_grid", "gwen-grid-A.png"),
                    os.path.join(out, "4_example_picture.png"))
    gw = Image.open(os.path.join(ROOT, "assets", "source", "gwen", "codex_grid", "gwen-grid-A_1x.png")).convert("RGBA")
    gw = gw.crop(gw.getbbox())
    gw.resize((gw.width * 8, gw.height * 8), Image.NEAREST).save(os.path.join(out, "5_example_sprite.png"))
    quality_bar().convert("RGB").save(os.path.join(out, "6_quality_bar.png"))
    parts(pic).convert("RGB").save(os.path.join(out, "7_parts.png"))
    shutil.copyfile(SIDE_REF, os.path.join(out, "8_league_side.png"))
    big(np.zeros_like(g)).convert("RGB").save(os.path.join(out, "9_empty_grid.png"))
    Image.fromarray(g).save(os.path.join(out, "guide_1x.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(a.out, "MODEL_PROMPTS.md"))
    ys, xs = np.nonzero(g[..., 3])
    print(f"guide: rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()} ({xs.max() - xs.min() + 1} wide)")
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()

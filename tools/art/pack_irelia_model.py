#!/usr/bin/env python3
"""Irelia's step-1 pack for Codex (assets/source/irelia/MODEL_PROMPTS.md): the design drawn ON THE GAME GRID.

    python tools/art/pack_irelia_model.py --out dist/irelia_packs/irelia_model_pack

The user picked picture B (assets/source/irelia/codex_picture/irelia-model-B.png, 2026-10-11: the blades folded into
one bundle behind her back, hands down). Both lessons of the pack go in at once: the design is drawn at game size, not
shrunk from a bigger drawing (art-spec "A design drawn at game size"), and on a fixed 26-px grid (Gwen's geometry,
1024 x 1536 = 39 x 59 squares: art-spec "A muddy design" - league_zeri's 40-row restore of a big picture stayed muddy
until it was drawn square by square). Layout: the tip of her crest on row TOP, the soles on row SOLE (37 rows, the
size the user picked for league_zeri), the blade tips no higher than row BLADE_TOP, the feet's middle on column MID.
  1_guide_grid.png       picture B brought straight down to the layout (blurry, at 26 px a square with a yellow
                         measuring grid and the rows marked): the size, the pose and the place only
  2_picture.png          picture B on light grey: the look
  3_league_face.png      League's in-game model, her face (local render, Riot's model: never committed): the brows,
                         the cyan eyes, the liner, the lips, the silver tiara
  4_example_picture.png  Gwen's on-grid delivery (Codex, approved) at 26 px a square: the way of working
  5_example_sprite.png   the same at 1x enlarged 8x
  6_quality_bar.png      heroes the user approved, 8x on one feet line (league_zeri at 37 rows among them)
  7_parts.png            picture B's head and the blade bundle, enlarged
  8_league_side.png      League's model turned to the side (yaw 70: idle, two run frames, an attack; local render,
                         never committed): how she looks side-on - every action is drawn side-on facing right (the
                         user after league_nautilus: 「你得做侧面的吧 泰坦教训还不够吗」), so the design comes in two views
  9_empty_grid.png       the same grid empty, with the rows and the feet column marked: the canvas for the side view
The League side render: python tools/lol/pose_ref.py --champ Irelia --hq --bg 225,225,225 --no-labels --size 800
--fit 0.8 --ground 0.92 --width 1.0 --yaw 70 --mirror --name league_side --out %TEMP%/ir_work/side --frame
irelia_idle_01@0 --frame irelia_run_base@0 --frame irelia_run_base@300 --frame irelia_attack_01@200
The League face render: python tools/lol/pose_ref.py --champ Irelia --frame irelia_attack_01@0 --name face --hq
--size 1800 --fit 0.92 --pitch 4 --yaw 40 --mirror --no-labels --bg 225,225,225 --out %TEMP%/ir_work/face_ref
"""
import argparse
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "irelia")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
PICTURE = os.path.join(SRC, "codex_picture", "irelia-model-B.png")
FACE_REF = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ir_work", "face_ref", "face.png")
SIDE_REF = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ir_work", "side", "league_side.png")
SQ = 26                         # Codex's square
COLS, ROWS = 39, 59             # 1014 x 1534 inside the 1024 x 1536 canvas
TOP, SOLE, BLADE_TOP = 15, 51, 12   # crest tip row 15, soles row 51 (37 rows), blade tips not above row 12
MID = 19                        # the feet's middle column
# picture B: the crest's tip y 130, the soles y 972, the middle between the feet x 795
P_TOP, P_SOLE, P_MID = 130, 972, 795
HEAD_BOX = (735, 115, 925, 315)
BLADES_BOX = (585, 65, 790, 560)


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
    d.line([(0, BLADE_TOP * SQ), (COLS * SQ, BLADE_TOP * SQ)], fill=(245, 140, 20, 255), width=3)
    d.line([((MID + 0.5) * SQ, 0), ((MID + 0.5) * SQ, ROWS * SQ)], fill=(40, 90, 230, 255), width=3)
    return img


def on_grey(im, k=1):
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.resize((im.width * k, im.height * k), Image.NEAREST)


def league_face():
    im = Image.open(FACE_REF).convert("RGB")
    face = im.crop((380, 300, 680, 580))
    return face.resize((face.width * 2, face.height * 2), Image.LANCZOS)


def hero(n):
    im = Image.open(os.path.join(NATIVE, f"{n}_native.png")).convert("RGBA")
    if im.width == 1024:
        im = im.resize((128, 128), Image.NEAREST)
    return im.crop(im.getbbox())


def quality_bar():
    shots = [hero(n) for n in ("gwen", "zeri", "syndra", "seraphine", "samira")]
    z, pad = 8, 24
    tall = max(s.height for s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for s in shots) + pad, tall + 2 * pad), (255, 255, 255, 255))
    x = pad
    for s in shots:
        img.alpha_composite(s.resize((s.width * z, s.height * z), Image.NEAREST), (x, pad + tall - s.height * z))
        x += s.width * z + pad
    return img


def parts(pic):
    tiles = [on_grey(pic.crop(HEAD_BOX), 3), on_grey(pic.crop(BLADES_BOX), 2)]
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
    out = os.path.join(a.out, "irelia")
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

#!/usr/bin/env python3
"""Zeri's on-grid redraw pack for Codex (assets/source/zeri/GRID_PROMPTS.md): the whole sprite drawn again at game size.

    python tools/art/pack_zeri_grid.py --out dist/zeri_packs/zeri_grid_pack

Why (2026-10-11): the 40-row design (design40/zeri40_final.txt) is the user's own picture (72 rows) block-voted down to
40 rows and finished by hand, the face from Codex's face pack (take C). The user: 「模型整体还是太糊」「眼睛我还是挺不满意的
没有泽丽的特色」「我相信之前英雄碰到过我说的这些问题」 - the pitfall the pack met before (Lux / Ashe, then Akali, Vayne,
Zed, Lillia, Janna): a picture squeezed to game size breaks into specks; what came out clean was Codex drawing the sprite
on the game grid itself (assets/source/gwen|lillia|zed/codex_grid). So Codex redraws Zeri square by square on a fixed
26-px grid (Gwen's geometry: 1024 x 1536, 39 x 59 squares), keeping the approved layout, with Zeri's own face.
  1_current_grid.png   the current sprite at 26 px a square with a yellow measuring grid: size, proportions, pose, place
  2_picture.png        the user's picture: her look (costume, colours, parts)
  3_league_face.png    League's in-game model, her face (local render, Riot's model: never committed): the brows, the
                       eyeliner, the yellow-green eyes, the coral lips - her character
  4_example_picture.png  Gwen's on-grid redraw (Codex, approved) at 26 px a square: the way of working
  5_example_sprite.png   the same at 1x enlarged 8x
  6_quality_bar.png    heroes the user approved, 8x on one feet line
  7_rejected_faces.png the faces the user turned down (v5, v6, Codex's take C)
The League face render: python tools/lol/pose_ref.py --champ Zeri --frame idle@0 --name face --hq --size 1800 --fit 0.92
--pitch 4 --yaw 40 --no-labels --bg 225,225,225 --out %TEMP%/zr_work/face_ref
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "zeri")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
D40 = os.path.join(SRC, "design40")
PAL = json.load(open(os.path.join(D40, "palette.json")))
FACE_REF = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "zr_work", "face_ref", "face.png")
SQ = 26                       # Codex's square
COLS, ROWS = 39, 59           # 1014 x 1534 inside the 1024 x 1536 canvas
TOP, SOLE = 12, 51            # bun tips on row 12, soles on row 51: 40 rows
MID = 19                      # the feet's middle column


def table(name):
    rows = open(os.path.join(D40, name)).read().splitlines()[:40]
    a = np.zeros((40, 24, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL:
                a[y, x, :3] = [int(PAL[ch][i:i + 2], 16) for i in (1, 3, 5)]
                a[y, x, 3] = 255
    return a


def logical(a):
    """The 24 x 40 table on the 39 x 59 canvas: top on TOP, the feet's middle (table column 11) on MID."""
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[TOP:TOP + 40, MID - 11:MID - 11 + 24] = a
    return can


def big(can, grid=True):
    img = Image.new("RGBA", (1024, 1536), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can).resize((COLS * SQ, ROWS * SQ), Image.NEAREST))
    if grid:
        d = ImageDraw.Draw(img)
        for c in range(COLS + 1):
            d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(240, 200, 0, 255), width=1)
        for r in range(ROWS + 1):
            d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(240, 200, 0, 255), width=1)
        for r in range(0, ROWS, 5):
            d.text((2, r * SQ + 6), str(r), fill=(200, 0, 0, 255))
        for c in range(0, COLS, 5):
            d.text((c * SQ + 6, 2), str(c), fill=(0, 0, 200, 255))
    return img


def league_face():
    im = Image.open(FACE_REF).convert("RGB")
    a = np.asarray(im).astype(int)
    m = (np.abs(a - np.array([225, 225, 225])).max(-1) > 12)
    ys, xs = np.nonzero(m)
    h = ys.max() - ys.min()
    head = im.crop((xs.min(), ys.min(), xs.max(), ys.min() + int(h * 0.28)))
    face = head.crop((330, 110, 480, 240)).resize((600, 520), Image.LANCZOS)
    out = Image.new("RGB", (head.width + 640, max(head.height, 520) + 20), (255, 255, 255))
    out.paste(head, (0, 0))
    out.paste(face, (head.width + 30, 0))
    return out


def hero(n):
    im = Image.open(os.path.join(NATIVE, f"{n}_native.png")).convert("RGBA")
    if im.width == 1024:
        im = im.resize((128, 128), Image.NEAREST)
    return im.crop(im.getbbox())


def quality_bar():
    shots = [hero(n) for n in ("gwen", "akali", "samira", "syndra", "seraphine")]
    z, pad = 8, 24
    tall = max(s.height for s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for s in shots) + pad, tall + 2 * pad), (255, 255, 255, 255))
    x = pad
    for s in shots:
        img.alpha_composite(s.resize((s.width * z, s.height * z), Image.NEAREST), (x, pad + tall - s.height * z))
        x += s.width * z + pad
    return img


def rejected():
    tiles = []
    for name in ("zeri40_v5.txt", "zeri40_v6.txt", "zeri40_final.txt"):
        a = table(name)[4:18, 3:18]
        tiles.append(Image.fromarray(a).resize((a.shape[1] * 20, a.shape[0] * 20), Image.NEAREST))
    img = Image.new("RGBA", (sum(t.width + 30 for t in tiles) + 30, tiles[0].height + 40), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    x = 30
    for t, lab in zip(tiles, ("v5: not like Zeri", "v6: looks weird", "take C: no Zeri character")):
        img.alpha_composite(t, (x, 30))
        d.text((x, 8), lab, fill=(200, 0, 0, 255))
        x += t.width + 30
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, "zeri")
    os.makedirs(out, exist_ok=True)
    cur = logical(table("zeri40_final.txt"))
    big(cur).convert("RGB").save(os.path.join(out, "1_current_grid.png"))
    shutil.copyfile(os.path.join(SRC, "user_ref", "zeri_user.png"), os.path.join(out, "2_picture.png"))
    league_face().save(os.path.join(out, "3_league_face.png"))
    shutil.copyfile(os.path.join(SRC, "..", "gwen", "codex_grid", "gwen-grid-A.png"), os.path.join(out, "4_example_picture.png"))
    g = Image.open(os.path.join(SRC, "..", "gwen", "codex_grid", "gwen-grid-A_1x.png")).convert("RGBA")
    g = g.crop(g.getbbox())
    g.resize((g.width * 8, g.height * 8), Image.NEAREST).save(os.path.join(out, "5_example_sprite.png"))
    quality_bar().convert("RGB").save(os.path.join(out, "6_quality_bar.png"))
    rejected().convert("RGB").save(os.path.join(out, "7_rejected_faces.png"))
    Image.fromarray(cur).save(os.path.join(out, "current_1x.png"))
    shutil.copyfile(os.path.join(SRC, "GRID_PROMPTS.md"), os.path.join(a.out, "GRID_PROMPTS.md"))
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()

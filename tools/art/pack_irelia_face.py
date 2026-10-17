#!/usr/bin/env python3
"""Irelia's face pack for Codex (assets/source/irelia/FACE_PROMPTS.md): redraw only the face of the 42-row design.

    python tools/art/pack_irelia_face.py --out dist/irelia_packs/irelia_face_pack

How it came about (2026-10-11): the 42-row design (design42/irelia42.txt) is Codex's front draft
(codex_model/raw/irelia-front-B.png) restored square by square (tools/art/restore_irelia.py, then by hand). The user:
「修的挺好的 细节部分可以做更好一点」, 「嘴巴可以不画 眼睛做的精致一点 更像刀妹一点」, 「你可以看看英雄联盟刀妹的眼睛什么样吧」,
and after my two eye redraws 「眼睛还是太怪 可以让codex帮忙 你觉得做不出的地方」. So Codex redraws the face box alone;
everything outside it stays square for square (the blades, hair, crest, body are being finished on my side).
  1_design.png         the design at 8x on the 1024 canvas (soles on row 99, the feet's middle on x 512), face box in red
  2_face_box.png       the head at 24x, every square numbered (table rows/columns), the face box marked
  3_picture.png        Codex's front draft the design restores (the look)
  4_picture_face.png   that draft's face, big
  5_league_face.png    League's in-game model, her face (local render, Riot's model: never committed): the EYES to copy
  6_quality_bar.png    heads of heroes the user approved, 8x
  7_rejected.png       my eye redraws the user rejected (「眼睛还是太怪」)
  design_1x.png        the design at 1x (128 x 128) to check that nothing outside the box moved
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "irelia")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
PAL = json.load(open(os.path.join(SRC, "design42", "palette.json")))
OX, OY = 50, 58                     # the 22 x 42 table on the 128 x 128 canvas
BOX = (8, 15, 9, 18)                # face box: table rows 8..14, columns 9..17 (start inclusive, end exclusive)
LEAGUE_FACE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ir_work", "eyes", "front.png")
LEAGUE_CROP = (1050, 180, 1250, 340)
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ir_work", "d42")
REJECTED = [("v2: E3", os.path.join(TMP, "irelia42_v2_face_rejected.txt")),
            ("v3: G7", os.path.join(SRC, "design42", "irelia42.txt"))]
RED = (230, 30, 30, 255)


def table(path):
    rows = [r.rstrip("\n") for r in open(path, encoding="utf-8") if r.strip("\n")]
    a = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL:
                a[y, x, :3] = [int(PAL[ch][i:i + 2], 16) for i in (1, 3, 5)]
                a[y, x, 3] = 255
    return a


def canvas(a):
    can = np.zeros((128, 128, 4), np.uint8)
    can[OY:OY + a.shape[0], OX:OX + a.shape[1]] = a
    return can


def on_white(can, z=8):
    img = Image.new("RGBA", (can.shape[1], can.shape[0]), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can))
    return img.resize((can.shape[1] * z, can.shape[0] * z), Image.NEAREST)


def design_sheet(a):
    img = on_white(canvas(a))
    d = ImageDraw.Draw(img)
    r0, r1, c0, c1 = BOX
    d.rectangle([(OX + c0) * 8 - 1, (OY + r0) * 8 - 1, (OX + c1) * 8, (OY + r1) * 8], outline=RED, width=2)
    return img


def numbered(a, r0, r1, c0, c1, z=24):
    w, h = c1 - c0, r1 - r0
    img = Image.new("RGBA", (w * z + 40, h * z + 30), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(a[r0:r1, c0:c1]).resize((w * z, h * z), Image.NEAREST), (36, 26))
    d = ImageDraw.Draw(img)
    for j in range(h + 1):
        d.line([(36, 26 + j * z), (36 + w * z, 26 + j * z)], fill=(190, 190, 190, 255))
    for i in range(w + 1):
        d.line([(36 + i * z, 26), (36 + i * z, 26 + h * z)], fill=(190, 190, 190, 255))
    for j in range(h):
        d.text((4, 26 + j * z + z // 3), f"{r0 + j}", fill=(0, 0, 0, 255))
    for i in range(w):
        d.text((36 + i * z + z // 3, 6), f"{c0 + i}", fill=(0, 0, 0, 255))
    b0, b1, k0, k1 = BOX
    d.rectangle([36 + (k0 - c0) * z - 1, 26 + (b0 - r0) * z - 1, 36 + (k1 - c0) * z + 1, 26 + (b1 - r0) * z + 1],
                outline=RED, width=3)
    return img


def heads():
    shots = []
    for h in ("gwen", "seraphine", "syndra", "zeri", "xayah"):
        im = Image.open(os.path.join(NATIVE, f"{h}_native.png")).convert("RGBA")
        if im.width == 1024:
            im = im.resize((128, 128), Image.NEAREST)
        im = im.crop(im.getbbox())
        shots.append((h, im.crop((0, 0, im.width, min(im.height, 20)))))
    z, pad = 8, 24
    tall = max(s.height for _, s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for _, s in shots) + pad, tall + 2 * pad + 16), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for h, s in shots:
        img.alpha_composite(s.resize((s.width * z, s.height * z), Image.NEAREST), (x, pad))
        d.text((x, pad + tall + 4), f"league_{h}", fill=(0, 0, 0, 255))
        x += s.width * z + pad
    return img


def rejected():
    tiles = []
    for name, path in REJECTED:
        a = table(path)
        r0, r1, c0, c1 = BOX
        tiles.append((name, Image.fromarray(a[r0 - 2:r1 + 1, c0 - 2:c1 + 1]).resize(((c1 - c0 + 3) * 20, (r1 - r0 + 3) * 20),
                                                                                    Image.NEAREST)))
    img = Image.new("RGBA", (sum(t.width + 30 for _, t in tiles) + 30, tiles[0][1].height + 50), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    x = 30
    for name, t in tiles:
        img.alpha_composite(t, (x, 30))
        d.text((x, 8), f"{name} - rejected: the eyes look weird", fill=(200, 0, 0, 255))
        x += t.width + 30
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, "irelia")
    os.makedirs(out, exist_ok=True)
    des = table(os.path.join(SRC, "design42", "irelia42.txt"))
    design_sheet(des).convert("RGB").save(os.path.join(out, "1_design.png"))
    numbered(des, 2, 18, 5, 20).convert("RGB").save(os.path.join(out, "2_face_box.png"))
    pic = Image.open(os.path.join(SRC, "codex_model", "raw", "irelia-front-B.png")).convert("RGBA")
    bg = Image.new("RGBA", pic.size, (255, 255, 255, 255))
    bg.alpha_composite(pic)
    bg.crop(bg.getbbox()).convert("RGB").save(os.path.join(out, "3_picture.png"))
    face = bg.crop((500, 380, 740, 640))
    face.resize((face.width * 3, face.height * 3), Image.NEAREST).convert("RGB").save(os.path.join(out, "4_picture_face.png"))
    lol = Image.open(LEAGUE_FACE).convert("RGB").crop(LEAGUE_CROP)
    lol.resize((lol.width * 4, lol.height * 4), Image.LANCZOS).save(os.path.join(out, "5_league_face.png"))
    heads().convert("RGB").save(os.path.join(out, "6_quality_bar.png"))
    rejected().convert("RGB").save(os.path.join(out, "7_rejected.png"))
    Image.fromarray(canvas(des)).save(os.path.join(out, "design_1x.png"))
    shutil.copyfile(os.path.join(SRC, "FACE_PROMPTS.md"), os.path.join(a.out, "FACE_PROMPTS.md"))
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()

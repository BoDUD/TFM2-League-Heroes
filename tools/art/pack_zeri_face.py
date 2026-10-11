#!/usr/bin/env python3
"""Zeri's face pack for Codex (assets/source/zeri/FACE_PROMPTS.md): redraw only the face of the 40-row design.

    python tools/art/pack_zeri_face.py --out dist/zeri_packs/zeri_face_pack

How it came about (2026-10-11): the user gave their own picture of Zeri (user_ref/zeri_user.png, 72 x 41 squares of about
10 px) and asked for it at 40 rows, 「一点点还原 还原到完美」. The 40-row design (design40/zeri40_v5.txt, 24 x 40) is the
picture block-voted square by square (a square is outline only when half of it is), finished by hand; the user: 「眼睛嘴巴
做的不太像泽丽 其他都挺好的」, then for the face 「做成这样也行啊」 with two face pictures (user_ref/face_liked_1/2.png),
and after my redraw after them (design40/zeri40_v6.txt) 「你改的脸还是有点诡异啊 让codex帮忙把」. So Codex redraws the
face box alone; everything outside it is approved and stays square for square.
  1_design.png        v5 at 8x on the 1024 canvas (soles on row 99, the feet's middle on x 512), the face box in red
  2_face_box.png      the head at 24x, every square numbered, the face box marked: the squares Codex may change
  3_picture.png       the user's picture (the look)
  4_picture_face.png  the picture's face at 8x on the same 40-row grid (where her eyes, plaster and mouth sit)
  5_liked_faces.png   the two faces the user said are fine
  6_quality_bar.png   heads of heroes the user approved (Gwen, Senna, Seraphine, Jinx), 8x
  7_rejected.png      my two faces the user rejected (v5: 「不太像泽丽」, v6: 「有点诡异」)
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zeri")
D40 = os.path.join(SRC, "design40")
PAL = json.load(open(os.path.join(D40, "palette.json")))
OX, OY = 53, 60                     # the 24 x 40 table on the 128 x 128 canvas: soles on row 99, feet's middle on 64
BOX = (8, 16, 7, 15)                # face box: table rows 8..15, columns 7..14 (inclusive start, exclusive end)
PIC_BOX = (451, 553, 855, 1243)     # the figure in the user's picture; 40 rows of 690 / 40 px
RED = (230, 30, 30, 255)


def table(name):
    rows = open(os.path.join(D40, name)).read().split("\n")[:40]
    a = np.zeros((40, 24, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL:
                a[y, x, :3] = [int(PAL[ch][i:i + 2], 16) for i in (1, 3, 5)]
                a[y, x, 3] = 255
    return a


def canvas(a):
    can = np.zeros((128, 128, 4), np.uint8)
    can[OY:OY + 40, OX:OX + 24] = a
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
    d.line([(0, 800), (1023, 800)], fill=(230, 30, 30, 120), width=1)
    d.line([(512, 0), (512, 1023)], fill=(40, 90, 230, 120), width=1)
    return img


def numbered(a, r0, r1, c0, c1, z=24, box=True):
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
    if box:
        b0, b1, k0, k1 = BOX
        d.rectangle([36 + (k0 - c0) * z - 1, 26 + (b0 - r0) * z - 1, 36 + (k1 - c0) * z + 1, 26 + (b1 - r0) * z + 1],
                    outline=RED, width=3)
    return img


def picture_face():
    pic = Image.open(os.path.join(SRC, "user_ref", "zeri_user.png")).convert("RGBA")
    bg = Image.new("RGBA", pic.size, (255, 255, 255, 255))
    bg.alpha_composite(pic)
    s = (PIC_BOX[3] - PIC_BOX[1]) / 40
    r0, r1, c0, c1 = 5, 19, 3, 19
    crop = bg.crop((int(PIC_BOX[0] + c0 * s), int(PIC_BOX[1] + r0 * s), int(PIC_BOX[0] + c1 * s), int(PIC_BOX[1] + r1 * s)))
    z = 24
    w, h = c1 - c0, r1 - r0
    img = Image.new("RGBA", (w * z + 40, h * z + 30), (255, 255, 255, 255))
    img.alpha_composite(crop.resize((w * z, h * z), Image.LANCZOS), (36, 26))
    d = ImageDraw.Draw(img)
    for j in range(h + 1):
        d.line([(36, 26 + j * z), (36 + w * z, 26 + j * z)], fill=(255, 0, 255, 160))
    for i in range(w + 1):
        d.line([(36 + i * z, 26), (36 + i * z, 26 + h * z)], fill=(255, 0, 255, 160))
    for j in range(h):
        d.text((4, 26 + j * z + z // 3), f"{r0 + j}", fill=(0, 0, 0, 255))
    for i in range(w):
        d.text((36 + i * z + z // 3, 6), f"{c0 + i}", fill=(0, 0, 0, 255))
    b0, b1, k0, k1 = BOX
    d.rectangle([36 + (k0 - c0) * z - 1, 26 + (b0 - r0) * z - 1, 36 + (k1 - c0) * z + 1, 26 + (b1 - r0) * z + 1],
                outline=RED, width=3)
    return img


def liked():
    ims = [Image.open(os.path.join(SRC, "user_ref", f"face_liked_{i}.png")).convert("RGBA") for i in (1, 2)]
    ims = [im.resize((im.width * 5, im.height * 5), Image.NEAREST) for im in ims]
    img = Image.new("RGBA", (sum(i.width + 30 for i in ims) + 30, max(i.height for i in ims) + 60), (255, 255, 255, 255))
    x = 30
    for im in ims:
        img.alpha_composite(im, (x, 30))
        x += im.width + 30
    return img


def quality_bar():
    shots = []
    for h, rows in (("gwen", (8, 30)), ("senna", (4, 26)), ("seraphine", (0, 22)), ("jinx", (0, 20))):
        sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{h}"))
        f = sp.frames[sp.tag_frames("idle")[0]]
        f = f.crop(f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox())
        shots.append((h, f.crop((0, rows[0], f.width, min(f.height, rows[1])))))
    z, pad = 8, 24
    tall = max(s.height for _, s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for _, s in shots) + pad, tall + 2 * pad + 16), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for h, s in shots:
        img.alpha_composite(s.resize((s.width * z, s.height * z), Image.NEAREST), (x, pad))
        d.text((x, pad + tall + 4), f"league_{h} (head, idle frame)", fill=(0, 0, 0, 255))
        x += s.width * z + pad
    return img


def rejected():
    a5, a6 = table("zeri40_v5.txt"), table("zeri40_v6.txt")
    tiles = [numbered(a, 6, 18, 4, 17, z=20) for a in (a5, a6)]
    img = Image.new("RGBA", (sum(t.width + 30 for t in tiles) + 30, tiles[0].height + 40), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    x = 30
    for t, lab in zip(tiles, ("v5: not like Zeri", "v6: looks weird")):
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
    v5 = table("zeri40_v5.txt")
    design_sheet(v5).convert("RGB").save(os.path.join(out, "1_design.png"))
    numbered(v5, 0, 20, 0, 24).convert("RGB").save(os.path.join(out, "2_face_box.png"))
    shutil.copyfile(os.path.join(SRC, "user_ref", "zeri_user.png"), os.path.join(out, "3_picture.png"))
    picture_face().convert("RGB").save(os.path.join(out, "4_picture_face.png"))
    liked().convert("RGB").save(os.path.join(out, "5_liked_faces.png"))
    quality_bar().convert("RGB").save(os.path.join(out, "6_quality_bar.png"))
    rejected().convert("RGB").save(os.path.join(out, "7_rejected.png"))
    Image.fromarray(canvas(v5)).save(os.path.join(out, "design_1x.png"))
    shutil.copyfile(os.path.join(SRC, "FACE_PROMPTS.md"), os.path.join(a.out, "FACE_PROMPTS.md"))
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()

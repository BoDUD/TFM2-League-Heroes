#!/usr/bin/env python3
"""Zeri's step 1b pack for Codex (assets/source/zeri/REFINE_PROMPTS.md): redraw the design clean at the refined size.

    python tools/art/pack_zeri_refine.py --out dist/zeri_packs/zeri_pack1b

The user picked Codex's own codex_B (32 x 42) and then: 「你还得精修啊 头太大了」「整体模型尺寸也太大了」「还有好多模糊的地方」.
design_zeri.polish() cut it band by band to p35c (28 x 36: the head, bun tips to chin, 21 -> 15 rows) but the dark
lines inside the hair and the coat come from the draft itself; the user chose a clean redraw by Codex at that size.
  1_target.png       p35c at 8x on the 1024 canvas (128 squares; soles on row 99, the feet's middle on x 512): the SIZE,
                     the PROPORTIONS and the POSE to keep (red = the soles' row, blue = the middle, green = the top,
                     purple = the widest allowed)
  2_look.png         codex_B, the approved look (8x)
  3_picture.png      the approved picture A
  4_quality_bar.png  league_jinx, league_caitlyn, league_syndra, league_seraphine as in the game now, 8x on one soles line
  5_target_rows.png  p35c at 12x with every row numbered and the head's rows marked
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
sys.path.insert(0, HERE)
import design_zeri as D  # noqa: E402
import tfm2_ase  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zeri")
MAX_W = 28


def lines(img, top):
    d = ImageDraw.Draw(img)
    d.line([(0, 800), (1023, 800)], fill=(230, 30, 30, 255), width=2)
    d.line([(512, 0), (512, 1023)], fill=(40, 90, 230, 255), width=2)
    d.line([(0, top * 8), (1023, top * 8)], fill=(30, 170, 60, 255), width=2)
    for x in (512 - MAX_W * 4, 512 + MAX_W * 4):
        d.line([(x, 0), (x, 1023)], fill=(150, 60, 200, 255), width=2)
    return img


def on_white(can):
    img = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can))
    return img.resize((1024, 1024), Image.NEAREST)


def quality_bar():
    shots = []
    for h in ("jinx", "caitlyn", "syndra", "seraphine"):
        sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{h}"))
        f = sp.frames[sp.tag_frames("idle")[0]]
        shots.append((h, f.crop(f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox())))
    pad, z = 24, 8
    tall = max(s.height for _, s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for _, s in shots) + pad, tall + 2 * pad + 20), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for h, s in shots:
        big = s.resize((s.width * z, s.height * z), Image.NEAREST)
        img.alpha_composite(big, (x, pad + tall - big.height))
        d.text((x, pad + tall + 6), f"league_{h} {s.width}x{s.height}", fill=(0, 0, 0, 255))
        x += big.width + pad
    return img


def rows_sheet(can):
    bb = Image.fromarray(can).getbbox()
    fig = Image.fromarray(can).crop((bb[0] - 2, bb[1], bb[2] + 2, bb[3]))
    z = 12
    img = Image.new("RGBA", (fig.width * z + 60, fig.height * z), (255, 255, 255, 255))
    img.alpha_composite(fig.resize((fig.width * z, fig.height * z), Image.NEAREST), (60, 0))
    d = ImageDraw.Draw(img)
    for r in range(fig.height):
        d.text((4, r * z), f"{r:2d}", fill=(0, 0, 0, 255))
        d.line([(56, r * z), (img.width, r * z)], fill=(210, 210, 210, 255))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.join(a.out, "zeri")
    os.makedirs(out, exist_ok=True)
    can, _, _ = D.polish(**D.POLISH["p35c"])
    top = Image.fromarray(can).getbbox()[1]
    lines(on_white(can), top).convert("RGB").save(os.path.join(out, "1_target.png"))
    look = np.asarray(Image.open(os.path.join(SRC, "codex_model", "zeri_design_B_1x.png")).convert("RGBA")).copy()
    on_white(look).convert("RGB").save(os.path.join(out, "2_look.png"))
    shutil.copyfile(os.path.join(SRC, "codex_picture", "zeri-model-A.png"), os.path.join(out, "3_picture.png"))
    quality_bar().convert("RGB").save(os.path.join(out, "4_quality_bar.png"))
    rows_sheet(can).convert("RGB").save(os.path.join(out, "5_target_rows.png"))
    shutil.copyfile(os.path.join(SRC, "REFINE_PROMPTS.md"), os.path.join(a.out, "REFINE_PROMPTS.md"))
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()

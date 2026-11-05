#!/usr/bin/env python3
"""A pair of sunglasses beside Leona's Sunlight mark (the user's easter egg, 2026-11-05: 「太阳镜防晒」).

    python tools/art/fx_leona_shades.py [--review out.png]

Champions whose art wears sunglasses take 1 less from Leona's Sunlight: while one carries her Sunlight
(league_leona_sunlight, +10% damage taken) the match add-on league_eggs also gives him league_leona_shades (damaged_reduce
1 per Sunlight: +9%). This is that buff's picture: a small pair of black sunglasses with a glint, floating just right of
her sun mark (league_leona_fx's `sunlight`: rows -36..-25 over the pivot, columns -6..6) - an icon, not something worn,
since the heads stand at every height. Two frames, the glint moving across the lenses (an Animated buff view loops).
Written as league/effects/league_leona_shades.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

OUT = os.path.join(ROOT, "league", "effects", "league_leona_shades")
TAG = "shades"
HALF, TOP, BOTTOM = 19, -36, 0     # pivot-relative cell (x right, y down)
X0, Y0 = 8, -32                    # the glasses' top left: right of the sun mark, level with its middle
FRAME = ["kkkkkkkkkkk",            # k frame, l lens, . clear: two lenses hanging from one bar
         "kllllkllllk",
         ".kllk.kllk.",
         "..kk...kk.."]
DARK, LENS, SHINE, WHITE = (16, 14, 24), (40, 38, 64), (120, 132, 170), (255, 255, 255)
MS = [400, 400]


def frame(glint):
    a = np.zeros((BOTTOM - TOP + 1, 2 * HALF + 1, 4), np.uint8)
    for r, row in enumerate(FRAME):
        for c, ch in enumerate(row):
            col = {"k": DARK, "l": LENS}.get(ch)
            if col:
                a[Y0 + r - TOP, X0 + c + HALF] = (*col, 255)
    for c, r, col in glint:
        a[Y0 + r - TOP, X0 + c + HALF] = (*col, 255)
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the frames at 8x here, over the sun mark")
    a = ap.parse_args()
    frames = [frame([(1, 1, WHITE), (2, 2, SHINE), (7, 1, SHINE)]),
              frame([(2, 1, SHINE), (7, 1, WHITE), (8, 2, SHINE)])]
    cells = [(G.centre_frame(f, -HALF, TOP), ms) for f, ms in zip(frames, MS)]
    w, h = G.write_sheet(OUT, {TAG: cells}, share=True)
    print(f"league/effects/league_leona_shades#sheet.png {w}x{h}: {TAG} {len(cells)}f")
    if a.review:
        import json
        an = json.load(open(os.path.join(ROOT, "league", "effects", "league_leona_fx#anim.fanim"), encoding="utf-8"))
        d = an["anims"]["sunlight"]["frames"][0]["data"]
        sheet = Image.open(os.path.join(ROOT, "league", "effects", "league_leona_fx#sheet.png")).convert("RGBA")
        sun = sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"])))
        Z = 8
        img = Image.new("RGBA", ((2 * HALF + 3) * 2 * Z, (BOTTOM - TOP + 2) * Z), (90, 140, 90, 255))
        for k, f in enumerate(frames):
            cell = Image.new("RGBA", (2 * HALF + 1, BOTTOM - TOP + 1), (0, 0, 0, 0))
            # the sun's frame is centred on the pivot: its row -36 is its top
            cell.alpha_composite(sun, (HALF - sun.width // 2, -36 - TOP))
            cell.alpha_composite(Image.fromarray(f))
            img.alpha_composite(cell.resize((cell.width * Z, cell.height * Z), Image.NEAREST), (k * (2 * HALF + 3) * Z, 0))
        img.convert("RGB").save(a.review)
        print("review", a.review)


if __name__ == "__main__":
    main()

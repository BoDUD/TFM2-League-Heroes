#!/usr/bin/env python3
"""Sion's step-1 pack for Codex (assets/source/sion/MODEL_PROMPTS.md): the game-size design redrawn on the grid,
3/4 front + side-on facing right.

    python tools/art/pack_sion_model.py --out dist/sion_packs/sion_model_pack

The user picked picture A (axe hanging by the near leg) at 44 rows crown to soles (2026-10-14). Codex's own 44-row cut
and a majority cut of its raw draft both read muddy (small face, specks), so Codex draws the sprite again square by
square on a fixed grid (art-spec "A muddy design", Gwen's way) - the front keeping the guide's size and place, the side
the same figure seen from the side (memory side-view-design: every action strip is drawn from the side view).
  1_current_grid.png   design/A44_cut.png at 19 px a square on the 1536 x 1024 canvas, a yellow measuring grid with
                       numbers: size, proportions, pose, place (crown row 7, soles row 50)
  2_look_draft.png     Codex's own raw draft A read back (design/A_draft_rg.png) at 8x: the look and the details
  3_league_head.png    League's head close-up      (local renders from the step-0 pack, Riot's model: never committed)
  4_league_front.png   League's idle, 3/4 front
  5_league_side.png    League's idle seen from the side (yaw 85, mirrored to face right)
  6_league_axe.png     League's axe raised
  7-9 style            darius / nautilus / alistar 1x idle at 8x (assets/source/sion/style_ref)
  10_side_canvas.png   the empty grid for the side view: the crown and soles rows, the standing column
"""
import argparse
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "sion")
REFS = os.path.join(ROOT, "dist", "sion_packs", "sion_pack0", "refs")
SQ = 19                         # Codex's square
COLS, ROWS = 80, 53             # 1520 x 1007 inside the 1536 x 1024 canvas
CROWN, SOLE = 7, 50             # top of the bald head, the soles: 44 rows
CUT_CROWN = 6                   # the crown's row in design/A44_cut.png
STAND = 40                      # the side view's standing column (between the feet)


def grid(img, lines=True):
    d = ImageDraw.Draw(img)
    if lines:
        for c in range(COLS + 1):
            d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(240, 200, 0, 255), width=1)
        for r in range(ROWS + 1):
            d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(0, ROWS, 5):
        d.text((2, r * SQ + 4), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 5):
        d.text((c * SQ + 5, 2), str(c), fill=(0, 0, 200, 255))
    return d


def current():
    cut = np.array(Image.open(os.path.join(SRC, "design", "A44_cut.png")).convert("RGBA"))
    h, w = cut.shape[:2]
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    top, left = CROWN - CUT_CROWN, (COLS - w) // 2
    assert top + h - 1 == SOLE, (top, h)
    can[top:top + h, left:left + w] = cut
    img = Image.new("RGBA", (1536, 1024), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can).resize((COLS * SQ, ROWS * SQ), Image.NEAREST))
    grid(img)
    return img.convert("RGB")


def side_canvas():
    img = Image.new("RGBA", (1536, 1024), (255, 255, 255, 255))
    d = grid(img)
    d.line([(0, CROWN * SQ), (COLS * SQ, CROWN * SQ)], fill=(220, 40, 40, 255), width=3)
    d.line([(0, (SOLE + 1) * SQ), (COLS * SQ, (SOLE + 1) * SQ)], fill=(40, 160, 40, 255), width=3)
    d.line([(STAND * SQ, CROWN * SQ), (STAND * SQ, (SOLE + 1) * SQ)], fill=(80, 80, 220, 255), width=2)
    return img.convert("RGB")


def x8(path):
    im = Image.open(path).convert("RGBA")
    out = Image.new("RGBA", (im.width + 4, im.height + 4), (255, 255, 255, 255))
    out.alpha_composite(im, (2, 2))
    return out.resize((out.width * 8, out.height * 8), Image.NEAREST).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    current().save(os.path.join(a.out, "1_current_grid.png"))
    x8(os.path.join(SRC, "design", "A_draft_rg.png")).save(os.path.join(a.out, "2_look_draft.png"))
    for name, ref in (("3_league_head", "3_sion_league_head"), ("4_league_front", "1_sion_league_front"),
                      ("5_league_side", "9_sion_league_side"), ("6_league_axe", "8_sion_league_axe")):
        shutil.copyfile(os.path.join(REFS, ref + ".png"), os.path.join(a.out, name + ".png"))
    for k, hero in ((7, "darius"), (8, "nautilus"), (9, "alistar")):
        shutil.copyfile(os.path.join(SRC, "style_ref", f"{hero}_idle_x8.png"), os.path.join(a.out, f"{k}_style_{hero}.png"))
    side_canvas().save(os.path.join(a.out, "10_side_canvas.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(a.out, "MODEL_PROMPTS.md"))
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()

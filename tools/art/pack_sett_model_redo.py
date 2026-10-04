#!/usr/bin/env python3
"""Sett's step 1, second round: the pictures that go with assets/source/sett/MODEL_REDO.md.

    python tools/art/pack_sett_model_redo.py --out <folder>

Codex's first round (assets/source/sett/codex_model/) did not draw at game size: its raw generations read back on
their own grids (scripts/regrid.py) as 50 x 81 (B) and 78 x 118 (A) squares, and the 42-row designs it delivered were
made by resampling them - the face, the mantle and the fists broke into specks. Raw B's readback is clean, so the
second round asks for that drawing again, square by square, a size smaller (league_sivir's second round):
  1_draft.png         raw B read back on its own grid (50 x 81), at 8x on white: copy it
  2_target_size.png   a 1024x1024 canvas (128 x 128 squares at 8x): the draft scaled evenly to TOTAL rows (grey),
                      red = the bottom of the soles' row (row 99), blue = the middle column, green = the ear tips,
                      orange / purple = the chin of version A / B
  3_quality_bar.png   five pack fighters as they are in the game now, at 8x (pack_sett_model.py)
  4_rejected.png      Codex's two resampled 42-row designs at 8x: what not to do
  5_size_guide.png    the draft scaled evenly to TOTAL rows in colour (blurry): only what fits where
  6_face_ref.png      the draft's head (the ear tips to just under the chin, 24 rows) at 16x
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pack_sett_model as P  # noqa: E402
from regrid import regrid  # noqa: E402

MODEL = os.path.join(ROOT, "assets", "source", "sett", "codex_model")
RAW = os.path.join(MODEL, "sett_design_B_raw.png")
HEAD_ROWS = 24                   # the draft's ear tips to just under its chin


def draft():
    out, _, _ = regrid(np.asarray(Image.open(RAW).convert("RGBA")))
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def on_white(im, z):
    bg = Image.new("RGBA", (im.width * z, im.height * z), (255, 255, 255, 255))
    bg.alpha_composite(im.resize((im.width * z, im.height * z), Image.NEAREST))
    return bg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    d = draft()
    print(f"draft: {d.width} x {d.height} squares")
    on_white(d, 8).convert("RGB").save(os.path.join(args.out, "1_draft.png"))
    P.target_size(d).convert("RGB").save(os.path.join(args.out, "2_target_size.png"))
    P.quality_bar().convert("RGB").save(os.path.join(args.out, "3_quality_bar.png"))
    rej = [Image.open(os.path.join(MODEL, f"sett_design_{k}_1x.png")).convert("RGBA") for k in "AB"]
    rej = [r.crop(r.getchannel("A").getbbox()) for r in rej]
    gap = 6
    both = Image.new("RGBA", (sum(r.width for r in rej) + gap, max(r.height for r in rej)), (0, 0, 0, 0))
    both.alpha_composite(rej[0], (0, 0))
    both.alpha_composite(rej[1], (rej[0].width + gap, 0))
    on_white(both, 8).convert("RGB").save(os.path.join(args.out, "4_rejected.png"))
    P.size_guide(d).convert("RGB").save(os.path.join(args.out, "5_size_guide.png"))
    on_white(d.crop((0, 0, d.width, HEAD_ROWS)), 16).convert("RGB").save(os.path.join(args.out, "6_face_ref.png"))
    print("wrote", ", ".join(sorted(os.listdir(args.out))))


if __name__ == "__main__":
    main()

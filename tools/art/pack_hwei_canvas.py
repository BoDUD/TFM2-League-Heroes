#!/usr/bin/env python3
"""Hwei's last effect for GPT's image generator (assets/source/hwei/PROMPT_R_CANVAS.md; the user, 2026-10-22: 「慧还差一张
你写好提示词让gpt做吧」): r_canvas, Spiraling Despair's painted spiral on the ground, 14 frames - Gemini left it out and
GPT's canvas tops out at 1536 x 1024, so the frames go in a grid of 4 x 4 cells (the last two empty) instead of the FX
pack's row.

    python tools/art/pack_hwei_canvas.py [--out dist/hwei_packs]

Writes <out>/hwei_canvas_gpt_pack.zip: PROMPT.md; 1_style_r_paint.png and 2_style_r_burst.png (Gemini's pictures of the
ult, the style to match: the user's JPGs from C:/t/hw_work/gemini, kept local); 3_layout_guide.png (the canvas drawn by
process_hwei_fx.draw_r_canvas, 8x, in the 4 x 4 grid: the oval's size and place per frame only); 4_lol_ref.png (League's
textures for the spell: Riot's, kept local); 5_hwei_size.png (the pack's size sheet).
"""
import argparse
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402  ref_sheet
import process_hwei_fx as PH  # noqa: E402  draw_r_canvas

GEMINI = "C:/t/hw_work/gemini"
REF = "C:/t/hw_work/fxref"
SIZE = "C:/t/hw_work/fx/hwei_fx_pack/design/hwei_size.png"     # pack_hwei_fx.py's size sheet
CELL = (384, 256)


def guide(path):
    """The drawn canvas's 14 frames, 6x, each in a 384 x 256 cell of a 4 x 4 grid, the oval a little below the middle."""
    frames = PH.draw_r_canvas()
    can = Image.new("RGBA", (CELL[0] * 4, CELL[1] * 4), (0, 0, 0, 255))
    for k, f in enumerate(frames):
        im = Image.fromarray(f).resize((f.shape[1] * 6, f.shape[0] * 6), Image.NEAREST)
        x0 = (k % 4) * CELL[0] + (CELL[0] - im.width) // 2
        y0 = (k // 4) * CELL[1] + round(CELL[1] * 0.56) - im.height // 2
        can.alpha_composite(im, (x0, y0))
    can.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "hwei_packs"))
    a = ap.parse_args()
    work = "C:/t/hw_work/fx/hwei_canvas_gpt_pack"
    if os.path.isdir(work):
        shutil.rmtree(work)
    os.makedirs(work)
    for src, dst in (("g22_r_paint.jpg", "1_style_r_paint.png"), ("g20.jpg", "2_style_r_burst.png")):
        im = Image.open(os.path.join(GEMINI, src)).convert("RGB")
        im.resize((2048, round(im.height * 2048 / im.width)), Image.LANCZOS).save(os.path.join(work, dst))
    guide(os.path.join(work, "3_layout_guide.png"))
    RF.REF = REF
    RF.GROUPS = [("r_canvas (cracks, swirling strokes, gold strands)",
                  ["hwei_base_r_cracks", "hwei_base_paintstrokediffuse_rotate", "hwei_base_goldstrand01dissolve",
                   "hwei_base_foundation_palette_ssgold"])]
    RF.ref_sheet(os.path.join(work, "4_lol_ref.png"))
    shutil.copyfile(SIZE, os.path.join(work, "5_hwei_size.png"))
    shutil.copyfile(os.path.join(ROOT, "assets", "source", "hwei", "PROMPT_R_CANVAS.md"), os.path.join(work, "PROMPT.md"))
    os.makedirs(a.out, exist_ok=True)
    zp = os.path.join(a.out, "hwei_canvas_gpt_pack.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(work)):
            z.write(os.path.join(work, fn), fn)
    print(zp, os.path.getsize(zp) // 1024, "KB")


if __name__ == "__main__":
    main()

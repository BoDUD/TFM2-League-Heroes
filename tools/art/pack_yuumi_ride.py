#!/usr/bin/env python3
"""Yuumi's ride-picture pack for Codex (assets/source/yuumi/RIDE_PROMPTS.md): B, the cat lying on her flat book over
the attached ally's head, redrawn on a fixed grid at its game count (Gwen's on-grid way, assets/source/gwen/codex_grid).

    python tools/art/pack_yuumi_ride.py [--out %TEMP%/yu_work/yuumi_ride_pack]

The user's picks (2026-10-19): 14 game px tall at 1.5 squares a game px -> ROWS = 21 squares (about 24 wide). Step 1's
B drafts (55-58 rows) cut or voted down to 21 rows came out muddy (muddy-design rule: an on-grid redraw, never more
hand work). The canvas: 1254 x 1254, PX = 50 px a square, the bottom (the tail tuft) on y 1150.
Writes <out>/ (and <out>.zip): RIDE_PROMPTS.md, 1_picture_B.png (step 0), 1_model_B1.png / 1_model_B2.png (step 1's
drafts: the look and pose), 2_target_B.png (B-1 voted to the count on the grid: size and place only, details broken),
3_layout_B.png (the same with grid lines), 4_head.png (the approved idle's head, 8x: the face to keep), 5_method/ (Gwen's
on-grid delivery and its HANDOFF: the way of working), style/6_style_zoe.png.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_yuumi_model as D  # noqa: E402
import pack_yuumi_model as M  # noqa: E402
import pixel_down as PD  # noqa: E402
from pack_gangplank_model import crop, cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yuumi")
GWEN = os.path.join(ROOT, "assets", "source", "gwen", "codex_grid")
PX, SOLE, ROWS = 50, 1150, 21
HEAD_ROWS = 24          # the idle's head and collar: its top rows in hd/idle.png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(M.TMP, "yuumi_ride_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    os.makedirs(os.path.join(out, "5_method"))
    raw = D.read_back("B-1")
    g, _ = PD.pixelate(raw, ROWS / raw.shape[0], (raw.shape[1] / 2, raw.shape[0]), PD.edge_colour(raw))
    g = crop(g)
    can, x0, y0 = M.place(g, PX, SOLE)
    can.save(os.path.join(out, "2_target_B.png"))
    lay = Image.new("RGBA", (M.CANVAS, M.CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(can)
    M.lines(lay, y0, None, f"B: orange top y {y0}   red bottom y {SOLE}   one square = {PX} px   "
                           f"{g.shape[1]} x {g.shape[0]} squares", PX, SOLE)
    lay.convert("RGB").save(os.path.join(out, "3_layout_B.png"))
    print("B", g.shape[1], "x", g.shape[0], "at", (x0, y0))
    shutil.copyfile(D.lp(os.path.join(SRC, "codex_picture", "yuumi-picture", "yuumi-B.png")),
                    os.path.join(out, "1_picture_B.png"))
    for n in ("1", "2"):
        shutil.copyfile(D.lp(os.path.join(SRC, "codex_model", "yuumi-model", f"yuumi-model-B-{n}.png")),
                        os.path.join(out, f"1_model_B{n}.png"))
    idle = np.asarray(Image.open(D.lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    h = idle[:HEAD_ROWS]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), M.GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for f in ("gwen-grid-A.png", "gwen-grid-A_1x.png", "HANDOFF.md"):
        shutil.copyfile(D.lp(os.path.join(GWEN, f)), os.path.join(out, "5_method", f))
    cut("zoe", "hd_idle", os.path.join(out, "style", "6_style_zoe.png"))
    shutil.copyfile(D.lp(os.path.join(SRC, "RIDE_PROMPTS.md")), os.path.join(out, "RIDE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()

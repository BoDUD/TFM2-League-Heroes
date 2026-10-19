#!/usr/bin/env python3
"""Zoe's step-1 pack for Codex (assets/source/zoe/MODEL_PROMPTS.md): the step-0 design at game size, squares drawn BIG
so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_zoe_model.py [--out %TEMP%/zo_work/zoe_model_pack] [--lol D:/WeGameApps/lol]

The user's pick (2026-10-19): picture A (League's idle), 35 game px crown to soles at PPU 1.5 -> ROWS = 53 squares. Her
hair streams back about as far as she is tall (A is 62 squares wide at that count), so a square is PX = 19 px: the
figure is 1178 x 1007 on Codex's own 1254 canvas. Two pictures of the same Zoe at that count (side-view-design: every
action is drawn from the side view):
  A  the idle, 3/4 front (step 0's A, cut to the count: 2_target_A.png),
  S  SIDE-ON facing right (League's idle at yaw +15 as the layout: 3_side_ref.png, faded, grid on).
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png / 1_picture_B.png (step 0, the look to keep; B shows
the arms hanging), 2_target_A.png (cut to the count at PX: size, place, pose - details broken), 3_layout_A.png (A with
the grid, crown / eye / ground lines), 3_side_ref.png (the League render at the count: Riot's, kept local), 4_head.png
(A's head read back, 8x), style/5..7.
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
import pack_rammus_model as RM  # noqa: E402
from design_zoe_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zoe")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "zo_work")
PX = 19                 # pixels a square on the canvas
SOLE_Y = 1197           # the soles' bottom edge (63 squares x 19)
ROWS = 53               # 35 game px x PPU 1.5, crown to soles
EYE_ROW = 30            # her eyes' row in hd/A.png (rows 27-33: violet cols 72-78, blue cols 83-86)
HEAD = (0, 50, 54, 100)  # rows / cols of the buns, the face and the scarf in hd/A.png
GREY = (225, 225, 225)
STYLE = {"5_style_janna.png": ("janna", "hd_idle"), "6_style_nami.png": ("nami", "hd_idle"),
         "7_style_katarina.png": ("katarina", "hd_idle")}
PROPS = ["Zoe_Base_Jumprope_Mat", "Zoe_Base_TennisRac_Mat", "Zoe_Base_Yoyo_Mat", "Zoe_Base_IceCream_Mat"]
# League renders laid out at the count: name -> (frame, yaw)
REFS = {"3_side_ref.png": ("zoe_idle1@0", 15)}


def configure():
    """pack_rammus_model's layout helpers, set to this pack's square, ground line, count and champion."""
    RM.PX, RM.SOLE_Y, RM.ROWS = PX, SOLE_Y, ROWS
    run = RM.subprocess.run

    def zoe_run(cmd, **kw):   # its pose_ref call names Rammus: render Zoe without her props
        if "--champ" in cmd:
            cmd = list(cmd)
            cmd[cmd.index("--champ") + 1] = "Zoe"
            for p in PROPS:
                cmd += ["--hide-submesh", p]
        return run(cmd, **kw)
    RM.subprocess = type("S", (), {"run": staticmethod(zoe_run)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "zoe_model_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    configure()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    work = out + "_measure"
    os.makedirs(work, exist_ok=True)
    A = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    k = ROWS / A.shape[0]
    gA = RM.target(A, k)
    canA, xA, yA = RM.place(gA)
    canA.save(os.path.join(out, "2_target_A.png"))
    eye = SOLE_Y - round((A.shape[0] - EYE_ROW) * k) * PX
    lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(canA)
    RM.lines(lay, yA, eye, f"A: orange crown y {yA}   blue eyes y {eye}   red ground y {SOLE_Y}   one square = {PX} px"
                           f"   {gA.shape[1]} x {gA.shape[0]} squares")
    lay.convert("RGB").save(os.path.join(out, "3_layout_A.png"))
    for fname, (frame, yaw) in REFS.items():
        can, top, w = RM.league_ref(a.lol, frame, yaw, work, fname[:-4])
        RM.lines(can, top, None, f"{fname[2:-4]}: League's model at the count (faded): top y {top}   ground y {SOLE_Y}   "
                                 f"about {w / PX:.0f} squares wide   one square = {PX} px")
        can.convert("RGB").save(os.path.join(out, fname))
    for n in "AB":
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "zoe-picture", f"zoe-{n}.png")),
                        os.path.join(out, f"1_picture_{n}.png"))
    r0, r1, c0, c1 = HEAD
    h = A[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"A {gA.shape[1]}x{gA.shape[0]} at ({xA},{yA}), eyes y {eye}; ground y {SOLE_Y} ->", zp)


if __name__ == "__main__":
    main()

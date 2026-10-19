#!/usr/bin/env python3
"""Cho'Gath's step-1 pack for Codex (assets/source/chogath/MODEL_PROMPTS.md): design A at game size in two views,
the 3/4 front (the idle, the ban-pick card, the one face of every frame) and SIDE-ON facing right (the base of the
run and the attacks), squares drawn BIG so the image generator's habit of filling the canvas lands on the right
count (league_gangplank round 2: 21 px squares on 1254 came back on the count).

    python tools/art/pack_chogath_model.py [--out %TEMP%/cg_work/chogath_model_pack] [--lol D:/WeGameApps/lol]

The user's pick (2026-10-19): A (League's idle, the scythes raised), 38 game px scythe top to soles, PPU 1.2 -> ROWS =
46 squares; he is ~70 squares wide at that, so the squares are 16 px (1120 px on Codex's own 1254 canvas).
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png (step 0's A, the look to keep), 2_target.png (A cut
to the count at PX on the canvas: size, place, pose - its details are broken), 3_layout.png (with the grid, the
top, eye and ground lines), 4_head.png (A's head read back, 8x), 5_side_ref.png (League's idle nearly side-on,
facing right), 6_side_layout.png (that render at the same height on the grid: where the side view goes), style/7..10.
League's renders are Riot's: kept local, never committed. The height of a figure does not change with the yaw, so the
side view takes the same 46 rows.
"""
import argparse
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_chogath_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "chogath")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "cg_work")
PX = 16                 # pixels a square on the canvas
CANVAS = 1254
SOLE_Y = 1120           # the soles' bottom edge (70 squares x 16)
ROWS = 46               # 38 game px x PPU 1.2
EYE_ROW = 35            # his eyes' row in hd/A.png (cyan squares, rows 35-37, cols 66-69 and 74-75)
HEAD = (28, 51, 56, 89)  # rows / cols of the head (crown to jaw, the tusks) in hd/A.png
GREY = (225, 225, 225)
STYLE = {"7_style_reksai.png": ("reksai", "hd_idle"), "8_style_volibear.png": ("volibear", "hd_idle"),
         "9_style_rammus.png": ("rammus", "hd_idle"), "10_style_urgot.png": ("urgot", "hd_idle")}


def lines(img, top, eye, label):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(img)
    dr = ImageDraw.Draw(lay)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    dr.line([(0, top), (CANVAS, top)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, eye), (CANVAS, eye)], fill=(60, 110, 230, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), label, fill=(40, 40, 40, 255))
    return lay.convert("RGB")


def side_render(lol, work):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Chogath",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1600",
           "--fit", "0.5", "--ground", "0.84", "--width", "1.8", "--yaw", "75", "--name", "side", "--out", work,
           "--frame", "chogath_idle1@0"]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "side.png")).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a).crop(Image.fromarray(a).getbbox())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "chogath_model_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    k = ROWS / d.shape[0]
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    op = g[..., 3] > 0
    g = g[np.ix_(np.any(op, 1), np.any(op, 0))]
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    eye = SOLE_Y - round((d.shape[0] - EYE_ROW) * k) * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target.png"))
    lines(can, y0, eye, f"green top y {y0}   blue eyes y {eye}   red ground y {SOLE_Y}   one square = {PX} px   "
                        f"{gw} x {gh} squares").save(os.path.join(out, "3_layout.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "chogath-picture", "raw", "chogath-A-generated.png")),
                    os.path.join(out, "1_picture_A.png"))
    r0, r1, c0, c1 = HEAD
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    # the side view: League's idle at yaw 75, the same top-to-sole height, soles on the ground line
    side = side_render(a.lol, out + "_work")
    bg = Image.new("RGB", side.size, GREY)
    bg.paste(side, (0, 0), side)
    bg.save(os.path.join(out, "5_side_ref.png"))
    s = ROWS * PX / side.height
    sm = side.resize((round(side.width * s), round(side.height * s)), Image.LANCZOS)
    am = np.asarray(sm).copy()
    am[..., 3] = (am[..., 3] * 0.45).astype(np.uint8)
    sc = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    sx = (CANVAS - sm.width) // 2
    sc.alpha_composite(Image.fromarray(am), (sx, SOLE_Y - sm.height))
    lines(sc, SOLE_Y - ROWS * PX, eye, f"SIDE VIEW: green top y {SOLE_Y - ROWS * PX}   blue eyes y {eye}   red ground "
                                       f"y {SOLE_Y}   one square = {PX} px   {ROWS} squares tall (faded: size only)"
          ).save(os.path.join(out, "6_side_layout.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{gw}x{gh} squares at ({x0},{y0}), top y {y0}, eyes y {eye}, ground y {SOLE_Y}; side "
          f"{sm.width}x{sm.height} px ->", zp)


if __name__ == "__main__":
    main()

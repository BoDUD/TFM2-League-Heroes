#!/usr/bin/env python3
"""Graves's step-1 pack for Codex (assets/source/graves/MODEL_PROMPTS.md): design A at game size in two views, the
3/4 front (the idle, the ban-pick card, the one face of every frame) and SIDE-ON facing right (the base of the run and
the casts), squares drawn BIG so the image generator's habit of filling the canvas lands on the right count.

    python tools/art/pack_graves_model.py [--out C:/t/gv_work/graves_model_pack] [--lol D:/WeGameApps/lol]

The user's pick (2026-10-20): A (League's long shotgun), 38 game px hair top to soles, PPU 1.5 -> ROWS = 57 squares;
the shotgun reaches out to the right, so the figure is ~66 squares wide; 16 px squares put it 912 px tall on Codex's
own 1254 canvas.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png and 1b_picture_SA.png (step 0's A and its side: the
look to keep), 2_target.png (A cut to the count at PX on the canvas: size, place, pose - its details are broken),
3_layout.png (with the grid, the hair top, eye and ground lines), 4_head.png (A's head read back, 8x),
5_side_ref.png (League's idle side-on, facing right: the body), 6_side_layout.png (step 0's side SA cut to the count),
style/7..10. League's renders are Riot's: kept local, never committed.
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
from design_graves_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402
from review_graves_size import body_height  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "graves")
PX = 16                 # pixels a square on the canvas
CANVAS = 1254
SOLE_Y = 1168           # the soles' bottom edge (73 squares x 16)
ROWS = 57               # hair top to soles: 38 game px x PPU 1.5
EYE_ROW = 24            # his eyes' row in hd/A.png (rows 23-24, cols 67-77)
HEAD = (0, 36, 48, 92)  # rows / cols of the head (hair top to the beard's tip, the scarf's collar) in hd/A.png
GREY = (225, 225, 225)
STYLE = {"7_style_gangplank.png": ("gangplank", "hd_idle"), "8_style_jayce.png": ("jayce", "hd_idle"),
         "9_style_jarvaniv.png": ("jarvaniv", "hd_idle"), "10_style_swain.png": ("swain", "hd_idle")}


def lines(img, marks, label):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(img)
    dr = ImageDraw.Draw(lay)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    for y, colour in marks:
        dr.line([(0, y), (CANVAS, y)], fill=colour, width=3)
    dr.text((12, 12), label, fill=(40, 40, 40, 255))
    return lay.convert("RGB")


def side_render(lol, work):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Graves",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1600",
           "--fit", "0.5", "--ground", "0.84", "--width", "1.6", "--yaw", "75", "--name", "side", "--out", work,
           "--frame", "graves_idle1@0"]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "side.png")).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a).crop(Image.fromarray(a).getbbox())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/gv_work/graves_model_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    k = ROWS / body_height(d)
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    op = g[..., 3] > 0
    g = g[np.ix_(np.any(op, 1), np.any(op, 0))]
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    crown = SOLE_Y - ROWS * PX    # the hair top
    eye = SOLE_Y - round((d.shape[0] - EYE_ROW) * k) * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target.png"))
    marks = [(crown, (40, 170, 60, 255)), (eye, (60, 110, 230, 255)), (SOLE_Y, (230, 40, 40, 255))]
    lines(can, marks, f"green hair top y {crown}   blue eyes y {eye}   red ground y {SOLE_Y}"
                      f"   one square = {PX} px   {gw} x {gh} squares").save(os.path.join(out, "3_layout.png"))
    raw = os.path.join(SRC, "codex_picture", "raw")
    shutil.copyfile(lp(os.path.join(raw, "graves-A.png")), os.path.join(out, "1_picture_A.png"))
    shutil.copyfile(lp(os.path.join(raw, "graves-SA.png")), os.path.join(out, "1b_picture_SA.png"))
    r0, r1, c0, c1 = HEAD
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    # the side view: League's idle at yaw 75, the same crown-to-sole height, soles on the ground line
    side = side_render(a.lol, out + "_work")
    bg = Image.new("RGB", side.size, GREY)
    bg.paste(side, (0, 0), side)
    bg.save(os.path.join(out, "5_side_ref.png"))
    # the side layout: step 0's side (SA) cut to the same count - the body's size and place, the shotgun's length
    ds = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "SA.png"))).convert("RGBA"))
    ks = ROWS / body_height(ds)
    gs, _ = PD.pixelate(ds, ks, (ds.shape[1] / 2, ds.shape[0]), PD.edge_colour(ds))
    ops = gs[..., 3] > 0
    gs = gs[np.ix_(np.any(ops, 1), np.any(ops, 0))]
    sc = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    sx0, sy0 = (CANVAS // PX - gs.shape[1]) // 2 * PX, SOLE_Y - gs.shape[0] * PX
    sc.paste(Image.fromarray(up(gs, PX)), (sx0, sy0))
    lines(sc, [(crown, (40, 170, 60, 255)), (eye, (60, 110, 230, 255)), (SOLE_Y, (230, 40, 40, 255))],
          f"SIDE VIEW (your step-0 side cut to the count): green hair top y {crown}   blue eyes y {eye}   "
          f"red ground y {SOLE_Y}   one square = {PX} px   {gs.shape[1]} x {gs.shape[0]} "
          f"squares").save(os.path.join(out, "6_side_layout.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{gw}x{gh} squares at ({x0},{y0}), hair top y {crown}, eyes y {eye}, ground y {SOLE_Y}; "
          f"side {gs.shape[1]}x{gs.shape[0]} squares ->", zp)


if __name__ == "__main__":
    main()

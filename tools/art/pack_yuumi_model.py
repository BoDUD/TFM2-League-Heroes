#!/usr/bin/env python3
"""Yuumi's step-1 pack for Codex (assets/source/yuumi/MODEL_PROMPTS.md): the step-0 designs at game size, squares drawn
BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_yuumi_model.py [--out %TEMP%/yu_work/yuumi_model_pack] [--lol D:/WeGameApps/lol]

The user's picks (2026-10-19): A (League's idle in the open book) 32 game px orb top to the book's bottom at PPU 1.5 ->
ROWS = 48 squares; B (lying on the flat book, the attached look riding the ally's head) 14 game px -> B_ROWS = 21;
C (the closed book, her death) at A's scale (the book in A is about 37 squares wide). Pictures of the same Yuumi:
  A  the idle, 3/4 front (2_target_A.png: step 0's A cut to the count),
  S  SIDE-ON facing right in the book (League's idle at yaw 80 as the layout: 3_side_ref.png) - the base of the actions,
  L  the leap: out of the book, stretched long, the book trailing (League's attack and W dash: 3_leap_ref*.png),
  R  Final Chapter: the book standing upright and open, the cat clinging to its edge (3_ult_ref.png),
  B  attached (2_target_B.png, its own bigger squares), C  the closed book (2_target_C.png, its own squares).
A, S, L and R share one square (PX 22, one ground line); B and C are drawn alone on bigger squares (they are small).
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_{A,B,C}.png (step 0, the look to keep), 2_target_*.png,
3_layout_A.png, 3_*_ref.png (League renders at the count: Riot's, kept local), 4_head.png (A's head read back, 8x),
style/5..7.
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
from design_yuumi_hd import lp  # noqa: E402
from pack_gangplank_model import crop, cut, up  # noqa: E402
from pack_yuumi_picture import LOOK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yuumi")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "yu_work")
CANVAS = 1254
GREY = (225, 225, 225)
# A, S, L, R: one square, one ground line; 48 squares orb top to the book's bottom
PX, SOLE_Y, ROWS = 22, 1188, 48
# B and C: their own canvases, bigger squares
B_PX, B_SOLE, B_ROWS = 44, 1188, 21
C_PX, C_SOLE, C_COLS = 30, 1170, 37
EYE_ROW = 47            # her eyes' row in hd/A.png (cyan irises, rows 40-55)
HEAD = (0, 80, 40, 122)  # rows / cols of the antenna, the ears, the face and the collar in hd/A.png
STYLE = {"5_style_zoe.png": ("zoe", "hd_idle"), "6_style_smolder.png": ("smolder", "hd_idle"),
         "7_style_katarina.png": ("katarina", "hd_idle")}
IDLE = "yuumi_idle01@0"
# League renders at the count (A's scale): name -> (frame, yaw)
REFS = {"3_side_ref.png": (IDLE, 80), "3_leap_ref.png": ("yuumi_attack01@333", 80),
        "3_ult_ref.png": ("yuumi_spell4_in@1250", 70)}


def lines(can, top, eye, label, px, sole):
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, px * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(sole % (px * 5), CANVAS, px * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    dr.line([(0, top), (CANVAS, top)], fill=(230, 150, 30, 255), width=3)
    if eye is not None:
        dr.line([(0, eye), (CANVAS, eye)], fill=(60, 110, 230, 255), width=3)
    dr.line([(0, sole), (CANVAS, sole)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), label, fill=(40, 40, 40, 255))


def target(d, k):
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    return crop(g)


def place(g, px, sole):
    gh, gw = g.shape[:2]
    x0 = (CANVAS // px - gw) // 2 * px
    y0 = sole - gh * px
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, px)), (x0, y0))
    return can, x0, y0


def render(lol, frame, yaw, work, name):
    """One League render (one camera for every frame: the same --fit / --size), keyed, cropped to the figure."""
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Yuumi", "--hq",
           "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1600", "--fit", "0.5",
           "--ground", "0.84", "--width", "1.8", "--yaw", str(yaw), "--name", name, "--out", work, "--frame", frame] + LOOK
    subprocess.run(cmd, check=True, capture_output=True)
    a = np.asarray(Image.open(os.path.join(work, name + ".png")).convert("RGBA")).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    fig = Image.fromarray(a)
    return fig.crop(fig.getbbox())


def faded(fig, k, right=False):
    """A render scaled by k, faded, on the white grid canvas, its lowest point on the ground line; centred, or its right
    end two squares from the right edge (the leap is wider than the canvas: its tail runs off on the left)."""
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    f = np.asarray(fig).copy()
    f[..., 3] = (f[..., 3] * 0.45).astype(np.uint8)
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    x = CANVAS - 2 * PX - fig.width if right else round(CANVAS / 2 - fig.width / 2)
    can.alpha_composite(Image.fromarray(f), (x, SOLE_Y - fig.height))
    return can, SOLE_Y - fig.height, fig.width, fig.height


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "yuumi_model_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    work = out + "_measure"
    os.makedirs(work, exist_ok=True)
    hd = {n: np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{n}.png"))).convert("RGBA")) for n in "ABC"}

    kA = ROWS / hd["A"].shape[0]
    gA = target(hd["A"], kA)
    canA, xA, yA = place(gA, PX, SOLE_Y)
    canA.save(os.path.join(out, "2_target_A.png"))
    eye = SOLE_Y - round((hd["A"].shape[0] - EYE_ROW) * kA) * PX
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(canA)
    lines(lay, yA, eye, f"A: orange orb top y {yA}   blue eyes y {eye}   red ground y {SOLE_Y}   one square = {PX} px   "
                        f"{gA.shape[1]} x {gA.shape[0]} squares", PX, SOLE_Y)
    lay.convert("RGB").save(os.path.join(out, "3_layout_A.png"))
    print("A", gA.shape[1], "x", gA.shape[0], "top", yA, "eyes", eye)

    gB = target(hd["B"], B_ROWS / hd["B"].shape[0])
    canB, _, yB = place(gB, B_PX, B_SOLE)
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(canB)
    lines(lay, yB, None, f"B: orange top y {yB}   red bottom y {B_SOLE}   one square = {B_PX} px   "
                         f"{gB.shape[1]} x {gB.shape[0]} squares", B_PX, B_SOLE)
    lay.convert("RGB").save(os.path.join(out, "2_target_B.png"))
    print("B", gB.shape[1], "x", gB.shape[0], "top", yB)

    gC = target(hd["C"], C_COLS / hd["C"].shape[1])
    canC, _, yC = place(gC, C_PX, C_SOLE)
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(canC)
    lines(lay, yC, None, f"C: orange top y {yC}   red ground y {C_SOLE}   one square = {C_PX} px   "
                         f"{gC.shape[1]} x {gC.shape[0]} squares", C_PX, C_SOLE)
    lay.convert("RGB").save(os.path.join(out, "2_target_C.png"))
    print("C", gC.shape[1], "x", gC.shape[0], "top", yC)

    # League renders: the idle sets the scale (its height = ROWS squares), every pose takes the same scale
    figs = {f: render(a.lol, frame, yaw, work, f[:-4]) for f, (frame, yaw) in REFS.items()}
    k = ROWS * PX / figs["3_side_ref.png"].height
    for fname, fig in figs.items():
        can, top, w, h = faded(fig, k, right=fname == "3_leap_ref.png")
        lines(can, top, None, f"{fname[2:-4]}: League's model at A's scale (faded): top y {top}   ground y {SOLE_Y}   "
                              f"about {w / PX:.0f} x {h / PX:.0f} squares   one square = {PX} px", PX, SOLE_Y)
        can.convert("RGB").save(os.path.join(out, fname))
        print(fname, f"{w / PX:.0f} x {h / PX:.0f} squares")

    for n in "ABC":
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "yuumi-picture", f"yuumi-{n}.png")),
                        os.path.join(out, f"1_picture_{n}.png"))
    r0, r1, c0, c1 = HEAD
    h = hd["A"][r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()

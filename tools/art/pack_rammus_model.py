#!/usr/bin/env python3
"""Rammus's step-1 pack for Codex (assets/source/rammus/MODEL_PROMPTS.md): the step-0 designs at game size, squares drawn
BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's 26-px way).

    python tools/art/pack_rammus_model.py [--out %TEMP%/ra_work/rammus_model_pack] [--lol D:/WeGameApps/lol]

The user's pick (2026-10-19): 36 game px spike tips to soles at PPU 1.2 -> ROWS = 43 squares. At PX px a square on
Codex's own 1254 canvas that is 1118 px: a figure that fills the picture IS the count. Four pictures of the same
Rammus at that count (side-view-design: every action is drawn from the side view):
  A  the idle, 3/4 front (step 0's A, cut to the count: 2_target_A.png),
  S  SIDE-ON facing right (League's idle at yaw 80 as the layout: 3_side_ref.png, faded, grid on),
  B  Powerball's ball (step 0's B at A's scale, cut: 2_target_B.png),
  W  Defensive Ball Curl, side-on (League's Rammus_channel at yaw 80: 3_curl_ref.png).
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png / 1_picture_B.png (step 0, the look to keep),
2_target_A.png / 2_target_B.png (cut to the count at PX: size, place, pose - details broken), 3_layout_A.png (A with
the grid, spike-top / eye / ground lines), 3_side_ref.png / 3_curl_ref.png (League renders at the count, faded, on the
grid: Riot's, kept local), 4_head.png (A's head read back, 8x), style/5..7.
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
from design_rammus_hd import SIZES, lp  # noqa: E402
from pack_gangplank_model import crop, cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rammus")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ra_work")
PX = 26                 # pixels a square on the canvas
CANVAS = 1254
SOLE_Y = 1196           # the soles' bottom edge (46 squares x 26)
ROWS = 43               # 36 game px x PPU 1.2, spike tips to soles
EYE_ROW = 65            # his eyes' row in hd/A.png (red squares, rows 63-66, cols 78-81 and 91-93)
HEAD = (52, 84, 66, 106)  # rows / cols of the shell's front lip, the head and the harness top in hd/A.png
GREY = (225, 225, 225)
STYLE = {"5_style_reksai.png": ("reksai", "hd_idle"), "6_style_wukong.png": ("wukong", "hd_idle"),
         "7_style_poppy.png": ("poppy", "hd_idle")}
# League renders laid out at the count: name -> (frame, yaw)
REFS = {"3_side_ref.png": ("rammus_idle1@0", 80), "3_curl_ref.png": ("Rammus_channel@400", 80)}


def lines(can, top, eye=None, label=""):
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(SOLE_Y % (PX * 5), CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    dr.line([(0, top), (CANVAS, top)], fill=(230, 150, 30, 255), width=3)
    if eye is not None:
        dr.line([(0, eye), (CANVAS, eye)], fill=(60, 110, 230, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), label, fill=(40, 40, 40, 255))


def target(d, k):
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    return crop(g)


def place(g):
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    return can, x0, y0


def league_ref(lol, frame, yaw, work, name):
    """League's model at yaw, scaled so its top to its soles is ROWS squares, soles on SOLE_Y, faded on the grid."""
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Rammus", "--hq",
           "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1600", "--fit", "0.5",
           "--ground", "0.84", "--width", "1.8", "--yaw", str(yaw), "--name", name, "--out", work, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    a = np.asarray(Image.open(os.path.join(work, name + ".png")).convert("RGBA")).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    fig = Image.fromarray(a)
    fig = fig.crop(fig.getbbox())
    k = ROWS * PX / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    f = np.asarray(fig).copy()
    f[..., 3] = (f[..., 3] * 0.45).astype(np.uint8)
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    can.alpha_composite(Image.fromarray(f), (round(CANVAS / 2 - fig.width / 2), SOLE_Y - fig.height))
    return can, SOLE_Y - fig.height, fig.width


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "rammus_model_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    work = out + "_measure"
    os.makedirs(work, exist_ok=True)
    A = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    B = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "B.png"))).convert("RGBA"))
    k = ROWS / A.shape[0]
    gA, gB = target(A, k), target(B, k * SIZES[1] / SIZES[0])
    canA, xA, yA = place(gA)
    canB, xB, yB = place(gB)
    canA.save(os.path.join(out, "2_target_A.png"))
    canB.save(os.path.join(out, "2_target_B.png"))
    eye = SOLE_Y - round((A.shape[0] - EYE_ROW) * k) * PX
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(canA)
    lines(lay, yA, eye, f"A: orange spike top y {yA}   blue eyes y {eye}   red ground y {SOLE_Y}   one square = {PX} px"
                        f"   {gA.shape[1]} x {gA.shape[0]} squares")
    lay.convert("RGB").save(os.path.join(out, "3_layout_A.png"))
    for fname, (frame, yaw) in REFS.items():
        can, top, w = league_ref(a.lol, frame, yaw, work, fname[:-4])
        lines(can, top, None, f"{fname[2:-4]}: League's model at the count (faded): top y {top}   ground y {SOLE_Y}   "
                              f"about {w / PX:.0f} squares wide   one square = {PX} px")
        can.convert("RGB").save(os.path.join(out, fname))
    for n in "AB":
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "rammus-picture", f"rammus-{n}.png")),
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
    print(f"A {gA.shape[1]}x{gA.shape[0]} at ({xA},{yA}), eyes y {eye}; B {gB.shape[1]}x{gB.shape[0]} at ({xB},{yB}); "
          f"ground y {SOLE_Y} ->", zp)


if __name__ == "__main__":
    main()

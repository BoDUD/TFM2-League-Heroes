#!/usr/bin/env python3
"""Quinn's step-1 pack for Codex (assets/source/quinn/MODEL_PROMPTS.md): design A at game size in two views - the 3/4
front (the idle, the ban-pick card, the one face of every frame) and SIDE-ON facing right (the base of the run and the
attacks) - plus Valor alone (the eagle circling over her head) and her riding Valor (R's ride form), squares drawn BIG
so the image generator's habit of filling the canvas lands on the right count (league_gangplank round 2).

    python tools/art/pack_quinn_model.py [--out %TEMP%/qn_work/quinn_model_pack] [--lol D:/WeGameApps/lol]

The user's picks (2026-10-19): A (League's idle, the crossbow raised), 38 game px visor crest to soles, PPU 1.3 ->
ROWS = 49 squares; the head enlarged to the pack's marksmen (league_caitlyn / league_akshan: about 15 of 49 squares
crest to chin, step 0's was 25 of 100). Valor circling: VALOR_W squares wing tip to wing tip; the ride: RIDE_W squares
wide, her head the same squares as the idle's.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png / 1b_picture_V.png / 1c_picture_R.png (step 0, the
look to keep), 2_target.png (A cut to the count at PX on the canvas: size, place, pose - its details are broken),
3_layout.png (with the grid, the crest-top, eye and ground lines), 4_head.png (A's head read back, 8x),
5_side_ref.png (League's idle nearly side-on, facing right), 6_side_layout.png (that render at the same height on the
grid), 7_proportions.png (league_caitlyn and league_akshan brought to the same 49 rows: the head share to copy),
8_valor_target.png / 9_ride_target.png (V and R cut to their counts on their own canvases), style/11..14.
League's renders are Riot's: kept local, never committed.
"""
import argparse
import json
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
from design_quinn_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "quinn")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "qn_work")
CANVAS = 1254
PX = 22                 # pixels a square on the idle's canvas
SOLE_Y = 1210           # the soles' bottom edge (55 squares x 22)
ROWS = 49               # 38 game px x PPU 1.3
EYE_ROW = 17            # her eyes' row in hd/A.png (rows 17-18, cols 36-38 and 42)
HEAD = (0, 26, 12, 50)  # rows / cols of the head (visor crest to chin) in hd/A.png
VALOR_W, VALOR_PX = 34, 30   # Valor circling: wing tip to wing tip, pixels a square
RIDE_W, RIDE_PX = 64, 18     # the ride: width in squares, pixels a square
GREY = (225, 225, 225)
STYLE = {"11_style_caitlyn.png": ("caitlyn", "hd_idle"), "12_style_akshan.png": ("akshan", "hd_idle"),
         "13_style_vayne.png": ("vayne", "hd_idle"), "14_style_anivia.png": ("anivia", "hd_idle")}


def lines(img, top, eye, label, px=PX, sole=SOLE_Y):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(img)
    dr = ImageDraw.Draw(lay)
    for x in range(0, CANVAS, px * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, px * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    if top is not None:
        dr.line([(0, top), (CANVAS, top)], fill=(40, 170, 60, 255), width=3)
    if eye is not None:
        dr.line([(0, eye), (CANVAS, eye)], fill=(60, 110, 230, 255), width=3)
    if sole is not None:
        dr.line([(0, sole), (CANVAS, sole)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), label, fill=(40, 40, 40, 255))
    return lay.convert("RGB")


def side_render(lol, work):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Quinn",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1600",
           "--fit", "0.5", "--ground", "0.84", "--width", "1.8", "--yaw", "80", "--name", "side", "--out", work,
           "--frame", "Quinn_idle1@0"]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "side.png")).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a).crop(Image.fromarray(a).getbbox())


def count(d, k):
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    op = g[..., 3] > 0
    return g[np.ix_(np.any(op, 1), np.any(op, 0))]


def frame0(hero):
    anims = json.load(open(lp(os.path.join(CHAMPS, f"league_{hero}#anim.fanim")), encoding="utf-8-sig"))["anims"]
    f = anims["hd_idle" if "hd_idle" in anims else "idle"]["frames"][0]["data"]
    sheet = Image.open(lp(os.path.join(CHAMPS, f"league_{hero}#sheet.png"))).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    return np.asarray(im.crop(im.getbbox()))


def centred(g, px, sole=None):
    gh, gw = g.shape[:2]
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x0 = (CANVAS // px - gw) // 2 * px
    y0 = (sole - gh * px) if sole is not None else (CANVAS // px - gh) // 2 * px
    can.paste(Image.fromarray(up(g, px)), (x0, y0))
    return can, x0, y0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "quinn_model_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    hd = {n: np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{n}.png"))).convert("RGBA")) for n in "AVR"}
    # the idle: A cut to ROWS
    d = hd["A"]
    k = ROWS / d.shape[0]
    g = count(d, k)
    can, x0, y0 = centred(g, PX, SOLE_Y)
    gh, gw = g.shape[:2]
    eye = SOLE_Y - round((d.shape[0] - EYE_ROW) * k) * PX
    can.save(os.path.join(out, "2_target.png"))
    lines(can, y0, eye, f"green crest top y {y0}   blue eyes y {eye}   red ground y {SOLE_Y}   one square = {PX} px   "
                        f"{gw} x {gh} squares").save(os.path.join(out, "3_layout.png"))
    pics = os.path.join(SRC, "codex_picture", "quinn-picture")
    for src, dst in (("quinn-A.png", "1_picture_A.png"), ("valor-V.png", "1b_picture_V.png"),
                     ("quinn-R.png", "1c_picture_R.png")):
        shutil.copyfile(lp(os.path.join(pics, src)), os.path.join(out, dst))
    r0, r1, c0, c1 = HEAD
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    # the side view: League's idle at yaw 80, the same crest-to-sole height, soles on the ground line
    side = side_render(a.lol, out + "_work")
    bg = Image.new("RGB", side.size, GREY)
    bg.paste(side, (0, 0), side)
    bg.save(os.path.join(out, "5_side_ref.png"))
    s = ROWS * PX / side.height
    sm = side.resize((round(side.width * s), round(side.height * s)), Image.LANCZOS)
    am = np.asarray(sm).copy()
    am[..., 3] = (am[..., 3] * 0.45).astype(np.uint8)
    sc = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    sc.alpha_composite(Image.fromarray(am), ((CANVAS - sm.width) // 2, SOLE_Y - sm.height))
    lines(sc, SOLE_Y - ROWS * PX, eye, f"SIDE VIEW: green crest top y {SOLE_Y - ROWS * PX}   blue eyes y {eye}   red "
                                       f"ground y {SOLE_Y}   one square = {PX} px   {ROWS} squares tall (faded: size only)"
          ).save(os.path.join(out, "6_side_layout.png"))
    # the head share to copy: Caitlyn and Akshan at the same 49 rows, side by side, the head line marked
    cells = []
    for hero in ("caitlyn", "akshan"):
        f = frame0(hero)
        cells.append(Image.fromarray(up(count(f, ROWS / f.shape[0]), 12)))
    pw = sum(c.width for c in cells) + 60
    prop = Image.new("RGBA", (pw, cells[0].height + 40), GREY + (255,))
    x = 20
    for c in cells:
        prop.alpha_composite(c, (x, 40 + cells[0].height - c.height))
        x += c.width + 20
    dr = ImageDraw.Draw(prop)
    hy = 40 + 15 * 12
    dr.line([(0, hy), (pw, hy)], fill=(60, 110, 230, 255), width=3)
    dr.text((10, 10), f"two marksmen of this pack at {ROWS} squares (12 px a square): the blue line is 15 squares from "
                      "the top - her head (crest to chin) about that big", fill=(30, 30, 30, 255))
    prop.convert("RGB").save(os.path.join(out, "7_proportions.png"))
    # Valor circling and the ride, each on its own canvas
    gv = count(hd["V"], VALOR_W / hd["V"].shape[1])
    cv, vx, vy = centred(gv, VALOR_PX)
    lines(cv, None, None, f"VALOR: {gv.shape[1]} x {gv.shape[0]} squares, one square = {VALOR_PX} px (size and place "
                          "only)", VALOR_PX, None).save(os.path.join(out, "8_valor_target.png"))
    gr = count(hd["R"], RIDE_W / hd["R"].shape[1])
    cr, rx, ry = centred(gr, RIDE_PX)
    lines(cr, None, None, f"RIDE: {gr.shape[1]} x {gr.shape[0]} squares, one square = {RIDE_PX} px (size and place "
                          "only; her head is drawn BIGGER than here, the idle's squares)", RIDE_PX, None
          ).save(os.path.join(out, "9_ride_target.png"))
    for fname, (hero, tag) in STYLE.items():
        try:
            cut(hero, tag, os.path.join(out, "style", fname))
        except KeyError:
            cut(hero, "idle", os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"idle {gw}x{gh} squares at ({x0},{y0}), crest y {y0}, eyes y {eye}, ground y {SOLE_Y}; side "
          f"{sm.width}x{sm.height} px; valor {gv.shape[1]}x{gv.shape[0]} at ({vx},{vy}); ride {gr.shape[1]}x{gr.shape[0]} "
          f"at ({rx},{ry}) ->", zp)


if __name__ == "__main__":
    main()

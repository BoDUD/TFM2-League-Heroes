#!/usr/bin/env python3
"""Jarvan IV's design redo pack for Codex (assets/source/jarvaniv/REDESIGN_PROMPTS.md): the approved step-1 design
(hd/design.png, PPU 1.5, 34 x 73 squares) redrawn on the same grid with three changes.

    python tools/art/pack_jarvaniv_redesign.py [--out %TEMP%/jv_work/jarvaniv_redesign_pack]

Why (the user, 2026-10-18): every walk posed from the design's own legs and Codex's run legs were 「变形」 - the shins
stand 2 squares apart (any step lays one leg over the other) and the knee guards sit tight under the skirt's hem with the
middle flap hanging between the knees (any lift hides a knee guard); and 「脸部太糊」 at game size (PPU stays 1.5:
「PPU还是1.5不用改」). The user took the redo: 「按方案做 ... 脸清楚、两腿稍分开、护膝离裙甲 ... 走路用造型自己的腿」.
The guide is the design itself with the changes made by whole squares (a rough guide of size and place):
  * the near leg (image left) LEG_OUT squares further left, the far leg where it is (the lance stands by it);
  * the skirt SKIRT_CUT rows shorter (its rows 49-50 taken out, the hem up from row 53 to 51) and nothing of it under
    the hem (the middle flap between the knees gone);
  * the two rows between the new hem and each knee guard dark navy leggings (League's model shows its dark legs there);
  * the face as it is (Codex redraws it clear - 4_head.png is its own step-0 face).
Writes <out>/ (and <out>.zip): REDESIGN_PROMPTS.md, 1_design_now.png (the approved design 10x), 2_target.png (the guide
on a 1024 canvas, PX px a square, the soles on y SOLE_Y), 3_layout.png (the same with grid and the helmet / chin / hem /
knee / ground lines), 4_head.png (the step-0 picture's head 8x), 5_league.png (League's idle: the dark legs between the
armour skirt and the knee guards), 6_face_now.png (the design's head 12x: too muddy), style/ (pack heroes at 8x, PPU 1.5).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_jarvaniv as J  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jarvaniv")
CHAMPS = os.path.join(ROOT, "league", "champions")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "jv_work")
PX = 12                 # pixels a square on the canvas (step 1's grid)
CANVAS = 1024
SOLE_Y = 960            # the soles' bottom edge on the canvas (step 1's)
PADL = 4                # squares added left of the design (the near leg moves out)
LEG_OUT = 3             # squares the near leg moves left: the shins 2 -> 5 squares apart
CUT_ROWS = (49, 50)     # skirt rows taken out: the hem goes up from row 53 to 51
HEM_NEW = 51
KNEE_TOP = 54           # the knee guards' top row (unchanged)
HEAD = (36, 64, 16, 42)  # the step-0 read-back (hd/A.png): helmet top, chin, the head's columns
STYLE = {"7_style_pantheon.png": ("pantheon", "hd_idle"), "8_style_swain.png": ("swain", "hd_idle"),
         "9_style_jax.png": ("jax", "hd_idle")}


def lp(path):
    return J.lp(path)


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def on_grey(a, k, grey=(225, 225, 225, 255)):
    im = Image.new("RGBA", (a.shape[1] * k, a.shape[0] * k), grey)
    im.alpha_composite(Image.fromarray(up(a, k)))
    return im.convert("RGB")


def cut(hero, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density), on grey."""
    anims = json.load(open(lp(os.path.join(CHAMPS, f"league_{hero}#anim.fanim")), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(lp(os.path.join(CHAMPS, f"league_{hero}#sheet.png"))).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = np.asarray(im.crop(im.getbbox()))
    pad = np.zeros((im.shape[0] + 4, im.shape[1] + 4, 4), np.uint8)
    pad[2:-2, 2:-2] = im
    on_grey(pad, 8).save(out)


def padded(a):
    out = np.zeros((a.shape[0], a.shape[1] + PADL, 4), np.uint8)
    out[:, PADL:] = a
    return out


def guide():
    """The design with the three changes (whole squares). -> RGBA, PADL columns wider than the design."""
    D = J.design()
    d = padded(D.d)
    m = {k: np.pad(v, ((0, 0), (PADL, 0))) for k, v in D.parts.items()}
    skirt = padded(J.skirt_layer(D))
    legs = {n: padded(J.leg_layer(D, n)) for n in ("near_leg", "far_leg")}
    out = d.copy()
    out[m["skirt"] | m["near_leg"] | m["far_leg"]] = 0
    # the skirt: down to the old hem only, rows CUT_ROWS out, the rows under them up
    keep = [y for y in range(KNEE_TOP) if y not in CUT_ROWS]
    sk = np.zeros_like(skirt)
    for i, y in enumerate(keep):
        sk[i] = skirt[y]
    for lay, dx in ((sk, 0),):
        op = lay[..., 3] > 0
        out[op & (out[..., 3] == 0)] = lay[op & (out[..., 3] == 0)]
    # the legs (the near one LEG_OUT squares left), under the arms and the lance
    for name, dx in (("far_leg", 0), ("near_leg", -LEG_OUT)):
        lay = np.roll(legs[name], dx, axis=1)
        op = lay[..., 3] > 0
        free = out[..., 3] == 0
        out[op & free] = lay[op & free]
    # leggings between the new hem and each knee guard: navy over the knee guard's top span, outlined at its ends
    navy_px = D.d[J.navy(D.d)]
    cols, n = np.unique(navy_px[:, :3], axis=0, return_counts=True)
    navy = tuple(int(v) for v in cols[n.argmax()]) + (255,)
    light = tuple(int(v) for v in cols[np.argsort(cols.astype(int).sum(1))[-2]]) + (255,)
    outline = tuple(D.outline) + (255,)
    for name, dx in (("far_leg", 0), ("near_leg", -LEG_OUT)):
        xs = np.nonzero(np.roll(legs[name], dx, axis=1)[KNEE_TOP, :, 3] > 0)[0]
        x0, x1 = xs.min(), xs.max()
        for y in range(HEM_NEW + 1, KNEE_TOP):
            for x in range(x0, x1 + 1):
                if out[y, x, 3] == 0 or not (m["near_arm"][y, x] or m["lance"][y, x] or m["far_arm"][y, x]):
                    out[y, x] = outline if x in (x0, x1) else (light if x == x0 + 1 else navy)
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[:, xs.min():xs.max() + 1], D


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "jarvaniv_redesign_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    g, D = guide()
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target.png"))
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(can)
    dr = ImageDraw.Draw(lay)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    marks = [("helmet top", 13, (40, 170, 60)), ("chin", 28, (60, 110, 230)), ("hem", HEM_NEW + 1, (240, 140, 20)),
             ("knee guard top", KNEE_TOP, (170, 60, 200)), ("ground", gh, (230, 40, 40))]
    for i, (lab, row, col) in enumerate(marks):
        y = y0 + row * PX
        dr.line([(0, y), (CANVAS, y)], fill=col + (255,), width=3)
        dr.text((CANVAS - 230, y - 14), f"{lab} y {y}", fill=col + (255,))
    dr.text((12, 12), f"one square = {PX} px, {gw} x {gh} squares, soles on y {SOLE_Y}", fill=(40, 40, 40, 255))
    lay.convert("RGB").save(os.path.join(out, "3_layout.png"))
    on_grey(D.d, 10).save(os.path.join(out, "1_design_now.png"))
    t, c, c0, c1 = HEAD
    h = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))[t:c + 4, c0 - 4:c1 + 4]
    on_grey(np.ascontiguousarray(h), 8).save(os.path.join(out, "4_head.png"))
    lol = Image.open(os.path.join(TMP, "r", "idle_45.png")).convert("RGB").crop((540, 380, 800, 1040))
    lol.resize((lol.width * 3 // 2, lol.height * 3 // 2), Image.LANCZOS).save(os.path.join(out, "5_league.png"))
    on_grey(np.ascontiguousarray(D.d[8:32]), 12).save(os.path.join(out, "6_face_now.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "REDESIGN_PROMPTS.md")), os.path.join(out, "REDESIGN_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{gw}x{gh} squares at ({x0},{y0}); helmet top y {y0 + 13 * PX}, chin y {y0 + 28 * PX}, hem y "
          f"{y0 + (HEM_NEW + 1) * PX}, knee guards y {y0 + KNEE_TOP * PX}, ground y {SOLE_Y}")
    print("->", zp)


if __name__ == "__main__":
    main()

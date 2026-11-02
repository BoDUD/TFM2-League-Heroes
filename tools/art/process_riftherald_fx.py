#!/usr/bin/env python3
"""The Rift Herald's effects and icons from the one Gemini sheet the user made (2026-11-02, 「这是gemini生成的技能特效和技能
图标你导入后处理一下就能使用」): each drawing cut from the sheet, keyed off its ground, brought down to the game size the
pack's prompt gave (assets/source/riftherald/PROMPTS_FX.md), the frames the sheet did not draw built from its drawings,
its colours cut to its own palette, made symmetric, and written as a strip of equal cells for import_riftherald_fx.py.

    python tools/art/process_riftherald_fx.py [--src C:/t/rh_work/gemini/riftherald_fx.jpg] [--review out.png]

The sheet (2440 x 1728, JPEG, a dark navy ground ~#1A1E2C with every effect's name written over it in white; a_hit, q_hit
and e_hit on black boxes; the original is the user's Downloads/Gemini_Generated_Image_xehw2exehw2exehw.jpg, kept out of
git like the other heroes' Gemini art). DRAWINGS below are each drawing's box on it, read by eye on a 50-px grid
(C:/t/rh_work/gemini/grid0.png, grid1.png); every box is clear of the labels.
What the sheet gave and what is built here (fix-delivered-art-myself):
  a_hit    three crossed-gash drawings: the three middle frames; a small flash (the first, shrunk) before them;
  q_spin   ONE wide drawing (both sweeps, crystals and dust): grown in from 45% (frames 1-3), whole (4), its bright
           magenta gone - the dust, the crystals and the dark arcs left (5), the dust alone thinned (6);
  q_hit    ONE comet-shaped slash pointing right: mirrored into a flat two-ended slash (the prompt's), grown in and faded;
  q_slow   two tendril drawings: the loop alternates them, each also one row lower (the tendrils sinking);
  e_hit    two drawings (the star, the burst with rocks): a flash before them, the burst's rocks alone after, faded;
  e_crash  ONE drawing (two dust plumes, the cracks): grown in, whole, the dust lowered and thinned, the cracks alone;
  e_stun   ONE ring of four eyes: the loop pulses it (the eyes' glow brighter, dimmer);
  r_roar   two ring drawings; only the round one (fewer, tighter rings) is used - the wide one's box clipped its outer
           rings into a rectangle, and cut to an ellipse it squashed into an oval beside the round frames. The round one
           cut to the circle inside its box: grown in, whole, its outer ring alone, faded; the centre (its body) cleared;
  r_slam   ONE drawing (the shock ring, the cracks, the shards): a flash, grown in, whole, the shards alone falling, the
           cracks alone, faded;
  r_armor  two plate-ring drawings: the loop alternates them, each also one row higher (the plates bobbing);
  icons    the sheet's two "icon_skill" tiles: the whirl with the pincer (the second, right) is skill's - the prompt's
           sweep arc with a pincer; the crescent one is left out.
Every picture is made symmetric left to right by union with its mirror (the client never mirrors an effect).
Writes assets/source/riftherald/gemini_fx/pixel_1x/riftherald_fx_<name>.png (one row of equal cells at game size, alpha
0 / 255), gemini_fx/cells.json (each strip's frames and cell) and gemini_fx/icons/riftherald_icon_<name>.png (64 x 64).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_varus as V  # noqa: E402
import process_brock_fx as B  # noqa: E402  shrink, put, tight, union_mirror, review

OUT = os.path.join(ROOT, "assets", "source", "riftherald", "gemini_fx")
SRC = "C:/t/rh_work/gemini/riftherald_fx.jpg"
lp = B.lp

# drawing boxes (x0, y0, x1, y1) on the sheet
DRAWINGS = {
    "a_hit": [(45, 205, 310, 475), (310, 205, 575, 475), (575, 205, 840, 475)],
    "q_spin": [(915, 205, 1985, 478)],
    "q_hit": [(2055, 205, 2420, 475)],
    "q_slow": [(50, 555, 445, 835), (490, 555, 845, 835)],
    "e_hit": [(950, 555, 1262, 842), (1262, 555, 1615, 842)],
    "e_crash": [(1712, 560, 2422, 848)],
    "e_stun": [(45, 960, 420, 1172)],
    "r_roar": [(1255, 920, 1642, 1272)],
    "r_slam": [(1672, 920, 2422, 1272)],
    "r_armor": [(450, 1352, 832, 1684), (845, 1352, 1218, 1684)],
}
ICONS = {"skill": (1270, 1345, 1625, 1697), "skill2": (1670, 1345, 2025, 1697), "ult": (2068, 1345, 2425, 1697)}

# name -> (cell w, h at game size, where the frames sit in the cell: "c" centre / "b" bottom, colours)
SPEC = {
    "a_hit": (16, 14, "c", 14), "q_spin": (76, 28, "c", 16), "q_hit": (14, 12, "c", 10), "q_slow": (18, 8, "b", 10),
    "e_hit": (22, 20, "c", 16), "e_crash": (56, 26, "b", 16), "e_stun": (16, 8, "c", 10), "r_roar": (68, 56, "b", 14),
    "r_slam": (88, 34, "b", 18), "r_armor": (64, 52, "b", 14),
}


def key(rgb):
    """The sheet's grounds off: the dark navy (low, blue over red, little green) and the black boxes."""
    a = rgb.astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(2)
    navy = (mx < 56) & (b - r > 6) & (g < 44)
    black = mx < 24
    fg = ~(navy | black)
    fg = ndimage.binary_opening(fg, iterations=1)
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(fg, 255, 0)
    return out


def bright(a):
    """The glowing magenta / pink-white squares (the light), as a mask."""
    c = a[..., :3].astype(int)
    return (a[..., 3] > 0) & (c[..., 0] > 170) & (c[..., 2] > 140)


def only(a, mask):
    out = a.copy()
    out[~mask] = 0
    return out


def dim(a, k):
    out = a.copy()
    out[..., :3] = (out[..., :3].astype(float) * k).round().astype(np.uint8)
    return out


def thin(a, every=2):
    """A checker of it (the dust thinning out)."""
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    return only(a, (yy + xx) % every == 0)


def over(a, b):
    """b laid over a (b's opaque squares win)."""
    out = a.copy()
    m = b[..., 3] > 0
    out[m] = b[m]
    return out


def cell_of(W, H, parts):
    """parts = [(picture at game size, where, dy)] stacked into one cell."""
    c = np.zeros((H, W, 4), np.uint8)
    for p, where, dy in parts:
        B.put(c, p, where, dy)
    return c


def fit(p, W, H, k=1.0):
    """p brought down to fit W x H (by its own larger side), times k."""
    s = min(W / p.shape[1], H / p.shape[0]) * k
    return B.shrink(p, s)


def drawings(sheet, name):
    return [B.tight(B.crop(sheet, box)) for box in DRAWINGS[name]]


def build(sheet):
    out = {}
    for name, (W, H, where, ncol) in SPEC.items():
        d = drawings(sheet, name)
        one = lambda p, k=1.0, dy=0: cell_of(W, H, [(fit(p, W, H, k), where, dy)])
        if name == "a_hit":
            cells = [one(d[0], 0.4)] + [one(p) for p in d]
        elif name == "q_spin":
            p = d[0]
            cells = [one(p, 0.45), one(p, 0.7), one(p, 0.88), one(p), one(only(p, ~bright(p))),
                     one(thin(only(p, ~bright(p))))]
        elif name == "q_hit":
            p = B.union_mirror(d[0], "LR")
            cells = [one(p, 0.45), one(p), one(dim(p, 0.75)), one(thin(dim(p, 0.6)))]
        elif name == "q_slow":
            cells = [one(d[0]), one(d[0], 1.0, 1), one(d[1]), one(d[1], 1.0, 1), one(d[0], 0.95), one(d[1], 0.95)]
        elif name == "e_hit":
            rocks = only(d[1], ~bright(d[1]))
            cells = [one(d[0], 0.35), one(d[0]), one(d[1]), one(rocks), one(thin(dim(rocks, 0.7)))]
        elif name == "e_crash":
            p = d[0]
            dust = only(p, ~bright(p))
            cracks = only(p, bright(p))
            cells = [one(p, 0.55), one(p, 0.8), one(p), one(dust, 1.0, 2), over(one(thin(dust)), one(cracks)),
                     one(dim(cracks, 0.6))]
        elif name == "e_stun":
            p = d[0]
            cells = [one(p), one(dim(p, 0.85)), one(dim(p, 0.7)), one(dim(p, 0.7)), one(dim(p, 0.85)), one(p)]
        elif name == "r_roar":
            ring = only(d[0], ring_core(d[0], 0.98))   # the box's corners (clipped arcs) off
            outer = only(ring, ~ring_core(ring, 0.72))
            cells = [one(ring, 0.5), one(ring, 0.75), one(ring), one(outer), one(dim(outer, 0.75)),
                     one(thin(dim(outer, 0.6)))]
        elif name == "r_slam":
            p = d[0]
            shards = only(p, ~bright(p))
            cracks = only(p, bright(p))
            cells = [one(p, 0.25), one(p, 0.6), one(p, 0.85), one(p), over(one(dim(cracks, 0.8)), one(shards, 1.0, 3)),
                     one(dim(cracks, 0.65)), one(thin(dim(cracks, 0.5)))]
        elif name == "r_armor":
            cells = [one(d[0]), one(d[0], 1.0, -1), one(d[0], 1.0, -2), one(d[1], 1.0, -2), one(d[1], 1.0, -1),
                     one(d[1])]
        cells = [binary(c) for c in cells]
        if name == "r_roar":    # its body: the middle of the rings stays clear
            cells = [clear_core(c, 0.42) for c in cells]
        cells = B.palette(cells, ncol)
        cells = [B.union_mirror(c, "LR") for c in cells]
        out[name] = cells
    return out


def binary(c):
    c = c.copy()
    c[c[..., 3] < 128] = 0
    c[c[..., 3] > 0, 3] = 255
    return c


def ring_core(p, frac):
    """The ellipse inside `frac` of the picture's half sizes (the rings' inner part), as a mask."""
    h, w = p.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx - (w - 1) / 2) / (w / 2 * frac)) ** 2 + ((yy - (h - 1) / 2) / (h / 2 * frac)) ** 2 <= 1


def clear_core(c, frac):
    ys, xs = np.nonzero(c[..., 3] > 0)
    if not len(ys):
        return c
    box = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    m = ring_core(box, frac)
    out = c.copy()
    sub = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sub[m] = 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review", help="also write every strip at 6x here")
    a = ap.parse_args()
    rgb = np.asarray(Image.open(lp(a.src)).convert("RGB"))
    if rgb.shape[:2] != (1728, 2440):
        sys.exit(f"{a.src}: {rgb.shape[1]}x{rgb.shape[0]}, not the 2440 x 1728 sheet")
    sheet = key(rgb)
    out = build(sheet)
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    os.makedirs(lp(os.path.join(OUT, "icons")), exist_ok=True)
    meta = {}
    for name, cs in out.items():
        Image.fromarray(np.concatenate(cs, axis=1)).save(lp(os.path.join(OUT, "pixel_1x", f"riftherald_fx_{name}.png")))
        meta[name] = {"frames": len(cs), "cell": [cs[0].shape[1], cs[0].shape[0]], "symmetry": "LR"}
        print(f"{name:9s} {len(cs)} x {cs[0].shape[1]}x{cs[0].shape[0]}")
    with open(lp(os.path.join(OUT, "cells.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    for n, box in ICONS.items():
        B.icon(rgb, box).save(lp(os.path.join(OUT, "icons", f"riftherald_icon_{n}.png")))
    if a.review:
        B.review(out, a.review)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""T-Hex's effects and icons from the one Gemini sheet the user made (2026-11-02, 「这是gemini生成的技能特效和技能图标你导入后
处理一下就能使用」): each frame cut from the sheet, keyed off its dark grey ground, brought down to the game size the pack's
prompt gave (assets/source/thex/PROMPTS_FX.md), its colours cut to its own palette, made symmetric, and written as a
strip of equal cells for import_thex_fx.py.

    python tools/art/process_thex_fx.py [--src C:/t/tx_work/gemini/thex_fx.jpg] [--review out.png]

The sheet (1792 x 2400, JPEG: the three icons on navy at the top, then one panel an effect on a flat dark grey #3B3B39
with its name written at its top left; the original is the user's Downloads/Gemini_Generated_Image_d4fc85d4fc85d4fc.jpg,
kept out of git like the other heroes' Gemini art). PANELS below are each effect's box on it (under its label), read
by eye; the frames in a panel are its keyed pieces split where a run of empty columns parts them.
The sheet drew most effects as ONE picture (a_hit, e_dash, e_hit, r_hit, r_shield, p_blast) and q_fall as two; the
missing frames are made from those pictures here (fix-delivered-art-myself): a smaller first frame (the burst
starting), the whole picture, then parts of it fading (only its smoke, its ring, its sparks) by colour. r_beam's two
frames point opposite ways: the second is flipped to point right too. Every picture made symmetric (left to right;
a_bullet and r_beam top to bottom) by union with its mirror: the client never mirrors an effect.
Writes assets/source/thex/gemini_fx/pixel_1x/thex_fx_<name>.png (one row of equal cells at game size, alpha 0 / 255),
gemini_fx/cells.json (each strip's frames and cell) and gemini_fx/icons/thex_icon_<name>.png (64 x 64, LANCZOS).
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
import process_brock_fx as PB  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "thex", "gemini_fx")
SRC = "C:/t/tx_work/gemini/thex_fx.jpg"
lp = PB.lp

# each effect's panel (x0, y0, x1, y1) on the sheet, below its label
PANELS = {
    "a_bullet": (0, 640, 462, 810), "a_hit": (468, 640, 860, 810), "a_crit": (868, 640, 1792, 810),
    "q_launch": (0, 880, 1070, 1250), "q_fall_a": (1080, 880, 1416, 1250), "q_fall_b": (1422, 880, 1792, 1250),
    "e_dash": (0, 1320, 890, 1494), "e_hit": (898, 1320, 1312, 1494), "e_slow": (1318, 1320, 1792, 1494),
    "r_beam": (0, 1556, 1340, 1740), "r_hit": (1348, 1556, 1792, 1740),
    "r_shield": (0, 1796, 890, 2400), "p_blast": (898, 1796, 1792, 2400),
}
GAP = {"r_beam": 8}   # the two beams' heads nearly touch
ICONS = {"skill": (120, 78, 534, 480), "skill2": (690, 78, 1104, 480), "ult": (1260, 78, 1674, 480)}

# name -> (cell w, h at game size, "c" centre / "b" bottom, symmetry, colours)
SPEC = {
    "a_bullet": (10, 4, "c", "TB", 8), "a_hit": (10, 10, "c", "LR", 8), "a_crit": (20, 18, "c", "LR", 12),
    "q_launch": (40, 44, "b", "LR", 16), "q_fall": (24, 52, "b", "LR", 16), "e_dash": (40, 12, "b", "LR", 10),
    "e_hit": (24, 22, "c", "LR", 12), "e_slow": (24, 8, "b", "LR", 10), "r_beam": (56, 10, "c", "TB", 10),
    "r_hit": (20, 20, "c", "LR", 12), "r_shield": (64, 50, "c", "LR", 12), "p_blast": (80, 56, "b", "LR", 18),
}


def key(rgb):
    """The panels' dark grey ground off: alpha 0 where the colour is that flat grey."""
    a = rgb.astype(int)
    mx, mn = a.max(2), a.min(2)
    bg = (mx - mn < 14) & (mx > 40) & (mx < 78)
    fg = ndimage.binary_opening(~bg, iterations=1)
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(fg, 255, 0)
    return out


def pieces(sheet, name, gap=24):
    """A panel's frames: its keyed pixels split where `gap` empty columns part them (specks dropped)."""
    x0, y0, x1, y1 = PANELS[name]
    a = sheet[y0:y1, x0:x1].copy()
    m = a[..., 3] > 0
    lab, n = ndimage.label(m)
    sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
    for i, s in enumerate(sizes, 1):
        if s < 30:
            a[lab == i, 3] = 0
    cols = (a[..., 3] > 0).any(0)
    runs, start, empty = [], None, 0
    for x, c in enumerate(cols):
        if c:
            if start is None:
                start = x
            empty = 0
        elif start is not None:
            empty += 1
            if empty >= gap:
                runs.append((start, x - empty + 1))
                start, empty = None, 0
    if start is not None:
        runs.append((start, len(cols)))
    # a 1-px panel divider at the edge is no frame
    return [f for f in (PB.tight(a[:, s:e]) for s, e in runs) if min(f.shape[:2]) >= 4]


def kind(a):
    """Masks by colour: fire (yellow-orange), blue (hextech), grey (smoke, metal)."""
    c = a[..., :3].astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    op = a[..., 3] > 0
    fire = op & (r > 170) & (g > 70) & (b < 140) & (r > b + 60)
    blue = op & (b > 140) & (b > r + 30)
    grey = op & (c.max(2) - c.min(2) < 30) & (c.max(2) > 90)
    return fire, blue, grey


def only(a, mask):
    out = a.copy()
    out[~mask, 3] = 0
    return out


def scaled_by(a, k):
    return np.asarray(Image.fromarray(a).resize((max(1, round(a.shape[1] * k)), max(1, round(a.shape[0] * k))),
                                                 Image.BOX))


def made(name, p):
    """The frames (full-size pictures, before the game-size shrink) of an effect; `p` = its panel's pieces."""
    if name in ("a_bullet", "a_crit", "e_slow"):
        return p
    if name == "q_launch":   # the missiles lean right: turned to lean left, the mirror adds the right-hand ones (a V);
        # its grey smoke column off (a solid grey block over the body in game): the missiles and their fire trails
        return [only(x, ~kind(x)[2])[:, ::-1] for x in p]
    if name == "r_beam":   # the second beam points left: flipped to point right
        return [p[0], p[1][:, ::-1]]
    one = max(p, key=lambda x: x.shape[0] * x.shape[1]) if name not in ("e_slow",) else p[0]
    fire, blue, grey = kind(one)
    if name == "a_hit":    # the burst small, whole, its sparks without the bright core
        core = fire & (one[..., :3].astype(int).min(2) > 150)
        return [scaled_by(one, 0.55), one, only(one, ~core)]
    if name == "e_dash":   # the dust kicking up, whole, the dust alone settling
        return [scaled_by(one, 0.5), scaled_by(one, 0.8), one, only(one, grey)]
    if name == "e_hit":    # the jaws, the jaws and the spark, the spark and what is not grey metal
        return [only(one, ~fire), one, only(one, ~grey)]
    if name == "r_hit":    # the flash small, whole, the smoke and the last arcs
        return [scaled_by(only(one, blue), 0.7), one, only(one, ~blue | (one[..., 2] < 200))]
    if name == "r_shield":   # a pulse: the ring, the ring a shade brighter
        bright = one.copy()
        bright[..., :3] = np.minimum(255, bright[..., :3].astype(int) * 115 // 100).astype(np.uint8)
        return [one, bright]
    if name == "p_blast":  # the fireball starting, the ball and the ring, whole, the ring and smoke, the smoke
        return [scaled_by(only(one, fire), 0.4), scaled_by(only(one, fire | blue), 0.75), one, only(one, ~fire),
                only(one, grey)]
    raise KeyError(name)


def fall_frames(sheet, W, H):
    """The falling missile: Q's two pictures (the missile over its blast); the missile alone (its rows above the blast)
    at three heights, then both pictures, then the second's blast without the missile, then its ring."""
    a = pieces(sheet, "q_fall_a")[0]
    b = pieces(sheet, "q_fall_b")[0]
    fire, blue, grey = kind(a)
    rows = np.nonzero(fire.sum(1) > a.shape[1] * 0.12)[0]   # where the blast's sparks start spreading
    top = a[:rows.min()] if len(rows) else a[: a.shape[0] // 2]
    lab, n = ndimage.label(top[..., 3] > 0)                 # the missile and its trail alone (spark tips off)
    big = 1 + int(np.argmax(ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))))
    top = top.copy()
    top[lab != big, 3] = 0
    k = min(W / max(a.shape[1], b.shape[1]), H / max(a.shape[0], b.shape[0]))
    missile = PB.shrink(PB.tight(top), k)
    bf, bb, bg = kind(b)
    cut = int(b.shape[0] * 0.55)           # the missile's part of the second picture: above its blast
    low = b.copy()
    low[:cut, 3] = 0
    cells = []
    for drop in (0, (H - missile.shape[0]) // 3, 2 * (H - missile.shape[0]) // 3):
        c = np.zeros((H, W, 4), np.uint8)
        PB.put(c, missile, "b", -(H - missile.shape[0] - drop))
        cells.append(c)
    ring = only(low, bb)
    ring[: int(b.shape[0] * 0.8), 3] = 0                    # the ring on the ground, not the missile's blue fins
    for pic in (a, b, low, ring):
        c = np.zeros((H, W, 4), np.uint8)
        PB.put(c, PB.shrink(PB.tight(pic), k), "b")
        cells.append(c)
    return cells


def specks(c, least=3):
    """Pieces smaller than `least` squares off (the shrink's leftovers: two lone fin dots over q_fall's ring)."""
    lab, n = ndimage.label(c[..., 3] > 0)
    out = c.copy()
    for i, sz in enumerate(ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1)), 1):
        if sz < least:
            out[lab == i] = 0
    return out


RIM = 3


def build(sheet):
    out = {}
    for name, (W, H, where, sym, ncol) in SPEC.items():
        if name == "q_fall":
            cells = fall_frames(sheet, W, H)
        else:
            frames = [PB.tight(f) for f in made(name, pieces(sheet, name, GAP.get(name, 24)))]
            cells = []
            for f in PB.scaled(frames, W, H):
                c = np.zeros((H, W, 4), np.uint8)
                if name == "q_launch":   # its right edge 3 past the middle: the mirror keeps the left half
                    f = f[:, : W // 2 + 3] if f.shape[1] > W // 2 + 3 else f
                    c[H - f.shape[0]:, W // 2 + 3 - f.shape[1]: W // 2 + 3][f[..., 3] > 0] = f[f[..., 3] > 0]
                else:
                    PB.put(c, f, where)
                cells.append(c)
        cells = PB.palette(cells, ncol)
        cells = [specks(PB.union_mirror(c, sym)) for c in cells]
        if name == "q_launch":   # the smoke's last wisps (two dark dots under the missiles) off too
            cells = [specks(c, 8) for c in cells]
        if name == "r_shield":   # the sheet's bubble is solid blue and hid T-Hex inside it: hollowed to a RIM-px rim
            cells = [PB.hollow(c, RIM) for c in cells]
        out[name] = cells
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review", help="also write every strip at 6x here")
    a = ap.parse_args()
    rgb = np.asarray(Image.open(lp(a.src)).convert("RGB"))
    if rgb.shape[:2] != (2400, 1792):
        sys.exit(f"{a.src}: {rgb.shape[1]}x{rgb.shape[0]}, not the 1792 x 2400 sheet")
    out = build(key(rgb))
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    os.makedirs(lp(os.path.join(OUT, "icons")), exist_ok=True)
    meta = {}
    for name, cs in out.items():
        Image.fromarray(np.concatenate(cs, axis=1)).save(lp(os.path.join(OUT, "pixel_1x", f"thex_fx_{name}.png")))
        meta[name] = {"frames": len(cs), "cell": [cs[0].shape[1], cs[0].shape[0]], "symmetry": SPEC[name][3]}
        print(f"{name:9s} {len(cs)} x {cs[0].shape[1]}x{cs[0].shape[0]}")
    with open(lp(os.path.join(OUT, "cells.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    for n, box in ICONS.items():
        PB.icon(rgb, box).save(lp(os.path.join(OUT, "icons", f"thex_icon_{n}.png")))
    if a.review:
        PB.review(out, a.review)


if __name__ == "__main__":
    main()

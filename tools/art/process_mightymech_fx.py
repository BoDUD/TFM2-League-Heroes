#!/usr/bin/env python3
"""The Mighty Mech's effects and icons from the one Gemini sheet the user made (2026-11-03, 「这是gemini做的技能特效和技能图标
你导入后弄到完美后使用」): each frame cut from the sheet, keyed off its dark grey ground, brought down to its game size,
its colours cut to its own palette, made symmetric, and written as a strip of equal cells for import_mightymech_fx.py.

    python tools/art/process_mightymech_fx.py [--src C:/t/mm_work/gemini/mightymech_fx.jpg] [--review out.png]

The sheet (2204 x 1952, JPEG: one row of effects after another on a flat dark grey #424347, a file name over each, the
three framed icons at the bottom and a spare frameless ult; the original is the user's
Downloads/Gemini_Generated_Image_eubmh6eubmh6eubm.jpg, kept out of git like the other heroes' Gemini art). FRAMES below
are each frame's box on it, read from its keyed column runs (a frame drawn as a left and a right half - a_slow,
r_transform, r_form - is the box round both).
What it drew differently from assets/source/mightymech/PROMPTS_FX.md, fixed here (fix-delivered-art-myself):
- q_stance is a FILLED hexagon disc lying flat, not a ring round the body: it goes on the ground under it (the kit's
  view z -1), a gravity field it stands in.
- r_transform (two fans of blades) and r_sword (a light pillar) stand in the middle where its body is: both go behind
  it (z -1) from its soles, the blades flaring out like its wings, the pillar rising behind it.
- r_slash's three crescents point different ways (the first curves down, the second points left): the left one is
  flipped, the first is kept small as the wave starting, and every frame made symmetric top to bottom.
- fewer frames than asked for some (q_stance 4, q_wave 3, r_transform 3, r_sword 3, r_slash 3, r_form 3): played as
  they are.
Every picture made symmetric (left to right; r_slash top to bottom) by union with its mirror: the client never mirrors
an effect.
Writes assets/source/mightymech/gemini_fx/pixel_1x/mightymech_fx_<name>.png (one row of equal cells at game size, alpha
0 / 255), gemini_fx/cells.json (each strip's frames and cell) and gemini_fx/icons/mightymech_icon_<name>.png (64 x 64).
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

OUT = os.path.join(ROOT, "assets", "source", "mightymech", "gemini_fx")
SRC = "C:/t/mm_work/gemini/mightymech_fx.jpg"
SIZE = (1952, 2204)
lp = PB.lp


def band(y0, y1, *xs):
    return [(x0, y0, x1, y1) for x0, x1 in xs]


# each frame's box (x0, y0, x1, y1) on the sheet
FRAMES = {
    "a_hit": band(37, 207, (49, 138), (229, 329), (420, 512)),
    "a_crush": band(37, 207, (704, 862), (885, 1025), (1050, 1198), (1220, 1376)),
    "a_slow": band(306, 382, (28, 162), (213, 342), (401, 529), (582, 710), (764, 898), (949, 1079)),
    "q_stance": band(435, 575, (16, 361), (383, 727), (750, 1094), (1116, 1461)),
    "q_taunt": band(435, 575, (1487, 1641), (1670, 1824), (1853, 2006), (2037, 2190)),
    "q_wave": band(631, 763, (43, 337), (396, 717), (752, 1094)),
    "q_hit": band(631, 763, (1224, 1347), (1486, 1602), (1714, 1844)),
    "e_slam": band(823, 979, (66, 312), (435, 681), (802, 1046), (1169, 1413)),
    "e_up": band(823, 979, (1490, 1618), (1688, 1816), (1849, 1990), (2050, 2204)),
    "r_transform": band(1001, 1164, (14, 364), (386, 727), (754, 1092)),
    "r_sword": band(1001, 1164, (1141, 1436), (1507, 1803), (1878, 2161)),
    "r_slash": band(1209, 1367, (389, 728), (753, 1094), (1117, 1459)),
    "r_hit": band(1209, 1367, (1482, 1641), (1665, 1824), (1847, 2007), (2030, 2204)),
    "r_form": band(1392, 1553, (25, 353), (394, 714), (770, 1074)),
    "p_shield": band(1392, 1553, (1161, 1234), (1337, 1414), (1525, 1599), (1706, 1785), (1887, 1967), (2069, 2155)),
}
BLADE_ROWS, BLADE_W, SHARDS_FROM = 0.62, 3, 6.5   # a_crush: its blade thinned above the impact (build)
ICONS = {"skill": (28, 1600, 354, 1926), "skill2": (398, 1600, 725, 1926), "ult": (768, 1600, 1094, 1926)}

# name -> (cell w, h at game size, "c" centre / "b" bottom, symmetry, colours)
SPEC = {
    "a_hit": (18, 20, "c", "LR", 10), "a_crush": (24, 22, "b", "LR", 12), "a_slow": (24, 8, "b", "LR", 8),
    "q_stance": (64, 26, "c", "LR", 10), "q_taunt": (16, 14, "c", "LR", 8), "q_wave": (90, 34, "c", "LR", 12),
    "q_hit": (16, 16, "c", "LR", 8), "e_slam": (60, 38, "b", "LR", 14), "e_up": (16, 20, "b", "LR", 8),
    "r_transform": (90, 44, "b", "LR", 12), "r_sword": (64, 36, "b", "LR", 12), "r_slash": (80, 20, "c", "TB", 12),
    "r_hit": (22, 22, "c", "LR", 12), "r_form": (70, 34, "b", "LR", 8), "p_shield": (22, 40, "c", "LR", 8),
}


def key(rgb):
    """The sheet's dark grey ground off: alpha 0 where the colour is that flat grey."""
    a = rgb.astype(int)
    mx, mn = a.max(2), a.min(2)
    bg = (mx - mn < 14) & (mx > 40) & (mx < 90)
    fg = ndimage.binary_opening(~bg, iterations=1)
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(fg, 255, 0)
    return out


def frame(sheet, box):
    """A frame's keyed pixels, specks (JPEG noise) dropped, cropped tight."""
    x0, y0, x1, y1 = box
    a = sheet[y0:y1, x0:x1].copy()
    lab, n = ndimage.label(a[..., 3] > 0)
    for i, s in enumerate(ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1)), 1):
        if s < 30:
            a[lab == i, 3] = 0
    return PB.tight(a)


def scaled_by(a, k):
    return np.asarray(Image.fromarray(a).resize((max(1, round(a.shape[1] * k)), max(1, round(a.shape[0] * k))),
                                                 Image.BOX))


def made(name, p):
    """The frames (full-size pictures, before the game-size shrink) of an effect; `p` = its cut frames."""
    if name == "r_slash":   # the left-pointing crescent flipped; the first (curving down) kept small: the wave starting
        return [PB.tight(scaled_by(p[2], 0.6)), p[1][:, ::-1], p[2]]
    return p


def specks(c, least=3):
    """Pieces smaller than `least` squares off (the shrink's leftovers)."""
    lab, n = ndimage.label(c[..., 3] > 0)
    out = c.copy()
    for i, sz in enumerate(ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1)), 1):
        if sz < least:
            out[lab == i] = 0
    return out


def build(sheet):
    out = {}
    for name, (W, H, where, sym, ncol) in SPEC.items():
        frames = [PB.tight(f) for f in made(name, [frame(sheet, b) for b in FRAMES[name]])]
        cells = []
        for f in PB.scaled(frames, W, H):
            c = np.zeros((H, W, 4), np.uint8)
            PB.put(c, f, where)
            cells.append(c)
        cells = PB.palette(cells, ncol)
        # a_slow's crackles are 1-2 squares at this size: every speck stays (its last frame would go empty)
        cells = [specks(PB.union_mirror(c, sym), 1 if name == "a_slow" else 2) for c in cells]
        if name == "a_crush":   # the sheet's blade is a solid red column that hid the struck body: above the impact
            # (its top BLADE_ROWS) only its middle BLADE_W columns stay, a thin cut; the shards beyond SHARDS_FROM stay
            cx = (W - 1) / 2
            xx = np.abs(np.arange(W) - cx)
            for c in cells:
                c[: int(H * BLADE_ROWS), (xx > BLADE_W / 2) & (xx < SHARDS_FROM)] = 0
        out[name] = cells
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review", help="also write every strip at 6x here")
    a = ap.parse_args()
    rgb = np.asarray(Image.open(lp(a.src)).convert("RGB"))
    if rgb.shape[:2] != SIZE:
        sys.exit(f"{a.src}: {rgb.shape[1]}x{rgb.shape[0]}, not the {SIZE[1]} x {SIZE[0]} sheet")
    out = build(key(rgb))
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    os.makedirs(lp(os.path.join(OUT, "icons")), exist_ok=True)
    meta = {}
    for name, cs in out.items():
        Image.fromarray(np.concatenate(cs, axis=1)).save(lp(os.path.join(OUT, "pixel_1x", f"mightymech_fx_{name}.png")))
        meta[name] = {"frames": len(cs), "cell": [cs[0].shape[1], cs[0].shape[0]], "symmetry": SPEC[name][3]}
        print(f"{name:12s} {len(cs)} x {cs[0].shape[1]}x{cs[0].shape[0]}")
    with open(lp(os.path.join(OUT, "cells.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    for n, box in ICONS.items():
        PB.icon(rgb, box).save(lp(os.path.join(OUT, "icons", f"mightymech_icon_{n}.png")))
    if a.review:
        PB.review(out, a.review)


if __name__ == "__main__":
    main()

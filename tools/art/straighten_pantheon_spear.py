#!/usr/bin/env python3
"""Pantheon's design spear made one straight line (the user, 2026-10-16: 「潘森的武器怎么看起来是歪的 调直了」, then
「折的拉成一条直线」).

    python tools/art/straighten_pantheon_spear.py [--review DIR]

The design's spear bent twice: the butt end ran down at ~34 degrees to the hand, the hidden part on at ~23 degrees and
the head at 45 degrees, 3 squares above the line. The shaft's visible middle (the fist to the shin) is already a 2:1 line, and the butt cap and the head's
gem sit on it; only the butt end sagged ~2 squares and the head was turned to 45 degrees round its gem. So:
  * the butt cap is moved whole onto the line and a shaft of Codex's own level shaft column (e_hold frame 1: outline,
    gold, outline) runs from it to the fist, one square down every two columns;
  * the design's own head (the squares within HEAD_BAND of its 45-degree axis, right of the shin) keeps every pixel,
    each column moved whole onto the line (the gem stays where it was, the tip comes up 3 squares);
  * nothing is resampled or redrawn.
Reads assets/source/pantheon/hd/design_bent.png (the cut the user picked), writes assets/source/pantheon/hd/design.png.
Then tools/art/rig_pantheon.py, ppu_restyle.py --hero pantheon, ppu_hd.py --hero pantheon.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "pantheon", "hd")
PPU_ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")

LINE = (38.5, 45)        # a square on the visible middle of the shaft (hand to shin, already 2:1)
BUTT = (10, 15, 31, 35)  # the butt cap: columns 10-15, rows 31-35
BUTT_X = (10, 25)        # the butt end's columns, up to the fist
BUTT_ROWS = (31, 41)     # its rows (row 30 is the cape's hem)
OLD_HEAD = 3             # the old head's axis: y = x - OLD_HEAD (through the gem at (57, 54), 45 degrees)
HEAD_BAND = 3.0          # |x - y - OLD_HEAD| <= this: the old head
HEAD_FROM = 53           # the head's first column right of the shin


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def axis_y(x):
    """The spear's axis row at column x: one square down every two columns, through the shaft's middle."""
    return int(LINE[1] + (x - LINE[0]) // 2)


def level_shaft():
    """A plain column of Codex's level shaft (e_hold frame 1): outline, gold, outline; its gold row."""
    im = Image.open(lp(os.path.join(PPU_ORIG, "pantheon_e_hold.png"))).convert("RGBA")
    w, h = json.load(open(lp(os.path.join(PPU_ORIG, "pantheon_e_hold.json"))))["sizes"][0]
    f = np.array(im.crop((0, 0, w, h)))
    x1 = Image.fromarray(f).getbbox()[2]
    return f[22:25, x1 - 30], 1


def straighten(d):
    d = d.copy()
    rgb = d[..., :3].astype(int)
    blue = (rgb[..., 2] > rgb[..., 0] + 40) & (d[..., 3] > 0)
    # the butt cap, moved whole onto the line
    cx0, cx1, cy0, cy1 = BUTT
    cap = {(x, y): d[y, x].copy() for y in range(cy0, cy1 + 1) for x in range(cx0, cx1 + 1)
           if d[y, x, 3] and not blue[y, x]}
    cap_dy = axis_y((cx0 + cx1) // 2) - (cy0 + cy1) // 2
    # the old head: its squares within the band, each column moved onto the line (the column's pixels kept)
    head = {(x, y): d[y, x].copy() for y in range(44, d.shape[0]) for x in range(HEAD_FROM, d.shape[1])
            if d[y, x, 3] and abs(x - y - OLD_HEAD) <= HEAD_BAND}
    for y in range(BUTT_ROWS[0], BUTT_ROWS[1] + 1):
        for x in range(BUTT_X[0], BUTT_X[1] + 1):
            if not blue[y, x]:
                d[y, x] = 0
    for (x, y) in head:
        d[y, x] = 0
    shaft, gold = level_shaft()
    for x in range(cx1 - 1, BUTT_X[1] + 1):
        for k in range(shaft.shape[0]):
            y = axis_y(x) - gold + k
            if d[y, x, 3] == 0:
                d[y, x] = shaft[k]
    for (x, y), c in cap.items():
        d[y + cap_dy, x] = c
    for (x, y), c in head.items():
        d[y + axis_y(x) - (x - OLD_HEAD), x] = c
    # the old head's outline squares just outside the band, left alone on the ground (one at (58, 59))
    a = d[..., 3] > 0
    for y in range(44, d.shape[0]):
        for x in range(HEAD_FROM, d.shape[1]):
            if a[y, x] and not any(a[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                                   if 0 <= y + dy < d.shape[0] and 0 <= x + dx < d.shape[1]):
                d[y, x] = 0
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write before/after sheets (8x and 3x) here instead of the design")
    a = ap.parse_args()
    src = np.array(Image.open(lp(os.path.join(HD, "design_bent.png"))).convert("RGBA"))
    out = straighten(src)
    if a.review:
        os.makedirs(lp(a.review), exist_ok=True)
        for z in (8, 3):
            sheet = Image.new("RGBA", (src.shape[1] * z * 2 + 10 * z, src.shape[0] * z), (90, 96, 86, 255))
            for i, im in enumerate((src, out)):
                big = Image.fromarray(im).resize((src.shape[1] * z, src.shape[0] * z), Image.NEAREST)
                sheet.alpha_composite(big, (i * (src.shape[1] + 10) * z, 0))
            sheet.save(lp(os.path.join(a.review, f"spear_{z}x.png")))
        print("review sheets in", a.review)
        return
    Image.fromarray(out).save(lp(os.path.join(HD, "design.png")))
    print("wrote", os.path.join(HD, "design.png"))


if __name__ == "__main__":
    main()

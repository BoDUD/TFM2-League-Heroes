#!/usr/bin/env python3
"""LeBlanc's dense (PPU 2.0) design: Codex's step-1 take A of 2026-10-02 as drawn, the staff's shaft straight, the leg
gaps filled.

    python tools/art/design_leblanc_hd.py [--review DIR]

The user, 2026-10-19, on a PPU redo pack for her: 「其实这个就挺好的 你只要把法杖做好 利用PPU就行了」 (take A,
assets/source/leblanc/codex_model/leblanc_design_A_1x.png: 51 x 86 squares, one square a pixel, read back by Codex on
its own 8-px grid; 86 rows over her 43 game rows = PPU 2.0, the user's pick 「PPU 2.0 原样」), 「另外法杖别做歪啊」 and
「腿部有缺失像素的地方补上就行」. Nothing is cut or resampled; three edits:
  1. the shaft from under the wings' neck (row Y0) to the foot (row Y1): Codex drew it wandering over three columns
     (gold squares zig-zagging, a step of two at the foot); the old shaft is taken away (each row's rightmost run of
     outline / gold / red squares, at most 5 wide, with gold in it; above the hand all right of column 37) and it is
     drawn again as one straight line of its own lower-shaft squares - outline, gold, outline - on the crystal's middle
     column AXIS, a lighter gold square every 6th row, closed by a row of outline at the foot; the gripping glove
     (rows HAND, its own colours GLOVE) stays drawn over it; what the old shaft left against the new one (small loose
     pieces, the short dark run of its ring at row 78) is taken away. The crystal, the bat-wing guards and their gold
     neck stay as drawn.
  2. the leg gaps: clear squares in the legs and the hem (rows 70 down, left of the staff) walled on 5 or more of
     their 8 sides take the commonest colour round them (not the outline): 12 squares.
-> assets/source/leblanc/hd/design.png. With --review: <dir>/leblanc_design_fix.png (Codex's take, the design, the
filled squares magenta) at 10x.
"""
import argparse
import os

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "leblanc")
CROP = (39, 14, 90, 100)                        # the figure's box on Codex's 128 x 128 canvas
AXIS = 41                                       # the crystal's middle column
Y0, Y1 = 31, 84                                 # the shaft redrawn from under the wings' neck to the foot
HAND = range(43, 53)                            # the glove gripping it
GLOVE = {(55, 12, 43), (107, 15, 53), (19, 2, 21), (5, 0, 19), (97, 1, 21)}
OUTLINE, SHAFT, HI = (3, 0, 15), (217, 155, 64), (233, 177, 94)
LEG_ROW, LEG_RIGHT = 70, 36                     # the leg gaps: rows from here down, columns left of this


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def take():
    d = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", "leblanc_design_A_1x.png"))).convert("RGBA"))
    x0, y0, x1, y1 = CROP
    return d[y0:y1, x0:x1].copy()


def straight_staff(d):
    H, W = d.shape[:2]
    rgb = d[..., :3].astype(int)
    op = d[..., 3] > 0
    dark = op & (rgb.sum(-1) < 70)
    gold = op & (rgb[..., 0] > 150) & (rgb[..., 1] > 90) & (rgb[..., 0] - rgb[..., 2] > 60)
    red = op & (rgb[..., 0] > 90) & (rgb[..., 1] < 40) & ~gold
    staffish = dark | gold | red
    out = d.copy()
    for y in range(Y0, H):
        if y in HAND:
            for x in range(39, 44):
                if op[y, x] and tuple(rgb[y, x]) not in GLOVE and staffish[y, x]:
                    out[y, x] = 0
            continue
        if y < HAND[0]:
            out[y, 38:] = 0
            continue
        xs = np.nonzero(op[y])[0]
        if not len(xs) or xs.max() < 36:
            continue
        x1 = xs.max()
        x0 = x1
        while x0 - 1 >= 0 and staffish[y, x0 - 1] and x1 - (x0 - 1) < 5:
            x0 -= 1
        if gold[y, x0:x1 + 1].any():
            out[y, x0:x1 + 1] = 0
    for y in range(Y0, Y1 + 1):
        for x, c in ((AXIS - 1, OUTLINE), (AXIS, HI if (y - Y0) % 6 == 0 else SHAFT), (AXIS + 1, OUTLINE)):
            if y in HAND and out[y, x, 3] and tuple(out[y, x, :3].astype(int)) in GLOVE:
                continue
            out[y, x] = (*c, 255)
    # the old shaft's leavings: loose pieces of at most 6 squares beside it, a short dark run against it
    shaft = np.zeros((H, W), bool)
    shaft[Y0:Y1 + 1, AXIS - 1:AXIS + 2] = True
    lbl, n = ndimage.label((out[..., 3] > 0) & ~shaft, structure=np.ones((3, 3)))
    for k in range(1, n + 1):
        m = lbl == k
        ys, xs = np.nonzero(m)
        if m.sum() <= 6 and ys.min() >= Y0 and ys.max() <= Y1 and xs.min() >= 34:
            out[m] = 0
    for y in range(Y0, Y1 + 1):
        if y in HAND:
            continue
        x = AXIS - 2
        while x >= 0 and out[y, x, 3] and int(out[y, x, :3].astype(int).sum()) < 70:
            x -= 1
        if 0 < AXIS - 2 - x <= 3 and x >= 0 and not out[y, x, 3]:
            out[y, x + 1:AXIS - 1] = 0
    out[Y1 + 1, 36:] = 0
    out[Y1 + 1, AXIS - 1:AXIS + 2] = (*OUTLINE, 255)
    return out


def fill_legs(out):
    H, W = out.shape[:2]
    fill = np.zeros((H, W), bool)
    o = out[..., 3] > 0
    for _ in range(3):
        n = ndimage.convolve(o.astype(int), np.ones((3, 3), int), mode="constant") - o
        cand = ~o & (n >= 5)
        cand[:LEG_ROW] = False
        cand[:, LEG_RIGHT:] = False
        if not cand.any():
            break
        for y, x in zip(*np.nonzero(cand)):
            nb = [tuple(int(v) for v in out[yy, xx]) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
                  if 0 <= yy < H and 0 <= xx < W and out[yy, xx, 3] and (yy, xx) != (y, x)]
            cols = [c for c in nb if sum(c[:3]) >= 70] or nb
            vals, counts = np.unique(np.array(cols), axis=0, return_counts=True)
            out[y, x] = vals[counts.argmax()]
        fill |= cand
        o = out[..., 3] > 0
    return out, fill


def design():
    d = take()
    out, fill = fill_legs(straight_staff(d))
    return d, out, fill


def big(a, z=10, bg=(225, 225, 225, 255)):
    b = Image.new("RGBA", (a.shape[1] * z, a.shape[0] * z), bg)
    b.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1)))
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    d, out, fill = design()
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    Image.fromarray(out).save(lp(os.path.join(SRC, "hd", "design.png")))
    print(f"assets/source/leblanc/hd/design.png {out.shape[1]} x {out.shape[0]}, {int(fill.sum())} leg squares filled")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        mark = out.copy()
        mark[fill] = (255, 0, 255, 255)
        tiles = [big(d), big(out), big(mark)]
        o = Image.new("RGBA", (sum(t.width + 20 for t in tiles), tiles[0].height), (60, 60, 60, 255))
        x = 0
        for t in tiles:
            o.paste(t, (x, 0))
            x += t.width + 20
        o.save(os.path.join(a.review, "leblanc_design_fix.png"))


if __name__ == "__main__":
    main()

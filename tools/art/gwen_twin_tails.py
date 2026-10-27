#!/usr/bin/env python3
"""Gwen's twin tails: the picture the user gave Codex (hd/raw/gwen-v2.png) has THREE drill tails - one hanging from the
bow at the back of her head (image left), one in front of her near cheek and one on the far side - and the design and
every action Codex drew after it kept all three. The user, 2026-10-27: 「格温双马尾你做成三马尾了 想办法修复一下吧」,
then 「去掉最左边吧」: the one behind her head goes, the bow it hangs from stays; nothing behind it needs drawing (only
the ground shows there).

  design_cut(d)   the design (hd/design.png, written once by --design): its squares from row 38 down left of column 30
                  (and rows 34-37 left of 22: the drill's top under the bow), the new edge closed in the outline colour.
                  The frames casts_gwen_hd.right_hand builds on the design's upper body (attack 1/8, Q 14, E 1-4, R 4-5)
                  follow it by themselves.
  cut_casts(fr)   every other cast frame Codex drew: the tail's squares inside a polygon marked by hand per frame (CUTS:
                  the frames that are one picture share one), except the bow's navy squares near the polygon's top
                  that hang on to her head; the new edge closed in the outline colour, and the tail's bits left cut off
                  near the polygon (60 squares at most) gone with it.

    python tools/art/gwen_twin_tails.py --design     # rewrite hd/design.png without the back tail (idempotent)
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "gwen", "hd")
OUTLINE = (6, 2, 19)
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
# (the frames that are one picture, the polygon round the back tail in that picture's own squares)
CUTS = [
    (("attack_2",), [(55, 32), (81, 32), (81, 40), (74, 48), (68, 52), (68, 66), (54, 66)]),
    (("attack_3",), [(0, 32), (26, 32), (26, 46), (14, 50), (12, 63), (0, 63)]),
    (("attack_4", "attack_5"), [(0, 30), (27, 30), (28, 44), (22, 50), (12, 52), (10, 62), (0, 62)]),
    (("attack_6", "attack_7"), [(0, 31), (29, 31), (30, 44), (22, 52), (16, 56), (12, 62), (0, 62)]),
    (("skill_1",), [(0, 32), (20, 32), (21, 50), (14, 54), (12, 66), (0, 66)]),
    (("skill_2", "skill_5", "skill_6"), [(0, 33), (29, 33), (29, 48), (16, 52), (14, 64), (0, 64)]),
    (("skill_3", "skill_4", "skill_7", "skill_8"), [(0, 34), (24, 34), (25, 50), (16, 54), (14, 65), (0, 65)]),
    (("skill_9", "skill_10", "skill_11"), [(0, 34), (22, 34), (22, 50), (14, 54), (12, 64), (0, 64)]),
    (("skill_12",), [(0, 32), (27, 32), (27, 48), (16, 52), (14, 64), (0, 64)]),
    (("skill_13",), [(0, 34), (24, 34), (24, 50), (14, 54), (12, 64), (0, 64)]),
    (("skill_15",), [(2, 36), (27, 36), (27, 50), (16, 54), (14, 67), (2, 67)]),
    (("skill2_6", "skill2_8"), [(0, 84), (21, 84), (21, 100), (14, 104), (12, 114), (0, 114)]),
    (("skill2_7",), [(0, 98), (24, 98), (24, 112), (16, 116), (14, 130), (0, 130)]),
    (("ult_1",), [(9, 34), (31, 34), (31, 48), (22, 54), (20, 67), (9, 67)]),
    (("ult_2", "ult_3"), [(8, 32), (30, 32), (30, 46), (22, 52), (20, 64), (8, 64)]),
    (("ult_6",), [(10, 34), (31, 34), (31, 48), (24, 54), (22, 66), (10, 66)]),
    (("hit_1",), [(6, 36), (27, 36), (27, 50), (19, 54), (16, 66), (6, 66)]),
    (("hit_2",), [(8, 36), (29, 36), (29, 48), (22, 52), (18, 64), (8, 64)]),
    (("dead_1",), [(0, 34), (21, 34), (21, 50), (16, 56), (14, 72), (0, 72)]),
    (("dead_2",), [(0, 30), (19, 30), (19, 48), (14, 56), (14, 74), (0, 74)]),
    (("dead_3",), [(6, 54), (26, 54), (29, 60), (27, 70), (26, 76), (24, 90), (6, 90)]),
    (("dead_4",), [(0, 44), (24, 44), (27, 50), (27, 60), (26, 76), (0, 76)]),
    (("dead_5",), [(4, 37), (27, 37), (29, 44), (28, 57), (4, 57)]),
    (("dead_6",), [(2, 32), (24, 32), (26, 40), (24, 50), (2, 50)]),
    (("dead_7", "dead_8"), [(2, 34), (24, 34), (26, 42), (24, 50), (2, 50)]),
]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def close(a, gone):
    """The squares next to the removed ones (gone) the outline colour: the new edge closed."""
    edge = ndimage.binary_dilation(gone, structure=CROSS) & (a[..., 3] > 0) & ~gone
    a[edge, :3] = OUTLINE
    a[edge, 3] = 255
    return a


def design_cut(d):
    m = np.zeros(d.shape[:2], bool)
    m[38:69, :30] = True
    m[34:38, :22] = True
    m &= d[..., 3] > 0
    out = d.copy()
    out[m] = 0
    return close(out, m)


def cut(pic, poly):
    """pic without the back tail inside poly (see the module's notes)."""
    h, w = pic.shape[:2]
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=1, outline=1)
    m = np.asarray(m).astype(bool) & (pic[..., 3] > 0)
    rgb = pic[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    top = min(p[1] for p in poly)
    navy = (b >= 50) & (b <= 170) & (r <= 45) & (g <= 95) & (np.arange(h)[:, None] < top + 8)
    outside = (pic[..., 3] > 0) & ~m
    lbl, _ = ndimage.label((m & navy) | outside, structure=CROSS)
    m &= ~(navy & np.isin(lbl, list(set(np.unique(lbl[outside])) - {0})))
    out = pic.copy()
    out[m] = 0
    out = close(out, m)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs) - 8, max(xs) + 8, min(ys) - 8, max(ys) + 8
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    sz = ndimage.sum(op, lbl, range(1, n + 1))
    main = int(np.argmax(sz)) + 1
    for k in range(1, n + 1):
        if k == main:
            continue
        yy, xx = np.nonzero(lbl == k)
        near = ((xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)).mean() > 0.5
        if sz[k - 1] <= 8 or (sz[k - 1] <= 60 and near):
            out[lbl == k] = 0
    return out


def cut_casts(fr):
    """{name: (picture, x, y)} with the back tail cut from every frame CUTS names."""
    out = dict(fr)
    for names, poly in CUTS:
        for n in names:
            pic, x, y = fr[n]
            out[n] = (cut(pic, poly), x, y)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", action="store_true")
    a = ap.parse_args()
    if a.design:
        p = lp(os.path.join(HD, "design.png"))
        d = np.asarray(Image.open(p).convert("RGBA"))
        Image.fromarray(design_cut(d)).save(p)
        print("hd/design.png written")


if __name__ == "__main__":
    main()

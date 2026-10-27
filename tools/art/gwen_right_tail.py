#!/usr/bin/env python3
"""Gwen's near-side drill (image right) read as two tails: between the cheek lock (its pink edge) and the drill hangs a
narrow navy strand of its own, outlined on both sides, so the side read lock - strand - drill, three tails (the user,
2026-10-28: 「怎么格温模型头发右边看起来还有三个马尾的感觉？」, then 「把中间那条深蓝细发束并进卷筒马尾，当马尾的暗面，
所有动作都改」). The strand becomes the drill's shadow side: its navy squares take the drill's darkest blues and the
outline between it and the drill goes (the drill's dark blue there); the outline between it and the cheek lock stays.

  merge(pic, box)   inside box (x0, y0, x1, y1): NAVY squares recoloured, and the outline squares with a recoloured
                    square on their left and a drill square (LIGHT) on their right turned the drill's dark blue.
  design_merge(d)   the design (hd/design.png, written once by --design): the box DESIGN_BOX. The frames built on the
                    design (the idle, the run, casts_gwen_hd.right_hand's attack 1/8, Q 14, E 1-4, R 4-5) follow it.
  merge_casts(fr)   every other cast frame Codex drew with the strand where the design has it: the design's box moved by
                    the frame's own offset (MOVES: where the design's lock-strand-drill patch, columns 58-79 / rows 22-51,
                    matches the frame best). The falls (dead 2, 4-8) and E's raised arms (skill2 6-8) are left alone - the
                    patch does not sit on her hair there.

    python tools/art/gwen_right_tail.py --design     # rewrite hd/design.png with the strand merged (idempotent)
"""
import argparse
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "gwen", "hd")
# the strand's navy -> the drill's shadow blues
NAVY = {(0x0d, 0x1e, 0x5b): (0x17, 0x4c, 0x9d), (0x09, 0x14, 0x41): (0x17, 0x4c, 0x9d), (0x18, 0x32, 0x82): (0x03, 0x5b, 0xbb)}
OUTLINES = {(0x07, 0x07, 0x23), (0x06, 0x02, 0x13)}
SEAM = (0x03, 0x5b, 0xbb)
LIGHT = {(0x14, 0xcb, 0xf7), (0x17, 0xda, 0xfc), (0x3c, 0xbd, 0xeb), (0xc7, 0xcc, 0xe0), (0xb4, 0xb4, 0xd9), (0x19, 0xa8, 0xef),
         (0x25, 0x8e, 0xe3), (0x0b, 0x6f, 0xc8), (0x30, 0x79, 0x99), (0x03, 0x5b, 0xbb), (0x17, 0x4c, 0x9d), (0x21, 0x7e, 0xc3),
         (0x95, 0x98, 0xc4)}
# the strand in the design's squares, and the corner of the patch the frames were matched on
DESIGN_BOX = (70, 35, 74, 44)
PATCH = (58, 22)
# (the frames that are one picture, where the design's patch corner lands in that picture)
MOVES = [
    (("attack_2",), (110, 23)),
    (("attack_3",), (58, 24)),
    (("attack_4", "attack_5"), (59, 25)),
    (("attack_6", "attack_7"), (59, 26)),
    (("dead_1",), (39, 18)),
    (("dead_3",), (47, 19)),
    (("hit_1",), (53, 19)),
    (("hit_2",), (53, 20)),
    (("skill_1",), (50, 24)),
    (("skill_2", "skill_5", "skill_6"), (55, 23)),
    (("skill_3", "skill_4", "skill_7", "skill_8", "skill_15"), (50, 23)),
    (("skill_9", "skill_10", "skill_11"), (49, 22)),
    (("skill_12",), (51, 22)),
    (("skill_13",), (47, 22)),
    (("skill2_5", "skill2_9"), (58, 22)),
    (("ult_1", "ult_2", "ult_3"), (56, 21)),
    (("ult_6",), (57, 22)),
]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def merge(pic, box):
    """pic with the strand inside box merged into the drill (see the module's notes)."""
    x0, y0, x1, y1 = box
    h, w = pic.shape[:2]
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, w), min(y1, h)
    rgb = lambda y, x: tuple(int(v) for v in pic[y, x, :3])  # noqa: E731
    navy = np.zeros((h, w), bool)
    for y in range(y0, y1):
        for x in range(x0, x1):
            navy[y, x] = pic[y, x, 3] > 0 and rgb(y, x) in NAVY
    out = pic.copy()
    for y in range(y0, y1):
        for x in range(max(x0, 1), min(x1 + 1, w - 1)):
            if (pic[y, x, 3] and rgb(y, x) in OUTLINES and navy[y, x - 1] and pic[y, x + 1, 3]
                    and rgb(y, x + 1) in LIGHT):
                out[y, x, :3] = SEAM
    for y, x in zip(*np.nonzero(navy)):
        out[y, x, :3] = NAVY[rgb(y, x)]
    return out


def design_merge(d):
    return merge(d, DESIGN_BOX)


def box_at(corner):
    dx, dy = corner[0] - PATCH[0], corner[1] - PATCH[1]
    x0, y0, x1, y1 = DESIGN_BOX
    return (x0 + dx - 2, y0 + dy - 2, x1 + dx + 2, y1 + dy + 2)


def merge_casts(fr):
    """{name: (picture, x, y)} with the strand merged in every frame MOVES names."""
    out = dict(fr)
    for names, corner in MOVES:
        for n in names:
            pic, x, y = fr[n]
            out[n] = (merge(pic, box_at(corner)), x, y)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", action="store_true")
    a = ap.parse_args()
    if a.design:
        p = lp(os.path.join(HD, "design.png"))
        d = np.asarray(Image.open(p).convert("RGBA"))
        Image.fromarray(design_merge(d)).save(p)
        print("hd/design.png written")


if __name__ == "__main__":
    main()

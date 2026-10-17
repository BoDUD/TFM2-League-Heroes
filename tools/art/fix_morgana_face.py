#!/usr/bin/env python3
"""Morgana's face shape (the user, 2026-10-08: 「莫甘娜脸型要改」; 2026-10-09 picked option A of three): the square
lower face - seven skin squares wide down to the mouth, one row narrower under it - becomes a V tapering to a pointed
chin in the middle: the mouth row keeps two squares either side of the face's middle, the row under it one, then the
chin point alone; what is cut off becomes outline, the light neck squares beside the point dark hair.

    python tools/art/fix_morgana_face.py            # edits the design and every strip in place (8x), then
    python tools/art/import_native.py --hero morgana

The face's middle is taken from each frame's own eyes (tools/art/fix_morgana_eyes.py's violet, one row: the middle
of the two eyes), so every frame gets the same chin wherever its head sits; frames whose eyes are closed or hidden
have their eye row and eye columns in ANCHORS; the lying deaths (the face turned on its side) keep their faces. Run
twice, it finds nothing left to change.
"""
import glob
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NATIVE = os.path.join(ROOT, "assets", "source", "native")


def rgb(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), np.uint8)


SKIN, INK, HAIR = rgb("F2D6EA"), rgb("0D0113"), rgb("3B1B4F")
LIGHT = [SKIN, rgb("AD828B"), rgb("966C96")]           # skin and the neck's mauve shades
GLOW, DEEP = rgb("C9A6FF"), rgb("8A4FE0")
# (tag, frame from 1): (eye row, first eye column, last eye column) where the eyes cannot be found
ANCHORS = {("hit", 1): (49, 47, 52),        # closed: two dark lid lines where the eyes are
           ("attack", 3): (49, 46, 51)}     # the far eye under the bolt's flash
SKIP = {("dead", k) for k in range(4, 9)}   # lying on her side


def load1x(path):
    return np.asarray(Image.open(path).convert("RGBA"))[::8, ::8].copy()


def save8x(a, path):
    Image.fromarray(np.repeat(np.repeat(a, 8, 0), 8, 1)).save(path)


def same(p, c):
    return p[3] and (p[:3] == c).all()


def eyes(c):
    """(eye row, first eye column, last eye column) of the violet eyes, or None."""
    m = ((c[..., :3] == GLOW).all(-1) | (c[..., :3] == DEEP).all(-1)) & (c[..., 3] > 0)
    ys, xs = np.nonzero(m)
    if len(ys) < 3:
        return None
    ey = int(np.bincount(ys).argmax())
    row = sorted(xs[ys == ey])
    return ey, int(row[0]), int(row[-1])


def put(c, x, y, col):
    c[y, x, :3] = col
    c[y, x, 3] = 255


def done(c, ey, cx):
    y = ey + 5
    return same(c[y, cx], SKIN) and same(c[y, cx - 1], INK) and same(c[y, cx + 1], INK) and same(c[y + 1, cx], INK)


def chin(c, ey, ex0, ex1):
    """Option A on one frame (in place); False when it was already there."""
    cx = (ex0 + ex1) // 2
    if done(c, ey, cx):
        return False
    for dy, keep in ((3, 2), (4, 1)):            # the mouth row: 2 either side of the middle; the row under it: 1
        y = ey + dy
        for side in (-1, 1):
            x = cx + side * (keep + 1)
            if same(c[y, x], SKIN) or (dy == 4 and c[y, x, 3]):
                put(c, x, y, INK)
            x2 = x + side
            while same(c[y, x2], SKIN):              # skin further out takes the colour under it
                c[y, x2] = c[y + 1, x2]
                x2 += side
    y = ey + 5                                       # the chin point, outlined
    put(c, cx, y, SKIN)
    put(c, cx - 1, y, INK)
    put(c, cx + 1, y, INK)
    if c[y, cx - 2, 3] and any((c[y, cx - 2, :3] == k).all() for k in LIGHT):
        put(c, cx - 2, y, HAIR)
    put(c, cx, y + 1, INK)
    return True


def main():
    with open(os.path.join(NATIVE, "morgana_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells.get("cell", [96, 96])
    dpath = os.path.join(NATIVE, "morgana_native.png")
    d = load1x(dpath)
    e = eyes(d)
    print("morgana_native.png:", "chin made" if chin(d, *e) else "already done")
    save8x(d, dpath)
    for tag in cells["tags"]:
        path = os.path.join(NATIVE, f"morgana_{tag}.png")
        a = load1x(path)
        ncol = a.shape[1] // cw
        made, kept, missing = [], [], []
        for k in range(len(cells["tags"][tag])):
            key = (tag, k + 1)
            if key in SKIP:
                kept.append(k + 1)
                continue
            c = a[(k // ncol) * ch:(k // ncol + 1) * ch, (k % ncol) * cw:(k % ncol + 1) * cw]
            anchor = ANCHORS.get(key) or eyes(c)
            if anchor is None:
                missing.append(k + 1)
                continue
            if chin(c, *anchor):
                made.append(k + 1)
        if made:
            save8x(a, path)
        print(f"morgana_{tag}.png: chin made in {made or '-'}"
              + (f", lying (kept) {kept}" if kept else "") + (f", NO FACE FOUND {missing}" if missing else ""))


if __name__ == "__main__":
    main()

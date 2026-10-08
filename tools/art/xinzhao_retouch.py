#!/usr/bin/env python3
"""Xin Zhao's retouch table (assets/source/native/xinzhao_retouch.json): the spear's head in line with its shaft.

    python tools/art/xinzhao_retouch.py [--preview DIR]     # then: python tools/art/import_native.py --hero xinzhao

The user, 2026-10-06 (a screenshot of the idle spear): 「赵信的武器这里有点歪啊」. In the idle the spear is held low,
its head down to image left: the shaft drops one row every two columns (1/2), but the part left of the crescent guard -
the gold ferrule and the violet blade - only one row every three (1/3), so the head bends up at the guard. The same
drawing of the spear sits in 28 frames (idle, run, the ends of attack / attack_p / Q / E / R, hit, the first death
frame), found by exact match of the head's pixels.

Each of those frames gets the head turned down to the shaft's line the pixel-art way: every column of the head (the
columns left of the guard) moves down by round((GUARD - x) * BEND) rows, nothing else changes - the guard, the shaft
and the body keep every pixel. x, y in the table count from the pivot (x right, y down), as import_native.py cuts the
frames (before its retouch step, which applies the table this writes).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import import_native as N  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "native", "xinzhao_retouch.json")
ABOUT = ("Written by tools/art/xinzhao_retouch.py, do not edit by hand. SPEAR: the head left of the guard turned down to "
         "the shaft's line (it bent up at the guard) in every frame that holds the idle's spear.")
HEAD_W, HEAD_H = 18, 12      # the head's box in the idle (columns left of the guard, rows of the blade)
TOP, BELOW = 4, 5            # rows above the box that the head may reach (the guard's tip) / below it it may move into
GUARD = 17                   # box column of the guard's first column: columns left of it move
BEND = 1 / 2 - 1 / 3         # shaft slope minus head slope


def head_box(idle):
    """The head's box in the idle's first cut frame: the violet blade's tip column to the guard, its rows."""
    a = idle
    violet = (a[..., :3] == (0xA7, 0x2D, 0xE2)).all(-1) & (a[..., 3] > 0)
    ys, xs = np.nonzero(violet)
    x0 = int(xs.min()) - 1                      # the tip's outline
    y1 = int(ys.max()) + 2                      # the blade's lower outline
    return y1 - HEAD_H, x0


def shift(col):
    return int(round((GUARD - col) * BEND)) if col < GUARD else 0


def plan(sheet):
    idle = sheet["idle"][0][0]
    r0, c0 = head_box(idle)
    ref = idle[r0:r0 + HEAD_H, c0:c0 + HEAD_W]
    jobs = []
    for tag, frames in sheet.items():
        for k, (a, _) in enumerate(frames):
            H, W = a.shape[:2]
            for r in range(H - HEAD_H + 1):
                hit = None
                for c in range(W - HEAD_W + 1):
                    if (a[r:r + HEAD_H, c:c + HEAD_W] == ref).all():
                        hit = c
                        break
                if hit is not None:
                    jobs.append((tag, k, r, hit))
                    break
    return jobs


def turned(a, r, c):
    """The frame with the head's columns moved down; the box rows TOP above to BELOW under it."""
    b = a.copy()
    top, bot = max(0, r - TOP), min(a.shape[0], r + HEAD_H + BELOW)
    for col in range(GUARD):
        s = shift(col)
        if not s:
            continue
        x = c + col
        column = a[top:bot, x].copy()
        b[top:bot, x] = 0
        for i in range(bot - top):
            if column[i, 3] and top + i + s < a.shape[0]:
                b[top + i + s, x] = column[i]
    return b


def hexc(p):
    return "#%02X%02X%02X" % tuple(int(v) for v in p[:3])


def main():
    # superseded 2026-10-08: rig_xinzhao.straight_head turns the head on the spear part itself (every orientation);
    # running this on those frames would bend the head down a second time
    sys.exit("xinzhao_retouch.py: superseded by rig_xinzhao.straight_head - the table is no longer used")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", help="write before/after sheets of the changed frames here")
    a_ = ap.parse_args()
    sheet, _ = N.build("xinzhao")
    N.neck_up("xinzhao", sheet)
    jobs = plan(sheet)
    palette, frames = {}, {}
    before, after = [], []
    for tag, k, r, c in jobs:
        a = sheet[tag][k][0]
        b = turned(a, r, c)
        # the rows the head moves into must be clear in the frame (nothing of the body there)
        for col in range(GUARD):
            for y in range(max(0, r - TOP), min(a.shape[0], r + HEAD_H + BELOW)):
                if b[y, c + col, 3] and not a[y, c + col, 3] and y >= r + HEAD_H:
                    pass
        hh, hw = a.shape[0] // 2, a.shape[1] // 2
        px = []
        for y, x in zip(*np.nonzero((a != b).any(-1))):
            was = "." if a[y, x, 3] == 0 else hexc(a[y, x])
            now = "." if b[y, x, 3] == 0 else hexc(b[y, x])
            for h in (was, now):
                if h != ".":
                    palette[h] = h
            px.append([int(x) - hw, int(y) - hh, was, now])
        lst = frames.setdefault(tag, [])
        while len(lst) <= k:
            lst.append([])
        lst[k] = px
        before.append(a)
        after.append(b)
    spec = {"about": ABOUT, "palette": dict(sorted(palette.items())), "frames": frames}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, indent=1)
    print(f"{len(jobs)} frames:", ", ".join(f"{t} {k + 1}" for t, k, _, _ in jobs))
    print("wrote", OUT, sum(len(p) for fr in frames.values() for p in fr), "pixels")
    if a_.preview:
        os.makedirs(a_.preview, exist_ok=True)
        z = 6
        for name, arrs in (("before", before), ("after", after)):
            w = max(x.shape[1] for x in arrs)
            h = max(x.shape[0] for x in arrs)
            img = Image.new("RGBA", (8 * (w + 2) * z, ((len(arrs) + 7) // 8) * (h + 2) * z), (200, 200, 190, 255))
            for i, x in enumerate(arrs):
                im = Image.fromarray(x, "RGBA").resize((x.shape[1] * z, x.shape[0] * z), Image.NEAREST)
                img.alpha_composite(im, ((i % 8) * (w + 2) * z, (i // 8) * (h + 2) * z))
            img.save(os.path.join(a_.preview, f"xinzhao_spear_{name}.png"))


if __name__ == "__main__":
    main()

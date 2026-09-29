#!/usr/bin/env python3
"""Tidy Codex's redraw of Fiddlesticks (design B, assets/source/fiddlesticks/MODEL_PROMPTS.md) into the native strips.

    python tools/art/tidy_fiddlesticks.py <Codex's delivery folder>

Codex delivered fiddlesticks_native.png and ten strips on the reference cells (96x96 game pixels, every pixel an
8x8 block, 15 colours, nothing under the feet line). Three things read wrong in the frames, and are fixed here
on the game pixels (one per 8x8 block) before the strips are written to assets/source/native/:
  - the eyes: the idle's two 2x2 eyes (the far one a row higher, a column between them) ran together into a
    bar of eye green in some frames (Terrify's first frame, a landing frame...): those get the idle's pair
    in the same five columns;
  - Reap's last frame has eye-green pixels on the scythe's pole (away from the head): they take the pole's
    colour;
  - the attack's claw arm (frames 2-5) sticks out of the sack's front at eye height, like a tongue: it moves
    5 rows down, out from under the sack at the chest, its root is joined to the body, and the sack gets
    an outline where the arm was.
The sideways wobble of the run (the head 12 px back and forth about the pivot) is left to
tools/art/import_native.py, which steadies him on his eyes (EYES). Then run import_native.py --hero
fiddlesticks.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z, CELL = 8, 96
TAGS = ["idle", "run", "attack", "skill", "skill2", "w_loop", "ult", "ult_land", "hit", "dead"]
EYE = (200, 224, 96)
OUTLINE = (20, 10, 14)
BURLAP = [(234, 203, 148), (200, 152, 94), (148, 100, 56), (160, 138, 64), (110, 90, 40)]
# the idle's eyes from the near eye's lower row and the pair's first column (dx, dy): the near eye on the left,
# the far one a row higher on the right, a column between them
NEAR = [(0, -1), (1, -1), (0, 0), (1, 0)]
FAR = [(3, -2), (4, -2), (3, -1), (4, -1)]
ARM_FRAMES = {"attack": [1, 2, 3, 4]}
ARM_DOWN = 5


def lp(p):
    return G.lp(p)


def blocks(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    return b[:, 0, :, 0].copy()


def is_col(c, rgb):
    return (c[..., 3] > 0) & (c[..., :3] == np.array(rgb, np.uint8)).all(-1)


def burlap(c):
    m = np.zeros(c.shape[:2], bool)
    for rgb in BURLAP:
        m |= is_col(c, rgb)
    return m


def clusters(mask, gap=1):
    """Groups of mask pixels, two pixels in one group when they are at most gap + 1 apart (Chebyshev)."""
    pts = list(zip(*np.nonzero(mask)))
    groups, seen = [], set()
    for p in pts:
        if p in seen:
            continue
        todo, g = [p], []
        seen.add(p)
        while todo:
            y, x = todo.pop()
            g.append((y, x))
            for q in pts:
                if q not in seen and abs(q[0] - y) <= gap + 1 and abs(q[1] - x) <= gap + 1:
                    seen.add(q)
                    todo.append(q)
        groups.append(g)
    return groups


def head_eyes(c):
    """The eyes - the group of eye-green pixels with the most light sack pixels round it - and their middle;
    eye green anywhere else (Reap's last frame has some on the scythe's pole) is returned apart."""
    eye = is_col(c, EYE)
    light = is_col(c, BURLAP[0]) | is_col(c, BURLAP[1])
    best, score = None, 0
    groups = clusters(eye)
    for g in groups:
        n = sum(light[max(0, y - 2):y + 3, max(0, x - 2):x + 3].sum() for y, x in g)
        if n > score:
            best, score = g, n
    stray = np.zeros_like(eye)
    for g in groups:
        if g is not best:
            for y, x in g:
                stray[y, x] = True
    if best is None:
        return None, stray
    ys, xs = zip(*best)
    return (int(np.floor(np.mean(xs) + 0.5)), int(np.floor(np.mean(ys) + 0.5))), stray


def fill_colour(c, y, x, avoid):
    """The commonest colour of the 8 neighbours that is not `avoid` and not transparent."""
    cols = {}
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            yy, xx = y + dy, x + dx
            if (dy or dx) and 0 <= yy < c.shape[0] and 0 <= xx < c.shape[1] and c[yy, xx, 3]:
                k = tuple(int(v) for v in c[yy, xx, :3])
                if k not in avoid:
                    cols[k] = cols.get(k, 0) + 1
    return max(cols, key=cols.get) if cols else None


def fix_eyes(c):
    """Eyes run together into a bar (a row of five eye pixels) are redrawn as the idle's pair, the far eye a row
    above the near one, in the same five columns (the rows moved so the near eye keeps its lower row); stray eye
    green takes its neighbours' colour. Level pairs with a gap, the tilted head of the channel and a lone eye
    stay as drawn. Returns pixels changed."""
    before = c.copy()
    mid, stray = head_eyes(c)
    for y, x in zip(*np.nonzero(stray)):
        col = fill_colour(c, y, x, {EYE})
        if col:
            c[y, x, :3] = col
    if mid is None:
        return int((before != c).any(-1).sum())
    eye = is_col(c, EYE) & ~stray
    ys, xs = np.nonzero(eye)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    bar = x1 - x0 == 4 and any(eye[y, x0:x1 + 1].all() for y in range(y0, y1 + 1))
    if bar:
        for y, x in zip(ys, xs):                        # the old eyes become sack
            c[y, x, :3] = fill_colour(c, y, x, {EYE, OUTLINE}) or BURLAP[1]
        low = y1                                        # the near eye's lower row
        for dx, dy in NEAR + FAR:
            y, x = low + dy, x0 + dx
            if c[y, x, 3]:
                c[y, x, :3] = EYE
    return int((before != c).any(-1).sum())


def lower_arm(c):
    """The claw arm stretched out of the sack's front: everything right of the sack (a line one pixel past its
    rightmost pixel, the sack found by its own colours - the straw colours are on the arm too) moves ARM_DOWN
    rows down, out from under the sack; the forearm's rows (the leftmost ones) are drawn on leftwards until
    they meet the body, and the sack is outlined where the arm left it. Returns pixels changed."""
    before = c.copy()
    (mx, my), _ = head_eyes(c)
    sack = np.zeros(c.shape[:2], bool)
    for rgb in BURLAP[:3] + [EYE]:
        sack |= is_col(c, rgb)
    band = sack[my - 9:my + 9, mx - 9:mx + 9]
    rmax = mx - 9 + int(np.nonzero(band.any(0))[0].max())
    cut = rmax + 2
    arm = np.zeros(c.shape[:2], bool)
    arm[my - 12:my + 10, cut:] = c[my - 12:my + 10, cut:, 3] > 0
    ys, xs = np.nonzero(arm)
    moved = c[ys, xs].copy()
    c[arm] = 0
    c[ys + ARM_DOWN, xs] = moved
    # the forearm: rows whose first pixel is within 1 of the arm's leftmost, drawn on to the body (up to 6 px)
    first = {}
    for y, x in zip(ys + ARM_DOWN, xs):
        first[y] = min(first.get(y, x), x)
    left = min(first.values())
    for y, xl in first.items():
        if xl > left + 1:
            continue
        x = xl - 1
        while x > mx - 6 and not c[y, x, 3] and xl - x <= 6:
            c[y, x] = c[y, xl]
            x -= 1
    # the sack's right side, bare where the arm was: outlined
    for y in range(my - 9, my + 9):
        xs_ = np.nonzero(sack[y, mx - 9:mx + 9])[0]
        if len(xs_):
            e = mx - 9 + int(xs_.max())
            if not c[y, e + 1, 3]:
                c[y, e + 1, :3] = OUTLINE
                c[y, e + 1, 3] = 255
    return int((before != c).any(-1).sum())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery", help="Codex's folder with fiddlesticks_native.png and the ten strips")
    args = ap.parse_args()
    with open(lp(os.path.join(SRC, "fiddlesticks_cells.json")), encoding="utf-8") as f:
        table = json.load(f)["tags"]
    out = Image.open(lp(os.path.join(args.delivery, "fiddlesticks_native.png")))
    out.save(lp(os.path.join(SRC, "fiddlesticks_native.png")))
    for tag in TAGS:
        a = blocks(os.path.join(args.delivery, f"fiddlesticks_{tag}.png"))
        cols = a.shape[1] // CELL
        report = []
        for k in range(len(table[tag])):
            cell = a[k // cols * CELL:(k // cols + 1) * CELL, k % cols * CELL:(k % cols + 1) * CELL]
            n = 0
            if k in ARM_FRAMES.get(tag, []):
                n += lower_arm(cell)
            n += fix_eyes(cell)
            report.append(n)
        Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1), "RGBA").save(lp(os.path.join(SRC, f"fiddlesticks_{tag}.png")))
        print(f"fiddlesticks_{tag}.png  pixels changed per frame: {report}")


if __name__ == "__main__":
    main()

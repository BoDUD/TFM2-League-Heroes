#!/usr/bin/env python3
"""Clean the dark edges of Taric's game-size strips in place (the user, on the finished sprite: "最后去除黑边 弄干净一点").

    python tools/art/tidy_taric.py [--write] [--review DIR]

Reads assets/source/native/taric_<tag>.png (8x blocks, the cells of taric_cells.json) and in every frame:
  - an outline-coloured square doubling the outer outline - just inside it, a light square (luminance 70 or more) on
    its inner side, at most one other outline square beside it off the ring (so not an inner line) - takes that light
    colour: the outline is one square thick;
  - a lone square (no 4-neighbour of its colour: the specks the vote left) takes the commonest colour of its 8
    neighbours when 5 or more share it.
The outer ring stays (import_native closes it: COMPLETE), and so do the face round the eyes (from the two #182CB0
squares) and the blues (the gems, the scarf, the eyes). The run (STEADY) is first cleaned of one-frame flicker (steady:
the user, watching it: "跑动时不干净啊 多余的像素不清理吗"). Without --write it only counts; --review DIR writes the
frames before and after at 6x.
It was run once on the committed strips; the run's legs were then recoloured by Codex (the far leg darker:
assets/source/taric/MODEL_RUN_LEGS2.md), whose one-square highlights a second run would take for specks.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NATIVE = os.path.join(ROOT, "assets", "source", "native")
Z = 8
OUTLINE = (0x17, 0x0F, 0x1D)
EYE = (24, 44, 176)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def ring(op):
    """The outer ring: opaque squares with a transparent 4-neighbour."""
    p = np.pad(op, 1)
    return op & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])


def near_eye(g):
    """(row, column) of the near eye when the frame's two EYE squares are level (a row apart at most) and 2-4 apart."""
    ys, xs = np.nonzero(np.all(g[..., :3] == np.array(EYE, np.uint8), -1) & (g[..., 3] > 0))
    if len(ys) == 2 and abs(int(ys[0]) - int(ys[1])) <= 1 and 2 <= abs(int(xs[1]) - int(xs[0])) <= 4:
        k = int(np.argmin(xs))
        return int(ys[k]), int(xs[k])
    return None


def tidy(g):
    """Clean one frame in place; the squares changed."""
    op = g[..., 3] > 0
    H, W = op.shape
    keep = op & (g[..., 2].astype(int) > g[..., 0].astype(int) + 60)
    at = near_eye(g)
    if at is not None:
        keep[max(at[0] - 3, 0):at[0] + 8, max(at[1] - 4, 0):at[1] + 6] = True
    rg = ring(op)
    out = np.all(g[..., :3] == np.array(OUTLINE, np.uint8), -1) & op
    n = 0
    for y, x in zip(*np.nonzero(out & ~rg & ~keep)):
        nb = [(a, b) for a, b in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= a < H and 0 <= b < W]
        for a, b in nb:
            if rg[a, b] and out[a, b]:
                oy, ox = 2 * y - a, 2 * x - b
                inner = 0 <= oy < H and 0 <= ox < W and op[oy, ox]
                if inner and g[oy, ox, :3].astype(float) @ np.array([0.299, 0.587, 0.114]) >= 70 \
                        and sum(1 for c, d in nb if out[c, d] and not rg[c, d]) <= 1:
                    g[y, x] = g[oy, ox]
                    n += 1
                break
    op = g[..., 3] > 0
    rg = ring(op)
    for y, x in zip(*np.nonzero(op & ~rg & ~keep)):
        col = tuple(int(v) for v in g[y, x, :3])
        alone, votes = True, {}
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                a, b = y + dy, x + dx
                if (dy or dx) and 0 <= a < H and 0 <= b < W and g[a, b, 3] > 0:
                    c = tuple(int(v) for v in g[a, b, :3])
                    alone &= not (abs(dy) + abs(dx) == 1 and c == col)
                    votes[c] = votes.get(c, 0) + 1
        if alone and votes:
            c, k = max(votes.items(), key=lambda kv: kv[1])
            if k >= 5:
                g[y, x, :3] = c
                n += 1
    return n


def shifted(g, dy, dx):
    """The frame moved dy rows down and dx columns right (what falls off is lost)."""
    out = np.zeros_like(g)
    H, W = g.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    sy, sx = ys - dy, xs - dx
    ok = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W)
    out[ok] = g[sy[ok], sx[ok]]
    return out


def steady(frames, rows):
    """The loop's one-frame flicker removed, in place (the user, watching the run: "跑动时不干净啊 多余的像素不清理吗"):
    with the frames aligned on their near eye, a square that the frame before and the frame after agree on but this
    frame does not takes their colour - motion that lasts two frames or more stays. Only from the pivot row up: the
    legs below it change every frame. Returns the squares changed per frame."""
    at = [near_eye(g) for g in frames]
    before = [g.copy() for g in frames]
    n = len(frames)
    changed = []
    for k, g in enumerate(frames):
        if at[k] is None or at[k - 1] is None or at[(k + 1) % n] is None:
            changed.append(0)
            continue
        prev = shifted(before[k - 1], at[k][0] - at[k - 1][0], at[k][1] - at[k - 1][1])
        nxt = shifted(before[(k + 1) % n], at[k][0] - at[(k + 1) % n][0], at[k][1] - at[(k + 1) % n][1])
        px, py = rows[k]["pivot"]
        region = np.zeros(g.shape[:2], bool)
        region[:py + 1] = True
        flick = region & np.all(prev == nxt, -1) & ~np.all(before[k] == prev, -1)
        g[flick] = prev[flick]
        changed.append(int(flick.sum()))
    return changed


STEADY = ("run",)                      # the loops cleaned of one-frame flicker


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="write the cleaned strips back")
    ap.add_argument("--review", help="folder for before/after sheets")
    a = ap.parse_args()
    with open(lp(os.path.join(NATIVE, "taric_cells.json")), encoding="utf-8") as f:
        spec = json.load(f)
    cw, chh = spec["cell"]
    for tag, rows in spec["tags"].items():
        path = os.path.join(NATIVE, f"taric_{tag}.png")
        big = np.asarray(Image.open(lp(path)).convert("RGBA"))
        b = big.reshape(big.shape[0] // Z, Z, big.shape[1] // Z, Z, 4)
        if not (b == b[:, :1, :, :1]).all():
            sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
        a1 = b[:, 0, :, 0].copy()
        before = a1.copy()
        ncol = a1.shape[1] // cw
        views = [a1[(k // ncol) * chh:(k // ncol + 1) * chh, (k % ncol) * cw:(k % ncol + 1) * cw] for k in range(len(rows))]
        if tag in STEADY:
            print(f"{tag:8s} one-frame flicker removed per frame: {steady(views, rows)}")
        counts = [tidy(v) for v in views]
        print(f"{tag:8s} squares cleaned per frame: {counts}")
        if a.write:
            Image.fromarray(np.repeat(np.repeat(a1, Z, 0), Z, 1)).save(lp(path))
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            pair = np.concatenate([before, np.zeros((before.shape[0], 4, 4), np.uint8), a1], 1)
            bg = np.zeros(pair.shape, np.uint8)
            bg[...] = (92, 98, 86, 255)
            m = pair[..., 3] > 0
            bg[m] = pair[m]
            Image.fromarray(np.repeat(np.repeat(bg, 6, 0), 6, 1)).save(os.path.join(a.review, f"tidy_{tag}.png"))


if __name__ == "__main__":
    main()

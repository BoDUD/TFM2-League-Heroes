#!/usr/bin/env python3
"""Aurora's long-legged poses shortened to the design's legs, by me (the user, 2026-10-23: 「有问题的话你自己修复」 - no
Codex round for the legs redo pack).

    python tools/art/design_aurora_legfix.py --sheet DIR     # every pose: the design, the first readback, the fix (5x)
    python tools/art/design_aurora_legfix.py                 # writes hd/pose_<name>.png (+ .json: head_at, ground)

Codex drew eight poses' legs 2-10 rows long (hip to soles against the design's 26: a_wind 31, q_catch 29 on her toes,
r_reach 36 on her toes, q_cast's lunge 32.6, e_hop's tucked hop 29.3, the runs 29 / 31 / 29 / 26). Each is shortened
without drawing anything: whole rows go from the legs' zone only - from DROP_FROM rows under the hip (the skirt and the
coat's hem above it stay) to BOOT rows over the soles (the boots stay whole) - DROP[name] of them, the cheapest first (the
row most like a neighbour: a stocking's straight run loses nothing), each choice made again on what is left; the
outline closed after. Everything over the zone - the design's head, the arms, the wand held up, the coat - keeps its
squares and place, so the json's head box stays; the ground row is the new lowest row.
The first readbacks stay in hd_first/ (design_aurora_poses.py --rematch writes hd/ again from Codex's pictures).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_aurora_poses as DP  # noqa: E402  finish
import pack_aurora_legs as L  # noqa: E402  hip
from design_aurora_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aurora")
OUT = os.path.join(SRC, "hd")
FIRST = os.path.join(SRC, "hd_first")
DROP_FROM = 2                    # rows under the hip where the zone starts
BOOT = 8                         # rows over the soles kept whole: the short boots (the design's ankle to sole)
# rows to drop: hip to soles to the design's 26 standing (27-28 on her toes), about 24 for the strides and the lunge (the
# runs' head boxes then 102 / 104 / 102 / 104 rows over the ground: the contact frames a little lower),
# about 21 for the hops (r_leap's tucked legs)
DROP = {"a_wind": 5, "q_catch": 2, "r_reach": 8, "q_cast": 8, "e_hop": 8, "run1": 5, "run2": 5, "run3": 5}
# a wand crossing the zone (r_reach: pointed down to the right of her legs): its squares right of column x0 under the
# zone's top are taken out before the rows go (dropping rows through a diagonal leaves it stepped), then put back slid
# along the wand's own line by the rows dropped - a straight wand, a little shorter, its tip as high over her soles as
# before
WAND = {"r_reach": 52}


def first(name):
    path = os.path.join(FIRST, f"pose_{name}.png")
    with open(lp(path[:-4] + ".json"), encoding="utf-8") as f:
        meta = json.load(f)
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy(), meta


def row_cost(a, r):
    """What dropping row r loses: the squares in which it differs from its nearer twin (above or below)."""
    def diff(i, j):
        if j < 0 or j >= a.shape[0]:
            return 10 ** 6
        return int((np.abs(a[i].astype(int) - a[j].astype(int)).sum(-1) > 0).sum())
    return min(diff(r, r - 1), diff(r, r + 1))


def shorten(a, top, n):
    """a with n rows dropped from [top, lowest - BOOT], each time the cheapest -> (picture, rows dropped (original))."""
    rows = list(range(a.shape[0]))
    cur = a
    dropped = []
    for _ in range(n):
        low = int(np.nonzero(cur[..., 3].any(1))[0].max())
        zone = range(top, low - BOOT + 1)
        if len(zone) < 2:
            break
        r = min(zone, key=lambda i: (row_cost(cur, i), i))
        dropped.append(rows[r])
        cur = np.delete(cur, r, axis=0)
        del rows[r]
    return cur, sorted(dropped)


def wand_line(w):
    """The wand piece's direction (dx per row) from its squares: a least-squares line x = k y + c."""
    ys, xs = np.nonzero(w[..., 3] > 0)
    k, _ = np.polyfit(ys, xs, 1)
    return float(k)


def fix(name):
    a, meta = first(name)
    _, py = L.hip(name, meta)
    top = int(round(py)) + DROP_FROM
    wand = None
    if name in WAND:
        region = np.zeros(a.shape[:2], bool)
        region[top:, WAND[name]:] = True
        wand = np.where(region[..., None] & (a[..., 3:] > 0), a, 0).astype(np.uint8)
        a = np.where(region[..., None], 0, a).astype(np.uint8)
    b, dropped = shorten(a, top, DROP[name])
    if wand is not None:                              # slid up its own line by the rows dropped
        k = wand_line(wand)
        n = len(dropped)
        dx, dy = -int(round(k * n)), -n
        ys, xs = np.nonzero(wand[..., 3] > 0)
        ty, tx = ys + dy, xs + dx
        ok = (ty >= 0) & (ty < b.shape[0]) & (tx >= 0) & (tx < b.shape[1])
        b[ty[ok], tx[ok]] = wand[ys[ok], xs[ok]]
    b = DP.finish(b)                                  # one square of padding round it
    ys, xs = np.nonzero(b[..., 3] > 0)
    y0, x0 = ys.min(), xs.min()
    b = b[y0:ys.max() + 1, x0:xs.max() + 1]
    hx, hy = meta["head_at"]
    at = (int(hx + 1 - x0), int(hy + 1 - y0))
    return b, dict(meta, head_at=[at[0], at[1]], ground=int(b.shape[0])), dropped, a


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma-separated pose names")
    a = ap.parse_args()
    names = [n for n in DROP if not a.only or n in a.only.split(",")]
    design = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    for n in names:
        b, meta, dropped, f0 = fix(n)
        hip = L.hip(n, first(n)[1])[1]
        print(f"{n:8s} {f0.shape[1]}x{f0.shape[0]} -> {b.shape[1]}x{b.shape[0]}, dropped rows {dropped} "
              f"(hip {hip:.1f}), hip to soles {f0.shape[0] - hip:.1f} -> {b.shape[0] - (hip - (meta['head_at'][1] - first(n)[1]['head_at'][1])):.1f}")
        if a.sheet:
            os.makedirs(lp(a.sheet), exist_ok=True)
            z = 5
            tiles = [design, f0, b]
            Hm = max(t.shape[0] for t in tiles)
            W = sum(t.shape[1] * z + 12 for t in tiles)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for label, t in zip(("design", "first", "fixed"), tiles):
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{label} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            sheet.convert("RGB").save(lp(os.path.join(a.sheet, f"legfix_{n}.png")))
            continue
        Image.fromarray(b).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump(meta, f)


if __name__ == "__main__":
    main()

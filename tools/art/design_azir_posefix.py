#!/usr/bin/env python3
"""Azir's read-back poses fixed by me (the user, 2026-10-23: 「有问题的地方你直接修复」 - no Codex round).

    python tools/art/design_azir_posefix.py --sheet DIR     # every fixed pose: the design, the first readback, the fix (5x)
    python tools/art/design_azir_posefix.py                 # writes hd/pose_<name>.png (+ .json: head_at, ground)

The runs' passing frames (run2, run4: one leg straight under him, the other knee lifted) came back 2-3 rows taller from
the crest to the standing sole than the contact frames (run1, run3: 55 rows; run2 58, run4 57), so the head bobbed 3-4
rows (2.5 game px) in the cycle. Whole rows go from the legs' zone only - from DROP_FROM rows under the hip (the robe, the
magenta cloth's tip and the gems above it stay) to BOOT rows over the soles (the greaves' feet stay whole) - DROP[name]
of them, the cheapest first (the row most like a neighbour), each choice made again on what is left; the outline closed
after (design_aurora_legfix.py's way). Everything over the zone keeps its squares and place, so the json's head box
stays; the ground row is the new lowest row.
The first readbacks stay in hd_first/ (design_azir_poses.py writes hd/ again from Codex's pictures).
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
import design_azir_poses as DP  # noqa: E402  finish
import pack_azir_poses as PK  # noqa: E402
from design_azir_hd import lp  # noqa: E402
from design_aurora_legfix import row_cost  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "azir")
OUT = os.path.join(SRC, "hd")
FIRST = os.path.join(SRC, "hd_first")
HIP = int(PK.REST["spine"][0][1]) - PK.HEAD[0]   # the hip's row under the head box's top (the design: 58 - 16 = 42)
DROP_FROM = 2                    # rows under the hip where the zone starts
BOOT = 7                         # rows over the soles kept whole: the greaves' feet (the design's ankle to sole)
DROP = {"run2": 2, "run4": 2}


def first(name):
    path = os.path.join(FIRST, f"pose_{name}.png")
    with open(lp(path[:-4] + ".json"), encoding="utf-8") as f:
        meta = json.load(f)
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy(), meta


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


def fix(name):
    a, meta = first(name)
    top = meta["head_at"][1] + HIP + DROP_FROM
    b, dropped = shorten(a, top, DROP[name])
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
        print(f"{n:8s} {f0.shape[1]}x{f0.shape[0]} -> {b.shape[1]}x{b.shape[0]}, dropped rows {dropped}, "
              f"crest to soles {f0.shape[0] - first(n)[1]['head_at'][1]} -> {b.shape[0] - meta['head_at'][1]}")
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
            sheet.convert("RGB").save(lp(os.path.join(a.sheet, f"posefix_{n}.png")))
            continue
        Image.fromarray(b).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump(meta, f)


if __name__ == "__main__":
    main()

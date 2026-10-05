#!/usr/bin/env python3
"""Make effect strips bigger by whole rows and columns, about each cell's anchor (no resampling, no new colours).

    python tools/art/fx_scale.py --hero aatrox --fx q1_body q2_body --factor 1.2 [--x 1.2 --y 1.0] [--dry]

For an effect whose Codex original is gone (the importer's --raw needs it): each cell of
assets/source/<hero>/<hero>_fx_<name>.png (8x blocks, the cells and anchors in <hero>_fx_anchors.json) is redrawn
`factor` times as big - every new square takes the square it falls on, counted out from the anchor, so the anchor
square stays where it was and a shape symmetric about its anchor row (a projectile's) stays symmetric; at 1.2 every
fifth row and column comes out doubled. The anchors file gets the new cell size and anchor. Then run the hero's
importer without --raw to rebuild the sheets. Made for 2026-10-05, the user: 「瑟提的W和剑魔的三段Q特效适当加长或者
加宽一点」 (Aatrox's drafts were no longer on disk).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
Z = 8


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def axis(n_half, f):
    """New half-size and, for each new index, the old index (both counted from the anchor at n_half)."""
    m = int(math.floor(n_half * f + 0.5))
    src = [n_half + int(math.floor((i - m) / f + 0.5)) if i >= m else n_half - int(math.floor((m - i) / f + 0.5))
           for i in range(2 * m + 1)]
    return m, [min(max(s, 0), 2 * n_half) for s in src]


def scale(path, info, fx, fy):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    g = b[:, 0, :, 0]
    tw, th = info["cell"]
    L, U = info["anchor"]
    n = info["frames"]
    # the anchor is the cell's middle in these strips (2L+1 wide, 2U+1 tall); otherwise pad the cell to make it so
    if tw != 2 * L + 1 or th != 2 * U + 1:
        sys.exit(f"{path}: anchor {L},{U} is not the middle of its {tw}x{th} cells")
    L2, xs = axis(L, fx)
    U2, ys = axis(U, fy)
    out = np.zeros((2 * U2 + 1, (2 * L2 + 1) * n, 4), np.uint8)
    for k in range(n):
        cell = g[:, k * tw:(k + 1) * tw]
        out[:, k * (2 * L2 + 1):(k + 1) * (2 * L2 + 1)] = cell[np.ix_(ys, xs)]
    return out, {**info, "cell": [2 * L2 + 1, 2 * U2 + 1], "anchor": [L2, U2]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--fx", nargs="+", required=True)
    ap.add_argument("--factor", type=float, default=1.2)
    ap.add_argument("--x", type=float, help="the width's factor (default --factor)")
    ap.add_argument("--y", type=float, help="the height's factor (default --factor)")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    src = os.path.join(ROOT, "assets", "source", a.hero)
    apath = os.path.join(src, f"{a.hero}_fx_anchors.json")
    with open(lp(apath), encoding="utf-8") as f:
        anchors = json.load(f)
    fx, fy = a.x or a.factor, a.y or a.factor
    for name in a.fx:
        path = os.path.join(src, f"{a.hero}_fx_{name}.png")
        out, info = scale(path, anchors[name], fx, fy)
        print(f"{a.hero}_fx_{name}.png  {anchors[name]['cell']} -> {info['cell']}, anchor {anchors[name]['anchor']} -> "
              f"{info['anchor']}")
        if not a.dry:
            Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(lp(path))
            anchors[name] = info
    if not a.dry:
        text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
        with open(lp(apath), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


if __name__ == "__main__":
    main()

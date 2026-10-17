#!/usr/bin/env python3
"""Import Master Yi's effects (assets/source/masteryi/PROMPTS.md, 1-9) as game sheets.

    python tools/art/import_masteryi.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_masteryi.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's nine strips came
back as raw image-generator output, like Leona's and Jinx's: soft alpha, antialiased colours, canvases of
other sizes than asked (1983x793, 2172x724, and 1774x887 for the Highlander aura, whose cells came out
tall instead of 2:1). --raw cuts each strip at its widest empty column runs (import_jinx.split), or into
equal cells where two drawings touch (Alpha Strike's burst and the frame after it), turns every frame into
a cell of a native strip (equal cells, every game pixel one flat 8x8 block, binary alpha, 16 colours by
median cut, each game pixel the majority colour of the source pixels it covers, opaque when a third of them
are) and writes assets/source/masteryi/masteryi_fx_<name>.png at a scale set by the kit and his body (1000
distance units a pixel; he stands 34 px from the helmet's crown to the soles): the slash 20 px, the Double
Strike's X 24 px, the Wuju spark 16 px, Alpha Strike's X burst 34 px, the vanish 30 px; the aura, the
meditation and the Highlander burst at the size of his body - the empty person Codex drew around is his
height - and the Highlander's ground ring 22 px, round his feet.
Each frame sits in its cell on an anchor: hits and the vanish on their middle, or on the middle of the whole
strip; Alpha Strike's X on its crossing (source row 355) and the loops (Wuju, Highlander) on their equal
cell's centre, so nothing jitters from frame to frame; the Wuju wisps on their lowest row (512: his knees),
the lotus and the Highlander ring on the ground line Codex drew them on, the Highlander burst on the empty
figure's soles.

The second step places every cell's centre: the hits and the vanish on the target's (or his) chest; the
Wuju wisps' lowest row 9 px above his soles; the lotus, the burst's soles and the Highlander ring on the
unit's feet. Views are drawn at the unit's pivot, 11 px above the feet line. No palette or outline pass on
the sheets.
Writes league/effects/league_masteryi_fx (hit, ds_hit, e_hit, q_hit, q_vanish, wuju) and
league/effects/league_masteryi_big (w_aura, r_cast, highlander).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from import_jinx import split  # noqa: E402
from import_leona import palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "masteryi")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
KNEES = (0, 2)                        # 9 px above his soles

# raw strip -> native: name: (frames, game px per source px, x anchor, y anchor, cuts)
#   x: "mid" each drawing's middle, "cell" the middle of its equal share of the strip
#   y: "mid" each drawing's middle, "strip" the middle of all the strip's drawings, or a source row
#   cuts: None (the widest empty column runs) or "equal"
RAW = {
    "hit": (5, 20 / 316, "mid", "strip", None),
    "ds_hit": (5, 24 / 287, "mid", "strip", None),
    "e_hit": (5, 16 / 257, "mid", "strip", None),
    "q_hit": (6, 34 / 362, "cell", 355, "equal"),              # row 355: the X's crossing
    "q_vanish": (6, 30 / 363, "mid", "strip", None),
    "wuju": (10, 31 / 319, "cell", 512, None),                 # row 512: the wisps' lowest row
    "w_aura": (8, 0.11, "cell", 490, None),                    # row 490: the lotus's middle
    "r_cast": (6, 34 / 360, "mid", 540, None),                 # row 540: the empty figure's soles
    "highlander": (10, 22 / 110, "cell", 488, None),           # row 488: the ring's middle, 110 wide
}


def from_raw(folder):
    for name, (n, s, xr, yr, cuts) in RAW.items():
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"masteryi_fx_{name}.png"))).convert("RGBA"))
        H, W = a.shape[:2]
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        cols = [(round(i * W / n), round((i + 1) * W / n)) for i in range(n)] if cuts == "equal" else split(a, n, cuts)
        boxes, anchors = [], []
        rows_all = np.nonzero(solid.any(1))[0]
        for k, (x0, x1) in enumerate(cols):
            ys, xs = np.nonzero(solid[:, x0:x1])
            xs = xs + x0
            box = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1)
            ax = (k + 0.5) * W / n if xr == "cell" else (box[0] + box[1]) / 2
            if yr == "mid":
                ay = (box[2] + box[3]) / 2
            elif yr == "strip":
                ay = (rows_all.min() + rows_all.max() + 1) / 2
            else:
                ay = yr
            boxes.append(box)
            anchors.append((ax, ay))
        # a cell symmetric round its anchor, big enough for every frame
        hw = max(max(ax - b[0], b[1] - ax) for b, (ax, _) in zip(boxes, anchors))
        hh = max(max(ay - b[2], b[3] - ay) for b, (_, ay) in zip(boxes, anchors))
        L, U = math.ceil(hw * s) + 1, math.ceil(hh * s) + 1
        tw, th = 2 * L, 2 * U
        out = np.zeros((th, tw * n, 4), np.uint8)
        for k, ((x0, x1), (ax, ay)) in enumerate(zip(cols, anchors)):
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U) / s))
                sy1 = max(int(math.floor(ay + (r + 1 - U) / s)), sy0 + 1)
                if sy1 <= 0 or sy0 >= H:
                    continue
                sy0, sy1 = max(0, sy0), min(H, sy1)
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L) / s))
                    sx1 = max(int(math.floor(ax + (c + 1 - L) / s)), sx0 + 1)
                    sx0, sx1 = max(x0, sx0), min(x1, sx1)            # this drawing's columns only
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"masteryi_fx_{name}.png")))
        print(f"masteryi_fx_{name}.png  {n} cells of {tw}x{th}, {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"masteryi_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"masteryi_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# the cell's anchor goes to `spot`: the anchor sits at the cell's centre (from_raw makes the cell symmetric)
# sprite: {tag: (frames, spot of the cell's centre from the pivot, ms per frame)}
FX = {
    "league_masteryi_fx": {
        "hit": (5, CHEST, [50] * 5),
        "ds_hit": (5, CHEST, [50] * 5),
        "e_hit": (5, CHEST, [50] * 5),
        "q_hit": (6, CHEST, [40] * 6),                  # a strike every 0.2 s
        "q_vanish": (6, CHEST, [60] * 6),
        "wuju": (10, KNEES, [100] * 10),                # replayed every second for 5 s
    },
    "league_masteryi_big": {
        "w_aura": (8, FEET, [100] * 8),                 # the 0.75 s meditation, the lotus closing as he stands
        "r_cast": (6, FEET, [70] * 6),
        "highlander": (10, FEET, [100] * 10),           # replayed every second for 7 s, behind him
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (n, (sx, sy), ms) in tags.items():
            frames = []
            for f, m in zip(cells(tag, n), ms):
                u0, r0 = sx - f.shape[1] // 2, sy - f.shape[0] // 2
                frames.append((G.centre_frame(f, u0, r0), m))
            out[tag] = frames
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

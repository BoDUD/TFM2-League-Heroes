#!/usr/bin/env python3
"""Import Leona's effects (assets/source/leona/PROMPTS.md, 1-10) as game sheets.

    python tools/art/import_leona.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_leona.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's ten strips came
back as raw image-generator output, like Jinx's: soft alpha, antialiased colours, canvases of other sizes
than asked (2172x724, 1983x793, 1586x992, 2097x750). --raw cuts each strip at its widest empty column
runs (import_jinx.split; the Eclipse burst, whose flaming rings nearly touch, at columns written below),
turns every frame into a cell of a native strip (equal cells, every game pixel one flat 8x8 block,
binary alpha, 16 colours by median cut, each game pixel the majority colour of the source pixels it
covers, opaque when a third of them are) and writes assets/source/leona/leona_fx_<name>.png, at a scale
set by the kit (1000 distance units a pixel): the sword slash 20 px, the shield's sunburst 22 px, the
Zenith Blade 28 px long (radius 7000), its hit 22 px, the root's sun sigil 26 px, the Sunlight mark 12 px,
the Eclipse shell 45 px from its ground ring to its top (over her crown, 30 px above her pivot), the Eclipse burst's ring 70 px (radius 35000) and the Solar
Flare's outer ring 72 px (radius 36000) - both drawn at half that and enlarged 2x - and the stun stars
16 px. Each frame sits in its cell on an anchor: the blade on its point; hits on their middle; the root,
the Eclipse shell, the burst and the flare on the ground line Codex drew them on; the stars on the whole
strip's middle. The shield bash's three star frames move up 10 px, from the chest to the top of the head.

The second step anchors every cell on its centre: the slash, the bash and the blade's hit on the target's
chest; the blade flies with its point on the projectile; the root, the shell, the burst and the flare
with their ground ring under the unit's feet; the Sunlight mark over the head; the stun stars round the
top of the head, under the Sunlight mark (listed twice: 1.75 s). Views are drawn at the unit's pivot, 11 px above the feet line. No palette
or outline pass on the sheets.
Writes league/effects/league_leona_fx (hit, q_hit, e_blade, e_hit, e_root, sunlight, eclipse, r_stun)
and league/effects/league_leona_big (w_burst, r_flare).
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

SRC = os.path.join(ROOT, "assets", "source", "leona")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
OVERHEAD = (0, -30)                   # above a hero's head (most reach 21-24 px above the pivot)
HEAD = (0, -16)                       # the stun stars: on a 34 px hero's head top

# raw strip -> native: name: (frames, game px per source px, x anchor, y anchor, cuts, {frame: game px up})
#   x: "nose" the drawing's right edge, "mid" its middle
#   y: "mid" each drawing's middle, "strip" the middle of all the strip's drawings, or a source row
RAW = {
    "hit": (5, 20 / 331, "mid", "strip", None, {}),
    "q_hit": (6, 22 / 393, "mid", "strip", None, {3: 10, 4: 10, 5: 10}),
    "e_blade": (4, 28 / 373, "nose", "strip", None, {}),
    "e_hit": (5, 22 / 423, "mid", "strip", None, {}),
    "e_root": (6, 26 / 311, "mid", 489, None, {}),              # row 489: the ring's middle
    "sunlight": (6, 12 / 293, "mid", "mid", None, {}),
    "eclipse": (8, 45 / 317, "mid", 490, None, {}),             # row 490: its ground ring's middle, 317 below the top
    "w_burst": (7, 35 / 366, "mid", 450, [232, 514, 842, 1240, 1566, 1878], {}),   # ring 70 px at 2x, row 450
    "r_flare": (12, 36 / 160, "mid", 476, None, {}),           # ring 72 px at 2x, row 476
    "r_stun": (8, 16 / 175, "mid", "strip", None, {}),
}


def palette(a, n=16):
    """The median-cut palette of a strip's solid pixels."""
    px = a[..., :3][a[..., 3] >= 100]
    q = Image.fromarray(px.reshape(-1, 1, 3)).quantize(n, method=Image.MEDIANCUT)
    return np.array(q.getpalette()[:3 * n], float).reshape(n, 3)


def from_raw(folder):
    for name, (n, s, xr, yr, cuts, up) in RAW.items():
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"leona_fx_{name}.png"))).convert("RGBA"))
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        cols = split(a, n, cuts)
        boxes, anchors = [], []
        rows_all = np.nonzero(solid.any(1))[0]
        for k, (x0, x1) in enumerate(cols):
            ys, xs = np.nonzero(solid[:, x0:x1])
            xs = xs + x0
            box = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1)
            ax = box[1] if xr == "nose" else (box[0] + box[1]) / 2
            if yr == "mid":
                ay = (box[2] + box[3]) / 2
            elif yr == "strip":
                ay = (rows_all.min() + rows_all.max() + 1) / 2
            else:
                ay = yr
            ay += up.get(k, 0) / s                     # a larger source row under the anchor: drawn higher
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
                if sy1 <= 0 or sy0 >= a.shape[0]:
                    continue
                sy0, sy1 = max(0, sy0), min(a.shape[0], sy1)
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
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"leona_fx_{name}.png")))
        print(f"leona_fx_{name}.png  {n} cells of {tw}x{th}, {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"leona_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"leona_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (frames, enlarge, spot of the cell's centre from the pivot, ms per frame, times played)}
FX = {
    "league_leona_fx": {
        "hit": (5, 1, CHEST, [50] * 5, 1),
        "q_hit": (6, 1, CHEST, [60, 60, 80, 100, 180, 180], 1),
        "e_blade": (4, 1, (0, 0), [50] * 4, 1),
        "e_hit": (5, 1, CHEST, [60] * 5, 1),
        "e_root": (6, 1, FEET, [85] * 6, 1),                  # the root: 0.5 s
        "sunlight": (6, 1, OVERHEAD, [100] * 6, 1),            # a buff view: loops while the mark lasts
        "eclipse": (8, 1, FEET, [100] * 8, 1),                 # a buff view: loops for 3 s
        "r_stun": (8, 1, HEAD, [110] * 8, 2),                  # the stun: 1.75 s
    },
    "league_leona_big": {
        "w_burst": (7, 2, FEET, [70] * 7, 1),
        "r_flare": (12, 2, FEET, [100] * 6 + [50] + [70] * 5, 1),   # the beam on frame 7, at 0.6 s; a ViewEffect on the cast point (a zone view turns: upside down cast leftward)
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (n, k, (sx, sy), ms, times) in tags.items():
            frames = []
            for f, m in list(zip(cells(tag, n), ms)) * times:
                if k > 1:
                    f = np.kron(f, np.ones((k, k, 1), np.uint8))
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

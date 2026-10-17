#!/usr/bin/env python3
"""Import Jinx's effects (assets/source/jinx/PROMPTS.md, 1-15) as game sheets.

    python tools/art/import_jinx.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_jinx.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's fifteen
strips came back as raw image-generator output, like Yasuo's and Amumu's: soft alpha, antialiased
colours, canvases of other sizes than asked (2172x724, 1983x793, 1774x887, 2079x756) and, this time,
frames that are not evenly spaced (the rocket blast's six stages sit at uneven distances). --raw cuts
each strip at the widest empty columns between its drawings (the trap fizzle and Get Excited!, whose
own drawings have wide gaps, at columns written below), and turns every frame into a cell of a native
strip (equal cells, every game pixel one flat 8x8 block, binary alpha) written to
assets/source/jinx/jinx_fx_<name>.png: the strip's colours cut to 16 by median cut (the rockets 20, the chompers 20 shared by their five strips), every game pixel the
majority colour of the source pixels it covers (opaque when a third of them are), at a scale set by the
kit (1000 distance units a pixel): the minigun burst 14 px long, its sparks 18 px, the Fishbones rocket 24 px, its blast
about 37 px across (splash radius 20000), the zap 30 px (radius 15000), the thrown chompers 18 px, the
row of three traps 32 px (radius 15000; each strip scaled to that width, as Codex drew the arm, trap
and fizzle rows at 589, 635 and 504 px), the Super Mega Death Rocket 59 px (radius 28000) and its blast
about 97 px across (radius 62000, drawn at 0.2 and enlarged 2x). Each frame sits in its cell on an
anchor: flying things on their nose (so frames do not jitter and the nose meets the target), the
tumbling chompers and hits on their middle, the traps and the bite on the ground line Codex drew them
on, Get Excited! on its ring (its speed streaks left out of the measure). The rockets keep the first
frame's body in every frame, only the flame moving (Codex's bodies wobbled).

The second step anchors every cell on its centre: bullets, rockets and the zap fly with their nose on
the projectile; the minigun sparks on the target's chest, the rocket blast on its body; the zapper's
charge at Jinx's muzzle in the W animation (13, -8), mirrored with her; the zap's lightning with its
slow ring under the target's feet; traps and the bite with their bottom row on the sole row; the big
blast's ring on the ground; Get Excited! round her body. Views are drawn at the unit's pivot, 11 px
above the feet line. No palette or outline pass on the sheets.
Writes league/effects/league_jinx_fx (bullets, minigun_hit, rocket, rocket_hit, w_charge, zap,
zap_hit, e_throw, e_arm, e_trap, e_bite, e_fizzle, excited) and league/effects/league_jinx_big
(r_rocket, r_blast).
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
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jinx")
MOD = os.path.join(ROOT, "league")
Z = 8
SOLE = (0, 12)                        # a cell anchored on its bottom edge: the bottom row on the sole row
FEET = (0, 11)
CHEST = (0, -4)
BODY = (0, -6)                        # the middle of a 34 px hero
MUZZLE = (13, -8)                     # the zapper's muzzle in her W (skill) frames 4-6

# raw strip -> native: name: (frames, game px per source px, x anchor, y anchor, cuts)
#   x: "nose" the drawing's right edge, "mid" its middle, "base" the middle of its bottom fifth,
#      (y0, y1) the middle of what lies in those source rows
#   y: "mid" each drawing's middle, "strip" the middle of all the strip's drawings, or a source row
RAW = {
    "bullets": (4, 0.045, "nose", "strip", None),
    "minigun_hit": (5, 0.055, "mid", "strip", None),
    "rocket": (4, 0.05, "nose", "strip", None),
    "rocket_hit": (6, 0.09, "mid", "strip", None),
    "w_charge": (5, 0.04, "mid", "strip", None),
    "zap": (4, 0.06, "nose", "strip", None),
    "zap_hit": (6, 0.085, "mid", 540, None),                 # row 540: the slow ring's middle
    "e_throw": (4, 0.044, "mid", "mid", None),
    "e_arm": (3, 32 / 589, "mid", 471, None),                # rows 471 / 494 / 473: the ground line
    "e_trap": (3, 32 / 635, "mid", 494, None),
    "e_bite": (8, 0.054, "base", 657, None),
    "e_fizzle": (4, 32 / 504, "mid", 473, [575, 1109, 1663]),
    "r_rocket": (4, 0.12, "nose", "strip", None),
    "r_blast": (8, 0.2, "mid", 505, None),                   # row 505: the ground ring's middle
    "excited": (8, 0.12, (180, 470), 347, [245, 554, 811, 1086, 1356, 1630, 1918]),
}
LOCK = {"rocket": 0.75, "r_rocket": 0.8}     # the right part of the cell (the body) from frame 1
COLOURS = {"rocket": 20, "r_rocket": 20}      # 16 for the rest; the rockets' purples left the flame 2 colours
# strips cut to one palette: the traps play one after another (with 16 colours each, the arming flames
# came out pink and the waiting ones orange)
GROUP = {"e_arm": "trap", "e_trap": "trap", "e_fizzle": "trap", "e_bite": "trap", "e_throw": "trap"}


def palette(folder, name):
    """The median-cut palette of a strip, or of all the strips in its GROUP."""
    names = [k for k, g in GROUP.items() if g == GROUP[name]] if name in GROUP else [name]
    px = []
    for k in names:
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"jinx_fx_{k}.png"))).convert("RGBA"))
        px.append(a[..., :3][a[..., 3] >= 100])
    n = COLOURS.get(name, 20 if name in GROUP else 16)
    q = Image.fromarray(np.concatenate(px).reshape(-1, 1, 3)).quantize(n, method=Image.MEDIANCUT)
    return np.array(q.getpalette()[:3 * n], float).reshape(n, 3)


def split(a, n, cuts=None):
    """Column ranges of the n drawings: cut at the n - 1 widest empty column runs, or at `cuts`."""
    occ = (a[..., 3] >= 100).any(0)
    W = a.shape[1]
    if cuts is None:
        gaps, x = [], 0
        while x < W:
            if occ[x]:
                x += 1
                continue
            s = x
            while x < W and not occ[x]:
                x += 1
            if s > 0 and x < W:
                gaps.append((x - s, (s + x) // 2))
        cuts = sorted(c for _, c in sorted(gaps, reverse=True)[:n - 1])
    edges = [0] + list(cuts) + [W]
    return [(edges[i], edges[i + 1]) for i in range(n)]


def from_raw(folder):
    for name, (n, s, xr, yr, cuts) in RAW.items():
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"jinx_fx_{name}.png"))).convert("RGBA"))
        solid = a[..., 3] >= 100
        pal = palette(folder, name)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        cols = split(a, n, cuts)
        boxes, anchors = [], []
        rows_all = np.nonzero(solid.any(1))[0]
        for x0, x1 in cols:
            ys, xs = np.nonzero(solid[:, x0:x1])
            xs = xs + x0
            box = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1)
            if xr == "nose":
                ax = box[1]
            elif xr == "mid":
                ax = (box[0] + box[1]) / 2
            elif xr == "base":
                low = ys >= box[3] - (box[3] - box[2]) / 5
                ax = (xs[low].min() + xs[low].max() + 1) / 2
            else:
                band = (ys >= xr[0]) & (ys < xr[1])
                ax = (xs[band].min() + xs[band].max() + 1) / 2
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
        if name in LOCK:
            body = int(round(tw * (1 - LOCK[name])))
            for k in range(1, n):
                out[:, k * tw + body:(k + 1) * tw] = out[:, body:tw]
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"jinx_fx_{name}.png")))
        print(f"jinx_fx_{name}.png  {n} cells of {tw}x{th}, {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"jinx_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"jinx_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (frames, enlarge, spot of the cell's centre from the pivot, ms per frame)}
FX = {
    "league_jinx_fx": {
        "bullets": (4, 1, (0, 0), [50] * 4),
        "minigun_hit": (5, 1, CHEST, [50] * 5),
        "rocket": (4, 1, (0, 0), [60] * 4),
        "rocket_hit": (6, 1, BODY, [60] * 6),
        "w_charge": (5, 1, MUZZLE, [80] * 5),
        "zap": (4, 1, (0, 0), [50] * 4),
        "zap_hit": (6, 1, FEET, [60] * 6),
        "e_throw": (4, 1, (0, 0), [60] * 4),
        "e_arm": (3, 1, SOLE, [83] * 3),                 # one trap link: 15 ticks
        "e_trap": (3, 1, SOLE, [83] * 3),
        "e_bite": (8, 1, SOLE, [60, 60, 70, 180, 240, 240, 240, 240]),
        "e_fizzle": (4, 1, SOLE, [70] * 4),
        "excited": (8, 1, BODY, [100] * 8),
    },
    "league_jinx_big": {
        "r_rocket": (4, 1, (0, 0), [60] * 4),
        "r_blast": (8, 2, FEET, [70] * 8),
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (n, k, (sx, sy), ms) in tags.items():
            frames = []
            for f, m in zip(cells(tag, n), ms):
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

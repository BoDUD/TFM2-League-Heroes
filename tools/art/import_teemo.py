#!/usr/bin/env python3
"""Import Teemo's effects (assets/source/teemo/PROMPTS.md, 1-12) as game sheets.

    python tools/art/import_teemo.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_teemo.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's twelve strips came
back as raw image-generator output, like Leona's and Jinx's: soft alpha, antialiased colours, canvases of
other sizes than asked (2172x724, 1983x793, 1774x887) and frames not evenly spaced (the mushroom burst most
of all). The delivery's manifest.json gives every frame's columns (found at the transparent gaps and
checked by eye); without it the strip is cut at its widest empty column runs (import_jinx.split). --raw
turns every frame into a cell of a native strip (equal cells, every game pixel one flat 8x8 block, binary
alpha, 16 colours by median cut, each game pixel the majority colour of the source pixels it covers,
opaque when a third of them are) and writes assets/source/teemo/teemo_fx_<name>.png, one scale per strip
so the frames keep their sizes against each other, set by the kit (1000 distance units a pixel): the
dart 16 px long with its trail, its hit 18 px, the blinding dart 20 px, its splash 24 px, the blind's
smoke 16 px, the dash dust 30 px, the camouflage whirl 30 px tall, the poison 20 px, the thrown mushroom
12 px, the mushroom set on the ground 14 px wide (the hidden one, drawn 1.7 times bigger, as wide as the
last frame of the setting), and the burst's ground mist 60 px (radius 30000; drawn at half that and
enlarged 2x). Each frame sits in its cell on an anchor: the darts on their point; hits, the smoke band
and the tumbling mushroom on their middle; the dust, the whirl, the poison and the mushrooms on the
ground line Codex drew them on (the dust's right edge in front of the feet, so it trails behind him);
the burst on its mist ring's middle row.

The second step anchors every cell on its centre: the dart's hit on the chest; the blinding splash and
the smoke band on the head; the darts fly with their point on the projectile and the mushroom tumbles
round it; the dust, the whirl, the poison and the mushroom's setting, waiting and burst with their
ground line under the feet (a view played at a spot is drawn like one on a unit, 11 px above the
ground). The smoke band is listed twice (1.5 s of blind). No palette or outline pass on the sheets.
Writes league/effects/league_teemo_fx (dart, hit, q_dart, q_hit, blind, w_cast, stealth, poisoned) and
league/effects/league_teemo_big (r_throw, r_arm, r_trap, r_burst).
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from import_jinx import split  # noqa: E402
from import_leona import palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "teemo")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
EYES = (0, -15)                       # a 34 px hero's eye row, 26 px above the ground

# raw strip -> native: name: (frames, game px per source px, x anchor, y anchor)
#   x: "nose" the drawing's right edge, "mid" its middle, ("nose", dx) the right edge dx game px right of the anchor
#   y: "mid" each drawing's middle, "strip" the middle of all the strip's drawings, or a source row
RAW = {
    "dart": (3, 16 / 592, "nose", "strip"),
    "hit": (5, 18 / 438, "mid", "strip"),
    "q_dart": (4, 20 / 500, "nose", "strip"),
    "q_hit": (5, 24 / 368, "mid", "strip"),
    "blind": (6, 16 / 295, "mid", "strip"),
    "w_cast": (5, 30 / 380, ("nose", 4), 503),          # row 503: the ground under every puff
    "stealth": (6, 30 / 362, "mid", 525),               # row 525: the ring of leaves round the feet
    "poisoned": (6, 20 / 250, "mid", 548),              # row 548: where the wisps leave the ground
    "r_throw": (4, 12 / 416, "mid", "mid"),
    "r_arm": (6, 14 / 269, "mid", 546),                 # row 546: the ground; 14 px: the settled mushroom
    "r_trap": (2, 306 * 14 / 269 / 527, "mid", 656),    # as wide as r_arm's last frame (306 source px there)
    "r_burst": (8, 30 / 466, "mid", 464),               # the mist ring 60 px at 2x; row 464: its middle
}


def regions(folder, name, a, n):
    """Each frame's source columns: the delivery's manifest when it has them, else the widest gaps."""
    path = os.path.join(folder, "manifest.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for e in json.load(f)["files"]:
                if e["filename"] == f"teemo_fx_{name}.png" and len(e.get("source_regions_full_height", [])) == n:
                    return [(r[0], r[2]) for r in e["source_regions_full_height"]]
    return split(a, n, None)


def from_raw(folder):
    for name, (n, s, xr, yr) in RAW.items():
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"teemo_fx_{name}.png"))).convert("RGBA"))
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        cols = regions(folder, name, a, n)
        boxes, anchors = [], []
        rows_all = np.nonzero(solid.any(1))[0]
        for (x0, x1) in cols:
            ys, xs = np.nonzero(solid[:, x0:x1])
            xs = xs + x0
            box = (xs.min(), xs.max() + 1, ys.min(), ys.max() + 1)
            if isinstance(xr, tuple):
                ax = box[1] - xr[1] / s
            else:
                ax = box[1] if xr == "nose" else (box[0] + box[1]) / 2
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
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"teemo_fx_{name}.png")))
        print(f"teemo_fx_{name}.png  {n} cells of {tw}x{th}, {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"teemo_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"teemo_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (frames, enlarge, spot of the cell's centre from the pivot, ms per frame, times played)}
FX = {
    "league_teemo_fx": {
        "dart": (3, 1, (0, 0), [50] * 3, 1),
        "hit": (5, 1, CHEST, [50] * 5, 1),
        "q_dart": (4, 1, (0, 0), [50] * 4, 1),
        "q_hit": (5, 1, EYES, [60] * 5, 1),
        "blind": (6, 1, EYES, [125] * 6, 2),                  # the blind: 1.5 s
        "w_cast": (5, 1, FEET, [70] * 5, 1),
        "stealth": (6, 1, FEET, [80] * 6, 1),
        "poisoned": (6, 1, FEET, [100] * 6, 1),
    },
    "league_teemo_big": {
        "r_throw": (4, 1, (0, 0), [80] * 4, 1),
        "r_arm": (6, 1, FEET, [80, 80, 120, 120, 300, 300], 1),    # arming: 1 s
        "r_trap": (2, 1, FEET, [125] * 2, 1),                       # one link of the waiting chain: 15 ticks
        "r_burst": (8, 2, FEET, [120] * 8, 1),
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

#!/usr/bin/env python3
"""Import Malphite's effects (assets/source/malphite/PROMPTS.md, 1-10) as game sheets.

    python tools/art/import_malphite.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_malphite.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's ten strips came back as
raw image-generator output, like Miss Fortune's: soft alpha, antialiased colours, 2172x724-sized canvases. Its
manifest.json (schema malphite-vfx-raw-handoff-v1) gives every frame's rectangle in the source
(`assets[].frames[].rect`, [x, y, width, height]; the frames are not all equally wide) and the drawing's box in
it (`content_bbox_local`). --raw turns every frame into a cell of a native strip exactly like
import_missfortune.py (every game pixel one flat 8x8 block, binary alpha, 16 colours by median cut, each game
pixel the majority colour of the source pixels it covers, opaque when a third of them are) and writes
assets/source/malphite/malphite_fx_<name>.png plus malphite_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings, not typed in:
the widest drawing of a strip becomes the hit 14 px, Thunderclap's burst 26 px, the flying shard with its dust
trail 16 px, its shatter 22 px, Ground Slam's jolt under a foe 14 px, the slam's ring 72 px (radius 36000) and
Unstoppable Force's crater 64 px (radius 30000); the tallest drawing of the knock-up eruption 32 px (a column
as wide as Codex drew it would stand 39 px, over the head of the foe it throws); the Granite Shield ring 50 px
across, round his 43 px body; Thunderclap's two arcs 40 px apart, at his fists. Each frame sits in its cell on an
anchor: the shard on its nose; the hits and bursts on their cell's middle (a frame's own box drifts with loose
sparks); the jolt and the eruption on the ground row they stand on; the rings, the shield and the arcs on the
middle Codex drew them round (the slam's and the crater's ellipse at 60% of the canvas height, as asked).

The second step places every cell by its anchor: the shard flies with its nose on the projectile; the hits on
the body; the jolt, the eruption, the slam's ring and the crater on the ground under the unit (11 px below the
pivot); the shield round his body and the arcs at his fists (both a few px above his pivot: he is 45 px tall).
No palette or outline pass on the sheets. Writes league/effects/league_malphite_fx (hit, w_hit, q_shard,
q_hit, e_hit, r_knockup, granite, thunder) and league/effects/league_malphite_big (e_slam, r_slam).
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
from import_leona import palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "malphite")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
BODY = (0, -6)                         # the middle of a 34 px hero
MALPHITE = (2, -10)                    # the middle of his 45 px body
FISTS = (2, -2)                        # his fists hang either side of his hips

# raw strip -> native: name: (frames, size in game px, measured on "w" (widest drawing) or "h" (tallest),
#                             x anchor, y anchor)
#   x: "nose" the drawing's right edge, "cell" the middle of its rectangle
#   y: "strip" the middle of all the strip's drawings, "ground" the lowest row of its drawings, or a share of
#      the canvas height (the ellipses' middle)
RAW = {
    "hit": (5, 14, "w", "cell", "strip"),
    "w_hit": (6, 26, "w", "cell", "strip"),
    "q_shard": (4, 16, "w", "nose", "strip"),
    "q_hit": (6, 22, "w", "cell", "strip"),
    "e_hit": (4, 14, "w", "cell", "ground"),
    "r_knockup": (6, 32, "h", "cell", "ground"),
    "granite": (8, 50, "w", "cell", "strip"),
    "thunder": (4, 40, "w", "cell", "strip"),
    "e_slam": (7, 72, "w", "cell", 0.6),
    "r_slam": (8, 64, "w", "cell", 0.6),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8") as f:
        return {a["file"]: a for a in json.load(f)["assets"]}


def from_raw(folder):
    manifest = load_manifest(folder)
    anchors = {}
    for name, (n, size, measure, xr, yr) in RAW.items():
        fn = f"malphite_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        frames = manifest[fn]["frames"]
        if len(frames) != n:
            sys.exit(f"{fn}: the manifest lists {len(frames)} frames, not {n}")
        rects = [f["rect"] for f in frames]
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        extent = max((b[1] - b[0]) if measure == "w" else (b[3] - b[2]) for b in boxes)
        s = size / extent
        rows = (min(b[2] for b in boxes), max(b[3] for b in boxes))
        anchor = []
        for (x, y, w, h), box in zip(rects, boxes):
            ax = box[1] if xr == "nose" else x + w / 2
            if yr == "strip":
                ay = (rows[0] + rows[1]) / 2
            elif yr == "ground":
                ay = rows[1] - 1
            else:
                ay = y + yr * h
            anchor.append((ax, ay))
        left = max(ax - b[0] for b, (ax, _) in zip(boxes, anchor))
        right = max(b[1] - ax for b, (ax, _) in zip(boxes, anchor))
        up = max(ay - b[2] for b, (_, ay) in zip(boxes, anchor))
        down = max(b[3] - ay for b, (_, ay) in zip(boxes, anchor))
        L = R = max(math.ceil(left * s), math.ceil(right * s)) + 1
        U = D = max(math.ceil(up * s), math.ceil(down * s)) + 1
        tw, th = L + R, U + D
        out = np.zeros((th, tw * n, 4), np.uint8)
        for k, ((x, y, w, h), (ax, ay)) in enumerate(zip(rects, anchor)):
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U) / s))
                sy1 = max(int(math.floor(ay + (r + 1 - U) / s)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)             # this frame's rows only
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L) / s))
                    sx1 = max(int(math.floor(ax + (c + 1 - L) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)         # and columns
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U]}
        print(f"{fn}  {n} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({size} px over {extent} source px), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "malphite_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"malphite_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"malphite_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (frames, spot of the anchor from the pivot, ms per frame, times played)}
FX = {
    "league_malphite_fx": {
        "hit": (5, CHEST, [50] * 5, 1),
        "w_hit": (6, BODY, [50] * 6, 1),
        "q_shard": (4, (0, 0), [60] * 4, 1),
        "q_hit": (6, BODY, [50] * 6, 1),
        "e_hit": (4, FEET, [60] * 4, 1),
        "r_knockup": (6, FEET, [80] * 6, 1),
        "granite": (8, MALPHITE, [100] * 8, 1),
        "thunder": (4, FISTS, [80] * 4, 1),
    },
    "league_malphite_big": {
        "e_slam": (7, FEET, [60] * 7, 1),
        "r_slam": (8, FEET, [70] * 8, 1),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "malphite_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (n, (sx, sy), ms, times) in tags.items():
            ax, ay = anchors[tag]["anchor"]
            out[tag] = [(G.centre_frame(f, sx - ax, sy - ay), m) for f, m in list(zip(cells(tag, n), ms)) * times]
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

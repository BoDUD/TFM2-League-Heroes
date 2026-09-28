#!/usr/bin/env python3
"""Import Miss Fortune's effects (assets/source/missfortune/PROMPTS.md, 1-12) as game sheets.

    python tools/art/import_missfortune.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_missfortune.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's twelve strips came back
as raw image-generator output, like Annie's: soft alpha, antialiased colours, canvases of other sizes than asked
(2172x724, 1983x793, 1659x948...). Its manifest.json (schema missfortune-vfx-raw-v1) gives every frame's
rectangle in the source (`assets[].frames[].source_rect`, x, y, width, height). Bullet Time's wave came on black
(`"background": "black_fallback"`): its alpha is taken from the brightness. --raw turns every frame into a cell
of a native strip (every game pixel one flat 8x8 block, binary alpha, 16 colours by median cut, each game pixel
the majority colour of the source pixels it covers, opaque when a third of them are) and writes
assets/source/missfortune/missfortune_fx_<name>.png, plus missfortune_fx_anchors.json (each strip's cell and
where its anchor sits in it). One scale per strip, set by the kit (1000 distance units a pixel): the pistol
bullet 12 px long with its trail, the Love Tap bullet 14 px, the hit 14 px, the heart's burst 18 px, Double Up's
bullet 20 px, its hit 22 px, the bounce 24 px, the crit 32 px, Bullet Time's sparks 10 px, Strut's ring 20 px
wide round her feet, Make It Rain's ring 60 px wide (radius 30000; Codex drew it flatter than 2:1). Bullet
Time's wave is squeezed to 100 x 72 px: its seven bullets travel from the muzzle to the end of the 100000-long
rectangle and fan out to +-20 degrees (Codex spread them over 442 source px, the length over 475). Each frame
sits in its cell on an anchor: the bullets on their nose; the hits, the heart and the sparks on their cell's
middle (Codex centred every frame in its cell; a frame's own box drifts with its loose sparks); Strut and the
rain on the ground row Codex drew their ring on; the wave on its muzzle's column in every cell, so the bullets
move forward from frame to frame.

The second step places every cell by its anchor: the bullets fly with their nose on the projectile; the hits,
the heart and the crit on the body; Strut's ring and the rain's ring under the feet (a view played at a spot is
drawn like one on a unit, 11 px above the ground); the wave's muzzle 50 px behind the middle of the rectangle
it is drawn on (a LineRangeProjectile's view is centred on the rectangle and turned to the cast direction). The
rain lists its 1 s loop twice (the zone lasts 2 s; its view repeats). No palette or outline pass on the sheets.
Writes league/effects/league_missfortune_fx (bullet, bullet_lt, hit, lovetap, q_bullet, q_hit, q_bounce,
q_crit, r_hit, strut) and league/effects/league_missfortune_big (e_rain, r_wave).
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

SRC = os.path.join(ROOT, "assets", "source", "missfortune")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
BODY = (0, -6)                         # the middle of a 34 px hero

# raw strip -> native: name: (frames, game px per source px (one, or across and down), x anchor, y anchor)
#   x: "nose" the drawing's right edge, "mid" its middle, "cell" the middle of its rectangle, an int: that column
#      of every cell (the wave's muzzle)
#   y: "strip" the middle of all the strip's drawings, or a source row (the ground ring's middle)
RAW = {
    "bullet": (3, 12 / 565, "nose", "strip"),
    "bullet_lt": (3, 14 / 572, "nose", "strip"),
    "hit": (5, 14 / 316, "cell", "strip"),
    "lovetap": (6, 18 / 287, "cell", "strip"),
    "q_bullet": (3, 20 / 503, "nose", "strip"),
    "q_hit": (6, 22 / 340, "cell", "strip"),
    "q_bounce": (6, 24 / 352, "cell", "strip"),
    "q_crit": (7, 32 / 251, "cell", "strip"),
    "r_hit": (4, 10 / 262, "cell", "strip"),
    "strut": (7, 20 / 167, "cell", 612),                # row 612: the ring's middle round her feet
    "e_rain": (8, 60 / 234, "cell", 443),               # row 443: the ring's middle, at its widest
    "r_wave": (4, (100 / 475, 72 / 442), 18, "strip"),  # column 18: the muzzle flash of frame 1
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8") as f:
        return {a["file"]: a for a in json.load(f)["assets"]}


def rgba(folder, fn, asset):
    a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
    if asset.get("background") == "black_fallback":     # drawn on black: brightness is the alpha
        a[..., 3] = np.clip((a[..., :3].max(-1).astype(int) - 40) * 4, 0, 255)
    return a


def from_raw(folder):
    manifest = load_manifest(folder)
    anchors = {}
    for name, (n, s, xr, yr) in RAW.items():
        sx, sy = s if isinstance(s, tuple) else (s, s)
        fn = f"missfortune_fx_{name}.png"
        a = rgba(folder, fn, manifest[fn])
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        rects = [f["source_rect"] for f in manifest[fn]["frames"]]
        if len(rects) != n:
            sys.exit(f"{fn}: the manifest lists {len(rects)} frames, not {n}")
        boxes, anchor = [], []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        rows = (min(b[2] for b in boxes), max(b[3] for b in boxes))
        for (x, y, w, h), box in zip(rects, boxes):
            if isinstance(xr, int):
                ax = x + xr
            else:
                ax = {"nose": box[1], "mid": (box[0] + box[1]) / 2, "cell": x + w / 2}[xr]
            ay = (rows[0] + rows[1]) / 2 if yr == "strip" else y + yr
            anchor.append((ax, ay))
        # a cell round the anchor, big enough for every frame; the wave's muzzle on its left edge
        left = max(ax - b[0] for b, (ax, _) in zip(boxes, anchor))
        right = max(b[1] - ax for b, (ax, _) in zip(boxes, anchor))
        up = max(ay - b[2] for b, (_, ay) in zip(boxes, anchor))
        down = max(b[3] - ay for b, (_, ay) in zip(boxes, anchor))
        if isinstance(xr, int):
            L, R = max(0, math.ceil(left * sx)), math.ceil(right * sx)
        else:
            L = R = max(math.ceil(left * sx), math.ceil(right * sx)) + 1
        U = D = max(math.ceil(up * sy), math.ceil(down * sy)) + 1
        tw, th = L + R, U + D
        out = np.zeros((th, tw * n, 4), np.uint8)
        for k, ((x, y, w, h), (ax, ay)) in enumerate(zip(rects, anchor)):
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U) / sy))
                sy1 = max(int(math.floor(ay + (r + 1 - U) / sy)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)             # this frame's rows only
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L) / sx))
                    sx1 = max(int(math.floor(ax + (c + 1 - L) / sx)), sx0 + 1)
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
        print(f"{fn}  {n} cells of {tw}x{th}, anchor {L},{U}, {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "missfortune_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"missfortune_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"missfortune_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (frames, spot of the anchor from the pivot, ms per frame, times played)}
FX = {
    "league_missfortune_fx": {
        "bullet": (3, (0, 0), [50] * 3, 1),
        "bullet_lt": (3, (0, 0), [50] * 3, 1),
        "hit": (5, CHEST, [50] * 5, 1),
        "lovetap": (6, BODY, [60] * 6, 1),
        "q_bullet": (3, (0, 0), [40] * 3, 1),
        "q_hit": (6, BODY, [50] * 6, 1),
        "q_bounce": (6, BODY, [50] * 6, 1),
        "q_crit": (7, BODY, [50] * 7, 1),
        "r_hit": (4, CHEST, [50] * 4, 1),
        "strut": (7, FEET, [70] * 7, 1),
    },
    "league_missfortune_big": {
        "e_rain": (8, FEET, [125] * 8, 2),                   # the zone: 2 s, its view repeats
        "r_wave": (4, (-50, 0), [62] * 4, 1),                # the muzzle at the caster, 50 px behind the middle
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "missfortune_fx_anchors.json")), encoding="utf-8") as f:
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

#!/usr/bin/env python3
"""Import Ahri's effects (assets/source/ahri/PROMPTS.md, 1-15) as game sheets.

    python tools/art/import_ahri.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_ahri.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py (her head is drawn and pasted).
Codex's strips come back as raw image-generator output with a manifest.json giving every frame's rectangle
(`assets[].frames[].rect` or `source_rect`, [x, y, width, height] or {x, y, w, h}). --raw turns every frame into a
cell of a native strip the way tools/art/import_thresh.py does (every game pixel one flat 8x8 block, binary alpha,
16 colours by median cut, each game pixel the majority colour of the source pixels it covers, opaque when a third
of them are). What flies (the attack orb, Orb of Deception, the fox-fires, the kiss, the essence bolts) is turned
to its direction by the game, so it is made exactly symmetric about its middle row (the upper half mirrored down);
the kiss's heart was asked for lying on its side, its point forward. Writes assets/source/ahri/ahri_fx_<name>.png
plus ahri_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the attack orb 10 px
with its trail, Orb of Deception 14 px tall (its circle has a radius of 9000: an 18 px path), the fox-fire and the
essence bolt 12 px, the kiss 16 px, the hits 12-16 px, the fires circling her 30 px wide, the hearts over a charmed
champion 14 px, the heal round her body 30 px, the essence motes round her waist 24 px, the dash's cloud 30 px tall.

The second step places every cell by its anchor. Projectiles ride on their projectile with the anchor on the
orb, flame or heart (a few pixels behind the drawing's nose). On the units: the hits on the upper body, the fires
at chest height, the charm's hearts just over the head (their lowest row at the crown of a 35 px hero), the heal
on the body, the essence motes at the waist; the dash's cloud stays where she started, on her pivot.
No palette or outline pass on the sheets. Writes league/effects/league_ahri_fx (orb, hit, q_orb, q_hit, q_true,
w_orbit, w_fire, w_hit, e_kiss, e_charm, r_bolt, r_hit, heal, essence) and league/effects/league_ahri_big (r_dash).
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
from import_thresh import load_manifest, rect, x_anchor, y_anchor  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ahri")
MOD = os.path.join(ROOT, "league")
Z = 8
BODY = (0, -6)                         # the middle of a 34 px hero
HIT = (0, -8)                          # a hit on the upper body
CHEST = (0, -10)                       # the fires circle at chest height
WAIST = (0, -2)                        # the essence motes at her waist
OVERHEAD = (0, -24)                    # the crown of a 35 px hero: the charm's hearts rise from it

# raw strip -> native: name: dict(n frames, size in game px, measure "w" (widest drawing) or "h" (tallest),
#   x anchor, y anchor, mirror) - the anchors as in tools/art/import_thresh.py
RAW = {
    "orb": dict(n=4, size=10, measure="w", x=("nose", -3), y="strip", mirror=True),
    "hit": dict(n=5, size=12, measure="w", x="cell", y="strip"),
    "q_orb": dict(n=6, size=14, measure="h", x=("nose", -7), y="strip", mirror=True),
    "q_hit": dict(n=5, size=16, measure="w", x="cell", y="strip"),
    "q_true": dict(n=5, size=16, measure="w", x="cell", y="strip"),
    "w_orbit": dict(n=8, size=30, measure="w", x="cell", y="strip"),
    "w_fire": dict(n=4, size=12, measure="w", x=("nose", -3), y="strip", mirror=True),
    "w_hit": dict(n=5, size=14, measure="w", x="cell", y="strip"),
    "e_kiss": dict(n=4, size=18, measure="w", x=("nose", -5), y="strip", mirror=True),
    "e_charm": dict(n=10, size=14, measure="w", x="cell", y=("bottom", 0)),
    "r_dash": dict(n=6, size=30, measure="h", x="cell", y="strip"),
    "r_bolt": dict(n=4, size=14, measure="w", x=("nose", -3), y="strip", mirror=True),
    "r_hit": dict(n=5, size=14, measure="w", x="cell", y="strip"),
    "heal": dict(n=6, size=30, measure="w", x="cell", y="strip"),
    "essence": dict(n=6, size=24, measure="w", x="cell", y="strip"),
}


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "ahri_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        n = spec["n"]
        fn = f"ahri_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        if not (a[..., 3] < 255).any():             # delivered on black: alpha from the brightness
            a[..., 3] = np.clip(a[..., :3].max(-1).astype(int) * 3, 0, 255)
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        frames = manifest[fn]["frames"]
        if len(frames) != n:
            sys.exit(f"{fn}: the manifest lists {len(frames)} frames, not {n}")
        rects = [rect(f) for f in frames]
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = (lambda b: b[1] - b[0]) if spec["measure"] == "w" else (lambda b: b[3] - b[2])
        extent = max(ext(b) for b in boxes)
        s = spec["size"] / extent
        rows_rel = (min(b[2] - r[1] for b, r in zip(boxes, rects)), max(b[3] - r[1] for b, r in zip(boxes, rects)))
        anchor = []
        for k, ((x, y, w, h), box) in enumerate(zip(rects, boxes)):
            rows = (y + rows_rel[0], y + rows_rel[1])
            anchor.append((x_anchor(spec["x"], k, rects, boxes, s), y_anchor(spec["y"], k, rects, boxes, rows, s)))
        # the anchor is the middle of pixel (L, U); the cell is 2L+1 x 2U+1
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for b, (ax, _) in zip(boxes, anchor)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for b, (_, ay) in zip(boxes, anchor)) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * n, 4), np.uint8)
        for k, ((x, y, w, h), (ax, ay)) in enumerate(zip(rects, anchor)):
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / s))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / s)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
            cell = out[:, k * tw:(k + 1) * tw]
            if spec.get("mirror"):
                cell[U + 1:] = cell[:U][::-1]
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U]}
        print(f"{fn}  {n} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over {extent} source px), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"ahri_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"ahri_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (strip, its frames used, spot of the anchor from the pivot, ms per frame)}
FX = {
    "league_ahri_fx": {
        "orb": ("orb", range(4), (0, 0), [60] * 4),
        "hit": ("hit", range(5), HIT, [50] * 5),
        "q_orb": ("q_orb", range(6), (0, 0), [60] * 6),
        "q_hit": ("q_hit", range(5), HIT, [50] * 5),
        "q_true": ("q_true", range(5), HIT, [50] * 5),
        "w_orbit": ("w_orbit", range(8), CHEST, [60] * 8),
        "w_fire": ("w_fire", range(4), (0, 0), [60] * 4),
        "w_hit": ("w_hit", range(5), HIT, [50] * 5),
        "e_kiss": ("e_kiss", range(4), (0, 0), [70] * 4),
        # the hearts over the head for the whole 1.25 s charm
        "e_charm": ("e_charm", range(10), OVERHEAD, [125] * 10),
        "r_bolt": ("r_bolt", range(4), (0, 0), [50] * 4),
        "r_hit": ("r_hit", range(5), HIT, [50] * 5),
        "heal": ("heal", range(6), BODY, [70] * 6),
        "essence": ("essence", range(6), WAIST, [100] * 6),
    },
    "league_ahri_big": {
        "r_dash": ("r_dash", range(6), (0, -4), [70] * 6),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "ahri_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (src, used, (sx, sy), ms) in tags.items():
            ax, ay = anchors[src]["anchor"]
            strip = cells(src, RAW[src]["n"])
            out[tag] = [(G.centre_frame(strip[k], sx - ax, sy - ay), m) for k, m in zip(used, ms)]
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--only", nargs="+", help="with --raw: just these strips (e.g. q_orb e_kiss)")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

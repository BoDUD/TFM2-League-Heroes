#!/usr/bin/env python3
"""Import Ezreal's effects (assets/source/ezreal/PROMPTS.md, 1-15) as game sheets.

    python tools/art/import_ezreal.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_ezreal.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's fifteen strips came back
as raw image-generator output on transparent canvases of their own size (1942-2172 px wide), with a manifest.json
(schema ezreal-fx-raw-handoff-v1) that gives every frame's rectangle in the source (`assets[].frames[].source_rect`,
x, y, w, h) and one vertical crop per strip. --raw turns every frame into a cell of a native strip like
import_yone.py (every game pixel one flat 8x8 block, binary alpha, 16 colours by median cut, each game pixel the
majority colour of the source pixels it covers, opaque when a third of them are) and writes
assets/source/ezreal/ezreal_fx_<name>.png plus ezreal_fx_anchors.json (each strip's cell and its anchor in it).
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the attack bolt
12 px long, its hit 14 px, Mystic Shot's bolt 22 px long and its hit 22 px, Essence Flux's orb 16 px tall
(radius 8000), its stick 22 px, the mark 18 px and the detonation 40 px, the homing bolt 16 px long and its hit
20 px, Trueshot Barrage's charge 26 px and its wave 36 px tall (radius 18000), the wave's hit 26 px; the blink's
ground ring 26 px wide (its light columns then stand 38 px, a little over his 34) and the Rising Spell Force
ring 22 px. Anchors: the flying bolts on their nose (each frame's own, so the tip stays put), the orb on its
white core (the ring turns round it), the hits and the charge on their cell's middle row and column (Codex
centred every frame in its cell), the blink and the aura on the middle of their ground ring. The flying
pictures are made exactly symmetric about their middle row (the upper half mirrored down: the game turns a
projectile to its direction and turns it over when it flies left), as the handoff asked.

The second step places every cell by its anchor: the bolts fly with their nose on the projectile, the orb with
its core on it, the wave with its nose 18 px ahead of it (the front of its 18000-radius circle); the hits, the
stick, the mark and the detonation on the body; the blink's and the aura's ring under the feet; the charge on
his gauntlet, 12 px in front of him (a CasterViewEffect is mirrored with the caster when he faces left). Arcane Shift plays the blink forward where he leaves (e_depart) and backward where he lands
(e_arrive). No palette or outline pass on the sheets. Writes league/effects/league_ezreal_fx (bolt, hit, q_bolt,
q_hit, w_orb, w_stick, w_mark, w_boom, e_depart, e_arrive, e_bolt, e_hit, r_hit, rsf_max) and
league/effects/league_ezreal_big (r_charge, r_wave).
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

SRC = os.path.join(ROOT, "assets", "source", "ezreal")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
BODY = (0, -6)                         # the middle of a 34 px hero
FRONT = (12, -8)                       # his gauntlet held out in the R wind-up (a CasterViewEffect is mirrored
                                       # with him when he faces left)

# raw strip -> native: name: dict(n frames, size in game px, measure "w" (widest drawing) or "h" (tallest) or
#   "ring" (the widest row of frame `on`: a ground ring), on: measure one frame (index) instead of all,
#   x anchor, y anchor, mirror)
#   x: "cell" the middle of the frame's rectangle; ("nose", px) the drawing's right edge plus px game pixels;
#      "core" the white core's middle (the strip's median place of it in the rectangles)
#   y: "strip" the middle of all the strip's drawings; "ring" the ring's row; "core" as for x
RAW = {
    "bolt": dict(n=4, size=12, measure="w", x=("nose", 0), y="strip", mirror=True),
    "hit": dict(n=5, size=14, measure="w", x="cell", y="strip"),
    "q_bolt": dict(n=4, size=22, measure="w", x=("nose", 0), y="strip", mirror=True),
    "q_hit": dict(n=6, size=22, measure="w", x="cell", y="strip"),
    "w_orb": dict(n=4, size=16, measure="h", x="core", y="core", mirror=True),
    "w_stick": dict(n=5, size=22, measure="w", x="cell", y="strip"),
    "w_mark": dict(n=4, size=18, measure="w", x="cell", y="strip"),
    "w_boom": dict(n=7, size=40, measure="w", x="cell", y="strip"),
    "e_blink": dict(n=6, size=26, measure="ring", on=0, x="cell", y="ring"),
    "e_bolt": dict(n=4, size=16, measure="w", x=("nose", 0), y="strip", mirror=True),
    "e_hit": dict(n=5, size=20, measure="w", x="cell", y="strip"),
    "r_charge": dict(n=8, size=26, measure="w", x="cell", y="strip"),
    "r_wave": dict(n=4, size=36, measure="h", x=("nose", 0), y="strip", mirror=True),
    "r_hit": dict(n=5, size=26, measure="w", x="cell", y="strip"),
    "rsf": dict(n=6, size=22, measure="ring", on=0, x="cell", y="ring"),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8-sig") as f:
        return {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}


def rect(fr):
    r = fr.get("rect", fr.get("source_rect"))
    if isinstance(r, dict):
        return [int(r["x"]), int(r["y"]), int(r.get("w", r.get("width"))), int(r.get("h", r.get("height")))]
    return [int(v) for v in r]


def ring_row(solid, r):
    """(row, left, right) of the widest row of rectangle r's drawing: the middle of a flat ground ring."""
    x, y, w, h = r
    best = (0, y, x, x)
    for row in range(y, y + h):
        xs = np.nonzero(solid[row, x:x + w])[0]
        if len(xs) and xs[-1] - xs[0] + 1 > best[0]:
            best = (xs[-1] - xs[0] + 1, row, x + xs[0], x + xs[-1] + 1)
    return best[1:]


def core_offset(a, solid, rects):
    """The median place of the white core (the brightest solid pixels) inside the rectangles."""
    lum = a[..., :3].astype(float).mean(-1)
    offs = []
    for x, y, w, h in rects:
        m = solid[y:y + h, x:x + w] & (lum[y:y + h, x:x + w] >= np.percentile(lum[y:y + h, x:x + w][solid[y:y + h, x:x + w]], 95))
        ys, xs = np.nonzero(m)
        offs.append((xs.mean() + 0.5, ys.mean() + 0.5))
    return float(np.median([o[0] for o in offs])), float(np.median([o[1] for o in offs]))


def from_raw(folder):
    manifest = load_manifest(folder)
    anchors = {}
    for name, spec in RAW.items():
        n = spec["n"]
        fn = f"ezreal_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
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
        if spec["measure"] == "ring":
            row, left, right = ring_row(solid, rects[spec["on"]])
            extent = right - left
        else:
            ext = (lambda b: b[1] - b[0]) if spec["measure"] == "w" else (lambda b: b[3] - b[2])
            extent = ext(boxes[spec["on"]]) if "on" in spec else max(ext(b) for b in boxes)
        s = spec["size"] / extent
        rows = (min(b[2] for b in boxes), max(b[3] for b in boxes))
        core = core_offset(a, solid, rects) if "core" in (spec["x"], spec["y"]) else None
        anchor = []
        for k, ((x, y, w, h), box) in enumerate(zip(rects, boxes)):
            if spec["x"] == "cell":
                ax = x + w / 2
            elif spec["x"] == "core":
                ax = x + core[0]
            else:
                ax = box[1] + spec["x"][1] / s
            if spec["y"] == "strip":
                ay = (rows[0] + rows[1]) / 2
            elif spec["y"] == "core":
                ay = y + core[1]
            else:                                           # the ring's row, at the same height in every rectangle
                ay = y + (row - rects[spec["on"]][1]) + 0.5
            anchor.append((ax, ay))
        # the anchor is the middle of pixel (L, U); the cell is 2L+1 x 2U+1
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for b, (ax, _) in zip(boxes, anchor)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for b, (_, ay) in zip(boxes, anchor)) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * n, 4), np.uint8)
        for k, ((x, y, w, h), (ax, ay)) in enumerate(zip(rects, anchor)):
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / s))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / s)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)             # this frame's rows only
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)         # and columns
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
            if spec.get("mirror"):
                cell = out[:, k * tw:(k + 1) * tw]
                cell[U + 1:] = cell[:U][::-1]
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U]}
        print(f"{fn}  {n} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over {extent} source px), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "ezreal_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"ezreal_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"ezreal_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (strip, its frames used, spot of the anchor from the pivot, ms per frame)}
FX = {
    "league_ezreal_fx": {
        "bolt": ("bolt", range(4), (0, 0), [60] * 4),
        "hit": ("hit", range(5), CHEST, [50] * 5),
        "q_bolt": ("q_bolt", range(4), (0, 0), [60] * 4),
        "q_hit": ("q_hit", range(6), BODY, [50] * 6),
        "w_orb": ("w_orb", range(4), (0, 0), [60] * 4),
        "w_stick": ("w_stick", range(5), BODY, [50] * 5),
        "w_mark": ("w_mark", range(4), BODY, [62] * 4),
        "w_boom": ("w_boom", range(7), BODY, [55] * 7),
        "e_depart": ("e_blink", range(6), FEET, [50] * 6),
        "e_arrive": ("e_blink", range(5, -1, -1), FEET, [50] * 6),
        "e_bolt": ("e_bolt", range(4), (0, 0), [60] * 4),
        "e_hit": ("e_hit", range(5), CHEST, [50] * 5),
        "r_hit": ("r_hit", range(5), BODY, [50] * 5),
        "rsf_max": ("rsf", range(6), FEET, [100] * 6),
    },
    "league_ezreal_big": {
        # the charge over his 56-tick wind-up (933 ms), the wave's nose on the front of its circle
        "r_charge": ("r_charge", range(8), FRONT, [117] * 8),
        "r_wave": ("r_wave", range(4), (18, 0), [70] * 4),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "ezreal_fx_anchors.json")), encoding="utf-8") as f:
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
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

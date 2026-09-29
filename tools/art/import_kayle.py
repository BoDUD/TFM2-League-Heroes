#!/usr/bin/env python3
"""Import Kayle's effects (assets/source/kayle/PROMPTS.md, 1-14) as game sheets.

    python tools/art/import_kayle.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_kayle.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's fourteen strips came
back as raw image-generator output on transparent canvases of their own size (1774-2172 px wide) with a
manifest.json giving every frame's rectangle (`assets[].frames[].rect`, [x, y, width, height]; the Q blast's
and the ascent's frames are not equally wide). --raw works like tools/art/import_yone.py: alpha solid from 100
up, 16 colours by median cut, every game pixel the majority colour of the source pixels it covers, opaque when a
third of them are, the anchor in the middle of a game pixel; the four drawings that fly (the bolt, Aflame's wave,
the Q sword, the starfire) are made exactly symmetric about their middle row (the game turns them to their
direction and turns them over when she shoots to the left). Writes assets/source/kayle/kayle_fx_<name>.png plus
kayle_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the hits 14 px,
the starfire's hit 20 px; the bolt 14 px long, the starfire 18, the Q sword with its trail 26; Aflame's wave 20 px
tall (its projectile's radius 10000); the Q and E blasts' rings 40 px (radius 20000) and the falling swords' ring
80 px (radius 40000); the blessing 42 px tall round a small hero, the protection bubble 54 px tall with its shaft,
the ascent's fire wings 46 px across, the Exalted flames 40 px tall round her (Codex drew both narrower than asked).
Anchors: "cell" the middle of the frame's rectangle; ("nose", px) the drawing's right edge plus px game pixels (a
projectile's point: the bolt's and the starfire's core, the wave's front, the sword a third of the way back from
its tip); ("box", k) the vertical middle of frame k's drawing (a ring's centre); ("bottom", k) the bottom of frame
k's drawing (the ground under a unit).
The second step places every cell by its anchor: projectiles on their point, the hits on the body, the rings on
the ground where they burst, the blessing, the protection and the Exalted flames round the unit with their ground
ring under its feet, the ascent round Kayle (she floats 3 px up: her soles 8 px under the pivot, the ground 11).
No palette or outline pass on the sheets. Writes league/effects/league_kayle_fx (bolt, wave, q_sword, e_bolt, hit,
bolt_hit, e_hit, w_heal, exalted) and league/effects/league_kayle_big (q_blast, e_blast, r_blades, ascend,
r_invuln).
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

SRC = os.path.join(ROOT, "assets", "source", "kayle")
MOD = os.path.join(ROOT, "league")
Z = 8
GROUND = (0, 11)                       # the ground under a unit
CHEST = (0, -4)                        # the middle of a 34 px hero
KAYLE = (0, -8)                        # the middle of Kayle, crown (-24) to soles (8)

# raw strip -> native: name: dict(n frames, size in game px, measure "w" (widest drawing) or "h" (tallest),
#   on: measure one frame (index) instead of the widest/tallest of all, x anchor, y anchor, mirror)
RAW = {
    "hit": dict(n=5, size=14, measure="w", x="cell", y="strip"),
    "bolt": dict(n=4, size=14, measure="w", x=("nose", -2), y=0.5, mirror=True),
    "bolt_hit": dict(n=5, size=14, measure="w", x="cell", y="strip"),
    "wave": dict(n=4, size=20, measure="h", x=("nose", -2), y=0.5, mirror=True),
    "q_sword": dict(n=4, size=26, measure="w", x=("nose", -8), y=0.5, mirror=True),
    "q_blast": dict(n=7, size=40, measure="w", x="cell", y=("box", 3)),
    "e_bolt": dict(n=4, size=18, measure="w", x=("nose", -3), y=0.5, mirror=True),
    "e_hit": dict(n=6, size=20, measure="w", on=2, x="cell", y=("box", 2)),
    "e_blast": dict(n=7, size=40, measure="w", x="cell", y=("box", 4)),
    "w_heal": dict(n=8, size=42, measure="h", on=3, x="cell", y=("bottom", 0)),
    "r_invuln": dict(n=6, size=54, measure="h", x="cell", y=("bottom", 0)),
    "r_blades": dict(n=8, size=80, measure="w", on=0, x="cell", y=("box", 0)),
    "ascend": dict(n=10, size=46, measure="w", on=4, x="cell", y=("bottom", 0)),
    "exalted": dict(n=6, size=40, measure="h", x="cell", y=("bottom", 0)),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8-sig") as f:
        return {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}


def rect(fr):
    r = fr.get("rect", fr.get("source_rect"))
    if isinstance(r, dict):
        return [int(r["x"]), int(r["y"]), int(r.get("w", r.get("width"))), int(r.get("h", r.get("height")))]
    return [int(v) for v in r]


def x_anchor(how, k, rects, boxes, s):
    x, y, w, h = rects[k]
    if how == "cell":
        return x + w / 2
    kind, arg = how
    if kind == "nose":
        return boxes[k][1] + arg / s
    raise ValueError(how)


def y_anchor(how, k, rects, boxes, rows):
    x, y, w, h = rects[k]
    if how == "strip":
        return (rows[0] + rows[1]) / 2
    if isinstance(how, float):
        return y + how * h
    kind, arg = how
    if kind == "box":                  # frame `arg`'s drawing's vertical middle, at the same height in every frame
        return rects[k][1] + ((boxes[arg][2] + boxes[arg][3]) / 2 - rects[arg][1])
    if kind == "bottom":               # frame `arg`'s drawing's bottom
        return rects[k][1] + (boxes[arg][3] - rects[arg][1])
    raise ValueError(how)


def from_raw(folder):
    manifest = load_manifest(folder)
    anchors = {}
    for name, spec in RAW.items():
        n = spec["n"]
        fn = f"kayle_fx_{name}.png"
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
        ext = lambda b: (b[1] - b[0]) if spec["measure"] == "w" else (b[3] - b[2])  # noqa: E731
        extent = ext(boxes[spec["on"]]) if "on" in spec else max(ext(b) for b in boxes)
        s = spec["size"] / extent
        rows = (min(b[2] for b in boxes), max(b[3] for b in boxes))
        anchor = [(x_anchor(spec["x"], k, rects, boxes, s), y_anchor(spec["y"], k, rects, boxes, rows)) for k in range(n)]
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
    with open(G.lp(os.path.join(SRC, "kayle_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"kayle_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"kayle_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (strip, its frames used, spot of the anchor from the pivot, ms per frame)}
FX = {
    "league_kayle_fx": {
        "bolt": ("bolt", range(4), (0, 0), [60] * 4),
        "wave": ("wave", range(4), (0, 0), [60] * 4),
        "q_sword": ("q_sword", range(4), (0, 0), [60] * 4),
        "e_bolt": ("e_bolt", range(4), (0, 0), [60] * 4),
        "hit": ("hit", range(5), CHEST, [50] * 5),
        "bolt_hit": ("bolt_hit", range(5), CHEST, [50] * 5),
        "e_hit": ("e_hit", range(6), CHEST, [50] * 6),
        "w_heal": ("w_heal", range(8), GROUND, [80] * 8),
        "exalted": ("exalted", range(6), (0, 8), [100] * 6),
    },
    "league_kayle_big": {
        "q_blast": ("q_blast", range(7), (0, 0), [60] * 7),
        "e_blast": ("e_blast", range(7), (0, 0), [60] * 7),
        "r_blades": ("r_blades", range(8), (0, 0), [70] * 8),
        "ascend": ("ascend", range(10), GROUND, [80] * 10),
        "r_invuln": ("r_invuln", range(6), GROUND, [100] * 6),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "kayle_fx_anchors.json")), encoding="utf-8") as f:
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

#!/usr/bin/env python3
"""Import Yone's effects (assets/source/yone/PROMPTS.md, 1-16) as game sheets.

    python tools/art/import_yone.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_yone.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py (the body he leaves behind in
Soul Unbound is the sprite's own `e_body` tag). Codex's sixteen strips came back as raw image-generator output
on near-black opaque canvases of their own size (1881-2172 px wide), with a manifest.json that gives every
frame's rectangle in the source (`assets[].frames[].rect`, [x, y, width, height]; Mortal Steel's five are not
equally wide). --raw keys the black out (alpha from the brightest channel, solid from 34 up: League's dark ink
#1E1648 stays) and turns every frame into a cell of a native strip like import_ekko.py (every game pixel one
flat 8x8 block, binary alpha, 16 colours by median cut, each game pixel the majority colour of the source
pixels it covers, opaque when a third of them are). Here the anchor is the middle of a game pixel, so the four
drawings that fly or lie along a line (Mortal Steel's thrust, the Gathering Storm gust, Spirit Cleave's fan,
Fate Sealed's slash) are made exactly symmetric about their middle row (the upper half mirrored down; the game
turns them to the cast direction and turns them over when he casts to the left). Writes
assets/source/yone/yone_fx_<name>.png plus yone_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the hits
14-16 px, the thrust's full lance 42 px (its rectangle is 45000 long and the lance starts at his front), the
gust 30 px (its front 22 px ahead of him: it leads him through the dash, its tail streaks over his back), the
knock-up whirlwind 28 px tall, the fan's full sweep 45 px from its apex (the cone's radius), the Soul Unbound
burst 36 px tall, the shield shell 46 px tall round his 39 px (horns to feet), the spirit flames and the storm
round his waist 39 and 36 px wide (their empty middle his width), the mark 16 px, its burst 24 px, the
return's ground ring 30 px, the slash 90 px (its rectangle's length).

The second step places every cell by its anchor. A line's picture is centred on its rectangle and turned to
the cast direction (champion-data "Cone / fan"), so the thrust's tail sits 19 px behind the middle of its
45000 rectangle (3.5 px in front of him), the fan's apex 22 px behind the middle of its 45000 rectangle (at
him) and the slash on the middle of its 90000 one; the gust flies on its projectile, which rides on him
through the dash. On the units: the hits, the mark and its burst on the body; the knock-up's ground ring, the
storm's and the spirit's (drawn with the feet at 90% of their canvas) and the return's ring on the ground
under the unit (11 px below the pivot); the shield round his body; the Soul Unbound burst rising from his
knees. Yone's body is 3 px left of his pivot when he faces right (his katana hangs on the right): the pictures
round his body (q_ready, spirit, shield, e_return, e_cast) sit 2-3 px left, the half of it a buff's picture
keeps if the game does not mirror it when he faces left.
Also writes the mark in three tags for its buff (`e_mark_in` its first three frames, `e_mark` the last three
looped, `e_mark_end` the dimmed last frame): it stays on the enemy until it bursts. No palette or outline pass
on the sheets. Writes league/effects/league_yone_fx (hit, hit2, q_hit, q_ready, knockup, w_hit, shield,
e_cast, spirit, e_mark_in, e_mark, e_mark_end, e_pop, e_return) and league/effects/league_yone_big (q_thrust,
q3_wave, w_cone, r_line).
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

SRC = os.path.join(ROOT, "assets", "source", "yone")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
BODY = (0, -6)                         # the middle of a 34 px hero
YONE = (-3, -8)                        # the middle of his body, horns to feet (-27..11), when he faces right
YONE_FEET = (-2, 11)
KNEES = (-2, 4)                        # Soul Unbound's burst rises from here

# raw strip -> native: name: dict(n frames, size in game px, measure "w" (widest drawing) or "h" (tallest),
#   on: measure one frame (index) instead of the widest/tallest of all, x anchor, y anchor, mirror)
#   x: "cell" the middle of the frame's rectangle; "tail" the drawing's left edge; ("apex", k) frame k's left
#      edge at the same place in every rectangle; ("tip", k) the drawing's right edge less frame k's length (its
#      streaks at the end of a lance); ("nose", px) the drawing's right edge plus px game pixels; a list gives
#      one per frame
#   y: "strip" the middle of all the strip's drawings, or a share of the rectangle's height
RAW = {
    "hit": dict(n=5, size=14, measure="w", x="cell", y="strip"),
    "hit2": dict(n=6, size=16, measure="w", x="cell", y="strip"),
    "q_thrust": dict(n=5, size=42, measure="w", on=2, x=["tail"] * 4 + [("tip", 2)], y=0.49, mirror=True),
    "q_hit": dict(n=5, size=16, measure="w", x="cell", y="strip"),
    "q_ready": dict(n=6, size=36, measure="w", x="cell", y=0.9),
    "q3_wave": dict(n=4, size=30, measure="w", x=("nose", -22), y=0.499, mirror=True),
    "knockup": dict(n=6, size=28, measure="h", x="cell", y=0.925),
    "w_cone": dict(n=6, size=45, measure="w", on=2, x=("apex", 2), y=0.499, mirror=True),
    "w_hit": dict(n=5, size=16, measure="w", x="cell", y="strip"),
    "shield": dict(n=6, size=46, measure="h", x="cell", y=0.5),
    "e_cast": dict(n=6, size=36, measure="h", x="cell", y=0.89),
    "spirit": dict(n=6, size=39, measure="w", x="cell", y=0.9),
    "e_mark": dict(n=6, size=16, measure="w", x="cell", y="strip"),
    "e_pop": dict(n=6, size=24, measure="w", x="cell", y="strip"),
    "e_return": dict(n=6, size=30, measure="w", x="cell", y=0.875),
    "r_line": dict(n=8, size=90, measure="w", x="cell", y=0.485, mirror=True),
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
    if how == "tail":
        return boxes[k][0]
    kind, arg = how
    if kind == "apex":
        return x + (boxes[arg][0] - rects[arg][0])
    if kind == "tip":
        return boxes[k][1] - (boxes[arg][1] - boxes[arg][0])
    if kind == "nose":
        return boxes[k][1] + arg / s
    raise ValueError(how)


def from_raw(folder):
    manifest = load_manifest(folder)
    anchors = {}
    for name, spec in RAW.items():
        n = spec["n"]
        fn = f"yone_fx_{name}.png"
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
        ext = lambda b: (b[1] - b[0]) if spec["measure"] == "w" else (b[3] - b[2])
        extent = ext(boxes[spec["on"]]) if "on" in spec else max(ext(b) for b in boxes)
        s = spec["size"] / extent
        rows = (min(b[2] for b in boxes), max(b[3] for b in boxes))
        xs_how = spec["x"] if isinstance(spec["x"], list) else [spec["x"]] * n
        anchor = []
        for k, ((x, y, w, h), box) in enumerate(zip(rects, boxes)):
            ax = x_anchor(xs_how[k], k, rects, boxes, s)
            ay = (rows[0] + rows[1]) / 2 if spec["y"] == "strip" else y + spec["y"] * h
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
    with open(G.lp(os.path.join(SRC, "yone_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"yone_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"yone_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (strip, its frames used, spot of the anchor from the pivot, ms per frame)}
FX = {
    "league_yone_fx": {
        "hit": ("hit", range(5), CHEST, [50] * 5),
        "hit2": ("hit2", range(6), CHEST, [50] * 6),
        "q_hit": ("q_hit", range(5), CHEST, [50] * 5),
        "q_ready": ("q_ready", range(6), YONE_FEET, [80] * 6),
        "knockup": ("knockup", range(6), FEET, [80] * 6),
        "w_hit": ("w_hit", range(5), CHEST, [50] * 5),
        "shield": ("shield", range(6), YONE, [250] * 6),
        "e_cast": ("e_cast", range(6), KNEES, [60] * 6),
        "spirit": ("spirit", range(6), YONE_FEET, [100] * 6),
        "e_mark_in": ("e_mark", range(3), CHEST, [80] * 3),
        "e_mark": ("e_mark", range(3, 6), CHEST, [120] * 3),
        "e_mark_end": ("e_mark", [5], CHEST, [50]),
        "e_pop": ("e_pop", range(6), BODY, [60] * 6),
        "e_return": ("e_return", range(6), YONE_FEET, [60] * 6),
    },
    "league_yone_big": {
        # the full lance on the hit (tick 8 of the cast), the slash's flash on its hit (tick 15)
        "q_thrust": ("q_thrust", range(5), (-19, 0), [50, 40, 50, 40, 40]),
        "q3_wave": ("q3_wave", range(4), (0, 0), [60] * 4),
        "w_cone": ("w_cone", range(6), (-22, 0), [40] * 6),
        "r_line": ("r_line", range(8), (0, 0), [80, 80, 90, 60, 60, 60, 60, 60]),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "yone_fx_anchors.json")), encoding="utf-8") as f:
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

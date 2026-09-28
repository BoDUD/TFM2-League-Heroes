#!/usr/bin/env python3
"""Import Janna's effects (assets/source/janna/PROMPTS.md, 1-11) as game sheets.

    python tools/art/import_janna.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_janna.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's eleven strips came back
as raw image-generator output like Annie's (soft alpha, canvases of 2172x724 and 1983x793). Its manifest.json
(schema janna-fx-raw-handoff-v1) gives every frame's rectangle in the source as `assets[].frames[].rect`
{x, y, w, h}; the Monsoon blast's six rectangles are uneven, so every strip is cut by them. --raw turns each frame
into a cell of a native strip (every game pixel one flat 8x8 block, binary alpha, 16 colours by median cut, each
game pixel the majority colour of the source pixels it covers, opaque when a third of them are) and writes
assets/source/janna/janna_fx_<name>.png plus janna_fx_anchors.json (each strip's cell and its anchor in it).
One scale per strip, set by the kit (1000 distance units a pixel) and Janna's 28 px: the gust bolt 12 px long,
its hit 16 px, Zephyr's wind spirit 14 px, its hit 18 px, Howling Gale's vortex 26 px across (34 px with its
wake), the knock-up spiral and the healing wind for a hero of 34 px (the heal a little smaller: its sparkles
climb far above the head), the Monsoon blast 84 px wide (radius 40000) and the Monsoon on the ground squeezed
to 84 x 42 (Codex drew it 1.47 to 1, the ground ellipses are 2 to 1). The storm shield is 36 px tall round the
ally, and Eye of the Storm's last frame is scaled to the same oval, so the loop takes over without a jump.
Anchors: the bolt and the wind spirit on their nose; the tornado on its vortex's centre (the projectile's
hitbox), its wake trailing behind; hits on the strip's middle; the knock-up spiral, the shield, the heal and
the two Monsoon rings on the ground row or middle they were drawn on.

The second step places every cell by its anchor: projectiles on the projectile, hits on the chest, the spiral,
the shield, the heal and the rings on the feet (a view on a unit is drawn at its pivot, 11 px above the ground;
Janna hovers 3 px above it). No palette or outline pass on the sheets. The storm shield is one buff picture in three phases (view_buffs
ThreePhase): Eye of the Storm's forming as the intro, the storm loop while the shield holds, and the forming
played backwards (flash, spiral, wings flying off) when it breaks or runs out. Writes league/effects/league_janna_fx
(bolt, hit, knockup, w_gust, w_hit, e_cast, storm, storm_end, r_heal) and league/effects/league_janna_big (tornado,
r_gale, r_storm).
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

SRC = os.path.join(ROOT, "assets", "source", "janna")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
PERSON = 34 / 362                      # a 34 px hero in the person-sized space of a 724 px tall frame

# raw strip -> native: name: (frames, game px per source px (one, or across and down), x anchor, y anchor)
#   x: "nose" the drawing's right edge, "vortex" the centre of the round vortex at its right end, "mid" each
#      drawing's middle, "cell" the middle of its rectangle
#   y: "mid" each drawing's middle, "strip" the middle of all the strip's drawings, or a source row (the ground)
RAW = {
    "bolt": (3, 12 / 553, "nose", "strip"),
    "hit": (5, 16 / 373, "mid", "strip"),
    "tornado": (4, 26 / 390, "vortex", "strip"),
    "knockup": (6, PERSON, "mid", 601),                    # row 601: the dust puffs on the ground
    "w_gust": (4, 14 / 498, "nose", "strip"),
    "w_hit": (5, 18 / 397, "mid", "strip"),
    "e_cast": (5, 36 / 428, "mid", 615),                   # its settled oval (frame 5) 36 px, bottom row 615
    "storm": (6, 36 / 391, "cell", 533),                   # the oval 36 px tall, its bottom on row 533
    "r_heal": (6, 0.08, "mid", 638),                       # the lowest sparkles, at the feet
    "r_gale": (6, 84 / 429, "mid", 360),                   # the ring's middle row
    "r_storm": (8, (84 / 231, 42 / 157), "mid", "mid"),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8") as f:
        return {a["file"]: a for a in json.load(f)["assets"]}


def from_raw(folder):
    manifest = load_manifest(folder)
    anchors = {}
    for name, (n, s, xr, yr) in RAW.items():
        sx, sy = s if isinstance(s, tuple) else (s, s)
        fn = f"janna_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA"))
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        rects = [(f["rect"]["x"], f["rect"]["y"], f["rect"]["w"], f["rect"]["h"]) for f in manifest[fn]["frames"]]
        if len(rects) != n:
            sys.exit(f"{fn}: the manifest lists {len(rects)} frames, not {n}")
        boxes, anchor = [], []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        rows = (min(b[2] for b in boxes), max(b[3] for b in boxes))
        for (x, y, w, h), box in zip(rects, boxes):
            ax = {"nose": box[1], "vortex": box[1] - (box[3] - box[2]) / 2, "mid": (box[0] + box[1]) / 2,
                  "cell": x + w / 2}[xr]
            ay = {"mid": (box[2] + box[3]) / 2, "strip": (rows[0] + rows[1]) / 2}.get(yr, yr)
            anchor.append((ax, ay))
        left = max(ax - b[0] for b, (ax, _) in zip(boxes, anchor))
        right = max(b[1] - ax for b, (ax, _) in zip(boxes, anchor))
        up = max(ay - b[2] for b, (_, ay) in zip(boxes, anchor))
        down = max(b[3] - ay for b, (_, ay) in zip(boxes, anchor))
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
    with open(G.lp(os.path.join(SRC, "janna_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"janna_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"janna_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (frames, spot of the anchor from the pivot, ms per frame, times played)}
FX = {
    "league_janna_fx": {
        "bolt": (3, (0, 0), [50] * 3, 1),
        "hit": (5, CHEST, [50] * 5, 1),
        "knockup": (6, FEET, [125] * 6, 1),                  # the 0.75 s knock-up
        "w_gust": (4, (0, 0), [60] * 4, 1),
        "w_hit": (5, CHEST, [60] * 5, 1),
        "e_cast": (5, FEET, [70] * 5, 1),
        "storm": (6, FEET, [100] * 6, 1),                    # loops while the shield holds
        # the shield breaking or running out: its forming played backwards (flash, spiral, wings)
        "storm_end": (("e_cast", 5, [3, 1, 0]), FEET, [70] * 3, 1),
        "r_heal": (6, FEET, [80] * 6, 1),
    },
    "league_janna_big": {
        "tornado": (4, (0, 0), [60] * 4, 1),
        "r_gale": (6, FEET, [80] * 6, 1),
        "r_storm": (8, FEET, [125] * 8, 1),                  # one second, played by each heal pulse
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "janna_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (n, (sx, sy), ms, times) in tags.items():
            src, frames = tag, None
            if isinstance(n, tuple):                         # frames of another strip, in this order
                src, n, frames = n
            ax, ay = anchors[src]["anchor"]
            fr = cells(src, n)
            if frames is not None:
                fr = [fr[k] for k in frames]
            out[tag] = [(G.centre_frame(f, sx - ax, sy - ay), m) for f, m in list(zip(fr, ms)) * times]
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

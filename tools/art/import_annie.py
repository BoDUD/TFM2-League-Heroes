#!/usr/bin/env python3
"""Import Annie's effects (assets/source/annie/PROMPTS.md, 1-13) as game sheets.

    python tools/art/import_annie.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_annie.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's thirteen strips came
back as raw image-generator output, like Teemo's: soft alpha, antialiased colours, canvases of other sizes
than asked (2172x724, 1983x793, 1585x992). Its manifest.json (schema annie_fx_raw_v1) gives every frame's
rectangle in the source (`assets[].frames[].rect`, x, y, width, height; the Q explosion and Tibbers' vanishing
have uneven ones). --raw turns every frame into a cell of a native strip (every game pixel one flat 8x8 block,
binary alpha, 16 colours by median cut, each game pixel the majority colour of the source pixels it covers,
opaque when a third of them are) and writes assets/source/annie/annie_fx_<name>.png, plus
annie_fx_anchors.json (each strip's cell and where its anchor sits in it). One scale per strip, set by the
kit (1000 distance units a pixel): the small fireball 12 px long with its trail, its hit 16 px, Disintegrate's
fireball 20 px, its explosion 28 px, the burning flames 16 px across, Molten Shield an oval 42 px tall round
her, the Pyromania ribbons 30 px tall, the stun stars 16 px, the ring of fire 60 px (radius 30000). Incinerate's
cone is squeezed to the kit's rectangle, 56 x 50 px, its point on the cell's left edge (Codex opened it wider
than 50 degrees). Tibbers is 42 px from his ears to his feet in all three of his strips, which Codex drew at
three sizes (the bear 235, 218 and about 270 source px tall), each scaled on its own. Each frame sits in its
cell on an anchor: the fireballs on their nose; hits, the explosion and the stars on the strip's middle; the
cone on its point; the shield on its oval's middle; the flames, the ribbons, Tibbers and his ring on the ground
row Codex drew them on, Tibbers across on his cell's middle so he does not slide between frames. His
three strips share one 20-colour palette, so his fur and glow are the same colours in all of them.

The second step places every cell by its anchor: the fireballs fly with their nose on the projectile; the hits
and the explosion on the chest; the cone's point 28 px behind the middle of the rectangle it is drawn on (a
LineRangeProjectile's view is centred on the rectangle and turned to the cast direction); the stun stars round
the head; the shield round her body; the flames, the ribbons, Tibbers and his ring with their ground row under
the feet (a view played at a spot is drawn like one on a unit, 11 px above the ground). The stars are listed
twice (the 1 s stun). No palette or outline pass on the sheets. Writes league/effects/league_annie_fx (bolt,
hit, q_ball, q_hit, burn, e_shield, pyro_ready, stun) and league/effects/league_annie_big (w_cone, tibbers_drop,
tibbers, tibbers_vanish, r_ring).
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

SRC = os.path.join(ROOT, "assets", "source", "annie")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
BODY = (0, -6)                         # the middle of a 34 px hero
HEAD = (0, -20)                        # round the top of a 34 px hero's head
TIBBERS = 42 / 218                     # game px per source px for the bear of the standing loop

# raw strip -> native: name: (frames, game px per source px (one, or across and down), x anchor, y anchor)
#   x: "nose" the drawing's right edge, "left" its left edge, "mid" its middle, "cell" the middle of its rectangle
#   y: "mid" each drawing's middle, "strip" the middle of all the strip's drawings, or a source row (the ground)
RAW = {
    "bolt": (3, 12 / 500, "nose", "strip"),
    "hit": (5, 16 / 387, "mid", "strip"),
    "q_ball": (4, 20 / 496, "nose", "strip"),
    "q_hit": (6, 28 / 386, "mid", "strip"),
    "w_cone": (6, (56 / 272, 50 / 342), "left", "strip"),
    "burn": (5, 16 / 300, "mid", 680),                  # row 680: the ground under both flames
    "e_shield": (6, 42 / 469, "mid", "strip"),
    "pyro_ready": (6, 30 / 383, "mid", 546),            # row 546: the ribbons' lowest point, at her ankles
    "stun": (6, 16 / 320, "mid", "strip"),
    "tibbers_drop": (6, TIBBERS * 218 / 235, "cell", 541),      # row 541: his feet; the bear 235 px tall here
    "tibbers": (8, TIBBERS, "cell", 515),
    "tibbers_vanish": (6, TIBBERS * 218 / 271, "cell", 531),
    "r_ring": (8, 60 / 155, "cell", 507),               # row 507: the ellipse's middle, on the ground
}


SHARED = ("tibbers_drop", "tibbers", "tibbers_vanish")      # one palette: the bear the same colours in all three


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8") as f:
        return {a["file"]: a for a in json.load(f)["assets"]}


def from_raw(folder):
    manifest = load_manifest(folder)
    anchors = {}
    bear = np.concatenate([np.asarray(Image.open(G.lp(os.path.join(folder, f"annie_fx_{k}.png"))).convert("RGBA")).reshape(-1, 4)
                           for k in SHARED])[:, None]
    bear_pal = palette(bear, 20)
    for name, (n, s, xr, yr) in RAW.items():
        sx, sy = s if isinstance(s, tuple) else (s, s)
        fn = f"annie_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA"))
        solid = a[..., 3] >= 100
        pal = bear_pal if name in SHARED else palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        rects = [f["rect"] for f in manifest[fn]["frames"]]
        if len(rects) != n:
            sys.exit(f"{fn}: the manifest lists {len(rects)} frames, not {n}")
        boxes, anchor = [], []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        rows = (min(b[2] for b in boxes), max(b[3] for b in boxes))
        for (x, y, w, h), box in zip(rects, boxes):
            ax = {"nose": box[1], "left": box[0], "mid": (box[0] + box[1]) / 2, "cell": x + w / 2}[xr]
            ay = {"mid": (box[2] + box[3]) / 2, "strip": (rows[0] + rows[1]) / 2}.get(yr, yr)
            anchor.append((ax, ay))
        # a cell round the anchor, big enough for every frame; the cone's point on its left edge
        left = max(ax - b[0] for b, (ax, _) in zip(boxes, anchor))
        right = max(b[1] - ax for b, (ax, _) in zip(boxes, anchor))
        up = max(ay - b[2] for b, (_, ay) in zip(boxes, anchor))
        down = max(b[3] - ay for b, (_, ay) in zip(boxes, anchor))
        if xr == "left":
            L, R = 0, math.ceil(right * sx)
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
    with open(G.lp(os.path.join(SRC, "annie_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"annie_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"annie_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (frames, spot of the anchor from the pivot, ms per frame, times played)}
FX = {
    "league_annie_fx": {
        "bolt": (3, (0, 0), [50] * 3, 1),
        "hit": (5, CHEST, [50] * 5, 1),
        "q_ball": (4, (0, 0), [50] * 4, 1),
        "q_hit": (6, BODY, [60] * 6, 1),
        "burn": (5, FEET, [70] * 5, 1),
        "e_shield": (6, BODY, [90] * 6, 1),
        "pyro_ready": (6, (0, 10), [110] * 6, 1),
        "stun": (6, HEAD, [85] * 6, 2),                      # the stun: 1 s
    },
    "league_annie_big": {
        "w_cone": (6, (-28, 0), [65] * 6, 1),                # its point at the caster, 28 px behind the middle
        "tibbers_drop": (6, FEET, [100, 60, 60, 60, 60, 60], 1),    # the impact on frame 2, 6 ticks in
        "tibbers": (8, FEET, [125] * 8, 1),                  # one link of the standing chain: 60 ticks
        "tibbers_vanish": (6, FEET, [85] * 6, 1),
        "r_ring": (8, FEET, [125] * 8, 1),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "annie_fx_anchors.json")), encoding="utf-8") as f:
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

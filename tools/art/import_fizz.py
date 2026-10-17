#!/usr/bin/env python3
"""Import Fizz's effects (assets/source/fizz/PROMPTS_FX.md, 1-12) as game sheets.

    python tools/art/import_fizz.py --native <Codex's delivery folder>   # once: Codex's 1x strips -> native strips
    python tools/art/import_fizz.py --raw <Codex's delivery folder>      # or: image-model drafts -> native strips
    python tools/art/import_fizz.py                                      # native strips -> effect sheets

The body comes from tools/art/import_native.py. Codex delivered the effects finished at game size (fizz_fx_done,
2026-10-01): `logical/fizz_fx_<name>_1x.png` in the pack's palettes, binary alpha, no dark ring round the splashes,
manifest.json's `assets[].frames[].rect_1x` ([x, y, w, h]) the window of every frame. --native keeps every pixel: each
frame is cut by its window (the sharks by their whole cell - the three rows have their own windows but one ground
line), anchored by the rules below and copied 1:1; only the warning ring, drawn once at 48 px (the small shark's
radius 24000), is widened to 60 and 72 px for the medium and the big shark (radii 30000 / 36000) along its rays,
the rim and the teeth keeping their width in pixels.
--raw is the route for image-model drafts (soft alpha, free colours; `frames[].rect`), as tools/art/import_fiora.py
does: each game pixel the majority colour of the source pixels it covers, opaque when a third of them are solid,
every colour snapped to the ramps that strip asked for (water, the trident's teal, the orange fish, the shark and its
maw); then the ring Codex draws round splashes in their darkest shade comes off (an edge pixel of the darkest water or
teal goes when two lighter neighbours hold the shape, else it takes the next shade; the fish and the shark keep their
own dark edge - the pack allowed it for objects). One scale per strip, set by the kit (1000 distance units a pixel):
the hits 14-22 px, the dash wake 32, the jump splash 24, the slam 64 (radius 30000), the slow 18, the fish 14 flying /
16 stuck or lying, the warning ring 48 / 60 / 72 (the three sharks' radii 24000 / 30000 / 36000) and the sharks drawn
at their own sizes in one strip, scaled so the big one's ring is 72.
Writes assets/source/fizz/fizz_fx_<name>.png plus fizz_fx_anchors.json.
The second step places every cell by its anchor on the unit and times it by the kit (60 ticks a second): hits on the
chest, ground pieces on the soles' row (11 px under the pivot), the fish on the right of the chest of the champion it
stuck to, the rings and the sharks round a unit's feet, the flying fish on its projectile; the lying fish over the 2 s
until the shark (its loop five times). Writes league/effects/league_fizz_fx and league_fizz_big (the slam, the rings,
the sharks).
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
from import_fiora import anchors_of, mirror, rgb, shifted, snap  # noqa: E402
from import_morgana import load_manifest, rect  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "fizz")
MOD = os.path.join(ROOT, "league")
Z = 8
HIT = (0, -8)                          # a hit on the upper body of a 32-40 px hero
STUCK = (8, -10)                       # the fish stuck on a champion: on the right of his chest (Codex drew it
                                       # clinging to the side, the figure left clear)
GROUND = (0, 10)                       # the middle of a ring round a unit's feet (the soles 11 px under its pivot)
FEET = (0, 12)                         # the lowest row of a splash at a unit's feet
POINT = (0, 0)                         # a projectile, or a picture on a point
# the pack's colours (PROMPTS_FX.md)
WATER = ["FFFFFF", "D8F8FF", "8CE6FF", "3CC0F0", "1A84D0", "0E4A94"]
TEAL = ["E8FFF6", "9EF2D8", "3FD0B0", "16947E", "0A5B4A"]
FISH = ["FFF4E0", "FFC878", "FF8C34", "D85A18", "8C3412"]
SHARK = ["F0F6FA", "B4CCDC", "6E90AC", "3E5C7C", "22344C", "121C2C"]
MAW = ["FFFFFF", "E8E0D0", "B03A48", "6A1828"]
RAMPS = {"white": ["FFFFFF"], "water": WATER, "teal": TEAL, "fish": FISH, "shark": SHARK, "maw": MAW}
RIM = {"0E4A94": "1A84D0", "0A5B4A": "16947E"}   # Codex's ring shade -> the next shade (splashes only)
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames; ramps; scale by `size` game px over `measure` ("w" the widest drawing, "h" the tallest)
# or an explicit `scale`; anchors per axis as in import_fiora ("cell", "lowest", "ring", ("at", share), ("px", n));
# `file` names the source when one drawing makes several strips (the warning ring at three sizes); `rim` False keeps
# the darkest edge (the fish, the shark)
RAW = {
    "hit": dict(n=5, ramps="water", size=14, measure="w"),
    "w_hit": dict(n=6, ramps="white teal water", size=22, measure="w"),
    "q_hit": dict(n=5, ramps="water", size=20, measure="w"),
    "q_dash": dict(n=5, ramps="water", size=32, measure="w", x=("at", 0.2), y="lowest"),
    "e_up": dict(n=5, ramps="water", size=24, measure="w", y="lowest"),
    "e_slam": dict(n=7, ramps="water", size=64, measure="w", y="ring"),
    "e_slow": dict(n=6, ramps="water", size=18, measure="w", y="ring"),
    "r_fish": dict(n=4, ramps="fish water", size=14, measure="w", rim=False),
    "r_stuck": dict(n=4, ramps="fish water", size=16, measure="w", rim=False),
    "r_ring1": dict(file="r_ring", n=4, ramps="water shark", size=48, measure="w"),
    "r_ring2": dict(file="r_ring", n=4, ramps="water shark", size=60, measure="w"),
    "r_ring3": dict(file="r_ring", n=4, ramps="water shark", size=72, measure="w"),
    "r_fish_ground": dict(n=4, ramps="fish water", size=16, measure="w", y="lowest", rim=False),
    "r_shark": dict(n=24, ramps="shark maw water", size=72, measure="w", y="lowest", rim=False),
}


def unrim(a):
    """The ring off: an edge pixel in a ramp's darkest shade goes when 2+ lighter 8-neighbours hold the shape, else it
    takes the ramp's next shade. Returns the picture and how many edge pixels were in the ring shade."""
    a = a.copy()
    op = a[..., 3] > 0
    hexa = np.array([["%02X%02X%02X" % tuple(p[:3]) for p in row] for row in a])
    rim = op & np.isin(hexa, list(RIM))
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    lit = sum(shifted(op & ~rim, dy, dx).astype(int) for dy, dx in N8)
    target = rim & edge
    gone = target & (lit >= 2)
    a[gone] = 0
    for dark, nxt in RIM.items():
        m = target & ~gone & (hexa == dark)
        a[m, :3] = rgb(nxt)
    return a, int(target.sum())


def strip(name, spec, a, solid, rects, sx, sy, rim):
    """The native strip of one effect: every frame round its anchor, each game pixel the majority colour of the source
    pixels it covers (1:1 at scale 1), colours snapped to the strip's ramps; saved at 8x. Returns its anchors entry."""
    box = []
    for x, y, w, h in rects:
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        box.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
    hexes = [h for r in spec["ramps"].split() for h in RAMPS[r]]
    idx = snap(a, solid, np.array([rgb(h) for h in hexes], float))
    pal = np.array([rgb(h) for h in hexes], np.uint8)
    anc = anchors_of(spec, solid, rects, box)
    L = math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, box)) * sx) + 1
    U = math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, box)) * sy) + 1
    tw, th = 2 * L + 1, 2 * U + 1
    n = len(rects)
    out = np.zeros((th, tw * n, 4), np.uint8)
    rims = 0
    for k, (x, y, w, h) in enumerate(rects):
        ax, ay = anc[k]
        for r in range(th):
            sy0 = int(math.floor(ay + (r - U - 0.5) / sy))
            sy1 = max(int(math.floor(ay + (r - U + 0.5) / sy)), sy0 + 1)
            sy0, sy1 = max(y, sy0), min(y + h, sy1)
            if sy1 <= sy0:
                continue
            for c in range(tw):
                sx0 = int(math.floor(ax + (c - L - 0.5) / sx))
                sx1 = max(int(math.floor(ax + (c - L + 0.5) / sx)), sx0 + 1)
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
        if rim and spec.get("rim", True):
            cell, m = unrim(cell)
            rims += m
        if spec.get("mirror"):
            cell = mirror(cell, U)
        out[:, k * tw:(k + 1) * tw] = cell
    Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"fizz_fx_{name}.png")))
    print(f"fizz_fx_{name}.png  {n} cells of {tw}x{th}, anchor {L},{U}, scale {sx:.4f}, {rims} ring pixels, "
          f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    return {"cell": [tw, th], "anchor": [L, U], "frames": n}


def old_anchors(path, only):
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_anchors(path, anchors):
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "fizz_fx_anchors.json")
    anchors = old_anchors(path, only)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"fizz_fx_{spec.get('file', name)}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [rect(f) for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        if "scale" in spec:
            sx, sy = spec["scale"]
        else:
            ext = []
            for x, y, w, h in rects:
                ys, xs = np.nonzero(solid[y:y + h, x:x + w])
                ext.append((xs.max() - xs.min() + 1) if spec["measure"] == "w" else (ys.max() - ys.min() + 1))
            sx = sy = spec["size"] / max(ext)
        anchors[name] = strip(name, spec, a, solid, rects, sx, sy, True)
    save_anchors(path, anchors)


# --native: the warning ring drawn once at 48 px, widened for the medium and the big shark; the sharks cut by their
# whole cell (the three rows share the ground line, their windows differ)
RING = {"r_ring2": 60, "r_ring3": 72}
BY_CELL = {"r_shark"}


def widen_ring(frame, wt):
    """A 2:1 ring frame widened to `wt` px along its rays: every target pixel takes the source pixel at the same angle
    and the same distance in from the outer ellipse, so the rim and the teeth keep their width in pixels (a nearest
    scale by 1.25 / 1.5 made the 1-px rim 1-2 px and the teeth lumpy); the teeth only spread apart."""
    hs, ws = frame.shape[:2]
    cxs, cys, a_s, b_s = (ws - 1) / 2, (hs - 1) / 2, ws / 2, hs / 2
    ht = wt // 2
    a_t, b_t = wt / 2, ht / 2
    out = np.zeros((ht, wt, 4), np.uint8)
    for yy in range(ht):
        for xx in range(wt):
            x, y = xx - (wt - 1) / 2, yy - (ht - 1) / 2
            phi = math.atan2(y, x)
            c, s = math.cos(phi), math.sin(phi)
            d = 1 / math.sqrt(c * c / a_t ** 2 + s * s / b_t ** 2) - math.hypot(x, y)
            rs = 1 / math.sqrt(c * c / a_s ** 2 + s * s / b_s ** 2) - d
            if d < 0 or rs < 0:
                continue
            xs, ys = int(round(cxs + rs * c)), int(round(cys + rs * s))
            if 0 <= xs < ws and 0 <= ys < hs:
                out[yy, xx] = frame[ys, xs]
    return out


def from_native(folder, only=None):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8") as f:
        assets = {a["name"]: a for a in json.load(f)["assets"]}
    path = os.path.join(SRC, "fizz_fx_anchors.json")
    anchors = old_anchors(path, only)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        asset = assets[spec.get("file", name)]
        a = np.asarray(Image.open(G.lp(os.path.join(folder, asset["file_1x"]))).convert("RGBA")).copy()
        solid = a[..., 3] > 0
        frames = sorted(asset["frames"], key=lambda f: (f["row"], f["column"]))
        if name in BY_CELL:
            cw, ch = asset["logical_cell"]
            rects = [(f["column"] * cw, f["row"] * ch, cw, ch) for f in frames]
        else:
            rects = [tuple(f["rect_1x"]) for f in frames]
        if len(rects) != spec["n"]:
            sys.exit(f"{asset['file_1x']}: {len(rects)} frames, not {spec['n']}")
        if name in RING:
            wide = [widen_ring(a[y:y + h, x:x + w], RING[name]) for x, y, w, h in rects]
            ht, wt = wide[0].shape[:2]
            a = np.zeros((ht + 2, (wt + 2) * len(wide), 4), np.uint8)
            rects = []
            for k, f in enumerate(wide):
                a[1:ht + 1, k * (wt + 2) + 1:k * (wt + 2) + 1 + wt] = f
                rects.append((k * (wt + 2), 0, wt + 2, ht + 2))
            solid = a[..., 3] > 0
        anchors[name] = strip(name, spec, a, solid, rects, 1.0, 1.0, False)
    save_anchors(path, anchors)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"fizz_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"fizz_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


LYING = [0, 1, 2, 3] * 5                 # the lying fish: its loop over the 2 s until the shark

# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_fizz_fx": {
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "w_hit": [("w_hit", range(6), HIT, [55] * 6)],
        "q_hit": [("q_hit", range(5), HIT, [50] * 5)],
        "q_dash": [("q_dash", range(5), FEET, [70] * 5)],
        "e_up": [("e_up", range(5), FEET, [60] * 5)],
        "e_slow": [("e_slow", range(6), GROUND, [80] * 6)],
        "r_fish": [("r_fish", range(4), POINT, [60] * 4)],
        "r_stuck": [("r_stuck", range(4), STUCK, [100] * 4)],
        "r_fish_ground": [("r_fish_ground", LYING, FEET, [100] * len(LYING))],
    },
    "league_fizz_big": {
        "e_slam": [("e_slam", range(7), GROUND, [70] * 7)],
        "r_ring1": [("r_ring1", range(4), GROUND, [100] * 4)],
        "r_ring2": [("r_ring2", range(4), GROUND, [100] * 4)],
        "r_ring3": [("r_ring3", range(4), GROUND, [100] * 4)],
        "r_shark1": [("r_shark", range(0, 8), FEET, [70] * 8)],
        "r_shark2": [("r_shark", range(8, 16), FEET, [70] * 8)],
        "r_shark3": [("r_shark", range(16, 24), FEET, [70] * 8)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "fizz_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, parts in tags.items():
            out[tag] = []
            for src, used, spot, ms in parts:
                ax, ay = anchors[src]["anchor"]
                strip = cells(src, anchors[src]["frames"])
                for k, m in zip(used, ms):
                    out[tag].append((G.centre_frame(strip[k], spot[0] - ax, spot[1] - ay), m))
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--native", help="Codex's delivery folder: rebuild the native strips from its 1x strips first")
    ap.add_argument("--only", action="append", help="with --raw / --native: only this strip (repeatable)")
    args = ap.parse_args()
    if args.native:
        from_native(args.native, args.only)
    elif args.raw:
        from_raw(args.raw, args.only)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

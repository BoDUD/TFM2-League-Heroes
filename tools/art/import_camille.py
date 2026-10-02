#!/usr/bin/env python3
"""Import Camille's effects (assets/source/camille/PROMPTS_FX.md, 1-16) as game sheets.

    python tools/art/import_camille.py --raw <Codex's delivery folder>   # once: delivered PNGs -> native strips
    python tools/art/import_camille.py                                   # native strips -> effect sheets

The body comes from tools/art/import_native.py. --raw turns every delivered strip into a native strip
(assets/source/camille/camille_fx_<name>.png, 8x blocks). Codex's delivery (2026-10-02, 16 strips, 95 frames) is
flat 8x8 blocks in the asked palette, its cells larger than the drawings, so each strip is read a pixel a block and
then either kept as drawn (`native`: drawn within ~20% of its game size - Q2's burst, the sweep's fan (41 long against
W's DirDot radius 46000), the hook and its cable (8 squares a frame), the stun, R's spark, E's landing ring and the
arena, whose forming and standing strips must keep one scale so the loop meets the landing) or resampled to its game
size like a raw drawing (each game pixel the majority colour of the source pixels it covers, kept when a fifth of them
are solid so one-pixel sparks survive): the hits 14-20 px wide (drawn 25-29), the shield 50 tall over her 46 rows
(drawn 65), the target's mark 28 (drawn 46), the wall zap 20. Every colour is snapped to the ramps the strip asked
for, then the ring comes off the glows (import_riven.unrim's rule: an edge pixel of a ramp's darkest shade goes when
two lighter neighbours hold the shape, else it takes the next shade). The shield slid 7 px sideways a frame in the
delivery: each of its frames is anchored on its own drawing. Writes camille_fx_anchors.json beside the strips.
The second step places every cell by its anchor on the unit and times it by the kit (60 ticks a second): a hit on the
chest, the stun over the crown, the shield round her whole figure, the rings and the arena on the soles' row; the
sweep's fan with its point 30 px behind the line's middle (a LineRangeProjectile's picture is centred on the line,
length 60000, so the point starts at her), the hook on the projectile (its cable trailing back to her: 8 squares a
frame at 6 px a tick is 22 ms a frame). The arena forms over r_piece's 30 ticks (r_land) and the kit replays the
standing arena (r_zone) every 30 ticks after it until R ends. Writes league/effects/league_camille_fx and
league_camille_big.
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
from import_morgana import load_manifest, rect  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "camille")
MOD = os.path.join(ROOT, "league")
Z = 8
HIT = (0, -8)                          # a hit on the upper body of a 35-40 px hero
OVERHEAD = (0, -31)                    # over a 35-40 px hero's crown (the stun)
GROUND = (0, 10)                       # the middle of a ring round a unit's feet (the soles 11 px under its pivot)
BODY = (0, -12)                        # the middle of her 46 rows (crown 34 over the pivot, blade tips 11 under it)
LINE = (-30, 0)                        # the sweep's point: half of the line's 60000 behind its middle
TURNED = {"r_field"}                   # pictures of zones the engine draws turned half round (direction (-1, 0))
# the pack's colours (PROMPTS_FX.md)
HEX = ["FFFFFF", "CFFBFF", "6FF2FF", "00C8F0", "0089C7", "00457A"]
DEEP = ["B8D8FF", "5A9CFF", "2F5FD9", "1C2F80"]
GOLD = ["FFF4C2", "FFE487", "E2B644", "9A752C"]
VIOLET = ["F2D9FF", "C98CF0", "9447D1", "5E2491"]
STEEL = ["FFFFFF", "E6E8F0", "B8C4D8", "7F8CA8", "4A5470"]
DUST = ["C8BCA8", "9A8C78", "6E6252"]
RAMPS = {"hex": HEX, "deep": DEEP, "gold": GOLD, "violet": VIOLET, "steel": STEEL, "dust": DUST}
RIM = {"00457A": "0089C7", "1C2F80": "2F5FD9", "5E2491": "9447D1", "4A5470": "7F8CA8", "6E6252": "9A8C78"}
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames; ramps; scale: `native` reads the delivery a pixel a block (Codex drew it near its
# game size: within ~20%), else `size` game px over `measure` ("w" the widest drawing, "h" the tallest) on `measure_on`
# frames (default all), a game pixel kept when `keep` of the source pixels it covers are solid (sparks of one
# source pixel survive a halving at 0.2); anchors per axis: "cell" the cell's middle, ("at", share) of the cell
# (0: the middle of its first column), "lowest" the lowest drawn row over all frames, "box" the middle of all the
# frames' drawing, "own" each frame's own drawing (Codex's shield slid 7 px a frame); `mirror` the top half onto the
# bottom (an odd-height strip drawn symmetric about its line)
RAW = {
    "hit": dict(n=5, ramps="steel hex", size=14, measure="w", keep=0.2),
    "q_hit": dict(n=6, ramps="hex", size=20, measure="w", keep=0.2),
    "q2_hit": dict(n=7, ramps="hex", native=True),
    "w_arc": dict(n=6, ramps="hex steel", native=True, x=("at", 0)),
    "w_hit": dict(n=4, ramps="hex", size=14, measure="w", keep=0.2),
    "w_edge": dict(n=6, ramps="hex deep", size=20, measure="w", keep=0.2),
    "e_hook": dict(n=8, ramps="gold hex deep", native=True, keep_rim=True),   # the cable's dark core is its middle
    "e_hit": dict(n=5, ramps="hex deep", size=16, measure="w", keep=0.2),
    "e_stun": dict(n=8, ramps="hex", native=True),
    "p_shield": dict(n=6, ramps="hex", size=50, measure="h", keep=0.2, x="own", y="own"),
    "r_mark": dict(n=4, ramps="violet hex", size=28, measure="w", keep=0.2, x="box", y="box"),
    "r_wall": dict(n=5, ramps="violet hex", size=20, measure="w", keep=0.2),
    "r_hit": dict(n=4, ramps="violet", native=True),
    "e_land": dict(n=7, ramps="hex dust", native=True, x="box", y="box"),
    "r_land": dict(n=8, ramps="hex deep", native=True),
    "r_zone": dict(n=6, ramps="hex deep", native=True),
}


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = m[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
    return out


def snap(a, solid, pal):
    """Palette index of every solid pixel (-1 elsewhere), in chunks."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - pal[None]) ** 2).sum(2).argmin(1)
    return idx


def unrim(a):
    """The ring off the glows: an edge pixel in a ramp's darkest shade goes when 2+ lighter 8-neighbours hold the
    shape, else it takes the ramp's next shade. Returns the picture and how many edge pixels were in the ring shade."""
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


def mirror(cell, U):
    """The top half (rows 0..U) mirrored onto the bottom: exact symmetry about the anchor row."""
    out = cell.copy()
    for r in range(U):
        out[2 * U - r] = cell[r]
    return out


def anchors_of(spec, rects, box):
    """Source (x, y) of every frame's anchor."""
    out = []
    for axis, how in ((0, spec.get("x", "cell")), (1, spec.get("y", "cell"))):
        vals = []
        for k, (x, y, w, h) in enumerate(rects):
            o, size = (x, w) if axis == 0 else (y, h)
            if how == "cell":
                vals.append(o + size / 2)
            elif how == "lowest":
                vals.append(y + max(b[3] - r[1] for b, r in zip(box, rects)) - 0.5)
            elif how == "box":
                lo = min((b[0] - r[0]) if axis == 0 else (b[2] - r[1]) for b, r in zip(box, rects))
                hi = max((b[1] - r[0]) if axis == 0 else (b[3] - r[1]) for b, r in zip(box, rects))
                vals.append(o + (lo + hi) / 2)
            elif how == "own":
                b = box[k]
                vals.append(((b[0] + b[1]) if axis == 0 else (b[2] + b[3])) / 2)
            elif how[0] == "at":
                vals.append(o + size * how[1] if how[1] else o + 0.5)
            else:
                raise ValueError(how)
        out.append(vals)
    return list(zip(out[0], out[1]))


def flat_blocks(a):
    """The image one pixel a block when it is made of flat 8x8 blocks with alpha 0/255, else None."""
    H, W = a.shape[:2]
    if H % Z or W % Z or not set(np.unique(a[..., 3])) <= {0, 255}:
        return None
    b = a.reshape(H // Z, Z, W // Z, Z, 4)
    return b[:, 0, :, 0].copy() if (b == b[:, :1, :, :1]).all() else None


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "camille_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"camille_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        flat = flat_blocks(a)
        if flat is not None:                       # flat 8x8 blocks: work on the delivery's own pixels
            a = flat
        solid = a[..., 3] >= 100
        if fn in manifest and flat is None:
            rects = [rect(f) for f in manifest[fn]["frames"]]
        else:                                      # equal cells across the image
            cw = a.shape[1] // spec["n"]
            rects = [[k * cw, 0, cw, a.shape[0]] for k in range(spec["n"])]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        box = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            box.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1) if len(xs) else
                       (x + w // 2, x + w // 2 + 1, y + h // 2, y + h // 2 + 1))
        if spec.get("native"):
            sx = sy = 1.0
        else:
            on = [box[k] for k in spec.get("measure_on", range(spec["n"]))]
            ext = {"h": lambda: max(b[3] - b[2] for b in on), "w": lambda: max(b[1] - b[0] for b in on)}[spec["measure"]]()
            sx = sy = spec["size"] / ext
        hexes = [h for r in spec["ramps"].split() for h in RAMPS[r]]
        idx = snap(a, solid, np.array([rgb(h) for h in hexes], float))
        pal = np.array([rgb(h) for h in hexes], np.uint8)
        anc = anchors_of(spec, rects, box)
        L = math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, box)) * sx) + 1
        U = math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, box)) * sy) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * spec["n"], 4), np.uint8)
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
                    if m.mean() < spec.get("keep", 1 / 3):
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
            cell = out[:, k * tw:(k + 1) * tw]
            if not spec.get("keep_rim"):
                cell, n = unrim(cell)
                rims += n
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, k * tw:(k + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": spec["n"]}
        print(f"{fn}  {spec['n']} cells of {tw}x{th}, anchor {L},{U}, scale {sx:.4f}, {rims} ring pixels, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"camille_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"camille_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_camille_fx": {
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "q_hit": [("q_hit", range(6), HIT, [55] * 6)],
        "q2_hit": [("q2_hit", range(7), HIT, [60] * 7)],
        "w_arc": [("w_arc", range(6), LINE, [60] * 6)],                    # the line lives w_arc_t 22 ticks
        "w_hit": [("w_hit", range(4), HIT, [50] * 4)],
        "w_edge": [("w_edge", range(6), HIT, [60] * 6)],
        "e_hook": [("e_hook", range(8), (0, 0), [22] * 8)],                 # 8 squares of cable at 6 px a tick
        "e_hit": [("e_hit", range(5), HIT, [50] * 5)],
        "e_stun": [("e_stun", range(8), OVERHEAD, [94] * 7 + [92])],        # e_stun 45 ticks (League's 0.75 s)
        "p_shield": [("p_shield", range(6), BODY, [100] * 6)],              # a buff view: loops while the shield holds
        # the charged second kick waiting (q2_ready's three-phase buff view, drawn by work/cm/q2_glow_cm.py): the
        # flash as the charge completes, the blades' bloom while it waits, the bloom draining as the kick goes off
        "q2_flash": [("q2_flash", range(4), (0, 0), [60] * 4)],
        "q2_ready": [("q2_ready", range(6), (0, 0), [80] * 6)],
        "q2_end": [("q2_end", range(3), (0, 0), [50] * 3)],
        "r_mark": [("r_mark", range(4), GROUND, [120] * 4)],                # a buff view: loops under the target
        "r_wall": [("r_wall", range(5), HIT, [60] * 5)],
        "r_hit": [("r_hit", range(4), HIT, [50] * 4)],
    },
    "league_camille_big": {
        "e_land": [("e_land", range(7), GROUND, [50] * 7)],
        # R's field: its zone's own picture for the zone's 180 ticks - the arena forming (500 ms), then standing
        # (five 500-ms loops) - turned half round, as the zone's direction is (-1, 0) and the engine turns it back
        "r_field": [("r_land", range(8), GROUND, [60] * 6 + [70, 70])] +
                   [("r_zone", range(6), GROUND, [83, 83, 84, 83, 83, 84])] * 5,
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "camille_fx_anchors.json")), encoding="utf-8") as f:
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
                    f = G.centre_frame(strip[k], spot[0] - ax, spot[1] - ay)
                    out[tag].append((np.ascontiguousarray(f[::-1, ::-1]) if tag in TURNED else f, m))
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    ap.add_argument("--only", action="append", help="with --raw: only this strip (repeatable)")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Import Jhin's effects (assets/source/jhin/PROMPTS_FX.md, 27 sheets) as the game sheets league_jhin_fx and
league_jhin_big.

    python tools/art/import_jhin.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_jhin.py                                   # native strips -> the effect sheets

The body comes from tools/art/rig_jhin.py and import_native.py. --raw turns each frame of Codex's image-model drafts
(every frame's cell in manifest.json, `assets[].frames[].rect` = [x, y, w, h]; the slows' 4 x 2 read row by row: the
lotus's, then R's) into a cell of a native strip (assets/source/jhin/jhin_fx_<name>.png, 8x, plus jhin_fx_anchors.json)
the way import_ryze.py does: each game pixel the majority colour of the source pixels it covers, opaque when a quarter of
them are solid (alpha 100 and up: the one-pixel sparks survive), every colour snapped to the ramps the pack gave that
effect (GOLD, ROSE, VIOLET, TEAL; the grenade's METAL and the outline of the two objects, the canister and the lotus;
SMOKE), then the ring comes off the glows (an edge pixel in a ramp's darkest shade goes when two lighter neighbours
hold the shape, else it takes the next shade) - not off the objects, whose outline is drawn. One scale per strip: `size`
game px over the drawings' widest (w), tallest (h) or larger side (m), the pack's sizes. The four bullets are made
exactly symmetric about their core's row (the game turns them with their flight).
Anchors (source pixels, the same spot in every cell unless the drawing moves): the bullets on their white core (its
front half); the muzzle flashes and the dropping grenade on the points Codex registered in manifest.json (`anchor`:
the white core at the cell's left middle, the landing point two thirds down); the flashes and blasts on a frame's
flash; the objects and the slows on their cell's middle; the root, the lotus on the ground, the blast and the curtain
on their ground ring.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot; measured on the finished strips, tools/art/rig_jhin.py: Whisper raised in attack 2 (19, -21), its muzzle in
attack 3 (30, -7), the fourth shot's (35, -8), the gold fist in Q 3 (10, -10), the cane-rifle's muzzle in W 7 (39, -9),
the cannon's in the R shot (39, -8); the reload's bullets 3 px over the hood) and times it by the kit (60 ticks a
second): the bullets start with an empty tick (a projectile's first move points its picture up; import_lucian.py's
RAY_SKIP) and loop their frames over their longest flight; the root holds its vines to the root's end (100 ticks); the
bloom turns until the blast (120 ticks); the reload lights a bullet each 0.5 s of its 130 ticks; the curtain plays with
the deploy (30 ticks). Writes league/effects/league_jhin_fx and league_jhin_big (the lotus's bloom and blast).
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
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jhin")
MOD = os.path.join(ROOT, "league")
Z = 8

RAMPS = {
    "GOLD": ["A85E14", "F0A030", "FFD45E", "FFF3C4", "FFFFFF"],
    "ROSE": ["8A1240", "E0306A", "FF7FA6", "FFD6E2", "FFFFFF"],
    "VIOLET": ["4E2A9E", "8E5BEA", "C49CFF", "EEDCFF", "FFFFFF"],
    "TEAL": ["126858", "22B28A", "7EF2D8", "D2FFF6", "FFFFFF"],
    "METAL": ["0E0814", "1E2230", "3A4458", "6A7890", "A8B4C4", "E6ECF2"],   # the canister, with Jhin's outline
    "SMOKE": ["746A5C", "A69C8C", "D2CABC", "F4F0E8"],
}
# a ramp's darkest shade at a glow's edge -> the next shade
RIM = {"A85E14": "F0A030", "8A1240": "E0306A", "4E2A9E": "8E5BEA", "126858": "22B28A"}
OUTLINE = "0E0814"
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps, mirror (bullets), obj (keeps its outline)
RAW = {
    "a_bolt": dict(n=4, size=10, measure="w", anchor="head", ramps="GOLD", mirror=True),
    "a4_bolt": dict(n=4, size=18, measure="w", anchor="head", ramps="GOLD ROSE", mirror=True),
    "a_cast": dict(n=4, size=10, measure="m", anchor=("fixed", "core", 0), ramps="GOLD"),
    "a_muzzle": dict(n=4, size=12, measure="w", anchor="manifest", ramps="TEAL GOLD"),
    "a_hit": dict(n=4, size=10, measure="m", anchor=("fixed", "core", 0), ramps="GOLD"),
    "a4_muzzle": dict(n=5, size=20, measure="w", anchor="manifest", ramps="GOLD ROSE"),
    "a4_hit": dict(n=5, size=18, measure="m", anchor=("fixed", "core", 0), ramps="GOLD ROSE"),
    "a_reload": dict(n=8, size=18, measure="w", anchor="cell", ramps="GOLD"),
    "q_nade": dict(n=4, size=8, measure="m", anchor="cell", ramps="METAL GOLD TEAL", obj=True),
    "q_throw": dict(n=4, size=10, measure="m", anchor=("fixed", "core", 0), ramps="GOLD"),
    "q_boom": dict(n=5, size=18, measure="m", anchor=("fixed", "core", 0), ramps="GOLD SMOKE"),
    "q_drop": dict(n=4, size=24, measure="h", anchor="manifest", ramps="METAL GOLD TEAL", obj=True),
    "w_shot": dict(n=4, size=32, measure="w", anchor="head", ramps="GOLD VIOLET", mirror=True),
    "w_muzzle": dict(n=5, size=22, measure="w", anchor="manifest", ramps="GOLD ROSE VIOLET"),
    "w_hit": dict(n=5, size=16, measure="m", anchor=("fixed", "core", 0), ramps="GOLD ROSE VIOLET"),
    "w_root": dict(n=8, size=22, measure="w", anchor=("fixed", "ring", 0), ramps="VIOLET ROSE"),
    "e_seed": dict(n=4, size=8, measure="m", anchor="cell", ramps="GOLD ROSE", obj=True),
    "e_land": dict(n=8, size=14, measure="w", anchor=("fixed", "low", 0), ramps="GOLD ROSE", obj=True),
    "e_bloom": dict(n=10, size=36, measure="w", anchor="cell", ramps="GOLD ROSE"),
    "e_boom": dict(n=7, size=40, measure="m", anchor=("fixed", "ring", 0), ramps="GOLD ROSE SMOKE"),
    "e_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="GOLD ROSE"),
    # Codex drew the curtain as two tall pillars on a ring (152 x ~300 source px): 36 wide made it 72 rows; 40 rows
    # tall (his height) puts the pillars ~20 px apart, beside his body
    "r_deploy": dict(n=8, size=40, measure="h", anchor=("fixed", "ring", 0), ramps="ROSE GOLD"),
    "r_muzzle": dict(n=5, size=24, measure="w", anchor="manifest", ramps="GOLD ROSE"),
    "r_bullet": dict(n=4, size=30, measure="w", anchor="head", ramps="GOLD ROSE", mirror=True),
    "r_hit": dict(n=5, size=18, measure="m", anchor=("fixed", "core", 0), ramps="GOLD ROSE"),
    "r_crit": dict(n=6, size=26, measure="m", anchor=("fixed", "core", 0), ramps="GOLD ROSE"),
    "slowed": dict(n=8, size=20, measure="w", anchor="cell", ramps="ROSE GOLD"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def hexes(a):
    return np.array([["%02X%02X%02X" % tuple(int(v) for v in p[:3]) for p in row] for row in a])


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = m[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
    return out


def unrim(a):
    a = a.copy()
    op = a[..., 3] > 0
    hx = hexes(a)
    rim = op & np.isin(hx, list(RIM))
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    lit = sum(shifted(op & ~rim, dy, dx).astype(int) for dy, dx in N8)
    target = rim & edge
    gone = target & (lit >= 2)
    a[gone] = 0
    for dark, nxt in RIM.items():
        m = target & ~gone & (hx == dark)
        a[m, :3] = [int(nxt[i:i + 2], 16) for i in (0, 2, 4)]
    return a


def snap(a, solid, pal):
    """Palette index of every solid pixel (-1 elsewhere)."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - pal[None]) ** 2).sum(2).argmin(1)
    return idx


def mirror(cell, U):
    out = cell.copy()
    for r in range(U):
        if 2 * U - r < cell.shape[0]:
            out[2 * U - r] = cell[r]
    return out


def bright(a):
    return (a[..., 3] >= 100) & (a[..., :3].min(-1) >= 215)


def anchor(how, k, a, solid, rects):
    """(x, y) of frame k's anchor in the source."""
    x, y, w, h = rects[k]
    if how == "cell":
        return x + w / 2, y + h / 2
    if how[0] == "fixed":                  # frame j's anchor, the same spot in every cell
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    s = solid[y:y + h, x:x + w]
    ys, xs = np.nonzero(s)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    b = bright(a[y:y + h, x:x + w])
    if how == "head":                      # the white core in the drawing's front half
        b[:, :int(x0 + 0.5 * (x1 - x0))] = False
        by, bx = np.nonzero(b)
        if not len(bx):
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + (bx.min() + bx.max() + 1) / 2, y + (by.min() + by.max() + 1) / 2
    if how == "core":                      # the white flash's middle
        by, bx = np.nonzero(b)
        if len(bx) < 20:
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + bx.mean() + 0.5, y + by.mean() + 0.5
    if how == "left":                      # a muzzle: the star's left end, halfway down its bright rows
        by, bx = np.nonzero(b)
        if len(bx) < 5:
            by, bx = ys, xs
        return x + bx.min(), y + (by.min() + by.max() + 1) / 2
    if how == "ring":                      # the ring's middle: the lower 40% of the drawing
        low = s.copy()
        low[:int(y1 - 0.4 * (y1 - y0))] = False
        ly, lx = np.nonzero(low)
        return x + (lx.min() + lx.max() + 1) / 2, y + (ly.min() + ly.max() + 1) / 2
    if how == "low":                       # an object on the ground: the middle of its lowest row
        lx = np.nonzero(s[y1 - 1])[0]
        return x + (lx.min() + lx.max() + 1) / 2, y + y1
    raise ValueError(how)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"jhin_fx_{name}.png"
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        idx = snap(a, solid, pal)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
        if spec["anchor"] == "manifest":       # registered by Codex (the muzzles' white core, the grenade's landing)
            anc = [(x + f["anchor"][0], y + f["anchor"][1]) for (x, y, _, _), f in zip(rects, manifest[fn]["frames"])]
        else:
            anc = [anchor(spec["anchor"], k, a, solid, rects) for k in range(len(rects))]
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rects), 4), np.uint8)
        for i, (x, y, w, h) in enumerate(rects):
            ax, ay = anc[i]
            cell = np.zeros((th, tw, 4), np.uint8)
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
                    if m.mean() < 1 / 4:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    cell[r, c, :3] = pal[col]
                    cell[r, c, 3] = 255
            if not spec.get("obj"):
                cell = unrim(cell)
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, i * tw:(i + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "jhin_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"jhin_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"jhin_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (rig_jhin.py)
A_CAST = (19, -21)          # Whisper raised in attack 2
A_MUZZLE = (30, -7)         # Whisper's muzzle in attack 3 (the shot)
A4_MUZZLE = (35, -8)        # the fourth shot's muzzle (attack4 4)
Q_FIST = (10, -10)          # the gold fist in Q 3
W_MUZZLE = (39, -9)         # the cane-rifle's muzzle in W 7
R_MUZZLE = (39, -8)         # the cannon's muzzle in ult_shot 1 (and the aim)
RELOAD = (-2, -36)          # 3 px over the hood (the idle's top -29), over the head's middle
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # the ground under a unit (its soles' row)
EMPTY = "empty"             # a frame with nothing in it (the bullets' first tick)


def seq(frames, ms):
    return list(zip(frames, ms))


def flight(n, ms, total):
    """An empty first tick, then n frames of ms looped over `total` ms (twice a bullet's straight flight: homing shots
    chase), the last held a second (a `repeat: false` view must not run out mid-flight; champion-data.md)."""
    k = max(1, math.ceil(total / ms))
    return [(EMPTY, 17)] + seq([i % n for i in range(k)], [ms] * (k - 1) + [1000])


ROOT_MS = 100 * 1000 // 60 - 110 - 180      # the root's 100 ticks after the vines rise (110 ms) and fade (180 ms)
BLOOM_MS = 120 * 1000 // 60 - 3 * 60 - 140  # the bloom's 120 ticks after it opens (3 x 60 ms) and curls (2 x 70 ms)
FX = {
    # the bullets: the attack 55 px at 7 / 8 px a tick, W 220 px at 16, R 240 px at 20
    "a_bolt": [("a_bolt", flight(4, 50, 320), [(0, 0)])],
    "a4_bolt": [("a4_bolt", flight(4, 50, 280), [(0, 0)])],
    "w_shot": [("w_shot", flight(4, 50, 300), [(0, 0)])],
    "r_bullet": [("r_bullet", flight(4, 50, 300), [(0, 0)])],
    "q_nade": [("q_nade", seq(range(4), [60] * 4), [(0, 0)])],
    "e_seed": [("e_seed", seq([0, 1, 2, 3, 0, 1], [50] * 6), [(0, 0)])],
    "a_cast": [("a_cast", seq(range(4), [30, 40, 50, 60]), [A_CAST])],
    "a_muzzle": [("a_muzzle", seq(range(4), [40, 50, 60, 70]), [A_MUZZLE])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "a4_muzzle": [("a4_muzzle", seq(range(5), [40, 50, 60, 70, 80]), [A4_MUZZLE])],
    "a4_hit": [("a4_hit", seq(range(5), [40, 50, 60, 80, 100]), [HIT])],
    # the reload: 130 ticks (2167 ms): a bullet lit each ~0.5 s, the flash at the end
    "a_reload": [("a_reload", seq(range(8), [250, 120, 380, 120, 500, 500, 120, 177]), [RELOAD])],
    "q_throw": [("q_throw", seq(range(4), [40, 50, 60, 70]), [Q_FIST])],
    "q_boom": [("q_boom", seq(range(5), [40, 50, 60, 80, 100]), [HIT])],
    # a hop: the grenade drops onto the next unit (6 ticks, 100 ms) and q_boom plays there as it lands
    "q_drop": [("q_drop", seq(range(4), [25, 25, 25, 25]), [(0, -6)])],     # lands on the hit spot
    "w_muzzle": [("w_muzzle", seq(range(5), [40, 50, 60, 70, 80]), [W_MUZZLE])],
    "w_hit": [("w_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "w_root": [("w_root", seq([0, 1] + [2, 3, 4, 5] * 3, [50, 60] + [ROOT_MS // 12] * 12) + seq([6, 7], [80, 100]),
                [FEET])],
    "e_land": [("e_land", seq(range(8), [50, 60, 70, 100, 120, 150, 200, 250]), [SOLES])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_deploy": [("r_deploy", seq(range(8), [40, 60, 70, 80, 90, 100, 110, 120]), [FEET])],
    "r_muzzle": [("r_muzzle", seq(range(5), [40, 50, 60, 70, 80]), [R_MUZZLE])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "r_crit": [("r_crit", seq(range(6), [40, 50, 60, 80, 100, 120]), [HIT])],
    "e_slowed": [("slowed", seq(range(4), [100] * 4), [FEET])],
    "r_slowed": [("slowed", seq(range(4, 8), [100] * 4), [FEET])],
}
BIG = {
    "e_bloom": [("e_bloom", seq([0, 1, 2] + [3, 4, 5, 6, 7] * 4, [60, 60, 60] + [BLOOM_MS // 20] * 20)
                 + seq([8, 9], [70, 70]), [FEET])],
    "e_boom": [("e_boom", seq(range(7), [40, 60, 70, 80, 90, 100, 120]), [FEET])],
}


def place(cell, anchor_px, spots):
    """The cell with its anchor on every spot (from the pivot), as one frame centred on the pivot."""
    ax, ay = anchor_px
    h, w = cell.shape[:2]
    xs = [int(round(sx - ax)) for sx, _ in spots]
    ys = [int(round(sy - ay)) for _, sy in spots]
    u0, r0 = min(xs), min(ys)
    canvas = np.zeros((max(ys) - r0 + h, max(xs) - u0 + w, 4), np.uint8)
    for x, y in zip(xs, ys):
        sub = canvas[y - r0:y - r0 + h, x - u0:x - u0 + w]
        m = cell[..., 3] > 0
        sub[m] = cell[m]
    return G.centre_frame(canvas, u0, r0)


def build(table):
    with open(G.lp(os.path.join(SRC, "jhin_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                out[tag].append((place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_jhin_fx", FX), ("league_jhin_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

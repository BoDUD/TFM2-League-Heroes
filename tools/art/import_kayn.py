#!/usr/bin/env python3
"""Import Kayn's effects (assets/source/kayn/PROMPTS_FX.md: 23 sheets drawn, 8 recoloured) as the game sheet
league_kayn_fx.

    python tools/art/import_kayn.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_kayn.py --wall <kayn-wall-fx folder>      # once: the Shadow Step's wall strips (PROMPTS_WALL.md)
    python tools/art/import_kayn.py                                   # native strips -> the effect sheet

The body comes from tools/art/import_native.py. --raw turns each frame of Codex's image-model drafts (every frame's
cell in manifest.json, `assets[].frames[].rect` = [x, y, w, h]) into a cell of a native strip
(assets/source/kayn/kayn_fx_<name>.png, 8x, plus kayn_fx_anchors.json) the way tools/art/import_jhin.py does: each
game pixel the majority colour of the source pixels it covers, opaque when a quarter of them are solid (alpha 100 and
up), every colour snapped to the ramps the pack gave that effect (BASE: his shadow violet to crimson, EDGE: the base Q's
cyan blade light, DARKIN: Rhaast's blood red to gold, SHADOW: the Shadow Assassin's indigo to pale cyan, SMOKE), then
the ring comes off the glows (an edge pixel in a ramp's darkest shade goes when two lighter neighbours hold the shape,
else it takes the next shade). One scale per strip: `size` game px over the drawings' widest (w), tallest (h) or
larger side (m), the pack's sizes (the transformations, drawn as narrow pillars, get a width and a height of their own,
46 x 60, so the flames and tendrils stand beside his body instead of on it; the shadow step and the slow, drawn under
the feet, a size up so they show past his legs and Rhaast); W's three slashes are the lines' lengths (62000 / 80000 = 62 / 80 px) and are made
exactly symmetric about their middle row (the game turns them with the cast and flips them cast leftward).
The forms' copies of four base effects are recoloured step for step (RECOLOUR): hit, q_spin, w_wind and r_mark in the
Darkin's and the Shadow Assassin's ramps.
Anchors (source pixels): the hits and bursts on a frame's white core; the transformations, the auras, the shadow
step and the slow on their ground ring; Q's spin on its ellipse's middle; the dash and dive trails on their front
(right) end; the W slashes on their middle (a LineRangeProjectile's picture is centred on the line); W's charge on
its star; R's mark and the swallow on their middle; W's rising slash and the shadow step's pool on their foot (the
step's smoke trails out behind him, past Rhaast).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (60 ticks a second). Writes league/effects/league_kayn_fx.
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

SRC = os.path.join(ROOT, "assets", "source", "kayn")
MOD = os.path.join(ROOT, "league")
Z = 8

RAMPS = {   # light to dark, as the pack gave them (work/ka/fx_pack_ka.py)
    "BASE": ["FFFFFF", "FFC2CC", "FF4058", "D61C39", "8E1834", "46205E", "22163A"],
    "EDGE": ["D6EFFF", "3FE9FC", "1BAEC3", "2165BD"],
    "DARKIN": ["FFFFFF", "FFEF9A", "F7D48E", "ECA173", "F74508", "C03233", "9C2429", "571E21"],
    "SHADOW": ["FFFFFF", "D6F7FF", "8EE3F7", "3FE9FC", "73ABEC", "3C2EBA", "31209C", "2E1E57"],
    "SMOKE": ["9A8EC8", "6A5C9E", "463A74", "2C2250", "181030"],
}
# a ramp's darkest shade at a glow's edge -> the next shade
RIM = {"22163A": "46205E", "2165BD": "1BAEC3", "571E21": "9C2429", "2E1E57": "31209C", "181030": "2C2250"}
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps, mirror (symmetric about the middle row)
RAW = {
    "hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="BASE"),
    "sa_hit": dict(n=5, size=18, measure="m", anchor=("fixed", "core", 2), ramps="SHADOW SMOKE"),
    "tf_d": dict(n=8, size=(46, 60), anchor=("fixed", "ring", 3), ramps="DARKIN"),
    "tf_s": dict(n=8, size=(46, 60), anchor=("fixed", "ring", 3), ramps="SHADOW SMOKE"),
    "form_d": dict(n=6, size=36, measure="w", anchor=("fixed", "ring", 0), ramps="DARKIN"),
    "form_s": dict(n=6, size=36, measure="w", anchor=("fixed", "ring", 0), ramps="SHADOW SMOKE"),
    "q_dash": dict(n=4, size=36, measure="w", anchor=("fixed", "right", 0), ramps="SMOKE BASE"),
    "q_spin": dict(n=5, size=52, measure="w", anchor=("fixed", "box", 2), ramps="BASE EDGE"),
    "q_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="BASE EDGE"),
    "q_d_hit": dict(n=5, size=20, measure="m", anchor=("fixed", "core", 2), ramps="DARKIN"),
    "ghost": dict(n=4, size=40, measure="w", anchor=("fixed", "low", 0), ramps="SMOKE BASE"),
    "w_wind": dict(n=6, size=24, measure="m", anchor=("fixed", "core", 5), ramps="BASE"),
    "w_line": dict(n=5, size=62, measure="w", anchor=("fixed", "box", 2), ramps="BASE SMOKE", mirror=True),
    "w_line_d": dict(n=5, size=62, measure="w", anchor=("fixed", "box", 2), ramps="DARKIN", mirror=True),
    "w_line_s": dict(n=5, size=80, measure="w", anchor=("fixed", "box", 2), ramps="SHADOW SMOKE", mirror=True),
    "w_hit": dict(n=4, size=18, measure="h", anchor=("fixed", "low", 1), ramps="BASE"),
    "w_slow": dict(n=4, size=26, measure="w", anchor=("fixed", "box", 0), ramps="SMOKE BASE"),
    "r_dive": dict(n=4, size=36, measure="w", anchor=("fixed", "right", 0), ramps="SMOKE BASE"),
    "r_enter": dict(n=5, size=24, measure="m", anchor=("fixed", "box", 0), ramps="SMOKE BASE"),
    "r_mark": dict(n=4, size=16, measure="m", anchor=("fixed", "box", 0), ramps="BASE SMOKE"),
    "r_exit": dict(n=6, size=36, measure="m", anchor=("fixed", "core", 2), ramps="SMOKE BASE"),
    "r_exit_d": dict(n=6, size=36, measure="m", anchor=("fixed", "core", 2), ramps="DARKIN"),
    "r_exit_s": dict(n=6, size=36, measure="m", anchor=("fixed", "core", 2), ramps="SHADOW SMOKE"),
}
# the forms' copies: the base strip's colours moved to the form's ramp, step for step (BASE light to dark; EDGE, the
# base Q's cyan blade light, to the form's light end; SMOKE: the Darkin's swirl in dark reds, the Shadow keeps it)
TO_DARKIN = dict(zip(RAMPS["BASE"], ["FFFFFF", "F7D48E", "F74508", "C03233", "9C2429", "571E21", "571E21"]))
TO_DARKIN.update(zip(RAMPS["EDGE"], ["FFEF9A", "F7D48E", "ECA173", "F74508"]))
TO_DARKIN.update(zip(RAMPS["SMOKE"], ["C03233", "9C2429", "9C2429", "571E21", "571E21"]))
TO_SHADOW = dict(zip(RAMPS["BASE"], ["FFFFFF", "D6F7FF", "8EE3F7", "73ABEC", "3C2EBA", "31209C", "2E1E57"]))
TO_SHADOW.update(zip(RAMPS["EDGE"], ["D6F7FF", "3FE9FC", "73ABEC", "3C2EBA"]))
TO_SHADOW.update({c: c for c in RAMPS["SMOKE"]})
RECOLOUR = {"hit_d": ("hit", TO_DARKIN), "hit_s": ("hit", TO_SHADOW), "q_spin_d": ("q_spin", TO_DARKIN),
            "q_spin_s": ("q_spin", TO_SHADOW), "w_wind_d": ("w_wind", TO_DARKIN), "w_wind_s": ("w_wind", TO_SHADOW),
            "r_mark_d": ("r_mark", TO_DARKIN), "r_mark_s": ("r_mark", TO_SHADOW)}


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
    """The cell made symmetric about its middle row U: the upper half copied down."""
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
    if how[0] == "at":                     # a set point in the cell (x, y from its corner)
        return x + how[1], y + how[2]
    if how == "cell":
        return x + w / 2, y + h / 2
    if how[0] == "fixed":                  # frame j's anchor, the same spot in every cell
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    s = solid[y:y + h, x:x + w]
    ys, xs = np.nonzero(s)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    if how == "box":                       # the drawing's middle
        return x + (x0 + x1) / 2, y + (y0 + y1) / 2
    if how == "core":                      # the white flash's middle
        by, bx = np.nonzero(bright(a[y:y + h, x:x + w]))
        if len(bx) < 20:
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + bx.mean() + 0.5, y + by.mean() + 0.5
    if how == "ring":                      # the ring's middle: the lower 40% of the drawing
        low = s.copy()
        low[:int(y1 - 0.4 * (y1 - y0))] = False
        ly, lx = np.nonzero(low)
        return x + (lx.min() + lx.max() + 1) / 2, y + (ly.min() + ly.max() + 1) / 2
    if how == "right":                     # a trail's front: its right end, halfway down the rightmost tenth
        band = s[:, max(x0, int(x1 - 0.1 * (x1 - x0))):x1]
        by = np.nonzero(band.any(1))[0]
        return x + x1, y + (by.min() + by.max() + 1) / 2
    if how == "low":                       # a slash rising from the ground: the middle of its lowest row
        lx = np.nonzero(s[y1 - 1])[0]
        return x + (lx.min() + lx.max() + 1) / 2, y + y1
    raise ValueError(how)


def convert(name, spec, a, rects):
    """One raw strip (RGBA a, frame rects [x, y, w, h]) to a native strip at Z x, written as kayn_fx_<name>.png;
    its anchors entry."""
    fn = f"kayn_fx_{name}.png"
    hexes_, pal = palette(spec["ramps"])
    solid = a[..., 3] >= 100
    if len(rects) != spec["n"]:
        sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
    idx = snap(a, solid, pal)
    boxes = []
    for x, y, w, h in rects:
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
    ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
    ext["m"] = max(ext["w"], ext["h"])
    if isinstance(spec["size"], tuple):    # a width and a height of their own (the transformations)
        sx, sy = spec["size"][0] / ext["w"], spec["size"][1] / ext["h"]
    else:
        sx = sy = spec["size"] / ext[spec["measure"]]
    anc = [anchor(spec["anchor"], k, a, solid, rects) for k in range(len(rects))]
    L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes)) * sx - 0.5), 0) + 1
    U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * sy - 0.5), 0) + 1
    tw, th = 2 * L + 1, 2 * U + 1
    out = np.zeros((th, tw * len(rects), 4), np.uint8)
    for i, (x, y, w, h) in enumerate(rects):
        ax, ay = anc[i]
        cell = np.zeros((th, tw, 4), np.uint8)
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
                if m.mean() < 1 / 4:
                    continue
                col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                cell[r, c, :3] = pal[col]
                cell[r, c, 3] = 255
        cell = unrim(cell)
        if spec.get("mirror"):
            cell = mirror(cell, U)
        if spec.get("hmirror"):
            cell = hmirror(cell, L)
        out[:, i * tw:(i + 1) * tw] = cell
    Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
    print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {sx:.4f} x {sy:.4f} (size {spec['size']}"
          f" over {ext['w']} x {ext['h']}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    return {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}


def recolour(name, base, table, anchors):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"kayn_fx_{base}.png"))).convert("RGBA")).copy()
    op = a[..., 3] > 0
    hx = hexes(a)
    left = set(np.unique(hx[op])) - set(table)
    assert not left, f"{base}: colours outside the recolour table {sorted(left)}"
    for old, new in table.items():
        a[op & (hx == old), :3] = [int(new[i:i + 2], 16) for i in (0, 2, 4)]
    Image.fromarray(a, "RGBA").save(G.lp(os.path.join(SRC, f"kayn_fx_{name}.png")))
    anchors[name] = dict(anchors[base])
    print(f"kayn_fx_{name}.png  recoloured from {base}")


def write_anchors(anchors):
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "kayn_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def hmirror(cell, L):
    """The cell made symmetric about its middle column L: the right half copied onto the left (a picture on a unit
    that the game does not mirror by his facing, or played where he stands - the same both ways)."""
    out = cell.copy()
    for c in range(L):
        if 2 * L - c < cell.shape[1]:
            out[:, c] = cell[:, 2 * L - c]
    return out


# The Shadow Step through a wall (assets/source/kayn/PROMPTS_WALL.md; addons/league_kayn_form puts these on him while he
# stands in a wall cell, and plays the burst as he goes in and comes out). Codex's delivery (kayn_wall_fx_done.zip,
# kayn-wall-fx/): two strips of 6 cells of 256 x 256, the shroud's empty figure standing on y = 232 of its cell
# (FRAME_LAYOUT.json), the splash in the middle of its cell. Its shapes only look symmetric: made exact here (hmirror).
WALL_RAW = {
    "wall_aura": dict(n=6, size=44, measure="w", anchor=("at", 128, 232), ramps="SMOKE BASE", hmirror=True),
    "wall_burst": dict(n=6, size=40, measure="w", anchor=("at", 128, 128), ramps="SMOKE BASE", hmirror=True),
}
WALL_RECOLOUR = {"wall_aura_d": ("wall_aura", TO_DARKIN), "wall_aura_s": ("wall_aura", TO_SHADOW),
                 "wall_burst_d": ("wall_burst", TO_DARKIN), "wall_burst_s": ("wall_burst", TO_SHADOW)}


def from_wall(folder):
    """Codex's wall strips (folder: its kayn-wall-fx/) -> native strips, the forms' copies, their anchors."""
    with open(G.lp(os.path.join(SRC, "kayn_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    for name, spec in WALL_RAW.items():
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"kayn_fx_{name}.png"))).convert("RGBA")).copy()
        n, w = spec["n"], a.shape[1] // spec["n"]
        rects = [[k * w, 0, w, a.shape[0]] for k in range(n)]
        anchors[name] = convert(name, spec, a, rects)
    for name, (base, table) in WALL_RECOLOUR.items():
        recolour(name, base, table, anchors)
    write_anchors(anchors)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"kayn_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        anchors[name] = convert(name, spec, a, rects)
    for name, (base, table) in RECOLOUR.items():
        recolour(name, base, table, anchors)
    write_anchors(anchors)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"kayn_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"kayn_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down)
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # the ground under a unit (its soles' row)
WAIST = (0, -1)             # Q's spin: the ring round him at the hips
TRAIL = (0, 6)              # the dash's trail: low behind him, its front at his legs
DIVE = (0, -2)              # R's dive trail: its front at his body
OVER = (0, -36)             # over a unit's head (R's mark on the target he rides)
EYE = (31, -2)              # Rhaast's eye in W frame 1 (measured on the finished strips, 2026-10-04)
EYE_D = (41, -7)            # the Darkin scythe's eye in rh_skill2 frame 1
EYE_S = (36, -2)            # the Shadow scythe's blade root in sh_skill2 frame 1
LINE = (0, 0)               # a LineRangeProjectile's picture: centred on the line


def seq(frames, ms):
    return list(zip(frames, ms))


def loop(n, ms, total):
    """n frames of ms looped for `total` ms (a view_effects Animation plays its tag once)."""
    k = max(n, math.ceil(total / ms))
    return seq([i % n for i in range(k)], [ms] * k)


TF = [50, 60, 70, 80, 90, 100, 110, 120]           # the transformation: its 36-tick pose, then the embers
EXIT = [40, 50, 60, 80, 100, 120]
FX = {
    "hit": [("hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "hit_d": [("hit_d", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "hit_s": [("hit_s", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "sa_hit": [("sa_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "tf_d": [("tf_d", seq(range(8), TF), [FEET])],
    "tf_s": [("tf_s", seq(range(8), TF), [FEET])],
    "form_d": [("form_d", seq(range(6), [100] * 6), [FEET])],            # buff pictures loop while the form lasts
    "form_s": [("form_s", seq(range(6), [100] * 6), [FEET])],
    "q_dash": [("q_dash", seq(range(4), [40, 40, 50, 60]), [TRAIL])],     # the 8-tick dash
    "q_spin": [("q_spin", seq(range(5), [50, 60, 70, 80, 100]), [WAIST])],
    "q_spin_d": [("q_spin_d", seq(range(5), [50, 60, 70, 80, 100]), [WAIST])],
    "q_spin_s": [("q_spin_s", seq(range(5), [50, 60, 70, 80, 100]), [WAIST])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_d_hit": [("q_d_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "ghost": [("ghost", seq(range(4), [100] * 4), [SOLES])],          # the pool under his soles, the smoke behind
    "w_wind": [("w_wind", seq(range(6), [100, 100, 100, 100, 80, 70]), [EYE])],   # the 33-tick wind-up
    "w_wind_d": [("w_wind_d", seq(range(6), [100, 100, 100, 100, 80, 70]), [EYE_D])],
    "w_wind_s": [("w_wind_s", seq(range(6), [100, 100, 100, 100, 80, 70]), [EYE_S])],
    "w_line": [("w_line", seq(range(5), [50, 60, 70, 90, 110]), [LINE])],          # the line's 24 ticks
    "w_line_d": [("w_line_d", seq(range(5), [50, 60, 70, 90, 110]), [LINE])],
    "w_line_s": [("w_line_s", seq(range(5), [50, 60, 70, 90, 110]), [LINE])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [SOLES])],
    "w_slow": [("w_slow", seq(range(4), [100] * 4), [FEET])],
    "r_dive": [("r_dive", seq(range(4), [40, 50, 50, 60]), [DIVE])],            # the 12-tick dive
    "r_enter": [("r_enter", seq(range(5), [60, 70, 80, 90, 100]), [HIT])],
    "r_mark": [("r_mark", seq(range(4), [100] * 4), [OVER])],
    "r_mark_d": [("r_mark_d", seq(range(4), [100] * 4), [OVER])],
    "r_mark_s": [("r_mark_s", seq(range(4), [100] * 4), [OVER])],
    "r_exit": [("r_exit", seq(range(6), EXIT), [HIT])],
    "r_exit_d": [("r_exit_d", seq(range(6), EXIT), [HIT])],
    "r_exit_s": [("r_exit_s", seq(range(6), EXIT), [HIT])],
    # the Shadow Step through a wall (addons/league_kayn_form): the shroud loops while he is in the wall (a buff
    # picture), the splash plays once as he goes in and as he comes out
    **{f"wall_aura{f}": [(f"wall_aura{f}", seq(range(6), [100] * 6), [SOLES])] for f in ("", "_d", "_s")},
    **{f"wall_burst{f}": [(f"wall_burst{f}", seq(range(6), [40, 50, 60, 70, 80, 90]), [FEET])] for f in ("", "_d", "_s")},
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


def _rgba(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


def shadow_step(k, pool, anchor):
    """The Shadow Step picture (the 2 s after Q's spin, walking through walls), frame k of 6: Codex's pool under his
    soles made symmetric about its anchor (its smoke trailed out behind him - a buff picture is not mirrored on the red
    side, so behind became ahead), and dark flames rising beside his body, two on each side, drawn for the right side
    and mirrored (exactly symmetric). The user: 「穿墙也要加特效」 - the pool alone hardly showed past his legs; drawn
    under him (z -1) the flames still show beside his body. Pivot-centred, like place()."""
    L, T, W, H = -30, -40, 61, 52                     # the canvas from the pivot: x -30..30, y -40..11
    can = np.zeros((H, W, 4), np.uint8)
    ax, ay = anchor
    # the pool, mirrored onto itself about its anchor column, its anchor on the soles' row (SOLES)
    p = pool.copy()
    mir = np.zeros_like(p)
    for x in range(p.shape[1]):
        mx = 2 * ax - x
        if 0 <= mx < p.shape[1]:
            mir[:, mx] = p[:, x]
    p = np.where(p[..., 3:4] > 0, p, mir)
    ox, oy = SOLES[0] - ax - L, SOLES[1] - ay - T
    for y, x in zip(*np.nonzero(p[..., 3])):
        if 0 <= y + oy < H and 0 <= x + ox < W:
            can[y + oy, x + ox] = p[y, x]
    # the flames: (base column from the pivot, height in rows, phase)
    shades = [_rgba(h) for h in RAMPS["SMOKE"][::-1]]   # dark to light
    ember = _rgba(RAMPS["BASE"][2])
    for bx, height, ph in ((11, 36, 0.0), (15, 26, 2.1)):
        for r in range(height):
            y = SOLES[1] - 1 - r
            t = r / height                                # 0 at the ground, 1 at the tip
            wob = int(round(1.6 * math.sin(r / 3.2 + ph - k * 1.05)))
            x = bx + wob
            width = 3 if t < 0.35 else 2 if t < 0.8 else 1
            if t > 0.6 and (r + k * 3 + int(ph * 7)) % 5 == 0:
                continue                                  # the top breaks up as it rises
            shade = shades[min(len(shades) - 1, int(t * (len(shades) - 1)) + (1 if (r + k) % 6 == 0 else 0))]
            for dx in range(width):
                for side in (1, -1):
                    cx = side * (x + dx) - L
                    if 0 <= y - T < H and 0 <= cx < W:
                        can[y - T, cx] = shade
        for r in (height // 3, (2 * height) // 3):         # an ember rising with the phase
            y = SOLES[1] - 1 - ((r + k * 4) % height)
            x = bx + 1 + int(round(1.6 * math.sin(r / 3.2 + ph)))
            for side in (1, -1):
                cx = side * x - L
                if 0 <= y - T < H and 0 <= cx < W:
                    can[y - T, cx] = ember
    # exactly symmetric about the pivot column: the right half (with whatever the left alone had) mirrored left
    can = np.where(can[..., 3:4] > 0, can, can[:, ::-1])
    can[:, :-L] = can[:, -L + 1:][:, ::-1]
    return G.centre_frame(can, L, T)


def build(table):
    with open(G.lp(os.path.join(SRC, "kayn_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                out[tag].append((place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--wall", help="Codex's wall delivery (kayn-wall-fx/): rebuild the wall strips from it first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    if args.wall:
        from_wall(args.wall)
    tags = build(FX)
    with open(G.lp(os.path.join(SRC, "kayn_fx_anchors.json")), encoding="utf-8") as f:
        ga = json.load(f)["ghost"]
    pools = cells("ghost", ga["frames"])
    tags["ghost"] = [(shadow_step(k, pools[k % len(pools)], ga["anchor"]), 100) for k in range(6)]
    w, h = G.write_sheet(os.path.join(MOD, "effects", "league_kayn_fx"), tags)
    print(f"league/effects/league_kayn_fx#sheet.png {w}x{h}: " + ", ".join(
        f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

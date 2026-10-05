#!/usr/bin/env python3
"""Import Alistar's effects (assets/source/alistar/PROMPTS_FX.md, 15 sheets) as the game sheets league_alistar_fx and
league_alistar_big.

    python tools/art/import_alistar.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_alistar.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/fix_alistar_strips.py built the strips). --raw turns each frame of
Codex's drawings (generated, one row each, soft edges) into a cell of a native strip
(assets/source/alistar/alistar_fx_<name>.png, 8x, plus alistar_fx_anchors.json) the way import_lissandra.py does: the
frames are the drawing's pieces split at its empty columns when there are exactly as many as frames, else its n equal
columns; each game pixel the majority colour of the source pixels it covers, opaque when a quarter of them are solid,
every colour snapped to the ramps the pack gave that effect (DUST, ROCK, CRACK, FLASH, RAGE, HEAL, STAR, IRON and the
INK outline of the rocks and chain links), then the light's darkest-shade ring comes off (import_jhin.unrim). One scale
per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m) - or (w, h) scaled apart (wh).
Anchors (source pixels): the hits on their white flash, the headbutt's burst on its left end, the rings on the ground
on the ring's widest row, the pictures round him on the figure's feet where the pack placed them (`feet`: a fraction
of the cell's width from the left, squares over its bottom out of the cell's height in squares).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11
under the pivot) measured on the finished strips: the horn tip in butt 1 (38, -33), over the idle's head (6, -38) -
and times it by the kit (work/al/build_alistar.py, 60 ticks a second).
Writes league/effects/league_alistar_fx and league_alistar_big.
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
import import_jhin as J  # noqa: E402
import import_twistedfate as TF  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "alistar")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (work/al/fx_pack_al.py)
RAMPS = {
    "DUST": ["6A4A2C", "9A7448", "C8A46E", "EAD2A2", "FFF4DC"],
    "ROCK": ["563820", "8A5E34", "C08E58", "F0D4A0"],
    "CRACK": ["CCC6E8", "F2EEFF", "FFFFFF"],
    "FLASH": ["E06A10", "FFA830", "FFD870", "FFF6C8", "FFFFFF"],
    "RAGE": ["B01E18", "F04A20", "FF9A40", "FFE0A0", "FFFFFF"],
    "HEAL": ["1A8A3A", "3CC850", "8CF078", "D8FFD0", "FFFFFF"],
    "STAR": ["E89A10", "FFD23C", "FFF4A0", "FFFFFF"],
    "IRON": ["2A2730", "4A4652", "8A848E", "C8C4CC"],
    "INK": ["140A20"],                         # the rocks' and the chain links' outline
}
# the light's darkest shade on its edge goes (or takes the next); rocks and iron keep their darks
RIM = {"6A4A2C": "9A7448", "E06A10": "FFA830", "B01E18": "F04A20", "1A8A3A": "3CC850", "E89A10": "FFD23C",
       "CCC6E8": "F2EEFF"}


def feet(fx, up, ch):
    """The figure's feet: fx of the cell's width from the left, `up` squares over the bottom of a `ch`-square cell."""
    return ("feet", fx, up, ch)


# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="FLASH DUST"),
    "q_slam": dict(n=6, size=64, measure="w", anchor=("fixed", "ellipse", 3), ramps="INK ROCK CRACK DUST FLASH"),
    "q_up": dict(n=5, size=22, measure="h", anchor=feet(0.5, 4, 44), ramps="INK ROCK DUST CRACK"),
    "w_dash": dict(n=6, size=36, measure="w", anchor=feet(38 / 64, 4, 40), ramps="DUST CRACK"),
    "w_butt": dict(n=4, size=20, measure="w", anchor="left", ramps="FLASH"),
    "w_hit": dict(n=4, size=16, measure="m", anchor="core", ramps="FLASH"),
    "e_stomp": dict(n=4, size=52, measure="w", anchor=("fixed", "ellipse", 2), ramps="INK ROCK DUST"),
    "e_hit": dict(n=3, size=10, measure="m", anchor="core", ramps="DUST FLASH"),
    "e_ready": dict(n=5, size=18, measure="w", anchor="box", ramps="INK IRON STAR"),
    "e_hit_stun": dict(n=5, size=20, measure="m", anchor="core", ramps="INK IRON FLASH"),
    "e_stun": dict(n=8, size=18, measure="w", anchor="box", ramps="STAR"),
    "p_roar": dict(n=6, size=48, measure="w", anchor=feet(0.5, 8, 40), ramps="HEAL"),
    "p_heal": dict(n=5, size=18, measure="h", anchor="box", ramps="HEAL"),
    "r_cast": dict(n=6, size=56, measure="h", anchor=feet(0.5, 8, 48), ramps="RAGE CRACK"),
    # Codex drew the aura as a tall narrow arch (2.7 times taller than wide): scaled to 56 x 54 instead, so its hollow
    # clears his 41 columns and the flames stand round all of him (the kit draws it behind him)
    "r_on": dict(n=6, size=(56, 54), measure="wh", anchor=feet(0.5, 8, 50), ramps="RAGE"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def unrim(a):
    J.RIM = RIM
    return J.unrim(a)


def rects_of(a, solid, n):
    """The frames: the drawing's pieces between empty columns when there are exactly n of them (Codex's cells are
    not always equal), else its n equal columns (full height)."""
    H, W = a.shape[:2]
    cols = solid.any(0)
    runs, x = [], 0
    while x < W:
        if cols[x]:
            x0 = x
            while x < W and cols[x]:
                x += 1
            runs.append([x0, x])
        x += 1
    # pieces closer than 1% of the width belong together (a flash's stray sparks)
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < W * 0.01:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    if len(merged) == n:
        edges = [0] + [(merged[k][1] + merged[k + 1][0]) // 2 for k in range(n - 1)] + [W]
        return [[edges[k], 0, edges[k + 1] - edges[k], H] for k in range(n)]
    return [[round(k * W / n), 0, round((k + 1) * W / n) - round(k * W / n), H] for k in range(n)]


def anchor(how, k, a, solid, rects, s):
    if isinstance(how, tuple) and how[0] == "feet":
        _, fx, up, ch = how
        x, y, w, h = rects[k]
        return x + w * fx, y + h - h * up / ch
    return TF.anchor(how, k, a, solid, rects, s)


def from_raw(folder):
    anchors = {}
    for name, spec in RAW.items():
        fn = f"alistar_fx_{name}.png"
        path = os.path.join(folder, fn)
        if not os.path.exists(G.lp(path)):
            path = os.path.join(folder, "raw", fn)
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(path)).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = rects_of(a, solid, spec["n"])
        idx = J.snap(a, solid, pal)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        if spec["measure"] == "wh":
            sx, sy = spec["size"][0] / ext["w"], spec["size"][1] / ext["h"]
        else:
            sx = sy = spec["size"] / ext[spec["measure"]]
        s = sx
        anc = [anchor(spec["anchor"], k, a, solid, rects, s) for k in range(len(rects))]
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
            out[:, i * tw:(i + 1) * tw] = unrim(cell)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {sx:.4f} x {sy:.4f} ({spec['size']} px), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "alistar_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"alistar_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"alistar_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips
HORN = (38, -33)            # the horn tip in butt 1 (the headbutt landing)
OVER_HEAD = (6, -38)        # over the idle's head (its top 32 over the pivot)
STUN = (0, -30)             # over a struck unit's head (36-44 px units)
HIT = (0, -10)              # a hit on the upper body
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # a picture standing round a figure: the figure's feet on the soles
seq = J.seq

FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_up": [("q_up", seq(range(5), [50, 70, 90, 110, 130]), [SOLES])],
    "w_butt": [("w_butt", seq(range(4), [40, 50, 60, 70]), [HORN])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(3), [40, 60, 80]), [HIT])],
    "e_ready": [("e_ready", seq(range(5), [60, 80, 100, 120, 140]), [OVER_HEAD])],
    "e_hit_stun": [("e_hit_stun", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "e_stun": [("e_stun", seq(range(8), [100] * 8), [STUN])],          # a buff: loops while the stun lasts
    "p_heal": [("p_heal", seq(range(5), [80, 100, 120, 140, 160]), [HIT])],
}
BIG = {
    "q_slam": [("q_slam", seq(range(6), [50, 60, 70, 80, 90, 110]), [FEET])],
    "w_slam": [("q_slam", seq(range(6), [50, 60, 70, 80, 90, 110]), [FEET])],
    "w_dash": [("w_dash", seq(range(6), [70] * 6), [SOLES])],
    "e_stomp": [("e_stomp", seq(range(4), [60, 70, 80, 90]), [FEET])],
    "p_roar": [("p_roar", seq(range(6), [60, 70, 80, 90, 100, 110]), [SOLES])],
    "r_cast": [("r_cast", seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES])],
    "r_on": [("r_on", seq(range(6), [120] * 6), [SOLES])],                # a buff: loops for the 7 s
}


def build(table):
    with open(G.lp(os.path.join(SRC, "alistar_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                out[tag].append((J.place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_alistar_fx", FX), ("league_alistar_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

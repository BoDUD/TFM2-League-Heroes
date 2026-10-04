#!/usr/bin/env python3
"""Import Sivir's effects (assets/source/sivir/PROMPTS_FX.md, 16 sheets) as the game sheets league_sivir_fx and
league_sivir_big.

    python tools/art/import_sivir.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_sivir.py                                   # native strips -> the effect sheets

The body comes from import_native.py (work/sv/fix_strips_sv.py built the strips). --raw turns each frame of Codex's
drawings (every frame's cell in manifest.json, `assets[].frames[].rect` = [x, y, w, h]; the two three-phase sheets read
row by row: appear, hold, go) into a cell of a native strip (assets/source/sivir/sivir_fx_<name>.png, 8x, plus
sivir_fx_anchors.json) the way import_jhin.py does: each game pixel the majority colour of the source pixels it covers,
opaque when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect (GOLD, TEAL, SHIELD,
CYAN; the crossblade's outline on the four flying blades), then the ring comes off the glows (an edge pixel in a ramp's
darkest shade goes when two lighter neighbours hold the shape, else it takes the next shade) - not off the blades,
whose outline is drawn. One scale per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side
(m), the pack's sizes.
Anchors (source pixels, the same spot in every cell unless the drawing moves): the blades, the auras and the glints on
their cell's middle (the pack asked for them centred); the hits on a frame's white flash; the shield bubble, the war
cry's ring and the hunt's ring on the box of their full-size frame.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot), measured on the rigged strips (tools/art/rig_sivir.py, the small crossblade's ring): the blade leaving her
near hand in attack 3 (27, -14), the near hand that throws Q in skill 4 (23, -12), the blade she catches in the raised
near hand in skill_catch 1 (22, -22), the blade at her back hip when W starts in attack 1 (-17, -8), her chest (3, -10)
- and times it by the
kit (60 ticks a second): the flying blades start with empty ticks (a projectile's first move points its picture up,
import_lucian.py's RAY_SKIP; and it leaves her pivot, so the blade stays unseen until it is past her hand) and loop
their frames over their longest flight; the shield holds up to e_cap (180 ticks); the hunt's ring loops for its 8 s.
Writes league/effects/league_sivir_fx and league_sivir_big (Q's blade, the shield, the war cry).
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

SRC = os.path.join(ROOT, "assets", "source", "sivir")
MOD = os.path.join(ROOT, "league")
Z = 8

RAMPS = {
    "GOLD": ["A8641A", "E8A830", "FFD45E", "FFF3C4", "FFFFFF"],
    "TEAL": ["137A70", "2CC4B0", "7EF2DC", "D6FFF6", "FFFFFF"],
    "SHIELD": ["3A2E9E", "5A6CF0", "8FB4FF", "DCE8FF", "FFFFFF"],
    "CYAN": ["1A4E9E", "2E9EE8", "7FE0FF", "D8F8FF", "FFFFFF"],
    "BLADE": ["14101A"],                       # the crossblade's outline (her sprite's)
}
RIM = {"A8641A": "E8A830", "137A70": "2CC4B0", "3A2E9E": "5A6CF0", "1A4E9E": "2E9EE8"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps, obj (keeps its outline); the flying blades
# a size over the pack's (10 / 12 / 20): at 10 the spinning drawing was a blur; Q's blade (22 at first) the size of
# the crossblade in her hand since it was made smaller (16 x 16, rig_sivir.SMALL_BLADE): she catches what she threw
RAW = {
    "a_blade": dict(n=4, size=13, measure="m", anchor="cell", ramps="BLADE GOLD TEAL", obj=True),
    "w_blade": dict(n=4, size=15, measure="m", anchor="cell", ramps="BLADE GOLD TEAL", obj=True),
    "a_hit": dict(n=4, size=10, measure="m", anchor="cell", ramps="GOLD TEAL"),
    "w_cast": dict(n=5, size=16, measure="m", anchor="cell", ramps="TEAL GOLD"),
    "w_on": dict(n=4, size=18, measure="w", anchor="cell", ramps="TEAL"),
    "w_bounce": dict(n=4, size=16, measure="m", anchor="cell", ramps="BLADE GOLD TEAL", obj=True),
    "w_hit": dict(n=4, size=12, measure="m", anchor="cell", ramps="TEAL GOLD"),
    "q_blade": dict(n=4, size=16, measure="m", anchor="cell", ramps="BLADE GOLD TEAL", obj=True),
    "q_throw": dict(n=4, size=12, measure="m", anchor="cell", ramps="GOLD TEAL"),
    "q_hit": dict(n=5, size=16, measure="m", anchor="cell", ramps="GOLD TEAL"),
    "q_catch": dict(n=4, size=14, measure="m", anchor="cell", ramps="GOLD TEAL"),
    "e_shroud": dict(n=12, size=46, measure="w", anchor=("fixed", "box", 4), ramps="SHIELD CYAN"),
    "e_block": dict(n=5, size=24, measure="m", anchor="cell", ramps="SHIELD CYAN"),
    "r_cast": dict(n=6, size=64, measure="w", anchor=("fixed", "box", 4), ramps="CYAN"),
    "r_hunt": dict(n=12, size=26, measure="w", anchor=("fixed", "box", 4), ramps="CYAN"),
    "r_renew": dict(n=5, size=22, measure="m", anchor="cell", ramps="CYAN GOLD"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def unrim(a):
    J.RIM = RIM
    return J.unrim(a)


def anchor(how, k, a, solid, rects):
    """(x, y) of frame k's anchor in the source: import_jhin's, plus `box` (the middle of the drawing's box)."""
    if how == "box":
        x, y, w, h = rects[k]
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        return x + (xs.min() + xs.max() + 1) / 2, y + (ys.min() + ys.max() + 1) / 2
    if isinstance(how, tuple) and how[0] == "fixed":
        x, y, _, _ = rects[k]
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    return J.anchor(how, k, a, solid, rects)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"sivir_fx_{name}.png"
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        idx = J.snap(a, solid, pal)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
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
            out[:, i * tw:(i + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "sivir_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"sivir_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"sivir_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (fx_pack_sv.py's marks)
A_BLADE = (27, -14)         # the blade leaving her near hand in attack 3 (the throw)
W_HIP = (-17, -8)           # the blade at her back hip in attack 1 (W lights it as the attack starts)
Q_HAND = (23, -12)          # the near hand that throws Q in skill 4
Q_CATCH = (22, -22)         # the blade she catches in the raised near hand (skill_catch 1)
CHEST = (3, -10)            # her chest (the idle's, eyes + 9)
WAIST = (2, -4)             # W's motes round her waist
BUBBLE = (2, -9)            # the shield's middle: 20 over her soles
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
EMPTY = J.EMPTY

seq = J.seq
flight = J.flight

E_HOLD = 180 * 1000 // 60 - 4 * 50          # the shield's 180 ticks after it forms
FX = {
    # the blades: the attack 55 px at 6 px a tick (homing, so twice that); out of her hand 27 px away: 4 empty ticks
    "a_blade": [("a_blade", flight(4, 50, 400, lead=4), [(0, 0)])],
    "w_blade": [("w_blade", flight(4, 40, 600, lead=4), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_cast": [("w_cast", seq(range(5), [30, 40, 50, 60, 70]), [W_HIP])],
    "w_on": [("w_on", seq(range(4), [120] * 4), [WAIST])],
    # a bounce: the blade arrives (w_hop 5 ticks, 83 ms) and w_hit plays as it lands
    "w_bounce": [("w_bounce", seq(range(4), [20, 20, 20, 30]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_throw": [("q_throw", seq(range(4), [17, 25, 33, 42]), [Q_HAND])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_catch": [("q_catch", seq(range(4), [30, 40, 50, 60]), [Q_CATCH])],
    "e_block": [("e_block", seq(range(5), [40, 50, 70, 90, 110]), [CHEST])],
    "r_renew": [("r_renew", seq(range(5), [40, 50, 70, 90, 110]), [CHEST])],
    "r_pre": [("r_hunt", seq(range(4), [50, 60, 70, 80]), [FEET])],
    "r_loop": [("r_hunt", seq(range(4, 8), [100] * 4), [FEET])],
    "r_remove": [("r_hunt", seq(range(8, 12), [60, 70, 80, 90]), [FEET])],
}
BIG = {
    # Q: 110 px out at 6.5 px a tick (17 ticks), back at 7 (a chase: twice); out of her hand 30 px away: 4 empty ticks
    "q_out": [("q_blade", flight(4, 40, 400, lead=4), [(0, 0)])],
    "q_back": [("q_blade", seq([i % 4 for i in range(25)], [40] * 24 + [1000]), [(0, 0)])],
    "e_pre": [("e_shroud", seq(range(4), [40, 50, 50, 60]), [BUBBLE])],
    "e_loop": [("e_shroud", seq(range(4, 8), [100] * 4), [BUBBLE])],
    "e_remove": [("e_shroud", seq(range(8, 12), [50, 60, 70, 80]), [BUBBLE])],
    "r_cast": [("r_cast", seq(range(6), [40, 60, 70, 80, 90, 100]), [FEET])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "sivir_fx_anchors.json")), encoding="utf-8") as f:
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
                out[tag].append((J.place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_sivir_fx", FX), ("league_sivir_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

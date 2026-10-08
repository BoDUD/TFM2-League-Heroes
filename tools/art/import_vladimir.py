#!/usr/bin/env python3
"""Import Vladimir's effects (assets/source/vladimir/PROMPTS_FX.md, 19 sheets) as the game sheets league_vladimir_fx
and league_vladimir_big.

    python tools/art/import_vladimir.py --raw assets/source/vladimir/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_vladimir.py                                      # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_vladimir.py built the strips). --raw turns each frame of Codex's
drawings into a cell of a native strip (assets/source/vladimir/vladimir_fx_<name>.png, 8x, plus
vladimir_fx_anchors.json) the way import_xayah.py does, with the frames cut by the delivery's manifest.json rects (some
strips have frames of different widths): each game pixel the majority colour of the source pixels it covers, opaque
when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect (BLOOD, PLAGUE, HEAL),
then the light's darkest ring comes off (import_jhin.unrim). One scale per strip: `size` game px over the drawings'
widest (w), tallest (h) or larger side (m).
Anchors (source pixels): the flying bolts and orbs on their front, the hits and bursts on their white core, what sits
on the ground (the splash, the pool, the cloud, the blink, the mark's glow, the drain's strands) on the middle of its
lowest row or on its ring's widest row, the pictures round a body on the middle of their box.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (tools/kit/build_vladimir.py, 60 ticks a second).
The red side: the client never mirrors a data picture. The flying ones are turned to their flight - drawn over their
own top-bottom flip; everything on a unit or on the ground is drawn as stored whichever way he faces - drawn over its
own left-right flip (league_xayah's FLIP_TB / FLIP_LR). Every frame is centred on the pivot, so the flips are about it.
Writes league/effects/league_vladimir_fx and league_vladimir_big.
"""
import argparse
import json
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
import import_varus as V  # noqa: E402
import import_xayah as X  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vladimir")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (work/vl/fx_pack_vl.py)
RAMPS = {
    "BLOOD": ["780614", "B80A1C", "F01828", "FF5A64", "FFA8B0", "FFE0E4", "FFFFFF"],
    "PLAGUE": ["4A0A30", "7E1450", "B42870", "DC5A9C", "F59AC8", "FFD8EC", "FFFFFF"],
    "HEAL": ["FF6C84", "FF9CAC", "FFD0D8", "FFF2F4", "FFFFFF"],
}
# the light's darkest shade on its edge goes (or takes the next)
RIM = {"780614": "B80A1C", "4A0A30": "7E1450"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps (sizes: the pack's, the areas the kit's
# radii: E 32000 -> 64 px across, the pool 22000 -> 44, Hemoplague 26000 -> 52)
RAW = {
    "a_bolt": dict(n=3, size=10, measure="w", anchor="front", ramps="BLOOD"),
    "a_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="BLOOD"),
    "q_drain": dict(n=5, size=20, measure="h", anchor=("fixed", "box", 1), ramps="BLOOD"),
    "q_orb": dict(n=4, size=12, measure="w", anchor="front", ramps="BLOOD"),
    "q_rush": dict(n=4, size=16, measure="w", anchor="front", ramps="BLOOD HEAL"),
    "q_heal": dict(n=5, size=24, measure="h", anchor=("fixed", "box", 2), ramps="BLOOD HEAL"),
    "q_ready": dict(n=4, size=20, measure="w", anchor=("fixed", "ellipse", 0), ramps="BLOOD"),
    "e_charge": dict(n=4, size=30, measure="h", anchor=("fixed", "ring", 0), ramps="BLOOD"),
    "e_burst": dict(n=5, size=64, measure="w", anchor="ellipse", ramps="BLOOD"),
    "e_bolt": dict(n=3, size=10, measure="w", anchor="front", ramps="BLOOD"),
    "e_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="BLOOD"),
    "w_splash": dict(n=5, size=40, measure="w", anchor="low", ramps="BLOOD"),
    "w_pool": dict(n=6, size=44, measure="w", anchor=("fixed", "ellipse", 0), ramps="BLOOD"),
    "w_drain": dict(n=4, size=22, measure="h", anchor=("fixed", "low", 0), ramps="BLOOD"),
    "r_cloud": dict(n=7, size=52, measure="w", anchor="low", ramps="PLAGUE BLOOD"),
    "r_mark": dict(n=4, size=28, measure="h", anchor=("fixed", "low", 0), ramps="PLAGUE BLOOD"),
    "r_burst": dict(n=6, size=30, measure="h", anchor="core", ramps="PLAGUE BLOOD"),
    "r_heal": dict(n=6, size=32, measure="h", anchor="box", ramps="BLOOD HEAL"),
    "c_blink": dict(n=5, size=28, measure="h", anchor=("fixed", "low", 1), ramps="BLOOD"),
}


def anchor(how, k, a, solid, rects, s):
    return V.anchor(how, k, a, solid, rects, s)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(x["file"]): x for x in json.load(f)["assets"]}
    V.RAMPS = RAMPS
    V.RIM = RIM
    anchors = {}
    for name, spec in RAW.items():
        fn = f"vladimir_fx_{name}.png"
        hexes_, pal = V.palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = [list(fr["rect"]) for fr in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames in the manifest, {spec['n']} expected")
        out, cell, anc, s, ext = V.convert(name, spec, a, solid, idx, pal, rects)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"vladimir_fx_{name}.png")))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": len(rects)}
        print(f"vladimir_fx_{name}.png  {len(rects)} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "vladimir_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"vladimir_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"vladimir_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the rigged strips (vladimir_shots.png)
HIT = (0, -10)              # a hit on the upper body of a 36-44 px unit
CHEST = (0, -11)            # his chest (the heals)
FEET = (0, 10)              # a ring on the ground round a unit's feet
SOLES = (0, 11)             # what stands on the ground: its lowest row on the soles
GROUND = (0, 13)            # a splash or cloud on the ground: its lowest row a little in front of the soles
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the bolts: the attack 48 px at 5 a tick (homing: twice that), E's 32 px at 4.5, the orbs back up to 60 px at 4.5
    "a_bolt": [("a_bolt", flight(3, 60, 400, lead=2), [(0, 0)])],
    "e_bolt": [("e_bolt", flight(3, 60, 300, lead=1), [(0, 0)])],
    "q_orb": [("q_orb", flight(4, 60, 600, lead=1), [(0, 0)])],
    "q_rush": [("q_rush", flight(4, 60, 600, lead=1), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_drain": [("q_drain", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_heal": [("q_heal", seq(range(5), [50, 60, 70, 80, 90]), [CHEST])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_burst": [("r_burst", seq(range(6), [40, 50, 60, 80, 100, 120]), [HIT])],
    "r_heal_on": [("r_heal", seq(range(6), [50, 60, 70, 80, 90, 100]), [CHEST])],
    "c_blink": [("c_blink", seq(range(5), [40, 50, 60, 70, 80]), [SOLES])],
    # the buffs' loops
    "q1": [("q_ready", seq(range(4), [110] * 4), [FEET])],
    "e_chg": [("e_charge", seq(range(4), [100] * 4), [SOLES])],
    "w_drain": [("w_drain", seq(range(4), [100] * 4), [SOLES])],
    "r_mark": [("r_mark", seq(range(4), [110] * 4), [SOLES])],
}
BIG = {
    "e_burst": [("e_burst", seq(range(5), [40, 60, 70, 90, 110]), [SOLES])],
    "w_splash": [("w_splash", seq(range(5), [40, 50, 60, 70, 80]), [GROUND])],
    "w_in": [("w_pool", seq(range(6), [110] * 6), [SOLES])],
    "r_cloud": [("r_cloud", seq(range(7), [50, 70, 80, 90, 100, 110, 120]), [GROUND])],
}
FLIP_TB = {"a_bolt", "e_bolt", "q_orb", "q_rush"}
FLIP_LR = set(FX) - FLIP_TB | set(BIG)


def build(table):
    with open(G.lp(os.path.join(SRC, "vladimir_fx_anchors.json")), encoding="utf-8") as f:
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
                f = J.place(strip[k], anchors[src]["anchor"], spots)
                f = X.over_flip(f, "tb" if tag in FLIP_TB else "lr")
                out[tag].append((f, ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_vladimir_fx", FX), ("league_vladimir_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Import Rengar's effects (assets/source/rengar/PROMPTS_FX.md, 20 sheets) as the game sheets league_rengar_fx and
league_rengar_big.

    python tools/art/import_rengar.py --raw assets/source/rengar/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_rengar.py                                     # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_rengar.py built the strips). --raw turns each frame of Codex's
drawings into a cell of a native strip (assets/source/rengar/rengar_fx_<name>.png, 8x, plus rengar_fx_anchors.json)
the way import_vladimir.py does, the frames cut by the delivery's manifest.json rects: each game pixel the majority
colour of the source pixels it covers, opaque when a quarter of them are solid, every colour snapped to the ramps the
pack gave that effect (work/rg/fx_pack_rg.py: GOLD, FERO, BONE, DUST, SMOKE, EYE, HEAL, VOID), then the lights' darkest
ring comes off (import_jhin.unrim). One scale per strip: `size` game px over the drawings' widest (w), tallest (h) or
larger side (m); the sizes are the pack's, the roar's ring the kit's radius (w_r 22000 -> 44 px across).
Anchors (source pixels): the bola on its front, the hits on their white core, what sits on the ground (the dust, the
slam, the roar, the attack-speed ring) on its ring's widest row, the rising slash on its lowest row, the rest on the
middle of their box.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot, his crown 26 over it) and times it by the kit (tools/kit/build_rengar.py, 60 ticks a second).
The red side: the client never mirrors a data picture. The bola is turned to its flight - drawn over its own
top-bottom flip; everything on a unit or on the ground is drawn as stored whichever way he faces - drawn over its own
left-right flip (league_xayah's FLIP_TB / FLIP_LR). Every frame is centred on the pivot, so the flips are about it.
Writes league/effects/league_rengar_fx and league_rengar_big (league_khazix's anger mark reads k_meet from the first).
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

SRC = os.path.join(ROOT, "assets", "source", "rengar")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps (work/rg/fx_pack_rg.py), darkest first
RAMPS = {
    "GOLD": ["8A4208", "C86A10", "F09A1E", "FFC24A", "FFE29A", "FFF6D8", "FFFFFF"],
    "FERO": ["700A08", "B01810", "E8361E", "FF6A3A", "FFAA70", "FFE0C8", "FFFFFF"],
    "BONE": ["3E2414", "6E4220", "A86A34", "D9A060", "F6E0B6", "FFFFFF"],
    "DUST": ["7A6A54", "A8967A", "D2C2A6", "EEE6D8", "FFFFFF"],
    "SMOKE": ["3A3E60", "5A6290", "8A92B8", "B8C0DC", "E4E8F4", "FFFFFF"],
    "EYE": ["C01408", "FF3A20", "FF8A60", "FFD8C8", "FFFFFF"],
    "HEAL": ["3FB44C", "7EDD68", "BDF5A6", "ECFFE4", "FFFFFF"],
    "VOID": ["341870", "5A30A8", "8A58D8", "B890F0", "E8D8FF", "FFFFFF"],
}
# the lights' darkest shade on their edge goes (or takes the next)
RIM = {"8A4208": "C86A10", "700A08": "B01810", "C01408": "FF3A20", "3FB44C": "7EDD68"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="GOLD"),
    "l_dust": dict(n=4, size=22, measure="w", anchor=("fixed", "ellipse", 2), ramps="DUST"),
    "l_hit": dict(n=5, size=20, measure="h", anchor="core", ramps="GOLD"),
    "p_ready": dict(n=4, size=10, measure="w", anchor=("fixed", "box", 0), ramps="GOLD"),
    "f_stack": dict(n=4, size=14, measure="w", anchor=("fixed", "box", 3), ramps="FERO GOLD"),
    "q_slam": dict(n=5, size=24, measure="w", anchor=("fixed", "ellipse", 2), ramps="GOLD DUST"),
    "q_rip": dict(n=4, size=20, measure="h", anchor=("fixed", "low", 1), ramps="GOLD"),
    "q_buff": dict(n=4, size=22, measure="w", anchor=("fixed", "ellipse", 0), ramps="GOLD"),
    "q_emp": dict(n=4, size=30, measure="h", anchor=("fixed", "box", 0), ramps="FERO GOLD"),
    "w_roar": dict(n=6, size=44, measure="w", anchor=("fixed", "ellipse", 3), ramps="GOLD"),
    "w_heal": dict(n=5, size=24, measure="h", anchor=("fixed", "box", 2), ramps="HEAL"),
    "w_emp": dict(n=4, size=30, measure="h", anchor=("fixed", "box", 0), ramps="FERO GOLD"),
    "e_bola": dict(n=4, size=12, measure="w", anchor="front", ramps="BONE GOLD"),
    "e_slow": dict(n=4, size=18, measure="w", anchor=("fixed", "box", 0), ramps="BONE"),
    "e_root": dict(n=4, size=20, measure="w", anchor=("fixed", "box", 0), ramps="FERO BONE"),
    "r_smoke": dict(n=6, size=28, measure="w", anchor=("fixed", "box", 2), ramps="SMOKE"),
    "r_mark": dict(n=4, size=12, measure="w", anchor=("fixed", "box", 0), ramps="EYE"),
    "r_hit": dict(n=6, size=24, measure="h", anchor="core", ramps="FERO GOLD"),
    "t_trophy": dict(n=6, size=14, measure="h", anchor=("fixed", "low", 5), ramps="VOID GOLD BONE"),
    "k_meet": dict(n=5, size=12, measure="m", anchor=("fixed", "box", 2), ramps="FERO GOLD"),
}


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(x["file"]): x for x in json.load(f)["assets"]}
    V.RAMPS = RAMPS
    V.RIM = RIM
    anchors = {}
    for name, spec in RAW.items():
        fn = f"rengar_fx_{name}.png"
        hexes_, pal = V.palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = [list(fr["rect"]) for fr in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames in the manifest, {spec['n']} expected")
        out, cell, anc, s, ext = V.convert(name, spec, a, solid, idx, pal, rects)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "rengar_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"rengar_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"rengar_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the rigged strips (rengar_shots.png)
HIT = (0, -11)              # a hit on the upper body of a 36-44 px unit
BODY = (0, -8)              # an aura round his body
CHEST = (0, -10)            # his chest (the heal)
LEGS = (0, 6)               # the bola round a unit's legs
FEET = (0, 10)              # a ring on the ground round a unit's feet
LOW = (0, 9)                # the rising slash's foot
OVER = (0, -31)             # over his head: the Ferocity pips, the hunter's eye on a target
EYE = (0, -37)              # the passive's eye, over the pips
CROWN = (0, -29)            # what pops up from his head: its lowest row
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight


def one(k):
    """A Ferocity pip count: one frame held (the buff's view loops it)."""
    return [("f_stack", seq([k], [1000]), [OVER])]


FX = {
    # the bola: 7000 a tick (14 px) straight, 12000 homing in the leap combo
    "e_bola": [("e_bola", flight(4, 60, 500, lead=1), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "l_hit": [("l_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "l_dust": [("l_dust", seq(range(4), [50, 60, 70, 90]), [FEET])],
    "q_slam": [("q_slam", seq(range(5), [40, 50, 60, 70, 90]), [FEET])],
    "q_rip": [("q_rip", seq(range(4), [40, 50, 60, 80]), [LOW])],
    "w_heal": [("w_heal", seq(range(5), [60, 70, 80, 90, 100]), [CHEST])],
    "t_trophy": [("t_trophy", seq(range(6), [70, 80, 90, 400, 500, 300]), [CROWN])],
    "k_meet": [("k_meet", seq(range(5), [60, 70, 400, 400, 200]), [OVER])],
    # the buffs' loops
    "p_ready": [("p_ready", seq(range(4), [120] * 4), [EYE])],
    "f1": one(0), "f2": one(1), "f3": one(2), "f4": one(3),
    "q_buff": [("q_buff", seq(range(4), [100] * 4), [FEET])],
    "e_slow": [("e_slow", seq(range(4), [110] * 4), [LEGS])],
    "e_root": [("e_root", seq(range(4), [110] * 4), [LEGS])],
    "r_mark": [("r_mark", seq(range(4), [120] * 4), [OVER])],
}
BIG = {
    "w_roar": [("w_roar", seq(range(6), [40, 60, 70, 80, 90, 100]), [FEET])],
    "r_smoke": [("r_smoke", seq(range(6), [50, 70, 90, 110, 130, 150]), [BODY])],
    "r_hit": [("r_hit", seq(range(6), [40, 50, 60, 70, 80, 90]), [HIT])],
    "q_emp": [("q_emp", seq(range(4), [90] * 4), [BODY])],
    "w_emp": [("w_emp", seq(range(4), [90] * 4), [BODY])],
}
FLIP_TB = {"e_bola"}
FLIP_LR = set(FX) - FLIP_TB | set(BIG)


def build(table):
    with open(G.lp(os.path.join(SRC, "rengar_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_rengar_fx", FX), ("league_rengar_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

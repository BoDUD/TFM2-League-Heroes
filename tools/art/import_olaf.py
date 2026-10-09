#!/usr/bin/env python3
"""Import Olaf's effects (assets/source/olaf/PROMPTS_FX.md, 13 sheets) as the game sheets league_olaf_fx and
league_olaf_big.

    python tools/art/import_olaf.py --raw assets/source/olaf/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_olaf.py                                    # native strips -> the effect sheets

The body comes from import_native.py (tools/art/fix_olaf_strips.py built the strips). --raw turns each frame of
Codex's generated originals (about 2000 px wide, semi-transparent edges, the frames cut by the delivery's
manifest.json rects) into a cell of a native strip (assets/source/olaf/olaf_fx_<name>.png, 8x, plus
olaf_fx_anchors.json) the way import_rengar.py does: each game pixel the majority colour of the source pixels it
covers, opaque when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect
(work/ol/fx_pack_ol.py: ICE, RAGE, the design's AXE colours, DUST), then the lights' darkest ring comes off
(import_jhin.unrim; the axes keep their outline). One scale per strip: `size` game px over the drawings' widest (w),
tallest (h) or larger side (m).
Anchors (source pixels): the flying axe on its front, the hits on their white core, what sits on the ground (the axe
striking it, the frost, the stuck axe, the rage fire) on its ring's widest row or its lowest row, the pictures round
his body on the middle of their box.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (tools/kit/build_olaf.py, 60 ticks a second).
The red side: the client never mirrors a data picture. The flying axe is turned to its flight - drawn over its own
top-bottom flip would make it two-headed, so it stays as drawn (an axe spinning reads the same upside down);
everything on a unit or on the ground is drawn as stored whichever way he faces - drawn over its own left-right flip
(league_xayah's FLIP_LR), except the stuck axe (an object lying in the world, the same picture for both sides).
Writes league/effects/league_olaf_fx and league_olaf_big.
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

SRC = os.path.join(ROOT, "assets", "source", "olaf")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps (work/ol/fx_pack_ol.py), darkest first
RAMPS = {
    "ICE": ["10265C", "1E4AA0", "3C7ED6", "72B8F2", "B4E2FF", "E6F6FF", "FFFFFF"],
    "RAGE": ["5C0C08", "A81E10", "E2461A", "FF8C1E", "FFCB5E", "FFF2C2", "FFFFFF"],
    "AXE": ["2A1208", "4A2A1E", "74442C", "A06A44", "2E3448", "4E5E7E", "8494B2", "BCC4D8", "ECEAF0", "FFFFFF"],
    "DUST": ["3C3428", "5E5244", "8A7A66", "B4A68E"],
}
# the lights' darkest shade on their edge goes (or takes the next)
RIM = {"10265C": "1E4AA0", "5C0C08": "A81E10"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=18, measure="h", anchor="core", ramps="ICE"),
    "q_fly": dict(n=4, size=20, measure="w", anchor="front", ramps="AXE ICE"),
    "q_land": dict(n=5, size=22, measure="w", anchor=("fixed", "ellipse", 2), ramps="ICE DUST"),
    "q_axe": dict(n=3, size=20, measure="h", anchor=("fixed", "low", 0), ramps="AXE ICE"),
    "q_hit": dict(n=4, size=18, measure="w", anchor="core", ramps="ICE"),
    "q_slow": dict(n=4, size=16, measure="w", anchor=("fixed", "ellipse", 0), ramps="ICE"),
    "q_pick": dict(n=4, size=28, measure="h", anchor=("fixed", "box", 1), ramps="ICE"),
    "e_hit": dict(n=5, size=28, measure="m", anchor="core", ramps="ICE"),
    "w_cast": dict(n=5, size=30, measure="w", anchor=("fixed", "box", 2), ramps="RAGE ICE"),
    "w_on": dict(n=4, size=44, measure="h", anchor=("fixed", "box", 0), ramps="RAGE ICE"),
    "r_cast": dict(n=6, size=44, measure="h", anchor=("fixed", "low", 3), ramps="RAGE"),
    "r_on": dict(n=4, size=36, measure="w", anchor=("fixed", "low", 0), ramps="RAGE"),
    "p_4": dict(n=4, size=40, measure="h", anchor=("fixed", "box", 0), ramps="RAGE"),
}


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(x["file"]): x for x in json.load(f)["assets"]}
    V.RAMPS = RAMPS
    V.RIM = RIM
    anchors = {}
    for name, spec in RAW.items():
        fn = f"olaf_fx_{name}.png"
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
    with open(G.lp(os.path.join(SRC, "olaf_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"olaf_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"olaf_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down): the soles 11 under it, his crown 30 over it (the 42-row design)
HIT = (0, -11)              # a hit on the upper body of a unit
BODY = (0, -8)              # an aura round his body
WAIST = (0, -6)             # the axe pick-up's ring
FEET = (0, 10)              # a ring on the ground round a unit's feet (and a point on the ground: the stuck axe)
GROUND = (0, 11)            # what stands on the ground by its lowest row (the rage fire)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the axe lobbed q_fly 10 ticks (167 ms); the picture loops over twice that, the first tick hidden
    "q_fly": [("q_axe_fly", flight(4, 60, 340, lead=1), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_land": [("q_land", seq(range(5), [40, 50, 60, 80, 100]), [FEET])],
    # the stuck axe: replayed every axe_step (15 ticks = 250 ms) while it lies there
    "q_axe": [("q_axe", seq(range(3), [80, 90, 80]), [GROUND])],
    "q_pick": [("q_pick", seq(range(4), [50, 60, 70, 90]), [WAIST])],
    "w_cast": [("w_cast", seq(range(5), [50, 60, 70, 90, 100]), [BODY])],
    # the buffs' loops
    "q_slow": [("q_slow", seq(range(4), [110] * 4), [FEET])],
    "w_on": [("w_on", seq(range(4), [110] * 4), [BODY])],
    "p_4": [("p_4", seq(range(4), [120] * 4), [BODY])],
}
BIG = {
    "e_hit": [("e_hit", seq(range(5), [40, 50, 60, 70, 90]), [HIT])],
    "r_cast": [("r_cast", seq(range(6), [40, 60, 80, 90, 110, 130]), [GROUND])],
    "r_on": [("r_on", seq(range(4), [100] * 4), [GROUND])],
}
SRC_OF = {"q_axe_fly": "q_fly"}    # a tag whose cells come from another strip
NO_FLIP = {"q_fly", "q_axe"}       # objects: the spinning axe (turned with its flight) and the axe lying in the world
FLIP_LR = (set(FX) | set(BIG)) - NO_FLIP


# Tough It Out's aura: Codex drew a thick ring of fire (its HANDOFF: brighter and thicker than the faint glow asked for)
# that reads as Ragnarok's fire for 4 s - only its bright rim stays (the ramp's three darkest shades go)
THIN = {"w_on": ("5C0C08", "A81E10", "E2461A")}


def thin(cell, hexes_):
    out = cell.copy()
    for h in hexes_:
        rgb = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)
        out[(out[..., :3] == rgb).all(-1)] = 0
    return out


def build(table):
    with open(G.lp(os.path.join(SRC, "olaf_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            src = SRC_OF.get(src, src)
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                cell = thin(strip[k], THIN[src]) if src in THIN else strip[k]
                f = J.place(cell, anchors[src]["anchor"], spots)
                if tag in FLIP_LR:
                    f = X.over_flip(f, "lr")
                out[tag].append((f, ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_olaf_fx", FX), ("league_olaf_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

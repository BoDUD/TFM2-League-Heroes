#!/usr/bin/env python3
"""Import Kog'Maw's effects (assets/source/kogmaw/PROMPTS_FX.md, 18 sheets) as the game sheets league_kogmaw_fx and
league_kogmaw_big.

    python tools/art/import_kogmaw.py --raw assets/source/kogmaw/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_kogmaw.py                                     # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_kogmaw.py built the strips). --raw turns each frame of Codex's
drawings into a cell of a native strip (assets/source/kogmaw/kogmaw_fx_<name>.png, 8x, plus kogmaw_fx_anchors.json)
the way import_rengar.py does, the frames cut by the delivery's manifest.json rects (its `filename` key): each game
pixel the majority colour of the source pixels it covers, opaque when a quarter of them are solid, every colour snapped
to the ramps the pack gave that effect (work/km/fx_pack_km.py: ACID, SPIT, VOID, WARN), then the lights' darkest ring
comes off (import_jhin.unrim). Codex drew these with 4-px squares on the 16-px-a-square canvases (its HANDOFF: read at
16 px the white cores vanished), so the scale comes from the sizes, never from the grid. One scale per strip: `size`
game px over the drawings' widest (w), tallest (h) or larger side (m); the trail is the kit's line (110000 -> 110 px,
league_nocturne's q_path rule), the warning ring the shell's radius (r_r 15000 -> 30 px across).
Anchors (source pixels): the flying ones on their front, the hits on their white core, the rings on the ground on
their widest row, the auras on the middle of their box, the falling shell and the void eruption on the ground point
the delivery's manifest gives (anchor_px).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (tools/kit/build_kogmaw.py, 60 ticks a second).
The red side: the client never mirrors a data picture. The flying ones and the trail are turned to their flight - drawn
over their own top-bottom flip; everything on a unit or on the ground is drawn as stored whichever way he faces - drawn
over its own left-right flip (league_xayah's FLIP_TB / FLIP_LR). Every frame is centred on the pivot.
Writes league/effects/league_kogmaw_fx and league_kogmaw_big.
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

SRC = os.path.join(ROOT, "assets", "source", "kogmaw")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps (work/km/fx_pack_km.py), darkest first
RAMPS = {
    "ACID": ["26640E", "46961A", "74C41E", "A8E838", "D4F87A", "F2FFD0", "FFFFFF"],
    "SPIT": ["4A760E", "7CA816", "B4D21E", "E2E83A", "FFF07A", "FFFCD8", "FFFFFF"],
    "VOID": ["42106A", "7420A0", "AE38D0", "DA66EC", "F6A8FA", "FFE4FF", "FFFFFF"],
    "WARN": ["84C02A", "B6E44A", "DCF88A", "F6FFD8", "FFFFFF"],
}
# the lights' darkest shade on their edge goes (or takes the next)
RIM = {"26640E": "46961A", "4A760E": "7CA816", "42106A": "7420A0", "84C02A": "B6E44A"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_glob": dict(n=4, size=8, measure="w", anchor="front", ramps="ACID"),
    "a_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="ACID"),
    "w_cast": dict(n=5, size=44, measure="w", anchor=("fixed", "box", 0), ramps="ACID"),
    "w_on": dict(n=4, size=40, measure="w", anchor=("fixed", "ellipse", 0), ramps="ACID"),
    "q_spit": dict(n=4, size=14, measure="w", anchor="front", ramps="SPIT"),
    "q_hit": dict(n=5, size=18, measure="m", anchor="core", ramps="SPIT"),
    "q_shred": dict(n=4, size=20, measure="w", anchor=("fixed", "box", 0), ramps="SPIT"),
    "e_ooze": dict(n=4, size=12, measure="w", anchor="front", ramps="VOID"),
    "e_trail": dict(n=4, size=110, measure="w", anchor=("fixed", "box", 0), ramps="VOID"),
    "e_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="VOID"),
    "e_slow": dict(n=4, size=18, measure="w", anchor=("fixed", "ellipse", 0), ramps="VOID"),
    "r_mark": dict(n=6, size=30, measure="w", anchor=("fixed", "ellipse", 0), ramps="WARN ACID"),
    "r_fall": dict(n=7, size=32, measure="w", anchor="manifest", ramps="ACID"),
    "r_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="ACID"),
    "p_wake": dict(n=6, size=34, measure="h", anchor="manifest", ramps="VOID"),
    "p_form": dict(n=4, size=18, measure="w", anchor="front", ramps="VOID"),
    "p_boom": dict(n=6, size=26, measure="m", anchor="core", ramps="VOID"),
    "p_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="VOID"),
}
MANIFEST_ANCHOR = {}             # name -> (x, y) inside a cell, from the delivery's manifest (anchor_px)


def anchor(how, k, a, solid, rects, s):
    if how == "manifest":
        x, y, _, _ = rects[k]
        ax, ay = MANIFEST_ANCHOR[CURRENT[0]]
        return x + ax, y + ay
    return ORIG_ANCHOR(how, k, a, solid, rects, s)


CURRENT = [None]
ORIG_ANCHOR = V.anchor


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(x["filename"]): x for x in json.load(f)["assets"]}
    V.RAMPS = RAMPS
    V.RIM = RIM
    V.anchor = anchor
    anchors = {}
    for name, spec in RAW.items():
        fn = f"kogmaw_fx_{name}.png"
        CURRENT[0] = name
        MANIFEST_ANCHOR[name] = tuple(manifest[fn]["anchor_px"])
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
    V.anchor = ORIG_ANCHOR
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "kogmaw_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"kogmaw_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"kogmaw_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down)
HIT = (0, -11)              # a hit on the upper body of a 36-44 px unit
BODY = (0, -8)              # an aura round a body (his own: 38 rows from the soles at +11)
FEET = (0, 10)              # a ring on the ground round a unit's feet; a point on the ground
CENTRE = (0, 0)             # a projectile (centred on itself)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight


def loop(n, ms):
    return seq(range(n), [ms] * n)


FX = {
    # the flying ones: the glob 6500 a tick for ~55000 (9 ticks), the spittle 5000 for 105000 (21), the ooze 4000 for
    # 110000 (28) - homing / straight, the pictures looped and held (flight's rule)
    "a_glob": [("a_glob", flight(4, 60, 400), [CENTRE])],
    "q_spit": [("q_spit", flight(4, 70, 700), [CENTRE])],
    "e_ooze": [("e_ooze", flight(4, 80, 900), [CENTRE])],
    # the hits
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 80, 100]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 80]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 70, 90]), [HIT])],
    "p_hit": [("p_hit", seq(range(4), [40, 50, 60, 80]), [HIT])],
    "w_cast": [("w_cast", seq(range(5), [50, 60, 70, 80, 100]), [BODY])],
    # the buffs' loops
    "w_on": [("w_on", loop(4, 100), [FEET])],
    "q_shred": [("q_shred", loop(4, 120), [BODY])],
    "e_slow": [("e_slow", loop(4, 110), [FEET])],
}
BIG = {
    # the trail lies 240 ticks: its 4 frames looped (Animated, repeat)
    "e_trail": [("e_trail", loop(4, 110), [CENTRE])],
    # the void form: homing at 1800 a tick, up to ~70000 and on (chasing)
    "p_form": [("p_form", flight(4, 80, 3000), [CENTRE])],
    # the warning ring: the 40 ticks (667 ms) from the mark to the blast, its last frame the flash
    "r_mark": [("r_mark", seq(range(6), [110, 110, 110, 110, 110, 120]), [FEET])],
    # the shell: started 8 ticks before the blast - two falling frames (133 ms), the impact on the blast
    "r_fall": [("r_fall", seq(range(7), [66, 67, 60, 80, 100, 130, 160]), [FEET])],
    "p_wake": [("p_wake", seq(range(6), [60, 70, 80, 100, 120, 150]), [FEET])],
    "p_boom": [("p_boom", seq(range(6), [40, 50, 60, 70, 90, 110]), [HIT])],
}
FLIP_TB = {"a_glob", "q_spit", "e_ooze", "e_trail", "p_form"}
FLIP_LR = (set(FX) | set(BIG)) - FLIP_TB


def build(table):
    with open(G.lp(os.path.join(SRC, "kogmaw_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_kogmaw_fx", FX), ("league_kogmaw_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

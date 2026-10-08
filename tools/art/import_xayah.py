#!/usr/bin/env python3
"""Import Xayah's effects (assets/source/xayah/PROMPTS_FX.md, 21 sheets) as the game sheets league_xayah_fx and
league_xayah_big.

    python tools/art/import_xayah.py --raw assets/source/xayah/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_xayah.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_xayah.py built the strips). --raw turns each frame of Codex's
drawings into a cell of a native strip (assets/source/xayah/xayah_fx_<name>.png, 8x, plus xayah_fx_anchors.json) the
way import_varus.py does: the frames are the drawing's equal grid, each game pixel the majority colour of the source
pixels it covers, opaque when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect
(MAGENTA, VIOLET, CRIMSON, GOLD and the objects' INK outline), then the light's darkest ring comes off
(import_jhin.unrim) - the INK outline of blades and daggers stays. One scale per strip: `size` game px over the
drawings' widest (w), tallest (h) or larger side (m).
Anchors (source pixels): the flying blades on their front (3 px in from the tip), the hits on their white flash, the
throw flash on its left end, the glows and rings round her on their box (one frame's for the whole strip), the rings on
the ground on their widest row, what stands on the ground (the feathers stuck in it, the root's blades, the speed
wisps) on the middle of its lowest row, the dagger rain's fan on its apex.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) measured on the rigged strips (work/xy/fx_pack_xy.hand_at / chest_at): the out-flung hand in attack 3-4
(19, -4) and Q 3 (19, -5), the hanging hand (15, -1), the chest (3, -8) - and times it by the kit
(tools/kit/build_xayah.py, 60 ticks a second). The dagger rain is the LineRangeProjectile's own picture, which the game
centres on the 90-px line and turns to the cast: its apex sits half the line behind the centre (league_ashe W's fan).
Writes league/effects/league_xayah_fx and league_xayah_big.
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

V_ANCHOR = V.anchor

SRC = os.path.join(ROOT, "assets", "source", "xayah")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (work/xy/fx_pack_xy.py)
RAMPS = {
    "MAGENTA": ["7A1450", "C0207A", "F02D9C", "FF7AD8", "FFD6F2", "FFFFFF"],
    "VIOLET": ["2A1050", "5A1FA0", "8A3CD8", "B87AF0", "ECD8FF", "FFFFFF"],
    "CRIMSON": ["600A24", "B0123A", "F02D50", "FF8A9A", "FFE6E6"],
    "GOLD": ["B84313", "F08122", "FCC24F", "FFF4C8"],
    "INK": ["0B040E"],                       # the blades', daggers' and stuck feathers' outline
}
# the light's darkest shade on its edge goes (or takes the next)
RIM = {"7A1450": "C0207A", "2A1050": "5A1FA0", "600A24": "B0123A", "B84313": "F08122"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_blade": dict(n=4, size=11, measure="w", anchor="front", ramps="INK MAGENTA VIOLET"),
    "a_pierce": dict(n=4, size=16, measure="w", anchor="front", ramps="INK MAGENTA VIOLET GOLD"),
    "a_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="MAGENTA VIOLET"),
    "p_on": dict(n=4, size=10, measure="m", anchor=("fixed", "box", 1), ramps="MAGENTA VIOLET"),
    "f_drop": dict(n=3, size=10, measure="h", anchor=("fixed", "low", 2), ramps="INK MAGENTA VIOLET"),
    "f_lie": dict(n=2, size=9, measure="h", anchor=("fixed", "low", 0), ramps="INK MAGENTA VIOLET"),
    "feather": dict(n=4, size=13, measure="w", anchor="front", ramps="INK MAGENTA VIOLET"),
    "q_dagger": dict(n=4, size=14, measure="w", anchor="front", ramps="INK MAGENTA VIOLET GOLD"),
    "q_flash": dict(n=3, size=12, measure="w", anchor="left", ramps="MAGENTA VIOLET"),
    "q_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="MAGENTA VIOLET"),
    "e_cast": dict(n=4, size=24, measure="m", anchor=("fixed", "box", 0), ramps="MAGENTA VIOLET"),
    "e_hit": dict(n=3, size=12, measure="m", anchor="core", ramps="MAGENTA VIOLET"),
    "e_root": dict(n=5, size=20, measure="w", anchor=("fixed", "low", 2), ramps="INK MAGENTA CRIMSON"),
    "e_bind": dict(n=4, size=16, measure="w", anchor=("fixed", "low", 0), ramps="INK MAGENTA CRIMSON"),
    "w_cast": dict(n=5, size=26, measure="m", anchor=("fixed", "box", 1), ramps="INK MAGENTA VIOLET"),
    "w_on": dict(n=4, size=22, measure="w", anchor="ellipse", ramps="MAGENTA VIOLET"),
    "w_flash": dict(n=3, size=10, measure="m", anchor=("fixed", "box", 1), ramps="VIOLET MAGENTA"),
    "w_ms": dict(n=4, size=18, measure="w", anchor=("fixed", "low", 0), ramps="MAGENTA GOLD"),
    "r_cast": dict(n=5, size=28, measure="m", anchor=("fixed", "box", 2), ramps="INK MAGENTA VIOLET GOLD"),
    "r_rain": dict(n=6, size=90, measure="w", anchor="apex", ramps="INK MAGENTA VIOLET CRIMSON"),
    "r_hit": dict(n=4, size=16, measure="m", anchor="core", ramps="INK MAGENTA CRIMSON"),
}


def anchor(how, k, a, solid, rects, s):
    if how == "apex":                  # the fan's apex: its leftmost solid column over all frames, the middle row
        left = min(x + int(np.nonzero(solid[y:y + h, x:x + w].any(0))[0].min()) - x
                   for x, y, w, h in rects if solid[y:y + h, x:x + w].any())
        x, y, w, h = rects[k]
        return x + left, y + h / 2
    return V_ANCHOR(how, k, a, solid, rects, s)


def from_raw(folder):
    V.RAMPS = RAMPS
    V.RIM = RIM
    V.anchor = anchor
    anchors = {}
    for name, spec in RAW.items():
        fn = f"xayah_fx_{name}.png"
        hexes_, pal = V.palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = V.grid(a, spec["n"])
        out, cell, anc, s, ext = V.convert(name, spec, a, solid, idx, pal, rects)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"xayah_fx_{name}.png")))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": len(rects)}
        print(f"xayah_fx_{name}.png  {len(rects)} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "xayah_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"xayah_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"xayah_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (fx_pack_xy.hand_at / chest_at)
HAND_OUT = (19, -4)         # the out-flung hand in attack 3-4 (the blade leaves it; W's second blade at tick 14)
HAND_Q = (19, -5)           # the out-flung hand in Q 3 (a row up: the hop)
GLOW = (0, -6)              # the passive's glow as a spell starts: on her middle, both ways the same (it plays in
                            # each spell's five charge branches - too many to draw into her frames)
CHEST = (3, -8)             # her chest (E's call, W's storm, R's wings)
HIT = (0, -10)              # a hit on the upper body of a 36-44 px unit
FEET = (0, 9)               # a ring on the ground round a unit's feet
SOLES = (0, 11)             # what stands on the ground: its lowest row on the soles (a point's own ground too)
APEX = (-45, 0)             # the rain's apex: half the 90-px line behind its centre
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the blades: the attack 57.5 px at 7 a tick (homing: twice that), the empowered line 72 px, Q's daggers 95 px
    # at 6, the feathers flying back up to 160 px at 4.5
    "a_blade": [("a_blade", flight(4, 60, 300, lead=2), [(0, 0)])],
    "w_blade": [("a_blade", flight(4, 60, 300, lead=2), [(0, 0)])],
    "a_pierce": [("a_pierce", flight(4, 60, 300, lead=2), [(0, 0)])],
    "q_dagger": [("q_dagger", flight(4, 60, 400, lead=2), [(0, 0)])],
    "feather": [("feather", flight(4, 60, 900, lead=1), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(3), [40, 50, 60]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_on": [("p_on", seq(range(4), [50, 60, 70, 80]), [GLOW])],
    "q_flash": [("q_flash", seq(range(3), [30, 40, 50]), [HAND_Q])],
    "w_flash": [("w_flash", seq(range(3), [30, 40, 50]), [HAND_OUT])],
    # a feather lands where its blade stopped, then is re-stamped every f_step (20 ticks) while it lies
    "f_drop": [("f_drop", seq(range(3), [50, 80, 140]), [SOLES])],
    "f_lie": [("f_lie", seq([0, 1], [170, 163]), [SOLES])],
    "e_cast": [("e_cast", seq(range(4), [50, 60, 70, 80]), [CHEST])],
    "e_root": [("e_root", seq(range(5), [50, 60, 80, 120, 160]), [SOLES])],
    "e_bind": [("e_bind", seq(range(4), [110] * 4), [SOLES])],
    "w_cast": [("w_cast", seq(range(5), [50, 60, 70, 80, 90]), [CHEST])],
    "w_on": [("w_on", seq(range(4), [110] * 4), [FEET])],
    "w_ms": [("w_ms", seq(range(4), [100] * 4), [SOLES])],
    "r_cast": [("r_cast", seq(range(5), [60, 70, 80, 90, 100]), [CHEST])],
}
BIG = {
    # the LineRangeProjectile lives `delay` 18 ticks (300 ms): the fan's six frames over it
    "r_rain": [("r_rain", seq(range(6), [50, 50, 50, 50, 50, 33]), [APEX])],
}


# the red side (the user: 「蓝色方红色方特效不要颠倒」): the client never mirrors a data picture. A projectile is turned to its
# flight, so flying left (red) it is upside down: the blades, daggers, feathers and the rain's fan are drawn over
# their own top-bottom flip. The views on units and on the ground (the hits' slashes, the feathers stuck in the
# ground, the root's blades, the storm ring, the speed wisps behind her) are drawn as stored whichever way she faces:
# drawn over their own left-right flip. Every frame is centred on the pivot, so the flips are about it. (Q's, W's, E's
# and R's casting pictures are drawn into her frames: tools/fix/bake_caster_fx.py; the passive's glow is
# league_xayah_sym.)
FLIP_TB = {"a_blade", "w_blade", "a_pierce", "q_dagger", "feather", "r_rain"}
FLIP_LR = {"a_hit", "q_hit", "e_hit", "r_hit", "f_drop", "f_lie", "e_root", "e_bind", "w_on", "w_ms"}


def over_flip(f, axis):
    """f drawn over its own flip about the frame's centre (the pivot): its pixels stay, the flip fills in under them."""
    g = f[::-1] if axis == "tb" else f[:, ::-1]
    out = g.copy()
    out[f[..., 3] > 0] = f[f[..., 3] > 0]
    return out


def build(table):
    with open(G.lp(os.path.join(SRC, "xayah_fx_anchors.json")), encoding="utf-8") as f:
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
                if tag in FLIP_TB or tag in FLIP_LR:
                    f = over_flip(f, "tb" if tag in FLIP_TB else "lr")
                out[tag].append((f, ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_xayah_fx", FX), ("league_xayah_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

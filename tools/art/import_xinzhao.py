#!/usr/bin/env python3
"""Import Xin Zhao's effects (assets/source/xinzhao/PROMPTS_FX.md, 20 sheets) as the game sheets league_xinzhao_fx and
league_xinzhao_big.

    python tools/art/import_xinzhao.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_xinzhao.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_xinzhao.py built the strips). --raw turns each frame of Codex's
drawings (laid out on the requested cells, semi-transparent edges, drawn bigger than asked: hits ~27 squares for 14)
into a cell of a native strip (assets/source/xinzhao/xinzhao_fx_<name>.png, 8x, plus xinzhao_fx_anchors.json) the way
import_tryndamere.py does (import_varus.convert): the frames are the drawing's equal grid, each game pixel the majority
colour of the source pixels it covers, opaque when a quarter of them are solid, every colour snapped to the ramps the
pack gave that effect (GOLD, STORM, DUSK and the INK outline of the challenge emblem), then the light's darkest ring
comes off (unrim). One scale per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m).
Anchors (source pixels): the hits on their white flash, the ground rings on their widest row, the marks on their lowest
row, and the caster pictures on the cell point the prompt put the figure's feet on ("pt": fractions of the cell).
Q's count marks came as 3 rows of 4 (3, 2 and 1 talons): one scale for the rows (the widest row), each row its own strip
q_1 .. q_3. W's thrust is a LineRangeProjectile's picture, turned to the cast: its rows are made a mirror top to bottom
about the line (import_jhin.mirror) - Codex's came 4-12% off. The guard's glow is a buff's picture, never mirrored by
his facing: its right half is its left half mirrored (sym).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (tools/kit/build_xinzhao.py, 60 ticks a second). Writes league/effects/league_xinzhao_fx
and league_xinzhao_big.
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
import import_twistedfate as TF  # noqa: E402
import import_varus as V  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "xinzhao")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (tools/art/pack_xinzhao_fx.py)
RAMPS = {
    "GOLD": ["7A3A08", "C06A10", "F0A020", "FFD45A", "FFF4C0", "FFFFFF"],
    "STORM": ["12307A", "1E5AC0", "3A9CF0", "8AD8FF", "D8F4FF", "FFFFFF"],
    "DUSK": ["1C1640", "2E2468", "4A3A9A", "6A5AC8"],
    "INK": ["10102A"],                       # the challenge emblem's outline
}
# the light's darkest shade on its edge goes (or takes the next); the ink outline stays
RIM = {"7A3A08": "C06A10", "12307A": "1E5AC0", "1C1640": "2E2468"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=14, measure="w", anchor=("fixed", "core", 1), ramps="GOLD"),
    "p_hit": dict(n=5, size=22, measure="m", anchor=("fixed", "core", 1), ramps="GOLD"),
    "p_heal": dict(n=5, size=18, measure="h", anchor=("fixed", "box", 0), ramps="GOLD"),
    "e_dash": dict(n=5, size=34, measure="w", anchor=("pt", 0.5, 20 / 24), ramps="STORM GOLD"),
    "e_land": dict(n=5, size=40, measure="w", anchor=("fixed", "ellipse", 2), ramps="STORM GOLD DUSK"),
    "e_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="STORM GOLD"),
    "e_slow": dict(n=4, size=18, measure="w", anchor=("fixed", "ellipse", 3), ramps="STORM DUSK"),
    "q_marks": dict(n=12, rows=3, size=13, measure="w", anchor=("fixed", "low", 0), ramps="GOLD"),
    "q_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 1), ramps="GOLD"),
    "q3_up": dict(n=5, size=30, measure="h", anchor=("pt", 0.5, 36 / 40), ramps="GOLD DUSK"),
    "w_slash": dict(n=4, size=30, measure="h", anchor=("pt", 12 / 40, 26 / 30), ramps="GOLD STORM"),
    "w_thrust": dict(n=5, size=60, measure="w", anchor=("pt", 0.5, 0.5), ramps="STORM", mirror=True),
    "w_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 1), ramps="GOLD STORM"),
    "w_hit2": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="STORM"),
    "w_slow": dict(n=4, size=20, measure="w", anchor=("fixed", "ellipse", 0), ramps="STORM DUSK"),
    "r_tell": dict(n=4, size=28, measure="m", anchor=("pt", 0.5, 0.5), ramps="GOLD STORM"),
    "r_sweep": dict(n=6, size=76, measure="w", anchor=("fixed", "ellipse", 3), ramps="STORM GOLD DUSK"),
    "r_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 1), ramps="STORM GOLD"),
    "r_chal": dict(n=4, size=12, measure="h", anchor=("fixed", "low", 0), ramps="INK GOLD STORM"),
    "r_guard": dict(n=4, size=46, measure="h", anchor=("pt", 0.5, 40 / 44), ramps="GOLD", sym=True),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def anchor(how, k, a, solid, rects, s):
    if how[0] == "pt":                       # a point of the cell, as fractions of its width and height
        x, y, w, h = rects[k]
        return x + how[1] * w, y + how[2] * h
    return TF.anchor(how, k, a, solid, rects, s)


def from_raw(folder):
    V.RIM = RIM                              # import_varus.convert's unrim reads its module's RIM
    V.anchor = anchor                        # ... and its anchor (the cell points added)
    anchors = {}
    for name, spec in RAW.items():
        _, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"xinzhao_fx_{name}.png"))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rows = spec.get("rows", 1)
        rects = V.grid(a, spec["n"], rows)
        per = spec["n"] // rows
        groups = [(name, rects)] if rows == 1 else [(f"q_{r + 1}", rects[r * per:(r + 1) * per]) for r in range(rows)]
        widest = None
        if rows > 1:                         # one scale for the three rows: the widest row sets it
            def width(rr):
                x, y, w, h = rr
                xs = np.nonzero(solid[y:y + h, x:x + w].any(0))[0]
                return xs.max() - xs.min() + 1 if len(xs) else 0
            widest = max(width(r) for r in rects)
        for gname, grects in groups:
            sp = spec
            if rows > 1:
                rw = max(width(r) for r in grects)
                sp = dict(spec, size=spec["size"] * rw / widest)
            out, cell, anc, s, ext = V.convert(gname, sp, a, solid, idx, pal, grects)
            if spec.get("sym"):              # a buff's picture is never mirrored by his facing: exactly symmetric
                tw, th = cell
                for i in range(len(grects)):
                    c = out[:, i * tw:(i + 1) * tw]
                    c[:, tw - anc[0]:] = c[:, :anc[0]][:, ::-1][:, :c.shape[1] - (tw - anc[0])]
            if spec.get("mirror"):
                tw, th = cell
                for i in range(len(grects)):
                    c = out[:, i * tw:(i + 1) * tw]
                    out[:, i * tw:(i + 1) * tw] = J.mirror(c, anc[1])
            Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
                G.lp(os.path.join(SRC, f"xinzhao_fx_{gname}.png")))
            anchors[gname] = {"cell": list(cell), "anchor": list(anc), "frames": len(grects)}
            print(f"xinzhao_fx_{gname}.png  {len(grects)} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
                  f"{s:.4f} ({sp['size']:.0f} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "xinzhao_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"xinzhao_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"xinzhao_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (pack_xinzhao_fx.SHOTS)
HIT = (0, -11)              # a hit on the upper body of a 36-44 px unit
CHEST = (2, -8)             # his chest (canvas (66, 80), the pivot (64, 88))
FEET = (0, 11)              # the soles under the pivot: the prompts put the figure's feet on the cell point
RING = (0, 10)              # a ring on the ground round a unit's feet
OVER = (0, -33)             # a mark's foot over the head (his topknot tops 30 over the pivot)
LINE = (0, 0)               # a LineRangeProjectile's picture is centred on its line
DASH = (0, 2)               # the leap's streak: Codex drew it 7-12 squares over the cell point; at FEET it hung at his
                            # boots, 9 px up it trails from his waist
seq = J.seq

FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_hit": [("p_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    # Determination's heal: played with the third hit's damage, not following him
    "p_heal": [("p_heal", seq(range(5), [60, 70, 80, 90, 110]), [CHEST])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q3_up": [("q3_up", seq(range(5), [40, 60, 80, 90, 100]), [FEET])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit2": [("w_hit2", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # buffs (looped while they last): the talon count over his head, the slows at the feet, the challenge mark
    "q_1": [("q_1", seq(range(4), [130] * 4), [OVER])],
    "q_2": [("q_2", seq(range(4), [130] * 4), [OVER])],
    "q_3": [("q_3", seq(range(4), [130] * 4), [OVER])],
    "e_slow": [("e_slow", seq(range(4), [120] * 4), [RING])],
    "w_slow": [("w_slow", seq(range(4), [120] * 4), [RING])],
    "r_chal": [("r_chal", seq(range(4), [130] * 4), [OVER])],
}
BIG = {
    # E: the streak follows him from the action's first tick (the skill strip is e_anim = 16 ticks)
    "e_dash": [("e_dash", seq(range(5), [40, 50, 60, 60, 60]), [DASH])],
    # the landing ring under him, on the spot he landed (not following)
    "e_land": [("e_land", seq(range(5), [50, 60, 70, 80, 90]), [RING])],
    # W: the slash in front of him on tick 13 (not following); the thrust is its line's picture (turned to the cast)
    "w_slash": [("w_slash", seq(range(4), [50, 60, 70, 80]), [FEET])],
    "w_thrust": [("w_thrust", seq(range(5), [30, 40, 50, 60, 70]), [LINE])],
    # R: the spear's spin from the first tick (following), the crescent round him on tick 10 (not following)
    "r_tell": [("r_tell", seq(range(4), [50, 60, 60, 70]), [CHEST])],
    "r_sweep": [("r_sweep", seq(range(6), [40, 50, 60, 70, 80, 90]), [RING])],
    # the guard's 3 s: under him, symmetric (a buff's picture is never mirrored by his facing)
    "r_guard": [("r_guard", seq(range(4), [120] * 4), [FEET])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "xinzhao_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_xinzhao_fx", FX), ("league_xinzhao_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

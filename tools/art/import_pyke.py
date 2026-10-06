#!/usr/bin/env python3
"""Import Pyke's effects (assets/source/pyke/PROMPTS_FX.md, 16 sheets) as the game sheets league_pyke_fx and
league_pyke_big.

    python tools/art/import_pyke.py --raw assets/source/pyke/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_pyke.py                                    # native strips -> the effect sheets

--raw turns each frame of Codex's generated sheets into a cell of a native strip (assets/source/pyke/pyke_fx_<name>.png,
8x, plus pyke_fx_anchors.json) the way import_samira.py does: each game pixel the majority colour of the source pixels
it covers, opaque when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect, then the
water's / blood's darkest shade comes off its edge (import_jhin.unrim; the thrown harpoon keeps its outline). One scale
per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m).

Red side and blue side alike (the user: 「注意红色方和蓝色方的技能特效不要不对称 导致歪的」): the client mirrors his own
frames with his facing and never an effect picture, so
- the flying pictures (the harpoon, the phantom) are mirrored top to bottom about their middle row (cast leftward the
  engine turns them upside down); q_return is q_hook mirrored left to right (the harpoon coming back tail first);
- the charge glow on his raised blade is drawn into his own skill frames (pyke_bake.json, import_native.bake);
- what plays on him whichever way he faces late (r_reset, p_heal), E's wake (e_trail, drawn here), the buffs (e_stun, q_slow) and the ground pictures (w_cast, e_left, r_mark, r_strike) are mirrored left to right about their middle.
Spots (game px from the pivot, x forward, y down; his soles 11 under it) come from the finished strips (rig_pyke.py;
pack_pyke_fx.SHOTS). Times from the strips (rig_pyke.MS) and the kit (build_pyke.P, 60 ticks a second).
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
import import_xerath as X  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "pyke")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (tools/art/pack_pyke_fx.py)
RAMPS = {
    "WATER": ["0B5466", "16929E", "3CCFC8", "8CF4E6", "D8FFF8", "FFFFFF"],
    "BONE": ["8E7A54", "C8B484", "E8D8AA", "FFF8E0", "FFFFFF"],
    "STEEL": ["9A1020", "D81A26", "B86A28", "E09A40", "F6D48C"],
    "BLOOD": ["4A0612", "8A0A1C", "D01E2A", "FF5A4A", "FFC8C0", "FFFFFF"],
    "GOLD": ["A85A08", "E89A10", "FFD040", "FFF0A0", "FFFFFF"],
    "INK": ["0A0608"],                       # the thrown harpoon's outline
}
# the effect's darkest shade on its edge goes (or takes the next)
RIM = {"0B5466": "16929E", "8E7A54": "C8B484", "4A0612": "8A0A1C", "A85A08": "E89A10"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps, sym ("lr" / "tb"), rim (False: keep it),
# hollow (half width of the columns kept clear over his middle)
RAW = {
    "a_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="BONE WATER"),
    "q_charge": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0), ramps="WATER", sym="lr"),
    "q_hook": dict(n=4, size=26, measure="w", anchor="front", ramps="INK BONE STEEL WATER", sym="tb", rim=False),
    "q_hit": dict(n=5, size=16, measure="m", anchor=("fixed", "core", 0), ramps="WATER"),
    "q_stab_hit": dict(n=4, size=16, measure="w", anchor=("fixed", "core", 0), ramps="BONE WATER", sym="tb"),
    "w_cast": dict(n=5, size=28, measure="w", anchor=("fixed", "ellipse", 0), ramps="WATER", sym="lr"),
    "e_left": dict(n=6, size=26, measure="w", anchor=("fixed", "ellipse", 0), ramps="WATER", sym="lr"),
    "e_phantom": dict(n=4, size=24, measure="w", anchor="front", ramps="WATER", sym="tb"),
    "e_hit": dict(n=5, size=18, measure="m", anchor=("fixed", "core", 0), ramps="WATER"),
    "e_stun": dict(n=4, size=14, measure="w", anchor=("fixed", "box", 0), ramps="WATER", sym="lr"),
    "q_slow": dict(n=4, size=16, measure="w", anchor="ellipse", ramps="WATER", sym="lr"),
    "r_mark": dict(n=6, size=56, measure="w", anchor=("fixed", "box", 5), ramps="BLOOD WATER", sym="lr"),
    "r_strike": dict(n=5, size=58, measure="w", anchor=("fixed", "box", 0), ramps="BLOOD WATER", sym="lr"),
    "r_hit": dict(n=5, size=20, measure="m", anchor=("fixed", "core", 0), ramps="BLOOD"),
    "r_reset": dict(n=6, size=24, measure="m", anchor=("fixed", "box", 0), ramps="GOLD BLOOD", sym="lr"),
    "p_heal": dict(n=6, size=22, measure="w", anchor=("fixed", "low", 0), ramps="WATER", sym="lr", hollow=5),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def from_raw(folder):
    V.TF = TF
    anchors = {}
    for name, spec in RAW.items():
        V.RIM = RIM if spec.get("rim", True) else {}      # import_varus.convert's unrim reads its module's RIM
        J.RIM = V.RIM
        fn = f"pyke_fx_{name}.png"
        _, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = V.grid(a, spec["n"])
        out, cell, anc, s, ext = V.convert(name, spec, a, solid, idx, pal, rects)
        if spec.get("sym"):
            X.symmetric(out, cell, anc, spec["n"], spec["sym"])
        if spec.get("hollow"):
            X.hollow(out, cell, anc, spec["n"], spec["hollow"])
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"pyke_fx_{name}.png")))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": spec["n"]}
        print(f"pyke_fx_{name}.png  {spec['n']} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "pyke_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"pyke_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"pyke_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x forward, y down), measured on the finished strips (pack_pyke_fx.SHOTS)
BLADE = (-11, -20)              # the raised harpoon's blade in the charge (skill frames 2-4; rig_pyke.shrunk_xy)
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -33)                 # over a head
BODY = (0, -4)                  # round his body (after rig_pyke.SHRINK)
SOLES = (0, 11)                 # what stands on the ground (round a unit, or on a point: a point is a unit's pivot,
                                # its ground 11 under it): its ellipse there
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the harpoon: 95 px at 6 px a tick, leaves his pivot (the throwing hand 5 px behind, 20 over it): 2 empty ticks
    "q_hook": [("q_hook", flight(4, 70, 600, lead=2), [(0, 0)])],
    "q_hook_c": [("q_hook", flight(4, 70, 600, lead=2), [(0, 0)])],
    "q_return": [("q_return", flight(4, 70, 1200, lead=0), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_charge": [("q_charge", seq([0, 1, 2, 3, 0, 1, 2, 3], [75] * 8), [BLADE])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 60, 70]), [HIT])],
    "q_stab_hit": [("q_stab_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_cast": [("w_cast", seq(range(5), [50, 60, 70, 70, 80]), [SOLES])],
    "e_hit": [("e_hit", seq(range(5), [40, 50, 60, 60, 70]), [HIT])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 60, 70]), [HIT])],
    "r_reset": [("r_reset", seq(range(6), [50, 60, 70, 80, 90, 100]), [BODY])],
    "p_heal": [("p_heal", seq(range(6), [80] * 6), [SOLES])],
    # buffs (looped while they last)
    "e_stun": [("e_stun", seq(range(4), [80] * 4), [OVER])],
    "q_slow": [("q_slow", seq(range(4), [100] * 4), [SOLES])],
}
# E's wake (the user: 「E少了点特效？中间没线条」): drawn here, not by Codex - a thin streak of ghost water, left-right
# symmetric (it stays put; the client never mirrors it), dropped under him every 2 ticks of the dash (9 px a tick, so
# the 22 px streaks overlap into one line on the ground from the puddle to where he lands; under the units, so the
# ones dropped after he lands hide under his feet); it fades as the phantom runs back along it
TRAIL_W = 22


def trail():
    hexes_, _ = palette("WATER")
    col = {k: np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8) for k, h in zip("dmlwW", hexes_[1:])}
    rows = [
        # fresh: a bright core, dark-teal wisps over and under
        ["....dd..dmmmmmmd..dd....", "..mmllllwwwwwwwwllllmm..", "....dd..dmmmmmmd..dd...."],
        # the core goes
        ["......d..dmmmmd..d......", "...dmmllllllllllllmmd...", "......d..dmmmmd..d......"],
        # breaking up
        [".......d...dd...d.......", "....dm.mmlllllmm.md.....", "........d.dd.d........."],
        # drops
        ["........................", ".....d..m..mm..m..d.....", "........................"],
    ]
    out = []
    for fr in rows:
        c = np.zeros((3, TRAIL_W + 2, 4), np.uint8)
        for y, line in enumerate(fr):
            line = (line + "." * (TRAIL_W + 2))[:TRAIL_W + 2]
            for x, ch in enumerate(line):
                if ch != ".":
                    c[y, x] = col[ch]
        c[:, (TRAIL_W + 2) // 2:] = c[:, :(TRAIL_W + 2) // 2][:, ::-1]   # left-right symmetric
        out.append(c)
    return out, [(TRAIL_W + 2) // 2 - 0.5, 1]


FX["e_trail"] = [("e_trail", seq(range(4), [140, 120, 110, 100]), [(0, 9)])]   # on the ground, under the units


BIG = {
    # the phantom: back to him at 12 px a tick from up to 120 px away
    "e_phantom": [("e_phantom", flight(4, 60, 600, lead=0), [(0, 0)])],
    # the puddle where the dash started, until the phantom has left it (12 ticks after the 14-tick dash)
    "e_left": [("e_left", seq(range(6), [60, 70, 80, 80, 70, 60]), [SOLES])],
    # R: the X on the target's spot, 30 ticks to the strike (the last frame held); the strike 6 ticks before it
    "r_mark": [("r_mark", seq(range(6), [80, 80, 80, 80, 80, 100]), [SOLES])],
    "r_strike": [("r_strike", seq(range(5), [60, 70, 80, 90, 100]), [SOLES])],
}


def build(table, extra):
    with open(G.lp(os.path.join(SRC, "pyke_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            base = "q_hook" if src == "q_return" else src
            if src == "e_trail":
                strip, anc = trail()
            else:
                strip = cells(base, anchors[base]["frames"])
                anc = anchors[base]["anchor"]
            if src == "q_return":            # tail first: mirrored left to right about the anchor
                strip = [c[:, ::-1].copy() for c in strip]
                anc = [strip[0].shape[1] - 1 - anc[0], anc[1]]
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                out[tag].append((J.place(strip[k], anc, spots), ms))
    return out


# the pictures drawn into his frames (import_native.bake): the charge glow on the raised blade rides the skill strip's
# four charge frames (rig_pyke.MS skill: 4 x 150 ms) - placed off his middle, a data picture would stay on the wrong
# side when he faces left (lint_mod: "has a front and a back")
BAKE = {"fx": "league_pyke_fx", "items": [{"tag": "q_charge", "into": "skill", "at_ms": 0}]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_pyke_fx", FX), ("league_pyke_big", BIG)):
        tags = build(table, None)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    with open(G.lp(os.path.join(ROOT, "assets", "source", "native", "pyke_bake.json")), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(json.dumps(BAKE, indent=1) + "\n")
    print("assets/source/native/pyke_bake.json:", len(BAKE["items"]), "items")


if __name__ == "__main__":
    main()

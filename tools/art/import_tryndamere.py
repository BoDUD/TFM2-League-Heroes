#!/usr/bin/env python3
"""Import Tryndamere's effects (assets/source/tryndamere/PROMPTS_FX.md, 11 sheets) as the game sheets
league_tryndamere_fx and league_tryndamere_big.

    python tools/art/import_tryndamere.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_tryndamere.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_tryndamere.py built the strips). --raw turns each frame of Codex's
drawings (generated originals, semi-transparent, about 2172x724) into a cell of a native strip
(assets/source/tryndamere/tryndamere_fx_<name>.png, 8x, plus tryndamere_fx_anchors.json) the way import_varus.py does:
the frames are the drawing's equal grid, each game pixel the majority colour of the source pixels it covers, opaque
when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect (RED, EMBER, DARK and the
INK outline of the ash and the broken-sword icon), then the light's darkest ring comes off (import_jhin.unrim). One
scale per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m).
Anchors (source pixels): the hits on their white flash (w_hit and q_heal on the flash of their burst frame, the same
spot in every cell), the spin on the box of its full ring (frame 5), the rings and flames on the ground on the ring's
widest row (w_shout on its widest ring, frame 4; r_cast on frame 2's), the attack-down icon on the middle of its lowest
row.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) measured on the rigged strips (tools/art/pack_tryndamere_fx.py SHOTS): the waist in E (7, -2), the chest in
Q (6, -8), the feet - and times it by the kit (tools/kit/build_tryndamere.py, 60 ticks a second). Writes
league/effects/league_tryndamere_fx and league_tryndamere_big.
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
import import_varus as V  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "tryndamere")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (tools/art/pack_tryndamere_fx.py)
RAMPS = {
    "RED": ["8A0A1A", "D0141E", "FF3A1E", "FF9A5A", "FFE0C8", "FFFFFF"],
    "EMBER": ["9A2A10", "E0501A", "FF8A1E", "FFC83A", "FFF2A8", "FFFFFF"],
    "DARK": ["1E040C", "3A0618", "5A0A24", "8A1030", "C02040"],
    "INK": ["12040A"],                       # the ash flakes' and the broken sword's outline
}
# the light's darkest shade on its edge goes (or takes the next); the ink outline stays
RIM = {"8A0A1A": "D0141E", "9A2A10": "E0501A", "1E040C": "3A0618"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=16, measure="m", anchor="core", ramps="RED EMBER"),
    "f_full": dict(n=4, size=48, measure="h", anchor=("fixed", "ellipse", 0), ramps="RED EMBER", stretch=1.7),
    "e_spin": dict(n=6, size=52, measure="w", anchor=("fixed", "box", 4), ramps="RED EMBER"),
    "e_hit": dict(n=4, size=16, measure="m", anchor="core", ramps="RED EMBER"),
    "w_shout": dict(n=6, size=84, measure="w", anchor=("fixed", "ellipse", 3), ramps="RED DARK"),
    "w_hit": dict(n=4, size=20, measure="m", anchor=("fixed", "core", 1), ramps="RED DARK"),
    "w_weak": dict(n=4, size=14, measure="h", anchor="low", ramps="INK DARK RED"),
    "w_slow": dict(n=4, size=24, measure="w", anchor="ellipse", ramps="DARK RED"),
    "q_heal": dict(n=5, size=44, measure="h", anchor=("fixed", "core", 2), ramps="RED EMBER"),
    "r_cast": dict(n=6, size=58, measure="h", anchor=("fixed", "ellipse", 2), ramps="INK EMBER RED DARK", stretch=1.75),
    "r_rage": dict(n=4, size=54, measure="h", anchor=("fixed", "ellipse", 0), ramps="EMBER RED", stretch=1.75),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def from_raw(folder):
    V.RIM = RIM                              # import_varus.convert's unrim reads its module's RIM
    anchors = {}
    for name, spec in RAW.items():
        fn = f"tryndamere_fx_{name}.png"
        _, pal = palette(spec["ramps"])
        im = Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")
        if spec.get("stretch"):
            # flames round the whole figure: drawn as tall as asked, then widened to cover him (the user, in game:
            # 「特效盖不住身体」 - 35 px of fire round a 57 px figure with his greatsword); every cell widens alike
            im = im.resize((round(im.width * spec["stretch"]), im.height), Image.NEAREST)
        a = np.asarray(im).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = V.grid(a, spec["n"])
        out, cell, anc, s, ext = V.convert(name, spec, a, solid, idx, pal, rects)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"tryndamere_fx_{name}.png")))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": spec["n"]}
        print(f"tryndamere_fx_{name}.png  {spec['n']} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "tryndamere_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"tryndamere_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"tryndamere_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (pack_tryndamere_fx.SHOTS)
WAIST = (6, -2)             # E 3: the middle of the spin (canvas (71, 86), the pivot (64, 88))
BODY = (5, 10)              # a ring under him centred on his torso, not on the middle of his wide stance
CHEST = (6, -7)             # Q 3: the chest (canvas (70, 80))
HIT = (0, -11)              # a hit on the upper body of a 36-44 px unit
OVER = (0, -32)             # the attack-down icon's foot over the head (the idle tops 28 over the pivot)
FEET = (0, 10)              # a ring on the ground round a unit's feet (the soles 11 under the pivot)
seq = J.seq

FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [50, 60, 70, 80]), [HIT])],
    # Bloodlust: played r_q_at ticks into the rage (or when the danger drinks it), not following him
    "q_heal": [("q_heal", seq(range(5), [60, 70, 80, 90, 110]), [CHEST])],
    # buffs (looped while they last): full Fury under him, the attack-down icon over the head, the slow at the feet
    "f_5": [("f_full", seq(range(4), [110] * 4), [FEET])],
    "w_weak": [("w_weak", seq(range(4), [130] * 4), [OVER])],
    "w_slow": [("w_slow", seq(range(4), [110] * 4), [FEET])],
}
BIG = {
    # E: the skill strip lasts e_tick + 4 = 16 ticks (267 ms); the spin follows him through the dash
    "e_spin": [("e_spin", seq(range(6), [40, 45, 45, 45, 45, 50]), [WAIST])],
    # W: the roar (the release is skill2 frame 4, tick 10); the ring reaches w_r (40 px) by frame 4
    "w_shout": [("w_shout", seq(range(6), [50, 60, 70, 80, 90, 100]), [BODY])],
    "r_cast": [("r_cast", seq(range(6), [50, 60, 80, 90, 100, 120]), [BODY])],
    # the 5 undying seconds: flames round him (under him). A buff's picture is never mirrored by his facing
    # (champion-data: league_fiora's parry), so it stays centred on the pivot and is wide enough for both sides
    "r_rage": [("r_rage", seq(range(4), [100] * 4), [FEET])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "tryndamere_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_tryndamere_fx", FX), ("league_tryndamere_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

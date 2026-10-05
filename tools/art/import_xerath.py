#!/usr/bin/env python3
"""Import Xerath's effects (assets/source/xerath/PROMPTS_FX.md, 27 sheets) as the game sheets league_xerath_fx and
league_xerath_big.

    python tools/art/import_xerath.py --raw assets/source/xerath/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_xerath.py                                       # native strips -> the effect sheets

The body comes from import_native.py (Codex's strips with fix_xerath_strips.py's lean). --raw turns each frame of Codex's
drawings (generated originals, semi-transparent, about 2172x724, the frames in equal columns) into a cell of a native
strip (assets/source/xerath/xerath_fx_<name>.png, 8x, plus xerath_fx_anchors.json) the way import_varus.py does: each
game pixel the majority colour of the source pixels it covers, opaque when a quarter of them are solid, every colour
snapped to the ramps the pack gave that effect (ARC, DEEP and the INK outline of the stone shards), then the light's
darkest ring comes off (import_jhin.unrim). One scale per strip: `size` game px over the drawings' widest (w), tallest
(h) or larger side (m). Then the pack's symmetry rules where the drawing missed them (Codex's HANDOFF lists them): the
beams mirrored top to bottom about their middle row (cast leftward the engine turns them upside down), the pictures a
buff or a follow-less caster view plays on him whichever way he faces (e_stun, w_slow, r_chan, r_rise, r_end) mirrored
left to right about the anchor; r_rise's column is hollowed where his body stands (its fourth frame filled him with a
bright mist), so it never covers him.
Anchors (source pixels): the flying things on their front (3 px in from the tip), the hits and flashes on their white
core, the charge on the orb of its last frame, the rings on the ground on their widest row, the pillar and the shell on
the ring of their landing frame, the summoning flash and the ground burst on their lowest row, the stun mark on its box.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the leg tips 11
under the pivot) measured on the finished strips (pack_xerath_fx.SHOTS): the front claw in the release frames
(18, -15), the raised claw while Q charges (10, -20) - and times it by the kit (tools/kit/build_xerath.py, 60 ticks a
second). Writes league/effects/league_xerath_fx and league_xerath_big.
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
import import_varus as V  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "xerath")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (tools/art/pack_xerath_fx.py)
RAMPS = {
    "ARC": ["1A48C0", "1E8CF0", "4CD4FF", "9AF2FF", "E0FCFF", "FFFFFF"],
    "DEEP": ["120C3A", "241C70", "3A34B0", "5A64E8", "8AA8FF"],
    "INK": ["0A0A12"],                       # the stone shards' outline
}
# the light's darkest shade on its edge goes (or takes the next); the ink outline stays
RIM = {"1A48C0": "1E8CF0", "120C3A": "241C70"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps, sym ("lr" / "tb"), hollow (half width)
RAW = {
    "a_orb": dict(n=4, size=14, measure="w", anchor="front", ramps="ARC"),
    "a_orb_p": dict(n=4, size=20, measure="w", anchor="front", ramps="ARC"),
    "a_flash": dict(n=3, size=12, measure="m", anchor=("fixed", "core", 0), ramps="ARC"),
    "a_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="ARC"),
    "p_surge": dict(n=4, size=18, measure="m", anchor=("fixed", "core", 0), ramps="ARC"),
    "p_hit": dict(n=5, size=20, measure="m", anchor=("fixed", "core", 0), ramps="ARC"),
    "q_charge": dict(n=8, size=20, measure="m", anchor=("fixed", "core", 7), ramps="ARC"),
    "q_charge_s": dict(n=4, size=18, measure="m", anchor=("fixed", "core", 3), ramps="ARC"),
    "q_fire": dict(n=3, size=24, measure="w", anchor=("fixed", "core", 0), ramps="ARC"),
    "q_beam": dict(n=3, size=56, measure="w", anchor="front", ramps="ARC", sym="tb"),
    "q_beam_s": dict(n=3, size=36, measure="w", anchor="front", ramps="ARC", sym="tb"),
    "q_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="ARC"),
    "e_cast": dict(n=3, size=16, measure="m", anchor=("fixed", "core", 0), ramps="ARC"),
    "e_orb": dict(n=4, size=16, measure="w", anchor="front", ramps="ARC"),
    "e_hit": dict(n=5, size=22, measure="m", anchor=("fixed", "core", 0), ramps="ARC"),
    "e_stun": dict(n=4, size=14, measure="w", anchor="box", ramps="ARC", sym="lr"),
    "w_mark": dict(n=8, size=54, measure="w", anchor="ellipse", ramps="ARC DEEP"),
    "w_blast": dict(n=6, size=64, measure="h", anchor=("fixed", "ellipse", 2), ramps="ARC DEEP"),
    "w_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "low", 0), ramps="ARC"),
    "w_slow": dict(n=4, size=18, measure="w", anchor="ellipse", ramps="DEEP ARC", sym="lr"),
    "r_rise": dict(n=6, size=64, measure="h", anchor=("fixed", "ellipse", 0), ramps="INK ARC DEEP", sym="lr",
                   hollow=7),
    "r_chan": dict(n=6, size=48, measure="w", anchor="ellipse", ramps="DEEP ARC", sym="lr"),
    "r_cast_shot": dict(n=3, size=20, measure="h", anchor=("fixed", "low", 0), ramps="ARC"),
    "r_end": dict(n=4, size=44, measure="h", anchor=("fixed", "low", 0), ramps="ARC", sym="lr"),
    "r_mark": dict(n=7, size=38, measure="w", anchor="ellipse", ramps="ARC DEEP"),
    "r_bolt": dict(n=7, size=80, measure="h", anchor=("fixed", "ellipse", 3), ramps="ARC DEEP"),
    "r_hit": dict(n=4, size=18, measure="m", anchor=("fixed", "core", 0), ramps="ARC"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def symmetric(out, cell, anc, n, how):
    """Each cell mirrored about its anchor: `lr` the left half onto the right, `tb` the top half onto the bottom."""
    tw, th = cell
    L, U = anc
    for i in range(n):
        c = out[:, i * tw:(i + 1) * tw]
        if how == "lr":
            left = c[:, :L].copy()
            c[:, L + 1:L + 1 + L] = left[:, ::-1][:, :tw - L - 1]
        else:
            top = c[:U].copy()
            c[U + 1:U + 1 + U] = top[::-1][:th - U - 1]


def hollow(out, cell, anc, n, half):
    """Clear the figure's place: the columns within `half` of the anchor, from 2 rows over the ground up."""
    tw, th = cell
    L, U = anc
    for i in range(n):
        c = out[:, i * tw:(i + 1) * tw]
        c[:U - 2, L - half:L + half + 1] = 0


def from_raw(folder):
    V.RIM = RIM                              # import_varus.convert's unrim reads its module's RIM
    V.TF = TF
    anchors = {}
    for name, spec in RAW.items():
        fn = f"xerath_fx_{name}.png"
        _, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = V.grid(a, spec["n"])
        out, cell, anc, s, ext = V.convert(name, spec, a, solid, idx, pal, rects)
        if spec.get("sym"):
            symmetric(out, cell, anc, spec["n"], spec["sym"])
        if spec.get("hollow"):
            hollow(out, cell, anc, spec["n"], spec["hollow"])
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"xerath_fx_{name}.png")))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": spec["n"]}
        print(f"xerath_fx_{name}.png  {spec['n']} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "xerath_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"xerath_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"xerath_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (pack_xerath_fx.SHOTS)
CLAW = (18, -15)            # the front claw in the release frames (attack 4, Q 6, E 3, R's shots)
Q_HAND = (10, -20)          # the raised front claw while Q charges (skill 1-5)
SHOT = (18, -11)            # the summoning flash's lowest row, a few rows under the claw
HIT = (0, -12)              # a hit on the upper body of a 36-44 px unit
OVER = (0, -36)             # the stun mark's middle over the head (his idle tops 32 over the pivot)
FEET = (0, 10)              # a ring on the ground round a unit's feet (the soles or leg tips 11 under the pivot)
SOLES = (0, 11)             # what stands on the ground: its lowest row there
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the orb: 55 px at 4.5 px a tick, homing (twice that); out of the claw 18 px away: 4 empty ticks
    "a_orb": [("a_orb", flight(4, 70, 450, lead=4), [(0, 0)])],
    "a_orb_p": [("a_orb_p", flight(4, 70, 450, lead=4), [(0, 0)])],
    "a_flash": [("a_flash", seq(range(3), [30, 40, 50]), [CLAW])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_surge": [("p_surge", seq(range(4), [50, 60, 70, 80]), [CLAW])],
    "p_hit": [("p_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    # Q: the full charge lasts q_full_t (54 ticks = 900 ms), the quick one q_quick_t (22 = 367 ms)
    "q_charge": [("q_charge", seq(range(8), [100, 100, 100, 110, 110, 120, 120, 140]), [Q_HAND])],
    "q_charge_s": [("q_charge_s", seq(range(4), [80, 90, 100, 100]), [Q_HAND])],
    "q_fire": [("q_fire", seq(range(3), [40, 50, 60]), [CLAW])],
    # the beam: 150 px at 15 px a tick (10 ticks); the quick one 95 px; one empty tick out of the claw
    "q_beam": [("q_beam", flight(3, 50, 250, lead=1), [(0, 0)])],
    "q_beam_s": [("q_beam_s", flight(3, 50, 200, lead=1), [(0, 0)])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # E: the orb 110 px at 4 px a tick (28 ticks); out of the claw 18 px away: 4 empty ticks
    "e_cast": [("e_cast", seq(range(3), [40, 50, 60]), [CLAW])],
    "e_orb": [("e_orb", flight(4, 70, 500, lead=4), [(0, 0)])],
    "e_hit": [("e_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [50, 60, 70, 80]), [SOLES])],
    # R
    "r_cast_shot": [("r_cast_shot", seq(range(3), [40, 50, 60]), [SHOT])],
    "r_end": [("r_end", seq(range(4), [70, 80, 90, 100]), [SOLES])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # buffs (looped while they last): the stun over the head, the slow at the feet
    "e_stun": [("e_stun", seq(range(4), [100] * 4), [OVER])],
    "w_slow": [("w_slow", seq(range(4), [110] * 4), [FEET])],
}
BIG = {
    # W: the eye opens where the lob lands; the blast comes w_delay - 1 (29 ticks = 483 ms) later
    "w_mark": [("w_mark", seq(range(8), [60] * 8), [FEET])],
    "w_blast": [("w_blast", seq(range(6), [50, 60, 70, 80, 90, 100]), [FEET])],
    # R: the rise for r_deploy (30 ticks = 500 ms), the rune circle under him while he channels (a buff: never mirrored
    # by his facing, so symmetric about the pivot), each shell's mark for r_delay - 8 (28 ticks = 467 ms) until the bolt,
    # whose third frame - the impact - meets the blast at r_delay (36 ticks = 600 ms)
    "r_rise": [("r_rise", seq(range(6), [70, 80, 80, 90, 90, 90]), [SOLES])],
    "r_chan": [("r_chan", seq(range(6), [110] * 6), [FEET])],
    "r_mark": [("r_mark", seq(range(7), [70, 70, 70, 70, 70, 70, 50]), [FEET])],
    "r_bolt": [("r_bolt", seq(range(7), [60, 60, 70, 90, 100, 110, 120]), [FEET])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "xerath_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_xerath_fx", FX), ("league_xerath_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Import Brand's effects (assets/source/brand/PROMPTS_FX.md, 20 sheets) as the game sheets league_brand_fx and
league_brand_big, and the hand flashes drawn into his own frames (assets/source/native/brand_bake.json).

    python tools/art/import_brand.py --raw <Codex's brand-fx folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_brand.py                                  # native strips -> the effect sheets
    python tools/art/import_native.py --hero brand                    # then: the bake into his frames

Codex delivered generated originals (about 2172x724, semi-transparent edges, the frames in equal columns - the warning
circle and the spread in two rows: its HANDOFF.md). --raw turns each frame into a cell of a native strip
(assets/source/brand/brand_fx_<name>.png, 8x, plus brand_fx_anchors.json) as import_gwen.py does: each game pixel the
majority colour of the source pixels it covers, every colour snapped to the ramps the pack gave that effect, the
darkest shade off the edge of fire (import_jhin.unrim; the stack marks keep their dark outline). One scale per strip:
`size` game px over the drawings' widest (w), tallest (h) or larger side (m).

Red side and blue side alike (the user's rule): the client mirrors his own frames with his facing and never an effect
picture, so
- the hand flash rides in his frames (brand_bake.json) - and is mirrored both ways anyway, as hands point anywhere;
- the three projectiles are mirrored top to bottom about their middle row (cast leftward the engine turns them over);
- what plays round him or on the ground whichever way he faces - R's swirl (played after the cast's first tick, not
  following), the burn, the timer ring, the stun halo, the embers, the warning circle, the pillar, the spread, the
  blast, the burst on a lit unit, the dropping seed - is mirrored left to right about its middle; the stack pips are
  placed by this script, one sheet cell per count.
Spots (game px from the pivot, x forward, y down; his soles 11 under it) come from the finished strips
(tools/art/rig_brand.py via pack_brand_fx.hand_points): the fire hands in the release frames.
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

SRC = os.path.join(ROOT, "assets", "source", "brand")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
Z = 8
PIVOT = (64, 88)                # rig_brand's standing point on the 128 canvas

# the pack's ramps, darkest first (tools/art/pack_brand_fx.py)
RAMPS = {
    "FIRE": ["5E0C06", "A81A08", "E0360A", "FF6A0C", "FFA41C", "FFD64A", "FFF2A8", "FFFDF0"],
    "LAVA": ["3A0E08", "7A1E0A", "C2400C", "F27A12", "FFC23A", "FFF2B0"],
    "TAR": ["1A1216", "2E2228", "4A3C44", "6A5660"],
    "INK": ["1A0A08"],                       # the stack pips' outline
}
# fire's darkest shade on its edge goes (or takes the next)
RIM = {"5E0C06": "A81A08", "3A0E08": "7A1E0A"}

# raw -> native: frames n (rows: grid rows), size (game px) over measure, anchor, ramps, sym ("lr" / "tb" / "both"),
# rim, open_ (his place cleared round the anchor's column: half width), top (rows kept over the cleared place)
RAW = {
    "c_flash": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 1), ramps="FIRE", sym="both"),
    "r_cast": dict(n=6, size=48, measure="h", anchor=("fixed", "low", 0), ramps="FIRE", sym="lr", open_=5, top=10),
    "a_bolt": dict(n=4, size=14, measure="w", anchor="front", ramps="FIRE", sym="tb"),
    "q_ball": dict(n=4, size=24, measure="w", anchor="front", ramps="FIRE TAR", sym="tb"),
    "r_ball": dict(n=4, size=18, measure="w", anchor="front", ramps="FIRE LAVA", sym="tb"),
    "a_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="FIRE"),
    "q_hit": dict(n=5, size=22, measure="m", anchor=("fixed", "core", 0), ramps="FIRE TAR"),
    "e_hit": dict(n=5, size=24, measure="h", anchor=("fixed", "low", 0), ramps="FIRE", sym="lr"),
    "r_drop": dict(n=4, size=28, measure="h", anchor=("fixed", "low", 3), ramps="FIRE LAVA", sym="lr"),
    "r_hit": dict(n=4, size=18, measure="m", anchor=("fixed", "core", 0), ramps="FIRE LAVA"),
    "p_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="FIRE TAR"),
    "w_mark": dict(n=6, rows=2, size=46, measure="w", anchor=("fixed", "ellipse", 5), ramps="FIRE LAVA", sym="lr"),
    "w_pillar": dict(n=7, size=72, measure="h", anchor=("fixed", "low", 0), ramps="FIRE TAR", sym="lr"),
    "e_flare": dict(n=6, rows=2, size=58, measure="w", anchor=("fixed", "ellipse", 3), ramps="FIRE TAR", sym="lr"),
    "p_boom": dict(n=7, size=54, measure="w", anchor=("fixed", "core", 0), ramps="FIRE TAR", sym="lr"),
    "p_stacks": dict(n=3, size=6, measure="h", anchor="box", ramps="INK FIRE", rim=False),
    "p_burn": dict(n=4, size=30, measure="h", anchor=("fixed", "box", 0), ramps="FIRE", sym="lr"),
    "p_unstable": dict(n=4, size=30, measure="w", anchor=("fixed", "ellipse", 0), ramps="FIRE", sym="lr"),
    "q_stun": dict(n=4, size=18, measure="w", anchor=("fixed", "box", 0), ramps="FIRE", sym="lr"),
    "r_slow": dict(n=4, size=24, measure="w", anchor=("fixed", "ellipse", 0), ramps="FIRE TAR", sym="lr"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def open_middle(out, cell, anc, n, half, top=0):
    """His place cleared in a picture drawn round him: the columns within `half` of the anchor, below `top` rows."""
    tw, th = cell
    L, U = anc
    for i in range(n):
        out[top:max(top, U - 2), i * tw + L - half:i * tw + L + half + 1] = 0


def from_raw(folder):
    V.TF = TF
    anchors = {}
    for name, spec in RAW.items():
        V.RIM = RIM if spec.get("rim", True) else {}      # import_varus.convert's unrim reads its module's RIM
        J.RIM = V.RIM
        fn = f"brand_fx_{name}.png"
        _, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = V.grid(a, spec["n"], spec.get("rows", 1))
        out, cell, anc, s, ext = V.convert(name, dict(spec), a, solid, idx, pal, rects)
        sym = spec.get("sym")
        for how in (("lr", "tb") if sym == "both" else (sym,) if sym else ()):
            X.symmetric(out, cell, anc, spec["n"], how)
        if spec.get("open_"):
            open_middle(out, cell, anc, spec["n"], spec["open_"], spec.get("top", 0))
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"brand_fx_{name}.png")))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": spec["n"]}
        print(f"brand_fx_{name}.png  {spec['n']} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']:.1f} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "brand_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"brand_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"brand_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def hands():
    """The fire hands in the release frames, from the pivot (pack_brand_fx.hand_points on rig_brand's strips)."""
    import pack_brand_fx as PF
    _, shots = PF.hand_points()
    out = {}
    for tag, k, what, pts in shots:
        if what.startswith("c_flash"):
            out[(tag, k)] = [(x - PIVOT[0], y - PIVOT[1]) for x, y in pts]
    return out


HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
BODY = (0, -8)                  # round a unit: the burn's flames
OVER = (0, -37)                 # over the head (his crown 31 over the pivot, the flames higher)
FEET = (0, 10)                  # a ring on the ground round a unit's feet (the soles 11 under the pivot)
SOLES = (0, 11)                 # what stands on the ground: its lowest row there
CHEST = (0, 0)                  # the dropping seed's lowest point (12 over the standing point)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the attack's bolt: 52 px at 4.5 px a tick, homing (twice that); out of the hand 17 px away: 4 empty ticks
    "a_bolt": [("a_bolt", flight(4, 70, 400, lead=4), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # Q: 95 px at 8 px a tick (12 ticks); one empty tick out of the hand
    "q_ball": [("q_ball", flight(4, 60, 300, lead=1), [(0, 0)])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    # W's hit on each unit in the pillar: Q's fire burst (the pack has no picture of its own for it)
    "w_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "e_hit": [("e_hit", seq(range(5), [50, 60, 70, 70, 80]), [SOLES])],
    # R: the swirl round him (late, not following); the seed 65 px at 4 px a tick; each bounce's drop r_fall
    # (6 ticks = 100 ms) before the hit
    "r_cast": [("r_cast", seq(range(6), [60, 70, 80, 80, 90, 100]), [SOLES])],
    "r_ball": [("r_ball", flight(4, 70, 500, lead=2), [(0, 0)])],
    "r_drop": [("r_drop", seq(range(4), [20, 25, 25, 30]), [CHEST])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_hit": [("p_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # buffs (looped while they last)
    "p_burn": [("p_burn", seq(range(4), [110] * 4), [BODY])],
    "p_unstable": [("p_unstable", seq(range(4), [100] * 4), [FEET])],
    "q_stun": [("q_stun", seq(range(4), [90] * 4), [OVER])],
    "r_slow": [("r_slow", seq(range(4), [120] * 4), [FEET])],
    # the hand flash (brand_bake.json), one tag per release with its hands
    "c_flash": [("c_flash", seq(range(4), [40, 40, 50, 50]), [(0, 0)])],
}
BIG = {
    # W: the warning circle where the lob lands until the pillar (w_delay - 4 = 32 ticks = 533 ms), its frames 2-5 looped;
    # the pillar's brightest frame (4) at the damage (5 ticks after it appears)
    "w_mark": [("w_mark", seq([0, 1, 2, 3, 4, 1, 2, 3, 4, 5], [60, 50, 50, 50, 50, 50, 50, 50, 50, 70]), [FEET])],
    "w_pillar": [("w_pillar", seq(range(7), [40, 30, 30, 80, 80, 90, 110]), [FEET])],
    "e_flare": [("e_flare", seq(range(6), [50, 60, 70, 80, 90, 110]), [FEET])],
    "p_boom": [("p_boom", seq(range(7), [50, 60, 70, 80, 90, 100, 130]), [(0, -8)])],
}
STACKS = {"p_s1": 0, "p_s2": 1, "p_s3": 2}      # cell k: k + 1 flames


def build(table):
    with open(G.lp(os.path.join(SRC, "brand_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    hand = hands() if table is FX else {}
    for tag, parts in table.items():
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            if tag == "c_flash":                    # one tag per release frame, a flash on each of its hands
                for (t, k), pts in hand.items():
                    out[f"c_flash_{t}_{k}"] = [(J.place(strip[i], anchors[src]["anchor"], pts), ms)
                                               for i, ms in frames]
                continue
            out.setdefault(tag, [])
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                out[tag].append((J.place(strip[k], anchors[src]["anchor"], spots), ms))
    if table is FX:
        strip = cells("p_stacks", anchors["p_stacks"]["frames"])
        for tag, k in STACKS.items():
            c = strip[k]
            ys, xs = np.nonzero(c[..., 3])
            m = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            out[tag] = [(J.place(m, (m.shape[1] / 2, m.shape[0] / 2), [OVER]), 600)]
    return out


# the flashes drawn into his frames (import_native.bake), at the release frames' times (rig_brand.MS)
BAKE = {"fx": "league_brand_fx", "items": [
    {"tag": "c_flash_attack_4", "into": "attack", "at_ms": 180},     # attack 4 (the throw): 180-250 ms
    {"tag": "c_flash_skill2_3", "into": "skill2", "at_ms": 100},     # skill2 3 (E, both hands flung wide): 100-170
    {"tag": "c_flash_skill2_6", "into": "skill2", "at_ms": 290},     # skill2 6 (Q, the thrust): 290-360
    {"tag": "c_flash_skill_4", "into": "skill", "at_ms": 180},       # skill 4 (W, the slam): 180-260
]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_brand_fx", FX), ("league_brand_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    text = json.dumps(BAKE, indent=1) + "\n"
    with open(G.lp(os.path.join(NATIVE, "brand_bake.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("assets/source/native/brand_bake.json:", len(BAKE["items"]), "items")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Import Senna's effects (assets/source/senna/PROMPTS_FX.md, 21 sheets) as the game sheets league_senna_fx and
league_senna_big.

    python tools/art/import_senna.py --raw assets/source/senna/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_senna.py                                     # native strips -> the effect sheets

The body comes from import_native.py (tools/art/fix_senna_strips.py built the strips). --raw turns each frame of
Codex's generated originals (about 2000 px wide, semi-transparent edges, the frames cut by the delivery's
manifest.json rects) into a cell of a native strip (assets/source/senna/senna_fx_<name>.png, 8x, plus
senna_fx_anchors.json) the way import_olaf.py does: each game pixel the majority colour of the source pixels it
covers, opaque when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect
(work/se/fx_pack_se.py: MIST, SHADE, HOLY), then the lights' darkest ring comes off (import_jhin.unrim). One scale
per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m).
Anchors (source pixels): the flying shots on their front, the hits on their white core, the Q beam on its left end
(the muzzle) and its densest row (the line), the rings on the ground on their widest row, what stands on the ground
on its lowest row. Codex cut its frames on the transparent gaps, so the frames of one strip are not one width: the
pictures that stand on a spot (`xbox`) take each frame's own box middle across and one frame's ground or ring row
down.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (tools/kit/build_senna.py, 60 ticks a second). Her cannon is long: the muzzle is
44 px in front of the pivot on the attack's shot frame, 43 on Q's, 40 on W's (league_senna#anim.fanim, the 85% sprite), so the
shots stay hidden until they pass it and the Q beam's picture starts there.
The red side: the client never mirrors a data picture. The shots and the beam are turned to their flight and stay as
drawn; everything on a unit or on the ground is drawn over its own left-right flip (league_xayah's FLIP_LR).
Writes league/effects/league_senna_fx and league_senna_big.
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
import import_xayah as X  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "senna")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps (work/se/fx_pack_se.py), darkest first
RAMPS = {
    "MIST": ["08302A", "0E5444", "1A8A6A", "3CCB9C", "86F4CC", "D8FFF0", "FFFFFF"],
    "SHADE": ["1A1B22", "2C2F3A", "4A4F5E"],
    "HOLY": ["9A5E1C", "D9952E", "F7C65A", "FFE79A", "FFF8DA", "FFFFFF"],
}
# the lights' darkest shade on their edge goes (or takes the next)
RIM = {"08302A": "0E5444", "1A1B22": "2C2F3A", "9A5E1C": "D9952E"}

# Q: the beam's picture runs from the muzzle (43 px out on Q's shot frame) to the line's end (q_len 130 px); a
# LineRangeProjectile's picture is centred on its line, so its left end sits 65 - 43 = 22 px behind the middle
Q_LEN, Q_MUZZLE = 130, 43
Q_DRAWN = Q_LEN - Q_MUZZLE

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_shot": dict(n=4, size=14, measure="w", anchor="front", ramps="MIST SHADE"),
    "a_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="MIST SHADE"),
    "p_mark": dict(n=4, size=22, measure="w", anchor=("xbox", "ellipse", 0), ramps="MIST SHADE"),
    "p_take": dict(n=5, size=26, measure="h", anchor=("xbox", "core", 0), ramps="MIST SHADE"),
    "p_gain": dict(n=4, size=22, measure="w", anchor=("xbox", "core", 2), ramps="MIST SHADE"),
    "q_beam": dict(n=5, size=Q_DRAWN, measure="w", anchor="beam", ramps="MIST SHADE"),
    "q_hit": dict(n=4, size=16, measure="w", anchor="core", ramps="MIST SHADE"),
    "q_heal": dict(n=4, size=28, measure="h", anchor=("xbox", "ellipse", 0), ramps="HOLY"),
    "q_slow": dict(n=4, size=18, measure="w", anchor=("xbox", "ellipse", 0), ramps="MIST SHADE"),
    "w_mist": dict(n=4, size=16, measure="w", anchor="front", ramps="MIST SHADE"),
    "w_hit": dict(n=4, size=18, measure="m", anchor="core", ramps="MIST SHADE"),
    "w_cling": dict(n=4, size=26, measure="h", anchor=("xbox", "low", 0), ramps="MIST SHADE"),
    "w_burst": dict(n=6, size=58, measure="w", anchor=("xbox", "ellipse", 1), ramps="MIST SHADE"),
    "w_root": dict(n=4, size=20, measure="w", anchor=("xbox", "low", 0), ramps="MIST SHADE"),
    "e_mist": dict(n=6, size=84, measure="w", anchor=("xbox", "low", 2), ramps="MIST SHADE"),
    "e_ms": dict(n=4, size=18, measure="w", anchor=("xbox", "ellipse", 0), ramps="MIST SHADE"),
    "r_core": dict(n=4, size=44, measure="w", anchor="front", ramps="MIST SHADE"),
    "r_light": dict(n=4, size=96, measure="h", anchor="front", ramps="HOLY"),
    "r_hit": dict(n=5, size=28, measure="w", anchor="core", ramps="MIST SHADE HOLY"),
    "r_sh": dict(n=4, size=34, measure="h", anchor=("xbox", "low", 3), ramps="HOLY"),
    "r_shield": dict(n=4, size=34, measure="h", anchor="box", ramps="HOLY"),
}


def anchor(how, k, a, solid, rects, s):
    """(x, y) of frame k's anchor in the source: import_twistedfate's, plus `beam` (the left end of the strip's
    drawings, the same column in every frame, on each frame's densest row) and ("xbox", how, j) (frame k's box middle
    across, frame j's `how` anchor down, from the top of its rect)."""
    x, y, w, h = rects[k]
    if how == "beam":
        left = min(np.nonzero(solid[ry:ry + rh, rx:rx + rw].any(0))[0].min() for rx, ry, rw, rh in rects)
        row = solid[y:y + h, x:x + w].sum(1).argmax()
        return x + left, y + row + 0.5
    if isinstance(how, tuple) and how[0] == "xbox":
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        j = how[2]
        _, ay = TF.anchor(how[1], j, a, solid, rects, s)
        return x + (xs.min() + xs.max() + 1) / 2, y + ay - rects[j][1]
    return TF.anchor(how, k, a, solid, rects, s)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(x["file"]): x for x in json.load(f)["assets"]}
    V.RAMPS = RAMPS
    V.RIM = RIM
    V.anchor = anchor
    anchors = {}
    for name, spec in RAW.items():
        fn = f"senna_fx_{name}.png"
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
    with open(G.lp(os.path.join(SRC, "senna_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"senna_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"senna_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down): the soles 11 under it, her crown 29 over it (the 40-row design)
HIT = (0, -11)              # a hit on the upper body of a unit
CHEST = (0, -9)             # the mark's ring round a champion's chest
BODY = (0, -9)              # a shield round a body
CANNON = (0, -6)            # her cannon at her waist: the gained Mist's spark
FEET = (0, 10)              # a ring on the ground round a unit's feet
GROUND = (0, 11)            # what stands on the ground by its lowest row
Q_LINE = (Q_MUZZLE - Q_LEN / 2, 0)   # the beam's left end on its line
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the attack's shot: 7 px a tick from the pivot, hidden for the 6 ticks it spends inside the 44 px cannon; the
    # picture loops over twice its 62 px flight
    "a_shot": [("a_shot", flight(4, 50, 300, lead=6), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # the passive: the mark on a champion (p_mark 4 s), the soul torn out of it, the Mist gained at her cannon
    "p_mark": [("p_mark", seq(range(4), [110] * 4), [CHEST])],
    "p_take": [("p_take", seq(range(5), [50, 70, 80, 90, 100]), [HIT])],
    "p_gain": [("p_gain", seq(range(4), [60, 70, 80, 100]), [CANNON])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_heal": [("q_heal", seq(range(4), [60, 80, 90, 110]), [FEET])],
    "q_slow": [("q_slow", seq(range(4), [110] * 4), [FEET])],
    # W: 4.5 px a tick, hidden for the 8 ticks inside the cannon (40 px); 110 px of flight
    "w_mist": [("w_mist", flight(4, 60, 600, lead=8), [(0, 0)])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 80]), [HIT])],
    "w_cling": [("w_cling", seq(range(4), [100] * 4), [GROUND])],
    "w_root": [("w_root", seq(range(4), [110] * 4), [GROUND])],
    "e_ms": [("e_ms", seq(range(4), [110] * 4), [FEET])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 80, 100]), [HIT])],
    "r_sh": [("r_sh", seq(range(4), [50, 70, 90, 120]), [GROUND])],
    "r_shield": [("r_shield", seq(range(4), [120] * 4), [BODY])],
}
BIG = {
    # the LineRangeProjectile lives q_beam's delay 18 ticks (300 ms): the thin line, the beam, its fading
    "q_beam": [("q_beam", seq(range(5), [33, 50, 67, 67, 66]), [Q_LINE])],
    "w_burst": [("w_burst", seq(range(6), [40, 50, 60, 80, 100, 120]), [FEET])],
    "e_mist": [("e_mist", seq(range(6), [60, 80, 100, 150, 200, 250]), [GROUND])],
    # R: 30 px a tick, its 260 px in 9 ticks; the first tick hidden (the picture points up on a projectile's first move)
    "r_core": [("r_core", flight(4, 50, 500, lead=1), [(0, 0)])],
    "r_light": [("r_light", flight(4, 60, 500, lead=1), [(0, 0)])],
}
SRC_OF = {}                                          # a tag whose cells come from another strip
NO_FLIP = {"a_shot", "w_mist", "q_beam", "r_core", "r_light"}   # turned with their flight
FLIP_LR = (set(FX) | set(BIG)) - NO_FLIP

# the shield's ring: Codex drew it 3-4 px thick, a gold disc over the whole body for its 3 s - only its bright rim
# stays (the ramp's two darkest shades go)
THIN = {"r_shield": ("9A5E1C", "D9952E")}


def thin(cell, hexes_):
    out = cell.copy()
    for h in hexes_:
        rgb = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)
        out[(out[..., :3] == rgb).all(-1)] = 0
    return out


def build(table):
    with open(G.lp(os.path.join(SRC, "senna_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_senna_fx", FX), ("league_senna_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

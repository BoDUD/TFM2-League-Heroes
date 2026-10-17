#!/usr/bin/env python3
"""Import Karma's effects (assets/source/karma/PROMPTS_FX.md, 24 strips) as the game sheets league_karma_fx and
league_karma_big.

    python tools/art/import_karma.py

The body comes from tools/art/fix_karma_strips.py + import_native.py. Codex delivered every effect at game size
already (assets/source/karma/codex_fx/native/karma_fx_<name>_1x.png: one pixel a game pixel, equal cells, its
manifest.json giving each strip's cell size and anchor), so nothing is rescaled here: each cell goes by its anchor on a
spot from the pivot (game px, x right, y down; the soles 11 under the pivot) and is timed by the kit
(tools/kit/build_karma.py, 60 ticks a second). Anchors: the flying ones on their middle, the hits on their core, the
rings on the ground on the ellipse's middle, the auras round a body on the feet, the bursts on the ground point.
The red side: the client never mirrors a data picture. The flying ones (bolt, flames, beam head, tether segments) are
turned to their flight - drawn over their own top-bottom flip; everything on a unit or on the ground is drawn as stored
whichever way she faces - drawn over its own left-right flip (league_xayah's over_flip). Every frame is centred on the
pivot. Writes league/effects/league_karma_fx and league_karma_big.
"""
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
import import_xayah as X  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "karma", "codex_fx")
MOD = os.path.join(ROOT, "league")

# spots from the pivot (game px, x right, y down)
HIT = (0, -11)              # a hit on the upper body of a 36-44 px unit
SOLES = (0, 11)             # an aura drawn round a body, anchored on its feet
FEET = (0, 10)              # a ring on the ground round a unit's feet; a point on the ground
CENTRE = (0, 0)             # a projectile (centred on itself)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight


def loop(n, ms):
    return seq(range(n), [ms] * n)


FX = {
    # the flying ones: the bolt 5000 a tick for ~55000 (11 ticks), the flames 5500 for 70000 (13), the beam head at
    # 100000 (one tick), the tether's segments 3000 a tick back to her (up to ~32 ticks) - looped and held
    "a_bolt": [("a_bolt", flight(4, 60, 400), [CENTRE])],
    "q_ball": [("q_ball", flight(4, 60, 500), [CENTRE])],
    "rq_ball": [("rq_ball", flight(4, 60, 500), [CENTRE])],
    "w_beam": [("w_beam", flight(4, 50, 200), [CENTRE])],
    "w_tether": [("w_tether", flight(4, 80, 1200), [CENTRE])],
    # the hits and the flashes on a unit
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 80, 100]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 80]), [HIT])],
    "w_snap": [("w_snap", seq(range(5), [50, 60, 70, 80, 100]), [SOLES])],
    "e_land": [("e_land", seq(range(5), [50, 60, 70, 80, 100]), [SOLES])],
    "r_cast": [("r_cast", seq(range(5), [50, 70, 90, 110, 130]), [SOLES])],
    "rw_heal": [("rw_heal", seq(range(5), [60, 80, 100, 120, 140]), [SOLES])],
    # the buffs' loops
    "e_on": [("e_on", loop(4, 120), [SOLES])],
    "e_haste": [("e_haste", loop(4, 100), [FEET])],
    "w_mark": [("w_mark", loop(4, 110), [SOLES])],
    "w_root": [("w_root", loop(4, 110), [FEET])],
    "mantra": [("mantra", loop(4, 130), [SOLES])],
    "q_slow": [("q_slow", loop(4, 100), [FEET])],
    "rq_slow": [("rq_slow", loop(4, 100), [FEET])],
}
BIG = {
    "q_boom": [("q_boom", seq(range(6), [40, 50, 70, 90, 110, 130]), [FEET])],
    "rq_boom": [("rq_boom", seq(range(6), [40, 50, 70, 90, 110, 140]), [FEET])],
    # the field lies rq_wait = 90 ticks; the blast plays from rq_wait - 4 (86 ticks = 1433 ms)
    "rq_field": [("rq_field", seq(range(8), [180] * 7 + [190]), [FEET])],
    "rq_blast": [("rq_blast", seq(range(6), [50, 60, 80, 100, 120, 150]), [FEET])],
    "re_wave": [("re_wave", seq(range(6), [50, 60, 70, 80, 100, 120]), [FEET])],
}
FLIP_TB = {"a_bolt", "q_ball", "rq_ball", "w_beam", "w_tether"}


def manifest():
    with open(G.lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig") as f:
        return {x["name"]: x for x in json.load(f)["assets"]}


def cells(name, spec):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, "native", f"karma_fx_{name}_1x.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    w, h = spec["cell_native"]
    n = spec["frame_count"]
    if a.shape[1] != w * n or a.shape[0] != h:
        sys.exit(f"karma_fx_{name}_1x.png is {a.shape[1]}x{a.shape[0]}, {n} cells of {w}x{h} expected")
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def build(table, man):
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            spec = man[src]
            strip = cells(src, spec)
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                f = J.place(strip[k], spec["native_anchor"], spots)
                f = X.over_flip(f, "tb" if tag in FLIP_TB else "lr")
                out[tag].append((f, ms))
    return out


def main():
    man = manifest()
    missing = (set(FX) | set(BIG)) - set(man)
    if missing:
        sys.exit(f"not in the delivery: {sorted(missing)}")
    for sheet, table in (("league_karma_fx", FX), ("league_karma_big", BIG)):
        tags = build(table, man)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

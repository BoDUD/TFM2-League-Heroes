#!/usr/bin/env python3
"""Import Shen's effects (assets/source/shen/PROMPTS_FX.md, 15 sheets) as the game sheets league_shen_fx and
league_shen_big.

    python tools/art/import_shen.py --raw <Codex's shen-fx folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_shen.py                                  # native strips -> the effect sheets

The body comes from tools/art/fix_shen_strips.py + import_native.py. Codex's exports (shen_fx_<name>.png) are on the
pack's grid already - every game pixel a flat 16 x 16 block, alpha 0/255, the pack's ramps, no black - so --raw reads
each block's colour (refusing a sheet whose blocks are not flat), cuts the equal cells and keeps Codex's anchor from its
manifest.json (`pivot`, in export px: the cell's middle, or the feet / ground point the pack put above the bottom).
It writes assets/source/shen/shen_fx_<name>.png (8x) and shen_fx_anchors.json.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (tools/kit/build_shen.py, 60 ticks a second).
The red side: the client never mirrors a data picture. The flying blade and the dash's smoke turn with their flight -
drawn over their own top-bottom flip; everything on a unit or on the ground is drawn over its own left-right flip
(league_xayah's over_flip; Codex drew them symmetric already), centred on the pivot.
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
import import_xayah as X  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shen")
MOD = os.path.join(ROOT, "league")
Z = 8
BLOCK = 16                  # Codex's export: one game pixel = 16 x 16
NAMES = ["a_hit", "a_emp", "q_blade", "q_hit", "q_slow", "q_1", "p_on", "w_zone", "w_safe", "e_dash", "e_hit",
         "r_cast", "r_ch", "r_shield", "r_land"]


def from_raw(folder):
    """Codex's exports -> native strips + shen_fx_anchors.json."""
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8") as f:
        man = {a["name"]: a for a in json.load(f)["assets"]}
    anchors = {}
    for name in NAMES:
        spec = man[name]
        a = np.asarray(Image.open(G.lp(os.path.join(folder, spec["file"]))).convert("RGBA"))
        h, w = a.shape[:2]
        if h % BLOCK or w % BLOCK:
            sys.exit(f"{spec['file']} {w}x{h} is not on a {BLOCK}-px grid")
        b = a.reshape(h // BLOCK, BLOCK, w // BLOCK, BLOCK, 4)
        if not (b == b[:, :1, :, :1]).all():
            sys.exit(f"{spec['file']} is not made of flat {BLOCK}x{BLOCK} blocks")
        g = b[:, 0, :, 0].copy()
        g[g[..., 3] < 128] = 0
        g[..., 3] = np.where(g[..., 3] > 0, 255, 0)
        n = spec["frame_count"]
        cw, ch = spec["cell_size"][0] // BLOCK, spec["cell_size"][1] // BLOCK
        if g.shape[1] != n * cw:
            sys.exit(f"{name}: {g.shape[1]} columns for {n} cells of {cw}")
        Image.fromarray(np.repeat(np.repeat(g, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"shen_fx_{name}.png")))
        anc = [spec["pivot"][0] / BLOCK, spec["pivot"][1] / BLOCK]
        anchors[name] = {"cell": [cw, ch], "anchor": anc, "frames": n}
        cols = len(np.unique(g[g[..., 3] > 0][:, :3], axis=0))
        print(f"shen_fx_{name}.png  {n} cells of {cw}x{ch}, anchor {anc[0]:g},{anc[1]:g}, {cols} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "shen_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"shen_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"shen_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down); his design is 46 rows: the hood 29 over the pivot, the soles 11 under
HIT = (0, -13)              # a hit on the upper body
FEET = (0, 10)              # a ring on the ground round a unit's feet (the ellipse's middle)
GROUND = (0, 11)            # what stands on the ground: the feet the pack drew round, on the soles
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "a_emp": [("a_emp", seq(range(5), [40, 50, 60, 70, 90]), [HIT])],
    # the blade flies back q_out + 20000 = 66000 at 4000 a tick (17 ticks = 275 ms) - looped, then held
    "q_blade": [("q_blade", flight(4, 50, 400, lead=0), [(0, 0)])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_slow": [("q_slow", seq(range(4), [110] * 4), [FEET])],
    "q_1": [("q_1", seq(range(4), [100] * 4), [GROUND])],
    "p_on": [("p_on", seq(range(4), [120] * 4), [GROUND])],
    "w_safe": [("w_safe", seq(range(4), [120] * 4), [GROUND])],
    # the dash's line rides with him: e_len 66000 at 3500 a tick (19 ticks = 314 ms)
    "e_dash": [("e_dash", flight(3, 60, 400, lead=0), [(0, 0)])],
    "e_hit": [("e_hit", seq(range(5), [40, 50, 60, 70, 90]), [HIT])],
}
BIG = {
    # once, w_t 105 ticks = 1750 ms: opens, holds (frames 3-6), fades
    "w_zone": [("w_zone", seq(range(7), [60, 80, 350, 350, 350, 350, 210]), [GROUND])],
    "r_cast": [("r_cast", seq(range(6), [50, 60, 70, 80, 90, 100]), [GROUND])],
    "r_ch": [("r_ch", seq(range(4), [100] * 4), [GROUND])],
    "r_shield": [("r_shield", seq(range(4), [120] * 4), [GROUND])],
    # Codex's frame 6 is a lone bar and dot floating over the ring: the landing ends on frame 5
    "r_land": [("r_land", seq(range(5), [40, 50, 60, 70, 120]), [GROUND])],
}
FLIP_TB = {"q_blade", "e_dash"}


def build(table):
    with open(G.lp(os.path.join(SRC, "shen_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_shen_fx", FX), ("league_shen_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

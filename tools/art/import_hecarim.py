#!/usr/bin/env python3
"""Import Hecarim's effects (assets/source/hecarim/PROMPTS_FX.md, 17 sheets) as the game sheets league_hecarim_fx and
league_hecarim_big.

    python tools/art/import_hecarim.py --raw assets/source/hecarim/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_hecarim.py                                      # native strips -> the effect sheets

The body comes from tools/art/fix_hecarim_strips.py + import_native.py. --raw turns each frame of Codex's drawings
(generator originals, one row of frames a sheet, no 1x export) into a cell of a native strip
(assets/source/hecarim/hecarim_fx_<name>.png, 8x, plus hecarim_fx_anchors.json) the way import_zed.py does: the frames
on the equal grid, or split at the emptiest column near each grid line where drawings cross it (the delivery's rects
are nominal),
each game pixel the majority colour of the source pixels it covers, opaque when a quarter of them are solid, every
colour snapped to the ramps the pack gave that effect (work/hc/fx_pack_hc.py: GHOST, SHADE, DUST), then the lights'
darkest ring comes off (import_jhin.unrim; the smoke's near-black stays: it is the smoke's inside). e_dust came on
opaque black: its black is keyed out first. One scale per strip: `size` game px over the drawings' widest (w), tallest
(h) or larger side (m) - or over frame `ref`'s alone, where the other frames' sparks run wider than the ring the size
is (the rings are the kit's radii: q_r 26000 -> 54 px across, w_r 30000 -> 60, r_r 26000 -> 52).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (tools/kit/build_hecarim.py, 60 ticks a second).
The red side: the client never mirrors a data picture. The riders are turned to their flight - drawn over their own
top-bottom flip; everything on a unit or on the ground is drawn as stored whichever way he faces - drawn over its own
left-right flip (league_xayah's over_flip). Every frame is centred on the pivot, so the flips are about it.
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

SRC = os.path.join(ROOT, "assets", "source", "hecarim")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps (work/hc/fx_pack_hc.py), darkest first
RAMPS = {
    "GHOST": ["005A5A", "148C82", "28C8B4", "50F0DC", "A4FAEE", "E0FFFA", "FFFFFF"],
    "SHADE": ["161B20", "262E36", "3C4650", "5A6672"],
    "DUST": ["6E644E", "9A8C70", "C2B496", "E6DCC8"],
}
# the lights' darkest shade on their edge goes (or takes the next); the smoke's near-black is its inside and stays
RIM = {"005A5A": "148C82", "6E644E": "9A8C70"}

# raw strip -> native: frames n, size (game px) over measure (of frame ref when given), anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=12, measure="m", ref=1, anchor=("fixed", "box", 1), ramps="GHOST"),
    "q_spin": dict(n=6, size=54, measure="w", ref=2, anchor=("fixed", "ellipse", 2), ramps="GHOST"),
    "q_hit": dict(n=4, size=14, measure="w", ref=1, anchor=("fixed", "box", 1), ramps="GHOST"),
    # the stack flames: the left half of each frame (Codex drew them too big for their spacing), placed on his left
    # flank; the left-right flip draws the right one
    "q1": dict(n=4, size=10, measure="h", half=True, anchor=("fixed", "box", 0), ramps="GHOST"),
    "q2": dict(n=4, size=16, measure="h", half=True, anchor=("fixed", "box", 0), ramps="GHOST"),
    "w_start": dict(n=6, size=60, measure="w", ref=2, anchor=("fixed", "ellipse", 2), ramps="GHOST SHADE"),
    "w_aura": dict(n=4, size=60, measure="w", anchor=("fixed", "ellipse", 0), ramps="GHOST SHADE"),
    "w_hit": dict(n=5, size=18, measure="h", anchor=("fixed", "low", 2), ramps="GHOST"),
    "e_dust": dict(n=5, size=32, measure="w", anchor=("fixed", "low", 2), ramps="GHOST DUST"),
    "e_ride": dict(n=4, size=42, measure="w", anchor=("fixed", "low", 0), ramps="GHOST DUST"),
    "e_hit": dict(n=5, size=22, measure="w", anchor=("fixed", "low", 2), ramps="GHOST DUST SHADE"),
    "e_haste": dict(n=4, size=40, measure="w", anchor=("fixed", "low", 0), ramps="GHOST"),
    "r_riders": dict(n=4, size=36, measure="w", anchor=("fixed", "box", 0), ramps="GHOST SHADE"),
    "r_cast": dict(n=5, size=56, measure="w", anchor=("fixed", "low", 1), ramps="GHOST SHADE"),
    "r_land": dict(n=6, size=52, measure="w", ref=2, anchor=("fixed", "ellipse", 2), ramps="GHOST DUST SHADE"),
    "r_hit": dict(n=4, size=14, measure="m", ref=1, anchor=("fixed", "box", 1), ramps="GHOST SHADE"),
    "r_fear": dict(n=6, size=12, measure="w", ref=3, anchor=("fixed", "low", 2), ramps="GHOST SHADE"),
}


def anchor(how, k, a, solid, rects, s=1.0):
    """import_twistedfate's anchors plus `low` (the middle of the drawing's lowest row, the box's middle across)."""
    if how == "low":
        x, y, w, h = rects[k]
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        return x + (xs.min() + xs.max() + 1) / 2, y + ys.max() + 1
    if isinstance(how, tuple) and how[0] == "fixed":
        x, y, _, _ = rects[k]
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects, s)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    return TF.anchor(how, k, a, solid, rects, s)


def split(solid, n):
    """n frames in one row: the equal grid when nothing lies on its lines (a frame's pieces may stand apart - the
    stack flames), else each cut at the emptiest column within a fifth of a cell of the grid's line."""
    H, W = solid.shape
    cols = solid.sum(0)
    cw = W / n
    if all(cols[max(round(i * cw) - 2, 0):round(i * cw) + 2].sum() == 0 for i in range(1, n)):
        return [[round(i * cw), 0, round((i + 1) * cw) - round(i * cw), H] for i in range(n)]
    cuts = [0]
    for i in range(1, n):
        c = round(i * cw)
        lo, hi = max(cuts[-1] + 1, round(c - cw / 5)), min(W - 1, round(c + cw / 5))
        win = cols[lo:hi]
        best = np.flatnonzero(win == win.min())
        cuts.append(lo + int(best[len(best) // 2]))
    cuts.append(W)
    return [[cuts[i], 0, cuts[i + 1] - cuts[i], H] for i in range(n)]


def box_w_h(solid, r):
    x, y, w, h = r
    ys, xs = np.nonzero(solid[y:y + h, x:x + w])
    return xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


def from_raw(folder):
    V.RAMPS = RAMPS
    V.RIM = RIM
    V.anchor = anchor
    apath = os.path.join(SRC, "hecarim_fx_anchors.json")
    anchors = {}
    if os.path.exists(G.lp(apath)):
        with open(G.lp(apath), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        fn = f"hecarim_fx_{name}.png"
        if not os.path.exists(G.lp(os.path.join(folder, fn))):
            continue
        hexes_, pal = V.palette(spec["ramps"])
        im = Image.open(G.lp(os.path.join(folder, fn)))
        a = np.asarray(im.convert("RGBA")).copy()
        if im.mode != "RGBA":           # drawn on opaque black: the black is the background
            a[..., 3] = np.where(a[..., :3].max(-1) > 40, 255, 0)
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = split(solid, spec["n"])
        if spec.get("half"):
            rects = [[x, y, w // 2, h] for x, y, w, h in rects]
        sp = dict(spec)
        if "ref" in spec:               # the size is frame ref's: the scale of the strip from it
            boxes = [box_w_h(solid, r) for r in rects]
            ext = {"w": max(b[0] for b in boxes), "h": max(b[1] for b in boxes)}
            ext["m"] = max(ext["w"], ext["h"])
            bw, bh = boxes[spec["ref"]]
            ref = {"w": bw, "h": bh, "m": max(bw, bh)}[spec["measure"]]
            sp["size"] = spec["size"] * ext[spec["measure"]] / ref
        out, cell, anc, s, ext = V.convert(name, sp, a, solid, idx, pal, rects)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale {s:.4f} "
              f"({spec['size']} px over {spec['measure']}{' of frame %d' % spec['ref'] if 'ref' in spec else ''}), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(apath), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"hecarim_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"hecarim_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down)
HIT = (0, -12)              # a hit on the upper body of a 36-44 px unit
SOUL = (0, -6)              # the soul drain's glow on the chest; its wisps rise over the head
FEET = (0, 10)              # a ring on the ground round a unit's feet
GROUND = (0, 11)            # what stands on the ground: its lowest row on the soles
Q1 = (-22, -3)              # the stack flame on his left flank, 14 px over his soles (the flip: the right one)
Q2 = (-19, -6)              # the full stack's pair there (22 and 15 px out, 14 and 20 over the soles)
FEAR = (0, -18)             # the fear ghost's lowest wisp: its skull over the head (~30-36 over the soles)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q1": [("q1", seq(range(4), [120] * 4), [Q1])],
    "q2": [("q2", seq(range(4), [110] * 4), [Q2])],
    "w_hit": [("w_hit", seq(range(5), [50, 60, 70, 80, 90]), [SOUL])],
    "e_dust": [("e_dust", seq(range(5), [50, 60, 70, 80, 90]), [GROUND])],
    "e_ride": [("e_ride", seq(range(4), [80] * 4), [GROUND])],
    "e_hit": [("e_hit", seq(range(5), [40, 60, 70, 80, 90]), [GROUND])],
    "e_haste": [("e_haste", seq(range(4), [110] * 4), [GROUND])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_fear": [("r_fear", seq(range(6), [70, 90, 110, 130, 130, 110]), [FEAR])],
}
BIG = {
    # Q's spin lasts q_dur 24 ticks (400 ms): the sweep's peak on the hit (q_at 9 = 150 ms)
    "q_spin": [("q_spin", seq(range(6), [40, 50, 60, 70, 80, 90]), [FEET])],
    "w_start": [("w_start", seq(range(6), [50, 60, 70, 80, 90, 100]), [FEET])],
    "w_aura": [("w_aura", seq(range(4), [120] * 4), [FEET])],
    # the riders ride r_range 70000 at 3000 a tick (~23 ticks): looped, held
    "r_riders": [("r_riders", flight(4, 60, 500, lead=0), [(0, 0)])],
    "r_cast": [("r_cast", seq(range(5), [50, 60, 70, 80, 90]), [GROUND])],
    "r_land": [("r_land", seq(range(6), [40, 60, 70, 80, 90, 110]), [FEET])],
}
FLIP_TB = {"r_riders"}


def build(table):
    with open(G.lp(os.path.join(SRC, "hecarim_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_hecarim_fx", FX), ("league_hecarim_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

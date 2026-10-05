#!/usr/bin/env python3
"""Import Lissandra's effects (assets/source/lissandra/PROMPTS_FX.md, 21 sheets) as the game sheets league_lissandra_fx
and league_lissandra_big.

    python tools/art/import_lissandra.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_lissandra.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_lissandra.py built the strips). --raw turns each frame of Codex's
drawings into a cell of a native strip (assets/source/lissandra/lissandra_fx_<name>.png, 8x, plus
lissandra_fx_anchors.json) the way import_twistedfate.py does: the frames are the drawing's n equal columns (Codex drew
every sheet as one row; a manifest.json's `assets[].frames[].rect` wins when there is one), each game pixel the majority
colour of the source pixels it covers, opaque when a quarter of them are solid, every colour snapped to the ramps the
pack gave that effect (ICE, FROST, GLOW, BLACK and the ice's INK outline), then the darkest-shade ring comes off the
light (import_jhin.unrim) - the INK outline of solid ice stays. One scale per strip: `size` game px over the drawings'
widest (w), tallest (h) or larger side (m).
Anchors (source pixels): the flying things on their front (3 px in from the tip), the hits on their white flash, the
hand flashes on their left end, the rings and fields on the ground on the ring's widest row, the things standing on
the ground (the root, the tomb, the ice block, the thrall) on the middle of their lowest row, the pictures round her on
the figure's feet the pack placed 8 squares over each cell's bottom.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the hem 11 under the
pivot) measured on the rigged strips (fx_pack_lz.hand_at): the near hand in Q 4 (17.5, -16) and in E 2 (17.5, -12) -
and times it by the kit (work/lz/build_lissandra.py, 60 ticks a second).
Writes league/effects/league_lissandra_fx and league_lissandra_big.
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

SRC = os.path.join(ROOT, "assets", "source", "lissandra")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (work/lz/fx_pack_lz.py)
RAMPS = {
    "ICE": ["1A4AA0", "2A84E0", "5CC0F8", "A8E4FF", "E2F6FF", "FFFFFF"],
    "FROST": ["78C8F0", "B4E6FA", "E6F8FF", "FFFFFF"],
    "GLOW": ["1E78D0", "40B4FF", "7AD8FF", "C8F4FF", "FFFFFF"],
    "BLACK": ["0F1028", "1B1F42", "2C3C70", "4A64A8", "7F9CDA", "C8D4FF"],
    "INK": ["0B0A14"],                         # solid ice's outline
}
# the light's darkest shade on its edge goes (or takes the next): never the black ice's own darks, which are its body
RIM = {"1A4AA0": "2A84E0", "78C8F0": "B4E6FA", "1E78D0": "40B4FF"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
FEET8 = ("feet8",)          # the figure's feet the pack placed 8 squares over the cell's bottom
RAW = {
    "a_bolt": dict(n=4, size=14, measure="w", anchor="front", ramps="INK ICE FROST", sq=(64, 32)),
    "a_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="INK ICE FROST", sq=(32, 32)),
    "q_cast": dict(n=4, size=16, measure="w", anchor="left", ramps="GLOW FROST", sq=(32, 24)),
    "q_shard": dict(n=4, size=26, measure="w", anchor="front", ramps="INK ICE FROST", sq=(64, 32)),
    "q_hit": dict(n=5, size=16, measure="m", anchor="core", ramps="INK ICE FROST", sq=(32, 32)),
    "slow": dict(n=4, size=18, measure="w", anchor="ellipse", ramps="INK ICE FROST", sq=(80, 32)),
    "w_ring": dict(n=6, size=60, measure="w", anchor=("fixed", "ellipse", 2), ramps="INK ICE FROST", sq=(60, 34)),
    "w_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="INK ICE FROST", sq=(32, 32)),
    "w_root": dict(n=4, size=20, measure="w", anchor="low", ramps="INK ICE FROST", sq=(80, 48)),
    "e_cast": dict(n=4, size=16, measure="w", anchor="left", ramps="GLOW FROST", sq=(32, 24)),
    "e_claw": dict(n=4, size=22, measure="w", anchor="front", ramps="INK ICE GLOW FROST", sq=(64, 32)),
    "e_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="INK ICE FROST", sq=(32, 32)),
    "e_port": dict(n=5, size=34, measure="w", anchor=FEET8, ramps="INK ICE FROST", sq=(34, 30)),
    "r_cast": dict(n=5, size=50, measure="h", anchor=FEET8, ramps="GLOW FROST", sq=(40, 50)),
    "r_tomb": dict(n=4, size=46, measure="h", anchor="low", ramps="INK ICE FROST", sq=(30, 44)),
    "r_burst": dict(n=6, size=56, measure="w", anchor=("fixed", "ellipse", 2), ramps="INK BLACK ICE FROST", sq=(56, 36)),
    "r_field": dict(n=4, size=60, measure="w", anchor="box", ramps="INK BLACK GLOW", sq=(64, 32)),
    "r_self_cast": dict(n=4, size=50, measure="h", anchor=FEET8, ramps="INK ICE FROST", sq=(34, 50)),
    "r_stasis": dict(n=4, size=50, measure="h", anchor="low", ramps="INK ICE FROST", sq=(34, 50)),
    "p_thrall": dict(n=8, size=32, measure="h", anchor="low", ramps="INK BLACK GLOW", sq=(26, 40)),
    "p_burst": dict(n=6, size=50, measure="w", anchor=("fixed", "ellipse", 2), ramps="INK BLACK GLOW FROST", sq=(50, 34)),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def unrim(a):
    J.RIM = RIM
    return J.unrim(a)


def rects_of(folder, fn, a, n):
    """The frames: a manifest's rects when there is one, else the drawing's n equal columns (full height)."""
    man = os.path.join(folder, "manifest.json")
    if os.path.exists(G.lp(man)):
        with open(G.lp(man), encoding="utf-8-sig") as f:
            assets = {os.path.basename(x["file"]): x for x in json.load(f).get("assets", [])}
        if fn in assets:
            return [[int(v) for v in f["rect"]] for f in assets[fn]["frames"]]
    H, W = a.shape[:2]
    return [[round(k * W / n), 0, round((k + 1) * W / n) - round(k * W / n), H] for k in range(n)]


def anchor(how, k, a, solid, rects, s, spec):
    if how == FEET8:
        x, y, w, h = rects[k]
        cw, ch = spec["sq"]
        return x + w / 2, y + h - h * 8 / ch
    return TF.anchor(how, k, a, solid, rects, s)


def from_raw(folder):
    anchors = {}
    for name, spec in RAW.items():
        fn = f"lissandra_fx_{name}.png"
        path = os.path.join(folder, fn)
        if not os.path.exists(G.lp(path)):
            path = os.path.join(folder, "raw", fn)
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(path)).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = rects_of(folder, fn, a, spec["n"])
        idx = J.snap(a, solid, pal)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
        anc = [anchor(spec["anchor"], k, a, solid, rects, s, spec) for k in range(len(rects))]
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rects), 4), np.uint8)
        for i, (x, y, w, h) in enumerate(rects):
            ax, ay = anc[i]
            cell = np.zeros((th, tw, 4), np.uint8)
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / s))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / s)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 4:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    cell[r, c, :3] = pal[col]
                    cell[r, c, 3] = 255
            out[:, i * tw:(i + 1) * tw] = unrim(cell)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "lissandra_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"lissandra_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"lissandra_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (fx_pack_lz.hand_at)
Q_HAND = (17, -16)          # the near hand that throws Q in skill 4
E_HAND = (17, -12)          # the near hand that throws the claw in skill2_e 2
HIT = (0, -10)              # a hit on the upper body of a 36-44 px unit
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # what stands on the ground: its lowest row on the soles
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
looped = TF.looped

P_MS = 90 * 1000 // 60          # p_delay: the thrall stands 90 ticks
FIELD_MS = 180 * 1000 // 60     # r_field_t: the field lasts 180 ticks
FX = {
    # the bolt: 55 px at 5 px a tick, homing (twice that), out of her hand 17 px away: 3 empty ticks
    "a_bolt": [("a_bolt", flight(4, 60, 450, lead=3), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # Q: 88 px at 5 px a tick (18 ticks)
    "q_shard": [("q_shard", flight(4, 60, 360, lead=2), [(0, 0)])],
    "q_cast": [("q_cast", seq(range(4), [30, 40, 50, 60]), [Q_HAND])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    # one frost mark for Q's, R's field's and the thrall's slows
    "q_slow": [("slow", seq(range(4), [110] * 4), [FEET])],
    "r_slow": [("slow", seq(range(4), [110] * 4), [FEET])],
    "p_slow": [("slow", seq(range(4), [110] * 4), [FEET])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_root": [("w_root", seq(range(4), [120] * 4), [SOLES])],
    # E: the claw 90 px at 3.5 px a tick (26 ticks)
    "e_claw": [("e_claw", flight(4, 70, 520, lead=2), [(0, 0)])],
    "e_cast": [("e_cast", seq(range(4), [30, 40, 50, 60]), [E_HAND])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
}
BIG = {
    "w_ring": [("w_ring", seq(range(6), [40, 50, 60, 80, 80, 90]), [FEET])],
    "w_ring_late": [("w_ring", seq(range(6), [40, 50, 60, 80, 80, 90]), [FEET])],
    "e_port": [("e_port", seq(range(5), [40, 50, 60, 70, 80]), [SOLES])],
    "r_cast": [("r_cast", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
    "r_tomb": [("r_tomb", seq(range(4), [130] * 4), [SOLES])],
    "r_burst": [("r_burst", seq(range(6), [40, 50, 60, 70, 80, 90]), [FEET])],
    "r_field": [("r_field", looped([0], [1, 2, 3, 0], [150], 150, FIELD_MS), [FEET])],
    "r_self_cast": [("r_self_cast", seq(range(4), [60, 70, 80, 90]), [SOLES])],
    "r_stasis": [("r_stasis", seq(range(4), [150] * 4), [SOLES])],
    # the thrall: rises (3), stands swaying (4), cracks (1) over the 90 ticks before it shatters
    "p_thrall": [("p_thrall", seq(range(8), [100, 100, 120, 250, 250, 250, 250, P_MS - 1320]), [SOLES])],
    "p_burst": [("p_burst", seq(range(6), [40, 50, 60, 70, 80, 90]), [FEET])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "lissandra_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_lissandra_fx", FX), ("league_lissandra_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

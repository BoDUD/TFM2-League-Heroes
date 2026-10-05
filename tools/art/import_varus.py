#!/usr/bin/env python3
"""Import Varus's effects (assets/source/varus/PROMPTS_FX.md, 24 sheets) as the game sheets league_varus_fx and
league_varus_big.

    python tools/art/import_varus.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_varus.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_varus.py built the strips). --raw turns each frame of Codex's
drawings into a cell of a native strip (assets/source/varus/varus_fx_<name>.png, 8x, plus varus_fx_anchors.json) the
way import_lissandra.py does: the frames are the drawing's equal grid (its manifest's `rows` x `columns`; Codex's own
rectangles are estimates of the same grid), each game pixel the majority colour of the source pixels it covers,
opaque when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect (VIOLET, MAGENTA,
CRIMSON, DARK and the objects' INK outline), then the light's darkest ring comes off (import_jhin.unrim) - the INK
outline of arrows and tendrils stays. One scale per strip: `size` game px over the drawings' widest (w), tallest (h)
or larger side (m). b_mark's three rows become the strips b_v1, b_v2 and b_v3.
Anchors (source pixels): the flying things on their front (3 px in from the tip), the hits on their white flash, the
bow flashes on their left end (e_cast on the lower left corner of its first frame), the glows on their box, the rings
and fields on the ground on the ring's widest row, what stands on the ground (the binding tendrils, the passive's
burst) on the middle of its lowest row.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) measured on the rigged strips (work/vr/fx_pack_vr.grip_at): the bow grip in attack 3 (13, -9), Q 3 / 6
(12, -8) / (13, -8), E 3 (13, -18), R 3 (14, -8) - and times it by the kit (tools/kit/build_varus.py, 60 ticks a
second). Writes league/effects/league_varus_fx and league_varus_big.
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

SRC = os.path.join(ROOT, "assets", "source", "varus")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (work/vr/fx_pack_vr.py)
RAMPS = {
    "VIOLET": ["6A1AB8", "A112F7", "CA2BFB", "E8A0FF", "F6D8FF", "FFFFFF"],
    "MAGENTA": ["C0208F", "E838F3", "FF70D8", "FFC8F0", "FFFFFF"],
    "CRIMSON": ["4A0428", "890851", "D32087", "F01A1A", "FF6A6A", "FFD0D0"],
    "DARK": ["140A1E", "261432", "3B185F", "5E3A88", "8A5CC0"],
    "INK": ["0B0410"],                       # arrows', thorns' and tendrils' outline
}
# the light's darkest shade on its edge goes (or takes the next): never the tendrils' own darks, which are their body
RIM = {"6A1AB8": "A112F7", "C0208F": "E838F3", "4A0428": "890851"}

# raw strip -> native: frames n (rows x cols), size (game px) over measure, anchor, ramps
RAW = {
    "a_arrow": dict(n=4, size=14, measure="w", anchor="front", ramps="INK VIOLET MAGENTA"),
    "a_flash": dict(n=3, size=12, measure="w", anchor="left", ramps="VIOLET MAGENTA"),
    "a_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="VIOLET MAGENTA"),
    "b_mark": dict(n=12, rows=3, size=16, measure="w", anchor="box", ramps="INK VIOLET MAGENTA CRIMSON"),
    "b_pop": dict(n=5, size=22, measure="m", anchor="core", ramps="INK VIOLET CRIMSON MAGENTA"),
    "w_pop": dict(n=5, size=28, measure="m", anchor="core", ramps="VIOLET CRIMSON MAGENTA"),
    "w_glow": dict(n=4, size=22, measure="h", anchor="box", ramps="CRIMSON VIOLET"),
    "q_charge": dict(n=6, size=24, measure="m", anchor=("fixed", "box", 2), ramps="VIOLET MAGENTA"),
    "q_fire": dict(n=4, size=24, measure="w", anchor="left", ramps="VIOLET MAGENTA"),
    "q_arrow": dict(n=4, size=30, measure="w", anchor="front", ramps="INK VIOLET MAGENTA"),
    "q_hit": dict(n=5, size=18, measure="m", anchor="core", ramps="VIOLET MAGENTA"),
    "e_cast": dict(n=4, size=16, measure="m", anchor="ll", ramps="VIOLET MAGENTA"),
    "e_rain": dict(n=7, size=56, measure="w", anchor=("fixed", "ellipse", 4), ramps="INK VIOLET CRIMSON DARK"),
    "e_field": dict(n=4, size=58, measure="w", anchor="box", ramps="INK DARK CRIMSON VIOLET"),
    "e_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="INK VIOLET CRIMSON"),
    "e_slow": dict(n=4, size=18, measure="w", anchor="ellipse", ramps="INK CRIMSON DARK VIOLET"),
    "r_cast": dict(n=4, size=20, measure="w", anchor="left", ramps="INK CRIMSON DARK VIOLET"),
    "r_chain": dict(n=4, size=28, measure="w", anchor="front", ramps="INK DARK CRIMSON VIOLET"),
    "r_hit": dict(n=5, size=22, measure="m", anchor="core", ramps="INK CRIMSON DARK VIOLET"),
    "r_bind": dict(n=4, size=36, measure="h", anchor="low", ramps="INK DARK CRIMSON VIOLET"),
    "r_spread": dict(n=6, size=60, measure="w", anchor=("fixed", "ellipse", 1), ramps="INK DARK CRIMSON VIOLET"),
    "r_spread_hit": dict(n=4, size=16, measure="m", anchor="core", ramps="INK CRIMSON DARK VIOLET"),
    "p_rage_on": dict(n=5, size=46, measure="h", anchor=("fixed", "low", 1), ramps="VIOLET MAGENTA CRIMSON"),
    "p_rage": dict(n=4, size=22, measure="w", anchor="ellipse", ramps="VIOLET MAGENTA"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def unrim(a):
    J.RIM = RIM
    return J.unrim(a)


def grid(a, n, rows=1):
    """The drawing's n frames as an equal grid of `rows` rows, read left to right, top to bottom."""
    H, W = a.shape[:2]
    cols = n // rows
    out = []
    for r in range(rows):
        y0, y1 = round(r * H / rows), round((r + 1) * H / rows)
        for c in range(cols):
            x0, x1 = round(c * W / cols), round((c + 1) * W / cols)
            out.append([x0, y0, x1 - x0, y1 - y0])
    return out


def anchor(how, k, a, solid, rects, s):
    if how == "ll":                     # e_cast: the lower left corner of frame 0's drawing, the same spot in every cell
        x, y, w, h = rects[0]
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        ax, ay = xs.min() + 2 / s, ys.max() + 1 - 2 / s
        return rects[k][0] + ax, rects[k][1] + ay
    return TF.anchor(how, k, a, solid, rects, s)


def convert(name, spec, a, solid, idx, pal, rects):
    """One native strip (cells of one size, a shared anchor) from the frames `rects`."""
    boxes = []
    for x, y, w, h in rects:
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        if not len(xs):
            boxes.append(None)
            continue
        boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
    real = [b for b in boxes if b]
    ext = {"w": max(b[1] - b[0] for b in real), "h": max(b[3] - b[2] for b in real)}
    ext["m"] = max(ext["w"], ext["h"])
    s = spec["size"] / ext[spec["measure"]]
    anc = [anchor(spec["anchor"], k, a, solid, rects, s) if boxes[k] else (rects[k][0] + rects[k][2] / 2,
                                                                          rects[k][1] + rects[k][3] / 2)
           for k in range(len(rects))]
    L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes) if b) * s - 0.5), 0) + 1
    U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes) if b) * s - 0.5), 0) + 1
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
    return out, (tw, th), (L, U), s, ext[spec["measure"]]


def from_raw(folder):
    anchors = {}
    for name, spec in RAW.items():
        fn = f"varus_fx_{name}.png"
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rows = spec.get("rows", 1)
        rects = grid(a, spec["n"], rows)
        groups = [(name, rects)] if rows == 1 else [(f"b_v{r + 1}", rects[r * (spec['n'] // rows):(r + 1) * (spec['n'] // rows)])
                                                     for r in range(rows)]
        if rows > 1:
            # one scale for the three rows (the widest row sets it), then each row its own strip
            spec1 = dict(spec)
            boxes = []
            for x, y, w, h in rects:
                ys, xs = np.nonzero(solid[y:y + h, x:x + w])
                boxes.append(xs.max() - xs.min() + 1 if len(xs) else 0)
            widest = max(boxes)
        for gname, grects in groups:
            sp = spec
            if rows > 1:
                # the scale of the widest row for every row: size px over that row's width
                rw = max(boxes[rects.index(r)] for r in grects)
                sp = dict(spec, size=spec["size"] * rw / widest)
            out, cell, anc, s, ext = convert(gname, sp, a, solid, idx, pal, grects)
            Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
                G.lp(os.path.join(SRC, f"varus_fx_{gname}.png")))
            anchors[gname] = {"cell": list(cell), "anchor": list(anc), "frames": len(grects)}
            print(f"varus_fx_{gname}.png  {len(grects)} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
                  f"{s:.4f} ({sp['size']:.0f} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "varus_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"varus_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"varus_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (fx_pack_vr.grip_at)
A_GRIP = (13, -9)           # the bow in attack 3 (the release)
Q_GRIP = (12, -8)           # the bow while Q charges (frames 2-5, the lunge)
Q_FIRE = (13, -8)           # the bow in Q 6 (the release)
E_GRIP = (13, -18)          # the bow, turned up, in E 3 (the release)
R_GRIP = (14, -8)           # the bow in R 3 (the throw)
HIT = (0, -10)              # a hit on the upper body of a 36-44 px unit
OVER = (0, -32)             # over the head (the idle tops 28 over the pivot)
FEET = (0, 9)               # a ring on the ground round a unit's feet
SOLES = (0, 11)             # what stands on the ground: its lowest row on the soles
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
looped = TF.looped

FIELD_MS = 240 * 1000 // 60     # e_field_t: the corrupted ground lasts 240 ticks
CHARGE_MS = 66 * 1000 // 60     # q_full_t: the full draw
FX = {
    # the arrow: 57.5 px at 7 px a tick, homing (twice that); out of the bow 13 px away: 2 empty ticks
    "a_arrow": [("a_arrow", flight(4, 60, 300, lead=2), [(0, 0)])],
    "a_flash": [("a_flash", seq(range(3), [30, 40, 50]), [A_GRIP])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # Blight: the stack pips over the head (one per hit), the detonation on the target
    "b_v1": [("b_v1", seq(range(4), [60, 90, 90, 120]), [OVER])],
    "b_v2": [("b_v2", seq(range(4), [60, 90, 90, 120]), [OVER])],
    "b_v3": [("b_v3", seq(range(4), [60, 90, 90, 120]), [OVER])],
    "b_pop1": [("b_pop", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "b_pop2": [("b_pop", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "b_pop3": [("b_pop", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "w_pop": [("w_pop", seq(range(5), [40, 60, 70, 80, 90]), [HIT])],
    # the crimson glow round the bow through the full draw (Blighted Arrow ready)
    "w_glow": [("w_glow", looped([0], [1, 2, 3, 0], [100], 100, CHARGE_MS), [Q_GRIP])],
    # Q: the charge gathers (frames 0-1) then loops (2-5) through the 66-tick draw; the quick draw its first 3 frames
    "q_charge": [("q_charge", looped([0, 1], [2, 3, 4, 5], [100, 150], 100, CHARGE_MS), [Q_GRIP])],
    "q_charge_s": [("q_charge", seq(range(3), [120, 140, 140]), [Q_GRIP])],
    "q_fire": [("q_fire", seq(range(4), [30, 40, 50, 60]), [Q_FIRE])],
    # the arrow: 140 px at 6.5 px a tick (22 ticks); the quick one 100 px
    "q_arrow": [("q_arrow", flight(4, 60, 400, lead=2), [(0, 0)])],
    "q_arrow_s": [("q_arrow", flight(4, 60, 300, lead=2), [(0, 0)])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    # E
    "e_cast": [("e_cast", seq(range(4), [30, 40, 50, 60]), [E_GRIP])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_slow": [("e_slow", seq(range(4), [110] * 4), [FEET])],
    # R
    "r_cast": [("r_cast", seq(range(4), [40, 50, 60, 70]), [R_GRIP])],
    "r_chain": [("r_chain", flight(4, 60, 400, lead=2), [(0, 0)])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "r_spread_hit": [("r_spread_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_bind": [("r_bind", seq(range(4), [120] * 4), [SOLES])],
    # the passive's aura under him while the attack speed lasts
    "p_rage": [("p_rage", seq(range(4), [110] * 4), [FEET])],
}
BIG = {
    # the rain lands e_land (20 ticks = 333 ms) after the release: the strike frame (3) starts there
    "e_rain": [("e_rain", seq(range(7), [100, 110, 120, 90, 100, 110, 120]), [FEET])],
    "e_field": [("e_field", looped([0], [1, 2, 3, 0], [150], 150, FIELD_MS), [FEET])],
    "r_spread": [("r_spread", seq(range(6), [50, 60, 70, 80, 90, 100]), [FEET])],
    "p_rage_on": [("p_rage_on", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "varus_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_varus_fx", FX), ("league_varus_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

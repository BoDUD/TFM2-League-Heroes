#!/usr/bin/env python3
"""Import Kennen's effects (assets/source/kennen/PROMPTS_FX.md, 1-19) as the game sheets league_kennen_fx and _big.

    python tools/art/import_kennen.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_kennen.py                                   # native strips -> the effect sheets

The body comes from tools/art/rig_kennen.py and import_native.py. Codex delivered image-model drafts
(outputs/kennen-fx, 2026-10-02 20:58: 1619-2172 x 724-971 px, soft alpha, free colours; HANDOFF, manifest and prompts
in assets/source/kennen/codex_fx), every frame's rectangle in manifest.json (`assets[].frames[].rect` = [x, y, w, h]).
--raw turns each frame into a cell of a native strip (assets/source/kennen/kennen_fx_<name>.png, 8x, plus
kennen_fx_anchors.json), as tools/art/import_kaisa.py does: each game pixel the majority colour of the solid source
pixels it covers (alpha 100 and up), opaque when FILL of them are solid; every colour snapped to the pack's ramps -
his lightning (white core to violet), the cyan edges, the shuriken's gold (and a dark gold for the thrown star's edge),
the storm's dark clouds - each effect only to the ramps its prompt named (PAL); then a glow's darkest violet at its
edge goes when two lighter neighbours hold the shape, else it takes the next shade. One scale per strip: `size` game px
over the drawings' widest (w), tallest (h) or larger side (m) - the pack's sizes - or a width and height of their own
(the stun's two columns are spread round a unit's body: Codex drew them a third as wide as tall, the pack asked 4:5).
Q's star is made exactly symmetric about its core's row (the game turns it with its flight).
Anchors (source pixels, the same spot in every cell): the thrown stars on their middle (the attack's) or their gold
star (Q's, the lightning trailing behind it); the flashes and hits on frame 1's (2's) white core; the mark counters
and E's ball on their drawing's middle; W's surge on its white ring's middle (frame 4: its spokes are uneven), R's
storm on its clouds' middle; the stun's columns and R's bolt on their drawings' foot.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; measured on
league/champions/league_kennen: the shuriken leaving his hand in the throw's release (30, -5), attack's and Q's frame
4, the soles 11 under the pivot, his body's middle -6 (-5 crouched in E's dash)) and times it by the kit: the
thrown stars start empty while they cross him (5 ticks, Q's 3: from his pivot to his hand), then spin; the mark
counters 0.8 s over the target's head, the stun its 1.25 s, E's ball the 0.28 s of the rush (until e_out), R's storm
2.9 s (forming, the loop of frames 3-10 four times, the fade; the strikes end at 2.5 s, the armour at 3 s).
Writes league/effects/league_kennen_fx and league_kennen_big (W's surge, R's storm and bolt).
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
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kennen")
MOD = os.path.join(ROOT, "league")
Z = 8

VOLT = ["FFFFFF", "EDE4FF", "C3A6FF", "9466F2", "6232C4"]
CYAN = ["F2FFFF", "A8F0FF", "4CC8F5"]
GOLD = ["FFF4C8", "FEDC80", "F8A23B", "CB7420"]
DARK_GOLD = ["8A4614"]
STORM = ["2A1446", "3E2066", "5B3590"]
PAL = {"star": GOLD + DARK_GOLD + ["FFFFFF"],
       "gold": GOLD + ["FFFFFF"],
       "volt": VOLT + CYAN,
       "mark": VOLT + CYAN + STORM[1:],
       "volt_gold": VOLT + CYAN + GOLD,
       "storm": VOLT + CYAN + GOLD + DARK_GOLD + STORM}
RIM = {"6232C4": "9466F2"}      # a glow's darkest violet at its edge -> the next shade
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]
FILL = 0.25                     # share of a game pixel's source pixels that must be solid

# raw strip -> native: frames n, size (game px) over measure or (w, h), anchor, palette, mirror (Q's star)
RAW = {
    "a_star": dict(n=4, size=9, measure="m", anchor=("fixed", "box", 0), pal="star"),
    "a_cast": dict(n=3, size=10, measure="m", anchor=("fixed", "core", 0), pal="gold"),
    "a_hit": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0), pal="gold"),
    "a_cast2": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), pal="volt"),
    "a_hit2": dict(n=5, size=18, measure="m", anchor=("fixed", "core", 0), pal="volt"),
    "k_mark1": dict(n=4, size=14, measure="w", anchor=("fixed", "box", 0), pal="mark"),
    "k_mark2": dict(n=4, size=14, measure="w", anchor=("fixed", "box", 0), pal="mark"),
    "k_stun": dict(n=10, size=(24, 38), anchor=("fixed", "foot", None), pal="volt"),
    "q_star": dict(n=4, size=20, measure="w", anchor=("fixed", "gold", 0), pal="volt_gold", mirror=True),
    "q_cast": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), pal="volt_gold"),
    "q_hit": dict(n=5, size=20, measure="m", anchor=("fixed", "core", 0), pal="volt_gold"),
    "w_burst": dict(n=7, size=100, measure="w", anchor=("fixed", "core", 3), pal="volt"),
    "w_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), pal="volt"),
    "e_in": dict(n=4, size=24, measure="m", anchor=("fixed", "core", 0), pal="volt"),
    "e_ball": dict(n=4, size=30, measure="w", anchor=("fixed", "box", 0), pal="volt"),
    "e_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), pal="volt"),
    "e_out": dict(n=5, size=28, measure="m", anchor=("fixed", "core", 1), pal="volt"),
    "r_storm": dict(n=12, size=110, measure="w", anchor=("fixed", "clouds", 5), pal="storm"),
    "r_hit": dict(n=5, size=48, measure="h", anchor=("fixed", "foot", None), pal="volt"),
}


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def hexes(a):
    return np.array([["%02X%02X%02X" % tuple(int(v) for v in p[:3]) for p in row] for row in a])


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = m[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
    return out


def unrim(a):
    a = a.copy()
    op = a[..., 3] > 0
    hx = hexes(a)
    rim = op & np.isin(hx, list(RIM))
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    lit = sum(shifted(op & ~rim, dy, dx).astype(int) for dy, dx in N8)
    target = rim & edge
    gone = target & (lit >= 2)
    a[gone] = 0
    for dark, nxt in RIM.items():
        a[target & ~gone & (hx == dark), :3] = rgb(nxt)
    return a


def snap(a, solid, pal):
    """Palette index of every solid pixel (-1 elsewhere)."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - pal[None]) ** 2).sum(2).argmin(1)
    return idx


def mirror(cell, U):
    out = cell.copy()
    for r in range(U):
        if 2 * U - r < cell.shape[0]:
            out[2 * U - r] = cell[r]
    return out


def bright(a):
    return (a[..., 3] >= 100) & (a[..., :3].min(-1) >= 215)


def anchor(how, k, a, solid, rects):
    """(x, y) of frame k's anchor in the source."""
    x, y, w, h = rects[k]
    if how[0] == "fixed":                  # frame j's anchor, the same spot in every cell
        if how[1] == "foot":
            ax, ay = foot(solid, rects)
            return x + ax - rects[0][0], y + ay - rects[0][1]
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    s = solid[y:y + h, x:x + w]
    ys, xs = np.nonzero(s)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    if how == "box":                       # the drawing's middle
        return x + (x0 + x1) / 2, y + (y0 + y1) / 2
    sub = a[y:y + h, x:x + w]
    if how == "core":                      # the white flash's middle
        by, bx = np.nonzero(bright(sub))
        if len(bx) < 20:
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + bx.mean() + 0.5, y + by.mean() + 0.5
    if how == "gold":                      # the gold star's middle
        c = sub[..., :3].astype(int)
        g = s & (c[..., 0] > 180) & (c[..., 1] > 90) & (c[..., 2] < 140) & (c[..., 0] - c[..., 2] > 90)
        by, bx = np.nonzero(g)
        return x + (bx.min() + bx.max() + 1) / 2, y + (by.min() + by.max() + 1) / 2
    if how == "clouds":                    # the storm's ring of dark clouds: its middle
        c = sub[..., :3].astype(int)
        d = s & (c.max(-1) < 130)
        by, bx = np.nonzero(d)
        return x + (bx.min() + bx.max() + 1) / 2, y + (by.min() + by.max() + 1) / 2
    raise ValueError(how)


def foot(solid, rects):
    """The middle of the lowest drawn row over all frames, in frame 0's coordinates."""
    lows, mids = [], []
    for x, y, w, h in rects:
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        lows.append(ys.max() + 1)
        mids.append((xs.min() + xs.max() + 1) / 2)
    return rects[0][0] + float(np.median(mids)), rects[0][1] + max(lows)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"kennen_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        pal = np.array([rgb(h) for h in PAL[spec["pal"]]], float)
        idx = snap(a, solid, pal)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        if isinstance(spec["size"], tuple):
            sx, sy = spec["size"][0] / ext["w"], spec["size"][1] / ext["h"]
        else:
            sx = sy = spec["size"] / ext[spec["measure"]]
        anc = [anchor(spec["anchor"], k, a, solid, rects) for k in range(len(rects))]
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes)) * sx - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * sy - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rects), 4), np.uint8)
        for i, (x, y, w, h) in enumerate(rects):
            ax, ay = anc[i]
            cell = np.zeros((th, tw, 4), np.uint8)
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / sy))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / sy)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / sx))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / sx)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < spec.get("fill", FILL):
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    cell[r, c, :3] = pal[col]
                    cell[r, c, 3] = 255
            cell = unrim(cell)
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, i * tw:(i + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {sx:.4f} x {sy:.4f} "
              f"({spec['size']} px over {ext['w']} x {ext['h']}), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "kennen_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"kennen_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"kennen_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


HAND_A = (30, -5)               # the shuriken leaving his hand in the throw's release (attack frame 4)
HAND_Q = (30, -5)               # the same release in Q (frame 4)
HIT = (0, -8)                   # a hit on the upper body of a 31-44 px unit
OVERHEAD = (0, -35)             # over a 31-44 px unit's head: the mark counter
SOLES = (0, 11)                 # the ground under a unit (its soles' row)
BODY = (0, -6)                  # his body's middle
CROUCH = (0, -5)                # his body's middle in E's crouched dash


TICK = 1000 / 60


def seq(frames, ms):
    return list(zip(frames, ms))


def flight(lead_ticks, loops=4, ms=50):
    """A projectile: empty while it is inside him (the engine also turns its first tick's picture straight up), the
    4-frame spin, then frame 1 held (repeat: false)."""
    return [(None, round(lead_ticks * TICK))] + [(k, ms) for k in [0, 1, 2, 3] * loops] + [(0, 3000)]


FX = {
    # the attack's star leaves the pivot 3.5 px up and reaches his hand (27 px) in 5 ticks at 5 px a tick; Q's (30 px)
    # in 3 at 8
    "a_star": [("a_star", flight(5), [(0, 0)])],
    "q_star": [("q_star", flight(3), [(0, 0)])],
    "a_cast": [("a_cast", seq(range(3), [40, 50, 60]), [HAND_A])],
    "a_cast2": [("a_cast2", seq(range(4), [40, 50, 60, 70]), [HAND_A])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "a_hit2": [("a_hit2", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "k_mark1": [("k_mark1", seq(range(4), [100, 250, 250, 200]), [OVERHEAD])],
    "k_mark2": [("k_mark2", seq(range(4), [100, 250, 250, 200]), [OVERHEAD])],
    "k_stun": [("k_stun", seq(range(10), [125] * 10), [SOLES])],
    "q_cast": [("q_cast", seq(range(4), [40, 50, 60, 70]), [HAND_Q])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_in": [("e_in", seq(range(4), [40, 50, 60, 70]), [BODY])],
    "e_ball": [("e_ball", seq(range(4), [70] * 4), [CROUCH])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_out": [("e_out", seq(range(5), [40, 50, 60, 70, 80]), [BODY])],
}
BIG = {
    "w_burst": [("w_burst", seq(range(7), [40, 50, 60, 70, 80, 90, 100]), [SOLES])],
    "r_storm": [("r_storm", seq([0, 1] + list(range(2, 10)) * 4 + [10, 11], [80, 80] + [80] * 32 + [100, 100]),
                 [SOLES])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 70, 80]), [SOLES])],
}


def place(cell, anchor_px, spots):
    """The cell with its anchor on every spot (from the pivot), as one frame centred on the pivot."""
    ax, ay = anchor_px
    h, w = cell.shape[:2]
    xs = [int(round(sx - ax)) for sx, _ in spots]
    ys = [int(round(sy - ay)) for _, sy in spots]
    u0, r0 = min(xs), min(ys)
    canvas = np.zeros((max(ys) - r0 + h, max(xs) - u0 + w, 4), np.uint8)
    for x, y in zip(xs, ys):
        sub = canvas[y - r0:y - r0 + h, x - u0:x - u0 + w]
        m = cell[..., 3] > 0
        sub[m] = cell[m]
    return G.centre_frame(canvas, u0, r0)


def build(table):
    with open(G.lp(os.path.join(SRC, "kennen_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                if k is None:
                    out[tag].append((np.zeros((1, 1, 4), np.uint8), ms))
                else:
                    out[tag].append((place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for stem, table in (("league_kennen_fx", FX), ("league_kennen_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", stem), tags)
        print(f"league/effects/{stem}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

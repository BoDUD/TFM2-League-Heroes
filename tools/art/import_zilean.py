#!/usr/bin/env python3
"""Import Zilean's effects (assets/source/zilean/PROMPTS_FX.md, 19 sheets) as the game sheets league_zilean_fx and
league_zilean_big.

    python tools/art/import_zilean.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_zilean.py                                   # native strips -> the effect sheets

The body comes from tools/art/fix_zilean_strips.py and import_native.py. Codex delivered (outputs/zilean_fx_done.zip,
2026-10-03 13:11; HANDOFF, manifest and prompts in assets/source/zilean/codex_fx) its image-model drafts (raw/: 1774-2172
x 724-887 px, soft alpha, free colours; the blasts, the rune and the rewind drawn 4 x 2) and strips it read from them on
an 8-px grid, with fewer squares than the game sizes asked for the large ones (the double blast 38 squares wide for 64).
--raw reads the drafts, every frame's cell in manifest.json (`assets[].raw_frames[].rect` = [x, y, w, h]), and turns
each frame into a cell of a native strip (assets/source/zilean/zilean_fx_<name>.png, 8x, plus zilean_fx_anchors.json) the way
import_ryze.py does: each game pixel the majority colour of the source pixels it covers, opaque when a quarter of them
are solid (alpha 100 and up: the one-pixel sparks survive), every colour snapped to the pack's three ramps (CYAN for
time: the orb, the blasts, the arcs, the clock rings; GOLD for the bomb, the clock, the rune and the bottle; VIOLET for
Time Warp's slow), then the ring comes off the glows (an edge pixel in a ramp's darkest shade goes when two lighter
neighbours hold the shape, else it takes the next shade; the bomb and the bottle, objects with their own dark band,
keep theirs). One scale per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m), the
pack's sizes. The orb is made exactly symmetric about its core's row (the game turns it with its flight).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot; measured on league/champions/league_zilean: the attack's hand (17, -6) in its frame 5, Q's raised hand
(15, -21) in its frame 4, E's hand (14, -5) in its frame 4) and times it by the kit (60 ticks a second). Writes
league/effects/league_zilean_fx and league_zilean_big (the blasts, the rewind clock, the rune and the cast: large
frames kept apart from the small ones).
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

SRC = os.path.join(ROOT, "assets", "source", "zilean")
MOD = os.path.join(ROOT, "league")
Z = 8

CYAN = ["1A7FB0", "2FC8E8", "7FF4FF", "D8FFFF", "FFFFFF"]
GOLD = ["9C5A10", "E39A1E", "FFD24A", "FFF2B0"]
VIOLET = ["4724A8", "7B4BF0", "B98CFF", "EAD8FF"]
PAL_HEX = CYAN + GOLD + VIOLET
PAL = np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in PAL_HEX], float)
# a ramp's darkest shade at a glow's edge -> the next shade
RIM = {"1A7FB0": "2FC8E8", "9C5A10": "E39A1E", "4724A8": "7B4BF0"}
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames n, size (game px) over measure, anchor, mirror (projectiles), rim (False: keep the
# darkest shade at the edge - an object, not a glow)
RAW = {
    "a_orb": dict(n=4, size=10, measure="w", anchor="head", mirror=True),
    "a_cast": dict(n=4, size=10, measure="m", anchor=("fixed", "core", 0)),
    "a_hit": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0)),
    "q_cast": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0)),
    "q_bomb": dict(n=4, size=9, measure="m", anchor=("fixed", "box", 0), rim=False),
    "q_bomb_on": dict(n=4, size=14, measure="m", anchor=("fixed", "box", 0), rim=False),
    "q_bomb_ground": dict(n=12, size=28, measure="w", anchor=("fixed", "ring", 0), rim=False),
    "q_boom": dict(n=7, size=56, measure="w", anchor=("fixed", "core", 0), trim=True),
    "q_boom2": dict(n=8, size=64, measure="w", anchor=("fixed", "core", 0), trim=True),
    "q_hit": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0)),
    "q_stun": dict(n=6, size=18, measure="w", anchor=("fixed", "box", 0)),
    "w_rewind": dict(n=6, size=40, measure="m", anchor=("fixed", "box", 0)),
    "e_cast": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0)),
    "e_slow": dict(n=6, size=22, measure="w", anchor=("fixed", "box", 0)),
    "e_haste": dict(n=6, size=24, measure="w", anchor=("fixed", "ring", 0)),
    "p_bottle": dict(n=6, size=18, measure="h", anchor=("fixed", "foot", None), rim=False),
    "r_cast": dict(n=5, size=36, measure="w", anchor=("fixed", "ring", 1)),
    "r_rune": dict(n=8, size=26, measure="m", anchor="top", rim=False, trim=True),
    "r_rewind": dict(n=8, size=40, measure="h", anchor=("fixed", "foot", None), trim=True),
}


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
        m = target & ~gone & (hx == dark)
        a[m, :3] = [int(nxt[i:i + 2], 16) for i in (0, 2, 4)]
    return a


def snap(a, solid):
    """Palette index of every solid pixel (-1 elsewhere)."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - PAL[None]) ** 2).sum(2).argmin(1)
    return idx


def mirror(cell, U):
    out = cell.copy()
    for r in range(U):
        if 2 * U - r < cell.shape[0]:
            out[2 * U - r] = cell[r]
    return out


def bright(a):
    return (a[..., 3] >= 100) & (a[..., :3].min(-1) >= 215)


def foot(solid, rects):
    """The middle of the lowest drawn row over all frames (the feet the drawings were made round), in frame 0's
    coordinates."""
    lows, mids = [], []
    for x, y, w, h in rects:
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        lows.append(ys.max() + 1)
        mids.append((xs.min() + xs.max() + 1) / 2)
    return float(np.median(mids)), max(lows)


def anchor(how, k, a, solid, rects):
    """(x, y) of frame k's anchor in the source."""
    x, y, w, h = rects[k]
    if how == "cell":
        return x + w / 2, y + h / 2
    if how[0] == "fixed":                  # frame j's anchor, the same spot in every cell
        if how[1] == "foot":
            ax, ay = foot(solid, rects)
            return x + ax, y + ay
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    s = solid[y:y + h, x:x + w]
    ys, xs = np.nonzero(s)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    b = bright(a[y:y + h, x:x + w])
    if how == "box":                       # the middle of the drawing
        return x + (x0 + x1) / 2, y + (y0 + y1) / 2
    if how == "top":                       # the middle of the drawing's top 40% (the rune's clock: the drafts drift
        top = s.copy()                     # sideways from cell to cell)
        top[int(y0 + 0.4 * (y1 - y0)):] = False
        ty, tx = np.nonzero(top)
        return x + (tx.min() + tx.max() + 1) / 2, y + (y0 + y1) / 2
    if how == "head":                      # the white core in the drawing's front half
        b[:, :int(x0 + 0.5 * (x1 - x0))] = False
        by, bx = np.nonzero(b)
        if not len(bx):
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + (bx.min() + bx.max() + 1) / 2, y + (by.min() + by.max() + 1) / 2
    if how == "core":                      # the white flash's middle
        by, bx = np.nonzero(b)
        if len(bx) < 20:
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + bx.mean() + 0.5, y + by.mean() + 0.5
    if how == "ring":                      # the ring's middle: the lower 40% of the drawing
        low = s.copy()
        low[:int(y1 - 0.4 * (y1 - y0))] = False
        ly, lx = np.nonzero(low)
        return x + (lx.min() + lx.max() + 1) / 2, y + (ly.min() + ly.max() + 1) / 2
    raise ValueError(how)


def trim(solid, rects, edge=0.15, gap=3):
    """Slivers of the neighbouring drawing inside a cell (the 4 x 2 drafts: the cells are as tall and wide as their
    drawings): content in the outer `edge` of a cell cut off from the rest by `gap` empty columns or rows goes."""
    for x, y, w, h in rects:
        for axis, size in ((0, w), (1, h)):
            lines = solid[y:y + h, x:x + w].any(axis)
            n = max(1, int(edge * size))
            for side in (range(n), range(size - 1, size - 1 - n, -1)):
                run, cut = 0, None
                for c in reversed(list(side)):          # from the inside out
                    run = run + 1 if not lines[c] else 0
                    if run >= gap:
                        cut = c
                        break
                if cut is None:
                    continue
                lo, hi = (0, cut) if side.start == 0 else (cut, size)
                if axis == 0:
                    solid[y:y + h, x + lo:x + hi] = False
                else:
                    solid[y + lo:y + hi, x:x + w] = False


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"zilean_fx_{name}.png"
        entry = manifest[fn]
        a = np.asarray(Image.open(G.lp(os.path.join(folder, entry["raw_file"]))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in entry["raw_frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        if spec.get("trim"):
            trim(solid, rects)
        idx = snap(a, solid)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
        anc = [anchor(spec["anchor"], k, a, solid, rects) for k in range(len(rects))]
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
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(PAL)).argmax()
                    cell[r, c, :3] = PAL[col]
                    cell[r, c, 3] = 255
            if spec.get("rim", True):
                cell = unrim(cell)
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, i * tw:(i + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "zilean_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"zilean_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"zilean_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


A_HAND = (18, -6)          # just past the hand in the attack's frame 5
Q_HAND = (16, -21)         # just past the raised hand in Q's frame 4
E_HAND = (15, -5)          # just past the hand in E's frame 4
HIT = (0, -8)              # a hit on the upper body of a 32-44 px unit
CHEST = (0, -8)            # the bomb stuck on a unit's chest
OVERHEAD = (0, -33)        # the stun's clocks over a 32-44 px unit's head
WAIST = (0, 0)             # the slow's clock ring round the waist
BACK = (-1, -9)            # the rewind's clock behind him, round his body and his own clock
FEET = (0, 9)              # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)            # the ground under a unit (its soles' row)
HEAD_TOP = (0, -27)        # the bottle's stream ends on a unit's head
RUNE = (0, -23)            # the rune's clock over a unit's head, its ring round the shoulders
# the blasts' flash (their anchor) over the ground ring's middle: the single blast's ring 8 under it, the double's 12
BOOM = (0, 1)
BOOM2 = (0, -3)
# rings anchored on the lower part of their drawing, lifted onto the feet: the cast's ring middle 4 over its anchor,
# the haste's 2
R_FEET = (0, 13)
HASTE_FEET = (0, 11)


def seq(frames, ms):
    return list(zip(frames, ms))


FX = {
    "a_orb": [("a_orb", seq(range(4), [70] * 4), [(0, 0)])],
    "a_cast": [("a_cast", seq(range(4), [40, 50, 60, 70]), [A_HAND])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_cast": [("q_cast", seq(range(4), [40, 50, 60, 70]), [Q_HAND])],
    "q_bomb": [("q_bomb", seq(range(4), [80] * 4), [(0, 0)])],
    "q_bomb_on": [("q_bomb_on", seq(range(4), [125] * 4), [CHEST])],
    # 3 s on the ground: frames 1-10 twice, then 11-12 just before it blows
    "q_bomb_ground": [("q_bomb_ground", seq(list(range(10)) * 2 + [10, 11], [125] * 20 + [250, 250]), [FEET])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_stun": [("q_stun", seq(list(range(6)) * 2, [104, 104, 104, 104, 104, 105] * 2), [OVERHEAD])],
    "e_cast": [("e_cast", seq(range(4), [40, 50, 60, 70]), [E_HAND])],
    "e_slow": [("e_slow", seq(range(6), [100] * 6), [WAIST])],
    "e_haste": [("e_haste", seq(range(6), [80] * 6), [HASTE_FEET])],
    "p_bottle": [("p_bottle", seq(range(6), [80, 90, 100, 110, 120, 130]), [HEAD_TOP])],
}
BIG = {
    "q_boom": [("q_boom", seq(range(7), [40, 50, 60, 70, 80, 90, 100]), [BOOM])],
    "q_boom2": [("q_boom2", seq(range(8), [40, 50, 60, 70, 80, 90, 100, 110]), [BOOM2])],
    "w_rewind": [("w_rewind", seq(range(6), [60, 70, 80, 90, 100, 100]), [BACK])],
    "r_cast": [("r_cast", seq(range(5), [60, 80, 100, 120, 140]), [R_FEET])],
    "r_rune": [("r_rune", seq(range(8), [100] * 8), [RUNE])],
    "r_rewind": [("r_rewind", seq(range(8), [50, 60, 70, 80, 90, 100, 110, 140]), [SOLES])],
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
    with open(G.lp(os.path.join(SRC, "zilean_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                out[tag].append((place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_zilean_fx", FX), ("league_zilean_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

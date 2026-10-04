#!/usr/bin/env python3
"""Import Ryze's effects (assets/source/ryze/PROMPTS_FX.md, 19 sheets) as the game sheets league_ryze_fx and
league_ryze_big.

    python tools/art/import_ryze.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_ryze.py                                   # native strips -> the effect sheets

The body comes from tools/art/fix_ryze_strips.py and import_native.py. Codex delivered image-model drafts
(outputs/ryze_fx_done.zip, 2026-10-03 00:42: 1448-2172 x 724-1086 px, soft alpha, free colours; HANDOFF and manifest
in assets/source/ryze/codex_fx), every frame's cell in manifest.json (`assets[].frames[].rect` = [x, y, w, h], the
runes' 6 x 2 read row by row: one rune, then two). --raw turns each frame into a cell of a native strip
(assets/source/ryze/ryze_fx_<name>.png, 8x, plus ryze_fx_anchors.json) the way import_kaisa.py does: each game pixel
the majority colour of the source pixels it covers, opaque when a quarter of them are solid (alpha 100 and up: the
one-pixel sparks survive), every colour snapped to the pack's two ramps (BLUE for Overload, the runes, Rune Prison and
Realm Warp; VIOLET for Spell Flux and its mark), then the ring comes off the glows (an edge pixel in a ramp's darkest
shade goes when two lighter neighbours hold the shape, else it takes the next shade). One scale per strip: `size`
game px over the drawings' widest (w), tallest (h) or larger side (m), the pack's sizes. The three projectiles are made
exactly symmetric about their core's row (the game turns them with their flight).
Anchors (source pixels, the same spot in every cell unless the drawing moves): the projectiles on their white core
(its front half); the flashes and blasts on a frame's flash (q_pop on its burst, frame 2: frame 1 is the bolt coming
down); the rings and orbits (Flux, the runes, the slow, the two runes bursting, the portal) on their cell's middle,
where Codex centred them (the portal's cells are as wide as its drawings: a sliver of the next one cut off by empty
columns at a cell's edge goes); the cage, the column and the arrival on their ground ring (frame 1); the haste and the
ally's flash on their drawings' foot.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot; measured on league/champions/league_ryze: Q's palm (23, -8) in Q's frame 3 and the combo's frame 9, E's
palm (23, -15) in the combo's frame 2) and times it by the kit (60 ticks a second): the projectiles loop (70 ms a
frame); Flux 4 x 50 ms (the kit replays it every 12 ticks); the cage of a root holds its standing bars to the root's
end (75 ticks) and fades, the slow's cage only flashes (its chain ring stays on the feet as the slow buff); the portal
opens, turns through R's channel (60 ticks) and closes as he leaves. Writes league/effects/league_ryze_fx and
league_ryze_big (R's portal, its column and the arrival: large frames kept apart from the small ones).
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

SRC = os.path.join(ROOT, "assets", "source", "ryze")
MOD = os.path.join(ROOT, "league")
Z = 8

BLUE = ["1A4FB8", "2E9BF0", "7FDBFF", "D6F4FF", "FFFFFF"]
VIOLET = ["4724A8", "7B4BF0", "B98CFF", "EAD8FF"]
PAL_HEX = BLUE + VIOLET
PAL = np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in PAL_HEX], float)
# a ramp's darkest shade at a glow's edge -> the next shade
RIM = {"1A4FB8": "2E9BF0", "4724A8": "7B4BF0"}
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames n, size (game px) over measure, anchor, mirror (projectiles)
RAW = {
    "orb": dict(n=4, size=10, measure="w", anchor="head", mirror=True),
    "hit": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0)),
    "q_bolt": dict(n=4, size=20, measure="w", anchor="head", mirror=True),
    "q_cast": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0)),
    "q_hit": dict(n=5, size=18, measure="m", anchor=("fixed", "core", 0)),
    "q_pop": dict(n=5, size=20, measure="w", anchor=("fixed", "core", 1)),
    "e_orb": dict(n=4, size=12, measure="w", anchor="head", mirror=True),
    "e_cast": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0)),
    "e_hit": dict(n=5, size=22, measure="m", anchor=("fixed", "core", 0)),
    "flux": dict(n=4, size=20, measure="w", anchor="cell"),
    "w_cage": dict(n=8, size=30, measure="h", anchor=("fixed", "ring", 0)),
    "rune_out": dict(n=5, size=26, measure="w", anchor="cell"),
    "runes": dict(n=12, size=28, measure="w", anchor="cell"),
    "w_slow": dict(n=4, size=22, measure="w", anchor="cell"),
    "q_haste": dict(n=4, size=24, measure="w", anchor=("fixed", "foot", None)),
    "r_portal": dict(n=10, size=60, measure="w", anchor="cell", trim=True),
    "r_out": dict(n=6, size=44, measure="h", anchor=("fixed", "ring", 0)),
    "r_in": dict(n=6, size=34, measure="m", anchor=("fixed", "ring", 0)),
    "r_ally": dict(n=4, size=24, measure="h", anchor=("fixed", "foot", None)),
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


def trim(solid, rects, edge=0.12, gap=3):
    """Slivers of the neighbouring drawing inside a cell (the portal's cells are as wide as its drawings): content in
    the outer `edge` of a cell cut off from the rest by `gap` empty columns goes."""
    for x, y, w, h in rects:
        cols = solid[y:y + h, x:x + w].any(0)
        n = max(1, int(edge * w))
        for side in (range(n), range(w - 1, w - 1 - n, -1)):
            run, cut = 0, None
            for c in reversed(list(side)):          # from the inside out
                run = run + 1 if not cols[c] else 0
                if run >= gap:
                    cut = c
                    break
            if cut is not None:
                lo, hi = (0, cut) if side.start == 0 else (cut, w)
                solid[y:y + h, x + lo:x + hi] = False


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"ryze_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
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
            cell = unrim(cell)
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, i * tw:(i + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "ryze_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"ryze_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"ryze_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


Q_PALM = (21, -20)         # just past the open palm in Q's frame 3, the pointing hand's tip in the combo's frame 9
E_PALM = (21, -26)         # the tip of the hand pointing up in the combo's frame 2 (Codex's second strips, the arms
                           # thinned on the idle's body: tools/art/fix_ryze_strips_v2.py); both moved with the near
                           # hand when the arms became 2 rows shorter (2026-10-04, design_ryze_v2.py step 6: Q 3 and the
                           # combo's 9 a square in, the combo's 2 two in and two up)
HIT = (0, -8)              # a hit on the upper body of a 32-44 px unit
CHEST = (0, -7)            # Flux circles a unit's chest
WAIST = (0, -2)            # his belt: the runes he charges and lets out
FEET = (0, 9)              # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)            # the ground under a unit (its soles' row)
PORTAL = (0, 10)           # R's portal: the unit stands in its middle


def seq(frames, ms):
    return list(zip(frames, ms))


HOLD = 1140                 # the root's 75 ticks after the cage's 110 ms of rising
FX = {
    "orb": [("orb", seq(range(4), [70] * 4), [(0, 0)])],
    "q_bolt": [("q_bolt", seq(range(4), [70] * 4), [(0, 0)])],
    "e_orb": [("e_orb", seq(range(4), [70] * 4), [(0, 0)])],
    "hit": [("hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_cast": [("q_cast", seq(range(4), [40, 50, 60, 70]), [Q_PALM])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_pop": [("q_pop", seq(range(5), [50, 50, 60, 70, 80]), [HIT])],
    "e_cast": [("e_cast", seq(range(4), [40, 50, 60, 70]), [E_PALM])],
    "e_hit": [("e_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "flux": [("flux", seq(range(4), [50] * 4), [CHEST])],
    "w_root": [("w_cage", seq([0, 1] + [2, 3, 4, 5] * 3 + [2, 3], [50, 60] + [HOLD // 14] * 14)
                + seq([6, 7], [80, 100]), [FEET])],
    "w_cage": [("w_cage", seq([0, 1, 2, 3, 6, 7], [50, 60, 70, 80, 80, 100]), [FEET])],
    "rune_out": [("rune_out", seq(range(5), [50, 60, 70, 80, 90]), [WAIST])],
    "rune1": [("runes", seq(range(6), [100] * 6), [WAIST])],
    "rune2": [("runes", seq(range(6, 12), [100] * 6), [WAIST])],
    "w_slow": [("w_slow", seq(range(4), [100] * 4), [FEET])],
    "q_haste": [("q_haste", seq(range(4), [80] * 4), [SOLES])],
    "r_ally": [("r_ally", seq(range(4), [50, 60, 70, 90]), [SOLES])],
}
PORTAL_MS = seq([0, 1] + list(range(2, 8)) * 2 + [8, 9], [60, 60] + [73] * 12 + [60, 60])
BIG = {
    "r_portal": [("r_portal", PORTAL_MS, [PORTAL])],
    "r_dest": [("r_portal", PORTAL_MS, [PORTAL])],
    "r_out": [("r_out", seq(range(6), [50, 60, 70, 80, 90, 100]), [PORTAL])],
    "r_in": [("r_in", seq(range(6), [50, 60, 70, 80, 90, 100]), [PORTAL])],
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
    with open(G.lp(os.path.join(SRC, "ryze_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in (("league_ryze_fx", FX), ("league_ryze_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

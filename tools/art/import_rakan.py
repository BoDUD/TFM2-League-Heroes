#!/usr/bin/env python3
"""Import Rakan's effects (assets/source/rakan/PROMPTS_FX.md: 15 sheets) as the game sheets league_rakan_fx and
league_rakan_big.

    python tools/art/import_rakan.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_rakan.py                                   # native strips -> the effect sheets

The body comes from tools/art/import_native.py (after tools/art/fix_rakan_strips.py). --raw turns each frame of
Codex's image-model drafts (every frame's cell in manifest.json, `assets[].frames[].rect` = [x, y, w, h]; three
sheets have uneven cells) into a cell of a native strip (assets/source/rakan/rakan_fx_<name>.png, 8x, plus
rakan_fx_anchors.json) the way tools/art/import_kayn.py does: each game pixel the majority colour of the source
pixels it covers, opaque when a quarter of them are solid (alpha 100 and up), every colour snapped to the ramps the
pack gave that effect (GOLD: his feathers, white to dark red; IRIS: the cloak tips' cyan, blue and violet; HEAL: the
Q heal's yellow-green; HEART: the charm's golden hearts), then the ring comes off the glows (an edge pixel in a
ramp's darkest shade goes when two lighter neighbours hold the shape, else it takes the next shade). One scale per
strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m), the pack's sizes; Q's heal wave
is the heal's radius (40000: an 80-px ellipse). W's launch gets a width and a height of its own: Codex drew it a
narrow pillar (223 x 843), which at 44 px high would be 12 px wide and hide behind him (it is drawn under him), so its
ground ring takes the knock-up's 26 px and the column 44 (the feathers 2.6 times wider than drawn). The charm's hearts,
6 px wide, would rise 36 px over the head as drawn: they rise 45% of that (`mix`). The passive's shield, drawn a narrow
oval (326 x 622), crossed his face at 46 px high (24 wide): it is 34 wide, round his cloak, and lies behind him. Codex filled some glows with opaque
dark brown (E's shield oval read as a dark red disc over the ally): in the gold-only sheets source pixels darker than
the ramp's last shade (luminance under `dark`) are left out.
Anchors (source pixels), x and y apart: a frame's own (`box` the drawing's middle, `core` the white flash's middle,
`ring` the middle of the drawing's lowest 40%, `low` the middle of its lowest row, `right` a trail's front, `round`
the middle of a round burst whose left side streams off: its right edge less half its height) or frame j's, the same
spot in every cell (`fixed`). Codex's cells are equal for twelve sheets, so their anchors are fixed; Q's hit, the heal
wave and R's start have cells of their own widths (the drawings grow and shrink), so x is each frame's own and y the
fixed one (one ground line, one flash height).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (60 ticks a second). Writes league/effects/league_rakan_fx (the small pictures) and
league_rakan_big (the heal wave and the launch, drawn on the ground at his feet).
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

SRC = os.path.join(ROOT, "assets", "source", "rakan")
MOD = os.path.join(ROOT, "league")
Z = 8

RAMPS = {   # light to dark, as the pack gave them (work/rk/fx_pack_rk.py)
    "GOLD": ["FFFFFF", "FFF8D6", "FFE47A", "FFC63A", "FF9E21", "F07018", "D04A1A", "9A2A1C"],
    "IRIS": ["FFFFFF", "DBF7FF", "94F7EF", "4FE0C8", "5AA0F0", "7A6CE8", "A64CD0", "6A2A9A"],
    "HEAL": ["FFFFFF", "F6FFD6", "E2FF7A", "C6F04E", "9AD83A", "6AAE2C", "3E7A22"],
    "HEART": ["FFFFFF", "FFF3C6", "FFD554", "FFAC12", "F06A2A", "E0405A", "A82048"],
}
# a ramp's darkest shade at a glow's edge -> the next shade
RIM = {"9A2A1C": "D04A1A", "6A2A9A": "A64CD0", "3E7A22": "6AAE2C", "A82048": "E0405A"}
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def fx(n, size, measure, ax, ay, ramps, dark=0):
    return dict(n=n, size=size, measure=measure, anchor=(ax, ay), ramps=ramps, dark=dark)


F0, F2, F3 = ("fixed", "box", 0), ("fixed", "box", 2), ("fixed", "box", 3)
# raw strip -> native: frames n, size (game px) over measure, anchor x and y, ramps
RAW = {
    "a_feather": fx(3, 12, "w", F0, F0, "GOLD IRIS"),
    "a_hit": fx(4, 12, "m", ("fixed", "core", 0), ("fixed", "core", 0), "GOLD IRIS"),
    "q_feather": fx(4, 22, "w", F0, F0, "GOLD IRIS"),
    "q_hit": fx(5, 18, "m", "box", F2, "GOLD IRIS"),
    "q_heal": fx(4, 32, "w", ("fixed", "ring", 2), ("fixed", "ring", 2), "HEAL GOLD"),
    "q_burst": fx(6, 84, "w", "box", ("fixed", "ring", 2), "HEAL GOLD"),
    "q_healed": fx(5, 24, "h", ("fixed", "low", 2), ("fixed", "low", 2), "HEAL GOLD"),
    "w_burst": fx(7, (26, 44), "wh", ("fixed", "ring", 3), ("fixed", "ring", 3), "GOLD", dark=80),
    "w_hit": fx(5, 26, "h", ("fixed", "low", 2), ("fixed", "low", 2), "GOLD", dark=80),
    "e_shield": fx(6, 30, "h", F3, F3, "GOLD", dark=80),
    "e_on": fx(6, 40, "h", ("fixed", "ring", 0), ("fixed", "ring", 0), "GOLD", dark=80),
    "p_on": fx(6, (34, 46), "wh", F0, F0, "GOLD IRIS"),
    "r_start": fx(6, 44, "m", "round", ("fixed", "core", 0), "GOLD IRIS"),
    "r_on": fx(4, 48, "w", ("fixed", "right", 0), ("fixed", "right", 0), "GOLD IRIS"),
    "r_charmed": fx(8, 14, "w", ("fixed", "core", 0), ("mix", "box", ("fixed", "core", 0), 0.45), "HEART"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


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


def snap(a, solid, pal):
    """Palette index of every solid pixel (-1 elsewhere)."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - pal[None]) ** 2).sum(2).argmin(1)
    return idx


def bright(a):
    return (a[..., 3] >= 100) & (a[..., :3].min(-1) >= 215)


def spot(how, k, a, solid, rects):
    """(x, y) of frame k's anchor in the source."""
    x, y, w, h = rects[k]
    if isinstance(how, tuple) and how[0] == "mix":     # ("mix", a, b, f): a moved the share f of the way to b
        _, ha, hb, f = how
        (xa, ya), (xb, yb) = spot(ha, k, a, solid, rects), spot(hb, k, a, solid, rects)
        return xa + (xb - xa) * f, ya + (yb - ya) * f
    if isinstance(how, tuple):             # ("fixed", how, j): frame j's anchor, the same spot in every cell
        _, inner, j = how
        ax, ay = spot(inner, j, a, solid, rects)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    s = solid[y:y + h, x:x + w]
    ys, xs = np.nonzero(s)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    if how == "box":                       # the drawing's middle
        return x + (x0 + x1) / 2, y + (y0 + y1) / 2
    if how == "core":                      # the white flash's middle
        by, bx = np.nonzero(bright(a[y:y + h, x:x + w]))
        if len(bx) < 20:
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + bx.mean() + 0.5, y + by.mean() + 0.5
    if how == "ring":                      # a ring on the ground: the middle of the drawing's lowest 40%
        low = s.copy()
        low[:int(y1 - 0.4 * (y1 - y0))] = False
        ly, lx = np.nonzero(low)
        return x + (lx.min() + lx.max() + 1) / 2, y + (ly.min() + ly.max() + 1) / 2
    if how == "right":                     # a trail's front: its right end, halfway down the rightmost tenth
        band = s[:, max(x0, int(x1 - 0.1 * (x1 - x0))):x1]
        by = np.nonzero(band.any(1))[0]
        return x + x1, y + (by.min() + by.max() + 1) / 2
    if how == "low":                       # rising from the ground: the middle of its lowest row
        lx = np.nonzero(s[y1 - 1])[0]
        return x + (lx.min() + lx.max() + 1) / 2, y + y1
    if how == "round":                     # a round burst streaming off to the left: right edge less half its height
        return x + x1 - (y1 - y0) / 2, y + (y0 + y1) / 2
    raise ValueError(how)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"rakan_fx_{name}.png"
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        if spec["dark"]:                   # Codex's opaque dark-brown glow bodies: darker than the ramp's last shade
            solid &= (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]) >= spec["dark"]
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        idx = snap(a, solid, pal)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        if spec["measure"] == "wh":            # a width and a height of their own (W's launch: the ring, the column)
            sx, sy = spec["size"][0] / ext["w"], spec["size"][1] / ext["h"]
        else:
            sx = sy = spec["size"] / ext[spec["measure"]]
        hx_, hy_ = spec["anchor"]
        anc = [(spot(hx_, k, a, solid, rects)[0], spot(hy_, k, a, solid, rects)[1]) for k in range(len(rects))]
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
                    if m.mean() < 1 / 4:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    cell[r, c, :3] = pal[col]
                    cell[r, c, 3] = 255
            out[:, i * tw:(i + 1) * tw] = unrim(cell)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {sx:.4f} x {sy:.4f} (size {spec['size']} over "
              f"{ext['w']} x {ext['h']}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "rakan_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"rakan_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"rakan_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down)
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
CHEST = (0, -9)             # the middle of a 40-px unit: the shields round him
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # the ground under a unit (its soles' row)
FLY = (0, 0)                # a projectile's picture: centred on the projectile
TRAIL = (2, -6)             # R's trail: its front at his back, hip to chest high
OVER = (0, -30)             # just over a unit's head: the charm's hearts rise from there


def seq(frames, ms):
    return list(zip(frames, ms))


SHEETS = {
    "league_rakan_fx": {
        "a_feather": [("a_feather", seq(range(3), [50] * 3), [FLY])],               # a 7-tick flight
        "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
        "q_feather": [("q_feather", seq(range(4), [50] * 4), [FLY])],               # an 11-tick flight
        "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
        "q_heal": [("q_heal", seq(range(4), [100] * 4), [FEET])],                   # the buff loops up to 3 s
        "q_healed": [("q_healed", seq(range(5), [60, 70, 80, 90, 100]), [SOLES])],
        "w_hit": [("w_hit", seq(range(5), [50, 60, 80, 100, 120]), [SOLES])],       # the 48-tick knock-up
        "e_shield": [("e_shield", seq(range(6), [50, 60, 70, 90, 100, 110]), [CHEST])],
        "e_on": [("e_on", seq(range(6), [100] * 6), [FEET])],                       # the 3-s shield
        "p_on": [("p_on", seq(range(6), [110] * 6), [CHEST])],                      # until it breaks
        "r_start": [("r_start", seq(range(6), [40, 50, 60, 80, 100, 120]), [CHEST])],
        "r_on": [("r_on", seq(range(4), [90] * 4), [TRAIL])],                       # the 4-s speed
        "r_charmed": [("r_charmed", seq(range(8), [100, 120, 140, 160, 180, 180, 180, 190]), [OVER])],  # 75 ticks
    },
    "league_rakan_big": {
        "q_burst": [("q_burst", seq(range(6), [50, 60, 70, 90, 110, 120]), [FEET])],
        "w_burst": [("w_burst", seq(range(7), [50, 60, 80, 100, 110, 120, 120]), [FEET])],
    },
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
    with open(G.lp(os.path.join(SRC, "rakan_fx_anchors.json")), encoding="utf-8") as f:
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
    for sheet, table in SHEETS.items():
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

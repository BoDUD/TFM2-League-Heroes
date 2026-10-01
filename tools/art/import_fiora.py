#!/usr/bin/env python3
"""Import Fiora's effects (assets/source/fiora/PROMPTS_FX.md, 1-18) as game sheets.

    python tools/art/import_fiora.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_fiora.py                                   # native strips -> effect sheets

The body comes from tools/art/import_native.py. Codex delivered image-model drafts (soft alpha, free colours, the
glows ringed in their darkest blue and gold; manifest.json's `assets[].frames[].rect` gives the frames), so --raw
turns every frame into a cell of a native strip the way tools/art/import_veigar.py does: each game pixel the
majority colour of the source pixels it covers, opaque when a third of them are solid, every colour snapped to the
pack's ramps that strip asked for (the steel of the thrusts, the vital blue, gold, the healing mint, dust: no mint
speck in a blue flash). Then the ring comes off (the user on Riven's: "记得清理描边"; import_riven.unrim's rule): an
edge pixel of the darkest blue or gold goes when two lighter neighbours hold the shape, else it takes the next shade.
The vital's shatter is a navy rose at 30 px (its petal lines are thinner than a pixel), lifted a shade to the blue
of its crest. Writes assets/source/fiora/fiora_fx_<name>.png plus
fiora_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel): the hits 16-20 px wide, the crit 26, the vital's
shatter 30, R's 32; the vital mark 14 tall; the parry crescent 44 tall; W's thrust 56 long (its line is 55000); the
slow ring 20 wide, the stun stars 18; the victory zone 72 wide (radius 35000); the Bladework aura's cell 36 wide round
her 40-px body; the speed lines 26; the dash dust 32. R's remaining vitals are 44 wide (their row of four), and the
challenge's crests land on them: its picture is squeezed to 72/84 across (Codex spread its four crests wider) and
held 4 source px lower, so the crests stay put when the remaining-vital loop takes over.
Anchors (from which point of the drawing a cell is cut): most cells on their middle, so a picture never drifts; W's
thrust on its white core row (row 71 of 128), then its top half mirrored onto the bottom (the game turns the
picture to the stab, upside down when she stabs left); the parry on its crescent's right edge (Codex's crescent
wanders 35 source px across the loop); the slow's ring on its widest rows (the ring rises in frames 4-5); the dash
dust and the speed lines on their lowest row over all frames, across at their puff.
The second step places every cell by its anchor on the unit and times it by the kit (60 ticks a second): a hit on the
chest, the vital beside it, the stun over the crown, R's crests round the waist, the ground pieces on the soles'
row; the vital mark and R's crests in 20-tick pieces (the kit replays them every 20 ticks while they last), the
challenge over the 22 ticks before the first of them, the parry over its 45 ticks (a caster picture played once:
the loop twice), the speed lines over the burst's strong half (45 ticks, a caster picture too), the thrust inside
its line's 11 ticks, the stun over its 1 s, the victory zone over its 3 s (opening 1-2, the loop 3-6 six times,
fading 7-8). Writes league/effects/league_fiora_fx and league_fiora_big (r_zone).
"""
import argparse
import json
import math
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from import_morgana import load_manifest, rect  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "fiora")
MOD = os.path.join(ROOT, "league")
Z = 8
HIT = (0, -8)                          # a hit on the upper body of a 35-40 px hero
VITAL = (9, -9)                        # a vital: beside the chest
WAIST = (0, -5)                        # the middle of R's ring of vitals
OVERHEAD = (0, -29)                    # over a 35-40 px hero's crown
GROUND = (0, 10)                       # the middle of a ring round a unit's feet (the soles 11 px under its pivot)
FEET = (0, 12)                         # the lowest row of dust at a unit's feet
MIDDLE = (0, -9)                       # the middle of Fiora (40 px, the crown 29 px over her pivot)
PARRY = (17, -9)                       # the parry crescent's right edge, in front of her
HEEL = (-1, 12)                        # the speed lines' puff at her heels
# the pack's colours (PROMPTS_FX.md)
STEEL = ["FFFFFF", "E6E8F0", "B8D8F8", "6FA8E8", "3A6FC0"]
BLUE = ["CFF4FF", "7FDFFF", "2FB0F0", "1470C8", "0B3F86"]
GOLD = ["FFF4C0", "FCD87A", "F9C740", "C99631", "784C17"]
MINT = ["E4FFF4", "8CF7C8", "36D99A"]
DUST = ["C8BCA8", "9A8C78", "6E6252"]
RAMPS = {"white": ["FFFFFF"], "steel": STEEL, "blue": BLUE, "gold": GOLD, "mint": MINT, "dust": DUST}
RIM = {"0B3F86": "1470C8", "784C17": "C99631"}   # Codex's ring shade -> the next shade
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]
R_S = 44 / 223                         # R's remaining vitals: their row of four (223 source px) 44 px wide

# raw strip -> native: frames; ramps; scale by `size` game px over `measure` ("w" the widest drawing, "h" the tallest,
# "cellw" the cell's width) or an explicit (x, y) `scale`; anchors per axis: "cell" the cell's middle, ("at", share)
# of the cell, ("px", source px) from the cell's top/left, "lowest" the lowest drawn row over all frames, "ring" the
# widest rows, "blade" the biggest piece's right edge; `mirror` the top half onto the bottom; `lift` shades
RAW = {
    "hit": dict(n=5, ramps="steel blue", size=16, measure="w"),
    "e_hit": dict(n=5, ramps="steel blue", size=18, measure="w"),
    "e_crit": dict(n=6, ramps="steel gold blue", size=26, measure="w"),
    "q_hit": dict(n=5, ramps="steel gold", size=20, measure="w"),
    "q_dash": dict(n=5, ramps="steel dust", size=32, measure="w", x=("at", 0.2), y="lowest"),
    "vital_mark": dict(n=4, ramps="white blue", size=14, measure="h"),
    "vital_hit": dict(n=6, ramps="white blue", size=30, measure="w", lift={"0B3F86": "1470C8"}),
    "w_parry": dict(n=4, ramps="white blue steel", size=44, measure="h", x="blade"),
    "w_line": dict(n=4, ramps="steel blue", size=56, measure="w", y=("px", 71.5), mirror=True),
    "w_hit": dict(n=5, ramps="steel blue", size=18, measure="w"),
    "w_slow": dict(n=6, ramps="white blue", size=20, measure="w", y="ring"),
    "w_stun": dict(n=8, ramps="white gold blue", size=18, measure="w"),
    "r_on": dict(n=6, ramps="white gold blue", scale=(R_S * 72 / 84, R_S), y=("px", 132)),
    "r_marks": dict(n=16, ramps="white blue", scale=(R_S, R_S)),
    "r_hit": dict(n=6, ramps="white gold blue", size=32, measure="w"),
    "r_zone": dict(n=8, ramps="white gold mint", size=72, measure="w"),
    "e_glint": dict(n=4, ramps="steel blue", size=36, measure="cellw"),
    "v_ms": dict(n=4, ramps="steel blue dust", size=26, measure="w", x=("at", 0.77), y="lowest"),
}


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = m[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
    return out


def snap(a, solid, pal):
    """Palette index of every solid pixel (-1 elsewhere), in chunks."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - pal[None]) ** 2).sum(2).argmin(1)
    return idx


def biggest(s):
    """(x0, x1, y0, y1) of the biggest 8-connected piece of a mask."""
    lab = np.zeros(s.shape, int)
    best, n = None, 0
    for y0, x0 in zip(*np.nonzero(s)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        q, pts = deque([(y0, x0)]), []
        while q:
            y, x = q.popleft()
            pts.append((y, x))
            for dy, dx in N8:
                yy, xx = y + dy, x + dx
                if 0 <= yy < s.shape[0] and 0 <= xx < s.shape[1] and s[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    q.append((yy, xx))
        if best is None or len(pts) > best[0]:
            p = np.array(pts)
            best = (len(pts), (p[:, 1].min(), p[:, 1].max() + 1, p[:, 0].min(), p[:, 0].max() + 1))
    return best[1]


def unrim(a):
    """The ring off: an edge pixel in a ramp's darkest shade goes when 2+ lighter 8-neighbours hold the shape, else it
    takes the ramp's next shade. Returns the picture and how many edge pixels were in the ring shade."""
    a = a.copy()
    op = a[..., 3] > 0
    hexa = np.array([["%02X%02X%02X" % tuple(p[:3]) for p in row] for row in a])
    rim = op & np.isin(hexa, list(RIM))
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    lit = sum(shifted(op & ~rim, dy, dx).astype(int) for dy, dx in N8)
    target = rim & edge
    gone = target & (lit >= 2)
    a[gone] = 0
    for dark, nxt in RIM.items():
        m = target & ~gone & (hexa == dark)
        a[m, :3] = rgb(nxt)
    return a, int(target.sum())


def mirror(cell, U):
    """The top half (rows 0..U) mirrored onto the bottom: exact symmetry about the anchor row."""
    out = cell.copy()
    for r in range(U):
        out[2 * U - r] = cell[r]
    return out


def anchors_of(spec, solid, rects, box):
    """Source (x, y) of every frame's anchor."""
    n = len(rects)
    out = []
    for axis, how in ((0, spec.get("x", "cell")), (1, spec.get("y", "cell"))):
        vals = []
        for k, (x, y, w, h) in enumerate(rects):
            o, size = (x, w) if axis == 0 else (y, h)
            if how == "cell":
                vals.append(o + size / 2)
            elif how == "lowest":
                vals.append(y + max(b[3] - r[1] for b, r in zip(box, rects)) - 0.5)
            elif how == "blade":
                vals.append(biggest(solid[y:y + h, x:x + w])[1] + x - 0.5)
            elif how == "ring":
                s = solid[y:y + h, x:x + w]
                widths = s.sum(1)
                rows = np.nonzero(widths >= 0.5 * widths.max())[0]
                widest = max(solid[r[1]:r[1] + r[3], r[0]:r[0] + r[2]].sum(1).max() for r in rects)
                vals.append(y + (rows.min() + rows.max() + 1) / 2 if widths.max() >= 0.5 * widest else None)
            elif how[0] == "at":
                vals.append(o + size * how[1])
            elif how[0] == "px":
                vals.append(o + how[1])
            else:
                raise ValueError(how)
        base = [r[axis] for r in rects]
        known = [v - b for v, b in zip(vals, base) if v is not None]
        vals = [v if v is not None else b + sum(known) / len(known) for v, b in zip(vals, base)]
        out.append(vals)
    return [(out[0][k], out[1][k]) for k in range(n)]


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "fiora_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"fiora_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [rect(f) for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        box = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            box.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        if "scale" in spec:
            sx, sy = spec["scale"]
        else:
            ext = {"cellw": lambda: max(r[2] for r in rects), "h": lambda: max(b[3] - b[2] for b in box),
                   "w": lambda: max(b[1] - b[0] for b in box)}[spec["measure"]]()
            sx = sy = spec["size"] / ext
        hexes = [h for r in spec["ramps"].split() for h in RAMPS[r]]
        idx = snap(a, solid, np.array([rgb(h) for h in hexes], float))
        pal = np.array([rgb(spec.get("lift", {}).get(h, h)) for h in hexes], np.uint8)
        anc = anchors_of(spec, solid, rects, box)
        L = math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, box)) * sx) + 1
        U = math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, box)) * sy) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * spec["n"], 4), np.uint8)
        rims = 0
        for k, (x, y, w, h) in enumerate(rects):
            ax, ay = anc[k]
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
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
            cell, n = unrim(out[:, k * tw:(k + 1) * tw])
            rims += n
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, k * tw:(k + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": spec["n"]}
        print(f"{fn}  {spec['n']} cells of {tw}x{th}, anchor {L},{U}, scale {sx:.4f}x{sy:.4f}, {rims} ring pixels, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"fiora_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"fiora_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


PIECE = [83, 83, 83, 84]                  # a 20-tick piece (the kit replays the marks every 20 ticks)
ZONE = [0, 1] + [2, 3, 4, 5] * 6 + [6, 7]
ZONE_MS = [100, 100] + [100] * 24 + [200, 200]

# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_fiora_fx": {
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "e_hit": [("e_hit", range(5), HIT, [50] * 5)],
        "e_crit": [("e_crit", range(6), HIT, [55] * 6)],
        "q_hit": [("q_hit", range(5), HIT, [50] * 5)],
        "q_dash": [("q_dash", range(5), FEET, [70] * 5)],
        "vital_mark": [("vital_mark", range(4), VITAL, PIECE)],
        "vital_hit": [("vital_hit", range(6), VITAL, [60] * 6)],
        "w_parry": [("w_parry", [0, 1, 2, 3] * 2, PARRY, [100] * 7 + [50])],
        "w_line": [("w_line", range(4), (0, 0), [33, 50, 50, 50])],
        "w_hit": [("w_hit", range(5), HIT, [50] * 5)],
        "w_slow": [("w_slow", range(6), GROUND, [80] * 6)],
        "w_stun": [("w_stun", range(8), OVERHEAD, [125] * 8)],
        "r_on": [("r_on", range(6), WAIST, [60] * 5 + [67])],
        "r_m4": [("r_marks", range(0, 4), WAIST, PIECE)],
        "r_m3": [("r_marks", range(4, 8), WAIST, PIECE)],
        "r_m2": [("r_marks", range(8, 12), WAIST, PIECE)],
        "r_m1": [("r_marks", range(12, 16), WAIST, PIECE)],
        "r_hit": [("r_hit", range(6), HIT, [60] * 6)],
        "e_glint": [("e_glint", range(4), MIDDLE, [100] * 4)],
        "v_ms": [("v_ms", [0, 1, 2, 3] * 2 + [0, 1], HEEL, [75] * 10)],
    },
    "league_fiora_big": {
        "r_zone": [("r_zone", ZONE, GROUND, ZONE_MS)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "fiora_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, parts in tags.items():
            out[tag] = []
            for src, used, (sx, sy), ms in parts:
                ax, ay = anchors[src]["anchor"]
                strip = cells(src, anchors[src]["frames"])
                out[tag] += [(G.centre_frame(strip[k], sx - ax, sy - ay), m) for k, m in zip(used, ms)]
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--only", action="append", help="with --raw: only this strip (repeatable)")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Import Veigar's effects (assets/source/veigar/PROMPTS.md, 1-12) as game sheets.

    python tools/art/import_veigar.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_veigar.py                                   # native strips -> effect sheets

The body comes from tools/art/rig_veigar.py and tools/art/import_native.py. Codex delivered image-model drafts
(soft alpha, free colours; manifest.json's `assets[].frames[].rect` gives the frames), so --raw turns every frame
into a cell of a native strip the way tools/art/import_akali.py does: each game pixel the majority colour of the
source pixels it covers, opaque when a third of them are solid, every colour snapped to the pack's 13 (the violet
energy ramp, the void darks, the evil gold). Writes assets/source/veigar/veigar_fx_<name>.png plus
veigar_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel): the attack bolt 12 px long, its hit 12; Q's bolt
22 long, its hit 16; the stack glow's cell 48 wide round his 37x40 body; the cage 64 wide (the zone's radius 28000,
the picture a little inside the reach it gets with the units' own radius) - Codex drew its bars as tall as the ring
is wide (60 px at that scale, taller than Darius), so the rows over the ring's back edge (row 82 of the cell) are
sampled 0.45 times as tall: walls of about 20 px, as the pack asked; the stun ring 16; Dark Matter's fall 48 at
its widest (the blast circle 22000), its hit on a unit 16; the ult's gathering orb 20, its bolt 20 long, its
explosion 30. The three bolts are drawn facing right and are mirrored top to bottom into exact symmetry (the game
turns them to their flight; a lopsided bolt would wobble between directions).
Anchors, measured on each drawing: hits and the gathering orb on their white core (the drawing's middle once it has
faded); the bolts on their core (the head that sits on the projectile's spot); the cage on its ground ellipse (frame
1 is the ellipse alone); Dark Matter on its target ellipse, the lowest blob of its first four frames (the sphere
touches it in the fifth); the stun ring and the stack glow on their cell's middle.
The second step places every cell by its anchor and times each view by the kit: the cage over its 3 s zone (forming
1-3, the loop 4-7 six times, fading 8-10), Dark Matter landing on the zone's hit 45 ticks after the cage forms (five
falling frames of 150 ms, then the impact) in two layers started together - w_mark, the ground band (the target
ellipse, the shockwave, the scorch) under the units, and w_fall, the sphere, the flash and the shards over them;
the stun ring over the 1 s stun, the gathering orb flashing when the ult's bolt leaves (the ult starts it on tick 2,
the bolt leaves on tick 12). Writes league/effects/league_veigar_fx and league_veigar_big (e_cage, w_mark, w_fall,
r_hit).
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
from import_morgana import Frames, load_manifest, rect  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "veigar")
MOD = os.path.join(ROOT, "league")
Z = 8
HIT = (0, -8)                          # a hit on the upper body of a 35-40 px hero
GROUND = (0, 10)                       # a point's ground: the soles 11 px under a unit's pivot
HIS = (0, -9)                          # the middle of Veigar (40 px from the hat's top to the soles)
OVERHEAD = (0, -31)                    # over a 35-40 px hero's crown
STAFF_TIP = (-9, -39)                  # the claw of his staff raised overhead at the top of the ult's leap
BURST = (0, -14)                       # the ult's orb flies 20 px over the pivot (y_offset -15000): its burst on the chest
# the pack's colours (PROMPTS.md): the violet energy ramp, the void darks, the evil gold
PAL = np.array([(0xFF, 0xFF, 0xFF), (0xEB, 0xDD, 0xFF), (0xBE, 0x95, 0xFF), (0x8F, 0x52, 0xF5), (0x5E, 0x27, 0xC8),
                (0x3B, 0x13, 0x8A), (0x21, 0x0A, 0x52), (0x2A, 0x1A, 0x40), (0x1A, 0x0E, 0x2E), (0x0E, 0x07, 0x18),
                (0xFF, 0xF6, 0xB0), (0xFF, 0xD8, 0x4A), (0xE8, 0xA0, 0x20)], float)

# raw strip -> native: frames, size in game px of `measure` ("w" drawing width, "cellw" cell width), anchor per axis
# ("centre" core or middle, "cell" the cell's middle, ("frame", [k]) the middle of frame k's drawing, ("core", ks)
# the mean white core, ("lowest", ks) the middle of the lowest blob), "mirror" for the bolts
RAW = {
    "orb": dict(n=4, size=12, measure="w", x=("core", None), y=("core", None), mirror=True),
    "hit": dict(n=5, size=12, measure="w", x="centre", y="centre"),
    "p_gain": dict(n=5, size=48, measure="cellw", x="cell", y="cell"),
    "q_bolt": dict(n=4, size=22, measure="w", x=("core", None), y=("core", None), mirror=True),
    "q_hit": dict(n=5, size=16, measure="w", x="centre", y="centre"),
    "e_cage": dict(n=10, size=64, measure="w", x=("frame", [0]), y=("frame", [0]), squash=(82, 0.45)),
    "e_stun": dict(n=4, size=16, measure="w", x="cell", y="cell"),
    "w_fall": dict(n=9, size=48, measure="w", x=("lowest", [0, 1, 2, 3]), y=("lowest", [0, 1, 2, 3])),
    "w_hit": dict(n=5, size=16, measure="w", x="centre", y="centre"),
    "r_cast": dict(n=5, size=20, measure="w", x="centre", y="centre"),
    "r_bolt": dict(n=4, size=20, measure="w", x=("core", None), y=("core", None), mirror=True),
    "r_hit": dict(n=7, size=30, measure="w", x="centre", y="centre"),
}


def lowest_blob(solid, r):
    """(middle x, middle y) of the lowest connected blob in a cell (Dark Matter's target ellipse)."""
    x, y, w, h = r
    s = solid[y:y + h, x:x + w]
    lab = np.zeros(s.shape, int)
    best = None
    n = 0
    for y0, x0 in zip(*np.nonzero(s)):
        if lab[y0, x0]:
            continue
        n += 1
        todo, px = [(y0, x0)], []
        lab[y0, x0] = n
        while todo:
            yy, xx = todo.pop()
            px.append((yy, xx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = yy + dy, xx + dx
                    if 0 <= ny < s.shape[0] and 0 <= nx < s.shape[1] and s[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        todo.append((ny, nx))
        if len(px) < 20:
            continue
        ys, xs = zip(*px)
        if best is None or max(ys) > best[0]:
            best = (max(ys), (min(xs) + max(xs) + 1) / 2, (min(ys) + max(ys) + 1) / 2)
    return x + best[1], y + best[2]


def anchor(fr, how, k, axis, rects, solid):
    if how == "cell":
        x, y, w, h = rects[k]
        return (x + w / 2) if axis == 0 else (y + h / 2)
    if isinstance(how, tuple) and how[0] == "lowest":
        return rects[k][axis] + np.mean([lowest_blob(solid, rects[j])[axis] - rects[j][axis] for j in how[1]])
    return fr.anchor(how, k, axis)


def mirror(cell, U):
    """The top half (rows 0..U) mirrored onto the bottom: exact symmetry about the anchor row."""
    out = cell.copy()
    for r in range(U):
        out[2 * U - r] = cell[r]
    return out


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "veigar_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"veigar_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [rect(f) for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        used = list(range(spec["n"]))
        fr = Frames(a, solid, rects)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - PAL[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        ext = max(rects[k][2] for k in used) if spec["measure"] == "cellw" else max(fr.extent("w", k) for k in used)
        s = spec["size"] / ext
        anc = {k: (anchor(fr, spec["x"], k, 0, rects, solid), anchor(fr, spec["y"], k, 1, rects, solid)) for k in used}
        cut, sq = spec.get("squash", (None, 1))

        def game_y(k, sy):
            """Source row sy of frame k -> game px from the anchor (rows over the cut `sq` times as tall)."""
            ay = anc[k][1]
            if cut is None or sy >= rects[k][1] + cut:
                return (sy - ay) * s
            yc = rects[k][1] + cut
            return (yc - ay) * s + (sy - yc) * s * sq

        def source_y(k, t):
            ay = anc[k][1]
            if cut is None:
                return ay + t / s
            yc = rects[k][1] + cut
            tc = (yc - ay) * s
            return ay + t / s if t >= tc else yc + (t - tc) / (s * sq)

        L = max(math.ceil(max(max(anc[k][0] - fr.box[k][0], fr.box[k][1] - anc[k][0]) for k in used) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(-game_y(k, fr.box[k][2]), game_y(k, fr.box[k][3])) for k in used) - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(used), 4), np.uint8)
        for i, k in enumerate(used):
            x, y, w, h = rects[k]
            ax, ay = anc[k]
            for r in range(th):
                sy0 = int(math.floor(source_y(k, r - U - 0.5)))
                sy1 = max(int(math.floor(source_y(k, r - U + 0.5))), sy0 + 1)
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
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(PAL)).argmax()
                    out[r, i * tw + c, :3] = PAL[col]
                    out[r, i * tw + c, 3] = 255
            if spec.get("mirror"):
                out[:, i * tw:(i + 1) * tw] = mirror(out[:, i * tw:(i + 1) * tw], U)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(used)}
        print(f"{fn}  {len(used)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over {ext} "
              f"source px), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"veigar_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"veigar_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# the cage over its 3 s zone: forming (3 x 60 ms), the loop six times (24 x 100), fading (3 x 140)
CAGE = [0, 1, 2] + [3, 4, 5, 6] * 6 + [7, 8, 9]
CAGE_MS = [60] * 3 + [100] * 24 + [140] * 3
# the stun ring over the 1 s stun
STUN = [0, 1, 2, 3] * 2 + [0, 1]

# Dark Matter in two layers started together: what lies on the ground (the target ellipse, the shockwave, the
# scorch: the rows from the ellipse's top down) under the units, the rest (the sphere, the flash, the shards) over them
FALL_MS = [150] * 5 + [80] * 4


def ground_top(cell):
    """The first row of the ground band: the top of the lowest drawing, under the last empty row."""
    rows = np.nonzero((cell[..., 3] > 0).any(1))[0]
    r = rows.max()
    while r - 1 in rows:
        r -= 1
    return r


def part(cells, which):
    """Keep the ground band ("ground") or everything over it ("air") of every cell."""
    top = ground_top(cells[0])
    out = []
    for c in cells:
        c = c.copy()
        if which == "ground":
            c[:top] = 0
        else:
            c[top:] = 0
        out.append(c)
    return out


# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame[, layer]), ...]}
FX = {
    "league_veigar_fx": {
        "orb": [("orb", range(4), (0, 0), [60] * 4)],
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "p_gain": [("p_gain", range(5), HIS, [60] * 5)],
        "q_bolt": [("q_bolt", range(4), (0, 0), [60] * 4)],
        "q_hit": [("q_hit", range(5), HIT, [50] * 5)],
        "e_stun": [("e_stun", STUN, OVERHEAD, [100] * len(STUN))],
        "w_hit": [("w_hit", range(5), HIT, [60] * 5)],
        "r_cast": [("r_cast", range(5), STAFF_TIP, [55, 55, 57, 60, 80])],
        "r_bolt": [("r_bolt", range(4), (0, 0), [60] * 4)],
    },
    "league_veigar_big": {
        "e_cage": [("e_cage", CAGE, GROUND, CAGE_MS)],
        "w_mark": [("w_fall", range(9), GROUND, FALL_MS, "ground")],
        "w_fall": [("w_fall", range(9), GROUND, FALL_MS, "air")],
        "r_hit": [("r_hit", range(7), BURST, [50, 50, 60, 70, 80, 90, 100])],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "veigar_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, parts in tags.items():
            out[tag] = []
            for src, used, (sx, sy), ms, *layer in parts:
                ax, ay = anchors[src]["anchor"]
                strip = cells(src, anchors[src]["frames"])
                if layer:
                    strip = part(strip, layer[0])
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

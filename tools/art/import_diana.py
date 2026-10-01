#!/usr/bin/env python3
"""Import Diana's effects (assets/source/diana/PROMPTS.md, 1-17) as game sheets.

    python tools/art/import_diana.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_diana.py                                   # native strips -> effect sheets

The body comes from tools/art/tidy_diana.py and import_native.py. Codex delivered each strip three ways
(diana_fx_pack_generated: equal cells in an 11-colour palette, native/ at its own guess of the game size, and raw/,
the image tool's output with real alpha, 1983-2172 x 724-793 px, every frame's rectangle in manifest.json as
`assets[].frames[].source_rect` = [x, y, w, h]). --raw starts from raw/ the way tools/art/import_vayne.py does: every
game pixel the majority colour of the source pixels it covers, opaque when a third of them are, the anchor on the middle
of a game pixel, one scale per strip set by the kit (1000 distance units a pixel) and measured on the drawings, into the
pack's 11 colours (moonlight, lavender, dark violet: the nearest to each source pixel). The two projectiles are turned
by the game, so they are made exactly symmetric about their core's row. The three orbit loops come from native/ as
they are: Codex laid its orb drawings on one 8-step path there, the two- and one-orb loops pixel subsets of the
three-orb one (their raw drawings each had their own path); and so does the moon: the tool squeezed its 12 frames into
its canvas (the raw frames 143-162 px wide, 748 tall: the ring 205 px wide would have made the column 250 px tall),
while native/ has the 70 x 120 cells the pack asked for, the ground spot at 85% of the height.
Sizes (game px): the hit 12, the cleave's hit 16, the cleave sweep 44 wide (its circle: 18000 round a point 18000 in
front), the crescent 22 tall (the bolt's 12000 radius plus a body), its hit 22, the Moonlight mark 10, the dash's ground
mark 26, the orbs forming 40, a flying orb 8, its burst 16, the shield 36 (round her 40-row body), Moonfall's pull ring
96 wide (radius 40000 plus both bodies), the moon's cells 70 x 120 (its ring about the crash radius), the moonlight strike 20.
Anchors, measured on each drawing: the projectiles on their white core; the hits, the burst, the mark and the forming
orbs on the fullest frame's middle; the sweep on its fullest frame's middle; the ground marks on their middle; the moon's
cells on their ground spot (85% down the middle).
The second step places every cell by its anchor: the hits on the upper body, the mark over the head, the ground marks
under the feet, the sweep 20 px in front of her waist, the orbs and the shield round her, the moon's ring on her feet
line, and times each view: the moon's crash on its sixth frame, 20 ticks after it starts (the kit's r_moon_lead).
No outline pass on the sheets. Writes assets/source/diana/diana_fx_<name>.png plus diana_fx_anchors.json, and
league/effects/league_diana_fx and league_diana_big.
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
from import_morgana import Frames  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "diana")
MOD = os.path.join(ROOT, "league")
Z = 8
HIT = (0, -8)                          # a hit on a 35 px hero's upper body
STRIKE = (0, -6)                       # Moonfall's strike on a hero
OVER = (0, -30)                        # over a 35 px hero's crown (the Moonlight mark)
FEET = (0, 10)                         # the ground under a unit
WAIST = (0, -1)                        # round Diana's waist (the orbs)
BODY = (0, -9)                         # the middle of her 40-row body (the shield)
SWEEP = (20, -4)                       # the cleave's sweep in front of her
GROUND = (0, 11)                       # her feet line (the moon's ring)
# the pack's 11 colours: moonlight, lavender, dark violet (Codex's manifest palette)
PAL = np.array([(0xFF, 0xFF, 0xFF), (0xEA, 0xF8, 0xFF), (0xBF, 0xE4, 0xF2), (0x8F, 0xC7, 0xD8), (0x5E, 0x97, 0xAE),
                (0xE6, 0xD8, 0xFF), (0xB9, 0xA2, 0xF0), (0x8B, 0x6F, 0xD6), (0x5F, 0x46, 0xA8),
                (0x3E, 0x2C, 0x74), (0x26, 0x18, 0x4A)], float)

# raw strip -> native: n frames, size in game px over measure ("w" widest drawing, "h" tallest), anchors as
# import_morgana.Frames.anchor; native=True takes native/ as it is (anchor = the cell's middle)
RAW = {
    "hit": dict(n=5, size=12, measure="w", x=("frame", [2]), y=("frame", [2])),
    "p_cleave": dict(n=6, size=44, measure="w", x=("frame", [2]), y=("frame", [2])),
    "p_hit": dict(n=5, size=16, measure="w", x=("frame", [1]), y=("frame", [1])),
    "q_bolt": dict(n=4, size=22, measure="h", x=("core", None), y=("core", None), mirror=True),
    "q_hit": dict(n=6, size=22, measure="w", x=("frame", [0]), y=("frame", [0])),
    "moon_mark": dict(n=6, size=10, measure="w", x=("frame", [0]), y=("frame", [0])),
    "e_hit": dict(n=6, size=26, measure="w", x=("frame", [2]), y=("frame", [2])),
    "w_cast": dict(n=6, size=40, measure="w", x=("frame", [1]), y=("frame", [1])),
    "w_orb3": dict(n=8, native=True),
    "w_orb2": dict(n=8, native=True),
    "w_orb1": dict(n=8, native=True),
    "w_orb": dict(n=4, size=8, measure="w", x=("core", None), y=("core", None), mirror=True),
    "w_boom": dict(n=6, size=16, measure="w", x=("frame", [1]), y=("frame", [1])),
    "w_shield": dict(n=6, size=36, measure="w", x=("frame", [0]), y=("frame", [0])),
    "r_draw": dict(n=8, size=96, measure="w", x=("frame", [0]), y=("frame", [0])),
    "r_moon": dict(n=12, native=True, frac=(0.5, 0.85)),
    "r_hit": dict(n=6, size=20, measure="w", x=("frame", [2]), y=("frame", [2])),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8-sig") as f:
        return {a["name"]: a for a in json.load(f)["assets"]}


def native_strip(folder, entry, n):
    """native/ as it is: n equal cells of native_cell, snapped to the palette."""
    a = np.asarray(Image.open(G.lp(os.path.join(folder, entry["native_file"]))).convert("RGBA")).copy()
    cw, ch = entry["native_cell"]
    a = a[:ch, :cw * n]
    op = a[..., 3] >= 128
    idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - PAL[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
    out = np.zeros_like(a)
    out[op, :3] = PAL[idx[op]]
    out[op, 3] = 255
    return out, cw, ch


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "diana_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        entry = manifest[name]
        if spec.get("native"):
            out, tw, th = native_strip(folder, entry, spec["n"])
            fx, fy = spec.get("frac", (0.5, 0.5))
            L, U = int(tw * fx), int(th * fy)
            scale = "native, as delivered"
        else:
            a = np.asarray(Image.open(G.lp(os.path.join(folder, entry["raw_file"])))).copy()
            if a.ndim == 2 or a.shape[2] == 3:
                a = np.asarray(Image.open(G.lp(os.path.join(folder, entry["raw_file"]))).convert("RGBA")).copy()
            solid = a[..., 3] >= 100
            rects = [[int(v) for v in f["source_rect"]] for f in entry["frames"]]
            if len(rects) != spec["n"]:
                sys.exit(f"{entry['raw_file']}: {len(rects)} frames, not {spec['n']}")
            fr = Frames(a, solid, rects)
            idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - PAL[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
            used = list(range(spec["n"]))
            anc = {k: (fr.anchor(spec["x"], k, 0), fr.anchor(spec["y"], k, 1)) for k in used}
            ext = max(fr.box[k][1] - fr.box[k][0] for k in used) if spec["measure"] == "w" else \
                max(fr.box[k][3] - fr.box[k][2] for k in used)
            s = spec["size"] / ext
            L = max(math.ceil(max(max(anc[k][0] - fr.box[k][0], fr.box[k][1] - anc[k][0]) for k in used) * s - 0.5), 0) + 1
            U = max(math.ceil(max(max(anc[k][1] - fr.box[k][2], fr.box[k][3] - anc[k][1]) for k in used) * s - 0.5), 0) + 1
            tw, th = 2 * L + 1, 2 * U + 1
            scale = f"{s:.4f} ({spec['size']} px over {ext} source px)"
            out = np.zeros((th, tw * len(used), 4), np.uint8)
            for i, k in enumerate(used):
                x, y, w, h = rects[k]
                ax, ay = anc[k]
                for r in range(th):
                    y0 = int(math.floor(ay + (r - U - 0.5) / s))
                    y1 = max(int(math.floor(ay + (r - U + 0.5) / s)), y0 + 1)
                    y0, y1 = max(y, y0), min(y + h, y1)
                    if y1 <= y0:
                        continue
                    for c in range(tw):
                        x0 = int(math.floor(ax + (c - L - 0.5) / s))
                        x1 = max(int(math.floor(ax + (c - L + 0.5) / s)), x0 + 1)
                        x0, x1 = max(x, x0), min(x + w, x1)
                        if x1 <= x0:
                            continue
                        m = solid[y0:y1, x0:x1]
                        if m.mean() < 1 / 3:
                            continue
                        col = np.bincount(idx[y0:y1, x0:x1][m], minlength=len(PAL)).argmax()
                        out[r, i * tw + c, :3] = PAL[col]
                        out[r, i * tw + c, 3] = 255
                if spec.get("mirror"):
                    cell = out[:, i * tw:(i + 1) * tw]
                    cell[U + 1:] = cell[:U][::-1]
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"diana_fx_{name}.png")))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": spec["n"]}
        print(f"diana_fx_{name}.png  {spec['n']} cells of {tw}x{th}, anchor {L},{U}, scale {scale}, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"diana_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"diana_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_diana_fx": {
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "p_hit": [("p_hit", range(5), HIT, [50] * 5)],
        "q_bolt": [("q_bolt", range(4), (0, 0), [60] * 4)],
        "q_hit": [("q_hit", range(6), HIT, [50] * 6)],
        "moon_mark": [("moon_mark", range(6), OVER, [100] * 6)],
        "e_hit": [("e_hit", range(6), FEET, [60] * 6)],
        "w_cast": [("w_cast", range(6), WAIST, [60] * 6)],
        "w_orb3": [("w_orb3", range(8), WAIST, [80] * 8)],
        "w_orb2": [("w_orb2", range(8), WAIST, [80] * 8)],
        "w_orb1": [("w_orb1", range(8), WAIST, [80] * 8)],
        "w_orb": [("w_orb", range(4), (0, 0), [60] * 4)],
        "w_boom": [("w_boom", range(6), HIT, [50] * 6)],
        "w_shield": [("w_shield", range(6), BODY, [100] * 6)],
        "r_hit": [("r_hit", range(6), STRIKE, [60] * 6)],
    },
    "league_diana_big": {
        "p_cleave": [("p_cleave", range(6), SWEEP, [50] * 6)],
        "r_draw": [("r_draw", range(8), FEET, [60] * 8)],
        # the crash on frame 6: five frames of fall in 20 ticks (the kit's r_moon_lead)
        "r_moon": [("r_moon", range(12), GROUND, [66] * 5 + [70] * 7)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "diana_fx_anchors.json")), encoding="utf-8") as f:
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

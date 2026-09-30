#!/usr/bin/env python3
"""Import Vayne's effects (assets/source/vayne/PROMPTS.md, 1-14) as game sheets.

    python tools/art/import_vayne.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_vayne.py                                   # native strips -> effect sheets

The body comes from tools/art/export_vayne.py, tidy_vayne.py and import_native.py. Codex delivered each strip three
ways (vayne_fx_complete: its own 8x export at the layout's canvas, native/ at 1/8 of that, and raw/, the image
tool's own output with real alpha, 2098-2206 x 713-836 px, with every frame's rectangle in manifest.json as
`assets[].frames[].rawRect`). Its exports put one game pixel on every 8x8 block of the layout canvas, so a basic
attack's bolt came out 29 px long and its hit 20 px (the kit wants 12), and for Final Hour's three pictures it
cleared the middle of every cell (x 22.5-77.5%, y 17-89%) to keep her body free - the flare's rays, the refresh's
ring and most of the aura's motes went with it. --raw therefore starts from raw/: every frame of a strip is sampled
the way tools/art/import_briar.py does it (each game pixel the majority colour of the source pixels it covers,
opaque when a third of them are, the anchor on the middle of a game pixel; one scale per strip, set by the kit at
1000 distance units a pixel and measured on the drawings), into the pack's four ramps (silver, night purple,
crimson, dust: 16 colours, the nearest to each source pixel). The three bolts are turned to their direction by the
game, so they are made exactly symmetric about their core's row. Final Hour's pictures keep their middles: they are
drawn under the units (z -1, the kit), so her own body covers what is behind it. The tool packed their 7 and 5
frames into its fixed canvas (frames 0.40 and 0.56 as wide as tall, the pack asked 0.75), so they are sampled back
into 3:4 cells, x and y each to its own scale.
Sizes (game px): the bolt 16 with its trail (12 left a 4 px arrow), Tumble's bolt 18, Condemn's 24 (long); the hits
12, 20 and 24; Silver Bolts' rings 16 and 18 across, the burst 26; the roll's smoke 28 wide; the slam 20 and its stars
16; Final Hour's cast and aura 40 x 53 cells, the refresh 35 x 47 (her figure is 40 tall with the ponytail; they were
48 x 64 and 42 x 56 round the first, 48-row design).
Anchors, measured on each drawing: the bolts on their white core (their head); the hits and the burst on their core
or the first full frame's middle; the rings on their middle; the smoke on its lowest row; the slam on its middle,
its stars on theirs; Final Hour's cells on the point 92% down their middle, where the pack put her feet.
The second step places every cell by its anchor: the bolts on the projectile's point, the hits on the upper body,
the rings round the chest, the smoke and Final Hour on the ground under her, the stars over a 35 px hero's head, and
times each view by the kit: the slam's stars loop for the rest of the 1 s stun, the aura loops (a buff view).
No outline pass on the sheets. Writes assets/source/vayne/vayne_fx_<name>.png plus vayne_fx_anchors.json, and
league/effects/league_vayne_fx.
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

SRC = os.path.join(ROOT, "assets", "source", "vayne")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)                         # the ground under a unit (11 px under its pivot)
BODY = (0, -6)                         # the middle of a 35 px hero
HIT = (0, -8)                          # a hit on the upper body
CHEST = (0, -9)                        # Silver Bolts' rings round a 35 px hero's chest
OVERHEAD = (0, -29)                    # over a 35 px hero's crown (the slam's stars)
# the pack's four ramps: silver, night purple, crimson, dust
PAL = np.array([(0xFF, 0xFF, 0xFF), (0xEE, 0xF0, 0xFF), (0xC8, 0xCA, 0xE8), (0x9A, 0x9C, 0xC8), (0x6A, 0x6E, 0x9E),
                (0x5A, 0x3C, 0x84), (0x3A, 0x26, 0x60), (0x22, 0x16, 0x3C), (0x14, 0x0C, 0x24),
                (0xFF, 0xD0, 0xD6), (0xFF, 0x5A, 0x6E), (0xD8, 0x20, 0x3E), (0x8F, 0x0B, 0x24),
                (0xE0, 0xD2, 0xB0), (0xB0, 0x98, 0x78), (0x7A, 0x64, 0x48)], float)

# raw strip -> native: n frames in the source, size in game px over measure ("w" widest drawing, "h" tallest), or
# cell = (w, h) game px for the whole frame rectangle (x and y scaled apart); anchors as import_morgana.RAW, plus
# ("cellfrac", fx, fy): that point of the frame's rectangle; src: another strip's PNG; frames: the ones taken
RAW = {
    "bolt": dict(n=4, size=16, measure="w", x=("core", None), y=("core", None), mirror=True),
    "q_bolt": dict(n=4, size=18, measure="w", x=("core", None), y=("core", None), mirror=True),
    "e_bolt": dict(n=4, size=24, measure="w", x=("core", None), y=("core", None), mirror=True),
    "hit": dict(n=5, size=12, measure="w", x="centre", y="centre"),
    "q_hit": dict(n=6, size=20, measure="w", x=("frame", [1]), y=("frame", [1])),
    "sb_ring1": dict(n=6, size=16, measure="w", x=("frame", [1, 2, 3]), y=("frame", [1, 2, 3])),
    "sb_ring2": dict(n=6, size=18, measure="w", x=("frame", [1, 2, 3]), y=("frame", [1, 2, 3])),
    "sb_proc": dict(n=7, size=26, measure="w", x=("frame", [0]), y=("frame", [0])),
    "q_roll": dict(n=6, size=28, measure="w", x=("frame", [2]), y=("bottom", 2)),
    "e_hit": dict(n=5, size=24, measure="w", x=("frame", [1]), y=("frame", [1])),
    "e_stun": dict(n=8, frames=[0, 1, 2, 3], size=20, measure="w", x=("frame", [1]), y=("frame", [1])),
    "e_stars": dict(src="e_stun", n=8, frames=[4, 5, 6, 7], size=16, measure="w", x=("frame", [4, 5, 6, 7]),
                    y=("frame", [4, 5, 6, 7])),
    "r_cast": dict(n=7, cell=(40, 53), x=("cellfrac", 0.5, 0.92), y=("cellfrac", 0.5, 0.92)),
    "r_refresh": dict(n=5, cell=(35, 47), x=("cellfrac", 0.5, 0.92), y=("cellfrac", 0.5, 0.92)),
    "r_aura": dict(n=4, cell=(40, 53), x=("cellfrac", 0.5, 0.92), y=("cellfrac", 0.5, 0.92)),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8-sig") as f:
        return {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}


def anchor(fr, how, k, axis, rects):
    if isinstance(how, tuple) and how[0] == "cellfrac":
        x, y, w, h = rects[k]
        return x + how[1] * w if axis == 0 else y + how[2] * h
    return fr.anchor(how, k, axis)


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "vayne_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        entry = manifest[f"vayne_fx_{spec.get('src', name)}.png"]
        a = np.asarray(Image.open(G.lp(os.path.join(folder, entry["raw_file"]))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rawRect"]] for f in entry["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{entry['raw_file']}: {len(rects)} frames, not {spec['n']}")
        used = spec.get("frames", list(range(spec["n"])))
        fr = Frames(a, solid, rects)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - PAL[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        anc = {k: (anchor(fr, spec["x"], k, 0, rects), anchor(fr, spec["y"], k, 1, rects)) for k in used}
        if "cell" in spec:                      # the whole rectangle into a cell, x and y each to its own scale
            tw, th = spec["cell"]
            sx = [tw / rects[k][2] for k in used]
            sy = [th / rects[k][3] for k in used]
            L, U = tw // 2, int(round(th * spec["y"][2]))
            tw, th = 2 * L + 1, 2 * U + 1       # the anchor on a middle pixel, as for the others
            scale = f"{min(sx):.4f}-{max(sx):.4f} x {min(sy):.4f}-{max(sy):.4f}"
        else:
            # measured over the frames this strip takes (the slam and its stars share one source)
            ext = max(fr.box[k][1] - fr.box[k][0] for k in used) if spec["measure"] == "w" else \
                max(fr.box[k][3] - fr.box[k][2] for k in used)
            s = spec["size"] / ext
            sx = sy = [s] * len(used)
            L = max(math.ceil(max(max(anc[k][0] - fr.box[k][0], fr.box[k][1] - anc[k][0]) for k in used) * s - 0.5), 0) + 1
            U = max(math.ceil(max(max(anc[k][1] - fr.box[k][2], fr.box[k][3] - anc[k][1]) for k in used) * s - 0.5), 0) + 1
            tw, th = 2 * L + 1, 2 * U + 1
            scale = f"{s:.4f} ({spec['size']} px over {ext} source px)"
        out = np.zeros((th, tw * len(used), 4), np.uint8)
        for i, k in enumerate(used):
            x, y, w, h = rects[k]
            ax, ay = anc[k]
            for r in range(th):
                y0 = int(math.floor(ay + (r - U - 0.5) / sy[i]))
                y1 = max(int(math.floor(ay + (r - U + 0.5) / sy[i])), y0 + 1)
                y0, y1 = max(y, y0), min(y + h, y1)
                if y1 <= y0:
                    continue
                for c in range(tw):
                    x0 = int(math.floor(ax + (c - L - 0.5) / sx[i]))
                    x1 = max(int(math.floor(ax + (c - L + 0.5) / sx[i])), x0 + 1)
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
            G.lp(os.path.join(SRC, f"vayne_fx_{name}.png")))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(used)}
        print(f"vayne_fx_{name}.png  {len(used)} cells of {tw}x{th}, anchor {L},{U}, scale {scale}, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"vayne_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"vayne_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# Condemn's slam: the stun is 1 s (60 ticks); the impact's four frames take 240 ms, the stars loop for the rest
STARS = [0, 1, 2, 3, 0, 1, 2, 3]

# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_vayne_fx": {
        "bolt": [("bolt", range(4), (0, 0), [60] * 4)],
        "q_bolt": [("q_bolt", range(4), (0, 0), [60] * 4)],
        "e_bolt": [("e_bolt", range(4), (0, 0), [60] * 4)],
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "q_hit": [("q_hit", range(6), HIT, [50] * 6)],
        "sb_ring1": [("sb_ring1", range(6), CHEST, [60, 60, 120, 120, 100, 80])],
        "sb_ring2": [("sb_ring2", range(6), CHEST, [60, 60, 120, 120, 100, 80])],
        "sb_proc": [("sb_proc", range(7), CHEST, [50, 50, 50, 60, 60, 70, 70])],
        "q_roll": [("q_roll", range(6), FEET, [70] * 6)],
        "e_hit": [("e_hit", range(5), BODY, [60] * 5)],
        "e_stun": [("e_stun", range(4), BODY, [60] * 4), ("e_stars", STARS, OVERHEAD, [95] * 8)],
        "r_cast": [("r_cast", range(7), FEET, [70] * 7)],
        "r_refresh": [("r_refresh", range(5), FEET, [70] * 5)],
        "r_aura": [("r_aura", range(4), FEET, [110] * 4)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "vayne_fx_anchors.json")), encoding="utf-8") as f:
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

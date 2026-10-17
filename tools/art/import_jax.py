#!/usr/bin/env python3
"""Import Jax's effects (assets/source/jax/PROMPTS_FX.md, 1-10) as game sheets.

    python tools/art/import_jax.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_jax.py                                   # native strips -> effect sheets

The body comes from tools/art/export_jax.py and import_native.py. The effects are read the way
tools/art/import_vayne.py reads Vayne's: every frame of a strip sampled to game pixels (each the majority colour of
the source pixels it covers, opaque when a third of them are, the anchor on the middle of a game pixel; one scale per
strip, set by the kit at 1000 distance units a pixel - a ground ring's radius plus the two units' collision radii,
about 17000 - and measured on the drawings), into the pack's four ramps (lantern fire, bronze, violet energy, dust:
19 colours, the nearest to each source pixel). No outline pass on the sheets (effects carry none).
Frames: a manifest.json with `assets[].frames[].rawRect` per strip (Vayne's delivery) is used when there is one;
otherwise every PNG is the one row of equal cells the pack asked for, cut in equal widths (the default), or at the
empty columns nearest those lines (`--gaps`: Counter Strike's burst and the slam overran their cells).
Sizes (game px, PROMPTS_FX.md): the hit 16, Empower's 26, the Grandmaster proc 22, Leap Strike's landing 32 wide,
the stun's stars 18, Counter Strike's whirl 52 (its ring; 44 sat inside his stance), its burst 96 and the ult's
slam 104 (radius + 17000 either side), the slam's hit 20, the ult's aura 56 wide (48 hugged his lamppost).
Anchors, measured on each drawing, and where they go from the pivot (11.5 px over the feet): the hits on their core
or the first full frame's middle, on the upper body; the landing's dust on its lowest row, on the feet line; the
stars on their middle, over a 35 px hero's crown; the whirl, the burst and the slam on their ground ring's middle
(the full frame's for the last two), on the ground under him; the aura on its halo's lowest row, just under the feet.
Writes assets/source/jax/jax_fx_<name>.png (8x) plus jax_fx_anchors.json, and league/effects/league_jax_fx and
league_jax_big (the ground rings and the aura, bigger than the rest).
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

SRC = os.path.join(ROOT, "assets", "source", "jax")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)                         # the ground under a unit (11 px under its pivot)
GROUND = (0, 9)                        # the middle of a ring round a unit's feet
HIT = (0, -7)                          # a hit on the upper body of a 35 px hero
OVERHEAD = (0, -29)                    # over a 35 px hero's crown
# the pack's four ramps: lantern fire, bronze, violet energy, dust
PAL = np.array([(0xFF, 0xFF, 0xFF), (0xFF, 0xF3, 0xB8), (0xFF, 0xD2, 0x4A), (0xFF, 0x9A, 0x1F), (0xE0, 0x56, 0x0F),
                (0x8A, 0x29, 0x01),
                (0xFF, 0xE7, 0xA0), (0xE4, 0xBE, 0x6A), (0xB4, 0x83, 0x40), (0x70, 0x4A, 0x23),
                (0xF4, 0xC6, 0xFF), (0xD0, 0x6C, 0xF0), (0x9A, 0x34, 0xC8), (0x5E, 0x1E, 0x86), (0x2E, 0x0E, 0x48),
                (0xE8, 0xD6, 0xB0), (0xB8, 0x9C, 0x74), (0x7C, 0x64, 0x46), (0x4A, 0x3A, 0x2A)], float)

# raw strip -> native: n frames, size in game px over measure ("w" widest drawing, "ring" its ring's width), or
# cell = (w, h) game px for the whole frame rectangle; anchors as import_morgana.Frames.anchor plus ("cellfrac",
# fx, fy): that point of the frame's rectangle, and ("ringof", [k...]): the middle of those frames' ground ring (the
# widest connected drawing's rows at least half its width - the flames over Counter Strike's ring and the dust round
# the slam would lift a box's middle off the ground)
RAW = {
    "hit": dict(n=5, size=16, measure="w", x="centre", y="centre"),
    "w_hit": dict(n=6, size=26, measure="w", x=("frame", [1]), y=("frame", [1])),
    "r_proc": dict(n=6, size=22, measure="w", x=("frame", [1]), y=("frame", [1])),
    "q_hit": dict(n=6, size=32, measure="w", x=("frame", [2]), y=("bottom", 2)),
    "stun": dict(n=8, size=18, measure="w", x=("frame", list(range(8))), y=("frame", list(range(8)))),
    "e_stance": dict(n=4, size=52, measure="ring", x=("ringof", [0, 1, 2, 3]), y=("ringof", [0, 1, 2, 3])),
    "e_burst": dict(n=7, size=96, measure="w", x=("ringof", [3]), y=("ringof", [3])),
    "r_slam": dict(n=8, size=104, measure="w", x=("ringof", [3]), y=("ringof", [3])),
    "r_hit": dict(n=5, size=20, measure="w", x="centre", y="centre"),
    "r_aura": dict(n=4, size=56, measure="w", x=("frame", [0, 1, 2, 3]), y=("bottom", 0)),
}


def lp(p):
    return G.lp(p)


def rects_of(folder, name, a, n, gaps):
    """The frames' rectangles [x, y, w, h] in the source: the manifest's, or equal cells, or cut at the gaps."""
    man = os.path.join(folder, "manifest.json")
    if os.path.exists(man):
        with open(man, encoding="utf-8-sig") as f:
            data = json.load(f)
        for entry in (data.get("assets", []) if isinstance(data, dict) else []):
            if os.path.basename(entry.get("file", "")) == f"jax_fx_{name}.png" and entry.get("frames"):
                return [[int(v) for v in fr["rawRect"]] for fr in entry["frames"]]
    H, W = a.shape[:2]
    if not gaps:
        return [[int(round(k * W / n)), 0, int(round((k + 1) * W / n)) - int(round(k * W / n)), H] for k in range(n)]
    cols = (a[..., 3] >= 100).any(0)
    mids, x = [], 0                       # the middles of the empty runs of columns between drawings
    while x < W:
        if not cols[x]:
            x0 = x
            while x < W and not cols[x]:
                x += 1
            if x0 > 0 and x < W:
                mids.append((x0 + x) / 2)
        else:
            x += 1
    # a cut per equal-cell line, at the empty run nearest it (a fading frame's own gaps lie off the lines; the full
    # rings overran their cells, so the line itself cut through them)
    cell = W / n
    edges = [0]
    for k in range(1, n):
        near = [m for m in mids if abs(m - k * cell) <= 0.45 * cell and m > edges[-1]]
        edges.append(int(round(min(near, key=lambda m: abs(m - k * cell)) if near else k * cell)))
    edges.append(W)
    return [[edges[k], 0, edges[k + 1] - edges[k], H] for k in range(n)]


def anchor(fr, how, k, axis, rects):
    if isinstance(how, tuple) and how[0] == "cellfrac":
        x, y, w, h = rects[k]
        return x + how[1] * w if axis == 0 else y + how[2] * h
    if isinstance(how, tuple) and how[0] == "ringof":
        return rects[k][axis] + np.mean([fr.ring[j][axis] - rects[j][axis] for j in how[1]])
    return fr.anchor(how, k, axis)


def from_raw(folder, only=None, gaps=False):
    path = os.path.join(SRC, "jax_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(lp(path)):
        with open(lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        a = np.asarray(Image.open(lp(os.path.join(folder, f"jax_fx_{name}.png"))).convert("RGBA")).copy()
        if not (a[..., 3] < 255).any():             # delivered on black: alpha from the brightness
            a[..., 3] = np.clip(a[..., :3].max(-1).astype(int) * 3, 0, 255)
        solid = a[..., 3] >= 100
        rects = rects_of(folder, name, a, spec["n"], gaps)
        used = list(range(spec["n"]))
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
            ext = fr.extent(spec["measure"])
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
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(lp(os.path.join(SRC, f"jax_fx_{name}.png")))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(used)}
        print(f"jax_fx_{name}.png  {len(used)} cells of {tw}x{th}, anchor {L},{U}, scale {scale}, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"jax_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"jax_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


STUN_MS = 1000                          # Counter Strike's stun (the kit's e_stun, 60 ticks)

# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_jax_fx": {
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "w_hit": [("w_hit", range(6), HIT, [50] * 6)],
        "r_proc": [("r_proc", range(6), HIT, [50, 60, 60, 60, 60, 60])],
        "q_hit": [("q_hit", range(6), FEET, [50, 60, 60, 70, 70, 70])],
        "stun": [("stun", range(8), OVERHEAD, [STUN_MS // 8] * 8)],
        "e_stance": [("e_stance", range(4), GROUND, [100] * 4)],
        "r_hit": [("r_hit", range(5), HIT, [50] * 5)],
    },
    "league_jax_big": {
        "e_burst": [("e_burst", range(7), GROUND, [50, 60, 60, 60, 70, 70, 70])],
        "r_slam": [("r_slam", range(8), GROUND, [50, 60, 60, 70, 70, 80, 80, 80])],
        "r_aura": [("r_aura", range(4), (0, 14), [110] * 4)],     # the halo's lowest row 2.5 px under the feet
    },
}


def build():
    with open(lp(os.path.join(SRC, "jax_fx_anchors.json")), encoding="utf-8") as f:
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
    ap.add_argument("--gaps", action="store_true", help="with --raw: cut the frames at the empty columns")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only, args.gaps)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

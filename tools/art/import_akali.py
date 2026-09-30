#!/usr/bin/env python3
"""Import Akali's effects (assets/source/akali/PROMPTS.md, 1-15) as game sheets.

    python tools/art/import_akali.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_akali.py                                   # native strips -> effect sheets

The body comes from tools/art/design_akali.py and tools/art/import_native.py. --raw turns every frame of Codex's
strips into a cell of a native strip the way tools/art/import_briar.py does (every game pixel one flat 8x8 block,
binary alpha, Codex's own colours, each game pixel the majority colour of the source pixels it covers, opaque when a
third of them are; manifest.json's `assets[].frames[].rect` gives the frames). Writes
assets/source/akali/akali_fx_<name>.png plus akali_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel): the kama hit 16 px, the empowered crescent 28,
the mark's ground ring 36 wide, the ready motes' cell 34 wide round her 43 px body (the prompt's 34x32; its table
still said 24x30), Q's fan 45 long (its cone's radius 45000: the view is centred on the line, the apex at the left
end), its hit 12, the smoke 70 wide (drawn for Q's 30000 zone; Twilight Shroud now rides E and hides her 2 s wherever
she goes, so it only marks where she landed), the shuriken 12 tall (its tail trails left), its hit
16, the mark over the head 12, E's dash streak 48 long, its slash 20, R's streak 64 long (the rush covers 72000), its
pass-through slash 22 and the execution's X 30.
Anchors, measured on each drawing: hits on their white core (or the drawing's middle once it has faded); the ring and
the smoke on their middle; the ready motes and the fan on their cell's middle; the shuriken on its white core; the
mark on its middle; the two dash streaks on their left end (where she starts) at their middle height, so the streak
lies along the path she runs.
The second step places every cell by its anchor and times each view by the kit: the fan over its 14-tick line, the
smoke over the 2 s of invisibility (open 1-3, frames 4-7 three times, fade 8-10), the buff views loop (the ready motes for
the 4 s window, the mark for its 0.7 s). No palette or outline pass on the sheets. Writes league/effects/league_akali_fx
and league/effects/league_akali_big (q_fan, w_smoke, e_dash, r_dash).
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
from import_leona import palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "akali")
MOD = os.path.join(ROOT, "league")
Z = 8
HIT = (0, -8)                          # a hit on the upper body of a 35 px hero
GROUND = (0, 10)                       # the middle of a ring round a unit's feet (the soles 11 px under the pivot)
HERS = (0, -10)                        # the middle of Akali (43 px from the crown to the soles)
OVERHEAD = (0, -31)                    # over a 35 px hero's crown

# raw strip -> native (see import_morgana.RAW for the measures and anchors; ("left", frames) is the drawing's left
# edge, averaged over those frames)
RAW = {
    "hit": dict(n=5, size=16, measure="w", x="centre", y="centre"),
    "p_hit": dict(n=6, size=28, measure="w", x=("frame", [1, 2]), y=("frame", [1, 2])),
    "p_ring": dict(n=6, size=36, measure="w", x=("frame", [1, 2, 3]), y=("frame", [1, 2, 3])),
    "p_ready": dict(n=4, size=34, measure="cellw", x="cell", y="cell"),
    "q_fan": dict(n=6, size=45, measure="cellw", x="cell", y="cell"),
    "q_hit": dict(n=4, size=12, measure="w", x="centre", y="centre"),
    "w_smoke": dict(n=10, size=70, measure="w", x=("frame", [3, 4, 5, 6]), y=("frame", [3, 4, 5, 6])),
    "e_shuriken": dict(n=4, size=12, measure="h", x=("core", None), y=("core", None)),
    "e_hit": dict(n=5, size=16, measure="w", x="centre", y="centre"),
    "e_mark": dict(n=4, size=12, measure="w", x=("frame", [0, 1, 2, 3]), y=("frame", [0, 1, 2, 3])),
    "e_dash": dict(n=5, size=48, measure="cellw", x=("left", [0, 1, 2]), y=("frame", [1, 2])),
    "e2_hit": dict(n=5, size=20, measure="w", x="centre", y="centre"),
    "r_dash": dict(n=6, size=64, measure="cellw", x=("left", [1, 2, 3]), y=("frame", [1, 2, 3])),
    "r1_hit": dict(n=5, size=22, measure="w", x="centre", y="centre"),
    "r2_hit": dict(n=6, size=30, measure="w", x=("core", [2, 3]), y=("core", [2, 3])),
}


def extent(fr, spec, used, rects):
    if spec["measure"] == "cellw":
        return max(rects[k][2] for k in used)
    if spec["measure"] == "cellh":
        return max(rects[k][3] for k in used)
    return max(fr.extent(spec["measure"], k) for k in used)


def anchor(fr, how, k, axis, rects):
    if how == "cell":
        x, y, w, h = rects[k]
        return (x + w / 2) if axis == 0 else (y + h / 2)
    if isinstance(how, tuple) and how[0] == "left":
        return rects[k][0] + np.mean([fr.box[j][0] - rects[j][0] for j in how[1]])
    return fr.anchor(how, k, axis)


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "akali_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"akali_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        if not (a[..., 3] < 255).any():             # delivered on black: alpha from the brightness
            a[..., 3] = np.clip(a[..., :3].max(-1).astype(int) * 3, 0, 255)
        solid = a[..., 3] >= 100
        if fn in manifest:
            rects = [rect(f) for f in manifest[fn]["frames"]]
        else:
            W = a.shape[1]
            rects = [[k * W // spec["n"], 0, (k + 1) * W // spec["n"] - k * W // spec["n"], a.shape[0]]
                     for k in range(spec["n"])]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        used = list(range(spec["n"]))
        fr = Frames(a, solid, rects)
        own = np.unique(a[solid][:, :3], axis=0)
        pal = own.astype(float) if len(own) <= 16 else palette(a)   # Codex's clean strips keep their own colours
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        ext = extent(fr, spec, used, rects)
        s = spec["size"] / ext
        anc = {k: (anchor(fr, spec["x"], k, 0, rects), anchor(fr, spec["y"], k, 1, rects)) for k in used}
        L = max(math.ceil(max(max(anc[k][0] - fr.box[k][0], fr.box[k][1] - anc[k][0]) for k in used) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(anc[k][1] - fr.box[k][2], fr.box[k][3] - anc[k][1]) for k in used) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(used), 4), np.uint8)
        for i, k in enumerate(used):
            x, y, w, h = rects[k]
            ax, ay = anc[k]
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
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, i * tw + c, :3] = pal[col]
                    out[r, i * tw + c, 3] = 255
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"akali_fx_{name}.png")))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(used)}
        print(f"akali_fx_{name}.png  {len(used)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} "
              f"({spec['size']} px over {ext} source px), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"akali_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"akali_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# the smoke for the 2 s of invisibility: opening, the four-frame loop three times, fading (18 frames of 111 ms)
SMOKE = [0, 1, 2] + [3, 4, 5, 6] * 3 + [7, 8, 9]

# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_akali_fx": {
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "p_hit": [("p_hit", range(6), HIT, [60] * 6)],
        "p_ring": [("p_ring", range(6), GROUND, [100] * 6)],
        "p_ready": [("p_ready", range(4), HERS, [120] * 4)],
        "q_hit": [("q_hit", range(4), HIT, [50] * 4)],
        "e_shuriken": [("e_shuriken", range(4), (0, 0), [60] * 4)],
        "e_hit": [("e_hit", range(5), HIT, [50] * 5)],
        "e_mark": [("e_mark", range(4), OVERHEAD, [100] * 4)],
        "e2_hit": [("e2_hit", range(5), HIT, [50] * 5)],
        "r1_hit": [("r1_hit", range(5), HIT, [50] * 5)],
        "r2_hit": [("r2_hit", range(6), HIT, [60] * 6)],
    },
    "league_akali_big": {
        "q_fan": [("q_fan", range(6), (0, 0), [40, 40, 40, 40, 37, 36])],
        "w_smoke": [("w_smoke", SMOKE, GROUND, [111] * len(SMOKE))],
        "e_dash": [("e_dash", range(5), HERS, [60] * 5)],
        "r_dash": [("r_dash", range(6), HERS, [60] * 6)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "akali_fx_anchors.json")), encoding="utf-8") as f:
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

#!/usr/bin/env python3
"""Import Briar's effects (assets/source/briar/PROMPTS.md, 1-15) as game sheets.

    python tools/art/import_briar.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_briar.py                                   # native strips -> effect sheets

The body comes from tools/art/tidy_briar.py and tools/art/import_native.py. --raw turns every frame of Codex's raw
strips into a cell of a native strip the way tools/art/import_morgana.py does (every game pixel one flat 8x8 block,
binary alpha, 16 colours by median cut, each game pixel the majority colour of the source pixels it covers, opaque
when a third of them are, the anchor on the middle of a game pixel; a manifest.json with `assets[].frames[].rect`
gives the frames, else equal cells side by side). The flying gem is turned to its direction by the game, so it is
made exactly symmetric about its core's row. Writes assets/source/briar/briar_fx_<name>.png plus
briar_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel): the bite hit 16 px, Snack Attack's jaws 24, its
heal 30 tall round the hero, Head Rush's impact 24, the frenzy 44 and Hemomania 48 tall round a 46 px hero (her
pillory's gem at 46), the charge's shell 40, the scream's fan 50 long (its cone's radius 50000: the view is centred
on the line), its hit 16, the stun stars 18, the gem 20, the prey mark 14, the landing blast's ring 70 (radius
35000), its hit 18, the fear icon 16 tall.
Anchors, measured on each drawing: hits and bursts on their white core (or the drawing's middle once it has faded);
the auras on their ground ring's middle, the lowest drawn row on the ground line; the stars, the mark and the fear
icon on their own middle over the target's head; the gem on its core; the fan on the middle of its cell (the apex
at the left end); the blast on the middle of its ellipse.
The second step places every cell by its anchor and times each view by the kit: Head Rush's stars loop for the 0.5 s
stun after the impact, the scream's stars for the 1 s stun, the fear icon for 1.5 s; the auras loop (buff views).
No palette or outline pass on the sheets. Writes league/effects/league_briar_fx and league/effects/league_briar_big
(r_boom, e_wave).
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

SRC = os.path.join(ROOT, "assets", "source", "briar")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)                         # the ground under a unit (11 px under its pivot)
BODY = (0, -6)                         # the middle of a 35 px hero
HIT = (0, -8)                          # a hit on the upper body
HERS = (0, -12)                        # the middle of Briar (46 px with the pillory)
OVERHEAD = (0, -29)                    # over a 35 px hero's crown (the targets of the stun and the fear)

# raw strip -> native (see import_morgana.RAW for the measures and anchors)
RAW = {
    "hit": dict(n=5, size=16, measure="w", x="centre", y="centre"),
    "snack": dict(n=6, size=24, measure="w", x=("frame", [2, 3]), y=("frame", [2, 3])),
    "snack_heal": dict(n=5, size=30, measure="cellh", x="cell", y="cell"),
    "q_hit": dict(n=6, frames=[0, 1, 2, 3], size=24, measure="w", x=("core", [0, 1]), y=("core", [0, 1])),
    "q_stars": dict(src="q_hit", n=6, frames=[4, 5], size=18, measure="w", x=("frame", [4, 5]), y=("frame", [4, 5])),
    "frenzy": dict(n=4, size=44, measure="h", x=("frame", [0, 1, 2, 3]), y=("bottom", 0)),
    "hema": dict(n=4, size=48, measure="h", x=("frame", [0, 1, 2, 3]), y=("bottom", 0)),
    "e_guard": dict(n=4, size=40, measure="h", x=("frame", [0, 1, 2, 3]), y=("frame", [0, 1, 2, 3])),
    "e_wave": dict(n=5, size=50, measure="cellw", x="cell", y=("frame", [1, 2, 3])),
    "e_hit": dict(n=4, size=16, measure="w", x="centre", y="centre"),
    "e_stun": dict(n=4, size=18, measure="w", x=("frame", [0, 1, 2, 3]), y=("frame", [0, 1, 2, 3])),
    "r_gem": dict(n=4, size=20, measure="w", x=("core", None), y=("core", None), mirror=True),
    "r_mark": dict(n=4, size=14, measure="w", x=("frame", [1, 2]), y=("frame", [1, 2])),
    "r_boom": dict(n=7, size=70, measure="body", on=3, x="body", y="body"),
    "r_hit": dict(n=4, size=18, measure="w", x=("core", [1]), y=("core", [1])),
    "r_fear": dict(n=4, size=16, measure="h", x=("frame", [0, 1, 2, 3]), y=("frame", [0, 1, 2, 3])),
}


def extent(fr, spec, used, rects):
    if spec["measure"] == "cellw":
        return max(rects[k][2] for k in used)
    if spec["measure"] == "cellh":
        return max(rects[k][3] for k in used)
    on = spec.get("on")
    return fr.extent(spec["measure"], on) if on is not None else max(fr.extent(spec["measure"], k) for k in used)


def anchor(fr, how, k, axis, rects):
    if how == "cell":
        x, y, w, h = rects[k]
        return (x + w / 2) if axis == 0 else (y + h / 2)
    return fr.anchor(how, k, axis)


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "briar_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"briar_fx_{spec.get('src', name)}.png"
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
        used = spec.get("frames", list(range(spec["n"])))
        fr = Frames(a, solid, rects)
        mask = np.zeros(solid.shape, bool)
        for k in used:
            x, y, w, h = rects[k]
            mask[y:y + h, x:x + w] = True
        b = a.copy()
        b[~mask, 3] = 0
        own = np.unique(b[b[..., 3] >= 100][:, :3], axis=0)
        pal = own.astype(float) if len(own) <= 16 else palette(b)   # Codex's clean strips keep their own colours
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
            if spec.get("mirror"):
                cell = out[:, i * tw:(i + 1) * tw]
                cell[U + 1:] = cell[:U][::-1]
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"briar_fx_{name}.png")))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(used)}
        print(f"briar_fx_{name}.png  {len(used)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} "
              f"({spec['size']} px over {ext} source px), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"briar_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"briar_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# Head Rush's stars: the 0.5 s stun after the impact (the two star frames three times)
Q_STARS = [0, 1] * 3
# the scream's stun stars: 1 s (the four frames two and a half times)
E_STUN = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1]
# the fear icon: 1.5 s
FEAR = [0, 1, 2, 3] * 4

# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_briar_fx": {
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "snack": [("snack", range(6), HIT, [60] * 6)],
        "snack_heal": [("snack_heal", range(5), HERS, [80] * 5)],
        "q_hit": [("q_hit", range(4), BODY, [50] * 4), ("q_stars", Q_STARS, OVERHEAD, [50] * 6)],
        "frenzy": [("frenzy", range(4), FEET, [100] * 4)],
        "hema": [("hema", range(4), FEET, [100] * 4)],
        "e_guard": [("e_guard", range(4), HERS, [80] * 4)],
        "e_hit": [("e_hit", range(4), BODY, [50] * 4)],
        "e_stun": [("e_stun", E_STUN, OVERHEAD, [100] * 10)],
        "r_gem": [("r_gem", range(4), (0, 0), [60] * 4)],
        "r_mark": [("r_mark", range(4), (0, -31), [100] * 4)],
        "r_hit": [("r_hit", range(4), BODY, [50] * 4)],
        "r_fear": [("r_fear", FEAR, OVERHEAD, [94] * 16)],
    },
    "league_briar_big": {
        "e_wave": [("e_wave", range(5), (0, 0), [66, 66, 67, 67, 67])],
        "r_boom": [("r_boom", range(7), FEET, [70] * 7)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "briar_fx_anchors.json")), encoding="utf-8") as f:
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

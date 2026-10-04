#!/usr/bin/env python3
"""Import Sett's effects (assets/source/sett/PROMPTS_FX.md, 14 sheets) as the game sheets league_sett_fx and
league_sett_big.

    python tools/art/import_sett.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_sett.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/strips_sett.py builds the strips). --raw turns each frame of Codex's
drawings (its manifest.json: `assets[].frames[].rect` = [x, y, w, h]; the shield's three rows read appear, hold, go)
into a cell of a native strip (assets/source/sett/sett_fx_<name>.png, 8x, plus sett_fx_anchors.json) as
import_sivir.py does: each game pixel the majority colour of the source pixels it covers, opaque when a quarter of them
are solid, every colour snapped to the ramps the pack gave that effect (ORANGE, SILVER, HEAT, EARTH), then the ring
comes off the glows (an edge pixel in a ramp's darkest shade goes when two lighter neighbours hold the shape, else it
takes the next shade; the slam's rocks keep their dark edge). One scale per strip: `size` game px over the drawings'
widest (w) or larger side (m) - or over one frame's width (W's fist: its warning fan in frame 1 is the 50-square line).
Anchors (source pixels): the hits on their cell's middle (the pack asked for them centred); the shield on its full
shell's box (frame 4), the crater on its widest ring's box (frame 3), the heat on its ring (the lower part), the fist
glow on its first frame's box; W's fist 25 squares right of its fan's left end, on the fan's axis - the middle of the
50000 line its picture is laid on (champion-data "Cone / fan": centred on the line, pointing right).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot), measured on the action strips (tools/art/pack_sett_fx.py's sett_shots.png): E's clap in skill 6 (7, -11),
the idle's fists (+-10, -5: the glow's middle at (-1, -5)), the soles (the crater's and the heat's middle, (0, 10)), the
shield round his body (-1, -10), a hit on the upper body (0, -8) - and times it by the kit (60 ticks a second): W's fist
46 ticks with the fist in frame 5 on tick 27 (Codex's 7/7/7/6/4/4/4/4/3), the shield's 180 ticks held by its loop.
Writes league/effects/league_sett_fx and league_sett_big (W's fist, E's clap, R's crater).
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sett")
MOD = os.path.join(ROOT, "league")
Z = 8

RAMPS = {
    "ORANGE": ["B85712", "F59A1E", "FFCC4D", "FFF2C2", "FFFFFF"],
    "SILVER": ["626A82", "959CB0", "C9CEDB", "EEF1F6", "FFFFFF"],
    "HEAT": ["7A1E16", "C23A1E", "F2662A", "FFAA40", "FFE6A8"],
    "EARTH": ["3C2C22", "604834", "94704A", "CBA676", "F2DDB8"],
}
RIM = {"B85712": "F59A1E", "626A82": "959CB0", "7A1E16": "C23A1E"}      # the earth's dark edge stays (rocks)

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=12, measure="m", anchor="cell", ramps="ORANGE"),
    "a2_hit": dict(n=5, size=16, measure="m", anchor="cell", ramps="ORANGE"),
    "q_glow": dict(n=4, size=30, measure="w", anchor=("fixed", "box", 0), ramps="ORANGE"),
    "q_hit": dict(n=5, size=22, measure="m", anchor="cell", ramps="ORANGE"),
    "e_hit": dict(n=4, size=14, measure="m", anchor="cell", ramps="ORANGE"),
    "e_smash": dict(n=5, size=26, measure="w", anchor="cell", ramps="ORANGE"),
    "w_fist": dict(n=9, size=50, measure=("frame", 0, "w"), anchor="fan", ramps="ORANGE"),
    "w_shield": dict(n=12, size=44, measure="w", anchor=("fixed", "box", 3), ramps="SILVER ORANGE"),
    "w_true": dict(n=5, size=20, measure="m", anchor="cell", ramps="ORANGE"),
    "w_hit": dict(n=4, size=14, measure="m", anchor="cell", ramps="ORANGE EARTH"),
    "r_grab": dict(n=4, size=18, measure="m", anchor="cell", ramps="ORANGE"),
    "r_slam": dict(n=6, size=64, measure="w", anchor=("fixed", "box", 2), ramps="HEAT EARTH"),
    "r_hit": dict(n=4, size=14, measure="m", anchor="cell", ramps="ORANGE EARTH"),
    "grit": dict(n=6, size=32, measure="w", anchor=("fixed", "ring", 0), ramps="HEAT"),
}
W_LINE = 50                       # W's line, squares (sett_kit.W_LENGTH 50000): the fan's anchor is its middle


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def unrim(a):
    J.RIM = RIM
    return J.unrim(a)


def box(solid, rect):
    x, y, w, h = rect
    ys, xs = np.nonzero(solid[y:y + h, x:x + w])
    return x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1


def anchor(how, k, a, solid, rects, s=None):
    """(x, y) of frame k's anchor in the source: import_jhin's, plus `box` (the middle of the drawing's box) and `fan`
    (W's line middle: W_LINE / 2 squares right of frame 1's left end, on its box's middle row, in every frame)."""
    if how == "box":
        x0, x1, y0, y1 = box(solid, rects[k])
        return (x0 + x1) / 2, (y0 + y1) / 2
    if how == "fan":
        x0, x1, y0, y1 = box(solid, rects[0])
        return rects[k][0] + (x0 - rects[0][0]) + W_LINE / 2 / s, rects[k][1] + (y0 + y1) / 2 - rects[0][1]
    if isinstance(how, tuple) and how[0] == "fixed":
        x, y, _, _ = rects[k]
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects, s)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    return J.anchor(how, k, a, solid, rects)


def from_raw(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    os.makedirs(os.path.join(SRC, "codex_fx"), exist_ok=True)
    for name in ("HANDOFF.md", "manifest.json", "generation_prompts.json"):
        shutil.copy(os.path.join(folder, name), os.path.join(SRC, "codex_fx", name))
    anchors = {}
    for name, spec in RAW.items():
        fn = f"sett_fx_{name}.png"
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(os.path.join(folder, fn)).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        idx = J.snap(a, solid, pal)
        boxes = [box(solid, r) for r in rects]
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        m = spec["measure"]
        over = boxes[m[1]][1] - boxes[m[1]][0] if isinstance(m, tuple) else ext[m]
        s = spec["size"] / over
        anc = [anchor(spec["anchor"], k, a, solid, rects, s) for k in range(len(rects))]
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
                    msk = solid[sy0:sy1, sx0:sx1]
                    if msk.mean() < 1 / 4:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][msk], minlength=len(pal)).argmax()
                    cell[r, c, :3] = pal[col]
                    cell[r, c, 3] = 255
            out[:, i * tw:(i + 1) * tw] = unrim(cell)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(os.path.join(SRC, fn))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{over}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(os.path.join(SRC, "sett_fx_anchors.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(os.path.join(SRC, f"sett_fx_{name}.png")).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"sett_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (pack_sett_fx.py's sett_shots.png)
CLAP = (7, -11)             # his fists meeting in front of his chest in skill 6 (E's tick 18)
FISTS = (-1, -5)            # the middle of the idle's fists (-11, -6) and (9, -5): the glow's two flames
SHELL = (-1, -10)           # the shield round his body (his crown -31, his soles 11)
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
FEET = (0, 10)              # a ring or a crater on the ground round his feet (its middle a row over the soles)


def ms(ticks):
    return [round(t * 1000 / 60) for t in ticks]


seq = J.seq
FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "a2_hit": [("a2_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 90]), [HIT])],
    "q_glow": [("q_glow", seq(range(4), [100] * 4), [FISTS])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_true": [("w_true", seq(range(5), [40, 50, 60, 70, 90]), [HIT])],
    "r_grab": [("r_grab", seq(range(4), [40, 50, 60, 80]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 80]), [HIT])],
    "w_pre": [("w_shield", seq(range(4), [40, 50, 50, 60]), [SHELL])],
    "w_loop": [("w_shield", seq(range(4, 8), [100] * 4), [SHELL])],
    "w_remove": [("w_shield", seq(range(8, 12), [50, 60, 70, 80]), [SHELL])],
    "grit": [("grit", seq(range(6), [100] * 6), [FEET])],
}
BIG = {
    # the line's picture: 46 ticks, the fist in frame 5 on tick 27 (sett_kit W_VIEW_TICKS, W_APPLY)
    "w_fist": [("w_fist", seq(range(9), ms([7, 7, 7, 6, 4, 4, 4, 4, 3])), [(0, 0)])],
    "e_smash": [("e_smash", seq(range(5), [40, 50, 60, 70, 90]), [CLAP])],
    "r_slam": [("r_slam", seq(range(6), [70, 100, 120, 130, 140, 140]), [FEET])],
}


def build(table):
    with open(os.path.join(SRC, "sett_fx_anchors.json"), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, t in frames:
                out[tag].append((J.place(strip[k], anchors[src]["anchor"], spots), t))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_sett_fx", FX), ("league_sett_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

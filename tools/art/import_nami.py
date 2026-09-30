#!/usr/bin/env python3
"""Import Nami's effects (assets/source/nami/PROMPTS.md, 1-13) as game sheets.

    python tools/art/import_nami.py --raw <Codex's delivery folder>   # once: Codex's strips -> native strips
    python tools/art/import_nami.py                                   # native strips -> effect sheets

The body comes from tools/art/tidy_nami.py and tools/art/import_native.py. Codex delivered every effect three ways
(nami_fx_generated): its generated drawing (raw_generated/), that drawing snapped by Codex to a grid of 8x8 blocks in
the layout asked for (nami_fx_<name>.png, 7-10 colours, alpha 0 or 255) and the same at one pixel a block (1x/).
The grid is cell / 8, so most effects came out near the size the prompts asked for and are taken as Codex drew them
(NATIVE: every block one game pixel, no resampling). The ones that must match the kit are resampled: each game pixel
the majority colour of the source pixels it covers, opaque when a third of them are, Codex's own colours only -
the bolt's hit and the stream's hit to the other heroes' hits (18 and 20 px; Codex's were 27), Aqua Prison's landing
ring to its radius (22000: 44 px wide), and the tidal wave to its radius (32000: 64 px tall) from the generated
drawing, as Codex's grid had it 46 px tall. The flying bolt, stream and wave are made exactly symmetric about the
middle row (the game turns them to their direction; Codex's grids of the bolt and the stream already are). Writes assets/source/nami/nami_fx_<name>.png plus
nami_fx_anchors.json.
Anchors: the flying effects on their cell's middle row, the bolt and the stream on the white-hot head (their core);
hits on their core; the auras (heal, blessing) and the prison on their cell's middle, which Codex left as the
figure's middle; the landing ring on its middle; the burst, the wave hit and the haste swirl on their lowest drawn
row (the ground).
The second step places every cell by its anchor and times each view by the kit: the landing ring lasts the bubble's
0.4 s flight, the prison the 1.25 s the target floats. Writes league/effects/league_nami_fx and
league/effects/league_nami_big (r_wave).
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

SRC = os.path.join(ROOT, "assets", "source", "nami")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)                         # the ground under a unit (11 px under its pivot)
BODY = (0, -6)                         # the middle of a 35 px hero
HIT = (0, -8)                          # a hit on the upper body

# name: frames, and either native=True (Codex's grid as it is) or size (px) along measure ("w"/"h") resampled from
# Codex's strip (or, raw=True, from its generated drawing); anchor: "core", "cell" or "low" (x on the cell's middle,
# y on the lowest drawn row over all frames); fly: the anchor on the cell's middle row (the game turns a flying
# picture about it); mirror: made symmetric about that row (Codex's own grids already are)
RAW = {
    "bolt": dict(n=4, native=True, anchor="core", fly=True),
    "hit": dict(n=5, size=18, measure="w", anchor="core"),
    "w_stream": dict(n=4, native=True, anchor="core", fly=True),
    "w_hit": dict(n=5, size=20, measure="w", anchor="core"),
    "w_heal": dict(n=5, native=True, anchor="cell"),
    "e_blessing": dict(n=4, native=True, anchor="cell"),
    "q_bubble": dict(n=4, native=True, anchor="cell"),
    "q_mark": dict(n=4, size=44, measure="w", anchor="cell"),
    "q_burst": dict(n=6, native=True, anchor="low"),
    "q_prison": dict(n=8, native=True, anchor="cell"),
    "r_wave": dict(n=4, size=64, measure="h", raw=True, anchor="cell", fly=True, mirror=True),
    "r_hit": dict(n=5, native=True, anchor="low"),
    "p_haste": dict(n=4, native=True, anchor="low"),
}


def load_manifest(folder):
    path = os.path.join(folder, "manifest.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8-sig") as f:
        return {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}


def hexrgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def source(folder, name, spec, manifest):
    """(RGBA source, solid mask, frame rects, palette, pixels per game pixel at Codex's grid)."""
    fn = f"nami_fx_{name}.png"
    info = manifest.get(fn, {})
    grid = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA"))
    n = spec["n"]
    if info.get("frames"):
        rects = [list(f["rect"]) for f in info["frames"]]
    else:
        W = grid.shape[1]
        rects = [[k * W // n, 0, W // n, grid.shape[0]] for k in range(n)]
    pal = np.array([hexrgb(c) for c in info["palette"]], float) if info.get("palette") else \
        np.unique(grid[grid[..., 3] > 0][:, :3], axis=0).astype(float)
    if not spec.get("raw"):
        return grid, grid[..., 3] > 0, rects, pal, Z
    raw = np.asarray(Image.open(G.lp(os.path.join(folder, "raw_generated", fn))).convert("RGBA"))
    k = raw.shape[1] / grid.shape[1]                      # the drawing's cells line up with the grid's, scaled
    rrects = [[int(round(x * k)), int(round(y * k)), int(round(w * k)), int(round(h * k))] for x, y, w, h in rects]
    return raw, raw[..., 3] >= 100, rrects, pal, None


def boxes(solid, rects):
    out = []
    for x, y, w, h in rects:
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        out.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1) if len(xs) else None)
    return out


def anchors_of(a, solid, rects, spec, box):
    """Per frame (ax, ay) in source pixels."""
    how = spec["anchor"]
    if how == "cell":
        return [(x + w / 2, y + h / 2) for x, y, w, h in rects]
    if how == "low":
        low = max(b[3] - r[1] for b, r in zip(box, rects) if b)
        return [(x + w / 2, y + low - 0.5) for x, y, w, h in rects]
    # core: the white-hot pixels' middle, averaged over the frames that have some (else the box's middle)
    white = solid & (a[..., :3].min(-1) >= 225)
    offs = []
    for (x, y, w, h), b in zip(rects, box):
        wy, wx = np.nonzero(white[y:y + h, x:x + w])
        if len(wx) >= 3:
            offs.append((wx.mean() + 0.5, wy.mean() + 0.5))
        elif b:
            offs.append(((b[0] + b[1]) / 2 - x, (b[2] + b[3]) / 2 - y))
    ox, oy = np.mean([o[0] for o in offs]), np.mean([o[1] for o in offs])
    if spec.get("fly"):
        oy = rects[0][3] / 2                               # the flying ones sit on their cell's middle row
    return [(x + ox, y + oy) for x, y, w, h in rects]


def resample(a, solid, rects, pal, spec, box, anc, s):
    idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
    L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, box) if b) * s - 0.5), 0) + 1
    U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, box) if b) * s - 0.5), 0) + 1
    tw, th = 2 * L + 1, 2 * U + 1
    out = np.zeros((th, tw * len(rects), 4), np.uint8)
    for i, ((x, y, w, h), (ax, ay)) in enumerate(zip(rects, anc)):
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
    return out, tw, th, L, U


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "nami_fx_anchors.json")
    anchors = {}
    if os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        a, solid, rects, pal, grid = source(folder, name, spec, manifest)
        box = boxes(solid, rects)
        anc = anchors_of(a, solid, rects, spec, box)
        if spec.get("native"):
            s = 1 / grid
            anc = [(math.floor(ax / grid) * grid + grid / 2, math.floor(ay / grid) * grid + grid / 2) for ax, ay in anc]
            ext = None
        else:
            k = 0 if spec["measure"] == "w" else 2
            ext = max(b[k + 1] - b[k] for b in box if b)
            s = spec["size"] / ext
        out, tw, th, L, U = resample(a, solid, rects, pal, spec, box, anc, s)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"nami_fx_{name}.png")))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        how = "native" if ext is None else f"{spec['size']} px over {ext} source px"
        print(f"nami_fx_{name}.png  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, {how}, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"nami_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"nami_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_nami_fx": {
        "bolt": [("bolt", range(4), (0, 0), [60] * 4)],
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "w_stream": [("w_stream", range(4), (0, 0), [60] * 4)],
        "w_hit": [("w_hit", range(5), HIT, [60] * 5)],
        "w_heal": [("w_heal", range(5), BODY, [80] * 5)],
        "e_blessing": [("e_blessing", range(4), BODY, [100] * 4)],
        "q_bubble": [("q_bubble", range(4), (0, 0), [80] * 4)],
        "q_mark": [("q_mark", range(4), FEET, [100] * 4)],                 # the bubble's 0.4 s flight
        "q_burst": [("q_burst", range(6), FEET, [60] * 6)],
        "q_prison": [("q_prison", range(8), BODY, [100, 120, 160, 160, 160, 160, 190, 200])],   # 1.25 s afloat
        "r_hit": [("r_hit", range(5), FEET, [70] * 5)],
        "p_haste": [("p_haste", range(4), FEET, [90] * 4)],
    },
    "league_nami_big": {
        "r_wave": [("r_wave", range(4), (0, 0), [80] * 4)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "nami_fx_anchors.json")), encoding="utf-8") as f:
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
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from it first")
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

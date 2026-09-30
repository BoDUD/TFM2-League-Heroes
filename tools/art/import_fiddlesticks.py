#!/usr/bin/env python3
"""Import Fiddlesticks' effects (assets/source/fiddlesticks/PROMPTS.md, 1-14) as game sheets.

    python tools/art/import_fiddlesticks.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_fiddlesticks.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py (his sack head is drawn and
pasted). Codex's thirteen strips came back as raw image-generator output with real alpha (1774-2172 px wide
canvases) and a manifest.json (schema fiddlesticks_raw_handoff_v1) giving every frame's rectangle in the source
(`assets[].frame_regions[]`, {index, x, y, w, h}, one band of rows per strip). --raw turns every frame into a cell
of a native strip the way tools/art/import_thresh.py does (every game pixel one flat 8x8 block, binary alpha, 16
colours by median cut, each game pixel the majority colour of the source pixels it covers, opaque when a third of
them are, the anchor on the middle of a game pixel). A frame takes the connected drawings that lie mostly in its
rectangle, wherever they reach (own()): in the crows' flight two birds cross into the next frame's rectangle, and
cutting by the rectangles left half a crow on one side and a wing tip on the other. The pictures the game turns
to their direction (the bolt, the crow, Reap's crescent) are made exactly symmetric about their middle row (the
upper half mirrored down), as the handoff asked. Writes assets/source/fiddlesticks/fiddlesticks_fx_<name>.png
plus fiddlesticks_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the bolt 14 px
long with its smoke, its hit 16 px; the crow's wings 22 px across, the screaming ghost 30 px tall; the fear eye
16 px with its circling crow, the stitched mouth 17 px (three 3 px stitches); the soul pulled out of a drained
foe 26 px tall and the final harvest 32 px; Reap's crescent 48 px tall (a slash through the foes in its
30000-radius circle, taller than a hero and short of the circle's 60 px, which stood like a wall); the souls
round the channel 44 px wide; Crowstorm's landing mark 90 px wide (radius 45000, squeezed to 2:1), the smoke
column he dissolves into 44 px (his 40 px and a little), the storm 84 px wide (the crows' ellipse round the
45000 radius) and squeezed to 0.8 of its height (Codex's cell came square, not 3:2; unsqueezed the crows rose
90 px).

The second step places every cell by its anchor: the bolt and the crow ride their projectiles with their nose a
few pixels ahead, the crescent with its middle on the cast point; the hit, the ghost's burst, the drained soul's
root and the harvest's flash on the body; the fear eye and the stitched mouth over the head; the souls' ground
ring, the smoke column's foot and the storm's ring on his feet (caster views); the landing mark's ellipse on the
ground where he will land. The fear eye plays its six frames twice (1.2 s, the 1.25 s fear), the mouth its four
three times (1.25 s, the silence). No palette or outline pass on the sheets.
The soul chain (14, added after players missed League's tethers on the drain) came later and at game size: Codex's
1x strip (codex_fx_chain/, four 24 x 8 cells, anchored on their middle) is used as it came, so --raw leaves it be.
Writes league/effects/league_fiddlesticks_fx (bolt, hit, q_crow, q_hit, fear, silence, w_drain, w_final, w_chain)
and league/effects/league_fiddlesticks_big (e_reap, w_souls, r_mark, r_depart, r_storm).
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
from import_leona import palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "fiddlesticks")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
HIT = (0, -8)                          # a hit on the upper body
CHEST = (0, -6)
OVER = (0, -29)                        # over the head

# raw strip -> native: name: dict(n frames, size in game px, measure "w" (widest drawing) or "h" (tallest),
#   x anchor, y anchor, mirror, sy (the vertical scale against the horizontal))
#   x: "cell" the middle of the frame's rectangle; ("nose", px) the drawing's right edge plus px game pixels;
#      ("frame", k) the middle of frame k's drawing, at the same place in every rectangle; ("col", c) source column
#      c of every rectangle
#   y: "strip" the middle of all the strip's drawings; ("frame", k) the middle of frame k's drawing; ("row", r)
#      source row r (the bands are equal)
RAW = {
    "bolt": dict(n=4, size=14, measure="w", x=("nose", -3), y="strip", mirror=True),
    "hit": dict(n=5, size=16, measure="w", x=("frame", 0), y=("frame", 0)),
    "q_crow": dict(n=4, size=22, measure="h", x=("nose", -5), y="strip", mirror=True),
    "q_hit": dict(n=6, size=30, measure="h", x=("col", 188), y=("row", 512)),        # the crow's red burst
    "fear": dict(n=6, size=16, measure="w", x=("col", 180), y=("row", 380)),         # the eye's middle
    "silence": dict(n=4, size=17, measure="w", x="cell", y=("row", 341)),
    "w_drain": dict(n=4, size=26, measure="h", x=("col", 230), y=("row", 745)),      # the soul's root
    "w_final": dict(n=6, size=32, measure="h", x=("col", 193), y=("row", 486)),      # the flash
    "e_reap": dict(n=6, size=48, measure="h", x="cell", y="strip", mirror=True),
    "w_souls": dict(n=4, size=44, measure="w", x=("col", 248), y=("row", 612)),      # the ground ring's middle
    "r_mark": dict(n=8, size=90, measure="w", x=("col", 135), y=("row", 359), sy=0.95),
    "r_depart": dict(n=6, size=44 / 508, x=("col", 166), y=("row", 649)),            # the column 508 px, its foot
    "r_storm": dict(n=6, size=84, measure="w", x=("col", 172), y=("row", 500), sy=0.8),  # the ring's middle
    # 14, the soul chain (codex_fx_chain/): Codex drew it at game size, 24 x 8 a frame - its 1x strip as it came
    "w_chain": dict(n=4, native=True),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8-sig") as f:
        return {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}


def rects_of(asset):
    frames = sorted(asset.get("frame_regions") or asset.get("frames"), key=lambda f: f.get("index", 0))
    out = []
    for fr in frames:
        r = fr.get("rect", fr.get("source_rect", fr))
        out.append([int(r["x"]), int(r["y"]), int(r.get("w", r.get("width"))), int(r.get("h", r.get("height")))])
    return out


def own(solid, rects):
    """Each frame's pixels: the connected drawings (8-connected, alpha >= 100) with most of their pixels in its
    rectangle, in the strip's band of rows."""
    y0 = min(r[1] for r in rects)
    y1 = max(r[1] + r[3] for r in rects)
    band = solid[y0:y1]
    lab, count = G.label(band)
    cols = np.arange(band.shape[1])
    which = np.full(band.shape[1], -1)
    for k, (x, y, w, h) in enumerate(rects):
        which[(cols >= x) & (cols < x + w)] = k
    home = np.full(count + 1, -1)
    ys, xs = np.nonzero(lab)
    labs = lab[ys, xs]
    frame = which[xs]
    for c in range(1, count + 1):
        f = frame[labs == c]
        f = f[f >= 0]
        if len(f):
            home[c] = np.bincount(f).argmax()
    out = []
    for k in range(len(rects)):
        m = np.zeros_like(solid)
        m[y0:y1] = (lab > 0) & (home[lab] == k)
        out.append(m)
    return out


def x_anchor(how, k, rects, boxes, s):
    x, y, w, h = rects[k]
    if how == "cell":
        return x + w / 2
    kind, arg = how
    if kind == "nose":
        return boxes[k][1] + arg / s
    if kind == "frame":
        return x + ((boxes[arg][0] + boxes[arg][1]) / 2 - rects[arg][0])
    if kind == "col":
        return x + arg
    raise ValueError(how)


def y_anchor(how, k, rects, boxes):
    x, y, w, h = rects[k]
    if how == "strip":
        return (min(b[2] for b in boxes) + max(b[3] for b in boxes)) / 2
    kind, arg = how
    if kind == "frame":
        return y + ((boxes[arg][2] + boxes[arg][3]) / 2 - rects[arg][1])
    if kind == "row":
        return arg
    raise ValueError(how)


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "fiddlesticks_fx_anchors.json")
    anchors = {}
    if os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if (only and name not in only) or spec.get("native"):
            continue
        n = spec["n"]
        fn = f"fiddlesticks_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        rects = rects_of(manifest[fn])
        if len(rects) != n:
            sys.exit(f"{fn}: the manifest lists {len(rects)} frames, not {n}")
        mine = own(solid, rects)
        boxes = []
        for m in mine:
            ys, xs = np.nonzero(m)
            boxes.append((xs.min(), xs.max() + 1, ys.min(), ys.max() + 1))
        if isinstance(spec["size"], float) and spec["size"] < 1:
            s, extent = spec["size"], None
        else:
            ext = (lambda b: b[1] - b[0]) if spec["measure"] == "w" else (lambda b: b[3] - b[2])
            extent = max(ext(b) for b in boxes)
            s = spec["size"] / extent
        sv = s * spec.get("sy", 1.0)
        anchor = [(x_anchor(spec["x"], k, rects, boxes, s), y_anchor(spec["y"], k, rects, boxes)) for k in range(n)]
        # the anchor is the middle of pixel (L, U); the cell is 2L+1 x 2U+1
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for b, (ax, _) in zip(boxes, anchor)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for b, (_, ay) in zip(boxes, anchor)) * sv - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * n, 4), np.uint8)
        H, W = solid.shape
        for k, (ax, ay) in enumerate(anchor):
            m = mine[k]
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / sv))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / sv)), sy0 + 1)
                sy0, sy1 = max(0, sy0), min(H, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(0, sx0), min(W, sx1)
                    if sx1 <= sx0:
                        continue
                    mm = m[sy0:sy1, sx0:sx1]
                    if mm.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][mm], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
            if spec.get("mirror"):
                cell = out[:, k * tw:(k + 1) * tw]
                cell[U + 1:] = cell[:U][::-1]
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U]}
        how = f"{spec['size']} px over {extent} source px" if extent else f"{s:.4f} a source px"
        print(f"{fn}  {n} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({how}), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"fiddlesticks_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"fiddlesticks_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# sprite: {tag: (strip, its frames used, spot of the anchor from the pivot, ms per frame)}
FX = {
    "league_fiddlesticks_fx": {
        "bolt": ("bolt", range(4), (0, 0), [60] * 4),
        "hit": ("hit", range(5), HIT, [50] * 5),
        "q_crow": ("q_crow", range(4), (0, 0), [60] * 4),
        "q_hit": ("q_hit", range(6), CHEST, [60] * 6),
        "fear": ("fear", list(range(6)) * 2, OVER, [100] * 12),
        "silence": ("silence", list(range(4)) * 3, (0, -27), [104] * 12),
        "w_drain": ("w_drain", range(4), CHEST, [62] * 4),
        "w_final": ("w_final", range(6), CHEST, [60] * 6),
        "w_chain": ("w_chain", range(4), (0, 0), [60] * 4),       # rides its projectile, turned to its way
    },
    "league_fiddlesticks_big": {
        "e_reap": ("e_reap", range(6), (0, 0), [66] * 6),          # turned half round when cast left
        "w_souls": ("w_souls", range(4), FEET, [62] * 4),
        "r_mark": ("r_mark", range(8), FEET, [125] * 8),
        "r_depart": ("r_depart", range(6), FEET, [70] * 6),
        "r_storm": ("r_storm", range(6), FEET, [83] * 6),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "fiddlesticks_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (src, used, (sx, sy), ms) in tags.items():
            ax, ay = anchors[src]["anchor"]
            strip = cells(src, RAW[src]["n"])
            out[tag] = [(G.centre_frame(strip[k], sx - ax, sy - ay), m) for k, m in zip(used, ms)]
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--only", nargs="+", help="with --raw: just these strips (e.g. bolt r_storm)")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

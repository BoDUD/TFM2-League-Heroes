#!/usr/bin/env python3
"""Import Lucian's effects (assets/source/lucian/PROMPTS.md, 1-14) as a game sheet.

    python tools/art/import_lucian.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_lucian.py                                   # native strips -> the effect sheet

The body (model and strips) is Codex's too (assets/source/lucian/MODEL_PROMPTS.md, imported by
tools/art/import_native.py). The effects come back as raw image-generator output with a manifest.json giving
every frame's rectangle in the source (`assets[].frame_regions[]` or `frames[]`, {x, y, w, h}); --raw turns every
frame into a cell of a native strip the way tools/art/import_fiddlesticks.py does (its helpers are reused: every
game pixel one flat 8x8 block, binary alpha, 16 colours by median cut, a frame takes the connected drawings that lie
mostly in its rectangle). The pictures the game turns to their direction (the bullets, the beam, Ardent Blaze's
bolt, The Culling's bullets) are made exactly symmetric about their middle row. Writes
assets/source/lucian/lucian_fx_<name>.png plus lucian_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the attack's bullet
12 px long (Codex's gold second bullet, 14 px, is kept but unused); the Culling's hits 16 px. tracer() draws the
Culling's bullet (the user found Codex's too small at 16 and 10 px; League's are long bright tracers) and the double
shot's two (the user saw no double shot: both flew small on one line), blue then gold; Piercing Light's beam 80 px,
from his muzzle 21 px ahead to the end of the 100000-long line (Q_RAY);
Ardent Blaze's bolt 14 px, its star cross 52 px wide (the 20000 burst radius and the star's long arms), the mark
under a marked foe 22 px; the dash's burst 32 px; the other hits 14-24 px; the Vigilance sparks 26 px across his
hands, the haste lines 24 px at his feet.

The second step places every cell by its anchor: the bullets, the bolt and the beam ride their projectiles (the
bullets' noses a little ahead; the beam's carrier stands raised to the muzzle, so its picture starts 21 px ahead of
it); the hits on the upper body; the dash's ring, the star cross, the mark and the haste lines on the feet (a
picture on a point or on a unit is drawn at its pivot, 11 px above the soles). Writes
league/effects/league_lucian_fx.
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
from import_fiddlesticks import load_manifest, own, x_anchor, y_anchor  # noqa: E402
from import_leona import palette as median_palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "lucian")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
HIT = (0, -8)                          # a hit on the upper body
CHEST = (0, -6)
HANDS = (0, -10)                       # his hands, the pistols in them
# Piercing Light's picture rides q_ray, a TargetProjectile creeping 1 px a tick from his pivot at the target, its
# picture lifted to the muzzle (the kit): one frame a tick, each drawing the beam 1 px further back, so it stands from
# the muzzle, 21 px ahead of where the carrier started, for the line's length; then one empty frame until the carrier
# reaches the target. Codex's frames 0-1 (a spark, the beam coming on) are left out - his own frame 4 flashes at the
# muzzle - so the full beam (2) shows at once for 5 ticks, then thins (3) and fades (4-5); the hit comes at the end
# of the full glow (the kit's apply 7), so a target it kills, which takes the carrier along, still had the beam
RAY_AHEAD, RAY_LEN, RAY_SPEED = 21, 80, 1
RAY_FRAMES = [2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5]
RAY_AFTER = 2000                       # ms of nothing: the carrier creeps on to the target (70000 at 1000 a tick: 1.2 s)
Q_RAY = [(f, (RAY_AHEAD + RAY_LEN // 2 - RAY_SPEED * i, 0), 1000 / 60) for i, f in enumerate(RAY_FRAMES)]

# raw strip -> native (keys as in tools/art/import_fiddlesticks.py RAW; x / y "pivot": the frame's pivot in Codex's
# manifest - the middle of a hit, the feet of a burst drawn round a figure, the middle line of a flying picture)
RAW = {
    "bullet": dict(n=4, size=12, measure="w", x=("nose", -2), y="pivot", mirror=True),
    "bullet2": dict(n=4, size=14, measure="w", x=("nose", -2), y="pivot", mirror=True),     # unused: ls_shot2
    "hit": dict(n=5, size=14, measure="w", x="pivot", y="pivot"),
    "vig_hit": dict(n=5, size=18, measure="w", x="pivot", y="pivot"),
    "vig_glow": dict(n=4, size=26, measure="w", x="pivot", y="pivot"),
    "q_beam": dict(n=6, size=80, measure="w", x="pivot", y="pivot", mirror=True),     # muzzle to the line's end
    "q_hit": dict(n=5, size=24, measure="h", x="pivot", y="pivot"),
    "e_dash": dict(n=6, size=32, measure="w", x="pivot", y="pivot"),                   # the pivot is his feet
    "w_bolt": dict(n=4, size=14, measure="w", x=("nose", -2), y="pivot", mirror=True),
    "w_burst": dict(n=7, size=52, measure="w", x="pivot", y="pivot"),
    "w_mark": dict(n=4, size=22, measure="w", x="pivot", y="pivot"),
    "w_haste": dict(n=4, size=24, measure="w", x="pivot", y="pivot"),                  # the pivot is his feet
    "r_hit": dict(n=3, size=16, measure="w", x="pivot", y="pivot"),
}

# The Culling's bullet is drawn here (tracer()), not taken from Codex: its drawing was a bar two pixels high, and
# scaled to League's long bright tracer it stayed a thin stick. Piercing Light's five blues (Codex's) over a
# profile: (row from the middle, first and last pixel behind the nose, colour) per frame; mirrored below.
BEAM = {"deep": (16, 42, 140), "dark": (31, 79, 216), "blue": (79, 139, 255), "light": (168, 204, 255),
        "white": (244, 250, 255)}
TRACER = [
    [(0, 0, 9, "white"), (0, 10, 17, "light"), (0, 18, 23, "blue"), (0, 24, 27, "dark"),
     (1, 1, 8, "light"), (1, 9, 16, "blue"), (1, 17, 21, "dark"),
     (2, 2, 6, "blue"), (2, 7, 12, "dark"), (2, 13, 15, "deep"),
     (3, 3, 5, "dark"), (3, 6, 8, "deep")],
    [(0, 0, 11, "white"), (0, 12, 18, "light"), (0, 19, 24, "blue"), (0, 25, 27, "dark"),
     (1, 1, 9, "light"), (1, 10, 17, "blue"), (1, 18, 22, "dark"),
     (2, 2, 7, "blue"), (2, 8, 13, "dark"), (2, 14, 16, "deep")],
    [(0, 0, 9, "white"), (0, 10, 17, "light"), (0, 18, 23, "blue"), (0, 24, 27, "dark"),
     (1, 1, 8, "light"), (1, 9, 16, "blue"), (1, 17, 21, "dark"),
     (2, 2, 8, "blue"), (2, 9, 13, "dark"), (2, 14, 16, "deep"),
     (3, 3, 4, "blue"), (3, 5, 9, "deep")],
]
TRACER_LEN, TRACER_H = 28, 3                     # px behind the nose (0-27); rows above and below the middle

# Lightslinger's two shots, drawn the same way so they show (the user could not see the double shot): a 22 px tracer
# 5 px thick, the first in the beam's blues from the raised pistol, the second in gold from the lower one
SHOT = [
    [(0, 0, 7, "white"), (0, 8, 13, "light"), (0, 14, 18, "blue"), (0, 19, 21, "dark"),
     (1, 1, 6, "light"), (1, 7, 12, "blue"), (1, 13, 16, "dark"),
     (2, 2, 5, "blue"), (2, 6, 9, "dark"), (2, 10, 11, "deep")],
    [(0, 0, 9, "white"), (0, 10, 14, "light"), (0, 15, 19, "blue"), (0, 20, 21, "dark"),
     (1, 1, 7, "light"), (1, 8, 13, "blue"), (1, 14, 17, "dark"),
     (2, 2, 4, "blue"), (2, 5, 9, "dark")],
    [(0, 0, 7, "white"), (0, 8, 13, "light"), (0, 14, 18, "blue"), (0, 19, 21, "dark"),
     (1, 1, 6, "light"), (1, 7, 12, "blue"), (1, 13, 16, "dark"),
     (2, 2, 6, "blue"), (2, 7, 10, "dark"), (2, 11, 12, "deep")],
]
GOLD_BEAM = {"deep": (110, 76, 24), "dark": (138, 100, 32), "blue": (200, 150, 46), "light": (240, 200, 90),
             "white": (255, 246, 214)}
DRAWN_SPEC = {"r_bullet": (TRACER, TRACER_LEN, TRACER_H, BEAM),
              "ls_shot": (SHOT, 22, 2, BEAM), "ls_shot2": (SHOT, 22, 2, GOLD_BEAM)}
DRAWN = {k: len(v[0]) for k, v in DRAWN_SPEC.items()}     # strips made here, not from Codex's raw: their cells


def tracer():
    """The drawn bullets: tracers thick at the head, thinning to the tail; the nose at the anchor."""
    path = os.path.join(SRC, "lucian_fx_anchors.json")
    with open(G.lp(path), encoding="utf-8") as f:
        anchors = json.load(f)
    for name, (rows_by_frame, length, half, pal) in DRAWN_SPEC.items():
        L, U = length, half + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rows_by_frame), 4), np.uint8)
        for k, rows in enumerate(rows_by_frame):
            for dy, x0, x1, col in rows:
                for y in {U - dy, U + dy}:
                    out[y, k * tw + L - x1:k * tw + L - x0 + 1, :3] = pal[col]
                    out[y, k * tw + L - x1:k * tw + L - x0 + 1, 3] = 255
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"lucian_fx_{name}.png")))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U]}
    write_anchors(anchors)


def write_anchors(anchors):
    order = list(RAW)[:list(RAW).index("r_hit")] + ["r_bullet", "r_hit", "ls_shot", "ls_shot2"]
    anchors = {k: anchors[k] for k in order if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "lucian_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def palette(a):
    """The strip's own colours when it has 16 or fewer (Codex's cleaned strips), else a 16-colour median cut."""
    cols = np.unique(a[a[..., 3] >= 100][:, :3], axis=0)
    return cols.astype(float) if len(cols) <= 16 else median_palette(a)


def rects_of(asset):
    """Every frame's rectangle [x, y, w, h] (a list, or a dict with x/y/w/h) and its pivot in the sheet (Codex's
    manifest gives it per frame, local to the rectangle)."""
    frames = sorted(asset.get("frame_regions") or asset.get("frames"), key=lambda f: f.get("index", 0))
    rects, pivots = [], []
    for fr in frames:
        r = fr.get("rect", fr.get("source_rect", fr))
        r = [r["x"], r["y"], r.get("w", r.get("width")), r.get("h", r.get("height"))] if isinstance(r, dict) else r
        rects.append([int(v) for v in r])
        pv = fr.get("pivot")
        pivots.append((r[0] + pv[0], r[1] + pv[1]) if pv else None)
    return rects, pivots


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "lucian_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        n = spec["n"]
        fn = f"lucian_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        rects, pivots = rects_of(manifest[fn])
        if len(rects) != n:
            sys.exit(f"{fn}: the manifest lists {len(rects)} frames, not {n}")
        mine = own(solid, rects)
        boxes = []
        for m in mine:
            ys, xs = np.nonzero(m)
            boxes.append((xs.min(), xs.max() + 1, ys.min(), ys.max() + 1) if len(xs) else None)
        live = [b for b in boxes if b]
        boxes = [b or live[0] for b in boxes]
        ext = (lambda b: b[1] - b[0]) if spec["measure"] == "w" else (lambda b: b[3] - b[2])
        extent = max(ext(b) for b in live)
        s = spec["size"] / extent
        sv = s * spec.get("sy", 1.0)
        anchor = [(pivots[k][0] if spec["x"] == "pivot" else x_anchor(spec["x"], k, rects, boxes, s),
                   pivots[k][1] if spec["y"] == "pivot" else y_anchor(spec["y"], k, rects, boxes)) for k in range(n)]
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
        print(f"{fn}  {n} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over {extent} source px), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"lucian_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"lucian_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# tag: (strip, its frames used, spot of the anchor from the pivot, ms per frame)
FX = {
    "league_lucian_fx": {
        "bullet": ("bullet", range(4), (0, 0), [50] * 4),
        "ls_shot": ("ls_shot", range(3), (0, 0), [40] * 3),              # the double shot's first
        "ls_shot2": ("ls_shot2", range(3), (0, 0), [40] * 3),            # ... and its second, gold
        "hit": ("hit", range(5), HIT, [40] * 5),
        "vig_hit": ("vig_hit", range(5), HIT, [50] * 5),
        "vig_glow": ("vig_glow", range(4), HANDS, [80] * 4),
        "q_ray": ("q_beam", [f for f, _, _ in Q_RAY], [s for _, s, _ in Q_RAY], [m for _, _, m in Q_RAY]),
        "q_hit": ("q_hit", range(5), CHEST, [40] * 5),
        "e_dash": ("e_dash", range(6), FEET, [50] * 6),
        "w_bolt": ("w_bolt", range(4), (0, 0), [50] * 4),
        "w_burst": ("w_burst", range(7), FEET, [50] * 7),
        "w_mark": ("w_mark", range(4), FEET, [120] * 4),
        "w_haste": ("w_haste", range(4), FEET, [60] * 4),
        "r_bullet": ("r_bullet", range(3), (0, 0), [40] * 3),
        "r_hit": ("r_hit", range(3), HIT, [40] * 3),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "lucian_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (src, used, spot, ms) in tags.items():
            ax, ay = anchors[src]["anchor"]
            strip = cells(src, RAW[src]["n"] if src in RAW else DRAWN[src])
            spots = spot if isinstance(spot, list) else [spot] * len(ms)       # one spot, or one a frame
            out[tag] = [(G.centre_frame(strip[k], sx - ax, sy - ay), m) for k, (sx, sy), m in zip(used, spots, ms)]
            if tag == "q_ray":
                out[tag].append((np.zeros((1, 1, 4), np.uint8), RAY_AFTER))
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--only", nargs="+", help="with --raw: just these strips (e.g. bullet w_burst)")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only)
    tracer()
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

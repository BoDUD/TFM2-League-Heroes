#!/usr/bin/env python3
"""Import Morgana's effects (assets/source/morgana/PROMPTS.md, 1-11) as game sheets.

    python tools/art/import_morgana.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_morgana.py                                   # native strips -> effect sheets

The body comes from tools/art/tidy_morgana.py and tools/art/import_native.py. Codex's eleven strips came back as
raw image-generator output with real alpha (1484-2172 px wide canvases, 26 000-61 000 colours) and a manifest.json
giving every frame's rectangle in the source (`assets[].frames[].rect`, [x, y, width, height], one band of rows per
strip; Codex moved some cut lines into the gaps between drawings, so the burst's and the hit's rectangles are not
equally wide). --raw turns every frame into a cell of a native strip the way tools/art/import_thresh.py does (every
game pixel one flat 8x8 block, binary alpha, 16 colours by median cut, each game pixel the majority colour of the
source pixels it covers, opaque when a third of them are, the anchor on the middle of a game pixel). The two
pictures that fly (the bolt, the binding orb) are turned to their direction by the game, so they are made exactly
symmetric about their core's row (the upper half mirrored down). Writes assets/source/morgana/morgana_fx_<name>.png
plus morgana_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the bolt 14 px
long, the orb with its chain trail 28 px (its spiky orb about 14, the projectile's circle radius 7000), the hits
14-20 px, the shackles 36 px from their ground ring to the chains' top (a 35 px hero's crown), the pool's ellipse
44 px wide (radius 22000), the shield 42 px tall round a 35 px hero, the burst's plain ring 100 px (radius 50000),
the chain's waist ring 22 px, the chains breaking 28 px and the stun sigil 24 px.
Anchors, measured on each drawing (not on the rectangles): the flying pictures on their white core; the hits on
their core (or, once it has faded, the drawing's middle) frame by frame; the shackles on their ground ring (frame
1 draws it alone); the pool on the middle of its ellipse (the rows at least half as wide as the widest, the smoke
above left out); the shield's bottom rim on the ground; the burst frame by frame on its ring; the latch on the
flash where the chain snaps shut; the waist ring on its own middle (the chain to the left and the smoke above
left out); the breaking chains on their flash, the sigil on its core.
The second step places every cell by its anchor: the bolt and the orb on their projectile's point; the hits on the
body; the shackles' ring, the pool, the shield's rim and the burst on the ground under the unit (a view played at
a spot is drawn like one on a unit, 11 px above the ground); the chain's ring round the waist; the snap's three
breaking frames round the waist and the sigil over the head (40 px above the ground). The shackles play 2 s in one
Animation (three frames binding, the four held ones four times, two breaking: the root), the pool 4 s (its zone's
time: two spreading, the four pulsing nine times, two shrinking), the snap 1.5 s (the stun: the sigil's four frames
three times); the shield is the buff's three phases (rising, held, shattering); the chain loops once in 333 ms, the
tether's pulse (its buff is added again every 20 ticks while the champion stays in reach).
No palette or outline pass on the sheets. Writes league/effects/league_morgana_fx (bolt, q_orb, hit, q_hit,
q_bind, e_shield_in, e_shield, e_shield_out, r_hit, r_chain, r_snap) and league/effects/league_morgana_big (w_pool,
r_cast).
"""
import argparse
import json
import math
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from import_leona import palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "morgana")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
BODY = (0, -6)                         # the middle of a 34 px hero
HIT = (0, -8)                          # a hit on the upper body
WAIST = (0, -1)
OVERHEAD = (0, -29)                    # 40 px above the ground: over a 35 px hero's crown

# raw strip -> native: name: dict(n frames in the source, size in game px, measure, x anchor, y anchor, mirror,
#   src (another strip's PNG), frames (the source frames this strip takes))
#   measure: "w" the widest drawing, "h" the tallest, "body" the widest ellipse (rows at least half as wide as the
#     widest), "ring" the widest waist ring; on=k measures frame k only
#   anchors (x and y alike):
#     "centre"        frame by frame: the white core's middle, or the drawing's middle once there is no core
#     ("core", ks)    the white core's middle in frames ks (None: every frame with one), the same spot in every
#                     frame's rectangle
#     ("frame", ks)   the drawing's middle in frame ks (one index or a list), the same spot in every rectangle
#     "body"          frame by frame (x) or averaged (y): the middle of the ellipse's rows
#     "ring"          frame by frame: the middle of the waist ring (the widest connected drawing, the columns where
#                     it is at least half its greatest height up to its right end)
#     ("bottom", k)   y: the lowest row of frame k's drawing
RAW = {
    "bolt": dict(n=4, size=14, measure="w", x=("core", None), y=("core", None), mirror=True),
    "hit": dict(n=5, size=14, measure="w", x="centre", y="centre"),
    "q_orb": dict(n=4, size=28, measure="w", x=("core", None), y=("core", None), mirror=True),
    "q_hit": dict(n=5, size=16, measure="w", x=("core", [1, 2, 3]), y=("core", [1, 2, 3])),
    "q_bind": dict(n=9, size=36, measure="h", x=("frame", 0), y=("frame", 0)),
    "w_pool": dict(n=8, size=44, measure="body", x="body", y="body"),
    "e_shield": dict(n=10, size=42, measure="h", on=3, x=("frame", 3), y=("bottom", 3)),
    "r_cast": dict(n=7, size=100, measure="w", on=4, x="centre", y=("frame", [0, 1, 2, 3, 4])),
    "r_hit": dict(n=5, size=20, measure="w", x=("core", [1, 2]), y=("core", [1, 2])),
    "r_chain": dict(n=4, size=22, measure="ring", x="ring", y="ring"),
    "r_snap": dict(n=8, frames=[0, 1, 2], size=28, measure="w", x=("core", [0, 1]), y=("core", [0, 1])),
    "r_stun": dict(src="r_snap", n=8, frames=[3, 4, 5, 6, 7], size=24, measure="w", x=("core", [3, 4, 5, 6]),
                   y=("core", [3, 4, 5, 6])),
}


def load_manifest(folder):
    path = os.path.join(folder, "manifest.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8-sig") as f:
        return {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}


def rect(fr):
    r = fr.get("rect", fr.get("source_rect"))
    if isinstance(r, dict):
        return [int(r["x"]), int(r["y"]), int(r.get("w", r.get("width"))), int(r.get("h", r.get("height")))]
    return [int(v) for v in r]


class Frames:
    """What the anchors are measured on, per frame of a strip, in the source's coordinates."""

    def __init__(self, a, solid, rects):
        self.rects = rects
        bright = solid & (a[..., :3].min(-1) >= 225)
        self.box, self.core, self.body, self.ring = [], [], [], []
        for x, y, w, h in rects:
            s = solid[y:y + h, x:x + w]
            ys, xs = np.nonzero(s)
            self.box.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
            by, bx = np.nonzero(bright[y:y + h, x:x + w])
            self.core.append((x + bx.mean() + 0.5, y + by.mean() + 0.5) if len(bx) >= 50 else None)
            widths = s.sum(1)
            rows = np.nonzero(widths >= 0.5 * widths.max())[0]
            cols = np.nonzero(s[rows].any(0))[0]
            self.body.append((x + (cols.min() + cols.max() + 1) / 2, y + (rows.min() + rows.max() + 1) / 2,
                              cols.max() - cols.min() + 1))
            self.ring.append(self.waist_ring(s, x, y))

    @staticmethod
    def waist_ring(s, x, y):
        """(middle x, middle y, width) of the widest connected drawing's ring part, or None."""
        lab = np.zeros(s.shape, int)
        best, n = None, 0
        for y0, x0 in zip(*np.nonzero(s)):
            if lab[y0, x0]:
                continue
            n += 1
            todo, px = deque([(y0, x0)]), []
            lab[y0, x0] = n
            while todo:
                yy, xx = todo.popleft()
                px.append((yy, xx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = yy + dy, xx + dx
                        if 0 <= ny < s.shape[0] and 0 <= nx < s.shape[1] and s[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n
                            todo.append((ny, nx))
            if best is None or len(px) > len(best):
                best = px
        comp = np.zeros(s.shape, bool)
        ys, xs = zip(*best)
        comp[list(ys), list(xs)] = True
        span = np.array([np.ptp(np.nonzero(c)[0]) + 1 if c.any() else 0 for c in comp.T])
        left = int(np.nonzero(span >= 0.5 * span.max())[0].min())
        right = int(max(xs)) + 1
        rows = np.nonzero(comp[:, left:right].any(1))[0]
        return x + (left + right) / 2, y + (rows.min() + rows.max() + 1) / 2, right - left

    def extent(self, measure, on=None):
        ks = [on] if on is not None else range(len(self.rects))
        if measure == "w":
            return max(self.box[k][1] - self.box[k][0] for k in ks)
        if measure == "h":
            return max(self.box[k][3] - self.box[k][2] for k in ks)
        if measure == "body":
            return max(self.body[k][2] for k in ks)
        if measure == "ring":
            return max(self.ring[k][2] for k in ks)
        raise ValueError(measure)

    def anchor(self, how, k, axis):
        """The anchor's x (axis 0) or y (axis 1) in frame k."""
        origin = self.rects[k][axis]

        def mid(box):
            return (box[0] + box[1]) / 2 if axis == 0 else (box[2] + box[3]) / 2

        if how == "centre":
            return self.core[k][axis] if self.core[k] else mid(self.box[k])
        if how == "body":
            if axis == 0:
                return self.body[k][0]
            return origin + np.mean([b[1] - r[1] for b, r in zip(self.body, self.rects)])
        if how == "ring":
            return self.ring[k][axis]
        kind, arg = how
        if kind == "core":
            ks = [j for j in range(len(self.rects)) if self.core[j]] if arg is None else arg
            return origin + np.mean([self.core[j][axis] - self.rects[j][axis] for j in ks])
        if kind == "frame":
            ks = arg if isinstance(arg, list) else [arg]
            return origin + np.mean([mid(self.box[j]) - self.rects[j][axis] for j in ks])
        if kind == "bottom":
            return origin + (self.box[arg][3] - self.rects[arg][1])
        raise ValueError(how)


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "morgana_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"morgana_fx_{spec.get('src', name)}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        if not (a[..., 3] < 255).any():             # delivered on black: alpha from the brightness
            a[..., 3] = np.clip(a[..., :3].max(-1).astype(int) * 3, 0, 255)
        solid = a[..., 3] >= 100
        if fn in manifest:
            rects = [rect(f) for f in manifest[fn]["frames"]]
        else:                                       # no manifest: equal cells side by side
            W = a.shape[1]
            rects = [[k * W // spec["n"], 0, (k + 1) * W // spec["n"] - k * W // spec["n"], a.shape[0]]
                     for k in range(spec["n"])]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: the manifest lists {len(rects)} frames, not {spec['n']}")
        used = spec.get("frames", list(range(spec["n"])))
        fr = Frames(a, solid, rects)
        mask = np.zeros(solid.shape, bool)          # the palette from this strip's frames only
        for k in used:
            x, y, w, h = rects[k]
            mask[y:y + h, x:x + w] = True
        b = a.copy()
        b[~mask, 3] = 0
        pal = palette(b)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        on = spec.get("on")
        extent = fr.extent(spec["measure"], on) if on is not None else max(
            fr.extent(spec["measure"], k) for k in used)
        s = spec["size"] / extent
        anchor = {k: (fr.anchor(spec["x"], k, 0), fr.anchor(spec["y"], k, 1)) for k in used}
        # the anchor is the middle of pixel (L, U); the cell is 2L+1 x 2U+1
        L = max(math.ceil(max(max(anchor[k][0] - fr.box[k][0], fr.box[k][1] - anchor[k][0]) for k in used) * s - 0.5),
                0) + 1
        U = max(math.ceil(max(max(anchor[k][1] - fr.box[k][2], fr.box[k][3] - anchor[k][1]) for k in used) * s - 0.5),
                0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(used), 4), np.uint8)
        for i, k in enumerate(used):
            x, y, w, h = rects[k]
            ax, ay = anchor[k]
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / s))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / s)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)             # this frame's rows only
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)         # and columns
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
            G.lp(os.path.join(SRC, f"morgana_fx_{name}.png")))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(used)}
        print(f"morgana_fx_{name}.png  {len(used)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} "
              f"({spec['size']} px over {extent} source px), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"morgana_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"morgana_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# the shackles: three frames binding, the four held ones four times, two breaking - the 2 s root
BIND = [0, 1, 2] + [3, 4, 5, 6] * 4 + [7, 8]
BIND_MS = [80] * 3 + [100] * 16 + [80] * 2
# the pool: two frames spreading, the four pulsing ones nine times, two shrinking - its zone's 4 s
POOL = [0, 1] + [2, 3, 4, 5] * 9 + [6, 7]
POOL_MS = [100] * 40
# the stun sigil (r_stun's cells: Codex's frames 4-8): its four frames three times, then the specks - with the three
# breaking frames, the 1.5 s stun
STUN = [0, 1, 2, 3] * 3 + [4]
STUN_MS = [100] * 12 + [60]

# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]} - a tag can be
# made of several strips, one after another
FX = {
    "league_morgana_fx": {
        "bolt": [("bolt", range(4), (0, 0), [60] * 4)],
        "q_orb": [("q_orb", range(4), (0, 0), [60] * 4)],
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "q_hit": [("q_hit", range(5), BODY, [50] * 5)],
        "q_bind": [("q_bind", BIND, FEET, BIND_MS)],
        "e_shield_in": [("e_shield", range(3), FEET, [80] * 3)],
        "e_shield": [("e_shield", range(3, 7), FEET, [100] * 4)],
        "e_shield_out": [("e_shield", range(7, 10), FEET, [70] * 3)],
        "r_hit": [("r_hit", range(5), BODY, [60] * 5)],
        "r_chain": [("r_chain", range(4), WAIST, [83, 83, 84, 83])],
        "r_snap": [("r_snap", range(3), WAIST, [80] * 3), ("r_stun", STUN, OVERHEAD, STUN_MS)],
    },
    "league_morgana_big": {
        "w_pool": [("w_pool", POOL, FEET, POOL_MS)],
        "r_cast": [("r_cast", range(7), FEET, [70] * 7)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "morgana_fx_anchors.json")), encoding="utf-8") as f:
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

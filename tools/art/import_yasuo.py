#!/usr/bin/env python3
"""Import Yasuo's effects (assets/source/yasuo/PROMPTS.md, 12-23) as game sheets.

    python tools/art/import_yasuo.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_yasuo.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's effect strips
came back as raw image-generator output, like Amumu's: soft alpha, antialiased colours, and cells in
other proportions than asked (2172x724 and 1983x793 for square or 2:1 cells). --raw turns each into a
native strip (equal cells, every game pixel one flat 8x8 block, binary alpha) written to
assets/source/yasuo/yasuo_fx_<name>.png: the strip's colours cut to 12 by median cut, every game
pixel the majority colour of the source pixels it covers (opaque when a third of them are), at a
scale set by the kit: the Q thrust 45 px long (its 45000 x 12000 hit area), the whirlwind 24 px wide
(radius 12000), the EQ rings 50 px wide (radius 25000, drawn at half size and enlarged 2x, so their
squares match the others'), the rest sized to a 34 px hero.

Codex's wind wall (22) is not used: the user dropped Wind Wall from the kit.

The second step anchors each strip on the union of its frames' drawings: hits on the target's chest,
the Q thrust centred on its rectangle (the game turns it to the cast direction), the whirlwind with
its foot on the ground and its middle on the projectile, the knock-up rising from the target's feet,
the shield and the R slashes around the body, the Q-ready ribbons at the waist, the EQ rings round
Yasuo's middle. Views are drawn at the unit's pivot, 11 px above the feet line. No palette or
outline pass on the sheets.
Writes league/effects/league_yasuo_fx (hit, q_hit, knockup, e_hit, shield, q_ready) and
league/effects/league_yasuo_big (q_thrust, tornado, eq, eq3, r_slash, tornado_0 .. tornado_5).

Q3's whirlwind is not drawn as its projectile's picture, which the game turns to the flight: the upright funnel
flew upside down to the left (the red side, mostly; the user kept the funnel: 「亚索的旋风特效还是用这个 右边的话你想办法处理一下」,
2026-10-05). The projectile flies without a picture and the funnel is stamped where it is, every STAMP_TICKS, by
`ViewEffect`s (never turned) in the end_effects of hidden projectiles that stop there
(tools/fix/fix_yasuo_q3_stamps.py). tornado_0 .. tornado_5 are the loop's six frames one by one, each held for
STAMP_MS (its stamp's ticks and a little more, so that one stamp is not gone before the next is drawn); they
share the tornado tag's squares on the sheet.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yasuo")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)                        # the feet line / the ground, from the pivot
CHEST = (0, -4)
BODY = (0, -6)                        # the middle of a 34 px hero

# raw strip -> native: {name: (frames, game px per source px)}
RAW = {
    "hit": (5, 0.06),
    "q_hit": (5, 0.06),
    "knockup": (6, 0.085),
    "e_hit": (5, 0.075),
    "shield": (6, 0.1),
    "q_ready": (6, 0.1),
    "q_thrust": (4, 0.088),          # the spear ~510 source px -> 45 px
    "tornado": (6, 0.08),            # ~300 -> 24 px
    "eq": (5, 0.0735),               # enlarged 2x on import: ring ~50 px
    "eq3": (6, 0.08),                # 2x: ring ~50 px
    "r_slash": (8, 0.1),
}


def from_raw(folder):
    for name, (n, s) in RAW.items():
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"yasuo_fx_{name}.png"))).convert("RGBA"))
        solid = a[..., 3] >= 100
        q = Image.fromarray(a[..., :3][solid].reshape(-1, 1, 3)).quantize(12, method=Image.MEDIANCUT)
        pal = np.array(q.getpalette()[:36], float).reshape(12, 3)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        H, W = a.shape[:2]
        cw = W / n
        tw, th = int(round(cw * s)), int(round(H * s))
        out = np.zeros((th, tw * n, 4), np.uint8)
        for k in range(n):
            for r in range(th):
                y0, y1 = int(r / s), max(int((r + 1) / s), int(r / s) + 1)
                for c in range(tw):
                    x0 = int(k * cw + c / s)
                    x1 = max(int(k * cw + (c + 1) / s), x0 + 1)
                    m = solid[y0:y1, x0:x1]
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[y0:y1, x0:x1][m], minlength=12).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"yasuo_fx_{name}.png")))
        print(f"yasuo_fx_{name}.png  {n} cells of {tw}x{th}, {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"yasuo_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"yasuo_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def union(fx, fy):
    """One anchor for every frame, from the union of their drawings: fx / fy of the way across and down
    (0.5 = the middle, 1.0 = the bottom row)."""
    def at(fs):
        m = np.any([f[..., 3] > 0 for f in fs], 0)
        ys, xs = np.nonzero(m)
        return [(xs.min() + fx * (xs.max() + 1 - xs.min()), ys.min() + fy * (ys.max() + 1 - ys.min()))] * len(fs)
    return at


# sprite: {tag: (strip, frames, enlarge, anchor, spot from the pivot, ms per frame)}
FX = {
    "league_yasuo_fx": {
        "hit": ("hit", 5, 1, union(0.5, 0.5), CHEST, [60] * 5),
        "q_hit": ("q_hit", 5, 1, union(0.5, 0.5), CHEST, [60] * 5),
        # rises from the target's feet; follows the target into the air
        "knockup": ("knockup", 6, 1, union(0.5, 1.0), FEET, [167] * 6),
        "e_hit": ("e_hit", 5, 1, union(0.5, 0.5), (0, -2), [60] * 5),
        "shield": ("shield", 6, 1, union(0.5, 0.5), BODY, [333] * 6),
        # the ribbons circle the waist of his crouch, 13 px above the feet
        "q_ready": ("q_ready", 6, 1, union(0.5, 0.5), (0, -2), [100] * 6),
    },
    "league_yasuo_big": {
        # the rectangle's view is centred on it and turned to the cast direction
        "q_thrust": ("q_thrust", 4, 1, union(0.5, 0.5), (0, 0), [55] * 4),
        # a projectile flies at the pivot's height: the foot 11 px below it, on the ground
        "tornado": ("tornado", 6, 1, union(0.5, 0.65), (0, 0), [60] * 6),
        "eq": ("eq", 5, 2, union(0.5, 0.5), (0, 0), [60] * 5),
        # the ring on the ground round his feet, the column rising out of it
        "eq3": ("eq3", 6, 2, union(0.5, 0.9), FEET, [70] * 6),
        "r_slash": ("r_slash", 8, 1, union(0.5, 0.5), BODY, [70] * 8),
    },
}


STAMP_TICKS = 2
STAMP_MS = 34                         # 2 ticks are 33.3 ms


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (strip, n, k, anchor, (sx, sy), ms) in tags.items():
            fs = cells(strip, n)
            frames = []
            for f, (ax, ay), m in zip(fs, anchor(fs), ms):
                if k > 1:
                    f = np.kron(f, np.ones((k, k, 1), np.uint8))
                    ax, ay = ax * k, ay * k
                u0, r0 = int(round(sx - ax)), int(round(sy - ay))
                frames.append((G.centre_frame(f, u0, r0), m))
            out[tag] = frames
        sheets[sprite] = out
    big = sheets["league_yasuo_big"]
    for i, (f, _) in enumerate(big["tornado"]):
        big[f"tornado_{i}"] = [(f, STAMP_MS)]
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags, share=sprite == "league_yasuo_big")
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

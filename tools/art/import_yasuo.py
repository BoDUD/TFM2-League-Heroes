#!/usr/bin/env python3
"""Import Yasuo's effects (assets/source/yasuo/PROMPTS.md, 12-23) as game sheets.

    python tools/art/import_yasuo.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_yasuo.py --wall                            # once: draw the wind wall strip
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

The wind wall is drawn by --wall instead (see wall_frame): Codex's upright column of twisted wind
read as a tornado to the user, so it now takes the shape of League's own ground line. It is a caster
view, not a projectile's: a LineRangeProjectile's view is turned to the cast direction, and cast
upward the wall lay over Yasuo's head, which the user ruled out; a CasterViewEffect is not turned,
is mirrored when he faces left and stays where he raised it.

The second step anchors each strip on the union of its frames' drawings (the wall on its back line):
hits on the target's chest, the Q thrust centred on its rectangle (the game turns it to the cast
direction), the wind wall 20 px in front of Yasuo, the whirlwind with its foot on the ground and its
middle on the projectile, the knock-up rising from the target's feet, the shield and the R slashes
around the body, the Q-ready ribbons at the waist, the EQ rings round Yasuo's middle. Views are drawn
at the unit's pivot, 11 px above the feet line. No palette or outline pass on the sheets; repeated
frames (the wall's 4 s loop) are packed once.
Writes league/effects/league_yasuo_fx (hit, q_hit, knockup, e_hit, shield, q_ready) and
league/effects/league_yasuo_big (q_thrust, tornado, wall, eq, eq3, r_slash).
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

# the wind wall: the effects' blues from dark to light, and League's ground-line cyan
WALL_BLUES = ["2173c4", "3f9fe0", "4eb5ec", "65c7f3", "a0e7fc", "ccf4fd", "fdfdfe"]
WALL_LINE = "4ae3ee"
WALL_GUST = [6, 6, 5, 4, 4, 3, 3]    # a gust's shades from its head down its tail
# (spacing, phase) of the gusts in each lane, back to front: a spacing of 12 or 18 moves 2 or 3 px a
# frame and loops in 6 frames
WALL_LANES = [(12, 6), (18, 5), (12, 9), (18, 10), (12, 2), (18, 14), (12, 4), (18, 1), (12, 11), (18, 8)]
WALL_SIZE = dict(length=64, depth=10, bow=3, arm=6)
# strip cells: 0-5 the loop, 6-7 the wall rising, 8-10 blowing away. It stands the buff's 4 s (240
# ticks): 40 frames of 100 ms, rising into the loop's first frame and blowing away after its fifth
WALL_CELLS = 11
WALL_ORDER = [6, 7] + list(range(6)) * 5 + [0, 1, 2, 3, 4] + [8, 9, 10]
WALL_BACK = (13, 35)                  # the back line's middle in a cell (column, row edge)


def _noise(x, y):
    n = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return (n ^ (n >> 16)) / 2 ** 32


def wall_frame(k, length=64, depth=10, bow=3, arm=6, grow=1.0, gone=0.0):
    """Frame k (of the 6-frame loop) of League's Wind Wall in front of Yasuo facing right, as RGBA.

    The shape is League's ground line (Yasuo_base_W_windwall_indicator): a long line across his
    facing, bowed `bow` px forward, its ends bent back toward him at 45 degrees with the tips curled
    in. The curtain of wind stands on its forward side, `depth` px: dense at the foot, only gusts
    toward the top, which gives a wispy front edge. The gusts flow along the wall (up, 2 or 3 px a
    frame) with white heads and fading tails like Yasuo_W_windwall_main_02, and the wall dims toward
    its ends. `length` 64 stands well past him (34 px, the ponytail 43): the user found 44 px too
    small to shield him. `grow` < 1 draws only the middle of the wall (rising), `gone` > 0 drops that
    share of its pixels (blowing away). The back line's middle is WALL_BACK of the 28 x 70 canvas.
    """
    pad = 3
    h, w = length + 2 * pad, arm + bow + depth + 2 * pad + 3
    img = np.zeros((h, w, 4), np.uint8)
    cy, half = h / 2, length / 2
    x0 = pad + arm + 1                             # the back line where the arms start

    def put(x, y, colour):
        x, y = int(x), int(y)
        if _noise(x, y) >= gone:
            img[y, x, :3] = [int(colour[i:i + 2], 16) for i in (0, 2, 4)]
            img[y, x, 3] = 255

    for y in range(int(cy - half), int(cy + half)):
        off = y + 0.5 - cy
        if abs(off) > half * grow:
            continue
        e = half - abs(off)                        # rows from the nearer end
        if e >= arm:
            s = off / (half - arm)
            xb = x0 + round(bow * (1 - s * s))
            t = depth
        else:                                      # the arms: bent back, the curtain thinning out
            xb = x0 - int(arm - e)
            t = max(0, round(depth * e / arm) - 1)
        c = min(1.0, e / (half * 0.6))             # 0 at the ends .. 1 over the middle
        for j in range(1, t + 1):
            per, phase = WALL_LANES[j - 1]
            q = (y + k * (per // 6) + phase) % per
            if q < len(WALL_GUST):
                shade = WALL_GUST[q] - (1 if c < 0.5 else 0)
            elif j > (t + 1) // 2:
                continue                           # the top of the curtain: only the gusts
            else:
                shade = 3 if c > 0.5 else 2
            put(xb + j, y, WALL_BLUES[shade])
        put(xb, y, WALL_LINE)
    if grow >= 1:
        for sgn in (-1, 1):
            ty = cy + sgn * half - (1 if sgn > 0 else 0)
            put(x0 - arm - 1, ty - sgn, WALL_LINE)
            put(x0 - arm - 2, ty, WALL_LINE)
    return img


def draw_wall():
    cells = [wall_frame(k, **WALL_SIZE) for k in range(6)]
    cells += [wall_frame(4, grow=0.45, **WALL_SIZE), wall_frame(5, grow=0.8, **WALL_SIZE)]
    cells += [wall_frame(k, gone=g, **WALL_SIZE) for k, g in ((5, 0.3), (0, 0.55), (1, 0.8))]
    strip = np.concatenate(cells, 1)
    Image.fromarray(np.repeat(np.repeat(strip, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, "yasuo_fx_wall.png")))
    print(f"yasuo_fx_wall.png  {len(cells)} cells of {strip.shape[1] // len(cells)}x{strip.shape[0]}, "
          f"{len(np.unique(strip[strip[..., 3] > 0][:, :3], axis=0))} colours")


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


def point(x, y):
    """One fixed anchor for every frame, in cell pixels."""
    return lambda fs: [(x, y)] * len(fs)


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
        # a caster view (not turned; mirrored when he faces left): the back line 20 px in front of
        # his pivot, clear of his body, the wall's middle 7 px above it (18 px above his feet), so
        # it reaches 14 px below the feet line and 7 px over his ponytail
        "wall": ("wall", WALL_CELLS, 1, point(*WALL_BACK), (20, -7), [100] * len(WALL_ORDER), WALL_ORDER),
        "eq": ("eq", 5, 2, union(0.5, 0.5), (0, 0), [60] * 5),
        # the ring on the ground round his feet, the column rising out of it
        "eq3": ("eq3", 6, 2, union(0.5, 0.9), FEET, [70] * 6),
        "r_slash": ("r_slash", 8, 1, union(0.5, 0.5), BODY, [70] * 8),
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (strip, n, k, anchor, (sx, sy), ms, *order) in tags.items():
            fs = cells(strip, n)
            at = anchor(fs)
            order = order[0] if order else range(n)
            frames = []
            for (f, (ax, ay)), m in zip([(fs[i], at[i]) for i in order], ms):
                if k > 1:
                    f = np.kron(f, np.ones((k, k, 1), np.uint8))
                    ax, ay = ax * k, ay * k
                u0, r0 = int(round(sx - ax)), int(round(sy - ay))
                frames.append((G.centre_frame(f, u0, r0), m))
            out[tag] = frames
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--wall", action="store_true", help="draw the wind wall's native strip first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    if args.wall:
        draw_wall()
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags, dedupe=True)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

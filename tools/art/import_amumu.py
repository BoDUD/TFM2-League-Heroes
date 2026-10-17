#!/usr/bin/env python3
"""Import Amumu's effects (assets/source/amumu/PROMPTS.md, 11-18) as game sheets.

    python tools/art/import_amumu.py --raw <Codex's generated/ folder>   # once: raw PNGs -> native strips
    python tools/art/import_amumu.py                                       # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's eight effect
strips came back as raw image-generator output: soft alpha, antialiased colours, and cells in other
proportions than asked (2172x724 for six square cells). --raw turns each into a native strip, the
format of the other heroes' deliveries (equal cells, every game pixel one flat 8x8 block, binary
alpha), written to assets/source/amumu/amumu_fx_<name>.png: the strip's colours are cut to 12 by
median cut, every game pixel takes the majority colour of the source pixels it covers (opaque when a
third of them are), at a scale that makes one of the generator's blocks about one game pixel, or one
effect pixel of an effect enlarged 2x. The sizes follow the kit: the Tantrum ring about 58 px wide
(E radius 28000), the R burst about 84 px (42000), Despair's ground ring about 56 px (25000).

The second step reads those strips like import_darius.py: hits on the target's chest, the bandage
projectile on its knot (the front of the drawing, flying right), the wraps and the curse on the
target, Despair's ring and the Tantrum ring on Amumu's feet, the R burst on his middle. Views are
drawn at the unit's pivot, 11 px above the feet line. No palette or outline pass on the sheets.
Writes league/effects/league_amumu_fx (hit, q_bandage, q_wrap, curse, despair, r_wrap) and
league/effects/league_amumu_big (e_tantrum, r_burst).
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

SRC = os.path.join(ROOT, "assets", "source", "amumu")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)                        # the feet line / the ground, from the pivot
CHEST = (0, -4)

# raw strip -> native: {name: (frames, game px per source px)}
RAW = {
    "hit": (5, 0.06),
    "q_bandage": (4, 0.09),
    "q_wrap": (6, 0.085),
    "curse": (6, 0.065),
    "despair": (6, 0.0875),          # enlarged 2x on import: ring ~56 px
    "e_tantrum": (6, 0.08),          # 2x: ring ~58 px
    "r_burst": (6, 0.118),           # 2x: ring ~84 px
    "r_wrap": (6, 0.085),
}


def from_raw(folder):
    for name, (n, s) in RAW.items():
        a = np.asarray(Image.open(G.lp(os.path.join(folder, f"amumu_fx_{name}.png"))).convert("RGBA"))
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
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"amumu_fx_{name}.png")))
        print(f"amumu_fx_{name}.png  {n} cells of {tw}x{th}, {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"amumu_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"amumu_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def centre(fs):
    """Anchor: the middle of the cell (the drawing is centred in it)."""
    return [(f.shape[1] / 2.0, f.shape[0] / 2.0) for f in fs]


def knot(fs):
    """The projectile flying right: the front of its drawing, 3 px back, at the height of the
    pixels in its front quarter (the bandage trails to the left)."""
    out = []
    for f in fs:
        ys, xs = np.nonzero(f[..., 3])
        x1 = xs.max()
        front = xs >= x1 - max(3, (x1 - xs.min()) // 4)
        out.append((x1 - 2.5, float(np.median(ys[front])) + 0.5))
    return out


def union(fx, fy):
    """One anchor for every frame, from the union of their drawings: fx / fy of the way across and down
    (0.5 = the middle, 1.0 = the bottom row)."""
    def at(fs):
        m = np.any([f[..., 3] > 0 for f in fs], 0)
        ys, xs = np.nonzero(m)
        return [(xs.min() + fx * (xs.max() + 1 - xs.min()), ys.min() + fy * (ys.max() + 1 - ys.min()))] * len(fs)
    return at


def cell_at(fx, fy):
    """One anchor for every frame at a fixed place in the cell."""
    return lambda fs: [(fx * fs[0].shape[1], fy * fs[0].shape[0])] * len(fs)


# sprite: {tag: (strip, frames, enlarge, anchor, spot from the pivot, ms per frame)}
FX = {
    "league_amumu_fx": {
        "hit": ("hit", 5, 1, centre, CHEST, [60] * 5),
        "q_bandage": ("q_bandage", 4, 1, knot, (0, 0), [60] * 4),
        "q_wrap": ("q_wrap", 6, 1, union(0.5, 0.5), (0, -6), [167] * 6),
        # the mark floats over the head: its drawing's top at 36 px above the pivot
        "curse": ("curse", 6, 1, union(0.5, 0.0), (0, -36), [167] * 6),
        # the ground ring round Amumu's feet: the union's bottom 12% is the ring's lower edge
        "despair": ("despair", 6, 2, union(0.5, 0.88), (0, 18), [167] * 6),
        # the cocoon stands on the target's feet
        "r_wrap": ("r_wrap", 6, 1, union(0.5, 1.0), (0, 12), [250] * 6),
    },
    "league_amumu_big": {
        # the burst surrounds a person 40% of the cell tall, feet at 70% of the cell height
        "e_tantrum": ("e_tantrum", 6, 2, cell_at(0.5, 0.70), FEET, [60] * 6),
        "r_burst": ("r_burst", 6, 2, union(0.5, 0.5), (0, -2), [80] * 6),
    },
}


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
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's generated/ folder: rebuild the native strips from its raw PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()

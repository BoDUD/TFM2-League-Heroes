#!/usr/bin/env python3
"""Put Codex's redraw of Lucian's back shoulder into the native strips.

    python tools/art/lucian_shoulder.py <Codex's delivery folder> [--dry] [--review FILE]

The user (2026-10-01): "卢锡安怎么释放技能的释放模型变形了" - "肩膀那里失去一块". In every frame where he points
both pistols forward - Q (skill) 2-5, R (ult) 1-4, the double shot (passive) 2-6 - the shoulder on the image's left
of his neck was not drawn: in the idle his raised arm fills that place, and when Codex brought that arm down to the
second pistol the place stayed empty, so the torso looked bitten off between the head and the cream collar. Codex
redrew only that shoulder (assets/source/lucian/SHOULDER_FIX.md): each frame came back as the whole 96x96 cell at 8x
with every square it had kept as it was. Per frame this reads the picture back one pixel per 8x8 block (the centre
of each block, every colour snapped to the design's 19), puts it over the cell by the irises and takes only the
squares that are empty in the cell and inside the frame's shoulder patch (area()); the outline is closed round the
new squares only (strips.complete_outline). The old outline at the edge of the gap now runs inside the shoulder: it
takes the next darker shade of the cream or gold around it, so no black seam splits the shoulder cap from the collar.
Every other pixel stays. Writes assets/source/native/lucian_{skill,ult,passive}.png; then run
import_native.py --hero lucian.
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from native_refs import layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z = 8
FRAMES = [("skill", n) for n in (2, 3, 4, 5)] + [("ult", n) for n in (1, 2, 3, 4)] + \
         [("passive", n) for n in (2, 3, 4, 5, 6)]
PALETTE = ("#181118 #2D2327 #28272F #2F2D36 #432541 #423536 #4F352C #3A3A42 #562E48 #77532D #3F6A74 #955F44 "
           "#66717C #B48D3E #CBA04B #A29690 #CFC1B4 #F3E6D1 #F4F2EA")
PAL = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in PALETTE.split()]
OUTLINE = PAL[0]
IRIS = (0x3F, 0x6A, 0x74)
H = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))  # noqa: E731
# the next darker shade inside the material's own ramp, for the old outline closed in by the new shoulder
SHADE = {H("#F4F2EA"): H("#CFC1B4"), H("#F3E6D1"): H("#CFC1B4"), H("#CFC1B4"): H("#A29690"),
         H("#A29690"): H("#A29690"), H("#CBA04B"): H("#B48D3E"), H("#B48D3E"): H("#77532D")}


def read_back(path):
    """One RGBA pixel per 8x8 block of a 768x768 picture: magenta, the brief's light grey or clear = empty."""
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    if a.shape[:2] != (768, 768):
        sys.exit(f"{path}: {a.shape[1]}x{a.shape[0]}, not the 768x768 cell")
    a = a[Z // 2::Z, Z // 2::Z]
    rgb = a[..., :3].astype(int)
    mag = (rgb[..., 0] > 200) & (rgb[..., 1] < 90) & (rgb[..., 2] > 200)
    grey = (np.abs(rgb - 225) <= 12).all(-1)
    op = (a[..., 3] >= 128) & ~mag & ~grey
    pal = np.array(PAL)
    idx = ((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    out = np.zeros(a.shape, np.uint8)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def eyes(a):
    """(row, left column) of the two irises."""
    p = np.argwhere((a[..., :3] == IRIS).all(-1) & (a[..., 3] > 0))
    return int(p[:, 0].min()), int(p[:, 1].min())


def n4(m):
    out = np.zeros_like(m)
    out[1:] |= m[:-1]
    out[:-1] |= m[1:]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    return out


def area(a):
    """The empty squares where the back shoulder goes (the brief's cyan patch): inside a round patch left of the
    neck, from the chin down beside the cream collar (centre 7 squares left of the left iris, 6.5 rows below it,
    radius 4.6), connected to the body."""
    ly, lx = eyes(a)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    cx, cy = lx - 7.0, ly + 6.5
    inside = (((xx + 0.5 - cx) / 4.6) ** 2 + ((yy + 0.5 - cy) / 4.6) ** 2 <= 1.0) & (yy >= ly + 2) & (xx <= lx - 3)
    m = inside & (a[..., 3] == 0)
    keep = np.zeros_like(m)
    grow = m & n4(a[..., 3] > 0)
    while grow.any():
        keep |= grow
        grow = m & n4(keep) & ~keep
    return keep


def pieces(a):
    op = a[..., 3] > 0
    seen = np.zeros_like(op)
    count = 0
    for y, x in zip(*np.nonzero(op)):
        if seen[y, x]:
            continue
        count += 1
        stack = [(y, x)]
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = cy + dy, cx + dx
                    if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and op[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
    return count


def patch(cell, got):
    """The cell with the delivered shoulder: (new cell, squares taken, outline added, seam squares shaded)."""
    (ly, lx), (gy, gx) = eyes(cell), eyes(got)
    dy, dx = ly - gy, lx - gx
    shifted = np.zeros_like(cell)
    h, w = cell.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    sy, sx = ys - dy, xs - dx
    ok = (sy >= 0) & (sy < got.shape[0]) & (sx >= 0) & (sx < got.shape[1])
    shifted[ok] = got[sy[ok], sx[ok]]
    take = area(cell) & (shifted[..., 3] > 0) & (cell[..., 3] == 0)
    new = cell.copy()
    new[take] = shifted[take]
    new, added, _ = G.complete_outline(new, color=OUTLINE, dark=70, keep=~(take | n4(take)))
    # the old outline that touched the gap and is now closed in by the shoulder
    lum = new[..., :3].astype(float) @ np.array([0.299, 0.587, 0.114])
    empty = cell[..., 3] == 0
    seam = (cell[..., 3] > 0) & (lum < 40) & n4(empty) & ~n4(new[..., 3] == 0) & n4(take)
    out = new.copy()
    shaded = 0
    for y, x in zip(*np.nonzero(seam)):
        around = [tuple(new[y + a, x + b, :3]) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if new[y + a, x + b, 3] > 0 and not seam[y + a, x + b]]
        light = [c for c in around if c in SHADE]
        if len(light) >= 2:                     # a seam between light materials; one along the dark body stays
            out[y, x, :3] = SHADE[Counter(light).most_common(1)[0][0]]
            shaded += 1
    return out, int(take.sum()), added, shaded, (dy, dx)


def find(delivery, tag, n):
    for base, _, files in os.walk(delivery):
        for f in files:
            if f.lower() in (f"lucian_{tag}_{n}.png", f"{tag}_{n}.png"):
                return os.path.join(base, f)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    ap.add_argument("--dry", action="store_true", help="check and report, write nothing")
    ap.add_argument("--review", help="before/after of the 13 frames at 4x")
    o = ap.parse_args()
    cells = json.load(open(G.lp(os.path.join(SRC, "lucian_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    strips, before, after = {}, [], []
    for tag, n in FRAMES:
        if tag not in strips:
            strips[tag] = np.asarray(Image.open(G.lp(os.path.join(SRC, f"lucian_{tag}.png"))).convert("RGBA")).copy()
        big = strips[tag]
        cols = layout(len(cells["tags"][tag]))[0]
        y0, x0 = ((n - 1) // cols) * ch, ((n - 1) % cols) * cw
        cell = big[y0 * Z:(y0 + ch) * Z:Z, x0 * Z:(x0 + cw) * Z:Z].copy()
        path = find(o.delivery, tag, n)
        if path is None:
            sys.exit(f"{tag} {n}: no lucian_{tag}_{n}.png in {o.delivery}")
        new, taken, added, shaded, (dy, dx) = patch(cell, read_back(path))
        if not taken:
            sys.exit(f"{tag} {n}: no shoulder in {path}")
        if pieces(new) > pieces(cell):
            sys.exit(f"{tag} {n}: the shoulder adds a loose piece")
        print(f"{tag} {n}: eyes {dy:+d},{dx:+d}; shoulder {taken} squares, outline +{added}, seam {shaded} shaded")
        before.append(cell)
        after.append(new)
        big[y0 * Z:(y0 + ch) * Z, x0 * Z:(x0 + cw) * Z] = np.repeat(np.repeat(new, Z, 0), Z, 1)
    if o.review:
        tiles = []
        for a, b in zip(before, after):
            ys, xs = np.nonzero((a[..., 3] > 0) | (b[..., 3] > 0))
            box = (slice(ys.min() - 1, ys.max() + 2), slice(xs.min() - 1, xs.max() + 2))
            col = []
            for c in (a[box], b[box]):
                t = np.zeros(c.shape, np.uint8)
                t[...] = (86, 112, 70, 255)
                t[c[..., 3] > 0] = c[c[..., 3] > 0]
                col.append(np.repeat(np.repeat(t, 4, 0), 4, 1))
            tiles.append(np.concatenate([col[0], np.full((4, col[0].shape[1], 4), 255, np.uint8), col[1]], 0))
        h = max(t.shape[0] for t in tiles)
        tiles = [np.pad(t, ((0, h - t.shape[0]), (0, 6), (0, 0)), constant_values=255) for t in tiles]
        Image.fromarray(np.concatenate(tiles, 1)).save(G.lp(o.review))
        print("review:", o.review)
    if not o.dry:
        for tag, big in strips.items():
            Image.fromarray(big).save(G.lp(os.path.join(SRC, f"lucian_{tag}.png")))
        print("written:", ", ".join(f"lucian_{t}.png" for t in strips))


if __name__ == "__main__":
    main()

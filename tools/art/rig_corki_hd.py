#!/usr/bin/env python3
"""Corki's frames, dense (PPU 5) and 1x, posed from whole drawings: league/champions/league_corki (1x tags + hd_ tags)
and assets/source/ppu/corki_<tag>.png (the dense strips tools/art/ppu_hd.py reads as drawn).

    python tools/art/rig_corki_hd.py [--review DIR]

The user, 2026-10-12: 「直接用PPU做吧」, then on Codex's PPU delivery (assets/source/corki/codex_ppu/raw): the side view
is Codex's raw drawing read back on its own grid (「用原稿 B」 - its own processed copy redrew the craft), then 「等等 模型应该用A」:
every action is posed from the FRONT (model A, as league_gragas's 「全部 3/4 正面」); the side drawing stays unused. No tilted poses
(「不倾斜，只浮动」: the nose-down / nose-up drawings came at the front angle), PPU 5 (「PPU 5：高 30、侧面宽 44」).
- FRONT (the idle and every action): the user's picture 2 read back on the side drawing's density (regrid --size 6.4: 195 x 150 squares,
  where design_corki_hd.py's first reading at its own 7.5 px gave 146 x 125); SIDE (every action): codex_ppu/raw/
  corki-side.png on its own grid (218 x 144), read but unused since 「模型应该用A」.
  DEAD: corki-dead-fall.png and corki-dead-crash.png read at the side's 6.3 px.
- One palette: k-means in Lab over every drawing together (COLOURS), so the craft's blues and the pilot's browns are the
  same in every frame.
- Every frame is a whole drawing moved by whole dense pixels (the hover's bob, a recoil, a lift) - never turned or
  stretched; only the propellers change: each blade is foreshortened toward its hub (a spinning blade seen at another
  angle: SPIN lengths), the side's edge-on bars and the front's blades that stand over empty ground (the front left
  rotor's lower blade lies on the wing and stays).
- He hovers: the bombs' lowest square HOVER 1x px over the ground line (the 1x soles row, FEET under the pivot).
A dense frame is 5x its 1x frame round the same centre (the pivot's 5x5 block in the middle); the 1x frame is the dense
one read back by 5x5 blocks (the commonest opaque colour where at least half the block is drawn), only for players
without league.dll.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402
import strips as G  # noqa: E402

K = 5                                     # PPU
SRC = os.path.join(ROOT, "assets", "source", "corki")
PICTURE = os.path.join(SRC, "user_picture", "corki-picture-2.png")
RAW = os.path.join(SRC, "codex_ppu", "raw")
OUT_PPU = os.path.join(ROOT, "assets", "source", "ppu")
STEM = os.path.join(ROOT, "league", "champions", "league_corki")
COLOURS = 56
FEET = 11                                 # the 1x ground row under the pivot (the soles' row of a standing hero)
HOVER = 3                                 # 1x px between the bombs and the ground
HALF = 40                                 # the 1x canvas half-size round the pivot (81 x 81)
SPIN = [1.0, 0.7, 0.4, 0.7]               # a blade's length in the spin's four states

# the rotors: blades as k-means-free boxes on each drawing (rows, cols) and their hub (row, col)
# (each blade: its box and the axis it is squeezed along - a spinning blade foreshortens along its length only)
SIDE_ROTORS = [{"hub": (8, 56), "blades": [((3, 13), (17, 54), "x"), ((3, 13), (59, 90), "x")]},
               {"hub": (19, 104), "blades": [((13, 24), (67, 102), "x"), ((13, 24), (106, 144), "x")]}]
FRONT_ROTORS = [{"hub": (20, 46), "blades": [((12, 27), (0, 40), "x"), ((5, 24), (51, 83), "x")]},
                {"hub": (14, 137), "blades": [((0, 11), (126, 145), "y"), ((9, 24), (95, 133), "x"),
                                              ((15, 31), (141, 189), "x")]}]
SPECK = 12                                # pieces smaller than this left apart by a squeeze go


def read(path, size=None):
    a = np.asarray(Image.open(path).convert("RGBA")).copy()
    d = RG.regrid(a, size)[0] if size else RG.regrid(a)[0]
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d[d[..., 3] == 0] = 0
    return d


def drawings():
    """{name: dense drawing} in one palette."""
    raw = {"front": read(PICTURE, 6.4), "side": read(os.path.join(RAW, "corki-side.png")),
           "fall": read(os.path.join(RAW, "corki-dead-fall.png"), 6.3),
           "crash": read(os.path.join(RAW, "corki-dead-crash.png"), 6.3)}
    # one k-means over all of them: stack them side by side
    H = max(a.shape[0] for a in raw.values())
    W = sum(a.shape[1] for a in raw.values())
    big = np.zeros((H, W, 4), np.uint8)
    x = 0
    for a in raw.values():
        big[:a.shape[0], x:x + a.shape[1]] = a
        x += a.shape[1]
    idx, pal = V.kmeans(big, COLOURS)
    out, x = {}, 0
    for n, a in raw.items():
        sub = idx[:a.shape[0], x:x + a.shape[1]]
        d = np.zeros_like(a)
        op = a[..., 3] > 0
        d[op, :3] = pal[sub[op]]
        d[op, 3] = 255
        out[n] = d
        x += a.shape[1]
    return out


def blade_mask(a, box):
    """The blade's pixels in its box: everything drawn there that is not the steel of a pole or wing under it."""
    (r0, r1), (c0, c1) = box[:2]
    m = np.zeros(a.shape[:2], bool)
    sub = a[r0:r1 + 1, c0:c1 + 1]
    r, g, b = [sub[..., i].astype(int) for i in range(3)]
    wood = (sub[..., 3] > 0) & (r > b + 30) & (r >= g - 10)
    dark = (sub[..., 3] > 0) & (r + g + b < 150)
    keep = wood | (dark & ndimage.binary_dilation(wood, iterations=1))
    m[r0:r1 + 1, c0:c1 + 1] = keep
    return m


def spin(a, rotors, f):
    """The drawing with every listed blade foreshortened to `f` of its length toward the hub along its axis (nearest
    pixels), the pieces a squeeze leaves apart dropped."""
    if f >= 1.0:
        return a
    out = a.copy()
    for rot in rotors:
        hy, hx = rot["hub"]
        for box in rot["blades"]:
            m = blade_mask(a, box)
            ys, xs = np.nonzero(m)
            if not len(ys):
                continue
            src = a.copy()
            out[m] = 0
            # every target pixel within the blade's shrunk reach takes the source pixel at hub + (p - hub) / f
            (r0, r1), (c0, c1), axis = box
            for y in range(r0, r1 + 1):
                for x in range(c0, c1 + 1):
                    sy = round(hy + (y - hy) / f) if axis == "y" else y
                    sx = round(hx + (x - hx) / f) if axis == "x" else x
                    if 0 <= sy < a.shape[0] and 0 <= sx < a.shape[1] and m[sy, sx]:
                        out[y, x] = src[sy, sx]
    lab, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3)))
    size = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
    for v, z in enumerate(size, 1):
        if z < SPECK:
            out[lab == v] = 0
    return out


def place(canvas, a, dx, dy, anchor):
    """Draw `a` on the dense canvas so its anchor (row, col in a) lands on the canvas point + (dy, dx)."""
    cy, cx = canvas.shape[0] // 2, canvas.shape[1] // 2
    y0, x0 = cy + dy - anchor[0], cx + dx - anchor[1]
    h, w = a.shape[:2]
    sub = canvas[y0:y0 + h, x0:x0 + w]
    m = a[..., 3] > 0
    sub[m] = a[m]


def anchor_of(a):
    """(row, col) of the drawing that sits on the pivot column and HOVER over the ground: the middle column, the row
    from which the lowest square is at FEET - HOVER 1x rows under the pivot."""
    h, w = a.shape[:2]
    low = K * (FEET - HOVER) + K // 2               # dense rows from the pivot's centre to the lowest square
    return (h - 1 - low, w // 2)


def frame(parts):
    """One dense frame on a (2 HALF + 1) K canvas from [(drawing, dx, dy, anchor)]."""
    n = (2 * HALF + 1) * K
    can = np.zeros((n, n, 4), np.uint8)
    for a, dx, dy, anc in parts:
        place(can, a, dx, dy, anc)
    return can


def down(dense):
    """The 1x frame: every 5x5 block one pixel, its commonest opaque colour when at least half of it is drawn."""
    n = dense.shape[0] // K
    out = np.zeros((n, n, 4), np.uint8)
    for r in range(n):
        for c in range(n):
            blk = dense[r * K:(r + 1) * K, c * K:(c + 1) * K].reshape(-1, 4)
            op = blk[blk[:, 3] > 0]
            if len(op) * 2 < K * K:
                continue
            cols, cnt = np.unique(op, axis=0, return_counts=True)
            out[r, c] = cols[cnt.argmax()]
    return out


def crop(dense, one):
    """Both frames cut to the same centred box (the 1x frame odd, the dense one K times it round the same centre)."""
    ys, xs = np.nonzero(dense[..., 3] > 0)
    c = dense.shape[0] // 2
    hh = (max(c - ys.min(), ys.max() - c) + K // 2) // K
    hw = (max(c - xs.min(), xs.max() - c) + K // 2) // K
    o = one.shape[0] // 2
    one_c = one[o - hh:o + hh + 1, o - hw:o + hw + 1]
    d0 = (o - hh) * K
    e0 = (o - hw) * K
    dense_c = dense[d0:d0 + (2 * hh + 1) * K, e0:e0 + (2 * hw + 1) * K]
    return dense_c, one_c


def tags(dr):
    """{tag: [(dense frame, ms)]} - the timings follow tools/kit/build_corki.P (duration, release tick)."""
    front = dr["front"]
    fa = anchor_of(front)
    fs = [spin(front, FRONT_ROTORS, f) for f in SPIN]
    T = {}
    bob = [0, 2, 4, 6, 8, 6, 4, 2]
    T["idle"] = [(frame([(fs[i % 4], 0, bob[i], fa)]), 100) for i in range(8)]
    run_bob = [0, 2, 4, 2, 0, -2, -4, -2]
    T["run"] = [(frame([(fs[i % 4], 0, run_bob[i], fa)]), 80) for i in range(8)]
    # attack: 24 ticks, the shot on tick 8: hold, hold, recoil 5 at the shot, ease back
    T["attack"] = [(frame([(fs[i % 4], dx, 0, fa)]), ms) for i, (dx, ms) in
                   enumerate([(0, 67), (0, 66), (-5, 100), (-3, 84), (-1, 83)])]
    # Q: 22 ticks, the bomb leaves on tick 8: a lift and back
    T["skill"] = [(frame([(fs[i % 4], 0, dy, fa)]), ms) for i, (dy, ms) in
                  enumerate([(0, 50), (-4, 50), (-8, 67), (-5, 100), (-2, 100)])]
    # E: the gatling's spin-up, 18 ticks: a shiver
    T["skill2"] = [(frame([(fs[i % 4], dx, 0, fa)]), 60) for i, dx in enumerate([0, -2, 0, -2, 0])]
    # W / the Package: 24 ticks of flight (the dash itself is the engine's MoveBack): the rotors racing
    T["skill2_w"] = [(frame([(fs[i % 4], 0, dy, fa)]), 80) for i, dy in enumerate([0, -2, -3, -2, 0])]
    # R: 16 ticks, the missile on tick 6: a lift, the kick back
    T["ult"] = [(frame([(fs[i % 4], dx, dy, fa)]), ms) for i, (dx, dy, ms) in
                enumerate([(0, 0, 50), (0, -3, 50), (-8, -3, 67), (-4, -1, 50), (0, 0, 50)])]
    T["hit"] = [(frame([(fs[0], dx, 0, fa)]), 67) for dx in (-6, -3, 0)]
    fall, crash = dr["fall"], dr["crash"]
    T["dead"] = [(frame([(fs[0], 0, 0, fa)]), 100), (frame([(fall, 0, -20, anchor_of(fall))]), 150),
                 (frame([(fall, 0, -8, anchor_of(fall))]), 150), (frame([(crash, 0, HOVER * K, anchor_of(crash))]), 120),
                 (frame([(crash, 0, HOVER * K, anchor_of(crash))]), 900)]
    return T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write corki_hd_frames.png and corki_hd_all.gif there")
    a = ap.parse_args()
    dr = drawings()
    T = tags(dr)
    one_tags, hd_tags = {}, {}
    os.makedirs(OUT_PPU, exist_ok=True)
    for tag, frames in T.items():
        ones, dens = [], []
        for d, ms in frames:
            dc, oc = crop(d, down(d))
            ones.append((oc, ms))
            dens.append((dc, ms))
        one_tags[tag], hd_tags["hd_" + tag] = ones, dens
        H = max(f.shape[0] for f, _ in dens)
        W = sum(f.shape[1] for f, _ in dens) + len(dens) - 1
        s = np.zeros((H, W, 4), np.uint8)
        x = 0
        for f, _ in dens:
            s[:f.shape[0], x:x + f.shape[1]] = f
            x += f.shape[1] + 1
        Image.fromarray(s).save(os.path.join(OUT_PPU, f"corki_{tag}.png"))
    G.write_sheet(STEM, {**one_tags, **hd_tags})
    print("written", STEM, {t: len(f) for t, f in one_tags.items()})
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        review(a.review, hd_tags)


def review(out, hd):
    """Every dense frame on one sheet (grey ground, the ground line) and one GIF of all actions."""
    rows = []
    n = (2 * HALF + 1) * K
    for tag, frames in hd.items():
        cells = []
        for f, _ in frames:
            can = np.full((n, n, 4), (225, 225, 225, 255), np.uint8)
            y0, x0 = (n - f.shape[0]) // 2, (n - f.shape[1]) // 2
            m = f[..., 3] > 0
            can[y0:y0 + f.shape[0], x0:x0 + f.shape[1]][m] = f[m]
            g = n // 2 + K * FEET + K // 2
            can[g, :, :3] = (200, 60, 60)
            cells.append(can[40:n - 120])
        rows.append(np.concatenate(cells, axis=1))
    W = max(r.shape[1] for r in rows)
    sheet = np.concatenate([np.pad(r, ((0, 0), (0, W - r.shape[1]), (0, 0)), constant_values=255) for r in rows])
    Image.fromarray(sheet).convert("RGB").save(os.path.join(out, "corki_hd_frames.png"))
    gif = []
    for tag, frames in hd.items():
        for f, ms in frames:
            can = np.full((n, n, 4), (225, 225, 225, 255), np.uint8)
            y0, x0 = (n - f.shape[0]) // 2, (n - f.shape[1]) // 2
            m = f[..., 3] > 0
            can[y0:y0 + f.shape[0], x0:x0 + f.shape[1]][m] = f[m]
            gif.append((Image.fromarray(can[40:n - 120]).convert("RGB").resize(((n) * 2, (n - 160) * 2), Image.NEAREST), ms))
    gif[0][0].save(os.path.join(out, "corki_hd_all.gif"), save_all=True, append_images=[g for g, _ in gif[1:]],
                   duration=[ms for _, ms in gif], loop=0)


if __name__ == "__main__":
    main()

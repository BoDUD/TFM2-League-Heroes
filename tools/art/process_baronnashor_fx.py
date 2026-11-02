#!/usr/bin/env python3
"""Baron Nashor's effects and icons from the one Gemini sheet the user made (2026-11-03, 「这是大龙的技能特效和技能图标
gemini做的 你导入后完善」): each frame cut from the sheet, keyed off its drawn checkerboard, brought down to the game size the
pack's prompt gave (assets/source/baronnashor/PROMPTS_FX.md), its colours cut to its own palette, made symmetric, and
written as a strip of equal cells for import_baronnashor_fx.py.

    python tools/art/process_baronnashor_fx.py [--src C:/t/bn_work/gemini/baron_fx.jpg] [--review out.png]

The sheet (2862 x 1472, JPEG; the original is the user's Downloads/Gemini_Generated_Image_33x7iz33x7iz33x7.jpg, kept out
of git like the other heroes' Gemini art): on a dark plum ground, ten panels each one effect on a DRAWN grey-and-white
checkerboard (not real alpha) under its name, then the three icons. PANELS below are the checkered boxes (read from the
sheet: the light rows and columns under each label). The checkerboard is keyed by flood: light, grey-neutral pixels
joined to the panel's edge (or in a pocket of 400+ px) are ground, so a pale core shut inside a picture stays (e_burst's
cream glow); the JPEG fringe next to the ground goes with it. A panel's pictures are its keyed pixels split where 12
empty columns part them.
The sheet drew most effects as one or two pictures; the missing frames are made from them here (fix-delivered-art-
myself): parts of a picture by colour (rocks, void light, the cream glow, the bright core), its lower rows only (spikes
rising out of the ground), shifted pieces (the teeth closing, the acid ball falling). q_acid's middle picture is a grey
stand-in figure for the unit: dropped (its left group's two outer drips beside the body, mirrored). e_hit is its right
half mirrored. The tentacles are all turned to curl right. Every picture made symmetric (left to right; q_spray top to bottom) by union
with its mirror (the client never mirrors an effect), except p_tent: a tentacle curling one way under an enemy has no
front or back toward the Baron, so it is kept as drawn (import_baronnashor_fx.py skips its check).
Writes assets/source/baronnashor/gemini_fx/pixel_1x/baronnashor_fx_<name>.png (one row of equal cells at game size,
alpha 0 / 255), gemini_fx/cells.json (each strip's frames and cell) and gemini_fx/icons/baronnashor_icon_<name>.png
(64 x 64, LANCZOS).
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
import process_brock_fx as PB  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "baronnashor", "gemini_fx")
SRC = "C:/t/bn_work/gemini/baron_fx.jpg"
lp = PB.lp

# each effect's checkered panel (x0, y0, x1, y1) on the sheet
PANELS = {
    "a_hit": (36, 73, 939, 328), "q_spray": (1004, 72, 1893, 328), "q_hit": (1957, 72, 2845, 328),
    "q_acid": (37, 418, 923, 675), "e_burst": (1000, 418, 1989, 675), "e_hit": (2060, 418, 2845, 675),
    "r_spikes": (36, 766, 1082, 1019), "r_hit": (1152, 766, 1735, 1019), "r_fall": (1811, 766, 2845, 1019),
    "p_tent": (36, 1114, 1440, 1371),
}
# the icons' tiles under their labels (the frame's rows and columns: lit across 85% of the box)
ICONS = {"skill": (1532, 1078, 1910, 1448), "skill2": (1997, 1078, 2376, 1448), "ult": (2461, 1078, 2838, 1448)}

# name -> (cell w, h at game size, "c" centre / "b" bottom, symmetry, colours)
SPEC = {
    "a_hit": (16, 16, "c", "LR", 12), "q_spray": (48, 22, "c", "TB", 12), "q_hit": (18, 18, "c", "LR", 10),
    "q_acid": (34, 16, "b", "LR", 10), "e_burst": (60, 40, "b", "LR", 16), "e_hit": (18, 20, "b", "LR", 12),
    "r_spikes": (96, 48, "b", "LR", 16), "r_hit": (18, 22, "b", "LR", 12), "r_fall": (24, 52, "b", "LR", 14),
    "p_tent": (28, 60, "b", None, 14),
}


def key(a):
    """The drawn checkerboard off: light grey-neutral pixels joined to the panel's edge (or in a big pocket), and the
    JPEG fringe beside them."""
    c = a.astype(int)
    mx, mn = c.max(2), c.min(2)
    bg = (mx - mn < 22) & (mx > 168)
    lab, n = ndimage.label(bg)
    sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
    edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    ground = np.zeros(n + 1, bool)
    for i, s in enumerate(sizes, 1):
        ground[i] = i in edge or s > 400
    g = ground[lab]
    g |= ndimage.binary_dilation(g, iterations=2) & (mx - mn < 40) & (mx > 140)
    fg = ndimage.binary_opening(~g, iterations=1)
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[..., :3] = a
    out[..., 3] = np.where(fg, 255, 0)
    return out


def pictures(rgb, name, gap=12):
    """A panel keyed, its pictures in order: (x0, x1, the keyed picture cut to its columns, full panel height)."""
    x0, y0, x1, y1 = PANELS[name]
    a = key(rgb[y0:y1, x0:x1])
    cols = (a[..., 3] > 0).any(0)
    runs, start, empty = [], None, 0
    for x, c in enumerate(cols):
        if c:
            if start is None:
                start = x
            empty = 0
        elif start is not None:
            empty += 1
            if empty >= gap:
                runs.append((start, x - empty + 1))
                start, empty = None, 0
    if start is not None:
        runs.append((start, len(cols)))
    return a, runs


def masks(a):
    """By colour: void (violet / magenta light), rock (browns), cream (the pale glow), ivory (teeth)."""
    c = a[..., :3].astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    op = a[..., 3] > 0
    void = op & (b > g + 40) & (r > g + 10)
    rock = op & (r >= g) & (g >= b - 6) & (r - b < 90) & (c.max(2) < 190) & ~void
    cream = op & (c.min(2) > 200)
    return void, rock, cream


def only(a, mask):
    out = a.copy()
    out[~mask, 3] = 0
    return out


def rows_below(a, frac):
    """Its lower `frac` of rows only (spikes / a tentacle coming up out of the ground)."""
    out = a.copy()
    out[: int(a.shape[0] * (1 - frac)), :, 3] = 0
    return out


def scaled_by(a, k):
    return np.asarray(Image.fromarray(a).resize((max(1, round(a.shape[1] * k)), max(1, round(a.shape[0] * k))),
                                                 Image.BOX))


def comps(a, least=1):
    """Its pieces (label, sizes)."""
    lab, n = ndimage.label(a[..., 3] > 0)
    return lab, ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))


def made(name, rgb):
    """The frames (full-size pictures, before the game-size shrink) of an effect."""
    a, runs = pictures(rgb, name)
    cut = lambda s, e: a[:, s:e]
    if name == "a_hit":
        # the sheet's four jaws round one burst: the first jaw open; the same jaw closed (its rows of teeth moved
        # together); the burst; the burst's streaks without its bright core
        w = a.shape[1] // 4
        jaw = PB.tight(a[:, :w])
        h = jaw.shape[0]
        top, bot = jaw[: h // 2], jaw[h // 2:]
        d = h // 5
        shut = np.zeros_like(jaw)
        shut[d: d + top.shape[0]][top[..., 3] > 0] = top[top[..., 3] > 0]
        sb = shut[h // 2 - d: h // 2 - d + bot.shape[0]]
        sb[bot[..., 3] > 0] = bot[bot[..., 3] > 0]
        mid = a[int(a.shape[0] * 0.22): int(a.shape[0] * 0.78), int(a.shape[1] * 0.3): int(a.shape[1] * 0.7)]
        void, _, _ = masks(mid)
        burst = only(mid, void)
        core = burst[..., :3].astype(int).min(2) > 170
        return [jaw, shut, burst, only(burst, ~core & (burst[..., 3] > 0))]
    if name == "q_spray":   # the gush, and the gush with its blobs and drops rolled on (its right part moved right)
        g = PB.tight(cut(*runs[0]))
        k = int(g.shape[1] * 0.42)
        rolled = np.zeros_like(g)
        rolled[:, :k] = g[:, :k]
        dx = max(2, g.shape[1] // 30)
        rolled[:, k + dx:] = g[:, k: g.shape[1] - dx]
        return [g, rolled]
    if name == "q_hit":     # the splash (its left part; the smoke wisps to its right came down to nothing): small,
        # whole, its drops without the blob
        p = PB.tight(cut(*runs[0]))
        splash = PB.tight(p[:, : int(p.shape[1] * 0.45)])
        lab, sizes = comps(splash)
        blob = lab == 1 + int(np.argmax(sizes))
        return [scaled_by(splash, 0.6), splash, only(splash, ~blob & (splash[..., 3] > 0))]
    if name == "q_acid":
        return "acid"
    if name == "e_burst":   # the void light breaking through, the whole burst, then the rocks and earth settling
        p = PB.tight(cut(*runs[0]))
        void, rock, cream = masks(p)
        return [scaled_by(only(p, void | cream), 0.55), p, only(p, ~cream & (p[..., 3] > 0)), only(p, rock)]
    if name == "e_hit":     # its right half (streaks and rocks flying up and out; the mirror adds the left): the
        # streaks small, whole, the rocks falling
        p = PB.tight(cut(*runs[1]))
        void, rock, _ = masks(p)
        return [scaled_by(only(p, void), 0.7), p, only(p, rock)]
    if name == "r_spikes":  # the glowing ring, the spikes coming up, full, cracking, sinking, the ring
        p = PB.tight(cut(*runs[0]))
        ring = rows_below(p, 0.38)
        return [ring, rows_below(p, 0.6), p, p, rows_below(p, 0.6), ring]
    if name == "r_hit":     # the spike coming up, the spike, it cracking, the shards
        pics = [PB.tight(cut(*runs[0])), PB.tight(cut(*runs[1])), PB.tight(cut(runs[2][0], runs[3][1]))]
        return [rows_below(pics[0], 0.5)] + pics
    if name == "r_fall":
        return "fall"
    if name == "p_tent":    # the hole, the tentacle rising (its pictures by height), at its full height, sinking, the hole
        pics = [curled_right(PB.tight(cut(s, e))) for s, e in runs]
        order = sorted(range(len(pics)), key=lambda i: pics[i].shape[0])
        low = pics[order[0]]
        hole = rows_below(low, 0.12)
        up = [pics[i] for i in order]
        return [hole, rows_below(up[0], 0.5)] + up + [up[-2], rows_below(up[0], 0.5), hole]
    raise KeyError(name)


def curled_right(p):
    """A tentacle turned so its curled tip leans right (the sheet drew them leaning either way: in turn they flickered)."""
    op = p[..., 3] > 0
    top = op[: p.shape[0] // 3]
    base = op[-p.shape[0] // 4:]
    tx = np.nonzero(top.any(0))[0].mean() if top.any() else 0
    bx = np.nonzero(base.any(0))[0].mean() if base.any() else 0
    return p if tx >= bx else p[:, ::-1].copy()


def acid_frames(rgb, W, H):
    """The corrosion on a unit: the sheet's left group (the grey stand-in figure in the middle and the right group left
    out) cut to its two outer drips and the puddle under them, at a size where the mirrored pair leaves the unit's body
    (16 wide) clear between them; the second frame without the loose drops and the smoke wisps (the drips seem to
    fall)."""
    a, runs = pictures(rgb, "q_acid")
    s, e = runs[0]
    side = PB.tight(a[:, s: s + int((e - s) * 0.46)])
    k = min((W - 16) / 2 / side.shape[1], H / side.shape[0])
    lab, sizes = comps(side)
    small = np.isin(lab, [i for i, sz in enumerate(sizes, 1) if sz < 900])
    cells = []
    for pic in (side, only(side, ~small & (side[..., 3] > 0))):
        p = PB.shrink(pic, k)
        c = np.zeros((H, W, 4), np.uint8)
        c[H - p.shape[0]:, : p.shape[1]][p[..., 3] > 0] = p[p[..., 3] > 0]
        cells.append(c)
    return cells


def fall_frames(rgb, W, H):
    """The falling acid ball: the first picture's ball (its shadow under it left out) at three heights, then the other
    three pictures (splashing, the splash, the puddle) on the ground; one factor for all."""
    a, runs = pictures(rgb, "r_fall")
    pics = [PB.tight(a[:, s:e]) for s, e in runs]
    lab, sizes = comps(pics[0])
    big = 1 + int(np.argmax(sizes))
    ball = PB.tight(only(pics[0], lab == big))
    # the drops over it (joined to it) read as two ears: its top rows off until a row is most of the ball's width
    width = (ball[..., 3] > 0).sum(1)
    top = int(np.argmax(width >= 0.6 * width.max()))
    ball = PB.tight(ball[max(0, top - 2):])
    k = min(W / max(p.shape[1] for p in pics), H / (2.2 * max(p.shape[0] for p in pics[1:])))
    k = min(k, W / ball.shape[1])
    b = PB.shrink(ball, k)
    cells = []
    for drop in (0, (H - b.shape[0]) // 3, 2 * (H - b.shape[0]) // 3):
        c = np.zeros((H, W, 4), np.uint8)
        PB.put(c, b, "b", -(H - b.shape[0] - drop))
        cells.append(c)
    for p in pics[1:]:
        c = np.zeros((H, W, 4), np.uint8)
        PB.put(c, PB.shrink(p, k), "b")
        cells.append(c)
    return cells


def specks(c, least=3):
    lab, sizes = comps(c)
    out = c.copy()
    for i, sz in enumerate(sizes, 1):
        if sz < least:
            out[lab == i] = 0
    return out


def build(rgb):
    out = {}
    for name, (W, H, where, sym, ncol) in SPEC.items():
        if name == "r_fall":
            cells = fall_frames(rgb, W, H)
        elif name == "q_acid":
            cells = acid_frames(rgb, W, H)
        else:
            frames = [PB.tight(f) for f in made(name, rgb)]
            if name == "a_hit":   # each its own fit: the jaw is narrower than the burst, and at the burst's factor its
                # teeth were too small to read
                fitted = [PB.scaled([f], W, H)[0] for f in frames]
            else:
                fitted = PB.scaled(frames, W, H)
            cells = []
            for f in fitted:
                c = np.zeros((H, W, 4), np.uint8)
                PB.put(c, f, where)
                cells.append(c)
        cells = PB.palette(cells, ncol)
        cells = [specks(PB.union_mirror(c, sym) if sym else c) for c in cells]
        out[name] = cells
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review", help="also write every strip at 6x here")
    a = ap.parse_args()
    rgb = np.asarray(Image.open(lp(a.src)).convert("RGB"))
    if rgb.shape[:2] != (1472, 2862):
        sys.exit(f"{a.src}: {rgb.shape[1]}x{rgb.shape[0]}, not the 2862 x 1472 sheet")
    out = build(rgb)
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    os.makedirs(lp(os.path.join(OUT, "icons")), exist_ok=True)
    meta = {}
    for name, cs in out.items():
        Image.fromarray(np.concatenate(cs, axis=1)).save(lp(os.path.join(OUT, "pixel_1x", f"baronnashor_fx_{name}.png")))
        meta[name] = {"frames": len(cs), "cell": [cs[0].shape[1], cs[0].shape[0]], "symmetry": SPEC[name][3]}
        print(f"{name:9s} {len(cs)} x {cs[0].shape[1]}x{cs[0].shape[0]}")
    with open(lp(os.path.join(OUT, "cells.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    for n, box in ICONS.items():
        PB.icon(rgb, box).save(lp(os.path.join(OUT, "icons", f"baronnashor_icon_{n}.png")))
    if a.review:
        PB.review(out, a.review)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Braum's game sheets from his dense frames (tools/art/import_braum_strips.py -> assets/source/braum/frames).

    python tools/art/rig_braum.py [--review DIR]

PPU 121 / 42 (the design's 121 rows from the crown to the soles = 42 game rows: as tall as the pack's other heroes, the
lesson of Kassadin's 37 rows - 「在游戏太小了吧」). Every frame's outer outline is grown THICK hd squares (with the drawn
one about a game pixel, like the base heroes' and the 1x pack heroes'; Kassadin's lesson: 「和原本游戏有点违和感」).
The idle breathes (Kassadin's lesson: 「可能卡萨丁像个僵尸？」): the upper body - head, torso, both arms with the far
hand on the shield's crossbar - rises BREATH hd rows over the legs and the shield as one piece (no part turned or
sheared); the squares it uncovers take the colour of the square under them (the belt's row repeated over the waist,
the crossbar's top under the lifted hand). The run is league_nautilus's approved walk on the idle (walk_frame / WALK):
the idle's own legs lifted in turn under the same body and shield - Codex's run (its step-2 strips and the crossing-step
redraw in codex_run) kept one leg in front in every frame (the user: 「怎么感觉腿不换位？」), and bone-drawn legs came out
deformed (「腿都变形了哥 现在这么多做好的英雄你不会参考吗」).
Writes:
  league/champions/league_braum#sheet.png / #anim.fanim - the 1x tags (each hd frame brought down by PPU, every 1x
      pixel the commonest colour of its squares; the fallback without league.dll), frames centred on the pivot
  assets/source/ppu/braum_<tag>.png + .json - the hd frames (ppu_hd.py's drawn strips: one row, 1 px gaps)
Then tools/art/ppu_hd.py --hero braum adds the hd_ tags (PPU["braum"]).
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_braum_strips as I  # noqa: E402

PPU = 121 / 42                    # 2.881: the design's 121 rows = 42 game rows
FEET = 11                         # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes)
STEM = os.path.join(ROOT, "league", "champions", "league_braum")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu", "orig")  # the dense frames as drawn; tools/art/ppu_restyle.py makes the strips ppu_hd.py reads from them (2026-10-13)
FRAMES = os.path.join(ROOT, "assets", "source", "braum", "frames")
OUTLINE = (6, 5, 5)
THICK = 2                         # the outer outline grown by 2 hd squares: with the drawn one 3 / 2.88 = ~1 game px
WAIST = 60                        # the design's belt row: the upper body above it (and the near arm below it) breathes
BAR_TOP = 29                      # the shield crossbar's top row under the far hand
BREATH = [0, 1, 2, 2, 1, 0]
# On the battlefield he is drawn at SIZE of the 1x size (addons/league_main/src/hd.rs SIZES; the user: 「布隆做的也有点大
# 得缩小一点」 - 43 game rows with the shield beside him: 85%, then 「稍微调大点」 - 90%, 39 rows), scaled about his position, so every
# hd frame is drawn SHIFT hd rows lower: the soles, (FEET + 0.5) x PPU under the pivot, land (33.1 + SHIFT) x SIZE =
# 33.1 under it again (league_gragas's way, tools/art/ppu_gragas.py). A frame without SHIFT clear rows under the soles
# grows SHIFT rows at both ends first (its centre, the pivot, kept).
SIZE = 0.90
SHIFT = round((FEET + 0.5) * PPU * (1 / SIZE - 1))


def ms(ticks):
    return ticks * 1000.0 / 60.0


def upper_mask(d):
    """The design's upper body: everything above WAIST left of the shield (column 70), the near arm down to its fist
    (columns < 20 above row 80), and the far arm lying on the crossbar: everything above the crossbar's top (row
    BAR_TOP) between columns 56 and 112, plus the fingers' skin over the bar (rows BAR_TOP-36, columns 84-112) with the
    outline squares touching them."""
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:H, 0:W]
    r, g, b = (d[..., i].astype(int) for i in range(3))
    skin = (r > 150) & (g > 80) & (g < 200) & (b < 170) & (r - b > 40)
    dark = r + g + b < 60
    up = op & (((yy < WAIST) & (xx < 70)) | ((xx < 20) & (yy < 80)))
    arm = op & (yy < BAR_TOP) & (xx >= 56) & (xx <= 112)
    fingers = op & skin & (yy >= BAR_TOP) & (yy <= 36) & (xx >= 84) & (xx <= 112)
    ink = op & dark & (yy >= BAR_TOP) & (yy <= 37) & (xx >= 84) & (xx <= 112) &         ndimage.binary_dilation(fingers, structure=np.ones((3, 3)))
    return up | arm | fingers | ink


def breathe(can, mask, k):
    """The masked squares moved k rows up; the squares they uncover take the colour of the square under them."""
    if k == 0:
        return can.copy()
    out = can.copy()
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    rest = out.copy()
    out[ys - k, xs] = can[ys, xs]
    hole = (out[..., 3] == 0) & mask
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            below = y + 1
            while below < can.shape[0] and out[below, x, 3] == 0 and mask[below, x]:
                below += 1
            if below < can.shape[0] and rest[below, x, 3] > 0:
                out[y, x] = rest[below, x]
            elif below < can.shape[0] and out[below, x, 3] > 0:
                out[y, x] = out[below, x]
    return out


def thick(can):
    """The outer outline grown outward by THICK hd squares (the drawn outline and everything inside kept)."""
    op = can[..., 3] > 0
    ring = ndimage.binary_dilation(op, structure=np.ones((3, 3)), iterations=THICK) & ~op
    out = can.copy()
    out[ring, :3] = OUTLINE
    out[ring, 3] = 255
    return out


def down(can):
    """The hd canvas -> (the 1x frame centred on the pivot, the hd frame of round(PPU x its size)). The outline is
    thickened first. The pivot: column PIV_X's centre, FEET 1x rows above the soles' bottom edge. Every 1x pixel takes
    the commonest colour of the hd squares under it (clear when most of them are clear)."""
    can = thick(can)
    px, py = I.PIV_X + 0.5, I.SOLE + 1 - FEET * PPU
    ys, xs = np.nonzero(can[..., 3])
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() * 2 < len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    W, H = round(w1 * PPU), round(h1 * PPU)
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sy0, sx0 = max(0, hy0), max(0, hx0)
    sub = can[sy0:hy0 + H, sx0:hx0 + W]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return one, hd


# the run: league_nautilus's approved walk (tools/art/fix_nautilus_strips2.py walk_frame / WALK: the user,
# 「腿都变形了哥 现在这么多做好的英雄你不会参考吗」 after Codex's run kept one leg in front in every frame and a bone-drawn
# leg came out deformed). The idle's body, the shield, the head and both legs as they are - the legs cut under the hip
# band (row LEG_BAND of the design) into the near leg (columns up to LEG_SPLIT) and the far one (to the shield's edge
# SHIELD_EDGE); in each frame a leg is lifted by losing its top rows (the thigh turned toward us) and moved forward, the
# legs take turns, and the whole figure rises a little; no part turned or stretched.
LEG_BAND = 78                    # the design's row under the hip band: the legs start below it
LEG_SPLIT = 43                   # the column between the legs
SHIELD_EDGE = 70                 # the shield's left outline column: the far leg ends left of it
# per frame: the near leg's (columns forward, rows lifted), the far leg's, the figure's rise (hd squares: league_nautilus's
# 1x steps x 3)
WALK = [((0, 0), (0, 6), 3), ((0, 0), (3, 9), 6), ((0, 0), (3, 3), 3), ((0, 0), (3, 0), 0),
        ((0, 6), (0, 0), 3), ((3, 9), (0, 0), 6), ((3, 3), (0, 0), 3), ((3, 0), (0, 0), 0)]
WALK_MS = 115
CRACK = 80                       # enclosed gaps this small that a step opens are cracks, filled with the outline


def walk_frame(idle, near_step, far_step, rise):
    """The idle canvas with the legs stepping: each leg's squares under the band moved (dx, -lift) after losing their
    top `lift` rows; the far leg first, the near one over it, the body over both; the whole frame `rise` rows up."""
    x0, y0 = I.DESIGN_AT
    band = y0 + LEG_BAND
    H, W = idle.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    op = idle[..., 3] > 0
    near = op & (yy > band) & (xx <= x0 + LEG_SPLIT)
    far = op & (yy > band) & (xx > x0 + LEG_SPLIT) & (xx < x0 + SHIELD_EDGE)
    out = idle.copy()
    out[near | far] = 0
    body = out.copy()
    out[:] = 0
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        leg = np.where(m[..., None], idle, 0).astype(np.uint8)
        leg[:band + 1 + lift] = 0
        ys, xs = np.nonzero(leg[..., 3] > 0)
        ok = (ys - lift >= 0) & (xs + dx < W)
        out[ys[ok] - lift, xs[ok] + dx] = leg[ys[ok], xs[ok]]
    m = body[..., 3] > 0
    out[m] = body[m]
    # cracks the step opened (the far leg moved toward the shield's outline: the idle's gap between them squeezed to
    # slivers): enclosed gaps of at most CRACK squares, new ones or at most 3 columns wide, take the outline (gap-check)
    opq = out[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    own = ndimage.binary_fill_holes(idle[..., 3] > 0) & ~(idle[..., 3] > 0)
    for j in range(1, n + 1):
        hole = lab == j
        xs = np.nonzero(hole.any(0))[0]
        if hole.sum() <= CRACK and (xs.max() - xs.min() < 3 or not (hole & own).any()):
            out[hole] = (*OUTLINE, 255)
    return np.roll(out, -rise, axis=0)


def lower(hd):
    """The hd frame moved SHIFT rows down (grown SHIFT rows at both ends first when its soles have no room)."""
    if not SHIFT:
        return hd
    rows = np.nonzero(hd[..., 3].any(1))[0]
    if hd.shape[0] - 1 - rows.max() < SHIFT:
        hd = np.pad(hd, ((SHIFT, SHIFT), (0, 0), (0, 0)))
    out = np.zeros_like(hd)
    out[SHIFT:] = hd[:-SHIFT]
    return out


def actions():
    """{tag: [(hd canvas, ms)]}: the imported frames, the idle breathing."""
    fr = json.load(open(os.path.join(FRAMES, "frames.json"), encoding="utf-8"))
    load = lambda n: np.asarray(Image.open(os.path.join(FRAMES, n)).convert("RGBA")).copy()
    out = {}
    idle = load(fr["idle"][0][0])
    d = np.asarray(Image.open(I.DESIGN).convert("RGBA"))
    mask = np.zeros(idle.shape[:2], bool)
    x0, y0 = I.DESIGN_AT
    mask[y0:y0 + d.shape[0], x0:x0 + d.shape[1]] = upper_mask(d)
    out["idle"] = [(breathe(idle, mask, k), ms(10)) for k in BREATH]
    out["run"] = [(walk_frame(idle, n_, f_, r_), WALK_MS) for n_, f_, r_ in WALK]
    for tag in ("attack", "skill", "skill2", "w_leap", "ult", "hit", "dead"):
        out[tag] = [(load(n), t) for n, t in fr[tag]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's hd frames at 3x here")
    a = ap.parse_args()
    acts = actions()
    sheet = {}
    os.makedirs(PPU_SRC, exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, t in frames:
            one, hd = down(can)
            hd = lower(hd)
            ones.append((one, round(t, 3)))
            hds.append(hd)
        sheet[tag] = ones
        H = max(h.shape[0] for h in hds)
        strip = np.zeros((H, sum(h.shape[1] + 1 for h in hds) - 1, 4), np.uint8)
        x = 0
        for h in hds:
            strip[:h.shape[0], x:x + h.shape[1]] = h
            x += h.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(PPU_SRC, f"braum_{tag}.png"))
        with open(os.path.join(PPU_SRC, f"braum_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds]}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 3
            tiles = [Image.fromarray(thick(c[0])) for c in frames]
            w, h = tiles[0].size
            big = Image.new("RGBA", (len(tiles) * w * Z, h * Z), (96, 112, 96, 255))
            for k, t in enumerate(tiles):
                big.alpha_composite(t.resize((w * Z, h * Z), Image.NEAREST), (k * w * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"braum_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_braum#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()

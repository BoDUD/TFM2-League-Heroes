#!/usr/bin/env python3
"""Nidalee's game sheets from her dense frames (tools/art/import_nidalee_strips.py -> assets/source/nidalee/frames).

    python tools/art/rig_nidalee.py [--review DIR]

PPU 159 / 41.5 (the huntress's 159 rows from the ponytail's top to the soles = 41.5 game rows, as tall as the pack's other
heroes). Both forms are in one sheet: the huntress's tags and the cougar's c_* (league_kayn's way; the data plays the
cougar's casts by CasterAnimation, the add-on addons/league_nidalee swaps idle / run / hit / dead to c_idle ...).
  idle / c_idle  the design breathing (Kassadin's lesson: 「可能卡萨丁像个僵尸？」): the huntress's upper body above WAIST
                 (her javelin and the far hand on it left where they are, columns from SPEAR on) and the cougar's body above
                 its legs (C_LEGS) rise BREATH dense rows as one piece; the squares they uncover take the colour of the
                 square under them;
  hit / c_hit    the design moved HIT_DX back with a white flash on the first frame;
  run            league_braum's approved walk on her design (import_nidalee_strips.walk_frame);
  the rest       Codex's frames as imported.
The look follows league_zeri's (the user: 「按泽丽标准」, 2026-10-13): these frames are the ones as drawn, written to
assets/source/ppu/orig/nidalee_<tag>.png (ppu 3.83); tools/art/ppu_restyle.py (RESTYLE["nidalee"]) brings them to about
2.2 squares a game pixel, the outline about a game pixel, and writes the strips tools/art/ppu_hd.py reads.
Writes league/champions/league_nidalee#sheet.png / #anim.fanim: the 1x tags (each dense frame brought down by PPU, every
1x pixel the commonest colour of its squares; the fallback without league.dll), frames centred on the pivot.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_nidalee_strips as I  # noqa: E402

PPU = round(159 / 41.5, 4)        # 3.8313
FEET = 11                         # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes)
STEM = os.path.join(ROOT, "league", "champions", "league_nidalee")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
FRAMES = os.path.join(ROOT, "assets", "source", "nidalee", "frames")
WAIST = 100                       # the huntress design's row under the loincloth's belt: the upper body above it breathes
SPEAR = 76                        # her far forearm, hand and javelin (design columns from here) stay
C_LEGS = 72                       # the cougar design's row where the legs start
BREATH = [0, 1, 2, 2, 1, 0]
BREATH_MS = 170
HIT_DX = 4
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]


def load(name):
    return np.asarray(Image.open(os.path.join(FRAMES, name)).convert("RGBA")).copy()


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


def upper(form):
    """The breathing part of a form's design on the canvas."""
    can = I.canvas(form)
    x0, y0 = I.FORMS[form]["at"]
    op = can[..., 3] > 0
    yy, xx = np.mgrid[0:can.shape[0], 0:can.shape[1]]
    if form == "human":
        return can, op & (yy < y0 + WAIST) & (xx < x0 + SPEAR)
    return can, op & (yy < y0 + C_LEGS)


def hit(can, dx, flash):
    out = np.roll(can, -dx, axis=1)
    if flash:
        m = out[..., 3] > 0
        out[m, :3] = (out[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
    return out


def down(can, piv):
    """The dense canvas -> (the 1x frame centred on the pivot, the dense frame of round(PPU x its size)). The pivot:
    column piv's centre, FEET 1x rows above the soles' bottom edge. Every 1x pixel takes the commonest colour of the
    dense squares under it (clear when most of them are clear)."""
    px, py = piv + 0.5, I.SOLE + 1 - FEET * PPU
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
    one = G.complete_outline(one)[0]
    W, H = round(w1 * PPU), round(h1 * PPU)
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return one, hd


def actions():
    """{tag: [(dense canvas, ms, form)]}."""
    fr = json.load(open(os.path.join(FRAMES, "frames.json"), encoding="utf-8"))
    out = {}
    for form, pre in (("human", ""), ("cougar", "c_")):
        can, mask = upper(form)
        out[pre + "idle"] = [(breathe(can, mask, k), BREATH_MS, form) for k in BREATH]
        out[pre + "hit"] = [(hit(can, dx, fl), ms, form) for dx, fl, ms in HIT]
    for tag, frames in fr.items():
        form = "cougar" if tag.startswith("c_") else "human"
        out[tag] = [(load(n), ms, form) for n, ms in frames]
    order = ["idle", "run", "attack", "skill", "skill2", "transform", "hit", "dead",
             "c_idle", "c_run", "c_attack", "c_skill", "c_pounce", "c_swipe", "c_transform", "c_hit", "c_dead"]
    return {t: out[t] for t in order}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's dense frames at 3x here")
    a = ap.parse_args()
    acts = actions()
    sheet = {}
    os.makedirs(ORIG, exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, t, form in frames:
            one, hd = down(can, I.FORMS[form]["piv"])
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        H = max(h.shape[0] for h in hds)
        strip = np.zeros((H, sum(h.shape[1] + 1 for h in hds) - 1, 4), np.uint8)
        x = 0
        for h in hds:
            strip[:h.shape[0], x:x + h.shape[1]] = h
            x += h.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(ORIG, f"nidalee_{tag}.png"))
        with open(os.path.join(ORIG, f"nidalee_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 3
            tiles = [Image.fromarray(c[0]) for c in frames]
            w, h = tiles[0].size
            big = Image.new("RGBA", (len(tiles) * w * Z, h * Z), (96, 112, 96, 255))
            for k, t in enumerate(tiles):
                big.alpha_composite(t.resize((w * Z, h * Z), Image.NEAREST), (k * w * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"nidalee_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_nidalee#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()

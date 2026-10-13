#!/usr/bin/env python3
"""Nilah's game sheets from her dense frames (tools/art/import_nilah_strips.py and tools/art/run_nilah.py ->
assets/source/nilah/frames) - league_nidalee's way (tools/art/rig_nidalee.py).

    python tools/art/rig_nilah.py [--review DIR]

PPU 2.5: the user kept her design's 99 squares from the blade's tip to the soles 1:1 (2026-10-13, 「保留 99 格，PPU 2.5」),
about 40 game rows like Karma and Zeri, shown at 90 % (hd.rs SIZES, 「模型别太大」). Tags:
  idle   the front design (3/4 front, assets/source/nilah/hd/front.png) breathing (Kassadin's lesson: 「可能卡萨丁像个
         僵尸？」): everything above WAIST rises BREATH dense rows as one piece, the squares it uncovers take the colour of
         the square under them;
  hit    the side design moved HIT_DX back with a white flash on the first frame (the actions are side-on);
  the rest  the frames as drawn (frames.json: run, attack, attack_q, skill, q_spin, skill2, w_cast, ult, dead).
The look follows league_zeri's (「按泽丽标准」): these frames are the ones as drawn, written to
assets/source/ppu/orig/nilah_<tag>.png (ppu 2.5); tools/art/ppu_restyle.py (RESTYLE["nilah"]) grows the outer outline
to two squares (about a game pixel, as on Zeri, Nidalee, Soraka, Karma) and lowers the frames for the 90 %, and writes
the strips tools/art/ppu_hd.py reads.
Writes league/champions/league_nilah#sheet.png / #anim.fanim: the 1x tags (each dense frame brought down by PPU, every
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
import import_nilah_strips as I  # noqa: E402

PPU = 2.5
FEET = 11                         # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes)
STEM = os.path.join(ROOT, "league", "champions", "league_nilah")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
FRAMES = I.OUT
FRONT = os.path.join(I.SRC, "hd", "front.png")
FRONT_SOLE, FRONT_MID = 115, 42   # the front design's last row (the soles' outline) and its standing column
WAIST = 76                        # the front design's row under the sash: the upper body above it breathes
BREATH = [0, 1, 2, 2, 1, 0]
BREATH_MS = 170
HIT_DX = 4
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
ORDER = ["idle", "run", "attack", "attack_q", "skill", "q_spin", "skill2", "w_cast", "ult", "hit", "dead"]


def load(name):
    return np.asarray(Image.open(os.path.join(FRAMES, name)).convert("RGBA")).copy()


def front_canvas():
    """The front design on the frames' canvas: its soles on SOLE, its standing column on PIV."""
    d = np.asarray(Image.open(FRONT).convert("RGBA"))
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    ox, oy = I.PIV - FRONT_MID, I.SOLE - FRONT_SOLE
    ys, xs = np.nonzero(d[..., 3] > 0)
    can[ys + oy, xs + ox] = d[ys, xs]
    return can, oy


def side_canvas():
    d = I.design()
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    ys, xs = np.nonzero(d[..., 3] > 0)
    can[ys + I.AT[1], xs + I.AT[0]] = d[ys, xs]
    return can


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
    """{tag: [(dense canvas, ms)]} in ORDER."""
    fr = json.load(open(os.path.join(FRAMES, "frames.json"), encoding="utf-8"))
    out = {}
    front, oy = front_canvas()
    yy = np.mgrid[0:front.shape[0], 0:front.shape[1]][0]
    mask = (front[..., 3] > 0) & (yy < oy + WAIST)
    out["idle"] = [(breathe(front, mask, k), BREATH_MS) for k in BREATH]
    side = side_canvas()
    out["hit"] = [(hit(side, dx, fl), ms) for dx, fl, ms in HIT]
    for tag, frames in fr.items():
        out[tag] = [(load(n), ms) for n, ms in frames]
    missing = [t for t in ORDER if t not in out]
    if missing:
        sys.exit(f"no frames for {missing}")
    return {t: out[t] for t in ORDER}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's dense frames at 3x here")
    a = ap.parse_args()
    acts = actions()
    sheet = {}
    os.makedirs(ORIG, exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, t in frames:
            one, hd = down(can, I.PIV)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        H = max(h.shape[0] for h in hds)
        strip = np.zeros((H, sum(h.shape[1] + 1 for h in hds) - 1, 4), np.uint8)
        x = 0
        for h in hds:
            strip[:h.shape[0], x:x + h.shape[1]] = h
            x += h.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(ORIG, f"nilah_{tag}.png"))
        with open(os.path.join(ORIG, f"nilah_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 3
            tiles = [Image.fromarray(c[0]) for c in frames]
            w, h = tiles[0].size
            big = Image.new("RGBA", (len(tiles) * w * Z, h * Z), (96, 112, 96, 255))
            for k, t in enumerate(tiles):
                big.alpha_composite(t.resize((w * Z, h * Z), Image.NEAREST), (k * w * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"nilah_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_nilah#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()

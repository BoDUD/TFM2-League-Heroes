#!/usr/bin/env python3
"""Kassadin's action frames, posed from the approved PPU design (no Codex strips: the user, 「动作帧你可以照着画吧？」).

    python tools/art/rig_kassadin.py [--review DIR]

The design (tools/art/design_kassadin_hd.py, approved 「可以了 你继续吧」): front A for the idle, side A for every action,
both without the blade (design_kassadin_hd.base_views) - the Nether Blade is drawn per frame by
design_kassadin_hd.blade at the near hand, pointing at a multiple of 45 degrees, always straight. The rules the user
holds every rig to (memories rig-deformation-checks, fix-only-what-is-reported, one-face-all-frames): no part is
turned, sheared or stretched - the body moves only as a whole (whole squares), so the mask, the hoses, the arms and the
robe are the design's square for square in every frame; the blade turns about the hand (an energy blade, League's
voidblade_glow). He has no legs (the robe to the ground): the run is League's glide - the whole figure bobbing.
Riftwalk and the death: the figure recoloured toward the void (TINT) and, dying, dissolving into it from the head down
(a fixed per-square order), no squashing.
Writes:
  league/champions/league_kassadin#sheet.png / #anim.fanim - the 1x tags (each hd frame brought down by PPU, every 1x
      pixel the commonest colour of its squares; the fallback without league.dll), frames centred on the pivot
  assets/source/ppu/kassadin_<tag>.png + .json - the hd frames (ppu_hd.py's drawn strips: one row, 1 px gaps)
Then tools/art/ppu_hd.py --hero kassadin adds the hd_ tags (PPU["kassadin"]).
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
import design_kassadin_hd as D  # noqa: E402

PPU = 3.622                       # 134 design rows / 37 game rows (the user's pick)
FEET = 11                         # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes: 88 -> 99)
STEM = os.path.join(ROOT, "league", "champions", "league_kassadin")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")
CAN = 220                         # the hd canvas (square), the pivot at its middle column
GROUND = 190                      # the hd row under the robe (the soles' line)
VOID = np.array([108, 40, 196], float)      # Riftwalk's tint
DARK = np.array([30, 8, 56], float)
WHITE = np.array([255, 255, 255], float)


def ms(ticks):
    return ticks * 1000.0 / 60.0


def robe_mid(a):
    """The middle column of the robe's lowest 10 rows."""
    ys, xs = np.nonzero(a[..., 3])
    low = ys >= ys.max() - 9
    return (xs[low].min() + xs[low].max()) / 2.0


def hand_base(view):
    return D.BLADE[view][0]


class Rig:
    def __init__(self):
        self.views = D.base_views()
        self.place = {}
        for v, a in self.views.items():
            ys, xs = np.nonzero(a[..., 3])
            # the design's top-left on the canvas: the robe's middle on the pivot column, its lowest row on GROUND - 1
            self.place[v] = (int(round(CAN / 2 - robe_mid(a))), GROUND - 1 - int(ys.max()))

    def frame(self, view, dx=0, dy=0, blade=(1, 1), length=32, bright=False, tint=None, dissolve=0.0, flash=0.0,
              keep_rows=None):
        """One hd frame on the canvas: the view moved by (dx, dy) whole squares, the blade, then the recolouring."""
        a = self.views[view]
        can = np.zeros((CAN, CAN, 4), np.uint8)
        x0, y0 = self.place[view]
        x0, y0 = x0 + dx, y0 + dy
        h, w = a.shape[:2]
        can[y0:y0 + h, x0:x0 + w] = a
        if blade is not None:
            bx, by = hand_base(view)
            can = D.blade(can, (bx + x0, by + y0), length, blade, bright=bright, crop=False)
        op = can[..., 3] > 0
        rgb = can[..., :3].astype(float)
        if tint:                                   # toward the void: violet, then a dark violet silhouette
            lum = rgb @ np.array([0.3, 0.55, 0.15]) / 255.0
            target = DARK[None] + (VOID - DARK)[None] * lum[..., None] * 1.6
            rgb[op] = rgb[op] * (1 - tint) + np.clip(target[op], 0, 255) * tint
        if flash:
            rgb[op] = rgb[op] * (1 - flash) + WHITE * flash
        can[..., :3] = np.clip(rgb, 0, 255).round().astype(np.uint8)
        if dissolve:
            ys, xs = np.nonzero(op)
            top = ys.min()
            hgt = max(1, ys.max() - top)
            bx_, by_ = xs // 4, ys // 4                         # 4 x 4 squares go together (about a game pixel)
            r = ((bx_ * 73856093) ^ (by_ * 19349663)) % 1000 / 1000.0
            order = 0.55 * r + 0.45 * (ys - top) / hgt        # the head first, the robe's hem last
            gone = order < dissolve
            if keep_rows is not None:
                gone |= ys < GROUND - keep_rows
            can[ys[gone], xs[gone]] = 0
        return can


def down(can):
    """The hd canvas -> (the 1x frame centred on the pivot, the hd frame of round(PPU x its size)).
    The pivot: canvas column CAN / 2, FEET 1x rows above GROUND. Every 1x pixel takes the commonest colour of the hd
    squares under it (clear when most of them are clear)."""
    px, py = CAN / 2.0, GROUND - FEET * PPU
    ys, xs = np.nonzero(can[..., 3])
    # half sizes in 1x pixels round the pivot pixel (its centre on the pivot)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))]
            blk = blk.reshape(-1, 4)
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


def actions(r):
    """{tag: [(hd canvas, ms)]} - the moves, the blade's direction and the timings (the kit's ticks)."""
    F, S = "front", "side"
    UP, FWD, DOWN, VERT_DN = (1, -1), (1, 0), (1, 1), (0, 1)
    out = {}
    # idle: the front design standing still, the blade's rim lighting up and down (no breathing: the user's still idles)
    out["idle"] = [(r.frame(F), ms(10)), (r.frame(F), ms(10)), (r.frame(F, bright=True), ms(10)),
                   (r.frame(F, bright=True), ms(10))]
    # run: League's glide - the whole figure floating up and down two squares, twice a loop
    bob = [0, -1, -2, -1, 0, -1, -2, -1]
    out["run"] = [(r.frame(S, dy=b), ms(5)) for b in bob]
    # attack (24 ticks, the hit on tick 8): the blade raised up-forward, swung through forward to down-forward on the
    # hit as he steps in 3 squares, then back
    swing = [(-1, UP, 4), (1, FWD, 4), (3, DOWN, 6), (2, DOWN, 6), (0, DOWN, 4)]
    out["attack"] = [(r.frame(S, dx=x, blade=b), ms(t)) for x, b, t in swing]
    # attack_w: Nether Blade's strike - the same swing, the blade longer and its whole rim lit
    out["attack_w"] = [(r.frame(S, dx=x, blade=b, length=40, bright=True), ms(t)) for x, b, t in swing]
    # skill Q (24 ticks, the orb on tick 8): the blade raised up-forward, lowered to point at the target as he leans in
    # (never straight up: from the wrist it would cross the forearm)
    q = [(-1, UP, 4), (0, UP, 4), (2, FWD, 6), (1, FWD, 6), (0, DOWN, 4)]
    out["skill"] = [(r.frame(S, dx=x, blade=b), ms(t)) for x, b, t in q]
    # skill2 E (24 ticks, the pulse on tick 8): drawn back gathering (the blade straight down), thrust forward
    e = [(-2, VERT_DN, 4), (-2, VERT_DN, 4), (3, FWD, 6), (2, FWD, 6), (0, DOWN, 4)]
    out["skill2"] = [(r.frame(S, dx=x, blade=b), ms(t)) for x, b, t in e]
    # ult R (24 ticks, he vanishes on tick 6): turning to void, a dark silhouette over the jump, back to himself
    rr = [(0.0, 3), (0.5, 3), (0.95, 6), (0.5, 6), (0.0, 6)]
    out["ult"] = [(r.frame(S, blade=UP if k == 0 else DOWN, tint=t), ms(d)) for k, (t, d) in enumerate(rr)]
    # hit: knocked back 2 squares with a white flash, then 1
    out["hit"] = [(r.frame(S, dx=-2, flash=0.35), ms(6)), (r.frame(S, dx=-1), ms(6))]
    # dead: turning to void and dissolving into it from the head down, a game pixel at a time; the empty robe's hem
    # (its lowest 16 rows) is left on the ground
    d = [(0, 0.0, 0.0, None, 6), (-1, 0.5, 0.0, None, 6), (-1, 0.9, 0.3, None, 8), (-1, 0.9, 0.55, None, 8),
         (-1, 0.95, 0.0, 16, 10), (-1, 0.95, 0.0, 16, 60)]
    out["dead"] = [(r.frame(S, dx=x, blade=None if k >= 2 else DOWN, tint=t, dissolve=v or (1e-9 if keep else 0),
                             keep_rows=keep), ms(tk)) for k, (x, t, v, keep, tk) in enumerate(d)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's hd frames at 3x here")
    a = ap.parse_args()
    r = Rig()
    acts = actions(r)
    sheet = {}
    os.makedirs(PPU_SRC, exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, t in frames:
            one, hd = down(can)
            ones.append((one, round(t, 3)))
            hds.append(hd)
        sheet[tag] = ones
        H = max(h.shape[0] for h in hds)
        strip = np.zeros((H, sum(h.shape[1] + 1 for h in hds) - 1, 4), np.uint8)
        x = 0
        for h in hds:
            strip[:h.shape[0], x:x + h.shape[1]] = h
            x += h.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(PPU_SRC, f"kassadin_{tag}.png"))
        with open(os.path.join(PPU_SRC, f"kassadin_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds]}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 3
            tiles = [Image.fromarray(c[0]) for c in frames]
            big = Image.new("RGBA", (len(tiles) * CAN * Z, CAN * Z), (104, 112, 72, 255))
            for k, t in enumerate(tiles):
                big.alpha_composite(t.resize((CAN * Z, CAN * Z), Image.NEAREST), (k * CAN * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"kassadin_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_kassadin#sheet.png {w}x{h}: " +
          ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()

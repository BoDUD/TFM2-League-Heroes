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
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import design_kassadin_hd as D  # noqa: E402
import design_riven as R  # noqa: E402

PPU = 3.622                       # 134 design rows / 37 game rows (the user's pick)
FEET = 11                         # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes: 88 -> 99)
STEM = os.path.join(ROOT, "league", "champions", "league_kassadin")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")
CAN = 220                         # the hd canvas (square), the pivot at its middle column
GROUND = 190                      # the hd row under the robe (the soles' line)
VOID = np.array([108, 40, 196], float)      # Riftwalk's tint
DARK = np.array([30, 8, 56], float)
WHITE = np.array([255, 255, 255], float)
OUTLINE = np.array([12, 9, 19])
ARM_ELBOW = (66, 62)              # the front design's far elbow (the arm unit turns about it)
SIDE_ELBOW = (62, 64)             # where it sits in the side design: the front hand then lands on the side hand
RAISED_ELBOW = (72, 64)           # raised, the elbow at the chest's front edge: the hand clear of the mask (x <= 80)
BELT = 92                         # the death's collapse: the side design's rows above this (both hands, the belt and
                                  # the robe's top) sink as one; the cloth below piles up


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

    # ---------------------------------------------------------------- the swinging arm (the attack)
    def arm(self, length=32, bright=False):
        """The front design's far forearm, hand and blade as one rigid unit on a square canvas, the elbow at its
        centre (ARM_ELBOW). The forearm: the bracer from the elbow down to the hand (rows 59-86, from column 63; the
        upper arm's and the torso's cyan left of column 76 excluded) - the front view shows it whole; in the side view
        it hides behind the belt plate."""
        f = self.views["front"]
        H, W = f.shape[:2]
        ys, xs = np.mgrid[0:H, 0:W]
        rgb = f[..., :3].astype(int)
        cyan = (rgb[..., 1] > 100) & (rgb[..., 2] > 100) & (rgb[..., 0] < 140)
        keep = (f[..., 3] > 0) & (ys >= 59) & (ys <= 86) & (xs >= 63) & ~(cyan & (xs < 76)) & ~((ys < 66) & (xs < 67))
        # only the forearm itself: the biggest 8-connected piece (a bracer spike cut off by the box floated loose)
        lab, n = ndimage.label(keep, structure=np.ones((3, 3)))
        if n > 1:
            keep = lab == (1 + int(np.argmax(ndimage.sum(keep, lab, range(1, n + 1)))))
        ex, ey = ARM_ELBOW
        R_ = 70
        can = np.zeros((2 * R_ + 1, 2 * R_ + 1, 4), np.uint8)
        yy, xx = np.nonzero(keep)
        can[yy - ey + R_, xx - ex + R_] = f[yy, xx]
        bx, by = D.BLADE["front"][0]
        can = D.blade(can, (bx - ex + R_, by - ey + R_), length, (1, 1), bright=bright, crop=False)
        return can, R_

    def side_no_hand(self):
        """The side design without its far hand (it sticks out in front of the robe from column 75, rows 66-86): the
        hand's whole cyan family - its teal outline (12, 71, 89) too - goes; the robe's front edge is closed again with
        the design's outline."""
        a = self.views["side"].copy()
        H, W = a.shape[:2]
        ys, xs = np.mgrid[0:H, 0:W]
        a[(xs >= 75) & (ys >= 66) & (ys <= 86) & teal(a)] = 0
        a, _, _ = G.complete_outline(a, color=tuple(int(v) for v in OUTLINE))
        return a

    def swing(self, k, dx=0, elbow=SIDE_ELBOW, length=32, bright=False):
        """An attack frame: the body (the side design without its far hand) moved dx, the arm unit turned k quarter
        turns (1 = counter-clockwise: raised up and forward) about its elbow at `elbow` (side design squares), drawn
        BEHIND the body - the far arm: as in the design, the forearm hides behind the belt plate and only what reaches
        past the body shows."""
        body = self.side_no_hand()
        can = np.zeros((CAN, CAN, 4), np.uint8)
        x0, y0 = self.place["side"]
        x0 += dx
        unit, R_ = self.arm(length, bright)
        unit = np.ascontiguousarray(np.rot90(unit, k))
        ex, ey = elbow
        cx, cy = x0 + ex - R_, y0 + ey - R_
        yy, xx = np.nonzero(unit[..., 3])
        ok = (yy + cy >= 0) & (yy + cy < CAN) & (xx + cx >= 0) & (xx + cx < CAN)
        can[yy[ok] + cy, xx[ok] + cx] = unit[yy[ok], xx[ok]]
        h, w = body.shape[:2]
        sub = can[y0:y0 + h, x0:x0 + w]
        op = body[..., 3] > 0
        sub[op] = body[op]
        return can

    # ---------------------------------------------------------------- the death (League's collapse)
    def collapse(self, sink, dx=0, blade=True):
        """A death frame (League's Death: he sinks where he stands, the robe piling on the ground): the upper body (the
        side design's rows above BELT: the head, both arms and hands, the belt, the robe's top) moved down `sink`
        rows over the robe's lower tiers, which stay as they are (no row of anything is cut or squeezed: squeezed rows
        thinned the trailing tip to a line); where the lower tier now stands out beside the sunk upper part its cut
        top edge gets the design's outline. Then the blade at the hand where it went (blade=False: gone)."""
        a = self.views["side"]
        H, W = a.shape[:2]
        ys, xs = np.mgrid[0:H, 0:W]
        op = a[..., 3] > 0
        upper = (ys < BELT) & op
        low = ~upper & op
        out = np.zeros_like(a)
        out[low] = a[low]                                        # the lower tiers where they stood
        uy, ux = np.nonzero(upper)
        ok = uy + sink < H
        out[uy[ok] + sink, ux[ok]] = a[uy[ok], ux[ok]]           # the upper body over them, `sink` rows down
        covered = np.zeros((H, W), bool)
        covered[uy[ok] + sink, ux[ok]] = True
        # the lower tier's cut top row, where the upper body no longer covers it: an outline square above it
        cap = np.zeros((H, W), bool)
        cap[BELT - 1] = low[BELT] & ~covered[BELT] & (out[BELT - 1, :, 3] == 0)
        out[cap, :3] = OUTLINE
        out[cap, 3] = 255
        can = np.zeros((CAN, CAN, 4), np.uint8)
        x0, y0 = self.place["side"]
        x0 += dx
        can[y0:y0 + H, x0:x0 + W] = out
        if not blade:                                            # the energy blade gone (it would reach under the ground)
            return can
        bx, by = hand_base("side")
        return D.blade(can, (bx + x0, by + y0 + sink), 32, (1, 1), crop=False)


def teal(a):
    """The hands' colours: the cyan skin and its teal outline (green and blue well over red)."""
    rgb = a[..., :3].astype(int)
    return (a[..., 3] > 0) & (rgb[..., 1] > rgb[..., 0] + 40) & (rgb[..., 2] > rgb[..., 0] + 40)


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
    # attack (24 ticks, the hit on tick 8), League's swipe with the whole arm (the user: 「卡萨丁这样平A的？」): the
    # forearm, hand and blade as one unit raised up and forward (a quarter turn about the elbow) as he draws in, then
    # brought down in front of him on the hit as he steps in 3 squares; the last frame is the design again
    def swipe(length=32, bright=False):
        up = dict(elbow=RAISED_ELBOW, length=length, bright=bright)
        return [(r.swing(1, -1, **up), ms(4)), (r.swing(1, 1, **up), ms(4)),
                (r.swing(0, 3, length=length, bright=bright), ms(6)), (r.swing(0, 2, length=length, bright=bright), ms(6)),
                (r.frame(S, blade=DOWN, length=length, bright=bright), ms(4))]
    out["attack"] = swipe()
    # attack_w: Nether Blade's strike - the same swipe, the blade longer and its whole rim lit
    out["attack_w"] = swipe(40, True)
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
    # dead (League's Death, the user: 「死亡动作不太对吧」): he collapses where he stands - the upper body sinking onto
    # the robe as it pools on the ground (only cloth rows taken out); no sideways slide (it would split the belt)
    out["dead"] = [(r.frame(S, dx=-1), ms(6)), (r.collapse(8, -1), ms(6)), (r.collapse(16, -1, False), ms(8)),
                   (r.collapse(22, -1, False), ms(10)), (r.collapse(26, -1, False), ms(60))]
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

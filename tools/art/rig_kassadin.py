#!/usr/bin/env python3
"""Kassadin's action frames, posed from the approved PPU design (no Codex strips: the user, 「动作帧你可以照着画吧？」).

    python tools/art/rig_kassadin.py [--review DIR]

The design (tools/art/design_kassadin_hd.py, approved 「可以了 你继续吧」): front A, without the blade
(design_kassadin_hd.base_views) - every action is posed from it, the 3/4 front view (the user, 2026-10-12: 「感觉卡萨丁
侧身可以不做吧」「切来切去变扭」 - the side-on actions after a front idle; Gragas's way). The Nether Blade is drawn per
frame by design_kassadin_hd.blade at the blade hand, pointing at a multiple of 45 degrees, always straight. The rules
the user holds every rig to (memories rig-deformation-checks, fix-only-what-is-reported, one-face-all-frames): no part
is turned (but by quarter turns), sheared or stretched - the parts move as wholes, so the mask, the hoses, the arms and
the robe are the design's square for square in every frame.
The parts (split): the robe - the body under row SPLIT that reaches the hem; the upper body - everything else: the
head, the torso, both arms with the hands hanging below SPLIT, the belt's front plate. The forearm unit (arm): the blade
arm's bracer, hand and blade, turned about its elbow for the swipe (League's attack: 「卡萨丁这样平A的？」).
Breathing (the user: 「可能卡萨丁像个僵尸？」): the upper body rises over the robe, the robe's top row repeated under it in
the gap (plain cloth); the run: League's glide - the figure floating, the upper body a little forward, the hem trailing;
the death: League's collapse - the upper body sinking onto the robe (the user: 「死亡动作不太对吧」); Riftwalk: the figure
recoloured toward the void (TINT) and back.
Sizes (the user: 「在游戏太小了吧」「和原本游戏有点违和感」, picked 115% and a thicker outline, then 「感觉太大了点？调到110%
差不多吧」): league.dll draws him SIZE
about his pivot, so every hd frame is drawn RAISE rows higher; every frame's outer outline is grown THICK hd squares.
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

PPU = 3.622                       # 134 design rows / 37 game rows (the user's pick)
FEET = 11                         # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes: 88 -> 99)
STEM = os.path.join(ROOT, "league", "champions", "league_kassadin")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu", "orig")  # the dense frames as drawn; tools/art/ppu_restyle.py makes the strips ppu_hd.py reads from them (2026-10-13)
CAN = 220                         # the hd canvas (square), the pivot at its middle column
GROUND = 190                      # the hd row under the robe (the soles' line)
VOID = np.array([108, 40, 196], float)      # Riftwalk's tint
DARK = np.array([30, 8, 56], float)
WHITE = np.array([255, 255, 255], float)
OUTLINE = (12, 9, 19)
ARM_ELBOW = (66, 62)              # the blade arm's elbow in the design (the forearm unit turns about it)
SPLIT = 70                        # the robe starts here (under the belt plate); the hands hang lower, with the arms
SIZE = 1.10                       # (hd.rs SIZES is 1.00 since 2026-10-13: ppu_restyle lift_sq -3 undoes this) league_main hd.rs SIZES: the DLL draws him 110% about his pivot ...
RAISE = round(FEET * PPU * (1 - 1 / SIZE))   # ... so every hd frame is drawn this many hd rows higher: soles on the ground
THICK = 3                         # the outer outline grown outward by 3 hd squares (with the drawn one ~1 game pixel; the
                                  # base heroes' and the 1x pack heroes' outline is 1 game pixel, his was 0.28)
HEM = 16                          # the robe's lowest rows: they trail behind him in the run
UP, FWD, DOWN, VERT_DN = (1, -1), (1, 0), (1, 1), (0, 1)


def ms(ticks):
    return ticks * 1000.0 / 60.0


def robe_mid(a):
    """The middle column of the robe's lowest 10 rows."""
    ys, xs = np.nonzero(a[..., 3])
    low = ys >= ys.max() - 9
    return (xs[low].min() + xs[low].max()) / 2.0


def dark_of(a):
    return (a[..., 3] > 0) & (a[..., :3].astype(int).sum(-1) < 60)


def split(a):
    """(upper, robe) masks of the design: the robe = the 4-connected body (outline squares aside) under SPLIT that
    reaches the hem's rows, with the outline squares that touch only it; everything else is the upper body."""
    op = a[..., 3] > 0
    H, W = op.shape
    rows = np.arange(H)[:, None] + np.zeros((1, W), int)
    dark = dark_of(a)
    low = op & ~dark & (rows >= SPLIT)
    lab, n = ndimage.label(low)
    bottom = set(np.unique(lab[H - 12:][lab[H - 12:] > 0]))
    robe_body = np.isin(lab, list(bottom))
    up_body = op & ~dark & ~robe_body
    near = lambda m: ndimage.binary_dilation(m, structure=np.ones((3, 3)))
    # an outline square goes with the robe when it touches the robe and no upper-body square under SPLIT
    robe_ink = dark & (rows >= SPLIT) & near(robe_body) & ~near(up_body & (rows >= SPLIT))
    robe = robe_body | robe_ink
    upper = op & ~robe
    # under SPLIT the upper body is only what hangs from above it (the arms, the hands, the belt's plate): a stray
    # outline square down by the hem joined to nothing above goes with the robe
    lab, n = ndimage.label(upper, structure=np.ones((3, 3)))
    above = set(np.unique(lab[:SPLIT][lab[:SPLIT] > 0]))
    loose = upper & ~np.isin(lab, list(above))
    return upper & ~loose, robe | loose


def forearm(a):
    """The blade arm's bracer and hand (rows 59-86, from column 63; the upper arm's and the torso's cyan left of
    column 76 left out): the biggest 8-connected piece."""
    H, W = a.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    rgb = a[..., :3].astype(int)
    cyan = (rgb[..., 1] > 100) & (rgb[..., 2] > 100) & (rgb[..., 0] < 140)
    keep = (a[..., 3] > 0) & (ys >= 59) & (ys <= 86) & (xs >= 63) & ~(cyan & (xs < 76)) & ~((ys < 66) & (xs < 67))
    lab, n = ndimage.label(keep, structure=np.ones((3, 3)))
    if n > 1:
        keep = lab == (1 + int(np.argmax(ndimage.sum(keep, lab, range(1, n + 1)))))
    return keep


class Rig:
    def __init__(self):
        self.a = D.base_views()["front"]
        ys, xs = np.nonzero(self.a[..., 3])
        # the design's top-left on the canvas: the robe's middle on the pivot column, its lowest row on GROUND - 1
        self.x0 = int(round(CAN / 2 - robe_mid(self.a)))
        self.y0 = GROUND - 1 - int(ys.max())
        self.upper, self.robe = split(self.a)
        self.fore = forearm(self.a)

    def frame(self, dx=0, dy=0, rise=0, lean=0, hem=0, sink=0, arm=None, blade=DOWN, length=32, bright=False,
              tint=None, flash=0.0):
        """One hd frame on the canvas. dx, dy: the whole figure moved; rise / sink: the upper body up / down over the
        robe (rising, the robe's top row is repeated under it); lean: the upper body forward; hem: the robe's lowest
        HEM rows back (the robe stays drawn under them); arm: the forearm unit (with the blade) turned that many quarter
        turns counter-clockwise about its elbow, drawn in front; else the blade at the hand pointing `blade` (None: no
        blade). Open edges closed with the outline when a part moved; then the recolouring."""
        a = self.a
        h, w = a.shape[:2]
        x0, y0 = self.x0 + dx, self.y0 + dy
        can = np.zeros((CAN, CAN, 4), np.uint8)

        def put(img, mask, px, py):
            ys, xs = np.nonzero(mask)
            ok = (ys + py >= 0) & (ys + py < CAN) & (xs + px >= 0) & (xs + px < CAN)
            can[ys[ok] + py, xs[ok] + px] = img[ys[ok], xs[ok]]
        put(a, self.robe, x0, y0)
        if hem:
            band = self.robe.copy()
            band[:h - HEM] = False
            put(a, band, x0 - hem, y0)
        if rise:
            top = self.robe[SPLIT] & ~dark_of(a)[SPLIT]
            for k in range(1, rise + 1):
                xs = np.nonzero(top)[0]
                can[y0 + SPLIT - k, x0 + xs] = a[SPLIT, xs]
        ux, uy = x0 + lean, y0 - rise + sink
        upper = self.upper & ~self.fore if arm is not None else self.upper
        put(a, upper, ux, uy)
        if arm is not None:
            unit, R_ = self.arm_unit(length, bright)
            unit = np.ascontiguousarray(np.rot90(unit, arm))
            ex, ey = ARM_ELBOW
            m = unit[..., 3] > 0
            cx, cy = ux + ex - R_, uy + ey - R_
            ys, xs = np.nonzero(m)
            ok = (ys + cy >= 0) & (ys + cy < CAN) & (xs + cx >= 0) & (xs + cx < CAN)
            can[ys[ok] + cy, xs[ok] + cx] = unit[ys[ok], xs[ok]]
        if rise or lean or sink or arm is not None:
            can, _, _ = G.complete_outline(can, color=OUTLINE)
        if arm is None and blade is not None:
            bx, by = D.BLADE["front"][0]
            can = D.blade(can, (bx + ux, by + uy), length, blade, bright=bright, crop=False)
        op = can[..., 3] > 0
        rgb = can[..., :3].astype(float)
        if tint:                                   # toward the void: violet, then a dark violet silhouette
            lum = rgb @ np.array([0.3, 0.55, 0.15]) / 255.0
            target = DARK[None] + (VOID - DARK)[None] * lum[..., None] * 1.6
            rgb[op] = rgb[op] * (1 - tint) + np.clip(target[op], 0, 255) * tint
        if flash:
            rgb[op] = rgb[op] * (1 - flash) + WHITE * flash
        can[..., :3] = np.clip(rgb, 0, 255).round().astype(np.uint8)
        return can

    def arm_unit(self, length, bright):
        """The forearm unit on a square canvas, the elbow at its centre, the blade drawn on it pointing down and
        forward (its rest pose: the design's)."""
        ex, ey = ARM_ELBOW
        R_ = 70
        unit = np.zeros((2 * R_ + 1, 2 * R_ + 1, 4), np.uint8)
        yy, xx = np.nonzero(self.fore)
        unit[yy - ey + R_, xx - ex + R_] = self.a[yy, xx]
        bx, by = D.BLADE["front"][0]
        unit = D.blade(unit, (bx - ex + R_, by - ey + R_), length, DOWN, bright=bright, crop=False)
        return unit, R_


def thick(can):
    """The outer outline grown outward by THICK hd squares (the drawn outline and everything inside kept)."""
    op = can[..., 3] > 0
    ring = ndimage.binary_dilation(op, structure=np.ones((3, 3)), iterations=THICK) & ~op
    out = can.copy()
    out[ring, :3] = OUTLINE
    out[ring, 3] = 255
    return out


def down(can):
    """The hd canvas -> (the 1x frame centred on the pivot, the hd frame of round(PPU x its size), grown RAISE rows at
    both ends with its picture RAISE rows higher: the DLL draws him SIZE about the pivot, so his soles stay on the
    ground). The outline is thickened first (thick). The pivot: canvas column CAN / 2, FEET 1x rows above GROUND.
    Every 1x pixel takes the commonest colour of the hd squares under it (clear when most of them are clear)."""
    can = thick(can)
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
    W, H = round(w1 * PPU), round(h1 * PPU) + 2 * RAISE
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py + RAISE - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sy0, sx0 = max(0, hy0), max(0, hx0)
    sub = can[sy0:hy0 + H, sx0:hx0 + W]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return one, hd


def actions(r):
    """{tag: [(hd canvas, ms)]} - the moves, the blade's direction and the timings (the kit's ticks)."""
    out = {}
    # idle: he breathes - the upper body rises 3 hd rows over the robe and settles, the blade's rim lit at the top
    breath = [0, 1, 2, 3, 3, 2, 1, 0]
    out["idle"] = [(r.frame(rise=b, bright=b >= 3), ms(7.5)) for b in breath]
    # run: League's glide - the figure floating up and down two squares twice a loop, the upper body 2 squares forward
    # over the robe, the hem trailing back
    bob = [0, -1, -2, -1, 0, -1, -2, -1]
    trail = [0, 1, 2, 1, 0, 1, 2, 1]
    out["run"] = [(r.frame(dy=b, lean=2, hem=t), ms(5)) for b, t in zip(bob, trail)]
    # attack (24 ticks, the hit on tick 8), League's swipe with the whole arm: the forearm, hand and blade raised up
    # and forward (a quarter turn about the elbow) as he draws in, brought down in front of him on the hit as he steps
    # in 3 squares; the last frame is the design again
    def swipe(length=32, bright=False):
        k = dict(length=length, bright=bright)
        return [(r.frame(dx=-1, arm=1, **k), ms(4)), (r.frame(dx=1, arm=1, **k), ms(4)),
                (r.frame(dx=3, arm=0, **k), ms(6)), (r.frame(dx=2, arm=0, **k), ms(6)), (r.frame(**k), ms(4))]
    out["attack"] = swipe()
    # attack_w: Nether Blade's strike - the same swipe, the blade longer and its whole rim lit
    out["attack_w"] = swipe(40, True)
    # skill Q (24 ticks, the orb on tick 8): the blade raised up and forward, lowered to point at the target as he
    # leans in
    q = [(-1, UP, 4), (0, UP, 4), (2, FWD, 6), (1, FWD, 6), (0, DOWN, 4)]
    out["skill"] = [(r.frame(dx=x, blade=b), ms(t)) for x, b, t in q]
    # skill2 E (24 ticks, the pulse on tick 8): drawn back gathering (the blade straight down), thrust forward
    e = [(-2, VERT_DN, 4), (-2, VERT_DN, 4), (3, FWD, 6), (2, FWD, 6), (0, DOWN, 4)]
    out["skill2"] = [(r.frame(dx=x, blade=b), ms(t)) for x, b, t in e]
    # ult R (24 ticks, he vanishes on tick 6): turning to void, a dark silhouette over the jump, back to himself
    rr = [(0.0, 3), (0.5, 3), (0.95, 6), (0.5, 6), (0.0, 6)]
    out["ult"] = [(r.frame(blade=UP if k == 0 else DOWN, tint=t), ms(d)) for k, (t, d) in enumerate(rr)]
    # hit: knocked back 2 squares with a white flash, then 1
    out["hit"] = [(r.frame(dx=-2, flash=0.35), ms(6)), (r.frame(dx=-1), ms(6))]
    # dead: League's collapse - the upper body sinking onto the robe; the energy blade gone from frame 3 (it would
    # reach under the ground)
    out["dead"] = [(r.frame(dx=-1), ms(6)), (r.frame(dx=-1, sink=10), ms(6)), (r.frame(dx=-1, sink=20, blade=None), ms(8)),
                   (r.frame(dx=-1, sink=26, blade=None), ms(10)), (r.frame(dx=-1, sink=30, blade=None), ms(60))]
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

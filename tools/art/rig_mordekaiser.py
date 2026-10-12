#!/usr/bin/env python3
"""Mordekaiser's action frames: the approved dense design (idle) and Codex's key poses on the same grid.

    python tools/art/rig_mordekaiser.py [--review DIR]

The design (tools/art/design_mordekaiser_hd.py, picture A read back, 166 x 246 squares) is the idle and the card. Every
action is the 3/4 front view (the user: 「侧面只要四分之三那种就行 参考卡萨丁」). His mace rests behind the helm and the
pauldron, so the swings were drawn by Codex on the design's own grid (tools/art/pack_mordekaiser_poses.py ->
assets/source/mordekaiser/codex_poses: the user's 「交给 Codex 画姿势」); Codex's own _1x copies sit on the pack's grid
canvases with the horn tips and the soles on the pack's lines, so they share the design's scale and ground.
  - one face (memory one-face-all-frames): the design's helm (HELM, the horns down to the chin) is pasted square for
    square over the pose's own wherever the pose shows it upright and uncovered (HELM_AT: its offset in the pose,
    found by matching); Q's raise and slam and the death keep Codex's (the helm between the raised arms, bowed, fallen);
  - the run and every skill: Codex's drawings turned 65 degrees toward the image right (codex_run, codex_turned:
    the user's 「待机姿势和走路放技能的时候应该不一样的」), tones matched to the run's phase 2; the idle stays A;
  - the idle: the design breathing - the upper body rises over the legs, the row at the cut repeated in the gap;
  - W and the hit: the design recoloured (a teal pulse; a white flash) and moved as a whole.
Sizes (the user's pick C: 110% and a thicker outline, Kassadin's way): league.dll draws him SIZE about his pivot, so
every hd frame is drawn RAISE rows higher; every frame's outer outline is grown THICK hd squares.
Writes:
  league/champions/league_mordekaiser#sheet.png / #anim.fanim - the 1x tags (each hd frame brought down by PPU, every 1x
      pixel the commonest colour of its squares; the fallback without league.dll), frames centred on the pivot
  assets/source/ppu/mordekaiser_<tag>.png + .json - the hd frames (ppu_hd.py's drawn strips: one row, 1 px gaps)
Then tools/art/ppu_hd.py --hero mordekaiser adds the hd_ tags (PPU["mordekaiser"]).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402
sys.path.insert(0, HERE)
import design_varus as V  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "mordekaiser")
FRONT = os.path.join(SRC, "hd", "front.png")
POSES = os.path.join(SRC, "codex_poses")
STEM = os.path.join(ROOT, "league", "champions", "league_mordekaiser")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")

PPU = 5.0                         # 246 design rows / 49 game rows
FEET = 11                         # 1x rows from the pivot down to the soles
SIZE = 1.10                       # league_main hd.rs SIZES: the DLL draws him 110% about his pivot ...
RAISE = round(FEET * PPU * (1 - 1 / SIZE))   # ... so every hd frame is drawn this many hd rows higher
THICK = 3                         # the outer outline grown outward by 3 hd squares (the user's pick C)
OUTLINE = (2, 3, 3)
CW, CH = 480, 420                 # the hd canvas
GROUND = 400                      # the hd row under the soles
PACK = {"landscape": (60, 6), "portrait": (40, 134)}   # the design's top-left on the pack's grid canvases
PIVOT_X = 148                     # the pivot column in landscape coordinates (between the design's feet)
HELM = [(70, 62), (73, 30), (84, 30), (87, 48), (91, 30), (101, 30), (103, 44), (104, 58), (103, 76), (98, 88),
        (92, 92), (84, 90), (78, 80), (72, 72)]
# the helm's offset in each pose from where it sits in the design (template match on the 1x copies)
HELM_AT = {"attack-raise": (13, -10), "attack-strike": (22, 9), "e-grasp": (0, 0), "r-point": (-14, -7)}
# poses whose own helm is cleared first round the pasted one (above the shoulders: a horn of Codex's showed beside
# ours); e-grasp keeps its pixels (the mace behind the helm, its helm the design's within a square)
CLEAR = {"attack-raise", "attack-strike", "r-point"}
CLEAR_PAD, CLEAR_ROWS = 5, 76     # hd squares round the helm, the design rows above which the clearing reaches
RUN = os.path.join(SRC, "codex_run")          # the 65-degree run (Codex, 2026-10-12: mordekaiser_run_poses.zip)
TURNED = os.path.join(SRC, "codex_turned")    # the 65-degree stand and skill poses (mordekaiser_turned_done.zip; their
                                              # helms Codex's copy of walk-1's)
TURNED_POSES = ["turned", "attack-raise", "attack-strike", "q-raise", "q-slam", "e-grasp", "r-point"]
TURN_DX = -33                                 # the turned stand's torso over the pivot (the run's: RUN_DX)
LIFT = 1                                      # Codex's 65-degree soles sit on row 252, the design's on 251: one row up
# The user, on Codex's two raises a tenth taller than the stand and the strike's spike cut at the ground: 「我自己缩小和补
# 尖刺」. SHRINK: pose -> (its horn row, the stand's horn row, the soles' row) from Codex's QA.json - the pose brought to
# the stand's height by whole rows and columns out (design_riven.seam_shrink: the least-loss line of each group), about
# the soles' middle, then the run's helm pasted back at its full size where Codex had put it (HELM_REF, QA's
# helmet_position, scaled). SPIKE: the strike's raw read back on Codex's own 4-px grid (offset found by matching: 14
# rows down) gives back the mace head's spikes Codex cleared under the soles' row (columns from SPIKE_X).
SHRINK = {"attack-raise": (142, 164, 380, (137, 142)), "q-raise": (145, 164, 380, (122, 145))}
HELM_REF = os.path.join(TURNED, "helmet_reference_1x.png")
SPIKE = ("attack-strike", 14, 252, 290)       # pose, Codex's shift down, the soles' row, the first column kept
RUN_DX = {1: -37, 2: -29, 3: -37, 4: -37}     # phase 2's upper body stood 8 squares left of the others'; all onto the pivot
# poses Codex drew away from the design's place: the body (the mace on the ground aside) brought back over the pivot
POSE_DX = {"dead-kneel": -95, "dead-lying": -58}   # the step's bob (the helm's offset in each walk phase)
LEG_CUT = 165                     # design row: the idle's upper body rises above it
TEAL = np.array([20, 230, 220], float)
WHITE = np.array([255, 255, 255], float)


def ms(ticks):
    return ticks * 1000.0 / 60.0


class Rig:
    def __init__(self):
        self.a = np.asarray(Image.open(FRONT).convert("RGBA"))
        h, w = self.a.shape[:2]
        pm = Image.new("L", (w, h), 0)
        ImageDraw.Draw(pm).polygon(HELM, fill=255)
        self.helm = (np.asarray(pm) > 0) & (self.a[..., 3] > 0)
        self.poses = {}
        for f in os.listdir(POSES):
            if f.endswith("_1x.png"):
                p = np.asarray(Image.open(os.path.join(POSES, f)).convert("RGBA"))
                kind = "portrait" if p.shape[0] > p.shape[1] else "landscape"
                self.poses[f[len("mordekaiser-"):-len("_1x.png")]] = (p, kind)
        pal = np.unique(self.a[self.a[..., 3] > 0][:, :3], axis=0)
        raw = {k: np.asarray(Image.open(os.path.join(RUN, f"mordekaiser-walk-{k}_1x.png")).convert("RGBA"))
               for k in (1, 2, 3, 4)}
        self.run = {k: (raw[k] if k == 2 else relum(raw[k], raw[2], pal)) for k in raw}
        self.turned = {}
        helm = np.asarray(Image.open(HELM_REF).convert("RGBA"))
        for n in TURNED_POSES:
            p = np.asarray(Image.open(os.path.join(TURNED, f"mordekaiser-{n}_1x.png")).convert("RGBA"))
            kind = "portrait" if p.shape[0] > p.shape[1] else "landscape"
            if n in SHRINK:
                p = shrink(p, *SHRINK[n], helm)
            if n == SPIKE[0]:
                p = spike(p)
            self.turned[n] = (relum(p, raw[2], pal), kind)

    def canvas(self):
        return np.zeros((CH, CW, 4), np.uint8)

    def origin(self, kind):
        """Where a canvas's (0, 0) goes on the hd canvas: the soles' row on GROUND, the pivot column in the middle."""
        x0, y0 = PACK[kind]
        lx, ly = PACK["landscape"]
        # landscape coordinates: the soles on row ly + 246, the pivot on PIVOT_X
        ox = CW // 2 - PIVOT_X + (lx - x0)
        oy = GROUND - (ly + self.a.shape[0]) + (ly - y0)
        return ox, oy

    def put(self, can, img, mask, ox, oy):
        ys, xs = np.nonzero(mask)
        ok = (ys + oy >= 0) & (ys + oy < CH) & (xs + ox >= 0) & (xs + ox < CW)
        can[ys[ok] + oy, xs[ok] + ox] = img[ys[ok], xs[ok]]

    def design(self, dx=0, dy=0, rise=0):
        """The design; rise: the upper body (above LEG_CUT) that many rows up, the cut's row repeated under it."""
        can = self.canvas()
        ox, oy = self.origin("landscape")
        ox, oy = ox + PACK["landscape"][0] + dx, oy + PACK["landscape"][1] + dy
        a = self.a
        op = a[..., 3] > 0
        legs = op.copy()
        legs[:LEG_CUT] = False
        self.put(can, a, legs, ox, oy)
        for k in range(1, rise + 1):
            row = op[LEG_CUT]
            xs = np.nonzero(row)[0]
            can[oy + LEG_CUT - k, ox + xs] = a[LEG_CUT, xs]
        upper = op.copy()
        upper[LEG_CUT:] = False
        self.put(can, a, upper, ox, oy - rise)
        return can

    def pose(self, name, helm=True):
        """Codex's pose on the hd canvas, the design's helm pasted square for square where HELM_AT has it."""
        p, kind = self.poses[name]
        can = self.canvas()
        ox, oy = self.origin(kind)
        ox += POSE_DX.get(name, 0)
        self.put(can, p, p[..., 3] > 0, ox, oy)
        if helm and name in HELM_AT:
            dx, dy = HELM_AT[name]
            x0, y0 = PACK[kind]
            hx, hy = ox + x0 + dx, oy + y0 + dy
            if name in CLEAR:
                zone = ndimage.binary_dilation(self.helm, structure=np.ones((3, 3)), iterations=CLEAR_PAD)
                zone[CLEAR_ROWS:] = False
                ys, xs = np.nonzero(zone)
                ok = (ys + hy >= 0) & (ys + hy < CH) & (xs + hx >= 0) & (xs + hx < CW)
                can[ys[ok] + hy, xs[ok] + hx] = 0
            self.put(can, self.a, self.helm, hx, hy)
        return can

    def turn(self, name, dx=0):
        """A 65-degree drawing (the stand or a skill pose), its tones matched to the run's, over the pivot."""
        p, kind = self.turned[name]
        can = self.canvas()
        ox, oy = self.origin(kind)
        self.put(can, p, p[..., 3] > 0, ox + TURN_DX + dx, oy - (0 if name in SHRINK else LIFT))
        return can

    def walk(self, k):
        """The run turned toward the image right (the user: 「走路的时候腿既然是那个方向 身体也要那个方向吧？」, picked
        League's 65 degrees): Codex's phase k (codex_run), its tones matched to phase 2's (relum), moved by RUN_DX so
        the four upper bodies stand on one column and the torso over the pivot."""
        p = self.run[k]
        can = self.canvas()
        ox, oy = self.origin("landscape")
        self.put(can, p, p[..., 3] > 0, ox + RUN_DX[k], oy - LIFT)
        return can


def shrink(p, horn, target, feet, helm_at, helm):
    """Codex's pose brought to the stand's height (SHRINK), the run's helm pasted back at its full size."""
    import design_riven as D
    f = (feet - target) / (feet - horn)
    op = p[..., 3] > 0
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    cols = np.unique(p[op][:, :3], axis=0)
    lut = {tuple(int(v) for v in c): i for i, c in enumerate(cols)}
    idx = np.full(p.shape[:2], -1, int)
    for y, x in zip(ys, xs):
        idx[y, x] = lut[tuple(int(v) for v in p[y, x, :3])]
    box = idx[y0:y1, x0:x1]
    th, tw = round(box.shape[0] * f), round(box.shape[1] * f)
    small = D.seam_shrink(box, th, tw)
    low = np.nonzero(op[feet - 10:feet].any(0))[0]
    ax = (low.min() + low.max()) / 2.0                       # the soles' middle stays put
    nx0 = int(round(ax - (ax - x0) * f))
    ny0 = feet - th
    out = np.zeros_like(p)
    m = small >= 0
    yy, xx = np.nonzero(m)
    out[yy + ny0, xx + nx0, :3] = cols[small[m]]
    out[yy + ny0, xx + nx0, 3] = 255
    # the helm: its middle where the scaled one sits, at full size, the shrunk one cleared round it
    hh, hw = helm.shape[:2]
    cx = ax + (helm_at[0] + hw / 2.0 - ax) * f
    cy = feet - (feet - (helm_at[1] + hh / 2.0)) * f
    hx, hy = int(round(cx - hw / 2.0)), int(round(cy - hh / 2.0))
    hm = helm[..., 3] > 0
    zone = ndimage.binary_dilation(hm, structure=np.ones((3, 3)), iterations=2)
    zone[int(hh * 0.8):] = False                             # the neck and shoulders below stay the pose's
    zy, zx = np.nonzero(zone)
    out[zy + hy, zx + hx] = 0
    yy, xx = np.nonzero(hm)
    out[yy + hy, xx + hx] = helm[yy, xx]
    return out


def spike(p):
    """The strike's mace head under the soles' row, read back from the raw on Codex's grid (SPIKE)."""
    name, down, feet, x_from = SPIKE
    pal = np.unique(p[p[..., 3] > 0][:, :3], axis=0).astype(int)
    raw = np.asarray(Image.open(os.path.join(TURNED, "raw", f"mordekaiser-{name}.png")).convert("RGBA")).astype(int)
    H, W = raw.shape[0] // 4, raw.shape[1] // 4
    blk = raw[:H * 4, :W * 4].reshape(H, 4, W, 4, 4).transpose(0, 2, 1, 3, 4).reshape(H, W, 16, 4)
    extra = []
    for y in range(feet - down, H):
        for x in range(x_from, W):
            b = blk[y, x]
            o = b[b[:, 3] >= 128]
            if len(o) * 2 < 16:
                continue
            c, n = np.unique(o[:, :3], axis=0, return_counts=True)
            extra.append((y + down, x, pal[np.abs(pal - c[n.argmax()]).sum(1).argmin()]))
    if not extra:
        return p
    out = np.zeros((max(p.shape[0], max(e[0] for e in extra) + 1),) + p.shape[1:], np.uint8)
    out[:p.shape[0]] = p
    for y, x, c in extra:
        out[y, x, :3] = c
        out[y, x, 3] = 255
    return out


def relum(p, ref, pal):
    """p's colours moved to ref's tones: every colour's place among p's lightnesses (its median quantile) mapped to
    the lightness at that quantile of ref, then the palette colour nearest in Lab to that lightness with the colour's
    own hue (teal stays teal). The four run phases came 173 / 199 / 210 / 232 bright (the design 202)."""
    op, ro = p[..., 3] > 0, ref[..., 3] > 0
    lab = V.srgb2lab(p[op][:, :3].astype(float))
    rl = np.sort(V.srgb2lab(ref[ro][:, :3].astype(float))[:, 0])
    plab = V.srgb2lab(pal.astype(float))
    order = np.argsort(lab[:, 0], kind="stable")
    q = np.empty(len(lab))
    q[order] = (np.arange(len(lab)) + 0.5) / len(lab)
    out = p.copy()
    px = out[op]
    keys = [tuple(c) for c in p[op][:, :3]]
    groups = {}
    for i, key in enumerate(keys):
        groups.setdefault(key, []).append(i)
    for key, idx in groups.items():
        idx = np.array(idx)
        target = rl[min(len(rl) - 1, int(np.median(q[idx]) * len(rl)))]
        c = lab[idx[0]]
        d = (plab[:, 0] - target) ** 2 + (plab[:, 1] - c[1]) ** 2 + (plab[:, 2] - c[2]) ** 2
        px[idx, :3] = pal[d.argmin()]
    out[op] = px
    return out


SPECK = 12                        # loose pieces smaller than this (8-connected) are dropped
PINHOLE = 4                       # enclosed clear holes up to this size (Codex's grid vote left them) are filled


def finish(can, tint=None, flash=0.0):
    lab, n = ndimage.label(can[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        can[np.isin(lab, 1 + np.nonzero(sizes < SPECK)[0])] = 0
    op = can[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    hl, hk = ndimage.label(holes)
    for k in range(1, hk + 1):
        m = hl == k
        if m.sum() > PINHOLE:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(can[ring][:, :3], axis=0, return_counts=True)
        can[m, :3] = cols[cnt.argmax()]
        can[m, 3] = 255
    can, _, _ = G.complete_outline(can, color=OUTLINE)
    op = can[..., 3] > 0
    rgb = can[..., :3].astype(float)
    if tint:
        rgb[op] = rgb[op] * (1 - tint) + TEAL * tint
    if flash:
        rgb[op] = rgb[op] * (1 - flash) + WHITE * flash
    can[..., :3] = np.clip(rgb, 0, 255).round().astype(np.uint8)
    return can


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
    both ends with its picture RAISE rows higher). The pivot: column CW / 2, FEET 1x rows above GROUND. Every 1x pixel
    takes the commonest colour of the hd squares under it (clear when most of them are clear)."""
    can = thick(can)
    px, py = CW / 2.0, GROUND - FEET * PPU
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
    W, H = round(w1 * PPU), round(h1 * PPU) + 2 * RAISE
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py + RAISE - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sy0, sx0 = max(0, hy0), max(0, hx0)
    sub = can[sy0:hy0 + H, sx0:hx0 + W]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return one, hd


def actions(r):
    """{tag: [(hd canvas, ms)]} - the kit's ticks (tools/kit/build_mordekaiser.py). The idle is design A; the run and every
    skill the 65-degree drawings (the user: 「待机姿势和走路放技能的时候应该不一样的」, picked 65); the death step 2's."""
    out = {}
    stand = finish(r.turn("turned"))
    # idle: he breathes - the upper body rises 2 rows over the legs and settles
    out["idle"] = [(finish(r.design(rise=b)), ms(8)) for b in (0, 1, 2, 2, 1, 0)]
    # run: Codex's four walking phases turned 65 degrees
    out["run"] = [(finish(r.walk(k)), ms(8)) for k in (1, 2, 3, 4)]
    # attack (24 ticks, the hit on tick 10): raise, swing down on the hit, back to the shoulder
    out["attack"] = [(stand, ms(4)), (finish(r.turn("attack-raise")), ms(6)), (finish(r.turn("attack-strike")), ms(9)),
                     (stand, ms(5))]
    # skill Q (26 ticks, the slam on tick 10): both hands overhead, the slam held, back
    out["skill"] = [(finish(r.turn("q-raise")), ms(10)), (finish(r.turn("q-slam")), ms(11)), (stand, ms(5))]
    # skill2 E (24 ticks, the claw on tick 8): the free hand thrust forward
    out["skill2"] = [(stand, ms(3)), (finish(r.turn("e-grasp")), ms(16)), (stand, ms(5))]
    # skill2_w W (20 ticks): a teal pulse over the stand
    out["skill2_w"] = [(finish(r.turn("turned"), tint=0.25), ms(6)), (finish(r.turn("turned"), tint=0.45), ms(8)),
                       (finish(r.turn("turned"), tint=0.2), ms(6))]
    # ult R (30 ticks, the curse on tick 8): the mace pointed at the target
    out["ult"] = [(stand, ms(3)), (finish(r.turn("r-point")), ms(22)), (stand, ms(5))]
    # hit: knocked back 2 squares with a white flash, then 1
    out["hit"] = [(finish(r.turn("turned", dx=-2), flash=0.35), ms(6)), (finish(r.turn("turned", dx=-1)), ms(6))]
    # dead: down on one knee, then lying
    out["dead"] = [(finish(r.pose("dead-kneel")), ms(14)), (finish(r.pose("dead-lying")), ms(60))]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's hd frames here (3x) and an all-tags GIF")
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
        Image.fromarray(strip).save(os.path.join(PPU_SRC, f"mordekaiser_{tag}.png"))
        with open(os.path.join(PPU_SRC, f"mordekaiser_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds]}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 2
            tiles = [Image.fromarray(thick(c)) for c, _ in frames]
            big = Image.new("RGBA", (len(tiles) * CW * Z, CH * Z), (92, 98, 86, 255))
            for k, t in enumerate(tiles):
                big.alpha_composite(t.resize((CW * Z, CH * Z), Image.NEAREST), (k * CW * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"mordekaiser_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_mordekaiser#sheet.png {w}x{h}: " +
          ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()

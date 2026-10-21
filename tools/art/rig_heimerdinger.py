#!/usr/bin/env python3
"""league_heimerdinger's action frames after League's own clips (the user, 2026-10-21, on the first rig: 「身体背后的机械的
动作帧呢？没有 还有头和身体不协调 走路也怪」「你觉得这个动作帧和英雄联盟一样吗 我觉得差的很大」「做不出来就让codex帮忙」).

    python tools/art/rig_heimerdinger.py --review DIR    # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_heimerdinger.py                 # orig strips + the 1x sheet (then ppu_restyle / ppu_hd)

Every frame is three layers on the design's grid (PPU 1.5):
  * his BODY - the approved design (hd/idle.png, 50 x 54) where League's body barely moves (Q, E, W, R: the backpack's
    machinery does the work), breathing above the belt (whole rows set down onto the waist: the legs never move);
    Codex's whole-body poses where it moves (pack A, read back by design_heimerdinger_poses.py with the design head
    pasted back and placed by League's neck): the run's bouncing skip, the attack's kick and jab, the idle's tinkering,
    the death;
  * the backpack CRANE behind him (pack B, design_heimerdinger_props.py: 17 positions read at one joint size, the root
    on League's Rocket_Base for that frame), its rocket held or gone as League's clips;
  * R's GEAR over him (the drum, the coil antennas, the ring round the top of his mane).
Effects drawn into the frames (Gemini's, assets/source/heimerdinger/codex_fx): the crane's launch flash (w_flash) at the
claw when W fires, the backpack bursting (dead_burst) in the death - laid on after the outline (ppu_restyle fx).
Timings follow League's clips, squeezed to the kit's actions (build_heimerdinger.P): attack 27 ticks (the bolt on 10),
attack_w (W's third attack: the crane fires on 10), Q and E 36 (the turret set down / the grenade flung on 16), R 40
(the gear bursts on 12, the upgrade on 14).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "heimerdinger"
PPU = 1.5
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
FX = os.path.join(R.ROOT, "assets", "source", HERO, "codex_fx", "heimerdinger_fx", "pixel_1x")
POSE_PAD = 40                # hd/pose_<name>.png: the design's (0, 0) at (40, 40)
PROP_AT = (40, 100)          # hd/prop_<name>.png: the design's (0, 0) at (40, 100)
BREATH_ROW = 44              # rows above (the head, the coat to the belt, the arms) breathe; the waist and legs stay


def lp(path):
    return R.lp(path)


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


class Design:
    def __init__(self):
        d = load(os.path.join(HD, "idle.png"))
        self.d0 = d
        self.H, self.W = d.shape[:2]
        self.hero, self.ppu = HERO, PPU
        op = d[..., 3] > 0
        lum = d[..., :3].astype(int).sum(-1)
        self.outline = tuple(int(v) for v in d[op][np.argmin(lum[op])][:3])
        ys, xs = np.nonzero(op)
        self.ground = ys.max() + 1
        low = d[ys.max() - 2:ys.max() + 1, :, 3].any(0)
        fx = np.nonzero(low)[0]
        self.px = int(round((fx.min() + fx.max() + 1) / 2))
        self.poses, self.props, self.fx = {}, {}, {}

    def pose(self, name):
        if name not in self.poses:
            self.poses[name] = load(os.path.join(HD, f"pose_{name}.png"))
        return self.poses[name]

    def prop(self, name):
        if name not in self.props:
            self.props[name] = load(os.path.join(HD, f"prop_{name}.png"))
        return self.props[name]

    def effect(self, name):
        """A Gemini effect's frames (pixel_1x strip, equal cells) brought to PPU (nearest, every 1x pixel kept)."""
        if name not in self.fx:
            man = json.load(open(lp(os.path.join(os.path.dirname(FX), "manifest.json")), encoding="utf-8"))
            meta = next(e for e in man["effects"] if e["name"] == name)
            a = load(os.path.join(FX, meta["file"]))
            w, h = meta["cell_1x"]
            cells = []
            for k in range(meta["frames"]):
                c = a[:h, k * w:(k + 1) * w]
                yy = np.minimum(((np.arange(round(h * PPU)) + 0.5) / PPU).astype(int), h - 1)
                xx = np.minimum(((np.arange(round(w * PPU)) + 0.5) / PPU).astype(int), w - 1)
                b = c[yy][:, xx].copy()
                # sparks under 4 squares dropped (ppu_hd's check: no specks on a frame; ppu_rig.Rig.bake's way)
                lbl, n = ndimage.label(b[..., 3] > 0, structure=np.ones((3, 3)))
                if n:
                    sz = ndimage.sum(b[..., 3] > 0, lbl, range(1, n + 1))
                    for j in range(1, n + 1):
                        if sz[j - 1] < 4:
                            b[lbl == j] = 0
                cells.append(b)
            self.fx[name] = cells
        return self.fx[name]


def put(can, layer, x0, y0):
    """layer's drawn squares onto can with layer's (0, 0) at (x0, y0)."""
    ys, xs = np.nonzero(layer[..., 3] > 0)
    H, W = can.shape[:2]
    ok = (ys + y0 >= 0) & (ys + y0 < H) & (xs + x0 >= 0) & (xs + x0 < W)
    can[ys[ok] + y0, xs[ok] + x0] = layer[ys[ok], xs[ok]]


def breathe(d, n):
    """The design with everything above BREATH_ROW set down n rows onto the waist (whole rows; the legs untouched)."""
    if not n:
        return d
    out = d.copy()
    top = d[:BREATH_ROW].copy()
    out[n:BREATH_ROW + n] = np.where(top[..., 3:4] > 0, top, out[n:BREATH_ROW + n])
    out[:n] = 0
    # the rows the upper body left are the upper body's own lowest rows again (no gap opens at the belt)
    return out


class Frame:
    """body: "rest" (the design) or a pose name; crane / gear: a prop name or None; breath: rows the upper body sets
    down; dx, dy: the whole frame's move; flash: the hit's white; fx: [(effect, frame index, (x, y) design squares of
    its middle, "over" | "under")]."""

    def __init__(self, body="rest", crane=None, gear=None, breath=0, dx=0, dy=0, flash=False, fx=()):
        self.body, self.crane, self.gear, self.breath = body, crane, gear, breath
        self.dx, self.dy, self.flash, self.fx = dx, dy, flash, list(fx)


def compose(rig, D, f):
    ox, oy = rig.ox + f.dx, rig.oy + f.dy
    can = rig.canvas()
    if f.crane:
        put(can, D.prop(f.crane), ox - PROP_AT[0], oy - PROP_AT[1])
    if f.body == "rest":
        put(can, breathe(D.d0, f.breath), ox, oy)
    else:
        put(can, D.pose(f.body), ox - POSE_PAD, oy - POSE_PAD)
    if f.gear:
        put(can, D.prop(f.gear), ox - PROP_AT[0], oy - PROP_AT[1])
    can[rig.GY:] = 0
    if f.flash:
        can = R.flash(can)
    if not f.fx:
        return can
    over, under = rig.canvas(), rig.canvas()
    for name, k, (cx, cy), where in f.fx:
        cell = D.effect(name)[k]
        h, w = cell.shape[:2]
        put(over if where == "over" else under, cell, int(round(ox + cx - w / 2)), int(round(oy + cy - h / 2)))
    return {"body": can, "over": over if over[..., 3].any() else None, "under": under if under[..., 3].any() else None}


def claw(D, prop):
    """The red claw's middle in a crane prop (design squares)."""
    p = D.prop(prop)
    r, g, b = (p[..., i].astype(int) for i in range(3))
    red = (p[..., 3] > 0) & (r > 150) & (g < 80) & (b < 80)
    ys, xs = np.nonzero(red)
    return (xs.mean() - PROP_AT[0], ys.mean() - PROP_AT[1])


def acts(D):
    F = Frame
    run = [F(f"run{k}") for k in range(1, 9)]
    fire = claw(D, "crane_fire")
    return {
        # League's Idle1: he stands breathing, then brings the multitool up to his chest and tinkers with it
        "idle": [(F(breath=0), 167), (F(breath=1), 167), (F(breath=1), 167), (F("tinker"), 167), (F("tinker"), 167),
                 (F(breath=1), 167), (F(breath=0), 167), (F(breath=0), 165)],
        # Run1: the bouncing skip, both tools swinging (Codex's eight poses, placed by League's hops)
        "run": [(f, 100) for f in run],
        # Attack1: the kick up, the jab (the bolt leaves on tick 10, 167 ms), the follow-through
        "attack": [(F(), 60), (F("attack1"), 90), (F("attack2"), 120), (F("attack3"), 100), (F(breath=1), 80)],
        # Spell2 (W rides his third attack): the crane out with a rocket, up, it fires on tick 10 - the flash at the claw
        "attack_w": [(F(crane="crane_peek2"), 67), (F(crane="crane_aim"), 83),
                     (F(crane="crane_fire", breath=1, fx=[("w_flash", 0, fire, "over")]), 42),
                     (F(crane="crane_fire", breath=1, fx=[("w_flash", 1, fire, "over")]), 41),
                     (F(crane="crane_recover", fx=[("w_flash", 2, fire, "over")]), 83), (F(crane="crane_aim_empty"), 67),
                     (F(crane="crane_fold"), 67)],
        # Spell1 (Q): the crane lifts the turret kit high, swings over and sets it down at his front (tick 16, 267 ms),
        # comes back up and folds; he ducks a row as it sets down
        "skill": [(F(crane="crane_peek"), 67), (F(crane="crane_up"), 67), (F(crane="crane_up_back"), 67),
                  (F(crane="crane_up_high"), 66), (F(crane="crane_place", breath=1), 67),
                  (F(crane="crane_lift", breath=1), 67), (F(crane="crane_return"), 67), (F(crane="crane_up_empty"), 67),
                  (F(crane="crane_fold"), 65)],
        # Spell3 (E): the crane up with the grenade, cocked forward, flung (tick 16, 267 ms), back up, folded
        "skill2": [(F(crane="crane_peek2"), 67), (F(crane="crane_up_high"), 67), (F(crane="crane_up_high", breath=1), 67),
                   (F(crane="crane_cock", breath=1), 66), (F(crane="crane_throw"), 67), (F(crane="crane_recoil"), 67),
                   (F(crane="crane_up_empty"), 67), (F(crane="crane_up_empty"), 67), (F(crane="crane_fold"), 65)],
        # Spell4_IN / LOOP (R): the drum pops up, the antennas spring out and the ring opens (tick 12), they settle
        "ult": [(F(gear="gear_drum"), 67), (F(gear="gear_drum", breath=1), 67), (F(gear="gear_drum", breath=1), 66),
                (F(gear="gear_burst"), 67), (F(gear="gear_burst"), 67), (F(gear="gear_settle"), 67),
                (F(gear="gear_settle"), 67), (F(gear="gear_settle", breath=1), 67), (F(gear="gear_settle", breath=1), 67),
                (F(gear="gear_settle"), 65)],
        "hit": [(F(dx=-1, flash=True), 100), (F(dx=-1), 100)],
        # Death: the backpack bursts (the engine and the crane out, dead_burst over the engine at his back, clear of his face), he
        # tips over backwards and
        # lies on his back on the engine
        "dead": [(F(), 100), (F("death1", fx=[("dead_burst", 0, (-6, 36), "over")]), 120),
                 (F("death1", fx=[("dead_burst", 1, (-6, 36), "over")]), 120),
                 (F("death2", fx=[("dead_burst", 2, (-4, 44), "over")]), 120),
                 (F("death2", fx=[("dead_burst", 3, (-4, 44), "over")]), 120),
                 (F("death3", fx=[("dead_burst", 4, (-14, 44), "over")]), 300), (F("death3"), 800)],
    }


def frames(rig):
    D = rig.D
    return {tag: [(compose(rig, D, f), ms) for f, ms in seq] for tag, seq in acts(D).items()}


def make_rig(D):
    return R.Rig(D, pad=(60, 60, 110, 30))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    D = Design()
    rig = make_rig(D)
    fr = frames(rig)
    if a.review:
        rig.review(fr, a.review)
        return
    rig.export(fr)


if __name__ == "__main__":
    main()

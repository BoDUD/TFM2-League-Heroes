#!/usr/bin/env python3
"""tft_terra's action frames: Terra's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-31: sprites by Codex from written prompts).

    python tools/art/rig_terra.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_terra.py                  # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_terra), then ppu_restyle.py / ppu_hd.py --hero terra

The pictures (tools/art/design_terra_model.py, design_terra_poses.py):
  hd/idle.png         Terra crouched on all fours, 3/4 facing right, 86 x 52 at PPU 1.45 (36 game px, the wing-bone tips to
                      her soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size and density with the design's face where the head is
                      not turned (assets/source/terra/POSE_PROMPTS.md, design_terra_poses.py): a_wind a_hit q_crouch
                      q_pounce q_bite e_spread e_roar r_rear r_stomp r_roar d_fall d_down and the flight run1-6.
Placing a pose: Codex drew every pose bigger than asked and not on its reference's place, so each pose stands by its
hind legs (its json's pivot: the middle of the hind feet, design_terra_poses.pivot_of) on the design's (DESIGN_PIVOT,
the same measure on hd/idle.png), plus SHIFT[name] columns, its lowest row on the ground, lifted LIFT[name] rows.
The flight: Codex's six frames were not one body (run4 and run5 twisted, run6 balled up), so it is run1-3 only - the
same standing body, the wings top (run2), high (run1), level (run3) - beaten top, high, level, high, every frame
held by its eye on the design's eye (FLY_ALIGN, across and up: the head still, the wings and legs moving) and lifted off the ground with a small bob (TFT's run: she flies).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_terra_poses import pivot_of  # noqa: E402

HERO = "terra"
PPU = 1.45
DESIGN_ROOT = 50              # her standing point: the design's root column (pack_terra_poses' pelvis column 50.4)
SRC = os.path.join(ROOT, "assets", "source", "terra", "hd")
FLAP = ("run2", "run1", "run3", "run1")
FLY_ALIGN = ("run1", "run2", "run3")
POSES = ("a_wind", "a_hit", "q_crouch", "q_pounce", "q_bite", "e_spread", "e_roar", "r_rear", "r_stomp", "r_roar",
         "d_fall", "d_down") + FLY_ALIGN
SHIFT = {}
FLY = 8                       # the flight's height (design rows; 5.5 game px)
LIFT = {"q_pounce": 12}       # the pounce in the air (8 game px)
LIFT_MAX = 14


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


def eye(p):
    """The eye's middle (x, y): her glowing yellow squares (the biggest group's centre)."""
    r, g, b = [p[..., i].astype(int) for i in range(3)]
    m = (p[..., 3] > 0) & (r > 215) & (g > 190) & (b < 110)
    ys, xs = np.nonzero(m)
    return (xs.mean(), ys.mean()) if len(xs) else None


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.pivot = pivot_of(d)[0]
        self.eye = eye(d)
        lefts, rights, tops = [0], [d.shape[1]], [-LIFT_MAX]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y - LIFT_MAX)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_ROOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its hind legs on the design's (the flight: its eye's
        column and row on the design's eye's), its lowest row on the ground."""
        if name in FLY_ALIGN:   # the head held still: its eye on the design's eye, across and up
            e = eye(p)
            return round(self.eye[0] - e[0]) + SHIFT.get(name, 0), round(self.eye[1] - e[1])
        x = self.pivot - meta(name)["pivot"][0]
        return x + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas, lifted `lift` rows; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_terra.py) match these (a frame's start in ticks = ms x 0.06): attack
# 500 ms = atk_dur 30, the blow on atk_st 14 (233 ms: the strike); Rending Bite 667 ms = q_dur 40, the lunge on q_st 14
# (233 ms: the pounce, then the bite as she lands); Dragon's Roar 600 ms = e_dur 36, the roar on e_st 14 (233 ms);
# Earthquake 1833 ms = r_dur 110: rear, stomp (r_t1 30 = 500 ms inside it), rear, stomp (r_t2 58 = 967), rear, stomp
# (r_t3 86 = 1433), the roar to the end. The flight: one beat in 600 ms.
MS = {"idle": [1000], "run": [150] * 4, "attack": [233, 267], "skill": [233, 167, 267], "skill2": [233, 367],
      "ult": [433, 267, 200, 267, 200, 233, 233], "hit": [100, 100], "dead": [100, 200, 700]}
BOB = (0, 1, 2, 1)            # the flight's rows up and down with the beat (the downstroke lifts her)


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n, lift=FLY + BOB[k]) for k, n in enumerate(FLAP)]
    out["attack"] = [f("a_wind"), f("a_hit")]                                  # Rock Claw
    out["skill"] = [f("q_crouch"), f("q_pounce", lift=LIFT["q_pounce"]), f("q_bite")]   # Rending Bite
    out["skill2"] = [f("e_spread"), f("e_roar")]                               # Dragon's Roar
    out["ult"] = [f("r_rear"), f("r_stomp"), f("r_rear"), f("r_stomp"), f("r_rear"), f("r_stomp"), f("r_roar")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down")]
    return out


def frames(C, tags=None):
    out = {}
    for tag, cans in actions(C).items():
        if tags and tag not in tags:
            continue
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()

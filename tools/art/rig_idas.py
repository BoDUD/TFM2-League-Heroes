#!/usr/bin/env python3
"""tft_idas's action frames: Idas's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-30: sprites by Codex from written prompts).

    python tools/art/rig_idas.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_idas.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_idas), then ppu_restyle.py / ppu_hd.py --hero idas

The pictures (tools/art/design_idas_model.py, design_idas_poses.py, design_idas_run.py):
  hd/idle.png         Idas standing side-on facing right, 127 x 98 at PPU 2.45 (40 game px, the top of her crest to
                      her feet): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's density (assets/source/idas/POSE_PROMPTS.md): a_wind a_claw
                      q_rear q_breath e_open e_roar r_wrap r_hold r_burst d_fall d_down;
  hd/run<k>.png       her run, 8 frames of TFT's low bound (assets/source/idas/RUN_PROMPTS.md, design_idas_run.py).
Placing a pose: the pack drew every reference with her root on one canvas column and her lowest point on the ground
line, and Codex placed each pose by its body over its reference; so a pose's pivot (its json: that column) goes on the
design's root column (DESIGN_PIVOT) and its lowest row on the design's ground line. None of her poses leaves the
ground.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "idas"
PPU = 2.45
SRC = os.path.join(ROOT, "assets", "source", "idas", "hd")
DESIGN_PIVOT = 63             # the design's root column (pack_idas_poses' pelvis column 63.1)
POSES = ("a_wind", "a_claw", "q_rear", "q_breath", "e_open", "e_roar", "r_wrap", "r_hold", "r_burst", "d_fall",
         "d_down")
RUN = tuple(f"run{k}" for k in range(1, 9))


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def pivot(name):
    with open(lp(os.path.join(SRC, f"{name}.json" if name in RUN else f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["pivot"]


def picture(name):
    return load(f"{name}.png" if name in RUN else f"pose_{name}.png")


class Canvas:
    def __init__(self, run=True):
        self.d = load("idle.png")
        d = self.d
        self.names = POSES + (RUN if run else ())
        lefts, rights, tops = [0], [d.shape[1]], [0]
        for n in self.names:
            p = picture(n)
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)
        self.outline = D.outline

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its pivot column on the design's, its lowest row on the
        ground."""
        px, _ = pivot(name)
        return DESIGN_PIVOT - px, self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas, lifted `lift` rows; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = picture(name)
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_idas.py) match these (a frame's start in ticks = ms x 0.06): attack
# 467 ms = atk_dur 28, the claw lands on atk_st 14 (233 ms: the claw frame); Golden Breath 600 ms = q_dur 36, breathed
# on q_rel 14 (233 ms: the breath frame, held while the breath's picture runs); Dragon's Roar 500 ms = e_dur 30, the roar
# on e_st 12 (200 ms: the roar frame); Golden Scales 2300 ms = r_t + r_out (138 ticks): the wings close (200 ms), the
# shell held through r_t (1800 ms, a one-row breath), the burst on tick 120 (300 ms)
RUN_MS = [86, 86, 86, 130, 86, 86, 86, 72]       # pack_idas_run.MS: the clip's own spacing in a 720 ms loop
HOLD = 6
MS = {"idle": [1000], "run": RUN_MS, "attack": [233, 234], "skill": [233, 367], "skill2": [200, 300],
      "ult": [200] + [300] * HOLD + [300], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C, run=True):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    if run:
        out["run"] = [f(n) for n in RUN]
    # attack (the wing-arm drawn back, the lunge with the claw slashing down)
    out["attack"] = [f("a_wind"), f("a_claw")]
    # Golden Breath (rearing back drawing breath, the head thrust forward breathing)
    out["skill"] = [f("q_rear"), f("q_breath")]
    # Dragon's Roar (the wings flung open, the roar)
    out["skill2"] = [f("e_open"), f("e_roar")]
    # Golden Scales (crouching into the wings, the shell held with a one-row breath, the burst)
    out["ult"] = [f("r_wrap")] + [f("r_hold", lift=k % 2) for k in range(HOLD)] + [f("r_burst")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (knocked back rearing, fallen on her side)
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down")]
    return out


def frames(C, tags=None, run=True):
    out = {}
    for tag, cans in actions(C, run).items():
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
    run = all(os.path.isfile(lp(os.path.join(SRC, f"{n}.png"))) for n in RUN)
    if not run and not a.review:
        sys.exit("no run frames yet (hd/run1-8.png: tools/art/design_idas_run.py): --review only")
    C = Canvas(run)
    acts = frames(C, a.tags.split(",") if a.tags else None, run)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()

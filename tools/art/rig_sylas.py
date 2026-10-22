#!/usr/bin/env python3
"""league_sylas's action frames: the approved 3/4 design (idle) and Codex's skeleton poses (every action), timed after
League's own clips (the user, 2026-10-20: 3/4 only, 「Codex 照骨架画关键姿势」).

    python tools/art/rig_sylas.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_sylas.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_sylas.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/review_sylas_actions.py --out DIR   # League left / ours right, one GIF

The design (tools/art/design_sylas_model.py: Codex's step-1 take A-1 read back to 65 x 46 = 38 game px at PPU 1.2;
Codex's own face): League's idle seen 3/4 from the front-right - feet planted apart, the manacled fists hanging at his
sides, the gold chains down to the ground and trailing out on both sides.
The idle breathes on the design itself (the upper body, chains included, sets down a row onto the legs and comes back:
League's Sylas_Idle). Every action is Codex's poses (tools/art/design_sylas_poses.py: sixteen of League's frames drawn
on skeletons at the design's segment lengths, read back at the design's scale with the design's own head on each) - the
wind-up, the lash, the whirl, the leap, the stab, the slam, the dash, the throw, the pull, the stagger, the kneel, the
fall and four run frames - each placed with the middle of its trousers on the design's and its lowest row on the ground
(or `lift` rows over it in the air), moved by whole squares only: then `whole` keeps the body (all but the chains) over
his standing point as the idle's is (its middle 2 squares behind it), a few squares forward in the lunges and the pull
(a kneeling or lunging pose's trousers reach far back, so its middle alone would put the body ahead).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_warwick import close_cracks  # noqa: E402
from rig_wukong import CutDesign as _Cut, P, pad  # noqa: E402

HERO = "sylas"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "sylas", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


STAND = 37                     # the column between his feet: the standing point
WAIST = 27                     # the last row of the upper body (the belt's top): the idle's breath sets it down


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    D.part("upper", D.box(0, WAIST, 0, D.W - 1))
    D.part("lower", D.rest())
    return D


def trousers(d):
    """The dark teal trousers' squares (and the scarf's, above): green and blue over red, dark."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (d[..., 3] > 0) & (g > r + 8) & (b > r + 8) & (r < 100) & (g < 140)


def trousers_mid(d):
    """The middle column of a figure's trousers (the lower 60% of the figure: the scarf left out)."""
    m = trousers(d)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    m[:ys.min() + int(0.4 * (ys.max() - ys.min()))] = False
    xs = np.nonzero(m)[1]
    return (xs.min() + xs.max() + 1) / 2


class Form:
    def __init__(self, D, rig_pad=(70, 70, 70, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}

    def pose(self, whole=(0, 0), crouch=0):
        wx, wy = whole
        can = R.compose(self.rig, [(self.L["lower"], dict(dx=wx, dy=wy)), (self.L["upper"], dict(dx=wx, dy=wy + crouch))])
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def posed(self, name, whole=(0, 0), lift=0):
        """A Codex pose (hd/pose_<name>.png) standing where the design stands: the middle of its trousers on the
        design's, its lowest row on the ground - `lift` rows above it (in the air)."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        top = P + self.D.ground - (ys.max() + 1) - lift
        left = P + int(round(trousers_mid(self.D.d) - trousers_mid(d)))
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        y0, y1 = max(0, top), min(lay.shape[0], top + d.shape[0])
        lay[y0:y1, x0:x1] = d[y0 - top:y1 - top, x0 - left:x1 - left]
        can = R.compose(self.rig, [(lay, dict(dx=whole[0], dy=whole[1]))])
        can[self.rig.GY:] = 0
        return can


def form():
    F = Form(design())
    F.rig.idle_canvas = F.pose()
    return F


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_sylas.py) come from these (a frame's start in ticks = ms x 0.06)
# the run 150 ms a frame (2026-10-22, 「塞拉斯局内也是跑的时候跳动频率太高 和之前奎桑提一个问题」: 110 made a 0.44 s cycle)
MS = {"idle": [150] * 8, "run": [150] * 4,
      "attack": [80, 80, 70, 90, 110],            # the lash from 160 ms: a_rel 10
      "attack_p": [100, 100, 150, 150],           # the whirl from 100 ms: p_rel 7
      "skill_w": [100, 120, 140, 140],            # the stab from 100 ms: w_rel 7
      "skill": [110, 130, 130, 130],              # the slam from 110 ms: q_rel 7
      "skill2": [90, 90, 130, 130, 127],          # the dash (7 ticks), the throw from 180 ms (the chain at tick 13)
      "skill2_pull": [150, 150],
      "ult": [100, 150, 120, 130],                # the throw from 100 ms: r_rel 7
      "ult_cast": [150, 120, 150, 100, 80],       # the slam from 270 ms: r2_rel 17
      "ult_dash": [80, 80, 80, 80],
      "hit": [100, 100],
      "dead": [120, 140, 160, 200, 160, 600]}


def frames_all(F):
    p, q = F.pose, F.posed
    out = {}
    # idle (League's Sylas_Idle: a slow breath, the chains swaying a little): the upper body sets down a row and back
    out["idle"] = [p(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # run (League's Sylas_Run: an upright run, the arms pumping, the chains trailing): Codex's four run frames, the body
    # one square higher on the passing frames (run2 / run4 drawn so)
    out["run"] = [q("run1"), q("run2"), q("run3"), q("run4")]
    # auto attack (League's Sylas_Attack_01: leaning back with the near arm swung behind him, then lunging forward
    # with the far arm and its chain flung ahead): wind-up, the lash (the hit), held, back
    out["attack"] = [q("wind"), q("wind", whole=(-1, 0)), q("lash", whole=(-3, 0)), q("lash", whole=(-3, 0)), p()]
    # Petricite Burst (League's Sylas_Attack_Passive: wound up, then the chains whirled round him in a wide crouch)
    out["attack_p"] = [q("wind"), q("spin"), q("spin", whole=(1, 0)), p()]
    # W Kingslayer (League's Sylas_Spell2: a leap with the manacles raised, then the stab forward on landing)
    out["skill_w"] = [q("leap", lift=4), q("stab", whole=(-5, 0)), q("stab", whole=(-5, 0)), p(whole=(1, 0))]
    # Q Chain Lash (League's Sylas_Spell1_Cast: up with the manacles raised, then down on one knee slamming them into
    # the ground in front)
    out["skill"] = [q("leap", lift=3), q("slam", whole=(-8, 0)), q("slam", whole=(-8, 0)), p()]
    # E Abscond (League's Sylas_Spell3_Dash: rushing forward low, the chains streaming) then Abduct (Sylas_Spell4_Cast-
    # like: planted, the far arm thrust forward with the chain)
    out["skill2"] = [q("dash", whole=(5, 0)), q("dash", whole=(6, 0)), q("throw"), q("throw"), p()]
    # Abduct's pull (League's Sylas_Spell3_Bhit_Cast: flying forward level after his chain)
    out["skill2_pull"] = [q("pull", whole=(-6, 0), lift=3), q("pull", whole=(-6, 0), lift=2)]
    # R Hijack, the steal (League's Sylas_Spell4_Cast: wound back, the far arm thrust forward, back)
    out["ult"] = [q("wind"), q("throw"), q("throw"), p()]
    # R, the stolen ult (League shows the robbed champion's own: here up with the manacles raised and down slamming)
    out["ult_cast"] = [q("leap", lift=5), q("leap", lift=7), q("slam", whole=(-8, 0)), q("slam", whole=(-8, 0)), p()]
    # the add-on's melee stolen ult: the leap onto the champion
    out["ult_dash"] = [q("leap", lift=k) for k in (5, 7, 7, 4)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Sylas_Death: struck back, down on his knees, then face down)
    out["dead"] = [q("stagger"), q("stagger", whole=(-1, 0)), q("kneel", whole=(-6, 0)), q("kneel", whole=(-6, 0)),
                   q("lie", whole=(-7, 0), lift=1), q("lie", whole=(-7, 0))]
    return out


def frames(F):
    a = frames_all(F)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = [(c, m) for c, m in zip(cans, ms)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    F = form()
    acts = frames(F)
    if a.audit:
        import rig_wukong as RW
        RW.HERO = HERO
        RW.audit(F, acts, a.audit)
    elif a.review:
        F.rig.review(acts, a.review)
    else:
        F.rig.export(acts)


if __name__ == "__main__":
    main()

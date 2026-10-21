#!/usr/bin/env python3
"""league_ornn's action frames: the approved 3/4 design (idle) and Codex's skeleton poses (every action), timed after
League's own clips (the user, 2026-10-21: 3/4 only, 「Codex 照骨架画关键姿势」, 「有连招要做连招」).

    python tools/art/rig_ornn.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_ornn.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_ornn.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design (tools/art/design_ornn_model.py: Codex's step-1 take A-3 read back to 71 x 66 = 44 game px at PPU 1.5;
Codex's own face): League's idle seen 3/4 from the front-right - hunched, legs planted apart, the big steel hammer low
in the near hand, the smaller one in the molten far hand. The idle breathes on the design itself (the upper body sets
down a row onto the legs and comes back). Every action is Codex's poses (tools/art/design_ornn_poses.py: eighteen of
League's frames drawn on skeletons at the design's segment lengths, read back at the design's scale with the design's
own face) - but the run, drawn on the design itself (ornn_legs.py: his boots stepping under the design's own upper body) -
each placed with the middle between its feet on the design's (the folded, lunging and lying ones by the
middle of the plum apron) and its lowest row on the ground (or `lift` rows over it in the air), moved by whole squares
only.
The combos have their own frames (POSE_PROMPTS.md): Q -> E is `skill` (q_raise, q_slam: the fissure and the pillar)
then `skill2` (charge, the dash) and `skill2_hit` (impact: the pillar shattered, the quake); R1 -> R2 is `ult` (summon,
call: the ram summoned far away, held while it runs back to him) then `ult_butt` (butt_wind, headbutt: the ram sent
back). The kit's ticks (tools/kit/build_ornn.py) come from MS (a frame's start in ticks = ms x 0.06).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ornn_legs as GL  # noqa: E402
import ppu_rig as R  # noqa: E402
from rig_warwick import close_cracks  # noqa: E402
from rig_wukong import CutDesign as _Cut, P, pad  # noqa: E402

HERO = "ornn"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "ornn", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


STAND = 45                     # the column between his feet (under the apron's middle): the standing point
WAIST = 50                     # the last row of the upper body (the belt): the idle's breath sets it down


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    D.part("upper", D.box(0, WAIST, 0, D.W - 1))
    D.part("lower", D.rest())
    return D


def apron(d):
    """The plum leather apron's and boots' squares: dark red-purple, blue over green."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (d[..., 3] > 0) & (r > 45) & (r < 150) & (g < 45) & (b > g + 8) & (r > b + 15)


def apron_mid(d):
    """The middle column of a figure's apron (the lower 45% of the figure: the beard's red left out)."""
    m = apron(d)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    m[:ys.min() + int(0.55 * (ys.max() - ys.min()))] = False
    xs = np.nonzero(m)[1]
    if not len(xs):
        xs = np.nonzero(d[..., 3] > 0)[1]
    return float(np.median(xs))


def feet_mid(d, rows=5):
    """The middle between his outermost feet: the lowest `rows` rows of a standing figure without the steel hammers'
    squares (blue over red) - the apron is hidden behind a hammer in some poses (smash, call)."""
    rgb = d[..., :3].astype(int)
    op = (d[..., 3] > 0) & ~(rgb[..., 2] > rgb[..., 0] + 25)
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys.max() + 1 - rows:ys.max() + 1])[1]
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

    def drawn(self, arr, pad):
        """A frame drawn on the design's own grid (`pad` = (columns, rows) of margin round the design in `arr`): placed
        exactly where the design stands."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        y0, x0 = P - pad[1], P - pad[0]
        lay[y0:y0 + arr.shape[0], x0:x0 + arr.shape[1]] = arr
        can = R.compose(self.rig, [(lay, dict(dx=0, dy=0))])
        can[self.rig.GY:] = 0
        return can

    def posed(self, name, whole=(0, 0), lift=0):
        """A Codex pose (hd/pose_<name>.png) standing where the design stands: the middle of its apron on the design's,
        its lowest row on the ground - `lift` rows above it (in the air)."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        top = P + self.D.ground - (ys.max() + 1) - lift
        mid = apron_mid if name in APRON else feet_mid
        left = P + int(round(mid(self.D.d) - mid(d)))
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        y0, y1 = max(0, top), min(lay.shape[0], top + d.shape[0])
        lay[y0:y1, x0:x1] = d[y0 - top:y1 - top, x0 - left:x1 - left]
        can = R.compose(self.rig, [(lay, dict(dx=whole[0], dy=whole[1]))])
        can[self.rig.GY:] = 0
        return can


# poses whose feet are not under him (in the air, folded, lying, a foot lifted in the run): placed by the apron
APRON = {"charge", "headbutt", "kneel", "lie", "run1", "run2", "run3", "run4"}


def form():
    F = Form(design())
    F.rig.idle_canvas = F.pose()
    return F


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame
MS = {"idle": [160] * 8, "run": [110] * 8,
      "attack": [110, 123, 100, 90, 80],           # the smash from 233 ms: atk_st 14
      "skill_w": [125] * 6,                        # the breath held 750 ms: w_t 45
      "skill": [100, 100, 120, 100, 80],           # the fissure from 200 ms: q_rel 12
      "skill2": [100, 100],                        # the charge, looped while he runs (e_anim 20)
      "skill2_hit": [120, 113],                    # the quake on contact: e_hit_t 14
      "ult": [100, 100, 200, 200, 200, 200],       # the call from 200 ms (r_rel 12), held while the ram runs back
      "ult_butt": [70, 63, 130, 137],              # the headbutt from 133 ms: r_butt_rel 8, r_butt_t 24
      "hit": [100, 100],
      "dead": [120, 140, 160, 200, 160, 600]}


def frames_all(F):
    p, q = F.pose, F.posed
    out = {}
    # idle (League's Ornn_Idle1: a slow heavy breath): the upper body sets down a row and back
    out["idle"] = [p(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # run (League's Ornn_Run: a heavy hunched trot, the hammers held): the design's upper body with his boots stepping in
    # eight phases (tools/art/ornn_legs.py - the user, 2026-10-21, on Codex's four run poses: 「奥恩走路是这样走的？」 then
    # 「跑步用定稿的上身，你自己画腿的跑步循环（像格雷福斯那样），大锤只轻微摆动」)
    out["run"] = [F.drawn(GL.frame(F.D.d, k), (4, 4)) for k in range(8)]
    # auto attack (League's Ornn_Attack1: the big hammer raised over his head, then smashed down ahead): raise, the
    # smash (the hit), held, back
    out["attack"] = [q("raise"), q("raise", whole=(-1, 0)), q("smash"), q("smash"), p()]
    # W Bellows Breath (League's Ornn_Spell2: leaning forward, breathing fire for 0.75 s): the breath, the head a square
    # forward and back
    out["skill_w"] = [q("breath"), q("breath", whole=(1, 0)), q("breath"), q("breath", whole=(1, 0)), q("breath"), p()]
    # Q Volcanic Rupture (League's Ornn_Spell1: the molten fist raised, then slammed into the ground) - the combo's start
    out["skill"] = [q("q_raise"), q("q_raise", lift=1), q("q_slam"), q("q_slam"), p()]
    # E Searing Charge (League's Ornn_Spell3_Dash: low, horns first like a ram)
    out["skill2"] = [q("charge"), q("charge", lift=1)]
    # E's contact (League's Ornn_Spell3_Hit: rearing up after the crash) - the pillar shattered, the quake
    out["skill2_hit"] = [q("impact"), q("impact", whole=(-1, 0))]
    # R Call of the Forge God (League's Ornn_Spell4_Windup / Spell4): the hammer raised, then the call; held while the
    # ram runs back to him
    out["ult"] = [q("summon"), q("summon", lift=1), q("call"), q("call", whole=(1, 0)), q("call"), q("call", whole=(1, 0))]
    # R's second step (League's Ornn_Spell4_Charge / Spell4_Hit: drawn back, then the headbutt that sends the ram back)
    out["ult_butt"] = [q("butt_wind"), q("butt_wind", whole=(-1, 0)), q("headbutt"), q("headbutt", whole=(1, 0))]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Ornn_Death: struck back, down on his knees, then face down)
    out["dead"] = [q("stagger"), q("stagger", whole=(-1, 0)), q("kneel"), q("kneel"), q("lie", lift=1), q("lie")]
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

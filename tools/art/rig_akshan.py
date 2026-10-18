#!/usr/bin/env python3
"""league_akshan's action frames posed from the approved design's own squares (the user, 2026-10-18: 「动作帧就参照塔姆
那种方法做吧 做好后自己review 真正没问题了完美了喊我review」), with one arm pose drawn by Codex (「做不了就让codex做」).

    python tools/art/rig_akshan.py --parts DIR       # the design with its parts tinted
    python tools/art/rig_akshan.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_akshan.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_akshan.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design: Codex's step-1 round-2 take A-1 read back on its own 10 px grid and brought from 63 to 57 rows hair to soles
by whole rows / columns (tools/art/design_akshan_cut.py --take codex_model2/akshan-model2-A-1.png --size 10 --hair 13
--face 17 33 22 42; PPU 1.5, 38 game rows), 46 x 69 squares: the gun's hooks row 0, the hair's top row 12, the soles
row 68. Every pose is lossless (memory no-deformation-lossless-poses): the design's squares only moved whole - the whole
figure, the body set down at most two rows over the boots, the boots stepping, the whole standing frame turned a quarter
to lie - nothing drawn again at another angle, and no part moved that is not a whole limb (the first draft slid and
turned the forearm with the gun alone: 「手都断了？」 - an arm apart from its shoulder).
The forward gun arm the design does not have (attack, Q, E's shots, R) is Codex's (POSE_PROMPTS.md, gangplank's way):
assets/source/akshan/hd/pose_aim.png + pose_aim_edit.png (tools/art/design_akshan_poses.py) - only the squares of the
edit mask are put, moving with the upper body; everything else stays the design's.
Parts: the gun arm (the pistol, the gloved hand round its grip and the braced forearm: left out where the stamp is
used), the near and far lower legs (the boots and the shins below the cape's hems); the rest is the body.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_wukong as W  # noqa: E402  (CutDesign, pad, sheet, audit, _steps)

HERO = "akshan"
W.HERO = HERO                                   # CutDesign and the audit's file names read it
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "akshan", "hd")
P = W.P


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


# ------------------------------------------------------------------------------------------------- the design's parts
ELBOW = (6.5, 38.5)                             # the first draft's turn point (pack_akshan_poses' rejected posings)
STAND = 25                                      # the column between the boots: the standing point
CROUCH_MAX = 2                                  # the body sets down at most this many rows over the boots


def design():
    d = load("design.png")
    D = W.CutDesign(d, px=STAND)
    # the gun arm: the hooks (rows 0-11), the gun body with the hand on its grip (rows 12-30, left of the transparent
    # gap at column 12 that parts it from the hair), the gold bracer and the forearm down to the elbow (rows 31-37)
    D.part("gun", D.box(0, 11, 0, 17) | D.box(12, 30, 0, 11) | D.box(31, 37, 2, 9))
    # the boots (a colour map of rows 52-68 at 26x): the cape's gold hems reach row 61 on the left (columns 1-9) and row
    # 62 on the right (columns 40-45), the shins come down to row 62 - so only rows 63-68 step (near boot columns 6-18,
    # far boot 34-45); the shins and the hems stay on the body (the first cut took the left hem's edge along: a notch)
    D.part("near_leg", D.box(63, 68, 6, 18))
    D.part("far_leg", D.box(63, 68, 34, 45))
    D.part("body", D.rest())
    return D


TINT = {"gun": (255, 60, 60), "near_leg": (255, 220, 0), "far_leg": (0, 220, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


class Form:
    """The design's layers (+ Codex's aim stamp); pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: W.pad(D.layer(k)) for k in D.order}
        self.stamp = None
        sp, ep = os.path.join(SRC, "pose_aim.png"), os.path.join(SRC, "pose_aim_edit.png")
        if os.path.isfile(lp(sp)) and os.path.isfile(lp(ep)):
            self.stamp = (load("pose_aim.png"), np.asarray(Image.open(lp(ep))) > 0)

    def pose(self, crouch=0, whole=(0, 0), legs=None, leg_layers=None, aim=False, gun_rot=0):
        """crouch: rows (0..CROUCH_MAX) the body sets down onto the boots; whole: the whole figure; legs: ((near dx, dy),
        (far dx, dy)) for the boots; aim: Codex's forward gun arm (the stamp) instead of the raised one; gun_rot: only
        for the pack's picture of the rejected posings."""
        if not 0 <= crouch <= CROUCH_MAX:
            raise ValueError(f"crouch {crouch}: the body sets down 0..{CROUCH_MAX} rows over the boots")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        legs_l = leg_layers if leg_layers is not None else [(L["far_leg"], dict(dx=wx + flx, dy=wy + fly)),
                                                             (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly))]
        layers = [*legs_l, (L["body"], dict(dx=ux, dy=uy))]
        if not aim:
            layers.append((L["gun"], dict(dx=ux, dy=uy, rot=gun_rot, about=ELBOW)))
        can = R.compose(self.rig, layers)
        if aim:
            can = self.put_stamp(can, ux, uy)
        return can

    def put_stamp(self, can, ux, uy):
        if self.stamp is None:
            raise SystemExit("no aim stamp yet: run tools/art/design_akshan_poses.py on Codex's pose")
        st, ed = self.stamp
        rig = self.rig
        out = can.copy()
        ys, xs = np.nonzero(ed)
        out[rig.oy + uy + ys, rig.ox + ux + xs] = st[ys, xs]
        return out


def form():
    return Form(design(), rig_pad=(40, 60, 40, 20))


# ------------------------------------------------------------------------------------------------- the actions
AIM = dict(gun_rot=3)                           # the first draft's level forearm (only for the pack's rejected posings)

# ms per frame; the kit's ticks (tools/kit/build_akshan.py) come from these
MS = {"idle": [150] * 8, "run": [100] * 8, "attack": [70, 60, 70, 60, 80, 90], "skill": [70, 80, 90, 120],
      "skill2": [70, 70], "e_swing": [115, 115], "e_roll": [80, 90], "ult": [70, 70], "ult_ch": [160, 160],
      "ult_shot": [50, 50], "hit": [100, 100], "dead": [100, 110, 120, 150, 200, 500]}
AIMED = ("attack", "skill", "e_swing", "ult", "ult_ch", "ult_shot")


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    # idle: the body sets down a row onto the boots and rises
    out["idle"] = [p(crouch=c) for c in [0, 0, 0, 1, 1, 1, 1, 0]]
    if F.stamp is not None:
        # the double shot (League's Attack1 / Attack2: the arm held out, two shots 0.12 s apart): aimed, the first
        # shot's kick (the whole figure back a column), aimed, the second kick, aimed, the gun raised again
        out["attack"] = [p(aim=True), p(aim=True, whole=(-1, 0)), p(aim=True), p(aim=True, whole=(-1, 0)), p(aim=True),
                         p()]
        # Q Avengerang (League's Spell1: the throw): set, the throw with a step in (the boomerang is the effect), back
        out["skill"] = [p(crouch=1), p(aim=True, whole=(1, 0)), p(aim=True, whole=(1, 0), crouch=1), p()]
        # E's swing: off the ground, aimed, shooting (the second frame a kick back)
        out["e_swing"] = [p(aim=True, whole=(1, -6)), p(aim=True, whole=(0, -6))]
        # R Comeuppance: aimed and lowered; the channel breathing a row; the shots' kick
        out["ult"] = [p(aim=True, crouch=1), p(aim=True, crouch=2)]
        out["ult_ch"] = [p(aim=True, crouch=2), p(aim=True, crouch=1)]
        out["ult_shot"] = [p(aim=True, crouch=2, whole=(-1, 0)), p(aim=True, crouch=2)]
    # E Heroic Swing's hook (League's Spell3: the gun raised, the hook shot up): set, then up off the ground
    out["skill2"] = [p(crouch=1), p(whole=(0, -2))]
    # the roll off the rope: landing low, rising
    out["e_roll"] = [p(crouch=2, whole=(1, 0)), p(crouch=1)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Death: he staggers back and falls): back, lower, lower, then the whole standing frame turned a
    # quarter (lossless) to lie on his back, head away from the enemy
    lying = R.lie(rig, p(), k=1, dx=-4)
    out["dead"] = [p(whole=(-1, 0)), p(crouch=1, whole=(-2, 0)), p(crouch=2, whole=(-2, 0)), lying, lying.copy(),
                   lying.copy()]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# The design's own lower legs moved whole under the cape (memory codex-legs-deform): each boot steps on its own side,
# planted and sliding back, then lifted and carried forward, the far one half a cycle later; the body set down a row on
# each contact (rig_wukong's walk, stride 2: the boots never meet).
WALK_STEP = dict(W._steps(2, (1, 2, 1)), rise=[0, 0, 1, 0, 0, 0, 1, 0])


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    L = F.L
    for (ndx, nup), (fdx, fup), bob, up in zip(st["near"], st["far"], st["bob"], st["rise"]):
        legs = [(L["far_leg"], dict(dx=fdx, dy=-fup - up)), (L["near_leg"], dict(dx=ndx, dy=-nup - up))]
        out.append(F.pose(whole=(0, bob - up), leg_layers=legs))
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order (the aimed tags only once the stamp exists)."""
    a = frames_all(F)
    order = ["idle", "run", "attack", "skill", "skill2", "e_swing", "e_roll", "ult", "ult_ch", "ult_shot", "hit", "dead"]
    a["run"] = walk(F)
    out = {}
    for tag in order:
        if tag not in a:
            continue
        cans, ms = a[tag], MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    if not (a.audit or a.review or a.parts):
        F = form()
        if F.stamp is None:
            sys.exit("no aim stamp yet: the aimed actions cannot be exported")
        F.rig.export(frames(F))
        return
    if a.audit or a.review:
        F = form()
        acts = frames(F)
        if a.audit:
            W.audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in D.parts.items()})
    F = form()
    idle = F.pose()
    ref = F.rig.canvas()
    ref[F.rig.oy:F.rig.oy + D.H, F.rig.ox:F.rig.ox + D.W] = D.d
    print("idle vs design: squares differing", int((np.abs(idle.astype(int) - ref.astype(int)).sum(-1) > 0).sum()))


if __name__ == "__main__":
    main()

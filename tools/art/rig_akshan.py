#!/usr/bin/env python3
"""league_akshan's action frames posed from the approved design's own squares (the user, 2026-10-18: 「动作帧就参照塔姆
那种方法做吧 做好后自己review 真正没问题了完美了喊我review」).

    python tools/art/rig_akshan.py --parts DIR       # the design with its parts tinted + pose tries
    python tools/art/rig_akshan.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_akshan.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_akshan.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design: Codex's step-1 round-2 take A-1 read back on its own 10 px grid and brought from 63 to 57 rows hair to soles
by whole rows / columns (tools/art/design_akshan_cut.py --take codex_model2/akshan-model2-A-1.png --size 10 --hair 13
--face 17 33 22 42; PPU 1.5, 38 game rows), 46 x 69 squares: the gun's hooks row 0, the hair's top row 12, the soles
row 68. Every pose is lossless (memory no-deformation-lossless-poses): parts cut square by square from the design and
only moved by whole squares and quarter turns about half-integer pivots; nothing is drawn again at another angle.
Parts (from a colour map of the design): the gun arm - the relic pistol, the pale-gloved hand round its grip and the
gold-braced forearm up to the elbow (one rigid piece: the hand and the grip are drawn into each other), image left,
raised; the near lower leg and the far lower leg (the boots and the shins below the cape's hems); the rest is the body
(the head, the scarf, the sash, the far arm on the hip, the cape, the belt and the cloth, the thighs).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_wukong as W  # noqa: E402  (CutDesign, pad, spans, sheet, audit)

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
ELBOW = (6.5, 38.5)                             # the gun arm turns about the elbow (its bottom, where the upper arm meets it)
STAND = 25                                      # the column between the boots: the standing point


def design():
    d = load("design.png")
    D = W.CutDesign(d, px=STAND)
    # the gun arm: the hooks (rows 0-11), the gun body with the hand on its grip (rows 12-30, left of the transparent
    # gap at column 12 that parts it from the hair), the gold bracer and the forearm down to the elbow (rows 31-37)
    D.part("gun", D.box(0, 11, 0, 17) | D.box(12, 30, 0, 11) | D.box(31, 37, 2, 9))
    # the upper arm (the skin from the elbow up to the shoulder pad, rows 36-40): hidden when the arm reaches forward
    skin = W.classes(d, [(206, 98, 48), (249, 146, 79), (161, 74, 24), (136, 51, 24)])
    D.part("upper", D.box(36, 40, 6, 13) & skin)
    # the lower legs under the cape's hems (a colour map of rows 56-68): near - the shin and the boot (rows 60-68,
    # columns 7-19); far - the shin (rows 60-62, columns 33-38, left of the right hem's gold) and the boot (rows 63-68)
    D.part("near_leg", D.box(60, 68, 7, 19))
    D.part("far_leg", D.box(60, 62, 33, 38) | D.box(63, 68, 33, 44))
    D.part("body", D.rest())
    return D


TINT = {"gun": (255, 60, 60), "upper": (255, 0, 255), "near_leg": (255, 220, 0), "far_leg": (0, 220, 255)}


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
    """The design's layers; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: W.pad(D.layer(k)) for k in D.order}

    def pose(self, crouch=0, whole=(0, 0), gun=(0, 0), gun_rot=0, legs=None, leg_layers=None, gun_under=False,
             reach=False):
        """crouch: rows the body (with the gun arm) sets down onto the lower legs; whole: the whole figure; gun: the gun
        arm moved (dx, dy); gun_rot: quarter turns counter-clockwise about ELBOW (3 = one clockwise: the gun points
        forward, level); legs: ((near dx, dy), (far dx, dy)); gun_under: the gun arm drawn behind the body; reach: the
        upper arm hidden (the arm reaching forward across him)."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        legs_l = leg_layers if leg_layers is not None else [(L["far_leg"], dict(dx=wx + flx, dy=wy + fly)),
                                                             (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly))]
        gun_l = (L["gun"], dict(dx=ux + gun[0], dy=uy + gun[1], rot=gun_rot, about=ELBOW))
        upper = [] if reach else [(L["upper"], dict(dx=ux, dy=uy))]
        layers = [*legs_l, *([gun_l] if gun_under else []), (L["body"], dict(dx=ux, dy=uy)), *upper,
                  *([] if gun_under else [gun_l])]
        can = R.compose(self.rig, layers)
        if reach:
            can = self.drop_stub(can, ux, uy)
        return can

    def drop_stub(self, can, ux, uy):
        """The upper arm's outline left round where it was (rows 34-42, columns 3-14): outline squares that no longer
        touch a coloured square are taken away (the arm reaches forward across him, its upper part behind)."""
        D, rig = self.D, self.rig
        out = can.copy()
        y0, y1 = rig.oy + uy + 34, rig.oy + uy + 43
        x0, x1 = rig.ox + ux + 3, rig.ox + ux + 15
        dark = np.zeros(out.shape[:2], bool)
        op = out[..., 3] > 0
        dark[op] = np.abs(out[op][:, :3].astype(int) - np.array(D.outline)).sum(-1) < 30
        for _ in range(3):
            col = op & ~dark
            near = ndimage.binary_dilation(col, structure=R.CROSS)
            orphan = dark & ~near
            orphan[:y0] = False
            orphan[y1:] = False
            orphan[:, :x0] = False
            orphan[:, x1:] = False
            if not orphan.any():
                break
            out[orphan] = 0
            op = out[..., 3] > 0
            dark &= op
        return out


def form():
    return Form(design(), rig_pad=(40, 50, 40, 20))


# ------------------------------------------------------------------------------------------------- the actions
AIM = dict(gun_rot=3)                           # the gun level, pointing forward from the elbow

# ms per frame; the kit's ticks (tools/kit/build_akshan.py) come from these
MS = {"idle": [150] * 8, "run": [100] * 8, "attack": [70, 60, 70, 60, 80, 90], "skill": [70, 80, 90, 120],
      "skill2": [70, 70], "e_swing": [115, 115], "e_roll": [80, 90], "ult": [70, 70], "ult_ch": [160, 160],
      "ult_shot": [50, 50], "hit": [100, 100], "dead": [100, 110, 120, 150, 200, 500]}


def tries(F):
    p = F.pose
    return [p(), p(gun=(15, -5), reach=True, **AIM), p(gun=(17, -6), reach=True, **AIM), p(gun=(13, -5), gun_under=True, **AIM),
            p(gun=(16, -4), gun_under=True, **AIM), p(gun=(18, -8), reach=True, **AIM), p(gun=(12, -3), **AIM), p(gun=(20, -5), reach=True, **AIM)]


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    # idle: the body sets down a row onto the boots and rises
    out["idle"] = [p(crouch=c) for c in [0, 0, 0, 1, 1, 1, 1, 0]]
    # the double shot (League's Attack1 / Attack2: the gun brought down level, two shots 0.12 s apart): level, the
    # first shot's kick (the arm back a column), level, the second kick, level, raised again
    aim = dict(gun=(17, -6), reach=True, **AIM)
    kick = dict(gun=(16, -6), reach=True, **AIM)
    out["attack"] = [p(**aim), p(whole=(-1, 0), **kick), p(**aim), p(whole=(-1, 0), **kick), p(**aim), p()]
    # Q Avengerang (League's Spell1: the boomerang thrown overarm): the arm drawn back up, the throw level and a step in,
    # held, back (the boomerang is the effect)
    out["skill"] = [p(gun=(-2, 0)), p(whole=(1, 0), crouch=1, **aim), p(whole=(1, 0), crouch=1, **aim), p()]
    # E Heroic Swing: the hook thrown up (the arm raised higher), the swing (off the ground, the boots drawn up, the gun
    # level, shooting - two frames, the second a kick), the roll off (low, crouched)
    out["skill2"] = [p(gun=(0, -2)), p(crouch=1, gun=(0, -3))]
    swing = dict(whole=(1, -6), legs=((1, -2), (1, -2)))
    out["e_swing"] = [p(**swing, **aim), p(**swing, **kick)]
    out["e_roll"] = [p(crouch=3, whole=(1, 0), legs=((1, 0), (-1, 0))), p(crouch=2)]
    # R Comeuppance (League's Channel: aiming low and steady): the gun brought level, the stance lowered; the channel
    # (the arm steady, the body breathing a row); the shots' kick
    low = dict(crouch=2, **aim)
    out["ult"] = [p(crouch=1, **aim), p(**low)]
    out["ult_ch"] = [p(**low), p(crouch=3, **aim)]
    out["ult_shot"] = [p(crouch=2, whole=(-2, 0), **kick), p(**low)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]

    # the death (League's Death: he staggers and drops): back, low, then down to the ground - the body set down over the
    # boots, which draw in under him, cut at the ground line
    def ground(can):
        out_ = can.copy()
        out_[rig.GY:] = 0
        return out_
    sit = ground(p(crouch=9, whole=(-2, 0), legs=((3, 0), (-3, 0)), **aim))
    out["dead"] = [p(whole=(-1, 0)), p(crouch=2, whole=(-2, 0)), p(crouch=4, whole=(-2, 0), legs=((1, 0), (-1, 0))),
                   ground(p(crouch=6, whole=(-2, 0), legs=((2, 0), (-2, 0)), **aim)), sit, sit.copy()]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# The design's own lower legs moved whole under the cape (memory codex-legs-deform): each boot steps on its own side,
# planted and sliding back, then lifted and carried forward, the far one half a cycle later; the body set down a row on
# each contact (rig_wukong's walk, stride 2).
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
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": walk(F), **{k: v for k, v in a.items() if k != "idle"}}
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
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
    t = [F.rig.finish(c) for c in tries(F)]
    W.sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    W.sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""league_volibear's action frames posed from the approved designs' own squares (2026-10-19: the actions are not drawn
by Codex; League's clips are the reference, tools/lol/anim_graph.py Volibear + pose_ref.py).

    python tools/art/rig_volibear.py --parts DIR       # the designs with their parts tinted + pose tries (12x)
    python tools/art/rig_volibear.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_volibear.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_volibear.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_volibear_model.py; the user's picks: B, 44 game px, PPU 1.2): the 3/4 front view
hd/modelB.png (51 x 54, Codex's step-1 B-2 read back on its 21 px grid; ear top row 0, soles row 53) and the side-on
view hd/modelS_cut.png (33 x 54, side-2 cut to the same rows), whose head rows 0-10 are the front view's own squares
(SIDE_HEAD: Codex drew the same head 8 columns left, with the earring - one face in every frame, memory
one-face-all-frames). Every pose is lossless (memory no-deformation-lossless-poses): parts cut square by square from a
design and only moved by whole squares, quarter turns about integer pivots and mirror images.
Front parts: the near arm (image left: the whole arm from the shoulder fur to the claws, ringed by its own outline),
the far arm (image right, from the shoulder under the far tress to the claws), the near and far lower legs (from row
LEG_TOP: they part there); the rest is the body (head, shoulders, chest with the tresses, belly). The arms turn in
quarter turns about their shoulders: up (2), forward (1 for the near arm: across the chest, lowered below the chin),
back (3). Side parts: the rear and the front leg (the near arm is the whole back half in that view: it never moves,
so the side view only walks and charges - the standing actions are the front view's).
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
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet, _steps  # noqa: E402

HERO = "volibear"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "volibear", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def dark(d):
    return (d[..., 3] > 0) & (d[..., :3].astype(int).sum(-1) < 60)


def ringed(d, m):
    """m with the outline squares round it (an arm keeps its own outline)."""
    return m | (ndimage.binary_dilation(m, structure=R.CROSS) & dark(d))


# ------------------------------------------------------------------------------------------------- the front view
STAND = 25                     # the column between the feet: the standing point
NEAR_SHOULDER = (13.0, 15.0)   # the near arm turns about this corner (the top of the arm under the shoulder fur)
FAR_SHOULDER = (40.0, 15.0)
# a turned arm leaves its shoulder cap (the rows above ARM_TOP, inside the joint) out: turned with the arm the cap stuck
# out as a white wedge beside the body, and left on the body it stood up as a spike
ARM_TOP = 16
LEG_TOP = 42                   # the legs part from this row down: near columns <= LEG_X, far > LEG_X
LEG_X = 25


def front():
    d = load("modelB.png")
    D = CutDesign(d, px=STAND)
    op = d[..., 3] > 0
    lbl, _ = ndimage.label(op & ~dark(d))
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    near = lbl == lbl[25, 6]                                   # the near arm's own fur, closed off by its outline
    D.part("near_arm", ringed(d, near) & (xx <= 18))
    far = op & (yy >= 13) & (yy <= 47) & (((yy <= 38) & (xx >= 39)) | ((yy > 38) & (xx >= 40)))
    far &= ~dark(d) | ndimage.binary_dilation(far & ~dark(d), structure=R.CROSS)
    D.part("far_arm", ringed(d, far & ~dark(d)) & (xx >= 38))
    legs = op & (yy >= LEG_TOP) & ~D.parts["near_arm"] & ~D.parts["far_arm"]
    D.part("near_leg", legs & (xx <= LEG_X))
    D.part("far_leg", legs & (xx > LEG_X))
    D.part("body", D.rest())
    return D


# ------------------------------------------------------------------------------------------------- the side view
SIDE_STAND = 17
SIDE_HEAD = (0, 10, 8)         # rows 0-10 of the side view = the front view's, 8 columns right of it there
SIDE_LEG_TOP = 39


def side():
    d = load("modelS_cut.png")
    f = load("modelB.png")
    r0, r1, k = SIDE_HEAD
    for y in range(r0, r1 + 1):
        d[y] = 0
        d[y, :] = f[y, k:k + d.shape[1]]
    D = CutDesign(d, px=SIDE_STAND)
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    lbl, _ = ndimage.label(op & ~dark(d))
    rear = (lbl == lbl[48, 3]) & (yy >= SIDE_LEG_TOP)
    D.part("rear_leg", ringed(d, rear) & (yy >= SIDE_LEG_TOP) & (xx <= 12))
    D.part("front_leg", op & (yy >= SIDE_LEG_TOP) & (xx >= 17))
    D.part("body", D.rest())
    return D


TINT = {"near_arm": (60, 120, 255), "far_arm": (0, 220, 120), "near_leg": (255, 220, 0), "far_leg": (0, 220, 255),
        "rear_leg": (255, 220, 0), "front_leg": (0, 220, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        if name in D.parts:
            m = D.parts[name]
            out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


# both views on one canvas: the same width, height, standing column and ground row
PAD_TOP, PAD_BOTTOM, PAD_LEFT = 40, 20, 50
WIDTH = 51 + 50 + 60


class Form:
    """The front view's layers (pose) and the side view's (side_pose) -> canvases of one rig."""

    def __init__(self):
        self.D, self.S = front(), side()
        left_s = PAD_LEFT + STAND - SIDE_STAND
        self.rig = R.Rig(self.D, pad=(PAD_LEFT, WIDTH - 51 - PAD_LEFT, PAD_TOP, PAD_BOTTOM))
        self.srig = R.Rig(self.S, pad=(left_s, WIDTH - 33 - left_s, PAD_TOP, PAD_BOTTOM))
        assert (self.rig.CX, self.rig.GY, self.rig.CW, self.rig.CH) == (self.srig.CX, self.srig.GY, self.srig.CW,
                                                                        self.srig.CH)
        self.L = {k: pad(self.D.layer(k)) for k in self.D.order}
        for k in ("near_arm", "far_arm"):
            cap = self.L[k].copy()
            cap[:P + ARM_TOP] = 0
            self.L[k + "_turned"] = cap
        self.SL = {k: pad(self.S.layer(k)) for k in self.S.order}
        self.ref_holes = None

    def pose(self, crouch=0, whole=(0, 0), near=(0, 0), near_rot=0, far=(0, 0), far_rot=0, legs=None,
             near_back=False, far_front=False, fill=True):
        """crouch: rows the body (with both arms) sets down onto the lower legs; whole: the whole figure; near / far:
        an arm moved (dx, dy), *_rot quarter turns counter-clockwise about its shoulder (near 1: forward across the
        chest, 2: up, 3: back; far 1: forward, 2: up); near_back: the near arm drawn behind the body (raised behind the
        head); far_front: the far arm over the body (thrust forward); legs: ((near dx, dy), (far dx, dy))."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        far_l = (L["far_arm_turned" if far_rot % 4 else "far_arm"], dict(dx=ux + far[0], dy=uy + far[1], rot=far_rot, about=FAR_SHOULDER))
        near_l = (L["near_arm_turned" if near_rot % 4 else "near_arm"], dict(dx=ux + near[0], dy=uy + near[1], rot=near_rot, about=NEAR_SHOULDER))
        layers = [*([] if far_front else [far_l]), *([near_l] if near_back else []),
                  (L["far_leg"], dict(dx=wx + flx, dy=wy + fly)), (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly)),
                  (L["body"], dict(dx=ux, dy=uy)), *([far_l] if far_front else []),
                  *([] if near_back else [near_l])]
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    def side_pose(self, crouch=0, whole=(0, 0), legs=None):
        """The side view: the body set down crouch rows over the legs, legs ((front dx, dy), (rear dx, dy))."""
        wx, wy = whole
        (fx, fy), (rx, ry) = legs or ((0, 0), (0, 0))
        S = self.SL
        layers = [(S["rear_leg"], dict(dx=wx + rx, dy=wy + ry)), (S["front_leg"], dict(dx=wx + fx, dy=wy + fy)),
                  (S["body"], dict(dx=wx, dy=wy + crouch))]
        return R.compose(self.srig, layers)

    MOST = _Form.MOST
    close_holes = _Form.close_holes


def tries(F):
    p = F.pose
    return [p(), p(near_rot=3), p(near_rot=1, near=(0, 6)), p(near_rot=2, near_back=True),
            p(far_rot=1), p(far_rot=2), p(crouch=2), F.side_pose()]


# ------------------------------------------------------------------------------------------------- the actions
MS = {"idle": [150] * 8, "run": [100] * 8, "attack": [90, 110, 100, 120, 80], "attack_w": [80, 90, 100, 120, 80],
      "skill_run": [70] * 6, "skill": [80, 70, 120, 140], "skill2": [100, 120, 167, 120],
      "ult": [100, 150, 200, 550], "ult_land": [70, 130, 200], "hit": [100, 100],
      "dead": [100, 110, 120, 150, 60, 60, 100, 500]}


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    out["idle"] = [p(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    back = dict(near_rot=3, near=(2, 2))                       # the near arm drawn back, claws behind him
    raised = dict(near_rot=2, near_back=True)                  # the near arm up behind the head
    # the near arm swung forward passes BEHIND the body (turned across the chest it covered the tresses as a white slab):
    # only its forearm and claws show past his far side
    swipe = dict(near_rot=1, near=(4, 7), near_back=True)
    thrust = dict(far_rot=1, far=(-1, 5))                      # the far arm thrust forward at chest height
    # auto attack (League's Volibear_Attack_1: one arm drawn back and raised high, then raked down forward, the body
    # thrown after it): back, up, the rake (frame 3, both claws forward), followed through, standing
    out["attack"] = [p(crouch=1, whole=(-1, 0), **back), p(whole=(-1, 0), **raised),
                     p(crouch=1, whole=(2, 0), **swipe, **thrust), p(crouch=1, whole=(3, 0), **thrust), p()]
    # W Frenzied Maul (Volibear_Spell2_Slash: a lunge with both claws forward and the bite)
    out["attack_w"] = [p(crouch=1, whole=(-1, 0), **back), p(crouch=2, whole=(2, 0), **swipe, **thrust),
                       p(crouch=2, whole=(4, 0), **swipe, **thrust), p(crouch=1, whole=(3, 0), **thrust), p()]
    # Q Thundering Smash (volibear_spell1_attack: he rears up with both arms high and slams down on the target)
    out["skill"] = [p(whole=(0, -3), legs=((0, -1), (0, -1)), **raised, far_rot=2),
                    p(whole=(1, -5), legs=((0, -2), (0, -2)), **raised, far_rot=2),
                    p(crouch=2, whole=(3, 0), **swipe, far_rot=1, far=(-1, 7)),
                    p(crouch=1, whole=(2, 0), **thrust)]
    # E Sky Splitter (volibear_spell3: one arm raised straight up to the sky, held, down): gathering with the arm back,
    # raised, raised with a row's rise of the arm (the call), down
    out["skill2"] = [p(crouch=1, **back), p(**raised), p(crouch=1, **raised, near=(0, -2)), p(crouch=1)]
    # R Stormbringer (Volibear_Spell4_Ground_Pound): crouched, the spring, in the air with both arms up (held while he
    # flies), then ult_land: the slam with both arms down in front, the rebound, up
    air = p(whole=(1, -8), legs=((0, -2), (0, -2)), **raised, far_rot=2)
    out["ult"] = [p(crouch=2, **back), p(whole=(0, -4), legs=((0, -1), (0, -1)), **raised, far_rot=2), air, air.copy()]
    out["ult_land"] = [p(crouch=2, whole=(1, 0), **swipe, far_rot=1, far=(-1, 8)),
                       p(crouch=1, whole=(1, 0), **thrust), p(crouch=1)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (volibear_death): staggers back, sinks, falls on his back, bounces once on the ground
    body = p(crouch=2, whole=(-3, 0))
    lie = lambda sink: R.lie(rig, body, k=1, dx=-4, sink=sink)
    out["dead"] = [p(whole=(-1, 0)), p(crouch=1, whole=(-2, 0)), p(crouch=2, whole=(-3, 0)), lie(-3), lie(0),
                   lie(-1), lie(0), lie(0)]
    return out


# ------------------------------------------------------------------------------------------------- the walk (side view)
SIDE_TAGS = ("run", "skill_run")
WALK = dict(_steps(3, (1, 2, 1)), rise=[0, 0, 1, 0, 0, 0, 1, 0])
CHARGE = dict(_steps(4, (2, 3, 2)), rise=[0, 1, 1, 0, 0, 1, 1, 0])


def walk(F, st, crouch=0, n=8):
    out = []
    for (fdx, fup), (rdx, rup), bob, up in list(zip(st["near"], st["far"], st["bob"], st["rise"]))[:n]:
        out.append(F.side_pose(crouch=crouch + bob, whole=(0, -up), legs=((fdx, -fup), (rdx, -rup))))
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    charge = walk(F, CHARGE, crouch=1)
    a = {"idle": a["idle"], "run": walk(F, WALK), "skill_run": charge[::2] + charge[1:4:2],
         **{k: v for k, v in a.items() if k != "idle"}}
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
        F = Form()
        F.rig.export(frames(F))
        return
    if a.audit or a.review:
        F = Form()
        acts = frames(F)
        if a.audit:
            import types
            import rig_wukong as RW
            RW.HERO = HERO
            # the side view's tags against the side view standing (its own colours and outline), then the front's
            S = types.SimpleNamespace(D=F.S, rig=F.srig)
            RW.audit(S, {"idle": [(F.side_pose(), 100)], **{t: acts[t] for t in SIDE_TAGS}}, a.audit)
            RW.audit(F, {t: v for t, v in acts.items() if t not in SIDE_TAGS}, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    F = Form()
    tinted(F.D).save(os.path.join(a.parts, f"{HERO}_parts_front.png"))
    tinted(F.S).save(os.path.join(a.parts, f"{HERO}_parts_side.png"))
    print({k: int(v.sum()) for k, v in F.D.parts.items()}, {k: int(v.sum()) for k, v in F.S.parts.items()})
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()

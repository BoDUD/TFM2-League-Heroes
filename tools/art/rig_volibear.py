#!/usr/bin/env python3
"""league_volibear's action frames: the approved front design's own squares, the arm poses and the walk Codex drew on
its grid (the user, 2026-10-19: the rigged arms 「左手严重变形」 ... 「看了还是奇怪 你改不好就让codex帮忙」, the walk
「没交叉换步 腿看起来都没变的」). League's clips are the reference (tools/lol/anim_graph.py Volibear + pose_ref.py).

    python tools/art/rig_volibear.py --parts DIR       # the design with its parts tinted + pose tries (12x)
    python tools/art/rig_volibear.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_volibear.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_volibear.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design (tools/art/design_volibear_model.py; the user's picks: B, 44 game px, PPU 1.2): hd/modelB.png (51 x 54,
Codex's step-1 B-2 read back on its 21 px grid; ear top row 0, soles row 53). Its parts: the near arm (image left: its
own fur ringed by its outline), the far arm (image right), the near and far lower legs (from row LEG_TOP); the rest is
the body. Poses without new arms (idle, hit, death) move these parts by whole squares only.
The arm poses (tools/art/design_volibear_poses.py: Codex's "same bear, only the arms" pictures read back on the design's
grid, the design's own head and legs laid back over them): up2 (both arms raised), up1 (the near arm raised), rake (the
near arm swung forward and down across the belly), maul (both arms thrust forward). Each is the design's legs plus one
upper layer (head, torso and the new arms) that crouches and moves like the body (cpose).
The walk (tools/art/design_volibear_run.py: Codex's skin swap over oppi's Alistar run, crossing steps, the design's head
on every frame): nine frames, each placed by its head so the head stays where the idle's is, the soles on the ground.
The first rigged arms (quarter turns, moves, mirror images) are kept in pose() only for the pose pack's "not like
this" picture (tools/art/pack_volibear_poses.py).
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
import volibear_storm as VS  # noqa: E402
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet, vflip  # noqa: E402

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


# ------------------------------------------------------------------------------------------------- the design
STAND = 25                     # the column between the feet: the standing point
NEAR_SHOULDER = (13.0, 15.0)   # the near arm turned about this corner (the rejected posings only)
FAR_SHOULDER = (40.0, 15.0)
ARM_TOP = 16                   # a turned arm left its shoulder cap (the rows above) out
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
    D.part("far_arm", ringed(d, far & ~dark(d)) & (xx >= 38))
    legs = op & (yy >= LEG_TOP) & ~D.parts["near_arm"] & ~D.parts["far_arm"]
    D.part("near_leg", legs & (xx <= LEG_X))
    D.part("far_leg", legs & (xx > LEG_X))
    D.part("body", D.rest())
    return D


TINT = {"near_arm": (60, 120, 255), "far_arm": (0, 220, 120), "near_leg": (255, 220, 0), "far_leg": (0, 220, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


PAD = (50, 60, 40, 20)          # canvas padding round the design: left, right, top, bottom
POSES = ("up2", "up1", "rake", "maul")
RUN_N = 9


def placed(img, origin, H, W):
    """A picture whose design (0, 0) is at `origin` inside it, as a padded design-sized layer."""
    lay = np.zeros((H + 2 * P, W + 2 * P, 4), np.uint8)
    ox, oy = origin
    y0, x0 = P - oy, P - ox
    lay[y0:y0 + img.shape[0], x0:x0 + img.shape[1]] = img
    return lay


class Form:
    """The design's layers, the Codex arm poses and the walk frames -> canvases of one rig."""

    def __init__(self):
        self.D = front()
        D = self.D
        self.rig = R.Rig(D, pad=PAD)
        # slits closed after the rig's own finish too (its outline pass can close a gap between two thrust arms)
        base_finish = self.rig.finish
        self.rig.finish = lambda can: self.dark_slits(base_finish(can))
        self.L = {k: pad(D.layer(k)) for k in D.order}
        for k in ("near_arm", "far_arm"):
            cap = self.L[k].copy()
            cap[:P + ARM_TOP] = 0
            self.L[k + "_turned"] = cap
            self.L[k + "_up"] = vflip(cap, ARM_TOP - 1)
        legs = np.zeros(self.L["body"].shape[:2], bool)
        legs[P:P + D.H, P:P + D.W] = D.parts["near_leg"] | D.parts["far_leg"]
        self.U = {}
        for k in POSES:
            with open(lp(os.path.join(SRC, f"pose_{k}.json")), encoding="utf-8") as f:
                meta = json.load(f)
            lay = placed(load(f"pose_{k}.png"), meta["origin"], D.H, D.W)
            lay[legs] = 0                                   # the legs are the design's own layers
            self.U[k] = lay
        with open(lp(os.path.join(SRC, "run.json")), encoding="utf-8") as f:
            run = json.load(f)
        self.RUN = []
        for n, m in enumerate(run):
            img = load(f"run_{n}.png")
            oy = img.shape[0] - D.ground                     # the soles on the design's ground row
            self.RUN.append(placed(img, (m["origin"][0], oy), D.H, D.W))
        # Q (design_volibear_q.py): the charge on all fours and the pounce, placed by the head, soles on the ground
        # (the pounce's leap frames lifted as Codex drew them)
        with open(lp(os.path.join(SRC, "q.json")), encoding="utf-8") as f:
            q = json.load(f)
        self.Q = {}
        for key, metas in q.items():
            self.Q[key] = []
            for n, m in enumerate(metas):
                img = load(f"q_{key}_{n}.png")
                oy = img.shape[0] - D.ground + m["lift"]
                self.Q[key].append(placed(img, (m["origin"][0], oy), D.H, D.W))
        self.ref_holes = None

    def pose(self, crouch=0, whole=(0, 0), near=(0, 0), near_rot=0, far=(0, 0), far_rot=0, legs=None,
             near_back=False, far_front=False, near_up=False, far_up=False, fill=True):
        """The design's own parts: crouch: rows the body (with both arms) sets down onto the lower legs; whole: the
        whole figure; near / far: an arm moved (dx, dy); legs: ((near dx, dy), (far dx, dy)). *_rot (quarter turns),
        *_up (mirrored top to bottom), near_back / far_front: the rejected arm posings, for the pose pack's picture."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        far_k = "far_arm_up" if far_up else "far_arm_turned" if far_rot % 4 else "far_arm"
        near_k = "near_arm_up" if near_up else "near_arm_turned" if near_rot % 4 else "near_arm"
        far_l = (L[far_k], dict(dx=ux + far[0], dy=uy + far[1], rot=far_rot, about=FAR_SHOULDER))
        near_l = (L[near_k], dict(dx=ux + near[0], dy=uy + near[1], rot=near_rot, about=NEAR_SHOULDER))
        layers = [*([] if far_front else [far_l]), *([near_l] if near_back else []),
                  (L["far_leg"], dict(dx=wx + flx, dy=wy + fly)), (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly)),
                  (L["body"], dict(dx=ux, dy=uy)), *([far_l] if far_front else []),
                  *([] if near_back else [near_l])]
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    def cpose(self, key, crouch=0, whole=(0, 0), legs=None, fill=True):
        """A Codex arm pose: the design's lower legs and the pose's upper layer (head, torso, arms) set down crouch
        rows onto them; whole: the whole figure; legs ((near dx, dy), (far dx, dy))."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        layers = [(L["far_leg"], dict(dx=wx + flx, dy=wy + fly)), (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly)),
                  (self.U[key], dict(dx=wx, dy=wy + crouch))]
        can = R.compose(self.rig, layers)
        return self.dark_slits(self.close_holes(can)) if fill else can

    def q(self, key, n, dx=0):
        return self.dark_slits(R.compose(self.rig, [(self.Q[key][n], dict(dx=dx))]))

    def run(self, n, dy=0):
        """A walk frame; the slits Codex left between a thigh and an arm or the crossing legs (enclosed, not in the
        idle) closed with the outline's dark (memory gap-check)."""
        return self.dark_slits(R.compose(self.rig, [(self.RUN[n], dict(dy=dy))]))

    def dark_slits(self, can):
        if self.ref_holes is None:
            self.close_holes(self.pose(fill=False))
        op = can[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op & ~self.ref_holes
        out = can.copy()
        out[holes] = (*self.D.outline, 255)
        return out

    MOST = 16                                          # (league_wukong's 10: the slit between the two thrust arms is 10-12)
    close_holes = _Form.close_holes


def tries(F):
    p = F.pose
    return [p(), p(crouch=2), p(whole=(2, 0)), F.run(0), F.cpose("up2"), F.cpose("up1"), F.cpose("rake"),
            F.cpose("maul")]


# ------------------------------------------------------------------------------------------------- the actions
# (skill: the slam lands on frame 4, 280 ms in - the kit's q_rel 17)
MS = {"idle": [150] * 8, "run": [110] * 9, "skill_run": [80] * 8, "attack": [90, 110, 100, 120, 80],
      "attack_w": [80, 90, 100, 120, 80], "skill": [80, 90, 110, 100, 170], "skill2": [100, 120, 167, 120],
      "ult": [100, 150, 200, 550], "ult_land": [70, 130, 200], "hit": [100, 100],
      "dead": [100, 110, 120, 150, 60, 60, 100, 500]}
ORDER = ["idle", "run", "skill_run", "attack", "attack_w", "skill", "skill2", "ult", "ult_land", "hit", "dead"]


def frames_all(F):
    p, c = F.pose, F.cpose
    rig = F.rig
    out = {}
    out["idle"] = [p(crouch=k) for k in (0, 0, 0, 1, 1, 1, 1, 0)]
    out["run"] = [F.run(n) for n in range(RUN_N)]
    # Q's charge (League's Volibear_spell1_run): Codex's run on all fours (the user: 「Q技能的释放技能姿势和英雄联盟不一样？」)
    out["skill_run"] = [F.q("charge", n) for n in range(len(F.Q["charge"]))]
    # auto attack (League's Volibear_Attack_1: one arm raised high, then raked down forward, the body thrown after it):
    # raised, raised with the body drawn back, the rake (frame 3), followed through, standing
    out["attack"] = [c("up1", crouch=1), c("up1", whole=(-1, 0)), c("rake", crouch=1, whole=(2, 0)),
                     c("rake", crouch=1, whole=(3, 0)), p()]
    # W Frenzied Maul (Volibear_Spell2_Slash: a lunge with both claws forward and the bite)
    out["attack_w"] = [p(crouch=1, whole=(-1, 0)), c("maul", crouch=2, whole=(2, 0)), c("maul", crouch=2, whole=(4, 0)),
                       c("rake", crouch=1, whole=(3, 0)), p()]
    # Q Thundering Smash (Volibear_spell1_attack_stationary): Codex's pounce - low on all fours, rearing up, the claws
    # high over his head, the dive forward slamming the claws down (frame 4), landed low on all fours
    out["skill"] = [F.q("pounce", n) for n in range(len(F.Q["pounce"]))]
    # E Sky Splitter (volibear_spell3: one arm raised to the sky, held, down)
    out["skill2"] = [p(crouch=1), c("up1"), c("up1", crouch=1), p(crouch=1)]
    # R Stormbringer (Volibear_Spell4_Ground_Pound): crouched, the spring, in the air with both arms up (held while he
    # flies), then ult_land: the slam with both claws down in front, the rebound, up
    air = c("up2", whole=(1, -8), legs=((0, -2), (0, -2)))
    out["ult"] = [p(crouch=2), c("up2", whole=(0, -4), legs=((0, -1), (0, -1))), air, air.copy()]
    out["ult_land"] = [c("maul", crouch=2, whole=(1, 0)), c("rake", crouch=1, whole=(1, 0)), p(crouch=1)]
    hit = [p(whole=(-2, 0)), p(whole=(-1, 0))]
    out["hit"] = [R.flash(hit[0]), hit[1]]
    # the death (volibear_death): staggers back, sinks, falls on his back, bounces once on the ground
    body = p(crouch=2, whole=(-3, 0))
    lie = lambda sink: R.lie(rig, body, k=1, dx=-4, sink=sink)
    out["dead"] = [p(whole=(-1, 0)), p(crouch=1, whole=(-2, 0)), p(crouch=2, whole=(-3, 0)), lie(-3), lie(0),
                   lie(-1), lie(0), lie(0)]
    # R's storm form (tools/art/volibear_storm.py, 2026-10-30: 「沃利贝尔开大是不是得搞个变色啊」 -> 「2 雷电蓝+描边」): every
    # action he plays in it again in the storm's colours, r_<tag> (the add-on plays them while the form lasts). Recoloured
    # once finished: the finish closes the outline next to light squares only (strips.complete_outline), and his three
    # mid purples turn dark navy, so a twin finished in its own colours lost outline squares his frame has; finished
    # again on export, it stays square for square his. The hit's first frame recoloured before its flash, so it flashes
    # as white as his own (all light then: it finishes as his does)
    for tag in VS.TAGS:
        out[VS.PREFIX + tag] = [VS.recolour(rig.finish(c)) for c in out[tag]]
    out[VS.PREFIX + "hit"] = [R.flash(VS.recolour(hit[0])), VS.recolour(rig.finish(hit[1]))]
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order (the storm form's twins last, each at its action's times)."""
    a = frames_all(F)
    out = {}
    for tag in ORDER + [VS.PREFIX + t for t in VS.TAGS]:
        cans, ms = a[tag], MS[tag.removeprefix(VS.PREFIX)]
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
        VS.twin_ones()
        return
    if a.audit or a.review:
        F = Form()
        acts = frames(F)
        if a.audit:
            import rig_wukong as RW
            RW.HERO = HERO
            RW.audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    F = Form()
    tinted(F.D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in F.D.parts.items()})
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()

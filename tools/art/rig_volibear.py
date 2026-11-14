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
import inbetween as IB  # noqa: E402
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


# ------------------------------------------------------------------------------------------------- the thigh ice
# League's skin draws two plates of ice on his thighs (its submesh ice_legs), but pose_ref's old --hide-submeshes guess
# left them out of every render he was drawn from (tools/lol/hide_audit.py; the user, 2026-11-09: 「沃利贝尔大腿上那两块
# 冰补啊」). They are stamped here on every picture the rig uses, over his violet fur only (the outline, the white and
# blue fur, the braids and the claws stay): each plate on the upper outer side of its thigh, as in League's idle - the
# near one on the near thigh, the far one on the far thigh where it shows (on all fours only the near haunch shows).
# ICE: the stamps' top-left squares on each picture, fitted so each stamp lies whole on that leg's fur.
ICE_NEAR = (".WL.",
            "WLMS",
            "LMCS",
            "MCMS",
            "MMSD",
            ".SD.")
ICE_FAR = (".LM",
           "LMS",
           "MCS",
           "MSD",
           ".D.")
ICE_COL = {"W": (253, 253, 253), "L": (193, 220, 252), "M": (150, 176, 236), "S": (126, 135, 191),
           "D": (94, 82, 128), "C": (60, 41, 66)}           # the design's own ice-blue fur shades and violet darks
ICE = {"modelB": ((15, 36), (32, 36)), "pose_up2": ((17, 50), (33, 50)), "pose_up1": ((16, 53), (33, 53)),
       "pose_rake": ((16, 37), (33, 37)), "pose_maul": ((16, 37), (33, 37)), "run_0": ((15, 28), (27, 31)),
       "run_1": ((15, 28), (26, 30)), "run_2": ((15, 26), (26, 30)), "run_3": ((14, 27), (26, 32)),
       "run_4": ((16, 27), (27, 28)), "run_5": ((19, 29), (29, 28)), "run_6": ((21, 27), (31, 29)),
       "run_7": ((17, 28), (29, 31)), "run_8": ((18, 27), (29, 27)), "q_charge_0": ((18, 12), None),
       "q_charge_1": ((18, 12), None), "q_charge_2": ((18, 12), None), "q_charge_3": ((19, 10), None),
       "q_charge_4": ((18, 11), None), "q_charge_5": ((16, 11), None), "q_charge_6": ((18, 10), None),
       "q_charge_7": ((18, 12), None), "q_pounce_0": ((20, 30), None), "q_pounce_1": ((11, 45), (27, 47)),
       "q_pounce_2": ((11, 49), (27, 49)), "q_pounce_3": ((15, 10), None), "q_pounce_4": ((6, 17), None)}


def violet(d):
    """His violet fur (legs, haunches, forearms) - not the outline, the white or blue fur, the braids or the claws."""
    r, g, b = (d[..., i].astype(int) for i in range(3))
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return (d[..., 3] > 0) & (r > 30) & (lum > 35) & (lum < 165) & (b >= g)


def iced(img, name):
    """Picture `name` (assets/source/volibear/hd/<name>.png, as loaded) with the thigh ice stamped on its fur."""
    out = img.copy()
    fur = violet(img)
    for rows, anchor in zip((ICE_NEAR, ICE_FAR), ICE[name]):
        if anchor is None:
            continue
        ax, ay = anchor
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                y, x = ay + j, ax + i
                if ch != "." and 0 <= y < out.shape[0] and 0 <= x < out.shape[1] and fur[y, x]:
                    out[y, x, :3] = ICE_COL[ch]
    return out


# ------------------------------------------------------------------------------------------------- the design
STAND = 25                     # the column between the feet: the standing point
NEAR_SHOULDER = (13.0, 15.0)   # the near arm turned about this corner (the rejected posings only)
FAR_SHOULDER = (40.0, 15.0)
ARM_TOP = 16                   # a turned arm left its shoulder cap (the rows above) out
LEG_TOP = 42                   # the legs part from this row down: near columns <= LEG_X, far > LEG_X
LEG_X = 25


def front(ice=False):
    """The design cut into its parts; ice: with the thigh ice (the rig's frames; the design readers paste the design's
    head and lower legs, which never carry it)."""
    d = load("modelB.png")
    if ice:
        d = iced(d, "modelB")
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


PAD = (50, 60, 80, 20)          # canvas padding round the design: left, right, top (R's leap), bottom
POSES = ("up2", "up1", "rake", "maul")
RUN_N = 9
# The R's hang in three frames (2026-11-14, the user: 「有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): held at
# the top while he flies, the pounce's raised claws were one drawing for 780 ms; now the claws come down a little as he
# hangs - each forearm (HANG_ARMS in q_pounce_2's own squares: the rows over his shoulders, the head left out) slid HANG
# rows down along itself, behind his shoulders (inbetween.vary: everything else checked unchanged), drawn in toward the
# crash. The leap's drawings, heights and times stay (100 / 50 / 70, the hang from 220 ms, 780 in all: 260 x 3); the
# arms only get shorter, nothing of him grows (the user: 「开大模型变的实在太大了」).
HANG_ARMS = {"near": [(0, 0, 19, 10), (0, 11, 15, 13)], "far": [(24, 0, 43, 10), (29, 11, 43, 13)]}
HANG = (2, 4)
VPAD = 8


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
        self.D = front(ice=True)
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
            lay = placed(iced(load(f"pose_{k}.png"), f"pose_{k}"), meta["origin"], D.H, D.W)
            lay[legs] = 0                                   # the legs are the design's own layers
            self.U[k] = lay
        with open(lp(os.path.join(SRC, "run.json")), encoding="utf-8") as f:
            run = json.load(f)
        self.RUN = []
        for n, m in enumerate(run):
            img = iced(load(f"run_{n}.png"), f"run_{n}")
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
                img = iced(load(f"q_{key}_{n}.png"), f"q_{key}_{n}")
                oy = img.shape[0] - D.ground + m["lift"]
                self.Q[key].append(placed(img, (m["origin"][0], oy), D.H, D.W))
        # the R's hang: the pounce's raised claws with both forearms slid down (HANG_ARMS), placed as the pounce is
        img, m = iced(load("q_pounce_2.png"), "q_pounce_2"), q["pounce"][2]
        oy = img.shape[0] - D.ground + m["lift"]
        self.HANG = [placed(IB.vary(img, HANG_ARMS, tuple(int(c) for c in D.outline),
                                    moves=[("near", (0, k), "under"), ("far", (0, k), "under")], pad=VPAD,
                                    name=f"q_pounce_2 forearms {k}"), (m["origin"][0] + VPAD, oy + VPAD), D.H, D.W)
                     for k in HANG]
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

    def q(self, key, n, dx=0, dy=0):
        return self.dark_slits(R.compose(self.rig, [(self.Q[key][n], dict(dx=dx, dy=dy))]))

    def hang(self, n, dy=0):
        return self.dark_slits(R.compose(self.rig, [(self.HANG[n], dict(dy=dy))]))

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
      "ult": [100, 50, 70, 260, 260, 260], "ult_land": [35, 35, 160, 170], "hit": [100, 100],
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
    # R Stormbringer (Volibear_Spell4_Ground_Pound: crouched on all fours, a spring far up - out of League's frame -,
    # held up there with the claws high, a crash straight down and the pound on all fours, 0.9 s): the pounce's own
    # poses lifted (the user, 2026-11-02: 「开大的时候没有像LOL那样跳进去的动作」「我们明显不对」 - the R stood up with
    # both arms raised 8 squares off the ground and clawed forward on landing). ult: low on all fours, rearing up,
    # rising, held at the top (about his height) while he flies; ult_land (on arrival, the kit's r_rel 4 ticks to the
    # slam): the dive down from the height in two steps, the pound on all fours (frame 3, 70 ms in), up; the hang's
    # claws drawn in a little (HANG)
    out["ult"] = [F.q("pounce", 0), F.q("pounce", 1, dy=-10), F.q("pounce", 2, dy=-32), F.q("pounce", 2, dy=-46),
                  F.hang(0, dy=-46), F.hang(1, dy=-46)]
    out["ult_land"] = [F.q("pounce", 3, dy=-28), F.q("pounce", 3, dy=-10), F.q("pounce", 4), p(crouch=1)]
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

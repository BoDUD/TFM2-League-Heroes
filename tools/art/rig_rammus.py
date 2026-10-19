#!/usr/bin/env python3
"""league_rammus's action frames posed from the approved designs' own squares (the 2026-10-19 frame-audit way: no
Codex strips, lossless poses compared with League's clips).

    python tools/art/rig_rammus.py --parts DIR       # the side design with its parts tinted + pose tries (12x)
    python tools/art/rig_rammus.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_rammus.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_rammus.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_rammus_model.py, the user's picks 2026-10-19; 36 game px at PPU 1.2, one palette):
idle.png (A-2, 3/4 front, 41 x 42), side.png (S-1, side-on facing right, 39 x 43: every action's base), ball.png
(Powerball's spiked ball, 45 x 44) and curl.png (Defensive Ball Curl, side-on, 41 x 41). Every pose is lossless: parts
cut square by square from a design and only moved by whole squares, quarter turns about half-integer pivots and
mirrors; the ball rolls by quarter turns of the whole ball. The side design is the rig's own (its standing point and
ground); the other three stand on the same point and ground.
Parts of the side design: the near arm (hanging in front of the belly, claws at the bottom; it turns about its
shoulder), the two feet (the bottom rows, split between the claws); the rest is the body (the shell, the head, the
harness, the belly, the far arm).
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
import pixel_down as PD  # noqa: E402
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet  # noqa: E402

HERO = "rammus"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "rammus", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def stand_col(d, rows=3):
    """The middle of the lowest `rows` rows' squares: where the design stands."""
    op = d[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys.max() - rows + 1:ys.max() + 1].any(0))[0]
    return int(round((xs.min() + xs.max() + 1) / 2))


# ------------------------------------------------------------------------------------------------- the side's parts
ARM_BOX = (21, 39, 17, 27)            # rows / cols the near arm lies in (the claws reach row 39)
SHOULDER = (22.5, 23.5)               # (x, y) the arm turns about
FOOT_ROW = 40                         # the feet: rows FOOT_ROW to the soles, split at FOOT_X
FOOT_X = 21


def is_skin(c):
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return g > r + 20 and g >= b - 10


def is_claw(c):
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return r > 200 and g > 190 and b > 110


def design():
    d = load("side.png")
    D = CutDesign(d, px=stand_col(d))
    y0, y1, x0, x1 = ARM_BOX
    arm = np.zeros((D.H, D.W), bool)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = d[y, x]
            if c[3] and (is_skin(c) or (y >= 35 and is_claw(c))):
                arm[y, x] = True
    # the arm's own outline: dark squares beside it inside the box
    box = D.box(y0, y1, x0, x1)
    dark = (d[..., 3] > 0) & (d[..., :3].astype(int).sum(-1) < 70)
    arm |= ndimage.binary_dilation(arm, structure=R.CROSS) & dark & box
    lbl, n = ndimage.label(arm, structure=np.ones((3, 3)))
    if n > 1:
        big = 1 + int(np.argmax(ndimage.sum(arm, lbl, range(1, n + 1))))
        arm = lbl == big
    D.part("arm", arm)
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    feet = D.box(FOOT_ROW, D.H - 1, 0, D.W - 1) & ~D.parts["arm"]
    D.part("far_foot", feet & (xx <= FOOT_X))
    D.part("near_foot", feet & (xx > FOOT_X))
    D.part("body", D.rest())
    return D


TINT = {"arm": (60, 120, 255), "far_foot": (255, 220, 0), "near_foot": (0, 220, 255)}


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
    """The designs' layers; pose() / whole designs -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.other = {n: self.placed(load(f"{n}.png")) for n in ("idle", "ball", "curl")}

    def placed(self, d):
        """Another design in a padded layer of the side design's size, standing on the same point and ground."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand_col(d)
        lay[top:top + d.shape[0], left:left + d.shape[1]] = d
        return lay

    def pose(self, crouch=0, whole=(0, 0), arm=(0, 0), arm_rot=0, feet=None, fill=True):
        """crouch: rows the body (with the arm) sets down onto the feet; whole: the whole figure; arm: the near arm
        moved, arm_rot quarter turns counter-clockwise about SHOULDER (1: pointing forward); feet: ((near dx, dy),
        (far dx, dy))."""
        if crouch < 0:
            raise ValueError("the body never lifts off the feet")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nx, ny), (fx, fy) = feet or ((0, 0), (0, 0))
        L = self.L
        layers = [(L["far_foot"], dict(dx=wx + fx, dy=wy + fy)), (L["near_foot"], dict(dx=wx + nx, dy=wy + ny)),
                  (L["body"], dict(dx=ux, dy=uy)),
                  (L["arm"], dict(dx=ux + arm[0], dy=uy + arm[1], rot=arm_rot, about=SHOULDER))]
        moved = arm != (0, 0) or arm_rot % 4
        # where the arm hung, the belly and harness it hid are filled from the squares round them (drawn anew: shown
        # to the user before it ships)
        can = R.compose(self.rig, layers, fill=[("arm", (ux, uy))] if moved and fill else ())
        if moved and fill:
            can = self.fill_vacated(can, ux, uy)
        return self.close_holes(can) if fill else can

    def fill_vacated(self, can, ux, uy):
        """Clear squares left inside the figure where the arm hung (ringed by outline, so fill_under cannot reach
        them): the colour of the nearest light square."""
        rig = self.rig
        allow = np.zeros(can.shape[:2], bool)
        allow[rig.oy:rig.oy + self.D.H, rig.ox:rig.ox + self.D.W] = self.D.parts["arm"]
        allow = np.roll(np.roll(allow, uy, 0), ux, 1)
        op = can[..., 3] > 0
        shut = ndimage.binary_closing(np.pad(op, 3), structure=np.ones((3, 3)), iterations=2)[3:-3, 3:-3]
        left = allow & ndimage.binary_fill_holes(shut | op) & ~op
        if not left.any():
            return can
        out = can.copy()
        rgb = can[..., :3].astype(int)
        # the belly's tan and the harness's red, not the outline nor the grey studs (they would smear)
        src = op & (rgb.sum(-1) >= 70) & ((rgb.max(-1) - rgb.min(-1)) > 50)
        _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
        out[left] = out[iy[left], ix[left]]
        return out

    def whole(self, name, dx=0, dy=0, flash=False):
        can = R.compose(self.rig, [(self.other[name], dict(dx=dx, dy=dy))])
        return R.flash(can) if flash else can

    def ball(self, k=0, dx=0, up=0, flash=False):
        """The ball turned k quarter turns counter-clockwise (k = 3: a quarter rolled to the right), on the ground
        (up rows above it), centred dx columns from the standing point."""
        can = self.whole("ball")
        if k % 4:
            can = R.lie(self.rig, can, k % 4, dx=0, sink=0)
            can = shift(can, self.ball_dx(can), 0)
        can = shift(can, dx, -up)
        return R.flash(can) if flash else can

    def ball_dx(self, can):
        """Columns that bring a turned ball's middle back onto the standing ball's middle."""
        if not hasattr(self, "_bx"):
            b = self.whole("ball")
            xs = np.nonzero(b[..., 3].any(0))[0]
            self._bx = (xs.min() + xs.max() + 1) / 2
        xs = np.nonzero(can[..., 3].any(0))[0]
        return int(round(self._bx - (xs.min() + xs.max() + 1) / 2))

    ref_holes = None
    close_holes = _Form.close_holes                   # small enclosed holes the side lacks, filled (league_wukong)
    MOST = _Form.MOST


def shift(can, dx, dy):
    out = np.zeros_like(can)
    H, W = can.shape[:2]
    ys, xs = slice(max(0, dy), H + min(0, dy)), slice(max(0, dx), W + min(0, dx))
    yd, xd = slice(max(0, -dy), H + min(0, -dy)), slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = can[yd, xd]
    return out


def form():
    return Form(design(), rig_pad=(40, 40, 50, 20))


def tries(F):
    p = F.pose
    return [p(), p(arm_rot=1, arm=(0, 8)), p(arm_rot=3, arm=(-1, 4)), p(crouch=2), F.whole("idle"),
            F.whole("curl"), F.ball(), F.ball(3)]


# ------------------------------------------------------------------------------------------------- the actions
FWD = dict(arm_rot=1, arm=(0, 8))     # the near arm swung forward, level under his face (never across it)
BACK = dict(arm_rot=3, arm=(-1, 6))   # the near arm drawn back, level behind the belly

# ms per frame; the kit's ticks (tools/kit/build_rammus.py) come from these
MS = {"idle": [150] * 8, "run": [100] * 8, "attack": [90, 90, 60, 80, 80, 100],
      "skill": [60, 70, 70], "skill_roll": [60] * 4, "skill_hit": [80, 80, 73],
      "skill2": [70, 70, 100, 93], "skill_w": [80, 90, 97],
      "ult": [100, 100, 100, 100, 100, 100], "ult_land": [80, 80, 73],
      "hit": [100, 100], "dead": [100, 110, 120, 150, 60, 60, 100, 500],
      "b_idle": [200, 200], "b_run": [60] * 4, "b_hit": [100, 100],
      "c_idle": [300, 300], "c_run": [100] * 4, "c_hit": [100, 100]}
IDLE_LEG_ROW = 35                     # the idle design's legs: rows from here down stay while the body breathes


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    # idle (League's rammus_idle1: he breathes under the shell): the 3/4 design's body sets down a row onto its legs
    idle = F.other["idle"]
    legs = idle.copy()
    top = idle.copy()
    ys = np.nonzero(idle[..., 3].any(1))[0]
    cut_row = ys.max() + 1 - (F.D.ground - IDLE_LEG_ROW)
    legs[:cut_row] = 0
    top[cut_row:] = 0

    def breathe(c):
        return R.compose(rig, [(legs, dict(dy=0)), (top, dict(dy=c))])
    out["idle"] = [breathe(c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # auto attack (League's rammus_attack1: he rears back, then lunges and swipes): drawn back, the lunge with the arm
    # swung forward (the blow, frame 3), held, back
    out["attack"] = [p(whole=(-2, 0), **BACK), p(crouch=1, whole=(-1, 0), **BACK), p(whole=(3, 0), **FWD),
                     p(whole=(4, 0), **FWD), p(whole=(2, 0)), p()]
    # Q Powerball (League's rammus_spell1_windup: he tucks in and curls up into the ball): crouched, curled, the ball
    out["skill"] = [p(crouch=2), F.whole("curl"), F.ball()]
    # the roll: the ball a quarter turn clockwise each frame (rolling to the right)
    out["skill_roll"] = [F.ball(k) for k in (0, 3, 2, 1)]
    # the hit: the ball bounces back off the target, he uncurls
    out["skill_hit"] = [F.ball(3, dx=-2, up=4), F.whole("curl", dx=-1), p(whole=(-1, 0))]
    # E Frenzying Taunt (League's rammus_spell3: he rears up with his claws raised): crouched, reared up in the curl's
    # raised arms (the taunt, frame 2), higher, down
    out["skill2"] = [p(crouch=2), F.whole("curl", dy=-2), F.whole("curl", dy=-3), p()]
    # W Defensive Ball Curl (League's Rammus_channel): crouched, curled, held
    out["skill_w"] = [p(crouch=2), F.whole("curl"), F.whole("curl")]
    # R Soaring Slam (League's Spell4_Jump: he curls up, leaps high as the ball and comes down on them)
    out["ult"] = [p(crouch=2), F.whole("curl"), F.ball(0, up=6), F.ball(3, up=12), F.ball(2, up=16),
                  F.ball(1, up=10)]
    out["ult_land"] = [F.ball(0), F.whole("curl"), p()]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]

    # the death (League's rammus_death: he topples back onto his shell, belly up): staggering, crouched, falling back
    # (a quarter turn), on his back (half a turn, the spikes in the ground), a bounce, lying
    def lying(k, sink, dx):
        return R.lie(rig, p(fill=True), k, dx=dx, sink=sink)
    out["dead"] = [p(whole=(-1, 0)), p(crouch=2, whole=(-2, 0)), lying(1, 0, -4), lying(2, 8, -5), lying(2, 6, -5),
                   lying(2, 8, -5), lying(2, 8, -5), lying(2, 8, -5)]
    # the add-on's forms (addons/league_rammus): the ball standing / rolling / hit, the curl standing / walking / hit
    out["b_idle"] = [F.ball(), F.ball()]
    out["b_run"] = [F.ball(k) for k in (0, 3, 2, 1)]
    out["b_hit"] = [F.ball(dx=-2, flash=True), F.ball(dx=-1)]
    out["c_idle"] = [F.whole("curl"), F.whole("curl")]
    out["c_run"] = [F.whole("curl"), F.whole("curl", dx=1, dy=-1), F.whole("curl"), F.whole("curl", dx=-1, dy=-1)]
    out["c_hit"] = [F.whole("curl", dx=-2, flash=True), F.whole("curl", dx=-1)]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# League's rammus_run: a waddle under the shell. The design's own feet step whole under the body that stays (each
# planted and sliding back, then lifted and carried forward, the far one half a cycle later), the body set down a row
# on each contact (league_wukong's walk).
from rig_wukong import _steps  # noqa: E402

WALK_STEP = dict(_steps(2, (1, 2, 1)), rise=[0, 0, 1, 0, 0, 0, 1, 0])


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    for (ndx, nup), (fdx, fup), bob, up_ in zip(st["near"], st["far"], st["bob"], st["rise"]):
        out.append(F.pose(whole=(0, bob - up_), feet=((ndx, -nup), (fdx, -fup))))
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
            import rig_wukong as RW
            RW.HERO = HERO
            RW.audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in D.parts.items()}, "stand", D.px, "ground", D.ground)
    F = form()
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""league_poppy's action frames posed from the approved design's own squares (the user, 2026-10-18: 「动作帧参考塔姆那种做法
不用依赖codex 然后做完了你自己review 完美了再喊我review」).

    python tools/art/rig_poppy.py --parts DIR       # the design with its parts tinted + pose tries (12x)
    python tools/art/rig_poppy.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_poppy.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_poppy.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design: Codex's step-1 take B-2 read back on its own 20 px grid (design_poppy_model.py) and brought to 47 rows
from the pigtail top to the soles by whole rows / columns (design_poppy_cut.py; the user's pick: B, 36 game px, PPU
1.3), 42 x 55 squares: the pommel's top row 0, the pigtails' top row 8, the soles row 54; the hammer stands upright on
its head by her near foot, her near fist on the haft. Every pose is lossless (memory no-deformation-lossless-poses):
parts cut square by square from the design and only moved by whole squares and quarter turns about half-integer
pivots; nothing is drawn again at another angle.
Parts: the hammer (a rigid prop, laid once straight - see HAFT), the near fist (drawn over the haft), the near forearm,
the near and far lower legs (the copper knee guards and the boots, rows LEG_TOP on: they part there); the rest is the
body (the head and pigtails, the far arm with its fist at her waist, the armour, the hips).
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

HERO = "poppy"
PPU = 1.3
SRC = os.path.join(R.ROOT, "assets", "source", "poppy", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the design's parts
# The hammer as Codex drew it is a little crooked: the pommel's middle on x 6.0, the haft 2 reds wide above the fist
# (columns 5-6) and 1 below it (column 6), the gold flanges and the head centred on x 7.5. Turned level any jog becomes
# a step in the line (league_wukong's staff: 「武器做的也是歪的」), so the hammer is laid once, straight, on the axis
# x = AXIS: the pommel as drawn (rows 0-7), the haft HAFT_ROWS long in the design's own reds - outline, red, red,
# outline, a dark band every third row (its upper run's pattern) - the collar as drawn (rows 39-40) and the flanges
# and head as drawn, moved one column left (centre 6.5).
AXIS = 6.0
POMMEL = (0, 7, 3, 8)                 # rows / cols as drawn
HAFT_ROWS = (8, 38)
COLLAR = (39, 40, 3, 9)
HEAD = (41, 54, 0, 15)                # the flanges' lower rows and the head, moved HEAD_DX
HEAD_DX = -1
RED, DARK = (206, 40, 47), (145, 20, 31)
GRIP = (6.0, 30.5)                    # the fist's middle on the haft (the hammer turns about it)
FIST = [(range(28, 33), (4, 9)), ((33,), (7, 9))]
FOREARM = [((31,), (10, 15)), ((32,), (10, 15)), ((33,), (10, 15)), ((34,), (8, 16)), ((35,), (10, 16)),
           ((36,), (12, 16)), ((37,), (13, 16))]
LEG_TOP = 46                          # the legs part from this row down: near columns <= LEG_X, far > LEG_X
LEG_X = 25
STAND = 25                            # the column between the shoes: the standing point


def spans(table):
    out = {}
    for rows, cols in table:
        for y in rows:
            out[y] = cols
    return out


def design():
    d = load("design.png")
    D = CutDesign(d, px=STAND)
    hammer = D.box(0, 7, 3, 8) | D.box(8, 38, 4, 8) | D.box(39, 40, 3, 9) | D.box(41, 54, 0, 15)
    D.part("hammer", hammer)
    D.part("fist", D.rows(spans(FIST)))
    D.part("forearm", D.rows(spans(FOREARM)))
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    legs = D.box(LEG_TOP, D.H - 1, 14, D.W - 1) & ~D.parts["hammer"]
    D.part("near_leg", legs & (xx <= LEG_X))
    D.part("far_leg", legs & (xx > LEG_X))
    D.part("body", D.rest())
    return D


TINT = {"hammer": (255, 60, 60), "fist": (60, 120, 255), "forearm": (0, 220, 120), "near_leg": (255, 220, 0),
        "far_leg": (0, 220, 255)}


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
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.L["hammer"] = self.hammer_src()
        self._ham = {}

    def hammer_src(self):
        """The straight hammer in a padded layer (the head's left column may reach x -1)."""
        d = self.D.d
        lay = np.zeros((d.shape[0] + 2 * P, d.shape[1] + 2 * P, 4), np.uint8)
        r0, r1, c0, c1 = POMMEL
        lay[P + r0:P + r1 + 1, P + c0:P + c1 + 1] = d[r0:r1 + 1, c0:c1 + 1] * (self.D.parts["hammer"][r0:r1 + 1, c0:c1 + 1, None] > 0)
        o = tuple(self.D.outline)
        for y in range(HAFT_ROWS[0], HAFT_ROWS[1] + 1):
            dark = (y - 11) % 3 == 0
            for i, c in enumerate([o, DARK if dark else RED, DARK if dark else RED, o]):
                lay[P + y, P + int(AXIS) - 2 + i] = (*c, 255)
        r0, r1, c0, c1 = COLLAR
        m = self.D.parts["hammer"][r0:r1 + 1, c0:c1 + 1, None] > 0
        lay[P + r0:P + r1 + 1, P + c0:P + c1 + 1] = np.where(m, d[r0:r1 + 1, c0:c1 + 1], 0)
        r0, r1, c0, c1 = HEAD
        m = self.D.parts["hammer"][r0:r1 + 1, c0:c1 + 1, None] > 0
        blk = np.where(m, d[r0:r1 + 1, c0:c1 + 1], 0)
        dst = lay[P + r0:P + r1 + 1, P + c0 + HEAD_DX:P + c1 + 1 + HEAD_DX]
        dst[blk[..., 3] > 0] = blk[blk[..., 3] > 0]
        return lay

    def hammer(self, rot, grip=GRIP[1]):
        """The hammer with the haft's row `grip` (design rows, standing) in the fist's middle, turned rot quarter
        turns counter-clockwise about GRIP (1: the head points forward, 2: up, 3: back)."""
        key = (rot % 4, grip)
        if key not in self._ham:
            src = np.roll(self.L["hammer"], int(round(GRIP[1] - grip)), axis=0)
            lay = np.zeros_like(src)
            R.put(lay, src, rot=rot, about=(GRIP[0] + P, GRIP[1] + P))
            self._ham[key] = lay
        return self._ham[key]

    def pose(self, crouch=0, whole=(0, 0), fist=(0, 0), arm=(0, 0), rot=0, grip=GRIP[1], ham=None, legs=None,
             leg_layers=None, no_hammer=False, hammer_over=False, fill=True):
        """crouch: rows the body (with the arm and fist) sets down onto the lower legs; whole: the whole figure; fist /
        arm: the near fist and forearm moved (the fist carries the hammer); rot / grip: the hammer turned about the
        fist / slid in it; ham: the hammer moved apart from the fist (it stands on the ground while she crouches);
        legs: ((near dx, dy), (far dx, dy))."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        legs_l = leg_layers if leg_layers is not None else [(L["far_leg"], dict(dx=wx + flx, dy=wy + fly)),
                                                             (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly))]
        hx, hy = (ux + fist[0], uy + fist[1]) if ham is None else (wx + ham[0], wy + ham[1])
        ham_l = [] if no_hammer else [(self.hammer(rot, grip), dict(dx=hx, dy=hy))]
        layers = [*([] if hammer_over else ham_l), *legs_l, (L["body"], dict(dx=ux, dy=uy)),
                  (L["forearm"], dict(dx=ux + arm[0], dy=uy + arm[1])), *(ham_l if hammer_over else []),
                  (L["fist"], dict(dx=ux + fist[0], dy=uy + fist[1]))]
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    ref_holes = None
    close_holes = _Form.close_holes                   # small enclosed holes the idle lacks, filled (league_wukong)
    MOST = _Form.MOST


def form():
    return Form(design(), rig_pad=(60, 60, 50, 20))


def tries(F):
    p = F.pose
    return [p(), p(rot=3), p(rot=2), p(rot=1, grip=9), p(rot=1, grip=9, hammer_over=True),
            p(crouch=2, ham=(0, 0)), p(rot=3, fist=(0, 6), arm=(0, 4)),
            p(rot=1, grip=9, fist=(2, 6), arm=(2, 4), hammer_over=True)]


# ------------------------------------------------------------------------------------------------- the actions
# The hammer only turns about the fist (rot) and slides in it (grip): upright on its head standing, back (rot 3: the
# head behind her, the haft level through the fist), overhead (rot 2) and forward (rot 1, held near the pommel - grip
# SWING - with the fist and forearm lowered (LOW) so the haft crosses her waist, not her face, the head in front of her).
SWING = 9                                             # the haft row held for a forward swing (under the pommel)
LOW = dict(fist=(2, 6), arm=(2, 4))                   # the fist and forearm lowered for a forward swing
BACK = dict(rot=3, fist=(0, 4), arm=(0, 3))           # the hammer drawn back level at the hip


def fwd(dx=0, dy=0, ady=None, **kw):
    """The forward swing: the head in front of her; the fist lowered dy more, the forearm ady (default dy)."""
    ady = dy if ady is None else ady
    return dict(rot=1, grip=SWING, fist=(LOW["fist"][0] + dx, LOW["fist"][1] + dy),
                arm=(LOW["arm"][0] + dx, LOW["arm"][1] + ady), hammer_over=True, **kw)


RAISE = 20.5                                          # the haft row held overhead: the head high above her


def up(dy=0):
    """The hammer raised: the head high above her (held low on the haft, RAISE), the fist and forearm raised dy rows
    (dy < 0). Held at the fist's own row the pommel hung down to the ground like a staff held upside down."""
    return dict(rot=2, grip=RAISE, fist=(0, dy), arm=(0, dy))


# ms per frame; the kit's ticks (tools/kit/build_poppy.py) come from these: the attack's blow at 200 ms (tick 12,
# frame 3), Q's slam at 200 ms (q_rel 12), R's swing 133 ms after the charge (r_rel 8), the tap's at 133 (r_tap_rel 8)
MS = {"idle": [150] * 8, "run": [100] * 8, "attack": [90, 110, 120, 60, 53], "skill": [100, 100, 140, 127],
      "skill2": [90, 90, 87], "ult_charge": [167] * 4, "ult": [70, 63, 120, 114], "ult_tap": [133, 120, 80],
      "hit": [100, 100], "dead": [100, 110, 120, 150, 60, 60, 100, 500]}


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    stand = dict(ham=(0, 0))                          # the hammer stays on the ground, the fist slides on the haft
    # idle: the body sets down a row onto the lower legs and rises, the hammer standing where it is
    out["idle"] = [p(crouch=c, **stand) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # auto attack (League's poppy_attack1/2: a big swing of the hammer): drawn back level at the hip, swung up over
    # her head, down in front of her (the blow, frame 3), held, back upright
    out["attack"] = [p(whole=(-1, 0), **BACK), p(**up(-2)), p(crouch=1, whole=(2, 0), **fwd()),
                     p(crouch=1, whole=(2, 0), **fwd()), p()]
    # Q Hammer Shock (League's poppy_spell1: the hammer swung high and slammed into the ground in front of her):
    # raised, higher, the slam - crouched low, the head in front at her knees - and up
    out["skill"] = [p(crouch=1, **up(-1)), p(**up(-3)), p(crouch=3, whole=(2, 0), **fwd(dy=7, ady=3)),
                    p(crouch=1, whole=(1, 0), **fwd(dy=3, ady=1))]
    # E Heroic Charge (League's poppy_spell3: she runs at the target, the hammer level behind her): crouched with the
    # hammer back, the lunge, landing low
    out["skill2"] = [p(crouch=2, **BACK), p(whole=(3, -1), legs=((1, -1), (1, -1)), **BACK),
                     p(crouch=2, whole=(4, 0), **BACK)]
    # R Keeper's Verdict: the charge (League's Poppy_Spell4_Windup: the hammer held up over her head while it gathers),
    # the raised hammer of the attack / Q, shaking a row and the fist a row (2026-10-19 frame audit: it was drawn back
    # at the hip, four near-identical frames - League's holds it high)
    out["ult_charge"] = [p(crouch=c, **up(dy)) for c, dy in ((1, -2), (2, -3), (1, -3), (2, -2))]
    # the release (Poppy_Spell4_Charged: swung over and forward with all her weight): overhead, forward, held, back
    out["ult"] = [p(crouch=1, **up(-2)), p(crouch=2, whole=(3, 0), **fwd()), p(crouch=2, whole=(3, 0), **fwd()),
                  p(crouch=1, whole=(1, 0))]
    # the quick tap (Poppy_Spell4_Instant): raised, the slam low in front (Q's), up
    out["ult_tap"] = [p(crouch=1, **up(-2)), p(crouch=3, whole=(2, 0), **fwd(dy=7, ady=3)), p(crouch=1)]
    out["hit"] = [R.flash(p(whole=(-2, 0), **stand)), p(whole=(-1, 0), **stand)]

    # the death (League's poppy_death: the hammer drops and she falls back): staggering, low, the hammer falling away
    # in front of her (level on the ground, its head forward), she sinks down to sit behind it
    def ground(can):
        out_ = can.copy()
        out_[rig.GY:] = 0
        return out_
    lying = F.hammer(1)
    low_row = int(np.nonzero(lying[..., 3].any(1))[0].max()) - P

    def dropped(can, dx):
        """The hammer lying level (head forward) on the ground dx columns from standing, under the frame."""
        out_ = can.copy()
        lay = R.compose(rig, [(lying, dict(dx=dx, dy=F.D.ground - 1 - low_row))])
        m = (lay[..., 3] > 0) & (out_[..., 3] == 0)
        out_[m] = lay[m]
        return out_
    # she drops onto the ground and sits (league_wukong's death: a figure turned to lie read upside down, its legs in
    # the air): the body set down 8 rows over the lower legs, which spread out, everything under the ground clipped
    sit = dropped(ground(p(crouch=8, whole=(-3, 0), legs=((-3, 0), (3, 0)), no_hammer=True)), 25)
    # (8 frames since the 2026-10-19 frame audit: she lands sitting, the body bounces a row, sits)
    bounce = dropped(ground(p(crouch=7, whole=(-3, 0), legs=((-3, 0), (3, 0)), no_hammer=True)), 25)
    out["dead"] = [p(whole=(-1, 0), **stand), p(crouch=2, whole=(-2, 0), **BACK),
                   dropped(ground(p(crouch=4, whole=(-3, 0), no_hammer=True)), 25),
                   dropped(ground(p(crouch=6, whole=(-3, 0), legs=((-2, 0), (2, 0)), no_hammer=True)), 25),
                   sit, bounce, sit.copy(), sit.copy()]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# The design's own lower legs (knee guards and boots) moved whole under the hips that stay on the body (memory
# codex-legs-deform): each steps on its own side, planted and sliding back, then lifted and carried forward, the far one
# half a cycle later; the body set down a row on each contact (league_wukong's walk); the hammer carried two rows off
# the ground in the fist (the fist and forearm raised with it, never the fist alone).
from rig_wukong import _steps  # noqa: E402

WALK_STEP = dict(_steps(3, (1, 2, 1)), rise=[0, 0, 1, 0, 0, 0, 1, 0])
CARRY = dict(fist=(0, -2), arm=(0, -2))


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    L = F.L
    for (ndx, nup), (fdx, fup), bob, up_ in zip(st["near"], st["far"], st["bob"], st["rise"]):
        legs = [(L["far_leg"], dict(dx=fdx, dy=-fup - up_)), (L["near_leg"], dict(dx=ndx, dy=-nup - up_))]
        out.append(F.pose(whole=(0, bob - up_), leg_layers=legs, **CARRY))
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
    print({k: int(v.sum()) for k, v in D.parts.items()})
    F = form()
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""league_zoe's action frames posed from the approved designs' own squares (the 2026-10-19 frame-audit way: no Codex
strips, lossless poses compared with League's clips).

    python tools/art/rig_zoe.py --parts DIR       # the side design with its parts tinted + pose tries (12x)
    python tools/art/rig_zoe.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_zoe.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_zoe.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_zoe_model.py, the user's picks 2026-10-19; 35 game px at PPU 1.5, one palette): idle.png
(A-1, 3/4 front, arms a little out, 59 x 53) and side.png (S-1, side-on facing right with the same 3/4 face - both
eyes - 48 x 53: every action's base). Every pose is lossless: parts cut square by square from a design and only moved
by whole squares, quarter turns about half-integer pivots and mirrors. League's Zoe is an acrobat - her attack is a
forward somersault, Paddle Star a twirl and a flip, the bubble a flip kick, Portal Jump a leap - so most actions turn
the whole figure by quarter turns in the air (ppu_rig.lie), the way league_rammus's attack tumbles.
Parts of the side design: the near arm (hanging behind her hip, the bangle and the hand at the bottom; it turns about
its shoulder), the two lower legs (rows LEG_TOP on, split at LEG_X); the rest is the body (the hair, the head, the
scarf, the top and the skirt).
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
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet, spans  # noqa: E402

HERO = "zoe"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "zoe", "hd")


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
# the near arm (side.png, read at 20x): the upper arm columns 32-35 from the shoulder (row 28) down, the forearm, the
# bangle (rows 36-38) and the hand (rows 39-42) hanging behind her hip at columns 27-33
ARM = [(range(28, 36), (32, 35)), (range(36, 43), (27, 33))]
SHOULDER = (34.5, 29.5)               # (x, y) the arm turns about
LEG_TOP = 43                          # the lower legs: rows LEG_TOP to the soles, columns LEG_COLS (the hair's tips
LEG_COLS = (31, 47)                   # reach row 43 further left), near columns <= LEG_X, far > LEG_X
LEG_X = 39
HIP = (37.5, 43.5)                    # the near leg turns about it (the kick)
ISLAND = 12                           # loose pieces up to this many squares are dropped (drop_islands)


def design():
    d = load("side.png")
    D = CutDesign(d, px=stand_col(d))
    D.part("arm", D.rows(spans(ARM)))
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    legs = D.box(LEG_TOP, D.H - 1, *LEG_COLS) & ~D.parts["arm"]
    D.part("far_leg", legs & (xx > LEG_X))
    D.part("near_leg", legs & (xx <= LEG_X))
    D.part("body", D.rest())
    return D


TINT = {"arm": (60, 120, 255), "far_leg": (255, 220, 0), "near_leg": (0, 220, 255)}


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
    """The designs' layers; pose() / the idle design -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.idle = self.placed(load("idle.png"))

    def placed(self, d):
        """Another design in a padded layer of the side design's size, standing on the same point and ground."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand_col(d)
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        lay[top:top + d.shape[0], x0:x1] = d[:, x0 - left:x1 - left]
        return lay

    def pose(self, crouch=0, whole=(0, 0), arm=(0, 0), arm_rot=0, legs=None, kick=0, fill=True):
        """crouch: rows the body (with the arm) sets down onto the lower legs; whole: the whole figure; arm: the near
        arm moved, arm_rot quarter turns counter-clockwise about SHOULDER (1: pointing forward, 2: up, 3: back); legs:
        ((near dx, dy), (far dx, dy)); kick: the near leg's quarter turns counter-clockwise about HIP (1: forward)."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nx, ny), (fx, fy) = legs or ((0, 0), (0, 0))
        L = self.L
        near = dict(dx=wx + nx, dy=wy + ny)
        if kick % 4:
            near.update(rot=kick, about=HIP, dy=uy + ny)
        layers = [(L["far_leg"], dict(dx=wx + fx, dy=wy + fy)), (L["near_leg"], near),
                  (L["body"], dict(dx=ux, dy=uy)),
                  (L["arm"], dict(dx=ux + arm[0], dy=uy + arm[1], rot=arm_rot, about=SHOULDER))]
        if kick % 4:          # the leg kicked forward is drawn over the skirt
            layers = layers[:1] + layers[2:] + layers[1:2]
        moved = arm != (0, 0) or arm_rot % 4
        can = R.compose(self.rig, layers, fill=[("arm", (ux, uy))] if moved and fill else ())
        if moved:
            can = drop_islands(can)
        return self.close_holes(can) if fill else can

    def front(self, crouch=0, whole=(0, 0), flash=False):
        """The 3/4 idle design, its body (above IDLE_LEG_ROW) set down `crouch` rows onto its own legs."""
        legs, top = self.idle.copy(), self.idle.copy()
        cut_row = P + IDLE_LEG_ROW
        legs[:cut_row] = 0
        top[cut_row:] = 0
        wx, wy = whole
        can = R.compose(self.rig, [(legs, dict(dx=wx, dy=wy)), (top, dict(dx=wx, dy=wy + crouch))])
        return R.flash(can) if flash else can

    ref_holes = None
    close_holes = _Form.close_holes                   # small enclosed holes the side lacks, filled (league_wukong)
    MOST = _Form.MOST


def drop_islands(can, most=ISLAND):
    """Pieces of at most `most` squares cut off from the figure: the tip of a hair strand that hung beside the arm
    (rows 32-36, columns 30-32 of the side design) floats once the arm swings away; it goes with the arm's move."""
    op = can[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n < 2:
        return can
    out = can.copy()
    sizes = ndimage.sum(op, lbl, range(1, n + 1))
    for k, sz in enumerate(sizes, 1):
        if sz <= most:
            out[lbl == k] = 0
    return out


def shift(can, dx, dy):
    out = np.zeros_like(can)
    H, W = can.shape[:2]
    ys, xs = slice(max(0, dy), H + min(0, dy)), slice(max(0, dx), W + min(0, dx))
    yd, xd = slice(max(0, -dy), H + min(0, -dy)), slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = can[yd, xd]
    return out


def form():
    F = Form(design(), rig_pad=(60, 60, 70, 20))
    # a step opens cracks between the legs and the skirt: closed with the outline (Rig.finish, gap-check)
    F.rig.fill_rows = (LEG_TOP - 4, F.D.H - 1)
    F.rig.idle_canvas = F.pose()
    return F


IDLE_LEG_ROW = 41                     # the idle design's legs: rows from here down stay while the body breathes
BACK_SINK = 20                        # lying on her back: the hair's rows hidden by the ground (the hair from column 0, her
                                      # back at column 34: 14 rows of the mane stay as the bed she lies on)


def tries(F):
    p = F.pose
    return [p(), p(arm_rot=1), p(arm_rot=2), p(arm_rot=3), p(kick=1, whole=(0, -6)), p(crouch=2), F.front(),
            F.front(crouch=1)]


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_zoe.py) come from these
MS = {"idle": [150] * 8, "run": [100] * 8,
      "attack": [80, 70, 70, 70, 80, 90], "attack_p": [80, 80, 90, 90, 110],
      "skill": [70, 70, 70, 90, 70, 70, 60], "skill2": [70, 70, 80, 100, 70, 60],
      "ult": [80, 60, 80, 80, 70, 70], "skill_w": [60, 60, 60, 60, 80], "ult_exit": [60, 70, 70],
      "ult_back": [80, 80, 140],
      "hit": [100, 100], "dead": [100, 110, 120, 150, 60, 60, 100, 500]}


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}

    def tumble(k, dx, up, **kw):
        """The side pose turned k quarter turns counter-clockwise (3: forward), up rows in the air, dx forward."""
        return shift(R.lie(rig, p(**kw), k, dx=dx, sink=0), 0, -up)
    # idle (League's Zoe_Idle1: she bobs on the spot): the 3/4 design's body sets down a row onto its legs
    out["idle"] = [F.front(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # auto attack (League's Zoe_attack1: she crouches, springs up with the arm flung back and flicks the star off at
    # the top, then comes down bent forward and lands): crouched, up with the arm back, the flick (the arm forward,
    # frame 3: the star leaves), coming down, landing low, standing
    out["attack"] = [p(crouch=2), p(whole=(0, -5), arm_rot=3), p(whole=(1, -6), arm_rot=1), p(whole=(2, -3), arm_rot=1),
                     p(crouch=2, whole=(2, 0), arm_rot=1), p(whole=(1, 0))]
    # More Sparkles! (League's Zoe_Empowered_Attack: a big jump with the arms flung out, the star thrown down from the
    # top): crouched, up high with the arm drawn back, the throw (the arm forward at shoulder height - turned up it
    # covered her face), coming down, landing
    out["attack_p"] = [p(crouch=2), p(whole=(0, -9), arm_rot=3), p(whole=(1, -8), arm_rot=1, arm=(0, -2)),
                       p(whole=(1, -4), arm_rot=1), p(crouch=2, whole=(1, 0))]
    # Q Paddle Star (League's Spell1: a hop and a twirl in the air with the arm drawn back, a low landing as the star is
    # flung forward, then she straightens up): crouched with the arm back, up, higher, the throw landing low (the arm
    # forward, frame 4), held low, rising, standing
    out["skill"] = [p(crouch=2, arm_rot=3), p(whole=(0, -5), arm_rot=3), p(whole=(-1, -7), arm_rot=3),
                    p(crouch=2, whole=(1, 0), arm_rot=1), p(crouch=2, whole=(1, 0), arm_rot=1), p(crouch=1, whole=(1, 0)),
                    p(whole=(0, 0))]
    # E Sleepy Trouble Bubble (League's Zoe_Spell3: she springs up, turns upside down in the air and flies feet first at
    # the bubble, kicking it off): crouched, up, upside down (half a turn), the flying kick (the whole figure tipped
    # back a quarter turn, the legs forward, frame 4 - her shin alone turned at the knee did not read as a kick),
    # landing, standing
    out["skill2"] = [p(crouch=2), p(whole=(1, -6)), tumble(2, 3, 9), tumble(1, 5, 7, arm_rot=3),
                     p(crouch=2, whole=(3, 0)), p(whole=(1, 0))]
    # R Portal Jump (League's Zoe_Spell2: a leap into the portal, out at the far end, landing wide): crouched, up, high
    # (the jump, on frame 3 she is through), falling in from above at the far end, landing, standing wide (the 3/4 idle
    # with its arms out)
    out["ult"] = [p(crouch=2), p(whole=(1, -8), arm_rot=3), p(whole=(2, -16), arm_rot=3), p(whole=(0, -12)),
                  p(crouch=2), F.front()]
    # W Spell Thief's missiles, thrown after the portal's star (League's Zoe_spell2_missile: a little hop, a toss of the
    # hand, landing with the arms out): crouched with the arm back, up with the toss (the arm forward, frame 2: the
    # missiles leave), higher, coming down, standing wide (the 3/4 idle)
    out["skill_w"] = [p(crouch=2, arm_rot=3), p(whole=(1, -4), arm_rot=1), p(whole=(1, -5), arm_rot=1),
                      p(whole=(1, -2)), F.front()]
    # leaving the far end to go back (League's Zoe_Spell4_Exit: she springs straight up out of sight): crouched, up,
    # high up
    out["ult_exit"] = [p(crouch=2), p(whole=(0, -8), arm_rot=3), p(whole=(0, -16), arm_rot=3)]
    # back through the portal (League's Zoe_Spell4_B: dropping in from above): falling in, landing, standing
    out["ult_back"] = [p(whole=(0, -10)), p(crouch=2), F.front()]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]

    # the death (League's Zoe_Death: she spins, tips over backwards and lands on her back, legs up, then lies still):
    # staggering, crouched, tipping back (a quarter turn, in the air), on her back, a bounce, lying. Lying on her back
    # the mane streaming behind her points into the ground: her back rests on the ground line and the hair under it is
    # hidden by the ground (turned with her, it held her body 25 rows up in the air)
    def lying(up=0, dx=-8):
        can = R.lie(rig, p(arm_rot=1), 1, dx=dx, sink=BACK_SINK)      # the arm forward: up off the ground
        can[rig.GY:] = 0
        return shift(can, 0, -up)
    out["dead"] = [p(whole=(-1, 0)), p(crouch=2, whole=(-2, 0)), shift(R.lie(rig, p(arm_rot=1), 1, dx=-6, sink=0), 0, -4),
                   lying(), lying(2), lying(), lying(), lying()]
    return out


# ------------------------------------------------------------------------------------------------- the run
# League's Zoe_Run1: a skipping run. The design's own lower legs step whole under the body (each planted and sliding
# back, then lifted and carried forward, the far one half a cycle later), the body set down a row on each contact and
# lifted a row between (the skip) - league_wukong's walk.
from rig_wukong import _steps  # noqa: E402

RUN_STEP = dict(_steps(3, (1, 2, 1)), rise=[0, 1, 1, 0, 0, 1, 1, 0])


def run(F, steps=None):
    st = steps or RUN_STEP
    out = []
    for (ndx, nup), (fdx, fup), bob, up_ in zip(st["near"], st["far"], st["bob"], st["rise"]):
        out.append(F.pose(whole=(0, bob - up_), legs=((ndx, -nup), (fdx, -fup))))
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": run(F), **{k: v for k, v in a.items() if k != "idle"}}
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

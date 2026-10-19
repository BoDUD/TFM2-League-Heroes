#!/usr/bin/env python3
"""league_chogath's action frames posed from the approved designs' own squares (the 2026-10-19 frame-audit way:
lossless poses compared with League's clips) and, where League rears him up or lays him down, from Codex's poses drawn
on the side design's grid (pack_chogath_poses.py).

    python tools/art/rig_chogath.py --parts DIR       # the side design with its parts tinted + walk tries (12x)
    python tools/art/rig_chogath.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_chogath.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_chogath.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (the user's picks 2026-10-19; 38 game px at PPU 1.2, one palette): idle.png (A-1, 3/4 front, 69 x 46:
the idle and the hit) and side.png (side-1 with the idle's head, side-on facing right, 71 x 45: every action's base,
its standing point and ground the rig's own). Every pose is lossless: parts cut square by square from a design and only
moved by whole squares, quarter turns and mirrors.
Parts of the side design: the four legs below the belly (rows from LEG_ROW down, split by columns: the near hind leg,
the far hind leg, the far front leg, the near front leg under the jaw); the rest is the body (the carapace, the head,
the scythe arms, the tail).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet  # noqa: E402

HERO = "chogath"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "chogath", "hd")


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
# (rows from, columns from - to) of each leg on hd/side.png; the near front leg starts lower (the jaw sits on it)
LEGS = {"near_hind": (36, 15, 30), "far_hind": (36, 31, 40), "far_front": (37, 41, 51), "near_front": (40, 52, 66)}
FAR = ("far_hind", "far_front")


def design():
    d = load("side.png")
    D = CutDesign(d, px=stand_col(d))
    for name, (y0, x0, x1) in LEGS.items():
        D.part(name, D.box(y0, D.H - 1, x0, x1))
    D.part("body", D.rest())
    return D


TINT = {"near_hind": (255, 60, 60), "far_hind": (60, 120, 255), "far_front": (0, 220, 255), "near_front": (255, 220, 0)}


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
        self.other = {n: self.placed(load(f"{n}.png")) for n in ("idle",)}
        for n, foot in POSES.items():
            self.other[n] = self.by_foot(load(f"pose_{n}.png"), foot)

    def placed(self, d):
        """Another design in a padded layer of the side design's size, standing on the same point and ground."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand_col(d)
        lay[top:top + d.shape[0], left:left + d.shape[1]] = d
        return lay

    def by_foot(self, d, foot):
        """A Codex pose in a padded layer of the side design's size: its near hind foot (column `foot`) on the side
        design's (SIDE_FOOT), its lowest row on the ground (every pose has a foot, a claw or the lying body there)."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + SIDE_FOOT - foot
        y0, x0 = max(0, top), max(0, left)
        lay[y0:top + d.shape[0], x0:left + d.shape[1]] = d[y0 - top:, x0 - left:]
        return lay

    def pose(self, whole=(0, 0), body=(0, 0), legs=None, fill=True):
        """whole: the whole figure moved; body: the body moved on its legs (never lifted off them); legs: {leg: (dx,
        dy)} each leg moved whole (lifted: dy < 0)."""
        wx, wy = whole
        bx, by = body
        if by < 0:
            raise ValueError("the body never lifts off the legs")
        legs = legs or {}
        L = self.L
        lay = []
        for name in ("far_hind", "far_front"):
            dx, dy = legs.get(name, (0, 0))
            lay.append((L[name], dict(dx=wx + dx, dy=wy + dy)))
        lay.append((L["body"], dict(dx=wx + bx, dy=wy + by)))
        for name in ("near_hind", "near_front"):
            dx, dy = legs.get(name, (0, 0))
            lay.append((L[name], dict(dx=wx + dx, dy=wy + dy)))
        can = R.compose(self.rig, lay)
        return self.close_holes(can) if fill else can

    def whole(self, name, dx=0, dy=0, flash=False):
        can = R.compose(self.rig, [(self.other[name], dict(dx=dx, dy=dy))])
        return R.flash(can) if flash else can

    ref_holes = None
    close_holes = _Form.close_holes                   # small enclosed holes the side lacks, filled (league_wukong)
    MOST = _Form.MOST


def eye_point(d):
    """The middle of the topmost cyan squares (the eyes; the tongue's cyan lies lower): (row, column)."""
    a = d.astype(int)
    cy = (a[..., 2] > 180) & (a[..., 1] > 170) & (a[..., 0] < 140) & (a[..., 3] > 0)
    yy, xx = np.nonzero(cy)
    top = yy <= yy.min() + 2
    return yy[top].mean(), xx[top].mean()


# Codex's poses (tools/art/design_chogath_poses.py -> hd/pose_<name>.png) stand on the side design's hind feet (League:
# rearing, slamming and biting he pivots on his planted hind legs): each pose's near hind foot column (the middle of its
# talons on the ground; slam's hind legs kick back in the air - its hips' column less the side design's hip-to-foot 3)
SIDE_FOOT = 24
POSES = {"crouch": 26, "rise": 22, "rear": 24, "slam": 17, "lunge": 19, "fall": 31, "lie": 37}


def shift(can, dx, dy):
    out = np.zeros_like(can)
    H, W = can.shape[:2]
    ys, xs = slice(max(0, dy), H + min(0, dy)), slice(max(0, dx), W + min(0, dx))
    yd, xd = slice(max(0, -dy), H + min(0, -dy)), slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = can[yd, xd]
    return out


def form():
    return Form(design(), rig_pad=(40, 40, 60, 20))


# ------------------------------------------------------------------------------------------------- the walk
# League's chogath_run: a heavy bounding gallop, the body rocking down and up once a stride and surging forward as
# it pushes off. The design's own legs step whole (league_braum / league_nautilus heavy walks): a planted leg slides
# back under the body, a lifted one is carried forward off the ground; the near hind leg with the far front leg, the
# far hind leg with the near front leg half a cycle later. The body sets down onto the legs as a pair lands (BOB) and
# the whole figure surges a column forward on the push (SURGE).
STRIDE = [2, 1, -1, -3, -2, 0, 2, 3]          # a leg's column offset round the cycle (planted 0-3, swinging 4-7)
LIFT = [0, 0, 0, 0, 2, 3, 2, 1]
BOB = [2, 1, 0, 0, 2, 1, 0, 0]
SURGE = [0, 0, 1, 1, 0, 0, 1, 1]


def walk(F):
    out = []
    for i in range(8):
        j = (i + 4) % 8
        a = (STRIDE[i], -LIFT[i])
        b = (STRIDE[j], -LIFT[j])
        out.append(F.pose(whole=(SURGE[i], 0), body=(0, BOB[i]),
                          legs={"near_hind": a, "far_front": a, "far_hind": b, "near_front": b}))
    return out


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_chogath.py) come from these
MS = {"idle": [150] * 8, "run": [90] * 8,
      "attack": [70, 70, 90, 90, 80, 100], "attack_e": [70, 80, 90, 90, 80, 90],
      "skill": [70, 100, 100, 100, 120, 100], "skill2": [60, 60, 90, 140, 140, 90, 70],
      "ult": [80, 100, 100, 150, 150, 100],
      "hit": [100, 100], "dead": [120, 100, 120, 100, 150, 60, 100, 500]}
IDLE_LEG_ROW = 38                     # the idle design's legs: rows from here down stay while the body breathes


def frames_all(F):
    rig = F.rig
    out = {}
    # idle (League's chogath_idle1: he breathes, the carapace sinking and rising on his planted legs): the 3/4
    # design's body sets down a row onto its legs
    idle = F.other["idle"]
    legs, top = idle.copy(), idle.copy()
    ys = np.nonzero(idle[..., 3].any(1))[0]
    cut_row = ys.max() + 1 - (46 - IDLE_LEG_ROW)
    legs[:cut_row] = 0
    top[cut_row:] = 0

    def breathe(c):
        return R.compose(rig, [(legs, dict(dy=0)), (top, dict(dy=c))])
    out["idle"] = [breathe(c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    out["hit"] = [F.whole("idle", dx=-2, flash=True), F.whole("idle", dx=-1)]
    w = F.whole
    # auto attack (League's chogath_attack1 / attack2: he crouches, rears up on his hind legs with the scythes high and
    # slams down onto all fours, the claws and the maw striking - the hit on frame 4)
    out["attack"] = [w("crouch"), w("rise"), w("rear"), w("slam"), w("slam", dx=1), w("crouch")]
    # E's spiked attack (League's chogath_crit: the same rear and slam, deeper - the spikes leave on frame 4)
    out["attack_e"] = [w("crouch", dx=-1), w("rise", dx=-1), w("rear", dx=-1), w("slam", dx=1), w("slam", dx=2),
                       w("crouch")]
    # Q Rupture (League's chogath_spell4: he ducks low and stamps, head down - the ground cracks on frame 2 - then arches
    # up and settles)
    out["skill"] = [w("crouch"), w("slam"), w("slam"), w("rise"), w("rear"), w("crouch")]
    # W Feral Scream (League's chogath_spell1: he rears up, the head thrown back, and screams - the scream from frame 3)
    out["skill2"] = [w("crouch"), w("rise"), w("rear"), w("rear", dy=-1), w("rear"), w("rise"), w("crouch")]
    # R Feast (League's chogath_spell2: he lunges and bites, rears up swallowing it whole, comes down - the bite frame 2)
    out["ult"] = [w("crouch"), w("lunge"), w("lunge", dx=1), w("rear"), w("rear", dy=-1), w("crouch")]

    # the death (League's chogath_death: he rears up, twists and collapses onto his side): rearing, half down,
    # collapsing, down, on his side, a bounce, lying
    out["dead"] = [w("rear"), w("rise"), w("fall"), w("fall", dy=1), w("lie"), w("lie", dy=-1), w("lie"), w("lie")]
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
    t = [F.rig.finish(c) for c in walk(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_walk1.png"), z=6)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_walk2.png"), z=6)


if __name__ == "__main__":
    main()

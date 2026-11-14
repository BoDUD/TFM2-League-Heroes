#!/usr/bin/env python3
"""league_warwick's action frames, posed on the approved 3/4 design after League's own clips, frame by frame (the user,
2026-10-20: 「不做侧面 只做四分之三的侧面」「动作帧按照英雄联盟的自己做」「做到完美了喊我review」).

    python tools/art/rig_warwick.py --parts DIR       # the design with its parts tinted (12x)
    python tools/art/rig_warwick.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_warwick.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_warwick.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/review_warwick_actions.py --out DIR   # League left / ours right, one GIF

The design (tools/art/design_warwick_model.py: Codex's step-1 take A-1, drawn at the count - 46 game px spike top to
soles at PPU 1.5 = 69 rows, 94 wide with the tail; Codex's own face): League's idle seen 3/4 from the front-right -
hunched, the head pushed out, the near arm (image left, the gauntlet with the green vials) hanging at his side, the far
arm (image right) hanging forward with its claws open, the tail raised behind him.
Lossless (memory rig-deformation-checks): parts cut square by square from the design and moved by whole squares, the
far arm also turned by quarter turns about its shoulder (forward for the swipes, up for the wind-ups, drawn behind the
head so it never covers the face); the head is never cut from the body, sheared or turned. Parts: the tail (left of
the near gauntlet), the far arm (right of the face from the shoulder down), the near arm (the gauntlet and the hand),
the two legs under the shorts; the rest is the body.
The run below was league_braum's / league_galio's approved walk for big heroes (memory run-legs-caitlyn-way, 「你按照泰坦布隆那种
走路方式这种腿就不会变形」): the design's own legs, one lifted per frame by losing its top rows and stepped forward, the body
floating a little, the arms swinging a square against the legs, the tail swaying. Since 2026-11-01 (「狼人的走路姿势现在有点
奇怪」) it only places the frames: the export ends with tools/art/casts_warwick_run.py writing Codex's redrawn run over it.
The in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」):
a Codex pose with a part of it moved (PARTS, in the pose's own squares): the bushy tail waved by its columns from where
it leaves him (only its fur and the outline round it: a gauntlet or a claw in its box stays), the raised forearm turned
about the elbow; every other square of the pose checked unchanged (no head box: Codex's own face, far from both parts).
The design's own frames move its tail whole (pose's tail_at, up and down only, as the idle does).
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
import inbetween as IB  # noqa: E402
from rig_wukong import CutDesign as _Cut, P, pad  # noqa: E402

HERO = "warwick"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "warwick", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the design's parts
STAND = 52                     # the column between his feet: the standing point
TAIL = (0, 52, 0, 25)          # rows, columns (inclusive): the tail, left of the near gauntlet's outline (column 26)
NEAR_ARM = [(28, 46, 25, 40), (47, 60, 25, 36)]   # the near gauntlet, the hand hanging from it (in front of the near leg)
# the legs: whole from the thigh under the shorts (so the shorts slide over the thigh's top when the body moves, never a
# step in the thigh), the shorts' own olive squares left to the body
NEAR_FOOT = (61, 68, 24, 40)   # the near foot under the hand: the near leg's only part that steps (the near thigh, beside the
                               # hand, stays with the body; the shin between them is hidden behind the hand in the design)
FAR_LEG = [(47, 68, 64, 82), (54, 68, 57, 82)]      # the far thigh right of the shorts, the shin and the long foot
FAR_SHOULDER = (79.0, 30.0)    # what the far arm turns about (square edges)


def far_arm_mask(D):
    """The far arm: right of the face from the shoulder down - rows 29-31 from column 78, rows 32-61 from column 75
    (the face's muzzle and teeth end at column 76 / 73) - above the far foot (rows 62 on)."""
    m = np.zeros((D.H, D.W), bool)
    m[29:32, 78:] = True
    m[32:62, 75:] = True
    return m & (D.d[..., 3] > 0)


def olive(d):
    """The shorts' olive and khaki squares (and the belt's browns): warm, green above blue."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (d[..., 3] > 0) & (r > 55) & (g > 45) & (r >= g) & (g > b + 15) & (r < 190)


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    D.part("tail", D.box(*TAIL[:2], *TAIL[2:]))
    D.part("far_arm", far_arm_mask(D))
    shorts = olive(d)
    D.part("near_leg", D.box(*NEAR_FOOT))
    D.part("far_leg", (D.box(*FAR_LEG[0]) | D.box(*FAR_LEG[1])) & ~shorts & ~far_arm_mask(D))
    D.part("near_arm", D.box(*NEAR_ARM[0]) | D.box(*NEAR_ARM[1]))
    D.part("body", D.rest())
    return D


TINT = {"tail": (60, 200, 255), "far_arm": (255, 220, 0), "near_arm": (0, 255, 120), "near_leg": (255, 0, 255),
        "far_leg": (255, 120, 0)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


# ------------------------------------------------------------------------------------------------- lossless moves
def turned(layer, k, about):
    """A padded layer turned k quarter turns counter-clockwise on screen about `about` (design square edges): every
    square kept, none stretched."""
    out = np.zeros_like(layer)
    ys, xs = np.nonzero(layer[..., 3] > 0)
    ax, ay = about[0] + P, about[1] + P
    ox, oy = xs + 0.5 - ax, ys + 0.5 - ay
    for _ in range(k % 4):
        ox, oy = oy, -ox
    tx = np.floor(ax + ox).astype(int)
    ty = np.floor(ay + oy).astype(int)
    ok = (tx >= 0) & (tx < out.shape[1]) & (ty >= 0) & (ty < out.shape[0])
    out[ty[ok], tx[ok]] = layer[ys[ok], xs[ok]]
    return out


def lifted(layer, lift):
    """A leg layer lifted `lift` rows by losing its top rows (the thigh turned toward us): league_braum's walk."""
    if not lift:
        return layer
    out = layer.copy()
    ys = np.nonzero(layer[..., 3].any(1))[0]
    out[:ys.min() + lift] = 0
    return np.roll(out, -lift, axis=0)


def close_cracks(can, outline, most=12, slit=40):
    """Enclosed gaps a move opened: up to `most` squares, or up to `slit` squares but only one square across (a crack
    between a moved part and the one beside it, two squares across at most) - the outline (gap-check). The design's own armpit gap (37 squares,
    several across) stays open."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        k = int(h.sum())
        if k <= most or (k <= slit and ndimage.distance_transform_edt(h).max() <= 1.5):
            out[h] = (*outline, 255)
    return out


class Form:
    """The design's layers; pose() -> canvas."""

    def __init__(self, D, rig_pad=(70, 70, 70, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}

    def pose(self, whole=(0, 0), crouch=0, upper=0, far=0, far_at=(0, 0), near_at=(0, 0), tail_at=(0, 0),
             near_leg=(0, 0, 0), far_leg=(0, 0, 0), far_back=None, tail=True):
        """whole: the figure (dx, dy); crouch: rows the upper body (body, arms, tail) sets down onto the legs; upper:
        columns the upper body moves over the legs; far: the far arm's quarter turns (counter-clockwise) about its
        shoulder, moved far_at; near_at / tail_at: the near arm's / the tail's (dx, dy) on the upper body; near_leg /
        far_leg: a leg's (dx, dy, lift) - the far leg lifted by losing its top rows (league_braum), the near foot (all
        of the near leg that steps) moved up whole; far_back: the far arm drawn behind the body (default: when
        turned)."""
        wx, wy = whole
        ux, uy = wx + upper, wy + crouch
        L = self.L
        arm = turned(L["far_arm"], far, FAR_SHOULDER) if far else L["far_arm"]
        behind = far != 0 if far_back is None else far_back
        layers = [(L["tail"], dict(dx=ux + tail_at[0], dy=uy + tail_at[1]))] if tail else []
        layers.append((lifted(L["far_leg"], far_leg[2]), dict(dx=wx + far_leg[0], dy=wy + far_leg[1])))
        if behind:
            layers.append((arm, dict(dx=ux + far_at[0], dy=uy + far_at[1])))
        layers.append((L["body"], dict(dx=ux, dy=uy)))
        if not behind:
            layers.append((arm, dict(dx=ux + far_at[0], dy=uy + far_at[1])))
        layers.append((L["near_leg"], dict(dx=wx + near_leg[0], dy=wy + near_leg[1] - near_leg[2])))
        layers.append((L["near_arm"], dict(dx=ux + near_at[0], dy=uy + near_at[1])))
        can = R.compose(self.rig, layers)
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def posed(self, name, whole=(0, 0), lift=0, sway=(), spins=()):
        """A Codex pose (hd/pose_<name>.png, design_warwick_poses.py) standing where the design stands: the middle of its
        shorts (shorts_mid: the body's own middle, steady while the limbs swing) on the design's, its lowest row on the
        ground - `lift` rows above it (in the air). sway / spins (inbetween.vary, by PARTS' names): an in-between made
        from it, placed where the pose stands."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        top = P + self.D.ground - (ys.max() + 1) - lift
        left = P + int(round(shorts_mid(self.D.d) - shorts_mid(d)))
        if sway or spins:
            d = IB.vary(d, parts(d, PARTS[name]), self.D.outline, (), sway, None, None, VPAD, name, spins=spins)
            top, left = top - VPAD, left - VPAD
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        y0, y1 = max(0, top), min(lay.shape[0], top + d.shape[0])
        lay[y0:y1, x0:x1] = d[y0 - top:y1 - top, x0 - left:x1 - left]
        can = R.compose(self.rig, [(lay, dict(dx=whole[0], dy=whole[1]))])
        can[self.rig.GY:] = 0
        return can


# ------------------------------------------------------------------------------------------------- the in-betweens
VPAD = 30                      # an in-between's picture is this much bigger on every side (inbetween.vary)
# each pose's parts, in its own squares: ("fur", box) = the tail's fur in the box and the outline round it (fur_in: a
# gauntlet, a claw or the shorts in the box stay where they are), cut square across where the tail meets his back or
# leg; plain boxes otherwise
PARTS = {
    "crouch": {"tail": [("fur", (0, 0, 20, 42))]},          # raised behind him, over the near gauntlet
    "rear": {"tail": [("fur", (0, 38, 24, 71))]},           # hanging behind, under the near gauntlet
    "leap": {"tail": [("fur", (0, 32, 30, 50)), ("fur", (0, 51, 13, 59))]},   # streaming back over the trailing leg
    "bite": {"tail": [("fur", (0, 0, 26, 34))]},            # raised behind him, over the near gauntlet
    "howl": {"tail": [("fur", (0, 32, 22, 66))]},           # hanging behind the near arm
    "strike": {"tail": [("fur", (0, 0, 30, 39))]},          # raised high behind him
    "raise": {"tail": [("fur", (0, 58, 29, 79))],           # low behind him, under the hanging near arm
              "forearm": [(63, 0, 82, 26)]},                # the raised far forearm: the gauntlet, the hand, the claws
    "stagger": {"tail": [("fur", (0, 49, 37, 70))]},        # swung out behind, under the near arm
    "lie": {"tail": [(0, 16, 40, 29)]},                     # lying on his legs (nothing else in the box)
}
ELBOW = {"raise": (67, 27)}    # the raised forearm turns about the elbow's inner corner (inbetween.spin)


def fur(d):
    """His blue fur (every blue of the design: blue well over red, not under green)."""
    c = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (c[..., 2] > c[..., 0] + 25) & (c[..., 2] >= c[..., 1])


def fur_in(d, box):
    """The fur's squares in the box (x0, y0, x1, y1) and the near-black squares edging them where nothing but fur and
    air is next to them (a line between the tail and a gauntlet lying over it stays with the gauntlet)."""
    x0, y0, x1, y1 = box
    op = d[..., 3] > 0
    inb = np.zeros(op.shape, bool)
    inb[y0:y1 + 1, x0:x1 + 1] = True
    f = fur(d) & inb
    dark = op & inb & (IB.lum(d[..., :3]) < IB.DARK)
    other = op & ~fur(d) & ~dark
    near = lambda m: np.pad(m, 1)[2:, 1:-1] | np.pad(m, 1)[:-2, 1:-1] | np.pad(m, 1)[1:-1, 2:] | np.pad(m, 1)[1:-1, :-2]
    return f | (dark & near(f) & ~near(other))


def parts(d, spec):
    """PARTS' items -> row runs (x0, y, x1, y) for inbetween.vary."""
    out = {}
    for k, items in spec.items():
        m = IB.part_mask(d.shape, [it for it in items if it[0] != "fur"])
        for it in items:
            if it[0] == "fur":
                m |= fur_in(d, it[1])
        runs = []
        for y in range(m.shape[0]):
            xs = np.nonzero(m[y])[0]
            if not len(xs):
                continue
            cut = np.nonzero(np.diff(xs) > 1)[0]
            runs += [(int(a), y, int(b), y) for a, b in zip(np.r_[xs[0], xs[cut + 1]], np.r_[xs[cut], xs[-1]])]
        out[k] = runs
    return out


def tail(name, k):
    """The tail of pose `name` waved: its columns lifted 0..k rows from where it leaves him to its tip (negative:
    lowered; inbetween.wave)."""
    x1 = max((it[1] if it[0] == "fur" else it)[2] for it in PARTS[name]["tail"])
    return [("tail", 0, x1, k, "right")]


def shorts_mid(d):
    """The middle column of a figure's olive shorts."""
    xs = np.nonzero(olive(d))[1]
    return (xs.min() + xs.max() + 1) / 2


def form():
    F = Form(design())
    F.rig.idle_canvas = F.pose()
    return F


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_warwick.py) come from these (a frame's start in ticks = ms x 0.06)
# The in-betweens (2026-11-14: the bite, the leap, R's dash and R's hold were one or two pictures moved or held): Q's
# leap, the bite's getting up and the hold's raised claw split in two (inbetween.spans: whole ms, none under 50); every
# action is as long as it was and every frame that begins a move keeps its millisecond (the leap at 70, the rakes at 0,
# 500 and 1000).
MS = {"idle": [150] * 8, "run": [95] * 8,
      "attack": [70, 80, 90, 90, 90, 80],
      "skill": IB.spans((70, 1), (130, 2)), "skill_bite": IB.spans((100, 1), (100, 1), (100, 2)),
      "skill2": [60, 90, 100, 83], "skill2_howl": [60, 85, 85, 85, 85],
      "ult": [70, 60, 90, 90, 90], "ult_dash": [83, 83, 83, 84],
      "ult_hold": IB.spans((150, 1), (150, 1), (200, 2)) * 3,
      "hit": [100, 100],
      "dead": [120, 120, 140, 160, 200, 600]}
# the walk (league_braum / league_galio): per frame the near leg's (dx, dy, lift), the far leg's, the figure's rise, the
# arms' swing (columns: the near arm, the far arm - against the legs), the tail's sway (dx, dy)
# (the near arm stays: its hand hides the near shin, which the design does not draw - moved, it opens a gap; the far arm
# swings a square forward only - back, it would touch the muzzle; the tail sways right / up / down only: its right edge,
# hidden behind the near gauntlet in the design, is a straight line that must never show)
WALK = [((0, 0, 0), (0, 0, 2), 1, (0, 0), (0, 0)), ((0, 0, 0), (2, 0, 5), 2, (0, 0), (1, 0)),
        ((0, 0, 0), (2, 0, 2), 1, (0, 0), (1, 1)), ((0, 0, 0), (2, 0, 0), 0, (0, 1), (0, 1)),
        ((0, 0, 2), (0, 0, 0), 1, (0, 1), (0, 0)), ((2, 0, 5), (0, 0, 0), 2, (0, 1), (1, 0)),
        ((3, 0, 2), (0, 0, 0), 1, (0, 1), (1, -1)), ((3, 0, 0), (0, 0, 0), 0, (0, 0), (0, -1))]
DEAD_SINK = 6                                # rows of the lying figure under the ground line (lying flat, not a heap)
SWIPE = dict(far=1, far_at=(-6, 4))          # the far arm thrust forward (claws ahead at head height, its root behind the jaw)
RAISE = dict(far=2, far_at=(-2, 3))          # the far arm raised behind the head (the claws over the far ear)


def frames_all(F):
    p, q = F.pose, F.posed
    out = {}
    # idle (League's Warwick_Idle: a slow heavy breath, the shoulders rising and falling): the upper body sets down a
    # row onto the legs and comes back, the tail a beat behind
    out["idle"] = [p(crouch=c, tail_at=(0, t)) for c, t in ((0, 0), (0, 0), (1, 0), (1, 1), (1, 1), (1, 1), (0, 1),
                                                             (0, 0))]
    # run (League's Warwick_Run, a heavy bounding run): league_braum's walk on the design's own legs
    out["run"] = [p(whole=(0, -r), near_leg=n, far_leg=f, near_at=(sw[0], 0), far_at=(sw[1], 0), tail_at=t)
                  for n, f, r, sw, t in WALK]
    # auto attack (League's Warwick_Attack1: crouched low with the arms spread, then lunging forward and down with the
    # claws; the hit at ~150 ms = tick 9): crouched (Codex's crouch), the lunge with both claws raking down (strike:
    # the hit), held, back up
    # (the in-betweens: the tail dipping as he springs, whipping down after the rake, settling)
    out["attack"] = [q("crouch"), q("crouch", whole=(1, 0), sway=tail("crouch", -6)), q("strike", whole=(2, 0)),
                     q("strike", whole=(2, 0), sway=tail("strike", -6)), p(whole=(1, 0), tail_at=(0, 2)), p()]
    # Q Jaws of the Beast (League's Warwick_Spell1: reared back with the claws up and the jaws open, the leap, landed
    # low on the bite): skill = the rear and the leap (12 ticks; he flies from tick 4), skill_bite = low on the bite,
    # crouched, up again
    # (the in-betweens: the tail swinging down in the leap, swinging on after the bite, settling as he gets up; a tail
    # with a leg or an arm drawn over its edge only moves in under it)
    out["skill"] = [q("rear"), q("leap", whole=(2, 0), lift=6), q("leap", whole=(2, 0), lift=6, sway=tail("leap", -6))]
    out["skill_bite"] = [q("bite", whole=(2, 0)), q("bite", whole=(1, 0), sway=tail("bite", -6)),
                         q("crouch", sway=tail("crouch", -5)), q("crouch")]
    # E Primal Howl (League's Warwick_Spell3: rearing up with the fists raised, then the guard): skill2 = crouched,
    # reared up with the claws before his chest, back; skill2_howl (League's Spell3_Howl: gathered low, then standing
    # tall, chest out, the jaws to the sky): crouched, standing tall (Codex's howl) and held, back
    # (the in-betweens: the reared-up and the howling poses held with the tail swinging)
    out["skill2"] = [q("crouch"), q("rear"), q("rear", sway=tail("rear", 6)), p()]
    out["skill2_howl"] = [q("crouch"), q("howl"), q("howl", sway=tail("howl", 6)), q("howl", sway=tail("howl", -5)),
                          p()]
    # R Infinite Duress (League's Warwick_Spell4 + Spell4Dash: crouched low with the claws forward, the leap with both
    # arms raised): ult = the coil and the spring (the leap leaves at tick 8), ult_dash = in the air until he lands on
    # the champion
    # (the in-betweens: the coiled tail dipping, then swinging down twice in the air)
    out["ult"] = [q("crouch"), q("crouch", whole=(1, 0), sway=tail("crouch", -6)), q("leap", whole=(2, 0), lift=4),
                  q("leap", whole=(3, 0), lift=7, sway=tail("leap", -6)),
                  q("leap", whole=(3, 0), lift=7, sway=tail("leap", -3))]
    out["ult_dash"] = [q("leap", lift=h, sway=tail("leap", k) if k else ())
                       for h, k in ((7, 0), (8, -6), (7, -2), (4, -5))]
    # R's hold (League's Warwick_Spell4Hit: on top of the champion, raking down with both claws, then rearing up with
    # one claw raised high, again and again; the three claws at ticks 1 / 31 / 61): the rake (strike), held, the claw
    # raised (raise)
    # (the in-betweens: the raked-down pose held with the tail whipping down; the raised claw coming down - the forearm
    # turned 35 degrees about the elbow - before the next rake)
    hold = [q("strike"), q("strike", sway=tail("strike", -6)), q("raise"),
            q("raise", spins=[("forearm", ELBOW["raise"], 35, "under")])]
    out["ult_hold"] = [c.copy() for _ in range(3) for c in hold]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Warwick_Death: struck back with the arms flung out, then down on his belly): staggering
    # (Codex's stagger), a step back, falling flat (lie, in the air), down, a bounce, lying
    # (the in-betweens: the tail swinging up under the near arm as he staggers, flopping down as he falls and bounces)
    out["dead"] = [q("stagger"), q("stagger", whole=(-1, 0), sway=tail("stagger", 6)),
                   q("lie", whole=(-2, 0), lift=4, sway=tail("lie", -6)), q("lie", whole=(-2, 0)),
                   q("lie", whole=(-2, 0), lift=1, sway=tail("lie", -4)), q("lie", whole=(-2, 0))]
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


EYE = (252, 218, 30)           # his yellow eyes: one square wide, two tall, ringed by the outline


def one_with_eyes(can, px, py, hw, hh, ppu, need=0.5):
    """ppu_rig.one_of, his eyes kept (league_vex's way): brought down to 1x by the commonest colour, the far eye (one
    square wide inside the outline) was outvoted and the 1x frames kept one eye. Every 1x square over an eye square
    takes the eye's colour."""
    one = _ONE_OF(can, px, py, hw, hh, ppu, need)
    eye = (can[..., 3] > 0) & (can[..., :3] == EYE).all(-1)
    for y, x in zip(*np.nonzero(eye)):
        j = int(np.floor((y + 0.5 - py) / ppu + 0.5)) + hh
        i = int(np.floor((x + 0.5 - px) / ppu + 0.5)) + hw
        if 0 <= j < one.shape[0] and 0 <= i < one.shape[1]:
            one[j, i] = (*EYE, 255)
    return one


_ONE_OF = R.one_of


def export(F, acts):
    """Rig.export with his eyes kept in the 1x frames (one_with_eyes)."""
    R.one_of = one_with_eyes
    try:
        F.rig.export(acts)
    finally:
        R.one_of = _ONE_OF


def strip_frames(path, sizes):
    a = np.asarray(Image.open(lp(path)).convert("RGBA")).copy()
    out, x = [], 0
    for w, h in sizes:
        out.append(a[:h, x:x + w].copy())
        x += w + 1
    return a, out


def restyled_eyes():
    """His two yellow eyes put back into the restyled frames (ppu_restyle brings the 1.5 frames down to 1.2 by the
    commonest colour of each square and the eyes, one square wide inside the outline, were outvoted - 「太高清了 降点像素」
    left some frames with one eye or none). Each restyled frame is laid over its 1.5 frame shrunk 1.2 / 1.5 about its
    middle, at the whole-square offset (within 3) where their silhouettes agree most; every restyled square over an eye
    square of the 1.5 frame takes the eye's colour. Run after ppu_restyle.py, before ppu_hd.py."""
    import json
    import ppu_restyle
    new_ppu = ppu_restyle.RESTYLE[HERO]["ppu"]
    k = new_ppu / PPU
    src = os.path.join(R.ROOT, "assets", "source", "ppu")
    fixed = 0
    for fn in sorted(os.listdir(lp(os.path.join(src, "orig")))):
        if not (fn.startswith(HERO + "_") and fn.endswith(".json")):
            continue
        tag = fn[len(HERO) + 1:-5]
        o_meta = json.load(open(lp(os.path.join(src, "orig", fn)), encoding="utf-8"))
        n_path = os.path.join(src, f"{HERO}_{tag}.json")
        if not os.path.isfile(lp(n_path)):
            continue
        n_meta = json.load(open(lp(n_path), encoding="utf-8"))
        _, olds = strip_frames(os.path.join(src, "orig", f"{HERO}_{tag}.png"), o_meta["sizes"])
        whole, news = strip_frames(os.path.join(src, f"{HERO}_{tag}.png"), n_meta["sizes"])
        x = 0
        for o, n in zip(olds, news):
            h, w = n.shape[:2]
            oy, ox = np.nonzero(o[..., 3] > 0)
            ty = np.floor((oy + 0.5 - o.shape[0] / 2) * k + h / 2).astype(int)
            tx = np.floor((ox + 0.5 - o.shape[1] / 2) * k + w / 2).astype(int)
            nop = n[..., 3] > 0
            best, bd = -1, (0, 0)
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    yy, xx = ty + dy, tx + dx
                    ok = (yy >= 0) & (yy < h) & (xx >= 0) & (xx < w)
                    sc = int(nop[yy[ok], xx[ok]].sum())
                    if sc > best:
                        best, bd = sc, (dy, dx)
            eye = (o[..., 3] > 0) & (o[..., :3] == EYE).all(-1)
            ey, ex = np.nonzero(eye)
            yy = np.floor((ey + 0.5 - o.shape[0] / 2) * k + h / 2).astype(int) + bd[0]
            xx = np.floor((ex + 0.5 - o.shape[1] / 2) * k + w / 2).astype(int) + bd[1]
            for y_, x_ in zip(yy, xx):
                if 0 <= y_ < h and 0 <= x_ < w and n[y_, x_, 3] > 0 and not (n[y_, x_, :3] == EYE).all():
                    whole[y_, x + x_] = (*EYE, 255)
                    fixed += 1
            x += w + 1
        Image.fromarray(whole).save(lp(os.path.join(src, f"{HERO}_{tag}.png")))
    print(f"{HERO}: {fixed} eye squares put back in the restyled frames")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    ap.add_argument("--eyes", action="store_true", help="after ppu_restyle.py: the eyes put back (restyled_eyes)")
    a = ap.parse_args()
    if a.eyes:
        restyled_eyes()
        return
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        D = design()
        tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
        print({k: int(v.sum()) for k, v in D.parts.items()}, "stand", D.px, "ground", D.ground)
        return
    F = form()
    acts = frames(F)
    if a.audit:
        import rig_wukong as RW
        RW.HERO = HERO
        RW.audit(F, acts, a.audit)
    elif a.review:
        F.rig.review(acts, a.review)
    else:
        export(F, acts)
        # the run is Codex's redraw now (tools/art/casts_warwick_run.py): the rig's own run kept as its frames' places
        import shutil
        import casts_warwick_run as CR
        for ext in (".png", ".json"):
            shutil.copyfile(CR.ORIG + ext, CR.RIG + ext)
        CR.write()


if __name__ == "__main__":
    main()

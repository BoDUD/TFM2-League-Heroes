#!/usr/bin/env python3
"""Elise's spiderling as a unit of its own: league/champions/league_elise_spiderling#sheet.png + #anim.fanim, drawn by
code at 1x and at PPU 2 (2026-11-14, the user: 「马尔扎哈和蜘蛛的召唤物画高清点啊 现在像什么 一个不像虫子 一个不像蜘蛛
模糊不清」 - its frames had been the Volatile Spiderling's 1x frames seen from above: a 9 px box with red dots).

    python -I tools/art/unit_elise_spiderling.py [--check] [--review <dir>]

The add-on league_elise spawns the passive's spiderlings in Spider Form through the mod API's spawn_unit under this name;
the game draws a unit of a name from asset/base/aseprite_resources/champions/<name> (the add-on's mod.override_info sends
that here) with the tags the engine's own summons (base `ghoul`) play: idle, run, attack, hit and dead. league.dll
registers the sheet (addons/league_main/src/hd.rs HEROES, PPU 2): each tag's hd_ twin is drawn on the battlefield, its
squares half a game pixel; without the DLL the 1x frames, the same size.

A small spider seen from the side, facing right, in Elise's spider colours (her sheet's c_* frames: the near-black
purple body, the teal-grey legs with red claws, the red markings and eyes): a round glossy abdomen with a red stripe
down its back and red spots, a smaller head with red eyes and fangs, and eight jointed legs - the near four arching up
over the body and down to red claws, the far four thinner and darker behind it, their feet higher up. 16 game px from
the hind claws to the front ones and 9 from the back to the soles (the old frames' 9 to 11 read as a speck): about a
third of her spider form's 53 (c_idle) - a spider at a glance on the battlefield, still small beside her. Everything is
shapes in game pixels (tools/art/unit_draw.py) sampled once a game pixel and twice (PPU 2: the dense frame exactly twice
the 1x frame, both centred on the pivot): the same drawing at both densities, hard edges, a dark outline. The body -
abdomen and head, 10 x 8 game px - is one picture moved by whole game pixels only, so it never grows or shrinks; each
leg is two bones of fixed lengths whose knee follows the foot.

  idle    4 frames: a front leg lifts and feels the air, the fangs part, the other front leg, the eyes glint - the body
          still (「上下摆动全不要了啊」);
  run     6 frames: the alternating gait (near legs 1 and 3 with far legs 2 and 4, then the other four), feet planted
          while they push, lifted on the way forward;
  attack  6 frames: back with the front legs up (0), reared (1), the bite - BITE_MS in, a red snap at the fangs -
          lunging two game px (2), held (3), back (4, 5); 400 ms;
  hit     2 frames: knocked back a game px and down, the eyes flaring, then back up;
  dead    7 frames: knocked back, the legs give way and splay flat (it drops a game px), a last twitch of a front leg
          as the eyes and the markings go dark, it lies still, an empty frame (as base's dead tags end).
The add-on's unit attack lands on the bite (league_elise src/lib.rs: SL_ACT 24 / SL_LANDS 8 ticks, checked by its
make_override.py against this sheet's .fanim: the attack's length and its first two frames).
--check: exit 1 when the sheet in the repo is not what this writes. --review: contact sheets of every frame (1x and dense
at 3x), the spiderling beside Elise at game scale.
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_draw as U  # noqa: E402

NAME = "league_elise_spiderling"
OUT_STEM = os.path.join(U.CHAMPIONS, NAME)
PPU = 2
ELISE_PPU = 1.8                         # league_main hd.rs: her HEROES row, no SIZES row (for the review only)

# colours: Elise's spider form's own (league_elise c_idle: the outline, the body's purples, the legs' teal greys, reds)
INK = (4, 2, 3)
BODY = [(27, 21, 38), (39, 27, 51), (51, 37, 70), (63, 46, 83), (89, 70, 125), (106, 88, 152), (150, 136, 190)]
LEG = [(25, 40, 47), (42, 50, 71), (61, 85, 94), (83, 101, 117), (120, 140, 156)]
RED = [(54, 3, 16), (96, 1, 23), (131, 1, 26), (175, 4, 35), (227, 2, 29), (250, 12, 40), (251, 68, 97),
       (255, 200, 210)]

# the body at rest (game px; it only ever moves by whole game px)
ABD = (-3.4, 5.0, 3.5, 3.0, 0.42)          # the abdomen's ellipse: centre, radii, turn (its back end up)
CEPH = (1.5, 8.0, 2.2, 1.7, -0.1)          # the head (cephalothorax)
EYES = (2.8, 7.4, 0.75, 0.5)
FANGS = [(3.0, 8.8), (3.7, 9.9), (3.3, 10.5)]
# legs at rest: (hip, knee, foot), front to back; the bones' lengths and the way each knee bends are read off these
NEAR_LEGS = [((2.8, 8.5), (5.6, 3.8), (7.8, 11.3)),
             ((2.2, 8.8), (3.9, 6.0), (5.4, 11.4)),
             ((1.2, 8.9), (-1.6, 7.0), (-2.5, 11.4)),
             ((0.4, 8.6), (-4.8, 7.2), (-6.4, 11.3))]
FAR_LEGS = [((2.6, 7.4), (4.6, 3.2), (6.8, 10.2)),
            ((2.0, 7.6), (3.0, 5.0), (4.2, 10.4)),
            ((1.2, 7.6), (-0.8, 4.8), (-3.8, 10.4)),
            ((0.4, 7.4), (-3.5, 3.0), (-7.2, 10.2))]

IDLE_MS = (300, 160, 300, 160)
RUN_MS = 65
ATTACK_MS = (70, 70, 70, 70, 60, 60)
BITE_MS = sum(ATTACK_MS[:2])
HIT_MS = (80, 100)
DEAD_MS = (90, 90, 100, 100, 120, 150, 60)


def bones(leg):
    """(femur, tibia, the way the knee bends) of a leg at rest"""
    (hx, hy), (kx, ky), (fx, fy) = leg
    l1, l2 = float(np.hypot(kx - hx, ky - hy)), float(np.hypot(fx - kx, fy - ky))
    mx, my = (hx + fx) / 2, (hy + fy) / 2
    return l1, l2, (kx - mx, ky - my)


class Pose:
    def __init__(self, body=(0, 0), near=None, far=None, fangs=0.0, eyes=0, mark=0, snap=0, fold=0.0):
        self.body = body                    # whole game px
        self.near = near or [f for _, _, f in NEAR_LEGS]
        self.far = far or [f for _, _, f in FAR_LEGS]
        self.fangs = fangs                  # how far the fangs part (game px)
        self.eyes = eyes                    # 0 red, 1 glinting, 2 white-hot, -1 dark
        self.mark = mark                    # the red markings: -1 dim, 0, 1 bright
        self.snap = snap                    # the bite's flash: 0 none, 1 full, 2 fading
        self.fold = fold                    # how far the feet have been drawn in toward the hips (0..1)


class Spiderling:
    def __init__(self, R):
        self.R = R
        self.bodies = {}

    def body(self, eyes, mark):
        """the body at rest (abdomen and head with their markings and eyes) - one picture for each light"""
        key = (eyes, mark)
        if key in self.bodies:
            return self.bodies[key]
        R = self.R
        B = U.Body(R)
        m, u, v = U.ellipse(R, *ABD)
        t = -v * 0.9 + u * 0.25 + 0.35 * (1 - np.clip(u * u + v * v, 0, 1))
        B.part(m, U.tones(U.band(t, (-0.25, 0.15, 0.5, 0.85)), BODY[0:5]))
        mc, uc, vc = U.ellipse(R, *CEPH)
        B.part(mc, U.tones(U.band(-vc * 0.9 + uc * 0.3, (-0.3, 0.2, 0.7)), BODY[1:5]))
        rgba = B.finish(INK, INK, width=1)
        inner = m & ~U.edge4(m)
        stripe = inner & (v > -0.92) & (v < -0.5) & (u > -0.75) & (u < 0.55)
        rgba[stripe, :3] = RED[4 + mark]
        rgba[stripe & (v < -0.72) & (u > -0.2), :3] = RED[6]
        for (cx, cy) in ((-2.6, 5.6), (-4.8, 4.6)):
            sp, _, _ = U.ellipse(R, cx, cy, 0.55, 0.5)
            rgba[sp & inner, :3] = RED[3 + mark]
        spec, _, _ = U.ellipse(R, -1.0, 5.2, 0.6, 0.4, 0.42)
        rgba[spec & inner, :3] = BODY[6]
        ex, ey, erx, ery = EYES
        eye_m, _, _ = U.ellipse(R, ex, ey, erx, ery)
        eye_m &= mc & ~U.edge4(mc)
        rgba[eye_m, :3] = {-1: RED[1], 0: RED[5], 1: RED[6], 2: RED[7]}[eyes]
        glint, _, _ = U.ellipse(R, ex + 0.35, ey - 0.15, 0.3, 0.25)
        if eyes >= 1:
            rgba[eye_m & glint, :3] = RED[7]
        self.bodies[key] = (rgba, m | mc)
        return self.bodies[key]

    def legs(self, canvas, pose, far):
        R = self.R
        bx, by = pose.body
        for leg, foot in zip(FAR_LEGS if far else NEAR_LEGS, pose.far if far else pose.near):
            l1, l2, toward = bones(leg)
            hip = (leg[0][0] + bx, leg[0][1] + by)
            if pose.fold:
                foot = (foot[0] + (hip[0] - foot[0]) * pose.fold, foot[1])
            knee = U.ik2(hip, foot, l1, l2, toward)
            if far:
                U.stroke(R, canvas, [hip, knee, foot], LEG[1], None, tip=RED[2], tip_len=1.0)
            else:
                U.stroke(R, canvas, [hip, knee, foot], LEG[3 if R.d > 1 else 1], INK, tip=RED[4], tip_len=1.2,
                         joint=LEG[4] if R.d > 1 else None)

    def fangs(self, canvas, pose, far):
        """a fang (the far one dense only, darker, a little behind): its tip raised and forward by `fangs`"""
        R = self.R
        if far and R.d == 1:
            return
        bx, by = pose.body
        o = pose.fangs
        dx, dy = (-0.6, -0.3) if far else (0.0, 0.0)
        pts = [(x + bx + dx + o * k / 2.0, y + by + dy - o * k / 4.0) for k, (x, y) in enumerate(FANGS)]
        U.stroke(R, canvas, pts, RED[1] if far else RED[3], INK if R.d > 1 else None)

    def snap(self, canvas, pose):
        if not pose.snap:
            return canvas
        R = self.R
        bx, by = pose.body
        cx, cy = 4.6 + bx, 9.8 + by
        lay = R.blank()
        r = 1.6 if pose.snap == 1 else 1.0
        star = U.capsule(R, (cx - r, cy), (cx + r, cy), 0.3) | U.capsule(R, (cx, cy - r), (cx, cy + r), 0.3)
        if pose.snap == 1:
            star |= U.capsule(R, (cx - r * 0.6, cy - r * 0.6), (cx + r * 0.6, cy + r * 0.6), 0.28)
            star |= U.capsule(R, (cx - r * 0.6, cy + r * 0.6), (cx + r * 0.6, cy - r * 0.6), 0.28)
        core, _, _ = U.ellipse(R, cx, cy, 0.55, 0.55)
        lay[star, :3] = RED[5] if pose.snap == 1 else RED[3]
        lay[star, 3] = 255
        lay[star & core, :3] = RED[7] if pose.snap == 1 else RED[6]
        return U.over(canvas, lay)

    def frame(self, pose):
        """-> (the frame, the body's picture where this frame put it, the body's squares there)"""
        R = self.R
        d = R.d
        c = R.blank()
        self.legs(c, pose, far=True)
        self.fangs(c, pose, far=True)
        rgba, body = self.body(pose.eyes, pose.mark)
        bx, by = pose.body
        layer = U.shift(rgba, by * d, bx * d)
        c = U.over(c, layer)
        self.fangs(c, pose, far=False)
        self.legs(c, pose, far=False)
        c = self.snap(c, pose)
        c[R.Y > U.GROUND] = 0
        mask = U.shift(body[..., None].astype(np.uint8), by * d, bx * d)[..., 0] > 0
        return c, layer, mask


def gait(phase, rest, stride, lift):
    """a foot at `phase` (0..1) of its step: on the ground pushing back over the first half, lifted forward over the
    second"""
    x0, y0 = rest
    if phase < 0.5:
        return (x0 + stride / 2 - stride * phase / 0.5, y0)
    p = (phase - 0.5) / 0.5
    return (x0 - stride / 2 + stride * p, y0 - lift * np.sin(np.pi * p))


def poses():
    near = [f for _, _, f in NEAR_LEGS]
    far = [f for _, _, f in FAR_LEGS]

    def moved(feet, k, dx, dy):
        out = list(feet)
        out[k] = (feet[k][0] + dx, feet[k][1] + dy)
        return out

    tags = {}
    tags["idle"] = [Pose(), Pose(near=moved(near, 0, 0.6, -1.6), fangs=0.4), Pose(fangs=0.0),
                    Pose(far=moved(far, 0, 0.6, -1.4), eyes=1, mark=1)]
    run = []
    for k in range(6):
        ph = k / 6.0
        a = [0.0, 0.5, 0.0, 0.5]           # near 1 and 3 with far 2 and 4
        run.append(Pose(near=[gait((ph + a[i]) % 1.0, near[i], 2.6, 1.4) for i in range(4)],
                        far=[gait((ph + 0.5 - a[i]) % 1.0, far[i], 2.6, 1.4) for i in range(4)]))
    tags["run"] = run
    up_n = moved(moved(near, 0, -0.8, -3.2), 1, -0.4, -1.4)
    up_f = moved(moved(far, 0, -0.8, -3.0), 1, -0.4, -1.2)
    high_n = moved(moved(near, 0, -1.6, -5.0), 1, -0.6, -2.6)
    high_f = moved(moved(far, 0, -1.4, -4.6), 1, -0.6, -2.2)
    strike_n = moved(moved(near, 0, 2.4, -0.6), 1, 1.6, 0.0)
    strike_f = moved(moved(far, 0, 2.2, -0.4), 1, 1.4, 0.0)
    tags["attack"] = [Pose(body=(-1, 0), near=up_n, far=up_f, fangs=0.6),
                      Pose(body=(-1, -1), near=high_n, far=high_f, fangs=0.9, eyes=1, mark=1),
                      Pose(body=(2, 0), near=strike_n, far=strike_f, fangs=0.0, eyes=1, mark=1, snap=1),
                      Pose(body=(2, 0), near=strike_n, far=strike_f, fangs=0.0, snap=2),
                      Pose(body=(1, 0), near=moved(near, 0, 1.0, 0.0), far=moved(far, 0, 1.0, 0.0)),
                      Pose()]
    splay_n = [(x + (1.6 if x > 0 else -1.6), y) for x, y in near]
    splay_f = [(x + (1.6 if x > 0 else -1.6), y) for x, y in far]
    tags["hit"] = [Pose(body=(-1, 1), fangs=0.8, eyes=2, mark=1), Pose(body=(-1, 0), fangs=0.3)]
    flat_n = [(x + (2.6 if x > 0 else -2.6), y) for x, y in near]
    flat_f = [(x + (2.6 if x > 0 else -2.6), y) for x, y in far]
    twitch_n = moved(flat_n, 0, -0.6, -1.2)
    tags["dead"] = [Pose(body=(-1, 1), fangs=0.8, eyes=2, mark=1),
                    Pose(body=(-1, 1), near=splay_n, far=splay_f, fangs=1.0, eyes=2),
                    Pose(body=(-1, 1), near=flat_n, far=flat_f, fangs=0.6, eyes=0),
                    Pose(body=(-1, 1), near=twitch_n, far=flat_f, fangs=0.3, eyes=-1),
                    Pose(body=(-1, 1), near=flat_n, far=flat_f, eyes=-1, mark=-1),
                    Pose(body=(-1, 1), near=flat_n, far=flat_f, eyes=-1, mark=-1, fold=0.15),
                    None]
    return tags


def build():
    timing = {"idle": IDLE_MS, "run": (RUN_MS,) * 6, "attack": ATTACK_MS, "hit": HIT_MS, "dead": DEAD_MS}
    return U.build_unit(Spiderling, poses(), timing, PPU)


def review(tags, rigid, folder):
    """the contact sheet (the body's top and bottom as yellow lines), the body's size in every frame, and the spiderling
    beside Elise (her spider form and her human form) at game scale"""
    os.makedirs(folder, exist_ok=True)
    print("review", U.contact(tags, PPU, os.path.join(folder, "spiderling_frames.png"), U.rigid_lines(rigid)))
    text, one = U.rigid_text(rigid, NAME)
    print(text)
    if not one:
        sys.exit("the body is not one size in every frame")
    elise = os.path.join(U.CHAMPIONS, "league_elise")
    figs = [("Elise 1x", U.sheet_frames(elise, "c_idle")[0][0], 1.0),
            ("spiderling 1x", tags["idle"][0][0], 1.0),
            ("Elise hd", U.sheet_frames(elise, "hd_c_idle")[0][0], 1.0 / ELISE_PPU),
            ("spiderling hd", tags["hd_idle"][0][0], 1.0 / PPU),
            ("attack", tags["hd_attack"][2][0], 1.0 / PPU),
            ("run", tags["hd_run"][1][0], 1.0 / PPU),
            ("human", U.sheet_frames(elise, "hd_idle")[0][0], 1.0 / ELISE_PPU)]
    print("review", U.beside(figs, os.path.join(folder, "spiderling_beside_elise.png"), scale=3))
    print("review", U.beside(figs, os.path.join(folder, "spiderling_beside_elise_6x.png"), scale=6))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    tags, rigid = build()
    if a.review:
        review(tags, rigid, a.review)
    U.write_unit(NAME, OUT_STEM, tags, a.check)


if __name__ == "__main__":
    main()

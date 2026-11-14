#!/usr/bin/env python3
"""Malzahar's voidling as a unit of its own: league/champions/league_malzahar_voidling#sheet.png + #anim.fanim, drawn by
code at 1x and at PPU 2 (2026-11-14, the user: 「马尔扎哈和蜘蛛的召唤物画高清点啊 现在像什么 一个不像虫子 一个不像蜘蛛
模糊不清」 - its frames had been cut from the swarm effect's 1x frames: a hunched purple blob).

    python -I tools/art/unit_malzahar_voidling.py [--check] [--review <dir>]

The add-on league_malzahar spawns the voidlings of Void Swarm (his E's) through the mod API's spawn_unit under this name;
the game draws a unit of a name from asset/base/aseprite_resources/champions/<name> (the add-on's mod.override_info sends
that here) with the tags the engine's own summons (base `ghoul`) play: idle, run, attack, hit and dead. league.dll
registers the sheet (addons/league_main/src/hd.rs HEROES, PPU 2): each tag's hd_ twin is drawn on the battlefield, its
squares half a game pixel; without the DLL the 1x frames, the same size.

A void bug seen from the side, facing right, 22 game px from the tail spike to the pincers and 14 from the spikes to the
soles (the 23 px the swarm has had on screen): a domed shell of four violet plates with void light glowing magenta
between them and a spike on three of them, a dark underbody, a head with a lavender plate, a glowing magenta eye and
mouth, two pincers and two elbowed feelers, and six jointed legs (the far three darker and higher up). Everything is
shapes in game pixels (tools/art/unit_draw.py) sampled once a game pixel and twice (PPU 2: the dense frame exactly
twice the 1x frame, both centred on the pivot): the same drawing at both densities, hard edges, a dark outline. The body
- shell (14 x 7 game px), head, underbody, spikes - is one picture moved by whole game pixels only, so it never grows or
shrinks; legs are two bones of fixed lengths whose knees follow the feet.

  idle    4 frames: the pincers part, the feelers twitch, a front leg taps, the void light pulses - the body still
          (「上下摆动全不要了啊」);
  run     6 frames: the tripod gait (near front + near hind + far middle, then the other three), feet planted while they
          push, lifted on the way forward;
  attack  6 frames: back and pincers wide (0), up on its legs (1), the bite - BITE_MS in, a magenta snap at the
          pincers - lunging two game px (2), held (3), back (4, 5); 400 ms;
  hit     2 frames: knocked back a game px and down, the eye flaring, then back up;
  dead    8 frames: knocked back, the legs give way and it drops onto its belly, a void rift opens under it and it sinks
          in, the rift closes, an empty frame (as base's dead tags end).
The add-on's unit attack lands on the bite (league_malzahar src/lib.rs: VOID_ACT 24 / VOID_LANDS 11 ticks, checked by its
make_override.py against this sheet's .fanim: the attack's length and its first two frames).
--check: exit 1 when the sheet in the repo is not what this writes. --review: contact sheets of every frame (1x and dense
at 3x), the voidling beside Malzahar at game scale.
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_draw as U  # noqa: E402

NAME = "league_malzahar_voidling"
OUT_STEM = os.path.join(U.CHAMPIONS, NAME)
PPU = 2
MALZ_PPU, MALZ_SIZE = 1.38, 1.15        # league_main hd.rs: his HEROES and SIZES rows (for the review only)

# colours: the swarm effect's own (league_malzahar_fx w_swarm: outline, purples, the lavender plates, the magenta glow),
# the plates tinted toward Malzahar's void violet
INK = (16, 4, 34)
PUR = [(28, 8, 56), (46, 15, 82), (74, 28, 122), (106, 48, 164), (140, 80, 200)]
PLATE = [(66, 40, 98), (106, 74, 148), (150, 116, 190), (196, 168, 228), (238, 226, 252)]
GLOW = [(110, 11, 75), (180, 24, 122), (238, 58, 166), (255, 140, 216), (255, 224, 246)]
RIFT = [(10, 2, 22), (40, 10, 74), (96, 34, 170), (150, 84, 226), (214, 176, 255), (250, 240, 255)]
RIFT_Y = 10.6                               # the rift's middle on the ground (game px under the pivot)

# the body at rest (game px; it only ever moves by whole game px)
SHELL = (-3.8, 5.4, 7.0, 5.8, 0.06)        # its ellipse: centre, radii, turn; cut under the rim
SEAMS = (-0.52, -0.1, 0.32)                 # where the plates meet, along the shell
HEAD = (3.9, 5.9, 2.8, 2.5, 0.1)
BELLY = (-3.0, 6.9, 6.0, 1.7)
SPIKES = ([(-9.2, 2.2), (-11.2, -0.2), (-8.0, 1.0)], [(-6.0, 0.4), (-7.4, -2.4), (-4.6, -0.1)],
          [(-2.6, -0.2), (-3.4, -2.8), (-1.2, -0.2)])
EYE = (5.1, 5.5, 1.1, 0.9)
MOUTH = (6.2, 7.2, 0.8, 0.6)

# legs: (hip on the body at rest, foot at rest, femur, tibia, the way the knee bends), front to back
NEAR_LEGS = [((0.8, 7.4), (6.8, 11.3), 3.8, 4.2, (1, -1)),
             ((-2.6, 7.8), (-1.0, 11.4), 2.6, 3.0, (0.4, -1)),
             ((-6.2, 7.4), (-10.2, 11.3), 3.6, 4.2, (-1, -1))]
FAR_LEGS = [((0.6, 6.6), (5.0, 10.3), 3.8, 4.2, (1, -1)),
            ((-3.0, 6.8), (-2.0, 10.4), 2.6, 3.0, (0.4, -1)),
            ((-6.6, 6.6), (-10.6, 10.3), 3.6, 4.2, (-1, -1))]
# pincers and feelers (far, near): polylines from the head out; a pose parts the pincers' tips and moves the feelers'
FAR_PINCER = [(6.0, 6.2), (7.6, 5.6), (9.0, 6.1), (9.4, 7.0)]
NEAR_PINCER = [(6.2, 7.8), (7.8, 8.4), (9.4, 8.0), (10.0, 7.1)]
FAR_FEELER = [(3.6, 4.0), (4.4, 1.4), (7.0, 0.0)]
NEAR_FEELER = [(4.6, 4.0), (5.8, 1.8), (8.6, 0.8)]

IDLE_MS = (260, 180, 260, 180)
RUN_MS = 75
ATTACK_MS = (90, 90, 70, 60, 50, 40)
BITE_MS = sum(ATTACK_MS[:2])
HIT_MS = (80, 100)
DEAD_MS = (90, 100, 90, 90, 90, 80, 70, 60)


def rim_y(x):
    return 6.7 - 0.03 * (x + 3.8) ** 2


class Pose:
    def __init__(self, body=(0, 0), near=None, far=None, pincer=0.0, feeler=(0.0, 0.0), glow=0, eye=0,
                 snap=0, rift=None, sink=0):
        self.body = body                    # whole game px
        self.near = near or [f for _, f, *_ in NEAR_LEGS]
        self.far = far or [f for _, f, *_ in FAR_LEGS]
        self.pincer = pincer                # the tips part by this much (negative: crossed shut)
        self.feeler = feeler                # the feelers' tips moved by this
        self.glow, self.eye = glow, eye     # the void light: -1 dim, 0, 1 bright; the eye 2: white-hot
        self.snap = snap                    # the bite's flash: 0 none, 1 full, 2 fading
        self.rift = rift                    # (half width, half depth) of the void rift under it, or None
        self.sink = sink                    # game px sunk into the rift


def tapered(R, pts, r0, r1):
    """the squares of a limb along the polyline `pts`, its radius going from r0 to r1"""
    n = len(pts) - 1
    m = R.none()
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        m |= U.capsule(R, p, q, r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n)
    return m


class Voidling:
    def __init__(self, R):
        self.R = R
        self.bodies = {}

    def body(self, glow, eye):
        """the body at rest (shell, spikes, underbody, head, eye) - one picture for each light"""
        key = (glow, eye)
        if key in self.bodies:
            return self.bodies[key]
        R = self.R
        B = U.Body(R)
        for pts in SPIKES:
            B.part(U.polygon(R, pts), PLATE[3])
        mu, _, vu = U.ellipse(R, *BELLY)
        B.part(mu, U.tones(U.band(-vu, (-0.2, 0.5)), PUR[0:3]))
        m, u, v = U.ellipse(R, *SHELL)
        m &= R.Y < rim_y(R.X)
        B.part(m, U.tones(U.band(-v + 0.25 * u, (-0.15, 0.3, 0.8, 1.15)), PLATE))
        mh, uh, vh = U.ellipse(R, *HEAD)
        th = -vh * 0.8 + uh * 0.5
        helmet = vh < -0.1
        B.part(mh, np.where(helmet[..., None], U.tones(U.band(th, (0.2, 0.7)) + 1, PLATE),
                            U.tones(U.band(th, (-0.3, 0.2, 0.7)), PUR[1:])))
        rgba = B.finish(INK, INK, width=1)
        inner = m & ~U.edge4(m) & ~mh
        sq = 1.0 / R.d
        uu = u + 0.3 * v * v
        seam_glow = GLOW[2 + glow]
        for s in SEAMS:
            dd = (uu - s) * SHELL[2]
            line = inner & (dd >= -sq / 2) & (dd < sq / 2)
            if R.d == 1:
                rgba[line & (v > 0.0), :3] = GLOW[1 + max(glow, 0)]
                rgba[line & (v <= 0.0), :3] = INK
            else:
                rgba[line, :3] = INK
                rgba[inner & (dd < -sq / 2) & (dd >= -sq * 1.5) & (v > -0.35), :3] = seam_glow
        ex, ey, erx, ery = EYE
        eye_m, _, _ = U.ellipse(R, ex, ey, erx, ery)
        hot, _, _ = U.ellipse(R, ex + 0.2, ey - 0.2, 0.45, 0.4)
        rgba[eye_m, :3] = GLOW[4] if eye == 2 else GLOW[3 + min(glow, 0)]
        rgba[eye_m & hot, :3] = GLOW[4]
        mouth, _, _ = U.ellipse(R, *MOUTH)
        rgba[mouth & mh & ~U.edge4(mh), :3] = GLOW[2 + glow]
        self.bodies[key] = (rgba, m)
        return self.bodies[key]

    def legs(self, canvas, pose, far):
        R = self.R
        bx, by = pose.body
        legs, feet = (FAR_LEGS, pose.far) if far else (NEAR_LEGS, pose.near)
        core = PUR[2] if far else PUR[4 if R.d > 1 else 3]
        joint = (PUR[3] if far else PLATE[3]) if R.d > 1 else None
        tip = PLATE[1] if far else PLATE[3]
        for (hip, _, l1, l2, toward), foot in zip(legs, feet):
            h = (hip[0] + bx, hip[1] + by)
            k = U.ik2(h, foot, l1, l2, toward)
            U.stroke(R, canvas, [h, k, foot], core, INK, tip=tip, tip_len=0.8, joint=joint)

    def pincer(self, canvas, pose, far):
        R = self.R
        bx, by = pose.body
        o = pose.pincer
        if far:
            pts = [(x, y - o * k / 3.0) for k, (x, y) in enumerate(FAR_PINCER)]
            col = PLATE[2]
        else:
            pts = [(x, y + o * k / 3.0) for k, (x, y) in enumerate(NEAR_PINCER)]
            col = PLATE[4]
        pts = [(x + bx, y + by) for x, y in pts]
        lay = R.blank()
        if R.d == 1:
            U.stroke(R, lay, pts, col)
        else:
            m = tapered(R, pts, 0.85, 0.4)
            lay[m, :3] = col
            lay[m, 3] = 255
            lay[U.edge4(m), :3] = INK
        return U.over(canvas, lay)

    def feeler(self, canvas, pose, far):
        bx, by = pose.body
        fx, fy = pose.feeler
        pts = FAR_FEELER if far else NEAR_FEELER
        pts = [(x + bx + fx * k / 2.0, y + by + fy * k / 2.0) for k, (x, y) in enumerate(pts)]
        if far:
            U.stroke(self.R, canvas, pts, PUR[2], None, tip=GLOW[1], tip_len=0.8)
        else:
            U.stroke(self.R, canvas, pts, PUR[4], None, tip=GLOW[3], tip_len=0.8)

    def snap(self, canvas, pose):
        """the bite's flash between the pincer tips: a magenta star (1: full, 2: fading)"""
        if not pose.snap:
            return canvas
        R = self.R
        bx, by = pose.body
        cx, cy = 10.4 + bx, 7.4 + by
        lay = R.blank()
        r = 1.8 if pose.snap == 1 else 1.2
        star = (U.capsule(R, (cx - r, cy), (cx + r, cy), 0.35) | U.capsule(R, (cx, cy - r), (cx, cy + r), 0.35))
        if pose.snap == 1:
            star |= U.capsule(R, (cx - r * 0.6, cy - r * 0.6), (cx + r * 0.6, cy + r * 0.6), 0.3)
            star |= U.capsule(R, (cx - r * 0.6, cy + r * 0.6), (cx + r * 0.6, cy - r * 0.6), 0.3)
        core, _, _ = U.ellipse(R, cx, cy, 0.6, 0.6)
        lay[star, :3] = GLOW[3] if pose.snap == 1 else GLOW[2]
        lay[star, 3] = 255
        lay[star & core, :3] = GLOW[4] if pose.snap == 1 else GLOW[3]
        return U.over(canvas, lay)

    def rift(self, pose):
        """(back, lip): the rift's hole and far rim, drawn under the body; its near rim, drawn over it"""
        R = self.R
        hw, hd = pose.rift
        cx, cy = -1.0, RIFT_Y
        hole, u, v = U.ellipse(R, cx, cy, hw, hd)
        back, lip = R.blank(), R.blank()
        if not hole.any():
            return back, lip
        edge = U.edge4(hole)
        back[hole, :3] = U.tones(U.band(-v, (-0.3, 0.5)), RIFT[0:3])[hole]
        back[hole, 3] = 255
        back[edge & (v < 0), :3] = RIFT[3]
        swirl = hole & ~edge & (np.abs(v + 0.1 * np.sin(u * 7.0)) < 0.18) & (np.abs(u) < 0.7)
        back[swirl, :3] = RIFT[2]
        near = edge & (v >= 0)
        lip[near, :3] = RIFT[4]
        lip[near, 3] = 255
        lip[near & (np.abs(u) < 0.45), :3] = RIFT[5]
        return back, lip

    def frame(self, pose):
        """-> (the frame, the shell's picture where this frame put it, the shell's squares there)"""
        R = self.R
        d = R.d
        c = R.blank()
        lip = None
        if pose.rift is not None:
            back, lip = self.rift(pose)
            c = U.over(c, back)
        figure = R.blank()
        self.legs(figure, pose, far=True)
        self.feeler(figure, pose, far=True)
        figure = self.pincer(figure, pose, far=True)
        rgba, shell = self.body(pose.glow, pose.eye)
        bx, by = pose.body
        dr, dc = (by + pose.sink) * d, bx * d
        figure = U.over(figure, U.shift(rgba, by * d, dc))
        self.legs(figure, pose, far=False)
        figure = self.pincer(figure, pose, far=False)
        self.feeler(figure, pose, far=False)
        figure = self.snap(figure, pose)
        if pose.sink:
            figure = U.shift(figure, pose.sink * d, 0)
            figure[R.Y > RIFT_Y + 0.3] = 0
        c = U.over(c, figure)
        if lip is not None:
            c = U.over(c, lip)
        c[R.Y > U.GROUND] = 0
        mask = U.shift(shell[..., None].astype(np.uint8), dr, dc)[..., 0] > 0
        return c, U.shift(rgba, dr, dc), mask


def gait(phase, rest, stride, lift, ground):
    """a foot at `phase` (0..1) of its step: on the ground pushing back over the first half, lifted forward over the
    second"""
    x0, _ = rest
    if phase < 0.5:
        return (x0 + stride / 2 - stride * phase / 0.5, ground)
    p = (phase - 0.5) / 0.5
    return (x0 - stride / 2 + stride * p, ground - lift * np.sin(np.pi * p))


def poses():
    near_rest = [f for _, f, *_ in NEAR_LEGS]
    far_rest = [f for _, f, *_ in FAR_LEGS]
    tags = {}
    # idle: nothing but the pincers, feelers, a front leg and the light
    tap = list(near_rest)
    tap[0] = (near_rest[0][0] + 0.6, near_rest[0][1] - 1.8)
    tags["idle"] = [Pose(), Pose(pincer=1.0, feeler=(1.0, -0.8), glow=1), Pose(feeler=(-0.6, 0.5)),
                    Pose(near=tap, glow=-1)]
    # run: the tripod gait - near front, near hind and far middle together, the other three half a step later
    run = []
    for k in range(6):
        ph = k / 6.0
        near = [gait((ph + (0.0 if i != 1 else 0.5)) % 1.0, near_rest[i], 3.0, 1.6, near_rest[i][1]) for i in range(3)]
        far = [gait((ph + (0.5 if i != 1 else 0.0)) % 1.0, far_rest[i], 3.0, 1.6, far_rest[i][1]) for i in range(3)]
        run.append(Pose(near=near, far=far, feeler=(0.0, 0.4 if k % 3 == 0 else 0.0)))
    tags["run"] = run
    # attack: back with the pincers wide, up, the bite two game px forward, held, back
    tags["attack"] = [Pose(body=(-1, 0), pincer=1.4, feeler=(-0.6, 0.3)),
                      Pose(body=(-1, -1), pincer=1.8, feeler=(-0.8, 0.0), glow=1),
                      Pose(body=(2, 0), pincer=-0.4, feeler=(0.8, 0.4), glow=1, snap=1),
                      Pose(body=(2, 0), pincer=-0.4, feeler=(0.6, 0.2), snap=2),
                      Pose(body=(1, 0), pincer=0.4),
                      Pose(pincer=0.2)]
    # hit: knocked back and down, the eye flaring; back up
    tags["hit"] = [Pose(body=(-1, 1), pincer=1.0, feeler=(-0.8, 0.6), eye=2, glow=1),
                   Pose(body=(-1, 0), pincer=0.4, feeler=(-0.4, 0.2))]
    # dead: knocked back, the legs give way, a rift opens and it sinks in, the rift closes
    splay_n = [(x + (1.5 if x > -2 else -1.5), y) for x, y in near_rest]
    splay_f = [(x + (1.5 if x > -2 else -1.5), y) for x, y in far_rest]
    flat_n = [(x + (2.5 if x > -2 else -2.5), y) for x, y in near_rest]
    flat_f = [(x + (2.5 if x > -2 else -2.5), y) for x, y in far_rest]
    tags["dead"] = [Pose(body=(-1, 1), pincer=1.0, feeler=(-0.8, 0.6), eye=2, glow=1),
                    Pose(body=(-1, 2), near=splay_n, far=splay_f, pincer=1.6, feeler=(-1.0, 1.0), eye=2, glow=1),
                    Pose(body=(-1, 3), near=flat_n, far=flat_f, pincer=0.8, feeler=(-1.2, 1.4), rift=(6.0, 1.2)),
                    Pose(body=(-1, 3), near=flat_n, far=flat_f, pincer=0.6, feeler=(-1.2, 1.4), glow=-1, rift=(10.0, 2.0),
                         sink=2),
                    Pose(body=(-1, 3), near=flat_n, far=flat_f, pincer=0.6, feeler=(-1.2, 1.4), glow=-1, rift=(11.0, 2.2),
                         sink=5),
                    Pose(body=(-1, 3), near=flat_n, far=flat_f, glow=-1, rift=(10.0, 2.0), sink=9),
                    Pose(body=(-1, 3), glow=-1, rift=(6.0, 1.2), sink=16),
                    None]
    return tags


def build():
    timing = {"idle": IDLE_MS, "run": (RUN_MS,) * 6, "attack": ATTACK_MS, "hit": HIT_MS, "dead": DEAD_MS}
    return U.build_unit(Voidling, poses(), timing, PPU)


def review(tags, rigid, folder):
    """the contact sheet (the shell's top and bottom as yellow lines), the shell's size in every frame, and the voidling
    beside Malzahar at game scale (his frames at his PPU and his 115 %)"""
    os.makedirs(folder, exist_ok=True)
    print("review", U.contact(tags, PPU, os.path.join(folder, "voidling_frames.png"), U.rigid_lines(rigid)))
    text, one = U.rigid_text(rigid, NAME)
    print(text)
    if not one:
        sys.exit("the shell is not one size in every frame")
    malz = os.path.join(U.CHAMPIONS, "league_malzahar")
    figs = [("Malzahar 1x", U.sheet_frames(malz, "idle")[0][0], MALZ_SIZE),
            ("voidling 1x", tags["idle"][0][0], 1.0),
            ("Malzahar hd", U.sheet_frames(malz, "hd_idle")[0][0], MALZ_SIZE / MALZ_PPU),
            ("voidling hd", tags["hd_idle"][0][0], 1.0 / PPU),
            ("attack", tags["hd_attack"][2][0], 1.0 / PPU),
            ("run", tags["hd_run"][1][0], 1.0 / PPU)]
    print("review", U.beside(figs, os.path.join(folder, "voidling_beside_malzahar.png"), scale=3))
    print("review", U.beside(figs, os.path.join(folder, "voidling_beside_malzahar_6x.png"), scale=6))


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

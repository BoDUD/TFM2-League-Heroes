#!/usr/bin/env python3
"""Preview images for Camille, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_camille.py [--out docs/preview]

  league_camille_frames.png     every animation, frame by frame, 3x on the arena colour
  league_camille_effects.png    every effect animation, 3x
  league_camille_showcase.gif   a scripted fight against Garen and Darius, timed like the kit: she runs in and kicks
                                Garen - Adaptive Defenses wraps her in its hex shield; Precision Protocol's first
                                kick (the cyan star), a plain kick while it charges, the charged second kick (the
                                true-damage burst); Tactical Sweep's crescent catches Garen on its outer edge and he
                                falls. Darius walks up behind a red caster minion (a prop drawn here); Hookshot's
                                claw catches the minion beside him (she never hooks a champion), she is pulled to it
                                and dashes on at Darius - the shock ring, Darius stunned under the hex stars. The Hextech
                                Ultimatum: a short leap, the arena rises where she lands and stays there, the mark at
                                his feet; her kicks add true damage, he walks to the field's edge, hits the wall and
                                is dragged back, and falls; 3x
"""
import argparse
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import Held, OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_camille")
FX = os.path.join(LEAGUE, "effects", "league_camille_fx")
BIG = os.path.join(LEAGUE, "effects", "league_camille_big")
KICK = 64                                             # the attack's cooldown, ticks
KICK_E = 50                                           # with Hookshot's 30% attack speed
FIELD_R = 36                                          # R's field: 36000 round the point she landed on
# a red caster minion facing left - a prop for the showcase only (the base game's minion art is not ours to show)
MINION = ["...ooooo...",
          "..olllllo..",
          ".olrrrrrlo.",
          ".orRRRRRro.",
          ".oyRyRRRro.",
          ".orRRRRRro.",
          "..orrrrro..",
          "..odddddo..",
          ".olrrrrrlo.",
          "olrrrrrrrlo",
          "orrrrrrrrro",
          "orrrrrrrrro",
          ".ooo...ooo."]
MINION_COL = {"o": (42, 10, 20), "l": (252, 45, 63), "r": (179, 17, 45), "R": (106, 10, 30), "y": (243, 191, 39),
              "d": (62, 52, 80)}


class Fleer(Held):
    """A foe that can also walk in (mirrored run frames, from the right) and walk off to the right (unmirrored)."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.flees = []                               # (t0, t1, dx): walking off to the right
        self.walks_in = []                            # (t0, t1, dx): walking left toward the fight

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx in self.flees + self.walks_in:
            if t >= t0:
                x += int(round(dx * min(1.0, (t - t0) / (t1 - t0))))
        return x, y

    def frame(self, t):
        if self.death is not None and t >= self.death:
            return super().frame(t)
        for t0, t1, _ in self.flees:
            if t0 <= t < t1:
                return self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
        for t0, t1, _ in self.walks_in:
            if t0 <= t < t1:
                return self.flip(self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run)))
        return super().frame(t)


def turned(frames, angle):
    """A projectile's frames turned to its flight (degrees, counter-clockwise on screen)."""
    if abs(angle) < 0.5:
        return frames
    return [(f.rotate(angle, resample=Image.NEAREST, expand=True), ms) for f, ms in frames]


class Prop:
    """A unit that only stands (the minion): its picture centred on its pivot, the soles 11 px under it."""

    def __init__(self, x, y):
        h, w = len(MINION), len(MINION[0])
        img = Image.new("RGBA", (w, 23), (0, 0, 0, 0))
        for r, row in enumerate(MINION):
            for c, ch in enumerate(row):
                if ch != ".":
                    img.putpixel((c, 23 - h + r), MINION_COL[ch] + (255,))
        self.img, self.x, self.y = img, x, y

    def pos(self, t):
        return self.x, self.y

    def frame(self, t):
        return self.img


class FieldView:
    """R's field as the contact sheet shows it: turned back upright, the forming and one standing loop (14 frames)."""

    def __init__(self, sp):
        fr = frames_of(sp, "r_field")[:14]
        self.frames = [f.transpose(Image.ROTATE_180) for f, _ in fr]
        self.durations = [ms for _, ms in fr]
        self.h = sp.h

    def tag_frames(self, tag):
        return list(range(len(self.frames)))


def showcase(out, z=3, step=40):
    cam = load(CHAMP)
    fx, big = load(FX), load(BIG)
    W, H = 300, 130
    gy = 92                                            # her pivot row: the crown stands 34 px over it
    back = gy - 12                                     # the back row, where Darius comes in
    g = Fleer(load(os.path.join(LEAGUE, "champions", "league_garen")), 102, gy)
    d = Fleer(load(os.path.join(LEAGUE, "champions", "league_darius")), 340, back)
    body, under, over, props = [], [], [], []
    t = 0.0
    spot = {"x": 70, "y": gy}

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(cam, tag), t, at if at is not None else spot["x"], spot["y"], loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        return an

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def on(sp, tag, at, foe, z=2):
        an = OnFoe(frames_of(sp, tag), at, foe, z=z)
        (under if z < 0 else over).append(an)
        return an

    def kick(foe, tag="attack", hit_tick=8, ticks=None, view="hit", gap=KICK, extra=None):
        """A kick: its strip, the hit on hit_tick, idle until the next attack."""
        start = t
        hit = start + tick(hit_tick)
        on(fx, view, hit, foe)
        foe.flinches.append(hit)
        if extra:
            on(fx, extra, hit + tick(1), foe)
        a(tag, tick(ticks) if ticks else None)
        idle_to(start + tick(gap))
        return hit

    # she runs in (move speed 1040: 62 px a second) to 32 px from Garen
    a("run", 900, loop=True, at=14, to=70)
    first = kick(g)
    # Adaptive Defenses: the shield (and its picture) for 120 ticks on the first champion hit
    over.append(Follow(frames_of(fx, "p_shield"), first, 0, 0, loop=True, until=first + tick(120), on=body))
    # Precision Protocol: Q1 (25 ticks, the hit on 8), a plain kick while Q2 charges 90 ticks, the charged Q2 (27, on 9)
    kick(g, "attack_q", 8, 25, "q_hit")
    kick(g)
    kick(g, "attack_q2", 9, 27, "q2_hit")
    # Darius walks up behind, to the back row 58 px ahead of her
    d.walks_in.append((2600, 5600, 128 - d.x))
    # Tactical Sweep: the sweep on tick 22 - the crescent (a line's picture, centred 30 px ahead) and the outer edge
    w0 = t
    sweep = w0 + tick(22)
    over.append(Anim(frames_of(fx, "w_arc"), sweep, spot["x"] + 30, gy))
    on(fx, "w_edge", sweep, g)
    g.flinches.append(sweep)
    g.death = sweep + 120
    a("skill", tick(40))
    # Hookshot: the throw plays when a pulse finds a hold near a champion - the minion beside Darius (never a champion);
    # the claw leaves on tick 9 (5 px over her pivot) at 6 px a tick, then the pull at 3.5 px a tick to it; E2: a dash
    # at Darius (4.5 px a tick) - the landing ring, the hit round her, his stun
    mn = Prop(126, gy + 9)                            # a front-row minion, right of the fallen Garen
    props.append(mn)
    e0 = t
    rel = e0 + tick(9)
    sx, sy = spot["x"], gy - 5
    tx, ty = mn.pos(rel)
    arrive = rel + tick(math.hypot(tx - sx, ty - sy) / 6.0)
    over.append(Anim(turned(frames_of(fx, "e_hook"), math.degrees(math.atan2(sy - ty, tx - sx))), rel, sx, sy,
                     until=arrive, x1=tx, y1=ty))
    a("skill2", arrive + tick(1) - e0)

    def glide(tag, x0, y0, x1, y1, t0, t1, dur):
        an = a(tag, dur, loop=True)                        # a forced tag loops past its 430 ms
        an.pos = lambda tt: (int(round(x0 + (x1 - x0) * min(1.0, max(0.0, (tt - t0) / max(1, t1 - t0))))),
                             int(round(y0 + (y1 - y0) * min(1.0, max(0.0, (tt - t0) / max(1, t1 - t0))))))
        return an
    px_, py_ = tx - 16, ty
    t0 = t
    pulled = t0 + tick(math.hypot(px_ - spot["x"], py_ - spot["y"]) / 3.5)
    glide("skill2_dash", spot["x"], spot["y"], px_, py_, t0, pulled, pulled - t0)
    dx_, dy_ = d.pos(pulled)
    ex_, ey_ = dx_ - 18, dy_
    landed = pulled + tick(math.hypot(ex_ - px_, ey_ - py_) / 4.5)
    glide("skill2_dash", px_, py_, ex_, ey_, pulled, landed, tick(26))
    spot["x"], spot["y"] = ex_, ey_
    under.append(Anim(frames_of(big, "e_land"), landed, ex_, ey_))
    on(fx, "e_hit", landed, d)
    on(fx, "e_hit", landed, mn)
    on(fx, "e_stun", landed, d)
    d.holds.append((landed, landed + tick(30)))
    # The Hextech Ultimatum on Darius: the leap on tick 5 at 5 px a tick, onto him; where she lands the field is set
    # and stays - its own picture, the arena forming and then standing for its 180 ticks (the sheet holds it turned half
    # round for the engine: turned back here) - and the mark is on him from 3 ticks after
    r0 = t
    hop_to = dx_ - 14
    reach = r0 + tick(5) + tick(max(1.0, abs(hop_to - ex_) / 5.0))
    ult = a("ult", tick(30))
    ult.pos = lambda tt, t0=r0 + tick(5), t1=reach: (
        int(round(ex_ + (hop_to - ex_) * min(1.0, max(0.0, (tt - t0) / (t1 - t0))))), ey_)
    spot["x"] = hop_to
    on_until = reach + tick(180)
    under.append(Anim([(f.transpose(Image.ROTATE_180), ms) for f, ms in frames_of(big, "r_field")], reach, hop_to, ey_))
    under.append(OnFoe(frames_of(fx, "r_mark"), reach + tick(3), d, z=-1))
    under[-1].loop, under[-1].until = True, on_until
    # kicks in the arena, 30% faster: each adds R's true damage; Darius walks off, the wall drags him back
    kick(d, gap=KICK_E, extra="r_hit")
    k2 = t
    kick(d, gap=KICK_E, extra="r_hit")
    flee0 = k2 + 333                                   # after the second kick's flinch he walks for the edge
    centre = hop_to
    out_by = FIELD_R + 2 - (d.pos(flee0)[0] - centre)  # until he is 2 px out of the field
    d.flees.append((flee0, flee0 + 520, out_by))
    zap = flee0 + 520                                  # out: a 4-tick Grab drags him back toward her, the wall's zap
    d.slides.append((zap, zap + tick(4), -(out_by + 2)))
    on(fx, "r_wall", zap, d)
    last = kick(d, gap=KICK_E, extra="r_hit")
    d.death = last + 120
    idle_to(max(on_until, d.death) + 700)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    gaps = [tt for tt in range(0, int(end), step) if not any(an.frame(tt) is not None for an in body)]
    assert not gaps, f"Camille missing at {gaps[:10]} ms"

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        her = next((an for an in body if an.frame(tt) is not None), None)
        units = [(foe.pos(tt)[1], 0, foe) for foe in [d, g] + props] + [(her.pos(tt)[1], 1, her)]
        for _, _, u in sorted(units, key=lambda v: (v[0], v[1])):
            place(img, u.frame(tt), *u.pos(tt))
        for an in over:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        frames.append(img.resize((W * z, H * z), Image.NEAREST).convert("RGB"))
        tt += step
    sample = frames[::6]                               # one palette for the whole clip
    strip = Image.new("RGB", (W * z, H * z * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * H * z))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_camille_frames.png")))
    sp, bp = load(FX), load(BIG)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags] +
                             [(bp, "e_land", "e_land"), (FieldView(bp), "r_field", "r_field (14 of 38)")],
                             os.path.join(args.out, "league_camille_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_camille_showcase.gif")))


if __name__ == "__main__":
    main()

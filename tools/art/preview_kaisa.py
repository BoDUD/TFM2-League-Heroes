#!/usr/bin/env python3
"""Preview images for Kai'Sa, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kaisa.py [--out docs/preview]

  league_kaisa_frames.png    every animation, frame by frame, 3x on the arena colour
  league_kaisa_effects.png   every effect animation, 3x
  league_kaisa_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: she runs in and fires
                             Void Seeker from 150 px: the charge in her arm cannon, the blast, the big void bullet
                             across the field, two Plasma pips over his head; she walks up to him: her first shot
                             sets off Supercharge (the flash round her, then her attacks speed up with the arcs on her)
                             and adds a pip; Icathian Rain flashes from both pods and six lasers fan out and meet on
                             him; two more shots: the fifth pip ruptures and he falls;
                             Garen walks up; Killer Instinct: the launch burst left on the ground, she flies at him in
                             the dash pose with the trail behind her, lands next to him in her shield; she evolves;
                             3x
Projectiles fly as the kit flies them: from over her pivot, lifted 5000 - y_offset (the bolt and W's line 8 px, Q's
lasers 26, 17 and 35 px: out of the pods, fanned), at the target's pivot, turned to their way; the bolt and the W
bullet start empty while they cross her (tools/art/import_kaisa.py).
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
from preview_caitlyn import Turned  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_kaisa")
FX = os.path.join(LEAGUE, "effects", "league_kaisa_fx")
# the kit's projectiles: speed in px a tick, lift over her pivot in px (5000 - y_offset)
BOLT, VOID = (7.0, 8.0), (14.0, 8.0)
MISSILES = [(4.5, 26.0), (4.5, 17.0), (4.5, 35.0)]   # Q's three lifts (the kit's q_lifts), the first at the pods
DASH = 6.0                                     # Killer Instinct's MoveToTarget, px a tick


def showcase(out, z=3, step=40):
    ks = load(CHAMP)
    fx = load(FX)
    W, H = 320, 132
    gy = 96                                            # her pivot row: the raised pods stand 33 px over it
    x = 16
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 193, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 350, gy - 6)      # a row behind, off the edge
    body, under, over = [], [], []
    t = 0.0
    stacks = {"n": 0}

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t, x
        an = Anim(frames_of(ks, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to
        return an

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def flash(tag, at, until=None):
        """A CasterViewEffect with is_follow: it rides her pivot."""
        an = Follow(frames_of(fx, tag), at, x, gy, on=body)
        if until is not None:
            an.loop, an.until = True, until
        over.append(an)
        return an

    def fly(tag, at, foe, kind):
        """A TargetProjectile from over her pivot to the foe's pivot. Its arrival."""
        speed, lift = kind
        fx_, fy = foe.pos(at)
        x0, y0 = x, gy - lift
        arrive = at + tick(max(1.0, math.hypot(fx_ - x0, fy - y0) / speed))
        over.append(Turned(frames_of(fx, tag), at, x0, y0, until=arrive, x1=fx_, y1=fy))
        return arrive

    def on(foe, tag, at, until=None):
        an = OnFoe(frames_of(fx, tag), at, foe, z=2)
        if until is not None:
            an.loop, an.until = True, until
        over.append(an)
        return an

    def plasma(foe, at, n=1):
        """n Plasma stacks: the mark with that many pips for 1 s; the fifth ruptures."""
        for k in range(n):
            stacks["n"] += 1
            when = at + tick(k)
            if stacks["n"] >= 5:
                on(foe, "p_burst", when)
                stacks["n"] = 0
                return when
            on(foe, f"pl_{stacks['n']}", when)
        return None

    def shot(foe, cd=60):
        """The attack: the bolt leaves her palm on tick 8 of the 24-tick strip; the next one cd ticks later."""
        start = t
        fire = start + tick(8)
        flash("shot", fire)
        land = fly("bolt", fire, foe, BOLT)
        on(foe, "hit", land)
        foe.flinches.append(land)
        a("attack", tick(24))
        return start + tick(cd), land

    # she runs in (move speed 900: 54 px a second) and stops 150 px from Darius: Void Seeker's reach (150000)
    a("run", 500, loop=True, at=x, to=x + 27)
    # Void Seeker: the charge in the arm cannon (from 170 ms), the aim locked 6 ticks before the shot on tick 23 of
    # the 36-tick strip; the big bullet at 14 px a tick from 8 px over her pivot, across the field; its hit gives two
    # Plasma stacks
    w0 = t
    flash("w_charge", w0)
    wf = w0 + tick(23)
    flash("w_muzzle", wf)
    dx_, dy_ = d.pos(wf - tick(6))
    w_hit = wf + tick(max(1.0, math.hypot(dx_ - x, dy_ - (gy - VOID[1])) / VOID[0]))
    over.append(Turned(frames_of(fx, "w_bolt"), wf, x, gy - VOID[1], until=w_hit, x1=dx_, y1=dy_))
    on(d, "w_hit", w_hit)
    d.flinches.append(w_hit)
    plasma(d, w_hit, n=2)
    a("skill2", tick(36))
    # then into her attack reach (55000: 55 px)
    a("run", 1750, loop=True, to=d.x - 55)
    # the first champion hit: Supercharge - the burst round her, 45% move speed, then 70% attack speed for 4 s with
    # the arcs replayed every second; the hit is the third stack
    nxt, land = shot(d)
    plasma(d, land)
    flash("e_cast", land)
    for k in range(4):
        flash("e_aura", land + 1000 * k + 450)
    idle_to(nxt)
    # Icathian Rain: both pods flash on tick 9 of the 30-tick strip; the first laser at him, the other five from the
    # three casteds (a 2-tick step, the first after one 6-tick period), each from its own height: they fan out and meet
    q0 = t
    qf = q0 + tick(9)
    flash("q_cast", qf)
    for k, when in enumerate((0, 6, 8, 10, 12, 14)):
        lift = MISSILES[0] if k == 0 else MISSILES[k % 3]
        arrive = fly("q_missile", qf + tick(when), d, lift)
        on(d, "q_hit", arrive)
        d.flinches.append(arrive)
    a("skill", tick(30))
    # two more shots: the fourth stack, then the fifth ruptures and he falls
    for _ in range(2):
        nxt, land = shot(d, cd=35)
        burst = plasma(d, land)
        idle_to(nxt)
    d.death = burst + tick(10)
    idle_to(t + 200)
    # Garen comes up behind him
    g.walks.append((t - 1400, t + 300, 262 - g.x))
    idle_to(t + 700)
    # Killer Instinct on Garen: the 8-tick launch, the burst left where she stood (not following), then she flies
    # at him in the dash pose (6 px a tick) with the trail and lands beside him: the landing, the shield for 2 s
    r0 = t
    rl = r0 + tick(7)
    under.append(Anim(frames_of(fx, "r_launch"), rl, x, gy))
    a("ult", rl - r0)
    gx, _ = g.pos(rl)
    to = gx - 16
    fly_ms = tick(max(1.0, (to - x) / DASH))
    flash("r_trail", r0)                    # played on the ult's first tick, empty for the 7 ticks before the dash
    a("ult_dash", fly_ms, loop=True, to=to)
    landed = t
    flash("r_land", landed)
    flash("r_shield", landed)
    a("ult_land", tick(14))
    for _ in range(2):
        nxt, land = shot(g)
        on(g, "pl_1" if _ == 0 else "pl_2", land)
        idle_to(nxt)
    idle_to(landed + 2100)
    # an evolution (a level reached): the column of light
    flash("evolve", t)
    idle_to(t + 1100)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted((d, g), key=lambda f: f.y)          # the one further back first
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        for foe in order:
            place(img, foe.frame(tt), *foe.pos(tt))
        for an in body:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
                break
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
                            os.path.join(args.out, "league_kaisa_frames.png")))
    sp = load(FX)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags],
                             os.path.join(args.out, "league_kaisa_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_kaisa_showcase.gif")))


if __name__ == "__main__":
    main()

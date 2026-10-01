#!/usr/bin/env python3
"""Preview images for Tristana, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_tristana.py [--out docs/preview]

  league_tristana_frames.png    every animation, frame by frame, 3x on the arena colour
  league_tristana_effects.png   every effect animation, 3x
  league_tristana_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: she runs in and her
                                cannon's ball hits Darius; E + Q: the charge flies from the lowered barrel and
                                sticks on him (no light yet) while the barrel steams (Rapid Fire); two quick
                                shots light two lights, Rocket Jump lands on him (the fire ring, the third light)
                                and the fourth hit blows the charge at once (the big explosion); Garen walks up
                                behind him; Buster Shot: the muzzle blast, the blazing ball, the shockwave knocks
                                both back and they are stunned where they land; her next ball kills Darius - he
                                explodes (Explosive Charge's passive) and W is ready again (the rocket over her
                                head); she shoots Garen; 3x
"""
import argparse
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
CHAMP = os.path.join(LEAGUE, "champions", "league_tristana")
FX = os.path.join(LEAGUE, "effects", "league_tristana_fx")
BIG = os.path.join(LEAGUE, "effects", "league_tristana_big")


def showcase(out, z=3, step=40):
    tr = load(CHAMP)
    fx, big = load(FX), load(BIG)
    W, H = 320, 130
    gy = 90                                            # her pivot row: the goggles stand 22 px over it
    x = 70                                             # where she stands after running in
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 150, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 360, gy - 6)      # a row behind, off the edge
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t, x
        an = Anim(frames_of(tr, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def mine(sp, tag, at, px=None, py=None, ground=False):
        """A CasterViewEffect on her (drawn at her pivot, where she was when it played)."""
        an = Anim(frames_of(sp, tag), at, x if px is None else px, gy if py is None else py)
        (under if ground else over).append(an)
        return an

    def fly(tag, at, foe, speed, lift):
        """A TargetProjectile from her pivot, its picture `lift` px over it (5000 - y_offset), to the foe's pivot; the
        tag's empty lead-in hides it while it crosses her. Its arrival."""
        fx_, fy = foe.pos(at)
        arrive = at + tick(max(1.0, (fx_ - x) / speed))
        over.append(Anim(frames_of(fx, tag), at, x, gy - lift, until=arrive, x1=fx_, y1=fy - lift))
        return arrive

    stacks = {"n": 0, "since": None}
    bomb = []                                          # (t0, t1, stacks) on Darius

    def light(at):
        """A hit of hers on the bomb's carrier: a light more (the spark), the fourth blows it."""
        if stacks["since"] is None:
            return False
        bomb.append((stacks["since"], at, stacks["n"]))
        stacks["n"] += 1
        if stacks["n"] == 4:
            stacks["since"] = None
            under.append(Anim(frames_of(big, "e_boom4"), at, *d.pos(at)))
            d.flinches.append(at)
            return True
        stacks["since"] = at
        over.append(OnFoe(frames_of(fx, "e_stack"), at, d, z=3))
        return False

    def attack(foe, gap=1000):
        """The cannon: the ball leaves on tick 8 of the 24-tick strip (6 px a tick, 3 px over the pivot), the flash at
        the bell; the next shot `gap` ms later (1 s, 0.55 s in Rapid Fire)."""
        start = t
        fire = start + tick(8)
        mine(fx, "shot", fire)
        land = fly("bolt", fire, foe, 6.0, 3)
        over.append(OnFoe(frames_of(fx, "hit"), land, foe, z=2))
        foe.flinches.append(land)
        a("attack", tick(24))
        return start + gap, land

    # she runs in (move speed 900: 54 px a second) to 80 px from Darius, in her reach with the level-9 stages
    a("run", 1100, loop=True, at=10, to=x)
    x = 70
    nxt, _ = attack(d)
    idle_to(nxt)
    # E + Q: the charge leaves the lowered barrel on tick 8 (4.5 px a tick, 4 px under the pivot) and sticks; the
    # barrel steams every second of Rapid Fire's 7 s
    e0 = t
    mine(fx, "e_shot", e0 + tick(8))
    mine(fx, "q_cast", e0 + tick(18))
    stick = fly("e_charge", e0 + tick(8), d, 4.5, -4)
    stacks["since"] = stick
    steam = [e0 + tick(k) for k in range(20, 420, 60)]
    a("skill", tick(18))
    idle_to(t + 120)
    for _ in range(2):                                 # two quick shots: two lights
        nxt, land = attack(d, gap=550)
        light(land)
        idle_to(nxt)
    # Rocket Jump onto him (the bomb holds two lights): 7 ticks' crouch, 4 px a tick, the fire ring where she lands
    # and the third light
    w0 = t
    land_x = d.x - 30
    lift_off = w0 + tick(7)
    touch = lift_off + tick((land_x - x) / 4.0)
    body.append(Anim(frames_of(tr, "skill2"), w0, x, gy, until=w0 + tick(32), x1=land_x))
    body[-1].pos = lambda tt, a0=x, a1=land_x: (
        a0 if tt <= lift_off else (a1 if tt >= touch else int(round(a0 + (a1 - a0) * (tt - lift_off) / (touch - lift_off)))),
        gy)
    t = w0 + tick(32)
    x = land_x
    under.append(Anim(frames_of(big, "w_land"), touch, x, gy))
    light(touch)
    idle_to(t + 100)
    nxt, land = attack(d, gap=550)                    # the fourth light: the charge blows at once
    light(land)
    idle_to(nxt)
    # Garen comes up behind Darius
    g.walks.append((1500, nxt + 200, 172 - g.x))
    idle_to(nxt + 250)
    # Buster Shot at Darius (the nearest champion): the blast on tick 9, the ball 7 px a tick 1 px under the pivot;
    # the shockwave round him a tick after the hit knocks both 30 px away over 10 ticks, stunned 0.5 s where they land
    r0 = t
    mine(fx, "r_muzzle", r0 + tick(9))
    hit = fly("r_ball", r0 + tick(9), d, 7.0, -1)
    over.append(OnFoe(frames_of(fx, "r_hit"), hit, d, z=2))
    blast = hit + tick(1)
    under.append(Anim(frames_of(big, "r_blast"), blast, *d.pos(blast)))
    for foe in (d, g):
        foe.slides.append((blast, blast + tick(10), 30))
        over.append(OnFoe(frames_of(fx, "r_stun"), blast + tick(10), foe, z=3))
        foe.holds.append((blast, blast + tick(40)))
    a("ult", tick(40))
    idle_to(blast + tick(40) + 150)
    # her next ball kills Darius: he explodes where he stood and W is ready again
    nxt, land = attack(d)
    d.death = land
    boom_at = land + tick(8)
    under.append(Anim(frames_of(fx, "p_boom"), boom_at, *d.pos(boom_at)))
    mine(fx, "w_ready", land + tick(4))
    over[-1].pos = lambda tt: (x, gy)
    idle_to(nxt)
    nxt, _ = attack(g)
    idle_to(nxt)
    attack(g)
    idle_to(t + 700)
    end = t
    for s0 in steam:                                   # the steam follows her (a CasterViewEffect with is_follow)
        over.append(Follow(frames_of(fx, "q_rapid"), s0, x, gy, on=body))

    # the bomb on Darius: its picture replayed every 10 ticks, the lights as they stand
    for b0, b1, n in bomb:
        k = b0
        while k < b1:
            over.append(OnFoe(frames_of(fx, f"e_bomb{n}"), k, d, z=2))
            over[-1].until = min(k + tick(10), b1)
            k += tick(10)

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
                            os.path.join(args.out, "league_tristana_frames.png")))
    sp, bp = load(FX), load(BIG)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags] +
                             [(bp, t["name"], t["name"]) for t in bp.tags],
                             os.path.join(args.out, "league_tristana_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_tristana_showcase.gif")))


if __name__ == "__main__":
    main()

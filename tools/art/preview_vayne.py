#!/usr/bin/env python3
"""Preview images for Vayne, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_vayne.py [--out docs/preview]

  league_vayne_frames.png    every animation, frame by frame, 3x on the arena colour
  league_vayne_effects.png   every effect animation, 3x
  league_vayne_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: she runs in and her
                             wrist crossbow's bolt puts Silver Bolts' first ring on Darius; Tumble, with him in her
                             reach, is the hop back (the smoke stays where she left), and its shot puts the second
                             ring on; the third bolt bursts the rings (true damage); Condemn's heavy bolt knocks him
                             back and he slams down stunned for a second; Final Hour: the flare and the bats behind
                             her, the silver aura round her feet for 8 s; her bolts burst the rings again and Darius
                             falls, which refreshes Final Hour (the crimson ring); Garen walks up, she Tumbles
                             away from him unseen for a second and her Tumble shot rings him; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_vayne")
FX = os.path.join(LEAGUE, "effects", "league_vayne_fx")


class Slide(Anim):
    """An animation whose unit slides from x to x1 between moments m0 and m1 (Tumble inside its strip)."""

    def __init__(self, *args, m0=0.0, m1=0.0, **kw):
        super().__init__(*args, **kw)
        self.m0, self.m1 = m0, m1

    def pos(self, t):
        if t <= self.m0:
            return self.x, self.y
        if t >= self.m1:
            return self.x1, self.y1
        u = (t - self.m0) / (self.m1 - self.m0)
        return int(round(self.x + (self.x1 - self.x) * u)), self.y


def showcase(out, z=3, step=40):
    va = load(CHAMP)
    fx = load(FX)
    W, H = 320, 130
    gy = 92                                            # her pivot row: the ponytail stands 37 px over it
    vx = 22                                            # where she is
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 140, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 360, gy - 8)      # a row behind, off the edge
    body, under, over = [], [], []
    unseen = []                                        # Final Hour's Tumble: invisible for a second
    t = 0.0

    def a(tag, dur=None, loop=False, to=None):
        nonlocal t, vx
        an = Anim(frames_of(va, tag), t, vx, gy, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            vx = to

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def fly(tag, at, speed, foe, hit_tags, dy=-12, dx=18):
        """A TargetProjectile from her wrist (dx, dy from her pivot) at `speed` px a tick onto `foe`; the hit views
        where it lands; the moment it lands."""
        x0, y0 = vx + dx, gy + dy
        fx_, fy = foe.pos(at)
        arrive = at + tick(max(1.0, (fx_ - 4 - x0) / speed))
        over.append(Anim(frames_of(fx, tag), at, x0, y0, loop=True, until=arrive, x1=fx_ - 4, y1=fy + dy))
        for h in hit_tags:
            over.append(OnFoe(frames_of(fx, h), arrive, foe, z=2))
        foe.flinches.append(arrive)
        return arrive

    rings = {"n": 0}

    def silver(foe):
        """Silver Bolts on this hit: the first ring, the second, the burst on the third."""
        rings["n"] = rings["n"] % 3 + 1
        return {1: "sb_ring1", 2: "sb_ring2", 3: "sb_proc"}[rings["n"]]

    def attack(foe, tumble=False):
        """The wrist crossbow: the bolt leaves on tick 8 of the 26-tick strip; the next attack a second later.
        After a Tumble it is the Tumble shot (its own crouched strip, the bigger bolt)."""
        start = t
        if tumble:
            land = fly("q_bolt", start + tick(8), 6.0, foe, ["q_hit", silver(foe)])
            a("attack_q", tick(26))
        else:
            land = fly("bolt", start + tick(8), 6.0, foe, ["hit", silver(foe)])
            a("attack", tick(26))
        return start + 1000, land

    def tumble_back(px):
        """Tumble with a champion in her reach: the hop back (px over the move's ticks from tick 1), the smoke on
        the ground where she left."""
        nonlocal t, vx
        start = t
        under.append(Anim(frames_of(fx, "q_roll"), start + tick(1), vx, gy))
        body.append(Slide(frames_of(va, "skill_back"), start, vx, gy, x1=vx - px, m0=start + tick(1),
                          m1=start + tick(1 + (2 if px <= 10 else 4))))
        vx -= px
        t = body[-1].until
        return start

    # she runs in (move speed 900: 54 px a second) to 50 px from Darius, in her 55 reach
    a("run", 1200, loop=True, to=90)
    nxt, _ = attack(d)
    idle_to(t + 120)
    # Tumble (Darius in her reach: the hop back, 10 px), then the Tumble shot
    tumble_back(10)
    idle_to(nxt)
    nxt, _ = attack(d, tumble=True)
    idle_to(nxt)
    nxt, _ = attack(d)                                 # the third hit: the rings burst
    idle_to(t + 150)
    # Condemn: the heavy bolt on tick 12 (7 px a tick), the knockback 24 px over 8 ticks, the slam 8 ticks after
    # the hit and a 1 s stun
    start = t
    hit = fly("e_bolt", start + tick(12), 7.0, d, ["e_hit"], dy=-12, dx=16)
    d.slides.append((hit, hit + tick(8), 24))
    slam = hit + tick(8)
    over.append(OnFoe(frames_of(fx, "e_stun"), slam, d, z=3))
    d.holds.append((slam, slam + 1000))
    a("skill2", tick(31))
    idle_to(slam + 250)
    # Final Hour: the flare and the bats on tick 8, the aura for 8 s (both under the units: her body covers them)
    r0 = t
    under.append(Follow(frames_of(fx, "r_cast"), r0 + tick(8), vx, gy, on=body))
    aura_end = r0 + tick(8) + 8000
    a("ult", tick(34))
    # her bolts in Final Hour: the rings again, the burst finishes Darius and refreshes Final Hour
    nxt = t + 200
    for k in range(3):
        idle_to(nxt)
        nxt, land = attack(d)
    d.death = land
    under.append(Follow(frames_of(fx, "r_refresh"), land, vx, gy, on=body))
    aura_end = land + 8000
    # Garen walks up to her; she Tumbles away from him (within 30 px: 24 px back), unseen for a second
    g.walks.append((r0, land + 900, -255))
    idle_to(land + 900)
    q2 = tumble_back(24)
    unseen.append((q2 + tick(1), q2 + tick(1) + 1000))
    idle_to(q2 + 700)
    rings["n"] = 0
    nxt, _ = attack(g, tumble=True)
    idle_to(nxt)
    attack(g)
    idle_to(t + 600)
    end = t
    under.append(Follow(frames_of(fx, "r_aura"), r0 + tick(8), vx, gy, loop=True, until=min(aura_end, end),
                        on=body))

    def place(img, f, px, py, alpha=1.0):
        if alpha < 1.0:
            f = f.copy()
            f.putalpha(f.getchannel("A").point(lambda v: int(v * alpha)))
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
                seen = 0.4 if any(u0 <= tt < u1 for u0, u1 in unseen) else 1.0
                place(img, f, *an.pos(tt), alpha=seen)
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
                            os.path.join(args.out, "league_vayne_frames.png")))
    sp = load(FX)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags],
                             os.path.join(args.out, "league_vayne_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_vayne_showcase.gif")))


if __name__ == "__main__":
    main()

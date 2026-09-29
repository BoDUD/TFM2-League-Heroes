#!/usr/bin/env python3
"""Preview images for Lucian, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_lucian.py [--out docs/preview]

  league_lucian_frames.png    every animation, frame by frame, 3x on the arena colour
  league_lucian_effects.png   every effect animation, 3x
  league_lucian_showcase.gif  a scripted fight against Darius and Garen, timed like the kit (cooldowns kept): he
                              runs in and Darius, still out of his reach, gets Relentless Pursuit forward (the dust
                              where he leaves; he lands in range when the path stops) and Ardent Blaze's star
                              cross, which marks him; the next two attacks fire twice (the second shot gold) and
                              every hit while the mark lasts speeds Lucian up (the lines at his feet); Piercing
                              Light, both pistols held out at shoulder height: the beam from the muzzle through
                              Darius, the double shot it gives, a single bullet; The Culling: three seconds of
                              tracers at the nearest champion - Darius falls, the rest go to Garen walking up; Garen
                              reaches him, and nine seconds after the first the E dashes him back out of Garen's
                              reach, the bolt bursts on Garen and the double shot follows; 3x
"""
import argparse
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_ezreal import Hop  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow, Walker  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_lucian")
FX = os.path.join(LEAGUE, "effects", "league_lucian_fx")


class Slide(Anim):
    """An animation whose unit slides from x to x1 between moments m0 and m1 (a dash inside the action)."""

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


class Ray(Anim):
    """Piercing Light's carrier as the game moves it: from (x, y) toward (x1, y1) at `speed` px a tick, its frames
    turned to that direction (they draw the beam further back as it flies, so the beam stands still)."""

    def __init__(self, fr, t0, x, y, x1, y1, speed):
        ang = math.degrees(math.atan2(y1 - y, x1 - x))
        turned = [(f.rotate(-ang, resample=Image.NEAREST, expand=True), ms) for f, ms in fr]
        dist = math.hypot(x1 - x, y1 - y)
        super().__init__(turned, t0, x, y, until=t0 + tick(dist / speed))
        self.ux, self.uy, self.speed, self.x1, self.y1 = (x1 - x) / dist, (y1 - y) / dist, speed, x1, y1

    def pos(self, t):
        d = self.speed * math.floor(max(0.0, t - self.t0) * 60 / 1000.0 + 1e-6)      # it moves once a tick
        return int(round(self.x + self.ux * d)), int(round(self.y + self.uy * d))


def showcase(out, z=3, step=40):
    lu = load(CHAMP)
    fx = load(FX)
    W, H = 320, 130
    gy = 92                                            # his pivot row
    lx = 70                                            # where he stops running
    d = Walker(load(os.path.join(LEAGUE, "champions", "league_darius")), 195, gy)
    d.walks.append((0.0, 1000.0, -48))                 # to 147: 77 px from him, in E's 80 but out of his 55
    g = Walker(load(os.path.join(LEAGUE, "champions", "league_garen")), 400, gy - 10)    # a row behind Darius
    g.walks.append((0.0, 8600.0, -275))                # walks up behind Darius to 125
    body, under, over = [], [], []
    hits = []                                          # moments a hit lands (Ardent Blaze's haste)
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(lu, tag), t, lx, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def idle_to(at):
        if at > t:
            a("idle", at - t, loop=True)

    def fx_at(tag, at, px, py, until=None, x1=None, y1=None, loop=None, z_under=False):
        an = Anim(frames_of(fx, tag), at, px, py, loop=(until is not None) if loop is None else loop,
                  until=until, x1=x1, y1=y1)
        (under if z_under else over).append(an)
        return an

    def fly(tag, at, speed, foe, hit="hit", dy=-11, dx=12):
        """A shot from the pistols at `speed` px a tick onto `foe`'s chest, its hit picture on arrival."""
        x0, y0 = lx + dx, gy + dy
        fx_, fy = foe.pos(at)
        arrive = at + tick(max(1.0, (fx_ - 4 - x0) / speed))
        fx_at(tag, at, x0, y0, until=arrive, x1=fx_ - 4, y1=fy - 8)
        fx_at(hit, arrive, *foe.pos(arrive))
        foe.flinches.append(arrive)
        return arrive

    def attack(foe):
        """A single bullet on tick 7; the next attack a second after this one."""
        start = t
        hits.append(fly("bullet", start + tick(7), 7.0, foe))
        a("attack")
        return start + 1000

    def double(foe):
        """Lightslinger: two shots, ticks 6 and 13, the second gold."""
        start = t
        hits.append(fly("bullet", start + tick(6), 7.0, foe))
        hits.append(fly("bullet2", start + tick(13), 7.0, foe))
        a("passive")
        return start + 1000

    def blaze(start, foe):
        """Ardent Blaze on tick 14 of the E: the bolt to the first enemy, the star cross, the mark."""
        x0, y0 = lx + 12, gy - 11
        fx_, fy = foe.pos(start + tick(14))
        boom = start + tick(14) + tick(max(1.0, (fx_ - x0) / 7.0))
        fx_at("w_bolt", start + tick(14), x0, y0, until=boom, x1=fx_, y1=fy - 8)
        fx_at("w_burst", boom, *foe.pos(boom), z_under=True)
        foe.flinches.append(boom)
        return boom

    # he runs in; Darius comes on, Garen walks up far behind him
    body.append(Anim(frames_of(lu, "run"), 0.0, 16, gy, loop=True, until=1000.0, x1=lx))
    t = 1000.0
    # Relentless Pursuit forward: nothing in his reach, so the invisible path runs 6 px a tick at Darius and he lands
    # where it stops (its full 30 px here, on tick 5; 47 px from Darius); the dust stays where he left
    e1 = t
    fx_at("e_dash", e1 + tick(1), lx, gy, z_under=True)
    body.append(Hop(frames_of(lu, "skill2"), e1, lx, gy, x1=lx + 30, m=e1 + tick(6)))
    lx += 30
    t = body[-1].until
    boom = blaze(e1, d)
    marked = [(boom, boom + 6000, d)]
    flag = [(boom, boom + 6000)]                       # w_ms on him: every hit speeds him up for a second
    # the two charged attacks, then Piercing Light (on tick 12 the carrier starts 12 px above him, at the muzzle
    # of frame 4, and flies to the line's end 100 px ahead at his waist's height, 7 px a tick; the hit a tick
    # later), its double shot, a single bullet
    nxt = double(d)
    idle_to(nxt)
    nxt = double(d)
    idle_to(nxt - 480)
    q0 = t
    over.append(Ray(frames_of(fx, "q_ray"), q0 + tick(12), lx, gy - 12, lx + 100, gy, 7.0))
    for foe in (d, g):
        if foe.pos(q0 + tick(12))[0] - lx <= 104:
            fx_at("q_hit", q0 + tick(13), *foe.pos(q0 + tick(13)))
            foe.flinches.append(q0 + tick(13))
            hits.append(q0 + tick(13))
    a("skill")
    idle_to(nxt)
    nxt = double(d)
    idle_to(nxt)
    nxt = attack(d)
    idle_to(nxt + 90)
    # The Culling: a standing channel (186 ticks), a shot every 9 ticks from tick 10 at the nearest champion
    # (rings of 40, 75 and 110 px), 12 px a tick from 5 px above him (a LinearProjectile's height, the lower
    # pistol of the ult frames); Darius falls to the ninth, the rest go to Garen
    r0 = t
    a("ult", tick(186), loop=True)
    for k in range(20):
        at = r0 + tick(10 + 9 * k)
        foe = d if d.death is None else g
        x0, y0 = lx + 13, gy - 5
        fx_, fy = foe.pos(at)
        arrive = at + tick(max(1.0, (fx_ - 4 - x0) / 12.0))
        fx_at("r_bullet", at, x0, y0, until=arrive, x1=fx_ - 4, y1=fy - 5)
        fx_at("r_hit", arrive, *foe.pos(arrive))
        if foe is d and k == 8:
            d.death = arrive
        else:
            foe.flinches.append(arrive)
    # its end charges one double shot; Garen comes into reach, a single bullet after it
    nxt = double(g)
    idle_to(nxt)
    nxt = attack(g)
    # nine seconds after the first, the E again: Garen stands on him (within 30 px), so a dash back, 6 px a tick
    # for 5 ticks, and the bolt bursts on Garen as he follows
    idle_to(e1 + 9000)
    e2 = t
    fx_at("e_dash", e2 + tick(1), lx, gy, z_under=True)
    body.append(Slide(frames_of(lu, "skill2_back"), e2, lx, gy, x1=lx - 30, m0=e2 + tick(1), m1=e2 + tick(6)))
    lx -= 30
    t = body[-1].until
    g.walks.append((e2 + 300, e2 + 1000, -22))
    boom = blaze(e2, g)
    marked.append((boom, boom + 6000, g))
    flag.append((boom, boom + 6000))
    double(g)
    idle_to(t + 700)
    end = t

    for m0, m1, foe in marked:
        until = min(m1, foe.death) if foe.death is not None else m1
        under.append(Follow(frames_of(fx, "w_mark"), m0, *foe.pos(m0), loop=True, until=min(until, end),
                            on=[foe]))
    spans = []
    for h in sorted(hits):
        if any(f0 <= h < f1 for f0, f1 in flag):
            if spans and h <= spans[-1][1]:
                spans[-1][1] = h + 1000
            else:
                spans.append([h, h + 1000])
    for h0, h1 in spans:
        under.append(Follow(frames_of(fx, "w_haste"), h0, lx, gy, loop=True, until=min(h1, end), on=body))

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted((d, g), key=lambda f: f.y)         # the one further back first
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
    sample = frames[::6]                              # one palette for the whole clip
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
                            os.path.join(args.out, "league_lucian_frames.png")))
    sp = load(FX)
    print("effects", contact([(sp, t["name"], t["name"]) for t in sp.tags],
                             os.path.join(args.out, "league_lucian_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_lucian_showcase.gif")))


if __name__ == "__main__":
    main()

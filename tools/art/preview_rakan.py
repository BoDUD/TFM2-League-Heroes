#!/usr/bin/env python3
"""Preview images for Rakan, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_rakan.py [--out docs/preview]

  league_rakan_frames.png    every animation, frame by frame, 3x on the arena colour
  league_rakan_effects.png   every effect animation, 3x
  league_rakan_showcase.gif  a scripted fight beside Jhin against Darius with Garen behind him, timed like the kit:
                             Rakan runs in under Fey Feathers' shield and throws two feathers at Darius; Gleaming
                             Quill bursts on him and arms the heal (the yellow-green ring at Rakan's feet); Grand
                             Entrance: he dashes onto Darius, spirals up in a column of golden feathers and knocks
                             him up, then Battle Dance flies him back to Jhin - the golden ward on Jhin, and landing
                             beside him sets the heal off over both; The Quickness: the burst of feathers, the
                             ribbons trailing behind him as he dashes through Darius and Garen, golden hearts over
                             both as they are charmed and walk to him; Darius falls; 3x
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

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_rakan")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_rakan_fx", "league_rakan_big")}


class Charmed(Held):
    """A foe that walks either way: toward Rakan when charmed - to the right it faces right (its run unmirrored)."""

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1, dx in self.walks:
                if t0 <= t < t1 and dx > 0:
                    return self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
        return super().frame(t)


class Body:
    """Rakan's pivot over time (the views that follow him read it), from his body animations."""

    def __init__(self, body):
        self.body = body

    def pos(self, t):
        last = None
        for an in self.body:
            if an.t0 <= t and (an.until is None or t < an.until):
                return an.pos(t)
            if an.t0 <= t:
                last = an
        return last.pos(t) if last else self.body[0].pos(t)


def showcase(out, z=3, step=40):
    rakan = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_rakan_fx"], fx["league_rakan_big"]
    W, H = 300, 130
    gy = 90                                           # the pivot row: W's column rises 44 px over his soles
    x0 = 70
    j = Held(load(os.path.join(LEAGUE, "champions", "league_jhin")), x0 - 34, gy - 2)       # his lane partner
    j.mirrored = False
    d = Charmed(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 40, gy + 4)  # 40 px: attack range
    g = Charmed(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 70, gy - 10)  # behind him
    body, under, over = [], [], []
    me = Body(body)
    t = 0.0
    x = x0

    def a(tag, dur=None, loop=False, to=None):
        nonlocal t, x
        an = Anim(frames_of(rakan, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def at(sp, tag, when, px, py, ground=False):
        an = Anim(frames_of(sp, tag), when, px, py, z=-1 if ground else 1)
        (under if ground else over).append(an)
        return an

    def fly(tag, launch, sx, sy, tx, ty, speed):
        """A projectile from (sx, sy) to (tx, ty) at `speed` px a tick; returns its arrival."""
        span = ((tx - sx) ** 2 + (ty - sy) ** 2) ** 0.5
        arrive = launch + tick(max(1.0, span / speed))
        over.append(Anim(frames_of(small, tag), launch, sx, sy, loop=True, until=arrive, x1=tx, y1=ty))
        return arrive

    # he runs in under Fey Feathers' shield (given at his first action of the life); Jhin, Darius and Garen wait
    a("run", 900, loop=True, to=x0)
    x = x0
    body[-1].x = x0 - 40
    shield = on(me, small, "p_on", 0.0, until=10 ** 9, ground=True)
    a("idle", 250, loop=True)
    # two feathers at Darius: the attack's 12-tick release, 6000 a tick
    for _ in range(2):
        hit = fly("a_feather", t + tick(12), x + 6, gy - 2, d.x - 4, d.y - 2, 6.0)
        on(d, small, "a_hit", hit)
        d.flinches.append(hit)
        a("attack")
        a("idle", tick(85 - 26), loop=True)
    # Darius hits back: the shield breaks
    d.attacks.append(t - 300)
    shield.until = t - 100
    # Gleaming Quill: the feather bursts on Darius, the heal is armed (its ring at his feet until it goes off)
    hit = fly("q_feather", t + tick(10), x + 6, gy - 2, d.x - 4, d.y - 2, 6.0)
    on(d, small, "q_hit", hit)
    d.flinches.append(hit)
    ring = on(me, small, "q_heal", hit, until=10 ** 9, ground=True)
    a("skill")
    a("idle", 300, loop=True)
    # Grand Entrance: the dash onto Darius (3000 a tick), the landing spin, the launch 8 ticks after it
    land = t + tick(abs(d.x - 18 - x) / 3.0)
    a("skill2", land - t, to=d.x - 18)
    a("w_spin", tick(26))
    up = land + tick(8)
    at(big, "w_burst", up, x, gy, ground=True)
    on(d, small, "w_hit", up)
    d.hops.append((up, up + tick(48), 12))
    # Battle Dance 24 ticks after the landing: the ward on Jhin, the flight back (4000 a tick), landing sets the heal off
    e0 = land + tick(24)
    if t < e0:
        a("idle", e0 - t, loop=True)
    on(j, small, "e_shield", e0)
    on(j, small, "e_on", e0, until=e0 + tick(180))
    back = e0 + tick(abs(x - (j.x + 14)) / 4.0)
    a("e_dash", back - e0, to=j.x + 14)
    ring.until = back
    at(big, "q_burst", back, x, gy, ground=True)
    on(me, small, "q_healed", back)
    on(j, small, "q_healed", back)
    a("e_land", tick(14))
    a("idle", 700, loop=True)
    # The Quickness: the burst, the ribbons behind him; he dashes through Darius, then Garen (pulses 20 ticks apart,
    # the dash 2600 a tick once the first champion is charmed), each charmed for 75 ticks and walking to him
    r0 = t
    on(me, small, "r_start", r0)
    trail = on(me, small, "r_on", r0, until=r0 + 2600, ground=True)
    past_d = d.x + 15
    reach_d = r0 + tick(abs(d.x - x) / 1.8)
    a("ult", tick(abs(past_d - x) / 1.8), loop=True, to=past_d)
    on(d, small, "r_charmed", reach_d)
    d.flinches.append(reach_d)
    past_g = g.x + 15
    reach_g = t + tick(abs(g.x - x) / 2.6)
    a("ult", tick(abs(past_g - x) / 2.6), loop=True, to=past_g)
    on(g, small, "r_charmed", reach_g)
    g.flinches.append(reach_g)
    d.walks.append((reach_d + 250, t + 200, 10))
    g.walks.append((reach_g + 250, t + 200, 6))
    # the next pulse sends him back through both, facing left: the ribbons trail on his right
    turn = t + 200
    a("ult", 200, loop=True)
    back_to = d.x - 6
    a("ult", tick(abs(x - back_to) / 2.6), loop=True, to=back_to)
    body[-1].flip = True
    trail.until = turn
    left = OnFoe([(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in frames_of(small, "r_on")], turn, me, z=-1)
    left.loop, left.until = True, t
    under.append(left)
    a("idle", 300, loop=True)                         # turned back to them
    d.death = t
    a("idle", 1300, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (j, d, g)]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1], f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p)
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
    q_ = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_rakan_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_rakan_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_rakan_showcase.gif")))


if __name__ == "__main__":
    main()

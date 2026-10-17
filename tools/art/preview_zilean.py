#!/usr/bin/env python3
"""Preview images for Zilean, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_zilean.py [--out docs/preview]

  league_zilean_frames.png    every animation, frame by frame, 3x on the arena colour
  league_zilean_effects.png   every effect animation, 3x
  league_zilean_showcase.gif  a scripted fight with Lucian in front of him against Darius and Garen, timed like the
                              kit: Zilean floats in and throws a time orb at Darius; Time Bomb: the bomb is lobbed at
                              Darius and sticks to him (ticking on his chest), Rewind turns the clock behind Zilean
                              back, he throws again and the second bomb flies at Darius: both blow at once, Darius and
                              Garen beside him are stunned (clocks over their heads); Time Warp slows Darius (a violet
                              clock round his waist) and hastens Lucian (a gold ring at his feet), the full bottle
                              pours over Lucian; a second bomb sticks to Darius and Zilean's orb finishes him - the bomb
                              blows up at once where he fell, hitting Garen; Garen walks to Lucian and silences him with
                              Decisive Strike: Chronoshift (the rune at Zilean's feet) puts the time rune on Lucian, who
                              cannot die under it while Garen spins on him, and after 5 s it rewinds him (the heal); 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_annie import OnFoe  # noqa: E402
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_zilean")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_zilean_fx", "league_zilean_big")}


class Lob(Anim):
    """A lobbed projectile: from (x, y) to (x1, y1) on a parabola `h` px high (a `ParabolicProjectile`)."""

    def __init__(self, *args, h=20, **kw):
        super().__init__(*args, **kw)
        self.h = h

    def pos(self, t):
        x, y = super().pos(t)
        u = min(1.0, max(0.0, (t - self.t0) / (self.until - self.t0)))
        return x, int(round(y - 4 * self.h * u * (1 - u)))


class Unit:
    """A unit on the field: `moves` [(t0, t1, x1, y1)] walk it (run frames, facing the way it walks), `acts`
    [(t0, frames)] play an action once, `flinches` its hit frames, `holds` [(t0, t1)] a stun (its first hit frame),
    `death` its dead frames (the last one held). Faces left when `left`."""

    def __init__(self, sprite, x, y, left):
        self.x, self.y, self.left = x, y, left
        self.idle, self.run = frames_of(sprite, "idle"), frames_of(sprite, "run")
        self.hit, self.dead = frames_of(sprite, "hit"), frames_of(sprite, "dead")
        self.moves, self.acts, self.flinches, self.holds, self.death = [], [], [], [], None
        self.cache = {}

    def flip(self, f, left):
        if not left:
            return f
        if id(f) not in self.cache:
            self.cache[id(f)] = f.transpose(Image.FLIP_LEFT_RIGHT)
        return self.cache[id(f)]

    def pos(self, t):
        x, y = self.x, self.y
        for t0, t1, x1, y1 in self.moves:
            if t >= t1:
                x, y = x1, y1
            elif t > t0:
                u = (t - t0) / (t1 - t0)
                return int(round(x + (x1 - x) * u)), int(round(y + (y1 - y) * u))
        return x, y

    @staticmethod
    def pick(fr, dt, hold=False):
        for f, ms in fr:
            if dt < ms:
                return f
            dt -= ms
        return fr[-1][0] if hold else None

    def frame(self, t):
        if self.death is not None and t >= self.death:
            return self.flip(self.pick(self.dead, t - self.death, hold=True), self.left)
        for t0, t1 in self.holds:
            if t0 <= t < t1:
                return self.flip(self.hit[0][0], self.left)
        for t0, fr in self.acts:
            f = self.pick(fr, t - t0) if t >= t0 else None
            if f is not None:
                return self.flip(f, self.left)
        x0 = self.x
        for t0, t1, x1, _ in self.moves:
            if t0 <= t < t1:
                f = self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run))
                return self.flip(f, x1 < x0 or (x1 == x0 and self.left))
            if t >= t1:
                x0 = x1
        for t0 in self.flinches:
            f = self.pick(self.hit, t - t0) if t >= t0 else None
            if f is not None:
                return self.flip(f, self.left)
        return self.flip(self.pick(self.idle, t % sum(ms for _, ms in self.idle)), self.left)


class Me:
    """Zilean's pivot for the views that follow him."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


def showcase(out, z=3, step=40):
    zl = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_zilean_fx"], fx["league_zilean_big"]
    W, H = 300, 150
    gy = 92                                           # his pivot row: the rewind clock rises 34 px over it
    x = 70
    me = Me(x, gy)
    garen_sp = load(os.path.join(LEAGUE, "champions", "league_garen"))
    lucian = Unit(load(os.path.join(LEAGUE, "champions", "league_lucian")), x + 24, gy + 20, False)  # in front
    d = Unit(load(os.path.join(LEAGUE, "champions", "league_darius")), x + 56, gy + 2, True)        # attack range
    g = Unit(garen_sp, 296, gy - 12, True)                                                            # walking in
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(zl, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def on(unit, sp, tag, at, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), at, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def at(sp, tag, when, px, py, ground=False):
        an = Anim(frames_of(sp, tag), when, px, py, z=-1 if ground else 1)
        (under if ground else over).append(an)
        return an

    def orb(launch, foe):
        """The attack's orb: from his pivot 6 px up (y_offset -1000) to the foe's at 5 px a tick."""
        tx, ty = foe.pos(launch)
        arrive = launch + tick(max(1.0, ((tx - x) ** 2 + (ty - gy) ** 2) ** 0.5 / 5.0))
        over.append(Anim(frames_of(small, "a_orb"), launch, x, gy - 6, loop=True, until=arrive, x1=tx, y1=ty - 6))
        on(foe, small, "a_hit", arrive)
        foe.flinches.append(arrive)
        return arrive

    def attack(foe):
        start = t
        on(me, small, "a_cast", start + tick(17))
        hit = orb(start + tick(17), foe)
        a("attack")
        return hit

    def bomb_ticks(foe, start, end):
        """The bomb stuck on a unit: its ticking picture replayed every 30 ticks."""
        k = start
        while k < end:
            on(foe, small, "q_bomb_on", k, until=min(k + 500, end))
            k += tick(30)

    def lob(foe, launch):
        """Q's bomb from his raised hand to where the foe stood, 24 ticks on a parabola; returns the landing."""
        tx, ty = foe.pos(launch)
        land = launch + tick(24)
        over.append(Lob(frames_of(small, "q_bomb"), launch, x + 15, gy - 21, loop=True, until=land, x1=tx,
                        y1=ty - 8, h=22))
        return land

    def stunned(foes, when):
        for foe in foes:
            on(foe, small, "q_hit", when)
            on(foe, small, "q_stun", when)
            foe.holds.append((when, when + tick(75)))

    # he floats in, Lucian beside him; Garen walks up behind Darius
    run_in = Anim(frames_of(zl, "run"), 0.0, x - 40, gy, loop=True, until=1000, x1=x)
    body.append(run_in)
    lucian.moves.append((0.0, 1000.0, lucian.x, lucian.y))
    lucian.x -= 40
    t = run_in.until
    g.moves.append((300.0, 2600.0, x + 80, gy - 12))   # 24 px behind Darius: inside the 30 px blast
    a("idle", 300, loop=True)
    attack(d)
    a("idle", 400, loop=True)
    # Time Bomb + Rewind (QWQ): the bomb leaves on tick 12 and lands on Darius 24 ticks later; with W ready he turns
    # time back (w, 30 ticks), throws again (skill, the bomb on tick 12) and the second bomb (6 px a tick, 19 px up)
    # blows both a tick after it hits: double damage, a 75-tick stun round Darius
    start = t
    on(me, small, "q_cast", start + tick(12))
    land = lob(d, start + tick(12))
    a("skill")
    a("idle", land - t, loop=True)
    a("w")
    under.append(OnFoe(frames_of(big, "w_rewind"), land, me, z=-1))
    on(me, small, "q_cast", t + tick(12))
    launch = t + tick(12)
    tx, ty = d.pos(launch)
    hit = launch + tick(max(1.0, ((tx - x) ** 2 + (ty - gy) ** 2) ** 0.5 / 6.0))
    over.append(Anim(frames_of(small, "q_bomb"), launch, x + 15, gy - 19, loop=True, until=hit, x1=tx, y1=ty - 19))
    a("skill")
    bomb_ticks(d, land, hit)
    boom = hit + tick(1)
    at(big, "q_boom2", boom, *d.pos(boom), ground=True)
    stunned([u for u in (d, g) if abs(u.pos(boom)[0] - d.pos(boom)[0]) <= 30], boom)
    a("idle", max(0.0, boom + 200 - t), loop=True)
    # Time Warp: Darius slowed 35% for 2.5 s, Lucian (beside him) hastened as long; the full bottle goes to Lucian
    start = t
    on(me, small, "e_cast", start + tick(12))
    on(d, small, "e_slow", start + tick(12), until=start + tick(12 + 150))
    on(lucian, small, "e_haste", start + tick(12), until=start + tick(12 + 150), ground=True)
    on(lucian, small, "p_bottle", start + tick(12))
    a("skill2")
    a("idle", 300, loop=True)
    attack(d)
    a("idle", 300, loop=True)
    # a single bomb on Darius (Rewind is cooling down); the next orb finishes him: the bomb blows up where he fell
    start = t
    on(me, small, "q_cast", start + tick(12))
    land = lob(d, start + tick(12))
    a("skill")
    a("idle", land - t + 200, loop=True)
    kill = attack(d)
    d.death = kill
    bomb_ticks(d, land, kill)
    blast = kill + tick(4)                            # the watch lands 2-5 ticks after the death
    at(big, "q_boom", blast, *d.pos(kill), ground=True)
    if abs(g.pos(blast)[0] - d.pos(kill)[0]) <= 30:
        on(g, small, "q_hit", blast)
        g.flinches.append(blast)
    a("idle", 500, loop=True)
    # Garen walks to Lucian, Decisive Strike silences him (crowd control) and he spins on him: Chronoshift on Lucian at
    # Zilean's next action - the rune for 5 s (he cannot die under it), then the rewind heal
    walk0 = t
    lx, ly = lucian.pos(walk0)
    g.moves.append((walk0, walk0 + 1300, lx + 22, ly - 2))
    strike = walk0 + 1300
    g.acts.append((strike, frames_of(garen_sp, "q_attack")))
    lucian.flinches.append(strike + 300)
    r = strike + 350
    a("idle", r - t, loop=True)
    under.append(OnFoe(frames_of(big, "r_cast"), r, me, z=-1))
    a("skill")
    on(lucian, big, "r_rune", r, until=r + tick(300))
    spin = frames_of(garen_sp, "spin")
    for k in range(6):                                # Garen spins on him and keeps hitting
        hit_t = r + 500 + k * 650
        g.acts.append((hit_t, spin if k % 2 == 0 else frames_of(garen_sp, "attack")))
        lucian.flinches.append(hit_t + 200)
    on(lucian, big, "r_rewind", r + tick(299))
    a("idle", r + tick(300) + 1400 - t, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in sorted(under, key=lambda a_: a_.z):
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(u.pos(tt)[1], u.frame(tt), u.pos(tt)) for u in (g, d, lucian)]
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_zilean_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_zilean_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_zilean_showcase.gif")))


if __name__ == "__main__":
    main()

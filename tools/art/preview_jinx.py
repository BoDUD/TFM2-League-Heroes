#!/usr/bin/env python3
"""Preview images for Jinx, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_jinx.py [--out docs/preview]

  league_jinx_frames.png    every animation, frame by frame, 3x on the arena colour
  league_jinx_effects.png   every effect animation, 3x
  league_jinx_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Pow-Pow's
                            bullets and Zap! (its charge at the muzzle) bring Darius down, the kill
                            sets off Get Excited!, the Super Mega Death Rocket blows up on Garen far
                            off, he charges in onto the Flame Chompers (they land, arm and bite), and
                            Fishbones fires at him, out of the minigun's reach, 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_leesin import Foe  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_jinx")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_jinx_fx", "league_jinx_big")}


class Arc(Anim):
    """An animation thrown along a parabola `h` px high from (x, y) to (x1, y1)."""

    def __init__(self, *args, h=0, **kw):
        super().__init__(*args, **kw)
        self.h = h

    def pos(self, t):
        x, y = super().pos(t)
        u = min(1.0, max(0.0, (t - self.t0) / (self.until - self.t0)))
        return x, int(round(y - 4 * self.h * u * (1 - u)))


class Walker(Foe):
    """A foe that can also walk (mirrored run frames) by dx px between t0 and t1."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.run = frames_of(sp, "run")
        self.walks = []

    def pos(self, t):
        x, y = super().pos(t)
        for t0, t1, dx in self.walks:
            if t >= t0:
                x += int(round(dx * min(1.0, (t - t0) / (t1 - t0))))
        return x, y

    def frame(self, t):
        for t0, t1, _ in self.walks:
            if t0 <= t < t1:
                return self.flip(self.pick(self.run, (t - t0) % sum(ms for _, ms in self.run)))
        return super().frame(t)


class Follow(Anim):
    """An animation that stays on a unit: its place is the unit's body animation's at each moment."""

    def __init__(self, *args, on=None, **kw):
        super().__init__(*args, **kw)
        self.on = on

    def pos(self, t):
        for an in self.on:
            if an.frame(t) is not None:
                return an.pos(t)
        return self.x, self.y


def showcase(out, z=3, step=40):
    jinx = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 290, 124
    gy = 88                                           # Jinx's pivot row
    x = 40
    foes = {
        "darius": Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), 80, gy),       # 40 px: Pow-Pow
        "garen": Walker(load(os.path.join(LEAGUE, "champions", "league_garen")), 236, gy - 10),  # far off
    }
    d, g = foes["darius"], foes["garen"]
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(jinx, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(fx[sprite], tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def fly(tag, at, x0, y0, foe, speed, sprite="league_jinx_fx", x1=None):
        """A projectile from (x0, y0) to the foe's pivot at `speed` px a tick; its arrival time."""
        fx1, fy1 = (foe.x if x1 is None else x1), foe.y - 1
        arrive = at + tick(abs(fx1 - x0) / speed)
        fx_at(sprite, tag, at, x0, y0, until=arrive, x1=fx1, y1=fy1)
        return arrive

    def bursts(gaps, last_kills=False):
        """Pow-Pow at Darius: the bullets leave on tick 7 at 4.5 px a tick; faster each time (Rev'd Up)."""
        hit = None
        for gap in gaps:
            start = t
            hit = fly("bullets", start + tick(7), x + 8, gy - 2, d, 4.5)
            fx_at("league_jinx_fx", "minigun_hit", hit, d.x, d.y)
            d.flinches.append(hit)
            a("attack")
            a("idle", gap, loop=True)
        if last_kills:
            d.death = hit + 30
        return hit

    a("idle", 400, loop=True)
    bursts((260, 200, 150))
    # Zap!: the charge at her muzzle for 0.4 s, the bolt on tick 23 at 3.3 px a tick, the target slowed
    start = t
    fx_at("league_jinx_fx", "w_charge", start, x, gy)
    hit = fly("zap", start + tick(23), x + 13, gy - 8, d, 3.3)
    fx_at("league_jinx_fx", "zap_hit", hit, d.x, d.y)
    d.flinches.append(hit)
    a("skill")
    a("idle", 150, loop=True)
    # two more bursts: the second kills Darius, and the kill sets off Get Excited! (read 4 ticks later)
    kill = bursts((150, 250), last_kills=True)
    over.append(Follow(frames_of(fx["league_jinx_fx"], "excited"), kill + tick(4), x, gy, on=body))
    # Super Mega Death Rocket! at Garen, far off: fired on tick 17 at 4.5 px a tick, a 62 px blast
    start = t
    boom = fly("r_rocket", start + tick(17), x + 6, gy - 10, g, 4.5, sprite="league_jinx_big")
    fx_at("league_jinx_big", "r_blast", boom, g.x, g.y)
    g.flinches.append(boom + 60)
    a("ult")
    a("idle", 100, loop=True)
    # Garen charges in; Flame Chompers! thrown on tick 12, 24 ticks in the air to 78 px in front of
    # her; link 1 arms, he walks onto them, and the check at the end of the next link bites: rooted
    start = t
    throw = start + tick(12)
    land = throw + tick(24)
    tx = x + 78                                       # E reaches 80 px
    walk0 = boom + 400                                # out of the blast, 1.6 px a tick
    walk1 = walk0 + tick((g.x - tx) / 1.6)
    g.walks.append((walk0, walk1, tx - g.x))
    arc = Arc(frames_of(fx["league_jinx_fx"], "e_throw"), throw, x + 6, gy - 10, loop=True, until=land,
              x1=tx, y1=g.y, h=22)
    over.append(arc)
    fx_at("league_jinx_fx", "e_arm", land, tx, g.y, ground=True, loop=False)
    k = 1
    while land + tick(15 * k + 14) < walk1:
        k += 1
    bite = land + tick(15 * k + 14)
    fx_at("league_jinx_fx", "e_trap", land + tick(15), tx, g.y, ground=True, until=bite)
    fx_at("league_jinx_fx", "e_bite", bite, tx, g.y)
    g.flinches.append(bite)
    a("skill2")
    a("idle", max(0.0, bite - t) + 150, loop=True)
    # rooted 78 px away: out of Pow-Pow's reach (52.5 px); still excited, she runs until he is in
    # Fishbones' (64.5 px) and fires two rockets
    to = tx - 63
    a("run", tick((to - x) / 2.6), loop=True, to=to)
    x = to
    for gap in (120, 400):
        start = t
        hit = fly("rocket", start + tick(11), x + 10, gy - 7, g, 4.5, x1=tx)
        fx_at("league_jinx_fx", "rocket_hit", hit, tx, g.y)
        g.flinches.append(hit)
        a("rocket")
        a("idle", gap, loop=True)
    a("idle", 900, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted(foes.values(), key=lambda f: f.y)   # the one further back first
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_jinx_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_jinx_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_jinx_showcase.gif")))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Preview images for Ezreal, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ezreal.py [--out docs/preview]

  league_ezreal_frames.png    every animation, frame by frame, 3x on the arena colour
  league_ezreal_effects.png   every effect animation, 3x
  league_ezreal_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: he runs in, a bolt
                              from the gauntlet, Mystic Shot; with a champion in range Essence Flux goes first,
                              sticks to Darius and marks him, and the Mystic Shot that follows detonates it; two
                              more bolts fill Rising Spell Force (the aura); Darius closes in, Arcane Shift blinks
                              Ezreal away (the flash where he leaves and where he lands) and its homing bolt hits
                              Darius; Trueshot Barrage charges on the gauntlet for a second and its wave sweeps
                              through Darius, who falls, and Garen walking up behind him; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow, Walker  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_ezreal")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ezreal_fx", "league_ezreal_big")}


class Hop(Anim):
    """An animation whose unit moves from x to x1 between moments m0 and m1 (Arcane Shift's hop)."""

    def __init__(self, *args, m0=0.0, m1=0.0, **kw):
        super().__init__(*args, **kw)
        self.m0, self.m1 = m0, m1

    def pos(self, t):
        u = min(1.0, max(0.0, (t - self.m0) / (self.m1 - self.m0)))
        return int(round(self.x + (self.x1 - self.x) * u)), self.y


def showcase(out, z=3, step=40):
    ez = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 300, 130
    gy = 92                                            # his pivot row
    ex = 96
    d = Walker(load(os.path.join(LEAGUE, "champions", "league_darius")), ex + 55, gy)    # 55 px: his range
    g = Walker(load(os.path.join(LEAGUE, "champions", "league_garen")), 330, gy - 4)     # walks in behind him
    body, under, over = [], [], []
    t = 0.0

    def muzzle():
        return ex + 14, gy - 3                          # the gauntlet's front when he shoots

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(ez, tag), t, ex, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, px, py, until=None, x1=None, y1=None, loop=None, z_under=False):
        an = Anim(frames_of(fx[sprite], tag), at, px, py, loop=(until is not None) if loop is None else loop,
                  until=until, x1=x1, y1=y1)
        (under if z_under else over).append(an)
        return an

    def fly(tag, at, speed, foe=None, hits=(), sprite="league_ezreal_fx"):
        """A projectile from the gauntlet at `speed` px a tick onto `foe`'s chest, its hit pictures on arrival."""
        foe = foe or d
        x0, y0 = muzzle()
        fx_, fy = foe.pos(at)
        arrive = at + tick(max(1.0, (fx_ - 4 - x0) / speed))
        fx_at(sprite, tag, at, x0, y0, until=arrive, x1=fx_ - 4, y1=fy - 6)
        for h in hits:
            fx_at("league_ezreal_fx", h, arrive, *foe.pos(arrive))
        foe.flinches.append(arrive)
        return arrive

    # he runs in while Garen walks up far behind Darius
    body.append(Anim(frames_of(ez, "run"), 0.0, ex - 40, gy, loop=True, until=1500, x1=ex))
    t = 1500.0
    g.walks.append((0.0, 6000, 222 - 330))
    a("idle", 300, loop=True)
    # a bolt from the gauntlet (tick 7), one attack a second: Rising Spell Force 1
    fly("bolt", t + tick(7), 5.0, hits=("hit",))
    a("attack")
    a("idle", tick(60) - tick(26), loop=True)
    # Mystic Shot (tick 1 + 7): Rising Spell Force 2
    fly("q_bolt", t + tick(8), 8.0, hits=("q_hit",))
    a("skill")
    a("idle", 400, loop=True)
    # Essence Flux first (tick 1 + 10): it sticks and marks Darius; the Mystic Shot (1 + 21) detonates the mark
    start = t
    stuck = fly("w_orb", start + tick(11), 9.0, hits=("w_stick",))
    boom = fly("q_bolt", start + tick(22), 8.0, hits=("q_hit", "w_boom"))
    over.append(Anim(frames_of(fx["league_ezreal_fx"], "w_mark"), stuck + 250, *d.pos(stuck), loop=True, until=boom))
    a("skill_w", tick(26))
    a("idle", tick(60) - tick(26), loop=True)
    # two more bolts: Rising Spell Force 3, 4, and 5 with its aura
    for _ in range(2):
        fly("bolt", t + tick(7), 5.0, hits=("hit",))
        a("attack")
        a("idle", tick(60) - tick(26), loop=True)
    full = t - tick(60) + tick(26) + tick(7) + tick(8)
    # Darius closes in to 30 px: Arcane Shift hops Ezreal 40 px away from him (tick 3 to 8), the homing bolt at 14
    d.walks.append((t - 700, t, -25))
    start = t
    fx_at("league_ezreal_fx", "e_depart", start + tick(3), ex, gy)
    body.append(Hop(frames_of(ez, "skill2"), start, ex, gy, x1=ex - 40, m0=start + tick(3), m1=start + tick(8)))
    ex -= 40
    fx_at("league_ezreal_fx", "e_arrive", start + tick(8), ex, gy)
    t = body[-1].until
    fly("e_bolt", start + tick(14), 6.0, hits=("e_hit",))
    a("idle", 900, loop=True)
    # Trueshot Barrage: the charge on the gauntlet from tick 2, the wave at tick 58, 3.5 px a tick to the right
    start = t
    fx_at("league_ezreal_big", "r_charge", start + tick(2), ex, gy)
    launch = start + tick(58)
    x_end = W + 60
    fx_at("league_ezreal_big", "r_wave", launch, ex, gy - 8, until=launch + tick((x_end - ex) / 3.5), x1=x_end)
    for foe in (d, g):
        fx_, _ = foe.pos(launch)
        hit = launch + tick(max(1.0, (fx_ - 18 - ex) / 3.5))
        fx_at("league_ezreal_fx", "r_hit", hit, *foe.pos(hit))
        if foe is d:
            d.death = hit
        else:
            foe.flinches.append(hit)
    a("ult")
    a("idle", 1400, loop=True)
    end = t
    aura = Follow(frames_of(fx["league_ezreal_fx"], "rsf_max"), full, ex, gy, loop=True, until=end, on=body)
    over.insert(0, aura)

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
                            os.path.join(args.out, "league_ezreal_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_ezreal_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ezreal_showcase.gif")))


if __name__ == "__main__":
    main()

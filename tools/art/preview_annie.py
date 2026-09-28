#!/usr/bin/env python3
"""Preview images for Annie, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_annie.py [--out docs/preview]

  league_annie_frames.png    every animation, frame by frame, 3x on the arena colour
  league_annie_effects.png   every effect animation, 3x
  league_annie_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Annie runs in
                             with Pyromania's stun ready (she spawns with it), summons Tibbers onto Garen as
                             he walks up to Darius - he crashes down beside Garen, both are stunned, and he
                             keeps to Garen's side in his ring of fire, burning round him, as Garen backs off
                             and comes back; Disintegrate's fireball bursts on Darius, her small fireballs
                             follow, Incinerate's cone of fire burns him while Molten Shield wraps her, and
                             the next Disintegrate is her fourth spell: the glow is back. Tibbers vanishes in
                             smoke and Darius falls; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_annie")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_annie_fx", "league_annie_big")}


class Held(Walker):
    """A foe that can also be held still (stunned: its first hit frame)."""

    def __init__(self, sp, x, y):
        super().__init__(sp, x, y)
        self.holds = []

    def frame(self, t):
        if self.death is None or t < self.death:
            for t0, t1 in self.holds:
                if t0 <= t < t1:
                    return self.flip(self.hit[0][0])
        return super().frame(t)


class OnFoe(Anim):
    """A view played on a unit with is_follow: drawn on the unit's pivot wherever it walks."""

    def __init__(self, fr, t0, foe, z=-1):
        super().__init__(fr, t0, 0, 0, z=z)
        self.foe = foe

    def pos(self, t):
        return self.foe.pos(t)


def showcase(out, z=3, step=40):
    annie = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 300, 150
    gy = 112                                          # Annie's pivot row: Tibbers stands 44 px tall
    x = 44
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 100, gy)          # 56 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 270, gy - 6)       # walking in
    body, under, over, glow = [], [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(annie, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(fx[sprite], tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def fireball(start, tag, hit, speed, fire=12, foe=None):
        """A fireball leaves her hand `fire` ticks into the action and homes on the foe."""
        foe = foe or d
        launch = start + tick(fire)
        x0, y0 = x + 8, gy - 12
        fx_, fy = foe.pos(launch)
        arrive = launch + tick(max(1.0, (fx_ - 6 - x0) / speed))
        fx_at("league_annie_fx", tag, launch, x0, y0, until=arrive, x1=fx_ - 6, y1=fy - 4)
        fx_at("league_annie_fx", hit, arrive, *foe.pos(arrive))
        foe.flinches.append(arrive)
        return arrive

    # she runs in with the stun ready: the glow is on from the start
    glow.append([0.0, None])
    run_in = Anim(frames_of(annie, "run"), 0.0, x - 36, gy, loop=True, until=1200, x1=x)
    body.append(run_in)
    t = run_in.until
    # Garen walks up to 28 px beyond Darius
    g.walks.append((0.0, 2100, 128 - g.x))
    a("idle", 700, loop=True)
    # Summon on Garen: cast on tick 12, Tibbers lands beside him 6 ticks later: 130 + 70% AP round Garen and
    # both stunned (the stun was ready); then he keeps to Garen's side for 6 s, burning round him every second
    # while Garen backs off and comes back (his views follow the unit they are played on)
    start = t
    cast = start + tick(12)
    land = cast + tick(6)
    big = fx["league_annie_big"]
    under.append(OnFoe(frames_of(big, "tibbers_drop"), cast, g))      # under the units, like in game
    stand = cast + tick(24)                         # after the 400 ms drop picture
    g.walks.append((land + 1100, land + 2700, 70))
    g.walks.append((land + 3500, land + 4700, -60))
    for i in range(6):
        under.append(OnFoe(frames_of(big, "r_ring"), stand + tick(60 * i), g, z=-2))
        under.append(OnFoe(frames_of(big, "tibbers"), stand + tick(60 * i), g))
    vanish = stand + tick(360)
    fx_at("league_annie_big", "tibbers_vanish", vanish, *g.pos(vanish), ground=True)   # it stays where it starts

    def near(foe, when):                            # inside the 30000 radius round Garen (+ a body)
        return abs(foe.pos(when)[0] - g.pos(when)[0]) <= 36

    for foe in (d, g):
        fx_at("league_annie_fx", "burn", land, *foe.pos(land))
        fx_at("league_annie_fx", "stun", land, *foe.pos(land), until=land + tick(45), loop=True)
        foe.holds.append((land, land + tick(45)))
        foe.flinches.append(land)
        for k in range(6):                            # the burn every second, round Garen wherever he is
            burn = stand + tick(60 * k + 1)
            if near(foe, burn):
                fx_at("league_annie_fx", "burn", burn, *foe.pos(burn))
                foe.flinches.append(burn)
    glow[-1][1] = land + tick(1)
    a("ult")
    a("idle", 200, loop=True)
    # Disintegrate: the fireball on tick 12 at 5 px a tick bursts on Darius (her first spell after the stun)
    fireball(t, "q_ball", "q_hit", 5.0)
    a("skill")
    a("idle", 150, loop=True)
    # two small fireballs (the attack's cooldown, 90 ticks)
    for _ in range(2):
        fireball(t, "bolt", "hit", 6.0)
        a("attack")
        a("idle", tick(90) - tick(26), loop=True)
    # Incinerate + Molten Shield: the cone appears on tick 8 and burns on tick 12; the shield for 3 s
    start = t
    fx_at("league_annie_big", "w_cone", start + tick(8), x + 28, gy - 8, until=start + tick(8 + 24), loop=False)
    burn = start + tick(12)
    fx_at("league_annie_fx", "burn", burn, *d.pos(burn))
    d.flinches.append(burn)
    over.append(Follow(frames_of(fx["league_annie_fx"], "e_shield"), start + tick(8), x, gy, loop=True,
                       until=start + tick(8 + 180), on=body))
    a("skill2")
    a("idle", 200, loop=True)
    fireball(t, "bolt", "hit", 6.0)
    a("attack")
    a("idle", tick(90) - tick(26), loop=True)
    # the second Disintegrate is her fourth spell (Q, W and E, Q): the stun is ready again
    ready = t + tick(12)
    fireball(t, "q_ball", "q_hit", 5.0)
    glow.append([ready, None])
    a("skill")
    a("idle", max(300.0, vanish + 700 - t), loop=True)
    d.death = vanish - 400
    end = t
    for t0, t1 in glow:
        over.append(Follow(frames_of(fx["league_annie_fx"], "pyro_ready"), t0, x, gy, loop=True,
                           until=t1 if t1 is not None else end, on=body))

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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_annie_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_annie_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_annie_showcase.gif")))


if __name__ == "__main__":
    main()

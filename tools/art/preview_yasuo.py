#!/usr/bin/env python3
"""Preview images for Yasuo, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_yasuo.py [--out docs/preview]

  league_yasuo_frames.png    every animation, frame by frame, 3x on the arena colour
  league_yasuo_effects.png   every effect animation, 3x
  league_yasuo_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Yasuo
                             runs in, his first cut raises the wind shield and the wind wall
                             (Way of the Wanderer), two Steel Tempest thrusts gather the storm, the
                             whirlwind knocks both up, Last Breath blinks to them and cuts them in
                             the air (Darius falls), Sweeping Blade dashes through Garen and a
                             spinning EQ follows, 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_yasuo")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_yasuo_fx", "league_yasuo_big")}


def showcase(out, z=3, step=40):
    yas = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 250, 130
    gy = 90                                           # Yasuo's pivot row
    x0, sx = 30, 110                                  # he runs in from x0 to sx (melee range of Darius)
    foes = {
        "darius": Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), 136, gy),
        "garen": Foe(load(os.path.join(LEAGUE, "champions", "league_garen")), 150, gy - 9),
    }
    d, g = foes["darius"], foes["garen"]
    body, under, over = [], [], []
    t = 0.0
    x = sx

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(yas, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, px, py=gy, ground=False, until=None, x1=None):
        an = Anim(frames_of(fx[sprite], tag), at, px, py, z=-1 if ground else 1, loop=until is not None,
                  until=until, x1=x1)
        (under if ground else over).append(an)
        return an

    # run in (move speed 1100, about 1.1 px a tick)
    a("run", tick((sx - x0) / 1.1), loop=True, at=x0, to=sx)
    a("idle", 200, loop=True)
    # a cut at tick 11; the first one of the fight raises the wind shield and a gust of wall in front
    # of him (both seen for 1 s; the shield holds 2 s, the wall's buff 4 s)
    start = t
    cut = start + tick(11)
    fx_at("league_yasuo_fx", "shield", cut, x, until=cut + 1000)
    fx_at("league_yasuo_big", "wall", cut, x + 4, until=cut + 1000)
    fx_at("league_yasuo_fx", "hit", cut, d.x, d.y)
    d.flinches.append(cut)
    a("attack")
    a("idle", 150, loop=True)
    # two Steel Tempest thrusts: the 45 px spear shows from tick 1, hits at tick 8; the second one
    # gathers the storm (the ribbons stay on him until the whirlwind)
    for k in range(2):
        start = t
        fx_at("league_yasuo_big", "q_thrust", start + tick(1), x + 22)
        fx_at("league_yasuo_fx", "q_hit", start + tick(8), d.x, d.y)
        d.flinches.append(start + tick(8))
        a("skill")
        a("idle", 200, loop=True)
    ready = t - 200
    # the whirlwind flies 2.5 px a tick and knocks up whoever it passes, for 1 s
    start = t
    fx_at("league_yasuo_fx", "q_ready", ready, x, until=start + tick(4))
    launch = start + tick(4)
    fly_end = launch + tick(80 / 2.5)
    fx_at("league_yasuo_big", "tornado", launch, x + 8, until=fly_end, x1=x + 88)
    ups = {}
    for f in (d, g):
        up = launch + tick((f.x - x - 8) / 2.5)
        ups[id(f)] = up
        fx_at("league_yasuo_fx", "knockup", up, f.x, f.y)
    a("q3")
    # Last Breath: he blinks next to Darius while both are in the air, re-lifts them and cuts at tick 24
    start = t
    x = d.x - 12
    land = start + tick(24)
    for f in (d, g):
        f.hops.append((ups[id(f)], land + 250, 16))
    for f in (d, g):
        fx_at("league_yasuo_big", "r_slash", start + tick(4), *f.pos(start + tick(4)))
    d.death = land + 260
    g.flinches.append(land + 260)
    a("ult")
    a("idle", 250, loop=True)
    # Sweeping Blade through Garen (3.5 px a tick) to 15 px behind him, then EQ, the spin, at once
    start = t
    to = g.x + 15
    dash = tick((to - x) / 3.5)
    fx_at("league_yasuo_fx", "e_hit", start + tick(2) + dash / 2, g.x, g.y)
    g.flinches.append(start + tick(2) + dash / 2)
    a("skill2", tick(2) + dash, to=to)
    x = to
    start = t
    fx_at("league_yasuo_big", "eq", start + tick(2), x)
    fx_at("league_yasuo_fx", "q_hit", start + tick(4), g.x, g.y)
    g.flinches.append(start + tick(4))
    a("eq")
    a("idle", 1500, loop=True)
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_yasuo_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_yasuo_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_yasuo_showcase.gif")))


if __name__ == "__main__":
    main()

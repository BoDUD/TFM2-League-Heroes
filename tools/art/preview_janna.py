#!/usr/bin/env python3
"""Preview images for Janna, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_janna.py [--out docs/preview]

  league_janna_frames.png    every animation, frame by frame, 3x on the arena colour
  league_janna_effects.png   every effect animation, 3x
  league_janna_showcase.gif  a scripted fight with Ashe behind her against Darius and Garen, timed like the kit: Janna
                             floats in, Zephyr flies at Darius while Eye of the Storm wraps Ashe (the shield's
                             forming, its loop for 4 s, its breaking up), two gusts of wind, Howling Gale's
                             vortex knocks up Darius and Garen as Garen walks in, and when both dive at her,
                             Monsoon blows them away and she channels for 3 s, healing herself and Ashe every
                             second; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_janna")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_janna_fx", "league_janna_big")}


def showcase(out, z=3, step=40):
    janna = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_janna_fx"], fx["league_janna_big"]
    W, H = 300, 150
    gy = 104                                          # the pivot row
    x = 70
    ashe_x = 38                                       # Ashe behind her, 32 px: inside Monsoon's 40000
    ashe = Anim(frames_of(load(os.path.join(LEAGUE, "champions", "league_ashe")), "idle"), 0.0, ashe_x, gy + 4,
                loop=True, until=None)
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 132, gy)          # 62 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 280, gy - 8)       # walking in
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t
        an = Anim(frames_of(janna, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def shot(start, tag, hit, speed, fire, foe):
        """A projectile leaves her staff `fire` ticks into the action and homes on the foe."""
        launch = start + tick(fire)
        x0, y0 = x + 10, gy - 8
        fx_, fy = foe.pos(launch)
        arrive = launch + tick(max(1.0, (fx_ - 6 - x0) / speed))
        fx_at(small, tag, launch, x0, y0, until=arrive, x1=fx_ - 6, y1=fy - 6)
        over.append(OnFoe(frames_of(small, hit), arrive, foe, z=1))
        foe.flinches.append(arrive)
        return arrive

    def storm_on(px, py, t0, t1):
        """The shield's picture in three phases: forming, the loop while it holds, breaking up."""
        pre = frames_of(small, "e_cast")
        loop_start = t0 + sum(ms for _, ms in pre)
        fx_at(small, "e_cast", t0, px, py)
        fx_at(small, "storm", loop_start, px, py, until=t1)
        fx_at(small, "storm_end", t1, px, py)

    # she floats in; Garen walks up behind Darius
    run_in = Anim(frames_of(janna, "run"), 0.0, x - 40, gy, loop=True, until=1000, x1=x)
    body.append(run_in)
    t = run_in.until
    g.walks.append((600.0, 2600.0, 152 - g.x))
    a("idle", 400, loop=True)
    # Eye of the Storm + Zephyr: on tick 11 the gust flies at Darius, the storm wraps Ashe for 4 s
    start = t
    shot(start, "w_gust", "w_hit", 5.0, 11, d)
    storm_on(ashe_x, gy + 4, start + tick(11), start + tick(11 + 240))
    a("skill2")
    a("idle", 200, loop=True)
    for _ in range(2):                                # the attack's cooldown, 90 ticks
        shot(t, "bolt", "hit", 5.0, 13, d)
        a("attack")
        a("idle", tick(90) - tick(30), loop=True)
    # Howling Gale: on tick 13 the vortex rolls out at 2.5 px a tick for 85 px, knocking up both
    start = t
    launch = start + tick(13)
    x0, x1 = x + 10, x + 10 + 85
    fx_at(big, "tornado", launch, x0, gy - 2, until=launch + tick(85 / 2.5), x1=x1)
    for foe in (d, g):
        fx_, _ = foe.pos(launch)
        if x0 <= fx_ <= x1 + 8:
            hit = launch + tick((fx_ - x0) / 2.5)
            foe.hops.append((hit, hit + tick(45), 10))
            over.append(OnFoe(frames_of(small, "knockup"), hit, foe, z=1))
    a("skill")
    a("idle", 700, loop=True)
    # both dive at her
    for foe, to in ((d, x + 22), (g, x + 30)):
        foe.walks.append((t, t + 800, to - foe.pos(t)[0]))
    a("idle", 900, loop=True)
    # Monsoon: the wind-up, on tick 20 the blast pushes both away 30 px and the channel starts; heal pulses on
    # ticks 35, 95, 155 and 215, each with the storm on the ground under her
    start = t
    blast = start + tick(20)
    fx_at(big, "r_gale", blast, x, gy, ground=True)
    for foe in (d, g):
        foe.slides.append((blast, blast + tick(15), 30))
    body.append(Anim(frames_of(janna, "ult"), start, x, gy, until=blast))
    body.append(Anim(frames_of(janna, "ult_loop"), blast, x, gy, loop=True, until=blast + tick(200)))
    for k in range(4):
        pulse = start + tick(35 + 60 * k)
        fx_at(big, "r_storm", pulse, x, gy, ground=True)
        fx_at(small, "r_heal", pulse, x, gy)
        fx_at(small, "r_heal", pulse, ashe_x, gy + 4)
    t = blast + tick(200)
    a("idle", 700, loop=True)
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt)),
                 (ashe.y, ashe.frame(tt), ashe.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((gy, f, an.pos(tt)))
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
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_janna_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_janna_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_janna_showcase.gif")))


if __name__ == "__main__":
    main()

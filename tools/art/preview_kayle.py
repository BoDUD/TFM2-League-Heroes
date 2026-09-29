#!/usr/bin/env python3
"""Preview images for Kayle, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_kayle.py [--out docs/preview]

  league_kayle_frames.png    every animation, frame by frame, 3x on the arena colour
  league_kayle_effects.png   every effect animation, 3x
  league_kayle_showcase.gif  a scripted fight against Darius, timed like the kit: Kayle flies in and cuts him
                             three times with her sword (Zealous stacking up: at five she is Exalted and burns);
                             Radiant Blast's sword flies into him and bursts; at level 5 she ascends (Arisen) and
                             shoots starfire from range; at level 8 (Aflame) every Exalted attack also sends a
                             wave of fire through him; Starfire Spellblade strikes and explodes round him while
                             Celestial Blessing heals her; Divine Judgment makes her immune for 2.5 s, and the
                             swords fall round her as Darius closes in, and he falls; 3x
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
from preview_yone import Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_kayle")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_kayle_fx", "league_kayle_big")}


def showcase(out, z=3, step=40):
    kayle = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_kayle_fx"], fx["league_kayle_big"]
    W, H = 330, 150
    gy = 100                                          # the pivot row
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 150, gy)
    body, under, over = [], [], []
    t = 0.0
    x = 40

    def a(tag, dur=None, loop=False, at=None, way=None):
        nonlocal t
        an = Path(frames_of(kayle, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def on_kayle(sp, tag, t0, until=None, loop=False, z=1):
        over.append(Follow(frames_of(sp, tag), t0, x, gy, loop=loop, until=until, on=body, z=z))

    def hit(when, tag="hit", sp=None):
        over.append(OnFoe(frames_of(sp or small, tag), when, d, z=1))
        d.flinches.append(when)

    def shoot(start, tag, hit_tag, speed, fire=10, dy=-10):
        """A projectile leaves her `fire` ticks into the action and flies to Darius at `speed` px a tick."""
        launch = start + tick(fire)
        x0 = x + 8
        fx_, fy = d.pos(launch)
        arrive = launch + tick(max(1.0, (fx_ - 6 - x0) / speed))
        fx_at(small, tag, launch, x0, gy + dy, until=arrive, x1=fx_ - 6, y1=fy + dy)
        if hit_tag:
            hit(arrive, hit_tag)
        return arrive

    # she flies in (her move speed 1000: 60 px a second), League's own glide
    a("run", 1200, loop=True, way=[(0, x), (1200, 118)])
    x = 118
    # three sword cuts (the hit 10 ticks in, an attack every 65): Zealous, and at five stacks Exalted
    for k in range(3):
        start = t
        hit(start + tick(10), "hit")
        a("attack_melee", tick(22))
        a("idle", tick(43), loop=True)
    exalted = t
    on_kayle(small, "exalted", exalted, until=exalted + 1800, loop=True, z=0)
    # Radiant Blast: the sword leaves 12 ticks in at 9 px a tick, stops on Darius and bursts
    start = t
    boom = shoot(start, "q_sword", None, 9, fire=12, dy=-9)
    fx_at(big, "q_blast", boom, d.pos(boom)[0], gy + 6, ground=True)
    hit(boom, "bolt_hit")
    a("skill", tick(24))
    a("idle", 300, loop=True)
    # level 5: Arisen - the ascent, then she keeps her distance and shoots starfire (7 px a tick)
    on_kayle(big, "ascend", t)
    a("idle", 800, loop=True)
    a("run", 500, loop=True, way=[(t, x), (t + 500, 92)])
    x = 92
    for k in range(2):
        start = t
        shoot(start, "bolt", "bolt_hit", 7)
        a("attack", tick(22))
        a("idle", tick(43), loop=True)
    # level 8: Aflame - the ascent again, and every Exalted attack also sends a wave through him
    on_kayle(big, "ascend", t)
    a("idle", 800, loop=True)
    on_kayle(small, "exalted", t, until=t + 5200, loop=True, z=0)
    for k in range(2):
        start = t
        shoot(start, "bolt", "bolt_hit", 7)
        launch = start + tick(10)
        fx_at(small, "wave", launch, x + 8, gy - 8, until=launch + tick(70 / 7), x1=x + 78)
        a("attack", tick(22))
        a("idle", tick(43), loop=True)
    # Starfire Spellblade (8 px a tick): the strike, the blast round him (level 8), Celestial Blessing on her
    start = t
    arrive = shoot(start, "e_bolt", "e_hit", 8, dy=-9)
    fx_at(big, "e_blast", arrive, d.pos(arrive)[0], gy + 4, ground=True)
    on_kayle(small, "w_heal", start + tick(10))
    a("skill2", tick(24))
    a("idle", 400, loop=True)
    # Divine Judgment: immune for 150 ticks, Darius walks up to her, then the swords fall round her
    start = t
    guard = start + tick(20)
    on_kayle(big, "r_invuln", guard, until=guard + tick(150), loop=True, z=2)
    d.walks.append((start + 200, start + 1200, -36))
    a("ult", tick(44))
    a("idle", guard + tick(150) - t, loop=True)
    fall = guard + tick(150)
    fx_at(big, "r_blades", fall, x, gy + 4, ground=False)
    for k in (3, 4, 5):
        d.flinches.append(fall + 70 * k)
    d.death = fall + 450
    a("idle", 1800, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (int(px) - f.width // 2, int(py) - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
        units = [(d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((gy, f, an.pos(tt)))
                break
        for _, f, p in sorted(units, key=lambda u: u[0]):
            if f is not None:
                place(img, f, *p)
        for an in sorted(over, key=lambda o: o.z):
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
    q[0].save(T.long_path(out), save_all=True, append_images=q[1:], duration=step, loop=0, optimize=False)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_kayle_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_kayle_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_kayle_showcase.gif")))


if __name__ == "__main__":
    main()

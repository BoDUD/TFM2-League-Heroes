#!/usr/bin/env python3
"""Preview images for Morgana, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_morgana.py [--out docs/preview]

  league_morgana_frames.png    every animation, frame by frame, 3x on the arena colour
  league_morgana_effects.png   every effect animation, 3x
  league_morgana_showcase.gif  a scripted fight against Darius, timed like the kit: Morgana walks up and throws Dark
                               Binding - the orb pierces into him, the shackles hold him 2 s and the Tormented
                               Shadow pool burns under him for 4 s while her shadow bolts hit him; she raises Black
                               Shield round herself as he comes for her; Soul Shackles bursts round her feet and
                               chains him, he drags himself on for 3 s, the chains snap and stun him, and he falls; 3x
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
from preview_yone import OnFoeFor, Path  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_morgana")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_morgana_fx", "league_morgana_big")}


def showcase(out, z=3, step=40):
    morgana = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_morgana_fx"], fx["league_morgana_big"]
    W, H = 250, 150
    gy = 96                                           # the pivot row
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 196, gy)
    body, under, over = [], [], []
    t = 0.0
    x = 40

    def a(tag, dur=None, loop=False, at=None, way=None):
        nonlocal t
        an = Path(frames_of(morgana, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, way=way or ())
        body.append(an)
        t = an.until

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def on_her(tag, t0, until=None, loop=False, z=1):
        over.append(Follow(frames_of(small, tag), t0, x, gy, loop=loop, until=until, on=body, z=z))

    def shoot(start, tag, speed, fire, dy=-10):
        """A projectile leaves her hand `fire` ticks into the action and flies to Darius at `speed` px a tick."""
        launch = start + tick(fire)
        x0 = x + 8
        fx_, fy = d.pos(launch)
        arrive = launch + tick(max(1.0, (fx_ - 6 - x0) / speed))
        fx_at(small, tag, launch, x0, gy + dy, until=arrive, x1=fx_ - 6, y1=fy + dy)
        return arrive

    # she walks up (move speed 1000: 60 px a second)
    a("run", 1000, loop=True, way=[(0, x), (1000, 100)])
    x = 100
    # Dark Binding (80 px, 10 px a tick, 9 ticks in): the orb pierces into him, the shackles hold him 2 s, the
    # pool burns under him 4 s (its damage every half second)
    start = t
    bound = shoot(start, "q_orb", 10, 9, dy=-9)
    over.append(OnFoe(frames_of(small, "q_hit"), bound, d, z=1))
    over.append(OnFoe(frames_of(small, "q_bind"), bound, d, z=2))
    fx_at(big, "w_pool", bound, d.pos(bound)[0], gy, ground=True)
    d.flinches.append(bound)
    for k in range(1, 8):
        d.flinches.append(bound + 500 * k)
    a("skill", tick(34))
    a("idle", 200, loop=True)
    # into bolt range (50 px) and two shadow bolts (5 px a tick, 8 ticks in, one every 90 ticks)
    a("run", 420, loop=True, way=[(t, x), (t + 420, 125)])
    x = 125
    for k in range(2):
        start = t
        arrive = shoot(start, "bolt", 5, 8)
        over.append(OnFoe(frames_of(small, "hit"), arrive, d, z=1))
        d.flinches.append(arrive)
        a("attack", tick(30))
        a("idle", tick(40), loop=True)
    # he is free and comes for her: Black Shield round herself (12 ticks in), held while he closes in, shattering
    free = bound + 2000
    d.walks.append((max(free, t), max(free, t) + 700, -26))
    start = t
    up = start + tick(12)
    on_her("e_shield_in", up)
    in_ms = sum(ms for _, ms in frames_of(small, "e_shield_in"))
    on_her("e_shield", up + in_ms, until=up + in_ms + 1600, loop=True)
    on_her("e_shield_out", up + in_ms + 1600)
    a("skill2", tick(30))
    a("idle", 600, loop=True)
    # Soul Shackles (10 ticks in): the burst round her feet, the chain on him for 3 s while he drags himself on,
    # then the snap and the 1.5 s stun, and he falls
    start = t
    cast = start + tick(10)
    fx_at(big, "r_cast", cast, x, gy, ground=True)
    over.append(OnFoe(frames_of(small, "r_hit"), cast, d, z=1))
    d.flinches.append(cast)
    over.append(OnFoeFor(frames_of(small, "r_chain"), cast, d, cast + 3000, z=1))
    d.walks.append((cast + 300, cast + 2800, -14))
    a("ult", tick(46))
    a("idle", cast + 3000 - t, loop=True)
    snap = cast + 3000
    over.append(OnFoe(frames_of(small, "r_snap"), snap, d, z=2))
    d.holds.append((snap, snap + 1500))
    for k in range(2):
        start = t
        arrive = shoot(start, "bolt", 5, 8)
        over.append(OnFoe(frames_of(small, "hit"), arrive, d, z=1))
        a("attack", tick(30))
        a("idle", tick(30), loop=True)
    d.death = snap + 1500
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_morgana_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[15:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_morgana_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_morgana_showcase.gif")))


if __name__ == "__main__":
    main()

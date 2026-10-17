#!/usr/bin/env python3
"""Preview images for Amumu, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_amumu.py [--out docs/preview]

  league_amumu_frames.png    every animation, frame by frame, 3x on the arena colour
  league_amumu_effects.png   every effect animation, 3x
  league_amumu_showcase.gif  a scripted fight against Darius, Garen and Lux, timed like the kit:
                             Amumu shuffles in, Q Bandage Toss sticks to Darius and pulls him over,
                             Despair starts on landing (a pulse a second, Darius cursed), R Curse of
                             the Sad Mummy wraps all three, E Tantrum, two slams finish Darius, 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_amumu")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_amumu_fx", "league_amumu_big")}


def showcase(out, z=3, step=40):
    amu = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 250, 150
    gy = 100                                          # Amumu's pivot row
    x0, sx = 36, 92                                   # he shuffles in from x0 to sx, then throws
    land = 140                                        # where the bandage pulls him (melee range of Darius)
    foes = {
        "darius": Foe(load(os.path.join(LEAGUE, "champions", "league_darius")), 162, gy),
        "garen": Foe(load(os.path.join(LEAGUE, "champions", "league_garen")), 184, gy - 12),
        "lux": Foe(load(os.path.join(LEAGUE, "champions", "league_lux")), 180, gy + 10),
    }
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, x=None, x1=None):
        nonlocal t
        an = Anim(frames_of(amu, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None, x1=x1)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, x, y=gy, ground=False, until=None, x1=None):
        an = Anim(frames_of(fx[sprite], tag), at, x, y, z=-1 if ground else 1, loop=until is not None,
                  until=until, x1=x1)
        (under if ground else over).append(an)
        return an

    def hit(foe, at, tag="hit"):
        f = foes[foe]
        fx_at("league_amumu_fx", tag, at, f.x, f.y)
        f.flinches.append(at)

    # shuffle in (move speed 1000, about 1 px a tick)
    a("run", tick(sx - x0), loop=True, x=x0, x1=sx)
    a("idle", 150, loop=True, x=sx)
    # Q: the bandage leaves at tick 16, flies 5 px a tick, sticks to Darius (stunned 1 s) and pulls him in
    start = t
    throw = start + tick(16)
    d = foes["darius"]
    fly = tick((d.x - 8 - (sx + 8)) / 5.0)
    fx_at("league_amumu_fx", "q_bandage", throw, sx + 8, gy - 4, until=throw + fly, x1=d.x - 8)
    stuck = throw + fly
    fx_at("league_amumu_fx", "q_wrap", stuck, d.x, d.y)
    a("skill", stuck - start, x=sx)
    pull = tick((land - sx) / 4.0)                    # 4000 a tick
    a("q_pull", pull, loop=True, x=sx, x1=land)
    landed = t
    # Despair: a pulse a second from the landing on; Darius stands inside it and stays cursed
    for k in range(7):
        pulse = landed + 1000 * k
        fx_at("league_amumu_fx", "despair", pulse, land, ground=True)
        if pulse < landed + 2600:
            fx_at("league_amumu_fx", "curse", pulse, d.x, d.y, until=pulse + 1000)
    a("idle", 250, loop=True, x=land)
    # R: the bandages burst out at tick 18 and wrap all three for 1.5 s, cursed for 3 s
    start = t
    burst = start + tick(18)
    fx_at("league_amumu_big", "r_burst", burst, land)
    for f in foes.values():
        fx_at("league_amumu_fx", "r_wrap", burst, f.x, f.y)
        if f is not d:
            fx_at("league_amumu_fx", "curse", burst, f.x, f.y, until=burst + 3000)
    fx_at("league_amumu_fx", "curse", burst + 1000, d.x, d.y, until=burst + 3000)
    a("ult", x=land)
    a("idle", 150, loop=True, x=land)
    # E: the stomp at tick 20, Darius and Garen inside the ring
    start = t
    stomp = start + tick(20)
    fx_at("league_amumu_big", "e_tantrum", stomp, land)
    hit("darius", stomp)
    hit("garen", stomp)
    a("skill2", x=land)
    a("idle", 100, loop=True, x=land)
    # two slams, the second one finishes Darius
    for k in range(2):
        start = t
        slam = start + tick(15)
        hit("darius", slam)
        if k == 1:
            d.death = slam + 60
        a("attack", x=land)
        a("idle", 120, loop=True, x=land)
    a("idle", 1400, loop=True, x=land)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted(foes.values(), key=lambda f: f.y)   # the ones further back first
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_amumu_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_amumu_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_amumu_showcase.gif")))


if __name__ == "__main__":
    main()

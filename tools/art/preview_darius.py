#!/usr/bin/env python3
"""Preview images for Darius, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_darius.py [--out docs/preview]

  league_darius_frames.png    every animation, frame by frame, 3x on the arena colour
  league_darius_effects.png   every effect animation, 3x
  league_darius_showcase.gif  a scripted fight against Garen, timed like the kit: Darius runs in, E
                              Apprehend hooks Garen in (Crippling Strike ready at his feet), the
                              empowered strike, three axe blows and Q Decimate stack Hemorrhage to
                              Noxian Might, and R Noxian Guillotine executes him, 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_darius")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_darius_fx", "league_darius_big")}


def showcase(out, z=3, step=40):
    dar = load(CHAMP)
    garen = load(os.path.join(LEAGUE, "champions", "league_garen"))
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 240, 150
    gy = 118                                          # pivot row (the Guillotine rises ~110 px)
    sx = 72                                           # Darius
    foe = Foe(garen, sx + 44, gy)                     # inside E's 46000, outside the 25000 attack range
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, x0=None, x1=None):
        nonlocal t
        an = Anim(frames_of(dar, tag), t, sx if x0 is None else x0, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=x1)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, x, ground=False, until=None):
        (under if ground else over).append(Anim(frames_of(fx[sprite], tag), at, x, gy, z=-1 if ground else 1,
                                               loop=until is not None, until=until))

    def blow(at, tag="hit"):
        fx_at("league_darius_fx", tag, at, foe_x())
        fx_at("league_darius_fx", "bleed", at, foe_x())
        foe.flinches.append(at)

    def foe_x():
        return foe.pos(t)[0]

    # run in (move_speed 1000 ~ 1 px a tick)
    a("run", tick(44), loop=True, x0=sx - 44, x1=sx)
    a("idle", 250, loop=True)
    # E: the hook sweeps out at tick 12 and drags Garen in at 3500 a tick; Crippling Strike is ready
    start = t
    a("skill2")
    hook = start + tick(12)
    fx_at("league_darius_big", "e_sweep", hook, sx)
    fx_at("league_darius_fx", "e_hook", hook, foe.x)
    pulled = sx + 22
    foe.slides.append((hook, hook + tick((foe.x - pulled) / 3.5), pulled - foe.x))
    a("idle", 200, loop=True)
    # W: the next basic attack is the low crippling sweep (w_attack), the hit at tick 16
    start = t
    a("w_attack")
    hit = start + tick(16)
    fx_at("league_darius_fx", "w_ready", hook, sx, ground=True, until=hit)
    blow(hit, "w_hit")
    a("idle", 200, loop=True)
    # three basic attacks, the axe lands at tick 12
    for _ in range(3):
        start = t
        a("attack")
        blow(start + tick(12))
        a("idle", 150, loop=True)
    # Q: the blade sweeps round at tick 26 - the fifth hit: Noxian Might, a pulse a second for 5 s
    start = t
    a("skill")
    spin = start + tick(26)
    fx_at("league_darius_big", "q_spin", spin, sx)
    blow(spin)
    fx_at("league_darius_fx", "q_heal", spin, sx)
    for k in range(5):
        fx_at("league_darius_fx", "might", spin + tick(60 * k), sx, ground=True)
    a("idle", 300, loop=True)
    # R: the axe comes down at tick 22 and executes him
    start = t
    a("ult")
    slam = start + tick(22)
    fx_at("league_darius_big", "r_impact", slam, foe_x())
    foe.death = slam
    a("idle", 1500, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    while tt < end:
        img = Image.new("RGBA", (W, H), ARENA)
        for an in under:                              # ground effects and the aura behind the units
            f = an.frame(tt)
            if f is not None:
                place(img, f, *an.pos(tt))
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_darius_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[14:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_darius_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_darius_showcase.gif")))


if __name__ == "__main__":
    main()

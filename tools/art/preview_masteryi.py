#!/usr/bin/env python3
"""Preview images for Master Yi, built from the exported game sprites (so they also prove the sheets
load).

    python tools/art/preview_masteryi.py [--out docs/preview]

  league_masteryi_frames.png    every animation, frame by frame, 3x on the arena colour
  league_masteryi_effects.png   every effect animation, 3x
  league_masteryi_showcase.gif  a scripted fight against Darius, Garen and Ashe, timed like the kit: Alpha
                                Strike blinks him onto Darius and on to the others, four strikes 0.2 s apart,
                                and back beside Darius; he meditates (the lotus and the rising rings) and his
                                blade turns to Wuju Style (the golden wisps, true damage sparks on every hit);
                                his basic attacks, every fourth a Double Strike; then Highlander: the burst,
                                the speed aura under him, and faster attacks until Darius falls; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow  # noqa: E402
from preview_leona import Held  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_masteryi")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_masteryi_fx", "league_masteryi_big")}


def showcase(out, z=3, step=40):
    yi = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 300, 150
    gy = 104                                          # his pivot row: the raised sword stands 45 px over it
    x = 40
    foes = {
        "darius": Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 112, gy),    # 72 px: Alpha Strike range
        "garen": Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 148, gy - 14),  # within 35 px of Darius
        "ashe": Held(load(os.path.join(LEAGUE, "champions", "league_ashe")), 176, gy + 6),
    }
    d, g, s = foes["darius"], foes["garen"], foes["ashe"]
    body, under, over = [], [], []
    t = 0.0

    def a(tag, dur=None, loop=False, speed=1.0):
        nonlocal t
        fr = frames_of(yi, tag)
        if speed != 1.0:
            fr = [(f, ms / speed) for f, ms in fr]
        an = Anim(fr, t, x, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, when, px, py=gy, ground=False, until=None, loop=None):
        an = Anim(frames_of(fx[sprite], tag), when, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until)
        (under if ground else over).append(an)
        return an

    def on_yi(sprite, tag, when, ground=False):
        an = Follow(frames_of(fx[sprite], tag), when, x, gy, on=body)
        (under if ground else over).append(an)
        return an

    wuju_until = [0.0]

    def strike_hit(foe, when, view="hit"):
        fx_at("league_masteryi_fx", view, when, foe.x, foe.y)
        if when < wuju_until[0]:
            fx_at("league_masteryi_fx", "e_hit", when, foe.x, foe.y)
        foe.flinches.append(when)

    a("idle", 500, loop=True)
    # Alpha Strike, cast on Darius 72 px away: the effects start on tick 2 - he vanishes where he stood,
    # blinks onto Darius (strike 1), then onto a random foe near him every 12 ticks (Garen, Ashe, Darius),
    # banished between the strikes, and back beside Darius on tick 48, where he reappears
    start = t
    fx_at("league_masteryi_fx", "q_vanish", start + tick(2), x, gy)
    body.append(Anim(frames_of(yi, "skill")[:1], start, x, gy, until=start + tick(2)))
    for k, foe in enumerate((d, g, s, d)):
        when = start + tick(2 + 12 * k)
        body.append(Anim(frames_of(yi, "skill"), when, foe.x - 12, foe.y, until=when + tick(12)))
        fx_at("league_masteryi_fx", "q_hit", when, foe.x, foe.y)
        foe.flinches.append(when)
    x = d.x - 24
    back = start + tick(48)
    fx_at("league_masteryi_fx", "q_vanish", back, x, gy)
    t = back
    a("idle", 300, loop=True)
    # Meditate (0.75 s: the lotus and the rising rings), then Wuju Style for 5 s: the golden wisps once a
    # second, true damage sparks on every hit; the attack after it is a Double Strike
    start = t
    on_yi("league_masteryi_big", "w_aura", start, ground=True)
    a("skill2")
    wuju_until[0] = t + 5000
    for k in range(5):
        on_yi("league_masteryi_fx", "wuju", t + 1000 * k)
    double_next = True
    stacks = 0

    def attacks(until, speed=1.0):
        """Basic attacks on Darius, one every 48 ticks (hit on tick 12); the fourth - or the first after the
        meditation - is a Double Strike: the swing up to its hit, then the second slash (attack2, 16 ticks)
        with its hit 8 ticks later."""
        nonlocal t, double_next, stacks
        cycle = tick(48) / speed
        while t + cycle < until:
            start = t
            hit = start + tick(12) / speed
            strike_hit(d, hit)
            if double_next or stacks == 3:
                body.append(Anim(frames_of(yi, "attack")[:3], start, x, gy, until=hit))
                body.append(Anim(frames_of(yi, "attack2"), hit, x, gy))
                strike_hit(d, hit + tick(8), "ds_hit")
                double_next, stacks = False, 0
                t = hit + tick(16)
            else:
                stacks += 1
                a("attack", speed=speed)
            a("idle", max(0.0, start + cycle - t), loop=True)

    attacks(wuju_until[0] - 600)
    a("idle", 200, loop=True)
    # Highlander: the burst, the speed aura under him once a second for 7 s, 45% faster attacks
    start = t
    on_yi("league_masteryi_big", "r_cast", start + tick(6))
    for k in range(7):
        on_yi("league_masteryi_big", "highlander", start + tick(6) + 1000 * k, ground=True)
    a("ult")
    attacks(start + 3600, speed=1.45)
    d.death = t
    a("idle", 1400, loop=True)
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
        for an in reversed(body):                         # the latest body animation playing wins
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_masteryi_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[16:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_masteryi_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_masteryi_showcase.gif")))


if __name__ == "__main__":
    main()

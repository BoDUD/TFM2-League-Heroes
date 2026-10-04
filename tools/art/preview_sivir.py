#!/usr/bin/env python3
"""Preview images for Sivir, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_sivir.py [--out docs/preview]

  league_sivir_frames.png    every animation, frame by frame, 3x on the arena colour
  league_sivir_effects.png   every effect animation, 3x
  league_sivir_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit: Sivir runs in
                             and her first attack starts Ricochet (teal light on the blade at her hip, teal motes
                             round her while it lasts): three faster throws, each blade bouncing from Darius onto
                             Garen; Boomerang Blade flies out through both and back through both into her hand (she
                             waits empty-handed, then catches it); Spell Shield wraps her, blocks a spell and fades;
                             On The Hunt: the shockwave at her feet, the wind ring of the hunt, two more blades and
                             Darius falls - the hunt renews; 3x
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
from preview_jhin import Me  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_sivir")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_sivir_fx", "league_sivir_big")}


def showcase(out, z=3, step=40):
    sivir = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_sivir_fx"], fx["league_sivir_big"]
    W, H = 300, 130
    gy = 86
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 55, gy + 4)     # 55 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 82, gy - 10)     # behind him
    body, under, over = [], [], []
    t = 0.0
    me = Me(x0, gy)
    x = x0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(sivir, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def fly(sp, tag, launch, sx, sy, tx, ty, speed):
        """A picture flying from (sx, sy) to (tx, ty) at `speed` px a tick; returns its arrival."""
        span = ((tx - sx) ** 2 + (ty - sy) ** 2) ** 0.5
        arrive = launch + tick(max(1.0, span / speed))
        over.append(Anim(frames_of(sp, tag), launch, sx, sy, until=arrive, x1=tx, y1=ty))
        return arrive

    def blade(tag, launch, foe, lift=8, speed=6.0, hit="a_hit"):
        tx, ty = foe.pos(launch)
        arrive = fly(small, tag, launch, x, gy - lift, tx, ty - lift, speed)
        on(foe, small, hit, arrive)
        foe.flinches.append(arrive)
        return arrive

    # she runs in; Darius and Garen wait
    run_in = Anim(frames_of(sivir, "run"), 0.0, x - 44, gy, loop=True, until=1100, x1=x)
    body.append(run_in)
    t = run_in.until
    a("idle", 300, loop=True)
    # Ricochet: the first attack lights the blade (w_cast at her hip), 4 s of motes and +45% attack speed (41 ticks
    # apart); each blade lands on Darius, hops 5 ticks onto Garen
    w0 = t
    on(me, small, "w_cast", w0)
    on(me, small, "w_on", w0, until=w0 + tick(240))
    for _ in range(3):
        arrive = blade("w_blade", t + tick(6), d)
        on(g, small, "w_bounce", arrive)
        on(g, small, "w_hit", arrive + tick(5))
        g.flinches.append(arrive + tick(5))
        a("attack")
        a("idle", tick(41 - 24), loop=True)
    a("idle", 300, loop=True)
    # Boomerang Blade: thrown on tick 10, 110 px out at 6.5 a tick through both, back at 7 into her hand
    q = t + tick(10)
    on(me, small, "q_throw", q)
    far = x + 110
    out_end = fly(big, "q_out", q, x, gy - 2, far, gy - 2, 6.5)
    for foe in (d, g):
        hit = q + tick((foe.pos(q)[0] - x) / 6.5)
        on(foe, small, "q_hit", hit)
        foe.flinches.append(hit)
    back = fly(big, "q_back", out_end, far, gy - 2, x, gy - 2, 7.0)
    for foe in (g, d):
        hit = out_end + tick((far - foe.pos(out_end)[0]) / 7.0)
        on(foe, small, "q_hit", hit)
        foe.flinches.append(hit)
    a("skill")
    a("skill_wait", back - t, loop=True)
    on(me, small, "q_catch", t)
    a("skill_catch", tick(10))
    a("idle", 400, loop=True)
    # Spell Shield: up at once, a spell lands 50 ticks later (the block: heal + Fleet of Foot), gone 60 ticks after it
    e0 = t
    pre = on(me, big, "e_pre", e0)
    blocked = e0 + tick(50)
    on(me, big, "e_loop", pre.until, until=blocked + tick(60))
    on(me, small, "e_block", blocked)
    on(me, big, "e_remove", blocked + tick(60))
    a("skill2")
    a("idle", blocked + tick(60) + 300 - t, loop=True)
    # On The Hunt: the shockwave under her, the hunt's ring at her feet; two blades and Darius falls -> it renews
    r0 = t
    on(me, big, "r_cast", r0, ground=True)
    hunt = on(me, small, "r_pre", r0, ground=True)
    on(me, small, "r_loop", hunt.until, until=r0 + tick(480), ground=True)
    a("ult")
    last = None
    for _ in range(2):
        last = blade("a_blade", t + tick(6), d)
        a("attack")
        a("idle", tick(60 - 24), loop=True)
    d.death = last
    on(me, small, "r_renew", last + tick(18))
    a("idle", 1200, loop=True)
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt))]
        for an in body:
            f = an.frame(tt)
            if f is not None:
                units.append((an.pos(tt)[1], f, an.pos(tt)))
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
    q_ = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q_[0].save(T.long_path(out), save_all=True, append_images=q_[1:], duration=step, loop=0)
    return len(frames), round(end / 1000.0, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "preview"))
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    s = load(CHAMP)
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_sivir_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_sivir_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_sivir_showcase.gif")))


if __name__ == "__main__":
    main()

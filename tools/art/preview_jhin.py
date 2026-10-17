#!/usr/bin/env python3
"""Preview images for Jhin, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_jhin.py [--out docs/preview]

  league_jhin_frames.png    every animation, frame by frame, 3x on the arena colour
  league_jhin_effects.png   every effect animation, 3x
  league_jhin_showcase.gif  a scripted fight against Darius with Garen behind him, timed like the kit: Jhin walks in
                            and fires Whisper three times (a glint as he raises it, teal fire at the muzzle, gold
                            bullets); the fourth shot after his flourish - rose rings at the muzzle and on the crit -
                            and the four bullets of the reload lighting up over his hood while he throws the Dancing
                            Grenade, which bursts on Darius and drops onto Garen; Deadly Flourish: the lotus lands at
                            Darius's feet, the cane-rifle's long shot roots him (he was hit by Jhin lately) and the
                            lotus blooms under him and bursts two seconds later; Curtain Call: the rose curtain as he
                            kneels with the cannon, four shells (the fourth a crit) and Darius falls, a lotus blooming
                            on his body; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_jhin")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_jhin_fx", "league_jhin_big")}


class Me:
    """Jhin's pivot for the views that follow him."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def pos(self, t):
        return self.x, self.y


def showcase(out, z=3, step=40):
    jhin = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_jhin_fx"], fx["league_jhin_big"]
    W, H = 300, 130
    gy = 92                                           # the pivot row: the R curtain rises 40 px over his soles
    x0 = 70
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 55, gy + 4)     # 55 px: attack range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 82, gy - 10)     # behind him
    body, under, over = [], [], []
    t = 0.0
    me = Me(x0, gy)
    x = x0

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(jhin, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def at(sp, tag, when, px, py, ground=False, until=None):
        an = Anim(frames_of(sp, tag), when, px, py, z=-1 if ground else 1, loop=until is not None, until=until)
        (under if ground else over).append(an)
        return an

    def shot(tag, launch, foe, speed, lift, hit=None):
        """A bullet from his pivot `lift` px up to the foe's pivot at `speed` px a tick; returns its arrival."""
        tx, ty = foe.pos(launch)
        span = ((tx - x) ** 2 + (ty - gy + lift) ** 2) ** 0.5
        arrive = launch + tick(max(1.0, span / speed))
        over.append(Anim(frames_of(small, tag), launch, x, gy - lift, until=arrive, x1=tx, y1=ty - 6))
        if hit:
            on(foe, small, hit, arrive)
        foe.flinches.append(arrive)
        return arrive

    # he walks in; Darius and Garen wait
    run_in = Anim(frames_of(jhin, "run"), 0.0, x - 44, gy, loop=True, until=1100, x1=x)
    body.append(run_in)
    t = run_in.until
    a("idle", 300, loop=True)
    # three shots of Whisper: the glint as he raises it, the bullet on tick 9 at 7 px a tick, 72 ticks apart
    for _ in range(3):
        on(me, small, "a_cast", t + tick(3))           # as Whisper comes up (the kit: 2 ticks after the attack applies)
        on(me, small, "a_muzzle", t + tick(9))
        shot("a_bolt", t + tick(9), d, 7.0, 7, "a_hit")
        a("attack")
        a("idle", tick(72 - 24), loop=True)
    # the fourth: his flourish, the shot on tick 12 at 8 px a tick, the crit; the reload lights up over his hood
    f4 = t + tick(12)
    on(me, small, "a4_muzzle", f4)
    shot("a4_bolt", f4, d, 8.0, 7, "a4_hit")
    on(me, small, "a_reload", f4)
    a("attack4")
    a("idle", 200, loop=True)
    # Dancing Grenade while he reloads: the throw on tick 9, 4 px a tick, the hop onto Garen 6 ticks after the hit
    q = t + tick(9)
    on(me, small, "q_throw", q)
    hit = shot("q_nade", q, d, 4.0, 9, "q_boom")
    on(g, small, "q_drop", hit + tick(6))
    on(g, small, "q_boom", hit + tick(12))
    g.flinches.append(hit + tick(12))
    a("skill")
    a("idle", 900, loop=True)
    # Deadly Flourish with the lotus: the seed flies 18 ticks to Darius's feet, arms in 24 and blooms under him (he
    # stands on it): the slow and, 120 ticks later, the burst; the shot on tick 42 at 16 px a tick roots him 100 ticks
    w0 = t
    dx, dy = d.pos(w0)
    over.append(Anim(frames_of(small, "e_seed"), w0, x, gy - 14, until=w0 + tick(18), x1=dx, y1=dy + 8))
    at(small, "e_land", w0 + tick(18), dx, dy, ground=True)
    bloom = w0 + tick(18 + 24 + 1)
    at(big, "e_bloom", bloom, dx, dy, ground=True)
    on(d, small, "e_slowed", bloom, until=bloom + tick(120))
    at(big, "e_boom", bloom + tick(120), dx, dy)
    for foe in (d, g):
        if abs(foe.pos(bloom)[0] - dx) <= 30:
            on(foe, small, "e_hit", bloom + tick(122))
            foe.flinches.append(bloom + tick(122))
    w = w0 + tick(42)
    on(me, small, "w_muzzle", w)
    arrive = shot("w_shot", w, d, 16.0, 9, "w_hit")
    on(d, small, "w_root", arrive + tick(1))
    d.holds.append((arrive + tick(1), arrive + tick(101)))
    a("skill2")
    a("idle", bloom + tick(120) + 600 - t, loop=True)
    # Curtain Call: the deploy (30 ticks), then the aim; four shells 48 ticks apart, 20 px a tick, the 4th a crit
    r0 = t
    on(me, small, "r_deploy", r0)
    a("ult", tick(30))
    shells = [r0 + tick(38 + 48 * k) for k in range(4)]
    for k, s in enumerate(shells):
        if s > t:
            a("ult_aim", s - t, loop=True)
        on(me, small, "r_muzzle", s)
        last = shot("r_bullet", s, d, 20.0, 8, "r_crit" if k == 3 else "r_hit")
        on(d, small, "r_slowed", last, until=last + tick(30))
        a("ult_shot", tick(12))
    a("ult_aim", tick(20), loop=True)
    d.death = last
    # the kill blooms a lotus on his body (the corpse lob lands 10 ticks after the shot, reads 8 later)
    cx, cy = d.pos(last)
    bloom2 = shells[3] + tick(18)
    at(big, "e_bloom", bloom2, cx, cy, ground=True)
    at(big, "e_boom", bloom2 + tick(120), cx, cy)
    if abs(g.pos(bloom2)[0] - cx) <= 30:
        on(g, small, "e_slowed", bloom2, until=bloom2 + tick(120))
        on(g, small, "e_hit", bloom2 + tick(122))
        g.flinches.append(bloom2 + tick(122))
    a("idle", bloom2 + tick(120) + 700 - t, loop=True)
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_jhin_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_jhin_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_jhin_showcase.gif")))


if __name__ == "__main__":
    main()

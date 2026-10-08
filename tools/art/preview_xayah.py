#!/usr/bin/env python3
"""Preview images for Xayah, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_xayah.py [--out docs/preview]

  league_xayah_frames.png    every animation, frame by frame, 3x on the arena colour
  league_xayah_effects.png   every effect animation, 3x
  league_xayah_showcase.gif  a scripted fight against Darius with Garen behind him, Rakan at her back, timed like
                             the kit (tools/kit/build_xayah.py): Xayah runs in; two blades at Darius; Double Daggers
                             pierce both and leave two feathers behind Garen; two empowered attacks (Clean Cuts) pierce
                             Darius and drop their feathers; the recall (Bladecaller) pulls all four back through them
                             and roots Darius; Deadly Plumage - the storm round her, a second blade on every attack, the
                             speed wisps; Featherstorm - the leap, the dagger rain on both and five feathers, the recall
                             finishes Darius; 3x
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
from preview_varus import At  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_xayah")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_xayah_fx", "league_xayah_big", "league_xayah_sym")}


def showcase(out, z=3, step=40):
    me_sp = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big, sym = fx["league_xayah_fx"], fx["league_xayah_big"], fx["league_xayah_sym"]
    W, H = 330, 140
    gy = 96
    x0 = 92
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), x0 + 56, gy + 4)     # 57.5 px: her range
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), x0 + 84, gy - 8)      # behind him
    rakan = Anim(frames_of(load(os.path.join(LEAGUE, "champions", "league_rakan")), "idle"), 0.0, x0 - 34, gy - 12,
                 loop=True, until=10 ** 9)
    body, under, over = [], [], []
    t = 0.0
    x = x0
    me = At(x, gy)
    lying = []                                       # feathers on the ground: [x, y, since, anim]

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(me_sp, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until
        return an

    def on(unit, sp, tag, when, until=None, ground=False):
        an = OnFoe(frames_of(sp, tag), when, unit, z=-1 if ground else 1)
        if until is not None:
            an.loop, an.until = True, until
        (under if ground else over).append(an)
        return an

    def fly(sp, tag, launch, sx, sy, tx, ty, speed):
        span = ((tx - sx) ** 2 + (ty - sy) ** 2) ** 0.5
        arrive = launch + tick(max(1.0, span / speed))
        over.append(Anim(frames_of(sp, tag), launch, sx, sy, until=arrive, x1=tx, y1=ty))
        return arrive

    def hit(foe, tag, when):
        on(foe, small, tag, when)
        foe.flinches.append(when)

    def feather(fx_, when):
        """A feather lands at fx_ (where its blade stopped) and lies there until the recall picks it up."""
        drop = Anim(frames_of(small, "f_drop"), when, fx_, gy)
        under.append(drop)
        lie = Anim(frames_of(small, "f_lie"), drop.until, fx_, gy, loop=True, until=10 ** 9)
        under.append(lie)
        lying.append(lie)

    def recall(when):
        """Bladecaller: every lying feather flies back to her at 4.5 px a tick, cutting Darius and Garen on the way;
        the third champion hit roots."""
        hits = []
        for lie in lying:
            lie.until = when
            fly(small, "feather", when, lie.x, gy - 4, x, gy - 4, 4.5)
            over[-1].fr = [(f.transpose(Image.FLIP_LEFT_RIGHT), ms) for f, ms in over[-1].fr]   # flying left
            for foe in (g, d):
                fx_ = foe.pos(when)[0]
                if x < fx_ < lie.x:
                    hits.append((when + tick((lie.x - fx_) / 4.5), foe))
        lying.clear()
        for k, (h, foe) in enumerate(sorted(hits, key=lambda u: u[0])):
            if foe.death is not None and h >= foe.death:
                continue
            hit(foe, "e_hit", h)
            if k == 2:
                on(foe, small, "e_root", h, ground=True)
                on(foe, small, "e_bind", h + 470, until=h + tick(75), ground=True)
                foe.holds.append((h, h + tick(75)))
        return max([h for h, _ in hits] or [when])

    def blade(foe, cast="attack", second=False):
        """One attack: the homing blade leaves her hand on tick 8 (19 px out, 4 up) at 7 a tick; with W on, a second
        blade 6 ticks later (the speed wisps when it hits a champion)."""
        rel = t + tick(8)
        tx, ty = foe.pos(rel)
        hit(foe, "a_hit", fly(small, "a_blade", rel + tick(2), x + 19, gy - 4, tx, ty - 8, 7.0))
        if second:
            arrive = fly(small, "w_blade", rel + tick(8), x + 19, gy - 4, tx, ty - 8, 7.0)
            hit(foe, "a_hit", arrive)
            on(me, small, "w_ms", arrive, until=arrive + tick(90), ground=True)
        a(cast)

    def pierce(foe):
        """An empowered attack (Clean Cuts): a line at the target, 72 px, through everything; a feather where it
        stops."""
        rel = t + tick(8)
        end = x + 72
        fly(small, "a_pierce", rel + tick(2), x + 19, gy - 4, end, gy - 4, 7.0)
        for f in (d, g):
            fx_ = f.pos(rel)[0]
            if fx_ < end and (f.death is None or rel < f.death):
                hit(f, "a_hit", rel + tick(2 + (fx_ - x - 19) / 7.0))
        feather(end, rel + tick(2 + (end - x - 19) / 7.0))
        a("attack")

    # she runs in; Rakan beside her, Darius and Garen wait
    walk = Anim(frames_of(me_sp, "run"), 0.0, x - 44, gy, loop=True, until=1300, x1=x)
    body.append(walk)
    t = walk.until
    a("idle", 300, loop=True)
    for _ in range(2):
        blade(d)
        a("idle", tick(50 - 24), loop=True)
    # Double Daggers (the passive's glow as it starts): two daggers 6 ticks apart through both, feathers at 95 px
    q0 = t
    on(me, sym, "p_on", q0)
    for k in range(2):
        rel = q0 + tick(8 + 6 * k)
        end = x + 95
        fly(small, "q_dagger", rel + tick(2), x + 19, gy - 5, end, gy - 5, 6.0)
        for f in (d, g):
            hit(f, "q_hit", rel + tick(2 + (f.pos(rel)[0] - x - 19) / 6.0))
        feather(end - 3 * k, rel + tick(2 + (95 - 19) / 6.0))
    a("skill_fx1")
    a("idle", 200, loop=True)
    # two empowered attacks drop their feathers behind Darius
    for _ in range(2):
        pierce(d)
        a("idle", tick(50 - 24), loop=True)
    # the recall: E's pose, every feather back (70 ticks after Q's release in the kit; here after the empowered attacks)
    e0 = t
    a("skill_e_fx1")
    recall(e0 + tick(2))
    a("idle", 500, loop=True)
    # Deadly Plumage: the storm round her (240 ticks), +50% attack speed, a second blade on every attack
    w0 = t
    on(me, sym, "p_on", w0)
    on(me, small, "w_on", w0 + 200, until=w0 + tick(240), ground=True)
    a("skill2_fx1")
    for _ in range(3):
        blade(d, second=True)
        a("idle", tick(33 - 24), loop=True)
    a("idle", 300, loop=True)
    # Featherstorm: the leap (untargetable), the rain at tick 48 on the 90-px line, five feathers along it, the recall
    # 40 ticks later finishes Darius
    r0 = t
    on(me, sym, "p_on", r0)
    rain = r0 + tick(48)
    over.append(Anim(frames_of(big, "r_rain"), rain, x + 45, gy - 4))
    for f in (d, g):
        hit(f, "r_hit", rain + tick(2))
    for k in range(5):
        feather(x + 40 + int(55 * k / 4), rain + tick(3))
    a("ult_fx1")
    a("idle", tick(40) - (t - rain), loop=True)
    last = recall(t)
    d.death = last
    a("skill_e_fx1")
    a("idle", 1300, loop=True)
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
                 (rakan.pos(tt)[1], rakan.frame(tt), rakan.pos(tt))]
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
    sample = frames[::6]
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
    ap.add_argument("--only", choices=["frames", "effects", "showcase"])
    args = ap.parse_args()
    os.makedirs(T.long_path(args.out), exist_ok=True)
    if args.only in (None, "frames"):
        s = load(CHAMP)
        print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                                os.path.join(args.out, "league_xayah_frames.png")))
    if args.only in (None, "effects"):
        rows = []
        for name, path in FX.items():
            sp = load(path)
            rows += [(sp, t["name"], f"{name[13:]}:{t['name']}") for t in sp.tags]
        print("effects", contact(rows, os.path.join(args.out, "league_xayah_effects.png")))
    if args.only in (None, "showcase"):
        print("showcase frames/seconds", showcase(os.path.join(args.out, "league_xayah_showcase.gif")))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Preview images for Miss Fortune, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_missfortune.py [--out docs/preview]

  league_missfortune_frames.png    every animation, frame by frame, 3x on the arena colour
  league_missfortune_effects.png   every effect animation, 3x
  league_missfortune_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: she runs in and
                                   her first shot is Love Tap (the heart), the next a plain one; Double Up goes
                                   through Darius into Garen behind him, the bounce with its heart; Make It Rain
                                   falls between them while she Struts, two quicker shots; Bullet Time's twelve
                                   waves sweep them both; the last Double Up kills Darius and the bounce crits
                                   Garen; 3x
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from preview_ashe import Anim, tick  # noqa: E402
from preview_garen import ARENA, T, contact, frames_of, load  # noqa: E402
from preview_jinx import Follow, Walker  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
LEAGUE = os.path.join(ROOT, "league")
CHAMP = os.path.join(LEAGUE, "champions", "league_missfortune")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_missfortune_fx", "league_missfortune_big")}


def showcase(out, z=3, step=40):
    mf = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    W, H = 300, 142                                    # Bullet Time's +-25 degree wave reaches 47 px below her pivot
    gy = 92                                            # her pivot row
    x = 44
    d = Walker(load(os.path.join(LEAGUE, "champions", "league_darius")), 99, gy)        # 55 px: her range
    g = Walker(load(os.path.join(LEAGUE, "champions", "league_garen")), 280, gy - 4)    # walks in behind him
    body, under, over = [], [], []
    t = 0.0
    muzzle = (x + 12, gy - 8)                          # where her shots leave the pistol

    def a(tag, dur=None, loop=False):
        nonlocal t
        an = Anim(frames_of(mf, tag), t, x, gy, loop=loop, until=(t + dur) if dur else None)
        body.append(an)
        t = an.until

    def fx_at(sprite, tag, at, px, py, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(fx[sprite], tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def shot(start, tag, hits, speed, fire=8):
        """A bullet leaves the pistol `fire` ticks into the action at `speed` px a tick and hits Darius."""
        launch = start + tick(fire)
        fx_, fy = d.pos(launch)
        arrive = launch + tick(max(1.0, (fx_ - 4 - muzzle[0]) / speed))
        fx_at("league_missfortune_fx", tag, launch, *muzzle, until=arrive, x1=fx_ - 4, y1=fy - 6)
        for h in hits:
            fx_at("league_missfortune_fx", h, arrive, *d.pos(arrive))
        d.flinches.append(arrive)
        return arrive

    def double_up(start, first, second, kill=False):
        """Double Up: one bullet at 12 px a tick through Darius into Garen behind him (the bounce 4 ticks later)."""
        launch = start + tick(8)
        dx_, dy_ = d.pos(launch)
        gx, gy_ = g.pos(launch)
        hit1 = launch + tick((dx_ - muzzle[0]) / 12.0)
        hit2 = launch + tick((gx - muzzle[0]) / 12.0)
        fx_at("league_missfortune_fx", "q_bullet", launch, *muzzle, until=hit2, x1=gx, y1=gy_ - 6)
        fx_at("league_missfortune_fx", first, hit1, *d.pos(hit1))
        fx_at("league_missfortune_fx", second, hit2 + tick(4), *g.pos(hit2))
        if kill:
            d.death = hit1
        else:
            d.flinches.append(hit1)
        g.flinches.append(hit2 + tick(4))

    # she runs in while Garen walks up behind Darius, 47 px back: inside the bounce's reach
    body.append(Anim(frames_of(mf, "run"), 0.0, x - 36, gy, loop=True, until=1200, x1=x))
    t = 1200.0
    g.walks.append((0.0, 2000, 146 - g.x))
    a("idle", 300, loop=True)
    # the first shot of the fight is Love Tap: the heart; the next, one second later, a plain one
    shot(t, "bullet_lt", ("lovetap", "hit"), 6.0)
    a("attack")
    a("idle", tick(60) - tick(22), loop=True)
    shot(t, "bullet", ("hit",), 6.0)
    a("attack")
    a("idle", 500, loop=True)
    # Double Up: through Darius, into Garen (the bounce carries Love Tap: its heart)
    double_up(t, "q_hit", "q_bounce")
    a("skill")
    a("idle", 300, loop=True)
    # Make It Rain between them (2 s, a wave every 0.25 s) and Strut: 40% attack speed for 4 s
    start = t
    zx = (d.x + 146) // 2
    fx_at("league_missfortune_big", "e_rain", start + tick(8), zx, gy - 2, ground=True)
    for k in range(8):
        wave = start + tick(8 + 15 * k)
        d.flinches.append(wave)
        g.flinches.append(wave)
    over.append(Follow(frames_of(fx["league_missfortune_fx"], "strut"), start + tick(8), x, gy, on=body))
    a("skill2")
    for _ in range(2):
        shot(t, "bullet", ("hit",), 6.0)
        a("attack")
        a("idle", tick(43) - tick(22), loop=True)
    a("idle", 300, loop=True)
    # Bullet Time: twelve waves 15 ticks apart, each fanning out to both of them
    start = t
    for k in range(12):
        wave = start + tick(8 + 15 * k)
        fx_at("league_missfortune_big", "r_wave", wave, x + 50, gy)
        for foe in (d, g):
            hit = wave + tick(4)
            fx_at("league_missfortune_fx", "r_hit", hit, *foe.pos(hit))
            foe.flinches.append(hit)
    a("ult", tick(8 + 180), loop=True)
    a("idle", 400, loop=True)
    # the last Double Up: its first shot kills Darius, so the bounce crits Garen
    double_up(t, "q_hit", "q_crit", kill=True)
    a("skill")
    a("idle", 1200, loop=True)
    end = t

    def place(img, f, px, py):
        img.alpha_composite(f, (px - f.width // 2, py - f.height // 2))

    frames, tt = [], 0.0
    order = sorted((d, g), key=lambda f: f.y)         # the one further back first
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags],
                            os.path.join(args.out, "league_missfortune_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[19:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_missfortune_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_missfortune_showcase.gif")))


if __name__ == "__main__":
    main()

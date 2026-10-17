#!/usr/bin/env python3
"""Preview images for Ekko, built from the exported game sprites (so they also prove the sheets load).

    python tools/art/preview_ekko.py [--out docs/preview]

  league_ekko_frames.png    every animation, frame by frame, 3x on the arena colour
  league_ekko_effects.png   every effect animation, 3x
  league_ekko_showcase.gif  a scripted fight against Darius and Garen, timed like the kit: Ekko runs in and throws
                            Timewinder through Darius (its field opens where it stops, then it flies home and its
                            second hit is the third Resonance hit: Z-Drive's burst); he closes in and swings; Phase
                            Dive takes him onto Garen, Parallel Convergence forms under Garen 1.5 s later and bursts
                            with Ekko inside, stunning both and shielding him; Chronobreak leaves his hologram where
                            he stands, he chases Garen for 4 s, and snaps back to the hologram, blasting Darius
                            who had walked up to it; 3x
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
CHAMP = os.path.join(LEAGUE, "champions", "league_ekko")
FX = {n: os.path.join(LEAGUE, "effects", n) for n in ("league_ekko_fx", "league_ekko_big")}


def showcase(out, z=3, step=40):
    ekko = load(CHAMP)
    fx = {k: load(v) for k, v in FX.items()}
    small, big = fx["league_ekko_fx"], fx["league_ekko_big"]
    W, H = 320, 150
    gy = 104                                          # the pivot row
    d = Held(load(os.path.join(LEAGUE, "champions", "league_darius")), 132, gy)
    g = Held(load(os.path.join(LEAGUE, "champions", "league_garen")), 300, gy - 6)     # walking in
    body, under, over = [], [], []
    t = 0.0
    x = 60

    def a(tag, dur=None, loop=False, at=None, to=None):
        nonlocal t, x
        an = Anim(frames_of(ekko, tag), t, at if at is not None else x, gy, loop=loop,
                  until=(t + dur) if dur else None, x1=to)
        body.append(an)
        t = an.until
        if to is not None:
            x = to

    def fx_at(sp, tag, at, px, py=gy, ground=False, until=None, x1=None, y1=None, loop=None):
        an = Anim(frames_of(sp, tag), at, px, py, z=-1 if ground else 1,
                  loop=(until is not None) if loop is None else loop, until=until, x1=x1, y1=y1)
        (under if ground else over).append(an)
        return an

    def hit(foe, when, tag="hit", sp=None):
        over.append(OnFoe(frames_of(sp or small, tag), when, foe, z=1))
        foe.flinches.append(when)

    # he runs in; Garen walks up behind Darius
    a("run", 900, loop=True, at=x - 50, to=x)
    g.walks.append((0.0, 2600.0, 184 - g.x))
    a("idle", 300, loop=True)
    # Timewinder on tick 11: out 65 px at 3.5 px a tick through Darius, the field 45 ticks where it stops, home again
    start = t
    launch = start + tick(11)
    x0, xe = x + 8, x + 8 + 65
    out_end = launch + tick(65 / 3.5)
    fx_at(small, "q_device", launch, x0, gy - 6, until=out_end, x1=xe)
    hit(d, launch + tick((d.x - x0) / 3.5), "q_hit")
    fx_at(big, "q_field", out_end, xe, gy, ground=True)
    back = out_end + tick(45)
    a("skill")
    # he closes in on Darius and swings once (the second Resonance hit)
    a("run", 250, loop=True, to=d.x - 26)
    swing = t
    hit(d, swing + tick(10))
    a("attack")
    a("idle", tick(55) - tick(24), loop=True)
    # the device flies home from the field's spot: its hit on Darius is the third - Z-Drive Resonance
    home = back + tick((xe - x) / 3.5)
    fx_at(small, "q_device", back, xe, gy - 6, until=home, x1=x + 6)
    third = back + tick((xe - d.x) / 3.5)
    hit(d, third, "q_hit")
    over.append(OnFoe(frames_of(small, "z_proc"), third, d, z=1))
    swing = t
    hit(d, swing + tick(10))
    a("attack")
    a("idle", tick(55) - tick(24), loop=True)
    # Phase Dive onto Garen: the afterimage stays behind, he lands on him on tick 12 and strikes; Parallel
    # Convergence forms under Garen for 1.5 s and bursts at once, Ekko being there: both stunned 1 s, Ekko shielded
    start = t
    fx_at(small, "e_dash", start + tick(2), x, gy)
    gx = g.pos(start)[0]
    body.append(Anim(frames_of(ekko, "skill2"), start, x, gy, until=start + tick(29), x1=gx - 24))
    x = gx - 24
    t = start + tick(29)
    hit(g, start + tick(12), "e_hit")
    spot = g.pos(start)
    fx_at(big, "w_forming", start + tick(2), spot[0], spot[1], ground=True)
    burst = start + tick(2 + 90)
    swing = t
    hit(g, swing + tick(10))
    a("attack")
    a("idle", tick(55) - tick(24), loop=True)
    swing = t
    hit(g, swing + tick(10))
    a("attack")
    a("idle", burst - t, loop=True)
    fx_at(big, "w_sphere", burst - tick(1), spot[0], spot[1], ground=True)
    fx_at(big, "w_shatter", burst, spot[0], spot[1])
    for foe in (g, d):
        if abs(foe.pos(burst)[0] - spot[0]) <= 40:
            foe.holds.append((burst, burst + 1000))
            over.append(OnFoe(frames_of(small, "w_stun"), burst, foe, z=1))
    fx_at(small, "w_shield", burst, x, gy, until=burst + 2000, loop=True)
    a("idle", 400, loop=True)
    # Chronobreak on tick 4: his hologram stays where he stands for 4 s; Garen backs off and Ekko chases him
    # (two swings) while Darius walks up to the hologram; then he vanishes and snaps back onto it, blasting it
    start = t
    anchor = x
    fx_at(big, "r_ghost", start + tick(4), anchor, gy)
    a("ult")
    g.walks.append((t, t + 900, 40))
    d.walks.append((t + 400, t + 2600, anchor + 18 - d.pos(t)[0]))
    a("run", 900, loop=True, to=x + 36)
    for _ in range(2):
        swing = t
        hit(g, swing + tick(10))
        a("attack")
        a("idle", tick(55) - tick(24), loop=True)
    back_at = start + tick(4 + 239)
    a("idle", back_at - t, loop=True)
    fx_at(big, "r_depart", back_at, x, gy)
    x = anchor
    fx_at(big, "r_arrive", back_at, anchor, gy, ground=True)
    for foe in (d, g):
        if abs(foe.pos(back_at)[0] - anchor) <= 38:
            hit(foe, back_at, "r_hit")
    a("ult_arrive", at=anchor)
    a("idle", 900, loop=True)
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
        units = [(g.pos(tt)[1], g.frame(tt), g.pos(tt)), (d.pos(tt)[1], d.frame(tt), d.pos(tt))]
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
    print("frames", contact([(s, t["name"], t["name"]) for t in s.tags], os.path.join(args.out, "league_ekko_frames.png")))
    rows = []
    for name, path in FX.items():
        sp = load(path)
        rows += [(sp, t["name"], f"{name[12:]}:{t['name']}") for t in sp.tags]
    print("effects", contact(rows, os.path.join(args.out, "league_ekko_effects.png")))
    print("showcase frames/seconds", showcase(os.path.join(args.out, "league_ekko_showcase.gif")))


if __name__ == "__main__":
    main()
